"""Eight real role principals: layers, facility/domain filtering and stale scopes."""

import json
import uuid
from contextlib import ExitStack

from configure_foundation_identity import graph, request
from databricks.sdk.service import catalog as c
from databricks.sdk.service import iam
from deploy_security_baseline import execute
from foundation_support import ROOT, databricks_clients, load, now, save
from platform_control import ControlStore, admission
from probe_security_baseline import principal_client

BASE = "hc_test"
WAREHOUSE = "bd30bdac29080126"
DOMAINS = ["clinical", "quality", "flow", "workforce", "finance", "revenue"]
LAYER_ROLES = {
    "bronze": {"platform-admins", "data-engineers"},
    "silver": {"platform-admins", "data-engineers", "data-scientists"},
    "gold": {
        "platform-admins",
        "data-engineers",
        "data-scientists",
        "analysts",
        "clinical",
        "finance",
        "operations",
        "auditors",
    },
    "features": {"platform-admins", "data-engineers", "data-scientists", "auditors"},
    "dq": {"platform-admins", "data-engineers", "data-scientists", "auditors"},
}


def domain_scope(role):
    return {
        "clinical": {"clinical", "quality", "flow"},
        "finance": {"finance", "revenue"},
        "operations": {"flow", "workforce"},
    }.get(role, set(DOMAINS))


def scope_insert(record, version, mode="active", facility="A"):
    uuid.UUID(record["application_id"])
    uuid.UUID(record["entra_object_id"])
    if (
        not record["databricks_id"].isdigit()
        or record["role"] not in {"hcp-" + name for name in LAYER_ROLES["gold"]}
        or type(version) is not int
        or version < 1
        or mode not in {"active", "revoked", "expired", "ambiguous"}
        or facility not in {"A", "B"}
    ):
        raise ValueError("Unverified identity/scope assertion")
    principal = record["application_id"]
    revoked = "current_timestamp()" if mode == "revoked" else "NULL"
    until = (
        "current_timestamp() - INTERVAL 1 MINUTE"
        if mode == "expired"
        else "current_timestamp() + INTERVAL 30 MINUTES"
    )
    phi = (
        "true" if record["role"] in {"hcp-clinical", "hcp-platform-admins"} else "false"
    )
    return f"('{uuid.uuid4()}', '807ebfbb-86ca-41a5-87df-d9c348b89f83', '{record['entra_object_id']}', '{record['databricks_id']}', '{principal}', NULL, '{record['role']}', array('{facility}'), {phi}, current_timestamp() - INTERVAL 1 DAY, {until}, {revoked}, {version}, 'verified_entra_fixture_admin', current_timestamp())"


