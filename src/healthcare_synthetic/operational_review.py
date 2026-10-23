"""Content-bound operational plausibility review, separate from final release approval."""
import hashlib
import json
from collections import defaultdict
from decimal import Decimal

from .operational_validation import bed_intervals, seconds, START, CUTOFF


def render_operations(tables,cfg):
    enc={r['encounter_version_id']:r for r in tables['encounter']};latest={}
    for e in tables['encounter']:
        if e['encounter_id'] not in latest or e['revision_no']>latest[e['encounter_id']]['revision_no']:latest[e['encounter_id']]=e
    people={r['patient_version_id']:r for r in tables['patient']};locations={r['location_id']:r for r in tables['location']}
    facilities={r['facility_id']:r for r in tables['facility']}
    intervals=defaultdict(list)
    for bid,eid,a,b in bed_intervals(tables['bed_event'],enc):intervals[eid].append((bid,a,b))
    for values in intervals.values():values.sort(key=lambda value:(value[1],value[0]))
    by_case=defaultdict(list)
    for r in tables['bed_event']:
        if r['encounter_version_id']:by_case[enc[r['encounter_version_id']]['encounter_id']].append(r)
    documents=defaultdict(list)
    for r in tables['clinical_event']:
        if r['source_record_id'].endswith(('/placement-assessment','/placement-disposition','/transfer-referral')):documents[enc[r['encounter_version_id']]['encounter_id']].append(r)
    candidates={eid:e for eid,e in latest.items() if e['encounter_class']=='IPD'}
    features={}
    for eid,e in candidates.items():
        iv=intervals[eid];f={e['facility_id'],e['disposition'],e['admission_source']}
        if e['carry_in']:f.add('CARRY_IN')
        if any(locations[b]['service_line']=='ICU' for b,_,_ in iv):f.add('ICU_STEPDOWN' if len(iv)>1 else 'ICU')
        wait=seconds(max(START,e['admission_decision_at']),iv[0][1]) if iv else seconds(max(START,e['admission_decision_at']),e['discharged_at'] or CUTOFF)
        if not iv and e['disposition']=='TRANSFER':f.add('UNMET_EXTERNAL_TRANSFER')
        if not iv and e['disposition']=='DEATH':f.add('BOARDING_DEATH')
        if any(r['source_record_id'].endswith('/placement-assessment') for r in documents[eid]):f.add('PRIVATE_ISOLATION')
        if wait>3600:f.add('BOARDING_OVER_HOUR')
        if wait>86400:f.add('BOARDING_OVER_DAY')
        if e['admission_source']=='TRANSFER':f.add('SITE_TRANSFER')
        if e['arrival_at'].startswith('2024-06') or e['arrival_at'].startswith('2024-07'):f.add('MAINTENANCE_SEASON')
        features[eid]=f
    selected=[];covered=set()
    while len(selected)<cfg['review_cases']:
        remaining=[eid for eid in candidates if eid not in selected]
        choice=min(remaining,key=lambda eid:(-len(features[eid]-covered),hashlib.sha256(eid.encode()).hexdigest()))
        selected.append(choice);covered.update(features[choice])
    lines=['# Operational patient-flow review','',
        'Phase 4: user-designated synthetic operational plausibility review. Times are UTC. No licensed clinical endorsement.',
        'Admission care includes monitored boarding; only physical licensed-bed intervals contribute to bed occupancy.','']
    source=hashlib.sha256();mirrored=0
    for i,eid in enumerate(selected,1):
        e=candidates[eid];p=people[e['patient_version_id']];iv=intervals[eid]
        wait=seconds(max(START,e['admitted_at']),iv[0][1]) if iv else seconds(max(START,e['admitted_at']),e['discharged_at'] or CUTOFF)
        lines.extend([f"## Case {i}: {p['given_name']} {p['family_name']}",'',
            f"Birth {p['birth_date']}; recorded sex {p['administrative_sex']}; {facilities[e['facility_id']]['facility_name']}; strata: {', '.join(sorted(features[eid]))}.",
            f"Encounter {eid}; episode {e['episode_id']}; acuity {e['initial_acuity']}; {e['arrival_at']} arrival; {e['admission_decision_at']} decision; {e['admitted_at']} admission; {e['discharged_at'] or 'CENSORED'} end; {e['disposition']}.",
            f"Time from admission/opening to first placement: {Decimal(wait)/3600:.3f} hours."])
        mirrored+=1
        for bid,a,b in iv:
            lines.append(f"- {locations[bid]['location_code']}: {a} to {b}, {Decimal(seconds(a,b))/3600:.3f} hours.");mirrored+=1
        for r in sorted(by_case[eid],key=lambda r:(r['effective_at'],0 if r['event_type']=='VACATE' else 1,r['bed_location_id'],r['sequence_no'])):
            lines.append(f"- {r['effective_at']} {r['event_type']}: {r['reason']}; transfer {r['transfer_group_id'] or 'none'}; delivered {r['delivery_at']}.");mirrored+=1
        for r in sorted(documents[eid],key=lambda r:(r['occurred_at'],r['clinical_event_version_id'])):
            lines.append(f"- Source operational note @ {r['occurred_at']}: {r['text_value']}");mirrored+=1
        lines.append('')
        facts=sorted((r for r in tables['encounter'] if r['encounter_id']==eid),key=lambda r:r['revision_no'])+sorted(by_case[eid],key=lambda r:r['bed_event_id'])+sorted(documents[eid],key=lambda r:r['clinical_event_version_id'])
        for r in facts:source.update(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()+b'\n')
    lines+=['## Capacity and source correction review','']
    special=[r for r in tables['bed_event'] if r['reason'] in ('PLANNED_EMPTY_BED_MAINTENANCE','MAINTENANCE_COMPLETE','PLANNED_MAINTENANCE_STAFF_DISABLED','STAFFED_CAPACITY_RESTORED','BED_HOLD_CANCELLED') or r['event_type']=='CORRECTION']
    for r in sorted(special,key=lambda r:(r['effective_at'],r['bed_location_id'],r['sequence_no'])):
        lines.append(f"- {locations[r['bed_location_id']]['location_code']} ({r['bed_location_id']}): {r['effective_at']} {r['event_type']} {r['reason']}; service {r['service_state']}; staffing {r['staffing_enabled']}; reserved {r['reserved']}; corrects {r['corrects_bed_event_id'] or 'none'}.")
        source.update(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()+b'\n');mirrored+=1
    body='\n'.join(lines).rstrip()+'\n'
    return body,{'cases':len(selected),'encounter_ids':selected,'strata':sorted(covered),'sample_sha256':hashlib.sha256(body.encode()).hexdigest(),
                 'selected_facts_sha256':source.hexdigest(),'mirror_rows':mirrored,'mirror_bytes':len(body.encode())}


def review_gate(selection,decision):
    passed=bool(decision and decision.get('status')=='APPROVED' and decision.get('cases_reviewed')==selection['cases']>=100
        and decision.get('sample_sha256')==selection['sample_sha256'] and decision.get('selected_facts_sha256')==selection['selected_facts_sha256']
        and decision.get('review_scope')=='USER_DESIGNATED_SYNTHETIC_OPERATIONAL_PLAUSIBILITY' and decision.get('licensed_clinical_endorsement') is False
        and not decision.get('unresolved_critical_findings',['review missing']))
    return {'status':'PASS' if passed else 'PENDING_REVIEW','cases':selection['cases'],'sample_sha256':selection['sample_sha256'],'licensed_clinical_endorsement':False}
