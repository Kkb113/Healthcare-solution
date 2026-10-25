"""Append-only acceptance and retirement records outside immutable payloads."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .common import read, sha_file
from .package import DESCRIPTOR, release_id, verify_healthcare_release


def create_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.writing')
    try:
        with temporary.open('xb') as target:
            target.write(data)
            target.flush()
            os.fsync(target.fileno())
        # Windows rename is atomic and refuses an existing destination. POSIX
        # rename can overwrite, so use an exclusive hard-link publication there.
        if os.name == 'nt':
            os.rename(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def acceptance_contract(approval, identifier, descriptor_sha256, limitations_sha256):
    if approval.get('decision') != 'ACCEPT_DATA_RELEASE':
        raise ValueError('explicit business-owner acceptance is required')
    if approval.get('release_id') != identifier or approval.get('descriptor_sha256') != descriptor_sha256:
        raise ValueError('acceptance is for a different release/content')
    if approval.get('limitations_sha256') != limitations_sha256 or approval.get('limitations_acknowledged') is not True:
        raise ValueError('documented limitations were not explicitly acknowledged')
    if not isinstance(approval.get('business_owner'), str) or not approval['business_owner'].strip():
        raise ValueError('business owner identity is missing')
    if approval.get('authority') != 'DIRECT_HUMAN_USER_APPROVAL' or not isinstance(approval.get('approval_message'), str) or not approval['approval_message'].strip():
        raise ValueError('human approval evidence is missing; a generated default cannot accept the release')
    if approval.get('separate_solution_authorization_required') is not True:
        raise ValueError('data acceptance must not start a solution product')


def record_acceptance(package, registry, expected_descriptor_sha256, approval):
    verified = verify_healthcare_release(package, expected_descriptor_sha256)
    identifier = verified['release_id']
    limitations_sha = sha_file(Path(package) / 'docs/limitations.md')
    acceptance_contract(approval, identifier, expected_descriptor_sha256, limitations_sha)
    directory = Path(registry) / identifier
    if (directory / 'retirement.json').exists():
        raise ValueError('a retired release cannot be accepted')
    record = {**approval, 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'status': 'DATA_ACCEPTED', 'phase9_status': 'PASSED', 'solution_implementation_started': False,
              'domain_review_sha256': sha_file(Path(package) / 'reviews/integrated-history-review.json'),
              'certification_sha256': sha_file(Path(package) / 'evidence/certification.json')}
    create_once(directory / 'acceptance.json', record)
    return record


def state(package, registry, expected_descriptor_sha256):
    d = verify_healthcare_release(package, expected_descriptor_sha256)
    directory = Path(registry) / d['release_id']
    if (directory / 'retirement.json').exists():
        retired = read(directory / 'retirement.json')
        if retired['descriptor_sha256'] != expected_descriptor_sha256 or retired['release_id'] != d['release_id']:
            raise ValueError('retirement binding differs')
        return {'status': 'RETIRED', 'solution_status': 'BLOCKED_FOR_SOLUTION', 'release_id': d['release_id']}
    if not (directory / 'acceptance.json').exists():
        return {'status': 'AWAITING_BUSINESS_ACCEPTANCE', 'solution_status': 'BLOCKED_FOR_SOLUTION', 'release_id': d['release_id']}
    a = read(directory / 'acceptance.json')
    acceptance_contract(a, d['release_id'], expected_descriptor_sha256, sha_file(Path(package) / 'docs/limitations.md'))
    if a.get('status') != 'DATA_ACCEPTED' or a.get('phase9_status') != 'PASSED' or a.get('solution_implementation_started') is not False:
        raise ValueError('acceptance lifecycle status is inconsistent')
    if a['domain_review_sha256'] != sha_file(Path(package) / 'reviews/integrated-history-review.json') or a['certification_sha256'] != sha_file(Path(package) / 'evidence/certification.json'):
        raise ValueError('acceptance review/certification binding differs')
    return {'status': 'DATA_ACCEPTED', 'solution_status': 'DATA_ACCEPTED', 'release_id': d['release_id'],
            'phase9_status': 'PASSED', 'solution_implementation_started': False}


def retire(package, registry, expected_descriptor_sha256, reason, replacement=None):
    d = verify_healthcare_release(package, expected_descriptor_sha256)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError('retirement needs an explicit reason')
    if replacement:
        release_id(replacement)
        if replacement == d['release_id']:
            raise ValueError('replacement cannot be the retired version')
        replacement_record = Path(registry) / replacement / 'acceptance.json'
        if not replacement_record.exists() or read(replacement_record).get('status') != 'DATA_ACCEPTED' or read(replacement_record).get('release_id') != replacement or (Path(registry) / replacement / 'retirement.json').exists():
            raise ValueError('replacement release must already be accepted and active')
    value = {'release_id': d['release_id'], 'descriptor_sha256': expected_descriptor_sha256,
             'reason': reason, 'replacement': replacement, 'retired_at': datetime.now(timezone.utc).isoformat(),
             'status': 'RETIRED', 'solution_status': 'BLOCKED_FOR_SOLUTION', 'payload_deleted': False}
    create_once(Path(registry) / d['release_id'] / 'retirement.json', value)
    return value
