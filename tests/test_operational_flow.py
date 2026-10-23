"""Operational end-to-end acceptance, independent oracle mutations and saturation fixtures."""
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
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from healthcare_synthetic.clinical_pipeline import load_master,read
from healthcare_synthetic.operational_pipeline import GRAPH,run_operations
from healthcare_synthetic.operational_generation import FlowSimulator
from healthcare_synthetic.operational_demand import DemandGenerator
from healthcare_synthetic.operational_validation import OperationalValidator,bed_intervals,current_beds,resolve_events,sha,seconds,START,CUTOFF
from healthcare_synthetic.operational_review import render_operations,review_gate
from healthcare_synthetic.operational_queries import availability
from healthcare_synthetic.core import instant
from healthcare_synthetic.clinical_validation import ClinicalValidator
from validate_operational_data import inspect_operations


class OperationalFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=Path(os.environ.get('HEALTHCARE_OPERATIONAL_TEST_CANDIDATE',ROOT/'output/operational-flow'))
        cls.cfg=read(ROOT/'config/operational-flow-generation.json');cls.manifest=read(cls.base/'manifest.json')
        cls.tables={}
        for t,meta in cls.manifest['canonical_files'].items():
            with (cls.base/meta['file']).open(encoding='utf-8') as f:cls.tables[t]=[json.loads(line) for line in f]
        cls.ccfg=read(ROOT/'config/clinical-history-generation.json');cls.master,cls.schema,_=load_master(cls.ccfg)
        cls.checked=OperationalValidator(cls.tables,cls.schema,cls.cfg,cls.manifest['simulation']).run()
        cls.temp=tempfile.TemporaryDirectory(prefix='operational-tests-',dir=ROOT/'output');cls.work=Path(cls.temp.name)
        cls.enc={r['encounter_version_id']:r for r in cls.tables['encounter']}

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def validator(self,tables=None,simulation=None):return OperationalValidator(tables or self.tables,self.schema,self.cfg,simulation)

    def test_full_candidate_and_all_operational_checks(self):
        self.assertEqual(self.checked['status'],'PASS',self.checked['defects']);self.assertEqual(len(self.checked['checks']),7)
        self.assertEqual(len(self.tables),16);self.assertLess(self.manifest['business_rows'],1958210)
        self.assertEqual(self.manifest['release_business_tables'],25);self.assertFalse(self.manifest['full_dataset_accepted'])

    def test_occupied_seconds_match_two_independent_oracles(self):
        intervals=bed_intervals(self.tables['bed_event'],self.enc)
        self.assertEqual(sha(intervals),self.manifest['simulation']['simulated_interval_sha256'])
        self.assertEqual(sum(seconds(a,b) for _,_,a,b in intervals),self.checked['metrics']['occupied_seconds'])
        bad={**self.manifest['simulation'],'simulated_occupied_seconds':self.checked['metrics']['occupied_seconds']+1}
        with self.assertRaisesRegex(ValueError,'simulator/independent'):self.validator(simulation=bad).check_state()

    def test_opening_cutoff_and_every_census_boundary_reconcile(self):
        m=self.checked['metrics'];self.assertEqual(m['opening_census'],57);self.assertGreater(m['closing_census'],0)
        self.assertGreater(m['census_boundaries_checked'],20000);self.assertEqual(m['occupied_seconds'],m['interval_seconds'])

    def test_capacity_maintenance_turnaround_and_waits(self):
        m=self.checked['metrics'];self.assertEqual(m['lost_staffed_bed_days'],'962');self.assertEqual(m['unexplained_unplaced_completed'],0)
        self.assertGreater(m['delayed_placements'],100);self.assertEqual(m['cancelled_reservations'],100)
        self.assertTrue(60<=float(m['mean_turnaround_minutes'])<=90)

    def test_unmet_capacity_transfers_retain_cause_and_observed_scope(self):
        notes=[r for r in self.tables['clinical_event'] if r['source_record_id'].endswith('/placement-disposition') and 'external transfer at' in r['text_value']]
        self.assertGreater(len(notes),0)
        placed={eid for _,eid,_,_ in bed_intervals(self.tables['bed_event'],self.enc)}
        for note in notes:
            e=self.enc[note['encounter_version_id']]
            self.assertEqual(e['disposition'],'TRANSFER');self.assertNotIn(e['encounter_id'],placed)
            self.assertEqual(seconds(e['admitted_at'],e['discharged_at']),86400)
            self.assertIn('Cause: ',note['text_value']);self.assertIn('outside the modeled network',note['text_value'])
        t=dict(self.tables);t['clinical_event']=[r for r in self.tables['clinical_event'] if r['clinical_event_version_id']!=notes[0]['clinical_event_version_id']]
        with self.assertRaisesRegex(ValueError,'unexplained completed inpatient'):self.validator(t).check_queues()

    def test_observed_boarding_death_never_creates_a_bed_interval(self):
        notes=[r for r in self.tables['clinical_event'] if r['source_record_id'].endswith('/placement-disposition') and 'observed death at' in r['text_value']]
        self.assertEqual(len(notes),self.checked['metrics']['boarding_deaths'])
        placed={eid for _,eid,_,_ in bed_intervals(self.tables['bed_event'],self.enc)}
        for note in notes:
            e=self.enc[note['encounter_version_id']];self.assertEqual(e['disposition'],'DEATH');self.assertNotIn(e['encounter_id'],placed)
            self.assertTrue(0<seconds(e['admitted_at'],e['discharged_at'])<=86400)
            self.assertIn('Care continued in monitored boarding',note['text_value'])

    def test_current_availability_distinguishes_private_rooms_staffing_and_holds(self):
        bed=next(r for r in self.tables['location'] if r['location_type']=='BED' and r['service_line']=='MEDICINE')
        peer=next(r for r in self.tables['location'] if r['location_type']=='BED' and r['parent_location_id']==bed['parent_location_id'] and r['location_id']!=bed['location_id'])
        a=next(r for r in self.tables['bed_event'] if r['bed_location_id']==bed['location_id'] and r['event_type']=='OPENING')
        b=next(r for r in self.tables['bed_event'] if r['bed_location_id']==peer['location_id'] and r['event_type']=='OPENING')
        events=[{**a,'occupancy_state':'OCCUPIED','reason':'PRIVATE_ISOLATION_PLACEMENT','service_state':'IN_SERVICE','staffing_enabled':True,'reserved':False},
                {**b,'occupancy_state':'EMPTY','reason':'READY','service_state':'IN_SERVICE','staffing_enabled':True,'reserved':False}]
        t={'location':[bed,peer],'bed_event':events}
        v=availability(t,START);self.assertEqual((v['licensed'],v['staffed'],v['occupied'],v['immediately_available']),(2,2,1,0))
        events[0]['staffing_enabled']=False
        v=availability(t,START);self.assertEqual((v['staffed'],v['occupied']),(1,1))
        events[0].update(occupancy_state='EMPTY',reason='READY',staffing_enabled=True,reserved=True)
        v=availability(t,START);self.assertEqual((v['reserved'],v['immediately_available']),(1,1))
        request={'administrative_sex':'F','isolation_required':True,'allowed_services':['ICU']}
        self.assertEqual(availability(t,START,request=request)['patient_compatible'],0)

    def test_current_state_projection_matches_reconciled_closing_census(self):
        projected=availability(self.tables,CUTOFF,'2026-01-10T23:59:59Z')
        self.assertEqual(projected['occupied'],self.checked['metrics']['closing_census']);self.assertEqual(projected['unknown_bed_states'],0)
        self.assertLessEqual(projected['immediately_available'],projected['staffed']-projected['occupied'])

    def test_availability_normalizes_offsets_and_rejects_unobserved_future(self):
        a=availability(self.tables,'2024-07-15T18:00:00Z','2024-07-15T18:00:00Z')
        b=availability(self.tables,'2024-07-15T13:00:00-05:00','2024-07-15T13:00:00-05:00')
        self.assertEqual(a,b)
        with self.assertRaisesRegex(ValueError,'outside the three-year'):availability(self.tables,'2026-02-01T00:00:00Z')

    def test_internal_and_site_transfers_have_balanced_atomic_legs(self):
        self.assertEqual(self.checked['metrics']['site_transfers'],12);self.assertGreater(self.checked['metrics']['internal_transfers'],100)
        rows=self.tables['bed_event'];index=next(i for i,r in enumerate(rows) if r['transfer_group_id'] and r['event_type']=='OCCUPY')
        t=dict(self.tables);t['bed_event']=list(rows);t['bed_event'][index]={**rows[index],'transfer_group_id':None}
        with self.assertRaisesRegex(ValueError,'unpaired atomic transfer'):self.validator(t).check_state()

    def test_cross_city_transport_respects_route_and_handover_windows(self):
        latest=self.validator().latest;recipient=next(e for e in latest.values() if e['admission_source']=='TRANSFER')
        sender=self.enc[recipient['previous_encounter_version_id']]
        compressed=(instant(sender['discharged_at'])+timedelta(minutes=30)).isoformat().replace('+00:00','Z')
        t=dict(self.tables);t['encounter']=[{**r,'arrival_at':compressed} if r['encounter_id']==recipient['encounter_id'] else r for r in self.tables['encounter']]
        with self.assertRaisesRegex(ValueError,'site transport violates configured route'):self.validator(t).check_state()
        self.assertGreater(self.checked['metrics']['site_transport_seconds'],12*60*60)

    def test_network_continuation_is_source_known_before_capacity_exemption(self):
        notes=[r for r in self.tables['clinical_event'] if r['source_record_id'].endswith('/transfer-referral')]
        self.assertEqual(len(notes),24)
        for note in notes:
            e=self.enc[note['encounter_version_id']]
            self.assertEqual(note['known_from'],e['admitted_at'])
            if e['admission_source']=='TRANSFER':self.assertIn('receiving arrival is observed at '+e['arrival_at'],note['text_value']);self.assertIn('Later care outcome is not yet established',note['text_value'])
            else:self.assertIn('actual handoff time is not yet established',note['text_value'])
        t=dict(self.tables);t['clinical_event']=[r for r in self.tables['clinical_event'] if r['clinical_event_version_id']!=notes[0]['clinical_event_version_id']]
        with self.assertRaisesRegex(ValueError,'source-known referral'):self.validator(t).check_state()

    def test_capacity_transfer_does_not_force_clinical_deterioration(self):
        cases={self.enc[r['encounter_version_id']]['encounter_id'] for r in self.tables['clinical_event'] if r['source_record_id'].endswith('/placement-disposition') and 'external transfer at' in r['text_value']}
        catalog={r['catalog_item_id']:r['code'] for r in self.tables['catalog_item']}
        observations={}
        for r in self.tables['clinical_event']:
            eid=self.enc[r['encounter_version_id']]['encounter_id']
            if eid in cases and r['event_type']=='OBSERVATION':observations.setdefault((eid,catalog[r['catalog_item_id']]),[]).append(r)
        recovery=[]
        from decimal import Decimal
        for (eid,code),rows in observations.items():
            if code not in ('OBS-006','OBS-007','OBS-005','OBS-019'):continue
            rows.sort(key=lambda r:r['occurred_at'])
            if len(rows)>=2:recovery.append(Decimal(rows[-1]['numeric_value'])<Decimal(rows[0]['numeric_value']))
        self.assertGreater(len(recovery),100);self.assertGreater(sum(recovery)/len(recovery),.8)

    def test_conflicting_duplicate_and_orphan_correction_fail_closed(self):
        rows=self.tables['bed_event'];r=rows[0]
        with self.assertRaisesRegex(ValueError,'conflicting duplicate'):resolve_events([r,{**r,'reason':'CONFLICT'}])
        correction=next(r for r in rows if r['event_type']=='CORRECTION')
        with self.assertRaisesRegex(ValueError,'orphan correction'):resolve_events([correction])

    def test_source_sequence_and_required_correction_target_are_enforced(self):
        rows=self.tables['bed_event'];correction=next(r for r in rows if r['event_type']=='CORRECTION')
        t=dict(self.tables);t['bed_event']=[{**r,'corrects_bed_event_id':None} if r['bed_event_id']==correction['bed_event_id'] else r for r in rows]
        with self.assertRaisesRegex(ValueError,'correction must identify'):self.validator(t).check_clocks()
        same=sorted((r for r in rows if r['bed_location_id']==correction['bed_location_id']),key=lambda r:r['sequence_no'])
        a,b=same[0],same[-1];swap={a['bed_event_id']:b['sequence_no'],b['bed_event_id']:a['sequence_no']}
        t['bed_event']=[{**r,'sequence_no':swap[r['bed_event_id']]} if r['bed_event_id'] in swap else r for r in rows]
        with self.assertRaisesRegex(ValueError,'source sequence does not follow'):self.validator(t).check_clocks()

    def test_duplicate_reservation_transition_is_rejected(self):
        rows=self.tables['bed_event'];hold=next(r for r in resolve_events(rows) if r['_kind']=='RESERVE')
        duplicate={k:v for k,v in hold.items() if not k.startswith('_')};duplicate.update(bed_event_id='deliberate-duplicate-hold',sequence_no=hold['sequence_no']+1)
        t=dict(self.tables);t['bed_event']=[*rows,duplicate]
        with self.assertRaisesRegex(ValueError,'duplicate or invalid reservation'):self.validator(t).check_state()

    def test_late_duplicate_and_cancelled_reservation_replay_converges(self):
        rows=self.tables['bed_event'];self.assertEqual(resolve_events(rows),resolve_events([*reversed(rows),*rows[:250]]))
        self.assertEqual(self.checked['metrics']['replay_convergence'],'PASS')

    def test_correction_preserves_before_delivery_knowledge(self):
        by_id={r['bed_event_id']:r for r in self.tables['bed_event']}
        c=next(r for r in self.tables['bed_event'] if r['event_type']=='CORRECTION' and by_id[r['corrects_bed_event_id']]['delivery_at']<r['delivery_at'])
        original=by_id[c['corrects_bed_event_id']]
        before=resolve_events([original,c],original['delivery_at']);after=resolve_events([original,c],c['delivery_at'])
        self.assertEqual(before[0]['service_state'],'BLOCKED');self.assertEqual(after[0]['service_state'],'IN_SERVICE')
        # A correction that arrives before its original waits for that dependency.
        early={**c,'delivery_at':original['delivery_at'],'export_available_at':original['delivery_at']}
        late={**original,'delivery_at':c['delivery_at'],'export_available_at':c['delivery_at']}
        self.assertEqual(resolve_events([late,early],early['delivery_at']),[])
        self.assertEqual(len(resolve_events([late,early],late['delivery_at'])),1)

    def test_room_cohort_incompatibility_is_rejected(self):
        openings=[r for r in self.tables['bed_event'] if r['event_type']=='OPENING' and r['occupancy_state']=='OCCUPIED']
        locations={r['location_id']:r for r in self.tables['location']}
        pair=next((a,b) for a in openings for b in openings if a['bed_event_id']!=b['bed_event_id'] and locations[a['bed_location_id']]['parent_location_id']==locations[b['bed_location_id']]['parent_location_id'])
        key=self.enc[pair[1]['encounter_version_id']]['patient_version_id']
        t=dict(self.tables);t['patient']=[{**p,'administrative_sex':'F' if p['administrative_sex']=='M' else 'M'} if p['patient_version_id']==key else p for p in self.tables['patient']]
        with self.assertRaisesRegex(ValueError,'room cohort'):self.validator(t).check_state()

    def test_no_patient_can_occupy_two_beds(self):
        rows=self.tables['bed_event'];openings=[r for r in resolve_events(rows) if r['_kind']=='OPENING' and r['occupancy_state']=='OCCUPIED']
        a=openings[0];b=next(r for r in openings[1:] if self.enc[r['encounter_version_id']]['facility_id']==self.enc[a['encounter_version_id']]['facility_id'])
        t=dict(self.tables);t['bed_event']=[{**r,'encounter_version_id':a['encounter_version_id']} if r['bed_event_id']==b['bed_event_id'] else r for r in rows]
        with self.assertRaisesRegex(ValueError,'simultaneous inpatient'):self.validator(t).check_state()

    def test_placement_before_clean_ready_is_rejected(self):
        rows=self.tables['bed_event'];target=next(r for r in rows if r['event_type']=='CLEAN_START')
        t=dict(self.tables);t['bed_event']=[r for r in rows if r['bed_event_id']!=target['bed_event_id']]
        with self.assertRaisesRegex(ValueError,'cleanliness transition'):self.validator(t).check_state()

    def test_saturated_capacity_retains_waiting_demand_and_reservations(self):
        g=DemandGenerator(self.tables,self.ccfg,read(ROOT/'contracts/clinical-history-policy.json'),'stress',self.cfg)
        sim=FlowSimulator(self.tables,g,self.cfg)
        cases=[e for e in sim.latest.values() if e['encounter_class']=='IPD' and not e['carry_in'] and e['initial_acuity']==3 and sim.diagnosis[e['encounter_id']]!='J189']
        a=cases[0];b=next(e for e in cases[1:] if e['facility_id']==a['facility_id'] and e['patient_version_id']!=a['patient_version_id'])
        at=instant(max(a['admitted_at'],b['admitted_at']))
        for state in sim.state.values():state.update(service_state='OUT_OF_SERVICE',staffing_enabled=False)
        sim.waiting={a['encounter_id']:(False,at),b['encounter_id']:(False,at)};sim.dispatch(at)
        self.assertEqual(len(sim.waiting),2);self.assertEqual(sim.events,[])
        bed=next(x for x in sim.beds if x['facility_id']==a['facility_id'] and x['service_line']=='MEDICINE')
        sim.state[bed['location_id']].update(service_state='IN_SERVICE',staffing_enabled=True)
        sim.dispatch(at+timedelta(minutes=30))
        self.assertEqual(len(sim.waiting),1);self.assertEqual(len(sim.reserving),1)
        self.assertEqual(sim.events[0]['event_type'],'RESERVE');self.assertFalse(sim.placed)

    def test_daily_drivers_are_realized_only_after_local_day_end(self):
        t=dict(self.tables);t['facility_day_driver']=list(self.tables['facility_day_driver']);r=t['facility_day_driver'][0]
        t['facility_day_driver'][0]={**r,'observations_known_at':r['calendar_date']+'T12:00:00Z'}
        with self.assertRaisesRegex(ValueError,'realized driver leaked'):self.validator(t).check_drivers()

    def test_surge_changes_connected_respiratory_cohorts(self):
        ops={**self.cfg,'surge_start':'2099-01-01','surge_end':'2099-02-01'}
        g=DemandGenerator(self.master,self.ccfg,read(ROOT/'contracts/clinical-history-policy.json'),'counterfactual',ops)
        journeys=g.journeys();catalog={r['catalog_item_id']:r for r in self.master['catalog_item']}
        index={r['encounter_version_id']:r for r in journeys['encounter']}
        count=sum(c['revision_no']==1 and c['diagnosis_rank']==1 and catalog[c['catalog_item_id']]['code'] in ('J189','J449')
                  and '2024-01-08'<=index[c['encounter_version_id']]['arrival_at'][:10]<'2024-02-26'
                  for c in journeys['clinical_condition'] if c['encounter_version_id'])
        self.assertGreater(self.checked['metrics']['surge_counts']['resp'],count+100)

    def test_calendar_seasonality_and_facility_curves(self):
        self.assertEqual(len(self.checked['metrics']['monthly_ed_counts']),36)
        self.assertTrue(1.1<=float(self.checked['metrics']['monthly_ed_rate_peak_trough'])<=1.8)

    def test_operational_elective_window_is_an_explicit_scoped_addendum(self):
        policy=read(ROOT/'contracts/clinical-history-policy.json')
        standalone=ClinicalValidator(self.tables,self.schema,self.ccfg,policy,self.master).check('TRAJECTORIES')
        self.assertEqual(standalone['status'],'FAIL');self.assertIn('weekday/daytime schedule',standalone['failures'][0]['reason'])
        from healthcare_synthetic.operational_validation import IntegratedClinicalValidator
        integrated=IntegratedClinicalValidator(self.tables,self.schema,self.ccfg,policy,self.master).check('TRAJECTORIES')
        self.assertEqual(integrated['status'],'PASS',integrated)

    def test_recipient_encounter_identity_cannot_drift_between_revisions(self):
        from healthcare_synthetic.operational_validation import IntegratedClinicalValidator
        rows=self.tables['encounter'];target=next(r for r in rows if r['admission_source']=='TRANSFER' and r['revision_no']==2)
        patient_by_version={p['patient_version_id']:p['patient_id'] for p in self.tables['patient']}
        other=next(p for p in self.tables['patient'] if p['patient_id']!=patient_by_version[target['patient_version_id']])
        t=dict(self.tables);t['encounter']=[{**r,'patient_version_id':other['patient_version_id']} if r['encounter_version_id']==target['encounter_version_id'] else r for r in rows]
        result=IntegratedClinicalValidator(t,self.schema,self.ccfg,read(ROOT/'contracts/clinical-history-policy.json'),self.master).check('ENCOUNTERS')
        self.assertEqual(result['status'],'FAIL');self.assertIn('logical encounter identity drifts',result['failures'][0]['reason'])

    def test_review_hundred_cases_is_content_bound(self):
        body,s=render_operations(self.tables,self.cfg);decision=read(ROOT/'reviews/operational-flow-review.json')
        self.assertEqual(s['cases'],100);self.assertTrue({'CARRY_IN','SITE_TRANSFER','ICU_STEPDOWN','MAINTENANCE_SEASON','BOARDING_OVER_HOUR'}<=set(s['strata']))
        self.assertEqual(review_gate(s,decision)['status'],'PASS')
        self.assertEqual(review_gate({**s,'selected_facts_sha256':'changed'},decision)['status'],'PENDING_REVIEW')
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),s['sample_sha256'])

    def test_review_waits_use_chronological_first_placement(self):
        import re
        from decimal import Decimal
        body,_=render_operations(self.tables,self.cfg);first={}
        for _,eid,a,_ in bed_intervals(self.tables['bed_event'],self.enc):first[eid]=min(first.get(eid,a),a)
        latest=self.validator().latest
        for section in body.split('## Case ')[1:]:
            eid=re.search(r'Encounter (encounter_[a-f0-9]+);',section).group(1);e=latest[eid]
            stop=first.get(eid,e['discharged_at'] or CUTOFF)
            expected=Decimal(seconds(max(START,e['admitted_at']),stop))/3600
            self.assertIn(f'Time from admission/opening to first placement: {expected:.3f} hours.',section)
            starts=re.findall(r'^- [A-Z]+-R\d+-B\d+: (\S+) to ',section,re.MULTILINE)
            self.assertEqual(starts,sorted(starts))

    def test_review_is_reproducible_from_reordered_persisted_rows(self):
        body,selection=render_operations(self.tables,self.cfg)
        reordered={name:list(reversed(rows)) for name,rows in self.tables.items()}
        other,other_selection=render_operations(reordered,self.cfg)
        self.assertEqual(body,other);self.assertEqual(selection,other_selection)

    def test_frozen_budget_counts_all_versions_and_corrections(self):
        t=dict(self.tables);t['bed_event']=[self.tables['bed_event'][0]]*80001
        with self.assertRaisesRegex(ValueError,'budget exceeded: bed_event'):self.validator(t).check_budget()

    def test_oracle_does_not_import_simulator_or_random_draw(self):
        tree=ast.parse((ROOT/'src/healthcare_synthetic/operational_validation.py').read_text())
        imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any('generation' in n or 'core' in n or 'pipeline' in n for n in imports))

    def test_independent_persisted_inspector_recomputes_controls(self):
        result=inspect_operations(self.base)
        self.assertEqual(result['gate_status'],'OPERATIONAL_FLOW_PASSED',result['defects']);self.assertEqual(result['artifact_integrity'],'PASS')

    def command(self,output,*options):
        return subprocess.run([sys.executable,str(ROOT/'scripts/generate_operational_flow.py'),'--output',str(output),*options],capture_output=True,text=True,timeout=1800)

    def test_clean_end_to_end_rebuild_and_cached_resume(self):
        output=self.work/'clean-rebuild';result=self.command(output)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);m=read(output/'manifest.json')
        self.assertEqual(m['business_sha256'],self.manifest['business_sha256'])
        result=self.command(output);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        m=read(output/'manifest.json');self.assertEqual(m['executed'],[]);self.assertEqual(set(m['reused']),set(GRAPH))

    def test_actual_process_crash_rolls_back_then_resumes(self):
        output=self.work/'crash-recovery';output.mkdir()
        with sqlite3.connect(self.base/'checkpoints.sqlite3') as source,sqlite3.connect(output/'checkpoints.sqlite3') as target:
            source.backup(target);target.execute("DELETE FROM stages WHERE name='validation'");target.commit()
        (output/'manifest.json').write_text(json.dumps({'profile':'OPERATIONAL_PATIENT_FLOW'}))
        crashed=self.command(output,'--crash-stage','validation');self.assertEqual(crashed.returncode,97,crashed.stdout+crashed.stderr)
        with sqlite3.connect(output/'checkpoints.sqlite3') as c:self.assertEqual(c.execute("SELECT count(*) FROM stages WHERE name='validation'").fetchone()[0],0)
        self.assertFalse((output/'candidate-ready.json').exists())
        resumed=self.command(output);self.assertEqual(resumed.returncode,0,resumed.stdout+resumed.stderr)
        m=read(output/'manifest.json');self.assertEqual(m['executed'],['validation']);self.assertEqual(m['business_sha256'],self.manifest['business_sha256'])

    def test_corrupt_checkpoint_fails_closed(self):
        output=self.work/'corrupt';output.mkdir()
        from healthcare_synthetic.engine import Store
        store=Store(output/'checkpoints.sqlite3')
        store.db.execute('INSERT INTO stages VALUES (?,?,?,?,?,?)',('flow','bad','bad','{}','corrupt',0));store.db.commit();store.close()
        with self.assertRaisesRegex(ValueError,'checkpoint corruption'):run_operations(output_dir=output)
        self.assertFalse((output/'candidate-ready.json').exists())

    def test_changed_seed_invalidates_children_before_a_failed_recompute(self):
        output=self.work/'changed-seed';output.mkdir()
        with sqlite3.connect(self.base/'checkpoints.sqlite3') as source:row=source.execute("SELECT name,local_hash,input_hash,payload,checksum,row_count FROM stages WHERE name='validation'").fetchone()
        from healthcare_synthetic.engine import Store
        store=Store(output/'checkpoints.sqlite3');store.db.execute('INSERT INTO stages VALUES (?,?,?,?,?,?)',row);store.db.commit();store.close()
        (output/'manifest.json').write_text(json.dumps({'profile':'OPERATIONAL_PATIENT_FLOW'}));(output/'candidate-ready.json').write_text('{}')
        cfg={**self.cfg,'seed':self.cfg['seed']+1};path=self.work/'changed-seed.json';path.write_text(json.dumps(cfg))
        result=self.command(output,'--config',str(path),'--fail-stage','flow')
        self.assertNotEqual(result.returncode,0);manifest=read(output/'manifest.json')
        self.assertEqual(manifest['status'],'FAILED');self.assertIn('validation',manifest['invalidated'])
        self.assertFalse((output/'candidate-ready.json').exists())
        with sqlite3.connect(output/'checkpoints.sqlite3') as c:self.assertEqual(c.execute('SELECT count(*) FROM stages').fetchone()[0],0)

    def test_unreviewed_limits_cannot_silently_change(self):
        cfg=copy.deepcopy(self.cfg);cfg['maintenance_bed_days']=0;path=self.work/'invalid-config.json';path.write_text(json.dumps(cfg))
        with self.assertRaisesRegex(ValueError,'reviewed operational configuration'):run_operations(path,self.work/'invalid')

if __name__=='__main__':unittest.main()
