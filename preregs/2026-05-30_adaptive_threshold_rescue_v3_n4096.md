# Pre-reg: adaptive_threshold_rescue_v3_n4096

**Date:** 2026-05-30
**Anchor:** adaptive_threshold_rescue_v3_n4096
**Script:** experiments/exp_adaptive_threshold_rescue_v3_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T2.4 (third instrumentation rescue for adaptive_threshold; research drill 2026-05-30 commit ee0d4f8 identified pathology pattern)

## Hypothesis

v1 used a broken proxy (all-zero score in every cell).
v2 used TPR - 5*FPR which SATURATES at sweep endpoints (constant at both ends).
v3 uses Youden's J = TPR(tau) - FPR(tau), which is bounded in [-1, 1] and
ZERO at both endpoints by construction (at tau=0: TPR=FPR=1, J=0; at
tau=1: TPR=FPR=0, J=0). Any interior peak is by construction non-saturated.

This is the standard ROC-optimal-threshold metric and structurally cannot
exhibit the v2 saturation pathology.

## Pre-registered bands (revised post research drill)

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | >=7/9 cells produce INTERIOR optimal tau (not at sweep boundaries) AND cell-optima span >= 1 order of magnitude (max/min >= 10) |
| HARD_FAIL    | >=4/9 cells saturate at sweep boundary OR all optima within +/-10% of each other |
| MIDDLE_BAND  | otherwise                                                                |

## Calibration

The framework's heuristic tau_pred = 1/sqrt(M_frac * beta) is REFERENCE
only -- the research drill (commit ee0d4f8) identified tau_pred as
heuristic with no theoretical derivation. We compute log2_miss vs
tau_pred but do NOT gate on it. Verdict is based on empirical optima
behavior alone (interior + cell-dependence).

## Instrumentation safeguard (key v3 fix)

`_instrumentation_selftest` asserts at smoke scale:
- (a) `distinct_j_vals >= 2` (rules out v1 all-zero AND v2 all-flat-saturation)
- (b) `j_range > 0.1` (J actually varies across the sweep)
- (c) `j_max >= 0.5` (substrate is discriminative)
- (d) `operational == True` (in_mean clearly > 2 * oos_mean)

This blocks the 3-occurrence pathology pattern (v1: broken metric; v2:
boundary saturation; v3: would block at gate if either repeated).

## Self-test

- N == 4096 (PROT-018).
- M_FRACS_FULL == [1.0, 4.0, 16.0] (M_frac=0.25 dropped per research spec).
- TAU_SWEEP_FULL has 11 points spanning 4 orders of magnitude.
- predicted_threshold(1,1) == 1.0; predicted_threshold(4,4) == 0.25.
- Verdict gates HARD_PASS / HARD_FAIL on synthetic.
- Forward pass at smoke (M_frac=1, beta=10, N=1024) shows
  distinct_j_vals=4, j_range=1.0, j_max=1.0, tau_emp=0.001, interior=True,
  operational=True.

## Timeout estimate

smoke_wall_s = 0.16s. FULL: 3 M_fracs x 3 betas x 3 seeds = 27 cells,
each with 11-tau sweep (200 in-store + 200 OOS probes once per cell-seed).
N ratio = 4 (1024 -> 4096), seed ratio = 3, M_frac ratio increases work.
scaling_exp = 1.5. Estimate: `ceil(1.5 * 0.16 * 4^1.5 * 3) ≈ 6s`.
But the per-cell work involves a 200-probe in-store eval at N=4096 with
softmax on a (C, n_probe) tensor where C = codebook size at N=4096.
Realistic: ~10-30s per cell-seed -> 27 cells * 30s = 810s. Pad for
M_frac=16 -> ~1500s. Round up to 1800s. **timeout_s = 14400** (safety
margin for GPU contention; large headroom).

## Production config

N=4096, M_fracs=[1.0, 4.0, 16.0] (M_frac=0.25 DROPPED per research spec),
betas=[4.0, 10.0, 32.0], seeds=[7,17,23],
tau_sweep=[0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99] (11 points).
M is CAPPED at 16384 for the highest M_frac to avoid OOM.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
