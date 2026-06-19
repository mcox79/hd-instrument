# Prereg: multi_signal_kf1_design_v1_n4096

Date: 2026-05-30
Anchor: multi_signal_kf1_design_v1_n4096
Script: experiments/exp_multi_signal_kf1_design_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

Per (operating point in [low M=128, mid M=1024, near-cap M=4096], signal in 5):
AUC for in-store vs OOS discrimination. Composite (weighted-mean across
signals) AUC across all 3 operating points: does it extend to >= 0.90?

## Five signals

1. `posterior_entropy` — `-sum P log P`; lower for in-store (negated for AUC).
2. `bundle_norm` — `||W k_query||`; higher for in-store.
3. `geometric_distance` — `max cos(c, W k_query)`; higher for in-store.
4. `spectral_signature` — `max(sim) - 2nd-max(sim)`; sharper for in-store.
5. `cross_replica` — cosine of `W1 k` vs `W2 k` under 2 replicas; higher for
   in-store (true signal stable across replicas).

## Pre-registered bands

- **HARD_PASS**: composite_wmean AUC >= 0.90 across ALL 3 operating points.
- **HARD_FAIL**: composite_wmean AUC <= 0.75 at ANY operating point.
- **MIDDLE_BAND**: otherwise.

## Sweep

- N=4096; M_ops=[128, 1024, 4096]; 5 seeds; beta=8.0.

## Timeout estimate

User specified 21600s. scaling_exp=1.5.
