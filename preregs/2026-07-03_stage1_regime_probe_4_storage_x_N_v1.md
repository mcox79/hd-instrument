# Pre-registration: Regime Probe 4 - STORAGE x N (SCALE_FREE) cross-term

Date: 2026-07-03
Author: exp_dev (agent-spawn, Opus 4.7)
Anchor: `stage1_regime_probe_4_storage_x_N_v1`
Sibling seeds: `_s7`, `_s13`, `_s19`
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER strategic direction 2026-07-03).

## Purpose (intuitive)

Fourth probe in the Stage 1 Regime Map arc. Prior probes established:
- Probe 1 (`stage1_regime_map_storage_x_cleanup_v1`) - STORAGE moderates CLEANUP_MECHANISM at 3-seed FULL (`mech_var@BUNDLED = 0.103 +/- 0.03`)
- Probe 2 (`stage1_regime_probe_2_N_x_cleanup_mechanism_v1`) - N does NOT moderate CLEANUP_MECHANISM at SHARDED
- Probe 3 (`regime_probe_3_topology_x_cleanup_v1`) - TOPOLOGY does NOT moderate CLEANUP_MECHANISM at SHARDED, across F in {1,2,4,8}

Question: does STORAGE moderate OTHER axes too? Specifically STORAGE x N -
is STORAGE the "master axis" that gates whether SCALE_FREE holds, or is STORAGE
only special for MECHANISM? SCALE_FREE was established at SHARDED
(`sharded_fhrr_capacity_scale_free_extension_N16384_v1_seed_7` MIDDLE_BAND at
N=16384; source atom `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1`).
This probe crosses STORAGE with N to test whether the smoothness of the top1(N)
curve is a SHARDED-only property or extends to BUNDLED.

## Hypotheses (falsifiable)

- **H1 (STORAGE is master moderator):** SCALE_FREE holds at SHARDED (top1 curve
  smooth in N over 3 octaves 2048->16384) but DEGRADES at BUNDLED (top1 has
  cliff or crossover in N) -> STORAGE moderates SCALE_FREE the same way it
  moderates MECHANISM -> STORAGE is master.
- **H2 (STORAGE special only for MECH):** SCALE_FREE holds at BOTH SHARDED and
  BUNDLED (top1 curve smooth either way) -> STORAGE's moderating power is
  specific to MECHANISM axis.
- **H3 (surprising crossover):** SCALE_FREE reverses direction at BUNDLED
  (larger N gives WORSE top1). This is the non-monotonic outcome; would flag
  bundle-noise interaction that grows with N.

Distinguishing rule (measured at cliff corr=0.45; M >= 800 pooled):
- H1 <-> `storage_x_N_max_abs_deviation >= 0.10` AND
  `per_storage_N_monotonicity_break_count[BUNDLED] >= 1` while
  `per_storage_N_monotonicity_break_count[SHARDED] == 0`.
- H2 <-> `storage_x_N_max_abs_deviation < 0.05` AND monotonic on both storages.
- H3 <-> `bundled_top1(N=16384) < bundled_top1(N=2048) - 0.10` (reversal).

## Cited source atoms (exact names per META_RULE_AC + MM_STANDARD)

- `stage1_regime_map_storage_x_cleanup_v1` - Probe 1 STORAGE x CLEANUP_MECH
  FULL result: `mech_var@BUNDLED = 0.103` HYPOTHESIZED@Director framing 2026-07-03
  (per spawn prompt).
- `stage1_regime_probe_2_N_x_cleanup_mechanism_v1` - Probe 2 N x CLEANUP null
  at SHARDED (Director framing 2026-07-03).
- `regime_probe_3_topology_x_cleanup_v1` - Probe 3 TOPOLOGY x CLEANUP null at
  SHARDED F in {1,2,4,8}.
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` -
  SCALE_FREE physics law established 2026-07-02 at SHARDED F=1.
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` - SHARDED-vs-
  BUNDLED chain-depth physics law established 2026-07-02.
- `sharded_fhrr_capacity_scale_free_extension_N16384_v1_seed_7` MEASURED@
  `data/exp_sharded_fhrr_capacity_scale_free_extension_N16384_v1_seed_7/metrics.json`
  (SHARDED N=16384 capacity extension, MIDDLE_BAND).
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` - bipolar-codebook
  M-sweep source for `iterative_cosine` primitive.
- `stage1_physics_law_joint_composition_factorial_v1_s11` - Option Y source
  of imported primitives (build_rules, run_chain, cleanup_argmax_idx).
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`
  - SMOKE-gate discipline for null-hypothesis probes.

