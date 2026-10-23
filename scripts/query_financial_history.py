"""Inspect accepted financial history without deploying an analytics solution."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from healthcare_synthetic.financial_queries import load_candidate,claim_history,selected_costs,select_monthly

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('view',choices=('claims','costs','monthly'));p.add_argument('--output',type=Path,default=ROOT/'output/financial-history')
    p.add_argument('--at',default='2026-01-01T05:59:59Z');p.add_argument('--known',default='2026-01-10T23:59:59Z');p.add_argument('--month',default='2025-12-01');p.add_argument('--scenario',choices=('ACTUAL','BUDGET','FORECAST'),default='ACTUAL');a=p.parse_args()
    if a.view=='claims':
        result=claim_history(load_candidate(a.output,('claim','claim_event','patient_coverage','payer_plan')),a.at,a.known);result.pop('balances')
    elif a.view=='costs':
        result=selected_costs(load_candidate(a.output,('cost_allocation',)),a.known);result={'selected_pool_runs':len(result['selected_runs']),'totals':result['totals']}
    else:
        rows=select_monthly(load_candidate(a.output,('finance_monthly',)),a.scenario,a.month,a.known)
        result={'scenario':a.scenario,'target_month':a.month,'known_at':a.known,'rows':len(rows),'vintages':sorted({r['vintage_id'] for r in rows}),'units':sorted({r['unit_code'] for r in rows})}
    print(json.dumps(result,indent=2))
