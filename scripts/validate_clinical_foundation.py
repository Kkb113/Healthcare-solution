"""Evaluate clinical exit criteria, independent persisted inspection and all repository regressions."""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from healthcare_synthetic.clinical_pipeline import run_clinical
from validate_clinical_data import inspect_clinical
from validate_phase0 import report as design_report
from validate_phase1 import RecordingResult

class ProgressResult(RecordingResult):
    def startTest(self, test):
        super().startTest(test)
        if any(name in test.id() for name in ('clean_rebuild', 'real_process_crash', 'exact_git_revision', 'changed_clinical_seed', 'independent_persisted')):
            print('Verifying: ' + test.id().split('.')[-1], flush=True)

    def addSuccess(self, test):
        super().addSuccess(test)
        if self.testsRun % 10 == 0:
            print(f'Verification progress: {self.testsRun} cases evaluated', flush=True)

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def evaluate(output):
    evidence = {'implementation_phase': 3, 'evaluated_at': datetime.now(timezone.utc).isoformat(),
                'scope': 'Full cohort provisional longitudinal clinical histories; no resource-constrained release or analytics solution',
                'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION'}
    design = subprocess.run([sys.executable, str(ROOT / 'scripts/build_phase0_spec.py'), '--check'], capture_output=True, text=True, timeout=30)
    evidence['design_artifacts_current'] = design.returncode == 0
    evidence['design_regression'] = design_report()
    old = json.loads((ROOT / 'evidence/phase-0/validation-report.json').read_text())['contract_sha256']
    evidence['frozen_design_hashes_unchanged'] = evidence['design_regression']['contract_sha256'] == old
    manifest = run_clinical(output_dir=output)
    independent = inspect_clinical(output)
    previous_candidate = os.environ.get('HEALTHCARE_CLINICAL_TEST_CANDIDATE')
    os.environ['HEALTHCARE_CLINICAL_TEST_CANDIDATE'] = str(output)
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    log = io.StringIO()
    results = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=ProgressResult).run(suite)
    if previous_candidate is None: os.environ.pop('HEALTHCARE_CLINICAL_TEST_CANDIDATE', None)
    else: os.environ['HEALTHCARE_CLINICAL_TEST_CANDIDATE'] = previous_candidate
    evidence['tests'] = {'run': results.testsRun, 'passed': results.wasSuccessful() and not results.skipped,
                         'failed': len(results.failures), 'errors': len(results.errors), 'skipped': len(results.skipped), 'cases': results.records,
                         'failure_details': [message for _, message in results.failures + results.errors]}
    if not evidence['tests']['passed']: print(log.getvalue())
    passed_names = {r['test'].split('.')[-1] for r in results.records if r['status'] == 'PASS'}
    required = {
      'all_hard_clinical_identity_chronology_terminology_rules': ['test_complete_cohort_and_all_hard_clinical_checks', 'test_accepted_master_records_are_preserved_exactly', 'test_prebirth_and_postdeath_care_are_rejected', 'test_lab_collection_and_result_availability_are_enforced', 'test_terminology_release_domain_and_unit_are_enforced', 'test_allergy_withholding_never_consumes_stock', 'test_notes_are_fact_grounded_and_reject_unsupported_prose'],
      'pathways_and_boundaries_in_candidate_fixtures_and_sample': ['test_correlated_trajectories_and_adverse_cases_are_present', 'test_cutoff_censoring_and_readmission_denominator', 'test_appointment_no_show_cancellation_and_reschedule_chronology', 'test_condition_resolution_never_leaks_into_initial_assertion', 'test_stratified_hundred_journey_review_is_content_bound'],
      'at_least_100_stratified_longitudinal_journeys_reviewed': ['test_stratified_hundred_journey_review_is_content_bound', 'test_note_result_and_future_fact_mutations_are_rejected'],
      'designated_domain_review_scope_and_result_recorded': ['test_stratified_hundred_journey_review_is_content_bound', 'test_validator_is_independent_of_generation_and_serializer'],
      'end_to_end_reproducibility_recovery_and_independent_validation': ['test_full_clean_rebuild_and_cached_resume_are_identical', 'test_real_process_crash_rolls_back_validation_then_resumes', 'test_checkpoint_corruption_fails_closed', 'test_independent_persisted_inspector_recomputes_all_rules', 'test_accepted_master_can_be_rebuilt_from_exact_git_revision']}
    decision = json.loads((ROOT / 'reviews/clinical-journey-review.json').read_text())
    common = (design.returncode == 0 and evidence['design_regression']['passed'] and evidence['frozen_design_hashes_unchanged'] and evidence['tests']['passed']
              and manifest['status'] == independent['gate_status'] == 'CLINICAL_HISTORIES_PASSED' and not independent['defects']
              and independent['review']['status'] == 'PASS' and decision['licensed_clinical_endorsement'] is False)
    exits = {name: {'passed': common and set(names) <= passed_names, 'evidence_tests': names} for name, names in required.items()}
    evidence.update(manifest=manifest, independent_validation=independent, review_decision=decision, exit_criteria=exits, passed=common and all(e['passed'] for e in exits.values()))
    paths = sorted((ROOT / 'tests').glob('*.py')) + [ROOT / ('scripts/' + n) for n in ('generate_clinical_histories.py', 'validate_clinical_data.py', 'validate_clinical_foundation.py', 'restore_master_snapshot.py')]
    evidence['verification_source_sha256'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    gate = {'implementation_phase': 3, 'status': 'PASSED' if evidence['passed'] else 'BLOCKED', 'evaluated_at': evidence['evaluated_at'], 'exit_criteria': exits,
            'tests_run': results.testsRun, 'clinical_checks': len(independent['checks']), 'business_rows': manifest['business_rows'], 'rows_by_table': manifest['rows_by_table'],
            'generated_business_tables': manifest['generated_business_tables'], 'release_business_tables': 25, 'reviewed_longitudinal_journeys': independent['review']['journeys'],
            'business_sha256': manifest['business_sha256'], 'master_business_sha256': manifest['locks']['master_business_sha256'],
            'remaining_planned_rows': manifest['remaining_planned_rows'], 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION',
            'trajectory_status': manifest['trajectory_status'], 'licensed_clinical_endorsement': False, 'next_phase': 'Demand, patient flow and beds - not started'}
    return evidence, gate

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT / 'output/clinical-histories')
    p.add_argument('--report', type=Path, default=ROOT / 'evidence/clinical-histories/validation-report.json')
    p.add_argument('--gate', type=Path, default=ROOT / 'evidence/clinical-histories/acceptance-gate.json')
    a = p.parse_args()
    pending = {'implementation_phase': 3, 'status': 'EVALUATING', 'passed': False, 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION'}
    write(a.report, pending); write(a.gate, pending)
    try: evidence, gate = evaluate(a.output)
    except Exception as exc: evidence = gate = {**pending, 'status': 'BLOCKED', 'error': str(exc)}
    write(a.report, evidence); write(a.gate, gate)
    print(json.dumps({k: gate[k] for k in ('implementation_phase', 'status', 'tests_run', 'business_rows', 'error') if k in gate}))
    return 0 if gate['status'] == 'PASSED' else 1

if __name__ == '__main__': sys.exit(main())
