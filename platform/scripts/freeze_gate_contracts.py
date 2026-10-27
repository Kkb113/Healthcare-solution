"""Snapshot approved roadmap exit criteria/dependencies for later phase gates."""

from __future__ import annotations

import json
import re

from freeze_source_contracts import ROOT, topological_order

NAMES = [
    "architecture-baseline",
    "adopted-infrastructure",
    "workspace-foundation",
    "source-onboarding",
    "bronze-delivery",
    "silver-conformance",
    "gold-semantics",
    "autopilot-core",
    "forecast-products",
    "genie-analytics",
    "healthcare-agent",
    "autopilot-remediation",
    "batch-release",
    "operational-streaming",
]
DEPENDENCIES = [
    [],
    [0],
    [1],
    [2],
    [3],
    [4],
    [5],
    [4, 5, 6],
    [6, 7],
    [6, 8],
    [6, 8, 9],
    [7, 10],
    list(range(1, 12)),
    [12],
]


def build(root=ROOT) -> dict:
    plan = (root / "azure-databricks-implementation.md").read_text(encoding="utf-8")
    phases = []
    for phase, name in enumerate(NAMES):
        criteria = [
            {
                "id": match[0],
                "criterion": match[1].strip(),
                "measure": match[2].strip(),
                "waivable": False,
            }
            for match in re.findall(
                r"^\| (\d+\.\d+) \| ([^|]+) \| (.+) \|$", plan, re.MULTILINE
            )
            if match[0].split(".")[0] == str(phase)
        ]
        if not criteria:
            raise ValueError(f"No criteria for {phase}")
        phases.append(
            {
                "phase": phase,
                "name": name,
                "dependencies": DEPENDENCIES[phase],
                "gate": f"evidence/platform/{name}/gate.json",
                "environment": "local-design + read-only cloud metadata"
                if phase == 0
                else "dev/test; prod publication only at batch/RTI release",
                "criteria": criteria,
                "evidence_required": [
                    "source_sha",
                    "dataset_descriptor_sha256",
                    "contract_hashes",
                    "environment",
                    "dependency_gates",
                    "tests",
                    "measurements",
                    "costs",
                    "limitations",
                    "owner_signoff",
                ],
            }
        )
    topological_order(
        {str(p["phase"]): list(map(str, p["dependencies"])) for p in phases}
    )
    return {
        "contract_version": "architecture-1",
        "phase_count": 14,
        "criteria_are_frozen": True,
        "phase0_is_not_tenant_integration": True,
        "phases": phases,
    }


def check_dependencies(phase: int, records: dict[int, dict], contract: dict) -> None:
    for parent in contract["phases"][phase]["dependencies"]:
        record = records.get(parent)
        if not record or record.get("status") != "PASS":
            raise ValueError(f"Phase {phase} blocked by missing/failing gate {parent}")
        if any(
            item.get("status") != "PASS" for item in record.get("criteria", [])
        ) or not record.get("criteria"):
            raise ValueError(f"Dependency {parent} has an unpassed criterion")


if __name__ == "__main__":
    path = ROOT / "platform/contracts/architecture/gate-dependencies.json"
    path.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(f"Frozen fourteen-phase exit/dependency contract: {path.relative_to(ROOT)}")
