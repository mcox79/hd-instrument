# Pre-registration: edge_importance_bound_pair_consolidation_v1

**Date:** 2026-06-26
**Anchor:** edge_importance_bound_pair_consolidation_v1
**Script:** experiments/exp_edge_importance_bound_pair_consolidation_v1.py
**Queue:** remote_cpu_queue (numpy; ~3-5 CPU-hr estimate per Research handoff ANCHOR 5)
**Seeds:** [7, 17, 23] (3 mandatory minimum; matches cortex_E_tensor_RETEST_fairness_v2 cohort)
**Primitive:** hdlab/edge_importance.py (NEW; sparse H[i,j] + derive_E_rowsum + derive_E_pagerank)

## Promotion context (Wave 2 ANCHOR 5; per Research 2x revival drill)

Reference handoff: `notes/exp_dev_handoff_research_cortex_E_tensor_alternatives_2x_revival_2026-06-26.md` ANCHOR 5.
Research note: `notes/research_cortex_E_tensor_wrong_direction_2x_revival_drill_2026-06-26.md` Section ANCHOR 5.

**Prior failure mode (TRIPLE-CONFIRMED):**
- Wave 1 cortex_E_tensor_HARDER_REGIME_v1: gap_E_vs_RND = -0.217 (wrong direction)
- Wave 1.6 cortex_E_tensor_RETEST_fairness_v2: cor(E,|W|) = 0.984 (per-atom scalar inherits magnitude)
- Diagnosis: ANY retrieval-history-driven per-atom-scalar importance inherits magnitude
  correlation because retrieval-hit IS magnitude-driven on argmax cleanup.

**Structural pivot (ANCHOR 5):** importance lives on per-EDGE space H[i,j] over bound-pair
structure. Atom-level importance is DERIVED via row-sum (or PageRank) of the edge graph.
Edges have a DIFFERENT observability axis than per-atom magnitude.

## v1 design

### Substrate setup
- N = 1024 (bipolar HRR; no _n suffix in anchor; capability-test cell)
- M_OLD = 600, M_RECENT = 400 (alpha = 0.977, above Hopfield-critical 0.138)
- Composite-query workload: J_comp = 3000 cycles, arity = 3 (bundles of 3 atoms)
- USE_FRAC = 0.40 -> N_USE = 240 atoms in RETRIEVED partition; remaining 360 in UNRETRIEVED
- Downscale scale = 0.20, E_thresh = 2.0 (atom importance), H_thresh = 3.0 (load-bearing edge)

### Composite-query workload (NEW; absent in prior cortex cells)
- Each cycle: draw 3 atoms uniformly from RETRIEVED pool
- Bundle their keys via bipolar sign-majority bundle (substrate-native HRR composition)
- Decode bundled query against W; increment H[i,j] for all unordered pairs in the triple
- Decay-step = 0.0 (no decay in v1; pure cumulative accumulation)

### Arms (3 mandatory)
- **ARM_BASELINE_NO_DOWNSCALE**: rail; no pruning. Sanity baseline.
- **ARM_EDGE_GATED_DOWNSCALE**: prune atoms with E_derived < E_thresh AND max_edge < H_thresh.
- **ARM_RANDOM_GATED**: control; prune random subset of same size (tests SELECTIVITY vs CAPACITY).

## Pre-registered bands (LOAD-BEARING; LOCKED at smoke clearance)

### LOAD-BEARING USER FAIRNESS CHECK
- `cor(E_derived_rowsum, |W @ key|) < 0.30` -- USER pre-reg gate (carried forward from Wave 1.6).
- If `cor >= 0.30`: HARD_FAIL. Edge-derived importance has inherited magnitude correlation;
  mechanism class structurally indistinguishable from per-atom-scalar failure mode. ROUTE BACK
  TO RESEARCH for next structural pivot (ANCHOR 6 distribution-homeostasis is the next-line).

### HARD_PASS (chain-grade candidate; pending Skunkworks landed-VET)
- cor(E_derived, |W|) < 0.30 [structural orthogonality]
- recall_old_RETRIEVED >= 0.85 [user spec: rec_old preservation > 0.85 on RETRIEVED subset]
- recall_recent >= 0.85 [user spec: rec_recent > 0.85]
- delta_E_vs_RND on RETRIEVED >= 0.05 [selectivity matters vs random pruning]
- cv (across seeds) on recall_old_RETRIEVED <= 0.10

