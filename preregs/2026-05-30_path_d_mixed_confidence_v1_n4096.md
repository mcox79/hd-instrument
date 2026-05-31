# Pre-registration: path_d_mixed_confidence_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_d_mixed_confidence_v1_n4096
**Test:** T1 (Test 14 of user-routed batch)
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_path_d_mixed_confidence_v1_n4096.py

## Hypothesis

Path D's per-candidate Bayesian propagation natively accommodates per-fact
confidence. Extending Path D's likelihood query to weight each hop by the
source-fact confidence + emitting a per-prediction propagated confidence
will yield calibrated reasoning: predicted_confidence ~= actual_correct
fraction across confidence buckets, with no major accuracy or latency cost.

If true, Path D becomes the distinguishing mechanism for regulated industries
(legal, medical, audit) that need calibrated multi-hop reasoning.

## Config

- N = 4096 (PROT-018 _n4096 binding).
- BSC substrate (Kerdock-4-coset codebook from shared make_substrate).
- M = 2048; depth = 5; K_paths = 500.
- 5 seeds = [7, 17, 23, 31, 41]; 64 path-starts per seed.
- Path D ONLY (the cross-path generic variant is S9).

### Fact corpus (confidence-stratified)

Base distribution:
- 50% high-confidence facts (conf = 1.0)
- 30% medium (conf = 0.7)
- 20% low (conf = 0.4)

Adversarial overlay: 5% of facts (randomly chosen via separate seed) set to
conf = 0.2 (low-confidence noisy facts).

### Extension

Path D's per-candidate-path log-likelihood is multiplied per-hop by the
source-fact confidence value:

  weighted_log_lik[k, hop] = src_conf(candidates[k][hop]) * log_lik[k, hop]
  log_posterior[k] = sum over hops of weighted_log_lik[k, .]
  predicted_conf[b] = mean over hops of src_conf(top_path[hop])

## Pre-registered bands

**HARD_PASS:**
- Mean calibration deviation across 4 buckets [0.2, 0.4, 0.7, 1.0] <= 0.15
  (per-bucket calibration computed as |mean predicted_conf - actual_correct
  fraction|, averaged over observed buckets).
- Accuracy_conf >= accuracy_blind in >= 3/5 seeds.
- Latency overhead (conf - blind) / blind <= 0.20 in >= 3/5 seeds.

**HARD_FAIL:**
- Mean calibration deviation > 0.40 in >= 3/5 seeds, OR
- Accuracy_conf < 0.80 * accuracy_blind in >= 3/5 seeds.

**MIDDLE_BAND:** all other outcomes.

## Self-tests

- N_FULL == 4096 (PROT-018).
- assign_confidences emits values in {0.2, 0.4, 0.7, 1.0} only.
- per-path predicted_conf is mean over hops (length depth), so values lie
  in the discrete-mixture range of those four levels.
- bucket centering at {0.2, 0.4, 0.7, 1.0} with eps=0.075 yields disjoint
  windows (0.2±0.075 and 0.4±0.075 do not overlap; 0.7±0.075 and 1.0±0.075
  do not overlap; 0.4±0.075 and 0.7±0.075 do not overlap).
- compute_verdict returns T1_HARD_PASS / T1_HARD_FAIL / T1_MIDDLE_BAND /
  T1_INCONCLUSIVE only.

## OOM check

- N=4096, M=2048: keys+vals 16 MiB; W = 64 MiB; CB = 805 MiB (Kerdock).
- Path D allocates per-batch likelihood matrices ~K*depth float32 = 500*5*4
  bytes = 10 KiB per start. Trivial.
- Total peak ~1 GB. Well under 6 GB GPU ceiling.

## Smoke result

- N_smoke=1024, M=256, depth=3, K=50, 1 seed, n_paths=16.
- smoke_wall_s ~ 0.3s.
- acc_blind=1.000, acc_conf=1.000, calib_dev=0.325 (single-seed under-bucketed;
  full sweep gives stable buckets with N_PATHS=64).
- All metrics non-null; instrumentation self-test PASSes.

## Walk-back gate

Smoke produced acc=1.000 in both arms (M=256 is sub-capacity, perfect recall
expected). At FULL (M=2048), the meaningful differentiator is calibration,
not raw accuracy. 5-seed sweep is appropriate; not increasing n.

## Timeout estimate

- smoke_wall_s = 0.3s at N=1024, M=256, depth=3, K=50, n_paths=16, 1 seed.
- FULL: N=4096 (4x), M=2048 (8x), depth=5 (1.7x), K=500 (10x), n_paths=64
  (4x), 5 seeds.
- Scaling: O(B * K * depth) with W mat-vec dominant: per-cell ~ N^2/B amortized
  cost is O(K*depth*N) per start. Net scaling exponent estimate: 1.5
  (dominant K*depth product on per-start basis).
- Component scale factor (FULL/smoke): 4 * 8 * 1.7 * 10 * 4 = ~2176; with
  scaling_exp=1.5 effective ratio ~ 32 vs smoke per-cell, * 5 seeds = 160x.
- timeout_s = ceil(1.5 * 0.3 * 160) = ceil(72) = 300s minimum.
- However the per-start Path D loop is Python-level; conservative actual
  measured equivalents at N=4096 in the existing S9 anchor are ~15-30
  minutes for 5 seeds. Apply 2x safety -> 14400s.

**timeout_s = 14400** (user task spec).

## Notes

- The 5% adversarial overlay tests whether calibration degrades gracefully
  under deliberate low-confidence noise injection.
- This is the FIRST per-confidence-bucket calibration measurement at this N.
  No prior empirical anchor -> bands set per calibration-probe policy
  (theoretical bucket centers ± 0.15 absolute on calibration deviation).
