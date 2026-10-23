# Three-year record budget

Baseline 1.0.0. Generated from the authoritative definitions in `scripts/build_phase0_spec.py`.

**25 business tables; 1,958,210 planned records; 41,790 remaining below the 2,000,000 hard ceiling.**

Envelopes include versions, lifecycle revisions, openings, corrections and declared business line facts. They are feasible planning allowances, not arbitrary quotas to pad or truncate. Future stochastic generation may use contingency, but an over-cap candidate must be recalibrated as connected histories and regenerated.

| Table | Inclusive planned rows | Grain |
| --- | ---: | --- |
| `facility` | 3 | One fictional hospital; stable identity and geography. |
| `cost_center` | 45 | One stable financial responsibility center; replacements receive a new ID. |
| `location` | 150 | One department, ward, room or physical bed; hierarchical location, not an occupancy snapshot. |
| `patient` | 22,000 | One bitemporal demographic version of a persistent synthetic patient. |
| `worker_assignment` | 900 | One bitemporal version of one worker's single exclusive primary assignment. |
| `access_scope` | 1,800 | One bitemporal grant/revocation version for a synthetic principal and business scope. |
| `payer_plan` | 24 | One versioned fictional payer product/contract. |
| `patient_coverage` | 28,000 | One bitemporal primary coverage enrollment interval/version. |
| `catalog_item` | 3,000 | One code/product/account version within a typed, validated vocabulary. |
| `source_key_map` | 10,000 | One bitemporal typed crosswalk or association mapping. |
| `encounter` | 130,000 | One knowledge revision of an ED, inpatient or ambulatory encounter. |
| `clinical_condition` | 95,000 | One diagnosis/problem/allergy assertion version with optional encounter context. |
| `clinical_event` | 580,000 | One scalar clinical event/value or text document version; typed event family. |
| `appointment` | 30,000 | One immutable booked slot; reschedule creates linked replacement, not an overwritten slot. |
| `bed_event` | 80,000 | One immutable bed state change/correction or opening-state assertion. |
| `staff_shift` | 70,000 | One knowledge version of a worker/unit shift or leave block. |
| `inventory_movement` | 60,000 | One signed location/item/lot stock movement in base units. |
| `service_charge` | 120,000 | One encounter/revenue-category/billing-period charge line with explicit units and interval; not an uncounted list of daily charges. |
| `claim` | 56,000 | One original primary institutional claim; attempts are events, not new original claims. |
| `claim_line` | 112,000 | One original claim charge line, preserving a one-charge-to-one-line baseline contract. |
| `claim_event` | 160,000 | One signed immutable submission, adjudication, settlement or adjustment event. |
| `financial_posting` | 180,000 | One debit/credit journal line; daily operational source groups or explicit monthly cost-pool close. |
| `cost_allocation` | 180,000 | One eligible monthly expense-pool-posting allocation to an encounter or explicit nonpatient/residual destination. |
| `finance_monthly` | 36,000 | One month/cost-center/account-or-statistical-measure/scenario/vintage/currency-or-unit value. |
| `facility_day_driver` | 3,288 | One facility/local-day external/calendar observation; no future realized data is known early. |
| **Total** | **1,958,210** | |

## Capacity and workload arithmetic

- Window: 1,096 days. Licensed capacity: 72 x 1,096 = 78,912 bed-days.
- Planned empty-bed closures remove 962 staffed bed-days, leaving 77,950. Occupied days: 12,000 intersecting IPD episodes x 5.2 clipped days = 62,400.
- Licensed occupancy: 79.0754%; staffed occupancy: 80.0513%. These are calibration expectations, not fixed outcomes or clinical benchmarks.
- 12,000 IPD intervals plus 3,000 extra transfers yield 15,000 intervals. At 1.25 hours mean cleaning/turnaround, 781.25 bed-days fit within staffed slack.
- 80,000 bed events include 72 opening states, 60,000 primary transition allowance, 18,528 service/staffing/reservation changes and 1,400 corrections. Actual carry-in/open-end histories may need fewer four-transition sequences; no duplicate opening admission is generated to fill a quota.
- 130,000 encounter rows = 56,000 intersecting visits + 2,000 completed opening-AR contexts + 68,000 lifecycle versions + 4,000 corrections. Opening-only contexts do not add occupancy or new-period admissions.
- 70,000 shift rows = 52,000 worked shifts + 4,000 leave/unavailability blocks + 14,000 revisions. Never sum all shift versions as worked time.
- Productive RN supply: 52,000 x 0.70 x 10.5 = 382,200 hours. Modeled RN requirement: 62,400 x 5.5 = 343,200 hours. This permits aggregate slack and local absence/coverage gaps, not an assertion that every shift is safely staffed.
- Annual worked hours: 52,000 x 12 / 3 = 208,000. Contracted roster capacity: 180 workers x 0.65 mean FTE x 2,080 = 243,360 hours/year; other workers cover nonrostered roles. Role-specific FTE/rate histories remain varied.

