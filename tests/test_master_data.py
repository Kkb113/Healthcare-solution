"""Full-cohort master-data, fault, consumer and recovery tests."""
import ast
import copy
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from healthcare_synthetic.master_generation import MasterGenerator
from healthcare_synthetic.master_pipeline import GRAPH, load_inputs, run_master
from healthcare_synthetic.master_queries import authorized, eligible_worker, person_at, primary_coverage, source_target, worker_at
from healthcare_synthetic.master_review import render_review, review_gate
from healthcare_synthetic.master_validation import MasterValidator, contains, years
from healthcare_synthetic.source_identity_projection import axiom_center_record, patient_identity_record, workday_identity_record
from validate_master_data import inspect_master


class MasterDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / "output").mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="master-validation-tests-", dir=ROOT / "output")
        cls.work = Path(cls.temp.name)
        cls.config_path = ROOT / "config/master-data-generation.json"
        cls.cfg, cls.policy, cls.schema, cls.refs, _ = load_inputs(cls.config_path)
        cls.base = cls.work / "baseline"
        cls.manifest = run_master(cls.config_path, cls.base)
        cls.tables = {name: [json.loads(line) for line in (cls.base / meta["file"]).read_text(encoding="utf-8").splitlines()]
                      for name, meta in cls.manifest["canonical_files"].items()}
        cls.checked = json.loads((cls.base / "validation-report.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def validator(self, tables=None):
        return MasterValidator(self.tables if tables is None else tables, self.schema, self.cfg, self.policy, self.refs)

    def fault(self, check, table, index, changes, expected):
        tables = dict(self.tables)
        tables[table] = list(tables[table])
        tables[table][index] = {**tables[table][index], **changes}
        outcome = self.validator(tables).check(check)
        self.assertEqual(outcome["status"], "FAIL", outcome)
        self.assertIn(expected, outcome["failures"][0]["reason"])
        self.assertTrue(outcome["failures"][0]["record_key"])

    def clone_checkpoints(self, name):
        target = self.work / name
        target.mkdir()
        with sqlite3.connect(self.base / "checkpoints.sqlite3") as source, sqlite3.connect(target / "checkpoints.sqlite3") as destination:
            source.backup(destination)
        (target / "manifest.json").write_text(json.dumps({"profile": "MASTER_FOUNDATION"}))
        return target

    def custom_config(self, name, mutation):
        cfg = copy.deepcopy(self.cfg)
        mutation(cfg)
        path = self.work / (name + ".json")
        path.write_text(json.dumps(cfg), encoding="utf-8")
        return path

    def test_complete_master_scope_and_budget(self):
        self.assertEqual(self.checked["status"], "MASTER_CHECKS_PASSED", self.checked.get("defects"))
        self.assertEqual(self.manifest["business_rows"], 78922)
        self.assertEqual(len(self.tables), 11)
        self.assertEqual({t: len(r) for t, r in self.tables.items()}, self.cfg["budgets"])
        self.assertEqual(self.manifest["remaining_planned_rows"], 1879288)
        self.assertFalse(self.manifest["full_dataset_accepted"])
        self.assertEqual(self.manifest["solution_status"], "BLOCKED_FOR_SOLUTION")

    def test_full_field_schema_not_fixture_projection(self):
        self.assertEqual(self.validator().check("SCHEMA")["status"], "PASS")
        self.fault("SCHEMA", "patient", 0, {"given_name": None}, "required given_name")
        self.fault("SCHEMA", "location", 0, {"licensed_bed": "false"}, "wrong type")
        self.fault("SCHEMA", "worker_assignment", 0, {"fte": "0.1234567"}, "wrong type/scale")
        self.fault("SCHEMA", "patient", 0, {"administrative_sex": "PLACEHOLDER"}, "discriminator")

    def test_primary_source_keys_and_name_collisions(self):
        self.assertEqual(self.validator().check("KEYS")["status"], "PASS")
        self.assertGreaterEqual(self.checked["metrics"]["patients"]["name_collision_groups"], 10)
        tables = dict(self.tables)
        tables["patient"] = self.tables["patient"] + [self.tables["patient"][0]]
        self.assertEqual(self.validator(tables).check("KEYS")["status"], "FAIL")

    def test_foreign_key_orphan_is_rejected(self):
        self.fault("REFERENCES", "patient_coverage", 0, {"patient_version_id": "MISSING"}, "orphan")

    def test_source_authority_and_availability(self):
        self.fault("AVAILABILITY", "worker_assignment", 0, {"source_system": "AXIOM"}, "source authority")
        self.fault("AVAILABILITY", "patient", 0, {"export_available_at": "1900-01-01T00:00:00Z"}, "chronology")

    def test_exclusive_bitemporal_rectangles_and_revision_sequence(self):
        index = next(i for i, r in enumerate(self.tables["patient"]) if r["revision_no"] == 1 and r["known_to"] is not None)
        self.fault("RECTANGLES", "patient", index, {"known_to": None}, "overlapping")
        self.fault("RECTANGLES", "patient", index, {"valid_to": self.tables["patient"][index]["valid_from"]}, "valid interval")

    def test_real_names_contacts_and_adult_eligibility(self):
        for changes, reason in (({"given_name": "Patient001"}, "placeholder"), ({"birth_date": "2015-01-01"}, "adult eligibility"),
                                ({"test_email": "person@live.test"}, "reserved namespace"), ({"test_phone": "+1-217-555-1234"}, "reserved range"),
                                ({"deceased_at": "1900-01-01T00:00:00Z"}, "death precedes birth")):
            with self.subTest(changes=changes):
                self.fault("PATIENT_IDENTITIES", "patient", 0, changes, reason)
        self.assertEqual(years("2004-02-29", "2023-02-28"), 19)
        tables = dict(self.tables)
        tables["patient"] = list(self.tables["patient"])
        tables["patient"][0] = {**tables["patient"][0], "family_name": "Sample"}
        self.assertEqual(self.validator(tables).check("PATIENT_IDENTITIES")["status"], "PASS")

    def test_birth_cohort_weights_and_demographic_bands(self):
        self.assertEqual(self.validator().check("DEMOGRAPHICS")["status"], "PASS")
        self.assertEqual(self.validator().check("NAME_WEIGHTS")["status"], "PASS")
        m = self.checked["metrics"]["patients"]
        self.assertGreaterEqual(m["given_names"], 300)
        self.assertGreaterEqual(m["family_names"], 1000)
        self.assertGreaterEqual(self.checked["metrics"]["addresses"]["shared"], 1000)
        self.fault("DEMOGRAPHICS", "patient", 0, {"postal_code": "99999"}, "postal")

    def test_names_do_not_determine_self_report_or_opening_health(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["population"].update(patients=50, patient_history_changes=0)
        cfg["opening_health"].update(problems=30, allergies=5)
        refs = copy.deepcopy(self.refs)
        first = MasterGenerator(cfg, refs, "isolated-test").patients({})["patient"]
        refs["names"]["surnames"] = [["Smith", 100]]
        refs["names"]["surname_profiles"] = {key: [["Smith", 100]] for key in refs["names"]["surname_profiles"]}
        second = MasterGenerator(cfg, refs, "isolated-test").patients({})["patient"]
        fields = ("patient_id", "birth_date", "administrative_sex", "race_ethnicity", "preferred_language")
        self.assertEqual([tuple(r[f] for f in fields) for r in first], [tuple(r[f] for f in fields) for r in second])
        catalog = self.tables["catalog_item"]
        a = MasterGenerator(cfg, self.refs, "isolated-test").opening_health({"patients": {"patient": first}, "catalog": {"catalog_item": catalog}})
        b = MasterGenerator(cfg, refs, "isolated-test").opening_health({"patients": {"patient": second}, "catalog": {"catalog_item": catalog}})
        self.assertEqual(a, b)

    def test_reordering_configuration_objects_preserves_individual_records(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["population"].update(patients=50, patient_history_changes=0)
        def reverse(value):
            if isinstance(value, dict):
                return {key: reverse(value[key]) for key in reversed(value)}
            if isinstance(value, list):
                return [reverse(v) for v in value]
            return value
        a = MasterGenerator(cfg, self.refs, "order-test").patients({})
        b = MasterGenerator(reverse(cfg), self.refs, "order-test").patients({})
        self.assertEqual(a, b)

    def test_hierarchies_and_physical_capacity(self):
        self.assertEqual(self.validator().check("ORG_HIERARCHY")["status"], "PASS")
        self.fault("ORG_HIERARCHY", "location", 0, {"parent_location_id": self.tables["location"][0]["location_id"]}, "cycle")
        bed_index = next(i for i, r in enumerate(self.tables["location"]) if r["location_type"] == "BED")
        self.fault("ORG_HIERARCHY", "location", bed_index, {"licensed_bed": False}, "licensed capacity")

    def test_workforce_credentials_types_and_fte(self):
        self.assertEqual(self.checked["metrics"]["workforce"]["opening_roster_mean_fte"], "0.650000")
        self.assertEqual(self.checked["metrics"]["workforce"]["late_hires"], 18)
        self.assertEqual(self.checked["metrics"]["workforce"]["terminated"], 18)
        self.fault("WORKFORCE", "worker_assignment", 0, {"credential_code": "INVALID"}, "credential")
        self.fault("WORKFORCE", "worker_assignment", 0, {"fte": "1.100000"}, "FTE")

    def test_manager_cycle_and_temporal_resolution(self):
        self.assertEqual(self.validator().check("MANAGERS")["status"], "PASS")
        rows = list(self.tables["worker_assignment"])
        target = rows[0]["worker_id"]
        tables = dict(self.tables)
        tables["worker_assignment"] = [{**r, "manager_worker_id": target} if r["worker_id"] == target else r for r in rows]
        self.assertEqual(self.validator(tables).check("MANAGERS")["status"], "FAIL")

    def test_primary_coverage_changes_and_selfpay(self):
        self.assertEqual(self.checked["metrics"]["coverage"]["changed_patients"], 8000)
        self.assertEqual(self.validator().check("COVERAGE")["status"], "PASS")
        self.fault("COVERAGE", "payer_plan", 0, {"allowed_factor": "1.50"}, "reimbursement factor")
        tables = dict(self.tables)
        tables["patient_coverage"] = self.tables["patient_coverage"] + [dict(self.tables["patient_coverage"][0])]
        self.assertEqual(self.validator(tables).check("COVERAGE")["status"], "FAIL")

    def test_official_and_local_reference_semantics(self):
        self.assertEqual(self.checked["metrics"]["catalog"]["official_rows"], 2800)
        self.assertEqual(self.checked["metrics"]["catalog"]["local_rows"], 200)
        medication = next(i for i, r in enumerate(self.tables["catalog_item"]) if r["domain"] == "MEDICATION")
        self.fault("CATALOG", "catalog_item", medication, {"strength_per_base_unit": "999.000000"}, "attribute differs")
        self.fault("CATALOG", "catalog_item", medication, {"allergen_catalog_id": None}, "allergen")
        official = next(i for i, r in enumerate(self.tables["catalog_item"]) if r["code_system"] == "ICD-10-CM")
        self.fault("CATALOG", "catalog_item", official, {"valid_from": "2020-01-01"}, "release differs")
        accounts = {r["code"] for r in self.tables["catalog_item"] if r["domain"] == "ACCOUNT"}
        self.assertEqual(len(accounts), 17)

    def test_code_releases_cover_october_and_april_boundaries(self):
        rows = [r for r in self.tables["catalog_item"] if r["code"] == "I10"]
        for day, version in (("2023-01-01", "FY2023-OCT"), ("2023-04-01", "FY2023-APR"), ("2023-10-01", "FY2024-OCT"),
                             ("2024-04-01", "FY2024-APR"), ("2024-10-01", "FY2025-OCT"), ("2025-04-01", "FY2025-APR"), ("2025-10-01", "FY2026-OCT")):
            active = [r for r in rows if r["valid_from"] <= day < r["valid_to"]]
            self.assertEqual(len(active), 1)
            self.assertEqual(active[0]["version"], version)
        excluded = set(self.refs["codes"]["excluded_midyear_touched_pcs_codes"])
        self.assertFalse(any(r["code"] in excluded for r in self.tables["catalog_item"] if r["code_system"] == "ICD-10-PCS"))

    def test_typed_crosswalks_no_fuzzy_or_ambiguous_mapping(self):
        self.assertEqual(self.validator().check("CROSSWALKS")["status"], "PASS")
        self.fault("CROSSWALKS", "source_key_map", 0, {"target_key": "NO_TARGET"}, "typed crosswalk")
        row = next(r for r in self.tables["source_key_map"] if r["entity_type"] == "PATIENT")
        self.assertEqual(source_target(self.tables["source_key_map"], row["source_namespace"], "PATIENT", row["source_key"], "2023-03-01T12:00:00Z", "2023-03-02T12:00:00Z"), row["target_key"])
        with self.assertRaises(ValueError):
            source_target(self.tables["source_key_map"], "WRONG_NAMESPACE", "PATIENT", row["source_key"], "2023-03-01T12:00:00Z", "2023-03-02T12:00:00Z")

    def test_revocation_blocks_and_active_scopes_remain(self):
        revoked = next(r for r in self.tables["access_scope"] if r["decision"] == "REVOKED")
        first = next(r for r in self.tables["access_scope"] if r["grant_id"] == revoked["grant_id"] and r["revision_no"] == 1)
        args = (first["principal_id"], first["role"], first["scope_type"], first["scope_key"])
        self.assertTrue(authorized(self.tables, *args, "2023-03-01T12:00:00Z", "2023-03-02T12:00:00Z"))
        self.assertFalse(authorized(self.tables, *args, "2025-12-30T12:00:00Z", "2025-12-31T12:00:00Z"))
        self.fault("ACCESS", "access_scope", 0, {"scope_key": "UNKNOWN_SCOPE"}, "typed scope")

    def test_opening_health_has_no_fabricated_encounters_or_future_outcomes(self):
        self.assertEqual(self.validator().check("OPENING_HEALTH")["status"], "PASS")
        self.fault("OPENING_HEALTH", "clinical_condition", 0, {"encounter_version_id": "FAKE"}, "fabricated encounter")
        self.fault("OPENING_HEALTH", "clinical_condition", 0, {"onset_at": "2024-01-01T00:00:00Z"}, "chronology")
        allergy = next(i for i, r in enumerate(self.tables["clinical_condition"]) if r["condition_type"] == "ALLERGY")
        self.fault("OPENING_HEALTH", "clinical_condition", allergy, {"reaction": None}, "allergy substance")

    def test_patient_name_change_preserves_person_and_source_identity(self):
        versions = {}
        for row in self.tables["patient"]:
            versions.setdefault(row["patient_id"], []).append(row)
        rows = next(rows for rows in versions.values() if len({r["family_name"] for r in rows}) > 1)
        first = min(rows, key=lambda r: r["revision_no"])
        new = max(rows, key=lambda r: r["revision_no"])
        self.assertEqual(patient_identity_record(first)["MRN"], patient_identity_record(new)["MRN"])
        self.assertNotEqual(patient_identity_record(first)["NameComponentText"], patient_identity_record(new)["NameComponentText"])
        self.assertEqual(person_at(rows, first["patient_id"], new["valid_from"], first["export_available_at"])["family_name"], first["family_name"])

    def test_workday_and_axiom_identity_projections(self):
        row = self.tables["worker_assignment"][0]
        projected = workday_identity_record(row, self.tables["worker_assignment"], self.tables["cost_center"])
        self.assertEqual(projected["EmployeeID"], row["employee_number"])
        self.assertIn(row["family_name"].upper(), projected["DisplayName"])
        center = self.tables["cost_center"][0]
        self.assertEqual(axiom_center_record(center)["CostCenterReference"], "AX-" + center["cost_center_code"])

    def test_worker_hire_termination_and_retroactive_cost_consumers(self):
        rows = self.tables["worker_assignment"]
        terminated = next(r for r in rows if r["termination_date"] is not None)
        self.assertFalse(eligible_worker(rows, terminated["worker_id"], "2025-12-30T12:00:00Z", "2025-12-31T12:00:00Z"))
        late = next(r for r in rows if r["hire_date"] >= "2023-01-01")
        with self.assertRaises(ValueError):
            worker_at(rows, late["worker_id"], "2023-01-01T12:00:00Z", "2023-01-02T12:00:00Z")
        self.assertEqual(self.validator().check("ASOF")["status"], "PASS")

    def test_coverage_consumer_resolves_same_person_after_demographic_change(self):
        row = self.tables["patient"][0]
        coverage = primary_coverage(self.tables, row["patient_id"], "2025-10-15T12:00:00Z", "2025-10-16T12:00:00Z")
        patient = next(p for p in self.tables["patient"] if p["patient_version_id"] == coverage["patient_version_id"])
        self.assertEqual(patient["patient_id"], row["patient_id"])

    def test_independent_inspector_checks_files_and_recalculates(self):
        result = inspect_master(self.base)
        self.assertEqual(result["artifact_integrity"], "PASS")
        self.assertEqual(result["status"], "MASTER_CHECKS_PASSED")
        self.assertFalse(result["full_dataset_accepted"])

    def test_identity_review_is_stratified_and_content_bound(self):
        _, selection = render_review(self.tables, self.cfg)
        self.assertEqual(selection["patient_count"], 100)
        self.assertEqual(selection["worker_count"], 50)
        self.assertEqual(len([s for s in selection["patient_strata"] if s.startswith("age/")]), 5)
        self.assertEqual(len([s for s in selection["worker_strata"] if s.startswith("role/")]), 8)
        self.assertEqual(review_gate(selection, None)["status"], "PENDING_REVIEW")
        stale = {"status": "APPROVED", "sample_sha256": "WRONG", "patient_identities_reviewed": 100, "worker_identities_reviewed": 50, "unresolved_critical_findings": []}
        self.assertEqual(review_gate(selection, stale)["status"], "PENDING_REVIEW")

    def test_validator_imports_no_generation_helpers(self):
        for filename in ("src/healthcare_synthetic/master_validation.py", "scripts/validate_master_data.py"):
            tree = ast.parse((ROOT / filename).read_text())
            modules = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
            self.assertFalse(any("master_generation" in m or "master_pipeline" in m or m.endswith(".core") for m in modules), modules)

    def test_cached_resume_preserves_exact_business_hashes(self):
        repeat = run_master(self.config_path, self.base)
        self.assertEqual(repeat["business_sha256"], self.manifest["business_sha256"])
        self.assertEqual(repeat["stage_checksums"], self.manifest["stage_checksums"])
        self.assertEqual(repeat["reused"], list(GRAPH))

    def test_clean_rebuild_matches_all_business_and_stage_hashes(self):
        clean = run_master(self.config_path, self.work / "clean-rebuild")
        self.assertEqual(clean["business_sha256"], self.manifest["business_sha256"])
        self.assertEqual(clean["stage_checksums"], self.manifest["stage_checksums"])

    def test_changed_seed_keeps_all_master_rules_and_requires_fresh_review(self):
        path = self.custom_config("new-seed", lambda c: c.update(seed=c["seed"] + 1))
        alternate = run_master(path, self.work / "new-seed")
        checked = json.loads((self.work / "new-seed/validation-report.json").read_text())
        self.assertEqual(checked["status"], "MASTER_CHECKS_PASSED", checked["defects"])
        self.assertEqual(alternate["status"], "REVIEW_PENDING")
        self.assertNotEqual(alternate["business_sha256"], self.manifest["business_sha256"])

    def test_failed_upstream_invalidates_descendants_before_recomputation(self):
        destination = self.clone_checkpoints("invalidation")
        path = self.custom_config("cost-update", lambda c: c["workforce"].update(renewal_loaded_factor="1.05"))
        with self.assertRaisesRegex(RuntimeError, "injected failure"):
            run_master(path, destination, fail_stage="workforce")
        with sqlite3.connect(destination / "checkpoints.sqlite3") as connection:
            stages = {r[0] for r in connection.execute("SELECT name FROM stages")}
        self.assertFalse({"workforce", "security", "mappings", "validation"} & stages)
        self.assertTrue({"organizations", "catalog", "patients", "payers", "coverage", "opening_health"} <= stages)
        resumed = run_master(path, destination)
        self.assertEqual(resumed["status"], "REVIEW_PENDING")
        self.assertIn("patients", resumed["reused"])

    def test_real_process_crash_rolls_back_and_resumes_without_duplicate_rows(self):
        destination = self.clone_checkpoints("crash-recovery")
        with sqlite3.connect(destination / "checkpoints.sqlite3") as connection:
            for stage in ("coverage", "validation"):
                connection.execute("DELETE FROM stages WHERE name=?", (stage,))
        command = [sys.executable, str(ROOT / "scripts/generate_master_data.py"), "--output", str(destination), "--crash-stage", "coverage"]
        child = subprocess.run(command, capture_output=True, text=True, timeout=120)
        self.assertEqual(child.returncode, 97, child.stdout + child.stderr)
        with sqlite3.connect(destination / "checkpoints.sqlite3") as connection:
            self.assertNotIn("coverage", {r[0] for r in connection.execute("SELECT name FROM stages")})
        resumed = run_master(self.config_path, destination)
        self.assertEqual(resumed["business_sha256"], self.manifest["business_sha256"])
        self.assertEqual(resumed["business_rows"], 78922)

    def test_budget_rejection_and_no_later_domain_generation(self):
        path = self.custom_config("over-budget", lambda c: c["budgets"].update(patient=22001))
        with self.assertRaisesRegex(ValueError, "budget"):
            run_master(path, self.work / "rejected")
        self.assertNotIn("encounter", self.tables)
        self.assertNotIn("bed_event", self.tables)
        self.assertNotIn("financial_posting", self.tables)
        self.assertEqual(self.validator().check("BUDGET")["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
