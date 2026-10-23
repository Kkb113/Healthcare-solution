# Connected workforce and inventory foundation

Phase 5 implements the three-year workforce and selected resource-consumption foundation. The [acceptance gate](../../evidence/resource-foundation/acceptance-gate.json) is the authoritative completion record. The complete healthcare dataset and Azure Databricks analytics solution remain blocked until Phase 9. Microsoft Fabric is excluded.

The candidate contains **1,053,661 canonical rows across 18 populated tables**, including **66,582 staff-shift versions**, **47,839 inventory movements** and **561,909 clinical events**. The frozen release still has 25 tables, a 1,958,210-row plan and 41,790 rows of reserve. There are 904,549 planned rows remaining. No table or frozen contract was added or changed.

The accepted operational parent remains immutable. Fifteen of its sixteen canonical tables are byte-identical in this candidate, including all encounter, attending-of-record and bed histories. Clinical events acquire working source authors and inventory links; 788 operative services have coordinated timing changes and grounded resource-response notes. All fifteen clinical and seven operational check groups run again on the integrated candidate.

| Component | Retained business meaning |
| --- | --- |
| `staff_shift` | One immutable source assertion per logical roster/attendance revision; published plans, cancellations, absence, leave, actual attendance and corrections |
| `inventory_movement` | One signed item/lot/location/base-unit movement, with receipt valuation, provenance, transfer/return groups and linked reversal |
| `clinical_event` | Original care facts plus actual working source authors, scalar medication use, consumption-group references and 788 coordination notes |
| Existing masters | Named people, versioned worker assignments, employment, credentials, loaded rates, facilities, locations, cost centers and catalog conversions |

This represents selected source capture: it is not complete payroll, all hospital materials, an entire operative/anesthetic team or every ward cabinet. The [policy](../../contracts/resource-foundation-policy.json) defines the boundaries. Cost inputs are recomputable source quantities, not financial postings or patient-level cost allocations. Workday-style workforce authorities are retained; native source exports and Axiom financial scenarios follow in their planned phases.

Read the [generation design](generation-design.md), [runbook](runbook.md), [validation and review](validation-and-review.md), [100-case review](../../reviews/resource-foundation-sample.md) and [review decision](../../reviews/resource-foundation-review.json). Generated business data and recovery checkpoints remain in ignored `output/`; only code, policy, selected review and acceptance evidence are versioned.
