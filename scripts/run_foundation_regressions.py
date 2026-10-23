"""Run scoped regression groups without rewriting historical acceptance or accepted inputs."""
import argparse
import io
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_phase1 import RecordingResult

class ProgressResult(RecordingResult):
    def startTest(self,test):
        super().startTest(test)
        print('Testing '+test.id(),flush=True)

def verification_hashes():
    paths=sorted((ROOT/'src/healthcare_synthetic').glob('*.py'))+sorted((ROOT/'tests').glob('*.py'))+sorted((ROOT/'scripts').glob('*.py'))
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def run_group(group,report):
    before=verification_hashes()
    suite=unittest.TestSuite()
    patterns={'framework-master':['test_phase*.py','test_master_data.py'],'operational':['test_operational_flow.py'],'clinical':['test_clinical_histories.py']}[group]
    for pattern in patterns:suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern))
    log=io.StringIO();result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=ProgressResult).run(suite)
    value={'group':group,'run':result.testsRun,'passed':result.wasSuccessful() and not result.skipped,'failed':len(result.failures),
        'errors':len(result.errors),'skipped':len(result.skipped),'cases':result.records,'failure_details':[message for _,message in result.failures+result.errors]}
    value['verification_source_sha256']=before
    value['verification_sources_unchanged_during_tests']=before==verification_hashes()
    value['passed']=value['passed'] and value['verification_sources_unchanged_during_tests']
    if group=='operational':value['candidate_business_sha256']=json.loads((Path(os.environ.get('HEALTHCARE_OPERATIONAL_TEST_CANDIDATE',ROOT/'output/operational-flow'))/'manifest.json').read_text())['business_sha256']
    Path(report).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not value['passed']:print(log.getvalue(),flush=True)
    return value

def historical_clinical(report):
    before=verification_hashes()
    from restore_clinical_snapshot import archive_source,ACCEPTED_COMMIT
    with tempfile.TemporaryDirectory(prefix='accepted-clinical-regressions-',dir=ROOT/'output') as directory:
        source=archive_source(Path(directory))
        # The runner is outside src and does not change historical generation locks.
        runner=source/'run_foundation_regressions.py';runner.write_text(Path(__file__).read_text().replace("ROOT=Path(__file__).resolve().parents[1]","ROOT=Path(__file__).resolve().parent"),encoding='utf-8',newline='\n')
        env=dict(os.environ,GIT_DIR=str(ROOT/'.git'),GIT_WORK_TREE=str(source),HEALTHCARE_CLINICAL_TEST_CANDIDATE=str(ROOT/'output/clinical-histories'))
        result=subprocess.run([sys.executable,str(runner),'--group','clinical','--report',str(Path(report).resolve())],cwd=source,env=env,timeout=2700)
        if not Path(report).exists():raise ValueError('historical clinical runner failed without evidence')
        value=json.loads(Path(report).read_text());value['accepted_source_commit']=ACCEPTED_COMMIT
        value['scope']='Exact accepted clinical generator and tests; immutable accepted clinical data. Current framework/master and operational modules are tested separately.'
        value['verification_source_sha256']=before
        value['verification_sources_unchanged_during_tests']=before==verification_hashes()
        value['passed']=value['passed'] and value['verification_sources_unchanged_during_tests']
        Path(report).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
        if result.returncode:raise ValueError('accepted clinical regression failed: '+str(value['failure_details']))
    return value

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--group',choices=('framework-master','operational','clinical','historical-clinical'),required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    a.report.parent.mkdir(parents=True,exist_ok=True)
    result=historical_clinical(a.report) if a.group=='historical-clinical' else run_group(a.group,a.report)
    print(json.dumps({k:result[k] for k in ('group','run','passed','failed','errors','skipped')}));sys.exit(0 if result['passed'] else 1)
