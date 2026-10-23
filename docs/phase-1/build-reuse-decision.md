# Build/reuse decision: optional clinical lifecycle tooling

Decision date: October 23, 2026. **Build the controlled Python generation/validation framework for this baseline. Do not make Synthea a mandatory runtime dependency in Phase 1.** Keep future clinical reuse behind an explicit adapter and change review.

The evaluation reviewed the [official Synthea repository and README](https://github.com/synthetichealth/synthea), not a locally executed Synthea trial. It documents a modular patient lifecycle simulator, reproducible seed/configuration options, clinical records and CSV/FHIR exports; its current requirements include Java 17 or newer and its code uses Apache License 2.0. These features make it a plausible clinical-content component, but do not establish compatibility with this project's row budget or business contracts.

| Decision factor | Assessment for this baseline |
| --- | --- |
| Clinical longitudinal content | Reuse could reduce later pathway authoring effort; outputs still require independent plausibility and terminology review |
| Exact volume and scope | The project must fit 25 scalar business tables and 1,958,210 planned rows, including histories; no evidence yet that unconstrained lifecycle output fits |
| Hospital resource causality | Bed/cleaning/acuity/staff/stock feedback and explicit unmet demand need a shared operational scheduler and adapters |
| Workday | Effective/known workforce, hierarchy, security and retroactive corrections require a separate source/identity model |
| Axiom and finance | Recognition, claim attempts, signed cash/AR, double entry, cost-pool conservation and planning vintages require separate modeling |
| Historical knowledge | Generated clinical facts must acquire lifecycle versions and source/availability times without hindsight |
| Reproducibility | Adding Java and clinical module releases adds input locks and cross-runtime rebuild requirements |
| Validation | Generator-generated expected outcomes cannot replace independently calculated invariants |

Before future reuse, prototype a small fixed cohort and explicitly map identity, code release, encounter/condition/event grain, order/result/admin links, unit conversions, cancellation and censoring, known/available timestamps and reference licenses. Measure child-row expansion against the complete budget. Reconcile resource use and charges to the shared scheduler. Pin the exact Synthea commit/modules/Java runtime, and prove clean rebuild and existing fault detectors still pass. A failed budget/causality assessment means keep the reviewed native pathway approach; do not trim connected clinical rows after generation.

No Synthea installation, execution, performance benchmark or clinical signoff is claimed. Phase 1 delivered the necessary framework and a recorded decision, as required. The full Phase 3 lifecycle generation strategy remains reviewable when actual pathway content is implemented.
