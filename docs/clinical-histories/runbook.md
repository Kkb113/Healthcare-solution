# Clinical generation runbook

Use the pinned CPython 3.10.10 and tzdata 2025.2 runtime. No cloud credentials or new package dependencies are needed. All commands run from the repository root.

If the accepted master candidate is absent in a fresh checkout, restore the exact accepted version first:

```powershell
python scripts/restore_master_snapshot.py
```

This reads the accepted commit's Git objects, extracts trusted versioned source into an ignored temporary workspace, runs that revision's master generator, verifies the accepted business hash and copies the candidate into output/master-foundation. It refuses to overwrite a destination. Existing master candidates are used directly. Git history must include f7d512673e21f032065774b8afcde6800df28f72; a shallow clone needs that commit fetched before restoration. The historical master report's code lock describes the historical generator, not the current clinical source tree.

```powershell
python scripts/generate_clinical_histories.py
python scripts/validate_clinical_data.py --report output/clinical-histories/independent-validation.json
python scripts/validate_clinical_foundation.py
```

The first command returns REVIEW_PENDING (exit 2) until the selected journey sample has a matching reviewed decision. It writes canonical JSONL, transactional checkpoints, a manifest, full clinical check results and the 100-journey review package under ignored output/clinical-histories. Review the complete sample and bound structured evidence, record scope/findings/hashes in reviews/clinical-journey-review.json, then rerun. The user has designated Codex as the synthetic domain reviewer; this must never be represented as licensed clinician approval. A stale or missing review prevents candidate-ready.json.

The read-only inspector recalculates canonical hashes, exact schema, source anchor, checkpoint equivalence, clinical invariants and review binding. It never repairs data. The final command includes all historical tests, frozen-contract regression, current clinical checks, clean full-cohort rebuild, cache reuse, real crash recovery and independent inspection. The gate succeeds only when every required exit criterion passes with no skipped tests. Evidence lives under evidence/clinical-histories; earlier phase evidence is retained unchanged.

For manual recovery exercises, use a new ignored directory:

```powershell
python scripts/generate_clinical_histories.py --output output/clinical-recovery --fail-stage appointments
python scripts/generate_clinical_histories.py --output output/clinical-recovery
python scripts/generate_clinical_histories.py --output output/clinical-crash --crash-stage validation
python scripts/generate_clinical_histories.py --output output/clinical-crash
```

Success returns 0; ordinary execution failure returns 1; a data/review block returns 2; the deliberate process crash returns 97. A resumed stage is not rerun just to activate a fault hook. One OS writer lock and atomic SQLite stage commits prevent concurrent publication and partially committed histories. Input changes invalidate descendants before recomputation. A corrupt checkpoint fails closed and should be retained for investigation; rebuild into a new directory. An incomplete/failed manifest or missing ready marker prohibits consuming stale files left by a previous attempt.

The seven stages are accepted_master, journeys, appointments, care_springfield, care_peoria, care_rockford and validation. The care stages are separated by actual hospital identity. Clinical seed/pathway changes preserve the accepted master snapshot and invalidate clinical descendants. Code/reference changes conservatively invalidate the whole profile. A review-only change recomputes validation without changing business rows. Exact per-file hashes and the aggregate business hash must match a clean rebuild.

Normal physical row accounting is canonical rows plus the same rows in SQLite plus the explicitly rendered journey mirror. The committed review-document copy is an additional review mirror; it is not canonical data. Raw checkpoint files and generated business datasets stay ignored. Do not add full JSONL, SQLite, temporary source archives or public downloads to Git.

Phase 3 completion makes patient-flow and bed simulation eligible when requested. It does not authorize solution development or declare capacity, staffing, stock, claims, financial or source-delivery reconciliation complete.
