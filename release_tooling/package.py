"""Content-addressed release envelopes and independent transport verification."""
from __future__ import annotations

import csv
import json
import os
import re
import shutil
from collections import Counter
from pathlib import Path

from .common import digest, inside, inventory, read, safe_relative, save, sha_file
from .profiles import V1_0, profile

MANIFEST = 'payload-manifest.json'
DESCRIPTOR = 'release-descriptor.json'
PROFILE = 'HEALTHCARE_SYNTHETIC_RELEASE'
# Version 1.0 anchors, retained for callers that predate per-release profiles.
BUSINESS_SHA = V1_0['business_sha256']
SOURCE_SHA = V1_0['source_sha256']


def release_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'healthcare-synthetic-v[1-9][0-9]*\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)', value):
        raise ValueError('release ID must use healthcare-synthetic-vMAJOR.MINOR.PATCH')
    return value


def copy_tree(source, target):
    if Path(target).exists():
        raise ValueError('artifact destination already exists')
    if any(p.is_symlink() for p in Path(source).rglob('*')):
        raise ValueError('symbolic link in release input')
    shutil.copytree(source, target)


def seal(directory, identifier, metadata):
    """Seal exactly the current files; verification requires an external hash."""
    directory = Path(directory)
    identifier = release_id(identifier)
    if (directory / MANIFEST).exists() or (directory / DESCRIPTOR).exists():
        raise ValueError('release is already sealed')
    files = inventory(directory)
    if not files:
        raise ValueError('cannot seal an empty release')
    save(directory / MANIFEST, {'release_id': identifier, 'files': files})
    descriptor = {**metadata, 'release_id': identifier, 'payload_manifest_sha256': sha_file(directory / MANIFEST),
                  'payload_files': len(files), 'payload_bytes': sum(f['bytes'] for f in files.values())}
    save(directory / DESCRIPTOR, descriptor)
    return sha_file(directory / DESCRIPTOR)


def verify_seal(directory, expected_descriptor_sha256):
    directory = Path(directory).resolve()
    if not isinstance(expected_descriptor_sha256, str) or not re.fullmatch('[a-f0-9]{64}', expected_descriptor_sha256):
        raise ValueError('a trusted external descriptor SHA256 is required')
    if sha_file(directory / DESCRIPTOR) != expected_descriptor_sha256:
        raise ValueError('release descriptor differs from trusted external SHA256')
    descriptor = read(directory / DESCRIPTOR)
    release_id(descriptor['release_id'])
    if sha_file(directory / MANIFEST) != descriptor['payload_manifest_sha256']:
        raise ValueError('payload manifest checksum differs')
    manifest = read(directory / MANIFEST)
    if manifest['release_id'] != descriptor['release_id'] or not manifest['files']:
        raise ValueError('payload identity/empty inventory differs')
    for name in manifest['files']:
        safe_relative(name)
        if name in (MANIFEST, DESCRIPTOR):
            raise ValueError('recursive manifest declaration')
        inside(directory, name)
    observed = inventory(directory)
    del observed[MANIFEST]
    del observed[DESCRIPTOR]
    if observed != manifest['files']:
        raise ValueError('actual release inventory, bytes or checksums differ')
    if descriptor['payload_files'] != len(observed) or descriptor['payload_bytes'] != sum(v['bytes'] for v in observed.values()):
        raise ValueError('physical payload totals differ')
    return descriptor


def check_healthcare_metadata(descriptor, certificate, canonical, native, schema, challenges):
    """No reviewer or caller can relax the frozen final business envelope of this release version."""
    p = profile(descriptor.get('release_id'))
    business, source = p['business_sha256'], p['source_sha256']
    if descriptor['profile'] != PROFILE or descriptor['technical_status'] != 'PASSED':
        raise ValueError('uncertified release profile')
    if certificate['status'] != 'PASSED' or certificate['unresolved_p0_p1'] or certificate['unexplained_differences']:
        raise ValueError('technical certification failed')
    if certificate['domain_checks'] != p['domain_checks'] or certificate['source_files'] != p['source_files'] or certificate['fault_outcomes'] != p['fault_outcomes']:
        raise ValueError('mandatory full-population/native controls incomplete')
    if certificate['future_fact_failures'] or certificate['unknown_outcomes_preserved'] is not True:
        raise ValueError('point-in-time/censoring controls failed')
    if certificate['clean_rebuild_passed'] is not True or certificate['phase8_unchanged_evidence_verified'] is not True:
        raise ValueError('clean lineage or earlier evidence not established')
    if canonical['business_sha256'] != business or descriptor['canonical_business_sha256'] != business:
        raise ValueError('normalized release differs from the accepted Phase 8 candidate')
    if descriptor['source_package_sha256'] != source or certificate['source_package_sha256'] != source:
        raise ValueError('native release differs from the accepted Phase 8 package')
    names = {t['name'] for t in schema['tables']}
    if len(names) != 25 or names != set(canonical['canonical_files']) or canonical['business_tables'] != 25:
        raise ValueError('required final business tables missing or duplicated')
    rows = sum(v['rows'] for v in canonical['canonical_files'].values())
    copies = challenges['published_challenge_record_copies']
    if rows != p['business_rows'] or canonical['business_rows'] != rows or not 1000000 <= rows + copies <= 2000000 or copies != p['challenge_copies']:
        raise ValueError('final record cap/count differs')
    if descriptor['cap_counted_release_rows'] != rows + copies or descriptor['business_tables'] != 25:
        raise ValueError('descriptor business totals differ')
    if native['business_sha256'] != business or native['canonical_business_rows'] != rows:
        raise ValueError('source/canonical business anchor differs')
    primary = Counter()
    for f in native['files']:
        if f['role'] == 'PRIMARY':
            primary[f['table']] += f['expected_rows']
    if dict(primary) != {t: v['rows'] for t, v in canonical['canonical_files'].items()} or len(native['files']) != p['source_files'] or len(native['reports']) != p['reports']:
        raise ValueError('native source scopes/counts differ')
    if digest({t: m['sha256'] for t, m in sorted(canonical['canonical_files'].items())}) != business:
        raise ValueError('canonical file-map digest differs')
    return rows, copies


