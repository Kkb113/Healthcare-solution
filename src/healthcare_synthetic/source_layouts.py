"""Declarative synthetic source contracts. No vendor-specific compatibility claim."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEY_EXCLUSIONS = {'source_record_id', 'source_file_id', 'report_template_id',
                  'generation_run_id', 'vintage_id', 'supersedes_vintage_id'}
ALIASES = {
    'worker_id': 'EmployeeID', 'worker_assignment_id': 'AssignmentReference',
    'manager_worker_id': 'ManagerEmployeeID', 'given_name': 'FirstName',
    'family_name': 'LastName', 'cost_center_id': 'CostCenterReference',
    'parent_cost_center_id': 'ParentReference', 'cost_center_name': 'CostCenterName',
    'valid_from': 'EffectiveTime', 'known_from': 'KnownFrom',
    'known_to': 'AuditKnowledgeClosedAt',
    'access_scope_id': 'GrantVersion', 'grant_id': 'GrantReference',
    'principal_id': 'PrincipalReference', 'scope_key': 'ScopeReference',
    'decision': 'Decision', 'bed_event_id': 'MessageControlID',
    'bed_location_id': 'BedReference', 'effective_at': 'EffectiveTime',
    'sequence_no': 'Sequence', 'corrects_bed_event_id': 'CorrectionReference',
    'finance_record_id': 'FinanceRecordReference', 'accounting_month': 'Period',
    'account_catalog_id': 'Account', 'amount': 'Amount', 'quantity': 'Quantity',
    'unit_code': 'Unit', 'vintage_id': 'Version', 'published_at': 'Publication',
    'report_template_id': 'ReportID', 'source_file_id': 'OriginalFileID',
    'export_available_at': 'SourceAvailableAt', 'revision_no': 'ExtractVersion',
    'patient_id': 'PatientReference', 'birth_date': 'BirthDate', 'mrn': 'MRN',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def read_rows(path):
    with Path(path).open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


def contracts():
    result = {}
    for table in read(ROOT / 'contracts/phase0/schema.json')['tables']:
        name = table['name']
        source = ('WORKDAY' if name in ('worker_assignment', 'cost_center', 'access_scope')
                  else 'AXIOM' if name == 'finance_monthly' else
                  'ROSTER_TIME' if name == 'staff_shift' else
                  'ADT_BED' if name == 'bed_event' else
                  'FINANCE_ERP' if name in ('financial_posting', 'cost_allocation') else
                  'REVENUE_CYCLE' if name in ('claim', 'claim_line', 'claim_event', 'service_charge') else
                  'SUPPLY_PHARMACY' if name == 'inventory_movement' else 'EHR')
        fields = []
        for column in table['columns']:
            c = column['name']
            fields.append({'canonical': c, 'source': ALIASES.get(c, ''.join(p.title() for p in c.split('_'))),
                           'type': column['type'], 'nullable': column['nullable'],
                           'temporal_role': 'RETROSPECTIVE_AUDIT_ONLY_OMIT_FROM_ASOF_VIEWS' if c == 'known_to' else 'SOURCE_SCALAR',
                           'reference': c not in KEY_EXCLUSIONS and (c.endswith('_id') or c.endswith('_key'))})
        if len({f['source'] for f in fields}) != len(fields):
            raise ValueError('source field alias collision: ' + name)
        result[name] = {'table': name, 'source': source, 'schema_version': 'synthetic-source-1',
                        'primary_key': table['primary_key'][0], 'fields': fields,
                        'format': 'JSONL_EVENT_ENVELOPE' if source in ('EHR', 'ADT_BED') else 'RFC4180_CSV',
                        'null_token': '\\N', 'encoding': 'UTF-8', 'vendor_certified': False}
    return result
