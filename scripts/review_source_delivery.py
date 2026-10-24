"""Render deterministic native source samples for the designated engineering review."""
import csv
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))
from healthcare_synthetic.source_layouts import read
from healthcare_synthetic.source_reader import sha
from run_source_regressions import package_digest


def render(output=ROOT / 'output/source-delivery'):
    output = Path(output); m = read(output / 'manifest.json'); policy = read(ROOT / 'contracts/source-delivery-policy.json')
    cases = []; primary = [f for f in m['files'] if f['role'] == 'PRIMARY' and f['expected_rows']]
    def add(name, f, predicate=None):
        path = output / f['path']
        with path.open(encoding='utf-8', newline='') as stream:
            records = (json.loads(line) for line in stream) if path.suffix == '.jsonl' else csv.DictReader(stream)
            record = next((r for r in records if predicate is None or predicate(r)), None)
        if record is None:
            return False
        family = f.get('family')
        facts = (sum(v != '\\N' for k, v in record.items() if k.startswith('P') and k.endswith('Record')) if family == 'actual-wide-months' else
                 2 if family == 'actual-with-adjustments' else
                 1 + (record['BudgetRecord'] != '\\N') if family == 'variance-comparison' else 1)
        cases.append({'review_case': name, 'file_id': f['file_id'], 'path': f['path'],
                      'mode': f['mode'], 'available_at': f['available_at'], 'mirrored_scalar_facts': facts, 'native_record': record})
        return True
    for source, table in [('EHR', 'patient'), ('WORKDAY', 'worker_assignment'), ('ADT_BED', 'bed_event'),
                          ('ROSTER_TIME', 'staff_shift'), ('SUPPLY_PHARMACY', 'inventory_movement'),
                          ('REVENUE_CYCLE', 'claim_event'), ('FINANCE_ERP', 'financial_posting'), ('AXIOM', 'finance_monthly')]:
        f = sorted((f for f in primary if f['source'] == source and f['table'] == table), key=lambda f: f['file_id'])[0]
        add(source + '-native-layout', f)
    for family in policy['axiom_inventory']['families']:
        candidates = [f for f in primary + m['reports'] if f.get('family') == family]
        add('axiom-' + family, min(candidates, key=lambda f: f['file_id']))
    nonzero = lambda value: value != '\\N' and Decimal(value) != 0
    strata = [('actual-long', 'nonzero-actual', lambda r: nonzero(r['Amount'])),
              ('budget-revised', 'nonzero-revised-budget', lambda r: nonzero(r['Amount'])),
              ('statistics-workforce', 'nonzero-workforce-statistic', lambda r: nonzero(r['Quantity'])),
              ('actual-wide-months', 'nonzero-wide-history', lambda r: any(nonzero(v) for k, v in r.items() if len(k) == 3 and k.startswith('P') and k[1:].isdigit())),
              ('actual-with-adjustments', 'nonzero-final-close-confirmation', lambda r: nonzero(r['OriginalValue'])),
              ('variance-comparison', 'comparable-budget-variance', lambda r: r['ComparisonState'] == 'COMPARABLE'),
              ('variance-comparison', 'explicit-zero-budget', lambda r: r['ComparisonState'] == 'ZERO_BUDGET')]
    for family, name, predicate in strata:
        for f in sorted((f for f in primary + m['reports'] if f.get('family') == family), key=lambda f: f['file_id']):
            if add(name, f, predicate):
                break
        else:
            raise ValueError('required native review stratum absent: ' + name)
    lines = ['# Native source engineering review sample', '', 'Implementation phase: 7.', '',
             'Twenty-seven deterministic strata: eight source systems, twelve Axiom archetypes and seven explicit value/state counterexamples. The baseline first-record strata retain legitimate zeros; the additional preregistered nonzero/comparable/zero-budget strata prevent a first-row zero bias. These are synthetic records. Complete round-trip controls, typed dictionaries and all fault outcomes are reviewed alongside these samples.', '']
    for case in cases:
        lines += ['## ' + case['review_case'], '', '```json', json.dumps(case, ensure_ascii=False, indent=2), '```', '']
    body = '\n'.join(lines)
    return body, {'reviewed_cases': len(cases), 'selection_sha256': sha(cases),
                  'review_mirror_rows': len(cases), 'review_scalar_fact_mirrors': sum(c['mirrored_scalar_facts'] for c in cases),
                  'sample_bytes': len(body.encode()), 'sample_sha256': hashlib.sha256(body.encode()).hexdigest(), 'source_package_sha256': package_digest(output)}


if __name__ == '__main__':
    body, selection = render(); path = ROOT / 'reviews/source-delivery-sample.md'; path.write_text(body, encoding='utf-8', newline='\n')
    print(json.dumps(selection))
