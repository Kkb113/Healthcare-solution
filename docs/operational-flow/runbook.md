# Operational data runbook

Use the repository's locked Python runtime and tzdata package. Generation is local and offline after the pinned public reference packages are available. No Azure or source-system credentials are required.

## Preserve the accepted inputs

The operational profile consumes the exact accepted master and clinical snapshots. On a fresh clone, restore them with their committed generators:

```powershell
python scripts/restore_master_snapshot.py
python scripts/restore_clinical_snapshot.py
```

Restoration refuses to overwrite an existing destination and verifies its acceptance hash. Do not regenerate an accepted parent in place using a later source checkout: historical profiles bind all source modules into generation metadata. The historical clinical regression runner uses the exact accepted Git revision and the unchanged parent data. Current framework/master and operational tests execute against current code.

## Generate and validate

```powershell
python scripts/generate_operational_flow.py
python scripts/validate_operational_data.py --report output/operational-flow/independent-inspection.json
python scripts/validate_operational_foundation.py
```

A first run can produce REVIEW_PENDING after all data checks pass. Inspect output/operational-flow/operational-review-sample.md. Record the designated review with its sample and selected-fact hashes in reviews/operational-flow-review.json, then rerun generation. Review-only changes reuse business stages and reevaluate validation. No approval record is fabricated automatically by the generator.

The acceptance script verifies frozen design hashes, independently rereads canonical data and checkpoint mirrors, and executes current framework/master tests, the exact accepted clinical regression group and current operational tests. Passing test results may be reused only when all current source/test/script hashes remain identical; operational test reuse additionally requires the same candidate business hash. A source change during evaluation blocks the gate.

Generated business rows and checkpoints stay under ignored output/. Selected review and acceptance evidence are versioned. Check candidate-ready.json and manifest status before consuming a candidate. A RUNNING, FAILED, BLOCKED or REVIEW_PENDING candidate is not accepted.

## Query derived state

```powershell
python scripts/query_operational_state.py --at 2024-07-15T18:00:00Z --known-at 2024-07-15T18:00:00Z --sex F --isolation
```

This local read-only projection verifies its four canonical input files, reconstructs delivered historical bed events and reports licensed, staffed, occupied, reserved, immediately available and patient-compatible counts. It excludes the empty partner bed of a private-isolation occupant. Missing delivered peer demographics yield unknown compatibility rather than a fabricated match. A staffing shortfall never removes an occupant. Interval/state/availability projections are views, not extra published business tables.

## Recovery and troubleshooting

A single writer owns a candidate. Checkpoints commit complete stages with checksums; corruption fails closed. After a real interruption, rerun the same command and configuration. Completed valid stages are reused, while unfinished transactions are rolled back. Ready markers are removed before any attempted recomputation. Do not manually edit canonical files or checkpoint payloads to make a gate pass.

For experimental seeds/configuration, use a separate output directory and a separate content-bound review. Frozen phase-zero contracts require baseline review before modification. The final 20-25-table and 1-2-million-row acceptance requirement applies to the complete Phase 9 release, not to this intentionally partial 16-table candidate.
