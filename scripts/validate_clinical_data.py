"""Read-only verification of persisted clinical files and independent clinical rules."""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import sqlite3
import sys
from importlib import metadata, resources
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from healthcare_synthetic.clinical_validation import ClinicalValidator
from healthcare_synthetic.clinical_review import render_journeys, review_gate

def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def encode(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def files_at(output, manifest):
    tables = {}
    actual = {p.relative_to(output).as_posix() for p in (output / 'canonical').iterdir() if p.is_file()}
    if actual != {v['file'] for v in manifest['canonical_files'].values()}: raise ValueError('canonical file inventory differs')
    for name, meta in manifest['canonical_files'].items():
        path = (output / meta['file']).resolve()
        if output not in path.parents: raise ValueError('canonical file path escaped candidate')
        sha, size, rows = hashlib.sha256(), 0, []
        with path.open('rb') as stream:
            for line in stream:
                sha.update(line); size += len(line)
                row = json.loads(line)
                if encode(row) + b'\n' != line: raise ValueError('noncanonical serialized row: ' + name)
                rows.append(row)
        if sha.hexdigest() != meta['sha256'] or size != meta['bytes'] or len(rows) != meta['rows']: raise ValueError('canonical checksum/size/count mismatch: ' + name)
        tables[name] = rows
    if hashlib.sha256(encode({t: manifest['canonical_files'][t]['sha256'] for t in sorted(tables)})).hexdigest() != manifest['business_sha256']:
        raise ValueError('canonical business hash differs')
    return tables

def inspect_clinical(output, config_path=ROOT / 'config/clinical-history-generation.json', review_path=ROOT / 'reviews/clinical-journey-review.json'):
    output = Path(output).resolve()
    raw_manifest = (output / 'manifest.json').read_bytes()
    manifest, cfg = json.loads(raw_manifest), read(config_path)
    if manifest['profile'] != 'LONGITUDINAL_CLINICAL' or manifest['status'] not in ('CLINICAL_HISTORIES_PASSED', 'REVIEW_PENDING', 'BLOCKED'): raise ValueError('clinical candidate incomplete, failed or wrong profile')
    if hashlib.sha256(encode(cfg)).hexdigest() != manifest['locks']['configuration_sha256']: raise ValueError('clinical config lock mismatch')
    runtime = {'python': platform.python_version(), 'implementation': platform.python_implementation(), 'tzdata': metadata.version('tzdata'),
               'chicago_sha256': hashlib.sha256(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()).hexdigest()}
    if runtime != manifest['locks']['runtime']: raise ValueError('clinical runtime differs')
    for relative, expected in manifest['locks']['files'].items():
        path = (ROOT / relative).resolve()
        if ROOT not in path.parents or hashlib.sha256(path.read_bytes()).hexdigest() != expected: raise ValueError('clinical input lock mismatch: ' + relative)
    accepted = read(ROOT / 'evidence/master-data/acceptance-gate.json')
    parent_path = (ROOT / cfg['master_candidate']).resolve()
    if ROOT not in parent_path.parents: raise ValueError('master candidate outside workspace')
    parent_manifest = read(parent_path / 'manifest.json')
    if accepted['status'] != 'PASSED' or accepted['business_sha256'] != cfg['master_business_sha256'] or parent_manifest['business_sha256'] != accepted['business_sha256']: raise ValueError('accepted master anchor differs')
    master = files_at(parent_path, parent_manifest)
    tables = files_at(output, manifest)
    schema = read(ROOT / 'contracts/phase0/schema.json')
    policy = read(ROOT / 'contracts/clinical-history-policy.json')
    # Verify transactional payloads and compare their row sets with the independently read files.
    connection = sqlite3.connect('file:' + (output / 'checkpoints.sqlite3').as_posix() + '?mode=ro', uri=True)
    seen = set()
    table_hashes = {t: {} for t in tables}
    primary = {t['name']: t['primary_key'][0] for t in schema['tables']}
    try:
        for stage, payload, checksum in connection.execute('SELECT name,payload,checksum FROM stages'):
            seen.add(stage)
            if hashlib.sha256(payload.encode()).hexdigest() != checksum or manifest['stage_checksums'].get(stage) != checksum: raise ValueError('checkpoint checksum mismatch: ' + stage)
            for name, rows in json.loads(payload)['tables'].items():
                for row in rows:
                    key = row[primary[name]]
                    if key in table_hashes[name]: raise ValueError('duplicate checkpoint business row')
                    table_hashes[name][key] = hashlib.sha256(encode(row)).digest()
        if seen != set(manifest['stage_checksums']): raise ValueError('checkpoint inventory differs')
        for name, rows in tables.items():
            if len(rows) != len(table_hashes[name]): raise ValueError('checkpoint/canonical row count differs')
            for row in rows:
                if table_hashes[name].get(row[primary[name]]) != hashlib.sha256(encode(row)).digest(): raise ValueError('checkpoint/canonical content differs')
    finally:
        connection.close()
    del table_hashes
    checked = ClinicalValidator(tables, schema, cfg, policy, master).run()
    body, selection = render_journeys(tables, cfg)
    if (output / 'journey-review-sample.md').read_bytes() != body.encode(): raise ValueError('journey review content differs')
    checked['review_selection'] = selection
    checked['review'] = review_gate(selection, read(review_path) if Path(review_path).exists() else None)
    checked['gate_status'] = ('CLINICAL_HISTORIES_PASSED' if checked['review']['status'] == 'PASS' else 'REVIEW_PENDING') if not checked['defects'] else 'BLOCKED'
    if (output / 'manifest.json').read_bytes() != raw_manifest: raise ValueError('candidate changed during inspection')
    if manifest['rows_by_table'] != {t: len(rows) for t, rows in tables.items()} or manifest['business_rows'] != sum(map(len, tables.values())): raise ValueError('manifest canonical counts differ')
    checked['artifact_integrity'], checked['business_sha256'] = 'PASS', manifest['business_sha256']
    return checked

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT / 'output/clinical-histories')
    p.add_argument('--config', type=Path, default=ROOT / 'config/clinical-history-generation.json')
    p.add_argument('--review', type=Path, default=ROOT / 'reviews/clinical-journey-review.json')
    p.add_argument('--report', type=Path)
    a = p.parse_args()
    try: result = inspect_clinical(a.output, a.config, a.review)
    except Exception as exc: result = {'gate_status': 'BLOCKED', 'error': str(exc), 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION'}
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: result[k] for k in ('gate_status', 'artifact_integrity', 'error') if k in result}))
    return 0 if result['gate_status'] == 'CLINICAL_HISTORIES_PASSED' else 2

if __name__ == '__main__': sys.exit(main())
