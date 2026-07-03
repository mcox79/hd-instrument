# Pre-registration: Stage 1 Regime Probe 2 - N x CLEANUP_MECHANISM cross-term

**Anchor**: `stage1_regime_probe_2_N_x_cleanup_mechanism_v1`
**Cell files**: `experiments/exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_s{11,17,23}.py`
**Core module**: `experiments/_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_core.py`
**Author**: exp_dev (Opus 4.7, agent-spawn 2026-07-03)
**Arc**: Stage 1 Regime Map arc (USER-directed 2026-07-03; memory: `project_stage1_regime_map_of_CG_META_axes_USER_2026-07-03`)

## Purpose

Second cell in the Stage 1 Regime Map arc. Measures whether the
CLEANUP_MECHANISM axis (found to be regime-narrow to bipolar-codebook cleanup
per today's physics-law composition Option Y finding
`PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` v2 M-sweep 2026-07-03)
has a meaningful cross-term with the SCALE_FREE_in_N axis when both are
simultaneously varied.

Question: does N moderate the mechanism-degeneracy at FHRR SHARDED chain
composition? If yes, boundary is N-dependent (crossover exponent). If no,
Option Y finding extends without N-dependence.

## Cited source atoms (exact names, no abstraction)

- `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` (SHARDED default)
- `T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1` (N axis prior)
- `T4/META_SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1_2026-07-02` (chain regime)
- `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` (Option Y M-sweep 2026-07-03)

## Reuse (Principle 11)

Primitives imported from `_stage1_physics_law_joint_composition_factorial_v1_core`:
- `cphasor_torch`, `cnorm_torch`, `phase_corrupt`
- `build_rules` (SHARDED codebook)
- `cleanup_iterative_cosine`, `cleanup_modern_hopfield`, `cleanup_soft_energy_attractor`
- `cleanup_argmax_idx`, `run_chain`, `CLEANUP_REGISTRY`, `CLEANUP_MECHANISMS`

Cell-specific: sweep grid + verdict logic + hypothesis assessment.

## Design

### Sweep axes

- **N** in {2048, 4096, 8192, 16384} - 4 levels (larger than usual to probe scale-crossover)
- **CLEANUP_MECHANISM** in {`modern_hopfield`, `iterative_cosine`, `soft_energy_attractor`} - 3 non-Hebbian
- **Storage** FIXED = SHARDED (canonical FHRR chain composition regime)
- **M** in {200, 800, 3200} - 3 M-scaling levels
- **Corruption** in {0.20, 0.45} - 2 cleanup regimes
- **F** = 1 fixed
- **L** = 2 fixed

### Cardinality

- **FULL**: 4 x 3 x 3 x 2 = **72 phase points per seed** x 3 seeds = 216 pts total
- **SMOKE**: 2 (N in {2048, 8192}) x 3 x 1 (M=800) x 1 (corr=0.45) = **6 phase points per seed**

`cardinality_ok = True` iff observed == expected; `HARD_FAIL_CARDINALITY_BREACH` else.

## Compute architecture

**Class**: (a) batched-GPU (USER-LOCKED 2026-07-02). Auto-CUDA when available;
falls back to CPU on laptop. Substrate primitives (bind = elementwise complex64
mul; bundle = complex64 sum; cleanup = complex64 matmul + argmax) are matmul-
heavy and eligible for GPU batching. Per-phase-point matmul dominates.

**Storage strategy** (per META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW):
SHARDED (each rule stored as its own complex64 vector; L=2 chain composition).
Compositional cell, chain retrieval at L=2 -> SHARDED mandated by physics law.

**Wall-time estimate**:
- Smoke on CPU: ~6 pts x ~2s/pt (N up to 8192, M=800, TR=40) ~ 15s per seed
- FULL on GPU: ~72 pts x ~5s/pt (N up to 16384, M=3200, TR=100) ~ 6 minutes per seed
- 3 seeds sequential on GPU ~ 18 min; parallelizable via 3 sibling wrappers

**Timeout**: FULL 1800s per sibling (30 min); SMOKE 300s.

## Hypotheses (falsifiable, mutually exclusive)

- **H1** (Option Y extends, regime-narrow universally): at all N in FHRR SHARDED
  regime, per-N mechanism-axis variance stays < 0.05 (mean across M/corr cells).
  -> CLEANUP_MECHANISM axis universally regime-narrow to bipolar-codebook cleanup.
  Preferred sub-form: `H1_REGIME_NARROW_UNIVERSAL` requires additionally
  `N-range(mech_var) < 0.02` (uniform across N).

