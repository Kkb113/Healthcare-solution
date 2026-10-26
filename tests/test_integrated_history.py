"""Independent grain, PIT, end-to-end regeneration and failure controls."""
import copy
import gc
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from decimal import Context,Decimal,ROUND_HALF_UP,localcontext
from datetime import datetime,timedelta,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.integrated_consumers import latest,claim_balances,selected_allocations,finance_series,variances,feature_snapshot,digest,build_index,connect,profile
from healthcare_synthetic.integrated_generation import generate,load_snapshot,read,schema,financial_config,dependencies,sha_file,STAGES
from healthcare_synthetic.integrated_exports import export,inspect
from healthcare_synthetic.integrated_validation import reconcile,point_in_time


def revision(number,known,**fields):
    return {'id':'a','revision_no':number,'known_from':known,'recorded_at':known,'export_available_at':known,
            'valid_from':'2023-01-01T00:00:00Z','valid_to':None,'known_to':None,**fields}


def monthly(scenario,amount='100.00',known='2023-01-01T00:00:00Z',**fields):
    return {'finance_record_id':scenario+known,'accounting_month':'2023-02-01','facility_id':'f','cost_center_id':'c',
            'account_catalog_id':'account','measure_code':'ACCOUNT_AMOUNT','unit_code':'USD','scenario':scenario,
            'amount':amount,'quantity':None,'published_at':known,'export_available_at':known,**fields}


