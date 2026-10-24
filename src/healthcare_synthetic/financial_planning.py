"""Axiom-shaped canonical monthly values with immutable, historically valid vintages."""
from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from .core import instant, stable_id
from .financial_common import Context, START, CUTOFF, at, cash, close, date_parts, day, delivered_assignments, latest, month, months, next_month, quantity, stamp
from .operational_validation import bed_intervals


def statistics(tables,period,known):
    """Captured actual activity at publication; no completed future shifts or stays."""
    enc={r['encounter_version_id']:r for r in tables['encounter']};loc={r['location_id']:r for r in tables['location']}
    values=defaultdict(lambda:defaultdict(Decimal));m=str(period)[:7]
    # The publication may observe an incomplete later-month stream. Only
    # effective events before this target month's boundary are needed here.
    target_end=stamp(at(next_month(period)))
    period_events=[r for r in tables['bed_event'] if r['effective_at']<target_end]
    for bid,eid,a,z in bed_intervals(period_events,enc,known):
        start=max(instant(a),at(period));end=min(instant(z),at(next_month(period)))
        if end>start:values[loc[bid]['cost_center_id']]['PATIENT_DAYS']+=Decimal(str((end-start).total_seconds()))/86400
    for e in latest(tables['encounter'],'encounter_id',known=known).values():
        if e['encounter_class']=='IPD' and not e['carry_in'] and e['admitted_at'] and str(day(e['admitted_at']))[:7]==m:
            values[loc[e['location_id']]['cost_center_id']]['ADMISSIONS']+=1
    for r in sorted(latest(tables['staff_shift'],'shift_id',known=known).values(),key=lambda r:r['shift_id']):
        if not r['actual_start'] or not r['actual_end']:continue
        start=instant(r['actual_start']);end=instant(r['actual_end']);a=max(start,at(period));z=min(end,at(next_month(period)))
        if z>a:values[r['cost_center_id']]['PRODUCTIVE_HOURS']+=Decimal(r['productive_hours'])*Decimal(str((z-a).total_seconds()))/Decimal(str((end-start).total_seconds()))
    for v in values.values():v['FTE']=v['PRODUCTIVE_HOURS']*12/2080
    return values


def nominal(c,cc,account,target,known):
    """Published capacity and rate assumptions; no future realized facts."""
    center=c.cc[cc];unit=center['cost_center_code'].split('-')[-1];n=calendar.monthrange(target.year,target.month)[1]
    inflation=1+Decimal(c.cfg['annual_cost_escalation'])*(target.year-2023)
    season=Decimal('1.10') if target.month in (1,2,12) else Decimal('0.96') if target.month in (6,7,8) else Decimal(1)
    occupancy=Decimal(c.cfg['planning_occupancy']);prices=c.cfg['prices'];gross=Decimal(0)
    if unit in ('MEDICINE','SURGERY','ICU'):
        beds=4 if unit=='ICU' else 10
        gross=beds*n*occupancy*Decimal(prices['BILL-ICU' if unit=='ICU' else 'BILL-ROOM'])*season
    elif unit=='ED':gross=n*Decimal(c.cfg['planning_ed_visits_per_day'])*Decimal(prices['BILL-ED'])*season
    elif unit=='AMBULATORY':gross=n*Decimal(c.cfg['planning_opd_visits_per_day'])*Decimal(prices['BILL-OPD'])
    elif unit=='OPERATING':gross=24*n*occupancy/Decimal(c.cfg['planning_mean_los_days'])*Decimal('0.25')*Decimal(prices['0FT44ZZ'])
    elif unit=='LABORATORY':gross=n*30*Decimal(prices['LAB'])
    elif unit=='PHARMACY':gross=n*70*Decimal(prices['PHARMACY'])
    if account=='GROSS_REVENUE':return gross*inflation
    if account=='CONTRA_REVENUE':return gross*(1-Decimal(c.cfg['planning_allowed_factor']))*inflation
    if account=='LABOR_POOL':
        workers=defaultdict(list)
        for w in delivered_assignments(c.t['worker_assignment'],known):
            if w['valid_from']<=stamp(at(target,12))<(w['valid_to'] or '9999'):
                workers[w['worker_id']].append(w)
        total=Decimal(0)
        for history in workers.values():
            w=max(history,key=lambda x:x['revision_no'])
            if w['cost_center_id']==cc and w['hire_date']<=str(target)<(w['termination_date'] or '9999'):
                capture=Decimal(1) if w['role'] in ('ADMIN','RN','PHYSICIAN') else Decimal('0.08')
                total+=Decimal(w['fte'])*Decimal(w['hourly_cost_rate'])*2080/12*capture
        return total*inflation
    if account=='DRUG_POOL':return n*Decimal('32.00')*inflation if unit=='PHARMACY' else Decimal(0)
    if account=='SUPPLY_POOL':return n*Decimal('8.00')*inflation if unit=='LABORATORY' else n*Decimal('12.00')*inflation if unit=='OPERATING' else Decimal(0)
    if account=='OVERHEAD_POOL':return 24*n*Decimal(c.cfg['utilities_per_licensed_bed_day'])*inflation if unit=='FACILITIES' else Decimal(0)
    return Decimal(0)


