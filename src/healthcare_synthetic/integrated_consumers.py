"""Independent local consumers of persisted scalar facts. No generator imports.

SQLite is a disposable test index, never a new business dataset or a solution
pipeline. Decimal arithmetic stays in Python; SQL is used for joins and grains.
"""
from __future__ import annotations

import calendar
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo
from importlib import resources

ROOT = Path(__file__).resolve().parents[2]
START = '2023-01-01T06:00:00Z'; END = '2026-01-01T06:00:00Z'; GRACE = '2026-01-10T23:59:59Z'
with resources.files('tzdata').joinpath('zoneinfo/America/Chicago').open('rb') as _zone_file:
    ZONE = ZoneInfo.from_file(_zone_file,key='America/Chicago')


def stamp(value):
    return value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def month(value):
    return instant(value).astimezone(ZONE).strftime('%Y-%m')


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def latest(rows, key, known=GRACE, effective=None):
    selected = {}
    for row in rows:
        if row['export_available_at'] > known or row.get('known_from', row['recorded_at']) > known:
            continue
        if effective and row.get('valid_from', START) > effective:
            continue
        identity = row[key]
        if identity not in selected or (row.get('revision_no', 1), row['export_available_at']) > (selected[identity].get('revision_no', 1), selected[identity]['export_available_at']):
            selected[identity] = row
    # valid_to is business validity; known_to is retrospective and never used.
    return {k: r for k, r in selected.items() if not effective or r.get('valid_to') is None or effective < r['valid_to']}


def claim_balances(headers, events, coverage, payers, at=END, known=GRACE):
    accounts = {r['claim_id']: r for r in headers if r['created_at'] <= at and r['export_available_at'] <= known}
    balances = {k: Decimal(h['opening_ar']) for k, h in accounts.items()}; seen = {}; observed = set(); denied = set(); cash = defaultdict(Decimal)
    insured = {k for k, h in accounts.items() if not h['carry_in'] and payers[coverage[h['coverage_version_id']]['payer_plan_id']]['payer_type'] != 'SELF_PAY'}
    for row in events:
        key = row['claim_event_id']
        if key in seen:
            if seen[key] != row:
                raise ValueError('conflicting duplicate claim event')
            continue
        seen[key] = row
        cid = row['claim_id']
        if cid not in accounts or row['occurred_at'] >= at or row['export_available_at'] > known:
            continue
        balances[cid] += Decimal(row['ar_delta']); cash[month(row['occurred_at'])] += Decimal(row['cash_delta'])
        if cid in insured and row['attempt_no'] == 1:
            if row['event_type'] in ('ADJUDICATED', 'DENIED'):
                observed.add(cid)
            if row['event_type'] == 'DENIED':
                denied.add(cid)
    return {'ar_by_original': {k: str(v) for k, v in sorted(balances.items())}, 'cash_by_month': {k: str(v) for k, v in sorted(cash.items())},
            'observed_initial_insured': len(observed), 'denied_initial_insured': len(denied),
            'denial_rate': str(Decimal(len(denied)) / len(observed)) if observed else None}


def selected_allocations(rows, known=GRACE):
    versions = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row['known_from'] <= known and row['export_available_at'] <= known:
            versions[row['posting_id']][row['allocation_run_id']].append(row)
    selected = []
    for runs in versions.values():
        choice = max(runs, key=lambda rid: (runs[rid][0]['known_from'], rid))
        selected.extend(runs[choice])
    return selected


def finance_series(rows, known=GRACE):
    selected = {}
    for row in rows:
        if max(row['published_at'], row['export_available_at']) > known:
            continue
        key = tuple(row[k] for k in ('accounting_month', 'facility_id', 'cost_center_id', 'account_catalog_id', 'measure_code', 'unit_code', 'scenario'))
        if key not in selected or row['published_at'] > selected[key]['published_at']:
            selected[key] = row
    return selected


