# Version 1.1 behaviour revision

Version 1.1.0 corrects six generator behaviours that version 1.0.2 produced as fixed rules. Each made a planned forecasting, real-time or agent use case unrealistic. The scale, master data, schema, row cap and every unaffected rule stay unchanged. Every seed, including the primary, now regenerates care, capacity, workforce, stock and finance from the accepted master snapshot.

Before any change, a full regeneration with the unchanged code reproduced the accepted v1.0.2 primary row for row (only `generation_run_id` differed). Every v1.1 difference therefore comes from the revisions below.

| Behaviour | Version 1.0.2 | Version 1.1.0 (primary seed) | Code |
| --- | --- | --- | --- |
| ED stay, treat-and-release | 1.7–3.0 h uniform | median 3.0 h, p90 4.3 h, 15% over 4 h | `ClinicalGenerator.ed_duration` |
| ED stay, admitted | exactly 4.0 h | median 5.6 h, p90 7.8 h | `ClinicalGenerator.ed_duration` |
| Left without being seen | full-length stay | median 1.1 h | `ClinicalGenerator.journeys` |
| Medically ready to discharge | exactly 1 h | median 3.5 h, p90 8.3 h | `ClinicalGenerator.discharge_plan` |
| Home discharge hour | flat over 24 h | 09:00–20:00, 85% between 10:00 and 17:00 | `ClinicalGenerator.discharge_window`, `extend_completion` |
| Weekend home discharges | as weekdays | 0.78 × weekday | `ClinicalGenerator.discharge_plan` |
| Admission to first bed | 10 min for 75–100% | 20–90 min when a bed is free; capacity waits to 24 h | `FlowSimulator.placement_minutes` |
| Vacate to cleaning start | exactly 10 min | median 31 min, slower overnight | `FlowSimulator.vacate` |
| Outpatient Monday volume | 3.0 × Tue–Fri | 1.06 × | `ClinicalGenerator.weekday_slot` |
| Elective Monday admissions | 2.7 × Tue–Fri | 1.34 × | `ClinicalGenerator.weekday_slot` |
| No-shows | follow-ups, 14-day lead, 10–11 h, 93% weekend | 19% base; graded by age, payer, lead time, visit type and prior misses | `ClinicalGenerator.appointments`, `booking_lead` |
| Initial insured denials | flat 9% | 9.3% overall; Medicaid 12.7%, Commercial 10.7%, Medicare 6.5%; IPD 14.0%, ED 8.5%, OPD 7.3% | `denial_risk`, `denial_reason` |
| RN unplanned absence | 0.4% | 2.5% (3.9% Dec–Feb, 2.0% otherwise); 63% colleague pickup, 37% agency | `WorkforceGenerator.absence_rate`, `choose` |

Frozen totals are unchanged: 58,012 visits, 21,800 attended / 4,000 no-show / 4,000 cancelled / 200 pending appointments, the 8–12% denial band, the 4.4–6.2 day mean stay band and every other realism target. The 900 basis-point denial rate remains the average; each claim's probability is scaled by its relative risk and normalized.

## Budget amendment

Realistic absences add retained roster history: each absent shift keeps its published, reassigned and absent versions plus a distinct replacement attendance. Version 1.1 moves 3,000 unused `bed_event` slots to `staff_shift` (bed_event 77,000, staff_shift 73,000). The 1,995,215 planned rows and 4,785 reserve are unchanged. See [the integrated policy](../../contracts/integrated-validation-policy.json).

## Checks

`scripts/validate_behaviour_revision.py` measures every revision on the full population of each seed and writes `behaviour-revision.json` beside that seed's inspection. It requires the old fixed rules to be gone (no constant durations, no feature value that makes a no-show near-certain or impossible), graded signal in the expected direction, unchanged master/reference/driver tables, and every table within budget. The Phase 8 gate requires it to pass for all three seeds, alongside the unchanged 58 domain controls, six consumers, eleven point-in-time controls, realism profiles and full native reconstruction.

## Known limitation

RN overtime rose only from 0.2% to 0.4% of RN hours. The fixed workforce holds about 88 RNs per hospital for roughly 14 RN shifts a day, so a pickup rarely crosses 40 weekly hours. Changing that would change workforce scale, which this revision deliberately does not do.
