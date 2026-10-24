# Synthetic Data Generation Implementation Plan

**Status:** Phases 0-7 are complete for their defined scopes. Phase 7 passes all four [source-simulation exit criteria](evidence/source-delivery/acceptance-gate.json): **58 source tests** without failures/errors/skips, exact reconstruction of **1,924,164 canonical rows across all 25 tables**, zero unexplained differences, 3,444 idempotent source deliveries, a recorded 27-case native-source review and fifteen verified fault/delivery outcomes. The prior 280-test domain evidence and accepted canonical files remain unchanged; twelve legacy source tests are additionally rerun within the 58-test suite, so the counts overlap. The [financial budget amendment](docs/financial-history/record-budget-amendment.md) retains 1,995,215 planned canonical rows plus 4,785 reserve rows; the [source policy](contracts/source-delivery-policy.json) allocates 64 reserve slots to challenges, of which 22 are used. Current cap-counted release rows are **1,924,186**, with 4,721 reserve slots still unallocated. All earlier accepted snapshots and original frozen design artifacts remain immutable. **Phases 8-9 have not started.** No full healthcare dataset is accepted and no healthcare analytics solution or live source integration has been built.

**Prepared:** October 23, 2026  
**Setting:** Fictional US hospital group, USD, Workday workforce integration, and Axiom healthcare financial planning integration.  
**Implementation sequence:** Ten phases, numbered Phase 0 through Phase 9.  
**Current completed deliverables:** This plan, frozen baseline, runnable framework, master/reference packages, clinical histories, capacity-integrated operations, workforce/resource/stock generation, connected financial histories and source-shaped exports/delivery simulation, with recorded reviews, runbooks and passing evidence. The user authorized implementation, end-to-end testing, commit and push through Phase 7. The [source contracts](docs/source-delivery/source-contracts.md), [delivery/fault accounting](docs/source-delivery/delivery-and-faults.md), [runbook](docs/source-delivery/runbook.md), [native review](reviews/source-delivery-review.json) and [passing gate](evidence/source-delivery/acceptance-gate.json) document the latest completed scope. New artifacts use descriptive filenames with phase numbers inside their content. The full dataset and solution remain blocked until final Phase 9 acceptance.

## 1. Purpose and mandatory delivery boundary

Build a reproducible synthetic healthcare data platform that produces believable people, longitudinal patient histories, hospital operations, workforce activity, resource consumption, claims, and financial records. The records must form a consistent business system, with evidence that relationships, balances, event histories, and source exports reconcile.

Realistic names and ages are mandatory, but realism also requires coherent histories, clinically plausible care, variable demand, resource constraints, incomplete processes at the reporting cutoff, and realistic source-system behavior. Independently randomized tables, identical patient journeys, repeated placeholder text, and financial totals forced to balance through unexplained adjustments do not satisfy this plan.

**The healthcare analytics solution must not proceed until Phase 9 passes and the dataset is explicitly accepted.** This includes solution Medallion pipelines, operational command dashboards, forecasting models, deployed streaming intelligence, production AI agents, and other solution products. Microsoft Fabric is excluded throughout.

Data-generation tooling, isolated storage for candidate datasets, automated validation, source-format simulators, reconciliation queries, and disposable consumer test fixtures are within the data-foundation scope. They may use Azure Databricks where appropriate. Passing a consumer test does not authorize building or deploying the corresponding solution component.

This is a plan for realistic synthetic business data. Clinical plausibility and terminology checks support a trustworthy demonstration foundation; they do not establish clinical effectiveness or validate a treatment policy.

## 2. Requirements and planning assumptions

| Requirement | Implementation contract |
| --- | --- |
| Three years | Business activity covers January 1, 2023 through December 31, 2025, with all 36 months represented. These dates are the working baseline to freeze in Phase 0. |
| Record volume | Target one to two million records, with a hard ceiling of 2,000,000 published business records under the counting contract below. |
| Table count | Between 20 and 25 physical business tables. Phase 0 must demonstrate how every required entity and history is represented within that limit. |
| Healthcare setting | Fictional US hospital group, with its geography, services, patient cohort, and capacity explicitly defined. |
| Realistic identities | Patients and workers have believable names, birth dates, relevant demographic attributes, and consistent identities across sources. |
| History | Repeat encounters, disease progression, coverage changes, worker changes, and financial/source revisions occur where relevant. |
| Sources | Workday-style scheduled workforce, hierarchy, cost-center, and security extracts; Axiom-style monthly financial exports; clinical and operational source payloads. |
| Platform | Azure Databricks is the intended platform. Data-generation and validation code must remain reproducible and independently testable. |
| Quality | Automated structural, temporal, clinical, operational, financial, source-contract, and statistical validation is required. |
| Completion | No unresolved release-blocking defects, no unexplained reconciliation differences, and evidence-backed acceptance of the final release. |

### 2.1 Earlier estimates are not a frozen specification

The earlier 25-table proposal, 1,961,205-record estimate, three hospitals, 300 beds, 60,000 patients, and 120,000 encounters are provisional planning inputs. They must not force clinically sparse records or unrealistic operations.

Phase 0 must calculate the full detail required per patient journey, including diagnoses, observations, medications where in scope, clinical services, claim lines, bed movements, roster revisions, and financial events. If the earlier scale does not fit the record ceiling, reduce the modeled hospital scale or cohort and recompute its capacity and demand. Do not drop necessary clinical detail, truncate child records, or discard inconvenient encounters after generation to meet a row target.

The final scope may represent selected services or a smaller hospital network, but must represent those services coherently. A selected cohort must never be presented as the complete hospital census unless all occupancy-contributing patients are represented or an explicit, reconcilable background population is included in the budget.

### 2.2 Record and table counting contract

The published business-record count includes all rows in the agreed 20-25 business tables: master versions, opening balances, carry-in encounters, transaction lines, lifecycle events, corrections, reversals, forecast vintages, and any published challenge records. No history rows are excluded merely because they are inconvenient for the budget.

Source-format mirrors and repeated full-snapshot exports must be reported separately as physical serialized records and bytes. The canonical business-row ceiling does not imply that multiple representations of the same data occupy fewer than two million physical rows. Every release manifest must show both counts clearly.

Run manifests, schema definitions, test results, and reconciliation reports are control artifacts. If an artifact contains operational business facts rather than control metadata, classify and count it as business data. Do not evade the ceiling through hidden fact files, uncounted business tables, or large arrays of uncounted line items. Any nested clinical structure must have a documented grain, justified semantics, and explicit leaf-record accounting.

Plan a release below the ceiling, retaining a documented allowance for boundary records, corrections, histories, and fault fixtures. A budget overrun fails the release; it does not permit arbitrary sampling from connected data.

### 2.3 Time and reporting boundaries

- Store instants in UTC and retain the facility time zone for local reporting, daylight saving, and shifts.
- Use half-open intervals, `[start, end)`, with a defined rule for unknown ends.
- Separate business occurrence, source recording, ingestion, effective validity, and knowledge/availability time.
- Derive age at each encounter from birth date and the actual local encounter date, using calendar birthdays rather than an approximate days-per-year division.
- Earlier birth dates, employment dates, condition onset dates, code releases, and carry-in context are permitted. They provide the opening state of the three-year activity window.
- Do not fabricate future outcomes beyond December 31, 2025 to close open encounters, claims, or follow-up periods. Preserve censoring and distinguish it from missing or invalid data.

## 3. Generation and validation principles

### 3.1 Generate a connected operating system

Use shared state and a causal event model:

`Population and baseline health -> demand -> care pathway -> capacity/resource decisions -> actual clinical and operational events -> resource costs and billing -> claims and accounting -> source exports`.

