"""Restore the accepted clinical snapshot using its exact committed generator, without resetting Git."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACCEPTED_COMMIT='691435db3708939196b83d9cbade39b3e5db4785'

def archive_source(work):
    archive=work/'accepted-source.tar';source=work/'source';source.mkdir()
    subprocess.run(['git','archive','--format=tar','--output',str(archive),ACCEPTED_COMMIT],cwd=ROOT,check=True,capture_output=True)
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            target=(source/member.name).resolve()
            if source not in target.parents or not(member.isfile() or member.isdir()):raise ValueError('unsafe source archive entry')
        tar.extractall(source)
    parent=source/'output/master-foundation';parent.mkdir(parents=True)
    shutil.copytree(ROOT/'output/master-foundation/canonical',parent/'canonical')
    shutil.copy2(ROOT/'output/master-foundation/manifest.json',parent/'manifest.json')
    return source

def restore(output=ROOT/'output/clinical-histories'):
    output=Path(output).resolve()
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output','data'):raise ValueError('destination must be ignored workspace output/data')
    if output.exists():raise ValueError('clinical destination already exists; accepted candidates are never overwritten')
    if not (ROOT/'output/master-foundation/manifest.json').exists():
        from restore_master_snapshot import restore as master_restore
        master_restore()
    with tempfile.TemporaryDirectory(prefix='accepted-clinical-rebuild-',dir=ROOT/'output') as directory:
        source=archive_source(Path(directory));generated=source/'output/clinical-histories'
        result=subprocess.run([sys.executable,str(source/'scripts/generate_clinical_histories.py')],cwd=source,timeout=1200)
        if result.returncode:raise ValueError('accepted clinical rebuild failed')
        manifest=json.loads((generated/'manifest.json').read_text());gate=json.loads((ROOT/'evidence/clinical-histories/acceptance-gate.json').read_text())
        if manifest['status']!='CLINICAL_HISTORIES_PASSED' or manifest['business_sha256']!=gate['business_sha256']:raise ValueError('rebuilt clinical hash differs')
        output.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(generated,output)
    return {'status':'RESTORED_ACCEPTED_CLINICAL','accepted_commit':ACCEPTED_COMMIT,'business_sha256':manifest['business_sha256'],'output':str(output)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/clinical-histories');a=p.parse_args()
    try:print(json.dumps(restore(a.output)))
    except Exception as exc:print(json.dumps({'status':'FAILED','error':str(exc)}));sys.exit(1)
