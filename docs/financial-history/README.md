# Connected financial histories

Phase 6 completed on October 24, 2026, with all four exit criteria passing, 280 tests without failures/errors/skips, nine financial control groups and a recorded 60-case review. Its candidate contains **1,924,164 canonical records across 25 tables**.

This package implements Phase 6 for the three fictional Illinois adult hospitals. It extends the accepted workforce/inventory snapshot with service charges, original institutional receivable accounts, claim lines/events, double-entry postings, patient cost allocations and canonical Axiom monthly values. All accepted clinical/resource rows remain unchanged; five explicit local billing vocabulary rows are appended.

The [generation design](generation-design.md) defines the accounting and historical-availability semantics. The [budget amendment](record-budget-amendment.md) explains the reviewed 25-table, 1,995,215-row envelope and 4,785-row reserve. The [runbook](runbook.md) covers immutable-parent restoration, generation, validation, recovery and read-only consumer checks. The [validation/review guide](validation-and-review.md) maps controls and tests to the four exit criteria.

The [variance lineage guide](variance-lineage.md) traces demand, payer/service mix, price/rate changes, agency use, denial recovery, resource consumption and timing differences back to the counted source facts and their independently reconciled postings.

The completed scope is established by the [acceptance gate](../../evidence/financial-history/acceptance-gate.json) and [complete evidence](../../evidence/financial-history/validation-report.json). Generated JSONL/SQLite files remain under ignored `output/financial-history/`; no business data files are committed. The [review decision](../../reviews/financial-history-review.json) binds the [60 complete financial traces](../../reviews/financial-history-sample.md).

These are selected synthetic facility accounts and captured resource costs. They are not full professional billing, all hospital payroll/materials, certified payer claims, tenant exports or audited accounts. Source file serialization and delivery replay belong to Phase 7. Full dataset acceptance remains Phase 9; analytics, dashboards, models, agents and live integrations remain blocked.

The [restoration check](../../evidence/financial-history/restoration-check.json) reproduces all 18 accepted parent files exactly. The [consumer checks](../../evidence/financial-history/consumer-checks.json) verify claim cash/AR, selected patient/nonpatient costs and publication-aware monthly replacement selection. The formal envelope retains 71,051 unused planned rows and 4,785 reserve rows below two million.