## Substrate-KB concept-query result

Query: `"STORAGE strategy scale-free N cross-term BUNDLED SHARDED capacity"`.
Top-5 cosines 0.276-0.360; **only 1 hit above 0.30** (top-1 "Storage strategy"
cosine=0.360, from Cortex integration prereg, not directly related to this
STORAGE x N cross-term). The `sharded_fhrr_capacity_scale_free_extension_N16384`
atom is at cosine 0.281 (below threshold) and covers SHARDED-only SCALE_FREE up
to N=16384. **The STORAGE x N cross-term (SCALE_FREE curve at BUNDLED vs SHARDED)
has not been directly explored.**

Prior-work check result: `NONE at cosine>0.30 that is substantively related to
the STORAGE x N cross-term; genuinely novel arc extension`.

## Compute architecture

- Class: `(a) batched-GPU` - reuses batched-GPU primitives from
  `_stage1_physics_law_joint_composition_factorial_v1_core` (torch.cuda when
  available; CPU fallback for local smoke).
- Storage strategy: mixed (SHARDED and BUNDLED both as discriminator arms).
- Progress logging: `print_flush_true`.
- Timeout budget: SMOKE ~30-90s local CPU; FULL ~10-15 GPU-sec/seed on remote
  GPU or ~5-10min per seed on remote CPU (matches prior Probe 3 wall time).

## Design

### Sweep axes

