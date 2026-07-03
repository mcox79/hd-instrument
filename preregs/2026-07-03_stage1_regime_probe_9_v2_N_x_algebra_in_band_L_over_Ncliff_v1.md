# Pre-reg: Stage 1 Regime Probe 9 v2 — N (SCALE) x ALGEBRA (chain-depth L) at BUNDLED near-capacity

Cell anchor: `stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1`
Core:   `experiments/_stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1_core.py`
Sibling: `experiments/exp_stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1_s7.py` (s13/s19 to follow for FULL)
Date: 2026-07-03
Arc: Stage 1 REGIME MAP; Research 2x-drill NEG1 cheap-decisive-test follow-up.

## Purpose

Probe 9 v1 (2026-07-03 earlier) tested N x TOPOLOGY at SHARDED and passed SMOKE.
Independently, Skunkworks VET on a broader 4-negative regime drill (see
`notes/research_stage1_regime_map_4negatives_2026-07-03.md`) flagged that a
prior test of N x depth-L had used only N=256 (floor) and N=2048 (ceiling)
endpoints — cross-term=0 was TRIVIALLY TRUE because both endpoints pinned
(saturation-vacuous framing). Plate 1995 predicts separability far from
capacity; Frady/Sommer 2018/2020 predict cross-term emerges NEAR-CAPACITY as
L approaches a threshold fraction of N_cliff.

Research authority explicitly identifies NEG1 as the ONLY of 4 negatives
where 40-70yr theory does NOT already predict today's specific result:

> "NEG1 (N x depth cross-term) requires an in-band follow-up cell because
> the prior test sat at saturation extremes, not the theoretically
> interesting crossover zone."

This v2 targets the theoretically-interesting crossover zone using L/N_cliff
bucketing as directed by Research.

## Design constraints (empirically bracketed 2026-07-03)

- STORAGE=BUNDLED (per Research: theory predicts cross-term at BUNDLED near
  capacity; SHARDED has arbitrary-depth prior finding suggesting no coupling
  per `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`).
- MECH=modern_hopfield (theory-predicted first-order transition; matches Probe 10 arm).
- N_cliff empirically bracketed via `bracket_scout2` + `bracket_verify`
  (in scratchpad, MEASURED@2026-07-03): BUNDLED modern_hopfield near-capacity
  regime is (N=2048, M=10, F=1, corr=0.10). At M=10, per-cell mean acc at
  3-seed TR=100 lands in [0.30, 0.95] band for 7/12 cells across N x L grid.
- N grid: {1024, 2048, 4096} = {0.5x, 1x, 2x} N_cliff.
- L grid: {2, 4, 8, 16} per Research spec.
- Fixed: M=10, F=1, corr=0.10 (BUNDLED near-capacity operating point).
- Plate 0.14 bound NOT relied on (per feedback_plate_bound_too_pessimistic);
  bracket verified EMPIRICALLY at 3 seeds TR=100.

## Source signature (MECHANISM_ABSTRACTION_LOSSY per feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03)

`(STORAGE=BUNDLED, MECH=modern_hopfield, N_cliff=2048, M=10, F=1, corr=0.10, TR=100)`

Bracket verification result MEASURED@bracket_verify 2026-07-03 (3 seeds TR=100):
- (N=1024, L=2)  mean acc = 0.367
- (N=1024, L=4)  mean acc = 0.473
- (N=1024, L=8)  mean acc = 0.650 (in-band, NON-MONOTONIC RISING with L)
- (N=1024, L=16) mean acc = 0.587 (in-band)
- (N=2048, L=2)  mean acc = 0.297 (floor-adjacent)
- (N=2048, L=16) mean acc = 0.300
- (N=4096, L=2)  mean acc = 0.503 (in-band)
- (N=4096, L=8)  mean acc = 0.400 (in-band)
- max|additive-model residual|_in_band = 0.162 (already at/above H1 top-bucket
  threshold 0.15 in bracket).

