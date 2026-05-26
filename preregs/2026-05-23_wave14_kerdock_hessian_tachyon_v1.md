# Prereg: wave14_kerdock_hessian_tachyon_v1

**Date:** 2026-05-23
**Author:** exp_dev (post-v165 CPU drill batch)
**Substrate-product axis:** substrate-physics kernel-dimension fingerprint (orthogonal to spectral/moment/structural overlap fingerprints)

## Hypothesis

The Kerdock Hessian W = (1/N) A^T A may have EXCESS zero eigenvalues beyond the rank-deficiency floor max(0, 1 - 1/alpha) expected for a generic M x N matrix. Excess zero modes = additional algebraic constraints from the Kerdock 4-coset structure → substrate-novel kernel dimension.

## Predictions

H1: HAS_EXCESS_ZERO_MODES — fraction of empirical eigenvalues below ε=1e-6 exceeds rank-deficiency floor by >5% in ≥half of cells. Mechanism: nontrivial code-theoretic intersections produce flat directions beyond generic rank.

H2: NO_EXCESS_ZERO_MODES — empirical zero-fraction matches rank-deficiency floor to within 1% across all cells (smoke at N=1024 alpha=1 shows 0.001 excess, i.e. supports H2).

## Hard-fail thresholds

- HAS_EXCESS_ZERO_MODES claim requires excess > 0.05 in ≥2/3 of cells (3 alphas × 3 seeds = 9 cells).
- NO_EXCESS_ZERO_MODES claim requires excess < 0.01 in ALL 9 cells.

## Config

- N = 1024
- alphas = [0.5, 1.0, 2.0]
- n_seeds = 3
- eps = 1e-6 (zero-eigenvalue threshold)
- Pure numpy.linalg.eigvalsh on 1024×1024 PSD matrices. Peak memory ~30 MB.
- Expected wallclock: <60 seconds

## Cap_map row impact

- HAS_EXCESS_ZERO_MODES: new substrate-physics row "Kerdock kernel-dimension excess" added 🟡 — substrate has additional flat directions beyond rank; reframes capacity story.
- NO_EXCESS_ZERO_MODES: closes the kernel-axis question; documents that the substrate-novel signature is moment/structural, NOT kernel-dimensional. Sharpens the claim.
