"""Read official Azure Retail Prices API pages into an ignored evidence cache."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
FILTERS = {
    "databricks": "serviceName eq 'Azure Databricks' and armRegionName eq 'eastus'",
    "storage": "serviceName eq 'Storage' and armRegionName eq 'eastus' and productName eq 'General Block Blob v2'",
    "key-vault": "serviceName eq 'Key Vault' and armRegionName eq 'eastus'",
    "event-hubs": "serviceName eq 'Event Hubs' and armRegionName eq 'eastus'",
    "luna": "contains(skuName, 'Luna')",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("service", choices=FILTERS)
    args = parser.parse_args()
    query = FILTERS[args.service]
    url = "https://prices.azure.com/api/retail/prices?" + urlencode(
        {"api-version": "2023-01-01-preview", "$filter": query, "currencyCode": "USD"}
    )
    source_url = url
    items, pages = [], 0
    while url:
        with urlopen(url, timeout=90) as response:
            page = json.load(response)
        items.extend(page["Items"])
        url = page.get("NextPageLink")
        pages += 1
        if pages > 50:
            raise ValueError("Unexpected price pagination; refine the bounded query")
    document = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_url": source_url,
        "filter": query,
        "currency": "USD",
        "pages": pages,
        "items": items,
    }
    folder = ROOT / "output/platform-architecture"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{args.service}-retail-prices.json").write_text(
        json.dumps(document, indent=2) + "\n"
    )
    selected = [
        {
            k: item.get(k)
            for k in [
                "skuName",
                "meterName",
                "retailPrice",
                "unitOfMeasure",
                "productName",
                "armRegionName",
                "type",
            ]
        }
        for item in items
        if item.get("type") == "Consumption" and "Free Trial" not in item["skuName"]
    ]
    print(
        json.dumps(
            {
                "service": args.service,
                "count": len(items),
                "consumption_prices": len(selected),
                "cache": str(folder / f"{args.service}-retail-prices.json"),
            }
        )
    )


if __name__ == "__main__":
    main()
