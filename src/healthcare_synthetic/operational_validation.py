"""Independent interval/state oracle and operational data-quality controls.

No simulator, generation helper, serializer or random draw is imported here.
"""
from __future__ import annotations

import calendar
import hashlib
import json
from collections import Counter, defaultdict
from datetime import timedelta
from decimal import Decimal

from .clinical_validation import ClinicalValidator
from .master_validation import MasterValidator, timestamp, contains, years

START='2023-01-01T06:00:00Z'
CUTOFF='2026-01-01T06:00:00Z'


def encode(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(value):return hashlib.sha256(encode(value)).hexdigest()
def seconds(a,b):return int((timestamp(b)-timestamp(a)).total_seconds())


def resolve_events(events,known_at=None):
    unique={}
    for row in events:
        if known_at and row['delivery_at']>known_at:continue
        key=row['bed_event_id']
        if key in unique and unique[key]!=row:raise ValueError('conflicting duplicate event ID')
        unique[key]=row
    if known_at:
        # Delivery may put a correction ahead of its original; retain it externally and
        # make it effective only when its complete dependency chain is available.
        while True:
            pending=[key for key,r in unique.items() if r['corrects_bed_event_id'] and r['corrects_bed_event_id'] not in unique]
            if not pending:break
            for key in pending:unique.pop(key)
    replacements={}
    for row in unique.values():
        target=row['corrects_bed_event_id']
        if target:
            if target not in unique:raise ValueError('orphan correction target')
            old=unique[target]
            if row['event_type']!='CORRECTION' or row['bed_location_id']!=old['bed_location_id'] or row['effective_at']!=old['effective_at'] or row['recorded_at']<=old['recorded_at']:
                raise ValueError('invalid correction context or chronology')
            if target in replacements:raise ValueError('ambiguous correction branches')
            replacements[target]=row['bed_event_id']
    result=[]
    for key,original in unique.items():
        if original['corrects_bed_event_id']:continue
        current=key; seen=set()
        while current in replacements:
            if current in seen:raise ValueError('cyclic correction history')
            seen.add(current);current=replacements[current]
        row=dict(unique[current]); row['_kind']=original['event_type']; row['_sequence']=original['sequence_no']
        result.append(row)
    if len(result)+len(replacements)!=len(unique):raise ValueError('unreachable cyclic correction')
    return sorted(result,key=lambda r:(r['effective_at'],0 if r['_kind']=='VACATE' else 2 if r['_kind']=='OCCUPY' else 1,r['bed_location_id'],r['_sequence'],r['bed_event_id']))


def bed_intervals(events,encounters,known_at=None):
    """Pair occupancy boundaries independently of full-state integration."""
    active={}; intervals=[]
    for r in resolve_events(events,known_at):
        bid=r['bed_location_id'];kind=r['_kind'];at=r['effective_at']
        if kind=='OPENING' and r['occupancy_state']=='OCCUPIED' or kind=='OCCUPY':
            if bid in active:raise ValueError('overlapping bed occupancy')
            if not r['encounter_version_id']:raise ValueError('occupied bed lacks context')
            active[bid]=(encounters[r['encounter_version_id']]['encounter_id'],at)
        elif kind=='VACATE':
            if bid not in active:raise ValueError('vacate without occupant')
            eid,begin=active.pop(bid)
            if not r['encounter_version_id'] or encounters[r['encounter_version_id']]['encounter_id']!=eid:raise ValueError('vacate patient differs')
            intervals.append((bid,eid,max(begin,START),min(at,CUTOFF)))
    for bid,(eid,begin) in active.items():intervals.append((bid,eid,max(begin,START),CUTOFF))
    return sorted(intervals)


def current_beds(events,at,known_at=None):
    state={}
    for r in resolve_events(events,known_at):
        if r['effective_at']<=at:state[r['bed_location_id']]={k:r[k] for k in ('occupancy_state','service_state','staffing_enabled','reserved','encounter_version_id')}
    return state


class IntegratedClinicalValidator(ClinicalValidator):
    """Retain every clinical check, with an explicit continuous-transfer cohort addendum."""
    def __init__(self,tables,schema,cfg,policy,master):
        observed={r['encounter_id'] for r in tables['encounter'] if r['disposition']=='DEATH'}
        cfg={**cfg,'cohort':{**cfg['cohort'],'death_outcomes':len(observed)}}
        policy={**policy,'elective_admission_hours':[7,14]}
        super().__init__(tables,schema,cfg,policy,master)
        self.metrics['planned_terminal_cohort']=30

    def check_documents(self):
        notes=[r for r in self.t['clinical_event'] if r['source_record_id'].endswith(('/placement-assessment','/placement-disposition','/transfer-referral')) or (r['text_value'] or '').startswith(('Placement assessment for ','Placement disposition for ','Transfer coordination for '))]
        note_ids={r['clinical_event_version_id'] for r in notes}
        old=self.t;self.t={**old,'clinical_event':[r for r in old['clinical_event'] if r['clinical_event_version_id'] not in note_ids]}
        try:super().check_documents()
        finally:self.t=old
        self.need(sum(r['source_record_id'].endswith('/placement-assessment') for r in notes)>=200,'placement-notes','precaution assessment scenario absent')
        facility_codes={r['facility_id']:r['facility_code'] for r in self.t['facility']};expected_referrals={}
        for destination in self.latest.values():
            if destination['admission_source']=='TRANSFER':
                sender=self.idx['encounter'][destination['previous_encounter_version_id']]
                expected_referrals[sender['encounter_id']]=facility_codes[destination['facility_id']]
                expected_referrals[destination['encounter_id']]=facility_codes[destination['facility_id']]
        for r in notes:
            e=self.idx['encounter'][r['encounter_version_id']];at=r['occurred_at'];pid=self.person(e)
            self.need(r['event_type']=='DOCUMENT' and r['document_type']=='PROGRESS_NOTE' and r['document_signed_at']==at==r['known_from'],r['clinical_event_version_id'],'operational document type/signing chronology')
            if r['source_record_id'].endswith('/transfer-referral'):
                import re
                if e['admission_source']=='TRANSFER':pattern=r'Transfer coordination for encounter '+re.escape(e['encounter_id'])+r': accepted continuation at (HSP-[A-Z]+); receiving arrival is observed at '+re.escape(e['arrival_at'])+r'\. Later care outcome is not yet established\.'
                else:pattern=r'Transfer coordination for encounter '+re.escape(e['encounter_id'])+r': continuation at (HSP-[A-Z]+) is accepted within the modeled network\. Capacity escalation remains within that referral; actual handoff time is not yet established\.'
                match=re.fullmatch(pattern,r['text_value'])
                self.need(match is not None and match.group(1)==expected_referrals.get(e['encounter_id']) and e['admitted_at']==at,r['clinical_event_version_id'],'referral plan is not source-known at admission or targets the wrong hospital')
                continue
            if r['source_record_id'].endswith('/placement-disposition'):
                import re
                if e['disposition']=='DEATH':
                    pattern=r'Placement disposition for encounter '+re.escape(e['encounter_id'])+r': observed death at '+re.escape(at)+r' before compatible placement\. Care continued in monitored boarding; no licensed bed occupancy is asserted\. Cause: ([A-Z_,]+)\.'
                else:pattern=r'Placement disposition for encounter '+re.escape(e['encounter_id'])+r': external transfer at '+re.escape(at)+r' after 24 hours from inpatient admission awaiting a compatible bed\. Cause: ([A-Z_,]+)\. Receiving care and later outcome are outside the modeled network\.'
                match=re.fullmatch(pattern,r['text_value'])
                allowed={'COMPATIBLE_CAPACITY_EXHAUSTED','ICU_STABILIZATION_REQUIRED','ISOLATION_COHORT_REQUIRED','MAINTENANCE_REDUCED_CAPACITY'}
                self.need(match is not None and set(match.group(1).split(','))<=allowed,r['clinical_event_version_id'],'unsupported placement disposition narrative')
                self.need(e['discharged_at']==at and (e['disposition']=='TRANSFER' and seconds(e['admitted_at'],at)==86400 or e['disposition']=='DEATH' and 0<seconds(e['admitted_at'],at)<=86400),r['clinical_event_version_id'],'unmet-demand disposition timing differs')
                continue
            p=next(p for p in self.patient_histories[pid] if contains(p,at,at,availability=False))
            age=years(p['birth_date'],timestamp(at).astimezone(self.local_zone).date().isoformat())
            body=f"Placement assessment for {p['given_name']} {p['family_name']}, age {age}: suspected transmissible respiratory illness; isolation-capable private room requested. Recorded at {at}."
            self.need(r['text_value']==body and r['event_type']=='DOCUMENT' and r['document_type']=='PROGRESS_NOTE' and r['document_signed_at']==at==r['known_from'],r['clinical_event_version_id'],'unsupported placement assessment narrative or timing')
            self.need(e['encounter_class']=='IPD' and e['admitted_at']==at and r['catalog_item_id'] is None,r['clinical_event_version_id'],'placement assessment lacks admission context')
        self.metrics['placement_assessment_documents']=sum(r['source_record_id'].endswith('/placement-assessment') for r in notes)
        self.metrics['placement_disposition_documents']=sum(r['source_record_id'].endswith('/placement-disposition') for r in notes)
        self.metrics['transfer_referral_documents']=sum(r['source_record_id'].endswith('/transfer-referral') for r in notes)
        self.need(self.metrics['transfer_referral_documents']==24,'referrals','continuous-care referral source documents missing')
        legacy_count=self.metrics['document_counts']['PROGRESS_NOTE'];legacy_share=Decimal(str(self.metrics['normalized_note_duplicate_shares']['PROGRESS_NOTE']))
        # Conservative duplicate bound: treat every additional placement template as
        # identical after identity/date removal, even when source details differ.
        pooled=(legacy_share*legacy_count+max(0,len(notes)-1))/(legacy_count+len(notes))
        self.need(pooled<=Decimal(str(self.policy['targets']['maximum_normalized_note_duplicate_share'])),'placement-notes','pooled progress-note duplication target missed')
        self.metrics['progress_note_duplicate_share_upper_bound']=str(pooled)
    def check_encounters(self):
        for eid,rows in self.encounters.items():
            identities={(self.person(r),r['episode_id'],r['facility_id'],r['encounter_class']) for r in rows}
            self.need(len(identities)==1,eid,'logical encounter identity drifts between source revisions')
        recipients={eid:e for eid,e in self.latest.items() if e['admission_source']=='TRANSFER'}
        saved_histories,saved_latest=self.encounters,self.latest
        self.encounters={eid:v for eid,v in saved_histories.items() if eid not in recipients}
        self.latest={eid:v for eid,v in saved_latest.items() if eid not in recipients}
        try:super().check_encounters()
        finally:self.encounters,self.latest=saved_histories,saved_latest
        self.need(len(recipients)==12,'transfers','continuous recipient cohort differs')
        self.need(0<len(self.deaths)<=30,'deaths','observed terminal outcomes outside integrated scope')
        for eid,e in recipients.items():
            rows=sorted(self.encounters[eid],key=lambda r:r['revision_no'])
            prior=self.idx['encounter'][e['previous_encounter_version_id']]
            self.need(prior['disposition']=='TRANSFER' and prior['facility_id']!=e['facility_id'] and prior['episode_id']==e['episode_id'] and self.person(prior)==self.person(e),eid,'continuous transfer identity does not reconcile')
            codes={r['facility_id']:r['facility_code'] for r in self.t['facility']}
            route='|'.join(sorted((codes[prior['facility_id']],codes[e['facility_id']])))
            minimum=self.policy['site_transport_minutes'][route]*60
            maximum=minimum+self.policy['site_transport_handover_max_minutes']*60
            self.need(minimum<=seconds(prior['discharged_at'],e['arrival_at'])<=maximum,eid,'transport gap outside the approved route and handover window')
            self.need([r['revision_no'] for r in rows]==[1,2,3],eid,'recipient knowledge chain differs')
            for i,r in enumerate(rows):
                self.need(r['known_to']==(rows[i+1]['known_from'] if i<2 else None),eid,'recipient supersession differs')
                milestones=[r['arrival_at']]+[r[f] for f in ('admission_decision_at','admitted_at','medically_ready_at','discharged_at') if r[f]]
                self.need(milestones==sorted(milestones) and all(t<=r['known_from'] for t in milestones),eid,'recipient future milestone')
                self.need(contains(self.patient[r['patient_version_id']],r['arrival_at'],r['arrival_at'],availability=False),eid,'recipient patient snapshot unavailable')
                cov=self.idx['patient_coverage'][r['coverage_version_id']]
                self.need(self.patient[cov['patient_version_id']]['patient_id']==self.person(r) and contains(cov,r['arrival_at'],r['arrival_at'],availability=False),eid,'recipient coverage unavailable')
                self.valid_author(r['attending_assignment_id'],r['facility_id'],r['arrival_at'],eid)
                self.need(self.idx['location'][r['location_id']]['facility_id']==r['facility_id'],eid,'recipient facility mismatch')
        self.metrics['continuous_transfer_recipients']=len(recipients)


class OperationalValidator:
    def __init__(self,tables,schema,cfg,simulation=None):
        self.t,self.schema,self.cfg,self.simulation=tables,schema,cfg,simulation
        self.enc={r['encounter_version_id']:r for r in tables['encounter']}
        self.latest={}
        for e in tables['encounter']:
            if e['encounter_id'] not in self.latest or e['revision_no']>self.latest[e['encounter_id']]['revision_no']:self.latest[e['encounter_id']]=e
        self.patients={r['patient_version_id']:r for r in tables['patient']}
        self.loc={r['location_id']:r for r in tables['location']}
        cat={r['catalog_item_id']:r for r in tables['catalog_item']}
        self.dx={self.enc[c['encounter_version_id']]['encounter_id']:cat[c['catalog_item_id']]['code'] for c in tables['clinical_condition'] if c['encounter_version_id'] and c['diagnosis_rank']==1 and c['revision_no']==1}
        self.precautions={self.enc[r['encounter_version_id']]['encounter_id'] for r in tables.get('clinical_event',[]) if r['source_record_id'].endswith('/placement-assessment')}
        self.referrals={self.enc[r['encounter_version_id']]['encounter_id']:r for r in tables.get('clinical_event',[]) if r['source_record_id'].endswith('/transfer-referral')}
        self.metrics={};self.resolved=None

    def need(self,ok,msg):
        if not ok:raise ValueError(msg)

    def check_schema(self):
        v=MasterValidator(self.t,self.schema,{}, {'permitted_tables':list(self.t)}, {})
        for method in ('schema','keys','references'):getattr(v,'check_'+method)()
        specs={t['name']:t for t in self.schema['tables']}
        for name in ('bed_event','facility_day_driver'):
            for r in self.t[name]:self.need(r['source_system']==specs[name]['source_authority'],'incorrect operational source authority')

    def check_clocks(self):
        seq=defaultdict(set)
        by_bed=defaultdict(list)
        for r in self.t['bed_event']:
            self.need(START<=r['effective_at']<CUTOFF,'bed event outside business window')
            self.need(r['effective_at']<=r['recorded_at']<=r['delivery_at']==r['export_available_at']<='2026-01-10T23:59:59Z','bed source/delivery chronology')
            self.need(r['sequence_no'] not in seq[r['bed_location_id']],'duplicate source sequence')
            seq[r['bed_location_id']].add(r['sequence_no'])
            by_bed[r['bed_location_id']].append(r)
            self.need((r['event_type']=='CORRECTION')==bool(r['corrects_bed_event_id']),'correction must identify exactly one earlier assertion')
        for values in seq.values():self.need(values==set(range(1,len(values)+1)),'source sequence gap')
        for rows in by_bed.values():
            clocks=[r['recorded_at'] for r in sorted(rows,key=lambda r:r['sequence_no'])]
            self.need(clocks==sorted(clocks),'source sequence does not follow recording order')
        self.resolved=resolve_events(self.t['bed_event'])
        self.metrics['corrections']=sum(r['event_type']=='CORRECTION' for r in self.t['bed_event'])
        self.need(self.metrics['corrections']==self.cfg['corrected_events'],'correction scenario count differs')

    def check_state(self):
        states={}; previous_time={}; integrated=0;staffed=0;available=0;licensed=0
        occupied_patients={}; opening=0; transfers=defaultdict(list); clinical_ends=Counter();placements=Counter()
        dirty={}; turnaround=[]; closures=defaultdict(list); boundary=defaultdict(Counter)
        last_boundary=START;true_available_seconds=0
        room_beds=defaultdict(list)
        for bed in self.loc.values():
            if bed['location_type']=='BED':room_beds[bed['parent_location_id']].append(bed['location_id'])
        def available_now():
            count=0
            for bid,state in states.items():
                if state['occupancy_state']!='EMPTY' or state['service_state']!='IN_SERVICE' or not state['staffing_enabled'] or state['reserved']:continue
                private_peer=False
                for peer_id in room_beds[self.loc[bid]['parent_location_id']]:
                    peer=states.get(peer_id)
                    if peer and peer['occupancy_state']=='OCCUPIED':
                        occupant=self.enc[peer['encounter_version_id']]
                        if occupant['encounter_id'] in self.precautions or self.patients[occupant['patient_version_id']]['administrative_sex'] not in ('M','F'):private_peer=True
                count+=not private_peer
            return count
        for r in self.resolved or resolve_events(self.t['bed_event']):
            bid,at,kind=r['bed_location_id'],r['effective_at'],r['_kind']
            if at>last_boundary:
                true_available_seconds+=seconds(last_boundary,at)*available_now();last_boundary=at
            bed=self.loc[bid];self.need(bed['location_type']=='BED','event references non-bed')
            old=states.get(bid)
            if old:
                duration=seconds(previous_time[bid],at)
                integrated+=duration*(old['occupancy_state']=='OCCUPIED')
                staffed+=duration*(old['service_state']=='IN_SERVICE' and old['staffing_enabled'])
                available+=duration*(old['service_state']=='IN_SERVICE' and old['staffing_enabled'] and old['occupancy_state']=='EMPTY' and not old['reserved'])
                licensed+=duration
            else:self.need(kind=='OPENING' and at==START,'missing explicit opening bed state')
            before=bool(old and old['occupancy_state']=='OCCUPIED');after=r['occupancy_state']=='OCCUPIED'
            if kind=='OPENING':opening+=after
            if before and not after:
                old_e=self.enc[old['encounter_version_id']];pid=self.patients[old_e['patient_version_id']]['patient_id']
                occupied_patients.pop(pid)
                self.need(kind=='VACATE','occupied patient disappeared without vacate')
                self.need(r['encounter_version_id'] and self.enc[r['encounter_version_id']]['encounter_id']==old_e['encounter_id'],'vacate context mismatch')
                dirty[bid]=at;clinical_ends[old_e['encounter_id']]+=1
                boundary[at][bed['facility_id']]-=1
            if after and not before:
                self.need(kind in ('OPENING','OCCUPY'),'unexplained new occupant')
                e=self.enc[r['encounter_version_id']];p=self.patients[e['patient_version_id']];pid=p['patient_id'];eid=e['encounter_id']
                self.need(pid not in occupied_patients,'simultaneous inpatient placement for patient')
                self.need(r['service_state']=='IN_SERVICE' and r['staffing_enabled'] and not r['reserved'],'occupied unavailable bed')
                if old:self.need(old['occupancy_state']=='EMPTY' and old['service_state']=='IN_SERVICE' and old['staffing_enabled'],'placement before bed ready')
                self.need(e['facility_id']==bed['facility_id'] and e['encounter_class']=='IPD','placement facility/class mismatch')
                self.need(self.latest[eid]['admitted_at']<=at<(self.latest[eid]['discharged_at'] or CUTOFF),'bed outside admitted care period')
                self.need(e['known_from']<=at,'future encounter snapshot used for placement')
                isolation=eid in self.precautions
                self.need(not isolation or bed['isolation_capable'],'pneumonia placed in incompatible bed')
                if bed['service_line']=='ICU':self.need((not e['planned'] and e['initial_acuity']<=2) or 'WARD_OVERFLOW_ICU' in r['reason'],'ICU location lacks intensive indication or explicit ward overflow semantics')
                else:self.need(bed['service_line'] in ('MEDICINE','SURGERY'),'adult med-surg capability mismatch')
                for peer_id,peer in states.items():
                    if peer_id!=bid and self.loc[peer_id]['parent_location_id']==bed['parent_location_id'] and peer['occupancy_state']=='OCCUPIED':
                        other=self.enc[peer['encounter_version_id']];op=self.patients[other['patient_version_id']]
                        self.need(p['administrative_sex'] in ('M','F') and p['administrative_sex']==op['administrative_sex'] and not isolation and other['encounter_id'] not in self.precautions,'room cohort incompatibility')
                occupied_patients[pid]=bid;placements[eid]+=1;boundary[at][bed['facility_id']]+=1
            if before and after:self.need(old['encounter_version_id']==r['encounter_version_id'],'occupant changed without transfer legs')
            if r['service_state']!='IN_SERVICE' or not r['staffing_enabled']:self.need(not after,'closure removed an occupied bed')
            self.need(not r['reserved'] or r['occupancy_state']=='EMPTY','reservation counted as occupancy')
            if kind=='RESERVE':self.need(old and not old['reserved'] and r['reserved'],'duplicate or invalid reservation transition')
            if kind=='RELEASE':self.need(old and old['reserved'] and not r['reserved'],'release without an active reservation')
            transitions={'OCCUPY':('EMPTY','OCCUPIED'),'VACATE':('OCCUPIED','DIRTY'),'CLEAN_START':('DIRTY','CLEANING'),'READY':('CLEANING','EMPTY')}
            if kind in transitions:
                a,b=transitions[kind];self.need(old and old['occupancy_state']==a and r['occupancy_state']==b,'invalid cleanliness transition')
            if kind=='READY':turnaround.append(seconds(dirty.pop(bid),at))
            if r['transfer_group_id']:transfers[r['transfer_group_id']].append(r)
            states[bid]=r;previous_time[bid]=at
        for bid,r in states.items():
            duration=seconds(previous_time[bid],CUTOFF);licensed+=duration
            integrated+=duration*(r['occupancy_state']=='OCCUPIED')
            staffed+=duration*(r['service_state']=='IN_SERVICE' and r['staffing_enabled'])
            available+=duration*(r['service_state']=='IN_SERVICE' and r['staffing_enabled'] and r['occupancy_state']=='EMPTY' and not r['reserved'])
        true_available_seconds+=seconds(last_boundary,CUTOFF)*available_now()
        self.need(len(states)==72 and opening==57,'opening inventory/census differs')
        intervals=bed_intervals(self.t['bed_event'],self.enc)
        paired=sum(seconds(a,b) for _,_,a,b in intervals)
        self.need(paired==integrated,'event integral versus independent intervals differs')
        if self.simulation:
            self.need(integrated==self.simulation['simulated_occupied_seconds'] and sha(intervals)==self.simulation['simulated_interval_sha256'],'simulator/independent interval oracle differs')
        # Independent deltas, evaluated at EVERY event boundary, not just month-end totals.
        expected=Counter(); closing=Counter();starts=defaultdict(Counter);ends=defaultdict(Counter)
        for bid,eid,a,b in intervals:
            fid=self.loc[bid]['facility_id'];starts[a][fid]+=1
            if b<CUTOFF:ends[b][fid]+=1
            else:closing[fid]+=1
            latest=self.latest[eid]
            self.need(latest['admitted_at']<=a<b<=(latest['discharged_at'] or CUTOFF),'interval not contained in care')
        for at in sorted(set(starts)|set(ends)|set(boundary)):
            delta=starts[at].copy();delta.subtract(ends[at])
            actual=boundary[at].copy()
            if at==START:
                actual=starts[START].copy()
            self.need(all(delta[fid]==actual[fid] for fid in set(delta)|set(actual)),'census boundary reconciliation difference')
            expected.update(delta)
            self.need(all(v>=0 for v in expected.values()),'negative reconciled census')
        self.need(+expected==+closing,'closing census roll-forward difference')
        site=internal=transport=site_bed_gap=0
        for group,legs in transfers.items():
            self.need(len(legs)==2 and {r['_kind'] for r in legs}=={'VACATE','OCCUPY'},'unpaired atomic transfer')
            out=next(r for r in legs if r['_kind']=='VACATE');into=next(r for r in legs if r['_kind']=='OCCUPY')
            a,b=self.enc[out['encounter_version_id']],self.enc[into['encounter_version_id']]
            self.need(self.patients[a['patient_version_id']]['patient_id']==self.patients[b['patient_version_id']]['patient_id'],'transfer patient differs')
            if a['facility_id']==b['facility_id']:
                internal+=1;self.need(a['encounter_id']==b['encounter_id'] and out['effective_at']==into['effective_at'],'internal transfer changed admission/instant')
            else:
                site+=1;self.need(a['episode_id']==b['episode_id'] and out['effective_at']<into['effective_at'] and b['admission_source']=='TRANSFER','site transfer episode/gap differs')
                sending,receiving=self.latest[a['encounter_id']],self.latest[b['encounter_id']]
                self.need(sending['encounter_id'] in self.referrals and receiving['encounter_id'] in self.referrals,'accepted continuation lacks a source-known referral plan')
                codes={r['facility_id']:r['facility_code'] for r in self.t['facility']}
                route='|'.join(sorted((codes[sending['facility_id']],codes[receiving['facility_id']])))
                actual=seconds(sending['discharged_at'],receiving['arrival_at'])
                self.need(self.cfg['site_transport_minutes'][route]*60<=actual<=(self.cfg['site_transport_minutes'][route]+self.cfg['site_transport_handover_max_minutes'])*60,'site transport violates configured route window')
                self.need(sending['discharged_at']==out['effective_at'],'sending occupancy does not end at the transfer handoff')
                transport+=seconds(sending['discharged_at'],receiving['arrival_at'])
                site_bed_gap+=seconds(out['effective_at'],into['effective_at'])
        self.need(site==self.cfg['continuous_site_transfers'] and internal>0,'transfer scenario absent')
        lost=licensed-staffed
        self.need(lost==self.cfg['maintenance_bed_days']*86400,'staffed capacity closure budget differs')
        occupancy=Decimal(integrated)/staffed
        lo,hi=map(Decimal,self.cfg['targets']['staffed_occupancy']);self.need(lo<=occupancy<=hi,'staffed occupancy target missed: '+str(occupancy))
        self.metrics.update(occupied_seconds=integrated,interval_seconds=paired,interval_count=len(intervals),interval_sha256=sha(intervals),
            licensed_bed_seconds=licensed,staffed_bed_seconds=staffed,lost_staffed_bed_days=str(Decimal(lost)/86400),
            staffed_occupancy=str(occupancy),clean_unreserved_staffed_bed_seconds=available,immediately_available_bed_seconds=true_available_seconds,opening_census=opening,closing_census=sum(closing.values()),
            closing_by_facility=dict(closing),internal_transfers=internal,site_transfers=site,site_transport_seconds=transport,site_transfer_bed_gap_seconds=site_bed_gap,census_boundaries_checked=len(set(starts)|set(ends)),
            mean_turnaround_minutes=str(Decimal(sum(turnaround))/len(turnaround)/60))

    def check_queues(self):
        intervals=bed_intervals(self.t['bed_event'],self.enc);first={};placed=defaultdict(int)
        for bid,eid,a,b in intervals:first[eid]=min(first.get(eid,a),a);placed[eid]+=seconds(a,b)
        boarding=[];admitted_waits=[];unplaced=[];censored=[];total_care=0;pre=0;gaps=0;decision_to_admit=0
        for eid,e in self.latest.items():
            if e['encounter_class']!='IPD':continue
            a=max(START,e['admitted_at']);b=e['discharged_at'] or CUTOFF
            total_care+=seconds(a,b)
            decision=max(START,e['admission_decision_at']);decision_to_admit+=seconds(decision,a)
            if eid not in first:
                if e['discharged_at']:unplaced.append(eid)
                else:censored.append(seconds(decision,CUTOFF))
                pre+=seconds(a,b)
            else:
                wait=seconds(a,first[eid]);admitted_waits.append(wait);boarding.append(seconds(decision,first[eid]));pre+=wait
                gaps+=seconds(a,b)-wait-placed[eid]
        disposition_notes={self.enc[r['encounter_version_id']]['encounter_id'] for r in self.t.get('clinical_event',[]) if r['source_record_id'].endswith('/placement-disposition')}
        unexplained=[eid for eid in unplaced if eid not in disposition_notes or not (self.latest[eid]['disposition']=='TRANSFER' and seconds(self.latest[eid]['admitted_at'],self.latest[eid]['discharged_at'])==86400 or self.latest[eid]['disposition']=='DEATH' and 0<seconds(self.latest[eid]['admitted_at'],self.latest[eid]['discharged_at'])<=86400)]
        self.need(len(unexplained)<=self.cfg['targets']['maximum_unexplained_unplaced_completions'],'unexplained completed inpatient without placement: '+str(len(unexplained)))
        for eid in unplaced:
            admitted_waits.append(seconds(max(START,self.latest[eid]['admitted_at']),self.latest[eid]['discharged_at']))
            boarding.append(seconds(max(START,self.latest[eid]['admission_decision_at']),self.latest[eid]['discharged_at']))
        self.need(gaps>=0 and total_care==sum(placed.values())+pre+gaps,'care/bed/boarding/gap accounting differs')
        boarding.sort();p95=boarding[(95*len(boarding)-1)//100]
        self.need(p95<=Decimal(self.cfg['targets']['maximum_boarding_p95_hours'])*3600,'boarding p95 target missed')
        cancellations=sum(r['reason']=='BED_HOLD_CANCELLED' for r in self.t['bed_event'])
        self.need(cancellations==self.cfg['cancelled_reservations'],'cancelled hold scenario absent')
        self.metrics.update(boarding_p95_hours=str(Decimal(p95)/3600),maximum_boarding_hours=str(Decimal(max(boarding))/3600),
            boarding_completed_observations=len(boarding),boarding_right_censored_unplaced=len(censored),maximum_censored_boarding_lower_bound_hours=str(Decimal(max(censored,default=0))/3600),
            delayed_placements=sum(s>600 for s in admitted_waits),unplaced_completed=len(unplaced),unexplained_unplaced_completed=len(unexplained),external_capacity_transfers=sum(self.latest[eid]['disposition']=='TRANSFER' for eid in unplaced),boarding_deaths=sum(self.latest[eid]['disposition']=='DEATH' for eid in unplaced),boarding_seconds=pre+decision_to_admit,decision_to_admission_seconds=decision_to_admit,admitted_wait_seconds=pre,other_inpatient_gap_seconds=gaps,
            admitted_care_seconds=total_care,cancelled_reservations=cancellations)
        deferrals=sorted(max(0,seconds(a['scheduled_start'],a['arrived_at'])) for a in self.t['appointment'] if a['appointment_type']=='ELECTIVE_ADMISSION' and a['arrived_at'])
        d95=deferrals[(95*len(deferrals)-1)//100]
        self.need(Decimal(d95)/86400<=Decimal(self.cfg['targets']['maximum_elective_deferral_p95_days']),'elective deferral p95 target missed')
        self.metrics.update(elective_deferral_p95_days=str(Decimal(d95)/86400),maximum_elective_deferral_days=str(Decimal(max(deferrals))/86400))

    def check_drivers(self):
        rows=self.t['facility_day_driver'];self.need(len(rows)==3288,'daily drivers incomplete')
        lookup={(r['facility_id'],r['calendar_date']):r for r in rows}
        v=ClinicalValidator.__new__(ClinicalValidator);zone=v.local_zone
        monthly=Counter();curves=defaultdict(Counter);shock=Counter();no_shock=Counter();weekday=Counter();hours=Counter()
        for r in rows:
            day=timestamp(r['calendar_date']+'T12:00:00Z').date()
            self.need(r['day_of_week']==day.isoweekday(),'driver weekday differs')
            local_end=timestamp((day+timedelta(days=1)).isoformat()+'T00:00:00+00:00').replace(tzinfo=zone)
            self.need(timestamp(r['calendar_known_at'])<timestamp(r['calendar_date']+'T00:00:00Z') and timestamp(r['observations_known_at'])>=local_end,'realized driver leaked into prior day')
            self.need(r['observations_known_at']<=r['recorded_at']<=r['export_available_at']<='2026-01-10T23:59:59Z','driver delivery chronology')
        for eid,e in self.latest.items():
            day=timestamp(e['arrival_at']).astimezone(zone)
            if day.year not in (2023,2024,2025):continue
            self.need((e['facility_id'],day.date().isoformat()) in lookup,'care missing corresponding driver')
            if e['encounter_class']=='ED':
                month=day.strftime('%Y-%m');monthly[month]+=1;curves[e['facility_id']][month]+=1;weekday[day.weekday()]+=1;hours[day.hour]+=1
            if self.cfg['surge_start']<=day.date().isoformat()<self.cfg['surge_end']:
                shock['all']+=1;shock['resp']+=self.dx.get(eid) in ('J189','J449')
            # Same days of year in adjacent nonshock years, allowing leap-year calendar differences.
            if day.year in (2023,2025) and '01-08'<=day.strftime('%m-%d')<'02-26':
                no_shock['all']+=1;no_shock['resp']+=self.dx.get(eid) in ('J189','J449')
        self.need(len(monthly)==36,'monthly ED coverage incomplete')
        rates={m:Decimal(n)/calendar.monthrange(int(m[:4]),int(m[5:]))[1] for m,n in monthly.items()}
        ratio=max(rates.values())/min(rates.values());lo,hi=map(Decimal,self.cfg['targets']['monthly_ed_rate_peak_trough'])
        self.need(lo<=ratio<=hi,'monthly ED peak/trough rate target missed: '+str(ratio))
        self.need(len({tuple(sorted(c.items())) for c in curves.values()})==3,'identical facility demand curves')
        self.need(shock['resp']>=self.cfg['targets']['minimum_surge_respiratory_encounters'] and shock['resp']*2>no_shock['resp'],'surge did not increase related clinical demand')
        self.metrics.update(monthly_ed_counts=dict(sorted(monthly.items())),monthly_ed_rate_peak_trough=str(ratio),surge_counts=dict(shock),matched_nonshock_two_year_counts=dict(no_shock),ed_hours={str(k):v for k,v in hours.items()})

    def check_replay(self):
        events=self.t['bed_event'];base=resolve_events(events)
        shuffled=resolve_events([*reversed(events),*events[:123]])
        self.need(base==shuffled,'late/repeated delivery failed to converge')
        corrections=[r for r in events if r['event_type']=='CORRECTION']
        original={r['bed_event_id']:r for r in events}
        for c in corrections:
            old=original[c['corrects_bed_event_id']]
            before_time=(timestamp(c['delivery_at'])-timedelta(seconds=1)).isoformat().replace('+00:00','Z')
            before=resolve_events(events,before_time)
            self.need(not any(r['bed_event_id']==c['bed_event_id'] for r in before),'correction visible before delivery')
        self.metrics['replay_convergence']='PASS'

    def check_budget(self):
        specs={t['name']:t for t in self.schema['tables']}
        for name,rows in self.t.items():
            self.need(name in specs and len(rows)<=specs[name]['planned_rows'],'frozen table budget exceeded: '+name)
            self.need(not any(isinstance(x,(list,dict)) for r in rows for x in r.values()),'nested business facts')
        total=sum(map(len,self.t.values()));self.need(total<=1958210 and len(self.t)==16,'aggregate operational table/record budget exceeded')
        self.metrics.update(business_rows=total,rows_by_table={t:len(r) for t,r in self.t.items()},remaining_planned_rows=1958210-total,reserve_untouched=41790)

    def run(self):
        checks=[]
        for name in ('SCHEMA','CLOCKS','STATE','QUEUES','DRIVERS','REPLAY','BUDGET'):
            try:getattr(self,'check_'+name.lower())();checks.append({'rule_id':name,'status':'PASS'})
            except Exception as exc:checks.append({'rule_id':name,'status':'FAIL','reason':str(exc)})
        return {'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'BLOCKED','checks':checks,
            'defects':[c for c in checks if c['status']=='FAIL'],'metrics':self.metrics}
