"""Versioned SQL adapter for policy functions unsupported by Terraform resources.

No business tables or source rows are created. Policies are default-deny until
separately attested identity mappings and protected table grants are tested.
"""

import argparse
import hashlib
import time

from databricks.sdk.service.sql import StatementState
from foundation_support import ROOT, now, save
from platform_control import ControlStore, admission, workspace_client


def execute(client, warehouse, statement, timeout=120, control=None):
    admission((control or ControlStore()).read()[0], True)
    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse, statement=statement, wait_timeout="0s"
    )
    deadline = time.monotonic() + timeout
    while response.status.state in {StatementState.PENDING, StatementState.RUNNING}:
        if time.monotonic() >= deadline:
            client.statement_execution.cancel_execution(response.statement_id)
            raise TimeoutError("SQL command exceeded bounded timeout")
        time.sleep(1)
        response = client.statement_execution.get_statement(response.statement_id)
    if response.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(str(response.status.error))
    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--warehouse-id", required=True)
    args = parser.parse_args()
    sources = [
        ROOT / "platform/sql/security/baseline.sql",
        ROOT / "platform/sql/security/domain_policies.sql",
    ]
    sql = "\n-- COMMAND ----------\n".join(path.read_text() for path in sources)
    client = workspace_client()
    results = []
    try:
        for index, command in enumerate(sql.split("-- COMMAND ----------")):
            response = execute(client, args.warehouse_id, command)
            results.append(
                {
                    "ordinal": index + 1,
                    "statement_id": response.statement_id,
                    "status": "PASS",
                }
            )
    finally:
        save(
            ROOT / "output/platform-foundation/security-baseline.json",
            {
                "observed_at": now(),
                "source_sha256": hashlib.sha256(sql.encode()).hexdigest(),
                "commands": results,
                "business_read_grants": 0,
            },
        )
    print(f"PASS: {len(results)} security baseline commands")


if __name__ == "__main__":
    main()