Capacity, workforce, and stock can affect the timing of later care. The simulator therefore needs a common clock and controlled feedback, not a single pass that finalizes discharge before resource constraints are known. Later phases may require regenerating earlier candidate histories and repeating affected gates.

Canonical business facts must originate from the shared simulation. Source exports are representations of those facts, with independently controlled delivery delays, formats, corrections, and defects. Independent source generators must not invent conflicting realities unless a specific, documented reconciliation test requires that conflict.

### 3.2 Make realism measurable

Realism has six required dimensions:

| Dimension | Evidence required |
| --- | --- |
| Identity | Believable names, demographic diversity, non-placeholder contacts, legitimate name collisions, and cross-source identity continuity. |
| Longitudinal | Persistent health conditions, repeat visits, resolved and recurring episodes, changing coverage, and worker/organizational history. |
| Clinical | Diagnosis-service relationships, result units, observation trajectories, medications and allergies where in scope, and valid chronology. |
| Operational | Capacity-constrained placement, transfers, cleaning, shift coverage, resource use, and explicit unmet demand. |
| Financial | Charge and claim detail, adjudication, payments, adjustments, cost allocation, accounting periods, and monthly reconciliation. |
| Source behavior | Historical extracts, heterogeneous layouts, duplicate delivery, late events, schema changes, and recoverable corrections. |

Freeze target distributions, conditional relationships, and tolerances before evaluating a candidate. Record whether each target comes from a public aggregate source, a reviewed healthcare assumption, or a specific scenario requirement. A configured assumption must not be presented as a measured US healthcare benchmark.

### 3.3 Use deterministic controls and independent checks

- Version the generation code, dependencies, reference catalogs, configuration, seed, and schema.
- Use stable per-entity random streams so adding one patient does not reshuffle the entire population.
- Maintain a scenario catalog and expected-outcome fixtures outside business-facing feature columns.
- Separate generation logic from validation logic. A validator must not simply call the generator's calculation and compare it to itself.
- Use hand-calculated fixtures, property checks, metamorphic tests, independent event projections, and ledger roll-forwards.
- Produce checksums over stable, normalized, business-sorted representations. Volatile run timestamps belong in separate execution metadata and do not mask reproducibility failures.
- Treat malformed source data as a deliberate challenge input. The accepted canonical dataset must contain valid business facts; legitimate adverse clinical or financial outcomes remain valid facts.

### 3.4 Use realistic fictional identities

Names must be plausible human names, with realistic frequencies, middle names, suffixes, punctuation, spacing, and occasional changes. Do not require unique names or assume that a name determines ethnicity, sex, language, or disease.

Represent birth date and event-specific age, relevant demographic fields, contact preferences, geographic attributes, and identity status. Include household/guardian relationships when the selected cohort requires them. Distinguish clinical sex-related attributes, administrative sex, and gender identity where represented; do not substitute one for another in clinical rules.

Use synthetic street addresses and non-deliverable contact fixtures with plausible geography and formatting. Do not copy identifiable patient records, real contact details, or real clinician identities. Source identifiers must be clearly synthetic and consistent across files; real-world identifier formats are included only when the interface contract requires them and their test semantics are documented.

Clinical notes must be grounded in structured facts available at the note timestamp. Text variation must not create new diagnoses, medication doses, future outcomes, or fabricated source evidence. If a language model assists with wording, freeze and hash accepted outputs and validate their factual content; unconstrained text generation is not the clinical truth engine.

## 4. Phase sequence and gate policy

| Phase | Main objective | Required gate evidence |
| --- | --- | --- |
| 0 | Freeze scope, schema, realism targets, and record budget | Complete data contract and reviewed acceptance matrix |
| 1 | Implement reproducible generation controls and validation infrastructure | Passing deterministic and negative-control fixtures |
| 2 | Generate identities, organizations, reference data, and histories | Valid, varied, temporally consistent master data |
| 3 | Implement longitudinal clinical journeys | Clinically coherent, linked patient histories |
| 4 | Implement hospital demand, beds, and ADT events | Reconciled state histories and realistic capacity behavior |
| 5 | Integrate workforce, resource use, and inventory | Reconciled labor/resource activity and constrained feedback |
| 6 | Implement claims, costs, accounting, and monthly financial scenarios | Exact operational-to-financial reconciliation |
| 7 | Produce source exports, event delivery, and fault scenarios | Contract-valid files and predictable recovery behavior |
| 8 | Validate downstream consumption and full three-year candidates | Independent end-to-end evidence and corrected defects |
| 9 | Certify and publish the synthetic data release | Reproducible release with explicit data acceptance |

Each phase has one accountable owner and identified reviewers. One person may hold several roles, but cannot mark an independent review complete without performing and recording it. Clinical and finance judgments require a qualified reviewer or the business owner's explicitly designated domain reviewer; automated checks alone do not constitute those reviews.

Phase exit requires all its criteria and applicable earlier criteria to pass. A later change that alters prior evidence reopens affected gates. No gate passes because work is nearly complete, because the row count is correct, or because a preview looks convincing.

## Phase 0 - Scope, schema, realism baseline, and acceptance contract

### Objective

Create a complete, feasible specification for realistic three-year data before implementation or volume generation begins.

### Work

1. Define the hospital group, facilities, services, care settings, catchment, time zones, fiscal calendar, and patient cohort. Make pediatric, maternity/newborn, intensive-care, and other specialist inclusions explicit; do not generate pathways unsupported by the chosen scope.
2. Finalize 20-25 physical business tables and map every required logical entity to its storage location. Include the necessary history and relationships for patients, providers/workers, payer coverage, conditions, relevant allergies, clinical activities/results, encounters, appointments, beds, workforce, items, claims, costs, financial scenarios, source keys, and access scopes.
3. Produce a field-level dictionary: grain, keys, type, precision, nullability, units, permitted values, source authority, effective dates, recorded/available time, correction behavior, and lineage. Document any justified entity consolidation and its type-specific validation.
4. Define patient, episode, encounter, transfer, bed assignment, appointment, original claim, claim attempt, payment, cost pool, financial version, and publication identities. Separate transactions from snapshots and movements from balances.
5. Calculate the record budget from coherent event frequencies and required clinical/financial detail. Reconcile inpatient demand, length of stay, staffed capacity, bed-hours, staffing workload, and expected resource events. Define the policy for background occupancy if modeling a cohort.
6. Define initial conditions, opening inventory, open claims, carry-in patients, cutoff censoring, and how these records consume the budget.
7. Register realistic name/demographic sources, clinical pathway assumptions, code catalogs, cost/reimbursement assumptions, and statistical target bands. Use the terminology version valid for the service/discharge date, including fiscal-year and applicable midyear updates [R2].
8. Define source contracts for clinical/operational payloads, Workday-style scheduled extracts, and Axiom-style monthly exports. Treat the image's approximately 900 Axiom exports as a source-inventory question, not 900 tables or a confirmed file count per cycle. Choose and document a bounded simulation interpretation if actual layouts are unavailable.
9. Freeze reconciliation equations, rule severities, sample-review requirements, fault types, expected rejection behavior, and the final release checklist. Map each future use case to required facts and independent validation queries without building that use case.

### Expected outcomes

- Versioned scope, entity-relationship model, complete dictionary, source contracts, causal/dependency graph, and table/record budget.
- A realism specification with target values or bands, provenance, sample-size rules, and identified reviewers.
- A numbered validation catalog and scenario inventory with expected outcomes.

### Validation criteria

