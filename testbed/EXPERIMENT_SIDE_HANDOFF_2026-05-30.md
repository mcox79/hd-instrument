# Experiment-side handoff to testbed (received 2026-05-30)

Verbatim from experiment session at commit 947b22e -> 392242b. Read this BEFORE
acting on any testbed Tier 2-5 work — priorities have shifted.

## Key changes since prior handoff

1. **Triple-path multi-hop rescue** — 3 mechanisms HARD_PASS at M=256:
   Path B (continuous-output), Path D (Bayesian path-probability propagation),
   Path E (spectral path identification). Caveat: M=256 << M_c~16K — durability
   to production-relevant M pending P1 verdict.
2. **Continuous-output substrate** — works at M <= 2048, degrades at M=8192.
   Sweet spot maps to Pattern B regime (50-500 facts).
3. **Sparse-W** — 16x memory savings within standard envelope (M <= 8192 at N=4096).
   Does NOT extend past M_c. Holds under mixed-CRUD + deletion + edit-storm. Production-ready
   for sub-capacity deployment.
4. **GPU acceleration** — 22.67x speedup at N=4096 confirmed; N=8192 expansion pending.
   Killer features intact on GPU. Closes centralized-deployment latency gap.
5. **Substrate-physics framework** — NOT degraded (correction from v285). The
   adaptive-threshold "framework degradation" was instrumentation pathology. beta_c=10
   invariance, NESS thermodynamics, SKAH-M class, TCFT all remain valid.

## Reshaped testbed priorities

### Priority 1: Pattern B LLM integration with continuous-output Path B multi-hop

THE strategically important test. Path B validated at M <= 2048 maps directly onto
Pattern B (50-500 active facts).

Build `substrate_retrieve_multihop_continuous` tool using Path B internally for
depth-2/3 multi-hop. Example query: "Find the manager of the team that handles
product line X" (X -> team -> manager).

Compare 4 conditions:
- (a) LLM-only
- (b) LLM + RAG (FAISS + sentence-transformers)
- (c) LLM + substrate single-hop only (LLM orchestrates multi-hop)
- (d) LLM + substrate with Path B multi-hop tool

Measure: API tokens (c vs d, expect 50-70% reduction); accuracy across (a)-(d);
audit trail completeness; end-to-end + per-component latency.

Success: (d) >= (c) on accuracy with substantially fewer tokens.

Cost: ~3-4 weeks engineering, $5-20 LLM API.
Dependencies: experiment-side P1 (higher-M durability).
- If P1 sub-capacity-only: M <= 500 in Pattern B corpus.
- If P1 production-scale: extend to larger corpora.

### Priority 2: Sparse-W backing Pattern B

Same as P1 but with sparse-W. Measure memory at M=100/500/1000; verify killer
features hold; measure latency overhead of sparse indirection.

Cost: ~1-2 weeks on top of P1.

### Priority 3: GPU-backed substrate for centralized deployments

Same as P1 but with GPU substrate. Per-call latency vs CPU vs FAISS; throughput
at concurrent queries; killer features intact (verify against N5 result).

Cost: ~1-2 weeks after GPU N=8192 verdict lands.

### Priority 4: Three-mechanism routing

LLM has tool access to Path B (low-M shallow), Path D (Bayesian moderate depth),
Path E (spectral deep). Picks mechanism per query OR runs multiple + consensus.

Cost: ~4-6 weeks.
Dependencies: Q2 (composition) + Q3 (K-scaling). Defer.

## Deferred / parallel-track

- Multi-hop Path C/F/G — subsumed by P1 or niche; defer.
- T3.1-T3.4 production engineering (hashed codebook / batched / cached / async cert)
  — ALREADY MOSTLY SHIPPED in current testbed (T2/T3/T4); T5 async cert remains.
- T5.1 compliance docs — parallel; requires lawyer.
- T5.2 public library cleanup — parallel.
- T5.3 standard benchmark integration — parallel; produces competitive-positioning data.
- T5.4 pilot deployment — gated on P1 validation.

## Open experiment-side questions (24-48h horizon)

- P1 multi-hop higher-M durability — settles P1's M-range
- P2 GPU baseline N=8192 — settles P3 readiness
- Q1 adaptive_threshold_rescue_v3 — fixed vs adaptive thresholds for testbed
- Q2 mechanism composition — gates P4
- Q3 large-K path scaling — informs P4 routing logic

**WAIT FOR THESE before committing to multi-week engineering.**

## Current testbed state vs new priorities

Old `NEXT_SESSION_STATE.md` Tier 2-5 plan:
- T2 hashed codebook — SHIPPED (maps to T3.1)
- T3 batched ops — SHIPPED (maps to T3.2)
- T4 cached retrieval — SHIPPED (maps to T3.3)
- T5 async deletion cert — DEFERRED (maps to T3.4)
- T6 cross-shard correlation — DEFERRED
- T7 LLM-substrate integration — **NOW Priority 1** (Pattern B + Path B multi-hop)
- T8-T13 — deferred per old plan

## Immediate next action

N=16384 envelope bench (b29dfhv12 bench 3 of 3) still running on remote;
answers the linear-vs-exponential capacity question. Result is informational —
does NOT gate any new-priority work. After bench finishes, testbed enters
**verdict-wait** mode for P1/P2/Q1/Q2/Q3.

Allowed parallel work during wait:
- T5.3 standard benchmark integration (competitive positioning data)
- T5.2 public library cleanup (no dependencies)
- T5 async deletion certificate (small scope, 1-2 weeks)