def plan_amount(c,postings,cc,account,target,published,vintage):
    # Complete historical posting months only. Availability, rather than event
    # time alone, governs every observation used in a planning vintage.
    if not hasattr(c,'planning_history'):c.planning_history={}
    if published not in c.planning_history:
        preceding=sorted({r['posting_date'][:7] for r in postings if r['known_from']<=published and r['posting_date'][:7]<published[:7]})[-3:]
        totals=defaultdict(Decimal)
        for r in postings:
            if r['known_from']<=published and r['posting_date'][:7] in preceding:
                totals[r['cost_center_id'],c.cat[r['account_catalog_id']]['code']]+=Decimal(r['debit_amount'])-Decimal(r['credit_amount'])
        c.planning_history[published]=(preceding,totals)
    preceding,totals=c.planning_history[published];prior=totals[cc,account]
    if preceding:
        if account=='GROSS_REVENUE':prior=-prior
        prior=prior/len(preceding)*Decimal('1.03')
    model=nominal(c,cc,account,target,published)
    estimate=Decimal('0.70')*prior+Decimal('0.30')*model if preceding else model
    noise=Decimal(c.pick(cc+'/'+account+'/'+str(target)+'/'+vintage,'planning-uncertainty',1001)-500)/10000
    return cash(max(0,estimate*(1+noise)))


