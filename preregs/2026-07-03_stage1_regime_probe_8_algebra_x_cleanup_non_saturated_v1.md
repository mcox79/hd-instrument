# Pre-registration: Regime Probe 8 -- ALGEBRA (F fan-out) x CLEANUP_MECHANISM at cliff-adjacent regime

Date: 2026-07-03
Author: exp_dev (agent-spawn, Opus 4.7)
Anchor: `stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1`
Sibling seed wrapper (this filing): `_s7`. Additional seeds `_s13`, `_s19` to be authored by
Orchestrator/exp_dev after Tailscale restore for 3-seed FULL replication.
Arc: Stage 1 REGIME MAP of CG_META axes (USER strategic direction 2026-07-03).

## Purpose (intuitive)

Fills the 4th missing data point on the revised regime hypothesis:

> "ALL Stage 1 axes moderate CLEANUP_MECHANISM at cliff-adjacent regime; NONE at deep-saturation."

Probes 1 (STORAGE), 6 v2 (TOPOLOGY = F in {1,4,8,16}), and 7 v2 (N = SCALE_FREE) have covered
STORAGE, TOPOLOGY, and N crosses with MECHANISM at (or approaching) cliff. ALGEBRA (fan-out F at
finer resolution + at the specific cliff-adjacent operating point) is the 4th non-mechanism axis
and has not been probed as a dedicated cell with:
  (a) F=2 as an interstitial resolution point (Probe 6 v2 sampled F in {1,4,8,16}); and
  (b) a fixed, empirically-verified cliff-adjacent operating point (N=512, M=6400, corr=0.85, L=2)
      that lands mid-band across the entire F sweep; and
  (c) an explicit H3-NULL DEEP_SATURATION control arm (N=8192, M=800, corr=0.60) where mech_var
      is expected to vanish by mechanism DEGENERACY.

A dedicated cell isolates the ALGEBRA x MECHANISM interaction cleanly and provides the paired
DEEP_SAT null control that the revised regime hypothesis demands.

## Empirical pre-reg bracket (2026-07-03 exp_dev, PRE-DISPATCH design validation)

Per `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`, I
empirically bracketed the cliff BEFORE committing the pre-reg grid. Single-seed TR=40 bracket
at `scratchpad/probe8_cliff_bracket.py`:

**Bracket 1: cliff-adjacent operating point (N=512 M=6400 corr=0.85 L=2 F sweep):**
```
  F    mean  spread   modern_hopfield  iterative_cosine  soft_energy_attractor
  1  0.5917  0.100         0.550            0.575                0.650
  2  0.6833  0.025         0.675            0.700                0.675
  4  0.7667  0.075         0.800            0.775                0.725
  8  0.6583  0.100         0.700            0.600                0.675
 16  0.7333  0.075         0.775            0.725                0.700
```
All F land in [0.30, 0.95] non-saturated band. Grand mean 0.687; spread 0.025-0.100. Noise
floor at TR=40 ~ sqrt(0.5/40) ~ 0.079; TR=100 3-seed noise floor ~ 0.05. H1 threshold 0.10
is measurable given noise floor at FULL configuration.

**Bracket 2: F=1 cliff walk (N=512 M=6400 L=2 corr sweep):**
```
 corr    mean  spread   modern_hopfield  iterative_cosine  soft_energy_attractor
 0.85  0.5917  0.100         0.550            0.575                0.650  <-- LOCKED
 0.88  0.2667  0.050         0.250            0.300                0.250
 0.90  0.1167  0.100         0.100            0.075                0.175
 0.92  0.0333  0.025         0.025            0.050                0.025
```
F=1 cliff sits between 0.85 and 0.88. Task's suggested fallback corr in {0.88, 0.90, 0.92}
puts F=1 BELOW-floor. corr=0.85 is the correct cliff-adjacent operating point for F=1;
locked as the CLIFF regime for all F.

**Bracket 3: DEEP_SAT null control (N=8192 M=800 corr=0.60 L=2 F sweep):**
```
  F    mean  spread   modern_hopfield  iterative_cosine  soft_energy_attractor
  1  1.0000  0.000         1.000            1.000                1.000
  4  1.0000  0.000         1.000            1.000                1.000
 16  1.0000  0.000         1.000            1.000                1.000
```
All F, all mechanisms saturate at 1.0 with spread=0. Perfect null control (mechanism
DEGENERACY at deep-saturation).