## Counted clinical-event detail

| Family | Rows |
| --- | ---: |
| ORDER | 50,000 |
| OBSERVATION | 70,000 |
| LAB_RESULT | 70,000 |
| PROCEDURE | 20,000 |
| MED_ADMIN | 260,000 |
| MED_DISPENSE | 20,000 |
| DOCUMENT | 70,000 |
| REVISION_ROWS | 20,000 |

6000 ED admissions +4800 elective +1143 direct/external +57 occupied carry-ins =12000 intersecting IPD. Code/clinical assumptions and uncensored LOS are validated separately from clipped bed-day arithmetic.

## Revenue, finance and allocation detail

56,000 claims include 54,000 current-period originals and 2,000 openings. The 160,000 event envelope counts 2,000 opening assertions, 54,000 submissions, 48,000 adjudications, 44,000 payments and 12,000 denial/appeal/resubmission/adjustment/refund/other events. Unsettled/unknown cases remain open.

120,000 charges have explicit billing-category intervals/quantities, split at month boundaries. 112,000 claim lines reference those charges once; unbilled/self-pay/open charge lines remain identifiable. This grain preserves billing units without inventing uncounted daily charge facts.

180,000 allocation rows fund patient-month/center/category detail: approximately 48,000 base IPD category allocations, 8,200 cross-month additions, 12,000 transfer-center additions, approximately 100,000 ED/OP category allocations, and approximately 11,800 nonpatient/residual/revision allowance. These are design envelopes; exact counts follow actual care and journal pools. Monthly pool close avoids daily allocation fan-out while retaining traceable signed expense.

All opening and monthly pool-close journals count in the following 180,000 posting rows:

| Posting family | Rows |
| --- | ---: |
| opening | 500 |
| workforce | 60,000 |
| inventory | 50,000 |
| revenue_ar_cash | 50,000 |
| monthly_pool_close | 12,960 |
| overhead_accrual_other_reclassification | 6,540 |

The 36,000 normalized financial rows have an explicit sparse-series contract. No unbudgeted Cartesian product of all account/cost-center/scenario/vintage combinations is assumed.

| Series/vintage coverage | Rows |
| --- | ---: |
| actual_pnl_45_centers_11_accounts_36_months | 17,820 |
| actual_balance_3_control_centers_6_accounts_36_months | 648 |
| actual_stats_15_centers_4_measures_36_months | 2,160 |
| original_budget_45_centers_6_accounts_36_months | 9,720 |
| midyear_budget_45_centers_6_accounts_12_months | 3,240 |
| forecast_12_selected_centers_2_accounts_12_vintages_3_months | 864 |
| budget_stats_3_centers_4_measures_36_months | 432 |
| correction_vintage_allowance | 1,116 |

Actual P&L includes 11 defined control accounts at 45 centers; balance levels use six accounts at three designated facility control centers. The six budget accounts cover gross/contra revenue and four cost pools. Source expense accounts zeroed by monthly close remain required reconciliation controls, not arbitrary padding. Correction-vintage allowance is a maximum plan, not a mandate to fabricate corrections.

## Physical release accounting

Every business version/opening is counted above. Derived intervals/calendar/census stay views. Export snapshots, repeated deliveries and raw-file mirrors report their physical serialized counts and bytes separately from canonical rows. Control reports contain metrics, hashes and evidence rather than hidden business transactions.

Future generation must publish actual per-table and total counts, source mirror counts and reserve consumption. No generator or patient records have been created in Phase 0.
