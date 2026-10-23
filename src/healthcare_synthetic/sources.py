"""Bounded source-format simulator, not a live connector or Medallion pipeline."""
from __future__ import annotations

import csv
import hashlib
import io
from decimal import Decimal

from .core import canonical, digest, instant, ordered_rows


def serialize(source, scope, vintage, available_at, rows, schema, *, replacement_of=None):
    """Explicit scalar projection with row/byte checksums and exact control total."""
    if not rows or any(set(r) != set(schema) for r in rows):
        raise ValueError("source projection must match declared schema")
    instant(available_at)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=sorted(schema), lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(ordered_rows(rows))
    payload = buffer.getvalue()
    control = sum((Decimal(r.get("amount", "0")) for r in rows), Decimal(0))
    manifest = {"source": source, "scope": scope, "vintage": vintage, "replacement_of": replacement_of,
                "available_at": available_at, "schema_version": "phase1-projection-1", "schema": schema,
                "expected_rows": len(rows), "amount_total": format(control, "f"),
                "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(), "bytes": len(payload.encode("utf-8"))}
    manifest["file_id"] = digest(manifest)
    return {"manifest": manifest, "payload": payload}


def parse(envelope, approved_schema):
    manifest, payload = envelope["manifest"], envelope["payload"]
    if manifest["schema_version"] != "phase1-projection-1" or manifest["schema"] != approved_schema:
        raise ValueError("F_SCHEMA: incompatible source contract")
    if hashlib.sha256(payload.encode("utf-8")).hexdigest() != manifest["sha256"] or len(payload.encode("utf-8")) != manifest["bytes"]:
        raise ValueError("F_CORRUPT: file checksum/byte length")
    reader = csv.DictReader(io.StringIO(payload, newline=""))
    if reader.fieldnames != sorted(approved_schema):
        raise ValueError("F_SCHEMA: field layout mismatch")
    rows = []
    for ordinal, row in enumerate(reader, 1):
        try:
            if set(row) != set(approved_schema) or any(v is None for v in row.values()):
                raise ValueError("wrong field count")
            parsed = {}
            for key, kind in approved_schema.items():
                value = row[key]
                if kind == "int":
                    parsed[key] = int(value)
                elif kind == "decimal":
                    amount = Decimal(value)
                    if not amount.is_finite():
                        raise ValueError("nonfinite decimal")
                    parsed[key] = format(amount, "f")
                elif kind == "timestamp":
                    instant(value)
                    parsed[key] = value
                elif kind == "string":
                    if not value:
                        raise ValueError("empty required source scalar")
                    parsed[key] = value
                else:
                    raise ValueError("unregistered scalar type")
            rows.append(parsed)
        except Exception as exc:
            raise ValueError(f"F_CORRUPT: row {ordinal} key {row.get('key', 'UNKNOWN')}: {exc}") from exc
    if len(rows) != manifest["expected_rows"]:
        raise ValueError("F_MISSING: row count mismatch")
    total = sum((Decimal(r.get("amount", "0")) for r in rows), Decimal(0))
    if total != Decimal(manifest["amount_total"]):
        raise ValueError("F_CORRUPT: amount control total")
    keys = [r["key"] for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("F_CORRUPT: duplicate version keys inside file")
    return rows


class Replay:
    """Knowledge-preserving snapshots, exact deliveries, and effective event projection.

    All changes are staged in memory and committed only after the entire file
    validates. Durable stage publication is provided by engine.Store.
    """
    def __init__(self, schemas):
        self.schemas = schemas
        self.files = {}
        self.quarantine = []

    def ingest(self, envelope, as_of, typed_targets=None):
        m = envelope["manifest"]
        if instant(m["available_at"]) > instant(as_of):
            raise ValueError("source not available as of requested knowledge")
        try:
            rows = parse(envelope, self.schemas[m["source"]])
            if typed_targets is not None:
                for row in rows:
                    if row.get("target") not in typed_targets:
                        raise ValueError(f"F_UNMAPPED: {row['key']} target {row.get('target')}")
            if m["file_id"] in self.files:
                if canonical(self.files[m["file_id"]]["manifest"]) != canonical(m):
                    raise ValueError("F_CORRUPT: conflicting file ID")
                return "DUPLICATE"
            replacement = m["replacement_of"]
            prior_scope = [f for f in self.files.values() if (f["manifest"]["source"], f["manifest"]["scope"]) == (m["source"], m["scope"])]
            if m["source"] == "AXIOM" and prior_scope and not replacement:
                raise ValueError("F_SCHEMA: revised Axiom scope requires explicit replacement lineage")
            if replacement:
                if replacement not in self.files:
                    raise ValueError("F_MISSING: replacement predecessor not delivered")
                prior = self.files[replacement]["manifest"]
                if (prior["source"], prior["scope"]) != (m["source"], m["scope"]):
                    raise ValueError("F_SCHEMA: replacement crosses declared scope")
                if instant(m["available_at"]) <= instant(prior["available_at"]):
                    raise ValueError("F_SCHEMA: replacement knowledge must advance")
                if any(f["manifest"]["replacement_of"] == replacement for f in self.files.values()):
                    raise ValueError("F_SCHEMA: branched replacement chain")
            # Event IDs identify immutable effective post-state messages across files.
            existing = {r["key"]: r for f in self.files.values() if f["manifest"]["source"] == m["source"]
                        and m["source"] == "ADT" for r in f["rows"]}
            for row in rows:
                if row["key"] in existing and row != existing[row["key"]]:
                    raise ValueError(f"F_CORRUPT: conflicting immutable event {row['key']}")
            self.files[m["file_id"]] = {"manifest": dict(m), "rows": rows}
            return "APPLIED"
        except Exception as exc:
            self.quarantine.append({"file_id": m["file_id"], "reason": str(exc), "status": "QUARANTINED"})
            raise

    def snapshot(self, source, scope, as_of):
        candidates = [f for f in self.files.values() if f["manifest"]["source"] == source
                      and f["manifest"]["scope"] == scope and instant(f["manifest"]["available_at"]) <= instant(as_of)]
        if not candidates:
            raise ValueError("F_MISSING: requested source partition incomplete")
        selected = max(candidates, key=lambda f: (instant(f["manifest"]["available_at"]), f["manifest"]["file_id"]))
        return ordered_rows(selected["rows"])

    def events(self, source, scope, as_of):
        versions = {}
        for file in self.files.values():
            m = file["manifest"]
            if m["source"] == source and m["scope"] == scope and instant(m["available_at"]) <= instant(as_of):
                for row in file["rows"]:
                    if instant(row["effective"]) <= instant(as_of):
                        versions[row["key"]] = row
        corrected = {r["corrects"] for r in versions.values() if r["corrects"] != "NONE"}
        for row in versions.values():
            if row["corrects"] != "NONE" and row["corrects"] not in versions:
                raise ValueError("F_MISSING: correction predecessor missing")
        live = [r for key, r in versions.items() if key not in corrected]
        # Cycle detection: a closed correction cycle must not erase all history.
        for row in versions.values():
            seen, cursor = set(), row
            while cursor["corrects"] != "NONE":
                if cursor["key"] in seen:
                    raise ValueError("F_CORRUPT: correction cycle")
                seen.add(cursor["key"])
                cursor = versions[cursor["corrects"]]
        return sorted(live, key=lambda r: (instant(r["effective"]), r["sequence"], r["key"]))

    def certify(self, required_partitions, as_of):
        if any(q["status"] == "QUARANTINED" for q in self.quarantine):
            raise ValueError("uncorrected quarantined delivery blocks source certification")
        for source, scope in required_partitions:
            self.snapshot(source, scope, as_of)
            if source == "ADT":
                self.events(source, scope, as_of)
        return "COMPLETE"

    def recover(self, envelope, as_of, repairs_file_id, typed_targets=None):
        pending = [q for q in self.quarantine if q["file_id"] == repairs_file_id and q["status"] == "QUARANTINED"]
        if not pending:
            raise ValueError("no quarantined delivery to repair")
        disposition = self.ingest(envelope, as_of, typed_targets)
        for defect in pending:
            defect.update({"status": "RESOLVED", "repaired_by": envelope["manifest"]["file_id"]})
        return disposition


def recovery_exercises():
    """Return reproducible evidence from real serializer/replay operations."""
    schema = {"key": "string", "amount": "decimal", "target": "string"}
    a = serialize("AXIOM", "2024-01/C1", "v1", "2024-02-05T08:00:00Z",
                  [{"key": "a1", "amount": "100.00", "target": "C1"}], schema)
    b = serialize("AXIOM", "2024-01/C1", "v2", "2024-02-06T08:00:00Z",
                  [{"key": "a2", "amount": "90.00", "target": "C1"}], schema, replacement_of=a["manifest"]["file_id"])
    replay = Replay({"AXIOM": schema})
    replay.ingest(a, "2024-02-05T09:00:00Z", {"C1"})
    original = replay.snapshot("AXIOM", "2024-01/C1", "2024-02-05T09:00:00Z")
    duplicate = replay.ingest(a, "2024-02-05T09:00:00Z", {"C1"})
    replay.ingest(b, "2024-02-06T09:00:00Z", {"C1"})
    current = replay.snapshot("AXIOM", "2024-01/C1", "2024-02-06T09:00:00Z")
    if duplicate != "DUPLICATE" or current[0]["amount"] != "90.00" or replay.snapshot("AXIOM", "2024-01/C1", "2024-02-05T09:00:00Z") != original:
        raise ValueError("source replay/replacement did not preserve history")
    outcomes = [{"fault_id": "F_DUP", "status": "PASS", "observed": "exact delivery deduplicated"},
                {"fault_id": "F_REPLACE", "status": "PASS", "observed": "90 current; 100 historical; no 190 total"}]

    def rejected(fault, action):
        try:
            action()
        except (ValueError, KeyError) as exc:
            if fault not in str(exc):
                raise AssertionError(f"wrong detector for {fault}: {exc}") from exc
            outcomes.append({"fault_id": fault, "status": "PASS", "observed": str(exc)})
        else:
            raise AssertionError(f"missed {fault}")
    import copy
    rejected("F_MISSING", lambda: replay.snapshot("AXIOM", "2024-02/C1", "2024-03-01T00:00:00Z"))
    bad = copy.deepcopy(a)
    bad["manifest"]["schema_version"] = "unapproved"
    rejected("F_SCHEMA", lambda: replay.ingest(bad, "2024-02-07T00:00:00Z"))
    unmapped = serialize("AXIOM", "2024-02/C2", "v1", "2024-03-05T08:00:00Z",
                         [{"key": "u1", "amount": "5.00", "target": "C2"}], schema)
    rejected("F_UNMAPPED", lambda: replay.ingest(unmapped, "2024-03-06T00:00:00Z", {"C1"}))
    corrupt = copy.deepcopy(a)
    corrupt["payload"] += "BROKEN"
    rejected("F_CORRUPT", lambda: replay.ingest(corrupt, "2024-02-07T00:00:00Z"))
    event_schema = {"key": "string", "effective": "timestamp", "sequence": "int", "corrects": "string", "occupant": "string"}
    event_replay = Replay({"ADT": event_schema})
    late = serialize("ADT", "BED_A", "m1", "2024-01-01T10:30:00Z", [{"key": "m1", "effective": "2024-01-01T10:00:00Z", "sequence": 1, "corrects": "NONE", "occupant": "P1"}], event_schema)
    newer = serialize("ADT", "BED_A", "m2", "2024-01-01T10:20:00Z", [{"key": "m2", "effective": "2024-01-01T10:10:00Z", "sequence": 2, "corrects": "NONE", "occupant": "EMPTY"}], event_schema)
    correction = serialize("ADT", "BED_A", "m3", "2024-01-01T10:40:00Z", [{"key": "m3", "effective": "2024-01-01T10:00:00Z", "sequence": 1, "corrects": "m1", "occupant": "P2"}], event_schema)
    event_replay.ingest(newer, "2024-01-01T11:00:00Z")
    event_replay.ingest(late, "2024-01-01T11:00:00Z")
    event_replay.ingest(correction, "2024-01-01T11:00:00Z")
    projected = event_replay.events("ADT", "BED_A", "2024-01-01T11:00:00Z")
    if [r["key"] for r in projected] != ["m3", "m2"] or projected[-1]["occupant"] != "EMPTY":
        raise AssertionError("out-of-order correction failed effective projection")
    if len(event_replay.events("ADT", "BED_A", "2024-01-01T10:25:00Z")) != 1:
        raise AssertionError("late event leaked before available time")
    outcomes.append({"fault_id": "F_LATE", "status": "PASS", "observed": "effective order/correction converges; historical availability preserved"})
    return sorted(outcomes, key=lambda r: r["fault_id"])
