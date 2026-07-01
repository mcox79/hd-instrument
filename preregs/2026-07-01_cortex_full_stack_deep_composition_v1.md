# Prereg: cortex_full_stack_deep_composition_v1

**Anchor:** `cortex_full_stack_deep_composition_v1`
**Seeds:** 7, 13, 19 (chunked single-seed-per-cell per META §13)
**Route:** `remote_cpu_queue` (numpy CPU per M1.5/M1.6 pattern)
**Timeout:** 1800s per seed
**Date:** 2026-07-01
**Author:** hdi_exp_dev spawn (M3 Phase 1 validation)

## Motivation

M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15), M1.5 v2 TWOTIER context retention (Atom 18), and M1.6 v2 4-class router (Atom D) each cleared chain-grade INDIVIDUALLY. The M3 Phase 1 substrate-side router pattern claims these compose into a production-ready stack. Deep-composition has NOT been tested at chain depth > 5.

Substrate-KB check 2026-07-01 (via `bash tools/substrate_query.sh "cortex full stack composition depth 100 M1.4 M1.5 M1.6 refuse context router"`): top hit cosine=0.3057 from unrelated arcs (training-speed hierarchical / cross-modal). **Prior-work check: NONE at cosine>0.30 for THIS specific composition. Genuinely novel.**

## Functional Requirements (META §15E)

- **FR1**: Deep chain preserves entity identity across steps. Primitive: WM multi-bank K=100 STM (M1.5 v2 CG).
- **FR2**: OOD probes trigger refuse mid-chain without corrupting later steps. Primitive: CONFORMAL_MODERATE tau=P5 refuse-gate (M1.4 v8 CG).
- **FR3**: Router switches route-class per step correctly with tail-of-chain context. Primitive: 4-class nearest-class HV router (M1.6 v2 CG).
- **FR4**: Combined composition shows lift over any single-primitive ablation.

## Arms (5)

- `ARM_FULL_STACK_D10`: full cortex stack at chain depth 10.
- `ARM_FULL_STACK_D50`: full stack at depth 50.
- `ARM_FULL_STACK_D100`: full stack at depth 100. (FULL only; smoke skips.)
- `ARM_SUBSTRATE_ONLY_D50`: substrate bipolar primitives only (broken-PC baseline).
- `ARM_NO_REFUSE_D50`: cortex router + WM but NO refuse-gate at depth 50.

## Test Regimes (3)

1. `RETRIEVE_CHAIN`: chain of RETRIEVE steps (entity -> attribute -> relation).
2. `REFUSE_TERMINATED`: OOD probe injected at step ceil(depth/2); later steps route REFUSE.
3. `ROUTER_MIXED`: alternating route classes per step (RETRIEVE -> BIND -> MULTI_HOP -> RETRIEVE ...).

## Cardinality (META_RULE_H)

- **FULL**: 3 depths for FULL_STACK x 3 regimes + 2 ablation arms x 3 regimes = 15 arm-rows/seed.
- **SMOKE**: 2 depths for FULL_STACK x 2 regimes + 2 ablation arms x 2 regimes = 8 arm-rows.
- **EXPECTED_N_UNITS**: 15 (FULL); HF_CARDINALITY_BREACH if `observed < 13`.

## CRLB / Discriminator Reachability

- Chance floor = 1/V_CB = 1/1024 = 0.000977 THEORETICAL@codebook-argmax-uniform.
- Bernoulli sigma at p=0.5, N_TRIALS=10, depth=50: sqrt(0.25 / (10 * 50)) = 0.022. HP gap 0.15 = ~7 sigma. Reachable.
- At depth=100: HP=0.30, sigma_per_arm = sqrt(0.3*0.7/1000) = 0.014. Margin above chance = 0.30 = ~21 sigma. Reachable.
- `discriminator_reachability: true`.

## Discriminator-Must-Survive-Scale (META §DISCRIMINATOR)

- N_DIM=8192 in BOTH smoke and full (Check A path).
- Substrate bipolar bind survives ~10 compositions CITED@Kanerva-1988 before cosine < 0.30.
- Cleanup + refuse-gate should extend that to 50-100 (this is the tested claim).
- Depth axis IS the discriminator; HP thresholds decline with depth to reflect compounding noise.

## Effective vs Nominal Parameter Audit (META §15A)

