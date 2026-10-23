"""Full-cohort clinical checks, deliberately invalid histories and real process recovery."""
import ast
import copy
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from healthcare_synthetic.clinical_pipeline import GRAPH, load_master, run_clinical
from healthcare_synthetic.clinical_review import render_journeys, review_gate
from healthcare_synthetic.clinical_validation import ClinicalValidator
from healthcare_synthetic.core import age_on
from validate_clinical_data import inspect_clinical


class ClinicalHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads((ROOT / 'config/clinical-history-generation.json').read_text())
        cls.policy = json.loads((ROOT / 'contracts/clinical-history-policy.json').read_text())
        cls.master, cls.schema, _ = load_master(cls.cfg)
        cls.base = Path(os.environ.get('HEALTHCARE_CLINICAL_TEST_CANDIDATE', str(ROOT / 'output/clinical-histories')))
        if not (cls.base / 'canonical/clinical-event.jsonl').exists(): run_clinical(output_dir=cls.base)
        cls.manifest = json.loads((cls.base / 'manifest.json').read_text())
        if cls.manifest['status'] not in ('CLINICAL_HISTORIES_PASSED', 'REVIEW_PENDING', 'BLOCKED'):
            raise RuntimeError('Finish clinical generation before running full-cohort tests')
        cls.tables = {}
        for table, meta in cls.manifest['canonical_files'].items():
            with (cls.base / meta['file']).open(encoding='utf-8') as stream:
                cls.tables[table] = [json.loads(line) for line in stream]
        cls.checked = ClinicalValidator(cls.tables, cls.schema, cls.cfg, cls.policy, cls.master).run()
        cls.temp = tempfile.TemporaryDirectory(prefix='clinical-tests-', dir=ROOT / 'output')
        cls.work = Path(cls.temp.name)
        cls.event_positions = {r['clinical_event_version_id']: i for i, r in enumerate(cls.tables['clinical_event'])}
        cls.events = cls.tables['clinical_event']
        cls.validate_catalog = {r['catalog_item_id']: r for r in cls.tables['catalog_item']}
        cls.med = next(i for i, r in enumerate(cls.events) if r['event_type'] == 'MED_ADMIN' and r['status'] == 'COMPLETED')
        cls.lab = next(i for i, r in enumerate(cls.events) if r['event_type'] == 'LAB_RESULT')
        cls.note = next(i for i, r in enumerate(cls.events) if r['event_type'] == 'DOCUMENT')

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def validate(self, tables=None): return ClinicalValidator(tables or self.tables, self.schema, self.cfg, self.policy, self.master)

    def fault(self, group, table, index, updates, message):
        tables = dict(self.tables)
        tables[table] = list(tables[table])
        tables[table][index] = {**tables[table][index], **updates}
        result = self.validate(tables).check(group)
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertIn(message, result['failures'][0]['reason'])
        self.assertTrue(result['failures'][0]['record_key'])

    def test_complete_cohort_and_all_hard_clinical_checks(self):
        self.assertEqual(self.checked['status'], 'CLINICAL_CHECKS_PASSED', self.checked['defects'])
        self.assertEqual(len(self.checked['checks']), 15)
        self.assertEqual(self.checked['metrics']['encounter_classes'], {'IPD': 12000, 'ED': 27000, 'OPD': 17000})
        self.assertEqual(len(self.tables), 14)
        self.assertFalse(self.manifest['full_dataset_accepted'])
        self.assertEqual(self.manifest['trajectory_status'], 'PROVISIONAL_PENDING_RESOURCE_INTEGRATION')

    def test_accepted_master_records_are_preserved_exactly(self):
        self.assertEqual(self.validate().check('MASTER_PRESERVATION')['status'], 'PASS')
        self.fault('MASTER_PRESERVATION', 'patient', 0, {'given_name': 'Generic Patient'}, 'changed or removed')

    def test_full_schema_and_required_source_fields(self):
        self.fault('SCHEMA', 'clinical_event', self.med, {'dose_quantity': 650.0}, 'wrong type/scale')
        self.fault('AVAILABILITY', 'clinical_event', self.med, {'source_system': 'FABRIC'}, 'wrong source authority')

    def test_duplicate_event_identity_is_rejected(self):
        self.fault('KEYS', 'clinical_event', 1, {'source_record_id': self.events[0]['source_record_id']}, 'duplicate source')

    def test_orphan_order_and_cross_encounter_order_are_rejected(self):
        self.fault('REFERENCES', 'clinical_event', self.lab, {'parent_event_version_id': 'missing-order'}, 'orphan')
        other = next(r for r in self.events if r['event_type'] == 'ORDER' and r['encounter_version_id'] != self.events[self.lab]['encounter_version_id'])
        self.fault('EVENTS', 'clinical_event', self.lab, {'parent_event_version_id': other['clinical_event_version_id']}, 'provenance')

    def test_prebirth_and_postdeath_care_are_rejected(self):
        index = next(i for i, r in enumerate(self.tables['encounter']) if r['revision_no'] == 1)
        self.fault('ENCOUNTERS', 'encounter', index, {'arrival_at': '1900-01-01T12:00:00Z'}, 'before birth')
        v = self.validate()
        death_pid = next(iter(v.deaths))
        e = v.by_person[death_pid][0]
        positions = {r['encounter_version_id']: i for i, r in enumerate(self.tables['encounter'])}
        self.fault('ENCOUNTERS', 'encounter', positions[e['encounter_version_id']], {'arrival_at': '2026-01-01T05:59:00Z'}, 'after observed death')

    def test_future_encounter_milestone_and_snapshot_are_rejected(self):
        index = next(i for i, r in enumerate(self.tables['encounter']) if r['revision_no'] == 1)
        self.fault('ENCOUNTERS', 'encounter', index, {'discharged_at': '2025-12-31T23:59:00Z'}, 'future or unordered')

    def test_lab_collection_and_result_availability_are_enforced(self):
        self.fault('EVENTS', 'clinical_event', self.lab, {'collected_at': '2020-01-01T00:00:00Z'}, 'specimen')
        self.fault('AVAILABILITY', 'clinical_event', self.lab, {'result_ready_at': '2026-01-01T00:00:00Z'}, 'not yet known')

    def test_terminology_release_domain_and_unit_are_enforced(self):
        self.fault('TERMINOLOGY', 'clinical_event', self.lab, {'value_unit': 'kg'}, 'measurement unit')
        item = next(r for r in self.tables['catalog_item'] if r['domain'] == 'LAB')
        index = next(i for i, r in enumerate(self.events) if r['event_type'] == 'PROCEDURE')
        self.fault('TERMINOLOGY', 'clinical_event', index, {'catalog_item_id': item['catalog_item_id']}, 'wrong terminology domain')
        procedure = next(r for r in self.events if r['event_type'] == 'PROCEDURE' and self.validate_catalog[r['catalog_item_id']]['code_system'] == 'ICD-10-PCS' and r['occurred_at'] < '2024-01-01')
        index = self.event_positions[procedure['clinical_event_version_id']]
        current = self.validate().catalog[procedure['catalog_item_id']]
        other = next(r for r in self.tables['catalog_item'] if r['code'] == current['code'] and r['valid_from'] > procedure['occurred_at'][:10])
        self.fault('TERMINOLOGY', 'clinical_event', index, {'catalog_item_id': other['catalog_item_id']}, 'release invalid')

    def test_order_dose_route_and_course_are_enforced(self):
        order_id = self.events[self.med]['parent_event_version_id']
        index = self.event_positions[order_id]
        # Keep actual administrations and strength conversion consistent with the bad order.
        # This isolates the label-bounded order limit even when child rows sort before the order.
        from decimal import Decimal
        tables = dict(self.tables); tables['clinical_event'] = list(self.events)
        tables['clinical_event'][index] = {**self.events[index], 'dose_quantity': '100000'}
        for i, r in enumerate(self.events):
            if r['parent_event_version_id'] == order_id and r['event_type'] == 'MED_ADMIN':
                strength = Decimal(self.validate_catalog[r['catalog_item_id']]['strength_per_base_unit'])
                quantity = '0' if r['status'] in ('NOT_DONE', 'CANCELLED') else str((Decimal('100000') / strength).quantize(Decimal('0.000001')))
                tables['clinical_event'][i] = {**r, 'dose_quantity': '100000', 'consumed_base_quantity': quantity}
        result = self.validate(tables).check('MEDICATIONS')
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertIn('dose/schedule', result['failures'][0]['reason'])
        self.fault('MEDICATIONS', 'clinical_event', index, {'route': 'IV'}, 'route/unit')
        self.fault('MEDICATIONS', 'clinical_event', index, {'order_end_at': '2027-01-01T00:00:00Z'}, 'course outside')

    def test_actual_dose_and_strength_conversion_reconcile(self):
        self.fault('MEDICATIONS', 'clinical_event', self.med, {'dose_quantity': '100000'}, 'conversion')
        self.fault('MEDICATIONS', 'clinical_event', self.med, {'consumed_base_quantity': '999'}, 'conversion')

    def test_administration_schedule_and_sequence_are_enforced(self):
        order = self.events[self.event_positions[self.events[self.med]['parent_event_version_id']]]
        from datetime import datetime, timedelta
        early = (datetime.fromisoformat(order['order_start_at'].replace('Z', '+00:00')) - timedelta(seconds=1)).isoformat().replace('+00:00', 'Z')
        self.fault('MEDICATIONS', 'clinical_event', self.med, {'occurred_at': early}, 'outside active order')
        base = self.events[self.med]
        sibling = next(i for i, r in enumerate(self.events) if i != self.med and r['event_type'] == 'MED_ADMIN' and r['parent_event_version_id'] == base['parent_event_version_id'])
        self.fault('MEDICATIONS', 'clinical_event', sibling, {'administration_sequence': base['administration_sequence']}, 'duplicate administration')
        # Use a short/censored course whose entire actual count is within one day's cap.
        # Moving two administrations together cannot trip a local-day or rolling maximum.
        from collections import defaultdict
        v = self.validate()
        groups = defaultdict(list)
        for i, r in enumerate(self.events):
            if r['event_type'] == 'MED_ADMIN' and r['status'] == 'COMPLETED':
                groups[r['parent_event_version_id']].append(i)
        pair = next(positions for oid, positions in groups.items() if 2 <= len(positions) <= v.events[oid]['max_doses_per_day'])
        first, second = sorted(pair, key=lambda i: self.events[i]['occurred_at'])[:2]
        self.fault('MEDICATIONS', 'clinical_event', second, {'occurred_at': self.events[first]['occurred_at']}, 'too close')

    def test_allergy_withholding_never_consumes_stock(self):
        index = next(i for i, r in enumerate(self.events) if r['event_type'] == 'MED_ADMIN' and r['status'] == 'NOT_DONE')
        self.fault('MEDICATIONS', 'clinical_event', index, {'consumed_base_quantity': '1'}, 'consumes stock')
        r = self.events[index]
        cat = self.validate().catalog[r['catalog_item_id']]
        from decimal import Decimal
        consumed = str((Decimal(r['dose_quantity']) / Decimal(cat['strength_per_base_unit'])).quantize(Decimal('0.000001')))
        self.fault('MEDICATIONS', 'clinical_event', index, {'status': 'COMPLETED', 'consumed_base_quantity': consumed, 'consumption_group_key': 'synthetic-group'}, 'active recorded allergy')

    def test_fall_back_day_cannot_add_an_extra_daily_dose(self):
        orders = {r['clinical_event_version_id']: r for r in self.events if r['event_type'] == 'ORDER' and r['dose_interval_hours'] == '24'}
        from collections import defaultdict
        groups = defaultdict(list)
        for i, r in enumerate(self.events):
            if r['event_type'] == 'MED_ADMIN' and r['status'] == 'COMPLETED' and r['parent_event_version_id'] in orders:
                groups[r['parent_event_version_id']].append(i)
        chosen = next((oid, positions) for oid, positions in groups.items() if len(positions) >= 2 and orders[oid]['order_start_at'] < '2023-11-05T05:15:00Z' and orders[oid]['order_end_at'] > '2023-11-06T05:15:00Z')
        _, positions = chosen
        tables = dict(self.tables); tables['clinical_event'] = list(self.events)
        for index, at in zip(positions[:2], ('2023-11-05T05:15:00Z', '2023-11-06T05:15:00Z')):
            tables['clinical_event'][index] = {**self.events[index], 'occurred_at': at}
        result = self.validate(tables).check('MEDICATIONS')
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertIn('local-day maximum', result['failures'][0]['reason'])

    def test_take_home_is_not_future_administration(self):
        dispenses = [r for r in self.events if r['event_type'] == 'MED_DISPENSE']
        self.assertGreater(len(dispenses), 100)
        idx = self.validate().idx['encounter']
        self.assertTrue(all(idx[r['encounter_version_id']]['encounter_class'] != 'IPD' for r in dispenses))
        index = self.events.index(dispenses[0])
        self.fault('MEDICATIONS', 'clinical_event', index, {'dose_quantity': '10000000', 'consumed_base_quantity': '1'}, 'conversion')

    def test_condition_resolution_never_leaks_into_initial_assertion(self):
        index = next(i for i, r in enumerate(self.tables['clinical_condition']) if r['status'] == 'RESOLVED')
        self.fault('CONDITIONS', 'clinical_condition', index, {'resolved_at': '2026-12-01T00:00:00Z'}, 'future or pre-onset')
        self.assertGreater(sum(r['condition_type'] == 'PROBLEM' for r in self.tables['clinical_condition']), 12000)

    def test_reference_context_and_triage_scale_are_enforced(self):
        self.fault('TRAJECTORIES', 'clinical_event', self.lab, {'reference_low': '0', 'reference_high': '100000'}, 'reference context')
        self.fault('ENCOUNTERS', 'encounter', 0, {'initial_acuity': 99}, 'acuity outside')

    def test_no_new_condition_onset_after_observed_death(self):
        v = self.validate()
        index = next(i for i, r in enumerate(self.tables['clinical_condition']) if r['encounter_version_id'] and v.latest[v.idx['encounter'][r['encounter_version_id']]['encounter_id']]['disposition'] == 'DEATH')
        row = self.tables['clinical_condition'][index]
        from datetime import timedelta
        from healthcare_synthetic.master_validation import timestamp
        death = v.deaths[v.patient[row['patient_version_id']]['patient_id']]
        after = (timestamp(death) + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')
        self.fault('CONDITIONS', 'clinical_condition', index, {'onset_at': after, 'known_from': after}, 'onset after death')

    def test_repeat_visits_vary_complaints_without_future_chronic_history(self):
        self.assertGreaterEqual(float(self.checked['metrics']['repeat_complaint_variation_share']), .35)
        self.assertGreater(self.checked['metrics']['laboratory_results_known_after_discharge'], 100)
        codes = {r['code'] for r in self.tables['catalog_item'] if r['domain'] == 'DIAGNOSIS'}
        self.assertTrue({'R079', 'R1010'} <= codes)

    def test_booked_outpatient_visit_is_planned_and_not_elective_admission(self):
        idx = self.validate().idx['encounter']
        visited = [a for a in self.tables['appointment'] if a['resulting_encounter_version_id'] and idx[a['resulting_encounter_version_id']]['encounter_class'] == 'OPD']
        self.assertEqual(len(visited), 17000)
        self.assertTrue(all(a['appointment_type'] != 'ELECTIVE_ADMISSION' and idx[a['resulting_encounter_version_id']]['planned'] for a in visited))

    def test_notes_are_fact_grounded_and_reject_unsupported_prose(self):
        self.fault('DOCUMENTS', 'clinical_event', self.note, {'text_value': self.events[self.note]['text_value'] + ' Patient will recover tomorrow.'}, 'unsupported')
        self.fault('DOCUMENTS', 'clinical_event', self.note, {'document_signed_at': '2020-01-01T00:00:00Z'}, 'signing/type')
        self.fault('DOCUMENTS', 'clinical_event', self.note, {'text_value': self.events[self.note]['text_value'].replace('age ', 'age 99')}, 'identity/age')

    def test_note_result_and_future_fact_mutations_are_rejected(self):
        index = next(i for i, r in enumerate(self.events) if r['event_type'] == 'DOCUMENT' and 'Oxygen saturation:' in r['text_value'])
        self.fault('DOCUMENTS', 'clinical_event', index, {'text_value': self.events[index]['text_value'].replace('Oxygen saturation:', 'Oxygen saturation: 999')}, 'contradicts structured value')

    def test_correlated_trajectories_and_adverse_cases_are_present(self):
        self.assertEqual(len(self.checked['metrics']['pathway_counts']), 6)
        self.assertEqual(self.checked['metrics']['death_outcomes'], 30)
        self.assertTrue(all(float(v) >= .8 for v in self.checked['metrics']['recovery_direction_shares'].values()))
        self.fault('TRAJECTORIES', 'clinical_event', self.lab, {'numeric_value': '9999999'}, 'physiological envelope')

    def test_operative_notes_document_actual_procedure_evidence(self):
        index = next(i for i, r in enumerate(self.events) if r['document_type'] == 'OPERATIVE_NOTE')
        self.assertEqual(self.checked['metrics']['document_counts']['OPERATIVE_NOTE'], 4800)
        self.fault('DOCUMENTS', 'clinical_event', index, {'text_value': self.events[index]['text_value'].replace('Procedure documented:', 'Procedure not performed:')}, 'ordered and performed')

    def test_operations_have_surgical_specialty_and_daytime_elective_admission(self):
        v = self.validate()
        index = next(i for i, r in enumerate(self.events) if r['event_type'] == 'PROCEDURE' and v.catalog[r['catalog_item_id']]['code_system'] == 'ICD-10-PCS')
        event = self.events[index]
        e = v.idx['encounter'][event['encounter_version_id']]
        wrong = next(w for w in self.tables['worker_assignment'] if w['facility_id'] == e['facility_id'] and w['role'] == 'PHYSICIAN' and w['specialty'] == 'Internal Medicine')
        self.fault('TRAJECTORIES', 'clinical_event', index, {'author_assignment_id': wrong['worker_assignment_id']}, 'operative author specialty')

    def test_appointment_no_show_cancellation_and_reschedule_chronology(self):
        index = next(i for i, r in enumerate(self.tables['appointment']) if r['no_show_recorded_at'])
        self.fault('APPOINTMENTS', 'appointment', index, {'no_show_recorded_at': self.tables['appointment'][index]['booked_at']}, 'no-show before')
        self.assertEqual(self.checked['metrics']['appointment_outcomes']['CENSORED'], 200)

    def test_cutoff_censoring_and_readmission_denominator(self):
        m = self.checked['metrics']
        self.assertGreater(m['open_inpatient'], 0)
        self.assertGreater(m['readmission_censored_discharges'], 0)
        self.assertGreaterEqual(m['readmission_numerator'], 1200)
        self.assertLessEqual(m['readmission_numerator'], 1320)
        self.assertGreater(m['readmission_eligible_denominator'], m['readmission_numerator'])

    def test_stratified_hundred_journey_review_is_content_bound(self):
        body, selection = render_journeys(self.tables, self.cfg)
        self.assertEqual(selection['journeys'], 100)
        self.assertIn('outcome/DEATH', selection['strata'])
        self.assertIn('outcome/OPEN', selection['strata'])
        self.assertIn('carry/True', selection['strata'])
        self.assertIn('allergy-withheld', selection['strata'])
        decision = json.loads((ROOT / 'reviews/clinical-journey-review.json').read_text())
        self.assertEqual(review_gate(selection, decision)['status'], 'PASS')
        self.assertEqual(review_gate({**selection, 'selected_facts_sha256': 'changed'}, decision)['status'], 'PENDING_REVIEW')
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(), selection['sample_sha256'])

    def test_review_strata_use_birthday_aware_local_ages(self):
        import re
        from healthcare_synthetic.master_validation import timestamp, years
        body, _ = render_journeys(self.tables, self.cfg)
        v = self.validate()
        for section in body.split('## Journey ')[1:]:
            identity = section.splitlines()[2]
            pid = identity.split('Stable patient: ')[1].split(';')[0]
            expected = set()
            for e in v.by_person[pid]:
                age = years(v.patient[e['patient_version_id']]['birth_date'], timestamp(e['arrival_at']).astimezone(v.local_zone).date().isoformat())
                expected.add('18-34' if age < 35 else '35-49' if age < 50 else '50-64' if age < 65 else '65-79' if age < 80 else '80+')
            self.assertEqual(set(re.findall(r'age/([0-9+\-]+)', identity)), expected)

    def test_february_leap_age_convention_is_preserved(self):
        self.assertEqual(age_on('1960-02-29', '2023-02-28'), 63)
        self.assertEqual(age_on('1960-02-29', '2024-02-28'), 63)
        self.assertEqual(age_on('1960-02-29', '2024-02-29'), 64)

    def test_validator_is_independent_of_generation_and_serializer(self):
        tree = ast.parse((ROOT / 'src/healthcare_synthetic/clinical_validation.py').read_text())
        imports = [n.module or '' for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(any('generation' in n or 'core' in n or 'pipeline' in n for n in imports))

    def test_unapproved_profile_or_record_budget_cannot_be_used(self):
        config = copy.deepcopy(self.cfg)
        config['cohort']['inpatient'] = 1000000
        path = self.work / 'invalid-budget.json'; path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, 'cohort'): run_clinical(path, self.work / 'invalid-output')

    def test_full_clean_rebuild_and_cached_resume_are_identical(self):
        output = self.work / 'clean-rebuild'
        command = [sys.executable, str(ROOT / 'scripts/generate_clinical_histories.py'), '--output', str(output)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=900)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        first = json.loads((output / 'manifest.json').read_text())
        self.assertEqual(first['business_sha256'], self.manifest['business_sha256'])
        result = subprocess.run(command, capture_output=True, text=True, timeout=900)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        again = json.loads((output / 'manifest.json').read_text())
        self.assertEqual(again['business_sha256'], first['business_sha256'])
        self.assertEqual(set(again['reused']), set(GRAPH))
        self.assertEqual(again['executed'], [])

    def test_real_process_crash_rolls_back_validation_then_resumes(self):
        output = self.work / 'recovery'
        output.mkdir()
        with sqlite3.connect(self.base / 'checkpoints.sqlite3') as source, sqlite3.connect(output / 'checkpoints.sqlite3') as target:
            source.backup(target)
            target.execute("DELETE FROM stages WHERE name='validation'"); target.commit()
        (output / 'manifest.json').write_text(json.dumps({'profile': 'LONGITUDINAL_CLINICAL'}))
        command = [sys.executable, str(ROOT / 'scripts/generate_clinical_histories.py'), '--output', str(output)]
        crashed = subprocess.run([*command, '--crash-stage', 'validation'], capture_output=True, text=True, timeout=900)
        self.assertEqual(crashed.returncode, 97, crashed.stdout + crashed.stderr)
        with sqlite3.connect(output / 'checkpoints.sqlite3') as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM stages WHERE name='validation'").fetchone()[0], 0)
        self.assertFalse((output / 'candidate-ready.json').exists())
        resumed = subprocess.run(command, capture_output=True, text=True, timeout=900)
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        after = json.loads((output / 'manifest.json').read_text())
        self.assertEqual(after['business_sha256'], self.manifest['business_sha256'])
        self.assertEqual(after['executed'], ['validation'])

    def test_checkpoint_corruption_fails_closed(self):
        output = self.work / 'corrupt'; output.mkdir()
        with sqlite3.connect(output / 'checkpoints.sqlite3') as c:
            c.execute('CREATE TABLE stages(name TEXT PRIMARY KEY,local_hash TEXT,input_hash TEXT,payload TEXT,checksum TEXT,row_count INTEGER)')
            c.execute('INSERT INTO stages VALUES (?,?,?,?,?,?)', ('accepted_master', 'x', 'x', '{}', 'corrupt', 0))
        (output / 'manifest.json').write_text(json.dumps({'profile': 'LONGITUDINAL_CLINICAL'}))
        with self.assertRaisesRegex(ValueError, 'checkpoint corruption'): run_clinical(output_dir=output)
        self.assertFalse((output / 'candidate-ready.json').exists())

    def test_changed_clinical_seed_invalidates_descendants_before_failure(self):
        output = self.work / 'changed-seed'; output.mkdir()
        with sqlite3.connect(self.base / 'checkpoints.sqlite3') as source, sqlite3.connect(output / 'checkpoints.sqlite3') as target:
            source.backup(target)
        (output / 'manifest.json').write_text(json.dumps({'profile': 'LONGITUDINAL_CLINICAL'}))
        (output / 'candidate-ready.json').write_text('{}')
        config = copy.deepcopy(self.cfg); config['seed'] += 1
        path = self.work / 'changed-clinical-seed.json'; path.write_text(json.dumps(config))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_clinical_histories.py'), '--config', str(path), '--output', str(output), '--fail-stage', 'journeys'], capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        with sqlite3.connect(output / 'checkpoints.sqlite3') as c:
            self.assertEqual(c.execute('SELECT name FROM stages').fetchall(), [('accepted_master',)])
        self.assertFalse((output / 'candidate-ready.json').exists())
        manifest = json.loads((output / 'manifest.json').read_text())
        self.assertEqual(set(manifest['invalidated']), set(GRAPH) - {'accepted_master'})

    def test_independent_persisted_inspector_recomputes_all_rules(self):
        result = inspect_clinical(self.base)
        self.assertEqual(result['artifact_integrity'], 'PASS')
        self.assertEqual(result['gate_status'], 'CLINICAL_HISTORIES_PASSED', result.get('defects'))
        self.assertEqual(result['business_sha256'], self.manifest['business_sha256'])

    def test_accepted_master_can_be_rebuilt_from_exact_git_revision(self):
        output = self.work / 'restored-master'
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/restore_master_snapshot.py'), '--output', str(output)], capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        restored = json.loads((output / 'manifest.json').read_text())
        self.assertEqual(restored['business_sha256'], self.cfg['master_business_sha256'])

if __name__ == '__main__': unittest.main(verbosity=2)
