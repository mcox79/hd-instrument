# Pre-reg: Wave 14 VAMP-on-Chain N-Sweep v1

**Filed:** 2026-05-22

## Question

At what N does the VAMP-on-chain advantage over argmax emerge? Sweep N ∈ {4096, 8192, 16384, 32768, 65536} at depth=50 K=100.

## Verdicts

- `N_SWEEP_CLEAN_TRANSITION` — VAMP stays ≥0.9 throughout AND argmax decays substantially.
- `N_SWEEP_DISTINCT_CLIFF` — argmax has a sharp drop at a specific N.
- `N_SWEEP_BOTH_DECAY` — both methods decay (VAMP advantage shrinks at large N).
- `N_SWEEP_INCONCLUSIVE` — unclear pattern.

## Method

For each N, run 15 chains at depth=50, K=100; compare argmax vs VAMP-on-chain.

## Config

- N_grid: [4096, 8192, 16384, 32768, 65536].
- depth=50, K=100, num_entities=200, num_relations=20.
- n_trials=15, single seed.
