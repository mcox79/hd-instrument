# Strategy → Experiment Dev: Cluster census Phase 1 — FINAL substrate-physics gate

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~21:30 EDT
**Topic**: Cheapest decisive test for cluster-trapping mechanism (4th-attempt FINAL)
**cap_map state**: v133 (commit pending)
**Trigger**: Research 4th-attempt FINAL delivered SPURIOUS-ATTRACTOR CLUSTER TRAPPING framework P=[0.45, 0.60]; cluster census is single-experiment decisive falsification gate

## Context

Research 4th-attempt FINAL delivered cluster-trapping framework with FIRST
cross-N quantitative match across 4 attempts:
- N=4096 K=100: cluster ~1.4 → plateau 0.71 ≈ empirical 0.767 ✓
- N=65536 K=100: cluster ~5.0 → plateau 0.20 ≈ empirical 0.217 ✓
- Cluster size ∝ N^0.73

7-constraint score 6.5/7 (best across 4 attempts; cycle 131 HMM was 6/7
then refuted at C3). Honest P=[0.45, 0.60] calibration-deflated.

Cluster census is the single-experiment decisive test. ~5-15 GPU-min.

## Experiment 1 — Cluster census at N=65536 K=100 (HIGHEST PRIORITY)

**`wave14_cluster_census_N65536_v1`** (~5-15 GPU-min):

```python
def cluster_census(W, codebook, true_codeword, depth=25, n_trials=500,
                   noise_level=0.05):
    """
    Run n_trials forward chains starting from same true codeword;
    record final argmax output; check if outputs concentrate on small
    set of codewords (cluster trap).
    """
    K, N = codebook.shape
    final_outputs = []
    for trial in range(n_trials):
        q = true_codeword + np.random.randn(N) * noise_level
        for hop in range(depth):
            scores = codebook @ q
            winner = int(np.argmax(scores))
            q = np.sign(W @ codebook[winner])
        final_outputs.append(winner)

    from collections import Counter
    counts = Counter(final_outputs)
    unique = len(counts)
    top5_share = sum(sorted(counts.values(), reverse=True)[:5]) / n_trials
    return dict(unique_codewords_hit=unique, top5_share=top5_share)
```

**Verdict criteria**:
- **CLUSTER_TRAPPING_CONFIRMED**: unique_codewords < 10 AND top5_share > 0.9
  (chains concentrate on ~5 codewords)
- **CLUSTER_TRAPPING_REFUTED**: unique_codewords > 50 OR top5_share < 0.5
  (chains spread randomly across codebook)
- **CLUSTER_TRAPPING_PARTIAL**: between thresholds (substrate has partial
  attractor structure)

**Predicted at N=65536 K=100**: cluster ~5; unique_codewords ~5-7; top5_share > 0.9.

## Experiment 2 — Cross-N cluster size scaling (validates N^γ claim)

**`wave14_cluster_census_N_sweep_v1`** (~15 GPU-min):

Run cluster census at N ∈ {4096, 16384, 65536} at K=100. Fit cluster_size ∝ N^γ.

**Predicted**: γ ≈ 0.73; cluster sizes 1.4 → 2.9 → 5.0.

**Verdict criteria**:
- CLUSTER_NSCALE_CONFIRMS: fit γ ∈ [0.5, 1.0]
- CLUSTER_NSCALE_REFUTES: γ < 0.3 (cluster flat with N) OR γ > 1.3 (super-linear)

## Experiment 3 — W^L effective rank check (cheap CPU-only)

**`wave14_W_L_effective_rank_v1`** (~5 min CPU):

Compute SVD of W^L for L ∈ {1, 5, 10, 20, 50} at N=65536. Measure effective
rank (eigenvalues above 1% of top eigenvalue).

**Predicted**: effective rank drops ≥2× from L=1 to L=50 (subspace collapse).

**Verdict criteria**:
- RANK_COLLAPSE_CONFIRMS: effective_rank(L=50) ≤ effective_rank(L=1) / 2
- RANK_COLLAPSE_REFUTES: effective rank flat or increases with L

## Priority ordering

1. **`wave14_cluster_census_N65536_v1`** (Experiment 1) — single decisive test
   for cluster-trapping at substrate operating point
2. **`wave14_W_L_effective_rank_v1`** (Experiment 3) — fastest; CPU only;
   validates Oseledets-collapse aspect
3. **`wave14_cluster_census_N_sweep_v1`** (Experiment 2) — N-scaling validation

Total: smoke + FULL = 6 runs; ~20-30 GPU-min + 5 min CPU.

## Substrate-product implication

**If CLUSTER_TRAPPING_CONFIRMED**:
- Substrate-physics characterization gains theoretical anchor for FIRST TIME
  across 4 attempts
- Substrate-product narrative: "substrate exhibits structured spurious-attractor
  clustering at scale; VAMP-on-chain is the exact-recovery decoder via
  endpoint-anchored global resolution"
- Lane D Demo 1 narrative strengthens

**If CLUSTER_TRAPPING_REFUTED**:
- 5th candidate mechanism refuted (cluster-trapping out)
- Substrate-physics characterization stands at "forward-lossy + reverse-invertible
  (SMOOTHER_ONLY_WORKS) but specific mechanism unknown"
- Substrate is in genuinely unprecedented regime per [[feedback-lit-scan-calibration-penalty]]
- Substrate-product Demo 1 capstone STILL HOLDS via VAMP-on-chain regardless

**Substrate-physics characterization gain INDEPENDENT of cluster census outcome**:
- SMOOTHER_ONLY_WORKS at FULL (cycle 134) ALREADY established substrate's chain
  composition is forward-lossy + reverse-invertible
- Cluster trapping is the CANDIDATE EXPLANATION; substrate-physics finding
  (reverse-invertibility) holds regardless

## What I need from you

1. Queue 3 experiments per priority ordering
2. Flag infrastructure issues — cluster census needs forward chain code (likely
   reuses cycle 121 multi-hop infrastructure); SVD-based effective rank check
   is CPU-only at N=65536 (~5 min)
3. Estimate timeline given pipeline state (queue=0, current=None)

## Per [[feedback-no-papers-product-only]]

All 3 experiments substrate-product oriented (substrate-physics characterization
feeds substrate-product narrative). Cluster census is FINAL substrate-physics
gate per user signal "research is free - maybe this is the final run".

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 30-60 min per recent patterns.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
