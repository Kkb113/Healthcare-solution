# Scope and architecture decisions for the data foundation

## D01 - Scale follows clinical detail and history

Use three fictional Illinois community hospitals with 72 inpatient beds. The former 300-bed proposal is superseded. The same bed-day arithmetic can be retained at smaller scale without dropping necessary histories to fund headline volume.

The 20-25-table and two-million-record constraints apply to published canonical business rows, including every version, opening context and correction. No hidden JSON/array facts or uncounted population are permitted. Raw export snapshots and mirrors have separate serialized row/byte counts; they are not falsely described as fitting within the canonical cap.

## D02 - Cohort and care boundaries

All patients are adults at service. Model medicine, limited general/orthopedic elective care, adult ED, hospital-based follow-up, and short ICU stabilization. Do not model pediatrics, maternity/newborns, tertiary transplants, long-term ICU, full-device telemetry, PACS images, secondary payer coordination or professional billing.

Every inpatient occupancy contributor is represented. The inpatient census is the complete census of the modeled facilities, not an undisclosed sample of larger hospitals. The clinical detail is the complete set of **modeled** drug administrations, orders and diagnostic/clinical variables; it is not every observation or every drug in a full EHR. A missing out-of-scope monitor reading does not mean that a hospital did not observe the patient or that the result was normal.

20,000 stable patients have realistic names, birth dates, contact fixtures, repeated visits, health history and primary coverage. Birth-cohort names use SSA aggregates; surnames use Census 2010 aggregates. Names may collide, change and contain natural punctuation. Surnames never determine demographics or disease. Public weights must be imported and hashed before Phase 2 generation, rather than replaced with one uniform short name list.

The calendar convention for Feb-29 births is Feb-28 in nonleap years, explicitly frozen for synthetic age validation. Clinical sex-related eligibility must use the relevant recorded clinical attribute if a future pathway needs it; none of the baseline pathways is a sex-specific maternity pathway. Administrative sex or a name is never substituted for clinical anatomy.

## D03 - Physical tables and purposeful consolidation

Exactly 25 physical business tables are defined. Consolidations preserve a meaningful grain:

- `location` is a hierarchy of departments, units, rooms and beds; physical bed availability comes from events, not an overwritten master flag.
- `worker_assignment` combines worker identity and one exclusive primary assignment as bitemporal versions. Multiple simultaneous jobs and multi-credential management are outside v1; worked-unit changes occur on shifts.
- `clinical_condition` contains typed diagnosis, longitudinal problem and drug-allergy assertions. An allergy points to an ALLERGEN row; a medication product references its allergen family.
- `clinical_event` is one typed scalar event or one document version. Each lab analyte, medication administration, procedure and observation value counts its own row. Family-specific mandatory fields are in `clinical-type-matrix.json`.
- `catalog_item` is a typed vocabulary/product/account catalog, not a generic entity-attribute store. Domain-specific required attributes are validated. It includes code versions, units, medication strength and account class.
- Bed intervals, a calendar date dimension and current census are deterministic **views/test projections**, not additional persisted business tables. They add no hidden occupancy facts.

Household/guardian entities are unnecessary for the adult baseline. Supplier identities may be descriptive source attributes on later receipt interfaces; a complete procurement/PO module is outside this release. These decisions bound the scope rather than pretending that omitted systems have been modeled.

## D04 - Stable identity versus immutable version

Mutable patient, coverage, workforce, condition and mapping facts carry business-valid and knowledge-valid intervals. Encounters, clinical events and shifts use immutable lifecycle/knowledge revisions. Movements and postings use immutable reversals/corrections.

FKs point to immutable row identities, never a nonunique stable patient/worker/encounter identifier. To obtain current or as-of status, resolve the stable identity from the referenced row, then select exactly one applicable revision. The version that recorded an order does not automatically become a later discharge snapshot.

Stable manager/worker references and typed crosswalk targets are explicit logical lookups with bitemporal uniqueness rules. They are not declared as unenforceable FKs to nonunique stable-ID columns. Financial source groups are exact aggregation predicates, not invented row FKs to batch strings.

## D05 - Historical and reporting boundaries

There are 56,000 distinct encounters intersecting the activity window: 12,000 IPD, 27,000 ED and 17,000 OPD. This includes 57 occupied inpatient carry-ins. Another 2,000 completed pre-window encounters exist solely to explain 2,000 opening claims/AR balances. They contribute no 2023 admissions, patient-days or newly recognized revenue.

All carry-in/context facts count in the row envelope. Their earlier birth/service dates are context, not an extra generated fourth year. Opening events at T0 establish census/stock/AR. Closing open cases remain open at T1. Future scheduled dates may be known plans, but observed future discharge/payment/outcome dates are not invented.

Store UTC instants. Report by America/Chicago local day; daylight-saving days may have 23/25 hours. Time-weighted occupancy uses actual seconds; financial/statistical day conventions are explicitly labeled. A midnight census count, occupied hours/24 and completed LOS are different measures.

## D06 - Resource constraints feed back into actual care

```mermaid
flowchart LR
    P[People and known baseline health] --> D[Demand and planned care]
    D --> Q[Capacity and queue decisions]
    R[Staff and eligible stock] --> Q
    Q --> C[Actual clinical and bed events]
    C --> R
    C --> F[Charges and resource costs]
    F --> G[Claims and balanced journals]
    G --> A[Monthly actuals and allocations]
    A --> E[Source export representations]
```

The later simulator must advance one coordinated clock. A shortage that changes service/discharge time regenerates affected clinical, bed, roster, stock, charge and accounting descendants. No downstream grand total is patched without its underlying business facts.

## D07 - Accounting and cost-pool grain

The GL stores daily source-group journal lines plus explicit monthly cost-pool-close journals. Each source group has a deterministic predicate over the underlying transactions. It is not a claim to retain a separate journal per administration or shift within 180,000 rows.

Monthly pool-close entries debit pool expense and credit the original expense account, leaving total expense unchanged. Only the designated pool debit/reversal lines are eligible for analytical patient-month/category allocations. This avoids both daily allocation-row explosion and double-counting original expense plus pool expense. Allocation rows create no GL expense themselves.

The scope has one primary institutional original claim per claimed encounter. Original claims, attempts, adjudications, denials, payments and cash are distinct identities/events. Opening AR is not re-recognized or re-submitted. Monthly Axiom actuals come from the represented ledger, not unrelated random targets.

## D08 - Source simulation is bounded and honest

Use deterministic synthetic source IDs and documented Workday/Axiom mappings. No live tenant credentials or assumed native connector are necessary for Phase 0. Readable human names coexist with technical surrogate keys.

The approximately 900 Axiom exports in the reference image are interpreted as 900 report definitions grouped into 12 representative layout families. All 12 families are exercised in later fixtures, with file counts reported. This baseline does not fabricate 900 nonempty monthly files or claim compatibility with an unseen tenant inventory. Real tenant onboarding is outside this synthetic data release.

## D09 - Review authority and phase boundary

Kkb113 explicitly delegated review/finalization to Codex. Codex performs the business-model, technical, clinical-assumption and simplified finance design reviews in `review-and-gate.md`. This is a user-designated baseline review, not an independent clinician endorsement. Later clinical-data sample reviews and real vendor compatibility tests cannot be marked complete by this baseline review.

Phase 0 produces metadata, offline SQL, design validators, tests and review evidence only. It does not implement a generator or deploy data tables. Phase 1 is the next permitted phase; the analytics solution remains `BLOCKED_FOR_SOLUTION` until Phase 9 acceptance.
