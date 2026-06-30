# PRE-REG: substrate_cortex_hippo_handoff_chain_grade_M_2048_GPU_v3_capacity_compliant

Drafted: 2026-06-30 by hdi_exp_dev per Skunkworks negatives 2x-drill audit
(cell 8 HARD_FAIL META_RULE_AW filed for config-drift).

## Context
v2 (substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed)
FULL with M=8192 / N_h=4096 / N_c=8192 (M/N_h = 2.0 = CAPACITY BREACH):
- MEASURED@data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_{7,13,19}/metrics.json
  seed_7: HARD_PASS at smoke (numpy CPU, M=512 / N_h=512 / N_c=2048)
  seed_13: HARD_FAIL (FULL, GPU); gap_FULL_vs_NO_REPLAY=+0.013 (transfer
    mechanism doing essentially nothing); DIRECT collapsed to 0.327
  seed_19: HARD_FAIL similar pattern
- Capacity breach: at M/N_h=2.0, hippo storage is overloaded; DIRECT cortex
  store (M=8192 items in N_c=8192 dense matrix, alpha=1.0) is also at the
  Hopfield capacity ceiling (~0.138*N_c = 1130 items)
- META_RULE_AW filed (cell-author drifted from chain-grade-compatible config)

## v3 fix (CAPACITY-COMPLIANT, NOT mechanism change)

Same replay_fixed mechanism (CLS-faithful; McClelland-McNaughton-O'Reilly 1995;
Wittkuhn & Schuck 2021 cue-reactivation). Reduce M to fit hippo capacity:

| Param      | v2 (CAPACITY BREACH) | v3 (CAPACITY COMPLIANT) |
|------------|----------------------|--------------------------|
| N_HIPPO    | 4096                 | 4096 (unchanged)         |
| N_CORTEX   | 8192                 | 8192 (unchanged)          |
| M_ITEMS    | 8192                 | 2048                     |
| M/N_h      | 2.0 (BREACH)          | 0.5 (sub-capacity)       |
| alpha_simple = M/N_c | 1.0           | 0.25                     |
| alpha_hopfield = M/(2*N_h*log(N_h)) | 0.12 | 0.030 (well below Hopfield ceiling 0.138) |

All other params UNCHANGED:
- HIPPO_SPARSITY = 0.10 (k=410 active in N_h=4096)
- N_REPLAY_CYCLES = 50
- ETA_CORTEX = 0.01
- SEEDS = [7, 13, 19] (META_RULE_AW: same seeds across cells)
- ARM_FULL_HANDOFF, ARM_NO_REPLAY, ARM_DIRECT_CORTEX (unchanged)

## Predicted (HYPOTHESIZED from physics + v2 smoke)

- DIRECT_CORTEX recall HYPOTHESIZED ~= 0.95-1.0 (M=2048 << Hopfield ceiling
  for N_c=8192 ~= 0.138 * 8192 = 1130 items; alpha=0.25 below ceiling)
- NO_REPLAY recall HYPOTHESIZED ~= 0.000 (cortex empty; W_hippo zeroed)
- FULL_HANDOFF recall HYPOTHESIZED ~= 0.70-0.90 (v2 smoke MEASURED=0.748 at
  alpha_simple=0.25 same; v3 has same alpha_simple)

Key test:
- If gap_FULL_vs_NO_REPLAY >= 0.20: mechanism works; v2 capacity was the
  genuine failure mode
- If gap_FULL_vs_NO_REPLAY < 0.05: mechanism broken at all scales

## HARD_PASS gate (per v2; META_RULE_AW preserved)

All of:
1. acc(FULL) >= 0.50
2. acc(FULL) - acc(NO_REPLAY) >= 0.40
3. abs(acc(FULL) - acc(DIRECT_CORTEX)) > 0.05 (META_RULE_AF arm-distinct)
4. alpha_simple = M/N_c >= 0.05 (v3: 0.25; auto-satisfied)

## HARD_FAIL ladder

