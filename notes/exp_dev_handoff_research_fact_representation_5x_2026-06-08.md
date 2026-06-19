# exp_dev hand-off -- research: fact representation rethink 5x

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_fact_representation_rethink_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

A 5-level architectural drill on fact representation concludes that Pattern B triples
are a correct but sub-optimal primitive. Three extensions compose cleanly with all
validated algebraic primitives without breaking them:

1. Episode-arity binding (k>2 participants as one binding).
2. Temporal validity native (time-window as a fourth bind() argument).
3. Continuous binding strength (float32 instead of bipolar sign output).

All three require empirical pre-tests before engineering authorization per
[[feedback-drill-pretest-required]]. The cheapest pre-test (EP1 below) is 30 min CPU.

The drill also identifies that multi-resolution consolidation (two-tier episode + semantic
store with sleep migration) is the direct biological analog of the planned sleep-defrag
Mechanism B+C extensions.

Additionally: continuous binding strength has a privacy surface (float32 strength leaks
more ZKL signal than bipolar). This must be flagged to the ZKL privacy thread before
Layer B ships.

---

## Anchor Candidates (rank-ordered by P_deflated x value x engineering cost)

### 1. EP1 -- Episode-arity binding capacity pre-test (HIGHEST PRIORITY)

Anchor pointer: FACT-EP1 (new; not yet queued)
Substrate-product reading: Determines whether k-ary episode binding (k>2 participants
  in one hypervector) outperforms k-1 sequential triples for N-ary event retrieval.
  If yes (>10pp gap in precision@1 at 50% noise), episode_bind() is authorized as a
  v2.0 primitive. If no, triple decomposition is sufficient and episode-arity is closed.
Tier hint: CPU laptop; ~30 min wall; N=4096, k in {2, 3, 5, 8}, 50% bit-flip noise.
Why-now: Gate for the biggest structural gap in current fact representation. Cheapest
  pre-test in the batch. Runs first and independently.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: episode-bind precision@1 >= 0.85 at k=4, N=4096, 50% noise AND
             triple-chain precision@1 <= 0.70 under same conditions.
  HARD-FAIL: episode-bind precision@1 < 0.55 (chance floor) at k=4, N=4096.
  MID-BAND: episode precision@1 in [0.70, 0.84] -- better but not decisive; hybrid
            approach warranted (episode-bind for known high-arity types only).

Inputs required: existing bind() and inner_product() primitives from hdlab/. No new
  embeddings or models needed. Pure arithmetic test.

### 2. EP2 -- k-ary SNR formula derivation pre-test (PAIRS WITH EP1)

Anchor pointer: FACT-EP2 (new; not yet queued)
Substrate-product reading: Validates the k-ary extension of the capacity formula
  SNR = sqrt(N/(VE*deg)) for k=2. For k>2, the interference term may grow as
  O(k * VE * deg). If this growth is validated empirically, the capacity ceiling for
  episode stores is well-characterized and engineering can size N accordingly.
Tier hint: CPU laptop; ~45 min wall; sweep k in {2,3,5,8,10}, VE in {1, 4, 8},
  N in {1024, 4096, 16384}.
Why-now: Architectural sizing question -- if k-ary SNR degrades too fast, episode-arity
  is only useful for small k (2-4 participants), not large events (8-10 participants).

Pre-reg bands:
  HARD-PASS: measured SNR follows sqrt(N / (k * VE * deg)) to within 20% relative error
             across all k in {2,3,5,8}, establishing k-linear interference growth.
  HARD-FAIL: SNR degrades as O(N / (k^2 * VE * deg)) (superlinear interference growth),
             implying episode-arity is only practical for k <= 3.
  MID-BAND: SNR between the two regimes; k-dependent empirical correction factor needed.

Note: this is a pure empirical measurement, no theory required. Generate random role
and value hypervectors; compute retrieval SNR directly.

### 3. EP3 -- Temporal validity bind() extension pre-test

Anchor pointer: FACT-EP3 (new; not yet queued)
Substrate-product reading: Validates that adding a time-window vector as a 4th argument
  to bind() does not degrade retrieval precision for temporally-queried facts vs
  baseline (no time dimension). Specifically: does time-conditioned retrieval achieve
  precision@1 >= baseline - 0.05 at N=4096?
Tier hint: CPU laptop; ~20-30 min wall.
Why-now: Substrate already has validated bitemporal operations at 0.003ms (production
  scale). This pre-test checks the algebraic extension specifically -- whether time
  vectors encoded as positional hypervectors interfere with content retrieval.

