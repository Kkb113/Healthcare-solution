"""Regenerate native source simulations for an explicitly changed candidate.

Uses the accepted source scalar contracts/serializers; never changes Phase 7
truth anchors or reuses their acceptance for changed financial facts.
"""
from __future__ import annotations

import json
from pathlib import Path

from .engine import atomic_json, single_writer
from .integrated_generation import ROOT, read, sha_file
from .source_delivery import primary_exports, weekly_snapshots
from .source_export import footprint
from .source_layouts import contracts, read_rows
from .source_reports import reports
from .source_reader import DeliveryReplay, sha


def source_dependencies():
    names = ('core', 'engine', 'source_layouts', 'source_export', 'source_reports', 'source_delivery', 'source_faults', 'integrated_generation', 'integrated_exports')
    paths = [f'src/healthcare_synthetic/{n}.py' for n in names]
    paths += ['pyproject.toml','contracts/source-delivery-policy.json','contracts/phase0/schema.json',
              'contracts/phase0/source-contracts.json','config/integrated-history-generation.json']
    return {p:sha_file(ROOT/p) for p in paths}


def export(candidate, output, *, fail_table=None, crash_table=None):
    candidate = Path(candidate).resolve(); output = Path(output).resolve(); accepted = read(candidate / 'manifest.json')
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output', 'data'):
        raise ValueError('integrated sources must stay in ignored output/data')
    if accepted['profile'] != 'INTEGRATED_HISTORY_CANDIDATE' or accepted['status'] not in ('CANDIDATE_NOT_YET_ACCEPTED', 'ELIGIBLE_FOR_CERTIFICATION'):
        raise ValueError('source candidate is incomplete')
    for meta in accepted['canonical_files'].values():
        if candidate not in (candidate/meta['file']).resolve().parents:
            raise ValueError('canonical export input escaped candidate')
    layouts = contracts()
    if fail_table not in (None, *layouts) or crash_table not in (None, *layouts):
        raise ValueError('unknown integrated export failure table')
    before = source_dependencies(); output.mkdir(parents=True, exist_ok=True)
    with single_writer(output / 'run.lock'):
        if (output / 'manifest.json').exists() and read(output / 'manifest.json').get('profile') != 'INTEGRATED_SOURCE_DELIVERY':
            raise ValueError('foreign export profile')
        (output / 'candidate-ready.json').unlink(missing_ok=True)
        atomic_json(output / 'source-dictionary.json', layouts); native = {}
        for table, key, label, kind in [('worker_assignment','worker_id','employee_number','WORKER'), ('cost_center','cost_center_id','cost_center_code','COST_CENTER'),
                                        ('patient','patient_id','mrn','PATIENT'), ('catalog_item','catalog_item_id','code','ACCOUNT')]:
            for row in read_rows(candidate / accepted['canonical_files'][table]['file']):
                if table != 'catalog_item' or row['domain'] == 'ACCOUNT':
                    native[row[key]] = (kind, row[label])
        files = []; executed = []; reused = []; checkpoint = output / 'checkpoints'; checkpoint.mkdir(exist_ok=True)
        m = {'profile': 'INTEGRATED_SOURCE_DELIVERY', 'implementation_phase': 8, 'status': 'RUNNING', 'locks': before,
             'business_sha256': accepted['business_sha256'], 'canonical_business_rows': accepted['business_rows'], 'business_tables': 25,
             'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION'}
        atomic_json(output / 'manifest.json', m)
        try:
            for table, layout in layouts.items():
                meta = accepted['canonical_files'][table]; path = candidate / meta['file']
                if footprint(path) != {k: meta[k] for k in ('bytes','sha256')}:
                    raise ValueError('changed export canonical bytes: ' + table)
                key = sha({'locks': before, 'canonical': meta}); state = checkpoint / (table.replace('_','-')+'.json')
                old = read(state) if state.exists() else None
                if old and old['fingerprint'] == key:
                    result = old['files']
                    for f in result:
                        for p, metrics in ((f['path'], f), (f['dictionary_path'], f['dictionary'])):
                            if footprint(output / p) != {k: metrics[k] for k in ('bytes','sha256')}:
                                raise ValueError('integrated source checkpoint artifact corruption')
                    reused.append(table)
                else:
                    if old:
                        for f in old['files']:
                            for field in ('path','dictionary_path'):
                                target = (output / f[field]).resolve()
                                if output not in target.parents:
                                    raise ValueError('checkpoint cleanup escaped integrated export')
                                target.unlink(missing_ok=True)
                    values = read_rows(path); writer_layout = {**layout, 'native_aliases': native}
                    result = primary_exports(output, writer_layout, values) + weekly_snapshots(output, writer_layout, values); del values
                    if table == crash_table:
                        import os
                        os._exit(97)
                    if table == fail_table:
                        raise ValueError('injected integrated export failure')
                    atomic_json(state, {'fingerprint': key, 'files': result}); executed.append(table)
                files.extend(result)
                print('Integrated native export: ' + table, flush=True)
            def load(table):
                return read_rows(candidate / accepted['canonical_files'][table]['file'])
            derived = reports(output, load('finance_monthly'), load('cost_center'), load('catalog_item'))
            if source_dependencies() != before or read(candidate / 'manifest.json')['business_sha256'] != accepted['business_sha256']:
                raise ValueError('integrated source producer/parent changed')
            m.update(status='EXPORTED_NOT_YET_VALIDATED', files=files, reports=derived, executed=executed, reused=reused,
                     source_dictionary_sha256=sha_file(output / 'source-dictionary.json'), primary_source_rows=sum(f['expected_rows'] for f in files if f['role']=='PRIMARY'),
                     scheduled_mirror_rows=sum(f['expected_rows'] for f in files if f['role']!='PRIMARY'), dictionary_mapping_rows=sum(f['dictionary_rows'] for f in files),
                     derived_report_rows=sum(f['expected_rows'] for f in derived), derived_scalar_fact_mirrors=sum(f['mirrored_scalar_facts'] for f in derived),
                     source_payload_bytes=sum(f['bytes']+f['dictionary']['bytes'] for f in files)+sum(f['bytes'] for f in derived))
        except Exception as exc:
            m.update(status='FAILED', error=str(exc)); raise
        finally:
            atomic_json(output / 'manifest.json', m)
    from .source_faults import build_faults
    build_faults(output, candidate, accepted)
    return m


from .integrated_source_validation import inspect
