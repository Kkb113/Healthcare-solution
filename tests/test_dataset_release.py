"""Release-tool fixtures; full-population cold rebuild/validation is separate."""
import copy
import hashlib
import io
import json
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from release_tooling.common import ROOT, digest, inventory, read, safe_relative, save, sha_file
from release_tooling.package import (BUSINESS_SHA, SOURCE_SHA, PROFILE, DESCRIPTOR, MANIFEST,
    check_healthcare_metadata, publish, release_id, seal, verify_healthcare_release, verify_seal)
from release_tooling.rebuild import extract_archive, rebuild, snapshot
from release_tooling.registry import acceptance_contract, create_once, record_acceptance, retire, state
from release_tooling.offline_check import clone_bundle
from release_tooling.certification import certification_workspace
from release_tooling.final_gate import require_closed_critical_issues


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        (ROOT / 'output').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='release-fixture-', dir=ROOT / 'output')
        self.work = Path(self.temp.name).resolve()
        self.assertIn((ROOT / 'output').resolve(), self.work.parents)

    def tearDown(self):
        self.assertIn((ROOT / 'output').resolve(), self.work.parents)
        self.temp.cleanup()

    def envelope(self, identifier='healthcare-synthetic-v1.0.0'):
        root = self.work / ('staging-' + identifier)
        root.mkdir()
        for name, value in [('docs/limitations.md', 'Fixture limitations; not a healthcare population.\n'),
                            ('reviews/integrated-history-review.json', '{"fixture":true}\n'),
                            ('evidence/certification.json', '{"fixture":true}\n'),
                            ('dataset/fixture.jsonl', '{"fictional_id":"a"}\n')]:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding='utf-8', newline='\n')
        anchored = seal(root, identifier, {'profile': 'RELEASE_UNIT_FIXTURE', 'technical_status': 'PASSED'})
        return root, anchored

    def approval(self, root, anchored):
        return {'decision': 'ACCEPT_DATA_RELEASE', 'release_id': read(root / DESCRIPTOR)['release_id'],
                'descriptor_sha256': anchored, 'limitations_sha256': sha_file(root / 'docs/limitations.md'),
                'limitations_acknowledged': True, 'business_owner': 'Unit-test owner; not an actual user approval',
                'authority': 'DIRECT_HUMAN_USER_APPROVAL', 'approval_message': 'Fixture-only explicit acceptance',
                'separate_solution_authorization_required': True}

    def verify_fixture(self, root, anchored):
        # Unit lifecycle tests exercise actual filesystem seals/state writes;
        # only the full-population dependency is replaced by a sealed fixture.
        # Production verify_healthcare_release is exercised by full certification.
        return verify_seal(root, anchored)


class OfflineBundleTests(WorkspaceTest):
    def test_open_critical_issue_blocks_even_with_zero_claimed_count(self):
        with self.assertRaisesRegex(ValueError, 'unresolved P0/P1'):
            require_closed_critical_issues({'unresolved_p0_p1': 0,
                'issues': [{'severity': 'P1', 'status': 'OPEN'}]})

    def test_nonzero_critical_count_blocks_even_with_closed_details(self):
        with self.assertRaisesRegex(ValueError, 'unresolved P0/P1'):
            require_closed_critical_issues({'unresolved_p0_p1': 1,
                'issues': [{'severity': 'P1', 'status': 'CLOSED'}]})

    def test_closed_critical_issue_passes(self):
        require_closed_critical_issues({'unresolved_p0_p1': 0,
            'issues': [{'severity': 'P1', 'status': 'CLOSED'}]})

    def test_certification_workspace_rejects_reuse(self):
        first = certification_workspace(self.work, 'healthcare-synthetic-v1.0.0')
        (first / 'replay-proof.txt').write_text('prior audit')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            certification_workspace(self.work, 'healthcare-synthetic-v1.0.0')
        self.assertEqual((first / 'replay-proof.txt').read_text(), 'prior audit')

    def test_patch_certification_has_separate_empty_workspace(self):
        first = certification_workspace(self.work, 'healthcare-synthetic-v1.0.0')
        (first / 'old-checkpoint.txt').write_text('must not be imported')
        second = certification_workspace(self.work, 'healthcare-synthetic-v1.0.1')
        self.assertNotEqual(first, second)
        self.assertEqual(list(second.iterdir()), [])

    def test_main_only_bundle_clones_with_master_as_host_default(self):
        source = self.work / 'producer'
        subprocess.run(['git', 'init', '--initial-branch=main', str(source)], check=True, capture_output=True)
        (source / 'producer.txt').write_text('Pinned miniature producer fixture\n', encoding='utf-8')
        subprocess.run(['git', 'add', 'producer.txt'], cwd=source, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'user.name=Release fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-m', 'Fixture producer'], cwd=source, check=True, capture_output=True)
        bundle = self.work / 'main-only.bundle'
        subprocess.run(['git', 'bundle', 'create', str(bundle), 'main'], cwd=source, check=True, capture_output=True)
        checkout = self.work / 'checkout'
        with patch.dict(os.environ, {'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'init.defaultBranch',
                                     'GIT_CONFIG_VALUE_0': 'master'}):
            clone_bundle(bundle, checkout)
        self.assertEqual((checkout / 'producer.txt').read_bytes(), (source / 'producer.txt').read_bytes())
        branch = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], cwd=checkout,
                                check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(branch, 'main')


