# Frozen business and reconciliation rules

This document defines the baseline policies. The machine-readable catalog contains 55 numbered acceptance rules with owners, severities, scopes, expected results and execution phases. None of those data rules has run against generated records yet.

## Identity, history and clinical eligibility

- Stable patient, worker, coverage, encounter and claim identities persist across source changes. A demographic/worker correction appends a revision; it never creates a new person merely because a surname or assignment changed.
- Each version records when its facts became known. The initial encounter revision has arrival facts, later versions add admission/discharge; this is why 130,000 encounter rows are budgeted for 58,000 distinct encounter contexts.
- Adults are at least 18 on each local service date. Birthdays use calendar arithmetic. Death prohibits new clinical care afterward, while legitimate billing, appeals and settlement can continue.
- One primary payer applies at a time, including explicit SELF_PAY intervals. Coverage changes affect later service under effective/knowledge time; a prior claim is not silently reassigned to a different payer. Secondary coordination is outside v1.
- Completed assessed encounters have a primary encounter diagnosis or documented diagnostic uncertainty. Longitudinal problems, encounter diagnoses and drug-allergy assertions are different condition types, with separate required fields.
- Active drug allergies resolve to an ALLERGEN catalog row; medication products reference that allergen family. Matching only text or one particular brand/product ID is insufficient.
- Codes must be valid under their code-system date policy. For example, the Oct-Dec 2025 interval requires applicable FY2026 ICD-10 releases, not just a file labelled calendar year 2025. Relevant midyear updates must also be considered.

## Clinical pathway calibration

The following case mix and mean durations are fictional generation targets, not clinical guidance or US benchmarks. Initial route, age/comorbidity eligibility, actual resource constraints, and cutoff censoring still apply.

| Adult IPD pathway family | Starting case share | Target completed mean days | Expected linked evidence |
| --- | ---: | ---: | --- |
| Heart failure exacerbation | 20% | 5.6 | Prior/history assertions where applicable, diagnostic results, known medication orders/admin, changing clinical state |
| COPD exacerbation | 15% | 5.2 | Respiratory history, selected observations/results, respiratory treatment and supply demand |
| Pneumonia | 15% | 6.6 | Acute diagnosis, relevant diagnostic results, medication course, variable acuity |
| Other reviewed general medicine | 10% | 4.8 | Explicit pathway membership and compatible diagnoses/services, not random unused codes |
| Limited elective general surgery | 30% | 4.8 | Booking, authorization where needed, procedure order/performance, postprocedure care/resources |
| Limited elective orthopedic care | 10% | 4.0 | Planned procedure, mobility/resource needs, discharge follow-up |

The weighted completed-duration calibration is 5.21 days. The separate bed budget uses 5.2 **in-window occupied days per intersecting inpatient episode**; neither value is forced onto every patient. Use skewed conditional duration distributions and a predeclared long-stay tail, then validate completed and clipped distributions separately. The exact treatment/dosing content is not invented by this table: later pathway implementation uses pinned catalog/modules and reviewed order-specific constraints, with unit, strength, route, allergy and timing validation.

Initial route budget: 4,800 new elective admissions, approximately 6,000 ED-to-IPD admissions and 1,143 direct/external transfers, plus 57 occupied carry-ins, total 12,000 intersecting inpatient episodes. The 27,000 ED visits include nonadmitted, left-without-seen, diverted and still-open outcomes. Route and encounter-class totals must reconcile; internal ward transfers are not new admissions.

Clinical events use explicit family rules:

- Results/admin/procedures link an earlier compatible order for the same patient/episode. Document text is not an order or an observed result.
- Each analyte/value is a counted scalar row with its real unit and context-specific reference interval. Uncertain/qualitative results retain their meaning.
- Completed modeled administrations/dispenses have valid order, dose, strength conversion, route where applicable, stock group and actual consumed quantity. A cancelled/not-done administration consumes zero and creates no charge.
- Medication orders retain intended start/end, scheduled dose interval or PRN status/maximum, dose/unit/route and product formulation. Administration sequence is unique within its stable order. Validate actual timing and daily maximum, not just the existence of any earlier medication order. Infusion-rate/continuous device detail is outside the modeled formulary in v1.
- Lab results retain specimen, collection and result-ready times. Collection follows the order; a value is not known before result-ready time. Scalar analytes may share a specimen but each counts one row.
- Selected observations can be labeled daily summaries with a period and aggregation method; no summary is misrepresented as complete monitor telemetry.
- Notes vary in wording while retaining structured fact consistency, negation and availability. A discharge summary cannot leak a later readmission or payment.

## Appointment and bed-state rules

Appointments preserve their booked slot. Rescheduling cancels the old slot and links its replacement. No-show determination occurs only after the scheduled interval. A draft plan or future schedule is not a performed service.

Bed state has independent occupancy, service, staffing and reservation attributes. Normal occupancy changes are:

`EMPTY/READY -> OCCUPIED -> DIRTY -> CLEANING -> EMPTY/READY`.

`IN_SERVICE`, `BLOCKED` and `OUT_OF_SERVICE` are service states. An empty bed may still be unavailable because it is unstaffed, dirty, reserved or incompatible. Availability categories can overlap and must not be added blindly.

Enforce one occupant per bed and one active inpatient bed per patient. Transfers close/open correlated intervals atomically at the business timestamp. Do not close an occupied bed without relocation. Labor undercoverage is a separate risk measure; it does not remove an occupied patient from census or automatically relabel the bed as empty.

Resolve correction links before applying the source sequence in event time. Replaying a late correction recomputes the affected history; a correction is not an extra admission. All 72 physical beds have opening states, including 57 occupied carry-ins. Histories are integrated into intervals independently for validation.

At matching scope/time:

`opening census + admissions + external transfers in - discharges - external transfers out = closing census`.

`event-state occupied seconds = independent bed-interval occupied seconds`.

Inpatient LOS may include explicitly modeled boarding/transport/leave gaps. Do not force encounter duration to equal physical occupancy if the care model defines such gaps. Midnight billed room-days, occupied hours/24 and census-at-midnight have different definitions.

## Staffing and stock rules

Worker assignment, credential and rate must be valid and known at the relevant instant. The baseline permits one exclusive primary assignment; temporary worked-unit changes belong to shift versions. Leave/availability blocks do not create worked hours. WORK intervals cannot overlap for a stable worker.

`worked hours = productive hours + paid nonproductive hours + unpaid attended breaks`.

Overtime is a subset of paid hours, not additional elapsed hours. Loaded cost includes the effective employer burden and explicit overtime/agency rules once. A late attendance correction changes a later knowledge version and produces an accounting adjustment rather than rewriting a certified prior close.

The 5.5 RN productive hours per patient-day assumption is a demand-model parameter. Actual acuity-specific shift targets, constraints and absence scenarios are validated separately; it is not a safe-staffing recommendation.

For stock at location/item/lot/base-unit grain:

`closing = opening + signed receipts + returns + transfers in - consumption - transfers out - expiry + signed adjustments`.

Transfers balance across locations. Administered quantity is converted from dose unit using catalog strength/base units. A daily item/lot/unit consumption group equals all modeled administrations/dispenses plus explicit nonpatient waste. Transfers are not consumption. Receiving stock does not itself mean that a patient consumed it. Expired/unavailable stock cannot be issued unless a tagged raw-source fault is being rejected.

MED_DISPENSE is take-home supply in this baseline. Ward dispensing is an inventory transfer, and subsequent inpatient administration is consumption; it is not charged to stock twice. A take-home prescription does not invent future administrations outside the observed care setting. Cancelled/not-done medication events have zero consumption and a null stock-consumption group.

Eligible stock follows first-expiry-first-out selection. A lot retains its receipt unit cost and expiry through transfers and returns; returns/reversals preserve original valuation. A procurement price change creates a new lot/cost identity instead of silently repricing earlier consumption. Partial receipts against one lot must agree on the declared valuation policy. This keeps quantity and monetary stock roll-forwards compatible.

## Charges and claims

`service_charge` represents the source billing line at encounter/revenue-category/billing-period grain, with explicit service_from, service_to and quantity. A line cannot span accounting months. This is a declared source grain, not hidden daily charge rows. Room units derive from the configured billable-day convention over represented stays, with a minimum one unit for a billable short stay; the discharge-day convention must be consistent. Procedures use actual performed units, pharmacy categories use actual modeled consumption under the configured price basis.

`billed_amount = HALF_UP(units * unit_price, cents)`.

Each charge appears in at most one live original claim line. Some charges remain unbilled, self-pay or in progress at cutoff. Original billed header amount equals original claim-line totals. Attempts and appeals use the original claim identity; a resubmission is not a new denominator.

Submission and appeal state events can have zero financial deltas. Adjudication may establish payer/patient responsibility and adjust contractual estimates. Pending denial is not automatically a write-off. Payments are not recognized revenue. The simplified model has no secondary payer coordination, cross-payer rebilling or detailed professional billing.

Claim AR is the **billed claim subledger**, not all enterprise receivables. Completed eligible charges initially create unbilled service AR, derived from the charge/service/coverage predicate. The first SUBMITTED event assigns the net prospective receivable into claim AR with positive ar_delta; it transfers an already recognized balance and has zero new recognized revenue. Any GL control-account reclassification has zero net AR and zero revenue. Later attempts do not repeat that assignment. Enterprise AR reconciles billed claim AR **plus** current unbilled eligible service AR, not claim balances alone. Baseline opening unbilled AR is explicitly zero; opening billed claim balances remain nonzero.

