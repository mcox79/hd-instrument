# Pre-reg: Wave 14 Pseudoinverse + Kerdock Combo v1

**Filed:** 2026-05-22
**Source:** Synthesis of `wave14_pseudoinverse_capacity_v1` PINV_PASS (20× over Hebbian) + Bet C M/N=8 Kerdock-codebook substrate-product anchor.

## Question

At α ∈ {0.30, 0.50, 0.70, 0.90}, does pseudoinverse W with Kerdock 4-coset keys preserve basin radius better than pseudoinverse W with random ±1 keys (Personnaz-Guyon-Dreyfus 1985 baseline)?

Hypothesis: Kerdock's near-Welch-bound coherence (lower max-pairwise-overlap than random) reduces basin-shrinkage at supra-AGS α.

## Hypothesis

H_better: kerdock_basin_alpha50 / random_basin_alpha50 ≥ 2.0. Structured codebook synergizes with pseudoinverse rule to preserve robustness.

H_worse: ratio < 0.5 — Kerdock degrades pseudoinverse basins.

## Pre-declared verdicts

- `PINVK_BETTER` — kerdock basin ≥ 2× random basin at α=0.50.
- `PINVK_NEUTRAL` — 0.5× ≤ ratio < 2×.
- `PINVK_WORSE` — kerdock basin < 0.5× random.
- `PINVK_INCONCLUSIVE` — metric collection error.

## Method

For each α:
1. Build M = ⌈αN⌉ patterns: Kerdock 4-coset subset OR random ±1.
2. Compute pseudoinverse W = Ξ^T (Ξ Ξ^T)^(-1) Ξ; zero diagonal.
3. Measure basin radius via Hamming perturbation sweep (reuses `bw.measure_basin_radius`).
4. Compare ratio kerdock_basin / random_basin at α=0.50.

## Acceptance thresholds

- 2.0 BETTER threshold = "structured codebook synergy real".
- 0.5 WORSE threshold = "Kerdock actively hurts".

## Config

- N=1024 smoke, 4096 full.
- α_grid full: [0.30, 0.50, 0.70, 0.90].
- d_flip_frac_grid full: [0.01, 0.02, 0.05, 0.10, 0.20].
- n_iter=5 sync updates.

## Pre-declared interpretation

- **BETTER**: substrate-product winner — pseudoinverse + Kerdock combines F2 capacity gain (α→1) with structured robustness. Strategy promotes as Tier-1 substrate-product engineering primitive.
- **NEUTRAL**: structured codebook doesn't help pseudoinverse. Stick with either rule but not both together.
- **WORSE**: Kerdock interferes with pseudoinverse rule (perhaps via dimensional reduction in covariance — Kerdock atoms are not linearly independent in same way as IID random).

## Not in scope

- Higher α (>0.90).
- Other structured codebooks (Hadamard, Reed-Muller, Delsarte-Goethals).
- Hebbian + Kerdock control (Bet C already validated this).
