# Prereg: sparse_w_active_subspace_v1_n4096

Date: 2026-05-30
Anchor: sparse_w_active_subspace_v1_n4096
Script: experiments/exp_sparse_w_active_subspace_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

Sparse-W stores M rank-1 components (keys, values) instead of dense N x N.
Memory ratio = 2 * M * N / (N * N) = 2 * M / N.
At M=128, N=4096: memory_ratio = 256/4096 = 0.0625 = 1/16 of dense.

Mathematically, sparse retrieve `(k_query @ keys.T) @ values / N` ==
dense retrieve `W @ k_query` where `W = values.T @ keys / N`. So accuracy
should match dense modulo numerical precision (verified in self-test).

## Pre-registered bands

- **HARD_PASS**: at M=128, memory_ratio <= 0.25 AND mean_retention >= 0.95
  AND KF-2 max_iso <= 0.05.
- **HARD_FAIL**: ANY tested M loses >= 20% retention (sparse storage broke
  retrieval at that M).
- **MIDDLE_BAND**: otherwise.

## Sweep

N=4096; M in [32, 64, 128, 256, 512, 1024]; 5 seeds.

## Timeout estimate

User specified 14400s. scaling_exp=1.5.
