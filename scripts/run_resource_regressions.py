"""Run current resource and version-bound foundation regressions with input locks."""
import argparse
import hashlib
import io
import json
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_foundation_regressions import run_group,historical_clinical,verification_hashes,ProgressResult


def input_hashes():
    files=sorted((ROOT/'config').glob('*.json'))+sorted((ROOT/'contracts').rglob('*.json'))+sorted((ROOT/'reviews').glob('*.json'))+sorted((ROOT/'reviews').glob('*.md'))
    files += [ROOT/p for p in ('evidence/master-data/acceptance-gate.json','evidence/clinical-histories/acceptance-gate.json','evidence/operational-flow/acceptance-gate.json')]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def run(group,report):
    report=Path(report);report.parent.mkdir(parents=True,exist_ok=True);before=input_hashes()
    if group=='historical-clinical':result=historical_clinical(report)
    elif group!='resource':result=run_group(group,report)
    else:
        source_before=verification_hashes();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_resource_foundation.py')
        log=io.StringIO();test_result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=ProgressResult).run(suite)
        result={'group':'resource','run':test_result.testsRun,'passed':test_result.wasSuccessful() and not test_result.skipped,
            'failed':len(test_result.failures),'errors':len(test_result.errors),'skipped':len(test_result.skipped),'cases':test_result.records,
            'failure_details':[msg for _,msg in test_result.failures+test_result.errors],
            'verification_source_sha256':source_before,'verification_sources_unchanged_during_tests':source_before==verification_hashes(),
            'candidate_business_sha256':json.loads((Path(os.environ.get('HEALTHCARE_RESOURCE_TEST_CANDIDATE',ROOT/'output/resource-foundation'))/'manifest.json').read_text())['business_sha256']}
        if not result['passed']:print(log.getvalue(),flush=True)
    result['verification_input_sha256']=before;result['verification_inputs_unchanged_during_tests']=before==input_hashes()
    result['passed']=result['passed'] and result['verification_sources_unchanged_during_tests'] and result['verification_inputs_unchanged_during_tests']
    report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--group',choices=('framework-master','historical-clinical','operational','resource'),required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    result=run(a.group,a.report);print(json.dumps({k:result[k] for k in ('group','run','passed','failed','errors','skipped')}));sys.exit(0 if result['passed'] else 1)
