# Pre-registration: wave14_moe_shift_partition_v3

Date: 2026-05-26
Experiment file: experiments/exp_wave14_moe_shift_partition_v3.py
Queue: overnight_queue

## Context
MoE SHIFT/PARTITION/SINGLE 3-arm probe. v1 OOM at K=8 M=25600 (1.11GiB). v2 FAILED on remote.
v3 fixes OOM by capping M_mult at 1.0 for K>=8 (max M_total=12800 at K=8).

## Design
- 3 arms: SHIFT (context-shift routing), PARTITION (disjoint expert sets), SINGLE (no MoE baseline)
- K_SWEEP: [1, 2, 4, 8]
- M_PER_EXPERT: 1600
- M_MULT: [0.5, 1.0] for K>=8; [0.5, 1.0, 2.0] for K<=4
- Max M_total at K=8: 12800 (within 8GB GPU budget)

## Pre-registered bands (inherited from v2)
HARD-PASS: Arm A (SHIFT) mean_lift > Arm C (SINGLE) mean_lift by > 0.15 across K=[4,8]
HARD-FAIL: All arms within +/- 0.05 (MoE routing provides no benefit)
MIDDLE: Arm A > Arm C but lift < 0.15, OR inconsistent across K

## Falsifiable predictions
- If SHIFT mechanism is real, lift should scale with K (more experts = more benefit)
- If PARTITION mechanism is real, PARTITION > SINGLE across K
- If neither, SINGLE ~= both MoE arms within noise

## Self-test inputs/outputs
- gini([0.5, 0.5]) -> 0.0 (maximum diversity)
- gini([1.0, 0.0]) -> 1.0 (maximum concentration)
- K=8 M_mult budget: get_m_mult(8, False) -> [0.5, 1.0] (no 2.0)
- K=4 M_mult budget: get_m_mult(4, False) -> [0.5, 1.0, 2.0] (full grid)
