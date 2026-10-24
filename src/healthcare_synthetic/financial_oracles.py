"""Independent cent arithmetic and source-to-journal reconciliation oracle.

No financial generator is imported. These predicates read counted source facts;
their totals are compared with persisted journals, including every timing bridge.
"""
from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

from .core import instant, chicago, draw
from .operational_validation import bed_intervals
from .resource_stock_validation import expected_uses

ZONE=chicago()


def money(v):return Decimal(v).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
def stamp(v):return v.isoformat(timespec='seconds').replace('+00:00','Z')
def day(v):return instant(v).astimezone(ZONE).date() if isinstance(v,str) else v.astimezone(ZONE).date()
def local(d,hour=0):return datetime.combine(d,datetime.min.time()).replace(hour=hour,tzinfo=ZONE).astimezone(timezone.utc)
def midnight(d):return local(d)
def following(d):return (d.replace(day=28)+timedelta(days=4)).replace(day=1)
def close(d,n=5):return stamp(local(following(d).replace(day=n),18))


def partition(total,weights):
    denominator=sum(weights.values());raw={k:abs(money(total))*100*v/denominator for k,v in weights.items()}
    amounts={k:int(v.to_integral_value(rounding=ROUND_FLOOR)) for k,v in raw.items()}
    remaining=int(abs(money(total))*100)-sum(amounts.values())
    for k in sorted(raw,key=lambda k:(-(raw[k]-amounts[k]),k))[:remaining]:amounts[k]+=1
    return {k:Decimal(v)/100*(-1 if Decimal(total)<0 else 1) for k,v in amounts.items()}


