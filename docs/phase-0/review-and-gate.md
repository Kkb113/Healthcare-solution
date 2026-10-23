# Phase 0 review and gate record

**Baseline:** 1.0.0  
**Review date:** October 23, 2026  
**Business owner:** Kkb113  
**Designated reviewer and implementer:** Codex  
**Delegation:** The user explicitly instructed Codex to review and finalize Phase 0.  
**Phase status:** PASSED for design/contract implementation.  
**Next phase:** Phase 1, not started.  
**Solution status:** BLOCKED_FOR_SOLUTION.

This review evaluates the specification and its design arithmetic. It is performed under user delegation, not represented as an independent licensed clinical review or live Workday/Axiom certification. No synthetic patient charts, financial transactions or operational records have yet been generated, so their later validation/review gates remain unperformed.

## Baseline reviews performed

| Review area | Review performed | Result |
| --- | --- | --- |
| Business scope | Adult community care, complete modeled inpatient census, patient identity, primary payer, explicit service exclusions and three-year boundaries | Accepted as a bounded synthetic design; no undisclosed background occupancy or extra business tables |
| Clinical assumptions | Longitudinal condition families, adult eligibility, selected observation scope, orders/results/admin sequencing, drug-allergy families, medication schedule fields, notes and censoring | Accepted as design assumptions; actual clinical generation and chart plausibility review still required in Phases 3/8/9 |
| Operations/workforce | 72 physical beds, opening states, transfer intervals, time-weighted capacity, lifecycle versions, RN workload/roster capacity, credential/history and stock conservation | Arithmetic and constraints pass design checks; local shift/queue/stock behavior awaits generated-data validation |
| Finance | Claim versus attempt identities, unbilled/billed AR, opening balances, double entry, expense timing, monthly pool close, allocation fan-out, P&L movement versus balance levels and forecast vintages | Accepted simplified accounting model with exact conservation requirements and explicit data-phase checks |
| Source integration | Typed Workday keys, security scope, separate roster source, 12 representative Axiom layouts, manifest/replacement/fault semantics | Accepted simulation contracts; actual tenant inventory/certification explicitly excluded |
| Technical schema | 25 scalar business tables, all fields/types/units/nullability, physical and logical references, offline DDL, source mappings, deterministic metadata build and validator negative controls | Accepted; no live DDL executed or general data-generation framework claimed |

## Material findings resolved before baseline freeze

1. **Earlier scale exceeded the detail budget.** Replaced provisional 300-bed assumptions with a complete 72-bed modeled network. Retained realistic identities, detailed clinical-event rows and longitudinal histories instead of truncating children.
2. **Final-only encounters would leak future outcomes.** Budgeted 130,000 encounter rows for initial, lifecycle and correction versions; source and knowledge times are explicit.
3. **Opening AR lacked prior service context.** Included 2,000 pre-window closed encounter/claim contexts and original line/balance history. They do not inflate current admissions, occupancy or revenue.
4. **Daily cost allocation could exceed the cap or double expenses.** Defined explicit monthly pool-close reclassification journals and 180,000 counted allocation rows, including cross-month/transfer detail and revisions. Only eligible pool lines allocate; total GL expense is unchanged.
5. **Monthly totals could conceal account-period errors.** Froze the account/center/month/vintage grid and independently recomputed each product. Negative tests reject offsetting grid errors with an unchanged grand total.
6. **Cash, recognized revenue and claim AR could be conflated.** Separated gross/net service recognition, unbilled services, first-submission assignment into billed claim AR, adjudication adjustments and cash. Opening AR is not added twice.
7. **Balance-sheet levels are not monthly movement.** Axiom actual P&L uses movement; balance accounts use cumulative closing balances. Historical January-known December close remains unavailable to December as-of consumers.
8. **Drug allergy/product and dose history needed explicit structure.** Added ALLERGEN families, formulation, intended order intervals/PRN maximum, specimen/result-ready timestamps, administration sequences and nonconsuming cancelled-event semantics.
9. **Raw mirrors and report counts could hide volume.** Canonical rows and serialized file copies are reported separately. The 900-report assumption is bounded to 12 explicit layout families without pretending that a tenant inventory was tested.
10. **Generated metadata could drift from narrative contracts.** Added a deterministic authoring/render command with `--check`, contract hashes, link checks and mutation tests. Data-quality rules remain honestly marked specified, not data-executed.

## Phase 0 acceptance evidence

| Exit requirement from implementation plan | Evidence | Disposition |
| --- | --- | --- |
| Scope, cohort and facilities finalized | `scope-and-decisions.md`, `baseline.json` | PASSED |
| 20-25 complete tables and field-level dictionary | `schema.json`, `data-dictionary.md`, `databricks-schema.sql` | PASSED |
| Keys, relationships and historical semantics | `relationships.md`, physical/logical reference checks | PASSED |
| Feasible three-year record and resource budget | `record-budget.md`, independent capacity/financial-grid/allocation checks | PASSED |
| Clinical/operational/financial business rules | `business-rules.md`, clinical matrix and 55 rule definitions | PASSED as specification, not future data execution |
| Source contracts and approximately 900-export assumption resolved for simulation | `source-contracts.md`, `source-contracts.json` | PASSED for stated simulation scope |
| Realism targets/provenance and connected scenarios | `realism-and-validation.md`, 12 targets, 12 scenarios | PASSED as preregistration |
| Domain review responsibilities assigned and reviews recorded | User delegation and reviews/findings above | PASSED for baseline review |
| Reproducible design validation and negative controls | `evidence/phase-0/validation-report.json`, standard-library unit tests | PASSED; run commands below reproduce evidence |
| No unresolved blocking baseline decisions | Frozen working assumptions/exclusions and issue dispositions above | PASSED; later generation/vendor tests are not claimed complete |

The final row budget is **1,958,210**, with **41,790** remaining below the hard two-million ceiling. Actual generation is zero. Actual future data validation, live schema execution, sampling clinical charts and vendor tenant tests are not performed by this gate.

## Reproduction and reopening

Run from the repository root:

```powershell
python scripts/build_phase0_spec.py --check
python scripts/validate_phase0.py --report evidence/phase-0/validation-report.json
python -m unittest discover -s tests -v
```

Current evidence records 41 passing design/artifact checks and 23 passing contract tests, including negative controls. If the schema, code, budget, source contracts or accepted assumptions change, rebuild metadata, rerun checks, re-review affected decisions and version the baseline. Do not treat this review as a waiver of any later phase exit criterion.

Phase 1 may be requested next. No automatic progression into generation or any analytics solution is part of this Phase 0 commit.
