"""Evaluate every Phase 5 exit criterion with independent persisted checks and tests."""
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
from healthcare_synthetic.resource_pipeline import run_resources
from validate_resource_data import inspect_resources
from run_foundation_regressions import verification_hashes
from run_resource_regressions import input_hashes
from validate_phase0 import report as design_report


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def evaluate(output):
    source_before=verification_hashes();inputs_before=input_hashes();started=datetime.now(timezone.utc).isoformat()
    design=subprocess.run([sys.executable,str(ROOT/'scripts/build_phase0_spec.py'),'--check'],capture_output=True,text=True,timeout=60)
    frozen=design_report();prior=json.loads((ROOT/'evidence/phase-0/validation-report.json').read_text())['contract_sha256']
    print('Evaluating connected resource candidate and independently persisted controls',flush=True)
    manifest=run_resources(output_dir=output);independent=inspect_resources(output)
    groups=[];env=dict(os.environ,HEALTHCARE_RESOURCE_TEST_CANDIDATE=str(output))
    for group in ('framework-master','historical-clinical','operational','resource'):
        report=output/(group+'-tests.json');cached=json.loads(report.read_text()) if report.exists() else None
        reusable=bool(cached and cached['passed'] and cached.get('verification_source_sha256')==source_before and cached.get('verification_input_sha256')==inputs_before
            and cached.get('verification_sources_unchanged_during_tests') and cached.get('verification_inputs_unchanged_during_tests')
            and (group!='resource' or cached.get('candidate_business_sha256')==manifest['business_sha256']))
        print(('Reusing verified ' if reusable else 'Running ')+group+' regression group',flush=True)
        completed=None if reusable else subprocess.run([sys.executable,str(ROOT/'scripts/run_resource_regressions.py'),'--group',group,'--report',str(report)],cwd=ROOT,env=env,timeout=3600)
        if not report.exists():raise ValueError(group+' produced no test evidence')
        result=json.loads(report.read_text());groups.append(result)
        if completed and completed.returncode or not result['passed']:raise ValueError(group+' regression failed: '+json.dumps(result['failure_details']))
    names={r['test'].split('.')[-1] for g in groups for r in g['cases'] if r['status']=='PASS'}
    unchanged=source_before==verification_hashes() and inputs_before==input_hashes()
    common=bool(design.returncode==0 and frozen['passed'] and frozen['contract_sha256']==prior and unchanged
        and manifest['status']==independent['gate_status']=='RESOURCE_FOUNDATION_PASSED' and not independent['defects']
        and independent['review']['status']=='PASS' and all(g['passed'] and not g['skipped'] for g in groups))
    required={
        'labor_cost_stock_balance_and_resource_link_controls':[
            'test_all_labor_and_stock_controls_pass','test_overtime_is_a_paid_subset','test_labor_costs_recompute_from_rates_once',
            'test_stock_quantity_and_value_roll_forwards','test_point_of_use_stock_and_clinical_group_quantities_reconcile'],
        'no_unexplained_negative_stock_or_untraceable_cost':[
            'test_issue_before_receipt_is_rejected','test_expired_lot_is_rejected_at_point_of_use','test_wrong_price_and_pack_conversion_are_rejected',
            'test_wrong_labor_rate_is_rejected','test_unbalanced_transfer_or_return_is_rejected'],
        'connected_normal_shortage_absence_agency_and_stockout_scenarios':[
            'test_absence_and_agency_have_distinct_attendance_and_cost','test_shortages_change_actual_services_without_stale_facts',
            'test_declared_stockouts_are_probed_before_case_cart_arrival','test_operative_concurrency_requires_actual_rn_coverage',
            'test_future_roster_actuals_are_rejected','test_forecast_cancellations_and_unknown_early_history_are_explicit'],
        'changed_clinical_and_operational_histories_pass_again':[
            'test_all_fifteen_clinical_and_seven_operational_groups_pass','test_clinical_authors_have_actual_qualified_attendance',
            'test_source_attending_and_all_bed_histories_are_preserved','test_review_is_hundred_case_content_bound_and_order_invariant',
            'test_independent_persisted_files_and_mirrors','test_clean_rebuild_cached_resume_and_complete_hash_match',
            'test_real_process_crash_rolls_back_and_resumes','test_changed_seed_invalidates_descendants_before_failure','test_corrupt_checkpoint_cannot_publish_ready']}
    exits={name:{'passed':common and set(tests)<=names,'evidence_tests':tests} for name,tests in required.items()}
    passed=common and all(v['passed'] for v in exits.values())
    evidence={'implementation_phase':5,'evaluated_at':started,'scope':'Selected source workforce, clinical resource linkage and stock foundation; financial postings and source release remain future phases',
        'design_artifacts_current':design.returncode==0,'design_regression':frozen,'frozen_design_hashes_unchanged':frozen['contract_sha256']==prior,
        'verification_sources_and_inputs_unchanged_during_evaluation':unchanged,'verification_source_sha256':source_before,'verification_input_sha256':inputs_before,
        'test_groups':groups,'tests_run':sum(g['run'] for g in groups),'manifest':manifest,'independent_validation':independent,
        'review_decision':json.loads((ROOT/'reviews/resource-foundation-review.json').read_text()),'exit_criteria':exits,'passed':passed,
        'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
    gate={'implementation_phase':5,'status':'PASSED' if passed else 'BLOCKED','evaluated_at':started,'exit_criteria':exits,'tests_run':evidence['tests_run'],
        'clinical_check_groups':len(independent['clinical']['checks']),'operational_check_groups':len(independent['operations']['checks']),
        'labor_check_groups':len(independent['workforce']['checks']),'stock_check_groups':len(independent['stock']['checks']),
        'business_sha256':manifest['business_sha256'],'accepted_operational_sha256':manifest['locks']['accepted_operational_sha256'],
        'business_rows':manifest['business_rows'],'rows_by_table':manifest['rows_by_table'],'generated_business_tables':18,'release_business_tables':25,
        'remaining_planned_rows':manifest['remaining_planned_rows'],'reserve_rows':41790,'workforce_metrics':independent['workforce']['metrics'],
        'stock_metrics':independent['stock']['metrics'],'reviewed_resource_cases':independent['review']['cases'],'licensed_clinical_endorsement':False,
        'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION','next_phase':'Revenue cycle and financial reconciliation - not started'}
    return evidence,gate


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/resource-foundation');a=p.parse_args()
    report=ROOT/'evidence/resource-foundation/validation-report.json';gate_path=ROOT/'evidence/resource-foundation/acceptance-gate.json'
    pending={'implementation_phase':5,'status':'EVALUATING','full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
    write(report,pending);write(gate_path,pending)
    try:evidence,gate=evaluate(a.output.resolve())
    except Exception as exc:evidence=gate={**pending,'status':'BLOCKED','error':str(exc)}
    write(report,evidence);write(gate_path,gate);print(json.dumps({k:gate[k] for k in ('implementation_phase','status','tests_run','business_rows','error') if k in gate}));sys.exit(0 if gate['status']=='PASSED' else 1)
