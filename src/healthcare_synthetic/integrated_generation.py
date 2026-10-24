"""Integrated candidate experiments; accepted snapshots are never overwritten.

The primary seed reuses immutable resource facts. Comparison seeds regenerate
calendar-conditioned demand, capacity, care, labor and stock against the same
fictional catchment. All three regenerate finance. No months are tiled.
"""
from __future__ import annotations

import hashlib
import json
import logging
import platform
from importlib import metadata, resources
from decimal import Context, ROUND_HALF_UP, localcontext
from pathlib import Path

from .core import canonical, digest
from .engine import Store, atomic_json, check_budget, single_writer

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'config/integrated-history-generation.json'
STAGES = ('resources', 'billing', 'claims', 'posting', 'allocation', 'planning')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def schema():
    from .financial_pipeline import finance_schema
    result = finance_schema(); cfg = read(CONFIG)
    for table in result['tables']:
        table['planned_rows'] = cfg['table_budget_reassignment'].get(table['name'], table['planned_rows'])
    if sum(t['planned_rows'] for t in result['tables']) != cfg['planned_rows']:
        raise ValueError('integrated budget does not conserve the reviewed envelope')
    return result


def financial_config(seed):
    cfg = read(ROOT / 'config/financial-history-generation.json')
    cfg.update(seed=seed, denial_basis_points=read(CONFIG)['denial_basis_points'])
    return cfg


def load_snapshot(path):
    path = Path(path); m = read(path / 'manifest.json'); result = {}
    expected = {f['file'] for f in m['canonical_files'].values()}
    if {p.relative_to(path).as_posix() for p in (path / 'canonical').iterdir()} != expected:
        raise ValueError('snapshot inventory differs')
    for table, meta in m['canonical_files'].items():
        target = (path / meta['file']).resolve()
        if path.resolve() not in target.parents or sha_file(target) != meta['sha256'] or target.stat().st_size != meta['bytes']:
            raise ValueError('snapshot bytes differ: ' + table)
        with target.open('rb') as stream:
            result[table] = [json.loads(line) for line in stream]
        if len(result[table]) != meta['rows']:
            raise ValueError('snapshot row count differs: ' + table)
    if digest({k: v['sha256'] for k, v in sorted(m['canonical_files'].items())}) != m['business_sha256']:
        raise ValueError('snapshot business hash differs')
    return result, m


def dependencies():
    # Producer locks deliberately exclude consumers/reviews. Tests bind those
    # separately. A changed generator/assumption invalidates every later stage.
    runtime = read(ROOT/'contracts/phase1/runtime-lock.json')['runtime']
    observed = {'python':platform.python_version(),'implementation':platform.python_implementation(),
                'tzdata':metadata.version('tzdata'),'chicago_sha256':hashlib.sha256(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()).hexdigest()}
    if observed != runtime:
        raise ValueError('integrated generator runtime differs from approved lock')
    modules = ('core', 'engine', 'master_generation', 'clinical_generation', 'operational_demand',
               'operational_generation', 'operational_timing', 'resource_generation',
               'resource_workforce', 'resource_inventory', 'financial_common', 'financial_billing',
               'financial_postings', 'financial_allocations', 'financial_planning', 'financial_pipeline',
               'operational_validation', 'resource_stock_validation', 'master_validation', 'trajectory_scheduling', 'integrated_master_context', 'integrated_generation')
    files = [ROOT / f'src/healthcare_synthetic/{m}.py' for m in modules]
    files += sorted((ROOT / 'config').glob('*generation.json'))
    files += sorted((ROOT / 'contracts').rglob('*.json'))
    files += [ROOT / 'evidence/resource-foundation/acceptance-gate.json']
    return {p.relative_to(ROOT).as_posix(): sha_file(p) for p in files}


def write_snapshot(tables, output):
    files = {}; directory = output / 'canonical'; directory.mkdir(parents=True, exist_ok=True)
    specs = {t['name']: t for t in schema()['tables']}
    for name, values in tables.items():
        pk = specs[name]['primary_key'][0]; target = directory / (name.replace('_', '-') + '.jsonl')
        temp = target.with_suffix('.tmp'); h = hashlib.sha256(); size = 0
        with temp.open('wb') as stream:
            for row in sorted(values, key=lambda r: r[pk]):
                data = (canonical(row) + '\n').encode(); stream.write(data); h.update(data); size += len(data)
        temp.replace(target)
        files[name] = {'file': target.relative_to(output).as_posix(), 'rows': len(values), 'bytes': size, 'sha256': h.hexdigest()}
    return files


