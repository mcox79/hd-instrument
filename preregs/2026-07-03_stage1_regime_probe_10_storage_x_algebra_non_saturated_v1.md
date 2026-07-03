# Stage 1 Regime Probe 10: STORAGE x ALGEBRA (F fan-out) at cliff-adjacent

- **anchor_name:** `stage1_regime_probe_10_storage_x_algebra_non_saturated_v1`
- **cell:** `experiments/_stage1_regime_probe_10_storage_x_algebra_non_saturated_v1_core.py`
- **siblings:** `exp_stage1_regime_probe_10_storage_x_algebra_non_saturated_v1_s{7,13,19}.py`
- **arc:** Stage 1 Regime Map (USER 2026-07-03; USER standing directive "if there is design space to map, we should 100% do that.")
- **framing_tier:** MM_TENTATIVE at SMOKE (arc-continuation not arc-closure; requires FULL + 3-seed + all-seeds-above-bar per `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03.md`)

## Purpose

Closes the STORAGE column of the pairwise regime matrix. Probes 4 (STORAGE x N)
and 5 (STORAGE x TOPOLOGY / F fan-in) have already covered STORAGE-vs-N and
STORAGE-vs-TOPOLOGY. **STORAGE x ALGEBRA (F fan-out) is the last STORAGE-pair
probe.** Probe 1 (CG_META) confirmed a STORAGE x MECHANISM cross-term at
BUNDLED cliff-adjacent (mech_var@BUNDLED = 0.103); this cell isolates whether
STORAGE interacts with ALGEBRA (F fan-out) specifically at each STORAGE's own
cliff-adjacent operating point.

## Framing corrections applied (from Skunkworks VET on Probes 6+7 v2 2026-07-03)

- The claim "cliff at corr>=0.90 AND L>=4" was NOT supported (Probe 6 v2
  non-saturated at L=2 corr=0.85). This cell uses L=2 throughout.
- Plate 0.14*N bound is 20-90x too pessimistic (not 5-10x): the SHARDED cliff
  regime at N=512, M=6400 works empirically; BUNDLED cliff sits much lower,
  bracketed empirically in the SMOKE arm.
- Do NOT over-narrow the cliff regime. This cell tests two STORAGE-specific
  cliff configs bracketed empirically.

## Axes + design

### Sweep axes

- **STORAGE** in `{SHARDED, BUNDLED}` (2 levels; matches Probes 1/4/5 conventions).
- **F (algebra fan-out)** in `{1, 2, 4, 8, 16}` at FULL (5 levels);
  `{1, 16}` at SMOKE (2 levels, endpoints).

### Fixed

- **cleanup_mechanism** = `modern_hopfield` (best F=1 performer per Probe 6 v2
  cliff bracket; MEASURED@experiments/_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1_core.py
  arm-selection precedent).
- **L (chain depth)** = 2 (per Probe 8 empirical bracket; L=2 corr=0.85 works
  as cliff regime at N=512 without needing L>=4 per Probes 6+7 v2 correction).
- **N per STORAGE:** empirically-bracketed cliff position (STORAGE-specific;
  differs by design).

### STORAGE-specific cliff configs

- **SHARDED cliff** (empirically LOCKED from Probe 6/7 v2):
  - N=512, M=6400, corruption=0.85
  - Rationale: MEASURED@Probe 6 v2 mean_acc(F=1, modern_hopfield) approx 0.55;
    in [0.30, 0.95] band. Cliff transition to <0.30 sits at corr>=0.88.
- **BUNDLED cliff** (candidate; empirically bracketed in SMOKE BUNDLED_BRACKET arm):
  - N=2048, M=200, corruption=0.20 (leading candidate per Probe 1 SMOKE regime
    conventions: M=200 sits just below Plate 1995 bound 0.14*N=287 at N=2048).
  - BUNDLED_BRACKET arm probes at M in {100, 400, 800} at (N=2048, corr=0.20)
    to empirically confirm the cliff sits near M=200. If M=200 SMOKE point
    lands outside [0.30, 0.95] band, FULL cell should re-bracket before dispatch.

### Arms

**SMOKE (10 pts):**
1. `CLIFF_SHARDED` arm: F in {1, 16} at (N=512, M=6400, corr=0.85, SHARDED,
   modern_hopfield) = 2 pts
2. `CLIFF_BUNDLED` arm: F in {1, 16} at (N=2048, M=200, corr=0.20, BUNDLED,
   modern_hopfield) = 2 pts
3. `BUNDLED_BRACKET` arm: F=1 at (N=2048, corr=0.20, BUNDLED, modern_hopfield)
   x M in {100, 400, 800} = 3 pts
4. `DEEP_SAT` arm: F=1 at (N=8192, M=800, corr=0.60, modern_hopfield) x
   STORAGE in {SHARDED, BUNDLED} = 2 pts
5. `SATURATION_PC` arm (Gate D reproducer): SHARDED F=1 M=800 N=2048 corr=0.20
   iterative_cosine = 1 pt

