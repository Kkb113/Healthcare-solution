"""Source-shaped serializer; accepted facts are inputs, never regenerated here."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

from .core import canonical, digest


def footprint(path):
    h = hashlib.sha256(); size = 0
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block); size += len(block)
    return {'sha256': h.hexdigest(), 'bytes': size}


def totals(rows, layout):
    return {f['canonical']: format(sum((Decimal(r[f['canonical']]) for r in rows
            if r[f['canonical']] is not None), Decimal(0)), 'f')
            for f in layout['fields'] if f['type'].startswith('DECIMAL')}


def unit_totals(rows, layout):
    if layout['table'] != 'finance_monthly':
        return {}
    result = defaultdict(Decimal)
    for row in rows:
        # Period, scenario, vintage, account/measure and unit may never be
        # collapsed into a misleading combined quantity or financial total.
        key = '|'.join((row['scenario'], row['accounting_month'], row['vintage_id'],
                        row['account_catalog_id'] or 'NONE', row['measure_code'], row['unit_code']))
        result[key] += Decimal(row['amount'] if row['amount'] is not None else row['quantity'])
    return {k: format(v, 'f') for k, v in sorted(result.items())}


def reference(source, field, value, aliases=None):
    # Immutable transport identities; dictionary lookup, never token decoding, resolves them.
    if aliases and value in aliases:
        kind, native = aliases[value]
        if kind == 'WORKER' and source == 'WORKDAY':
            return native
        if kind == 'COST_CENTER' and source in ('WORKDAY', 'AXIOM'):
            return ('WO-' if source == 'WORKDAY' else 'AX-') + native
        if kind == 'ACCOUNT' and source == 'AXIOM':
            return 'AX-' + native
        if kind == 'PATIENT' and source == 'EHR':
            return native
    return source + '-' + field.replace('_id', '').replace('_key', '').upper() + '-' + hashlib.sha256(value.encode()).hexdigest()[:24]


def export_file(root, layout, rows, label, *, mode='IMMUTABLE_VERSION_DELTA', role='PRIMARY',
                available_at=None, scope=None, replacement_of=None, family=None):
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
        return _export_file(root, layout, rows, label, mode=mode, role=role, available_at=available_at,
                            scope=scope, replacement_of=replacement_of, family=family)


def _export_file(root, layout, rows, label, *, mode, role, available_at, scope, replacement_of, family):
    rows = sorted(rows, key=lambda r: r[layout['primary_key']])
    source, table = layout['source'], layout['table']
    stem = f"valid/{source.lower().replace('_', '-')}/{table.replace('_', '-')}/{label}"
    path = Path(root) / (stem + ('.jsonl' if layout['format'] == 'JSONL_EVENT_ENVELOPE' else '.csv'))
    path.parent.mkdir(parents=True, exist_ok=True)
    dictionary = {}; encoded = []
    for row in rows:
        converted = {}
        for f in layout['fields']:
            value = row[f['canonical']]
            if value is None:
                value = '\\N'
            elif f['reference']:
                token = reference(source, f['canonical'], value, layout.get('native_aliases'))
                key = (f['canonical'], token)
                if key in dictionary and dictionary[key] != value:
                    raise ValueError('transport identifier collision')
                dictionary[key] = value; value = token
            elif f['type'] == 'TIMESTAMP':
                time = datetime.fromisoformat(value.replace('Z', '+00:00'))
                value = time.strftime('%m/%d/%Y %H:%M:%S %z') if source == 'WORKDAY' else time.strftime('%Y%m%d%H%M%S%z')
            elif f['type'] == 'DATE':
                value = datetime.strptime(value, '%Y-%m-%d').strftime('%m/%d/%Y')
            elif f['type'] == 'BOOLEAN':
                value = 'Y' if value else 'N'
            else:
                value = str(value)
                if value == '\\N' or value.startswith('\\E'):
                    value = '\\E' + value
            converted[f['source']] = value
        encoded.append(converted)
    columns = [f['source'] for f in layout['fields']]
    temporary = path.with_suffix('.tmp')
    if layout['format'] == 'RFC4180_CSV':
        with temporary.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\r\n')
            writer.writeheader(); writer.writerows(encoded)
    else:
        with temporary.open('w', encoding='utf-8', newline='\n') as stream:
            for ordinal, (row, body) in enumerate(zip(rows, encoded), 1):
                message = {'MessageID': reference(source, layout['primary_key'], row[layout['primary_key']], layout.get('native_aliases')),
                           'SourceSequence': ordinal, 'SourceAvailableAt': row['export_available_at'],
                           'SchemaVersion': layout['schema_version'], 'Record': body}
                stream.write(canonical(message) + '\n')
    temporary.replace(path)
    dictionary_path = Path(root) / (stem + '.keys.csv')
    with dictionary_path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\r\n'); writer.writerow(['Field', 'Reference', 'CanonicalKey'])
        writer.writerows((field, token, key) for (field, token), key in sorted(dictionary.items()))
    availability = [r['export_available_at'] for r in rows]
    manifest = {'path': path.relative_to(root).as_posix(), 'dictionary_path': dictionary_path.relative_to(root).as_posix(),
                'source': source, 'table': table, 'schema_version': layout['schema_version'], 'format': layout['format'],
                'source_contract_id': {'worker_assignment': 'WD_WORKER', 'cost_center': 'WD_COST_CENTER',
                    'access_scope': 'WD_SECURITY', 'bed_event': 'ADT_EVENT'}.get(table,
                    'AX_STATS' if table == 'finance_monthly' and rows and rows[0]['scenario'] == 'ACTUAL' and family in ('statistics-volume', 'statistics-workforce') else
                    'AX_' + (rows[0]['scenario'] if rows else 'EMPTY') if table == 'finance_monthly' else 'CANON_' + table.upper()),
                'role': role, 'mode': mode, 'scope': scope or table + '/' + label,
                'period': rows[0]['accounting_month'] if table == 'finance_monthly' and rows else label,
                'family': family, 'replacement_of': replacement_of, 'expected_rows': len(rows),
                'control_totals': totals(rows, layout), 'unit_control_totals': unit_totals(rows, layout), 'dictionary_rows': len(dictionary),
                'dictionary': footprint(dictionary_path), **footprint(path),
                'available_at': available_at or (max(availability) if availability else None),
                'record_available_min': min(availability) if availability else None,
                'record_available_max': max(availability) if availability else None,
                'vintages': sorted({r['vintage_id'] for r in rows}) if table == 'finance_monthly' else [],
                'original_source_files': sorted({r['source_file_id'] for r in rows}) if table == 'finance_monthly' else [],
                'report_templates': sorted({r['report_template_id'] for r in rows}) if table == 'finance_monthly' else []}
    manifest['file_id'] = digest(manifest)
    return manifest


def partition_rows(table, rows):
    groups = defaultdict(list)
    for row in rows:
        key = row['source_file_id'] if table == 'finance_monthly' else row['export_available_at'][:7]
        groups[key].append(row)
    return groups
