# Disposable consumer contracts

These Python/SQLite consumers are local validation tools. Their internal timestamp inputs use the canonical UTC seconds format. They are not Medallion pipelines, forecasting models, dashboards, agents or live integrations. Microsoft Fabric is excluded.

| Consumer | Grain and semantics | Independent comparison |
| --- | --- | --- |
| Census and capacity | One bed state per effective instant, delivered correction chain; integrate half-open occupied intervals clipped to the business window. Unknown source state and reserved/unavailable capacity remain separate. | Full-state occupied-seconds integration versus paired OCCUPY/VACATE intervals at every bed; accepted operational validator checks facility/unit roll-forward, patient compatibility and resource constraints. |
| Staffing | Latest delivered shift revision; sum worked, productive, paid nonproductive, unpaid break, overtime classification and cost by local service month. Published roster alone is not attendance. | All 36 months compared to a separate query implementation; fresh workforce rules check worker/shift/week, eligibility, time and cost equations and monthly acuity demand. Sparse captures remain scoped. |
| Inventory | Signed opening/movements at location x product x lot x base unit; amounts use Decimal. Never sum unlike quantities as one utilization metric. | Every nonzero lot balance and total book value compared to the stock consumer; fresh lot chronology/expiry/reversal/consumption rules retain source-level conservation. |
| Claims and cash | One original account; all immutable signed events; insured first observed initial adjudication/denial denominator. Opening and SELF_PAY statements excluded from payer-denial rates. | Original-level AR compared separately; signed monthly cash retains refunds/reversals. Independent source-group accounting rules compare all journals, posting dates and timing bridges. Attempts do not create new originals. |
| Patient cost | Choose one delivered allocation run per source posting; aggregate selected allocations to encounter x month x category before joining descriptive dimensions. | Every eligible posting conserves exact cents across patient, nonpatient and residual destinations. No pool disappears, and revised runs are not added to original runs. |
| Plan variance | Month x facility x center x account/measure x unit x scenario; select the latest published eligible vintage for that series. | Monetary actuals compare against known GL movement or facility closing balance at every publication. Statistics and prospective plans are independently checked by the financial oracle. Both Actual-Budget and Actual-Forecast retain NO_PLAN and ZERO_PLAN states. |

Variance output reports arithmetic actual-minus-plan. Financial favorability requires account nature and is a separate interpretation; expense and revenue differences must not share an unexplained sign convention. Closing balance controls are not monthly flows. Statistical quantity and money never share a series or denominator.

## Point-in-time inputs and labels

Historical selectors require source knowledge and delivery availability, choose the latest delivered revision, and then check business validity. They do not expire a previously delivered assertion using a retrospective `known_to` value learned later. Native Workday delivery gates can delay rows beyond their canonical source availability; native replay applies those gates in addition.

The feature fixture distinguishes orders/schedules from completed performed services, hides late diagnoses and discharge records until delivered, preserves roster publication versus attendance/corrections, and selects forecast/budget vintages only after publication. No model is trained. A live eligible IPD discharge can receive a negative 30-day readmission label only after complete observed followup and the validated two-hour encounter delivery watermark; open/censored outcomes remain UNKNOWN. Network transfers and planned returns are excluded under the modeled rule.

## Fan-out controls

Diagnoses, services, claim lines and bed intervals are many-to-one dimensions of an encounter. Joining all raw facts multiplies charges and can multiply census and patient cost. The population test calculates the unsafe multiplication exposure from the actual cardinalities and contrasts it with protected canonical sums. A 2-diagnosis x 3-service x 2-bed-interval fixture demonstrates a twelvefold error.

Consumers aggregate facts at their own grain, use existence predicates for filters and select revisions before joining. Distinct monetary values are never used to deduplicate facts: equal amounts on different charge IDs are legitimate separate facts.
