# Research -> Exp-Dev + Orchestrator + Testbed: v1 plan update + 7 authorizations

**From:** Research session
**To:** Exp-Dev (primary) + Orchestrator + Testbed
**Date:** 2026-06-07
**Trigger:** User authorized all recommendations from morning + multi-hop drill results.

---

## Context

Cell A came back this morning with c_d_empirical = 0.48 (real Llama embeddings; smoke).
That's above the 0.40 HARD-FAIL band for "the 50-LOC averaging+confidence filter is
sufficient." The cheap v1 distributed-reasoning fix is not enough on real data.

Four multi-hop drills landed (shard-count sanity check, distributed coordination patterns,
substrate-native coordination, biological coordination). Their combined finding: there are
two cheap distributed-reasoning mitigations that might work at c_d=0.48 where naive
averaging won't -- soft-Krum (federated-learning style robust aggregation) and immune-style
corroboration gating.

Each takes about 1 week to implement. Both have cheap decisive tests (laptop CPU, < 5 min).

R3 anisotropy confirmed earlier today (PR/D=0.16, top-10pct dims hold 62pct energy);
SRHT engineering is greenlit but empirical validation blocked on attack-methodology
reconciliation (separate note already filed).

CELL-2 v3 left-padded Wikipedia cache extraction completed overnight (5.84M articles,
21 GB on disk, $26.58 actual). CELL-3 and CELL-4 are unblocked.

---

## 7 authorizations

### 1. CELL-3 distilled 22M student: AUTHORIZED for dispatch

- Spec: feature-mimic via MSE on the 21 GB Wikipedia cache; train from BASE (Q4 lock); ~22M parameter student.
- Latest processes: uses left-padded cache (Q4 lift), trained from BASE not LoRA (Q4 HF lock), MSE not SFT (Drill B finding).
- Safety stack: 4-layer baseline (hardened launcher, kill switch, 5-min rsync, watchdog).
- Budget: ~$5-15 GH200 (smaller than CELL-2; encoder forward only).

### 2. CELL-4 HP-12 V2 at 100K facts: AUTHORIZED for dispatch with one check

- Spec: pseudoinverse (cycle 143/148 lock) + PCA whitening + left-pad + HNSW ef_search=256; 100K facts from CELL-2 cache.
- Check before dispatch: confirm CELL-4 includes multi-head H=2 setup (cycle 149 production point). If not, add this to the script before launch.
- Latest processes: production recipe at cycle 152 state.
- Safety stack: 4-layer baseline.
- Budget: ~$5-15.

### 3. v1 distributed reasoning architecture: Option C+ (try two cheap mitigations in parallel)

Rather than committing to either Option A (single-shard v1) or Option B (3-4 week semantic
sharding before v1 ships), spend 2 weeks running the two cheap-decisive tests of Option C+
in parallel. Each tests one mitigation against the c_d=0.48 reality.

- **Mitigation 1 -- soft-Krum confidence-weighted bundling.** From the distributed coordination
  patterns drill (Pattern 1; FedHDC + Krum literature; P=0.68 at v1). Each shard returns
  (embedding, confidence). Coordinator weights each contribution by mean cosine similarity
  to its neighbors among all contributions. Outlier wrong-answer shards have low weight.
  Cheap decisive test: 16-shard synthetic harness with c_d=0.28-0.48 injected coherent
  distractors at B=10, K=12. Pass: K-hop end-quality > 80%.
- **Mitigation 2 -- immune-style corroboration gate.** From the biological coordination
  drill (Pattern 2; P=0.40 at v2 but plausible at v1). High-confidence shards gossip to
  K=3-5 nearest-neighbor shards; corroborating neighbors send CORROBORATE, non-finding
  neighbors send DAMP. Bundle includes only majority-corroborated contributions.
  Cheap decisive test: 16-shard, 5 adversarial, 3 gossip rounds. Pass: adversarial content
  in final bundle < 5%.

Both tests run in < 2 minutes on laptop CPU. Decision rule:

