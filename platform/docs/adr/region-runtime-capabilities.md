# Region, versions and capabilities

**ADR-03 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Docs show regional availability but cannot establish tenant quotas, feature enablement, exact API schemas or connectivity.

**Decision:** Use East US supported serverless services. Pin customer-controlled CLI/provider/Python/lockfiles and environment5/CURRENT channels; record managed engine patches. Required probes P01–P14 pass before onboarding; P11 optional can be unsupported only safely disabled with P10 passed.

**Alternatives considered:** Assuming every generated SDK resource works; classic fallback; untested Beta dependencies.

**Consequences and acceptance:** Explicit core SQL masks/row filters selected, normal immutable merges, supported sync. Excluded previews have no silent fallback. Unresolved required capability blocks dependent provisioning.

**Contract:** [capability-matrix.json](../../contracts/architecture/capability-matrix.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
