# Fixtures, reconciliation and coverage

The [fixture catalog](../../contracts/phase1/rule-fixtures.json) contains **55 rule-family positive cases and 123 deliberately invalid mutations**. Each case records its Phase 0 rule ID, severity, affected case key and classification. Every negative control names the reason expected from the intended detector. Missing a fault, rejecting its valid counterexample, or failing for the wrong reason fails the control.

Cases classify valid business behavior separately from adverse outcomes such as death followed by permissible billing, no-shows, diversion, staffing shortage, denied/resubmitted claims and open appeals. Those adverse positives must pass consistency checks; they are not malformed source rows. Malformed/inconsistent mutations remain outside the candidate business projections.

## Literal golden expectations

| Scenario | Independent expectation |
| --- | --- |
| Name collision | Two Maya Thompsons have different typed source/person keys and separate records; names cannot deduplicate them |
| Leap birth | DOB 2004-02-29 has age 19 on 2023-02-28; 19 on 2024-02-28; 20 on 2024-02-29, matching the frozen Feb-28 nonleap convention |
| Spring DST | Chicago 2024-03-10 01:30 to 03:30 is one elapsed hour; 02:30 is nonexistent and rejected |
| Fall DST | 2024-11-03 01:30 fold 0 is 06:30 UTC and fold 1 is 07:30 UTC; 00:30–02:30 is three elapsed hours |
| ED/IPD linkage | ED 04:30–06:30 UTC and IPD 06:30–09:30 UTC on Nov 3 share one patient, two encounters and no overlap; transfer adds no encounter |
| Bed transfer | Bed A occupied 06:30–07:30 and bed B 07:30–09:30: 3,600 + 7,200 = 10,800 occupied seconds; a shared half-open boundary is valid |
| Staff shift | Three worked hours = 2.50 productive + 0.25 paid nonproductive + 0.25 unpaid break |
| Stock | Opening 10 + receipt 5 − consumption 2 = 13 base units |
| Charge rounding | Three units × 0.335 = 1.005, rounded HALF_UP to 1.01; a negative lot valuation −1.005 rounds to −1.01 |
| Partial payment and refund | Opening billed AR 100 − payment 60 + refund 10 = closing AR 50; cash 60 − 10 = 50; refund links to the payment |
| Cost pool | 100 allocated by weights 7:2:1 gives patient 70, nonpatient 20, residual 10; GL expense remains 100 |
| Cent allocation tie | Five cents with equal A/B/C weights gives .02/.02/.01 in stable key order; the reversal gives the exact negatives |
| Code release | Test code `FIXTURE_DX` selects FY2024 on 2024-09-30 and FY2025 on 2024-10-01, provided the release was already published |
| Retroactive worker correction | A Jan-effective rate remains 40 when queried before the Nov 10 knowledge correction; the same service time resolves 42 after that correction |
| Axiom replacement | Historical actual 100, corrected current actual 90; current total is 90, not 190; both knowledge versions remain inspectable |

`FIXTURE_DX` is explicitly a test namespace. No test value is represented as a complete official ICD/UCUM/RxNorm release, real payer contract or measured clinical benchmark. Human names are fabricated examples and contacts use `example.invalid`.

The projected candidate includes a simplified opening receivable/payment/refund ledger and a separate 100 cost-pool fixture. It is not a complete accounting close or full cost-to-care model. Full charge-to-claim-to-GL/enterprise billed+unbilled AR reconciliation remains Phase 5 work. These limitations do not weaken the primitive arithmetic/recovery checks or silently change Phase 0 recognition rules.

## What runs independently

The validation module imports no generation/orchestration/source helper. It recalculates decimal products and sums, UTC duration, calendar age, interval overlap, bitemporal selection, per-grain journals, account/center/month balances and record-budget arithmetic. Literal expected values live outside generated formulas. An AST check and a generator-rounding sabotage test demonstrate this separation. Removing the charge detector also causes its negative controls to fail.

For the candidate projections, six checks cover shape, identities, encounter/clinical chronology, references, resources and finance. A seventh reads the Workday/Axiom CSV with Python's CSV parser and independently compares hashes, counts, exact rows and totals. As-of lookup expectations add another check in the framework runner; the standalone inspector additionally verifies the framework gate and all persisted input/output locks. All checks identify scope and supply affected keys/reasons on failure.

The framework's **193 expected-pass results** comprise 55 positives + 123 negative-control outcomes + 7 source-recovery outcomes + 6 candidate projection checks + 1 export check + 1 as-of lookup check. Negative-control detector findings themselves are expected failures, recorded under each control; they are not silently counted as passing real-data rules. Profiles expose row counts, null counts, distinct values and extrema. Reconciliation reports expose independently observed values, literal expectations and differences, including nonzero differences on a blocked run.

## Complete rule-family inventory

| Group | Phase 0 IDs exercised by microfixtures |
| --- | --- |
| Identity/organization/security/coverage | ID01, ID02, NM01, NM02, OR01, WK01, WK02, AC01, CV01 |
| Time, lifecycle and terminology | TM01, TM02, TM03, CD01, CD02, EN01, EN02, EN03 |
| Clinical and appointment | CN01, CN02, CE01, CE02, CE03, AP01 |
| Beds and workforce | BD01–BD05, SF01, SF02 |
| Inventory and charging | IV01–IV03, CH01 |
| Claims and accounting | CL01–CL04, GL01–GL03, CO01, CO02 |
| Planning and source | AX01–AX03, SR01–SR03 |
| Drivers, realism and global controls | DR01, RS01, RS02, CP01, RP01, FN01 |

The case catalog is checked against all frozen rule IDs/severities; an omitted case, omitted negative control or disabled fault stage cannot produce a passing run. Budget fixtures include hidden history, per-table limits, table limits, aggregate child rows and the hard ceiling. Financial fixtures include offsetting errors that preserve the grand total but fail the declared source/account/encounter grain.

These are **rule-family microfixture implementations**, not exhaustive implementations of every clause of the release rules. For example, the miniature hierarchy has two beds rather than the release's 72; clinical discriminator fixtures cover representative types rather than the full clinical matrix; staffing and realism checks use tiny literal denominators. Full-schema validation, full code/clinical-matrix coverage, all 72 bed openings, clinical safety constraints and cohort-specific statistical evidence must be expanded alongside their data phases. The release rules remain `SPECIFIED_NOT_DATA_EXECUTED` until those phases execute them on a candidate release.

## Framework and recovery tests

The suite tests every stage's exception/rollback/resume; real subprocess death during a billing transaction; single-writer rejection by a second process; invalidation before changed-upstream failure; seed variation; stable per-entity streams; clean rebuild and cached resume; code/reference changes; corrupt checkpoints; quota rejection before commit; source missing/corrupt/schema/mapping faults; correction chains; replacement lineage; quarantine repair; independent export inspection; and critical-rule block/resolution.

See the exact test names, outcomes, runtime/code/reference/config hashes, canonical and mirror counts, stage hashes, expected/observed reconciliation and independent inspection in the [execution report](../../evidence/phase-1/validation-report.json). The report contains small test-control evidence only. It does not contain a generated healthcare population.
