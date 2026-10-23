# Healthcare master-data foundation

This package implements Phase 2 of the [implementation plan](../../synthetic-data-generation-implementation.md): realistic identities, organizations, effective-dated coverage, workforce/security history, terminology, source mappings and opening health context. See the [acceptance gate](../../evidence/master-data/acceptance-gate.json) and [execution evidence](../../evidence/master-data/validation-report.json).

The candidate contains **78,922 full-schema canonical records** in 11 currently generated business tables. It represents **20,000 stable patients**, **300 stable workers**, all three hospitals/72 inpatient beds, and every required master domain. The complete release still has the frozen **25-table / 1,958,210-row** plan. The master candidate is a partial data foundation, not the accepted final dataset. Clinical journeys, operational events, financial activity and the Azure Databricks analytics solution have not started.

| Canonical table | Current records | Scope |
| --- | ---: | --- |
| facility | 3 | Fictional Illinois community hospitals |
| cost_center | 45 | Financial responsibility hierarchies |
| location | 150 | Departments, units, rooms and 72 licensed beds |
| patient | 22,000 | 20,000 people plus 2,000 bitemporal history rows |
| worker_assignment | 900 | 300 people, credentials, assignments, costs and history |
| access_scope | 1,800 | Synthetic read-only grants, revisions and revocations |
| payer_plan | 24 | Fictional stable and renewed payer contract versions |
| patient_coverage | 28,000 | Complete primary coverage and 8,000 changes |
| catalog_item | 3,000 | 2,800 official dated ICD rows and 200 local references |
| source_key_map | 10,000 | Typed source aliases and effective financial associations |
| clinical_condition | 13,000 | Opening problems/allergies only; no encounter diagnoses |
| **Total** | **78,922** | **All versions and opening context count** |

The 13,000 condition rows consume part of the existing 95,000-row `clinical_condition` budget, leaving 82,000 there. The overall planned remainder is **1,879,288 rows**, with the original **41,790-row reserve** below two million intact. Later generators must extend this candidate and reconcile these rows, not generate duplicate master or opening-condition populations.

Read the [generation design](generation-design.md), [reference provenance](reference-provenance.md), [validation and review](validation-and-review.md), and [runbook](runbook.md). The [reviewed identity sample](../../reviews/master-data-identity-sample.md) is a deliberate 150-row review mirror; the [recorded review](../../reviews/master-data-realism-review.json) is bound to its content hash.

New artifacts use descriptive filenames under `docs/master-data`, `evidence/master-data`, `references`, `reviews` and `config`, following the user's naming preference. Phase numbers appear only in artifact content. Microsoft Fabric is excluded; no cloud resources or solution components are deployed.
