"""Local validation consumers that retain delivered-source knowledge semantics."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from decimal import Decimal
from zoneinfo import ZoneInfo


def instant_text(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('query timestamps require an explicit UTC offset')
    return result.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')


def delivered_staff(tables,known_at):
    known=instant_text(known_at)
    if known>'2026-01-10T23:59:59Z':raise ValueError('knowledge timestamp exceeds delivery grace')
    latest={}
    for r in tables['staff_shift']:
        # Do not expire an older source assertion merely because a later version
        # exists in the final dataset but has not yet been delivered.
        if r['export_available_at']<=known and (r['shift_id'] not in latest or r['revision_no']>latest[r['shift_id']]['revision_no']):latest[r['shift_id']]=r
    return latest


def labor_totals(tables,known_at,service_month=None):
    rows=list(delivered_staff(tables,known_at).values());zone=ZoneInfo('America/Chicago')
    if service_month:
        rows=[r for r in rows if datetime.fromisoformat(r['planned_start'].replace('Z','+00:00')).astimezone(zone).strftime('%Y-%m')==service_month]
    fields=('worked_hours','productive_hours','paid_nonproductive_hours','unpaid_break_hours','overtime_hours','loaded_cost')
    return {'delivered_at':instant_text(known_at),'service_month':service_month,'captured_blocks':len(rows),
        'scope':'Captured source history only; absent early history is unknown, not zero staffing or complete payroll.',
        'attendance_states':dict(Counter(r['attendance_status'] for r in rows)),
        'totals':{field:format(sum((Decimal(r[field]) for r in rows),Decimal(0)),'f') for field in fields}}


def roster_at(tables,effective_at,known_at):
    at=instant_text(effective_at)
    if not '2023-01-01T06:00:00Z'<=at<='2026-01-01T06:00:00Z':raise ValueError('roster target lies outside the three-year window')
    rows=[r for r in delivered_staff(tables,known_at).values() if r['planned_start']<=at<r['planned_end']]
    observed=[r for r in rows if r['actual_start'] is not None and r['actual_start']<=at<(r['actual_end'] or '2026-01-01T06:00:00Z')]
    return {'effective_at':at,'delivered_at':instant_text(known_at),'captured_roster_slots':len(rows),
        'source_states':dict(Counter(r['attendance_status'] for r in rows)),'observed_attending_blocks':len(observed),
        'scope':'Retained plans and delivered attendance; a published plan alone does not establish actual presence.'}


def inventory_ledger_at(tables,effective_at,known_at):
    at,known=instant_text(effective_at),instant_text(known_at)
    if not '2023-01-01T06:00:00Z'<=at<='2026-01-01T06:00:00Z' or at>known or known>'2026-01-10T23:59:59Z':raise ValueError('inventory query is outside the observed window/knowledge scope')
    quantities=defaultdict(Decimal);values=defaultdict(Decimal)
    for r in tables['inventory_movement']:
        if r['occurred_at']<=at and r['export_available_at']<=known:
            grain=r['location_id'],r['catalog_item_id'],r['lot_id'];quantities[grain]+=Decimal(r['quantity_base']);values[grain]+=Decimal(r['extended_cost'])
    return {'effective_at':at,'delivered_at':known,'lot_location_balances':len(quantities),
        'total_book_value_usd':format(sum(values.values(),Decimal(0)),'f'),
        'negative_book_balances':sum(q<0 for q in quantities.values()),
        'scope':'Delivered stock ledger; daily issue postings can lag point-of-use care. This is not a real-time cabinet count.',
        'balances':[{'location_id':k[0],'catalog_item_id':k[1],'lot_id':k[2],'quantity_base':format(q,'f'),'book_value_usd':format(values[k],'f')} for k,q in sorted(quantities.items()) if q]}
