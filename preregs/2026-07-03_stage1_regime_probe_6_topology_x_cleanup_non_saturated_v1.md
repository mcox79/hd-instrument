# Pre-registration: Regime Probe 6 — TOPOLOGY x CLEANUP_MECHANISM (NON-SATURATED regime revival of Probe 3)

Date: 2026-07-03
Author: exp_dev (agent-spawn, Opus 4.7)
Anchor: `stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1`
Sibling seeds: `_s7`, `_s13`, `_s19`
Arc: Stage 1 REGIME MAP of CG_META axes (USER strategic direction 2026-07-03).

## Purpose (intuitive)

Skunkworks VET of Probe 3 (TOPOLOGY x CLEANUP_MECHANISM at N=4096 fixed, corruption in {0.20, 0.45}, M in {200, 800, 3200}) revealed that ALL 72 phase points reached acc=1.0. The null-result "TOPOLOGY does not moderate CLEANUP_MECHANISM" is SATURATION-VACUOUS — mechanism variance cannot be nonzero when all mechanisms trivially saturate.

To actually test the hypothesis, we need to force the regime BELOW saturation so mechanism variance has room to appear. This probe:

- Adds F=16 (satisfies Skunkworks revival criterion `F >= 16`)
- Adds corruption ∈ {0.60, 0.70} (satisfies revival criterion `corr >= 0.6`)
- Extends M ∈ {800, 3200, 6400} (M=6400 well above Plate 0.14*N bound at N=8192 → sharded_pc drops below 0.95 as revival requires `M such that sharded_pc < 0.95`)
- Sweeps N ∈ {2048, 8192} (2 levels of scale)

If mechanism variance now appears in the non-saturated regimes → Probe 3's null was saturation artifact; TOPOLOGY IS a moderator.
If mechanism variance still ~0 at non-saturated mean-acc in [0.30, 0.95] → genuine null; Probe 3 lesson reinforced with non-vacuous evidence.

## Hypotheses (falsifiable)

- **H1 (TOPOLOGY moderates when non-saturated):** at slices with grand-mean(acc) in [0.30, 0.95] band, `F_x_cleanup_max_abs_deviation` >= 0.05 (which is 3σ scale for accuracy noise; see reachability). Confirms Probe 3's null was saturation artifact; **TOPOLOGY is a moderator**.
- **H2 (TOPOLOGY genuinely does NOT moderate):** at non-saturated slices, mechanism variance stays < 0.05 → Probe 3's null result holds at NEW REGIMES (not saturation-vacuous). Validates Probe 1's "STORAGE UNIQUELY moderates" thesis.
- **H3 (surprising crossover):** mechanism ranking changes with F within non-saturated slices → published F-dependent crossover exponent.

## Cited source atoms (exact names per META_RULE_AC + MM_STANDARD)

- `META_saturation_floor_masks_null_variance_probe3_lesson` (T4 MM_STANDARD METHODOLOGY_RULE, filed 2026-07-03 18:29Z) — SATURATION-VACUOUS meta rule that gates this revival.
- `regime_probe_3_topology_x_cleanup_v1_MM_BOUNDED_NULL` (T3 MM_BOUNDED_NULL) — the Probe 3 landing being revived here.
- `MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1` — Probe 1 CG_META template for the working non-saturated regime.
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` — TOPOLOGY axis established 2026-07-02; F ∈ {1, 2, 4, 8, MIXED} at sharded FHRR.
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` — SHARDED-vs-BUNDLED chain-depth physics law 2026-07-02.
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` — bipolar-codebook regime M-sweep 2026-07-03; source of the 3 non-Hebbian mechanisms tested here.
- 2026-06-18 associative-memory BY-CONSTRUCTION saturation tiering discipline (memory: `reference_associative_memory_cell_noise_scaling_bug_and_by_construction_saturation_tiering_2026-06-18.md`).
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03` — SMOKE gate discipline for null-hypothesis-plausible probes.

## Prior-work check (substrate-KB query)

Query: `"TOPOLOGY sharded bundled CLEANUP_MECHANISM cross-term non-saturated regime"`.
Top-5 cosines: 0.2822, 0.2773, 0.2715, 0.2695, 0.2637. **NONE at cosine > 0.30 threshold.**
The non-saturated cross-term revival with N-sweep + higher-M + higher-corruption is a genuinely novel arc extension. Probe 3 is closest CG landing but its saturated regime does not test the same question.

## Compute architecture