class EnvelopeTests(WorkspaceTest):
    def test_complete_payload_verifies_against_external_anchor(self):
        root, anchor = self.envelope()
        self.assertEqual(verify_seal(root, anchor)['payload_files'], 4)

    def test_external_anchor_is_required(self):
        root, _ = self.envelope()
        for anchor in (None, '', 'not-a-hash'):
            with self.subTest(anchor=anchor), self.assertRaises(ValueError):
                verify_seal(root, anchor)

    def test_wrong_descriptor_anchor_blocks(self):
        root, _ = self.envelope()
        with self.assertRaisesRegex(ValueError, 'trusted external'):
            verify_seal(root, '0' * 64)

    def test_single_byte_corruption_blocks(self):
        root, anchor = self.envelope()
        (root / 'dataset/fixture.jsonl').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'inventory, bytes or checksums'):
            verify_seal(root, anchor)

    def test_extra_file_blocks(self):
        root, anchor = self.envelope()
        (root / 'unlisted.txt').write_text('extra')
        with self.assertRaises(ValueError):verify_seal(root, anchor)

    def test_missing_file_blocks(self):
        root, anchor = self.envelope()
        (root / 'dataset/fixture.jsonl').unlink()
        with self.assertRaises(ValueError):verify_seal(root, anchor)

    def test_manifest_corruption_blocks(self):
        root, anchor = self.envelope()
        (root / MANIFEST).write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError, 'manifest checksum'):verify_seal(root, anchor)

    def test_rehashing_tampered_payload_cannot_replace_trusted_anchor(self):
        root, anchor = self.envelope()
        (root / 'dataset/fixture.jsonl').write_bytes(b'changed')
        m = read(root / MANIFEST);m['files'] = {k:v for k,v in inventory(root).items() if k not in (MANIFEST, DESCRIPTOR)}
        save(root / MANIFEST, m)
        d = read(root / DESCRIPTOR);d['payload_manifest_sha256'] = sha_file(root / MANIFEST);save(root / DESCRIPTOR, d)
        with self.assertRaisesRegex(ValueError, 'trusted external'):verify_seal(root, anchor)

    def test_physical_totals_are_recomputed(self):
        root, _ = self.envelope()
        d = read(root / DESCRIPTOR);d['payload_bytes'] += 1;save(root / DESCRIPTOR, d)
        with self.assertRaisesRegex(ValueError, 'physical payload totals'):
            verify_seal(root, sha_file(root / DESCRIPTOR))

    def test_even_a_trusted_manifest_cannot_escape_payload(self):
        root, _ = self.envelope()
        m = read(root / MANIFEST);m['files']['../outside'] = {'sha256':'0'*64,'bytes':0};save(root / MANIFEST,m)
        d = read(root / DESCRIPTOR);d['payload_manifest_sha256']=sha_file(root / MANIFEST);save(root / DESCRIPTOR,d)
        with self.assertRaisesRegex(ValueError,'unsafe relative'):verify_seal(root,sha_file(root / DESCRIPTOR))

    def test_recursive_manifest_declaration_is_rejected(self):
        root, _ = self.envelope()
        m = read(root / MANIFEST);m['files'][MANIFEST]={'sha256':'0'*64,'bytes':0};save(root / MANIFEST,m)
        d = read(root / DESCRIPTOR);d['payload_manifest_sha256']=sha_file(root / MANIFEST);save(root / DESCRIPTOR,d)
        with self.assertRaisesRegex(ValueError,'recursive'):verify_seal(root,sha_file(root / DESCRIPTOR))

    def test_seal_is_create_once(self):
        root, anchor = self.envelope()
        with self.assertRaisesRegex(ValueError,'already sealed'):seal(root,'healthcare-synthetic-v1.0.0',{})
        self.assertEqual(sha_file(root / DESCRIPTOR),anchor)

    def test_empty_release_cannot_be_sealed(self):
        root=self.work/'empty';root.mkdir()
        with self.assertRaisesRegex(ValueError,'empty'):seal(root,'healthcare-synthetic-v1.0.0',{})

    def test_unit_fixture_cannot_pass_production_population_verification(self):
        root,anchor=self.envelope()
        with self.assertRaises((ValueError,KeyError,FileNotFoundError)):
            verify_healthcare_release(root,anchor)

    def test_relative_paths_reject_windows_and_posix_escapes(self):
        for name in ('','../x','a/../x','/x','C:/x','a\\b','a//b','a/','./a','a\x00b'):
            with self.subTest(name=name),self.assertRaises(ValueError):safe_relative(name)
        self.assertEqual(str(safe_relative('dataset/canonical/patient.jsonl')),'dataset/canonical/patient.jsonl')

    def test_version_identity_is_bounded_and_path_safe(self):
        for name in ('../release','healthcare-synthetic-v0.1.0','healthcare-synthetic-v1.0','healthcare-synthetic-v01.0.0','healthcare-synthetic-v1.01.0','healthcare-synthetic-v1.0.00'):
            with self.subTest(name=name),self.assertRaises(ValueError):release_id(name)
        self.assertEqual(release_id('healthcare-synthetic-v2.1.0'),'healthcare-synthetic-v2.1.0')