def main():
    store = ControlStore()
    admission(store.read()[0], True)
    identity = load(ROOT / "output/platform-foundation/authorization-identities.json")
    if identity.get("status") != "PREPARED_NO_GROUP_MEMBERSHIP_NO_SECRETS":
        raise PermissionError("Verified, fresh fixture manifest required")
    account, operator = databricks_clients()
    azure = graph()
    connector = load(ROOT / "platform/config/identity-provisioning.json")
    path = f"servicePrincipals/{connector['service_principal_object_id']}/synchronization/jobs/{connector['job_id']}"
    original = request(azure, "GET", path)
    groups = {}
    added = []
    report = {"status": "INCOMPLETE", "started_at": now(), "cases": [], "cleanup": {}}
    tables = [f"{BASE}.{layer}.authorization_fixture" for layer in LAYER_ROLES]
    raw = BASE + ".bronze.raw_payload_fixture"
    oracle = BASE + ".reference.answer_access_probe"

    def sql(client, statement):
        response = execute(client, WAREHOUSE, statement, control=store)
        return response.result.data_array or []

    def deny(client, statement):
        try:
            sql(client, statement)
        except Exception as error:
            if any(
                code in str(error)
                for code in [
                    "INSUFFICIENT_PRIVILEGES",
                    "PERMISSION_DENIED",
                    "INSUFFICIENT_PERMISSIONS",
                ]
            ):
                return
            raise
        raise AssertionError("Unexpected authorized access")

    try:
        request(azure, "POST", path + "/pause")
        paused = request(azure, "GET", path)
        assert paused["schedule"]["state"] == "Paused"
        for role, record in identity["principals"].items():
            verified = request(
                azure,
                "GET",
                f"servicePrincipals/{record['entra_object_id']}?$select=id,appId",
            )
            assert (
                verified["id"] == record["entra_object_id"]
                and verified["appId"] == record["application_id"]
            )
            matches = list(
                account.groups.list(filter=f'displayName eq "{record["role"]}"')
            )
            assert len(matches) == 1
            group = account.groups.get(matches[0].id)
            groups[role] = {
                "id": group.id,
                "members": sorted(m.value for m in group.members or []),
            }
            account.groups.patch(
                group.id,
                operations=[
                    iam.Patch(
                        op=iam.PatchOp.ADD,
                        path="members",
                        value=[{"value": record["databricks_id"]}],
                    )
                ],
                schemas=[
                    iam.PatchSchema("urn:ietf:params:scim:api:messages:2.0:PatchOp")
                ],
            )
            added.append((group.id, record["databricks_id"]))
        values = ",".join(
            f"({i + offset}, '{facility}', '{domain}', 'Fixture Person', 0)"
            for offset, facility in [(0, "A"), (10, "B")]
            for i, domain in enumerate(DOMAINS)
        )
        for layer, allowed in LAYER_ROLES.items():
            table = f"{BASE}.{layer}.authorization_fixture"
            for command in [
                f"CREATE TABLE {table} (id INT, facility_id STRING, domain STRING, person_name STRING, measure INT) USING DELTA",
                f"INSERT INTO {table} VALUES {values}",
                f"ALTER TABLE {table} SET ROW FILTER hc_ops.security.scope_allowed ON (facility_id, domain)",
                f"ALTER TABLE {table} ALTER COLUMN person_name SET MASK hc_ops.security.mask_person_name USING COLUMNS (facility_id)",
            ]:
                sql(operator, command)
            operator.grants.update(
                "TABLE",
                table,
                changes=[
                    c.PermissionsChange(
                        principal="hcp-" + role, add=[c.Privilege.SELECT]
                    )
                    for role in allowed
                    if role != "platform-admins"
                ],
            )
        sql(operator, f"CREATE TABLE {raw} (marker STRING) USING DELTA")
        sql(operator, f"CREATE TABLE {oracle} (marker STRING) USING DELTA")
        with ExitStack() as stack:
            clients = {
                role: stack.enter_context(
                    principal_client(
                        account, (record["databricks_id"], record["application_id"])
                    )
                )
                for role, record in identity["principals"].items()
            }
            for role, client in clients.items():
                assert (
                    sql(client, f"SELECT * FROM {BASE}.gold.authorization_fixture")
                    == []
                )
                report["cases"].append(
                    {"role": role, "case": "unmapped", "status": "PASS"}
                )
            sql(
                operator,
                "INSERT INTO hc_ops.security.principal_scope VALUES "
                + ",".join(scope_insert(r, 1) for r in identity["principals"].values()),
            )
            for role, client in clients.items():
                for layer, allowed in LAYER_ROLES.items():
                    query = f"SELECT facility_id, domain, person_name FROM {BASE}.{layer}.authorization_fixture"
                    if role in allowed:
                        rows = sql(client, query)
                        assert len(rows) == len(domain_scope(role))
                        assert all(
                            r[0] == "A" and r[1] in domain_scope(role) for r in rows
                        )
                        expected = (
                            "Fixture Person"
                            if role in {"clinical", "platform-admins"}
                            else "[REDACTED]"
                        )
                        assert all(r[2] == expected for r in rows)
                    else:
                        deny(client, query)
                    report["cases"].append(
                        {
                            "role": role,
                            "case": "layer_" + layer,
                            "status": "PASS",
                            "allowed": role in allowed,
                        }
                    )
                assert (
                    sql(
                        client,
                        f"SELECT * FROM {BASE}.gold.authorization_fixture WHERE facility_id = 'B'",
                    )
                    == []
                )
                for name in [raw, oracle, "hc_ops.security.principal_scope"]:
                    if role == "platform-admins":
                        sql(client, f"SELECT * FROM {name}")
                    else:
                        deny(client, f"SELECT * FROM {name}")
                    report["cases"].append(
                        {
                            "role": role,
                            "case": "control_" + name,
                            "status": "PASS",
                            "allowed": role == "platform-admins",
                        }
                    )
            for version, mode in [(2, "revoked"), (3, "expired"), (4, "ambiguous")]:
                entries = [
                    scope_insert(record, version, mode)
                    for record in identity["principals"].values()
                ]
                if mode == "ambiguous":
                    entries += [
                        scope_insert(record, version, mode)
                        for record in identity["principals"].values()
                    ]
                sql(
                    operator,
                    "INSERT INTO hc_ops.security.principal_scope VALUES "
                    + ",".join(entries),
                )
                for role, client in clients.items():
                    assert (
                        sql(client, f"SELECT * FROM {BASE}.gold.authorization_fixture")
                        == []
                    )
                    report["cases"].append(
                        {"role": role, "case": mode, "status": "PASS"}
                    )
        report["status"] = "PASS"
    except Exception as error:  # noqa: BLE001 - always restore scopes, groups and connector
        report["failure"] = {"type": type(error).__name__, "message": str(error)[:700]}
    finally:
        names = ",".join(
            "'" + r["application_id"] + "'" for r in identity["principals"].values()
        )
        try:
            sql(
                operator,
                f"DELETE FROM hc_ops.security.principal_scope WHERE principal_name IN ({names})",
            )
            for table in tables + [raw, oracle]:
                sql(operator, f"DROP TABLE IF EXISTS {table}")
            report["cleanup"]["tables_and_bindings_removed"] = True
        finally:
            cleanup_errors = []
            try:
                for group_id, principal_id in reversed(added):
                    try:
                        account.groups.patch(
                            group_id,
                            operations=[
                                iam.Patch(
                                    op=iam.PatchOp.REMOVE,
                                    path=f'members[value eq "{principal_id}"]',
                                )
                            ],
                            schemas=[
                                iam.PatchSchema(
                                    "urn:ietf:params:scim:api:messages:2.0:PatchOp"
                                )
                            ],
                        )
                    except Exception as error:  # noqa: BLE001 - continue cleanup for all identities
                        cleanup_errors.append(
                            {
                                "stage": "membership_remove",
                                "type": type(error).__name__,
                                "group_id": group_id,
                            }
                        )
                for value in groups.values():
                    if (
                        sorted(
                            m.value
                            for m in account.groups.get(value["id"]).members or []
                        )
                        != value["members"]
                    ):
                        cleanup_errors.append(
                            {"stage": "membership_readback", "group_id": value["id"]}
                        )
                report["cleanup"]["original_memberships_restored"] = not cleanup_errors
            finally:
                try:
                    if original["schedule"]["state"] == "Active":
                        request(azure, "POST", path + "/start")
                        assert (
                            request(azure, "GET", path)["schedule"]["state"] == "Active"
                        )
                    report["cleanup"]["connector_state_restored"] = True
                except Exception as error:  # noqa: BLE001 - durable evidence if connector restore fails
                    cleanup_errors.append(
                        {"stage": "connector_restore", "type": type(error).__name__}
                    )
                report["cleanup_errors"] = cleanup_errors
                if cleanup_errors or not report["cleanup"].get(
                    "tables_and_bindings_removed"
                ):
                    report["status"] = "FAIL_CLEANUP"
                report["completed_at"] = now()
                save(ROOT / "output/platform-foundation/role-matrix.json", report)
    print(json.dumps(report))
    if report["status"] != "PASS":
        raise RuntimeError("Role matrix failed; inspect sanitized report")


if __name__ == "__main__":
    main()
