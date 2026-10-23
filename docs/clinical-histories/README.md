# Longitudinal clinical foundation

Phase 3 is complete for its defined scope: 840,061 canonical rows, 58,000 encounter contexts, 159 passing repository tests, 15 clinical check groups and 100 reviewed journeys on the accepted master foundation. The generated data remains a **provisional clinical candidate** until capacity, staffing and stock integration in subsequent phases. The Azure Databricks solution remains blocked until final dataset acceptance.

- [Generation design](generation-design.md) defines the history, capture granularity and temporal semantics.
- [Reference and scope review](reference-and-scope-review.md) records supported assumptions and clinical limitations.
- [Validation and review](validation-and-review.md) explains actual counts, planning allocation differences and scoped review.
- [Runbook](runbook.md) covers snapshot restoration, generation, restart, inspection and acceptance.
- [Clinical history policy](../../contracts/clinical-history-policy.json) and [configuration](../../config/clinical-history-generation.json) define the versioned controls.
- [Acceptance evidence](../../evidence/clinical-histories/acceptance-gate.json) records executed exit criteria.
- [Journey review](../../reviews/clinical-journey-sample.md) and [review decision](../../reviews/clinical-journey-review.json) record the user-designated synthetic domain review.
