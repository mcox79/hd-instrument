# Pre-reg: Wave 14 Lane D Noise Robustness v1

**Filed:** 2026-05-22
**Bet:** Lane D adversarial robustness (extends end-to-end PASS)
**Predecessor:** `wave14_lane_D_end_to_end_v1` (composed_acc=1.000 on clean obs)

## Question

Does the Lane D end-to-end pipeline (Bet U → S → T → X) survive realistic Hamming-flipped observations? At 10% bit-flip per observation, does composed_acc stay ≥ 0.50?

## Hypothesis

H_robust: composed_acc(p_flip=0.10) ≥ 0.50. HDC substrate is known-tolerant to ~30% bit-flips on individual atoms (sub-Gaussian concentration), so 10% per-observation noise should survive bundle quantization.

H_brittle: composed_acc drops below 0.50 at 10% noise. Pipeline-compounded errors interact with noise to break composition.

## Pre-declared verdicts

- `NOISE_ROBUST` — composed_acc(10%) ≥ 0.50.
- `NOISE_BRITTLE` — composed_acc(0%) ≥ 0.50 AND composed_acc(10%) < 0.50.
- `NOISE_BROKEN` — composed_acc(0%) < 0.50 (regression).
- `NOISE_INCONCLUSIVE` — metric collection error.

## Method

- For each noise rate p ∈ {0.0, 0.05, 0.10, 0.20, 0.30}:
  - Run end-to-end pipeline as in `lane_D_end_to_end_v1` but flip each input triple's bits at rate p before EMA accumulation.
- composed_acc = fraction of trials where ALL 4 stages decode correctly (S ∧ T ∧ X).
- Per-noise: 3 seeds × 80 trials = 240 trials.

## Acceptance thresholds

- 0.50 threshold for ROBUST matches Lane D end-to-end PASS gate.
- 10% is the canonical realistic-noise rate for deployment-grade HDC substrates.

## Config

- N=4096 full.
- K=3, F=10 facts per hyp, skill_len=4, alphabet=5.
- noise_levels full: [0.0, 0.05, 0.10, 0.20, 0.30].
- seeds full: [17, 23, 31].
- Smoke: noise_levels=[0.0, 0.10], single seed, N=1024.

## Pre-declared interpretation

- **ROBUST**: substrate-product Lane D demo can claim deployment-grade noise tolerance. Strategy substrate-product story strengthens.
- **BRITTLE**: pipeline doesn't survive realistic noise. Investigate which stage degrades first.
- **BROKEN**: regression. Audit end-to-end script for divergence.

## Not in scope

- Per-stage-only noise (only observation-level noise; codebook atoms stay clean).
- Adversarial noise (worst-case flip selection). Random uniform only.
- Higher noise rates (>30%).
