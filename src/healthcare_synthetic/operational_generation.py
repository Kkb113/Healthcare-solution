"""Finite-capacity event simulation. All durable clinical and bed facts use frozen tables."""
from __future__ import annotations

import heapq
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from .clinical_generation import START, CUTOFF, source_version, stamp
from .core import digest, instant, stable_id
from .operational_timing import extend_completion, move_encounter, finalize_timing, external_transfer, boarding_death


def connect_site_transfers(generator, journeys, number, operational):
    """Split selected continuous medical care; regenerate dependent care afterwards."""
    histories = defaultdict(list)
    for r in journeys['encounter']: histories[r['encounter_id']].append(r)
    latest = {k: max(v, key=lambda r: r['revision_no']) for k, v in histories.items()}
    primary = {r['encounter_version_id']: r for r in journeys['clinical_condition'] if r['condition_type'] == 'DIAGNOSIS' and r['revision_no'] == 1}
    context = {r['encounter_version_id']: r for r in journeys['encounter']}
    diagnoses = {context[k]['encounter_id']: c for k,c in primary.items()}
    selected = sorted((e for e in latest.values() if e['encounter_class'] == 'IPD' and e['disposition'] == 'HOME'
                       and not e['planned'] and not e['carry_in'] and e['arrival_at'][:4] == '2024'
                       and (instant(e['discharged_at']) - instant(e['arrival_at'])).days >= 7
                       and generator.by_catalog[diagnoses[e['encounter_id']]['catalog_item_id']]['code'] != 'J189'), key=lambda r: r['encounter_id'])[:number]
    if len(selected) != number: raise ValueError('insufficient eligible continuous transfer cases')
    for old in selected:
        eid = old['encounter_id']; begin = instant(old['arrival_at']) + timedelta(days=3)
        final_end = instant(old['discharged_at'])
        original_final = histories[eid][-1] if histories[eid][-1]['revision_no'] == 3 else max(histories[eid],key=lambda r:r['revision_no'])
        for r in histories[eid]:
            if r['revision_no'] == 2: r['known_to'] = stamp(begin)
        original_final.update(known_from=stamp(begin), recorded_at=stamp(begin), export_available_at=stamp(begin+timedelta(hours=2)),
                              discharged_at=stamp(begin), disposition='TRANSFER', medically_ready_at=None)
        new_id = stable_id('encounter', eid, 'continuous-site-transfer')
        fid = generator.facilities[(generator.facilities.index(old['facility_id'])+1)%3]
        codes={r['facility_id']:r['facility_code'] for r in generator.t['facility']}
        route='|'.join(sorted((codes[old['facility_id']],codes[fid])))
        minutes=operational['site_transport_minutes'][route]+generator.n(eid,'transport-handover',operational['site_transport_handover_max_minutes']+1)
        at = begin + timedelta(minutes=minutes)
        pid = generator.by_patient_version[old['patient_version_id']]['patient_id']
        base = {k: old[k] for k in ('episode_id','initial_acuity')}
        base.update(encounter_id=new_id, previous_encounter_version_id=original_final['encounter_version_id'],
            patient_version_id=source_version(generator.patients[pid], at)['patient_version_id'], facility_id=fid,
            location_id=generator.locations[fid,'MED'], coverage_version_id=source_version(generator.coverage[pid],at)['coverage_version_id'],
            attending_assignment_id=generator.clinician(fid,at,'Internal Medicine'), encounter_class='IPD', admission_source='TRANSFER',
            arrival_at=stamp(at), disposition='OPEN', planned=False, carry_in=False)
        state, rows = base, []
        for rev,(known,changes) in enumerate(((at,{}),(at+timedelta(minutes=15),{'admission_decision_at':stamp(at),'admitted_at':stamp(at+timedelta(minutes=15))}),
                    (final_end,{'discharged_at':stamp(final_end),'medically_ready_at':stamp(final_end-timedelta(hours=1)),'disposition':'HOME'})),1):
            state = {**state, **changes}
            row = generator.row('encounter', f'{new_id}/v{rev}', known, encounter_version_id=stable_id('encounter_version',new_id,rev),
                revision_no=rev, known_from=stamp(known), known_to=None, **state)
            if rows: rows[-1]['known_to'] = stamp(known)
            rows.append(row)
        journeys['encounter'].extend(rows)
        known = at+timedelta(minutes=25)
        cat = generator.code('DIAGNOSIS',generator.by_catalog[diagnoses[eid]['catalog_item_id']]['code'],known)
        cid = stable_id('clinical_condition',new_id,'primary')
        journeys['clinical_condition'].append(generator.row('clinical_condition',cid+'/v1',known,
            condition_version_id=stable_id('clinical_condition_version',cid,1),condition_id=cid,
            patient_version_id=base['patient_version_id'],encounter_version_id=rows[1]['encounter_version_id'],catalog_item_id=cat['catalog_item_id'],
            condition_type='DIAGNOSIS',status='ACTIVE',diagnosis_rank=1,present_on_admission='Y',onset_at=stamp(at),
            severity='SEVERE' if base['initial_acuity']<=2 else 'MODERATE',revision_no=1,valid_from=stamp(known),valid_to=None,known_from=stamp(known),known_to=None))
    return journeys


