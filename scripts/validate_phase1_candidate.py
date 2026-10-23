"""Read-only independent validator for Phase 1 scalar fixture artifacts.

Does not import generation, orchestration, source parsing or generation arithmetic.
This command can never accept the full healthcare dataset.
"""
import argparse
import hashlib
import json
import platform
import sqlite3
import sys
from pathlib import Path
from importlib import metadata, resources

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from healthcare_synthetic.validation import defects, gate, profile, reconcile_candidate, validate_candidate, validate_exports


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def inspect(run_dir, config_path):
    manifest_path = run_dir / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if manifest["profile"] != "DEVELOPMENT_FIXTURE" or manifest["status"] not in ("FIXTURES_PASSED", "BLOCKED"):
        raise ValueError("run incomplete/failed or wrong validation profile")
    if hashlib.sha256(encoded(config)).hexdigest() != manifest["locks"]["config_sha256"]:
        raise ValueError("configuration differs from manifest")
    zone_bytes = resources.files("tzdata").joinpath("zoneinfo/America/Chicago").read_bytes()
    runtime = {"python": platform.python_version(), "implementation": platform.python_implementation(),
               "tzdata": metadata.version("tzdata"), "chicago_sha256": hashlib.sha256(zone_bytes).hexdigest()}
    if runtime != manifest["locks"]["runtime"]:
        raise ValueError("independent inspection runtime differs from approved manifest")
    for kind in ("code", "contracts", "reference"):
        for relative, expected_hash in manifest["locks"][kind].items():
            path = (ROOT / relative).resolve()
            if ROOT not in path.parents or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                raise ValueError(f"input lock mismatch: {relative}")
    tables = json.loads((run_dir / "fixture-tables.json").read_text(encoding="utf-8"))
    normalized = {t: sorted(rows, key=lambda r: encoded(r)) for t, rows in tables.items()}
    if hashlib.sha256(encoded(normalized)).hexdigest() != manifest["business_sha256"]:
        raise ValueError("business artifact checksum mismatch")
    if sum(len(rows) for rows in tables.values()) != manifest["business_rows"]:
        raise ValueError("business artifact row count mismatch")
    connection = sqlite3.connect("file:" + (run_dir / "checkpoints.sqlite3").as_posix() + "?mode=ro", uri=True)
    try:
        checkpoints = {r[0]: (r[1], r[2]) for r in connection.execute("SELECT name,payload,checksum FROM stages")}
    finally:
        connection.close()
    if set(checkpoints) != set(manifest["stage_checksums"]):
        raise ValueError("checkpoint inventory differs from manifest")
    for stage, (payload, checksum) in checkpoints.items():
        if hashlib.sha256(payload.encode("utf-8")).hexdigest() != checksum or checksum != manifest["stage_checksums"][stage]:
            raise ValueError(f"checkpoint checksum mismatch: {stage}")
    envelopes = json.loads(checkpoints["serialization"][0])["controls"]["envelopes"]
    results = validate_candidate(tables, config["expectations"])
    results.append(validate_exports(tables, envelopes))
    # Preserve a block from the full framework gate (e.g. a missed negative control).
    framework_gate = manifest["gate"]["status"] == "FIXTURES_PASSED"
    results.append({"rule_id": "P1_FRAMEWORK_GATE", "severity": "P0", "scope": "MANIFEST", "status": "PASS" if framework_gate else "FAIL",
                    "failures": [] if framework_gate else [{"record_key": "manifest", "reason": "framework gate blocked"}]})
    if manifest_path.read_bytes() != manifest_bytes:
        raise ValueError("run changed during independent inspection; retry after writer finishes")
    return {"validation_scope": "DEVELOPMENT_PROJECTIONS_ONLY", "results": results, "gate": gate(results),
            "defects": defects(results), "profiling": profile(tables), "reconciliation": reconcile_candidate(tables, config["expectations"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "config/phase1-development.json")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.run_dir.resolve(), args.config.resolve())
    except Exception as exc:
        result = {"gate": {"status": "BLOCKED", "dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}, "error": str(exc)}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["gate"]))
    return 0 if result["gate"]["status"] == "FIXTURES_PASSED" else 2


if __name__ == "__main__":
    sys.exit(main())