- Every required entity, historical version, financial movement, and source relationship has a defined grain and representation.
- Capacity, utilization, staffing, and event-count calculations fit within the release budget with contingency.
- No essential details depend on unspecified extra tables or uncounted nested facts.
- Every acceptance measure has a formula, population, tolerance, severity, and reviewer.
- All open decisions either have a documented working assumption or block the relevant implementation work.

### Exit criteria

- The schema, source contracts, scope, budget, realism targets, and acceptance matrix are recorded as baseline version 1.
- There are no unresolved blocking questions about clinical scope, identity, grain, history, financial semantics, or the record cap.
- Business, clinical, data, and finance review responsibilities are assigned and the required baseline reviews are recorded.
- Phase 1 may begin; volume generation and solution development remain blocked.

## Phase 1 - Reproducible generator framework and validation harness

**Implementation:** Complete for the framework/development-fixture scope; [artifacts and runbook](docs/phase-1/README.md), [exit evidence](evidence/phase-1/gate.json). Only 30 scalar development rows and 3 separately counted source-mirror rows are generated. Rule-family microfixtures do not certify full Phase 0 data rules on a future healthcare release.

### Objective

Implement the controls that make all later generation repeatable, observable, restartable, and testable.

### Work

1. Build configuration-driven modules for identities/reference data, clinical pathways, demand, resource constraints, billing/accounting, source serialization, and fault injection. Keep domain assumptions outside hard-coded scripts.
2. Implement stable identifiers, per-entity seeded random streams, an event scheduler/common clock, code-version lookup, temporal utilities, and deterministic rounding rules.
3. Implement run manifests, stage checkpoints, dependency tracking, output checksums, budgets, and failure/restart behavior. Changes to an upstream configuration must invalidate affected downstream candidate outputs.
4. Implement independent rule execution, result capture, reconciliation output, profiling, defect tracking, and gate evaluation. Rules must identify affected records and failure reasons.
5. Create small hand-calculated fixtures before any large run: identity collisions, leap-day birthdays, daylight-saving shifts, linked ED/inpatient encounters, bed transfers, partial payments, refunds, code-version changes, and retroactive worker corrections.
6. Add deliberate faulty fixtures for every hard invariant and source-recovery behavior. Establish separate valid-business, adverse-outcome, and malformed-source classifications.
7. Evaluate Synthea or similar lifecycle tooling as an optional clinical component. Record a build/reuse decision and adapter gaps; it is not a replacement for hospital operations, Workday, Axiom, or independent validation [R1].

### Expected outcomes

- A runnable generation framework and independent validation runner.
- Versioned configuration, manifests, small reference fixtures, and a deterministic replay mechanism.
- Evidence of how budgets, failures, changes, and reruns are controlled.

### Validation criteria

- Identical code, configuration, references, and seed reproduce identical normalized business outputs.
- A changed seed varies individual records while respecting the same configured rules.
- Restarting a failed stage produces no duplicate identities, movements, or balances.
- Every seeded hard-rule fault is detected by the intended check; valid counterexamples pass.
- Validators detect a deliberately introduced arithmetic or chronology error without relying on the generator's own implementation of that calculation.

### Exit criteria

- All positive, negative-control, determinism, restart, and budget fixtures pass.
- A failed critical rule prevents candidate acceptance automatically.
- The generator/validator separation and checkpoint/invalidation behavior are demonstrated.
- Only development fixtures exist; a full business dataset has not yet been accepted.

## Phase 2 - Realistic identities, organizations, reference data, and histories

**Implementation:** Complete for master data and opening problem/allergy context; [design and runbook](docs/master-data/README.md), [exit evidence](evidence/master-data/acceptance-gate.json). Generates 20,000 stable patients and 300 stable workers within 78,922 counted full-schema rows, preserving the 25-table / 1,958,210-row complete-release plan. The 13,000 opening condition rows are part of the existing condition budget. The final healthcare dataset remains unaccepted.

### Objective

Create believable people and the stable, time-aware master data that connects every later event.

### Work

1. Generate named patients with birth dates, demographics, geography, contact attributes, preferred language, and required household/guardian links. Include legitimate shared names, shared addresses, middle-name variation, and known/unknown attribute states.
2. Generate named physicians, nurses, allied-health staff, administrative staff, agency workers, managers, and required provider-role relationships. Include specialties, qualifications, effective credential periods, employment types, FTE, pay basis, and historical assignments where required by scope.
3. Generate facilities, departments, wards, rooms/beds, clinical capabilities, cost centers, reporting hierarchies, and active periods. Separate clinical hierarchy, management hierarchy, and financial responsibility.
4. Generate payer products and effective-dated patient coverage. Represent coverage changes across three years and define primary/secondary coverage behavior if included; do not infer coverage merely from a static patient payer column.
5. Establish versioned clinical, medication, supply, role, account, denial, and other reference catalogs. Define item units, pack conversions, drug formulation/strength where needed, and account/measure semantics.
6. Generate source identifiers and effective-dated crosswalks for clinical, workforce, finance, and security domains. Simulate selected source-specific name formatting and identity changes without changing the canonical person.
7. Establish opening health and demographic context required by the selected clinical pathways. Define unknown emergency identities and later identity resolution if that scenario is included.

### Expected outcomes

- Realistic, connected master data with human-readable identities and valid source identifiers.
- Historical workforce, coverage, organizational, and mapping records.
- A reference-data package and identity/history validation report.

### Validation criteria

- No unexplained placeholders such as numbered patient names or universal default addresses in the accepted master data.
- Birth dates, age eligibility, employment periods, credentials, coverage, and deceased status satisfy the configured rules.
- Legitimate name collisions do not merge different people or cause false duplicate-key failures.
- No unexplained overlapping exclusive assignments or coverage priorities; historical queries resolve the intended version.
- Hierarchies are acyclic; source mappings are unambiguous within their entity, key, validity, and knowledge intervals.
- Identity and demographic distributions meet the predeclared bands without deterministic name-to-demographic or demographic-to-disease assignments.

### Exit criteria

- All structural and temporal master-data checks pass.
- A stratified sample of at least 100 patient identities and 50 worker identities, or all records if fewer exist, is reviewed for realism.
- Each required master domain is represented and linked to its source authority.
- No critical realism or identity defects remain unresolved.

## Phase 3 - Longitudinal clinical histories and care pathways

**Implementation status:** Completed for the defined scope on October 23, 2026. See the [generation design](docs/clinical-histories/generation-design.md), [actual counts and review](docs/clinical-histories/validation-and-review.md), [recorded review decision](reviews/clinical-journey-review.json), and [passing acceptance evidence](evidence/clinical-histories/acceptance-gate.json). All 159 repository tests, 15 full-candidate clinical groups, independent file inspection and frozen-design regression pass. Clinical trajectories remain provisional for later resource integration; final data/solution acceptance stays blocked.

### Objective

Implement patient histories that evolve over time and contain the clinical detail needed to explain operational and financial activity.

### Work

1. Implement a reviewed set of clinical pathways for the selected services, including common conditions, chronic-condition follow-up, elective care, acute deterioration, uncomplicated recovery, and a controlled number of complex cases.
2. Maintain baseline conditions, new diagnoses, onset/resolution, clinically relevant allergies, and follow-up needs. Ensure later encounters can use previously known history without using future diagnoses.
3. Generate linked appointments, ED visits, outpatient encounters, and inpatient episodes with clinically meaningful transitions. Include repeat visits, no-shows, cancellations, referrals, readmissions, and death where supported by scope.
4. Generate required orders, procedures, observations/laboratory results, medication orders/dispenses/administrations, and care documentation at the agreed granularity. Every included pathway must have its necessary evidence rather than arbitrary one-row-per-encounter detail.
5. Generate observation trajectories conditional on clinical state, measurement units, timing, and treatment where modeled. Preserve meaningful correlations and variation; do not sample each result independently from one generic range.
6. Validate medications against age, formulation, dose unit, route, timing, relevant allergies, and the configured clinical constraints. Specific dosing assumptions require reviewed reference rules rather than invented universal limits.
7. Produce varied clinical text from facts available at authoring/signing time. Distinguish observations made, orders placed, services completed, and diagnoses coded later. FHIR Patient, Encounter, and Observation provide useful semantic references, without implying full FHIR conformance [R3-R5].
8. Emit planned clinical demand and provisional trajectories for the operational simulator. Actual service timing and discharge remain subject to the capacity/resource integration in Phases 4-5.