def monthly(tables,cfg,run_id):
    c=Context(tables,cfg,run_id);postings=tables['financial_posting'];rows=[]
    baseline=__import__('json').loads((__import__('pathlib').Path(__file__).resolve().parents[2]/'contracts/phase0/baseline.json').read_text())
    accounts=baseline['account_sets'];stat_units={'PATIENT_DAYS':'patient_days','ADMISSIONS':'admissions','PRODUCTIVE_HOURS':'hours','FTE':'FTE'}
    stats_centers=[r['cost_center_id'] for r in tables['cost_center'] if r['cost_center_code'].split('-')[-1] in ('MEDICINE','SURGERY','ICU','ED','AMBULATORY')]
    forecast_centers=[r['cost_center_id'] for r in tables['cost_center'] if r['cost_center_code'].split('-')[-1] in ('MEDICINE','SURGERY','ED','AMBULATORY')]
    def emit(cc,account,measure,m,scenario,vintage,published,amount=None,qty=None,supersedes=None):
        unit='USD' if account else stat_units[measure];key='/'.join((cc,account or measure,str(m),scenario,vintage,unit))
        family='FINANCIAL_STATISTICS' if not account else 'FINANCIAL_BALANCES' if account in accounts['balance'] else 'FINANCIAL_PNL'
        rows.append(c.row('finance_monthly',key,published,finance_record_id=stable_id('finance_record',key),facility_id=c.cc[cc]['facility_id'],cost_center_id=cc,
            account_catalog_id=c.code(account,m) if account else None,measure_code=measure,accounting_month=str(m),scenario=scenario,vintage_id=vintage,published_at=published,
            amount=cash(amount) if account else None,quantity=quantity(qty) if not account else None,unit_code=unit,
            report_template_id='AXIOM-SYNTHETIC-'+family,source_file_id='AXIOM/'+family+'/'+scenario+'/'+vintage+'/'+str(m),supersedes_vintage_id=supersedes))
    # Cache journal totals by knowledge bucket and monthly close, to avoid a
    # series-by-series scan of all journal lines.
    for m in months():
        vintages=[('ACTUAL-'+str(m),close(m),None)]
        if m==date(2025,12,1):vintages.append(('ACTUAL-'+str(m)+'-FINAL',close(m,9),'ACTUAL-'+str(m)))
        for vintage,published,supersedes in vintages:
            pnl=defaultdict(Decimal);balances=defaultdict(Decimal)
            for p in postings:
                if p['known_from']>published or p['posting_date']>=str(next_month(m)):continue
                code=c.cat[p['account_catalog_id']]['code'];v=Decimal(p['debit_amount'])-Decimal(p['credit_amount'])
                if code in accounts['pnl'] and p['posting_date']>=str(m):pnl[p['cost_center_id'],code]+=v
                elif code in accounts['balance']:balances[p['facility_id'],code]+=v
            for cc in sorted(c.cc):
                for account in accounts['pnl']:
                    value=pnl[cc,account]*(-1 if account=='GROSS_REVENUE' else 1)
                    emit(cc,account,'ACCOUNT_AMOUNT',m,'ACTUAL',vintage,published,amount=value,supersedes=supersedes)
            for fid in sorted(r['facility_id'] for r in tables['facility']):
                for account in accounts['balance']:
                    value=balances[fid,account]*(-1 if account in ('AP','PAYROLL_PAYABLE','OPENING_EQUITY') else 1)
                    emit(c.centers[fid,'ADMINISTRATION'],account,'ACCOUNT_AMOUNT',m,'ACTUAL',vintage,published,amount=value,supersedes=supersedes)
            actual_stats=statistics(tables,m,published)
            for cc in sorted(stats_centers):
                for measure in stat_units:emit(cc,None,measure,m,'ACTUAL',vintage,published,qty=actual_stats[cc].get(measure,0),supersedes=supersedes)
        original=f'BUDGET-{m.year}-ORIGINAL';publication=stamp(at(date(m.year-1,12,20),12))
        versions=[(original,publication,None)]
        if m.year in (2024,2025) and m.month>=7:versions.append((f'BUDGET-{m.year}-MIDYEAR',stamp(at(date(m.year,6,20),12)),original))
        for vintage,published,supersedes in versions:
            for cc in sorted(c.cc):
                for account in accounts['budget']:
                    amount=plan_amount(c,postings,cc,account,m,published,vintage)
                    emit(cc,account,'ACCOUNT_AMOUNT',m,'BUDGET',vintage,published,amount=amount,supersedes=supersedes)
        if m.month in (1,4,7,10):
            published=stamp(at(m-timedelta(days=12),12));vintage='FORECAST-'+str(m)
            for horizon in range(3):
                target=m
                for _ in range(horizon):target=next_month(target)
                for cc in sorted(forecast_centers):
                    for account in ('GROSS_REVENUE','LABOR_POOL'):
                        emit(cc,account,'ACCOUNT_AMOUNT',target,'FORECAST',vintage,published,amount=plan_amount(c,postings,cc,account,target,published,vintage))
        # Facility-level planning statistics are separate unit series.
        n=calendar.monthrange(m.year,m.month)[1]
        for fid in sorted(r['facility_id'] for r in tables['facility']):
            days=24*n*Decimal(cfg['planning_occupancy']);hours=days*Decimal('5.5')
            for measure,value in [('PATIENT_DAYS',days),('ADMISSIONS',days/Decimal(cfg['planning_mean_los_days'])),('PRODUCTIVE_HOURS',hours),('FTE',hours*12/2080)]:
                emit(c.centers[fid,'ADMINISTRATION'],None,measure,m,'BUDGET',original,publication,qty=value)
    return {'tables':{'finance_monthly':rows},'controls':{'monthly_values':len(rows),'source_layout_serialization':'RESERVED_FOR_SOURCE_EXPORT_PHASE'}}
