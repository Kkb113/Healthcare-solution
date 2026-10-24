"""Independent expected-delivery calendar and full-snapshot membership oracle."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src'))
from healthcare_synthetic.source_reader import read_file


def inspect_calendar(output, manifest):
    output = Path(output)
    files = manifest['files']; expected = set(); dt = datetime(2023, 1, 1, 7, tzinfo=timezone.utc)
    while dt <= datetime(2026, 1, 10, 7, tzinfo=timezone.utc):
        expected.add(dt.strftime('%Y-%m-%dT%H:%M:%SZ')); dt += timedelta(days=1)
    for table in ('worker_assignment', 'access_scope'):
        primary = [f for f in files if f['table'] == table and f['role'] == 'PRIMARY']
        dates = [f['available_at'] for f in primary]
        if len(set(dates)) != len(dates) or not expected <= set(dates) or any(d > max(expected) for d in dates):
            raise ValueError('F_MISSING: expected Workday daily delivery calendar differs: ' + table)
    weekly = set(); dt = datetime(2022, 12, 18, 7, tzinfo=timezone.utc)
    while dt.year < 2026:
        weekly.add(dt.strftime('%Y-%m-%dT%H:%M:%SZ')); dt += timedelta(days=7)
    for table in ('worker_assignment', 'cost_center'):
        snapshots = [f for f in files if f['table'] == table and f['mode'] == 'FULL_SNAPSHOT']
        dates = [f['available_at'] for f in snapshots]
        if len(set(dates)) != len(dates) or set(dates) != weekly:
            raise ValueError('F_MISSING: expected Workday Sunday calendar differs: ' + table)
    actual = [f for f in files if f['table'] == 'finance_monthly' and f['vintages'][0].startswith('ACTUAL-')]
    periods = {f'{year}-{month:02}-01' for year in range(2023, 2026) for month in range(1, 13)}
    by_family = {}
    for f in actual:
        if f['mode'] != 'REPLACE_DECLARED_SCOPE_VERSION':
            raise ValueError('F_REPLACE: actual close is not replacement-aware')
        if not f['replacement_of']:
            by_family.setdefault((f['report_templates'][0], f['family']), []).append(f['period'])
    if len(by_family) != 4 or any(set(dates) != periods or len(dates) != 36 for dates in by_family.values()):
        raise ValueError('F_MISSING: actual close template/family/period inventory differs')
    layout_path = output / 'source-dictionary.json'
    layouts = json.loads(layout_path.read_text(encoding='utf-8'))
    finance_headers = 0
    for f in files:
        if f['table'] != 'finance_monthly':
            continue
        rows = read_file(output, f, layouts['finance_monthly'])
        if not rows or {r['accounting_month'] for r in rows} != {f['period']} or sorted({r['vintage_id'] for r in rows}) != f['vintages'] or sorted({r['source_file_id'] for r in rows}) != f['original_source_files'] or sorted({r['report_template_id'] for r in rows}) != f['report_templates']:
            raise ValueError('F_SCHEMA: source header period/vintage/file/template differs from records')
        r = rows[0]
        expected_scope = '/'.join((r['report_template_id'], r['accounting_month'], r['scenario'], f['family']))
        if f['scope'] != expected_scope or len({r['scenario'] for r in rows}) != 1 or f['available_at'] != max(r['export_available_at'] for r in rows):
            raise ValueError('F_SCHEMA: source header scope/scenario/arrival differs from records')
        contract = 'AX_STATS' if r['scenario'] == 'ACTUAL' and r['quantity'] is not None else 'AX_' + r['scenario']
        if f['source_contract_id'] != contract or (r['scenario'] != 'ACTUAL' and (f['mode'] != 'APPEND_VINTAGE' or f['replacement_of'])):
            raise ValueError('F_SCHEMA: Axiom scenario contract/mode differs')
        finance_headers += 1
    parent = ROOT / 'output/financial-history'; accepted = json.loads((parent / 'manifest.json').read_text(encoding='utf-8'))
    snapshots_checked = 0; snapshot_rows = 0
    for table in ('worker_assignment', 'cost_center'):
        with (parent / accepted['canonical_files'][table]['file']).open(encoding='utf-8') as stream:
            known = [json.loads(line) for line in stream]
        key = layouts[table]['primary_key']
        for f in files:
            if f['table'] != table or f['mode'] != 'FULL_SNAPSHOT':
                continue
            rows = read_file(output, f, layouts[table]); expected_keys = {r[key] for r in known if r['export_available_at'] <= f['available_at']}
            if {r[key] for r in rows} != expected_keys or any(r['export_available_at'] > f['available_at'] for r in rows):
                raise ValueError('F_LATE: full snapshot membership includes future/omits known revisions')
            snapshots_checked += 1; snapshot_rows += len(rows)
    return {'status': 'PASS', 'expected_daily_dates_per_worker_security_feed': len(expected),
            'expected_weekly_dates_per_worker_center_feed': len(weekly), 'snapshots_checked': snapshots_checked,
            'snapshot_revision_mirrors_checked': snapshot_rows, 'actual_close_template_families': len(by_family),
            'actual_close_months_per_family': 36, 'axiom_file_headers_reconciled_to_records': finance_headers}
