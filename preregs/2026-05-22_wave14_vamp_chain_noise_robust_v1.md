# Pre-reg: Wave 14 VAMP-on-Chain Noise Robustness v1

**Filed:** 2026-05-22
**Source:** Strategy cycle 127 VAMPCHAIN_RESTORES PERFECT. Test deployment-grade noise tolerance for Demo 1 substrate-product story.

## Question

At N=65536, K=100, d=50, does VAMP-on-chain sustain acc ≥ 0.50 with Hamming bit-flips at rate p=0.10 injected into the factbase M?

## Hypothesis

H_robust: acc(p=0.10) ≥ 0.50 — VAMP-on-chain tolerates realistic noise.

H_brittle: acc(p=0.10) < 0.50 while acc(p=0.0) ≥ 0.50 — PERFECT result only at clean substrate.

## Pre-declared verdicts

- `VAMPNOISE_ROBUST` — acc(p=0.10) ≥ 0.50.
- `VAMPNOISE_BRITTLE` — acc(p=0.0) ≥ 0.50 AND acc(p=0.10) < 0.50.
- `VAMPNOISE_BROKEN` — acc(p=0.0) < 0.50 (regression).
- `VAMPNOISE_INCONCLUSIVE` — metric collection error.

## Method

For each p ∈ {0.0, 0.05, 0.10, 0.20, 0.30}:
- Build factbase M as usual.
- Inject random bit-flips into M at rate p (Bernoulli per bit).
- Run VAMP-on-chain with noisy M.
- 15 trials × 2 seeds.

## Acceptance thresholds

- 0.50 PASS matches existing multi-hop rehab threshold.
- 0.10 noise rate is canonical deployment-noise level for HDC substrates.

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- depth=50 full (25 smoke).
- noise_levels full: [0.0, 0.05, 0.10, 0.20, 0.30].
- n_trials=15, 2 seeds.

## Pre-declared interpretation

- **ROBUST**: VAMP-on-chain Demo 1 deployment-grade. Substrate-product Demo 1 positions as robust deep-chain memory.
- **BRITTLE**: PERFECT only at clean substrate. Demo 1 positioning needs honest-bound caveats.
- **BROKEN**: regression from cycle 127. Audit code for divergence.

## Not in scope

- Noise injection into query state (only factbase).
- Per-hop adversarial selection of bit positions (random uniform only).
- Combined K-stress + noise (separate experiment if needed).
