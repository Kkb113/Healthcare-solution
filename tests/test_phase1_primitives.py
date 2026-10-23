import json
import sys
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from healthcare_synthetic.core import (Clock, age_on, allocate_cents, canonical, code_at,
                                       digest, draw, instant, local_instant, money,
                                       ordered_rows, stable_id, temporal_lookup)


class PrimitiveTests(unittest.TestCase):
    def test_canonical_unicode_and_field_order(self):
        self.assertEqual(canonical({"b": "e\u0301", "a": 1}), canonical({"a": 1, "b": "é"}))
        with self.assertRaisesRegex(ValueError, "collision"):
            canonical({"é": 1, "e\u0301": 2})

    def test_no_binary_float_or_naive_instants(self):
        for value in (0.1, datetime(2024, 1, 1), Decimal("NaN")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                canonical(value)

    def test_equivalent_utc_instants(self):
        self.assertEqual(digest(instant("2024-01-01T00:00:00Z")), digest(instant("2023-12-31T18:00:00-06:00")))
        with self.assertRaises(ValueError):
            instant("2024-01-01T00:00:00")

    def test_row_order_invariance_keeps_duplicates(self):
        rows = [{"key": "B"}, {"key": "A"}, {"key": "A"}]
        self.assertEqual(digest(ordered_rows(rows)), digest(ordered_rows(list(reversed(rows)))))
        self.assertEqual(len(ordered_rows(rows)), 3)

    def test_typed_identity_and_name_collisions(self):
        self.assertNotEqual(stable_id("person", "source-a"), stable_id("person", "source-b"))
        self.assertNotEqual(stable_id("person", 1), stable_id("person", "1"))
        self.assertNotEqual(stable_id("worker", "1"), stable_id("patient", "1"))
        self.assertEqual(stable_id("patient", "1"), stable_id("patient", "1"))
        with self.assertRaises(ValueError):
            stable_id("patient", None)

    def test_streams_do_not_reshuffle_existing_people(self):
        original = {p: [draw(42, p, "dose", i) for i in range(4)] for p in ("A", "B")}
        added = {p: [draw(42, p, "dose", i) for i in range(4)] for p in ("C", "B", "A")}
        self.assertEqual(original, {p: added[p] for p in original})
        self.assertNotEqual(original["A"], original["B"])
        self.assertNotEqual(draw(42, "A", "dose"), draw(43, "A", "dose"))
        self.assertNotEqual(draw(42, "A", "dose"), draw(42, "A", "name"))

    def test_stream_boundaries(self):
        self.assertEqual(draw(42, "A", "one", upper=1), 0)
        for kwargs in ({"upper": 0}, {"upper": 2**256 + 1}, {"index": -1}, {"upper": 3.5}, {"upper": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                draw(42, "A", "dose", **kwargs)

    def test_half_up_signed_rounding(self):
        self.assertEqual(money("0.005"), Decimal("0.01"))
        self.assertEqual(money("-0.005"), Decimal("-0.01"))
        self.assertEqual(money("3.335"), Decimal("3.34"))
        with self.assertRaises(ValueError):
            money(0.1)

    def test_allocation_conservation_and_reversal(self):
        result = allocate_cents("0.05", {"C": "1", "B": "1", "A": "1"})
        self.assertEqual(result, {"A": Decimal(".02"), "B": Decimal(".02"), "C": Decimal(".01")})
        self.assertEqual(allocate_cents("-0.05", {"A": "1", "B": "1", "C": "1"}), {k: -v for k, v in result.items()})
        self.assertEqual(sum(result.values()), Decimal(".05"))
        for weights in ({}, {"A": "0"}, {"A": "-1", "B": "2"}):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                allocate_cents("10", weights)

    def test_leap_birthdays_follow_frozen_phase0_convention(self):
        for service, expected in (("2023-02-27", 18), ("2023-02-28", 19), ("2024-02-28", 19), ("2024-02-29", 20)):
            with self.subTest(service=service):
                self.assertEqual(age_on("2004-02-29", service), expected)
        with self.assertRaises(ValueError):
            age_on("2004-02-29", "2000-01-01")

    def test_spring_gap_and_elapsed_shift(self):
        start, end = local_instant("2024-03-10T01:30:00"), local_instant("2024-03-10T03:30:00")
        self.assertEqual((end - start).total_seconds(), 3600)
        with self.assertRaisesRegex(ValueError, "nonexistent"):
            local_instant("2024-03-10T02:30:00")

    def test_fall_fold_is_explicit(self):
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            local_instant("2024-11-03T01:30:00")
        early, late = local_instant("2024-11-03T01:30:00", fold=0), local_instant("2024-11-03T01:30:00", fold=1)
        self.assertEqual((late - early).total_seconds(), 3600)
        self.assertEqual(early, datetime(2024, 11, 3, 6, 30, tzinfo=timezone.utc))
        self.assertEqual((local_instant("2024-11-03T02:30:00") - local_instant("2024-11-03T00:30:00")).total_seconds(), 10800)

    def test_retroactive_worker_asof(self):
        workers = json.loads((ROOT / "contracts/phase1/reference-fixtures.json").read_text())["workers"]
        lookup = lambda known: temporal_lookup(workers, "worker", "worker-a", "2024-11-03T00:00:00Z", known)["rate"]
        self.assertEqual(lookup("2024-11-09T00:00:00Z"), "40.00")
        self.assertEqual(lookup("2024-11-10T00:00:00Z"), "42.00")
        with self.assertRaises(ValueError):
            temporal_lookup(workers + [workers[0]], "worker", "worker-a", "2024-11-03T00:00:00Z", "2024-11-09T00:00:00Z")

    def test_effective_code_release_boundary(self):
        codes = json.loads((ROOT / "contracts/phase1/reference-fixtures.json").read_text())["codes"]
        for day, expected in (("2024-09-30", "FY2024"), ("2024-10-01", "FY2025")):
            self.assertEqual(code_at(codes, "DIAGNOSIS", "FIXTURE_DX", day, "2024-11-01T00:00:00Z")["version"], expected)
        for domain, known in (("MEDICATION", "2024-11-01T00:00:00Z"), ("DIAGNOSIS", "2024-01-01T00:00:00Z")):
            with self.subTest(domain=domain), self.assertRaises(ValueError):
                code_at(codes, domain, "FIXTURE_DX", "2024-10-01", known)

    def test_clock_order_ties_and_dynamic_feedback(self):
        clock = Clock("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")
        at = "2024-01-01T01:00:00Z"
        for key, priority in (("b", 2), ("a", 2), ("clean", 1)):
            clock.schedule(key, at, priority, {})
        self.assertEqual(clock.pop()["event_id"], "clean")
        clock.schedule("feedback", at, 0, {"capacity": 1})
        self.assertEqual([clock.pop()["event_id"] for _ in range(3)], ["feedback", "a", "b"])
        with self.assertRaises(ValueError):
            clock.schedule("past", "2024-01-01T00:00:00Z", 1, {})
        with self.assertRaises(ValueError):
            clock.schedule("b", at, 1, {})
        with self.assertRaises(ValueError):
            clock.schedule("future", "2025-01-01T00:00:00Z", 1, {})


if __name__ == "__main__":
    unittest.main()