- Both pass at c_d=0.48: ship distributed reasoning in v1 with both mitigations.
- Only soft-Krum passes: ship distributed reasoning in v1 with soft-Krum only; queue
  corroboration gate for v1.1.
- Only corroboration gate passes: ship v1 with corroboration gate only; queue soft-Krum
  for v1.1.
- Both fail: fall back to single-shard v1 (Option A). Queue semantic sharding for v1.1.

**Engineering owner:** Exp-Dev for the two cheap-decisive tests. Each ~1 week.

### 4. Sparse-W deployment in v1 spec: AUTHORIZED for inclusion (subject to production-readiness check)

The shard-count drill flagged sparse-W as a 10x infrastructure cost reduction. v1 hardware
cost goes from $10-30K/month to $1-3K/month if deployed.

- Confirm with Orchestrator/Exp-Dev that sparse-W is production-ready at cycle 142+148
  validation level.
- If yes, add sparse-W to v1 spec as default storage mode (configurable to dense for
  high-throughput write workloads).
- If no, flag the gap so it can be closed for v1.

### 5. SRHT empirical validation: methodology spec already filed (separate note)

Filed at notes/research_to_exp_dev_ZKL_attack_methodology_spec_2026-06-07.md. Exp-Dev
needs to reproduce the cycle-150 synthetic baseline (target ZKL(50) ~ 0.035) and
cycle-151 real-key baseline (target ZKL(50) ~ 0.40) before measuring SRHT recovery.
R3 anisotropy result stands and still justifies SRHT engineering. No additional
authorization needed beyond what was already greenlit this morning.

### 6. Benchmark suite definition: Research session owns

Research is starting the benchmark suite definition work today. Deliverable: concrete
list of head-to-head benchmarks vs 1B-class LLMs (Llama-3.2-1B BASE, Phi-2, similar),
why each one plays to substrate strengths, and what scores would constitute a
demonstrable win. Estimated 1-2 weeks. Will deliver via a benchmark-design drill note
and a routing note to Exp-Dev for benchmark cell dispatch.

### 7. Queued for later (do not act on now)

- Pheromone-style temporal decay on confidence weights: v1.1 nice-to-have, 2-4 weeks
  engineering. Queue but do not block v1.
- Background defragmentation (hippocampal sleep-replay analog): v2/v3 research direction,
  2-3 months. Queue as v2 research target.
- Stigmergy / ant colony reinforcement learning: v3 research direction.

---

## Cross-references

- 8-authorization morning routing: notes/research_to_orchestrator_exp_dev_8_authorizations_morning_2026-06-07.md
- SRHT methodology spec: notes/research_to_exp_dev_ZKL_attack_methodology_spec_2026-06-07.md
- Cell A result: notes/exp_dev_to_research_8auth_R3_cellA_results_2026-06-07.md
- Shard-count sanity drill: notes/research_drill_shard_count_sanity_check_2x_2026-06-07.md
- Distributed coordination patterns drill: notes/research_drill_distributed_coordination_patterns_3x_2026-06-07.md
- Substrate-native coordination drill: notes/research_drill_substrate_native_coordination_3x_2026-06-07.md
- Biological coordination drill: notes/research_drill_biological_distributed_coordination_2x_2026-06-07.md
- Sparse-KEY low-B reconciliation drill: notes/research_drill_sparse_key_low_B_regime_reconciliation_2x_2026-06-07.md
- North star memory entry: ~/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md
- Plain-language feedback: ~/.claude/projects/d--AI/memory/feedback_plain_language_no_hype.md

---

**END.**

**Exp-Dev:** authorize the 7 items above. Items 1-3 are dispatch-actionable now. Item 4 needs
a production-readiness check on sparse-W. Item 5 is already in flight. Item 6 is Research's
work. Item 7 is queued for later.

**Testbed:** CELL-3 + CELL-4 dispatch authorized; CELL-4 needs the multi-head H=2 setup check
before launch.

**Orchestrator:** track Option C+ progress; verdict either mitigation works at c_d=0.48 and
ships in v1, or fall back to single-shard v1 plus semantic sharding for v1.1.

**User:** all 7 authorizations confirmed.
