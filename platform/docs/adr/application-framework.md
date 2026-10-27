# Application framework

**ADR-05 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Four apps need consistent identity, errors, budgets and source-citation handling.

**Decision:** Use React front ends and FastAPI back ends in Databricks Apps. Execute the versioned MLflow ResponsesAgent inside the FastAPI app, with its own chat API; no third standalone Model Serving endpoint. Query embeddings run in this costed app CPU with the same pinned local document-embedding model. Share typed contracts, auth/query/citation clients; keep privileged remediation backend separate.

**Alternatives considered:** Independent duplicated apps; shared superuser application principal.

**Consequences and acceptance:** Each app receives platform-created identity with narrowly declared resources. User OBO identity and app identity are distinct. Pin front-end/backend dependencies when implemented, no speculative deployment in Phase0.

**Contract:** [security-ownership.json](../../contracts/architecture/security-ownership.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
