"""Generate only the connected synthetic financial foundation."""
import argparse
import json
import logging
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from healthcare_synthetic.financial_pipeline import run_financial

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/financial-history');p.add_argument('--config',type=Path,default=ROOT/'config/financial-history-generation.json')
    p.add_argument('--review',type=Path,default=ROOT/'reviews/financial-history-review.json');p.add_argument('--fail-stage');p.add_argument('--crash-stage');a=p.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    result=run_financial(a.config,a.output,a.review,a.fail_stage,a.crash_stage)
    print(json.dumps({k:result[k] for k in ('status','business_sha256','business_rows','rows_by_table')}));sys.exit(0 if result['status'] in ('FINANCIAL_HISTORY_PASSED','REVIEW_PENDING') else 2)
