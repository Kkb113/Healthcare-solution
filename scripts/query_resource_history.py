"""Inspect local delivered roster, labor or stock history without mutating a candidate."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from healthcare_synthetic.resource_queries import labor_totals,roster_at,inventory_ledger_at

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('view',choices=('roster','labor','stock'));p.add_argument('--output',type=Path,default=ROOT/'output/resource-foundation');p.add_argument('--known-at',required=True);p.add_argument('--at');p.add_argument('--month');p.add_argument('--include-balances',action='store_true');a=p.parse_args()
    m=json.loads((a.output/'manifest.json').read_text());ready=json.loads((a.output/'candidate-ready.json').read_text())
    if m['profile']!='CONNECTED_WORKFORCE_AND_STOCK' or m['status']!='RESOURCE_FOUNDATION_PASSED' or ready['business_sha256']!=m['business_sha256']:raise ValueError('resource candidate is not ready')
    needed=('inventory_movement',) if a.view=='stock' else ('staff_shift',);tables={}
    for name in needed:
        meta=m['canonical_files'][name];file=(a.output/meta['file']).resolve()
        if a.output.resolve() not in file.parents:raise ValueError('query input path escaped candidate')
        h=hashlib.sha256();size=0;rows=[]
        with file.open('rb') as stream:
            for line in stream:h.update(line);size+=len(line);rows.append(json.loads(line))
        if h.hexdigest()!=meta['sha256'] or size!=meta['bytes'] or len(rows)!=meta['rows']:raise ValueError('query input checksum/count differs: '+name)
        tables[name]=rows
    if a.view=='labor':result=labor_totals(tables,a.known_at,a.month)
    else:
        if not a.at:p.error('--at is required for roster/stock views')
        result=roster_at(tables,a.at,a.known_at) if a.view=='roster' else inventory_ledger_at(tables,a.at,a.known_at)
        if a.view=='stock' and not a.include_balances:result.pop('balances')
    print(json.dumps(result,indent=2))
