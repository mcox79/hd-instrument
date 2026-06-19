# Pre-reg: multi_signal_kf1_design_v2_n4096

**Date:** 2026-05-30
**Anchor:** multi_signal_kf1_design_v2_n4096
**Script:** experiments/exp_multi_signal_kf1_design_v2_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T2.3 (multi-signal KF-1 rebuild)

## Hypothesis

A weighted composite of 5 KF-1 signals (posterior entropy, spectral spread,
bundle norm, geometric distance to nearest stored fact, cross-replica
consistency) clears the 0.90 AUC ceiling that v1's composite hit
(0.898-0.906) at ALL 3 operating points (M=128 low, M=1024 mid,
M=4096 near-cap).

## Pre-registered bands

| Outcome      | Condition                                                                      |
|--------------|--------------------------------------------------------------------------------|
| HARD_PASS    | best composite AUC >= 0.92 at ALL 3 ops AND robust (std_seeds <= 0.03)         |
| HARD_FAIL    | best composite AUC <= 0.85 at any operating point                              |
| MIDDLE_BAND  | otherwise                                                                      |

## Calibration

v1 anchored at 0.898-0.906. HP at 0.92 = 2% absolute improvement, requiring
the per-OP weight optimization to do real work. HF at 0.85 = clear
regression. Robustness clause (std <= 0.03 across seeds) prevents lucky
single-seed HP.

## Self-test

- N == 4096 (PROT-018).
- AUC returns 1.0 for [0.1,0.2,0.8,0.9]/[0,0,1,1] (oriented).
- Verdict gates return HARD_PASS / HARD_FAIL on synthetic.
- Forward pass at N=1024 M=32 returns per_signal_auc, composite_max_auc,
  composite_weighted_auc all non-null.

## Timeout estimate

smoke_wall_s ~ 0.4s. FULL: 3 OPs x 5 seeds x ~120s (grid search over 5^5
composite weights) = 1800s. scaling_exp=1.5.
**timeout_s = 14400**

## Production config

N=4096, ops=[("low",128),("mid",1024),("near-cap",4096)],
seeds=[7,17,23,31,41], beta=8.0, top_k_sig=32, n_probe_in=100, n_probe_out=100.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
