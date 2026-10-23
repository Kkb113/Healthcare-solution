"""Run financial and retained foundation regressions with complete verification locks."""
import argparse
import hashlib
import io
import json
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from run_resource_regressions import run as prior_run,input_hashes as prior_inputs
from run_foundation_regressions import verification_hashes,ProgressResult


def input_hashes():
    result=prior_inputs();path=ROOT/'evidence/resource-foundation/acceptance-gate.json'
    result[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest();return result


def run(group,report):
    report=Path(report);report.parent.mkdir(parents=True,exist_ok=True);inputs_before=input_hashes();source_before=verification_hashes()
    if group!='financial':result=prior_run(group,report)
    else:
        discovered=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_financial_history.py');log=io.StringIO()
        def flatten(suite):
            for test in suite:
                if isinstance(test,unittest.TestSuite):yield from flatten(test)
                else:yield test
        recovery={'test_clean_rebuild_cached_resume_and_complete_hash_match','test_real_process_crash_rolls_back_and_resumes'}
        suite=unittest.TestSuite(sorted(flatten(discovered),key=lambda t:(t.id().split('.')[-1] in recovery,t.id())))
        tested=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=ProgressResult,failfast=True).run(suite)
        result={'group':'financial','run':tested.testsRun,'passed':tested.wasSuccessful() and not tested.skipped,
            'failed':len(tested.failures),'errors':len(tested.errors),'skipped':len(tested.skipped),'cases':tested.records,
            'failure_details':[message for _,message in tested.failures+tested.errors],
            'verification_source_sha256':source_before,'verification_sources_unchanged_during_tests':source_before==verification_hashes(),
            'candidate_business_sha256':json.loads((Path(os.environ.get('HEALTHCARE_FINANCIAL_TEST_CANDIDATE',ROOT/'output/financial-history'))/'manifest.json').read_text())['business_sha256']}
        if not result['passed']:print(log.getvalue(),flush=True)
    result['verification_input_sha256']=inputs_before;result['verification_inputs_unchanged_during_tests']=inputs_before==input_hashes()
    result['passed']=result['passed'] and result['verification_sources_unchanged_during_tests'] and result['verification_inputs_unchanged_during_tests']
    report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--group',choices=('framework-master','historical-clinical','operational','resource','financial'),required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    result=run(a.group,a.report);print(json.dumps({k:result[k] for k in ('group','run','passed','failed','errors','skipped')}));sys.exit(0 if result['passed'] else 1)
