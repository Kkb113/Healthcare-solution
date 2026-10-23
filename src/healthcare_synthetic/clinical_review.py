"""Content-bound, stratified longitudinal journey review; no hidden business sidecar."""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from .core import chicago
from .master_validation import years


def render_journeys(tables, cfg):
    zone = chicago()
    patients = {r['patient_version_id']: r for r in tables['patient']}
    catalog = {r['catalog_item_id']: r for r in tables['catalog_item']}
    encounters = {r['encounter_version_id']: r for r in tables['encounter']}
    latest, visits, events, diagnoses, revisions = {}, defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    for r in encounters.values():
        eid = r['encounter_id']
        revisions[eid].append(r)
        if eid not in latest or r['revision_no'] > latest[eid]['revision_no']:
            latest[eid] = r
    for r in latest.values(): visits[patients[r['patient_version_id']]['patient_id']].append(r)
    for r in tables['clinical_event']: events[encounters[r['encounter_version_id']]['encounter_id']].append(r)
    for r in tables['clinical_condition']:
        if r['encounter_version_id'] and r['diagnosis_rank'] == 1 and r['revision_no'] == 1:
            diagnoses[encounters[r['encounter_version_id']]['encounter_id']].append(r)
    features = {}
    for pid, rows in visits.items():
        fs = {'repeat/' + str(len(rows) >= 2)}
        for r in rows:
            patient = patients[r['patient_version_id']]
            age = years(patient['birth_date'], datetime.fromisoformat(r['arrival_at'].replace('Z', '+00:00')).astimezone(zone).date().isoformat())
            fs |= {'age/' + ('18-34' if age < 35 else '35-49' if age < 50 else '50-64' if age < 65 else '65-79' if age < 80 else '80+'),
                   'acuity/' + str(r['initial_acuity']), 'service/' + r['encounter_class'], 'site/' + r['facility_id'], 'outcome/' + r['disposition'],
                   'carry/' + str(r['carry_in'])}
            for c in diagnoses[r['encounter_id']]: fs.add('pathway/' + catalog[c['catalog_item_id']]['code'])
            if r['discharged_at']:
                days = (datetime.fromisoformat(r['discharged_at'].replace('Z', '+00:00')) - datetime.fromisoformat(r['arrival_at'].replace('Z', '+00:00'))).total_seconds() / 86400
                fs.add('long-stay/' + str(days > 10))
            for ev in events[r['encounter_id']]:
                if ev['event_type'] == 'MED_ADMIN' and ev['status'] == 'NOT_DONE': fs.add('allergy-withheld')
        features[pid] = fs
    ordered = sorted(visits, key=lambda pid: hashlib.sha256(('clinical-review/' + pid).encode()).hexdigest())
    wanted = set().union(*features.values())
    selected = []
    while wanted:
        best = max((p for p in ordered if p not in selected), key=lambda p: len(features[p] & wanted))
        selected.append(best)
        wanted -= features[best]
    selected.extend(p for p in ordered if p not in selected)
    selected = selected[:cfg['review_journeys']]
    covered = set().union(*(features[p] for p in selected))
    if covered != set().union(*features.values()): raise ValueError('journey sample misses required strata')
    lines = ['# Longitudinal clinical journey review', '', 'Selected synthetic records are deliberate review mirrors. Timings remain provisional until resource integration. This is a synthetic plausibility review, not a clinical endorsement.', '']
    source = hashlib.sha256()
    mirrored = 0
    for number, pid in enumerate(selected, 1):
        mirrored += 1
        rows = sorted(visits[pid], key=lambda r: r['arrival_at'])
        patient = patients[rows[0]['patient_version_id']]
        lines += [f"## Journey {number}: {patient['given_name']} {patient['family_name']}", '', f"Stable patient: {pid}; birth date {patient['birth_date']}; strata: {', '.join(sorted(features[pid]))}.", '']
        for e in rows:
            eid = e['encounter_id']
            facts = sorted(events[eid], key=lambda r: (r['occurred_at'], r['clinical_event_version_id']))
            conditions = diagnoses[eid]
            # Bind every selected journey fact, not just the displayed latest revision or prose excerpt.
            all_rows = [*sorted(revisions[eid], key=lambda r: r['revision_no']), *facts, *conditions]
            for r in all_rows:
                source.update(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode() + b'\n')
            mirrored += 1 + len(conditions)
            codes = ', '.join(catalog[c['catalog_item_id']]['code'] for c in conditions) or 'unassessed'
            counts = Counter(f['event_type'] for f in facts)
            lines += [f"- {e['encounter_class']} {e['arrival_at']} to {e['discharged_at'] or 'CENSORED'}; acuity {e['initial_acuity']}; {e['disposition']}; diagnosis {codes}; episode {e['episode_id']}; predecessor {e['previous_encounter_version_id'] or 'none'}.",
                      '  Captured evidence: ' + ', '.join(f'{k}={v}' for k, v in sorted(counts.items())) + '.']
            meds = [f for f in facts if f['event_type'] in ('MED_ADMIN', 'MED_DISPENSE')]
            if meds:
                mirrored += min(2, len(meds))
                lines.append('  Treatment evidence: ' + '; '.join(f"{catalog[f['catalog_item_id']]['clinical_group']} {f['dose_quantity']} {f['dose_unit']} {f['route']} {f['status']}" for f in [meds[0], *([meds[-1]] if len(meds) > 1 else [])]) + '.')
            for note in (f for f in facts if f['event_type'] == 'DOCUMENT'):
                lines += ['', f"  {note['document_type']} @ {note['occurred_at']}: {note['text_value']}"]
                mirrored += 1
        lines.append('')
    body = '\n'.join(lines) + '\n'
    selection = {'patient_ids': selected, 'journeys': len(selected), 'strata': sorted(covered), 'sample_sha256': hashlib.sha256(body.encode()).hexdigest(),
                 'selected_facts_sha256': source.hexdigest(), 'mirror_rows': mirrored, 'mirror_bytes': len(body.encode())}
    return body, selection


def review_gate(selection, decision):
    passed = (decision is not None and decision.get('status') == 'APPROVED' and decision.get('journeys_reviewed') == selection['journeys'] >= 100
              and decision.get('sample_sha256') == selection['sample_sha256'] and decision.get('selected_facts_sha256') == selection['selected_facts_sha256']
              and decision.get('review_scope') == 'USER_DESIGNATED_SYNTHETIC_DOMAIN_PLAUSIBILITY' and decision.get('licensed_clinical_endorsement') is False
              and not decision.get('unresolved_critical_findings', ['missing disposition']))
    return {'status': 'PASS' if passed else 'PENDING_REVIEW', 'journeys': selection['journeys'], 'sample_sha256': selection['sample_sha256'],
            'licensed_clinical_endorsement': False, 'reviewer': decision.get('reviewer') if passed else None}
