# Validation execution notes

Phase 0, 2026-10-27. No new paid workload, synthetic generation, analytics pipeline or dataset change was made. Read-only metadata and official price retrieval supplemented existing prerequisite evidence. Prior prerequisite charges remain unsettled and retain the INR200 reservation.

The initial full-scope estimate failed the INR20,000 ceiling. A proposed INR45,000 increase was declined. The user then explicitly approved the reduced POC scope at the original ceiling; the rejected model is retained for traceability. Benchmark reduction is approved scope, not an undisclosed skipped test. All mandatory integrity, authorization, recovery and performance/RTI contracts remain.

Price selector development exposed SKU-vs-meter naming and multiple storage-redundancy matches. The corrected selector requires one matching paid Consumption item, East US, first tier, exact meter/SKU and Hot LRS storage; ambiguity fails. The selected evidence retains full official item metadata and raw-response hash.

The first pytest attempt had13 passing cases and21 setup errors because the sandbox's default numbered temporary directory was unavailable. No contract assertion failed in that attempt. The runbook now uses a new uniquely named directory within ignored workspace output; the complete suite passes there. Lint/format findings were corrected before the final run. Reports record the final complete run; these notes preserve earlier failures rather than recasting them as successes.

Required tenant probes have not been executed by this phase. Capacity5 Luna is explicitly insufficient concurrent-load sizing; Lakebase billing mapping and automated compute quantities remain unmeasured planning assumptions. Later admission gates must measure/reprice them. Phase 0 design validation does not establish future latency, forecast quality, alert delivery, exact billing cessation or real-patient readiness.

Final semantic review corrected two roadmap/design assumptions against accepted source policy/code: base RN demand is5.5HPPD with acuity/minimumcoverage, not flat8.0; and availability-aware projections must not use retrospectiveknown_to to hide a version before its replacement is delivered. Payerdenial excludesSELF_PAY/internal statement adjudication; estimatedcontribution includes initial allowed revenue as well as later recognized_revenue_delta. Source data was unchanged.
