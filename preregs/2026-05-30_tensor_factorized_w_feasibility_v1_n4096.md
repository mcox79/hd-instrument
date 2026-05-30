# Prereg: tensor_factorized_w_feasibility_v1_n4096

Date: 2026-05-30
Anchor: tensor_factorized_w_feasibility_v1_n4096
Script: experiments/exp_tensor_factorized_w_feasibility_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

W ≈ U * diag(S) * V^T via SVD at ranks [128, 256, 512, 1024, 2048]; full
rank = 4096. Does factored W at rank=512 give >= 95% of full-rank retention
at 1/4 memory (memory_ratio = 2 * 512 / 4096 = 0.25)?

## Pre-registered bands

- **HARD_PASS**: `mean_rank_512_retention_ratio >= 0.95` AND not HARD_FAIL.
- **HARD_FAIL**: in >= 60% of seeds, ALL ranks below 2048 show >= 30% loss
  from full (compression universally broken across the rank-reduction region).
- **MIDDLE_BAND**: otherwise.

## Self-tests

SVD round-trip at full rank reproduces W exactly (atol 1e-4); memory_ratio
formula (2*rank/N) verified.

## Sweep

N=4096; M=512; 5 ranks; 5 seeds.

## Timeout estimate

User specified 21600s. scaling_exp=2.0 (SVD is matrix-dominant).
