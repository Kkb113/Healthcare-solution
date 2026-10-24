# Integrated record-budget amendment

Phase 8 retains the reviewed **1,995,215 planned canonical rows plus 4,785 reserve rows**, within the two-million cap. The frozen Phase 0 files and historical Phase 6/7 snapshots remain unchanged.

The corrected payer and denial histories require more original insured lifecycle events. Reassign 20,000 unused slots: clinical events −10,000; conditions −3,000; stock movements −5,000; allocations −2,000; claim events +20,000. This changes allowances, never removes facts. Every registered comparison seed must also fit each table and the total.

| Business table | Planned allowance | Primary candidate rows | Unused allowance |
| --- | ---: | ---: | ---: |
| `facility` | 3 | 3 | 0 |
| `cost_center` | 45 | 45 | 0 |
| `location` | 150 | 150 | 0 |
| `patient` | 22,000 | 22,000 | 0 |
| `worker_assignment` | 900 | 900 | 0 |
| `access_scope` | 1,800 | 1,800 | 0 |
| `payer_plan` | 24 | 24 | 0 |
| `patient_coverage` | 28,000 | 28,000 | 0 |
| `catalog_item` | 3,005 | 3,005 | 0 |
| `source_key_map` | 10,000 | 10,000 | 0 |
| `encounter` | 130,000 | 128,000 | 2,000 |
| `clinical_condition` | 82,000 | 79,103 | 2,897 |
| `clinical_event` | 570,000 | 561,909 | 8,091 |
| `appointment` | 30,000 | 30,000 | 0 |
| `bed_event` | 80,000 | 71,018 | 8,982 |
| `staff_shift` | 70,000 | 66,582 | 3,418 |
| `inventory_movement` | 50,000 | 47,839 | 2,161 |
| `service_charge` | 120,000 | 113,181 | 6,819 |
| `claim` | 58,000 | 57,819 | 181 |
| `claim_line` | 117,000 | 113,097 | 3,903 |
| `claim_event` | 240,000 | 230,012 | 9,988 |
| `financial_posting` | 180,000 | 174,904 | 5,096 |
| `cost_allocation` | 163,000 | 158,527 | 4,473 |
| `finance_monthly` | 36,000 | 35,457 | 543 |
| `facility_day_driver` | 3,288 | 3,288 | 0 |
| **Total** | **1,995,215** | **1,936,663** | **58,552** |

The primary candidate business digest is `61124cc71b21198163a278fc103798d919c4346d587b3bef320091ff17edaa5e`. All 25 tables, versions, opening records, adjustments and histories are included. Native challenge/control copies are additionally cap-counted; 22 independently verified published copies produce **1,936,685** cap-counted release rows. The 64-slot challenge allocation leaves 4,721 reserve slots unallocated.

Resource-context files, generator checkpoints, SQLite test indices, native source mirrors/dictionaries, derived report cells, selected review summaries and two seed experiments have separate physical counts in the integrated validation report. They are not appended to the primary canonical tables or represented as new business facts. Only the accepted primary seed proceeds to later release certification.

## Physical copy disclosure

These counts are verified technical mirrors or metadata, not additional canonical business facts. They remain under ignored output paths and are never unioned into the accepted primary tables.

| Physical artifact | Rows / mappings |
| --- | ---: |
| Primary canonical business tables | 1,936,663 |
| Published challenge/control record copies, additionally cap-counted | 22 |
| Resource-context canonical mirrors | 1,053,661 |
| Stage checkpoint mirrors, including the repeated billing catalog | 886,002 |
| Disposable consumer index mirrors | 1,936,663 |
| Primary native source mirrors | 1,936,663 |
| Scheduled Workday snapshot mirrors | 108,440 |
| Typed source dictionary mappings | 4,940,257 |
| Derived report rows | 21,686 |
| Scalar fact mirrors represented by report rows | 50,888 |
| Selected review source-fact mirrors | 970 |
| Selected review case summaries | 136 |
| Comparison-seed canonical rows (20261024 / 20261025) | 1,935,475 / 1,932,523 |

The native package contains 3,444 data files and six derived reports, totaling 2,385,274,730 source/dictionary/report payload bytes. Recovery experiments create additional disposable copies; the test harness cleans its temporary directory. Comparison experiments and technical mirrors are not published as separate business datasets within the primary release. The final gate records the same physical accounting in machine-readable evidence.
