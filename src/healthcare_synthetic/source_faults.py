"""Published bounded delivery challenges and executable disposition evidence."""
from __future__ import annotations

import copy
import csv
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from decimal import Decimal

from .core import digest
from .engine import atomic_json
from .source_export import export_file, footprint
from .source_layouts import contracts, read_rows
from .source_reader import DeliveryReplay, read_file


def refresh(manifest):
    manifest['file_id'] = digest({k: v for k, v in manifest.items() if k != 'file_id'})
    return manifest


def fixture(root, case, layout, rows, **kwargs):
    folder = Path(root) / 'challenges' / case
    m = export_file(folder, layout, rows, 'records', role='CHALLENGE_CONTROL', **kwargs)
    for field in ('path', 'dictionary_path'):
        m[field] = (folder / m[field]).relative_to(root).as_posix()
    return refresh(m)


def change_csv(root, m, column, value):
    path = Path(root) / m['path']
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream); columns = reader.fieldnames; rows = list(reader)
    rows[0][column] = value
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\r\n'); writer.writeheader(); writer.writerows(rows)
    m.update(footprint(path)); return refresh(m)


def build_faults(root, parent, accepted):
    root = Path(root); layouts = contracts()
    def load(table):
        return read_rows(parent / accepted['canonical_files'][table]['file'])
    finance = load('finance_monthly'); workers = load('worker_assignment'); access = load('access_scope'); beds = load('bed_event')
    key = lambda r: tuple(r[k] for k in ('accounting_month', 'cost_center_id', 'account_catalog_id', 'measure_code', 'unit_code'))
    initial = {key(r): r for r in finance if r['scenario'] == 'ACTUAL' and r['amount'] is not None and r['accounting_month'] == '2025-12-01' and not r['supersedes_vintage_id']}
    # The accepted final close legitimately confirms unchanged actual values.
    # Select a nonzero value so accidental addition would still double money;
    # never invent a changed business fact merely to exercise replacement.
    revised = next(r for r in finance if r['scenario'] == 'ACTUAL' and r['supersedes_vintage_id'] and r['amount'] is not None and Decimal(initial[key(r)]['amount']) != 0)
    original = initial[key(revised)]
    valid = fixture(root, 'valid-financial-control', layouts['finance_monthly'], [original], mode='REPLACE_DECLARED_SCOPE_VERSION')
    replacement = fixture(root, 'valid-financial-replacement', layouts['finance_monthly'], [revised],
                          mode='REPLACE_DECLARED_SCOPE_VERSION', scope=valid['scope'], replacement_of=valid['file_id'])
    cases = []; files = [valid, replacement]
    def bad(case, detector, mutate):
        m = fixture(root, case.lower().replace('_', '-'), layouts['finance_monthly'], [original])
        mutate(m); refresh(m); files.append(m)
        cases.append({'fault_id': case, 'manifest': m, 'expected_detector': detector, 'expected_action': 'QUARANTINE_FILE_ATOMICALLY_THEN_REDELIVER_VALID_CONTROL',
                      'injection_stage': 'observed-delivery', 'affected_records': [original['finance_record_id']],
                      'expected_final_canonical_state': 'EXACT_VALID_CONTROL_NO_EXTRA_VERSION'})
    bad('F_SCHEMA', 'F_SCHEMA', lambda m: m.update(schema_version='unapproved-source-2'))
    bad('F_UNMAPPED', 'F_UNMAPPED', lambda m: change_csv(root, m, 'CostCenterReference', 'UNKNOWN-CENTER'))
    bad('F_REQUIRED_KEY', 'F_UNMAPPED', lambda m: change_csv(root, m, 'FinanceRecordReference', '\\N'))
    bad('F_DECIMAL', 'F_CORRUPT', lambda m: change_csv(root, m, 'Amount', 'NaN'))
    bad('F_CONTROL', 'F_CORRUPT', lambda m: m['control_totals'].update(amount='999999.99'))
    bad('F_ROW_COUNT', 'F_MISSING', lambda m: m.update(expected_rows=2))
    def corrupt(m):
        with (root / m['path']).open('ab') as stream:
            stream.write(b'BROKEN')
    bad('F_CORRUPT', 'F_CORRUPT', corrupt)
    conflicting = copy.deepcopy(original); conflicting['amount'] = '9.99' if original['amount'] != '9.99' else '8.99'
    conflict = fixture(root, 'conflicting-immutable-version', layouts['finance_monthly'], [conflicting]); files.append(conflict)
    cases.append({'fault_id': 'F_IMMUTABLE', 'manifest': conflict, 'expected_detector': 'F_CORRUPT',
                  'expected_action': 'QUARANTINE_CONFLICT_RETAIN_ORIGINAL_THEN_REDELIVER', 'injection_stage': 'observed-delivery',
                  'affected_records': [original['finance_record_id']], 'expected_final_canonical_state': 'ORIGINAL_UNCHANGED'})
    correction = next(r for r in beds if r['corrects_bed_event_id'])
    predecessor = next(r for r in beds if r['bed_event_id'] == correction['corrects_bed_event_id'])
    bed_files = [fixture(root, 'bed-' + label, layouts['bed_event'], [r], mode='EVENT_ARCHIVE') for label, r in [('original', predecessor), ('correction', correction)]]
    files += bed_files
    # Select an actual retroactive workforce correction and explicit revocation.
    retro = next(r for r in workers if r['revision_no'] == 3 and r['valid_from'] < r['known_from'])
    worker_history = [r for r in workers if r['worker_id'] == retro['worker_id']]
    revoke = next(r for r in access if r['decision'] == 'REVOKED')
    grant_history = [r for r in access if r['grant_id'] == revoke['grant_id']]
    worker_files = [fixture(root, 'retroactive-worker-revision-' + str(r['revision_no']), layouts['worker_assignment'], [r]) for r in worker_history]
    grant_files = [fixture(root, 'revoked-grant-revision-' + str(r['revision_no']), layouts['access_scope'], [r]) for r in grant_history]
    files += worker_files + grant_files
    snapshot = fixture(root, 'full-snapshot-reload', layouts['worker_assignment'], worker_history,
                       mode='FULL_SNAPSHOT', scope='workers/full-history', available_at=max(r['export_available_at'] for r in worker_history))
    files.append(snapshot)
    package = {'implementation_phase': 7, 'classification': 'CONTROLLED_SOURCE_CHALLENGES_NOT_VALID_BUSINESS_FACTS',
               'accepted_business_sha256': accepted['business_sha256'],
               'challenge_generator_sha256': footprint(Path(__file__))['sha256'],
               'files': files, 'cases': cases, 'valid_control': valid['file_id'], 'replacement': replacement['file_id'],
               'bed_history': [m['file_id'] for m in bed_files], 'worker_history': [m['file_id'] for m in worker_files], 'worker_snapshot': snapshot['file_id'],
               'grant_history': [m['file_id'] for m in grant_files], 'retroactive_record': retro['worker_assignment_id'], 'revoked_record': revoke['access_scope_id'],
               'published_challenge_record_copies': 0,
               'record_allowance': 64, 'vendor_certified': False}
    observed = {}; records = 0; copies_by_table = {}
    for m in files:
        path = root / m['path']
        with path.open(encoding='utf-8', newline='') as stream:
            count = sum(1 for _ in stream) if path.suffix == '.jsonl' else max(0, sum(1 for _ in csv.reader(stream)) - 1)
        records += count; copies_by_table[m['table']] = copies_by_table.get(m['table'], 0) + count
        for field in ('path', 'dictionary_path'):
            observed[m[field]] = footprint(root / m[field])
    package.update(published_challenge_record_copies=records, published_copies_by_table=copies_by_table, observed_artifacts=observed)
    package['delivery_scenarios'] = [
        {'fault_id': name, 'affected_files': ids, 'injection_stage': 'observed-delivery', 'expected_detector': detector,
         'expected_action': action, 'expected_final_canonical_state': state}
        for name, ids, detector, action, state in [
            ('F_DUP', [valid['file_id']], 'EXACT_FILE_ID', 'DEDUPLICATE', 'ONE_ORIGINAL_VERSION'),
            ('F_MISSING', [valid['file_id']], 'F_MISSING', 'BLOCK_CLOSE_UNTIL_EXPECTED_FILE', 'EXACT_VALID_CONTROL'),
            ('F_REPLACE', [valid['file_id'], replacement['file_id']], 'EXPLICIT_PREDECESSOR_SCOPE', 'REPLACE_SCOPE_RETAIN_HISTORY', 'ONE_CURRENT_REPLACEMENT'),
            ('F_LATE', [m['file_id'] for m in reversed(bed_files)], 'SOURCE_AVAILABILITY_AND_EFFECTIVE_SEQUENCE', 'WAIT_FOR_PREDECESSOR_REPROJECT', 'CORRECTED_BED_STATE'),
            ('WORKDAY_RETRO', [m['file_id'] for m in worker_files], 'VALID_PLUS_KNOWLEDGE_TIME', 'RETAIN_EARLIER_KNOWLEDGE', 'LATEST_APPLICABLE_REVISION'),
            ('WORKDAY_REVOKE', [m['file_id'] for m in grant_files], 'EXPLICIT_REVOKED_REVISION', 'REVOKE_SCOPE', 'REVOKED_NO_INHERITED_ALLOW'),
            ('FULL_SNAPSHOT', [snapshot['file_id']], 'EXACT_VERSION_AND_FILE_ID', 'IDEMPOTENT_RELOAD', 'NO_ADDITIONAL_WORKER_VERSIONS')]]
    if package['published_challenge_record_copies'] > 64:
        raise ValueError('challenge allowance exceeded')
    atomic_json(root / 'challenge-manifest.json', package)
    return package


