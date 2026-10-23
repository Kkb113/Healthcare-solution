# Resource validation and review

The [acceptance gate](../../evidence/resource-foundation/acceptance-gate.json) records all four Phase 5 exits. The [complete evidence](../../evidence/resource-foundation/validation-report.json) binds the candidate, frozen design, tests, review and source/configuration hashes. Approval of plausibility alone never bypasses technical acceptance.

The frozen regression run passed **238 tests**, with zero failures, errors or skips:

| Regression scope | Passed tests |
| --- | --- |
| Current framework and master data | 121 |
| Exact accepted historical clinical revision | 38 |
| Current operational foundation | 38 |
| Current workforce and inventory foundation | 41 |

The resource tests include a complete matching clean rebuild, cached resume, real process crash/rollback/resume, deliberate faults and content-bound review. Local CLI smoke checks also reproduced 61,644 delivered logical staff blocks, USD 47,658,801.10 captured labor cost and USD 6,210.92 closing stock value with zero negative closing book balances. These are local foundation checks, not a deployed Databricks/source-system integration certification.

## Independent controls

The validators import no generation, scheduler, pipeline or generator serializer. They recompute controls from scalar canonical facts. The persisted inspector separately checks canonical file hashes/bytes/counts, the accepted parent, checkpoint fingerprints/payload checksums, ownership, earlier clinical shadows, mirror accounting, review serialization and source locks. It requires exact equality with saved validation controls, including Decimal metrics.

| Groups | Required evidence |
| --- | --- |
| 15 clinical | Relationships, clinical chronology, orders/doses/results, author validity, fact-grounded notes and budget, evaluated again on resource-integrated data |
| 7 operational | Immutable bed histories, independent interval/state census, occupancy seconds, capacity/queue/transfer flow and budget, evaluated again |
| 6 workforce | Schema/history; elapsed/productive/break/leave/rest/credential rules; rate/OT/cost inputs; actual event authors/operative concurrency; independent monthly census/acuity coverage; frozen caps |
| 3 inventory | Lot/price/unit/sign/value/transfer/reversal ledger; independently derived event-time FEFO and patient groups; shortage causes, readiness and permitted clinical changes |

Nursing requirement integration uses complete observed bed intervals rather than importing the shift-start scheduling calculation. Monthly coverage is checked across all 36 months against the reviewed 0.90-1.20 range. Stable logical ordering makes recurring-decimal month-boundary prorations reproduce exactly from serialized facts. This is a synthetic calibration check, not a clinical staffing validation.

The stock oracle derives its own item requirements and identifiers. It tests stock at actual medication/specimen/procedure use, then reconciles daily issue groups and closing lot/location balances. Stockout probes run before planned case-cart arrival; existing stock arriving late cannot falsely prove that the original planned start was feasible.

## Deliberate faults and end-to-end tests

The resource suite tests incorrect labor rates, double-counted overtime, mismatched time components, future plan leakage, overlapping attendance, invalid credentials, missing authors/circulating nurses, issue before receipt, expired stock, wrong receipt price/pack quantities, unbalanced returns/transfers, orphan reversals and unsupported clinical prose. It also verifies historical delivered assertions, no expense duplication across versions, late stock reversals, exact sample reproducibility and row-order invariance.

End-to-end checks regenerate the entire candidate into a clean directory and compare its complete business hash, rerun a cached resume, terminate a real subprocess during a transaction and recover, reject corrupted checkpoints, and verify descendant invalidation before injected failure. The accepted clinical regression suite runs against its exact historical source revision; current framework/master, operational and resource suites run against frozen current sources. No skipped test counts as passing. A separate [restoration check](../../evidence/resource-foundation/restoration-check.json) rebuilt the operational parent from its exact accepted Git revision and independently matched all sixteen canonical file checksums.

| Phase 5 exit | Gate requirement |
| --- | --- |
| Labor, cost, stock and resource links pass | All 31 groups, independent persisted inspection and named positive/negative regressions pass |
| No unexplained negative stock or untraceable resource cost | Event-time balance/eligibility, rate/quantity/price recomputation, transfer/return/reversal and deliberate fault controls pass |
| Connected normal, shortage, absence, agency and stockout effects | Thirty stockout and thirty absence windows, actual delay/RN/agency behavior and preserved planned knowledge pass |
| Changed clinical/operational histories pass again | All 22 prior-domain groups pass on the integrated candidate, immutable parent tables match, review passes and full rebuild/recovery tests pass |

## Recorded synthetic review

The user expressly designated Codex to review and finalize the synthetic foundation. The [decision](../../reviews/resource-foundation-review.json) records that authority and explicitly disclaims licensed clinical endorsement. All 100 named encounter summaries were inspected, including sixty shortage-window cases and forty operational/boundary cases, plus detailed source labor, clinical use, lot/expiry and correction examples. Selected facts and exact rendered text bind the decision by SHA-256; changed reviewed content reopens the review.

Findings resolved during implementation include preservation of attending-of-record semantics, surgeon concurrency and actual case-list duties, published-roster knowledge leakage, six-place reported-hour cost rounding, expiry-aware replenishment, exact prior-assessment note grounding and deterministic nursing prorations. The decision records these resolutions and the selected workforce/material boundaries. It does not claim complete clinical capture, national statistical representativeness or a production integration certification.

Financial allocations/postings, claims, Axiom actuals/budgets/forecast vintages, native source release replay, final Databricks consumer acceptance and analytics solution implementation remain outside this gate.
