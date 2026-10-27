# Operational alerts

**ADR-08 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Delayed system tables cannot deliver operational SLA; optional inbound webhook must not become anonymous workaround.

**Decision:** Teams incidents and daily email summaries, redacted and idempotent; verify exact authorized destinations before Phase11 first send. Required authenticated API polling <=120s, detection<=15wall minutes.

**Alternatives considered:** System-table-only detection; mandatory unsupported inbound handler.

**Consequences and acceptance:** P11 can be UNSUPPORTED_DISABLED only with removed route/security finding closed and polling passed. Outbound destination access remains required later; Phase0 sends no messages.

**Contract:** [probe-matrix.json](../../contracts/architecture/probe-matrix.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
