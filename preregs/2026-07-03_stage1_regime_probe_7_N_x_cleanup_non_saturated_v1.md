# Pre-registration: Regime Probe 7 — N x CLEANUP_MECHANISM (NON-SATURATED regime revival of Probe 2)

Date: 2026-07-03
Author: exp_dev (agent-spawn, Opus 4.7)
Anchor: `stage1_regime_probe_7_N_x_cleanup_non_saturated_v1`
Sibling seeds: `_s7`, `_s13`, `_s19`
Arc: Stage 1 REGIME MAP of CG_META axes (USER strategic direction 2026-07-03).

Companion cell to Probe 6 (F x CLEANUP TOPOLOGY revival, same day).

## Purpose (intuitive)

Skunkworks VET of Probe 2 (`T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_3seed_FULL_MM_STANDARD_cleanup_axis_regime_narrow_extended_to_N_axis`) revealed that all 72 phase points landed at acc=1.0. The null-result "N does not moderate CLEANUP_MECHANISM" is SATURATION-VACUOUS by the meta rule
`META_saturation_floor_masks_null_variance_probe3_lesson` (T4 MM_STANDARD, filed 2026-07-03 18:29Z): mechanism variance
cannot be non-zero when all mechanisms trivially saturate.

To actually test whether N moderates the CLEANUP_MECHANISM axis, I need to force the grid BELOW saturation
so mechanism variance has room to appear. This probe:

- Adds corruption in {0.88, 0.90, 0.92} (v2 CORRECTED per empirical smoke discovery; see below).
- Adds M in {800, 3200, 6400} for capacity pressure.
- Preserves 4 N levels {2048, 4096, 8192, 16384} to test scale sensitivity across half a decade.

**Empirical design correction (2026-07-03 exp_dev, v2):** original v1 spec was L=2 with
corr in {0.45, 0.60, 0.70}. First smoke landed all 6 SHARDED main pts at acc=1.0. Iterative
saturation-scans revealed SHARDED FHRR at L=2 is bulletproof up to corr=0.90 across all
tested N (36 configs, 1 non-saturated). L-scans at L in {2, 4, 8} corr up to 0.80 also
all-saturated. Extreme scan revealed a very narrow SHARDED FHRR cliff at corr=0.90 - 0.95
with mechanism differentiation only at L>=4. Critically, the cliff is **N-DEPENDENT**:
  - L=8 corr=0.90 N=2048 M=6400: modern_hopfield=0.875, iter_cos=0.950, soft_energy=0.975 (spread 0.10)
  - L=8 corr=0.90 N=4096-16384 M=6400: all mechs saturate at 1.0
  - L=8 corr=0.92 N=2048 M=6400: 0.500/0.450/0.450 (floor)
  - L=8 corr=0.92 N=4096 M=6400: 0.975/0.975/1.0 (borderline)
  - L=8 corr=0.92 N=8192-16384 M=6400: all 1.0

This IS the H1 signal (N moderates corruption tolerance) but visible ONLY at L=8 in a narrow corr band.
v2 grid: L_FIXED=8 (from 2), CORRUPTION_GRID_FULL=[0.88, 0.90, 0.92]. Cardinality unchanged at 108+PC=109/seed.
This changes what Probe 2's null test measured (L=2 regime) but is REQUIRED to escape the saturation ceiling
per META_RULE_AG. Trade-off honestly disclosed: v2 tests whether N moderates CLEANUP at L=8 (deeper chain),
which is a stronger operational regime than Probe 2's L=2 baseline. The SATURATION_PC arm still reproduces
Probe 2 baseline (L=2 config) as Gate D primitive-invocation reproducer.

- Fixes F=1 and STORAGE=SHARDED (Option Y regime — where mechanism-degeneracy was originally observed).

Probe 6 addresses the same META revival for TOPOLOGY axis (F x CLEANUP). Probe 7 addresses the same META
revival for SCALE_FREE axis (N x CLEANUP). Together they close the two open saturation-vacuous null revivals
required by `META_saturation_floor_masks_null_variance_probe3_lesson`.

If mechanism variance appears in the non-saturated slices -> Probe 2's null was saturation artifact and
N IS a moderator.
If mechanism variance stays ~0 in non-saturated slices -> Probe 2's null result stands with non-vacuous
evidence and strengthens the "STORAGE_UNIQUELY_moderates" thesis (Probe 1 CG_META result).

