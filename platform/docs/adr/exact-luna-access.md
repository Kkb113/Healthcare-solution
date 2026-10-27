# Exact GPT-6 Luna route

**ADR-04 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Native ADI route failed despite metadata. Readiness tool round trip passes. Current5RPM/5000TPM is insufficient concurrent-user sizing.

**Decision:** Use existing Databricks Unity Gateway Responses route -> UC service credential/managed identity -> Azure OpenAI gpt-6-luna revision2026-09-22 US DataZoneStandard in subscription0725b5e7-75db-4c60-b5e9-928c3df3fcd1. Never substitute a different model silently.

**Alternatives considered:** Workspace region move; API-key secret; claiming native entitlement; unreviewed Global processing fallback.

**Consequences and acceptance:** P05 must price and size exact token/RPM/TPM workload with20% headroom, adjust capacity within verified quota or block. Quota increase/support may be required; no latency guarantee from model access alone.

**Contract:** [probe-matrix.json](../../contracts/architecture/probe-matrix.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
