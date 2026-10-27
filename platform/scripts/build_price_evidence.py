"""Select auditable non-promotional East US prices from the downloaded API cache."""

from __future__ import annotations

import json

from freeze_source_contracts import ROOT, digest, load


def build() -> dict:
    model = load(ROOT / "platform/contracts/architecture/cost-model.json")
    cache = ROOT / "output/platform-architecture"
    pages = {
        service: load(cache / f"{service}-retail-prices.json")
        for service in ["databricks", "storage", "event-hubs", "key-vault"]
    }
    selected = {}
    for name, rate in model["rates"].items():
        if name == "allowance":
            continue
        if name.startswith("luna_"):
            selected[name] = {
                "status": "OFFICIAL_PUBLICATION",
                "source_url": rate["source"],
                "reviewed_on": model["as_of"],
                "currency": "USD",
                "deployment": "US Data Zone Standard",
                "context": "short",
                "usd": rate["usd"],
                "unit": rate["unit"],
                "note": "Retail API query contained zero Luna items; Azure pricing page links this publication while model table publishing is pending. Revalidate before funded invocation.",
            }
            continue
        matches = []
        for service, page in pages.items():
            for item in page["items"]:
                if (
                    (
                        item.get("meterName") == rate["meter"]
                        or service == "databricks"
                        and item.get("skuName") == rate["meter"]
                    )
                    and item.get("type") == "Consumption"
                    and item.get("tierMinimumUnits", 0) == 0
                    and str(item.get("armRegionName")) == "eastus"
                    and float(item["retailPrice"]) == float(rate["usd"])
                    and "Free" not in item["skuName"]
                    and "Non-Billable" not in item["skuName"]
                    and (service != "storage" or item["skuName"] == "Hot LRS")
                    and (service != "key-vault" or item["skuName"] == "Standard")
                ):
                    matches.append((service, page, item))
        if len(matches) != 1:
            raise ValueError(
                f"Expected one public price for {name}, got {len(matches)}"
            )
        service, page, item = matches[0]
        selected[name] = {
            "status": "RETAIL_API",
            "source_url": page["source_url"],
            "retrieved_at": page["retrieved_at"],
            "raw_response_sha256": digest(cache / f"{service}-retail-prices.json"),
            "item": item,
            "usd": rate["usd"],
            "unit": rate["unit"],
        }
    return {
        "reviewed_on": model["as_of"],
        "region": "eastus",
        "currency": "USD",
        "promotions_assumed": False,
        "rates": selected,
        "multipliers_source": "https://learn.microsoft.com/en-us/azure/databricks/resources/pricing",
        "minimums_and_tails": {
            "sql_2x_small_dbu_hour": 4,
            "app_medium_interactive_dbu_hour": "0.5",
            "search_standard_inference_dbu_hour": 4,
            "search_units": 1,
            "search_last_index_deletion_tail_hours": 24,
            "search_tail_source": "https://learn.microsoft.com/en-us/azure/databricks/ai-search/cost-management",
            "lakebase_autoscaling_multiplier": "0.213X (CU billing mapping must be measured, not inferred from multiplier)",
            "lakebase_idle_default_hours": 24,
            "lakebase_idle_override_seconds": 300,
            "lakebase_source": "https://learn.microsoft.com/en-us/azure/databricks/oltp/projects/manage-computes",
        },
    }


if __name__ == "__main__":
    path = ROOT / "evidence/platform/architecture-baseline/price-evidence.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(f"Selected price evidence: {path.relative_to(ROOT)}")
