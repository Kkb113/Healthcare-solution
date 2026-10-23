"""Generate the local connected workforce/resource/stock foundation."""
import argparse
import json
import logging
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from healthcare_synthetic.resource_pipeline import run_resources

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/resource-foundation');p.add_argument('--config',type=Path,default=ROOT/'config/resource-foundation-generation.json');p.add_argument('--review',type=Path,default=ROOT/'reviews/resource-foundation-review.json');p.add_argument('--fail-stage');p.add_argument('--crash-stage');a=p.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(message)s')
    try:
        m=run_resources(a.config,a.output,a.review,a.fail_stage,a.crash_stage)
        print(json.dumps({k:m[k] for k in ('status','business_rows','business_sha256','rows_by_table')}))
        sys.exit(0 if m['status']=='RESOURCE_FOUNDATION_PASSED' else 2)
    except Exception as exc:print(json.dumps({'status':'FAILED','error':str(exc)}));sys.exit(1)
