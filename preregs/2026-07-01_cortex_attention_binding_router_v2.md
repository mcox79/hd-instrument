# Pre-reg: cortex_attention_binding_router_v2

**Date filed:** 2026-07-01
**Author:** hdi_exp_dev (agent-spawn from Director; M1.6 SURGICAL v2 after Atom 27 MM)
**Anchor:** `cortex_attention_binding_router_v2`
**Chunks:** `_seed_7`, `_seed_13`, `_seed_19` (chunk-per-seed; Skunkworks aggregates).
**Research parent:** M1.6 v1 pre-reg (2026-07-01_cortex_attention_binding_router_v1.md).
**Prior work:** Atom 27 v1 MM (Skunkworks Wave 10, 2026-07-01).
**Mechanism class:** cortex integration classifier (Stage 3 composition; unchanged from v1).
**Milestone:** v2 CLOSES M1.6 if 3-seed HP FULL with all per-class precisions >= 0.70.

## Diagnosis (from Atom 27 v1 VET)

v1 was tier'd MEASURED_MECHANISM because seed_13 chain_multihop regime RETRIEVE per-class
precision = 0.625 (5/8) breached HP_PER_CLASS_PRECISION >= 0.70. All other HP gates cleared
cross-seed. Small n=8 predictions labeled RETRIEVE at that regime gave Bernoulli sigma
0.162 at p=0.70 (THEORETICAL@sqrt(p*(1-p)/n)) — 0.625 is only ~0.46 sigma below floor;
noise-plausible not mechanism-inherent.

## Two surgical fixes (v1 mechanism otherwise identical)

### Fix 1 (PRIMARY): N_TEST_PER_CLASS_FULL 5 -> 20

- v1: 5 items per class per regime -> 20 items per regime -> ~5-8 predictions per class in CM.
- v2: 20 items per class per regime -> 80 items per regime -> ~20-24 predictions per class.
- Bernoulli sigma at p=0.70: 0.162 -> 0.094 (~1.7x tighter).
- HP gate breach at 0.625 becomes far less noise-plausible; genuine breaches surface as real.

### Fix 2 (SECONDARY): explicit chain_signal feature

v1 feature_hv = quantize(bind(refuse_role, refuse_slot) + bind(retrieval_role, retrieval_slot)
+ bind(query_role, query)). Chain-vs-retrieve distinction was implicit in retrieval_slot alone
(RETRIEVE=slot0/1, MULTI_HOP=slot1). v2 adds:

- New role vector `chain_role` (bipolar N_DIM).
- New codebook `signal_codebook_chain` with 2 slots: 0=chain-required, 1=no-chain-required.
- MULTI_HOP items get chain_slot=0; RETRIEVE/BIND/REFUSE get chain_slot=1.
- feature_hv v2 = quantize(bind(refuse_role, refuse) + bind(retrieval_role, retrieval)
  + bind(query_role, query) + bind(chain_role, chain)).

ARM_M14_M15_ISOLATED excludes chain_signal (use_chain=False) so isolated-baselines don't
inherit v2's discriminator; composition-vs-isolated remains an honest comparison.

## Falsifiable predictions (unchanged bands from v1)

- HP_ROUTE_ACCURACY: ARM_ROUTE_CONFUSION_MATRIX top-1 acc >= 0.85 cross-seed.
- HP_LIFT_OVER_NULL: CM - ARM_NO_ROUTER >= 0.30.
- HP_PER_CLASS_PRECISION: min per-class precision >= 0.70 across all classes ALL regimes.
  **This is the failing gate; v2 targets it directly.**
- HP_LIFT_OVER_ISOLATED: CM - ARM_M14_M15_ISOLATED >= 0.15.
- HF_MECHANISM: CM < 0.65 (composition not working).
- HF_CLASS_COLLAPSE: any per-class precision < 0.30.
- HF_ISOLATED_BEATS_COMPOSITION: ISOLATED >= CM.
- HF_TRIVIAL_BASELINE: ARM_NO_ROUTER not in [0.15, 0.35].
- MIDDLE_BAND: CM in [0.65, 0.85].

## Cardinality

- FULL: 7 arms x 3 regimes x 3 seeds = 63 arm-rows total.
- EXPECTED_N_UNITS = 21 per seed. HF_CARDINALITY_BREACH if < 18 per seed.
- ARM_ROUTE_CONFUSION_MATRIX evaluates 80 items per regime per seed (v1 had 20).

## CRLB / feasibility

