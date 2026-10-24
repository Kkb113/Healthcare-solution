"""Run bound integrated candidate tests, preserving evidence for the final gate."""
import argparse
import io
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.integrated_generation import read,sha_file,dependencies
from healthcare_synthetic.integrated_consumers import digest
from run_foundation_regressions import verification_hashes,ProgressResult
from run_source_regressions import input_hashes as previous_inputs,package_digest

def inputs():
    result=previous_inputs()
    for p in (ROOT/'evidence/source-delivery').glob('*.json'):result[p.relative_to(ROOT).as_posix()]=sha_file(p)
    return result

def candidates():
    result={}
    for name in ('integrated-history','integrated-comparison-20261024','integrated-comparison-20261025'):
        root=ROOT/'output'/name;m=read(root/'manifest.json');files={}
        if m['status'] not in ('CANDIDATE_NOT_YET_ACCEPTED','ELIGIBLE_FOR_CERTIFICATION'):raise ValueError('candidate is incomplete: '+name)
        if m['locks']!=dependencies():raise ValueError('candidate producer/configuration locks are stale: '+name)
        for table,f in m['canonical_files'].items():
            actual=sha_file(root/f['file'])
            if actual!=f['sha256']:raise ValueError('candidate actual bytes differ: '+name+'/'+table)
            files[table]=actual
        result[name]=digest(files)
        if result[name]!=m['business_sha256']:raise ValueError('candidate hash differs')
    source_root=ROOT/'output/integrated-source-delivery'
    if read(source_root/'manifest.json')['status'] not in ('EXPORTED_NOT_YET_VALIDATED','INTEGRATED_SOURCE_SIMULATION_PASSED'):raise ValueError('native source candidate is incomplete')
    result['native_sources']=package_digest(source_root)
    return result

def run(small_only=False):
    before=verification_hashes();bindings=inputs();initial=candidates() if not small_only else None
    evidence_paths=[ROOT/'output/integrated-validation/inspection.json', ROOT/'output/integrated-comparison-20261024/validation/inspection.json', ROOT/'output/integrated-comparison-20261025/validation/inspection.json']
    inspected={p.relative_to(ROOT).as_posix():sha_file(p) for p in evidence_paths} if not small_only else {}
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_integrated_history.py')
    if small_only:
        def flatten(s):
            for item in s:
                if isinstance(item,unittest.TestSuite):yield from flatten(item)
                else:yield item
        suite=unittest.TestSuite(t for t in flatten(suite) if t.__class__.__name__=='ConsumerContractTests')
    log=io.StringIO();tested=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=ProgressResult,failfast=True).run(suite)
    result={'run':tested.testsRun,'passed':tested.wasSuccessful() and not tested.skipped,'failures':[x for _,x in tested.failures+tested.errors],
            'failed':len(tested.failures),'errors':len(tested.errors),'skipped':len(tested.skipped),'cases':tested.records,
            'verification_source_sha256':before,'verification_input_sha256':bindings,'candidate_bindings':initial,
            'inspection_bindings':inspected,'inspections_unchanged':all(sha_file(ROOT/p)==h for p,h in inspected.items()),
            'sources_unchanged':before==verification_hashes(),'inputs_unchanged':bindings==inputs(),
            'candidates_unchanged':True if small_only else initial==candidates()}
    source_inspection=ROOT/'output/integrated-validation/source-inspection.json'
    result['source_inspection_sha256']=sha_file(source_inspection) if source_inspection.exists() else None
    result['passed']=result['passed'] and result['sources_unchanged'] and result['inputs_unchanged'] and result['candidates_unchanged'] and result['inspections_unchanged']
    target=ROOT/'output/integrated-validation'/('consumer-fixture-tests.json' if small_only else 'integrated-tests.json');target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not result['passed']:print(log.getvalue(),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--small-only',action='store_true');a=p.parse_args()
    r=run(a.small_only);print(json.dumps({k:r[k] for k in ('run','passed','failed','errors','skipped')}));sys.exit(0 if r['passed'] else 1)
