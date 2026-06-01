# Pre-registration: t3_susceptibility_v1_n4096

**Date:** 2026-05-28
**Anchor:** t3_susceptibility_v1_n4096
**Queue:** overnight_queue
**Script:** experiments/exp_t3_susceptibility_v1_n4096.py
**N-suffix binding:** _n4096 -> N_FULL = 4096 (PROT-018)

## Hypothesis

At the current operating point (M_frac=10, beta=32, N=4096 Kerdock), measure
susceptibilities along three principal axes:
- chi_M = |dret/dM| / epsilon (memory load axis)
- chi_beta = |dret/dbeta| / epsilon (inverse temperature axis)
- chi_codebook = |dret/d(codebook order)| / epsilon (structural axis)

If all three diverge (chi >= 0.5 at epsilon=0.10): NEAR_TRIPLE_POINT.
If only chi_M large: TWO_PHASE_BOUNDARY.
If all small: STABLE_REGION.

## Pre-registered bands

**HARD_PASS (NEAR_TRIPLE_POINT):** All 3 chi >= 0.5 at epsilon=0.10 across >= 4/5 seeds.
**HARD_FAIL:** All 3 chi < 0.05 at epsilon=0.10 across all seeds (stable region, substrate insensitive).
**MIDDLE_BAND:** 1-2 axes show chi >= 0.5 but not all 3 (two-phase boundary or partial saddle).

## Timeout estimate

Smoke wall_s: 4.5s at N=1024, 1 seed, 2 operating points, 1 epsilon.
FULL: N=4096, 5 seeds, 2 operating points, 3 epsilons.
Scale: (4096/1024)^1.5 * 5 * (3/1) = 8 * 5 * 3 = 120x.
Estimate: 4.5 * 120 = 540s. Safety 1.5x = 810s.
User-approved floor for _n4096: timeout >= 14400.
**timeout_s = 14400** (user override for overnight batch).

## N-suffix section

_n4096 suffix; production N = 4096 (PROT-018 binding).
Smoke ran at N=1024.

## Prior anchor

axis3_triplepoint_v2_n4096 MIDDLE_BAND (v262): sign_divergence=True at M_frac=10, beta=8.
This probe explicitly quantifies the susceptibility magnitudes.
