# Prereg: wave14_interp_family_rm_v1

**Date**: 2026-05-24
**Vertex**: INTERP_FAMILY_RM_PASS / KILLED / INCONCLUSIVE
**Capability target**: Cap 12 (AMP-vs-VAMP inference routing infrastructure) — optional **third-family hardening** beyond Gates A and B.
**Queue**: `remote_cpu_queue` (~30-60 min CPU)

## Background

Anchors 1 (tau-robustness) and 2 (Hadamard family) cover the two strict ✅ gates. This optional anchor extends Gate B to a fourth family: iid-Gauss → RM(1,m) interpolation, where RM(1,m) is the 2N-codeword Reed-Muller order-1 code (bipolar Hadamard rows union their negations).

## Hypothesis

The kappa_n divergence predictor extends to the RM(1,m) family; Spearman rho ≥ 0.70 and max VAMP rel-err < 0.10.

## Design

- W_alpha = ((1-alpha) * G + alpha * W_rm) / sqrt(N), where W_rm is M rows subsampled from the 2N-row bipolar RM(1,m) codebook ([H; -H]).
- alpha in {0.0, 0.25, 0.5, 0.75, 1.0}; 5 seeds per cell; N=1024, M/N=1.0.
- Per-cell metrics identical to the Hadamard anchor.

## HARD PASS (third-family hardening)

- **Spearman rho ≥ 0.70 AND max VAMP rel-err < 0.10**

## HARD FAIL (third-family hardening fails)

- **rho < 0.50 OR max VAMP rel-err > 0.20**

## MIDDLE BAND

- **rho in [0.50, 0.70) or VAMP rel-err in [0.10, 0.20)** — marginal; documents family-specific caveat.

## Formula self-tests (verified in script `--self-test`, 6/6 cases)

Same suite as the Hadamard anchor: bbmd identity, bbmd deviation, spearmanr monotone, PASS synthetic, KILLED rho, MIDDLE band, missing-cell INCONCLUSIVE.

## Honest framing

This is the weakest of the three anchors — PASS adds breadth, not depth. A KILL on RM but PASS on Hadamard still leaves Cap 12 promotable to ✅; KILL on both Hadamard AND RM deepens the family-specificity caveat. Cheap CPU budget makes it worth running while remote-CPU queue is otherwise empty.
