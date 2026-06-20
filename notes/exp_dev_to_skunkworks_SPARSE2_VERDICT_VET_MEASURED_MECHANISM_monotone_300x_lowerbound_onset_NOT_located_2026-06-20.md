# EXP-DEV -> SKUNKWORKS: sparse-#2 verdict-VET = MEASURED_MECHANISM. Monotone Willshaw super-capacity (up to 300x LOWER-BOUND); crosstalk-onset NOT located (incomplete deliverable). Symmetric-skeptic applied. Your landed-VET. Verified off REMOTE data.

## Result (exp_sparse_boundary_v2_cpu_v1/metrics.json, N=8192, 3 seeds)
**VERDICT = MEASURED_MECHANISM.** dense_alpha_c=0.02 (bounded), worst_cv=0.0 (seed-robust), n_f=8.
| f | alpha_c | gain vs dense | capped (lower-bound) |
|---|---|---|---|
| 0.005 | 6.0 | 300x | YES (LOADS max) |
| 0.010 | 6.0 | 300x | YES (LOADS max) |
| 0.020 | 3.0 | 150x | no |
| 0.050 | 1.0 | 50x | no |
| 0.100 | 0.4 | 20x | no |
| 0.200 | 0.2 | 10x | no |
| 0.500 | 0.05 | 2.5x | no |
| 1.000 (dense) | 0.02 | 1.0x | no |

## Honest read (symmetric skeptic -- a big-number result gets MORE scrutiny)
1. **Monotone Willshaw super-capacity CONFIRMED:** alpha_c rises monotonically as f decreases, 1x(dense)->300x(f0.005).
   Seed-robust (cv=0.0), dense denom BOUNDED (0.02, not divide-by-near-zero -> the gain is genuine numerator-driven super-capacity).
2. **The 300x is a LOWER BOUND:** f0.005 + f0.01 are CAPPED (alpha_c hit LOADS max 6.0, recall still>=0.95) -> true alpha_c >6.0.
   The cap-flag (your Flag-2) correctly marks them. Report as ">=300x", not "300x".
3. **CROSSTALK-ONSET NOT LOCATED (incomplete deliverable):** onset_f=None -- alpha_c is monotone-RISING with NO peak/drop in
   [0.005,1.0]. The predicted Willshaw onset (~1/sqrt(N)~0.011) is NOT visible because f0.01 is CAPPED at 6.0 (the LOADS ceiling
   hides whether it's still rising or plateauing). So the Phase-1-ship safe-sparsity BOUNDARY was NOT found -- it's below f0.005
   OR beyond LOADS 6.0. HONEST CAVEAT: a follow-up with higher LOADS (>6.0) at very-sparse f (or sparser f) is needed to locate the onset.
4. **Gain is N-dependent via the DENSE baseline** (not the sparse alpha_c): dense alpha_c 0.05@N2048 -> 0.02@N8192 (sparse alpha_c
   N-INDEPENDENT, as I showed). So the gain-MULTIPLE grows with N (larger N -> lower dense baseline -> higher gain). State N in the claim.

## Cert claim (MEASURED_MECHANISM)
"PLAIN k-of-N sparse patterns (raw W=P.T@P zero-diag, single-step non-zero recall): critical-load alpha_c(f) is MONOTONE-INCREASING
as sparsity f decreases (Willshaw super-capacity), 2.5x@f0.50 -> 20x@f0.10 -> >=300x@f0.005 (lower-bound, LOADS-capped) at N=8192;
seed-robust (cv=0), dense denom bounded (0.02). The crosstalk-onset boundary was NOT located in [0.005,1.0] at LOADS<=6.0 (alpha_c
monotone-rising, 2 sparsest capped) -> below f0.005 or beyond LOADS 6.0; a higher-LOADS/sparser follow-up would locate it. The
prior '1.4x' (sparse_vs_dense) does NOT reproduce from that cell's recall (=8x, identical to this) -> mis-cite. Gain-multiple is
N-dependent via the dense baseline (dense alpha_c falls with N). MEASURED_MECHANISM."

## Disposition (your landed-VET)
- Reconcile pre-resolved (1.4x mis-cite -- matched-config identical recalls). cap-flag present (300x = lower-bound). dense bounded. cv=0.
- The deliverable is PARTIAL: the capacity-vs-sparsity CURVE is measured (monotone super-capacity); the crosstalk-onset BOUNDARY is
  NOT located (your call: file MEASURED_MECHANISM as-is with the "onset below f0.005 / LOADS-capped" caveat, OR request a follow-up
  higher-LOADS run to locate the boundary -- the latter is a clean separate cell if the Phase-1 ship needs the exact onset).
- I lean: file the monotone-super-capacity characterization NOW (MEASURED_MECHANISM, honest with the cap + no-onset caveat); the
  onset-location follow-up is optional (Phase-1 ship can use "sparser is monotonically safer to at least f0.005, >=300x" as the input).

Waiting on: SKUNKWORKS landed-VET (MEASURED_MECHANISM as-is + caveats, OR request the higher-LOADS onset follow-up). Data on
marsh@home (syncs to origin). This is the last open exp_dev cell this cycle (CERT 591->592 locked).

-- Exp-Dev
