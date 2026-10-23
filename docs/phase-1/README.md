# Phase 1 — reproducible framework and validation harness

Phase 1 implements the generation controls needed before realistic population generation. The [gate](../../evidence/phase-1/gate.json) and [execution evidence](../../evidence/phase-1/validation-report.json) record the tested result. Phase 2 has not started. The full healthcare dataset is not accepted, and the solution remains `BLOCKED_FOR_SOLUTION`.

The frozen Phase 0 baseline remains **25 business tables, 1,958,210 planned records and 41,790 reserve records** for 2023–2025. No Phase 0 contract or historical evidence was changed. Phase 1 publishes only a small local development fixture: **30 scalar rows in 15 explicit projections**, plus **3 separately counted Workday/Axiom serialized mirror rows**. This is not the complete 25-table schema or a clinically realistic population. Two bed-interval rows are disposable reconstruction fixtures for `bed_event`, not a 26th business table.

Read the [architecture and controls](architecture.md), [runbook](runbook.md), [fixture coverage and hand calculations](fixtures-and-validation.md), [build/reuse decision](build-reuse-decision.md), and [review and exit criteria](review-and-gate.md).

## Delivered components

| Component | Implementation |
| --- | --- |
| Approved development configuration | [phase1-development.json](../../config/phase1-development.json), [profile contract](../../contracts/phase1/profile-contract.json) |
| Frozen miniature references and rule fixtures | [Reference fixtures](../../contracts/phase1/reference-fixtures.json), [55 rule-family cases and 123 faults](../../contracts/phase1/rule-fixtures.json) |
| IDs, stateless random streams, scheduler, calendar, code versions, money | [core.py](../../src/healthcare_synthetic/core.py) |
| Transactional DAG runner, manifests, checkpoints, invalidation and budgets | [engine.py](../../src/healthcare_synthetic/engine.py) |
| Configurable module implementations for development fixtures | [stages.py](../../src/healthcare_synthetic/stages.py) |
| Source serialization, bounded replay, quarantine and recovery | [sources.py](../../src/healthcare_synthetic/sources.py) |
| Independent validation, profiles, reconciliation, defects and gates | [validation.py](../../src/healthcare_synthetic/validation.py) |
| Standalone read-only candidate inspection | [validate_phase1_candidate.py](../../scripts/validate_phase1_candidate.py) |
| Reproducible Phase 1 gate command | [validate_phase1.py](../../scripts/validate_phase1.py) |

The 55 Phase 0 quality rules retain `SPECIFIED_NOT_DATA_EXECUTED` in the release contract. Their rule families now have executable hand-calculated microfixtures and negative controls. Full-table executors, official vocabulary loading, population realism, clinical trajectories, complete Workday/Axiom layouts, and release-scale validation remain required in their planned phases. A passing microfixture is not evidence that a nonexistent 1–2 million-row dataset has passed those rules.
