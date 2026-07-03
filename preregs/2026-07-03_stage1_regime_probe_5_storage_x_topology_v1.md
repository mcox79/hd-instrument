# Pre-registration: Regime Probe 5 - STORAGE x TOPOLOGY (F fan-in) cross-term

Date: 2026-07-03
Author: exp_dev (agent-spawn, Opus 4.7)
Anchor: `stage1_regime_probe_5_storage_x_topology_v1`
Sibling seeds: `_s7`, `_s13`, `_s19`
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER strategic direction 2026-07-03).

## Purpose (intuitive)

Fifth probe in the Stage 1 Regime Map arc. Prior probes established:
- Probe 1 (`stage1_regime_map_storage_x_cleanup_v1`) - STORAGE moderates CLEANUP_MECHANISM at 3-seed FULL (`mech_var@BUNDLED = 0.103 +/- 0.03`, T1 filed 18:16Z 2026-07-03).
- Probe 2 (`stage1_regime_probe_2_N_x_cleanup_mechanism_v1`) - N does NOT moderate CLEANUP_MECHANISM at SHARDED (null CG confirmed).
- Probe 3 (`regime_probe_3_topology_x_cleanup_v1`) - TOPOLOGY_FREE across F in {1,2,4,8} at SHARDED (pending FULL).
- Probe 4 (`stage1_regime_probe_4_storage_x_N_v1`) - STORAGE x N cross-term (SMOKE in flight).

Question: does STORAGE moderate TOPOLOGY_FREE too? I am extending Probes 1 and 4
to test the master-moderator claim on a THIRD axis. If STORAGE moderates
TOPOLOGY_FREE the same way it moderates CLEANUP_MECHANISM (Probe 1), the
STORAGE-as-master-axis reading strengthens. If not, STORAGE's moderating power
is either MECHANISM-specific or MECHANISM-and-N-specific (depending on Probe 4).

TOPOLOGY_FREE was established at SHARDED F in {1,2,4,8} (source atom:
`T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` +
`sharded_fhrr_topology_free_multi_f_dag_v1` HARD_PASS). This probe crosses
STORAGE with F to test whether the F-invariance of top1 is a SHARDED-only
property or extends to BUNDLED.

## Hypotheses (falsifiable)

- **H1 (STORAGE is master moderator):** TOPOLOGY_FREE holds at SHARDED
  (top1 curve F-invariant across {1,2,4,8}) but DEGRADES at BUNDLED (top1 has
  cliff or crossover in F) -> STORAGE moderates TOPOLOGY_FREE the same way it
  moderates MECHANISM -> STORAGE is master.
- **H2 (STORAGE special only for MECH):** TOPOLOGY_FREE holds at BOTH SHARDED
  and BUNDLED (top1 F-invariant either way) -> STORAGE's moderating power is
  specific to MECHANISM axis.
- **H3 (surprising crossover):** TOPOLOGY_FREE reverses direction at BUNDLED
  (higher F gives WORSE top1 more strongly). This is the non-monotonic outcome;
  would flag bundle-crosstalk interaction that grows with fan-in.

Distinguishing rule (measured at cliff corr=0.45; pooled over M):
- H1 <-> `storage_x_F_max_abs_deviation >= 0.10` AND
  `per_storage_F_monotonicity_break_count[BUNDLED] >= 1` while
  `per_storage_F_monotonicity_break_count[SHARDED] == 0`.
- H2 <-> `storage_x_F_max_abs_deviation < 0.05` AND F-invariant on both storages
  (max_delta_top1_across_F < 0.05 per storage).
- H3 <-> `bundled_top1(F=8) < bundled_top1(F=1) - 0.10` (reversal).

## Cited source atoms (exact names per META_RULE_AC + MM_STANDARD)

- `META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` (T4) -
  TOPOLOGY_FREE physics law established 2026-07-02 at SHARDED.
  HYPOTHESIZED@Director framing 2026-07-03.
- `MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP...` (T1, filed 18:16Z 2026-07-03) -
  Probe 1 result: STORAGE moderates CLEANUP_MECHANISM.
- `META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_PROMOTION_MM_TENTATIVE_to_CG_META_CONFIRMED`
  (T4, filed 18:16Z 2026-07-03) - Probe 1 CG_META confirmation.
