# Pre-reg: path_probability_propagation_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_probability_propagation_v1_n4096
**Script:** experiments/exp_path_probability_propagation_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Multi-hop Path D (Bayesian probability-domain propagation)

## Hypothesis

Multi-hop reasoning via Bayesian path-likelihood combination
(probability-domain, not state-domain) does not suffer noise compounding.
Independent per-hop likelihood queries combined via log-likelihood sum
yield top-1 path identification accuracy >= 0.60 at depth 4.

## Pre-registered bands

| Outcome      | Condition                                                                       |
|--------------|---------------------------------------------------------------------------------|
| HARD_PASS    | top-1 accuracy >= 0.60 at depth 4 with K_paths >= 100 in >=3/5 seeds            |
| HARD_FAIL    | accuracy <= 0.20 at EVERY depth in {3,4,5} across all K_paths in >=3/5 seeds    |
| MIDDLE_BAND  | otherwise                                                                       |

## Calibration

Path B (state-propagation) is the same-cap_map alternative; if Path B fails
and Path D passes, this opens a substantively-different multi-hop mechanism.
K_paths=50 (cheap) vs 100 (HP) vs 500 (saturation check). No prior empirical
anchor; bands widened to depth=4 (mid-range) per calibration policy.

## Self-test

- N == 4096 (PROT-018).
- HP_DEPTH=4 in DEPTHS_FULL.
- HP_K_MIN=100 in K_PATHS_FULL.
- Forward pass at N=1024 M=32 depth=3 K=20 confirms accuracy, margin non-null.

## Timeout estimate

smoke_wall_s ~ 0.07s. FULL: 3 K x 3 depths x 5 seeds = 45 cells.
scaling_exp=1.5. Estimated ~1800s.
**timeout_s = 21600**

## Production config

N=4096, M=256, depths=[3,4,5], K_paths=[50,100,500], seeds=[7,17,23,31,41],
beta=4.0.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