- Swept params: depth (10, 50, 100); regime (RETRIEVE_CHAIN, REFUSE_TERMINATED, ROUTER_MIXED).
- No partition-routing masks depth for any primitive. Each primitive experiences the sweep parameter directly.
- `sweep_alignment_verdict: ALIGNED`.

## Bracket-Includes-Discriminating-Band (META §15B)

- Predicted mean-score per depth (HYPOTHESIZED@this prereg):
  - D=10: 0.85-0.95 (upper band)
  - D=50: 0.55-0.70 (discriminating band [0.30, 0.70])
  - D=100: 0.25-0.40 (discriminating band lower edge)
- Discriminating fraction (points in [0.30, 0.70]): 2/3 = 0.67 (>= 0.30 required). PASS.

## Signal Shape Compatibility (META §15C)

- Composition edges:
  - refuse_gate output (bool) -> router feature slot (int): SHAPE_MATCH (signal_slot_idx encoding).
  - router output (route str) -> STM/LTM primitive dispatcher: SHAPE_MATCH (route -> handler function).
  - STM output (val_idx int) -> next-step query key (HV): SHAPE_MATCH via codebook lookup.

## Positive Control (META §15D)

- ARM_FULL_STACK_D10 serves as positive control: at low depth (10), the composed stack SHOULD reproduce M1.4/M1.5/M1.6's individual chain-grade performance (aggregate accuracy >= 0.85). If FS_D10 < 0.75 at test regime, the composition is broken at even shallow depth AND downstream depth-50/100 arms are unreliable.
- Cited prior atoms:
  - M1.4 v8 CONFORMAL_MODERATE: ~0.700 empirical tau in-KB max_sim MEASURED@data/exp_substrate_refuse_gate_v8_conformal_v1_seed_7/metrics.json (Atom 15 seed_7)
  - M1.5 v2 TWOTIER: >= 0.80 top-1 codebook accuracy at K=500 turn-distance=5 MEASURED@data/exp_cortex_context_retention_v2_seed_7/metrics.json (Atom 18)
  - M1.6 v2 router: >= 0.85 route accuracy MEASURED@data/exp_cortex_attention_binding_router_v2_seed_7/metrics.json (Atom D)
- `regime_extension_audit: SHAPE_DRIFT_with_documented_risk` — this cell tests a NEW composition regime (chained depth-100) that no single prior atom tested. Downstream tolerance for extension risk: ARM_FULL_STACK_D10 must land >= 0.75 (else composition broken at floor; do NOT trust deep arms).

## HARD_PASS Gates (chain-grade if all fire)

Cross-seed (3 seeds, cv <5%) aggregated over regimes:

- **HP_D10_HOLDS**: `mean(ARM_FULL_STACK_D10)` >= 0.85 + 0.05*(1-0.85) = 0.8575 (META §L strict above floor)
- **HP_D50_HOLDS**: `mean(ARM_FULL_STACK_D50)` >= 0.60 + 0.05*(1-0.60) = 0.62
- **HP_D100_HOLDS** (FULL only): `mean(ARM_FULL_STACK_D100)` >= 0.30 + 0.05*(1-0.30) = 0.335
- **HP_LIFT_OVER_NO_REFUSE**: `FS_D50 - NO_REFUSE_D50` >= 0.15
- **HP_LIFT_OVER_SUBSTRATE_ONLY**: `FS_D50 - SUBSTRATE_ONLY_D50` >= 0.20

**HP_SCOPE per-arm declaration (META §15 5b):**
- HP_D10_HOLDS: applies to ARM_FULL_STACK_D10 only.
- HP_D50_HOLDS: applies to ARM_FULL_STACK_D50 only.
- HP_D100_HOLDS: applies to ARM_FULL_STACK_D100 only.
- HP_LIFT_OVER_NO_REFUSE: applies to pair (ARM_FULL_STACK_D50, ARM_NO_REFUSE_D50).
- HP_LIFT_OVER_SUBSTRATE_ONLY: applies to pair (ARM_FULL_STACK_D50, ARM_SUBSTRATE_ONLY_D50).
- ARM_SUBSTRATE_ONLY_D50 + ARM_NO_REFUSE_D50 do NOT inherit HP gates from FULL_STACK arms.

## HARD_FAIL Gates