class FlowSimulator:
    def __init__(self, tables, generator, cfg):
        self.t,self.g,self.cfg = tables,generator,cfg
        self.locations = {r['location_id']:r for r in tables['location']}
        self.beds = sorted((r for r in tables['location'] if r['location_type']=='BED'),key=lambda r:(r['facility_id'],r['location_code']))
        self.beds_by_site=defaultdict(list);self.beds_by_room=defaultdict(list)
        for bed in self.beds:
            self.beds_by_site[bed['facility_id']].append(bed);self.beds_by_room[bed['parent_location_id']].append(bed)
        self.histories=defaultdict(list)
        for e in tables['encounter']: self.histories[e['encounter_id']].append(e)
        self.latest={k:max(v,key=lambda r:r['revision_no']) for k,v in self.histories.items()}
        self.context={r['encounter_version_id']:r for r in tables['encounter']}
        cat={r['catalog_item_id']:r for r in tables['catalog_item']}
        self.diagnosis={self.context[c['encounter_version_id']]['encounter_id']:cat[c['catalog_item_id']]['code'] for c in tables['clinical_condition'] if c['encounter_version_id'] and c['revision_no']==1 and c['diagnosis_rank']==1}
        self.placement_notes={self.context[r['encounter_version_id']]['encounter_id']:r for r in tables.get('clinical_event',[]) if r['source_record_id'].endswith('/placement-assessment')}
        self.referral_notes={self.context[r['encounter_version_id']]['encounter_id']:r for r in tables.get('clinical_event',[]) if r['source_record_id'].endswith('/transfer-referral')}
        self.conditions_by_enc=defaultdict(list);self.successors=defaultdict(list);self.ipd_by_person=defaultdict(list)
        for c in tables['clinical_condition']:
            if c['encounter_version_id']:self.conditions_by_enc[self.context[c['encounter_version_id']]['encounter_id']].append(c)
        for e in self.latest.values():
            if e['admission_source']=='TRANSFER':self.successors[self.context[e['previous_encounter_version_id']]['encounter_id']].append(e)
            if e['encounter_class']=='IPD':self.ipd_by_person[self.g.by_patient_version[e['patient_version_id']]['patient_id']].append(e)
        self.state={b['location_id']:dict(occupancy_state='EMPTY',service_state='IN_SERVICE',staffing_enabled=True,reserved=False,encounter_version_id=None) for b in self.beds}
        self.seq=defaultdict(int); self.recording={};self.events=[]; self.heap=[]; self.serial=0
        self.waiting={}; self.placed={}; self.reserving={}; self.intervals=[]; self.active_intervals={};self.completed=set()
        self.close_requests={}; self.closed_until={}; self.queue_causes={}; self.cancelled=0
        self.elective_windows=set()
        self.site_pairs={}
        self.transit={}
        for e in self.latest.values():
            if e['admission_source']=='TRANSFER':
                prior=self.context[e['previous_encounter_version_id']]
                self.transit[e['encounter_id']]=instant(e['arrival_at'])-instant(prior['discharged_at'])
                group=stable_id('site_transfer',prior['encounter_id'],e['encounter_id'])
                self.site_pairs[prior['encounter_id']]=group; self.site_pairs[e['encounter_id']]=group

    def push(self,at,priority,kind,key):
        if at>=CUTOFF: return
        self.serial+=1; heapq.heappush(self.heap,(at,priority,str(key),self.serial,kind,key))

    def context_at(self,eid,at):
        available=[r for r in self.histories[eid] if r['known_from']<=stamp(at)]
        if not available:raise ValueError(f'encounter source context unavailable: {eid}, event {stamp(at)}, arrival {self.histories[eid][0]["arrival_at"]}')
        return max(available,key=lambda r:r['revision_no'])['encounter_version_id']

    def emit(self,bid,at,kind,reason,group=None,**changes):
        self.state[bid].update(changes); self.seq[bid]+=1
        key=stable_id('bed_event',bid,self.seq[bid])
        recorded=at+timedelta(seconds=self.g.n(key,'record-lag',30))
        recorded=max(recorded,self.recording.get(bid,recorded-timedelta(seconds=1))+timedelta(seconds=1))
        self.recording[bid]=recorded
        delivery=recorded+timedelta(seconds=5+self.g.n(key,'delivery-lag',90))
        if self.g.n(key,'late-delivery',100)<2: delivery+=timedelta(hours=6)
        row=self.g.row('bed_event',key,recorded,bed_event_id=key,bed_location_id=bid,sequence_no=self.seq[bid],
            effective_at=stamp(at),event_type=kind,reason=reason,transfer_group_id=group,delivery_at=stamp(delivery),**self.state[bid])
        row['export_available_at']=stamp(delivery)
        self.events.append(row)
        return row

    def requirement(self,e):
        code=self.diagnosis[e['encounter_id']]
        return 'SURGERY' if e['planned'] else 'MEDICINE', e['encounter_id'] in self.placement_notes

    def compatible(self,bid,e,icu=False):
        bed=self.locations[bid]; s=self.state[bid]
        if bed['facility_id']!=e['facility_id'] or s['occupancy_state']!='EMPTY' or s['service_state']!='IN_SERVICE' or not s['staffing_enabled'] or s['reserved']: return False
        service,isolation=self.requirement(e)
        if icu != (bed['service_line']=='ICU'): return False
        # Both adult wards are configured med-surg flex units. Their service line
        # expresses primary responsibility, while ICU remains a separate capability.
        if not icu and bed['service_line'] not in ('MEDICINE','SURGERY'): return False
        if isolation and not bed['isolation_capable']: return False
        p=self.g.by_patient_version[e['patient_version_id']]
        for peer in self.beds_by_room[bed['parent_location_id']]:
            if peer['parent_location_id']!=bed['parent_location_id'] or peer['location_id']==bid: continue
            state=self.state[peer['location_id']]
            other=state['encounter_version_id']
            if other:
                enc=self.context[other]; person=self.g.by_patient_version[enc['patient_version_id']]
                if p['administrative_sex'] not in ('M','F') or person['administrative_sex']!=p['administrative_sex'] or isolation or self.requirement(enc)[1]: return False
            for reserved_eid,reserved_bid in self.reserving.items():
                if reserved_bid==peer['location_id']:
                    enc=self.latest[reserved_eid]; person=self.g.by_patient_version[enc['patient_version_id']]
                    if p['administrative_sex'] not in ('M','F') or person['administrative_sex']!=p['administrative_sex'] or isolation or self.requirement(enc)[1]: return False
        return True

    def choose(self,e,icu=False):
        possible=[b for b in self.beds_by_site[e['facility_id']] if self.compatible(b['location_id'],e,icu)]
        def score(b):
            peers=sum(self.state[x['location_id']]['occupancy_state']=='OCCUPIED' for x in self.beds_by_room[b['parent_location_id']])
            return (b['isolation_capable'] and not self.requirement(e)[1],-peers,b['service_line']!=self.requirement(e)[0],b['location_code'])
        return min(possible,key=score)['location_id'] if possible else None

    def vacate(self,eid,at,reason,group=None):
        bid=self.placed.pop(eid)
        begin=self.active_intervals.pop(eid)
        self.intervals.append((bid,eid,stamp(begin),stamp(at)))
        self.emit(bid,at,'VACATE',reason,group,occupancy_state='DIRTY',encounter_version_id=self.context_at(eid,at),reserved=False)
        self.state[bid]['encounter_version_id']=None
        self.push(at+timedelta(minutes=10),1,'clean',bid)
        self.push(at+timedelta(minutes=60+self.g.n(bid+stamp(at),'clean-minutes',31)),1,'ready',bid)
        return bid

    def occupy(self,eid,bid,at,reason,group=None):
        if eid in self.placement_notes:reason+=';PRIVATE_ISOLATION_PLACEMENT'
        if self.g.by_patient_version[self.latest[eid]['patient_version_id']]['administrative_sex'] not in ('M','F'):reason+=';PRIVATE_ROOM_PLACEMENT'
        self.emit(bid,at,'OCCUPY',reason,group,occupancy_state='OCCUPIED',reserved=False,encounter_version_id=self.context_at(eid,at))
        self.placed[eid]=bid; self.active_intervals[eid]=at
        e=self.latest[eid]
        if self.locations[bid]['service_line']=='ICU':
            when=at+timedelta(hours=12 if 'WARD_OVERFLOW_ICU' in reason else self.cfg['icu_stabilization_hours'])
            if when+timedelta(hours=12)<instant(e['discharged_at'] or stamp(CUTOFF)):
                self.push(when,3,'stepdown',eid)

    def close(self,bid,at):
        if bid not in self.close_requests or self.state[bid]['occupancy_state']!='EMPTY' or self.state[bid]['reserved']: return
        duration=self.close_requests.pop(bid)
        self.emit(bid,at,'STAFF_CHANGE','PLANNED_MAINTENANCE_STAFF_DISABLED',staffing_enabled=False)
        self.emit(bid,at,'SERVICE_CHANGE','PLANNED_EMPTY_BED_MAINTENANCE',service_state='OUT_OF_SERVICE')
        self.push(at+timedelta(days=duration),0,'reopen',bid)

    def dispatch(self,at):
        exhausted=set()
        def priority(item):
            eid,(_,request)=item;e=self.latest[eid]
            rank=0 if e['initial_acuity']==1 else 1 if e['planned'] and eid not in self.placed and at-request>=timedelta(days=self.cfg['elective_priority_aging_days']) else e['initial_acuity']
            return rank,request,eid
        for eid,(icu,request) in sorted(list(self.waiting.items()),key=priority):
            e=self.latest[eid]
            if e['disposition']=='DEATH' and at>=instant(e['discharged_at']): continue
            if e['planned'] and eid not in self.placed:
                local=at.astimezone(self.g.zone)
                if local.weekday()>=5 or not 7<=local.hour<=self.cfg['elective_latest_arrival_hour'] or (local.hour==7 and local.minute<15):
                    self.queue_causes.setdefault(eid,set()).add('ELECTIVE_MORNING_SLOT_REQUIRED')
                    due=local.replace(hour=7,minute=15,second=0)
                    if due<=local:due+=timedelta(days=1)
                    while due.weekday()>=5:due+=timedelta(days=1)
                    token=stamp(due)
                    if token not in self.elective_windows:
                        self.elective_windows.add(token);self.push(due.astimezone(timezone.utc),3,'elective_window',eid)
                    continue
            signature=(e['facility_id'],icu,self.g.by_patient_version[e['patient_version_id']]['administrative_sex'],self.requirement(e)[1])
            bid=None if signature in exhausted else self.choose(e,icu)
            if not bid and not icu and eid not in self.placed:
                # ICU is a physical location: a stable adult ward patient can use
                # an otherwise idle monitored bed, without being labeled ICU care.
                spare=[b for b in self.beds_by_site[e['facility_id']] if self.compatible(b['location_id'],e,True)]
                if len(spare)>1:bid=spare[0]['location_id']
            if not bid:
                exhausted.add(signature)
                self.queue_causes.setdefault(eid,set()).add('COMPATIBLE_CAPACITY_EXHAUSTED')
                if icu:self.queue_causes[eid].add('ICU_STABILIZATION_REQUIRED')
                elif self.requirement(e)[1]:self.queue_causes[eid].add('ISOLATION_COHORT_REQUIRED')
                if any(self.state[b['location_id']]['service_state']!='IN_SERVICE' for b in self.beds_by_site[e['facility_id']]):self.queue_causes[eid].add('MAINTENANCE_REDUCED_CAPACITY')
                continue
            self.waiting.pop(eid)
            if eid in self.placed:
                group=stable_id('ward_transfer',eid,stamp(at))
                self.vacate(eid,at,'INTERNAL_STEPDOWN_OUT',group)
                self.occupy(eid,bid,at,'INTERNAL_STEPDOWN_IN',group)
            else:
                due=at+timedelta(minutes=self.cfg['reservation_minutes'])
                if e['disposition']=='DEATH' and due>=instant(e['discharged_at']):
                    self.waiting[eid]=(icu,request); continue
                self.reserving[eid]=bid
                self.emit(bid,at,'RESERVE','PLACEMENT_PREPARATION',reserved=True)
                self.push(due,2,'place',eid)

    def run(self):
        ipd=[e for e in self.latest.values() if e['encounter_class']=='IPD']
        carry=sorted((e for e in ipd if e['carry_in']),key=lambda e:(e['facility_id'],-(self.diagnosis[e['encounter_id']]=='J189'),e['initial_acuity'],e['encounter_id']))
        # All 57 opening occupants are explicit. Start with four eligible ICU stabilizations/site.
        for fid in self.g.facilities:
            local=[e for e in carry if e['facility_id']==fid]
            critical={e['encounter_id'] for e in sorted(local,key=lambda e:e['initial_acuity'])[:4]}
            for e in local:
                icu=e['encounter_id'] in critical
                if icu and e['initial_acuity']>2:
                    for row in self.histories[e['encounter_id']]: row['initial_acuity']=2
                bid=self.choose(e,icu)
                if bid is None: raise ValueError('opening census cannot be placed compatibly: '+fid)
                self.state[bid].update(occupancy_state='OCCUPIED',encounter_version_id=self.context_at(e['encounter_id'],START))
                self.placed[e['encounter_id']]=bid; self.active_intervals[e['encounter_id']]=START
                if icu:self.push(START+timedelta(days=2),3,'stepdown',e['encounter_id'])
        for b in self.beds:
            state=self.state[b['location_id']];context=state['encounter_version_id']
            private=context and self.context[context]['encounter_id'] in self.placement_notes
            unknown=context and self.g.by_patient_version[self.context[context]['patient_version_id']]['administrative_sex'] not in ('M','F')
            self.emit(b['location_id'],START,'OPENING','OBSERVED_OPENING_CENSUS'+(';PRIVATE_ISOLATION_PLACEMENT' if private else '')+(';PRIVATE_ROOM_PLACEMENT' if unknown else ''))
        for e in ipd:
            eid=e['encounter_id']
            if not e['carry_in']: self.push(instant(e['admitted_at']),3,'admit',eid)
            if e['discharged_at']: self.push(instant(e['discharged_at']),0,'discharge',eid)
        maintenance=[]
        for fid in self.g.facilities:
            beds=[b for b in self.beds if b['facility_id']==fid and b['location_code'] in ('MED-R04-B1','MED-R05-B1','SURG-R04-B1','SURG-R05-B1')]
            maintenance.extend(beds)
        if len(maintenance)!=12: raise ValueError('maintenance inventory mismatch')
        for i,b in enumerate(maintenance):
            self.push(datetime(2024,6,1,6,tzinfo=timezone.utc)+timedelta(days=(i%4)*7),0,'closure_request',(b['location_id'],82 if i==0 else 80))
        while self.heap:
            at,_,_,_,kind,key=heapq.heappop(self.heap)
            if kind=='admit':
                e=self.latest[key]
                if at!=instant(e['admitted_at']):continue
                if key in self.placed or key in self.reserving or key in self.waiting:continue
                if e['admission_source']=='TRANSFER':
                    sender=self.context[e['previous_encounter_version_id']]
                    if sender['encounter_id'] not in self.completed:
                        desired=max(at+timedelta(hours=1),instant(sender['discharged_at'])+self.transit[key]+timedelta(minutes=15))
                        move_encounter(self,key,desired-at)
                        self.push(instant(e['admitted_at']),3,'admit',key)
                        self.push(instant(e['discharged_at']),0,'discharge',key)
                        continue
                pid=self.g.by_patient_version[e['patient_version_id']]['patient_id']
                prior=[p for p in self.ipd_by_person[pid] if p['arrival_at']<e['arrival_at'] and p['episode_id']!=e['episode_id']]
                if prior:
                    previous=max(prior,key=lambda p:p['arrival_at']);end=instant(previous['discharged_at'] or stamp(CUTOFF))
                    if previous['encounter_id'] not in self.completed or end+timedelta(hours=5)>instant(e['arrival_at']):
                        delta=max(timedelta(hours=1),end+timedelta(hours=5)-instant(e['arrival_at']));move_encounter(self,key,delta)
                        self.push(instant(e['admitted_at']),3,'admit',key)
                        if e['discharged_at']:self.push(instant(e['discharged_at']),0,'discharge',key)
                        continue
                icu=not e['planned'] and e['admission_source']!='TRANSFER' and (e['initial_acuity']==1 or e['initial_acuity']==2 and self.g.n(key,'icu-stabilization',100)<self.cfg['icu_selection_percent'])
                self.waiting[key]=(icu,at)
                if not e['planned'] and key not in self.referral_notes:self.push(at+timedelta(hours=self.cfg['maximum_admission_to_escalation_hours']),0,'boarding_limit',key)
            elif kind=='place':
                bid=self.reserving.pop(key)
                e=self.latest[key]
                delay=at-instant(e['admitted_at'])-timedelta(minutes=self.cfg['reservation_minutes'])
                if e['planned']:
                    move_encounter(self,key,delay)
                    if e['discharged_at']:self.push(instant(e['discharged_at']),0,'discharge',key)
                else:extend_completion(self,key,delay)
                reason='SITE_TRANSFER_IN' if key in self.site_pairs and self.latest[key]['admission_source']=='TRANSFER' else ('FIRST_PLACEMENT_AFTER_WAIT:'+','.join(sorted(self.queue_causes[key])) if key in self.queue_causes else 'FIRST_PLACEMENT')
                requested_icu=not e['planned'] and e['admission_source']!='TRANSFER' and (e['initial_acuity']==1 or e['initial_acuity']==2 and self.g.n(key,'icu-stabilization',100)<self.cfg['icu_selection_percent'])
                if self.locations[bid]['service_line']=='ICU' and not requested_icu:reason+=';WARD_OVERFLOW_ICU'
                self.occupy(key,bid,at,reason,self.site_pairs.get(key) if e['admission_source']=='TRANSFER' else None)
            elif kind=='stepdown':
                if key in self.placed:self.waiting[key]=(False,at)
            elif kind=='boarding_limit':
                if key in self.waiting and key not in self.placed:
                    external_transfer(self,key,at)
                    self.waiting.pop(key,None);self.completed.add(key)
            elif kind=='discharge':
                e=self.latest[key]
                if not e['discharged_at'] or at!=instant(e['discharged_at']):continue
                if key not in self.placed and e['disposition']!='DEATH':continue
                if key not in self.placed and e['disposition']=='DEATH':boarding_death(self,key,at)
                self.completed.add(key)
                self.waiting.pop(key,None)
                if key in self.reserving:
                    bid=self.reserving.pop(key); self.emit(bid,at,'RELEASE','PATIENT_NO_LONGER_REQUIRES_PLACEMENT',reserved=False)
                if key in self.placed:self.vacate(key,at,'SITE_TRANSFER_OUT' if key in self.site_pairs and self.latest[key]['admission_source']!='TRANSFER' else 'OBSERVED_CARE_END',self.site_pairs.get(key) if self.latest[key]['admission_source']!='TRANSFER' else None)
            elif kind=='clean':self.emit(key,at,'CLEAN_START','ENVIRONMENTAL_SERVICES_TURNAROUND',occupancy_state='CLEANING')
            elif kind=='ready':
                self.emit(key,at,'READY','CLEANING_COMPLETED',occupancy_state='EMPTY')
                self.close(key,at)
                if self.cancelled<self.cfg['cancelled_reservations'] and self.state[key]['service_state']=='IN_SERVICE':
                    self.emit(key,at,'RESERVE','BED_HOLD_REQUEST',reserved=True)
                    self.push(at+timedelta(minutes=15),1,'cancel_hold',key); self.cancelled+=1
            elif kind=='cancel_hold':
                self.emit(key,at,'RELEASE','BED_HOLD_CANCELLED',reserved=False); self.close(key,at)
            elif kind=='closure_request':
                bid,days=key; self.close_requests[bid]=days; self.close(bid,at)
            elif kind=='reopen':
                self.emit(key,at,'SERVICE_CHANGE','MAINTENANCE_COMPLETE',service_state='IN_SERVICE')
                self.emit(key,at,'STAFF_CHANGE','STAFFED_CAPACITY_RESTORED',staffing_enabled=True)
            if kind in ('admit','stepdown','ready','cancel_hold','reopen','elective_window'):self.dispatch(at)
        for eid,bid in self.placed.items():self.intervals.append((bid,eid,stamp(self.active_intervals[eid]),stamp(CUTOFF)))
        deferred=finalize_timing(self)
        # Source mistakes are retained, then corrected at the original effective instant.
        originals=[r for r in self.events if r['event_type']=='READY' and r['effective_at']<'2025-12-30T00:00:00Z'][:self.cfg['corrected_events']]
        for r in originals:
            correction={**r}; r['service_state']='BLOCKED'; r['reason']='SOURCE_SERVICE_STATUS_ENTRY_ERROR'
            bid=r['bed_location_id']; self.seq[bid]+=1
            known=instant(r['recorded_at'])+timedelta(hours=2)
            correction.update(bed_event_id=stable_id('bed_correction',r['bed_event_id']),source_record_id='correction/'+r['bed_event_id'],
                event_type='CORRECTION',corrects_bed_event_id=r['bed_event_id'],sequence_no=self.seq[bid],reason='CORRECTED_CLEAN_READY_SERVICE_STATUS',
                recorded_at=stamp(known),delivery_at=stamp(known+timedelta(minutes=1)),export_available_at=stamp(known+timedelta(minutes=1)))
            self.events.append(correction)
        # Source sequence follows recording order, including backdated corrections.
        for bid in self.state:
            for sequence,row in enumerate(sorted((r for r in self.events if r['bed_location_id']==bid),key=lambda r:(r['recorded_at'],r['bed_event_id'])),1):row['sequence_no']=sequence
        seconds=sum(int((instant(end)-instant(begin)).total_seconds()) for _,_,begin,end in self.intervals)
        intervals=sorted(self.intervals)
        return {'bed_event':self.events}, {'simulated_interval_count':len(intervals),'simulated_occupied_seconds':seconds,
            'simulated_interval_sha256':digest(intervals),'maintenance_requested_beds':12,'cancelled_reservations':self.cancelled,
            'pending_maintenance_requests':len(self.close_requests),'pending_placement_requests':len(self.waiting),
            'source_corrections':len(originals),'deferred_followup_encounters':deferred}