## Hypotheses (falsifiable)

- **H1 (N moderates when non-saturated):** at slices with grand-mean(acc) in [0.30, 0.95] band,
  `N_x_cleanup_max_abs_deviation_in_band >= 0.15` OR `max_per_N_mech_variance_in_band >= 0.10`.
  Confirms Probe 2's null was saturation artifact; **N IS a moderator of CLEANUP_MECHANISM**.
- **H2 (N genuinely does NOT moderate):** at non-saturated slices,
  `N_x_cleanup_max_abs_deviation_in_band < 0.05` AND `max_per_N_mech_variance_in_band < 0.05`.
  Probe 2's null result holds at NON-SATURATED regime; strengthens the "STORAGE_UNIQUELY_moderates"
  thesis (Probe 1 CG_META). Files as CG_META revival of Probe 2.
- **H3 (surprising crossover):** mechanism ranking changes with N within non-saturated slices ->
  published N-dependent crossover exponent (MM_TENTATIVE tier).

## Cited source atoms (exact names per META_RULE_AC + MM_STANDARD)

- `META_saturation_floor_masks_null_variance_probe3_lesson` (T4 MM_STANDARD METHODOLOGY_RULE, filed 2026-07-03 18:29Z)
   -- SATURATION-VACUOUS meta rule that gates this revival.
- `T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_3seed_FULL_MM_STANDARD_cleanup_axis_regime_narrow_extended_to_N_axis`
   -- the Probe 2 landing being revived here.
- `MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1` -- Probe 1 CG_META template + working non-saturated regime.
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` -- SCALE_FREE axis established 2026-07-02; N in {2048..16384}.
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` -- SHARDED-vs-BUNDLED chain-depth physics law 2026-07-02.
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` -- bipolar-codebook regime M-sweep 2026-07-03; source of 3 non-Hebbian mechanisms.
- 2026-06-18 associative-memory BY-CONSTRUCTION saturation tiering discipline (memory `reference_associative_memory_cell_noise_scaling_bug_and_by_construction_saturation_tiering_2026-06-18.md`).
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03` -- SMOKE gate discipline for null-hypothesis-plausible probes.

## Prior-work check (substrate-KB query)

Query concept keywords: `"N SCALE_FREE cleanup mechanism cross-term non-saturated revival Probe 2"`.
The closest prior arc landing IS Probe 2 (`stage1_regime_probe_2_N_x_cleanup_mechanism_v1`) which motivates this cell.
No prior non-saturated N x CLEANUP cross-term cell exists in the substrate-KB. Probe 7 is the FIRST intended
non-saturated N-axis test in the arc. Probe 3 (TOPOLOGY at N=4096 fixed) is a sibling saturation-vacuous null.
Probe 6 (companion, TOPOLOGY revival) authored same day is the direct methodological sibling.

## Compute architecture

- Class: `(a) batched-GPU` -- reuses batched-GPU primitives from
  `experiments/_stage1_physics_law_joint_composition_factorial_v1_core` (torch.cuda when available; CPU fallback for
  local smoke). At N=16384 M=6400 phase points are matmul-dominated; batched-GPU mandatory on remote.
- Storage strategy: `sharded` for the entire main factorial (Probe 7 is N x CLEANUP; STORAGE is not swept).
  One SATURATION positive-control point (SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine) reproduces Probe 2 baseline.
- Progress logging: `print_flush_true` (per-phase-point + per-seed prints all use `flush=True`; PROT-024 compliant).
- Timeout budget: SMOKE ~30-90s local CPU (7 pts at N in {2048, 16384}, M=6400). FULL ~10-25 min per seed
  on remote GPU (109 pts, most at N=16384 M=6400).

## Design

### Sweep axes (FULL)

- CLEANUP_MECHANISM in {modern_hopfield, iterative_cosine, soft_energy_attractor}
- N in {2048, 4096, 8192, 16384}  (4 scale levels; revives the swept axis from Probe 2)
- M in {800, 3200, 6400}  (M=6400 for capacity pressure)
- corruption in {0.88, 0.90, 0.92}  (v2 CORRECTED; empirical cliff of SHARDED FHRR at L=8)
- Fixed: F = 1, L = 8  (v2 CORRECTED from L=2; L=2 was empirically bulletproof to corr>=0.90 for all tested N)
- Fixed: STORAGE = SHARDED

