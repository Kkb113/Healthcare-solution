# Healthcare synthetic data foundation

Phases 0-5 are complete for their defined data-foundation scopes for a fictional US healthcare group on Azure Databricks. Microsoft Fabric is excluded. The deterministic framework produces full-schema master data, longitudinal clinical histories, capacity-integrated operations, workforce attendance and selected resource/inventory histories. Phase 5 passes all four exit criteria with **238 tests**, **31 clinical/operational/workforce/stock check groups**, independent persisted-file inspection and a recorded 100-case resource review. The full healthcare dataset and analytics solution remain blocked until final Phase 9 data acceptance.

The finalized baseline contains **25 business tables and 1,958,210 planned records** across **2023-2025**, with **41,790 records of headroom** below the two-million ceiling. Three fictional Illinois community hospitals have 72 inpatient beds in total. This replaces the earlier provisional 300-bed scale so the budget includes clinical detail and historical revisions.

Start with the [frozen baseline](docs/phase-0/README.md), [framework](docs/phase-1/README.md), [master-data foundation](docs/master-data/README.md), and [implementation plan](synthetic-data-generation-implementation.md). The [clinical foundation](docs/clinical-histories/README.md) implements Phase 3; its current acceptance status is recorded in the [clinical exit gate](evidence/clinical-histories/acceptance-gate.json). The analytics solution stays blocked until final Phase 9 data acceptance.

## Connected workforce and inventory data

The [resource foundation](docs/resource-foundation/README.md) implements Phase 5 and passes all four [exit criteria](evidence/resource-foundation/acceptance-gate.json). Its three-year candidate contains **1,053,661 canonical rows across 18 populated business tables**, including **66,582 staff-shift versions**, **47,839 inventory movements** and **561,909 clinical events**. All fifteen unchanged parent tables, including encounter/attending and bed histories, remain byte-identical. Actual operative timing, qualified source authors and clinical stock links are integrated and independently revalidated.

The [generation design](docs/resource-foundation/generation-design.md) states workload, historical-knowledge, rate/OT, lot/expiry, quantity and valuation rules. Source costs reconcile without unexplained negative stock or balancing plugs. Thirty operating-unit stockout and thirty circulating-RN absence windows have connected service effects. Selected capture is explicit: this is not complete payroll, all materials or an entire operative/anesthetic team. Financial postings, Axiom scenarios and native source release replay remain later data-foundation phases.

```powershell
# Restore missing immutable inputs only; preserve existing accepted snapshots.
if (-not (Test-Path output/master-foundation/manifest.json)) {
    python scripts/restore_master_snapshot.py
}
if (-not (Test-Path output/clinical-histories/manifest.json)) {
    python scripts/restore_clinical_snapshot.py
}
if (-not (Test-Path output/operational-flow/manifest.json)) {
    python scripts/restore_operational_snapshot.py
}
python scripts/generate_resource_foundation.py
python scripts/validate_resource_data.py --report output/resource-foundation/independent-inspection.json
python scripts/validate_resource_foundation.py
```

See the [runbook](docs/resource-foundation/runbook.md), [complete validation evidence](evidence/resource-foundation/validation-report.json), [review decision](reviews/resource-foundation-review.json) and [named case sample](reviews/resource-foundation-sample.md). The acceptance command runs current framework/master, operational and resource tests plus the exact accepted historical clinical tests, with strict source/configuration/review locks and no skipped tests. Phase 6 has not started.

## Capacity-integrated operational data

The [operational foundation](docs/operational-flow/README.md) implements the Phase 4 data scope. Its [acceptance gate](evidence/operational-flow/acceptance-gate.json) passes all four exit criteria. The three-year candidate contains **938,452 canonical records across 16 populated business tables**, including 71,018 immutable bed events. Event-state and independent interval oracles reconcile at all 25,245 census boundaries with zero unexplained differences. The final schema remains 25 tables with 1,958,210 planned records; the 41,790-record reserve is untouched.

