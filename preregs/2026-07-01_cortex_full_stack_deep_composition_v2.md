# Prereg: cortex_full_stack_deep_composition_v2

**Anchor:** `cortex_full_stack_deep_composition_v2`
**Seeds:** 7, 13, 19 (chunked)
**Route:** `remote_cpu_queue` (numpy CPU)
**Timeout:** 1800s per seed
**Date:** 2026-07-01
**Author:** hdi_exp_dev spawn (M3 Phase 1 validation, Option A: faithful M1.6)

## V2 Surgical Fix from v1

**v1 issue** (2026-07-01 smoke HARD_FAIL_BROKEN_PC_BEATS_STACK): used ORTHOGONAL RANDOM class-HVs for M1.6 router (no training signal). Router picked routes at ~0.25 chance, penalizing full-stack. SUBSTRATE_ONLY arm always predicted RETRIEVE (bypassed router) so it "won" on RETRIEVE_CHAIN. Result: FS_D10 = 0.15 (positive control BROKEN); SUB_ONLY = 0.75.

**v2 fix** (per Director spawn 2026-07-01): implement M1.6 v2's FAITHFUL class-HV training:
- N_TRAIN_PER_CLASS = 20 items per (route_class x regime)
- Class-HV = `bipolar_quantize(bundle([feature_hv(item) for item in train_items_of_class]))`
- Feature-HV = `bipolar_quantize(sum of bind(role, signal_slot) across refuse_role + retrieval_role + query_role + chain_role)`
- Signal codebook + role vectors fixed per seed
- Cross-reference: `exp_cortex_attention_binding_router_v2_seed_7.py:378-586` (M1.6 v2 Atom D CG)

**v2 additional**: chain-noise accumulation per step (~0.02 flip fraction/step) so depth actually degrades the discriminator (Not just decorative).

## Motivation (unchanged from v1)

M1.4 v8, M1.5 v2, M1.6 v2 each cleared chain-grade INDIVIDUALLY. M3 Phase 1 substrate-side router claims these compose. Deep-composition at depth 100+ untested. Substrate-KB check 2026-07-01: top hit cosine=0.3057 unrelated → novel.

## Functional Requirements (META §15E)

- FR1: Deep chain preserves entity identity. Primitive: M1.5 v2 STM K=100 multi-bank.
- FR2: OOD probes trigger refuse mid-chain. Primitive: M1.4 v8 CONFORMAL_MODERATE tau=P5.
- FR3: Router switches route-class per step (M1.6 v2 trained class-HVs).
- FR4: Combined composition shows lift over any single-primitive ablation.

## Arms (5), Regimes (3), Depths (3)

- ARM_FULL_STACK_{D10, D50, D100}: full cortex stack at chain depth d.
- ARM_SUBSTRATE_ONLY_D50: substrate primitives only (no router discrimination; predicts RETRIEVE always).
- ARM_NO_REFUSE_D50: trained router + WM but refuse-gate DISABLED.

Regimes: RETRIEVE_CHAIN, REFUSE_TERMINATED, ROUTER_MIXED.

## Cardinality

- FULL: 3 depths x 3 regimes (FULL_STACK) + 2 arms x 3 regimes = 15 rows/seed.
- SMOKE: 2 depths x 2 regimes (FULL_STACK) + 2 arms x 2 regimes = 8 rows.
- HF_CARDINALITY_BREACH if observed < 13 (FULL).

## HARD_PASS Gates

- HP_D10_HOLDS: mean(FULL_STACK_D10 across regimes) >= 0.8575 (META §L strict above 0.85)
- HP_D50_HOLDS: mean(FULL_STACK_D50) >= 0.62
- HP_D100_HOLDS: mean(FULL_STACK_D100) >= 0.335 (FULL only)
- HP_LIFT_OVER_NO_REFUSE: FS_D50 - NO_REFUSE_D50 >= 0.15
- HP_LIFT_OVER_SUBSTRATE_ONLY: FS_D50 - SUBSTRATE_ONLY_D50 >= 0.20

## HARD_FAIL Gates

- HF_MECHANISM_DEATH: any HP D10/D50/D100 misses by >= 0.15
- HF_ARMS_IDENTICAL (META_RULE_AF)
- HF_CARDINALITY_BREACH (META_RULE_H)
- HF_BROKEN_PC_BEATS_STACK: SUB_ONLY > FS_D50

## Composition Provenance (META_RULE_AT)

1. M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15)
2. M1.5 v2 TWOTIER context retention (Atom 18; commit adaab6b7)
3. M1.6 v2 4-class router with FAITHFUL trained class-HVs (Atom D)

## Defensive Error-Checking (§13)

- cell_chunked: true (3 sibling seeds)
- start_marker_written: true
- crash_diagnostic_present: true (SystemExit + KeyboardInterrupt preserved)
- heartbeat_present: true
- defensive_error_checking: passed_all_4_patterns

## Atomicity + Run-Mode

- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- progress_logging: print_flush_true + line_buffered_stdout (META §17)

## Post-Landing

- Smoke lands: verify run_mode == "smoke", baseline_in_band, arms_differ_verified.
- Full lands: hdi_skunkworks landed-VET; classify chain-grade / MM / HF per gates.
- If HARD_PASS: M3 Phase 1 architecture validated. Atomize as CG.
- If MIDDLE_BAND: characterize which HP misses; may indicate composition saturates at N=8192.

## Cells

- `experiments/exp_cortex_full_stack_deep_composition_v2_seed_7.py`
- `experiments/exp_cortex_full_stack_deep_composition_v2_seed_13.py`
- `experiments/exp_cortex_full_stack_deep_composition_v2_seed_19.py`
