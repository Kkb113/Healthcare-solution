"""Evaluate all four financial exit criteria, independent controls and end-to-end tests."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.financial_pipeline import run_financial
from validate_financial_data import inspect_financial
from run_foundation_regressions import verification_hashes
from run_financial_regressions import input_hashes
from validate_phase0 import report as design_report


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def evaluate(output):
    source_before=verification_hashes();inputs_before=input_hashes();started=datetime.now(timezone.utc).isoformat()
    design=subprocess.run([sys.executable,str(ROOT/'scripts/build_phase0_spec.py'),'--check'],capture_output=True,text=True,timeout=60)
    frozen=design_report();prior=read(ROOT/'evidence/phase-0/validation-report.json')['contract_sha256']
    print('Evaluating financial generation and independent persisted-file/source controls',flush=True)
    manifest=run_financial(output_dir=output);independent=inspect_financial(output)
    env=dict(os.environ,HEALTHCARE_FINANCIAL_TEST_CANDIDATE=str(output));groups=[]
    for group in ('financial','framework-master','historical-clinical','operational','resource'):
        report=output/(group+'-tests.json');cached=read(report) if report.exists() else None
        reusable=bool(cached and cached['passed'] and cached.get('verification_source_sha256')==source_before and cached.get('verification_input_sha256')==inputs_before
            and cached.get('verification_sources_unchanged_during_tests') and cached.get('verification_inputs_unchanged_during_tests')
            and (group!='financial' or cached.get('candidate_business_sha256')==manifest['business_sha256']))
        print(('Reusing verified ' if reusable else 'Running ')+group+' regression group',flush=True)
        completed=None if reusable else subprocess.run([sys.executable,str(ROOT/'scripts/run_financial_regressions.py'),'--group',group,'--report',str(report)],cwd=ROOT,env=env,timeout=7200)
        if not report.exists():raise ValueError(group+' did not produce test evidence')
        result=read(report);groups.append(result)
        if completed and completed.returncode or not result['passed']:raise ValueError(group+' regressions failed: '+json.dumps(result['failure_details']))
    names={r['test'].split('.')[-1] for g in groups for r in g['cases'] if r['status']=='PASS'}
    unchanged=source_before==verification_hashes() and inputs_before==input_hashes();decision=read(ROOT/'reviews/financial-history-review.json')
    common=bool(design.returncode==0 and frozen['passed'] and frozen['contract_sha256']==prior and unchanged
        and manifest['status']==independent['gate_status']=='FINANCIAL_HISTORY_PASSED' and not independent['defects']
        and independent['review']['status']=='PASS' and independent['review']['cases']>=50 and all(g['passed'] and not g['skipped'] for g in groups))
    required={
        'all_monetary_reconciliations_pass_at_stored_precision':[
            'test_all_financial_controls_and_exact_budget_pass','test_balanced_but_false_journal_fails_independent_source_oracle',
            'test_inventory_purchase_consumption_and_closing_asset_reconcile','test_labor_revisions_salary_and_unfinished_shift_accrual_are_costed',
            'test_billed_plus_unbilled_ar_equals_enterprise_control','test_treasury_settles_known_obligations_and_cash_stays_funded','test_direct_and_pooled_expense_is_counted_once','test_monthly_movement_and_closing_balances_reconcile'],
        'at_least_fifty_complete_stratified_financial_traces_reviewed':['test_review_has_sixty_complete_bound_stratified_traces','test_pending_denial_is_not_an_automatic_writeoff',
            'test_refunds_reversals_and_posting_links_have_opposite_effect','test_denial_denominator_uses_original_insured_observed_claims'],
        'designated_finance_reviewer_accepts_accounting_allocation_and_reconciliation':['test_review_has_sixty_complete_bound_stratified_traces','test_allocation_vintages_are_selected_not_added'],
        'no_unresolved_critical_financial_or_historical_availability_defects':[
            'test_forecast_and_budget_recompute_from_known_information','test_future_postings_and_worker_corrections_cannot_change_earlier_plan',
            'test_header_does_not_publish_future_first_submission','test_no_postcutoff_economic_events_are_invented','test_duplicate_delivery_is_idempotent_and_conflicting_duplicate_rejected',
            'test_clean_rebuild_cached_resume_and_complete_hash_match','test_real_process_crash_rolls_back_and_resumes',
            'test_changed_seed_invalidates_descendants_before_injected_failure','test_corrupt_checkpoint_cannot_publish_ready','test_parent_histories_remain_byte_identical']}
    exits={name:{'passed':common and set(tests)<=names,'evidence_tests':tests} for name,tests in required.items()}
    passed=common and all(v['passed'] for v in exits.values());amendment=read(ROOT/'contracts/financial-history-policy.json')['record_budget_amendment']
    evidence={'implementation_phase':6,'evaluated_at':started,'scope':'Selected facility financial histories, source-derived journals/costs and canonical Axiom vintages; source export replay and the analytics solution remain later phases',
        'design_artifacts_current':design.returncode==0,'frozen_design_regression':frozen,'frozen_design_hashes_unchanged':frozen['contract_sha256']==prior,
        'reviewed_budget_amendment':amendment,'verification_sources_and_inputs_unchanged_during_evaluation':unchanged,
        'verification_source_sha256':source_before,'verification_input_sha256':inputs_before,'test_groups':groups,'tests_run':sum(g['run'] for g in groups),
        'manifest':manifest,'independent_validation':independent,'review_decision':decision,'exit_criteria':exits,'passed':passed,
        'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
    gate={'implementation_phase':6,'status':'PASSED' if passed else 'BLOCKED','evaluated_at':started,'exit_criteria':exits,'tests_run':evidence['tests_run'],
        'financial_check_groups':len(independent['checks']),'business_sha256':manifest['business_sha256'],'accepted_resource_sha256':manifest['locks']['accepted_resource_sha256'],
        'business_rows':manifest['business_rows'],'rows_by_table':manifest['rows_by_table'],'generated_business_tables':25,'planned_record_envelope':1995215,'reserve_rows':4785,
        'financial_metrics':independent['metrics'],'reviewed_financial_traces':independent['review']['cases'],'independent_accountant_endorsement':False,
        'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION','next_phase':'Source-system exports and delivery simulation - not started'}
    return evidence,gate


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/financial-history');a=p.parse_args()
    report=ROOT/'evidence/financial-history/validation-report.json';gate_path=ROOT/'evidence/financial-history/acceptance-gate.json'
    pending={'implementation_phase':6,'status':'EVALUATING','full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'};write(report,pending);write(gate_path,pending)
    try:evidence,gate=evaluate(a.output.resolve())
    except Exception as exc:evidence=gate={**pending,'status':'BLOCKED','error':str(exc)}
    write(report,evidence);write(gate_path,gate);print(json.dumps({k:gate[k] for k in ('implementation_phase','status','tests_run','business_rows','error') if k in gate}));sys.exit(0 if gate['status']=='PASSED' else 1)
