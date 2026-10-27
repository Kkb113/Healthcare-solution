"""Approved system-table queries, scoped runtime views and informational UC mirror."""

import json

from deploy_security_baseline import execute
from foundation_support import ROOT, databricks_clients, now, save
from platform_control import ControlStore
from probe_security_baseline import JOBS, principal_client

WAREHOUSE = "bd30bdac29080126"
WORKSPACE = "7405619366453187"


def main():
    store = ControlStore()
    account, operator = databricks_clients()
    report = {
        "status": "INCOMPLETE",
        "observed_at": now(),
        "operator_sources": [],
        "runtime_views": [],
        "raw_runtime_access": "NOT_GRANTED",
    }

    def query(client, value):
        return execute(client, WAREHOUSE, value, control=store)

    sources = {
        "system.billing.usage": f"workspace_id = '{WORKSPACE}'",
        "system.billing.list_prices": "cloud = 'AZURE'",
        "system.lakeflow.job_run_timeline": f"workspace_id = '{WORKSPACE}'",
        "system.access.table_lineage": f"workspace_id = '{WORKSPACE}'",
    }
    for source, predicate in sources.items():
        result = query(
            operator, f"SELECT COUNT(*) AS records FROM {source} WHERE {predicate}"
        )
        report["operator_sources"].append(
            {
                "table": source,
                "statement_id": result.statement_id,
                "query_status": "PASS",
                "rows_in_scope": int(result.result.data_array[0][0]),
            }
        )
    with principal_client(account, JOBS) as jobs:
        for view in [
            "workspace_usage",
            "workspace_prices",
            "workspace_job_runs",
            "workspace_lineage",
        ]:
            result = query(
                jobs, f"SELECT COUNT(*) AS records FROM hc_ops.telemetry.{view}"
            )
            report["runtime_views"].append(
                {
                    "view": "hc_ops.telemetry." + view,
                    "statement_id": result.statement_id,
                    "query_status": "PASS",
                    "rows_in_scope": int(result.result.data_array[0][0]),
                }
            )
    query(
        operator,
        "CREATE TABLE IF NOT EXISTS hc_ops.autopilot.platform_state (workspace_id BIGINT, session_id STRING, control_revision BIGINT, state STRING, captured_at TIMESTAMP, manifest_json STRING) USING DELTA",
    )
    state = store.read()[0]
    # Values are generated locally from a validated closed state schema. JSON is
    # escaped as a SQL string only for this metadata mirror, never user data.
    manifest = json.dumps(state["resources"]).replace("'", "''")
    session = state["session"]["id"]
    query(
        operator,
        f"INSERT INTO hc_ops.autopilot.platform_state VALUES ({WORKSPACE}, '{session}', {state['revision']}, '{state['state']}', current_timestamp(), '{manifest}')",
    )
    report.update(
        status="PASS",
        mirror="hc_ops.autopilot.platform_state",
        mirror_authoritative=False,
        authoritative_state="ADLS control object",
        billing_caveat="Empty or delayed usage is not zero spend; pending phase reservations remain in force",
    )
    save(ROOT / "output/platform-foundation/telemetry-probe.json", report)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
