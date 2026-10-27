# Infrastructure and lifecycle ownership

**ADR-02 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Dual deployment owners cause permission/state drift and unreliable sleep/wake.

**Decision:** Terraform owns foundations/workspace infrastructure; Bundles own supported jobs/pipelines/apps/dashboards; one versioned API adapter owns search, Lakebase, Genie and serving. Existing workspace is reference-only. Adopt/import prior authorized prerequisites without recreation.

**Alternatives considered:** Ad hoc manual changes; mixed agents.deploy and Bundle ownership; Beta Postgres bundle dependency.

**Consequences and acceptance:** Resource register specifies owner, state scope and rollback. Sleep invokes owner, refresh/import reconciles disposable deletion; CI privileged bootstrap remains operator-controlled.

**Contract:** [security-ownership.json](../../contracts/architecture/security-ownership.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