### Expected outcomes

- A functioning longitudinal clinical generator and linked patient journeys.
- Structured clinical facts and fact-grounded notes with availability timestamps.
- Cohort, chronology, terminology, and pathway-validation evidence.

### Validation criteria

- No encounter before birth or new clinical activity after recorded death; later administrative activity remains possible under its own rules.
- Services and results belong to valid patients/encounters and follow their applicable order, collection, performance, and documentation sequence.
- Diagnosis, medication, procedure, and observation terminology and units are valid for their dates and context.
- Notes do not contradict structured facts or mention future outcomes as already known.
- Repeated patients exhibit coherent history and variation; disease, service, LOS, and result relationships meet predeclared conditional targets.
- Unobserved follow-up outcomes at the cutoff are censored, not labelled negative or completed.

### Exit criteria

- [x] All hard clinical, identity, chronology, and terminology rules pass.
- [x] Every required pathway and relevant boundary case is represented in fixtures and sampled histories.
- [x] At least 100 stratified longitudinal journeys, or all if fewer exist, are reviewed across acuity, service, age, repeat visits, and adverse outcomes.
- [x] The designated clinical/domain reviewer records the scope and result of plausibility review; no unsupported clinical assumptions are marked validated.

## Phase 4 - Demand, patient flow, beds, and operational event history

**Implementation status:** Completed for the defined scope on October 23, 2026. The [generation design](docs/operational-flow/generation-design.md), [runbook](docs/operational-flow/runbook.md), [reconciled controls and test scope](docs/operational-flow/validation-and-review.md), [recorded hundred-case review](reviews/operational-flow-review.json), and [passing acceptance evidence](evidence/operational-flow/acceptance-gate.json) document the implementation. All four exit criteria pass: 197 regression tests, fifteen integrated clinical groups, seven operational groups, independent persisted-file/checkpoint inspection and frozen-design regression. The candidate contains 938,452 canonical rows in 16 populated business tables, including 71,018 immutable bed events and 3,288 facility/day drivers. All 25,245 census boundaries and 5,085,526,680 occupied seconds reconcile with zero unexplained differences. The frozen final 25-table/1,958,210-record plan remains unchanged, with 1,019,758 planned records remaining and the 41,790-record reserve untouched. Earlier accepted master and clinical snapshots remain immutable. Actual workforce/inventory integration, later financial and source-system phases, and final dataset acceptance remain outstanding; solution development stays blocked.

### Objective

Make hospital activity dynamically consistent with capacity, patient placement, transfers, and real operational timing.

### Work

1. Generate calendar-driven and stochastic demand: intraday and weekday patterns, elective schedules, seasonality, growth, and finite-duration disruptions. Avoid identical weekly patterns or the same seasonal curve in every facility.
2. Integrate clinical demand with actual arrival, triage, admission decision, boarding, placement, transfer, discharge, cleaning, and bed-ready events.
3. Maintain separate dimensions for occupancy, commissioning/service state, staffing enablement, reservation, and placement suitability. Distinguish licensed, staffed, immediately available, and patient-compatible beds.
4. Enforce unit capability and bed/room constraints. Represent unmet demand as waiting, deferred care, diversion, or transfer rather than silently dropping patients or placing multiple patients in a single bed.
5. Create atomic transfer correlation, opening census, closed/blocked capacity, and late/corrected event scenarios. Record the cause of delays separately from the resulting timestamps.
6. Derive bed intervals and current-state projections from the event history. Validate them against an independently constructed interval/state oracle. Derived representations must follow the agreed table/row counting contract.
7. Integrate demand shocks with clinical cohorts so a respiratory surge changes relevant clinical, bed, and later resource activity together.

### Expected outcomes

- Chronologically valid patient flow and a replayable ADT/bed event history.
- Time-weighted capacity, occupancy, queue, transfer, and turnaround control totals.
- Evidence that every occupancy-contributing patient is represented under the scope contract.

### Validation criteria

- No overlapping occupancy of one bed or simultaneous inpatient bed placement for one patient, except explicitly modeled nonoccupancy reservation semantics.
- Capacity changes, cleaning, reservations, and compatibility rules produce the intended availability state.
- Opening census plus admissions/transfers in minus discharges/transfers out equals closing census at every agreed reconciliation boundary.
- Event-integrated occupied seconds equal the sum of independently reconstructed bed-interval seconds at the same scope and cutoff.
- Bed intervals are contained in the relevant care period; transport, boarding, leave, and other gaps have explicit semantics rather than being forced to equal encounter LOS.
- Facility transfers reconcile across sites; internal bed transfers do not become additional network admissions.
- Late events, cancellations, and corrections converge to the correct historical state without silent loss.

### Exit criteria

- All patient-flow and bed-state invariants pass for normal and stress scenarios.
- No unexplained census, capacity, transfer, or occupied-time differences remain.
- Queues and utilization meet the configured targets and scenario expectations.
- Operational review confirms that time sequences and placement behavior are believable.

## Phase 5 - Workforce, resource consumption, and inventory

**Implementation status:** Completed for the defined scope on October 23, 2026. All four exit criteria pass with 238 regression tests, fifteen revalidated clinical groups, seven revalidated operational groups, six workforce groups, three stock groups, independent persisted-file/checkpoint inspection and unchanged frozen-design checks. The [accepted candidate](evidence/resource-foundation/acceptance-gate.json) contains 1,053,661 canonical rows in 18 populated business tables, including 66,582 shift versions and 47,839 inventory movements. Source labor hours and USD 47,658,801.10 captured labor cost reconcile; stock quantities, USD 118,574.25 patient consumption, USD 11.41 nonpatient consumption and USD 6,210.92 closing stock value recompute from rates/quantities/lot prices. There are no unexplained negative stocks or untraceable resource costs. Thirty stockout and thirty circulating-RN absence windows, 198 agency replacements and 788 coordinated operative services have connected effects. The [review](reviews/resource-foundation-review.json) binds 100 named cases and selected labor/stock correction facts; it is user-designated synthetic review, not licensed clinical endorsement. All fifteen unchanged parent tables, including encounter/attending and bed histories, are byte-identical; all changed clinical histories pass their prior-domain gates again. Complete clean rebuild, cached resume, actual process-crash rollback/recovery, source-knowledge, intentional-fault and row-order tests pass. An exact-revision [operational restoration check](evidence/resource-foundation/restoration-check.json) also matches all sixteen parent file checksums. Selected workforce/material capture and simplified costing assumptions are explicit in the [policy](contracts/resource-foundation-policy.json). The frozen 25-table/1,958,210-row plan and 41,790-row reserve remain unchanged. At this phase's acceptance, financial postings and subsequent data-release phases were still outstanding; their later status is recorded separately below.

### Objective

Make staffing and supplies respond to actual care activity and constrain it where the scenario requires.

### Work

