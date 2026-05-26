# Pre-registration: wave14_vamp_amp_universality_contrast_v1

**Date**: 2026-05-23
**Queue**: overnight_queue (GPU; SVD + VAMP/AMP iteration at N=4096, alpha up to 2)
**Axis probed**: VAMP-vs-AMP universality split on Kerdock
**Trigger**: Emergency refill 2026-05-23 19:50; Verdict 3 (KERDOCK_SPECTRUM_BULK_BOUNDED) suggests VAMP (which uses singular vectors) may hold where AMP (scalar only) fails
**Script**: experiments/exp_wave14_vamp_amp_universality_contrast_v1.py
**Peak memory**: ~2 GB GPU at N=4096 M=8192 (alpha=2)
**Expected elapsed**: ~30-45 min GPU full sweep

---

## Scientific question

The Bayati-Montanari scalar AMP-SE failed to predict empirical AMP MSE on the
substrate's Kerdock codebook (v163 AMP_SE_DIVERGES). VAMP (Rangan-Schniter-
Fletcher 2017) uses the *full* singular spectrum -- mathematically equivalent
to S-transform information -- not just the scalar mean. If the divergence is
"moment-based on the bulk" (Verdict 3), VAMP should track empirics where AMP
fails.

That gives a clean substrate-product story: "AMP fails on this codebook because
of higher kappa_n; VAMP succeeds because it uses S-transform-equivalent info."

---

## Design

- **N**: 4096
- **M/N alpha grid**: [0.5, 1.0, 2.0]
- **sigma_noise**: 0.1 (SNR ~ 100; diagnostic regime)
- **signal_var**: 1.0 (matched Gaussian prior, MMSE denoiser)
- **Seeds**: 5 per alpha
- **n_iter**: 300 (VAMP and AMP empirical)
- **VAMP-SE**: closed-form Gauss-Gauss posterior (= LMMSE) over empirical singular spectrum
- **AMP-SE**: scalar Bayati-Montanari fixed point (single iteration of scalar recursion)

Both predictions and both empirical recoveries computed on identical (A, y, x_true)
triples for matched comparison.

---

## Falsifiable predictions

### VAMP_AMP_CONTRAST_PASS (HARD PASS)

VAMP-SE within 20% of empirical VAMP in >=2/3 of cells AND AMP-SE within 20% of
empirical AMP in <=1/3 of cells. Clean substrate-product split. Deflated P = 0.45.

### VAMP_AMP_BOTH_DIVERGE (HARD FAIL of VAMP, substrate-novel even stronger story)

Both VAMP and AMP fail at >=2/3 of cells. Substrate is OUTSIDE both AMP and VAMP
universality classes. Need OAMP/generalized-VAMP for this codebook. Deflated P = 0.20.

### VAMP_AMP_BOTH_MATCH (REVERSES v163)

Both VAMP and AMP succeed at >=2/3 of cells. Contradicts v163; possible only if v163's
empirical AMP at alpha=8 was the failure mode and lower-alpha empirical AMP is in-class.
P = 0.15.

### VAMP_AMP_INCONCLUSIVE

Mixed. P = 0.20.

---

## Substrate-product interpretation

- **CONTRAST_PASS**: substrate-product story = "AMP fails, VAMP works." Architecture
  decision: any inference pipeline on the Kerdock substrate uses VAMP-style updates
  (full singular spectrum) rather than scalar AMP. Validates cap_map v127+ VAMP-on-chain
  architecture row.
- **BOTH_DIVERGE**: substrate is in a regime beyond standard VAMP universality. Suggests
  even singular-spectrum information is insufficient; OAMP with eigenvector-structure
  corrections may be required. Substrate-novel computational identity (rare).
- **BOTH_MATCH**: v163 may have been a specific-alpha effect, not a universality-class
  failure. Re-investigate v163 conditions.

---

## PROT compliance

Per [[feedback-pipeline-pacing]]: GPU-first depth probe; substantive universality test.
Follow-on to v163 AMP_SE_DIVERGES; lights up the cap_map VAMP row.
