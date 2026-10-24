"""Bounded Axiom report mirrors, derived exclusively from accepted financial facts."""
from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

from .core import digest
from .source_export import footprint


def write_report(root, family, columns, rows, mirrored_facts, available_at):
    path = Path(root) / 'valid/axiom/reports' / (family + '.csv'); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\r\n'); writer.writeheader(); writer.writerows(rows)
    result = {'path': path.relative_to(root).as_posix(), 'family': family, 'role': 'DERIVED_MIRROR',
              'mode': 'DERIVED_MIRROR', 'expected_rows': len(rows), 'mirrored_scalar_facts': mirrored_facts,
              'available_at': available_at, 'columns': columns, **footprint(path)}
    result['file_id'] = digest(result)
    return result


def reports(root, finance, centers, catalog):
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
        return _reports(root, finance, centers, catalog)


def _reports(root, finance, centers, catalog):
    result = []; actual = [r for r in finance if r['scenario'] == 'ACTUAL']
    latest = {}
    grain = lambda r: (r['cost_center_id'], r['account_catalog_id'], r['measure_code'], r['accounting_month'], r['unit_code'])
    for row in actual:
        key = grain(row)
        if key not in latest or row['published_at'] > latest[key]['published_at']:
            latest[key] = row
    wide = defaultdict(dict)
    for row in latest.values():
        key = (row['accounting_month'][:4], row['cost_center_id'], row['account_catalog_id'] or '', row['measure_code'], row['unit_code'])
        wide[key]['P' + row['accounting_month'][5:7]] = row
    columns = ['Year', 'CostCenter', 'Account', 'Measure', 'Unit'] + [x for i in range(1, 13) for x in (f'P{i:02}', f'P{i:02}Record')]
    rows = []
    for key, periods in sorted(wide.items()):
        record = dict(zip(columns[:5], key))
        for i in range(1, 13):
            r = periods.get(f'P{i:02}')
            record[f'P{i:02}'] = (r['amount'] if r['amount'] is not None else r['quantity']) if r else '\\N'
            record[f'P{i:02}Record'] = r['finance_record_id'] if r else '\\N'
        rows.append(record)
    final_time = max(r['export_available_at'] for r in finance)
    result.append(write_report(root, 'actual-wide-months', columns, rows, len(latest), final_time))
    original = {grain(r): r for r in actual if r['accounting_month'] == '2025-12-01' and not r['supersedes_vintage_id']}
    adjustments = []
    for row in actual:
        if row['supersedes_vintage_id']:
            prior = original[grain(row)]
            value = lambda r: r['amount'] if r['amount'] is not None else r['quantity']
            adjustments.append({'Period': row['accounting_month'], 'CostCenter': row['cost_center_id'],
                'Account': row['account_catalog_id'] or '', 'Measure': row['measure_code'], 'Unit': row['unit_code'],
                'OriginalRecord': prior['finance_record_id'], 'ReplacementRecord': row['finance_record_id'],
                'OriginalValue': value(prior), 'Adjustment': format(Decimal(value(row)) - Decimal(value(prior)), 'f'),
                'ReportedValue': value(row)})
    result.append(write_report(root, 'actual-with-adjustments', list(adjustments[0]), adjustments, 2 * len(adjustments), final_time))
    forecasts = [r for r in finance if r['scenario'] == 'FORECAST']
    # A transparent driver report: the accepted forecast's monthly value / calendar days.
    # Not a newly invented patient-demand forecast or model input.
    import calendar
    drivers = []
    for r in forecasts:
        days = calendar.monthrange(int(r['accounting_month'][:4]), int(r['accounting_month'][5:7]))[1]
        drivers.append({'FinanceRecord': r['finance_record_id'], 'Publication': r['published_at'], 'Period': r['accounting_month'],
                        'CalendarDays': str(days), 'MonthlyAmount': r['amount'],
                        'DailyPlanRate': format((Decimal(r['amount']) / days).quantize(Decimal('.000001')), 'f'),
                        'Unit': 'USD/calendar_day', 'Basis': 'DERIVED_FROM_ACCEPTED_FORECAST_NOT_A_CAUSAL_FEATURE'})
    result.append(write_report(root, 'forecast-drivers', list(drivers[0]), drivers, len(drivers), final_time))
    budgets = [r for r in finance if r['scenario'] == 'BUDGET' and r['amount'] is not None]
    budget_by_grain = defaultdict(list)
    for row in budgets:
        budget_by_grain[grain(row)].append(row)
    variances = []
    for row in sorted(latest.values(), key=lambda r: r['finance_record_id']):
        if row['amount'] is None:
            continue
        plans = [p for p in budget_by_grain[grain(row)] if p['published_at'] <= row['published_at']]
        plan = max(plans, key=lambda r: r['published_at']) if plans else None
        difference = Decimal(row['amount']) - Decimal(plan['amount']) if plan else None
        pct = difference / abs(Decimal(plan['amount'])) * 100 if plan and Decimal(plan['amount']) else None
        variances.append({'ActualRecord': row['finance_record_id'], 'BudgetRecord': plan['finance_record_id'] if plan else '\\N',
                          'Actual': row['amount'], 'Budget': plan['amount'] if plan else '\\N',
                          'Variance': format(difference, 'f') if difference is not None else '\\N',
                          'VariancePercent': format(pct.quantize(Decimal('.000001')), 'f') if pct is not None else '\\N',
                          'ComparisonState': 'NO_BUDGET' if not plan else 'ZERO_BUDGET' if not Decimal(plan['amount']) else 'COMPARABLE',
                          'Unit': 'USD'})
    result.append(write_report(root, 'variance-comparison', list(variances[0]), variances, sum(1 + (r['BudgetRecord'] != '\\N') for r in variances), final_time))
    accounts = [{'Account': 'AX-' + r['code'], 'CanonicalAccount': r['catalog_item_id'], 'Description': r['display'],
                 'Class': r['account_class'], 'NormalBalance': r['normal_balance'] or '\\N'}
                for r in catalog if r['domain'] == 'ACCOUNT']
    result.append(write_report(root, 'account-mapping', list(accounts[0]), accounts, len(accounts), final_time))
    mapped = [{'CostCenter': 'AX-' + r['cost_center_code'], 'CanonicalCostCenter': r['cost_center_id'],
               'Description': r['cost_center_name'], 'Facility': r['facility_id'],
               'Parent': r['parent_cost_center_id'] or '\\N'} for r in centers]
    result.append(write_report(root, 'center-mapping', list(mapped[0]), mapped, len(mapped), final_time))
    return result
