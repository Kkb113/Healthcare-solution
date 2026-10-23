"""Independent lot ledgers, point-of-use eligibility and resource response oracle."""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict,Counter
from datetime import timedelta
from decimal import Decimal,ROUND_HALF_UP
from zoneinfo import ZoneInfo

from .master_validation import timestamp

ZONE=ZoneInfo('America/Chicago');START='2023-01-01T06:00:00Z';CUTOFF='2026-01-01T06:00:00Z'


def key(namespace,*parts):
    raw=json.dumps([namespace,*parts],sort_keys=True,ensure_ascii=False,separators=(',',':'))
    return namespace+'_'+hashlib.sha256(raw.encode()).hexdigest()[:32]


def expected_uses(tables):
    """Reconstruct scalar requirements independently of the generation allocator."""
    catalog={r['catalog_item_id']:r for r in tables['catalog_item']};code_ids={r['code']:r['catalog_item_id'] for r in tables['catalog_item']}
    encounters={r['encounter_version_id']:r for r in tables['encounter']};locations={(r['facility_id'],r['location_code']):r['location_id'] for r in tables['location']}
    specimens={};uses=[]
    for r in tables['clinical_event']:
        if r['status']!='COMPLETED' or not START<=r['occurred_at']<CUTOFF:continue
        fid=encounters[r['encounter_version_id']]['facility_id'];items=[];scope=None;at=r['occurred_at']
        if r['event_type'] in ('MED_ADMIN','MED_DISPENSE'):
            items=[(catalog[r['catalog_item_id']]['code'],Decimal(r['consumed_base_quantity']))];scope='PHARM'
        elif r['event_type']=='LAB_RESULT':
            candidate=(r['occurred_at'],r['clinical_event_version_id'],r)
            if r['specimen_id'] not in specimens or candidate[:2]<specimens[r['specimen_id']][:2]:specimens[r['specimen_id']]=candidate
        elif r['event_type']=='PROCEDURE' and catalog[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9'):
            items=[('SUP-033',Decimal(1)),('SUP-013',Decimal(2))];scope='OR'
        elif r['source_record_id'].endswith('/placement-assessment'):
            items=[('SUP-015',Decimal(1))];scope='SUPPORT'
        for code,qty in items:uses.append((at,r['clinical_event_version_id'],locations[fid,scope],code,code_ids[code],qty,r['event_type'] in ('MED_ADMIN','MED_DISPENSE'),r['consumption_group_key']))
    for _,_,r in specimens.values():
        fid=encounters[r['encounter_version_id']]['facility_id']
        for code,qty in [('SUP-025',Decimal(1)),('SUP-035',Decimal(1)),('SUP-013',Decimal(2))]:
            uses.append((r['collected_at'],r['clinical_event_version_id'],locations[fid,'DIAG'],code,code_ids[code],qty,False,None))
    return sorted(uses,key=lambda x:(x[0],x[1],x[3]))


class StockValidator:
    def __init__(self,tables,cfg,parent=None):
        self.t,self.cfg,self.parent=tables,cfg,parent
        self.rows=tables['inventory_movement'];self.by_id={r['movement_id']:r for r in self.rows}
        self.catalog={r['catalog_item_id']:r for r in tables['catalog_item']};self.locations={r['location_id']:r for r in tables['location']}
        self.enc={r['encounter_version_id']:r for r in tables['encounter']};self.events={r['clinical_event_version_id']:r for r in tables['clinical_event']}
        self.metrics={};self.lots={};self.uses=None

    def need(self,ok,message):
        if not ok:raise ValueError(message)

    def check_ledger(self):
        values=defaultdict(Decimal);quantities=defaultdict(Decimal);transfers=defaultdict(list);by_kind=defaultdict(Decimal);provenance=set()
        for r in self.rows:
            qty=Decimal(r['quantity_base']);price=Decimal(r['unit_cost']);cost=Decimal(r['extended_cost']);cat=self.catalog[r['catalog_item_id']]
            self.need(cat['domain'] in ('MEDICATION','SUPPLY') and qty!=0 and price>0,'invalid stock item/quantity/unit cost')
            self.need(r['currency']=='USD' and Decimal(r['nonpatient_waste_base'])>=0,'invalid resource currency or negative waste')
            self.need(r['movement_type']=='CONSUME' or Decimal(r['nonpatient_waste_base'])==0,'non-consumption row misclassifies patient waste')
            self.need(cost==(qty*price).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'untraceable inventory extended cost')
            self.need(START<=r['occurred_at']<CUTOFF and r['occurred_at']<=r['recorded_at']<=r['export_available_at']<='2026-01-10T23:59:59Z','inventory occurrence/record/export/window differs')
            signature=(r['catalog_item_id'],r['unit_cost'],r['expires_on'])
            self.need(r['lot_id'] not in self.lots or self.lots[r['lot_id']]==signature,'lot price/item/expiry changed during transfer/return')
            self.lots[r['lot_id']]=signature
            if r['movement_type'] in ('OPENING','RECEIPT'):
                provenance.add(r['lot_id']);day=timestamp(r['occurred_at']).astimezone(ZONE);quarter=max(0,(day.year-2023)*4+(day.month-1)//3)
                expected=(Decimal(self.cfg['inventory_products'][cat['code']]['base_unit_price'])*(1+quarter*Decimal(self.cfg['quarterly_price_escalator']))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
                self.need(price==expected,'receipt/opening price differs from the declared supplier contract')
                if r['movement_type']=='RECEIPT':self.need(qty%Decimal(cat['pack_to_base_factor'])==0,'receipt pack/base conversion differs')
            grain=(r['location_id'],r['catalog_item_id'],r['lot_id']);quantities[grain]+=qty;values[grain]+=cost;by_kind[r['movement_type']]+=cost
            positive=r['movement_type'] in ('OPENING','RECEIPT','RETURN','TRANSFER_IN')
            self.need(qty>0 if positive else qty<0 if r['movement_type'] in ('CONSUME','TRANSFER_OUT','EXPIRE') else True,'movement sign differs from type')
            if r['transfer_group_id']:transfers[r['transfer_group_id']].append(r)
            if r['reverses_movement_id']:
                original=self.by_id.get(r['reverses_movement_id'])
                self.need(original is not None and original['movement_id']!=r['movement_id'] and original['recorded_at']<r['recorded_at'],'orphan or anticipatory inventory reversal')
                self.need(all(r[f]==original[f] for f in ('location_id','catalog_item_id','lot_id','unit_cost','expires_on','occurred_at')) and qty==-Decimal(original['quantity_base']) and cost==-Decimal(original['extended_cost']),'reversal does not preserve original quantity/value/context')
        self.need(set(self.lots)==provenance,'lot has no traceable opening/receipt valuation')
        for group,rows in transfers.items():
            self.need(sum((Decimal(r['quantity_base']) for r in rows),Decimal(0))==0 and sum((Decimal(r['extended_cost']) for r in rows),Decimal(0))==0,'unbalanced stock transfer/return')
            self.need(len({r['location_id'] for r in rows})==2 and len({r['catalog_item_id'] for r in rows})==1 and len({r['occurred_at'] for r in rows})==1,'stock transfer pairing grain differs')
        for grain,qty in quantities.items():
            price=Decimal(self.lots[grain[2]][1]);self.need(qty>=0,'negative closing lot/location balance')
            self.need(values[grain]==(qty*price).quantize(Decimal('.01')),'stock quantity/value roll-forward differs')
        self.metrics.update(stock_movements=len(self.rows),stock_lots=len(self.lots),closing_inventory_value=str(sum(values.values(),Decimal(0))),
            patient_consumption_cost=str(-sum((Decimal(r['extended_cost']) for r in self.rows if r['movement_type']=='CONSUME' and Decimal(r['nonpatient_waste_base'])==0),Decimal(0))),
            nonpatient_consumption_cost=str(-sum((Decimal(r['extended_cost']) for r in self.rows if r['movement_type']=='CONSUME' and Decimal(r['nonpatient_waste_base'])>0),Decimal(0))),
            cost_inputs_by_movement={k:str(v) for k,v in by_kind.items()},transfer_groups=len(transfers),expiry_movements=sum(r['movement_type']=='EXPIRE' for r in self.rows),
            unopened_return_groups=sum(any(r['movement_type']=='RETURN' for r in rows) for rows in transfers.values()),
            independent_closing_quantity_sha256=hashlib.sha256(json.dumps(sorted([list(k)+[str(v)] for k,v in quantities.items()]),separators=(',',':')).encode()).hexdigest())
        self.book_closing=quantities

    def check_eligibility_links(self):
        self.uses=expected_uses(self.t)
        lotmeta={r['lot_id']:(r['catalog_item_id'],r['expires_on'],Decimal(r['unit_cost'])) for r in self.rows}
        physical=defaultdict(Decimal);stock_index=defaultdict(set);groups=defaultdict(Decimal);group_meta={};agenda=[]
        for r in self.rows:
            if r['movement_type']=='CONSUME' and Decimal(r['nonpatient_waste_base'])==0:continue
            priority=0 if r['movement_type'] in ('OPENING','RECEIPT','EXPIRE','ADJUSTMENT') else 10 if r['movement_type']=='TRANSFER_OUT' else 20
            identifier=r['source_record_id']
            if r['movement_type']=='CONSUME':
                priority=30;identifier=r['source_record_id'].removeprefix('nonpatient-waste/')+'/'+self.catalog[r['catalog_item_id']]['code']+'~waste'
            agenda.append((r['occurred_at'],priority,identifier,'movement',r))
        for use in self.uses:agenda.append((use[0],30,use[1]+'/'+use[3],'clinical',use))
        probes=set();unit_ids={(r['facility_id'],r['location_code']):r['location_id'] for r in self.t['location']}
        drape=next(r['catalog_item_id'] for r in self.t['catalog_item'] if r['code']=='SUP-033')
        for r in self.t['clinical_event']:
            if r['source_record_id'].endswith('/resource-response') and 'Cause: UNIT_STOCKOUT.' in r['text_value']:
                planned=r['text_value'].split('planned ')[1].split(';')[0];fid=self.enc[r['encounter_version_id']]['facility_id'];probe=(fid,planned)
                required=(timestamp(planned)-timedelta(minutes=5)).isoformat().replace('+00:00','Z')
                if probe not in probes:agenda.append((required,25,'probe/'+fid,'probe',(unit_ids[fid,'OR'],drape)));probes.add(probe)
        for at,priority,identifier,kind,value in sorted(agenda,key=lambda x:x[:3]):
            day=timestamp(at).astimezone(ZONE).date().isoformat()
            if kind=='probe':
                location,item=value
                self.need(sum((physical[location,item,lot] for lot in stock_index[location,item] if lotmeta[lot][1]>day),Decimal(0))==0,'declared stockout has eligible stock at the planned service time')
                continue
            if kind=='movement':
                r=value;grain=(r['location_id'],r['catalog_item_id'],r['lot_id']);qty=Decimal(r['quantity_base'])
                if qty<0:self.need(physical[grain]>=-qty,'negative stock or issue before receipt at '+at)
                if r['movement_type'] in ('TRANSFER_OUT','CONSUME'):
                    self.need(day<r['expires_on'],'expired lot issued/transferred')
                if r['movement_type']=='EXPIRE':self.need(day==r['expires_on'] and -qty==physical[grain],'expiry time/remaining quantity differs')
                if r['movement_type']=='CONSUME':
                    self.need(-qty==Decimal(r['nonpatient_waste_base']) and r['source_record_id'].startswith('nonpatient-waste/'),'unclassified nonpatient stock issue')
                physical[grain]+=qty;stock_index[grain[:2]].add(grain[2])
            else:
                when,eid,loc,code,item,quantity,medication,link=value;remaining=quantity
                eligible=sorted((lotmeta[lot][1],lot) for lot in stock_index[loc,item] if lotmeta[lot][1]>day
                    and physical[loc,item,lot]>0 and (not medication or physical[loc,item,lot]>=quantity))
                used=[]
                for expiry,lot in eligible:
                    q=min(remaining,physical[loc,item,lot]);physical[loc,item,lot]-=q;remaining-=q
                    group=key('consumption',loc,code,lot,day);groups[group]+=q;group_meta[group]=(loc,item,lot)
                    used.append(group)
                    if remaining==0:break
                self.need(remaining==0,'clinical use before eligible receipt/after expiry/stockout: '+eid)
                if medication:self.need(len(used)==1 and link==used[0],'medication lot/group does not follow eligible whole-fill FEFO: '+eid)
        observed={r['consumption_group_key']:r for r in self.rows if r['movement_type']=='CONSUME' and Decimal(r['nonpatient_waste_base'])==0}
        self.need(set(groups)==set(observed),'missing or untraceable patient/supply consumption group')
        for group,qty in groups.items():
            r=observed[group];self.need(-Decimal(r['quantity_base'])==qty and (r['location_id'],r['catalog_item_id'],r['lot_id'])==group_meta[group],'scalar clinical/supply quantity does not reconcile to stock issue')
        for grain,qty in self.book_closing.items():self.need(physical[grain]==qty,'point-of-use and ledger closing balance differs')
        self.metrics.update(actual_medication_links=sum(u[6] for u in self.uses),selected_supply_requirements=sum(not u[6] for u in self.uses),reconciled_patient_consumption_groups=len(groups),
            nonpatient_waste_quantity=str(sum((Decimal(r['nonpatient_waste_base']) for r in self.rows),Decimal(0))),stockout_point_of_use_probes=len(probes),unexplained_negative_stock=0)

    def check_connected_scenarios(self):
        notes=[r for r in self.t['clinical_event'] if r['source_record_id'].endswith('/resource-response')]
        by_logical={r['clinical_event_id']:r for r in self.t['clinical_event']};windows=defaultdict(set);changed=set();max_delay=Decimal(0)
        for r in notes:
            m=re.match(r'Resource coordination for procedure (\S+): planned (\S+); resource ready (\S+); observed start (\S+)\. Cause: ([A-Z_]+)\. Care remains within the observed encounter; later outcome is not asserted\.',r['text_value'])
            self.need(m is not None,'resource response grammar differs');p=by_logical[m[1]];fid=self.enc[p['encounter_version_id']]['facility_id'];day=timestamp(m[2]).astimezone(ZONE).date().isoformat()
            delay=Decimal(int((timestamp(m[4])-timestamp(m[2])).total_seconds()))/60;max_delay=max(max_delay,delay)
            self.need(delay>0 and m[3]<=m[4]==p['occurred_at'],'resource response has no connected service effect')
            windows[m[5]].add((fid,day));changed.add(p['clinical_event_version_id'])
            if m[5]=='UNIT_STOCKOUT':
                carts=[x for x in self.rows if x['source_record_id'].startswith('case-cart/'+p['clinical_event_version_id']+'/SUP-033/in/')]
                required=(timestamp(m[2])-timedelta(minutes=5)).isoformat().replace('+00:00','Z')
                self.need(bool(carts) and all(required<x['occurred_at']<=m[4] for x in carts),'stockout lacks a delayed actual case-cart arrival')
        self.need(len(windows['UNIT_STOCKOUT'])==self.cfg['stockout_cases'] and len(windows['CIRCULATING_RN_ABSENCE'])==self.cfg['operative_absence_cases'],'configured connected shortage windows missing')
        if self.parent is not None:
            self.need(self.t['bed_event']==self.parent['bed_event'],'resource shortage left stale or unexpectedly changed bed history')
            old={r['clinical_event_version_id']:r for r in self.parent['clinical_event']}
            for event in self.t['clinical_event']:
                prior=old.get(event['clinical_event_version_id'])
                if prior is None:continue
                allowed={'author_assignment_id','consumption_group_key','generation_run_id'}
                if event['clinical_event_version_id'] in changed:allowed|={'occurred_at','period_end_at','encounter_version_id','recorded_at','known_from','export_available_at'}
                self.need(all(event[k]==v for k,v in prior.items() if k not in allowed),'unexplained stale/changed downstream clinical fact')
            self.need(set(old)<=set(self.events),'resource integration lost a parent clinical fact')
            parent_enc={r['encounter_version_id']:r for r in self.parent['encounter']}
            for e in self.t['encounter']:
                self.need(all(e[k]==v for k,v in parent_enc[e['encounter_version_id']].items() if k not in ('attending_assignment_id','generation_run_id')),'resource integration changes care timing without coordinated flow regeneration')
        self.metrics.update(stockout_windows=len(windows['UNIT_STOCKOUT']),absence_delay_windows=len(windows['CIRCULATING_RN_ABSENCE']),
            operative_capacity_queue_windows=len(windows['OPERATIVE_CAPACITY_QUEUE']),changed_operative_services=len(changed),maximum_operative_delay_minutes=str(max_delay))

    def run(self):
        checks=[]
        for name in ('LEDGER','ELIGIBILITY_LINKS','CONNECTED_SCENARIOS'):
            try:getattr(self,'check_'+name.lower())();checks.append({'rule_id':'STOCK_'+name,'status':'PASS'})
            except Exception as exc:checks.append({'rule_id':'STOCK_'+name,'status':'FAIL','reason':str(exc)})
        return {'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'BLOCKED','checks':checks,'defects':[c for c in checks if c['status']=='FAIL'],'metrics':self.metrics}
