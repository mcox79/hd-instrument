# Pre-registration: cross_shard_correlation_k10_v1_n4096

Date: 2026-05-30
Anchor: cross_shard_correlation_k10_v1_n4096
Track: C (cross-shard analytics) Phase 1 of 3 (K=10 correlation gate)
Script: experiments/exp_cross_shard_correlation_k10_v1_n4096.py
Queue: overnight_queue (GPU)
Timeout: 14400s (PROT-019 _n4096 floor)
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding contract)

## Scientific question

Given K=10 independently-populated substrate shards W_0..W_9, the matrix
inner-product

  C_ij = tr(W_i.T @ W_j) / N

is a similarity statistic between two outer-product memories. For
synthetic shard-relationship ground truth (specified below), does the
pairwise C_ij ranking correctly identify related shard pairs from a
universe of 45 pairwise comparisons?

This is the substrate-distinctive analytics-layer gate: cross-shard
discovery without exposing per-fact contents.

## Decision context (msg 1 staging)

If K=10 correlation analytics works (HARD_PASS), ship T3 P2 (more shards,
varying overlap densities). If it does not (HARD_FAIL), cross-shard
analytics is closed; per-shard query is the only mode.

## Design

- N=4096, BSC-equivalent Kerdock_4coset codebook (PROT-018 binding).
- K=10 shards. Each shard stores M=50 (key, value) pairs.
- Ground-truth shard relationships:
    Shards (0, 1): share 30 stored KEYS (different values per shard).
    Shards (2, 3): share 30 stored KEYS.
    Shards (4, 5): share 30 stored KEYS.
    Shards (6, 7, 8): share 30 KEYS in a 3-way overlap (one common key set;
       all three shards store that set with independent value assignments).
    Shard 9: isolated, NO key overlap with any other shard.
- 6 related pairs ((0,1), (2,3), (4,5), (6,7), (7,8), (6,8)); 39 unrelated.
- 5 seeds: [7, 17, 23, 31, 41] for shard population.
- 5 cell-seeds total at FULL.

## Metrics (per cell)

1. correlation_AUC: Mann-Whitney AUC of the 45 pairwise C_ij as classifiers
   for "related" vs "unrelated".
2. entity_resolution_precision: for each of 3 doublet pairs (0,1), (2,3),
   (4,5), compute fine-grained C_ij^{ab} = <W_i k_a, W_j k_a>/N for all
   30 true-overlap keys plus 50 distractor keys; threshold top-30;
   precision = correct / 30. Report mean across the 3 doublets.
3. triplet_in_top9: count of {C_(6,7), C_(7,8), C_(6,8)} ranking in
   the top 9 of all 45 pairwise correlations (3 means all 3 triplet
   edges are in the leading rank band).

## Pre-registered bands

HARD_PASS:
  correlation_AUC >= 0.85
  AND entity_resolution_precision >= 0.80
  in >= 3/5 seeds.

HARD_FAIL:
  correlation_AUC <= 0.60 in >= 50% of seeds
  (correlation indistinguishable from noise).

MIDDLE_BAND:
  0.60 < correlation_AUC < 0.85 OR entity_resolution_precision < 0.80
  but correlation_AUC > 0.60.

## Formula self-tests (verified in `_instrumentation_selftest`)

1. N == 4096 (PROT-018 binding).
2. K=10 shards; C(10,2) = 45 pairwise correlations.
3. 6 related pairs (3 doublets + 3 triplet-edges); 39 unrelated.
4. AUC of perfect separator = 1.0; tied = 0.5.
5. Overlap budget check: 4 overlap groups (3 doublets + 1 triplet) x 30
   keys + per-shard unique (M - membership-overlap-count) keys + per-shard
   M values. Codebook C at N=4096 is sufficient.
6. Verdict gates: HARD_PASS, HARD_FAIL fixtures classify correctly.

## Smoke result (CPU, N=1024, M=12 per shard, n_overlap=6, 1 seed)

  seed17: AUC=0.573  entity_prec=0.611  triplet_in_top9=1/3
          related_mean_C=0.0000  unrelated_mean_C=0.0000

  smoke wall: 0.20s (CPU). Verdict: XSHARD_HARD_FAIL because AUC=0.573 falls
  in the HF region (<=0.60). At smoke scale (M=12, overlap=6) the signal-
  to-noise is weak.

  IMPORTANT: at FULL (N=4096, M=50, n_overlap=30) the related-pair signal
  scales with n_overlap (linear in shared-key count), while noise scales
  with sqrt(N). Expect AUC improvement at FULL; HARD_PASS plausible but
  not guaranteed.

  Per role contract: instrumentation working (AUC computed, entity_prec
  non-zero, ranks emitted). Smoke is genuine weak signal, not
  instrumentation-suspect. PROCEEDING TO SHIP. FULL outcome IS the answer.

## OOM check

10 shards x 4096^2 x 4 = 640MB. Codebook: ~256MB. Total ~1GB. Well under
6GB ceiling.

## Timeout estimate

smoke_wall_s = 0.20 (CPU, 1 cell-seed smoke).
FULL has 5 cell-seeds (5x), N=4096 vs N=1024 (4x), 10 shards. Per cell:
build 10 W's (matmul), 45 pairwise tr(W_i W_j), entity-resolution scoring.
scaling_exp = 1.5 (matrix dominant).
  ceil(1.5 * 0.20 * 4^1.5 * 5) = ceil(12) = 12s CPU smoke -> FULL estimate.
GPU 10-50x faster; expected GPU wall < 60s.

User-specified timeout: 14400s. Generous; PROT-019 _n4096 floor.

## Outcome handlers (post-verdict)

- HARD_PASS -> file strategy_request_to_exp_dev for T3 P2 (more shards or
  varying overlap density); cap_map row "cross-shard analytics" advanced.
- HARD_FAIL -> close Track-C analytics layer; cap_map row marked X.
- MIDDLE_BAND -> diagnostic: AUC vs entity-precision split; consider
  rescuing via value-correlated overlap (related shards store correlated
  values for shared keys) before deciding.
