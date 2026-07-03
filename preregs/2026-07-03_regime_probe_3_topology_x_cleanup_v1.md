# Pre-registration: Regime Probe 3 — TOPOLOGY (F fan-in) x CLEANUP_MECHANISM cross-term

Date: 2026-07-03
Author: exp_dev (agent-spawn, Opus 4.7)
Anchor: `regime_probe_3_topology_x_cleanup_v1`
Sibling seeds: `_s7`, `_s13`, `_s19`
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER strategic direction 2026-07-03).
Arc note: `notes/project_stage1_regime_map_of_CG_META_axes_USER_2026-07-03.md`.

## Purpose (intuitive)

Third probe in the Stage 1 Regime Map arc. Probe 1 (STORAGE x CLEANUP_MECHANISM) is
filed at `preregs/2026-07-03_stage1_regime_map_storage_x_cleanup_first_probe.md`.
This probe fixes STORAGE = SHARDED and varies TOPOLOGY (F fan-out / fan-in in the
sharded DAG) x CLEANUP_MECHANISM.

The question: Option Y (`stage1_physics_law_joint_composition_factorial_v1_s11`
smoke, 2026-07-03) measured `max_mechanism_variation_at_cliff = 0.0` at SHARDED, F=1.
Does encoder TOPOLOGY (F) moderate that mechanism-degeneracy? If yes, another
boundary point in the regime map. If no, Option Y's finding extends across F.

## Hypotheses (falsifiable)

- **H1 (regime-boundary extends across F):** at all F in {1,2,4,8}, mechanism-axis
  variance stays close to 0 -> confirms CLEANUP_MECHANISM regime-narrow claim
  extends across encoder topology.
- **H2 (F-dependent boundary):** mechanism variance appears at some F but not
  others -> crossover exponent in F. Topology moderates cleanup-mechanism
  degeneracy.
- **H3 (DAG multi-source aggregation moderates):** at F > 1, the multi-source
  structure changes cleanup-mechanism sensitivity. Sub-case of H2.

Distinguishing rule: H1 <-> max_per_F_mech_variance < 0.05 AND F_x_cleanup_max_dev
< 0.05. H2/H3 <-> either metric >= threshold at some slice.

## Cited source atoms (exact names per META_RULE_AC + MM_STANDARD)

- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` — TOPOLOGY
  axis established 2026-07-02; F ∈ {1, 2, 4, 8, MIXED} at sharded FHRR.
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` — SHARDED-vs-BUNDLED
  chain-depth physics law established 2026-07-02.