Pre-reg bands:
  HARD-PASS: time-conditioned precision@1 >= 0.90 * baseline precision@1 (less than
             10% relative degradation from adding time dimension).
  HARD-FAIL: time-conditioned precision@1 < 0.70 * baseline (>30% relative degradation).
  MID-BAND: 10-30% relative degradation; time encoding scheme needs optimization.

Inputs required: existing bind(), positional hypervector generation, inner_product().
  Time-window vectors can be generated as bind(start_pos_vec, end_pos_vec).

### 4. EP4 -- Continuous binding strength (float32) retrieval quality check

Anchor pointer: FACT-EP4 (new; not yet queued)
Substrate-product reading: Validates that weighted superposition (sum of
  strength_i * fact_vec_i instead of sign-thresholded bipolar) retrieves facts
  correctly when strengths are heterogeneous (range [0.1, 1.0]) vs homogeneous (all 1.0).
  Key question: does the SNR formula need a correction term for heterogeneous strengths?
Tier hint: CPU laptop; ~30-45 min wall; sweep M (facts) in {10, 50, 100}, strength
  distributions in {uniform, exponential decay, power law}.
Why-now: Continuous strength is the foundation for soft deletion and temporal decay.
  Privacy analysis (ZKL surface) must happen AFTER this pre-test; do not route to
  ZKL thread until EP4 result is in hand.

Pre-reg bands:
  HARD-PASS: precision@1 >= 0.85 under exponential strength decay (newest fact = 1.0,
             oldest = 0.1) at M=50 facts, N=4096. Retrieval correctly ranks strongest
             facts highest.
  HARD-FAIL: precision@1 < 0.60 under heterogeneous strengths (strength distribution
             causes retrieval to return weak/old facts preferentially).
  MID-BAND: precision@1 in [0.60, 0.85]; normalization strategy for heterogeneous
             strengths needs tuning.

Caveat: flag EP4 result + float32 encoding details to ZKL privacy research thread
  before Layer B ships to production.

---

## Sequencing

EP1 and EP3 are independent; run in parallel.
EP2 depends on EP1 HARD-PASS or MID-BAND (only relevant if episode-arity proceeds).
EP4 is independent of EP1-EP3.

Recommended queue order:
  Round 1 (parallel): EP1 + EP3 + EP4 (all ~20-45 min CPU; no cloud needed)
  Round 2 (if EP1 passes): EP2 (45 min CPU; confirms k-ary capacity formula)

Total estimated cost: ~2-3 hours CPU, $0.

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_fact_representation_rethink_5x_2026-06-08.md
  Contains: Level 1-5 full analysis; design space 15 paradigms; engineering roadmap;
  35 verified citations; engineering-tractable ranking table.

Related prior notes:
  d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
    (production-scale validation context; 12+ algebraic primitives confirmed)
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_zkl_alternatives_crazy_ideas_2026-06-07.md
    (ZKL privacy thread; relevant to EP4 privacy caveat)

Validated primitives that must NOT be broken:
  PP-106 to PP-118 (algebraic primitives); PP-99 (multi-hop); PP-115 (one-shot transfer);
  PP-119 (native K-hop); bidirectional KG; nested d=16; bitemporal 0.003ms; GDPR 0.0004ms.

---

## Contract section

exp_dev owns: anchor design, sweep grids, pre-reg band adjustment, queue assignment,
  and dispatch timing. Research provides the theoretical case and priority ordering only.

exp_dev should NOT dispatch cloud for EP1-EP4. All four are CPU-only pre-tests.
  If any pre-test fails HARD, do not escalate to cloud without orchestrator approval.

If EP1 HARD-PASS: route engineering authorization for episode_bind() to orchestrator
  via a one-line status update. Orchestrator decides v2.0 timeline.

If EP4 passes AND ZKL privacy analysis is not yet done: hold Layer B (continuous
  binding strength) from production dispatch until ZKL analysis completes.

---

## Autonomy declaration

exp_dev has full autonomy to:
  - Design and queue EP1-EP4 anchors in any order (respecting sequencing above)
  - Adjust pre-reg band thresholds based on substrate-specific engineering knowledge
  - Add additional smoke checkpoints if intermediate results are ambiguous
  - Run all four in parallel on the local CPU runner

exp_dev does NOT have autonomy to:
  - Authorize v2.0 engineering (orchestrator gate)
  - Route Layer B to production before ZKL privacy analysis
  - Modify validated primitives PP-106 to PP-119
  - Dispatch cloud instances for these CPU-only pre-tests
