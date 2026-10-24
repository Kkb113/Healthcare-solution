# Integrated synthetic history validation

Phase 8 produces an integrated candidate and disposable acceptance consumers. It does not implement the healthcare analytics solution. Phase 9 release certification and explicit data acceptance remain required.

The primary candidate lives in ignored `output/integrated-history`; its native source simulation lives in `output/integrated-source-delivery`. Earlier accepted snapshots and their evidence remain immutable. The current candidate supersedes the earlier financial snapshot only after the [integrated gate](../../evidence/integrated-history/acceptance-gate.json) passes.

See the [candidate contract](candidate-contract.md), [record budget](record-budget-amendment.md), [consumer contracts](consumer-contracts.md), [validation and review](validation-and-review.md), [realism scorecard](realism-scorecard.md), and [runbook](runbook.md). The [integrated policy](../../contracts/integrated-validation-policy.json) and [generation configuration](../../config/integrated-history-generation.json) preregister seed experiments, calibration, budget, review and acceptance rules.
