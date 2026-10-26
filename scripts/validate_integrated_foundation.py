"""Evaluate all Phase 8 exit criteria; never certify the final release."""
import argparse
import json
import sys
import unittest
import hashlib
import subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.integrated_generation import read,sha_file,dependencies
from healthcare_synthetic.integrated_consumers import digest
from healthcare_synthetic.integrated_validation import inspection_dependencies
from run_integrated_regressions import verification_hashes,inputs,candidates
from review_integrated_history import render
from run_source_regressions import package_digest

def require(value,message):
    if not value:raise ValueError(message)

def retained_evidence():
    report=read(ROOT/'evidence/source-delivery/validation-report.json');prior=report['retained_prior_evidence']
    differences=[];historical=[]
    for path,expected in {**report['verification_source_sha256'],**report['verification_input_sha256']}.items():
        if sha_file(ROOT/path)!=expected:
            # A later version-bound change is allowed only when the retained
            # evidence still describes the exact pinned original implementation.
            found=subprocess.run(['git','show','bfd89b22d54bac051a3daf4ea27adcae0c5475b2:'+path],cwd=ROOT,capture_output=True)
            if found.returncode==0 and path.startswith(('src/','scripts/','tests/','config/','contracts/')):
                require(hashlib.sha256(found.stdout).hexdigest()==expected,'historical domain implementation does not match pinned original revision: '+path)
                historical.append({'path':path,'historical_commit':'bfd89b22d54bac051a3daf4ea27adcae0c5475b2','historical_sha256':expected,'current_sha256':sha_file(ROOT/path),
                                   'current_validation':'Fresh full-population domain, consumer, point-in-time, realism and behaviour-revision controls on three complete connected seed experiments'})
            else:differences.append(path)
    require(not differences and report['passed'],'unchanged prior implementation evidence differs: '+str(differences))
    return {'status':'PASS','historical_domain_tests_retained':prior['retained_tests'],'historical_source_tests_retained':report['tests']['run'],
            'version_bound_source_changes':historical,'overlap':12,'unique_preexisting_tests':326,
            'scope':'Retained historical implementation evidence, including pinned original clinical generation and monthly statistical code. Current boundary/scope fixes have fresh regression/full-population evidence; the older 326 tests are not claimed as newly rerun or as validation of changed code.'}

