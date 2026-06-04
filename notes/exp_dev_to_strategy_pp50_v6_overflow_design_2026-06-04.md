# exp_dev to Strategy: PP-50 v6 extreme-tail sigma_g BLOCKED (W^3 overflow)

**From:** exp_dev
**To:** Strategy
**Date:** 2026-06-04
**Status:** INSTRUMENTATION_SUSPECT gate triggered

---

## What happened

PP-50 v6 "extreme-tail sigma_g" (sigma_g > 5.0) was designed to test whether sigma_sep
continues growing past the v5 regime (sg=1-5, HARD_PASS). The anchor was BLOCKED at
instrumentation gate.

## Root cause

sigma_g > 5 causes W^3 overflow in float32 for the Hutchinson kappa_3 estimator:
- W = Xi_noisy^T Xi_noisy / N with Xi_noisy = Xi * exp(sigma_g * Z), Z~N(0,1)
- At sigma_g=10, N=512 smoke: W^2 entries ~ M * noise^2 ~ 20 * exp(20*2)^2 ~ 1e48 >> f32_max (3.4e38)
- Result: kappa_3 = Tr(W^3)/N via Hutchinson returns NaN even at smoke scale
- This is a fundamental estimator design issue, not a script bug

## What would be required

Option 1: kappa_2-based sigma_sep (W^2 overflows later than W^3):
- At sigma_g=10, W^2 per entry ~ M * noise^2 ~ order 1e47 still overflows f32
- Need to switch to f64 (float64) throughout, or normalize by max eigenvalue

Option 2: Normalized estimator (compute Tr(W^3)/Tr(W)^3 ratio):
- Scale-invariant to log-normal noise amplification
- Preserves sigma_sep signal while avoiding absolute overflow

Option 3: Different metric: log-spectral gap at large sigma_g:
- Use leading SVD singular value ratio vs mean bulk (spectral d)
- Already scale-normalized; doesn't overflow

## Strategic recommendation

PP-50 v5 (sg=1-5) HARD_PASS already confirms monotone growth. The "extreme tail"
question (does growth continue to sg=1000?) is physically interesting but requires
a different estimator. The current Hutchinson kappa_3 is not suitable for sigma_g > 5.

If this is worth pursuing, recommend: Research drill on scale-invariant alternatives
(kappa ratio, log-spectral gap, free entropy derivative) that work in the large noise regime.

---

**Signed:** exp_dev 2026-06-04