1. Generate published rosters, revisions, actual attendance, breaks, productive time, overtime, agency usage, leave, and absences. Preserve what was planned and known at each historical timestamp.
2. Link staffing requirements to unit census, acuity, service activity, and reviewed workload assumptions. Include skill mix, credential validity, worker availability, and configured shift/rest rules.
3. Link clinical services to the appropriate resource quantities and consumption times. Separate ordered, administered/consumed, returned, wasted, and cancelled quantities.
4. Generate opening stock, receipts, lot/expiry history, issues, returns, transfers, substitutions, and adjustments with explicit unit conversion.
5. Model stockouts and workforce gaps through explicit unmet work, substitutions, delays, or agency response. Re-run the integrated simulation if they alter care timing, discharge, occupancy, or claimable services.
6. Calculate source resource costs from quantities, rates, contract types, and time-effective prices. Distinguish clinical consumption cost, inventory expense, and purchases that remain in stock.
7. Record nonpatient activity and unallocated resource time where needed to reconcile costs and productive capacity.

### Expected outcomes

- Historical rosters and attendance linked to workforce and clinical activity.
- Balanced inventory ledgers and clinically plausible resource consumption.
- Reconciled resource cost inputs and integrated shortage/delay scenarios.

### Validation criteria

- No unexplained overlapping worked shifts or clinical activity outside credential/employment validity.
- Scheduled, actual, break, overtime, and productive hours reconcile under the configured definitions; overtime is not added twice to worked hours.
- Staffing demand responds to census and acuity without pretending that staffing shortage automatically removes an occupied patient.
- Stock roll-forwards balance by location, item, lot, and base unit; transfer quantities balance across locations.
- Stock cannot be issued before receipt or after expiry without an explicitly classified fault or approved exception.
- Medication/supply resource links reconcile to administration or service activity under the chosen policy, with legitimate nonpatient waste and returns kept separate.
- Resource constraints feed back into actual clinical and bed timelines without leaving stale downstream facts.

### Exit criteria

- All labor-hour, cost-input, stock-balance, and resource-link controls pass.
- There are no unexplained negative stock balances or untraceable resource costs.
- Normal operations, shortage, absence, agency, and stockout scenarios produce the expected connected effects.
- Any changed Phase 3-4 histories pass their gates again.

## Phase 6 - Revenue cycle, cost accounting, and Axiom financial scenarios

**Implementation status:** Completed for the defined scope on October 24, 2026. All four exit criteria pass: 280 tests without failures/errors/skips, nine financial control groups without critical defects, independent persisted-file/checkpoint inspection, a content-bound 60-case user-designated finance review, clean rebuild/hash equality, cached reuse and actual process-crash recovery. The candidate contains 1,924,164 canonical rows in all 25 tables. Seventeen parent tables remain byte-identical, all 3,000 accepted catalog rows are preserved, and five local billing codes are appended. Original insured claims and self-pay statements, charge/line/event histories, balanced source-derived journals, patient/nonpatient allocations and Axiom actual/budget/forecast vintages reconcile under the declared policy. Closing billed AR of USD 14,769,836.80 plus USD 512,295.12 unbilled service AR equals USD 15,282,131.92 enterprise AR; selected patient/nonpatient allocations exhaust USD 65,841,153.17 eligible expense. All eighteen immutable resource-parent files reproduce from their exact accepted Git revision. The [financial design](docs/financial-history/generation-design.md), [budget amendment](docs/financial-history/record-budget-amendment.md), [variance lineage](docs/financial-history/variance-lineage.md), [runbook](docs/financial-history/runbook.md), [60-case review](reviews/financial-history-review.json), [restoration proof](evidence/financial-history/restoration-check.json) and [passing acceptance evidence](evidence/financial-history/acceptance-gate.json) record the implementation. The financial envelope is 1,995,215 planned rows plus 4,785 reserve rows, with no truncation of accepted facts or histories. Source exports/replay, final integrated acceptance and solution development remain outstanding.

### Objective

Create an auditable financial history derived from business activity, with realistic timing and exact reconciliation at the selected accounting grain.

### Work

1. Generate chargeable service lines, prices, contractual reimbursement assumptions, coverage/authorization references, and original claim identities. Keep claim attempts separate from original claims.
2. Generate adjudications, line-level denials, partial approvals/payments, appeals, resubmissions, patient responsibility, write-offs, refunds, reversals, and open receivables. Preserve event and recording times [R6].
3. Derive recognized revenue and financial postings according to a documented simplified accounting policy. Keep billed charges, allowed amounts, recognized revenue, patient liability, and collected cash distinct.
4. Generate labor, medication, supply, and explicitly modeled nonpatient/shared expenses from their resource facts and accounting policy. Define accruals, purchase-versus-consumption treatment, service month, and posting month.
5. Implement cost pools, direct attribution, allocation drivers, nonpatient amounts, residuals, and allocation versions. Avoid assigning the same expense through both direct cost and pooled allocation.
6. Produce monthly actuals from reconciled subledger/posting facts. Generate budgets and rolling forecasts from information available at each planning vintage, plus genuine uncertainty; do not copy final actuals into earlier forecasts.
7. Map the canonical accounting results to Axiom accounts, cost centers, scenarios, units, and export versions. Axiom is the source representation/control for later consumers; its synthetic actuals must reconcile to the underlying generated business facts rather than an unrelated random monthly total [R8].
8. Create explainable budget/actual differences from demand, mix, prices, agency usage, denial recovery, and operational disruptions.

### Expected outcomes

- Traceable service-to-charge-to-claim-to-payment histories.
- Balanced subledgers/postings, cost allocations, receivables, and monthly actuals.
- Original/revised budgets and historically valid Axiom forecast vintages.

### Validation criteria

- Claim headers equal eligible line totals; adjudication categories and liability reconcile under the registered payer/accounting rules.
- Payment reversals/refunds have signed, linked effects; repeated delivery does not generate duplicate cash or recovery.
- Opening receivables plus recognized receivable movements minus settlements/adjustments equals closing receivables under the defined policy.
- A pending denial is not automatically a final write-off; a resubmission is not a new original claim denominator.
- Direct allocations plus pooled allocations plus nonpatient/unallocated residuals reconcile to the corresponding eligible expense postings, with each amount counted once.
- Expense and revenue actuals reconcile by period, facility, cost center, account, currency, and selected version, including documented service-to-posting bridges.
- Statistical financial measures retain units; FTE, patient-days, currency, and quantities are never added together.
- Each forecast vintage uses only facts available at publication and is retained independently of later revisions.

### Exit criteria

- All monetary reconciliation controls pass to the stored currency precision with no unexplained balancing entries.
- At least 50 complete financial traces, or all if fewer exist, are reviewed across payer, service, denial, appeal, refund, open claim, and cross-month cases.
- The designated finance reviewer records acceptance of the accounting, allocation, and reconciliation semantics.
- No unresolved critical financial or historical-availability defects remain.

## Phase 7 - Source-system exports, delivery simulation, and controlled faults

**Implementation status:** Completed for the defined scope on October 24, 2026. All four exit criteria pass. The 58-test suite includes 46 new source tests and twelve rerun legacy source tests, with zero failures/errors/skips. All 25 canonical table SHA/counts reconstruct exactly from persisted native files; all 3,444 source deliveries reload without adding facts. Four actual-close scopes replace the intended prior vintage, including unchanged final confirmations. Independent checks verify all 318 weekly snapshots, 1,106 daily dates per worker/security feed, 36 actual-close months per template/family and all 304 Axiom file headers. Six report mirrors reconcile wide cells, adjustments, forecast rates, variance states and account/center mappings. Fifteen published fault/delivery outcomes demonstrate quarantine, rejection, explicit repair, historical knowledge, revocation and idempotency. Complete clean rebuild, cache reuse, actual export crash/full resume, indexed full-history replay, SQLite WAL process-death rollback and corrupted-cache rejection pass. The [27-case review](reviews/source-delivery-review.json) binds 27 native rows / 53 scalar fact mirrors and the exact source package. The valid package retains 1,924,164 business rows / 25 tables; 22 separately labeled challenge/control records fit the 64-slot allocation, giving 1,924,186 cap-counted rows. Snapshot, dictionary and report copies are separately reported physical mirrors. Twelve illustrative Axiom archetypes are modeled, with no vendor-certified compatibility claim or invented coverage of the approximately 888 unmodeled inventory slots. The [source foundation](docs/source-delivery/README.md) and [passing evidence](evidence/source-delivery/validation-report.json) document the implementation. Earlier accepted data/evidence remain unchanged; full-data acceptance, Phases 8-9 and solution development remain outstanding.

