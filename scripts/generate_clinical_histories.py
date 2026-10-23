"""Generate linked provisional clinical histories from the accepted master foundation."""
import argparse
import json
import logging
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from healthcare_synthetic.clinical_pipeline import run_clinical

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=ROOT / 'config/clinical-history-generation.json')
    p.add_argument('--output', type=Path, default=ROOT / 'output/clinical-histories')
    p.add_argument('--review', type=Path, default=ROOT / 'reviews/clinical-journey-review.json')
    p.add_argument('--fail-stage'); p.add_argument('--crash-stage')
    args = p.parse_args()
    try:
        m = run_clinical(args.config, args.output, review_path=args.review, fail_stage=args.fail_stage, crash_stage=args.crash_stage)
    except Exception as exc:
        print(json.dumps({'status': 'FAILED', 'error': str(exc)})); return 1
    print(json.dumps({k: m[k] for k in ('status', 'business_rows', 'business_sha256', 'trajectory_status')}))
    return 0 if m['status'] == 'CLINICAL_HISTORIES_PASSED' else 2

if __name__ == '__main__': sys.exit(main())
