"""Negative controls for the design validator, not synthetic data generation tests."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_phase0 import load_contracts, run_checks

class Phase0ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_contracts()

    def mutate_and_fail(self, mutation, expected_check):
        bundle = copy.deepcopy(self.baseline)
        mutation(bundle)
        result = {x["id"]: x["passed"] for x in run_checks(bundle)}
        self.assertFalse(result[expected_check], expected_check)

    def test_frozen_baseline(self):
        self.assertTrue(all(x["passed"] for x in run_checks(self.baseline)))

    def test_over_cap(self):
        self.mutate_and_fail(lambda b: b["schema"]["tables"][0].update(planned_rows=2000001), "BUDGET")

    def test_budget_mismatch(self):
        self.mutate_and_fail(lambda b: b["baseline"]["tables"].update(facility=4), "BUDGET_SYNC")

    def test_duplicate_table(self):
        self.mutate_and_fail(lambda b: b["schema"]["tables"].append(copy.deepcopy(b["schema"]["tables"][0])), "TABLE_COUNT")

    def test_missing_fk_target(self):
        def mutate(b):
            next(c for t in b["schema"]["tables"] for c in t["columns"] if "references" in c)["references"] = "absent.id"
        self.mutate_and_fail(mutate, "REFERENCES")

    def test_fk_to_nonunique_stable_identity(self):
        def mutate(b):
            next(c for t in b["schema"]["tables"] for c in t["columns"] if "references" in c)["references"] = "patient.patient_id"
        self.mutate_and_fail(mutate, "REFERENCES")

    def test_nullable_primary_key(self):
        self.mutate_and_fail(lambda b: b["schema"]["tables"][0]["columns"][0].update(nullable=True), "DICTIONARY")

    def test_hidden_nested_business_facts(self):
        self.mutate_and_fail(lambda b: b["schema"]["tables"][0]["columns"][0].update(type="ARRAY<STRING>"), "DICTIONARY")

    def test_omitted_clinical_family(self):
        self.mutate_and_fail(lambda b: b["clinical-type-matrix"]["types"].pop("MED_ADMIN"), "CLINICAL_MATRIX")

    def test_unknown_source_column(self):
        self.mutate_and_fail(lambda b: b["source-contracts"]["source_families"][0]["maps"].update(Bad="absent"), "SOURCES")

    def test_realism_share_sum(self):
        self.mutate_and_fail(lambda b: b["realism-targets"]["targets"][0]["target"].update({"18-34": 0.99}), "REALISM_TARGETS")

    def test_unbudgeted_encounter_history(self):
        self.mutate_and_fail(lambda b: b["baseline"]["network"].update(encounter_lifecycle_revision_rows=0), "ENCOUNTER_ROWS")

    def test_impossible_occupancy(self):
        self.mutate_and_fail(lambda b: b["baseline"]["network"].update(planned_bed_days=80000), "OCCUPANCY")

    def test_insufficient_staff(self):
        self.mutate_and_fail(lambda b: b["baseline"]["staffing"].update(rn_share_of_work_shifts=0.1), "STAFF_FEASIBILITY")

    def test_unbudgeted_claim_events(self):
        self.mutate_and_fail(lambda b: b["baseline"]["claim_budget"]["events"].update(PAYMENT=100000), "CLAIM_ROWS")

    def test_scenario_refers_to_unknown_rule(self):
        self.mutate_and_fail(lambda b: b["scenarios"]["scenarios"][0]["rule_ids"].append("MISSING"), "SCENARIOS")

    def test_premature_data_validation_claim(self):
        self.mutate_and_fail(lambda b: b["validation-rules"]["rules"][0].update(implementation_status="PASSED"), "RULE_CATALOG")

    def test_solution_cannot_unlock(self):
        self.mutate_and_fail(lambda b: b["baseline"].update(solution_status="READY"), "SOLUTION_LOCK")

    def test_offsetting_financial_grid_errors(self):
        def mutate(b):
            grid = b["baseline"]["finance_row_breakdown"]
            grid["actual_stats_15_centers_4_measures_36_months"] += 100
            grid["budget_stats_3_centers_4_measures_36_months"] -= 100
        self.mutate_and_fail(mutate, "FINANCIAL_GRID")

    def test_unfunded_allocation_fanout(self):
        self.mutate_and_fail(lambda b: b["baseline"]["cost_allocation_components"].update(transfer_centers=90000), "ALLOCATION_FEASIBILITY")

    def test_omitted_clinical_budget_family(self):
        self.mutate_and_fail(lambda b: b["baseline"]["clinical_event_budget"].update(MED_ADMIN=0), "CLINICAL_BUDGET_FAMILIES")

    def test_unbudgeted_cost_pool_journals(self):
        self.mutate_and_fail(lambda b: b["baseline"]["financial_posting_budget"].update(monthly_pool_close=100), "POOL_CLOSE_LINES")

    def test_grace_cannot_add_another_business_year(self):
        self.mutate_and_fail(lambda b: b["baseline"].update(final_export_grace_end_utc="2026-12-31T23:59:59Z"), "EXPORT_GRACE")

if __name__ == "__main__":
    unittest.main()
