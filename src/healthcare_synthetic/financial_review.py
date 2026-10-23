"""Content-bound finance traces with named synthetic patients and complete claim events."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from decimal import Decimal

from .core import age_on, digest
from .financial_oracles import day


def render_financial(tables,cfg):
    enc={r['encounter_version_id']:r for r in tables['encounter']};patients={r['patient_version_id']:r for r in tables['patient']}
    coverage={r['coverage_version_id']:r for r in tables['patient_coverage']};payers={r['payer_plan_id']:r for r in tables['payer_plan']}
    facilities={r['facility_id']:r for r in tables['facility']};cat={r['catalog_item_id']:r for r in tables['catalog_item']}
    charges={r['charge_id']:r for r in tables['service_charge']};events=defaultdict(list);lines=defaultdict(list);alloc=defaultdict(list)
    journals=defaultdict(list);sources=defaultdict(set);postings={r['posting_id']:r for r in tables['financial_posting']}
    centers={(r['facility_id'],r['cost_center_code'].split('-')[-1]):r['cost_center_id'] for r in tables['cost_center']}
    reversed_events={r['reverses_claim_event_id'] for r in tables['claim_event'] if r['reverses_claim_event_id']}
    for r in tables['financial_posting']:journals[r['journal_id']].append(r);sources[r['source_group_key']].add(r['journal_id'])
    for r in tables['claim_event']:events[r['claim_id']].append(r)
    for r in tables['claim_line']:lines[r['claim_id']].append(r)
    for r in tables['cost_allocation']:
        if r['encounter_version_id']:alloc[enc[r['encounter_version_id']]['encounter_id']].append(r)
    headers=sorted(tables['claim'],key=lambda r:r['claim_id']);chosen=[];tags={}
    strata=[('refund',lambda h:any(r['event_type']=='REFUND' for r in events[h['claim_id']])),
        ('reversal',lambda h:any(r['event_type']=='REVERSAL' for r in events[h['claim_id']])),
        ('appeal_recovery',lambda h:any(r['attempt_no']==2 and r['event_type']=='PAYMENT' for r in events[h['claim_id']])),
        ('final_writeoff',lambda h:any(r['event_type']=='WRITEOFF' and r['attempt_no']>1 for r in events[h['claim_id']])),
        ('pending_denial',lambda h:any(r['event_type']=='DENIED' for r in events[h['claim_id']]) and not any(r['attempt_no']==2 for r in events[h['claim_id']])),
        ('patient_payment',lambda h:any(r['event_type']=='PATIENT_PAYMENT' for r in events[h['claim_id']])),
        ('patient_credit_loss',lambda h:any(r['event_type']=='WRITEOFF' and Decimal(r['patient_liability_delta'])<0 for r in events[h['claim_id']])),
        ('holding_no_room',lambda h:enc[h['encounter_version_id']]['encounter_class']=='IPD' and not any(charges[r['charge_id']]['revenue_category']=='ROOM' for r in lines[h['claim_id']])),
        ('draft',lambda h:h['first_submitted_at'] is None),('opening',lambda h:h['carry_in']),
        ('cross_month',lambda h:h['service_from'][:7]!=h['service_to'][:7]),
        ('open_receivable',lambda h:Decimal(h['opening_ar'])+sum((Decimal(r['ar_delta']) for r in events[h['claim_id']]),Decimal(0))>0)]
    for p in ('COMMERCIAL','MEDICARE','MEDICAID','SELF_PAY'):strata.append((p,lambda h,p=p:payers[coverage[h['coverage_version_id']]['payer_plan_id']]['payer_type']==p))
    for service in ('IPD','ED','OPD'):strata.append((service,lambda h,service=service:enc[h['encounter_version_id']]['encounter_class']==service))
    for label,predicate in strata:
        candidates=[h for h in headers if predicate(h)]
        if not candidates:raise ValueError('financial review stratum has no grounded case: '+label)
        take=0
        for h in candidates:
            if h['claim_id'] not in chosen:chosen.append(h['claim_id']);tags[h['claim_id']]=label;take+=1
            if take==3:break
    for h in headers:
        if len(chosen)>=cfg['review_cases']:break
        if h['claim_id'] not in chosen:chosen.append(h['claim_id']);tags[h['claim_id']]='normal'
    chosen=chosen[:cfg['review_cases']];index={r['claim_id']:r for r in headers};remembered={}
    pks={'patient':'patient_version_id','encounter':'encounter_version_id','claim':'claim_id','claim_line':'claim_line_id','claim_event':'claim_event_id','service_charge':'charge_id','cost_allocation':'allocation_id','financial_posting':'posting_id','patient_coverage':'coverage_version_id','payer_plan':'payer_plan_id','clinical_event':'clinical_event_version_id'}
    clinical={r['clinical_event_version_id']:r for r in tables['clinical_event']}
    def remember(table,row):remembered[table,row[pks[table]]]=row
    body=['# Synthetic financial trace review','',
          'User-designated synthetic finance review. Selected facility services and captured costs; simplified accounting, not independent accountant/clinical certification.',
          'Amounts are USD. Original claims retain all attempts. Allocation versions below must be selected by run, never added together.','']
    for i,cid in enumerate(chosen,1):
        h=index[cid];e=enc[h['encounter_version_id']];p=patients[e['patient_version_id']];payer=payers[coverage[h['coverage_version_id']]['payer_plan_id']]
        for t,r in [('patient',p),('encounter',e),('claim',h),('patient_coverage',coverage[h['coverage_version_id']]),('payer_plan',payer)]:remember(t,r)
        journal_ids=set()
        if h['carry_in']:journal_ids.update(sources['opening-claim-ar/'+e['facility_id']])
        age=age_on(p['birth_date'],str(day(e['arrival_at'])));balance=Decimal(h['opening_ar'])
        body += [f"## Trace {i}: {p['given_name']} {p['family_name']} ({age}) - {tags[cid]}",'',
            f"{facilities[e['facility_id']]['facility_name']}; {e['encounter_class']}; arrival {e['arrival_at']}; discharge {e['discharged_at'] or 'OPEN'}; {payer['payer_name']} / {payer['payer_type']}.",
            f"Original {h['claim_number']} ({cid}); services {h['service_from']} through {h['service_to']}; created {h['created_at']}; first submitted {h['first_submitted_at'] or 'DRAFT at cutoff'}.",
            f"Original billed {h['original_billed_amount']}; opening AR {h['opening_ar']}, historical contractual/cash/writeoff {h['opening_contractual_adjustments']}/{h['opening_cash_collected']}/{h['opening_writeoffs']}."]
        for line in sorted(lines[cid],key=lambda r:r['line_no']):
            charge=charges[line['charge_id']];remember('claim_line',line);remember('service_charge',charge)
            journal_ids.update(sources['charges/'+charge['cost_center_id']+'/'+charge['service_to']])
            if charge['clinical_event_version_id']:remember('clinical_event',clinical[charge['clinical_event_version_id']])
            body += [f"- Line {line['line_no']}: {cat[charge['catalog_item_id']]['display']}; {charge['revenue_category']}, {charge['service_from']}..{charge['service_to']}; {charge['units']} {charge['unit_code']} × {charge['unit_price']} = {charge['billed_amount']}; prospective allowed {line['expected_allowed_amount']}; auth {charge['authorization_status']} known {charge['authorization_known_at']}; actual event {charge['clinical_event_version_id'] or 'declared facility interval'}."]
        for r in sorted(events[cid],key=lambda r:(r['occurred_at'],r['claim_event_id'])):
            remember('claim_event',r);balance+=Decimal(r['ar_delta'])
            source='claim-events/'+centers[e['facility_id'],'ADMINISTRATION']+'/'+str(day(r['occurred_at']))+'/'+str(day(r['export_available_at']))
            if r['claim_event_id'] in reversed_events or r['reverses_claim_event_id']:source='claim-event-link/'+r['claim_event_id']
            journal_ids.update(sources[source])
            body += [f"- {r['occurred_at']} {r['event_type']} attempt {r['attempt_no']}; line {r['claim_line_id'] or 'header'}; denial {cat[r['denial_catalog_id']]['display'] if r['denial_catalog_id'] else 'none'}; deltas contract/payer/patient/cash/writeoff/revenue/AR {r['contractual_adjustment_delta']}/{r['payer_liability_delta']}/{r['patient_liability_delta']}/{r['cash_delta']}/{r['writeoff_delta']}/{r['recognized_revenue_delta']}/{r['ar_delta']}; balance {balance:.2f}; delivered {r['export_available_at']}; reverses {r['reverses_claim_event_id'] or 'none'}."]
        for r in sorted(alloc[e['encounter_id']],key=lambda r:(r['accounting_month'],r['cost_category'],r['known_from'],r['allocation_id'])):
            remember('cost_allocation',r)
            journal_ids.add(postings[r['posting_id']]['journal_id'])
            body += [f"- Cost {r['accounting_month']} {r['cost_category']} {r['allocated_amount']}; source pool posting {r['posting_id']}; driver {r['driver_quantity']} {r['driver_unit']}; share {r['allocation_share']}; run {r['allocation_run_id']} available {r['known_from']}; supersedes {r['supersedes_run_id'] or 'none'}."]
        body+=['- Reconciled GL source groups below can include other patients; each entire journal is shown, not charged again to this patient.']
        for jid in sorted(journal_ids):
            for posting in sorted(journals[jid],key=lambda r:r['line_no']):
                remember('financial_posting',posting)
                body += [f"  Journal {jid} line {posting['line_no']}: {cat[posting['account_catalog_id']]['code']} Dr {posting['debit_amount']} Cr {posting['credit_amount']}; posted {posting['posting_date']}; service {posting['service_from']}..{posting['service_to']}; known {posting['known_from']}; source {posting['source_group_key']}; allocatable {posting['eligible_for_allocation']}; reverses {posting['reverses_posting_id'] or 'none'}."]
        body+=['']
    text='\n'.join(body).rstrip()+'\n';facts=[{'table':t,'key':key,'row':row} for (t,key),row in sorted(remembered.items())]
    selection={'cases':len(chosen),'claim_ids':chosen,'strata':dict(sorted(CounterLike(tags[cid] for cid in chosen).items())),
               'sample_sha256':hashlib.sha256(text.encode()).hexdigest(),'selected_facts_sha256':digest(facts),'mirror_rows':len(facts),'mirror_bytes':len(text.encode())}
    return text,selection


def CounterLike(values):
    result={}
    for value in values:result[value]=result.get(value,0)+1
    return result


def review_gate(selection,decision):
    passed=bool(decision and decision.get('status')=='APPROVED' and decision.get('review_scope')=='USER_DESIGNATED_SYNTHETIC_FINANCE_REVIEW'
        and decision.get('independent_accountant_endorsement') is False and decision.get('cases_reviewed',0)>=50
        and decision.get('sample_sha256')==selection['sample_sha256'] and decision.get('selected_facts_sha256')==selection['selected_facts_sha256']
        and not decision.get('unresolved_critical_findings'))
    return {'status':'PASS' if passed else 'PENDING_REVIEW','cases':selection['cases'],'sample_sha256':selection['sample_sha256'],'independent_accountant_endorsement':False}
