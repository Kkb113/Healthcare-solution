"""Independent validation of changed-candidate native source deliveries."""
from pathlib import Path
import json
from collections import Counter
from .integrated_generation import ROOT, read, sha_file
from .source_export import footprint
from .source_reader import DeliveryReplay,safe_path


def inspect(candidate, output, replay_path):
    """Read every native scalar, independently reconstruct and duplicate replay."""
    candidate = Path(candidate); output = Path(output); m = read(output / 'manifest.json'); accepted = read(candidate / 'manifest.json')
    layouts = read(output / 'source-dictionary.json'); controls = {}; duplicates = 0
    from .integrated_exports import source_dependencies
    if m['locks'] != source_dependencies():
        raise ValueError('integrated native producer/configuration locks differ')
    if m['status'] not in ('EXPORTED_NOT_YET_VALIDATED','INTEGRATED_SOURCE_SIMULATION_PASSED') or m['business_sha256'] != accepted['business_sha256'] or m['source_dictionary_sha256'] != sha_file(output / 'source-dictionary.json'):
        raise ValueError('integrated source/candidate/dictionary anchors differ')
    declared = {f['path'] for f in m['files']} | {f['dictionary_path'] for f in m['files']} | {f['path'] for f in m['reports']}
    actual = {p.relative_to(output).as_posix() for p in (output / 'valid').rglob('*') if p.is_file()}
    if declared != actual or len({f['file_id'] for f in m['files']}) != len(m['files']):
        raise ValueError('integrated source inventory differs')
    prior_source = read(ROOT/'output/source-delivery/manifest.json')
    if m['source_dictionary_sha256'] != prior_source['source_dictionary_sha256']:
        raise ValueError('unreviewed native source scalar schema change')
    primary_counts = Counter()
    for f in m['files']:
        if f['role']=='PRIMARY':primary_counts[f['table']]+=f['expected_rows']
    if dict(primary_counts) != {t:f['rows'] for t,f in accepted['canonical_files'].items()}:
        raise ValueError('primary source scopes duplicate or omit canonical rows')
    footprint_controls = {'canonical_business_rows':accepted['business_rows'],'business_tables':25,
        'primary_source_rows':sum(primary_counts.values()),'scheduled_mirror_rows':sum(f['expected_rows'] for f in m['files'] if f['role']!='PRIMARY'),
        'dictionary_mapping_rows':sum(f['dictionary_rows'] for f in m['files']),
        'derived_report_rows':sum(f['expected_rows'] for f in m['reports']),
        'derived_scalar_fact_mirrors':sum(f['mirrored_scalar_facts'] for f in m['reports']),
        'source_payload_bytes':sum(f['bytes']+f['dictionary']['bytes'] for f in m['files'])+sum(f['bytes'] for f in m['reports'])}
    if any(m[k]!=v for k,v in footprint_controls.items()):
        raise ValueError('native physical/source fact accounting differs')
    replay = DeliveryReplay(replay_path)
    try:
        for f in sorted(m['files'], key=lambda f: (f['available_at'] or '', f['file_id'])):
            replay.ingest(output, f, layouts[f['table']])
        replay.certify([f['file_id'] for f in m['files']])
        for table, meta in accepted['canonical_files'].items():
            got = replay.table_hash(table)
            if got != (meta['sha256'], meta['rows']):
                raise ValueError('integrated native roundtrip differs: ' + table)
            controls[table] = {'rows': got[1], 'sha256': got[0], 'differences': 0}
        for f in reversed(m['files']):
            if replay.ingest(output, f, layouts[f['table']]) != 'DUPLICATE':
                raise ValueError('integrated duplicate delivery changed state')
            duplicates += 1
        for table, meta in accepted['canonical_files'].items():
            if replay.table_hash(table) != (meta['sha256'], meta['rows']):
                raise ValueError('duplicate integrated facts changed')
        historical = []
        for known in ('2023-01-02T06:00:00Z','2024-02-01T06:00:00Z','2025-12-31T06:00:00Z'):
            count = 0
            for table in layouts:
                for row in replay.rows(table,known):
                    if row['export_available_at'] > known or row.get('known_from',row['recorded_at']) > known or row.get('known_to') is not None:
                        raise ValueError('native historical snapshot leaked source knowledge/retrospective closure')
                    count += 1
            historical.append({'known_at':known,'delivered_versions_checked':count,'future_facts':0})
        from .source_report_validation import validate_reports
        reports_checked = validate_reports(output, m['reports'], replay.rows('finance_monthly'), replay.rows('cost_center'), replay.rows('catalog_item'))
        families = {f['family'] for f in m['files'] if f['family']} | set(reports_checked)
        if families != set(read(ROOT/'contracts/source-delivery-policy.json')['axiom_inventory']['families']):
            raise ValueError('native Axiom archetype coverage differs')
        from .source_faults import exercise_faults
        challenge = read(output / 'challenge-manifest.json')
        if challenge['accepted_business_sha256']!=accepted['business_sha256'] or challenge['challenge_generator_sha256']!=sha_file(ROOT/'src/healthcare_synthetic/source_faults.py'):
            raise ValueError('native challenge business/implementation anchors differ')
        import csv
        declared_challenges = set(challenge['observed_artifacts'])
        if declared_challenges != {p.relative_to(output).as_posix() for p in (output/'challenges').rglob('*') if p.is_file()}:
            raise ValueError('integrated challenge inventory differs')
        for relative, metrics in challenge['observed_artifacts'].items():
            if footprint(safe_path(output,relative)) != metrics:
                raise ValueError('integrated challenge bytes differ')
        copies = 0; copies_by_table = Counter()
        for f in challenge['files']:
            path = safe_path(output,f['path'])
            with path.open(encoding='utf-8',newline='') as stream:
                count = sum(1 for _ in stream) if path.suffix=='.jsonl' else max(0,sum(1 for _ in csv.reader(stream))-1)
                copies += count; copies_by_table[f['table']] += count
        if copies != challenge['published_challenge_record_copies'] or copies > 64 or copies+accepted['business_rows']>2000000:
            raise ValueError('integrated physical challenge/record cap differs')
        if dict(copies_by_table)!=challenge['published_copies_by_table']:
            raise ValueError('challenge physical table accounting differs')
        faults = exercise_faults(output, challenge, output / 'fault-replay')
        from .source_reader import project_bed_events
        if len(project_bed_events(replay.rows('bed_event'), '2026-01-01T05:59:59Z', '2026-01-10T23:59:59Z')) != 72:
            raise ValueError('integrated bed projection incomplete')
    finally:
        replay.close()
    # These two immutable master histories were deliberately retained. This
    # permits the independently implemented calendar oracle to retain its fixed
    # master anchor while validating every new finance header and delivery.
    old = read(ROOT/'output/financial-history/manifest.json')
    if accepted['canonical_files']['cost_center']['sha256'] != old['canonical_files']['cost_center']['sha256']:
        raise ValueError('calendar cost-center anchor changed; migrate calendar oracle')
    def worker_visibility(root,manifest):
        with (root/manifest['canonical_files']['worker_assignment']['file']).open(encoding='utf-8') as stream:
            return sorted((r['worker_assignment_id'],r['export_available_at']) for r in map(json.loads,stream))
    if worker_visibility(candidate,accepted) != worker_visibility(ROOT/'output/financial-history',old):
        raise ValueError('calendar worker version/delivery membership anchor changed')
    from inspect_source_calendar import inspect_calendar
    calendar = inspect_calendar(output,m)
    return {'status': 'PASS', 'canonical_roundtrip': controls, 'source_files': len(m['files']), 'duplicate_deliveries_checked': duplicates,
            'reports': reports_checked, 'faults': faults, 'roundtrip_rows': sum(f['rows'] for f in controls.values()),
            'delivery_calendar':calendar,'historical_native_snapshots':historical,'physical_source_accounting':footprint_controls,
            'axiom_archetypes':sorted(families),'challenge_copies':copies,'unexplained_differences': 0}
