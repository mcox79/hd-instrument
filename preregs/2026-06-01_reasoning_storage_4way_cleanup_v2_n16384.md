# Prereg: reasoning_storage_4way_cleanup_v2_n16384

**Date:** 2026-06-01
**Anchor:** reasoning_storage_4way_cleanup_v2_n16384
**Queue:** remote_cpu_queue
**Cap_map trigger:** v304 V1 R2 -- PP-11 5-seed upgrade to resolve borderline 3-seed result

## Scientific question

Does the v1 4WC + cleanup result replicate at 5-seed level [7, 17, 23, 31, 41] with Arm C ratio >= 0.98 on ALL 5 seeds? v1 landed mean ratio ~0.977 but per-seed strict <2% was borderline (seeds 7 and 17 at 2.5%, only seed 23 at 1.0%).

## Design

All logic identical to v1 (imports v1 science directly). Only SEEDS_FULL changed from [7,17,23] to [7,17,23,31,41]. N=16384, N_CHAINS=500, DEPTH_MIN=3, DEPTH_MAX=5.

## Pre-registered bands (identical to v1)

**Arm C (combined 4-way + cleanup) -- PRIMARY:**
- HARD-PASS: mean ratio >= 0.98 (gap < 2%); ALL 5 seeds pass; cleanup verify >= 0.95.
- HARD-FAIL: mean ratio < 0.96 (< 1% improvement vs PP-11 ~0.93).
- MIDDLE-BAND: mean ratio 0.96-0.98.

**Cap_map outcome if HARD-PASS:**
- PP-11 row LIFTS 0.50-0.65 -> 0.55-0.70 (+5%/+5% CONSERVATIVE clean-HP-upgrade).

**Cap_map outcome if MIDDLE-BAND or HARD-FAIL:**
- PP-11 row stays at 0.50-0.65 (v1 borderline result stands; no regression).

## Smoke result

Smoke (N=512, n_chains=20, seed=17): HARD_PASS. 4WC_HARD_PASS C_combined_ratio=1.000 cleanup_verify=1.000. Smoke wall_s=0.21s.

## Timeout estimate

```
v1 elapsed at remote CPU (3 seeds): ~33s/seed estimated from prior v1.
v2: 5 seeds x 33s = 165s. Safety: ceil(1.5 * 165) = 248s -> 300s.
PROT-019 floor: 14400s. timeout_s = 14400 (floor dominates; actual ~5 min).
```

## PROT-018 N-suffix

`_n16384`: N_FULL = 16384 (from v1 import). Confirmed via grep.

## Dependencies

Imports from `experiments/exp_reasoning_storage_4way_cleanup_v1_n16384.py`. Verified: v1 script exists at D:/AI/hd-instrument/experiments/exp_reasoning_storage_4way_cleanup_v1_n16384.py. Import chain smoke-tested successfully.
