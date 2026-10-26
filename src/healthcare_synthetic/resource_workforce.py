"""Finite worker scheduling, retained source history and activity-linked attendance."""
from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from datetime import timedelta,datetime
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
import logging

from .core import chicago, draw, instant, stable_id
from .operational_validation import bed_intervals
from .resource_generation import START, CUTOFF, ZONE, stamp, local_at, decimal_text, operative_plans, row_builder


def snapshot(rows, at, known=None):
    at = stamp(at) if not isinstance(at, str) else at
    known = at if known is None else stamp(known) if not isinstance(known, str) else known
    found = [r for r in rows if r['valid_from'] <= at and (r['valid_to'] is None or at < r['valid_to'])
             and r['known_from'] <= known and (r['known_to'] is None or known < r['known_to'])]
    return found[0] if len(found) == 1 else None


def week_parts(start, end, zone):
    """Elapsed seconds split at local Monday, including the DST-changing week."""
    cursor = start
    while cursor < end:
        local = cursor.astimezone(zone); monday = local.date() - timedelta(days=local.weekday())
        boundary = local_at(monday + timedelta(days=7))
        stop = min(boundary, end)
        yield monday.isoformat(), Decimal(int((stop-cursor).total_seconds())) / Decimal(3600)
        cursor = stop


