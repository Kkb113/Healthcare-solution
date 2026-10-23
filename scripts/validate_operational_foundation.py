"""Evaluate all Phase 4 exit criteria with current and exact accepted-history regressions."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.operational_pipeline import run_operations
from validate_operational_data import inspect_operations
from validate_phase0 import report as design_report

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')

def verification_hashes():
    paths=sorted((ROOT/'src/healthcare_synthetic').glob('*.py'))+sorted((ROOT/'tests').glob('*.py'))+sorted((ROOT/'scripts').glob('*.py'))
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def evaluate(output):
    before=verification_hashes();started=datetime.now(timezone.utc).isoformat()
    design=subprocess.run([sys.executable,str(ROOT/'scripts/build_phase0_spec.py'),'--check'],capture_output=True,text=True,timeout=60)
    regression=design_report();old=json.loads((ROOT/'evidence/phase-0/validation-report.json').read_text())['contract_sha256']
    print('Evaluating operational candidate and independent persisted controls',flush=True)
    manifest=run_operations(output_dir=output);independent=inspect_operations(output)
    groups=[];env=dict(os.environ,HEALTHCARE_OPERATIONAL_TEST_CANDIDATE=str(output))
    for group in ('framework-master','historical-clinical','operational'):
        report=output/(group+'-tests.json')
        print('Running '+group+' regression group',flush=True)
        cached=json.loads(report.read_text()) if report.exists() else None
        reusable=bool(cached and cached['passed'] and cached.get('verification_source_sha256')==before and cached.get('verification_sources_unchanged_during_tests') and (group!='operational' or cached.get('candidate_business_sha256')==manifest['business_sha256']))
        result=None if reusable else subprocess.run([sys.executable,str(ROOT/'scripts/run_foundation_regressions.py'),'--group',group,'--report',str(report)],cwd=ROOT,env=env,timeout=3600)
        if not report.exists():raise ValueError(group+' produced no test evidence')
        value=json.loads(report.read_text());groups.append(value)
        if result and result.returncode or not value['passed']:raise ValueError(group+' regression failed: '+json.dumps(value['failure_details']))
    all_cases=[case for group in groups for case in group['cases']]
    names={case['test'].split('.')[-1] for case in all_cases if case['status']=='PASS'}
    unchanged=before==verification_hashes()
    common=(design.returncode==0 and regression['passed'] and regression['contract_sha256']==old and unchanged
        and manifest['status']==independent['gate_status']=='OPERATIONAL_FLOW_PASSED' and not independent['defects']
        and independent['review']['status']=='PASS' and all(g['passed'] and g['skipped']==0 for g in groups))
    required={
      'normal_and_stress_flow_and_bed_invariants':['test_full_candidate_and_all_operational_checks','test_saturated_capacity_retains_waiting_demand_and_reservations','test_room_cohort_incompatibility_is_rejected','test_no_patient_can_occupy_two_beds','test_placement_before_clean_ready_is_rejected'],
      'zero_unexplained_reconciliation_differences':['test_occupied_seconds_match_two_independent_oracles','test_opening_cutoff_and_every_census_boundary_reconcile','test_internal_and_site_transfers_have_balanced_atomic_legs','test_late_duplicate_and_cancelled_reservation_replay_converges','test_correction_preserves_before_delivery_knowledge','test_independent_persisted_inspector_recomputes_controls'],
      'configured_queues_utilization_and_scenarios':['test_capacity_maintenance_turnaround_and_waits','test_surge_changes_connected_respiratory_cohorts','test_calendar_seasonality_and_facility_curves','test_daily_drivers_are_realized_only_after_local_day_end','test_unmet_capacity_transfers_retain_cause_and_observed_scope'],
      'recorded_operational_plausibility_review':['test_review_hundred_cases_is_content_bound','test_review_waits_use_chronological_first_placement','test_review_is_reproducible_from_reordered_persisted_rows','test_clean_end_to_end_rebuild_and_cached_resume','test_actual_process_crash_rolls_back_then_resumes','test_corrupt_checkpoint_fails_closed','test_changed_seed_invalidates_children_before_a_failed_recompute']}
    exits={key:{'passed':common and set(tests)<=names,'evidence_tests':tests} for key,tests in required.items()}
    passed=common and all(e['passed'] for e in exits.values())
    evidence={'implementation_phase':4,'evaluated_at':started,'scope':'Capacity-integrated synthetic data foundation; workforce, inventory, finance and source release remain future phases',
        'design_artifacts_current':design.returncode==0,'design_regression':regression,'frozen_design_hashes_unchanged':regression['contract_sha256']==old,
        'verification_sources_unchanged_during_evaluation':unchanged,'verification_source_sha256':before,'test_groups':groups,
        'tests_run':sum(g['run'] for g in groups),'manifest':manifest,'independent_validation':independent,'review_decision':json.loads((ROOT/'reviews/operational-flow-review.json').read_text()),
        'exit_criteria':exits,'passed':passed,'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
    gate={'implementation_phase':4,'status':'PASSED' if passed else 'BLOCKED','evaluated_at':started,'exit_criteria':exits,'tests_run':evidence['tests_run'],
        'clinical_check_groups':len(independent['clinical']['checks']),'operational_check_groups':len(independent['operations']['checks']),
        'business_sha256':manifest['business_sha256'],'accepted_clinical_sha256':manifest['locks']['accepted_clinical_sha256'],
        'business_rows':manifest['business_rows'],'rows_by_table':manifest['rows_by_table'],'generated_business_tables':16,'release_business_tables':25,
        'remaining_planned_rows':manifest['remaining_planned_rows'],'reserve_rows':41790,'operational_metrics':independent['operations']['metrics'],
        'reviewed_operational_cases':independent['review']['cases'],'licensed_clinical_endorsement':False,'full_dataset_accepted':False,
        'solution_status':'BLOCKED_FOR_SOLUTION','next_phase':'Workforce, resources and inventory - not started'}
    return evidence,gate

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/operational-flow');a=p.parse_args()
    report=ROOT/'evidence/operational-flow/validation-report.json';gate_path=ROOT/'evidence/operational-flow/acceptance-gate.json'
    pending={'implementation_phase':4,'status':'EVALUATING','full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
    write(report,pending);write(gate_path,pending)
    try:evidence,gate=evaluate(a.output.resolve())
    except Exception as exc:evidence=gate={**pending,'status':'BLOCKED','error':str(exc)}
    write(report,evidence);write(gate_path,gate);print(json.dumps({k:gate[k] for k in ('implementation_phase','status','tests_run','business_rows','error') if k in gate}))
    sys.exit(0 if gate['status']=='PASSED' else 1)
