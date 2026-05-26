# Prereg: wave14_kappa_gold_quickprobe_v1

**Date:** 2026-05-23
**Author:** exp_dev (Tier-C scoping probe)
**Tier:** C (quick scoping, <60s, single-config, 1 seed, local CPU)

## Motivation

Extend the codebook landscape map against the BBMD (bulk-bounded
moment-divergent) regime. Current landmarks:
- Paley Type-I Hadamard sub-block: PERFECT_ISOMETRY (kappa_n=0, delta spectrum)
- Kerdock 4-coset: BBMD candidate (kappa_n GROWS, bulk-bounded but moment-divergent)
- Haar: asymptotically free (kappa_n -> 0)
- iid Gauss: MP (kappa_n = c, free-Poisson)

**Gold sequences** are a natural disambiguator: they share Kerdock's
GF(2^m)-trace algebraic substrate but use a DIFFERENT construction
(cross-correlation of two m-sequences, not 4-coset Reed-Muller). Gold's
theorem guarantees 3-valued pairwise cross-correlation -- a structural
property distinct from Kerdock's even-distance Hamming spectrum.

## Hypothesis

H1 (BBMD_CANDIDATE): Gold falls in BBMD regime -> BBMD signature is GENERIC
to GF(2^m)-trace codebooks, not 4-coset-specific. Strong implication for
the substrate product: any algebraic-trace codebook family produces the
bulk-bounded-moment-divergent fingerprint, expanding the substrate's
addressable codebook envelope.

H2 (MP_LIKE): Gold sits near MP (with iid_gauss) -> Kerdock's 4-coset
combinatorics SPECIFICALLY (not the GF(2^m) machinery) drives BBMD. This
narrows the substrate-novel claim to 4-coset constructions.

H3 (NON_MP_OUTLIER): Gold spectrum has outliers beyond MP edges ->
3-valued cross-correlation -> spectral-outlier axis. New design-space
direction worth a depth probe.

H4 (PERFECT_ISOMETRY): Gold rows are mutually orthogonal of equal norm
(delta spectrum, kappa_n=0). Surprising but possible if our chosen
sub-family is over-structured.

## Verdict classes

- `GOLD_PERFECT_ISOMETRY`: kappa_n ~ 0 for n>=2 (within 1e-3), kappa_1 > 0.5
- `GOLD_MP_LIKE`: all |kappa_n / c - 1| < 0.10 for n=2..4 AND spectrum bulk-bounded
- `GOLD_BBMD_CANDIDATE`: kappa_n NOT MP-like (some |dev| >= 0.10) AND spectrum bulk-bounded
  (lam_max <= (1+sqrt(c))^2 * 1.05 AND lam_min within edge_width*0.05 of (1-sqrt(c))^2)
- `GOLD_NON_MP_OUTLIER`: spectrum has lam outside MP edges by >5%
- `GOLD_OTHER`: mixed/inconclusive

## Hard-fail thresholds

This is a Tier-C scoping probe -- ONE config, ONE seed. We do NOT make
a robust claim across the full Anchor-2 design space; the goal is to
classify Gold's position on the BBMD axis with one read. Follow-up
depth probe (multi-seed, multi-alpha) only if Gold lands in BBMD_CANDIDATE
or NON_MP_OUTLIER classes.

## Config

- m = 10 (so N = 2^m - 1 = 1023; smallest scale that admits Gold preferred
  pair at "Kerdock-compatible" scale; t=5 primitive polynomial maps to
  Reed-Muller scale 32 = 2^5 not Gold scale -- we use Gold's own native
  m=10 -> N=1023 which is the standard CDMA Gold scale)
- M = N = 1023 (square; alpha = 1) -- matches Kerdock's alpha=1 baseline
- n_seeds = 1 (Tier-C scoping)
- n_max_moment = 4 (Tier-C spec: kappa_2..kappa_4)
- numpy.linalg.svd on float32 (1023 x 1023); expected SVD time ~3-5s
- Total wallclock target: <60s

## Cap_map row impact

- BBMD_CANDIDATE -> add new 🟡 row "Gold codebook BBMD signature" (single-N,
  single-seed; promote to deeper probe before 🔬/✅)
- MP_LIKE -> sharpens the Kerdock cap_map row "BBMD signature requires
  4-coset combinatorics specifically (Gold's GF(2^m)-trace alone insufficient)"
- NON_MP_OUTLIER -> new 🔬 row "Gold spectral-outlier axis" needing
  follow-up depth probe
- PERFECT_ISOMETRY -> log alongside Paley as a second over-structured-codebook
  landmark; no new cap_map row

## Status log

importance=LOW (Tier-C scoping); plain_language: "extending the codebook
landscape map with Gold sequences; outcome useful only if it lands in
BBMD_CANDIDATE or NON_MP_OUTLIER (else just refines the Kerdock-axis story)".

## Queue

Local CPU (Tier C: <60s, single-config, single-seed).
