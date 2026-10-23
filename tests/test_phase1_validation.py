import ast
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from healthcare_synthetic import validation
from healthcare_synthetic.stages import microfixtures, mutate


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "contracts/phase1/rule-fixtures.json").read_text())

    def test_all_frozen_rule_families_have_positive_and_negative_controls(self):
        frozen = json.loads((ROOT / "contracts/phase0/validation-rules.json").read_text())["rules"]
        self.assertEqual({r["id"]: r["severity"] for r in frozen}, {r["rule_id"]: r["severity"] for r in self.catalog["cases"]})
        self.assertEqual(set(validation.RULES), {r["id"] for r in frozen})
        self.assertEqual(len(self.catalog["cases"]), 55)
        self.assertTrue(all(c["faults"] for c in self.catalog["cases"]))

    def test_all_55_positive_and_adverse_cases(self):
        for case in self.catalog["cases"]:
            with self.subTest(rule=case["rule_id"]):
                result = validation.execute(case["rule_id"], case["positive"], case["severity"], case["case_key"])
                self.assertEqual(result["status"], "PASS", result)

    def test_all_123_faults_use_intended_detector_and_block_gate(self):
        count = 0
        for case in self.catalog["cases"]:
            for fault in case["faults"]:
                with self.subTest(rule=case["rule_id"], fault=fault["name"]):
                    data = case["positive"]
                    for change in fault["changes"]:
                        data = mutate(data, change["path"], change["value"])
                    result = validation.execute(case["rule_id"], data, case["severity"], case["case_key"])
                    self.assertEqual(result["status"], "FAIL")
                    self.assertIn(fault["reason_contains"], result["failures"][0]["reason"])
                    self.assertEqual(validation.gate([result])["status"], "BLOCKED")
                    self.assertEqual(result["failures"][0]["record_key"], case["case_key"])
                    count += 1
        self.assertEqual(count, 123)

    def test_critical_detector_removed_is_caught_by_negative_controls(self):
        with patch.dict(validation.RULES, {"CH01": lambda data: None}):
            _, negative = microfixtures(self.catalog)
        misses = [r for r in negative if r["status"] == "FAIL"]
        self.assertEqual({r["rule_id"] for r in misses}, {"CH01"})

    def test_validator_arithmetic_does_not_use_generator_rounding(self):
        case = next(c for c in self.catalog["cases"] if c["rule_id"] == "CH01")
        with patch("healthcare_synthetic.core.money", side_effect=AssertionError("generator helper used")):
            self.assertEqual(validation.execute("CH01", case["positive"])["status"], "PASS")
            bad = mutate(case["positive"], "rows.0.billed", "1.00")
            self.assertEqual(validation.execute("CH01", bad)["status"], "FAIL")

    def test_validator_module_has_no_generation_imports(self):
        tree = ast.parse((ROOT / "src/healthcare_synthetic/validation.py").read_text())
        imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(any(x.startswith(("healthcare_synthetic", "core", "stages", "sources", "engine")) for x in imports))

    def test_unknown_rule_and_missing_fields_fail_closed(self):
        for rule, data in (("MISSING", {}), ("CH01", {})):
            result = validation.execute(rule, data, key="C99")
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(validation.gate([result])["status"], "BLOCKED")
            self.assertEqual(result["failures"][0]["record_key"], "C99")

    def test_empty_or_invalid_gate_evidence_cannot_pass(self):
        for rows in ([], [{"status": "SKIP", "severity": "P0"}], [{"status": "FAIL", "severity": "UNKNOWN"}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                validation.gate(rows)

    def test_defect_ids_stable_across_reason_changes(self):
        a = validation.execute("CH01", {}, key="C99")
        b = copy.deepcopy(a)
        b["failures"][0]["reason"] = "updated investigation"
        self.assertEqual(validation.defects([a])[0]["defect_id"], validation.defects([b])[0]["defect_id"])
        self.assertNotEqual(validation.defects([a])[0]["defect_id"], validation.defects([validation.execute("CH01", {}, key="C100")])[0]["defect_id"])

    def test_profile_preserves_null_distinct_and_extrema(self):
        p = validation.profile({"value": [{"key": "A", "v": None}, {"key": "B", "v": 2}, {"key": "C", "v": 4}]})
        self.assertEqual(p["value"]["rows"], 3)
        self.assertEqual(p["value"]["columns"]["v"], {"nulls": 1, "distinct": 2, "min": 2, "max": 4})

    def test_real_adverse_outcomes_do_not_equal_malformed_data(self):
        adverse = [c for c in self.catalog["cases"] if c["classification"] == "ADVERSE_OUTCOME"]
        self.assertGreaterEqual(len(adverse), 5)
        for case in adverse:
            self.assertEqual(validation.execute(case["rule_id"], case["positive"])["status"], "PASS")

    def test_offsetting_financial_errors_fail_at_declared_grain(self):
        for rule in ("GL02", "AX01", "FN01"):
            case = next(c for c in self.catalog["cases"] if c["rule_id"] == rule)
            fault = next(f for f in case["faults"] if "offsetting" in f["name"])
            data = mutate(case["positive"], fault["changes"][0]["path"], fault["changes"][0]["value"])
            self.assertEqual(validation.execute(rule, data)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
