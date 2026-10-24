"""Independent scalar reconciliation of published Axiom report mirrors."""
from __future__ import annotations

import calendar
import csv
from collections import defaultdict
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext

from .source_reader import check_file, safe_path, sha


def validate_reports(root, manifests, finance, centers, catalog):
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
        return _validate_reports(root, manifests, finance, centers, catalog)


def _validate_reports(root, manifests, finance, centers, catalog):
    by_id = {r['finance_record_id']: r for r in finance}
    actual = [r for r in finance if r['scenario'] == 'ACTUAL']
    grain = lambda r: (r['cost_center_id'], r['account_catalog_id'], r['measure_code'], r['accounting_month'], r['unit_code'])
    latest = {}
    for r in actual:
        k = grain(r)
        if k not in latest or r['published_at'] > latest[k]['published_at']:
            latest[k] = r
    value = lambda r: r['amount'] if r['amount'] is not None else r['quantity']
    checks = {}; seen_families = set()
    for m in manifests:
        family = m['family']
        if m['available_at'] != max(r['export_available_at'] for r in finance):
            raise ValueError('retrospective report publication differs')
        if family in seen_families or sha({k: v for k, v in m.items() if k != 'file_id'}) != m['file_id']:
            raise ValueError('F_CORRUPT: report family/manifest identity')
        seen_families.add(family); path = safe_path(root, m['path']); check_file(path, m)
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != m['columns']:
                raise ValueError('F_SCHEMA: report column layout')
            rows = list(reader)
        if len(rows) != m['expected_rows'] or any(set(r) != set(m['columns']) or None in r.values() for r in rows):
            raise ValueError('F_MISSING: report count/shape')
        seen = set(); facts = 0
        if family == 'actual-wide-months':
            groups = set()
            for row in rows:
                group = tuple(row[c] for c in ('Year', 'CostCenter', 'Account', 'Measure', 'Unit'))
                if group in groups:
                    raise ValueError('repeated wide report row')
                groups.add(group)
                for month in range(1, 13):
                    key = row[f'P{month:02}Record']; amount = row[f'P{month:02}']
                    if key == '\\N':
                        if amount != '\\N':
                            raise ValueError('wide missing cell became zero')
                        continue
                    r = by_id[key]
                    if key in seen or key != latest[grain(r)]['finance_record_id'] or value(r) != amount or r['accounting_month'] != f"{row['Year']}-{month:02}-01" or (
                       r['cost_center_id'], r['account_catalog_id'] or '', r['measure_code'], r['unit_code']) != (row['CostCenter'], row['Account'], row['Measure'], row['Unit']):
                        raise ValueError('wide period/id/unit/selected vintage differs')
                    seen.add(key); facts += 1
            if seen != {r['finance_record_id'] for r in latest.values()}:
                raise ValueError('wide omitted latest actual facts')
            if len(groups) != len({(r['accounting_month'][:4], r['cost_center_id'], r['account_catalog_id'] or '', r['measure_code'], r['unit_code']) for r in latest.values()}):
                raise ValueError('wide added empty groups')
        elif family == 'actual-with-adjustments':
            for row in rows:
                a, b = by_id[row['OriginalRecord']], by_id[row['ReplacementRecord']]
                if (row['Period'], row['CostCenter'], row['Account'], row['Measure']) != (b['accounting_month'], b['cost_center_id'], b['account_catalog_id'] or '', b['measure_code']):
                    raise ValueError('adjustment report scope differs')
                if b['finance_record_id'] in seen or grain(a) != grain(b) or b['supersedes_vintage_id'] != a['vintage_id'] or a['published_at'] >= b['published_at'] or (
                   row['OriginalValue'], row['ReportedValue'], row['Unit']) != (value(a), value(b), b['unit_code']) or Decimal(row['OriginalValue']) + Decimal(row['Adjustment']) != Decimal(row['ReportedValue']):
                    raise ValueError('adjustment mirror/replacement conservation differs')
                seen.add(b['finance_record_id']); facts += 2
            if seen != {r['finance_record_id'] for r in actual if r['supersedes_vintage_id']}:
                raise ValueError('adjustment coverage differs')
        elif family == 'forecast-drivers':
            for row in rows:
                r = by_id[row['FinanceRecord']]; days = calendar.monthrange(int(r['accounting_month'][:4]), int(r['accounting_month'][5:7]))[1]
                expected = (Decimal(r['amount']) / days).quantize(Decimal('.000001'))
                if r['finance_record_id'] in seen or r['scenario'] != 'FORECAST' or (row['Publication'], row['Period'], row['MonthlyAmount'], row['CalendarDays']) != (r['published_at'], r['accounting_month'], r['amount'], str(days)) or Decimal(row['DailyPlanRate']) != expected or row['Unit'] != 'USD/calendar_day' or row['Basis'] != 'DERIVED_FROM_ACCEPTED_FORECAST_NOT_A_CAUSAL_FEATURE':
                    raise ValueError('forecast driver identity/value/availability differs')
                seen.add(r['finance_record_id']); facts += 1
            if seen != {r['finance_record_id'] for r in finance if r['scenario'] == 'FORECAST'}:
                raise ValueError('forecast driver coverage differs')
        elif family == 'variance-comparison':
            budgets = defaultdict(list)
            for r in finance:
                if r['scenario'] == 'BUDGET' and r['amount'] is not None:
                    budgets[grain(r)].append(r)
            for row in rows:
                r = by_id[row['ActualRecord']]
                candidates = [p for p in budgets[grain(r)] if p['published_at'] <= r['published_at']]
                p = max(candidates, key=lambda x: x['published_at']) if candidates else None
                diff = Decimal(r['amount']) - Decimal(p['amount']) if p else None
                pct = diff / abs(Decimal(p['amount'])) * 100 if p and Decimal(p['amount']) else None
                expected = {'ActualRecord': r['finance_record_id'], 'BudgetRecord': p['finance_record_id'] if p else '\\N',
                    'Actual': r['amount'], 'Budget': p['amount'] if p else '\\N', 'Variance': format(diff, 'f') if diff is not None else '\\N',
                    'VariancePercent': format(pct.quantize(Decimal('.000001')), 'f') if pct is not None else '\\N',
                    'ComparisonState': 'NO_BUDGET' if not p else 'ZERO_BUDGET' if not Decimal(p['amount']) else 'COMPARABLE', 'Unit': 'USD'}
                if row != expected or r['finance_record_id'] in seen:
                    raise ValueError('variance comparison/source-known budget differs')
                seen.add(r['finance_record_id']); facts += 1 + bool(p)
            if seen != {r['finance_record_id'] for r in latest.values() if r['amount'] is not None}:
                raise ValueError('variance coverage differs')
        elif family == 'account-mapping':
            expected = {('AX-' + r['code'], r['catalog_item_id'], r['display'], r['account_class'], r['normal_balance'] or '\\N') for r in catalog if r['domain'] == 'ACCOUNT'}
            got = [tuple(r[c] for c in ['Account', 'CanonicalAccount', 'Description', 'Class', 'NormalBalance']) for r in rows]
            if set(got) != expected or len(got) != len(expected):
                raise ValueError('account mapping differs')
            facts = len(rows)
        elif family == 'center-mapping':
            expected = {('AX-' + r['cost_center_code'], r['cost_center_id'], r['cost_center_name'], r['facility_id'], r['parent_cost_center_id'] or '\\N') for r in centers}
            got = [tuple(r[c] for c in ['CostCenter', 'CanonicalCostCenter', 'Description', 'Facility', 'Parent']) for r in rows]
            if set(got) != expected or len(got) != len(expected):
                raise ValueError('center mapping differs')
            facts = len(rows)
        else:
            raise ValueError('unapproved report mirror family')
        if facts != m['mirrored_scalar_facts']:
            raise ValueError('derived scalar fact accounting differs')
        checks[family] = {'status': 'PASS', 'rows': len(rows), 'scalar_fact_mirrors': facts}
    if seen_families != {'actual-wide-months', 'actual-with-adjustments', 'forecast-drivers', 'variance-comparison', 'account-mapping', 'center-mapping'}:
        raise ValueError('report mirror inventory incomplete')
    return checks
