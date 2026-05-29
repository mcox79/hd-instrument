# Pre-registration: kf1_hallu_rescue_v3_n8192

**Date:** 2026-05-29
**Anchor:** kf1_hallu_rescue_v3_n8192
**Queue:** overnight_queue
**Script:** experiments/exp_kf1_hallu_rescue_v3_n8192.py
**Parent:** kf1_hallu_rescue_v2_n4096 (HARD_PASS at N=4096)

## Hypothesis

KF-1 hallucination-detection (posterior-entropy mechanism) holds at N=8192.
above_thresh_frac=0 in all 5 seeds at M <= N, same as N=4096 result.
This is the N-axis replication required for KF-1 row promotion from green to checkmark.

## Protocol

5 seeds x 3 M_fracs ([0.25, 0.50, 1.0] x N) x N=8192.
Readout: argmax-vs-uniform. NO Kerdock codebook construction (Kerdock audit: SAFE).
C = 4*N = 32768 codewords at N=8192.

## Pre-registered bands

HARD_PASS: above_thresh_frac=0 in ALL 5 seeds at M <= N
  AND mean_oos_max_conf <= 10/C (=3.052e-4) in >= 4/5 seeds
  AND max_oos_max_conf < 50/C (=1.526e-3).
  Interpretation: KF-1 N-axis replication confirmed; row eligible for tick promotion.

HARD_FAIL: any seed shows above_thresh_frac > 0 at M <= N.

MIDDLE_BAND: above_thresh_frac=0 but mean_max_conf > 10/C in >1 seed.

## Formula self-tests

1. N=8192 (PROT-018 binding).
2. C = 4*8192 = 32768. 1/C = 3.052e-5. 10/C = 3.052e-4. 50/C = 1.526e-3.
3. 10/C at N=8192 is TIGHTER than 10/C at N=4096 (6.103e-4). Bounds scale correctly.

## Timeout estimate

Smoke: v2 at N=4096 elapsed ~5-10s. N-scale 2x linear -> ~20s.
Safety 50x: 1000s. Floor _n8192 = 21600s.
timeout_s = 21600

## N-suffix binding (PROT-018)

_n8192 suffix -> N_FULL = 8192 in script. VERIFIED.

## Kerdock audit

Script imports exp_kf1_tier1_rescue_v1_n4096 which uses argmax-vs-uniform readout.
make_kerdock_4coset_codebook NOT called. SAFE at N=8192 (log2=13 odd, irrelevant).
