"""Minimum authenticated Apps OBO fixture, with per-request actual identities."""

import argparse
import hashlib
import json
import time
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone

import requests
import tomllib
from app_lifecycle import wait_initial_provisioning
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound
from databricks.sdk.service import apps, catalog, dashboards, iam, sql, workspace
from deploy_security_baseline import execute
from foundation_support import ROOT, databricks_clients, load, now, save
from platform_control import ControlStore, admit_operation, instant, register
from prepare_probe_artifacts import prepare
from probe_role_matrix import scope_insert
from probe_security_baseline import principal_client
from semantic_dashboard_fixture import CREATE_METRIC, METRIC, QUERY, definition

NAME = "hcp-foundation-authorization"
TABLE = "hc_test.gold.app_authorization_fixture"
DIRECTORY = "/Workspace/hcp/probes/authorization-app"
WAREHOUSE = "bd30bdac29080126"
OUTPUT = ROOT / "output/platform-foundation/app-authorization.json"


def main():
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-rejected-scopes", action="store_true")
    parser.add_argument("--resume-initial-provisioning", action="store_true")
    parser.add_argument("--resume-omitted-readback", action="store_true")
    parser.add_argument("--resume-authorization-protocol", action="store_true")
    parser.add_argument("--retry-sql-connector", action="store_true")
    parser.add_argument("--semantic-dashboard", action="store_true")
    args = parser.parse_args()
    maximum_seconds = 540 if args.semantic_dashboard else 900
    if args.semantic_dashboard:
        # Whole-attempt accounting deliberately includes setup/cleanup time.
        histories = [
            load(OUTPUT.with_name(name))
            for name in [
                "app-authorization-initial-provisioning-attempt.json",
                "app-authorization-omitted-readback-attempt.json",
                "app-authorization-service-principal-attempt.json",
                "app-authorization-rest-scope-attempt.json",
                "app-authorization.json",
            ]
        ]
        assert histories[-1]["status"] == "PASS"
        if (
            sum(item["elapsed_seconds"] for item in histories) + maximum_seconds
            > 33 * 60
        ):
            raise PermissionError("Semantic follow-up exceeds aggregate Apps allowance")
        OUTPUT = OUTPUT.with_name("semantic-dashboard.json")
    if OUTPUT.exists():
        prior = load(OUTPUT)
        archive = OUTPUT.with_name("app-authorization-rejected-scopes.json")
        rejected_scope = (
            args.resume_rejected_scopes
            and prior.get("failure_type") == "InvalidParameterValue"
            and not prior.get("app_identity")
            and not prior.get("cleanup_errors")
            and not archive.exists()
        )
        lifecycle_resume = (
            args.resume_initial_provisioning
            and prior.get("failure_type") == "BadRequest"
        )
        if lifecycle_resume:
            reconciliation = load(
                ROOT / "output/platform-foundation/app-cleanup-reconciliation.json"
            )
            archive = OUTPUT.with_name(
                "app-authorization-initial-provisioning-attempt.json"
            )
            lifecycle_resume = (
                reconciliation.get("deleted") is True
                and not archive.exists()
                and prior.get("elapsed_seconds", 1800) + 900 < 1800
            )
        readback_resume = (
            args.resume_omitted_readback
            and prior.get("failure_type") == "AssertionError"
        )
        if readback_resume:
            archive = OUTPUT.with_name(
                "app-authorization-omitted-readback-attempt.json"
            )
            readback_resume = (
                (not archive.exists() or load(archive) == prior)
                and prior.get("cleanup", {}).get("app_deleted") is True
                and not prior.get("cleanup_errors")
                and prior.get("app_identity", "").isdigit()
                and prior.get("elapsed_seconds", 1800) + 22 * 60 < 1800
            )
        authorization_resume = (
            args.resume_authorization_protocol
            and prior.get("failure_type") == "AssertionError"
        )
        if authorization_resume:
            archive = OUTPUT.with_name(
                "app-authorization-service-principal-attempt.json"
            )
            earlier = load(
                OUTPUT.with_name("app-authorization-initial-provisioning-attempt.json")
            )
            readback = load(
                OUTPUT.with_name("app-authorization-omitted-readback-attempt.json")
            )
            authorization_resume = (
                (not archive.exists() or load(archive) == prior)
                and prior.get("cleanup", {}).get("app_deleted") is True
                and not prior.get("cleanup_errors")
                and "sql:restricted-query" in prior.get("effective_user_api_scopes", [])
                and sum(
                    item.get("elapsed_seconds", 1800)
                    for item in [prior, earlier, readback]
                )
                + 16 * 60
                <= 1800
            )
        connector_retry = False
        if args.retry_sql_connector:
            archive = OUTPUT.with_name("app-authorization-rest-scope-attempt.json")
            previous = [
                load(OUTPUT.with_name(name))
                for name in [
                    "app-authorization-initial-provisioning-attempt.json",
                    "app-authorization-omitted-readback-attempt.json",
                    "app-authorization-service-principal-attempt.json",
                ]
            ]
            connector_retry = (
                (not archive.exists() or load(archive) == prior)
                and prior.get("failure_type") == "AssertionError"
                and prior.get("human_unmapped_protocol", {})
                .get("response", {})
                .get("stage")
                == "query"
                and prior.get("cleanup", {}).get("app_deleted") is True
                and not prior.get("cleanup_errors")
                and sum(
                    item.get("elapsed_seconds", 1980) for item in [prior, *previous]
                )
                + 900
                <= 1980
            )
        if not (
            rejected_scope
            or lifecycle_resume
            or readback_resume
            or authorization_resume
            or connector_retry
        ):
            raise PermissionError(
                "An Apps attempt already exists; reconcile before retry"
            )
        save(archive, prior)
    source = ROOT / "platform/probes/authorization_app"
    files = [
        source / name for name in ["app.py", "app.yaml", "pyproject.toml", "uv.lock"]
    ]
    project = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))
    wheel = (
        source
        / project["tool"]["uv"]["sources"]["intellify-healthcare-platform"]["path"]
    )
    if not wheel.exists():
        prepare()
    locked = tomllib.loads((source / "uv.lock").read_text(encoding="utf-8"))
    package = next(
        p for p in locked["package"] if p["name"] == "intellify-healthcare-platform"
    )
    assert (
        package["wheels"][0]["hash"]
        == "sha256:" + hashlib.sha256(wheel.read_bytes()).hexdigest()
    )
    files.append(wheel)
    report = {"status": "INCOMPLETE", "started_at": now(), "cases": [], "cleanup": {}}
    report["source_hashes"] = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in files
    }
    report["runner_sha256"] = hashlib.sha256(
        (ROOT / "platform/scripts/probe_app_authorization.py").read_bytes()
    ).hexdigest()
    identities = load(
        ROOT / "output/platform-foundation/authorization-identities.json"
    )["principals"]
    records = [identities["clinical"], identities["analysts"]]
    account, operator = databricks_clients()
    store = ControlStore()
    if (
        instant(
            (store.read()[0].get("session") or {}).get(
                "deadline_utc", "1970-01-01T00:00:00Z"
            )
        )
        - datetime.now(timezone.utc)
    ).total_seconds() < maximum_seconds:
        raise PermissionError("Fifteen guarded minutes required before the App fixture")
    admit_operation(store, "app-authorization-lifecycle", "app_minutes", 30)
    if args.retry_sql_connector:
        admit_operation(store, "app-thrift-followup", "app_minutes", 3)
    admit_operation(store, "app-authorization-sql", "sql_minutes", 20)
    if args.resume_initial_provisioning:
        admit_operation(store, "app-provisioning-retry-sql", "sql_minutes", 10)
    if args.resume_omitted_readback:
        admit_operation(store, "app-forwarded-protocol-sql", "sql_minutes", 10)
    if args.resume_authorization_protocol:
        admit_operation(store, "app-native-authorization-sql", "sql_minutes", 10)
    report["cost_admitted_at"] = now()
    save(OUTPUT, report)
    start = time.monotonic()
    created = False
    dashboard_id = None
    grants = []
    app_principal = None
    stack = ExitStack()
    original_warehouse_acl = []
    for item in operator.warehouses.get_permissions(WAREHOUSE).access_control_list:
        explicit = [
            permission
            for permission in item.all_permissions or []
            if not permission.inherited
        ]
        if len(explicit) > 1:
            raise PermissionError("Ambiguous warehouse ACL; do not mutate")
        if explicit:
            original_warehouse_acl.append(
                sql.WarehouseAccessControlRequest(
                    user_name=item.user_name,
                    group_name=item.group_name,
                    service_principal_name=item.service_principal_name,
                    permission_level=explicit[0].permission_level,
                )
            )

    def command(statement):
        return execute(operator, WAREHOUSE, statement, control=store)

    def grant(kind, name, principal, privileges):
        prior = operator.grants.get(kind, name)
        existing = {
            p.value
            for a in prior.privilege_assignments or []
            if a.principal == principal
            for p in a.privileges or []
        }
        added = [p for p in privileges if p.value not in existing]
        if added:
            operator.grants.update(
                kind,
                name,
                changes=[catalog.PermissionsChange(principal=principal, add=added)],
            )
            grants.append((kind, name, principal, added))

    def http(client, url, headers=None, authenticated=True):
        remaining = maximum_seconds - 120 - (time.monotonic() - start)
        if remaining <= 0:
            raise TimeoutError("App capability probe deadline reached")
        credentials = client.config.authenticate() if authenticated else {}
        with requests.Session() as session:
            session.trust_env = False
            response = session.get(
                url,
                headers={**credentials, **(headers or {})},
                timeout=min(100, remaining),
                allow_redirects=False,
            )
        # Never serialize request objects, headers or tokens into evidence.
        if response.status_code == 200:
            return response.status_code, response.json()
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = None
        safe = {}
        if isinstance(detail, dict):
            for key in [
                "code",
                "stage",
                "user_token_present",
                "error_type",
                "error_code",
            ]:
                value = detail.get(key)
                if (
                    value is None
                    or type(value) is bool
                    or isinstance(value, str)
                    and len(value) < 81
                    and all(c.isalnum() or c == "_" for c in value)
                ):
                    safe[key] = value
        elif isinstance(detail, str) and detail in {
            "CALLER_NOT_AUTHORIZED",
            "QUERY_NOT_AUTHORIZED_OR_AVAILABLE",
            "QUERY_DEADLINE",
        }:
            safe["code"] = detail
        return response.status_code, safe

    try:
        human = WorkspaceClient(profile="HEALTHCARE_USER")
        human_identity = human.current_user.me()
        assert (
            human_identity.id == "143467144294554"
            and human_identity.user_name == "karthik@intellifysolutions.com"
        )
        callers = [
            stack.enter_context(
                principal_client(account, (r["databricks_id"], r["application_id"]))
            )
            for r in records
        ]
        for statement in [
            f"CREATE TABLE {TABLE} (facility_id STRING, person_name STRING) USING DELTA",
            f"INSERT INTO {TABLE} VALUES ('A', 'Fixture Alice'), ('B', 'Fixture Bob')",
            f"ALTER TABLE {TABLE} SET ROW FILTER hc_ops.security.facility_allowed ON (facility_id)",
            f"ALTER TABLE {TABLE} ALTER COLUMN person_name SET MASK hc_ops.security.mask_person_name USING COLUMNS (facility_id)",
        ]:
            command(statement)
        if args.semantic_dashboard:
            command(CREATE_METRIC)
        for record in records:
            grant(
                "catalog",
                "hc_test",
                record["application_id"],
                [catalog.Privilege.USE_CATALOG],
            )
            grant(
                "schema",
                "hc_test.gold",
                record["application_id"],
                [catalog.Privilege.USE_SCHEMA],
            )
            grant("table", TABLE, record["application_id"], [catalog.Privilege.SELECT])
            if args.semantic_dashboard:
                grant(
                    "schema",
                    "hc_test.semantic",
                    record["application_id"],
                    [catalog.Privilege.USE_SCHEMA],
                )
                grant(
                    "table",
                    METRIC,
                    record["application_id"],
                    [catalog.Privilege.SELECT],
                )
            operator.warehouses.update_permissions(
                WAREHOUSE,
                access_control_list=[
                    sql.WarehouseAccessControlRequest(
                        service_principal_name=record["application_id"],
                        permission_level=sql.WarehousePermissionLevel.CAN_USE,
                    )
                ],
            )
        command(
            "INSERT INTO hc_ops.security.principal_scope VALUES "
            + ",".join(
                scope_insert(record, 1, facility=facility)
                for record, facility in zip(records, ["A", "B"], strict=True)
            )
        )
        for index, caller in enumerate(callers):
            rows = execute(
                caller,
                WAREHOUSE,
                QUERY
                if args.semantic_dashboard
                else f"SELECT facility_id, person_name FROM {TABLE}",
                control=store,
            ).result.data_array
            expected_direct = (
                [["A" if index == 0 else "B", "1"]]
                if args.semantic_dashboard
                else ([["A", "Fixture Alice"]] if index == 0 else [["B", "[REDACTED]"]])
            )
            assert rows == expected_direct
            report["cases"].append({"case": f"direct_api_{index}", "status": "PASS"})
        if args.semantic_dashboard:
            dashboard = operator.lakeview.create(
                dashboards.Dashboard(
                    display_name="hcp-foundation-metric-scope",
                    parent_path="/Workspace/hcp",
                    warehouse_id=WAREHOUSE,
                    serialized_dashboard=json.dumps(definition()),
                ),
                dataset_catalog="hc_test",
                dataset_schema="semantic",
            )
            dashboard_id = dashboard.dashboard_id
            report["dashboard_id"] = dashboard_id
            save(OUTPUT, report)
            operator.permissions.update(
                "dashboards",
                dashboard_id,
                access_control_list=[
                    iam.AccessControlRequest(
                        service_principal_name=r["application_id"],
                        permission_level=iam.PermissionLevel.CAN_READ,
                    )
                    for r in records
                ],
            )
            published = operator.lakeview.publish(
                dashboard_id, embed_credentials=False, warehouse_id=WAREHOUSE
            )
            assert published.embed_credentials is False
            report["published_dashboard"] = published.as_dict()
            for index, caller in enumerate(callers):
                assert (
                    caller.lakeview.get_published(dashboard_id).embed_credentials
                    is False
                )
                report["cases"].append(
                    {"case": f"scoped_dashboard_share_{index}", "status": "PASS"}
                )
        operator.workspace.mkdirs(DIRECTORY + "/vendor")
        for path in files:
            operator.workspace.upload(
                DIRECTORY + "/" + path.relative_to(source).as_posix(),
                path.read_bytes(),
                format=workspace.ImportFormat.AUTO,
                overwrite=False,
            )
        # Configure explicit app-only permissions before starting its compute.
        app = operator.apps.create(
            apps.App(
                name=NAME,
                compute_size=apps.ComputeSize.MEDIUM,
                compute_min_instances=1,
                compute_max_instances=1,
                usage_policy_id="bc6afd45-e76f-3af8-89af-cca1fbf5b603",
                forward_user_access_token=True,
                # The identity defaults are injected by the platform and are
                # not accepted as explicitly requested user_api_scopes here.
                user_api_scopes=["sql:restricted-query"],
            ),
            no_compute=True,
        ).response
        created = True
        report["configuration"] = app.as_dict()
        save(OUTPUT, report)
        store.transact(
            lambda old: register(
                old, {"kind": "app", "id": NAME, "name": NAME, "owner": "api-adapter"}
            )
        )
        app = wait_initial_provisioning(operator, NAME, start + 5 * 60)
        operator.apps.set_permissions(
            NAME,
            access_control_list=[
                apps.AppAccessControlRequest(
                    user_name="karthik@intellifysolutions.com",
                    permission_level=apps.AppPermissionLevel.CAN_MANAGE,
                ),
                apps.AppAccessControlRequest(
                    group_name="hcp-platform-admins",
                    permission_level=apps.AppPermissionLevel.CAN_MANAGE,
                ),
                *[
                    apps.AppAccessControlRequest(
                        service_principal_name=r["application_id"],
                        permission_level=apps.AppPermissionLevel.CAN_USE,
                    )
                    for r in records
                ],
            ],
        )
        app_principal = str(app.service_principal_id)
        report["app_identity"] = app_principal
        remaining = max(10, maximum_seconds - 150 - (time.monotonic() - start))
        if app.compute_status.state.value == "STOPPED":
            operator.apps.start(NAME).result(timeout=timedelta(seconds=remaining))
        remaining = max(10, maximum_seconds - 150 - (time.monotonic() - start))
        operator.apps.deploy(
            NAME, apps.AppDeployment(source_code_path=DIRECTORY)
        ).result(timeout=timedelta(seconds=remaining))
        actual = operator.apps.get(NAME)
        report["app_acl"] = operator.apps.get_permissions(NAME).as_dict()
        for record in records:
            assert any(
                entry.service_principal_name == record["application_id"]
                and any(
                    permission.permission_level == apps.AppPermissionLevel.CAN_USE
                    for permission in entry.all_permissions or []
                )
                for entry in operator.apps.get_permissions(NAME).access_control_list
            )
        report["last_app_metadata"] = actual.as_dict()
        assert actual.compute_size == apps.ComputeSize.MEDIUM
        report["effective_user_api_scopes"] = actual.effective_user_api_scopes
        # Some API responses omit legacy auth readback fields. The requested
        # read-only scope is retained in source; actual caller/UC assertions
        # below are the authority for the OBO capability, never a missing field.
        if actual.effective_user_api_scopes is not None:
            assert "sql:restricted-query" in actual.effective_user_api_scopes
        url = actual.url.rstrip("/") + (
            "/api/metric" if args.semantic_dashboard else "/api/fixture"
        )
        health_status, health_body = http(human, actual.url.rstrip("/") + "/api/health")
        report["runtime"] = {"http_status": health_status, "response": health_body}
        human_status, human_body = http(human, url + "?facility_id=A")
        report["human_unmapped_protocol"] = {
            "http_status": human_status,
            "response": human_body,
        }
        save(OUTPUT, report)
        assert (
            human_status == 200
            and human_body["caller_id"] == human_identity.id
            and human_body["rows"] == []
        )
        report["cases"].append({"case": "human_user_oauth_unmapped", "status": "PASS"})
        for index, caller in enumerate(callers):
            own, other = ("A", "B") if index == 0 else ("B", "A")
            for case, facility, headers in [
                ("own_facility", own, {}),
                ("cross_facility", other, {}),
                (
                    "forged_identity",
                    own,
                    {
                        "x-facility-id": other,
                        "x-entra-object-id": records[1 - index]["entra_object_id"],
                        "x-forwarded-user": "forged-admin",
                    },
                ),
                (
                    "forged_forwarded_token",
                    other,
                    {"x-forwarded-access-token": "invalid-fixture-token"},
                ),
            ]:
                status, body = http(caller, url + "?facility_id=" + facility, headers)
                if case == "forged_forwarded_token" and status == 403:
                    pass
                else:
                    if status != 200:
                        report["http_failure"] = {
                            "index": index,
                            "case": case,
                            "http_status": status,
                            "safe_detail": body,
                        }
                    assert status == 200, (index, case, status)
                    assert body["caller_id"] == records[index]["databricks_id"]
                    expected = (
                        []
                        if facility != own
                        else [[own, "Fixture Alice" if index == 0 else "[REDACTED]"]]
                    )
                    if args.semantic_dashboard and facility == own:
                        expected = [[own, 1]]
                    assert body["rows"] == expected
                report["cases"].append(
                    {
                        "case": f"obo_{index}_{case}",
                        "status": "PASS",
                        "http_status": status,
                    }
                )
        status, _ = http(callers[0], url, authenticated=False)
        assert status in {401, 403}
        report["cases"].append(
            {"case": "unauthenticated", "status": "PASS", "http_status": status}
        )
        command(
            "INSERT INTO hc_ops.security.principal_scope VALUES "
            + scope_insert(records[0], 2, mode="revoked")
        )
        status, body = http(callers[0], url + "?facility_id=A")
        assert status == 200 and body["rows"] == []
        report["cases"].append(
            {"case": "revoked_with_existing_token", "status": "PASS"}
        )
        if args.semantic_dashboard:
            # Exercise the GA webhook authentication shape against the same
            # protected Apps ingress. No anonymous handler or destination is
            # enabled. OAuth webhook destinations require a separate Beta.
            credentials = callers[1].config
            with requests.Session() as session:
                session.trust_env = False
                response = session.post(
                    actual.url.rstrip("/") + "/api/health",
                    json={"event_type": "jobs.on_failure", "run": {"run_id": 0}},
                    auth=(credentials.client_id, credentials.client_secret),
                    timeout=15,
                    allow_redirects=False,
                )
            assert response.status_code in {401, 403}
            report["optional_webhook"] = {
                "status": "UNSUPPORTED_DISABLED",
                "attempt": "Notification-shaped HTTP Basic POST to protected Apps ingress using the same valid scoped service principal used for successful bearer requests",
                "http_status": response.status_code,
                "actual_jobs_notification_engine_delivery_tested": False,
                "reason": "Approved GA GenericWebhookConfig exposes HTTP Basic only; Apps ingress accepts OAuth bearer. OAuth destinations are a separate Beta and were not enabled.",
                "receiver_enabled": False,
                "notification_destination_created": False,
                "polling_fallback": "runtime-probe-reconciliation.json",
            }
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["failure_type"] = type(error).__name__
        raise
    finally:
        errors = []
        actions = []
        if dashboard_id:
            actions.append(
                (
                    "dashboard_unpublished",
                    lambda: operator.lakeview.unpublish(dashboard_id),
                )
            )
            actions.append(
                ("dashboard_trashed", lambda: operator.lakeview.trash(dashboard_id))
            )
        if created:

            def stop_delete_app():
                current = operator.apps.get(NAME)
                if (
                    not current.compute_status
                    or current.compute_status.state.value != "STOPPED"
                ):
                    operator.apps.stop(NAME).result(timeout=timedelta(minutes=2))
                operator.apps.delete(NAME)
                deletion_deadline = time.monotonic() + 90
                while time.monotonic() < deletion_deadline:
                    try:
                        operator.apps.get(NAME)
                    except NotFound:
                        return
                    time.sleep(3)
                raise TimeoutError("App deletion did not settle")

            actions.append(("app_deleted", stop_delete_app))
        principals = ",".join(
            "'" + record["application_id"] + "'" for record in records
        )
        actions.extend(
            [
                (
                    "scope_bindings_removed",
                    lambda: command(
                        f"DELETE FROM hc_ops.security.principal_scope WHERE principal_name IN ({principals})"
                    ),
                ),
                *(
                    (
                        [
                            (
                                "metric_removed",
                                lambda: command(f"DROP VIEW IF EXISTS {METRIC}"),
                            )
                        ]
                    )
                    if args.semantic_dashboard
                    else []
                ),
                ("fixture_removed", lambda: command(f"DROP TABLE IF EXISTS {TABLE}")),
            ]
        )
        for kind, name, principal, privileges in reversed(grants):
            if kind != "table":
                actions.append(
                    (
                        "grant_removed_" + principal + "_" + kind,
                        lambda k=kind, n=name, p=principal, v=privileges: (
                            operator.grants.update(
                                k,
                                n,
                                changes=[
                                    catalog.PermissionsChange(principal=p, remove=v)
                                ],
                            )
                        ),
                    )
                )
        actions.append(
            (
                "warehouse_acl_restored",
                lambda: operator.warehouses.set_permissions(
                    WAREHOUSE, access_control_list=original_warehouse_acl
                ),
            )
        )
        actions.append(
            (
                "source_directory_removed",
                lambda: operator.workspace.delete(DIRECTORY, recursive=True),
            )
        )
        for name, action in actions:
            try:
                action()
                report["cleanup"][name] = True
            except Exception as error:  # noqa: BLE001 -- attempt every cleanup and fail the gate
                errors.append({"operation": name, "error_type": type(error).__name__})
        try:
            stack.close()
            report["cleanup"]["oauth_secrets_revoked"] = True
        except Exception as error:  # noqa: BLE001 -- record credential cleanup failure
            errors.append(
                {
                    "operation": "oauth_secret_revocation",
                    "error_type": type(error).__name__,
                }
            )
        if created:
            try:
                operator.apps.get(NAME)
                errors.append(
                    {"operation": "app_delete_readback", "error_type": "StillExists"}
                )
            except NotFound:
                report["cleanup"]["app_delete_readback"] = True
        report["cleanup_errors"] = errors
        report["completed_at"] = now()
        report["elapsed_seconds"] = round(time.monotonic() - start, 3)
        if errors or report["elapsed_seconds"] > maximum_seconds:
            report["status"] = "CLEANUP_FAILED"
        save(OUTPUT, report)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"])}))


if __name__ == "__main__":
    main()
