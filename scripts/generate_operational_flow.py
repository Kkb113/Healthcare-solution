"""Generate the integrated operational candidate, without advancing to solution development."""
import argparse
import json
import logging
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from healthcare_synthetic.operational_pipeline import run_operations

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=ROOT/'config/operational-flow-generation.json')
    p.add_argument('--output',type=Path,default=ROOT/'output/operational-flow')
    p.add_argument('--review',type=Path,default=ROOT/'reviews/operational-flow-review.json')
    p.add_argument('--fail-stage');p.add_argument('--crash-stage');a=p.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(message)s')
    try:
        result=run_operations(a.config,a.output,a.review,a.fail_stage,a.crash_stage)
        print(json.dumps({k:result[k] for k in ('status','business_rows','business_sha256','rows_by_table')}))
        sys.exit(0 if result['status'] in ('REVIEW_PENDING','OPERATIONAL_FLOW_PASSED') else 2)
    except Exception as exc:print(type(exc).__name__+': '+str(exc),file=sys.stderr);sys.exit(2)
