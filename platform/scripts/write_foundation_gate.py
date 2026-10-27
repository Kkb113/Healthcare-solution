"""Freeze Phase 1 only after committed code, live checks and regression tests pass."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys

from foundation_support import OUTPUT, ROOT, load, now, save, source_binding
from verify_foundation_gate import (
    EVIDENCE,
    REPORTS,
    check_reports,
    counts,
    require,
    verify,
)


def main():
    binding = source_binding()
    for relative, expected in binding["input_hashes"].items():
        raw = subprocess.check_output(
            ["git", "show", f"{binding['source_sha']}:{relative}"], cwd=ROOT
        )
        require(
            hashlib.sha256(raw).hexdigest() == expected,
            "Commit every gate input before certification",
        )
    reports = {name: load(OUTPUT / f"{name}.json") for name in REPORTS}
    for report in reports.values():
        require(
            report["source_sha"] == binding["source_sha"]
            and report["input_hashes"] == binding["input_hashes"],
            "Rerun live checks at the same committed source",
        )
    check_reports(reports)
    # Test report is generated here, rather than trusting a caller's old XML file.
    subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "pytest",
            "platform/tests/unit",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(OUTPUT / ("pytest-gate-" + binding["source_sha"][:12])),
            "--junitxml",
            str(OUTPUT / "all-platform-tests.xml"),
        ],
        cwd=ROOT,
        check=True,
    )
    test_counts = counts(OUTPUT / "all-platform-tests.xml")
    require(
        test_counts["tests"] >= 91
        and not any(test_counts[k] for k in ["errors", "failures", "skipped"]),
        "All regression tests must pass",
    )
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for filename in [
        *[f"{name}.json" for name in REPORTS],
        "all-platform-tests.xml",
        "scim-credential-bootstrap.json",
        "operator-display-name.json",
        "scoped-scim-bootstrap.png",
    ]:
        shutil.copyfile(OUTPUT / filename, EVIDENCE / filename)
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in EVIDENCE.iterdir()
        if p.is_file() and p.name not in {"gate.json", "ci-validation.json"}
    }
    gate = {
        **binding,
        "phase": 1,
        "status": "PASS",
        "recorded_at": now(),
        "criteria": [
            {"id": f"1.{i}", "status": "PASS", "evidence": evidence}
            for i, evidence in enumerate(
                [
                    "terraform-drift.json + databricks.json",
                    "databricks.json + control-plane.json",
                    "identity.json + databricks.json",
                    "control-plane.json + costs.json",
                    "control-plane.json + databricks.json",
                ],
                start=1,
            )
        ],
        "prerequisite_gate_sha256": hashlib.sha256(
            (ROOT / "evidence/platform/architecture-baseline/gate.json").read_bytes()
        ).hexdigest(),
        "report_hashes": hashes,
        "tests": test_counts,
        "governance": {
            "aim": "DISABLED; no shared-account migration",
            "user_scope": "Only existing Karthik Bhat identity may be reconciled",
            "provisioning_approval": "User explicitly approved healthcare-only SCIM setup",
            "bootstrap_console_exception": "Only generation/revocation of the account-SCIM-only credential; remaining provisioning and tests use CLI/API",
            "business_data_grants": "None in Phase 1",
        },
        "limitations": [
            "Azure budgets alert; they do not hard-stop spend. Phase 2 sleep/guard tests remain required.",
            "Provider costs are provisional. Empty tagged cost results are not zero spend; reservations remain until independent settlement.",
            "SCIM scope intentionally admits eight groups and one user. Expanding user scope needs explicit approval, schema revision and access tests. SP lifecycle remains the existing code-owned adapter.",
            "Actual serverless notebook read/write, layer-specific grants, masking and feature probes remain Phase 2; UC credential control-plane validation passed here.",
            "This is dated, source-bound execution evidence, not a perpetual assertion of live cloud state.",
        ],
    }
    save(EVIDENCE / "gate.json", gate)
    print(verify())


if __name__ == "__main__":
    main()
