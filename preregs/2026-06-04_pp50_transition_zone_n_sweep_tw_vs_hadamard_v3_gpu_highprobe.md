# Prereg: pp50_transition_zone_n_sweep_tw_vs_hadamard_v2_gpu

## Anchor
pp50_transition_zone_n_sweep_tw_vs_hadamard_v2_gpu

## Priority
A (Research Q2 answer; PP-50 transition-zone mechanism discriminator). Supersedes deferred v1 (guessed
noise -> 0 violations). Uses the CORRECT per-pattern log-normal noise (PP-50 v3 spec) + sigma_sep metric.

## Scientific question
At fixed sigma_g=0.80 (~sigma_g_crit=0.833), sweep N in {1024,2048,4096,8192,16384}; measure
sigma_sep = |k3_aug-k3_base|/|k3_base|*1000 (isochoric kappa3, matrix-free Hutchinson, per-pattern
log-normal noise on Xi). Fit scaling exponent beta (sigma_sep ~ N^-beta). beta~2/3 => Tracy-Widom
(N-parameterized envelope); beta~0 => Hadamard (N-independent envelope correct).

## Pre-registered bands (Q2)
HARD-PASS Tracy-Widom: beta in [0.50, 0.80]. HARD-PASS Hadamard: beta in [-0.15, 0.15].
MIDDLE: beta in [0.15, 0.50]. HARD-FAIL: sigma_sep non-monotone in N OR beta < -0.15 (increasing).

## Formula self-tests (PROT-022)
1. (8192/1024)^(-2/3)=0.25. 2. per-pattern lognormal mean=exp(sg^2/2). 3. kappa3 matrix-free finite + GPU mem>0.

## N-suffix binding (PROT-018)
NO _nN suffix; N is swept; grid {1024,2048,4096,8192,16384}. 5 seeds (PROT-021).

## Timeout
matrix-free Hutchinson (no N^2 matrix); N=16384 cell heaviest. timeout_s=21600.

## Smoke gate
--skip-smoke: no local CUDA. Remote --self-test gates lognormal-mean + matrix-free kappa3 + GPU mem.
GPU template (assert cuda, device=cuda, batched matmul).

## Queue
overnight_queue (GPU; fills empty GPU slot; avoids CPU overflow).
