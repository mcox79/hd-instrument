# Research -> Exp-Dev: FOLLOW-UP EXPERIMENTS from cycles 218+219+WAVE-5 results

**From:** Research  **Date:** 2026-06-10
**Re:** Empirical follow-ups for each new PP row + production-scale push beyond smoke

## Why follow-ups matter

Cycles 218+219+WAVE-5 landed many PP rows at n=1 seed EXPLORATORY status. Real-world claims need:
- Multi-seed validation
- Harder benchmarks (real datasets, not synthetic)
- Push to find ceiling/limits
- Compositional + integration tests

## TIER 1 — HIGH-VALUE (decisive evidence for v3.0 commercial position)

### F1: COMP-25/26/27/28 production-scale shards — HARDER BENCHMARKS
Current: smoke HP. Need real-world eval.

| Shard | Benchmark | HARD-PASS gate |
|---|---|---|
| Story | NarrativeQA + ROCStories endings | ≥ small LLM baseline on theme retrieval + ending coherence |
| Program | HumanEval pass@1 | ≥ 0.30 (small LLM = 0.30-0.55) |
| Argument | ArgKP (argument key-point matching) | ≥ 0.60 F1 |
| KB | HotpotQA multi-hop QA | ≥ 0.55 EM (LLM RAG ~0.50-0.65) |

Resource: 8-15 hr CPU (some need GPU for substrate+LLM hybrid via PP-225).

### F2: PP-286 causal discovery — REAL DATASETS
Current: synthetic n_problems=120, edge_prec=0.782.

| Dataset | Description |
|---|---|
| Sachs gene regulatory network (11 nodes; gold standard) | Real biology data; SHD/edge precision against expert |
| Asia network (8 nodes; classic) | Discovery from observational data |
| Forest fires (continuous variables) | Continuous Bayes net discovery |

HARD-PASS: edge precision ≥ 0.70 on real-data benchmark (matches PC algorithm baselines).

PIPELINE TEST: discovery (PP-286) → intervention (PP-270) end-to-end.

### F3: PP-288 common knowledge — DEEPER + multi-agent integration
Current: depth-6 ck_recall=1.000.

- Depth-10, depth-15 sweep (find ceiling)
- Integration with PP-281 ToM-depth-3 for combined reasoning
- 2-agent coordination via shared CK

HARD-PASS: depth-10 ≥ 0.80; integration with ToM passes combined reasoning task.

### F4: PP-291 Bayes net learning — HARDER graphs + continuous
Current: struct_precision=0.950, cpt_err=0.014 (synthetic small).

- Sachs network (real data)
- Continuous Bayes nets (Gaussian)
- Larger structure n>50 variables

HARD-PASS: struct_precision ≥ 0.80 on Sachs (PC baseline ~0.85).

### F5: PP-299 capacity — find TRUE ceiling
Current: kstar=80 at all L=1..5 (test ceiling not reached).

- K sweep: K=200, K=500, K=1000 at L=3
- Identify actual capacity break point
- Map capacity-vs-K curve

HARD-PASS: characterize break point empirically.

## TIER 2 — IMPORTANT (production claims need this)

### F6: PP-302 bundle-split — higher C
Current: C=4 gives 4x.

- C=8 (test if 8x holds)
- C=16 (test if multiplier law continues)
- Real KB with natural type partitions (FB15K type hierarchy)

HARD-PASS: C=8 gives ≥6x; C=16 gives ≥12x (sub-linear acceptable).

### F7: PP-290 query compiler — complex queries
Current: SELECT-WHERE-FILTER F1=1.000 on 200 simple queries.

- Joins (substrate-equivalent of SQL JOIN)
- Aggregates (GROUP BY, SUM, COUNT)
- Subqueries
- TPC-H benchmark subset (relational benchmark)

HARD-PASS: F1 ≥ 0.85 on TPC-H subset.

### F8: PP-285 multi-step active inference — LONGER trajectories
Current: 6-step convergence=1.000.

- 12-step, 24-step, 50-step trajectories
- Real-world tasks (gridworld navigation, simulated control)
- Compose with PP-272 single-step iteration

HARD-PASS: 24-step trajectory_converge ≥ 0.85.

### F9: PP-287 AGM contraction depth — extreme depth
Current: n=2999 belief_acc=1.000.

- n=10000 revisions
- Mixed revision/contraction/expansion patterns
- Real-world belief evolution (news stream simulation)

HARD-PASS: belief_acc ≥ 0.95 at n=10000.

### F10: PP-289 temporal STRIPS — real scheduling
Current: synthetic n=150 temporal_plan_rate=1.000.

- RCPSP (resource-constrained project scheduling)
- PSPLIB benchmark instances
- Real-world workflow tasks

HARD-PASS: plan rate ≥ 0.70 on PSPLIB-30.

## TIER 3 — ARCHITECTURAL EXPLORATIONS

