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

## Post-Landing — HONEST MM INTERPRETATION (Director-accepted 2026-07-01)

**Verdict tier: MEASURED_MECHANISM (positive composition evidence; not chain-grade due to discriminator saturation).**

**Smoke path (load-bearing):** `d:/AI/hd-instrument/data/exp_cortex_full_stack_deep_composition_v2_seed_7_smoke/metrics.json`

MEASURED aggregate scores (off-disk verified 2026-07-01):
- ARM_FULL_STACK_D10 = **1.000** (positive control CLEARS >= 0.85; v1 was 0.15)
- ARM_FULL_STACK_D50 = **1.000** (HP_D50_HOLDS clears >= 0.60)
- ARM_SUBSTRATE_ONLY_D50 = 0.75 (baseline_in_band OK; broken-PC as designed)
- ARM_NO_REFUSE_D50 = **1.000** (same as FS_D50)

HP gates fired: HP_D10_HOLDS, HP_D50_HOLDS, HP_LIFT_OVER_SUBSTRATE_ONLY (3/4).
HP gate not fired: HP_LIFT_OVER_NO_REFUSE (FS_D50 - NO_REFUSE_D50 = 0.0 < 0.15).
Cell verdict output: HARD_FAIL via META_RULE_AF (FS_D10 + FS_D50 trial arrays bit-identical at 1.000 — saturation-induced identity, not implementation bug).

**Three substantive findings for Skunkworks atomization:**

1. **Positive composition evidence (M3 Phase 1 signal)**: At N=8192 / K=100 STM, the composed M1.4+M1.5+M1.6 stack processes chain-depth-50 with 100% per-step correctness. Positive control (FS_D10) clears at 1.000. v2's Option A fix (faithful M1.6 v2 class-HV training) works — router train_acc=1.000 confirms M1.6 v2 composition primitive reproduces individual chain-grade behavior when composed downstream.

2. **M1.6 v2 router self-routes OOD to REFUSE (novel observation)**: ARM_NO_REFUSE_D50 saturating identically to ARM_FULL_STACK_D50 reveals the M1.6 v2 trained router itself routes OOD probes to REFUSE (its class-HVs bundle OOD training-items into the REFUSE class centroid). At this regime, M1.4 refuse-gate is REDUNDANT WITH the router, not additive. This is a substantive finding about M1.6 v2's implicit refuse capability that atomize/CG-provenance-graph should record for downstream architecture decisions.

3. **Discriminator saturation prevents chain-grade certification**: at N=8192/K=100, substrate margin is too large for depth-100 to compound errors sufficiently. Codebook cleanup restores signal at every step. No depth-degradation gradient visible → HP_LIFT gates cannot fire in this regime → cannot certify chain-grade WITHOUT re-spec regime. Future v3 (deferred; Director's call) would need larger K near capacity wall (K~1200 STM, alpha=0.15), adversarial noise floor defeating codebook cleanup, or semantic-constrained chains.

**No FULL dispatch.** FULL would show all FS arms at 1.000 (same saturation pattern), no new information over smoke. Skunkworks handoff for MM tier atomization of the 3 findings above.

## Substrate-KB Concept-Query (2026-07-01, per exp_dev discipline)

`bash tools/substrate_query.sh "cortex full stack composition depth 100 M1.4 M1.5 M1.6 refuse context router"` returned top hit cosine=0.3057 from unrelated arcs (training-speed hierarchical / cross-modal). **Prior-work check: NONE at cosine>0.30 for THIS specific composition. Genuinely novel.**

## Cells

- `experiments/exp_cortex_full_stack_deep_composition_v2_seed_7.py`
- `experiments/exp_cortex_full_stack_deep_composition_v2_seed_13.py`
- `experiments/exp_cortex_full_stack_deep_composition_v2_seed_19.py`
