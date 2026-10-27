# Gate, workload and migration contracts

**ADR-15 · Phase 0 · 2026-10-27**

**Status:** APPROVED by delegated technical review; funded POC scope explicitly approved by user.

**Context:** A syntactically valid design is not tenant integration or measured cost/performance. No laterphaseexit may be certified from Phase0 tests.

**Decision:** Every phase gate binds sourceSHA, contract/input hashes, nameddependency gates, targetenvironment, tests, measurements/costs/limitations/owner signoff. Frozen funded workload has explicit user scope approval recorded in design-review.json.

**Alternatives considered:** Passing unrun cloud probes; failing security exception markedPASS; cloud fullreruns aftereverymerge.

**Consequences and acceptance:** Mandatory integrity/auth/cost/recovery neverwaived. Design tests exercise contract mutations and negativegate behavior, not futurecloud implementation. ScopechangeusesADR+impactreview+newacceptancethenexecutes; failedmigrationsrestorecertifiedsnapshot or immutable-native rebuild.

**Contract:** [test-workloads.json](../../contracts/architecture/test-workloads.json). The [baseline review register](../../contracts/architecture/design-review.json) records accountability and approval scope.

**Rollback and evolution:** A changed decision requires versioned impact review, bounded migration/reconciliation/security/cost/recovery tests and a new gate before publication. Restore the previous code/configuration and certified state, or rebuild from immutable native deliveries. Do not rewrite the accepted source release or bypass a failed dependency gate.
