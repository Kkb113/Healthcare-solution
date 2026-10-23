# Reviewed financial record budget

The original 25-table baseline remains immutable as historical design evidence. Phase 6 records a specific additive amendment in [the financial policy](../../contracts/financial-history-policy.json), approved within the business owner's delegation to Codex to review/finalize the synthetic design. No new table or nested fact container is introduced.

| Table | Original envelope | Financial envelope | Reason |
|---|---:|---:|---|
| catalog_item | 3,000 | 3,005 | Five local room/ICU/ED/ambulatory/extended-holding codes; every accepted vocabulary row is preserved. |
| claim | 56,000 | 58,000 | Retain original patient-statement accounts for completed SELF_PAY visits, alongside insured originals. |
| claim_line | 112,000 | 117,000 | A charge has one original institutional billing line, including self-pay statements. |
| claim_event | 160,000 | 220,000 | Include patient statements, internal responsibility confirmations, variable insured/patient collections, staged remittances and final credit losses. |
| cost_allocation | 180,000 | 165,000 | Reassign unused envelope after complete resource, salary and boarding allocation; no source/driver/allocation is truncated. |
| clinical_condition | 95,000 | 85,000 | Retain all 79,103 accepted versions and 5,897 rows of headroom. |
| inventory_movement | 60,000 | 55,000 | Retain all 47,839 accepted movements and 7,161 rows of headroom. |
| All other tables | Unchanged | Unchanged | Source histories and financial-posting/allocation/Axiom allowances remain intact. |

The planned envelope increases by **37,005**, from **1,958,210** to **1,995,215** canonical rows. Reserve falls from **41,790** to **4,785**, below the user's **2,000,000** ceiling. Every opening, correction, allocation version, planning vintage and original statement row counts. Actual counts come from the acceptance manifest; envelopes are not quotas. Unused capacity inside table envelopes is also retained; future changes must pass both table and global checks.

The `claim` grain now explicitly includes an original SELF_PAY institutional patient-statement account. Coverage/payer type differentiates it from an insured original. Its SUBMITTED event means a patient statement was issued; ADJUDICATED means internal discount/responsibility confirmation. Neither is an external payer transmission/adjudication. Payer denial denominators exclude SELF_PAY and opening accounts, and include only insured originals with observed initial adjudication/denial. Resubmissions never create another original.

Without this amendment, uninsured visits or most insured patient balances would remain uncollected for three years, or relevant business events would be omitted to satisfy an envelope. The accepted approach retains these connected histories and keeps the user's total/table limits. Completed prewindow SELF_PAY contexts are settled before the window and generate no opening AR. Open visits and cutoff drafts remain explicit. A calibration check requires more than half of original accounts to be settled by the final cutoff; this is a synthetic design target, not an asserted industry benchmark.

Accepted parent snapshots are not regenerated or edited. Canonical rows, checkpoint mirrors, review mirrors and physical serialized copies are reported separately; the two-million canonical cap is not a claim about all physical copies.