def variances(rows, known=GRACE):
    series = finance_series(rows, known); result = []
    for key, actual in series.items():
        if actual['scenario'] != 'ACTUAL':
            continue
        for scenario in ('BUDGET', 'FORECAST'):
            plan = series.get((*key[:-1], scenario)); field = 'amount' if actual['amount'] is not None else 'quantity'
            a = Decimal(actual[field]); b = Decimal(plan[field]) if plan else None
            result.append({'grain': list(key[:-1]), 'comparison': scenario, 'actual': str(a), 'plan': str(b) if b is not None else None,
                           'difference': str(a-b) if b is not None else None,
                           'percent': str((a-b)/abs(b)*100) if b else None,
                           'state': 'NO_PLAN' if b is None else 'ZERO_PLAN' if not b else 'COMPARABLE'})
    return result


def feature_snapshot(tables, encounter_id, known, target):
    """Observed inputs and labels, never a model or a prospective prediction."""
    if target < START or target > known or target >= END or known > GRACE:
        raise ValueError('feature snapshot outside observed target/knowledge bounds')
    history = [r for r in tables['encounter'] if r['encounter_id'] == encounter_id]
    visible = latest(history, 'encounter_id', known)
    if not visible:
        return {'encounter_id': encounter_id, 'state': 'UNKNOWN', 'diagnoses': [], 'performed_events': [], 'readmission_label': 'UNKNOWN'}
    encounter = visible[encounter_id]; versions = {r['encounter_version_id'] for r in history}
    diagnoses = [r['condition_id'] for r in latest(tables['clinical_condition'],'condition_id',known).values() if r['encounter_version_id'] in versions
                 and r['known_from'] <= known and r['export_available_at'] <= known and r['onset_at'] <= target]
    performed = [r['clinical_event_id'] for r in latest(tables['clinical_event'],'clinical_event_id',known).values() if r['encounter_version_id'] in versions
                 and r['known_from'] <= known and r['export_available_at'] <= known and r['occurred_at'] <= target
                 and r['status'] == 'COMPLETED' and r['event_type'] != 'ORDER' and (r['period_end_at'] is None or r['period_end_at'] <= target)]
    discharge = encounter['discharged_at'] if encounter['discharged_at'] and encounter['discharged_at'] <= target else None
    # Linkage and cohort eligibility are resolved independently of the latest
    # final encounter row. No evidence of return is not automatically negative.
    label = 'UNKNOWN'
    if discharge and encounter['disposition'] == 'HOME' and encounter['encounter_class'] == 'IPD':
        followup = instant(discharge) + timedelta(days=30)
        index = {r['encounter_version_id']: r for r in tables['encounter']}
        person = {r['patient_version_id']: r['patient_id'] for r in tables['patient']}
        pid = person[encounter['patient_version_id']]
        for other in latest(tables['encounter'], 'encounter_id', known).values():
            if other['encounter_id'] == encounter_id or person[other['patient_version_id']] != pid:
                continue
            if other['encounter_class'] == 'IPD' and not other['planned'] and other['admission_source'] != 'TRANSFER' and discharge < other['arrival_at'] <= min(stamp(followup), target):
                label = 'POSITIVE'; break
        # The healthy encounter source has a validated two-hour delivery lag.
        # Reaching day 30 on the clock alone does not establish complete source
        # observation of arrivals near the followup boundary.
        complete_through = min(target, stamp(instant(known)-timedelta(hours=2)))
        if label != 'POSITIVE' and stamp(followup) < END and stamp(followup) <= complete_through:
            label = 'NEGATIVE'
    return {'encounter_id': encounter_id, 'state': 'KNOWN', 'diagnoses': sorted(set(diagnoses)), 'performed_events': sorted(set(performed)),
            'observed_discharge': discharge, 'readmission_label': label}


def rows(db, table, where='', args=()):
    return [dict(row) for row in db.execute('SELECT * FROM "' + table + '" ' + where, args)]


def wilson_interval(successes, observations):
    """Descriptive 95% binomial interval; repeated people are not independent."""
    if type(successes) is not int or type(observations) is not int or not 0 <= successes <= observations or observations == 0:
        raise ValueError('invalid binomial counts')
    z = 1.959963984540054; p = successes / observations
    denominator = 1 + z*z/observations
    center = (p + z*z/(2*observations))/denominator
    radius = z*math.sqrt(p*(1-p)/observations + z*z/(4*observations*observations))/denominator
    return [max(0.0, center-radius), min(1.0, center+radius)]


