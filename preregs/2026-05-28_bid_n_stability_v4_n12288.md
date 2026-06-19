# Pre-registration: bid_n_stability_v4_n12288

**Date:** 2026-05-28
**Anchor:** bid_n_stability_v4_n12288
**Script:** experiments/exp_bid_n_stability_v4_n12288.py
**Queue:** remote_cpu_queue
**Routing note:** strategy_request_to_exp_dev_v263_bid_n_stability_v4_n12288_2026-05-28.md

## Hypothesis

The BID scaling-law (approx +54% per N-doubling from v255) continues at intermediate N=12288.
Expected: BID(N=12288) in [110, 250] (geometric interpolation: 128 from BID(8192)*1.5^0.622).

## Context

v3 (N=16384) timed out at 4500s with zero production metrics. Root cause: v3 pre-reg
conflated total wall of v2 with per-cell baseline. Per-N=8192-cell actual: ~700s.
N=16384 requires 4x longer (O(M^2) where M=N*alpha=0.125*N). Rescue (b): intermediate
N=12288 reduces M^2 cost to 2.25x vs N=8192.

## Configuration

- N_VALUES_FULL = [8192, 12288] (control + new cell; PROT-018: _n12288 binding)
- Seeds = [7, 17, 23] (3-seed)
- M_FRAC = 0.125 (match v2)
- Queue: remote_cpu_queue (TwoNN; no CUDA)

## Pre-registered thresholds

Prior anchor: v2 BID at N=4096/8192 (v255 MIDDLE_BAND; outside Hopfield bands, drift>5%).

**HARD_PASS:** BID(N=12288) in [110, 250] AND in_known_class=False (outside all Hopfield bands).
  Interpretation: scaling-law continues through intermediate N; +54%/doubling rate holds.

**HARD_FAIL:** BID(N=12288) in_known_class=True (inside any Hopfield class band).
  Would refute v255 LIFT.

**MIDDLE_BAND:** BID outside bands but outside [110, 250] corridor.
  Regime change at intermediate N.

## Formula self-tests

1. interp_bid(100, 8192, 12288) = 100 * (12288/8192)^log2(1.54) = 100 * 1.5^0.622 = 128.1.
   Verified at design time: interp_bid returns 128.73. In range [120, 140]. PASS.
2. compute_verdict with BID(12288)=180, in_known_class=False -> HARD_PASS. Verified.
3. compute_verdict with in_known_class=True -> HARD_FAIL. Verified.
4. compute_verdict with BID(12288)=90 (below [110,250]) -> MIDDLE_BAND. Verified.

## Smoke gate result

Smoke N=[256, 1024] (multi-scale), 1 seed.
in_known_class=False at both smoke N values. BID values non-null, non-zero. elapsed=1.6s. PASS.
VERDICT: BID_N4_PARTIAL (expected: smoke doesn't include N=12288). Not suspicious.

## Cap_map impact

- HARD_PASS: scaling-law row 55-68% strengthened; evidence at 3 N-doublings.
- HARD_FAIL: would weaken LIFT; investigate.
- MIDDLE_BAND: regime change annotation; LIFT unchanged.

## Timeout estimate

Per-N=8192-cell baseline: ~700s (from v2 per routing note re-derivation).
N=12288: M_12288=1536 vs M_8192=1024 -> O(M^2) scale = (1536/1024)^2 = 2.25 -> ~1575s/cell.
Control N=8192 (3 seeds): 3 x 700 = 2100s.
N=12288 (3 seeds): 3 x 1575 = 4725s.
Total: 6825s. 1.5x safety: 10238s -> 10800s.
NOTE: exceeds 7200s (2h). Flagged for visibility.

## N-suffix binding (PROT-018)

_n12288 -> N_PRODUCTION = 12288 in script. Verified.
Script runs N in {8192, 12288}; N=12288 is the primary new cell.
