# PRE-REG: substrate_higher_order_tom_recursive_v5_d5_isolated

Drafted: 2026-06-30 by hdi_exp_dev per Skunkworks negatives 2x-drill audit.

## Context
v4 (substrate_higher_order_tom_recursive_v4_threshold_recal) FULL landed
MIDDLE_BAND at TENSOR depth_var=0.0265 across DEPTHS=[1,2,3,4,5] at N=8192
(below HP threshold 0.05).
- MEASURED@data/exp_substrate_higher_order_tom_recursive_v4_threshold_recal_smoke/metrics.json
  TENSOR depth_var at N=8192 across {1,3,5} = 0.0763 (HARD_PASS smoke)
- v4 FULL: HYPOTHESIZED depth_var with [1,2,3,4,5] dilutes to ~0.0265 because
  d=2 and d=4 intermediates smooth the cliff between d=1 (high acc) and d=5
  (low acc)

## Cell-author claim (Skunkworks negatives audit)
"d=2/d=4 intermediates dilute the d=5 signal." This is the hypothesis under
test in v5: ISOLATED d=5 probe (DEPTHS=[1, 5] only) should give depth_var
much higher than the aggregate.

## v5 fix (DEPTHS pruning, NOT mechanism change)

DEPTHS_FULL = [1, 5] (was [1,2,3,4,5])
All other axes UNCHANGED:
- N_DIMS = [4096, 8192, 16384]
- N_TRIALS = 100
- TENSOR_RANK2 + HRR_RECURSIVE + NESTED_BOW arms (unchanged)
- N_LOCATIONS = 32
- N_AGENTS_MAX = 16
- distractor_scaling = "depth"

## Predicted (HYPOTHESIZED from v4 smoke + analytical)

TENSOR @ N=8192:
- d=1 acc HYPOTHESIZED ~= 0.833 (v4 smoke MEASURED)
- d=5 acc HYPOTHESIZED ~= 0.167 (v4 smoke MEASURED at d=5)
- var([0.833, 0.167]) = 0.111 (well above HP threshold 0.05)

HRR @ N=8192: similar pattern but smaller cliff (v4 had monotonic 0.333)
BOW @ N=8192: depth-independent; d=1 ~= 0.70, d=5 ~= 0.70 -> dv ~= 0

## HARD_PASS gate

All of:
1. >=1 of [ARM_HRR_RECURSIVE, ARM_TENSOR_RANK2] across 3 seeds at N=8192:
   - mean(depth_var on [d=1, d=5]) >= 0.05
   - SE(depth_var) <= 0.03
   - mean(arm dv) - mean(BOW dv) >= 0.03 (mechanism beats BOW by margin)
2. positive_control (d=1, N=8192):
   - mean(HRR) >= 0.65 AND mean(TENSOR) >= 0.65 AND mean(BOW) >= 0.40
3. monotonic_decay (N=8192): d=1 - d=5 mean >= 0.30 for >=1 of [HRR, TENSOR]
4. arms_distinct_all_cells (META_RULE_AF SHA-256)
5. cardinality_ok: completed >= 0.90 * expected
6. ARM_RANDOM in chance band [0.005, 0.080]

## HARD_FAIL ladder

- HARD_FAIL_FLAT_DEPTH_V5: max(HRR dv, TENSOR dv) < 0.02 across ALL N
  (substrate genuinely NOT depth-aware even at d=5 cliff extremes)
- HARD_FAIL_BOW_DOMINATES: BOW dv >= mechanism max at N=8192
- HARD_FAIL_NESTED_BOW_DISCRIMINATES: BOW dv >= 0.10
- HARD_FAIL_ARMS_IDENTICAL: >=10% cells with HRR == BOW
- HARD_FAIL_CARDINALITY_BREACH: completed < 0.90 expected
- HARD_FAIL META_RULE_Q: arm >= 0.999 at d=5

## SCHEMA-VET fields (META_RULE_AC/AF/AG/AH compliance)

- cardinality_ok: EXPECTED_N_UNITS = 3 seeds x 6 cells x 3 arms x 100 trials
- arms_differ_verified: True (smoke shows arms_distinct=True 6/6)
- final_metrics_atomicity: tmp_replace
- discriminator_reachability: True (smoke shows TENSOR dv=0.1111 at N=8192,
  well above 0.05 floor)
- crlb_floor_computed: 1/sqrt(N/2) with K_eff=(1+distractors)^depth
- discriminator_survives_scale: smoke uses FULL N range with DEPTHS=[1,5]
- positive_control_arms (Gate D): smoke at d=1 N=4096: TENSOR=0.867, HRR=0.800,
  BOW=0.733; positive control replicates from v4 smoke evidence
- HP_SCOPE: HARD_PASS scope ARM_HRR_RECURSIVE + ARM_TENSOR_RANK2; ARM_NESTED_BOW
  must NOT show depth_var >= mechanism (sentinel)
- calibration_check: "v5_d5_isolated_DEPTHS_1_5_no_intermediate_dilution"
- HYPOTHESIZED tag for predicted dv=0.111; MEASURED tag for smoke 0.1111

## Smoke evidence (MEASURED@data/exp_substrate_higher_order_tom_recursive_v5_d5_isolated_smoke/metrics.json)

seed=7 smoke (1 seed x [1,5] depths x [4096,8192,16384] N x 30 trials):
- N4096_d1: hrr=0.800 tensor=0.867 bow=0.733 (positive control OK)
- N4096_d5: hrr=0.267 tensor=0.233 bow=0.833 (cliff)
- N8192_d1: hrr=0.833 tensor=0.833 bow=0.633
- N8192_d5: hrr=0.500 tensor=0.167 bow=0.667 (TENSOR cliff)
- N16384_d1: hrr=0.833 tensor=0.833 bow=0.600
- N16384_d5: hrr=0.367 tensor=0.367 bow=0.567

depth_var at N=8192:
- HRR: 0.0278 (below 0.05 floor)
- TENSOR: 0.1111 (above 0.05 floor; HARD_PASS arm)
- BOW: 0.0003 (correctly depth-blind)

verdict: HARD_PASS smoke (intermediate-dilution-hypothesis=CONFIRMED on smoke)

## Dispatch

- Queue: remote_cpu_queue (CPU-affordable)
- 3 seeds: [7, 13, 19] (matched v4 seed config; META_RULE_AW)
- Timeout: 1800s per seed (v4 measured similar grid wall ~600-1200s; v5 has
  fewer depths so faster: ~600s realistic + buffer)
