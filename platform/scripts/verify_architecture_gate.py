"""Verify immutable design gate/report bindings against source Git objects."""

from __future__ import annotations

import hashlib
import json
import subprocess

from freeze_source_contracts import DESCRIPTOR, ROOT, digest, load
from validate_architecture import require, validate_package
from write_architecture_gate import EVIDENCE, git_bytes, junit_counts, repository_digest


def main() -> None:
    gate = load(EVIDENCE / "gate.json")
    require(gate["phase"] == 0 and gate["status"] == "PASS", "Phase0 gate not passed")
    require(gate["dataset_descriptor_sha256"] == DESCRIPTOR, "Wrong gate release")
    require(
        [c["id"] for c in gate["criteria"]] == ["0.1", "0.2", "0.3", "0.4"]
        and all(c["status"] == "PASS" for c in gate["criteria"]),
        "Missing/failing criterion",
    )
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", gate["source_sha"], "HEAD"],
        cwd=ROOT,
        check=True,
    )
    for relative, expected in gate["contract_hashes"].items():
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT.resolve()), "Unsafe artifact path")
        require(
            repository_digest(path) == expected
            and hashlib.sha256(git_bytes(gate["source_sha"], relative)).hexdigest()
            == expected,
            f"Changed gate input: {relative}",
        )
    for relative, expected in gate["report_hashes"].items():
        require(digest(ROOT / relative) == expected, "Changed execution report")
    report = load(EVIDENCE / "design-validation.json")
    require(
        report["status"] == "PASS"
        and report["source_sha"] == gate["source_sha"]
        and report["full_release_verification"]["status"] == "PASSED",
        "Invalid execution/release report",
    )
    result = validate_package()
    require(
        report["costs"] == result["costs"] == gate["costs"]["modeled"],
        "Cost evidence mismatch",
    )
    counts = junit_counts(EVIDENCE / "architecture-tests.xml")
    require(
        all(gate["tests"][k] == value for k, value in counts.items())
        and not any(counts[k] for k in ["failures", "errors", "skipped"]),
        "Test evidence mismatch",
    )
    require(
        gate["measurements"]["tenant_probe_execution"].startswith("NOT_RUN"),
        "Phase0 cannot claim future tenant probes passed",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "phase": 0,
                "criteria": 4,
                "source_sha": gate["source_sha"],
                "bound_inputs": len(gate["contract_hashes"]),
                "tests": counts["tests"],
            }
        )
    )


if __name__ == "__main__":
    main()