### Objective

Produce believable source inputs and prove their delivery/correction behavior without building the analytics solution.

### Work

1. Serialize the accepted canonical facts into clinical/operational source layouts and event envelopes, Workday-style scheduled files, and Axiom-style monthly exports. Use source-specific identifiers, date formats, code representations, naming patterns, and schemas.
2. Workday contracts cover workers, managers, assignments, cost centers, and security mappings, including hires, transfers, terminations, retroactive corrections, and revocations. Scheduling/payroll content is included only if explicitly contracted; it is not assumed to arrive in a generic employee extract [R7].
3. Axiom contracts cover accounts/measures, cost centers, accounting periods, actuals, budgets, forecast vintages, and units. Preserve report/template and file identities. Record the chosen simulation coverage for the approximately 900-export inventory and any layouts not actually modeled.
4. Generate manifests with file checksums, schema versions, periods, row counts, control totals, arrival times, and replacement relationships. Distinguish full snapshots, deltas, replacement files, and additive transactions.
5. Simulate event-time versus delivery-time differences, per-source sequencing, delayed batches, duplicates, missing files, corrupt rows, schema changes, and correction/replay behavior.
6. Publish controlled fault fixtures with a fault manifest specifying affected records, injection stage, expected detector, expected quarantine/rejection/recovery action, and expected final canonical state.
7. Use isolated readers/replayers to prove source round trips. Defects alter the observed delivery layer; they do not silently corrupt the canonical truth or unrelated scenarios.

### Expected outcomes

- Source-shaped files, event payloads, source dictionaries, and delivery manifests.
- A documented separation between valid source data and challenge inputs.
- Evidence that known faults are detected and corrected predictably.

### Validation criteria

- Contract-valid exports parse and reconstruct the intended business facts and control totals.
- Full-snapshot reloads and duplicate delivery are idempotent; replacement exports replace the intended version rather than adding it to actuals.
- Late corrections preserve historical validity and availability; revoked workforce access resolves to the intended scope in test fixtures.
- Missing or invalid critical source keys are quarantined or rejected according to policy, never guessed or silently dropped.
- Every seeded release-blocking fault is detected and has a demonstrated disposition.
- Simulated layouts are clearly identified; no claim of vendor-certified Workday or Axiom compatibility is made without actual tenant/layout testing.

### Exit criteria

- All source contracts, round-trip controls, delivery scenarios, and critical fault fixtures pass.
- Canonical-versus-export differences are zero or an explicitly modeled, recoverable source defect with the expected result.
- Published challenge records and histories remain within their allocated record allowance.
- Source simulation is complete; production source integrations and solution ingestion remain unbuilt.

## Phase 8 - Full-history generation, reconciliation, and downstream contract validation

### Objective

Produce the complete three-year candidate and prove that independent consumers can reconstruct correct business results from it.

### Work

1. Run staged integrated candidates: small connected development fixtures, representative stratified pilot, and the full three-year release scale. Scale causal demand and resource detail together; do not tile one month or duplicate patient histories.
2. Execute the complete quality and reconciliation catalog on the full candidate, all source exports, opening states, and cutoffs.
3. Implement disposable validation consumers for census/bed availability, staffing hours, inventory, original-claim denial/cash history, patient cost, and monthly actual/budget/forecast variance. These are test queries and fixtures, not dashboards, models, agents, or production Medallion pipelines.
4. Verify point-in-time feature inputs and label availability for future consumers without training forecasting or clinical models. Include scheduled-versus-actual care, late diagnoses, discharge records, roster revisions, and forecast vintages.
5. Test fan-out protection at each analytical grain. Joining diagnoses, services, claim lines, and bed intervals must not multiply charges, census, or costs.
6. Run independent statistical profiles by month, facility, service, payer, age/cohort, acuity, and scenario. Check marginal and joint distributions, tails, transitions, missingness, text repetition, and rare-case presence.
7. Reconcile event projections against interval oracles, subledgers against accounting totals, source files against canonical facts, and historical snapshots against as-of expectations.
8. Exercise restart, failed export recovery, subset rebuild, schema evolution, and a changed upstream assumption. Ensure dependency invalidation triggers the necessary regeneration and reviews.
9. Compare a primary seed with at least two additional seeds at representative scale to detect hard-coded patterns and fragile calibration. Only the accepted release seed is published as the final dataset.

### Expected outcomes

- A full-scale candidate, independent validation queries, complete reconciliation reports, and a realism scorecard.
- An issue register with root causes, corrections, regenerated dependencies, and regression results.
- Evidence that the data supports the intended downstream questions without implementing the solution.

### Validation criteria

- All 36 months and expected facility/service partitions are present; blank periods require an explicit lifecycle reason.
- The business-table and record counts satisfy the frozen contract, including boundary/history/challenge allowances.
- All hard invariants and reconciliation equations pass at their declared grain, not merely at network grand total.
- Source reprocessing, duplicate delivery, and corrected events converge to the independently expected state.
- Future facts do not appear in historical feature views; unknown outcomes are distinguishable from negative outcomes.
- Statistical and conditional realism tests meet the predeclared sample-aware tolerances. Low-count groups use an approved interval or qualitative review rather than an arbitrary percentage test.
- Scenario behavior is causal and visible across the affected domains; normal periods are not uniformly noisy or uniformly clean.
- Identity, clinical, workforce, and financial review samples are drawn by recorded stratification rules rather than selected for appearance.

### Exit criteria

- No unresolved P0 or P1 defect remains, and no unexplained reconciliation difference remains.
- All required consumer contracts, fault scenarios, and point-in-time checks pass.
- Domain reviewers accept the scope-specific realism evidence and record remaining nonblocking limitations.
- The candidate is eligible for release certification; solution development is still blocked.

## Phase 9 - Reproducible release, certification, and data acceptance

### Objective

Publish a versioned synthetic dataset only after its completeness, realism, reconciliation, and reproducibility have been demonstrated.

### Work

1. Rebuild the final candidate from a clean environment using the pinned code, dependency set, reference catalogs, configuration, and seed. Compare normalized business checksums to the candidate accepted in Phase 8.
2. Execute all automated checks against the rebuilt files and event payloads that will actually be published. Do not rely only on validation of an earlier in-memory dataset.
3. Review the final evidence package: schema/dictionary, business rules, source mappings, scenario catalog, quality results, reconciliation controls, realism profiles, sample traces, fault outcomes, and limitations.
4. Confirm that legitimate open stays, open claims, missing-not-yet-known values, and censored outcomes remain represented rather than cleaned away.
5. Publish an immutable, versioned data package with checksums and manifests. Define rebuild, change-control, correction, and release-retirement procedures.
6. Record explicit acceptance by the business owner, with the required clinical, operational/workforce, finance, and data-engineering reviews attached. Acceptance acknowledges the documented modeled scope and limitations.

### Expected outcomes

