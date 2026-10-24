"""Render deterministic month/facility and rare-case review summaries."""
import argparse
import hashlib
import json
import sys
from collections import Counter,defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.integrated_consumers import connect,rows,latest,selected_allocations,START,END,digest,month,instant,ZONE
from healthcare_synthetic.integrated_generation import read,sha_file

def render():
    candidate=ROOT/'output/integrated-history';m=read(candidate/'manifest.json');db=connect(ROOT/'output/integrated-validation/consumer-index.sqlite3')
    try:
        encounters=rows(db,'encounter');index={r['encounter_version_id']:r for r in encounters};visits=latest(encounters,'encounter_id')
        patients={r['patient_version_id']:r for r in rows(db,'patient')};facilities={r['facility_id']:r for r in rows(db,'facility')}
        cover={r['coverage_version_id']:r for r in rows(db,'patient_coverage')};payers={r['payer_plan_id']:r for r in rows(db,'payer_plan')}
        groups=defaultdict(list);selected={}
        for eid,r in visits.items():
            if START<=r['arrival_at']<END:groups[month(r['arrival_at']),r['facility_id']].append(eid)
        for (period,fid),ids in sorted(groups.items()):
            choice=min(ids,key=lambda eid:digest(['monthly-facility-review',period,fid,eid]));selected[choice]=period+'/'+facilities[fid]['facility_code']
        conditions=[('open_stay',lambda r:r['encounter_class']=='IPD' and not r['discharged_at']),('death',lambda r:r['disposition']=='DEATH'),
                    ('continuous_transfer',lambda r:r['admission_source']=='TRANSFER'),('carry_in',lambda r:r['carry_in'] and r['encounter_class']=='IPD')]
        for tag,predicate in conditions:
            eligible=[eid for eid,r in visits.items() if predicate(r)]
            if not eligible:raise ValueError('review rare stratum absent: '+tag)
            selected.setdefault(min(eligible,key=lambda eid:digest([tag,eid])),tag)
        claims=rows(db,'claim');events=defaultdict(list);headers=defaultdict(list);costs=defaultdict(Decimal);notes={};facts={}
        for r in rows(db,'claim_event'):events[r['claim_id']].append(r)
        for r in claims:headers[index[r['encounter_version_id']]['encounter_id']].append(r)
        for r in selected_allocations(rows(db,'cost_allocation')):
            if r['encounter_version_id']:costs[index[r['encounter_version_id']]['encounter_id']]+=Decimal(r['allocated_amount'])
        for r in rows(db,'clinical_event',"WHERE event_type='DOCUMENT'"):
            eid=index[r['encounter_version_id']]['encounter_id']
            if eid in selected and (eid not in notes or r['known_from']<notes[eid]['known_from']):notes[eid]=r
        body=['# Integrated synthetic history review','',
              'Phase 8. User-designated synthetic business, clinical, workforce, finance and engineering review; no external licensed or vendor endorsement.',
              'One SHA256-selected complete visit context in each of 108 month/facility strata, plus fixed rare-case strata. Identities are fictional. Amounts describe selected capture, not full hospital cost. Open unclaimed care may have charges and unbilled AR; the balances below cover original accounts only. Full-history controls remain mandatory.','',
              '| Stratum | Person / DOB / age at arrival | Hospital / class / acuity / payer | Arrival → discharge | Original-account billed / claim AR / patient cost USD | Context |',
              '| --- | --- | --- | --- | --- | --- |']
        classes=Counter();reviewed=[]
        for eid,tag in sorted(selected.items(),key=lambda item:(item[1],item[0])):
            e=visits[eid];p=patients[e['patient_version_id']];payer=payers[cover[e['coverage_version_id']]['payer_plan_id']]
            birth=date.fromisoformat(p['birth_date']);arrival=instant(e['arrival_at']).astimezone(ZONE).date();age=arrival.year-birth.year-((arrival.month,arrival.day)<(birth.month,birth.day))
            hs=headers[eid];billed=sum((Decimal(h['original_billed_amount']) for h in hs),Decimal(0));ar=sum((Decimal(h['opening_ar'])+sum((Decimal(v['ar_delta']) for v in events[h['claim_id']]),Decimal(0)) for h in hs),Decimal(0))
            labels=Counter(v['event_type'] for h in hs for v in events[h['claim_id']]);classes[e['encounter_class']]+=1
            billed_text=f'{billed:.2f}' if hs else 'NO_ORIGINAL_ACCOUNT';ar_text=f'{ar:.2f}' if hs else 'UNBILLED_SCOPE'
            draft=' DRAFT_AT_CUTOFF;' if hs and all(not h['first_submitted_at'] and not h['carry_in'] for h in hs) else ''
            body.append(f"| {tag} | {p['given_name']} {p['family_name']} / {p['birth_date']} / {age} | {facilities[e['facility_id']]['facility_code']} / {e['encounter_class']} / {e['initial_acuity']} / {payer['payer_type']} | {e['arrival_at']} → {e['discharged_at'] or 'OPEN; outcome UNKNOWN'} | {billed_text} / {ar_text} / {costs[eid]:.2f} | {e['disposition'] or 'UNOBSERVED'};{draft} {dict(labels)}; `{eid}` |")
            facts[eid]={'patient':p,'encounter':e,'claims':hs,'claim_events':[v for h in hs for v in events[h['claim_id']]],'first_note':notes.get(eid),'selected_patient_cost':str(costs[eid])}
            reviewed.append(eid)
        workers=rows(db,'worker_assignment');current=latest(workers,'worker_id');worker_facts={}
        body+=['','## Workforce context strata','',
               '| Hospital / role | Person / DOB | Assignment history / FTE / credential |',
               '| --- | --- | --- |']
        for fid in sorted(facilities):
            for role in ('PHYSICIAN','RN','LPN','THERAPIST','TECHNICIAN','PHARMACIST','HOUSEKEEPING','ADMIN'):
                eligible=[r for r in current.values() if r['facility_id']==fid and r['role']==role]
                if not eligible:raise ValueError('worker review stratum absent: '+fid+'/'+role)
                w=min(eligible,key=lambda r:digest(['worker-role-facility-review',fid,role,r['worker_id']]))
                history=[r for r in workers if r['worker_id']==w['worker_id']];worker_facts[w['worker_id']]=history
                body.append(f"| {facilities[fid]['facility_code']} / {role} | {w['given_name']} {w['family_name']} / {w['birth_date']} | {len(history)} versions / {w['fte']} FTE / {w['credential_code']} through {w['credential_valid_to']}; `{w['worker_id']}` |")
        body+=['','## Recorded limitations','',
               '- Clinical values and treatment pathways demonstrate consistency within a fictional adult model; they are not epidemiologic benchmarks or treatment guidance.',
               '- The 30 selected terminal outcomes exercise late-window boundary cases; this is not a population mortality or survival series.',
               '- Worker birth years and names are preserved while the reviewed master-context migration varies month/day consistently across assignment versions. Patient birth dates remain unchanged; patients aged 100 at opening may age to 103 within the window.',
               '- Selected operational access grants end in revocation. This is a security-history demonstration cohort, not a census of all current authorized hospital users.',
               '- Sparse support/admin attendance, selected drug/supply consumption and bundled services do not represent complete hospital payroll, cost or claims billing.',
               '- Fixed public name distributions and catchment identities are shared across seeds; seeds test connected histories, not new population demographics.',
               '- Axiom native layouts are illustrative archetypes. Customer-specific layout/vendor certification and the estimated 900-report inventory are not implemented.',
               '- Clinical/care, roster and close outcomes remain censored or unknown at the cutoff when not observed. No unknown is recoded as a successful or negative outcome.',
               '- Phase 9 clean-environment release certification and explicit release acceptance remain pending; solution development stays blocked.','']
        text='\n'.join(body);return text,{'reviewed_cases':len(reviewed)+len(worker_facts),'reviewed_patient_cases':len(reviewed),'reviewed_worker_cases':len(worker_facts),
            'monthly_facility_strata':len(groups),'classes':dict(classes),'encounter_ids':reviewed,'worker_ids':sorted(worker_facts),
            'sample_sha256':hashlib.sha256(text.encode()).hexdigest(),'selected_facts_sha256':digest({'patients':facts,'workers':worker_facts}),
            'canonical_business_sha256':m['business_sha256'],'realism_profiles_sha256':sha_file(ROOT/'output/integrated-validation/realism-profiles.json'),
            'review_mirror_case_summaries':len(reviewed)+len(worker_facts),'review_bytes':len(text.encode()),
            'selected_source_fact_mirrors':sum(2+len(v['claims'])+len(v['claim_events'])+(v['first_note'] is not None) for v in facts.values())+sum(len(v) for v in worker_facts.values())}
    finally:db.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'reviews/integrated-history-sample.md');a=p.parse_args()
    body,selection=render();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(body,encoding='utf-8',newline='\n')
    target=ROOT/'output/integrated-validation/review-selection.json';target.write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in selection.items() if k!='encounter_ids'}))
