# Pre-reg: Wave 14 Pseudoinverse Basin Width v1

**Filed:** 2026-05-22
**Source:** Research 15:25 F2 (basins-shrink caveat) + PINV_PASS result this cycle (20× over Hebbian at α=0.5/0.95).
**Predecessor:** `wave14_pseudoinverse_capacity_v1` = PINV_PASS.

## Question

At α ∈ {0.10, 0.30, 0.50, 0.70, 0.90}, what is the largest Hamming-perturbation radius from a stored pattern at which the pseudoinverse-W substrate still recovers the pattern via sync update?

PINV_PASS confirmed exact-fixed-point capacity at α=0.95. Research's basin-shrinkage caveat (Cherrier-Dean-Lefevre 2002) must be quantified before deployment.

## Hypothesis

H_usable: basin radius at α=0.50 ≥ 0.10 · N (substrate tolerates 10% bit-flips on perturbed query).

H_collapsed: basin radius < 0.02 · N at α=0.50 — pseudoinverse storage gain useless without exact-pattern access.

## Pre-declared verdicts

- `BASIN_USABLE` — basin radius ≥ 0.10 · N at α=0.50.
- `BASIN_NARROW` — 0.02 · N ≤ radius < 0.10 · N (research-grade only).
- `BASIN_COLLAPSED` — radius < 0.02 · N.
- `BASIN_INCONCLUSIVE` — metric collection error.

## Method

For each α:
1. Build pseudoinverse W from M = ⌈αN⌉ random ±1 patterns.
2. For each d_flip ∈ {0.01N, 0.02N, 0.05N, 0.10N, 0.20N, 0.30N}:
   - Perturb each pattern by flipping d_flip random bits.
   - Sync update for 5 iterations.
   - Count fraction recovered (overlap > 0.95).
3. Basin radius = largest d_flip where recovery ≥ 0.90.

## Acceptance thresholds

- 0.10 N = "deployment-grade" basin (matches HDC robustness convention).
- 0.02 N = "research-grade" floor.

## Config

- N=256 smoke, 1024 full.
- α_grid: [0.10, 0.30, 0.50, 0.70, 0.90] full.
- d_flip_frac_grid: [0.01, 0.02, 0.05, 0.10, 0.20, 0.30] full.

## Pre-declared interpretation

- **USABLE at α=0.50**: F2 pseudoinverse deployment-viable. Strategy promotes as capacity-extension primitive. Combine with Bet C M/N=8 to check if pseudoinverse + Kerdock = supra-AGS + deployment-grade basins.
- **NARROW**: research-grade. Useful for exact-pattern recall (deterministic store/retrieve) but not for noisy query.
- **COLLAPSED**: F2 ✓ for storage capacity but ✗ for retrieval robustness. Closes F2 deployment-viable claim.

## Not in scope

- Multi-pattern superposition recall (separate experiment).
- Stochastic update (sync deterministic only).
- Pseudoinverse + Kerdock combined (separate experiment, conditional on USABLE here).
