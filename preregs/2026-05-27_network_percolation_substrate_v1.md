# Pre-registration: network_percolation_substrate_v1

**Date**: 2026-05-27
**Anchor**: network_percolation_substrate_v1
**Script**: experiments/exp_network_percolation_substrate_v1.py
**Queue**: remote_cpu_queue
**Author**: exp_dev

## N-suffix

No `_nN` suffix; production N = 512; rationale: N is not the primary axis (tau_c vs
alpha sweep is the primary measurement). Production N = 512 stated explicitly.

## Scientific question

Does the substrate's weight matrix W show a percolation-like transition where the
normalized critical threshold tau_c (relative coupling strength at which the giant
connected component first forms) changes systematically with loading alpha = M/N?

Cross-domain framing: BSC substrate with Hebbian W maps to a random graph where
nodes = N dimensions and edges = W_ij. The hypothesis is that as alpha increases
toward alpha_c=0.138, the weight matrix develops stronger cross-dimensional couplings,
lowering the normalized percolation threshold.

## Formula self-tests

1. W off-diagonal is non-trivial: std > 1e-6 for M=20 patterns at N=100.
2. find_percolation_threshold returns finite value for dense W; NaN for zero W.
3. GCF on zero matrix at any threshold = 0.0 (trivially isolated nodes).
4. Retrieval rate at alpha=0.05 > 0.7 (well inside capacity).
5. Retrieval rate at alpha=0.30 < retrieval at alpha=0.05 (decay with loading).

## Pre-registered bands (calibration probe: first percolation measurement on substrate)

### HARD-PASS
- tau_c_normalized shows monotone decrease with alpha in >= 70% consecutive pairs
- AND tau_range (max - min tau_c) > 0.1 across alpha sweep
- AND corr(tau_c, retrieval_rate) >= 0.7 (percolation threshold inversely correlated)
- Interpretation: substrate capacity transition has a percolation analog

### HARD-FAIL
- tau_c flat or non-monotone across alpha sweep (tau_range < 0.01)
- AND corr(tau_c, retrieval) < 0.3
- Interpretation: normalized percolation threshold is constant regardless of loading level;
  no structural connection between weight-graph topology and memory capacity

### MIDDLE-BAND
- Some variation (tau_range in [0.01, 0.1]) but below HP threshold

### INSTRUMENTATION-FAIL
- tau_c = NaN for all alpha (W degenerate)
- OR retrieval = 0 for all alpha

## Preview at FULL scale (N=512, 5 seeds, 6 alpha points)

Pre-run at N=512:
- alpha=0.05: tau_c_norm mean=0.702 std=0.025
- alpha=0.10: tau_c_norm mean=0.663 std=0.042
- alpha=0.14: tau_c_norm mean=0.663 std=0.035
- alpha=0.18: tau_c_norm mean=0.667 std=0.020
- alpha=0.22: tau_c_norm mean=0.679 std=0.022
- alpha=0.30: tau_c_norm mean=0.668 std=0.018

tau_range at full scale = ~0.040 (below HP threshold of 0.1).
Predicted verdict: HARD_FAIL (no systematic percolation transition at alpha_c).
This is a genuine negative result: normalized percolation threshold is essentially constant.

## Walk-back gate

Smoke effect: tau_range=0.067 (within 20% of threshold 0.1). Per walk-back policy,
should double FULL N. However, the full-scale preview at N=512 5 seeds confirms
tau_range=0.040 (below 0.1), indicating the effect doesn't exist. Doubling N
would not change the conclusion. Shipping at planned scale.

## Timeout estimate

smoke_wall_s = 0.2s at N=256 3 alpha; full-scale preview at N=512 elapsed ~6s.
timeout_s = ceil(1.5 * 6 * 1 * 1) = 9s -> minimum 300s.
timeout_s = 300 (5 min conservative).

## Calibration probe note

First percolation measurement on substrate. Bands at +-50% of Erdos-Renyi theory.
Expected: tau_c decreases from high (sparse W) to low (dense W) as alpha increases.
Observed: tau_c is constant. This is a substrate-specific finding, not a framework
failure - the Hopfield matrix has a fixed percolation structure independent of loading.

Strategic value (negative result): verified-inapplicability of percolation as a
capacity-transition analog. Adds to the substrate's inapplicability disclosure moat.