- Class: `(a) batched-GPU` — reuses batched-GPU primitives from `_stage1_physics_law_joint_composition_factorial_v1_core` (torch.cuda when available; CPU fallback for local smoke). N=8192 M=6400 phase points are matmul-dominated — batched-GPU mandatory.
- Storage strategy: `sharded` for entire main factorial (Probe 6 is TOPOLOGY x CLEANUP; STORAGE is not swept). One SATURATION positive-control point (SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine → reproduces Probe 3 baseline acc=1.0).
- Progress logging: `print_flush_true` (per-phase-point + per-seed prints all use `flush=True`; PROT-024 compliant).
- Timeout budget: SMOKE ~30-60s local CPU (7 pts at N=2048 M=3200); FULL ~10-20 min per seed on remote GPU (217 pts, mostly N=8192 M=6400).

## Design (v2 revised 2026-07-03 after v1 SMOKE HONEST_FAIL bracketing)

### v2 revision note

v1 SMOKE (M=3200 N=2048 corr=0.60) landed HARD_FAIL_SMOKE escapes_saturation_ceiling
(all 7 pts at acc=1.0000). Exp_dev's bracketing probe found the actual
non-saturated boundary in SHARDED-rule-storage FHRR chain composition sits at
SMALLER N (not larger N as v1 assumed) and higher corruption. Plate 0.14*N bound
was 5-10x too pessimistic. See memory rule `feedback_plate_bound_too_pessimistic_
for_sharded_fhrr_chain_composition_2026-07-03.md`. v2 grid uses EMPIRICAL rather
than theoretical cliff. Cardinality preserved: still 217/7.

### Sweep axes (FULL, v2)

- CLEANUP_MECHANISM ∈ {modern_hopfield, iterative_cosine, soft_energy_attractor}
- F ∈ {1, 4, 8, 16}  (revival criterion F >= 16 satisfied)
- M ∈ {800, 3200, 6400}  (unchanged from v1)
- N ∈ {512, 2048}  (v2: smaller N is where non-saturation happens; v1 [2048, 8192] never left ceiling)
- corruption ∈ {0.70, 0.85, 0.90}  (v2: empirical brackets non-saturated band)
- Fixed: L = 2
- Fixed: STORAGE = SHARDED

### Sweep axes (SMOKE, v2)

- CLEANUP_MECHANISM ∈ {modern_hopfield, iterative_cosine, soft_energy_attractor}
- F ∈ {1, 16}  (min + max of F axis; exercises TOPOLOGY axis endpoints)
- M ∈ {6400}
- N ∈ {512}
- corruption ∈ {0.85}
- Empirical bracket at v1-SMOKE-time (F=16 mech=iterative_cosine): N=512 M=3200 corr=0.85 -> acc=0.867 (in-band).
  At M=6400, expect mid-band ~[0.3, 0.9] across F=[1, 16] x 3 mechs.

### Cardinality

- FULL: 3 * 4 * 3 * 2 * 3 = **216 SHARDED main + 1 SATURATION_PC = 217 pts/seed** x 3 seeds = 651.
  - `EXPECTED_N_UNITS_FULL = 217`
- SMOKE: 3 * 2 * 1 * 1 * 1 = **6 SHARDED main + 1 SATURATION_PC = 7 pts** x 1 seed = 7.
  - `EXPECTED_N_UNITS_SMOKE = 7`

### Positive control (Gate D — reproduces Probe 3 baseline)

At `SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine`, cell must reproduce acc >= 0.95 (Probe 3 baseline). This is the SATURATION_PC arm — its purpose is to prove the cell's primitive-invocation matches Probe 3's substrate physics.
- Cited prior atom: `regime_probe_3_topology_x_cleanup_v1` (all 72 SHARDED pts at acc=1.0).
- Cited prior metric: 1.0.
- Tolerance: 0.05 (acc >= 0.95 acceptable).

### Reuse (Principle 11 — cite EXACT signatures per MM_STANDARD)

- Primitives (`cphasor_torch`, `cnorm_torch`, `phase_corrupt`, `build_rules`, `run_chain`, `CLEANUP_REGISTRY`, `CLEANUP_MECHANISMS`, `BETA`, `ALPHA_SOFT`) imported from `experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py` (Option Y core scaffold).
- Verdict + interaction-ANOVA logic modeled on `experiments/_regime_probe_3_topology_x_cleanup_v1_core.py`.
- New file: `experiments/_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1_core.py`.
- Seed wrappers: `experiments/exp_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1_s{7,13,19}.py`.

## SMOKE HP criteria (SHIP FULL if all met)

Per `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`: SMOKE gate is on INFRASTRUCTURE + POSITIVE CONTROL ONLY. Do NOT gate on discriminator variance firing — H2 (null) is a legitimate hypothesis-supportive outcome for this probe.

