# Delivery, faults and record accounting

The per-file manifest includes source contract, schema version, table/source, format, period/scope, original finance file/template identities, vintages, replacement predecessor, expected rows, exact decimal totals by scalar field, bytes/SHA-256, typed key-dictionary bytes/count/SHA, and record availability range. A deterministic file ID binds the full manifest.

Scalar field totals are arithmetic file-integrity controls, not clinical or financial KPIs. Finance also has independently recomputed totals at period/scenario/vintage/account-or-measure/unit grain; admissions, patient-days, productive hours, FTE and USD are never combined in these business controls. Clinical measurements retain their individual units and exact record values; mixed-unit scalar checksums must not be interpreted as clinical aggregates.

Monthly JSON/CSV archives compact physical storage while preserving individual source availability. An archive's maximum availability describes its archive range; it is not a fictional claim that all events happened or arrived together. Event envelope ordinals validate archive order. The original `sequence_no`, effective time, recording time and correction reference determine actual bed state. Workday scheduled files and Axiom publications additionally gate row visibility on batch arrival. A deliberately delayed redelivery advances observed knowledge without changing economic/effective occurrence.

`DeliveryReplay` is an isolated SQLite **test consumer**, not a production lakehouse. File publication, immutable version insertion and delivery visibility commit atomically. A failed file leaves no partial business state and creates an unresolved quarantine. A valid redelivery explicitly resolves that quarantine. Missing expected files block completeness; zero rows are not fabricated. Exact file replays and repeated full snapshots preserve the same version set. Same-version conflicting payloads are quarantined. Actual replacements require the delivered predecessor, matching scope/source/table, later availability and a nonbranching chain.

For bed corrections, unavailable predecessors block effective projection until delivered; late originals and corrections converge by effective sequence. Workday selection keeps valid and knowledge times distinct; an earlier knowledge query excludes later retroactive corrections and revocations. Process-death tests terminate the replay inside an uncommitted WAL transaction and terminate an export before its group checkpoint is published.

## Published challenge package

`challenge-manifest.json` lists each affected record/file, injection stage, expected detector, disposition and final state. The valid controls and malformed deliveries live under `challenges/`, separate from `valid/`. A second observed-artifact inventory fingerprints the actual malformed bytes: deliberately wrong inner checksums are expected defects, not untracked corruption of the challenge package.

The package tests incompatible schemas, unknown references, missing required keys, nonfinite decimals, wrong scalar totals, wrong row controls, corrupt bytes, immutable-version conflicts, missing files, duplicate delivery, late/out-of-order bed correction, exact-scope replacement, retroactive worker history, explicit access revocation and full-snapshot reload. Every quarantine is shown blocking certification, then explicitly resolved to the expected original state. Scope crossing, implicit/branched replacements, bad headers, dates, integers, envelope sequences, duplicate version keys, cycles and cross-bed corrections receive additional mutation tests.

## Record budget

No valid business fact or history is added to the accepted **1,924,164 records / 25 tables**. The previously reviewed envelope remains **1,995,215 planned canonical rows + 4,785 reserve = 2,000,000**.

This reviewed source policy allocates **64 reserve slots** for published challenge/control copies, leaving **4,721 unallocated reserve**. Every published challenge record is counted conservatively against the global ceiling even when it mirrors a canonical record; malformed fragments are also counted. The actual count and per-table attribution are computed from the physical challenge files, independently recounted, and recorded in the passing gate. These challenge rows do not become valid table rows or silently modify a per-table canonical envelope.

The global release count is `canonical business rows + physical challenge/control records`. Primary source exports, scheduled history snapshots, scalar report mirrors, typed transport dictionaries, disposable replay versions/delivery indexes and clean-test rebuild copies are separately reported **physical mirrors**, not new healthcare facts. Wide reports count both their physical rows and the number of scalar fact cells they mirror. The manifest reports payload bytes, source rows, scheduled mirrors, dictionary entries, derived rows and scalar mirrors. This phase does not publish an additional canonical copy.

The selected native engineering review separately records its physical sample rows, scalar fact mirrors and bytes, including every wide-period cell and both sides of an adjustment/comparison. Review copies are not new healthcare facts and are not silently treated as distinct patients or financial records.

The source simulation remains blocked for solution use until Phase 9 accepts the final dataset. Native tenant testing, the full customer export inventory, production service credentials and live delivery transports are outside this simulation.