Prior-work check (SUBSTRATE-KB CONCEPT-QUERY per USER-LOCKED 2026-07-01):
`bash tools/substrate_query.sh "N x algebra chain depth L cross term modern hopfield BUNDLED near capacity cliff"`
Top hit cosine=0.36 = `Modern Hopfield + capacity` (general reference in
`notes/research_BetX_skill_composition_2026-05-21.md`); NO prior atom
specifically on N x algebra cross-term at BUNDLED near-capacity. Cell is
GENUINELY NOVEL, matching Research NEG1 assessment ("only of 4 negatives
where 40-70yr theory does NOT already predict result").

## Hypotheses (falsifiable; band-restricted; L/N_cliff bucketed)

**Bucketing:** Cell "compositional pressure" p(N,L) = L * (N_cliff / N).
High L or small N -> high pressure. In-band cells split by median pressure
into LOW and HIGH pressure buckets.

**H1 (BUNDLED near-capacity N x L cross-term, per Frady/Sommer):**
- max|additive-model residual| in HIGH_bucket in-band >= 0.15
- AND max|additive-model residual| in LOW_bucket in-band < 0.05
- -> confirms Frady/Sommer near-capacity coupling literature; N and L are
  NON-additive at BUNDLED near-capacity; cross-term > 0 near cliff.

**H1_ALT (diffuse cross-term, weaker signal):**
- overall_max|dev|_in_band >= 0.10
- (but clean bucket separation NOT achieved)
- -> MM_TENTATIVE weak N x L coupling.

**H2 (null: N and L independent — NOVEL substrate-specific counter-finding):**
- overall_max|dev|_in_band < 0.05
- -> NOVEL substrate-specific finding CONTRADICTING Frady/Sommer near-capacity
  coupling literature; consistent with per-step cleanup resetting noise
  (analog to prior-arc SHARDED arbitrary-depth finding); would be a
  publishable substrate-signal per Research NEG1 framing.

**H3 (deep-saturation null control):**
- at DEEP_SAT arm (BUNDLED modern_hopfield, N=8192, M=100, corr=0.60,
  L in {2,4,8,16}), L-spread <= 0.10 AND mean_acc >= 0.95
- -> mechanism DEGENERATES at ceiling; no cross-term visible; positive null.

**H4 (SATURATION_PC / Gate D reproducer):**
- at PC arm (SHARDED modern_hopfield M=800, N=2048, F=1, L=4, corr=0.20),
  acc >= 0.95
- -> primitive invocation reproduces prior chain-grade evidence; downstream
  cross-term claim trustworthy.

## Grid (cardinality)

**FULL (17 pts / seed):**
- BUNDLED_main: 3 N x 4 L x 1 mech x 1 M x 1 F x 1 corr = 12 pts
- SATURATION_PC arm: 1 pt (Gate D; SHARDED modern_hopfield reproducer)
- DEEP_SAT arm: 4 pts (BUNDLED modern_hopfield, N=8192, M=100, corr=0.60,
  L in {2,4,8,16})
- Total: 12 + 1 + 4 = 17

**SMOKE (5 pts / seed):**
- BUNDLED_main: 2 N (endpoints {1024, 4096}) x 2 L (endpoints {2, 16}) = 4
- SATURATION_PC arm: 1 (DEEP_SAT skipped in smoke)
- Total: 4 + 1 = 5

CARDINALITY_OK gate: verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`
if observed != expected.

## Fixed hyperparameters

| Param   | Value              | Justification                                    |
|---------|--------------------|--------------------------------------------------|
| MECH    | modern_hopfield    | Per Research spec: theory-predicted 1st-order transition |
| STORAGE | BUNDLED            | Per Research spec: shared-vector crosstalk -> near-capacity coupling |
| M       | 10                 | BUNDLED near-capacity MEASURED@bracket_scout2   |
| F       | 1                  | Per Research spec: no fan-out confound in ALGEBRA sweep |
| corr    | 0.10               | BUNDLED near-capacity MEASURED@bracket_scout2   |
| N_cliff | 2048               | BUNDLED cliff MEASURED@bracket_scout2 + bracket_verify |
| TR_FULL | 100                | Statistical stability per bracket_verify         |
| TR_SMOKE| 40                 | Faster smoke                                     |
| BETA    | 8.0                | Modern Hopfield inverse temperature (inherited)  |
| ALPHA_SOFT | 0.5             | Soft attractor mix (inherited; N/A here)         |

## Verdict routing (band-restricted, in-order gates)

1. `cardinality_ok` (META_RULE_H) -> else HARD_FAIL_CARDINALITY_BREACH
2. `arms_differ_verified` (META_RULE_AF; L-axis endpoints hash-distinct per N)
   -> else HARD_FAIL_ARMS_MUST_DIFFER
3. `saturation_pc.pass` (Gate D) -> else HARD_FAIL_SATURATION_PC_MISMATCH
4. `escapes_saturation_ceiling_full` (fraction >= 0.30 in-band)
   -> else MIDDLE_BAND_ESCAPES_SATURATION_FAIL
5. Hypothesis routing (H1 / H1_ALT / H2 / MIDDLE_BAND) + H3 DEEP_SAT annotation

## HP_SCOPE per-arm declaration

| Arm            | HP gates applied                                    |
|----------------|-----------------------------------------------------|
| BUNDLED_main   | escapes_saturation_ceiling_full + H1/H1_ALT/H2 discriminator |
| SATURATION_PC  | Gate D reproducer (PC_THRESHOLD >= 0.95 at TR=100) |
| DEEP_SAT       | H3 null control (L_spread <= 0.10 AND mean_acc >= 0.95) |

## Compute architecture

CLASS: **sequential-CPU with justification**
- BUNDLED modern_hopfield at M=10 F=1 N in {1024,2048,4096} is O(M*N) per step
  = 10 * 4096 = 40960 floats per matmul; each phase point < 1s CPU
- Total seed wall time: ~15-30s CPU
- No GPU speedup meaningful for such small M
- Per USER-LOCKED 2026-07-01 `feedback_smoke_only_local_cpu_no_full_dispatches`,
  SMOKE dispatches to local_cpu_queue only (Tailscale down blocks remote per
  Director spec).

STORAGE STRATEGY: **BUNDLED** (explicit discriminator arm; Research-authority-
directed to test BUNDLED near-capacity per Plate/Frady/Sommer literature).
NOT a violation of `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW`
(that law defaults SHARDED for compositional cells; here BUNDLED IS the
discriminator arm being tested; H2 would confirm BUNDLED unable to compose
at near-capacity, matching the physics law).

## SCHEMA-VET checklist

- `cardinality_ok`: TRUE (17 FULL / 5 SMOKE gated in verdict logic)
- `arms_differ_verified`: TRUE (L-axis endpoints hash-distinct per N)
- `arms_differ_exempted`: []
- `final_metrics_atomicity`: "tmp_replace" (via sibling wrapper)
- `crlb_n/a`: "categorical accuracy; discriminator is band-restricted
  additive-model residual"
- `discriminator_reachability`: TRUE (bracket_verify measured max|dev|_in_band
  = 0.162 already >= H1 threshold 0.15 at 3-seed TR=100)
- `baseline_in_band`: SATURATION_PC = 0.95+ (in-band-adjacent by design);
  DEEP_SAT = deliberate ceiling
- `sweep_alignment_verdict`: ALIGNED (N and L sweep separately; run_chain
  primitive natively parameterized by N (via N-arg to build_rules) and L
  (via L-arg to run_chain); no partition-routing confound)
- `discriminating_fraction`: MEASURED@bracket_verify: 7/12 = 0.58 cells at
  3-seed TR=100 in-band; well above 0.30 threshold
- `composition_edges`: SHAPE_MATCH (BUNDLED chain composition primitive
  unchanged from Probe 10 arm)
- `positive_control_arms`: SATURATION_PC (Gate D) + DEEP_SAT (H3 null)
- `functional_requirements`: N and ALGEBRA (L) cross-term at BUNDLED
  near-capacity; matched to existing FHRR chain composition primitive
- `calibration_check`: "default_ok_for_this_regime" (BETA=8.0 inherited from
  Probe 9 v1 and Probe 10 v1 at same modern_hopfield; empirical bracket
  confirms discriminator range is measurable)
- `cell_chunked`: TRUE (per-seed sibling files; s7 first, s13/s19 for FULL)
- `start_marker_written`: TRUE
- `crash_diagnostic_present`: TRUE
- `heartbeat_present`: TRUE (per-phase-point flush print)
- `defensive_error_checking`: "passed_all_4_patterns"
- `progress_logging`: "print_flush_true" (all progress lines flush=True)
- `progress_cadence_expected_s`: 60 (per-point wall << 60s at these sizes)
- `run_mode_verified_post_dispatch`: mandatory (§16); verify metrics.json
  landed run_mode == "smoke" for smoke dispatch
- `predicted_accuracy_per_point`:
  ```
  N=1024 L=2:  0.37   (in-band)
  N=1024 L=4:  0.47   (in-band)
  N=1024 L=8:  0.65   (in-band)
  N=1024 L=16: 0.59   (in-band)
  N=2048 L=2:  0.30   (floor-adjacent)
  N=2048 L=4:  0.27   (floor-adjacent)
  N=2048 L=8:  0.17   (floor)
  N=2048 L=16: 0.30   (floor-adjacent)
  N=4096 L=2:  0.50   (in-band)
  N=4096 L=4:  0.27   (floor-adjacent)
  N=4096 L=8:  0.40   (in-band)
  N=4096 L=16: 0.26   (floor-adjacent)
  ```
  MEASURED@bracket_verify 3-seed TR=100; predicted FULL-seed 3-seed
  aggregation similar variance.
- `points_in_discriminating_band` (predicted): 7
- `points_in_sweep`: 12
- `discriminating_fraction`: 0.58 (>= 0.30 required by §15 Gate B)

## Cited source atoms (exact names; META_RULE_AC)

- `research_stage1_regime_map_4negatives_2026-07-03` (Research authority NEG1)
- `stage1_regime_probe_9_N_x_topology_non_saturated_v1` (v1 template)
- `stage1_regime_probe_10_storage_x_algebra_non_saturated_v1` (Probe 10 BUNDLED cliff)
- `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03`
- `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`
- `feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03`
- `feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01`
- `META_cross_term_measurement_requires_both_arms_in_band_probe10_v1` (Skunkworks meta #43)
- `feedback_experiment_bias_master_checklist_USER_2026-06-24`
- `feedback_cardinality_ok_mandatory_prereg_field_for_sweep_axis_cells_2026-06-26`
- CITED@Plate1995 (HRR IEEE TNN, separability far from capacity)
- CITED@FradyKleykoSommer2018 (Neural Computation, near-capacity coupling)
- CITED@FradyKleykoSommer2020 (Resonator Networks I/II, joint N-factors capacity)

## Dispatch plan

- SMOKE: local_cpu_queue (SMOKE only per USER-LOCKED 2026-07-01);
  s7 first, s13/s19 held for FULL
- FULL: NOT DISPATCHED IN THIS CYCLE (Tailscale down blocks remote GPU per
  Director spec). Files committed; FULL dispatch pending Tailscale + USER
  push authorization.

## Independence from other in-flight cells

Probe 11 in flight and Probe 10 v2 re-SMOKE in flight — different files,
different anchors. No shared file conflicts.

## Framing discipline

MM_TENTATIVE at SMOKE at best. Novel-substrate-signal (H2) OR
Frady/Sommer-confirmation (H1) only if reproduces at multi-seed FULL +
survives Skunkworks landed-VET. Per `feedback_arc_continuation_vs_arc_closure_
isolated_smoke_not_enough_2026-07-03`, isolated SMOKE HP != arc closure.
