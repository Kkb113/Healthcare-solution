"""Coordinate resource-constrained services before labor and stock are materialized."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import re

from .core import chicago, draw, instant, stable_id
from .master_generation import MasterGenerator

START = datetime(2023, 1, 1, 6, tzinfo=timezone.utc)
CUTOFF = datetime(2026, 1, 1, 6, tzinfo=timezone.utc)
OPERATIVE_CODES = {'0FT44ZZ': 'General Surgery', '0SRC0J9': 'Orthopedics'}
ZONE = chicago()  # Validate the pinned package once, not on every calendar lookup.


def stamp(at):
    return at.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def decimal_text(value):
    return format(Decimal(value).quantize(Decimal('0.000001')), 'f')


def local_at(day, hour=0):
    return datetime.combine(day, datetime.min.time()).replace(hour=hour, tzinfo=ZONE).astimezone(timezone.utc)


def row_builder(cfg, run_id):
    return MasterGenerator({'seed': cfg['seed']}, {}, run_id)


def coordinate_services(parent, cfg, run_id):
    """A finite agenda changes actual performance, never the already published intent.

    Shortage dates are deterministic scenarios, not future predictors. Readiness is
    observed at execution; the persisted coordination document is unavailable earlier.
    """
    catalog = {r['catalog_item_id']: r for r in parent['catalog_item']}
    encounters = {r['encounter_version_id']: r for r in parent['encounter']}
    histories = defaultdict(list)
    for e in parent['encounter']:
        histories[e['encounter_id']].append(e)
    operations = sorted((r for r in parent['clinical_event'] if r['event_type'] == 'PROCEDURE' and stamp(START) <= r['occurred_at']
                         and catalog[r['catalog_item_id']]['code'] in OPERATIVE_CODES),
                        key=lambda r: (r['occurred_at'], r['clinical_event_id']))
    assessments=defaultdict(list)
    for r in parent['clinical_event']:
        if r['event_type'] in ('OBSERVATION','LAB_RESULT') and r['numeric_value'] is not None:
            assessments[encounters[r['encounter_version_id']]['encounter_id']].append(r)
    first = {}
    for p in operations:
        fid = encounters[p['encounter_version_id']]['facility_id']
        day = instant(p['occurred_at']).astimezone(ZONE).date().isoformat()
        first.setdefault((fid, day), p['clinical_event_id'])
    eligible = sorted((day, fid, eid) for (fid, day), eid in first.items())
    stock = {eid for day, fid, eid in eligible if '2024-09-01' <= day < '2024-12-01'}
    stock = set(sorted(stock)[:cfg['stockout_cases']])
    absent = set(sorted(eid for day, fid, eid in eligible if day.startswith('2025-02'))[:cfg['operative_absence_cases']])
    if len(stock) != cfg['stockout_cases'] or len(absent) != cfg['operative_absence_cases']:
        raise ValueError('insufficient independently dated shortage scenarios')
    windows = {}
    for p in operations:
        if p['clinical_event_id'] in stock | absent:
            fid=encounters[p['encounter_version_id']]['facility_id']
            day=instant(p['occurred_at']).astimezone(ZONE).date().isoformat()
            windows[fid,day]=(instant(p['occurred_at']), 'UNIT_STOCKOUT' if p['clinical_event_id'] in stock else 'CIRCULATING_RN_ABSENCE')
    rooms = defaultdict(lambda: [START] * cfg['operative_concurrency'])
    replacements, notes, plans = {}, [], {}
    builder = row_builder(cfg, run_id)
    for p in operations:
        e = encounters[p['encounter_version_id']]
        fid = e['facility_id']; original = instant(p['occurred_at'])
        day=original.astimezone(ZONE).date().isoformat()
        window=windows.get((fid,day))
        cause = window[1] if window and original < window[0]+timedelta(minutes=cfg['shortage_delay_minutes']) else None
        ready = window[0] + timedelta(minutes=10) if cause else original
        slot = min(range(len(rooms[fid])), key=lambda i: (rooms[fid][i], i))
        actual = max(max(original,window[0] + timedelta(minutes=cfg['shortage_delay_minutes'])) if cause else original, rooms[fid][slot])
        if actual > original and cause is None:
            cause = 'OPERATIVE_CAPACITY_QUEUE'
        end = actual + (instant(p['period_end_at']) - original)
        latest = max(histories[e['encounter_id']], key=lambda x: x['revision_no'])
        if end >= min(instant(latest['discharged_at']) if latest['discharged_at'] else CUTOFF, CUTOFF):
            raise ValueError('resource delay crosses observed care boundary; full flow regeneration required')
        rooms[fid][slot] = end
        plans[p['clinical_event_id']] = {'facility_id': fid, 'slot': slot, 'planned': stamp(original),
            'start': stamp(actual), 'end': stamp(end), 'ready': stamp(ready), 'cause': cause,
            'specialty': OPERATIVE_CODES[catalog[p['catalog_item_id']]['code']]}
        if actual == original:
            continue
        context = max((x for x in histories[e['encounter_id']] if x['known_from'] <= stamp(actual)), key=lambda x: x['revision_no'])
        replacements[p['clinical_event_version_id']] = {**p, 'occurred_at': stamp(actual), 'period_end_at': stamp(end),
            'encounter_version_id': context['encounter_version_id'], 'recorded_at': stamp(end), 'known_from': stamp(end),
            'export_available_at': stamp(end + timedelta(hours=2)), 'generation_run_id': run_id}
        key = p['clinical_event_id'] + '/resource-response'
        text = (f"Resource coordination for procedure {p['clinical_event_id']}: planned {stamp(original)}; "
                f"resource ready {stamp(ready)}; observed start {stamp(actual)}. Cause: {cause}. "
                'Care remains within the observed encounter; later outcome is not asserted.')
        available=sorted((r for r in assessments[e['encounter_id']] if r['known_from']<=stamp(actual) and r['occurred_at']<=stamp(actual)),
            key=lambda r:(r['catalog_item_id'],r['occurred_at'],r['clinical_event_id']))
        preferred=sorted(available,key=lambda r:(catalog[r['catalog_item_id']]['code'] not in ('LAB-006','LAB-012'),catalog[r['catalog_item_id']]['code'],r['occurred_at']))[:2]
        for observation in preferred:
            text+=(f" Recorded assessment {catalog[observation['catalog_item_id']]['code']}={observation['numeric_value']} {observation['value_unit']} "
                f"(record {observation['clinical_event_id']}, observed {observation['occurred_at']}).")
        notes.append(builder.row('clinical_event', key, stamp(actual), clinical_event_version_id=stable_id('clinical_event_version', key, 1),
            clinical_event_id=stable_id('clinical_event', key), encounter_version_id=context['encounter_version_id'],
            author_assignment_id=p['author_assignment_id'], event_type='DOCUMENT', occurred_at=stamp(actual),
            document_signed_at=stamp(actual), status='COMPLETED', text_value=text, document_type='PROGRESS_NOTE',
            aggregation='NOT_APPLICABLE', revision_no=1, known_from=stamp(actual)))
    events = [replacements.get(r['clinical_event_version_id'], r) for r in parent['clinical_event']] + notes
    # Every changed service is still completed before its original operative note;
    # no note can silently cite a now-future procedure.
    by_encounter = {encounters[p['encounter_version_id']]['encounter_id']: p for p in operations}
    for r in events:
        if r['event_type'] == 'DOCUMENT' and r['document_type'] == 'OPERATIVE_NOTE':
            e = encounters[r['encounter_version_id']]
            p = by_encounter.get(e['encounter_id'])
            if p and plans[p['clinical_event_id']]['end'] > r['known_from']:
                raise ValueError('delayed procedure requires dependent note regeneration')
    return {'tables': {'clinical_event': events}, 'controls': {
        'operative_cases': len(operations), 'stockout_delays': len(stock), 'absence_delays': len(absent),
        'changed_procedures': len(replacements), 'coordination_documents': len(notes),
        'care_and_bed_timing_unchanged': True}}


def operative_plans(tables):
    """Transient schedule derived from counted scalar services and source documents."""
    notes = {}
    pattern = r'Resource coordination for procedure (\S+): planned (\S+); resource ready (\S+); observed start (\S+)\. Cause: ([A-Z_]+)\.'
    for r in tables['clinical_event']:
        if r['source_record_id'].endswith('/resource-response'):
            m = re.match(pattern, r['text_value'])
            if not m:
                raise ValueError('invalid resource coordination document')
            notes[m[1]] = {'planned': m[2], 'ready': m[3], 'cause': m[5]}
    catalog = {r['catalog_item_id']: r for r in tables['catalog_item']}
    enc = {r['encounter_version_id']: r for r in tables['encounter']}
    return {r['clinical_event_id']: {'facility_id': enc[r['encounter_version_id']]['facility_id'],
            'start': r['occurred_at'], 'end': r['period_end_at'],
            'specialty': OPERATIVE_CODES[catalog[r['catalog_item_id']]['code']],
            **notes.get(r['clinical_event_id'], {'planned': r['occurred_at'], 'ready': r['occurred_at'], 'cause': None})}
        for r in tables['clinical_event'] if r['event_type'] == 'PROCEDURE' and stamp(START) <= r['occurred_at']
        and catalog[r['catalog_item_id']]['code'] in OPERATIVE_CODES}