class WorkforceGenerator:
    def __init__(self, tables, cfg, run_id):
        self.t, self.cfg, self.run_id = tables, cfg, run_id
        self.zone = ZONE; self.builder = row_builder(cfg, run_id)
        self.hist = defaultdict(list)
        for w in tables['worker_assignment']:
            self.hist[w['worker_id']].append(w)
        self.info = {wid: min(rows, key=lambda r: r['revision_no']) for wid, rows in self.hist.items()}
        self.locations = {r['location_id']: r for r in tables['location']}
        self.units = {(r['facility_id'], r['location_code']): r for r in tables['location']}
        self.enc = {r['encounter_version_id']: r for r in tables['encounter']}
        self.latest = {}
        for e in tables['encounter']:
            if e['encounter_id'] not in self.latest or e['revision_no'] > self.latest[e['encounter_id']]['revision_no']:
                self.latest[e['encounter_id']] = e
        self.intervals = bed_intervals(tables['bed_event'], self.enc)
        self.intervals_by_site = defaultdict(list)
        for bed, eid, a, b in self.intervals:
            unit = self.locations[bed]['service_line']
            self.intervals_by_site[self.locations[bed]['facility_id']].append((a, b, eid, 'ICU' if unit == 'ICU' else 'ACUTE'))
        self.committed = defaultdict(list); self.week_hours = defaultdict(Decimal)
        self.jobs = []; self.rows = []; self.controls = defaultdict(int)
        self.case_plans = operative_plans(tables)
        self.publications = {}

    def eligible(self, wid, at, end=None, known=None):
        row = snapshot(self.hist[wid], at, known)
        if not row:
            return None
        day = at.astimezone(self.zone).date().isoformat()
        last = ((end or at + timedelta(seconds=1))-timedelta(seconds=1)).astimezone(self.zone).date().isoformat()
        if row['hire_date'] > day or row['termination_date'] and row['termination_date'] <= last:
            return None
        if not row['credential_valid_from'] <= day < row['credential_valid_to']:
            return None
        # A renewal during a worked block must be valid in the source knowledge used.
        closing = snapshot(self.hist[wid], end-timedelta(seconds=1), known or end) if end else row
        if not closing or not closing['credential_valid_from'] <= last < closing['credential_valid_to']:
            return None
        if closing['termination_date'] and closing['termination_date'] <= last:
            return None
        return row

    def free(self, wid, start, end):
        rest = timedelta(hours=float(self.cfg['minimum_rest_hours']))
        intervals=self.committed[wid]
        relevant=intervals[-1:] if intervals and start>=intervals[-1][0] else intervals
        if any(start < b+rest and a-rest < end for a, b in relevant):
            return False
        return all(self.week_hours[wid, week]+hours <= Decimal(self.cfg['maximum_weekly_hours'])
                   for week, hours in week_parts(start, end, self.zone))

    def choose(self, fid, role, start, end, specialties=None, agency=False, exclude=None, pickup=None):
        pool = []
        week = (start.astimezone(self.zone).date()-timedelta(days=start.astimezone(self.zone).weekday())).isoformat()
        for wid, w in self.info.items():
            if w['facility_id'] != fid or w['role'] != role or wid == exclude:
                continue
            if specialties and w['specialty'] not in specialties:
                continue
            current = self.eligible(wid, start, end)
            if not current or not self.free(wid, start, end):
                continue
            # Prefer source agency for an explicit callout; routine coverage uses
            # employee capacity first, balanced against contracted FTE.
            preference = (current['worker_type'] != 'AGENCY') if agency else (current['worker_type'] == 'AGENCY')
            score = self.week_hours[wid, week] / Decimal(current['fte'])
            if pickup:
                # A short-notice pickup goes to a rested colleague already working
                # that week, not to the least-loaded one, so some become overtime.
                score = -self.week_hours[wid, week] * 10000 + draw(self.cfg['seed'], pickup + '/' + wid, 'pickup-acceptance', upper=10000)
            pool.append((preference, score, len(self.committed[wid]), wid))
        if not pool:
            raise ValueError(f'no eligible rested {role} for {fid} at {stamp(start)}: {specialties}')
        return min(pool)[-1]

    def add_job(self, key, fid, role, scope, start, end, specialties=None, absence=False, forced_late=False, productive=None):
        if end-start > timedelta(hours=float(self.cfg['maximum_shift_hours'])):
            raise ValueError('resource job exceeds reviewed maximum shift')
        wid = self.choose(fid, role, start, end, specialties)
        actual_start = start
        if absence:
            self.jobs.append(dict(key=key, fid=fid, role=role, scope=scope, start=start, end=end,
                                  wid=wid, absent=True, force_history=True, productive=productive))
            # Availability is a real block for this worker, even though no hours
            # were attended; the replacement is a distinct identity and cost.
            self.committed[wid].append((start, end))
            actual_start = forced_late if isinstance(forced_late,datetime) else start + timedelta(minutes=25) if forced_late else start
            agency = draw(self.cfg['seed'], key, 'replacement-source', upper=100) < self.cfg['replacement_agency_percent']
            replacement = self.choose(fid, role, actual_start, end, specialties, agency=agency, exclude=wid, pickup=None if agency else key)
            self.controls['agency_replacements' if self.info[replacement]['worker_type']=='AGENCY' else 'employee_replacements'] += 1
            self.controls['absences'] += 1
            original_id = stable_id('shift', key)
            key = 'replace/'+original_id
            wid = replacement
        self.committed[wid].append((actual_start, end))
        for week, hours in week_parts(actual_start, end, self.zone):
            self.week_hours[wid, week] += hours
        # The absent shift keeps its roster history; the replacement keeps only its
        # attendance, within the frozen staffing row envelope.
        job = dict(key=key, fid=fid, role=role, scope=scope, start=start, end=end, actual_start=actual_start,
                   wid=wid, absent=False, force_history=absence and scope == 'OR', productive=productive)
        self.jobs.append(job)
        return job

    def absence_rate(self, at):
        """Unplanned RN absences per thousand shifts, higher in winter and the respiratory surge."""
        rates = self.cfg['rn_absence_per_thousand']
        local = at.astimezone(self.zone).date().isoformat()
        if '2024-01-08' <= local < '2024-02-26':
            return rates['surge']
        return rates['winter'] if local[5:7] in ('12', '01', '02') else rates['base']

    def census_requirement(self, fid, scope, at, hours):
        total = Decimal(0)
        when=stamp(at)
        for a, b, eid, unit in self.intervals_by_site[fid]:
            if unit == scope and a <= when < b:
                e = self.latest[eid]
                total += Decimal(self.cfg['rn_hours_per_patient_day']) * Decimal(self.cfg['acuity_weights'][str(e['initial_acuity'])]) * hours / 24
        return total

    def plan(self):
        sites = sorted(r['facility_id'] for r in self.t['facility'])
        # Plan surgery blocks from the counted, constrained actual agenda, then
        # merge a worker's contiguous day caseload so rest is not manufactured
        # between fragments of the same duty block.
        surgeon_groups = defaultdict(list); rn_groups = defaultdict(list)
        lane_ends = defaultdict(lambda: [START, START])
        for eid, p in sorted(self.case_plans.items(), key=lambda x: (x[1]['start'], x[0])):
            a, b = instant(p['start']), instant(p['end'])
            if not START <= a < CUTOFF:
                continue
            day = a.astimezone(self.zone).date().isoformat()
            lane_key = p['facility_id'], p['specialty'], day
            lane = min(range(2), key=lambda i: (lane_ends[lane_key][i], i))
            lane_ends[lane_key][lane] = b
            surgeon_groups[p['facility_id'], p['specialty'], day, lane].append((a, b, eid))
            key = p['facility_id'], day
            lane = min(range(2), key=lambda i: (lane_ends[key][i], i))
            lane_ends[key][lane] = b
            rn_groups[p['facility_id'], day, lane].append((a, b, eid))
        special_jobs = []
        for (fid, specialty, day, lane), cases in surgeon_groups.items():
            special_jobs.append((min(instant(self.case_plans[c[2]]['planned']) for c in cases)-timedelta(minutes=15), max(c[1] for c in cases)+timedelta(minutes=15),
                f'surgeon/{fid}/{specialty}/{day}/{lane}', fid, 'PHYSICIAN', 'OR', [specialty], False, False, None))
        for (fid, day, lane), cases in rn_groups.items():
            first = min(cases)
            p = self.case_plans[first[2]]
            absence = any(self.case_plans[c[2]]['cause']=='CIRCULATING_RN_ABSENCE' for c in cases)
            # A selected absent case is first in its lane/day; source publication
            # retains the original start, while replacement attendance is late.
            begin = min(instant(self.case_plans[c[2]]['planned']) for c in cases)-timedelta(minutes=15)
            end = max(c[1] for c in cases)+timedelta(minutes=15)
            productive = sum((Decimal(int((b-a).total_seconds()))/3600+Decimal('0.25') for a,b,_ in cases), Decimal(0))
            ready=min(instant(self.case_plans[c[2]]['ready']) for c in cases if self.case_plans[c[2]]['cause']=='CIRCULATING_RN_ABSENCE') if absence else False
            special_jobs.append((begin, end, f'circulator/{fid}/{day}/{lane}', fid, 'RN', 'OR', ['Medical-Surgical Nursing'], absence, ready, productive))
        agenda = []
        day = START.astimezone(self.zone).date()-timedelta(days=1)
        while day <= CUTOFF.astimezone(self.zone).date()-timedelta(days=1):
            for hour in (7, 19):
                a = local_at(day, hour); b = local_at(day+timedelta(days=1), 7) if hour==19 else local_at(day, 19)
                if b <= START or a >= CUTOFF:
                    continue
                elapsed = Decimal(int((b-a).total_seconds()))/3600
                productive = elapsed-Decimal('1.25')
                for fid in sites:
                    agenda.append((a,b,f'physician/ED/{fid}/{stamp(a)}',fid,'PHYSICIAN','ED',['Emergency Medicine'],False,False,None))
                    if hour==7:
                        agenda.append((a,b,f'physician/medicine/{fid}/{stamp(a)}',fid,'PHYSICIAN','ACUTE',['Internal Medicine'],False,False,None))
                    for scope in ('ACUTE','ICU','ED'):
                        need = max(productive, self.census_requirement(fid,scope,max(a,START),elapsed))
                        full = max(1,int(need//productive));remaining=need-full*productive
                        skills = ['Critical Care Nursing'] if scope=='ICU' else (['Emergency Nursing','Critical Care Nursing'] if scope=='ED' else ['Medical-Surgical Nursing','Emergency Nursing','Critical Care Nursing'])
                        for i in range(full):
                            key=f'RN/{fid}/{scope}/{stamp(a)}/{i}'
                            agenda.append((a,b,key,fid,'RN',scope,skills,False,False,None))
                        if remaining>=Decimal('3'):
                            length = min(elapsed, max(Decimal(4), (remaining+Decimal('0.75')).quantize(Decimal('0.25'), rounding=ROUND_CEILING)))
                            stop=a+timedelta(seconds=int(length*3600))
                            agenda.append((a,stop,f'RN/{fid}/{scope}/{stamp(a)}/{full}',fid,'RN',scope,skills,False,False,None))
                        window=f'RN/{fid}/{scope}/{stamp(a)}'
                        if draw(self.cfg['seed'],window,'retained-roster-window',upper=self.cfg['retain_initial_roster_every'])==0:
                            publication=a-timedelta(days=self.cfg['roster_lead_days'])
                            lagged=publication-timedelta(days=1)
                            forecast=max(productive,self.census_requirement(fid,scope,lagged,elapsed)) if lagged>=START else productive*(3 if scope=='ACUTE' else 1)
                            count=max(1,int(forecast//productive));rem=forecast-count*productive
                            for i in range(count):self.publications[window+'/'+str(i)]=(publication,a,b,fid,'RN',scope,skills)
                            if rem>=3:
                                length=min(elapsed,max(Decimal(4),(rem+Decimal('.75')).quantize(Decimal('.25'),rounding=ROUND_CEILING)))
                                self.publications[window+'/'+str(count)]=(publication,a,a+timedelta(seconds=int(length*3600)),fid,'RN',scope,skills)
            day += timedelta(days=1)
        agenda += special_jobs
        feb = sorted(x[2] for x in agenda if x[4]=='RN' and x[5]!='OR' and x[2].endswith('/0') and x[0].astimezone(self.zone).strftime('%Y-%m')=='2025-02')[:self.cfg['february_absences']]
        forced = set(feb)
        for ordinal,(a,b,key,fid,role,scope,skills,absence,late,productive) in enumerate(sorted(agenda,key=lambda x:(x[0],x[2]))):
            if ordinal%5000==0:logging.getLogger(__name__).info('Scheduling attendance block %s/%s',ordinal,len(agenda))
            baseline_absence = role=='RN' and scope!='OR' and draw(self.cfg['seed'],key,'reported-absence',upper=1000)<self.absence_rate(a)
            self.add_job(key,fid,role,scope,a,b,skills,absence or key in forced or baseline_absence,late,productive)
        # Selected ordinary support work and paid/nonpaid leave are retained source
        # activity, not invented full payroll or continuous contractor coverage.
        for wid,w in sorted(self.info.items()):
            if w['role'] in ('RN','PHYSICIAN'):
                continue
            for year in (2023,2024,2025):
                for month in (2,5,8,11):
                    day = START.date().replace(year=year,month=month,day=10+draw(self.cfg['seed'],wid+str(year)+str(month),'support-day',upper=10))
                    a,b=local_at(day,8),local_at(day,16)
                    if self.eligible(wid,a,b) and self.free(wid,a,b):
                        self.committed[wid].append((a,b))
                        for week,h in week_parts(a,b,self.zone):self.week_hours[wid,week]+=h
                        self.jobs.append(dict(key=f'support/{wid}/{day}',fid=w['facility_id'],role=w['role'],scope=self.locations[w['home_location_id']]['location_code'],start=a,end=b,actual_start=a,wid=wid,absent=False,force_history=False,productive=None))
        return self

    def materialize(self):
        running = defaultdict(Decimal)
        planned_calendar = defaultdict(list)
        # Build retained publications in source-knowledge order, independently of
        # the actual worker/headcount. Future extra actual slots cannot appear in
        # an earlier plan. A forecast slot not worked gets a counted cancellation.
        for job in self.jobs:
            a,b=job['start'],job['end'];key=job['key']
            selected=job['force_history'] or job['role']!='RN' and draw(self.cfg['seed'],stable_id('shift',key),'retained-publication',upper=self.cfg['retain_initial_roster_every'])==0
            if not selected:continue
            if key.startswith('replace/'):publication=a-timedelta(minutes=60)
            elif job['scope']=='OR':publication=a-timedelta(hours=2)
            else:publication=a-timedelta(days=self.cfg['roster_lead_days'])
            if job['scope']=='OR':b=a+timedelta(hours=12)
            skills=['Critical Care Nursing'] if job['scope']=='ICU' else ['Emergency Nursing','Critical Care Nursing'] if job['role']=='RN' and job['scope']=='ED' else ['Medical-Surgical Nursing'] if job['role']=='RN' and job['scope']=='OR' else None
            if job['role']=='PHYSICIAN':skills=[self.info[job['wid']]['specialty']]
            self.publications.setdefault(key,(publication,a,b,job['fid'],job['role'],job['scope'],skills))
        publication_fields={};planned_week=defaultdict(Decimal)
        for key,(pub,a,b,fid,role,scope,skills) in sorted(self.publications.items(),key=lambda x:(x[1][0],x[0])):
            candidates=[]
            for wid,w in self.info.items():
                if w['facility_id']!=fid or w['role']!=role or skills and w['specialty'] not in skills:continue
                ref=self.eligible(wid,a,b,pub)
                if not ref or any(a<stop+timedelta(hours=10) and begin-timedelta(hours=10)<b for begin,stop in planned_calendar[wid]):continue
                parts=list(week_parts(a,b,self.zone))
                if any(planned_week[wid,week]+hours>60 for week,hours in parts):continue
                candidates.append((sum(planned_week[wid,week] for week,_ in parts)/Decimal(ref['fte']),wid,ref))
            if not candidates:continue  # absent retained initial source history remains unknown
            _,wid,ref=min(candidates,key=lambda x:(x[0],x[1]));planned_calendar[wid].append((a,b))
            for week,hours in week_parts(a,b,self.zone):planned_week[wid,week]+=hours
            location=self.units[fid,scope];sid=stable_id('shift',key)
            state=dict(shift_id=sid,worker_assignment_id=ref['worker_assignment_id'],location_id=location['location_id'],cost_center_id=location['cost_center_id'],
                shift_type='WORK',planned_start=stamp(a),planned_end=stamp(b),actual_start=None,actual_end=None,
                worked_hours='0.000000',productive_hours='0.000000',paid_nonproductive_hours='0.000000',unpaid_break_hours='0.000000',overtime_hours='0.000000',
                loaded_cost='0.00',currency='USD',posting_group_key='labor/'+fid+'/'+location['cost_center_id']+'/'+a.astimezone(self.zone).date().isoformat(),attendance_status='PUBLISHED')
            publication_fields[key]=(pub,state)
        correction_budget=self.cfg['late_attendance_corrections']
        # Overtime is computed in chronological paid-time order, not by row order.
        for job in sorted(self.jobs,key=lambda j:(j.get('actual_start',j['start']),j['key'])):
            a,b=job['start'],job['end'];actual=job.get('actual_start',a);wid=job['wid']
            open_shift=b>CUTOFF
            known=(a-timedelta(minutes=90)) if job['absent'] else (a if open_shift else b+timedelta(minutes=30))
            reference=self.eligible(wid,actual,min(b,CUTOFF),known)
            if reference is None:
                raise ValueError('no source assignment for attendance revision: '+wid+' '+stamp(actual))
            sid=stable_id('shift',job['key']);location=self.units[job['fid'],job['scope']]
            exact_hours=Decimal(0) if job['absent'] or open_shift else Decimal(int((b-actual).total_seconds()))/3600
            actual_hours=exact_hours.quantize(Decimal('.000001'))
            unpaid=Decimal('0.5') if actual_hours>=6 else Decimal(0)
            nonproductive=Decimal('0.75') if actual_hours>=8 else Decimal('0.25') if actual_hours>=4 else Decimal(0)
            productive=max(Decimal(0),actual_hours-unpaid-nonproductive)
            if job['productive'] is not None and actual_hours:
                productive=min(productive,job['productive']);nonproductive=actual_hours-unpaid-productive
            paid=actual_hours-unpaid; overtime=Decimal(0)
            if actual_hours:
                parts=list(week_parts(actual,b,self.zone));allocated=Decimal(0)
                for i,(week,elapsed) in enumerate(parts):
                    part=paid-allocated if i==len(parts)-1 else (paid*elapsed/exact_hours).quantize(Decimal('0.000001'))
                    allocated+=part
                    overtime+=max(Decimal(0),running[wid,week]+part-40)-max(Decimal(0),running[wid,week]-40)
                    running[wid,week]+=part
            premium=Decimal('0.5') if reference['worker_type']=='EMPLOYEE' and reference['role']!='PHYSICIAN' else Decimal(0)
            cost=((paid+overtime*premium)*Decimal(reference['hourly_cost_rate'])).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
            fields=dict(shift_id=sid,worker_assignment_id=reference['worker_assignment_id'],location_id=location['location_id'],
                cost_center_id=location['cost_center_id'],shift_type='WORK',planned_start=stamp(a),planned_end=stamp(b),
                actual_start=None if job['absent'] else stamp(actual),actual_end=None if job['absent'] or open_shift else stamp(b),
                worked_hours=decimal_text(actual_hours),productive_hours=decimal_text(productive),paid_nonproductive_hours=decimal_text(nonproductive),
                unpaid_break_hours=decimal_text(unpaid),overtime_hours=decimal_text(overtime),loaded_cost=format(cost,'f'),currency='USD',
                posting_group_key='labor/'+job['fid']+'/'+location['cost_center_id']+'/'+a.astimezone(self.zone).date().isoformat(),
                attendance_status='ABSENT' if job['absent'] else 'PUBLISHED' if open_shift else 'WORKED')
            earlier=[]
            if job['key'] in publication_fields:
                publication,planned=publication_fields.pop(job['key']);earlier.append((publication,planned))
                fields.update(planned_start=planned['planned_start'],planned_end=planned['planned_end'])
                if job['absent'] and planned['worker_assignment_id']!=fields['worker_assignment_id']:
                    reassigned={**planned,'worker_assignment_id':fields['worker_assignment_id']}
                    earlier.append((max(publication+timedelta(minutes=1),a-timedelta(minutes=120)),reassigned))
            # Correct selected under-recorded paid nonproductive minutes later.
            # The earlier assertion is retained; final attendance, not both rows,
            # contributes to current expense and available productive capacity.
            late_correct=not job['absent'] and not open_shift and actual_hours>=8 and correction_budget>0 and a>START+timedelta(days=14) and b<CUTOFF-timedelta(days=4)
            if late_correct:
                wrong={**fields,'productive_hours':decimal_text(productive+Decimal('.25')),
                    'paid_nonproductive_hours':decimal_text(nonproductive-Decimal('.25'))}
                earlier.append((known,wrong));known+=timedelta(days=2);correction_budget-=1
                effective=snapshot(self.hist[wid],actual,known)
                if effective and effective['worker_assignment_id']!=fields['worker_assignment_id']:
                    fields.update(worker_assignment_id=effective['worker_assignment_id'],loaded_cost=format(((paid+overtime*premium)*Decimal(effective['hourly_cost_rate'])).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'f'))
            revisions=[*earlier,(known,fields)]
            if actual_hours:
                future_times=sorted({instant(w['known_from'])+timedelta(minutes=30) for w in self.hist[wid]
                    if known<instant(w['known_from'])<min(b+timedelta(days=12),CUTOFF)})
                for revised_at in future_times:
                    effective=snapshot(self.hist[wid],actual,revised_at)
                    if effective and effective['worker_assignment_id']!=revisions[-1][1]['worker_assignment_id']:
                        corrected={**fields,'worker_assignment_id':effective['worker_assignment_id'],
                            'loaded_cost':format(((paid+overtime*premium)*Decimal(effective['hourly_cost_rate'])).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'f')}
                        revisions.append((revised_at,corrected));self.controls['late_rate_corrections']+=1
            for i,(at,state) in enumerate(revisions,1):
                self.rows.append(self.builder.row('staff_shift',job['key']+f'/v{i}',stamp(at),shift_version_id=stable_id('shift_version',sid,i),
                    revision_no=i,known_from=stamp(at),known_to=stamp(revisions[i][0]) if i<len(revisions) else None,**state))
            self.controls['worked_blocks' if fields['attendance_status']=='WORKED' else 'absent_blocks' if job['absent'] else 'open_blocks']+=1
        for key,(publication,state) in sorted(publication_fields.items()):
            sid=state['shift_id'];cancelled={**state,'attendance_status':'CANCELLED'}
            for rev,at,values,end_known in [(1,publication,state,state['planned_start']),(2,instant(state['planned_start']),cancelled,None)]:
                self.rows.append(self.builder.row('staff_shift',key+f'/v{rev}',stamp(at),shift_version_id=stable_id('shift_version',sid,rev),
                    revision_no=rev,known_from=stamp(at),known_to=end_known,**values))
            self.controls['cancelled_forecast_slots']+=1
        # An explicit paid leave source block is separate from attended work.
        for wid,w in sorted(self.info.items()):
            for year in (2023,2024,2025):
                for month in (3,9):
                    a=local_at(START.date().replace(year=year,month=month,day=5+draw(self.cfg['seed'],wid+str(year)+str(month),'leave-date',upper=20)),8)
                    b=a+timedelta(hours=8)
                    reference=self.eligible(wid,a,b)
                    if not reference or not self.free(wid,a,b):continue
                    sid=stable_id('shift','leave',wid,stamp(a));at=b+timedelta(minutes=30);location=self.locations[reference['home_location_id']]
                    self.rows.append(self.builder.row('staff_shift',f'paid-leave/{sid}/v1',stamp(at),shift_version_id=stable_id('shift_version',sid,1),shift_id=sid,
                        worker_assignment_id=reference['worker_assignment_id'],location_id=location['location_id'],cost_center_id=location['cost_center_id'],shift_type='LEAVE',
                        planned_start=stamp(a),planned_end=stamp(b),worked_hours='0.000000',productive_hours='0.000000',paid_nonproductive_hours='0.000000',
                        unpaid_break_hours='0.000000',overtime_hours='0.000000',loaded_cost=format((Decimal(reference['hourly_cost_rate'])*8).quantize(Decimal('.01')),'f'),
                        currency='USD',posting_group_key='paid-leave/'+wid+'/'+a.astimezone(self.zone).date().isoformat(),attendance_status='ON_LEAVE',
                        revision_no=1,known_from=stamp(at)))
                    self.controls['leave_blocks']+=1
        envelope=self.cfg.get('staff_shift_row_envelope',70000)
        if len(self.rows)>envelope:raise ValueError(f'complete staffing source history exceeds frozen {envelope}-row envelope: '+str(len(self.rows)))
        self.controls['late_attendance_corrections']=self.cfg['late_attendance_corrections']-correction_budget
        return {'tables':{'staff_shift':self.rows},'controls':dict(self.controls)}


def bind_working_authors(tables, cfg, run_id):
    workers={w['worker_assignment_id']:w for w in tables['worker_assignment']}
    hist=defaultdict(list)
    for w in tables['worker_assignment']:hist[w['worker_id']].append(w)
    latest={}
    for r in tables['staff_shift']:
        if r['shift_id'] not in latest or r['revision_no']>latest[r['shift_id']]['revision_no']:latest[r['shift_id']]=r
    shifts=defaultdict(list);locations={r['location_id']:r for r in tables['location']}
    for r in latest.values():
        if r['actual_start'] is not None and r['attendance_status'] in ('WORKED','PUBLISHED'):
            w=workers[r['worker_assignment_id']]
            a=instant(r['actual_start']);b=instant(r['actual_end'] or stamp(CUTOFF));day=a.astimezone(ZONE).date()
            while day<=b.astimezone(ZONE).date():
                shifts[w['facility_id'],day.isoformat()].append((r['actual_start'],r['actual_end'] or stamp(CUTOFF),w['worker_id'],w['role'],w['specialty'],locations[r['location_id']]['location_code']))
                day+=timedelta(days=1)
    enc={r['encounter_version_id']:r for r in tables['encounter']};catalog={r['catalog_item_id']:r for r in tables['catalog_item']}
    intervals=defaultdict(list)
    for bed,eid,a,b in bed_intervals(tables['bed_event'],enc):intervals[eid].append((a,b,'ICU' if locations[bed]['service_line']=='ICU' else 'ACUTE'))
    cache={};operative_busy=defaultdict(list)
    def actor(fid,at,role='PHYSICIAN',scope=None,specialty=None,end=None):
        key=fid,at,role,scope,specialty,end
        if specialty is None and key in cache:return cache[key]
        candidates=[]
        for a,b,wid,r,s,unit in shifts[fid,instant(at).astimezone(ZONE).date().isoformat()]:
            if a<=at<b and (end is None or end<=b) and r==role and (specialty is None or s==specialty) and (scope is None or unit==scope):
                if specialty is None and role=='PHYSICIAN' and unit=='OR':continue
                if specialty is not None and any(at<stop and begin<(end or at) for begin,stop in operative_busy[wid]):continue
                row=snapshot(hist[wid],at,at)
                if row is not None:candidates.append(row['worker_assignment_id'])
        if not candidates:raise ValueError(f'no working source author {fid} {at} {role} {scope} {specialty}')
        selected=min(candidates)
        if specialty is not None:operative_busy[workers[selected]['worker_id']].append((at,end))
        else:cache[key]=selected
        return selected
    # The attending of record is an accountable/on-call source assignment, not
    # an assertion of continuous physical attendance. Preserve that identity and
    # specialty; actual event authors/performers bind to represented attendance.
    operative_authors={};case_lane_ends=defaultdict(lambda:[stamp(START),stamp(START)])
    for r in sorted((r for r in tables['clinical_event'] if r['event_type']=='PROCEDURE' and r['occurred_at']>=stamp(START) and catalog[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9')),key=lambda r:(r['occurred_at'],r['clinical_event_id'])):
        e=enc[r['encounter_version_id']];specialty='General Surgery' if catalog[r['catalog_item_id']]['code']=='0FT44ZZ' else 'Orthopedics'
        day=instant(r['occurred_at']).astimezone(ZONE).date().isoformat();lane_key=e['facility_id'],specialty,day
        lane=min(range(2),key=lambda i:(case_lane_ends[lane_key][i],i));case_lane_ends[lane_key][lane]=r['period_end_at']
        sid=stable_id('shift',f"surgeon/{e['facility_id']}/{specialty}/{day}/{lane}");shift=latest[sid]
        wid=workers[shift['worker_assignment_id']]['worker_id'];ref=snapshot(hist[wid],r['occurred_at'])
        if ref is None or not shift['actual_start']<=r['occurred_at'] or r['period_end_at']>(shift['actual_end'] or stamp(CUTOFF)):
            raise ValueError('operative case list has no eligible observed surgeon attendance')
        operative_authors[r['clinical_event_version_id']]=ref['worker_assignment_id']
    events=[];rn_count=0
    for r in tables['clinical_event']:
        at=r['occurred_at'];e=enc[r['encounter_version_id']]
        if at<stamp(START):events.append(r);continue
        if r['event_type']=='PROCEDURE' and catalog[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9'):
            author=operative_authors[r['clinical_event_version_id']]
        elif r['event_type']=='MED_ADMIN' or r['event_type']=='OBSERVATION' and e['encounter_class'] in ('IPD','ED'):
            scope=next((unit for a,b,unit in intervals[e['encounter_id']] if a<=at<b),'ED' if e['encounter_class']=='ED' or e['admission_source']=='ED' else 'ACUTE')
            author=actor(e['facility_id'],at,'RN',scope);rn_count+=1
        else:author=actor(e['facility_id'],at)
        events.append({**r,'author_assignment_id':author,'generation_run_id':run_id})
    return {'tables':{'clinical_event':events},'controls':{'rn_authored_events':rn_count}}
