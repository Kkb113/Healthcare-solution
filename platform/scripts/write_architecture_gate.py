"""Create Phase 0 evidence only from approved, committed, passing local reports."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

from freeze_source_contracts import DESCRIPTOR, ROOT, digest, load
from validate_architecture import require, validate_package

EVIDENCE = ROOT / "evidence/platform/architecture-baseline"


def git_bytes(sha: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT)


def repository_digest(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def input_paths() -> list[Path]:
    paths = set()
    for pattern in [
        "platform/contracts/architecture/*.json",
        "platform/docs/adr/*.md",
        "platform/scripts/*.py",
        "platform/tests/**/*.py",
        "platform/config/*.json",
    ]:
        paths.update(ROOT.glob(pattern))
    paths.update(
        ROOT / path
        for path in [
            "azure-databricks-implementation.md",
            ".github/workflows/platform-readiness.yml",
            "platform/docs/architecture-baseline.md",
            "platform/docs/build-budget-review.md",
            "platform/docs/runbooks/validate-architecture.md",
            "reviews/dataset-release-v1.1.0-acceptance.json",
            "evidence/dataset-release-v1.1.0/acceptance-gate.json",
            "evidence/platform/architecture-baseline/price-evidence.json",
            "evidence/platform/architecture-baseline/workspace-live.json",
            "evidence/platform/architecture-baseline/model-deployment-live.json",
        ]
    )
    for cap in load(ROOT / "platform/contracts/architecture/capability-matrix.json")[
        "capabilities"
    ]:
        paths.add(ROOT / cap["tenant_evidence"])
    quality = load(ROOT / "platform/contracts/architecture/data-quality-contracts.json")
    paths.add(ROOT / quality["rule_source"])
    paths.update(
        ROOT / name
        for name in quality["source_semantic_hashes"]
        if not name.startswith("data/")
    )
    return sorted(paths)


def junit_counts(path: Path) -> dict:
    suites = ElementTree.parse(path).getroot()
    return {
        name: sum(int(suite.attrib.get(name, 0)) for suite in suites.iter("testsuite"))
        for name in ["tests", "failures", "errors", "skipped"]
    }


def main() -> None:
    verified = validate_package(with_release=True)
    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    validation = load(ROOT / "output/platform-architecture/design-validation.json")
    require(
        validation["status"] == "PASS" and validation["source_sha"] == sha,
        "Rerun approved design validation at current committed source SHA",
    )
    require(
        validation.get("full_release_verification", {}).get("status") == "PASSED",
        "Full accepted package verification required",
    )
    require(
        validation["full_release_verification"]["descriptor_sha256"] == DESCRIPTOR,
        "Wrong verified release",
    )
    require(
        validation["costs"] == verified["costs"],
        "Cost report differs from reviewed contracts",
    )
    counts = junit_counts(ROOT / "output/platform-architecture/architecture-tests.xml")
    require(
        counts["tests"] >= 38
        and not any(counts[k] for k in ["failures", "errors", "skipped"]),
        "Complete negative/positive architecture suite must pass",
    )
    hashes = {}
    import hashlib

    for path in input_paths():
        relative = path.relative_to(ROOT).as_posix()
        current = repository_digest(path)
        committed = hashlib.sha256(git_bytes(sha, relative)).hexdigest()
        require(current == committed, f"Uncommitted gate input: {relative}")
        hashes[relative] = current
    for name in ["design-validation.json", "architecture-tests.xml"]:
        shutil.copyfile(ROOT / "output/platform-architecture" / name, EVIDENCE / name)
    reports = {
        f"evidence/platform/architecture-baseline/{name}": digest(EVIDENCE / name)
        for name in ["design-validation.json", "architecture-tests.xml"]
    }
    criteria = [
        {
            "id": "0.1",
            "status": "PASS",
            "measure": "15/15 ADRs and six-role RACI reviewed under delegated technical authority; reduced funded scope explicitly approved by user",
            "evidence": ["platform/contracts/architecture/design-review.json"],
        },
        {
            "id": "0.2",
            "status": "PASS",
            "measure": "19 dated capability entries, pinned compatibility manifest and16 exact bounded probes; tenant limitations/quotas explicit and dependent provisioning blocked until required probes pass",
            "evidence": [
                "platform/contracts/architecture/capability-matrix.json",
                "platform/contracts/architecture/probe-matrix.json",
                "platform/contracts/architecture/compatibility-manifest.json",
            ],
        },
        {
            "id": "0.3",
            "status": "PASS",
            "measure": {
                "build_estimate_inr": verified["costs"]["build"]["total_inr"],
                "monthly_estimates_inr": {
                    k: v["total_inr"] for k, v in verified["costs"]["monthly"].items()
                },
                "ceiling_inr": 20000,
                "estimated_not_measured": True,
                "price_tails_tax_contingency": "included",
                "ml_total_threshold_inr": 1200,
            },
            "evidence": [
                "platform/contracts/architecture/cost-model.json",
                "evidence/platform/architecture-baseline/price-evidence.json",
                "platform/docs/build-budget-review.md",
            ],
        },
        {
            "id": "0.4",
            "status": "PASS",
            "measure": {
                "tables": 25,
                "columns": 526,
                "business_rows": 1937925,
                "kpis": 42,
                "independent_kpi_check_contracts": 20,
                "ml_dispositions": 13,
                "dq_rules": 55,
                "gate_phases": 14,
                "required_optional_probes": "P11 only optional; all required probes blocking at their stated phase",
                "approved_native_questions": 124,
            },
            "evidence": [
                "platform/contracts/architecture/source-contracts.json",
                "platform/contracts/architecture/delivery-temporal.json",
                "platform/contracts/architecture/kpi-catalog.json",
                "platform/contracts/architecture/ml-eligibility.json",
                "platform/contracts/architecture/security-ownership.json",
                "platform/contracts/architecture/test-workloads.json",
                "platform/contracts/architecture/gate-dependencies.json",
            ],
        },
    ]
    accepted_gate = "evidence/dataset-release-v1.1.0/acceptance-gate.json"
    require(
        load(ROOT / accepted_gate)["full_dataset_accepted"] is True,
        "Accepted data prerequisite missing",
    )
    gate = {
        "phase": 0,
        "name": "architecture-baseline",
        "status": "PASS",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "source_sha": sha,
        "dataset_descriptor_sha256": DESCRIPTOR,
        "environment": "Local pinned Python3.12 design harness and read-only EastUS cloud metadata; no new workload provisioning",
        "dependency_gates": [
            {
                "path": accepted_gate,
                "sha256": digest(ROOT / accepted_gate),
                "status": "PASSED",
                "scope": "Accepted synthetic dataset prerequisite, not a platform phase gate",
            }
        ],
        "contract_hashes": hashes,
        "contract_hash_policy": "SHA256 of repository text with CRLF normalized to LF, matching .gitattributes/Git blobs. Accepted release/payload SHA256 remains raw and unchanged.",
        "report_hashes": reports,
        "criteria": criteria,
        "tests": dict(
            counts,
            commands=[
                "ruff check/format platform/scripts platform/tests",
                "verify_configuration.py",
                "pytest platform/tests/unit/test_architecture_contracts.py",
                "validate_architecture.py --with-release (includes complete release-tool checksum verification)",
            ],
        ),
        "measurements": {
            "full_release_verification": validation["full_release_verification"],
            "tenant_probe_execution": "NOT_RUN; later required gates remain unpassed",
            "cost_basis": "Official regional prices plus frozen unmeasured usage assumptions",
        },
        "costs": {
            "modeled": verified["costs"],
            "phase0_new_paid_workloads": 0,
            "actual_invoice_cost_inr": None,
            "prior_prerequisite_pending_reserve_inr": 200,
            "note": "No new compute was started; billing settlement is not asserted from metadata-only checks.",
        },
        "limitations": [
            "Not a tenant integration, model accuracy, latency or real-data production certification",
            "Luna5RPM/5000TPM readiness allocation requires Phase2 sizing/quota/capacity probe",
            "Lakebase CU billing and automated compute quantities remain measured-pilot hold points",
            "Reduced stochastic Genie coverage explicitly accepted by owner; exact deterministic/security/recovery checks retained",
            "FX/rate stress can exceed ceiling; future admission must stop/reprice rather than waive tests",
        ],
        "owner_signoff": {
            "actor": "Codex",
            "role": "Delegated Phase0 technical design/implementation reviewer",
            "authority": "Direct user instruction to finalize Phase0 plus explicit user acceptance of reduced POC scope at INR20000; approval hashes recorded in design-review.json",
            "independent_clinical_or_security_certification_claimed": False,
        },
        "next_phase": {
            "phase": 1,
            "status": "NOT_STARTED_BY_THIS_GATE",
            "rule": "Commit and push gate before dependent execution; adopt prior authorized prerequisites, do not infer Phase1 PASS.",
        },
    }
    (EVIDENCE / "gate.json").write_text(
        json.dumps(gate, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        f"PASS: four Phase0 criteria; committed source {sha}; tests {counts['tests']}"
    )


if __name__ == "__main__":
    main()
