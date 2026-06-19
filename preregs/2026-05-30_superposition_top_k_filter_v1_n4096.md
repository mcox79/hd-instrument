# Prereg: superposition_top_k_filter_v1_n4096

Date: 2026-05-30
Anchor: superposition_top_k_filter_v1_n4096
Script: experiments/exp_superposition_top_k_filter_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

Track A+B+C verdict_handler (commit 2a6bf84) recommended a top-K
post-decomp filter to address Op D cross-talk from superposition
single-hop decomp v1: keep only the K largest |alpha_c| values
(K = number of stored facts), zero the rest. Does this filter:
- drop `cross_talk` <= 0.10, AND
- preserve `per_component_accuracy` >= 0.90?

Across all 4 beta-patterns (P1 uniform, P2 peaked, P3 random, P4 sparse)?

## Pre-registered bands

- **HARD_PASS**: post-filter `cross_talk <= 0.10` AND
  `per_component_accuracy >= 0.90` in >= 3/5 seeds across ALL 4 patterns.
  Outcome: ship T1 P2 two-hop superposition.
- **HARD_FAIL**: in EVERY pattern, post-filter `cross_talk > 0.10` in
  3+/5 seeds (filter ineffective).
  Outcome: Op D superposition path closes definitively even with filter.
- **MIDDLE_BAND**: filter works for some patterns but not others.

## Sweep

- N=4096, K=10 stored facts
- Patterns: 4 (P1 uniform, P2 peaked, P3 random, P4 sparse) [same as v1]
- Seeds: 5 ([7,17,23,31,41])
- Total cells: 4 * 5 = 20

Pre-filter cross_talk and per-component-accuracy ALSO reported alongside
post-filter for reference / sanity.

## Timeout estimate

14400s (4h). 20 cells * ~30s = 600s; ample.

## N-suffix

`_n4096` binds production N = 4096. Smoke runs at N=1024.
