# Azure Databricks Implementation Plan: Healthcare Analytics Platform

**Status:** Revised design baseline with authorized prerequisite preparation, 2026-10-27; analytics implementation not started. The [readiness record](platform/docs/prerequisite-readiness.md) distinguishes tested prerequisite changes from unpassed implementation gates. Synthetic data generation is complete: release `healthcare-synthetic-v1.1.0` is certified and `DATA_ACCEPTED` (descriptor `c36a9b7841743057be2f6993a27790c82a170c847399687a0c2647b5b9167af5`).
**Platform:** Azure Databricks only. Microsoft Fabric and Power BI are out of scope.
**Sequence:** Fourteen phases, Phase 0 through Phase 13. Real-Time Intelligence is the final phase.
**Budget:** ₹20,000 one-time build budget for the POC. After the build, the platform runs 1–2 demo days a month and sleeps the rest of the time (sections 3.6–3.8).
**Related documents:** [synthetic data plan](synthetic-data-generation-implementation.md) · [behaviour revision](docs/behaviour-revision/README.md) · [dataset limitations](docs/dataset-release/limitations.md) · [solution design](docs/solution-design/healthcare-platform-solution-design.html)

---

## 1. Purpose and scope

This document is the execution roadmap for building the healthcare analytics platform on Azure Databricks. It defines what is built in each phase, in what order, what each phase depends on, what it delivers, how it is tested, and the measurable criteria that must pass before the next phase starts.

The platform delivers:

| Capability | Summary |
| --- | --- |
| Medallion architecture | Bronze, Silver and Gold layers for eight source systems, with data quality, schema validation, error handling and orchestration |
| Semantic layer and dashboards | Unity Catalog metric views with owned KPI definitions; AI/BI dashboards |
| Forecasting and prediction | 13 use cases: trained models, a census simulation and derived staffing demand, with eligibility checks, baselines, uncertainty and lifecycle controls |
| Genie | Four domain Genie spaces for no-SQL analytics |
| AI agent app | A Databricks App with a custom agent on GPT-6 Luna that answers from tables, predictions and documents with verified citations |
| DataOps Autopilot | A Databricks App that monitors platform health, diagnoses failures, assesses impact and recommends or performs guarded fixes |
| Real-Time Intelligence (RTI) | A continuous healthcare event generator, streaming ingestion, dedicated real-time tables, live monitoring and operational alerts |
| Governance | Unity Catalog data and AI governance, PHI protection, access control, audit and lineage |

### 1.1 Starting point

| Item | State |
| --- | --- |
| Dataset | `data/releases/healthcare-synthetic-v1.1.0/`, 7,126 payload files, verified and accepted |
| Canonical tables | 25 tables, 1,937,925 rows, business SHA256 `12859a18…` (the "answer key") |
| Native source files | 3,445 delivery files across 8 source systems, plus 19 challenge sets (22 challenge/control record copies, 15 expected fault outcomes) |
| Scope | 3 fictional Illinois hospitals, 72 beds, January 2023 to December 2025, America/Chicago time zone |
| Source systems | `ehr`, `adt-bed`, `workday`, `roster-time`, `supply-pharmacy`, `revenue-cycle`, `finance-erp`, `axiom` |
| Reference decoder | `src/healthcare_synthetic/source_reader.py` reconstructs every canonical row from the native files and is the reference implementation for Bronze and Silver decoding |

Acceptance is established by the pinned release descriptor and final certification/acceptance evidence. Some nested producer manifests retain their historical candidate/export status; verify their hashes as provenance without treating those older flags as a new acceptance decision or editing them to change status.

### 1.2 Dataset limits that shape the build

From the accepted [limitations](docs/dataset-release/limitations.md):

- Small scale by design: about 3.6 inpatient admissions per hospital per day. Forecast accuracy is modest; present methods and uncertainty, not accuracy claims.
- RN overtime is under 1% of RN hours. No overtime forecasting model.
- Nurse hours per patient-day is a fixed generation rule (8.0). Staffing demand is derived from the census forecast, not learned.
- Only 9 inventory items have consumption.
- Mortality is out of scope (30 boundary cases only).
- Clinical notes are template-driven. Suitable for retrieval demonstrations, not clinical claims.
- Never mix v1.0.2 and v1.1.0 deliveries. Load everything from v1.1.0.
- Prospective feature availability is limited: none of the 25,800 attended/no-show appointment records is exported before its scheduled start, none of the 4,800 elective-admission bookings becomes visible before its scheduled start (so booked elective schedules are never available at a forecast origin), and none of the 11,107 encounters with a medically-ready timestamp has that readiness record available before discharge. M11 is retrospective-only on this release; M2 forecasts elective admissions from history and M3 takes elective inflow from the M2 forecast; M5 must exclude the unavailable readiness flag. Business timestamps do not establish that a feature was available to the platform.
- Inpatient headers first become available 1 hour 45 minutes after admission across all 12,012 IPD encounters; none of the 57,818 claim headers is available by `first_submitted_at`. M4/M5 begin at the first eligible available inpatient snapshot, and M10 at the first eligible available claim snapshot before the predicted adjudication. These delays change decision origins, not the accepted dataset; the exact contract is in section 8.1.
- Cost allocations support encounter × accounting month × cost category for a selected allocation run. They do not establish measured patient × procedure costs or complete enterprise profitability.

### 1.3 Success boundary and controlled evolution

Success means a reproducible, governed **synthetic healthcare POC** with reconciled data, eligible predictive products, tested applications, recovery procedures and measured operating costs. `hc_prod` is the demonstration release catalog; passing this plan does not qualify the platform for real patient data or clinical use. Real-data production requires a separate funded security, privacy, clinical, availability and scale qualification.

Freeze source contracts, identifiers, grains, timestamp semantics and authorization rules before implementation. Evolve them through versioned contracts, impact analysis, migration tests, an ADR and a tested rollback or rebuild. Later phases may improve the design through that process; no phase may silently rewrite the accepted dataset or invalidate earlier evidence. This Markdown is the execution authority; linked HTML illustrations must not override its revised contracts.

---

## 2. Phase map

| Phase | Name | Depends on | Key deliverables | Indicative duration* |
| --- | --- | --- | --- | --- |
| 0 | Mobilization and architecture decisions | — | ADRs, environment plan, cost budget, team roles | 1 week |
| 1 | Azure infrastructure provisioning | 0 | Adopt existing workspace; dedicated resource group, ADLS Gen2, Key Vault, Unity Catalog storage and budgets; retain the documented Luna prerequisite exception; Event Hubs deferred | 1 week |
| 2 | Databricks platform foundation and CI/CD | 1 | Catalogs, schemas, volumes, groups, grants, compute and budget policies, SQL warehouse, Asset Bundles, CI/CD, shared library | 1–2 weeks |
| 3 | Synthetic data release and data onboarding | 2 | v1.1.0 native files in landing; answer key in `reference`; source contract registry | 3–4 days |
| 4 | Bronze ingestion | 3 | Metadata-driven ingestion of all 25 feeds, delivery ledger, quarantine, challenge handling | 1–2 weeks |
| 5 | Silver conformance and data quality | 4 | 25 conformed tables, key resolution, bitemporal history, DQ rule catalog, reconciliation to the answer key | 2–3 weeks |
| 6 | Gold, semantic layer, dashboards and access policies | 5 | Facts, dimensions, metric views, four dashboards, PHI masks and row filters | 2 weeks |
| 7 | DataOps Autopilot core app | 4, 5, 6 | Telemetry collection, health model, detection, incidents, health dashboard app | 2 weeks |
| 8 | Forecasting and machine learning | 6, 7 | Feature eligibility, 13 use-case dispositions, supported models and derived products, tracking, registry, inference and monitoring | 3–4 weeks |
| 9 | Genie spaces | 6, 8 | Four Genie spaces with instructions, trusted SQL and benchmarks | 1 week |
| 10 | AI agent and Databricks App | 6, 8, 9 | GPT-6 Luna endpoint, tools, citation ledger, grounding verifier, guardrails, evaluation, app | 3 weeks |
| 11 | DataOps Autopilot intelligence and remediation | 7, 10 | Root cause, impact analysis, playbooks, guarded remediation, diagnostic agent, alerting | 2 weeks |
| 12 | Batch integration, end-to-end testing and POC release readiness | 1–11 | E2E suite, performance and security tests, recovery, runbooks, demonstration release | 2 weeks |
| 13 | Real-Time Intelligence (final) | 12 | Continuous data generator app, Event Hubs, dedicated real-time tables, streaming pipelines, Lakebase, Command Center, live alerts | 3 weeks |

\*Indicative for a team of two data engineers, one ML engineer and one application engineer. Local design and unit-test preparation may overlap. Cloud execution, publication and gate approval follow the dependencies above: Phase 8 waits for both Phases 6 and 7. A partial domain wave is not a passed phase gate.

### 2.1 Gate rule

A phase is complete only when every applicable exit criterion is met, evidence is recorded in `evidence/platform/<capability-name>/gate.json`, and the phase owner signs off. Use descriptive directory and file names; record the phase number inside the gate. Each gate records the Git SHA, dataset descriptor, environment, dependency gates, test scope, measured values, costs, limitations and evidence links. A failed criterion blocks every dependent phase. Scope changes require an ADR and revised measurable acceptance criteria before execution; an exception cannot be reported as a passing result.

Use `PASS`, `FAIL` or `NOT_APPLICABLE` per criterion, with a reason and owner for the last status. A modeled use case marked retrospective-only is a published limitation, not a skipped prospective test or a successful online model. Mandatory integrity, authorization, cost and recovery checks cannot be waived. Commit and push the passing phase package, evidence and runbooks before starting its dependent phase.

### 2.2 Domain waves inside Phases 5, 6 and 8

Within layer phases, work proceeds in dependency order. Resolve within-wave references before publishing the wave; a topological dependency check covers the complete table and column contracts:

| Wave | Domain | Canonical tables |
| --- | --- | --- |
| A | Facility, financial and reference foundations | facility, cost_center, location, catalog_item, payer_plan, facility_day_driver |
| B | Patient and workforce identities | patient, patient_coverage, worker_assignment, access_scope, source_key_map |
| C | Patient flow and clinical activity | encounter, clinical_condition, clinical_event, appointment, bed_event |
| D | Workforce activity and supply | staff_shift, inventory_movement |
| E | Revenue cycle and finance | service_charge, claim, claim_line, claim_event, financial_posting, cost_allocation, finance_monthly |

In particular, cost centers and workers precede dependent locations, encounters and rosters; `source_key_map` loads after the patient and worker identities it targets; clinical events precede referencing service charges. The 25-table limit applies to the certified synthetic source model. Platform metadata, derived facts, features and streaming tables are additional application assets, never additional canonical source rows.

---

## 3. Platform-wide standards

### 3.1 Environments

| Environment | Catalog | Purpose | Data |
| --- | --- | --- | --- |
| dev | `hc_dev` | Development and unit tests | Full v1.1.0 (it is small) |
| test | `hc_test` | Bounded integration, fault injection, E2E, security and recovery gates | Required full v1.1.0 inputs plus isolated challenge sets |
| prod | `hc_prod` | Approved synthetic demonstration release | Full v1.1.0 |
| ops | `hc_ops` | Platform telemetry, Autopilot state, cost data | Telemetry only |

One workspace with separate catalogs is acceptable for the synthetic POC (ADR-01). Real-data workspace isolation and network controls require a separate architecture approval. Build in `hc_dev`; deploy changed assets to `hc_test` only for scheduled gate tests, not after every merge. Publish one batch release to `hc_prod` in Phase 12 and its RTI extension in Phase 13, with targeted smoke tests. Test catalogs and paths are isolated so challenge rows never enter the demonstration release.

Adopt the existing Premium **SERVERLESS** workspace `intellify-healthcare-dbw` in East US, workspace ID `7405619366453187`, subscription `d054aa64-95db-467b-a25c-387de70b15bd`. Reference it as existing infrastructure; do not recreate it as a classic workspace or move it to another region. Supporting healthcare resources use a dedicated resource group. The verified exact-model exception uses Azure OpenAI in a second MCPP subscription, `0725b5e7-75db-4c60-b5e9-928c3df3fcd1`, in the same tenant and East US region, through the existing workspace's gateway. Both subscriptions must be included in cost reconciliation. Configuration and dated probe evidence are in the readiness record.

### 3.2 Schemas in each environment catalog

`landing` (volumes) · `reference` (answer key, calendars) · `bronze` · `silver` · `gold` · `semantic` (metric views, functions) · `features` · `ml` (models) · `pred` (predictions) · `agent` (agent tables, vector indexes) · `dq` (rule catalog and results) · `rt` (real-time, created in Phase 13)

### 3.3 Repository layout

```
platform/
  databricks.yml                 # Asset Bundle root, targets dev / test / prod
  resources/                     # bundle-owned jobs, pipelines, apps, dashboards and alerts (YAML)
  infra/foundation/              # dedicated healthcare Azure resources and foundation identities
  infra/model-access/            # exact-model subscription exception, managed identity and cost alerts
  infra/workspace/               # workspace-level objects added in their implementation phase
  src/hcp/                       # shared Python package built as a wheel
    common/ contracts/ auth/ telemetry/ ingest/ silver/ gold/ dq/ features/ ml/ agent/ autopilot/ rti/
  pipelines/                     # Lakeflow Declarative Pipeline sources
  sql/                           # DDL, metric views, UC functions, masks, row filters
  apps/agent/  apps/autopilot/  apps/command-center/  apps/rti-generator/
  genie/                         # space definitions, instructions, trusted SQL, benchmarks
  ml/local/                      # local training entry points (Phase 8 evaluation)
  tests/unit/  tests/integration/  tests/e2e/  tests/agent_eval/  tests/fault_injection/
  docs/adr/  docs/runbooks/
evidence/platform/<capability>/ # descriptive names; phase numbers inside gate.json
```

### 3.4 Naming and standard columns

| Item | Rule | Example |
| --- | --- | --- |
| Tables | `<schema>.<domain>_<entity>` for Bronze/Silver; `fact_`, `dim_` in Gold | `silver.ehr_encounter`, `gold.fact_census_hourly` |
| Predictions | `pred.<model>_<grain>` | `pred.ed_arrivals_daily` |
| Bronze lineage columns | Every row | `_ingest_ts`, `_source_file`, `_file_sha256`, `_delivery_id`, `_batch_id`, `_source_system`, `_source_version`, `_record_hash` |
| Time | UTC plus local for every business timestamp | `arrival_at_utc`, `arrival_at_local`, `arrival_date_local` |
| Governed tags | Every table and column | `domain`, `owner`, `pii_class` (PHI, PII, NONE), `sla_tier`, `layer` |

Every cloud resource has **one lifecycle owner** in an ADR resource register: Terraform for infrastructure and workspace foundations, Bundles for supported application resources, and one versioned API deployment adapter for unsupported resources. For the agent endpoint, choose either an `agents.deploy` adapter or Bundle management, never both. Sleep and wake invoke the same owner; Terraform refresh/import reconciles intentional temporary deletion. Pin provider, CLI, runtime/channel, Spark/Delta, MLflow, SDK and dependency versions; upgrades require targeted compatibility tests. Share contracts, query clients, authorization, telemetry and citation code across apps; keep remediation execution in a separately privileged backend.

### 3.5 Cost policy (applies to every phase)

Cost controls are acceptance criteria, not suggestions. Each phase gate includes a cost check.

| Resource | Created in | Configuration | Idle policy |
| --- | --- | --- | --- |
| SQL warehouse | Phase 2 | Serverless, size 2X-Small, min 1 / max 1 cluster (max 2 in prod) | **Auto-stop 5 minutes.** Serverless warehouses support this; classic and pro warehouses do not go below 10 minutes, so they are not used |
| Jobs and pipelines | Phase 4 | Serverless; triggered, never continuous outside Phase 13 demo windows; cost-optimized (standard) serverless mode where offered | Stop on completion; no always-on pipelines |
| Notebooks | Phase 2 | Serverless notebook compute | Auto-terminates when idle |
| Classic clusters | Unavailable in the adopted SERVERLESS workspace | No classic-compute fallback or quota-dependent cluster policy | A need for classic compute requires a separate architecture decision; do not recreate this workspace |
| Model serving | Phase 8 | Small workload size, **scale to zero enabled** | Scales to zero when idle |
| Vector Search | Phase 10 | One shared endpoint, smallest option | Billed while provisioned: deleted by `platform_down`, recreated by `platform_up` |
| Lakebase | Phase 10 (sessions), Phase 13 (live state) | Smallest capacity; auto-pause where supported | Stopped by `platform_down` |
| Databricks Apps | Phases 7, 10, 13 | Smallest app compute | Billed while running: stopped by `platform_down` and at the end of each working day |
| Genie | Phase 9 | Native UI/API/benchmark usage has separate Unity Gateway shared/per-user budget controls and bounded query windows; SQL compute is priced separately | Space/query access limited to funded windows; actual billed/free usage tracked in the Genie allocation; the application reservation ledger does not cap native Genie |
| LLM tokens (GPT-6 Luna) | Phase 10 | Shared transactional reservations for application-controlled model calls; gateway limits and approximate budget blocking as an additional control (section 3.10) | Pay per token; no provisioned throughput for the POC; application admission control is not an absolute platform invoice cap |
| Event Hubs | Phase 13 only | Standard tier (required for the Kafka endpoint), 1 throughput unit, auto-inflate off | Billed hourly even with no traffic: deleted by `platform_down` after every RTI window |
| Storage | Phase 1 | ADLS Gen2 hot tier; lifecycle rule moves landing files older than 90 days to cool | Delete test and staging outputs after each test cycle |

