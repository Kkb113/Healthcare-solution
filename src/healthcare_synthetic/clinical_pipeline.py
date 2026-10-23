"""Restartable clinical generation using the accepted, immutable master snapshot."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from decimal import Context, ROUND_HALF_UP, localcontext
from pathlib import Path

from .core import canonical, digest
from .engine import Store, atomic_json, check_budget, single_writer
from .clinical_generation import ClinicalGenerator
from .clinical_review import render_journeys, review_gate
from .clinical_validation import ClinicalValidator
from .master_pipeline import ROOT, load_inputs
from .master_validation import MasterValidator

GRAPH = {'accepted_master': (), 'journeys': ('accepted_master',), 'appointments': ('accepted_master', 'journeys'),
         'care_springfield': ('accepted_master', 'journeys'), 'care_peoria': ('accepted_master', 'journeys'),
         'care_rockford': ('accepted_master', 'journeys'),
         'validation': ('accepted_master', 'journeys', 'appointments', 'care_springfield', 'care_peoria', 'care_rockford')}


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def load_master(cfg):
    path = (ROOT / cfg['master_candidate']).resolve()
    if ROOT not in path.parents or path.relative_to(ROOT).parts[0] not in ('output', 'data'):
        raise ValueError('accepted master must be in ignored workspace output/ or data/')
    accepted = read(ROOT / 'evidence/master-data/acceptance-gate.json')
    manifest = read(path / 'manifest.json')
    if accepted['status'] != 'PASSED' or accepted['business_sha256'] != cfg['master_business_sha256'] or manifest['business_sha256'] != cfg['master_business_sha256'] or manifest['status'] != 'MASTER_FOUNDATION_PASSED':
        raise ValueError('master candidate differs from accepted snapshot; explicit acceptance migration required')
    expected_files = {m['file'] for m in manifest['canonical_files'].values()}
    if {p.relative_to(path).as_posix() for p in (path / 'canonical').iterdir() if p.is_file()} != expected_files:
        raise ValueError('master snapshot file inventory differs')
    tables = {}
    for table, meta in manifest['canonical_files'].items():
        file = (path / meta['file']).resolve()
        if path not in file.parents: raise ValueError('master file escaped run directory')
        raw = file.read_bytes()
        if hashlib.sha256(raw).hexdigest() != meta['sha256'] or len(raw) != meta['bytes']:
            raise ValueError('accepted master file checksum mismatch: ' + table)
        rows = [json.loads(line) for line in raw.decode('utf-8').splitlines()]
        if len(rows) != meta['rows']: raise ValueError('master row count mismatch')
        tables[table] = rows
    if digest({t: manifest['canonical_files'][t]['sha256'] for t in sorted(tables)}) != cfg['master_business_sha256']:
        raise ValueError('accepted master content hash differs')
    mc, mp, schema, refs, runtime = load_inputs(ROOT / 'config/master-data-generation.json')
    checked = MasterValidator(tables, schema, mc, mp, refs).run()
    if checked['defects']: raise ValueError('accepted master data fails independent rules: ' + str(checked['defects']))
    return tables, schema, runtime


def merge(outputs):
    tables = {}
    for output in outputs.values():
        for table, rows in output['tables'].items():
            if table in tables:
                if table not in ('clinical_condition', 'clinical_event'):
                    raise ValueError('undeclared shared stage ownership')
                tables[table] = [*tables[table], *rows]
            else:
                tables[table] = rows
    return tables


def run_clinical(config_path=ROOT / 'config/clinical-history-generation.json', output_dir=ROOT / 'output/clinical-histories', *, review_path=ROOT / 'reviews/clinical-journey-review.json', fail_stage=None, crash_stage=None):
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
        return _run(Path(config_path), Path(output_dir).resolve(), Path(review_path), fail_stage, crash_stage)


def _run(config_path, output, review_path, fail_stage, crash_stage):
    cfg, policy = read(config_path), read(ROOT / 'contracts/clinical-history-policy.json')
    baseline_cfg = read(ROOT / 'config/clinical-history-generation.json')
    if cfg['profile'] != 'LONGITUDINAL_CLINICAL' or cfg['window'] != baseline_cfg['window'] or cfg['cohort'] != baseline_cfg['cohort'] or cfg['review_journeys'] < 100 or type(cfg['seed']) is not int:
        raise ValueError('clinical profile/window/cohort/review contract mismatch')
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output', 'data'):
        raise ValueError('clinical candidate must be in ignored workspace output/ or data/')
    if fail_stage not in (None, *GRAPH) or crash_stage not in (None, *GRAPH): raise ValueError('unknown clinical failure hook')
    master, schema, runtime = load_master(cfg)
    paths = sorted((ROOT / 'src/healthcare_synthetic').glob('*.py')) + sorted((ROOT / 'contracts/phase0').glob('*.json'))
    paths += [ROOT / 'contracts/clinical-history-policy.json', ROOT / 'contracts/reference-package-lock.json', ROOT / 'evidence/master-data/acceptance-gate.json']
    locks = {'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, 'runtime': runtime,
             'configuration_sha256': digest(cfg), 'master_business_sha256': cfg['master_business_sha256']}
    global_lock = {'files': locks['files'], 'runtime': runtime}
    review = read(review_path) if review_path.exists() else None
    local = {stage: digest({'global': global_lock, 'config': cfg if stage != 'accepted_master' else {'snapshot': cfg['master_business_sha256']},
                            'review': review if stage == 'validation' else None}) for stage in GRAPH}
    output.mkdir(parents=True, exist_ok=True)
    with single_writer(output / 'run.lock'):
        if (output / 'manifest.json').exists() and read(output / 'manifest.json').get('profile') != cfg['profile']:
            raise ValueError('run directory belongs to another profile')
        manifest = {'profile': cfg['profile'], 'implementation_phase': 3, 'status': 'RUNNING', 'started_at': datetime.now(timezone.utc).isoformat(),
                    'locks': locks, 'executed': [], 'reused': [], 'invalidated': [], 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION',
                    'trajectory_status': policy['trajectory_status']}
        atomic_json(output / 'manifest.json', manifest)
        for leaf in ('candidate-ready.json', 'validation-report.json', 'journey-review-sample.md'):
            (output / leaf).unlink(missing_ok=True)
        store = Store(output / 'checkpoints.sqlite3')
        attempt = None
        try:
            existing = store.stages()
            for stage, row in existing.items():
                if stage not in GRAPH or hashlib.sha256(row['payload'].encode()).hexdigest() != row['checksum']:
                    raise ValueError('clinical checkpoint corruption: ' + stage)
            invalid = {stage for stage, row in existing.items() if row['local_hash'] != local[stage]}
            for stage, parents in GRAPH.items():
                if set(parents) & invalid: invalid.add(stage)
            with store.db:
                for stage in invalid: store.db.execute('DELETE FROM stages WHERE name=?', (stage,))
                store.db.execute("UPDATE attempts SET status='INTERRUPTED' WHERE status='RUNNING'")
                attempt = store.db.execute('INSERT INTO attempts(started,status) VALUES (?,?)', (manifest['started_at'], 'RUNNING')).lastrowid
            for stage in invalid:
                existing.pop(stage, None)
            manifest['invalidated'] = sorted(invalid)
            outputs, hashes = {}, {}
            facilities = {r['facility_code']: r['facility_id'] for r in master['facility']}
            site_codes = {'care_springfield': 'HSP-SPR', 'care_peoria': 'HSP-PEO', 'care_rockford': 'HSP-RFD'}
            for stage, parents in GRAPH.items():
                fingerprint = digest({'local': local[stage], 'parents': {p: hashes[p] for p in parents}})
                cached = existing.pop(stage, None) if stage not in invalid else None
                if cached and cached['input_hash'] == fingerprint:
                    value = json.loads(cached['payload'])
                    hashes[stage] = cached['checksum']
                    manifest['reused'].append(stage)
                else:
                    if stage == 'accepted_master':
                        value = {'tables': master, 'controls': {'accepted_business_sha256': cfg['master_business_sha256']}}
                    elif stage == 'validation':
                        tables = merge(outputs)
                        control = ClinicalValidator(tables, schema, cfg, policy, master).run()
                        _, selection = render_journeys(tables, cfg)
                        control['review_selection'], control['review'] = selection, review_gate(selection, review)
                        control['gate_status'] = ('CLINICAL_HISTORIES_PASSED' if control['review']['status'] == 'PASS' else 'REVIEW_PENDING') if not control['defects'] else 'BLOCKED'
                        value = {'tables': {}, 'controls': control}
                    else:
                        generator = ClinicalGenerator(merge({p: outputs[p] for p in parents}), cfg, policy, 'clinical-' + fingerprint[:24])
                        if stage == 'journeys': tables = generator.journeys()
                        elif stage == 'appointments': tables = generator.appointments()
                        else: tables = generator.care(facilities[site_codes[stage]])
                        for table, rows in tables.items():
                            primary = next(t['primary_key'][0] for t in schema['tables'] if t['name'] == table)
                            rows.sort(key=lambda r: r[primary])
                        value = {'tables': tables, 'controls': {'generation_id': generator.run_id}}
                    check_budget(merge({**outputs, stage: value}), policy['business_cap'], schema)
                    hashes[stage] = store.publish(stage, local[stage], fingerprint, value, fail=stage == fail_stage, crash=stage == crash_stage)
                    manifest['executed'].append(stage)
                outputs[stage] = value
                logging.getLogger(__name__).info('Clinical stage %s: %s', stage, 'reused' if stage in manifest['reused'] else 'executed')
                del cached
            tables, control = merge(outputs), outputs['validation']['controls']
            total = check_budget(tables, policy['business_cap'], schema)
            files = {}
            canonical_dir = output / 'canonical'
            canonical_dir.mkdir(exist_ok=True)
            for table, rows in tables.items():
                primary = next(t['primary_key'][0] for t in schema['tables'] if t['name'] == table)
                rows = sorted(rows, key=lambda r: r[primary])
                file = canonical_dir / (table.replace('_', '-') + '.jsonl')
                temp = file.with_suffix('.tmp')
                sha, count = hashlib.sha256(), 0
                with temp.open('wb') as stream:
                    for r in rows:
                        line = (canonical(r) + '\n').encode()
                        stream.write(line); sha.update(line); count += len(line)
                temp.replace(file)
                files[table] = {'file': file.relative_to(output).as_posix(), 'sha256': sha.hexdigest(), 'bytes': count, 'rows': len(rows)}
            body, selection = render_journeys(tables, cfg)
            (output / 'journey-review-sample.md').write_text(body, encoding='utf-8', newline='\n')
            atomic_json(output / 'validation-report.json', control)
            manifest.update(status=control['gate_status'], business_sha256=digest({t: files[t]['sha256'] for t in sorted(files)}),
                            canonical_files=files, rows_by_table={t: len(r) for t, r in tables.items()}, business_rows=total,
                            generated_business_tables=len(tables), release_business_tables=25, remaining_planned_rows=1958210-total,
                            checkpoint_mirror_rows=total, review_mirror_rows=selection['mirror_rows'], review_mirror_bytes=selection['mirror_bytes'],
                            physical_serialized_rows=2*total+selection['mirror_rows'], stage_checksums=hashes, next_phase='Demand, patient flow and beds - not started')
            if manifest['status'] == 'CLINICAL_HISTORIES_PASSED':
                atomic_json(output / 'candidate-ready.json', {k: manifest[k] for k in ('status', 'business_sha256', 'full_dataset_accepted', 'solution_status', 'trajectory_status')})
        except Exception as exc:
            manifest.update(status='FAILED', error=str(exc))
            raise
        finally:
            manifest['finished_at'] = datetime.now(timezone.utc).isoformat()
            if attempt is not None:
                with store.db: store.db.execute('UPDATE attempts SET status=?,finished=?,manifest=? WHERE id=?', (manifest['status'], manifest['finished_at'], canonical(manifest), attempt))
            atomic_json(output / 'manifest.json', manifest)
            store.close()
        return manifest
