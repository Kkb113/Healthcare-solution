"""Independently inspect persisted master data, hashes, history and realism review."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sqlite3
import sys
from importlib import metadata, resources
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from healthcare_synthetic.master_review import render_review, review_gate
from healthcare_synthetic.master_validation import MasterValidator


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def inspect_master(output, config_path=ROOT / "config/master-data-generation.json", review_path=ROOT / "reviews/master-data-realism-review.json"):
    output = Path(output).resolve()
    manifest_bytes = (output / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest["profile"] != "MASTER_FOUNDATION" or manifest["status"] not in ("MASTER_FOUNDATION_PASSED", "REVIEW_PENDING", "BLOCKED"):
        raise ValueError("master run incomplete, failed or wrong profile")
    cfg = read(config_path)
    if hashlib.sha256(encode(cfg)).hexdigest() != manifest["locks"]["configuration_sha256"]:
        raise ValueError("master configuration checksum mismatch")
    runtime = {"python": platform.python_version(), "implementation": platform.python_implementation(), "tzdata": metadata.version("tzdata"),
               "chicago_sha256": hashlib.sha256(resources.files("tzdata").joinpath("zoneinfo/America/Chicago").read_bytes()).hexdigest()}
    if runtime != manifest["locks"]["runtime"]:
        raise ValueError("independent master runtime mismatch")
    for relative, expected in manifest["locks"]["files"].items():
        path = (ROOT / relative).resolve()
        if ROOT not in path.parents or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("master input lock mismatch: " + relative)
    tables = {}
    declared_files = {m["file"] for m in manifest["canonical_files"].values()}
    actual_files = {p.relative_to(output).as_posix() for p in (output / "canonical").iterdir() if p.is_file()}
    if actual_files != declared_files:
        raise ValueError("unexpected/missing canonical master files")
    for table, expected in manifest["canonical_files"].items():
        path = (output / expected["file"]).resolve()
        if output not in path.parents:
            raise ValueError("canonical path escaped run directory")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected["sha256"] or len(raw) != expected["bytes"]:
            raise ValueError("master canonical file checksum mismatch: " + table)
        rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
        if len(rows) != expected["rows"]:
            raise ValueError("master file row count differs: " + table)
        tables[table] = rows
    if hashlib.sha256(encode({t: manifest["canonical_files"][t]["sha256"] for t in sorted(tables)})).hexdigest() != manifest["business_sha256"]:
        raise ValueError("master business hash differs")
    connection = sqlite3.connect("file:" + (output / "checkpoints.sqlite3").as_posix() + "?mode=ro", uri=True)
    checkpoint_names = set()
    try:
        for stage, payload, checksum in connection.execute("SELECT name,payload,checksum FROM stages"):
            checkpoint_names.add(stage)
            if hashlib.sha256(payload.encode()).hexdigest() != checksum or manifest["stage_checksums"].get(stage) != checksum:
                raise ValueError("master checkpoint checksum differs: " + stage)
            for table, rows in json.loads(payload)["tables"].items():
                row_hash = hashlib.sha256()
                for row in rows:
                    row_hash.update(encode(row) + b"\n")
                if row_hash.hexdigest() != manifest["canonical_files"][table]["sha256"]:
                    raise ValueError("master canonical/checkpoint content differs: " + table)
    finally:
        connection.close()
    if checkpoint_names != set(manifest["stage_checksums"]):
        raise ValueError("master checkpoint inventory differs")
    refs = {"names": read(ROOT / cfg["references"]["names"]), "codes": read(ROOT / cfg["references"]["clinical_codes"]), "local": read(ROOT / cfg["references"]["local_catalog"])}
    result = MasterValidator(tables, read(ROOT / "contracts/phase0/schema.json"), cfg, read(ROOT / "contracts/master-data-policy.json"), refs).run()
    body, selection = render_review(tables, cfg)
    if (output / "identity-review-sample.md").read_bytes() != body.encode():
        raise ValueError("master review sample differs from selected records")
    result["review"] = review_gate(selection, read(review_path) if Path(review_path).exists() else None)
    result["review_selection"] = selection
    result["gate_status"] = "MASTER_FOUNDATION_PASSED" if result["status"] == "MASTER_CHECKS_PASSED" and result["review"]["status"] == "PASS" else ("REVIEW_PENDING" if result["status"] == "MASTER_CHECKS_PASSED" else "BLOCKED")
    if (output / "manifest.json").read_bytes() != manifest_bytes:
        raise ValueError("master run changed during inspection")
    result["artifact_integrity"] = "PASS"
    result["business_sha256"] = manifest["business_sha256"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/master-foundation")
    parser.add_argument("--config", type=Path, default=ROOT / "config/master-data-generation.json")
    parser.add_argument("--review", type=Path, default=ROOT / "reviews/master-data-realism-review.json")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_master(args.output, args.config, args.review)
    except Exception as exc:
        result = {"gate_status": "BLOCKED", "error": str(exc), "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("gate_status", "full_dataset_accepted", "solution_status")}, ensure_ascii=False))
    return 0 if result["gate_status"] == "MASTER_FOUNDATION_PASSED" else 2


if __name__ == "__main__":
    sys.exit(main())
