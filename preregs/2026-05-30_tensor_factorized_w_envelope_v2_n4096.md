# Prereg: tensor_factorized_w_envelope_v2_n4096

Date: 2026-05-30
Anchor: tensor_factorized_w_envelope_v2_n4096
Script: experiments/exp_tensor_factorized_w_envelope_v2_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

v1 (commit 75c565d) shipped at single M=512 and HP-passed (TF_HARD_PASS)
but cap_map v283 flagged sub-capacity caveat. v2 sweeps both M (3 points)
and rank (5 points) to confirm low-rank factorization survives across
the broader M-envelope.

## Pre-registered bands

Per (M, rank, seed) cell: `retention_ratio = ret_factored / ret_full`.

- **HARD_PASS**: rank in {128, 256, 512, 1024} preserves
  `retention_ratio >= 0.95` at ALL 3 M values in >= 3/5 seeds.
- **HARD_FAIL**: any rank loses `retention_ratio <= 0.70` at top M
  (M=8192) in 3+/5 seeds.
- **MIDDLE_BAND**: otherwise.

## Sweep

- N=4096
- M cells: [512, 2048, 8192] (3)
- Rank cells: [128, 256, 512, 1024, 2048] (5)
- Seeds: 5 ([7,17,23,31,41])
- Total cell-seeds: 3 x 5 x 5 = 75

## Timeout estimate

User-authorized 21600s (6h). scaling_exp=2.0 (SVD-dominant); 75 cells *
~30s = ~2250s headroom.

## Memory footprint

At M=8192, N=4096: keys=134MB, W=64MB, CB=805MB, SVD peak ~200MB.
Total ~1.2GB. Within 6GB cap.

## N-suffix

`_n4096` binds production N = 4096. Smoke runs at N=1024.
