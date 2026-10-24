"""Generate the primary integrated candidate or preregistered comparison seed."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src'))
from healthcare_synthetic.integrated_generation import generate

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--seed', type=int, default=20261023)
    p.add_argument('--output', type=Path, default=ROOT / 'output/integrated-history')
    p.add_argument('--fail-stage'); p.add_argument('--crash-stage'); a = p.parse_args()
    m = generate(a.seed, a.output, fail_stage=a.fail_stage, crash_stage=a.crash_stage)
    print(json.dumps({k: m[k] for k in ('status', 'business_rows', 'business_sha256', 'executed', 'reused')}))
