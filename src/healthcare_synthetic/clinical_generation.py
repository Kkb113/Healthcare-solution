"""Counted, full-schema adult clinical histories; provisional before resource integration."""
from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal

from .core import age_on, chicago, draw, instant, stable_id
from .master_generation import MasterGenerator
from .trajectory_scheduling import patient_slot

START = datetime(2023, 1, 1, 6, tzinfo=timezone.utc)
CUTOFF = datetime(2026, 1, 1, 6, tzinfo=timezone.utc)


def stamp(value):
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def source_version(rows, at):
    """Resolve source knowledge, separately from subsequent extract delivery latency."""
    when = stamp(at) if isinstance(at, datetime) else at
    found = [r for r in rows if r['valid_from'] <= when and (r['valid_to'] is None or when < r['valid_to'])
             and r['known_from'] <= when and (r['known_to'] is None or when < r['known_to'])]
    if len(found) != 1:
        raise ValueError(f"ambiguous or absent source snapshot: {when}")
    return found[0]


class ClinicalGenerator:
    def __init__(self, tables, cfg, policy, run_id):
        self.t, self.cfg, self.policy, self.run_id = tables, cfg, policy, run_id
        self.seed = cfg['seed']
        self.pathdefs = {**cfg['pathways'], **cfg.get('ambulatory_pathways', {})}
        self.zone = chicago()
        self.author_cache = {}
        self.builder = MasterGenerator({'seed': self.seed}, {}, run_id)
        self.patients, self.coverage, self.workers, self.catalog = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
        self.by_patient_version = {p['patient_version_id']: p for p in tables['patient']}
        self.by_catalog = {r['catalog_item_id']: r for r in tables['catalog_item']}
        for r in tables['patient']:
            self.patients[r['patient_id']].append(r)
        for r in tables['patient_coverage']:
            self.coverage[self.by_patient_version[r['patient_version_id']]['patient_id']].append(r)
        for r in tables['worker_assignment']:
            if r['role'] == 'PHYSICIAN':
                self.workers[r['facility_id']].append(r)
        for r in tables['catalog_item']:
            self.catalog[r['domain'], r['code']].append(r)
        self.facilities = sorted(r['facility_id'] for r in tables['facility'])
        self.locations = {(r['facility_id'], r['location_code']): r['location_id'] for r in tables['location']}
        self.opening = defaultdict(list)
        for r in tables['clinical_condition']:
            if r['encounter_version_id'] is None:
                self.opening[self.by_patient_version[r['patient_version_id']]['patient_id']].append(r)

    def n(self, entity, stream, upper):
        return draw(self.seed, entity, stream, upper=upper)

    def code(self, domain, code, when):
        day = when.astimezone(self.zone).date().isoformat()
        return next(r for r in self.catalog[domain, code] if r['valid_from'] <= day and (r['valid_to'] is None or day < r['valid_to']))

    def row(self, table, key, at, **fields):
        row = self.builder.row(table, key, stamp(at), **fields)
        row['export_available_at'] = stamp(at + timedelta(hours=2))
        return row

    def clinician(self, fid, at, specialty=None):
        when, day = stamp(at), at.astimezone(self.zone).date().isoformat()
        cache_key = fid, when[:13], specialty
        if cache_key in self.author_cache:
            return self.author_cache[cache_key]
        rows = [r for r in self.workers[fid] if r['valid_from'] <= when and (r['valid_to'] is None or when < r['valid_to'])
                and r['known_from'] <= when and (r['known_to'] is None or when < r['known_to'])
                and r['hire_date'] <= day and (r['termination_date'] is None or day < r['termination_date'])
                and r['credential_valid_from'] <= day < r['credential_valid_to'] and (specialty is None or r['specialty'] == specialty)]
        if not rows:
            raise ValueError('no credentialed source clinician')
        selected = sorted(rows, key=lambda r: r['worker_assignment_id'])[self.n(fid + day + (specialty or ''), 'clinician', len(rows))]['worker_assignment_id']
        self.author_cache[cache_key] = selected
        return selected

    def pathway(self, pid, elective=False):
        choices = self.cfg['pathways']
        names = ['GENERAL_SURGERY', 'ORTHOPEDIC'] if elective else ['HEART_FAILURE', 'COPD', 'PNEUMONIA', 'GENERAL_MEDICINE']
        age = age_on(self.patients[pid][0]['birth_date'], '2023-01-01')
        prior = {self.by_catalog[r['catalog_item_id']]['code'] for r in self.opening[pid] if r['condition_type'] == 'PROBLEM'}
        weights = [choices[n]['weight'] + (12 if choices[n]['diagnosis'] in prior else 0) for n in names]
        if elective:
            weights = [30, 0 if age < 45 else 18]
        elif age < 40:
            weights = [1, 0, 25, 14]
        k = self.n(pid, 'clinical-pathway', sum(weights))
        for name, weight in zip(names, weights):
            if k < weight:
                return name
            k -= weight

    def duration(self, eid, pathway, readmit=False):
        # Explicit skewed mixture: central variable stay plus a 5% long-stay component.
        mean = Decimal(self.cfg['pathways'][pathway]['mean_days'])
        if self.n(eid, 'tail', 100) < 5:
            return timedelta(hours=252 + self.n(eid, 'tail-hours', 150))
        hours = int(mean * 24) - 18 + self.n(eid, 'los-a', 31) + self.n(eid, 'los-b', 25) - 22
        return timedelta(hours=max(36, hours + (18 if readmit else 0)))

    def weekday_slot(self, begin, key):
        """Move a weekend draw to a seeded weekday instead of piling every one onto Monday."""
        weekday = begin.astimezone(self.zone).weekday()
        if weekday < 5:
            return begin
        target = self.n(key, 'weekday-remap', 5)
        forward = begin + timedelta(days=7 - weekday + target)
        return forward if forward < CUTOFF - timedelta(days=3) else begin - timedelta(days=weekday - target)

    def booking_lead(self, key, tail):
        """Booking lead in days: most within two weeks, with a longer tail of advance bookings."""
        lead = 2 + self.n(key, 'booking-lead', 14)
        if self.n(key, 'booking-lead-tail', 100) < tail:
            lead += self.n(key, 'booking-lead-extra', 31)
        return lead

    def ed_duration(self, key, admitted):
        """Right-skewed ED time; admitted visits include decision and inpatient handover."""
        if admitted:
            minutes = 150 + self.n(key, 'ed-admit-a', 181) + self.n(key, 'ed-admit-b', 181)
            if self.n(key, 'ed-admit-tail', 100) < 8:
                minutes += 120 + self.n(key, 'ed-admit-tail-minutes', 481)
        else:
            minutes = 55 + self.n(key, 'ed-visit-a', 121) + self.n(key, 'ed-visit-b', 121)
            if self.n(key, 'ed-visit-tail', 100) < 6:
                minutes += 60 + self.n(key, 'ed-visit-tail-minutes', 301)
        return timedelta(minutes=minutes)

    def discharge_window(self, eid, at):
        """Home discharges complete in the daytime; later completions wait for the next morning."""
        local = at.astimezone(self.zone)
        if 9 <= local.hour < 20:
            return at
        day = local.date() if local.hour < 9 else local.date() + timedelta(days=1)
        return (datetime.combine(day, time(9, 30), self.zone) + timedelta(minutes=self.n(eid, 'overnight-hold', 151))).astimezone(timezone.utc)

    def discharge_plan(self, eid, begin, nominal):
        """Readiness is declared on ward rounds; discharge follows medication, transport and paperwork."""
        day = nominal.astimezone(self.zone).date()
        if day.weekday() >= 5 and self.n(eid, 'weekend-readiness', 100) < 35:
            day += timedelta(days=7 - day.weekday()) if self.n(eid, 'weekend-readiness-side', 2) else -timedelta(days=day.weekday() - 4)
        ready = (datetime.combine(day, time(8), self.zone) + timedelta(minutes=self.n(eid, 'ready-minutes', 181))).astimezone(timezone.utc)
        if ready < begin + timedelta(hours=20):
            ready = nominal
        delay = 45 + self.n(eid, 'discharge-delay-a', 151) + self.n(eid, 'discharge-delay-b', 151)
        if self.n(eid, 'discharge-delay-tail', 100) < 12:
            delay += 120 + self.n(eid, 'discharge-delay-tail-minutes', 361)
        return ready, self.discharge_window(eid, ready + timedelta(minutes=delay))

    def journeys(self):
        cohort = self.cfg['cohort']
        # Only older adults can contribute the December 2022 opening contexts.
        people = sorted(self.patients, key=lambda p: (self.patients[p][0]['birth_date'] > '2000-01-01', stable_id('clinical-cohort', self.seed, p)))
        multi, singles = people[:12000], people[12000:]
        plans, busy, plans_by_person = [], defaultdict(list), defaultdict(list)
        terminal_people = set(multi[cohort['inpatient_people'] - cohort['death_outcomes']:cohort['inpatient_people']])

        def add(pid, identity, kind, begin, duration, path, route='WALK_IN', previous=None, episode=None, carry=False, opening=False, readmit=False, death=False):
            end = begin + duration
            if not carry and not opening:
                original = begin
                ordinary_visit = kind in ('ED','OPD') and identity.startswith(kind+'/')
                begin = patient_slot(begin,duration,busy[pid],START,CUTOFF,allow_backwards=ordinary_visit,
                                     fallback_weekday_zone=self.zone if kind=='OPD' else None)
                end = begin+duration
                if begin < original and path in ('HEART_FAILURE','COPD','GENERAL_MEDICINE'):
                    # Earlier placement cannot inherit a problem assertion that
                    # only becomes known at the later inpatient presentation.
                    code = self.cfg['pathways'][path]['diagnosis']
                    opening_known = any(c['condition_type']=='PROBLEM' and c['known_from']<=stamp(begin)
                                        and self.by_catalog[c['catalog_item_id']]['code']==code for c in self.opening[pid])
                    prior_known = any(p['kind']=='IPD' and p['path']==path and p['begin']+timedelta(minutes=25)<begin for p in plans_by_person[pid])
                    if not opening_known and not prior_known:
                        path = 'CHEST_PAIN' if self.n(identity,'free-slot-episodic-assessment',2)==0 else 'ABDOMINAL_PAIN'
            busy[pid].append((begin, end))
            eid = stable_id('encounter', identity)
            fid = self.facilities[self.n(pid, 'home-hospital', 3)]
            plans.append(dict(pid=pid, eid=eid, kind=kind, begin=begin, end=end, path=path, route=route, previous=previous,
                              episode=episode or stable_id('episode', eid), carry=carry, opening=opening, readmit=readmit, death=death, fid=fid))
            plans_by_person[pid].append(plans[-1])
            return plans[-1]

        for i, pid in enumerate(multi[:cohort['inpatient_people']]):
            carry = i < cohort['carry_in']
            elective = cohort['carry_in'] <= i < cohort['carry_in'] + cohort['elective']
            route = 'DIRECT' if carry else ('ELECTIVE' if elective else ('ED' if i < cohort['carry_in'] + cohort['elective'] + 4680 else 'DIRECT'))
            path = self.pathway(pid, elective)
            eid = stable_id('encounter', f'IPD/{pid}')
            readmission_index = cohort['carry_in'] + cohort['elective'] <= i < cohort['carry_in'] + cohort['elective'] + cohort['readmissions']
            begin = START + timedelta(days=4 + self.n(pid, 'ipd-day', 1020 if readmission_index else 1087), hours=self.n(pid, 'ipd-hour', 24), minutes=self.n(pid, 'ipd-minute', 60))
            if elective:
                begin = self.weekday_slot(begin.replace(hour=13 + self.n(pid, 'elective-admission-hour', 3)), pid)
            duration = self.duration(eid, path)
            death = cohort['inpatient_people'] - cohort['death_outcomes'] <= i
            if death and path == 'GENERAL_MEDICINE':
                path = 'PNEUMONIA'
            if carry:
                begin = START - timedelta(hours=12 + self.n(pid, 'carry-hours', 100))
                duration = timedelta(days=7, hours=self.n(pid, 'carry-los', 96))
            elif death:
                begin = CUTOFF - timedelta(hours=45 + self.n(pid, 'terminal-arrival', 20))
                duration = timedelta(hours=24 + self.n(pid, 'terminal-los', 16))
            elif i >= cohort['inpatient_people'] - 80:
                begin = CUTOFF - timedelta(hours=2 + self.n(pid, 'open-hours', 36))
            gap = None
            if not death and i < cohort['inpatient_people'] - 80:
                ready, discharge = self.discharge_plan(eid, begin, begin + duration)
                duration, gap = discharge - begin, discharge - ready
            ip = add(pid, f'IPD/{pid}', 'IPD', begin, duration, path, route, carry=carry, death=death)
            ip['ready_gap'] = gap
            if route == 'ED':
                stay = self.ed_duration(f'ED-ADMIT/{pid}', True)
                ed = add(pid, f'ED-ADMIT/{pid}', 'ED', begin - stay, stay, path, episode=ip['episode'])
                ip['previous'] = ed['eid']
            if readmission_index:
                # Acute unplanned return is a new episode, with explicit preceding live discharge.
                rid = stable_id('encounter', f'RETURN/{pid}')
                rbegin = ip['end'] + timedelta(days=8 + self.n(pid, 'return-gap', 18))
                ready, discharge = self.discharge_plan(rid, rbegin, rbegin + self.duration(rid, path, True))
                back = add(pid, f'RETURN/{pid}', 'IPD', rbegin, discharge - rbegin, path, 'ED', previous=ip['eid'], readmit=True)
                back['ready_gap'] = discharge - ready
                stay = self.ed_duration(f'RETURN-ED/{pid}', True)
                ed = add(pid, f'RETURN-ED/{pid}', 'ED', back['begin'] - stay, stay, path, previous=ip['eid'], episode=back['episode'])
                back['previous'] = ed['eid']

        # 4,680 initial ED arrivals + 1,320 returning ED arrivals = 6,000 admissions.
        free_ed = cohort['emergency'] - cohort['ed_to_inpatient']
        free_op = cohort['outpatient']
        assignments = [('ED', p) for p in singles[:4000]] + [('OPD', p) for p in singles[4000:]]
        assignments += [('OPD', p) for p in multi[cohort['inpatient_people']:]] * 2
        free_ed -= 4000
        free_op -= 4000 + 2 * (12000 - cohort['inpatient_people'])
        assignments += [('ED', multi[self.n(str(i), 'ed-person', len(multi))]) for i in range(free_ed)]
        assignments += [('OPD', multi[self.n(str(i), 'op-person', len(multi))]) for i in range(free_op)]
        for i, (kind, pid) in enumerate(assignments):
            hour = (8 + self.n(str(i), 'office-hour', 8)) if kind == 'OPD' else self.n(str(i), 'emergency-hour', 24)
            day = 2 + self.n(str(i), 'visit-day', 1060 if pid in terminal_people else 1092)
            begin = START + timedelta(days=day, hours=hour, minutes=self.n(str(i), 'visit-minute', 60))
            if kind == 'OPD':
                begin = self.weekday_slot(begin, str(i))
            # Chronic follow-up uses only opening assertions or an already-started earlier admission.
            # Other visits have episodic symptoms; a person is not assigned one acute diagnosis forever.
            prior_codes = {self.by_catalog[c['catalog_item_id']]['code'] for c in self.opening[pid] if c['condition_type'] == 'PROBLEM' and c['known_from'] <= stamp(begin)}
            chronic = [name for name in ('HEART_FAILURE', 'COPD', 'GENERAL_MEDICINE') if self.cfg['pathways'][name]['diagnosis'] in prior_codes]
            chronic += [p['path'] for p in plans_by_person[pid] if p['kind'] == 'IPD' and p['begin'] + timedelta(minutes=25) < begin and p['path'] in ('HEART_FAILURE', 'COPD', 'GENERAL_MEDICINE')]
            chronic = sorted(set(chronic))
            if age_on(self.patients[pid][0]['birth_date'], '2023-01-01') < 40:
                chronic = [name for name in chronic if name != 'COPD']
            if chronic and self.n(str(i), 'chronic-followup', 100) < 65:
                path = chronic[self.n(str(i), 'known-problem-selection', len(chronic))]
            else:
                choice = self.n(str(i), 'episodic-complaint', 100)
                path = 'CHEST_PAIN' if choice < 50 else ('ABDOMINAL_PAIN' if choice < 96 else 'PNEUMONIA')
            # Mild same-day episodes have shorter, varied observation and assessment periods.
            length = timedelta(minutes=35 + self.n(str(i), 'visit-length', 80)) if kind == 'OPD' else self.ed_duration(str(i), False)
            add(pid, f'{kind}/{i}/{pid}', kind, begin, length, path)
        for i, pid in enumerate(people[:cohort['opening_only']]):
            add(pid, f'OPENING/{pid}', 'OPD', START - timedelta(days=5 + self.n(pid, 'opening-day', 9)), timedelta(hours=2), self.pathway(pid), opening=True)

        encounters, conditions, last, encounter_histories = [], [], {}, {}
        ipd_episodes = {x['episode'] for x in plans if x['kind'] == 'IPD'}
        for p in sorted(plans, key=lambda p: (p['begin'], p['eid'])):
            begin, end, eid, pid = p['begin'], p['end'], p['eid'], p['pid']
            patient = source_version(self.patients[pid], begin)
            coverage = source_version(self.coverage[pid], begin)
            unit = 'MED' if p['kind'] == 'IPD' else ('ED' if p['kind'] == 'ED' else 'AMB')
            if p['kind'] == 'IPD' and p['path'] in ('GENERAL_SURGERY', 'ORTHOPEDIC'):
                unit = 'SURG'
            # Explicit visits precede linked follow-up without merging unrelated episodes.
            previous = p['previous'] or last.get(pid)
            previous_version = stable_id('encounter_version', previous, 1) if previous else None
            # Link a predecessor revision already known at arrival (including the ED closing row).
            if previous:
                prior = [r for r in encounter_histories[previous] if r['known_from'] <= stamp(begin)]
                previous_version = max(prior, key=lambda r: r['revision_no'])['encounter_version_id']
            acuity = (2 if p['readmit'] else 2 + self.n(eid, 'acuity', 2)) if p['kind'] == 'IPD' else 3 + self.n(eid, 'acuity', 3)
            if p['death']:
                acuity = 1 + self.n(eid, 'critical-acuity', 2)
            elif p['kind'] == 'ED' and p['episode'] in ipd_episodes:
                acuity = 2 + self.n(eid, 'admitted-triage-acuity', 2)
            base = dict(encounter_id=eid, episode_id=p['episode'], previous_encounter_version_id=previous_version,
                        patient_version_id=patient['patient_version_id'], facility_id=p['fid'], location_id=self.locations[p['fid'], unit],
                        coverage_version_id=coverage['coverage_version_id'], attending_assignment_id=self.clinician(p['fid'], begin, 'Emergency Medicine' if p['kind'] == 'ED' else ('General Surgery' if p['path'] == 'GENERAL_SURGERY' else 'Orthopedics' if p['path'] == 'ORTHOPEDIC' else 'Internal Medicine')),
                        encounter_class=p['kind'], admission_source=p['route'], initial_acuity=acuity, arrival_at=stamp(begin),
                        disposition='OPEN', planned=p['route'] == 'ELECTIVE' or (p['kind'] == 'OPD' and not p['opening']), carry_in=p['carry'])
            changes = [(begin, {})]
            if p['kind'] == 'IPD':
                changes.append((begin + timedelta(minutes=15), dict(admission_decision_at=stamp(begin), admitted_at=stamp(begin + timedelta(minutes=15)))))
            if end < CUTOFF:
                disposition = 'DEATH' if p['death'] else ('TRANSFER' if p['kind'] == 'ED' and p['episode'] in ipd_episodes else 'HOME')
                if not p['death'] and p['kind'] == 'IPD' and p['path'] not in ('GENERAL_SURGERY', 'ORTHOPEDIC') and self.n(eid, 'clinical-nonresponse', 100) < 3:
                    disposition = 'TRANSFER'
                if p['kind'] == 'ED' and p['episode'] not in ipd_episodes and self.n(eid, 'left-unseen', 100) < 2:
                    disposition = 'LEFT_WITHOUT_SEEN'
                    # People who leave before assessment go early in the wait, not after a full work-up.
                    end = min(end, begin + timedelta(minutes=20 + self.n(eid, 'left-unseen-minutes', 100)))
                final = {'discharged_at': stamp(end), 'disposition': disposition}
                if p['kind'] == 'IPD':
                    final['medically_ready_at'] = stamp(end - (p.get('ready_gap') or timedelta(hours=1))) if disposition == 'HOME' else None
                changes.append((end, final))
            rows, state = [], base
            for rev, (known, values) in enumerate(changes, 1):
                state = {**state, **values}
                rows.append(self.row('encounter', f'{eid}/v{rev}', known, encounter_version_id=stable_id('encounter_version', eid, rev),
                                     revision_no=rev, known_from=stamp(known), known_to=None, **state))
                if len(rows) > 1:
                    rows[-2]['known_to'] = stamp(known)
            encounters.extend(rows)
            encounter_histories[eid] = rows
            last[pid] = eid
            if rows[-1]['disposition'] == 'LEFT_WITHOUT_SEEN':
                continue
            at = begin + timedelta(minutes=25)
            if at >= CUTOFF:
                continue
            context = max((r for r in rows if r['known_from'] <= stamp(at)), key=lambda r: r['revision_no'])
            cat = self.code('DIAGNOSIS', self.pathdefs[p['path']]['diagnosis'], at)
            cid = stable_id('clinical_condition', eid, 'primary')
            condition = self.row('clinical_condition', cid + '/v1', at, condition_version_id=stable_id('clinical_condition_version', cid, 1),
                                 condition_id=cid, patient_version_id=patient['patient_version_id'], encounter_version_id=context['encounter_version_id'],
                                 catalog_item_id=cat['catalog_item_id'], condition_type='DIAGNOSIS', status='ACTIVE', diagnosis_rank=1,
                                 present_on_admission='Y' if p['kind'] == 'IPD' else 'NOT_APPLICABLE', onset_at=stamp(begin), severity='SEVERE' if acuity <= 2 else 'MODERATE',
                                 revision_no=1, valid_from=stamp(at), valid_to=None, known_from=stamp(at), known_to=None)
            conditions.append(condition)
            # Resolution of acute pneumonia is an assertion learned at recovery, never placed in the initial row.
            if p['path'] == 'PNEUMONIA' and p['kind'] == 'IPD' and end < CUTOFF and rows[-1]['disposition'] == 'HOME':
                condition['known_to'] = stamp(end)
                closed = {**condition, 'condition_version_id': stable_id('clinical_condition_version', cid, 2), 'revision_no': 2,
                          'source_record_id': cid + '/v2', 'known_from': stamp(end), 'known_to': None, 'valid_to': stamp(end),
                          'recorded_at': stamp(end), 'export_available_at': stamp(end + timedelta(hours=2))}
                resolved = {**closed, 'condition_version_id': stable_id('clinical_condition_version', cid, 3), 'revision_no': 3,
                            'source_record_id': cid + '/v3', 'valid_from': stamp(end), 'valid_to': None, 'status': 'RESOLVED', 'resolved_at': stamp(end)}
                conditions.extend([closed, resolved])
            # A newly recognized chronic problem becomes usable in later encounters.
            prior_codes = {self.by_catalog[r['catalog_item_id']]['code'] for r in self.opening[pid] if r['condition_type'] == 'PROBLEM'}
            if p['path'] in ('HEART_FAILURE', 'COPD', 'GENERAL_MEDICINE') and cat['code'] not in prior_codes:
                pcid = stable_id('clinical_condition', pid, 'new-problem', cat['code'])
                problem = {**condition, 'condition_id': pcid, 'condition_version_id': stable_id('clinical_condition_version', pcid, 1),
                           'source_record_id': pcid + '/v1', 'condition_type': 'PROBLEM', 'diagnosis_rank': 0,
                           'present_on_admission': 'NOT_APPLICABLE', 'encounter_version_id': None, 'known_to': None}
                conditions.append(problem)
                self.opening[pid].append(problem)
        return {'encounter': encounters, 'clinical_condition': conditions}

    def appointments(self):
        latest = {}
        for r in self.t['encounter']:
            if r['encounter_id'] not in latest or r['revision_no'] > latest[r['encounter_id']]['revision_no']:
                latest[r['encounter_id']] = r
        rows = []
        for e in sorted(latest.values(), key=lambda r: r['encounter_id']):
            if e['arrival_at'] < stamp(START) or not (e['encounter_class'] == 'OPD' or e['planned']):
                continue
            at = instant(e['arrival_at'])
            booked = at - timedelta(days=self.booking_lead(e['encounter_id'], 30))
            if booked < datetime(2022, 12, 15, 8, tzinfo=timezone.utc):
                booked = datetime(2022, 12, 15, 8, tzinfo=timezone.utc)
            pid = self.by_patient_version[e['patient_version_id']]['patient_id']
            attending = next(w for w in self.workers[e['facility_id']] if w['worker_assignment_id'] == e['attending_assignment_id'])
            rows.append(self.row('appointment', e['encounter_id'], at, appointment_id=stable_id('appointment', e['encounter_id']),
                                 patient_version_id=source_version(self.patients[pid], booked)['patient_version_id'], location_id=e['location_id'],
                                 worker_assignment_id=self.clinician(e['facility_id'], booked, attending['specialty']), resulting_encounter_version_id=stable_id('encounter_version', e['encounter_id'], 1),
                                 appointment_type='ELECTIVE_ADMISSION' if e['encounter_class'] == 'IPD' else ('FOLLOW_UP' if e['previous_encounter_version_id'] else 'CONSULTATION'),
                                 booked_at=stamp(booked), scheduled_start=stamp(at), scheduled_end=stamp(at + timedelta(minutes=45)), arrived_at=stamp(at)))
        attended = sorted(rows, key=lambda r: r['appointment_id'])
        # Missed visits come from a person-level attendance propensity: younger
        # adults, Medicaid/self-pay coverage, long booking leads and an earlier
        # miss raise it. Outcome counts stay at the frozen contract totals.
        office = [r for r in attended if r['appointment_type'] != 'ELECTIVE_ADMISSION']
        payer_type = {r['payer_plan_id']: r['payer_type'] for r in self.t.get('payer_plan', [])}
        stays = defaultdict(list)
        for e in latest.values():
            if e['encounter_class'] == 'IPD':
                stays[self.by_patient_version[e['patient_version_id']]['patient_id']].append((instant(e['arrival_at']), instant(e['discharged_at']) if e['discharged_at'] else CUTOFF))
        weights, total = [], 0
        for r in office:
            pid = self.by_patient_version[r['patient_version_id']]['patient_id']
            age = age_on(self.patients[pid][0]['birth_date'], r['scheduled_start'][:10])
            known = [c for c in self.coverage[pid] if c['valid_from'] <= r['booked_at'] and (c['valid_to'] is None or r['booked_at'] < c['valid_to'])
                     and c['known_from'] <= r['booked_at'] and (c['known_to'] is None or r['booked_at'] < c['known_to'])]
            cover = payer_type.get(known[0]['payer_plan_id'], 'COMMERCIAL') if len(known) == 1 else 'COMMERCIAL'
            weight = (160 if age < 35 else 125 if age < 50 else 100 if age < 65 else 75 if age < 80 else 90)
            weight = weight * {'MEDICAID': 170, 'SELF_PAY': 190, 'MEDICARE': 80}.get(cover, 100) // 100
            weight = weight * (50 + self.n(pid, 'attendance-propensity', 200)) // 100
            total += weight
            weights.append(total)
        for i in range(8200):
            base = attended[i % len(attended)]
            kind = 'FOLLOW_UP'
            if 3000 <= i < 7000:
                base = office[bisect_right(weights, self.n(str(i), 'missed-visit-person', total))]
                kind = 'CONSULTATION' if self.n(str(i), 'missed-visit-type', 100) < 25 else 'FOLLOW_UP'
            pid = self.by_patient_version[base['patient_version_id']]['patient_id']
            # Same office-hour convention as attended visits.
            at = self.weekday_slot(START + timedelta(days=21 + self.n(str(i), 'unattended-day', 1000), hours=8 + self.n(str(i), 'unattended-hour', 8),
                                                     minutes=15 * self.n(str(i), 'unattended-quarter', 4)), str(i))
            for _ in range(14):
                if not any(a - timedelta(hours=2) < at < b + timedelta(hours=24) for a, b in stays[pid]):
                    break
                at = self.weekday_slot(at + timedelta(days=1), str(i) + '/after-stay')
            lead = self.booking_lead(str(i), 55 if 3000 <= i < 7000 else 30)
            booked = max(at - timedelta(days=lead), datetime(2022, 12, 15, 8, tzinfo=timezone.utc))
            recorded = at + timedelta(hours=1)
            fields = {}
            if i < 3000:
                recorded = max(booked + timedelta(hours=1), at - timedelta(days=1 + self.n(str(i), 'cancel-notice', max(1, lead - 1))))
                fields = dict(cancelled_at=stamp(recorded), cancel_reason=['PATIENT', 'PROVIDER', 'CAPACITY'][i % 3])
            elif i < 7000:
                fields = dict(no_show_recorded_at=stamp(recorded))
            elif i < 8000:
                booked = instant(base['booked_at']) - timedelta(days=7 + self.n(str(i), 'rescheduled-lead', 21))
                recorded = instant(base['booked_at'])
                at = instant(base['scheduled_start']) - timedelta(days=1)
                fields = dict(cancelled_at=stamp(recorded), cancel_reason='RESCHEDULE', replacement_appointment_id=base['appointment_id'])
            else:
                booked, recorded = CUTOFF - timedelta(days=3), CUTOFF - timedelta(days=3)
                at = CUTOFF + timedelta(days=3 + i % 10, hours=10)
            # Prewindow bookings may precede the opening extract; retain the earliest known snapshot.
            booked = max(booked, datetime(2022, 12, 15, 8, tzinfo=timezone.utc))
            rows.append(self.row('appointment', f'unattended/{i}', recorded, appointment_id=stable_id('appointment', 'unattended', i),
                                 patient_version_id=source_version(self.patients[pid], booked)['patient_version_id'], location_id=base['location_id'],
                                 appointment_type=kind, booked_at=stamp(booked), scheduled_start=stamp(at), scheduled_end=stamp(at + timedelta(minutes=45)), **fields))
        return {'appointment': rows}

    def adverse_outcome(self, encounter):
        return encounter['encounter_class']=='IPD' and encounter['disposition'] in ('DEATH','TRANSFER')

    def care(self, facility=None):
        versions = defaultdict(list)
        for r in self.t['encounter']:
            versions[r['encounter_id']].append(r)
        diagnoses = {}
        for r in self.t['clinical_condition']:
            if r['condition_type'] == 'DIAGNOSIS' and r['diagnosis_rank'] == 1 and r['revision_no'] == 1:
                diagnoses[r['encounter_version_id']] = r
        encounter_index = {r['encounter_version_id']: r for r in self.t['encounter']}
        diagnoses = {encounter_index[k]['encounter_id']: v for k, v in diagnoses.items()}
        paths = {p['diagnosis']: (name, p) for name, p in self.pathdefs.items()}
        events = []
        for eid, history in sorted(versions.items()):
            latest = max(history, key=lambda r: r['revision_no'])
            if facility is not None and latest['facility_id'] != facility:
                continue
            begin = instant(latest['arrival_at'])
            end = instant(latest['discharged_at']) if latest['discharged_at'] else CUTOFF - timedelta(seconds=1)
            if eid not in diagnoses:
                continue  # Left without assessment; no invented diagnosis, treatment or signed assessment.
            diagnosis = diagnoses[eid]
            name, path = paths[self.by_catalog[diagnosis['catalog_item_id']]['code']]
            pid = self.by_patient_version[latest['patient_version_id']]['patient_id']
            ipd = latest['encounter_class'] == 'IPD'
            author_specialty = 'Emergency Medicine' if latest['encounter_class'] == 'ED' else ('General Surgery' if name == 'GENERAL_SURGERY' else 'Orthopedics' if name == 'ORTHOPEDIC' else 'Internal Medicine')
            local_events = []

            def emit(kind, key, at, cat=None, **fields):
                if at >= CUTOFF or at > end:
                    return None
                known = max([at] + [instant(fields[f]) for f in ('period_end_at', 'result_ready_at') if fields.get(f)])
                if kind == 'LAB_RESULT' and known >= CUTOFF:
                    return None  # Unfinished analysis is not an observed outcome at the business cutoff.
                context = max((r for r in history if r['known_from'] <= stamp(at)), key=lambda r: r['revision_no'])
                row = self.row('clinical_event', eid + '/' + key, known,
                               clinical_event_version_id=stable_id('clinical_event_version', eid, key, 1), clinical_event_id=stable_id('clinical_event', eid, key),
                               encounter_version_id=context['encounter_version_id'], catalog_item_id=cat['catalog_item_id'] if cat else None,
                               author_assignment_id=self.clinician(latest['facility_id'], at, author_specialty), event_type=kind, occurred_at=stamp(at), status='COMPLETED',
                               aggregation='POINT' if kind in ('OBSERVATION', 'LAB_RESULT') else 'NOT_APPLICABLE',
                               revision_no=1, known_from=stamp(known), known_to=None, **fields)
                local_events.append(row)
                return row

            # The same latent state drives paired measurements and their recovery/deterioration.
            severe = latest['initial_acuity'] <= 2
            adverse = self.adverse_outcome(latest)
            times = [begin + timedelta(minutes=30)]
            if ipd and end - begin > timedelta(hours=12):
                times.append(min(end - timedelta(hours=2), CUTOFF - timedelta(hours=1)))
            obs_codes = path['observations'] if ipd else ['OBS-001', 'OBS-004']
            for code in obs_codes:
                for j, at in enumerate(times):
                    cat = self.code('OBSERVATION', code, at)
                    number, low, high = self.measure(code, eid, name, severe, j if ipd or latest['encounter_class'] == 'ED' else 1, adverse, pid)
                    emit('OBSERVATION', f'{code}/{j}', at, cat, numeric_value=number, value_unit=cat['base_unit'], reference_low=low, reference_high=high)
            lab_codes = path['labs'] if ipd else ([path['labs'][0]] if name == 'CHEST_PAIN' or self.n(eid, 'lab-needed', 100) < 55 else [])
            for code in lab_codes:
                order_at = begin + timedelta(minutes=26)
                cat = self.code('LAB', code, order_at)
                order = emit('ORDER', code + '/order', order_at, cat, order_start_at=stamp(order_at), order_end_at=stamp(end) if latest['discharged_at'] else None)
                for j, collected in enumerate([begin + timedelta(minutes=35)] + ([times[-1]] if len(times) > 1 else [])):
                    ready = collected + timedelta(minutes=20 + self.n(eid + code, 'lab-turnaround', 30))
                    value, low, high = self.measure(code, eid, name, severe, j, adverse, pid)
                    if order:
                        emit('LAB_RESULT', f'{code}/result/{j}', collected, self.code('LAB', code, collected), parent_event_version_id=order['clinical_event_version_id'],
                             numeric_value=value, value_unit=cat['base_unit'], reference_low=low, reference_high=high,
                             specimen_id=stable_id('specimen', eid, j), collected_at=stamp(collected), result_ready_at=stamp(ready))

            if ipd:
                at = begin + timedelta(hours=3 if name in ('GENERAL_SURGERY', 'ORTHOPEDIC') else 8)
                if at < end and at < CUTOFF:
                    cat = self.code('PROCEDURE', path['procedure'], at)
                    order = emit('ORDER', 'procedure/order', begin + timedelta(hours=2), self.code('PROCEDURE', path['procedure'], begin + timedelta(hours=2)), order_start_at=stamp(at))
                    if order:
                        emit('PROCEDURE', 'procedure/performed', at, cat, parent_event_version_id=order['clinical_event_version_id'], period_end_at=stamp(min(at + timedelta(minutes=45), end)))
            else:
                if name == 'CHEST_PAIN' or self.n(eid, 'education-needed', 100) < 25:
                    at = begin + timedelta(minutes=32)
                    cat = self.code('PROCEDURE', 'SVC-003' if name == 'CHEST_PAIN' else 'SVC-021', at)
                    order = emit('ORDER', 'review/order', begin + timedelta(minutes=27), cat)
                    if order:
                        emit('PROCEDURE', 'review/performed', at, cat, parent_event_version_id=order['clinical_event_version_id'])

            med_code = path.get('medication')
            if med_code and (ipd or self.n(eid, 'prescription-needed', 100) < 30):
                at = begin + timedelta(minutes=40)
                cat = self.code('MEDICATION', med_code, at)
                rule = self.policy['medication_constraints'][med_code]
                course_end = at + timedelta(days=rule['max_course_days'])
                order_end = min(course_end, end) if ipd and latest['discharged_at'] else course_end
                allergy = any(r['condition_type'] == 'ALLERGY' and r['status'] == 'ACTIVE' and r['catalog_item_id'] == cat['allergen_catalog_id']
                              and r['known_from'] <= stamp(at) and (r['known_to'] is None or stamp(at) < r['known_to']) for r in self.opening[pid])
                order = emit('ORDER', 'med/order', at, cat, dose_quantity=rule['dose'], dose_unit=rule['unit'], route=rule['route'],
                             order_start_at=stamp(at), order_end_at=stamp(order_end), dose_interval_hours=str(rule['interval_hours']),
                             as_needed=rule['as_needed'], max_doses_per_day=rule['max_doses_per_day'])
                if order:
                    if ipd:
                        step = timedelta(hours=rule['interval_hours'])
                        due, sequence = at + timedelta(minutes=5), 1
                        given_per_day = defaultdict(int)
                        while due < min(order_end, CUTOFF, end):
                            local_day = due.astimezone(self.zone).date().isoformat()
                            if given_per_day[local_day] >= rule['max_doses_per_day']:
                                # A 25-hour fall-back day must not introduce an extra daily dose.
                                due += timedelta(hours=1)
                                continue
                            # PRN administrations are symptom-driven opportunities, not proof every ordered dose was given.
                            prn_chance = max(30, 80 - int((due - at).total_seconds() / 86400) * 10)
                            if not rule['as_needed'] or self.n(eid + str(sequence), 'prn-used', 100) < prn_chance:
                                fields = dict(parent_event_version_id=order['clinical_event_version_id'], dose_quantity=rule['dose'], dose_unit=rule['unit'],
                                              route=rule['route'], administration_sequence=sequence,
                                              consumed_base_quantity='0' if allergy else str((Decimal(rule['dose']) / Decimal(cat['strength_per_base_unit'])).quantize(Decimal('0.000001'))),
                                              consumption_group_key=None if allergy else stable_id('consumption_group', latest['location_id'], med_code, due.astimezone(self.zone).date().isoformat()))
                                event = emit('MED_ADMIN', f'med/admin/{sequence}', due, cat, **fields)
                                if event and allergy:
                                    event['status'] = 'NOT_DONE'
                                    break
                                if event:
                                    given_per_day[local_day] += 1
                            sequence += 1
                            due += step
                    else:
                        quantity = Decimal(rule['dose']) * rule['max_doses_per_day'] * rule['max_course_days']
                        event = emit('MED_DISPENSE', 'med/take-home', min(end, at + timedelta(minutes=10)), cat,
                                     parent_event_version_id=order['clinical_event_version_id'], dose_quantity=str(quantity), dose_unit=rule['unit'], route=rule['route'], administration_sequence=1,
                                     consumed_base_quantity='0' if allergy else str((quantity / Decimal(cat['strength_per_base_unit'])).quantize(Decimal('0.000001'))),
                                     consumption_group_key=None if allergy else stable_id('consumption_group', latest['location_id'], med_code, at.astimezone(self.zone).date().isoformat()))
                        if event and allergy:
                            event['status'] = 'NOT_DONE'

            surgical = ipd and name in ('GENERAL_SURGERY', 'ORTHOPEDIC')
            note_times = [min(end, begin + timedelta(hours=10 if surgical else 4))] if ipd else [end]
            if ipd and latest['discharged_at']:
                note_times.append(end)
            for j, at in enumerate(note_times):
                if at >= CUTOFF:
                    continue
                doc_type = ('DISCHARGE_SUMMARY' if j == 1 else 'PROGRESS_NOTE') if ipd else ('ED_NOTE' if latest['encounter_class'] == 'ED' else 'OP_NOTE')
                if surgical and j == 0:
                    doc_type = 'OPERATIVE_NOTE'
                note = self.note(eid, pid, diagnosis, local_events, path, at, latest, doc_type)
                emit('DOCUMENT', f'note/{j}', at, document_type=doc_type, text_value=note, document_signed_at=stamp(at))
            events.extend(local_events)
        return {'clinical_event': events}

    def measure(self, code, eid, name, severe, phase, adverse, pid):
        # Reference intervals are fictional adult laboratory context, not diagnostic cutoffs.
        ranges = {'OBS-001': (95, 100), 'OBS-004': (60, 100), 'OBS-005': (12, 20), 'OBS-006': (36, 37.5), 'OBS-007': (45, 140),
                  'OBS-009': (0, 10), 'OBS-015': (0, 5), 'OBS-019': (70, 140), 'LAB-002': (3.5, 5.1), 'LAB-004': (22, 29),
                  'LAB-006': (0.6, 1.3), 'LAB-007': (70, 140), 'LAB-011': (4, 11), 'LAB-012': (12, 17.5), 'LAB-024': (0, 10)}
        ranges['LAB-022'] = (0, 14)
        low, high = ranges[code]
        baseline = self.n(eid, 'latent-illness', 100) / 100
        noise = self.n(eid + code, 'measurement', 100) / 100
        recovery = phase and not adverse
        if code == 'OBS-001':
            value = (90 if severe else 93) + 3 * noise if name in ('COPD', 'PNEUMONIA', 'HEART_FAILURE') else 96 + 3 * noise
            value = (95 if name == 'COPD' else 97) + noise if recovery else (value - 4 if phase and adverse else value)
        elif code == 'OBS-005': value = (17 + 2 * noise) if recovery else (23 + 5 * baseline + (3 if severe else 0))
        elif code == 'OBS-006': value = 36.8 + noise / 2 if recovery else 38.0 + baseline
        elif code == 'OBS-007': value = 65 + self.n(pid, 'baseline-weight', 450) / 10 + (0 if recovery else 2 + baseline)
        elif code == 'OBS-009': value = (2 + self.n(eid, 'pain-recovery', 3)) if recovery else 5 + self.n(eid, 'pain-initial', 4)
        elif code == 'OBS-015': value = 4 if recovery else 1 + self.n(eid, 'mobility-initial', 2)
        elif code == 'OBS-019' or code == 'LAB-007': value = 110 + noise * 35 if recovery else 220 + baseline * 110
        elif code == 'OBS-004': value = 72 + noise * 15 if recovery else 90 + baseline * 25
        elif code == 'LAB-006':
            ckd = any(self.by_catalog[r['catalog_item_id']]['code'] == 'N189' for r in self.opening[pid] if r['condition_type'] == 'PROBLEM')
            value = (1.7 if ckd else 0.8) + noise / 3 + (0 if recovery else baseline / 4)
        elif code == 'LAB-002': value = 3.7 + noise / 2 + (0 if recovery else 0.3)
        elif code == 'LAB-004': value = 27 + noise * 3 - (1 if recovery else 0)
        elif code == 'LAB-011': value = (7 + noise * 3) if recovery else (12 + baseline * 7 + (noise - .5) * 2 if name in ('COPD', 'PNEUMONIA') else 6 + noise * 3)
        elif code == 'LAB-012': value = 13.4 + noise * 1.2 - (0.7 if recovery else 0)
        elif code == 'LAB-022': value = 2 + noise * 6
        elif code == 'LAB-024': value = (8 + noise * 8) if recovery else 60 + baseline * 90 + (noise - .5) * 18
        else: raise ValueError('unreviewed clinical measurement')
        if phase and adverse:
            value += .1 + self.n(eid + code, 'persistent-illness-measurement', 30) / 100
        return tuple(str(Decimal(str(v)).quantize(Decimal('0.01'))) for v in (value, low, high))

    def note(self, eid, pid, diagnosis, events, path, at, encounter, doc_type):
        patient = source_version(self.patients[pid], at)
        person = f"{patient['given_name']} {patient['family_name']}"
        age = age_on(patient['birth_date'], at.astimezone(self.zone).date().isoformat())
        headings = ['Clinical review', 'Interval assessment', 'Care assessment', 'Patient review', 'Encounter review', 'Assessment update']
        phrase = headings[self.n(eid + doc_type, 'note-opening', len(headings))]
        diagnosis_text = self.by_catalog[diagnosis['catalog_item_id']]['display']
        concern = ('Interval follow-up for ' if encounter['encounter_class'] == 'OPD' else 'Presenting concern: ') + path['symptom']
        clauses = [f"{phrase}: {person}, age {age}.", concern + '.', f"Working assessment: {diagnosis_text}."]
        # The evidence ledger is embedded in ordinary sentences with stable source references for audit.
        available = [r for r in events if r['known_from'] <= stamp(at) and r['occurred_at'] <= stamp(at)]
        values = [r for r in available if r['event_type'] in ('OBSERVATION', 'LAB_RESULT')]
        for row in values[-4:]:
            cat = self.by_catalog[row['catalog_item_id']]
            clauses.append(f"{cat['display']}: {row['numeric_value']} {row['value_unit']} (record {row['clinical_event_id']}).")
        history = [r for r in self.opening[pid] if r['condition_type'] == 'PROBLEM' and r['known_from'] <= stamp(at)]
        if history:
            names = sorted({self.by_catalog[r['catalog_item_id']]['display'] for r in history})
            clauses.append('Previously recorded problems: ' + '; '.join(names) + '.')
        else:
            clauses.append('Prior problem documentation is incomplete; absence of a record does not exclude disease.')
        medications = [r for r in available if r['event_type'] in ('MED_ADMIN', 'MED_DISPENSE')]
        if doc_type == 'OPERATIVE_NOTE':
            for procedure in (r for r in available if r['event_type'] == 'PROCEDURE' and r['status'] == 'COMPLETED'):
                cat = self.by_catalog[procedure['catalog_item_id']]
                clauses.append(f"Procedure documented: {cat['display']} (record {procedure['clinical_event_id']}).")
        if medications:
            med = medications[-1]
            cat = self.by_catalog[med['catalog_item_id']]
            action = 'withheld; recorded allergy requires review' if med['status'] == 'NOT_DONE' else ('administered' if med['event_type'] == 'MED_ADMIN' else 'dispensed for take-home use; ingestion is unobserved')
            clauses.append(f"{cat['clinical_group']} {med['dose_quantity']} {med['dose_unit']} {action} (record {med['clinical_event_id']}).")
        if doc_type == 'DISCHARGE_SUMMARY':
            clauses.append('Observed disposition: ' + encounter['disposition'] + '.')
        else:
            clauses.append(['Continue assessment as results become available.', 'Reassessment remains appropriate; later outcomes are unknown here.', 'The current assessment may change with further evidence.'][self.n(eid, 'uncertainty', 3)])
        clauses.append('Follow-up completion is not established by this document.')
        return ' '.join(clauses)
