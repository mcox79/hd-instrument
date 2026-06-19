# Pre-reg: gpu_baseline_expansion_v1_n8192

**Date:** 2026-05-30
**Anchor:** gpu_baseline_expansion_v1_n8192
**Script:** experiments/exp_gpu_baseline_expansion_v1_n8192.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T2.2 (extend GPU vs CPU speedup measurement to N=8192)

## Hypothesis

GPU implementation of the substrate at N=8192 delivers >= 10x speedup
vs CPU at single-op queries AND killer features (KF-1 hallucination
detection, KF-2 edit isolation, retention) pass on GPU.

## Pre-registered bands

| Outcome      | Condition                                                                       |
|--------------|---------------------------------------------------------------------------------|
| HARD_PASS    | mean single-op speedup >= 10x across seeds AND all KFs pass (per seed)          |
| HARD_FAIL    | speedup <= 2x OR any KF fails on GPU in any seed                                |
| MIDDLE_BAND  | speedup in [2, 10) or marginal KF                                               |

## Calibration

F-batch v2 measured 22.67x at N=4096. At N=8192, matrix-multiply bandwidth
should keep speedup high but not strictly proportional. HARD_PASS at 10x
is a conservative reinstatement of the v2 result at expanded scale.

## Self-test

- N == 8192 (PROT-018 _n8192).
- M = N // 4 = 2048.
- compute_verdict returns HARD_PASS on synthetic 12x speedup + KF_pass.
- Forward pass at N_smoke=1024 confirms cpu_lat_per_op_s populated.

## Timeout estimate

smoke_wall_s ~ 1s. FULL N=8192 with 3 seeds, 4 batch sizes, full KF battery.
scaling_exp=2.0 (matrix mult dominant). Estimated 600-1200s. PROT-019
_n8192 floor 21600s.
**timeout_s = 21600**

## Production config

N=8192, M=2048, seeds=[7,17,23], batch_sizes=[1,16,64,256], beta=8.0,
n_timing_reps=5, n_ops_per_timing=50.

## N-suffix binding

_n8192 -> production N = 8192 (PROT-018; PROT-019 timeout floor).
