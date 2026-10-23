"""Patient cost drivers, direct issue attribution and versioned analytical allocation."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from .core import allocate_cents, instant, stable_id
from .financial_common import Context, START, CUTOFF, at, cash, close, date_parts, day, month, quantity, shares, stamp
from .operational_validation import bed_intervals
from .resource_stock_validation import expected_uses


def care_drivers(tables,cfg):
    c=Context(tables,cfg,'drivers');weights=defaultdict(lambda:defaultdict(Decimal));ipd=defaultdict(lambda:defaultdict(Decimal));stats=defaultdict(lambda:defaultdict(Decimal))
    placed=defaultdict(list)
    for bid,eid,a,z in bed_intervals(tables['bed_event'],c.enc):
        placed[eid].append((instant(a),instant(z)))
        loc=c.loc[bid];fid=loc['facility_id'];cc=loc['cost_center_id'];e=c.latest[eid]
        for d,seconds in date_parts(instant(a),instant(z)):
            m=d[:7];hours=seconds/3600
            weights[m,cc,'LABOR'][eid]+=hours
            # ACUTE RN shifts are captured at MEDICINE, serving both medical and surgical beds.
            if cc==c.centers[fid,'SURGERY']:weights[m,c.centers[fid,'MEDICINE'],'LABOR'][eid]+=hours
            ipd[m,fid][eid]+=hours
            stats[m,cc]['PATIENT_DAYS']+=seconds/86400
    for eid,e in sorted(c.latest.items()):
        if e['discharged_at'] and e['discharged_at']<stamp(START):continue
        if e['encounter_class']=='IPD':
            if not e['carry_in']:
                cc=c.loc[e['location_id']]['cost_center_id'];stats[str(month(day(e['admitted_at'])) )[:7],cc]['ADMISSIONS']+=1
            # Clinical admission/boarding is distinct from licensed-bed use.
            # Holding care follows the accepted source-author routing proxy.
            cursor=max(START,instant(e['admitted_at']));end=min(CUTOFF,instant(e['discharged_at'])) if e['discharged_at'] else CUTOFF
            gaps=[]
            for a,z in sorted(placed[eid]):
                if a>cursor:gaps.append((cursor,a))
                cursor=max(cursor,z)
            if cursor<end:gaps.append((cursor,end))
            cc=c.centers[e['facility_id'],'ED' if e['admission_source']=='ED' else 'MEDICINE']
            for a,z in gaps:
                for d,seconds in date_parts(a,min(z,end)):weights[d[:7],cc,'LABOR'][eid]+=seconds/3600
        else:
            start=max(START,instant(e['arrival_at']));end=min(CUTOFF,instant(e['discharged_at'])) if e['discharged_at'] else CUTOFF
            cc=c.loc[e['location_id']]['cost_center_id']
            for d,seconds in date_parts(start,end):weights[d[:7],cc,'LABOR'][eid]+=seconds/3600
    event_index={r['clinical_event_version_id']:r for r in tables['clinical_event']}
    for r in tables['clinical_event']:
        if r['event_type']=='PROCEDURE' and c.cat[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9') and stamp(START)<=r['occurred_at']<stamp(CUTOFF):
            e=c.enc[r['encounter_version_id']];eid=e['encounter_id'];cc=c.centers[e['facility_id'],'OPERATING']
            weights[str(month(day(r['occurred_at'])))[:7],cc,'LABOR'][eid]+=(Decimal(str((instant(r['period_end_at'])-instant(r['occurred_at'])).total_seconds()))/60)
    # Medication source groups have a direct actual event-to-lot link. Allocate
    # the stored group cents, not rounded per-dose amounts that would drift.
    med=defaultdict(lambda:defaultdict(Decimal));sup=defaultdict(lambda:defaultdict(Decimal))
    for use in expected_uses(tables):
        when,event_id,loc,code,item,qty,medication,link=use;eid=c.enc[event_index[event_id]['encounter_version_id']]['encounter_id']
        if medication:med[link][eid]+=qty
        else:sup[loc,item,str(day(when))][eid]+=qty
    supply_value=defaultdict(Decimal)
    for r in tables['inventory_movement']:
        if r['movement_type']!='CONSUME' or Decimal(r['nonpatient_waste_base']):continue
        loc=c.loc[r['location_id']];cc=loc['cost_center_id'];m=str(month(day(r['occurred_at'])))[:7]
        if c.cat[r['catalog_item_id']]['domain']=='MEDICATION':
            source=med[r['consumption_group_key']]
            if not source:raise ValueError('patient drug cost has no actual issue driver')
            parts=allocate_cents(-Decimal(r['extended_cost']),{k:str(v) for k,v in source.items()})
            for eid,value in parts.items():weights[m,cc,'DRUG'][eid]+=value
        else:supply_value[r['location_id'],r['catalog_item_id'],str(day(r['occurred_at']))]-=Decimal(r['extended_cost'])
    for (loc,item,d),value in sorted(supply_value.items()):
        parts=allocate_cents(value,{k:str(v) for k,v in sup[loc,item,d].items()})
        for eid,amount in parts.items():weights[d[:7],c.loc[loc]['cost_center_id'],'SUPPLY'][eid]+=amount
    for (m,fid),values in ipd.items():weights[m,c.centers[fid,'FACILITIES'],'OVERHEAD']=values
    # Productive hours split by actual local elapsed time. Attendance revisions
    # are folded first; FTE is captured productive hours / (2080/12), not headcount.
    for r in sorted(__import__('healthcare_synthetic.financial_common',fromlist=['latest']).latest(tables['staff_shift'],'shift_id').values(),key=lambda r:r['shift_id']):
        if not r['actual_start'] or not r['actual_end']:continue
        seconds=Decimal(str((instant(r['actual_end'])-instant(r['actual_start'])).total_seconds()))
        for d,part in date_parts(instant(r['actual_start']),instant(r['actual_end'])):
            stats[d[:7],r['cost_center_id']]['PRODUCTIVE_HOURS']+=Decimal(r['productive_hours'])*part/seconds
    for values in stats.values():values['FTE']=values['PRODUCTIVE_HOURS']*12/2080
    return weights,stats


def allocations(tables,cfg,run_id):
    c=Context(tables,cfg,run_id);weights,_=care_drivers(tables,cfg);rows=[];histories=defaultdict(list)
    for e in tables['encounter']:histories[e['encounter_id']].append(e)
    for p in sorted(tables['financial_posting'],key=lambda r:r['posting_id']):
        if not p['eligible_for_allocation']:continue
        category=c.cat[p['account_catalog_id']]['code'].split('_')[0];m=p['posting_date'][:7]
        driver=weights.get((m,p['cost_center_id'],category),{})
        runs=[('COUNT' if category=='OVERHEAD' else 'SOURCE',p['known_from'])]
        if category=='OVERHEAD' and m+'-01' in cfg['revised_allocation_months']:runs.append(('PATIENT_HOURS',max(close(m+'-01',9),p['known_from'])))
        previous=None
        for method,known in runs:
            rid=stable_id('allocation_run',p['posting_id'],method,known)
            unsupported=not driver and category=='LABOR' and c.cc[p['cost_center_id']]['center_type']!='CLINICAL'
            if driver:
                w={eid:Decimal(1) if method=='COUNT' else v for eid,v in driver.items() if v>0}
                unit='encounter_months' if method=='COUNT' else 'USD_consumption' if category in ('DRUG','SUPPLY') else 'case_minutes' if p['cost_center_id']==c.centers[p['facility_id'],'OPERATING'] else 'patient_hours'
            else:w={'NONPATIENT' if unsupported else 'RESIDUAL':Decimal(1)};unit='explicit_destination'
            w={k:Decimal(quantity(v)) for k,v in w.items()}
            amount=Decimal(p['debit_amount'])-Decimal(p['credit_amount']);parts=allocate_cents(amount,{k:str(v) for k,v in w.items()});fractions=shares(w)
            for destination,value in sorted(parts.items()):
                key=rid+'/'+destination;e=c.latest.get(destination)
                # Resolve an encounter version already delivered at this close.
                if e and e['export_available_at']>known:
                    available=[r for r in histories[destination] if r['export_available_at']<=known]
                    e=max(available,key=lambda r:r['revision_no']) if available else None
                    if e is None:raise ValueError('allocation driver has no historically available encounter')
                rows.append(c.row('cost_allocation',key,known,allocation_id=stable_id('allocation',key),posting_id=p['posting_id'],
                    encounter_version_id=e['encounter_version_id'] if e else None,cost_center_id=p['cost_center_id'],allocation_run_id=rid,
                    destination_type='PATIENT' if e else destination,cost_category=category,accounting_month=m+'-01',driver_quantity=quantity(w[destination]),
                    driver_unit=unit,allocation_share=fractions[destination],allocated_amount=cash(value),currency='USD',known_from=known,supersedes_run_id=previous))
            previous=rid
    return {'tables':{'cost_allocation':rows},'controls':{'allocation_versions':len({r['allocation_run_id'] for r in rows})}}
