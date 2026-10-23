import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from decimal import localcontext, ROUND_DOWN
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from healthcare_synthetic.engine import STAGES, Store, check_budget, merged, run, single_writer
from healthcare_synthetic.stages import IMPLEMENTATIONS
from healthcare_synthetic.validation import gate, validate_candidate, validate_exports
from validate_phase1_candidate import inspect


class EngineTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "output").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="phase1-tests-", dir=ROOT / "output")
        self.work = Path(self.temp.name)
        self.config = json.loads((ROOT / "config/phase1-development.json").read_text())
        self.config_path = self.work / "config.json"
        self.write_config()

    def tearDown(self):
        self.temp.cleanup()

    def write_config(self):
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")

    def generate(self, name="candidate", **kwargs):
        return run(ROOT, self.config_path, self.work / name, **kwargs)

    def read(self, leaf, name="candidate"):
        return json.loads((self.work / name / leaf).read_text(encoding="utf-8"))

    def test_clean_build_cached_resume_and_manifest_accounting(self):
        first = self.generate()
        again = self.generate()
        self.assertEqual(first["status"], "FIXTURES_PASSED")
        self.assertEqual(first["executed"], list(STAGES))
        self.assertEqual(again["reused"], list(STAGES))
        self.assertEqual(first["business_sha256"], again["business_sha256"])
        self.assertEqual(first["stage_checksums"], again["stage_checksums"])
        self.assertEqual(first["business_rows"], 30)
        self.assertEqual(first["serialized_mirror_rows"], 3)
        self.assertEqual(first["fixture_projection_count"], 15)
        self.assertFalse(first["dataset_accepted"])
        self.assertEqual(first["solution_status"], "BLOCKED_FOR_SOLUTION")
        self.assertEqual(len(self.read("validation.json")["results"]), 193)

    def test_clean_rebuild_has_identical_business_and_stage_hashes(self):
        a, b = self.generate("one"), self.generate("two")
        self.assertEqual(a["business_sha256"], b["business_sha256"])
        self.assertEqual(a["stage_checksums"], b["stage_checksums"])
        self.assertEqual(self.read("fixture-tables.json", "one"), self.read("fixture-tables.json", "two"))

    def test_seed_change_varies_individuals_and_keeps_constraints(self):
        first = self.generate("one")
        self.config["seed"] += 1
        self.write_config()
        second = self.generate("two")
        self.assertNotEqual(first["business_sha256"], second["business_sha256"])
        self.assertEqual(second["status"], "FIXTURES_PASSED")
        a, b = self.read("fixture-tables.json", "one"), self.read("fixture-tables.json", "two")
        self.assertEqual({r["key"] for r in a["patient"]}, {r["key"] for r in b["patient"]})

    def test_every_stage_exception_rolls_back_then_resumes_without_duplicates(self):
        clean = self.generate("clean")
        for index, stage in enumerate(STAGES):
            with self.subTest(stage=stage):
                name = "failure-" + stage
                with self.assertRaisesRegex(RuntimeError, "injected failure"):
                    self.generate(name, fail_stage=stage)
                self.assertEqual(self.read("manifest.json", name)["status"], "FAILED")
                self.assertFalse((self.work / name / "fixture-tables.json").exists())
                with sqlite3.connect(self.work / name / "checkpoints.sqlite3") as db:
                    self.assertEqual(db.execute("SELECT COUNT(*) FROM stages").fetchone()[0], index)
                resumed = self.generate(name)
                self.assertEqual(resumed["business_sha256"], clean["business_sha256"])
                self.assertEqual(len(resumed["reused"]), index)
                self.assertEqual(resumed["status"], "FIXTURES_PASSED")

    def test_real_process_death_before_commit_recovers_wal_and_marks_attempt(self):
        output = self.work / "crashed"
        child = subprocess.run([sys.executable, str(ROOT / "scripts/run_phase1.py"), "--config", str(self.config_path), "--output", str(output), "--crash-stage", "billing"], capture_output=True, text=True, timeout=30)
        self.assertEqual(child.returncode, 97, child.stdout + child.stderr)
        self.assertEqual(self.read("manifest.json", "crashed")["status"], "RUNNING")
        with sqlite3.connect(output / "checkpoints.sqlite3") as db:
            self.assertEqual({r[0] for r in db.execute("SELECT name FROM stages")}, {"identities", "clinical", "demand", "resources"})
        resumed = self.generate("crashed")
        clean = self.generate("clean")
        self.assertEqual(resumed["business_sha256"], clean["business_sha256"])
        with sqlite3.connect(output / "checkpoints.sqlite3") as db:
            self.assertEqual([r[0] for r in db.execute("SELECT status FROM attempts ORDER BY id")], ["INTERRUPTED", "FIXTURES_PASSED"])

    def test_selective_config_invalidation_preserves_ancestors(self):
        first = self.generate()
        self.config["stages"]["demand"]["acuity_min"] = 3
        self.write_config()
        second = self.generate()
        self.assertEqual(second["reused"], ["identities", "clinical"])
        self.assertEqual(set(second["invalidated"]), set(STAGES) - {"identities", "clinical"})
        self.assertEqual(second["stage_checksums"]["identities"], first["stage_checksums"]["identities"])

    def test_failed_changed_upstream_removes_all_stale_descendants(self):
        self.generate()
        self.config["stages"]["demand"]["acuity_min"] = 3
        self.write_config()
        with self.assertRaises(RuntimeError):
            self.generate(fail_stage="demand")
        with sqlite3.connect(self.work / "candidate/checkpoints.sqlite3") as db:
            self.assertEqual({r[0] for r in db.execute("SELECT name FROM stages")}, {"identities", "clinical"})
        self.assertFalse((self.work / "candidate/validation.json").exists())
        self.assertFalse((self.work / "candidate/fixture-tables.json").exists())
        resumed = self.generate()
        rebuilt = self.generate("clean")
        self.assertEqual(resumed["stage_checksums"], rebuilt["stage_checksums"])

    def test_validation_only_config_changes_do_not_regenerate_business(self):
        first = self.generate()
        self.config["expectations"]["closing_cash"] = "49.00"
        self.write_config()
        second = self.generate()
        self.assertEqual(second["executed"], ["validation"])
        self.assertEqual(second["status"], "BLOCKED")
        self.assertEqual(second["business_sha256"], first["business_sha256"])

    def test_critical_failure_blocks_and_defect_resolves_after_upstream_fix(self):
        self.config["stages"]["clinical"]["unit"] = "WRONG_UNIT"
        self.write_config()
        blocked = self.generate()
        self.assertEqual(blocked["status"], "BLOCKED")
        defects = self.read("validation.json")["defects"]
        self.assertIn("P1_CHRONOLOGY", {d["rule_id"] for d in defects})
        self.assertTrue(all(d["record_key"] for d in defects))
        self.config["stages"]["clinical"]["unit"] = "%"
        self.write_config()
        self.assertEqual(self.generate()["status"], "FIXTURES_PASSED")
        with sqlite3.connect(self.work / "candidate/checkpoints.sqlite3") as db:
            self.assertEqual({r[0] for r in db.execute("SELECT status FROM defects")}, {"RESOLVED"})

    def test_budget_exceeded_before_any_stage_publication(self):
        self.config["fixture_cap"] = 1
        self.write_config()
        with self.assertRaisesRegex(ValueError, "record budget exceeded"):
            self.generate()
        with sqlite3.connect(self.work / "candidate/checkpoints.sqlite3") as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM stages").fetchone()[0], 0)
        self.assertEqual(self.read("manifest.json")["status"], "FAILED")

    def test_aggregate_budget_counts_child_rows_and_all_versions(self):
        self.config["fixture_cap"] = 29
        self.write_config()
        with self.assertRaisesRegex(ValueError, "30 > 29"):
            self.generate()
        with sqlite3.connect(self.work / "candidate/checkpoints.sqlite3") as db:
            self.assertNotIn("billing", {r[0] for r in db.execute("SELECT name FROM stages")})

    def test_no_full_generation_profile_unknown_fields_or_clock_change(self):
        mutations = [lambda c: c.update(profile="FULL_RELEASE"), lambda c: c.update(fixture_cap=2_000_000),
                     lambda c: c["stages"]["demand"].update(ignored_typo=1), lambda c: c["clock"].update(end="2027-01-01T00:00:00Z")]
        for change in mutations:
            original = copy.deepcopy(self.config)
            change(self.config)
            self.write_config()
            with self.subTest(config=self.config), self.assertRaises(ValueError):
                self.generate()
            self.config = original

    def test_checkpoint_corruption_fails_closed(self):
        self.generate()
        with sqlite3.connect(self.work / "candidate/checkpoints.sqlite3") as db:
            db.execute("UPDATE stages SET payload='{}' WHERE name='demand'")
        with self.assertRaisesRegex(ValueError, "checkpoint corruption"):
            self.generate()
        self.assertEqual(self.read("manifest.json")["status"], "FAILED")

    def test_second_process_cannot_write_active_run_directory(self):
        output = self.work / "locked"
        with single_writer(output / "run.lock"):
            child = subprocess.run([sys.executable, str(ROOT / "scripts/run_phase1.py"), "--config", str(self.config_path), "--output", str(output)], capture_output=True, text=True, timeout=30)
            self.assertEqual(child.returncode, 1)
            self.assertIn("another process", child.stdout)
        self.assertEqual(self.generate("locked")["status"], "FIXTURES_PASSED")

    def test_projection_detects_arithmetic_and_chronology_changes_independently(self):
        self.generate()
        tables = self.read("fixture-tables.json")
        for table, field, value, rule in (("service_charge", "billed", "101.00", "P1_FINANCE"),
                                          ("encounter", "end", "2023-01-01T00:00:00Z", "P1_CHRONOLOGY"),
                                          ("bed_interval", "patient", "ORPHAN", "P1_REFERENCES")):
            changed = copy.deepcopy(tables)
            changed[table][0][field] = value
            result = validate_candidate(changed, self.config["expectations"])
            self.assertEqual(next(r for r in result if r["rule_id"] == rule)["status"], "FAIL")
            self.assertEqual(gate(result)["status"], "BLOCKED")

    def test_independent_export_validator_finds_corrupt_source(self):
        self.generate()
        tables = self.read("fixture-tables.json")
        store = Store(self.work / "candidate/checkpoints.sqlite3")
        try:
            envelopes = json.loads(store.stages()["serialization"]["payload"])["controls"]["envelopes"]
        finally:
            store.close()
        self.assertEqual(validate_exports(tables, envelopes)["status"], "PASS")
        envelopes[0]["payload"] += "BROKEN"
        self.assertEqual(validate_exports(tables, envelopes)["status"], "FAIL")

    def test_reconciliation_reports_observed_values_and_differences(self):
        self.generate()
        report = self.read("validation.json")
        self.assertTrue(all(float(r["difference"]) == 0 for r in report["reconciliation"].values()))
        self.assertEqual(report["reconciliation"]["occupied_seconds"]["observed"], "10800")
        self.assertEqual(report["reconciliation"]["closing_ar"]["observed"], "50.00")

    def test_unregistered_tables_nested_rows_and_duplicate_owners_rejected(self):
        schema = json.loads((ROOT / "contracts/phase0/schema.json").read_text())
        for tables in ({"new_table": [{"key": "x"}]}, {"patient": [{"key": "x", "facts": [1, 2]}]}, {"facility": [{"key": str(i)} for i in range(4)]}):
            with self.subTest(tables=tables), self.assertRaises(ValueError):
                check_budget(tables, 100, schema)
        with self.assertRaises(ValueError):
            merged({"one": {"tables": {"patient": []}}, "two": {"tables": {"patient": []}}})

    def test_runtime_lock_mismatch_stops_run(self):
        with patch("healthcare_synthetic.engine.platform.python_version", return_value="0.0.0"):
            with self.assertRaisesRegex(ValueError, "runtime differs"):
                self.generate()

    def test_reference_bytes_change_invalidates_every_stage(self):
        reference = json.loads((ROOT / self.config["reference"]).read_text())
        reference_path = self.work / "references.json"
        reference_path.write_text(json.dumps(reference), encoding="utf-8")
        self.config["reference"] = reference_path.relative_to(ROOT).as_posix()
        self.write_config()
        self.generate()
        reference["note"] += " Reviewed reference correction."
        reference_path.write_text(json.dumps(reference), encoding="utf-8")
        changed = self.generate()
        self.assertEqual(changed["executed"], list(STAGES))
        self.assertEqual(set(changed["invalidated"]), set(STAGES))

    def test_code_hash_change_invalidates_every_stage(self):
        from healthcare_synthetic.engine import locks
        original = locks(ROOT, self.config)
        self.generate()
        changed = copy.deepcopy(original)
        changed["code"]["src/healthcare_synthetic/core.py"] = "new-code-digest"
        with patch("healthcare_synthetic.engine.locks", return_value=changed):
            result = self.generate()
        self.assertEqual(result["executed"], list(STAGES))
        self.assertEqual(set(result["invalidated"]), set(STAGES))

    def test_mandatory_negative_controls_cannot_be_disabled(self):
        self.config["stages"]["faults"]["enabled"] = False
        self.write_config()
        with self.assertRaisesRegex(ValueError, "cannot be disabled"):
            self.generate()

    def test_failure_cli_exit_status(self):
        self.config["stages"]["clinical"]["unit"] = "WRONG"
        self.write_config()
        child = subprocess.run([sys.executable, str(ROOT / "scripts/run_phase1.py"), "--config", str(self.config_path), "--output", str(self.work / "cli")], capture_output=True, text=True, timeout=30)
        self.assertEqual(child.returncode, 2)
        self.assertIn('"status": "BLOCKED"', child.stdout)

    def test_readonly_independent_candidate_runner(self):
        self.generate()
        result = inspect(self.work / "candidate", self.config_path)
        self.assertEqual(result["gate"]["status"], "FIXTURES_PASSED")
        self.assertFalse(result["gate"]["dataset_accepted"])
        self.assertEqual(len(result["results"]), 8)
        self.assertFalse(result["defects"])

    def test_independent_runner_rejects_modified_business_file(self):
        self.generate()
        path = self.work / "candidate/fixture-tables.json"
        tables = self.read("fixture-tables.json")
        tables["service_charge"][0]["billed"] = "101.00"
        path.write_text(json.dumps(tables), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "business artifact checksum"):
            inspect(self.work / "candidate", self.config_path)

    def test_ambient_decimal_settings_do_not_change_business_or_validation(self):
        original = self.generate("default-context")
        with localcontext() as context:
            context.prec = 6
            context.rounding = ROUND_DOWN
            changed = self.generate("modified-context")
            checked = inspect(self.work / "modified-context", self.config_path)
        self.assertEqual(original["business_sha256"], changed["business_sha256"])
        self.assertEqual(changed["status"], "FIXTURES_PASSED")
        self.assertEqual(checked["gate"]["status"], "FIXTURES_PASSED")

    def test_delivery_grace_does_not_allow_post_cutoff_care(self):
        self.generate()
        tables = self.read("fixture-tables.json")
        for row in tables["encounter"]:
            row["start"] = row["start"].replace("2024-11-03", "2026-01-02")
            row["end"] = row["end"].replace("2024-11-03", "2026-01-02")
        result = next(r for r in validate_candidate(tables, self.config["expectations"]) if r["rule_id"] == "P1_CHRONOLOGY")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("delivery grace", result["failures"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
