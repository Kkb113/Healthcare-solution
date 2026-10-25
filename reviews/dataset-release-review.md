# Synthetic healthcare release decision

Implementation Phase 9. **PASSED: all 16 final criteria; foundation DATA_ACCEPTED.** The [business owner explicitly accepted](dataset-release-acceptance.json) this exact release and its documented limitations after the delegated domain review and all technical checks passed. No analytics solution has started.

Published package: `C:/HealthCare_Solution/data/releases/healthcare-synthetic-v1.0.2`.

- Descriptor SHA256: `755532094c862c12163fabd1e4eff62206046fde8644c1415e5a4d5c80323be4`.
- Limitations SHA256: `63e3a19a3d4c7556ac0d8940826b4df10edaea5a7b40b78e489af008aa671130`.
- Certification SHA256: `21a9d6c09020a601a0befd4ea1514a5aa8ddf4a94c713dbf3f160674f3a19abd`.
- Payload manifest SHA256: `3f42e5d25cf815f3e7e4470c45921cda12946ee41f3294e1c43a60185c7587f8`.

The sealed package contains 7,109 payload files. The [machine-readable review](dataset-release-review.json) and [current gate](../evidence/dataset-release/acceptance-gate.json) bind the evidence to this exact descriptor.

## Dataset scope

The accepted `healthcare-synthetic-v1.0.2` release covers January 2023 through December 2025 for three fictional Illinois adult-care hospitals, with 72 licensed inpatient beds. It contains 25 canonical tables and 1,936,663 canonical records, plus 22 explicitly labeled challenge/control copies: **1,936,685 cap-counted records**. Native snapshots, key dictionaries, derived reports, validation indices and archived release versions are disclosed technical copies, not additional business facts to append to these tables.

The patient population contains 22,000 fictional identities. Names, birthdays, event-specific ages, coverage and repeated care histories are linked consistently. Workforce versions, credentials, schedules, capacity, stock consumption, services, claims and financial histories support the selected capture. No real patient record or individual contact dataset was imported.

## Required evidence

All technical conditions passed: the seven-stage cold rebuild, checksums on every actual release file, all 58 domain-control groups, six independent consumers, eleven point-in-time checks, all realism controls, exact reconstruction and duplicate replay of 3,444 native deliveries, six reports, 318 snapshots, 304 Axiom headers and fifteen fault outcomes. All 70 release tests pass in both the development and shipped offline checkout with zero failures, errors or skips. The current 136-case review binding passes. No unresolved P0/P1 defect or unexplained reconciliation difference remains. The three full-scale seed experiments and 59 integrated tests are retained unchanged evidence, not claimed as newly executed Phase 9 tests.

The cold rebuild uses a fresh isolated venv, pinned dependencies and empty generated-data workspaces on the same Windows host. It imports no earlier generated snapshot or checkpoint. The additional offline check proves source/archive and tool distribution; it does not claim a second complete data rebuild or separate-machine/container certification.

## Scope and limitations to acknowledge

- This is a configured fictional adult hospital cohort. Clinical plausibility does not establish clinical effectiveness, treatment guidance, population epidemiology or reimbursement compliance.
- Thirty selected terminal outcomes exercise late-window boundaries; they are not a mortality forecasting population. Under-65 disability Medicare eligibility is not modeled.
- Selected services, billing, stock, support/admin attendance and costs do not constitute complete hospital activity, payroll or total cost of care. Prices and bundled charges are demonstration assumptions.
- Workday-style and Axiom-style feeds are local simulations. Axiom supplies twelve illustrative layout archetypes; approximately 900 customer layouts and vendor certification are outside the delivered scope.
- The additional seeds vary connected histories against the same fixed fictional catchment. Sparse joint-cell intervals are descriptive; they are not population-inference confidence intervals.
- Open stays, unbilled care, draft claims, pending outcomes, missing plans and zero plans remain distinct. Unknown follow-up must not become a negative label.
- This integrated master-context baseline must not be incrementally mixed with older baseline deliveries. Verify versions and rebuild consumers for this release.
- Publication is local and checksummed. It is not Azure deployment, WORM storage, a security boundary or a production SLA. No analytics solution, model, dashboard, streaming product, agent or live integration is started by data acceptance.

The complete authoritative limitations are in [the release documentation](../docs/dataset-release/limitations.md). Their exact SHA256 is bound above and in the machine-readable review.

## Review authority and release history

The user delegated synthetic domain review and finalization. The [integrated review](integrated-history-review.json) contains 112 patient/financial contexts, 24 named worker contexts and twelve quarterly clinical-note reviews. Fresh Phase 9 validation confirms the selected source facts, profiles and rendered sample bytes remain unchanged in the actual published files. These are delegated synthetic business, clinical, workforce, finance and engineering reviews, with no external professional or vendor endorsement.

Version 1.0.0 passed data checks but failed offline distribution because an unspecified clone branch selected an unborn `master`. It was never business-accepted and is [retired](dataset-release-retirement.json). The 1.0.1 attempt was blocked before staging by the frozen exporter's output-path constraint. The [release issue register](dataset-release-issues.json) preserves both findings. Version 1.0.2 explicitly selects `main`, uses fresh version-specific audit storage and reruns all staged-file checks. These corrections do not change canonical healthcare content. The actual corrected bundle checkout and its 70 tests pass; the issue is closed with hash-bound evidence.

## Final decision

The [implementation plan, Section 9](../synthetic-data-generation-implementation.md#9-final-definition-of-done-and-solution-lock) requires: “The business owner explicitly accepts the data release with the designated domain reviews attached.”

The owner replied **“Accept release and documented limitations”** to the question identifying the exact descriptor and limitations hashes above. The [direct approval](dataset-release-approval.json), [recorded acceptance](dataset-release-acceptance.json) and [passing final gate](../evidence/dataset-release/acceptance-gate.json) preserve that decision. Phase 9 is complete and the foundation is `DATA_ACCEPTED`. Acceptance does not authorize starting the subsequent Azure Databricks solution workstream. The machine-readable domain review preserves its pre-owner-decision scope; the acceptance record is authoritative for final data acceptance.
