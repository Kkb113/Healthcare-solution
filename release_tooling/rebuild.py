"""Rebuild the pinned accepted lineage without importing any generated snapshot."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import venv
from datetime import datetime, timezone
from pathlib import Path

from .common import ROOT, digest, ignored_path, inventory, read, save, sha_file

PRODUCER_COMMIT = '0f398f3c09be70d34a1811283e80aa0de57dc8ed'
LINEAGE = (
    ('master-foundation', 'f7d512673e21f032065774b8afcde6800df28f72', 'generate_master_data.py',
     'c4e987cfd994c51a6bcf0352d44b386d701a84ef8e35a84240bbed25cf1dc59c'),
    ('clinical-histories', '691435db3708939196b83d9cbade39b3e5db4785', 'generate_clinical_histories.py',
     'a74a03a5b086143cc6db18b1b70e41a914aeab0750e64ea967ffe83e95ccf1ca'),
    ('operational-flow', '51ef26af7a1002e6a6074f96b72059f74dbbe5dc', 'generate_operational_flow.py',
     'f0ffb9bb73ef93375cd24dac8294ffefa05c2a6b48252493047011f5fb0e2eed'),
    ('resource-foundation', '1840da3dbe3edf643b12e7b3e4a1897312d99d86', 'generate_resource_foundation.py',
     'd74687a69f72c7e2b4f63fea2ede2d58e45487c86a2e92a2013ca639f675c439'),
    ('financial-history', 'eb20bfa55eb7ac9850f9b3f5b4037a247a4f3f82', 'generate_financial_history.py',
     '773a236ec9c7ec3df5605f38d21f4934a9384eae1bbf04ab4bf164cb51006b72'),
    ('source-delivery', 'bfd89b22d54bac051a3daf4ea27adcae0c5475b2', 'generate_source_delivery.py',
     '773a236ec9c7ec3df5605f38d21f4934a9384eae1bbf04ab4bf164cb51006b72'),
    ('integrated-history', PRODUCER_COMMIT, 'generate_integrated_history.py',
     '61124cc71b21198163a278fc103798d919c4346d587b3bef320091ff17edaa5e'),
)


def extract_archive(archive, destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive) as source:
        for member in source.getmembers():
            target = (destination / member.name).resolve()
            if destination not in target.parents or not (member.isfile() or member.isdir()):
                raise ValueError('unsafe frozen source archive')
        source.extractall(destination)


def environment(python):
    # Isolated Python ignores Python environment variables. Remove them as well
    # so subprocesses never inherit a user site, editable install or pip config.
    result = {k: v for k, v in os.environ.items()
              if not k.upper().startswith(('PYTHON', 'PIP_', 'GIT_CONFIG')) and k.upper() != 'VIRTUAL_ENV'}
    result['PIP_NO_INDEX'] = '1'
    result['VIRTUAL_ENV'] = str(Path(python).parents[1])
    return result


def run_script(python, source, script, args=(), log=None):
    source = Path(source).resolve()
    wrapper = ('import runpy,sys; '
               f'sys.path.insert(0,{str(source / "scripts")!r}); '
               f'sys.argv={[str(source / "scripts" / script), *map(str, args)]!r}; '
               f'runpy.run_path({str(source / "scripts" / script)!r},run_name="__main__")')
    command = [str(python), '-I', '-u', '-c', wrapper]
    with Path(log).open('w', encoding='utf-8', newline='\n') if log else open(os.devnull, 'w') as target:
        completed = subprocess.run(command, cwd=source, env=environment(python),
                                   stdout=target, stderr=subprocess.STDOUT)
    if completed.returncode:
        tail = Path(log).read_text(encoding='utf-8', errors='replace')[-6000:] if log else ''
        raise ValueError(f'isolated {script} exited {completed.returncode}: {tail}')
    return {'script': script, 'arguments': list(map(str, args)), 'isolated_mode': True,
            'exit_code': completed.returncode, 'log_sha256': sha_file(log) if log else None}


def create_runtime(work, wheel):
    lock = read(ROOT / 'release_tooling/runtime-lock.json')
    base = Path(sys._base_executable).resolve()
    if platform.python_version() != lock['python'] or platform.python_implementation() != 'CPython':
        raise ValueError('release base Python version differs')
    for name, expected in lock['base_binaries'].items():
        if sha_file(base.parent / name) != expected:
            raise ValueError('release base interpreter binary differs: ' + name)
    wheel = Path(wheel).resolve()
    if wheel.name != lock['wheel']['name'] or sha_file(wheel) != lock['wheel']['sha256']:
        raise ValueError('release dependency wheel differs')
    runtime = work / 'runtime'
    runtime.mkdir()
    shutil.copy2(wheel, runtime / wheel.name)
    requirements = runtime / 'requirements.txt'
    requirements.write_text('tzdata==2025.2 --hash=sha256:' + lock['wheel']['sha256'] + '\n',
                            encoding='utf-8', newline='\n')
    virtual = work / '.venv'
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(virtual)
    python = virtual / 'Scripts/python.exe'
    subprocess.run([str(python), '-I', '-m', 'pip', 'install', '--no-index', '--no-deps',
                    '--require-hashes', '--find-links', str(runtime), '-r', str(requirements)],
                   cwd=work, env=environment(python), check=True)
    probe = subprocess.run([str(python), '-I', '-c',
        'import sys,json,importlib.metadata as m,hashlib; from importlib import resources; '
        'print(json.dumps({"isolated":sys.flags.isolated,"no_user_site":sys.flags.no_user_site,'
        '"prefix":sys.prefix,"base_prefix":sys.base_prefix,"packages":{d.metadata["Name"].lower():d.version for d in m.distributions()},'
        '"chicago_sha256":hashlib.sha256(resources.files("tzdata").joinpath("zoneinfo/America/Chicago").read_bytes()).hexdigest()}))'],
        env=environment(python), capture_output=True, text=True, check=True)
    observed = json.loads(probe.stdout)
    if observed['packages'] != lock['packages'] or observed['chicago_sha256'] != lock['chicago_sha256'] or observed['prefix'] == observed['base_prefix']:
        raise ValueError('clean dependency environment differs')
    save(work / 'runtime-evidence.json', {**observed, 'lock_sha256': sha_file(ROOT / 'release_tooling/runtime-lock.json'),
         'wheel_sha256': sha_file(wheel), 'system_site_packages': False,
         'scope': 'Fresh venv and empty generated-data workspaces on this Windows host; same pinned CPython base, not a separate machine/container.'})
    return python


def snapshot(path, expected):
    path = Path(path)
    manifest = read(path / 'manifest.json')
    if manifest['business_sha256'] != expected or manifest['status'] in ('RUNNING', 'FAILED', 'BLOCKED'):
        raise ValueError('rebuilt snapshot anchor/status differs: ' + str(path))
    if 'canonical_files' not in manifest:
        return manifest
    declared = {v['file'] for v in manifest['canonical_files'].values()}
    if {p.relative_to(path).as_posix() for p in (path / 'canonical').iterdir()} != declared:
        raise ValueError('rebuilt canonical inventory differs')
    for table, meta in manifest['canonical_files'].items():
        file = path / meta['file']
        if sha_file(file) != meta['sha256'] or file.stat().st_size != meta['bytes']:
            raise ValueError('rebuilt actual table bytes differ: ' + table)
        with file.open('rb') as stream:
            if sum(1 for _ in stream) != meta['rows']:
                raise ValueError('rebuilt actual table count differs: ' + table)
    if digest({t: m['sha256'] for t, m in sorted(manifest['canonical_files'].items())}) != expected:
        raise ValueError('rebuilt file-map digest differs')
    return manifest


def copy_parent(parent, target):
    target.mkdir(parents=True, exist_ok=False)
    manifest = read(parent / 'manifest.json')
    shutil.copy2(parent / 'manifest.json', target / 'manifest.json')
    if 'canonical_files' in manifest:
        shutil.copytree(parent / 'canonical', target / 'canonical')
    else:
        for name in ('valid', 'challenges'):
            shutil.copytree(parent / name, target / name)
        for name in ('source-dictionary.json', 'challenge-manifest.json'):
            shutil.copy2(parent / name, target / name)


def rebuild(output, wheel):
    output = ignored_path(output)
    if output.exists():
        raise ValueError('clean certification workspace already exists; choose a new run directory')
    output.mkdir(parents=True)
    controller_paths = [ROOT / 'release_tooling' / name for name in
                        ('__init__.py', 'common.py', 'rebuild.py', 'runtime-lock.json')]
    bindings = {p.relative_to(ROOT).as_posix(): sha_file(p) for p in controller_paths}
    report = {'status': 'RUNNING', 'started_at': datetime.now(timezone.utc).isoformat(),
              'controller_bindings': bindings, 'generated_inputs_imported': 0,
              'checkpoint_inputs_imported': 0, 'external_network_used_during_rebuild': False, 'stages': []}
    save(output / 'clean-rebuild.json', report)
    try:
        python = create_runtime(output, wheel)
        built = {}
        for name, commit, script, expected in LINEAGE:
            begin = time.monotonic()
            print('Clean rebuild starting: ' + name, flush=True)
            archive = output / 'archives' / (name + '.tar')
            archive.parent.mkdir(exist_ok=True)
            subprocess.run(['git', 'archive', '--format=tar', '--output', str(archive), commit],
                           cwd=ROOT, check=True, capture_output=True)
            source = output / 'sources' / name
            extract_archive(archive, source)
            source_hash = digest(inventory(source))
            if (source / 'output').exists() or (source / 'data').exists():
                raise ValueError('frozen source archive contains generated inputs')
            parents = []
            for previous, parent in built.items():
                copy_parent(parent, source / 'output' / previous)
                parents.append({'name': previous, 'source_stage': previous,
                                'business_sha256': read(parent / 'manifest.json')['business_sha256'],
                                'generated_in_this_clean_run': True, 'checkpoints_copied': False})
            target = source / 'output' / name
            if target.exists():
                raise ValueError('stage checkpoint/output exists before first invocation')
            log = output / 'logs' / (name + '.log')
            log.parent.mkdir(exist_ok=True)
            command = run_script(python, source, script, log=log)
            manifest = snapshot(target, expected)
            if manifest.get('reused'):
                raise ValueError('clean generation unexpectedly reused checkpoints')
            entry = {'name': name, 'producer_commit': commit, 'archive_sha256': sha_file(archive),
                     'source_tree_sha256': source_hash, 'parents': parents, 'command': command,
                     'business_sha256': manifest['business_sha256'],
                     'business_rows': manifest.get('business_rows', manifest.get('canonical_business_rows')),
                     'executed': manifest.get('executed'), 'reused': manifest.get('reused'),
                     'elapsed_seconds': round(time.monotonic() - begin, 3), 'status': 'PASS'}
            report['stages'].append(entry)
            save(output / 'clean-rebuild.json', report)
            built[name] = target
            print('Clean rebuild passed: ' + name + ' ' + expected, flush=True)
        if any(sha_file(ROOT / p) != h for p, h in bindings.items()):
            raise ValueError('clean rebuild controller changed during execution')
        report.update(status='PASS', finished_at=datetime.now(timezone.utc).isoformat(),
                      producer_commit=PRODUCER_COMMIT, controller_unchanged=True)
        save(output / 'clean-rebuild.json', report)
        return report
    except Exception as exc:
        report.update(status='FAILED', error=str(exc))
        save(output / 'clean-rebuild.json', report)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, required=True)
    args = parser.parse_args()
    result = rebuild(args.output, args.wheel)
    print(json.dumps({'status': result['status'], 'lineage_stages': len(result['stages'])}))
