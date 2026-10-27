"""Live Phase 1 validation using Azure CLI, OAuth REST and Databricks SDK only."""

from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from decimal import Decimal
from email.utils import formatdate
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from foundation_ledger import BlobLedger, exposure, update_snapshot
from foundation_support import (
    CONFIG,
    OUTPUT,
    ROOT,
    AzureRest,
    CloudHttpError,
    azure,
    databricks_clients,
    load,
    now,
    save,
    source_binding,
)


def expect(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def without_nulls(value):
    """Azure CLI includes unused optional actions as null, raw ARM can omit them."""
    if isinstance(value, dict):
        return {
            key: without_nulls(item) for key, item in value.items() if item is not None
        }
    if isinstance(value, list):
        return [without_nulls(item) for item in value]
    return value


def validate_budgets(budgets: dict, config: dict) -> None:
    expected = {
        "workspace-build": (165, [25, 50, 75, 90]),
        "workspace-monthly": (55, [50, 80, 100]),
        "model-build": (35, [25, 50, 75, 90]),
        "model-monthly": (5, [50, 80, 100]),
    }
    for name, (amount, levels) in expected.items():
        props = budgets[name]["properties"]
        notifications = list(props["notifications"].values())
        expect(props["amount"] == amount, f"Budget amount drift: {name}")
        expect(props["category"] == "Cost", "Only cost budgets accepted")
        expect(
            sorted(item["threshold"] for item in notifications) == levels,
            "Alert thresholds/counts drift",
        )
        expect(
            all(
                item["enabled"]
                and item["operator"] == "GreaterThanOrEqualTo"
                and item["contactEmails"] == ["karthik@intellifysolutions.com"]
                for item in notifications
            ),
            "Budget alert recipient/action drift",
        )
        expect(
            props["timeGrain"] == ("Annually" if name.endswith("build") else "Monthly"),
            "Budget cadence drift",
        )
    expect(
        config["build_ceiling_paise"] == 2000000
        and config["monthly_target_paise"] == 600000,
        "Unapproved budget change",
    )


def validate_storage(
    storage: dict, containers: list, policy: dict, config: dict
) -> None:
    expect(
        storage["isHnsEnabled"] is True and storage["allowBlobPublicAccess"] is False,
        "Storage must use HNS and block anonymous containers",
    )
    expect(
        storage["allowSharedKeyAccess"] is False
        and storage["minimumTlsVersion"] == "TLS1_2",
        "Storage key/TLS configuration unsafe",
    )
    expect(storage["sku"]["name"] == "Standard_LRS", "Unexpected storage cost tier")
    expect(
        {c["name"] for c in containers} == set(config["containers"]),
        "Container inventory mismatch",
    )
    expect(
        all(
            c.get("properties", {}).get("publicAccess") in {None, "None", "Off"}
            for c in containers
        ),
        "Public container access",
    )
    # Azure CLI flattens management-policy properties; raw ARM retains them.
    rules = policy.get("properties", policy)["policy"]["rules"]
    expect(
        len(rules) == 1 and rules[0]["enabled"], "Unexpected lifecycle rule inventory"
    )
    rule = rules[0]["definition"]
    expect(
        rule["filters"]["prefixMatch"] == ["landing/"]
        and rule["filters"]["blobTypes"] == ["blockBlob"],
        "Lifecycle escaped landing",
    )
    expect(
        without_nulls(rule["actions"])
        == {"baseBlob": {"tierToCool": {"daysAfterModificationGreaterThan": 90}}},
        "Unexpected lifecycle deletion/tiering",
    )


def collect_control_plane(config: dict, foundation: dict) -> dict:
    sub, model = config["workspace_subscription"], config["model_subscription"]
    resources = azure(
        ["resource", "list", "--resource-group", config["resource_group"]], sub
    )
    model_resources = azure(
        ["resource", "list", "--resource-group", config["model_resource_group"]], model
    )
    workspace = azure(
        [
            "resource",
            "show",
            "--ids",
            load(ROOT / "platform/config/workspace.json")["workspace_resource_id"],
        ],
        sub,
    )
    storage = azure(
        [
            "storage",
            "account",
            "show",
            "--name",
            config["storage_account"],
            "--resource-group",
            config["resource_group"],
        ],
        sub,
    )
    containers = azure(
        [
            "storage",
            "container",
            "list",
            "--account-name",
            config["storage_account"],
            "--auth-mode",
            "login",
        ],
        sub,
    )
    policy = azure(
        [
            "storage",
            "account",
            "management-policy",
            "show",
            "--account-name",
            config["storage_account"],
            "--resource-group",
            config["resource_group"],
        ],
        sub,
    )
    vault = azure(
        [
            "keyvault",
            "show",
            "--name",
            config["key_vault"],
            "--resource-group",
            config["resource_group"],
        ],
        sub,
    )
    deployments = azure(
        [
            "cognitiveservices",
            "account",
            "deployment",
            "list",
            "--name",
            "aoai-hcp-luna-0725fcd1",
            "--resource-group",
            config["model_resource_group"],
        ],
        model,
    )
    model_account = azure(
        [
            "cognitiveservices",
            "account",
            "show",
            "--name",
            "aoai-hcp-luna-0725fcd1",
            "--resource-group",
            config["model_resource_group"],
        ],
        model,
    )
    arm = AzureRest(sub, "https://management.azure.com/", {"management.azure.com"})
    budgets = {}
    for name, scope, budget_name in [
        ("workspace-build", f"subscriptions/{sub}", "hcp-platform-build"),
        ("workspace-monthly", f"subscriptions/{sub}", "hcp-platform-monthly"),
        (
            "model-build",
            f"subscriptions/{model}/resourceGroups/{config['model_resource_group']}",
            "hcp-model-build",
        ),
        (
            "model-monthly",
            f"subscriptions/{model}/resourceGroups/{config['model_resource_group']}",
            "hcp-model-monthly",
        ),
    ]:
        _, _, body = arm.request(
            "GET",
            f"https://management.azure.com/{scope}/providers/Microsoft.Consumption/budgets/{budget_name}?api-version=2024-08-01",
        )
        budgets[name] = json.loads(body)
    roles = {}
    for name, scope in [
        ("storage", storage["id"]),
        ("vault", vault["id"]),
        ("control", storage["id"] + "/blobServices/default/containers/control"),
    ]:
        roles[name] = azure(
            ["role", "assignment", "list", "--scope", scope, "--include-inherited"], sub
        )
    connector = azure(
        ["resource", "show", "--ids", foundation["access_connector_id"]], sub
    )
    expect(
        connector["identity"]["type"] == "SystemAssigned"
        and any(
            r["principalId"] == connector["identity"]["principalId"]
            and r["scope"].lower() == storage["id"].lower()
            and r["roleDefinitionName"] == "Storage Blob Data Contributor"
            for r in roles["storage"]
        ),
        "Access connector does not have the exact storage-account data role",
    )
    validate_storage(storage, containers, policy, config)
    validate_budgets(budgets, config)
    expected_tags = {
        "project": "healthcare-platform",
        "owner": "karthik",
        "costcenter": "healthcare-poc",
    }
    for resource in resources + model_resources + [workspace]:
        expect(
            all(resource.get("tags", {}).get(k) == v for k, v in expected_tags.items()),
            "Missing healthcare ownership/cost tags",
        )
        expect(
            resource["type"].lower()
            not in {t.lower() for t in config["forbidden_resource_types"]}
            or resource["id"].lower() == workspace["id"].lower(),
            "Forbidden/duplicate resource",
        )
    expect(
        workspace["id"].lower()
        == load(ROOT / "platform/config/workspace.json")[
            "workspace_resource_id"
        ].lower(),
        "Wrong workspace",
    )
    expect(
        vault["properties"]["enableRbacAuthorization"]
        and vault["properties"]["enableSoftDelete"]
        and vault["properties"]["softDeleteRetentionInDays"] == 7,
        "Vault RBAC/soft delete configuration",
    )
    expect(
        any(
            r["principalId"] == foundation["groups"]["hcp-platform-admins"]
            and r["roleDefinitionName"] == "Key Vault Secrets Officer"
            for r in roles["vault"]
        ),
        "Missing scoped vault operator role",
    )
    expect(
        any(
            r["principalId"] == foundation["principals"]["sp-hcp-cicd"]["object_id"]
            and r["scope"].lower().endswith("/containers/control")
            and r["roleDefinitionName"] == "Storage Blob Data Contributor"
            for r in roles["control"]
        ),
        "Missing scoped control metadata role",
    )
    expect(
        len(deployments) == 1
        and deployments[0]["name"] == "gpt-6-luna"
        and deployments[0]["sku"]["name"] == "DataZoneStandard"
        and deployments[0]["sku"]["capacity"] == 5
        and deployments[0]["properties"]["model"]["version"] == "2026-09-22",
        "Exact-model prerequisite changed",
    )
    expect(
        model_account["properties"]["disableLocalAuth"] is True,
        "Model deployment must be keyless",
    )
    # Evidence is public: omit unrelated inherited subscription/account principals.
    selected_scopes = {
        "storage": storage["id"],
        "vault": vault["id"],
        "control": storage["id"] + "/blobServices/default/containers/control",
    }
    expected_principals = (
        set(foundation["groups"].values())
        | {p["object_id"] for p in foundation["principals"].values()}
        | {"5ee77c8e-621d-4953-9502-1be929c977e1", connector["identity"]["principalId"]}
    )
    return {
        "resources": [
            {k: r.get(k) for k in ["id", "name", "type", "location", "tags"]}
            for r in resources + model_resources
        ],
        "workspace_arm": {
            k: workspace.get(k) for k in ["id", "name", "location", "sku", "tags"]
        },
        "storage": storage,
        "containers": containers,
        "lifecycle": policy,
        "vault": {
            "id": vault["id"],
            "properties": {
                k: vault["properties"].get(k)
                for k in [
                    "tenantId",
                    "vaultUri",
                    "enableRbacAuthorization",
                    "enableSoftDelete",
                    "softDeleteRetentionInDays",
                ]
            },
        },
        "budgets": budgets,
        "roles": {
            scope: [
                {
                    k: r.get(k)
                    for k in [
                        "principalId",
                        "principalType",
                        "roleDefinitionName",
                        "scope",
                        "condition",
                    ]
                }
                for r in rs
                if r["principalId"] in expected_principals
                and r["scope"].lower() == selected_scopes[scope].lower()
            ]
            for scope, rs in roles.items()
        },
        "model_deployments": deployments,
        "model_keyless": True,
        "access_connector": {"id": connector["id"], "identity": connector["identity"]},
    }


def collect_databricks(config: dict, foundation: dict) -> dict:
    account, workspace = databricks_clients()
    current = account.workspaces.get(config["workspace_id"]).as_dict()
    expect(
        current["compute_mode"] == "SERVERLESS"
        and current["pricing_tier"] == "PREMIUM"
        and current["location"] == config["region"],
        "Unsupported workspace mode/region",
    )
    meta = workspace.metastores.current().as_dict()
    expect(
        meta["metastore_id"] == config["metastore_id"]
        and meta["workspace_id"] == config["workspace_id"],
        "Metastore assignment drift",
    )
    validations = {}
    credential = workspace.storage_credentials.get("hcp_storage_dev").as_dict()
    expect(
        credential["azure_managed_identity"]["access_connector_id"].lower()
        == foundation["access_connector_id"].lower(),
        "Storage credential uses wrong access connector",
    )
    for name in ["hcp_uc_managed_dev", "hcp_landing_dev"]:
        location = workspace.external_locations.get(name)
        expected_url = f"abfss://{'uc-managed' if name == 'hcp_uc_managed_dev' else 'landing'}@{config['storage_account']}.dfs.core.windows.net/"
        expect(
            location.url == expected_url
            and location.credential_name == "hcp_storage_dev",
            "External location identity drift",
        )
        result = workspace.storage_credentials.validate(
            storage_credential_name="hcp_storage_dev", external_location_name=name
        ).as_dict()
        expect(
            len(result.get("results", [])) == 6
            and all(item["result"] == "PASS" for item in result["results"]),
            "UC storage validation failed",
        )
        validations[name] = result
    principal_results = {}
    assignments = {
        str(item.principal.principal_id): item.as_dict()
        for item in account.workspace_assignment.list(config["workspace_id"])
    }
    for name, expected in foundation["principals"].items():
        actual = account.service_principals.get(
            expected["databricks_principal_id"]
        ).as_dict()
        expect(
            actual["applicationId"] == expected["client_id"]
            and actual["externalId"] == expected["object_id"]
            and actual["active"],
            "Foundation principal mismatch",
        )
        permissions = assignments.get(str(actual["id"]), {})
        expect(
            permissions.get("permissions") == ["USER"],
            "Unexpected service-principal workspace elevation",
        )
        principal_results[name] = {"identity": actual, "assignment": permissions}
    return {
        "workspace": current,
        "metastore": meta,
        "storage_validation": validations,
        "principals": principal_results,
        "warehouses": [w.as_dict() for w in workspace.warehouses.list()],
        "apps": [a.as_dict() for a in workspace.apps.list()],
        "jobs": [j.as_dict() for j in workspace.jobs.list()],
        "storage_credential": credential,
        "serving_endpoints": [
            {
                "name": e.name,
                "state": e.state.as_dict() if e.state else None,
                "builtin_foundation_models": all(
                    entity.foundation_model is not None
                    for entity in e.config.served_entities or []
                ),
            }
            for e in workspace.serving_endpoints.list()
        ],
    }


def probe_storage(config: dict) -> dict:
    host = f"{config['storage_account']}.blob.core.windows.net"
    client = AzureRest(
        config["workspace_subscription"], "https://storage.azure.com/", {host}
    )
    url = f"https://{host}/control/probes/foundation-{uuid.uuid4().hex}.json"
    headers = {
        "x-ms-version": "2023-11-03",
        "x-ms-date": formatdate(usegmt=True),
        "x-ms-blob-type": "BlockBlob",
    }
    payload = {"synthetic_nonpatient_fixture": "foundation-storage-check"}
    lease = None
    created = False
    try:
        _, _, _ = client.request(
            "PUT", url, body=payload, headers={**headers, "If-None-Match": "*"}
        )
        created = True
        _, original_headers, body = client.request("GET", url, headers=headers)
        expect(json.loads(body) == payload, "Storage read-after-write mismatch")
        etag = original_headers.get("ETag") or original_headers.get("Etag")
        expect(bool(etag), "Storage ETag missing")
        client.request(
            "PUT", url, body={"version": 2}, headers={**headers, "If-Match": etag}
        )
        stale_rejected = False
        try:
            client.request(
                "PUT",
                url,
                body={"corrupt": True},
                headers={**headers, "If-Match": etag},
            )
        except CloudHttpError as error:
            stale_rejected = error.status == 412
        expect(stale_rejected, "Stale ETag must be rejected")
        anonymous_denied = False
        try:
            with urlopen(
                Request(url, headers={"x-ms-version": "2023-11-03"}), timeout=30
            ):
                pass
        except HTTPError as error:
            anonymous_denied = error.code in {401, 403, 404}
        expect(anonymous_denied, "Anonymous blob access is possible")
        _, lease_headers, _ = client.request(
            "PUT",
            url + "?comp=lease",
            headers={
                **headers,
                "x-ms-lease-action": "acquire",
                "x-ms-lease-duration": "60",
            },
        )
        lease = lease_headers.get("x-ms-lease-id")
        expect(bool(lease), "Lease acquisition failed")
        second_rejected = False
        try:
            client.request(
                "PUT",
                url + "?comp=lease",
                headers={
                    **headers,
                    "x-ms-lease-action": "acquire",
                    "x-ms-lease-duration": "60",
                },
            )
        except CloudHttpError as error:
            second_rejected = error.status == 409
        expect(second_rejected, "Concurrent lease must be rejected")
        return {
            "status": "PASS",
            "read_write": True,
            "stale_etag_rejected": True,
            "anonymous_denied": True,
            "concurrent_lease_rejected": True,
            "fixture_sha256": hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest(),
        }
    finally:
        if lease:
            client.request(
                "PUT",
                url + "?comp=lease",
                headers={
                    **headers,
                    "x-ms-lease-action": "release",
                    "x-ms-lease-id": lease,
                },
            )
        # Only this exact UUID-scoped synthetic probe object is deleted.
        if created:
            client.request("DELETE", url, headers=headers)


def probe_vault(config: dict) -> dict:
    host = f"{config['key_vault']}.vault.azure.net"
    client = AzureRest(
        config["workspace_subscription"], "https://vault.azure.net", {host}
    )
    name = "foundation-probe-" + uuid.uuid4().hex
    url = f"https://{host}/secrets/{name}?api-version=7.4"
    value = "synthetic-test-only-" + uuid.uuid4().hex
    created = False
    try:
        client.request(
            "PUT",
            url,
            body={
                "value": value,
                "tags": {
                    "project": "healthcare-platform",
                    "purpose": "disposable-foundation-test",
                },
            },
        )
        created = True
        _, _, body = client.request("GET", url)
        expect(
            json.loads(body)["value"] == value, "Key Vault read-after-write mismatch"
        )
        return {
            "status": "PASS",
            "rbac_secret_write_read": True,
            "secret_name": name,
            "value_logged": False,
            "cleanup": "Soft-delete only; no purge",
        }
    finally:
        if created:
            client.request("DELETE", url)


def refresh_costs(config: dict) -> dict:
    ledger = BlobLedger(config)
    initial, created = ledger.initialize()
    arm = AzureRest(
        config["workspace_subscription"],
        "https://management.azure.com/",
        {"management.azure.com"},
    )
    costs = {}
    for subscription in [
        config["workspace_subscription"],
        config["model_subscription"],
    ]:
        scope = f"subscriptions/{subscription}"
        body = {
            "type": "ActualCost",
            "timeframe": "Custom",
            "timePeriod": {"from": "2026-10-01T00:00:00Z", "to": now()},
            "dataset": {
                "granularity": "Daily",
                "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
                "grouping": [
                    {"type": "Dimension", "name": "ResourceId"},
                    {"type": "Dimension", "name": "ChargeType"},
                ],
                "filter": {
                    "tags": {
                        "name": "project",
                        "operator": "In",
                        "values": ["healthcare-platform"],
                    }
                },
            },
        }
        try:
            _, _, raw = arm.request(
                "POST",
                f"https://management.azure.com/{scope}/providers/Microsoft.CostManagement/query?api-version=2025-03-01",
                body=body,
            )
            response = json.loads(raw)
            data = response["properties"]
            expect(
                not data.get("nextLink"),
                "Cost query pagination must be implemented before accepting partial totals",
            )
            columns = [c["name"] for c in data["columns"]]
            rows = [dict(zip(columns, row, strict=True)) for row in data["rows"]]
            expect(
                all(row.get("Currency") == "USD" for row in rows),
                "Unexpected billing currency",
            )
            cost_key = "PreTaxCost" if "PreTaxCost" in columns else "Cost"
            positive = sum(
                (
                    Decimal(str(row[cost_key]))
                    for row in rows
                    if Decimal(str(row[cost_key])) > 0
                ),
                Decimal(0),
            )
            credits = sum(
                (
                    Decimal(str(row[cost_key]))
                    for row in rows
                    if Decimal(str(row[cost_key])) < 0
                ),
                Decimal(0),
            )
            snapshot = {
                "currency": "USD",
                "positive_cost_usd": str(positive),
                "credits_usd": str(credits),
                "as_of": now(),
                "period_start": "2026-10-01",
                "scope": scope,
                "source_rows": len(rows),
                "status": "PROVISIONAL_EMPTY" if not rows else "PROVISIONAL",
                "planning_fx": "100",
                "tax_reserve": "0.18",
                "query_sha256": hashlib.sha256(
                    json.dumps(body, sort_keys=True).encode()
                ).hexdigest(),
            }
            ledger.transact(
                lambda old, key=scope, value=snapshot: update_snapshot(
                    old,
                    key,
                    value,
                    {
                        f"subscriptions/{s}"
                        for s in [
                            config["workspace_subscription"],
                            config["model_subscription"],
                        ]
                    },
                )
            )
            costs[scope] = snapshot
        except CloudHttpError as error:
            # Keep prior snapshots and reservations. Never replace a failed read with zero.
            costs[scope] = {
                "status": "UNAVAILABLE_RESERVATIONS_RETAINED",
                "http_status": error.status,
                "code": error.code,
            }
    final, _ = ledger.read()
    expect(not exposure(final)["over_ceiling"], "Build ledger exceeds ceiling")
    return {
        "created": created,
        "durable_ledger": {
            "container": "control",
            "blob": config["ledger_blob"],
            "revision": final["revision"],
        },
        "snapshots": costs,
        "exposure": exposure(final),
        "billing_settled": False,
        "no_compute_started": True,
        "prior_reservations_preserved": set(initial["reservations"])
        <= set(final["reservations"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "control-plane",
            "databricks",
            "storage-probe",
            "vault-probe",
            "costs",
        ],
    )
    args = parser.parse_args()
    config = load(CONFIG)
    foundation = load(ROOT / "platform/config/foundation-resources.json")
    actions = {
        "control-plane": lambda: collect_control_plane(config, foundation),
        "databricks": lambda: collect_databricks(config, foundation),
        "storage-probe": lambda: probe_storage(config),
        "vault-probe": lambda: probe_vault(config),
        "costs": lambda: refresh_costs(config),
    }
    report = {
        **source_binding(),
        "observed_at": now(),
        "phase": 1,
        "command": args.command,
        "status": "PASS",
        "results": actions[args.command](),
    }
    save(OUTPUT / f"{args.command}.json", report)
    print(
        json.dumps(
            {
                "status": "PASS",
                "command": args.command,
                "evidence": f"output/foundation-validation/{args.command}.json",
            }
        )
    )


if __name__ == "__main__":
    main()