- A complete synthetic dataset release and reproducible generation/validation package.
- A signed or explicitly recorded acceptance record with links to evidence and known limitations.
- A frozen foundation for later solution planning.

### Validation criteria

- A clean rebuild reproduces the accepted normalized business content.
- Published checksums, schemas, row counts, source totals, and evidence references match the actual release.
- All mandatory final acceptance checks in Section 9 pass.
- Reviewers have not waived structural integrity, unexplained financial differences, the record cap, or missing essential business entities to obtain release status.

### Exit criteria

- Phase 9 is marked `PASSED` with its evidence and explicit business acceptance.
- The synthetic data platform is marked `DATA_ACCEPTED`; otherwise it remains `BLOCKED_FOR_SOLUTION`.
- No solution product is built automatically as part of certification. Any subsequent solution implementation is a separate workstream authorized after data acceptance.

## 5. Mandatory reconciliation controls

All reconciliations specify the cutoff, selected source/version, grain, unit, sign convention, rounding policy, and allowable timing bridge. Equal grand totals cannot conceal offsetting errors between facilities, cost centers, accounts, lots, or months.

| Control | Equation or invariant | Required grain and treatment |
| --- | --- | --- |
| Census roll-forward | Opening census + qualifying admissions + external transfers in - qualifying discharges - external transfers out = closing census | Facility/unit and timestamp; internal transfers cancel at the appropriate parent scope. |
| Occupied time | Integrated occupied event-state seconds = reconstructed bed-interval seconds | Bed/unit/facility over the same clipped window; exact before display rounding. |
| Bed inventory | Every commissioned bed has one valid occupancy/service state at each relevant instant | Distinguish unavailable, unstaffed, reserved, and unsuitable capacity; these categories are not automatically additive. |
| Patient flow | All arrivals have an explicit lifecycle state or disposition at cutoff | Includes still-waiting, diverted, cancelled, admitted, completed, and censored cases under scope. |
| Workforce time | Worked time = productive time + paid/nonproductive components under the defined time policy | Worker/shift/day; overtime is a classification of hours rather than extra duplicated elapsed time. |
| Inventory | Opening quantity + signed movements = closing quantity | Location/item/lot/base unit; paired transfers and expiry reconcile. |
| Claim totals | Header billed amount = sum of applicable claim-line billed amounts | Original claim and selected revision; voided/replaced lines follow explicit rules. |
| Adjudication | Charges, contractual adjustments, allowed liability, payer/patient responsibility, and denials reconcile under the selected contract model | Claim/line/attempt with explicit categories; no universal equation imposed on incompatible payer contracts. |
| Cash | Opening cash/subledger balance + signed receipts/refunds/reversals = closing balance | Payer/payment batch/period and relevant account; replays have no additional economic effect. |
| Receivables | Opening AR + recognized receivable increases + other signed adjustments - applied settlements = closing AR | Claim/account/period under the documented recognition policy. |
| Expense postings | Eligible labor/resource/nonpatient costs plus documented accrual/timing movements = expense postings | Facility/cost center/account/posting month; avoid expensing both purchase and later consumption of the same stock. |
| Cost allocation | Eligible pool expense = direct allocations + pooled allocations + nonpatient/unallocated residual | Pool/period/currency/selected allocation version; each expense contributes once. |
| Axiom actuals | Selected monthly actual = sum of mapped accounting facts plus documented timing/reclassification bridge | Month/facility/cost center/account/unit/currency/version; never sum Actual, Budget, and Forecast together. |
| Plan variance | Recomputed actual-versus-plan variance = source-equivalent variance at the same scenario/vintage | Account nature determines favorability; a defined zero-denominator policy applies. |
| Source files | Manifest counts/control totals = parsed file counts/control totals = expected canonical scope | Source/file/version/period; snapshot replacement and duplicate-delivery semantics are explicit. |

Monetary calculations use decimal arithmetic. Specify rounding at the contractual line, posting, or allocation step. Any legitimate rounding residual is separately identified and allocated by a deterministic policy; there must be no unexplained residual hidden in a balancing account.

## 6. Quality rules, realism tests, and defect severity

### 6.1 Rule catalog structure

Every rule must have:

`rule_id`, description, domain, business rationale, scope/filter, severity, formula, expected result or tolerance, applicable scenario, owner, execution stage, failing-record evidence, and disposition.

Rules distinguish invalid data from valid adverse events. A denied claim, death, stockout, queue, or overtime shift is not a quality failure merely because it is undesirable. An unexplained negative balance, impossible timestamp, unlinked claim line, or unsupported clinical combination is a failure unless it is a tagged raw-source fault whose intended handling is being tested.

### 6.2 Minimum acceptance matrix

| Category | Minimum release requirement |
| --- | --- |
| Structure | 100% of required columns, types, key constraints, and allowed-domain rules pass in canonical data. |
| Referential integrity | Zero unexplained orphan references or ambiguous mandatory source mappings. |
| Identity | Required identity fields meet their completeness rules; zero unexplained generic placeholders or accidental identity merges. Legitimate duplicate names remain valid. |
| Time | Zero impossible chronologies or unexplained mutually exclusive interval overlaps. |
| Terminology | 100% of required coded facts use valid domain, version, and unit semantics for their date/context. |
| Clinical | All hard clinical constraints pass; reviewed pathway and statistical plausibility targets pass at their defined scope. |
| Operations | Zero unexplained bed overlaps, census differences, missing occupancy contributors, or invalid state transitions. |
| Workforce and resources | All hour, credential, consumption, transfer, and stock reconciliation controls pass. |
| Finance | Zero unexplained differences at stored monetary precision across mandatory subledger, allocation, and monthly controls. |
| Availability/history | All required as-of and correction tests pass; no detected future information in historical validation inputs. |
| Fault handling | Every seeded critical fault is detected and has the expected rejection, quarantine, correction, or replay result. |
| Realism | All preregistered marginal, conditional, tail, longitudinal, and scenario-specific tests pass or follow an approved low-count review method. |
| Reproducibility | Exact normalized business-content checksums match a clean rebuild under the same frozen inputs. |
| Volume and coverage | Three-year coverage and 20-25-table contract pass; published business records do not exceed 2,000,000. |

Do not assign one blanket tolerance to every realism measure. Set sample-aware bounds in Phase 0 for cohort proportions, LOS/cost quantiles, readmission patterns, arrival variance, name frequencies, roster changes, claim delays, and other agreed measures. A minimum realistic tail frequency must also be defined for important rare scenarios so an attractive mean cannot conceal their absence.

### 6.3 Severity and release decisions

| Severity | Meaning | Gate treatment |
| --- | --- | --- |
| P0 | Broken release integrity, irreproducibility, hard-limit breach, severe clinical/identity impossibility, or systemic data corruption | Blocks phase exit and release. Must be corrected and affected evidence rerun. |
| P1 | Material business-rule, history, coverage, reconciliation, clinical-plausibility, or source-contract defect | Blocks phase exit and release. Must be corrected and reviewed. |
| P2 | Nonblocking limitation with a bounded impact that does not violate a mandatory rule | Requires documented disposition, owner, consumer impact, and explicit acceptance. Cannot conceal P0/P1 defects. |

Databricks primary and foreign keys do not themselves enforce these relationships. The validation framework must explicitly test uniqueness, references, histories, and reconciliation [R9].

## 7. Required connected scenario catalog

