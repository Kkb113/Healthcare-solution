"""Source predicates to daily double-entry journals and monthly expense pool closes."""
from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from .core import allocate_cents, instant, stable_id
from .financial_common import Context, START, CUTOFF, GRACE, at, cash, close, date_parts, day, delivered_assignments, latest, month, months, next_month, posting_date, stamp


def resource_entries(tables,cfg):
    """Policy projection: scalar source predicates, not an uncounted transaction store.

    A tuple is domain/facility/center/service date/known/group/debit/credit/amount.
    This transient projection is completely reconstructible from counted source rows.
    """
    c=Context(tables,cfg,'projection');entries=[];admin_capture=defaultdict(list)
    def emit(domain,fid,cc,service,known,key,debit,credit,amount):
        amount=Decimal(cash(amount))
        if amount:entries.append((domain,fid,cc,service,known,key,debit,credit,amount))
    for r in tables['inventory_movement']:
        loc=c.loc[r['location_id']];fid=loc['facility_id'];cc=loc['cost_center_id'];kind=r['movement_type'];v=Decimal(r['extended_cost'])
        if kind in ('TRANSFER_IN','TRANSFER_OUT','RETURN'):continue
        if kind=='OPENING':debit,credit,domain='INVENTORY','OPENING_EQUITY','OPENING';cc=c.centers[fid,'ADMINISTRATION']
        elif kind=='RECEIPT':debit,credit,domain='INVENTORY','AP','INVENTORY';cc=c.centers[fid,'ADMINISTRATION']
        elif kind=='CONSUME':
            debit='OTHER_EXPENSE' if Decimal(r['nonpatient_waste_base']) else 'DRUG_DIRECT' if c.cat[r['catalog_item_id']]['domain']=='MEDICATION' else 'SUPPLY_DIRECT'
            credit,domain='INVENTORY','INVENTORY';v=-v
        else:debit,credit,domain='OTHER_EXPENSE','INVENTORY','INVENTORY';v=-v
        emit(domain,fid,cc,day(r['occurred_at']).isoformat(),r['export_available_at'],r['posting_group_key']+'/'+cc+'/'+debit,debit,credit,v)
    histories=defaultdict(list)
    for r in tables['staff_shift']:histories[r['shift_id']].append(r)
    for sid,history in sorted(histories.items()):
        previous={}
        for r in sorted(history,key=lambda x:x['revision_no']):
            known=r['export_available_at'];w=c.workers[r['worker_assignment_id']];value=Decimal(r['loaded_cost'])
            if value:
                if r['actual_start'] and r['actual_end']:
                    weights=dict(date_parts(instant(r['actual_start']),instant(r['actual_end'])))
                else:weights={day(r['planned_start']).isoformat():Decimal(1)}
                split=allocate_cents(value,{d:str(q) for d,q in weights.items()})
            else:split={}
            for service in sorted(set(split)|set(previous)):
                delta=split.get(service,Decimal(0))-previous.get(service,Decimal(0))
                opening=service<'2023-01-01'
                emit('OPENING' if opening else 'WORKFORCE',w['facility_id'],r['cost_center_id'],service,known,
                     ('opening-payroll/' if opening else 'shift/')+r['cost_center_id']+'/'+service+'/'+day(known).isoformat(),
                     'OPENING_EQUITY' if opening else 'LABOR_DIRECT','PAYROLL_PAYABLE',delta)
                if w['role']=='ADMIN' and delta:admin_capture[w['worker_id'],service[:7]].append((w['facility_id'],r['cost_center_id'],known,delta))
            previous=split
        r=history and max(history,key=lambda x:x['revision_no'])
        if r['attendance_status']=='PUBLISHED' and r['actual_start'] and r['actual_end'] is None:
            w=c.workers[r['worker_assignment_id']];begin=instant(r['actual_start']);planned=instant(r['planned_end'])-instant(r['planned_start'])
            elapsed=Decimal(str((CUTOFF-begin).total_seconds()))/3600
            attended=elapsed*(1-Decimal('0.5')/(Decimal(str(planned.total_seconds()))/3600))
            amount=Decimal(cash(attended*Decimal(w['hourly_cost_rate'])))
            emit('ACCRUAL',w['facility_id'],r['cost_center_id'],'2025-12-31','2026-01-02T18:00:00Z',
                 'unfinished-shifts/'+r['cost_center_id'],'LABOR_DIRECT','PAYROLL_PAYABLE',amount)
    # ADMIN has sparse quarterly attendance capture, rather than a complete
    # demand roster. Top up to known salary entitlement and subtract captured
    # ADMIN shift expense so the same worker cost is never counted twice.
    workers=defaultdict(list);admin_ids={w['worker_id'] for w in c.workers.values() if w['role']=='ADMIN'}
    for r in tables['worker_assignment']:
        if r['worker_id'] in admin_ids:workers[r['worker_id']].append(r)
    for wid,history in sorted(workers.items()):
        for m in months():
            n=calendar.monthrange(m.year,m.month)[1];previous={}
            captured=admin_capture[wid,str(m)[:7]]
            points=sorted({close(m)}|{r['export_available_at'] for r in history if close(m)<r['export_available_at']<=GRACE and r['valid_from']<stamp(at(next_month(m)))}|
                          {known for _,_,known,_ in captured if close(m)<known<=GRACE})
            for known in points:
                values=defaultdict(Decimal);assertions=delivered_assignments(history,known)
                for i in range(n):
                    d=m+timedelta(days=i);noon=stamp(at(d,12))
                    valid=[r for r in assertions if r['valid_from']<=noon<(r['valid_to'] or '9999')
                        and r['hire_date']<=str(d)<(r['termination_date'] or '9999')]
                    if not valid:continue
                    w=max(valid,key=lambda r:r['revision_no'])
                    if w['role']!='ADMIN':continue
                    values[w['facility_id'],w['cost_center_id']]+=Decimal(w['fte'])*Decimal(w['hourly_cost_rate'])*2080/12/n
                rounded={key:Decimal(cash(v)) for key,v in values.items()}
                for fid,cc,available,amount in captured:
                    if available<=known:rounded[fid,cc]=rounded.get((fid,cc),Decimal(0))-amount
                for fid,cc in sorted(set(rounded)|set(previous)):
                    amount=rounded.get((fid,cc),Decimal(0))-previous.get((fid,cc),Decimal(0))
                    emit('WORKFORCE',fid,cc,str(next_month(m)-timedelta(days=1)),known,'salary/'+cc+'/'+str(m)+'/'+day(known).isoformat(),
                         'LABOR_DIRECT','PAYROLL_PAYABLE',amount)
                previous=rounded
    licensed=defaultdict(int)
    for r in tables['location']:
        if r['licensed_bed']:licensed[r['facility_id']]+=1
    for m in months():
        for fid,beds in sorted(licensed.items()):
            end=next_month(m)-timedelta(days=1);rate=Decimal(cfg['utilities_per_licensed_bed_day'])*(1+Decimal(cfg['annual_cost_escalation'])*(m.year-2023))
            emit('OVERHEAD',fid,c.centers[fid,'FACILITIES'],str(end),stamp(at(next_month(m)+timedelta(days=2),12)),
                 'capacity-utilities/'+fid+'/'+str(m),'OVERHEAD_DIRECT','AP',beds*calendar.monthrange(m.year,m.month)[1]*rate)
    return entries


