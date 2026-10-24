# Source simulation runbook

Run from the repository with the pinned accepted environment (CPython 3.10.10, `tzdata==2025.2`). The immutable `output/financial-history` snapshot must match accepted business SHA `773a236ec9c7ec3df5605f38d21f4934a9384eae1bbf04ab4bf164cb51006b72` and the Phase 6 gate. The snapshot is generated data and is deliberately not committed to Git. Earlier accepted snapshots are restored with their exact-revision wrappers; never overwrite them using later source code. The accepted financial generator source is Git revision `eb20bfa55eb7ac9850f9b3f5b4037a247a4f3f82`.

```powershell
python scripts/generate_source_delivery.py
python scripts/run_source_regressions.py
python scripts/validate_source_delivery.py
```

The first command writes `output/source-delivery/valid`, source dictionaries, group checkpoints, manifests and the bounded challenge package. It writes `EXPORTED_NOT_YET_VALIDATED`, which is not acceptance. Native input fingerprints bind every table export to the accepted file, producer code, contracts, configuration and financial gate. The challenge package separately binds its own generator and accepted parent; readers/review controls are bound by complete regression fingerprints. Changing validation code cannot silently change native business files. Complete groups can be reused only after byte verification. Producer/input changes invalidate the affected export cache; stale/extra files fail inventory checks. Failed/crashed groups have no complete checkpoint and are regenerated. Every attempted rebuild removes an existing ready marker before inspecting inputs, after rejecting foreign output profiles.

The regression command runs all source tests, including independent round-trip inspection of all 1,924,164 persisted source records and reverse duplicate reload of all source files, six report-family mutation controls, published fault recovery, a separate complete clean export rebuild, full cache reuse, actual export process death/restart and actual SQLite transaction process death/recovery. It fingerprints source/test/script files, configuration/contracts/reviews, earlier acceptance evidence and actual source-package bytes before/after. Generated data and large test artifacts remain ignored.

The final command requires current complete passing test evidence and the matching, recorded user-designated engineering review. It retains the previous 280 domain tests only if every previously tested implementation/input/review byte remains unchanged, and labels those tests **retained**, not newly rerun. The new export stage cannot change accepted canonical files; all 25 reconstructed canonical table SHA/counts are independently compared to the accepted financial snapshot. Any preexisting source/input change reopens this dependency check rather than silently reusing a stale gate.

For an additional independent inspection without finalizing a gate:

```powershell
python scripts/validate_source_delivery.py --inspect-only --report output/source-delivery/additional-inspection.json
```

Acceptance publishes `evidence/source-delivery/acceptance-gate.json`, a detailed validation report, and an ignored `candidate-ready.json`. It certifies this source simulation only. Phase 8 integrated consumer/statistical validation and Phase 9 release certification remain required. No solution artifacts or live source integrations are created.

Review the printed failure and quarantined file identity before recovery. Do not edit canonical truth to accommodate a bad source. Restore or redeliver the expected file, rerun affected tests and gate, and retain the original fault lineage. A different customer source layout requires a reviewed, versioned mapping and its own native contract tests.