- **H2** (crossover exists): at some N, per-N mechanism-axis variance becomes
  > 0.10.
  -> boundary is N-dependent; regime map has a crossover exponent.
  This is **HP_CG_META**.

- **H3** (scale-invariant, non-zero degeneracy): mechanism variance uniform
  across N (range < 0.02) but at nonzero level (0.05 <= max <= 0.10).
  -> Option Y finding extends without N-dependence at a moderate degeneracy.

- **HF**: cardinality breach, arms-must-differ violation (mechanism outputs
  bit-identical), NaN in phase map, or unrecognized hypothesis condition.

## Envelope-fail-bands

Metric = `max_N_mean_spread` (= max over N in N_GRID of the mean over
{M, corr} cells of (max_acc across mech - min_acc across mech)).

Auxiliary metric = `range_N_mean_spread` (= max_N mech_var - min_N mech_var).

| Band | max_N_mean_spread | range_N_mean_spread | Verdict |
|------|-------------------|---------------------|---------|
| CG_META | > 0.10 | any | HARD_PASS_H2_CROSSOVER_N_MODERATES_MECHANISM |
| Narrow-universal | < 0.05 | < 0.02 | HARD_PASS_H1_OPTION_Y_EXTENDS_UNIVERSAL |
| Narrow-moderate-N-trend | < 0.05 | >= 0.02 | MIDDLE_BAND_H1_WITH_MODERATE_N_TREND |
| Scale-invariant-nonzero | [0.05, 0.10] | < 0.02 | MIDDLE_BAND_H3_SCALE_INVARIANT_NONZERO |
| Nascent crossover | [0.05, 0.10] | >= 0.02 | MIDDLE_BAND_NASCENT_CROSSOVER |

Gate ordering (early exits):
1. `cardinality_ok` -> else `HARD_FAIL_CARDINALITY_BREACH`
2. `arms_differ_verified` (3 distinct mechanism-output-hash aggregates)
   -> else `HARD_FAIL_ARMS_MUST_DIFFER` (META_RULE_AF)
3. `pc_reproduce_iterative_cosine_regime.pass` (iterative_cosine at min-N,
   min-M, min-corr >= 0.75 FULL / 0.60 SMOKE) -> else `HARD_FAIL_PC_REPRODUCE`
4. Then band-based verdict per table above

## SCHEMA-VET pre-dispatch checklist

- `cardinality_ok: True` (72 FULL / 6 SMOKE)
- `arms_differ_verified` at smoke gate (META_RULE_AF; 3 mechanism-output-hash
  aggregates must differ)
- `final_metrics_atomicity: "tmp_replace"` (write metrics.json.tmp then
  os.replace; per META_RULE_AH)
- `except SystemExit: raise` BEFORE `except Exception`; no bare `except:` or
  `except BaseException:`
- `crlb_n/a: "chain-composition per-N regime; no closed-form CRLB for
  mechanism-variance; H1/H2/H3 discriminator is threshold-based over
  measured spreads not against an information-theoretic floor"`
- `discriminator_reachability: True` (mechanisms produce distinct outputs
  at N_test=512 in selftest; SHARDED PC reproduces at easy regime)
- `baseline_in_band`: baseline concept N/A here (mechanism axis IS the
  discriminator; PC-reproduce arm at easy regime serves as positive control)
- `HP_SCOPE`: HARD_PASS_H1/H2/H3 gates apply to the full factorial;
  PC-reproduce gate applies only to iterative_cosine at
  (min-N, min-M, min-corr) SHARDED
- `cell_chunked: True` (3 sibling files for seeds 11, 17, 23)
- `start_marker_written: True` (STARTED metrics.json at main entry)
- `crash_diagnostic_present: True` (`_write_import_crash_sentinel`)
- `heartbeat_present: True` (per-phase-point flush print in `run_one_seed`)
- `defensive_error_checking: "passed_all_4_patterns"`
- `progress_logging: "print_flush_true"` (per-phase-point print + line-buffered
  stdout reconfigure)
- `calibration_check: "default_ok_for_this_regime"` (mechanism BETA=8.0,
  ALPHA_SOFT=0.5 inherited from sibling physics-law core which established
  discriminator-fires at these values)

## §15 Test-design failure prevention

### A) effective_vs_nominal_parameter_audit
- `swept_params`: {N, cleanup_mechanism, M, corruption}
- `effective_params_per_primitive`:
  - `build_rules`: effective_M = M, effective_N = N, effective_F = 1
  - `run_chain`: effective_L = 2, effective_corruption = corruption
  - `cleanup_fn`: effective_codebook_size = M (props), effective_dim = N
