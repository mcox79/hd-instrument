# Prereg: wave14_interp_family_hadamard_v1

**Date**: 2026-05-24
**Vertex**: INTERP_FAMILY_HADAMARD_PASS / KILLED / INCONCLUSIVE
**Capability target**: Cap 12 (AMP-vs-VAMP inference routing infrastructure) — **Gate B** of the 🟢 → ✅ promotion pre-reg gate set.
**Queue**: `remote_cpu_queue` (~30-60 min CPU)

## Background

Cap 12 was promoted to 🟢 at cap_map v174. Gate B requires a second-family validation of the AMP-error predictor (sum |Δκ_n|) beyond the SRHT family (v174 SRHT landed Spearman rho=0.700 / max VAMP rel-err 0.0938, exactly at the pre-reg PASS thresholds).

This experiment tests the iid-Gauss → Hadamard interpolation family — structurally different from SRHT because Hadamard omits the Dudeja-Lu-Kini random-diagonal `D` and column-subsample `S`.

## Hypothesis

The free-cumulant divergence sum kappa_n predictor generalizes across the Hadamard interpolation family. Spearman rho between AMP rel-err and BBMD-distance is ≥ 0.70 across the 5-cell alpha grid; max VAMP rel-err stays < 0.10.

## Design

- W_alpha = ((1-alpha) * G + alpha * W_hadamard) / sqrt(N), where G is iid N(0,1) and W_hadamard is M rows row-subsampled from N×N Sylvester Hadamard (entries in {+1,-1}; no D, no S).
- alpha in {0.0, 0.25, 0.5, 0.75, 1.0}; 5 seeds per cell; N=1024, M/N=1.0.
- Per cell: SVD, kappa profile k_2..k_6 (free-cumulant inversion), BBMD-distance d = Σ_{n=2..6} |κ_n - M/N|, AMP-SE prediction, empirical AMP, VAMP-SE closed-form, empirical VAMP, AMP/VAMP rel-errs.
- Cell mean = mean across 5 seeds.
- Final: Spearman rho(amp_rel_err_mean, bbmd_distance_mean) across 5 cells; max(vamp_rel_err_mean) across 5 cells.

## HARD PASS (Cap 12 Gate B satisfied)

- **Spearman rho ≥ 0.70 across 5 alpha cells**
- **AND max VAMP rel-err < 0.10**

## HARD FAIL (Cap 12 Gate B fails)

- **Spearman rho < 0.50**
- **OR max VAMP rel-err > 0.20**

## MIDDLE BAND

- **rho in [0.50, 0.70) or VAMP rel-err in [0.10, 0.20)** — second-family validation marginal; Cap 12 stays at 🟢, further investigation needed.

## Formula self-tests (verified in script `--self-test`, 8/8 cases)

1. `bbmd_distance` on MP-reference (kappas == c) -> 0.
2. `bbmd_distance` on monotonically-deviating kappas -> exact sum.
3. `spearmanr` on monotonically-increasing pair -> 1.0.
4. Synthetic PASS verdict (monotone amp_rel, low max VAMP).
5. KILLED via low rho (non-monotone amp_rel).
6. KILLED via VAMP blowup.
7. MIDDLE BAND (monotone rho but VAMP in (0.10, 0.20)).
8. Too-few cells INCONCLUSIVE.

## Honest framing

PASS adds Hadamard as a THIRD validation family (Kerdock + SRHT + Hadamard); FAIL marks Hadamard as the first family where the explainer breaks, deepens the family-specificity caveat noted at v174 (the rho-drop 0.900 → 0.700 from Kerdock to SRHT is already real degradation). This is meta-tool capability validation, not substrate-physics novelty.
