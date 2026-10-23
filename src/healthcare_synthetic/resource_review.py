"""Deterministic, content-bound synthetic labor/resource plausibility sample."""
from __future__ import annotations

from collections import defaultdict
import hashlib
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from .core import canonical,digest,age_on
from .operational_review import render_operations
from .operational_validation import bed_intervals


def render_resources(tables,cfg):
    enc={r['encounter_version_id']:r for r in tables['encounter']};latest={}
    for r in tables['encounter']:
        if r['encounter_id'] not in latest or r['revision_no']>latest[r['encounter_id']]['revision_no']:latest[r['encounter_id']]=r
    patients={r['patient_version_id']:r for r in tables['patient']};workers={r['worker_assignment_id']:r for r in tables['worker_assignment']}
    cat={r['catalog_item_id']:r for r in tables['catalog_item']};loc={r['location_id']:r for r in tables['location']}
    facilities={r['facility_id']:r for r in tables['facility']};events=defaultdict(list);notes=[]
    for r in tables['clinical_event']:
        eid=enc[r['encounter_version_id']]['encounter_id'];events[eid].append(r)
        if r['source_record_id'].endswith('/resource-response'):notes.append(r)
    chosen=[];seen_windows=set()
    for r in sorted(notes,key=lambda r:(r['occurred_at'],r['clinical_event_id'])):
        cause=r['text_value'].split('Cause: ')[1].split('.')[0]
        if cause not in ('UNIT_STOCKOUT','CIRCULATING_RN_ABSENCE'):continue
        e=enc[r['encounter_version_id']];planned=r['text_value'].split('planned ')[1].split(';')[0]
        window=(cause,e['facility_id'],datetime.fromisoformat(planned.replace('Z','+00:00')).astimezone(ZoneInfo('America/Chicago')).date().isoformat())
        if window not in seen_windows:
            seen_windows.add(window);chosen.append(e['encounter_id'])
    _,op_selection=render_operations(tables,cfg)
    for eid in op_selection['encounter_ids']:
        if eid not in chosen:chosen.append(eid)
        if len(chosen)==cfg['review_cases']:break
    if len(chosen)!=cfg['review_cases']:raise ValueError('resource review cohort does not meet required count')
    shift_hist=defaultdict(list)
    for r in tables['staff_shift']:shift_hist[r['shift_id']].append(r)
    shift_latest={sid:max(rows,key=lambda x:x['revision_no']) for sid,rows in shift_hist.items()}
    working=defaultdict(list)
    for r in shift_latest.values():
        if r['actual_start'] and r['attendance_status'] in ('WORKED','PUBLISHED'):working[workers[r['worker_assignment_id']]['worker_id']].append(r)
    stock_by_group={r['consumption_group_key']:r for r in tables['inventory_movement'] if r['movement_type']=='CONSUME' and Decimal(r['nonpatient_waste_base'])==0}
    lines=['# Connected workforce and inventory review','',
        'Phase 5 user-designated synthetic plausibility review; no licensed clinical endorsement. Times are UTC.',
        'Shift costs and daily stock-group costs can include other patients; they are not patient-level charges. Final-only attendance was unknown before its source knowledge timestamp.','']
    selected={};zone=ZoneInfo('America/Chicago')
    def remember(table,row):
        primary={'encounter':'encounter_version_id','clinical_event':'clinical_event_version_id','staff_shift':'shift_version_id','inventory_movement':'movement_id','worker_assignment':'worker_assignment_id','patient':'patient_version_id'}[table]
        selected[table,row[primary]]=row
    for i,eid in enumerate(chosen,1):
        e=latest[eid];p=patients[e['patient_version_id']];remember('patient',p)
        for r in tables['encounter']:
            if r['encounter_id']==eid:remember('encounter',r)
        age=age_on(p['birth_date'],datetime.fromisoformat(e['arrival_at'].replace('Z','+00:00')).astimezone(zone).date().isoformat())
        lines.extend([f"## Case {i}: {p['given_name']} {p['family_name']}",'',
            f"Birth {p['birth_date']}; age at arrival {age}; {facilities[e['facility_id']]['facility_name']}; {e['encounter_class']}, acuity {e['initial_acuity']}.",
            f"Encounter {eid}; arrival {e['arrival_at']}; admitted {e['admitted_at'] or 'not applicable'}; end {e['discharged_at'] or 'OPEN at cutoff'}; {e['disposition']}."])
        rows=sorted(events[eid],key=lambda r:(r['occurred_at'],r['clinical_event_version_id']))
        for r in rows:remember('clinical_event',r)
        for r in rows:
            if r['source_record_id'].endswith('/resource-response'):lines.append('- '+r['text_value'])
        medicines=[r for r in rows if r['event_type'] in ('MED_ADMIN','MED_DISPENSE') and r['occurred_at']>='2023-01-01T06:00:00Z']
        operative=[r for r in rows if r['event_type']=='PROCEDURE' and cat[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9')]
        examples=operative+medicines[:1]+(medicines[-1:] if len(medicines)>1 else [])
        for r in examples:
            w=workers[r['author_assignment_id']];remember('worker_assignment',w)
            lines.append(f"- {r['event_type']} {cat[r['catalog_item_id']]['display']} @ {r['occurred_at']}; status {r['status']}; source author {w['given_name']} {w['family_name']}, {w['role']}, {w['specialty']}.")
            matches=sorted((s for s in working[w['worker_id']] if s['actual_start']<=r['occurred_at']<(s['actual_end'] or '2026-01-01T06:00:00Z')),key=lambda s:s['shift_id'])
            for s in matches[:1]:
                for rev in shift_hist[s['shift_id']]:remember('staff_shift',rev)
                remember('worker_assignment',workers[s['worker_assignment_id']])
                lines.append(f"  Attendance {s['actual_start']} to {s['actual_end'] or 'unobserved completion'}; worked/productive/break/OT hours {s['worked_hours']}/{s['productive_hours']}/{s['unpaid_break_hours']}/{s['overtime_hours']}; {w['worker_type']}; whole-shift source cost USD {s['loaded_cost']}; attendance revision known {s['known_from']}.")
            if r['consumption_group_key'] in stock_by_group:
                stock=stock_by_group[r['consumption_group_key']];remember('inventory_movement',stock)
                lines.append(f"  Actual dose {r['dose_quantity']} {r['dose_unit']}; consumed {r['consumed_base_quantity']} {cat[r['catalog_item_id']]['base_unit']}; lot {stock['lot_id']}, expiry {stock['expires_on']}; unit cost USD {stock['unit_cost']}. Daily stock group {stock['consumption_group_key']} totals {-Decimal(stock['quantity_base'])} base units, USD {-Decimal(stock['extended_cost'])}.")
        lines.append('')
    lines.extend(['## Retained labor and cost corrections',''])
    selected_shifts=[]
    for kind in ('ABSENT','ON_LEAVE','PUBLISHED','CANCELLED','WORKED'):
        candidates=sorted((r for r in shift_latest.values() if r['attendance_status']==kind),key=lambda r:r['shift_id'])
        selected_shifts+=candidates[:6]
    rates=sorted((sid for sid,rows in shift_hist.items() if len({r['worker_assignment_id'] for r in rows})>1 and len({r['loaded_cost'] for r in rows})>1))[:12]
    selected_shifts += [shift_latest[sid] for sid in rates]
    for s in sorted({r['shift_id']:r for r in selected_shifts}.values(),key=lambda r:r['shift_id']):
        w=workers[s['worker_assignment_id']]
        lines.append(f"- {w['given_name']} {w['family_name']}, {w['worker_type']} {w['role']}, {loc[s['location_id']]['location_code']}; shift {s['shift_id']}.")
        for rev in sorted(shift_hist[s['shift_id']],key=lambda r:r['revision_no']):
            remember('staff_shift',rev);remember('worker_assignment',workers[rev['worker_assignment_id']])
            lines.append(f"  v{rev['revision_no']} known {rev['known_from']}: {rev['attendance_status']}; planned {rev['planned_start']} to {rev['planned_end']}; actual {rev['actual_start']} to {rev['actual_end']}; worked/productive/nonproductive/unpaid/OT {rev['worked_hours']}/{rev['productive_hours']}/{rev['paid_nonproductive_hours']}/{rev['unpaid_break_hours']}/{rev['overtime_hours']}; USD {rev['loaded_cost']}.")
    lines.extend(['','## Stock returns, expiry and corrections',''])
    for kind in ('EXPIRE','RETURN','ADJUSTMENT'):
        for r in sorted((r for r in tables['inventory_movement'] if r['movement_type']==kind),key=lambda r:r['movement_id'])[:12]:
            remember('inventory_movement',r)
            if r['transfer_group_id']:
                for peer in tables['inventory_movement']:
                    if peer['transfer_group_id']==r['transfer_group_id']:remember('inventory_movement',peer)
            lines.append(f"- {kind} {cat[r['catalog_item_id']]['display']}, {loc[r['location_id']]['location_code']}; lot {r['lot_id']}; effective {r['occurred_at']}, recorded {r['recorded_at']}; quantity {r['quantity_base']}; unit/extended USD {r['unit_cost']}/{r['extended_cost']}; expiry {r['expires_on']}; reverses {r['reverses_movement_id'] or 'none'}.")
    body='\n'.join(lines).rstrip()+'\n';facts=[{'table':t,'key':k,'row':v} for (t,k),v in sorted(selected.items())]
    selection={'cases':len(chosen),'encounter_ids':chosen,'sample_sha256':hashlib.sha256(body.encode()).hexdigest(),
        'selected_facts_sha256':digest(facts),'mirror_rows':len(facts),'mirror_bytes':len(body.encode()),
        'resource_shortage_windows':len(seen_windows),'labor_examples':len({r['shift_id'] for r in selected_shifts})}
    return body,selection


def review_gate(selection,decision):
    passed=bool(decision and decision.get('status')=='APPROVED' and decision.get('review_scope')=='USER_DESIGNATED_SYNTHETIC_RESOURCE_PLAUSIBILITY'
        and decision.get('licensed_clinical_endorsement') is False and decision.get('cases_reviewed',0)>=100
        and decision.get('sample_sha256')==selection['sample_sha256'] and decision.get('selected_facts_sha256')==selection['selected_facts_sha256']
        and not decision.get('unresolved_critical_findings'))
    return {'status':'PASS' if passed else 'PENDING_REVIEW','cases':selection['cases'],'sample_sha256':selection['sample_sha256'],'licensed_clinical_endorsement':False}