class ArchiveAndColdStartTests(WorkspaceTest):
    def archive(self, name, kind=tarfile.REGTYPE):
        p=self.work/'source.tar'
        with tarfile.open(p,'w') as tar:
            member=tarfile.TarInfo(name);member.type=kind
            if kind==tarfile.REGTYPE:member.size=3;tar.addfile(member,io.BytesIO(b'abc'))
            else:member.linkname='../escape';tar.addfile(member)
        return p

    def test_archive_extracts_only_declared_regular_source(self):
        extract_archive(self.archive('src/test.py'),self.work/'source')
        self.assertEqual((self.work/'source/src/test.py').read_bytes(),b'abc')

    def test_archive_traversal_blocks_before_extracting(self):
        with self.assertRaisesRegex(ValueError,'unsafe'):extract_archive(self.archive('../escape'),self.work/'source')
        self.assertFalse((self.work/'escape').exists())

    def test_archive_symbolic_link_blocks(self):
        with self.assertRaisesRegex(ValueError,'unsafe'):extract_archive(self.archive('link',tarfile.SYMTYPE),self.work/'source')

    def test_archive_hard_link_blocks(self):
        with self.assertRaisesRegex(ValueError,'unsafe'):extract_archive(self.archive('link',tarfile.LNKTYPE),self.work/'source')

    def test_cold_build_rejects_existing_workspace_without_overwrite(self):
        marker=self.work/'preserve.txt';marker.write_text('original')
        with self.assertRaisesRegex(ValueError,'already exists'):rebuild(self.work,self.work/'unused.whl')
        self.assertEqual(marker.read_text(),'original')

    def mini_snapshot(self):
        p=self.work/'candidate';(p/'canonical').mkdir(parents=True)
        file=p/'canonical/fixture.jsonl';file.write_bytes(b'{"id":"a"}\n')
        meta={'file':'canonical/fixture.jsonl','sha256':sha_file(file),'bytes':file.stat().st_size,'rows':1}
        anchor=digest({'fixture':meta['sha256']})
        save(p/'manifest.json',{'status':'PASSED','business_sha256':anchor,'canonical_files':{'fixture':meta}})
        return p,anchor

    def test_snapshot_checks_actual_bytes_not_manifest_only(self):
        root,anchor=self.mini_snapshot();snapshot(root,anchor)
        (root/'canonical/fixture.jsonl').write_bytes(b'{"id":"b"}\n')
        with self.assertRaisesRegex(ValueError,'actual table bytes'):snapshot(root,anchor)

    def test_snapshot_counts_actual_rows(self):
        root,anchor=self.mini_snapshot();m=read(root/'manifest.json');m['canonical_files']['fixture']['rows']=2;save(root/'manifest.json',m)
        with self.assertRaisesRegex(ValueError,'actual table count'):snapshot(root,anchor)

    def test_snapshot_rejects_unlisted_canonical_file(self):
        root,anchor=self.mini_snapshot();(root/'canonical/extra.jsonl').write_bytes(b'{}\n')
        with self.assertRaisesRegex(ValueError,'inventory'):snapshot(root,anchor)