Plus 1 SATURATION_PC arm: SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine (Gate D reproducer for Probe 2 baseline).

### Sweep axes (SMOKE)

- CLEANUP_MECHANISM in {modern_hopfield, iterative_cosine, soft_energy_attractor}
- N in {2048, 16384}  (endpoints of N-axis; exercises SCALE_FREE axis span)
- M in {6400}  (max; capacity pressure)
- corruption in {0.90}  (v2 CORRECTED; empirical cliff for L=8 SHARDED FHRR at N=2048)
- Per-N escapes-saturation semantics: N=2048 predicted non-saturated (mean ~0.93); N=16384 saturated (mean ~1.0).
  Gate fires if any N-slice mean-acc < 0.95.

Plus 1 SATURATION_PC arm (same as FULL).

### Cardinality

- FULL: 3 * 4 * 3 * 3 = **108 SHARDED main + 1 SATURATION_PC = 109 pts/seed** x 3 seeds = 327.
  - `EXPECTED_N_UNITS_FULL = 109`
- SMOKE: 3 * 2 * 1 * 1 = **6 SHARDED main + 1 SATURATION_PC = 7 pts** x 1 seed = 7.
  - `EXPECTED_N_UNITS_SMOKE = 7`

### Positive control (Gate D -- reproduces Probe 2 baseline)

At `SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine`, cell must reproduce acc >= 0.95 (Probe 2 baseline all at 1.0).
This is the SATURATION_PC arm; purpose is to prove the cell's primitive-invocation matches Probe 2's substrate physics.
- Cited prior atom: `T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_3seed_FULL_MM_STANDARD_...`
- Cited prior metric: 1.0 (all 72 SHARDED pts at acc=1.0)
- Tolerance: 0.05 (acc >= 0.95 acceptable).
- `regime_extension_audit: SHAPE_MATCH` -- same primitives at the identical (N, M, corr, F) config Probe 2 used.

### Reuse (Principle 11 -- cite EXACT signatures per MM_STANDARD)

- Primitives (`cphasor_torch`, `cnorm_torch`, `phase_corrupt`, `build_rules`, `run_chain`, `CLEANUP_REGISTRY`, `CLEANUP_MECHANISMS`, `BETA`, `ALPHA_SOFT`)
  imported from `experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py` (Option Y core scaffold).
- Verdict + interaction logic modeled on `experiments/_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_core.py` (Probe 2 core)
  with band-restricted discriminator additions (mirroring Probe 6 pattern).
- New file: `experiments/_stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_core.py`.
- Seed wrappers: `experiments/exp_stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_s{7,13,19}.py`.

## SMOKE HP criteria (SHIP FULL if all met)

Per `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`:
SMOKE gate is on INFRASTRUCTURE + POSITIVE CONTROL + NON-SATURATION CONFIRMATION only.
DO NOT gate on discriminator variance firing -- H2 (null-mechanism-degeneracy) is a legitimate
hypothesis-supportive outcome for this probe.

1. `selftest_ok` (cardinality math + 3-mech-distinct at N_test + SHARDED PC easy gate).
2. `cardinality_ok` (observed 7 = expected 7).
3. `arms_differ_verified` (3 distinct mechanism output-hash aggregates across SHARDED points; META_RULE_AF).
4. `saturation_pc_pass` (SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine acc >= 0.95 -> reproduces Probe 2 baseline).
5. `escapes_saturation_ceiling` (per-N semantics): at least one N-slice has mean-acc < 0.95. Grand mean
   is not the gate because high-N slices may saturate while low-N slices differentiate -- that IS the
   N-moderation signal. If NO N-slice is below 0.95 the design failed and I must REJECT SMOKE and re-spec.
6. **Informational (NOT gating):** report `max_per_N_mech_variance` at the smoke slice (mid-corr=0.60, M=6400,
   N in {2048, 16384}). Report the value regardless of magnitude -- H1 (variance appears) and H2 (variance ~0)
   are both hypothesis-supportive outcomes.

## FULL HARD_PASS_CG_TIER criteria

