# Integrated candidate runbook

Use pinned CPython 3.10.10 and tzdata 2025.2. Run commands from the repository root, with accepted parent snapshots restored as described in earlier runbooks. Public reference packages are pinned local inputs; generation does not fetch individual records or connect to live systems.

Run heavy generation/inspection/rebuild jobs sequentially. Generated candidates, context copies, dictionaries, indices, experiments and source payloads stay under ignored output paths.

```powershell
python scripts/run_integrated_regressions.py --small-only
python scripts/generate_integrated_history.py
python scripts/inspect_integrated_history.py
python scripts/generate_integrated_history.py --seed 20261024 --output output/integrated-comparison-20261024
python scripts/inspect_integrated_history.py --candidate output/integrated-comparison-20261024 --output output/integrated-comparison-20261024/validation
python scripts/generate_integrated_history.py --seed 20261025 --output output/integrated-comparison-20261025
python scripts/inspect_integrated_history.py --candidate output/integrated-comparison-20261025 --output output/integrated-comparison-20261025/validation
python scripts/export_integrated_sources.py
python scripts/review_integrated_history.py
```

Read the recorded sample, full population profiles, controls and issues. Record the delegated synthetic-domain review with current sample/fact/profile checksums and explicit limitations. The renderer never creates an approval by itself. The review decision is conditional on passing all technical gates.

After finalizing code, configuration, contracts, review and documentation, run the complete integrated tests. They intentionally build disposable candidates/exports and a durable replay index, so they take substantially longer than small-fixture checks.

```powershell
python scripts/run_integrated_regressions.py
python scripts/validate_integrated_foundation.py
```

The gate writes `evidence/integrated-history/acceptance-gate.json`, its validation report and an ignored candidate-ready marker only if every Phase 8 exit passes. Any failed gate removes readiness and reports BLOCKED. It leaves `full_dataset_accepted=false` and `solution_status=BLOCKED_FOR_SOLUTION`.

For recovery experiments, `--crash-stage` ends the actual generator with exit 97 before committing that stage. `--fail-stage` raises a precommit exception. Native exports have `--fail-table` and `--crash-table`. Do not run these against accepted parent output folders. Use a new disposable directory, resume without the fault flag, and compare actual business/source digests.

Source retries verify existing file bytes; corruption fails closed rather than silently trusting a checkpoint. A changed schema/assumption requires regeneration, fresh inspection, regenerated review and new complete tests. Do not hand-edit a manifest to force acceptance. Phase 9 remains a separate authorized task.