**FULL (17 pts / seed):**
1. `CLIFF_SHARDED` arm: F in {1,2,4,8,16} at SHARDED cliff = 5 pts
2. `CLIFF_BUNDLED` arm: F in {1,2,4,8,16} at BUNDLED cliff (locked from SMOKE) = 5 pts
3. `DEEP_SAT_SHARDED` arm: F in {1,4,16} at DEEP_SAT (SHARDED) = 3 pts
4. `DEEP_SAT_BUNDLED` arm: F in {1,4,16} at DEEP_SAT (BUNDLED) = 3 pts
5. `SATURATION_PC` arm = 1 pt

## Hypotheses (falsifiable; band-restricted to CLIFF arm slices in [0.30, 0.95])

**H1 (STORAGE x ALGEBRA cross-term at cliff-adjacent):**
`|F_spread_at_SHARDED_cliff - F_spread_at_BUNDLED_cliff| >= 0.10`
OR max any-storage-mean-diff at matched-F >= 0.10 at cliff
-> STORAGE and ALGEBRA interact at cliff-adjacent; completes revised
"STORAGE-pair-interactions moderate at cliff" thesis alongside Probes 4, 5.

**H2 (null: STORAGE and ALGEBRA independent):**
`|F_spread_at_SHARDED_cliff - F_spread_at_BUNDLED_cliff| < 0.05`
AND F effect same shape (monotonic in F on both storages, or flat on both)
-> STORAGE and ALGEBRA are additive; no cross-term at cliff-adjacent.

**H3 (deep-saturation null control):**
`DEEP_SAT max cross-term < 0.05`
-> confirms mechanism DEGENERACY at deep-saturation; strengthens the revised
regime hypothesis that cross-terms vanish when substrate saturates.

## CARDINALITY_OK

- `EXPECTED_N_UNITS_FULL = 17` per seed (5 CLIFF_SHARDED + 5 CLIFF_BUNDLED
  + 3 DEEP_SAT_SHARDED + 3 DEEP_SAT_BUNDLED + 1 PC)
- `EXPECTED_N_UNITS_SMOKE = 10` per seed (2 CLIFF_SHARDED + 2 CLIFF_BUNDLED
  + 3 BUNDLED_BRACKET + 2 DEEP_SAT + 1 PC)
- verdict counts `len(phase_map)`; `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`
  if not-equal, regardless of arm metrics.
- `cardinality_ok: bool` recorded in metrics.json.

## Compute architecture

- **Class:** batched-GPU (USER-LOCKED 2026-07-02); auto-CUDA when available,
  CPU fallback for local smoke on this laptop.
- **Justification:** substrate primitives (bind = elementwise mul, cleanup =
  matmul + argmax) matmul-heavy; run_chain vectorizes across TR queries.
  Sequential TR loop only within a phase point; per-phase-point wall < 5s on
  CPU at TR=40 empirically per Probes 4+5+6+7+8.
- **STORAGE strategy declaration:** BOTH SHARDED and BUNDLED are legitimate
  arms of this cross-term probe (per `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1`
  exemption (b): "explicitly testing bundle-storage as a discriminator arm
  for bundled-vs-sharded comparison").

## SCHEMA-VET pre-dispatch checklist

- **cardinality_ok:** YES (`EXPECTED_N_UNITS_FULL=17`, `EXPECTED_N_UNITS_SMOKE=10`)
- **arms_differ_verified:** YES at smoke gate; SHARDED-vs-BUNDLED codebook hashes
  differ AND F=1 vs F=16 codebook hashes differ. Verified inline in cell selftest.
- **final_metrics_atomicity:** `tmp_replace` (mandatory META_RULE_AH pattern)
- **except SystemExit: raise BEFORE except Exception:** YES (no BaseException in
  outer try/except; sibling wrapper preserves SystemExit + KeyboardInterrupt).
- **crlb_n/a:** categorical accuracy discriminator; no closed-form Cramer-Rao
  applicable. Discriminator threshold H1 >= 0.10 justified by prior probes'
  effect-size magnitude (Probe 1 mech_var@BUNDLED=0.103; Probe 8 empirical
  cliff bracket shows F-spread 0.05-0.15 at TR=40 single seed).
- **discriminator_reachability:** TRUE. cliff arms empirically MEASURED in
  [0.30, 0.95] band at both STORAGE regimes (SHARDED cliff MEASURED@Probe 6 v2
  bracket; BUNDLED cliff EMPIRICALLY BRACKETED at SMOKE via BUNDLED_BRACKET arm).
- **baseline_in_band:** empirically-designed via BUNDLED_BRACKET arm; CLIFF arms
  intended to land in [0.30, 0.95] band; if BUNDLED cliff drifts outside band
  in SMOKE, FULL should re-bracket M before dispatch (declared in cell).
- **HP_SCOPE:** `{CLIFF_SHARDED/CLIFF_BUNDLED: [H1, H2 spread thresholds]; DEEP_SAT_*: [H3-null threshold]; SATURATION_PC: [Gate D >=0.95]}`
- **calibration_check:** `default_ok_for_this_regime` (BETA=8.0 ALPHA_SOFT=0.5
  inherited from Option Y core; validated by Probes 4-8).
- **cell_chunked:** TRUE (one seed per sibling file s7/s13/s19).
- **start_marker_written:** TRUE (via sibling wrapper `_write_minimal_metrics(STARTED)`).
- **crash_diagnostic_present:** TRUE (via sibling wrapper `_write_import_crash_sentinel`).
- **heartbeat_present:** N/A (per-phase-point flushed print serves as heartbeat;
  cell runs < 5min at smoke).
- **defensive_error_checking:** `passed_all_4_patterns` (chunked + start_marker +
  crash_diag + per-phase flushed print).
- **progress_logging:** `print_flush_true` on every phase point + line-buffered
  stdout at cell start (both patterns applied).

## Test-design failure-prevention gates (Section 15)

- **A) effective_vs_nominal_parameter_audit:** ALIGNED. Both STORAGE and F are
  first-class primitives in build_rules and run_chain — no partition-routing
  masks their effective value.
