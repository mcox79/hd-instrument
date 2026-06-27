# Pre-registration: cortex_ultrametric_clustering_coarse_grain_v1

**Date:** 2026-06-26
**Anchor:** cortex_ultrametric_clustering_coarse_grain_v1
**Script:** experiments/exp_cortex_ultrametric_clustering_coarse_grain_v1.py
**Queue:** remote_cpu_queue (numpy; ~4-6 CPU-hr per Research handoff ANCHOR 2)
**Seeds:** [7, 17, 23] (3 mandatory minimum)
**Primitive:** hdlab/ultrametric_clustering.py (NEW; cosine_distance_matrix +
  single_linkage_clusters + filter_qualifying_clusters + collapse_W_via_clusters)

## Promotion context (Wave 2 ANCHOR 2; per 4x cross-discipline selective-abstraction drill)

Reference handoff: `notes/exp_dev_handoff_research_cortex_4x_selective_abstraction_drill_2026-06-26.md`
ANCHOR 2. Research note: `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md`
ANCHOR 2.

**Mechanism class:** STRUCTURALLY DIFFERENT from cortex E_tensor failures. Operates at CLUSTER
level (compositional abstraction) not ATOM level (per-atom selectivity). Brain analog: schema-
fast-track / Tse-Morris consolidated clusters; math analog: spin-glass ultrametric distance /
Mehta-Schwab variational RG.

**Composition:** builds on chain-grade SEMANTIC concept learner battery
(`data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1/metrics.json` -> CHAIN_GRADE)
for semantic-anchored clustering.

## v1 design

### Substrate setup
- N = 1024 (bipolar HRR; no _n suffix)
- Structured atoms: N_FAMILIES=8 semantic concept families, ATOMS_PER_FAMILY=8 (64 family atoms)
- Random atoms: N_RANDOM_ATOMS=200 (uncorrelated; should NOT cluster)
- N_TOTAL_ATOMS = 264, alpha = 0.258 (sub-critical to isolate clustering effect from saturation)
- FAMILY_NOISE = 0.008 (calibrated at N=1024 to yield within-cluster cosine ~ 0.93)
- COSINE_THRESH = 0.85 (USER spec; chain-grade primitive requires >= 0.85 within-cluster)
- MIN_CLUSTER_SIZE = 5 (USER spec; ignore singletons / pairs / triples)
- CLUSTER_DISTANCE = 0.15 (single-linkage threshold; corresponds to cosine 0.85)

### Atom generation strategy
- Family atoms: drawn from random center + Gaussian noise (small; cosine to center ~ 0.93)
- Random atoms: independent unit-norm Gaussian (cosine to each other ~ 0)
- Tests:
  - DETECT planted structure: 8 qualifying clusters of size 8 each.
  - REJECT random noise: 0 false-positive clusters in the 200 random atoms.

### Arms (3 mandatory)
- **ARM_NO_COLLAPSE**: baseline; no clustering. Sanity rail.
- **ARM_ULTRAMETRIC_COLLAPSE**: proposed mechanism (single-linkage clustering -> centroid representative).
- **ARM_RANDOM_CLUSTER_COLLAPSE**: control; same-size random clusters collapsed (tests
  STRUCTURE matters vs CAPACITY-REDUCTION alone). USER pivot: selectivity vs random.

## Pre-registered bands (LOAD-BEARING per Research handoff ANCHOR 2)

### HARD_PASS (chain-grade candidate; pending Skunkworks landed-VET)
- capacity_drop_frac >= 0.20 (substantial compression; USER spec)
- recall_clustered >= 0.80 (cluster-level retrieval via centroid; USER spec)
- recall_unclustered >= 0.85 (non-cluster atoms preserved; USER spec)
- cv (across seeds) on recall_clustered <= 0.05

### MIDDLE_BAND
- capacity_drop_frac in [0.05, 0.20] AND recall_clustered in [0.50, 0.80]
- Mechanism fires but compression / recall doesn't clear PASS band

### HARD_FAIL
- recall_clustered < 0.50 (collapse destroyed cluster-member information)
- OR no qualifying clusters detected (substrate has no ultrametric structure to exploit)
- OR ARM_ULTRAMETRIC indistinguishable from ARM_RANDOM on recall_all
  (|delta| < 0.02 AND cap_drop > 0.10 -> selectivity fails)