- `sweep_alignment_verdict`: **ALIGNED** (each primitive sees the swept
  parameter directly; no partition-routing or effective-vs-nominal mismatch)

### B) bracket_includes_discriminating_band
- Predicted per-point acc range: at N=2048/M=200/corr=0.20/iter_cos ~0.85;
  at N=16384/M=3200/corr=0.45/hopfield ~0.20-0.60 (unknown - THIS IS THE
  MEASUREMENT). Cited-prior: sibling Option Y cell established these
  mechanisms saturate to identical acc at SHARDED regime; H1 predicts full
  sweep collapses to same finding.
- Discriminating band [0.30, 0.70]: for H2 to fire, at least one (N, mech, M,
  corr) cell must sit in [0.30, 0.70] AND mechanisms must differ by > 0.10 at
  that cell.
- Predicted `discriminating_fraction >= 0.30` under H2 (crossover realized);
  under H1 predicted fraction may be 0 (all cells saturate together).
- Discipline: because H1 is a null-result outcome, the "band-in-fraction"
  gate is asymmetric here - we accept H1 as HARD_PASS regardless of band
  fraction because the null is the finding. Bands are only used for H2
  discrimination.

### C) signal_shape_compatibility_audit
No composition edges between novel primitives; single-primitive chain
retrieval. Existing `run_chain` established shape-compatible in sibling.
`composition_edges`: reuse of existing chain-composition primitive at L=2;
SHAPE_MATCH (identical to sibling physics-law core's use).

### D) reproduce_prior_chain_grade_result_as_positive_control
- Arm: `PC_iterative_cosine_at_min_regime`
- Primitive: iterative_cosine cleanup + SHARDED FHRR chain L=2
- Cited prior atom: Option Y v1 core's selftest (iterative_cosine SHARDED at
  easy regime acc_easy >= 0.80 at M=50/N=512/L=2/F=1/corr=0.05); adapted
  threshold at our regime (M=200/N=2048/L=2/F=1/corr=0.20 or 0.45):
  - FULL threshold: 0.75 (corr=0.20 easy)
  - SMOKE threshold: 0.60 (corr=0.45 only in smoke)
- Cited prior regime: `{N: 512, M: 50, L: 2, F: 1, corr: 0.05}` (selftest)
- Test regime: `{N: 2048, M: 200, L: 2, F: 1, corr: 0.20 or 0.45}`
- Tolerance: threshold-based (not delta-based) because regimes differ
- If outside tolerance: `HARD_FAIL_PC_REPRODUCE` -> mechanism-variance
  claims not trustworthy
- Regime extension audit: SHAPE_MATCH (identical primitives; larger M/N/corr
  in test regime is expected to reduce acc; threshold set below sibling's
  easy-regime value to accommodate)

### E) functional_requirement_decomposition_present
Functional Requirements:
- FR1: measure mechanism-variance at multiple N -> `per_N_mech_variance`
- FR2: detect crossover in mechanism-variance vs N ->
  `range_N_mean_spread` + hypothesis assessment
- FR3: verify mechanism-outputs differ (not bit-identical) -> META_RULE_AF
  arms-must-differ (`mech_output_hash_agg`)
- FR4: positive-control that primitive works at expected level ->
  PC-reproduce arm at min-regime

## Compute cost estimate

- SMOKE (local CPU laptop): 6 pts x ~2s/pt at max N=8192, M=800, TR=40 ~ 15s
- FULL (target = overnight_queue GPU): 72 pts x ~4s/pt at max N=16384, M=3200,
  TR=100 (GPU batched matmul dominates) ~ 5 minutes per seed
- 3 seeds x 5 min = ~15 GPU-min (upper-bound; likely faster with GPU)
- USER estimate: ~7.5 GPU-min matching M-sweep timing

## Post-SMOKE routing

If SMOKE HARD_PASS with informative variance:
- Route to hdi_orchestrator for FULL dispatch to `overnight_queue` (GPU)
- 3 sibling wrappers dispatched separately (chunked per-seed)
- Timeout 1800s per sibling

If SMOKE HARD_FAIL:
- Return smoke verdict with reason; do NOT dispatch FULL
- Bounce to Director for regime re-spec or hypothesis refinement

## Explicit self-reference (USER-locked)

I (exp_dev, Opus 4.7 agent-spawn) authored + smoke-vetted + prepped this cell
for remote-FULL dispatch on 2026-07-03. Not "Director dispatched"; not
"the cell was created" - I did this.
