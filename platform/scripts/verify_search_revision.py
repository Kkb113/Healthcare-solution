"""Strictly validate the separately versioned, owner-approved Search baseline.

The original architecture contracts and gate verifier remain unmodified. This
additional contract is required by the Phase 2 gate, not an old-hash exemption.
"""

import hashlib
from decimal import Decimal

from foundation_support import ROOT, load
from validate_architecture import calculate_costs


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def verify(root=ROOT):
    revision = load(root / "platform/contracts/revisions/search-basic-v1.json")
    owner = load(root / revision["approval"])
    if (
        revision["status"] != "APPROVED_BY_USER"
        or owner["status"] != "APPROVED_BY_USER"
        or owner["owner_reply"] != "Approve versioned Search baseline revision"
    ):
        raise ValueError("Search baseline lacks explicit owner approval")
    if (
        digest(root / revision["original_gate"]) != revision["original_gate_sha256"]
        or digest(root / "platform/contracts/architecture/gate-dependencies.json")
        != revision["frozen_gate_contract_sha256"]
    ):
        raise ValueError("Historical baseline or frozen exit criteria changed")
    if (
        revision["frozen_exit_criteria_changed"]
        or revision["required_tests_reduced"]
        or revision["microsoft_fabric_included"]
    ):
        raise ValueError("Search amendment exceeds the approved scope")
    config = load(root / "platform/config/search-backend.json")
    if (
        not config["no_24x7_search"]
        or config["replicas"] != 1
        or config["partitions"] != 1
        or config["region"] != "eastus"
        or config["sleep_action"]
        != "DELETE_SERVICE_AND_SERVICE_SCOPED_ROLE_ASSIGNMENTS"
    ):
        raise ValueError("Unfunded or persistent Search capacity")
    price = load(
        root / "evidence/platform/workspace-foundation/azure-search-price.json"
    )["item"]
    if (
        price["currencyCode"] != "USD"
        or price["armRegionName"] != "eastus"
        or price["skuName"] != "Basic"
        or Decimal(str(price["retailPrice"])) != Decimal(config["search_usd_hour"])
    ):
        raise ValueError("Search rate lacks matching regional provider evidence")
    model = load(root / revision["effective_overrides"]["cost_model"])
    costs = calculate_costs(model)
    if (
        model["ceiling_inr"] != "20000"
        or model["monthly_ceiling_inr"] != "6000"
        or not costs["build"]["fits"]
        or not all(x["fits"] for x in costs["monthly"].values())
        or not all(x["matches_expected"] for x in costs["stress_cases"])
    ):
        raise ValueError("Revised whole-platform funding contract failed")
    baseline = load(root / "platform/contracts/architecture/cost-model.json")
    before = {r["id"]: r for r in baseline["build"]}
    after = {r["id"]: r for r in model["build"]}
    if any(after.get(k) != v for k, v in before.items() if k != "search"):
        raise ValueError("Unrelated workload allowance changed")
    if (
        Decimal(after["search"]["quantity"]) < 196
        or Decimal(after["azure-search-demo-windows"]["quantity"]) < 16
    ):
        raise ValueError("Prior billing tails or remaining Search tests underfunded")
    if Decimal(after["completion-sql"]["quantity"]) < Decimal(50) / 60 * 4:
        raise ValueError("Additional billing SQL allowance missing")
    if not revision["original_contracts_remain_immutable"]:
        raise ValueError("Original architecture provenance discarded")
    return {
        "status": "PASS",
        "revision": revision["revision"],
        "costs": costs,
        "old_gate_hash": revision["original_gate_sha256"],
        "frozen_criteria_unchanged": True,
    }


if __name__ == "__main__":
    import json

    result = verify()
    print(
        json.dumps(
            {
                "status": result["status"],
                "revision": result["revision"],
                "build_inr": result["costs"]["build"]["total_inr"],
                "frozen_criteria_unchanged": True,
            }
        )
    )
