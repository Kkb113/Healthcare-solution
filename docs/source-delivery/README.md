# Source export and delivery simulation

Implementation phase: **7**. Acceptance is recorded in [the source gate](../../evidence/source-delivery/acceptance-gate.json). This phase produces source inputs and disposable validation consumers; it builds no production connector, Databricks ingestion pipeline, dashboard, model or agent.

The accepted financial snapshot remains the business truth: **1,924,164 canonical records in 25 tables**, January 2023 through December 2025 with declared opening and closing context. Every scalar column round-trips, including names, dates of birth, clinical text, nulls, decimal representations, source lineage and version identifiers. Source copies do not replace or modify that snapshot.

- [Contracts and source semantics](source-contracts.md)
- [Delivery, challenges and record accounting](delivery-and-faults.md)
- [Rebuild and acceptance runbook](runbook.md)
- [Recorded engineering review](../../reviews/source-delivery-review.json)
- [Validation evidence](../../evidence/source-delivery/validation-report.json)

New filenames describe their purpose; phase numbers appear inside content. Source formats are simulated extensions, **not vendor-certified Workday, Axiom, HL7 or FHIR interfaces**. Customer layouts, tenant APIs and certification remain outside this scope. Microsoft Fabric is excluded.