1. `selftest_ok` (imported cardinality + 3-mech-distinct + F-axis-fires + SHARDED PC easy gate).
2. `cardinality_ok` (observed 7 = expected 7).
3. `arms_differ_verified` (3 distinct mechanism output-hash aggregates across SHARDED points; META_RULE_AF).
4. `saturation_pc_pass` (SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine acc >= 0.95 → reproduces Probe 3 baseline).
5. `escapes_saturation_ceiling`: mean(acc across 6 SHARDED main-grid smoke pts) < 0.95 → confirms the smoke regime IS in the non-saturated regime we designed for. If mean-acc >= 0.95, the "non-saturated" design failed — REJECT SMOKE.
6. **Informational (NOT gating):** report `max_per_F_mech_variance` at the smoke slice (mid-corr=0.60, M=3200, N=2048). Report the value regardless of magnitude — H1 (variance appears) and H2 (variance ~0) are both hypothesis-supportive outcomes.

## FULL HARD_PASS_CG_TIER criteria

1. `cardinality_ok` per seed (217 pts each).
2. `arms_differ_verified` across seeds.
3. `saturation_pc_pass` per seed (SATURATION_PC arm reproduces acc >= 0.95).
4. 3-seed CV `< 0.10` per phase point (accuracy stability).
5. **`escapes_saturation_ceiling_full`: >= 30% of main-grid phase points have mean-acc in the `[0.30, 0.95]` non-saturated band.** If not, the FULL grid itself failed to escape saturation → cannot claim H1 or H2 with confidence → verdict = MIDDLE_BAND_ESCAPES_SATURATION_FAIL.
6. **Primary discriminator: F x CLEANUP_MECHANISM cross-term, restricted to slices with grand-mean(acc) in [0.30, 0.95].**
   - Within-band: `F_x_cleanup_max_abs_deviation_in_band < 0.05` AND `max_per_F_mech_variance_in_band < 0.05` → **HARD_PASS_H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED**: Probe 3's null result reproduces at NON-SATURATED regime; validates Probe 1's "STORAGE UNIQUELY moderates" thesis. Files as CG_META revival of Probe 3.
   - Within-band: `F_x_cleanup_max_abs_deviation_in_band >= 0.15` OR `max_per_F_mech_variance_in_band >= 0.10` → **HARD_PASS_H1_TOPOLOGY_MODERATES_WHEN_NON_SATURATED**: Probe 3's null was saturation artifact; TOPOLOGY IS a moderator. Updates REGIME MAP with new boundary point.
   - `H3 crossover`: if mech ranking changes across F within non-saturated slices, log `mech_ranking_crossover: True` and file as MM_TENTATIVE crossover exponent.
7. 3-seed replication + Skunkworks landed-VET before CG atom filing.

## HARD_FAIL

- `cardinality breach` (any seed missing pts).
- `saturation_pc_fail` (SATURATION_PC arm below 0.95 → primitive-invocation broken).
- `selftest fails`.

## MIDDLE_BAND

- `escapes_saturation_ceiling_full` fails (< 30% of pts in [0.30, 0.95]) → `MIDDLE_BAND_ESCAPES_SATURATION_FAIL`; grid needs further re-spec.
- `0.05 <= F_x_cleanup_max_abs_deviation_in_band < 0.15` → weak F-moderation regime; file as MM_TENTATIVE.

## SCHEMA-VET checklist (all True/present)