- STORAGE in {SHARDED, BUNDLED} - 2 levels (primary axis).
- N in {2048, 4096, 8192, 16384} - 4 levels (spans 3 octaves for SCALE_FREE
  curve; matches source atom's tested range).
- M in {200, 800, 3200} - 3 levels (M scaling).
- corruption in {0.20, 0.45} - 2 levels.
- CLEANUP_MECHANISM FIXED = `iterative_cosine` (winner from Probe 1; simplest
  for isolation).
- F=1, L=2 fixed.

### Cardinality

- FULL: 2 * 4 * 3 * 2 = **48 phase points / seed** x 3 seeds = 144.
  - `EXPECTED_N_UNITS_FULL = 48`
- SMOKE: 2 * 2 * 1 * 1 = **4 sweep pts + 1 SHARDED_PC_easy = 5 / seed** x 1 seed = 5.
  - `EXPECTED_N_UNITS_SMOKE = 5`
  - Smoke fixed: N in {2048, 8192}, M = 800, corr = 0.45 (cliff). Keep smoke
    short while spanning 2-octave N contrast. SHARDED_PC_easy point added
    at (SHARDED, N=4096, M=200, corr=0.20, iterative_cosine, F=1, L=2) since
    smoke sweep does not include M=200 or corr=0.20; PC-easy check needed for
    positive-control gate.

### Reuse (Principle 11)

- Primitives (`build_rules`, `run_chain`, `CLEANUP_REGISTRY`, `phase_corrupt`,
  `cphasor_torch`, `BETA`, `ALPHA_SOFT`, `DEVICE`, `GPU_NAME`) imported from
  `experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py`.
- New file: `experiments/_stage1_regime_probe_4_storage_x_N_v1_core.py` -
  defines sweep, verdict logic, per-storage per-N SCALE_FREE curve calc,
  STORAGE x N ANOVA interaction, monotonicity-break count.
- Seed wrappers: `experiments/exp_stage1_regime_probe_4_storage_x_N_v1_s{7,13,19}.py`.

## SMOKE HP criteria (SHIP FULL if all met)

Per null-hypothesis SMOKE gate discipline (memory rule
`feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`):
SMOKE does NOT gate on discriminator firing. It gates on plumbing + positive
controls only. H2 (null-result) must remain reachable.

1. `selftest_ok` (returns True; cardinality + storages-produce-distinct-outputs
   at PC regime + SHARDED PC easy passes).
2. `cardinality_ok` (observed 5 = expected 5).
3. `arms_differ_verified` (SHARDED and BUNDLED produce distinct output-hash
   aggregates across sweep points; META_RULE_AF).
4. `pc_easy_pass`: SHARDED at (M=200, N=4096, corr=0.20, F=1, L=2,
   iterative_cosine) acc >= 0.90 (positive control per USER spawn prompt).
5. `storage_gap_pass`: at (M=800, corr=0.45) sweep point where M/N > 0.14
   (Plate 1995 bundle bound: BUNDLED collapse regime), the storage gap
   `SHARDED_acc - BUNDLED_acc >= 0.30`. Applied at N=2048 (M/N=0.39, above
   bound); this asserts BUNDLED-vs-SHARDED discriminator arm actually
   differentiates in the smoke regime.
6. **INFORMATIONAL (does NOT gate; per null-hypothesis discipline):**
   `storage_x_N_smoke_deviation = storage_gap(N=8192) - storage_gap(N=2048)`.
   Report the value. Change in storage gap across N is a preview of H1
   vs H2. Do NOT reject SMOKE on any value; report for Director interpretation.

## FULL HARD_PASS_CG_TIER criteria

1. `cardinality_ok` per seed (48 pts each).
2. `arms_differ_verified` across seeds.
3. `pc_easy_pass` at (SHARDED, M=200, N=4096, corr=0.20) queried from sweep
   (mean over corr axis if needed): acc >= 0.90.
4. 3-seed CV `< 0.10` per phase point (accuracy stability).
5. **Primary discriminator: STORAGE x N cross-term ANOVA deviation.**
   - `storage_x_N_max_abs_deviation >= 0.10` AND
     `per_storage_N_monotonicity_break_count[BUNDLED] >= 1` AND
     `per_storage_N_monotonicity_break_count[SHARDED] == 0`
     -> **HARD_PASS_H1_STORAGE_MASTER_MODERATOR_SCALE_FREE_BREAKS_AT_BUNDLED**:
     STORAGE is master; SCALE_FREE is SHARDED-only property.
   - `storage_x_N_max_abs_deviation < 0.05` AND
     BOTH storages monotonic (0 breaks each) OR
     both SCALE_FREE curves parallel within 0.05
     -> **HARD_PASS_H2_STORAGE_SPECIAL_ONLY_FOR_MECHANISM**: STORAGE's
     moderating power is specific to CLEANUP_MECHANISM axis; SCALE_FREE
     is scale-free of storage.
   - `bundled_top1(N=16384) < bundled_top1(N=2048) - 0.10` at fixed M
     (pooled at cliff corr=0.45)
     -> **HARD_PASS_H3_BUNDLED_SCALE_FREE_REVERSAL**: bigger N gives worse
     BUNDLED top1; noise-vs-signal balance at BUNDLED interacts adversely
     with dimensionality.
6. 3-seed replication + Skunkworks landed-VET before CG atom filing.

## HARD_FAIL

- cardinality breach (any seed missing pts).
- `pc_easy_pass` fails (SHARDED PC easy < 0.90 -> primitive reproduction broken).
- selftest fails.
- storage_gap at BUNDLED collapse regime < 0.20 (arms don't differ -> discriminator
  arm broken).

## MIDDLE_BAND

- `0.05 <= storage_x_N_max_abs_deviation < 0.10` (weak STORAGE x N interaction).
- Mixed monotonicity signal (both storages have breaks or neither has).
- File as MM_TENTATIVE crossover.

## SCHEMA-VET checklist (all True/present)

- `cardinality_ok`: True (48 FULL / 5 SMOKE).
- `arms_differ_verified`: True (SHARDED vs BUNDLED bundle_hash / output_hash
  aggregates over sweep pts; META_RULE_AF).
- `final_metrics_atomicity`: `tmp_replace` (atomic tmp + os.replace at end).
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException).
- `crlb_n/a`: "categorical accuracy on FHRR chain composition; primary
  discriminator is a STORAGE x N interaction deviation over sweep marginals,
  not a CRLB-governed quantity. SHARDED-PC-easy positive-control reproduces
  a known chain-grade primitive at test regime (Gate D compliance): SHARDED
  iterative_cosine at (M=200, N=4096, corr=0.20) matches prior CG (Option Y
  N=2048 SHARDED corr=0.20 M=800) primitives at test regime; tolerance 0.10."
- `discriminator_reachability`: True. H1 disc >= 0.10 at some cell; H2 disc <
  0.05 uniformly. H3 negative reversal. All measurable in [0.0, 1.0] range.
- `baseline_in_band`: mixed by design. SHARDED at (M=200, corr=0.20) is
  near-ceiling (PC arm, expected >= 0.90 per META_RULE_AG exempted for PC
  arm); BUNDLED at (M=3200, N=2048) is expected near-floor (M/N=1.56 far above
  Plate bound; PC-collapse arm). Mid-regime sweep points (M=800 corr=0.45 N=4096
  or 8192) predicted 0.30-0.85 discriminating band.