def postings(tables,cfg,run_id):
    c=Context(tables,cfg,run_id);groups=defaultdict(lambda:defaultdict(Decimal));bounds={}
    def add(domain,fid,cc,service_from,service_to,known,source,debit,credit,value):
        value=Decimal(cash(value))
        if not value:return
        known=stamp(at(day(known)+timedelta(days=1))) if domain not in ('COST_POOL_CLOSE','REVENUE','AR','CASH','OPENING','ACCRUAL') and not source.startswith('salary/') else known
        posted=max('2023-01-01',posting_date(service_to,known)) if domain=='OPENING' else posting_date(service_to,known)
        # One daily source group per exact financial predicate. Keep the original
        # service range in the key for the service-to-posting-month bridge.
        key=(domain,fid,cc,posted,service_to,service_to,known,source)
        bounds[key]=min(bounds.get(key,service_from),service_from)
        groups[key][debit]+=value;groups[key][credit]-=value
    resource_source=resource_entries(tables,cfg)
    for domain,fid,cc,service,known,key,debit,credit,value in resource_source:
        add(domain,fid,cc,service,service,known,key,debit,credit,value)
    claimed={r['charge_id']:r for r in tables['claim_line']};headers={r['claim_id']:r for r in tables['claim']}
    revenue=defaultdict(lambda:{'first':'9999','known':'','gross':Decimal(0),'allowed':Decimal(0)})
    for r in tables['service_charge']:
        e=c.enc[r['encounter_version_id']]
        if r['service_to']<'2023-01-01':continue
        gross=Decimal(r['billed_amount']);estimate=Decimal(cash(gross*Decimal(c.payer(e)['allowed_factor'])))
        v=revenue[e['facility_id'],r['cost_center_id'],r['service_to']]
        v['first']=min(v['first'],r['service_from']);v['known']=max(v['known'],r['export_available_at']);v['gross']+=gross;v['allowed']+=estimate
    for (fid,cc,last),v in sorted(revenue.items()):
        source='charges/'+cc+'/'+last;k=stamp(at(day(v['known'])+timedelta(days=1)))
        add('REVENUE',fid,cc,v['first'],last,k,source,'AR','GROSS_REVENUE',v['gross'])
        add('REVENUE',fid,cc,v['first'],last,k,source,'CONTRA_REVENUE','AR',v['gross']-v['allowed'])
    for r in tables['claim']:
        if r['carry_in']:
            e=c.enc[r['encounter_version_id']];cc=c.centers[e['facility_id'],'ADMINISTRATION']
            add('OPENING',e['facility_id'],cc,'2023-01-01','2023-01-01',stamp(START),'opening-claim-ar/'+e['facility_id'],'AR','OPENING_EQUITY',r['opening_ar'])
    event_index={r['claim_event_id']:r for r in tables['claim_event']}
    reversed_events={r['reverses_claim_event_id'] for r in tables['claim_event'] if r['reverses_claim_event_id']}
    for r in tables['claim_event']:
        h=headers[r['claim_id']];e=c.enc[h['encounter_version_id']];fid=e['facility_id'];cc=c.centers[fid,'ADMINISTRATION']
        service=day(r['occurred_at']).isoformat();known=stamp(at(day(r['export_available_at'])+timedelta(days=1)))
        source='claim-events/'+cc+'/'+service+'/'+day(r['export_available_at']).isoformat()
        if r['claim_event_id'] in reversed_events or r['reverses_claim_event_id']:source='claim-event-link/'+r['claim_event_id']
        add('AR',fid,cc,service,service,known,source,'CONTRA_REVENUE','AR',r['contractual_adjustment_delta'])
        add('AR',fid,cc,service,service,known,source,'OTHER_EXPENSE','AR',r['writeoff_delta'])
        add('CASH',fid,cc,service,service,known,source,'CASH','AR',r['cash_delta'])
    rows=[]
    def materialize(key,amounts,pool=False):
        domain,fid,cc,posted,first,last,known,source=key;jid=stable_id('journal',*key)
        i=0
        for account,value in sorted(amounts.items()):
            if value==0:continue
            i+=1;pid=stable_id('posting',jid,i)
            rows.append(c.row('financial_posting',jid+'/'+str(i),known,posting_id=pid,journal_id=jid,line_no=i,facility_id=fid,cost_center_id=cc,
                account_catalog_id=c.code(account,posted),posting_date=posted,service_from=first,service_to=last,
                debit_amount=cash(max(value,0)),credit_amount=cash(max(-value,0)),currency='USD',source_domain=domain,source_group_key=source,
                allocation_pool_key=f'{posted[:7]}/{cc}/{account.split("_")[0]}' if pool and account.endswith('_POOL') else None,
                eligible_for_allocation=bool(pool and account.endswith('_POOL')),reverses_posting_id=None,known_from=known))
    for key,amounts in sorted(groups.items()):materialize((*key[:4],bounds[key],*key[5:]),amounts)
    # Treasury activity is explicitly generated from known obligations. December
    # obligations remain payable; January 2026 payments are not invented.
    liabilities=defaultdict(Decimal)
    for r in rows:
        account=c.cat[r['account_catalog_id']]['code']
        if account in ('PAYROLL_PAYABLE','AP'):
            period='2022-12' if r['source_group_key'].startswith('opening-payroll/') and r['known_from']<='2023-01-10T18:00:00Z' else r['posting_date'][:7]
            liabilities[r['facility_id'],period,account]+=Decimal(r['credit_amount'])-Decimal(r['debit_amount'])
    for fid in sorted(r['facility_id'] for r in tables['facility']):
        cc=c.centers[fid,'ADMINISTRATION']
        materialize(('OPENING',fid,cc,'2023-01-01','2023-01-01','2023-01-01',stamp(START),'opening-operating-cash/'+fid),
                    {'CASH':Decimal(cfg['opening_cash_per_facility']),'OPENING_EQUITY':-Decimal(cfg['opening_cash_per_facility'])})
    for (fid,period,account),value in sorted(liabilities.items()):
        paid=next_month(date.fromisoformat(period+'-01')).replace(day=cfg['payroll_settlement_day'] if account=='PAYROLL_PAYABLE' else cfg['supplier_settlement_day'])
        if paid>=date(2026,1,1) or value==0:continue
        cc=c.centers[fid,'ADMINISTRATION'];key=('payroll' if account=='PAYROLL_PAYABLE' else 'supplier')+'-settlement/'+fid+'/'+period
        materialize(('CASH',fid,cc,str(paid),str(paid),str(paid),stamp(at(paid,12)),key),{account:value,'CASH':-value})
    expenses=defaultdict(Decimal);knowns={}
    for r in rows:
        account=c.cat[r['account_catalog_id']]['code']
        if account not in ('LABOR_DIRECT','DRUG_DIRECT','SUPPLY_DIRECT','OVERHEAD_DIRECT'):continue
        key=(r['facility_id'],r['cost_center_id'],r['posting_date'][:7],account)
        expenses[key]+=Decimal(r['debit_amount'])-Decimal(r['credit_amount']);knowns[key]=max(knowns.get(key,''),r['known_from'])
    for (fid,cc,m,account),value in sorted(expenses.items()):
        if not value:continue
        first=date.fromisoformat(m+'-01');last=next_month(first)-timedelta(days=1);known=max(close(first),knowns[fid,cc,m,account])
        source='pool-close/'+cc+'/'+m+'/'+account.split('_')[0]
        materialize(('COST_POOL_CLOSE',fid,cc,str(last),str(first),str(last),known,source),{account:-value,account.replace('_DIRECT','_POOL'):value},True)
    source_index={(r['source_group_key'],r['account_catalog_id']):r for r in rows}
    for r in rows:
        if r['source_group_key'].startswith('claim-event-link/'):
            event=event_index[r['source_group_key'].split('/')[-1]]
            if event['reverses_claim_event_id']:
                original=source_index.get(('claim-event-link/'+event['reverses_claim_event_id'],r['account_catalog_id']))
                if original:r['reverses_posting_id']=original['posting_id']
    return {'tables':{'financial_posting':rows},'controls':{'journals':len({r['journal_id'] for r in rows}),'source_projection_rows':len(resource_source)}}
