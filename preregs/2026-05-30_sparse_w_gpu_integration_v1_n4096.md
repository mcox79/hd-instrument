# Pre-reg: sparse_w_gpu_integration_v1_n4096

**Date:** 2026-05-30
**Anchor:** sparse_w_gpu_integration_v1_n4096
**Script:** experiments/exp_sparse_w_gpu_integration_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T4.3 (sparse-W + GPU composition)

## Hypothesis

Sparse-W (memory savings) and GPU (latency reduction) are independent
capabilities; their COMPOSITION on GPU should preserve both: latency
competitive with dense-GPU (within 2x) AND memory savings >= 4x AND
killer features pass.

## Pre-registered bands

| Outcome      | Condition                                                                       |
|--------------|---------------------------------------------------------------------------------|
| HARD_PASS    | sparse_gpu_lat <= 2 * dense_gpu_lat AND mem_savings >= 4x AND retention >= 0.95 AND KF-2 <= 0.05 at all M in >=2/3 seeds |
| HARD_FAIL    | sparse_gpu_lat > 2 * dense_gpu_lat OR retention < 0.95 OR KF-2 > 0.05 at any M in >=2/3 seeds |
| MIDDLE_BAND  | otherwise                                                                       |

## Calibration

Sparse-CPU envelope and GPU baseline confirmed independently. This anchor
tests composition. The (sparse_GPU vs dense_GPU) latency ratio is the key
diagnostic; equality (1x) would say sparse-W has no latency cost vs dense
on GPU, 2x ceiling allows the extra (q @ keys.T) matmul to count.

## Self-test

- N == 4096 (PROT-018).
- Verdict gates HARD_PASS / HARD_FAIL on synthetic.
- Forward pass at N=1024 M=32 confirms lat_ratio, sparse_retention,
  mem_savings non-null.

## Timeout estimate

smoke_wall_s ~ 0.7s. FULL: 3 M x 3 seeds x ~30s = 270s. scaling_exp=1.5.
**timeout_s = 14400**

## Production config

N=4096, M_sweep=[128, 1024, 4096], seeds=[7,17,23], beta=8.0.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
