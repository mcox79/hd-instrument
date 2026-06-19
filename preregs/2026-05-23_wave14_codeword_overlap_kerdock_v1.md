# Prereg: wave14_codeword_overlap_kerdock_v1

**Date:** 2026-05-23
**Author:** exp_dev (post-v165 CPU drill batch)
**Substrate-product axis:** substrate-physics structural-algebraic fingerprint (independent of spectral fingerprint family v164a/v165 and geometric support v_spectral_support)

## Hypothesis

The distribution of inner products <x_i, x_j>/N between random distinct Kerdock 4-coset codewords departs from Gaussian (CLT) in a measurable way. Smoke at N=1024 already shows KS=0.256 — substantially above the 0.05 Gaussian-match threshold. This is an algebraic-structural axis independent of the spectral/moment family.

## Predictions

H1: KERDOCK_OVERLAPS_NON_GAUSSIAN — ≥half of cells have KS-statistic vs Gaussian fit > 0.10. Mechanism: discrete inner-product levels (related to nonzero coset cardinalities) prevent smooth Gaussian relaxation at finite N.

H2: KERDOCK_OVERLAPS_GAUSSIAN — all cells have KS < 0.05 (rejected by smoke).

## Hard-fail thresholds

- NON_GAUSSIAN claim requires ≥2/3 of cells (over N=1024 and N=4096, 3 seeds each = 6 cells) to have KS > 0.10. Smoke already shows N=1024 KS=0.256, so the test now hinges on whether the deviation PERSISTS at N=4096 (CLT may smooth out at larger N).
- GAUSSIAN claim requires all 6 cells KS < 0.05 (refuted by smoke at N=1024 already; if N=4096 KS drops to <0.05 across all seeds, verdict becomes INCONCLUSIVE — N-scaling crossover).

## Config

- N_list = [1024, 4096]
- n_pairs = 5000 per cell
- n_seeds = 3
- Pure numpy (einsum + sort + ks). Peak memory ~150 MB at N=4096 codebook (16384 x 4096 float32 = 256 MB).
- Expected wallclock: <60 seconds

## Cap_map row impact

- NON_GAUSSIAN at both N: new substrate-physics row "Kerdock codeword inner-product NON-Gaussian" added 🟡 (paired with v164a kappa_n & v165 S-transform); third independent algebraic fingerprint axis.
- GAUSSIAN at N=4096: refutes; CLT smooths the discrete signal at larger N; small-N artifact framing.
- INCONCLUSIVE: cross-N divergence flagged for re-probe with n_pairs ≥ 50000.