def expected_journals(tables,cfg):
    locations={r['location_id']:r for r in tables['location']};cat={r['catalog_item_id']:r for r in tables['catalog_item']}
    cc={r['cost_center_id']:r for r in tables['cost_center']};centers={(r['facility_id'],r['cost_center_code'].split('-')[-1]):r['cost_center_id'] for r in cc.values()}
    workers={r['worker_assignment_id']:r for r in tables['worker_assignment']};enc={r['encounter_version_id']:r for r in tables['encounter']}
    cov={r['coverage_version_id']:r for r in tables['patient_coverage']};payer={r['payer_plan_id']:r for r in tables['payer_plan']}
    expected=defaultdict(lambda:defaultdict(Decimal));bounds={};salary_total=Decimal(0);accrual_total=Decimal(0);opening_payroll=Decimal(0);admin_capture=defaultdict(list)
    def put(domain,fid,center,first,last,known,source,debit,credit,amount):
        v=money(amount)
        if not v:return
        if domain not in ('COST_POOL_CLOSE','REVENUE','AR','CASH','OPENING','ACCRUAL') and not source.startswith('salary/'):known=stamp(midnight(day(known)+timedelta(days=1)))
        service=date.fromisoformat(last)
        posted=last if known<=close(service) else '2025-12-31' if last.startswith('2025-12') and known<=close(service,9) else str(day(known))
        if domain=='OPENING':posted=max('2023-01-01',posted)
        if posted>'2025-12-31':raise ValueError('source oracle would post beyond cutoff')
        key=(domain,fid,center,posted,last,last,known,source);bounds[key]=min(bounds.get(key,first),first)
        expected[key][debit]+=v;expected[key][credit]-=v
    for r in tables['inventory_movement']:
        loc=locations[r['location_id']];fid=loc['facility_id'];center=loc['cost_center_id'];kind=r['movement_type'];value=Decimal(r['extended_cost'])
        if kind in ('TRANSFER_IN','TRANSFER_OUT','RETURN'):continue
        domain='INVENTORY'
        if kind=='OPENING':debit,credit,domain='INVENTORY','OPENING_EQUITY','OPENING';center=centers[fid,'ADMINISTRATION']
        elif kind=='RECEIPT':debit,credit='INVENTORY','AP';center=centers[fid,'ADMINISTRATION']
        else:
            debit='OTHER_EXPENSE' if kind!='CONSUME' or Decimal(r['nonpatient_waste_base']) else 'DRUG_DIRECT' if cat[r['catalog_item_id']]['domain']=='MEDICATION' else 'SUPPLY_DIRECT'
            credit='INVENTORY';value=-value
        service=str(day(r['occurred_at']));source=r['posting_group_key']+'/'+center+'/'+debit
        put(domain,fid,center,service,service,r['export_available_at'],source,debit,credit,value)
    shifts=defaultdict(list)
    for r in tables['staff_shift']:shifts[r['shift_id']].append(r)
    for sid,history in sorted(shifts.items()):
        prior={}
        for r in sorted(history,key=lambda r:r['revision_no']):
            value=Decimal(r['loaded_cost']);parts={}
            if value:
                if r['actual_start'] and r['actual_end']:
                    start=instant(r['actual_start']);end=instant(r['actual_end']);seconds={};cursor=start
                    while cursor<end:
                        boundary=min(end,midnight(day(cursor)+timedelta(days=1)))
                        seconds[str(day(cursor))]=Decimal(str((boundary-cursor).total_seconds()));cursor=boundary
                    parts=partition(value,seconds)
                else:parts={str(day(r['planned_start'])):value}
            w=workers[r['worker_assignment_id']];known=r['export_available_at'];center=r['cost_center_id']
            for service in sorted(set(parts)|set(prior)):
                delta=parts.get(service,0)-prior.get(service,0)
                before=service<'2023-01-01'
                if before:opening_payroll+=delta
                put('OPENING' if before else 'WORKFORCE',w['facility_id'],center,service,service,known,('opening-payroll/' if before else 'shift/')+center+'/'+service+'/'+str(day(known)),
                    'OPENING_EQUITY' if before else 'LABOR_DIRECT','PAYROLL_PAYABLE',delta)
                if w['role']=='ADMIN' and delta:admin_capture[w['worker_id'],service[:7]].append((w['facility_id'],center,known,delta))
            prior=parts
        r=max(history,key=lambda r:r['revision_no'])
        if r['attendance_status']=='PUBLISHED' and r['actual_start'] and r['actual_end'] is None:
            w=workers[r['worker_assignment_id']];elapsed=Decimal(str((instant('2026-01-01T06:00:00Z')-instant(r['actual_start'])).total_seconds()))
            planned=Decimal(str((instant(r['planned_end'])-instant(r['planned_start'])).total_seconds()))
            value=money((elapsed/3600-Decimal('.5')*elapsed/planned)*Decimal(w['hourly_cost_rate']));accrual_total+=value
            put('ACCRUAL',w['facility_id'],r['cost_center_id'],'2025-12-31','2025-12-31','2026-01-02T18:00:00Z',
                'unfinished-shifts/'+r['cost_center_id'],'LABOR_DIRECT','PAYROLL_PAYABLE',value)
    admin=defaultdict(list);admin_ids={w['worker_id'] for w in workers.values() if w['role']=='ADMIN'}
    for w in workers.values():
        if w['worker_id'] in admin_ids:admin[w['worker_id']].append(w)
    m=date(2023,1,1)
    while m<date(2026,1,1):
        n=calendar.monthrange(m.year,m.month)[1];end=following(m)-timedelta(days=1)
        for wid,history in sorted(admin.items()):
            prior={};captured=admin_capture[wid,str(m)[:7]]
            points=sorted({close(m)}|{r['export_available_at'] for r in history if close(m)<r['export_available_at']<='2026-01-10T23:59:59Z' and r['valid_from']<stamp(midnight(following(m)))}|
                          {known for _,_,known,_ in captured if close(m)<known<='2026-01-10T23:59:59Z'})
            for known in points:
                sums=defaultdict(Decimal)
                replacement={r['known_from']:min(x['export_available_at'] for x in history if x['known_from']==r['known_from']) for r in history}
                delivered=[w for w in history if w['export_available_at']<=known and (w['known_to'] is None or known<replacement.get(w['known_to'],'9999'))]
                for i in range(n):
                    d=m+timedelta(days=i);when=stamp(local(d,12))
                    valid=[w for w in delivered if w['valid_from']<=when<(w['valid_to'] or '9999') and w['hire_date']<=str(d)<(w['termination_date'] or '9999')]
                    if valid:
                        w=max(valid,key=lambda w:w['revision_no'])
                        if w['role']=='ADMIN':sums[w['facility_id'],w['cost_center_id']]+=Decimal(w['hourly_cost_rate'])*Decimal(w['fte'])*Decimal(2080)/12/n
                rounded={k:money(v) for k,v in sums.items()}
                for fid,center,available,amount in captured:
                    if available<=known:rounded[fid,center]=rounded.get((fid,center),Decimal(0))-amount
                for fid,center in sorted(set(prior)|set(rounded)):
                    value=rounded.get((fid,center),0)-prior.get((fid,center),0);salary_total+=value
                    put('WORKFORCE',fid,center,str(end),str(end),known,'salary/'+center+'/'+str(m)+'/'+str(day(known)),'LABOR_DIRECT','PAYROLL_PAYABLE',value)
                prior=rounded
        beds=defaultdict(int)
        for loc in locations.values():
            if loc['licensed_bed']:beds[loc['facility_id']]+=1
        for fid,n_beds in beds.items():
            amount=money(n_beds*n*Decimal(cfg['utilities_per_licensed_bed_day'])*(1+Decimal(cfg['annual_cost_escalation'])*(m.year-2023)))
            known=stamp(local(following(m)+timedelta(days=2),12))
            put('OVERHEAD',fid,centers[fid,'FACILITIES'],str(end),str(end),known,'capacity-utilities/'+fid+'/'+str(m),'OVERHEAD_DIRECT','AP',amount)
        m=following(m)
    revenue=defaultdict(lambda:{'first':'9999','known':'','gross':Decimal(0),'allowed':Decimal(0)})
    for r in tables['service_charge']:
        e=enc[r['encounter_version_id']]
        if r['service_to']<'2023-01-01':continue
        gross=Decimal(r['billed_amount']);allowed=money(gross*Decimal(payer[cov[e['coverage_version_id']]['payer_plan_id']]['allowed_factor']))
        v=revenue[e['facility_id'],r['cost_center_id'],r['service_to']];v['first']=min(v['first'],r['service_from']);v['known']=max(v['known'],r['export_available_at']);v['gross']+=gross;v['allowed']+=allowed
    for (fid,center,last),v in sorted(revenue.items()):
        source='charges/'+center+'/'+last;known=stamp(midnight(day(v['known'])+timedelta(days=1)))
        put('REVENUE',fid,center,v['first'],last,known,source,'AR','GROSS_REVENUE',v['gross'])
        put('REVENUE',fid,center,v['first'],last,known,source,'CONTRA_REVENUE','AR',v['gross']-v['allowed'])
    headers={r['claim_id']:r for r in tables['claim']}
    for h in headers.values():
        if h['carry_in']:
            fid=enc[h['encounter_version_id']]['facility_id']
            put('OPENING',fid,centers[fid,'ADMINISTRATION'],'2023-01-01','2023-01-01','2023-01-01T06:00:00Z','opening-claim-ar/'+fid,'AR','OPENING_EQUITY',h['opening_ar'])
    reversed_ids={r['reverses_claim_event_id'] for r in tables['claim_event'] if r['reverses_claim_event_id']}
    for r in tables['claim_event']:
        e=enc[headers[r['claim_id']]['encounter_version_id']];center=centers[e['facility_id'],'ADMINISTRATION'];service=str(day(r['occurred_at']))
        known=stamp(midnight(day(r['export_available_at'])+timedelta(days=1)))
        source='claim-events/'+center+'/'+service+'/'+str(day(r['export_available_at']))
        if r['claim_event_id'] in reversed_ids or r['reverses_claim_event_id']:source='claim-event-link/'+r['claim_event_id']
        for domain,debit,field in [('AR','CONTRA_REVENUE','contractual_adjustment_delta'),('AR','OTHER_EXPENSE','writeoff_delta'),('CASH','CASH','cash_delta')]:
            put(domain,e['facility_id'],center,service,service,known,source,debit,'AR',r[field])
    liabilities=defaultdict(Decimal)
    for key,amounts in list(expected.items()):
        for account,amount in amounts.items():
            if account in ('PAYROLL_PAYABLE','AP'):
                period='2022-12' if key[7].startswith('opening-payroll/') and key[6]<='2023-01-10T18:00:00Z' else key[3][:7]
                liabilities[key[1],period,account]-=amount
    for fid in sorted(r['facility_id'] for r in tables['facility']):
        put('OPENING',fid,centers[fid,'ADMINISTRATION'],'2023-01-01','2023-01-01','2023-01-01T06:00:00Z','opening-operating-cash/'+fid,'CASH','OPENING_EQUITY',cfg['opening_cash_per_facility'])
    disbursements=Decimal(0)
    for (fid,period,account),amount in sorted(liabilities.items()):
        paid=following(date.fromisoformat(period+'-01')).replace(day=cfg['payroll_settlement_day'] if account=='PAYROLL_PAYABLE' else cfg['supplier_settlement_day'])
        if paid>=date(2026,1,1) or not amount:continue
        disbursements+=amount;source=('payroll' if account=='PAYROLL_PAYABLE' else 'supplier')+'-settlement/'+fid+'/'+period
        put('CASH',fid,centers[fid,'ADMINISTRATION'],str(paid),str(paid),stamp(local(paid,12)),source,account,'CASH',amount)
    pools=defaultdict(Decimal);knowns={}
    for key,amounts in list(expected.items()):
        domain,fid,center,posted,first,last,known,source=key
        for account,amount in amounts.items():
            if account.endswith('_DIRECT'):
                k=(fid,center,posted[:7],account);pools[k]+=amount;knowns[k]=max(knowns.get(k,''),known)
    for (fid,center,period,account),amount in sorted(pools.items()):
        first=date.fromisoformat(period+'-01');last=following(first)-timedelta(days=1);known=max(close(first),knowns[fid,center,period,account])
        put('COST_POOL_CLOSE',fid,center,str(first),str(last),known,'pool-close/'+center+'/'+period+'/'+account.split('_')[0],account.replace('_DIRECT','_POOL'),account,amount)
    return {(*key[:4],bounds[key],*key[5:]):{a:v for a,v in amounts.items() if v} for key,amounts in expected.items() if any(amounts.values())},{'admin_salary':str(salary_total),'unfinished_shift_accrual':str(accrual_total),'opening_earned_payroll':str(opening_payroll),'treasury_disbursements':str(disbursements),'opening_operating_cash':str(Decimal(cfg['opening_cash_per_facility'])*len(tables['facility']))}


