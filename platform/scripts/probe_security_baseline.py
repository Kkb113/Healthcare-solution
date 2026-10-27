"""Actual run-as tests against fixed nonpatient rows; all probe secrets are revoked.

The baseline bridge remains empty after cleanup. No synthetic worker row is
trusted to grant cloud privileges, and no other human identity is changed.
"""

import json
from contextlib import contextmanager

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import PermissionsChange, Privilege
from deploy_security_baseline import execute
from foundation_support import ROOT, databricks_clients, now, save

WAREHOUSE = "bd30bdac29080126"
FIXTURE = "hc_test._foundation_probe.scoped_patient_fixture"
ORACLE = "hc_test.reference.answer_access_probe"
TENANT = "807ebfbb-86ca-41a5-87df-d9c348b89f83"
JOBS = ("147109184184541", "658faa8a-72bf-4285-bf4c-3cd25778ac5f")
VALIDATION = ("144866838711850", "5d3656f0-eac7-4874-b49b-02f637df54ec")


@contextmanager
def principal_client(account, principal):
    credential = account.service_principal_secrets.create(
        principal[0], lifetime="3600s"
    )
    try:
        client = WorkspaceClient(
            host="https://adb-7405619366453187.7.azuredatabricks.net",
            auth_type="oauth-m2m",
            client_id=principal[1],
            client_secret=credential.secret,
        )
        assert client.current_user.me().user_name == principal[1]
        yield client
    finally:
        account.service_principal_secrets.delete(principal[0], credential.id)


def rows(client, query):
    response = execute(client, WAREHOUSE, query)
    return response.result.data_array or []


def expect_denied(client, query):
    try:
        rows(client, query)
    except Exception as error:
        # Only authorization failures count; transport, quota and syntax failures
        # must never be misreported as a successful security denial.
        detail = str(error)
        if not any(
            code in detail
            for code in [
                "PERMISSION_DENIED",
                "INSUFFICIENT_PERMISSIONS",
                "INSUFFICIENT_PRIVILEGES",
            ]
        ):
            raise
        return {"status": "PASS", "outcome": "DENIED"}
    raise AssertionError("Unexpected successful access")


def main():
    account, operator = databricks_clients()
    checks = []
    try:
        for command in [
            f"CREATE TABLE IF NOT EXISTS {FIXTURE} (id INT, facility_id STRING, person_name STRING) USING DELTA",
            f"DELETE FROM {FIXTURE}",
            f"INSERT INTO {FIXTURE} VALUES (1, 'A', 'Fixture Alice'), (2, 'B', 'Fixture Bob')",
            f"ALTER TABLE {FIXTURE} SET ROW FILTER hc_ops.security.facility_allowed ON (facility_id)",
            f"ALTER TABLE {FIXTURE} ALTER COLUMN person_name SET MASK hc_ops.security.mask_person_name USING COLUMNS (facility_id)",
            f"CREATE TABLE IF NOT EXISTS {ORACLE} (fixture INT) USING DELTA",
        ]:
            execute(operator, WAREHOUSE, command)
        assert rows(operator, f"SELECT * FROM {FIXTURE}") == []
        checks.append({"case": "unmapped_operator", "status": "PASS", "rows": 0})
        operator.grants.update(
            "table",
            FIXTURE,
            changes=[
                PermissionsChange(principal=VALIDATION[1], add=[Privilege.SELECT])
            ],
        )
        with principal_client(account, JOBS) as jobs:
            checks.append(
                {
                    "case": "jobs_cannot_read_oracle",
                    **expect_denied(jobs, f"SELECT * FROM {ORACLE}"),
                }
            )
            checks.append(
                {
                    "case": "jobs_cannot_read_bridge",
                    **expect_denied(
                        jobs, "SELECT * FROM hc_ops.security.principal_scope"
                    ),
                }
            )
            assert rows(jobs, f"SELECT * FROM {FIXTURE}") == []
            checks.append({"case": "unmapped_jobs_zero_rows", "status": "PASS"})
        with principal_client(account, VALIDATION) as validation:
            rows(validation, f"SELECT * FROM {ORACLE}")
            checks.append({"case": "validation_oracle_read", "status": "PASS"})
            checks.append(
                {
                    "case": "validation_cannot_modify_output",
                    **expect_denied(validation, f"DELETE FROM {FIXTURE}"),
                }
            )
    finally:
        cleanup = []
        cleanup_errors = []
        for table in [FIXTURE, ORACLE]:
            try:
                execute(operator, WAREHOUSE, f"DROP TABLE IF EXISTS {table}")
                cleanup.append(table)
            except Exception as error:  # noqa: BLE001 - preserve cleanup failure evidence
                cleanup_errors.append(
                    {"table": table, "error_type": type(error).__name__}
                )
        save(
            ROOT / "output/platform-foundation/security-probe.json",
            {
                "observed_at": now(),
                "checks": checks,
                "cleanup_tables": cleanup,
                "cleanup_errors": cleanup_errors,
                "status": "PASS"
                if len(checks) == 6 and len(cleanup) == 2
                else "INCOMPLETE",
                "scope": "Foundation runtime/oracle separation and initial default deny; eight-role matrix pending",
                "eight_role_matrix_complete": False,
            },
        )
    print(json.dumps({"checks": checks, "eight_role_matrix_complete": False}))


if __name__ == "__main__":
    main()