An OPENING claim event establishes state, with **zero current-period ar_delta/cash/revenue**. Opening AR resides in the claim header and opening ledger journal. Do not add it twice. Prior billed charges/line contexts remain available for traceability but contribute no new-period revenue.

Opening claims preserve original billed lines, historical contractual adjustments, historical net cash and historical write-offs, with `opening_ar = original_billed_amount - opening_contractual_adjustments - opening_cash_collected - opening_writeoffs`. These are opening context balances, not uncounted prior-year transaction rows or new-period settlements. New claims have zero opening balances. Their initial contractual estimate is `original_billed_amount - sum(expected_allowed_amount)`; later changes are explicit events.

`closing AR = opening AR + sum(current-period signed ar_delta)`.

Cash receipts are positive cash deltas; refunds/reversals are negative and linked to the original event. Patient/payer responsibility reclassification alone changes neither total AR nor revenue. Write-offs reduce AR under explicit accounting policy. Original claim liability, original billed amount, contract adjustments and cash are not interchangeable measures.

## Double-entry accounting and monthly cost pools

Each journal line has exactly one positive debit or credit. Reversals swap sides and reference original lines. Per journal/entity/currency:

`sum(debits) = sum(credits)`.

The simplified recognition policy is:

1. Completed eligible service/billing periods create gross service AR and revenue; contractual estimates are explicit contra-revenue/AR entries.
2. Later adjudication changes the estimate/receivable through signed adjustment journals; it does not recognize the same gross service again.
3. Receipt debits cash and credits AR. Refunds and write-offs have explicit linked entries.
4. Stock receipt debits inventory and credits AP. Consumption debits expense and credits inventory. Never expense both purchase and consumption.
5. Actual loaded shift cost debits labor expense and credits payroll payable. Explicit accruals and corrections bridge service and posting months.
6. Overhead/nonpatient expense is represented in GL facts with declared generation assumptions, not a hidden target that appears only in the Axiom file.

Daily source groups retain exact recomputable predicates over charges, events, shifts and stock. A journal does not need one line per dose; the source-group sum must still reconcile exactly. Journals can balance across cost centers within an entity; an allocation/report must not falsely demand that every individual cost center is a balanced accounting entity.

Nonrostered administrative workers' modeled salary expense is derived from effective FTE, loaded hourly cost and annual contracted hours/12, prorated across effective employment/rate changes, rather than unlinked random overhead. These monthly source-group postings reference the worker-version/date predicate. Other modeled overhead has declared calendar/rate drivers and an explicit GL origin; no uncounted payroll table is implied.

At monthly close, debit LABOR/DRUG/SUPPLY/OVERHEAD_POOL expense and credit the corresponding DIRECT expense. This preserves net total expense. The 11 selected P&L accounts include gross/contra revenue, four direct expenses, four pool expenses and OTHER_EXPENSE. Six control balance-sheet accounts are cash, AR, inventory, AP, payroll payable and opening equity.

Only the monthly eligible pool debit/reversal is distributed analytically. Allocations use patient-month/category/center, with explicit NONPATIENT and RESIDUAL destinations. One selected known allocation run per source pool is used. Ordinary source expenses are not also allocated a second time.

`pool signed expense = patient allocations + nonpatient allocations + residual`.

Use nonnegative shares summing to one. Allocate cents with largest remainder and a stable destination-ID tie break; negative source reversals yield negative allocated amounts. Allocation rows are not new GL expenses.

## Axiom, financial metrics and leakage

Monetary ACTUAL equals net mapped journal movement for P&L, or the configured cumulative closing balance for balance-sheet accounts. **Do not compare a closing AR balance to only that month's AR movement.** The source contract distinguishes these semantics by account class. All data is USD; statistical quantities carry their own units.

Original budgets and revised budgets are separate vintages. Quarterly forecasts retain publication time and three target months; they cannot use later actuals or realized weather/respiratory drivers. Missing budget series are not silently zero. Compare variance only on explicitly comparable series/vintages; define zero-denominator behavior.

Revenue favorable variance is Actual minus Budget; expense favorable variance is Budget minus Actual under normalized business signs. Normalized revenue = credit minus debit, expense = debit minus credit, asset = cumulative debit minus credit, liability/equity = cumulative credit minus debit. Contra-revenue is separately labeled and reduces gross revenue. Never sum balance levels across months or sum Actual/Budget/Forecast together.

All independent additive facts are aggregated to the requested grain before a join. Denial rate uses original claims with observed initial adjudication; readmission uses eligible discharges with complete 30-day follow-up and excludes continuous transfers/planned returns. Selected clinical variables not recorded are unknown/out of scope, not automatically healthy.

## Change and exception policy

Statistical assumptions may be revised only as a new baseline version with affected evidence rerun. Hard integrity violations, unexplained money differences, the two-million cap and data-generation/solution separation cannot be waived. Raw faults are tagged challenge inputs; legitimate deaths, denials, absences and stockouts remain valid business facts.