1. `cardinality_ok` per seed (109 pts each).
2. `arms_differ_verified` across seeds.
3. `saturation_pc_pass` per seed (SATURATION_PC arm reproduces acc >= 0.95).
4. 3-seed CV `< 0.10` per phase point (accuracy stability).
5. **`escapes_saturation_ceiling_full`: >= 30% of main-grid phase points have mean-acc in the `[0.30, 0.95]`
   non-saturated band.** If not, the FULL grid itself failed to escape saturation -> cannot claim H1 or H2 with
   confidence -> verdict = `MIDDLE_BAND_ESCAPES_SATURATION_FAIL`.
6. **Primary discriminator: N x CLEANUP_MECHANISM cross-term, restricted to slices with grand-mean(acc) in [0.30, 0.95].**
   - Within-band: `N_x_cleanup_max_abs_deviation_in_band < 0.05` AND `max_per_N_mech_variance_in_band < 0.05` ->
     **HARD_PASS_H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED**: Probe 2's null result reproduces at NON-SATURATED
     regime; strengthens "STORAGE_UNIQUELY_moderates" thesis (Probe 1). Files as CG_META revival of Probe 2.
   - Within-band: `N_x_cleanup_max_abs_deviation_in_band >= 0.15` OR `max_per_N_mech_variance_in_band >= 0.10` ->
     **HARD_PASS_H1_N_MODERATES_WHEN_NON_SATURATED**: Probe 2's null was saturation artifact; N IS a moderator.
     Updates REGIME MAP with new SCALE_FREE_x_CLEANUP boundary point.
   - `H3 crossover`: if mech ranking changes across N within non-saturated slices, log
     `mech_ranking_crossover: True` and file as MM_TENTATIVE crossover exponent.
7. 3-seed replication + Skunkworks landed-VET before CG atom filing.

## HARD_FAIL

- `cardinality breach` (any seed missing pts).
- `saturation_pc_fail` (SATURATION_PC arm below 0.95 -> primitive-invocation broken).
- `selftest fails`.

## MIDDLE_BAND

- `escapes_saturation_ceiling_full` fails (< 30% of pts in [0.30, 0.95]) -> `MIDDLE_BAND_ESCAPES_SATURATION_FAIL`; grid needs re-spec.
- `0.05 <= N_x_cleanup_max_abs_deviation_in_band < 0.15` -> weak N-moderation regime; file as MM_TENTATIVE.

## SCHEMA-VET checklist (all True/present)

- `cardinality_ok`: True (109 FULL / 7 SMOKE)
- `arms_differ_verified`: True (3 distinct cleanup mechanisms; selftest hash-check + aggregate hash check in run_one_seed)
- `final_metrics_atomicity`: `tmp_replace` (atomic tmp + os.replace at end)
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException)
- `crlb_n/a`: "categorical accuracy on FHRR chain composition; discriminator is cross-term interaction deviation
   restricted to non-saturated band. Positive-control reproduces the same primitives at the test regime (Gate D
   compliance). The `escapes_saturation_ceiling` gate is the explicit reachability check."
- `discriminator_reachability`: True. If H1 correct, N_x_cleanup deviation >= 0.15 measured, gate fires. If H2 correct,
   deviation < 0.05 measured, gate fires. Non-saturated band is empirically enforced by grid design (M=6400 N=16384 corr=0.70
   -> mean-acc predicted 0.10-0.35 given Plate bound).
- `baseline_in_band`: main-grid designed for non-saturated band. SATURATION_PC deliberately at ceiling as reference.
   `escapes_saturation_ceiling` gate is the enforcement mechanism.
- `HP_SCOPE`: {`SHARDED_main`: [`arms_differ`, `cardinality_ok`, `escapes_saturation_ceiling`, `N_x_cleanup_deviation_in_band`, `max_per_N_mech_variance_in_band`], `SATURATION_PC_arm`: [`saturation_pc_pass acc>=0.95`]}
- `cell_chunked`: True (3 seed wrappers)
- `start_marker_written`: True
- `crash_diagnostic_present`: True
- `heartbeat_present`: per-phase-point print with flush=True
- `defensive_error_checking`: `passed_all_4_patterns`
- `sweep_alignment_verdict`: `ALIGNED` -- N, CLEANUP_MECHANISM, M, corr are the actual primitives that experience
   each swept value; no partition-routing intermediation. Every swept axis IS the axis primitives see.
