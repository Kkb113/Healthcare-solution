"""Reviewed synthetic baseline migration, without editing accepted snapshots.

Old and corrected candidates are different dataset versions. They must never be
incrementally merged by immutable source-version ID. Enrollment intervals and
identities are retained; prospective payer choice and worker birthday imputation
are corrected before downstream experiments are generated.
"""
from __future__ import annotations

from collections import defaultdict
import calendar
import json
from datetime import date
from pathlib import Path

from .core import draw, stable_id


def amend(tables, seed=20261023):
    result = dict(tables)
    cfg = json.loads((Path(__file__).resolve().parents[2]/'config/integrated-history-generation.json').read_text(encoding='utf-8'))
    people = {r['patient_version_id']: r for r in tables['patient']}
    plans = {r['payer_plan_id']: r for r in tables['payer_plan']}; pools = defaultdict(list)
    for r in tables['payer_plan']:
        if not r['plan_code'].startswith('RENEWAL'):
            pools[r['payer_type']].append(r)
    for values in pools.values():
        values.sort(key=lambda r:r['plan_code'])
    coverage = []
    for old in tables['patient_coverage']:
        p = people[old['patient_version_id']]; birth = date.fromisoformat(p['birth_date']); start = date.fromisoformat(old['valid_from'][:10])
        age = start.year-birth.year-((start.month,start.day)<(birth.month,birth.day))
        # These prospective weights are preregistered, not chosen using future
        # visits or payments. Medicare requires age eligibility at enrollment.
        weights = list(cfg['payer_mix_65plus' if age>=65 else 'payer_mix_under65'].items())
        if sum(w for _,w in weights)!=100 or any(w<0 for _,w in weights) or age<65 and any(k=='MEDICARE' for k,_ in weights):
            raise ValueError('invalid prospective payer weights or Medicare eligibility')
        value = draw(seed, old['coverage_id'], 'integrated-prospective-payer', upper=100)
        for kind,weight in weights:
            if value < weight:
                break
            value -= weight
        prior = plans[old['payer_plan_id']]
        selected = prior if prior['payer_type']==kind else pools[kind][draw(seed,old['coverage_id'],'integrated-payer-product',upper=len(pools[kind]))]
        row = {**old,'payer_plan_id':selected['payer_plan_id'],'coverage_status':'SELF_PAY' if kind=='SELF_PAY' else 'ACTIVE',
               'synthetic_member_id':('SP-' if kind=='SELF_PAY' else 'MBR-')+stable_id('member',p['patient_id'],selected['plan_code'])[-16:].upper(),
               'generation_run_id':'integrated-master-context-v1'}
        coverage.append(row)
    workers = []
    for old in tables['worker_assignment']:
        month = 1+draw(seed,old['worker_id'],'integrated-worker-birth-month',upper=12)
        day = 1+draw(seed,old['worker_id'],'integrated-worker-birth-day',upper=calendar.monthrange(int(old['birth_date'][:4]),month)[1])
        workers.append({**old,'birth_date':f"{old['birth_date'][:4]}-{month:02d}-{day:02d}", 'generation_run_id':'integrated-master-context-v1'})
    result['patient_coverage'] = coverage; result['worker_assignment'] = workers
    return result
