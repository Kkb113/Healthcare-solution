# Healthcare synthetic data foundation

Phases 0-2 establish the data foundation for a fictional US healthcare group on Azure Databricks. Microsoft Fabric is excluded. The deterministic framework now generates and validates realistic full-schema master data. No full healthcare dataset is accepted and no cloud deployment, forecasting model, dashboard, or AI agent has been built.

The finalized baseline contains **25 business tables and 1,958,210 planned records** across **2023-2025**, with **41,790 records of headroom** below the two-million ceiling. Three fictional Illinois community hospitals have 72 inpatient beds in total. This replaces the earlier provisional 300-bed scale so the budget includes clinical detail and historical revisions.

Start with the [frozen baseline](docs/phase-0/README.md), [framework](docs/phase-1/README.md), [master-data foundation](docs/master-data/README.md), and [implementation plan](synthetic-data-generation-implementation.md). Phase 2 completion makes **Phase 3** eligible to start when requested. The analytics solution stays blocked until final Phase 9 data acceptance.

## Generate and validate the master-data foundation

```powershell
python scripts/validate_master_foundation.py
python scripts/generate_master_data.py --output output/master-foundation
python scripts/validate_master_data.py --output output/master-foundation
```

The candidate contains **78,922 full-schema rows**: 20,000 stable patients, 300 stable workers, organizations/72 beds, payer/coverage/security histories, source mappings, 3,000 catalog entries and 13,000 opening health assertions. All rows fit within the existing budget; **1,879,288 planned rows remain** for later work. The candidate currently has 11 generated business tables; the complete release retains the frozen 25-table schema. It is not final data acceptance.

See the [master-data gate](evidence/master-data/acceptance-gate.json), [validation evidence](evidence/master-data/validation-report.json), [reviewed 100-patient/50-worker sample](reviews/master-data-identity-sample.md), and [runbook](docs/master-data/runbook.md). Public aggregate references are pinned and generation runs offline. Generated datasets remain under ignored output paths; only selected review/evidence artifacts are versioned. New filenames follow the [repository naming conventions](CONTRIBUTING.md).

## Run the Phase 1 framework and gate

Use CPython 3.10.10 and `tzdata==2025.2`, pinned by the runtime contract. The existing test environment already contains both.

```powershell
python -m pip install -r requirements-phase1.txt
python scripts/validate_phase1.py
python scripts/run_phase1.py --output output/phase1-development
python scripts/validate_phase1_candidate.py --run-dir output/phase1-development
```

The gate runs Phase 0 regression, the complete test suite, clean rebuild/resume checks and independent read-only inspection. See [Phase 1 exit evidence](evidence/phase-1/gate.json). Normal generation produces **30 development rows across 15 declared scalar projections** and **3 Workday/Axiom mirror rows**, never a full business dataset. The [runbook](docs/phase-1/runbook.md) explains recovery, invalidation, quotas and output semantics.

## Reviewable artifacts

- [Scope, decisions and dependency graph](docs/phase-0/scope-and-decisions.md)
- [Relationships and analytical grains](docs/phase-0/relationships.md)
- [Field-level data dictionary](docs/phase-0/data-dictionary.md)
- [Business, clinical and accounting rules](docs/phase-0/business-rules.md)
- [Three-year record budget and capacity arithmetic](docs/phase-0/record-budget.md)
- [Source contracts and historical availability](docs/phase-0/source-contracts.md)
- [Realism assumptions and acceptance criteria](docs/phase-0/realism-and-validation.md)
- [Design review and phase gate](docs/phase-0/review-and-gate.md)
- [Machine-readable contracts](contracts/phase0/)
- [Validation evidence](evidence/phase-0/validation-report.json)

## Reproduce the design checks

Python 3.10+ and its standard library are sufficient. Run from the repository root:

```powershell
python scripts/build_phase0_spec.py --check
python scripts/validate_phase0.py --report evidence/phase-0/validation-report.json
python -m unittest discover -s tests -v
```

`scripts/build_phase0_spec.py` is the versioned authoring source for the declarative contracts and generated dictionary/DDL. After an intentional specification change, run it without `--check`, review every generated change, rerun validation/tests, and reopen affected review gates. It never generates healthcare records. `databricks-schema.sql` is an offline schema template, not an executed migration.

The design validator checks schema integrity and feasibility arithmetic. The 55 data-quality rules are **specified**, not claimed to have run on nonexistent data. All actual data-quality, clinical, statistical, and reconciliation evidence is still required in later phases.

## Repository policy

Commit each completed phase with its evidence and push to `https://github.com/Kkb113/Healthcare-solution.git`. Never commit credentials, live patient data, or generated datasets by accident; generated business data belongs in a separately manifested release location. A source export mirror is counted separately from canonical business rows in that release manifest.
