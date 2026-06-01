# Pre-registration: path_d_k1_cross_n_null_prediction_v1_n4096

Date: 2026-06-01
Anchor: path_d_k1_cross_n_null_prediction_v1_n4096
Queue: remote_cpu_queue
Script: experiments/exp_path_d_k1_cross_n_null_prediction_v1_n4096.py
HDLAB_EXP_NAME env: 7d39e13

## Hypothesis

At K=1, depth=5, M=16N, sweeping N in {4096, 16384}:
the path_b_top1_acc (substrate K=1 phase-boundary signal) is N-INDEPENDENT.
The P3 percolation framework predicts: Path D's per-hop independence +
bootstrap-percolation dynamics set the signal magnitude by candidate-
discrimination capacity per hop (a function of p_eff = K/M = 1/16N only),
NOT by total substrate dimensionality N. This is a falsifiable null prediction.

## Config

- K_paths = 1 (fixed)
- depth = 5
- M = 16 * N (fixed ratio per routing)
- N sweep: {4096, 16384} (N=8192 skipped; see below)
- 5 seeds: [7, 17, 23, 42, 99]
- k_random_keys = 100 per cell
- device: cpu (PROT-022)

## N=8192 skip rationale

N=8192 has log2(N)=13 (odd). The Kerdock/dual-BCH codebook construction
requires even log2(N). Using a BSC codebook at N=8192 would change the
codebook class and confound the N-axis comparison (codebook type != N=4096
and N=16384 cells). Decision: skip N=8192; use {4096, 16384} only.
This is consistent with the routing's "OR trim to {4096, 16384}" option.
Pre-reg records 2 N-point design.

## Primary metric

path_b_top1_acc = direct Path B walk accuracy (K=1 effective, no candidate pool)
Measured per (N, seed) cell; N-mean computed per N value.
Baseline: v307 k1_mean = 0.022 at N=4096, M=16N.

## Pre-registered bands

### HARD-PASS (null prediction confirmed)
max|acc_N - baseline| <= 0.01 (1pp) across both N values.
Interpretation: K=1 signal is N-independent; percolation N-independence
prediction HOLDS; P3 framework's load-bearing claim strengthened.

### HARD-FAIL (null prediction refuted)
max|acc_N - baseline| > 0.03 (3pp) for any N value.
Interpretation: K=1 signal IS N-driven; percolation framing weakens;
substrate-physics signal has N-dependence percolation theory did not predict.

### MIDDLE-BAND
max|acc_N - baseline| in (0.01, 0.03].
Interpretation: weak N-dependence; some confound but small; inconclusive on
percolation framing; further N-axis sweep recommended.

## Formula self-tests (verified at module scope in script)

1. HP: N=4096 acc=0.022, N=16384 acc=0.025 -> delta=0.003 <= 0.01 -> NULL_PRED_HARD_PASS CONFIRMED
2. HF: N=4096 acc=0.022, N=16384 acc=0.060 -> delta=0.038 > 0.03 -> NULL_PRED_HARD_FAIL CONFIRMED
3. MIDDLE: N=4096 acc=0.022, N=16384 acc=0.040 -> delta=0.018 in (0.01,0.03] -> NULL_PRED_MIDDLE_BAND CONFIRMED

## N-suffix note

_n4096: PROT-018 base N = 4096 (minimum N in the N-sweep grid; anchor records base).
The sweep includes N=16384 as a second cell-axis point. Production run processes
N=4096 AND N=16384 cells. The suffix binds the base/minimum N.

## Smoke gate result

Smoke: N_grid=[1024,4096] seeds=[17] k_keys=20. wall=13.6s.
- N=1024 cell: path_b_top1=0.0 (expected at small N)
- N=4096 cell: path_b_top1=0.1 (expected smoke; fewer keys)
All metrics non-null, n_eval=20 per cell. PASS.
Formula gates fire correctly (self-test PASS at module scope).

## Timeout estimate

smoke_wall_s: N=4096 cell took ~13.6s at k_keys=20.
FULL: k_keys=100 (5x more) + 5 seeds.
  N=4096: 5 seeds * (13.6 * 100/20) = 5 * 68s = 340s.
  N=16384: scaling_exp=1.5; (16384/4096)^1.5 = 4^1.5 = 8x.
    340s * 8 = 2720s.
  Total: 340 + 2720 = 3060s. 1.5x safety = 4590s.
PROT-019 floor: 14400s. timeout_s = 14400.

## Calibration note

Prior empirical anchor at N=4096: v307 k1_mean=0.022.
N=16384 has no prior empirical anchor. The null prediction (N-independence)
is from percolation theory (P3 drill). Per calibration-probe policy:
tolerance bands set wide (HP: +-1pp; HF: >3pp) to allow for
first-measurement variance. These are tighter than +-50% because we have
a strong theoretical prediction with specific directional claim.

## Strategic value

Directly tests P3 percolation theory's falsifiable null prediction.
HARD-PASS: P3 cap_map percolation caveat strengthened; framework reliable.
HARD-FAIL: percolation framing weakens; substrate-physics has N-dependence
  percolation theory didn't predict; research drill warranted on N-scaling.
Either outcome is strategically informative for production dimensionality
selection (N=4096 vs N=16384 operating-point safety analysis).

## Origin

R4 from cap_map v307 follow-on routing (notes/strategy_request_to_strategy_v307_followon_experiments_2026-06-01.md).
