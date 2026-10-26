"""Check the version 1.1 behaviour revision on a full candidate against the prior release."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src'))
from healthcare_synthetic.behaviour_revision import evaluate
from healthcare_synthetic.engine import atomic_json
from healthcare_synthetic.integrated_generation import read, schema

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, default=ROOT / 'output/integrated-history')
    p.add_argument('--reference', type=Path, default=ROOT / 'data/releases/healthcare-synthetic-v1.0.2/dataset',
                   help='Prior release dataset whose unchanged domains must match; omit with --no-reference for comparison seeds')
    p.add_argument('--no-reference', action='store_true')
    p.add_argument('--output', type=Path, default=ROOT / 'output/integrated-validation/behaviour-revision.json')
    a = p.parse_args()
    result = evaluate(a.candidate, None if a.no_reference else a.reference, schema())
    result.update(seed=read(a.candidate / 'manifest.json')['seed'], business_sha256=read(a.candidate / 'manifest.json')['business_sha256'])
    a.output.parent.mkdir(parents=True, exist_ok=True); atomic_json(a.output, result)
    for c in result['checks']:
        print(('PASS ' if c['passed'] else 'FAIL ') + c['id'], c.get('value', c.get('evidence')))
    print(json.dumps({'status': result['status'], 'failed': result['failed']}))
    sys.exit(0 if result['status'] == 'PASS' else 1)
