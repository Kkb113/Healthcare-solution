"""Transactional master-data generation profile on the tested framework primitives."""
from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from decimal import Context, ROUND_HALF_UP, localcontext
from importlib import metadata
from pathlib import Path

from .core import TZ_HASH, canonical, chicago, digest
from .engine import Store, atomic_json, check_budget, single_writer
from .master_generation import MASTER_STAGES, MasterGenerator
from .master_review import render_review, review_gate
from .master_validation import MasterValidator

ROOT = Path(__file__).resolve().parents[2]
GRAPH = {**MASTER_STAGES, "validation": tuple(MASTER_STAGES)}
CONFIG_KEYS = {"organizations": ["organization"], "catalog": [], "patients": ["population"],
               "workforce": ["workforce", "population"], "payers": ["coverage"], "coverage": ["coverage"],
               "security": ["security"], "mappings": ["mapping"], "opening_health": ["opening_health"], "validation": ["review", "budgets", "population", "workforce", "coverage", "opening_health", "window"]}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_inputs(config_path):
    cfg = read(config_path)
    policy = read(ROOT / "contracts/master-data-policy.json")
    schema = read(ROOT / "contracts/phase0/schema.json")
    baseline = read(ROOT / "contracts/phase0/baseline.json")
    if cfg.get("profile") != "MASTER_FOUNDATION" or cfg.get("budgets") != policy["exact_budgets"] or sum(cfg["budgets"].values()) != policy["expected_rows"]:
        raise ValueError("unapproved master profile or row budget")
    if type(cfg["seed"]) is not int or cfg["population"]["patients"] != 20000 or cfg["population"]["workers"] != 300:
        raise ValueError("master cohort differs from frozen adult baseline")
    if cfg["window"] != {"start": baseline["business_start_date"], "end_inclusive": baseline["business_end_date_inclusive"], "timezone": baseline["local_timezone"], "delivery_grace_end": baseline["final_export_grace_end_utc"]}:
        raise ValueError("master business/delivery window differs from frozen baseline")
    chicago()
    runtime = {"python": platform.python_version(), "implementation": platform.python_implementation(), "tzdata": metadata.version("tzdata"), "chicago_sha256": TZ_HASH}
    if runtime != read(ROOT / cfg["references"]["runtime"])["runtime"]:
        raise ValueError("master runtime lock differs")
    references = {}
    package_lock = read(ROOT / "contracts/reference-package-lock.json")
    for relative, expected in package_lock["files"].items():
        content = (ROOT / relative).read_bytes()
        if len(content) != expected["bytes"] or hashlib.sha256(content).hexdigest() != expected["sha256"]:
            raise ValueError("reference package hash mismatch: " + relative)
    for key, path in cfg["references"].items():
        absolute = (ROOT / path).resolve()
        if ROOT not in absolute.parents or not absolute.is_file():
            raise ValueError("reference must be a versioned repository file")
        references[key] = read(absolute)
    references = {"names": references["names"], "codes": references["clinical_codes"], "local": references["local_catalog"]}
    return cfg, policy, schema, references, runtime


def input_locks(cfg, runtime):
    paths = sorted((ROOT / "src/healthcare_synthetic").glob("*.py"))
    paths += [ROOT / "contracts/master-data-policy.json", ROOT / "contracts/reference-package-lock.json", ROOT / "contracts/phase1/runtime-lock.json"]
    paths += sorted((ROOT / "contracts/phase0").glob("*.json"))
    paths += [ROOT / cfg["references"][key] for key in ("names", "clinical_codes", "local_catalog")]
    return {"files": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            "runtime": runtime, "configuration_sha256": digest(cfg)}


def merge(outputs):
    tables = {}
    for output in outputs.values():
        for name, rows in output["tables"].items():
            if name in tables:
                raise ValueError("multiple master stage owners")
            tables[name] = rows
    return tables


def run_master(config_path=ROOT / "config/master-data-generation.json", output_dir=ROOT / "output/master-foundation", *, fail_stage=None, crash_stage=None, review_path=ROOT / "reviews/master-data-realism-review.json"):
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
        return _run(config_path, Path(output_dir).resolve(), fail_stage, crash_stage, Path(review_path))