- **HF_MECHANISM_DEATH**: any HP D10/D50/D100 misses floor by >= 0.15 (deep-composition wall found).
- **HF_ARMS_IDENTICAL** (META_RULE_AF).
- **HF_CARDINALITY_BREACH** (META_RULE_H): observed < 0.85 * expected.
- **HF_BROKEN_PC_BEATS_STACK**: ARM_SUBSTRATE_ONLY_D50 > ARM_FULL_STACK_D50 (cortex hurt the composition).

## MIDDLE_BAND

- Any HP misses by 0.05 to 0.15.

## Baseline-in-Band (META_RULE_AG)

- ARM_SUBSTRATE_ONLY_D50 expected in [0.05, 0.30] (broken-PC baseline; substrate bipolar bind degrades past ~10-15 compositions).
- Smoke check: `baseline_in_band` must be True (0.05 < s < 0.95).

## Calibration Check (META_RULE_M)

- `calibration_check: default_ok_for_this_regime`
- Chance floor derives from V_CB=1024 codebook (uniform-argmax = 1/V_CB = 0.000977). Discriminator margin at D=50 (HP=0.60 - chance=0.001 ~ 0.60) is well above adversarial floor.

## Composition Provenance (META_RULE_AT)

3 CG parents:
1. **M1.4 v8 CONFORMAL_MODERATE refuse-gate** (Atom 15; seed_7 metrics; tau=P5 of MODERATE cal in-KB ~0.700 empirical)
2. **M1.5 v2 TWOTIER context retention** (Atom 18; commit adaab6b7; K=100 STM multi-bank + K=1200 LTM dense-Hopfield alpha=0.1465 > 0.138 wall)
3. **M1.6 v2 4-class attention-binding router** (Atom D; nearest-class HV with refuse_signal + retrieval_signal + chain_signal feature slots)

## Defensive Error-Checking (§13)

- `cell_chunked: true` (3 sibling cells: seed_7, seed_13, seed_19)
- `start_marker_written: true` (main() first action)
- `crash_diagnostic_present: true` (Exception -> CELL_CRASHED + traceback via `_write_crash_metrics`; SystemExit + KeyboardInterrupt preserved)
- `heartbeat_present: true` (per-unit `_heartbeat.jsonl` append)
- `defensive_error_checking: passed_all_4_patterns`

## Atomicity + Run-Mode + Progress Logging

- `final_metrics_atomicity: tmp_replace` (META_RULE_AH)
- `progress_logging: print_flush_true + line_buffered_stdout` (META §17)
- Run-mode: cell parses `--smoke`/`--self-test`/`--mode` + env `HDLAB_RUN_MODE`; default `full`.

## Numbers Provenance (META_RULE_AC)

Every quantitative claim in the cell docstring + this prereg is tagged:
- MEASURED@ for values read from prior metrics.json files (M1.4/M1.5/M1.6 individual atoms cited).
- HYPOTHESIZED@ for pre-reg predictions (predicted mean-scores per depth).
- THEORETICAL@ for closed-form (chance floor, Bernoulli sigma).
- CITED@ for external (Kanerva-1988 for bipolar bind composition-depth wall).

## Post-Landing Actions

- Smoke lands: verify `run_mode == "smoke"`, `baseline_in_band == True`, `arms_differ_verified == True`. If discriminator doesn't fire (e.g., FS_D50 == SUBSTRATE_ONLY_D50), STOP and re-spec regime.
- Full lands: hdi_skunkworks landed-VET; classify chain-grade / MM / HF per gates above.
- If HARD_PASS: M3 Phase 1 architecture validated as composed stack; production-ready module. Atomize as `cortex_full_stack_deep_composition_v1` CG.
- If HARD_FAIL_MECHANISM_DEATH: find the depth wall; author v2 with revival mechanism (e.g., mid-chain SWR replay, tag-refresh, or partition-oracle).

## Dispatch

- Smoke (local): first pass to verify cell RUNS + arms differ. Local CPU (SMOKE ONLY per USER 2026-07-01).
- Full: remote_cpu_queue via hdi_orchestrator (needs push; harness-DENIED to exp_dev).
- Timeout: 1800s per seed.
- Cells:
  - `experiments/exp_cortex_full_stack_deep_composition_v1_seed_7.py`
  - `experiments/exp_cortex_full_stack_deep_composition_v1_seed_13.py`
  - `experiments/exp_cortex_full_stack_deep_composition_v1_seed_19.py`
