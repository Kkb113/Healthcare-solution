# Clinical foundation validation and review

Implementation phase: 3. **All exit criteria passed: 159 tests, zero failures/errors/skips, 15 clinical groups, independent file inspection, clean rebuild/cache/crash recovery, and unchanged frozen-design regression.** The [acceptance gate](../../evidence/clinical-histories/acceptance-gate.json) records the authoritative full exit status and software test results. The clinical candidate remains provisional pending resource integration; final dataset and solution acceptance are blocked.

## Actual canonical scope

| Table | Actual rows | Frozen envelope |
| --- | ---: | ---: |
| `access_scope` | 1,800 | 1,800 |
| `appointment` | 30,000 | 30,000 |
| `catalog_item` | 3,000 | 3,000 |
| `clinical_condition` | 79,509 | 95,000 |
| `clinical_event` | 536,689 | 580,000 |
| `cost_center` | 45 | 45 |
| `encounter` | 127,941 | 130,000 |
| `facility` | 3 | 3 |
| `location` | 150 | 150 |
| `patient` | 22,000 | 22,000 |
| `patient_coverage` | 28,000 | 28,000 |
| `payer_plan` | 24 | 24 |
| `source_key_map` | 10,000 | 10,000 |
| `worker_assignment` | 900 | 900 |
| **Populated total** | **840,061** | **1,958,210 across the final 25 tables** |

The candidate has 14 populated business tables and 1,118,149 rows of unconsumed planned allowance. The original 41,790-record hard-ceiling reserve is untouched. All 78,922 accepted master/opening rows are preserved; clinical_condition adds new assertions rather than rewriting opening facts.

## Clinical-event family accounting

The frozen family breakdown is a planning allocation. Actual explicit orders, results and procedures use more of that allowance, while captured oral administrations use less. These differences were explicitly reviewed. The unchanged clinical_event table cap is 580,000; there is no quota padding or hidden panel/medication array.

| Family | Planned allocation | Actual counted rows |
| --- | ---: | ---: |
| ORDER | 50,000 | 108,295 |
| OBSERVATION | 70,000 | 139,200 |
| LAB_RESULT | 70,000 | 79,577 |
| PROCEDURE | 20,000 | 34,324 |
| MED_ADMIN | 260,000 | 97,871 |
| MED_DISPENSE | 20,000 | 7,865 |
| DOCUMENT | 70,000 | 69,557 |
| REVISION_ROWS | 20,000 | 0 |
| **Total** | **580,000** | **536,689** |

## Executed full-data checks

All 15 clinical groups run independently of generation arithmetic: full schema/types, keys, FKs, master preservation, availability, encounters, appointments, conditions, terminology, events/specimens, medications, trajectories, document facts, longitudinal targets and row budgets. The separate read-only inspector also compares serialized canonical content with checkpoint row sets and verifies input/reference/runtime locks.

| Metric | Measured result |
| --- | ---: |
| Intersecting IPD / ED / OPD | 12,000 / 27,000 / 17,000 |
| Completed prewindow contexts | 2,000 |
| ED-to-IPD continuous episode links | 6,000 |
| Occupied carry-ins / open IPD / terminal outcomes | 57 / 59 / 30 |
| Completed IPD mean LOS, days | 5.2042 |
| Completed IPD over 10 days | 5.03% |
| Patients with repeated in-window visits | 57.02% |
| Repeat ED/OPD patients with varied complaints | 79.60% |
| Eligible 30-day readmission numerator / denominator | 1,281 / 11,432 |
| Home discharges with incomplete 30-day follow-up | 256 |
| Labs becoming known after discharge | 5,391 |
| Pneumonia marker correlation | 0.9400 |
| CKD vs other creatinine mean difference, mg/dL | 0.904155 |

Readmission excludes continuous transfers, planned returns, deaths and incomplete follow-up. The 1,320 deliberately linked returns therefore do not automatically equal the eligible metric numerator. Late lab availability preserves pre-discharge collection time and does not appear in earlier notes. All scalar results, repeat collections, orders and documents count as individual rows.

## Recorded sample review

The [sample](../../reviews/clinical-journey-sample.md) contains 100 clinical journeys spanning every required age/acuity/service/site/pathway and adverse/censored boundary stratum. The [decision](../../reviews/clinical-journey-review.json) records the reviewer, method, findings, scope, patient identities and content hashes. All 100 encounter summaries were reviewed; ten detailed narrative examples cover all six inpatient and both episodic symptom pathways. Every generated note also passes independent closed-grammar fact checking. This does not imply manual or licensed clinical review of all notes.

The user designated Codex to review and finalize the synthetic domain design. The review accepts the scoped synthetic plausibility; it does not validate treatment effectiveness, individual prescribing suitability, regional prevalence or normal laboratory thresholds. The longer-stay inpatient surgical cohort and selected non-exhaustive capture are declared limitations. Resource-constrained timing, stock, finance and source-delivery reconciliation remain later gates.

## Physical copies and release boundary

This candidate serializes 840,061 canonical rows, 840,061 checkpoint row copies and 1,252 rendered review fact copies: 1,681,374 physical row copies within the run. The committed review-document copy is another 1,252-fact mirror. The retained accepted master run and temporary rebuild/test runs have their own manifests; they are not additional canonical release rows.

No generated JSONL, SQLite, source archive or test candidate is committed. Code, configuration, bounded references, selected review mirrors and control evidence are versioned. The final release still requires all 25 tables and its remaining phase gates before DATA_ACCEPTED.
