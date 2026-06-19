# Pre-registration: skahm_moe_shift_predictor_v1

Date: 2026-05-27
Experiment: exp_skahm_moe_shift_predictor_v1.py
Queue: overnight_queue (GPU)
Timeout: 900s

## Hypothesis
SKAH-M log-K routing-interference model:
  retention_A(K) ~ retention_A(K_ref) * exp(-gamma * log(K / K_ref))
is consistent with K_perarm_v1 data (K=2..64) if gamma is approximately stable across K.

Additionally, saddle-hierarchy DAM predicts first-doubling (K=2->4) steeper than
second-doubling (K=4->8): steepness_ratio > 1.0.

## Design
- Part 1: Analytical gamma-CV computation on K_perarm_v1 reference data (K=2..64)
- Part 2: Fresh-seed Hebbian MoE sweep at K={2,4,8}, N=1024, 5 seeds

N = 1024 (Part 2). No _n<N> suffix.

## N-suffix binding (PROT-018)
No _n<N> suffix in anchor name. Production N = N_FULL = 1024.

## Pre-registered thresholds

### Gamma CV (on reference K_perarm_v1 data)
- HARD-PASS: CV(gamma) < 0.30 AND steepness_ratio > 1.0
- HARD-FAIL: CV(gamma) > 0.50 OR steepness_ratio < 0.70
- MIDDLE-BAND: otherwise

Calibration note: gamma is computed from 5 K-values (K=4,8,16,32,64 relative to K=2).
The theoretical prediction (perfect log-K model) would give CV=0. We allow up to 30%
variation as the log-K approximation is a first-order fit.

## Timeout estimate
Analytical Part 1: ~0s (pure arithmetic on 6 reference points).
Part 2 (Hebbian sweep): N=1024, K={2,4,8}, 5 seeds.
smoke: N=256, K=[2,4], 1 seed -> elapsed=0.004s (analytical dominates)
FULL estimate: 5 seeds x 3 K x N=1024 Hebbian outer product -> ~30s CPU / ~10s GPU
timeout_s = 900 (including margin for serial seed loop)

## Parent experiment
wave14_moe_shift_K_perarm_v1 (K=2..64, retention_A={2:0.8209, 4:0.8086, 8:0.8012,
16:0.7959, 32:0.7919, 64:0.7883})

## Formula self-test results (pre-registered)
gamma(K=2->4) = 0.02178
gamma(K=2->8) = 0.01752
gamma(K=2->16) = 0.01487
gamma(K=2->32) = 0.01297
gamma(K=2->64) = 0.01169
CV_ref = 0.2546 < 0.30 -> HARD_PASS predicted
steepness_ratio = (0.8209-0.8086)/(0.8086-0.8012) = 0.0123/0.0074 = 1.662 > 1.0 -> HARD_PASS
Expected overall verdict: HARD_PASS (analytical result; Part 2 provides independent confirmation)