```powershell
# Restore only missing immutable parent snapshots.
if (-not (Test-Path output/master-foundation/manifest.json)) {
    python scripts/restore_master_snapshot.py
}
if (-not (Test-Path output/clinical-histories/manifest.json)) {
    python scripts/restore_clinical_snapshot.py
}
python scripts/generate_operational_flow.py
python scripts/validate_operational_data.py
python scripts/validate_operational_foundation.py
```

Existing accepted parents must be preserved. Historical standalone generators bind their committed source versions; use the restoration wrappers rather than regenerating an accepted parent in place from later code. The [runbook](docs/operational-flow/runbook.md) explains exact-history regression checks, current-code tests and local derived-state queries. No analytics solution is authorized by this phase gate.

## Historical longitudinal clinical workflow

Phase 3 evidence is retained against its accepted source commit. To reproduce that accepted data on a later checkout, use `restore_clinical_snapshot.py`. For complete historical clinical regressions, the operational exit gate runs every accepted clinical test against its exact archived generator and the unchanged accepted snapshot. Avoid running a newer standalone generator over that accepted parent directory.

The [clinical foundation](docs/clinical-histories/README.md) implements linked adult visits, conditions, selected orders/results/treatment courses, operative documentation and fact-grounded notes. Its 58,000 encounter contexts cover the three-year cohort and opening-only contexts, within the unchanged 25-table release schema and existing record envelopes. The clinical candidate contains **840,061 canonical rows across 14 populated business tables**, including 58,000 encounter contexts. The accepted master snapshot is preserved exactly. The current operational acceptance command prepares the operational candidate and evaluates current framework/master and operational tests together with the version-bound historical clinical suite.

Preserve the accepted historical master snapshot. Running a current master generator into that same directory changes its provenance identifiers; use a different output directory for master experiments. The restoration command reproduces the original accepted snapshot from its exact Git revision. It refuses to overwrite an existing destination.

Clinical timings and outcomes remain provisional until resource integration. Full dataset acceptance and solution development remain blocked. See the [clinical gate](evidence/clinical-histories/acceptance-gate.json), [100-journey review](reviews/clinical-journey-sample.md), and [runbook](docs/clinical-histories/runbook.md).


## Optional master-profile experiments

```powershell
python scripts/generate_master_data.py --output output/master-preview
python scripts/validate_master_data.py --output output/master-preview
# Run after preparing the clinical candidate; preserve accepted historical evidence.
python scripts/validate_master_foundation.py --output output/master-preview --report output/master-validation-report.json --gate output/master-acceptance-gate.json
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

The historical framework gate records its original regression and fixture scope. Use the resource acceptance command above for the complete current and version-bound historical regression assessment. See [Phase 1 exit evidence](evidence/phase-1/gate.json). Normal generation produces **30 development rows across 15 declared scalar projections** and **3 Workday/Axiom mirror rows**, never a full business dataset. The [runbook](docs/phase-1/runbook.md) explains recovery, invalidation, quotas and output semantics.

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
python -m unittest discover -s tests -p test_phase0_contracts.py -v
```

`scripts/build_phase0_spec.py` is the versioned authoring source for the declarative contracts and generated dictionary/DDL. After an intentional specification change, run it without `--check`, review every generated change, rerun validation/tests, and reopen affected review gates. It never generates healthcare records. `databricks-schema.sql` is an offline schema template, not an executed migration.

The design validator checks schema integrity and feasibility arithmetic. The 55 data-quality rules are **specified**, not claimed to have run on nonexistent data. All actual data-quality, clinical, statistical, and reconciliation evidence is still required in later phases.

## Repository policy

Commit each completed phase with its evidence and push to `https://github.com/Kkb113/Healthcare-solution.git`. Never commit credentials, live patient data, or generated datasets by accident; generated business data belongs in a separately manifested release location. A source export mirror is counted separately from canonical business rows in that release manifest.
