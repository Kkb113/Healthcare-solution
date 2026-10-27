# Build budget review

Phase 0, reviewed 2026-10-27. Authorized ceiling: **INR 20,000**. The user explicitly declined the INR45,000 proposal and requested a scope redesign before approval.

The original full repeated workload estimates **USD258.918 / INR32,252.33**, or **INR43,485.93** at four instead of two estimated Genie DBUs per question. That design does not fit the ceiling. Its [original cost model](../contracts/architecture/full-scope-cost-model.json) is retained as rejected-scope evidence, not permission to spend.

The redesigned POC estimates **USD136.458 / INR17,802.05**. Its four-DBU Genie stress case is **INR19,850.53**. Both include INR100/USD planning FX, an 18% tax allowance, INR200 held for unsettled prerequisites, all four search deletion tails and INR1,500 contingency. A simultaneous 10% increase in unit prices and planning FX reaches **INR21,183.59** and must block new work. No credits/free units/promotions are assumed. Usage quantities, including two DBUs per Genie question, remain engineering estimates requiring measured tenant pilots.

**Proposed scope revision — pending explicit owner approval:**

| Item | Roadmap before redesign | Funded POC proposal |
| --- | --- | --- |
| Initial native Genie benchmark | 40–60 questions per space | 20 per space, 80 total; at least 18/20 correct per space |
| Native Genie after recreation, batch release and RTI | Full repeated benchmark sets | 2 targeted stochastic questions per space at each stage, both must pass; complete deterministic trusted-SQL, contract, reconciliation and authorization tests still run |
| Native question envelope | 680 minimum with repeat suites and tool/control calls | 124 total: 80 initial +8 recreation +8 batch +8 RTI +12 agent tools +8 control/probes |
| Changed Genie definition | Rebenchmark | Fresh full affected-space 20-case benchmark; old evidence invalidated; reprice before dispatch |
| Search lifecycles | 5 independent cycles | 4: Phase2; one shared Phase10/11/12 initial window; Phase12 post-sleep wake; Phase13 |
| Cloud execution allowance | 15 SQL hours /48 batch DBUs /36 app-hours | 8 SQL hours /20 batch DBUs /24 app-hours; prepare locally, batch checks and stop unused components |
| Full agent evaluations | Two-evaluation placeholder conflicted with mandatory RTI regression | Full200 at Phases10,12,13 plus50 quick before each funded deployment; no reduction |
| Security, exact reconciliation, recovery, required capabilities, performance and RTI realism/soak | Mandatory | All retained, including >=100 completed requests/component, 10users, five/seven replay days and five-seed long-horizon realism |

The smaller native benchmark provides narrower stochastic coverage and less statistical confidence; it is a synthetic POC qualification. Eight targeted questions are never reported as a rerun of all80. Reuse requires exact input/code/configuration/permission/dependency hashes. Any affected definition change invalidates the relevant cached certification. The atomic reservation, native budget, uncertainty and external guard boundaries remain mandatory.

The combined search window does not bypass phase sequencing: gates and commits/pushes remain sequential. Only local preparation overlaps. If a failure breaks the window, stop and reserve a new lifecycle/tail before continuing. No phase may omit a required safety/integrity check to fit an hours estimate. The [frozen workload proposal](../contracts/architecture/test-workloads.json) contains exact counts, samples, clocks and environment requirements.

The [machine-readable model](../contracts/architecture/cost-model.json) prices every retained workload and meter. Published rates and estimated quantities are separate; the gate harness independently recomputes decimal totals, rounds each line upward to paise and verifies rate evidence.

Failed/retried billable native questions consume the124-question envelope too. There is no unlimited retry budget. Permission rejects before model dispatch do not consume a billable native question, and all mandatory negative authorization cases still run. A count/cost overrun requires an explicit remaining-work decision, never relabeling failed calls as free.

The mandatory settled 24-hour sleep interval starts after any billed deletion tail, rather than claiming that a billed tail is zero-compute sleep. Additional cycles must be repriced before starting.

The INR6,000 monthly target estimates **INR5,471.45 for one three-hour demonstration** or **INR5,698.01 for two one-hour demonstrations**, including INR600 monthly contingency. Each profile has20 native Genie questions total and short RTI windows. Two full working days are outside this funded proposal. Phase12 must measure and settle the selected profile before any recurring schedule.

Luna capacity five currently allows five requests and 5,000 tokens per minute. Phase 2 must size and verify the exact US Data Zone route against the frozen ten-user workload. A quota shortfall blocks dependent work; there is no automatic model or processing-geography substitution. Automated compute and Lakebase CU billing quantities also require tenant pilots. A planning estimate passing later does not waive these holds.

Decision: **Approved reduced POC scope at INR20,000**, direct user reply recorded in `design-review.json`. The roadmap now contains these counts. This design approval does not pass future tenant, performance or actual-cost gates; no cloud workload/budget was changed in Phase0.
