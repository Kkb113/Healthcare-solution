"""Evaluate every final definition-of-done item without inventing owner approval."""
import argparse
from datetime import datetime, timezone
from pathlib import Path

from .common import ROOT, inventory, read, save, sha_file
from .package import DESCRIPTOR, verify_healthcare_release
from .registry import state
from .verification import retained_bindings, tool_bindings


def require_closed_critical_issues(register):
    if register['unresolved_p0_p1'] or any(
            issue['severity'] in ('P0', 'P1') and issue['status'] != 'CLOSED'
            for issue in register['issues']):
        raise ValueError('release issue register has unresolved P0/P1 defects')


def evaluate(package, registry, descriptor_sha256):
    package = Path(package).resolve();registry = Path(registry).resolve()
    verified = verify_healthcare_release(package, descriptor_sha256)
    certificate = read(package / 'evidence/certification.json')
    inspection = read(package / 'evidence/inspection.json')
    source = read(package / 'evidence/source-inspection.json')
    review_binding = read(package / 'evidence/review-binding.json')
    if review_binding['status'] != 'PASS' or not review_binding['reviewed_facts_unchanged'] or review_binding['selection']['reviewed_cases'] != 136:
        raise ValueError('fresh published-fact domain review binding failed')
    if inspection['status'] != 'PASS' or inspection['domain_checks'] != 58 or inspection['domain_defects'] or inspection['partitions'] != 324 or not all(c['passed'] for c in inspection['realism_checks']):
        raise ValueError('published full-population/realism checks incomplete')
    if inspection['consumer_controls']['unexplained_differences'] or inspection['point_in_time']['future_fact_failures'] or not inspection['point_in_time']['unknown_outcomes_preserved'] or len(inspection['point_in_time']['checks']) != 11:
        raise ValueError('published consumer/point-in-time checks failed')
    if source['status'] != 'PASS' or source['source_files'] != source['duplicate_deliveries_checked'] or source['source_files'] != 3444 or source['roundtrip_rows'] != 1936663 or source['challenge_copies'] != 22 or source['unexplained_differences']:
        raise ValueError('published native roundtrip/replay/count controls failed')
    if source['delivery_calendar']['snapshots_checked'] != 318 or source['delivery_calendar']['axiom_file_headers_reconciled_to_records'] != 304 or source['faults']['unresolved_release_blocking_faults'] or len(source['faults']['outcomes']) != 15 or not all(o['status']=='PASS' for o in source['faults']['outcomes']):
        raise ValueError('published calendars/fault outcomes incomplete')
    for name, meta in certificate['validation_artifacts'].items():
        p = package / 'evidence' / name
        if sha_file(p) != meta['sha256'] or p.stat().st_size != meta['bytes']:
            raise ValueError('fresh published-file validation artifact differs: ' + name)
    tests = read(ROOT / 'output/release-certification/release-tests.json')
    offline = read(ROOT / 'output/release-certification/offline-source-check.json')
    if not tests['passed'] or tests['failures'] or tests['errors'] or tests['skipped'] or not tests['tools_unchanged'] or not tests['inputs_unchanged']:
        raise ValueError('release-tool tests incomplete/failed')
    if tests['tool_bindings'] != tool_bindings() or tests['retained_prior_bindings'] != retained_bindings():
        raise ValueError('release-tool/prior-evidence test bindings are stale')
    for path, expected in tests['tool_bindings'].items():
        if path.startswith('release_tooling/'):
            target = package / 'reproducibility' / path
        elif path == 'tests/test_dataset_release.py':
            target = package / 'reproducibility' / path
        else:
            target = package / 'docs' / Path(path).name
        if sha_file(target) != expected:
            raise ValueError('distributed verifier/tests/docs differ from tested current files: ' + path)
    if offline['status'] != 'PASSED' or offline['descriptor_sha256'] != descriptor_sha256 or offline['tool_bindings'] != tests['tool_bindings']:
        raise ValueError('offline distribution verification incomplete/stale')
    if certificate['release_tool_bindings'] != tests['tool_bindings']:
        raise ValueError('certification tool/input bindings are stale')
    issues = read(ROOT / 'reviews/dataset-release-issues.json')
    require_closed_critical_issues(issues)
    if issues['descriptor_sha256'] != descriptor_sha256 or issues['offline_check_sha256'] != sha_file(ROOT / 'output/release-certification/offline-source-check.json'):
        raise ValueError('release issue closure evidence is stale')
    review = read(ROOT / 'reviews/dataset-release-review.json')
    if review['status'] != 'APPROVED_FOR_BUSINESS_OWNER_DECISION' or review['descriptor_sha256'] != descriptor_sha256 or review['limitations_sha256'] != sha_file(package / 'docs/limitations.md'):
        raise ValueError('final designated domain review missing or stale')
    if review['integrated_review_sha256'] != sha_file(package / 'reviews/integrated-history-review.json') or review['fresh_review_binding_sha256'] != sha_file(package / 'evidence/review-binding.json') or review['certification_sha256'] != sha_file(package / 'evidence/certification.json'):
        raise ValueError('final domain review is bound to different facts/evidence')
    expected_roles = {'IDENTITY','CLINICAL','OPERATIONS_WORKFORCE','FINANCE','DATA_ENGINEERING'}
    if set(review['reviewed_domains']) != expected_roles or review['external_professional_endorsement']:
        raise ValueError('required scoped domain reviews incomplete')
    current = state(package, registry, descriptor_sha256)
    owner_accepted = current['status'] == 'DATA_ACCEPTED'
    items = [
        ('phase_gates', True, 'Version-bound prior gates/evidence plus current release checks; final owner gate evaluated here'),
        ('history_scope_tables_and_cap', True, '25 tables, 36 months, three-year window, all actual counts and release allowance verified'),
        ('fictional_identity_and_event_age', True, 'Fresh full master/clinical checks and current hash-bound delegated identity review'),
        ('coherent_reviewed_longitudinal_histories', True, 'Fresh clinical/operations/resource checks on published files; unchanged reviewed facts'),
        ('historical_version_resolution', True, 'Source-known/delivery/effective selection and three historical native snapshots'),
        ('required_grain_reconciliations', True, 'Fresh six independent consumers, full financial/resource rules and native reports'),
        ('adverse_open_and_censored_outcomes', True, 'Fresh point-in-time checks preserve unknown outcomes and actual open histories'),
        ('source_contracts_and_roundtrip', True, 'All published native payloads reconstructed exactly; complete duplicate replay'),
        ('controlled_fault_detectors_and_recovery', True, '15 fresh fault/delivery outcomes and retained unchanged recovery regressions'),
        ('downstream_grains_and_no_future_leakage', True, 'Fresh six consumers and eleven point-in-time controls'),
        ('realism_and_repeat_seed_checks', True, 'Fresh published full-population profiles; unchanged three full-scale seed experiments retained'),
        ('no_critical_defect_or_unexplained_difference', True, 'Zero unresolved P0/P1 and zero unexplained state/monetary differences'),
        ('required_designated_reviews', True, 'All five required delegated synthetic-data review domains attached and bound'),
        ('clean_rebuild_and_actual_release_checksums', True, 'Seven cold lineage stages and complete staged/published payload verification'),
        ('complete_reproducible_release_package', True, 'Contracts, references, provenance, source bundle, pinned wheel, evidence and offline checks'),
        ('explicit_business_owner_acceptance', owner_accepted, 'Exact release descriptor and limitations hash accepted by the identified human owner')]
    passed = all(value for _, value, _ in items)
    outcome = 'PASSED' if passed else ('RETIRED' if current['status'] == 'RETIRED' else 'AWAITING_BUSINESS_ACCEPTANCE')
    gate = {'implementation_phase': 9, 'status': outcome,
            'evaluated_at': datetime.now(timezone.utc).isoformat(), 'release_id': verified['release_id'],
            'descriptor_sha256': descriptor_sha256, 'technical_certification': 'PASSED',
            'definition_of_done': [{'id': name, 'passed': value, 'evidence': text} for name, value, text in items],
            'fresh_release_tool_tests': tests['run'], 'fresh_published_domain_checks': certificate['domain_checks'],
            'cap_counted_release_rows': verified['cap_counted_release_rows'], 'business_tables': 25,
            'unresolved_p0_p1': 0, 'unexplained_differences': 0,
            'full_dataset_accepted': passed, 'foundation_status': 'DATA_ACCEPTED' if passed else 'BLOCKED_FOR_SOLUTION',
            'solution_status': 'DATA_ACCEPTED' if passed else 'BLOCKED_FOR_SOLUTION',
            'solution_implementation_started': False, 'separate_solution_authorization_required': True}
    evidence = {'gate': gate, 'published_payload_verification': verified, 'release_tool_tests': tests,
                'offline_distribution_check': offline, 'domain_review': review, 'release_issues': issues,
                'certification_sha256': sha_file(package / 'evidence/certification.json'),
                'payload_manifest_sha256': sha_file(package / 'payload-manifest.json'),
                'acceptance_record_sha256': sha_file(registry / verified['release_id'] / 'acceptance.json') if (registry / verified['release_id'] / 'acceptance.json').exists() else None,
                'retirement_record_sha256': sha_file(registry / verified['release_id'] / 'retirement.json') if (registry / verified['release_id'] / 'retirement.json').exists() else None,
                'certificate': certificate}
    save(ROOT / 'evidence/dataset-release/validation-report.json', evidence)
    save(ROOT / 'evidence/dataset-release/acceptance-gate.json', gate)
    return gate


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, required=True);p.add_argument('--registry', type=Path, required=True)
    p.add_argument('--descriptor-sha256', required=True);a = p.parse_args()
    try:
        result = evaluate(a.package, a.registry, a.descriptor_sha256)
    except Exception as exc:
        result = {'implementation_phase':9,'status':'BLOCKED','error':str(exc),'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
        save(ROOT / 'evidence/dataset-release/acceptance-gate.json',result)
        print(result);raise SystemExit(1)
    print(result)
    raise SystemExit(0 if result['status']=='PASSED' else 2)
