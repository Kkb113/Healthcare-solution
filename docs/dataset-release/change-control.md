# Change control, correction and retirement

Freeze a release by its version, producer commits, descriptor SHA, full payload inventory, effective schema, reference hashes, rules, review and owner acceptance. Consumer onboarding starts by verifying the externally trusted descriptor and all payload bytes. Source snapshots and correction histories retain their declared event/knowledge semantics.

Never edit, truncate, repair in place or overwrite an existing release. A correction creates a new version and a new complete descriptor. A dataset change requires the affected generator/dependency history, all affected downstream facts, source exports, reconciliations, profiles and reviews to regenerate. Rerun the full applicable final checks and obtain new owner acceptance. A prior acceptance is specific to one descriptor and limitations hash.

Use a major version for incompatible schema/grain, identity namespace or modeled-scope changes; a minor version for compatible additions; a patch for compatible corrections or packaging/documentation changes. The same normalized data with a changed envelope still has a new descriptor and cannot inherit an old acceptance silently. Update the accepted-candidate policy/anchors deliberately when business content changes.

If a consumer detects corruption or a P0/P1 defect, stop using that version, preserve the observed files/checksums and record the incident. Retire the release with an explicit reason in the external registry; do not delete the payload or rewrite its original acceptance. Retirement takes precedence over acceptance and blocks solution use. A replacement pointer must name a different release that is already accepted and active.

```powershell
python -m release_tooling.cli retire --package data/releases/healthcare-synthetic-v1.1.0 --registry data/release-registry --descriptor-sha256 <trusted-descriptor-sha256> --reason <documented-reason> --replacement healthcare-synthetic-v1.1.1
```

The command is an explicit operator action, not an automatic response in this project. A retired release cannot be accepted again; correcting and recertifying creates another version. Keep original gate, provenance, human decision and retirement records for traceability. Storage security, retention periods and external distribution require the separately authorized operational environment.

Data acceptance marks only the synthetic foundation `DATA_ACCEPTED`. No dashboard, model, Medallion pipeline, streaming product, agent or live integration is created by a state transition. Those remain separate authorized workstreams on Azure Databricks; Microsoft Fabric remains excluded.
