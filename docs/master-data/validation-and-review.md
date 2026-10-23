# Master-data validation, review and acceptance

The independent master validator reads the frozen schema and validates **every generated row**, not a fixture projection. It imports no generator, pipeline or generation arithmetic helper. The standalone inspector additionally verifies configuration/runtime/reference/code locks, exact file inventory, all byte hashes, row counts, checkpoint-to-file content, review content and concurrent manifest stability.

| Check group | Required behavior |
| --- | --- |
| Structure and keys | Exact full-schema columns; required/null/type/scale/discriminator checks; unique PK/natural/source-version keys; all nonnull FKs resolve |
| Time and identity | Valid half-open business/knowledge rectangles, contiguous revision numbers, no exclusive overlap; source recording/export order; stable MRN/person identity; reserved contacts and adult calendar age |
| Realism | Predeclared age/sex/self-report/language bands; SSA/Census top-100-plus-other total variation ≤0.10; ≥300 given names and ≥1,000 surnames; legitimate name/address collisions; non-deterministic name/demographic relationships |
| Organizations and workforce | Acyclic same-facility physical/financial hierarchies; 72 beds/12 ICU and 24/4 per hospital; role/home/credential/employment/FTE/cost checks; temporal manager resolution and cycle rejection |
| Coverage, access and crosswalks | Continuous exclusive primary coverage; valid product intervals and explicit self-pay; typed scopes/targets; revoked or ineligible worker reads denied by consumer probes; exact namespace/time mapping with no fuzzy fallback |
| Reference and opening health | Exact approved release/local attributes; typed medication ingredient and unit/pack conversion; account semantics; pre-window onset/knowledge, valid problem/allergy types, no encounter fabrication |
| As-of and budgets | Intended old/new versions resolved at knowledge/effective boundaries; all 78,922 rows counted, including 13,000 opening assertions; no extra master/hidden nested fact tables |

The validator produces affected keys/reasons, profiles, scoped observed counts and critical defects. The acceptance runner requires all check groups, a passing test suite with no skips, unchanged frozen design hashes, independent inspection and the recorded matching identity review. It automatically blocks on an unexpected validation error or critical finding.

## Stratified human-readable review

The [sample](../../reviews/master-data-identity-sample.md) contains 100 stable patient identities and 50 stable worker identities. Selection spans all five age groups, all administrative-sex/self-report/language states, changed/unchanged patient histories, all eight worker roles, all three employers/types, later hires and former staff. The sample is deliberately small review evidence, not an additional population. Its 150 copied rows/bytes are reported separately from canonical counts.

Codex read the entire sample and recorded the [review disposition](../../reviews/master-data-realism-review.json), including naming/age plausibility, source attributes, variation, contacts/geography and workforce context. This is a user-authorized technical/synthetic-data review, not an independent clinician's endorsement. The review is bound to the exact sample hash. Changed seed, names, costs or other visible review content requires a fresh matching review; a previous approval cannot silently accept a new sample.

The full-data checks, not the visual sample alone, establish relationship and history correctness. Multiple-seed tests verify variation while keeping hard rules and realism bands. Source naming tests show that a surname/display-format change preserves MRN/employee identity and mapping. Counterexamples retain legitimate surnames such as `Sample`; deliberate numbered/unknown names are rejected. Tests also reject orphan references, wrong types/units/ingredients, overlapping histories, invalid code releases, manager cycles, eligibility errors and fabricated opening encounters.

## Rebuild and recovery evidence

Two clean builds reproduce every canonical file hash and stage checksum; cached resume preserves them. A real subprocess crash before coverage checkpoint commit is rolled back, then resumes without duplicate people/enrollments. A changed workforce configuration invalidates workforce/security/mappings/validation before recomputation, retaining unrelated organizations/patients/coverage. The existing framework suite continues to test every original stage's rollback, corrupt checkpoints, budgets, clocks and fault detectors.

The [execution report](../../evidence/master-data/validation-report.json) records actual tests, input locks, file hashes, counts, independent findings and review hash. The [gate](../../evidence/master-data/acceptance-gate.json) maps each Phase 2 exit criterion to evidence. Frozen Phase 0 contracts and prior evidence remain unchanged; new execution evidence is stored under descriptive paths.

## Scope limits

Full-schema master validation does not certify the unfinished clinical/operations/financial facts. For example, organization checks establish the bed inventory, while opening bed-event states are still a later requirement. Coverage is complete for this master population, while charge-to-claim-to-GL reconciliation still requires future generators. The 55 frozen release-rule definitions are not relabeled as fully executed on a final release.

The candidate currently has 11 generated business tables because other facts do not exist yet. The final 20–25-table/one-to-two-million-row requirement applies to the accepted complete release; empty fake tables or filler facts are not created to satisfy that condition prematurely. The planned complete schema stays at 25 tables and 1,958,210 records. `full_dataset_accepted=false` and `BLOCKED_FOR_SOLUTION` persist after master-data acceptance. Phase 3 remains unstarted.
