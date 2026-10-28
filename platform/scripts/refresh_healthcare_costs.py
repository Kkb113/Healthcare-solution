"""Resource-scoped Azure cost refresh; includes untagged and deleted HC resources."""

import hashlib
import json
from decimal import Decimal

from foundation_ledger import BlobLedger, exposure, update_snapshot
from foundation_support import CONFIG, ROOT, AzureRest, load, now, save


def main():
    config = load(CONFIG)
    ledger = BlobLedger()
    results = {}
    scopes = {
        f"subscriptions/{config[k]}"
        for k in ["workspace_subscription", "model_subscription"]
    }
    for key in ["workspace_subscription", "model_subscription"]:
        sub = config[key]
        scope = f"subscriptions/{sub}"
        group = (
            config["resource_group"]
            if key == "workspace_subscription"
            else config["model_resource_group"]
        )
        filters = [
            {
                "dimensions": {
                    "name": "ResourceGroupName",
                    "operator": "In",
                    "values": [group],
                }
            }
        ]
        if key == "workspace_subscription":
            filters.append(
                {
                    "dimensions": {
                        "name": "ResourceId",
                        "operator": "In",
                        "values": [
                            load(ROOT / "platform/config/workspace.json")[
                                "workspace_resource_id"
                            ]
                        ],
                    }
                }
            )
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
                "filter": {"or": filters} if len(filters) > 1 else filters[0],
            },
        }
        arm = AzureRest(sub, "https://management.azure.com/", {"management.azure.com"})
        _, _, raw = arm.request(
            "POST",
            f"https://management.azure.com/{scope}/providers/Microsoft.CostManagement/query?api-version=2025-03-01",
            body=body,
        )
        data = json.loads(raw)["properties"]
        save(ROOT / f"output/platform-foundation/azure-cost-response-{key}.json", data)
        if data.get("nextLink"):
            raise ValueError("Cost result is paginated; retain previous snapshot")
        columns = [c["name"] for c in data["columns"]]
        rows = [dict(zip(columns, row, strict=True)) for row in data["rows"]]
        currencies = {r.get("Currency") for r in rows}
        if rows and (len(currencies) != 1 or not currencies <= {"USD", "INR"}):
            raise ValueError(
                f"Unexpected billing currencies: {currencies}; columns: {columns}"
            )
        currency = next(iter(currencies)) if rows else "USD"
        amounts = [Decimal(str(r.get("PreTaxCost", r.get("Cost")))) for r in rows]
        snapshot = {
            "scope": scope,
            "currency": currency,
            "positive_cost_" + currency.lower(): str(
                sum((x for x in amounts if x > 0), Decimal(0))
            ),
            "credits_" + currency.lower(): str(
                sum((x for x in amounts if x < 0), Decimal(0))
            ),
            "as_of": now(),
            "period_start": "2026-10-01",
            "source_rows": len(rows),
            "status": "PROVISIONAL" if rows else "PROVISIONAL_EMPTY",
            "planning_fx": "100",
            "tax_reserve": "0.18",
            "query_sha256": hashlib.sha256(
                json.dumps(body, sort_keys=True).encode()
            ).hexdigest(),
        }
        ledger.transact(
            lambda old, scope=scope, snapshot=snapshot: update_snapshot(
                old, scope, snapshot, scopes
            )
        )
        results[scope] = {"snapshot": snapshot, "rows": rows}
    report = {
        "observed_at": now(),
        "status": "PROVISIONAL_PROVIDER_SNAPSHOT",
        "subscriptions": results,
        "exposure": exposure(ledger.read()[0]),
        "invoice_final": False,
        "reservations_released": False,
        "databricks_list_prices_added_to_azure_costs": False,
        "note": "List-price DBU attribution and Azure actual cost are separate views of the same spend, never added together. Missing/late billing retains every reservation.",
    }
    save(ROOT / "output/platform-foundation/completion-azure-costs.json", report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "exposure": report["exposure"],
                "rows": sum(len(r["rows"]) for r in results.values()),
            }
        )
    )


if __name__ == "__main__":
    main()
