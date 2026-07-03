# Pre-reg: Stage 1 Regime Probe 9 — N (SCALE) x TOPOLOGY (F fan-out) at cliff-adjacent

Cell anchor: `stage1_regime_probe_9_N_x_topology_non_saturated_v1`
Core:  `experiments/_stage1_regime_probe_9_N_x_topology_non_saturated_v1_core.py`
Sibling: `experiments/exp_stage1_regime_probe_9_N_x_topology_non_saturated_v1_s7.py` (s13/s19 to follow)
Date: 2026-07-03
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER 2026-07-03). Ninth probe.

## Purpose

First NON-MECHANISM axis pair on the revised regime map. Prior probes (2,3,6,7)
held one of N or F while varying CLEANUP_MECHANISM; probes 4,5 pair STORAGE
with N and F respectively. N x F is virgin regime-map territory.

Tests: at cliff-adjacent regime, are there cross-terms between the two
non-mechanism axes themselves? Concretely: does N moderate the effect of
TOPOLOGY on capacity (or vice versa)? MECHANISM is held constant =
modern_hopfield (best-performer per Probe 6 v2 F=1) to isolate the N x F
interaction cleanly.

USER standing directive (2026-07-02): "if there is design space to map, we
should 100% do that." N x F is unmapped regime map territory.

## Design constraints (empirically pre-validated by Probes 6+7 v2)

- SHARDED FHRR chain composition regime (Probe 6+7 v2 template).
- Cliff-adjacent operating point per Director spec: M=6400, corr=0.85, L=4.
- N axis spans below and above cliff position: {256, 512, 1024, 2048}.
- TOPOLOGY axis (F fan-out): {1, 4, 8, 16} — matches Probe 6 F grid.
- Fixed: mechanism=modern_hopfield, F(PC)=1 for Gate D.
- Plate 0.14 bound is NOT used (per `feedback_plate_bound_too_pessimistic_for_
  sharded_fhrr_chain_composition_2026-07-03.md`); cliff bracketed empirically.

## Hypotheses (falsifiable; band-restricted)

Discriminator restricted to slices with per-slice mean(acc) in [0.30, 0.95].

**H1 (cliff-adjacent shows N x TOPOLOGY cross-term):**
- max_topology_var_at_N_in_band >= 0.10 (max across-F acc-spread at any N)
- OR max_N_var_at_F_in_band >= 0.10 (max across-N acc-spread at any F)
- OR max_N_x_F_deviation_in_band >= 0.10 (max abs additive-model residual)
- -> N and TOPOLOGY have joint (non-additive) effect at cliff-adjacent regime.

**H2 (null: axes independent):**
- max_topology_var_at_N_in_band < 0.05
- AND max_N_var_at_F_in_band < 0.05
- AND max_N_x_F_deviation_in_band < 0.05
- -> Each axis has same marginal effect regardless of the other.
- Strengthens regime map ORTHOGONAL_AXES thesis (interactions concentrated
  on MECHANISM-anchored pairs only).

**H3 (deep-saturation null control):**
- at CEILING regime (N=8192, corr=0.60, across F in {1,4,8,16}),
  topology_var_across_F <= 0.03
- -> at ceiling, TOPOLOGY has no measurable effect; positive-null control
  confirms discriminator returns null under saturation-vacuous conditions.
- If H3 FAILS (var > 0.03 at CEILING), a positive H1 result is suspect
  (may be measurement artifact rather than genuine cliff-adjacent cross-term).

## Grid (cardinality)

**FULL (21 pts / seed):**
- Main: 4 N x 4 F x 1 mech x 1 M x 1 L x 1 corr = 16 SHARDED main pts
- SATURATION_PC arm: 1 pt (Gate D reproducer; modern_hopfield SHARDED F=1 M=800 N=2048 L=4 corr=0.20)
- CEILING_H3 arm: 4 pts (across F at N=8192 corr=0.60)
- Total: 16 + 1 + 4 = 21

**SMOKE (5 pts / seed):**
- Main: 2 N (endpoints {256, 2048}) x 2 F (endpoints {1, 16}) = 4
- SATURATION_PC arm: 1 (CEILING skipped in smoke)
- Total: 4 + 1 = 5

