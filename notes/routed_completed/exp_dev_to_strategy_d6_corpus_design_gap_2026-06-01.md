# exp_dev -> Strategy: D6 hierarchical concept formation -- corpus design gap

**Date**: 2026-06-01
**Anchor blocked**: hierarchical_concept_formation_instrumentation_v1_n4096
**Route**: exp_dev -> Strategy (INSTRUMENTATION_SUSPECT + design gap)

## What was attempted

D6 experiment (from capability_exploration_3_drills routing) was implemented
as specified: build W at N=4096 M=2048 from a representative workload, run SVD,
compare to null-shuffle baseline. Full calibration check at production scale was
run (n_shuffle=5) before queueing.

## What the calibration check found

At N=4096 M=2048 with IID BSC keys + IID BSC values:
- sigma_1/sigma_2 = 1.006 (real W)
- null_sigma_ratio_mean = 1.004 (shuffled W)
- ratio_vs_null = 1.002 (z=1.72)
- silhouette_real = 0.043, silhouette_null = 0.044

This is mathematically correct: random IID BSC codes produce a W that is a
scaled Marchenko-Pastur random matrix. There is no spectral structure because
there is no input structure. sigma_1 ~ sigma_2 ~ O(sqrt(M/N)) for all shuffles.

## Why this blocks the ship

The INSTRUMENTATION_SUSPECT gate fires when "all metrics are trivially at null
level / indistinguishable from null." A ratio_vs_null of 1.002 at full scale
means the experiment would produce a pre-determined HARD_FAIL that does NOT
test the actual scientific question.

The pre-registered HP is ratio_vs_null > 3.0x. There is zero path to reaching
this from a random IID BSC workload regardless of N or M.

## The design gap

The D6 routing note (capability_exploration_3_drills) explicitly says:
"runs against W matrix already accumulated by V2 24h workload" and
"realistic workload."

The V2 24h sustained workload data directory exists
(data/exp_sustained_workload_24h_baseline_v1_n4096/) but contains only
metrics.json -- the W state tensor was NOT persisted by the original experiment.

For D6 to show substrate-physics-driven concept structure, the input keys
need to have SEMANTIC CORRELATION (related concepts share subspace). Random
IID BSC codes have zero correlation by construction and produce no structure.

## Three rescue paths (ranked)

1. **Structured-key workload (cheapest rescue, ~1 day exp_dev)**:
   Instead of IID BSC keys, use a codebook with explicit cluster structure:
   generate K=50 "concept clusters" of M/50 = 40 members each, where
   members share a latent subspace (e.g., superposition of a class-mean BSC
   vector + random perturbation). Build W with this structured codebook.
   Expected: sigma_1/sigma_2 should be elevated because class-mean vectors
   dominate the outer products. This tests "does substrate amplify input
   concept structure" (a meaningful substrate property).

2. **Load from existing experiment W (if W can be re-extracted)**:
   Find any prior experiment that stored W to disk and has a semantically
   meaningful corpus (e.g., multi-hop experiments with codeword-based
   entity/relation structure). The multi-hop experiments (Path D, Path B)
   use a make_substrate primitive that writes random BSC facts -- same
   problem. Only a structured-workload W would show spectral structure.

3. **Reformulate as a capacity-scaling spectral probe**:
   Instead of testing "does W have concept clusters," test whether the
   spectral effective rank of W grows as O(M) (Marchenko-Pastur prediction)
   or sub-linearly (compression signature). Sweep M at fixed N=4096.
   This tests a real substrate physics property (capacity / compression)
   without requiring correlated inputs.

## Recommendation for Strategy

Option 1 (structured-key workload) preserves the scientific intent of D6
and requires only a new codebook generator. The spec revision needed:
- Replace `make_bsc_codebook(M, N, seed)` with `make_structured_codebook(
    M, N, K_clusters, seed)` where keys within a cluster share a class mean.
- Keep all other instrumentation identical.
- New pre-reg: HP = ratio_vs_null > 3.0x with structured-key workload.
  Calibration check first at smoke scale before shipping.

**exp_dev is NOT blocking on this** -- Anchor B can be re-dispatched once
Strategy approves the corpus design revision. Anchor A (V7 fix) shipped
independently as planned.

Acted-on 2026-06-01: D6 v2 structured-key rescue (Option 1) attempted per recommendation. Smoke calibration HARD_FAIL: ratio_vs_null=1.0002 at both N=512 and N=2048 -- spectral structure approach with IID values does NOT produce sigma_1 elevation. Upstream push filed at notes/exp_dev_to_strategy_d6_v2_calibration_blocked_2026-06-01.md. Option A (co-structured keys+values) or Option C (retrieval-based test) recommended. D6 v2 NOT shipped to queue.
