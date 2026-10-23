"""Generate full-schema synthetic healthcare master data only."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from healthcare_synthetic.master_pipeline import GRAPH, run_master


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/master-data-generation.json")
    parser.add_argument("--output", type=Path, default=ROOT / "output/master-foundation")
    parser.add_argument("--review", type=Path, default=ROOT / "reviews/master-data-realism-review.json")
    parser.add_argument("--fail-stage", choices=GRAPH)
    parser.add_argument("--crash-stage", choices=GRAPH)
    args = parser.parse_args()
    try:
        result = run_master(args.config, args.output, review_path=args.review, fail_stage=args.fail_stage, crash_stage=args.crash_stage)
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc)}))
        return 1
    print(json.dumps({k: result[k] for k in ("status", "business_rows", "business_sha256", "executed", "reused", "full_dataset_accepted")}))
    return 0 if result["status"] == "MASTER_FOUNDATION_PASSED" else 2


if __name__ == "__main__":
    sys.exit(main())
