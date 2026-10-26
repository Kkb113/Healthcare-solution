"""Propagate actual capacity timing into immutable clinical source revisions before publication."""
from collections import defaultdict
from datetime import timedelta

from .clinical_generation import CUTOFF, START, instant, source_version, stamp
from .core import age_on
from .core import stable_id


TIME_FIELDS=('arrival_at','admission_decision_at','admitted_at','medically_ready_at','discharged_at','known_from','known_to','recorded_at','export_available_at')
CONDITION_TIMES=('onset_at','resolved_at','valid_from','valid_to','known_from','known_to','recorded_at','export_available_at')


def external_transfer(sim,eid,at):
    """Observed external disposition after a bounded compatible-capacity wait."""
    e=sim.latest[eid];rows=sim.histories[eid]
    if e['revision_no']==2:
        final={**e,'encounter_version_id':stable_id('encounter_version',eid,3),'revision_no':3,'source_record_id':eid+'/v3'}
        rows.append(final);sim.t['encounter'].append(final);sim.context[final['encounter_version_id']]=final;sim.latest[eid]=final;e=final
    rows[-2]['known_to']=stamp(at)
    e.update(known_from=stamp(at),known_to=None,recorded_at=stamp(at),export_available_at=stamp(at+timedelta(hours=2)),
             discharged_at=stamp(at),disposition='TRANSFER',medically_ready_at=None)
    contexts={r['encounter_version_id'] for r in rows}
    sim.t['clinical_condition']=[c for c in sim.t['clinical_condition'] if not(c['encounter_version_id'] in contexts and c['revision_no']>1)]
    for c in sim.conditions_by_enc[eid]:
        if c['revision_no']==1:c['known_to']=None
    cause=','.join(sorted(sim.queue_causes.get(eid,{'COMPATIBLE_CAPACITY_EXHAUSTED'})))
    key=eid+'/placement-disposition'
    body=f"Placement disposition for encounter {eid}: external transfer at {stamp(at)} after {sim.cfg['maximum_admission_to_escalation_hours']} hours from inpatient admission awaiting a compatible bed. Cause: {cause}. Receiving care and later outcome are outside the modeled network."
    sim.t.setdefault('clinical_event',[]).append(sim.g.row('clinical_event',key,at,clinical_event_version_id=stable_id('clinical_event_version',key,1),clinical_event_id=stable_id('clinical_event',key),
        encounter_version_id=e['encounter_version_id'],author_assignment_id=sim.g.clinician(e['facility_id'],at,'Internal Medicine'),event_type='DOCUMENT',occurred_at=stamp(at),
        document_signed_at=stamp(at),document_type='PROGRESS_NOTE',text_value=body,status='COMPLETED',aggregation='NOT_APPLICABLE',revision_no=1,known_from=stamp(at),known_to=None))


def boarding_death(sim,eid,at):
    e=sim.latest[eid];cause=','.join(sorted(sim.queue_causes.get(eid,{'COMPATIBLE_CAPACITY_EXHAUSTED'})))
    key=eid+'/placement-disposition'
    body=f"Placement disposition for encounter {eid}: observed death at {stamp(at)} before compatible placement. Care continued in monitored boarding; no licensed bed occupancy is asserted. Cause: {cause}."
    sim.t.setdefault('clinical_event',[]).append(sim.g.row('clinical_event',key,at,clinical_event_version_id=stable_id('clinical_event_version',key,1),clinical_event_id=stable_id('clinical_event',key),
        encounter_version_id=e['encounter_version_id'],author_assignment_id=sim.g.clinician(e['facility_id'],at,'Internal Medicine'),event_type='DOCUMENT',occurred_at=stamp(at),document_signed_at=stamp(at),
        document_type='PROGRESS_NOTE',text_value=body,status='COMPLETED',aggregation='NOT_APPLICABLE',revision_no=1,known_from=stamp(at),known_to=None))

def move_encounter(sim,eid,delta):
    if not delta:return
    for row in sim.histories[eid]:
        for field in TIME_FIELDS:
            if row.get(field):row[field]=stamp(instant(row[field])+delta)
    linked={r['encounter_version_id'] for r in sim.histories[eid]}
    for c in sim.conditions_by_enc[eid]:
        if c['encounter_version_id'] in linked:
            for field in CONDITION_TIMES:
                if c.get(field):c[field]=stamp(instant(c[field])+delta)
    for note in [mapping[eid] for mapping in (sim.placement_notes,sim.referral_notes) if eid in mapping]:
        for field in ('occurred_at','document_signed_at','known_from','recorded_at','export_available_at'):
            note[field]=stamp(instant(note[field])+delta)


