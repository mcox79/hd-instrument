# Prereg: interference_patterns_commutator_v1_n4096

Date: 2026-05-30
Anchor: interference_patterns_commutator_v1_n4096
Script: experiments/exp_interference_patterns_commutator_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

Op F (msg-1 T7): substrate matrix products and commutators. For two
substrates W_A and W_B, does the COMMUTATOR
`[W_A, W_B] = W_A W_B - W_B W_A` carry an information-theoretic
signature that distinguishes:

- (a) Independent: W_A, W_B store disjoint facts
- (b) Related: 50% overlap of (key, val) pairs
- (c) Contradictory: same keys, different values

Normalized magnitude `c = ||[W_A, W_B]||_F / (||W_A||_F * ||W_B||_F)`.

## Pre-registered bands

- **HARD_PASS**: max(mean(c)) / min(mean(c)) across (a)/(b)/(c) >= 2.0,
  AND span_pct > 0.20 (conditions separated by more than the noise floor).
- **HARD_FAIL**: span_pct <= 0.20 (conditions within +/- 20% of each
  other; no separation signal).
- **MIDDLE_BAND**: partial separation.

## Sweep

- N=4096, M=256 facts per substrate
- 3 conditions: independent, related, contradictory
- Seeds: 5 ([7,17,23,31,41])
- Total cells: 3 * 5 = 15

Self-commutator [W_A, W_A] = 0 sanity check reported per cell.

## Timeout estimate

14400s (4h). 15 cells * ~10s = 150s; ample.

## Memory footprint

N=4096: 2 W matrices = 128MB. CB 805MB. Keys/vals 16MB. Matmul peak
~70MB. Total ~1GB. OK.

## N-suffix

`_n4096` binds production N = 4096. Smoke runs at N=1024.
