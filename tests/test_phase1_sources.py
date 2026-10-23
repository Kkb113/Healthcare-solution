import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from healthcare_synthetic.core import canonical, digest
from healthcare_synthetic.sources import Replay, parse, recovery_exercises, serialize


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.schema = {"key": "string", "amount": "decimal", "target": "string"}
        self.envelope = serialize("AXIOM", "C1/2024-01", "v1", "2024-02-05T08:00:00Z",
                                  [{"key": "a1", "amount": "100.00", "target": "C1"}], self.schema)
        self.replay = Replay({"AXIOM": self.schema})
        self.as_of = "2024-02-07T00:00:00Z"

    def refresh_bytes(self, envelope):
        m = envelope["manifest"]
        m["bytes"] = len(envelope["payload"].encode("utf-8"))
        m["sha256"] = hashlib.sha256(envelope["payload"].encode("utf-8")).hexdigest()
        m.pop("file_id")
        m["file_id"] = digest(m)
        return envelope

    def test_all_seven_source_recovery_behaviors(self):
        results = recovery_exercises()
        self.assertEqual({r["fault_id"] for r in results}, {"F_DUP", "F_LATE", "F_MISSING", "F_SCHEMA", "F_UNMAPPED", "F_REPLACE", "F_CORRUPT"})
        self.assertTrue(all(r["status"] == "PASS" for r in results))

    def test_csv_roundtrip_unicode_quotes_and_newlines(self):
        row = {"key": "a1", "amount": "100.00", "target": 'José, "Chen"\nUnit A'}
        envelope = serialize("AXIOM", "C1", "v1", "2024-02-01T00:00:00Z", [row], self.schema)
        # Round trip still works after canonical manifest serialization reorders keys.
        self.assertEqual(parse(json.loads(canonical(envelope)), self.schema), [row])

    def test_replayed_file_has_no_economic_effect(self):
        self.assertEqual(self.replay.ingest(self.envelope, self.as_of, {"C1"}), "APPLIED")
        self.assertEqual(self.replay.ingest(self.envelope, self.as_of, {"C1"}), "DUPLICATE")
        self.assertEqual(len(self.replay.files), 1)
        self.assertEqual(self.replay.snapshot("AXIOM", "C1/2024-01", self.as_of)[0]["amount"], "100.00")

    def test_replacement_scope_and_history(self):
        self.replay.ingest(self.envelope, self.as_of)
        replacement = serialize("AXIOM", "C1/2024-01", "v2", "2024-02-06T08:00:00Z",
                                [{"key": "a2", "amount": "90.00", "target": "C1"}], self.schema,
                                replacement_of=self.envelope["manifest"]["file_id"])
        self.replay.ingest(replacement, self.as_of)
        self.assertEqual(self.replay.snapshot("AXIOM", "C1/2024-01", self.as_of)[0]["amount"], "90.00")
        self.assertEqual(self.replay.snapshot("AXIOM", "C1/2024-01", "2024-02-05T09:00:00Z")[0]["amount"], "100.00")
        bad_scope = serialize("AXIOM", "C2/2024-01", "v2", "2024-02-06T08:00:00Z", [{"key": "a2", "amount": "90", "target": "C2"}], self.schema, replacement_of=self.envelope["manifest"]["file_id"])
        with self.assertRaisesRegex(ValueError, "crosses declared scope"):
            self.replay.ingest(bad_scope, self.as_of)

    def test_implicit_replacement_and_branched_vintages_rejected(self):
        self.replay.ingest(self.envelope, self.as_of)
        b = serialize("AXIOM", "C1/2024-01", "v2", "2024-02-06T08:00:00Z", [{"key": "a2", "amount": "90", "target": "C1"}], self.schema)
        with self.assertRaisesRegex(ValueError, "explicit replacement"):
            self.replay.ingest(b, self.as_of)
        b = serialize("AXIOM", "C1/2024-01", "v2", "2024-02-06T08:00:00Z", [{"key": "a2", "amount": "90", "target": "C1"}], self.schema, replacement_of=self.envelope["manifest"]["file_id"])
        self.replay.ingest(b, self.as_of)
        c = serialize("AXIOM", "C1/2024-01", "v3", "2024-02-07T00:00:00Z", [{"key": "a3", "amount": "80", "target": "C1"}], self.schema, replacement_of=self.envelope["manifest"]["file_id"])
        with self.assertRaisesRegex(ValueError, "branched"):
            self.replay.ingest(c, self.as_of)

    def test_missing_partition_is_never_zero(self):
        with self.assertRaisesRegex(ValueError, "F_MISSING"):
            self.replay.certify([("AXIOM", "C1/2024-01")], self.as_of)

    def test_not_yet_available_delivery_rejected(self):
        with self.assertRaisesRegex(ValueError, "not available"):
            self.replay.ingest(self.envelope, "2024-02-04T00:00:00Z")
        self.assertFalse(self.replay.files)

    def test_bad_row_is_atomic_and_repair_restores_certification(self):
        corrupt = copy.deepcopy(self.envelope)
        corrupt["payload"] += "BROKEN"
        with self.assertRaisesRegex(ValueError, "F_CORRUPT"):
            self.replay.ingest(corrupt, self.as_of)
        self.assertFalse(self.replay.files)
        with self.assertRaisesRegex(ValueError, "quarantined"):
            self.replay.certify([], self.as_of)
        self.replay.recover(self.envelope, self.as_of, corrupt["manifest"]["file_id"], {"C1"})
        self.assertEqual(self.replay.certify([("AXIOM", "C1/2024-01")], self.as_of), "COMPLETE")
        self.assertEqual(self.replay.quarantine[0]["status"], "RESOLVED")

    def test_schema_and_unmapped_quarantine_does_not_partially_apply(self):
        bad = copy.deepcopy(self.envelope)
        bad["manifest"]["schema_version"] = "unapproved"
        with self.assertRaisesRegex(ValueError, "F_SCHEMA"):
            self.replay.ingest(bad, self.as_of)
        with self.assertRaisesRegex(ValueError, "F_UNMAPPED.*a1"):
            self.replay.ingest(self.envelope, self.as_of, {"C9"})
        self.assertFalse(self.replay.files)
        self.assertEqual(len(self.replay.quarantine), 2)

    def test_exact_decimal_and_row_control_checks(self):
        for field, value in (("amount_total", "101"), ("expected_rows", 2)):
            bad = copy.deepcopy(self.envelope)
            bad["manifest"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                parse(bad, self.schema)
        bad = copy.deepcopy(self.envelope)
        bad["payload"] = bad["payload"].replace("100.00", "NaN")
        self.refresh_bytes(bad)
        with self.assertRaisesRegex(ValueError, "row 1 key a1.*nonfinite"):
            parse(bad, self.schema)

    def test_duplicate_version_inside_file_and_conflicting_message(self):
        row = {"key": "a1", "amount": "100.00", "target": "C1"}
        bad = serialize("AXIOM", "C1", "v1", "2024-02-01T00:00:00Z", [row, row], self.schema)
        with self.assertRaisesRegex(ValueError, "duplicate version"):
            parse(bad, self.schema)
        schema = {"key": "string", "effective": "timestamp", "sequence": "int", "corrects": "string", "occupant": "string"}
        replay = Replay({"ADT": schema})
        row = {"key": "m1", "effective": "2024-01-01T00:00:00Z", "sequence": 1, "corrects": "NONE", "occupant": "P1"}
        first = serialize("ADT", "B1", "v1", "2024-01-01T00:00:00Z", [row], schema)
        second = serialize("ADT", "B1", "v2", "2024-01-01T01:00:00Z", [{**row, "occupant": "P2"}], schema)
        replay.ingest(first, self.as_of)
        with self.assertRaisesRegex(ValueError, "conflicting immutable event"):
            replay.ingest(second, self.as_of)

    def test_correction_cycles_and_missing_predecessors_fail(self):
        schema = {"key": "string", "effective": "timestamp", "sequence": "int", "corrects": "string", "occupant": "string"}
        for rows, reason in (([{"key": "m1", "effective": "2024-01-01T00:00:00Z", "sequence": 1, "corrects": "m2", "occupant": "P1"}], "predecessor"),
                             ([{"key": "m1", "effective": "2024-01-01T00:00:00Z", "sequence": 1, "corrects": "m2", "occupant": "P1"}, {"key": "m2", "effective": "2024-01-01T00:00:00Z", "sequence": 1, "corrects": "m1", "occupant": "P2"}], "cycle")):
            replay = Replay({"ADT": schema})
            envelope = serialize("ADT", "B1", "v1", "2024-01-01T01:00:00Z", rows, schema)
            replay.ingest(envelope, self.as_of)
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                replay.events("ADT", "B1", self.as_of)
            with self.subTest(certification=reason), self.assertRaisesRegex(ValueError, reason):
                replay.certify([("ADT", "B1")], self.as_of)


if __name__ == "__main__":
    unittest.main()
