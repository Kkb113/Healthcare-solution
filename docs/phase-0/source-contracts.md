# Source contracts and data availability

Machine-readable contracts contain a canonical export mapping for every field of all 25 tables, eight named operational/vendor source families, 12 representative Axiom layout families, manifest fields and seven controlled fault classes. These specify simulated interfaces, not tested live integrations.

## Source authority and scheduling

| Source family | Authority and target | Cadence / mode |
| --- | --- | --- |
| EHR registration | Patient identity and demographic history | Registration/change revisions; stable MRN and patient identity |
| EHR coverage | Enrollment and primary payer | Effective/knowledge-dated changes; explicit self-pay |
| EHR clinical / scheduling | Conditions, orders, scalar results, modeled administrations, notes and appointments | Event/slot/revision payloads; no hidden multi-analyte arrays |
| ADT / bed | Encounter lifecycle and bed states | Immutable message ID, bed sequence, effective/recorded/delivery instants; bounded historical replay |
| Workday workers | Workers, primary assignments, managers, effective cost/rates and role/credential assumptions where included in the contracted test extract | Weekly full Sunday 07:00 UTC plus daily changes 07:00 UTC |
| Workday organizations | Cost centers and typed source associations | Weekly full snapshot; exact source-key mapping |
| Workday security | Synthetic principal roles, scopes and revocations | Daily versioned delta; no live identity provisioning |
| Roster/time | Published shifts, revisions, actual attendance and loaded shift cost | Explicit separate scheduling/time source contract; not presumed in Workday worker extracts |
| Inventory/pharmacy | Lots, stock movements, resource quantities and prices | Signed movements with paired transfers and consumption groups |
| Billing/RCM | Charges, original claim lines, submissions, adjudication and remittance movements | Event/line histories; attempts do not replace original claim identity |
| Synthetic GL/cost accounting | Balanced daily source groups and monthly pool-close/reclassification lines | Derived from represented resource and financial facts with reproducible group predicates |
| Axiom | Selected monthly actuals, original/revised budgets, quarterly forecast vintages and operational statistics | Monthly actual/statistical close day 5; scenario vintages appended, correction exports replace declared version/scope |

UTC batch schedules avoid ambiguous local daylight-saving trigger times. Service and clinical days still use America/Chicago, including 23/25-hour days.

## Formats, keys and transforms

- Canonical fixtures use UTF-8 RFC4180 CSV or schema-typed Parquet. Empty/null treatment, decimals and timestamp parsing follow the field dictionary, not guessed string coercion.
- Event fixtures use NDJSON envelopes with unique source message ID, schema version, source key, event occurrence, recording, sequence, delivery and correction reference. They are ADT-compatible semantic test payloads, not a falsely certified HL7 interface.
- Worker `EmployeeID`, manager IDs, cost-center codes and source principal IDs resolve through the typed crosswalk at valid and knowledge time. Name matching is never an identity key.
- Axiom account and cost-center references use source-specific mappings. Periods become first-of-month DATE values; amount/quantity and USD/statistical units remain separate.
- Axiom wide month columns unpivot into counted scalar finance rows. Comparison/variance exports validate recalculated differences, not additional additive actuals. Mapping exports populate existing catalog/cost-center/crosswalk tables.
- Every source row/version retains source_system, source_record_id, recorded_at, export_available_at and generation_run_id. Vendor field aliases and required/nullable rules are in `source-contracts.json`.

## Axiom report coverage and financial series

The approximately 900 reports in the reference are registered as report definitions, not assumed 900 populated files per month. The baseline exercises 12 layout families: actual-long, actual-wide-months, actual-with-adjustments, budget-original, budget-revised, forecast-amount, forecast-drivers, statistics-volume, statistics-workforce, variance-comparison, account-mapping and center-mapping.

All families have fixtures in the future source-simulation phase. Actual file counts, empty reports and serialized row counts are reported honestly. An unseen tenant's complete 900-report inventory is not claimed implemented by this baseline.

The financial series grid is frozen in the record budget. ACTUAL P&L uses monthly net movement; balance accounts use cumulative closing balances, including opening entries. Balance-sheet postings are mapped to three designated facility control cost centers; P&L expense/revenue retains the performing responsibility center. Journals balance by entity/currency and may cross centers.

Budget originals are published December 15 before each plan year. Midyear revised budgets cover Jul-Dec 2024 and Jul-Dec 2025. Quarterly forecasts cover three target months in the same quarter; only registered selected accounts/centers are forecast, not an uncounted dense cross product. Each vintage retains publication time. Historical queries choose the appropriate known version rather than the final revised file.

## Business cutoff and final export grace

Observed business activity ends at local midnight after December 31, 2025. Existing pre-window context and known future plans are allowed; future observed care/payment outcomes are not invented.

The final **delivery/close grace** ends January 10, 2026 at 23:59:59 UTC. This permits December 2025 accounting close and actual exports on January 5, plus delayed delivery/corrections to already occurred events. It is not an extra clinical activity year. December as-of consumers cannot see those January-known actuals. An unsettled claim at the business cutoff is not settled merely to fill a January export.

## Manifest and replacement semantics

Each file has file_id, source contract, schema version, period, explicit scope, vintage, replacement_of, row count, control totals, SHA-256 and availability time. Publish separate canonical business, serialized source mirror and raw repeated-delivery counts.

Full snapshots replace a declared source snapshot scope, not sum into transactions. Immutable history is retained for as-of queries. Deltas add exact new versions/movements once. Replacement financial files supersede precisely the identified scope/vintage; they cannot wipe unrelated centers or double revenue. Source-record ID plus version/message identity is the idempotency key.

## Controlled fault dispositions

| Fault | Required outcome |
| --- | --- |
| Duplicate message/file delivery | No new economic/state effect; duplicate evidence retained in delivery metadata |
| Late/out-of-order event | Preserve original event and actual knowledge/delivery; reproject affected history, including beyond normal lateness |
| Missing file/partition | Mark incomplete and block certified reconciliation; do not silently insert zero |
| Incompatible schema | Quarantine under a versioned contract; no silent destructive coercion |
| Unmapped key | Quarantine affected rows with exact namespace/key; no fuzzy guess |
| Corrected/replacement export | Target exact scope/version, retain prior knowledge, reconcile corrected state |
| Corrupt row/control total | Reject or quarantine; the partition remains unaccepted until a corrected input reconciles |

Controlled source faults are not accepted canonical business corruption. Legitimate death, denial, stockout and overtime are valid adverse business events and remain in the canonical data.
