# Candidate contract and dependency correction

## Scope and immutability

Business activity covers January 2023 through December 2025 in America/Chicago, with source closing grace through January 10, 2026. All 36 months, three fictional US hospitals, and IPD/ED/OPD service classes must be represented. The accepted 72-bed capacity, identities, vocabulary, worker histories and public name references remain the catchment context.

The primary seed reuses accepted resource histories after verifying every actual file checksum, inventory and row count. All original 3,000 catalog items remain; five existing local facility billing codes are regenerated. The reviewed master-context migration below intentionally corrects coverage assignments and worker birthdays while preserving their identities and intervals. Comparisons use the same identities and reference context but regenerate complete calendar-conditioned demand, transfer/placement events, care, operative coordination, workforce, stock and finance. All three experiments run at full scale, exceeding the representative-scale requirement. The experiments are separate candidates, not appended copies of the release. No months are tiled, no patient journeys duplicated to scale, and no histories truncated to meet a quota.

## Correct the denial calibration

The original frozen realism target requires an 8-12% initial full/partial denial share among current-period original insured claims with observed first adjudication. The earlier financial configuration used a 450-basis-point base probability and produced 2,296/46,525 = 4.93498%. The Phase 8 integrated assessment found this mismatch; prior structural/accounting acceptance did not demonstrate that statistical requirement.

The integrated configuration changes the base probability to 900 basis points, retaining the same conditional authorization rules, pending-authorization probability, original account identity, patient-statement exclusion, observation/censoring and line-level denial logic. It does not change the target. Claim events, journals, allocations, actuals, plans, native exports, review summaries and current validation evidence must be regenerated. Baseline accepted artifacts are preserved for audit.

The new candidate's producer fingerprint includes source implementation, generation configurations, all contracts and the accepted resource gate. Each checkpoint records its complete preceding-stage fingerprints. Changed inputs invalidate descendants; a candidate-ready marker is removed before generation/export/evaluation. Review binds actual selected facts and current profiles. An old review cannot approve changed facts.

## Correct coverage and worker context

The first integrated profile found Medicare at 22.47% and Medicaid at 22.30%, outside the frozen encounter-level targets of 35% and 15% with five-percentage-point tolerances. Original renewal histories excluded Medicare, and generic plan-change choices further diluted eligible senior enrollment. The revised prospective weights apply to every enrollment: under age 65 uses 64% Commercial, 24% Medicaid and 12% Self Pay; age 65 and above uses 95% Medicare, 4% Commercial and 1% Self Pay. No under-65 Medicare disability population is invented. Original compatible plan products are retained; otherwise selection uses an existing valid stable product. Enrollment/knowledge intervals, coverage identities and row counts are preserved. The rule uses only age at enrollment and stable keyed draws, never future utilization or payment outcomes.

The original workforce context contained 282 June-15 and 18 January-15 birthday imputations. The migration preserves each worker's birth year and varies calendar-valid month/day consistently across all assignment versions. Names, credentials, manager relationships, rates, hours and source knowledge dates remain coherent. The bounded review includes all eight workforce roles at all three facilities.

This is a new synthetic dataset baseline, `integrated-master-context-v1`. Earlier accepted files are never edited. Old/new baseline source deliveries must not be incrementally merged by immutable source-version ID: rebuild the consumer for the new baseline. Whitelisted field-difference tests permit only the explicitly amended coverage fields, worker birthday and generation provenance; other accepted clinical/resource facts retain exact bytes.

A patient aged 100 at opening can reach 103 during the three-year window. These valid ages are disclosed in a separate 101–103 profile cell, not capped, silently excluded or labeled invalid. Frozen 80–100 target comparisons retain their original definition.

## Record budget and physical copies

The amended planned envelope stays **1,995,215 canonical rows plus 4,785 reserve rows**. Reassign 20,000 unused slots to claim history: `clinical_event` becomes 570,000; `clinical_condition` 82,000; `inventory_movement` 50,000; `cost_allocation` 163,000; and `claim_event` 240,000. The reductions total 20,000 and preserve complete histories within their actual per-table envelopes. All other reviewed financial allowances remain unchanged. This is an explicit versioned amendment, not an edit of frozen Phase 0 design files.

The primary integrated candidate count is bound by the current acceptance gate after regeneration across all 25 business tables. Native challenge/control copies remain bounded by 64 reserve slots. Challenge copies are added conservatively to the cap-counted release total. Source mirrors, typed mapping dictionaries, derived report cells, SQLite indices, checkpoint payloads, resource-context mirrors, review summaries and comparison experiments are disclosed separately. They do not represent additional canonical business facts and must never be summed with canonical tables.

The resource context is file-backed because a whole serialized resource snapshot exceeds SQLite's single-cell string limit. Its checkpoint stores the complete file-map digest; loading a cached context recomputes actual hashes and counts. File-backed context rows are explicit mirrors, not hidden facts.

Only the accepted primary seed may proceed to Phase 9 publication. Phase 8 candidates are not immutable certified releases, and no final data-acceptance marker is emitted.
