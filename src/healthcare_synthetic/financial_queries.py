"""Disposable read-only acceptance consumers, with explicit as-of and grain rules."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


def unique_events(rows):
    seen={}
    for r in rows:
        key=r['claim_event_id']
        if key in seen and seen[key]!=r:raise ValueError('conflicting duplicate financial event')
        seen[key]=r
    return list(seen.values())


def claim_history(tables,at,known):
    """Independent original-claim balances; repeated delivery is idempotent."""
    headers={r['claim_id']:r for r in tables['claim'] if r['export_available_at']<=known and r['created_at']<=at}
    rows=defaultdict(list)
    for r in unique_events(tables['claim_event']):
        if r['claim_id'] in headers and r['occurred_at']<=at and r['export_available_at']<=known:rows[r['claim_id']].append(r)
    coverage={r['coverage_version_id']:r for r in tables['patient_coverage']};payer={r['payer_plan_id']:r for r in tables['payer_plan']}
    balances={};cash=Decimal(0);observed=set();denied=set();patient_accounts=0
    for cid,h in headers.items():
        balance=Decimal(h['opening_ar']) if at>='2023-01-01T06:00:00Z' else Decimal(0)
        for r in rows[cid]:balance+=Decimal(r['ar_delta']);cash+=Decimal(r['cash_delta'])
        balances[cid]=format(balance,'.2f')
        selfpay=payer[coverage[h['coverage_version_id']]['payer_plan_id']]['payer_type']=='SELF_PAY'
        patient_accounts+=selfpay
        if not selfpay and not h['carry_in']:
            for r in rows[cid]:
                if r['attempt_no']==1 and r['event_type'] in ('ADJUDICATED','DENIED'):observed.add(cid)
                if r['attempt_no']==1 and r['event_type']=='DENIED':denied.add(cid)
    return {'original_accounts':len(headers),'self_pay_statement_accounts':patient_accounts,'observed_initial_insured_claims':len(observed),
            'initial_denied_insured_claims':len(denied),'denial_rate':str(Decimal(len(denied))/len(observed)) if observed else None,
            'billed_ar':format(sum(map(Decimal,balances.values())),'.2f'),'cash':format(cash,'.2f'),'balances':balances}


def selected_costs(tables,known):
    by_posting=defaultdict(lambda:defaultdict(list))
    for r in tables['cost_allocation']:
        if r['export_available_at']<=known:by_posting[r['posting_id']][r['allocation_run_id']].append(r)
    totals=defaultdict(Decimal);runs={}
    for pid,versions in by_posting.items():
        chosen=max(versions,key=lambda rid:(versions[rid][0]['known_from'],rid));runs[pid]=chosen
        for r in versions[chosen]:totals[r['destination_type']]+=Decimal(r['allocated_amount'])
    return {'selected_runs':runs,'totals':{k:format(v,'.2f') for k,v in sorted(totals.items())}}


def select_monthly(tables,scenario,period,known):
    selected={}
    for r in tables['finance_monthly']:
        if r['scenario']!=scenario or r['accounting_month']!=period or r['published_at']>known:continue
        key=(r['cost_center_id'],r['account_catalog_id'],r['measure_code'],r['unit_code'])
        if key not in selected or r['published_at']>selected[key]['published_at']:selected[key]=r
    return [selected[k] for k in sorted(selected,key=lambda key:tuple(x or '' for x in key))]


def variance(actual,budget,normal_balance,account_code):
    if actual is None or budget is None:return {'favorable':None,'percent':None,'reason':'MISSING_COMPARABLE_SERIES'}
    a,b=Decimal(actual),Decimal(budget);value=a-b if account_code=='GROSS_REVENUE' else b-a
    return {'favorable':format(value,'.2f'),'percent':str(value/abs(b)*100) if b else None,'reason':None if b else 'ZERO_BUDGET_DENOMINATOR'}


def load_candidate(output,names):
    output=Path(output).resolve();manifest=json.loads((output/'manifest.json').read_text());ready=json.loads((output/'candidate-ready.json').read_text())
    if manifest['status']!='FINANCIAL_HISTORY_PASSED' or ready['business_sha256']!=manifest['business_sha256']:raise ValueError('financial candidate is not ready')
    tables={}
    for name in names:
        meta=manifest['canonical_files'][name];path=(output/meta['file']).resolve()
        if output not in path.parents:raise ValueError('financial consumer path escaped')
        h=hashlib.sha256();rows=[];size=0
        with path.open('rb') as stream:
            for line in stream:h.update(line);size+=len(line);rows.append(json.loads(line))
        if h.hexdigest()!=meta['sha256'] or size!=meta['bytes'] or len(rows)!=meta['rows']:raise ValueError('consumer input checksum/count differs')
        tables[name]=rows
    return tables
