"""Independent admission/day/bed responsibility oracle for room billing."""
from collections import defaultdict
from datetime import date,timedelta
from decimal import Decimal

from .core import instant
from .financial_oracles import day,local,stamp
from .operational_validation import bed_intervals


def room_scope(tables):
    enc={r['encounter_version_id']:r for r in tables['encounter']};latest={}
    for e in enc.values():
        if e['encounter_id'] not in latest or e['revision_no']>latest[e['encounter_id']]['revision_no']:latest[e['encounter_id']]=e
    loc={r['location_id']:r for r in tables['location']};coverage={r['coverage_version_id']:r for r in tables['patient_coverage']};payer={r['payer_plan_id']:r for r in tables['payer_plan']}
    intervals=defaultdict(list)
    for bid,eid,a,z in bed_intervals(tables['bed_event'],enc):intervals[eid].append((instant(a),instant(z),bid))
    source={r['bed_event_id']:r for r in tables['bed_event']};knowledge=defaultdict(list);carry=set()
    for r in source.values():
        if r['event_type']=='OPENING' and r['occupancy_state']=='OCCUPIED' and r['encounter_version_id']:carry.add(enc[r['encounter_version_id']]['encounter_id'])
        original=source.get(r['corrects_bed_event_id']) if r['corrects_bed_event_id'] else r
        if original and original['event_type'] in ('OPENING','OCCUPY','VACATE') and original['encounter_version_id']:
            knowledge[enc[original['encounter_version_id']]['encounter_id']].append((r['effective_at'],r['export_available_at']))
    result={}
    for eid,e in latest.items():
        if e['encounter_class']!='IPD':continue
        opening=bool(e['discharged_at'] and e['discharged_at']<'2023-01-01T06:00:00Z')
        if opening and payer[coverage[e['coverage_version_id']]['payer_plan_id']]['payer_type']=='SELF_PAY':continue
        if not opening and not intervals[eid]:continue
        admitted=instant(e['admitted_at']) if opening else min(a for a,z,b in intervals[eid])
        end=(instant(e['discharged_at']) if e['discharged_at'] else instant('2026-01-01T06:00:00Z')) if opening else max(z for a,z,b in intervals[eid])
        first=day(admitted) if opening else max(day(admitted),day('2023-01-01T06:00:00Z'))
        exclusive=day(end)+(timedelta(days=1) if day(end)==day(admitted) and eid not in carry else timedelta(0));d=first;keys=[]
        while d<exclusive and str(d)<'2026-01-01':
            point=max(admitted,local(d));beds=[bid for a,z,bid in intervals[eid] if a<=point<z]
            if not opening and not beds:
                candidates=sorted((a,bid) for a,z,bid in intervals[eid] if a<local(d+timedelta(days=1)) and z>local(d))
                if candidates:beds=[candidates[0][1]]
                else:d+=timedelta(days=1);continue
            where=loc[beds[0]] if beds else loc[e['location_id']];code='BILL-ICU' if where['service_line']=='ICU' else 'BILL-ROOM'
            key=(eid,where['cost_center_id'],str(d)[:7],code)
            if key not in result:result[key]={'units':Decimal(0),'first':str(d),'last':str(d),'known':''};keys.append(key)
            v=result[key];v['units']+=1;v['first']=min(v['first'],str(d));v['last']=max(v['last'],str(d));d+=timedelta(days=1)
        for key in keys:
            v=result[key];completed=min(end,local(date.fromisoformat(v['last'])+timedelta(days=1)))
            v['known']=max((available for effective,available in knowledge[eid] if effective<=stamp(completed)),default=stamp(completed))
    return result


def holding_scope(tables,cfg):
    enc={r['encounter_version_id']:r for r in tables['encounter']};latest={};placed=defaultdict(list)
    for e in enc.values():
        if e['encounter_id'] not in latest or e['revision_no']>latest[e['encounter_id']]['revision_no']:latest[e['encounter_id']]=e
    for bid,eid,a,z in bed_intervals(tables['bed_event'],enc):placed[eid].append(instant(a))
    centers={(r['facility_id'],r['cost_center_code'].split('-')[-1]):r['cost_center_id'] for r in tables['cost_center']}
    source={r['bed_event_id']:r for r in tables['bed_event']};knowledge=defaultdict(list)
    for r in source.values():
        original=source.get(r['corrects_bed_event_id']) if r['corrects_bed_event_id'] else r
        if original and original['event_type'] in ('OPENING','OCCUPY','VACATE') and original['encounter_version_id']:
            knowledge[enc[original['encounter_version_id']]['encounter_id']].append((r['effective_at'],r['export_available_at']))
    result={};start=instant('2023-01-01T06:00:00Z');cutoff=instant('2026-01-01T06:00:00Z')
    for eid,e in latest.items():
        if e['encounter_class']!='IPD' or e['discharged_at'] and e['discharged_at']<stamp(start):continue
        end=min(cutoff,instant(e['discharged_at'])) if e['discharged_at'] else cutoff
        if placed[eid]:end=min(end,min(placed[eid]))
        begin=max(start,instant(e['admitted_at'])+timedelta(seconds=int(Decimal(cfg['holding_bundled_hours'])*3600)))
        if begin>=end:continue
        segments=[];cursor=begin
        while cursor<end:
            d=day(cursor);following=(d.replace(day=28)+timedelta(days=4)).replace(day=1)
            boundary=min(end,local(following));segments.append((cursor,boundary));cursor=boundary
        total=(Decimal(str((end-begin).total_seconds()))/3600).quantize(Decimal('.000001'));remaining=total
        for i,(a,z) in enumerate(segments):
            units=remaining if i==len(segments)-1 else (Decimal(str((z-a).total_seconds()))/3600).quantize(Decimal('.000001'));remaining-=units
            cc=centers[e['facility_id'],'ED' if e['admission_source']=='ED' else 'MEDICINE'];first=str(day(a));last=str(day(z-timedelta(seconds=1)))
            known=max((available for effective,available in knowledge[eid] if effective<=stamp(z)),default=stamp(z))
            if not placed[eid] and e['discharged_at']:known=max(known,e['export_available_at'])
            result[eid,cc,first[:7]]={'units':units,'first':first,'last':last,'known':known}
    return result
