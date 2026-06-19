# Prereg: combo2_p4_l3_signed_am_v1_n4096_l4_extension_v1

**Date:** 2026-06-02
**Anchor:** combo2_p4_l3_signed_am_v1_n4096_l4_extension_v1
**Queue:** overnight_queue

## Scientific question
At N=4096, does 4-layer (L=4) p=4 DAM hierarchical composition + signed-AM produce l4_fidelity >= 0.75 and b_repulsion >= 0.90?

## Pre-registered thresholds
- HP1: l4_fidelity_A >= 0.75 (relaxed from L=3 0.85; one more binding step).
- HP2: b_repulsion_rate >= 0.90.
- HP3: parity_contamination <= 0.10.
- HARD-PASS: all 3 HP in >= 4/5 seeds.
- HARD-FAIL: l4_fidelity < 0.40 OR b_repulsion < 0.40.
- MIDDLE: 2/3 HP conditions met.
Calibration: first L=4 test. P_deflated = 0.60 (calibration probe; bands +-50% of predicted 0.80).

## Timeout estimate
smoke_wall_s ~ 5s at N=512 2-seed. FULL N=4096, 5 seeds, scaling_exp=1.5 (vector sweeps):
timeout_s = ceil(1.5 * 5 * 8^1.5 * 2.5) = ceil(424) = **600s**.

## PROT-018
anchor _n4096; production N = 4096. Verified.