class BusinessMetadataTests(unittest.TestCase):
    def setUp(self):
        prior=read(ROOT/'evidence/integrated-history/validation-report.json')
        canonical=prior['source_inspection']['canonical_roundtrip']
        self.c={'business_sha256':BUSINESS_SHA,'business_rows':1936663,'business_tables':25,'canonical_files':copy.deepcopy(canonical)}
        self.d={'profile':PROFILE,'technical_status':'PASSED','canonical_business_sha256':BUSINESS_SHA,
                'source_package_sha256':SOURCE_SHA,'cap_counted_release_rows':1936685,'business_tables':25}
        self.cert={'status':'PASSED','unresolved_p0_p1':0,'unexplained_differences':0,'domain_checks':58,
            'source_files':3444,'fault_outcomes':15,'future_fact_failures':0,'unknown_outcomes_preserved':True,
            'clean_rebuild_passed':True,'phase8_unchanged_evidence_verified':True,'source_package_sha256':SOURCE_SHA}
        files=[{'role':'PRIMARY','table':t,'expected_rows':m['rows']} for t,m in canonical.items()]
        files += [{'role':'SNAPSHOT','table':'worker_assignment','expected_rows':0} for _ in range(3444-len(files))]
        self.native={'business_sha256':BUSINESS_SHA,'canonical_business_rows':1936663,'files':files,'reports':[{} for _ in range(6)]}
        self.schema={'tables':[{'name':t} for t in canonical]};self.challenges={'published_challenge_record_copies':22}

    def check(self):return check_healthcare_metadata(self.d,self.cert,self.c,self.native,self.schema,self.challenges)

    def test_valid_metadata_controls_are_consistent(self):self.assertEqual(self.check(),(1936663,22))
    def test_missing_essential_table_blocks(self):
        self.c['canonical_files'].pop('patient')
        with self.assertRaises(ValueError):self.check()
    def test_over_cap_count_blocks(self):
        self.challenges['published_challenge_record_copies']=100000
        with self.assertRaises(ValueError):self.check()
    def test_source_scope_duplication_blocks(self):
        self.native['files'][0]['expected_rows']+=1
        with self.assertRaises(ValueError):self.check()
    def test_incomplete_native_inventory_blocks(self):
        self.native['files'].pop()
        with self.assertRaises(ValueError):self.check()
    def test_changed_normalized_business_anchor_blocks(self):
        self.c['business_sha256']='0'*64
        with self.assertRaises(ValueError):self.check()
    def test_changed_table_checksum_blocks(self):
        self.c['canonical_files']['patient']['sha256']='0'*64
        with self.assertRaises(ValueError):self.check()
    def test_changed_native_package_anchor_blocks(self):
        self.cert['source_package_sha256']='0'*64
        with self.assertRaises(ValueError):self.check()
    def test_unresolved_critical_issue_blocks(self):
        self.cert['unresolved_p0_p1']=1
        with self.assertRaises(ValueError):self.check()
    def test_unexplained_money_or_state_difference_blocks(self):
        self.cert['unexplained_differences']=1
        with self.assertRaises(ValueError):self.check()
    def test_missing_domain_group_blocks(self):
        self.cert['domain_checks']=57
        with self.assertRaises(ValueError):self.check()
    def test_missing_fault_outcome_blocks(self):
        self.cert['fault_outcomes']=14
        with self.assertRaises(ValueError):self.check()
    def test_future_fact_leak_blocks(self):
        self.cert['future_fact_failures']=1
        with self.assertRaises(ValueError):self.check()
    def test_cleaned_away_unknown_outcome_blocks(self):
        self.cert['unknown_outcomes_preserved']=False
        with self.assertRaises(ValueError):self.check()
    def test_reused_candidate_cannot_claim_clean_rebuild(self):
        self.cert['clean_rebuild_passed']=False
        with self.assertRaises(ValueError):self.check()
    def test_unverified_prior_evidence_cannot_unlock_release(self):
        self.cert['phase8_unchanged_evidence_verified']=False
        with self.assertRaises(ValueError):self.check()
    def test_review_waiver_cannot_substitute_for_technical_pass(self):
        self.cert['status']='WAIVED'
        with self.assertRaises(ValueError):self.check()


class LifecycleTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.root,self.anchor=self.envelope();self.registry=self.work/'registry'
        self.mock=patch('release_tooling.registry.verify_healthcare_release',side_effect=self.verify_fixture)
        self.mock.start()

    def tearDown(self):
        self.mock.stop();super().tearDown()

    def test_no_owner_acceptance_keeps_solution_blocked(self):
        self.assertEqual(state(self.root,self.registry,self.anchor)['solution_status'],'BLOCKED_FOR_SOLUTION')
    def test_real_acceptance_transition_does_not_modify_payload_or_start_solution(self):
        before=inventory(self.root)
        result=record_acceptance(self.root,self.registry,self.anchor,self.approval(self.root,self.anchor))
        self.assertEqual(result['status'],'DATA_ACCEPTED');self.assertFalse(result['solution_implementation_started'])
        self.assertEqual(state(self.root,self.registry,self.anchor)['phase9_status'],'PASSED')
        self.assertEqual(inventory(self.root),before)
    def test_acceptance_is_create_once(self):
        a=self.approval(self.root,self.anchor);record_acceptance(self.root,self.registry,self.anchor,a)
        p=self.registry/a['release_id']/'acceptance.json';before=p.read_bytes()
        with self.assertRaises(FileExistsError):record_acceptance(self.root,self.registry,self.anchor,a)
        self.assertEqual(p.read_bytes(),before)
    def test_plan_approval_is_not_release_acceptance(self):
        a=self.approval(self.root,self.anchor);a['decision']='APPROVE_PLAN'
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,a)
    def test_approval_for_another_descriptor_blocks(self):
        a=self.approval(self.root,self.anchor);a['descriptor_sha256']='0'*64
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,a)
    def test_unacknowledged_limitations_block(self):
        a=self.approval(self.root,self.anchor);a['limitations_acknowledged']=False
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,a)
    def test_changed_limitations_hash_blocks(self):
        a=self.approval(self.root,self.anchor);a['limitations_sha256']='0'*64
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,a)
    def test_missing_human_approval_evidence_blocks(self):
        a=self.approval(self.root,self.anchor);a['approval_message']=''
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,a)
    def test_missing_owner_identity_blocks(self):
        a=self.approval(self.root,self.anchor);a['business_owner']=' '
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,a)
    def test_data_acceptance_cannot_implicitly_authorize_solution(self):
        a=self.approval(self.root,self.anchor);a['separate_solution_authorization_required']=False
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,a)
    def test_failed_atomic_acceptance_cannot_publish_partial_record(self):
        operation='release_tooling.registry.os.rename' if os.name=='nt' else 'release_tooling.registry.os.link'
        with patch(operation,side_effect=OSError('injected before atomic publication')):
            with self.assertRaises(OSError):record_acceptance(self.root,self.registry,self.anchor,self.approval(self.root,self.anchor))
        self.assertFalse(list(self.registry.rglob('acceptance.json')))
        self.assertFalse(list(self.registry.rglob('*.writing')))
        self.assertEqual(state(self.root,self.registry,self.anchor)['solution_status'],'BLOCKED_FOR_SOLUTION')
    def test_retirement_blocks_an_accepted_release_without_deleting_data(self):
        record_acceptance(self.root,self.registry,self.anchor,self.approval(self.root,self.anchor));before=inventory(self.root)
        retire(self.root,self.registry,self.anchor,'Fixture incident')
        self.assertEqual(state(self.root,self.registry,self.anchor)['status'],'RETIRED');self.assertEqual(inventory(self.root),before)
    def test_retired_release_cannot_be_reaccepted(self):
        retire(self.root,self.registry,self.anchor,'Fixture withdrawn')
        with self.assertRaises(ValueError):record_acceptance(self.root,self.registry,self.anchor,self.approval(self.root,self.anchor))
    def test_retirement_needs_reason(self):
        with self.assertRaises(ValueError):retire(self.root,self.registry,self.anchor,' ')
    def test_inactive_replacement_is_rejected(self):
        with self.assertRaises(ValueError):retire(self.root,self.registry,self.anchor,'Fixture incident','healthcare-synthetic-v1.0.1')
    def test_tampered_payload_invalidates_existing_acceptance(self):
        record_acceptance(self.root,self.registry,self.anchor,self.approval(self.root,self.anchor))
        (self.root/'dataset/fixture.jsonl').write_text('changed')
        with self.assertRaises(ValueError):state(self.root,self.registry,self.anchor)
    def test_inconsistent_acceptance_status_cannot_unlock_release(self):
        a=record_acceptance(self.root,self.registry,self.anchor,self.approval(self.root,self.anchor))
        a['status']='PENDING';save(self.registry/a['release_id']/'acceptance.json',a)
        with self.assertRaisesRegex(ValueError,'lifecycle status'):state(self.root,self.registry,self.anchor)
    def test_replacement_registry_identity_must_match_version(self):
        save(self.registry/'healthcare-synthetic-v1.0.1'/'acceptance.json',{'status':'DATA_ACCEPTED','release_id':'healthcare-synthetic-v2.0.0'})
        with self.assertRaisesRegex(ValueError,'accepted and active'):
            retire(self.root,self.registry,self.anchor,'Fixture incident','healthcare-synthetic-v1.0.1')


