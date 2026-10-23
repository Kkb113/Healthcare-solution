"""Event-time FEFO stock allocation and counted daily source issue groups."""
from __future__ import annotations

import heapq
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP

from .core import chicago, draw, instant, stable_id
from .resource_generation import START, CUTOFF, ZONE, stamp, local_at, decimal_text, operative_plans, row_builder

# Fictional base-unit supplier prices and prospective planning rates, not external
# market quotations or estimates fitted to future realized demand.
PRODUCTS = ('MED-001','MED-009','MED-012','MED-020','SUP-025','SUP-035','SUP-013','SUP-033','SUP-015','SUP-019')


def clinical_demands(tables):
    """Transient scalar service requirements; no hidden published allocation table."""
    catalog={r['catalog_item_id']:r for r in tables['catalog_item']}
    by_code={r['code']:r for r in tables['catalog_item'] if r['code'] in PRODUCTS}
    enc={r['encounter_version_id']:r for r in tables['encounter']}
    units={(r['facility_id'],r['location_code']):r['location_id'] for r in tables['location']}
    seen=set();tasks=[]
    for r in sorted(tables['clinical_event'],key=lambda r:(r['occurred_at'],r['clinical_event_version_id'])):
        if r['status']!='COMPLETED' or not stamp(START)<=r['occurred_at']<stamp(CUTOFF):continue
        e=enc[r['encounter_version_id']];fid=e['facility_id'];items=[];scope=None
        if r['event_type'] in ('MED_ADMIN','MED_DISPENSE'):
            code=catalog[r['catalog_item_id']]['code'];items=[(code,Decimal(r['consumed_base_quantity']))];scope='PHARM'
        elif r['event_type']=='LAB_RESULT' and r['specimen_id'] not in seen:
            seen.add(r['specimen_id']);scope='DIAG';items=[('SUP-025',Decimal(1)),('SUP-035',Decimal(1)),('SUP-013',Decimal(2))]
        elif r['event_type']=='PROCEDURE' and catalog[r['catalog_item_id']]['code'] in ('0FT44ZZ','0SRC0J9'):
            scope='OR';items=[('SUP-033',Decimal(1)),('SUP-013',Decimal(2))]
        elif r['source_record_id'].endswith('/placement-assessment'):
            scope='SUPPORT';items=[('SUP-015',Decimal(1))]
        for code,qty in items:
            tasks.append({'event_id':r['clinical_event_version_id'],'clinical_event_id':r['clinical_event_id'],
                'at':r['collected_at'] if r['event_type']=='LAB_RESULT' else r['occurred_at'],
                'location_id':units[fid,scope],'catalog_item_id':by_code[code]['catalog_item_id'],
                'code':code,'quantity':qty,'medication':r['event_type'] in ('MED_ADMIN','MED_DISPENSE')})
    return sorted(tasks,key=lambda x:(x['at'],x['event_id'],x['code']))


