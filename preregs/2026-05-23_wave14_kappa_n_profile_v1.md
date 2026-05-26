# Pre-registration: wave14_kappa_n_profile_v1

**Date**: 2026-05-23
**Queue**: overnight_queue (GPU; SVD of (M x N) Kerdock matrix at N=4096, alpha up to 4)
**Axis probed**: Higher free cumulants kappa_n (n=2..8) growth pattern in n
**Trigger**: Emergency refill batch 2026-05-23 19:50; Verdicts 2 (KERDOCK_OVERLAPS_NON_GAUSSIAN) + 3 (KERDOCK_SPECTRUM_BULK_BOUNDED) sharpen the next-probe target as "moment-based deviation"
**Script**: experiments/exp_wave14_kappa_n_profile_v1.py
**Peak memory**: ~1.5 GB GPU at N=4096 M=16384 (alpha=4)
**Expected elapsed**: ~30-45 min GPU full sweep

---

## Scientific question

The substrate's Kerdock 4-coset codebook deviates from MP at low free cumulants
(kappa_1..kappa_4, established by Verdict 2 / wave14_free_cumulants_kerdock_v1).
Verdict 3 sharpens this: the deviation is "moment-based on the bulk" only --
the spectrum stays inside MP support, but its higher moments differ. Does the
substrate-MP deviation `delta_n = kappa_n_empirical / c - 1` (c = M/N):

  (a) GROW with n through n=8 -- substrate signature dominates at high moments
  (b) DECAY toward MP -- only low-order cumulants carry the algebraic signature
  (c) SATURATE at a constant offset -- "kappa shift" of all orders

Method: compute empirical spectral moments m_1..m_8, invert via the non-crossing
partition Mobius recursion (Nica-Speicher) to get kappa_1..kappa_8. Marchenko-
Pastur reference has kappa_n = c for all n.

---

## Design

- **N**: 4096
- **M/N alpha grid**: [0.5, 1.0, 2.0, 4.0]
- **Seeds**: 5 per alpha (independent Kerdock subsampling)
- **n_max_moment**: 8
- **Device**: GPU SVD via `torch.linalg.svd`; falls back to CPU if unavailable

Cumulant inversion uses the exact Mobius recursion on the non-crossing partition
lattice. Self-test verifies (1) NCP counts = Catalan numbers up through n=8,
(2) closed form matches general inversion for n<=4, (3) MP(c) gives all kappa_n = c
exactly for n=1..8.

---

## Falsifiable predictions

### KAPPA_PROFILE_GROWS (HARD PASS)

|kappa_n / c - 1| is monotone increasing with n in majority of alpha cells; ratio
between |delta_n_max| and |delta_2| > 1.5. Interpretation: substrate algebraic
signature dominates higher moments. Deflated P = 0.35.

### KAPPA_PROFILE_DECAYS (HARD FAIL)

Ratio |delta_n_max| / |delta_2| < 0.5 in majority of cells. Higher cumulants are
MP-like. Deflated P = 0.20.

### KAPPA_PROFILE_SATURATES

Ratio in [0.5, 1.5] across n, all |delta_n| > 0.05. Substrate has a constant
"kappa offset" at all orders. Deflated P = 0.30.

### KAPPA_PROFILE_INCONCLUSIVE

Mixed pattern across alpha cells; no dominant class. P = 0.15.

---

## Substrate-product interpretation

- **GROWS**: the substrate's algebraic structure (4-coset Kerdock, Maiorana-McFarland
  GF(2^t) quadratic) produces an *amplified* free-probabilistic signature at high
  moments. The substrate fingerprint sharpens with measurement depth. Implication for
  the AMP/VAMP universality classes: any approximation that truncates kappa_n at
  finite n will FAIL increasingly with measurement depth.
- **DECAYS**: substrate signature is entirely in the low-order spectral structure.
  OAMP/VAMP using up through 4th-order corrections would suffice. Suggests substrate's
  computational identity is captured by 2-4 free cumulants.
- **SATURATES**: substrate has an all-orders constant kappa shift. Mechanism is
  consistent with a structural mean-field offset (e.g., the Kerdock 4-coset structure
  imposing a uniform bias on the trace-moment functional).

---

## PROT compliance

Per [[feedback-pipeline-pacing]]: GPU-first depth probe. Substrate-fingerprint expansion
on the third independent algebraic axis (after kappa_n_v1 and S-transform).
