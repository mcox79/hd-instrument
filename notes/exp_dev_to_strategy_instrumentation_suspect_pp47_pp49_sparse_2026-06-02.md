# exp_dev -> Strategy: INSTRUMENTATION_SUSPECT pp47_pp49_sparse_placefrac

**Date:** 2026-06-02
**Anchor blocked:** pp47_pp49_counterfactual_abduction_v2_sparse_placefrac_n4096_v1
**Reason:** SUSPICIOUS_RESULT_GATE -- all metrics constant (all 0.7998), all retrievals converge to boundary patterns (xi_48, xi_49 at K=50) regardless of query.

## What was observed

Smoke run at N=1024, K=20 AND debug at N=4096, K=50 both show:
- ALL query positions (k=10, 15, 20, 25, 30 at K=50) converge to boundary patterns xi_48, xi_49.
- baseline_cos = 0.7998 identically for ALL positions, ALL seeds.
- cf_cos = 0.7998 identically for ALL positions, ALL seeds.
- consistency_cos = 0.7998 identically for ALL positions, ALL seeds.

All 3 metrics are identical constant across all conditions: SUSPICIOUS_RESULT_GATE triggered.
The experiment is NOT measuring counterfactual abduction -- it's measuring cos(any_probe, xi_K-1).

## Root cause

At PLACE_FRAC=0.10, sigma=2.0, the boundary patterns (xi_K-1, xi_K-2) are DOMINANT ATTRACTORS:
- Interior patterns have symmetric neighbor fields that partially cancel (left + right crosstalk).
- Boundary patterns (xi_{K-1}, xi_{K-2}) have ONLY left neighbors -- their self-field
  is relatively LARGER than their total crosstalk.
- Result: the Hopfield W attracts ALL starting points to the boundary cluster.
- This is independent of K (same at K=20 and K=50).

The research spec's closed-form prediction `cos ~ 1/sqrt(1+sum_overlap_sq)` IGNORED
the boundary asymmetry. The prediction was for INTERIOR patterns only; boundary patterns
break the symmetry assumption.

## Why K-bump hypothesis was right to be falsified but the fix was incomplete

The K-bump hypothesis was correctly refuted by the 0-compute drill (K-invariance of
sum_overlap_sq for interior patterns is correct). But the fix (PLACE_FRAC=0.10) only
reduces the LOCAL crosstalk magnitude -- it does NOT fix the GLOBAL boundary dominance.
With PLACE_FRAC=0.10, each interior pattern has weaker crosstalk BUT boundary patterns
ALSO have weaker interaction with their left neighbors, making them relatively EVEN MORE
dominant as attractors (lower total crosstalk BUT still asymmetric).

## Recommended R4 fix

**R4-A (RECOMMENDED): Circular topology (periodic boundary conditions)**

Anchor name: `pp47_pp49_counterfactual_abduction_v3_sparse_circular_n4096_v1`

Changes:
1. preferred_locs uses circular K-space: `preferred_locs = rng.uniform(0, K, size=N)` -- UNCHANGED.
2. Place-field distance: `d = ((preferred_locs - k) + K/2) % K - K/2` (circular distance).
3. Shift operation: `xi_cf = Xi[(k + SHIFT_STEPS) % K]` (wrap around).
4. Keep PLACE_FRAC=0.10, SIGMA=2.0, K=50, N=4096.

Effect: All K patterns are symmetric (every pattern has identical left/right neighbor count).
Eliminates boundary-attractor dominance. Predicts baseline_cos ~ 0.83 (HP boundary) for PLACE_FRAC=0.10.

P_deflated for R4-A: 0.65 (circular topology eliminates root cause; sparse-code lit strong;
novel-composition penalty 0.15 applies).

**R4-B (BACKUP): Increase N to 8192 + circular topology**

Anchor: `pp47_pp49_counterfactual_abduction_v3_sparse_circular_n8192_v1`
P_deflated: 0.70 (larger N + circular; margin above PLACE_FRAC boundary).

## What this means for PP-47 x PP-49 cap_map row

The SPARSE CODE research spec was correct that K-bump is the wrong fix and PLACE_FRAC
reduction is the right knob. The implementation issue (linear boundary) is a geometry
artifact, not a substrate failure. PP-47 x PP-49 row should NOT be downgraded.
R4-A circular topology is the correct next test.

## Cleanup note

experiments/exp_pp47_pp49_counterfactual_abduction_v2_sparse_placefrac_n4096_v1.py: BLOCKED.
Do not queue. Recommend Strategy create R4-A circular-topology routing for exp_dev.
