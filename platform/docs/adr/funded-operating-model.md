# Funded build/demo operating model

**ADR-10 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review; funded POC scope explicitly approved by user.

**Context:** Regional prices include search24h deletion tails, app minima, CPU serving concurrency and uncertain Lakebase/serverless usage; native Genie is billed separately from Luna.

**Decision:** Retain INR20000 build and INR6000 monthly target per explicit user decision. Adopt the reduced POC workload explicitly approved by the user; full original test repetition exceeds ceiling. Approved one3h monthly demo, or two1h demos, with no unchanged batch retraining.

**Alternatives considered:** Relying on credits/promotions or Azure budget alerts as hard caps; silently dropping tests; unapproved INR45000 proposal.

**Consequences and acceptance:** Shared durable atomic app reservations, separate native Genie Block usage scopes, all-subscription ledger and external guard. Quantities are estimates until tenant pilots. Cost shocks/extra lifecycle force re-estimation and may block later gates.

**Contract:** [cost-model.json](../../contracts/architecture/cost-model.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
