# Pre-registration: kf5_multi_output_steer_n4096

**Date:** 2026-05-29
**Anchor:** kf5_multi_output_steer_n4096
**Script:** experiments/exp_kf5_multi_output_steer_n4096.py
**Queue:** overnight_queue
**Trigger:** KF-5 post-PARTIAL_DECOUPLING; alpha-3 highest-priority Tier-1 batch

## Hypothesis
At fixed M_frac=4, N=4096, BSC codebook, beta in {2,8,16,32,64,128}:
Top-k output diversity (k in {1,5,10}) and output distribution entropy change with beta
even though argmax (bpc) does not. If top-5 Jaccard change >= 0.30 across beta sweep,
steerability EXISTS at the multi-output layer and KF-5 reformulates.

## Config
- N_FULL = 4096 (PROT-018: _n4096 suffix binding)
- Seeds: [7, 17, 23, 31, 41]
- Beta sweep: [2.0, 8.0, 16.0, 32.0, 64.0, 128.0]
- Beta ref: 32.0 (Jaccard change computed vs this reference)
- M_frac = 4.0, BSC codebook (Kerdock-safe at any N)
- top-k values: {1, 5, 10}

## Pre-registered bands
- HARD_PASS: mean_topk_jaccard_change(k=5) >= 0.30 across beta sweep in >= 3/5 seeds
  AND mean_entropy_range >= 1.0 bit.
- HARD_FAIL: mean_topk_jaccard_change(k=5) < 0.10 across all betas and all seeds
  AND entropy_range < 0.5 bits.
- MIDDLE_BAND: Jaccard change in [0.10, 0.30) OR entropy_range in [0.5, 1.0).

Calibration probe (no prior empirical multi-output diversity anchor).
Bands per calibration-probe policy: "no prior empirical anchor; +-50% of theoretical expectation."

## N-suffix
_n4096 suffix; production N = 4096. PROT-018 satisfied.

## Kerdock audit
BSC codebook: safe at any N. Not Kerdock. No even-log2 constraint. OK.

## Timeout estimate
smoke_wall_s = 0.3s (N=1024, 1 seed, 3 betas).
FULL: N=4096, 5 seeds, 6 betas. scale = (4096/1024)^1.5 * 5 * (6/3) = 8 * 5 * 2 = 80.
GPU speedup ~10x. timeout_s = ceil(1.5 * 0.3 * 80 / 10) = ceil(3.6) -> 600s.
PROT-019 floor for _n4096 = 14400s. timeout_s = 14400.

## Smoke result
SELFTEST PASS. entropy_range=7.74bits (valid, non-null). jc=0.0 at smoke scale expected
(near-untrained W at 3000 steps / N=1024). Not suspicious. Ship allowed.

## Downstream cap_map move
- HARD_PASS: KF-5 row reformulates from "beta-steerability" to "multi-output-steerability";
  annotation update; product story: "choose output distribution via beta at multi-output level"
- HARD_FAIL: KF-5 collapses to entropy-only; 1D M-axis model confirmed; row annotation
- MIDDLE_BAND: partial reformulation; refine KF-5 scope