def connect(path):
    db = sqlite3.connect(path); db.row_factory = sqlite3.Row
    return db


def build_index(candidate, target, declared_schema):
    candidate = Path(candidate); target = Path(target); manifest = json.loads((candidate / 'manifest.json').read_text(encoding='utf-8'))
    target.parent.mkdir(parents=True, exist_ok=True); temp = target.with_suffix('.building.sqlite3'); temp.unlink(missing_ok=True)
    db = connect(temp); counts = {}; missingness = {}; references = 0
    try:
        for table in declared_schema['tables']:
            name = table['name']; cols = table['columns']; pk = table['primary_key'][0]
            column_sql = ','.join('"' + c['name'] + '" ' + ('INTEGER' if c['type'] in ('INT', 'BIGINT', 'BOOLEAN') else 'TEXT') + (' PRIMARY KEY' if c['name'] == pk else '') for c in cols)
            db.execute('CREATE TABLE "' + name + '" (' + column_sql + ')')
            meta = manifest['canonical_files'][name]; file = (candidate / meta['file']).resolve()
            if candidate.resolve() not in file.parents:
                raise ValueError('index input escaped candidate')
            h = hashlib.sha256(); size = 0; count = 0; nulls = Counter(); batch = []
            insert = 'INSERT INTO "' + name + '" VALUES (' + ','.join('?' for _ in cols) + ')'
            with db, file.open('rb') as stream:
                for line in stream:
                    h.update(line); size += len(line); row = json.loads(line)
                    if set(row) != {c['name'] for c in cols}:
                        raise ValueError('schema columns differ: ' + name)
                    for c in cols:
                        v = row[c['name']]
                        if v is None:
                            nulls[c['name']] += 1
                            if not c['nullable']:
                                raise ValueError('required scalar absent: ' + name + '.' + c['name'])
                        elif c['type'] == 'BOOLEAN' and type(v) is not bool or c['type'] in ('INT', 'BIGINT') and type(v) is not int:
                            raise ValueError('scalar type differs: ' + name + '.' + c['name'])
                    if row['recorded_at'] > row['export_available_at'] or row['export_available_at'] > GRACE:
                        raise ValueError('source availability/grace differs: ' + name)
                    batch.append(tuple(row[c['name']] for c in cols)); count += 1
                    if len(batch) == 1000:
                        db.executemany(insert, batch); batch.clear()
                if batch:
                    db.executemany(insert, batch)
            if (h.hexdigest(), count, size) != (meta['sha256'], meta['rows'], meta['bytes']) or count > table['planned_rows']:
                raise ValueError('index checksum/count/budget differs: ' + name)
            counts[name] = count; missingness[name] = dict(nulls)
            for c in cols:
                if 'references' in c:
                    db.execute('CREATE INDEX "idx_' + name + '_' + c['name'] + '" ON "' + name + '" ("' + c['name'] + '")')
            print('Independent scalar index: ' + name, flush=True)
        for table in declared_schema['tables']:
            for c in table['columns']:
                if 'references' not in c:
                    continue
                ref, key = c['references'].split('.'); name = table['name']; col = c['name']; references += 1
                bad = db.execute(f'SELECT a."{col}" FROM "{name}" a LEFT JOIN "{ref}" b ON a."{col}"=b."{key}" WHERE a."{col}" IS NOT NULL AND b."{key}" IS NULL LIMIT 1').fetchone()
                if bad:
                    raise ValueError('orphan at declared grain: ' + name + '.' + col)
        db.execute('CREATE INDEX encounter_stable_revision ON encounter(encounter_id, revision_no)')
        db.execute('CREATE INDEX shift_stable_revision ON staff_shift(shift_id, revision_no)')
        db.commit()
    finally:
        db.close()
    temp.replace(target)
    return {'status': 'PASS', 'canonical_rows': sum(counts.values()), 'tables': len(counts), 'rows_by_table': counts,
            'physical_foreign_keys_checked': references, 'null_counts_by_column': missingness,
            'index_mirror_rows': sum(counts.values()), 'index_bytes': target.stat().st_size,
            'canonical_business_sha256': manifest['business_sha256']}


