"""Rebuild the accepted master snapshot from its exact committed generator, without resetting Git."""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED_COMMIT = 'f7d512673e21f032065774b8afcde6800df28f72'

def restore(output=ROOT / 'output/master-foundation'):
    output = Path(output).resolve()
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output', 'data'): raise ValueError('restoration must stay in ignored workspace output/ or data/')
    if output.exists(): raise ValueError('master destination already exists; do not overwrite an accepted candidate')
    (ROOT / 'output').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='accepted-master-rebuild-', dir=ROOT / 'output') as directory:
        work = Path(directory)
        archive = work / 'accepted-source.tar'
        subprocess.run(['git', 'archive', '--format=tar', '--output', str(archive), ACCEPTED_COMMIT], cwd=ROOT, check=True, capture_output=True)
        source = work / 'source'
        source.mkdir()
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                target = (source / member.name).resolve()
                if source not in target.parents or not (member.isfile() or member.isdir()): raise ValueError('unsafe source archive entry')
            tar.extractall(source)
        generated = source / 'output/master-foundation'
        result = subprocess.run([sys.executable, str(source / 'scripts/generate_master_data.py'), '--output', str(generated)], cwd=source, capture_output=True, text=True, timeout=300)
        if result.returncode != 0: raise ValueError('accepted master rebuild failed: ' + result.stdout + result.stderr)
        manifest = json.loads((generated / 'manifest.json').read_text())
        accepted = json.loads((ROOT / 'evidence/master-data/acceptance-gate.json').read_text())
        if manifest['status'] != 'MASTER_FOUNDATION_PASSED' or manifest['business_sha256'] != accepted['business_sha256']: raise ValueError('rebuilt master differs from accepted hash')
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(generated, output)
    return {'status': 'RESTORED_ACCEPTED_MASTER', 'accepted_commit': ACCEPTED_COMMIT, 'business_sha256': manifest['business_sha256'], 'output': str(output)}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT / 'output/master-foundation')
    a = p.parse_args()
    try: print(json.dumps(restore(a.output)))
    except Exception as exc: print(json.dumps({'status': 'FAILED', 'error': str(exc)})); sys.exit(1)