def allocation_weights(tables):
    """Reconstruct patient-month drivers without reading published allocations."""
    enc={r['encounter_version_id']:r for r in tables['encounter']};last={}
    for e in enc.values():
        if e['encounter_id'] not in last or e['revision_no']>last[e['encounter_id']]['revision_no']:last[e['encounter_id']]=e
    locations={r['location_id']:r for r in tables['location']};catalog={r['catalog_item_id']:r for r in tables['catalog_item']}
    centers={(r['facility_id'],r['cost_center_code'].split('-')[-1]):r['cost_center_id'] for r in tables['cost_center']}
    result=defaultdict(lambda:defaultdict(Decimal));ipd=defaultdict(lambda:defaultdict(Decimal));placed=defaultdict(list)
    for bid,eid,a,z in bed_intervals(tables['bed_event'],enc):
        placed[eid].append((instant(a),instant(z)))
        loc=locations[bid];cursor=instant(a);end=instant(z)
        while cursor<end:
            boundary=min(end,midnight(day(cursor)+timedelta(days=1)));hours=Decimal(str((boundary-cursor).total_seconds()))/3600;m=str(day(cursor))[:7]
            result[m,loc['cost_center_id'],'LABOR'][eid]+=hours
            if loc['cost_center_id']==centers[loc['facility_id'],'SURGERY']:result[m,centers[loc['facility_id'],'MEDICINE'],'LABOR'][eid]+=hours
            ipd[m,loc['facility_id']][eid]+=hours;cursor=boundary
    for eid,e in sorted(last.items()):
        if e['discharged_at'] and e['discharged_at']<'2023-01-01T06:00:00Z':continue
        if e['encounter_class']=='IPD':
            cursor=max(instant('2023-01-01T06:00:00Z'),instant(e['admitted_at']));end=instant(e['discharged_at']) if e['discharged_at'] else instant('2026-01-01T06:00:00Z');gaps=[]
            for a,z in sorted(placed[eid]):
                if a>cursor:gaps.append((cursor,a))
                cursor=max(cursor,z)
            if cursor<end:gaps.append((cursor,end))
            center=centers[e['facility_id'],'ED' if e['admission_source']=='ED' else 'MEDICINE']
            for a,z in gaps:
                cursor=a
                while cursor<z:
                    boundary=min(z,midnight(day(cursor)+timedelta(days=1)))
                    result[str(day(cursor))[:7],center,'LABOR'][eid]+=Decimal(str((boundary-cursor).total_seconds()))/3600;cursor=boundary
            continue
        cursor=max(instant('2023-01-01T06:00:00Z'),instant(e['arrival_at']));end=min(instant('2026-01-01T06:00:00Z'),instant(e['discharged_at'])) if e['discharged_at'] else instant('2026-01-01T06:00:00Z')
        while cursor<end:
            boundary=min(end,midnight(day(cursor)+timedelta(days=1)))
            result[str(day(cursor))[:7],locations[e['location_id']]['cost_center_id'],'LABOR'][eid]+=Decimal(str((boundary-cursor).total_seconds()))/3600;cursor=boundary
    clinical={r['clinical_event_version_id']:r for r in tables['clinical_event']}
    for r in clinical.values():
        if r['event_type']=='PROCEDURE' and catalog[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9') and '2023-01-01T06:00:00Z'<=r['occurred_at']<'2026-01-01T06:00:00Z':
            e=enc[r['encounter_version_id']]
            result[str(day(r['occurred_at']))[:7],centers[e['facility_id'],'OPERATING'],'LABOR'][e['encounter_id']]+=Decimal(str((instant(r['period_end_at'])-instant(r['occurred_at'])).total_seconds()))/60
    medication=defaultdict(lambda:defaultdict(Decimal));supply=defaultdict(lambda:defaultdict(Decimal));supply_amount=defaultdict(Decimal)
    for when,event,loc,code,item,qty,is_med,group in expected_uses(tables):
        eid=enc[clinical[event]['encounter_version_id']]['encounter_id']
        if is_med:medication[group][eid]+=qty
        else:supply[loc,item,str(day(when))][eid]+=qty
    for r in tables['inventory_movement']:
        if r['movement_type']!='CONSUME' or Decimal(r['nonpatient_waste_base']):continue
        center=locations[r['location_id']]['cost_center_id'];m=str(day(r['occurred_at']))[:7]
        if catalog[r['catalog_item_id']]['domain']=='MEDICATION':
            for eid,amount in partition(-Decimal(r['extended_cost']),medication[r['consumption_group_key']]).items():result[m,center,'DRUG'][eid]+=amount
        else:supply_amount[r['location_id'],r['catalog_item_id'],str(day(r['occurred_at']))]-=Decimal(r['extended_cost'])
    for (loc,item,d),value in sorted(supply_amount.items()):
        for eid,amount in partition(value,supply[loc,item,d]).items():result[d[:7],locations[loc]['cost_center_id'],'SUPPLY'][eid]+=amount
    for (m,fid),weights in ipd.items():result[m,centers[fid,'FACILITIES'],'OVERHEAD']=weights
    return result


def statistical_values(tables,period,known):
    enc={r['encounter_version_id']:r for r in tables['encounter']};locations={r['location_id']:r for r in tables['location']};values=defaultdict(lambda:defaultdict(Decimal))
    boundary=local(following(period))
    relevant=[event for event in tables['bed_event'] if instant(event['effective_at'])<boundary]
    for bid,eid,a,z in bed_intervals(relevant,enc,known):
        a=max(instant(a),local(period));z=min(instant(z),local(following(period)))
        if z>a:values[locations[bid]['cost_center_id']]['PATIENT_DAYS']+=Decimal(str((z-a).total_seconds()))/86400
    care={};staff={}
    for table,key,destination in [('encounter','encounter_id',care),('staff_shift','shift_id',staff)]:
        for r in tables[table]:
            if r['export_available_at']<=known and (r[key] not in destination or r['revision_no']>destination[r[key]]['revision_no']):destination[r[key]]=r
    for e in care.values():
        if e['encounter_class']=='IPD' and not e['carry_in'] and e['admitted_at'] and str(day(e['admitted_at']))[:7]==str(period)[:7]:values[locations[e['location_id']]['cost_center_id']]['ADMISSIONS']+=1
    for sid,r in sorted(staff.items()):
        if r['actual_start'] and r['actual_end']:
            a=instant(r['actual_start']);z=instant(r['actual_end']);first=max(a,local(period));last=min(z,local(following(period)))
            if last>first:values[r['cost_center_id']]['PRODUCTIVE_HOURS']+=Decimal(r['productive_hours'])*Decimal(str((last-first).total_seconds()))/Decimal(str((z-a).total_seconds()))
    for v in values.values():v['FTE']=v['PRODUCTIVE_HOURS']*12/2080
    return values


def planning_values(tables,cfg):
    """Separate reconstruction of prospective model and completed known history."""
    centers={r['cost_center_id']:r for r in tables['cost_center']};catalog={r['catalog_item_id']:r for r in tables['catalog_item']};history_cache={};worker_cache={};model_cache={}
    result={}
    for r in tables['finance_monthly']:
        if r['scenario'] not in ('BUDGET','FORECAST') or r['amount'] is None:continue
        known=r['published_at'];period=date.fromisoformat(r['accounting_month']);center=r['cost_center_id'];code=catalog[r['account_catalog_id']]['code']
        if known not in history_cache:
            observed=sorted({p['posting_date'][:7] for p in tables['financial_posting'] if p['known_from']<=known and p['posting_date'][:7]<known[:7]})[-3:];sums=defaultdict(Decimal)
            for p in tables['financial_posting']:
                if p['known_from']<=known and p['posting_date'][:7] in observed:sums[p['cost_center_id'],catalog[p['account_catalog_id']]['code']]+=Decimal(p['debit_amount'])-Decimal(p['credit_amount'])
            history_cache[known]=(observed,sums)
        if known not in worker_cache:
            replacement={}
            for w in tables['worker_assignment']:
                k=w['worker_id'],w['known_from'];replacement[k]=min(replacement.get(k,'9999'),w['export_available_at'])
            worker_cache[known]=[w for w in tables['worker_assignment'] if w['export_available_at']<=known and (not w['known_to'] or known<replacement.get((w['worker_id'],w['known_to']),'9999'))]
        cachekey=(known,str(period),center,code)
        if cachekey not in model_cache:
            unit=centers[center]['cost_center_code'].split('-')[-1];n=calendar.monthrange(period.year,period.month)[1];inflate=1+Decimal(cfg['annual_cost_escalation'])*(period.year-2023)
            season=Decimal('1.10') if period.month in (1,2,12) else Decimal('0.96') if period.month in (6,7,8) else Decimal(1);occupancy=Decimal(cfg['planning_occupancy']);gross=Decimal(0)
            if unit in ('MEDICINE','SURGERY','ICU'):gross=(4 if unit=='ICU' else 10)*n*occupancy*Decimal(cfg['prices']['BILL-ICU' if unit=='ICU' else 'BILL-ROOM'])*season
            elif unit=='ED':gross=n*Decimal(cfg['planning_ed_visits_per_day'])*Decimal(cfg['prices']['BILL-ED'])*season
            elif unit=='AMBULATORY':gross=n*Decimal(cfg['planning_opd_visits_per_day'])*Decimal(cfg['prices']['BILL-OPD'])
            elif unit=='OPERATING':gross=24*n*occupancy/Decimal(cfg['planning_mean_los_days'])*Decimal('.25')*Decimal(cfg['prices']['0FT44ZZ'])
            elif unit=='LABORATORY':gross=n*30*Decimal(cfg['prices']['LAB'])
            elif unit=='PHARMACY':gross=n*70*Decimal(cfg['prices']['PHARMACY'])
            if code=='GROSS_REVENUE':model=gross*inflate
            elif code=='CONTRA_REVENUE':model=gross*(1-Decimal(cfg['planning_allowed_factor']))*inflate
            elif code=='LABOR_POOL':
                eligible={}
                for w in worker_cache[known]:
                    if w['valid_from']<=stamp(local(period,12))<(w['valid_to'] or '9999') and (w['worker_id'] not in eligible or w['revision_no']>eligible[w['worker_id']]['revision_no']):eligible[w['worker_id']]=w
                model=Decimal(0)
                for w in eligible.values():
                    if w['cost_center_id']==center and w['hire_date']<=str(period)<(w['termination_date'] or '9999'):
                        model+=Decimal(w['fte'])*Decimal(w['hourly_cost_rate'])*2080/12*(1 if w['role'] in ('ADMIN','RN','PHYSICIAN') else Decimal('.08'))
                model*=inflate
            elif code=='DRUG_POOL':model=n*Decimal(32)*inflate if unit=='PHARMACY' else Decimal(0)
            elif code=='SUPPLY_POOL':model=n*Decimal(8)*inflate if unit=='LABORATORY' else n*Decimal(12)*inflate if unit=='OPERATING' else Decimal(0)
            elif code=='OVERHEAD_POOL':model=24*n*Decimal(cfg['utilities_per_licensed_bed_day'])*inflate if unit=='FACILITIES' else Decimal(0)
            else:raise ValueError('unregistered planning account')
            model_cache[cachekey]=model
        observed,sums=history_cache[known];model=model_cache[cachekey]
        prior=sums[center,code]*(-1 if code=='GROSS_REVENUE' else 1)
        estimate=Decimal('.70')*prior/len(observed)*Decimal('1.03')+Decimal('.30')*model if observed else model
        identity=center+'/'+code+'/'+str(period)+'/'+r['vintage_id'];noise=Decimal(draw(cfg['seed'],identity,'planning-uncertainty',upper=1001)-500)/10000
        result[r['finance_record_id']]=money(max(0,estimate*(1+noise)))
    return result
