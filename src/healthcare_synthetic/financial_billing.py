"""Selected facility-service billing and immutable original claim lifecycles."""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from .core import stable_id, instant
from .financial_common import Context, START, CUTOFF, at, cash, day, date_parts, month, stamp, quantity
from .operational_validation import bed_intervals


def billing(tables, cfg, run_id):
    c = Context(tables, cfg, run_id)
    additions = []
    for code, display in [('BILL-ROOM','Adult acute occupied room day'), ('BILL-ICU','Adult ICU occupied room day'),
                          ('BILL-ED','Emergency facility attendance'), ('BILL-OPD','Ambulatory facility attendance'),
                          ('BILL-HOLD','Extended monitored admission holding hour')]:
        additions.append(c.row('catalog_item', 'HOSPITAL_LOCAL/'+code, '2022-12-15T07:00:00Z',
            catalog_item_id=stable_id('billing_catalog', code), domain='PROCEDURE', code_system='HOSPITAL_LOCAL', code=code,
            display=display, version='SYNTHETIC-FACILITY-1', valid_from='2022-01-01', valid_to=None))
    extended = {**tables, 'catalog_item': tables['catalog_item']+additions}
    c = Context(extended, cfg, run_id)
    histories = defaultdict(list)
    for e in tables['encounter']: histories[e['encounter_id']].append(e)
    events = defaultdict(list)
    for r in tables['clinical_event']:
        if r['status']=='COMPLETED' and r['event_type'] in ('PROCEDURE','LAB_RESULT','MED_ADMIN','MED_DISPENSE'):
            events[c.enc[r['encounter_version_id']]['encounter_id']].append(r)
    beds = defaultdict(list)
    for bid,eid,start,end in bed_intervals(tables['bed_event'],c.enc): beds[eid].append((bid,start,end))
    bed_rows={r['bed_event_id']:r for r in tables['bed_event']};bed_knowledge=defaultdict(list);physical_carry_in=set()
    for r in tables['bed_event']:
        if r['event_type']=='OPENING' and r['occupancy_state']=='OCCUPIED' and r['encounter_version_id']:physical_carry_in.add(c.enc[r['encounter_version_id']]['encounter_id'])
        original=bed_rows.get(r['corrects_bed_event_id']) if r['corrects_bed_event_id'] else r
        if original and original['event_type'] in ('OPENING','OCCUPY','VACATE') and original['encounter_version_id']:
            bed_knowledge[c.enc[original['encounter_version_id']]['encounter_id']].append((r['effective_at'],r['export_available_at']))
    charges=[]

    def emit(e, category, code, units, first, last, cc, completed, event=None,dependent_known=None):
        if units<=0: return
        opening = bool(e['discharged_at'] and e['discharged_at']<stamp(START))
        known = max(stamp(completed), event['export_available_at'] if event else stamp(completed))
        if dependent_known:known=max(known,dependent_known)
        # Resolve the source encounter as available to billing, never a later correction.
        available = [x for x in histories[e['encounter_id']] if x['export_available_at']<=known]
        if not available:
            first_context=min(histories[e['encounter_id']],key=lambda x:x['export_available_at'])
            known=max(known,first_context['export_available_at']);available=[first_context]
        context=max(available,key=lambda x:x['revision_no'])
        key=f"{e['encounter_id']}/{category}/{cc}/{first}/{last}/{code}"
        price=Decimal(cfg['prices'].get(code,cfg['prices'].get(category,'190.00')))*(1+Decimal(cfg['annual_charge_escalation'])*max(0,first.year-2023))
        price=Decimal(cash(price));payer=c.payer(e)
        auth='NOT_REQUIRED'
        if payer['authorization_required'] and e['planned'] and (category=='ROOM' or code in cfg['authorization_service_codes']):
            auth=['APPROVED']*92+['PENDING']*4+['EXPIRED']*2+['DENIED']*2
            auth=auth[c.pick(e['encounter_id'],'authorization',100)]
        authorization_known=stamp(max(at(first)-timedelta(days=3), at(day(e['arrival_at']))-timedelta(days=1)))
        charges.append(c.row('service_charge',key,known,charge_id=stable_id('charge',key),encounter_version_id=context['encounter_version_id'],
            catalog_item_id=c.code(code,first),clinical_event_version_id=event['clinical_event_version_id'] if event else None,
            cost_center_id=cc,service_from=first.isoformat(),service_to=last.isoformat(),revenue_category=category,
            units=quantity(units),unit_code='holding_hours' if code=='BILL-HOLD' else 'room_days' if category=='ROOM' else 'base_units' if category=='PHARMACY' else 'services',
            unit_price=cash(price),billed_amount=cash(units*price),currency='USD',authorization_status=auth,
            authorization_known_at=authorization_known,reverses_charge_id=None,posting_group_key='service/'+e['encounter_id']+'/'+known+'/'+first.isoformat()+'/'+last.isoformat()))

    for eid,e in sorted(c.latest.items()):
        opening=bool(e['discharged_at'] and e['discharged_at']<stamp(START))
        if opening and c.payer(e)['payer_type']=='SELF_PAY': continue
        start=__import__('datetime').datetime.fromisoformat(e['arrival_at'].replace('Z','+00:00'))
        end=__import__('datetime').datetime.fromisoformat(e['discharged_at'].replace('Z','+00:00')) if e['discharged_at'] else CUTOFF
        if e['encounter_class']=='IPD' and (opening or beds[eid]):
            admitted=instant(e['admitted_at']) if opening else min(instant(a) for _,a,_ in beds[eid])
            room_end=end if opening else max(instant(z) for _,_,z in beds[eid])
            first=max(day(admitted),day(START)) if not opening else day(admitted)
            last=day(room_end)-timedelta(days=1)
            if day(admitted)==day(room_end) and eid not in physical_carry_in:last=day(admitted)
            grouped=defaultdict(list);d=first
            while d<=last and (opening or d<day(CUTOFF)):
                observed=stamp(max(at(d),admitted));matches=[b for b,a,z in beds[eid] if a<=observed<z]
                if not matches and not opening:
                    overlapping=sorted((a,b) for b,a,z in beds[eid] if instant(a)<at(d+timedelta(days=1)) and instant(z)>at(d))
                    if overlapping:matches=[overlapping[0][1]]
                    else:d+=timedelta(days=1);continue
                loc=c.loc[matches[0]] if matches else c.loc[e['location_id']]
                cc=loc['cost_center_id'];code='BILL-ICU' if loc['service_line']=='ICU' else 'BILL-ROOM'
                grouped[month(d),cc,code].append(d);d+=timedelta(days=1)
            for (_,cc,code),dates in sorted(grouped.items()):
                completed=min(room_end,at(max(dates)+timedelta(days=1)))
                dependent=max((known for effective,known in bed_knowledge[eid] if effective<=stamp(completed)),default=stamp(completed))
                emit(e,'ROOM',code,Decimal(len(dates)),min(dates),max(dates),cc,completed,dependent_known=dependent)
        elif e['encounter_class']!='IPD':
            if e['discharged_at'] is None:continue
            code='BILL-ED' if e['encounter_class']=='ED' else 'BILL-OPD'
            emit(e,'ED' if code=='BILL-ED' else 'AMBULATORY',code,Decimal(1),day(end),day(end),c.loc[e['location_id']]['cost_center_id'],end)
        if e['encounter_class']=='IPD' and not opening:
            placed=min((instant(a) for _,a,_ in beds[eid]),default=end)
            holding_end=min(end,placed);billable=max(START,instant(e['admitted_at'])+timedelta(seconds=int(Decimal(cfg['holding_bundled_hours'])*3600)))
            if holding_end>billable:
                by_month=defaultdict(lambda:{'seconds':Decimal(0),'dates':[]})
                for d,seconds in date_parts(billable,holding_end):by_month[d[:7]]['seconds']+=seconds;by_month[d[:7]]['dates'].append(d)
                total=Decimal(quantity(Decimal(str((holding_end-billable).total_seconds()))/3600));remaining=total
                for i,(period,group) in enumerate(sorted(by_month.items())):
                    units=remaining if i==len(by_month)-1 else Decimal(quantity(group['seconds']/3600));remaining-=units
                    first=__import__('datetime').date.fromisoformat(min(group['dates']));last=__import__('datetime').date.fromisoformat(max(group['dates']))
                    completed=min(holding_end,at(last+timedelta(days=1)))
                    known=max((known for effective,known in bed_knowledge[eid] if effective<=stamp(completed)),default=stamp(completed))
                    if not beds[eid] and e['discharged_at']:known=max(known,e['export_available_at'])
                    cc=c.centers[e['facility_id'],'ED' if e['admission_source']=='ED' else 'MEDICINE']
                    emit(e,'OTHER','BILL-HOLD',units,first,last,cc,completed,dependent_known=known)
        # Exactly one captured ancillary line, chosen from actual completed source services.
        actual=[r for r in events[eid] if (opening or stamp(START)<=r['occurred_at']<stamp(CUTOFF)) and r['export_available_at']<=stamp(CUTOFF+timedelta(days=4))]
        operative=[r for r in actual if c.cat[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9')]
        if operative:r=min(operative,key=lambda x:(x['occurred_at'],x['clinical_event_version_id']))
        elif actual:
            preferred=('LAB_RESULT','MED_ADMIN','PROCEDURE')[c.pick(eid,'ancillary-scope',3)]
            r=min(actual,key=lambda x:(x['event_type']!=preferred,x['occurred_at'],x['clinical_event_version_id']))
        else:continue
        code=c.cat[r['catalog_item_id']]['code'];category='LAB' if r['event_type']=='LAB_RESULT' else 'PHARMACY' if r['event_type'] in ('MED_ADMIN','MED_DISPENSE') else 'PROCEDURE'
        units=Decimal(r['consumed_base_quantity']) if category=='PHARMACY' and r['consumed_base_quantity'] else Decimal(1)
        d=day(r['occurred_at']);cc=c.centers[e['facility_id'], 'PHARMACY' if category=='PHARMACY' else 'LABORATORY' if category=='LAB' else 'OPERATING' if operative else c.cc[c.loc[e['location_id']]['cost_center_id']]['cost_center_code'].split('-')[-1]]
        emit(e,category,code,units,d,d,cc,__import__('datetime').datetime.fromisoformat((r['period_end_at'] or r['occurred_at']).replace('Z','+00:00')),r)
    return {'tables':{'catalog_item':extended['catalog_item'],'service_charge':charges},'controls':{'billing_catalog_rows_added':len(additions),'scope':'Selected ancillary itemization plus local facility charges'}}


def claims(tables,cfg,run_id):
    c=Context(tables,cfg,run_id);by_enc=defaultdict(list)
    for r in tables['service_charge']:by_enc[c.enc[r['encounter_version_id']]['encounter_id']].append(r)
    headers=[];lines=[];events=[];encounter_history=defaultdict(list)
    for r in tables['encounter']:encounter_history[r['encounter_id']].append(r)
    for eid,charges_ in sorted(by_enc.items()):
        e=c.latest[eid];payer=c.payer(e)
        if not e['discharged_at']:continue
        charges_=sorted(charges_,key=lambda r:(r['service_from'],r['charge_id']))
        opening=e['discharged_at']<stamp(START);cid=stable_id('claim',eid)
        ready=max([e['export_available_at']]+[r['export_available_at'] for r in charges_])
        created=instant(e['discharged_at'])
        submitted=instant(ready)+timedelta(days=2+c.pick(cid,'billing-lag',5))
        if opening:submitted=instant(ready)+timedelta(days=1)
        original=sum((Decimal(r['billed_amount']) for r in charges_),Decimal(0))
        expected=sum((Decimal(cash(Decimal(r['billed_amount'])*Decimal(payer['allowed_factor']))) for r in charges_),Decimal(0))
        oldcash=Decimal(cash(expected*Decimal('0.30'))) if opening else Decimal(0)
        oldwrite=Decimal(cash(expected*Decimal('0.02'))) if opening else Decimal(0)
        opening_ar=expected-oldcash-oldwrite if opening else Decimal(0)
        header=c.row('claim',cid,ready,claim_id=cid,encounter_version_id=e['encounter_version_id'],coverage_version_id=e['coverage_version_id'],
            claim_number='CLM-'+cid[-18:].upper(),service_from=min(r['service_from'] for r in charges_),service_to=max(r['service_to'] for r in charges_),
            created_at=stamp(created),first_submitted_at=stamp(submitted) if submitted<CUTOFF else None,original_billed_amount=cash(original),
            opening_ar=cash(opening_ar),opening_contractual_adjustments=cash(original-expected if opening else 0),opening_cash_collected=cash(oldcash),
            opening_writeoffs=cash(oldwrite),carry_in=opening,currency='USD')
        # Header context must exist by creation; use the most recent delivered care snapshot.
        available=[x for x in encounter_history[eid] if x['export_available_at']<=ready] if opening else None
        if opening and available: header['encounter_version_id']=max(available,key=lambda x:x['revision_no'])['encounter_version_id']
        if opening:
            header['recorded_at']=header['export_available_at']=stamp(START)
        headers.append(header);claim_lines=[]
        for i,r in enumerate(charges_,1):
            line=c.row('claim_line',cid+'/'+str(i),header['recorded_at'],claim_line_id=stable_id('claim_line',r['charge_id']),claim_id=cid,charge_id=r['charge_id'],line_no=i,
                billed_amount=r['billed_amount'],expected_allowed_amount=cash(Decimal(r['billed_amount'])*Decimal(payer['allowed_factor'])),currency='USD')
            lines.append(line);claim_lines.append(line)

        def event(kind,when,attempt=1,line=None,denial=None,reverse=None,**deltas):
            if when>=CUTOFF:return None
            key=cid+'/'+str(len(claim_events))+'/'+kind
            fields={n:cash(deltas.get(n,0)) for n in ('contractual_adjustment_delta','payer_liability_delta','patient_liability_delta','cash_delta','writeoff_delta','recognized_revenue_delta','ar_delta')}
            known=stamp(when+timedelta(hours=4+c.pick(key,'delivery',44)))
            row=c.row('claim_event',key,known,claim_event_id=stable_id('claim_event',key),claim_id=cid,claim_line_id=line,
                denial_catalog_id=denial,reverses_claim_event_id=reverse,event_type=kind,attempt_no=attempt,occurred_at=stamp(when),posting_group_key='claim-event/'+stable_id('claim_event',key),currency='USD',**fields)
            claim_events.append(row);events.append(row);return row

        claim_events=[];share=Decimal(cfg['patient_share'][payer['payer_type']])
        if opening:
            patient=Decimal(cash(expected*share));event('OPENING',START,0,payer_liability_delta=expected-patient,patient_liability_delta=patient)
            paid=event('PAYMENT',START+timedelta(days=10+c.pick(cid,'opening-settlement',100)),cash_delta=opening_ar,ar_delta=-opening_ar)
            continue
        if submitted>=CUTOFF:continue
        submission=event('SUBMITTED',submitted,ar_delta=expected)
        # The one immutable exported header carries the observed first-submission
        # field only once that submission is source-known. Earlier draft history
        # is intentionally uncaptured, rather than leaking a future actual.
        header['recorded_at']=header['export_available_at']=submission['export_available_at']
        for line in claim_lines:line['recorded_at']=line['export_available_at']=submission['export_available_at']
        # SELF_PAY is a patient-statement account in the institutional RCM
        # source, never an external payer submission/adjudication denominator.
        if payer['payer_type']=='SELF_PAY':
            review=submitted+timedelta(days=1)
            event('ADJUDICATED',review,patient_liability_delta=expected)
            collection=Decimal(cash(expected*Decimal('0.70'))) if c.pick(cid,'self-pay-collection',10)<7 else Decimal(0)
            if collection:event('PATIENT_PAYMENT',review+timedelta(days=20+c.pick(cid,'statement-lag',70)),cash_delta=collection,ar_delta=-collection)
            if c.pick(cid,'self-pay-credit-loss',5)==0:
                remaining=expected-collection
                if remaining:event('WRITEOFF',review+timedelta(days=180),patient_liability_delta=-remaining,writeoff_delta=remaining,ar_delta=-remaining)
            continue
        adjud=submitted+timedelta(days=14+c.pick(cid,'adjudication-delay',32))
        if adjud>=CUTOFF:continue
        charge_by_id={r['charge_id']:r for r in charges_};authorization={r['authorization_status'] for r in charges_}
        denied=bool(authorization&{'DENIED','EXPIRED'}) or c.pick(cid,'denial',10000)<(cfg['pending_authorization_denial_basis_points'] if 'PENDING' in authorization else cfg['denial_basis_points'])
        priority={'DENIED':3,'EXPIRED':2,'PENDING':1,'APPROVED':0,'NOT_REQUIRED':0}
        denied_line=max(claim_lines,key=lambda r:(priority[charge_by_id[r['charge_id']]['authorization_status']],Decimal(r['expected_allowed_amount']))) if denied else None
        denied_amount=Decimal(denied_line['expected_allowed_amount']) if denied else Decimal(0)
        # Payer review changes the prospective estimate by -2%..+2% on accepted lines.
        approved=expected-denied_amount
        adjust=Decimal(cash(approved*Decimal(c.pick(cid,'allowed-review',5)-2)/100))
        assigned=approved-adjust;patient=Decimal(cash(assigned*share));payer_amount=assigned-patient
        if assigned>0:
            event('ADJUDICATED',adjud,contractual_adjustment_delta=adjust,recognized_revenue_delta=-adjust,ar_delta=-adjust,
                  payer_liability_delta=payer_amount,patient_liability_delta=patient)
        if denied:
            status=charge_by_id[denied_line['charge_id']]['authorization_status']
            reason='DEN-02' if status=='EXPIRED' else 'DEN-01' if status in ('PENDING','DENIED') else ('DEN-08' if c.pick(cid,'denial-reason',2) else 'DEN-13')
            event('DENIED',adjud,line=denied_line['claim_line_id'],denial=c.code(reason,day(adjud)))
        paytime=adjud+timedelta(days=7+c.pick(cid,'payment-delay',45))
        fraction=Decimal('0.70') if c.pick(cid,'partial-payment',20)==0 else Decimal(1)
        amount=Decimal(cash(payer_amount*fraction))
        payment=event('PAYMENT',paytime,cash_delta=amount,ar_delta=-amount) if amount>0 else None
        if payment and fraction<1:
            remainder=payer_amount-amount
            event('PAYMENT',paytime+timedelta(days=45),cash_delta=remainder,ar_delta=-remainder)
        if payment and patient>0:
            path=c.pick(cid,'patient-collection',100)
            fully_paid_threshold=90 if patient<50 else 75 if patient<1000 else 55
            collection=patient if path<fully_paid_threshold else Decimal(cash(patient*Decimal('0.5'))) if path<90 else Decimal(0)
            if collection:event('PATIENT_PAYMENT',paytime+timedelta(days=20+c.pick(cid,'patient-collection-delay',50)),cash_delta=collection,ar_delta=-collection)
            remaining=patient-collection
            if remaining and c.pick(cid,'patient-credit-loss',100)<35:
                event('WRITEOFF',paytime+timedelta(days=180),patient_liability_delta=-remaining,writeoff_delta=remaining,ar_delta=-remaining)
        if denied:
            appeal=adjud+timedelta(days=12+c.pick(cid,'appeal-delay',14))
            if c.pick(cid,'appeal-path',5)<4:
                event('APPEALED',appeal,2,line=denied_line['claim_line_id'])
                event('RESUBMITTED',appeal+timedelta(days=2),2,line=denied_line['claim_line_id'])
                recovery=appeal+timedelta(days=24+c.pick(cid,'appeal-resolution',25))
                if c.pick(cid,'appeal-outcome',4)<3:
                    pat=Decimal(cash(denied_amount*share));payer_recovery=denied_amount-pat
                    event('ADJUDICATED',recovery,2,line=denied_line['claim_line_id'],payer_liability_delta=payer_recovery,patient_liability_delta=pat)
                    if payer_recovery>0:event('PAYMENT',recovery+timedelta(days=15),2,line=denied_line['claim_line_id'],cash_delta=payer_recovery,ar_delta=-payer_recovery)
                else:event('WRITEOFF',recovery,2,line=denied_line['claim_line_id'],writeoff_delta=denied_amount,ar_delta=-denied_amount)
        if payment and c.pick(cid,'payment-correction',500)==0:
            correction=paytime+timedelta(days=15)
            kind='REFUND' if c.pick(cid,'correction-kind',2) else 'REVERSAL'
            event(kind,correction,reverse=payment['claim_event_id'],cash_delta=-amount,ar_delta=amount)
            event('PAYMENT',correction+timedelta(days=7),cash_delta=amount,ar_delta=-amount)
    return {'tables':{'claim':headers,'claim_line':lines,'claim_event':events},'controls':{'originals':len(headers),'original_identity_not_attempts':True}}
