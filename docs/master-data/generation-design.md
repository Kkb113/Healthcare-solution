# Master generation and business rules

## People and identity

Patient identities are persistent typed source keys with separate immutable version IDs and unique MRNs. First names use imported SSA birth-decade weights; surnames use Census 2010 aggregates. No name is a primary key. Surname case normalizes the `Mc` prefix, while legitimate repeated names, initials, suffixes, hyphenation and addresses remain valid.

The source name data are curated before sampling: registration labels such as `Unknown`, `Infant`, `Babyboy`, `Babygirl`, `Male` and `Female` are explicitly excluded and their original aggregate counts recorded. A second-seed test exposed this distinction between an authoritative public file and a suitable person-name pool. A genuine surname such as `Sample` remains valid.

Birth dates use real calendar month lengths and the frozen Feb-28 convention for Feb-29 birthdays in nonleap years. Patients are 18–100 at the start of the service window. Names use the relevant birth cohort, with a configured small cross-series component so administrative attributes are never inferred from a first name. Race/self-report is drawn first; probabilistic Census surname weights and a 5% cross-population component then support plausible names without changing or imputing that self-report. Unknown self-report uses marginal surname weights. The opening-health generator does not read names or race.

The configured demographic shares, language mix, history rates, pay factors, payer contracts and morbidity weights are fictional project assumptions. The validator checks them against predeclared bands. They are not presented as measured US hospital benchmarks. Optional gender self-report is usually absent; where present it is probabilistically coherent with administrative fields and can differ. Unknown, declined and absent values keep separate semantics.

Addresses are constructed fictional street/number/apartment combinations in three explicitly modeled Illinois city/postal areas. Six thousand people share addresses in pairs; incidental additional collisions are retained. A shared address is not proof of household or family membership. The adult baseline requires no guardian or household table, and temporary anonymous emergency identities remain out of scope as frozen in the design.

Email uses a name plus opaque token under `patients.example`. Phones use the reserved US `555-0100`–`555-0199` range in configured Illinois area codes. Contacts may be missing and are not unique identity keys. No real personal contact/address record was imported. A null `deceased_at` means no recorded death in this opening/master scope, not a survival label; clinical outcome-driven death revisions belong to the clinical-history generator.

## Bitemporal histories

One observed effective change uses three rows: the original knowledge version, a retrospectively closed old business segment, and the new business segment. Validity and knowledge use half-open intervals. Source recording and export availability are explicit; consumers cannot use a revision before it is available.

Patients have 1,000 changes: 500 surnames, 300 addresses and 200 middle-name corrections. Two additional rows per change give exactly 22,000 versions. No change creates another person. Typed source IDs and MRNs persist even when source display names change.

Workers have 900 versions: 264 people with one renewal/rate/assignment change (three rows each), 18 later hires with one row, and 18 people with a renewal followed by termination (five rows each). Their source knowledge delays demonstrate retroactive cost/assignment corrections without changing an earlier as-of answer. Twenty-four nurses move between compatible medicine/surgery primary assignments; their actual cost center changes too. Manager references use stable identities, resolve as of both times, and form a multilevel hierarchy. Leaders remain available while supervising staff.

## Workforce and capacity

All eight frozen worker roles are represented: 45 physicians, 126 RNs, 12 LPNs, 12 therapists, 12 technicians, six pharmacists, 12 environmental-service workers and 75 administrative workers. Specialties resolve compatible home services and role credentials; pharmacy, laboratory/imaging, finance and HR responsibility are distinct. Source payroll interpretation is configured by role/employment type: employee physicians/admin use salary-equivalent loaded hourly costs, while other/agency/contract work uses modeled hourly costs.

There are 270 employees, 18 agency workers and 12 contractors. Loaded rates vary within configured role ranges, with explicit agency/contract premiums and a renewal factor. FTE values vary; the 180 rostered workers average exactly 0.65 FTE, preserving the frozen feasibility model. Credentials are synthetic eligibility intervals, not a claim of verification against a real license registry. Hires, terminations, credentials and source knowledge must all be respected by later shift generation.

Each hospital has 15 financial centers and 50 locations: four departments, eight units, 14 rooms and 24 inpatient beds. Ten two-bed general rooms and four single-bed ICU rooms give 20 general beds plus four ICU beds per hospital. Capability and isolation flags describe placement suitability; they do not create occupancy, availability or staffed-bed facts. Opening bed states and actual capacity changes remain operational-generation work.

## Coverage, access and source links

Sixteen stable payer contracts and four products with old/new versions form 24 contract rows. Coverage is an interval history rather than a static patient attribute: 20,000 opening enrollments plus 4,000 scheduled renewals and 4,000 other changes yield 28,000 rows. One primary plan applies continuously, including explicit self-pay. The scoped Medicare model uses age eligibility without modeling disability-based exceptions; age is checked on the actual enrollment boundary, including pre-window opening context. This is a synthetic scope rule, not benefits advice.

Contract expirations and planned enrollment changes may be known before their effective dates. Renewal knowledge is recorded before activation; unobserved clinical or claim outcomes are not fabricated. An old demographic assertion FK remains traceable after a patient correction; current attributes resolve through the stable patient identity.

One hundred fifty synthetic analytics principals have 900 initial read-only grants. Four hundred fifty grant changes produce 1,800 total rows, retaining 450 active and 450 revoked current scopes. Typed facility/location/center/network keys are validated; `ALL_NETWORK` is the only network sentinel. These data grant no live permissions. Consumer probes deny revoked grants and workers outside eligible employment/credential periods.

The crosswalk budget contains 6,382 patient aliases, 900 worker aliases across three namespaces, 150 location aliases, 90 center aliases, 2,400 catalog aliases, 24 payer aliases and 54 unit-finance association intervals. Eighteen of the 36 initial unit associations change financial responsibility. The crosswalk is a bounded alias/association map, not a requirement to duplicate every canonical source key. Primary source identifiers are already present on every master row and resolve via explicit stable-ID views; unknown namespaces are never guessed.

Pure source-format test adapters demonstrate patient component-name formatting, Workday employee/manager/cost-center references, and Axiom center references. They are not complete vendor-certified exports. The full Workday/Axiom layout and recovery work remains in the source-generation phase.

## Opening health and vocabulary

Twelve thousand active problem assertions use six selected ICD-10-CM codes, with configured age-dependent stochastic weights. One thousand allergy assertions point to typed allergen families and explicit reactions. Onset precedes source knowledge, assertions use the applicable opening code release, and there are no fabricated encounter links. A missing problem assertion means unknown/out of scope rather than confirmed absence. No treatment order, medication dose schedule or future clinical outcome is generated here.

The 3,000-row catalog covers all nine frozen domains. Its 200 local entries have explicit units, medication formulation/strength/pack conversion/allergen links, 17 financial accounts with correct class/normal balance, and readable supply/service/denial definitions. Local references remain clearly distinguished from official coding systems. Future care generation must implement and review order-specific dose/route/allergy rules; this catalog alone does not validate treatment content.