**Budgets and monitoring:** Azure budgets in section 3.6 and workload tags `component` and `phase` support attribution. Join Databricks usage to the applicable price list; DBUs alone are not currency. Reconcile delayed Azure/Databricks records without double-counting and reserve for outstanding usage before another window. Unity Gateway blocking uses approximate estimated spend, excludes direct standalone serving/provisioned-throughput traffic, and external-model budget inclusion is Beta. Application-controlled model calls must use both the approved gateway route and the reservation service in section 3.10; native Genie and other managed services have separate controls. None of these mechanisms guarantees an absolute final Azure bill cap. See [Gateway budget coverage and limits](https://learn.microsoft.com/en-us/azure/databricks/ai-gateway/budgets). Autopilot adds historical cost analysis in Phase 7.

### 3.6 Build budget: ₹20,000 one-time

The POC build (Phases 1–13) has a ₹20,000 ceiling for Azure and Databricks charges. This is a budget constraint, not a demonstrated estimate. Phase 0 must price the complete test plan, minimum service capacities, wake/rebuild time, idle billing tails and contingency in the selected region, with currency conversion and tax treatment recorded. Local hardware, staff time and any external CI charges are outside this cloud ceiling and must be disclosed separately. If the estimate does not fit, revise scope and acceptance criteria with the owner before provisioning; do not omit required checks or claim the full scope is affordable.

**Rule 1: develop locally, run on Databricks only when the code is ready.** The complete accepted payload is about 4.47 GB; size each working subset before choosing local resources. Develop decoders, DQ, features and models with local PySpark/Delta or Polars and pinned dependencies. Native deliveries remain the pipeline input; the local canonical copy is an independent test oracle. Databricks integration tests must verify UC, pipeline, authorization and serving behavior that local tools cannot reproduce.

**Rule 2: selective execution across three logical environments.** Use dev for iteration; run bounded test deployments for contract, security, fault, integration and recovery gates. Reuse a certified full test load when its code and input hashes have not changed. Prod receives the Phase 12 batch release and Phase 13 RTI extension only. No automatic full test/prod rebuild on each merge; all required exit checks still run in the declared environment.

**Rule 3: measured service lifecycle.** Vector Search, Lakebase, Event Hubs and serving run only for funded windows. Code must recreate or resume them, restore ACLs, and verify readiness; a create API returning successfully is not readiness. Persist reusable embeddings and configurations, include sync and index rebuild costs, measure billing cessation, and keep all incurred tails in the build total. Scale-to-zero behavior is tested rather than assumed to stop every associated charge.

**Rule 4: compute counts, not data volume.** At this scale a full Bronze-to-Gold run is a small cost. Running the SQL warehouse for hours, leaving apps or endpoints on, and repeating full agent evaluations are what consume the budget.

**Allocation**

The allocation covers every billed workload this plan requires, including the Phase 2 capability probes, the Autopilot operational worker during awake windows, Genie usage, the section 3.9 warm and cold load tests (at least 100 requests per component), the five Gold-deadline replay days (6.7) and seven Autopilot replay days (7.3), one shared clean-catalog release rebuild (12.1 and 12.5) and the continuous RTI pipeline and Lakebase sync. The lines are planning placeholders until Phase 0 prices them; if a priced line does not fit, revise scope with the owner (section 3.6) rather than move money silently between lines.

| Area | Phases | Budget | Main control |
| --- | --- | --- | --- |
| Medallion pipelines (validated runs, replay days, one shared clean-catalog release rebuild) | 4–6, 12 | ₹3,000 | Local development; about 10 full Databricks runs in total; 12.1 and 12.5 share one rebuild |
| SQL warehouse (dashboards, Genie queries, agent queries, gate checks, load tests) | 2–13 | ₹3,500 | 5-minute auto-stop; SQL development locally or in serverless notebooks |
| Phase 2 capability probes (LLM route, serving, search, Lakebase, Apps authorization) | 2 | ₹800 | Minimum fixtures only; every temporary resource removed after its probe |
| Autopilot telemetry jobs, app and operational worker | 7, 11 | ₹1,200 | Worker and collector run only while the platform is awake |
| ML training and batch scoring | 8 | ₹1,200 | Tune locally; cost both cloud and hybrid paths, including feature exports, verification and scoring |
| Model serving | 8, 10 | ₹500 | Scale to zero; endpoints created for testing windows only |
| Agent LLM tokens (GPT-6 Luna) | 10, 11 | ₹3,500 | 30–50-question quick evaluation during development; full 200-question evaluation at most twice |
| Genie usage billed through Unity Gateway | 9–13 | ₹300 | Benchmarks and demo questions only; tracked in the Unity Gateway budget |
| Vector Search, Lakebase, apps during test windows | 10, 11, 13 | ₹2,000 | Created on test days, deleted or stopped afterwards |
| RTI (Event Hubs, generator, continuous pipeline, continuous Lakebase sync) | 13 | ₹2,000 | Three test windows of up to 2 hours; continuous modes only inside windows; Event Hubs deleted afterwards |
| Storage, Key Vault, miscellaneous | 1–13 | ₹500 | Lifecycle rules; delete test outputs |
| Contingency | — | ₹1,500 | Released only by the platform owner |
| **Total** | | **₹20,000** | |

**POC test scope to cost in Phase 0** (larger operating/reliability programmes require separate funding):

| Plan item | POC version |
| --- | --- |
| Full test and prod runs after every merge | Selective test gate runs; one batch release and one RTI extension to the demo catalog |
| Three consecutive end-to-end runs (exit criterion 12.1) | One full run plus one rerun to prove idempotency |
| 24-hour RTI soak test (exit criterion 13.8) | 2-hour soak at 1× speed plus a 30-minute accelerated run at 30× |
| Full 200-question agent evaluation on every change | Quick 50-question evaluation before each funded agent deployment; full evaluation before the Phase 10 gate and Phase 12 release |
| Always-on Vector Search, Lakebase and serving endpoints | Created for test and demo windows only |
| Private networking (VNet injection) | Not used for the POC; its NAT gateway charges even when idle |

**Tracking:** maintain a dated build-cost ledger across billing months, reconciled to Azure Cost Management and priced Databricks usage. Configure a ₹20,000 build budget for a supported custom period, or monthly budgets plus that cumulative ledger; alerts are at ₹5,000, ₹10,000, ₹15,000 and ₹18,000. Azure budgets alert but do not stop pay-as-you-go spending. Before each window require remaining budget to cover its upper estimate, outstanding charges and shutdown costs. At ₹18,000, pause new workloads pending a reconciled completion estimate; stop if the ceiling cannot be met. Record gross consumption, credits and net charges separately so credits do not hide the operating cost.

### 3.7 Operating model after the build: demo days and sleep mode

After Phase 13 the platform is used 1–2 days a month. The batch history does not change, so Bronze-to-Gold, training and scoring are not rerun each month. Gold tables, predictions and model metrics produced during the build are read on demo days. Only the RTI stream creates new data on a demo day.

**Things that keep charging while nobody uses the platform**

| Keeps charging while idle | Sleep action |
| --- | --- |
| Scheduled jobs (`medallion_daily`, `autopilot_collect` every 15 minutes, `ml_score_*`, retraining) | Pause every schedule and file-arrival trigger |
| SQL alerts, dashboard subscriptions, data quality monitor refreshes | Pause; each one wakes the SQL warehouse |
| Native Genie access and benchmark callers | Disable the funded access profile and benchmark execution outside its window; restore approved permissions on wake through the registered lifecycle owner |
| Databricks Apps (agent, Autopilot, Command Center, RTI generator) | Stop |
| Vector Search endpoint | Delete; indexes are rebuilt from code on wake-up |
| Lakebase instance and sync pipelines | Stop or suspend using the supported product controls; confirm sync and connection polling cannot keep compute awake |
| Event Hubs Standard namespace (billed hourly with no traffic) | Delete; recreated by Terraform |
| Model serving endpoints | Scale to zero or delete through their registered lifecycle owner; confirm associated inference/monitoring work is paused |
| Interactive or classic compute | Confirm 0 running |
| SQL warehouse | Auto-stops after 5 minutes; confirm stopped |
| Storage, Key Vault, Unity Catalog metadata | Remain (small fixed cost) |

The sleep target is zero Databricks workload compute after shutdown has settled. Storage, secrets, external control-plane checks and any measured minimum/tail service charges are itemized separately; the observed bill must support the claim.

**Sleep and wake automation** (built in Phase 2, extended in Phases 7, 10 and 13)

| Control-plane command | What it does | Duration |
| --- | --- | --- |
| `platform_down` | Persists state, pauses schedules/triggers/alerts/monitors/syncs; drains streams; stops apps and Lakebase; deletes disposable Vector Search/Event Hubs resources through their owners; checks resource state and sets `ASLEEP` | Measure shutdown and billing-settlement time separately |
| `platform_up` | Restores only the chosen batch/RTI demo profile, indexes, ACLs and state; performs readiness and authorization checks and one health sweep; sets `AWAKE` only when ready | Target under 30 minutes; measure cold rebuilds before committing to the demo time |
| `platform_guard` | Checks resource and schedule state through control-plane REST APIs from a scheduled CI runner or local client; alerts and invokes an approved shutdown on drift | Daily while asleep; **no Databricks job, SQL query or serverless workload is started** |

Store the authoritative control state and resource/session manifest in a durable ADLS control object accessed by REST; mirror it to `hc_ops.autopilot.platform_state` while awake. This avoids waking a warehouse just to check whether the platform is asleep. Commands are idempotent and record `STARTING`, `AWAKE`, `STOPPING`, `ASLEEP` or `FAILED`, timestamps and failed actions. `platform_down` also runs from the external controller at each window's hard deadline (for example 20:00 local), independent of an app or collector remaining healthy.

**Autopilot sleep state:** while asleep, the collector is paused and expected inactivity does not open freshness incidents; security or resource-state drift can still alert through the external guard. On wake-up, verify content/version integrity and complete a health sweep before enabling the selected demo profile. Static 2023–2025 batch data uses `STATIC_CERTIFIED` SLOs, based on the accepted release and expected deliveries, even while awake. `SCHEDULED_REPLAY` checks use replay-clock due times; `LIVE` checks use wall-clock ingestion SLAs. Do not retrain or mark certified history stale just because a calendar month has passed.

**Monthly operating estimate** (planning figures, confirm in Phase 12):

| Demo-day item | Estimate |
| --- | --- |
| SQL warehouse for dashboards, Genie and agent queries (4–8 running hours) | ₹1,000–2,000 per demo day |
| Apps running for the day | A few hundred rupees |
| LLM tokens for a few hundred questions | ₹200–1,000, depending on GPT-6 Luna pricing |
| Genie usage billed through Unity Gateway | Measure in Phase 12; include in the monthly profile |
| RTI demo (generator, Event Hubs, streaming for 2–3 hours) | ₹500–1,500 |
| Vector Search and Lakebase for the day | A few hundred rupees |
| Storage (always on) | ₹100–300 per month |
| **Monthly target** | **₹6,000 ceiling to validate with measured demo durations; the component ranges above are not proof that two full days fit** |

A separate monthly Azure budget of ₹6,000 alerts at 50%, 80% and 100%. Phase 12 measures one complete demo profile and projects both one-day and two-day totals, including persistent storage, rebuilds, syncs and billing tails. Shorten the demo windows or revise the agreed budget before scheduling an unaffordable profile.

### 3.8 Cost checks added to phase gates

| Phase | Cost check in the gate |
| --- | --- |
| 1 | No VNet injection or NAT gateway; build budget and monthly budget both configured |
| 2 | Warehouse auto-stop 5 minutes; control-plane sleep/wake/guard skeletons tested; idle check returns 0 running compute without waking a workload; capability-probe spend within its allocation |
| 4–6 | Number of full Databricks pipeline runs and their cost recorded; within the medallion allocation |
| 7 | Autopilot collector honours the sleep state; collection cost recorded |
| 8 | Training location decision (ADR-06) recorded with measured cost; endpoints scale to zero |
| 9 | Native Genie budgets, actual caller identities, query/access windows and billed/free usage verified separately from app reservations; charges recorded in the Genie allocation |
| 10 | Shared application reservation/failure tests pass; token/evaluation costs settled or conservatively reserved; search/Lakebase services deleted or stopped after the gate |
| 12 | One full sleep–wake cycle passes after billing settlement; one measured demo day and one-/two-day monthly projections fit the agreed budget |
| 13 | Event Hubs deleted after the final RTI window; total build spend at or below ₹20,000 |

### 3.9 Measurement contracts

Phase 0 defines the workload and minimum sample size for each service target; gates report sample counts, p50/p95/p99, failures, compute size, data version and cost. For interactive load tests use at least 100 completed requests per component, a declared question/query mix and 10 concurrent users. Include timeouts and errors in the report; report both steady-state warm performance and a separate cold-start measurement after sleep or scale-to-zero. The warm targets are dashboard tile p95 <5 seconds, eligible risk endpoint p95 <300 ms, and full agent answer p95 <15 seconds. SQL/LLM/model time, tool calls, polling and network time are included at their respective boundaries. A first token is not a completed agent answer.

Static historical data has no daily refresh obligation in demonstration mode. Validate the 06:00 America/Chicago Gold SLA using timestamped scheduled-replay due times and five representative consecutive replay days, including DST and large delivery days. Replaying source timestamps is not a claim of five days of continuous operations. Freeze these workloads before testing; targets may change only through a reviewed contract revision, never after observing a failing result.

### 3.10 Spending controls and enforcement boundaries

The platform has three distinct cost boundaries. **Application-controlled model calls** from the healthcare agent, Ask Autopilot and their evaluation clients use a shared reservation service. **Native Genie** UI, Conversation API and benchmarks use native platform budgets and bounded access/query windows, including when the agent invokes Genie as a tool. **Compute, storage, search-managed operations and other service charges** use the priced workload ledger, resource limits and shutdown controls. Do not claim the application counter controls internal Genie model calls, managed embedding work or the whole Azure invoice; attribute each charge to one cost bucket.

For application-controlled model requests, implement the following contract before the first funded agent deployment:

1. **Shared durable ledger:** the agent and Autopilot use the same app-owned Lakebase budget ledger through a narrowly scoped service. A process-local counter is insufficient. Record request/turn/attempt IDs, verified caller, component, environment, budget window, model/price-policy version, reservation, settled usage and status. Keep monetary values in integer minor units with conservative rounding and recorded currency conversion. Sleeping/restarting an app must not erase outstanding reservations or cumulative build spend.
2. **Atomic admission:** in one transaction reserve against every applicable user, component, evaluation-run and shared build/day limit only if `settled_spend + outstanding_reservations + request_upper_bound <= limit`. Use row locking or an equivalent serializable transaction across buckets so concurrent app workers cannot each spend the same remaining balance. Reject new calls when the ledger is unavailable, a price/limit is unknown, the platform is asleep or any applicable limit is exhausted.
3. **Bounded request cost:** calculate a conservative upper reservation from the complete prompt/tool context, supported maximum billable output/reasoning tokens, provider operation/feature fees and price/FX safety margin. Bound tool/model-call counts per turn. An operation without a defensible cost bound is not admitted by this route. Reserve every billable retry/fallback attempt separately before dispatch; application idempotency prevents duplicate dispatch for the same attempt. A provider retry is not assumed free or idempotent.
4. **Settlement and uncertainty:** settle once against reported provider usage, release only the verified unused reservation, and reconcile later to billing. Persist pending/unknown outcomes across failures; a timeout, expired lease or calendar reset alone must not release money for an attempt that may still be billed. A new retry needs its own reservation while an uncertain earlier attempt remains covered. Reconcile late charges to their original window. Freeze new calls and investigate if actual usage exceeds the reserved bound; retain safety headroom rather than describe this as an invoice guarantee.

For native Genie, configure a Unity Gateway budget scoped with the supported `databricks-product: genie` resource tag, shared and per-user thresholds with **Block usage**, alerts, and a separately tracked SQL warehouse allocation. Do not add unsupported extra resource-tag filters. Apply the budget to the actual human/service-principal identities used by spaces, tools and benchmarks; those calls do not pass through the application reservation ledger. Bound benchmark/question counts and funded windows, restrict native access outside those windows, and retain room for approximate blocking and in-flight requests. Free/promotional versus paid usage depends on product, caller identity and date; verify actual SKUs/terms for each gate rather than assume UI and service-principal costs match. See [Genie budget configuration](https://learn.microsoft.com/en-us/azure/databricks/genie/budgets) and [Genie cost attribution](https://learn.microsoft.com/en-us/azure/databricks/genie/monitor-cost).

Phase 0 fixes the numerical limits, daily-window timezone, price/headroom policy, native Genie scope and ownership in ADR-10. Before the reservation service exists, Phase 2 capability probes are a narrowly defined exception: an isolated temporary principal, fixed maximum call/token count, preapproved upper-cost allowance and gateway controls; no application user access or unbounded agent loop. Record/cover the complete probe allowance in the build ledger, reconcile usage and remove probe access afterwards. Phase 9 verifies native Genie controls; Phase 10 tests concurrent reservations, duplicate dispatch/settlement, retry/timeout/crash recovery, price changes, exhausted budgets and unavailable ledgers before any funded agent deployment. A budget rejection is a controlled response, not a retry loop. Platform-wide billing reconciliation and the ₹20,000 go/no-go rule remain mandatory.

---

## Phase 0: Mobilization and architecture decisions

**Objective:** Establish the contracts, supported platform choices, cost feasibility and migration rules on which later phases depend.

**Prerequisites:** Accepted dataset v1.1.0; this revised design ready for baseline review.

**Implementation steps**

1. Confirm team roles: platform owner, data engineering lead, ML lead, application lead, business owner (KPI and acceptance sign-off), security reviewer.
2. Record Architecture Decision Records in `platform/docs/adr/`:

| ADR | Decision | Recommended option |
| --- | --- | --- |
| ADR-01 | Workspace topology | Adopt existing Premium SERVERLESS healthcare workspace in East US; catalogs per environment; dedicated supporting RG; no classic fallback |
| ADR-02 | Infrastructure as code and resource ownership | Terraform for foundations; Bundles for supported app assets; one API adapter for other assets; resource-by-resource ownership and reconciliation register |
| ADR-03 | Region and supported software | Verify region, subscription entitlements, quotas, serverless connectivity and feature maturity; pin runtime/channel, providers and SDKs; record every Beta/preview dependency and supported fallback |
| ADR-04 | LLM access path for GPT-6 Luna | Verified Azure OpenAI exact model via Databricks gateway and UC service credential/managed identity in the second MCPP subscription; preserve workspace region. Native ADI route is unavailable in this account. Complete remaining API, governance, price and fallback probes in Phase 2 and quality/cost evaluation in Phase 10 |
| ADR-05 | App framework | React front end with FastAPI back end for the agent, Autopilot and Command Center apps |
| ADR-06 | ML training location | Prototype, select features and tune locally; final training and scoring on Databricks serverless; full local training (hybrid path) if Phase 8 step 8.2 cost evaluation exceeds the threshold set here |
| ADR-07 | Autopilot remediation level | Automatic retry and repair runs; human approval for any data rewrite, restore or deletion |
| ADR-08 | Alert channels | Microsoft Teams for incidents, email for daily summaries |
| ADR-09 | RTI generator hosting | Databricks App with enforced maximum runtime (Phase 13) |
| ADR-10 | Operating model and spend boundaries | Local-first ₹20,000 budget; costed demo/sleep profiles; atomic application reservations and separately scoped native Genie controls, including identities, limits, prices, headroom and uncertain charges (sections 3.6–3.10) |
| ADR-11 | Delivery identity and temporal reconstruction | Manifest-scoped delivery keys, immutable source assertion/version keys, independent business/knowledge/availability time and snapshot/correction rules |
| ADR-12 | Authorization and copied data | Trusted Entra object-ID mappings, fail-closed facility scopes, per-app identities, retrieval ACLs, Lakebase policies, redacted audit/traces and revocation tests |
| ADR-13 | RTI processing, clock and recovery | Micro-batch Delta as the POC path, simulation/session clocks, source-instance checkpoints, durable generator/outbox state, late-event repair and Lakebase latency contract |
| ADR-14 | Business grains and predictive eligibility | Encounter-level cost scope, KPI denominators, 13 dispositions, M4/M5 first-available inpatient origins, M10 first-available pre-adjudication origin, field availability, disjoint holdouts and horizon-specific evaluation |
| ADR-15 | Gate and workload contracts | Dependency graph, descriptive evidence paths, execution/test matrix, required polling and optional-webhook probe outcomes, measured workloads, scope-change and rollback procedures |

3. Set the ₹20,000 build budget, the ₹6,000 monthly operating budget, the allocation in section 3.6 and the ML training cost threshold for ADR-06. Confirm regional unit prices for the SQL warehouse, serverless jobs, apps, Vector Search, Lakebase, Event Hubs and GPT-6 Luna tokens.
4. Define the gate format and measurement workloads (sections 2.1 and 3.9). Publish source/table dependency, delivery/temporal, KPI-grain, feature-eligibility and resource-ownership matrices. Record known unsupported prospective cases explicitly; no accepted batch source is changed by this plan.
5. Obtain dated official capability and regional quota evidence for required features and the chosen LLM API. Where a tenant-level probe needs the workspace, specify the exact low-cost Phase 2 probe, cleanup and blocking result. No Phase 3 onboarding begins until these probes pass; documentation availability alone is not a successful tenant test.

**Deliverables:** Fifteen ADRs, costed test plan, budgets and allocation, RACI, contract/dependency matrices, pinned compatibility manifest, probe plan and gate template.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 0.1 | ADR-01 to ADR-15 recorded and approved | 15 of 15; explicit source/history, security, ML eligibility, RTI, rollback and resource ownership choices |
| 0.2 | Region, entitlements and API contracts supported | Dated official evidence, quotas, maturity/versions and tenant probe plan for every required capability; unresolved availability blocks provisioning |
| 0.3 | Build and operating budgets feasible | Regional priced workload totals, billing tails, contingency and ADR-06 threshold recorded; estimate fits ₹20,000 and the chosen ₹6,000 monthly profile |
| 0.4 | Acceptance and dependency contracts frozen | All 25 source tables mapped; 13 dispositions with first-availability decision cutoffs; spend-control scopes/limits and required-vs-optional probe matrix approved alongside the test/environment workloads |

---

## Phase 1: Azure infrastructure provisioning

**Objective:** Provision only the Azure resources needed for Phases 2 to 12. Retain and reconcile the existing workspace and authorized prerequisite resources. Event Hubs is deferred to Phase 13; the sole Azure OpenAI exception is the tested exact Luna prerequisite route in section 3.1.

**Prerequisites:** Phase 0 gate; Azure subscription Owner or Contributor plus User Access Administrator rights, and the required Entra/Databricks account and metastore administration permissions. Confirm each scope separately; subscription Contributor alone cannot provision every group or UC account object.

**Dependencies:** ADR-01, ADR-02, ADR-03.

**Implementation steps** (Terraform under `platform/infra/foundation/` and `platform/infra/model-access/`; workspace objects under `platform/infra/workspace/` when introduced)

1. Resource group `rg-hcp-<env>` with tags `project`, `owner`, `costcenter`, `environment`.
2. ADLS Gen2 storage account (hierarchical namespace on), containers `uc-managed`, `landing`, `checkpoints`. Lifecycle rule for landing files older than 90 days.
3. Azure Key Vault for unavoidable secrets; prefer federated CI/OAuth and managed identities. Terraform state is encrypted, access-restricted and never committed; no credentials in plan output or evidence.
4. Adopt and verify the existing Premium SERVERLESS workspace specified in section 3.1; do not provision a replacement. Confirm serverless access to required storage, endpoints and secrets. Real-data network isolation, encryption and workspace topology are a separate prerequisite review, not implied by this POC gate.
5. Access Connector for Azure Databricks (managed identity) with Storage Blob Data Contributor on the storage account.
6. Unity Catalog: verify the existing East US metastore assignment; create the healthcare storage credential from the dedicated access connector and external locations for `uc-managed` and `landing`. The shared metastore owner was explicitly changed to the existing human platform administrator during prerequisite remediation; preserve that recorded governance approval and do not repeat ownership changes in routine deployment.
7. Entra ID: create groups `hcp-platform-admins`, `hcp-data-engineers`, `hcp-data-scientists`, `hcp-analysts`, `hcp-clinical`, `hcp-finance`, `hcp-operations`, `hcp-auditors`; enable automatic identity management or SCIM provisioning.
8. Foundation service principals: `sp-hcp-cicd` (deployments), `sp-hcp-jobs` (data jobs), `sp-hcp-validation` (independent answer-key checks). Each Databricks App later receives its own platform-created service principal; these cannot be replaced by a shared `sp-hcp-apps`. Grant each app only its declared resources. See [Databricks Apps authorization](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/auth).
9. Azure budgets and cumulative build ledger per section 3.6; monthly budget ₹6,000 with alerts at 50%, 80% and 100%. Alerts go to the platform owner by email.
10. Skip Log Analytics for the POC. Use operational Jobs/Pipelines API polling for timely signals, with job-notification webhooks into the Autopilot app only if the Phase 2 probe proves authenticated delivery, and system tables for historical analysis, not a real-time detection promise.

**Deliverables:** Terraform modules and state, provisioned resources, access connector, external locations, groups, service principals, budget.

**Testing:** `terraform plan` shows no drift after apply; a test notebook (Phase 2) reads and writes the landing external location using the storage credential.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 1.1 | New healthcare resources created from code; existing workspace adopted | `terraform plan` = 0 changes; workspace identity, SERVERLESS mode and reference-only ownership verified |
| 1.2 | Unity Catalog metastore attached; storage credential and 2 external locations validated | Validation passes |
| 1.3 | Foundation identities exist | 8 groups and 3 named foundation principals; app identities provisioned per app later |
| 1.4 | Budget alerts configured | Build budget with 4 alerts; monthly budget with 3 alerts |
| 1.5 | No Event Hubs, NAT gateway, Log Analytics or duplicate workspace resources | 0 deployed; the documented exact-model prerequisite exception is the sole Azure OpenAI deployment, keyless and pay per token |

---

## Phase 2: Databricks platform foundation and CI/CD

**Objective:** A governed, repeatable workspace where every later asset is deployed from Git.

**Prerequisites:** Phase 1 gate.

**Implementation steps**

1. **Catalogs and schemas (Terraform):** create `hc_dev`, `hc_test`, `hc_prod`, `hc_ops` with managed storage on `uc-managed`; create the schemas in section 3.2; create volume `landing.raw` as an external volume on the landing container.
2. **Grants (Terraform):** least privilege per group and layer, as in section 15.4. `sp-hcp-jobs` writes pipeline outputs but cannot read the answer key; `sp-hcp-validation` reads the oracle and published outputs and cannot write pipeline business tables. No business-user read grants before the masking/filtering path is tested.
3. **Protection at creation:** define governed tags, baseline masks and fail-closed facility policies before onboarding. Build an admin-managed `hc_ops.security.principal_scope` mapping verified Entra object IDs to synthetic worker/persona identities and allowed facilities. Synthetic Workday `access_scope` rows are test inputs to an approved mapping, never automatic cloud authorization. Deny missing, ambiguous, expired or revoked mappings. Use ABAC only if supported and approved in ADR-03; otherwise use explicit masks/row filters or secured views with equivalent tests.
4. **Compute policies:** serverless notebooks, jobs and pipelines only in the adopted SERVERLESS workspace. Do not create classic cluster policies or assume subscription VM quota is a serverless quota. Verify serverless workload and service limits through the required tenant probes.
5. **Budget policies:** one per component (`medallion`, `ml`, `agent`, `autopilot`, `genie`, `rti`), assigned to service principals and groups.
6. **SQL warehouse (Terraform `databricks_sql_endpoint`):** serverless, 2X-Small, `auto_stop_mins = 5`, `min_num_clusters = 1`, `max_num_clusters = 1` in dev and test, 2 in prod.
7. **System tables:** enable `system.billing`, `system.access`, `system.lakeflow`, `system.compute` and lineage system tables; grant read to `hcp-platform-admins` and `sp-hcp-jobs`.
8. **Repository and bundle:** create the layout in section 3.3; `databricks.yml` with targets `dev`, `test`, `prod`; variables for catalog, warehouse ID and service principal.
9. **Shared library `hcp`:** logging, configuration, time-zone helpers, versioned contracts, authorization/query clients, lineage, DQ and citation types; shared by jobs and apps. Remediation credentials are isolated from read-only app clients.
10. **CI/CD (GitHub Actions):** PRs run local lint/unit/contract tests and bundle validation. Approved funded merge windows deploy to dev and run targeted integration tests; phase gates deploy changed assets to test and execute their prescribed suite. Prod deployment is a release approval after the applicable gate. Store the environment/test selection and cost estimate in CI evidence; do not wake compute on every merge.
11. **Coding standards:** Python formatting and linting, SQL style, notebook policy (notebooks only for exploration; production logic in modules).
12. **Local development environment:** pinned Python 3.12, PySpark and Delta Lake in Ubuntu WSL on this Windows machine, with equivalent Linux CI. The native Windows environment supports SDK/control-plane tooling; Spark/Delta execution uses Linux to avoid unofficial Hadoop Windows binaries. Install the `hcp` package when introduced; local fixtures read the answer key from `data/releases/healthcare-synthetic-v1.1.0/dataset/canonical/`. Every module runs locally before deployment (section 3.6, rule 1).
13. **Sleep and wake controller:** deploy control-plane `platform_down`, `platform_up` and externally scheduled `platform_guard` per section 3.7. Start with schedules, warehouse and durable state; later phases add lifecycle actions. Guard never runs a Databricks workload to check sleep.
14. **Capability smoke probes:** execute the bounded ADR-03/04 tenant checks for serverless storage/SQL, Apps user authorization, the exact GPT-6 Luna Responses tool-call round trip with gateway attribution/controls, registry/serving, search, Lakebase create/read/sync/resume, and authenticated Jobs/Pipelines API polling. These are **required** probes. Use a tiny failed-job fixture to prove scoped status retrieval and a polling detection path within 15 wall-clock minutes; the complete Autopilot fault suite remains Phase 7. Use minimum fixtures, restore least privilege and remove temporary billable resources. An unsupported required capability blocks Phase 3 until the approved dependency/cost contract is revised.
15. **Optional inbound webhook probe:** separately attempt authenticated job-notification delivery to a protected temporary app handler. Record `PASS` if supported and secure; otherwise record `UNSUPPORTED_DISABLED`, the incompatibility evidence, disabled/removed route and the passing required API-polling evidence. This outcome is explicitly allowed without a scope exception. Never leave an anonymous or unsuccessfully authenticated receiver enabled. An insecure enabled route, missing required polling evidence or an unresolved security failure is `FAIL` and blocks the gate. Retain original failed-attempt evidence; do not relabel an unsafe configuration as a passed probe. Optional inbound webhooks are independent of the required outbound Teams/email alerts.

Bundle excerpt:

```yaml
bundle:
  name: hcp
variables:
  catalog: { default: hc_dev }
  warehouse_id: { description: Serverless SQL warehouse with 5-minute auto-stop }
targets:
  dev:  { mode: development, default: true, variables: { catalog: hc_dev } }
  test: { variables: { catalog: hc_test } }
  prod: { mode: production, variables: { catalog: hc_prod } }
```

**Deliverables:** Catalogs, schemas, volume, grants, tags, policies, warehouse, system tables, repository skeleton, wheel, CI/CD workflows.

**Testing:** CI pipeline runs green end to end on an empty bundle; a test user in each group verifies expected allow and deny on each schema.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 2.1 | Bundle deploys to dev and test from CI with no manual steps | 2 successful deployments |
| 2.2 | SQL warehouse is serverless with 5-minute auto-stop | Configuration verified; stops within 6 minutes of last query |
| 2.3 | Grant matrix verified | 100% of allow/deny test cases pass |
| 2.4 | System tables readable | Queries on billing, lakeflow and lineage tables succeed |
| 2.5 | No compute running when idle | 0 running clusters or warehouses 15 minutes after last activity |
| 2.6 | Sleep and wake work | External guard confirms 0 running workload compute without waking it; wake restores only the declared demo profile |
| 2.7 | Local development works | Unit tests pass locally and in CI with the same results |
| 2.8 | Required capabilities and optional webhook disposition verified | All required probes pass, including authenticated API polling; optional webhook is `PASS` or evidenced `UNSUPPORTED_DISABLED` with polling fallback passed and no exposed receiver/security finding; versions, controls, cost and cleanup recorded |

---

## Phase 3: Synthetic data release and data onboarding

**Objective:** Place the accepted dataset in Databricks exactly as delivered, and publish the answer key for reconciliation.

**Synthetic data generation status:** Complete. The generation programme (synthetic data plan Phases 0–9 and the v1.1.0 behaviour revision) produced, validated, certified and accepted `healthcare-synthetic-v1.1.0`. No further batch generation is planned. Continuous generation for RTI is built in Phase 13.

**Prerequisites:** Phase 2 gate.

**Implementation steps**

1. Verify the package locally before upload:
   `python -m release_tooling.cli verify --package data/releases/healthcare-synthetic-v1.1.0 --descriptor-sha256 c36a9b7841743057be2f6993a27790c82a170c847399687a0c2647b5b9167af5`
2. Upload `native/valid/` to `/Volumes/<catalog>/landing/raw/v1.1.0/valid/` and `native/challenges/` to `/Volumes/hc_test/landing/raw/v1.1.0/challenges/` (challenges only in test) with the Databricks CLI or AzCopy, preserving folder structure.
3. Upload `native/manifest.json`, `native/source-dictionary.json` and `native/challenge-manifest.json` alongside.
4. Load the 25 canonical `.jsonl` tables into `reference.answer_<table>`, owned by the validation/deployment role and read only by `sp-hcp-validation`. Data jobs, Gold/feature/model builders and apps have no oracle grant. Independent validation publishes pass/fail and bounded non-PHI aggregates; runtime pipelines never read the oracle.
5. Build `reference.source_contract` from `source-dictionary.json`: one row per feed and column with source name, type, nullability, key role and canonical mapping.
6. Build `reference.delivery_expectation` from `manifest.json`: one row per delivery with release, source, feed, manifest file/delivery identity, path, scope/period, expected rows, checksum, availability time and role (PRIMARY or SNAPSHOT). Hash is an integrity attribute, not the delivery key.
7. Load the facility calendar and America/Chicago time zone reference (`reference.calendar_local`).
8. Run an in-workspace verification job: file count, per-file SHA256 against the manifest, answer key row counts.

**Deliverables:** Landing files, reference tables, verification job and report.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 3.1 | Local package verification passes | `PASSED` for descriptor `c36a9b78…` |
| 3.2 | All delivery files in landing with matching checksums | 3,445 of 3,445 (plus dictionaries and reports as listed in the manifest) |
| 3.3 | Challenge sets in test landing | 19 of 19 sets, 22 record copies |
| 3.4 | Answer key loaded | 25 tables, 1,937,925 rows |
| 3.5 | Source contract and delivery expectation tables complete | Every feed and file in the manifest represented |

---

## Phase 4: Bronze ingestion

**Objective:** Capture every delivered record with full lineage, detect delivery problems at the door, and never lose or double-count data.

**Prerequisites:** Phase 3 gate.

**Implementation steps**

1. **Ingestion metadata:** `reference.source_contract` drives ingestion. No per-feed hand-written code.
2. **Lakeflow Declarative Pipeline `bronze_ingest`:** one streaming table per native feed (25 primary feeds plus key crosswalk and snapshot feeds) using Auto Loader (`cloudFiles`) with:
   - format per feed (JSON lines for `ehr` and `adt-bed` message envelopes, CSV for `workday`, `roster-time`, `axiom`, `revenue-cycle`, `finance-erp`, `supply-pharmacy`);
   - schema hints from the source contract, `rescuedDataColumn`, schema evolution in rescue mode;
   - all values read as strings in Bronze (types are applied in Silver);
   - lineage columns from section 3.4.
3. **Delivery ledger `bronze.delivery_ledger`:** one row per expected delivery identity, with separate append-only arrival attempts. Join on `(release_id, source_system, feed, manifest_delivery_id)` or a documented equivalent including path, period and scope. Retain zero-row/header-only deliveries and their timestamps. Flag missing, late, repeated attempts, checksum/row-count differences and foreign releases without suppressing distinct deliveries.
4. **Quarantine `bronze.quarantine`:** records and files that break the contract (unparseable, missing required key, wrong column set, wrong decimal format) with `reason_code`, `rule_id`, `source_file` and the raw payload.
5. **Duplicate protection:** replay of the *same delivery identity and content* does not append another business payload; changed content for an immutable delivery identity is quarantined. Distinct delivery identities remain distinct even when SHA256 matches: v1.1.0 has 3,445 valid files but only 1,001 distinct hashes, including legitimate repeated empty Workday extracts. Preserve raw observations and snapshot provenance. Logical record/version deduplication in Silver uses a feed-specific key, including source namespace, entity/assertion ID and version or event identity; a source entity ID alone must not collapse revisions. Identical keys with different immutable payload hashes are conflicts, not duplicates.
6. **Challenge handling (test only):** map each challenge set to its expected outcome:

| Challenge | Expected Bronze outcome |
| --- | --- |
| f-corrupt | File quarantined, reason `CORRUPT_FILE` |
| f-schema | File quarantined, reason `SCHEMA_MISMATCH` |
| f-row-count | Ledger flags `ROW_COUNT_MISMATCH` |
| f-decimal | Records quarantined, reason `INVALID_DECIMAL` |
| f-required-key | Records quarantined, reason `MISSING_REQUIRED_KEY` |
| f-unmapped | Passed to Silver, which quarantines on key resolution |
| full-snapshot-reload | Ingested; Silver deduplicates |
| retroactive-worker-revision-1..3, revoked-grant-revision-1..3, conflicting-immutable-version | Ingested; Silver applies or rejects per history rules |
| bed-original, bed-correction | Ingested; Silver applies the correction |
| f-control, valid-financial-control, valid-financial-replacement | Ingested as valid control deliveries |

7. **Orchestration:** Lakeflow Job `medallion_daily` task 1 runs `bronze_ingest` in a bounded scheduled replay or on-demand window. File-arrival triggers are enabled only for the chosen awake replay profile; static demos do not re-ingest history. Retries: 2 with backoff; timeout: 60 minutes.
8. **Run telemetry:** each update writes counts per feed to `dq.ingest_metrics` for the Autopilot.

**Deliverables:** Bronze pipeline, ledger, quarantine, challenge mapping, job, metrics table, runbook "Reprocess a delivery".

**Testing:** parsers/reason codes, all valid deliveries, each challenge set, same-delivery replay, distinct dated deliveries with identical hashes, zero-row files, valid revisions and conflicting payloads. Record both ledger identity counts and payload row counts; new arrival-attempt audit entries are permitted on replay.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 4.1 | All valid deliveries ingested | 3,445 of 3,445 files in ledger with status `OK` |
| 4.2 | Bronze row counts equal manifest expected rows | 100% of files, 0 differences |
| 4.3 | Every challenge set produces its expected outcome | 19 of 19 |
| 4.4 | Delivery identity and replay correct | Replaying the same deliveries adds 0 business payload rows; all distinct equal-hash and empty deliveries retained with their own ledger identities; immutable conflicts quarantined |
| 4.5 | No data lost to rescue | Rescued-data column null on 100% of valid records |
| 4.6 | Full initial load duration and cost recorded | Duration under 45 minutes; cost logged in gate |

---

## Phase 5: Silver conformance and data quality

**Objective:** Produce 25 conformed, typed, historized and validated tables that reproduce the canonical answer key exactly.

**Prerequisites:** Phase 4 gate.

**Implementation steps** (in domain waves A to E, section 2.2)

1. **Decoding:** port the decoding logic of `source_reader.py`: `\N` to null, compact timestamps (`20230107082327+0000`) to UTC timestamps, Axiom period formats, decimal precision, booleans `Y/N`.
2. **Key resolution:** join each feed's `*.keys.csv` crosswalk to replace source-scoped references (for example `ADT_BED-BED_LOCATION-…`) with canonical IDs. Unresolved keys go to `silver.quarantine` with `UNMAPPED_KEY`.
3. **Source history preservation:** reproduce each canonical assertion/version key and its original business-valid, source-knowledge and export-availability timestamps. Persist native version identifiers, lineage and correction links; do not recompute canonical intervals from ingestion order. Use deterministic batch `MERGE` on immutable assertion keys with conflict checks for these 25 tables. Build separately named current/as-of projections from this preserved history. Ordinary SCD2 `AUTO CDC` sequenced only by knowledge time is not a substitute for two timelines. Bitemporal AUTO CDC is a separate Beta capability and is excluded from the baseline unless ADR-03 explicitly approves it and proves exact canonical equivalence. See [bitemporal AUTO CDC semantics](https://learn.microsoft.com/en-us/azure/databricks/ldp/cdc-advanced).
4. **Corrections and revisions:** bed `CORRECTION` events supersede the corrected event; retroactive worker revisions and revoked grants add new knowledge versions; conflicting immutable versions are rejected to quarantine.
5. **Snapshot reloads:** deduplicate full snapshots against already-known versions.
6. **Local time:** add `_local` columns using America/Chicago with correct daylight-saving handling.
7. **Protection at creation:** apply PHI tags and the Phase 2 masks/row policies to names, birth date, address, MRN, member ID, test email, phone and clinical text before granting read access. Raw payloads and quarantine receive the same protection. Tagging alone does not enforce a mask.
8. **Data quality rule catalog `dq.rule_catalog`:** map the 55 Phase 0 validation rules (identity, temporal, numeric, encounter, bed, staffing, inventory, claims, GL, Axiom) to expectations with `rule_id`, severity, owner and action:
   - `warn` (record kept, counted),
   - `drop` (record to quarantine),
   - `fail` (pipeline update fails).
9. **Rule results `dq.rule_results`:** per run, table and rule: evaluated, failed, sample keys.
10. **Reconciliation job `silver_reconcile`:** compare each Silver table to `reference.answer_<table>` on canonical business columns using the certified normalization/hash contract: row counts, primary-key sets and content. Exclude only the explicitly documented non-business generation/ETL metadata; do not hide substantive differences in a permissive normalizer. Report every difference with protected keys.
11. **Orchestration:** `medallion_daily` task 2 runs `silver_conform` after Bronze; a separate job running as `sp-hcp-validation` executes `silver_reconcile` at gates and on changed inputs/code. Job-level run-as identities do not become per-task identities by convention. The static demo does not schedule weekly oracle reads or recompute certified history.
12. **Time semantics:** document business effective time, source knowledge time, export availability and actual platform ingestion independently. Historical backtests use the explicitly modeled source/export availability clock; they do not claim observed 2023–2025 platform arrival times. Live decisions must also respect actual ingestion/serving availability. Late export or a retroactive revision must never appear earlier in a point-in-time view.

**Deliverables:** Silver pipeline, 25 tables, quarantine, rule catalog, rule results, reconciliation job and report, runbooks.

**Testing:** every decoder/assertion merge; primary-key and normalized-content reconciliation; snapshots, identical delivery hashes, `f-unmapped`, late and retroactive revisions, revoked scopes, conflicting immutable versions and bed corrections. Test both valid-time and knowledge/availability-time boundaries, replay in different arrival orders and March/November DST.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 5.1 | Silver equals the answer key | 25 of 25 tables; 1,937,925 rows; 0 unexplained differences |
| 5.2 | DQ rules implemented | 55 of 55 mapped; 0 `fail` violations on valid data |
| 5.3 | Challenge outcomes correct in Silver | All Silver-handled challenges match expected outcome |
| 5.4 | PHI protected before exposure | 100% tagged and effective masks/row policies or restricted raw access tested, including payload/quarantine |
| 5.5 | Idempotent and replayable | Full rerun produces identical table hashes |
| 5.6 | Temporal correctness | 0 DST errors; as-of results correct before/after revisions, export availability and revoked grants; canonical assertion/version IDs and intervals preserved |

---

## Phase 6: Gold, semantic layer, dashboards and access policies

**Objective:** Business-ready facts and dimensions, one definition per KPI, the first dashboards, and enforced data protection.

**Prerequisites:** Phase 5 gate.

**Implementation steps**

1. **Dimensions:** `dim_date`, `dim_hour`, `dim_facility`, `dim_unit`, `dim_bed`, `dim_service_line`, `dim_payer`, `dim_patient` (masked attributes), `dim_worker_role`, `dim_catalog_item`, `dim_cost_center`, `dim_denial_reason`.
2. **Facts (materialized views or batch tables):**

| Fact | Grain |
| --- | --- |
| `fact_encounter` | Visit, latest known state and timing milestones; retrospective current-state fact |
| `fact_ed_visit` | ED visit with LOS, disposition, LWBS |
| `fact_census_hourly`, `fact_census_daily` | Facility × unit × hour / day |
| `fact_bed_turnaround`, `fact_placement_wait` | Bed cycle / admission |
| `fact_appointment` | Booking with outcome |
| `fact_staffing_shift`, `fact_staffing_daily` | Shift / facility × unit × shift |
| `fact_inventory_daily` | Item × location × day |
| `fact_claim_lifecycle`, `fact_denial`, `fact_cash_weekly` | Claim / denial / payer × week |
| `fact_cost_to_care` | Encounter × accounting month × cost category for the selected allocation run's PATIENT allocations; patient/facility attributes joined without fan-out |
| `fact_cost_nonpatient` | Cost centre × accounting month × cost category for the selected allocation run's NONPATIENT allocations, which have no encounter; facility attributes joined without fan-out |
| `fact_plan_actual_forecast` | Facility × cost centre × account × month × scenario × vintage |

3. **Fan-out and economic rules:** aggregate to the declared grain before joins; select one allocation run per eligible posting and one finance vintage per series/scenario. Reconcile selected allocated costs, PATIENT allocations in `fact_cost_to_care` plus NONPATIENT allocations in `fact_cost_nonpatient`, to eligible GL expense pools in exact cents; no allocation is dropped for lacking an encounter. Patient/procedure costing requires an additional approved allocation model and must be labeled estimated; it is not a baseline fact. Define cost/margin as selected allocated expense and the explicitly matched revenue scope, not complete profitability. Keep claims, payments, AR balances and charges distinct, use the original claim identity across attempts, and do not sum incompatible stock units or balance snapshots.
4. **Point-in-time access:** implement tested SQL table-valued functions such as `semantic.encounter_asof(valid_at, known_at, available_at)` over preserved Silver assertions, plus reproducible feature snapshots. Intervals and tie-breakers are explicit; only versions known and available by the decision cutoff may be returned. Current-state Gold facts cannot reconstruct earlier knowledge. Materialize common snapshots if needed and retain source assertion IDs, query/definition version and cutoff clock in their lineage.
5. **Metric views (`semantic` schema):** about 40 KPIs with owner and description: occupancy, ALOS, boarding hours, LWBS rate, bed turnaround, placement wait, HPPD, RN absence rate, agency share, no-show rate, denial rate, clean-claim rate, appeal recovery, days in AR, cash collected, cost per case, margin per case, plan variance.
6. **UC SQL functions (`semantic`):** parameterized, read-only functions for the most common KPI queries; reused by Genie and the agent.
7. **Access policies:**
   - reuse the Phase 2 PHI masks and fail-closed policies; unmasked access is limited to clinical users in their authorized facilities and explicitly audited administrator/break-glass actions;
   - derive facility scopes from the trusted Entra mapping in `hc_ops.security`, with approved synthetic `access_scope` scenarios used to test effective dates and revocation;
   - auditors receive masked read-only datasets and redacted audit views, not unrestricted raw payloads; test the role matrix in section 15.4 across tables, dashboards, Genie and APIs.
8. **AI/BI dashboards:** Executive, Operations, Revenue cycle, Finance. Model performance is added in Phase 8.
9. **Orchestration:** replay task 4 refreshes Gold, task 5 dashboard datasets; validate the 06:00 America/Chicago SLA under the section 3.9 workload. Static demos read certified tables without daily refreshes.
10. **Reference KPI checks:** independent SQL over the answer key computes reference values for 20 key KPIs; Gold must match.

**Deliverables:** Gold tables, PIT views, metric views, UC functions, masks, row filters, four dashboards, KPI reference checks.

**Testing:** grain and uniqueness tests per fact; reconciliation Gold vs Silver totals; KPI reference checks; permission tests per group; dashboard load test.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 6.1 | Gold grains unique | 0 duplicate keys across all facts |
| 6.2 | KPIs match reference values | 20 of 20 within 0.01% relative tolerance with a declared absolute tolerance near zero; counts and money exact |
| 6.3 | Money and balance reconciliations | 0 unexplained differences (claims, cash, allocations, Axiom series) |
| 6.4 | PHI masked and facility filters enforced | 100% of permission test cases pass |
| 6.5 | Metric views owned and documented | 100% have owner and description |
| 6.6 | Dashboards responsive | Warm p95 tile load <5 seconds under the section 3.9 request/concurrency contract; cold-start result reported separately |
| 6.7 | Gold refresh SLA | Five representative consecutive scheduled-replay days complete by 06:00 local; input due times, DST, run costs and clock semantics recorded |

---

## Phase 7: DataOps Autopilot core app

**Objective:** A dedicated Databricks App that continuously shows the health of the platform and detects failures, data quality issues, schema drift, freshness and volume anomalies, and job failures.

**Prerequisites:** Phases 4, 5 and 6 gates; the core graph includes certified Gold and dashboards from the start.

**Implementation steps**

1. **Two telemetry paths, awake windows only:** a small operational worker polls authenticated Jobs/Pipelines APIs and delivery/DQ status at most every 2 minutes and persists incident evidence; polling is required and remains active even if webhooks pass. Enable the inbound webhook handler only for the Phase 2 `PASS` disposition; `UNSUPPORTED_DISABLED` uses polling alone and is not a failed phase prerequisite. Verify detection with webhooks disabled/unavailable and do not wait for them or delayed system tables. The separate `autopilot_collect` job archives/enriches telemetry every 15 minutes. Record signal, polling/startup and persistence delays; outbound Teams/email alert delivery remains required.

| Signal | Source |
| --- | --- |
| Job and task runs | Jobs API polling for operational detection, plus webhook notifications only if the Phase 2 probe proves authenticated delivery; `system.lakeflow` for historical reconciliation |
| Pipeline updates, expectation results, flow progress | Current update status/API and pipeline event logs, with observed publication lag |
| Deliveries | `bronze.delivery_ledger`, `bronze.quarantine` |
| Data quality | `dq.rule_results`, reconciliation reports |
| Table health | Delta history (last write, rows written), information schema (schema version) |
| Lineage | Deployment dependency graph for current impact; UC lineage system tables enrich historical evidence |
| Cost | Priced `system.billing.usage` and Azure cost ledger; label delayed/estimated values |
| Access | API/application authorization failures for current signals; `system.access.audit` for audit reconciliation |

2. **Platform graph `autopilot.node`, `autopilot.edge`:** nodes for source feed, landing folder, Bronze, Silver and Gold tables, metric views, dashboards (later: features, models, predictions, endpoints, Genie spaces, apps). Edges from lineage plus bundle resource definitions.
3. **SLOs per node `autopilot.slo`:** freshness/completeness against expected deliveries, validity, schema stability and a clock mode (`STATIC_CERTIFIED`, `SCHEDULED_REPLAY`, `LIVE`). Record signal availability and detection budget. Jobs system-table records are typically available within one hour, so they cannot alone satisfy a 15-minute detection gate. See [Jobs system-table availability](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/jobs).
4. **Detection rules:**
   - hard failures: failed run, failed pipeline update, `fail` expectation;
   - SLA breach: freshness beyond tier target;
   - volume anomaly: rows written outside a seasonal baseline (robust z-score above 4 by weekday);
   - schema drift: column set or type differs from `reference.source_contract` or the last good version;
   - DQ spike: rule failure rate above its baseline;
   - delivery problems from the ledger.
5. **Incidents `autopilot.incident`:** one incident per root event; related alerts grouped; status open, acknowledged, resolved.
6. **Databricks App `autopilot` (React + FastAPI):** health overview, incidents, DQ, freshness, deliveries and cost pages. The app's dedicated principal has narrowly scoped telemetry collection/write privileges; user-facing read APIs apply the caller's authorized scope and redact payload samples. Users cannot invoke the collector's write path. Later remediation uses a separate privileged executor, not this app identity.
7. **Cost dashboard:** spend by component and phase from `system.billing.usage`, with the build budget and monthly budget as reference lines.
8. **Sleep state:** use the control-plane state and awake mirror (section 3.7); pause both telemetry paths during sleep. On wake, verify static release integrity and expected-delivery/live SLOs, not wall-clock age of historical facts. Include both paths in sleep/wake and cost tests.

**Deliverables:** Collection job, telemetry tables, platform graph, detection rules, incident model, Autopilot app v1, cost dashboard, sleep-state handling.

**Testing:** inject 6 faults in test (missing file, schema change, corrupt file, killed job, failing expectation, overdue expected refresh). Include faults just after a polling boundary and deliberately delayed system tables. Replay seven clean operating days for false-positive testing; this is a bounded replay, not an unfunded week of continuous cloud compute.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 7.1 | Every Bronze, Silver and Gold table is a graph node with SLOs | 100% coverage |
| 7.2 | Injected faults detected | 6 of 6 within 15 wall-clock minutes of failure/due time using required API polling with inbound webhooks disabled/unavailable and delayed system tables; delay components recorded |
| 7.3 | False positives on clean replay | Fewer than 2 incidents across seven representative replay days; no age-only alerts on static certified data |
| 7.4 | App available and secured | Login via Entra ID; non-admin users cannot modify state |
| 7.5 | Cost of Autopilot collection | Under 5% of platform compute spend; within the section 3.6 allocation |
| 7.6 | Sleep state honoured | 0 collector runs or expected-inactivity incidents while asleep; external resource/security drift still alerts; full sweep within 30 minutes of waking |

---

## Phase 8: Forecasting and machine learning

**Objective:** Implement the supported forecasting/prediction portfolio with honest eligibility, baseline comparisons, uncertainty and monitored deployment. All 13 use cases receive a documented disposition; simulations, derived staffing and unsupported prospective cases are not counted as 13 independently trained production models.

**Prerequisites:** Phase 6 gate (Gold and PIT views); Phase 7 gate (model health monitoring hooks).

### 8.1 Use-case portfolio and eligibility

| # | Model | Grain · horizon | Candidate algorithms | Primary metric | Serving |
| --- | --- | --- | --- | --- | --- |
| M1 | ED arrivals | Facility × day (14 d); × hour (24 h) | Seasonal naive, NB-GLM, LightGBM (Poisson), Prophet benchmark | MASE, WAPE, 80% coverage | Batch |
| M2 | Inpatient admissions (elective + emergency) | Facility × service line × day (14 d) | NB-GLM / LightGBM with known history; elective admissions forecast from history, because booked schedules are never available at the forecast origin | WAPE, MASE | Batch |
| M3 | Census and occupancy | Facility × unit × hour (72 h) / day (14 d) | Monte Carlo stock-and-flow on M2 and M4; LightGBM quantile challenger | Pinball loss, Brier score for P(full) | Batch hourly |
| M4 | Remaining length of stay / expected discharge date | Active inpatient at first eligible available snapshot, then supported updates | Conditional survival/AFT, Cox, LightGBM on remaining log-LOS | Remaining-LOS concordance/MAE and interval coverage | Online + batch after eligibility |
| M5 | Discharge within 24 h | Active inpatient × eligible as-of hour | Logistic regression, LightGBM | AUC, Brier from the decision origin | Batch hourly after eligibility |
| M6 | Staffing demand | Facility × unit × shift (14 d) | Derived from M3 patient-hours and the 8.0 HPPD generation rule; explicit shift/productive-hours conversion | Arithmetic, units, rounding and uncertainty propagation | Batch derived product |
| M7 | RN absence | Facility × week | Poisson GLM with winter and surge effects | MASE | Batch |
| M8 | Supply consumption | Item × location × day (28 d) | Croston/TSB, LightGBM with patient-days | WAPE, stock-out recall | Batch |
| M9 | Cash collections | Payer type × week (12 w) | Lag-distribution model, SARIMAX residual | WAPE | Batch weekly |
| M10 | Denial risk + denial volume | Pending claim at first eligible available snapshot; payer × month for volume | Logistic regression, LightGBM; ETS for volume | AUC, Brier, lift @ top decile at the declared cutoff | Online + batch after eligibility |
| M11 | Appointment no-show (retrospective-only in v1.1.0) | Per completed booking/outcome record | Optional retrospective logistic/LightGBM benchmark, clearly labeled unavailable for pre-visit prediction | Descriptive/retrospective metrics only | No prospective endpoint |
| M12 | 30-day readmission | Per discharge | Logistic regression, LightGBM | AUC, calibration | Batch daily |
| M13 | Monthly finance | Facility × cost centre × account × month (1–3 m supported where eligible; 12 m exploratory) | Seasonal naive, simple pooled ETS/ARIMA; hierarchical reconciliation | MASE by horizon, reconciliation error | Batch monthly |

Before training, publish `ml.use_case_eligibility` and `ml.feature_availability` with decision origin, target/label window, entity and grain, field-level known/export availability, source history coverage, sample counts, minimum support, baseline, metric threshold and disposition: `ELIGIBLE`, `BASELINE_ONLY`, `DERIVED`, `RETROSPECTIVE_ONLY` or `INSUFFICIENT_DATA`. Endpoints and agents expose only the supported disposition. A baseline may be the champion when no challenger improves it; publishing an unsupported learned model is not required to pass.

- **M11:** all 25,800 attended/no-show records arrive after the scheduled start. Historical `booked_at` does not supply earlier platform knowledge. Deliver the limitation, availability audit and optional retrospective benchmark, not an online risk service. A future certified dataset with pre-visit booking/change deliveries is a separately approved extension; this phase does not regenerate accepted data.
- **M5:** exclude medically-ready status because readiness is not available before discharge in this release. Audit all other snapshot fields similarly. M4/M5 may use only admission or later snapshots actually known at the selected decision origin; post-discharge facts cannot enter predictors.
- **M1/M2/M8:** calendar features are known in advance; realized weather/respiratory indices and future patient-days are not. Use available lagged observations, upstream forecasts or explicitly named scenario inputs. All 4,800 elective-admission bookings become visible only after their scheduled start, so booked elective schedules are never model inputs; M2 forecasts elective admissions from history. Compare models at the same information cutoff.
- **M3/M6:** version the simulation and deterministic staffing rules and propagate upstream uncertainty. M3 takes elective inflow from M2, not bookings. Eligible existing inpatients use conditional remaining LOS from M4; future admissions and patients awaiting M4 eligibility use a separately versioned cohort LOS prior estimated only from completed stays available at the forecast origin, conditioned on elapsed stay where applicable. Never invoke M4 at an unsupported admission-instant origin or apply its remaining-LOS output as an unconditional total LOS. Cite the model/prior used per simulation cohort. Do not add an uncalibrated acuity multiplier to fixed HPPD or call roster agreement learned accuracy. Compare M3 with persistence/stock-and-flow baselines; validate M3 capacity/state and M6 units, rounding and conservation.
- **M13:** 36 monthly points per series do not establish reliable annual forecasts for every cost center/account. Pool or aggregate sparse series, limit seasonal complexity, keep scenarios/vintages separate, and label 12-month outputs exploratory with the number of independent full-horizon evaluations. Do not promise a tuned 12-month model from a six-month holdout.

#### Decision-time and feature-availability contract

For M4/M5/M10, `first_source_available_at` is the earliest usable source assertion's modeled knowledge/export availability. `first_eligible_at` is the earliest time the header **and every required input** are known/available under that use case's feature contract; optional inputs may be missing only when the trained missing-value policy permits it. Historical replay uses the modeled source clock. Live inference additionally waits for actual ingestion, validated feature computation and serving-copy readiness. Do not backdate eligibility to `admitted_at`, `first_submitted_at` or the nominal business event time.

| Product | Frozen decision origin and target | No eligible input/window |
| --- | --- | --- |
| M4 | First eligible inpatient snapshot, never earlier than the header's admission +1 h 45 min modeled availability in v1.1.0. Predict **remaining LOS conditional on still being admitted and elapsed stay at `decision_at`**; `expected_discharge_at = decision_at + predicted_remaining_duration`. Training/baselines/evaluation use this origin/target; later supported snapshots keep the same conditional semantics. | Before eligibility return `NOT_YET_AVAILABLE`; known discharged encounters return `ALREADY_RESOLVED`. No admission-instant forecast is claimed. |
| M5 | First UTC hourly scoring boundary at or after inpatient eligibility, followed by supported active-stay snapshots. The label is discharge in `(decision_at, decision_at +24 h]`; an earlier business-time bucket must not be populated by rounding the availability cutoff down. | No predictions before eligibility or for known completed stays; exclude unavailable medically-ready data throughout. |
| M10 risk | First eligible available claim snapshot with known pending status before the targeted adjudication; `first_submitted_at` is context, **not** the scoring timestamp. Fix the original-claim/attempt and first-adjudication target definition in ADR-14. | No score at submission before delivery. Already known adjudicated/denied/paid cases return `ALREADY_RESOLVED`; cases without an auditable pre-outcome window are reported separately rather than backdated into prospective validation. |

Keep `first_source_available_at`, `first_eligible_at`, `decision_at`, feature cutoff, actual `scored_at` and clock mode in feature/prediction lineage and tool responses. Required-feature readiness can make a decision later than the header alone. Labels and follow-up must mature after the recorded origin; final outcomes are not used as predictors or to authorize a live lookup. The M10 volume forecast keeps its existing payer/month origin and availability-filtered aggregates.

Boundary tests must reject a request immediately before eligibility and permit it only at/after the full required-input cutoff, with separate delayed-feature/serving-sync and already-resolved cases. Verify hourly ceiling/DST behavior, remaining-LOS conditioning, target windows and missing-input policy. Fixed historical source delays are replay assumptions, not measured cloud pipeline latency. Immediate admission/submission scoring with richer RTI feeds is a separately versioned eligibility/source-contract extension with its own training/evaluation gate; it is excluded from this baseline and does not require regenerating the accepted dataset.

### 8.2 Training location evaluation (cost)

0. Develop eligible candidates locally first. Full feature pipelines still consume native-decoded Silver/Gold; the answer key is only a test oracle. Estimate cloud cost for the complete ML gate, including validation and serving, not just fitting.
1. Implement M1 and M10 end to end on Databricks serverless jobs first.
2. Measure bounded M1/M10 training/backtest runs and the feature, registration, verification, scoring and endpoint costs from priced usage. Use a small pilot search; run a 30-trial cloud search only when its marginal value and budget are approved in ADR-06.
3. Project the complete build cost and, separately, a funded operating scenario for eligible trained models. Derived products and retrospective-only cases have different workloads; a static monthly demo requires no repeated training.
4. If the projection exceeds the ADR-06 threshold, switch to the **hybrid path** below for the expensive models. Record the decision and numbers in ADR-06.

**Hybrid path (local training, Databricks registration and serving):**

| Requirement | How |
| --- | --- |
| Governed training data | Export training sets from UC feature tables at a recorded Delta version to Parquet in a volume, then download; record table name, version and SHA256 |
| Same environment | Pinned `uv`/conda lock shared by local training and serving |
| Experiment tracking | `mlflow.set_tracking_uri("databricks")`; runs logged to the workspace experiment with tag `training_location=local` |
| Lineage | `mlflow.log_input` with the UC table reference and version |
| Registration | `mlflow.set_registry_uri("databricks-uc")`; register to `<catalog>.ml.<model>` with signature and input example |
| Verification | Databricks job re-scores the holdout with the registered model; predictions must match local results within tolerance before an alias is assigned |
| Retraining | Owner-run on the agreed cadence; Autopilot flags models whose training data version is older than allowed |

Select the cloud or hybrid path using the measured pilot and remaining total budget, not a presumption that training or hybrid verification is free. Record export permissions and delete local governed training copies after the agreed retention period.

### 8.3 Lifecycle steps (each supported product)

1. **Data preparation and split manifest:** build eligible training sets from governed as-of functions and feature tables, preserving field availability and source assertion IDs. For M1–M12 use initial training in 2023–2024, model/feature selection at rolling origins in January–June 2025, and one locked July–December 2025 final holdout. Keep each target window and its required outcome availability inside its partition; purge/embargo overlapping horizons and repeated patient/claim follow-up as needed. Survival models handle censoring at the cutoff; readmission requires mature 30-day follow-up and is limited to observable hospitals. For M13 select simple candidates using pre-2025 rolling folds, refit through December 2024, and reserve all of 2025 for final evaluation, including the single full 12-month origin. Record limited power; do not tune on that holdout. Forecast origins lacking full observed targets do not count as full-horizon tests.
2. **Feature engineering:** UC feature tables:

| Feature table | Primary key · timestamp key | Example features |
| --- | --- | --- |
| `features.daily_demand` | facility, forecast_origin, target_date | Calendar terms, available lags/rolling means, lagged respiratory observations or separately forecast covariates; no booked electives, which are never available at the forecast origin on this release |
| `features.inpatient_snapshot` | encounter, decision_at | Eligible active-stay snapshot; elapsed LOS, known acuity/pathway/service line/conditions/orders, ICU flag and weekday; first-source/required-input availability retained, no unavailable readiness or final outcome |
| `features.claim_at_first_availability` | original claim, decision_at | Required claim inputs available by the cutoff: payer/auth/setting, known LOS/line count, billing and submission-to-availability lag, historical payer denials; preserve original submission time separately |
| `features.booking_retrospective` | appointment, export_available_at | Audited descriptive/retrospective fields and availability limitation; not a pre-visit online feature table |
| `features.discharge_history` | encounter, discharged_at | Prior admissions, LOS, diagnosis group, discharge disposition |

   Eligible online copies for M4 and M10 are introduced in Phase 10. Include source/required-input availability, decision origin, feature cutoff and sync/serving readiness; reject early/missing/stale snapshots with the documented status. Phase 8 endpoints use the same validated decision-time contract and authorized snapshots. M11 is excluded. Facility authorization applies even when a shared serving identity performs the lookup.
3. **Feature selection:** start from a domain-driven candidate list; remove leakage candidates by audit; for GLMs drop collinear features (VIF above 10); for tree models use permutation importance and SHAP stability across folds; keep the smallest set within 1% of the best backtest score.
4. **Model selection:** compare baseline, statistical and gradient-boosted candidates per model on the same backtest folds; pick by primary metric, calibration and simplicity; record the comparison in the model card.
5. **Hyperparameter tuning:** up to 30 Optuna trials for eligible learned candidates, early stopping and a measured time/cost limit. Baselines, simulations and deterministic products do not receive artificial searches. Tune on selection folds only.
6. **Validation and evaluation:** use the locked split manifest; horizon-specific error/coverage, naive/base-rate comparators, calibration and age/sex/payer slices with confidence intervals and sample counts. A classifier calibration gate requires at least 200 held-out cases and 30 positive and negative outcomes at the declared evaluation grain; sparse slices are reported as underpowered, not passed. Forecast interval calibration uses sufficiently many held-out origins with block-aware uncertainty; otherwise aggregate, shorten the supported horizon or publish insufficient support. Inject unavailable/future fields to prove they are rejected; randomized features alone are not a point-in-time eligibility test.
7. **Experiment tracking:** MLflow experiment per model `/Shared/hcp/ml/<model>`; tags `dataset_version=1.1.0`, feature table versions, Git SHA, `training_location`.
8. **Registration:** register deployable fitted artifacts in UC with signatures, examples and product cards. Use a champion alias for the selected eligible model or baseline; challenger exists only when a candidate is available. Version M3 simulation/M6 rules, code/configuration and upstream model references as reproducible artifacts. Record retrospective-only/unsupported cases in the portfolio register; do not fabricate a registered champion for every use-case number.
9. **Deployment:** batch scoring jobs and eligible M4/M10 serving patterns, with scale to zero and small workload size. Grant entity-lookup endpoint access only to the trusted authorization broker/approved jobs; UI users cannot bypass facility checks by querying a shared endpoint directly. If a pattern fails the eligibility audit, document the unsupported disposition instead of deploying it. Future M11 deployment requires a new prospective-data gate.
10. **Inference contract:** `pred.*` carries product ID/disposition, entity grain, UTC target/local zone, horizon/unit, decision origin/clock, source and required-input availability, feature cutoff, scored time, quantiles/probability, optional supported reasons, artifact/model version, resolved alias-at-run, feature snapshot/upstream versions, Git SHA and run ID. M4/M5/M10 enforce the section 8.1 origin and active/pending-state contract; non-eligible statuses do not publish a prospective prediction row. Validate non-negative counts, ordered quantiles and probabilities in [0,1]. Derived products cite rule/simulation versions; retrospective metrics are not prospective predictions.
11. **Monitoring:** join predictions to mature outcomes with explicit label availability; track both predictive and data-eligibility health. Publish accuracy/calibration, drift, delayed labels, feature age and supported status to Autopilot. M3/M6 also monitor invariant failures and upstream dependencies. Static demos use stored backtests and health evidence; no fictitious current accuracy/drift from unchanged 2025 data.
12. **Retraining and promotion:** schedules remain disabled in static demos. In funded replay/live mode, use weekly candidate refreshes for M1/M2/M5/M7/M8 and monthly for M4/M9/M10/M12/M13 only after enough new eligible, mature data exists; M3/M6 recompute from versioned upstream inputs. Degradation >20% or drift starts an investigation, not unconditional promotion. Promote only after the locked comparison and all mandatory slices; exercise alias rollback. M11 is excluded until prospective eligibility is recertified.
13. **Model performance dashboard:** accuracy, drift, usage and freshness per model.

**Deliverables:** 13-entry eligibility/product register with a card per use case; eligible feature tables and model/baseline artifacts; versioned simulation/staffing rules; supported prediction tables; M4/M10 endpoint patterns; retrospective M11 limitation; monitoring, controlled refresh/rollback, dashboard and measured ADR-06 decision.

**Testing:** unit tests for feature functions; leakage tests; backtest reproducibility (same data version and seed give the same metrics); endpoint contract and latency tests; retraining and rollback drills.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 8.1 | Every use case has an honest, tested disposition | 13 of 13 audited; supported champions meet predeclared baseline/metric rules; no improvement permits a baseline champion, not a false superiority claim; M3/M6 invariant and deterministic tests pass |
| 8.2 | Calibration and support | Eligible classifiers ECE ≤0.05; supported 80% forecast intervals empirical coverage 75–85% with sample counts/uncertainty. Underpowered cases are aggregated/restricted or marked insufficient, never claimed calibrated |
| 8.3 | No leakage and valid decision origins | 100% of availability-boundary, delayed-input/sync, active/pending-state, target-window, point-in-time and disjoint holdout tests pass; M4 conditional remaining LOS / M5 hourly origins / M10 first-available origin enforced; M11 prospective endpoint absent and M5 readiness excluded |
| 8.4 | Registered and documented | Every deployed artifact registered/versioned with a product card; all 13 use-case dispositions, baselines, horizons and limitations recorded |
| 8.5 | Predictions populated per contract | 100% carry the correct model or rule/simulation lineage, cutoff, supported status and run ID; no unsupported prospective rows |
| 8.6 | Eligible endpoints | Warm p95 <300 ms under section 3.9 workload; cold-start and feature-staleness behavior reported; scale to zero confirmed |
| 8.7 | Monitoring functional | Mature-label replay updates accuracy, drift and eligibility status; all products/dependencies visible in Autopilot; static-demo schedules paused |
| 8.8 | Retraining and rollback drill | One controlled eligible refresh/promotion and rollback per deployed pattern, using a test fixture if no real challenger qualifies; test promotion never changes the final holdout result or forces a losing champion |
| 8.9 | Training cost within ADR-06 threshold | Measured and recorded |

---

## Phase 9: Genie spaces

**Objective:** Business users query structured data in plain language without SQL.

**Prerequisites:** Phase 6 gate (Gold and metric views); Phase 8 gate (prediction tables).

**Implementation steps**

1. Create four Genie spaces, each on the serverless SQL warehouse:

| Space | Datasets |
| --- | --- |
| Patient flow and capacity | fact_encounter, fact_ed_visit, fact_census_*, fact_placement_wait, fact_bed_turnaround, pred.census_*, pred.ed_arrivals_*, pred.admissions_*, dimensions |
| Revenue cycle and denials | fact_claim_lifecycle, fact_denial, fact_cash_weekly, pred.denial_*, pred.cash_*, payer and reason dimensions |
| Workforce | fact_staffing_*, pred.staffing_demand, pred.rn_absence, role and unit dimensions |
| Finance and cost to care | fact_cost_to_care, fact_cost_nonpatient, fact_plan_actual_forecast, pred.finance_monthly, cost centre and account dimensions |

2. Write table and column comments as business definitions; add synonyms.
3. General instructions per space: time zone, static/replay/live clock, close timing, open stays and unknown outcomes, finance scenario/vintage, selected encounter-cost scope, prediction support/intervals and M11 retrospective-only limitation.
4. Trusted assets: example SQL for the top 20 questions per space and the UC functions from Phase 6.
5. Benchmarks: 40–60 questions per space with expected SQL; stored in `genie/` and run on every configuration change.
6. Permissions by Entra group; masks and row filters continue to apply.
7. Version the space configuration in Git and deploy with the bundle or the Genie API.
8. Embed the relevant space in each AI/BI dashboard.
9. Publish Genie usage and failure telemetry to the Autopilot.
10. **Native cost controls:** implement section 3.10 shared/per-user Genie budget scopes and bounded benchmark/demo access windows before releasing space access. Verify the human and service-principal identities used by UI, Conversation API, agent tools and benchmarks; record applicable billed/free treatment and separately priced SQL compute. Demonstrate blocking with a tiny supported billable test identity/fixture and conservative headroom, not an assumption that a free allowance can be removed. Disable the native access profile/benchmarks outside funded windows through sleep/wake ownership. Native Genie usage is not charged a second time to the application model reservation ledger.

**Deliverables:** Four spaces, instructions, trusted SQL, benchmarks, deployment scripts.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 9.1 | Benchmark accuracy | At least 90% per space |
| 9.2 | No access to Bronze, Silver or raw PHI | 0 such tables in any space |
| 9.3 | Permission tests | 100% pass (masked and filtered results for restricted users) |
| 9.4 | Configuration reproducible from Git | Configuration/permissions and trusted-query results match after targeted redeploy; repeated stochastic benchmarks still meet ≥90% per space, with run variance reported |
| 9.5 | Native Genie spend boundary controlled | Correct shared/per-user budget scope and caller identities, blocking behavior, funded access/query limits and sleep denial verified; actual billed/free Genie usage and separate SQL charges recorded; no claim that the app counter caps native Genie |

---

## Phase 10: AI agent and Databricks App (GPT-6 Luna)

**Objective:** A Databricks App with a custom agent that answers supported questions from authorized tables, predictions, Genie and documents, validates numerical claims/citations, and abstains on unsupported evidence. Zero fabricated numbers is a bounded evaluation gate, not a guarantee that an LLM can never make a mistake.

**Prerequisites:** Phases 6, 8 and 9 gates.

### 10.1 LLM access evaluation and configuration

The business has selected **GPT-6 Luna**. ADR-04 and the Phase 2 probes establish a viable API route before this phase. Phase 10 completes quality/cost evaluation. Keep a shared provider adapter, but do not assume identical endpoint protocols or parameter support across routes.

| Path | Setup | Evaluate |
| --- | --- | --- |
| A. Databricks Foundation Model APIs | Documented endpoint `databricks-gpt-6-luna` / service `system.ai.gpt-6-luna`, using the Responses API; verify regional/account entitlement | Exact model revision/API/SDK, provider terms/routing, tools, structured output, price, rate limits and data processing location |
| B. Azure OpenAI in Microsoft Foundry (selected prerequisite route) | Verified `gpt-6-luna`, revision `2026-09-22`, East US `DataZoneStandard`, in MCPP subscription `0725…fcd1`; Databricks gateway provider uses a UC service credential backed by a dedicated access-connector managed identity. No API key. The readiness service proves the Responses function round trip; Phase 2 completes the full compatibility/control contract before onboarding | Revalidate entitlement/quota, streaming/structured output, restrictions, regional price/residency, attribution and failover; external-model gateway budget inclusion is Beta, so application calls require the shared reservation contract |

Evaluate feasible paths for tool calling, structured output, streaming, timeout/retry behavior, context limits, price per 1,000 declared turns, safety/data handling and end-to-end p95. Record unavailable routes with evidence; do not provision two providers merely to satisfy a checklist. Native GPT-6 Luna uses Responses API per the [Databricks supported-model reference](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-model-apis/supported-models). The [OpenAI model reference](https://developers.openai.com/api/docs/models/gpt-6-luna) informs the model contract; Azure/Databricks access and prices must be verified separately. Test a named fallback through the same adapter and evaluation before using it.

**Application-controlled model traffic** passes through both the section 3.10 shared reservation service and the approved Databricks gateway route, including model calls inside the served agent, diagnostic agent and evaluation clients. No application calls Azure OpenAI directly or bypasses the approved controls through a standalone LLM endpoint. Gateway attribution, supported limits/guardrails and minimized logging supplement the application ledger; they do not make it an invoice cap. Native `ask_genie` traffic uses the separately tested Phase 9 controls, not the application model reservation, even when initiated by an agent tool. Record route-specific gaps and fail closed on an unbounded or unsupported operation; do not silently switch providers/models after a permission or quality failure.

**Endpoint configuration:** pin the model revision, Responses SDK/adapter and supported reasoning/output parameters; send temperature only if supported. Maximum output tokens 1,500, bounded billable reasoning/context/tool calls, whole-turn deadline and at most one separately reserved retry within it. Enforce shared/user/component/evaluation-run limits with the transactional ledger and supported gateway controls. Prompts are versioned; section 3.9 measures the complete answer, not first-token latency.

### 10.2 Agent build

1. **Agent framework:** pinned Mosaic/MLflow `ResponsesAgent` integration, registered in `<catalog>.ml.healthcare_agent`; use the single ADR-02 deployment owner. Verify the user-context/tool-broker path end to end; an agent endpoint's shared runtime identity must not silently replace the caller's authorization.
2. **Planner:** classifies each question as descriptive, diagnostic, predictive, document or out of scope; decomposes multi-part questions; selects tools.
3. **Tools (allow-listed):**

| Tool | Backed by | Returns |
| --- | --- | --- |
| `get_metric` | UC functions over metric views | Values + citation |
| `ask_genie` | Genie Conversation API | Result, generated SQL + citation |
| `get_forecast` | `pred.*` tables | Quantiles, model version, forecast time + citation |
| `get_risk` | Eligible M4/M10 endpoints | Conditional remaining-LOS estimate or pending-claim denial risk with decision/source-availability times, reasons/model citation; early/resolved cases return the defined status and M11 pre-visit requests return its limitation |
| `explain_prediction` | SHAP reasons and model cards | Reasons + citation |
| `search_documents` | Vector Search over notes (permission-filtered), KPI glossary, data dictionary, limitations, runbooks | Passages + citation |

   No free-form SQL against Bronze, Silver or PHI tables.
4. **Vector Search / AI Search:** one endpoint with glossary, dictionary, limitations, runbook and separately restricted clinical-note indexes. Materialize approved minimal source tables with document/version IDs, facility and security class; keep embeddings/configuration for repeatable rebuilds. UC table masks/row filters are not inherited by search indexes. Only the trusted retrieval broker can query clinical indexes: it constructs ACL filters from verified user entitlements and rechecks each hit before any text reaches the LLM or caller. Users cannot submit/omit authorization filters or directly query the protected index. Verify current source/index compatibility in ADR-03. See [AI Search permission limitations](https://learn.microsoft.com/en-us/azure/databricks/ai-search/ai-search).
5. **Lakebase:** store sessions by verified user/tenant ownership and eligible M4/M10 feature copies. Use minimal non-identifying columns and restricted database roles. Synced tables, including the M4/M10 feature copies, are owned by the internal sync pipeline role, so Postgres row-level security cannot be configured on them: the trusted broker enforces facility/ownership access to them through explicit server-side predicates. Apply Postgres row policies only to app-owned tables such as sessions, where they are supported and tested. See [Lakebase synced tables](https://learn.microsoft.com/en-us/azure/databricks/oltp/projects/sync-tables). Do not assume copied UC masks or row filters survive synchronization. No browser/database credentials or arbitrary SQL; verify cross-user/facility denial and revocation on every serving path.

### 10.3 Citation and grounding mechanism

1. Every tool returns a citation record:

```json
{"id": "c3", "source_type": "METRIC", "object": "hc_prod.semantic.occupancy_rate",
 "definition_git_sha": "<commit>", "dataset_release": "healthcare-synthetic-v1.1.0",
 "inputs": [{"table": "hc_prod.gold.fact_census_hourly", "delta_version": 412}],
 "query_hash": "<sha256>", "result_hash": "<sha256>", "evidence_id": "<restricted-result-snapshot>",
 "filters": {"facility": "HSP-PEO", "period": "2025-W06"}, "clock_mode": "STATIC_CERTIFIED",
 "row_keys": ["HSP-PEO|MED|2025-02-03"], "known_at": "2025-12-31T23:59:59Z",
 "authorization_decision_id": "<opaque-id>", "retrieved_at": "<utc>", "link": "https://<workspace>/explore/data/…"}
```

2. Metric views have versioned definitions, not Delta table versions. Cite their definition Git SHA and actual input table versions, plus query/result hashes, filters, cutoff clock and authorized evidence snapshot. Model citations include the resolved model/rule version and feature snapshot; document citations include document version, chunk and authorized excerpt. Live citations include simulation/session/source instance, event/state version and observation time. The composer attaches citation IDs to each factual claim.
3. The **grounding verifier** runs before any answer is shown:
   - every number appears in, or is deterministically computed from, a cited tool result;
   - every citation ID exists in this turn's ledger and resolves to an object the user can access;
   - an LLM judge scores textual support as an additional imperfect signal, with reviewed failure cases; it is not proof of factual correctness;
   - forecasts are labelled with interval, model version and forecast time.
4. If verification fails, the answer is regenerated once; if it fails again the agent abstains: "I can't confirm that from the governed data", and shows what it found.
5. Trace tool names, timings, hashes, authorization decision, source versions, citation/verifier results and minimized/redacted prompt/output metadata. Raw PHI, user tokens, unrestricted SQL parameters and full clinical text are not copied into broad inference/telemetry tables. If a restricted result snapshot is needed for verification, encrypt and ACL it separately with a defined retention period. Retain replayable release snapshots/definitions or evidence extracts for the citation retention period; do not promise arbitrary Delta time travel after `VACUUM` has removed its files. Recheck permission when opening historical sessions and source links.

### 10.4 Safeguards and data access

- Configure **on-behalf-of-user authorization** explicitly with required OAuth scopes; use a per-request user-authorized SQL/Genie client. Verify identity propagation at every tool hop. When an endpoint cannot propagate that identity, route data access through the trusted app tool broker using verified request context and fail-closed entitlements; never trust a facility/user supplied by the LLM or browser.
- Apply authorization **before retrieval and before LLM context construction**. Gateway/app PHI detection is defense in depth, not access control. Non-clinical requests cannot select clinical-note tools or receive their text/metadata. Clinical access remains limited to authorized facilities.
- Retrieved text is treated as data; instructions inside documents are ignored (prompt-injection defence).
- Tools have EXECUTE grants only for intended groups.
- Out-of-scope questions (for example RN overtime forecasts) are answered with the documented limitation.
- Revalidate trusted scopes on each request, invalidate caches on revocation, and isolate conversation/history/cache keys by user and scope. Test revoked access, another user's session, direct index/database access, masked values in traces and cross-facility retrieval, including when a sync/index is stale.

### 10.5 Application

React front end and FastAPI back end: streaming chat, inline charts and tables, sources panel per answer, "Show SQL" and "Show model" toggles, role starter prompts (CFO, CNO, bed manager, revenue cycle lead), feedback with reason codes, conversation history.

### 10.6 Evaluation

1. Golden set of 200 questions across all domains with expected answer, expected sources and expected abstentions (`tests/agent_eval/`).
2. MLflow GenAI evaluation with scorers: numeric exact match, citation validity, groundedness, relevance, abstention correctness, safety.
3. Red-team set: prompt injection, PHI extraction attempts, permission escalation, fabricated-source requests.
4. Review app for subject-matter experts; reviewed examples extend the golden set.
5. A 50-question quick evaluation runs in CI before every agent deployment; the full 200-question evaluation runs before the Phase 10 gate and the Phase 12 release (section 3.6).
6. Spend-control tests run against the shared agent/Autopilot/evaluation wrapper: simultaneous requests near a limit across workers, duplicate attempt/settlement IDs, retries and unknown provider outcomes, app/ledger restart, day-boundary late settlement, price-policy change, unavailable ledger and native Genie tool calls. Verify no unreserved application dispatch, no double release and no accidental charging of native Genie tokens to the model-call ledger. Use low-cost fixtures and include pending reservations in the cost report.

**Deliverables:** ADR-04 results, approved LLM route, search indexes, agent model/endpoint and app, shared budget reservation service/ledger with settlement/recovery runbook, evaluation suite/report and measured cost per question.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 10.1 | ADR-04 confirmed with evidence | Feasible route and tested fallback/unsupported alternatives recorded; exact Responses API/model/SDK contract passes |
| 10.2 | No fabricated numbers | 0 on the 200-question golden set |
| 10.3 | No invalid citations in the evaluation | 0 invalid/inaccessible citations; replay resolves the correct definition, input/model/document versions and authorized retained evidence |
| 10.4 | Groundedness and relevance | Groundedness ≥ 0.95; relevance ≥ 0.90 |
| 10.5 | Correct abstention | ≥ 95% of expected abstentions |
| 10.6 | Security | 100% permission/red-team tests pass across SQL, Genie, serving, retrieval, Lakebase, sessions, logs and revocation; no unauthorized context sent to the LLM |
| 10.7 | Performance | Warm p95 full answer <15 seconds under section 3.9 workload; cold-start latency, timeouts and tool-call mix reported |
| 10.8 | Cost and reservation enforcement | Concurrency/idempotency/retry/timeout/crash/limit/ledger-unavailable tests pass across agent, Autopilot and evaluation clients; 0 unreserved application model attempts, unsettled charges covered, Genie costs separately governed; mean cost/question and total fit the allocation |
| 10.9 | Short-lived services | Search/sync/Lakebase/app shutdown verified; cold wake restores ready indexes, sessions, scopes and serving in <30 minutes for the declared profile; incurred billing tails recorded |

---

## Phase 11: DataOps Autopilot intelligence and remediation

**Objective:** Extend the Autopilot from detection to diagnosis, impact analysis and guarded remediation across all components, including ML, Genie and the agent.

**Prerequisites:** Phase 7 gate; Phase 10 gate (LLM endpoint for the diagnostic agent).

**Implementation steps**

1. **Graph coverage:** add feature tables, models, prediction tables, endpoints, Vector Search indexes, Genie spaces, dashboards and apps as nodes.
2. **Root cause analysis:** walk upstream from the symptom to the earliest unhealthy node; classify the failure (missing or late delivery, schema drift, corrupt file, row-count mismatch, unmapped key, invalid decimal, duplicate reload, retroactive revision, code error, permission, compute or quota, model drift, endpoint error).
3. **Data-level diagnostics:** offending rows from quarantine, column diffs, expected vs actual counts, exact error messages, run and update IDs.
4. **Impact analysis:** walk downstream to list every affected table, model, prediction, dashboard, Genie space and agent tool, written in business terms.
5. **Playbooks `autopilot.playbook`:** one per failure class with recommended steps.
6. **Guarded remediation actions:** an isolated executor may automatically retry/repair only a preapproved idempotent task within its scope and retry budget. Reprocessing/backfill, data rewrites, restore and deletion require a scoped dry run, recorded human approval, recovery point and audit entry. The read/diagnostic app cannot execute these actions directly. Record requested/approved/executed identity, affected versions, idempotency key and result in `autopilot.action_log`; LLM output is never execution authority.
7. **Diagnostic agent:** "Ask Autopilot" uses the Phase 10 endpoint, citation/verifier components and shared section 3.10 reservation service, with scoped telemetry tools. Its separate app/workers must debit the same shared budget buckets; no independent process-local allowance or uncontrolled model client. Native Genie tools, if used, retain the Phase 9 spend boundary.
8. **Alerting:** SQL alerts and job notifications to Teams and email, by severity, with deduplication and on-call routing.
9. **App v2:** lineage view with failing and affected nodes, incident timeline, action buttons, model health and agent health pages.

**Testing:** all 19 challenge sets, including valid controls/replacements that must not raise false incidents, plus 8 platform faults (killed job, broken code deploy, revoked grant, warehouse unavailable, endpoint error, model drift injection, stale Genie dataset, agent verifier failure spike). Expected incidents are derived from the certified challenge manifest, not an assumption that all 19 sets are faults. Use the Phase 7 operational signals, inject system-table delays and exercise uncertain/multiple-root diagnoses with explicit confidence and evidence.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 11.1 | Detection and controls | All 27 scenarios have their expected outcome; every incident-producing fault detected within 15 wall-clock minutes of its defined failure/due time; valid controls cause no incident |
| 11.2 | Root cause | Correct root node/class for ≥95% of incident-producing scenarios; denominator, ambiguous cases and evidence recorded |
| 11.3 | Impact | Affected-node list matches lineage ground truth for 100% |
| 11.4 | Remediation | Each playbook executed successfully at least once in test |
| 11.5 | Safety | 0 rewrite/restore/delete or out-of-scope actions without approval; read/diagnostic credentials cannot invoke privileged executor paths |
| 11.6 | Diagnostic answers and shared spend | 0 invalid citations on 30 questions; every application model attempt accounted in the shared ledger; simultaneous healthcare-agent/Autopilot requests cannot oversubscribe the tested limit; exhausted-budget responses dispatch no new model request |

---

## Phase 12: Batch integration, end-to-end testing and POC release readiness

**Objective:** Prove the synthetic batch POC works as one system under its declared workload, is governed and recoverable, and publish the approved demonstration release. RTI starts only after this gate. Real-patient production qualification is a separate programme.

**Prerequisites:** Phases 1–11 gates.

**Implementation steps**

1. **End-to-end test:** begin from a recorded test baseline, deliver a declared native replay partition with all required prior context, then run Bronze → Silver → Gold → eligible features/scoring → semantics/dashboards → Genie/agent. Verify deterministic business answers with independent oracle checks, predictions with their registered artifacts/feature cutoffs, and healthy Autopilot nodes. Include the complete accepted load/rebuild in the release evidence; a one-day delta alone does not prove reconstruction of the whole release.
2. **Regression suite:** all unit, contract, reconciliation, fault-injection, ML, Genie benchmark and agent evaluation tests run in one pipeline.
3. **Performance tests:** section 3.9 workload, including replay Gold deadlines, 10-user concurrency, request sample counts, errors/timeouts and both warm and cold behavior for dashboards, endpoints and the full agent answer.
4. **Security review:** end-to-end identities/grants, PHI/row policies, index/Lakebase copies, session ownership, traces/caches, revoked entitlements, secrets and audit coverage. Public-network synthetic POC acceptance is not approval for real data; record separate production network, privacy, clinical, encryption and availability prerequisites.
5. **Disaster recovery:** restore a Gold table and a model alias from history. For the clean-catalog rebuild, use the same complete accepted load from landing into a clean catalog that step 1 records; compare its hashes rather than running a second full rebuild.
6. **Runbooks:** deployment, rollback, reprocess delivery, backfill, model rollback, agent rollback, incident response, cost spike response.
7. **Cost baseline:** run one simulated demo day (wake, dashboards, Genie, agent questions, sleep) and measure it against the section 3.7 estimate; record total build spend to date.
8. **Sleep–wake cycle:** record shutdown and service/billing-settlement boundaries, then observe a full 24-hour sleep interval. The external control-plane guard runs without Databricks compute. Reconcile delayed billing after the interval before asserting zero workload compute; include shutdown tails, storage and external checks in their proper cost categories. Wake the declared batch profile, verify index/sync readiness, scopes, sessions and health, and keep historical ingestion/training schedules paused.
9. **POC release:** deploy approved assets to `hc_prod` using each resource's single lifecycle owner; smoke-test the synthetic demo role/workload matrix. Record versioned release manifest, limitations, unresolved production prerequisites and rollback point.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 12.1 | End-to-end cycle | 1 full green run plus 1 idempotent rerun with identical business hashes and deterministic prediction results within frozen numeric tolerance; GenAI quality/permissions still pass without requiring identical wording (3 consecutive runs in a separately funded reliability programme) |
| 12.2 | Regression suite | 100% of applicable checks pass, 0 silently skipped; approved eligibility-based exclusions have explicit assertions and disposition tests |
| 12.3 | Service levels | Section 3.9 workloads meet replay Gold 06:00 and warm p95 dashboard <5 s / eligible endpoints <300 ms / full agent <15 s; cold results and failures disclosed |
| 12.4 | Security review | 0 open high or critical findings |
| 12.5 | Recovery | The single shared clean-catalog rebuild (also used by 12.1) has equal hashes; restore drills pass |
| 12.6 | Cost | One measured demo day and projected one-/two-day months fit the agreed profile/budget; build charges plus outstanding usage and remaining Phase 13 upper estimate fit ₹20,000 |
| 12.7 | POC release smoke tests | 100% pass; manifest, scope/limitations and rollback point recorded; real-data use explicitly outside this release |
| 12.8 | Sleep–wake cycle | Settled 24-hour interval has 0 Databricks workload compute charges; external guard performs no workload queries/jobs; declared batch profile ready in <30 minutes with authorization intact; all residual charges itemized |

---

## Phase 13: Real-Time Intelligence (final phase)

**Objective:** Generate coherent simulated hospital events during bounded demo windows, process them through a supported Databricks micro-batch/Delta path, and deliver measured near-real-time operations views, alerts and model overlays. This is synthetic operational decision support under the clock and latency contracts below.

**Prerequisites:** Phase 12 gate, ADR-13 clock/recovery/latency contract and remaining funded RTI budget. Supported batch products, apps and monitoring are validated before streaming begins.

### 13.1 Continuous data generator app (`apps/rti-generator`)

1. **Purpose:** emit a realistic, continuous stream of hospital events as if the three hospitals were live.
2. **Events and topics:**

| Topic | Events |
| --- | --- |
| `adt.bed-events` | Reserve, occupy, vacate, clean start, ready, transfer, correction |
| `ehr.encounters` | ED arrival, triage, admission decision, admission, medically ready, discharge, LWBS |
| `ehr.vitals` | Triage and ward observations (oxygen saturation, heart rate, temperature) |
| `roster.attendance` | Shift check-in, check-out, call-out, replacement |
| `supply.consumption` | Item issues by location |

3. **Realism:** calibrated from the accepted v1.1.0 behaviour: arrival rates by facility, hour, weekday and season; acuity mix; ED stay distributions; ward-round readiness and the 09:00–20:00 discharge window; placement and cleaning times; RN absence rates; supply usage per patient-day.
4. **Consistency and references:** deterministic bed/encounter state machines enforce capacity, transitions and unique occupancy. Use existing synthetic patients and facility/unit/bed/worker/item identities valid at the simulation time; verify worker role/credential and unit capability. New patient identities are excluded from the baseline. Adding them later requires an ordered reference-registration event contract, protected names/demographics and a missing-reference recovery gate. Seed queues, occupants, stock balances and active shifts from one consistent as-of snapshot with a version/hash manifest.
5. **Clock:** the default is a visibly labeled historical simulation at a declared 2025 origin supported by the reference histories and forecast artifacts. `simulation_time` advances at 1×–60× while wall-clock UTC tracks emission, arrival and latency. Forecast targets, clinical durations, credential validity and alert dwell times use simulation time; operational lag and timeout use wall time. Only models trained and features available by the simulated decision origin may be shown as point-in-time predictions. A real-calendar demo outside the 2023–2025 reference/forecast range requires a separately versioned scenario extension; no silent date shifting or reuse of stale predictions as current forecasts.
6. **Event schema:** versioned JSON carries `simulation_id`, `session_id`, `source_instance_id`, stable `event_id`, `event_type`, `entity_type`, entity keys, `entity_sequence`, `revision`, optional `supersedes_event_id`/`movement_id`, `simulation_time`, business event time, wall-clock `emitted_at_utc`, facility, payload and `schema_version`. Events are partition-keyed by owning entity. Cross-topic/transfer changes use an explicit movement/correlation contract; do not assume global Kafka order or order corrections solely by event timestamp.
7. **Fault mode:** configurable rates of late, duplicate, out-of-order, malformed and schema-drifted events to exercise streaming quality checks and the Autopilot.
8. **Hosting (ADR-09):** Databricks App with start/stop/speed/fault controls, a required deadline (maximum 4 hours, shorter for gate windows), maximum event volume and an independent external shutdown. Use the supported scoped credential path from ADR-03; no secrets in events or app output.
9. **Durability:** persist generator state, seed/RNG position, clock position and an emission outbox transactionally in Lakebase. Use stable event IDs on retry; keep source events until their archival ingestion is reconciled. A process restart resumes the same session without inventing another admission/discharge. Persist state and archived event manifests before deleting Event Hubs or stopping Lakebase; event transport acknowledgement alone is not proof of downstream durability.

### 13.2 Streaming infrastructure

1. Define the Event Hubs namespace (Standard, 1 throughput unit, auto-inflate off) with the five topics, 2 partitions each, retention 1 day, in Terraform. `platform_up` creates it for an RTI window and `platform_down` deletes it afterwards, because a Standard namespace bills every hour it exists.
2. Consumer group per pipeline.
3. Checkpoints/state and archived source manifests are scoped by simulation/session, **source instance**, pipeline and state-schema version. A restart against the same topics within retention resumes its existing checkpoints. Deleting/recreating a namespace creates a new source instance; old offsets/checkpoints must not be attached to it. Bootstrap a new checkpoint from durable archived events/outbox plus a reconciled state snapshot, or explicitly start a new independent simulation. See [checkpoint identity and restart behavior](https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/checkpoints).
4. Enable only the required network/authentication path, enforce throughput/event caps and document source-retention expiry. Missing offsets or data beyond retention trigger the archive replay runbook and a blocked/initializing status, not silent `latest` consumption.

### 13.3 Dedicated real-time tables (`<catalog>.rt`)

| Table | Type | Content |
| --- | --- | --- |
| `rt.bronze_events` | Append-only streaming Delta table | Raw observations with source instance, Kafka partition/offset, event identity and wall-clock ingest time; retained before any late-event filtering |
| `rt.quarantine`, `rt.reconciliation_queue` | Governed exception projections/ledger | Malformed/schema/state conflicts and late/correction cases requiring repair, with reason, provenance and disposition |
| `rt.silver_bed_event`, `rt.silver_encounter_event`, `rt.silver_vitals`, `rt.silver_attendance`, `rt.silver_consumption` | Materialized canonical event projections | Parsed immutable assertions, one per simulation/event ID; persistent duplicate/conflict checks and correction lineage |
| `rt.gold_bed_state_current` | Materialized state projection | Deterministic current bed state from the seed plus accepted event history |
| `rt.gold_unit_occupancy_minute` | Materialized time-bucket projection | Occupied, dirty, cleaning, reserved, unavailable and staffed/usable capacity by unit and simulation minute |
| `rt.gold_ed_queue` | Materialized state projection | Waiting, in treatment and admitted awaiting bed |
| `rt.gold_staffing_live` | Materialized shift projection | Rostered/present RNs vs explicitly derived required hours |
| `rt.gold_stock_live` | Materialized balance projection | Opening stock plus signed accepted movements by item/location/base unit |
| `rt.alert_state`, `rt.alerts` | Rule-state projection and durable notification ledger | Pending/open/resolved conditions, stable alert/notification IDs, evidence version and delivery acknowledgements |

Real-time tables stay separate from certified batch Gold. Every projection, Lakebase row, alert, feature and citation carries simulation/session and state-version context. A published state snapshot is shown only after its dependent projections reconcile to the same cut of accepted events. Display views such as `gold.v_census_hourly_live` select one scenario and an explicit cutover: historical intervals end at cutover, live intervals start there, and hourly buckets spanning cutover are recomputed. Do not add overlapping historical/live census snapshots or mix independently simulated sessions.

### 13.4 Streaming pipelines

1. **Selected path:** Lakeflow Declarative Pipeline `rt_stream` ingests Kafka-compatible Event Hubs into durable Delta Bronze; deterministic materialized event/state projections publish Silver/Gold. Run the pipeline through a continuous Lakeflow pipeline job during funded windows, with a target 10-second flow cadence and measured downstream refreshes. This uses supported serverless pipeline execution, not an infinite `ProcessingTime` query in a serverless notebook/job. Pin and test the actual pipeline configuration in ADR-03/13; see [pipeline execution modes](https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/pipeline-mode) and [serverless notebook/job trigger limitations](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/limitations). Prefer incremental projections where supported; measure any full refresh at the bounded session size before increasing scale.
2. **No implicit real-time-mode switch:** the specialized Lakeflow real-time mode currently supports Kafka/Event Hubs sources/sinks, not Delta sources/sinks, and has operator restrictions including watermark deduplication and `foreachBatch`. It is not a configuration replacement for this Delta path. A future sub-second route requires a separate ADR, Kafka-output/serving design and new tests. See [real-time-mode compatibility](https://learn.microsoft.com/en-us/azure/databricks/ldp/real-time).
3. **Ordering, deduplication and late repair:** canonical event projections enforce permanent `(simulation_id, event_id)` uniqueness and immutable payload checks; entity sequence/revision and correction links determine effective state. A 15-minute simulation-time lateness threshold may bound an optimized window/state operator, but raw events are archived first. Beyond-threshold events and corrections enter the reconciliation queue, rebuild affected entity/time windows from durable history, and republish a new state version. No event silently disappears at a watermark; bounded dedup state alone is insufficient for session replay.
4. **Streaming quality:** validate schema/IDs, unit/worker capability, state transitions, stock units and clock/session consistency. Quarantine invalid assertions with full protected provenance. Distinguish malformed events from valid late events awaiting reconciliation; expose degraded state until repaired. Test cross-partition transfers and correction chains explicitly.
5. **Serving and latency:** sync a minimal current-state serving projection to Lakebase. The synced tables are owned by the internal sync pipeline role and cannot carry Postgres row-level security, so the Command Center reads them only through the trusted broker with server-side facility predicates; row policies apply only to app-owned tables. Use one approved snapshot/change-feed strategy from the Phase 2 probe; if native CDF for a chosen materialized view needs a preview, use an approved supported automatic feed or an owned Delta serving projection with replay-safe publication. Managed continuous sync has a minimum 15-second interval; fast reads do not mean <5-second event freshness. Targets after warm-up are wall-clock p95 emission → raw Delta <15 seconds, → reconciled current Delta <30 seconds, → Lakebase <60 seconds, → rendered screen <75 seconds. These are POC acceptance targets to measure, not vendor guarantees. Show simulation clock, source cutoff and serving age in the UI. See [Lakebase sync modes](https://learn.microsoft.com/en-us/azure/databricks/oltp/projects/sync-tables).
6. **Cost control:** continuous pipeline, syncs, polling, generator and apps run only inside the selected window. `platform_down` drains/reconciles outbox and offsets, persists generator/state manifests, stops jobs/syncs/apps and deletes transport only after verified archive durability. `platform_up` verifies source identity and recovery state before resuming generation.

### 13.5 Real-time analytics and intelligence

1. **Live KPIs:** occupancy, placement queue, ICU overflow, turnaround breaches, ED waiting, staffing gap, stock risk.
2. **Model integration:** recompute M3 from live state and compatible upstream vintages; score M4 only after the section 8.1 inpatient eligibility cutoff and actual feature/serving readiness. The baseline replay profile preserves the modeled admission-header +1 h 45 min delay: operational bed/arrival events can update live state earlier, but they do not authorize an admission-instant M4 prediction. Preserve simulated source-availability and real ingestion/serving times separately and test them in their own clocks. M10 requests retain the first-available pending-claim cutoff; this phase does not introduce a submission-instant feed. Detect arrivals above compatible M1 P90. Incompatible artifacts or early/missing inputs return `FORECAST_UNAVAILABLE` / `NOT_YET_AVAILABLE`, not an old prediction labeled current. M6 remains derived and M11 retrospective-only.
3. **Alert rules (`rt.alerts`):**

| Rule | Condition |
| --- | --- |
| Capacity | Unit occupancy above 90% and M3 P(full within 8 h) above 0.6 |
| Boarding | Admitted patient without a bed for more than 2 hours |
| Turnaround | Vacate to ready above 90 minutes |
| ICU overflow | ICU patient placed on a ward bed |
| Staffing | Required RN hours exceed present RN hours for the shift |
| Stock | Projected on-hand below reorder point within 48 hours |
| Demand surge | ED arrivals above M1 P90 for 2 consecutive hours |

4. **Command Center app (`apps/command-center`):** live bed board by hospital and unit, alert feed, forecast overlay, recommended actions, drill-down to patient context (PHI only for `hcp-clinical`).
5. **Agent integration:** `get_live_status` and `get_alerts` use the same trusted authorization broker and citations containing simulation/session, definition and state versions, source cutoff and observation time. Snapshot retention supports replay; copied state never bypasses facility/clinical scopes.
6. **Autopilot integration:** source ingestion lag, throughput, pending repairs, state divergence, serving age, checkpoint/source identity and generator/outbox status become graph nodes. Alert on sustained wall-clock source-ingestion lag >30 seconds or serving freshness beyond its separate budget; accelerated business time is not ingestion latency. Notifications use durable idempotent IDs, deduplicated delivery attempts and persisted dwell/resolution state across restarts.

### 13.6 Testing

1. **Offline realism:** exercise the same generator logic over a complete seasonal year after warm-up, with at least 5 fixed seeds and ≥1,000 completed IPD stays per replication; extend observation/follow-up when required. Compare supported hourly/weekday/seasonal rates, acuity/disposition mixes, ED/LOS/placement/cleaning quantiles, absence and supply usage with accepted aggregate profiles. Freeze tolerances and sampling rules in ADR-13 before testing; report confidence intervals, merge sparse strata and handle censored stays. These are transient generator tests, not changes to the certified batch dataset.
2. **Latency:** synchronized wall-clock measurements at emission, Bronze commit, reconciled state publication, Lakebase availability and rendered screen; ≥100 tagged valid events per topic/path in a separate controlled probe. Declare load, concurrency, warm/cold state, dropped/quarantined/late cases and notification delay. Do not infer latency from historical or accelerated event timestamps.
3. **Faults:** late within/beyond the threshold, duplicate after dedup-state expiry, out-of-order transfer, conflicting event identity, retroactive correction, invalid references, malformed/schema drift, stale permissions and source-retention expiry. Check repair outcome against an independent reducer from seed plus the full accepted event log.
4. **Recovery:** kill/restart generator, pipeline and serving sync independently; compare durable outbox/archived IDs to accepted/rejected outcomes. Also delete/recreate transport using a new source instance and checkpoint bootstrap, then verify state hashes, alert deduplication and authorization. Recovery tests include interruption between publication stages.
5. **Online soak:** 2 hours at 1× plus 30 minutes at 30×, with bounded session/event limits. It validates state, lag, resource use and recovery, not low-volume LOS distributions. Seed the seven alert cases separately; a 2-hour sample need not naturally produce a multi-day stay or a surge. A future 24-hour production soak needs separate funding and still does not replace long-horizon realism tests.
6. Full Phase 12 applicable regression with streams running, plus cutover/non-overlap, model-origin and access tests. Seed cases immediately before and at/after the simulated admission eligibility boundary, plus delayed serving copies and completed stays; advance simulation time explicitly instead of waiting for a natural admission in the short soak. Publish the RTI extension only after the gate package is ready, then run targeted smoke tests.
7. Cost/sleep test: hard deadline stops every producer/consumer/sync/poller, durable state is complete, external guard confirms the resource state and settled charges are reconciled.

**Deliverables:** generator app, Event Hubs, `rt` tables, streaming pipeline, Lakebase live tables, live KPIs, real-time ML scoring, alert rules, Command Center app, agent and Autopilot integrations, test reports, RTI runbook.

**Exit criteria**

| # | Criterion | Measure |
| --- | --- | --- |
| 13.1 | Measured freshness | Warm wall-clock p95 raw Delta <15 s, current Delta <30 s, Lakebase <60 s, screen <75 s under section 13.6 probes; full latency breakdown, failures and cold start reported |
| 13.2 | State correctness | 0 double occupancies, invalid capacity/stock transitions or cross-session mixes; state/census hashes equal independent seed-plus-log reduction, including corrections and display cutover |
| 13.3 | Generator realism | Long-horizon, multi-seed tests pass frozen supported-stratum tolerances: aggregate arrivals and LOS median/p90 within ±10%, major outcome mixes within 3 percentage points; sample counts/confidence intervals and sparse/censored handling recorded; short soak not used for this claim |
| 13.4 | Data quality | 100% injected invalid events quarantined; valid beyond-threshold events reconciled; 0 duplicate accepted event identities or unexplained missing outcomes |
| 13.5 | Recovery | Generator/query/sync restart and transport recreation drills produce 0 lost accepted events or duplicate business effects; new source instance uses new checkpoint; state/alert results match the durable replay |
| 13.6 | Alerts | Each of 7 alert rules fires on a seeded scenario and appears in Command Center, Teams and Autopilot |
| 13.7 | Integration | Live citations, role/revocation and compatible model-origin tests pass; M4 early/delayed-copy/resolved cases enforce section 8.1 availability in both clocks; unsupported predictions abstain; Autopilot shows source/state/serving health |
| 13.8 | Soak | 2 hours at 1× plus 30 minutes at 30×, no unexplained failure/state drift; wall-clock source-ingestion p95 <30 s and serving meets its separate freshness budget; event count and fault profile reported |
| 13.9 | Cost | Generator, pipeline and apps stop automatically; Event Hubs deleted by `platform_down`; 0 streaming compute outside windows; total build spend at or below ₹20,000 |
| 13.10 | Regression and release | Applicable Phase 12 regression 100% pass with RTI running; demo extension smoke tests, updated runbooks/cost manifest and whole-platform sleep/wake recovery pass |

---

## 14. Testing strategy summary

| Level | Introduced | Runs | Gate |
| --- | --- | --- | --- |
| Unit | Phase 2 | Every pull request | 100% pass |
| Contract (schemas, grains, prediction contract, tool signatures) | Phase 4 | Every pull request | No unreviewed change |
| Reconciliation to answer key | Phase 5 | Local regression on PR; independent cloud checks at changed-input/code gates and release | 0 unexplained differences; runtime identities cannot read oracle |
| Fault injection | Phase 4, expanded in 7, 11, 13 | Every release in test | All expected outcomes |
| Idempotency and recovery | Phase 4 | Every release | Identical results |
| Permission and security | Phase 2, expanded in 6, 10, 13 | Before data exposure, at every changed access path and release | 100% pass, including copied stores, sessions, logs and revoked scopes |
| ML (leakage, backtests, slices) | Phase 8 | Every model change | Exit criteria 8.1–8.3 |
| Genie benchmarks | Phase 9 | Every configuration change | ≥ 90% |
| Agent evaluation and red team | Phase 10 | Every agent change | Exit criteria 10.2–10.6 |
| Performance | Phase 6, expanded in 8, 10, 12, 13 | Bounded gate/release windows | Declared warm/cold, concurrency/sample and clock contracts measured; SLOs met |
| End to end | Phase 12, extended in 13 | Every release | 100% pass |

---

## 15. Governance, security and access

### 15.1 Data governance

- Unity Catalog governs data/model objects and coarse search-index access; workspace permissions govern Apps, Genie and dashboards. Copied search/Lakebase/session/cache data needs the explicit authorization controls in Phase 10, not a claim of automatic UC policy inheritance.
- Every table has `owner`, `domain`, `pii_class`, `sla_tier` and `layer` tags and a description.
- Combine UC lineage with source-delivery/version IDs, declared dependency edges, model/feature manifests and citation ledgers to trace from landing to dashboard, prediction and agent answer. Capture edges that UC does not infer across app/API/copy boundaries.
- Retention: landing and frozen accepted snapshots for the release lifetime; protected quarantine 180 days; redacted telemetry and minimized agent traces 400 days. Retain referenced definitions, model artifacts and restricted citation evidence for that citation lifetime, or mark an explicitly shorter citation expiry. `VACUUM`, CDF retention and checkpoint/archive cleanup must respect the tested replay window; default time travel is not a 400-day audit archive.
- RTI source archives, generator/outbox state, snapshot manifests and notification logs remain available for at least 90 days and until a newer certified recovery point covers them. Bound session/event volume, compact snapshots, and cost retention explicitly; disposable Event Hubs is not the system of record.
- Version rule: one dataset version per environment; v1.0.2 is never loaded.

### 15.2 AI governance

- Product cards for all 13 use cases, distinguishing trained models/baselines, simulation, derived rules and retrospective-only/insufficient-data dispositions.
- Champion and challenger promotion requires the gate in step 8.3.12 and owner approval.
- Agent and Autopilot answers use minimized, permission-scoped traces/citations and verification; evaluation reports and observed failures are retained per release. Bounded passing tests do not establish universal factual correctness.
- Prompts versioned; LLM endpoint changes go through evaluation before deployment.
- Application-controlled LLM calls use the approved gateway route and shared transactional budget reservations. Native Genie has separate platform budgets, identity scopes and funded windows; neither the app ledger nor approximate gateway blocking is an absolute platform invoice cap (section 3.10).
- Human oversight: agent answers are decision support only; Autopilot destructive actions need approval.
- Documented dataset limitations are surfaced by the agent when a question touches them.

### 15.3 Security

- Entra ID single sign-on; groups provisioned from Entra; service principals for automation; no personal access tokens in production.
- Secrets in Key Vault-backed secret scopes.
- Encryption at rest for all POC stores, encrypted/restricted Terraform state and protected credential handling. Real-data key management, network isolation, workspace separation and compliance controls require a separately approved security design before ingestion; this POC does not make those production decisions optional or complete.
- Audit through `system.access.audit`, reviewed weekly by `hcp-auditors`.

### 15.4 Access matrix (prod)

| Group | bronze / silver | gold, semantic, pred | features, ml | dq, hc_ops | PHI columns | Apps |
| --- | --- | --- | --- | --- | --- | --- |
| hcp-platform-admins | Manage | Manage | Manage | Manage | Privileged access audited; break-glass recorded | All |
| hcp-data-engineers | Read/write (dev/test); protected reads (prod) | Read | Read | Redacted read | Masked; raw payload only by approved break-glass | Autopilot |
| hcp-data-scientists | Protected Silver reads | Read | Read/write (dev/test) | Redacted read | Masked | Agent, Autopilot |
| hcp-analysts | None | Read | None | None | Masked | Agent, Genie |
| hcp-clinical | None | Read | None | None | Unmasked | Agent, Command Center |
| hcp-finance | None | Read (finance, revenue) | None | None | Masked | Agent, Genie |
| hcp-operations | None | Read (flow, workforce) | None | None | Masked | Agent, Genie, Command Center |
| hcp-auditors | Protected read-only views | Read | Read metadata/approved features | Redacted read/audit views | Masked | Read-only views |

Facility policies apply to every non-admin user through the trusted `hc_ops.security.principal_scope` mapping. Dataset `access_scope` is a synthetic business entitlement source, not a direct mapping from fake worker IDs to real Entra identities. Only security administrators/approved jobs manage the bridge, with validity/revocation audit. Raw payload, quarantine, answer-key, security-control and deployment tables are separately restricted; a broad schema read must not bypass them. App principals, background jobs and the remediation executor have individually scoped grants outside this human-role summary. Test direct-object access as well as the UI.

---

## 16. Operational monitoring

| What | Where | Owner |
| --- | --- | --- |
| Pipeline and job health, DQ, freshness, schema drift, deliveries | Autopilot app (Phase 7, 11) | Data engineering |
| Model accuracy, drift, endpoint health | Model performance dashboard and Autopilot (Phase 8) | ML |
| Genie and agent quality, verifier failures, token usage | Autopilot and agent inference tables (Phases 9–11) | Application |
| Streaming lag, throughput, quarantine rate | Autopilot (Phase 13) | Data engineering |
| Cost by component | Cost dashboard and Azure budgets (Phases 1, 7) | Platform owner |
| Security and access | Audit review (Phase 2 onward) | Security |

---

## 17. Risk register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| GPT-6 Luna route, quota or SDK incompatible | Downstream rework | Phase 0 official/region/API contract; Phase 2 Responses/tool smoke probe; tested named fallback before use; Phase 10 quality/cost gate |
| A required Databricks feature unavailable or preview-only | Unsupported dependency | Phase 0 maturity/version/region matrix and Phase 2 tenant probes before onboarding; approved fallback and single lifecycle owner |
| Idle services left running | Budget overrun | Section 3.5 policies, `platform_down` at the end of every working or demo day, daily `platform_guard`, Autopilot cost anomalies, Azure budget alerts |
| Build spend exceeds ₹20,000 | POC stops before completion | Local-first development, section 3.6 allocation, spend recorded at every gate, contingency released only by the platform owner |
| Resources that bill while idle or during deletion/sync tails | Monthly budget exceeded | Measure shutdown/settlement and cold wake, pause syncs/pollers, use the external guard and reconcile a priced cost ledger; ₹6,000 is a target to validate |
| Silver does not reproduce the answer key | Wrong KPIs downstream | Phase 5 exit criterion 5.1 blocks Gold; port the reference decoder |
| Data leakage or backdated scoring origin | Inflated accuracy | First-available inpatient/claim origins, conditional remaining LOS, as-of/availability-boundary tests and gate 8.3; RTI preserves the baseline decision contract |
| Agent fabricates or mis-cites | Loss of trust | Verifier, abstain policy, exit criteria 10.2–10.3 |
| Mixing dataset versions | Corrupted history | One version per environment; ledger rejects foreign deliveries |
| Streaming costs during RTI | Budget overrun | RTI last; demo windows; automatic stop; Event Hubs created only in Phase 13 |
| Scope creep beyond dataset limits | Misleading outputs | Section 1.2 limits enforced in model and agent design |
| Equal file hashes or ordinary SCD2 collapse valid history | Missing deliveries or false point-in-time facts | Manifest-scoped identity, immutable assertion merges and revision/availability tests in Phases 4–5 |
| Feature unavailable before outcome or holdout reused for selection | Inflated predictive claims | M11 retrospective-only, M5 readiness excluded, field eligibility/split manifest and horizon-specific tests |
| Copied notes/features/sessions/logs bypass UC policies | Cross-user/facility exposure | Trusted retrieval/tool broker, explicit Lakebase scopes, minimized traces, revocation and direct-access tests |
| Transport recreation reuses stale checkpoints or generator state | Missing/duplicated events and wrong census | Source-instance-scoped recovery, durable outbox/archive/snapshots, deterministic replay and reconciliation |
| Short low-volume soak treated as distribution validation | Unsubstantiated realism claims | Long-horizon multi-seed offline generator tests; separate latency/state/recovery soak |
| App counter assumed to cap native Genie, or concurrent workers oversubscribe a balance | Unreported/over-budget usage | Section 3.10 separates charge/control scopes; shared atomic reservations cover uncertain attempts; native Genie scopes and funded windows pass gate 9.5 |
| Optional inbound webhook treated as a required dependency | Unnecessary gate failure or insecure workaround | Gate 2.8 accepts evidenced `UNSUPPORTED_DISABLED` only with passing required polling and disabled receiver; gate 7.2 proves detection without webhooks |

---

## Appendix A: Phase gate checklist

```
Phase: <n>  Owner: <name>  Date: <yyyy-mm-dd>
[ ] All implementation steps complete and merged to main
[ ] Required targets validated; changed assets deployed to the environments in the gate test matrix
[ ] Tests for this phase pass (attach report)
[ ] Every applicable exit criterion measured in gate.json; explicit eligibility/exclusion assertions, no silent skips
[ ] Cost check (section 3.8): phase spend recorded against the ₹20,000 allocation; no idle resources
[ ] New resources added to platform_down / platform_up / platform_guard
[ ] Exactly one lifecycle owner per resource; version/permission/state migrations and rollback tested
[ ] Autopilot coverage added for new assets (from Phase 7 onward)
[ ] Documentation and runbooks updated
[ ] Owner sign-off
```

## Appendix B: Resource creation timeline

| Resource | Phase created |
| --- | --- |
| Resource group, ADLS Gen2, Key Vault, workspace, access connector, budgets | 1 |
| Catalogs, schemas, volumes, warehouse, policies, system tables | 2 |
| Bronze, Silver, Gold pipelines and jobs | 4–6 |
| Autopilot app and telemetry jobs | 7 |
| Feature tables, models, serving endpoints | 8 |
| Genie spaces | 9 |
| Verified Azure OpenAI Luna prerequisite resource/route | Authorized readiness preparation; revalidate full contract in 2 and application controls in 10 |
| Vector Search, Lakebase, agent app | 10 |
| Event Hubs, RTI generator app, streaming pipeline, Command Center | 13 |

Phase 2 may create minimal temporary fixtures for the approved capability probes, including LLM/search/Lakebase access. They are not production assets, are charged to the build budget, and are removed after the probe. Full RTI transport/generation remains Phase 13; the Phase 12 demonstration release receives its versioned RTI extension then.

## Appendix C: Design revision register (2026-10-27)

| Review area | Revision incorporated | Acceptance evidence |
| --- | --- | --- |
| Delivery and history | Delivery identity separate from checksum; immutable canonical assertion history; current/as-of projections separate | Gates 4.1–4.5, 5.1–5.6 |
| Feature availability | Field-level clocks; M4/M5 first-available inpatient snapshots, M10 first-available pending claim, M11 retrospective-only and M5 readiness excluded | Gates 0.4, 8.1–8.5, 13.7 |
| ML validity | Baseline champions allowed; simulation/derived products identified; disjoint holdouts and horizon/sample support | Gates 8.1–8.9 |
| Financial grains | Selected encounter/month/category allocations; estimated procedure costing outside baseline | Gates 6.1–6.3 |
| Authorization | Trusted Entra bridge, per-app principals, brokered retrieval, copied-store/session/log controls | Gates 2.3, 5.4, 6.4, 10.6, 13.7 |
| Supported RTI path | Micro-batch Delta pipeline; measured multi-stage freshness; no implicit real-time-mode substitution | Gates 0.2, 2.8, 13.1 |
| RTI durability and clock | Simulation/source/session identities, persistent generator/outbox/state, late repair and transport-recreation recovery | Gates 13.2, 13.4–13.8, 13.10 |
| Operational detection | Required authenticated Jobs/Pipelines API polling; optional webhook may be `UNSUPPORTED_DISABLED` with safe cleanup; delayed system tables for history | Gates 2.8, 7.2–7.3, 11.1–11.3 |
| Budget and sequencing | Costed go/no-go, scoped atomic app reservations, separate native Genie budgets/windows, external sleep guard, selective tests and strict dependencies | Gates 0.1–0.4, 2.6, 7.6, 9.5, 10.8, 11.6, 12.6–12.8, 13.9 |
| Meaningful tests | Fixed workload/sample contracts, warm/cold performance and long-horizon realism separate from soak | Gates 6.6–6.7, 8.2, 10.7, 12.3, 13.1–13.8 |
| Agent reliability | Responses API probe, bounded quality claims, replayable definition/input/model/document citations and redacted traces | Gates 2.8, 10.1–10.9, 11.6 |

Official links beside platform constraints were reviewed on 2026-10-27. Recheck them and record the actual workspace/runtime/provider behavior in Phases 0–2 before relying on a changing service capability. This revision changes only the implementation design; no source dataset, cloud resource or phase gate result is changed by editing this document.
