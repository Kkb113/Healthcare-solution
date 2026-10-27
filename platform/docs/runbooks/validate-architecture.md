# Validate or revise the architecture baseline

Run from the repository root. Phase numbers belong inside artifacts, not new filenames. These commands validate Phase 0 design and immutable release binding; they do not deploy analytics or run paid probes.

```powershell
platform/.venv/Scripts/ruff.exe check platform/scripts platform/tests
platform/.venv/Scripts/ruff.exe format --check platform/scripts platform/tests
platform/.venv/Scripts/python.exe -B platform/scripts/verify_configuration.py
$testRoot = Join-Path (Resolve-Path output/platform-architecture) ('tests-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $testRoot) { throw 'Test directory must be new' }
platform/.venv/Scripts/python.exe -B -m pytest platform/tests/unit/test_architecture_contracts.py -q -p no:cacheprovider --basetemp $testRoot --junitxml output/platform-architecture/architecture-tests.xml
platform/.venv/Scripts/python.exe -B platform/scripts/validate_architecture.py --with-release
```

The temporary test path is unique and stays inside ignored workspace output. Linux CI uses the same locked platform dependencies; it validates the committed design and negative cases without downloading the synthetic payload. The full local command additionally recomputes all source matrix bindings and runs release-tool verification over the entire accepted package. Neither local design tests nor the earlier Spark/runtime smoke replaces a tenant capability gate.

The harness rejects missing approval, wrong release, changed approved artifact hashes, incomplete source mappings, cyclic dependencies, checksum-based delivery keys, oracle privilege leakage, unsupported prospective models, overlapping holdouts, missing required probes, duplicate lifecycle owners, reduced mandatory samples, omitted native charges, unsupported Genie scopes, missing search tails, unbacked prices and over-budget workloads. Costs use Decimal arithmetic and round each line upward to paise. FX/tax reserves and unknown usage remain explicit.

Run `validate_architecture.py --proposal` only to review a candidate before approval: its output says `PROPOSAL_VALIDATED_NOT_A_PHASE_PASS`. It cannot produce a passing phase gate. Scope/budget changes require a concrete diff, impact/cost review and explicit owner approval. Technical corrections within delegated authority still need targeted tests and a new source commit/gate. Record the original failed estimate or probe; never rewrite it as a passing attempt.

Price refresh is explicit and does not mutate the baseline automatically:

```powershell
python -B platform/scripts/collect_price_evidence.py databricks
python -B platform/scripts/collect_price_evidence.py storage
python -B platform/scripts/collect_price_evidence.py event-hubs
python -B platform/scripts/collect_price_evidence.py key-vault
python -B platform/scripts/build_price_evidence.py
```

This downloads official paginated Retail API responses to ignored output and selects non-promotional East US rates. Luna rates use the linked official Azure publication while Retail API/model pricing table publishing is pending. Revalidate before a funded window and at least every30days, record current actual invoice FX/tax and any changed tariff, reprice the complete remainder and refresh approval hashes only after the affected review. Do not assume a zero-price POC SKU, free human allowance or credit.

`freeze_source_contracts.py` and `freeze_gate_contracts.py` are explicit baseline-authoring commands, not normal validation. Normal checks recompute and compare in memory so drift fails. Do not regenerate accepted schema/source contracts to conceal a mismatch. Inspect the changed release identity, column/reference/clock semantics, source counts, downstream KPI/model/security effects and rollback/rebuild requirements first.

For a completed gate, commit the reviewed implementation/contracts first, rerun tests at that exact source SHA, then run `write_architecture_gate.py`. It binds reports/artifacts to the committed bytes, records four criteria and delegated sign-off, and refuses dirty source, missing approval, failing tests or an unverified release. Commit/push the evidence afterwards; the source SHA and evidence commit are deliberately distinct to avoid self-referential hashes. Verify with `verify_architecture_gate.py`. Later implementation must consume the passing committed gate, execute all required probes and respect the fourteen-phase dependency contract.

No paid job is needed to check sleep. The Phase 2 controller and later guards use control-plane APIs plus the authoritative ADLS object; unknown state, pending charges or an unresolved required capability blocks admission. Current prerequisites are adopted, not recreated. The previous shared-metastore administrator approval does not authorize new metastore ownership changes.
