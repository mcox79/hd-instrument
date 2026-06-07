# exp_dev hand-off -- research: bitemporal storage implementation spec (Chain 2 / Drill 3)

**Filed:** 2026-06-07 by research sub-agent (Chain 2 / Drill 3 delivery).

**Trigger:** Drill 3 produced a concrete 7-component implementation spec for substrate-native
bitemporal storage. The spec is close enough to code that a cheap decisive test is actionable:
build Component 1 (fact schema, ~200 lines) + 100-fact smoke test in 1 day to de-risk the
full 6-week build.

**Research note path:**
  notes/research_drill_substrate_developer_experience_5x_chain2_drill3_2026-06-07.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only.
exp_dev designs all numerical parameters, thresholds, seed counts, queue routing.

---

## Anchor candidates (rank-ordered)

### Anchor 1: Bitemporal smoke test (Component 1 + DuckDB adapter validation)

**Anchor pointer:** Drill 3 Section "CHEAP DECISIVE TEST" + Components 1 and 4.

**Substrate-product reading:** The 1-day smoke test (Component 1 schema + 100 facts + temporal
queries + retroactive correction + Merkle root verification) de-risks the full 6-week build.
If retroactive correction breaks the DuckDB shadow table, the adapter design must be revised
before committing engineering resources.

**Tier hint:** CPU laptop. <1 second execution. No GPU required. No torch usage.

**Why now:** This is the blocking prerequisite for regulated-market entry (healthcare/legal/finance).
HP threshold: as_of_valid(T) DuckDB latency <10ms; retroactive correction round-trip <500ms.
HF threshold: retroactive correction fails to produce both versions queryable.

---

### Anchor 2: GDPR erasure + snapshot invalidation correctness probe

**Anchor pointer:** Drill 3 Part 5 (GDPR deletion) + Part 7 item 7.4 (snapshot invalidation under
concurrent reads). This is the identified main engineering risk.

**Substrate-product reading:** The rank-1 pinv downdate + bitemporal audit marker combination
is a stronger compliance story than XTDB (which does logical deletion only, not physical vector
erasure). Verifying the correctness of snapshot invalidation (that as_of_system before erasure
returns erasure_marker, not content) is a correctness gate, not a performance gate.

**Tier hint:** CPU laptop. Build requires Component 1 + Component 6 (GDPR API, ~300 lines).
Prerequisite: Anchor 1 passes first.

**Why now:** This is the novel engineering risk with no direct prior art. If the snapshot
invalidation design is broken, the spec must be revised before full build proceeds.

---

### Anchor 3: DuckDB sync throughput under burst

**Anchor pointer:** Drill 3 Part 4.3 (sync latency analysis). Pre-reg: DuckDB Appender achieves
~160K rows/sec; at V1 write rates (<100/sec) sync should not be a bottleneck.

**Substrate-product reading:** Confirms (or refutes) that synchronous DuckDB sync is adequate
for V1 deployment. If sync latency exceeds 1ms per write at 100 writes/sec, async queue
required (adds complexity). Low priority given the throughput analysis; run only if Anchors
1+2 pass and DuckDB is showing unexpected latency.

**Tier hint:** CPU laptop. Microbenchmark. Prerequisite: Anchor 1 passes.

**Why now:** Deferred -- only run if Anchor 1 reveals sync latency concerns.

---

## Context pointers

- Research note (full spec): notes/research_drill_substrate_developer_experience_5x_chain2_drill3_2026-06-07.md
- Prior drill (XTDB verdict = Option B): notes/research_drill_substrate_developer_experience_5x_chain2_drill2_2026-06-07.md
- Adjacent (API design): notes/research_drill_substrate_native_API_design_2026-06-07.md
- Cap map: data/substrate_capability_map.md
- Status log: data/orchestrator_status_log.jsonl (research_delivery entry filed)

---

## Contract

The research note provides:
- Full Pydantic schema for BiTemporalFact (Section 1.1) -- ready to code
- DuckDB adapter class skeleton with SQL queries (Section 4.2) -- ready to code
- Write hook integration point (Section 6, Component 7) -- one-line substrate change
- Pre-reg HP/HF thresholds (Section 8) -- use these as exp bands

exp_dev owns: anchor names, queue routing, exact test matrix, seed count, run mode.

## Autonomy declaration

exp_dev is authorized to implement the cheap decisive test (Anchor 1) directly without
further orchestrator approval. Anchor 2 requires Anchor 1 to pass first. exp_dev decides
whether to combine Anchors 1+2 in a single session or sequence them.
