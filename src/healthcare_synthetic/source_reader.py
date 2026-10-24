"""Independent strict source reader and disposable durable replay test consumer.

Intentionally imports neither serializers nor generation/domain modules. Only the
published declarative source dictionary is shared with writers.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
from datetime import datetime
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sha(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def safe_path(root, relative):
    root = Path(root).resolve(); path = (root / relative).resolve()
    if root not in path.parents:
        raise ValueError('F_SCHEMA: source path escaped package')
    return path


def check_file(path, expected):
    h = hashlib.sha256(); size = 0
    try:
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk); size += len(chunk)
    except FileNotFoundError as exc:
        raise ValueError('F_MISSING: expected source file absent') from exc
    if h.hexdigest() != expected['sha256'] or size != expected['bytes']:
        raise ValueError('F_CORRUPT: checksum/byte control')


def read_file(root, manifest, layout):
    with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
        return _read_file(root, manifest, layout)


def _read_file(root, manifest, layout):
    m = manifest
    if sha({k: v for k, v in m.items() if k != 'file_id'}) != m['file_id']:
        raise ValueError('F_CORRUPT: manifest identity')
    if (m['table'], m['source'], m['schema_version'], m['format']) != (layout['table'], layout['source'], layout['schema_version'], layout['format']):
        raise ValueError('F_SCHEMA: unapproved source layout')
    path = safe_path(root, m['path']); keys_path = safe_path(root, m['dictionary_path'])
    check_file(path, m); check_file(keys_path, m['dictionary'])
    keys = {}; fields = {f['canonical']: f for f in layout['fields']}
    with keys_path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['Field', 'Reference', 'CanonicalKey']:
            raise ValueError('F_SCHEMA: transport key columns')
        for r in reader:
            key = (r['Field'], r['Reference'])
            if r['Field'] not in fields or not fields[r['Field']]['reference'] or key in keys or not r['CanonicalKey']:
                raise ValueError('F_UNMAPPED: invalid/ambiguous transport key')
            keys[key] = r['CanonicalKey']
    if len(keys) != m['dictionary_rows']:
        raise ValueError('F_MISSING: transport key count')
    rows = []; seen = set(); used_keys = set()
    columns = [f['source'] for f in layout['fields']]
    with path.open(encoding='utf-8', newline='') as stream:
        if layout['format'] == 'RFC4180_CSV':
            reader = csv.DictReader(stream)
            if reader.fieldnames != columns:
                raise ValueError('F_SCHEMA: source columns/order')
        else:
            reader = (json.loads(line) for line in stream)
        for ordinal, raw in enumerate(reader, 1):
            try:
                envelope = None
                if layout['format'] != 'RFC4180_CSV':
                    envelope = raw
                    if set(raw) != {'MessageID', 'SourceSequence', 'SourceAvailableAt', 'SchemaVersion', 'Record'} or raw['SchemaVersion'] != m['schema_version'] or type(raw['SourceSequence']) is not int or raw['SourceSequence'] != ordinal:
                        raise ValueError('F_SCHEMA: event envelope sequence/schema')
                    raw = raw['Record']
                if set(raw) != set(columns) or any(v is None or not isinstance(v, str) for v in raw.values()):
                    raise ValueError('F_CORRUPT: row field count/type')
                row = {}
                for f in layout['fields']:
                    c, kind = f['canonical'], f['type']; value = raw[f['source']]
                    if value == '\\N':
                        if not f['nullable']:
                            raise ValueError('F_UNMAPPED: missing critical ' + c)
                        value = None
                    elif f['reference']:
                        key = (c, value)
                        if key not in keys:
                            raise ValueError('F_UNMAPPED: unknown typed reference ' + c + '/' + value)
                        used_keys.add(key); value = keys[key]
                    elif kind == 'TIMESTAMP':
                        fmt = '%m/%d/%Y %H:%M:%S %z' if layout['source'] == 'WORKDAY' else '%Y%m%d%H%M%S%z'
                        dt = datetime.strptime(value, fmt)
                        if dt.utcoffset().total_seconds() != 0 or dt.strftime(fmt) != value:
                            raise ValueError('F_CORRUPT: noncanonical offset/time')
                        value = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    elif kind == 'DATE':
                        dt = datetime.strptime(value, '%m/%d/%Y')
                        if dt.strftime('%m/%d/%Y') != value:
                            raise ValueError('F_CORRUPT: date shape')
                        value = dt.strftime('%Y-%m-%d')
                    elif kind == 'BOOLEAN':
                        if value not in ('Y', 'N'):
                            raise ValueError('F_CORRUPT: boolean')
                        value = value == 'Y'
                    elif kind == 'INT':
                        if not re.fullmatch(r'-?(0|[1-9][0-9]*)', value):
                            raise ValueError('F_CORRUPT: integer')
                        value = int(value)
                    elif kind.startswith('DECIMAL'):
                        scale = int(kind.split(',')[1][:-1])
                        if not re.fullmatch(r'-?\d{1,' + str(18 - scale) + r'}(?:\.\d{1,' + str(scale) + '})?', value):
                            raise ValueError('F_CORRUPT: finite exact decimal precision/scale')
                        Decimal(value)
                    elif value.startswith('\\E'):
                        value = value[2:]
                    row[c] = value
                if layout['table'] == 'finance_monthly' and ((row['amount'] is None) == (row['quantity'] is None)):
                    raise ValueError('F_CORRUPT: finance measure requires exactly one amount or quantity')
                pk = row[layout['primary_key']]
                if not pk or pk in seen:
                    raise ValueError('F_CORRUPT: repeated/missing immutable version key')
                seen.add(pk)
                if envelope and (envelope['SourceAvailableAt'] != row['export_available_at'] or
                                 envelope['MessageID'] != raw[next(f['source'] for f in layout['fields'] if f['canonical'] == layout['primary_key'])]):
                    raise ValueError('F_CORRUPT: message identity/delivery differs')
                if row['recorded_at'] > row['export_available_at']:
                    raise ValueError('F_LATE: delivery precedes recording')
                rows.append(row)
            except (ValueError, KeyError, TypeError) as exc:
                message = str(exc)
                raise ValueError((message if message.startswith('F_') else 'F_CORRUPT: ' + message) + f' [row {ordinal}]') from exc
    if used_keys != set(keys):
        raise ValueError('F_UNMAPPED: unreferenced dictionary entry')
    if len(rows) != m['expected_rows']:
        raise ValueError('F_MISSING: row control')
    totals = {f['canonical']: format(sum((Decimal(r[f['canonical']]) for r in rows
              if r[f['canonical']] is not None), Decimal(0)), 'f')
              for f in layout['fields'] if f['type'].startswith('DECIMAL')}
    availability = [r['export_available_at'] for r in rows]
    if totals != m['control_totals']:
        raise ValueError('F_CORRUPT: scalar decimal controls')
    unit_controls = {}
    if layout['table'] == 'finance_monthly':
        for row in rows:
            key = '|'.join((row['scenario'], row['accounting_month'], row['vintage_id'],
                            row['account_catalog_id'] or 'NONE', row['measure_code'], row['unit_code']))
            unit_controls[key] = unit_controls.get(key, Decimal(0)) + Decimal(row['amount'] if row['amount'] is not None else row['quantity'])
        unit_controls = {k: format(v, 'f') for k, v in sorted(unit_controls.items())}
    if unit_controls != m['unit_control_totals']:
        raise ValueError('F_CORRUPT: period/scenario/vintage/measure/unit controls')
    if (min(availability) if rows else None, max(availability) if rows else None) != (m['record_available_min'], m['record_available_max']):
        raise ValueError('F_LATE: availability control')
    return rows


class DeliveryReplay:
    """Isolated SQLite validation store; no production ingestion or solution schema."""
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript('''
          PRAGMA journal_mode=WAL;
          CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY, manifest TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS versions(t TEXT, k TEXT, body TEXT, PRIMARY KEY(t,k));
          CREATE TABLE IF NOT EXISTS deliveries(file_id TEXT, t TEXT, k TEXT, observed TEXT, PRIMARY KEY(file_id,t,k));
          CREATE INDEX IF NOT EXISTS deliveries_visibility ON deliveries(t,k,observed);
          CREATE TABLE IF NOT EXISTS quarantine(id INTEGER PRIMARY KEY, file_id TEXT, reason TEXT, resolved_by TEXT);
        ''')

    def close(self):
        self.db.close()

    def ingest(self, root, manifest, layout, *, delivered_at=None, fail=False, crash=False):
        m = manifest
        try:
            if m['mode'] not in {'IMMUTABLE_VERSION_DELTA', 'ADDITIVE_TRANSACTION', 'EVENT_ARCHIVE', 'FULL_SNAPSHOT', 'REPLACE_DECLARED_SCOPE_VERSION', 'APPEND_VINTAGE'}:
                raise ValueError('F_SCHEMA: unknown delivery mode')
            if m['replacement_of'] and m['mode'] != 'REPLACE_DECLARED_SCOPE_VERSION':
                raise ValueError('F_REPLACE: replacement declared on incompatible delivery mode')
            rows = read_file(root, m, layout)
            if delivered_at is not None and delivered_at < m['available_at']:
                raise ValueError('F_LATE: batch not yet available')
            old = self.db.execute('SELECT manifest FROM files WHERE id=?', (m['file_id'],)).fetchone()
            if old:
                if old[0] != encode(m):
                    raise ValueError('F_CORRUPT: conflicting delivery identity')
                return 'DUPLICATE'
            if m['replacement_of']:
                prior = self.db.execute('SELECT manifest FROM files WHERE id=?', (m['replacement_of'],)).fetchone()
                if not prior:
                    raise ValueError('F_MISSING: replacement predecessor')
                p = json.loads(prior[0])
                if (p['scope'], p['source'], p['table']) != (m['scope'], m['source'], m['table']) or p['available_at'] >= m['available_at']:
                    raise ValueError('F_REPLACE: replacement scope/availability')
                for other, in self.db.execute('SELECT manifest FROM files'):
                    if json.loads(other)['replacement_of'] == m['replacement_of']:
                        raise ValueError('F_REPLACE: branched replacement')
            elif m['mode'] == 'REPLACE_DECLARED_SCOPE_VERSION':
                for other, in self.db.execute('SELECT manifest FROM files'):
                    p = json.loads(other)
                    if p['scope'] == m['scope'] and p['source'] == m['source']:
                        raise ValueError('F_REPLACE: implicit replacement')
            with self.db:
                self.db.execute('INSERT INTO files VALUES (?,?)', (m['file_id'], encode(m)))
                for row in rows:
                    key = row[layout['primary_key']]; body = encode(row)
                    old = self.db.execute('SELECT body FROM versions WHERE t=? AND k=?', (m['table'], key)).fetchone()
                    if old and old[0] != body:
                        raise ValueError('F_CORRUPT: conflicting immutable version')
                    self.db.execute('INSERT OR IGNORE INTO versions VALUES (?,?,?)', (m['table'], key, body))
                    observed = row['export_available_at']
                    if m['source'] in ('WORKDAY', 'AXIOM'):
                        observed = max(observed, m['available_at'])
                    if delivered_at:
                        observed = max(observed, delivered_at)
                    self.db.execute('INSERT INTO deliveries VALUES (?,?,?,?)', (m['file_id'], m['table'], key, observed))
                if crash:
                    import os
                    os._exit(97)
                if fail:
                    raise ValueError('F_CORRUPT: injected publication failure')
            return 'APPLIED'
        except Exception as exc:
            with self.db:
                self.db.execute('INSERT INTO quarantine(file_id,reason) VALUES (?,?)', (m.get('file_id'), str(exc)))
            raise

    def recover(self, root, manifest, layout, defect_file_id):
        if not self.db.execute('SELECT 1 FROM quarantine WHERE file_id=? AND resolved_by IS NULL', (defect_file_id,)).fetchone():
            raise ValueError('no pending quarantine to resolve')
        result = self.ingest(root, manifest, layout)
        with self.db:
            self.db.execute('UPDATE quarantine SET resolved_by=? WHERE file_id=? AND resolved_by IS NULL', (manifest['file_id'], defect_file_id))
        return result

    def certify(self, required):
        if self.db.execute('SELECT count(*) FROM quarantine WHERE resolved_by IS NULL').fetchone()[0]:
            raise ValueError('F_CORRUPT: unresolved quarantined delivery')
        present = {r[0] for r in self.db.execute('SELECT id FROM files')}
        if set(required) - present:
            raise ValueError('F_MISSING: incomplete expected delivery inventory')
        return 'COMPLETE'

    def rows(self, table, as_of='9999', scope=None):
        def visible(body):
            row = json.loads(body)
            # This explicit reconstruction/audit extension is not a future
            # source fact. A historical consumer cannot observe a future closure.
            if 'known_to' in row and as_of != '9999':
                row['known_to'] = None
            return row
        if scope is not None:
            files = [json.loads(r[0]) for r in self.db.execute('SELECT manifest FROM files')]
            files = [m for m in files if m['scope'] == scope and m['available_at'] <= as_of]
            if not files:
                raise ValueError('F_MISSING: source scope unavailable')
            latest = max(files, key=lambda m: (m['available_at'], m['file_id']))
            query = '''SELECT v.body FROM versions v JOIN deliveries d ON v.t=d.t AND v.k=d.k
                       WHERE v.t=? AND d.file_id=? AND d.observed<=? ORDER BY v.k'''
            return [visible(r[0]) for r in self.db.execute(query, (table, latest['file_id'], as_of))]
        query = '''SELECT v.body FROM versions v WHERE v.t=? AND EXISTS
                   (SELECT 1 FROM deliveries d WHERE d.t=v.t AND d.k=v.k AND d.observed<=?) ORDER BY v.k'''
        return [visible(r[0]) for r in self.db.execute(query, (table, as_of))]

    def table_hash(self, table):
        h = hashlib.sha256(); count = 0
        for body, in self.db.execute('SELECT body FROM versions WHERE t=? ORDER BY k', (table,)):
            h.update((body + '\n').encode()); count += 1
        return h.hexdigest(), count


def effective_versions(rows, stable_key, effective, known):
    """Do not use hindsight known_to to suppress a not-yet-delivered revision."""
    grouped = {}
    for row in rows:
        if row['export_available_at'] > known or row.get('known_from', '') > known or row.get('valid_from', '') > effective:
            continue
        key = row[stable_key]
        if key not in grouped or (row['known_from'], row['revision_no']) > (grouped[key]['known_from'], grouped[key]['revision_no']):
            grouped[key] = row
    # An expired latest-known version must not resurrect an older open-ended
    # grant or assignment merely because its ending was corrected later.
    return [row for row in grouped.values() if not row.get('valid_to') or row['valid_to'] > effective]


def project_bed_events(rows, effective, known):
    """Effective ordering differs from delivery ordering; corrections remain auditable."""
    rows = [r for r in rows if r['export_available_at'] <= known and r['effective_at'] <= effective]
    by_id = {r['bed_event_id']: r for r in rows}
    if len(by_id) != len(rows):
        raise ValueError('F_CORRUPT: duplicate bed message')
    superseded = set()
    for row in rows:
        prior = row['corrects_bed_event_id']
        if not prior:
            continue
        if prior not in by_id:
            raise ValueError('F_MISSING: correction predecessor not yet delivered')
        if prior in superseded:
            raise ValueError('F_CORRUPT: branched bed correction')
        if by_id[prior]['bed_location_id'] != row['bed_location_id']:
            raise ValueError('F_CORRUPT: correction crosses bed identity')
        superseded.add(prior); seen = set(); cursor = row
        while cursor['corrects_bed_event_id']:
            if cursor['bed_event_id'] in seen:
                raise ValueError('F_CORRUPT: bed correction cycle')
            seen.add(cursor['bed_event_id']); cursor = by_id[cursor['corrects_bed_event_id']]
    states = {}
    for r in sorted((r for r in rows if r['bed_event_id'] not in superseded), key=lambda r: (r['effective_at'], r['sequence_no'], r['bed_event_id'])):
        states[r['bed_location_id']] = r
    return states
