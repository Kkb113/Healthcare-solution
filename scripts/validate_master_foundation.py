"""Run the complete master-data acceptance gate, regressions and independent inspection."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from healthcare_synthetic.master_pipeline import run_master
from validate_master_data import inspect_master
from validate_phase0 import report as design_report
from validate_phase1 import RecordingResult


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def evaluate(output):
    evidence = {"implementation_phase": 2, "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "scope": "Full-schema master data and opening health context only", "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}
    built = subprocess.run([sys.executable, str(ROOT / "scripts/build_phase0_spec.py"), "--check"], capture_output=True, text=True, timeout=30)
    evidence["design_artifacts_current"] = built.returncode == 0
    evidence["design_regression"] = design_report()
    old_hashes = json.loads((ROOT / "evidence/phase-0/validation-report.json").read_text())["contract_sha256"]
    evidence["frozen_design_hashes_unchanged"] = evidence["design_regression"]["contract_sha256"] == old_hashes
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    log = io.StringIO()
    results = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordingResult).run(suite)
    evidence["tests"] = {"run": results.testsRun, "passed": results.wasSuccessful() and not results.skipped,
                         "failed": len(results.failures), "errors": len(results.errors), "skipped": len(results.skipped),
                         "cases": results.records, "failure_details": [message for _, message in results.failures + results.errors]}
    if not evidence["tests"]["passed"]:
        print(log.getvalue())
    manifest = run_master(output_dir=output)
    independent = inspect_master(output)
    evidence["manifest"] = manifest
    evidence["independent_validation"] = independent
    evidence["review_decision"] = json.loads((ROOT / "reviews/master-data-realism-review.json").read_text())
    passed_tests = {r["test"].split(".")[-1] for r in results.records if r["status"] == "PASS"}
    required = {
        "structural_temporal_master_checks": ["test_full_field_schema_not_fixture_projection", "test_foreign_key_orphan_is_rejected", "test_exclusive_bitemporal_rectangles_and_revision_sequence", "test_primary_coverage_changes_and_selfpay", "test_manager_cycle_and_temporal_resolution"],
        "stratified_realism_review": ["test_identity_review_is_stratified_and_content_bound", "test_real_names_contacts_and_adult_eligibility", "test_birth_cohort_weights_and_demographic_bands"],
        "required_domains_source_authorities": ["test_complete_master_scope_and_budget", "test_source_authority_and_availability", "test_typed_crosswalks_no_fuzzy_or_ambiguous_mapping", "test_official_and_local_reference_semantics", "test_workday_and_axiom_identity_projections"],
        "no_critical_identity_realism_defects": ["test_names_do_not_determine_self_report_or_opening_health", "test_revocation_blocks_and_active_scopes_remain", "test_opening_health_has_no_fabricated_encounters_or_future_outcomes", "test_independent_inspector_checks_files_and_recalculates"],
        "end_to_end_rebuild_and_recovery": ["test_clean_rebuild_matches_all_business_and_stage_hashes", "test_cached_resume_preserves_exact_business_hashes", "test_real_process_crash_rolls_back_and_resumes_without_duplicate_rows", "test_failed_upstream_invalidates_descendants_before_recomputation", "test_changed_seed_keeps_all_master_rules_and_requires_fresh_review"]}
    common = (built.returncode == 0 and evidence["design_regression"]["passed"] and evidence["frozen_design_hashes_unchanged"]
              and evidence["tests"]["passed"] and manifest["status"] == independent["gate_status"] == "MASTER_FOUNDATION_PASSED"
              and not independent["defects"])
    exits = {name: {"passed": common and set(tests) <= passed_tests, "evidence_tests": tests} for name, tests in required.items()}
    evidence["exit_criteria"] = exits
    evidence["passed"] = common and all(r["passed"] for r in exits.values())
    paths = sorted((ROOT / "tests").glob("*.py")) + [ROOT / ("scripts/" + name) for name in ("generate_master_data.py", "validate_master_data.py", "validate_master_foundation.py", "import_public_references.py")]
    evidence["verification_source_sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    gate = {"implementation_phase": 2, "status": "PASSED" if evidence["passed"] else "BLOCKED", "evaluated_at": evidence["evaluated_at"],
            "exit_criteria": exits, "tests_run": results.testsRun, "master_data_rows": manifest["business_rows"],
            "stable_patients": 20000, "stable_workers": 300, "generated_business_tables": 11, "frozen_release_business_tables": 25,
            "opening_problem_allergy_rows": 13000, "reviewed_patient_identities": 100, "reviewed_worker_identities": 50,
            "remaining_planned_rows": manifest["remaining_planned_rows"], "business_sha256": manifest["business_sha256"],
            "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION", "next_phase": "Longitudinal clinical histories - not started"}
    return evidence, gate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/master-foundation")
    parser.add_argument("--report", type=Path, default=ROOT / "evidence/master-data/validation-report.json")
    parser.add_argument("--gate", type=Path, default=ROOT / "evidence/master-data/acceptance-gate.json")
    args = parser.parse_args()
    pending = {"implementation_phase": 2, "status": "EVALUATING", "passed": False, "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}
    write(args.report, pending)
    write(args.gate, pending)
    try:
        evidence, gate = evaluate(args.output)
    except Exception as exc:
        evidence = gate = {**pending, "status": "BLOCKED", "error": str(exc)}
    write(args.report, evidence)
    write(args.gate, gate)
    print(json.dumps({k: gate[k] for k in ("implementation_phase", "status", "tests_run", "master_data_rows") if k in gate}))
    return 0 if gate["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
