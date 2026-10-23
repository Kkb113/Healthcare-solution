# Financial foundation runbook

Run commands from the repository with CPython 3.10.10 and the existing pinned dependencies. Business data/checkpoints remain ignored.

```powershell
# Restore only missing accepted parents, using their exact accepted Git revisions.
if (-not (Test-Path output/master-foundation/manifest.json)) { python scripts/restore_master_snapshot.py }
if (-not (Test-Path output/clinical-histories/manifest.json)) { python scripts/restore_clinical_snapshot.py }
if (-not (Test-Path output/operational-flow/manifest.json)) { python scripts/restore_operational_snapshot.py }
if (-not (Test-Path output/resource-foundation/manifest.json)) { python scripts/restore_resource_snapshot.py }
python scripts/generate_financial_history.py
python scripts/validate_financial_data.py --report output/financial-history/independent-inspection.json
python scripts/validate_financial_foundation.py
```

Generation initially returns REVIEW_PENDING when the content-bound reviewer decision is absent/stale; it does not publish readiness. Read all selected traces, record actual findings and bind their exact sample/fact hashes in `reviews/financial-history-review.json`. Re-run generation to evaluate the review. Never manufacture another stakeholder's approval. Codex performs the user-designated synthetic finance review under this chat's explicit delegation, without claiming independent accountant/clinical endorsement.

The final gate evaluates frozen design checks, independent persisted controls and five regression groups. The clinical group uses exact accepted historical source rather than forcing newer files into an old source-bound snapshot. Current framework/master, operations, resources and finance are separately tested. Passing test evidence can be reused only when complete before/after source, configuration, contract and review hashes match; financial results also bind the candidate business hash. Failures/skips do not pass.

```powershell
python scripts/query_financial_history.py claims
python scripts/query_financial_history.py costs
python scripts/query_financial_history.py monthly --month 2025-12-01 --known 2025-12-31T23:59:59Z
python scripts/query_financial_history.py monthly --month 2025-12-01 --known 2026-01-06T23:59:59Z
python scripts/query_financial_history.py monthly --month 2025-12-01 --known 2026-01-10T23:59:59Z
```

These are disposable acceptance queries, not a deployed semantic model. Claims deduplicate immutable events and reject conflicting duplicates. Monthly selection requires scenario/target/as-of; balance levels are not summed across months. Cost queries select one run per posting.

Re-running unchanged generation reuses all six stages and reproduces every canonical byte/hash. Changed seeds/policies/sources invalidate descendants before recomputation. `--fail-stage billing` tests a rollback; `--crash-stage posting` exits the process with 97 inside an uncommitted SQLite transaction. Use these only on an ignored scratch candidate. Resume the identical configuration to recover. Corrupt checkpoints must be rejected; do not patch checksums or accepted data to force readiness. Accepted parents are immutable and restoration refuses an existing destination.
