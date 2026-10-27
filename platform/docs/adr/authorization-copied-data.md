# Authorization across copied data

**ADR-12 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Synthetic Workday worker/access_scope records cannot directly grant real cloud permissions; UC row policies do not automatically transfer to copies.

**Decision:** Use trusted Entra tenant/object IDs -> admin-approved facility/persona bridge, deny missing/ambiguous/expired/revoked bindings, per-app SP and user OBO SQL/Genie. Broker enforces facility/PHI on all copied retrieval/live paths.

**Alternatives considered:** Browser-supplied worker/facility headers; shared omnipotent SP; copied notes available to all users.

**Consequences and acceptance:** Broker-only shared search with authorized prefilter+hit validation. Internally synced Lakebase tables cannot carry RLS: broker-only read with verified predicates. App-owned session/budget tables useRLS; revocation<=60s cache, sessions/logs/citations tested.

**Contract:** [security-ownership.json](../../contracts/architecture/security-ownership.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
