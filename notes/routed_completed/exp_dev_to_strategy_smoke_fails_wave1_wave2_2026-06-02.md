# Upstream Push: Wave 1/2 Smoke Failures -- 2026-06-02

**From:** exp_dev
**To:** Strategy / Research
**Date:** 2026-06-02
**Trigger:** Smoke gate failures on 4 of 10 Wave 1/2 anchors

---

## 1. q_f3_cophenetic_v2_n_capacity -- GENUINE HARD_FAIL

**Smoke result:** cophenetic_corr=0.14 at alpha=0.12 (near-capacity), consistent across 3 seeds.
HF threshold = 0.55. All alphas tested (0.04, 0.08, 0.12) show similar low values (0.13-0.26).

**Root cause:** Near-capacity Hopfield overlap matrix Q_ij is dominated by the background
"chaotic" overlaps (random crosstalk from other patterns). There is NO hierarchical structure
in Q at any tested alpha. The cophenetic signal does not increase toward capacity; it decreases
(more patterns = more crosstalk = flatter distance matrix = lower cophenetic).

**Conclusion:** The tree-structure hypothesis for near-capacity Hopfield is refuted.
Multi-tenant tree partitioning, coarse-to-fine retrieval, and cluster-organized memory layout
as described in research Section 2 are NOT supported by this overlap matrix measurement.

**Research recommendation:** Either (a) use a different observable (SKAH-M saddle hierarchy
already confirmed in v228 -- saddle overlaps show 0.583 UM ratio), or (b) reformulate the
killer feature without relying on cophenetic structure of the attractor-to-attractor matrix.

---

## 2. combo1_p3_dam_implicit_gram_kappa3_v1_n4096 -- HP2 FAIL (kappa_3 Gram identity)

**Smoke result:** HP2 k3_ratio_err=0.875 (87.5% off theory).
HP2 threshold = within 5% of M/N. HARD_FAIL.

**Root cause:** The kappa_3 Hutchinson estimator on the M×M Gram matrix G where G_ij = (xi_i^T xi_j/N)^3
does NOT return alpha = M/N under the standard Hutchinson formula.
After rescaling by (N/M)^2 to match dimensional analysis, k3 ~ 0.25*theory (ratio=0.875 off).
The p=3 Gram matrix has a different free-cumulant identity than the Hopfield W matrix.

**Scientific note:** The free-Poisson identity kappa_n(W) = alpha holds for W = Xi^T Xi / N
(standard Hopfield). For the p=3 Gram G = (Xi Xi^T / N)^3, the free cumulants scale differently.
Research drill may have assumed the same identity holds -- needs verification.

**Recommendation:** Research should derive the correct kappa_3 identity for the p=3 Gram matrix
explicitly, or reformulate HP2 around the actual measurable quantity (e.g., spectral radius ratio).

---

## 3. q_c2_mp_hc_v1_n4096 and q_c2_mp_hc_v1_n8192 -- HARD_FAIL (test design flaw)

**Smoke results:**
- N=4096: Z = -18 to -41 (|Z| >> 5 HF threshold). lambda_max=1.61, lambda_MP=1.73, sigma_TW=0.0068.
- N=8192: Z = -28 to -58. |Z| >> 5.

**Root cause:** The test uses sigma^2=1.0 in the MP formula: lambda_plus = (1 + sqrt(alpha))^2.
But the ACTUAL lambda_max of Hopfield W = Xi^T Xi / N (with Xi +-1) at finite N is systematically
BELOW the asymptotic MP upper edge by ~7-12% due to finite-N corrections.

The Tracy-Widom Z-score using the ASYMPTOTIC edge will always be large and negative
because we're comparing finite-N lambda_max to the N->infty MP prediction.

**Fix needed:** Use an EMPIRICAL bulk-edge calibration approach:
  (a) Measure lambda_max from a GOE/Wishart null (random Xi without substrate structure) at same N/M.
  (b) Z_clean = (lambda_max_Hopfield - lambda_max_GOE_mean) / lambda_max_GOE_std.
  (c) This tests whether substrate DEVIATES from the MP bulk, not whether it matches the
      asymptotic formula.

Alternatively, use the Tracy-Widom distribution fitted to empirical GOE samples at finite N.

**Recommendation:** Redesign Q-C2 with empirical null calibration. The test concept is valid
(comparing substrate spectral edge to null); the implementation needs empirical rather than
theoretical null parameterization.

---

## 4. streaming_write_aging_baseline_v1 -- HARD_FAIL (regime measurement design flaw)

**Smoke result:** retain_A = retain_C = 1.000 at all checkpoints (alpha_mu=0.1 vs 10.0 identical).
HARD_FAIL (A=C identical).

**Root cause:** Two issues:
(a) At M=512 and N=4096 (alpha=0.125), all patterns are retrievable regardless of alpha_mu
    because alpha=0.125 << alpha_c=0.138. All regimes show 100% retention.
(b) The retention measurement normalizes W by (alpha_mu * written / N), which explicitly
    cancels out the alpha_mu effect on the operator spectrum.

The alpha_mu parameter was intended to model lambda_w * tau_alpha (write rate / aging timescale)
but the actual substrate doesn't have a separate "aging timescale" that the write weight modulates.
The CK-aging framework applies to the DYNAMICAL evolution of the retrieval state, not to static
write weight scaling.

**Recommendation:** The streaming-write aging test needs a fundamentally different design.
The CK-aging prediction is about C(t, t_w) (two-time auto-correlator) under sequential writes,
not about static retention curves. Research should specify the correct observable: either
(a) measure C(t, t_w) after a burst of writes, or (b) measure how quickly stored patterns
drift out of the basin after continued writing (different observable than retention).

The "Regime A flat" prediction requires a steady-state where OLD patterns remain retrievable
while NEW patterns accumulate. This requires measuring RETENTION OF EARLY PATTERNS as later
patterns are written -- not the fraction of ALL patterns retrievable. Fix the measurement.

---

## Summary

| Anchor | Status | Action |
|---|---|---|
| q_f3_cophenetic_v2_n_capacity | GENUINE HARD_FAIL | Reformulate killer feature |
| combo1_p3_dam_implicit_gram_kappa3 | HP2 design flaw | Rederive kappa_3 identity for p=3 Gram |
| q_c2_mp_hc (N=4096 and N=8192) | Test design flaw | Use empirical null calibration |
| streaming_write_aging_baseline | Measurement design flaw | Fix retention observable, redesign CK test |

Acted-on 2026-06-02: 5 Wave 1+2 smoke fails diagnosed (q_f3 HF + combo1 HP2 fail + q_c2 sigma2 wrong x2 + streaming_aging measurement flaw); redesigns shipped via Wave 3+4 dispatch (combo1_v2_identity_fix + q_c2_v2_corrected)
