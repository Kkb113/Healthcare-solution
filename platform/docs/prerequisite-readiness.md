# Healthcare platform prerequisite readiness

Reviewed 2026-10-27. This is an access and prerequisite remediation record, not a passed Phase 0, Phase 1 or Phase 2 gate. Analytics implementation and source-data onboarding have not started. The user authorized remediation of the six readiness findings, plus the explicitly recorded telemetry and shared metastore administrator approvals.

## Exact GPT-6 Luna access: resolved without moving the workspace

The healthcare workspace remains `intellify-healthcare-dbw`, ID `7405619366453187`, Premium SERVERLESS, East US, in MCPP subscription `d054aa64-95db-467b-a25c-387de70b15bd`. There is no replacement workspace or classic-compute fallback.

The selected model route is:

```text
Existing healthcare Databricks workspace
  /ai-gateway/openai/v1/responses
  intellify_healthcare_dbw.readiness.gpt_6_luna
    -> governed Azure OpenAI model provider, restricted to gpt-6-luna
    -> UC service credential / dedicated access-connector managed identity
    -> aoai-hcp-luna-0725fcd1 / gpt-6-luna
       model revision 2026-09-22, DataZoneStandard, capacity 5
       East US resource, MCPP subscription 0725b5e7-75db-4c60-b5e9-928c3df3fcd1
```

Both subscriptions are in the same Entra tenant. The second subscription already had 250 Global Standard and 100 Data Zone Standard quota units; the deployment uses five Data Zone units, with no provisioned throughput. Resource location and processing geography are distinct: Data Zone deployments may process requests within the applicable US data zone, rather than guaranteeing execution in East US alone. No model API key or client secret was created. Only the operator and the dedicated gateway identity initially have Azure inference roles; the readiness UC service has no business-user/application grants.

Two direct Azure Responses requests and two requests through the existing Databricks gateway passed the same deterministic test: forced `add_numbers(17,25)` call, locally verified tool result, then final answer `42`. Responses identify the exact model as `gpt-6-luna`. Direct usage: 170 input / 27 output tokens; gateway usage: 182 input / 27 output tokens. This proves access, keyless authentication and a structured function round trip. Capacity five is a small readiness allocation, not a sizing result for the concurrent-user load target; scale within quota through Terraform only after a token/rate/cost estimate. The probe does not certify healthcare answer quality, JSON-schema response formatting, streaming, latency under load, failover, application authorization or budget blocking; the prescribed Phase 2/10 tests remain required.

The native Databricks/ADI path remains unavailable: partner-powered AI is enabled, no ADI integration toggle was exposed in the inspected account settings, and the native invocation failed with “endpoint does not exist.” A generated/default `system.ai.gpt-6-luna` service metadata response did not establish usable entitlement. Azure Luna quota in the workspace subscription was zero in East US, West US, East US 2, West US 3, South Central US and Central US. Moving the workspace between those regions would not resolve that observed quota gap. Native ADI eligibility can still be requested from the Databricks account team, but it is no longer the blocking model path.