def _run(config_path, output_dir, fail_stage, crash_stage, review_path):
    cfg, policy, schema, references, runtime = load_inputs(config_path)
    if ROOT not in output_dir.parents or output_dir.relative_to(ROOT).parts[0] not in ("output", "data"):
        raise ValueError("master candidate must be under ignored workspace output/ or data/")
    if fail_stage not in (None, *GRAPH) or crash_stage not in (None, *GRAPH):
        raise ValueError("unknown master failure hook")
    locks = input_locks(cfg, runtime)
    review = read(review_path) if review_path.exists() else None
    global_lock = {"files": locks["files"], "runtime": runtime, "seed": cfg["seed"]}
    local = {stage: digest({"global": global_lock, "config": {key: cfg[key] for key in CONFIG_KEYS[stage]},
                            "review": review if stage == "validation" else None}) for stage in GRAPH}
    output_dir.mkdir(parents=True, exist_ok=True)
    with single_writer(output_dir / "run.lock"):
        prior = read(output_dir / "manifest.json") if (output_dir / "manifest.json").exists() else None
        if prior and prior.get("profile") != "MASTER_FOUNDATION":
            raise ValueError("run directory belongs to another profile")
        manifest = {"profile": cfg["profile"], "implementation_phase": 2, "started_at": datetime.now(timezone.utc).isoformat(),
                    "status": "RUNNING", "locks": locks, "executed": [], "reused": [], "invalidated": [],
                    "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}
        atomic_json(output_dir / "manifest.json", manifest)
        # A new run cannot expose old exported business artifacts as current.
        for leaf in ("validation-report.json", "identity-review-sample.md", "candidate-ready.json"):
            (output_dir / leaf).unlink(missing_ok=True)
        store = Store(output_dir / "checkpoints.sqlite3")
        attempt = None
        try:
            existing = store.stages()
            for name, row in existing.items():
                if name not in GRAPH or hashlib.sha256(row["payload"].encode()).hexdigest() != row["checksum"]:
                    raise ValueError(f"master checkpoint corruption: {name}; rebuild in a new directory")
            invalid = {name for name, row in existing.items() if row["local_hash"] != local[name]}
            for name, parents in GRAPH.items():
                if set(parents) & invalid:
                    invalid.add(name)
            with store.db:
                for name in invalid:
                    store.db.execute("DELETE FROM stages WHERE name=?", (name,))
                store.db.execute("UPDATE attempts SET status='INTERRUPTED' WHERE status='RUNNING'")
                attempt = store.db.execute("INSERT INTO attempts(started,status) VALUES (?,?)", (manifest["started_at"], "RUNNING")).lastrowid
            manifest["invalidated"] = sorted(invalid)
            outputs, hashes = {}, {}
            for name, parents in GRAPH.items():
                fingerprint = digest({"local": local[name], "parents": {p: hashes[p] for p in parents}})
                cached = existing.get(name) if name not in invalid else None
                if cached and cached["input_hash"] == fingerprint:
                    output = json.loads(cached["payload"])
                    hashes[name] = cached["checksum"]
                    manifest["reused"].append(name)
                else:
                    if name == "validation":
                        tables = merge(outputs)
                        validation = MasterValidator(tables, schema, cfg, policy, references).run()
                        _, selection = render_review(tables, cfg)
                        reviewed = review_gate(selection, review)
                        validation["review"] = reviewed
                        validation["review_selection"] = selection
                        status = "MASTER_FOUNDATION_PASSED" if validation["status"] == "MASTER_CHECKS_PASSED" and reviewed["status"] == "PASS" else ("REVIEW_PENDING" if validation["status"] == "MASTER_CHECKS_PASSED" else "BLOCKED")
                        validation["gate_status"] = status
                        output = {"tables": {}, "controls": validation}
                    else:
                        generator = MasterGenerator(cfg, references, "master-" + fingerprint[:24])
                        tables = getattr(generator, name)({p: outputs[p]["tables"] for p in parents})
                        for table, rows in tables.items():
                            primary = next(t["primary_key"][0] for t in schema["tables"] if t["name"] == table)
                            rows.sort(key=lambda r: r[primary])
                        output = {"tables": tables, "controls": {"generation_id": generator.run_id}}
                    check_budget(merge({**outputs, name: output}), policy["expected_rows"], schema)
                    hashes[name] = store.publish(name, local[name], fingerprint, output, fail=name == fail_stage, crash=name == crash_stage)
                    manifest["executed"].append(name)
                outputs[name] = output
            tables, control = merge(outputs), outputs["validation"]["controls"]
            total = check_budget(tables, policy["expected_rows"], schema)
            files = {}
            data_dir = output_dir / "canonical"
            data_dir.mkdir(exist_ok=True)
            for table, rows in tables.items():
                path = data_dir / (table.replace("_", "-") + ".jsonl")
                temp = path.with_suffix(".tmp")
                hasher, size = hashlib.sha256(), 0
                with temp.open("wb") as stream:
                    for row in rows:
                        line = (canonical(row) + "\n").encode()
                        stream.write(line)
                        hasher.update(line)
                        size += len(line)
                temp.replace(path)
                files[table] = {"file": path.relative_to(output_dir).as_posix(), "sha256": hasher.hexdigest(), "bytes": size, "rows": len(rows)}
            body, selection = render_review(tables, cfg)
            (output_dir / "identity-review-sample.md").write_text(body, encoding="utf-8", newline="\n")
            atomic_json(output_dir / "validation-report.json", control)
            manifest.update({"status": control["gate_status"], "business_sha256": digest({t: files[t]["sha256"] for t in sorted(files)}),
                             "business_rows": total, "rows_by_table": {t: len(rows) for t, rows in tables.items()}, "canonical_files": files,
                             "stage_checksums": hashes, "release_business_tables": 25, "generated_business_tables": len(tables),
                             "remaining_planned_rows": 1958210 - total, "review_mirror_rows": selection["mirror_rows"],
                             "review_mirror_bytes": selection["mirror_bytes"], "checkpoint_mirror_rows": total,
                             "physical_serialized_rows": total * 2 + selection["mirror_rows"],
                             "next_phase": "Longitudinal clinical histories - not started"})
            if manifest["status"] == "MASTER_FOUNDATION_PASSED":
                atomic_json(output_dir / "candidate-ready.json", {"master_status": manifest["status"], "business_sha256": manifest["business_sha256"], "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"})
        except Exception as exc:
            manifest.update({"status": "FAILED", "error": str(exc)})
            raise
        finally:
            manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
            if attempt is not None:
                with store.db:
                    store.db.execute("UPDATE attempts SET status=?,finished=?,manifest=? WHERE id=?", (manifest["status"], manifest["finished_at"], canonical(manifest), attempt))
            atomic_json(output_dir / "manifest.json", manifest)
            store.close()
        return manifest