def regenerated_resources(seed):
    """Full connected comparison experiment, not a downsample of facts."""
    from .operational_demand import DemandGenerator
    from .operational_generation import connect_site_transfers, FlowSimulator
    from .resource_generation import coordinate_services
    from .resource_workforce import WorkforceGenerator, bind_working_authors
    from .resource_inventory import InventoryGenerator
    from .integrated_master_context import amend
    master, _ = load_snapshot(ROOT / 'output/master-foundation'); master = amend(master)
    ccfg = read(ROOT / 'config/clinical-history-generation.json'); ccfg['seed'] = seed
    ocfg = read(ROOT / 'config/operational-flow-generation.json'); ocfg['seed'] = seed
    rcfg = read(ROOT / 'config/resource-foundation-generation.json'); rcfg['seed'] = seed
    policy = read(ROOT / 'contracts/clinical-history-policy.json'); run_id = f'integrated-resources-{seed}'
    g = DemandGenerator(master, ccfg, policy, run_id, ocfg)
    journeys = connect_site_transfers(g, g.journeys(), ocfg['continuous_site_transfers'], ocfg)
    tables = {**master, **journeys}
    opening = [r for r in master['clinical_condition'] if r['encounter_version_id'] is None]
    tables['clinical_condition'] = opening + journeys['clinical_condition']
    g = DemandGenerator(tables, ccfg, policy, run_id, ocfg)
    tables.update(g.appointments()); tables.update(g.placement_assessments())
    sim = FlowSimulator(tables, g, ocfg); beds, simulation = sim.run(); tables = sim.t; tables.update(beds)
    g = DemandGenerator(tables, ccfg, policy, run_id, ocfg)
    care = g.care(); tables['clinical_event'] = tables.get('clinical_event', []) + care['clinical_event']
    tables['clinical_event'] += g.triage()['clinical_event']; tables.update(g.drivers())
    for operation in (lambda t: coordinate_services(t, rcfg, run_id),
                      lambda t: WorkforceGenerator(t, rcfg, run_id).plan().materialize(),
                      lambda t: bind_working_authors(t, rcfg, run_id),
                      lambda t: InventoryGenerator(t, rcfg, run_id).run()):
        tables.update(operation(tables)['tables'])
    return {'tables': tables, 'controls': {'simulation': simulation, 'all_domains_regenerated': True}}


