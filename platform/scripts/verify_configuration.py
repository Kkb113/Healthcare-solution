"""Offline preflight for pinned targets, budget partitions and configuration syntax."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    for path in (ROOT / "platform/config").glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    for path in (ROOT / "platform/scripts").glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    workspace = json.loads((ROOT / "platform/config/workspace.json").read_text())
    budget = json.loads((ROOT / "platform/config/cost-policy.json").read_text())
    if (
        workspace["compute_mode"] != "SERVERLESS"
        or workspace["required_model"] != "gpt-6-luna"
    ):
        raise ValueError("The approved workspace/model contract changed")
    parts = budget["budgets_usd"].values()
    if (
        sum(part["build"] for part in parts) * budget["planning_inr_per_usd"]
        != budget["build_ceiling"]
    ):
        raise ValueError("Build budget partitions do not reconcile")
    if (
        sum(part["monthly"] for part in parts) * budget["planning_inr_per_usd"]
        != budget["monthly_target"]
    ):
        raise ValueError("Monthly budget partitions do not reconcile")
    print(
        "PASS: JSON/Python configuration, exact model/serverless contract and budget partitions"
    )


if __name__ == "__main__":
    main()
