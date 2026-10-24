"""Independent persisted-file inspection or final four-exit source simulation gate."""
import argparse
import hashlib
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))
from healthcare_synthetic.engine import atomic_json
from healthcare_synthetic.source_layouts import read
from healthcare_synthetic.source_validation import inspect_sources
from healthcare_synthetic.source_faults import exercise_faults
from healthcare_synthetic.source_export import footprint
from run_source_regressions import package_digest, input_hashes, verification_hashes


def retained_prior_evidence():
    prior = read(ROOT / 'evidence/financial-history/validation-report.json')
    gate = read(ROOT / 'evidence/financial-history/acceptance-gate.json')
    differences = [p for mapping in ('verification_source_sha256', 'verification_input_sha256')
                   for p, expected in prior[mapping].items() if footprint(ROOT / p)['sha256'] != expected]
    if differences or not prior['passed'] or gate['status'] != 'PASSED' or prior['tests_run'] != 280:
        raise ValueError('accepted prior source/input/test evidence changed: ' + str(differences))
    return {'status': 'PASS', 'retained_tests': 280, 'changed_preexisting_sources_or_inputs': differences,
            'scope': 'Existing domain implementation, frozen contracts, accepted reviews and 280-test Phase 6 evidence are byte-identical. New source modules/scripts/tests are independently tested in this phase. Prior tests are retained, not reported as newly rerun.',
            'accepted_business_sha256': gate['business_sha256']}


