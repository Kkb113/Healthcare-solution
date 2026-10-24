"""Generate source-format mirrors and controlled delivery challenges, not business facts."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src'))
from healthcare_synthetic.source_delivery import run_sources, accepted_parent
from healthcare_synthetic.source_faults import build_faults


def generate(output, fail_table=None, crash_table=None):
    manifest = run_sources(output, fail_table=fail_table, crash_table=crash_table)
    parent, accepted = accepted_parent(); challenges = build_faults(output, parent, accepted)
    return {'status': manifest['status'], 'source_files': len(manifest['files']),
            'primary_source_rows': manifest['primary_source_rows'],
            'published_challenge_record_copies': challenges['published_challenge_record_copies']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, default=ROOT / 'output/source-delivery')
    p.add_argument('--fail-table'); p.add_argument('--crash-table'); a = p.parse_args()
    try:
        result = generate(a.output, a.fail_table, a.crash_table); print(json.dumps(result))
    except Exception as exc:
        print(json.dumps({'status': 'FAILED', 'error': str(exc)})); sys.exit(1)
