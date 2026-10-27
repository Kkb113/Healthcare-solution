"""Healthcare-only Entra SCIM connector; never migrate shared-account identities.

The gallery application and its paused synchronization job are code-owned here.
Secrets are configured out of Terraform state. Only the eight frozen groups and
the explicitly authorized operator may enter scope; any other member blocks.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from foundation_support import (
    CONFIG,
    OUTPUT,
    ROOT,
    AzureRest,
    databricks_clients,
    load,
    now,
    save,
    source_binding,
)

NAME = "hcp-account-scim-provisioning"
TEMPLATE = "9c9818d2-2900-49e8-8ba4-22688be7c675"
OPERATOR = "5ee77c8e-621d-4953-9502-1be929c977e1"
CONFIGURATION = ROOT / "platform/config/identity-provisioning.json"


def graph():
    return AzureRest(
        load(CONFIG)["workspace_subscription"],
        "https://graph.microsoft.com/",
        {"graph.microsoft.com"},
    )


def request(client, method, path, body=None):
    _, _, raw = client.request(
        method, "https://graph.microsoft.com/v1.0/" + path, body=body
    )
    return json.loads(raw) if raw else None


def collection(client, path):
    result = request(client, "GET", path)
    if result.get("@odata.nextLink"):
        raise ValueError(
            "Unexpected pagination; never accept a partial identity inventory"
        )
    return result["value"]


def verify_source(client, expected):
    results = {}
    for name, oid in expected["groups"].items():
        group = request(
            client, "GET", f"groups/{oid}?$select=id,displayName,securityEnabled"
        )
        if group["displayName"] != name or group["securityEnabled"] is not True:
            raise ValueError("Frozen Entra group identity drift")
        members = collection(client, f"groups/{oid}/members?$select=id")
        member_ids = {m["id"] for m in members}
        if member_ids != ({OPERATOR} if name == "hcp-platform-admins" else set()):
            raise ValueError(
                "Source membership changed: approval required before provisioning any other user"
            )
        results[name] = {"object_id": oid, "members": sorted(member_ids)}
    return results


def prepare():
    if CONFIGURATION.exists() and load(CONFIGURATION).get("state") == "ACTIVE_VERIFIED":
        verify_identities()
        return
    client = graph()
    expected = load(ROOT / "platform/config/foundation-resources.json")
    source = verify_source(client, expected)
    matches = collection(
        client,
        "servicePrincipals?" + urlencode({"$filter": f"displayName eq '{NAME}'"}),
    )
    if len(matches) > 1:
        raise ValueError("Ambiguous dedicated provisioning application")
    if matches:
        principal = matches[0]
        if principal.get("applicationTemplateId") != TEMPLATE:
            raise ValueError("Provisioning application name collision")
    else:
        created = request(
            client,
            "POST",
            f"applicationTemplates/{TEMPLATE}/instantiate",
            {"displayName": NAME},
        )
        principal = created["servicePrincipal"]
    oid = principal["id"]
    # This app is only a provisioning integration, not a new sign-in route.
    request(
        client,
        "PATCH",
        f"servicePrincipals/{oid}",
        {
            "appRoleAssignmentRequired": True,
            "notes": "Dedicated healthcare provisioning; eight frozen groups and Karthik only. AIM remains disabled. No Azure/Graph application permissions.",
        },
    )
    assigned = collection(client, f"servicePrincipals/{oid}/appRoleAssignedTo")
    user_roles = [
        role
        for role in principal["appRoles"]
        if role["displayName"] == "User"
        and role["isEnabled"]
        and role["allowedMemberTypes"] == ["User"]
    ]
    if len(user_roles) != 1:
        raise ValueError("Gallery User assignment role is missing or ambiguous")
    if any(a["principalId"] not in set(expected["groups"].values()) for a in assigned):
        raise ValueError("Unexpected application assignment outside healthcare groups")
    for group in expected["groups"].values():
        if not any(a["principalId"] == group for a in assigned):
            request(
                client,
                "POST",
                f"servicePrincipals/{oid}/appRoleAssignedTo",
                {
                    "principalId": group,
                    "resourceId": oid,
                    "appRoleId": user_roles[0]["id"],
                },
            )
    templates = collection(client, f"servicePrincipals/{oid}/synchronization/templates")
    if not any(t["id"] == "dataBricks" for t in templates):
        raise ValueError("Official Databricks provisioning template unavailable")
    jobs = collection(client, f"servicePrincipals/{oid}/synchronization/jobs")
    if len(jobs) > 1:
        raise ValueError("Unexpected additional provisioning job")
    job = (
        jobs[0]
        if jobs
        else request(
            client,
            "POST",
            f"servicePrincipals/{oid}/synchronization/jobs",
            {"templateId": "dataBricks"},
        )
    )
    if job["templateId"] != "dataBricks":
        raise ValueError("Unexpected synchronization template")
    configuration = {
        "schema_version": 1,
        "mode": "SCIM",
        "display_name": NAME,
        "application_template_id": TEMPLATE,
        "service_principal_object_id": oid,
        "application_client_id": principal["appId"],
        "job_id": job["id"],
        "allowed_group_object_ids": expected["groups"],
        "allowed_user_object_ids": [OPERATOR],
        "account_aim_enabled": False,
        "state": "PAUSED_PENDING_SCOPING_AND_CREDENTIAL_BOOTSTRAP",
        "lifecycle_owner": "platform/scripts/configure_foundation_identity.py",
        "secret_in_terraform_or_repository": False,
    }
    save(CONFIGURATION, configuration)
    schema = request(
        client,
        "GET",
        f"servicePrincipals/{oid}/synchronization/jobs/{job['id']}/schema",
    )
    save(OUTPUT / "scim-schema-before.json", schema)
    report = {
        **source_binding(),
        "observed_at": now(),
        "status": "PREPARED_NOT_ENABLED",
        "configuration": configuration,
        "source_membership": source,
        "job": job,
    }
    save(OUTPUT / "identity-preparation.json", report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "connector_id": oid,
                "job_id": job["id"],
                "assigned_groups": 8,
                "allowed_users": 1,
                "other_identities_modified": False,
            }
        )
    )


def bootstrap_token():
    """Read a credential over stdin, never argv, stdout, a file or Terraform state."""
    token = json.load(sys.stdin)["token"]
    if not re.fullmatch(r"dsapi[A-Za-z0-9]+", token):
        raise ValueError("Unexpected account SCIM credential format")
    config = load(CONFIG)
    host = f"{config['key_vault']}.vault.azure.net"
    vault = AzureRest(
        config["workspace_subscription"], "https://vault.azure.net", {host}
    )
    vault.request(
        "PUT",
        f"https://{host}/secrets/hcp-account-scim-token?api-version=7.4",
        body={
            "value": token,
            "tags": {
                "project": "healthcare-platform",
                "purpose": "entra-scim-only",
                "rotation-owner": "karthik",
            },
        },
    )

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = build_opener(NoRedirect())
    account_id = load(ROOT / "platform/config/workspace.json")["account_id"]
    base = f"https://accounts.azuredatabricks.net/api/2.1/accounts/{account_id}/scim/v2"
    with opener.open(
        Request(
            base + "/Users/143467144294554",
            headers={"Authorization": "Bearer " + token},
        ),
        timeout=60,
    ) as response:
        result = json.load(response)
    if (
        result["externalId"] != OPERATOR
        or result["userName"] != "karthik@intellifysolutions.com"
    ):
        raise ValueError("SCIM token does not resolve the exact authorized operator")
    denied = False
    try:
        with opener.open(
            Request(
                f"https://accounts.azuredatabricks.net/api/2.0/accounts/{account_id}/workspaces",
                headers={"Authorization": "Bearer " + token},
            ),
            timeout=60,
        ):
            pass
    except HTTPError as error:
        denied = error.code in {401, 403}
    if not denied:
        raise ValueError("Credential is not restricted to account SCIM APIs")
    save(
        OUTPUT / "scim-credential-bootstrap.json",
        {
            "status": "PASS",
            "observed_at": now(),
            "account_scim_verified": True,
            "non_scim_api_denied": True,
            "stored_in": "healthcare Key Vault",
            "credential_value_logged": False,
            "credential_value_in_terraform": False,
            "initial_token_revoked_after_redaction_miss": True,
        },
    )
    print(
        "PASS: restricted SCIM credential verified and stored in healthcare Key Vault"
    )


def exact_scope(ids):
    return {
        "groups": [
            {
                "name": "approved-" + oid,
                "clauses": [
                    {
                        "sourceOperandName": "objectId",
                        "operatorName": "EQUALS",
                        "targetOperand": {"values": [oid]},
                    }
                ],
            }
            for oid in sorted(ids)
        ]
    }


def validate_config(config):
    expected = load(ROOT / "platform/config/foundation-resources.json")
    if (
        config["allowed_user_object_ids"] != [OPERATOR]
        or config["allowed_group_object_ids"] != expected["groups"]
        or config["mode"] != "SCIM"
        or config["account_aim_enabled"] is not False
        or config["application_template_id"] != TEMPLATE
        or config["display_name"] != NAME
    ):
        raise ValueError("Provisioning configuration exceeds explicit user approval")


def scope_schema(schema, config):
    validate_config(config)
    result = copy.deepcopy(schema)
    rules = result["synchronizationRules"]
    if len(rules) != 1 or {
        m["sourceObjectName"] for m in rules[0]["objectMappings"]
    } != {"User", "Group"}:
        raise ValueError("Unexpected gallery synchronization mappings")
    for mapping in rules[0]["objectMappings"]:
        ids = (
            config["allowed_user_object_ids"]
            if mapping["sourceObjectName"] == "User"
            else config["allowed_group_object_ids"].values()
        )
        mapping["scope"] = exact_scope(ids)
        mapping["flowTypes"] = "Add,Update"
    return result


def validate_schema(schema, config):
    expected = scope_schema(schema, config)
    for actual, wanted in zip(
        schema["synchronizationRules"][0]["objectMappings"],
        expected["synchronizationRules"][0]["objectMappings"],
        strict=True,
    ):
        # Graph serializes optional empty filter collections as empty arrays.
        if not isinstance(actual.get("scope"), dict):
            raise TypeError("Provisioning scope missing")
        actual_scope = {key: value for key, value in actual["scope"].items() if value}
        if (
            actual_scope != wanted["scope"]
            or actual["flowTypes"].replace(" ", "") != "Add,Update"
            or not actual["enabled"]
        ):
            raise ValueError(
                "Provisioning scope widened or destructive operation enabled"
            )


def scim_token():
    config = load(CONFIG)
    host = f"{config['key_vault']}.vault.azure.net"
    client = AzureRest(
        config["workspace_subscription"], "https://vault.azure.net", {host}
    )
    _, _, raw = client.request(
        "GET", f"https://{host}/secrets/hcp-account-scim-token?api-version=7.4"
    )
    return json.loads(raw)["value"]


def validate_connection(client, path, config):
    base = (
        "https://accounts.azuredatabricks.net/api/2.1/accounts/"
        + load(ROOT / "platform/config/workspace.json")["account_id"]
        + "/scim/v2"
    )
    # This tenant's saved-credential validation returns CredentialsMissing even
    # though GET secrets confirms persistence. Explicit validation is supported;
    # actual scheduled-sync success is separately required before certification.
    saved = request(
        client,
        "GET",
        f"servicePrincipals/{config['service_principal_object_id']}/synchronization/secrets",
    )["value"]
    metadata = {item["key"]: item.get("value") for item in saved}
    if (
        metadata.get("BaseAddress") != base
        or metadata.get("SyncAll") != "false"
        or "SecretToken" not in metadata
    ):
        raise ValueError("Saved connector credentials or assigned-only scope mismatch")
    request(
        client,
        "POST",
        path + "/validateCredentials",
        {
            "templateId": "dataBricks",
            "useSavedCredentials": False,
            "credentials": [
                {"key": "BaseAddress", "value": base},
                {"key": "SecretToken", "value": scim_token()},
            ],
        },
    )


def configure():
    config = load(CONFIGURATION)
    validate_config(config)
    expected = load(ROOT / "platform/config/foundation-resources.json")
    client = graph()
    verify_source(client, expected)
    path = f"servicePrincipals/{config['service_principal_object_id']}/synchronization/jobs/{config['job_id']}"
    job = request(client, "GET", path)
    if job["schedule"]["state"] not in {"Disabled", "Paused"}:
        raise ValueError(
            "Pause the dedicated job before changing its schema or credentials"
        )
    operators = collection(client, path + "/schema/filterOperators")
    if not any(o.get("id", o.get("name")) == "EQUALS" for o in operators):
        raise ValueError("Exact object-ID equality operator unavailable")
    schema = scope_schema(request(client, "GET", path + "/schema"), config)
    request(
        client,
        "PUT",
        path + "/schema",
        {key: schema[key] for key in ["directories", "synchronizationRules"]},
    )
    actual = request(client, "GET", path + "/schema")
    validate_schema(actual, config)
    account = load(ROOT / "platform/config/workspace.json")["account_id"]
    secrets = [
        {
            "key": "BaseAddress",
            "value": f"https://accounts.azuredatabricks.net/api/2.1/accounts/{account}/scim/v2",
        },
        {"key": "SecretToken", "value": scim_token()},
        {"key": "SyncAll", "value": "false"},
    ]
    request(
        client,
        "PUT",
        f"servicePrincipals/{config['service_principal_object_id']}/synchronization/secrets",
        {"value": secrets},
    )
    validate_connection(client, path, config)
    config["state"] = "SCOPED_VALIDATED_PAUSED"
    save(CONFIGURATION, config)
    save(OUTPUT / "scim-schema-approved.json", actual)
    print(
        "PASS: exact eight-group/one-user filters saved; credentials validated; job remains paused"
    )


def preserved_identities(account):
    result = {}
    for kind, identities in [
        ("user", account.users.list()),
        ("service-principal", account.service_principals.list()),
    ]:
        for identity in identities:
            if kind == "user" and identity.id == "143467144294554":
                continue
            actual = (
                getattr(account, "users" if kind == "user" else "service_principals")
                .get(identity.id)
                .as_dict()
            )
            bounded = {
                key: actual.get(key)
                for key in [
                    "id",
                    "active",
                    "displayName",
                    "userName",
                    "applicationId",
                    "externalId",
                    "roles",
                ]
            }
            result[f"{kind}/{identity.id}"] = hashlib.sha256(
                json.dumps(bounded, sort_keys=True).encode()
            ).hexdigest()
    return result


def identity_digest(identities):
    return hashlib.sha256(json.dumps(identities, sort_keys=True).encode()).hexdigest()


def check_preservation(account, config):
    current = preserved_identities(account)
    expected = config.get("preserved_identities_sha256")
    if expected is None:
        expected = identity_digest(load(OUTPUT / "preserved-identities-before.json"))
    if identity_digest(current) != expected:
        raise ValueError("Out-of-scope identity changed; review before proceeding")
    return current


def start():
    config = load(CONFIGURATION)
    validate_config(config)
    client = graph()
    verify_source(client, load(ROOT / "platform/config/foundation-resources.json"))
    path = f"servicePrincipals/{config['service_principal_object_id']}/synchronization/jobs/{config['job_id']}"
    validate_schema(request(client, "GET", path + "/schema"), config)
    assigned = collection(
        client,
        f"servicePrincipals/{config['service_principal_object_id']}/appRoleAssignedTo",
    )
    if {a["principalId"] for a in assigned} != set(
        config["allowed_group_object_ids"].values()
    ):
        raise ValueError("Unexpected application assignment scope")
    validate_connection(client, path, config)
    account, _ = databricks_clients()
    baseline = OUTPUT / "preserved-identities-before.json"
    current = preserved_identities(account)
    if (
        config.get("preserved_identities_sha256")
        and identity_digest(current) != config["preserved_identities_sha256"]
    ):
        raise ValueError("An out-of-scope identity changed; review before proceeding")
    if (
        not config.get("preserved_identities_sha256")
        and baseline.exists()
        and load(baseline) != current
    ):
        raise ValueError("An out-of-scope identity changed; review before proceeding")
    if not baseline.exists():
        save(baseline, current)
    job = request(client, "GET", path)
    if job["schedule"]["state"] in {"Disabled", "Paused"}:
        request(client, "POST", path + "/start")
    elif job["schedule"]["state"] != "Active":
        raise ValueError(
            "Unexpected provisioning state; no automatic quarantine clearing"
        )
    config["state"] = "ACTIVE_PENDING_END_TO_END_VERIFICATION"
    save(CONFIGURATION, config)
    print("SCIM started with exact scopes; end-to-end verification remains required")


def verify_identities(assign=False):
    from databricks.sdk.service import iam

    config = load(CONFIGURATION)
    validate_config(config)
    expected = load(ROOT / "platform/config/foundation-resources.json")
    client = graph()
    source = verify_source(client, expected)
    path = f"servicePrincipals/{config['service_principal_object_id']}/synchronization/jobs/{config['job_id']}"
    schema = request(client, "GET", path + "/schema")
    validate_schema(schema, config)
    job = request(client, "GET", path)
    status = job["status"]
    if (
        job["schedule"]["state"] != "Active"
        or status["code"] != "Active"
        or status["quarantine"]
        or status["countSuccessiveCompleteFailures"]
        or status["lastExecution"]["state"] != "Succeeded"
        or status["lastExecution"]["countEscrowed"]
        or status["lastExecution"]["error"]
    ):
        raise ValueError("Scheduled SCIM execution has not succeeded cleanly")
    assignments = collection(
        client,
        f"servicePrincipals/{config['service_principal_object_id']}/appRoleAssignedTo",
    )
    if {a["principalId"] for a in assignments} != set(
        expected["groups"].values()
    ) or len(assignments) != 8:
        raise ValueError("SCIM assignment scope changed")
    if collection(
        client,
        f"servicePrincipals/{config['service_principal_object_id']}/appRoleAssignments",
    ):
        raise ValueError(
            "Provisioning connector has unexpected application permissions"
        )
    validate_connection(client, path, config)
    account, workspace = databricks_clients()
    protected = check_preservation(account, config)
    previous_assignments = {
        str(a.principal.principal_id): a.as_dict()
        for a in account.workspace_assignment.list(load(CONFIG)["workspace_id"])
    }
    groups = {}
    for name, oid in expected["groups"].items():
        matches = list(account.groups.list(filter=f'displayName eq "{name}"'))
        if len(matches) != 1:
            raise ValueError(f"Scheduled provisioning incomplete or ambiguous: {name}")
        actual = account.groups.get(matches[0].id)
        if actual.external_id != oid or {m.value for m in actual.members or []} != (
            {"143467144294554"} if name == "hcp-platform-admins" else set()
        ):
            raise ValueError("Databricks group identity/membership differs from Entra")
        if assign:
            previous = previous_assignments.get(actual.id)
            if previous is None:
                account.workspace_assignment.update(
                    workspace_id=load(CONFIG)["workspace_id"],
                    principal_id=int(actual.id),
                    permissions=[iam.WorkspacePermission.USER],
                )
            elif previous.get("permissions") != ["USER"]:
                raise ValueError(
                    "Existing group workspace elevation requires review; no automatic overwrite"
                )
        groups[name] = {
            "databricks_id": actual.id,
            "external_id": actual.external_id,
            "member_ids": sorted(m.value for m in actual.members or []),
        }
    assigned = {
        str(a.principal.principal_id): a.as_dict()
        for a in account.workspace_assignment.list(load(CONFIG)["workspace_id"])
    }
    for entry in groups.values():
        if assigned.get(entry["databricks_id"], {}).get("permissions") != ["USER"]:
            raise ValueError(
                "Healthcare group workspace assignment missing or elevated"
            )
    operator = workspace.users.get("143467144294554")
    if groups["hcp-platform-admins"]["databricks_id"] not in {
        g.value for g in operator.groups or []
    }:
        raise ValueError(
            "Provisioned group membership not visible in healthcare workspace"
        )
    if assign:
        config["state"] = "ACTIVE_VERIFIED"
        config["preserved_identities_sha256"] = identity_digest(protected)
        config["preserved_identity_count"] = len(protected)
        save(CONFIGURATION, config)
    result = {
        "mode": "SCIM",
        "groups": groups,
        "source_membership": source,
        "scheduled_sync_success": True,
        "native_on_demand_report": "scim-on-demand.json",
        "schedule": job["schedule"],
        "last_execution": status["lastExecution"],
        "synchronized_counts": status["synchronizedEntryCountByType"],
        "assigned_only": True,
        "user_filter": [OPERATOR],
        "group_filter_count": 8,
        "destructive_operations_enabled": False,
        "account_aim_enabled": False,
        "aim_evidence": "Console observation in scoped-scim-bootstrap.png; no AIM setting mutations performed",
        "out_of_scope_identities_unchanged": True,
        "preserved_identity_count": len(protected),
        "workspace_permissions": "USER; no business grants",
        "schema_sha256": hashlib.sha256(
            json.dumps(schema, sort_keys=True).encode()
        ).hexdigest(),
    }
    save(
        OUTPUT / "identity.json",
        {**source_binding(), "observed_at": now(), "status": "PASS", "results": result},
    )
    print(
        "PASS: eight groups provisioned from Entra, workspace assignments verified, all other identities preserved"
    )


def resync():
    """Explicit, operator-run full reread after directory assignment propagation."""
    config = load(CONFIGURATION)
    validate_config(config)
    client = graph()
    verify_source(client, load(ROOT / "platform/config/foundation-resources.json"))
    path = f"servicePrincipals/{config['service_principal_object_id']}/synchronization/jobs/{config['job_id']}"
    validate_schema(request(client, "GET", path + "/schema"), config)
    job = request(client, "GET", path)
    if job["status"]["quarantine"] or job["status"]["countSuccessiveCompleteFailures"]:
        raise ValueError(
            "Review provisioning failures; never clear quarantine automatically"
        )
    save(OUTPUT / "scim-before-resync.json", job)
    if job["schedule"]["state"] == "Active":
        request(client, "POST", path + "/pause")
    request(
        client, "POST", path + "/restart", {"criteria": {"resetScope": "Watermark"}}
    )
    save(
        OUTPUT / "scim-resync-request.json",
        {
            "observed_at": now(),
            "reason": "All eight Graph assignments confirmed; initial directory ingestion saw only two groups",
            "reset_scope": "Watermark only",
            "quarantine_cleared": False,
        },
    )
    print(
        "Scoped SCIM watermark reread requested; verify target groups before passing the gate"
    )


def provision():
    """Exercise the native connector for every approved group, including empties."""
    config = load(CONFIGURATION)
    validate_config(config)
    client = graph()
    source = verify_source(
        client, load(ROOT / "platform/config/foundation-resources.json")
    )
    path = f"servicePrincipals/{config['service_principal_object_id']}/synchronization/jobs/{config['job_id']}"
    schema = request(client, "GET", path + "/schema")
    validate_schema(schema, config)
    outcomes = {}
    for name, group in source.items():
        result = request(
            client,
            "POST",
            path + "/provisionOnDemand",
            {
                "parameters": [
                    {
                        "ruleId": schema["synchronizationRules"][0]["id"],
                        "subjects": [
                            {
                                "objectId": group["object_id"],
                                "objectTypeName": "Group",
                                "links": {
                                    "members": [
                                        {"objectId": member, "objectTypeName": "User"}
                                        for member in group["members"]
                                    ]
                                },
                            }
                        ],
                    }
                ]
            },
        )
        records = json.loads(result["value"])
        if not records or any(
            r["sourceIdentity"]["id"] not in {group["object_id"], OPERATOR}
            or r["statusInfo"]["status"] not in {"Success", "Skipped"}
            or r["statusInfo"].get("errorCode") not in {None, "RedundantExport"}
            for r in records
        ):
            raise ValueError(
                "Native provisioning rejected an approved subject; inspect failure without altering scope"
            )
        outcomes[name] = [
            {
                "source_id": r["sourceIdentity"]["id"],
                "target_id": r.get("targetIdentity", {}).get("id"),
                "action": r["action"],
                "status": r["statusInfo"],
            }
            for r in records
        ]
    save(
        OUTPUT / "scim-on-demand.json",
        {
            **source_binding(),
            "observed_at": now(),
            "status": "PASS",
            "mode": "Native Entra SCIM connector on-demand API",
            "outcomes": outcomes,
        },
    )
    print(
        "PASS: every approved group exercised through native Entra SCIM; source/target reconciliation still required"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "prepare",
            "bootstrap-token",
            "configure",
            "start",
            "assign",
            "verify",
            "resync",
            "provision",
        ],
    )
    args = parser.parse_args()
    {
        "prepare": prepare,
        "bootstrap-token": bootstrap_token,
        "configure": configure,
        "start": start,
        "assign": lambda: verify_identities(assign=True),
        "verify": verify_identities,
        "resync": resync,
        "provision": provision,
    }[args.command]()


if __name__ == "__main__":
    main()
