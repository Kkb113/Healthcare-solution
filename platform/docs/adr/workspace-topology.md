# Workspace topology

**ADR-01 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Existing workspace/account/metastore are shared administrative foundations; changing region does not cure subscription model quota.

**Decision:** Retain intellify-healthcare-dbw (7405619366453187), Premium SERVERLESS, East US, with hc_dev/hc_test/hc_prod and hc_ops catalogs; use dedicated rg-hcp-dev supporting resources. hc_prod is synthetic demonstration only.

**Alternatives considered:** Replacement/classic workspace; Fabric/PowerBI; multi-workspace real-data topology.

**Consequences and acceptance:** One-workspace catalog isolation must pass direct-object and copied-store authorization tests. No claim of real-data production isolation.

**Contract:** [security-ownership.json](../../contracts/architecture/security-ownership.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
