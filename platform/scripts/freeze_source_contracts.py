"""Freeze aggregate source contracts without copying synthetic patient records.

Run only for an explicitly reviewed release/baseline revision. Normal verification
recomputes this object in memory and rejects drift; it never refreshes the baseline.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "data/releases/healthcare-synthetic-v1.1.0"
OUTPUT = ROOT / "platform/contracts/architecture/source-contracts.json"
DESCRIPTOR = "c36a9b7841743057be2f6993a27790c82a170c847399687a0c2647b5b9167af5"
LOGICAL_PUBLICATION_PARENTS = {
    "access_scope": ["worker_assignment", "facility", "location", "cost_center"],
    "source_key_map": [
        "patient",
        "worker_assignment",
        "location",
        "cost_center",
        "catalog_item",
        "payer_plan",
    ],
    "financial_posting": [
        "staff_shift",
        "inventory_movement",
        "service_charge",
        "claim_event",
    ],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def topological_order(dependencies: dict[str, list[str]]) -> list[str]:
    remaining = {name: set(parents) for name, parents in dependencies.items()}
    if any(
        parent not in remaining for parents in remaining.values() for parent in parents
    ):
        raise ValueError("Unknown dependency")
    ordered = []
    while remaining:
        ready = sorted(name for name, parents in remaining.items() if not parents)
        if not ready:
            raise ValueError("Dependency cycle")
        ordered.extend(ready)
        remaining = {
            name: parents - set(ready)
            for name, parents in remaining.items()
            if name not in ready
        }
    return ordered


def build() -> dict:
    if digest(RELEASE / "release-descriptor.json") != DESCRIPTOR:
        raise ValueError("Unapproved dataset descriptor")
    schema = load(RELEASE / "schema/tables.json")
    dictionary = load(RELEASE / "native/source-dictionary.json")
    manifest = load(RELEASE / "native/manifest.json")
    files = manifest["files"]
    names = {table["name"] for table in schema["tables"]}
    rows, deliveries = Counter(), Counter()
    for item in files:
        deliveries[item["table"]] += 1
        if item["role"] == "PRIMARY":
            rows[item["table"]] += item["expected_rows"]
    tables = []
    dependencies = {}
    for table in schema["tables"]:
        name = table["name"]
        fields = dictionary[name]["fields"]
        if {c["name"] for c in table["columns"]} != {f["canonical"] for f in fields}:
            raise ValueError(f"Incomplete source dictionary: {name}")
        parents, self_links = set(), []
        for column in table["columns"]:
            reference = column.get("references")
            if reference:
                parent = reference.split(".")[0]
                if parent not in names:
                    raise ValueError(f"Unknown physical reference {reference}")
                if parent == name:
                    self_links.append(
                        {"column": column["name"], "reference": reference}
                    )
                else:
                    parents.add(parent)
        physical_parents = sorted(parents)
        logical_parents = LOGICAL_PUBLICATION_PARENTS.get(name, [])
        parents.update(logical_parents)
        dependencies[name] = sorted(parents)
        feed_files = [item for item in files if item["table"] == name]
        source = dictionary[name]["source"].lower().replace("_", "-")
        tables.append(
            {
                "table": name,
                "source": source,
                "authority": table["source_authority"],
                "grain": table["grain"],
                "primary_key": table["primary_key"],
                "canonical_rows": rows[name],
                "deliveries": deliveries[name],
                "history_policy": table["history_policy"],
                "formats": sorted({item["format"] for item in feed_files}),
                "bronze": f"bronze.{source.replace('-', '_')}_{name}",
                "silver": f"silver.{source.replace('-', '_')}_{name}",
                "oracle": f"reference.answer_{name}",
                "upstream": sorted(parents),
                "physical_upstream": physical_parents,
                "logical_publication_upstream": sorted(logical_parents),
                "self_references": self_links,
                "columns": [
                    dict(
                        field,
                        reference_target=next(
                            c.get("references")
                            for c in table["columns"]
                            if c["name"] == field["canonical"]
                        ),
                    )
                    for field in fields
                ],
            }
        )
    # Logical/polymorphic associations are separate from physical load edges.
    return {
        "contract_version": "architecture-1",
        "release_id": RELEASE.name,
        "descriptor_sha256": DESCRIPTOR,
        "business_rows": sum(rows.values()),
        "business_tables": len(tables),
        "delivery_files": len(files),
        "distinct_delivery_hashes": len({item["sha256"] for item in files}),
        "empty_deliveries": sum(item["expected_rows"] == 0 for item in files),
        "source_systems": sorted({item["source"] for item in files}),
        "time_range": ["2023-01-01", "2025-12-31"],
        "boundary_policy": "Opening/carry-in assertions and later exports retained outside business date range; never trim by export calendar.",
        "input_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): digest(path)
            for path in [
                RELEASE / "schema/tables.json",
                RELEASE / "native/source-dictionary.json",
                RELEASE / "native/manifest.json",
                RELEASE / "native/challenge-manifest.json",
                ROOT / "reviews/dataset-release-v1.1.0-acceptance.json",
            ]
        },
        "topological_order": topological_order(dependencies),
        "logical_reference_contracts": schema["logical_reference_contracts"],
        "deferred_association_validation": "Clinical/inventory consumption groups validate after both are loaded (not a cyclic physical FK). Polymorphic scope/crosswalk targets validate after master targets; source journal groups after workforce, inventory, charge and claim-event inputs. No source business table is generated from the oracle.",
        "tables": tables,
    }


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
