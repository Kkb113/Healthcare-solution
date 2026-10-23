"""Calendar, monetary and identity primitives for the synthetic accounting contract."""
from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR

from .core import allocate_cents, chicago, draw, instant, money, stable_id
from .master_generation import MasterGenerator

ZONE = chicago()
START = datetime(2023, 1, 1, 6, tzinfo=timezone.utc)
CUTOFF = datetime(2026, 1, 1, 6, tzinfo=timezone.utc)
GRACE = '2026-01-10T23:59:59Z'
NEW_TABLES = ('service_charge', 'claim', 'claim_line', 'claim_event', 'financial_posting', 'cost_allocation', 'finance_monthly')


def stamp(at): return at.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
def day(at): return instant(at).astimezone(ZONE).date() if isinstance(at, str) else at.astimezone(ZONE).date()
def month(d): return date.fromisoformat(d[:10]).replace(day=1) if isinstance(d, str) else d.replace(day=1)
def next_month(d): return (d.replace(day=28) + timedelta(days=4)).replace(day=1)
def at(d, hour=0): return datetime.combine(d, datetime.min.time()).replace(hour=hour, tzinfo=ZONE).astimezone(timezone.utc)
def close(d, n=5): return stamp(at(next_month(month(d)).replace(day=n), 18))
def cash(v): return format(money(v), '.2f')
def quantity(v): return format(Decimal(v).quantize(Decimal('.000001')), 'f')


def months():
    d = date(2023, 1, 1)
    while d < date(2026, 1, 1):
        yield d
        d = next_month(d)


def latest(rows, key, revision='revision_no', known=None):
    result = {}
    for row in rows:
        if known and row['export_available_at'] > known: continue
        if row[key] not in result or row[revision] > result[row[key]][revision]: result[row[key]] = row
    return result


def date_parts(start, end):
    cursor = start
    while cursor < end:
        boundary = min(end, at(day(cursor) + timedelta(days=1)))
        yield day(cursor).isoformat(), Decimal(str((boundary-cursor).total_seconds()))
        cursor = boundary


def posting_date(service, known):
    d = date.fromisoformat(service)
    if known <= close(d): return service
    if d.year == 2025 and d.month == 12 and known <= close(d, 9): return '2025-12-31'
    result = day(known).isoformat()
    if result > '2025-12-31': raise ValueError('source cannot post beyond the observed accounting window')
    return result


def shares(weights):
    """Independent of currency apportionment; retain exactly one million micros."""
    denominator = sum(map(Decimal, weights.values()))
    raw = {k: Decimal(w)*1000000/denominator for k,w in weights.items()}
    floor = {k: int(v.to_integral_value(rounding=ROUND_FLOOR)) for k,v in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k]-floor[k]), k))[:1000000-sum(floor.values())]: floor[k] += 1
    return {k: quantity(Decimal(v)/1000000) for k,v in floor.items()}


def delivered_assignments(history,known):
    """A superseded assertion remains usable until its replacement is delivered."""
    replacements=defaultdict(list)
    for r in history:replacements[r['worker_id'],r['known_from']].append(r['export_available_at'])
    return [r for r in history if r['export_available_at']<=known and
            (r['known_to'] is None or known<min(replacements.get((r['worker_id'],r['known_to']),['9999'])))]


class Context:
    def __init__(self, tables, cfg, run_id):
        self.t, self.cfg, self.seed = tables, cfg, cfg['seed']
        self.builder = MasterGenerator({'seed': self.seed}, {}, run_id)
        self.cat = {r['catalog_item_id']: r for r in tables['catalog_item']}
        self.codes = defaultdict(list)
        for r in tables['catalog_item']: self.codes[r['code']].append(r)
        self.enc = {r['encounter_version_id']: r for r in tables['encounter']}
        self.latest = latest(tables['encounter'], 'encounter_id')
        self.loc = {r['location_id']: r for r in tables['location']}
        self.cc = {r['cost_center_id']: r for r in tables['cost_center']}
        self.centers = {(r['facility_id'], r['cost_center_code'].split('-')[-1]): r['cost_center_id'] for r in tables['cost_center']}
        self.cover = {r['coverage_version_id']: r for r in tables['patient_coverage']}
        self.payers = {r['payer_plan_id']: r for r in tables['payer_plan']}
        self.workers = {r['worker_assignment_id']: r for r in tables['worker_assignment']}

    def row(self, table, key, known, **fields):
        return self.builder.row(table, key, known, export_available_at=known, **fields)

    def code(self, code, on):
        candidates = [r for r in self.codes[code] if r['valid_from'] <= str(on) < (r['valid_to'] or '9999')]
        if len(candidates) != 1: raise ValueError('ambiguous or invalid catalog code/date: '+code+' '+str(on))
        return candidates[0]['catalog_item_id']

    def payer(self, encounter): return self.payers[self.cover[encounter['coverage_version_id']]['payer_plan_id']]

    def pick(self, key, stream, upper): return draw(self.seed, key, stream, upper=upper)
