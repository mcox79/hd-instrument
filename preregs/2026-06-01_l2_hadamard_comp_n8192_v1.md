# Prereg: l2_hadamard_comp_n8192_v1

**Filed:** 2026-06-01
**Anchor:** l2_hadamard_comp_n8192_v1
**Queue:** overnight_queue
**Script:** experiments/exp_l2_hadamard_comp_n8192_v1.py

## Hypothesis

L=2 nested composition with Hadamard-binding achieves end-to-end accuracy > 0.88
at N_outer = N_inner = 8192 (conservative inner load alpha ~ 0.0024).

## Pre-registered bands

- HARD-PASS: end-to-end accuracy > 0.88 in >= 4/5 seeds.
- MIDDLE: 0.75 <= accuracy <= 0.88 (noisy but functional).
- HARD-FAIL: accuracy < 0.75 in >= 3/5 seeds.

## Design

N=8192 (FULL), N=1024 (SMOKE). n_entities=n_composite=20. Hadamard codebook first 20 rows.
W_inner, W_outer both N x N float32. Retrieval: synchronous 10 steps. 5 seeds (smoke: 2).

## PROT-018

_n8192 suffix binding. Production N=8192 confirmed (N = 8192 at top of script).

## OOM pre-check

W at N=8192: 8192^2 * 4 = 256 MB per matrix. Two matrices = 512 MB. Within 8 GB GPU.

## Timeout estimate

smoke_wall_s ~ 5s (N=1024). Full: smoke_wall * (8192/1024)^1.5 * (5/2) ~ 450s.
timeout_s = 900 (2x safety for GPU overhead).

## N-suffix note

_n8192 suffix: binds N=8192. Pre-ship audit: grep confirms N = 8192 in script.
