# PRE-REG: pfc_goal_conditioned_gate_v3_wm_additive_only

Date: 2026-06-27
Author: exp_dev (Opus 4.7 1M, agent-spawn)
Cell: experiments/exp_pfc_goal_conditioned_gate_v3_wm_additive_only.py
Predecessor: exp_pfc_goal_conditioned_gate_v2_cleanup_bind_output (HARD_FAIL smoke)

## Hypothesis

Per v2 metrics readout:
- V2 smoke: V1=0.340 / BIND_CLEAN=0.000 / WM=0.390 / ADDITIVE=0.390 / COMBINED=0.000 / ORACLE=1.000
- BIND_CLEAN arm collapses (cleanup-bind destroys bind info; snaps to single codebook entry).
- COMBINED arm inherits the collapse because it includes the bind path.
- WM_SLOT and ADDITIVE each gave +0.05 over V1 INDEPENDENTLY.
- ORACLE=1.000 means the pipeline works; headroom (ORACLE - V1) = 0.66.

V3 hypothesis: WM_SLOT and ADDITIVE_GOAL_BIAS are independent corrections; combining
them (COMBINED = WM bias + ADDITIVE bias, NO bind, NO cleanup) should be additive,
giving COMBINED >= V1 + 0.10 (each independently contributes +0.05).

## Arms (5; v3 redesign drops BIND_CLEAN + bind-cleanup-in-COMBINED)

- ARM_V1_NO_GOAL        baseline (regression sanity vs v2)
- ARM_WM_GOAL_SLOT      persistent WM slot goal-distance scoring (matches v2)
- ARM_ADDITIVE_GOAL_BIAS additive scoring; sweep alpha in {0.1, 0.2, 0.7, 1.0, 2.0}
  (alpha=0.5 EXCLUDED: produces bit-identical scoring to WM_SLOT; caught by AF self-test)
- ARM_COMBINED_WM_PLUS_ADDITIVE  WM goal-distance + additive bias (chosen alpha); NO bind, NO cleanup
- ARM_ORACLE            upper bound (correct op sequence given)

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS_SMOKE = 4 non-additive-arms x 2 seeds x 2 depths + 5 alphas x 2 seeds x 2 depths (ADDITIVE) = 16 + 20 = 36
- EXPECTED_N_UNITS_FULL  = 4 non-additive-arms x 5 seeds x 2 depths + 5 alphas x 5 seeds x 2 depths = 40 + 50 = 90
- Discriminator-survives-scale: smoke at N=8192 depths {3,6} (matches v1/v2 smoke regime).
- cardinality_ok = (completed_units >= EXPECTED_N_UNITS) per scale.

## Pre-reg HARD_PASS (ALL required)

- COMBINED_WM_PLUS_ADDITIVE.mean >= V1.mean + 0.10 (independent-additivity hypothesis)
- WM lift within +/-0.02 of v2 WM lift (regression sanity; v2 had WM-V1 = 0.05)
- ADDITIVE (best alpha) lift within +/-0.02 of v2 ADDITIVE lift (v2 had ADDITIVE-V1 = 0.05)
- COMBINED.cv across seeds < 0.10
- ORACLE - V1 >= 0.40 (pipeline still has headroom)

## HARD_FAIL (any one)

- COMBINED < V1 (combination FAILS like in v2)
- COMBINED < max(WM, ADDITIVE) (combination provides NO ADDITIVE VALUE)
- ORACLE - V1 < 0.20 (pipeline broken)

## MIDDLE_BAND

- COMBINED in [V1+0.03, V1+0.10) (modest combined lift; not chain-grade)

## Hardening (META_RULE_X / J / L1-L4 / AE / AF)

- L1: ASCII-only, no emojis/em-dashes
- L2: per-arm metrics in metrics["per_arm"][arm][seed][depth] (Fix #28 read directly)
- L3: outer try/except in main with except SystemExit: raise BEFORE except BaseException
- L4: import sentinel writes IMPORT_CRASH metrics.json on import failure
- META_RULE_AE: absolute paths in all citations (this prereg lives at d:/AI/hd-instrument/preregs/2026-06-27_pfc_goal_conditioned_gate_v3_wm_additive_only.md)
- META_RULE_AF: assert WM-arm output != ADDITIVE-arm output bit-identically (no parietal-REL silent-twin bug)
- RUN_MODE: --self-test / --smoke / HDLAB_EXP_NAME contains "_smoke" / HDLAB_RUN_MODE
- Resumable seeds via _seed_checkpoint module

## Route

remote_cpu_queue (per NO-EXPERIMENTS-LOCAL).

## Smoke gate

Smoke at N=8192, seeds=[7, 17], depths=[3, 6], 5 alphas for ADDITIVE.
- Smoke MUST FIRE discriminator (Wave 3A discipline): COMBINED arm must show measurable >0 lift over V1 in at least one alpha.
- If smoke HARD_PASS or MIDDLE_BAND -> dispatch FULL to remote_cpu_queue.
- If smoke HARD_FAIL -> report only; do NOT dispatch FULL.

## Smoke wall budget

Estimated: ~2-3 min per arm-seed-depth on N=8192. Total smoke units = 36. Total smoke wall ~5-15 min.
Full units = 90 with longer seed=5. Full wall estimate ~30-60 min.
Timeout: 5400s (1.5h) for full = 1.5 * smoke_wall_s * scaling

## Metrics path

data/exp_pfc_goal_conditioned_gate_v3_wm_additive_only/metrics.json (smoke variant suffix: _smoke).

## REQUIRED_FIELDS

anchor_name, verdict, verdict_msg, summary, elapsed_s, ts_iso, pid, run_mode,
config_version, per_arm, per_arm_summary, decision_depth, best_alpha,
combined_lift, oracle_headroom, combined_cv, cardinality_ok, expected_n_units,
completed_units.