class ConsumerContractTests(unittest.TestCase):
    def test_sparse_cell_wilson_intervals_have_explicit_denominators(self):
        from healthcare_synthetic.integrated_consumers import wilson_interval
        zero = wilson_interval(0,10); full = wilson_interval(10,10); half = wilson_interval(5,10)
        self.assertAlmostEqual(zero[0],0); self.assertAlmostEqual(zero[1],.2775327998628892)
        self.assertAlmostEqual(full[0],.7224672001371107); self.assertAlmostEqual(full[1],1)
        self.assertAlmostEqual(half[0],.236593090512564); self.assertAlmostEqual(half[1],.763406909487436)
        for a,b in ((1,0),(-1,10),(11,10),(1.0,10)):
            with self.assertRaises(ValueError):wilson_interval(a,b)

    def test_latest_revision_waits_for_delivery(self):
        a=revision(1,'2023-01-01T00:00:00Z');b=revision(2,'2023-02-01T00:00:00Z')
        self.assertEqual(latest([a,b],'id','2023-01-30T00:00:00Z')['a']['revision_no'],1)

    def test_latest_does_not_use_retrospective_known_to(self):
        a=revision(1,'2023-01-01T00:00:00Z',known_to='2023-01-02T00:00:00Z')
        self.assertIn('a',latest([a],'id','2023-01-30T00:00:00Z'))

    def test_expired_new_version_cannot_resurrect_old(self):
        a=revision(1,'2023-01-01T00:00:00Z');b=revision(2,'2023-01-02T00:00:00Z',valid_to='2023-01-15T00:00:00Z')
        self.assertEqual(latest([a,b],'id','2023-02-01T00:00:00Z','2023-02-01T00:00:00Z'),{})

    def test_unknown_source_revision_is_hidden(self):
        a=revision(1,'2023-02-01T00:00:00Z',export_available_at='2023-01-01T00:00:00Z')
        self.assertEqual(latest([a],'id','2023-01-15T00:00:00Z'),{})

    def claim_fixture(self):
        headers=[{'claim_id':'insured','created_at':'2023-01-01T06:00:00Z','export_available_at':'2023-01-02T00:00:00Z','coverage_version_id':'i','carry_in':False,'opening_ar':'0.00'},
                 {'claim_id':'statement','created_at':'2023-01-01T06:00:00Z','export_available_at':'2023-01-02T00:00:00Z','coverage_version_id':'s','carry_in':False,'opening_ar':'0.00'}]
        coverage={'i':{'payer_plan_id':'p'},'s':{'payer_plan_id':'self'}};payers={'p':{'payer_type':'COMMERCIAL'},'self':{'payer_type':'SELF_PAY'}}
        events=[]
        for cid in ('insured','statement'):
            events += [{'claim_event_id':cid+kind,'claim_id':cid,'event_type':kind,'attempt_no':1,'occurred_at':'2023-01-05T00:00:00Z','export_available_at':'2023-01-06T00:00:00Z','ar_delta':ar,'cash_delta':cash}
                       for kind,ar,cash in [('SUBMITTED','100.00','0.00'),('DENIED','0.00','0.00'),('PAYMENT','-60.00','60.00'),('REFUND','10.00','-10.00')]]
        return headers,events,coverage,payers

    def test_claims_exclude_selfpay_and_count_originals(self):
        h,e,c,p=self.claim_fixture();r=claim_balances(h,e,c,p)
        self.assertEqual(r['observed_initial_insured'],1);self.assertEqual(r['denied_initial_insured'],1)
        self.assertEqual(Decimal(r['ar_by_original']['insured']),50)

    def test_claim_duplicate_delivery_has_no_economic_effect(self):
        h,e,c,p=self.claim_fixture();self.assertEqual(claim_balances(h,e,c,p),claim_balances(h,e+e,c,p))

    def test_conflicting_claim_duplicate_fails(self):
        h,e,c,p=self.claim_fixture()
        with self.assertRaisesRegex(ValueError,'conflicting'):
            claim_balances(h,e+[{**e[0],'cash_delta':'1.00'}],c,p)

    def test_claim_future_delivery_is_unknown(self):
        h,e,c,p=self.claim_fixture();r=claim_balances(h,e,c,p,known='2023-01-05T12:00:00Z')
        self.assertEqual(r['observed_initial_insured'],0);self.assertIsNone(r['denial_rate'])

    def test_attempts_do_not_create_new_originals(self):
        h,e,c,p=self.claim_fixture();e.append({**e[1],'claim_event_id':'appeal','attempt_no':2})
        self.assertEqual(claim_balances(h,e,c,p)['denied_initial_insured'],1)

    def test_signed_refund_reduces_cash(self):
        h,e,c,p=self.claim_fixture();self.assertEqual(Decimal(claim_balances(h,e,c,p)['cash_by_month']['2023-01']),100)

    def test_allocation_runs_are_selected_per_source_posting(self):
        rows=[{'posting_id':'p','allocation_run_id':'v1','known_from':'2023-01-01','export_available_at':'2023-01-01','allocated_amount':'100.00'},
              {'posting_id':'p','allocation_run_id':'v2','known_from':'2023-02-01','export_available_at':'2023-02-01','allocated_amount':'90.00'}]
        self.assertEqual(selected_allocations(rows)[0]['allocated_amount'],'90.00')
        self.assertEqual(selected_allocations(rows,'2023-01-15')[0]['allocated_amount'],'100.00')

    def test_finance_scenarios_not_summed(self):
        rows=[monthly('ACTUAL'),monthly('BUDGET','110.00'),monthly('FORECAST','105.00')]
        self.assertEqual(len(finance_series(rows)),3);self.assertEqual(len(variances(rows)),2)

    def test_finance_new_vintage_replaces_only_its_series(self):
        rows=[monthly('ACTUAL'),monthly('ACTUAL','90.00','2023-02-01T00:00:00Z'),monthly('BUDGET','110.00')]
        self.assertEqual([r for r in finance_series(rows).values() if r['scenario']=='ACTUAL'][0]['amount'],'90.00')

    def test_zero_budget_is_not_missing_budget(self):
        rows=[monthly('ACTUAL'),monthly('BUDGET','0.00')];r=variances(rows)
        self.assertEqual({x['state'] for x in r},{'ZERO_PLAN','NO_PLAN'});self.assertTrue(all(x['percent'] is None for x in r))

    def test_statistical_units_have_separate_series(self):
        rows=[monthly('ACTUAL'),monthly('ACTUAL',None,account_catalog_id=None,measure_code='FTE',unit_code='FTE',quantity='2.000000')]
        self.assertEqual(len(finance_series(rows)),2)

    def test_future_forecast_vintage_is_hidden(self):
        self.assertEqual(finance_series([monthly('FORECAST',known='2023-02-01T00:00:00Z')],'2023-01-31T00:00:00Z'),{})

    def feature_fixture(self,discharge='2023-01-02T00:00:00Z',disposition='HOME'):
        e=revision(1,discharge,encounter_id='e',encounter_version_id='ev',patient_version_id='pv',encounter_class='IPD',
                   admission_source='DIRECT',arrival_at='2023-01-01T06:00:00Z',discharged_at=discharge,disposition=disposition,planned=False)
        return {'encounter':[e],'patient':[{'patient_version_id':'pv','patient_id':'p'}],'clinical_condition':[],'clinical_event':[]}

    def test_readmission_incomplete_followup_remains_unknown(self):
        t=self.feature_fixture();r=feature_snapshot(t,'e','2023-01-15T00:00:00Z','2023-01-15T00:00:00Z')
        self.assertEqual(r['readmission_label'],'UNKNOWN')

    def test_readmission_negative_requires_complete_followup(self):
        t=self.feature_fixture();r=feature_snapshot(t,'e','2023-02-15T00:00:00Z','2023-02-15T00:00:00Z')
        self.assertEqual(r['readmission_label'],'NEGATIVE')

    def test_negative_label_waits_for_source_completeness_after_day_thirty(self):
        t=self.feature_fixture();end='2023-02-01T00:00:00Z'
        self.assertEqual(feature_snapshot(t,'e',end,end)['readmission_label'],'UNKNOWN')
        self.assertEqual(feature_snapshot(t,'e','2023-02-01T02:00:00Z',end)['readmission_label'],'NEGATIVE')

    def test_readmission_positive_requires_observed_unplanned_return(self):
        t=self.feature_fixture();t['encounter'].append({**t['encounter'][0],'id':'back','encounter_id':'back','encounter_version_id':'backv',
            'arrival_at':'2023-01-20T00:00:00Z','discharged_at':None,'known_from':'2023-01-20T00:00:00Z','export_available_at':'2023-01-20T00:00:00Z'})
        self.assertEqual(feature_snapshot(t,'e','2023-01-25T00:00:00Z','2023-01-25T00:00:00Z')['readmission_label'],'POSITIVE')
        t['encounter'][1]['planned']=True
        self.assertEqual(feature_snapshot(t,'e','2023-01-25T00:00:00Z','2023-01-25T00:00:00Z')['readmission_label'],'UNKNOWN')

    def test_readmission_dead_index_is_not_a_negative(self):
        t=self.feature_fixture(disposition='DEATH')
        self.assertEqual(feature_snapshot(t,'e','2023-02-15T00:00:00Z','2023-02-15T00:00:00Z')['readmission_label'],'UNKNOWN')

    def test_readmission_end_window_is_censored(self):
        t=self.feature_fixture(discharge='2025-12-20T00:00:00Z')
        self.assertEqual(feature_snapshot(t,'e','2026-01-10T00:00:00Z','2026-01-01T05:59:59Z')['readmission_label'],'UNKNOWN')

    def test_retracted_performed_event_is_not_retained_as_completed(self):
        t=self.feature_fixture();first=revision(1,'2023-01-02T00:00:00Z',clinical_event_id='care',encounter_version_id='ev',
            event_type='PROCEDURE',status='COMPLETED',occurred_at='2023-01-02T00:00:00Z',period_end_at='2023-01-02T01:00:00Z')
        corrected={**first,'revision_no':2,'known_from':'2023-01-03T00:00:00Z','export_available_at':'2023-01-03T00:00:00Z','status':'NOT_DONE'}
        t['clinical_event']=[first,corrected]
        self.assertEqual(feature_snapshot(t,'e','2023-01-04T00:00:00Z','2023-01-04T00:00:00Z')['performed_events'],[])

    def test_grain_fanout_negative_control(self):
        charges=[Decimal('10.00'),Decimal('20.00')];diagnoses=range(2);services=range(3);intervals=range(2)
        unsafe=sum(v for v in charges for _ in diagnoses for _ in services for _ in intervals)
        self.assertEqual(unsafe,sum(charges)*12);self.assertEqual(sum(charges),30)

    def test_frozen_denial_target_is_not_relaxed(self):
        target=next(t for t in read(ROOT/'contracts/phase0/realism-targets.json')['targets'] if t['id']=='DENIAL')
        self.assertEqual((target['lower'],target['upper']),(.08,.12));self.assertEqual(financial_config(20261023)['denial_basis_points'],900)

    def test_budget_reassignment_conserves_total(self):
        s=schema();self.assertEqual(len(s['tables']),25);self.assertEqual(sum(t['planned_rows'] for t in s['tables']),1995215)
        cfg=read(ROOT/'config/integrated-history-generation.json');self.assertEqual(cfg['planned_rows']+cfg['reserve_rows'],2000000)

    def test_seed_search_is_forbidden(self):
        with self.assertRaisesRegex(ValueError,'preregistered'):
            generate(999,ROOT/'output/unused-integrated-seed')

    def test_unknown_failure_stage_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'unknown'):
            generate(20261023,ROOT/'output/unused-integrated-seed',fail_stage='invented')

    def test_foreign_generation_profile_preserves_existing_ready_marker(self):
        with tempfile.TemporaryDirectory(prefix='foreign-integrated-profile-',dir=ROOT/'output') as temp:
            path=Path(temp);(path/'manifest.json').write_text('{"profile":"FOREIGN"}',encoding='utf-8')
            ready=path/'candidate-ready.json';ready.write_bytes(b'preserve')
            with self.assertRaisesRegex(ValueError,'wrong integrated candidate profile'):generate(20261023,path)
            self.assertEqual(ready.read_bytes(),b'preserve')

    def master_fixture(self):
        kinds=('COMMERCIAL','MEDICARE','MEDICAID','SELF_PAY')
        return {'patient':[{'patient_version_id':'senior','patient_id':'p1','birth_date':'1950-01-01'},
                           {'patient_version_id':'adult','patient_id':'p2','birth_date':'1990-01-01'}],
                'payer_plan':[{'payer_plan_id':k,'plan_code':k+'-1','payer_type':k} for k in kinds],
                'patient_coverage':[{'coverage_version_id':'c'+str(i),'coverage_id':'c'+str(i),'patient_version_id':p,
                    'payer_plan_id':'COMMERCIAL','valid_from':'2022-12-15T06:00:00Z','valid_to':None,'known_from':'2022-12-15T06:00:00Z',
                    'coverage_status':'ACTIVE','synthetic_member_id':'old','generation_run_id':'old'} for i,p in enumerate(('senior','adult'))],
                'worker_assignment':[{'worker_id':f'worker-{i}','birth_date':'1970-06-15','generation_run_id':'old'} for i in range(200)]}

    def test_master_migration_preserves_identity_intervals_and_birth_years(self):
        from healthcare_synthetic.integrated_master_context import amend
        source=self.master_fixture();before=copy.deepcopy(source);changed=amend(source)
        self.assertEqual(source,before);self.assertEqual(len(changed['patient_coverage']),2)
        for a,b in zip(source['patient_coverage'],changed['patient_coverage']):
            for field in ('coverage_id','coverage_version_id','valid_from','valid_to','known_from'):self.assertEqual(a[field],b[field])
        self.assertTrue(all(w['birth_date'].startswith('1970-') for w in changed['worker_assignment']))
        self.assertGreater(len({w['birth_date'] for w in changed['worker_assignment']}),100)

    def test_master_migration_is_prospective_and_does_not_invent_under65_medicare(self):
        from healthcare_synthetic.integrated_master_context import amend
        a=self.master_fixture();b=copy.deepcopy(a);b['encounter']=[{'future_admissions':1000000}];b['claim_event']=[{'future_paid':'999999.00'}]
        first=amend(a);second=amend(b)
        self.assertEqual(first['patient_coverage'],second['patient_coverage'])
        self.assertNotEqual(first['patient_coverage'][1]['payer_plan_id'],'MEDICARE')

    def test_worker_birthday_is_consistent_across_assignment_versions(self):
        from healthcare_synthetic.integrated_master_context import amend
        source=self.master_fixture();source['worker_assignment']=[source['worker_assignment'][0]]*3
        amended=amend(source);self.assertEqual(len({w['birth_date'] for w in amended['worker_assignment']}),1)

    def test_patient_slot_preserves_unconstrained_proposal(self):
        from healthcare_synthetic.trajectory_scheduling import patient_slot
        at=datetime(2025,12,20,14,tzinfo=timezone.utc)
        self.assertEqual(patient_slot(at,timedelta(hours=2),[],datetime(2023,1,1,tzinfo=timezone.utc),datetime(2026,1,1,tzinfo=timezone.utc)),at)

    def test_patient_slot_preserves_legacy_forward_resolution(self):
        from healthcare_synthetic.trajectory_scheduling import patient_slot
        at=datetime(2025,12,20,14,tzinfo=timezone.utc)
        self.assertEqual(patient_slot(at,timedelta(hours=2),[(at,at+timedelta(days=2))],datetime(2023,1,1,tzinfo=timezone.utc),datetime(2026,1,1,tzinfo=timezone.utc)),at+timedelta(days=2))

    def test_patient_slot_boundary_trap_resolves_without_lost_visit(self):
        from healthcare_synthetic.trajectory_scheduling import patient_slot
        from zoneinfo import ZoneInfo
        at=datetime(2025,12,31,14,tzinfo=timezone.utc);start=datetime(2025,12,30,tzinfo=timezone.utc)
        result=patient_slot(at,timedelta(hours=2),[(start,datetime(2026,1,5,tzinfo=timezone.utc))],datetime(2023,1,1,tzinfo=timezone.utc),datetime(2026,1,1,6,tzinfo=timezone.utc),allow_backwards=True,fallback_weekday_zone=ZoneInfo('America/Chicago'))
        self.assertEqual(result,datetime(2025,12,29,14,tzinfo=timezone.utc))

    def test_linked_urgent_admission_cannot_move_backwards(self):
        from healthcare_synthetic.trajectory_scheduling import patient_slot
        at=datetime(2025,12,31,14,tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError,'no free'):
            patient_slot(at,timedelta(hours=2),[(at-timedelta(days=2),at+timedelta(days=4))],datetime(2023,1,1,tzinfo=timezone.utc),datetime(2026,1,1,6,tzinfo=timezone.utc))

    def test_patient_slot_impossible_calendar_fails_instead_of_dropping_fact(self):
        from healthcare_synthetic.trajectory_scheduling import patient_slot
        at=datetime(2025,12,31,14,tzinfo=timezone.utc);lower=at-timedelta(days=1);end=at+timedelta(days=1)
        with self.assertRaisesRegex(ValueError,'no free'):
            patient_slot(at,timedelta(hours=2),[(lower,end+timedelta(days=4))],lower,end,allow_backwards=True)

    def test_patient_slot_half_open_boundaries_do_not_overlap(self):
        from healthcare_synthetic.trajectory_scheduling import patient_slot
        at=datetime(2025,12,20,14,tzinfo=timezone.utc)
        self.assertEqual(patient_slot(at,timedelta(hours=2),[(at-timedelta(hours=2),at)],datetime(2023,1,1,tzinfo=timezone.utc),datetime(2026,1,1,tzinfo=timezone.utc)),at)

    def bed_period_fixture(self):
        events=[]
        for i,(kind,at,delivered,ev) in enumerate([
            ('OPENING','2023-01-01T06:00:00Z','2023-01-01T06:01:00Z',None),
            ('OCCUPY','2023-01-30T06:00:00Z','2023-01-30T06:01:00Z','ev1'),
            ('VACATE','2023-02-05T23:45:00Z','2023-02-06T05:45:00Z','ev1'),
            ('OCCUPY','2023-02-05T23:50:00Z','2023-02-05T23:51:00Z','ev2')]):
            events.append({'bed_event_id':str(i),'bed_location_id':'bed','encounter_version_id':ev,'corrects_bed_event_id':None,
                'event_type':kind,'effective_at':at,'delivery_at':delivered,'recorded_at':at,'sequence_no':i+1,
                'occupancy_state':'OCCUPIED' if kind=='OCCUPY' else 'EMPTY'})
        enc=[{'encounter_version_id':'ev'+str(i),'encounter_id':'e'+str(i),'revision_no':1,'export_available_at':'2023-01-01T06:00:00Z',
              'encounter_class':'IPD','carry_in':False,'admitted_at':at,'location_id':'bed'} for i,at in ((1,'2023-01-30T06:00:00Z'),(2,'2023-02-05T23:50:00Z'))]
        return {'encounter':enc,'location':[{'location_id':'bed','cost_center_id':'cc'}],'bed_event':events,'staff_shift':[]}

    def test_closed_month_ignores_unrelated_later_month_delivery_gap(self):
        from datetime import date
        from healthcare_synthetic.financial_planning import statistics
        from healthcare_synthetic.financial_oracles import statistical_values
        from healthcare_synthetic.operational_validation import bed_intervals
        t=self.bed_period_fixture();known='2023-02-06T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'overlapping'):bed_intervals(t['bed_event'],{r['encounter_version_id']:r for r in t['encounter']},known)
        self.assertEqual(statistics(t,date(2023,1,1),known)['cc']['PATIENT_DAYS'],Decimal(2))
        self.assertEqual(statistical_values(t,date(2023,1,1),known)['cc']['PATIENT_DAYS'],Decimal(2))

    def test_true_target_month_bed_gap_still_blocks_statistics(self):
        from datetime import date
        from healthcare_synthetic.financial_planning import statistics
        from healthcare_synthetic.financial_oracles import statistical_values
        t=self.bed_period_fixture();t['bed_event'][2]['effective_at']='2023-01-31T23:45:00Z';t['bed_event'][3]['effective_at']='2023-01-31T23:50:00Z'
        for implementation in (statistics,statistical_values):
            with self.assertRaisesRegex(ValueError,'overlapping'):implementation(t,date(2023,1,1),'2023-02-06T00:00:00Z')

    def test_schema_evolution_requires_approved_scalar_contract(self):
        from healthcare_synthetic.sources import serialize,parse
        v1={'key':'string','amount':'decimal'};v2={**v1,'unit':'string'}
        old=serialize('AXIOM','fixture','v1','2024-01-01T00:00:00Z',[{'key':'a','amount':'10.00'}],v1)
        with self.assertRaisesRegex(ValueError,'F_SCHEMA'):parse(old,v2)
        new=serialize('AXIOM','fixture','v2','2024-01-01T00:00:00Z',[{'key':'a','amount':'10.00','unit':'USD'}],v2)
        self.assertEqual(parse(new,v2)[0]['unit'],'USD')
        with self.assertRaisesRegex(ValueError,'F_SCHEMA'):parse(new,v1)

    def test_changed_upstream_assumption_invalidates_descendants(self):
        from healthcare_synthetic.engine import run
        with tempfile.TemporaryDirectory(prefix='integrated-connected-fixture-',dir=ROOT/'output') as temp:
            root=Path(temp);cfg=read(ROOT/'config/phase1-development.json');path=root/'fixture-config.json'
            path.write_text(json.dumps(cfg),encoding='utf-8');output=root/'candidate'
            first=run(ROOT,path,output);again=run(ROOT,path,output)
            self.assertEqual(first['status'],'FIXTURES_PASSED');self.assertEqual(first['business_sha256'],again['business_sha256'])
            cfg['stages']['billing']['cost_pool']='105.00';path.write_text(json.dumps(cfg),encoding='utf-8')
            stale_review=run(ROOT,path,output);self.assertEqual(stale_review['status'],'BLOCKED')
            cfg['expectations']['pool']='105.00';path.write_text(json.dumps(cfg),encoding='utf-8')
            changed=run(ROOT,path,output);self.assertEqual(changed['status'],'FIXTURES_PASSED')
            self.assertNotEqual(first['business_sha256'],changed['business_sha256'])
            self.assertIn('billing',stale_review['executed']);self.assertIn('serialization',stale_review['executed']);self.assertIn('validation',changed['executed'])
            self.assertIn('identities',changed['reused']);self.assertIn('clinical',changed['reused'])


class IntegratedHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate=ROOT/'output/integrated-history';cls.sources=ROOT/'output/integrated-source-delivery'
        cls.manifest=read(cls.candidate/'manifest.json')
        cls.temp=tempfile.TemporaryDirectory(prefix='integrated-contract-tests-',dir=ROOT/'output');cls.work=Path(cls.temp.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.context=localcontext(Context(prec=38,rounding=ROUND_HALF_UP));self.context.__enter__()
        if self._testMethodName in ('test_cent_mutation_at_individual_pool_is_detected','test_wrong_actual_at_one_series_is_detected',
                                    'test_full_history_point_in_time_and_unknown_labels','test_full_history_six_consumers_and_fanout'):
            self.tables,_=load_snapshot(self.candidate)
        elif self._testMethodName=='test_full_history_exact_parent_preservation':
            self.tables={}
            for table in ('patient_coverage','worker_assignment','catalog_item'):
                with (self.candidate/self.manifest['canonical_files'][table]['file']).open() as stream:self.tables[table]=list(map(json.loads,stream))

    def tearDown(self):
        if hasattr(self,'tables'):
            self.tables.clear();del self.tables;gc.collect()
        self.context.__exit__(None,None,None)

    def test_full_history_six_consumers_and_fanout(self):
        result=reconcile(self.tables);self.assertEqual(result['status'],'PASS');self.assertEqual(result['staffing_business_months'],36)
        self.assertEqual(result['staffing_opening_context_months'],['2022-12'])
        self.assertEqual(result['bed_seconds_grains'],72);self.assertEqual(result['unexplained_differences'],0)

    def test_full_history_point_in_time_and_unknown_labels(self):
        result=point_in_time(self.tables);self.assertEqual(result['status'],'PASS');self.assertGreaterEqual(len(result['checks']),10)

    def test_full_history_exact_parent_preservation(self):
        # Version 1.1 regenerates every care, capacity, workforce and stock domain
        # from the accepted master snapshot; master facts themselves are preserved.
        parent=read(ROOT/'output/master-foundation/manifest.json');amended=('catalog_item','patient_coverage','worker_assignment','clinical_condition')
        for name,meta in parent['canonical_files'].items():
            if name not in amended:self.assertEqual(meta['sha256'],self.manifest['canonical_files'][name]['sha256'],name)
        resource=read(ROOT/'output/resource-foundation/manifest.json')
        for name in ('encounter','bed_event','appointment','staff_shift'):
            self.assertNotEqual(resource['canonical_files'][name]['sha256'],self.manifest['canonical_files'][name]['sha256'],name)
        with (ROOT/'output/master-foundation'/parent['canonical_files']['clinical_condition']['file']).open() as stream:
            opening={r['condition_version_id']:r for r in map(json.loads,stream)}
        with (self.candidate/self.manifest['canonical_files']['clinical_condition']['file']).open() as stream:
            current={r['condition_version_id']:r for r in map(json.loads,stream) if r['encounter_version_id'] is None and r['condition_version_id'] in opening}
        self.assertEqual(current,opening)
        for table,pk,allowed in [('worker_assignment','worker_assignment_id',{'birth_date','generation_run_id'}),
                                  ('patient_coverage','coverage_version_id',{'payer_plan_id','coverage_status','synthetic_member_id','generation_run_id'})]:
            indexed={r[pk]:r for r in self.tables[table]}
            with (ROOT/'output/master-foundation'/parent['canonical_files'][table]['file']).open() as stream:
                for original in map(json.loads,stream):
                    self.assertEqual({k:v for k,v in indexed[original[pk]].items() if k not in allowed},{k:v for k,v in original.items() if k not in allowed})
        catalog={r['catalog_item_id']:r for r in self.tables['catalog_item']};old_keys=set()
        with (ROOT/'output/master-foundation'/parent['canonical_files']['catalog_item']['file']).open() as stream:
            for original in map(json.loads,stream):
                old_keys.add(original['catalog_item_id']);self.assertEqual(catalog[original['catalog_item_id']],original)
        self.assertEqual(len(catalog)-len(old_keys),5)

    def test_old_and_new_master_baselines_cannot_be_incrementally_mixed(self):
        from healthcare_synthetic.source_reader import DeliveryReplay
        old_root=ROOT/'output/source-delivery';old=read(old_root/'manifest.json');new=read(self.sources/'manifest.json')
        previous=next(f for f in old['files'] if f['table']=='worker_assignment' and f['role']=='PRIMARY' and f['expected_rows'])
        current=next(f for f in new['files'] if f['table']=='worker_assignment' and f['role']=='PRIMARY' and f['available_at']==previous['available_at'])
        replay=DeliveryReplay(':memory:')
        try:
            replay.ingest(old_root,previous,read(old_root/'source-dictionary.json')['worker_assignment'])
            with self.assertRaises(ValueError):replay.ingest(self.sources,current,read(self.sources/'source-dictionary.json')['worker_assignment'])
        finally:replay.close()

    def test_full_history_all_configured_seed_experiments_pass(self):
        expected=[20261023,20261024,20261025];hashes=[]
        for seed in expected:
            path=ROOT/('output/integrated-validation' if seed==20261023 else f'output/integrated-comparison-{seed}/validation')
            report=read(path/'inspection.json');self.assertEqual(report['status'],'PASS',seed);self.assertEqual(report['seed'],seed)
            self.assertEqual(report['partitions'],324);self.assertTrue(all(r['passed'] for r in report['realism_checks']))
            self.assertLessEqual(report['rows']+22,2000000);hashes.append(report['business_sha256'])
        self.assertEqual(len(set(hashes)),3)

    def test_boundary_fix_preserves_unaffected_candidate_goldens(self):
        # Version 1.1.0 goldens; version 1.0.2 was 61124cc7... (primary) and 418bca40... (20261024).
        self.assertEqual(self.manifest['business_sha256'],'12859a1807c54f2a1900b2ae430b11e88befc33d483e4e96ce0452d0e682eb1b')
        self.assertEqual(read(ROOT/'output/integrated-comparison-20261024/manifest.json')['business_sha256'],'eb914767717b452c168d415b95261bbe582793f86d049df30641a933aa967d3a')

    def test_registered_boundary_seed_really_exercises_slot_fallback(self):
        from unittest.mock import patch
        from collections import Counter
        from healthcare_synthetic.operational_demand import DemandGenerator
        from healthcare_synthetic.integrated_master_context import amend
        from healthcare_synthetic.trajectory_scheduling import patient_slot
        master,_=load_snapshot(ROOT/'output/master-foundation');master=amend(master)
        cfg=read(ROOT/'config/clinical-history-generation.json');cfg['seed']=20261025
        ops=read(ROOT/'config/operational-flow-generation.json');ops['seed']=20261025
        generator=DemandGenerator(master,cfg,read(ROOT/'contracts/clinical-history-policy.json'),'boundary-regression',ops);moved=[]
        def observe(desired,*args,**kwargs):
            result=patient_slot(desired,*args,**kwargs)
            if result<desired:moved.append(True)
            return result
        with patch('healthcare_synthetic.clinical_generation.patient_slot',new=observe):journeys=generator.journeys()
        visits=latest(journeys['encounter'],'encounter_id');counts=Counter(r['encounter_class'] for r in visits.values())
        # Version 1.1 weekday spreading and stay timing remove the end-of-window
        # collision this seed hit in 1.0, so the fallback count may be zero. The
        # boundary-trap unit tests above still exercise the fallback directly;
        # this seed must keep every proposal without seed replacement.
        self.assertEqual(dict(counts),{'IPD':12000,'ED':27000,'OPD':19000})
        result={'registered_seed':20261025,'unpublished_backward_placements':len(moved),'all_proposals_preserved':True,
                'fallback_unit_tests':['test_patient_slot_boundary_trap_resolves_without_lost_visit'],
                'stable_visit_counts_including_opening_context':dict(counts),'no_seed_replacement':True}
        (ROOT/'output/integrated-validation/boundary-control.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')

    def test_full_history_fresh_domain_catalog_passes(self):
        report=read(ROOT/'output/integrated-validation/domain-controls.json')
        self.assertEqual(report['defects'],[]);self.assertEqual(set(report['domains']),{'master','clinical','operations','workforce','stock','finance'})

    def test_full_history_denial_calibration_passes_original_target(self):
        report=read(ROOT/'output/integrated-validation/realism-profiles.json')
        check=next(c for c in report['checks'] if c['id']=='DENIAL');self.assertTrue(check['passed']);self.assertGreaterEqual(check['value'],.08)

    def test_cent_mutation_at_individual_pool_is_detected(self):
        from healthcare_synthetic.financial_validation import FinancialValidator
        rows=list(self.tables['cost_allocation']);r=rows[0];rows[0]={**r,'allocated_amount':format(Decimal(r['allocated_amount'])+Decimal('.01'),'.2f')}
        with self.assertRaises(ValueError):FinancialValidator({**self.tables,'cost_allocation':rows},financial_config(20261023),schema()).check_allocations()

    def test_wrong_actual_at_one_series_is_detected(self):
        from healthcare_synthetic.financial_validation import FinancialValidator
        rows=list(self.tables['finance_monthly']);i=next(i for i,r in enumerate(rows) if r['scenario']=='ACTUAL' and r['amount'] is not None)
        rows[i]={**rows[i],'amount':format(Decimal(rows[i]['amount'])+Decimal('.01'),'.2f')}
        with self.assertRaisesRegex(ValueError,'actual differs'):FinancialValidator({**self.tables,'finance_monthly':rows},financial_config(20261023),schema()).check_monthly()

    def test_full_native_inspection_reports_and_faults(self):
        result=inspect(self.candidate,self.sources,self.work/'source-replay.sqlite3')
        self.assertEqual(result['status'],'PASS');self.assertEqual(result['roundtrip_rows'],self.manifest['business_rows'])
        self.assertEqual(result['source_files'],result['duplicate_deliveries_checked']);self.assertEqual(result['faults']['status'],'PASS')
        (ROOT/'output/integrated-validation/source-inspection.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')

    def test_real_candidate_process_crash_and_resume(self):
        output=self.work/'crash-candidate'
        script=ROOT/'scripts/generate_integrated_history.py'
        p=subprocess.run([sys.executable,str(script),'--output',str(output),'--crash-stage','claims'],capture_output=True,text=True)
        self.assertEqual(p.returncode,97,p.stdout+p.stderr)
        db=sqlite3.connect(output/'checkpoints.sqlite3')
        try:self.assertEqual({r[0] for r in db.execute('SELECT name FROM stages')},{'resources','billing'})
        finally:db.close()
        result=generate(20261023,output)
        self.assertEqual(result['business_sha256'],self.manifest['business_sha256']);self.assertIn('billing',result['reused'])
        # A genuine subset rebuild invalidates dependent fingerprints. Untouched
        # resource/billing/claims remain cached; all later facts reproduce exactly.
        db=sqlite3.connect(output/'checkpoints.sqlite3')
        with db:db.execute("DELETE FROM stages WHERE name IN ('posting','allocation','planning')")
        db.close();subset=generate(20261023,output)
        self.assertEqual(subset['business_sha256'],result['business_sha256']);self.assertEqual(subset['executed'],['posting','allocation','planning'])

    def test_failed_export_recovery_and_complete_resume(self):
        output=self.work/'recovered-export'
        with self.assertRaisesRegex(ValueError,'injected'):
            export(self.candidate,output,fail_table='claim_event')
        self.assertFalse((output/'candidate-ready.json').exists())
        self.assertFalse((output/'checkpoints/claim-event.json').exists())
        result=export(self.candidate,output)
        self.assertEqual(len(result['files']),len(read(self.sources/'manifest.json')['files']))
        expected={f['path']:f['sha256'] for f in read(self.sources/'manifest.json')['files']}
        self.assertEqual({f['path']:f['sha256'] for f in result['files']},expected)

    def test_foreign_export_profile_preserves_existing_ready_marker(self):
        output=self.work/'foreign-export';output.mkdir();(output/'manifest.json').write_text('{"profile":"FOREIGN"}',encoding='utf-8')
        ready=output/'candidate-ready.json';ready.write_bytes(b'preserve')
        with self.assertRaisesRegex(ValueError,'foreign export profile'):export(self.candidate,output)
        self.assertEqual(ready.read_bytes(),b'preserve')

    def test_current_profile_scalar_checks_are_not_a_vacuous_sample(self):
        r=read(ROOT/'output/integrated-validation/inspection.json')
        self.assertEqual(r['index']['canonical_rows'],self.manifest['business_rows']);self.assertEqual(r['index']['tables'],25)
        self.assertGreater(r['index']['physical_foreign_keys_checked'],50)
        p=read(ROOT/'output/integrated-validation/realism-profiles.json');self.assertTrue(p['joint_profiles'])
        from collections import Counter
        totals=Counter()
        for cell in p['joint_profiles']:
            total=cell['parent_month_facility_class_n'];lo,hi=cell['wilson_95']
            self.assertGreater(total,0);self.assertTrue(0<=lo<=cell['n']/total<=hi<=1)
            totals[cell['month'],cell['facility'],cell['class']]+=cell['n']
        for cell in p['joint_profiles']:
            self.assertEqual(cell['parent_month_facility_class_n'],totals[cell['month'],cell['facility'],cell['class']])

