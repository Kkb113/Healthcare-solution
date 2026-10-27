# RTI processing, clocks and recovery

**ADR-13 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Specialized real-time mode is not a Delta-sink replacement. Low-volume2h soak cannot validate multi-day LOS distributions.

**Decision:** Supported continuous micro-batch Delta LDP,10s target flow,15s minimum serving sync. Preserve simulation/session/source-instance IDs, independent simulation and wall clocks, corrected seed-plus-event deterministic state, durable outbox and raw archive before late filtering.

**Alternatives considered:** Infinite serverless notebook ProcessingTime loop; stale checkpoints after namespace recreation; discarding beyond-watermark events.

**Consequences and acceptance:** Warmp95 raw/current/Lakebase/screen<15/30/60/75s measured; late beyond15simulationminutes repaired from durablehistory. Fivefixedseeds/fullseasonalyear>=1000completedIPD perseed validate arrivals/LOS±10%, major mixes±3pp. Fullfault/restart/recreate/state-reducer checks mandatory.

**Contract:** [test-workloads.json](../../contracts/architecture/test-workloads.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
