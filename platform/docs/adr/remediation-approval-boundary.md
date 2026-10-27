# Autopilot remediation

**ADR-07 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Remediation must not erase source history or overrun costs after a failure.

**Decision:** Automate only allowlisted idempotent retry/repair operations with stable request IDs, bounded retry/backoff and scoped targets. Human approval for every rewrite, restore, delete or new grant.

**Alternatives considered:** Unrestricted agent-generated SQL or autonomous destructive actions.

**Consequences and acceptance:** Read-only diagnostic app cannot access executor credentials. Approval binds exact target/version/action/expiry; dry-run and compensating rollback required; sleep/exhausted budget prevents execution.

**Contract:** [security-ownership.json](../../contracts/architecture/security-ownership.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