def profile(db):
    visits = latest(rows(db, 'encounter'), 'encounter_id')
    visits = {key:r for key,r in visits.items() if r['arrival_at']<END and (r['discharged_at'] is None or r['discharged_at']>START)}
    patients = {r['patient_version_id']: r for r in rows(db, 'patient')}
    coverage = {r['coverage_version_id']: r for r in rows(db, 'patient_coverage')}; payers = {r['payer_plan_id']: r for r in rows(db, 'payer_plan')}
    locations = {r['location_id']: r for r in rows(db, 'location')}
    counts = Counter(); joints = Counter(); first = {}; repeats = Counter(); payer_counts = Counter(); durations = []; missing = Counter(); partitions = set()
    for row in visits.values():
        person = patients[row['patient_version_id']]; pid = person['patient_id']; service_start = max(START,row['arrival_at']); when = instant(service_start).astimezone(ZONE).date(); birth = date.fromisoformat(person['birth_date'])
        age = when.year-birth.year-((when.month, when.day)<(birth.month, birth.day)); band = next((b for a,z,b in ((18,34,'18-34'),(35,49,'35-49'),(50,64,'50-64'),(65,79,'65-79'),(80,100,'80-100'),(101,103,'101-103')) if a<=age<=z), 'INVALID')
        if pid not in first or service_start < first[pid][0]:
            first[pid] = service_start, band
        repeats[pid] += 1; payer = payers[coverage[row['coverage_version_id']]['payer_plan_id']]['payer_type']; payer_counts[payer] += 1
        m = month(service_start); fid = row['facility_id']; cls = row['encounter_class']; service = locations[row['location_id']]['service_line']
        scenario = 'RESPIRATORY_SURGE' if '2024-01-08' <= str(when) < '2024-02-26' else 'RN_ABSENCE' if str(when).startswith('2025-02') else 'NORMAL'
        key = (m, fid, service, cls, payer, band, row['initial_acuity'], scenario); joints[key] += 1; partitions.add((m, fid, cls)); counts[cls] += 1
        if row['discharged_at'] is None:
            missing[cls + '_OPEN'] += 1
        elif cls == 'IPD':
            durations.append((instant(row['discharged_at'])-instant(row['arrival_at'])).total_seconds()/86400)
    parent_counts = Counter()
    for key, n in joints.items():
        parent_counts[key[0], key[1], key[3]] += n
    age_counts = Counter(b for _, b in first.values()); months = sorted({m for m, _, _ in partitions}); facilities = sorted({f for _, f, _ in partitions})
    expected = {(m, f, c) for m in (f'{y}-{n:02d}' for y in (2023,2024,2025) for n in range(1,13)) for f in facilities for c in ('IPD','ED','OPD')}
    if len(facilities) != 3 or len(months) != 36 or partitions != expected:
        raise ValueError('month/facility/service partition absent without lifecycle explanation')
    frozen = json.loads((ROOT / 'contracts/phase0/realism-targets.json').read_text()); targets = {r['id']: r for r in frozen['targets']}; checks = []
    def band_check(key, value):
        t = targets[key]; checks.append({'id': key, 'value': value, 'lower': t['lower'], 'upper': t['upper'], 'passed': t['lower'] <= value <= t['upper']})
    checks.append({'id':'AGE/ADULT_AND_NATURAL_AGING','invalid_people':age_counts['INVALID'],'passed':age_counts['INVALID']==0,
                   'scope':'100 at the opening baseline may age to 103; 101-103 is disclosed separately, never capped or recoded'})
    for band, target in targets['AGE']['target'].items():
        share = age_counts[band]/len(first); checks.append({'id': 'AGE/'+band, 'value': share, 'target': target, 'absolute_tolerance': .04, 'passed': abs(share-target)<=.04})
    for payer, target in targets['PAYER']['target'].items():
        share = payer_counts[payer]/sum(payer_counts.values()); checks.append({'id': 'PAYER/'+payer, 'value': share, 'target': target, 'absolute_tolerance': .05, 'passed': abs(share-target)<=.05})
    band_check('LOS', sum(durations)/len(durations)); band_check('TAIL', sum(d>10 for d in durations)/len(durations)); band_check('REPEAT', sum(n>=2 for n in repeats.values())/len(repeats))
    claims = claim_balances(rows(db, 'claim'), rows(db, 'claim_event'), coverage, payers); band_check('DENIAL', float(claims['denial_rate']))
    ed = Counter()
    for (m, fid, service, cls, payer, age, acuity, scenario), n in joints.items():
        if cls == 'ED':
            ed[m] += n
    rates = [n/calendar.monthrange(int(m[:4]), int(m[5:]))[1] for m,n in ed.items()]; band_check('SEASON', max(rates)/min(rates))
    notes = defaultdict(Counter); note_missing = Counter(); names = {(r['given_name']+' '+r['family_name']) for r in patients.values()}
    for row in db.execute("SELECT document_type,text_value FROM clinical_event WHERE event_type='DOCUMENT'"):
        text = row['text_value']
        if not text:
            note_missing[row['document_type']] += 1; continue
        normalized = re.sub(r'clinical_event_[a-f0-9]+', 'FACT', text)
        normalized = re.sub(r'(Clinical review|Interval assessment|Care assessment|Patient review|Encounter review|Assessment update): .*?, age \d+\.', r'\1: PERSON, age AGE.', normalized)
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', 'TIME', normalized)
        notes[row['document_type']][normalized.lower()] += 1
    duplicate = {k: sum(n-1 for n in c.values())/sum(c.values()) for k,c in notes.items()}
    for kind, share in duplicate.items():
        checks.append({'id': 'NOTES/'+kind, 'value': share, 'upper': .15, 'passed': share<=.15})
    workers = latest(rows(db, 'worker_assignment'), 'worker_id'); worker_dates = Counter(r['birth_date'][5:] for r in workers.values())
    checks.append({'id':'WORKER/BIRTHDAYS_NOT_FIXED','distinct_month_days':len(worker_dates),
                   'passed':len({r['birth_date'][5:7] for r in workers.values()})>1 and len({r['birth_date'][8:] for r in workers.values()})>1,
                   'scope':'Logical nonstatic-data control; not a claim about a US birthday distribution'})
    return {'status': 'PASS' if all(c['passed'] for c in checks) else 'FAIL', 'checks': checks, 'partitions': len(partitions),
            'active_people': len(first), 'encounter_classes': dict(counts), 'age_counts': dict(age_counts), 'payer_encounters': dict(payer_counts),
            'open_encounters': dict(missing), 'los_quantiles': {str(p): sorted(durations)[int((len(durations)-1)*p)] for p in (.5,.9,.95,.99)},
            'normalized_note_duplicate_shares': duplicate, 'worker_birth_month_day_counts': dict(worker_dates),
            'joint_interval_scope': 'Descriptive binomial intervals within month/facility/encounter class; correlated repeat visits and a configured fictional catchment prohibit population-inference claims. No arbitrary small-cell percentage pass/fail threshold.',
            'joint_profiles': [{'month': k[0], 'facility': k[1], 'service': k[2], 'class': k[3], 'payer': k[4], 'age_band': k[5], 'acuity': k[6], 'scenario': k[7], 'n': n,
                                'parent_month_facility_class_n': parent_counts[k[0],k[1],k[3]],
                                'wilson_95': wilson_interval(n,parent_counts[k[0],k[1],k[3]]),
                                'small_cell': n<200, 'review_policy': 'COUNTS_INTERVAL_AND_DOMAIN_CONSTRAINTS_NO_PERCENTAGE_CUTOFF' if n<200 else 'CONFIGURED_COHORT_REVIEW'} for k,n in sorted(joints.items())],
            'original_claims': {'observed_initial_insured': claims['observed_initial_insured'], 'denied_initial_insured': claims['denied_initial_insured'], 'denial_rate': claims['denial_rate']}}
