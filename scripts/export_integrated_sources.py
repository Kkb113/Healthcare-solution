"""Build native source simulations for the integrated candidate."""
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src'))
from healthcare_synthetic.integrated_exports import export
if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--candidate', type=Path, default=ROOT/'output/integrated-history')
    p.add_argument('--output', type=Path, default=ROOT/'output/integrated-source-delivery'); p.add_argument('--fail-table'); p.add_argument('--crash-table'); a=p.parse_args()
    m=export(a.candidate,a.output,fail_table=a.fail_table,crash_table=a.crash_table)
    print(json.dumps({k:m[k] for k in ('status','primary_source_rows','source_payload_bytes')}))