CARDINALITY_OK gate: verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`
if observed != expected.

## Fixed hyperparameters

| Param   | Value              | Justification                                       |
|---------|--------------------|-----------------------------------------------------|
| MECH    | modern_hopfield    | Best-performer at F=1 per Probe 6 v2 (Director spec)|
| STORAGE | SHARDED            | Compositional cell; META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW |
| M       | 6400               | Cliff-adjacent per Director spec                    |
| L       | 4                  | Mid-band chain depth per Director spec              |
| corr    | 0.85               | Cliff-adjacent per Director spec (matches Probe 6 v2 non-saturated) |
| TR_FULL | 100                | Queries per point (statistical stability)           |
| TR_SMOKE| 40                 | Faster smoke                                        |
| BETA    | 8.0                | Modern Hopfield inverse temperature (inherited)     |
| ALPHA_SOFT | 0.5             | Soft attractor mix (inherited; N/A here)            |

## Verdict routing (band-restricted, in-order gates)

1. `cardinality_ok` (META_RULE_H) — else `HARD_FAIL_CARDINALITY_BREACH`
2. `arms_differ_verified` (META_RULE_AF) — F-axis endpoints hash-distinct at
   each N; else `HARD_FAIL_ARMS_MUST_DIFFER`
3. `saturation_pc.pass` (Gate D) — else `HARD_FAIL_SATURATION_PC_MISMATCH`
4. `escapes_saturation_ceiling_full` — fraction in [0.30, 0.95] >= 0.30;
   else `MIDDLE_BAND_ESCAPES_SATURATION_FAIL`
5. Hypothesis routing (H1 / H2 / MIDDLE_BAND) + H3 CEILING pass/fail
   annotation in verdict_msg (H3 fail does NOT downgrade verdict but flags
   the H1 claim as suspect).

## HP_SCOPE per-arm declaration

| Arm            | HP gates applied                                    |
|----------------|-----------------------------------------------------|
| SHARDED_main   | escapes_saturation_ceiling_full + H1/H2 discriminator |
| SATURATION_PC  | Gate D reproducer (PC_THRESHOLD >= 0.95 at TR=100) |
| CEILING_H3     | Deep-saturation null control (topology_var <= 0.03)|

## SCHEMA-VET checklist

- `cardinality_ok`: TRUE (21 FULL / 5 SMOKE gated)
- `arms_differ_verified`: TRUE (F-axis endpoints hash-distinct per N)
- `arms_differ_exempted`: []
- `final_metrics_atomicity`: "tmp_replace" (see cell wrapper)
- `crlb_n/a`: "categorical accuracy; discriminator is band-restricted spread"
- `discriminator_reachability`: TRUE (H1 threshold 0.10 is in-band achievable
  per Probe 6 non-saturated topology variance evidence)
- `baseline_in_band`: SATURATION_PC = 0.95+ (in-band-adjacent by design as
  reproducer); CEILING_H3 = 0.95+ (deliberately saturating null control)
- `sweep_alignment_verdict`: ALIGNED (N and F sweep separately; oracle
  primitives natively parameterized by N and F; no partition-routing
  confound)
- `discriminating_fraction`: HYPOTHESIZED@this-prereg: at least 4/16 main
  pts predicted to land in [0.30, 0.95] band at cliff-adjacent corr=0.85
  (based on Probe 6 corr=0.85 M=6400 evidence). Actual fraction verified in
  smoke + FULL.
- `composition_edges`: SHAPE_MATCH (SHARDED chain composition unchanged from
  Probe 6/7 v2)
- `positive_control_arms`: SATURATION_PC (Gate D) + CEILING_H3 (H3 null control)
- `functional_requirements`: N and TOPOLOGY cross-term at cliff-adjacent
  regime; matched to existing SHARDED FHRR chain composition primitive
- `calibration_check`: "default_ok_for_this_regime" (BETA=8.0 inherited from
  Probe 6 non-saturated at same modern_hopfield; empirical variance evidence
  from Probe 6 confirms discriminator range is measurable)
- `cell_chunked`: TRUE (per-seed sibling files; s7/s13/s19)
- `start_marker_written`: TRUE
- `crash_diagnostic_present`: TRUE
- `heartbeat_present`: TRUE (per-phase-point flush print)
- `defensive_error_checking`: "passed_all_4_patterns"
- `progress_logging`: "print_flush_true" (all progress lines flush=True)
- `progress_cadence_expected_s`: 60 (per-point wall < 60s on CPU at N=2048 M=6400)
- `run_mode_verified_post_dispatch`: mandatory (§16); verify metrics.json
  landed run_mode == "smoke" for smoke dispatch

## Discriminator predictions (HYPOTHESIZED @ this-prereg)

- At cliff-adjacent (SHARDED, modern_hopfield, M=6400, L=4, corr=0.85), we
  expect per-N mean acc to span from ~0.30 (N=256) to ~0.95 (N=2048).
- If TOPOLOGY axis interacts with N (H1): F=1 (single-slot) at low N should
  suffer more than F=16 (multi-slot voting), producing acc-spread > 0.10 at
  N=256; at N=2048 all F should saturate and spread ~ 0.
- If TOPOLOGY axis is independent (H2): all F values track the same N-curve
  with parallel shifts < 0.05.
- At CEILING (N=8192 corr=0.60), all F should saturate at acc >= 0.95 with
  topology_var <= 0.03 (H3 positive-null-control).

## Cited source atoms (exact names; META_RULE_AC)

- `META_saturation_floor_masks_null_variance_probe3_lesson`
  (T4 MM_STANDARD 2026-07-03)
- `MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1`
  (Probe 1 template)
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1`
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1`
  (SHARDED-vs-BUNDLED)
- `regime_probe_6_topology_x_cleanup_non_saturated_v1_MECH_F1_MODERN_HOPFIELD_BEST`
  (Probe 6 v2 evidence for MECH_FIXED choice)
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian`
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`
- `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`
- `feedback_experiment_bias_master_checklist_USER_2026-06-24`
- `feedback_cardinality_ok_mandatory_prereg_field_for_sweep_axis_cells_2026-06-26`

## Dispatch plan

- SMOKE: local_cpu_queue (SMOKE only per USER-LOCKED 2026-07-01);
  s7 first, s13/s19 held for FULL.
- FULL: NOT DISPATCHED IN THIS CYCLE (Tailscale down blocks remote GPU per
  Director spec). Files committed; FULL dispatch pending Tailscale + USER
  push authorization.

## Independence from Probe 8

Probe 8 authoring in parallel — different anchor, different files. No shared
file conflicts.