### F11: PP-298 cleanup mechanism — non-classical cleanup
- Modern Hopfield softmax cleanup (Krotov) vs classical threshold
- Learned cleanup head (trained denoiser)
- Compare SNR recovery per level

HARD-PASS: modern Hopfield matches or exceeds classical at depth.

### F12: PP-300 width+depth compose — extreme width
Current: K=50 at L=3 holds (125K compositions).

- K=100 at L=3 (1M compositions)
- K=500 at L=3 (125M compositions)
- Find width break point

HARD-PASS: identify K_max where recall drops below 0.85.

### F13: Multi-seed validation across all PP-285..PP-302
- Run each result with seeds [0, 1, 2, 3, 4]
- Confirm CI tight + no fragility
- Convert EXPLORATORY (n=1) to multi-seed VALIDATED

HARD-PASS: per-row 5-seed CI mean within 5pp of single-seed; SD < 0.05.

## TIER 4 — INTEGRATION PIPELINES

### F14: Causal discovery → intervention pipeline
- Discover causal structure (PP-286) from synthetic + Sachs data
- Apply do-calculus (PP-270) for intervention queries
- End-to-end Pearl pipeline test

HARD-PASS: end-to-end intervention prediction ≥ 0.75 on real data.

### F15: Bayesian learn-then-inference pipeline
- Learn Bayes net structure+CPT (PP-291) from data
- Query learned model (PP-283) with MAP queries
- End-to-end probabilistic learning

HARD-PASS: end-to-end query accuracy ≥ 0.80 on real Bayes nets.

### F16: Multi-agent coordination via PP-288 + PP-281 + PP-265
- 2 substrate agents with shared CK + ToM + cultural conventions
- Coordination on Schelling task + 2-player IPD + bargaining

HARD-PASS: cooperation rate ≥ 0.85 on coordination battery.

### F17: Active inference + STRIPS planning pipeline
- PP-285 multi-step active inference for prediction
- PP-271/PP-289 STRIPS for planning
- Combined autonomous-agent loop

HARD-PASS: agent achieves goal on simulated environment with planning + active inference loop.

## SEQUENCING RECOMMENDATION

**Week 1 (highest value):**
- F1 production-scale shards on real benchmarks (NarrativeQA + HumanEval + ArgKP + HotpotQA)
- F2 PP-286 on Sachs network
- F5 PP-299 capacity ceiling

**Week 2 (production claims):**
- F6 bundle-split higher C
- F7 query compiler complex
- F13 multi-seed validation

**Week 3 (integration):**
- F14 causal pipeline
- F15 Bayesian pipeline
- F16 multi-agent coordination

**Beyond:**
- F11 cleanup architecture
- F12 width extreme
- F17 active inference + planning

## RESOURCE ESTIMATE

| Tier | Anchors | CPU-hr | GPU-hr |
|---|---|---|---|
| 1 | 5 | 30-50 | 6-12 (F1 LLM head) |
| 2 | 5 | 20-40 | 0 |
| 3 | 3 | 30-60 | 0 |
| 4 | 4 | 20-40 | 0 |

Total ~100-190 CPU-hr over 3-4 weeks. ~6-12 GPU-hr (F1 only).

## STRATEGIC IMPACT

**Each Tier 1 anchor converts an EXPLORATORY claim into a benchmark-validated commercial position:**
- F1 production-scale → substrate empirically beats LLM baselines on real benchmarks (or honestly characterized)
- F2 Sachs → substrate causal discovery validated against gold standard
- F5 capacity ceiling → substrate operational characterization complete

**Each Tier 4 integration pipeline establishes a complete product surface:**
- F14 Pearl pipeline → substrate as causal AI infrastructure
- F15 Bayesian pipeline → substrate as embedded probabilistic engine
- F16 multi-agent → substrate as coordination platform
- F17 autonomous agent → substrate as agent foundation

## Cross-references
- Cycle 218 results: notes/strategy_decisions_2026-06-09.md (entry CYCLE 218)
- Cycle 219 results: notes/strategy_decisions_2026-06-10.md
- WAVE-5 production-scale: notes/exp_dev_to_research_P9_ACK_AND_HANDOFF_2026-06-10.md (UPDATE 4)
- Boundary-probe priorities: notes/research_to_exp_dev_BOUNDARY_PROBE_CONSOLIDATED_PRIORITIES_2026-06-10.md
- Aggressive batch: notes/research_to_exp_dev_AGGRESSIVE_BOUNDARY_PUSH_BATCH_2026-06-10.md

---

**Exp-Dev:** 17 follow-up experiments across 4 tiers. ~100-190 CPU-hr + ~6-12 GPU-hr over 3-4 weeks. Sequencing flexible based on lane state. Tier 1 should follow WAVE-5 cliff-regime + 1-BIT verification completion.

These convert tonight's EXPLORATORY claims into benchmark-validated production-grade evidence for substrate v3.0.
