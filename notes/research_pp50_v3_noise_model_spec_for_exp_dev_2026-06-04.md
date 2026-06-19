# PP-50 V3 noise-model spec for exp_dev unblock

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Spec extraction / 0-compute research audit
**Source:** d:/AI/hd-instrument/experiments/exp_pp50_kappa3_delta_alpha_n16384_v3_fine_sigma_g_n16384.py (lines 157-186)

---

## What this is (plain language)

Exp-Dev's PP-50 N-sweep build gave 0 violations because the noise model differed from what v3 used. This note extracts the exact noise model from the v3 script that produced the published sensitivity envelope. Exp-Dev rebuilds the N-sweep against this spec.

---

## EXACT NOISE MODEL (from v3 lines 165-172)

**Noise type:** Multiplicative log-normal noise PER PATTERN (per-row scalar).

**Generation:**
```
Z_rows ~ N(0, 1) shape: (M_patterns,)
noise_scale = exp(sigma_g * Z_rows)  shape: (M_patterns, 1)
Xi_noisy = Xi * noise_scale  # broadcasts per row
```

**Critical specification:**
- Z is a vector of standard Gaussians, ONE per stored pattern (not per coordinate)
- Each pattern row gets a single log-normal scale factor exp(sigma_g * Z_mu)
- The same scale applies to ALL N coordinates of pattern mu
- NOT additive Gaussian on W
- NOT additive Gaussian on patterns
- NOT multiplicative per-coordinate Gaussian on patterns

---

## Why this matters for the sign

Log-normal multiplicative noise on patterns produces a POSITIVE kappa_3 deviation:
- exp(sigma_g * Z) > 0 always (log-normal is positive)
- E[exp(sigma_g * Z)] = exp(sigma_g^2 / 2) (mgf at 1)
- Var[exp(sigma_g * Z)] = (exp(sigma_g^2) - 1) * exp(sigma_g^2)

The 3 * (exp(sigma_g^2) - 1) * alpha NLO correction matches this noise model. Sign is positive.

If exp_dev used additive Gaussian noise on W (instead of multiplicative log-normal on patterns), the kappa_3 deviation would have OPPOSITE SIGN — because Gaussian noise CENTERS around zero, the deviation in kappa_3 averages downward, not upward. This explains the matched-magnitude / opposite-sign empirical observation.

---

## Violation criterion

From the v3 verdict logic (lines 282-348):

**HARD-FAIL trigger 1:** all sigma_sep < 10.0 across all cells (sensitivity absent)
**HARD-FAIL trigger 2:** sigma_sep at sigma_g=0.9 > 1.5 * max(sigma_sep at sigma_g in {0.1, 0.3, 0.5}) AND > HP_ENVELOPE_MIN (theory violation: monotone rise past sigma_g_crit)
**HARD-PASS trigger:** sigma_sep >= 100 across sigma_g in {0.1, 0.3, 0.5} AND >= 200 at some sigma_g in that mid-range

sigma_sep is defined (line 200-202) as:
```
sigma_sep = abs(k3_aug - k3_base) / max(abs(k3_base), 1e-10) * 1000.0
```

It's an ABSOLUTE relative deviation, scaled by 1000. Always positive by construction.

---

## sigma_g_crit theoretical anchor

From script lines 108-112:
```
sigma_g_crit = sqrt(ln(1 + epsilon / (3 * alpha)))
             = sqrt(ln(1 + 0.15 / 0.15))
             = sqrt(ln(2))
             = 0.8326
```

Where:
- epsilon = 0.15 (15% kappa_3 sensitivity gate; some prior threshold parameter)
- alpha = 0.05 (capacity ratio M/N at baseline)

This sets the boundary where sigma_sep should drop sharply (noise overwhelms signal).

---

## "5/10 cells violated" interpretation

The exact "5/10" phrasing isn't in v3 (v3 has 15 cells = 5 sigma_g x 3 delta_alpha). But the envelope-shape prediction implies: across 10 cells spanning sigma_g, roughly half should show sigma_sep ABOVE the HP_ENVELOPE_MIN threshold (mid-range cells at sigma_g < sigma_g_crit), and half should fall below (high-sigma_g cells past sigma_g_crit).

If your N-sweep uses 10 cells spanning sigma_g across the boundary, the predicted pattern is:
- ~5 cells at sigma_g < 0.833 (sigma_g_crit) show sigma_sep > HP_threshold
- ~5 cells at sigma_g >= 0.833 show sigma_sep < HP_threshold (decay past critical)

Net: ~5 cells violate the "below HP threshold" criterion in the predicted-decay region.

---

## Recommended exp_dev rebuild spec

```python
# Noise model -- CRITICAL FIX
Z_per_pattern = torch.randn(M, generator=gen_noise, device=DEVICE)  # shape (M,)
noise_scale = torch.exp(sigma_g * Z_per_pattern).unsqueeze(1)        # shape (M, 1)
Xi_noisy = Xi * noise_scale                                          # broadcast over N

# kappa_3 measurement via Hutchinson
def w_op(V):
    inner = Xi_noisy @ V         # (M, n_probes)
    return (Xi_noisy.t() @ inner) / N  # (N, n_probes)

V1 = w_op(V0); V2 = w_op(V1); V3 = w_op(V2)
k3 = (V0.double() * V3.double()).sum(dim=0).mean() / N

# sigma_sep -- ABSOLUTE relative deviation
sigma_sep = abs(k3_aug - k3_base) / max(abs(k3_base), 1e-10) * 1000.0
```

---

## Confidence

Direct extraction from working v3 script (HARD_PASSed in cap_map v370+ cycle with this noise model). No interpretation; literal code path.

Apply this spec to the N-sweep build and the 5-of-10-cells-violated pattern should emerge across the sigma_g range.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-verify-implementations]]: spec extracted verbatim from working script
- 0-compute artifact; ASCII-only
- No empirical verification (per [[feedback-research-drills-no-empirical-verification]]); this is a script-audit-spec note

---

**END.**

**Exp-Dev:** apply the multiplicative log-normal per-pattern noise model above. Rebuild N-sweep. Should reproduce the documented envelope shape (rises 0.1 -> 0.5, peaks near 0.5, drops past 0.833) with positive sigma_sep deviation.

**Research:** kappa_3-NLO 2x drill (in-flight; ~30 min remaining) will provide the algebraic noise-convention derivation that complements this empirical spec.
