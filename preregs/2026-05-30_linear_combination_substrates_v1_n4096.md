# Prereg: linear_combination_substrates_v1_n4096

Date: 2026-05-30
Anchor: linear_combination_substrates_v1_n4096
Script: experiments/exp_linear_combination_substrates_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

Op A (msg-1 T5): linear combinations of substrates
`W_combined = sum_i alpha_i W_i`. K=3 substrates with DISJOINT key/val
pools (each stores 256 facts from non-overlapping codebook partitions).
Form W_combined under uniform and weighted alpha. Do retrievals on
W_combined return the corresponding substrate's value?

## Pre-registered bands

- **HARD_PASS**: per-substrate retrieval accuracy >= 0.85 AND
  cross-substrate interference <= 0.15 in >= 3/5 seeds for BOTH
  uniform AND weighted modes.
- **HARD_FAIL**: per-substrate accuracy <= 0.40 OR cross-substrate
  interference >= 0.50 in 3+/5 seeds for any mode.
- **MIDDLE_BAND**: otherwise.

## Sweep

- N=4096
- K_SUBSTRATES = 3 (disjoint fact pools)
- M_PER_SUBSTRATE = 256
- Modes: uniform (1/3, 1/3, 1/3) and weighted (0.6, 0.3, 0.1)
- Seeds: 5 ([7,17,23,31,41])
- Total cells: 2 modes * 5 seeds = 10

Per-substrate accuracy = fraction of queries to substrate i that
return the correct fact from W_combined.
Cross-substrate interference = fraction of queries to substrate i
that return a fact from substrate j (j != i).

## Timeout estimate

14400s (4h). 10 cells * ~10s = 100s; ample.

## Memory footprint

3 substrates at N=4096 = 3*64MB = 192MB. Keys 3*256*4096*4 = 12MB.
CB = 805MB. Total ~1GB. Well under 6GB.

## N-suffix

`_n4096` binds production N = 4096. Smoke runs at N=1024.
