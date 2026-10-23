# Healthcare synthetic data foundation

Phase 0 defines the data foundation for a fictional US healthcare group on Azure Databricks. Microsoft Fabric is excluded. No patient dataset, generator, cloud deployment, forecasting model, dashboard, or AI agent has been built.

The finalized baseline contains **25 business tables and 1,958,210 planned records** across **2023-2025**, with **41,790 records of headroom** below the two-million ceiling. Three fictional Illinois community hospitals have 72 inpatient beds in total. This replaces the earlier provisional 300-bed scale so the budget includes clinical detail and historical revisions.

Start with the [Phase 0 baseline](docs/phase-0/README.md), then the [implementation plan](synthetic-data-generation-implementation.md). Phase 0 completion permits **Phase 1 data-generation framework work only**. The analytics solution stays blocked until final Phase 9 data acceptance.

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