def extend_completion(sim,eid,delay):
    """Boarding is care, but delays completion of the modeled ward stabilization work.

    A delayed home discharge then waits for the next daytime discharge window.
    A zero delay only realigns a discharge that an earlier move took out of it.
    """
    if delay<timedelta(0):return
    e=sim.latest[eid]
    if not e['discharged_at'] or e['disposition']=='DEATH':return
    old=instant(e['discharged_at']);new=old+delay
    if e['disposition']=='HOME':new=sim.g.discharge_window(eid,new)
    if new==old:return
    for r in sim.histories[eid]:
        if r['known_to']==stamp(old):r['known_to']=stamp(new)
    for field in ('known_from','recorded_at','export_available_at','discharged_at'):
        if e.get(field):e[field]=stamp(instant(e[field])+(new-old))
    if e.get('medically_ready_at'):e['medically_ready_at']=stamp(instant(e['medically_ready_at'])+delay)
    contexts={r['encounter_version_id'] for r in sim.histories[eid]}
    for c in sim.conditions_by_enc[eid]:
        if c['encounter_version_id'] in contexts:
            for field in CONDITION_TIMES:
                if c.get(field)==stamp(old):c[field]=stamp(new)
            if c['revision_no']>1 and c['recorded_at']==stamp(new):c['export_available_at']=stamp(new+timedelta(hours=2))
    # A downstream site handoff is scheduled from actual sending-site completion.
    for successor in sim.successors[eid]:
            move_encounter(sim,successor['encounter_id'],new+sim.transit[successor['encounter_id']]-instant(successor['arrival_at']))
            sim.push(instant(successor['admitted_at']),3,'admit',successor['encounter_id'])
            sim.push(instant(successor['discharged_at']),0,'discharge',successor['encounter_id'])
    sim.push(new,0,'discharge',eid)