- `T4/META_SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1_2026-07-02` — L
  algebra axis established 2026-07-02.
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` — bipolar-codebook regime
  M-sweep 2026-07-03; source of the 3 non-Hebbian mechanisms tested here.
- `stage1_physics_law_joint_composition_factorial_v1_s11_smoke` MEASURED@
  `data/exp_stage1_physics_law_joint_composition_factorial_v1_s11_smoke/metrics.json:
  max_mechanism_variation_at_cliff = 0.0` (source of the observation this probe
  extends).
- `feedback_chain_grade_primitives_not_trivially_composable_2026-06-28.md` —
  regime SHAPE_DRIFT audit discipline.

## Compute architecture

- Class: `(a) batched-GPU` — reuses batched-GPU primitives from
  `_stage1_physics_law_joint_composition_factorial_v1_core` (torch.cuda when
  available; CPU fallback for local smoke).
- Storage strategy: `sharded` for main factorial + one FIXED-regime BUNDLED PC
  arm (positive control per Gate D and META_RULE_AG storage-gap check).
- Progress logging: `print_flush_true` (per-phase-point + per-seed prints all use
  `flush=True`; PROT-024 compliant).
- Timeout budget: SMOKE ~30s local CPU; FULL ~5-10min per seed on remote CPU.

## Design

### Sweep axes

- CLEANUP_MECHANISM ∈ {modern_hopfield, iterative_cosine, soft_energy_attractor}
  (3 non-Hebbian).
- F ∈ {1, 2, 4, 8} (4 topology values; matches TOPOLOGY_FREE atom's range).
- M ∈ {200, 800, 3200} (M-scaling axis).
- corruption ∈ {0.20, 0.45} (cleanup-regime probe).
- Fixed: N = 4096 (mid-range).
- Fixed: L = 2.
- Fixed: STORAGE = SHARDED (main factorial); +1 BUNDLED PC arm at fixed regime.

### Cardinality

- FULL: 3 * 4 * 3 * 2 = **72 SHARDED phase points + 1 BUNDLED PC = 73/seed** x 3
  seeds = 219.
  - `EXPECTED_N_UNITS_FULL = 73`
- SMOKE: 3 * 2 * 1 * 1 = **6 SHARDED phase points + 1 BUNDLED PC = 7/seed** x 1
  seed = 7.
  - `EXPECTED_N_UNITS_SMOKE = 7`
  - Smoke fixed: F ∈ {1, 4}, M = 800, corr = 0.45. Chosen to keep smoke short
    while still exercising the F axis and the hardest corruption regime.

### Reuse (Principle 11)

- Primitives (`cphasor_torch`, `cnorm_torch`, `phase_corrupt`, `build_rules`,
  `run_chain`, `CLEANUP_REGISTRY`, `CLEANUP_MECHANISMS`, `BETA`, `ALPHA_SOFT`)
  imported from `experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py`.
- New file: `experiments/_regime_probe_3_topology_x_cleanup_v1_core.py` — defines
  the sweep, verdict logic, per-F mechanism-variance calculation, F x CLEANUP
  interaction ANOVA calculation.
- Seed wrappers: `experiments/exp_regime_probe_3_topology_x_cleanup_v1_s{7,13,19}.py`.

## SMOKE HP criteria (SHIP FULL if all met)

1. `selftest_ok` (returns True; imported cardinality + 3-mech-distinct + F-axis-
   fires + SHARDED-PC-easy gate).
2. `cardinality_ok` (observed 7 = expected 7).
3. `arms_differ_verified` (3 distinct mechanism output-hash aggregates across
   SHARDED points; META_RULE_AF).
4. `pc_reproduce_iterative_cosine_regime.pass` (SHARDED iterative_cosine at
   F=min-F=1, M=800, corr=0.45 acc >= 0.60 threshold; smoke uses cliff corruption
   so threshold is loosened).
5. `storage_gap_sharded_minus_bundled >= 0.15` at BUNDLED PC regime (M=800,
   N=4096, F=1, L=2, corr=0.20, iterative_cosine).
6. **KEY smoke discriminator (informational, not gating):** `max_per_F_mech_variance`
   across F ∈ {1, 4} at cliff corr=0.45. Report the value.
   - If `max_per_F_mech_variance == 0.0` at both F=1 AND F=4 -> preliminary
     evidence H1 extends (mechanism-axis degeneracy independent of F). FULL
     warranted to confirm at wider F grid + wider M/corr grid.
   - If `max_per_F_mech_variance >= 0.05` at F=1 OR F=4 -> preliminary evidence
     H2/H3 (F-dependent boundary). FULL warranted to characterize.
   - Either outcome is INFORMATIVE and does not gate SMOKE PASS.

## FULL HARD_PASS_CG_TIER criteria

1. `cardinality_ok` per seed (73 pts each).
2. `arms_differ_verified` across seeds.
3. `pc_reproduce_iterative_cosine_regime.pass` at PC regime (acc >= 0.75).
4. 3-seed CV `< 0.10` per phase point (accuracy stability).
5. **Primary discriminator: F x CLEANUP_MECHANISM cross-term.**
   - `max_per_F_mech_variance < 0.05` AND `F_x_cleanup_max_abs_deviation < 0.05`
     -> **HARD_PASS_H1_MECHANISM_DEGENERACY_EXTENDS_ACROSS_TOPOLOGY**:
     Option Y's SHARDED F=1 finding extends across F in {1, 2, 4, 8}; the
     CLEANUP_MECHANISM axis is truly regime-narrow (bipolar-codebook only) and
     encoder topology does not rescue mechanism variance.
   - `max_per_F_mech_variance >= 0.10` OR `F_x_cleanup_max_abs_deviation >= 0.15`
     -> **HARD_PASS_H2_F_DEPENDENT_MECHANISM_BOUNDARY**: topology moderates
     cleanup-mechanism degeneracy; REGIME MAP has an F-dependent boundary point.
6. 3-seed replication + Skunkworks landed-VET before CG atom filing.

## HARD_FAIL

- cardinality breach (any seed missing pts).
- PC storage-gap `< 0.15` at PC regime (SHARDED-BUNDLED distinction collapses;
  invalidates storage-axis baseline).
- selftest fails.
- PC reproduction fails (SHARDED iterative_cosine PC acc below threshold).

## MIDDLE_BAND

- `0.05 <= max_per_F_mech_variance < 0.10` OR `0.05 <= F_x_cleanup_max_abs_deviation
  < 0.15` -> weak F-moderation regime; file as MM_TENTATIVE crossover.

## SCHEMA-VET checklist (all True/present)

- `cardinality_ok`: True (73 FULL / 7 SMOKE)
- `arms_differ_verified`: True (3 distinct cleanup mechanisms; run-time hash check
  in selftest at F=2 multi-slot path + aggregate hash check in run_one_seed)
- `final_metrics_atomicity`: `tmp_replace` (atomic tmp + os.replace at end)
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException)
- `crlb_n/a`: "categorical accuracy on FHRR chain composition; discriminator is
  cross-term interaction deviation not a CRLB-governed quantity. Positive-control
  reproduces the same primitives at the test regime (Gate D compliance)."
- `discriminator_reachability`: True. If H1 correct, disc = 0 measured, gate
  fires. If H2/H3 correct, disc >= 0.05 at some F, gate fires. Either outcome is
  measurable.
- `baseline_in_band`: mixed. SHARDED at cliff corr=0.45 is expected to be in
  measurable band (not saturated) especially at M=3200 approaching capacity;
  SHARDED at M=200 corr=0.20 near-ceiling by prior CG (acceptable per HP_SCOPE
  since that arm is the positive control).
- `HP_SCOPE`: {`SHARDED_arm`: [`arms_differ`, `cardinality_ok`, `pc_reproduce`],
  `BUNDLED_PC_arm`: [`storage_gap >= 0.15`],
  `per_F_variance_metric`: [`max_per_F_mech_variance`, `F_x_cleanup_deviation`]}
- `cell_chunked`: True (3 seed wrappers)
- `start_marker_written`: True (inherited from v1 factorial pattern)
- `crash_diagnostic_present`: True
- `heartbeat_present`: per-phase-point print with flush=True
- `defensive_error_checking`: `passed_all_4_patterns`
- `sweep_alignment_verdict`: `ALIGNED` — F, CLEANUP_MECHANISM, M, N, corr are
  the actual primitives that experience each swept value; no partition-routing
  intermediation.
- `discriminating_fraction`: SHARDED at cliff corr=0.45 across (M=200, 800, 3200)
  is expected to span [0.3, 0.9] band; BUNDLED PC expected < 0.5 at M=800 N=4096
  (Plate bound 0.14*4096 = 573 -> M=800 above bound -> collapse). Predict >= 60%
  smoke pts in discriminating band.
- `composition_edges`: [`build_rules -> run_chain: SHAPE_MATCH`,
  `run_chain -> cleanup_argmax_idx: SHAPE_MATCH`, all inherited from v1 core].
- `positive_control_arms`: [{arm: `sharded_iterative_cosine_at_smoke_PC_regime`,
  primitive: `run_chain(storage=SHARDED, mechanism=iterative_cosine)`,
  cited_prior_atom: `stage1_physics_law_joint_composition_factorial_v1_s11_smoke`,
  cited_prior_metric: 1.0 (at M=800 N=2048 corr=0.20 SHARDED F=1),
  test_regime: {M: 800, N: 4096, F: 1, L: 2, corr: 0.45},
  tolerance: 0.30 (broader — higher corruption 0.45 vs cited 0.20),
  if_outside_tolerance: `HARD_FAIL_INVOCATION_MISMATCH`,
  regime_extension_audit: `SHAPE_MATCH`: same imported primitives; corruption
  differs (0.20 -> 0.45), documented risk; also add secondary N=2048 vs 4096
  check via internal SHARDED PC easy in selftest.
  }].
- `functional_requirements`:
  - FR-1: chain-composition (rule storage + unbind + cleanup + readout at
    varying F fan-out) -> `run_chain` primitive (imported).
  - FR-2: F-varying sharded codebook -> `build_rules(F=F)` primitive (imported).
  - FR-3: 3-mechanism cleanup families -> `CLEANUP_REGISTRY` (imported).
  - FR-4: F x CLEANUP interaction ANOVA deviation calculation -> new logic in
    this cell's `aggregate_and_verdict`.
- `progress_logging`: `print_flush_true`
- `calibration_check`: `default_ok_for_this_regime` — BETA=8.0 ALPHA=0.5
  inherited from Option Y core where they passed selftest at F=1 and F=2.

## Reachability of criteria

- SMOKE wall: ~20-60s on local CPU (7 pts x ~2-8s/pt at N=4096; small M=800).
- FULL wall estimate: 73 pts * ~1-3s each on remote CPU ~= 3-8 min/seed;
  timeout 3600s comfortable. GPU wall much shorter.

## Substrate-KB concept-query result

Query: `"cleanup mechanism topology fan-in cross-term FHRR"`. Top-5 cosines
0.271-0.305; **only 1 hit at 0.30 threshold** (top-1 "Mechanism" cosine=0.3047,
weakly related). Below 0.30 = cross-term (TOPOLOGY x CLEANUP_MECHANISM) has not
been directly explored. Prior-work check result: `NONE at cosine>0.30 that is
substantively related; genuinely novel arc extension`.

## Dispatch plan

- Local SMOKE: `local_cpu_queue` (SMOKE ONLY per USER-LOCKED 2026-07-01).
- Remote FULL: `remote_cpu_queue` (marsh@home CPU; 3 seeds parallel).
  Requires push to origin/main by Orchestrator (harness-denied to exp_dev).