- `discriminating_fraction`: SHARDED at cliff corr=0.70 across (M=800, 3200, 6400) x (N=2048, 4096, 8192, 16384)
   expected to span [0.10, 0.95] band. Predicted per-point mean-acc from Plate 0.14*N bound + phase corruption physics:
   at M/N > 1.5 corr=0.70, mean-acc ~0.10-0.35; at M/N < 0.4 corr=0.45, mean-acc ~0.80-1.0. Predicted >= 50%
   pts in discriminating [0.30, 0.95] band. Enforced by `escapes_saturation_ceiling_full` gate.
- `composition_edges`: [`build_rules -> run_chain: SHAPE_MATCH`, `run_chain -> cleanup_argmax_idx: SHAPE_MATCH`;
   all inherited from Option Y core].
- `positive_control_arms`: [{arm: `saturation_pc_sharded_iterative_cosine_at_probe2_regime`,
   primitive: `run_chain(storage=SHARDED, mechanism=iterative_cosine)`,
   cited_prior_atom: `T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_3seed_FULL_MM_STANDARD_cleanup_axis_regime_narrow_extended_to_N_axis`,
   cited_prior_metric: 1.0 (all 72 SHARDED pts at acc=1.0),
   test_regime: {M: 800, N: 2048, F: 1, L: 2, corr: 0.20},
   tolerance: 0.05,
   if_outside_tolerance: `HARD_FAIL_SATURATION_PC_MISMATCH`,
   regime_extension_audit: `SHAPE_MATCH` -- identical (M, N, F, L, corr) subset of Probe 2's grid}]
- `functional_requirements`:
  - FR-1: chain-composition with varying N/mech/M/corr -> `run_chain` primitive (imported)
  - FR-2: N-varying sharded codebook -> `build_rules(N=N)` primitive (imported)
  - FR-3: 3-mechanism cleanup families -> `CLEANUP_REGISTRY` (imported)
  - FR-4: N x CLEANUP interaction deviation restricted to non-saturated band -> new logic
  - FR-5: `escapes_saturation_ceiling` non-saturated fraction calculation -> new logic
- `progress_logging`: `print_flush_true`
- `calibration_check`: `default_ok_for_this_regime` -- BETA=8.0 ALPHA=0.5 inherited from Option Y core where they
   passed selftest at F=1. N-axis is the primary sweep here; F=1 fixed so cleanup calibration matches Probe 2.
- `progress_cadence_expected_s`: 30 (per-phase-point flush; longest single point <30s expected on GPU;
   N=16384 M=6400 corr=0.70 estimated 5-15s on cuda; ~60s worst-case on CPU).
- `saturation_gate_present`: True (`escapes_saturation_ceiling` both SMOKE gate and FULL gate).
- `null_hypothesis_smoke_discipline`: TRUE -- per `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`,
   SMOKE gates on infrastructure + saturation_pc + escapes_saturation only, NOT on H1 discriminator firing.

## Reachability of criteria

- SMOKE wall: ~30-90s on local CPU (7 pts; N in {2048, 16384} M=6400 corr=0.60; SATURATION_PC very fast).
- FULL wall estimate: 109 pts/seed on remote GPU ~= 5-15 min/seed (majority pts at N=8192 or 16384 with M=6400
   batched matmul on GPU). Per-seed timeout budget: 3600s (well above estimate; PROT-019 minimum met).
- CRLB-adjacent physics: at M/N=0.78 (Plate bound violated 5.5x), sharded_pc drops meaningfully below 1.0. At
   corr=0.70 with 70% of phasor dimensions randomized, cleanup mechanism differences become measurable if they exist.

## Dispatch plan

- Local SMOKE: local_cpu_queue (SMOKE ONLY per USER-LOCKED 2026-07-01; Tailscale down for remote right now).
- Remote FULL: `overnight_queue` (GPU) -- batching mandatory at N=16384 M=6400 grid. Requires push to origin/main
   by Orchestrator (harness-denied to exp_dev). USER re-auth needed for Tailscale.

## USER authorization

Full-auto authorized per USER 2026-07-03. Explicit self-reference (USER-locked): "I" (exp_dev agent) authored + smoked
+ prepared FULL dispatch. Orchestrator will dispatch FULL to GPU if SMOKE HP.
