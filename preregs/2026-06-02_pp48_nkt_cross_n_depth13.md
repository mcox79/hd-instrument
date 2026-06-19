# Pre-registration: pp48_nkt_cross_n_depth13_v1_n8192

**Date:** 2026-06-02
**Anchor:** pp48_nkt_cross_n_depth13_v1_n8192
**Queue:** overnight_queue
**Cap-map row:** PP-48 NKT negative-knowledge tree cross-N envelope

## Hypothesis

NKT depth-13 at N=8192 5-seed passes HP: pos_retrieval_rate >= 0.75 AND nkt_repulsion_rate >= 0.65.
Enables cross-N criterion band-lift: if depth-13 holds at BOTH N=4096 AND N=8192.

## Pre-registered Bands

- **HARD-PASS:** pos_retrieval_rate >= 0.75 AND nkt_repulsion_rate >= 0.65
- **HARD-FAIL:** pos_retrieval_rate < 0.40 OR nkt_repulsion_rate < 0.30
- **MIDDLE:** 1/2 conditions met

## Calibration

Prior: depth-13 HARD_PASS at N=4096. Bands unchanged for cross-N.

## Smoke Results

Smoke at N_smoke=1024 (smoke for N=8192 anchor), 2 seeds:
- pos_rate=1.0000, nkt_rep_rate=1.0000 -- HARD_PASS at smoke scale
- Wall: ~1.35s for 2 seeds. GPU util: 0.034 GB confirmed.

## Timeout Estimate

- smoke_wall_s ~ 1.35s for 2 seeds at N=1024 → 0.675s per seed
- FULL_N=8192, smoke_N=1024 → ratio=8; FULL_seeds=5, smoke_seeds=2
- scaling_exp=1.5 (vector ops, pattern matrices at N=8192)
- timeout_s = ceil(1.5 * 1.35 * (8^1.5) * 2.5) = ceil(115) = 300s

**timeout_s = 1800** (tree building 8191 nodes * N=8192 vectors; conservative 6x)

## Formula Self-tests

1. BRANCH=2, D=13 total = 2^13-1 = 8191. EXPECTED: 8191. VERIFIED.
2. alpha_total = 110/8192 = 0.013 < 0.138. VERIFIED.

## N-suffix

Anchor _n8192 binds N=8192 in production config. Verified: N=8192 in script.
