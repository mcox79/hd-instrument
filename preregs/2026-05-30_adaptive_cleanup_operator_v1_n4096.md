# Prereg: adaptive_cleanup_operator_v1_n4096

Date: 2026-05-30
Anchor: adaptive_cleanup_operator_v1_n4096
Script: experiments/exp_adaptive_cleanup_operator_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

Sweep cleanup-operator strength `alpha` in [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0]
at M_frac=2. Does adaptive cleanup yield >= 5% retention improvement over
standard (alpha=1.0)?

Cleanup operator (formula self-tested):
  `out = alpha * cand + (1 - alpha) * raw`
where `cand = top-1 codeword from sim(c, W @ k)` and `raw = W @ k`.

## Pre-registered bands

- **HARD_PASS**: optimal alpha != 1.0 AND `retention(best_alpha) - retention(1.0)`
  >= 0.05 in >= 3 of 5 seeds.
- **HARD_FAIL**: alpha=1.0 optimal in >= 4 of 5 seeds (no adaptive gain).
- **MIDDLE_BAND**: otherwise.

## Sweep

- N=4096; M_frac=2 -> M=8192; 7 alpha values * 5 seeds.

## Timeout estimate

User specified 14400s. scaling_exp=1.5.
