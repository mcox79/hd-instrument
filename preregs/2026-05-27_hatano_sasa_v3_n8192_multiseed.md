# Prereq: hatano_sasa_v3_n8192_multiseed

Date: 2026-05-27
Anchor: hatano_sasa_v3_n8192_multiseed
Queue: overnight_queue
Script: experiments/exp_hatano_sasa_v3_n8192_multiseed.py
Timeout: 3600s

## Hypothesis
Hatano-Sasa excess work identity <exp(-W_ex)>=1 holds at N=8192 across 5 seeds (multi-seed replication; v1 was single-seed). sigma_hk > 0.01 confirms genuine NESS cost.

## Pre-registered bands
- HARD-PASS: hs_identity_val in [0.80,1.25] in >= 4/5 seeds AND sigma_hk > 0.01 in >= 4/5 seeds
- HARD-FAIL: hs_identity_val < 0.40 or > 2.50 in >= 3/5 seeds (strong violation)
- MIDDLE-BAND: otherwise

NOTE: prior single-seed anchor from v1. Bands based on +-25% of 1.0.

## Walk-back gate
Smoke hs_val=0.67 at N=512 is 16% below 0.80 threshold (within 20%). Doubled trajectories to 800 per seed.

## Timeout estimate
v1 ~200-400s for 400 trajectories at N=8192. Full 5 seeds * 800 traj: 5 * 2 * 300 = 3000s -> 3600s.
