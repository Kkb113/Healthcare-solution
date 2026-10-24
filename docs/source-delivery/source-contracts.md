# Source contracts

## Coverage and authority

The frozen scalar schema is preserved across all 25 canonical tables. `source-dictionary.json` describes every source field, canonical field, data type, nullability and transport-reference role. Per-file typed key dictionaries resolve native identifiers; unknown keys fail closed. They mirror existing keys and do not create business `source_key_map` histories. The existing legacy-key histories themselves are exported without changing their meaning.

| Source | Tables / content | Representation |
|---|---|---|
| EHR | Organization, location, patient, coverage, payer/catalog references, appointments, encounters, conditions, clinical events, facility/day context and integration mappings | UTF-8 JSONL record envelopes, monthly delivery archives |
| ADT_BED | All immutable bed states and corrections | JSONL messages with control ID, archive ordinal, source availability and exact effective sequence/correction references |
| Workday simulation | Worker assignment revisions, names/DOB, employee numbers, managers, roles, FTE, costs, credentials, dates; cost centers/hierarchy; grants and explicit `REVOKED` decisions | RFC4180 CSV; weekly source-known history snapshots and scheduled daily changes |
| ROSTER_TIME | Scheduled and observed shift versions, breaks, productive/overtime/nonproductive hours and captured costs | Separate CSV history archives; no claim these arrive through a generic Workday HR extract |
| SUPPLY_PHARMACY | Lot, receipt, issue, transfer, return, waste and inventory correction movements | Additive transaction CSV archives |
| REVENUE_CYCLE | Service charges, original account headers, lines and immutable lifecycle events | CSV histories and additive transaction archives |
| FINANCE_ERP | Balanced journal lines and allocation-run details | Additive CSV transaction histories; alternative allocation runs remain explicit versions |
| Axiom simulation | Accepted actual, budget, forecast, volume and workforce statistics | Source-file-preserving CSV exports and six independently reconciled report mirrors |

CSV uses CRLF and quoted multiline text; event archives use LF. `\N` is the explicit null token; literal token/escape strings are escaped. Source timestamps use compact UTC offsets (`YYYYMMDDHHMMSS+0000`), with Workday-style `MM/DD/YYYY HH:MM:SS +0000`. Calendar dates use `MM/DD/YYYY`. Decimal text retains accepted precision exactly, without floats or extra rounding. Shorter fractional representations remain valid within the declared maximum scale.

Native patient MRNs and employee numbers are retained. Workday and Axiom cost-center references use `WO-` and `AX-` prefixes; Axiom accounts use `AX-<account code>`. Other version/message identifiers use deterministic source-specific opaque tokens and explicit field-typed dictionaries. Dictionary collisions, unmapped references and required null keys are rejected rather than inferred.

## Workday delivery and historical meaning

Daily worker/security change extracts are scheduled at 07:00 UTC after source availability. Empty expected dates are explicit header-only files through January 10, 2026. Opening changes retain their prewindow context. Weekly worker and cost-center **source-known revision-history** snapshots run on Sundays at 07:00 UTC from December 18, 2022 through December 28, 2025. A history snapshot includes source-known old revisions and terminated workers; it is not a list of only currently active staff. An effective workforce view selects the applicable stable-worker revision after both actual delivery and source knowledge, rather than treating every history row as a separate employee.

Manager references, hire/termination/transfer dates, credentials, retroactive revisions and security revocations come from the accepted histories. No new fictional workforce event is injected to make a scenario pass. Revocation selects the latest applicable grant decision; it never inherits an earlier allow through omission.

`AuditKnowledgeClosedAt` maps the canonical retrospective `known_to` helper. It is explicitly a historical reconstruction extension, not a claim the source knew a future correction. The replay omits this helper from every finite as-of view; version selection uses delivered revisions rather than hindsight closures. This also prevents a recording-time closure leaking before the successor's later delivery. The unrestricted reconstruction view retains the exact accepted helper values. Raw archive files contain the complete audited history after the simulation period; they are not suitable as historical model features without the documented replay/selection rules. Future valid dates can represent known planned changes; validity and knowledge remain separate.

## Axiom coverage

The customer described approximately **900 exports**, but supplied **zero actual layouts**. This package models **twelve illustrative archetypes**. The remaining approximately **888 inventory slots are unmodeled**, not assumed compatible. These are archetype counts, not verified counts of a customer's reports. Physical file count reflects periods, templates, scenarios, vintages and statistics splits, not 900 invented report definitions.

| Archetype | Meaning and independent control |
|---|---|
| actual-long | Complete accepted monetary actual rows, by original file/template, period and vintage |
| actual-wide-months | One annual row per center/account/measure/unit, twelve value and scalar record-ID columns; unpivot cells reconcile to selected latest actuals |
| actual-with-adjustments | Original December close, signed adjustment and final reported value; `original + adjustment = reported`; never additive to the primary actual feed |
| budget-original | Original plan monetary rows, with publication and target period retained |
| budget-revised | Midyear monetary revisions; separate plan vintages, not additions to original budget |
| forecast-amount | Quarterly published forecast amounts and target periods |
| forecast-drivers | Explicit daily plan rate derived from an already accepted monthly forecast divided by calendar days; not a new causal driver or model prediction |
| statistics-volume | Admission, patient-day and hours statistics and their declared units/scenarios |
| statistics-workforce | FTE statistics, preserving captured productive-hours basis rather than headcount |
| variance-comparison | Actual minus latest source-known budget, with explicit no-budget/zero-budget states and exact percentage rounding |
| account-mapping | Accepted account code, canonical key, description, classification and normal balance |
| center-mapping | Accepted center reference, canonical key, description, facility and parent |

All **231 original canonical finance file identities** and all report/template identities remain represented. Mixed statistics files can produce multiple physical files; their original identity is retained, not replaced with a guessed vendor layout. Actual replacement chains operate at exact template/period/scenario/statistics-family scope, preserving prior knowledge. Revised budgets and quarterly forecasts append their own vintages and must be selected, not summed together. December final actuals replace earlier December actuals even when a value is unchanged.

Publication times follow the accepted Phase 6 financial policy and actual canonical vintages. These supersede illustrative Phase 0 cadence strings such as 08:00 UTC close or first-business-day forecast. Accepted facts are not redated to an illustrative cadence. Budget statistics use the budget contract/publication, rather than being presented as actual-close statistics.

Wide/adjustment/driver/variance/mapping reports are explicitly derived mirrors. They never enter the primary financial fact stream. Monetary controls and quantities are reconciled separately by field/unit. The six derived reports are retrospective publications at the final accepted finance publication, not falsely backdated analytical features.
