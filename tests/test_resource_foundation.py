"""Connected workforce/stock acceptance, deliberate faults and process recovery."""
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
from datetime import timedelta
from decimal import Context,Decimal,ROUND_HALF_UP,localcontext
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.resource_pipeline import GRAPH,run_resources
from healthcare_synthetic.resource_validation import ResourceValidator
from healthcare_synthetic.resource_stock_validation import StockValidator
from healthcare_synthetic.resource_review import render_resources,review_gate
from healthcare_synthetic.master_validation import timestamp
from validate_resource_data import inspect_resources


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


class ResourceFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=Path(os.environ.get('HEALTHCARE_RESOURCE_TEST_CANDIDATE',ROOT/'output/resource-foundation'))
        cls.cfg=read(ROOT/'config/resource-foundation-generation.json');cls.manifest=read(cls.base/'manifest.json');cls.schema=read(ROOT/'contracts/phase0/schema.json')
        cls.tables={name:[json.loads(line) for line in (cls.base/meta['file']).open(encoding='utf-8')] for name,meta in cls.manifest['canonical_files'].items()}
        cls.report=inspect_resources(cls.base);cls.workforce=cls.report['workforce'];cls.stock=cls.report['stock']
        cls.temp=tempfile.TemporaryDirectory(prefix='resource-tests-',dir=ROOT/'output');cls.work=Path(cls.temp.name)
        cls.workers={r['worker_assignment_id']:r for r in cls.tables['worker_assignment']}

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def labor(self,tables=None):return ResourceValidator(self.tables if tables is None else tables,self.schema,self.cfg)
    def inventory(self,tables=None):return StockValidator(self.tables if tables is None else tables,self.cfg)
    def change(self,table,index,values):
        tables=dict(self.tables);tables[table]=list(tables[table]);tables[table][index]={**tables[table][index],**values};return tables
    def final_worked(self):
        latest={}
        for r in self.tables['staff_shift']:
            if r['shift_id'] not in latest or r['revision_no']>latest[r['shift_id']]['revision_no']:latest[r['shift_id']]=r
        return latest

    def test_all_labor_and_stock_controls_pass(self):
        self.assertEqual(self.workforce['status'],'PASS',self.workforce['defects']);self.assertEqual(len(self.workforce['checks']),6)
        self.assertEqual(self.stock['status'],'PASS',self.stock['defects']);self.assertEqual(len(self.stock['checks']),3)
        self.assertEqual(self.manifest['generated_business_tables'],18);self.assertLessEqual(self.manifest['business_rows'],1958210)
        self.assertFalse(self.manifest['full_dataset_accepted']);self.assertEqual(self.manifest['solution_status'],'BLOCKED_FOR_SOLUTION')

    def test_all_fifteen_clinical_and_seven_operational_groups_pass(self):
        self.assertEqual(len(self.report['clinical']['checks']),15);self.assertEqual(len(self.report['operations']['checks']),7)
        self.assertEqual(self.report['clinical']['defects'],[]);self.assertEqual(self.report['operations']['defects'],[])

    def test_source_attending_and_all_bed_histories_are_preserved(self):
        parent=read(ROOT/'output/operational-flow/manifest.json')
        for name in parent['canonical_files']:
            if name!='clinical_event':self.assertEqual(self.manifest['canonical_files'][name]['sha256'],parent['canonical_files'][name]['sha256'],name)
        self.assertEqual(self.report['operations']['metrics']['occupied_seconds'],5085526680)

    def test_overtime_is_a_paid_subset(self):
        self.assertGreater(Decimal(self.workforce['metrics']['overtime_hours']),0)
        for r in self.tables['staff_shift']:self.assertLessEqual(Decimal(r['overtime_hours']),Decimal(r['worked_hours'])-Decimal(r['unpaid_break_hours']))
        i=next(i for i,r in enumerate(self.tables['staff_shift']) if r['attendance_status']=='WORKED')
        with self.assertRaisesRegex(ValueError,'overtime exceeds'):self.labor(self.change('staff_shift',i,{'overtime_hours':'99.000000'})).check_labor_time()

    def test_labor_costs_recompute_from_rates_once(self):
        self.assertGreater(Decimal(self.workforce['metrics']['finalized_labor_cost']),0)
        self.assertGreater(self.workforce['metrics']['late_rate_revisions'],0)
        self.assertEqual(self.workforce['metrics']['late_attendance_revisions'],self.cfg['late_attendance_corrections'])

    def test_wrong_labor_rate_is_rejected(self):
        i=next(i for i,r in enumerate(self.tables['staff_shift']) if r['attendance_status']=='WORKED')
        r=self.tables['staff_shift'][i];bad=self.change('staff_shift',i,{'loaded_cost':str(Decimal(r['loaded_cost'])+Decimal('.01'))})
        with self.assertRaisesRegex(ValueError,'untraceable labor'):self.labor(bad).check_labor_cost()

    def test_elapsed_break_and_productive_hours_must_reconcile(self):
        i=next(i for i,r in enumerate(self.tables['staff_shift']) if r['attendance_status']=='WORKED')
        with self.assertRaisesRegex(ValueError,'do not reconcile'):self.labor(self.change('staff_shift',i,{'productive_hours':'0.000000'})).check_labor_time()

    def test_dst_and_open_attendance_have_observed_semantics(self):
        elapsed={r['worked_hours'] for r in self.tables['staff_shift'] if r['attendance_status']=='WORKED'}
        self.assertTrue({'11.000000','13.000000'}<=elapsed)
        opened=[r for r in self.final_worked().values() if r['actual_start'] and r['actual_end'] is None]
        self.assertGreater(len(opened),0)
        self.assertTrue(all(r['attendance_status']=='PUBLISHED' and Decimal(r['worked_hours'])==Decimal(r['loaded_cost'])==0 for r in opened))

    def test_future_roster_actuals_are_rejected(self):
        i=next(i for i,r in enumerate(self.tables['staff_shift']) if r['attendance_status']=='PUBLISHED' and r['actual_start'] is None)
        with self.assertRaisesRegex(ValueError,'leaks actual'):self.labor(self.change('staff_shift',i,{'worked_hours':'1.000000'})).check_schema_history()

    def test_forecast_cancellations_and_unknown_early_history_are_explicit(self):
        m=self.workforce['metrics'];self.assertGreater(m['retained_initial_publications'],1000);self.assertGreater(m['cancelled_forecast_slots'],0)
        histories=self.labor().histories
        final_only=[rows for rows in histories.values() if len(rows)==1 and rows[0]['attendance_status']=='WORKED']
        self.assertGreater(len(final_only),10000)
        self.assertTrue(all(rows[0]['known_from']>=rows[0]['actual_end'] for rows in final_only))

    def test_absence_and_agency_have_distinct_attendance_and_cost(self):
        m=self.workforce['metrics'];self.assertGreaterEqual(m['february_absences'],self.cfg['february_absences']);self.assertGreaterEqual(m['agency_replacements'],60)
        latest=self.final_worked();absences={r['shift_id']:r for r in latest.values() if r['attendance_status']=='ABSENT'}
        for r in latest.values():
            if r['source_record_id'].startswith('replace/'):
                absent_id=r['source_record_id'].split('/')[1];self.assertIn(absent_id,absences)
                self.assertNotEqual(self.workers[r['worker_assignment_id']]['worker_id'],self.workers[absences[absent_id]['worker_assignment_id']]['worker_id'])
                self.assertEqual(Decimal(absences[absent_id]['worked_hours']),0)

    def test_no_worker_can_hold_overlapping_worked_shifts(self):
        r=next(r for r in self.final_worked().values() if r['attendance_status']=='WORKED')
        duplicate={**r,'shift_id':'deliberate-overlap','shift_version_id':'deliberate-overlap-v1','revision_no':1,'known_to':None}
        tables=dict(self.tables);tables['staff_shift']=[*tables['staff_shift'],duplicate]
        with self.assertRaisesRegex(ValueError,'overlapping worked'):self.labor(tables).check_labor_time()

    def test_worked_clinical_credentials_and_skill_mix_are_enforced(self):
        i=next(i for i,r in enumerate(self.tables['worker_assignment']) if r['role']=='RN')
        w=self.tables['worker_assignment'][i]
        # Mutate all snapshots of a represented working nurse so no later version
        # can accidentally restore the credential during the same block.
        tables=dict(self.tables);tables['worker_assignment']=[{**r,'credential_valid_to':'2020-01-01'} if r['worker_id']==w['worker_id'] else r for r in tables['worker_assignment']]
        with self.assertRaisesRegex(ValueError,'credential'):self.labor(tables).check_labor_time()

    def test_clinical_authors_have_actual_qualified_attendance(self):
        self.assertGreater(self.workforce['metrics']['rn_authored_medication_events'],90000)
        self.assertEqual(self.workforce['metrics']['absent_blocks']>0,True)

    def test_missing_actual_clinical_attendance_is_rejected(self):
        tables=dict(self.tables);tables['staff_shift']=[]
        with self.assertRaisesRegex(ValueError,'no actual working coverage'):self.labor(tables).check_activity_links()

    def test_operative_concurrency_requires_actual_rn_coverage(self):
        locations={r['location_id']:r for r in self.tables['location']}
        tables=dict(self.tables);tables['staff_shift']=[r for r in tables['staff_shift'] if not (self.workers[r['worker_assignment_id']]['role']=='RN' and locations[r['location_id']]['location_code']=='OR')]
        with self.assertRaisesRegex(ValueError,'circulating-RN coverage'):self.labor(tables).check_activity_links()

    def test_monthly_census_responding_nursing_coverage_meets_targets(self):
        ratios=self.workforce['metrics']['monthly_rn_coverage'];self.assertEqual(len(ratios),36)
        self.assertTrue(all(Decimal('.9')<=Decimal(r)<=Decimal('1.2') for r in ratios.values()))
        self.assertGreater(Decimal(self.workforce['metrics']['rn_required_hours']),300000)

    def test_prorated_workforce_controls_are_row_order_invariant(self):
        tables={**self.tables,'staff_shift':list(reversed(self.tables['staff_shift']))}
        with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
            validator=self.labor(tables);validator.check_coverage()
        for key,value in validator.metrics.items():self.assertEqual(value,self.workforce['metrics'][key],key)

    def test_stock_quantity_and_value_roll_forwards(self):
        self.assertGreater(Decimal(self.stock['metrics']['closing_inventory_value']),0)
        self.assertEqual(self.stock['metrics']['unexplained_negative_stock'],0)
        self.assertGreaterEqual(self.stock['metrics']['expiry_movements'],self.cfg['opening_expiry_lots'])

    def test_point_of_use_stock_and_clinical_group_quantities_reconcile(self):
        self.assertGreater(self.stock['metrics']['actual_medication_links'],100000)
        self.assertGreater(self.stock['metrics']['selected_supply_requirements'],50000)
        self.assertGreater(self.stock['metrics']['reconciled_patient_consumption_groups'],10000)

    def test_issue_before_receipt_is_rejected(self):
        tables=dict(self.tables);tables['inventory_movement']=[r for r in tables['inventory_movement'] if r['movement_type'] not in ('OPENING','RECEIPT')]
        validator=self.inventory(tables);validator.book_closing={}
        with self.assertRaisesRegex(ValueError,'before receipt|before eligible receipt'):validator.check_eligibility_links()

    def test_expired_lot_is_rejected_at_point_of_use(self):
        opening={r['lot_id'] for r in self.tables['inventory_movement'] if r['movement_type']=='OPENING'}
        medications={r['catalog_item_id'] for r in self.tables['catalog_item'] if r['domain']=='MEDICATION'}
        target=next(r for r in self.tables['inventory_movement'] if r['movement_type']=='CONSUME' and Decimal(r['nonpatient_waste_base'])==0 and r['lot_id'] in opening and r['catalog_item_id'] in medications)
        tables=dict(self.tables);tables['inventory_movement']=[{**r,'expires_on':'2022-12-31'} if r['lot_id']==target['lot_id'] else r for r in tables['inventory_movement']]
        validator=self.inventory(tables);validator.book_closing={}
        with self.assertRaisesRegex(ValueError,'expired|before eligible receipt|stockout|FEFO|expiry'):validator.check_eligibility_links()

    def test_wrong_price_and_pack_conversion_are_rejected(self):
        i=next(i for i,r in enumerate(self.tables['inventory_movement']) if r['movement_type']=='RECEIPT');r=self.tables['inventory_movement'][i]
        bad=self.change('inventory_movement',i,{'unit_cost':str(Decimal(r['unit_cost'])+Decimal('1'))})
        with self.assertRaisesRegex(ValueError,'cost|price|lot'):self.inventory(bad).check_ledger()
        qty=Decimal(r['quantity_base'])+Decimal(1);cost=(qty*Decimal(r['unit_cost'])).quantize(Decimal('.01'))
        bad=self.change('inventory_movement',i,{'quantity_base':format(qty,'f'),'extended_cost':format(cost,'f')})
        with self.assertRaisesRegex(ValueError,'pack/base'):self.inventory(bad).check_ledger()

    def test_unbalanced_transfer_or_return_is_rejected(self):
        target=next(r for r in self.tables['inventory_movement'] if r['movement_type']=='RETURN')
        tables=dict(self.tables);tables['inventory_movement']=[r for r in tables['inventory_movement'] if r['movement_id']!=target['movement_id']]
        with self.assertRaisesRegex(ValueError,'unbalanced stock transfer'):self.inventory(tables).check_ledger()

    def test_lot_repricing_and_untraceable_reversal_are_rejected(self):
        i=next(i for i,r in enumerate(self.tables['inventory_movement']) if r['reverses_movement_id'])
        bad=self.change('inventory_movement',i,{'reverses_movement_id':'missing-source-movement'})
        with self.assertRaisesRegex(ValueError,'orphan'):self.inventory(bad).check_ledger()

    def test_expiry_and_nonpatient_waste_are_separate_from_patient_use(self):
        m=self.stock['metrics'];self.assertGreater(Decimal(m['nonpatient_waste_quantity']),0);self.assertGreater(Decimal(m['nonpatient_consumption_cost']),0)
        self.assertGreaterEqual(m['unopened_return_groups'],30)
        self.assertGreater(Decimal(m['patient_consumption_cost']),Decimal(m['nonpatient_consumption_cost']))

    def test_shortages_change_actual_services_without_stale_facts(self):
        m=self.stock['metrics'];self.assertEqual(m['stockout_windows'],30);self.assertEqual(m['absence_delay_windows'],30)
        self.assertGreaterEqual(m['changed_operative_services'],60);self.assertGreater(Decimal(m['maximum_operative_delay_minutes']),0)

    def test_declared_stockouts_are_probed_before_case_cart_arrival(self):
        self.assertGreaterEqual(self.stock['metrics']['stockout_point_of_use_probes'],30)

    def test_resource_notes_reject_unsupported_or_future_assessments(self):
        from healthcare_synthetic.resource_validation import ResourceClinicalValidator
        from healthcare_synthetic.clinical_pipeline import load_master
        ccfg=read(ROOT/'config/clinical-history-generation.json');master,_,_=load_master(ccfg);policy=read(ROOT/'contracts/clinical-history-policy.json')
        i=next(i for i,r in enumerate(self.tables['clinical_event']) if r['source_record_id'].endswith('/resource-response'))
        bad=self.change('clinical_event',i,{'text_value':self.tables['clinical_event'][i]['text_value']+' The patient will recover.'})
        validator=ResourceClinicalValidator(bad,self.schema,ccfg,policy,master)
        result=validator.check('DOCUMENTS');self.assertEqual(result['status'],'FAIL');self.assertIn('resource document grammar',result['failures'][0]['reason'])

    def test_review_is_hundred_case_content_bound_and_order_invariant(self):
        body,selection=render_resources(self.tables,self.cfg);decision=read(ROOT/'reviews/resource-foundation-review.json')
        self.assertEqual(selection['cases'],100);self.assertEqual(selection['resource_shortage_windows'],60)
        self.assertEqual(review_gate(selection,decision)['status'],'PASS')
        self.assertEqual(review_gate({**selection,'selected_facts_sha256':'changed'},decision)['status'],'PENDING_REVIEW')
        reordered={name:list(reversed(rows)) for name,rows in self.tables.items()}
        other,other_selection=render_resources(reordered,self.cfg);self.assertEqual(body,other);self.assertEqual(selection,other_selection)
        self.assertEqual(body.encode(),(ROOT/'reviews/resource-foundation-sample.md').read_bytes())

    def test_independent_persisted_files_and_mirrors(self):
        self.assertEqual(self.report['artifact_integrity'],'PASS');self.assertEqual(self.report['gate_status'],'RESOURCE_FOUNDATION_PASSED',self.report['defects'])

    def test_oracles_do_not_import_generators(self):
        for name in ('resource_validation','resource_stock_validation'):
            tree=ast.parse((ROOT/f'src/healthcare_synthetic/{name}.py').read_text())
            imported=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
            self.assertFalse(any('generation' in module or 'workforce' in module or 'inventory' in module or module.endswith('core') or 'pipeline' in module for module in imported))

    def test_frozen_table_and_whole_release_caps_cannot_be_exceeded(self):
        tables=dict(self.tables);tables['staff_shift']=[tables['staff_shift'][0]]*70001
        with self.assertRaisesRegex(ValueError,'budget exceeded: staff_shift'):self.labor(tables).check_budget()

    def command(self,output,*options):
        return subprocess.run([sys.executable,str(ROOT/'scripts/generate_resource_foundation.py'),'--output',str(output),*options],capture_output=True,text=True,timeout=2400)

    def test_clean_rebuild_cached_resume_and_complete_hash_match(self):
        output=self.work/'clean-rebuild';result=self.command(output)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);m=read(output/'manifest.json');self.assertEqual(m['business_sha256'],self.manifest['business_sha256'])
        result=self.command(output);self.assertEqual(result.returncode,0,result.stdout+result.stderr);m=read(output/'manifest.json')
        self.assertEqual(m['executed'],[]);self.assertEqual(set(m['reused']),set(GRAPH))
        # A syntactically valid but noncanonical persisted file must fail before
        # any saved PASS control can be trusted. Reuse the disposable rebuild.
        target=output/m['canonical_files']['staff_shift']['file']
        with target.open('rb+') as stream:
            content=stream.read();stream.seek(0);stream.write(b' '+content)
        with self.assertRaisesRegex(ValueError,'checksum|count|canonical'):
            inspect_resources(output)

    def test_real_process_crash_rolls_back_and_resumes(self):
        output=self.work/'crash-recovery';output.mkdir()
        with sqlite3.connect(self.base/'checkpoints.sqlite3') as source,sqlite3.connect(output/'checkpoints.sqlite3') as target:
            source.backup(target);target.execute("DELETE FROM stages WHERE name='validation'");target.commit()
        (output/'manifest.json').write_text(json.dumps({'profile':'CONNECTED_WORKFORCE_AND_STOCK'}))
        crashed=self.command(output,'--crash-stage','validation');self.assertEqual(crashed.returncode,97,crashed.stdout+crashed.stderr)
        with sqlite3.connect(output/'checkpoints.sqlite3') as c:self.assertEqual(c.execute("SELECT count(*) FROM stages WHERE name='validation'").fetchone()[0],0)
        self.assertFalse((output/'candidate-ready.json').exists())
        resumed=self.command(output);self.assertEqual(resumed.returncode,0,resumed.stdout+resumed.stderr);m=read(output/'manifest.json')
        self.assertEqual(m['executed'],['validation']);self.assertEqual(m['business_sha256'],self.manifest['business_sha256'])

    def test_corrupt_checkpoint_cannot_publish_ready(self):
        output=self.work/'corrupt';output.mkdir()
        from healthcare_synthetic.engine import Store
        store=Store(output/'checkpoints.sqlite3');store.db.execute('INSERT INTO stages VALUES (?,?,?,?,?,?)',('coordination','bad','bad','{}','corrupt',0));store.db.commit();store.close()
        with self.assertRaisesRegex(ValueError,'checkpoint corruption'):run_resources(output_dir=output)
        self.assertFalse((output/'candidate-ready.json').exists())

    def test_changed_seed_invalidates_descendants_before_failure(self):
        output=self.work/'changed-seed';output.mkdir()
        with sqlite3.connect(self.base/'checkpoints.sqlite3') as c:row=c.execute("SELECT name,local_hash,input_hash,payload,checksum,row_count FROM stages WHERE name='validation'").fetchone()
        from healthcare_synthetic.engine import Store
        store=Store(output/'checkpoints.sqlite3');store.db.execute('INSERT INTO stages VALUES (?,?,?,?,?,?)',row);store.db.commit();store.close()
        (output/'manifest.json').write_text(json.dumps({'profile':'CONNECTED_WORKFORCE_AND_STOCK'}));(output/'candidate-ready.json').write_text('{}')
        path=self.work/'changed-seed.json';path.write_text(json.dumps({**self.cfg,'seed':self.cfg['seed']+1}))
        result=self.command(output,'--config',str(path),'--fail-stage','coordination');self.assertNotEqual(result.returncode,0)
        m=read(output/'manifest.json');self.assertEqual(m['status'],'FAILED');self.assertIn('validation',m['invalidated']);self.assertFalse((output/'candidate-ready.json').exists())

    def test_unreviewed_configuration_cannot_silently_change(self):
        path=self.work/'invalid-profile.json';path.write_text(json.dumps({**self.cfg,'rn_hours_per_patient_day':'0'}))
        with self.assertRaisesRegex(ValueError,'reviewed resource'):run_resources(path,self.work/'invalid-profile')

    def test_delivered_history_keeps_prior_assertion_until_replacement_arrives(self):
        from healthcare_synthetic.resource_queries import delivered_staff
        histories=self.labor().histories
        rows=next(sorted(rows,key=lambda r:r['revision_no']) for rows in histories.values() if len(rows)>1)
        old,new=rows[0],rows[1]
        self.assertEqual(delivered_staff(self.tables,new['recorded_at'])[old['shift_id']]['shift_version_id'],old['shift_version_id'])
        self.assertEqual(delivered_staff(self.tables,new['export_available_at'])[old['shift_id']]['shift_version_id'],new['shift_version_id'])

    def test_asof_labor_does_not_add_all_knowledge_versions(self):
        from healthcare_synthetic.resource_queries import labor_totals
        totals=labor_totals(self.tables,'2026-01-10T23:59:59Z')
        self.assertEqual(Decimal(totals['totals']['loaded_cost']),Decimal(self.workforce['metrics']['finalized_labor_cost']))
        self.assertEqual(totals['captured_blocks'],self.workforce['metrics']['shift_blocks'])

    def test_late_stock_reversal_preserves_historical_book_state(self):
        from healthcare_synthetic.resource_queries import inventory_ledger_at
        before=inventory_ledger_at(self.tables,'2025-12-31T23:59:59-06:00','2026-01-01T09:00:00Z')
        after=inventory_ledger_at(self.tables,'2026-01-01T05:59:59Z','2026-01-04T09:00:00Z')
        self.assertEqual(Decimal(after['total_book_value_usd']),Decimal(self.stock['metrics']['closing_inventory_value']))
        self.assertGreater(Decimal(after['total_book_value_usd']),Decimal(before['total_book_value_usd']))


if __name__=='__main__':unittest.main()