- `HP_SCOPE`: `{"SHARDED_arm": ["pc_easy_pass", "arms_differ", "monotonicity_check"],
  "BUNDLED_arm": ["storage_gap_pass", "monotonicity_check"], "cross_term_metric":
  ["storage_x_N_max_abs_deviation"]}`.
- `cell_chunked`: True (3 seed wrappers).
- `start_marker_written`: True (inherited from Probe 3 pattern).
- `crash_diagnostic_present`: True.
- `heartbeat_present`: per-phase-point print with flush=True.
- `defensive_error_checking`: `passed_all_4_patterns`.
- `sweep_alignment_verdict`: `ALIGNED` - STORAGE, N, M, corr are the actual
  primitives that experience each swept value; no partition-routing intermediation.
- `discriminating_fraction`: predicted 5/8 SHARDED sweep points and 3/6 BUNDLED
  sweep points in [0.30, 0.90] discriminating band (BUNDLED collapse at high
  M/N; SHARDED near-ceiling at low M; both mid-cells discriminate). Fraction
  ~= 8/14 = 0.57 >= 0.30 -> PASS Gate B.
- `composition_edges`: [{"from": "build_rules", "to": "run_chain",
  "A_natural_output_shape": "sharded_codebook + bundle_vec both complex64",
  "B_natural_input_shape": "storage flag selects one", "verdict": "SHAPE_MATCH"},
  {"from": "run_chain", "to": "cleanup_argmax_idx",
  "A_natural_output_shape": "final_ci LongTensor [TR]",
  "B_natural_input_shape": "N/A (called internally)", "verdict": "SHAPE_MATCH"}].
  All inherited from v1 factorial core.
- `positive_control_arms`:
  [{"arm": "SHARDED_iterative_cosine_at_M200_N4096_corr020",
    "primitive": "run_chain(storage=SHARDED, mechanism=iterative_cosine)",
    "cited_prior_atom": "stage1_physics_law_joint_composition_factorial_v1_s11_smoke",
    "cited_prior_metric": 1.0 (at M=800 N=2048 corr=0.20 SHARDED F=1),
    "test_regime": {"M": 200, "N": 4096, "F": 1, "L": 2, "corr": 0.20},
    "tolerance": 0.10,
    "if_outside_tolerance": "HARD_FAIL_INVOCATION_MISMATCH",
    "regime_extension_audit": "SHAPE_MATCH; same imported primitives; lower M
     (200 < 800), higher N (4096 > 2048) -> expected easier so acc >= 0.90 threshold
     is reachable."},
   {"arm": "storage_gap_SHARDED_minus_BUNDLED_at_bundle_collapse_regime",
    "primitive": "run_chain(storage in {SHARDED, BUNDLED}, mechanism=iterative_cosine)",
    "cited_prior_atom": "T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1",
    "cited_prior_metric": 0.30 (typical storage_gap at collapse regime),
    "test_regime": {"M": 800, "N": 2048, "F": 1, "L": 2, "corr": 0.45},
    "tolerance": 0.20 (broader; corr=0.45 harsher than typical PC),
    "if_outside_tolerance": "HARD_FAIL_STORAGE_ARM_BROKEN"}].
- `functional_requirements`:
  - FR-1: chain-composition varying N -> `run_chain(N=variable)` primitive.
  - FR-2: switch storage per phase point -> `build_rules` + `run_chain(storage=...)`.
  - FR-3: STORAGE x N interaction ANOVA deviation -> new logic in
    `aggregate_and_verdict`.
  - FR-4: monotonicity-break count per storage over N -> new logic
    (increment count if top1(N_{i+1}) - top1(N_i) < -0.05 at fixed M cliff).
- `progress_logging`: `print_flush_true`.
- `calibration_check`: `default_ok_for_this_regime` - BETA=8.0 ALPHA=0.5
  inherited from Option Y core where they passed selftest at F=1 across
  SHARDED and BUNDLED.

## Reachability of criteria

- SMOKE wall: ~30-90s on local CPU (5 pts; N up to 8192 dominates; each pt
  ~5-15s on CPU with iterative_cosine + argmax).
- FULL wall estimate: 48 pts * ~1-3s each on remote GPU ~= 1-3 min/seed;
  or ~5-10 min/seed on remote CPU. Timeout 3600s comfortable.

## Dispatch plan

- Local SMOKE: `local_cpu_queue` (SMOKE ONLY per USER-LOCKED 2026-07-01).
- Remote FULL: `overnight_queue` (GPU; matches Probe 3 dispatch route ~5-15
  GPU-sec/seed). Requires push to origin/main by Orchestrator (harness-denied
  to exp_dev).
