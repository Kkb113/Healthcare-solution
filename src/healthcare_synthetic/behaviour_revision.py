"""Independent full-population checks for the version 1.1 behaviour revision.

Each check measures one revised behaviour directly from published canonical rows
and states a falsifiable band. The checks confirm the old fixed rules are gone
(no constant durations, no deterministic no-show rule) and that the new
behaviour carries graded, overlapping signal. This module does not import the
generators.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from io import BytesIO
from importlib import resources
from pathlib import Path
from zoneinfo import ZoneInfo

ZONE = ZoneInfo.from_file(BytesIO(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()))
# Tables whose rows must be unchanged by the revision (generation_run_id excluded).
UNCHANGED = ('facility', 'cost_center', 'location', 'patient', 'worker_assignment', 'access_scope', 'payer_plan',
             'patient_coverage', 'source_key_map', 'catalog_item', 'facility_day_driver')


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def local(value):
    return instant(value).astimezone(ZONE)


def hours(a, b):
    return (instant(b) - instant(a)).total_seconds() / 3600


def quantile(values, q):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def rate(flags):
    return sum(flags) / len(flags) if flags else None


def rows(directory, table):
    with (Path(directory) / 'canonical' / (table.replace('_', '-') + '.jsonl')).open('rb') as stream:
        for line in stream:
            yield json.loads(line)


def latest(records, key):
    result = {}
    for r in records:
        if r[key] not in result or r['revision_no'] > result[r[key]]['revision_no']:
            result[r[key]] = r
    return result


class Checks:
    def __init__(self):
        self.items = []

    def band(self, check_id, value, lower, upper, description):
        self.items.append({'id': check_id, 'description': description, 'value': value, 'lower': lower, 'upper': upper,
                           'passed': value is not None and lower <= value <= upper})

    def require(self, check_id, passed, description, evidence):
        self.items.append({'id': check_id, 'description': description, 'evidence': evidence, 'passed': bool(passed)})


def flow(directory, checks):
    encounters = latest(rows(directory, 'encounter'), 'encounter_id')
    ed = defaultdict(list)
    for e in encounters.values():
        if e['encounter_class'] == 'ED' and e['discharged_at']:
            ed[e['disposition']].append(hours(e['arrival_at'], e['discharged_at']))
    home, admitted = ed['HOME'], ed['TRANSFER']
    checks.band('ED_HOME_MEDIAN_HOURS', quantile(home, .5), 2.0, 4.0, 'Treat-and-release ED stay median')
    checks.band('ED_HOME_OVER_FOUR_HOURS', rate([h > 4 for h in home]), .05, .35, 'Treat-and-release ED stays are not capped at four hours')
    checks.band('ED_ADMITTED_MEDIAN_HOURS', quantile(admitted, .5), 4.0, 7.5, 'Admitted ED stay median, including decision and handover')
    checks.band('ED_ADMITTED_P90_HOURS', quantile(admitted, .9), 6.0, 16.0, 'Admitted ED stay has a long tail')
    checks.band('ED_LWBS_MEDIAN_HOURS', quantile(ed['LEFT_WITHOUT_SEEN'], .5), 0.2, 2.0, 'Left-without-being-seen leaves early in the wait')
    checks.require('ED_DURATIONS_NOT_CONSTANT', len({round(h, 3) for h in admitted}) > 200 and len({round(h, 3) for h in home}) > 200,
                   'ED stay durations are varied, not fixed', {'distinct_admitted': len({round(h, 3) for h in admitted}), 'distinct_home': len({round(h, 3) for h in home})})
    discharges = [e for e in encounters.values() if e['encounter_class'] == 'IPD' and e['disposition'] == 'HOME' and e['discharged_at']]
    gaps = [hours(e['medically_ready_at'], e['discharged_at']) for e in discharges]
    checks.band('READY_TO_DISCHARGE_MEDIAN_HOURS', quantile(gaps, .5), 2.0, 6.0, 'Medically ready to home discharge median')
    checks.band('READY_TO_DISCHARGE_EXACTLY_ONE_HOUR', rate([abs(g - 1) < 1e-9 for g in gaps]), 0, .05, 'The fixed one-hour discharge delay is gone')
    checks.band('READY_TO_DISCHARGE_P90_HOURS', quantile(gaps, .9), 5.0, 30.0, 'Discharge delays have a tail, including overnight holds')
    hour = Counter(local(e['discharged_at']).hour for e in discharges)
    checks.band('DISCHARGE_10_TO_17_SHARE', sum(hour[h] for h in range(10, 17)) / len(discharges), .60, .95, 'Home discharges concentrate late morning to afternoon')
    checks.band('DISCHARGE_OVERNIGHT_SHARE', sum(hour[h] for h in range(0, 7)) / len(discharges), 0, .03, 'Few home discharges overnight')
    weekday = Counter(local(e['discharged_at']).weekday() for e in discharges)
    checks.band('DISCHARGE_WEEKEND_TO_WEEKDAY_RATIO', (weekday[5] + weekday[6]) / 2 / (sum(weekday[d] for d in range(5)) / 5), .6, .95, 'Weekend discharges are lower than weekday')
    opd = Counter(local(e['arrival_at']).weekday() for e in encounters.values() if e['encounter_class'] == 'OPD' and e['arrival_at'] >= '2023-01-01T06:00:00Z')
    checks.band('OPD_MONDAY_RATIO', opd[0] / (sum(opd[d] for d in range(1, 5)) / 4), .8, 1.4, 'Outpatient Monday volume relative to Tuesday-Friday')
    elective = Counter(local(e['admitted_at']).weekday() for e in encounters.values() if e['encounter_class'] == 'IPD' and e['planned'] and e['admitted_at'])
    checks.band('ELECTIVE_MONDAY_RATIO', elective[0] / (sum(elective[d] for d in range(1, 5)) / 4), .8, 1.5, 'Elective admission Monday volume relative to Tuesday-Friday')
    los = [hours(e['admitted_at'], e['discharged_at']) / 24 for e in encounters.values() if e['encounter_class'] == 'IPD' and e['admitted_at'] and e['discharged_at']]
    checks.band('IPD_MEAN_LOS_DAYS', sum(los) / len(los), 4.4, 6.2, 'Frozen realism band for mean inpatient stay is still met')
    return encounters


def beds(directory, encounters, checks):
    versions = {}
    for e in rows(directory, 'encounter'):
        versions[e['encounter_version_id']] = e['encounter_id']
    first, turn, events = {}, [], defaultdict(list)
    for r in rows(directory, 'bed_event'):
        if r['event_type'] == 'OCCUPY' and 'FIRST_PLACEMENT' in r['reason'] and r['encounter_version_id']:
            eid = versions[r['encounter_version_id']]
            first[eid] = min(first.get(eid, r['effective_at']), r['effective_at'])
        if r['event_type'] in ('VACATE', 'CLEAN_START', 'READY'):
            events[r['bed_location_id']].append((r['effective_at'], r['event_type']))
    waits = defaultdict(list)
    for eid, at in first.items():
        e = encounters[eid]
        if e['admitted_at']:
            waits[e['planned']].append(hours(e['admitted_at'], at) * 60)
    every = waits[True] + waits[False]
    checks.band('PLACEMENT_EXACTLY_TEN_MINUTES', rate([abs(m - 10) < 1e-6 for m in every]), 0, .05, 'The fixed ten-minute placement is gone')
    checks.band('UNPLANNED_PLACEMENT_MEDIAN_MINUTES', quantile(waits[False], .5), 30, 180, 'Unplanned admission to bed placement median')
    checks.band('UNPLANNED_PLACEMENT_P90_HOURS', quantile(waits[False], .9) / 60, 2, 24, 'Capacity waits create a boarding tail')
    for bed in events.values():
        bed.sort()
        for (a, kind), (b, nxt) in zip(bed, bed[1:]):
            if kind == 'VACATE' and nxt == 'CLEAN_START':
                turn.append(hours(a, b) * 60)
    checks.band('CLEAN_START_MEDIAN_MINUTES', quantile(turn, .5), 15, 60, 'Vacate to cleaning start median')
    checks.require('CLEAN_START_NOT_CONSTANT', len({round(m) for m in turn}) >= 20, 'Cleaning response varies', {'distinct_minutes': len({round(m) for m in turn})})


def appointments(directory, checks):
    patients = {r['patient_version_id']: r for r in rows(directory, 'patient')}
    payer = {r['payer_plan_id']: r['payer_type'] for r in rows(directory, 'payer_plan')}
    coverage = defaultdict(list)
    for r in rows(directory, 'patient_coverage'):
        coverage[patients[r['patient_version_id']]['patient_id']].append(r)
    office, history = [], defaultdict(list)
    for r in rows(directory, 'appointment'):
        if r['appointment_type'] == 'ELECTIVE_ADMISSION' or not (r['arrived_at'] or r['no_show_recorded_at']):
            continue
        p = patients[r['patient_version_id']]
        when = r['booked_at']
        cover = [c for c in coverage[p['patient_id']] if c['valid_from'] <= when and (c['valid_to'] is None or when < c['valid_to'])
                 and c['known_from'] <= when and (c['known_to'] is None or when < c['known_to'])]
        item = dict(missed=bool(r['no_show_recorded_at']), type=r['appointment_type'], lead=hours(r['booked_at'], r['scheduled_start']) / 24,
                    weekday=local(r['scheduled_start']).weekday(), hour=local(r['scheduled_start']).hour,
                    age=int(r['scheduled_start'][:4]) - int(p['birth_date'][:4]), payer=payer[cover[0]['payer_plan_id']] if len(cover) == 1 else None,
                    person=p['patient_id'], at=r['scheduled_start'])
        office.append(item); history[item['person']].append(item)
    for visits in history.values():
        visits.sort(key=lambda x: x['at']); missed = 0
        for v in visits:
            v['prior_missed'] = missed; missed += v['missed']
    overall = rate([v['missed'] for v in office])
    checks.band('NO_SHOW_RATE', overall, .08, .25, 'Office visit no-show rate')
    deterministic = []
    for feature in ('type', 'weekday', 'hour'):
        groups = defaultdict(list)
        for v in office:
            groups[v[feature]].append(v['missed'])
        deterministic += [(feature, k, rate(g)) for k, g in groups.items() if len(g) >= 200 and not .02 < rate(g) < .60]
    leads = defaultdict(list)
    for v in office:
        leads[min(int(v['lead'] // 7), 6)].append(v['missed'])
    deterministic += [('lead_week', k, rate(g)) for k, g in leads.items() if len(g) >= 200 and not .02 < rate(g) < .60]
    checks.require('NO_SHOW_NOT_RULE_BASED', not deterministic, 'No single feature value makes a no-show (near) certain or impossible', {'violations': deterministic})
    young, old = rate([v['missed'] for v in office if v['age'] < 35]), rate([v['missed'] for v in office if v['age'] >= 65])
    checks.require('NO_SHOW_AGE_GRADIENT', young > old * 1.3, 'Younger adults miss more often', {'under_35': young, '65_plus': old})
    vulnerable = rate([v['missed'] for v in office if v['payer'] in ('MEDICAID', 'SELF_PAY')])
    medicare = rate([v['missed'] for v in office if v['payer'] == 'MEDICARE'])
    checks.require('NO_SHOW_PAYER_GRADIENT', vulnerable > medicare * 1.3, 'Medicaid and self-pay miss more often than Medicare', {'medicaid_self_pay': vulnerable, 'medicare': medicare})
    short, long_ = rate([v['missed'] for v in office if v['lead'] < 7]), rate([v['missed'] for v in office if v['lead'] >= 21])
    checks.require('NO_SHOW_LEAD_GRADIENT', long_ > short * 1.3, 'Long booking leads miss more often', {'under_7_days': short, '21_days_plus': long_})
    first, repeat = rate([v['missed'] for v in office if v['prior_missed'] == 0]), rate([v['missed'] for v in office if v['prior_missed'] > 0])
    checks.require('NO_SHOW_HISTORY_GRADIENT', repeat > first, 'A prior miss raises the chance of another', {'no_prior_miss': first, 'prior_miss': repeat})


def workforce(directory, checks):
    shifts = latest(rows(directory, 'staff_shift'), 'shift_id')
    routine = [r for r in shifts.values() if r['source_record_id'].startswith('RN/') and r['attendance_status'] in ('WORKED', 'ABSENT')]
    absent = [r['attendance_status'] == 'ABSENT' for r in routine]
    winter = [r['attendance_status'] == 'ABSENT' for r in routine if local(r['planned_start']).month in (12, 1, 2)]
    other = [r['attendance_status'] == 'ABSENT' for r in routine if local(r['planned_start']).month not in (12, 1, 2)]
    checks.band('RN_ABSENCE_RATE', rate(absent), .015, .05, 'Unplanned RN absence rate on routine unit shifts')
    checks.require('RN_ABSENCE_WINTER_SEASONALITY', rate(winter) > rate(other) * 1.3, 'RN absences rise in winter', {'winter': rate(winter), 'other': rate(other)})
    workers = {r['worker_assignment_id']: r for r in rows(directory, 'worker_assignment')}
    replacements = Counter(workers[r['worker_assignment_id']]['worker_type'] for r in shifts.values() if r['source_record_id'].startswith('replace/'))
    checks.require('ABSENCE_COVER_MIX', replacements['AGENCY'] >= 60 and replacements['EMPLOYEE'] > replacements['AGENCY'],
                   'Absences are covered by both colleague pickups and agency staff', dict(replacements))


def denials(directory, encounters, checks):
    versions = {r['encounter_version_id']: r['encounter_id'] for r in rows(directory, 'encounter')}
    payer = {r['payer_plan_id']: r['payer_type'] for r in rows(directory, 'payer_plan')}
    coverage = {r['coverage_version_id']: payer[r['payer_plan_id']] for r in rows(directory, 'patient_coverage')}
    codes = {r['catalog_item_id']: r['code'] for r in rows(directory, 'catalog_item')}
    adjudicated, denied, reasons = set(), {}, Counter()
    for r in rows(directory, 'claim_event'):
        if r['attempt_no'] == 1 and r['event_type'] in ('ADJUDICATED', 'DENIED'):
            adjudicated.add(r['claim_id'])
        if r['attempt_no'] == 1 and r['event_type'] == 'DENIED':
            denied[r['claim_id']] = codes[r['denial_catalog_id']]
    groups = defaultdict(list)
    for claim in rows(directory, 'claim'):
        kind = coverage[claim['coverage_version_id']]
        if claim['claim_id'] not in adjudicated or kind == 'SELF_PAY':
            continue
        e = encounters[versions[claim['encounter_version_id']]]
        flag = claim['claim_id'] in denied
        groups['all'].append(flag); groups[kind].append(flag); groups[e['encounter_class']].append(flag)
        if flag:
            reasons[denied[claim['claim_id']]] += 1
    checks.band('DENIAL_RATE', rate(groups['all']), .08, .12, 'Frozen initial insured denial band is still met')
    by_payer = {k: rate(groups[k]) for k in ('COMMERCIAL', 'MEDICAID', 'MEDICARE')}
    checks.require('DENIAL_PAYER_SPREAD', max(by_payer.values()) > 1.3 * min(by_payer.values()), 'Denial rate differs by payer', by_payer)
    by_class = {k: rate(groups[k]) for k in ('ED', 'IPD', 'OPD')}
    checks.require('DENIAL_SETTING_SPREAD', by_class['IPD'] > 1.3 * by_class['OPD'], 'Inpatient claims are denied more often than outpatient', by_class)
    other = {k: v for k, v in reasons.items() if k not in ('DEN-01', 'DEN-02')}
    checks.require('DENIAL_REASON_MIX', len(other) >= 4 and max(other.values()) / sum(other.values()) < .6, 'Non-authorization denials span several reasons', dict(reasons))


def unchanged(directory, reference, checks):
    differences = []
    for table in UNCHANGED:
        def content(root):
            return sorted(json.dumps({k: v for k, v in r.items() if k != 'generation_run_id'}, sort_keys=True) for r in rows(root, table))
        if content(directory) != content(reference):
            differences.append(table)
    checks.require('UNCHANGED_DOMAINS_IDENTICAL', not differences, 'Master, reference and driver tables are identical to the reference release', {'differences': differences, 'tables': list(UNCHANGED)})


def budget(directory, schema, checks):
    counts = {t['name']: sum(1 for _ in rows(directory, t['name'])) for t in schema['tables']}
    over = {t['name']: [counts[t['name']], t['planned_rows']] for t in schema['tables'] if counts[t['name']] > t['planned_rows']}
    checks.require('TABLE_BUDGETS', not over, 'Every table stays within its planned row budget', {'over_budget': over, 'rows': counts, 'total': sum(counts.values())})


def evaluate(directory, reference, schema):
    checks = Checks()
    encounters = flow(directory, checks)
    beds(directory, encounters, checks)
    appointments(directory, checks)
    workforce(directory, checks)
    denials(directory, encounters, checks)
    if reference:
        unchanged(directory, reference, checks)
    budget(directory, schema, checks)
    return {'status': 'PASS' if all(c['passed'] for c in checks.items) else 'FAIL', 'checks': checks.items,
            'failed': [c['id'] for c in checks.items if not c['passed']]}