class InventoryGenerator:
    def __init__(self,tables,cfg,run_id):
        self.t,self.cfg,self.run_id=tables,cfg,run_id;self.builder=row_builder(cfg,run_id);self.zone=ZONE
        self.cat={r['code']:r for r in tables['catalog_item'] if r['code'] in PRODUCTS}
        self.loc={r['location_id']:r for r in tables['location']};self.units={(r['facility_id'],r['location_code']):r for r in tables['location']}
        self.stock=defaultdict(Decimal);self.lots={};self.rows=[];self.groups={};self.med_links={};self.heap=[];self.seq=0
        self.pending=defaultdict(Decimal);self.controls=defaultdict(int);self.return_budget=cfg['return_cases'];self.case_plans=operative_plans(tables)
        self.tasks=clinical_demands(tables)

    def push(self,at,kind,value,priority):
        self.seq+=1;heapq.heappush(self.heap,(at,priority,self.seq,kind,value))

    def price(self,code,at):
        local=at.astimezone(self.zone);quarter=(local.year-2023)*4+(local.month-1)//3
        return (Decimal(self.cfg['inventory_products'][code]['base_unit_price'])*(1+Decimal(max(0,quarter))*Decimal(self.cfg['quarterly_price_escalator']))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)

    def movement(self,key,location,code,lot,kind,at,qty,group=None,waste=Decimal(0),transfer=None,reverse=None,recorded=None):
        meta=self.lots[lot];recorded=recorded or at
        row=self.builder.row('inventory_movement',key,stamp(recorded),movement_id=stable_id('movement',key),location_id=location,
            catalog_item_id=self.cat[code]['catalog_item_id'],lot_id=lot,movement_type=kind,occurred_at=stamp(at),quantity_base=decimal_text(qty),
            unit_cost=decimal_text(meta['price']),extended_cost=format((qty*meta['price']).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'f'),
            expires_on=meta['expiry'],transfer_group_id=transfer,consumption_group_key=group,nonpatient_waste_base=decimal_text(waste),
            reverses_movement_id=reverse,posting_group_key='inventory/'+self.loc[location]['facility_id']+'/'+kind+'/'+at.astimezone(self.zone).date().isoformat(),currency='USD')
        self.rows.append(row);return row

    def new_lot(self,location,code,at,qty,kind='RECEIPT',key=None,expiry=None):
        key=key or f'{kind}/{location}/{code}/{stamp(at)}';lot=stable_id('lot',key)
        self.lots[lot]={'code':code,'price':self.price(code,at),'expiry':expiry or (at.astimezone(self.zone).date()+timedelta(days=self.cfg['shelf_life_days'])).isoformat()}
        self.stock[location,code,lot]+=qty
        self.movement(key,location,code,lot,kind,at,qty)
        expire=local_at(__import__('datetime').date.fromisoformat(self.lots[lot]['expiry']))
        if expire<CUTOFF:self.push(expire,'expire',lot,0)
        return lot

    def available(self,location,code,at):
        day=at.astimezone(self.zone).date().isoformat()
        return sum((q for (loc,c,lot),q in self.stock.items() if loc==location and c==code and self.lots[lot]['expiry']>day),Decimal(0))

    def take(self,location,code,qty,at,whole_fill=False):
        eligible=sorted(((self.lots[lot]['expiry'],lot) for (loc,c,lot),q in self.stock.items()
                         if loc==location and c==code and q>0 and (not whole_fill or q>=qty) and self.lots[lot]['expiry']>at.astimezone(self.zone).date().isoformat()))
        result=[];remaining=qty
        for _,lot in eligible:
            amount=min(remaining,self.stock[location,code,lot])
            if amount:
                self.stock[location,code,lot]-=amount;remaining-=amount;result.append((lot,amount))
            if not remaining:break
        if remaining:raise ValueError(f'unmet eligible stock: {location} {code} {stamp(at)} short {remaining}')
        return result

    def transfer(self,origin,destination,code,qty,at,key,returned=False):
        group=stable_id('stock_transfer',key)
        for i,(lot,amount) in enumerate(self.take(origin,code,qty,at)):
            self.stock[destination,code,lot]+=amount
            self.movement(key+f'/out/{i}',origin,code,lot,'TRANSFER_OUT',at,-amount,transfer=group)
            self.movement(key+f'/in/{i}',destination,code,lot,'RETURN' if returned else 'TRANSFER_IN',at,amount,transfer=group)
        self.controls['unopened_returns' if returned else 'transfer_groups']+=1

    def run(self):
        sites=sorted(r['facility_id'] for r in self.t['facility'])
        # Routine pools use fixed prospective planning inputs. Supply products are
        # held at the appropriate DIAG/SUPPORT source location, then case carts
        # transfer to OR only after the observed order is known.
        pools=[]
        for fid in sites:
            for code in PRODUCTS:
                if code=='SUP-019':continue
                scope='PHARM' if code.startswith('MED') else 'DIAG' if code in ('SUP-025','SUP-035','SUP-013') else 'SUPPORT'
                location=self.units[fid,scope]['location_id'];daily=Decimal(self.cfg['inventory_products'][code]['daily_planning_units'])
                factor=Decimal(self.cat[code]['pack_to_base_factor']);qty=((daily*30/factor).to_integral_value(rounding=ROUND_CEILING))*factor
                self.new_lot(location,code,START,qty,'OPENING');pools.append((location,code,daily))
        for i in range(self.cfg['opening_expiry_lots']):
            fid=sites[i%3];location=self.units[fid,'DIAG']['location_id'];day=START.date().replace(month=2+i//3,day=1)
            self.new_lot(location,'SUP-019',START,Decimal(5+draw(self.cfg['seed'],str(i),'overstock-quantity',upper=21)),
                'OPENING',f'opening/aged-cup/{fid}/{i}',day.isoformat())
        for task in self.tasks:
            if task['code'] in ('SUP-033',) or task['code']=='SUP-013' and self.loc[task['location_id']]['location_code']=='OR':
                # An OR cart is a counted physical transfer, not consumption.
                at=instant(task['at'])-timedelta(minutes=5)
                self.push(at,'cart',task,1)
            self.push(instant(task['at']),'use',task,3)
        day=START.astimezone(self.zone).date()
        while local_at(day)<CUTOFF:
            self.push(local_at(day),'reorder',pools,2);day+=timedelta(days=1)
        while self.heap:
            at,_,_,kind,value=heapq.heappop(self.heap)
            if at>=CUTOFF:continue
            if kind=='reorder':
                for location,code,daily in value:
                    # Expiry is already known on the receipt. Exclude stock that
                    # expires within the delivery lead, before deciding to wait.
                    available=self.available(location,code,at+timedelta(days=self.cfg['procurement_lead_days']))+self.pending[location,code]
                    if available<daily*self.cfg['stock_reorder_days']:
                        factor=Decimal(self.cat[code]['pack_to_base_factor'])
                        qty=((daily*self.cfg['stock_target_days']-available)/factor).to_integral_value(rounding=ROUND_CEILING)*factor
                        if qty>0:
                            self.pending[location,code]+=qty
                            self.push(at+timedelta(days=self.cfg['procurement_lead_days']),'receipt',(location,code,qty),0)
            elif kind=='receipt':
                location,code,qty=value;self.pending[location,code]-=qty;self.new_lot(location,code,at,qty);self.controls['routine_receipts']+=1
            elif kind=='expire':
                lot=value;code=self.lots[lot]['code']
                for (location,c,l),qty in list(self.stock.items()):
                    if l==lot and qty>0:
                        self.stock[location,code,lot]=Decimal(0)
                        self.movement(f'expiry/{location}/{lot}',location,code,lot,'EXPIRE',at,-qty);self.controls['expiry_movements']+=1
            elif kind=='cart':
                task=value;fid=self.loc[task['location_id']]['facility_id'];code=task['code']
                origin=self.units[fid,'DIAG' if code=='SUP-013' else 'SUPPORT']['location_id']
                extra=code=='SUP-033' and self.return_budget>0
                qty=task['quantity']+int(extra)
                self.transfer(origin,task['location_id'],code,qty,at,'case-cart/'+task['event_id']+'/'+code)
                if extra:
                    self.return_budget-=1
                    end=instant(self.case_plans[task['clinical_event_id']]['end'])+timedelta(minutes=5)
                    self.push(end,'return',(task['location_id'],origin,code,Decimal(1),task['event_id']),1)
            elif kind=='return':
                origin,destination,code,qty,eid=value
                self.transfer(origin,destination,code,qty,at,'unopened-return/'+eid,True)
            elif kind=='use':
                task=value;location,code=task['location_id'],task['code']
                allocations=self.take(location,code,task['quantity'],at,task['medication'])
                if task['medication'] and len(allocations)!=1:
                    # A scalar administration has exactly one counted lot group.
                    # Splitting a tablet dose across lots would require another
                    # scalar source line, rather than hiding an allocation array.
                    raise ValueError('medication dose spans lots; scalar source split required')
                for lot,qty in allocations:
                    day=at.astimezone(self.zone).date().isoformat();group=stable_id('consumption',location,code,lot,day)
                    if group not in self.groups:self.groups[group]=dict(location=location,code=code,lot=lot,at=at,quantity=Decimal(0))
                    self.groups[group]['quantity']+=qty;self.groups[group]['at']=max(at,self.groups[group]['at'])
                    if task['medication']:self.med_links[task['event_id']]=group
                    waste=Decimal(2) if code in ('MED-001','MED-020') else Decimal(1)
                    if code.startswith('MED') and draw(self.cfg['seed'],task['event_id'],'nonpatient-unit-waste',upper=2000)==0 and self.stock[location,code,lot]>=waste:
                        self.stock[location,code,lot]-=waste;waste_key='nonpatient-waste/'+task['event_id']
                        self.movement(waste_key,location,code,lot,'CONSUME',at,-waste,group=stable_id('waste_group',waste_key),waste=waste);self.controls['nonpatient_waste_groups']+=1
        for group,g in sorted(self.groups.items()):
            recorded=local_at(g['at'].astimezone(self.zone).date()+timedelta(days=1))+timedelta(hours=1)
            self.movement('daily-issue/'+group,g['location'],g['code'],g['lot'],'CONSUME',g['at'],-g['quantity'],group=group,recorded=recorded)
        # Explicit independently reversible source corrections retain original
        # valuation; they never change a historical lot's receipt price.
        for i in range(self.cfg['cycle_count_corrections']):
            fid=sites[i%3];location=self.units[fid,'PHARM']['location_id'];code='MED-001'
            # Correct a source cycle count at the closing boundary, after all
            # patient use, against a still-positive eligible lot.
            at=CUTOFF-timedelta(seconds=1);lots=sorted(l for (loc,c,l),q in self.stock.items() if loc==location and c==code and q>3 and self.lots[l]['expiry']>'2025-12-31')
            if not lots:raise ValueError('cycle-count correction has no eligible stock')
            lot=lots[0];key=f'cycle-count/{fid}/{i}'
            old=self.movement(key+'/asserted',location,code,lot,'ADJUSTMENT',at,Decimal(-2))
            self.movement(key+'/reversal',location,code,lot,'ADJUSTMENT',at,Decimal(2),reverse=old['movement_id'],recorded=at+timedelta(days=2))
            self.movement(key+'/corrected',location,code,lot,'ADJUSTMENT',at,Decimal(-1),recorded=at+timedelta(days=2))
            self.stock[location,code,lot]-=1
        events=[{**r,'consumption_group_key':self.med_links[r['clinical_event_version_id']],'generation_run_id':self.run_id}
                if r['clinical_event_version_id'] in self.med_links else r for r in self.t['clinical_event']]
        if len(self.rows)>60000:raise ValueError('full inventory ledger exceeds 60000-row envelope: '+str(len(self.rows)))
        self.controls.update(medication_links=len(self.med_links),clinical_supply_demands=sum(not t['medication'] for t in self.tasks),
            consumption_groups=len(self.groups),movements=len(self.rows),closing_lot_locations=sum(q>0 for q in self.stock.values()),
            cycle_count_corrections=self.cfg['cycle_count_corrections'])
        return {'tables':{'clinical_event':events,'inventory_movement':self.rows},'controls':dict(self.controls)}
