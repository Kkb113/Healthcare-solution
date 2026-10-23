"""Calendar-conditioned clinical generation; no independent random fact tables."""
from __future__ import annotations

import bisect
import math
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from .clinical_generation import ClinicalGenerator, START, CUTOFF, source_version, stamp
from .core import instant, stable_id, age_on


class DemandGenerator(ClinicalGenerator):
    def __init__(self, tables, cfg, policy, run_id, operational):
        super().__init__(tables, cfg, policy, run_id)
        self.ops, self.calendars, self.paths = operational, {}, {}
        people = sorted(self.patients, key=lambda p: (self.patients[p][0]['birth_date'] > '2000-01-01', stable_id('clinical-cohort', self.seed, p)))
        multi, singles = people[:12000], people[12000:]
        self.carry_sites = {p: i % 3 for i, p in enumerate(multi[:57])}
        assignments = [('ED', p) for p in singles[:4000]] + [('OPD', p) for p in singles[4000:]]
        assignments += [('OPD', p) for p in multi[10680:]] * 2
        assignments += [('ED', multi[super(DemandGenerator, self).n(str(i), 'ed-person', 12000)]) for i in range(17000)]
        assignments += [('OPD', multi[super(DemandGenerator, self).n(str(i), 'op-person', 12000)]) for i in range(10360)]
        self.visits = dict(enumerate(assignments))
        self.visit_days = {}

    def site(self, pid):
        return self.carry_sites.get(pid, super().n(pid, 'home-hospital', 3))

    def index(self, day, site):
        shift = (0, 9, -12)[site]
        seasonal = 1 + float(self.ops['seasonal_amplitude']) * math.cos(2 * math.pi * (day.timetuple().tm_yday - 15 - shift) / 365.25)
        surge = self.ops['surge_start'] <= day.isoformat() < self.ops['surge_end']
        return seasonal, surge

    def calendar_day(self, entity, stream, upper, site, respiratory=False):
        key = stream, upper, site, respiratory
        if key not in self.calendars:
            cumulative, total = [], 0
            offset = 4 if stream == 'ipd-day' else 2
            for d in range(upper):
                day = START.date() + timedelta(days=d + offset)
                season, surge = self.index(day, site)
                weight = season * (1 + float(self.ops['annual_growth']) * (day.year - 2023))
                # Both rates and case mix respond; elective schedules remain weekday daytime.
                if surge: weight *= 2.4 if respiratory else 1.04
                if day.weekday() == 0: weight *= 1.08
                weight *= .94 + super().n(f'{site}/{day}', 'daily-demand-noise', 13) / 100
                total += max(1, round(weight * 100000))
                cumulative.append(total)
            self.calendars[key] = cumulative, total
        cumulative, total = self.calendars[key]
        return bisect.bisect_right(cumulative, super().n(entity, stream + '-weighted', total))

    def pathway(self, pid, elective=False):
        result = super().pathway(pid, elective)
        self.paths[pid] = result
        return result

    def n(self, entity, stream, upper):
        if stream=='terminal-arrival':return super().n(entity,'terminal-december-arrival',216)
        if stream=='open-hours':return super().n(entity,'boundary-december-arrival',288)
        if stream == 'home-hospital': return self.site(entity)
        if stream == 'ipd-day':
            return self.calendar_day(entity, stream, upper, self.site(entity), self.paths.get(entity) in ('PNEUMONIA', 'COPD'))
        if stream == 'visit-day':
            kind, pid = self.visits[int(entity)]
            result = self.calendar_day(entity, stream, upper, self.site(pid))
            self.visit_days[entity] = (START.date() + timedelta(days=result + 2)).isoformat()
            return result
        if stream in ('emergency-hour', 'ipd-hour'):
            weights = [2]*6 + [3]*3 + [5]*4 + [7]*8 + [4]*3
            k = super().n(entity, stream + '-weighted', sum(weights))
            for hour, weight in enumerate(weights):
                if k < weight: return hour
                k -= weight
        if stream == 'episodic-complaint' and self.ops['surge_start'] <= self.visit_days.get(entity, '') < self.ops['surge_end']:
            k = super().n(entity, stream, upper)
            return 96 + k % 4 if k < 35 else k
        return super().n(entity, stream, upper)

    def drivers(self):
        rows = []
        for fid in self.facilities:
            site = self.facilities.index(fid)
            for d in range(1096):
                day = date(2023, 1, 1) + timedelta(days=d)
                seasonal, surge = self.index(day, site)
                # Observed daily index has seeded local variation, distinct from calendar publication.
                resp = Decimal(str(seasonal * (1.8 if surge else 1))) + Decimal(self.n(f'{fid}/{day}', 'resp-noise', 15) - 7) / 100
                local_end = datetime.combine(day + timedelta(days=1), time(), self.zone)
                known = (local_end + timedelta(hours=6)).astimezone(timezone.utc)
                key = stable_id('facility_day', fid, day.isoformat())
                rows.append(self.row('facility_day_driver', key, known, facility_day_id=key, facility_id=fid,
                    calendar_date=day.isoformat(), day_of_week=day.isoweekday(), holiday=(day.month, day.day) in ((1,1),(7,4),(12,25)),
                    season=('WINTER' if day.month in (12,1,2) else 'SPRING' if day.month in (3,4,5) else 'SUMMER' if day.month in (6,7,8) else 'FALL'),
                    respiratory_index=str(resp.quantize(Decimal('.000001'))),
                    weather_index=str((Decimal(self.n(f'{fid}/{day}', 'weather', 80)) / 100 + (Decimal('.7') if day.isoformat() in ('2024-01-13','2024-01-14','2024-01-15') else 0)).quantize(Decimal('.000001'))),
                    calendar_known_at='2022-12-01T06:00:00Z', observations_known_at=stamp(known), calendar_source='SYNTHETIC_FIXED_DATE_CALENDAR_PARTIAL_HOLIDAYS'))
        return {'facility_day_driver': rows}

    def triage(self):
        rows = []
        for e in self.t['encounter']:
            if e['revision_no'] != 1 or e['encounter_class'] != 'ED': continue
            at = instant(e['arrival_at']) + timedelta(minutes=5)
            if at >= CUTOFF: continue
            cat = self.code('OBSERVATION', 'OBS-001', at)
            key = e['encounter_id'] + '/triage-saturation'
            value = str(93 + self.n(key, 'triage-saturation', 7))
            rows.append(self.row('clinical_event', key, at, clinical_event_version_id=stable_id('clinical_event_version', key, 1),
                clinical_event_id=stable_id('clinical_event', key), encounter_version_id=e['encounter_version_id'],
                catalog_item_id=cat['catalog_item_id'], author_assignment_id=self.clinician(e['facility_id'], at, 'Emergency Medicine'),
                event_type='OBSERVATION', occurred_at=stamp(at), status='COMPLETED', numeric_value=value,
                value_unit=cat['base_unit'], reference_low='95', reference_high='100', aggregation='POINT',
                revision_no=1, known_from=stamp(at), known_to=None))
        return {'clinical_event': rows}

    def adverse_outcome(self, encounter):
        # A transfer disposition is not itself a clinical deterioration label.
        return encounter['disposition']=='DEATH' or (encounter['encounter_class']=='IPD' and encounter['disposition']=='TRANSFER'
            and not encounter['planned'] and self.n(encounter['encounter_id'],'clinical-nonresponse',100)<3)

    def placement_assessments(self):
        rows=[];enc={r['encounter_version_id']:r for r in self.t['encounter']}
        admissions={r['encounter_id']:r for r in self.t['encounter'] if r['revision_no']==2 and r['encounter_class']=='IPD'}
        for c in self.t['clinical_condition']:
            if not c['encounter_version_id'] or c['revision_no']!=1 or c['diagnosis_rank']!=1:continue
            e=enc[c['encounter_version_id']];eid=e['encounter_id']
            if e['encounter_class']!='IPD' or self.by_catalog[c['catalog_item_id']]['code']!='J189' or self.n(eid,'suspected-communicable-risk',100)>=20:continue
            at=instant(e['arrival_at'])+timedelta(minutes=15)
            patient=source_version(self.patients[self.by_patient_version[e['patient_version_id']]['patient_id']],at)
            body=f"Placement assessment for {patient['given_name']} {patient['family_name']}, age {age_on(patient['birth_date'],at.astimezone(self.zone).date().isoformat())}: suspected transmissible respiratory illness; isolation-capable private room requested. Recorded at {stamp(at)}."
            key=eid+'/placement-assessment'
            context=admissions[eid]
            rows.append(self.row('clinical_event',key,at,clinical_event_version_id=stable_id('clinical_event_version',key,1),clinical_event_id=stable_id('clinical_event',key),
                encounter_version_id=context['encounter_version_id'],author_assignment_id=self.clinician(e['facility_id'],at,'Internal Medicine'),event_type='DOCUMENT',
                occurred_at=stamp(at),document_signed_at=stamp(at),document_type='PROGRESS_NOTE',text_value=body,status='COMPLETED',aggregation='NOT_APPLICABLE',revision_no=1,known_from=stamp(at),known_to=None))
        latest={}
        for e in self.t['encounter']:
            if e['encounter_id'] not in latest or e['revision_no']>latest[e['encounter_id']]['revision_no']:latest[e['encounter_id']]=e
        codes={r['facility_id']:r['facility_code'] for r in self.t['facility']}
        for e in sorted(latest.values(),key=lambda r:r['encounter_id']):
            if e['admission_source']!='TRANSFER':continue
            sender=enc[e['previous_encounter_version_id']]
            for context in (sender,e):
                eid=context['encounter_id'];at=instant(context['admitted_at']);key=eid+'/transfer-referral'
                body=f"Transfer coordination for encounter {eid}: continuation at {codes[e['facility_id']]} is accepted within the modeled network. Capacity escalation remains within that referral; actual handoff time is not yet established."
                if context['admission_source']=='TRANSFER':body=f"Transfer coordination for encounter {eid}: accepted continuation at {codes[e['facility_id']]}; receiving arrival is observed at {context['arrival_at']}. Later care outcome is not yet established."
                rows.append(self.row('clinical_event',key,at,clinical_event_version_id=stable_id('clinical_event_version',key,1),clinical_event_id=stable_id('clinical_event',key),
                    encounter_version_id=admissions[eid]['encounter_version_id'],author_assignment_id=self.clinician(context['facility_id'],at,'Internal Medicine'),event_type='DOCUMENT',occurred_at=stamp(at),
                    document_signed_at=stamp(at),document_type='PROGRESS_NOTE',text_value=body,status='COMPLETED',aggregation='NOT_APPLICABLE',revision_no=1,known_from=stamp(at),known_to=None))
        return {'clinical_event':rows}
