"""Bounded SQL readability probe; stop and delete the disposable warehouse."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import sql

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-billable-probe", action="store_true")
    if not parser.parse_args().execute_billable_probe:
        parser.error("Explicit billable probe opt-in required")
    config = json.loads((ROOT / "platform/config/workspace.json").read_text())
    os.environ["ARM_SUBSCRIPTION_ID"] = config["subscription_id"]
    client = WorkspaceClient(profile=config["workspace_profile"])
    report = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL",
        "queries": [],
        "cleanup": {},
    }
    warehouse_id = None
    try:
        warehouse = client.warehouses.create(
            name="hcp-readiness-telemetry-probe",
            cluster_size="2X-Small",
            min_num_clusters=1,
            max_num_clusters=1,
            auto_stop_mins=5,
            enable_serverless_compute=True,
            warehouse_type=sql.CreateWarehouseRequestWarehouseType.PRO,
        ).result(timeout=timedelta(minutes=4))
        warehouse_id = warehouse.id
        report["warehouse_id"] = warehouse_id
        statements = {
            "system.billing.usage": "SELECT COUNT(*) AS visible_rows FROM system.billing.usage WHERE workspace_id = '7405619366453187' AND usage_date >= current_date() - INTERVAL 1 DAY",
            "system.billing.list_prices": "SELECT COUNT(*) AS visible_rows FROM system.billing.list_prices WHERE price_end_time IS NULL",
            "system.lakeflow.job_run_timeline": "SELECT COUNT(*) AS visible_rows FROM system.lakeflow.job_run_timeline WHERE workspace_id = '7405619366453187' AND period_start_time >= current_timestamp() - INTERVAL 1 DAY",
            "system.access.table_lineage": "SELECT COUNT(*) AS visible_rows FROM system.access.table_lineage WHERE workspace_id = '7405619366453187' AND event_date >= current_date() - INTERVAL 1 DAY",
        }
        for table, statement in statements.items():
            result = client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=statement,
                wait_timeout="30s",
                on_wait_timeout=sql.ExecuteStatementRequestOnWaitTimeout.CANCEL,
            )
            status = result.status.state.value
            report["queries"].append(
                {
                    "table": table,
                    "statement_id": result.statement_id,
                    "state": status,
                    "error": result.status.error.message
                    if result.status.error
                    else None,
                    "aggregate": result.result.data_array if result.result else None,
                }
            )
            print(json.dumps(report["queries"][-1]), flush=True)
        report["status"] = (
            "PASS"
            if all(q["state"] == "SUCCEEDED" for q in report["queries"])
            else "FAIL"
        )
    except Exception as error:  # noqa: BLE001 - CLI boundary records failure and cleanup
        report["error"] = str(error)[:1500]
    finally:
        # A create waiter can fail after creation. Recover only this named fixture.
        if warehouse_id is None:
            candidates = [
                w
                for w in client.warehouses.list()
                if w.name == "hcp-readiness-telemetry-probe"
            ]
            if len(candidates) == 1:
                warehouse_id = candidates[0].id
        if warehouse_id:
            try:
                client.warehouses.stop(warehouse_id).result(
                    timeout=timedelta(minutes=2)
                )
                report["cleanup"]["stopped"] = True
                client.warehouses.delete(warehouse_id)
                report["cleanup"]["deleted"] = True
            except Exception as error:  # noqa: BLE001 - CLI boundary records failure and cleanup
                report["cleanup"]["error"] = str(error)[:1000]
                report["status"] = "FAIL"
        destination = ROOT / "output/platform-readiness/telemetry-sql-probe.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