def verify_healthcare_release(directory, expected_descriptor_sha256):
    directory = Path(directory).resolve()
    d = verify_seal(directory, expected_descriptor_sha256)
    cert = read(directory / 'evidence/certification.json')
    if sha_file(directory / 'evidence/certification.json') != d['certification_sha256']:
        raise ValueError('certification checksum differs')
    c = read(directory / 'dataset/manifest.json')
    native = read(directory / 'native/manifest.json')
    schema = read(directory / 'schema/tables.json')
    challenges = read(directory / 'native/challenge-manifest.json')
    rows, copies = check_healthcare_metadata(d, cert, c, native, schema, challenges)
    canonical_dir = directory / 'dataset'
    if {p.relative_to(canonical_dir).as_posix() for p in (canonical_dir / 'canonical').iterdir()} != {v['file'] for v in c['canonical_files'].values()}:
        raise ValueError('canonical table inventory differs')
    for table, meta in c['canonical_files'].items():
        p = inside(canonical_dir, meta['file'])
        if sha_file(p) != meta['sha256'] or p.stat().st_size != meta['bytes']:
            raise ValueError('canonical metadata differs: ' + table)
        with p.open('rb') as stream:
            if sum(1 for _ in stream) != meta['rows']:
                raise ValueError('canonical physical row count differs: ' + table)
    actual_copies = 0
    for f in challenges['files']:
        p = inside(directory / 'native', f['path'])
        with p.open(encoding='utf-8', newline='') as stream:
            actual_copies += sum(1 for _ in stream) if p.suffix == '.jsonl' else max(0, sum(1 for _ in csv.reader(stream)) - 1)
    if actual_copies != copies:
        raise ValueError('published challenge physical count differs')
    declared = {f['path'] for f in native['files']} | {f['dictionary_path'] for f in native['files']} | {f['path'] for f in native['reports']}
    actual = {p.relative_to(directory / 'native').as_posix() for p in (directory / 'native/valid').rglob('*') if p.is_file()}
    if declared != actual:
        raise ValueError('native delivery inventory differs')
    for f in native['files'] + native['reports']:
        p = inside(directory / 'native', f['path'])
        if sha_file(p) != f['sha256'] or p.stat().st_size != f['bytes']:
            raise ValueError('native file controls differ')
        if 'dictionary_path' in f:
            p = inside(directory / 'native', f['dictionary_path'])
            if sha_file(p) != f['dictionary']['sha256'] or p.stat().st_size != f['dictionary']['bytes']:
                raise ValueError('native dictionary controls differ')
    return {'status': 'PASSED', 'release_id': d['release_id'], 'descriptor_sha256': expected_descriptor_sha256,
            'business_tables': 25, 'business_rows': rows, 'challenge_copies': copies,
            'cap_counted_release_rows': rows + copies, 'payload_files': d['payload_files'],
            'canonical_business_sha256': profile(d['release_id'])['business_sha256'], 'source_package_sha256': profile(d['release_id'])['source_sha256']}


def publish(staging, destination, descriptor_sha256):
    staging = Path(staging).resolve()
    destination = Path(destination).resolve()
    if staging == destination or staging in destination.parents or destination in staging.parents:
        raise ValueError('release paths overlap')
    verify_healthcare_release(staging, descriptor_sha256)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock = destination.parent / (destination.name + '.publish-lock')
    handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        if destination.exists():
            raise ValueError('version already exists; immutable releases cannot be overwritten')
        if destination.name != read(staging / DESCRIPTOR)['release_id']:
            raise ValueError('publication directory identity differs')
        os.rename(staging, destination)
    finally:
        os.close(handle)
        lock.unlink()
    return {'status': 'PUBLISHED_PENDING_BUSINESS_ACCEPTANCE', 'release_id': destination.name,
            'descriptor_sha256': descriptor_sha256, 'solution_status': 'BLOCKED_FOR_SOLUTION',
            'storage_guarantee': 'Create-once version directory plus externally anchored hashes; ordinary local storage, not WORM/security immutability.'}
