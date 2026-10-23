"""Connected finance acceptance, falsifiable monetary controls and process recovery."""
import copy
import calendar
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from datetime import date,timedelta
from decimal import Context,Decimal,ROUND_HALF_UP,localcontext
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.core import canonical
from healthcare_synthetic.financial_pipeline import run_financial,finance_schema,GRAPH
from healthcare_synthetic.financial_validation import FinancialValidator
from healthcare_synthetic.financial_review import render_financial,review_gate
from healthcare_synthetic.financial_common import Context as FinanceContext,delivered_assignments,at,stamp
from healthcare_synthetic.financial_planning import plan_amount
from healthcare_synthetic.financial_queries import claim_history,selected_costs,select_monthly,unique_events,variance
from validate_financial_data import inspect_financial
from validate_clinical_data import files_at


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


class FinancialHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=Path(os.environ.get('HEALTHCARE_FINANCIAL_TEST_CANDIDATE',ROOT/'output/financial-history'))
        cls.cfg=read(ROOT/'config/financial-history-generation.json');cls.manifest=read(cls.base/'manifest.json');cls.schema=finance_schema()
        cls.report=inspect_financial(cls.base);cls.tables=files_at(cls.base,cls.manifest)
        cls.temp=tempfile.TemporaryDirectory(prefix='finance-tests-',dir=ROOT/'output');cls.work=Path(cls.temp.name)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        self.decimal_context=localcontext(Context(prec=38,rounding=ROUND_HALF_UP));self.decimal_context.__enter__()

    def tearDown(self):self.decimal_context.__exit__(None,None,None)

    def validator(self,tables=None):return FinancialValidator(self.tables if tables is None else tables,self.cfg,self.schema)
    def change(self,table,index,fields):
        tables=dict(self.tables);tables[table]=list(tables[table]);tables[table][index]={**tables[table][index],**fields};return tables
    def cache_copy(self,name):
        path=self.work/name;path.mkdir();source=sqlite3.connect(self.base/'checkpoints.sqlite3');dest=sqlite3.connect(path/'checkpoints.sqlite3')
        try:source.backup(dest)
        finally:dest.close();source.close()
        shutil.copy2(self.base/'manifest.json',path/'manifest.json');shutil.copy2(self.base/'candidate-ready.json',path/'candidate-ready.json');return path

    def test_all_financial_controls_and_exact_budget_pass(self):
        self.assertEqual(self.report['defects'],[]);self.assertEqual(len(self.report['checks']),9)
        self.assertEqual(self.report['gate_status'],'FINANCIAL_HISTORY_PASSED');self.assertEqual(self.manifest['generated_business_tables'],25)
        self.assertEqual(sum(t['planned_rows'] for t in self.schema['tables']),1995215)
        amendment=read(ROOT/'contracts/financial-history-policy.json')['record_budget_amendment']
        for table in self.schema['tables']:
            if table['name'] in amendment:self.assertEqual(table['planned_rows'],amendment[table['name']])
        self.assertEqual(amendment['planned_total']+amendment['reserve_rows'],2000000)
        self.assertLessEqual(self.manifest['business_rows'],1995215);self.assertGreaterEqual(self.manifest['business_rows'],1000000)
        self.assertEqual(sum(self.manifest['rows_by_table'].values()),self.manifest['business_rows']);self.assertFalse(self.manifest['full_dataset_accepted'])
        self.assertEqual(self.manifest['solution_status'],'BLOCKED_FOR_SOLUTION')

    def test_parent_histories_remain_byte_identical(self):
        parent=read(ROOT/'output/resource-foundation/manifest.json')
        for name,meta in parent['canonical_files'].items():
            if name!='catalog_item':self.assertEqual(meta['sha256'],self.manifest['canonical_files'][name]['sha256'],name)
        self.assertEqual(self.manifest['catalog_extension_rows'],5)

    def test_independent_persisted_files_and_checkpoints(self):
        self.assertEqual(self.report['artifact_integrity'],'PASS');self.assertEqual(self.report['business_sha256'],self.manifest['business_sha256'])
        self.assertGreater(self.manifest['checkpoint_mirror_rows'],0);self.assertGreater(self.manifest['review_mirror_rows'],0)

    def test_wrong_charge_amount_or_price_is_rejected(self):
        r=self.tables['service_charge'][0]
        with self.assertRaisesRegex(ValueError,'arithmetic'):self.validator(self.change('service_charge',0,{'billed_amount':str(Decimal(r['billed_amount'])+Decimal('.01'))})).check_charges()
        i=next(i for i,r in enumerate(self.tables['service_charge']) if r['revenue_category']=='ROOM');r=self.tables['service_charge'][i]
        units=Decimal(r['units'])+Decimal('1.000000');amount=(units*Decimal(r['unit_price'])).quantize(Decimal('.01'))
        with self.assertRaisesRegex(ValueError,'room day'):self.validator(self.change('service_charge',i,{'units':str(units),'billed_amount':str(amount)})).check_charges()
        i=next(i for i,r in enumerate(self.tables['service_charge']) if r['unit_code']=='holding_hours');r=self.tables['service_charge'][i]
        units=Decimal(r['units'])+Decimal('1.000000');amount=(units*Decimal(r['unit_price'])).quantize(Decimal('.01'))
        with self.assertRaisesRegex(ValueError,'holding hours'):self.validator(self.change('service_charge',i,{'units':str(units),'billed_amount':str(amount)})).check_charges()

    def test_month_spanning_charge_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'crosses accounting month'):self.validator(self.change('service_charge',0,{'service_to':'2026-02-01'})).check_charges()

    def test_unperformed_or_unrelated_service_cannot_be_charged(self):
        i=next(i for i,r in enumerate(self.tables['service_charge']) if r['clinical_event_version_id'])
        other=next(r for r in self.tables['clinical_event'] if r['status']!='COMPLETED')
        with self.assertRaisesRegex(ValueError,'unperformed|unrelated'):self.validator(self.change('service_charge',i,{'clinical_event_version_id':other['clinical_event_version_id']})).check_charges()

    def test_claim_header_line_and_contract_estimate_reconcile(self):
        r=self.tables['claim'][0]
        with self.assertRaisesRegex(ValueError,'header'):self.validator(self.change('claim',0,{'original_billed_amount':str(Decimal(r['original_billed_amount'])+Decimal('.01'))})).check_claims()
        line=self.tables['claim_line'][0]
        with self.assertRaisesRegex(ValueError,'reimbursement'):self.validator(self.change('claim_line',0,{'expected_allowed_amount':str(Decimal(line['expected_allowed_amount'])+Decimal('.01'))})).check_claims()

    def test_charge_cannot_appear_in_two_original_claims(self):
        tables=dict(self.tables);tables['claim_line']=self.tables['claim_line']+[dict(self.tables['claim_line'][0],claim_line_id='duplicate')]
        with self.assertRaisesRegex(ValueError,'duplicated across original claims'):self.validator(tables).check_claims()

    def test_opening_ar_is_context_not_current_revenue(self):
        openings=[r for r in self.tables['claim_event'] if r['event_type']=='OPENING'];self.assertGreater(len(openings),1000)
        self.assertTrue(all(Decimal(r['cash_delta'])==Decimal(r['recognized_revenue_delta'])==Decimal(r['ar_delta'])==0 for r in openings))
        self.assertTrue(all(r['service_to']>='2023-01-01' for r in self.tables['financial_posting'] if r['source_domain']=='REVENUE'))
        i=next(i for i,r in enumerate(self.tables['claim_event']) if r['event_type']=='OPENING')
        with self.assertRaisesRegex(ValueError,'state event'):self.validator(self.change('claim_event',i,{'ar_delta':'1.00'})).check_events()

    def test_submission_transfers_ar_without_new_revenue(self):
        rows=[r for r in self.tables['claim_event'] if r['event_type']=='SUBMITTED'];self.assertGreater(len(rows),40000)
        self.assertTrue(all(Decimal(r['ar_delta'])>0 and Decimal(r['recognized_revenue_delta'])==0 for r in rows))

    def test_pending_denial_is_not_an_automatic_writeoff(self):
        denials=[r for r in self.tables['claim_event'] if r['event_type']=='DENIED'];self.assertGreater(len(denials),100)
        self.assertTrue(all(r['claim_line_id'] and Decimal(r['writeoff_delta'])==Decimal(r['ar_delta'])==0 for r in denials))
        self.assertGreater(self.report['review_selection']['strata']['pending_denial'],0)

    def test_cash_and_revenue_are_distinct(self):
        self.assertTrue(all(Decimal(r['recognized_revenue_delta'])==0 for r in self.tables['claim_event'] if r['event_type'] in ('PAYMENT','PATIENT_PAYMENT')))
        i=next(i for i,r in enumerate(self.tables['claim_event']) if r['event_type']=='PAYMENT')
        with self.assertRaisesRegex(ValueError,'payment confuses'):self.validator(self.change('claim_event',i,{'recognized_revenue_delta':'1.00'})).check_events()

    def test_refunds_reversals_and_posting_links_have_opposite_effect(self):
        types=self.report['metrics']['claim_event_types'];self.assertGreater(types['REFUND'],0);self.assertGreater(types['REVERSAL'],0)
        self.assertGreater(self.report['metrics']['linked_posting_reversals'],0)
        i=next(i for i,r in enumerate(self.tables['claim_event']) if r['event_type']=='REFUND')
        with self.assertRaisesRegex(ValueError,'unlinked'):self.validator(self.change('claim_event',i,{'reverses_claim_event_id':None})).check_events()

    def test_unbalanced_journal_is_rejected(self):
        i=next(i for i,r in enumerate(self.tables['financial_posting']) if Decimal(r['debit_amount'])>0);r=self.tables['financial_posting'][i]
        with self.assertRaisesRegex(ValueError,'do not balance'):self.validator(self.change('financial_posting',i,{'debit_amount':str(Decimal(r['debit_amount'])+Decimal('.01'))})).check_journals()

    def test_balanced_but_false_journal_fails_independent_source_oracle(self):
        rows=self.tables['financial_posting'];first=rows[0];indexes=[i for i,r in enumerate(rows) if r['journal_id']==first['journal_id']]
        tables=dict(self.tables);tables['financial_posting']=list(rows)
        debit=next(i for i in indexes if Decimal(rows[i]['debit_amount'])>0);credit=next(i for i in indexes if Decimal(rows[i]['credit_amount'])>0)
        tables['financial_posting'][debit]={**rows[debit],'debit_amount':str(Decimal(rows[debit]['debit_amount'])+Decimal('.01'))}
        tables['financial_posting'][credit]={**rows[credit],'credit_amount':str(Decimal(rows[credit]['credit_amount'])+Decimal('.01'))}
        with self.assertRaisesRegex(ValueError,'independent oracle'):self.validator(tables).check_journals()

    def test_inventory_purchase_consumption_and_closing_asset_reconcile(self):
        self.assertEqual(Decimal(self.report['metrics']['closing_inventory']),Decimal('6210.92'))
        self.assertLess(Decimal(self.report['metrics']['ledger_totals']['AP']),0)

    def test_labor_revisions_salary_and_unfinished_shift_accrual_are_costed(self):
        self.assertGreater(Decimal(self.report['metrics']['admin_salary']),0);self.assertGreater(Decimal(self.report['metrics']['unfinished_shift_accrual']),0)
        catalog={r['catalog_item_id']:r for r in self.tables['catalog_item']}
        costs=sum((Decimal(r['credit_amount'])-Decimal(r['debit_amount']) for r in self.tables['financial_posting'] if r['source_domain'] in ('WORKFORCE','ACCRUAL') and catalog[r['account_catalog_id']]['code']=='PAYROLL_PAYABLE'),Decimal(0))
        self.assertGreater(Decimal(self.report['metrics']['opening_earned_payroll']),0)
        self.assertEqual(costs+Decimal(self.report['metrics']['opening_earned_payroll']),Decimal('47658801.10')+Decimal(self.report['metrics']['admin_salary'])+Decimal(self.report['metrics']['unfinished_shift_accrual']))
        workers={r['worker_assignment_id']:r for r in self.tables['worker_assignment']};history=defaultdict(list);final={}
        for w in workers.values():history[w['worker_id']].append(w)
        for r in self.tables['staff_shift']:
            if r['shift_id'] not in final or r['revision_no']>final[r['shift_id']]['revision_no']:final[r['shift_id']]=r
        captured=sum((Decimal(r['loaded_cost']) for r in final.values() if workers[r['worker_assignment_id']]['role']=='ADMIN'),Decimal(0))
        entitlement=Decimal(0)
        for wid,rows in sorted(history.items()):
            assertions=delivered_assignments(rows,'2026-01-10T23:59:59Z')
            for year in (2023,2024,2025):
                for m in range(1,13):
                    parts=defaultdict(Decimal);n=calendar.monthrange(year,m)[1]
                    for i in range(n):
                        d=date(year,m,1)+timedelta(days=i);when=stamp(at(d,12))
                        valid=[w for w in assertions if w['valid_from']<=when<(w['valid_to'] or '9999') and w['hire_date']<=str(d)<(w['termination_date'] or '9999')]
                        if valid:
                            w=max(valid,key=lambda w:w['revision_no'])
                            if w['role']=='ADMIN':parts[w['cost_center_id']]+=Decimal(w['fte'])*Decimal(w['hourly_cost_rate'])*2080/12/n
                    entitlement+=sum((v.quantize(Decimal('.01')) for v in parts.values()),Decimal(0))
        self.assertEqual(entitlement,captured+Decimal(self.report['metrics']['admin_salary']))

    def test_billed_plus_unbilled_ar_equals_enterprise_control(self):
        m=self.report['metrics'];self.assertEqual(Decimal(m['closing_claim_ar'])+Decimal(m['unbilled_service_ar']),Decimal(m['closing_enterprise_ar']))

    def test_treasury_settles_known_obligations_and_cash_stays_funded(self):
        metrics=self.report['metrics'];self.assertGreater(Decimal(metrics['treasury_disbursements']),0)
        self.assertEqual(Decimal(metrics['ledger_totals']['CASH']),Decimal(metrics['opening_operating_cash'])+Decimal(metrics['current_cash'])-Decimal(metrics['treasury_disbursements']))
        catalog={r['catalog_item_id']:r['code'] for r in self.tables['catalog_item']}
        cash=[Decimal(r['amount']) for r in self.tables['finance_monthly'] if r['scenario']=='ACTUAL' and catalog.get(r['account_catalog_id'])=='CASH']
        self.assertGreater(min(cash),0)
        payments=[r for r in self.tables['financial_posting'] if r['source_group_key'].startswith(('payroll-settlement/','supplier-settlement/'))]
        self.assertGreater(len(payments),400);self.assertTrue(all(r['posting_date']<='2025-12-31' and r['posting_date'][:7]>r['source_group_key'].split('/')[-1] for r in payments))

    def test_direct_and_pooled_expense_is_counted_once(self):
        p=self.report['metrics']['selected_allocated_costs'];allocated=sum(map(Decimal,p.values()))
        totals=self.report['metrics']['ledger_totals'];expense=sum((Decimal(totals.get(k,'0')) for k in ('LABOR_POOL','DRUG_POOL','SUPPLY_POOL','OVERHEAD_POOL')),Decimal(0))
        self.assertEqual(allocated,expense);self.assertGreater(Decimal(p['NONPATIENT']),0)

    def test_wrong_allocation_cent_or_driver_is_rejected(self):
        i=next(i for i,r in enumerate(self.tables['cost_allocation']) if r['destination_type']=='PATIENT');r=self.tables['cost_allocation'][i]
        with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
            with self.assertRaisesRegex(ValueError,'allocated cents'):self.validator(self.change('cost_allocation',i,{'allocated_amount':str(Decimal(r['allocated_amount'])+Decimal('.01'))})).check_allocations()
            with self.assertRaisesRegex(ValueError,'weights/destinations'):self.validator(self.change('cost_allocation',i,{'driver_quantity':str(Decimal(r['driver_quantity'])+Decimal('1.000000'))})).check_allocations()

    def test_daily_source_expense_cannot_be_allocated_again(self):
        i=next(i for i,r in enumerate(self.tables['financial_posting']) if r['source_domain']=='WORKFORCE')
        with self.assertRaisesRegex(ValueError,'allocated twice'):self.validator(self.change('financial_posting',i,{'eligible_for_allocation':True})).check_journals()

    def test_allocation_vintages_are_selected_not_added(self):
        before=selected_costs(self.tables,'2024-05-06T00:00:00Z');after=selected_costs(self.tables,'2024-05-10T00:00:00Z')
        self.assertNotEqual(before['selected_runs'],after['selected_runs']);self.assertEqual(before['totals'],after['totals'])

    def test_monthly_movement_and_closing_balances_reconcile(self):
        self.assertGreater(self.report['metrics']['monetary_actual_reconciliations'],18000)
        i=next(i for i,r in enumerate(self.tables['finance_monthly']) if r['scenario']=='ACTUAL' and r['amount'] is not None);r=self.tables['finance_monthly'][i]
        with self.assertRaisesRegex(ValueError,'Axiom actual'):self.validator(self.change('finance_monthly',i,{'amount':str(Decimal(r['amount'])+Decimal('.01'))})).check_monthly()

    def test_statistics_do_not_add_currency_fte_and_patient_days(self):
        i=next(i for i,r in enumerate(self.tables['finance_monthly']) if r['measure_code']=='FTE')
        with self.assertRaisesRegex(ValueError,'statistical measure'):self.validator(self.change('finance_monthly',i,{'unit_code':'USD'})).check_monthly()
        other=next(r['facility_id'] for r in self.tables['facility'] if r['facility_id']!=self.tables['finance_monthly'][i]['facility_id'])
        with self.assertRaisesRegex(ValueError,'affiliation'):self.validator(self.change('finance_monthly',i,{'facility_id':other})).check_monthly()

    def test_future_actuals_are_unavailable_to_december_consumers(self):
        self.assertEqual(select_monthly(self.tables,'ACTUAL','2025-12-01','2025-12-31T23:59:59Z'),[])
        initial=select_monthly(self.tables,'ACTUAL','2025-12-01','2026-01-06T23:59:59Z');final=select_monthly(self.tables,'ACTUAL','2025-12-01','2026-01-10T23:59:59Z')
        self.assertEqual(len(initial),573);self.assertEqual(len(final),573);self.assertNotEqual({r['vintage_id'] for r in initial},{r['vintage_id'] for r in final})
        i=next(i for i,r in enumerate(self.tables['finance_monthly']) if r['scenario']=='ACTUAL' and r['accounting_month']=='2025-12-01' and r['amount']=='0.00')
        with self.assertRaisesRegex(ValueError,'publication'):self.validator(self.change('finance_monthly',i,{'published_at':'2025-12-31T12:00:00Z','export_available_at':'2025-12-31T12:00:00Z'})).check_monthly()

    def test_forecast_and_budget_recompute_from_known_information(self):
        with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):self.validator().check_planning()

    def test_future_postings_and_worker_corrections_cannot_change_earlier_plan(self):
        r=next(r for r in self.tables['finance_monthly'] if r['scenario']=='FORECAST' and r['amount'] and Decimal(r['amount'])>0)
        c=FinanceContext(self.tables,self.cfg,'test');account=c.cat[r['account_catalog_id']]['code'];target=__import__('datetime').date.fromisoformat(r['accounting_month'])
        future=[dict(p,debit_amount='999999.00',credit_amount='0.00') if p['known_from']>r['published_at'] else p for p in self.tables['financial_posting']]
        tables=dict(self.tables);tables['worker_assignment']=[dict(w,hourly_cost_rate='99999.000000') if w['export_available_at']>r['published_at'] else w for w in self.tables['worker_assignment']]
        with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
            original=plan_amount(c,self.tables['financial_posting'],r['cost_center_id'],account,target,r['published_at'],r['vintage_id'])
            altered=plan_amount(FinanceContext(tables,self.cfg,'test'),future,r['cost_center_id'],account,target,r['published_at'],r['vintage_id'])
        self.assertEqual(original,altered)

    def test_superseded_worker_assertions_do_not_resurrect_old_assignments(self):
        history=[{'worker_id':'w','known_from':'2023-01-01','known_to':'2023-02-01','export_available_at':'2023-01-02'},
                 {'worker_id':'w','known_from':'2023-02-01','known_to':None,'export_available_at':'2023-02-03'}]
        self.assertEqual(delivered_assignments(history,'2023-02-02'),history[:1]);self.assertEqual(delivered_assignments(history,'2023-02-04'),history[1:])

    def test_duplicate_delivery_is_idempotent_and_conflicting_duplicate_rejected(self):
        self.assertEqual(len(unique_events(self.tables['claim_event']+self.tables['claim_event'][:10])),len(self.tables['claim_event']))
        altered=dict(self.tables['claim_event'][0],cash_delta='999.00')
        with self.assertRaisesRegex(ValueError,'conflicting duplicate'):unique_events(self.tables['claim_event']+[altered])

    def test_denial_denominator_uses_original_insured_observed_claims(self):
        result=claim_history(self.tables,'2026-01-01T05:59:59Z','2026-01-10T23:59:59Z')
        self.assertGreater(result['self_pay_statement_accounts'],7000);self.assertLess(result['observed_initial_insured_claims'],result['original_accounts'])
        self.assertGreater(result['original_accounts']-self.report['metrics']['open_claims'],result['original_accounts']//2)
        self.assertEqual(Decimal(result['cash']),Decimal(self.report['metrics']['current_cash']));self.assertEqual(Decimal(result['billed_ar']),Decimal(self.report['metrics']['closing_claim_ar']))

    def test_header_does_not_publish_future_first_submission(self):
        for h in self.tables['claim']:
            if h['first_submitted_at']:self.assertLessEqual(h['first_submitted_at'],h['export_available_at'])
            self.assertLess(h['created_at'],'2026-01-01T06:00:00Z')

    def test_no_postcutoff_economic_events_are_invented(self):
        i=0
        with self.assertRaisesRegex(ValueError,'outside scope'):self.validator(self.change('claim_event',i,{'occurred_at':'2026-01-02T00:00:00Z'})).check_events()

    def test_variance_missing_and_zero_budget_semantics(self):
        self.assertIsNone(variance('100',None,'CREDIT','GROSS_REVENUE')['favorable']);self.assertIsNone(variance('100','0','DEBIT','LABOR_POOL')['percent'])
        self.assertEqual(variance('110','100','CREDIT','GROSS_REVENUE')['favorable'],'10.00');self.assertEqual(variance('110','100','DEBIT','LABOR_POOL')['favorable'],'-10.00')

    def test_review_has_sixty_complete_bound_stratified_traces(self):
        body,selection=render_financial(self.tables,self.cfg);decision=read(ROOT/'reviews/financial-history-review.json')
        self.assertEqual(selection['cases'],60);self.assertEqual(body.count('## Trace '),60);self.assertEqual(review_gate(selection,decision)['status'],'PASS')
        self.assertTrue({'refund','reversal','opening','draft','cross_month','pending_denial','appeal_recovery','patient_payment','final_writeoff'}<=set(selection['strata']))
        stale=dict(selection,sample_sha256='stale');self.assertEqual(review_gate(stale,decision)['status'],'PENDING_REVIEW')

    def test_review_is_order_invariant_and_contains_complete_journals(self):
        body,selection=render_financial(self.tables,self.cfg)
        reordered={name:list(reversed(rows)) for name,rows in self.tables.items()}
        other,other_selection=render_financial(reordered,self.cfg)
        self.assertEqual(body,other);self.assertEqual(selection,other_selection);self.assertGreater(body.count('Journal '),100)

    def test_validation_and_inspection_do_not_import_financial_generators(self):
        import ast
        for path in (ROOT/'src/healthcare_synthetic/financial_validation.py',ROOT/'src/healthcare_synthetic/financial_oracles.py',ROOT/'src/healthcare_synthetic/financial_room_validation.py',ROOT/'scripts/validate_financial_data.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node,ast.ImportFrom):self.assertFalse(any(name in (node.module or '') for name in ('financial_pipeline','financial_billing','financial_postings','financial_allocations','financial_planning')),str(path))

    def test_clean_rebuild_cached_resume_and_complete_hash_match(self):
        target=self.work/'clean-rebuild';first=run_financial(output_dir=target);second=run_financial(output_dir=target)
        self.assertEqual(first['business_sha256'],self.manifest['business_sha256']);self.assertEqual(second['business_sha256'],first['business_sha256'])
        self.assertEqual(first['executed'],list(GRAPH));self.assertEqual(second['executed'],[]);self.assertEqual(second['reused'],list(GRAPH))

    def test_real_process_crash_rolls_back_and_resumes(self):
        target=self.cache_copy('process-crash');connection=sqlite3.connect(target/'checkpoints.sqlite3')
        with connection:
            for stage in ('posting','allocation','planning','validation'):connection.execute('DELETE FROM stages WHERE name=?',(stage,))
        connection.close()
        result=subprocess.run([sys.executable,str(ROOT/'scripts/generate_financial_history.py'),'--output',str(target),'--crash-stage','posting'],cwd=ROOT,capture_output=True,text=True,timeout=1800)
        self.assertEqual(result.returncode,97,result.stderr);self.assertFalse((target/'candidate-ready.json').exists())
        connection=sqlite3.connect(target/'checkpoints.sqlite3');self.assertEqual({r[0] for r in connection.execute('SELECT name FROM stages')},{'billing','claims'});connection.close()
        resumed=run_financial(output_dir=target);self.assertEqual(resumed['status'],'FINANCIAL_HISTORY_PASSED');self.assertEqual(resumed['business_sha256'],self.manifest['business_sha256'])

    def test_changed_seed_invalidates_descendants_before_injected_failure(self):
        target=self.cache_copy('changed-seed');cfg=dict(self.cfg,seed=self.cfg['seed']+1);path=self.work/'changed-config.json';path.write_text(json.dumps(cfg))
        with self.assertRaisesRegex(RuntimeError,'injected'):run_financial(path,target,fail_stage='billing')
        self.assertFalse((target/'candidate-ready.json').exists());connection=sqlite3.connect(target/'checkpoints.sqlite3')
        self.assertEqual(connection.execute('SELECT COUNT(*) FROM stages').fetchone()[0],0);connection.close()

    def test_corrupt_checkpoint_cannot_publish_ready(self):
        target=self.cache_copy('corrupt-checkpoint');connection=sqlite3.connect(target/'checkpoints.sqlite3')
        with connection:connection.execute("UPDATE stages SET payload=payload||'corrupt' WHERE name='validation'")
        connection.close()
        with self.assertRaisesRegex(ValueError,'checkpoint corruption'):run_financial(output_dir=target)
        self.assertFalse((target/'candidate-ready.json').exists())

    def test_unsupported_configuration_is_rejected(self):
        path=self.work/'unsupported-config.json';path.write_text(json.dumps(dict(self.cfg,close_day=3)))
        with self.assertRaisesRegex(ValueError,'configuration changed'):run_financial(path,self.work/'unsupported')
