"""Per-release business anchors, lineage and evidence locations.

A published release keeps its own profile forever; a new version adds a profile
instead of editing an earlier one. Verification resolves the profile from the
package's own release ID, so earlier versions stay independently verifiable.
"""
from __future__ import annotations

V1_0_PRODUCER = '0f398f3c09be70d34a1811283e80aa0de57dc8ed'
# None: the committed HEAD at clean-rebuild time, recorded once and enforced afterwards.
V1_1_PRODUCER = None

V1_0 = {
    'version': '1.0',
    'producer_commit': V1_0_PRODUCER,
    'lineage': (
        ('master-foundation', 'f7d512673e21f032065774b8afcde6800df28f72', 'generate_master_data.py',
         'c4e987cfd994c51a6bcf0352d44b386d701a84ef8e35a84240bbed25cf1dc59c'),
        ('clinical-histories', '691435db3708939196b83d9cbade39b3e5db4785', 'generate_clinical_histories.py',
         'a74a03a5b086143cc6db18b1b70e41a914aeab0750e64ea967ffe83e95ccf1ca'),
        ('operational-flow', '51ef26af7a1002e6a6074f96b72059f74dbbe5dc', 'generate_operational_flow.py',
         'f0ffb9bb73ef93375cd24dac8294ffefa05c2a6b48252493047011f5fb0e2eed'),
        ('resource-foundation', '1840da3dbe3edf643b12e7b3e4a1897312d99d86', 'generate_resource_foundation.py',
         'd74687a69f72c7e2b4f63fea2ede2d58e45487c86a2e92a2013ca639f675c439'),
        ('financial-history', 'eb20bfa55eb7ac9850f9b3f5b4037a247a4f3f82', 'generate_financial_history.py',
         '773a236ec9c7ec3df5605f38d21f4934a9384eae1bbf04ab4bf164cb51006b72'),
        ('source-delivery', 'bfd89b22d54bac051a3daf4ea27adcae0c5475b2', 'generate_source_delivery.py',
         '773a236ec9c7ec3df5605f38d21f4934a9384eae1bbf04ab4bf164cb51006b72'),
        ('integrated-history', V1_0_PRODUCER, 'generate_integrated_history.py',
         '61124cc71b21198163a278fc103798d919c4346d587b3bef320091ff17edaa5e'),
    ),
    'business_sha256': '61124cc71b21198163a278fc103798d919c4346d587b3bef320091ff17edaa5e',
    'source_sha256': '7f1b5a5dbe567ae3b28936e6ff6684f5c6cdeb767a73e321a2f1f628f71ab431',
    'business_rows': 1936663, 'challenge_copies': 22, 'source_files': 3444, 'reports': 6,
    'domain_checks': 58, 'fault_outcomes': 15, 'snapshots': 318, 'axiom_headers': 304,
    'reviewed_cases': 136, 'historical_native_control': True,
    'certification_root': 'output/release-certification',
    'evidence_dir': 'evidence/dataset-release',
    'review': 'reviews/dataset-release-review.json',
    'issues': 'reviews/dataset-release-issues.json',
}

V1_1 = {
    **V1_0,
    'version': '1.1',
    'producer_commit': V1_1_PRODUCER,
    # Version 1.1 regenerates every care, capacity, workforce, stock and finance
    # domain from the accepted master snapshot in one integrated stage.
    'lineage': (
        V1_0['lineage'][0],
        ('integrated-history', V1_1_PRODUCER, 'generate_integrated_history.py',
         '12859a1807c54f2a1900b2ae430b11e88befc33d483e4e96ce0452d0e682eb1b'),
    ),
    'business_sha256': '12859a1807c54f2a1900b2ae430b11e88befc33d483e4e96ce0452d0e682eb1b',
    'source_sha256': 'af91c63033f751850585509370b2a8a41db25ea47b49f04abe5289a97dad60db',
    'business_rows': 1937925, 'source_files': 3445,
    'historical_native_control': False,
    'certification_root': 'output/release-certification-v1.1.0',
    'evidence_dir': 'evidence/dataset-release-v1.1.0',
    'review': 'reviews/dataset-release-v1.1.0-review.json',
    'issues': 'reviews/dataset-release-v1.1.0-issues.json',
}

CURRENT_RELEASE = 'healthcare-synthetic-v1.1.0'


def lineage(release, producer):
    """The release lineage with an unpinned producer stage bound to the recorded commit."""
    if release['producer_commit'] and producer != release['producer_commit']:
        raise ValueError('producer commit differs from the pinned release profile')
    return tuple((name, commit or producer, script, expected) for name, commit, script, expected in release['lineage'])


def profile(identifier=None):
    """Resolve a release ID; legacy fixtures without an ID use the 1.0 profile."""
    if identifier is None or identifier.startswith('healthcare-synthetic-v1.0.'):
        return V1_0
    if identifier.startswith('healthcare-synthetic-v1.1.'):
        return V1_1
    raise ValueError('no release profile for ' + identifier)