def finalize_timing(sim):
    """Censor unobserved outcomes, defer conflicting follow-ups, refresh source snapshots."""
    by_person=defaultdict(list)
    for e in sim.latest.values():by_person[sim.g.by_patient_version[e['patient_version_id']]['patient_id']].append(e)
    deferred=0
    for pid,visits in by_person.items():
        ipd=sorted((e for e in visits if e['encounter_class']=='IPD'),key=lambda e:e['arrival_at'])
        busy=[(instant(e['arrival_at']),min(instant(e['discharged_at'] or stamp(CUTOFF)),CUTOFF)) for e in ipd]
        linked_episodes={e['episode_id'] for e in ipd}
        for e in (e for e in visits if e['encounter_class']=='ED' and e['episode_id'] in linked_episodes):
            child=next(i for i in ipd if i['episode_id']==e['episode_id'])
            stay=instant(e['discharged_at'])-instant(e['arrival_at']) if e['discharged_at'] else timedelta(hours=4)
            desired=instant(child['arrival_at'])-stay
            move_encounter(sim,e['encounter_id'],desired-instant(e['arrival_at']))
            busy.append((instant(e['arrival_at']),instant(e['discharged_at'])))
        for e in sorted((e for e in visits if e['encounter_class']!='IPD'),key=lambda e:e['arrival_at']):
            if e['episode_id'] in linked_episodes:
                continue
            begin=instant(e['arrival_at']);duration=instant(e['discharged_at'])-begin
            original=begin
            while any(begin<b and a<begin+duration for a,b in busy):
                begin=max(b for a,b in busy if begin<b and a<begin+duration)+timedelta(hours=1)
                if e['encounter_class']=='OPD':
                    local=begin.astimezone(sim.g.zone).replace(hour=9,minute=0,second=0)
                    if local<begin.astimezone(sim.g.zone):local+=timedelta(days=1)
                    while local.weekday()>=5:local+=timedelta(days=1)
                    begin=local.astimezone(begin.tzinfo)
                if begin+duration>=CUTOFF:
                    # Defer into an earlier free slot in the same reporting window.
                    begin=original-timedelta(days=1)
                    while begin>=START and (any(begin<b and a<begin+duration for a,b in busy) or (e['encounter_class']=='OPD' and begin.astimezone(sim.g.zone).weekday()>=5)):begin-=timedelta(days=1)
                    if begin<START:raise ValueError('no in-window follow-up slot after capacity integration')
                    break
            if begin!=original:move_encounter(sim,e['encounter_id'],begin-original);deferred+=1
            busy.append((begin,begin+duration))
    # Truncate closing revisions and acute resolutions whose outcomes are not observed.
    removed=set()
    for eid,rows in sim.histories.items():
        latest=max(rows,key=lambda r:r['revision_no'])
        if latest['discharged_at'] and (instant(latest['discharged_at'])>=CUTOFF or eid in sim.waiting or eid in sim.reserving):
            rows.remove(latest);removed.add(latest['encounter_version_id'])
            rows[-1]['known_to']=None;sim.latest[eid]=rows[-1]
            contexts={r['encounter_version_id'] for r in rows}|{latest['encounter_version_id']}
            sim.t['clinical_condition']=[c for c in sim.t['clinical_condition'] if not(c['encounter_version_id'] in contexts and c['revision_no']>1)]
            for c in sim.t['clinical_condition']:
                if c['encounter_version_id'] in contexts and c['revision_no']==1:c['known_to']=None
    sim.t['encounter']=[r for r in sim.t['encounter'] if r['encounter_version_id'] not in removed]
    for eid,rows in sim.histories.items():
        e=max(rows,key=lambda r:r['revision_no']);at=instant(e['arrival_at']);pid=sim.g.by_patient_version[e['patient_version_id']]['patient_id']
        patient=source_version(sim.g.patients[pid],at);cov=source_version(sim.g.coverage[pid],at)
        code=sim.diagnosis.get(eid,'R079')
        specialty='Emergency Medicine' if e['encounter_class']=='ED' else 'General Surgery' if code=='K8010' else 'Orthopedics' if code=='M1711' else 'Internal Medicine'
        for row in rows:
            row['patient_version_id']=patient['patient_version_id'];row['coverage_version_id']=cov['coverage_version_id']
            row['attending_assignment_id']=sim.g.clinician(e['facility_id'],at,specialty)
        for c in sim.conditions_by_enc[eid]:
            if c['encounter_version_id'] in {r['encounter_version_id'] for r in rows}:
                c['patient_version_id']=patient['patient_version_id']
                cat=sim.g.by_catalog[c['catalog_item_id']]
                c['catalog_item_id']=sim.g.code(cat['domain'],cat['code'],instant(c['valid_from']))['catalog_item_id']
    # Rebind predecessors to source revisions actually known at the actual arrival.
    all_by_person=defaultdict(list)
    for eid,rows in sim.histories.items():all_by_person[sim.g.by_patient_version[rows[0]['patient_version_id']]['patient_id']].append((eid,rows))
    for visits in all_by_person.values():
        prior=[]
        for eid,rows in sorted(visits,key=lambda item:(item[1][0]['arrival_at'],item[0])):
            e=rows[0];available=[r for _,history in prior for r in history if r['known_from']<=e['arrival_at'] and r['arrival_at']<e['arrival_at']]
            existing=e['previous_encounter_version_id']
            if existing:
                old=sim.context.get(existing)
                if old is None or old['known_from']>e['arrival_at'] or old['arrival_at']>=e['arrival_at']:
                    replacement=max(available,key=lambda r:(r['arrival_at'],r['revision_no']))['encounter_version_id'] if available else None
                    for row in rows:row['previous_encounter_version_id']=replacement
            prior.append((eid,rows))
    # Occupancy references are knowledge snapshots, never retrospective closing versions.
    for event in sim.events:
        if event['encounter_version_id']:
            eid=sim.context[event['encounter_version_id']]['encounter_id']
            event['encounter_version_id']=sim.context_at(eid,instant(event['effective_at']))
    for appointment in sim.t.get('appointment',[]):
        key=appointment['resulting_encounter_version_id']
        if key and appointment['arrived_at']:
            actual=sim.context[key]['arrival_at']
            appointment['arrived_at']=actual;appointment['recorded_at']=actual
            appointment['export_available_at']=stamp(instant(actual)+timedelta(hours=2))
            if appointment['booked_at']>actual:raise ValueError('deferred appointment moved before booking knowledge')
    for eid,note in sim.placement_notes.items():
        e=sim.latest[eid];at=instant(note['occurred_at']);pid=sim.g.by_patient_version[e['patient_version_id']]['patient_id']
        p=source_version(sim.g.patients[pid],at)
        note['text_value']=f"Placement assessment for {p['given_name']} {p['family_name']}, age {age_on(p['birth_date'],at.astimezone(sim.g.zone).date().isoformat())}: suspected transmissible respiratory illness; isolation-capable private room requested. Recorded at {stamp(at)}."
        note['encounter_version_id']=sim.context_at(eid,at);note['author_assignment_id']=sim.g.clinician(e['facility_id'],at,'Internal Medicine')
    for eid,note in sim.referral_notes.items():
        e=sim.latest[eid];at=instant(note['occurred_at']);note['encounter_version_id']=sim.context_at(eid,at)
        note['author_assignment_id']=sim.g.clinician(e['facility_id'],at,'Internal Medicine')
        if e['admission_source']=='TRANSFER':
            code=next(f['facility_code'] for f in sim.t['facility'] if f['facility_id']==e['facility_id'])
            note['text_value']=f"Transfer coordination for encounter {eid}: accepted continuation at {code}; receiving arrival is observed at {e['arrival_at']}. Later care outcome is not yet established."
    return deferred
