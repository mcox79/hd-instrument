# Pre-reg: Wave 14 Multi-hop HMM K-Scaling v1

**Filed:** 2026-05-22
**Follow-up to:** GEOMETRIC_FALSIFIED + plateau-at-0.22 phenomenon.

## Question

Does substrate's acc_d50 plateau at ~0.22 hold across K ∈ {50, 100, 200, 500} at N=65536?

K-invariance → fundamental substrate dynamics. K-dependence → capacity-mediated.

## Verdicts
- `HMMK_INVARIANT` — acc spread < 0.10 across K.
- `HMMK_DECREASING` — monotone decline with K.
- `HMMK_INCONCLUSIVE`.

## Config
- N=65536, depth=50, K_grid=[50, 100, 200, 500].
- 30 trials, single seed.
