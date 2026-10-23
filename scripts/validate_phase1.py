"""Execute Phase 1 gate evidence: regression, tests, clean rebuild and independent inspection."""
import argparse
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from healthcare_synthetic.engine import run
from validate_phase0 import report as phase0_report
from validate_phase1_candidate import inspect


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.started = {}

    def startTest(self, test):
        self.started[test.id()] = time.monotonic()
        super().startTest(test)

    def addSuccess(self, test):
        self.records.append({"test": test.id(), "status": "PASS", "seconds": round(time.monotonic() - self.started[test.id()], 6)})
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.records.append({"test": test.id(), "status": "FAIL"})
        super().addFailure(test, err)

    def addError(self, test, err):
        self.records.append({"test": test.id(), "status": "ERROR"})
        super().addError(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.records.append({"test": str(subtest), "status": "FAIL"})
        super().addSubTest(test, subtest, err)


def validate():
    result = {"phase": 1, "evaluated_at": datetime.now(timezone.utc).isoformat(),
              "scope": "Development framework and microfixtures; no full business-data acceptance"}
    check = subprocess.run([sys.executable, str(ROOT / "scripts/build_phase0_spec.py"), "--check"], capture_output=True, text=True, timeout=30)
    result["phase0_generated_artifacts"] = {"passed": check.returncode == 0, "output": (check.stdout + check.stderr).strip()}
    result["phase0_regression"] = phase0_report()
    historical = json.loads((ROOT / "evidence/phase-0/validation-report.json").read_text(encoding="utf-8"))
    result["phase0_frozen_hashes_unchanged"] = result["phase0_regression"]["contract_sha256"] == historical["contract_sha256"]
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    log = io.StringIO()
    tests = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordingResult).run(suite)
    result["tests"] = {"run": tests.testsRun, "passed": tests.wasSuccessful() and not tests.skipped,
                       "failures": len(tests.failures), "errors": len(tests.errors), "skipped": len(tests.skipped),
                       "cases": tests.records, "failure_details": [message for _, message in tests.failures + tests.errors]}
    (ROOT / "output").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="phase1-gate-", dir=ROOT / "output") as directory:
        location = Path(directory)
        first = run(ROOT, ROOT / "config/phase1-development.json", location / "first")
        clean = run(ROOT, ROOT / "config/phase1-development.json", location / "clean")
        resumed = run(ROOT, ROOT / "config/phase1-development.json", location / "first")
        independent = inspect(location / "first", ROOT / "config/phase1-development.json")
        validation = json.loads((location / "first/validation.json").read_text(encoding="utf-8"))
        # Paths and execution timestamps do not enter any business or stage checksum.
        result["end_to_end"] = {"first_manifest": first, "clean_rebuild_business_sha256": clean["business_sha256"],
                                "clean_rebuild_stage_checksums": clean["stage_checksums"], "resume_reused_stages": resumed["reused"],
                                "deterministic": first["business_sha256"] == clean["business_sha256"] == resumed["business_sha256"]
                                                 and first["stage_checksums"] == clean["stage_checksums"] == resumed["stage_checksums"],
                                "validation": validation, "independent_validation": independent}
    paths = sorted((ROOT / "tests").glob("test_*.py")) + sorted((ROOT / "scripts").glob("*phase1*.py"))
    result["test_and_runner_sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    result["passed"] = (result["phase0_generated_artifacts"]["passed"] and result["phase0_regression"]["passed"] and result["phase0_frozen_hashes_unchanged"]
                        and result["tests"]["passed"] and result["end_to_end"]["deterministic"]
                        and first["status"] == independent["gate"]["status"] == "FIXTURES_PASSED")
    if not result["tests"]["passed"]:
        print(log.getvalue())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "evidence/phase-1/validation-report.json")
    parser.add_argument("--gate", type=Path, default=ROOT / "evidence/phase-1/gate.json")
    args = parser.parse_args()
    # Mark this evaluation in progress before any check; stale PASS evidence cannot
    # survive a failed new attempt. These files also make first-run doc links valid.
    for path, pending in ((args.report, {"phase": 1, "passed": False, "status": "EVALUATING"}),
                          (args.gate, {"phase": 1, "status": "EVALUATING", "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"})):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pending, indent=2) + "\n", encoding="utf-8")
    try:
        result = validate()
    except Exception as exc:
        failure = {"phase": 1, "passed": False, "status": "BLOCKED", "error": str(exc),
                   "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}
        for path in (args.report, args.gate):
            path.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure))
        return 1
    test_ids = {r["test"].split(".")[-1] for r in result["tests"]["cases"] if r["status"] == "PASS"}
    criteria = {
        "positive_and_adverse_fixtures": ["test_all_55_positive_and_adverse_cases", "test_all_frozen_rule_families_have_positive_and_negative_controls"],
        "negative_controls_and_independence": ["test_all_123_faults_use_intended_detector_and_block_gate", "test_validator_arithmetic_does_not_use_generator_rounding", "test_validator_module_has_no_generation_imports"],
        "determinism_and_seed_variation": ["test_clean_rebuild_has_identical_business_and_stage_hashes", "test_seed_change_varies_individuals_and_keeps_constraints", "test_streams_do_not_reshuffle_existing_people"],
        "restart_and_invalidation": ["test_every_stage_exception_rolls_back_then_resumes_without_duplicates", "test_real_process_death_before_commit_recovers_wal_and_marks_attempt", "test_failed_changed_upstream_removes_all_stale_descendants"],
        "budgets": ["test_aggregate_budget_counts_child_rows_and_all_versions", "test_budget_exceeded_before_any_stage_publication", "test_no_full_generation_profile_unknown_fields_or_clock_change"],
        "failed_critical_rule_blocks": ["test_critical_failure_blocks_and_defect_resolves_after_upstream_fix", "test_critical_detector_removed_is_caught_by_negative_controls"],
        "source_recovery": ["test_all_seven_source_recovery_behaviors", "test_bad_row_is_atomic_and_repair_restores_certification"],
        "development_only_boundary": ["test_clean_build_cached_resume_and_manifest_accounting", "test_no_full_generation_profile_unknown_fields_or_clock_change"]}
    exits = {key: {"passed": result["passed"] and set(required) <= test_ids, "evidence_tests": required} for key, required in criteria.items()}
    passed = result["passed"] and all(c["passed"] for c in exits.values())
    gate_artifact = {"phase": 1, "status": "PASSED" if passed else "BLOCKED", "evaluated_at": result["evaluated_at"],
                     "exit_criteria": exits, "reviewer": "Codex technical self-review under user authorization",
                     "review_scope": "Framework engineering and test evidence; no licensed clinical signoff or full-data approval claimed",
                     "tests_run": result["tests"]["run"], "microfixture_rule_families": 55,
                     "deliberate_rule_faults": 123, "source_recovery_behaviors": 7,
                     "development_business_rows": result["end_to_end"]["first_manifest"]["business_rows"],
                     "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION", "next_phase": "Phase 2 - not started"}
    for path, value in ((args.report, result), (args.gate, gate_artifact)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": 1, "status": gate_artifact["status"], "tests": result["tests"]["run"],
                      "phase0_checks": result["phase0_regression"]["check_count"], "fixture_business_sha256": result["end_to_end"]["first_manifest"]["business_sha256"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
