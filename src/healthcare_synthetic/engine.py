"""Single-writer, transactional development-fixture DAG runner."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import platform
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Context, ROUND_HALF_UP, localcontext
from importlib import metadata
from pathlib import Path

from .core import TZ_HASH, canonical, chicago, digest, ordered_rows

STAGES = {
    "identities": (),
    "clinical": ("identities",),
    "demand": ("identities", "clinical"),
    "resources": ("demand",),
    "billing": ("resources",),
    "serialization": ("identities", "billing"),
    "faults": ("serialization",),
    "validation": ("identities", "clinical", "demand", "resources", "billing", "serialization", "faults"),
}


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def single_writer(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    file = path.open("a+b")
    file.seek(0, 2)
    if file.tell() == 0:
        file.write(b"0")
        file.flush()
    file.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        file.close()
        raise RuntimeError("another process owns this run directory") from exc
    try:
        yield
    finally:
        file.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(file, fcntl.LOCK_UN)
        file.close()


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS stages (
                name TEXT PRIMARY KEY, local_hash TEXT NOT NULL, input_hash TEXT NOT NULL,
                payload TEXT NOT NULL, checksum TEXT NOT NULL, row_count INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY, started TEXT NOT NULL, finished TEXT, status TEXT NOT NULL, manifest TEXT);
            CREATE TABLE IF NOT EXISTS defects (
                defect_id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL);
        """)

    def close(self):
        self.db.close()

    def stages(self):
        rows = self.db.execute("SELECT name,local_hash,input_hash,payload,checksum,row_count FROM stages").fetchall()
        return {r[0]: {"local_hash": r[1], "input_hash": r[2], "payload": r[3], "checksum": r[4], "row_count": r[5]} for r in rows}

    def publish(self, name, local_hash, input_hash, output, *, fail=False, crash=False):
        payload = canonical(output)
        checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        count = sum(len(rows) for rows in output["tables"].values())
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO stages VALUES (?,?,?,?,?,?)", (name, local_hash, input_hash, payload, checksum, count))
            if crash:
                os._exit(97)  # Deliberate test hook: process dies with an uncommitted WAL transaction.
            if fail:
                raise RuntimeError(f"injected failure before {name} commit")
            if name == "validation":
                self.db.execute("UPDATE defects SET status='RESOLVED'")
                for defect in output["controls"]["defects"]:
                    self.db.execute("INSERT OR REPLACE INTO defects VALUES (?,?,?)", (defect["defect_id"], canonical(defect), "OPEN"))
        return checksum


def load_config(root, path):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"profile", "seed", "fixture_cap", "clock", "stages", "reference", "expectations"}
    if set(config) != required or config["profile"] != "DEVELOPMENT_FIXTURE":
        raise ValueError("only the explicit Phase 1 DEVELOPMENT_FIXTURE profile is permitted")
    if type(config["seed"]) is not int or type(config["fixture_cap"]) is not int or not 1 <= config["fixture_cap"] <= 500:
        raise ValueError("invalid seed or development fixture cap (1..500)")
    if set(config["stages"]) != set(STAGES):
        raise ValueError("configuration must declare exactly the registered stage modules")
    profile = json.loads((root / "contracts/phase1/profile-contract.json").read_text(encoding="utf-8"))
    if config["clock"] != profile["clock"]:
        raise ValueError("clock differs from frozen Phase 0 business/delivery boundaries")
    for name, fields in profile["stage_fields"].items():
        if set(config["stages"][name]) != set(fields):
            raise ValueError(f"unknown or missing configuration fields in {name}")
    # Configurations refer to immutable repository assets, never arbitrary external files.
    reference = (root / config["reference"]).resolve()
    if root.resolve() not in reference.parents or not reference.is_file():
        raise ValueError("reference must be a repository file")
    return config, json.loads(reference.read_text(encoding="utf-8"))