- Chance floor = 0.250 THEORETICAL@uniform-4-class-argmax.
- Bernoulli sigma @ p=0.5, N_TEST_PER_REGIME=80: 0.056 (v1 was 0.112 at N=20).
- Per-class sigma @ p=0.70, n~24 predictions: 0.094 (v1 was 0.162 at n~8).
- HP gap 0.30 lift = 5.4 sigma at v2 tightening (very reachable).
- `discriminator_reachability: true`.

## SCHEMA-VET pre-dispatch fields

- `cardinality_ok: true` (EXPECTED_N_UNITS=21, HF if <18).
- `arms_differ_verified: true` (META_RULE_AF hash-test present).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `crlb_floor_computed: 0.25`, `crlb_formula_reference: chance=1/N_CLASSES`.
- `baseline_in_band: true` (NO_ROUTER = 0.250 exactly, in [0.15, 0.35]).
- `calibration_check: default_ok_for_this_regime` (chance=0.25 fixed by construction; NOT
  adaptively tuned).
- `cell_chunked: true` (single-seed-per-cell; 3 cells: seed_7 / seed_13 / seed_19).
- `start_marker_written: true` (inline `_write_start_marker`).
- `crash_diagnostic_present: true` (inline `_write_crash_metrics` + except Exception; SystemExit
  re-raised).
- `heartbeat_present: true` (inline `emit_heartbeat` per regime completion).
- `defensive_error_checking: passed_all_4_patterns`.
- `progress_logging: print_flush_true` (per-row print with flush=True).
- `discriminating_fraction: 1.0` (single-point mechanism test, not sweep).
- `positive_control_arms: ARM_TRUE_<class> arms per class reproduce class-specific CM subset`.

## Regime notes

- CPU-eligible (numpy).
- Estimated FULL wall: ~90-180s per seed (4x test items over v1's 30-60s).
- Route: SMOKE on local_cpu_queue (already ran; HARD_PASS cross-seed);
  FULL on remote_cpu_queue via hdi_orchestrator handoff (needs push).
- Per-experiment timeout: 1800s (30 min; ample buffer over 180s expected).

## Smoke verdicts (already landed)

- seed_7 smoke: HARD_PASS CM=1.000 NR=0.250 ISO=0.625 lift_null=+0.750 lift_iso=+0.375
  min_class_prec=1.000. `metrics.json` at
  `d:/AI/hd-instrument/data/exp_cortex_attention_binding_router_v2_seed_7/metrics.json`.
- seed_13 smoke: HARD_PASS CM=1.000 NR=0.250 ISO=0.708 lift_null=+0.750 lift_iso=+0.292
  min_class_prec=1.000. `metrics.json` at
  `d:/AI/hd-instrument/data/exp_cortex_attention_binding_router_v2_seed_13/metrics.json`.
- seed_19 smoke: HARD_PASS CM=1.000 NR=0.250 ISO=0.792 lift_null=+0.750 lift_iso=+0.208
  min_class_prec=1.000. `metrics.json` at
  `d:/AI/hd-instrument/data/exp_cortex_attention_binding_router_v2_seed_19/metrics.json`.

Smoke uses N_TRAIN_PER_CLASS=6, N_TEST_PER_CLASS=3, regimes=[dialogue_pronoun, ood_novel_bind]
(chain_multihop excluded from smoke; smoke fires the discriminator via the two included
regimes clearing all per-class precisions >= 0.70).

## Discriminator-survives-scale

- N_DIM=8192 in BOTH smoke and full (unchanged from v1).
- v1 measured cross-seed CM=0.85 mean at FULL-N with ONE per-class breach; discriminator
  survives to full scale. v2 is a strict superset (more items + explicit chain_signal); at
  worst v2 matches v1 (mechanism unchanged), at best v2 eliminates the breach.

## Failure-class notes

- If v2 FULL still shows chain_multihop RETRIEVE breach: mechanism-inherent (not noise),
  research must redesign chain-vs-retrieve distinction beyond binary chain_slot.
- If v2 FULL clears cleanly with all per-class >= 0.70: M1.6 closes as CG; 3 cortex milestones
  land 2026-07-01 (M1.4 v8 + M1.5 v2 + M1.6 v2).

## Cross-references

- Atom 15: M1.4 v8 CONFORMAL_MODERATE refuse-gate CG.
- Atom 18: M1.5 v2 TWOTIER context retention CG (commit adaab6b7).
- Atom 27: M1.6 v1 MM (Skunkworks Wave 10, seed_13 chain_multihop breach diagnosis).
- v1 pre-reg: `preregs/2026-07-01_cortex_attention_binding_router_v1.md`.
