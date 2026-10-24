"""Persisted-source acceptance, separate from export generation and business truth."""
from __future__ import annotations

import json
import csv
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path

from .source_layouts import ROOT, read
from .source_reader import DeliveryReplay, check_file, encode, safe_path, sha
from .source_report_validation import validate_reports


def inspect_sources(output=ROOT / 'output/source-delivery', *, verify_replay=True):
    output = Path(output).resolve(); raw = (output / 'manifest.json').read_bytes(); m = json.loads(raw)
    parent = ROOT / 'output/financial-history'; accepted = read(parent / 'manifest.json')
    policy = read(ROOT / 'contracts/source-delivery-policy.json'); layouts = read(output / 'source-dictionary.json')
    import hashlib
    if hashlib.sha256((output / 'source-dictionary.json').read_bytes()).hexdigest() != m['source_dictionary_sha256']:
        raise ValueError('published source dictionary checksum differs')
    if m['status'] not in ('EXPORTED_NOT_YET_VALIDATED', 'SOURCE_SIMULATION_PASSED') or m['business_sha256'] != policy['accepted_business_sha256'] or accepted['business_sha256'] != m['business_sha256']:
        raise ValueError('source/accepted truth anchors differ')
    # Recompute accepted file bytes independently; do not trust the exporter checkpoint.
    if sha({k: v['sha256'] for k, v in sorted(accepted['canonical_files'].items())}) != accepted['business_sha256']:
        raise ValueError('accepted file-map digest differs')
    for f in accepted['canonical_files'].values():
        check_file(safe_path(parent, f['file']), f)
    for relative, expected in m['locks'].items():
        import hashlib
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError('export source/input lock differs: ' + relative)
    if set(layouts) != set(accepted['canonical_files']) or len(layouts) != 25:
        raise ValueError('source dictionary table inventory differs')
    # Compare published declarations to the frozen scalar schema independently.
    frozen = read(ROOT / 'contracts/phase0/schema.json')
    for table in frozen['tables']:
        layout = layouts[table['name']]
        if [(f['canonical'], f['type'], f['nullable']) for f in layout['fields']] != [(c['name'], c['type'], c['nullable']) for c in table['columns']] or layout['primary_key'] != table['primary_key'][0]:
            raise ValueError('source dictionary dropped or altered canonical columns')
    declared = {m['path'] for m in m['files']} | {m['dictionary_path'] for m in m['files']} | {r['path'] for r in m['reports']}
    actual = {p.relative_to(output).as_posix() for p in (output / 'valid').rglob('*') if p.is_file()}
    if actual != declared:
        raise ValueError('source file inventory differs; missing or undeclared data')
    if len({f['file_id'] for f in m['files']}) != len(m['files']):
        raise ValueError('duplicate source manifest identity')
    primary_counts = Counter(); families = Counter(); sequences = Counter(); replaced = 0
    controls = {}; required = []
    with tempfile.TemporaryDirectory(prefix='source-roundtrip-', dir=ROOT / 'output') as temp:
        replay = DeliveryReplay(str(Path(temp) / 'roundtrip.sqlite3'))
        try:
            for f in sorted(m['files'], key=lambda f: (f['available_at'] or '', f['file_id'])):
                if f['role'] == 'PRIMARY':
                    replay.ingest(output, f, layouts[f['table']]); required.append(f['file_id'])
                    primary_counts[f['table']] += f['expected_rows']
                else:
                    # Scheduled mirror loads must not add versions or economic facts.
                    # Source-known history may arrive before its next daily delta; it
                    # is therefore checked against canonical truth after all deliveries.
                    replay.ingest(output, f, layouts[f['table']]); required.append(f['file_id'])
                if f['family']:
                    families[f['family']] += 1
                sequences[(f['table'], f['mode'])] += 1
                replaced += bool(f['replacement_of'])
            replay.certify(required)
            for table, expected in accepted['canonical_files'].items():
                got, count = replay.table_hash(table)
                if got != expected['sha256'] or count != expected['rows'] or primary_counts[table] != expected['rows']:
                    raise ValueError('canonical/source exact scalar roundtrip differs: ' + table)
                controls[table] = {'status': 'PASS', 'rows': count, 'sha256': got, 'unexplained_differences': 0}
            from .source_reader import project_bed_events
            bed_states = project_bed_events(replay.rows('bed_event'), '2026-01-01T05:59:59Z', '2026-01-10T23:59:59Z')
            if len(bed_states) != 72:
                raise ValueError('bed replay failed to resolve all 72 modeled beds')
            finance = replay.rows('finance_monthly'); centers = replay.rows('cost_center'); catalog = replay.rows('catalog_item')
            report_checks = validate_reports(output, m['reports'], finance, centers, catalog)
            # Every actual replacement selects only one complete scope, retaining earlier history.
            for f in m['files']:
                if f['replacement_of']:
                    prior = next(p for p in m['files'] if p['file_id'] == f['replacement_of'])
                    earlier = replay.rows(f['table'], prior['available_at'], f['scope'])
                    current = replay.rows(f['table'], f['available_at'], f['scope'])
                    if {r['vintage_id'] for r in earlier} != set(prior['vintages']) or {r['vintage_id'] for r in current} != set(f['vintages']) or len(current) != f['expected_rows']:
                        raise ValueError('Axiom replacement selected multiple/incorrect vintages')
            # Duplicate all primary files for a different delivery order; no fact changes.
            duplicate_checks = 0
            if verify_replay:
                for f in reversed(m['files']):
                    if replay.ingest(output, f, layouts[f['table']]) != 'DUPLICATE':
                        raise ValueError('repeated source/snapshot delivery changed state')
                    duplicate_checks += 1
                for table, expected in accepted['canonical_files'].items():
                    if replay.table_hash(table) != (expected['sha256'], expected['rows']):
                        raise ValueError('duplicate/reverse delivery changed canonical facts')
        finally:
            replay.close()
    all_families = set(families) | set(report_checks)
    if all_families != set(policy['axiom_inventory']['families']):
        raise ValueError('Axiom archetype coverage incomplete')
    primary_rows = sum(primary_counts.values()); scheduled = sum(f['expected_rows'] for f in m['files'] if f['role'] != 'PRIMARY')
    if primary_rows != policy['canonical_business_rows'] or m['canonical_business_rows'] != primary_rows or m['business_tables'] != 25:
        raise ValueError('source/business record allowance differs')
    expected_counts = {'primary_source_rows': primary_rows, 'scheduled_mirror_rows': scheduled,
        'dictionary_mapping_rows': sum(f['dictionary_rows'] for f in m['files']),
        'derived_report_rows': sum(r['expected_rows'] for r in m['reports']),
        'derived_scalar_fact_mirrors': sum(r['mirrored_scalar_facts'] for r in m['reports']),
        'source_payload_bytes': sum(f['bytes'] + f['dictionary']['bytes'] for f in m['files']) + sum(r['bytes'] for r in m['reports'])}
    if any(m[k] != v for k, v in expected_counts.items()):
        raise ValueError('physical source artifact accounting differs')
    package = read(output / 'challenge-manifest.json')
    if package['accepted_business_sha256'] != accepted['business_sha256'] or package['challenge_generator_sha256'] != hashlib.sha256((ROOT / 'src/healthcare_synthetic/source_faults.py').read_bytes()).hexdigest():
        raise ValueError('challenge source/input fingerprint differs')
    declared_challenges = set(package['observed_artifacts'])
    actual_challenges = {p.relative_to(output).as_posix() for p in (output / 'challenges').rglob('*') if p.is_file()}
    if declared_challenges != actual_challenges:
        raise ValueError('challenge physical file inventory differs')
    for relative, metrics in package['observed_artifacts'].items():
        check_file(safe_path(output, relative), metrics)
    copies = 0; copies_by_table = Counter()
    for f in package['files']:
        path = safe_path(output, f['path'])
        with path.open(encoding='utf-8', newline='') as stream:
            count = sum(1 for _ in stream) if path.suffix == '.jsonl' else max(0, sum(1 for _ in csv.reader(stream)) - 1)
        copies += count; copies_by_table[f['table']] += count
    if copies != package['published_challenge_record_copies'] or dict(copies_by_table) != package['published_copies_by_table']:
        raise ValueError('challenge record copy accounting differs')
    if package['published_challenge_record_copies'] > policy['challenge_allowance'] or primary_rows + package['published_challenge_record_copies'] > 2_000_000:
        raise ValueError('published challenge allowance exceeded')
    if (output / 'manifest.json').read_bytes() != raw:
        raise ValueError('source candidate changed during inspection')
    return {'status': 'PASS', 'canonical_roundtrip': controls, 'source_files': len(m['files']),
            'roundtrip_rows': primary_rows, 'duplicate_deliveries_checked': duplicate_checks,
            'resolved_beds_at_cutoff': len(bed_states),
            'replacement_scopes_checked': replaced, 'report_controls': report_checks,
            'axiom_families': sorted(all_families), 'physical_artifacts': expected_counts,
            'canonical_business_rows': primary_rows, 'published_challenge_record_copies': package['published_challenge_record_copies'],
            'cap_counted_release_rows': primary_rows + package['published_challenge_record_copies'],
            'unexplained_differences': 0, 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION'}
