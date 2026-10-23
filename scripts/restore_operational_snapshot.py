"""Restore the immutable accepted operational parent from its exact Git revision."""
import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACCEPTED_COMMIT='51ef26af7a1002e6a6074f96b72059f74dbbe5dc'


def restore(output=ROOT/'output/operational-flow'):
    output=Path(output).resolve()
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output','data'):raise ValueError('destination must be ignored workspace output/data')
    if output.exists():raise ValueError('operational destination already exists; accepted snapshots are never overwritten')
    if not (ROOT/'output/clinical-histories/manifest.json').exists():
        from restore_clinical_snapshot import restore as clinical_restore
        clinical_restore()
    with tempfile.TemporaryDirectory(prefix='accepted-operational-rebuild-',dir=ROOT/'output') as directory:
        work=Path(directory);source=work/'source';source.mkdir();archive=work/'accepted.tar'
        subprocess.run(['git','archive','--format=tar','--output',str(archive),ACCEPTED_COMMIT],cwd=ROOT,check=True,capture_output=True)
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                target=(source/member.name).resolve()
                if source not in target.parents or not (member.isfile() or member.isdir()):raise ValueError('unsafe accepted source archive')
            tar.extractall(source)
        for parent in ('master-foundation','clinical-histories'):
            destination=source/'output'/parent;destination.mkdir(parents=True)
            shutil.copytree(ROOT/'output'/parent/'canonical',destination/'canonical')
            shutil.copy2(ROOT/'output'/parent/'manifest.json',destination/'manifest.json')
        result=subprocess.run([sys.executable,str(source/'scripts/generate_operational_flow.py')],cwd=source,timeout=1800)
        if result.returncode:raise ValueError('exact accepted operational rebuild failed')
        generated=source/'output/operational-flow';manifest=json.loads((generated/'manifest.json').read_text());gate=json.loads((ROOT/'evidence/operational-flow/acceptance-gate.json').read_text())
        if manifest['status']!='OPERATIONAL_FLOW_PASSED' or manifest['business_sha256']!=gate['business_sha256']:raise ValueError('rebuilt operational hash differs')
        output.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(generated,output)
    return {'status':'RESTORED_ACCEPTED_OPERATIONAL','accepted_commit':ACCEPTED_COMMIT,'business_sha256':manifest['business_sha256'],'output':str(output)}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/operational-flow');a=p.parse_args()
    try:print(json.dumps(restore(a.output)))
    except Exception as exc:print(json.dumps({'status':'FAILED','error':str(exc)}));sys.exit(1)