def locks(root, config):
    chicago()  # Verify the exact packaged zone bytes, not the host time-zone database.
    lock = json.loads((root / "contracts/phase1/runtime-lock.json").read_text(encoding="utf-8"))
    runtime = {"python": platform.python_version(), "implementation": platform.python_implementation(),
               "tzdata": metadata.version("tzdata"), "chicago_sha256": TZ_HASH}
    if runtime != lock["runtime"]:
        raise ValueError(f"runtime differs from approved lock: {runtime}")
    contract_files = sorted((root / "contracts/phase0").glob("*.json")) + sorted((root / "contracts/phase1").glob("*.json"))
    code_files = sorted((root / "src/healthcare_synthetic").glob("*.py"))
    hashes = lambda paths: {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return {"runtime": runtime, "code": hashes(code_files), "contracts": hashes(contract_files),
            "reference": hashes([root / config["reference"]]), "config_sha256": digest(config)}


def merged(outputs):
    tables = {}
    for output in outputs.values():
        for table, rows in output["tables"].items():
            if table in tables:
                raise ValueError(f"multiple stages own business projection {table}")
            tables[table] = rows
    return tables


def check_budget(tables, cap, schema):
    planned = {t["name"]: t["planned_rows"] for t in schema["tables"]}
    aliases = {"bed_interval": "bed_event"}  # Two interval fixtures exercise BD04; not a new canonical table.
    total = 0
    for table, rows in tables.items():
        target = aliases.get(table, table)
        if target not in planned or len(rows) > planned[target]:
            raise ValueError(f"budget or unregistered table {table}")
        if any(not isinstance(row, dict) or any(isinstance(v, (dict, list)) for v in row.values()) for row in rows):
            raise ValueError("nested business facts cannot escape row accounting")
        total += len(rows)
    if total > min(cap, 2_000_000):
        raise ValueError(f"business record budget exceeded: {total} > {min(cap, 2_000_000)}")
    return total


def atomic_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run(root, config_path, output_dir, *, fail_stage=None, crash_stage=None):
    # Ambient process decimal settings must not change the generated business facts.
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
        return _run(root, config_path, output_dir, fail_stage=fail_stage, crash_stage=crash_stage)


def _run(root, config_path, output_dir, *, fail_stage=None, crash_stage=None):
    from .stages import IMPLEMENTATIONS
    root, output_dir = Path(root).resolve(), Path(output_dir).resolve()
    config, reference = load_config(root, config_path)
    # This CLI creates local candidate artifacts only and refuses to write inside source/control folders.
    if root == output_dir or root in output_dir.parents and output_dir.relative_to(root).parts[0] not in ("output", "data"):
        raise ValueError("in-repository runs must be under ignored output/ or data/")
    if fail_stage not in (None, *STAGES) or crash_stage not in (None, *STAGES):
        raise ValueError("unknown failure hook stage")
    input_locks = locks(root, config)
    schema = json.loads((root / "contracts/phase0/schema.json").read_text(encoding="utf-8"))
    # Seed and temporal/reference/code changes are global. Stage assumptions stay selective.
    global_inputs = {k: v for k, v in input_locks.items() if k != "config_sha256"}
    global_inputs.update({"seed": config["seed"], "clock": config["clock"], "fixture_cap": config["fixture_cap"]})
    local_hashes = {name: digest({"global": global_inputs, "stage": config["stages"][name],
                                  "expectations": config["expectations"] if name == "validation" else None}) for name in STAGES}
    output_dir.mkdir(parents=True, exist_ok=True)
    with single_writer(output_dir / "run.lock"):
        store = Store(output_dir / "checkpoints.sqlite3")
        manifest = {"profile": config["profile"], "started_at": now(), "status": "RUNNING", "locks": input_locks,
                    "executed": [], "reused": [], "invalidated": [], "dataset_accepted": False,
                    "solution_status": "BLOCKED_FOR_SOLUTION"}
        attempt = None
        try:
            # A crash or failed reconfiguration cannot leave a previous passing export looking current.
            atomic_json(output_dir / "manifest.json", manifest)
            for leaf in ("fixture-tables.json", "validation.json"):
                (output_dir / leaf).unlink(missing_ok=True)
            existing = store.stages()
            # Inspect all checksums before considering any cache hit.
            for name, checkpoint in existing.items():
                if name not in STAGES or hashlib.sha256(checkpoint["payload"].encode("utf-8")).hexdigest() != checkpoint["checksum"]:
                    raise ValueError(f"checkpoint corruption: {name}; preserve directory for investigation and rebuild in a new directory")
            invalid = {n for n in existing if existing[n]["local_hash"] != local_hashes[n]}
            for name, parents in STAGES.items():
                if any(parent in invalid for parent in parents):
                    invalid.add(name)
            # Invalidate before recomputation, including if the changed upstream stage fails.
            with store.db:
                for name in invalid:
                    store.db.execute("DELETE FROM stages WHERE name=?", (name,))
                store.db.execute("UPDATE attempts SET status='INTERRUPTED',finished=? WHERE status='RUNNING'", (now(),))
                attempt = store.db.execute("INSERT INTO attempts(started,status) VALUES (?,?)", (manifest["started_at"], "RUNNING")).lastrowid
            manifest["invalidated"] = sorted(invalid)
            outputs, checksums = {}, {}
            for name, parents in STAGES.items():
                input_hash = digest({"local": local_hashes[name], "parents": {p: checksums[p] for p in parents}})
                checkpoint = existing.get(name) if name not in invalid else None
                if checkpoint and checkpoint["input_hash"] == input_hash:
                    output = json.loads(checkpoint["payload"])
                    manifest["reused"].append(name)
                    checksums[name] = checkpoint["checksum"]
                else:
                    output = IMPLEMENTATIONS[name](copy.deepcopy(config), copy.deepcopy(reference), copy.deepcopy({p: outputs[p] for p in parents}))
                    if set(output) != {"tables", "controls"}:
                        raise ValueError(f"stage {name} returned an undeclared artifact")
                    output["tables"] = {t: ordered_rows(rows) for t, rows in output["tables"].items()}
                    check_budget(merged({**outputs, name: output}), config["fixture_cap"], schema)
                    checksums[name] = store.publish(name, local_hashes[name], input_hash, output,
                                                    fail=name == fail_stage, crash=name == crash_stage)
                    manifest["executed"].append(name)
                outputs[name] = output
                check_budget(merged(outputs), config["fixture_cap"], schema)
            tables = merged(outputs)
            control = outputs["validation"]["controls"]
            manifest.update({"status": control["gate"]["status"], "gate": control["gate"],
                             "business_sha256": digest({t: ordered_rows(r) for t, r in tables.items()}),
                             "stage_checksums": checksums, "business_rows": sum(map(len, tables.values())),
                             "business_rows_by_projection": {t: len(r) for t, r in tables.items()},
                             "serialized_mirror_rows": outputs["serialization"]["controls"]["physical_rows"],
                             "serialized_mirror_bytes": outputs["serialization"]["controls"]["physical_bytes"],
                             "release_business_table_count": 25, "fixture_projection_count": len(tables),
                             "fixture_cap": config["fixture_cap"]})
            atomic_json(output_dir / "fixture-tables.json", tables)
            atomic_json(output_dir / "validation.json", control)
        except Exception as exc:
            manifest.update({"status": "FAILED", "failure": {"type": type(exc).__name__, "reason": str(exc)}})
            raise
        finally:
            manifest["finished_at"] = now()
            if attempt is not None:
                with store.db:
                    store.db.execute("UPDATE attempts SET status=?,finished=?,manifest=? WHERE id=?",
                                     (manifest["status"], manifest["finished_at"], canonical(manifest), attempt))
            atomic_json(output_dir / "manifest.json", manifest)
            store.close()
        return manifest