- `sharded_fhrr_topology_free_multi_f_dag_v1` MEASURED@
  `data/exp_sharded_fhrr_topology_free_multi_f_dag_v1/metrics.json`
  (HARD_PASS TOPOLOGY_FREE across F {1,2,4,8} at SHARDED).
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` -
  SHARDED-vs-BUNDLED chain-depth physics law established 2026-07-02.
- `stage1_regime_probe_2_N_x_cleanup_mechanism_v1` - null Probe 2.
- `regime_probe_3_topology_x_cleanup_v1` - null Probe 3 (F-invariant at SHARDED).
- `stage1_regime_map_storage_x_cleanup_v1` - Probe 1 3-seed FULL result.
- `stage1_regime_probe_4_storage_x_N_v1` - Probe 4 STORAGE x N (in flight).
- `stage1_physics_law_joint_composition_factorial_v1_s11` - Option Y source of
  imported primitives (`build_rules`, `run_chain`, `cleanup_argmax_idx`).
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`
  - SMOKE-gate discipline for null-hypothesis probes.
- `feedback_orchestrator_hallucination_pattern_verify_disk_before_propagating_2026-07-03`
  - post-dispatch verify path is disk-not-agent-report.

## Substrate-KB concept-query result

Query: `"STORAGE topology fan-in F cross-term BUNDLED SHARDED TOPOLOGY_FREE moderator"`.
Top-5 cosines 0.337-0.411; only the abstract wordnet entity `topology`
(cosine=0.411) exceeds 0.40. Substrate-atom hits above 0.30:
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1`
  (cosine=0.348) - the source atom this probe extends.
- `sharded_fhrr_topology_free_multi_f_dag_v1` (cosine=0.337) - source metrics
  where TOPOLOGY_FREE was established at SHARDED.

**No prior STORAGE x TOPOLOGY cross-term probe exists.** The extension of
TOPOLOGY_FREE across the STORAGE axis (i.e. whether BUNDLED preserves
F-invariance) has NOT been directly explored. Genuinely novel arc extension.

Prior-work check result: `NONE at cosine>0.30 that is substantively related to
the STORAGE x TOPOLOGY cross-term; genuinely novel arc extension`.

## Compute architecture

- Class: `(a) batched-GPU` - reuses batched-GPU primitives from
  `_stage1_physics_law_joint_composition_factorial_v1_core` (torch.cuda when
  available; CPU fallback for local smoke).
- Storage strategy: mixed (SHARDED and BUNDLED both as discriminator arms; per
  META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW BUNDLED is the collapse
  arm intentional for this cross-term).
- Progress logging: `print_flush_true`.
- Timeout budget: SMOKE ~30-90s local CPU; FULL ~2-5 min per seed on remote GPU
  or ~5-10 min per seed on remote CPU (matches Probe 3 F-sweep + Probe 4 wall).

## Design

### Sweep axes

- STORAGE in {SHARDED, BUNDLED} - 2 levels (primary axis).
- F in {1, 2, 4, 8} - 4 levels (TOPOLOGY fan-in; matches Probe 3 range and
  source atom `sharded_fhrr_topology_free_multi_f_dag_v1` tested range).
- M in {200, 800, 3200} - 3 levels (M scaling).
- corruption in {0.20, 0.45} - 2 levels.
- CLEANUP_MECHANISM FIXED = `iterative_cosine` (Probe 1 winner; simplest for
  isolation).
- N=4096, L=2 fixed.

### Cardinality

- FULL: 2 * 4 * 3 * 2 = **48 phase points / seed** x 3 seeds = 144.
  - `EXPECTED_N_UNITS_FULL = 48`
- SMOKE: 2 * 2 * 1 * 1 = **4 sweep pts + 1 SHARDED_PC_easy = 5 / seed** x 1 seed = 5.
  - `EXPECTED_N_UNITS_SMOKE = 5`
  - Smoke fixed: F in {1, 4}, M = 800, corr = 0.45 (cliff). Keep smoke short
    while spanning 2-octave F contrast. SHARDED_PC_easy point added at
    (SHARDED, F=1, M=200, N=4096, corr=0.20, iterative_cosine, L=2) since
    smoke sweep does not include M=200 or corr=0.20; PC-easy needed for
    positive-control gate.

### Reuse (Principle 11)

- Primitives (`build_rules`, `run_chain`, `CLEANUP_REGISTRY`, `phase_corrupt`,
  `cphasor_torch`, `BETA`, `ALPHA_SOFT`, `DEVICE`, `GPU_NAME`) imported from
  `experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py`.
- Structure adapted from `_stage1_regime_probe_4_storage_x_N_v1_core.py`
  (identical 2 x 4 x 3 x 2 sweep shape; N and F axes swapped).
- New file: `experiments/_stage1_regime_probe_5_storage_x_topology_v1_core.py` -
  defines sweep, verdict logic, per-storage per-F TOPOLOGY curve calc,
  STORAGE x F ANOVA interaction, monotonicity-break count.
- Seed wrappers: `experiments/exp_stage1_regime_probe_5_storage_x_topology_v1_s{7,13,19}.py`.

## SMOKE HP criteria (SHIP FULL if all met)

Per null-hypothesis SMOKE gate discipline (memory rule
`feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`):
SMOKE does NOT gate on discriminator firing. It gates on plumbing + positive
controls only. H2 (null-result) must remain reachable.

1. `selftest_ok` (returns True; cardinality + storages-produce-distinct-outputs
   at PC regime + SHARDED PC easy passes + F-axis fires distinct codebooks).
2. `cardinality_ok` (observed 5 = expected 5).
3. `arms_differ_verified` (SHARDED and BUNDLED produce distinct output-hash
   aggregates across sweep points; META_RULE_AF).
4. `pc_easy_pass`: SHARDED at (M=200, N=4096, corr=0.20, F=1, L=2,
   iterative_cosine) acc >= 0.90 (positive control per USER spawn prompt).
5. `storage_gap_pass`: at (M=800, corr=0.45) sweep point where M/N=0.20 (above
   Plate 1995 bundle bound 0.14), the storage gap
   `SHARDED_acc - BUNDLED_acc >= 0.30`. Applied at F=1 (baseline TOPOLOGY);
   this asserts BUNDLED-vs-SHARDED discriminator arm actually differentiates
   in the smoke regime.
6. **INFORMATIONAL (does NOT gate; per null-hypothesis discipline):**
   `storage_x_F_smoke_deviation = storage_gap(F=4) - storage_gap(F=1)`.
   Report the value. Change in storage gap across F is a preview of H1
   vs H2. Do NOT reject SMOKE on any value; report for Director interpretation.

## FULL HARD_PASS_CG_TIER criteria

1. `cardinality_ok` per seed (48 pts each).
2. `arms_differ_verified` across seeds.
3. `pc_easy_pass` at (SHARDED, F=1, M=200, N=4096, corr=0.20) queried from
   sweep: acc >= 0.90.
4. 3-seed CV `< 0.10` per phase point (accuracy stability).
5. **Primary discriminator: STORAGE x F cross-term ANOVA deviation.**
   - `storage_x_F_max_abs_deviation >= 0.10` AND
     `per_storage_F_monotonicity_break_count[BUNDLED] >= 1` AND
     `per_storage_F_monotonicity_break_count[SHARDED] == 0`
     -> **HARD_PASS_H1_STORAGE_MASTER_MODERATOR_TOPOLOGY_BREAKS_AT_BUNDLED**:
     STORAGE is master; TOPOLOGY_FREE is SHARDED-only property.
   - `storage_x_F_max_abs_deviation < 0.05` AND
     BOTH storages F-invariant (max delta_top1 across F < 0.05 per storage)
     -> **HARD_PASS_H2_STORAGE_SPECIAL_ONLY_FOR_MECHANISM**: STORAGE's
     moderating power is specific to CLEANUP_MECHANISM axis; TOPOLOGY_FREE
     extends across storage.
   - `bundled_top1(F=8) < bundled_top1(F=1) - 0.10` at fixed M (pooled at
     cliff corr=0.45)
     -> **HARD_PASS_H3_BUNDLED_TOPOLOGY_REVERSAL**: bigger F gives worse
     BUNDLED top1; bundle-crosstalk-vs-signal balance interacts adversely
     with fan-in.
6. 3-seed replication + Skunkworks landed-VET before CG atom filing.

## HARD_FAIL

- cardinality breach (any seed missing pts).
- `pc_easy_pass` fails (SHARDED PC easy < 0.90 -> primitive reproduction broken).
- selftest fails.
- storage_gap at BUNDLED collapse regime < 0.20 (arms don't differ ->
  discriminator arm broken).

## MIDDLE_BAND

- `0.05 <= storage_x_F_max_abs_deviation < 0.10` (weak STORAGE x F interaction).
- Mixed monotonicity signal (both storages have breaks or neither has).
- File as MM_TENTATIVE crossover.

## SCHEMA-VET checklist (all True/present)

- `cardinality_ok`: True (48 FULL / 5 SMOKE).
- `arms_differ_verified`: True (SHARDED vs BUNDLED bundle_hash / output_hash
  aggregates over sweep pts; META_RULE_AF; also F axis produces distinct
  codebook hashes across F values in selftest).
- `final_metrics_atomicity`: `tmp_replace` (atomic tmp + os.replace at end).
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException).
- `crlb_n/a`: "categorical accuracy on FHRR chain composition; primary
  discriminator is a STORAGE x F interaction deviation over sweep marginals,
  not a CRLB-governed quantity. SHARDED-PC-easy positive-control reproduces a
  known chain-grade primitive at test regime (Gate D compliance):
  SHARDED iterative_cosine at (M=200, N=4096, F=1, corr=0.20) matches prior CG
  (Option Y N=2048 SHARDED F=1 corr=0.20 M=800) primitives at test regime;
  tolerance 0.10."
- `discriminator_reachability`: True. H1 disc >= 0.10 at some cell; H2 disc <
  0.05 uniformly. H3 negative reversal. All measurable in [0.0, 1.0] range.
- `baseline_in_band`: mixed by design. SHARDED at (M=200, corr=0.20) is
  near-ceiling (PC arm, expected >= 0.90 per META_RULE_AG exempted for PC arm);
  BUNDLED at (M=3200, F=8) is expected near-floor (M/N=0.78 far above Plate
  bound AND fan-in amplifies bundle crosstalk; PC-collapse arm). Mid-regime
  sweep points (M=800 corr=0.45 F=2 or 4) predicted 0.30-0.85 discriminating
  band.
- `HP_SCOPE`: `{"SHARDED_arm": ["pc_easy_pass", "arms_differ", "monotonicity_check"],
  "BUNDLED_arm": ["storage_gap_pass", "monotonicity_check"], "cross_term_metric":
  ["storage_x_F_max_abs_deviation"]}`.
- `cell_chunked`: True (3 seed wrappers).
- `start_marker_written`: True (inherited from Probe 3/4 pattern).
- `crash_diagnostic_present`: True.
- `heartbeat_present`: per-phase-point print with flush=True.
- `defensive_error_checking`: `passed_all_4_patterns`.
- `sweep_alignment_verdict`: `ALIGNED` - STORAGE, F, M, corr are the actual
  primitives that experience each swept value; no partition-routing.
- `discriminating_fraction`: predicted 5/8 SHARDED sweep points and 3/6 BUNDLED
  sweep points in [0.30, 0.90] discriminating band (BUNDLED collapse at high
  M/N + F; SHARDED near-ceiling at low M; mid-cells discriminate). Fraction
  ~= 8/14 = 0.57 >= 0.30 -> PASS Gate B.
- `composition_edges`: [{"from": "build_rules", "to": "run_chain",
  "A_natural_output_shape": "sharded_codebook + bundle_vec both complex64",
  "B_natural_input_shape": "storage flag selects one", "verdict": "SHAPE_MATCH"},
  {"from": "run_chain", "to": "cleanup_argmax_idx",
  "A_natural_output_shape": "final_ci LongTensor [TR]",
  "B_natural_input_shape": "N/A (called internally)", "verdict": "SHAPE_MATCH"}].
  All inherited from v1 factorial core.
- `positive_control_arms`:
  [{"arm": "SHARDED_iterative_cosine_at_M200_N4096_F1_corr020",
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
    "test_regime": {"M": 800, "N": 4096, "F": 1, "L": 2, "corr": 0.45},
    "tolerance": 0.20,
    "if_outside_tolerance": "HARD_FAIL_STORAGE_ARM_BROKEN"}].
- `functional_requirements`:
  - FR-1: chain-composition varying F -> `run_chain(F=variable)` primitive.
  - FR-2: switch storage per phase point -> `build_rules` + `run_chain(storage=...)`.
  - FR-3: STORAGE x F interaction ANOVA deviation -> new logic in
    `aggregate_and_verdict`.
  - FR-4: monotonicity-break count per storage over F -> new logic
    (increment count if top1(F_{i+1}) - top1(F_i) < -0.05 at cliff corr).
- `progress_logging`: `print_flush_true`.
- `calibration_check`: `default_ok_for_this_regime` - BETA=8.0 ALPHA=0.5
  inherited from Option Y core where they passed selftest at F in {1,2,4,8}
  across SHARDED and BUNDLED (Probe 3 selftest).

## Reachability of criteria

- SMOKE wall: ~30-90s on local CPU (5 pts; F up to 4 at N=4096; each pt
  ~5-15s on CPU with iterative_cosine + argmax; F=4 slightly longer than F=1).
- FULL wall estimate: 48 pts * ~1-3s each on remote GPU ~= 1-3 min/seed;
  or ~5-10 min/seed on remote CPU. Timeout 3600s comfortable.

## Dispatch plan

- Local SMOKE: `local_cpu_queue` (SMOKE ONLY per USER-LOCKED 2026-07-01).
- Remote FULL: `overnight_queue` (GPU; matches Probe 3 and Probe 4 dispatch
  route). Requires push to origin/main by Orchestrator (harness-denied to
  exp_dev). Post-landing verify path MUST be disk-inspection of metrics.json
  files (not orchestrator agent-report) per
  `feedback_orchestrator_hallucination_pattern_verify_disk_before_propagating_2026-07-03`.
