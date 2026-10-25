"""Bind release tooling separately from immutable historical producer evidence."""
from .common import ROOT, read, sha_file


def tool_bindings():
    paths = sorted((ROOT / 'release_tooling').glob('*.py'))
    paths += sorted((ROOT / 'release_tooling').glob('*.json'))
    paths += [ROOT / 'tests/test_dataset_release.py']
    paths += sorted((ROOT / 'docs/dataset-release').glob('*.md'))
    return {p.relative_to(ROOT).as_posix(): sha_file(p) for p in paths}


def retained_bindings():
    report = read(ROOT / 'evidence/integrated-history/validation-report.json')
    result = {**report['verification_source_sha256'], **report['verification_input_sha256']}
    if any(sha_file(ROOT / p) != h for p, h in result.items()):
        raise ValueError('an unchanged prior source/input no longer matches Phase 8 evidence')
    return result
