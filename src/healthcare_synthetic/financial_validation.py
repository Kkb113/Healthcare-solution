"""Financial invariants over canonical facts, independently of their generators."""
from __future__ import annotations

import calendar
import json
import logging
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from .core import instant, digest
from .financial_oracles import expected_journals, allocation_weights, statistical_values, planning_values, money, partition, day, local, following, close, stamp
from .financial_room_validation import room_scope,holding_scope

START='2023-01-01T06:00:00Z';CUTOFF='2026-01-01T06:00:00Z';GRACE='2026-01-10T23:59:59Z'
FINANCIAL=('service_charge','claim','claim_line','claim_event','financial_posting','cost_allocation','finance_monthly')


class FinancialValidator:
    def __init__(self,tables,cfg,schema):
        self.t,self.cfg,self.schema=tables,cfg,schema
        self.cat={r['catalog_item_id']:r for r in tables['catalog_item']};self.enc={r['encounter_version_id']:r for r in tables['encounter']}
        self.cc={r['cost_center_id']:r for r in tables['cost_center']};self.cover={r['coverage_version_id']:r for r in tables['patient_coverage']}
        self.pay={r['payer_plan_id']:r for r in tables['payer_plan']};self.headers={r['claim_id']:r for r in tables['claim']}
        self.charges={r['charge_id']:r for r in tables['service_charge']};self.lines={r['claim_line_id']:r for r in tables['claim_line']}
        self.events={r['claim_event_id']:r for r in tables['claim_event']};self.postings={r['posting_id']:r for r in tables['financial_posting']}
        self.metrics={}

    def need(self,ok,message):
        if not ok:raise ValueError(message)

    def check_schema(self):
        indexes={t['name']:{r[t['primary_key'][0]] for r in self.t[t['name']]} for t in self.schema['tables']}
        for t in self.schema['tables']:
            if t['name'] not in FINANCIAL:continue
            rows=self.t[t['name']];columns={c['name']:c for c in t['columns']};seen=set();source_seen=set();uniques=[set() for _ in t['unique_keys']]
            self.need(len(rows)<=t['planned_rows'],'table record allowance exceeded: '+t['name'])
            for r in rows:
                self.need(set(r)==set(columns),'financial schema differs: '+t['name'])
                key=r[t['primary_key'][0]];self.need(key not in seen,'duplicate financial identity');seen.add(key)
                sourcekey=r['source_system'],r['source_record_id'];self.need(sourcekey not in source_seen,'duplicate source namespace/key');source_seen.add(sourcekey)
                for i,uk in enumerate(t['unique_keys']):
                    values=tuple(r[x] for x in uk);self.need(values not in uniques[i],'duplicate financial unique key');uniques[i].add(values)
                for name,c in columns.items():
                    value=r[name]
                    if value is None:self.need(c['nullable'],'null required field '+name);continue
                    self.need(not isinstance(value,(dict,list)),'nested financial facts are forbidden')
                    if 'allowed_values' in c:self.need(value in c['allowed_values'],'invalid financial enum '+name)
                    if 'references' in c:
                        target,field=c['references'].split('.');self.need(value in indexes[target],'orphan financial foreign key '+name)
                    typ=c['type']
                    if typ.startswith('DECIMAL'):
                        scale=int(typ.split(',')[1].rstrip(')'));self.need(isinstance(value,str) and re.fullmatch(r'-?\d+\.\d{'+str(scale)+'}',value),'wrong stored financial decimal precision '+name)
                    elif typ=='TIMESTAMP':instant(value)
                    elif typ=='DATE':date.fromisoformat(value)
                    elif typ=='INT':self.need(type(value) is int,'wrong integer type')
                    elif typ=='BOOLEAN':self.need(type(value) is bool,'wrong boolean type')
                self.need(r['recorded_at']<=r['export_available_at']<=GRACE,'financial source clock invalid')
                if 'currency' in r:self.need(r['currency']=='USD','unexpected monetary unit')
        self.need(1000000<=sum(map(len,self.t.values()))<=1995215 and len(self.t)==25,'full financial table/record budget differs')
        self.need(len(self.t['catalog_item'])==3005,'explicit five-row billing catalog amendment differs')

    def check_charges(self):
        clinical={r['clinical_event_version_id']:r for r in self.t['clinical_event']};base=Counter();gross=Decimal(0);rooms=room_scope(self.t);observed_rooms={}
        holding=holding_scope(self.t,self.cfg);observed_holding={}
        for r in self.charges.values():
            e=self.enc[r['encounter_version_id']];category=r['revenue_category'];item=self.cat[r['catalog_item_id']]
            self.need(r['service_from']<=r['service_to'] and r['service_from'][:7]==r['service_to'][:7],'charge crosses accounting month')
            self.need(self.cc[r['cost_center_id']]['facility_id']==e['facility_id'],'charge responsibility entity differs')
            self.need(item['valid_from']<=r['service_from']<(item['valid_to'] or '9999'),'billing catalog version not valid for service')
            self.need(Decimal(r['units'])>0 and Decimal(r['billed_amount'])==money(Decimal(r['units'])*Decimal(r['unit_price'])),'charge arithmetic differs')
            price=Decimal(self.cfg['prices'].get(item['code'],self.cfg['prices'].get(category,'190.00')))*(1+Decimal(self.cfg['annual_charge_escalation'])*max(0,int(r['service_from'][:4])-2023))
            self.need(Decimal(r['unit_price'])==money(price),'charge price not from the declared service/date contract')
            self.need(r['authorization_known_at']<=r['export_available_at'],'authorization is future knowledge')
            required=self.pay[self.cover[e['coverage_version_id']]['payer_plan_id']]['authorization_required'] and e['planned'] and (category=='ROOM' or item['code'] in self.cfg['authorization_service_codes'])
            self.need((r['authorization_status']!='NOT_REQUIRED')==bool(required),'authorization requirements do not match elective service and payer policy')
            self.need(e['export_available_at']<=r['export_available_at'],'charge uses unavailable encounter context')
            if category in ('ED','AMBULATORY','ROOM'):
                self.need(item['code'] in ('BILL-ROOM','BILL-ICU','BILL-ED','BILL-OPD') and item['code_system']=='HOSPITAL_LOCAL','facility fee uses a misleading clinical code')
                base[e['encounter_id']]+=1
                if category=='ROOM':
                    key=e['encounter_id'],r['cost_center_id'],r['service_from'][:7],item['code']
                    self.need(key in rooms and key not in observed_rooms,'room day/center/category scope is duplicate or untraceable')
                    expected=rooms[key];observed_rooms[key]=r
                    self.need(Decimal(r['units'])==expected['units'] and r['service_from']==expected['first'] and r['service_to']==expected['last'],'room day quantity/interval differs from actual admission and occupied bed')
                    self.need(r['export_available_at']>=expected['known'],'room charge uses unavailable occupancy knowledge')
            if r['clinical_event_version_id']:
                event=clinical[r['clinical_event_version_id']]
                self.need(self.enc[event['encounter_version_id']]['encounter_id']==e['encounter_id'] and event['status']=='COMPLETED','charge refers to unperformed/unrelated care')
                self.need(event['export_available_at']<=r['export_available_at'] and str(day(event['occurred_at']))==r['service_from'],'charge precedes the actual billable event')
                self.need(r['catalog_item_id']==event['catalog_item_id'],'ancillary catalog does not match source event')
                if category=='PHARMACY' and event['consumed_base_quantity']:self.need(r['units']==event['consumed_base_quantity'],'pharmacy charge quantity not from actual issue')
            if item['code']=='BILL-HOLD':
                key=e['encounter_id'],r['cost_center_id'],r['service_from'][:7]
                self.need(category=='OTHER' and r['unit_code']=='holding_hours' and key in holding and key not in observed_holding,'holding charge scope/unit/identity differs')
                expected=holding[key];observed_holding[key]=r
                self.need(Decimal(r['units'])==expected['units'] and r['service_from']==expected['first'] and r['service_to']==expected['last'],'holding hours do not follow observed care, placement and bundled allowance')
                self.need(r['export_available_at']>=expected['known'],'holding charge precedes required source knowledge')
            if r['service_to']>='2023-01-01':gross+=Decimal(r['billed_amount'])
        latest={}
        for r in self.t['encounter']:
            if r['encounter_id'] not in latest or r['revision_no']>latest[r['encounter_id']]['revision_no']:latest[r['encounter_id']]=r
        current={r['encounter_id'] for r in latest.values() if r['discharged_at'] and r['discharged_at']>=START and r['encounter_class']!='IPD'}|{key[0] for key in rooms if rooms[key]['last']>='2023-01-01'}
        self.need(set(observed_rooms)==set(rooms),'billable occupied room scope is missing')
        self.need(set(observed_holding)==set(holding),'billable extended holding scope is missing')
        self.need(current<=set(base),'intersecting encounter has no facility/room charge')
        self.metrics.update(billed_selected_services=str(gross),charged_encounters=len(base))

    def check_claims(self):
        by_claim=defaultdict(list);used=set()
        for line in self.lines.values():
            h=self.headers[line['claim_id']];charge=self.charges[line['charge_id']];e=self.enc[h['encounter_version_id']]
            self.need(line['charge_id'] not in used,'charge duplicated across original claims');used.add(line['charge_id'])
            self.need(self.enc[charge['encounter_version_id']]['encounter_id']==e['encounter_id'],'claim line belongs to another encounter')
            self.need(line['billed_amount']==charge['billed_amount'],'claim line and charge total differ')
            payer=self.pay[self.cover[h['coverage_version_id']]['payer_plan_id']]
            self.need(Decimal(line['expected_allowed_amount'])==money(Decimal(charge['billed_amount'])*Decimal(payer['allowed_factor'])),'prospective reimbursement estimate differs')
            by_claim[h['claim_id']].append(line)
        for h in self.headers.values():
            rows=by_claim[h['claim_id']];e=self.enc[h['encounter_version_id']]
            self.need(rows and sum((Decimal(r['billed_amount']) for r in rows),Decimal(0))==Decimal(h['original_billed_amount']),'claim header does not equal its original lines')
            self.need(sorted(r['line_no'] for r in rows)==list(range(1,len(rows)+1)),'claim line sequence invalid')
            self.need(h['coverage_version_id']==e['coverage_version_id'],'claim coverage changed from its care source')
            self.need(h['created_at']<=h['recorded_at'] and e['export_available_at']<=h['export_available_at'],'claim uses unavailable source context')
            self.need(h['first_submitted_at'] is None or h['created_at']<=h['first_submitted_at']<CUTOFF,'submission outside observed business window')
            if h['carry_in']:
                self.need(Decimal(h['opening_ar'])==Decimal(h['original_billed_amount'])-Decimal(h['opening_contractual_adjustments'])-Decimal(h['opening_cash_collected'])-Decimal(h['opening_writeoffs'])>0,'opening AR components do not reconcile')
                self.need(e['discharged_at']<START,'opening claim has current-period care')
            else:self.need(all(Decimal(h[n])==0 for n in ('opening_ar','opening_contractual_adjustments','opening_cash_collected','opening_writeoffs')),'new claim carries fabricated opening balances')
        self.metrics.update(original_claims=len(self.headers),carry_in_claims=sum(h['carry_in'] for h in self.headers.values()),unclaimed_service_lines=len(self.charges)-len(used))

    def check_events(self):
        by_claim=defaultdict(list);reversed_ids=set();types=Counter()
        for r in self.events.values():
            by_claim[r['claim_id']].append(r);types[r['event_type']]+=1
            self.need(START<=r['occurred_at']<CUTOFF and r['occurred_at']<=r['recorded_at'],'claim event/knowledge clock outside scope')
            if r['claim_line_id']:self.need(self.lines[r['claim_line_id']]['claim_id']==r['claim_id'],'event line belongs to another original claim')
            kind=r['event_type'];cash_=Decimal(r['cash_delta']);contract=Decimal(r['contractual_adjustment_delta']);write=Decimal(r['writeoff_delta']);ar=Decimal(r['ar_delta']);revenue=Decimal(r['recognized_revenue_delta'])
            if kind in ('OPENING','DENIED','APPEALED','RESUBMITTED'):self.need(cash_==contract==write==ar==revenue==0,'state event creates an unexplained financial movement')
            if kind=='OPENING':self.need(r['attempt_no']==0 and self.headers[r['claim_id']]['carry_in'],'opening asserted as current activity')
            else:self.need(r['attempt_no']>=1,'invalid claim attempt')
            if kind=='SUBMITTED':self.need(cash_==contract==write==revenue==0,'submission recognizes new revenue/cash')
            if kind=='ADJUDICATED':self.need(ar==-contract and revenue==-contract and cash_==write==0,'adjudication adjustment categories fail reconciliation')
            if kind in ('PAYMENT','PATIENT_PAYMENT'):self.need(cash_>0 and ar==-cash_ and contract==write==revenue==0,'payment confuses cash, revenue or liability')
            if kind=='WRITEOFF':self.need(write>0 and ar==-write and cash_==contract==revenue==0,'credit loss/writeoff policy differs')
            if kind=='DENIED':self.need(r['denial_catalog_id'] and self.cat[r['denial_catalog_id']]['domain']=='DENIAL' and r['claim_line_id'],'denial has no valid line-level reason')
            if kind=='DENIED':
                status=self.charges[self.lines[r['claim_line_id']]['charge_id']]['authorization_status'];reason=self.cat[r['denial_catalog_id']]['code']
                if status=='EXPIRED':self.need(reason=='DEN-02','expired authorization has wrong denial reason')
                elif status in ('PENDING','DENIED'):self.need(reason=='DEN-01','authorization issue has wrong denial reason')
            if kind in ('REFUND','REVERSAL'):
                old=self.events.get(r['reverses_claim_event_id']);self.need(old and old['claim_id']==r['claim_id'] and old['occurred_at']<r['occurred_at'],'unlinked or noncausal cash reversal/refund')
                self.need(old['claim_event_id'] not in reversed_ids,'same receipt reversed more than once');reversed_ids.add(old['claim_event_id'])
                self.need(cash_==-Decimal(old['cash_delta'])<0 and ar==-cash_ and contract==write==revenue==0,'signed refund/reversal is not an opposite receipt')
        closing=Decimal(0);open_count=0
        line_by_claim=defaultdict(list)
        for r in self.lines.values():line_by_claim[r['claim_id']].append(r)
        for cid,h in self.headers.items():
            rows=sorted(by_claim[cid],key=lambda r:(r['occurred_at'],r['claim_event_id']));submitted=[r for r in rows if r['event_type']=='SUBMITTED']
            expected=sum((Decimal(r['expected_allowed_amount']) for r in line_by_claim[cid]),Decimal(0))
            self.need(len(submitted)==int(not h['carry_in'] and h['first_submitted_at'] is not None),'original submission count/denominator differs')
            if submitted:self.need(Decimal(submitted[0]['ar_delta'])==expected and submitted[0]['occurred_at']==h['first_submitted_at'],'submission does not transfer prospective unbilled AR once')
            balance=Decimal(h['opening_ar'])
            for r in rows:
                balance+=Decimal(r['ar_delta']);self.need(balance>=0,'negative or duplicated claim receivable')
                if r['attempt_no']>1:self.need(any(x['event_type']=='DENIED' and x['occurred_at']<=r['occurred_at'] for x in rows),'appeal attempt without initial denial')
            assigned=sum((Decimal(r['payer_liability_delta'])+Decimal(r['patient_liability_delta']) for r in rows),Decimal(0))
            contract=sum((Decimal(r['contractual_adjustment_delta']) for r in rows),Decimal(0));loss=sum((Decimal(r['writeoff_delta']) for r in rows),Decimal(0))
            if h['carry_in']:self.need(assigned==expected,'opening responsibility does not reconcile to historical allowed value')
            elif any(r['event_type'] in ('ADJUDICATED','DENIED') for r in rows):
                pending=Decimal(0)
                for denied in (r for r in rows if r['event_type']=='DENIED'):
                    resolved=any(r['claim_line_id']==denied['claim_line_id'] and r['attempt_no']>1 and r['event_type'] in ('ADJUDICATED','WRITEOFF') for r in rows)
                    if not resolved:pending+=Decimal(self.lines[denied['claim_line_id']]['expected_allowed_amount'])
                # Assigned patient credit losses carry a negative responsibility
                # delta; disputed-line losses extinguish unassigned liability.
                selfpay=self.pay[self.cover[h['coverage_version_id']]['payer_plan_id']]['payer_type']=='SELF_PAY'
                self.need(assigned+pending+loss==expected-contract,'payer/patient responsibility, disputed line and final loss do not reconcile to allowed amount')
                if not selfpay:
                    payer_assigned=sum((Decimal(r['payer_liability_delta']) for r in rows),Decimal(0));patient_assigned=assigned-payer_assigned
                    payer_cash=sum((Decimal(r['cash_delta']) for r in rows if r['event_type'] in ('PAYMENT','REFUND','REVERSAL')),Decimal(0))
                    patient_cash=sum((Decimal(r['cash_delta']) for r in rows if r['event_type']=='PATIENT_PAYMENT'),Decimal(0))
                    self.need(payer_cash<=payer_assigned and patient_cash<=patient_assigned,'collection exceeds assigned responsibility')
            closing+=balance;open_count+=balance>0
        self.metrics.update(claim_event_types=dict(sorted(types.items())),closing_claim_ar=str(closing),open_claims=open_count,
            current_cash=str(sum((Decimal(r['cash_delta']) for r in self.events.values()),Decimal(0))),payment_reversals_and_refunds=len(reversed_ids))

    def check_journals(self):
        grouped=defaultdict(Decimal);actual=defaultdict(lambda:defaultdict(Decimal));eligible=0;reversals=0
        for r in self.postings.values():
            debit=Decimal(r['debit_amount']);credit=Decimal(r['credit_amount']);account=self.cat[r['account_catalog_id']]
            self.need(debit>=0 and credit>=0 and (debit>0) != (credit>0),'journal line has two sides or no positive side')
            self.need(account['domain']=='ACCOUNT' and self.cc[r['cost_center_id']]['facility_id']==r['facility_id'],'journal account/entity mapping invalid')
            self.need('2023-01-01'<=r['posting_date']<='2025-12-31' and r['service_from']<=r['service_to'],'posting service/period outside window')
            self.need(r['known_from']==r['export_available_at'] and r['known_from']>=stamp(local(date.fromisoformat(r['service_to']))),'posting anticipates service or source delivery')
            grouped[r['journal_id'],r['facility_id'],r['currency'],r['posting_date']]+=debit-credit
            key=tuple(r[n] for n in ('source_domain','facility_id','cost_center_id','posting_date','service_from','service_to','known_from','source_group_key'))
            actual[key][account['code']]+=debit-credit
            if r['eligible_for_allocation']:
                eligible+=1;self.need(r['source_domain']=='COST_POOL_CLOSE' and account['code'].endswith('_POOL') and r['allocation_pool_key'],'daily/direct expense allocated twice')
            else:self.need(r['allocation_pool_key'] is None,'noneligible posting has hidden allocation pool')
            if r['reverses_posting_id']:
                old=self.postings[r['reverses_posting_id']];self.need(old['debit_amount']==r['credit_amount'] and old['credit_amount']==r['debit_amount'] and old['account_catalog_id']==r['account_catalog_id'],'posting reversal not an exact opposite');reversals+=1
        self.need(not any(grouped.values()),'journal debits and credits do not balance per entity/date/currency')
        expected,metrics=expected_journals(self.t,self.cfg)
        normalized={k:{a:v for a,v in amounts.items() if v} for k,amounts in actual.items() if any(amounts.values())}
        self.need(normalized==expected,'source predicates, amounts, service-to-posting bridge or pool-close totals differ from independent oracle')
        totals=defaultdict(Decimal)
        for r in self.postings.values():totals[self.cat[r['account_catalog_id']]['code']]+=Decimal(r['debit_amount'])-Decimal(r['credit_amount'])
        inventory=sum((Decimal(r['extended_cost']) for r in self.t['inventory_movement']),Decimal(0))
        self.need(totals['INVENTORY']==inventory,'inventory asset differs from opening/receipt/consumption/expiry/count roll-forward')
        self.need(totals['CASH']==sum((Decimal(r['cash_delta']) for r in self.events.values()),Decimal(0))+Decimal(metrics['opening_operating_cash'])-Decimal(metrics['treasury_disbursements']),'treasury cash does not reconcile exactly to patient receipts, funding and obligation settlements')
        self.metrics.update(metrics,journals=len(grouped),eligible_expense_pool_postings=eligible,linked_posting_reversals=reversals,
            closing_inventory=str(inventory),ledger_totals={k:str(v) for k,v in sorted(totals.items())},monetary_source_predicates=len(expected))

    def check_enterprise_ar(self):
        claimed={r['charge_id']:r['claim_id'] for r in self.lines.values()};unbilled=Decimal(0);submitted={r['claim_id'] for r in self.events.values() if r['event_type']=='SUBMITTED'}
        for r in self.charges.values():
            e=self.enc[r['encounter_version_id']]
            if r['service_to']<'2023-01-01':continue
            if r['charge_id'] not in claimed or claimed[r['charge_id']] not in submitted:
                payer=self.pay[self.cover[e['coverage_version_id']]['payer_plan_id']];unbilled+=money(Decimal(r['billed_amount'])*Decimal(payer['allowed_factor']))
        ledger=sum((Decimal(r['debit_amount'])-Decimal(r['credit_amount']) for r in self.postings.values() if self.cat[r['account_catalog_id']]['code']=='AR'),Decimal(0))
        self.need(ledger==Decimal(self.metrics['closing_claim_ar'])+unbilled,'billed claim AR plus unbilled service AR does not reconcile to enterprise AR')
        self.metrics.update(unbilled_service_ar=str(unbilled),closing_enterprise_ar=str(ledger))

    def check_allocations(self):
        grouped=defaultdict(list);latest_run={};by_posting=defaultdict(set);source_weights=allocation_weights(self.t)
        for r in self.t['cost_allocation']:
            p=self.postings[r['posting_id']];self.need(p['eligible_for_allocation'],'allocation references daily or ineligible expense')
            self.need(r['known_from']==r['export_available_at']>=p['known_from'],'allocation available before cost source')
            self.need(r['cost_center_id']==p['cost_center_id'] and r['accounting_month']==p['posting_date'][:7]+'-01','allocation pool period/center differs')
            self.need(r['cost_category']==self.cat[p['account_catalog_id']]['code'].split('_')[0],'allocation cost category differs')
            self.need((r['destination_type']=='PATIENT')==(r['encounter_version_id'] is not None),'nonpatient/residual destination carries a patient')
            if r['encounter_version_id']:self.need(self.enc[r['encounter_version_id']]['export_available_at']<=r['known_from'],'allocation uses future encounter correction')
            self.need(Decimal(r['driver_quantity'])>0 and 0<=Decimal(r['allocation_share'])<=1,'invalid/nonpositive allocation driver or share')
            grouped[r['posting_id'],r['allocation_run_id']].append(r);by_posting[r['posting_id']].add(r['allocation_run_id'])
        selected=defaultdict(Decimal)
        for (pid,rid),rows in grouped.items():
            p=self.postings[pid];amount=Decimal(p['debit_amount'])-Decimal(p['credit_amount'])
            self.need(sum((Decimal(r['allocation_share']) for r in rows),Decimal(0))==1,'allocation shares do not sum to one')
            self.need(sum((Decimal(r['allocated_amount']) for r in rows),Decimal(0))==amount,'patient/nonpatient/residual allocated cents do not exhaust eligible expense')
            weights={self.enc[r['encounter_version_id']]['encounter_id'] if r['encounter_version_id'] else r['destination_type']:Decimal(r['driver_quantity']) for r in rows}
            self.need(len(weights)==len(rows),'duplicate allocation destination in one run')
            category=rows[0]['cost_category'];source=source_weights.get((p['posting_date'][:7],p['cost_center_id'],category),{})
            if source:
                raw={eid:Decimal(1) if rows[0]['driver_unit']=='encounter_months' else v for eid,v in source.items() if v>0}
                expected_weights={eid:v.quantize(Decimal('.000001'),rounding=ROUND_HALF_UP) for eid,v in raw.items()}
                self.need(weights==expected_weights,'allocation weights/destinations do not follow actual care and consumption sources')
            else:self.need(set(weights)<={'NONPATIENT','RESIDUAL'},'unsupported expense allocated to invented patients')
            expected=partition(amount,weights)
            # The source records rounded six-place quantities; consuming weights
            # are exact currency or microhour/minute values. A one-cent ambiguity
            # is forbidden: generation must apportion using the stored weights.
            self.need(all(Decimal(r['allocated_amount'])==expected[self.enc[r['encounter_version_id']]['encounter_id'] if r['encounter_version_id'] else r['destination_type']] for r in rows),'allocation cent residual/tie break differs from stored drivers')
            fractions=partition(10000,weights)
            self.need(all(Decimal(r['allocation_share'])==fractions[self.enc[r['encounter_version_id']]['encounter_id'] if r['encounter_version_id'] else r['destination_type']]/10000 for r in rows),'stored shares differ from declared drivers')
            prior={r['supersedes_run_id'] for r in rows};self.need(len(prior)==1,'allocation run has conflicting predecessor')
            predecessor=next(iter(prior))
            if predecessor:self.need((pid,predecessor) in grouped and max(r['known_from'] for r in grouped[pid,predecessor])<min(r['known_from'] for r in rows),'allocation supersession is missing/noncausal')
            if pid not in latest_run or rows[0]['known_from']>latest_run[pid][0]:latest_run[pid]=(rows[0]['known_from'],rid)
        eligible={p['posting_id'] for p in self.postings.values() if p['eligible_for_allocation']}
        self.need(set(by_posting)==eligible,'eligible pool has no explicit allocation/residual')
        for pid,(_,rid) in latest_run.items():
            for r in grouped[pid,rid]:selected[r['destination_type']]+=Decimal(r['allocated_amount'])
        self.metrics.update(selected_allocated_costs={k:str(v) for k,v in sorted(selected.items())},allocation_runs=len(grouped),revised_allocation_pools=sum(len(v)>1 for v in by_posting.values()))

    def check_monthly(self):
        actual=[r for r in self.t['finance_monthly'] if r['scenario']=='ACTUAL'];count=Counter();comparisons=0
        for r in self.t['finance_monthly']:
            self.need(r['accounting_month'].endswith('-01') and '2023-01-01'<=r['accounting_month']<='2025-12-01','invalid financial target month')
            self.need(self.cc[r['cost_center_id']]['facility_id']==r['facility_id'],'Axiom facility and cost center affiliation differ')
            self.need(r['published_at']==r['export_available_at'],'financial vintage availability differs')
            if r['measure_code']=='ACCOUNT_AMOUNT':self.need(r['account_catalog_id'] and r['amount'] is not None and r['quantity'] is None and r['unit_code']=='USD','currency amount mixed with statistical units')
            else:self.need(r['account_catalog_id'] is None and r['amount'] is None and r['quantity'] is not None and r['unit_code']=={'PATIENT_DAYS':'patient_days','ADMISSIONS':'admissions','PRODUCTIVE_HOURS':'hours','FTE':'FTE'}[r['measure_code']],'statistical measure has wrong unit/money')
            if r['scenario'] in ('BUDGET','FORECAST'):self.need(r['published_at']<stamp(local(date.fromisoformat(r['accounting_month']))),'planning vintage uses target-period observations')
            target=date.fromisoformat(r['accounting_month'])
            if r['scenario']=='ACTUAL':
                final=r['vintage_id']=='ACTUAL-2025-12-01-FINAL'
                self.need(r['vintage_id']=='ACTUAL-'+str(target) or final and target==date(2025,12,1),'unregistered actual vintage')
                self.need(r['published_at']==close(target,9 if final else 5),'actual publication precedes or differs from the registered close')
                self.need(r['supersedes_vintage_id']==('ACTUAL-2025-12-01' if final else None),'actual replacement lineage differs')
                if r['account_catalog_id'] and self.cat[r['account_catalog_id']]['account_class'] in ('ASSET','LIABILITY','EQUITY'):
                    self.need(self.cc[r['cost_center_id']]['cost_center_code'].endswith('-ADMINISTRATION'),'balance control is not at facility administration')
            elif r['scenario']=='BUDGET':
                revised=r['vintage_id']==f'BUDGET-{target.year}-MIDYEAR'
                self.need(r['vintage_id']==f'BUDGET-{target.year}-ORIGINAL' or revised and target.year in (2024,2025) and target.month>=7,'unregistered budget vintage/horizon')
                published=stamp(local(date(target.year,6,20),12)) if revised else stamp(local(date(target.year-1,12,20),12))
                self.need(r['published_at']==published and r['supersedes_vintage_id']==(f'BUDGET-{target.year}-ORIGINAL' if revised else None),'budget publication/replacement lineage differs')
            else:
                quarter=date.fromisoformat(r['vintage_id'].removeprefix('FORECAST-'))
                self.need(quarter.day==1 and quarter.month in (1,4,7,10) and quarter.year==target.year and 0<=target.month-quarter.month<=2,'forecast horizon/vintage is invalid')
                self.need(r['published_at']==stamp(local(quarter-timedelta(days=12),12)) and r['supersedes_vintage_id'] is None,'forecast publication/lineage differs')
            count[r['scenario']]+=1
        # Aggregate once per publication, independently of the generation rollup.
        targets=defaultdict(list)
        for r in actual:targets[r['accounting_month'],r['published_at']].append(r)
        for (m,published),rows in targets.items():
            pnl=defaultdict(Decimal);balance=defaultdict(Decimal)
            end=str(following(date.fromisoformat(m)))
            for p in self.postings.values():
                if p['known_from']>published or p['posting_date']>=end:continue
                a=self.cat[p['account_catalog_id']];v=Decimal(p['debit_amount'])-Decimal(p['credit_amount'])
                if a['account_class'] in ('ASSET','LIABILITY','EQUITY'):balance[p['facility_id'],a['code']]+=v
                elif p['posting_date']>=m:pnl[p['cost_center_id'],a['code']]+=v
            stats=statistical_values(self.t,date.fromisoformat(m),published)
            for r in rows:
                if r['amount'] is None:
                    self.need(Decimal(r['quantity'])==stats[r['cost_center_id']][r['measure_code']].quantize(Decimal('.000001'),rounding=ROUND_HALF_UP),'Axiom statistical quantity differs from known captured activity')
                    continue
                a=self.cat[r['account_catalog_id']];is_balance=a['account_class'] in ('ASSET','LIABILITY','EQUITY')
                value=balance[r['facility_id'],a['code']] if is_balance else pnl[r['cost_center_id'],a['code']]
                if a['normal_balance']=='CREDIT':value=-value
                self.need(Decimal(r['amount'])==value,'Axiom actual differs from exact monthly movement/cumulative closing journal balance');comparisons+=1
        self.need(count['ACTUAL']==21201 and count['BUDGET']==13392 and count['FORECAST']==864,'required Axiom series/vintage inventory differs')
        self.metrics.update(finance_series=dict(count),monetary_actual_reconciliations=comparisons)

    def check_planning(self):
        expected=planning_values(self.t,self.cfg);vintages={}
        for r in self.t['finance_monthly']:
            if r['finance_record_id'] in expected:self.need(Decimal(r['amount'])==expected[r['finance_record_id']],'budget/forecast differs from known-history prospective planning oracle')
            if r['scenario'] in ('BUDGET','FORECAST'):
                key=r['scenario'],r['vintage_id'];vintages[key]=r['published_at']
                if r['quantity'] is not None:
                    n=calendar.monthrange(int(r['accounting_month'][:4]),int(r['accounting_month'][5:7]))[1];days=24*n*Decimal(self.cfg['planning_occupancy']);hours=days*Decimal('5.5')
                    value={'PATIENT_DAYS':days,'ADMISSIONS':days/Decimal(self.cfg['planning_mean_los_days']),'PRODUCTIVE_HOURS':hours,'FTE':hours*12/2080}[r['measure_code']]
                    self.need(Decimal(r['quantity'])==value.quantize(Decimal('.000001'),rounding=ROUND_HALF_UP),'budget statistic not from known capacity inputs')
        self.metrics.update(planning_vintages=len(vintages),independently_recomputed_plan_amounts=len(expected))

    def run(self):
        checks=[];defects=[]
        for method in ('schema','charges','claims','events','journals','enterprise_ar','allocations','monthly','planning'):
            logging.getLogger(__name__).info('Checking financial %s controls',method)
            try:getattr(self,'check_'+method)();checks.append({'name':method,'status':'PASS'})
            except Exception as exc:checks.append({'name':method,'status':'FAIL'});defects.append({'defect_id':digest([method,str(exc)])[:32],'severity':'P0','control':method,'message':str(exc)})
        return {'checks':checks,'defects':defects,'metrics':self.metrics}


def validate_financial(tables,cfg,schema):return FinancialValidator(tables,cfg,schema).run()
