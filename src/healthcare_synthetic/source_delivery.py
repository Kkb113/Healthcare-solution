"""Restartable source simulation around an immutable accepted financial snapshot."""
from __future__ import annotations

import hashlib
import json
import platform
from importlib import metadata, resources
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .core import digest
from .engine import atomic_json, single_writer
from .source_export import export_file, footprint, partition_rows
from .source_layouts import ROOT, contracts, read, read_rows
from .source_reports import reports


def locks():
    if platform.python_version() != '3.10.10' or platform.python_implementation() != 'CPython' or metadata.version('tzdata') != '2025.2' or hashlib.sha256(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()).hexdigest() != 'c27b739ff46a7df0594e120d725b439217e11e44ea9a50cdc49130383b5482e7':
        raise ValueError('accepted source simulation runtime differs')
    # Native files depend on producers, not disposable readers/review controls.
    # The latter are bound independently by complete regression fingerprints.
    modules = ('source_layouts', 'source_export', 'source_reports', 'source_delivery', 'core', 'engine')
    paths = [ROOT / ('src/healthcare_synthetic/' + module + '.py') for module in modules]
    paths += [ROOT / 'pyproject.toml']
    paths += [ROOT / 'contracts/source-delivery-policy.json', ROOT / 'config/source-delivery-generation.json',
              ROOT / 'contracts/phase0/schema.json', ROOT / 'contracts/phase0/source-contracts.json',
              ROOT / 'evidence/financial-history/acceptance-gate.json']
    return {p.relative_to(ROOT).as_posix(): footprint(p)['sha256'] for p in paths}


def accepted_parent():
    cfg = read(ROOT / 'config/source-delivery-generation.json')
    expected = {'profile': 'ACCEPTED_SOURCE_DELIVERY', 'parent_candidate': 'output/financial-history',
                'parent_business_sha256': '773a236ec9c7ec3df5605f38d21f4934a9384eae1bbf04ab4bf164cb51006b72',
                'schema_version': 'synthetic-source-1', 'closing_grace': '2026-01-10T23:59:59Z'}
    if cfg != expected:
        raise ValueError('reviewed source configuration differs')
    parent = ROOT / cfg['parent_candidate']
    m = read(parent / 'manifest.json'); gate = read(ROOT / 'evidence/financial-history/acceptance-gate.json')
    if m['status'] != 'FINANCIAL_HISTORY_PASSED' or gate['status'] != 'PASSED' or m['business_sha256'] != cfg['parent_business_sha256'] or gate['business_sha256'] != m['business_sha256']:
        raise ValueError('accepted financial parent anchor differs')
    if {p.relative_to(parent).as_posix() for p in (parent / 'canonical').iterdir()} != {f['file'] for f in m['canonical_files'].values()}:
        raise ValueError('accepted parent file inventory differs')
    if digest({k: v['sha256'] for k, v in sorted(m['canonical_files'].items())}) != m['business_sha256']:
        raise ValueError('accepted parent digest differs')
    for table, f in m['canonical_files'].items():
        path = (parent / f['file']).resolve()
        if parent.resolve() not in path.parents or footprint(path) != {k: f[k] for k in ('sha256', 'bytes')}:
            raise ValueError('accepted parent bytes differ: ' + table)
        with path.open('rb') as stream:
            if sum(1 for _ in stream) != f['rows']:
                raise ValueError('accepted parent row count differs')
    return parent, m


