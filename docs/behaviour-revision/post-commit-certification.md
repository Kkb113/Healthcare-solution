# Certify and publish version 1.1.0 after the producer commit

Run these steps from the repository root, in order, after committing every tracked change. The clean rebuild refuses an uncommitted tracked change and records the committed `HEAD` as the version 1.1.0 producer commit. Every later step is checked against that commit, so do not commit again until step 8. Generated data stays in ignored `output/` and `data/` paths.

```powershell
# 1. Release-tool fixtures, bound to the exact tools and prior evidence (about 1 minute)
python -m release_tooling.run_tests

# 2. Cold lineage: six accepted version 1.0 stages, then the version 1.1 integrated stage, in a fresh venv (about 90 minutes)
python -m release_tooling.rebuild --release-id healthcare-synthetic-v1.1.0 --output output/release-certification-v1.1.0/clean-build --wheel data/releases/healthcare-synthetic-v1.0.2/runtime/tzdata-2025.2-py2.py3-none-any.whl

# 3. Stage and certify the exact payload with the frozen validators (about 1 to 1.5 hours)
python -m release_tooling.certification --clean-build output/release-certification-v1.1.0/clean-build --staging output/release-certification-v1.1.0/staging --release-id healthcare-synthetic-v1.1.0
```

Step 3 prints the descriptor SHA256 and writes it to `output/release-certification-v1.1.0/clean-build/certifications/healthcare-synthetic-v1.1.0/technical-release-gate.json`. Use it as `<descriptor>` below.

```powershell
# 4. Publish create-once, then verify the published package and its offline reproducibility
python -m release_tooling.cli publish --staging output/release-certification-v1.1.0/staging --destination data/releases/healthcare-synthetic-v1.1.0 --descriptor-sha256 <descriptor>
python -m release_tooling.cli verify --package data/releases/healthcare-synthetic-v1.1.0 --descriptor-sha256 <descriptor>
python -m release_tooling.offline_check --package data/releases/healthcare-synthetic-v1.1.0 --output output/release-certification-v1.1.0/offline-check --descriptor-sha256 <descriptor>
```

5. Record the release-level domain review in `reviews/dataset-release-v1.1.0-review.json` and the issue closure in `reviews/dataset-release-v1.1.0-issues.json`, bound to the descriptor, limitations, certification, review-binding and offline-check hashes. The required fields match `reviews/dataset-release-review.json` and `reviews/dataset-release-issues.json` for version 1.0.2.

```powershell
# 6. Technical final gate: expect AWAITING_BUSINESS_ACCEPTANCE
python -m release_tooling.final_gate --package data/releases/healthcare-synthetic-v1.1.0 --registry data/release-registry --descriptor-sha256 <descriptor>
```

7. Business-owner acceptance is a human decision. Write an approval JSON with `decision=ACCEPT_DATA_RELEASE`, the release ID, the exact descriptor and `docs/limitations.md` SHA256 from the package, `limitations_acknowledged=true`, the owner's name, `authority=DIRECT_HUMAN_USER_APPROVAL`, the owner's actual approval message and `separate_solution_authorization_required=true`. Then:

```powershell
python -m release_tooling.cli accept --package data/releases/healthcare-synthetic-v1.1.0 --registry data/release-registry --descriptor-sha256 <descriptor> --approval <approval.json>
python -m release_tooling.final_gate --package data/releases/healthcare-synthetic-v1.1.0 --registry data/release-registry --descriptor-sha256 <descriptor>
```

8. Commit the release evidence (`evidence/dataset-release-v1.1.0/`, the two `reviews/dataset-release-v1.1.0-*.json` records and a copy of the registry acceptance record) and push.

After acceptance, retire version 1.0.2 with `python -m release_tooling.cli retire ... --replacement healthcare-synthetic-v1.1.0` only if downstream consumers should stop using it. Never mix 1.0.2 and 1.1.0 deliveries.