def generate(seed, output, *, fail_stage=None, crash_stage=None):
    from .financial_billing import billing, claims
    from .financial_postings import postings
    from .financial_allocations import allocations
    from .financial_planning import monthly
    cfg = read(CONFIG)
    if type(seed) is not int or seed not in [cfg['primary_seed'], *cfg['comparison_seeds']]:
        raise ValueError('seed is not in the preregistered experiment')
    output = Path(output).resolve()
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output', 'data'):
        raise ValueError('candidate must stay in ignored workspace output/data')
    if fail_stage not in (None, *STAGES) or crash_stage not in (None, *STAGES):
        raise ValueError('unknown integrated failure stage')
    output.mkdir(parents=True, exist_ok=True)
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)), single_writer(output / 'run.lock'):
        before = dependencies(); local = digest({'files': before, 'seed': seed})
        old_manifest = read(output / 'manifest.json') if (output / 'manifest.json').exists() else None
        if old_manifest and old_manifest.get('profile') != cfg['profile']:
            raise ValueError('wrong integrated candidate profile')
        (output / 'candidate-ready.json').unlink(missing_ok=True)
        manifest = {'profile': cfg['profile'], 'implementation_phase': 8, 'seed': seed, 'status': 'RUNNING',
                    'locks': before, 'executed': [], 'reused': [], 'invalidated': [], 'full_dataset_accepted': False,
                    'solution_status': cfg['solution_status']}
        atomic_json(output / 'manifest.json', manifest); store = Store(output / 'checkpoints.sqlite3')
        try:
            cached = store.stages(); tables = {}; hashes = {}; previous = {}
            for stage in STAGES:
                fingerprint = digest({'local': local, 'parents': previous}); old = cached.get(stage)
                if old and hashlib.sha256(old['payload'].encode()).hexdigest() != old['checksum']:
                    raise ValueError('integrated checkpoint corruption: ' + stage)
                if old and old['input_hash'] == fingerprint:
                    value = json.loads(old['payload']); checksum = old['checksum']; manifest['reused'].append(stage)
                else:
                    if old:
                        manifest['invalidated'].append(stage)
                    if stage == 'resources':
                        if seed == cfg['primary_seed']:
                            rows, parent = load_snapshot(ROOT / cfg['accepted_resource_candidate'])
                            if parent['business_sha256'] != cfg['accepted_resource_sha256']:
                                raise ValueError('accepted resource anchor differs')
                            from .integrated_master_context import amend
                            rows = amend(rows)
                            value = {'tables': rows, 'controls': {'simulation': parent['simulation'], 'all_domains_regenerated': False,
                                     'master_context_version':cfg['master_context_version']}}
                        else:
                            value = regenerated_resources(seed)
                    else:
                        functions = {'billing': billing, 'claims': claims, 'posting': postings, 'allocation': allocations, 'planning': monthly}
                        value = functions[stage](tables, financial_config(seed), f'integrated-{seed}-{stage}')
                    check_budget({**tables, **value['tables']}, cfg['planned_rows'], schema())
                    if stage == 'resources':
                        # Hash file-backed context instead of exceeding SQLite's
                        # single-cell string limit with a whole resource snapshot.
                        context = output / 'resource-context'
                        resource_files = write_snapshot(value['tables'], context)
                        resource_hash = digest({k: v['sha256'] for k,v in sorted(resource_files.items())})
                        atomic_json(context / 'manifest.json', {'canonical_files': resource_files, 'business_sha256': resource_hash})
                        tables = value['tables']
                        value = {'tables': {}, 'controls': value['controls'], 'resource_sha256': resource_hash}
                    checksum = store.publish(stage, local, fingerprint, value, fail=stage == fail_stage, crash=stage == crash_stage)
                    manifest['executed'].append(stage)
                if stage == 'resources' and stage in manifest['reused']:
                    tables, context = load_snapshot(output / 'resource-context')
                    if context['business_sha256'] != value['resource_sha256']:
                        raise ValueError('resource checkpoint file hash differs')
                tables.update(value['tables']); hashes[stage] = checksum; previous[stage] = checksum
                if stage == 'resources':
                    manifest['simulation'] = value['controls']['simulation']
                print(f'Integrated {seed} {stage}: ' + ('reused' if stage in manifest['reused'] else 'written'), flush=True)
                del value, old
            files = {}; directory = output / 'canonical'; directory.mkdir(exist_ok=True)
            for table in schema()['tables']:
                name = table['name']; pk = table['primary_key'][0]; target = directory / (name.replace('_', '-') + '.jsonl')
                temp = target.with_suffix('.tmp'); h = hashlib.sha256(); size = 0
                with temp.open('wb') as stream:
                    for row in sorted(tables[name], key=lambda r: r[pk]):
                        data = (canonical(row) + '\n').encode(); stream.write(data); h.update(data); size += len(data)
                temp.replace(target)
                files[name] = {'file': target.relative_to(output).as_posix(), 'rows': len(tables[name]), 'bytes': size, 'sha256': h.hexdigest()}
            if dependencies() != before:
                raise ValueError('integrated producer inputs changed during generation')
            manifest.update(status='CANDIDATE_NOT_YET_ACCEPTED', canonical_files=files, rows_by_table={k: v['rows'] for k, v in files.items()},
                            business_rows=sum(v['rows'] for v in files.values()), business_tables=len(files),
                            business_sha256=digest({k: v['sha256'] for k, v in sorted(files.items())}), stage_checksums=hashes,
                            checkpoint_mirror_rows=sum(r['row_count'] for r in store.stages().values()))
        except Exception as exc:
            manifest.update(status='FAILED', error=str(exc)); raise
        finally:
            store.close(); atomic_json(output / 'manifest.json', manifest)
    return manifest