def batch_time(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    arrival = dt.replace(hour=7, minute=0, second=0)
    if arrival < dt:
        arrival += timedelta(days=1)
    return arrival.strftime('%Y-%m-%dT%H:%M:%SZ')


def primary_exports(root, layout, rows):
    table = layout['table']; groups = partition_rows(table, rows); result = []
    if layout['source'] == 'WORKDAY':
        groups = defaultdict(list)
        for row in rows:
            groups[batch_time(row['export_available_at'])].append(row)
        # Daily scheduled changes include explicit empty extracts, not silently missing partitions.
        if table in ('worker_assignment', 'access_scope'):
            dt = datetime(2023, 1, 1, 7, tzinfo=timezone.utc)
            while dt <= datetime(2026, 1, 10, 7, tzinfo=timezone.utc):
                groups[dt.strftime('%Y-%m-%dT%H:%M:%SZ')]
                dt += timedelta(days=1)
    if table == 'finance_monthly':
        groups = defaultdict(list)
        for row in rows:
            family = ('statistics-workforce' if row['measure_code'] == 'FTE' else 'statistics-volume') if row['quantity'] is not None else (
                     'actual-long' if row['scenario'] == 'ACTUAL' else 'forecast-amount' if row['scenario'] == 'FORECAST' else
                     'budget-revised' if 'MIDYEAR' in row['vintage_id'] else 'budget-original')
            groups[(row['source_file_id'], family)].append(row)
    ordered = sorted(groups.items(), key=lambda item: (min((r['export_available_at'] for r in item[1]), default=str(item[0])), str(item[0])))
    for key, batch in ordered:
        label = digest(key)[:24] if table == 'finance_monthly' else str(key).replace(':', '').replace('T', '-').replace('Z', '')
        family = key[1] if table == 'finance_monthly' else None
        mode = 'EVENT_ARCHIVE' if layout['format'] == 'JSONL_EVENT_ENVELOPE' else 'IMMUTABLE_VERSION_DELTA'
        scope = table + '/' + str(key); arrival = None; prior = None
        if layout['source'] == 'WORKDAY':
            arrival = key
        if table == 'finance_monthly':
            r = batch[0]
            mode = 'REPLACE_DECLARED_SCOPE_VERSION' if r['scenario'] == 'ACTUAL' else 'APPEND_VINTAGE'
            scope = '/'.join((r['report_template_id'], r['accounting_month'], r['scenario'], family))
            if r['scenario'] == 'ACTUAL' and r['supersedes_vintage_id']:
                candidates = [m for m in result if m['scope'] == scope and r['supersedes_vintage_id'] in m['vintages']]
                if len(candidates) != 1:
                    raise ValueError('Axiom predecessor identity not unique')
                prior = candidates[0]['file_id']
        elif table in ('inventory_movement', 'financial_posting', 'service_charge', 'claim_event', 'cost_allocation'):
            mode = 'ADDITIVE_TRANSACTION'
        result.append(export_file(root, layout, batch, label, mode=mode, scope=scope,
                                  available_at=arrival, replacement_of=prior, family=family))
    return result


def weekly_snapshots(root, layout, rows):
    if layout['table'] not in ('worker_assignment', 'cost_center'):
        return []
    dt = datetime(2022, 12, 18, 7, tzinfo=timezone.utc); result = []
    while dt.year < 2026:
        as_of = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        batch = [r for r in rows if r['export_available_at'] <= as_of]
        result.append(export_file(root, layout, batch, 'weekly-' + dt.strftime('%Y%m%d'), mode='FULL_SNAPSHOT',
                      role='SCHEDULED_MIRROR', available_at=as_of, scope=layout['table'] + '/weekly-history'))
        dt += timedelta(days=7)
    return result


def run_sources(output=ROOT / 'output/source-delivery', *, fail_table=None, crash_table=None):
    output = Path(output).resolve()
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output', 'data'):
        raise ValueError('source artifacts must stay in ignored workspace output/data')
    if any(t is not None and t not in contracts() for t in (fail_table, crash_table)):
        raise ValueError('unknown source failure table')
    output.mkdir(parents=True, exist_ok=True)
    with single_writer(output / 'run.lock'):
        old = read(output / 'manifest.json') if (output / 'manifest.json').exists() else None
        if old and old.get('profile') != 'ACCEPTED_SOURCE_DELIVERY':
            raise ValueError('wrong source output profile')
        (output / 'candidate-ready.json').unlink(missing_ok=True)
        manifest = {'profile': 'ACCEPTED_SOURCE_DELIVERY', 'implementation_phase': 7, 'status': 'RUNNING',
                    'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION', 'executed': [], 'reused': []}
        atomic_json(output / 'manifest.json', manifest)
        try:
            parent, accepted = accepted_parent(); before = locks(); layouts = contracts()
            atomic_json(output / 'source-dictionary.json', layouts)
            native = {}
            for table, key, label, kind in [('worker_assignment', 'worker_id', 'employee_number', 'WORKER'),
                                           ('cost_center', 'cost_center_id', 'cost_center_code', 'COST_CENTER'),
                                           ('patient', 'patient_id', 'mrn', 'PATIENT'), ('catalog_item', 'catalog_item_id', 'code', 'ACCOUNT')]:
                for row in read_rows(parent / accepted['canonical_files'][table]['file']):
                    if table != 'catalog_item' or row['domain'] == 'ACCOUNT':
                        value = (kind, row[label])
                        if row[key] in native and native[row[key]] != value:
                            raise ValueError('native source identity changed across immutable versions')
                        native[row[key]] = value
            # Native aliases are writer context. The published per-file typed key
            # dictionaries, rather than generator context, drive independent readers.
            layouts = {k: {**layout, 'native_aliases': native} for k, layout in layouts.items()}
            files = []; journals = output / 'checkpoints'; journals.mkdir(exist_ok=True)
            for table, layout in layouts.items():
                checkpoint = journals / (table.replace('_', '-') + '.json')
                fingerprint = digest({'locks': before, 'canonical': accepted['canonical_files'][table]})
                previous = read(checkpoint) if checkpoint.exists() else None
                if previous and previous['fingerprint'] == fingerprint:
                    for m in previous['files']:
                        for key, metrics in (('path', m), ('dictionary_path', m['dictionary'])):
                            if footprint(output / m[key]) != {k: metrics[k] for k in ('sha256', 'bytes')}:
                                raise ValueError('source checkpoint artifact corruption: ' + m[key])
                    result = previous['files']; manifest['reused'].append(table)
                else:
                    if previous:
                        for m in previous['files']:
                            for key in ('path', 'dictionary_path'):
                                p = (output / m[key]).resolve()
                                if output not in p.parents:
                                    raise ValueError('checkpoint path escaped output')
                                p.unlink(missing_ok=True)
                    with (parent / accepted['canonical_files'][table]['file']).open(encoding='utf-8') as stream:
                        rows = [json.loads(line) for line in stream]
                    result = primary_exports(output, layout, rows) + weekly_snapshots(output, layout, rows)
                    del rows
                    if table == crash_table:
                        import os
                        os._exit(97)
                    if table == fail_table:
                        raise ValueError('injected uncommitted source export: ' + table)
                    atomic_json(checkpoint, {'fingerprint': fingerprint, 'files': result})
                    manifest['executed'].append(table)
                files += result
                print('Source export ' + table + ': ' + ('reused' if table in manifest['reused'] else 'written'), flush=True)
                if locks() != before:
                    raise ValueError('source inputs changed during export; unaccepted run stopped')
            def load(table):
                return read_rows(parent / accepted['canonical_files'][table]['file'])
            derived = reports(output, load('finance_monthly'), load('cost_center'), load('catalog_item'))
            if locks() != before or accepted_parent()[1]['business_sha256'] != accepted['business_sha256']:
                raise ValueError('source inputs changed during export')
            manifest.update(status='EXPORTED_NOT_YET_VALIDATED', locks=before, source_dictionary_sha256=footprint(output / 'source-dictionary.json')['sha256'], business_sha256=accepted['business_sha256'],
                canonical_business_rows=accepted['business_rows'], business_tables=25, files=files, reports=derived,
                primary_source_rows=sum(m['expected_rows'] for m in files if m['role'] == 'PRIMARY'),
                scheduled_mirror_rows=sum(m['expected_rows'] for m in files if m['role'] != 'PRIMARY'),
                dictionary_mapping_rows=sum(m['dictionary_rows'] for m in files),
                derived_report_rows=sum(m['expected_rows'] for m in derived),
                derived_scalar_fact_mirrors=sum(m['mirrored_scalar_facts'] for m in derived),
                source_payload_bytes=sum(m['bytes'] + m['dictionary']['bytes'] for m in files) + sum(m['bytes'] for m in derived))
            atomic_json(output / 'manifest.json', manifest)
            return manifest
        except Exception as exc:
            manifest.update(status='FAILED', error=str(exc)); atomic_json(output / 'manifest.json', manifest); raise
