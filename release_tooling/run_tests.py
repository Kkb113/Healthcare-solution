"""Record fresh release-tool tests and exact tool/prior-input bindings."""
import io
import json
import unittest
from datetime import datetime, timezone

from .common import ROOT, save
from .profiles import CURRENT_RELEASE, profile
from .verification import retained_bindings, tool_bindings


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
    def addSuccess(self, test):
        super().addSuccess(test);self.records.append({'test': test.id(), 'status': 'PASS'})
    def addFailure(self, test, error):
        super().addFailure(test, error);self.records.append({'test': test.id(), 'status': 'FAIL'})
    def addError(self, test, error):
        super().addError(test, error);self.records.append({'test': test.id(), 'status': 'ERROR'})
    def addSkip(self, test, reason):
        super().addSkip(test, reason);self.records.append({'test': test.id(), 'status': 'SKIPPED', 'reason': reason})


def run(output=None):
    before = tool_bindings();prior = retained_bindings()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_dataset_release.py')
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
    passed = result.wasSuccessful() and not result.skipped and before == tool_bindings() and prior == retained_bindings()
    report = {'implementation_phase': 9, 'scope': 'Release-tool fixtures; the cold lineage and full-population payload validators have separate end-to-end evidence.',
              'passed': passed, 'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'skipped': len(result.skipped), 'cases': result.records, 'evaluated_at': datetime.now(timezone.utc).isoformat(),
              'tool_bindings': before, 'retained_prior_bindings': prior,
              'tools_unchanged': before == tool_bindings(), 'inputs_unchanged': prior == retained_bindings(),
              'failure_details': [text for _, text in result.failures + result.errors]}
    save(output or ROOT / profile(CURRENT_RELEASE)['certification_root'] / 'release-tests.json', report)
    if not passed:print(stream.getvalue())
    print(json.dumps({k: report[k] for k in ('passed','run','failures','errors','skipped')}))
    return report


if __name__ == '__main__':
    raise SystemExit(0 if run()['passed'] else 1)
