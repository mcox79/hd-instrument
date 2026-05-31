# Testbed Track Queue v2 — Path D production track (filed 2026-05-30)

Routed from experiment-session research plan 2026-05-30. Triggered by v288 cap_map
finding: **Path D (Bayesian path-probability propagation) is the production-scale
robust mechanism.** Supersedes the Path B emphasis in
`testbed/TESTBED_TRACK_QUEUE_2026-05-30.md` for all multi-hop work.

The earlier queue's READY items (Q3 composition latency, Q4 cold/warm timing,
Q11 failure recovery) remain valid as parallel-track production-engineering work
not dependent on Path D primitives.

## Tier 3: Path D production engineering (10-12 weeks total, mostly parallel)

| Pri | Test | Item                                     | Cost            | Blocked on              |
|-----|------|------------------------------------------|-----------------|-------------------------|
| 1   | T10  | Posterior maximization optimization      | 3-4wk + 5-10 GD | **S2 verdict**          |
| 2   | T11  | Path D batch parallelism                 | 2-3wk + 3-5 GD  | T10 primitives          |
| 3   | T12  | Path D GPU implementation                | 3-4wk + GPU     | T10 primitives          |
| 4   | T13  | Path D with cached path priors           | 1-2wk           | T10 primitives          |

**Gating verdict:** S2 (latency_crossover_analysis) — identifies exact bottleneck
cells where optimization will have leverage. Currently running in experiment-session
S-batch.

### T10. Posterior maximization optimization

Path D's S1-identified bottleneck: `time_posterior_max` dominates in 196/240 cells.

**Optimization knobs:**
- Vectorize across candidate paths
- Approximate maximization with refinement
- Parallelize across paths
- Cache stable computations across hops

**Grids:** M=8192 d=5 K=1000 (typical) / M=8192 d=10 K=5000 (intensive) /
M=24576 d=5 K=500 (past sub-capacity).

**Success:** 5-10x latency reduction at the bottleneck, accuracy preserved within 1%.

**Strategic value:** Path D as production mechanism needs production latency.

### T11. Path D batch parallelism

Multiple Path D queries simultaneously. Batch sizes [1, 4, 16, 64, 256]. Mix:
similar queries (share computations) and different queries (independent).

**Success:** batch 64 -> >= 50x throughput vs single query.

**Strategic value:** production LLM applications issue concurrent queries.

### T12. Path D GPU implementation

Port Path D to GPU. Substrate likelihood queries (already validated GPU baseline
at 22.67x), Bayesian update on GPU, posterior maximization on GPU.

**Grids:** M in {2048, 8192, 24576}, depth in {5, 10, 15}, K in {500, 1000, 5000}.

**Success:** 10-50x end-to-end speedup, killer features pass.

**Strategic value:** combined with batching, GPU Path D delivers production-grade
latency.

### T13. Path D with cached path priors

Cache priors keyed by query type. Hit: skip enumeration. Miss: compute normally.
Invalidate on substrate updates. Audit chain extends to cache hits. Test on Zipfian.

**Success:** hot queries <10ms via cache; audit chain valid; invalidation correct.

**Strategic value:** closes hot-path latency gap with FAISS for skewed distributions.

## Tier 4: LLM integration with Path D

| Pri | Test | Item                                            | Cost          | Blocked on        |
|-----|------|-------------------------------------------------|---------------|-------------------|
| 5   | T17  | Hybrid substrate-LLM multi-hop for extreme depth| 3-4wk + $     | T10 + Path D in testbed |

### T17. Hybrid substrate-LLM multi-hop for extreme depth

Substrate Path D executes until ambiguity threshold. At ambiguity, return top-K
candidates with confidence scores to LLM. LLM picks continuation. Substrate
resumes. Test depths 10, 15, 20.

**Success:** depth 15+ with 50%+ less token consumption than LLM-only at same
depth.

**Dependencies:** T10 (latency optimization) recommended first.

## Tier 5: Production stress + competitive comparisons (weeks 10-16)

| Pri | Test | Item                                            | Cost            | Blocked on            |
|-----|------|-------------------------------------------------|-----------------|-----------------------|
| 6   | T18  | Sustained Path D multi-hop workload (24-72h)    | 1wk + multi-day | Path D in testbed     |
| 7   | T19  | Substrate vs vector DB comprehensive comparison | 3-4wk + $       | Path D in testbed     |
| 8   | T21  | Multi-tenant substrate isolation under load     | 2-3wk           | none (was Q10 ready)  |

### T18. Sustained Path D multi-hop workload

1000 Path D multi-hop queries/hour for 24-72 hours. Continuous edit/delete + audit
chain verification interspersed.

**Success:** 24+ hour sustained operation, throughput within 10% of initial, audit
chain 100%.

### T19. Substrate vs vector DB comprehensive comparison

Substrate (Path D multi-hop) vs FAISS, Pinecone, Weaviate on identical workloads:
single-fact retrieve, edit-then-query, delete-then-query, multi-hop, audit chain,
multi-tenant (50 tenants).

