# Validation and operational review

The operational acceptance gate combines all fifteen independent clinical groups with seven operational groups: full schema/keys/references, clocks/corrections, bed-state/census/interval reconciliation, queues and unmet demand, daily drivers/seasonality, late/repeated delivery convergence, and complete record-budget accounting. The frozen 25-table design hashes must remain unchanged.

The independent oracle imports neither the simulator nor its random generator or serializer. It resolves immutable corrections, reconstructs intervals by pairing occupancy boundaries, and separately integrates full event post-states. Both must match the simulator's independently accumulated interval digest and occupied seconds. Every census boundary reconciles by facility; all occupied patients have source encounter identities. Licensed and staffed time, cleaning, reservations, private-room restrictions, boarding, transport and actual bed occupancy have distinct definitions. Physical mirrors are separately counted.

Tests cover both accepted histories and deliberate faults: duplicate/conflicting messages, orphan/cyclic correction dependencies, source knowledge before/after correction delivery, incompatible room placement, double placement, missing cleaning transitions, broken transfer legs, leaked realized drivers, changed record budgets, saturation without silently dropping waiting requests, content-bound review, full clean rebuild, cached resume, real process death/rollback, checksum corruption and configuration invalidation before failed recomputation. A no-surge counterfactual verifies that actual respiratory care cohorts change, rather than merely increasing a disconnected driver value.

A stratified hundred-case operational sample includes all hospitals, opening carry-in, observed/open outcomes, ICU stepdown, private isolation, capacity waits, external unmet-demand dispositions, elective deferrals, continuous interhospital care and maintenance-season cases. Every selected encounter revision, correlated bed event and source operational note is bound to the review hash. All maintenance, cancelled-hold and correction samples are also rendered. A modified sample or changed selected fact invalidates approval.

The designated review is performed by Codex under the user's express authorization to review and finalize the design. It is a synthetic operational/domain plausibility review, not licensed clinical endorsement. Its decision records inspected scope, findings, material assumptions and unresolved issues. No unresolved critical finding may pass. Clinical/OR workforce completeness, stock constraints, financial reconciliation, vendor source replay and final downstream acceptance remain later work; this gate never unlocks solution development.

Boarding starts at the admission decision. Administrative admission-to-placement wait is a separately reconciled component; the external-transfer escalation clock is 24 hours from administrative inpatient admission. Report first-placement/disposition latency only for observed outcomes, and report still-open unplaced requests as right-censored lower bounds. Cross-site transport seconds are reported separately from admitted care and occupied-bed time.

Sending network referrals have prospective coordination documents known at admission, with actual handoff time explicitly unobserved. Receiving coordination receipts confirm the observed arrival without asserting a later outcome. Route-specific synthetic ground-transport assumptions are 120 minutes Peoria-Springfield, 180 minutes Peoria-Rockford and 240 minutes Rockford-Springfield, plus 0-30 minutes of handover variation. They are modeling assumptions, not ambulance travel quotations. Administrative capacity transfers and continuity transfers do not force every clinical measurement to worsen; the seeded illness-response component remains distinct from transfer cause.

## Candidate control totals

The complete candidate covers 2023-2025 and contains **938,452 canonical business records in 16 populated tables**. The final release schema remains 25 tables with 1,958,210 planned records; 1,019,758 planned records remain available and the 41,790-record hard-ceiling reserve is untouched. These are partial-foundation counts, not final release acceptance.

| Control | Reconciled result |
| --- | ---: |
| Immutable bed events, including corrections | 71,018 |
| Facility/day driver observations | 3,288 |
| Opening / closing physical census | 57 / 36 |
| Census boundaries checked | 25,245 |
| Occupied seconds: state integral and paired intervals | 5,085,526,680 each |
| Licensed / staffed bed-days | 78,912 / 77,950 |
| Maintenance reduction | 962 bed-days |
| Time-weighted staffed occupancy | 75.51% |
| Mean dirty-to-ready turnaround | 74.93 minutes |
| Internal bed relocations / continuous site transfers | 3,364 / 12 |
| Source corrections / cancelled nonoccupancy holds | 100 / 100 |
| Observed external transfers for unmet compatible capacity | 539 |
| Unexplained completed admissions without placement | 0 |
| Decision-to-placement/disposition latency, 95th percentile | 22.43 hours |
| Elective pre-admission deferral, 95th percentile | 7.96 days |

The maximum observed decision-to-placement/disposition latency is 27.25 hours. Accepted network-continuation referrals have an explicit coordination history and remain in the modeled network; the external escalation rule applies at 24 hours from administrative admission to other acute requests. No unplaced open admission remains at this cutoff. Transport totals 145,620 seconds across the twelve site transfers and is distinct from the 465,960-second physical-bed gap, which also includes receiving administrative/boarding time. No transport interval is counted as occupied-bed time.

The committed acceptance gate records the final automated regression count and the four exit decisions. Clinical, operational and review evidence all bind the same candidate business hash; earlier accepted master and clinical candidates remain immutable.

## Automated regression scope

All **197 regression tests pass with zero failures, errors or skips**: 121 current framework/master tests, 38 exact accepted-revision clinical tests, and 38 current operational tests. The historical clinical suite runs its committed generator and tests from `691435db3708939196b83d9cbade39b3e5db4785`, against the immutable accepted clinical snapshot. Current clinical validators are also exercised through all fifteen integrated full-candidate groups and the operational mutation tests.

The final exit evaluator independently checks frozen design contracts, persisted canonical files and checkpoint contents, source hashes before/after evaluation, all 22 clinical/operational groups and the content-bound hundred-case review. It requires the named positive, fault, saturation, rebuild and crash-recovery tests associated with every exit criterion. A failed, skipped, stale or source-mutated test report cannot certify completion.
