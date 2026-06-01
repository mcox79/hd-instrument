# exp_dev -> Strategy: D6 v2 structured-key calibration BLOCKED

**Date**: 2026-06-01
**Anchor attempted**: hierarchical_concept_formation_instrumentation_v2_structured_n4096
**Status**: INSTRUMENTATION_SUSPECT -- smoke gate HARD_FAIL. DO NOT SHIP.

## Smoke result

N=512 M=256 K_clusters=32 flip_p=0.3 seed=42:
- sigma_ratio_real = 1.0234
- null_sigma_ratio_mean = 1.0232
- ratio_vs_null = 1.0002 (z=0.01)

HARD_FAIL threshold: ratio_vs_null < 1.5. Smoke is at 1.0002 -- indistinguishable
from null. This triggers INSTRUMENTATION_SUSPECT gate.

## Multi-scale smoke (N_smoke x 4 = N=2048)

Also tested N=2048 M=1024 K=32 cluster_size=32 (larger cluster):
- ratio_vs_null = 0.9995 (IID values)
- ratio_vs_null = 0.61 (structured values, same cluster -- null HIGHER than real?)

Both show no spectral lift from structured keys.

## Root cause of failure

The spectral concentration metric sigma_1/sigma_2 in W measures the COMBINED
outer-product covariance of BOTH keys AND values. With structured keys but IID
values, the W matrix does NOT show spectral concentration because:

  W = (vals.T @ keys) / N

For keys with cluster structure K_c and IID values, the expected covariance is:
  E[W] = 0 (IID values)
  Var[W]_ij ~ M/N (same as random)

The cluster structure in keys only elevates sigma_1 if the VALUES also have
matching cluster structure, because the outer product v_k @ k.T only
concentrates spectral energy when v and k are correlated.

With IID values and structured keys, the Marchenko-Pastur bulk spectrum
dominates regardless of key structure at practical M/N ratios.

This is a fundamental design issue with the D6-rescue Option 1 spec. The
spec assumed that structured keys alone would elevate sigma_1, but this is
only true for E[W] (the mean substrate) and not for the per-sample W.

## What is needed for D6 to work

Option A (structured keys + structured values, same cluster):
  Build W with keys[i] and vals[i] from the same cluster. The outer product
  then has cluster-correlated terms that elevate sigma_1 above Marchenko-Pastur.
  This requires a co-structured codebook (keys and values share cluster labels).

Option B (spectral effective-rank sweep, different metric):
  The D6 rescue Option 3 from the gap note: measure spectral effective rank
  vs Marchenko-Pastur prediction as M varies at fixed N. This tests compression
  (sub-linear rank growth) rather than concept structure.
  Does NOT require structured keys.

Option C (abandon sigma_1/sigma_2, use intra-cluster retrieval):
  Instead of SVD-based spectral test, query W with a held-out cluster member
  and measure cosine to other members. Structured retrieval test, not spectral.

## Recommendation to Strategy

Option A is the clearest fix: replace D6's value codebook with a
co-structured codebook (shared cluster labels between keys and values).
This directly tests whether substrate amplifies semantic co-occurrence
(items from same cluster stored together retrieve from same cluster).

Revised spec:
  - K=50 clusters, M/K=40 members per cluster
  - keys[c*cluster_size + i] = class_mean_k[c] + perturbation
  - vals[c*cluster_size + i] = class_mean_v[c] + perturbation
    (different class means for keys vs vals, same cluster label)
  - W = (vals.T @ keys) / N; sigma_1 should now be elevated because
    W's top singular direction captures the cluster co-occurrence structure
  - Null: shuffle cluster assignments (keep norms, break co-structure)

exp_dev is NOT blocking on this -- Anchor B (AQSIM diagnostic) shipped
independently. This note is routed to Strategy for spec revision.

Acted-on 2026-06-01: D6 v3 co-structured codebook shipped per Option A recommendation
