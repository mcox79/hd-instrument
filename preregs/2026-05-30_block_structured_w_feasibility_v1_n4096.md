# Prereg: block_structured_w_feasibility_v1_n4096

Date: 2026-05-30
Anchor: block_structured_w_feasibility_v1_n4096
Script: experiments/exp_block_structured_w_feasibility_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

W as 4 logical domain blocks (N/D = 1024 each). W_dd diagonal blocks store
128 facts per domain; W_ij off-diagonal blocks (zeroed by default) test
cross-domain rank-1 updates via 30 cross-domain pairs. Memory savings:
keep D=4 blocks of (N/D)^2 each = N^2/D = 4x savings vs flat W (N^2).

## Pre-registered bands

- **HARD_PASS**: within_ret >= 0.90 AND cross_ret >= 0.70 AND memory_savings >= 4x.
- **HARD_FAIL**: within_ret <= 0.70 OR cross_ret <= 0.70 (i.e. >= 30% loss).
- **MIDDLE_BAND**: otherwise.

## Sweep

N=4096; D=4 domains; 128 facts/domain (512 within-domain); 30 cross-domain
pairs; 5 seeds.

## Timeout estimate

User specified 21600s. scaling_exp=1.5.
