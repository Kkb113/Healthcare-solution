# Phase 1 runbook

Run from the repository root. The execution lock intentionally requires **CPython 3.10.10** and **tzdata 2025.2**. `requirements-phase1.txt` is the runtime dependency list; the installed environment used for the evidence already has this version. To prepare another environment:

```powershell
python --version
python -m pip install -r requirements-phase1.txt
```

The CLI imports the package from `src/`; no editable installation, Java, Spark, Databricks workspace or cloud credential is needed. A different interpreter/version requires an intentional runtime-lock review and new rebuild evidence, not bypassing the lock.

## Reproduce the complete Phase 1 exit gate

```powershell
python scripts/validate_phase1.py
```

This runs the unchanged Phase 0 artifact check and all design checks, every Phase 0/1 test, two independent clean fixture builds, a cached resume, and read-only independent inspection. It writes [validation-report.json](../../evidence/phase-1/validation-report.json) and [gate.json](../../evidence/phase-1/gate.json). Nonzero exit blocks the phase. A run exception also exits nonzero; previous evidence must not be treated as a new successful evaluation.

The test suite uses temporary directories under ignored `output/` and removes them on completion. Normal outputs and SQLite databases are never committed. To run tests without rewriting evidence:

```powershell
python -m unittest discover -s tests -v
python scripts/build_phase0_spec.py --check
python scripts/validate_phase0.py
```

Keep the Phase 0 historical report intact; the Phase 1 report embeds fresh Phase 0 regression results.

## Inspect a development candidate

```powershell
python scripts/run_phase1.py --output output/phase1-development
python scripts/validate_phase1_candidate.py --run-dir output/phase1-development --report output/phase1-development/independent-validation.json
```

Rerun the first command with identical inputs to reuse all eight stages. The independent command uses only the validation module, Python CSV/hash/date/decimal utilities, and a read-only SQLite connection. It does not call the generator, its serializer/parser or its money/temporal helpers. It verifies the artifact and input locks before recalculating the small fixture's expected behavior.

| Output | Meaning |
| --- | --- |
| `manifest.json` | Input locks, attempts' current status, invalidated/executed/reused stages, business hash/count and mirror counts |
| `checkpoints.sqlite3` with optional WAL/SHM companions | Atomic stage checkpoints, run attempts and defect state; let SQLite manage its companion files |
| `fixture-tables.json` | The 30 scalar development rows; explicitly projected, not full Phase 0 records |
| `validation.json` | 193 expected-pass check results, intended-detector evidence, source recovery, profiles, observed/expected reconciliation and fixture gate |
| `independent-validation.json` | Optional independent artifact/projection inspection report |

Generator exit codes: `0` means `FIXTURES_PASSED`, `2` means validation `BLOCKED`, and `1` means execution failed. The deliberate crash hook exits `97`. Independent inspection returns `0` only for passing fixture inspection and `2` for a block or inspection error. None of these commands can set `DATA_ACCEPTED`.

## Exercise recovery and changes

Use a fresh run directory to trigger a failure hook; a cached stage does not execute its hook.

```powershell
python scripts/run_phase1.py --output output/phase1-exception --fail-stage billing
python scripts/run_phase1.py --output output/phase1-exception
python scripts/run_phase1.py --output output/phase1-crash --crash-stage billing
python scripts/run_phase1.py --output output/phase1-crash
```

The first/third commands intentionally fail. The following command resumes the same input, reuses committed ancestors and reproduces the clean hash. Do not manually copy or edit checkpoint payloads. For detected corruption, keep the directory as evidence and rebuild into another ignored output directory.

For assumption changes, copy `config/phase1-development.json` into an ignored output directory, change one declared stage assumption and run with `--config` pointing to the copy. A demand change invalidates demand/resources/billing/serialization/faults/validation while retaining identities and clinical configuration. An expectation-only change invalidates validation. A changed seed invalidates all stages but stable IDs stay connected. Incorrect expected totals or units cause a block with record keys and reasons.

Changing the fixture cap to `29` demonstrates aggregate budget enforcement: the billing stage would take the candidate to 30 rows, so its output is rejected before commit. Changing it to `1` blocks the first stage. Raising the cap over 500 or selecting a full-release profile is rejected at configuration load.

Source replay retains historical knowledge and rejects future availability. Exact deliveries are deduplicated; Axiom revisions require same-scope replacement lineage. Quarantined files do not partially apply. `Replay.recover` revalidates the repaired delivery and records the repair linkage before resolving quarantine; unresolved quarantine or missing partitions blocks source certification. ADT projection handles late messages and correction chains in effective order, including rejection of missing/cyclic predecessors.

## Next authorized boundary

A passing Phase 1 gate makes Phase 2 eligible to start when requested. It does not start it automatically. Phase 2 must replace miniature identity/reference inputs with reviewed realistic population/reference generation, use the full schema, and expand independent data validation. The remaining phases must complete clinical, operational, financial, source and release evidence before solution development.