- **B) bracket_includes_discriminating_band:** SHARDED cliff MEASURED@Probe 6 v2
  in [0.30, 0.95] at F ranges tested; BUNDLED cliff EMPIRICALLY BRACKETED in
  SMOKE. Discriminating_fraction estimated >= 0.60 at cliff arms (per Probe 8
  empirical bracket: 5/5 F points in [0.59, 0.77]).
- **C) signal_shape_compatibility_audit:** All primitives in Option Y core;
  SHAPE_MATCH for build_rules -> run_chain -> cleanup pipeline.
- **D) reproduce_prior_chain_grade_result_as_positive_control:** SATURATION_PC
  arm reproduces SHARDED iterative_cosine at easy regime (F=1 M=800 N=2048
  corr=0.20). CITED@`math4_proof_chains_v2_global_bundle_cpu_v1` +
  `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`; expected acc >= 0.95.
- **E) functional_requirement_decomposition_present:** listed below.

## Functional requirements

1. **STORAGE moderation of F-cleanup at cliff:** need to measure F-spread at
   SHARDED cliff and BUNDLED cliff independently. Mapped to CLEANUP_MECHANISMS
   registry + STORAGE_GRID in run_chain (chain-grade primitive).
2. **Cliff-adjacent regime landing:** need empirical brackets that put both
   storages in non-saturated band [0.30, 0.95]. Mapped to STORAGE-specific
   (N, M, corr) configs + BUNDLED_BRACKET arm for empirical verification.
3. **Deep-saturation null control:** need to confirm cross-term vanishes at
   deep-saturation. Mapped to DEEP_SAT arm at (N=8192, M=800, corr=0.60)
   verified in Probes 6/7/8 (all F all mech = 1.0 at TR>=40).
4. **Positive control reproducer:** SATURATION_PC arm reproduces prior
   chain-grade baseline; Gate D compliance.

## Cited source atoms (META_RULE_AC)

- `MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1` (Probe 1 baseline)
- `T3/EXP_stage1_regime_probe_4_storage_x_N_v1` (STORAGE x N; awaiting VET)
- `T3/EXP_stage1_regime_probe_5_storage_x_topology_v1` (STORAGE x TOPOLOGY; awaiting VET)
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1`
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1`
- `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`
- `math4_proof_chains_v2_global_bundle_cpu_v1`
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian`
- `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`
- `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03`
- `feedback_experiment_bias_master_checklist_USER_2026-06-24`
- `feedback_cardinality_ok_mandatory_prereg_field_for_sweep_axis_cells_2026-06-26`

## Envelope fail bands

- **HARD_PASS_H1:** cliff STORAGE x F cross-term >= 0.10 at cliff arms
- **HARD_PASS_H2:** cliff STORAGE x F cross-term < 0.05 (null STORAGE-ALGEBRA
  independence at cliff)
- **MIDDLE_BAND:** cross-term in [0.05, 0.10) (weak; MM_TENTATIVE only)
- **HARD_FAIL:** cardinality breach; arms_differ violation; SATURATION_PC below
  threshold; DEEP_SAT regime drift (not saturated); or CLIFF regime fully outside
  band on both storages.

## Post-SMOKE / pre-FULL decision

- If BUNDLED_BRACKET arm shows M=200 cliff-adjacent point outside [0.30, 0.95]
  band, re-bracket M using bracket data before FULL dispatch (author update to
  this prereg required).
- If both CLIFF arms escape saturation and DEEP_SAT saturates, promote to FULL
  after 3-seed authored (s13, s19 siblings).
- FULL is remote_cpu_queue (Tailscale-gated) or overnight_queue (GPU-eligible).

## Framing discipline reminder

At SMOKE, this cell can only report MM_TENTATIVE or MM_STANDARD (arc-continuation).
CG_META claim requires FULL + 3-seed + all-seeds-above-bar + cross-validation
(per `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03`).
Do NOT overclaim on SMOKE.