Official references: [ADI eligibility and enablement](https://docs.databricks.com/adi), [Databricks native Responses route](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/query-openai-responses), [Azure quota scopes](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/quota), [Azure deployment types and processing geography](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/deployment-types).

## Six readiness findings

| Finding | Remediation and verified boundary |
| --- | --- |
| 1. Luna route/quota | Resolved for the exact model through the tested Databricks gateway → keyless Azure route above. Native ADI remains unavailable; no model substitution. |
| 2. System telemetry access | Resolved for the approved operator and four tables. Actual SQL on billing usage/prices, job-run timeline and table lineage succeeded. Empty healthcare activity results are expected in a new workspace and are not end-to-end pipeline evidence. The disposable 2X-Small serverless warehouse was stopped and deleted. |
| 3. Serverless workspace adoption | Correct workspace and SERVERLESS mode verified through the account API. The implementation plan now adopts it and removes classic cluster assumptions. Full serverless feature probes stay in Phase 2. |
| 4. Ambiguous CLI targeting | Added `HEALTHCARE_AZURE` and `HEALTHCARE_ACCOUNT` Azure-CLI-authenticated profiles with explicit IDs. Live workspace identity and account workspace checks passed. Existing profiles, Azure default subscription and retail resources were preserved. |
| 5. Tooling and CI identity | Official checksum-verified CLI 1.22.1 and Terraform 1.17.0 installed under ignored `.tools/`. Isolated Python 3.12.13 environments use hash-locked dependencies. WSL Spark SQL and Delta write/append/time travel passed. Three dedicated Entra/Databricks service principals and a main-branch-only GitHub OIDC trust exist; CI execution evidence is recorded separately below. |
| 6. Supporting infrastructure and costs | Dedicated ADLS Gen2, private containers, RBAC Key Vault, access connector, eight Entra groups, scoped identity roles and budget alerts provisioned from pinned Terraform. The dedicated UC storage credential and two external locations were created with validation enabled. State is in a private encrypted Azure Blob backend. Workspace and model subscription costs must be reconciled together; full solution feasibility is not established by these prerequisite probes. |

## Governance approvals and permissions

The initial schema-wide telemetry SELECT attempt was rejected by automatic approval review. No rejected grant was applied. The user then explicitly approved only SELECT on `system.billing.usage`, `system.billing.list_prices`, `system.lakeflow.job_run_timeline`, `system.access.table_lineage`, with required USE permissions. These tables can expose shared account operational metadata; queries filter the healthcare workspace wherever the field exists.

Those grants initially failed because the shared metastore owner was `System user`. The user separately approved making `karthik@intellifysolutions.com` administrator of `metastore_azure_eastus`, ID `d9469652-1d8e-4e7f-9abd-8626b32a9f30`. That is a persistent role across all attached catalogs/workspaces, not a healthcare-only privilege. The owner change was verified, then the exact four table grants succeeded. No schema-wide SELECT or business-user telemetry grant was added.

Foundation service principals have Databricks workspace `USER` plus the required `workspace-access` entitlement, not workspace/account administrator. The second CI attempt proved Azure OIDC login but exposed the missing workspace entitlement. The third proved Databricks identity access and exposed the separate SQL service entitlement required by the warehouse-configuration check. The adapter adds `databricks-sql-access` only to CI; this grants neither warehouse `CAN_USE` nor table privileges. CI has Azure Contributor only on `rg-hcp-dev`, Reader only on the existing healthcare workspace, and Blob Data Contributor only on the `tfstate` container. It has no Owner, User Access Administrator, Azure model inference or business-table grants. Jobs and validation principals have no oracle/business-data grants yet. Administrative Terraform/RBAC bootstrap remains an operator responsibility; the CI identity is not an unrestricted infrastructure administrator. Phase 2 establishes and tests layer-specific deployment/run/validation permissions.

The first CI identity probe failed with `AADSTS700213`: this repository emits an OIDC subject containing immutable owner/repository IDs. Both IDs were verified through the GitHub repository API. Terraform now trusts exactly `repo:Kkb113@176327882/Healthcare-solution@1430602110:ref:refs/heads/main`, with issuer `https://token.actions.githubusercontent.com` and audience `api://AzureADTokenExchange`. No wildcard, additional branch, client secret or broader Azure role was introduced to fix the mismatch. The original failed attempt remains in the CI evidence.

Eight role groups exist in Entra; only the platform-admin group initially contains the operator. Entra group synchronization/Databricks assignment and authorization matrices remain formal foundation tasks; the presence of groups alone is not evidence that automatic identity management or access tests have passed. Synthetic Workday security data is never used to authorize these cloud identities automatically.

## Resource lifecycle and reproducibility

| Scope | Sole owner |
| --- | --- |
| Dedicated Azure foundation, Entra groups/apps/SPs, GitHub federated trust and scoped Azure roles | `platform/infra/foundation/` Terraform, AzureRM 5.11.0 / AzureAD 3.10.0 |
| Azure exact-model resource/deployment, inference identities and model budget alerts | `platform/infra/model-access/` Terraform, AzureRM 5.11.0 |
| Dedicated healthcare UC storage credential and external locations | `platform/infra/workspace/` Terraform, Databricks provider 1.140.0 |
| Existing Databricks workspace and metastore assignment | Reference-only adoption; never create a second workspace |
| Readiness UC schema, model service/provider and service credential | `configure_model_gateway.py`, isolated capability fixtures; remove or explicitly transfer ownership before formal application deployment; never manage concurrently through Terraform/Bundles |
| Account registration/workspace assignment of the three foundation SPs | `configure_ci_identity.py`; Entra lifecycle remains Terraform-owned |
| Explicit operator telemetry grants | `configure_telemetry_access.py`, approved scope JSON |
| Shared metastore owner bootstrap | One-time explicitly approved account API update; not routine deployment |
| Healthcare workspace cost tags | Tag-only Azure API merge; do not manage the serverless workspace as a classic Terraform workspace |

Use the committed backend configurations, provider locks, public target/identity configuration and runtime locks. State, downloaded binaries, caches, generated datasets and temporary probe outputs stay out of Git. Remote state is accessed through Entra auth, with private-container access and Blob lease locking; no storage key is placed in backend configuration. A new machine initializes an existing backend normally; `-migrate-state -force-copy` was a one-time bootstrap step and must not overwrite an established remote state. Bootstrap scripts do not change the global Azure default subscription or overwrite existing CLI profiles.

Native Windows SDK/control-plane tooling is supported, but local Spark/Delta execution uses the existing Ubuntu 24.04 WSL distribution with Java 21 and pinned Python 3.12.13. The initial native-Windows run failed due to missing Hadoop Windows support; the Linux run passed. No unofficial `winutils.exe` was installed. Run `wsl -d Ubuntu-24.04 -- bash /mnt/c/HealthCare_Solution/platform/scripts/bootstrap_runtime.sh` to reproduce. CI uses equivalent Linux dependencies.

## Costs, controls and implementation gates

The workspace subscription reports USD billing. `cost-policy.json` uses an explicitly labeled planning assumption of ₹100/USD, not a current FX quote. Build alert partitions are USD 165 for workspace/foundation and USD 35 for the model; monthly partitions are USD 55 and USD 5. Their planning totals equal ₹20,000 build and ₹6,000 monthly. Reconcile actual FX, taxes, gross usage, credits, billing delays and shutdown tails before each funded window. Annual build budgets do not automatically reset the project's cumulative build ledger after a billing period.

Workspace subscription alerts select `project=healthcare-platform`; model alerts select the dedicated model resource group. Verify cost-tag propagation when charges arrive. Each build partition has four alerts and each monthly partition three alerts; partition thresholds do not replace the cross-subscription cumulative ledger's global thresholds. Existing subscription-wide/retail budgets were preserved. Azure alerts do not stop spending, and external-model Databricks budget inclusion is Beta. Application reservations and tested sleep/wake/guard controls remain mandatory before applications or scheduled workloads are released.

Reserve ₹200 of the existing ₹800 capability-probe allowance for this preflight until both providers' bills settle. Actual currency cost is pending, not zero. No application, endpoint with provisioned throughput, Event Hubs, continuous job, Lakebase instance or search endpoint is kept running by this preflight. The model resource is pay per token; small storage/Key Vault and control-plane tails still require reconciliation. The readiness route is operator-only; it is not released as an unbudgeted application endpoint.

**Remaining implementation work is explicit:** complete all 15 ADRs, a regional priced whole-workload feasibility estimate and Phase 0 gate; reconcile/verify the prepared UC storage and finish identity synchronization/grants and formal foundation gates; execute all required Phase 2 capability/control probes; implement sleep/wake/external guard and the cumulative spend ledger before scheduled/application workloads; then begin source onboarding only after its prerequisite gates pass. No source files have been uploaded and no Bronze/Silver/Gold, ML, Genie, application or RTI solution workload has been built here.

## Evidence and CI

Bounded, non-secret evidence is committed under `evidence/platform/prerequisite-readiness/`. It preserves the failed native model probe alongside the successful Azure/gateway probes, telemetry query/cleanup results, runtime evidence, targeting checks, budget configuration and Terraform drift results. Both external locations explicitly passed all six credential checks: READ, LIST, WRITE, DELETE, PATH_EXISTS and HIERARCHICAL_NAMESPACE_ENABLED. This package is not named `gate.json` because no implementation phase is being certified.

CI workflow: `.github/workflows/platform-readiness.yml`. PRs run local configuration/lint/runtime checks. A manual main-branch invocation also verifies Entra OIDC → Azure CLI → Databricks service-principal access and warehouse metadata without launching Databricks compute or deploying assets. No client secret or repository secret is required. [Run 40468980776](https://github.com/Kkb113/Healthcare-solution/actions/runs/40468980776) passed after the recorded trust/entitlement fixes. CI and WSL runtime versions and Spark/Delta outcomes agree; the original failures and passing result are retained as bounded evidence. A clean [final-source run 40470464161](https://github.com/Kkb113/Healthcare-solution/actions/runs/40470464161) passed both jobs against source commit `d062bf816c50126cf62558010887170e721dffcc`, which includes all executable/configuration fixes. Subsequent evidence-only changes do not constitute a new implementation gate.
