"""Run the complete source simulation suite with source/input/content bindings."""
import argparse
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))
from run_financial_regressions import input_hashes as prior_inputs
from run_foundation_regressions import verification_hashes, ProgressResult
from healthcare_synthetic.source_reader import sha, safe_path
from healthcare_synthetic.source_export import footprint


def input_hashes():
    result = prior_inputs()
    for path in [ROOT / 'evidence/financial-history/acceptance-gate.json', ROOT / 'evidence/financial-history/validation-report.json']:
        result[path.relative_to(ROOT).as_posix()] = footprint(path)['sha256']
    return result


def package_digest(output=ROOT / 'output/source-delivery'):
    output = Path(output); m = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    package = json.loads((output / 'challenge-manifest.json').read_text(encoding='utf-8'))
    paths = {'source-dictionary.json'} | set(package['observed_artifacts'])
    paths |= {f['path'] for f in m['files']} | {f['dictionary_path'] for f in m['files']} | {f['path'] for f in m['reports']}
    paths |= {p.relative_to(output).as_posix() for folder in ('valid', 'challenges') for p in (output / folder).rglob('*') if p.is_file()}
    actual = {p: footprint(safe_path(output, p)) for p in sorted(paths)}
    return sha({'manifest': {k: v for k, v in m.items() if k not in ('status', 'executed', 'reused')}, 'challenges': package, 'actual_artifacts': actual})


def run(report=ROOT / 'output/source-delivery/source-tests.json'):
    before = verification_hashes(); inputs = input_hashes(); candidate = package_digest()
    discovered = unittest.TestSuite(unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern)
                                   for pattern in ('test_source_delivery.py', 'test_phase1_sources.py'))
    def flatten(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from flatten(item)
            else:
                yield item
    # Keep full persisted inspection and clean rebuilds out of small-fixture setup.
    suite = unittest.TestSuite(sorted(flatten(discovered), key=lambda t: (t.__class__.__name__ == 'SourceHistoryTests', t.id())))
    log = io.StringIO(); tested = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=ProgressResult, failfast=True).run(suite)
    result = {'group': 'source-delivery', 'run': tested.testsRun, 'passed': tested.wasSuccessful() and not tested.skipped,
        'failed': len(tested.failures), 'errors': len(tested.errors), 'skipped': len(tested.skipped), 'cases': tested.records,
        'failure_details': [message for _, message in tested.failures + tested.errors],
        'verification_source_sha256': before, 'verification_input_sha256': inputs,
        'verification_sources_unchanged_during_tests': before == verification_hashes(),
        'verification_inputs_unchanged_during_tests': inputs == input_hashes(),
        'candidate_source_package_sha256': candidate, 'candidate_unchanged_during_tests': candidate == package_digest()}
    inspection = ROOT / 'output/source-delivery/independent-inspection.json'
    result['inspection_artifact_sha256'] = footprint(inspection)['sha256'] if inspection.exists() else None
    result['passed'] = result['passed'] and all(result[k] for k in ('verification_sources_unchanged_during_tests', 'verification_inputs_unchanged_during_tests', 'candidate_unchanged_during_tests'))
    Path(report).parent.mkdir(parents=True, exist_ok=True); Path(report).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    if not result['passed']:
        print(log.getvalue(), flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--report', type=Path, default=ROOT / 'output/source-delivery/source-tests.json'); a = p.parse_args()
    result = run(a.report); print(json.dumps({k: result[k] for k in ('run', 'passed', 'failed', 'errors', 'skipped')})); sys.exit(0 if result['passed'] else 1)
