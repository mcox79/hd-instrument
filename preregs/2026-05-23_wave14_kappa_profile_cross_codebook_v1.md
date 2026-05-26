# Prereg — wave14_kappa_profile_cross_codebook_v1

**Date**: 2026-05-23 (late session)
**Owner**: exp_dev (BBMD anchor 2 of 2)
**Source**: research note `notes/research_promising_direction_2026-05-23.md` (BBMD regime proposal). Cap-12 promotion is conditional on BOTH anchors landing positive.

## Hypothesis

The BBMD-distance scalar `sum_{n=2..6} | kappa_n - kappa_n^MP |` is a
**portable discriminator** for AMP-non-universality that the standard MP-KS
bulk-fit pre-test misses. Concretely:

  Ordering by BBMD-distance: iid_gauss <= SRHT < Hadamard <= RM(1,m) < Kerdock

  AND MP-KS < 0.05 for ALL FIVE codebooks (the bulk-MP fit passes everywhere —
  the standard universality pre-test would say "AMP works" on every codebook).

If both hold, the kappa_n profile is the **needed** extra diagnostic over the
standard MP-KS pre-test.

## Setup

- N = 4096 (forced even-log2 for Kerdock 4-coset builder; matches Hadamard
  Sylvester 2^12; RM(1, m=12) gives 2N = 8192 codewords of length N).
- M = N (M/N = 1.0, alpha_ratio = 1.0).
- 10 seeds per codebook.
- kappa profile through n=6.
- Five codebooks:
  1. iid_gauss — `N(0, 1/N)` entries.
  2. srht — random sign diagonal D × Sylvester Hadamard H, subsample M rows.
  3. hadamard — direct row-subsample of N x N Sylvester Hadamard.
  4. rm_1_m — Reed-Muller RM(1, m=12): rows of Hadamard union rows of -Hadamard,
     yielding 2N codewords; subsample M of them.
  5. kerdock — substrate's 4-coset Kerdock 4N codebook; subsample M.

## Output metrics (per codebook)

- `bbmd_distance_mean`: average over seeds.
- `ks_stat_mean`, `ks_stat_max`: empirical-vs-MP KS statistic (per-seed eigenvalues
  vs analytic MP(c=M/N) CDF on a 400-point grid).
- `kappa_mean`: per-n cumulant averaged over seeds.

## Verdicts

**HARD PASS — `KAPPA_CROSS_CODEBOOK_PASS`** (Anchor 2 lands positive):
- BBMD-distance ordering: `iid_gauss <= ... <= kerdock` (iid_gauss is min,
  kerdock is max, srht <= rm_1_m), AND
- MP-KS mean stat < 0.05 for ALL FIVE codebooks.

**HARD FAIL — `KAPPA_CROSS_CODEBOOK_KILLED`** (BBMD as a portable discriminator killed):
- Ordering scrambled (iid_gauss is not bbmd-min, OR kerdock is not bbmd-max,
  OR srht > rm_1_m), OR
- Some structured codebook (srht / hadamard / rm_1_m) has MP-KS >= 0.05 —
  then the standard pre-test ALREADY discriminates and kappa_n adds nothing.

**INCONCLUSIVE — `KAPPA_CROSS_CODEBOOK_INCONCLUSIVE`**: anything in between or
missing codebooks.

## Pre-commit

- Ordering checks are FROZEN here.
- The "iid_gauss is min AND kerdock is max" constraints are the hard ordering
  anchors; the SRHT-vs-RM(1,m) check tests whether AMP-universal SRHT (Dudeja-
  Lu-Kini 2022) is genuinely BBMD-cheaper than the algebraically-richer RM code.
- A single seed-mean is used per codebook for ordering; per-seed details are
  retained in metrics.json for post-hoc inspection.

## Downstream

- PASS + Anchor-1 PASS -> propose Cap-12 (BBMD-VAMP) to Strategy.
- PASS + Anchor-1 FAIL -> kappa_n is a portable diagnostic but BBMD doesn't
  predict AMP-VAMP gap (rethink unification).
- KILLED -> kappa_n profile is not a portable substrate-product primitive;
  BBMD downgraded to Kerdock-internal characterization (still useful, less
  generalizable).

## Queue

- Queue: `remote_cpu_queue` (numpy-bound SVD x 50 cells; no GPU).
- Timeout: 5400 s.
- ETA: 60-90 min wallclock (Kerdock builder ~5 s per call; SVD M=N=4096 ~30 s
  per call; 5 codebooks * 10 seeds = 50 SVDs).

## Citations

- Dudeja-Lu-Kini 2022 (arXiv:2204.04281) — SRHT AMP universality (baseline).
- Calderbank-Jafarpour 2010 (arXiv:1004.4949) — Kerdock as deterministic
  sensing matrix.
- Reed-Muller RM(1, m): standard linear code over F_2 with 2^(m+1) codewords.
- Voiculescu 1983 + Speicher 1994 — free cumulants foundations.
