# Phase 0 baseline version 1.0.0

**Status:** See the [review and gate record](review-and-gate.md) and executable [validation report](../../evidence/phase-0/validation-report.json). No future data phase has been performed.

Phase 0 finalizes the scope, physical table grains, field dictionary, relationships, history semantics, source contracts, business rules, realism assumptions, and three-year record budget. The machine-readable definitions are under `contracts/phase0/`; the documents explain the decisions and limits rather than promising a complete clinical EHR in two million records.

| Frozen design choice | Baseline |
| --- | --- |
| Window | 2023-01-01 through 2025-12-31 inclusive; 1,096 local days and 36 months |
| Geography and currency | Fictional Illinois hospital group; America/Chicago; USD; calendar fiscal year |
| Facilities and capacity | Three community hospitals, 24 beds each: four ICU/stabilization and 20 medicine/surgery |
| Patient scope | Adults aged at least 18 at each service; 20,000 stable patients plus demographic revisions |
| Clinical history | 56,000 intersecting encounters; additional opening-only AR context; 580,000 clinical-event/version rows; 95,000 condition/assertion versions |
| Workforce | 300 stable workers; 900 assignment versions; 70,000 shift/leave/version rows |
| Row envelope | 1,958,210 across 25 tables, inclusive of openings, revisions, corrections and all declared business facts |
| Reserve | 41,790 below the hard two-million canonical business-row ceiling |
| Source support | Workday-style workforce/security extracts, Axiom-style financial exports, clinical/billing/inventory feeds, bounded ADT replay |
| Phase limit | Contracts and design checks only; no generator, patient data, deployed SQL tables or solution products |

## Navigation

1. [Scope and decisions](scope-and-decisions.md): what is modeled, what is deliberately outside scope, causal dependencies and reviewer authority.
2. [Relationships](relationships.md): physical FK map, stable-identity lookups, typed clinical events and as-of joins.
3. [Dictionary](data-dictionary.md): every scalar field, type, nullability, unit, key, meaning and source authority.
4. [Business rules](business-rules.md): operational state machines, clinical coherence, stock/cost/claim/accounting conservation and cutoff policy.
5. [Budget](record-budget.md): all table envelopes, lifecycle allowances, capacity, workload and aggregation arithmetic.
6. [Source contracts](source-contracts.md): field mappings, source schedules, schemas, versions, replacement files and known faults.
7. [Realism and validation](realism-and-validation.md): predeclared targets, source provenance and scenario acceptance.
8. [Review/gate](review-and-gate.md): user-delegated design reviews, findings and next-phase boundary.

All numeric realism parameters are **fictional calibration assumptions** unless an identified public aggregate source supplies the actual weights. Clinical pathway review here is a design review, not a licensed clinical safety certification. Real-data validation remains prohibited from being claimed on this synthetic specification.
