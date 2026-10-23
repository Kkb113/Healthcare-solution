# Master-data generation and acceptance runbook

Use the existing pinned CPython 3.10.10 / tzdata 2025.2 environment. Ordinary generation is offline; public reference packages are already committed and hash-locked. Run from the repository root.

## Complete acceptance

```powershell
python scripts/validate_master_foundation.py
```

This runs the frozen design artifact check and 41 design checks, the complete existing/new test suite, a normal master candidate generation/resume and independent read-only inspection. It writes [validation-report.json](../../evidence/master-data/validation-report.json) and [acceptance-gate.json](../../evidence/master-data/acceptance-gate.json). A new evaluation first marks evidence `EVALUATING`; exceptions or failed checks leave a blocking result, not a stale pass.

The tests include full-cohort clean rebuild, a changed seed, cached resume, real subprocess crash/recovery, selective invalidation, consumer/as-of probes, negative controls and all earlier regression tests. Temporary test candidates are removed afterward. A changed seed can pass all data checks while remaining `REVIEW_PENDING`; the recorded review is specific to its sampled content.

## Generate and inspect the current master candidate

```powershell
python scripts/generate_master_data.py --output output/master-foundation
python scripts/validate_master_data.py --output output/master-foundation --report output/master-foundation/independent-validation.json
```

The generated data stay in ignored output directories. Each canonical file uses a descriptive name, for example `canonical/patient.jsonl`, `canonical/worker-assignment.jsonl` and `canonical/patient-coverage.jsonl`. Logical table/column names remain identical to the frozen Databricks schema, with exact decimal strings, UTC timestamps and no nested business records. These files are suitable source artifacts for later Databricks loading; no table migration or cloud deployment runs now.

| Artifact | Interpretation |
| --- | --- |
| `manifest.json` | Current run status, input locks, stage lineage/checksums, row/file/byte counts and remaining release budget |
| `canonical/*.jsonl` | The 78,922 canonical master/opening-context records |
| `checkpoints.sqlite3` and managed WAL/SHM companions | Transactional stage copies, attempts and defect state; do not edit manually |
| `validation-report.json` | Full-row schema/business validation, metrics, keyed findings, as-of and review status |
| `identity-review-sample.md` | Deterministic 150-row review mirror with a content hash |
| `candidate-ready.json` | Created only for a passing master gate; never means final healthcare data acceptance |

The manifest counts canonical rows once. Physical materialization is explicit: 78,922 JSONL rows + 78,922 checkpoint mirror rows + 150 review rows = **157,994 serialized row copies** in a normal run. The deliberately committed review-document copy is another 150-row review mirror outside that run. There are no published Workday/Axiom production exports yet. Temporary test/alternate runs have their own manifests and are not silently added to a release.

## Restart and configuration changes

```powershell
python scripts/generate_master_data.py --output output/master-recovery --fail-stage coverage
python scripts/generate_master_data.py --output output/master-recovery
python scripts/generate_master_data.py --output output/master-crash --crash-stage coverage
python scripts/generate_master_data.py --output output/master-crash
```

Use a new directory to trigger an execution hook; a reused stage does not rerun its hook. Ordinary execution failures return 1, validation/review blocks return 2, and the deliberate process crash returns 97. Success returns 0. The independent command returns nonzero on any integrity/data/review block. PowerShell may render a nonzero native command as a failed tool call; the test suite verifies subprocess behavior directly.

Each run has one OS writer lock. Stage outputs and checkpoints publish in one SQLite transaction. An exception/process death leaves the unfinished stage uncommitted. Before recomputation, a changed upstream stage and its transitive descendants are invalidated. Cached payloads are checksum-verified. A corrupt checkpoint is retained for investigation; rebuild in a new directory. A failed/incomplete manifest and absence of `candidate-ready.json` prohibit consumption even if old canonical files remain on disk.

Copy [master-data-generation.json](../../config/master-data-generation.json) into an ignored directory to experiment with assumptions, then pass `--config`. The profile, cohort, business window and frozen row budgets are enforced. JSON object ordering cannot change individual weighted draws; list ordering remains explicit reference/configuration content. Never bypass budget failure by dropping connected records. Source reference changes require lock review, regeneration, sample review and the full gate.

The [query helpers](../../src/healthcare_synthetic/master_queries.py) demonstrate stable-person as-of lookup, eligible workers, primary coverage, typed source mappings and scope revocation. The [source-format probes](../../src/healthcare_synthetic/source_identity_projection.py) demonstrate source-specific names and keys. These are bounded dataset contract tests, not an analytics platform, live integration or production authorization service.

## Reference maintenance

Only when intentionally refreshing reviewed references:

```powershell
python scripts/import_public_references.py --names --download-codes --codes
python scripts/import_public_references.py --lock
```

The first command may use public network access. The second explicitly updates checksum approval; inspect the changes before accepting any candidate. Full public downloads remain ignored. The SSA fallback, raw hashes, curated-label exclusions and dated-code selection are documented in [reference provenance](reference-provenance.md).

Phase 2 completion makes the longitudinal clinical-history phase eligible when requested. Do not create encounters, services, operational ledgers, claims, forecasts, dashboards, agents or cloud resources as part of this master-data command. The complete dataset and Azure Databricks solution remain gated by later acceptance.
