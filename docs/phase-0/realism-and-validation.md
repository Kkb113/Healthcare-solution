# Realism targets, independent checks and scenario acceptance

The baseline registers 12 sample-aware realism targets, 12 connected business scenarios, 55 future data-quality/reconciliation rules and contract-only design tests. Configuration targets are fictional design choices; none is represented as measured healthcare performance.

## Source registrations

| Input | Registered authoritative source | Use and pinning requirement |
| --- | --- | --- |
| Given names | [SSA cohort name files](https://www.ssa.gov/oact/babynames/limits.html) | Weight names by birth cohort; import/freeze file version and SHA-256 before identity generation; no real person records |
| Surnames | [Census 2010 surname aggregates](https://www.census.gov/data/developers/data-sets/surnames/2010.html) | Public frequency weights with broad diversity; never infer person ethnicity or disease from surname |
| Diagnosis/procedure codes | [CMS ICD-10 files](https://www.cms.gov/medicare/coding-billing/icd-10-codes) and [CDC release dates](https://www.cdc.gov/nchs/icd/icd-10-cm/files.html) | Pin FY2023-2026 and applicable midyear releases covering 2023-2025; service/discharge date policy matters |
| Patient/encounter semantics | [FHIR Patient](https://hl7.org/fhir/R4/patient.html), [Encounter](https://hl7.org/fhir/R4/encounter.html) | Identity, visit and lifecycle semantics; not a claim of full FHIR conformance |
| Results and medication workflow | [FHIR Observation](https://hl7.org/fhir/R4/observation.html), [MedicationAdministration](https://hl7.org/fhir/R4/medicationadministration.html) | Scalar result context, units, occurrence versus documentation, order/admin distinction |
| Claims | [FHIR ClaimResponse](https://hl7.org/fhir/R4/claimresponse.html) | Adjudication/settlement concepts; not certified 837/835 transaction support |
| Candidate lifecycle engine | [Synthea official repository](https://github.com/synthetichealth/synthea) | Phase 1 evaluate reuse, exact revision and adapters; no generator was selected/installed by Phase 0 |
| Workforce interfaces | [Workday Integration Cloud](https://www.workday.com/content/dam/web/se/documents/datasheets/datasheet-integration-cloud-se.pdf) | General integration semantics; synthetic layouts are explicitly project-defined |
| Financial planning | [Axiom budgeting/forecasting](https://www.stratadecision.com/budgeting-forecasting-software) | Financial scenario context; no tenant-specific layout claimed |
| Key enforcement | [Azure Databricks constraints](https://learn.microsoft.com/en-us/azure/databricks/tables/constraints) | Informational PK/FK metadata requires explicit integrity validation |

References are registered now. Importing/licensing-checking exact code/name artifacts and recording immutable hashes is a Phase 1/2 prerequisite before their use, not a claim that these files have already been downloaded or validated.

## Preregistered acceptance targets

Exact structured definitions, denominators and tolerances are in `realism-targets.json`. They include adult age mix, name weighting/collisions, payer mix, LOS and tail, repeat care, readmissions, initial denials, occupancy, RN coverage, seasonality and note diversity.

- Age shares are tested at first qualifying service for stable patients, not over demographic version rows. Minimum age at every service is a hard rule independent of the cohort mix.
- Completed LOS and in-window clipped occupied time use different denominators. Open/carry-in/AR-only context does not distort completed-stay evaluation.
- Denial denominators exclude unknown initial adjudication and do not count appeals/resubmissions as new claims. Full and partial denial definitions remain explicit.
- Readmission requires an eligible unplanned return within 30 days with complete follow-up. A transfer is not an independent readmission; censored December discharges are not labeled negative.
- Payer mix is not assigned from age alone. Medicare under-65 eligibility needs explicit synthetic disability context if included; otherwise those assignments are rejected. Payer/age compatibility is reviewed independently from target shares.
- Name validation allows legitimate duplicate names. Weights are cohort-conditioned, not one name per ID or a uniformly repeated list. Contacts remain fictional/non-deliverable.
- Missingness depends on care context and documentation availability. Unobserved, not applicable and not-yet-known values differ; no unconditional null-fill makes patients appear healthy.
- Cells with n<200 use a documented confidence interval/stratified review, not a brittle percent-difference test. Rare-case minimum counts are independently required.
- Multiple seeds vary people, timing and outcomes while preserving hard rules and predeclared population bands. Scenario identities and generation run IDs cannot become future model features.

## Required scenario coverage

All 12 scenarios in `scenarios.json` have a positive minimum representation, a required exact small fixture, linked tables and rule dependencies: chronic repeat care; elective reschedule; ED-to-IPD; respiratory surge; bed closure; absence/agency; stockout/expiry; denial/appeal; cross-month settlement; coverage/reorganization; late correction/replay; window boundaries.

Scenario counts can overlap. They are not additional rows outside the budget. A respiratory surge must change related diagnoses and demand before occupancy/resources/costs change; it cannot be an unrelated flag pasted onto independent tables. Normal periods retain stochastic variation, while each facility and year differs.

## Independent validation strategy

Phase 0 validates **the design contracts**, including keys, explicit types, dictionary completeness, source field mappings, clinical event profiles, table/rule/scenario references, budget subgrids and capacity/workforce arithmetic. Mutation tests prove that corrupt contracts are rejected. These are meaningful design checks, not a clinical data-validation harness.

Later phases independently validate actual generated data through:

1. Hand-calculated positive and negative fixtures, not the generator's own totals.
2. Event-state projection versus independently built bed intervals and occupied-time integration.
3. Quantity/currency stock roll-forwards and administration-to-stock conversion groups.
4. Worker/credential availability and time-cost equations using selected knowledge revisions.
5. Source facts to balanced journals to monthly actuals, plus patient allocations and explicit residuals.
6. Source parse/serialize round trips, controlled faulty input detection and replay convergence.
7. Fact-grain tests that expose duplicate sums after one-to-many joins.
8. Historical queries with the same event time and different knowledge cutoffs.
9. Stratified identity/clinical/financial traces, conditional distributions and long-tail review.

Required later review samples remain at least 100 patient identities, 50 worker identities, 100 longitudinal journeys and 50 complete financial traces, or the full available population if smaller. Phase 0 does not mark any future sample as reviewed.

## Severity, evidence and lock

P0 integrity/limit failures and P1 material business or realism failures block dependent gates. P2 limitations require bounded impact, owner and explicit disposition; they cannot waive an unexplained balance or missing required entity.

Every data rule is marked `SPECIFIED_NOT_DATA_EXECUTED`. Only contract validation is executed now. Validation evidence reports generated records as zero. The implementation plan's Phase 1-9 responsibilities remain unchanged, and `BLOCKED_FOR_SOLUTION` remains mandatory until final data acceptance.
