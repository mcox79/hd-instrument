# Prereg: sparse_w_active_subspace_envelope_v2_n4096

Date: 2026-05-30
Anchor: sparse_w_active_subspace_envelope_v2_n4096
Script: experiments/exp_sparse_w_active_subspace_envelope_v2_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

v1 (commit 75c565d) HP-passed at M sweep [32..1024] with SP_HARD_PASS,
but cap_map v283 flagged sub-capacity caveat: the test capped at M=1024
(= N/4), with substrate envelope likely extending up to M_c (estimated
16K-20K). v2 extends the M-sweep to confirm sparse-W viability across
the full operating envelope.

## Pre-registered bands

- **HARD_PASS**: sparse W maintains retention >= 0.95 at ALL M tested
  in >= 3/5 seeds, AND at least one M-cell yields mem_ratio <= 0.5
  (sparse <= half dense memory).
- **HARD_FAIL**: sparse loses >= 20% accuracy at any M >= 1024 in 3+/5 seeds.
- **MIDDLE_BAND**: otherwise.

## Sweep

- N=4096, beta=8.0
- M cells: [128, 512, 1024, 2048, 4096, 8192] (6)
- Seeds: 5 ([7,17,23,31,41])
- Total cells: 30

Note: at M > N/2 = 2048 sparse storage EXCEEDS dense; the memory-savings
clause is satisfied by the smaller-M cells where mem_ratio <= 0.5.
Retention check applies at all M.

## Timeout estimate

14400s (4h). 30 cells * ~30s avg = 900s. Ample headroom.

## N-suffix

`_n4096` binds production N = 4096. Smoke runs at N=1024.