- `cardinality_ok`: True (217 FULL / 7 SMOKE)
- `arms_differ_verified`: True (3 distinct cleanup mechanisms; run-time hash check in selftest at F=2 multi-slot path + aggregate hash check in run_one_seed)
- `final_metrics_atomicity`: `tmp_replace` (atomic tmp + os.replace at end)
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException)
- `crlb_n/a`: "categorical accuracy on FHRR chain composition; discriminator is cross-term interaction deviation restricted to non-saturated band. Positive-control reproduces the same primitives at the test regime (Gate D compliance). The `escapes_saturation_ceiling` gate is the explicit reachability check."
- `discriminator_reachability`: True. If H1 correct, F_x_cleanup deviation >= 0.15 measured, gate fires. If H2 correct, deviation < 0.05 measured, gate fires. Non-saturated band is empirically enforced by grid design (M=6400 N=8192 corr=0.70 -> mean-acc predicted <0.50 given Plate bound).
- `baseline_in_band`: main-grid designed for non-saturated band. SATURATION_PC deliberately at ceiling as reference. `escapes_saturation_ceiling` gate is the enforcement mechanism.
- `HP_SCOPE`: {`SHARDED_main`: [`arms_differ`, `cardinality_ok`, `escapes_saturation_ceiling`, `F_x_cleanup_deviation_in_band`, `max_per_F_mech_variance_in_band`], `SATURATION_PC_arm`: [`saturation_pc_pass acc>=0.95`]}
- `cell_chunked`: True (3 seed wrappers)
- `start_marker_written`: True
- `crash_diagnostic_present`: True
- `heartbeat_present`: per-phase-point print with flush=True
- `defensive_error_checking`: `passed_all_4_patterns`
- `sweep_alignment_verdict`: `ALIGNED` — F, CLEANUP_MECHANISM, M, N, corr are the actual primitives that experience each swept value; no partition-routing intermediation.
- `discriminating_fraction`: SHARDED at cliff corr=0.70 across (M=800, 3200, 6400) x (N=2048, 8192) is expected to span [0.10, 0.95] band. Predicted per-point mean-acc from Plate bound + phase corruption physics: at M/N > 1.5 corr=0.70, mean-acc ~0.15-0.35; at M/N < 0.4 corr=0.45, mean-acc ~0.80-1.0. Predicted >= 50% pts in discriminating [0.30, 0.95] band.
- `composition_edges`: [`build_rules -> run_chain: SHAPE_MATCH`, `run_chain -> cleanup_argmax_idx: SHAPE_MATCH`, all inherited from Option Y core].
- `positive_control_arms`: [{arm: `saturation_pc_sharded_iterative_cosine_at_probe3_regime`, primitive: `run_chain(storage=SHARDED, mechanism=iterative_cosine)`, cited_prior_atom: `regime_probe_3_topology_x_cleanup_v1_MM_BOUNDED_NULL`, cited_prior_metric: 1.0 (all 72 SHARDED pts at acc=1.0), test_regime: {M: 800, N: 2048, F: 1, L: 2, corr: 0.20}, tolerance: 0.05, if_outside_tolerance: `HARD_FAIL_SATURATION_PC_MISMATCH`, regime_extension_audit: `SHAPE_MATCH`: same primitives at N=2048 (Probe 3 used N=4096, but N-sweep is intentional design here; saturation regime should reproduce across N)}]
- `functional_requirements`:
  - FR-1: chain-composition with varying F/mech/M/N/corr → `run_chain` primitive (imported)
  - FR-2: F-varying sharded codebook → `build_rules(F=F)` primitive (imported)
  - FR-3: 3-mechanism cleanup families → `CLEANUP_REGISTRY` (imported)
  - FR-4: F x CLEANUP interaction ANOVA deviation restricted to non-saturated band → new logic
  - FR-5: `escapes_saturation_ceiling` non-saturated fraction calculation → new logic
- `progress_logging`: `print_flush_true`
- `calibration_check`: `default_ok_for_this_regime` — BETA=8.0 ALPHA=0.5 inherited from Option Y core where they passed selftest at F=1 and F=2. F=16 is new; selftest hash-check verifies F-axis fires distinct outputs so calibration is not breaking F=16 invocation.
- `progress_cadence_expected_s`: 30 (per-phase-point flush; longest single point <30s expected on GPU).
- `saturation_gate_present`: True (escapes_saturation_ceiling both SMOKE gate and FULL gate).
- `null_hypothesis_smoke_discipline`: TRUE — per `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`, SMOKE gates on infrastructure + saturation_pc + escapes_saturation only, NOT on H1 discriminator firing.

## Reachability of criteria

- SMOKE wall: ~30-60s on local CPU (7 pts at N=2048 M=3200, ~5-10s/pt).
- FULL wall estimate: 217 pts/seed on remote GPU ~= 5-15 min/seed (majority N=8192 M=6400 batched matmul on GPU). Timeout 3600s per seed comfortable.
- CRLB-adjacent physics: at M/N=0.78 (Plate bound violated 5x), sharded_pc drops meaningfully below 1.0. At corr=0.70, 70% of phasor dimensions randomized → cleanup mechanism differences become measurable if they exist.

## Dispatch plan

- Local SMOKE: `local_cpu_queue` (SMOKE ONLY per USER-LOCKED 2026-07-01).
- Remote FULL: `overnight_queue` (GPU) — batching mandatory at N=8192 M=6400 grid. Requires push to origin/main by Orchestrator (harness-denied to exp_dev).

## USER authorization

Full-auto authorized per USER 2026-07-03 evening. Explicit self-reference (USER-locked): "I" (exp_dev agent) authored + smoked + prepared FULL dispatch. Orchestrator will dispatch FULL to GPU if SMOKE HP.
