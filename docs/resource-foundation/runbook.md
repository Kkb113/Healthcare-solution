# Resource foundation runbook

Use the pinned CPython 3.10.10 runtime and tzdata 2025.2 from the existing repository environment. No Databricks, Workday, Axiom or other live-system credentials are required. All generation is local data-foundation work.

## Immutable parent restoration

Preserve every existing accepted snapshot. On a fresh clone, restore only missing inputs:

```powershell
if (-not (Test-Path output/master-foundation/manifest.json)) {
    python scripts/restore_master_snapshot.py
}
if (-not (Test-Path output/clinical-histories/manifest.json)) {
    python scripts/restore_clinical_snapshot.py
}
if (-not (Test-Path output/operational-flow/manifest.json)) {
    python scripts/restore_operational_snapshot.py
}
```

The operational wrapper rebuilds from exact accepted commit `51ef26af7a1002e6a6074f96b72059f74dbbe5dc`, refuses overwrite and checks its accepted business hash. Historical generators bind their original source checkout; do not regenerate accepted parent directories using later source code. Temporary archive extraction stays inside ignored workspace output, rejects unsafe archive entries and does not change Git state.

## Candidate and acceptance commands

```powershell
python scripts/generate_resource_foundation.py
python scripts/validate_resource_data.py --report output/resource-foundation/independent-inspection.json
python scripts/validate_resource_foundation.py
```

An unreviewed candidate can return REVIEW_PENDING even when its data checks pass. Review `output/resource-foundation/resource-review-sample.md`; record the user-designated review and exact sample/fact hashes in `reviews/resource-foundation-review.json`, then copy the exact reviewed sample to `reviews/resource-foundation-sample.md`. Rerun generation to reevaluate validation. Changing only review or validation code reuses unchanged business stages. A generation-source/configuration change invalidates affected dependencies and requires a new content-bound review if sample facts change.

The final acceptance command checks the frozen design, independent persisted files, current framework/master and operational tests, all accepted historical clinical tests from their exact archived source revision, and current resource tests. Each group records individual cases, failures, errors, skips and before/after source/input hashes. Passing cached tests are reused only for identical source/test/script/configuration/contract/review/parent-gate inputs; the resource group also requires the same candidate hash. Source changes during evaluation block acceptance.

To run a group while diagnosing a failure:

```powershell
python scripts/run_resource_regressions.py --group resource --report output/resource-foundation/resource-tests.json
```

Generated data and checkpoints stay in ignored output/data paths. Gate evidence and selected review mirrors are committed. `candidate-ready.json` and RESOURCE_FOUNDATION_PASSED authorize only this data-foundation candidate; the committed acceptance gate must also pass before phase completion. They never authorize solution development or final dataset release.

## Read-only historical consumers

```powershell
python scripts/query_resource_history.py labor --known-at 2026-01-10T23:59:59Z
python scripts/query_resource_history.py labor --known-at 2025-03-05T18:00:00Z --month 2025-02
python scripts/query_resource_history.py roster --at 2025-02-10T16:00:00Z --known-at 2025-02-10T16:00:00Z
python scripts/query_resource_history.py stock --at 2026-01-01T05:59:59Z --known-at 2026-01-04T09:00:00Z
```

These local fixtures verify canonical input hashes, counts and readiness and fold delivered assertions without modifying data. The previous staff assertion remains visible until its replacement export arrives, even if the final dataset already contains the later source version. Missing early attendance is unknown. The labor month filter groups by local planned-start service month; it is not a split-month financial accrual/allocation rule. The stock view reports the batch delivered-source book ledger, not a live cabinet count. `--include-balances` adds the lot/location detail.

## Recovery

One writer owns a candidate. Complete stages commit transactionally in SQLite WAL; a process crash rolls back the incomplete stage. Rerun the same command to reuse valid stages and finish. A changed dependency invalidates descendants before attempted recomputation. Ready markers are removed before publication work. Corrupt checkpoints, changed accepted inputs, unsupported profiles and unexplained data differences fail closed. Never hand-edit source facts, checksums or accounting amounts to force acceptance.

Use a separate ignored output directory for experiments. Preserve source/config/review inputs while final regressions run. The 18-table candidate is intentionally partial; the final release must meet all 20-25-table and 1-2-million-record criteria at Phase 9.