### MIDDLE_BAND
- cor < 0.50 (mechanism structurally distinct) AND recall_old_RETRIEVED >= 0.65
- But full HARD_PASS band not cleared (e.g., delta_E_vs_RND between 0.02 and 0.05)

### HARD_FAIL
- cor(E_derived, |W|) >= 0.30 (FAIRNESS GATE)
- OR H_n_edges < 50 (mechanism didn't fire; composite-query workload too sparse)
- OR recall_old_RETRIEVED < 0.65 (collapse destroyed retrieval)
- OR substrate-only-decode gate violated (n_llm_calls > 0)

## Smoke gate (clean synthetic data per [[feedback-smoke-clean-synthetic-data-not-substrate-state]])

Smoke config: N=256, M_OLD=200, M_RECENT=150 (matches HARDER_REGIME smoke for comparability),
J_comp=1000, arity=3, 1 seed [7].

**Smoke result (2026-06-26 18:00 PT):**
```
cor(E_derived, |W|) = -0.043   PASS (< 0.30 fairness gate)
EDGE_GATED rec_RETR = 1.000
RANDOM rec_RETR    = 0.700
NO_DOWNSCALE rec_RETR = 1.000
d_E_vs_RND = +0.300   (selectivity FIRES)
H_n_edges = 1916 from 1000 composite queries (mechanism populates H)
VERDICT: MIDDLE_BAND (recall_recent=0.640 below 0.85; smoke alpha=1.367 above critical)
```

Smoke CLEARS fairness gate, selectivity gate, mechanism-fires gate. recall_recent below 0.85
at smoke is REGIME-EFFECT (alpha=1.367 above Hopfield critical 0.138 by 10x); FULL runs at
alpha=0.977 which is closer to manageable regime.

## Substrate-only decode gate
- `n_llm_calls == 0` by structural guarantee (no LLM imports anywhere).
- Decode = `sign(W @ key)` cosine cleanup against value matrix.

## Per-seed runtime estimate (REQUIRED per Fix #17)
- Smoke wall-clock (N=256, M=350, J=1000, 1 seed): 0.2s
- FULL: N=1024 (4x N), M=1000 (~3x M), J=3000 (3x J), 3 seeds.
  - scaling_exp 1.5 for matmul-heavy: time ~ 0.2 * (4^1.5) * (3) * 3 = 0.2 * 8 * 9 = 14.4s estimate.
  - Conservative buffer 100x for composite-query loop overhead: ~25 min wall-clock per seed.
- Total estimate: ~1.5 hr wall (3 seeds, sequential).
- Timeout: 7200s (2hr) -- conservative buffer.

## Citations (per Research handoff)
- Govindarajan-Israely-Huang-Tonegawa (2011) clustered synaptic plasticity (brain)
- Brin-Page (1998) PageRank (math)
- Seidman (1983) k-core decomposition (network science)
- Stauffer-Aharony percolation theory (materials)

## Cross-cycle composition
- Composes with ANCHOR 2 (ultrametric_clustering) -- ultrametric finds atom clusters;
  edge-importance finds atom-pair bonds. Could compose: cluster by ultrametric, weight
  clusters by their internal edge-importance.
- Aligns with USER pivot toward "compositional understanding first" -- the act of building
  a substrate-native composite-query pipeline advances strategic direction.

## Discipline checklist
- Pre-flight Fix #26 predispatch_check.py: PASS (0 matching landings)
- ARM_BASELINE rail: YES
- ARM_RANDOM control: YES (selectivity vs random gating)
- Multi-seed FULL >= 3: YES (seeds [7, 17, 23])
- ASCII-only: YES (no emojis / em-dashes / unicode in code)
- Substrate-only decode gate: YES (audit-logged)
- META_M7 reproduce-once rail: relies on per-seed runtime + cv <= 0.10 fence

-- exp_dev (Opus 4.7 1M), 2026-06-26
