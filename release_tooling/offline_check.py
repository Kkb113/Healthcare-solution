"""Prove the distributed Git bundle and copied release tools work offline."""
import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

from .common import ROOT, ignored_path, read, save, sha_file
from .package import verify_healthcare_release
from .profiles import lineage, profile


def clone_bundle(bundle, output):
    # A bundle made from `main` alone has no remote HEAD. Plain clone can
    # choose the host's default branch (often master), leaving no checkout.
    subprocess.run(['git', 'clone', '--no-hardlinks', '--branch', 'main', str(bundle), str(output)],
                   check=True, capture_output=True)


def check(package, output, descriptor_sha256):
    package = Path(package).resolve();output = ignored_path(output)
    verified = verify_healthcare_release(package, descriptor_sha256)
    release = profile(verified['release_id'])
    producer = read(package / 'evidence/certification.json')['producer_commit']
    stages_expected = lineage(release, producer)
    if output.exists():
        raise ValueError('offline source-check destination already exists')
    bundle = package / 'producers/producer-history.bundle'
    clone_bundle(bundle, output)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=output, capture_output=True, text=True, check=True).stdout.strip()
    if head != producer or (output / 'output').exists() or (output / 'data').exists():
        raise ValueError('offline bundle checkout differs or includes generated inputs')
    stages = []
    for name, commit, _, _ in stages_expected:
        raw = subprocess.run(['git', 'archive', '--format=tar', commit], cwd=output, capture_output=True, check=True).stdout
        expected = sha_file(package / 'producers' / (name + '.tar'))
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('offline producer archive differs: ' + name)
        stages.append({'stage': name, 'commit': commit, 'archive_sha256': expected})
    shutil.copytree(package / 'reproducibility/release_tooling', output / 'release_tooling')
    shutil.copy2(package / 'reproducibility/tests/test_dataset_release.py', output / 'tests/test_dataset_release.py')
    shutil.copytree(package / 'docs', output / 'docs/dataset-release')
    subprocess.run([sys.executable, '-m', 'release_tooling.run_tests'], cwd=output, check=True)
    tests = read(output / release['certification_root'] / 'release-tests.json')
    if not tests['passed'] or tests['skipped']:
        raise ValueError('distributed release-tool tests failed')
    result = {'status': 'PASSED', 'scope': 'Offline source/archive reconstruction and release-tool fixtures. The complete cold data rebuild is separately recorded, not claimed as executed twice.',
              'release_id': verified['release_id'], 'descriptor_sha256': descriptor_sha256,
              'bundle_sha256': sha_file(bundle), 'producer_stages': stages,
              'fresh_checkout_generated_inputs': 0, 'external_network_used': False,
              'distributed_tool_tests': tests['run'], 'tool_bindings': tests['tool_bindings']}
    save(ROOT / release['certification_root'] / 'offline-source-check.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    p.add_argument('--descriptor-sha256', required=True);a = p.parse_args()
    print(check(a.package, a.output, a.descriptor_sha256))
