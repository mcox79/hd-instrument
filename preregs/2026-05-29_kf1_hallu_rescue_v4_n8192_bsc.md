# Pre-registration: kf1_hallu_rescue_v4_n8192_bsc

**Date:** 2026-05-29
**Anchor:** kf1_hallu_rescue_v4_n8192_bsc
**Script:** experiments/exp_kf1_hallu_rescue_v4_n8192_bsc.py
**Queue:** overnight_queue
**Timeout:** 21600s

## Hypothesis

KF-1 hallucination-impossibility holds at N=8192 using BSC (random +/-1) codebook.
The BSC substitute bypasses the Kerdock-even-log2 constraint that blocked v3_n8192.

Parent: kf1_hallu_rescue_v2_n4096 (KF1T1_HARD_PASS at N=4096 Kerdock).
Trigger: v274 routing note kf1_v3_kerdock_rescue (BSC-substitution PRIMARY rescue arm (a)).

## Configuration

- N: 8192 (N_FULL), BSC codebook C = 4*N = 32768
- M_fracs: [0.25, 0.50, 1.0] (undercap regime only; M <= N)
- Seeds: [7, 17, 23, 31, 41] (FULL), [17] (SMOKE)
- Smoke: N=1024, M_fracs=[0.25, 1.0], 1 seed
- n_oos_queries: 1000 (FULL), 100 (SMOKE)
- beta_inf: 32.0 for readout

## Metrics

- above_thresh_frac: fraction of OOS queries with max softmax confidence >= 0.5 (hallucination gate)
- near_uniform_mean: True if mean_max_conf <= 10/C
- near_uniform_max: True if max_max_conf < 50/C
- ratio_to_uniform_mean: oos_max_conf_mean * C (expected ~2-4x for ideal random codebook)

## Pre-registered bands

**HARD_PASS:**
(a) above_thresh_frac=0 in ALL 5 seeds at M_fracs <= 1.0
AND (b) mean_oos_max_conf <= 10/C in >= 4/5 seeds
AND max_oos_max_conf < 50/C (C=32768 at N=8192).

**HARD_FAIL:** any seed shows above_thresh_frac > 0 at M <= N.

**MIDDLE_BAND:** above_thresh_frac=0 but near-uniform bound (b) exceeded in > 1 seed.

NOTE: smoke at N=1024 shows MIDDLE_BAND (near-uniform fails at N=1024 due to smaller C=4096).
The near-uniform threshold 10/C at N=8192 is 10/32768=3.05e-4 vs 10/4096=2.44e-3 at smoke N.
BSC at large N has near-uniform OOS responses; HARD_PASS expected at N=8192 FULL.

## Timeout estimate

Smoke: N=1024, 1 seed, 2 M_fracs, 100 OOS queries -> 0.06s.
Full: N=8192, 5 seeds, 3 M_fracs, 1000 OOS queries.
N-scale: (8192/1024)^1.5 = 22.6x. OOS scale: 10x. Seeds: 5.
Estimate: 0.06 * 22.6 * 10 * 5 = 67.8s. Safety 100x = 6780s.
Floor _n8192 = 21600. timeout_s = 21600.

## Downstream

- HARD_PASS: KF-1 N-axis replication confirmed at N=8192 (BSC codebook). Row eligible for multi-N tick promotion (pending strategy review).
- MIDDLE_BAND: above_thresh=0 confirmed but near-uniform weak; investigate C-scaling of OOS distribution.
- HARD_FAIL: KF-1 breaks at N=8192 with BSC codebook; investigate mechanism.
