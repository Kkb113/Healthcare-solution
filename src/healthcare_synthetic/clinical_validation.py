"""Independent clinical invariants and cohort oracles. Does not import generation code."""
from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from .master_validation import MasterValidator, contains, grouped, timestamp, years


class ClinicalValidator:
    def __init__(self, tables, schema, cfg, policy, master):
        self.t, self.schema, self.cfg, self.policy, self.master = tables, schema, cfg, policy, master
        self.spec = {s['name']: s for s in schema['tables']}
        self.idx = {t: {r[self.spec[t]['primary_key'][0]]: r for r in rows} for t, rows in tables.items()}
        self.encounters = grouped(tables['encounter'], 'encounter_id')
        self.latest = {k: max(v, key=lambda r: r['revision_no']) for k, v in self.encounters.items()}
        self.patient = self.idx['patient']
        self.catalog = self.idx['catalog_item']
        self.events = self.idx['clinical_event']
        self.events_by_encounter = defaultdict(list)
        self.conditions_by_encounter = defaultdict(list)
        self.by_person = defaultdict(list)
        self.deaths = {}
        for e in self.latest.values():
            pid = self.person(e)
            self.by_person[pid].append(e)
            if e['disposition'] == 'DEATH':
                self.deaths[pid] = e['discharged_at']
        for p in tables['patient']:
            if p['deceased_at']:
                self.deaths[p['patient_id']] = min(self.deaths.get(p['patient_id'], p['deceased_at']), p['deceased_at'])
        for r in tables['clinical_event']:
            self.events_by_encounter[self.idx['encounter'][r['encounter_version_id']]['encounter_id']].append(r)
        for r in tables['clinical_condition']:
            if r['encounter_version_id']:
                self.conditions_by_encounter[self.idx['encounter'][r['encounter_version_id']]['encounter_id']].append(r)
        self.metrics = {}
        self.cutoff = '2026-01-01T06:00:00Z'
        self.start = '2023-01-01T06:00:00Z'

    def person(self, encounter):
        return self.patient[encounter['patient_version_id']]['patient_id']

    def need(self, ok, key, reason):
        if not ok:
            exc = ValueError(reason)
            exc.record_key = key
            raise exc

    def check(self, name):
        try:
            getattr(self, 'check_' + name.lower())()
            return {'rule_id': name, 'status': 'PASS', 'severity': 'P0', 'scope': 'FULL_CLINICAL_CANDIDATE', 'failures': []}
        except Exception as exc:
            return {'rule_id': name, 'status': 'FAIL', 'severity': 'P0', 'scope': 'FULL_CLINICAL_CANDIDATE',
                    'failures': [{'record_key': str(getattr(exc, 'record_key', name)), 'reason': str(exc), 'error_type': type(exc).__name__}]}

    def run(self):
        checks = [self.check(n) for n in self.policy['checks']]
        defects = [{'defect_id': hashlib.sha256((r['rule_id'] + f['record_key']).encode()).hexdigest()[:32], 'rule_id': r['rule_id'], 'severity': 'P0', **f}
                   for r in checks if r['status'] != 'PASS' for f in r['failures']]
        # Derived ratios are controls, never binary floating-point business facts or checkpoint values.
        def exact(value):
            if isinstance(value, float): return str(Decimal(str(value)))
            if isinstance(value, dict): return {k: exact(v) for k, v in value.items()}
            if isinstance(value, list): return [exact(v) for v in value]
            return value
        return {'status': 'CLINICAL_CHECKS_PASSED' if not defects else 'BLOCKED', 'checks': checks, 'defects': defects, 'metrics': exact(self.metrics),
                'full_dataset_accepted': False, 'solution_status': 'BLOCKED_FOR_SOLUTION', 'trajectory_status': self.policy['trajectory_status']}

    def common(self, method):
        validator = MasterValidator(self.t, self.schema, {}, {'permitted_tables': list(self.t)}, {})
        getattr(validator, 'check_' + method)()

    def check_schema(self): self.common('schema')
    def check_keys(self): self.common('keys')
    def check_references(self): self.common('references')

    def check_master_preservation(self):
        for table, rows in self.master.items():
            for row in rows:
                key = row[self.spec[table]['primary_key'][0]]
                self.need(self.idx[table].get(key) == row, key, 'accepted master row was changed or removed')
            if table != 'clinical_condition':
                self.need(len(self.t[table]) == len(rows), table, 'master table received unauthorized extra rows')

    def check_availability(self):
        for table in ('encounter', 'appointment', 'clinical_condition', 'clinical_event'):
            for r in self.t[table]:
                key = r[self.spec[table]['primary_key'][0]]
                self.need(r['source_system'] == self.spec[table]['source_authority'], key, 'wrong source authority')
                self.need(r['recorded_at'] <= r['export_available_at'] <= self.cfg['window']['delivery_grace_end'], key, 'source/export/grace chronology')
                if 'known_from' in r:
                    self.need(r['recorded_at'] <= r['known_from'], key, 'knowledge precedes source recording')
                    self.need(r['known_to'] is None or r['known_from'] < r['known_to'], key, 'empty knowledge interval')
                if table == 'clinical_event':
                    self.need(r['occurred_at'] <= r['known_from'] and r['occurred_at'] < self.cutoff, key, 'future care occurrence or anticipatory knowledge')
                    for field in ('period_end_at', 'result_ready_at', 'collected_at', 'document_signed_at'):
                        self.need(r[field] is None or r[field] <= r['known_from'], key, field + ' is not yet known')

    def check_encounters(self):
        classes = Counter()
        carry = transfers = 0
        for eid, rows in self.encounters.items():
            ordered = sorted(rows, key=lambda r: r['revision_no'])
            self.need([r['revision_no'] for r in ordered] == list(range(1, len(rows) + 1)), eid, 'noncontiguous encounter revisions')
            for i, e in enumerate(ordered):
                if i:
                    self.need(ordered[i-1]['known_to'] == e['known_from'], eid, 'encounter knowledge chain is broken')
                self.need(e['known_to'] == (ordered[i+1]['known_from'] if i+1 < len(rows) else None), eid, 'encounter supersession is wrong')
                self.need(1 <= e['initial_acuity'] <= 5, eid, 'triage acuity outside configured scale')
                if e['encounter_class'] == 'IPD':
                    self.need(e['planned'] == (e['admission_source'] == 'ELECTIVE'), eid, 'elective/planned inpatient mismatch')
                p = self.patient[e['patient_version_id']]
                self.need(years(p['birth_date'], e['arrival_at'][:10]) >= 18, eid, 'encounter before birth or adult eligibility')
                pid = p['patient_id']
                self.need(pid not in self.deaths or e['arrival_at'] <= self.deaths[pid], eid, 'encounter after observed death')
                self.need(contains(p, e['arrival_at'], e['arrival_at'], availability=False), eid, 'patient snapshot not known/effective at creation')
                cov = self.idx['patient_coverage'][e['coverage_version_id']]
                self.need(self.patient[cov['patient_version_id']]['patient_id'] == pid and contains(cov, e['arrival_at'], e['arrival_at'], availability=False), eid, 'coverage snapshot mismatch')
                loc = self.idx['location'][e['location_id']]
                self.need(loc['facility_id'] == e['facility_id'], eid, 'location belongs to another facility')
                chain = [e['arrival_at']] + [e[k] for k in ('admission_decision_at', 'admitted_at', 'medically_ready_at', 'discharged_at') if e[k]]
                self.need(chain == sorted(chain) and all(t <= e['known_from'] for t in chain), eid, 'future or unordered encounter milestones')
                self.need(e['discharged_at'] is None or e['discharged_at'] < self.cutoff, eid, 'post-cutoff discharge must remain censored')
                self.need((e['disposition'] == 'OPEN') == (e['discharged_at'] is None), eid, 'open/completed disposition mismatch')
                if e['encounter_class'] != 'IPD':
                    self.need(e['admitted_at'] is None, eid, 'non-IPD has an inpatient admission')
                previous = e['previous_encounter_version_id']
                if previous:
                    prior = self.idx['encounter'][previous]
                    self.need(self.person(prior) == pid and prior['known_from'] <= e['arrival_at'] and prior['arrival_at'] < e['arrival_at'], eid, 'predecessor wrong patient or future knowledge')
                if e['attending_assignment_id']:
                    self.valid_author(e['attending_assignment_id'], e['facility_id'], e['arrival_at'], eid)
            e = ordered[-1]
            if e['arrival_at'] >= self.start or e['carry_in']:
                classes[e['encounter_class']] += 1
            if e['carry_in']:
                carry += 1
                self.need(e['arrival_at'] < self.start and (e['discharged_at'] or self.cutoff) > self.start and e['encounter_class'] == 'IPD', eid, 'invalid occupied carry-in')
            if e['encounter_class'] == 'IPD' and e['admission_source'] == 'ED':
                previous = self.idx['encounter'][e['previous_encounter_version_id']]
                ed = self.latest[previous['encounter_id']]
                self.need(ed['encounter_class'] == 'ED' and ed['discharged_at'] == e['arrival_at'] and ed['episode_id'] == e['episode_id'] and ed['disposition'] == 'TRANSFER', eid, 'ED-IPD episode does not reconcile')
                transfers += 1
        self.need(classes == {'IPD': 12000, 'ED': 27000, 'OPD': 17000} and carry == 57 and transfers == 6000, 'cohort', 'encounter class, carry-in or ED admission counts differ')
        self.need(len(self.latest) == 58000, 'cohort', 'opening-context distinct encounter count differs')
        for pid, visits in self.by_person.items():
            ordered = sorted(visits, key=lambda r: r['arrival_at'])
            for a, b in zip(ordered, ordered[1:]):
                self.need((a['discharged_at'] or self.cutoff) <= b['arrival_at'], pid, 'overlapping care encounters for one patient')
        self.metrics.update(encounter_classes=dict(classes), occupied_carry_in=carry, ed_admission_links=transfers, death_outcomes=len(self.deaths),
                            open_inpatient=sum(e['encounter_class'] == 'IPD' and e['discharged_at'] is None for e in self.latest.values()))

    def valid_author(self, key, facility, at, context):
        w = self.idx['worker_assignment'][key]
        day = timestamp(at).astimezone(self.local_zone).date().isoformat()
        self.need(w['facility_id'] == facility and w['role'] == 'PHYSICIAN' and contains(w, at, at, availability=False)
                  and w['hire_date'] <= day and (w['termination_date'] is None or day < w['termination_date'])
                  and w['credential_valid_from'] <= day < w['credential_valid_to'], context, 'author not an eligible source clinician')

    def check_appointments(self):
        counts = Counter()
        linked = set()
        for r in self.t['appointment']:
            key = r['appointment_id']
            self.need(r['booked_at'] <= r['scheduled_start'] < r['scheduled_end'], key, 'booking/slot chronology')
            self.need(r['booked_at'] <= r['recorded_at'], key, 'booking not yet known in source extract')
            self.need(contains(self.patient[r['patient_version_id']], r['booked_at'], r['booked_at'], availability=False), key, 'booking patient snapshot not known/effective')
            self.need((r['arrived_at'] is not None) == (r['resulting_encounter_version_id'] is not None), key, 'unattended booking linked to care')
            if r['worker_assignment_id']:
                fid = self.idx['location'][r['location_id']]['facility_id']
                self.valid_author(r['worker_assignment_id'], fid, r['booked_at'], key)
            flags = [r['arrived_at'], r['cancelled_at'], r['no_show_recorded_at']]
            self.need(sum(v is not None for v in flags) <= 1, key, 'appointment has conflicting outcomes')
            self.need(all(t <= r['recorded_at'] for t in flags if t), key, 'appointment outcome exposed at booking')
            if r['no_show_recorded_at']:
                self.need(r['no_show_recorded_at'] >= r['scheduled_end'], key, 'no-show before slot ended')
                counts['NO_SHOW'] += 1
            elif r['cancelled_at']:
                self.need(r['booked_at'] <= r['cancelled_at'] <= r['scheduled_start'], key, 'cancellation chronology')
                counts['CANCELLED'] += 1
            elif r['arrived_at']:
                e = self.idx['encounter'][r['resulting_encounter_version_id']]
                self.need(self.patient[r['patient_version_id']]['patient_id'] == self.person(e) and r['arrived_at'] == e['arrival_at'], key, 'attended slot patient/encounter mismatch')
                self.need(e['planned'] and self.idx['location'][r['location_id']]['facility_id'] == e['facility_id'], key, 'attended scheduled visit lacks planned flag or hospital match')
                self.need((r['appointment_type'] == 'ELECTIVE_ADMISSION') == (e['encounter_class'] == 'IPD'), key, 'appointment type does not match care setting')
                self.need(e['encounter_id'] not in linked, key, 'multiple attended bookings for one encounter')
                linked.add(e['encounter_id'])
                counts['ATTENDED'] += 1
            else:
                self.need(r['resulting_encounter_version_id'] is None and r['scheduled_start'] >= self.cutoff, key, 'pending appointment invents an outcome')
                counts['CENSORED'] += 1
            if r['replacement_appointment_id']:
                replacement = self.idx['appointment'][r['replacement_appointment_id']]
                self.need(r['cancel_reason'] == 'RESCHEDULE' and r['cancelled_at'] <= replacement['booked_at'] and self.patient[r['patient_version_id']]['patient_id'] == self.patient[replacement['patient_version_id']]['patient_id'], key, 'invalid reschedule linkage')
                seen, cursor = {key}, replacement
                while cursor['replacement_appointment_id']:
                    self.need(cursor['appointment_id'] not in seen, key, 'cyclic appointment replacements')
                    seen.add(cursor['appointment_id'])
                    cursor = self.idx['appointment'][cursor['replacement_appointment_id']]
                self.need(cursor['appointment_id'] not in seen, key, 'cyclic appointment replacements')
        self.need(counts == {'ATTENDED': 21800, 'NO_SHOW': 4000, 'CANCELLED': 4000, 'CENSORED': 200}, 'appointments', 'appointment outcomes differ')
        self.metrics['appointment_outcomes'] = dict(counts)

    def check_conditions(self):
        for cid, rows in grouped(self.t['clinical_condition'], 'condition_id').items():
            self.need(sorted(r['revision_no'] for r in rows) == list(range(1, len(rows)+1)), cid, 'condition revision sequence')
            for r in rows:
                cat = self.catalog[r['catalog_item_id']]
                allergy = r['condition_type'] == 'ALLERGY'
                self.need(cat['domain'] == ('ALLERGEN' if allergy else 'DIAGNOSIS'), cid, 'condition has wrong typed code')
                self.need((r['reaction'] is not None) == allergy, cid, 'allergy reaction or non-allergy reaction mismatch')
                self.need(r['onset_at'] is None or r['onset_at'] <= r['known_from'], cid, 'future onset asserted as observed')
                self.need(r['onset_at'] is None or r['onset_at'][:10] >= self.patient[r['patient_version_id']]['birth_date'], cid, 'condition onset before birth')
                pid = self.patient[r['patient_version_id']]['patient_id']
                self.need(r['onset_at'] is None or pid not in self.deaths or r['onset_at'] <= self.deaths[pid], cid, 'condition onset after death')
                self.need(r['resolved_at'] is None or r['onset_at'] <= r['resolved_at'] <= r['known_from'], cid, 'future or pre-onset resolution')
                self.need(r['resolved_at'] is None or r['resolved_at'] < self.cutoff, cid, 'post-cutoff resolution is unobserved')
                self.need(r['resolved_at'] is None or pid not in self.deaths or r['resolved_at'] <= self.deaths[pid], cid, 'clinical recovery asserted after death')
                self.need(r['valid_to'] is None or r['valid_from'] < r['valid_to'], cid, 'empty condition validity interval')
                self.need((r['status'] == 'RESOLVED') == (r['resolved_at'] is not None), cid, 'resolution status mismatch')
                if r['condition_type'] == 'DIAGNOSIS':
                    e = self.idx['encounter'][r['encounter_version_id']]
                    self.need(r['diagnosis_rank'] >= 1 and self.person(e) == self.patient[r['patient_version_id']]['patient_id'] and e['known_from'] <= r['known_from'], cid, 'diagnosis context/patient/knowledge mismatch')
                else:
                    self.need(r['diagnosis_rank'] == 0 and r['encounter_version_id'] is None, cid, 'problem/allergy has encounter diagnosis fields')
            for i, a in enumerate(rows):
                for b in rows[i+1:]:
                    valid = (a['valid_to'] is None or b['valid_from'] < a['valid_to']) and (b['valid_to'] is None or a['valid_from'] < b['valid_to'])
                    known = (a['known_to'] is None or b['known_from'] < a['known_to']) and (b['known_to'] is None or a['known_from'] < b['known_to'])
                    self.need(not (valid and known), cid, 'overlapping condition bitemporal rectangles')
        for eid, e in self.latest.items():
            if e['disposition'] != 'LEFT_WITHOUT_SEEN':
                primaries = [r for r in self.conditions_by_encounter[eid] if r['diagnosis_rank'] == 1 and r['known_to'] is None and r['valid_to'] is None]
                self.need(len(primaries) == 1, eid, 'assessed visit lacks one current primary diagnosis')

    def check_terminology(self):
        for r in self.t['clinical_event']:
            if r['catalog_item_id'] is None:
                self.need(r['event_type'] == 'DOCUMENT', r['clinical_event_version_id'], 'non-document missing terminology')
                continue
            cat, key = self.catalog[r['catalog_item_id']], r['clinical_event_version_id']
            # UTC-6/-5 date boundary; use the locked tzdata bytes rather than the host zone database.
            from importlib import resources
            from io import BytesIO
            from zoneinfo import ZoneInfo
            if not hasattr(self, 'zone'):
                self.zone = ZoneInfo.from_file(BytesIO(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()))
            day = timestamp(r['occurred_at']).astimezone(self.zone).date().isoformat()
            self.need(cat['valid_from'] <= day and (cat['valid_to'] is None or day < cat['valid_to']), key, 'code release invalid for service date')
            domains = {'OBSERVATION': ['OBSERVATION'], 'LAB_RESULT': ['LAB'], 'PROCEDURE': ['PROCEDURE'], 'MED_ADMIN': ['MEDICATION'], 'MED_DISPENSE': ['MEDICATION'], 'ORDER': ['LAB', 'PROCEDURE', 'MEDICATION', 'OBSERVATION']}
            self.need(cat['domain'] in domains.get(r['event_type'], []), key, 'event family has wrong terminology domain')
            if r['event_type'] in ('OBSERVATION', 'LAB_RESULT'):
                self.need(r['value_unit'] == cat['base_unit'], key, 'measurement unit differs from catalog')
        for r in self.t['clinical_condition']:
            if r['condition_version_id'] in self.idx_master_conditions:
                continue
            cat = self.catalog[r['catalog_item_id']]
            day = timestamp(r['valid_from']).astimezone(self.zone).date().isoformat()
            # A later status assertion retains the original diagnostic code, not a recoding of disease.
            if r['revision_no'] == 1:
                self.need(cat['valid_from'] <= day and (cat['valid_to'] is None or day < cat['valid_to']), r['condition_version_id'], 'diagnosis code release invalid at assertion')

    @property
    def idx_master_conditions(self):
        if not hasattr(self, '_master_condition_ids'):
            self._master_condition_ids = {r['condition_version_id'] for r in self.master['clinical_condition']}
        return self._master_condition_ids

    def check_events(self):
        specimens = {}
        for r in self.t['clinical_event']:
            key = r['clinical_event_version_id']
            context = self.idx['encounter'][r['encounter_version_id']]
            e = self.latest[context['encounter_id']]
            self.need(context['known_from'] <= r['occurred_at'] and (context['known_to'] is None or r['occurred_at'] < context['known_to']), key, 'future or superseded encounter context')
            self.need(e['arrival_at'] <= r['occurred_at'] <= (e['discharged_at'] or self.cutoff), key, 'clinical event outside encounter')
            pid = self.person(e)
            self.need(pid not in self.deaths or r['occurred_at'] <= self.deaths[pid], key, 'clinical activity after death')
            self.valid_author(r['author_assignment_id'], e['facility_id'], r['occurred_at'], key)
            parent = r['parent_event_version_id']
            if r['event_type'] in ('LAB_RESULT', 'PROCEDURE', 'MED_ADMIN', 'MED_DISPENSE'):
                self.need(parent is not None, key, 'required order parent is absent')
            if parent:
                order = self.events[parent]
                oe = self.idx['encounter'][order['encounter_version_id']]
                self.need(order['event_type'] == 'ORDER' and oe['encounter_id'] == e['encounter_id'] and order['occurred_at'] <= r['occurred_at'] and order['known_from'] <= r['known_from'], key, 'order provenance patient/encounter/time mismatch')
                a, b = self.catalog[order['catalog_item_id']], self.catalog[r['catalog_item_id']]
                self.need((a['domain'], a['code']) == (b['domain'], b['code']), key, 'order/catalog incompatibility')
            if r['event_type'] == 'LAB_RESULT':
                self.need(r['specimen_id'] is not None and r['collected_at'] is not None and r['result_ready_at'] is not None
                          and self.events[parent]['occurred_at'] <= r['collected_at'] <= r['result_ready_at'] <= r['known_from'], key, 'specimen collection/result chronology')
                specimen_context = (pid, r['collected_at'])
                self.need(r['specimen_id'] not in specimens or specimens[r['specimen_id']] == specimen_context, key, 'specimen shared across patients or different collections')
                specimens[r['specimen_id']] = specimen_context
            if r['event_type'] in ('OBSERVATION', 'LAB_RESULT'):
                self.need((r['numeric_value'] is not None) != (r['text_value'] is not None), key, 'measurement must contain exactly one scalar value')
                self.need(r['reference_low'] is not None and r['reference_high'] is not None and Decimal(r['reference_low']) <= Decimal(r['reference_high']), key, 'measurement reference interval')
            if r['period_end_at']:
                self.need(r['occurred_at'] <= r['period_end_at'] <= (e['discharged_at'] or self.cutoff), key, 'service period outside care')
            medication = r['catalog_item_id'] and self.catalog[r['catalog_item_id']]['domain'] == 'MEDICATION'
            if r['event_type'] not in ('ORDER', 'MED_ADMIN', 'MED_DISPENSE') or (r['event_type'] == 'ORDER' and not medication):
                self.need(all(r[f] is None for f in ('dose_quantity', 'dose_unit', 'route', 'consumed_base_quantity', 'consumption_group_key', 'administration_sequence')), key, 'nonmedication event carries medication fields')

    def check_medications(self):
        allergy_by_pid = defaultdict(list)
        for a in self.t['clinical_condition']:
            if a['condition_type'] == 'ALLERGY':
                allergy_by_pid[self.patient[a['patient_version_id']]['patient_id']].append(a)
        sequences, daily, times = set(), Counter(), defaultdict(list)
        for r in self.t['clinical_event']:
            if not r['catalog_item_id'] or self.catalog[r['catalog_item_id']]['domain'] != 'MEDICATION':
                continue
            key, cat = r['clinical_event_version_id'], self.catalog[r['catalog_item_id']]
            rule = self.policy['medication_constraints'].get(cat['code'])
            self.need(rule is not None and cat['clinical_group'] == rule['ingredient'] and cat['strength_unit'] == rule['unit'] and cat['formulation'] == rule['formulation'] and r['route'] == rule['route'] and r['dose_unit'] == rule['unit'], key, 'unreviewed product/formulation/route/unit')
            e = self.idx['encounter'][r['encounter_version_id']]
            self.need(years(self.patient[e['patient_version_id']]['birth_date'], r['occurred_at'][:10]) >= rule['min_age'], key, 'medication age eligibility')
            if r['event_type'] == 'ORDER':
                self.need(Decimal(r['dose_quantity']) == Decimal(rule['dose']) and r['as_needed'] == rule['as_needed']
                          and Decimal(r['dose_interval_hours']) == rule['interval_hours'] and r['max_doses_per_day'] == rule['max_doses_per_day'], key, 'order dose/schedule exceeds reviewed constraints')
                self.need(r['occurred_at'] <= r['order_start_at'] < r['order_end_at'] and timestamp(r['order_end_at']) - timestamp(r['order_start_at']) <= timedelta(days=rule['max_course_days']), key, 'order course outside configured interval')
                continue
            order = self.events[r['parent_event_version_id']]
            self.need(order['order_start_at'] <= r['occurred_at'] < order['order_end_at'], key, 'administration outside active order')
            self.need(type(r['administration_sequence']) is int and r['administration_sequence'] > 0, key, 'missing administration sequence')
            seq = (order['clinical_event_id'], r['administration_sequence'])
            self.need(seq not in sequences, key, 'duplicate administration sequence')
            sequences.add(seq)
            if r['status'] in ('CANCELLED', 'NOT_DONE'):
                self.need(Decimal(r['consumed_base_quantity']) == 0 and r['consumption_group_key'] is None, key, 'cancelled/not-done service consumes stock')
                continue
            self.need(r['status'] == 'COMPLETED' and r['consumption_group_key'] is not None and Decimal(r['consumed_base_quantity']) > 0, key, 'completed medication lacks consumption')
            expected = (Decimal(r['dose_quantity']) / Decimal(cat['strength_per_base_unit'])).quantize(Decimal('0.000001'))
            self.need(Decimal(r['consumed_base_quantity']) == expected, key, 'strength/base-unit conversion does not reconcile')
            pid = self.person(e)
            for a in allergy_by_pid[pid]:
                active = a['status'] == 'ACTIVE' and a['valid_from'] <= r['occurred_at'] and (a['valid_to'] is None or r['occurred_at'] < a['valid_to']) and a['known_from'] <= r['occurred_at'] and (a['known_to'] is None or r['occurred_at'] < a['known_to'])
                self.need(not (active and a['catalog_item_id'] == cat['allergen_catalog_id']), key, 'completed medication conflicts with active recorded allergy')
            if r['event_type'] == 'MED_ADMIN':
                self.need(Decimal(r['dose_quantity']) == Decimal(order['dose_quantity']), key, 'actual dose differs from order')
                local_day = timestamp(r['occurred_at']).astimezone(self.local_zone).date().isoformat()
                daily[order['clinical_event_id'], local_day] += 1
                self.need(daily[order['clinical_event_id'], local_day] <= rule['max_doses_per_day'], key, 'local-day maximum exceeded')
                # Also check any rolling 24h window; local-day maximum alone is insufficient near midnight.
                times[order['clinical_event_id']].append(r)
            elif r['event_type'] == 'MED_DISPENSE':
                self.need(e['encounter_class'] != 'IPD', key, 'ward dispensing double counts administered stock')
                maximum = Decimal(rule['dose']) * rule['max_doses_per_day'] * rule['max_course_days']
                self.need(Decimal(r['dose_quantity']) <= maximum, key, 'take-home quantity exceeds prescribed course')
        for oid, rows in times.items():
            ordered = sorted(rows, key=lambda r: r['occurred_at'])
            rule = self.policy['medication_constraints'][self.catalog[ordered[0]['catalog_item_id']]['code']]
            for i, r in enumerate(ordered):
                if i:
                    self.need(timestamp(r['occurred_at']) - timestamp(ordered[i-1]['occurred_at']) >= timedelta(hours=rule['interval_hours']), r['clinical_event_version_id'], 'doses too close for order schedule')
                in_day = sum(timestamp(r['occurred_at']) - timedelta(hours=24) < timestamp(a['occurred_at']) <= timestamp(r['occurred_at']) for a in ordered)
                self.need(in_day <= rule['max_doses_per_day'], r['clinical_event_version_id'], 'rolling daily maximum exceeded')
        self.metrics['medication_outcomes'] = dict(Counter(r['status'] for r in self.t['clinical_event'] if r['event_type'] in ('MED_ADMIN', 'MED_DISPENSE')))

    def check_trajectories(self):
        bounds = {'OBS-001': (60, 100), 'OBS-004': (35, 180), 'OBS-005': (6, 50), 'OBS-006': (34, 42), 'OBS-007': (40, 180),
                  'OBS-009': (0, 10), 'OBS-015': (0, 5), 'OBS-019': (50, 500), 'LAB-002': (2.5, 6.5), 'LAB-004': (15, 40),
                  'LAB-006': (0.3, 5), 'LAB-007': (50, 500), 'LAB-011': (2, 30), 'LAB-012': (7, 20), 'LAB-022': (0, 1000), 'LAB-024': (0, 250)}
        for r in self.t['clinical_event']:
            if r['event_type'] in ('OBSERVATION', 'LAB_RESULT') and r['numeric_value'] is not None:
                code = self.catalog[r['catalog_item_id']]['code']
                self.need(code in bounds and bounds[code][0] <= Decimal(r['numeric_value']) <= bounds[code][1], r['clinical_event_version_id'], 'measurement outside reviewed synthetic physiological envelope')
                interval = self.policy['measurement_contexts'][code]
                self.need(Decimal(r['reference_low']) == Decimal(interval['low']) and Decimal(r['reference_high']) == Decimal(interval['high']), r['clinical_event_version_id'], 'measurement reference context mismatch')
        primary = {eid: next((r for r in rows if r['diagnosis_rank'] == 1 and r['revision_no'] == 1), None) for eid, rows in self.conditions_by_encounter.items()}
        changes, directions, pathway_counts = Counter(), Counter(), Counter()
        pneumonia_pairs, creatinine_groups = [], defaultdict(list)
        ckd_people = {self.patient[c['patient_version_id']]['patient_id'] for c in self.master['clinical_condition'] if c['condition_type'] == 'PROBLEM' and self.catalog[c['catalog_item_id']]['code'] == 'N189'}
        for eid, e in self.latest.items():
            if e['encounter_class'] != 'IPD': continue
            condition = primary[eid]
            code = self.catalog[condition['catalog_item_id']]['code']
            path = next((n, p) for n, p in self.cfg['pathways'].items() if p['diagnosis'] == code)
            pathway_counts[path[0]] += 1
            age = years(self.patient[e['patient_version_id']]['birth_date'], e['arrival_at'][:10])
            self.need(path[0] != 'COPD' or age >= 40, eid, 'COPD age outside the selected synthetic pathway scope')
            self.need(path[0] != 'ORTHOPEDIC' or age >= 45, eid, 'elective knee replacement outside modeled adult age scope')
            rows = self.events_by_encounter[eid]
            first_labs = {}
            for r in sorted((r for r in rows if r['event_type'] == 'LAB_RESULT'), key=lambda r: r['occurred_at']):
                first_labs.setdefault(self.catalog[r['catalog_item_id']]['code'], Decimal(r['numeric_value']))
            if 'LAB-006' in first_labs:
                creatinine_groups[self.person(e) in ckd_people].append(first_labs['LAB-006'])
            if path[0] == 'PNEUMONIA' and {'LAB-011', 'LAB-024'} <= set(first_labs):
                pneumonia_pairs.append((float(first_labs['LAB-011']), float(first_labs['LAB-024'])))
            if e['discharged_at'] is None:
                continue
            expected = path[1]
            for obs in expected['observations']:
                values = sorted([r for r in rows if r['event_type'] == 'OBSERVATION' and self.catalog[r['catalog_item_id']]['code'] == obs], key=lambda r: r['occurred_at'])
                self.need(len(values) >= 2, eid, 'completed pathway missing observation trajectory')
                if e['disposition'] != 'DEATH':
                    delta = Decimal(values[-1]['numeric_value']) - Decimal(values[0]['numeric_value'])
                    down = obs in ('OBS-007', 'OBS-009', 'OBS-005', 'OBS-006', 'OBS-019', 'OBS-004')
                    changes[obs] += 1
                    directions[obs] += (delta < 0 if down else delta > 0)
            for lab in expected['labs']:
                values = [r for r in rows if r['event_type'] == 'LAB_RESULT' and self.catalog[r['catalog_item_id']]['code'] == lab]
                self.need(len(values) == 2, eid, 'completed pathway missing repeated scalar laboratory evidence')
            procedures = [r for r in rows if r['event_type'] == 'PROCEDURE' and self.catalog[r['catalog_item_id']]['code'] == expected['procedure']]
            self.need(len(procedures) == 1, eid, 'pathway procedure evidence missing')
            if path[0] in ('GENERAL_SURGERY', 'ORTHOPEDIC'):
                specialty = 'General Surgery' if path[0] == 'GENERAL_SURGERY' else 'Orthopedics'
                self.need(self.idx['worker_assignment'][e['attending_assignment_id']]['specialty'] == specialty, eid, 'operative attending specialty mismatch')
                self.need(self.idx['worker_assignment'][procedures[0]['author_assignment_id']]['specialty'] == specialty, eid, 'operative author specialty mismatch')
                day = timestamp(e['arrival_at']).astimezone(self.local_zone)
                first_hour,last_hour=self.policy.get('elective_admission_hours',[7,10])
                self.need(day.weekday() < 5 and first_hour <= day.hour <= last_hour, eid, 'elective admission outside modeled weekday/daytime schedule')
            if expected['medication']:
                self.need(any(r['event_type'] == 'ORDER' and self.catalog[r['catalog_item_id']]['code'] == expected['medication'] for r in rows if r['catalog_item_id']), eid, 'pathway treatment order missing')
                self.need(any(r['event_type'] == 'MED_ADMIN' for r in rows), eid, 'pathway lacks treatment administration or explicit withholding')
        for code, count in changes.items():
            self.need(directions[code] / count >= self.policy['targets']['minimum_recovery_change_share'], code, 'conditional recovery trajectory target missed')
        self.need(set(pathway_counts) == set(self.cfg['pathways']), 'pathways', 'required clinical pathway absent')
        self.metrics['pathway_counts'] = dict(pathway_counts)
        self.metrics['recovery_direction_shares'] = {k: directions[k] / v for k, v in changes.items()}
        count = len(pneumonia_pairs)
        xmean, ymean = (sum(p[i] for p in pneumonia_pairs) / count for i in (0, 1))
        covariance = sum((x-xmean)*(y-ymean) for x, y in pneumonia_pairs)
        variance = (sum((x-xmean)**2 for x, _ in pneumonia_pairs) * sum((y-ymean)**2 for _, y in pneumonia_pairs)) ** .5
        correlation = covariance / variance
        self.need(correlation >= .9, 'pneumonia', 'conditional inflammatory marker correlation target missed')
        renal_gap = sum(creatinine_groups[True]) / len(creatinine_groups[True]) - sum(creatinine_groups[False]) / len(creatinine_groups[False])
        self.need(renal_gap >= Decimal('.4'), 'renal-context', 'known CKD creatinine context is not differentiated')
        self.metrics['pneumonia_marker_correlation'], self.metrics['ckd_creatinine_mean_gap'] = correlation, str(renal_gap.quantize(Decimal('0.000001')))

    def check_documents(self):
        duplicate = defaultdict(Counter)
        types = Counter()
        for r in self.t['clinical_event']:
            if r['event_type'] != 'DOCUMENT': continue
            key, body = r['clinical_event_version_id'], r['text_value']
            context = self.idx['encounter'][r['encounter_version_id']]
            e = self.latest[context['encounter_id']]
            self.need(r['catalog_item_id'] is None and r['document_type'] is not None and body and r['occurred_at'] <= r['document_signed_at'] <= r['known_from'], key, 'document signing/type chronology')
            pid = self.person(e)
            at = r['occurred_at']
            versions = [p for p in self.patient_histories[pid] if contains(p, at, at, availability=False)]
            self.need(len(versions) == 1, key, 'note patient identity snapshot is ambiguous')
            patient = versions[0]
            day = timestamp(at).astimezone(self.local_zone).date().isoformat()
            identity = f"{patient['given_name']} {patient['family_name']}, age {years(patient['birth_date'], day)}."
            self.need(identity in body, key, 'note identity/age contradicts source facts')
            claims = [h + ': ' + identity for h in ('Clinical review', 'Interval assessment', 'Care assessment', 'Patient review', 'Encounter review', 'Assessment update')]
            known_diagnoses = [c for c in self.conditions_by_encounter[e['encounter_id']] if c['revision_no'] == 1 and c['known_from'] <= at]
            self.need(len(known_diagnoses) == 1, key, 'note assessment is not yet known')
            primary = self.catalog[known_diagnoses[0]['catalog_item_id']]
            definitions = {**self.cfg['pathways'], **self.cfg.get('ambulatory_pathways', {})}
            path = next(p for p in definitions.values() if p['diagnosis'] == primary['code'])
            claims += [('Interval follow-up for ' if e['encounter_class'] == 'OPD' else 'Presenting concern: ') + path['symptom'] + '.', 'Working assessment: ' + primary['display'] + '.']
            references = re.findall(r'\(record (clinical_event_[a-f0-9]+)\)', body)
            for ref in references:
                fact = self.by_event_id.get(ref)
                self.need(fact is not None, key, 'note references nonexistent fact')
                fe = self.idx['encounter'][fact['encounter_version_id']]
                self.need(fe['encounter_id'] == e['encounter_id'] and fact['known_from'] <= at and fact['occurred_at'] <= at, key, 'note exposes future or cross-patient fact')
                cat = self.catalog[fact['catalog_item_id']]
                if fact['event_type'] in ('OBSERVATION', 'LAB_RESULT'):
                    claim = f"{cat['display']}: {fact['numeric_value']} {fact['value_unit']} (record {ref})."
                    self.need(claim in body, key, 'note result contradicts structured value')
                    claims.append(claim)
                elif fact['event_type'] == 'PROCEDURE':
                    claim = f"Procedure documented: {cat['display']} (record {ref})."
                    self.need(fact['status'] == 'COMPLETED' and (fact['period_end_at'] is None or fact['period_end_at'] <= at) and claim in body, key, 'note confuses ordered and performed procedure')
                    claims.append(claim)
                else:
                    self.need(f"{cat['clinical_group']} {fact['dose_quantity']} {fact['dose_unit']} " in body, key, 'note medication contradicts structured dose')
                    phrase = 'withheld; recorded allergy requires review' if fact['status'] == 'NOT_DONE' else ('administered' if fact['event_type'] == 'MED_ADMIN' else 'dispensed for take-home use; ingestion is unobserved')
                    self.need(phrase + f' (record {ref}).' in body, key, 'note confuses ordered, administered, withheld or dispensed therapy')
                    claims.append(f"{cat['clinical_group']} {fact['dose_quantity']} {fact['dose_unit']} {phrase} (record {ref}).")
            if r['document_type'] == 'DISCHARGE_SUMMARY':
                self.need(e['discharged_at'] is not None and e['discharged_at'] <= at and f"Observed disposition: {e['disposition']}." in body, key, 'discharge note exposes unobserved outcome')
                claims.append(f"Observed disposition: {e['disposition']}.")
            problems = [c for c in self.problems_by_person[pid] if c['known_from'] <= at]
            if problems:
                claims.append('Previously recorded problems: ' + '; '.join(sorted({self.catalog[c['catalog_item_id']]['display'] for c in problems})) + '.')
            else:
                claims.append('Prior problem documentation is incomplete; absence of a record does not exclude disease.')
            claims += ['Continue assessment as results become available.', 'Reassessment remains appropriate; later outcomes are unknown here.',
                       'The current assessment may change with further evidence.', 'Follow-up completion is not established by this document.']
            remainder = body
            for claim in sorted(claims, key=len, reverse=True): remainder = remainder.replace(claim, '')
            self.need(not remainder.strip(), key, 'note contains unsupported or contradictory narrative claims')
            self.need('Follow-up completion is not established by this document.' in body, key, 'follow-up uncertainty lost')
            self.need(not any(token in body.lower() for token in ('readmitted on', 'will recover', 'claim paid', 'no known allergies', 'no evidence of disease')), key, 'unsupported negative or future outcome in prose')
            # Remove identifying/time/source keys before computing duplicate bodies; scalar clinical values remain.
            normalized = re.sub(r'clinical_event_[a-f0-9]+', 'FACT', body)
            normalized = normalized.replace(patient['given_name'] + ' ' + patient['family_name'], 'PERSON')
            normalized = re.sub(r'age \d+', 'age AGE', normalized).lower()
            duplicate[r['document_type']][normalized] += 1
            types[r['document_type']] += 1
        shares = {kind: sum(n-1 for n in counts.values()) / types[kind] for kind, counts in duplicate.items()}
        self.need(all(v <= self.policy['targets']['maximum_normalized_note_duplicate_share'] for v in shares.values()), 'documents', 'normalized note duplicate share exceeds target')
        self.metrics['document_counts'], self.metrics['normalized_note_duplicate_shares'] = dict(types), shares

    @property
    def patient_histories(self):
        if not hasattr(self, '_ph'): self._ph = grouped(self.t['patient'], 'patient_id')
        return self._ph

    @property
    def local_zone(self):
        if not hasattr(self, 'zone'):
            from importlib import resources
            from io import BytesIO
            from zoneinfo import ZoneInfo
            self.zone = ZoneInfo.from_file(BytesIO(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()))
        return self.zone

    @property
    def problems_by_person(self):
        if not hasattr(self, '_pbp'):
            self._pbp = defaultdict(list)
            for c in self.t['clinical_condition']:
                if c['condition_type'] == 'PROBLEM': self._pbp[self.patient[c['patient_version_id']]['patient_id']].append(c)
        return self._pbp

    @property
    def by_event_id(self):
        if not hasattr(self, '_be'): self._be = {r['clinical_event_id']: r for r in self.t['clinical_event']}
        return self._be

    def check_longitudinal(self):
        active = {pid: [e for e in visits if e['arrival_at'] >= self.start or e['carry_in']] for pid, visits in self.by_person.items()}
        repeats = sum(len(visits) >= 2 for visits in active.values()) / len(active)
        ipd = [e for e in self.latest.values() if e['encounter_class'] == 'IPD']
        completed = [e for e in ipd if e['discharged_at']]
        durations = [(timestamp(e['discharged_at']) - timestamp(e['arrival_at'])).total_seconds() / 86400 for e in completed]
        mean, tail = sum(durations) / len(durations), sum(d > 10 for d in durations) / len(durations)
        eligible, readmit, censored = 0, 0, 0
        for e in completed:
            if e['disposition'] != 'HOME': continue
            follow_end = timestamp(e['discharged_at']) + timedelta(days=30)
            if follow_end >= timestamp(self.cutoff):
                censored += 1
                continue
            eligible += 1
            returns = [r for r in self.by_person[self.person(e)] if r['encounter_class'] == 'IPD' and not r['planned'] and e['discharged_at'] < r['arrival_at'] <= follow_end.isoformat().replace('+00:00', 'Z') and r['episode_id'] != e['episode_id']]
            readmit += bool(returns)
        metrics = {'ipd_mean_days': mean, 'ipd_long_stay_share': tail, 'repeat_patient_share': repeats, 'readmission_share': readmit / eligible}
        for key, value in metrics.items():
            lo, hi = self.policy['targets'][key]
            self.need(lo <= value <= hi, key, f'predeclared longitudinal target missed: {value}')
        self.need(censored > 0 and len(self.deaths) == self.cfg['cohort']['death_outcomes'], 'boundaries', 'censored or terminal histories absent')
        self.metrics.update(metrics, readmission_numerator=readmit, readmission_eligible_denominator=eligible, readmission_censored_discharges=censored)
        diagnoses = {eid: next((c for c in rows if c['revision_no'] == 1 and c['diagnosis_rank'] == 1), None) for eid, rows in self.conditions_by_encounter.items()}
        repeated_diagnoses = []
        for pid, visits in active.items():
            outpatient = [e for e in visits if e['encounter_class'] != 'IPD' and e['encounter_id'] in diagnoses]
            if len(outpatient) >= 2:
                codes = {self.catalog[diagnoses[e['encounter_id']]['catalog_item_id']]['code'] for e in outpatient}
                repeated_diagnoses.append(len(codes) >= 2)
        varied_share = sum(repeated_diagnoses) / len(repeated_diagnoses)
        self.need(varied_share >= float(self.policy['targets']['minimum_repeat_complaint_variation_share']), 'repeated-visits', 'episodic complaints are unrealistically fixed per person')
        ipd_episodes = {e['episode_id'] for e in ipd}
        for eid, e in self.latest.items():
            if e['arrival_at'] < self.start or e['encounter_class'] == 'IPD' or e['episode_id'] in ipd_episodes or eid not in diagnoses:
                continue
            code = self.catalog[diagnoses[eid]['catalog_item_id']]['code']
            if code in ('I509', 'J449', 'E119'):
                known = [p for p in self.problems_by_person[self.person(e)] if p['known_from'] <= e['arrival_at'] and self.catalog[p['catalog_item_id']]['code'] == code]
                self.need(bool(known), eid, 'chronic follow-up uses unknown or future problem history')
        self.metrics['repeat_complaint_variation_share'] = varied_share
        self.metrics['laboratory_results_known_after_discharge'] = sum(r['event_type'] == 'LAB_RESULT' and self.latest[self.idx['encounter'][r['encounter_version_id']]['encounter_id']]['discharged_at'] is not None and r['known_from'] > self.latest[self.idx['encounter'][r['encounter_version_id']]['encounter_id']]['discharged_at'] for r in self.t['clinical_event'])

    def check_budget(self):
        allowed = set(self.master) | set(self.policy['new_business_tables'])
        self.need(set(self.t) == allowed and len(self.spec) == 25, 'tables', 'unregistered business table')
        for table, rows in self.t.items():
            self.need(len(rows) <= self.spec[table]['planned_rows'], table, 'table record budget exceeded')
            self.need(not any(isinstance(v, (list, dict)) for r in rows for v in r.values()), table, 'nested uncounted clinical facts')
        total = sum(map(len, self.t.values()))
        self.need(total <= min(self.policy['business_cap'], self.policy['hard_cap']), 'budget', 'total canonical cap exceeded')
        self.metrics['business_rows'] = total
        self.metrics['remaining_planned_rows'] = self.policy['business_cap'] - total
        self.metrics['clinical_event_families'] = dict(Counter(r['event_type'] for r in self.t['clinical_event']))
