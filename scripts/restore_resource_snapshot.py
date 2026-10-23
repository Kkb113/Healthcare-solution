"""Restore the immutable accepted resource parent using its exact Git source."""
import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACCEPTED_COMMIT='1840da3dbe3edf643b12e7b3e4a1897312d99d86'


def restore(output=ROOT/'output/resource-foundation'):
    output=Path(output).resolve()
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output','data'):raise ValueError('destination must be ignored workspace output/data')
    if output.exists():raise ValueError('resource destination already exists; accepted snapshots are never overwritten')
    if not (ROOT/'output/operational-flow/manifest.json').exists():
        from restore_operational_snapshot import restore as restore_operations
        restore_operations()
    with tempfile.TemporaryDirectory(prefix='accepted-resource-rebuild-',dir=ROOT/'output') as directory:
        work=Path(directory);source=work/'source';source.mkdir();archive=work/'accepted.tar'
        subprocess.run(['git','archive','--format=tar','--output',str(archive),ACCEPTED_COMMIT],cwd=ROOT,check=True,capture_output=True)
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                target=(source/member.name).resolve()
                if source not in target.parents or not (member.isfile() or member.isdir()):raise ValueError('unsafe accepted source archive')
            tar.extractall(source)
        for parent in ('master-foundation','clinical-histories','operational-flow'):
            destination=source/'output'/parent;destination.mkdir(parents=True)
            shutil.copytree(ROOT/'output'/parent/'canonical',destination/'canonical');shutil.copy2(ROOT/'output'/parent/'manifest.json',destination/'manifest.json')
        completed=subprocess.run([sys.executable,str(source/'scripts/generate_resource_foundation.py')],cwd=source,timeout=3600)
        if completed.returncode:raise ValueError('exact accepted resource rebuild failed')
        generated=source/'output/resource-foundation';manifest=json.loads((generated/'manifest.json').read_text());gate=json.loads((ROOT/'evidence/resource-foundation/acceptance-gate.json').read_text())
        if manifest['status']!='RESOURCE_FOUNDATION_PASSED' or manifest['business_sha256']!=gate['business_sha256']:raise ValueError('rebuilt resource hash differs')
        output.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(generated,output)
    return {'status':'RESTORED_ACCEPTED_RESOURCE','accepted_commit':ACCEPTED_COMMIT,'business_sha256':manifest['business_sha256'],'output':str(output)}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/resource-foundation');a=p.parse_args()
    try:print(json.dumps(restore(a.output)))
    except Exception as exc:print(json.dumps({'status':'FAILED','error':str(exc)}));sys.exit(1)
