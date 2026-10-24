# Full-history realism scorecard

All three preregistered seeds passed fresh full-population inspection. Each covers 36 local calendar months, three hospitals and 324 month/facility/encounter-class partitions. These are configured fictional healthcare distributions, not estimates of US population prevalence. Overall acceptance additionally requires the [integrated exit gate](../../evidence/integrated-history/acceptance-gate.json).

| Seed | Canonical records | Domain groups | Mean / P95 IPD stay (days) | Initial insured denials / observed originals | Denial rate | Joint profile cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 20261023 | 1,936,663 | 58 | 5.029 / 8.083 | 4,665 / 50,080 | 9.315% | 13,198 |
| 20261024 | 1,935,475 | 58 | 5.053 / 8.417 | 4,595 / 50,034 | 9.184% | 13,154 |
| 20261025 | 1,932,523 | 58 | 4.998 / 8.417 | 4,613 / 50,112 | 9.205% | 13,146 |

Opening-only claims and self-pay statements are excluded from payer-denial rates. The original 8-12% target, 4.4-6.2 day mean LOS, 2.5-9% long-stay tail and other frozen tolerances remain unchanged. Additional seeds regenerate complete connected histories against the same fixed catchment; they are not combined with the primary release.

| Payer share of intersecting visits | Frozen target (+/-5 percentage points) | 20261023 | 20261024 | 20261025 |
| --- | ---: | ---: | ---: | ---: |
| COMMERCIAL | 40% | 40.288% | 39.733% | 40.197% |
| MEDICARE | 35% | 37.483% | 37.747% | 37.844% |
| MEDICAID | 15% | 14.493% | 14.759% | 14.395% |
| SELF_PAY | 10% | 7.736% | 7.761% | 7.564% |

The primary includes 20,000 active fictional people, 300 stable workers, 209 distinct worker birth month/day combinations and 36 open IPD visit segments. Ages are calculated at local arrival: people aged 100 at opening may naturally age to 103. The 136 active people first observed at ages 101-103 are disclosed separately rather than capped or recoded. Twelve continuous-transfer segments are visit segments, not new network admission/readmission events.

Each joint cell retains month, hospital, service, encounter class, payer, age band, acuity, scenario, count, parent month/facility/class denominator and a descriptive 95% Wilson interval. All primary joint cells are sparse (n<200), so arbitrary subgroup percentage gates are prohibited. Repeat visits are correlated and the catchment is configured; these intervals do not establish population uncertainty. Fresh clinical/resource domain controls add conditional and causal validation.

The primary normalized duplicate-note shares range from 0% for operative notes to 0.754% for progress notes, below the predeclared 15% ceiling. The normalization removes the configured patient identity headers, event identifiers and timestamps; underlying clinical values and observed service context remain. Template-driven text is explicitly scoped and does not establish clinical effectiveness.

Independent primary consumers reconcile 57,819 original accounts, 1,001 location/product/lot grains, 1,673 selected source cost postings, 134,867 patient/month/category cost grains, 18,981 monetary Axiom comparisons and 41,256 actual/plan comparisons. There are zero unexplained differences. All 72 bed-level occupied-second balances reconcile, totaling 5,085,526,680 seconds. Opening staffing context in December 2022 remains separate from 36 business months.

The 11 point-in-time controls preserve source availability, late diagnoses, service completion, discharge, roster revisions, prospective plan vintages and unknown outcomes. A negative 30-day readmission label additionally waits for the independently validated two-hour encounter delivery watermark. No forecast or clinical model is trained.

The [recorded review](../../reviews/integrated-history-review.json) binds 112 patient summaries, 24 workforce summaries and twelve quarterly deep clinical notes. See [validation scope and limitations](validation-and-review.md), [issue dispositions](../../reviews/integrated-history-issues.json) and the [record budget](record-budget-amendment.md). Mortality incidence, complete hospital payroll/cost capture and vendor-certified source layouts are outside the accepted synthetic scope. Phase 9 clean-environment certification and explicit final acceptance remain pending; solution development stays blocked.
