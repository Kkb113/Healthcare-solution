"""Source contracts, falsifiable transport controls, replay and full-history recovery."""
import copy
import csv
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from decimal import localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))
from healthcare_synthetic.core import digest
from healthcare_synthetic.source_layouts import contracts, read, read_rows
from healthcare_synthetic.source_export import export_file, footprint
from healthcare_synthetic.source_delivery import primary_exports, weekly_snapshots, run_sources, accepted_parent, batch_time
from healthcare_synthetic.source_reader import DeliveryReplay, read_file, effective_versions, project_bed_events
from healthcare_synthetic.source_faults import change_csv, refresh, exercise_faults
from healthcare_synthetic.source_validation import inspect_sources
from healthcare_synthetic.source_reports import reports
from healthcare_synthetic.source_report_validation import validate_reports


class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layouts = contracts(); cls.parent = ROOT / 'output/financial-history'; cls.accepted = read(cls.parent / 'manifest.json')
        cls.examples = {}
        for table, f in cls.accepted['canonical_files'].items():
            with (cls.parent / f['file']).open(encoding='utf-8') as stream:
                cls.examples[table] = json.loads(next(stream))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='source-contract-tests-', dir=ROOT / 'output'); self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def file(self, table='finance_monthly', rows=None, **kwargs):
        layout = self.layouts[table]; rows = rows or [self.examples[table]]
        return export_file(self.root, layout, rows, 'fixture', **kwargs)

    def test_every_full_schema_table_roundtrips_without_hidden_json_fields(self):
        self.assertEqual(len(self.layouts), 25)
        for table, layout in self.layouts.items():
            with self.subTest(table=table):
                m = self.file(table)
                self.assertEqual(read_file(self.root, m, layout), [self.examples[table]])
                self.assertTrue(all(not isinstance(v, (list, dict)) for v in self.examples[table].values()))

    def test_names_unicode_csv_quotes_multiline_null_literal_and_empty_survive(self):
        row = copy.deepcopy(self.examples['worker_assignment'])
        row.update(given_name='Zoë, "María"\nAna', family_name='\\N', specialty='', credential_code='\\E-RN')
        m = self.file('worker_assignment', [row])
        self.assertEqual(read_file(self.root, m, self.layouts['worker_assignment']), [row])

    def test_exact_decimal_controls_do_not_mix_money_and_quantities(self):
        row = self.examples['staff_shift']; m = self.file('staff_shift')
        self.assertEqual(m['control_totals']['loaded_cost'], row['loaded_cost'])
        self.assertEqual(m['control_totals']['productive_hours'], row['productive_hours'])
        self.assertNotEqual(set(m['control_totals']), {'amount'})

    def test_finance_controls_separate_period_scenario_vintage_measure_and_unit(self):
        rows = read_rows(self.parent / self.accepted['canonical_files']['finance_monthly']['file'])
        examples = [next(r for r in rows if r['unit_code'] == unit) for unit in ('USD', 'FTE', 'hours', 'admissions', 'patient_days')]
        m = self.file(rows=examples)
        self.assertEqual(len(m['unit_control_totals']), 5)
        self.assertEqual({k.split('|')[-1] for k in m['unit_control_totals']}, {'USD', 'FTE', 'hours', 'admissions', 'patient_days'})
        self.assertEqual(len(read_file(self.root, m, self.layouts['finance_monthly'])), 5)
        change_csv(self.root, m, 'Unit', 'WRONG-UNIT')
        with self.assertRaisesRegex(ValueError, 'unit controls'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_ambient_decimal_context_cannot_change_source_controls_or_reconstruction(self):
        row = {**self.examples['finance_monthly'], 'amount': '1234567.89', 'quantity': None, 'unit_code': 'USD'}
        normal = self.file(rows=[row])
        with localcontext() as ambient:
            ambient.prec = 4
            changed = self.file(rows=[row])
            self.assertEqual(changed, normal)
            self.assertEqual(read_file(self.root, changed, self.layouts['finance_monthly']), [row])

    def test_missing_required_key_is_not_inferred_from_dictionary(self):
        m = self.file(); change_csv(self.root, m, 'FinanceRecordReference', '\\N')
        with self.assertRaisesRegex(ValueError, 'F_UNMAPPED'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_unknown_typed_reference_is_quarantined_even_with_valid_bytes(self):
        m = self.file(); change_csv(self.root, m, 'CostCenterReference', 'NOT-A-CENTER')
        with self.assertRaisesRegex(ValueError, 'F_UNMAPPED'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_key_dictionary_checksum_is_checked(self):
        m = self.file()
        with (self.root / m['dictionary_path']).open('ab') as stream:
            stream.write(b'BAD')
        with self.assertRaisesRegex(ValueError, 'F_CORRUPT'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_manifest_checksum_tampering_fails(self):
        m = self.file(); m['expected_rows'] += 1
        with self.assertRaisesRegex(ValueError, 'manifest identity'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_missing_file_does_not_turn_into_empty_partition(self):
        m = self.file(); (self.root / m['path']).unlink()
        with self.assertRaisesRegex(ValueError, 'F_MISSING'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_unknown_schema_and_wrong_headers_fail_closed(self):
        m = self.file(); m['schema_version'] = 'source-2'; refresh(m)
        with self.assertRaisesRegex(ValueError, 'F_SCHEMA'):
            read_file(self.root, m, self.layouts['finance_monthly'])
        m = self.file(); path = self.root / m['path']; path.write_bytes(path.read_bytes().replace(b'FinanceRecordReference', b'UnexpectedIdentifier', 1)); m.update(footprint(path)); refresh(m)
        with self.assertRaisesRegex(ValueError, 'F_SCHEMA'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_path_escape_is_rejected_before_reading(self):
        m = self.file(); m['path'] = '../sensitive.csv'; refresh(m)
        with self.assertRaisesRegex(ValueError, 'escaped'):
            read_file(self.root, m, self.layouts['finance_monthly'])

    def test_corrupt_last_row_is_atomic_and_recovery_resolves_quarantine(self):
        m = self.file(); good = copy.deepcopy(m); path = self.root / m['path']; saved = path.read_bytes()
        with path.open('ab') as stream:
            stream.write(b'BROKEN')
        replay = DeliveryReplay(':memory:')
        try:
            with self.assertRaisesRegex(ValueError, 'F_CORRUPT'):
                replay.ingest(self.root, m, self.layouts['finance_monthly'])
            self.assertEqual(replay.table_hash('finance_monthly')[1], 0)
            with self.assertRaisesRegex(ValueError, 'unresolved'):
                replay.certify([m['file_id']])
            path.write_bytes(saved); replay.recover(self.root, good, self.layouts['finance_monthly'], m['file_id'])
            self.assertEqual(replay.certify([m['file_id']]), 'COMPLETE')
        finally:
            replay.close()

    def test_decimal_nan_infinity_exponent_and_excess_scale_rejected(self):
        # Deliberately reseal valid byte checksums: the scalar detector must still fail.
        row = next(r for r in read_rows(self.parent / self.accepted['canonical_files']['finance_monthly']['file']) if r['amount'] is not None)
        for bad in ('NaN', 'Infinity', '1e3', '1.001', '999999999999999999.00'):
            m = self.file(rows=[row]); change_csv(self.root, m, 'Amount', bad)
            with self.subTest(value=bad), self.assertRaisesRegex(ValueError, 'F_CORRUPT'):
                read_file(self.root, m, self.layouts['finance_monthly'])

    def test_event_envelope_sequence_and_payload_identity_checked(self):
        for column, value in [('SourceSequence', 9), ('MessageID', 'CONFLICT'), ('SchemaVersion', 'unapproved')]:
            m = self.file('bed_event'); path = self.root / m['path']; body = json.loads(path.read_text()); body[column] = value
            path.write_text(json.dumps(body) + '\n', encoding='utf-8'); m.update(footprint(path)); refresh(m)
            with self.subTest(column=column), self.assertRaises(ValueError):
                read_file(self.root, m, self.layouts['bed_event'])

    def test_repeated_immutable_key_in_single_file_rejected(self):
        row = self.examples['worker_assignment']; m = self.file('worker_assignment', [row, row])
        with self.assertRaisesRegex(ValueError, 'repeated'):
            read_file(self.root, m, self.layouts['worker_assignment'])

    def test_conflicting_same_version_cannot_mutate_existing_history(self):
        a = self.file('worker_assignment'); row = {**self.examples['worker_assignment'], 'given_name': 'Different'}
        b = export_file(self.root, self.layouts['worker_assignment'], [row], 'conflict')
        replay = DeliveryReplay(':memory:')
        try:
            replay.ingest(self.root, a, self.layouts['worker_assignment']); before = replay.table_hash('worker_assignment')
            with self.assertRaisesRegex(ValueError, 'conflicting immutable'):
                replay.ingest(self.root, b, self.layouts['worker_assignment'])
            self.assertEqual(replay.table_hash('worker_assignment'), before)
        finally:
            replay.close()

    def test_late_batch_blocks_prior_knowledge_even_when_effective_date_is_old(self):
        row = self.examples['worker_assignment']; arrival = '2025-12-31T07:00:00Z'
        m = self.file('worker_assignment', available_at=arrival); replay = DeliveryReplay(':memory:')
        try:
            replay.ingest(self.root, m, self.layouts['worker_assignment'])
            self.assertEqual(replay.rows('worker_assignment', '2025-12-31T06:59:59Z'), [])
            self.assertEqual(replay.rows('worker_assignment', arrival), [{**row, 'known_to': None}])
        finally:
            replay.close()

    def test_scheduled_batch_rejects_delivery_before_publication(self):
        m = self.file('worker_assignment'); replay = DeliveryReplay(':memory:')
        try:
            with self.assertRaisesRegex(ValueError, 'not yet available'):
                replay.ingest(self.root, m, self.layouts['worker_assignment'], delivered_at='1900-01-01T00:00:00Z')
        finally:
            replay.close()

    def test_idempotence_survives_durable_reopen(self):
        m = self.file(); db = self.root / 'replay.sqlite3'; layout = self.layouts['finance_monthly']
        replay = DeliveryReplay(db); replay.ingest(self.root, m, layout); before = replay.table_hash('finance_monthly'); replay.close()
        replay = DeliveryReplay(db)
        try:
            self.assertEqual(replay.ingest(self.root, m, layout), 'DUPLICATE')
            self.assertEqual(replay.table_hash('finance_monthly'), before)
        finally:
            replay.close()

    def test_failed_transaction_rolls_back_every_version(self):
        m = self.file('worker_assignment'); replay = DeliveryReplay(':memory:')
        try:
            with self.assertRaisesRegex(ValueError, 'injected publication'):
                replay.ingest(self.root, m, self.layouts['worker_assignment'], fail=True)
            self.assertEqual(replay.db.execute('SELECT count(*) FROM versions').fetchone()[0], 0)
            self.assertEqual(replay.db.execute('SELECT count(*) FROM files').fetchone()[0], 0)
        finally:
            replay.close()

    def test_historical_visibility_uses_indexed_typed_version_and_time_lookup(self):
        replay = DeliveryReplay(':memory:')
        try:
            plan = replay.db.execute('EXPLAIN QUERY PLAN SELECT 1 FROM deliveries WHERE t=? AND k=? AND observed<=?', ('bed_event', 'message', '9999')).fetchall()
            descriptions = ' '.join(row[-1] for row in plan)
            self.assertIn('SEARCH', descriptions)
            self.assertIn('COVERING INDEX', descriptions)
            self.assertNotIn('SCAN deliveries', descriptions)
        finally:
            replay.close()

    def replacement_pair(self):
        rows = read_rows(self.parent / self.accepted['canonical_files']['finance_monthly']['file'])
        b = next(r for r in rows if r['scenario'] == 'ACTUAL' and r['supersedes_vintage_id'])
        a = next(r for r in rows if r['vintage_id'] == b['supersedes_vintage_id'] and all(r[k] == b[k] for k in ['cost_center_id', 'account_catalog_id', 'measure_code', 'unit_code', 'accounting_month']))
        layout = self.layouts['finance_monthly']
        old = export_file(self.root, layout, [a], 'original', mode='REPLACE_DECLARED_SCOPE_VERSION', scope='actual/2025-12')
        new = export_file(self.root, layout, [b], 'revised', mode='REPLACE_DECLARED_SCOPE_VERSION', scope=old['scope'], replacement_of=old['file_id'])
        return old, new

    def test_replacements_preserve_historical_value_without_adding_current(self):
        a, b = self.replacement_pair(); replay = DeliveryReplay(':memory:'); layout = self.layouts['finance_monthly']
        try:
            replay.ingest(self.root, a, layout); replay.ingest(self.root, b, layout)
            self.assertEqual(replay.rows('finance_monthly', a['available_at'], a['scope']), read_file(self.root, a, layout))
            self.assertEqual(replay.rows('finance_monthly', b['available_at'], b['scope']), read_file(self.root, b, layout))
        finally:
            replay.close()

    def test_missing_predecessor_cross_scope_implicit_and_branched_replacements_fail(self):
        a, b = self.replacement_pair(); layout = self.layouts['finance_monthly']
        for kind in ('missing', 'scope', 'implicit', 'branch'):
            replay = DeliveryReplay(':memory:'); bad = copy.deepcopy(b)
            try:
                if kind != 'missing':
                    replay.ingest(self.root, a, layout)
                if kind == 'scope':
                    bad['scope'] = 'actual/another-month'
                elif kind == 'implicit':
                    bad['replacement_of'] = None
                elif kind == 'branch':
                    replay.ingest(self.root, b, layout); bad['period'] = 'branched-delivery'
                refresh(bad)
                with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'F_MISSING|F_REPLACE'):
                    replay.ingest(self.root, bad, layout)
            finally:
                replay.close()

    def test_all_weekly_snapshots_are_source_known_and_reload_without_duplicates(self):
        rows = read_rows(self.parent / self.accepted['canonical_files']['worker_assignment']['file'])
        snapshots = weekly_snapshots(self.root, self.layouts['worker_assignment'], rows)
        self.assertEqual(len(snapshots), 159)
        for m in snapshots:
            got = read_file(self.root, m, self.layouts['worker_assignment'])
            self.assertTrue(all(r['export_available_at'] <= m['available_at'] for r in got))
            self.assertEqual({r['worker_assignment_id'] for r in got}, {r['worker_assignment_id'] for r in rows if r['export_available_at'] <= m['available_at']})

    def test_daily_workday_changes_include_empty_files_and_closing_grace(self):
        files = primary_exports(self.root, self.layouts['access_scope'], [self.examples['access_scope']])
        self.assertTrue(any(m['expected_rows'] == 0 for m in files))
        self.assertIn('2026-01-10T07:00:00Z', {m['available_at'] for m in files})
        self.assertEqual(sum(m['expected_rows'] for m in files), 1)
        self.assertEqual(batch_time('2024-06-01T08:00:00Z'), '2024-06-02T07:00:00Z')

    def test_retroactive_validity_does_not_override_past_knowledge(self):
        rows = read_rows(self.parent / self.accepted['canonical_files']['worker_assignment']['file'])
        target = next(r for r in rows if r['revision_no'] == 3 and r['valid_from'] < r['known_from'])
        selected = effective_versions(rows, 'worker_id', target['valid_from'], target['export_available_at'])
        self.assertIn(target, selected)
        before = effective_versions(rows, 'worker_id', target['valid_from'], '2022-01-01T00:00:00Z')
        self.assertNotIn(target, before)

    def test_expired_latest_revision_cannot_resurrect_older_open_ended_scope(self):
        old = {**self.examples['access_scope'], 'grant_id': 'grant-test', 'decision': 'ALLOW',
               'revision_no': 1, 'valid_from': '2023-01-01T00:00:00Z', 'valid_to': None,
               'known_from': '2023-01-01T00:00:00Z', 'export_available_at': '2023-01-01T07:00:00Z'}
        latest = {**old, 'revision_no': 2, 'known_from': '2024-01-01T00:00:00Z',
                  'export_available_at': '2024-01-01T07:00:00Z', 'valid_to': '2024-02-01T00:00:00Z'}
        self.assertEqual(effective_versions([old, latest], 'grant_id', '2025-01-01T00:00:00Z', '2025-01-01T00:00:00Z'), [])
        self.assertEqual(effective_versions([old, latest], 'grant_id', '2023-06-01T00:00:00Z', '2023-06-01T00:00:00Z'), [old])

    def test_workday_exports_do_not_claim_scheduling_or_payroll_authority(self):
        self.assertEqual(self.layouts['staff_shift']['source'], 'ROSTER_TIME')
        self.assertEqual({t for t, l in self.layouts.items() if l['source'] == 'WORKDAY'}, {'cost_center', 'worker_assignment', 'access_scope'})

    def test_retrospective_audit_closure_is_hidden_from_historical_source_views(self):
        row = self.examples['worker_assignment']; self.assertIsNotNone(row['known_to'])
        m = self.file('worker_assignment'); replay = DeliveryReplay(':memory:')
        try:
            replay.ingest(self.root, m, self.layouts['worker_assignment'])
            self.assertIsNone(replay.rows('worker_assignment', row['export_available_at'])[0]['known_to'])
            self.assertEqual(replay.rows('worker_assignment')[0]['known_to'], row['known_to'])
        finally:
            replay.close()

    def test_bed_correction_without_predecessor_blocks_state_until_recovered(self):
        rows = read_rows(self.parent / self.accepted['canonical_files']['bed_event']['file'])
        correction = next(r for r in rows if r['corrects_bed_event_id'])
        prior = next(r for r in rows if r['bed_event_id'] == correction['corrects_bed_event_id'])
        with self.assertRaisesRegex(ValueError, 'F_MISSING'):
            project_bed_events([correction], '9999', '9999')
        self.assertEqual(project_bed_events([correction, prior], '9999', '9999')[prior['bed_location_id']], correction)

    def test_cyclic_and_cross_bed_corrections_fail_instead_of_erasing_state(self):
        a = copy.deepcopy(self.examples['bed_event']); a.update(bed_event_id='a', corrects_bed_event_id='b')
        b = {**a, 'bed_event_id': 'b', 'corrects_bed_event_id': 'a'}
        with self.assertRaisesRegex(ValueError, 'cycle'):
            project_bed_events([a, b], '9999', '9999')
        b['corrects_bed_event_id'] = None; b['bed_location_id'] = 'ANOTHER_BED'
        with self.assertRaisesRegex(ValueError, 'crosses bed'):
            project_bed_events([a, b], '9999', '9999')

    def test_boolean_date_and_integer_malformed_values_fail(self):
        for table, column, value in [('staff_shift', 'ExtractVersion', '1.0'), ('worker_assignment', 'BirthDate', '02/30/1980')]:
            m = self.file(table); change_csv(self.root, m, column, value)
            with self.subTest(column=column), self.assertRaisesRegex(ValueError, 'F_CORRUPT'):
                read_file(self.root, m, self.layouts[table])

    def test_wrong_output_profile_is_rejected_without_touching_accepted_ready_marker(self):
        (self.root / 'manifest.json').write_text('{"profile":"CONNECTED_FINANCIAL_HISTORY"}', encoding='utf-8')
        ready = self.root / 'candidate-ready.json'; ready.write_text('accepted-parent', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'wrong source output profile'):
            run_sources(self.root)
        self.assertEqual(ready.read_text(), 'accepted-parent')


class SourceHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = ROOT / 'output/source-delivery'; cls.manifest = read(cls.output / 'manifest.json')

    def test_full_history_all_files_and_independent_roundtrip_and_duplicate_replay(self):
        result = inspect_sources(self.output)
        from inspect_source_calendar import inspect_calendar
        result['delivery_calendar'] = inspect_calendar(self.output, self.manifest)
        self.assertEqual(result['roundtrip_rows'], 1924164)
        self.assertEqual(len(result['canonical_roundtrip']), 25)
        self.assertEqual(result['unexplained_differences'], 0)
        self.assertEqual(len(result['axiom_families']), 12)
        self.assertEqual(result['duplicate_deliveries_checked'], len(self.manifest['files']))
        (self.output / 'independent-inspection.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')

    def test_all_published_critical_faults_detected_quarantined_repaired(self):
        package = read(self.output / 'challenge-manifest.json')
        result = exercise_faults(self.output, package, self.output / 'fault-replay')
        self.assertEqual(result['unresolved_release_blocking_faults'], 0)
        self.assertTrue(all(r['status'] == 'PASS' for r in result['outcomes']))

    def test_missing_header_only_expected_workday_file_blocks_completeness(self):
        from inspect_source_calendar import inspect_calendar
        altered = copy.deepcopy(self.manifest)
        target = next(m for m in altered['files'] if m['table'] == 'worker_assignment' and m['role'] == 'PRIMARY' and m['expected_rows'] == 0)
        altered['files'].remove(target)
        with self.assertRaisesRegex(ValueError, 'F_MISSING.*daily delivery'):
            inspect_calendar(self.output, altered)

    def test_missing_weekly_snapshot_blocks_completeness(self):
        from inspect_source_calendar import inspect_calendar
        altered = copy.deepcopy(self.manifest)
        target = next(m for m in altered['files'] if m['table'] == 'worker_assignment' and m['mode'] == 'FULL_SNAPSHOT')
        altered['files'].remove(target)
        with self.assertRaisesRegex(ValueError, 'F_MISSING.*Sunday calendar'):
            inspect_calendar(self.output, altered)

    def test_resealed_axiom_header_scope_period_and_source_identity_mismatches_fail(self):
        from inspect_source_calendar import inspect_calendar
        for key, value in [('scope', 'WRONG-SCOPE'), ('period', '2030-01-01'), ('vintages', ['UNKNOWN']),
                           ('original_source_files', ['WRONG-FILE']), ('report_templates', ['WRONG-TEMPLATE'])]:
            altered = copy.deepcopy(self.manifest)
            target = next(m for m in altered['files'] if m['table'] == 'finance_monthly')
            target[key] = value; refresh(target)
            with self.subTest(field=key), self.assertRaisesRegex(ValueError, 'source header'):
                inspect_calendar(self.output, altered)

    def test_manifest_budget_includes_challenge_copies_and_separates_mirrors(self):
        package = read(self.output / 'challenge-manifest.json'); policy = read(ROOT / 'contracts/source-delivery-policy.json')
        self.assertLessEqual(package['published_challenge_record_copies'], policy['challenge_allowance'])
        self.assertLessEqual(1924164 + package['published_challenge_record_copies'], 2000000)
        self.assertGreater(self.manifest['dictionary_mapping_rows'], 0)
        self.assertGreater(self.manifest['scheduled_mirror_rows'], 0)
        self.assertFalse(self.manifest['full_dataset_accepted'])

    def test_finance_original_file_and_template_identities_are_preserved(self):
        original = read(ROOT / 'output/financial-history/manifest.json')
        path = ROOT / 'output/financial-history' / original['canonical_files']['finance_monthly']['file']
        rows = read_rows(path)
        files = [m for m in self.manifest['files'] if m['table'] == 'finance_monthly']
        self.assertEqual({x for m in files for x in m['original_source_files']}, {r['source_file_id'] for r in rows})
        self.assertEqual({x for m in files for x in m['report_templates']}, {r['report_template_id'] for r in rows})
        self.assertEqual(len({r['source_file_id'] for r in rows}), 231)

    def test_report_mutation_is_detected_after_resealing_byte_checksum(self):
        parent = ROOT / 'output/financial-history'; accepted = read(parent / 'manifest.json')
        def load(t):
            return read_rows(parent / accepted['canonical_files'][t]['file'])
        with tempfile.TemporaryDirectory(prefix='source-report-mutations-', dir=ROOT / 'output') as tmp:
            root = Path(tmp); finance, centers, catalog = load('finance_monthly'), load('cost_center'), load('catalog_item')
            for family in ('actual-wide-months', 'actual-with-adjustments', 'forecast-drivers', 'variance-comparison', 'account-mapping', 'center-mapping'):
                manifests = reports(root, finance, centers, catalog); m = next(m for m in manifests if m['family'] == family)
                path = root / m['path']
                with path.open(encoding='utf-8', newline='') as stream:
                    reader = csv.DictReader(stream); columns = reader.fieldnames; rows = list(reader)
                column = {'actual-wide-months': 'P01', 'actual-with-adjustments': 'Adjustment', 'forecast-drivers': 'CalendarDays',
                          'variance-comparison': 'Actual', 'account-mapping': 'Description', 'center-mapping': 'Description'}[family]
                rows[0][column] = 'BAD'
                with path.open('w', encoding='utf-8', newline='') as stream:
                    writer = csv.DictWriter(stream, fieldnames=columns); writer.writeheader(); writer.writerows(rows)
                m.update(footprint(path)); refresh(m)
                with self.subTest(family=family), self.assertRaises((ValueError, KeyError, ArithmeticError)):
                    validate_reports(root, manifests, finance, centers, catalog)

    def test_clean_full_export_rebuild_cached_reuse_and_exact_all_file_hashes(self):
        from generate_source_delivery import generate
        with tempfile.TemporaryDirectory(prefix='source-clean-rebuild-', dir=ROOT / 'output') as tmp:
            fresh = Path(tmp); generate(fresh); got = read(fresh / 'manifest.json')
            self.assertEqual(got['files'], self.manifest['files'])
            self.assertEqual(got['reports'], self.manifest['reports'])
            self.assertEqual(read(fresh / 'challenge-manifest.json'), read(self.output / 'challenge-manifest.json'))
            again = run_sources(fresh)
            self.assertEqual(set(again['reused']), set(contracts()))
            self.assertEqual(again['executed'], [])
            self.assertEqual(again['files'], got['files'])
            # Crash the final export group after all other groups are durable,
            # then resume all the way to the same complete source package.
            (fresh / 'checkpoints/finance-monthly.json').unlink()
            child = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_source_delivery.py'), '--output', str(fresh), '--crash-table', 'finance_monthly'], cwd=ROOT, capture_output=True, timeout=600)
            self.assertEqual(child.returncode, 97, child.stdout.decode(errors='replace'))
            self.assertFalse((fresh / 'candidate-ready.json').exists())
            generate(fresh); resumed = read(fresh / 'manifest.json')
            self.assertEqual(resumed['files'], got['files'])
            self.assertEqual(resumed['reports'], got['reports'])
            self.assertEqual(len(resumed['reused']), 24)
            self.assertEqual(resumed['executed'], ['finance_monthly'])

    def test_real_export_process_crash_uncommitted_group_and_resume(self):
        with tempfile.TemporaryDirectory(prefix='source-export-crash-', dir=ROOT / 'output') as tmp:
            root = Path(tmp)
            child = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_source_delivery.py'), '--output', str(root), '--crash-table', 'facility'], cwd=ROOT, capture_output=True, timeout=240)
            self.assertEqual(child.returncode, 97, child.stdout.decode(errors='replace'))
            self.assertFalse((root / 'candidate-ready.json').exists())
            self.assertFalse((root / 'checkpoints/facility.json').exists())
            # Recovery independently reruns the interrupted group; a separate clean
            # full export test covers continuation through all remaining tables.
            with self.assertRaisesRegex(ValueError, 'injected uncommitted'):
                run_sources(root, fail_table='cost_center')
            self.assertTrue((root / 'checkpoints/facility.json').exists())
            self.assertEqual(read(root / 'checkpoints/facility.json')['files'], [m for m in self.manifest['files'] if m['table'] == 'facility'])

    def test_corrupt_checkpoint_artifact_blocks_reuse_and_removes_ready_marker(self):
        with tempfile.TemporaryDirectory(prefix='source-cache-corruption-', dir=ROOT / 'output') as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'injected uncommitted'):
                run_sources(root, fail_table='cost_center')
            checkpoint = read(root / 'checkpoints/facility.json'); payload = root / checkpoint['files'][0]['path']
            with payload.open('ab') as stream:
                stream.write(b'CORRUPT')
            (root / 'candidate-ready.json').write_text('stale', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'checkpoint artifact corruption'):
                run_sources(root)
            self.assertFalse((root / 'candidate-ready.json').exists())
            self.assertEqual(read(root / 'manifest.json')['status'], 'FAILED')

    def test_real_replay_process_death_rolls_back_wal_transaction(self):
        package = read(self.output / 'challenge-manifest.json'); m = next(m for m in package['files'] if m['file_id'] == package['valid_control'])
        with tempfile.TemporaryDirectory(prefix='source-replay-crash-', dir=ROOT / 'output') as tmp:
            db = Path(tmp) / 'replay.sqlite3'; runner = Path(tmp) / 'crash_replay.py'
            runner.write_text("import sys,json\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nfrom healthcare_synthetic.source_reader import DeliveryReplay\nr=DeliveryReplay(sys.argv[2]);r.ingest(Path(sys.argv[3]),json.loads(sys.argv[4]),json.loads(sys.argv[5]),crash=True)\n", encoding='utf-8')
            child = subprocess.run([sys.executable, str(runner), str(ROOT / 'src'), str(db), str(self.output), json.dumps(m), json.dumps(contracts()['finance_monthly'])], capture_output=True, timeout=60)
            self.assertEqual(child.returncode, 97, child.stderr.decode(errors='replace'))
            replay = DeliveryReplay(db)
            try:
                self.assertEqual(replay.db.execute('SELECT count(*) FROM files').fetchone()[0], 0)
                self.assertEqual(replay.table_hash('finance_monthly')[1], 0)
                self.assertEqual(replay.ingest(self.output, m, contracts()['finance_monthly']), 'APPLIED')
            finally:
                replay.close()


if __name__ == '__main__':
    unittest.main()
