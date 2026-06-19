# Prereg: continuous_output_substrate_v1_n4096

Date: 2026-05-30
Anchor: continuous_output_substrate_v1_n4096
Script: experiments/exp_continuous_output_substrate_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

Does substrate's CONTINUOUS output `W @ k_query` (no argmax) support:
- geometric interpolation at the midpoint of two stored keys?
- hallucination signal via softmax-shape (max - mean)?
- argmax consistency at stored keys?
- KF-2 edit isolation under continuous reads?

## Pre-registered bands (composite)

- **HARD_PASS**:
  - `interp_cosine >= 0.7`
  - `hallu_signal_AUC >= 0.85`
  - `argmax_consistency >= 0.95`
  - `KF-2 max_iso <= 0.10`
- **HARD_FAIL**: `interp_cosine <= 0.3` OR `argmax_consistency <= 0.5`
- **MIDDLE_BAND**: otherwise

## Sweep

- N=4096, M=512, 5 seeds, beta=8.0
- Interp pairs: 64; hallu probes: 200 in-store + 200 OOS; KF-2 edits: 16

## Timeout estimate

User specified 21600s (6h); honor. scaling_exp=1.5.