| Scenario | Required connected facts | Expected validation evidence |
| --- | --- | --- |
| Repeat chronic-care patient | Persistent identity/condition, follow-up, observations, medication where relevant, coverage at each visit | History continuity with event-specific age and no future-condition leakage. |
| Elective procedure | Booking, authorization when required, procedure, resources, bed use if admitted, claim | Service and financial links plus cancellations/reschedules where configured. |
| ED-to-inpatient admission | ED arrival, decision, boarding, linked IPD encounter, bed placement | Single coherent episode with correct encounter and admission denominators. |
| Seasonal respiratory surge | Related diagnoses, arrival increase, care intensity, beds, staffing, supply demand | Correlated multi-domain changes over the registered interval with recovery afterward. |
| Ward/bed closure | Service-state change, placement restrictions, queue or transfer response | Reduced usable capacity with no disappearing occupied patient. |
| Workforce absence/agency response | Published roster, absence, replacement or gap, changed labor cost | Historical plan/actual distinction and reconciled hours/cost. |
| Stockout or expiry | Lot balance, missing eligible stock, substitution/delay or wastage | Balanced movements and an explicit operational consequence. |
| Denial and appeal | Original service/claim, denial reason, evidence timing, appeal, settlement or unresolved outcome | Original claim counted once; partial/final outcomes and cash reconcile. |
| Cross-month stay/payment | Service dates, posting dates, accrual/AR, later settlement | Explainable bridge between service and accounting periods. |
| Coverage or cost-center change | Effective-dated old/new records and source mappings | Correct historical ownership/coverage without rewriting earlier events. |
| Retroactive source correction | Business-effective date, later recorded date, replacement/reversal | Correct as-of knowledge and final state after replay. |
| Opening and closing boundaries | Carry-in stay/claim/stock; open stay, unsettled claim, incomplete follow-up at cutoff | Balanced initial state and honest censoring without invented future events. |

Each scenario requires at least one exact small fixture and a predeclared minimum representation in the full release. Frequency and magnitude are configured assumptions, reviewed before generation rather than selected afterward to make tests pass.

## 8. Evidence, dependencies, and change control

### 8.1 Gate evidence package

Each phase gate must record:

- Phase status: `NOT_STARTED`, `IN_PROGRESS`, `VALIDATING`, `BLOCKED`, or `PASSED`.
- Code, schema, reference, configuration, seed, and candidate release versions.
- Inputs, predecessor gates, output counts/checksums, and record-budget status.
- Automated rule results, reconciliation results, and failing-record evidence.
- Review samples, reviewers, review scope, decisions, and dates.
- Defects, root causes, corrections, rerun evidence, and accepted limitations.
- The next permitted activity; analytics solution work remains explicitly blocked until final acceptance.

The eventual evidence package may use separate files and reports. Those artifacts are phase deliverables, not files claimed to exist as part of writing this plan.

### 8.2 Dependency and regeneration policy

| Changed input | Minimum impact to reassess |
| --- | --- |
| Patient identity, birth date, or cohort | Clinical eligibility, encounter ages/history, coverage, notes, claims, and all dependent counts. |
| Pathway, acuity, or LOS rule | Clinical events, bed placement, workforce/resources, service/cost/claims, monthly actuals, and source exports. |
| Capacity, staff availability, or inventory | Actual service timing, queues, transfers, discharge, resources, financial outcomes, and later demand/state. |
| Payer coverage/contract | Authorization, claim/adjudication, liability, recognized revenue, cash/AR, and affected financial exports. |
| Account/cost-center mapping | Historical attribution, allocations, financial controls, security scope where applicable, and source exports. |
| Code catalog or calendar/time zone | Applicable clinical facts, local date/age/shift handling, historical code validity, and affected consumer fixtures. |
| Source format/delivery policy | Serialization, manifest controls, parsing, fault handling, replay, and as-of availability expectations. |

An upstream change creates a new candidate version. Never patch only a presentation total while leaving its dependent business facts inconsistent. Rerun all impacted gates and retain the earlier accepted release unchanged.

## 9. Final definition of done and solution lock

The synthetic data platform is complete only when all of the following are evidenced:

- [ ] Phase 0-9 gates have passed against the final release or applicable unchanged evidence.
- [ ] The agreed three-year history, clinical scope, 20-25 tables, and record ceiling are satisfied.
- [ ] Patients, providers, and staff have believable fictional identities and event-specific ages.
- [ ] Longitudinal clinical and operational histories are coherent, variable, and reviewed.
- [ ] Coverage, employment, organizational, source-key, and financial versions resolve correctly over time.
- [ ] Census, bed-time, workforce, stock, claims, receivables, cost allocations, and Axiom actuals reconcile at the required grains.
- [ ] Valid adverse outcomes and open/censored processes are preserved with clear semantics.
- [ ] Workday-style, Axiom-style, and clinical/operational exports pass their declared contracts and round-trip controls.
- [ ] Every required controlled-fault scenario has the expected detector and recovery evidence.
- [ ] Independent downstream validation queries produce the expected results without fan-out or future-information leakage.
- [ ] Statistical and conditional realism targets pass; repeat-seed checks show variation without hard-rule violations.
- [ ] No unresolved P0/P1 defect or unexplained monetary/state discrepancy remains.
- [ ] Required identity, clinical, operations/workforce, and finance sample reviews are recorded.
- [ ] A clean rebuild reproduces the published normalized content and all release checksums match.
- [ ] The release includes its dictionary, contracts, rules, manifests, evidence, provenance, limitations, and rebuild instructions.
- [ ] The business owner explicitly accepts the data release with the designated domain reviews attached.

Until every mandatory item passes, the overall status is **`BLOCKED_FOR_SOLUTION`**. Completion of generation alone, approval of this plan, or a visually convincing sample does not unlock solution development.

After explicit final acceptance, the data foundation status becomes **`DATA_ACCEPTED`**. This permits a separately authorized solution workstream to begin; it does not automatically start architecture implementation, forecasting, dashboards, streaming products, or AI agents.

## 10. Reference basis

These references support terminology, possible generator reuse, and interface semantics. They do not supply project-specific prevalence, staffing ratios, prices, payer contracts, or vendor file layouts. Those inputs require explicit configuration and review.

- **[R1] Synthea:** [Official Synthetic Patient Population Simulator repository](https://github.com/synthetichealth/synthea). Candidate lifecycle generator to assess in Phase 1; custom operational and financial integration remains necessary.
- **[R2] CMS ICD-10:** [Official diagnosis and procedure coding files](https://www.cms.gov/medicare/coding-billing/ICD-10-codes). Select releases by applicable service/discharge dates rather than applying one current catalog to all three years.
- **[R3] HL7 FHIR Patient:** [Patient resource, R4](https://hl7.org/fhir/R4/patient.html). Reference for patient identity and administrative semantics.
- **[R4] HL7 FHIR Encounter:** [Encounter resource, R4](https://hl7.org/fhir/R4/encounter.html). Reference for care settings, encounter lifecycle, and contextual grouping.
- **[R5] HL7 FHIR Observation:** [Observation resource, R4](https://hl7.org/fhir/R4/observation.html). Reference for measurement context and clinical observations.
- **[R6] HL7 FHIR ClaimResponse:** [ClaimResponse resource, R4](https://hl7.org/fhir/R4/claimresponse.html). Reference for adjudication and payment concepts; this plan does not claim full electronic transaction conformance.
- **[R7] Workday:** [Workday Integration Cloud overview](https://www.workday.com/content/dam/web/se/documents/datasheets/datasheet-integration-cloud-se.pdf). General integration context; actual extract definitions remain tenant-specific.
- **[R8] Strata Axiom:** [Healthcare budgeting and forecasting](https://www.stratadecision.com/budgeting-forecasting-software). Product context for financial planning; actual layouts and account mappings require a source contract.
- **[R9] Azure Databricks:** [Table constraints](https://learn.microsoft.com/en-us/azure/databricks/tables/constraints). Referential and other business invariants require explicit validation beyond declared keys.
