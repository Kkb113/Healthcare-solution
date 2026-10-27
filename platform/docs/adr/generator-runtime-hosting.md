# RTI generator hosting

**ADR-09 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Ephemeral process memory and Kafka ACKs do not prove recoverable accepted state.

**Decision:** Databricks App with durable Lakebase transactional generator/RNG/outbox state, session/event caps, four-hour maximum runtime and independent external shutdown. Create only after batch Phase12 gate.

**Alternatives considered:** Unbounded laptop stream; process-local RNG/outbox; always-on namespace.

**Consequences and acceptance:** Stable event IDs on retry, archival reconciliation before transport deletion, new source-instance checkpoints on recreation. Bound maximum1million build ingress/250000sessionevents; no new patient identity feed.

**Contract:** [test-workloads.json](../../contracts/architecture/test-workloads.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
