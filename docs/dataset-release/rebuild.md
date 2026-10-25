# Rebuild and verification runbook

Use Windows x64 CPython 3.10.10 and the base-binary hashes in `runtime/runtime-lock.json`. Use a new directory with enough space for the full historical lineage and disposable validation mirrors. Heavy jobs run sequentially. Do not reuse a generated-data or checkpoint directory and do not install user/system-site packages in the clean venv.

The release includes an offline Git bundle containing all pinned producer revisions through the Phase 8 commit. Clone that bundle into a new workspace, then copy the release tools, test file and release documentation into that checkout. Verify those copied files against the trusted payload manifest before executing them. In the development repository the same modules already exist.

```powershell
$ReleasePackagePath = 'C:/HealthCare_Solution/data/releases/healthcare-synthetic-v1.0.2'
git clone --branch main "$ReleasePackagePath/producers/producer-history.bundle" rebuild-workspace
Copy-Item -LiteralPath "$ReleasePackagePath/reproducibility/release_tooling" -Destination rebuild-workspace/release_tooling -Recurse
Copy-Item -LiteralPath "$ReleasePackagePath/reproducibility/tests/test_dataset_release.py" -Destination rebuild-workspace/tests/test_dataset_release.py
Copy-Item -LiteralPath "$ReleasePackagePath/docs" -Destination rebuild-workspace/docs/dataset-release -Recurse
cd rebuild-workspace
python -m release_tooling.rebuild --output output/new-clean-build --wheel "$ReleasePackagePath/runtime/tzdata-2025.2-py2.py3-none-any.whl"
```

The rebuild creates a new venv, installs the wheel offline with `--require-hashes`, and archives every producer from its exact Git revision. It starts with zero generated snapshots/checkpoints, then passes only freshly generated parent canonical files and manifests to subsequent stages. The historical native source parent is rebuilt as well. Every primary table's bytes/count and every stage business digest must match its accepted anchor. A populated run directory is rejected; a failed run remains evidence, and another cold run uses a new directory. Select `--branch main` when cloning the bundle: a branch-only bundle has no remote HEAD and a plain clone may select an unborn host-default branch.

After generation, the certification command regenerates the final native simulation, stages only the primary publishable files and validates that exact staged canonical/native payload with the frozen full validators. Each version uses a new `certifications/<release-id>/` workspace under the clean build; existing workspaces are rejected, so a packaging correction cannot reuse an earlier validation database. An unchanged verified cold lineage can support a corrected packaging version, but all staged-file checks run again. It verifies unchanged earlier evidence, all original row/table limits and current review hashes. Full history profiling, independent consumers, historical cutoffs, six reports, 318 snapshots, all duplicate deliveries and fifteen fault/delivery outcomes execute against the staged files.

```powershell
python -m release_tooling.certification --clean-build output/new-clean-build --staging output/new-release-staging --release-id healthcare-synthetic-v1.0.2
python -m release_tooling.cli verify --package output/new-release-staging --descriptor-sha256 <trusted-descriptor-sha256>
```

Rebuilt business/source digests must match; run timestamps, environment paths and audit-log bytes can legitimately differ across certification executions. A new audit envelope therefore has a new descriptor even when normalized business content is identical. Do not overwrite an existing published version or copy a prior owner's acceptance to a new descriptor.

Use `python -m unittest discover -s tests -p test_dataset_release.py -v` for release-tool fixtures. Full end-to-end certification additionally runs the entire cold lineage and full-population published-file validators; fixture success alone cannot certify a healthcare release.

Publication is create-once and atomic at the directory boundary. Read the technical gate's descriptor hash, verify the package, then publish to an unused version path. Record explicit owner approval only after the owner reviews the descriptor, evidence, attached domain review and limitations. The CLI never generates approval by default.

```powershell
python -m release_tooling.cli publish --staging output/new-release-staging --destination data/releases/healthcare-synthetic-v1.0.2 --descriptor-sha256 <trusted-descriptor-sha256>
python -m release_tooling.cli state --package data/releases/healthcare-synthetic-v1.0.2 --registry data/release-registry --descriptor-sha256 <trusted-descriptor-sha256>
```

`accept` requires an approval JSON containing `decision=ACCEPT_DATA_RELEASE`, release ID, exact descriptor SHA, limitations SHA, `limitations_acknowledged=true`, identified business owner, `authority=DIRECT_HUMAN_USER_APPROVAL`, the actual approval message, and `separate_solution_authorization_required=true`. The operator must have that real human authorization; a generated sample is not an approval. Acceptance and retirement records are atomic create-once records outside the immutable payload. A process failure before publication/acceptance does not produce a ready/accepted state.

For redistribution, preserve the exact recorded external acceptance/retirement events and verify their SHA256 against the trusted repository gate before copying them to the corresponding registry version directory. Do not manufacture a new approval or silently transfer acceptance to another descriptor. The immutable payload, trusted descriptor and recorded owner decision travel as distinct artifacts.