All bracket numbers MEASURED@`scratchpad/probe8_cliff_bracket.py` (TR=40 single seed=7,
2026-07-03; pre-authoring bracket run before writing this pre-reg).

## Hypotheses (falsifiable)

- **H1 (F ALGEBRA moderates at cliff-adjacent):** `cliff_max_per_F_mech_variance_in_band >= 0.10`.
  F IS a moderator of CLEANUP_MECHANISM at cliff-adjacent regime; completes the revised
  regime hypothesis "ALL Stage 1 axes moderate at cliff-adjacent" alongside Probes 1/6v2/7v2.
- **H2 (F ALGEBRA does NOT moderate at cliff-adjacent):** `cliff_max_per_F_mech_variance_in_band < 0.05`.
  F is degenerate at cliff-adjacent regime; contradicts revised "ALL axes moderate"
  hypothesis; supports Probe 1 STORAGE_UNIQUELY_moderates thesis.
- **H3 (mechanism ranking crossover):** mech ranking changes across F within CLIFF band
  (MM_TENTATIVE crossover exponent).
- **H3-NULL (DEEP_SAT null fires):** `deep_sat_max_mech_variance < 0.05`. Confirms
  mechanism DEGENERACY at deep-saturation; strengthens revised regime hypothesis (variance
  vanishes when substrate saturates). If H3-NULL FAILS to fire (deep max_var >= 0.05),
  surprising positive result challenges the regime hypothesis and is flagged in verdict.

## Cited source atoms (exact names per META_RULE_AC + MM_STANDARD)

- `META_saturation_floor_masks_null_variance_probe3_lesson` (T4 MM_STANDARD METHODOLOGY_RULE, 2026-07-03)
- `T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_3seed_FULL_MM_STANDARD_cleanup_axis_regime_narrow_extended_to_N_axis`
   -- Probe 2 baseline for SATURATION_PC arm reproducer