def exercise_faults(root, package, scratch):
    """Execute every published defect against an isolated store, proving repair."""
    layouts = contracts(); index = {m['file_id']: m for m in package['files']}; valid = index[package['valid_control']]
    outcomes = []; scratch = Path(scratch); scratch.mkdir(parents=True, exist_ok=True)
    def record(case, observed, disposition):
        outcomes.append({'fault_id': case, 'status': 'PASS', 'observed': observed, 'disposition': disposition})
    for case in package['cases']:
        with_replay = DeliveryReplay(':memory:'); m = case['manifest']; layout = layouts[m['table']]
        try:
            if case['fault_id'] == 'F_IMMUTABLE':
                with_replay.ingest(root, valid, layout)
            before = with_replay.table_hash(m['table'])
            try:
                with_replay.ingest(root, m, layout)
            except ValueError as exc:
                if case['expected_detector'] not in str(exc):
                    raise AssertionError('wrong source fault detector: ' + str(exc)) from exc
                observed = str(exc)
            else:
                raise AssertionError('missed controlled source fault: ' + case['fault_id'])
            if with_replay.table_hash(m['table']) != before:
                raise AssertionError('quarantine partially applied source file')
            try:
                with_replay.certify([valid['file_id']])
            except ValueError:
                pass
            else:
                raise AssertionError('unresolved fault passed certification')
            with_replay.recover(root, valid, layout, m['file_id']); with_replay.certify([valid['file_id']])
            if with_replay.rows(m['table']) != read_file(root, valid, layout):
                raise AssertionError('repair changed intended canonical state')
            record(case['fault_id'], observed, 'QUARANTINED_ATOMICALLY_AND_RESOLVED')
        finally:
            with_replay.close()
    replay = DeliveryReplay(':memory:')
    try:
        layout = layouts['finance_monthly']; revised = index[package['replacement']]
        try:
            replay.certify([valid['file_id']])
        except ValueError as exc:
            if 'F_MISSING' not in str(exc):
                raise
            record('F_MISSING', str(exc), 'INCOMPLETE_NOT_ZERO; RECOVERED_BY_EXPECTED_FILE')
        else:
            raise AssertionError('missing file was accepted')
        replay.ingest(root, valid, layout)
        before = replay.table_hash('finance_monthly')
        if replay.ingest(root, valid, layout) != 'DUPLICATE' or replay.table_hash('finance_monthly') != before:
            raise AssertionError('duplicate changed totals')
        record('F_DUP', 'Exact file replay is a no-op', 'DEDUPLICATED')
        replay.ingest(root, revised, layout)
        old = replay.rows('finance_monthly', valid['available_at'], valid['scope'])
        current = replay.rows('finance_monthly', revised['available_at'], valid['scope'])
        if old != read_file(root, valid, layout) or current != read_file(root, revised, layout) or len(current) != 1:
            raise AssertionError('replacement added values or destroyed history')
        record('F_REPLACE', 'Original historical value; one replacement current value', 'REPLACED_EXACT_SCOPE_NOT_ADDED')
        replay.certify([valid['file_id'], revised['file_id']])
    finally:
        replay.close()
    replay = DeliveryReplay(':memory:')
    try:
        layout = layouts['bed_event']; old, correction = [index[k] for k in package['bed_history']]
        replay.ingest(root, correction, layout); replay.ingest(root, old, layout)
        original_row = read_file(root, old, layout)[0]; corrected_row = read_file(root, correction, layout)[0]
        historic = replay.rows('bed_event', old['available_at'])
        current = replay.rows('bed_event', correction['available_at'])
        if historic != [original_row] or {r['bed_event_id'] for r in current} != {original_row['bed_event_id'], corrected_row['bed_event_id']}:
            raise AssertionError('late correction leaked or lost predecessor')
        live = [r for r in current if r['bed_event_id'] not in {r['corrects_bed_event_id'] for r in current if r['corrects_bed_event_id']}]
        if live != [corrected_row]:
            raise AssertionError('effective bed correction did not converge')
        record('F_LATE', 'Out-of-order delivery converged; correction unavailable in earlier history', 'HISTORY_PRESERVED_EFFECTIVE_STATE_REPROJECTED')
    finally:
        replay.close()
    from .source_reader import effective_versions
    for table, file_key, stable, target_key, record_id in [
        ('worker_assignment', 'worker_history', 'worker_id', 'worker_assignment_id', package['retroactive_record']),
        ('access_scope', 'grant_history', 'grant_id', 'access_scope_id', package['revoked_record'])]:
        replay = DeliveryReplay(':memory:')
        try:
            for file_id in package[file_key]:
                replay.ingest(root, index[file_id], layouts[table])
            rows = replay.rows(table); target = next(r for r in rows if r[target_key] == record_id)
            known = target['export_available_at']; effective = max(target['valid_from'], known)
            selected = effective_versions(replay.rows(table, known), stable, effective, known)
            if not any(r[target_key] == record_id for r in selected) or (table == 'access_scope' and any(r['decision'] != 'REVOKED' for r in selected)):
                raise AssertionError('retroactive worker or revoked access not resolved')
            before_known = (datetime.fromisoformat(known.replace('Z', '+00:00')) - timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            prior = effective_versions(replay.rows(table, before_known), stable, effective, before_known)
            if any(r[target_key] == record_id for r in prior):
                raise AssertionError('correction appeared before source availability')
        finally:
            replay.close()
        record('WORKDAY_RETRO' if table == 'worker_assignment' else 'WORKDAY_REVOKE',
               'Earlier knowledge excludes revision; later knowledge resolves exact effective version', 'EXPLICIT_REVOKED' if table == 'access_scope' else 'BITEMPORAL_HISTORY_PRESERVED')
    replay = DeliveryReplay(':memory:')
    try:
        snapshot = index[package['worker_snapshot']]; layout = layouts['worker_assignment']
        replay.ingest(root, snapshot, layout); before = replay.table_hash('worker_assignment')
        if replay.ingest(root, snapshot, layout) != 'DUPLICATE' or replay.table_hash('worker_assignment') != before:
            raise AssertionError('full-snapshot reload duplicated workforce')
        record('FULL_SNAPSHOT', 'Reload preserves exact workforce versions', 'IDEMPOTENT_RELOAD')
    finally:
        replay.close()
    if len({r['fault_id'] for r in outcomes}) != len(outcomes):
        raise AssertionError('duplicated fault outcome')
    return {'status': 'PASS', 'outcomes': outcomes, 'unresolved_release_blocking_faults': 0,
            'published_challenge_record_copies': package['published_challenge_record_copies']}