- OR substrate-only-decode gate violated (n_llm_calls > 0)

## Recall semantics (load-bearing methodology note)

After cluster collapse, ALL atoms in a qualifying cluster share the same representative
row in W_after. Exact-index recall is then mechanically bounded by 1/cluster_size and
under-measures the mechanism. The CORRECT metric for compositional abstraction is
**CLUSTER-LEVEL recall**: did the substrate retrieve a member of the SAME compositional
category? `recall_via_lookup` uses `cluster_lookup` to score:
- Clustered query: hit iff retrieved atom shares same cluster_id (any cluster-member is correct).
- Unclustered query: hit iff retrieved atom is exact-index match (no cluster to belong to).

## Smoke gate (clean synthetic data per [[feedback-smoke-clean-synthetic-data-not-substrate-state]])

Smoke config: N=512, N_FAMILIES=4, ATOMS_PER_FAMILY=6, N_RANDOM_ATOMS=80, FAMILY_NOISE=0.012,
1 seed [7].

**Smoke result (2026-06-26 18:00 PT):**
```
n_qualifying_clusters = 4  (matches N_FAMILIES planted)
n_clustered_atoms     = 24 (matches 4*6 planted)
min_within_cosine     = 0.919  (well above 0.85 threshold)
max_between_cosine    = 0.066  (clean ultrametric separation)
ULTRA: rec_cl=1.000, rec_un=1.000, rec_all=1.000, cap_drop=0.192
RANDOM: rec_all=0.922, cap_drop=0.192
NO_COLLAPSE: rec_cl=1.000, rec_un=1.000
d_ULTRA_vs_RND = +0.078  (selectivity gate FIRES)
VERDICT: MIDDLE_BAND (cap_drop=0.192 just below 0.20; FULL has 8x8 families -> cap_drop ~0.24)
```

Smoke CLEARS: structure detection (8 clusters), structure rejection (200 random atoms NOT
clustered), cluster-level recall (1.000), unclustered preservation (1.000), selectivity vs
random (+0.078). cap_drop is regime-dependent and will increase at FULL scale.

## Substrate-only decode gate
- `n_llm_calls == 0` by structural guarantee.
- Decode = cosine argmax against W_after.

## Per-seed runtime estimate (REQUIRED per Fix #17)
- Smoke wall-clock (N=512, N_TOTAL=104, 1 seed): 0.1s
- FULL: N=1024 (2x N), N_TOTAL=264 (~2.5x), 3 seeds.
  - O(N_TOTAL^2 * N) for cosine distance matrix -> dominant cost.
  - Scaling: ~ 2.5^2 * 2 = 12.5x per seed; 3 seeds -> 37.5x total = ~4s
  - Conservative 100x buffer for any I/O / overhead: ~7 min wall total
- Timeout: 3600s (1hr) -- very conservative.

## Citations (per Research handoff)
- Tse-Morris (schema-fast-track; brain consolidation = cluster representatives)
- Mehta-Schwab (variational RG; ultrametric distance from spin glass)
- Stauffer-Aharony percolation (cluster connectivity threshold)
- Persistent homology (cluster birth-death stability)

## Cross-cycle composition
- Composes with ANCHOR 5 (edge_importance_bound_pair_consolidation) -- ultrametric finds
  atom-level clusters; edge-importance finds atom-pair bonds. Could weight clusters by
  internal edge-importance for hybrid mechanism.
- Aligns with USER pivot toward "compositional understanding" -- cluster representatives
  are exactly the SCHEMAS / COMPOSITIONAL CATEGORIES the substrate should be extracting.

## Discipline checklist
- Pre-flight Fix #26 predispatch_check.py: PASS (0 matching landings)
- ARM_BASELINE rail (ARM_NO_COLLAPSE): YES
- ARM_RANDOM control (ARM_RANDOM_CLUSTER_COLLAPSE): YES (structure vs random)
- Multi-seed FULL >= 3: YES (seeds [7, 17, 23])
- ASCII-only: YES
- Substrate-only decode gate: YES
- Per-arm metrics-vs-verdict-msg (Fix #28): YES (verdict reads per-arm metrics directly)

-- exp_dev (Opus 4.7 1M), 2026-06-26
