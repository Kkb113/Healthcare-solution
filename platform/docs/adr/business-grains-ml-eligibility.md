# Business grains and predictive eligibility

**ADR-14 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review for synthetic POC.

**Context:** Outcomes/business timestamps do not establish pre-outcome availability. The accepted5.5base-HPPD/acuity/minimumcoverage rules and sparse cohorts cannot support arbitrary learned workforce/annual forecasts.

**Decision:** Freeze42KPI definitions and16factgrains, twentyindependentreferencechecks, selected-run PATIENT/NONPATIENT cents conservation. Publish13modeldispositions. M4remainingLOSconditionalfirsteligible>=admission+1h45; M5hourlyceiling; M10firstvisiblependingbeforefirstadjudication; M12firstvisibledischarge residualwindow; M11retrospective-only.

**Alternatives considered:** Patient×procedure cost claims; admission/submission-instant risk; unavailable booked electives/readiness; future realized weather or finance vintages.

**Consequences and acceptance:** M1–M12 train2023–24/selectJan–Jun2025/lockedJul–Dec2025; M13pre2025selection/all2025holdout. Labelavailabilitypurge/censor/supportthresholds, ECE<=.05/80%coverage75–85%, baselinechampions/insufficientdata honest.

**Contract:** [ml-eligibility.json](../../contracts/architecture/ml-eligibility.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