def evaluate(output):
    output = Path(output).resolve(); (output / 'candidate-ready.json').unlink(missing_ok=True)
    sources = verification_hashes(); inputs = input_hashes(); candidate = package_digest(output)
    from validate_phase0 import report as frozen_report
    frozen = frozen_report()
    if not frozen['passed'] or frozen['check_count'] != 41:
        raise ValueError('frozen design/document linkage regression failed')
    tests = read(output / 'source-tests.json')
    expected_tests = sum(unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern).countTestCases()
                         for pattern in ('test_source_delivery.py', 'test_phase1_sources.py'))
    if not tests['passed'] or tests['failed'] or tests['errors'] or tests['skipped'] or tests['run'] != expected_tests or tests['verification_source_sha256'] != sources or tests['verification_input_sha256'] != inputs or tests['candidate_source_package_sha256'] != candidate or not tests['candidate_unchanged_during_tests']:
        raise ValueError('complete current source regression evidence is absent/stale/failed')
    required_cases = ['full_history_all_files', 'clean_full_export_rebuild', 'real_export_process_crash', 'real_replay_process_death', 'all_published_critical_faults']
    records = json.dumps(tests['cases'])
    if any(case not in records for case in required_cases):
        raise ValueError('required end-to-end/recovery tests missing')
    inspection_file = output / 'independent-inspection.json'
    if footprint(inspection_file)['sha256'] != tests['inspection_artifact_sha256']:
        raise ValueError('independent persisted inspection evidence changed')
    inspected = read(inspection_file)
    if inspected['status'] != 'PASS' or inspected['unexplained_differences'] or inspected['roundtrip_rows'] != 1924164 or inspected['duplicate_deliveries_checked'] != inspected['source_files']:
        raise ValueError('source roundtrip inspection incomplete')
    if inspected.get('delivery_calendar', {}).get('status') != 'PASS' or inspected['delivery_calendar']['snapshots_checked'] != 318:
        raise ValueError('independent expected-calendar/snapshot evidence incomplete')
    prior = retained_prior_evidence(); package = read(output / 'challenge-manifest.json')
    faults = exercise_faults(output, package, output / 'fault-replay'); review = read(ROOT / 'reviews/source-delivery-review.json')
    from review_source_delivery import render
    body, selection = render(output)
    if (ROOT / 'reviews/source-delivery-sample.md').read_bytes() != body.encode() or any(review[k] != v for k, v in selection.items()):
        raise ValueError('recorded native source review sample/selection differs')
    if review['decision'] != 'ACCEPT_SUBJECT_TO_PASSING_TECHNICAL_GATES' or review['source_package_sha256'] != candidate or len(review['reviewed_layout_families']) != 12 or not review['record_budget_accepted'] or not review['limitations_accepted']:
        raise ValueError('source engineering review missing or stale')
    exits = {
        'all_source_contracts_roundtrips_delivery_scenarios_and_critical_faults_pass': inspected['status'] == faults['status'] == 'PASS',
        'zero_unexplained_canonical_export_differences': inspected['unexplained_differences'] == 0,
        'published_challenge_histories_within_allocated_allowance': package['published_challenge_record_copies'] <= 64 and inspected['cap_counted_release_rows'] <= 2000000,
        'source_simulation_complete_production_integration_and_solution_unbuilt': review['production_integrations_built'] is False and review['solution_built'] is False}
    if verification_hashes() != sources or input_hashes() != inputs or package_digest(output) != candidate:
        raise ValueError('source/input/candidate changed during final evaluation')
    passed = all(exits.values()); gate = {'implementation_phase': 7, 'status': 'PASSED' if passed else 'BLOCKED',
        'evaluated_at': datetime.now(timezone.utc).isoformat(), 'exit_criteria': exits, 'fresh_source_tests_run': tests['run'],
        'new_source_tests_run': tests['run'] - 12, 'legacy_source_tests_rerun': 12, 'prior_and_fresh_test_counts_overlap': 12,
        'retained_prior_tests': 280, 'business_rows': 1924164, 'business_tables': 25,
        'published_challenge_record_copies': package['published_challenge_record_copies'],
        'cap_counted_release_rows': inspected['cap_counted_release_rows'], 'source_files': inspected['source_files'],
        'source_package_sha256': candidate, 'canonical_business_sha256': prior['accepted_business_sha256'],
        'critical_fault_and_delivery_outcomes': len(faults['outcomes']), 'unresolved_release_blocking_faults': 0,
        'native_review_cases': review['reviewed_cases'], 'review_mirror_rows': review['review_mirror_rows'],
        'review_scalar_fact_mirrors': review['review_scalar_fact_mirrors'],
        'source_review': 'USER_DESIGNATED_SYNTHETIC_DATA_ENGINEERING_REVIEW', 'vendor_certified': False,
        'production_integrations_built': False, 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION',
        'next_phase': 'Full-history reconciliation and downstream contract validation - not started'}
    evidence = {'implementation_phase': 7, 'passed': passed, 'verification_source_sha256': sources,
        'frozen_design_regression': frozen,
        'verification_input_sha256': inputs, 'source_package_sha256': candidate, 'tests': tests,
        'retained_prior_evidence': prior, 'independent_inspection': inspected, 'fault_dispositions': faults,
        'review': review, 'exit_criteria': exits, 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION'}
    if passed:
        manifest = read(output / 'manifest.json'); manifest['status'] = 'SOURCE_SIMULATION_PASSED'
        atomic_json(output / 'manifest.json', manifest)
        atomic_json(output / 'candidate-ready.json', gate)
    return evidence, gate


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, default=ROOT / 'output/source-delivery')
    p.add_argument('--inspect-only', action='store_true'); p.add_argument('--report', type=Path); a = p.parse_args()
    try:
        if a.inspect_only:
            result = inspect_sources(a.output)
            if a.report:
                atomic_json(a.report, result)
        else:
            report = ROOT / 'evidence/source-delivery/validation-report.json'; gate_path = ROOT / 'evidence/source-delivery/acceptance-gate.json'
            atomic_json(gate_path, {'implementation_phase': 7, 'status': 'EVALUATING', 'full_dataset_accepted': False})
            evidence, result = evaluate(a.output); atomic_json(report, evidence); atomic_json(gate_path, result)
        print(json.dumps({k: result[k] for k in ('status', 'fresh_source_tests_run', 'roundtrip_rows', 'source_files') if k in result}))
        sys.exit(0 if result['status'] in ('PASS', 'PASSED') else 1)
    except Exception as exc:
        result = {'implementation_phase': 7, 'status': 'BLOCKED', 'error': str(exc), 'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION'}
        if not a.inspect_only:
            atomic_json(ROOT / 'evidence/source-delivery/acceptance-gate.json', result)
        print(json.dumps(result)); sys.exit(1)
