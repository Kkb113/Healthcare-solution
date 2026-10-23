"""Run only the small Phase 1 development profile; no cloud access."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from healthcare_synthetic.engine import STAGES, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/phase1-development.json")
    parser.add_argument("--output", type=Path, default=ROOT / "output/phase1-development")
    parser.add_argument("--fail-stage", choices=STAGES, help="Controlled pre-commit exception for recovery testing")
    parser.add_argument("--crash-stage", choices=STAGES, help="Controlled process exit 97 before checkpoint commit")
    args = parser.parse_args()
    try:
        manifest = run(ROOT, args.config, args.output, fail_stage=args.fail_stage, crash_stage=args.crash_stage)
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc)}))
        return 1
    print(json.dumps({k: manifest[k] for k in ("status", "business_rows", "business_sha256", "executed", "reused", "dataset_accepted")}))
    return 0 if manifest["status"] == "FIXTURES_PASSED" else 2


if __name__ == "__main__":
    sys.exit(main())
