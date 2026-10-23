"""Independent workforce, clinical integration and resource budget controls.

No generator, scheduler, random draw or generation serializer is imported.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from .master_validation import MasterValidator, contains, timestamp
from .operational_validation import IntegratedClinicalValidator, OperationalValidator, bed_intervals, resolve_events

ZONE=ZoneInfo('America/Chicago')
START='2023-01-01T06:00:00Z';CUTOFF='2026-01-01T06:00:00Z';GRACE='2026-01-10T23:59:59Z'
HOUR=Decimal(3600)


def hours(a,b):return Decimal(int((timestamp(b)-timestamp(a)).total_seconds()))/HOUR


def asof_worker(hist,at,known):
    candidates=[w for w in hist if w['valid_from']<=at and (w['valid_to'] is None or at<w['valid_to'])
                and w['known_from']<=known and (w['known_to'] is None or known<w['known_to'])]
    if len(candidates)!=1:raise ValueError('worker snapshot is absent or ambiguous')
    return candidates[0]


def local_weeks(a,b):
    cursor=timestamp(a);end=timestamp(b)
    while cursor<end:
        local=cursor.astimezone(ZONE);monday=local.date()-timedelta(days=local.weekday())
        stop=min(end,datetime.combine(monday+timedelta(days=7),datetime.min.time(),tzinfo=ZONE).astimezone(timezone.utc))
        yield monday.isoformat(),Decimal(int((stop-cursor).total_seconds()))/HOUR
        cursor=stop


class ResourceClinicalValidator(IntegratedClinicalValidator):
    def valid_author(self,key,facility,at,context):
        worker=self.idx['worker_assignment'][key];event=self.events.get(context)
        if worker['role']=='RN' and event and event['event_type'] in ('MED_ADMIN','OBSERVATION'):
            day=timestamp(at).astimezone(self.local_zone).date().isoformat()
            self.need(worker['facility_id']==facility and contains(worker,at,at,availability=False)
                and worker['credential_code']=='RN' and worker['hire_date']<=day
                and (worker['termination_date'] is None or day<worker['termination_date'])
                and worker['credential_valid_from']<=day<worker['credential_valid_to'],context,'RN author credential/employment/source snapshot invalid')
        else:super().valid_author(key,facility,at,context)

    def check_documents(self):
        extra=[r for r in self.t['clinical_event'] if r['source_record_id'].endswith('/resource-response') or (r['text_value'] or '').startswith('Resource coordination for procedure ')]
        ids={r['clinical_event_version_id'] for r in extra};old=self.t
        self.t={**old,'clinical_event':[r for r in old['clinical_event'] if r['clinical_event_version_id'] not in ids]}
        try:super().check_documents()
        finally:self.t=old
        by_logical={r['clinical_event_id']:r for r in self.t['clinical_event']}
        pattern=r'Resource coordination for procedure (\S+): planned (\S+); resource ready (\S+); observed start (\S+)\. Cause: (UNIT_STOCKOUT|CIRCULATING_RN_ABSENCE|OPERATIVE_CAPACITY_QUEUE)\. Care remains within the observed encounter; later outcome is not asserted\.((?: Recorded assessment \S+=\S+ \S+ \(record \S+, observed \S+\)\.){1,2})'
        normalized=Counter()
        for r in extra:
            match=re.fullmatch(pattern,r['text_value'] or '')
            self.need(match is not None,r['clinical_event_version_id'],'unsupported resource document grammar')
            p=by_logical.get(match[1]);self.need(p is not None and p['event_type']=='PROCEDURE',r['clinical_event_version_id'],'resource note missing procedure')
            self.need(match[2]<match[4]==p['occurred_at']==r['occurred_at']==r['document_signed_at']==r['known_from'] and match[3]<=match[4],r['clinical_event_version_id'],'resource cause/ready/performed/signing chronology differs')
            self.need(r['event_type']=='DOCUMENT' and r['document_type']=='PROGRESS_NOTE' and r['status']=='COMPLETED'
                and self.idx['encounter'][p['encounter_version_id']]['encounter_id']==self.idx['encounter'][r['encounter_version_id']]['encounter_id'],r['clinical_event_version_id'],'resource note encounter or document type mismatch')
            facts=re.findall(r' Recorded assessment (\S+)=(\S+) (\S+) \(record (\S+), observed (\S+)\)\.',match[6])
            self.need(len(facts)==2,r['clinical_event_version_id'],'resource note lacks its two recorded assessment facts')
            for code,value,unit,identity,observed in facts:
                fact=by_logical.get(identity)
                self.need(fact is not None and fact['event_type'] in ('OBSERVATION','LAB_RESULT') and self.catalog[fact['catalog_item_id']]['code']==code
                    and fact['numeric_value']==value and fact['value_unit']==unit and fact['occurred_at']==observed<=r['known_from'] and fact['known_from']<=r['known_from']
                    and self.idx['encounter'][fact['encounter_version_id']]['encounter_id']==self.idx['encounter'][r['encounter_version_id']]['encounter_id'],r['clinical_event_version_id'],'resource assessment cites a future/different/unsupported observation')
            body=re.sub(r'clinical_event_[a-f0-9]+','FACT',r['text_value'])
            body=re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z','TIME',body)
            normalized[body.lower()]+=1
        count=self.metrics['document_counts']['PROGRESS_NOTE']+self.metrics['placement_assessment_documents']+self.metrics['placement_disposition_documents']+self.metrics['transfer_referral_documents']
        share=Decimal(str(self.metrics['progress_note_duplicate_share_upper_bound']))
        pooled=(share*count+sum(n-1 for n in normalized.values()))/(count+len(extra))
        self.need(pooled<=Decimal(str(self.policy['targets']['maximum_normalized_note_duplicate_share'])),'resource-notes','pooled resource-note duplicate bound exceeds frozen target')
        self.metrics['resource_coordination_documents']=len(extra)
        self.metrics['normalized_resource_note_duplicates']=sum(n-1 for n in normalized.values())
        self.metrics['resource_progress_duplicate_bound']=str(pooled)


class ResourceOperationalValidator(OperationalValidator):
    def check_budget(self):
        saved=self.t;self.t={k:v for k,v in saved.items() if k not in ('staff_shift','inventory_movement')}
        try:super().check_budget()
        finally:self.t=saved
        self.need(len(self.t)==18 and sum(map(len,self.t.values()))<=1958210,'resource extension aggregate budget differs')
        self.metrics.update(business_rows=sum(map(len,self.t.values())),rows_by_table={k:len(v) for k,v in self.t.items()},remaining_planned_rows=1958210-sum(map(len,self.t.values())))


class ResourceValidator:
    def __init__(self,tables,schema,cfg,parent=None):
        self.t,self.schema,self.cfg,self.parent=tables,schema,cfg,parent
        self.workers={r['worker_assignment_id']:r for r in tables['worker_assignment']};self.worker_hist=defaultdict(list)
        for w in tables['worker_assignment']:self.worker_hist[w['worker_id']].append(w)
        self.locations={r['location_id']:r for r in tables['location']};self.enc={r['encounter_version_id']:r for r in tables['encounter']}
        self.enc_latest={}
        for e in tables['encounter']:
            if e['encounter_id'] not in self.enc_latest or e['revision_no']>self.enc_latest[e['encounter_id']]['revision_no']:self.enc_latest[e['encounter_id']]=e
        self.catalog={r['catalog_item_id']:r for r in tables['catalog_item']}
        self.histories=defaultdict(list)
        for r in tables['staff_shift']:self.histories[r['shift_id']].append(r)
        # Fix aggregation order across in-memory stage output and canonical PK
        # serialization. Month-boundary prorations have recurring decimals;
        # summing identical terms in a different order must not change controls.
        self.latest={sid:max(rows,key=lambda r:r['revision_no']) for sid,rows in sorted(self.histories.items())}
        self.metrics={};self.working=[r for r in self.latest.values() if r['actual_start'] and r['attendance_status'] in ('WORKED','PUBLISHED')]

    def need(self,condition,message):
        if not condition:raise ValueError(message)

    def check_schema_history(self):
        v=MasterValidator(self.t,self.schema,{}, {'permitted_tables':list(self.t)}, {})
        for name in ('schema','keys','references'):getattr(v,'check_'+name)()
        specs={t['name']:t for t in self.schema['tables']}
        for table in ('staff_shift','inventory_movement'):
            for r in self.t[table]:
                self.need(r['source_system']==specs[table]['source_authority'],'wrong resource source authority')
                self.need(r['recorded_at']<=r['export_available_at']<=GRACE,'resource source/export/grace chronology')
        for sid,rows in self.histories.items():
            ordered=sorted(rows,key=lambda r:r['revision_no'])
            self.need([r['revision_no'] for r in ordered]==list(range(1,len(rows)+1)),'noncontiguous staff revision history')
            for i,r in enumerate(ordered):
                self.need(r['known_to']==(ordered[i+1]['known_from'] if i+1<len(rows) else None),'staff supersession differs')
                self.need(r['recorded_at']==r['known_from'] and (r['known_to'] is None or r['known_from']<r['known_to']),'staff knowledge ordering differs')
                self.need(r['planned_start']<r['planned_end'],'empty planned roster interval')
                if r['attendance_status']=='PUBLISHED':
                    self.need(all(Decimal(r[k])==0 for k in ('worked_hours','productive_hours','paid_nonproductive_hours','unpaid_break_hours','overtime_hours','loaded_cost')),'advance roster leaks actual hours/cost')
                    self.need(r['actual_end'] is None and (r['actual_start'] is None or r['actual_start']<=r['known_from']<CUTOFF),'advance roster leaks actual attendance')
                    worker=self.workers[r['worker_assignment_id']]
                    self.need(contains(worker,r['actual_start'] or r['planned_start'],r['known_from'],availability=False),'published roster references a future/invalid source assignment')
                if r['attendance_status']=='WORKED':self.need(r['actual_end'] is not None and r['actual_end']<=r['known_from'] and r['actual_end']<=CUTOFF,'future or missing actual attendance completion')
        self.metrics.update(shift_blocks=len(self.latest),shift_versions=len(self.t['staff_shift']),retained_initial_publications=sum(r['attendance_status']=='PUBLISHED' and r['actual_start'] is None for r in self.t['staff_shift']),cancelled_forecast_slots=sum(r['attendance_status']=='CANCELLED' for r in self.latest.values()),
            absent_blocks=sum(r['attendance_status']=='ABSENT' for r in self.latest.values()),
            february_absences=sum(r['attendance_status']=='ABSENT' and timestamp(r['planned_start']).astimezone(ZONE).strftime('%Y-%m')=='2025-02' for r in self.latest.values()),
            agency_replacements=sum(r['source_record_id'].startswith('replace/') and self.workers[r['worker_assignment_id']]['worker_type']=='AGENCY' for r in self.latest.values()))

    def check_labor_time(self):
        physical=defaultdict(list);weekly=defaultdict(Decimal)
        for r in self.t['staff_shift']:
            fields=[Decimal(r[k]) for k in ('worked_hours','productive_hours','paid_nonproductive_hours','unpaid_break_hours','overtime_hours')]
            self.need(all(x>=0 for x in fields),'negative labor-hour component')
            worked,productive,nonproductive,unpaid,overtime=fields
            self.need(worked==productive+nonproductive+unpaid,'worked/productive/break hours do not reconcile')
            self.need(overtime<=worked-unpaid,'overtime exceeds paid hours or is added twice')
            if r['attendance_status']=='WORKED':
                self.need(r['shift_type']=='WORK' and r['actual_start']<r['actual_end'] and worked==hours(r['actual_start'],r['actual_end']).quantize(Decimal('.000001')),'elapsed attendance hours differ')
                self.need(worked<=Decimal(self.cfg['maximum_shift_hours']),'maximum worked shift exceeded')
            elif r['attendance_status'] in ('ABSENT','CANCELLED','ON_LEAVE'):
                self.need(worked==0 and r['actual_start'] is None and r['actual_end'] is None,'leave/absence/cancellation creates attendance')
        for r in self.working:
            worker=self.workers[r['worker_assignment_id']];wid=worker['worker_id'];end=r['actual_end'] or CUTOFF
            physical[wid].append((r['actual_start'],end))
            for week,h in local_weeks(r['actual_start'],end):weekly[wid,week]+=h
            for at in (r['actual_start'],(timestamp(end)-timedelta(seconds=1)).isoformat().replace('+00:00','Z')):
                current=asof_worker(self.worker_hist[wid],at,r['known_from']);day=timestamp(at).astimezone(ZONE).date().isoformat()
                self.need(current['hire_date']<=day and (current['termination_date'] is None or day<current['termination_date']) and current['credential_valid_from']<=day<current['credential_valid_to'],'worked outside employment/credential validity')
            self.need(self.locations[r['location_id']]['facility_id']==worker['facility_id'],'worked responsibility belongs to another employer')
            if worker['role']=='RN':
                scope=self.locations[r['location_id']]['location_code'];allowed={'ICU':{'Critical Care Nursing'},'ED':{'Emergency Nursing','Critical Care Nursing'},'ACUTE':{'Medical-Surgical Nursing','Emergency Nursing','Critical Care Nursing'},'OR':{'Medical-Surgical Nursing'}}
                self.need(scope in allowed and worker['specialty'] in allowed[scope],'RN worked outside the reviewed unit skill mix')
        for intervals in physical.values():
            ordered=sorted(intervals)
            for left,right in zip(ordered,ordered[1:]):self.need(hours(left[1],right[0])>=Decimal(self.cfg['minimum_rest_hours']),'overlapping worked intervals or insufficient rest')
        self.need(all(h<=Decimal(self.cfg['maximum_weekly_hours']) for h in weekly.values()),'maximum weekly worked hours exceeded')
        for r in self.latest.values():
            if r['attendance_status'] not in ('ABSENT','ON_LEAVE'):continue
            wid=self.workers[r['worker_assignment_id']]['worker_id']
            self.need(not any(a<r['planned_end'] and r['planned_start']<b for a,b in physical[wid]),'worked during recorded absence or leave')
        self.metrics['worked_elapsed_hours']=str(sum((Decimal(r['worked_hours']) for r in self.latest.values()),Decimal(0)))
        self.metrics['open_attendance_blocks']=sum(r['actual_start'] is not None and r['actual_end'] is None for r in self.latest.values())

    def check_labor_cost(self):
        weekly=defaultdict(Decimal);overtime={};cost=Decimal(0);by_type=defaultdict(Decimal)
        for r in sorted(self.latest.values(),key=lambda r:(r['actual_start'] or r['planned_start'],r['source_record_id'])):
            worker=self.workers[r['worker_assignment_id']];wid=worker['worker_id'];paid=Decimal(r['worked_hours'])-Decimal(r['unpaid_break_hours']);expected=Decimal(0)
            if r['attendance_status']=='WORKED':
                parts=list(local_weeks(r['actual_start'],r['actual_end']));total=sum((v for _,v in parts),Decimal(0));allocated=Decimal(0)
                for i,(week,elapsed) in enumerate(parts):
                    part=paid-allocated if i==len(parts)-1 else (paid*elapsed/total).quantize(Decimal('.000001'))
                    allocated+=part
                    expected+=max(Decimal(0),weekly[wid,week]+part-40)-max(Decimal(0),weekly[wid,week]-40);weekly[wid,week]+=part
            self.need(Decimal(r['overtime_hours'])==expected,'weekly paid overtime classification differs')
            overtime[r['shift_id']]=expected
            cost+=Decimal(r['loaded_cost']);by_type[worker['worker_type']]+=Decimal(r['loaded_cost'])
        for r in self.t['staff_shift']:
            worker=self.workers[r['worker_assignment_id']];rate=Decimal(worker['hourly_cost_rate'])
            self.need(r['currency']==worker['currency']=='USD','resource labor currency is not USD')
            paid=Decimal(r['worked_hours'])-Decimal(r['unpaid_break_hours']);premium=Decimal('.5') if worker['worker_type']=='EMPLOYEE' and worker['role']!='PHYSICIAN' else Decimal(0)
            if r['attendance_status']=='ON_LEAVE':expected=rate*min(Decimal(8),hours(r['planned_start'],r['planned_end']))
            else:expected=(paid+Decimal(r['overtime_hours'])*premium)*rate
            self.need(Decimal(r['loaded_cost'])==expected.quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'untraceable labor rate/premium/leave cost')
            if r['actual_start']:
                source=asof_worker(self.worker_hist[worker['worker_id']],r['actual_start'],r['known_from'])
                self.need(source['worker_assignment_id']==r['worker_assignment_id'],'attendance references superseded/future rate snapshot')
        rate_revisions=sum(any(a['attendance_status']==b['attendance_status']=='WORKED' and self.workers[a['worker_assignment_id']]['worker_id']==self.workers[b['worker_assignment_id']]['worker_id'] and a['worker_assignment_id']!=b['worker_assignment_id'] and a['loaded_cost']!=b['loaded_cost'] for a,b in zip(sorted(rows,key=lambda r:r['revision_no']),sorted(rows,key=lambda r:r['revision_no'])[1:])) for rows in self.histories.values())
        attendance_revisions=sum(any(a['attendance_status']==b['attendance_status']=='WORKED' and a['productive_hours']!=b['productive_hours'] for a,b in zip(sorted(rows,key=lambda r:r['revision_no']),sorted(rows,key=lambda r:r['revision_no'])[1:])) for rows in self.histories.values())
        self.metrics.update(finalized_labor_cost=str(cost),labor_cost_by_contract={k:str(v) for k,v in by_type.items()},overtime_hours=str(sum(overtime.values(),Decimal(0))),late_rate_revisions=rate_revisions,late_attendance_revisions=attendance_revisions)

    def check_activity_links(self):
        by_day=defaultdict(list);or_nurses=defaultdict(list)
        for r in self.working:
            worker=self.workers[r['worker_assignment_id']];a,b=timestamp(r['actual_start']),timestamp(r['actual_end'] or CUTOFF);day=a.astimezone(ZONE).date()
            while day<=b.astimezone(ZONE).date():
                by_day[worker['worker_id'],day.isoformat()].append(r)
                if worker['role']=='RN' and self.locations[r['location_id']]['location_code']=='OR':or_nurses[worker['facility_id'],day.isoformat()].append(r)
                day+=timedelta(days=1)
        operations=defaultdict(list);rn_count=0;scopes=defaultdict(list);operative_events=[]
        for bed,eid,a,b in bed_intervals(self.t['bed_event'],self.enc):scopes[eid].append((a,b,'ICU' if self.locations[bed]['service_line']=='ICU' else 'ACUTE'))
        for event in self.t['clinical_event']:
            if event['occurred_at']<START:continue
            at=event['occurred_at'];worker=self.workers[event['author_assignment_id']];wid=worker['worker_id'];day=timestamp(at).astimezone(ZONE).date().isoformat()
            operative=event['event_type']=='PROCEDURE' and self.catalog[event['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9')
            found=[s for s in by_day[wid,day] if s['actual_start']<=at<(s['actual_end'] or CUTOFF) and (not operative or event['period_end_at']<=(s['actual_end'] or CUTOFF))]
            self.need(bool(found),'clinical author has no actual working coverage: '+event['clinical_event_version_id']+' '+event['event_type']+' '+at)
            if worker['role']=='RN':
                e=self.enc[event['encounter_version_id']]
                scope=next((unit for a,b,unit in scopes[e['encounter_id']] if a<=at<b),'ED' if e['encounter_class']=='ED' or e['admission_source']=='ED' else 'ACUTE')
                self.need(any(self.locations[s['location_id']]['location_code']==scope for s in found),'RN event belongs to a different worked clinical scope')
            if event['event_type']=='MED_ADMIN':self.need(worker['role']=='RN','administration lacks modeled RN source performer');rn_count+=1
            if event['event_type']=='PROCEDURE' and self.catalog[event['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9'):
                specialty='General Surgery' if self.catalog[event['catalog_item_id']]['code']=='0FT44ZZ' else 'Orthopedics'
                self.need(worker['role']=='PHYSICIAN' and worker['specialty']==specialty,'operative author lacks the required surgery specialty')
                operations[wid].append((at,event['period_end_at']))
                fid=self.enc[event['encounter_version_id']]['facility_id']
                operative_events.append((fid,at,event['period_end_at']))
                nurses=[s for s in or_nurses[fid,day]
                    if s['actual_start']<=at and event['period_end_at']<=(s['actual_end'] or CUTOFF)]
                self.need(bool(nurses),'operative case has no actual circulating-RN coverage')
        for intervals in operations.values():
            for a,b in zip(sorted(intervals),sorted(intervals)[1:]):self.need(a[1]<=b[0],'one surgeon performs overlapping operations')
        for fid in {x[0] for x in operative_events}:
            cases=[x for x in operative_events if x[0]==fid]
            for at in {x[1] for x in cases}:
                active=sum(a<=at<b for _,a,b in cases);day=timestamp(at).astimezone(ZONE).date().isoformat()
                present={self.workers[s['worker_assignment_id']]['worker_id'] for s in or_nurses[fid,day] if s['actual_start']<=at<(s['actual_end'] or CUTOFF)}
                self.need(active<=len(present) and active<=self.cfg['operative_concurrency'],'concurrent operative cases exceed actual circulating RN/capacity')
        self.metrics['rn_authored_medication_events']=rn_count

    def check_coverage(self):
        # Integrate actual bed intervals into each local roster period. This is a
        # separate retrospective requirement oracle, not the shift-start planner.
        demand=defaultdict(Decimal);supply=defaultdict(Decimal)
        for bed,eid,a,b in bed_intervals(self.t['bed_event'],self.enc):
            location=self.locations[bed];scope='ICU' if location['service_line']=='ICU' else 'ACUTE';e=self.enc_latest[eid]
            cursor=timestamp(a);end=timestamp(b)
            weight=Decimal(self.cfg['acuity_weights'][str(e['initial_acuity'])])
            while cursor<end:
                local=cursor.astimezone(ZONE);day=local.date();hour=7 if local.hour<7 else 19 if local.hour<19 else 7
                next_day=day+timedelta(days=1) if local.hour>=19 else day
                boundary=datetime.combine(next_day,datetime.min.time(),tzinfo=ZONE).replace(hour=hour).astimezone(timezone.utc)
                stop=min(end,boundary);period_day=day-timedelta(days=1) if local.hour<7 else day;period_hour=19 if local.hour<7 or local.hour>=19 else 7
                demand[location['facility_id'],scope,period_day.isoformat(),period_hour]+=Decimal(int((stop-cursor).total_seconds()))/86400*Decimal(self.cfg['rn_hours_per_patient_day'])*weight
                cursor=stop
        periods=defaultdict(Decimal)
        day=timestamp(START).astimezone(ZONE).date()-timedelta(days=1)
        sites=[r['facility_id'] for r in self.t['facility']]
        while day<timestamp(CUTOFF).astimezone(ZONE).date():
            for hour in (7,19):
                a=datetime.combine(day,datetime.min.time(),tzinfo=ZONE).replace(hour=hour).astimezone(timezone.utc)
                b=datetime.combine(day+timedelta(days=hour==19),datetime.min.time(),tzinfo=ZONE).replace(hour=7 if hour==19 else 19).astimezone(timezone.utc)
                clip=max(timestamp(START),a);stop=min(timestamp(CUTOFF),b)
                if clip>=stop:continue
                minimum=(Decimal(int((b-a).total_seconds()))/HOUR-Decimal('1.25'))*Decimal(int((stop-clip).total_seconds()))/Decimal(int((b-a).total_seconds()))
                month=clip.astimezone(ZONE).strftime('%Y-%m')
                for fid in sites:
                    for scope in ('ACUTE','ICU','ED'):periods[month]+=max(minimum,demand[fid,scope,day.isoformat(),hour])
            day+=timedelta(days=1)
        for r in self.latest.values():
            w=self.workers[r['worker_assignment_id']]
            if w['role']!='RN' or r['attendance_status']!='WORKED' or self.locations[r['location_id']]['location_code'] not in ('ACUTE','ICU','ED'):continue
            a,b=timestamp(r['actual_start']),timestamp(r['actual_end']);cursor=max(a,timestamp(START));end=min(b,timestamp(CUTOFF))
            while cursor<end:
                local=cursor.astimezone(ZONE);year,month=(local.year+1,1) if local.month==12 else (local.year,local.month+1)
                boundary=datetime(year,month,1,tzinfo=ZONE).astimezone(timezone.utc);stop=min(end,boundary)
                supply[local.strftime('%Y-%m')]+=Decimal(r['productive_hours'])*Decimal(int((stop-cursor).total_seconds()))/Decimal(int((b-a).total_seconds()));cursor=stop
        ratios={m:supply[m]/need for m,need in sorted(periods.items())}
        lo,hi=map(Decimal,self.cfg['targets']['monthly_rn_coverage'])
        self.need(len(ratios)==36 and all(lo<=ratio<=hi for ratio in ratios.values()),'monthly RN productive coverage target missed: '+str({m:str(v) for m,v in ratios.items() if not lo<=v<=hi}))
        self.metrics.update(monthly_rn_coverage={m:str(v) for m,v in ratios.items()},rn_required_hours=str(sum(periods.values(),Decimal(0))),rn_productive_hours=str(sum(supply.values(),Decimal(0))))

    def check_budget(self):
        specs={t['name']:t for t in self.schema['tables']};total=sum(map(len,self.t.values()))
        self.need(len(self.t)==18 and len(specs)==25 and total<=1958210,'resource table/aggregate budget differs')
        for name,rows in self.t.items():
            self.need(len(rows)<=specs[name]['planned_rows'],'frozen table budget exceeded: '+name)
            self.need(not any(isinstance(v,(dict,list)) for r in rows for v in r.values()),'nested uncounted resource facts')
        self.metrics.update(business_rows=total,rows_by_table={k:len(v) for k,v in self.t.items()},remaining_planned_rows=1958210-total,reserve_rows=41790)

    def run(self):
        checks=[]
        for name in ('SCHEMA_HISTORY','LABOR_TIME','LABOR_COST','ACTIVITY_LINKS','COVERAGE','BUDGET'):
            try:getattr(self,'check_'+name.lower())();checks.append({'rule_id':name,'status':'PASS'})
            except Exception as exc:checks.append({'rule_id':name,'status':'FAIL','reason':str(exc)})
        return {'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'BLOCKED','checks':checks,
            'defects':[c for c in checks if c['status']=='FAIL'],'metrics':self.metrics}
