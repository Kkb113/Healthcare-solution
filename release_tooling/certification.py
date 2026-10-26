"""Validate the exact payload to be published, using the frozen full validators."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from .common import ROOT, digest, ignored_path, inventory, read, save, sha_file
from .package import PROFILE, copy_tree, release_id, seal, verify_healthcare_release
from .profiles import CURRENT_RELEASE, lineage, profile
from .rebuild import environment, run_script, snapshot
from .verification import tool_bindings


def check_clean_build(clean, release):
    report = read(clean / 'clean-rebuild.json')
    if report['status'] != 'PASS' or report['generated_inputs_imported'] != 0 or report['checkpoint_inputs_imported'] != 0 or not report['controller_unchanged']:
        raise ValueError('a complete clean lineage rebuild is required')
    if [(s['name'], s['producer_commit'], s['business_sha256']) for s in report['stages']] != [(n, c, h) for n, c, _, h in lineage(release, report['producer_commit'])]:
        raise ValueError('clean lineage revisions or business anchors differ')
    for relative, expected in report['controller_bindings'].items():
        if sha_file(ROOT / relative) != expected:
            raise ValueError('clean rebuild controller no longer matches its evidence')
    for stage in report['stages']:
        archive = clean / 'archives' / (stage['name'] + '.tar')
        if sha_file(archive) != stage['archive_sha256']:
            raise ValueError('clean source archive differs')
        expected_tar = subprocess.run(['git', 'archive', '--format=tar', stage['producer_commit']],
                                      cwd=ROOT, capture_output=True, check=True).stdout
        if hashlib.sha256(expected_tar).hexdigest() != stage['archive_sha256']:
            raise ValueError('source archive does not match pinned Git commit')
        frozen = clean / 'sources' / stage['name']
        files = {}
        with tarfile.open(archive) as source:
            for member in source.getmembers():
                if member.isfile():
                    expected = hashlib.sha256(source.extractfile(member).read()).hexdigest()
                    if sha_file(frozen / member.name) != expected:
                        raise ValueError('frozen producer file changed: ' + member.name)
                    files[member.name] = {'sha256': expected, 'bytes': member.size}
        if digest(files) != stage['source_tree_sha256'] or stage['reused']:
            raise ValueError('source tree or cold-checkpoint proof differs')
        snapshot(frozen / 'output' / stage['name'], stage['business_sha256'])
    frozen = clean / 'sources/integrated-history'
    earlier = read(frozen / 'evidence/integrated-history/validation-report.json')
    mapped = {**earlier['verification_source_sha256'], **earlier['verification_input_sha256']}
    for relative, expected in mapped.items():
        if sha_file(frozen / relative) != expected or sha_file(ROOT / relative) != expected:
            raise ValueError('unchanged Phase 8 evidence/source input differs: ' + relative)
    runtime = read(clean / 'runtime-evidence.json')
    if runtime['system_site_packages'] or not runtime['isolated'] or runtime['packages'] != read(ROOT / 'release_tooling/runtime-lock.json')['packages']:
        raise ValueError('clean runtime isolation differs')
    return report, frozen, earlier


def isolated_call(python, frozen, code, log):
    setup = f'import sys; sys.path[:0]={[str(frozen / "src"), str(frozen / "scripts")]!r}; '
    with Path(log).open('w', encoding='utf-8', newline='\n') as target:
        result = subprocess.run([str(python), '-I', '-u', '-c', setup + code], cwd=frozen,
                                env=environment(python), stdout=target, stderr=subprocess.STDOUT)
    if result.returncode:
        raise ValueError('frozen payload validation failed: ' + Path(log).read_text(encoding='utf-8', errors='replace')[-6000:])


def certification_workspace(clean, identifier):
    audit = Path(clean) / 'certifications' / release_id(identifier)
    if audit.exists():
        raise ValueError('certification workspace already exists; use a new release version')
    audit.mkdir(parents=True)
    return audit


def certify(clean, staging, identifier):
    clean = ignored_path(clean)
    staging = ignored_path(staging)
    identifier = release_id(identifier)
    release = profile(identifier)
    business, source_package = release['business_sha256'], release['source_sha256']
    tool_inputs = tool_bindings()
    if staging.exists():
        raise ValueError('release staging directory already exists')
    report, frozen, earlier = check_clean_build(clean, release)
    python = clean / '.venv/Scripts/python.exe'
    audit = certification_workspace(clean, identifier)
    logs = audit / 'logs'
    logs.mkdir()
    historical_source_sha = None
    if release['historical_native_control']:
        # Version 1.0 rebuilt the Phase 7 native package as its own lineage stage.
        isolated_call(python, frozen,
            'from run_source_regressions import package_digest; from healthcare_synthetic.engine import atomic_json; '
            'from pathlib import Path; '
            f'atomic_json(Path({str(audit / "historical-source-control.json")!r}),'
            f'{{"sha256":package_digest(Path({str(frozen / "output/source-delivery")!r}))}})',
            logs / 'historical-native-control.log')
        historical_source_sha = read(audit / 'historical-source-control.json')['sha256']
        if historical_source_sha != read(frozen / 'evidence/source-delivery/acceptance-gate.json')['source_package_sha256']:
            raise ValueError('clean historical native source package differs from its accepted version')
    print('Regenerating native payload from the clean primary candidate', flush=True)
    # The frozen exporter requires its target inside its own output/data root.
    native_parent = frozen / 'output/certified-native' / identifier
    run_script(python, frozen, 'export_integrated_sources.py', ('--output', native_parent), log=logs / 'native-export.log')
    staging.mkdir(parents=True)
    dataset = staging / 'dataset'
    dataset.mkdir()
    primary = frozen / 'output/integrated-history'
    copy_tree(primary / 'canonical', dataset / 'canonical')
    shutil.copy2(primary / 'manifest.json', dataset / 'manifest.json')
    native = staging / 'native'
    native.mkdir()
    for name in ('valid', 'challenges'):
        copy_tree(native_parent / name, native / name)
    for name in ('manifest.json', 'source-dictionary.json', 'challenge-manifest.json'):
        shutil.copy2(native_parent / name, native / name)
    for name in ('contracts', 'references', 'reviews'):
        copy_tree(frozen / name, staging / name)
    copy_tree(frozen / 'docs', staging / 'historical-docs')
    copy_tree(ROOT / 'docs/dataset-release', staging / 'docs')
    (staging / 'schema').mkdir()
    isolated_call(python, frozen,
        'from healthcare_synthetic.integrated_generation import schema; import json; from pathlib import Path; '
        f'Path({str(staging / "schema/tables.json")!r}).write_text(json.dumps(schema(),indent=2)+"\\n",encoding="utf-8",newline="\\n")',
        logs / 'schema.log')
    copy_tree(clean / 'runtime', staging / 'runtime')
    shutil.copy2(ROOT / 'release_tooling/runtime-lock.json', staging / 'runtime/runtime-lock.json')
    copy_tree(clean / 'archives', staging / 'producers')
    tools = staging / 'reproducibility/release_tooling'
    tools.mkdir(parents=True)
    for p in sorted((ROOT / 'release_tooling').iterdir()):
        if p.is_file() and p.suffix in ('.py', '.json'):
            shutil.copy2(p, tools / p.name)
    tests_dir = staging / 'reproducibility/tests'
    tests_dir.mkdir()
    shutil.copy2(ROOT / 'tests/test_dataset_release.py', tests_dir / 'test_dataset_release.py')
    bundle = staging / 'producers/producer-history.bundle'
    subprocess.run(['git', 'bundle', 'create', str(bundle), 'main'], cwd=ROOT, capture_output=True, check=True)
    subprocess.run(['git', 'bundle', 'verify', str(bundle)], cwd=ROOT, capture_output=True, check=True)
    producer_head = subprocess.run(['git', 'rev-parse', 'main'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    if producer_head != report['producer_commit']:
        raise ValueError('producer bundle main must be the certified Phase 8 revision')
    evidence = staging / 'evidence'
    evidence.mkdir()
    for name in ('clean-rebuild.json', 'runtime-evidence.json'):
        shutil.copy2(clean / name, evidence / name)
    copy_tree(frozen / 'evidence', evidence / 'prior-gates')
    before = digest(inventory(dataset))
    print('Validating every canonical row in the actual staged payload', flush=True)
    validation = audit / 'published-payload-validation'
    run_script(python, frozen, 'inspect_integrated_history.py',
               ('--candidate', dataset, '--output', validation), log=logs / 'published-canonical.log')
    inspection = read(validation / 'inspection.json')
    if inspection['status'] != 'PASS' or inspection['domain_defects'] or not inspection['dependencies_unchanged']:
        raise ValueError('published canonical inspection failed')
    if inspection['business_sha256'] != business or inspection['domain_checks'] != release['domain_checks']:
        raise ValueError('published canonical checks/anchor incomplete')
    if digest(inventory(dataset)) != before:
        raise ValueError('canonical payload changed during validation')
    review_context = frozen / 'output/integrated-validation'
    review_context.mkdir(exist_ok=True)
    for name in ('consumer-index.sqlite3', 'realism-profiles.json'):
        shutil.copy2(validation / name, review_context / name)
    isolated_call(python, frozen,
        'from review_integrated_history import render; from healthcare_synthetic.integrated_generation import read; '
        'from healthcare_synthetic.engine import atomic_json; from pathlib import Path; import hashlib; '
        f'body,selection=render(); reviewed=read(Path({str(frozen / "reviews/integrated-history-review.json")!r})); '
        'assert all(reviewed[k]==v for k,v in selection.items()), "published facts/profile no longer match the designated review"; '
        f'assert hashlib.sha256(body.encode()).hexdigest()==hashlib.sha256(Path({str(staging / "reviews/integrated-history-sample.md")!r}).read_bytes()).hexdigest(); '
        f'atomic_json(Path({str(validation / "review-binding.json")!r}),{{"status":"PASS","selection":selection,"reviewed_facts_unchanged":True}})',
        logs / 'published-review-binding.log')
    before_native = digest(inventory(native))
    print('Reconstructing all actual staged native deliveries and fault outcomes', flush=True)
    isolated_call(python, frozen,
        'from healthcare_synthetic.integrated_source_validation import inspect; '
        'from run_source_regressions import package_digest; '
        'from healthcare_synthetic.engine import atomic_json; from pathlib import Path; '
        f'r=inspect(Path({str(dataset)!r}),Path({str(native)!r}),Path({str(audit / "published-native-replay.sqlite3")!r})); '
        f'r["package_sha256"]=package_digest(Path({str(native)!r})); '
        f'atomic_json(Path({str(validation / "source-inspection.json")!r}),r); print(r["status"])',
        logs / 'published-native.log')
    source = read(validation / 'source-inspection.json')
    if source['status'] != 'PASS' or source['unexplained_differences'] or source['package_sha256'] != source_package:
        raise ValueError('published native reconstruction or exact source package differs')
    # Fault execution writes disposable replay databases outside native valid/
    # and challenges/. Do not silently add those technical indices to a release.
    after_native = inventory(native)
    allowed = inventory(native_parent)
    allowed = {p: v for p, v in allowed.items() if p.split('/')[0] in ('valid', 'challenges') or '/' not in p and p in ('manifest.json','source-dictionary.json','challenge-manifest.json')}
    if any(after_native.get(p) != meta for p, meta in allowed.items()):
        raise ValueError('native published facts changed during validation')
    extras = set(after_native) - set(allowed)
    if extras:
        raise ValueError('validation created unexpected native artifacts: ' + str(sorted(extras)[:5]))
    if digest(after_native) != before_native:
        raise ValueError('native payload changed during validation')
    for name in ('inspection.json', 'domain-controls.json', 'consumer-controls.json', 'point-in-time.json', 'realism-profiles.json', 'source-inspection.json', 'review-binding.json'):
        shutil.copy2(validation / name, evidence / name)
    certificate = {
        'status': 'PASSED', 'implementation_phase': 9, 'release_id': identifier,
        'certified_at': datetime.now(timezone.utc).isoformat(), 'producer_commit': report['producer_commit'],
        'git_version': subprocess.run(['git', '--version'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(),
        'clean_rebuild_passed': True, 'generated_inputs_imported': 0, 'checkpoint_inputs_imported': 0,
        'phase8_unchanged_evidence_verified': True, 'phase8_tests_retained': earlier['tests']['run'],
        'prior_seed_experiments_retained': [20261023, 20261024, 20261025],
        'domain_checks': inspection['domain_checks'], 'partitions': inspection['partitions'],
        'source_files': source['source_files'], 'duplicate_deliveries_checked': source['duplicate_deliveries_checked'],
        'fault_outcomes': len(source['faults']['outcomes']),
        'future_fact_failures': inspection['point_in_time']['future_fact_failures'],
        'unknown_outcomes_preserved': inspection['point_in_time']['unknown_outcomes_preserved'],
        'unresolved_p0_p1': 0, 'unexplained_differences': 0,
        'canonical_business_sha256': business, 'source_package_sha256': source_package,
        'historical_source_package_sha256': historical_source_sha,
        'canonical_validation_target': 'The actual staged dataset/ files; not an earlier in-memory candidate',
        'native_validation_target': 'The actual staged native/ files and challenge/control payloads',
        'business_acceptance': 'REQUIRED_SEPARATELY', 'solution_implementation_started': False,
        'lineage': report['stages'], 'runtime_evidence_sha256': sha_file(evidence / 'runtime-evidence.json'),
        'validation_artifacts': {p.name: {'sha256': sha_file(p), 'bytes': p.stat().st_size}
                                 for p in sorted(evidence.glob('*.json'))},
        'current_domain_review_sha256': sha_file(staging / 'reviews/integrated-history-review.json'),
        'limitations_sha256': sha_file(staging / 'docs/limitations.md'),
        'release_tool_bindings': tool_inputs}
    if tool_bindings() != tool_inputs:
        raise ValueError('release tooling/tests/documentation changed during certification')
    save(evidence / 'certification.json', certificate)
    descriptor_sha = seal(staging, identifier, {
        'profile': PROFILE, 'technical_status': 'PASSED', 'producer_commit': report['producer_commit'],
        'canonical_business_sha256': business, 'source_package_sha256': source_package,
        'business_tables': 25, 'business_rows': release['business_rows'], 'cap_counted_release_rows': release['business_rows'] + release['challenge_copies'],
        'certification_sha256': sha_file(evidence / 'certification.json'),
        'business_acceptance_required': True, 'separate_solution_authorization_required': True})
    verified = verify_healthcare_release(staging, descriptor_sha)
    save(audit / 'technical-release-gate.json', {**verified, 'status': 'TECHNICALLY_CERTIFIED_PENDING_OWNER_ACCEPTANCE',
         'solution_status': 'BLOCKED_FOR_SOLUTION', 'staging': str(staging),
         'certification_sha256': sha_file(evidence / 'certification.json'),
         'limitations_sha256': sha_file(staging / 'docs/limitations.md')})
    print(json.dumps(verified), flush=True)
    return verified


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--clean-build', type=Path, required=True)
    p.add_argument('--staging', type=Path, required=True)
    p.add_argument('--release-id', default=CURRENT_RELEASE)
    a = p.parse_args()
    certify(a.clean_build, a.staging, a.release_id)
