# Pre-reg: wave14_kappa_paley_quickprobe_v1

**Date:** 2026-05-23
**Author:** exp_dev (sonnet)
**Status:** sub-60s LOCAL CPU scoping probe (NOT a verdict-ship experiment)
**Queue:** local_cpu_queue
**Wall time:** <5 s (smoke ran in 0.1 s)

## One-line purpose

Decide whether Paley Type-I Hadamard codebooks belong in the expanded BBMD codebook battery alongside Kerdock, by checking the spectrum of a M=510, N=1020 Paley sub-block.

## Motivation

Anchor 2 (`wave14_kappa_profile_cross_codebook_v1`) tests 5 codebooks (iid_gauss, srht, hadamard, rm_1_m, kerdock) for BBMD-distance ordering and MP-KS gate. The natural follow-up is whether a sixth algebraic family — Paley conference / Paley-Hadamard matrices, built from Legendre-symbol quadratic-residue patterns mod a prime p≡3 (mod 4) — also produces a non-trivial deviation worth integrating into a future Anchor-2 v2 or a separate sweep.

This is a *scoping* probe, not an Anchor:
- 1 codebook (Paley Type-I, p=1019, order 1020)
- 1 seed (row-permutation seed; Paley itself is deterministic)
- 1 alpha (M/N = 0.5)
- n_max = 6
- target wallclock < 60 s

## Construction

Paley Type-I Hadamard matrix of order p+1 for p prime with p ≡ 3 (mod 4):

```
Q[i,j] = chi(i - j mod p)        chi = Legendre symbol mod p
H = block matrix [[1, 1...1], [1^T, Q - I_p]]   -> H H^T = (p+1) I
```

Entries ±1. H is (p+1, p+1) = (1020, 1020) for p=1019. We sample M=510 rows (seed 0 permutation) and use the first N=1020 columns, giving a (510, 1020) bipolar measurement matrix.

## Method

1. Build H via Legendre table + block construction.
2. Sample M=510 rows; A = H[rows]; A_norm = A / sqrt(N).
3. numpy SVD of A_norm → singular values s; eigenvalues = s².
4. Spectral moments m_1..m_6 = mean(eig^n) over the M nonzero eigenvalues (matching v1's empirical path).
5. Invert to free cumulants kappa_1..kappa_6 via the moment-to-free-cumulant recursion from `exp_wave14_kappa_n_profile_v1.py` (reused).
6. Compare to MP reference (kappa_n = c = M/N = 0.5).
7. Classify per the `classify_profile` function: PERFECT_ISOMETRY / MP_LIKE / NEAR_KERDOCK / STRONGER_THAN_KERDOCK / WEAKER_NON_MP / INCONCLUSIVE.

## Verdict logic

- **PERFECT_ISOMETRY**: kappa_n ≈ 0 for n ≥ 2 (tol 1e-3), kappa_1 ≈ 1. The spectrum is a delta function at 1 — Paley sub-block rows are *exactly* orthogonal (Hadamard property). Implication: Paley does not deviate from MP within a bulk; it collapses the spectrum entirely. Different mechanism than Kerdock.
- **MP_LIKE**: max |delta_n| < 0.05 for n=2..6. Paley matches MP.
- **NEAR_KERDOCK**: |delta_2| ∈ [0.15, 0.35] (Kerdock's known band).
- **STRONGER_THAN_KERDOCK**: |delta_2| > 0.35.
- **WEAKER_NON_MP**: |delta_2| < 0.15 but not MP-like.

## Expected result

Mathematically, since H is Hadamard (H H^T = 1020·I_1020), any M-row subset has rows orthogonal of equal norm sqrt(1020). After /sqrt(N=1020) normalization the singular values are exactly 1, so kappa_n = 0 for n ≥ 2 exactly. **Expected verdict: PERFECT_ISOMETRY.** The probe is a sanity check that this falls out cleanly; the metrics.json records the kappa profile for downstream cross-codebook comparison.

This expected result is itself the *information yield* of the scoping probe: it tells us Paley-as-codebook lives on a different axis than Kerdock (isometric vs algebraic-bulk), so naive inclusion in BBMD-distance Anchor-2 would be uninformative without first generalizing BBMD-distance to handle delta-spectra.

## Hard fail / no-data branches

- Self-test fail (Hadamard property H H^T ≠ D·I) → script aborts before queue claim.
- SVD fail → numpy LAPACK error, surfaces as crash.
- "PALEY_QUICKPROBE_INCONCLUSIVE" → fewer than 2 valid kappa entries; means the probe machinery broke, not a scientific result.

## What the result tells the orchestrator

| Outcome | Action |
|---|---|
| PERFECT_ISOMETRY (expected) | Do NOT add Paley to Anchor-2 v2 unless BBMD-distance is reformulated. Document the result and move on. |
| MP_LIKE | Paley is MP-like; treat as a baseline like iid_gauss. Low priority. |
| NEAR_KERDOCK | Surprising; Paley shows the same algebraic signature as Kerdock. Include in Anchor-2 v2 expansion. |
| STRONGER_THAN_KERDOCK | High-priority Paley follow-up; might explore Paley combinatorial structure further. |
| WEAKER_NON_MP | Document; medium priority for expansion. |

## Reuse + dependencies

- Imports `moments_to_free_cumulants_general`, `mp_reference_cumulants`, `spectral_moments` from `experiments/exp_wave14_kappa_n_profile_v1.py` (existing, tested).
- No torch / no CUDA — pure numpy. Designed for laptop CPU queue.
- No new framework code.

## metrics.json schema

```json
{
  "verdict": "PALEY_QUICKPROBE_<class>",
  "verdict_msg": "<plain-language recommendation>",
  "elapsed_s": <float>,
  "summary": {
    "cells": [{
      "p": 1019, "D": 1020, "M": 510, "N": 1020, "c_ref": 0.5,
      "moments_emp": [...], "kappa_emp": [...], "kappa_mp": [...],
      "dev_rel": [...], "dev_abs_n2plus": [...],
      "growth_class": "...",
      "svd_seconds": <float>
    }],
    "config": {...}
  }
}
```
