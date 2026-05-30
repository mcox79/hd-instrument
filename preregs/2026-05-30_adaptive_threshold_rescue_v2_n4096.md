# Pre-reg: adaptive_threshold_rescue_v2_n4096

**Date:** 2026-05-30
**Anchor:** adaptive_threshold_rescue_v2_n4096
**Script:** experiments/exp_adaptive_threshold_rescue_v2_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T2.4 (rescue v1 broken-scoring failure)

## Hypothesis

v1 HARD_FAILed because best_score=0.0 in every cell (label-vs-honest #142
flagged: scoring proxy broken, not framework-prediction degraded). v2 fixes
the scoring metric to be killer-feature-anchored (TPR - 5*FPR over
in-store vs OOS probes) and verifies the framework's predicted optimum
threshold matches the empirical optimum.

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | |log2(tau_emp / tau_pred)| <= log2(1.2) in >=7/9 (M_frac x beta) cells   |
| HARD_FAIL    | |log2(tau_emp / tau_pred)| >= log2(1.5) in >=6/9 cells                   |
| MIDDLE_BAND  | otherwise                                                                |

## Calibration

The framework's tau_pred(M_frac, beta) = 1/sqrt(M_frac * beta) is a
heuristic from cap_map. HP at +/-20% in log2 is symmetric and tolerant
of small mismatches; HF at +/-50% in log2 is the dominant-mismatch
condition. v1 failed due to instrumentation, so v2's instrumentation
self-test explicitly asserts score variance across taus at smoke scale.

## Instrumentation safeguard (key v2 fix)

`_instrumentation_selftest` asserts `score_var > 0` across the test tau
sweep. v1's bug pattern (all-zero score) is structurally caught at gate
time.

## Self-test

- N == 4096 (PROT-018).
- predicted_threshold(1,1) == 1.0; predicted_threshold(4,4) == 0.25.
- Verdict gates HARD_PASS / HARD_FAIL on synthetic.
- Forward pass with stress config (M_frac=0.5, beta=1.0, taus=[0.001..0.9])
  confirms score_var > 0.

## Timeout estimate

smoke_wall_s ~ 0.1s. FULL: 3 M_fracs x 3 betas x 3 seeds = 27 cells,
each with 9-tau sweep + KF2 evaluation. scaling_exp=1.5. Estimated 1800s.
**timeout_s = 14400**

## Production config

N=4096, M_fracs=[0.25, 1.0, 4.0] (re-scaled to avoid OOM at original M_frac=16),
betas=[4.0, 10.0, 32.0], seeds=[7,17,23],
tau_sweep=[0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 0.9].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