- `MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1` -- Probe 1 CG_META (STORAGE axis)
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` -- F axis physics
- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` -- SHARDED FHRR chain composition
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` -- 3 non-Hebbian mechanisms
- `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`
   -- empirical cliff-bracketing discipline (why I did Bracket 1/2/3 before pre-reg)
- `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`
   -- SMOKE gate on infra + PC + escapes only, NOT on discriminator firing
- Probe 6 v2 landing (companion, TOPOLOGY F in {1,4,8,16} revival, same-day)
- Probe 7 v2 landing (companion, SCALE_FREE N in {2048..16384} revival, same-day)

## Prior-work check (substrate-KB query)

Query keywords: `"chain composition depth F ALGEBRA cleanup mechanism sharded FHRR interaction"`
Top-5 hits at cosine <=0.41 (all cortex Composition Mechanisms / mechanism_composition_v1 /
generic 'action_mechanism' / 'interaction' -- NONE match the ALGEBRA x CLEANUP cross-term
at cliff-adjacent regime). The direct sibling cells (Probe 6 v2 TOPOLOGY, Probe 7 v2 N)
were authored same-day; this Probe 8 is genuinely NOVEL as the F=2 interstitial + fixed-cliff-point
+ paired DEEP_SAT null design.

## Compute architecture

- Class: `(a) batched-GPU` -- reuses batched-GPU primitives from
  `experiments/_stage1_physics_law_joint_composition_factorial_v1_core` (torch.cuda when available;
  CPU fallback for local smoke). N=512 M=6400 is matmul-dominated; batched-GPU on remote.
- Storage strategy: `sharded` for the entire main factorial (Probe 8 is F x CLEANUP; STORAGE not swept).
  One SATURATION positive-control point reproduces Probe 2/3/6/7 baseline.
- Progress logging: `print_flush_true` (per-phase-point + per-seed prints all use `flush=True`).
- Timeout budget: SMOKE ~20-60s local CPU (10 pts; F=1..16 at N=512 fast, deep-sat spot-check).
  FULL ~2-6 min per seed on remote GPU (25 pts; N=512 cliff pts fast, deep-sat N=8192 pts heavier).

## Design

### Sweep axes (FULL)

CLIFF arm (primary discriminator):
- CLEANUP_MECHANISM in {modern_hopfield, iterative_cosine, soft_energy_attractor}
- F in {1, 2, 4, 8, 16}  (5 levels; F=2 interstitial vs Probe 6 v2)
- Fixed: N=512, M=6400, corruption=0.85, L=2, STORAGE=SHARDED  (cliff-adjacent, empirically LOCKED)

DEEP_SAT arm (H3-NULL control):
- CLEANUP_MECHANISM in {modern_hopfield, iterative_cosine, soft_energy_attractor}
- F in {1, 4, 16}  (3 levels; H3-NULL null-control sufficient)
- Fixed: N=8192, M=800, corruption=0.60, L=2, STORAGE=SHARDED  (deep saturation; empirically 1.0)

SATURATION_PC arm (Gate D reproducer):
- SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine (Probe 2/3/6/7 baseline reproducer)

### Sweep axes (SMOKE)

- CLIFF arm: F in {1, 16} (endpoints) x 3 mech = 6 pts
- DEEP_SAT arm: F in {1} x 3 mech = 3 pts (spot-check H3-NULL null control fires)
- SATURATION_PC arm: 1 pt
- Total: 10 pts (local CPU ~20-60s at TR=40).

### Cardinality (CARDINALITY_OK gate MANDATORY per META_RULE_H)

- `EXPECTED_N_UNITS_FULL = 5*3 + 3*3 + 1 = 25 pts / seed`
- `EXPECTED_N_UNITS_SMOKE = 2*3 + 1*3 + 1 = 10 pts`
- Verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if `observed != expected`.

### Positive control (Gate D reproducer)

At `SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine`, cell must reproduce acc >= 0.95.
Same regime as Probes 2/3/6/7 baseline. HARD_FAIL if below 0.95 -- primitive-invocation broken.
- Cited prior atom: `T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_...`
- Cited prior metric: 1.0
- Tolerance: 0.05 (acc >= 0.95)
- `regime_extension_audit: SHAPE_MATCH` -- identical (M, N, F, L, corr) subset of Probes 2/3/6/7.

### Reuse (Principle 11)

- Primitives (`cphasor_torch`, `cnorm_torch`, `phase_corrupt`, `build_rules`, `run_chain`,
  `CLEANUP_REGISTRY`, `CLEANUP_MECHANISMS`, `BETA`, `ALPHA_SOFT`) imported from
  `experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py`.
- Verdict + arm_tag routing modeled on `experiments/_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1_core.py`
  (band-restricted discriminator + arm-partition pattern).
- New file: `experiments/_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_core.py`.
- Seed wrapper (this filing): `experiments/exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s7.py`.

## SMOKE HP criteria (SHIP FULL if all met)

Per `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`:
SMOKE gate is on INFRASTRUCTURE + POSITIVE CONTROL + REGIME CONFIRMATION only.
DO NOT gate on discriminator variance firing -- H1 AND H2 are both hypothesis-supportive.

1. `selftest_ok` (cardinality math + 3-mech-distinct at F=2 + F-axis fires + SATURATION_PC easy + CLIFF regime sanity + DEEP_SAT regime sanity).
2. `cardinality_ok` (observed 10 = expected 10).
3. `arms_differ_verified` (3 distinct mech output-hash aggregates across CLIFF pts; META_RULE_AF).
4. `saturation_pc_pass` (SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine acc >= 0.95).
5. `escapes_saturation_ceiling_cliff` (per-F semantics): at least one CLIFF F-slice has mean-acc < 0.95.
6. `deep_sat_saturated` (DEEP_SAT arm mean_acc >= 0.95); H3-NULL null-control regime not drifted.
7. **Informational (NOT gating):** report `cliff_max_per_F_mech_variance_in_band` +
   `deep_sat_max_mech_variance` + `h3_null_fires` regardless of magnitude. H1 (cliff variance
   fires) and H2 (cliff variance does not fire) are both legitimate hypothesis outcomes.

## FULL HARD_PASS_CG_TIER criteria

1. `cardinality_ok` per seed (25 pts each).
2. `arms_differ_verified`.
3. `saturation_pc_pass` per seed (SATURATION_PC acc >= 0.95).
4. 3-seed CV < 0.10 per phase point (accuracy stability; validated across sibling seeds by verdict_handler).
5. `deep_sat_saturated` per seed (DEEP_SAT mean_acc >= 0.95; H3-NULL regime not drifted).
6. `cliff_fraction_in_band >= 0.30` (CLIFF arm lands mostly in [0.30, 0.95] non-saturated band).
7. **Primary discriminator:** `cliff_max_per_F_mech_variance_in_band`:
   - `>= 0.10` -> **HARD_PASS_H1_F_ALGEBRA_MODERATES_AT_CLIFF_ADJACENT**: F IS a moderator;
     completes "ALL Stage 1 axes moderate at cliff-adjacent" regime hypothesis.
   - `< 0.05` -> **HARD_PASS_H2_F_ALGEBRA_DEGENERACY_AT_CLIFF_ADJACENT**: F does NOT moderate;
     contradicts revised hypothesis; supports STORAGE_UNIQUELY_moderates thesis.
   - `[0.05, 0.10)` -> **MIDDLE_BAND_WEAK_F_MODERATION** (MM_TENTATIVE).
8. **H3-NULL secondary:** `deep_max_var < 0.05` reported as `h3_null_fires`. When firing:
   strengthens revised regime hypothesis. When failing: flagged as surprising positive result.
9. **H3 crossover:** `mech_ranking_crossover` (bool) reported; if True, log as MM_TENTATIVE crossover.
10. 3-seed replication + Skunkworks landed-VET before CG atom filing.

## HARD_FAIL

- `cardinality_breach` (any seed missing pts).
- `arms_differ_fail` (mechanisms produce identical outputs; META_RULE_AF).
- `saturation_pc_fail` (< 0.95 -> primitive-invocation broken; Gate D violation).
- `deep_sat_arm_drift` (DEEP_SAT mean_acc < 0.95; null control regime failed to saturate).
- `selftest_fail`.

## MIDDLE_BAND

- `cliff_fraction_in_band < 0.30` -> `MIDDLE_BAND_CLIFF_ARM_ESCAPES_SATURATION_FAIL`; grid re-spec.
- `cliff_max_per_F_mech_variance_in_band` in `[0.05, 0.10)` -> `MIDDLE_BAND_WEAK_F_MODERATION`.

## SCHEMA-VET checklist (all True/present)

- `cardinality_ok`: True (25 FULL / 10 SMOKE)
- `arms_differ_verified`: True (3 distinct cleanup mechanisms; selftest hash-check + aggregate hash check)
- `final_metrics_atomicity`: `tmp_replace` (atomic tmp + os.replace at end)
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException)
- `crlb_n/a`: "categorical accuracy on FHRR chain composition; discriminator is F x MECH cross-term
   spread restricted to non-saturated band on CLIFF arm. Positive-control reproduces primitives at
   test regime (Gate D). `escapes_saturation_ceiling_cliff` gate is the reachability check for CLIFF;
   `deep_sat_saturated` gate is the sanity check for DEEP_SAT null control."
- `discriminator_reachability`: True. Empirical bracket confirms CLIFF F=2 spread=0.025 (near-noise),
   F=1/8 spread=0.100 (at H1 threshold at TR=40; noise-floor-shrinks at TR=100 3-seed). H2 threshold
   (< 0.05) is measurable when TR=100 noise floor ~ 0.05. H1 threshold (>= 0.10) is measurable at 3-seed
   average when TRUE signal exists.
- `baseline_in_band`: CLIFF arm empirically 0.59-0.77 (mid-band). DEEP_SAT arm empirically 1.0
   (saturated, by design as null control). `escapes_saturation_ceiling_cliff` and `deep_sat_saturated`
   are enforcement gates.
- `HP_SCOPE`: {`CLIFF`: [`arms_differ`, `cardinality_ok`, `escapes_saturation_cliff`,
   `cliff_max_per_F_mech_variance_in_band`], `DEEP_SAT`: [`deep_sat_saturated`,
   `deep_sat_max_mech_variance < 0.05`], `SATURATION_PC`: [`sat_pc_acc >= 0.95`]}
- `cell_chunked`: True (single-seed sibling; s13/s19 to be authored by Orchestrator after Tailscale)
- `start_marker_written`: True (STARTED sentinel written at main() entry)
- `crash_diagnostic_present`: True (IMPORT_CRASH sentinel + outer try/except)
- `heartbeat_present`: per-phase-point print with flush=True
- `defensive_error_checking`: `passed_all_4_patterns`
- `sweep_alignment_verdict`: `ALIGNED` -- F is the actual axis experienced by each primitive
   (build_rules(F), run_chain(F)); no partition-routing intermediation.
- `discriminating_fraction`: 100% of CLIFF F sweep points empirically in [0.30, 0.95] band
   (Bracket 1 shows mean 0.59-0.77 all pts); enforced by `cliff_fraction_in_band >= 0.30` gate.
- `composition_edges`: [`build_rules -> run_chain: SHAPE_MATCH`,
   `run_chain -> cleanup_argmax_idx: SHAPE_MATCH`; all from Option Y core].
- `positive_control_arms`: [{arm: `saturation_pc_sharded_iterative_cosine_at_probe2_regime`,
   primitive: `run_chain(storage=SHARDED, mechanism=iterative_cosine)`,
   cited_prior_atom: `T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_...`,
   cited_prior_metric: 1.0, test_regime: {M: 800, N: 2048, F: 1, L: 2, corr: 0.20},
   tolerance: 0.05, if_outside_tolerance: `HARD_FAIL_SATURATION_PC_MISMATCH`,
   regime_extension_audit: `SHAPE_MATCH`}]
- `functional_requirements`:
  - FR-1: chain-composition with varying F/mech at fixed (N, M, corr) cliff point -> `run_chain` (imported)
  - FR-2: F-varying sharded codebook -> `build_rules(F=F)` (imported)
  - FR-3: 3-mechanism cleanup families -> `CLEANUP_REGISTRY` (imported)
  - FR-4: F x MECH variance restricted to non-saturated band on CLIFF arm -> new logic
  - FR-5: DEEP_SAT null-control arm variance check -> new logic
  - FR-6: SATURATION_PC Gate D reproducer -> new arm
- `progress_logging`: `print_flush_true`
- `calibration_check`: `default_ok_for_this_regime` -- BETA=8.0 ALPHA=0.5 inherited from Option Y core;
   F=2 selftest confirms 3 mechanisms distinct at reduced regime.
- `progress_cadence_expected_s`: 10 (per-phase-point flush; longest single point < 5s on CPU).
- `saturation_gate_present`: True (both `escapes_saturation_ceiling_cliff` and `deep_sat_saturated`).
- `null_hypothesis_smoke_discipline`: TRUE per
   `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`.

## Reachability of criteria

- SMOKE wall: ~20-60s local CPU (10 pts at TR=40; CPU bracket 40s TR=40 measured).
- FULL wall estimate: 25 pts/seed on remote GPU ~ 2-6 min/seed. Per-seed timeout budget: 1200s.
- Cliff physics: at N=512, corr=0.85, F=1: acc 0.59 (mid-band). Enough headroom for
   TR=100 3-seed mechanism differentiation if genuine signal exists.

## Dispatch plan

- Local SMOKE: local_cpu_queue (SMOKE ONLY per USER-LOCKED 2026-07-01; Tailscale down for remote).
- Remote FULL: `overnight_queue` (GPU) after Tailscale restore + Orchestrator push
   (harness-denied to exp_dev).
- Sibling seeds s13, s19: to be authored by Orchestrator/exp_dev post-Tailscale for FULL 3-seed
   replication (mirrors Probe 7 v2 CHUNKED pattern).

## USER authorization

Full-auto authorized per USER 2026-07-03. Explicit self-reference (USER-locked): "I" (exp_dev agent)
authored + smoked + prepared for FULL dispatch. NO FULL DISPATCH IN THIS CYCLE
(Tailscale down; USER-LOCKED SMOKE ONLY on local_cpu_queue).