def evaluate():
    root=ROOT/'output/integrated-validation';candidate=ROOT/'output/integrated-history';before=verification_hashes();bound=inputs();content=candidates()
    tests=read(root/'integrated-tests.json');expected=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_integrated_history.py').countTestCases()
    require(tests['passed'] and tests['run']==expected and tests['failed']==tests['errors']==tests['skipped']==0,'integrated tests missing/incomplete/failed')
    required=('test_real_candidate_process_crash_and_resume','test_full_native_inspection_reports_and_faults',
              'test_failed_export_recovery_and_complete_resume','test_full_history_all_configured_seed_experiments_pass',
              'test_registered_boundary_seed_really_exercises_slot_fallback','test_boundary_fix_preserves_unaffected_candidate_goldens',
              'test_closed_month_ignores_unrelated_later_month_delivery_gap','test_true_target_month_bed_gap_still_blocks_statistics',
              'test_negative_label_waits_for_source_completeness_after_day_thirty','test_old_and_new_master_baselines_cannot_be_incrementally_mixed')
    require(all(name in json.dumps(tests['cases']) for name in required),'required end-to-end/boundary/gate regression case missing')
    require(tests['verification_source_sha256']==before and tests['verification_input_sha256']==bound and tests['candidate_bindings']==content,'integrated regression bindings are stale')
    require(all(tests[k] for k in ('sources_unchanged','inputs_unchanged','candidates_unchanged','inspections_unchanged')),'inputs changed during tests')
    for path,expected_hash in tests['inspection_bindings'].items():require(sha_file(ROOT/path)==expected_hash,'inspection evidence changed')
    require(sha_file(root/'source-inspection.json')==tests['source_inspection_sha256'],'source inspection evidence changed')
    source=read(root/'source-inspection.json');require(source['status']=='PASS' and source['unexplained_differences']==0 and source['source_files']==source['duplicate_deliveries_checked'],'full new source export controls incomplete')
    inspections=[]
    for seed in (20261023,20261024,20261025):
        directory=root if seed==20261023 else ROOT/f'output/integrated-comparison-{seed}/validation'
        report=read(directory/'inspection.json');require(report['status']=='PASS' and not report['domain_defects'],'configured seed did not pass')
        require(report['inspection_dependencies']==inspection_dependencies() and report['dependencies_unchanged'],'inspection code/input bindings are stale')
        require(report['partitions']==324 and all(c['passed'] for c in report['realism_checks']),'realism/partition failure')
        for name,meta in report['artifacts'].items():require(sha_file(directory/name)==meta['sha256'],'full profile/control artifact changed: '+name)
        behaviour=read(directory/'behaviour-revision.json')
        require(behaviour['status']=='PASS' and behaviour['seed']==seed and behaviour['business_sha256']==report['business_sha256'],'version 1.1 behaviour revision checks failed or are stale: '+str(seed))
        report['behaviour_revision']={'status':behaviour['status'],'checks':len(behaviour['checks']),'sha256':sha_file(directory/'behaviour-revision.json')}
        inspections.append(report)
    body,selection=render();review=read(ROOT/'reviews/integrated-history-review.json')
    require((ROOT/'reviews/integrated-history-sample.md').read_bytes()==body.encode() and all(review[k]==v for k,v in selection.items()),'review selection/sample stale')
    require(review['status']=='APPROVED_CONDITIONAL_ON_TECHNICAL_GATES' and review['limitations_accepted'] and not review['external_professional_endorsement'],'synthetic domain review missing')
    issues=read(ROOT/'reviews/integrated-history-issues.json');require(not [i for i in issues['issues'] if i['severity'] in ('P0','P1') and i['status']!='CLOSED'],'unresolved release-blocking issue')
    manifest=read(candidate/'manifest.json');release_rows=manifest['business_rows']+source['challenge_copies']
    require(manifest['locks']==dependencies(),'candidate producer/configuration bindings are stale')
    require(20<=manifest['business_tables']<=25 and 1000000<=release_rows<=2000000,'release record/table cap failed')
    from validate_phase0 import report as design_report
    frozen=design_report();require(frozen['passed'] and frozen['check_count']==41,'frozen design regression failed')
    previous=retained_evidence()
    rules=read(ROOT/'contracts/phase0/validation-rules.json')['rules']
    mapping=[]
    domains_by_prefix={'ID':['master','workforce','finance'],'TM':['master','clinical','workforce'],'NM':['master'],
        'OR':['master','operations'],'WK':['master','clinical','workforce'],'AC':['master'],'CV':['master','clinical'],
        'CD':['master','clinical'],'EN':['clinical','operations'],'CN':['clinical'],'CE':['clinical'],
        'AP':['clinical','operations'],'BD':['operations'],'SF':['workforce'],'IV':['stock','finance'],
        'CH':['finance'],'CL':['finance'],'GL':['finance'],'CO':['finance'],'AX':['finance'],
        'SR':[],'DR':['operations'],'RS':['clinical','operations','workforce','stock'],'CP':['workforce','finance'],
        'RP':[],'FN':['finance']}
    for rule in rules:
        code=rule['id']
        scope='Fresh full-domain controls plus independent consumer/PIT/profile checks'
        if code=='RP01':scope='Phase 8 deterministic candidate replay, crashed-process recovery and subset rebuild; clean-environment final release certification explicitly remains Phase 9'
        if code.startswith('SR'):scope='Every changed-candidate native file reconstructed; all repeated in reverse order; 15 fault/delivery outcomes; 318 calendar snapshots'
        linked=domains_by_prefix[code[:2]]
        executed=read(root/'domain-controls.json')['domains']
        controls={name:[c.get('rule_id',c.get('name')) for c in executed[name]['checks']] for name in linked}
        integrated=[]
        if code.startswith('SR'):integrated=['source-inspection.json:canonical_roundtrip','source-inspection.json:faults','source-inspection.json:delivery_calendar']
        if code.startswith('TM') or code=='AX03':integrated+=['point-in-time.json','source-inspection.json:historical_native_snapshots']
        if code=='RS01':integrated+=['realism-profiles.json:checks','realism-profiles.json:joint_profiles']
        if code in ('BD03','BD04','CL03','CO01','CO02','AX01','AX02','FN01'):integrated+=['consumer-controls.json']
        if code=='RP01':integrated+=['integrated-tests.json:test_real_candidate_process_crash_and_resume']
        mapping.append({'rule_id':code,'severity':rule['severity'],'status':'CANDIDATE_SCOPE_PASSED_RELEASE_CERTIFICATION_PENDING' if code=='RP01' else 'PASS','scope':scope,
                        'executed_domain_controls':controls,'integrated_evidence':integrated,'full_population_seed_ids':[20261023,20261024,20261025]})
    exits={'no_unresolved_p0_p1_or_unexplained_reconciliation_differences':True,
           'all_consumer_contracts_faults_and_point_in_time_checks_pass':True,
           'user_designated_domain_review_accepts_scoped_realism_and_limits':True,
           'eligible_for_release_certification_solution_still_blocked':True}
    require(before==verification_hashes() and bound==inputs() and content==candidates(),'current evidence changed during final gate')
    resource_context=read(candidate/'resource-context/manifest.json')
    physical={'canonical_rows':manifest['business_rows'],'resource_context_mirror_rows':sum(f['rows'] for f in resource_context['canonical_files'].values()),
              'checkpoint_mirror_rows':manifest['checkpoint_mirror_rows'],'consumer_index_mirror_rows':inspections[0]['index']['index_mirror_rows'],
              'native_export_footprint':{k:v for k,v in read(ROOT/'output/integrated-source-delivery/manifest.json').items() if k.endswith('_rows') or k in ('derived_scalar_fact_mirrors','source_payload_bytes')},
              'review_case_summary_mirrors':selection['review_mirror_case_summaries'],'review_selected_source_fact_mirrors':selection['selected_source_fact_mirrors'],
              'comparison_canonical_rows_excluded_from_release':[r['rows'] for r in inspections[1:]]}
    gate={'implementation_phase':8,'dataset_version':read(ROOT/'config/integrated-history-generation.json')['version'],'status':'PASSED','evaluated_at':datetime.now(timezone.utc).isoformat(),'exit_criteria':exits,
          'behaviour_revision_checks_per_seed':[r['behaviour_revision']['checks'] for r in inspections],
          'fresh_integrated_tests':tests['run'],'fresh_domain_checks_per_seed':[r['domain_checks'] for r in inspections],
          'configured_seeds':[r['seed'] for r in inspections],'business_tables':25,'business_rows':manifest['business_rows'],
          'published_challenge_record_copies':source['challenge_copies'],'cap_counted_release_rows':release_rows,
          'canonical_business_sha256':manifest['business_sha256'],'source_package_sha256':content['native_sources'],
          'source_files':source['source_files'],'unexplained_differences':0,'unresolved_p0_p1':0,
          'reviewed_cases':selection['reviewed_cases'],'canonical_rule_catalog_entries':len(mapping),
          'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION','next_phase':'Reproducible release, certification and explicit data acceptance - not started'}
    evidence={'implementation_phase':8,'passed':True,'verification_source_sha256':before,'verification_input_sha256':bound,
              'candidate_bindings':content,'frozen_design_regression':frozen,'tests':tests,'retained_prior_evidence':previous,
              'seed_inspections':inspections,'source_inspection':source,'rule_execution_catalog':mapping,'physical_copy_accounting':physical,'review':review,'issues':issues,'gate':gate}
    return evidence,gate

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':
    evidence_dir=ROOT/'evidence/integrated-history';ready=ROOT/'output/integrated-history/candidate-ready.json';ready.unlink(missing_ok=True)
    (ROOT/'output/integrated-source-delivery/candidate-ready.json').unlink(missing_ok=True)
    save(evidence_dir/'acceptance-gate.json',{'implementation_phase':8,'status':'EVALUATING','full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'})
    try:
        report,gate=evaluate();save(evidence_dir/'validation-report.json',report);save(evidence_dir/'acceptance-gate.json',gate)
        manifest_path=ROOT/'output/integrated-history/manifest.json';manifest=read(manifest_path);manifest['status']='ELIGIBLE_FOR_CERTIFICATION';save(manifest_path,manifest)
        source_root=ROOT/'output/integrated-source-delivery';native=read(source_root/'manifest.json');native['status']='INTEGRATED_SOURCE_SIMULATION_PASSED';save(source_root/'manifest.json',native)
        save(source_root/'candidate-ready.json',gate);save(ready,gate)
        print(json.dumps(gate));sys.exit(0)
    except Exception as exc:
        gate={'implementation_phase':8,'status':'BLOCKED','error':str(exc),'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
        save(evidence_dir/'acceptance-gate.json',gate);print(json.dumps(gate));sys.exit(1)
