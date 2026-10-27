# ML training location and threshold

**ADR-06 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Small synthetic cohorts favor simple pooled baselines; cloud tuning can exhaust POC funding.

**Decision:** Tune/features prototype locally. Cloud pilot <=INR150; projected final fits <=INR400 and complete ML <=INR1200 inclusive planning FX/tax. At most one selected cloud fit/candidate, no cloud30-trial search. Switch expensive fits to governed local hybrid if threshold exceeded.

**Alternatives considered:** All tuning in cloud; pretending hybrid export/verification/scoring is free; deep models without support.

**Consequences and acceptance:** Both paths require feature export/version hashes, MLflow input lineage, registry signature and cloud parity scoring before promotion; no oracle-driven runtime features. Baseline champions allowed, unsupported models remain explicit.

**Contract:** [ml-eligibility.json](../../contracts/architecture/ml-eligibility.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
