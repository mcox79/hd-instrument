# exp_dev -> Strategy: PP-50 sigma_g v3 audit design issue

**Date:** 2026-06-03
**Routing from:** exp_dev (v364 refill cycle)

## Summary

PP-50 sigma_g v3 audit (candidate F from v364 refill prompt) cannot be shipped as designed.
The v3 pre-reg assumed kappa_3 holds through sigma_g=0.50 based on cap_map annotation, but
v2 FULL data contradicts this assumption.

## v2 FULL findings (already on file)

v2 verdict: HARD_FAIL
v2 verdict_msg: "HARD_FAIL: regression -- kappa3 breaks before sigma_g=0.30 (v1 boundary).
  sg0.01:r=1.150 sg0.10:r=1.169 sg0.20:r=1.223 sg0.30:r=1.319 sg0.40:r=1.464
  sg0.50:r=1.677 sg0.60:r=1.985 sg0.70:r=2.414 sg0.80:r=3.054 sg1.00:r=5.343
  sg1.20:r=11.053 n_seeds=5 N=4096"

Key observation: ratio at sg=0.01 is 1.150 (already 15% above 1.0 -- barely outside HOLD_FRAC=0.05).
ALL sigma_g values in [0.01, 1.20] show ratio > 1.0. This suggests systematic INFLATION of tr(W^3)
by multiplicative log-normal noise at ALL sigma_g levels, not a critical-point transition.

Multi-scale smoke (N=512 and N=2048) both confirm: ratio >= 1.68 at sg=0.50. N-independent.

## Why the v3 design is wrong

The v3 pre-reg assumed holding through sg=0.50 because:
- v1 finding "kappa_3 holds through sg=0.30" meant kappa_3 was measurably non-zero
- But v1 used HOLD_FRAC=0.05 (ratio within +-5%), so if sg=0.01 gives ratio=1.150, v1 would
  have triggered HARD_FAIL for the regression criterion, not "holds"

The sigma_g_crit=0.833 annotation appears to have come from a theoretical prediction,
not empirical measurement. The RETRACTION means: empirical data does not support sigma_g_crit=0.833.

## Recommended redesign

Strategy should determine:
1. What did v1 actually measure? Was sigma_g_crit in v1 evaluated differently (e.g., different
   M/N ratio, different noise model, or different HOLD_FRAC)?
2. Is the kappa_3 audit primitive actually sensitive to sigma_g=0.01 log-normal noise at N=4096?
   If ratio=1.15 at sg=0.01 is real, then PP-50 noise robustness is much weaker than claimed.
3. If systematic inflation is real: reframe the experiment to measure the INFLATION CURVE
   (ratio as function of sigma_g) rather than testing a hold/break threshold.
4. Possible v3 redesign: compare kappa_3 RELATIVE deviation (ratio - 1.0) to a sigma_g-dependent
   theoretical prediction (expected inflation from log-normal multiplicative noise model).
   Then HARD_PASS = measured ratio matches theoretical inflation to within +-10%.

## Impact

- PP-50 sigma_g noise-robustness annotation: may need significant downgrade if all sigma_g
  values show ratio >> 1 (systematic inflation, not robust identity preservation).
- This does NOT invalidate the delta_alpha discriminability axis (separate metric).
- PP-50 product story (kappa_3 audit under realistic noise) needs honest reframing.