- HARD_FAIL gap_FULL_vs_NO_REPLAY < 0.10 (transfer mechanism doing nothing)
- HARD_FAIL NO_REPLAY > 0.20 (cortex leaks signal)
- HARD_FAIL META_RULE_AF (bit-exact or fuzzy <= 0.05) FULL == DIRECT
- HARD_FAIL CARDINALITY_BREACH (expected 3 arms; not 3)
- WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb < 100MB on GPU dispatch

## SCHEMA-VET fields (META_RULE_AC/AF/AG/AH compliance)

- cardinality_ok: EXPECTED_N_UNITS = 3 arms x 1 seed = 3 arms per cell
- arms_differ_verified: True (META_RULE_AF bit-exact + fuzzy guards;
  selftest _selftest_full_arm_differs_from_direct enforces at module import)
- final_metrics_atomicity: tmp_replace (write_partial atomic)
- crlb_floor_computed: per-arm recall is binomial over M=2048;
  sigma_min(p=0.5) = sqrt(0.25/2048) = 0.0110.
  Discriminator gap sigma >= 0.0156 (sqrt(2) * sigma_min).
  HP gap band 0.40; HF gap band 0.10. Margin >>20*sigma. (Computed in Python)
- discriminator_reachability: True (smoke MEASURED gap=0.746; expected
  full gap >= 0.50 at sub-capacity)
- discriminator_survives_scale: smoke at intermediate alpha_simple=0.25 same
  as v3 FULL alpha_simple=0.25; mechanism gap MUST hold by alpha-invariance
- baseline_in_band: NO_REPLAY recall 0.002 at smoke (empty cortex floor);
  DIRECT 1.000 at smoke (ceiling); FULL 0.748 in band
- positive_control_arms: ARM_DIRECT_CORTEX is positive control; at M=2048
  N_c=8192 should HYPOTHESIZED ~= 0.95-1.0 (Hopfield sub-capacity)
- HP_SCOPE: ARM_FULL_HANDOFF gets the HARD_PASS gate; ARM_NO_REPLAY is
  baseline-floor (sentinel); ARM_DIRECT_CORTEX is baseline-ceiling (sentinel)
- calibration_check: "v3_capacity_compliant_M_over_N_h_0.5_sub_Hopfield"

## Smoke evidence (MEASURED@data/exp_substrate_cortex_hippo_handoff_chain_grade_M_2048_GPU_v3_capacity_compliant_smoke_seed_7/metrics.json)

seed=7 smoke (CPU/numpy; N_h=512, N_c=2048, M=512, N_replay=10, alpha=0.25):
- ARM_FULL_HANDOFF: recall=0.748, wall=166s
- ARM_NO_REPLAY: recall=0.002, wall=2s
- ARM_DIRECT_CORTEX: recall=1.000, wall=135s
- gap_FULL_vs_NO=+0.746, arm_dist_FULL_vs_DIRECT=0.252
- verdict: HARD_PASS smoke

Discriminator survives scale: smoke at alpha_simple=0.25 matches FULL
alpha_simple=0.25 by design (only N_h, N_c, M scaled proportionally).

## Dispatch

- Queue: overnight_queue (GPU; matmul-bound at FULL N_h=4096/N_c=8192)
- 3 seeds: [7, 13, 19] (META_RULE_AW: matched v2 seed config)
- Timeout: 1800s per seed (v2 FULL ran in ~300-600s per seed; v3 M is 1/4
  so faster: ~300s realistic + buffer)
- Per cell: ARM_FULL_HANDOFF (GPU batched matmul replay) + ARM_NO_REPLAY +
  ARM_DIRECT_CORTEX
- HDLAB_QUEUE env var preserved per cell PRESERVE_ENV_VARS line

## Risks

- If GPU N_h^2 matrix exceeds VRAM at N_h=4096 (4096^2 * 4B = 64MB; fine)
- If alpha_simple drift between smoke and FULL: BOTH are 0.25 BY DESIGN
- META_RULE_AW: ensure SEEDS = [7,13,19] match v2 across cells (verified)
