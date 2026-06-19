# Prereg: pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu

## Anchor
pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu

## Routing
notes/research_pp50_metric_reformulation_lambda1_power_iteration_2026-06-04.md (Research's stable-observable
replacement for the sigma_sep ratio Exp-Dev flagged as numerically unstable). SUPERSEDES v2 + v3.

## Scientific question
Discriminate the PP-50 transition-zone widening: Tracy-Widom soft-edge (~N^-2/3, N-parameterized envelope)
vs non-self-averaging Hadamard term (~N^0, N-independent envelope). Observable = largest eigenvalue lambda_1
of the noisy Wishart W = Xi_noisy Xi_noisy^T / N (canonical TW edge observable; no near-zero-denominator
blowup). PRIMARY = std(lambda_1) across seeds at each N; SECONDARY = mean edge shift (lambda_1_noisy - clean).
Noise: additive-on-patterns Xi_noisy = Xi + sigma_g*g (formula-matched). lambda_1 via power iteration
(float64, 20 iters) on the M x M Gram (M=int(0.05 N)). sigma_g=0.80; N in {1024,2048,4096,8192,16384}; 12 seeds.

## Pre-registered bands (on beta of PRIMARY std observable)
HARD-PASS Tracy-Widom: beta_std in [0.50,0.80] (~2/3); N-parameterized envelope needed.
HARD-PASS Hadamard: beta_std in [-0.15,0.15] (~0); N-independent envelope correct.
MIDDLE: beta_std in [0.15,0.50].
HARD-FAIL: beta_std < -0.15 (fluctuation grows with N).

## Formula self-tests (PROT-022)
1. (8192/1024)^(-2/3)=0.25. 2. power_iteration(diag[5,2,1])=5. 3. additive noise zero-mean. [PASS]

## Smoke gate
Smoke PASSED on remote GPU (N=256/512/1024, 6 seeds): std(l1) monotone-decreasing 0.083->0.068->0.031,
beta_std=0.700 (Tracy-Widom band), NUMERICALLY STABLE (the v2/v3 non-monotone instability is resolved).

## PROT-018
No _nN suffix (N swept). PROT-021 seed checkpoints keyed run_mode+seed.

## Timeout
Research est <5 min GPU wall (lambda_1 is cheap); timeout_s=7200.

## Queue
overnight_queue (GPU).