**Measure:** throughput, latency, cost, killer feature presence/absence.

**Success:** comprehensive competitive data published; clear customer guidance.

**Strategic value:** customer-facing positioning data.

### T21. Multi-tenant substrate isolation under load

K=50 substrates simulating 50 customer tenants. Independent fact corpora, shared
codebook, continuous operations across all tenants. Cross-tenant leakage test.

**Success:** 100% cross-tenant isolation; per-tenant performance independent.

**Note:** This is Q10 from the prior queue — does NOT require Path D primitives in
testbed; can extend existing `sharded_substrate.py`. READY to start after Q3
launches.

## Cross-track items (both sessions involved)

- **T22 N=16384 Modern Hopfield:** experiment-session shipped CPU-only v8 (T3 in
  T-batch). If T3 still fails, testbed should investigate hardware-upgrade path.
  Note: testbed-side N=16384 envelope bench (b29dfhv12 bench 3) is the parallel
  test of this question and is still running on remote at filing time.
- **T14 mixed-confidence Path D:** experiment-session designed mechanism (T1 in
  T-batch). When T1 returns HARD_PASS, testbed integrates into Pattern B for
  regulated-industry validation.
- **T15 Path D edit isolation:** experiment-session tests with synthetic edit
  threads (T2). When T2 returns HARD_PASS, testbed validates with real concurrent
  LLM-orchestrated edits in Pattern B context.

## Experiment-session queue status (as of dispatch)

- **S-batch (14 anchors):** 1 running (S2 latency_crossover_analysis), 12 pending.
  Will deliver per-hop bottlenecks, latency surfaces, memory profile, operation
  atlas, tradeoff Pareto, edit isolation (S6 generic), confidence (S9 generic),
  approximate-sampling, GPU-baseline-multi-hop, adversarial (S12), novel-query
  (S13), joint-execution, plus N=16384 v7-resilient (S4).
- **T-batch (5 anchors):** T1 running, T2-T5 pending. Path-D-focused + Path B/E
  characterization + N=16384 CPU-only.

## Reconciliation with prior testbed queue

The 2026-05-30 prior queue (`testbed/TESTBED_TRACK_QUEUE_2026-05-30.md`) had 14
items framed around Path B as the primary multi-hop mechanism. This v2 reframes
the multi-hop items around Path D per v288 cap_map. Status of prior items:

| Prior | New      | Status                                                                |
|-------|----------|-----------------------------------------------------------------------|
| Q1    | T17/T14  | EC2 Pattern B integration reframed as T17 hybrid + T14 mixed-conf    |
| Q2    | shipped  | Hashed codebook (E6.1) — still shipped                                |
| Q3    | parallel | E2.3 composition latency — STILL READY; user authorized start         |
| Q4    | parallel | E2.4 cold/warm timing — STILL READY                                   |
| Q5    | T19      | Multi-hop benchmark suite folded into T19 comprehensive comparison    |
| Q6    | T19      | Vector DB comparison absorbed by T19 (with Path D primary mechanism)  |
| Q7    | T17/T19  | Substrate vs LLM-only MH split across T17 + T19                       |
| Q8    | T17      | LLM-guided orchestration absorbed by T17 (Path D is the mechanism)    |
| Q9    | T18      | Sustained MH workload reframed around Path D as T18                   |
| Q10   | T21      | Multi-tenant K=50 — same item, renumbered. READY                      |
| Q11   | parallel | Failure recovery testing — STILL READY                                |
| Q12   | T13      | Multi-hop caching reframed as T13 Path D path-prior cache             |
| Q13   | T17      | Multi-hop hybrid is now T17                                           |
| Q14   | T14      | Mixed-confidence MH is now T14 (Path D mechanism)                     |

## Ready partition (can start now or imminently)

1. **Q3 (E2.3 composition latency)** — pre-authorized. Will start when N=16384
   envelope bench completes.
2. **Q4 (E2.4 cold/warm timing)** — READY; small scope.
3. **Q11 (failure recovery)** — READY; 2-3wk.
4. **T21 (multi-tenant K=50)** — READY; extends existing `sharded_substrate.py`.

All Tier 3-5 Path-D-specific items wait for **S2 verdict** (experiment-session)
OR Path D mechanism primitives in `testbed/` code.

## Recommended cadence

1. Hold for N=16384 envelope bench completion (in flight).
2. Launch Q3 (composition latency) per user authorization. Multi-day sustained
   run; results available 24-72h.
3. While Q3 runs: start Q4 (cold/warm timing) — small scope, completes in days.
4. While Q3 + Q4 run: monitor experiment-session S2 verdict.
5. On S2 verdict landing: receive S2 latency-crossover output, plan T10
   (posterior max optimization) with bottleneck cell guidance.
6. After T10 ships: T11/T12/T13 unblock; can start in parallel.

## End of v2 queue. Filed 2026-05-30.
