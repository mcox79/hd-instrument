# Pre-registration: axis4_hyst_critical_v2_n4096

**Date:** 2026-05-29
**Anchor:** axis4_hyst_critical_v2_n4096
**Queue:** overnight_queue
**Script:** experiments/exp_axis4_hyst_critical_v2_n4096.py
**Parent:** axis4_hyst_ramp_v1_n4096 (HARD_FAIL: max_loop_area=0.0 at beta=8)

## Hypothesis

Axis-4 M-ramp hysteresis may exist at the multi-basin operating point (beta near beta_c=10,
M near M_c boundary). v1 probed at beta=8 (subcritical); the multi-basin phase structure
(SKAH-M) concentrates near beta_c ~ 10-12. If M-history dependence exists, it lives here.

## Protocol

3 seeds x 4 M_frac_max values ([4, 6, 8, 10] x N) x beta=10.0 x rate=20.
Single medium rate (vs v1's 3 rates); sweep covers M_c boundary.
N=4096 (log2=12 EVEN, Kerdock SAFE).

## Pre-registered bands

HARD_PASS: loop_area >= 0.10 * M_max at at least 1 M_frac AND at >= 2/3 seeds.
  Interpretation: M-history dependence confirmed at critical operating point.

HARD_FAIL: loop_area < 0.01 * M_max at ALL M_fracs and ALL seeds.
  1D M-axis model fully validated; beta-steering of hysteresis not demonstrated.

MIDDLE_BAND: loop_area in [0.01, 0.10) * M_max.

## Formula self-tests

1. N=4096 (PROT-018 binding). N=4096 log2=12 EVEN -> Kerdock SAFE.
2. loop_area = sum |ret_load(M) - ret_unload(M)| * dM / M_max. Range [0, 1].
3. Reversible process -> loop_area = 0. Zero-area -> HARD_FAIL confirmed.
4. beta_critical = 10.0 (near multi-basin boundary; SKAH-M phase).
5. M_frac_max=10 -> M_max = 40960 at N=4096. OOM: W=64MB. SAFE.

## Timeout estimate

12 cells (3 seeds x 4 M_frac) x ~200s each = 2400s. Safety 1.5x: 3600s.
Floor _n4096 = 14400s.
timeout_s = 14400

## N-suffix binding (PROT-018)

_n4096 suffix -> N_FULL = 4096 in script. VERIFIED.