class PublicationTests(WorkspaceTest):
    def setUp(self):
        super().setUp();self.root,self.anchor=self.envelope();self.destination=self.work/'published/healthcare-synthetic-v1.0.0'
        self.mock=patch('release_tooling.package.verify_healthcare_release',side_effect=self.verify_fixture);self.mock.start()
    def tearDown(self):self.mock.stop();super().tearDown()
    def test_create_once_publication_keeps_external_anchor(self):
        result=publish(self.root,self.destination,self.anchor)
        self.assertEqual(result['solution_status'],'BLOCKED_FOR_SOLUTION');self.assertFalse(self.root.exists())
        self.assertEqual(verify_seal(self.destination,self.anchor)['release_id'],self.destination.name)
    def test_existing_version_cannot_be_overwritten(self):
        self.destination.mkdir(parents=True);p=self.destination/'preserve';p.write_text('original')
        with self.assertRaisesRegex(ValueError,'already exists'):publish(self.root,self.destination,self.anchor)
        self.assertEqual(p.read_text(),'original');self.assertTrue(self.root.exists())
    def test_directory_identity_must_match_descriptor(self):
        with self.assertRaises(ValueError):publish(self.root,self.work/'published/wrong-version',self.anchor)
    def test_overlapping_publication_paths_block(self):
        with self.assertRaises(ValueError):publish(self.root,self.root/'nested',self.anchor)
    def test_failed_atomic_rename_publishes_no_version(self):
        with patch('release_tooling.package.os.rename',side_effect=OSError('injected rename failure')):
            with self.assertRaises(OSError):publish(self.root,self.destination,self.anchor)
        self.assertTrue(self.root.exists());self.assertFalse(self.destination.exists())
        self.assertFalse((self.destination.parent/(self.destination.name+'.publish-lock')).exists())
