# Pre-registration: c1_kf_battery_phase_v1_n4096

**Date:** 2026-05-28
**Anchor:** c1_kf_battery_phase_v1_n4096
**Queue:** overnight_queue
**Script:** experiments/exp_c1_kf_battery_phase_v1_n4096.py
**N-suffix binding:** _n4096 -> N_FULL = 4096 (PROT-018)

## Hypothesis

Full killer-feature battery at beta=32, N=4096 Kerdock, 4 M values spanning the phase boundary.
M=20K (M/N=4.9, deep multi-basin), M=45K (M/N=10.9, near boundary),
M=80K (M/N=19.5, single-basin), M=200K (M/N=48.8, deep single-basin).

KILLER FEATURES TESTED:
- KF-1: Hallucination margin (1 - max_oos_conf >= 0.90 threshold)
- KF-1b: No confident hallucination (above_thresh_frac = 0)
- KF-2: Edit isolation (max |delta_acc| <= 0.05 threshold)
- KF-5: Steerable beta (entropy_range >= 1.0 bit threshold)
- KF-retention: argmax retention (informational; records phase-boundary profile)
- KF-multihop: max chain depth where accuracy > 0.5 (informational)

PRODUCT QUESTION: Which phase should the product live in?
If KFs survive to M=45K: product can use near-boundary capacity.
If KFs fail at M=45K: product must stay in multi-basin (M < ~35K at N=4096).

## Pre-registered bands

**HARD_PASS:** >= 3/4 primary KFs (kf1, kf1b, kf2, kf5) pass at M=20K AND
  ret is monotone decreasing AND >= 2/4 KFs survive to M=45K.
**HARD_FAIL:** >= 3/4 primary KFs broken at M=20K (instrument failure).
**MIDDLE_BAND:** 2-3/4 KFs pass at M=20K, or all pass but fewer than 2 survive to M=45K.

## Per-KF thresholds (pre-registered)

- KF1_hallu_margin >= 0.90
- KF1b_above_thresh_frac <= 0.0
- KF2_isolation_ratio <= 0.05
- KF5_entropy_range >= 1.0 bit

## Timeout estimate

Smoke wall_s: 6.5s at N=1024, 1 seed, 2 M values.
FULL: N=4096, 3 seeds, 4 M values.
N-scale: (4096/1024)^1.5 = 8x. Seed scale: 3/1 = 3x. M scale: 4/2 = 2x.
Estimate: 6.5 * 8 * 3 * 2 = 312s. Generous safety with M=200K store time: x3 = 936s.
**timeout_s = 14400** (user override for overnight batch; actual estimate ~1000s).

## N-suffix section

_n4096 suffix; production N = 4096 (PROT-018 binding).
Smoke ran at N=1024 (same absolute M values; M/N ratios 4x higher at smoke).

## Prior anchor

kf1_tier1_rescue_v1_n4096 HARD_PASS; kf2_isolation_proof_v2_n8192 HARD_PASS;
kf5_steerable_beta_v3_n8192 HARD_PASS. First integrated battery across phase boundary.
