# Prereg — wave14_interp_family_N8192_reduced_v1

## Hypothesis

The Cap 12 AMP-error predictor (Spearman rho between AMP rel-err and kappa_n
divergence sum) survives N-scaling to N=8192 on SRHT and Hadamard families
even at a REDUCED 3-alpha x 3-seed grid (rho >= 0.50 each).

This is a substrate-honest substitute for the timed-out N=8192 anchor: the
v1 full E2 anchor (`wave14_interp_family_N8192_v1`) is queued but covers
3 families x 3 N values x 5 alpha x 5 seeds = 225 cells; this reduced
variant does 1 N value (8192) x 2 families x 3 alpha x 3 seeds = 18 cells
and produces a fast first signal of whether N=8192 holds.

## Pre-registered bands (verbatim from v1 verdict)

- **HARD PASS** (`INTERP_FAMILY_N8192_PASS`):
  - rho >= 0.50 at N=8192 for BOTH families (SRHT, Hadamard) AND
  - max VAMP rel-err at N=8192 < 0.20.

- **HARD FAIL** (`INTERP_FAMILY_N8192_KILLED`):
  - rho < 0.30 at N=8192 on EITHER family.

- **MIDDLE BAND** (`INTERP_FAMILY_N8192_INCONCLUSIVE`):
  - rho in [0.30, 0.50) on at least one family, OR VAMP rel-err
    in [0.20, ...) on either.

## Design

- N = 8192 (only).
- 2 families: SRHT, Hadamard (Kerdock structurally absent: log2(8192)=13 odd).
- 3 alpha values: 0.0, 0.5, 1.0.
- 3 seeds per (family, alpha).
- M/N = 1.0 (so M = 8192).
- n_iter = 200 for AMP + VAMP.

Total cells: 2 * 3 * 3 = 18. Each (family, alpha, seed) does:
- One SVD of (8192, 8192) (~30 sec on GPU; can SVD-cache by (family, seed)).
- One AMP run (~few sec).
- One VAMP run from same SVD (~few sec).

ETA: 60-90 min on GPU.

## COMPUTE BUDGET / TIMEOUT-not-FAIL

- timeout = 5400s (90 min); if hit, the script returns a partial metrics.json
  with the cells completed so far; verdict_handler classifies as
  TIMEOUT-not-FAIL, NOT a substantive HARD FAIL.

## Citations / context

- v1 prereg: preregs/2026-05-24_wave14_interp_family_N8192_v1.md.
- Cap 12 ✅ at cap_map v175.

## Routing

- Queue: `overnight_queue` (GPU).
- Timeout: 5400 s.
