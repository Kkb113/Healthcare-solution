# Delivery identity and temporal reconstruction

**ADR-11 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** 3445 valid deliveries have only1001uniqueSHAs; empty scheduled extracts are real observations. Ordinary single-clock SCD2 would lose revisions.

**Decision:** Manifest-scoped delivery key is independent of SHA. Preserve every immutable assertion/version and business-valid/source-known/export/actual-ingest clocks. Deterministic canonical-key MERGE; named current/as-of projections, corrections and signed reversals.

**Alternatives considered:** Hash-only dedup; stable-entity-only key; recomputing original intervals from ingest order; Beta bitemporal AUTOCDC.

**Consequences and acceptance:** Same key/content replay adds audit attempt only; changed immutable payload quarantined; same hash/new identity retained. Forecast fields available only at explicit cutoff. Source matrices generated from exactaccepted schema/dictionary/manifest.

**Contract:** [delivery-temporal.json](../../contracts/architecture/delivery-temporal.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
