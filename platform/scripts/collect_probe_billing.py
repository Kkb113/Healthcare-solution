"""Read settled healthcare workspace meter rows without waking a warehouse.

Provider latency is explicit: missing usage or prices never releases a hold.
No identity metadata, request payloads or other workspaces are exported.
"""

import json

from deploy_security_baseline import execute
from foundation_support import ROOT, now, save
from platform_control import ControlStore, workspace_client

WAREHOUSE = "bd30bdac29080126"
WORKSPACE = "7405619366453187"


def main():
    client = workspace_client()
    if client.warehouses.get(WAREHOUSE).state.value != "RUNNING":
        raise PermissionError(
            "Billing collection must reuse an already-running funded warehouse"
        )
    result = execute(
        client,
        WAREHOUSE,
        f"""SELECT u.sku_name, u.usage_unit, to_json(u.usage_metadata) AS resource_metadata,
          SUM(u.usage_quantity) AS net_quantity,
          CAST(p.pricing.effective_list.default AS STRING) AS usd_list_unit_price,
          MIN(u.usage_start_time) AS first_usage, MAX(u.usage_end_time) AS last_usage,
          COUNT(*) AS provider_records
        FROM system.billing.usage u
        LEFT JOIN system.billing.list_prices p
          ON u.sku_name = p.sku_name AND u.cloud = p.cloud
          AND u.usage_unit = p.usage_unit
          AND u.usage_start_time >= p.price_start_time
          AND (p.price_end_time IS NULL OR u.usage_start_time < p.price_end_time)
        WHERE u.workspace_id = '{WORKSPACE}'
          AND u.usage_date >= DATE '2026-10-26' AND u.cloud = 'AZURE'
        GROUP BY u.sku_name, u.usage_unit, to_json(u.usage_metadata),
          CAST(p.pricing.effective_list.default AS STRING)
        ORDER BY u.sku_name, first_usage LIMIT 500""",
        control=ControlStore(),
    )
    columns = [item.name for item in result.manifest.schema.columns]
    rows = [
        dict(zip(columns, row, strict=True)) for row in result.result.data_array or []
    ]
    report = {
        "observed_at": now(),
        "status": "PROVISIONAL_PROVIDER_ROWS" if rows else "PENDING_PROVIDER_ROWS",
        "statement_id": result.statement_id,
        "workspace_id": WORKSPACE,
        "rows": rows,
        "reservations_released": False,
        "empty_usage_means_zero": False,
        "caveat": "List-price evidence, not an Azure invoice. Late records, retractions and unmatched prices require subsequent reconciliation.",
    }
    save(ROOT / "output/platform-foundation/probe-billing.json", report)
    print(json.dumps({"status": report["status"], "resource_meter_groups": len(rows)}))


if __name__ == "__main__":
    main()
