# Pre-reg: substrate_spoke3_hippocampal_encoder_lower_cluster_cos_boundary_probe_smoke (2026-07-03)

## Anchor name
`substrate_spoke3_hippocampal_encoder_lower_cluster_cos_boundary_probe_smoke_2026_07_03`

## Cell file
`experiments/exp_substrate_spoke3_hippocampal_encoder_lower_cluster_cos_boundary_probe_smoke_2026-07-03.py`

## Purpose (Skunkworks-approved scope-broadening (ii))
Characterizes the JL-vs-exact-carrier analytical-scope boundary of Skunkworks'
prior atom `MATH_COSINE_ARGMAX_ROBUST_AT_EXTREME_SPARSE_CUE_JL_ORTHOGONALITY_MM_STANDARD`
following the amendment atom
`META_GAUSSIAN_JL_ANALYTICAL_PREDICTION_FAILS_AT_CLUSTER_COS_HIGH_REGARDLESS_OF_FILLER_GEOMETRY`
(MM_STANDARD_2ND_WITNESS, 2026-07-03).

The two prior cells (Cell 4 + bipolar-vs-Gaussian) at cluster_cos~0.90 +
75% dim-zero cue showed baseline cosine SATURATES at r@1=1.000 regardless
of filler geometry (bipolar bit-identity determinism AND Gaussian both lead
to exact-carrier dominance). The OPEN question: at LOWER cluster_cos and/or
LOWER corruption, does the Gaussian-JL analytical prediction
(baseline degrades due to sib_std variance) ACTUALLY hold?

Answer determines the actual scope of the prior JL atom:
- If JL prediction VALIDATES at low cluster + moderate corruption: analytical
  model has a legitimate regime; MM_STANDARD atom promotes to
  CG_MEASURED_BOUND with clear regime characterization.
- If JL prediction ALSO fails at low cluster: deeper analytical model
  limitation; suggests bit/value exact-carrier dominates at ALL corruption
  > 50% regardless of cluster_cos.

## Framing discipline (LOAD-BEARING per USER 2026-07-02)
- SUBSTRATE KNOWS ALMOST NOTHING. This is a MECHANISM probe characterizing
  ANALYTICAL SCOPE of a prior atom. Not a general-knowledge or language claim.
- Anti-personification: substrate operates on integer indices + real-valued
  vectors.
- No sigma claims without formula verification AND filler-geometry AND
  cluster_cos annotation.
- Skunkworks-corrected T-F formula: `C_TF = dg_dim / (2 * ln(1/p))`.

## Task class
SAME as Cell 4 / bipolar-vs-Gaussian (episodic-binding + partial-cue retrieval;
N=500 pairs; adversarial cluster-shared codebook). ONLY cluster_cos and
corruption vary.

## Filler geometry
Gaussian ONLY. Bipolar bit-identity determinism already broken empirically
(Cell 4); Skunkworks predicted JL applies at Gaussian. This cell tests the
open question at Gaussian across the cluster_cos x corruption grid.

## Sweep design (2D characterization)

### cluster_cos in {0.30, 0.50, 0.70, 0.90}
- 0.30 = essentially random (no cluster structure); cosine-JL prediction
  should apply CLEANLY at Gaussian.
- 0.50 = mild cluster; intermediate regime.
- 0.70 = moderate cluster; should discriminate JL-vs-exact-carrier regimes.
- 0.90 = high cluster (Cell 4 regime; REGRESSION).

### corruption in {0.50, 0.75}
- 0.50 = moderate corruption; theoretically JL region if cluster_cos low.
- 0.75 = Cell 4 regime; REGRESSION.

## Arms (3 arms x 4 cluster_cos x 2 corruption = 24 arm-instances x 3 seeds = 72 units)
- `ARM_HIPPO_C{cc}_R{corr}` - hippocampal mechanism (DG + CA3).
- `ARM_COSINE_C{cc}_R{corr}` - cosine baseline (Skunkworks JL prediction target).
- `ARM_RANDOM_C{cc}_R{corr}` - chance floor.

DG_ONLY arms skipped for streamlining (CA3 anti-signal already
CG_HN_ARCHITECTURAL cross-geometry; DG_ONLY reproduction not required
by this scope-boundary characterization).

## HP band

### HP1 (Skunkworks-JL PREDICTION TEST at low cluster + moderate corruption)
`ARM_COSINE_C0.30_R0.50` r@1 <= 0.90 (baseline degrades; JL prediction
VALIDATES at counterfactual regime).

- LOAD_BEARING for the "analytical model has legitimate regime" branch.

### HP2 (regime boundary characterization)
cluster_cos threshold above which COSINE saturates at r@1 >= 0.99 identifiable
as INTERIOR to sweep axis (i.e. not at 0.30 or 0.90 edges) for AT LEAST ONE of
the corruption values.

- If interior boundary observable: scope-refinement clean (JL degradation
  observed at cluster_cos <= threshold; exact-carrier saturation at
  cluster_cos >= threshold).

### HP3 (regression at cluster_cos=0.90 + 75% corruption)
`ARM_COSINE_C0.90_R0.75` r@1 >= 0.99 (matches Cell 4 +
bipolar-vs-Gaussian pattern MEASURED@ 1.000).

- Code-integrity gate. If HP3 fails, codebook change broke regression;
  downstream boundary verdict UNRELIABLE.

`HARD_PASS = HP1 AND HP2 AND HP3`

## Failure classes

### HF-jl-fails-even-at-low-cluster
HP1 fails at cluster_cos=0.30 + corrupt=0.50 (deeper analytical model
limitation than just cluster_cos-0.90). Suggests bit/value exact-carrier
dominates at ALL corruption > 50% regardless of cluster_cos. Routes to
research 2x-drill on exact-carrier-vs-JL mechanism at moderate corruption.

### HF-regression-broken
HP3 fails. Code drift; downstream verdict UNRELIABLE.

### HF-no-boundary-observable
HP2 fails structurally (boundary OUTSIDE the sweep axis or spans multiple
axes non-monotonically). Sweep axis needs re-scoping (finer resolution /
different range).

### HF-baseline-out-of-band-META_RULE_AG
RANDOM arms above `5 * chance` (0.010) at any cluster_cos x corruption cell.
Retrieval bug.

### HF-dg-sparse-rate-architectural
Hippocampal DG rate outside [0.008, 0.040] at any cluster_cos x corruption
cell.

### MIDDLE_BAND
Partial HP fires (JL fires at some but not all low-cluster regimes).

## Regime
- N_DIM = 2048
- DG_DIM = 8192
- DG_SPARSITY = 0.02 (T-F capacity ~1047 THEORETICAL@ C_TF = 8192/(2*ln(50)))
- N_PAIRS = 500 (load ~48% of C_TF)
- CLUSTER_SIZE = 5
- Filler geometry: Gaussian only, rho = cluster_cos target
- SEEDS = [11, 17, 23]
- CORRUPTION varies per arm (see sweep)

## Selftests (before smoke dispatch)
1. `arg_parse_default_is_smoke` - argparse default returns "smoke" mode.
2. `corrupt_cue_50pct_and_75pct` - both corruption values produce exact
   zero-count per row + non-zero dims preserve episode values.
3. `gaussian_within_cluster_cos_at_each_rho` - empirical filler-cos matches
   theoretical rho at each cluster_cos value in [0.30, 0.50, 0.70, 0.90]
   within +/- 0.06.
4. `gaussian_filler_is_real_valued` - Gaussian fillers NOT bipolar (>10
   unique values, variance in [0.7, 1.3]).
5. `arms_differ_hash_micro` - HIPPO and COSINE arms produce distinct queries
   on same episodes.
6. `determinism_gaussian` - same (seed, rho) -> bit-identical fillers and
   episodes.
7. `scale_sentinel_n_dim_8192` - codebook + corrupt-cue work at N_DIM=8192
   without crash; cluster_cos observation matches theoretical.
8. `regression_expected_hippo_and_cosine_at_regression_regime` -
   Regression at (cluster_cos=0.90, corrupt=0.75, N=100) reduced-scale
   probe: COSINE r@1 >= 0.95 (saturation reproduces) AND HIPPO r@1 >= 0.35
   (mechanism not broken).
9. `primitive_selftests_chain` - `hdlab.hippocampal_encoder --self-test`
   returns 13/13 passed.

## Pre-reg gates (SCHEMA-VET compliance)
```yaml
# META_RULE_H (cardinality_ok)
expected_n_units: 72  # 3 arms x 4 cluster_cos x 2 corruption x 3 seeds
cardinality_ok: mandatory  # verdict emits HARD_FAIL_CARDINALITY_BREACH if
                          # actual < expected

# META_RULE_J (per-unit failure-class instrumentation)
per_unit_failure_class: mandatory  # captures encoder crashes with named class

# META_RULE_K (discriminator-fires)
discriminator_fires: cosine_r1_transitions_from_below_0.90_to_above_0.99
                    across_cluster_cos_sweep

# META_RULE_L (strictly-above-floor)
hp1_threshold_strict: true  # <= 0.90 (not just "<")
hp3_threshold_strict: true  # >= 0.99

# META_RULE_M (calibration_check)
calibration_check: default_ok_for_this_regime
calibration_evidence: >
  Regime is direct extension of Cell 4 + bipolar-vs-Gaussian
  (N_DIM=2048, DG_DIM=8192, sparsity=0.02, N_PAIRS=500). Only cluster_cos
  and corruption vary. Prior cells confirmed baseline + mechanism arms
  differentiate at cluster_cos=0.90+corrupt=0.75. Bands transferred directly.

# META_RULE_AC (HYPOTHESIZED/MEASURED/THEORETICAL tagging)
# All numbers in cell + prereg tagged; see cell docstring and HP bands.

# META_RULE_AF (arms-differ-verified)
arms_differ_verified: true  # verdict enforces sha256 distinctness across
                            # arm queries

# META_RULE_AG (baseline_in_band)
baseline_in_band: true  # RANDOM arm r@1 <= 5*chance = 0.010 at each cell
                        # of the sweep

# META_RULE_AH (final_metrics_atomicity)
final_metrics_atomicity: tmp_replace  # write to .tmp then os.replace()

# Discriminator-must-survive-scale
discriminator_survives_scale: analytical_justification
# Rationale: same regime as Cell 4 + bipolar-vs-Gaussian which produced
# discriminative measurements; the discriminator we test here IS the axis
# transition (COSINE degrades at low cluster / saturates at high cluster).
# HP1 fires the low-cluster limb; HP3 fires the high-cluster limb;
# HP2 asserts the sweep axis actually observes a transition. Regime is not
# a "cell running" question; it is the specific axis of the analytical scope.

# Sweep-cell-specific gates (Section 15)
sweep_alignment_verdict: ALIGNED
# cluster_cos parameter IS what the cosine baseline directly experiences
# through the filler variance channel; no compositional dilution.

discriminating_fraction: 0.50  # at minimum
# 2 of 4 cluster_cos values expected to fall in [0.30, 0.70] discriminating
# band (0.30 predicted <0.90 = JL-degrade; 0.50-0.70 uncertain regime;
# 0.90 predicted =1.000 = exact-carrier). If ALL sweep points saturate or
# ALL degrade, HP2 hits HF-no-boundary-observable and we learn the axis
# needs re-scoping.

composition_edges: []  # no compositional edges (single-primitive per arm)

positive_control_arms:
  - arm: ARM_COSINE_C0.90_R0.75
    primitive: cosine_baseline
    cited_prior_atom: (MEASURED@ Cell 4 metrics.json + bipolar-vs-Gaussian
                        ARM_COSINE_BASELINE_GAUSSIAN at rho=0.90/corr=0.75)
    cited_prior_metric: 1.000  # exact-carrier saturation
    cited_prior_regime: {N_DIM: 2048, DG_DIM: 8192, N_PAIRS: 500,
                          cluster_cos: 0.90, corrupt: 0.75}
    test_regime: {same}
    tolerance: 0.01
    if_outside_tolerance: HARD_FAIL_REGRESSION_BROKEN

functional_requirements:
  - name: JL_prediction_validation_at_low_cluster
    plain_english: "Does the JL analytical prediction (baseline cosine
                     degrades with sib_std variance) actually hold when
                     cluster_cos is low enough that no exact-carrier signal
                     dominates?"
    primitive_used: cosine_argmax_over_normalized_stored_vectors
    addressed_by_arm: ARM_COSINE_C0.30_R0.50
  - name: boundary_observability_across_cluster_cos_sweep
    plain_english: "Where does COSINE transition from JL-degradation to
                     exact-carrier-saturation as cluster_cos rises?"
    primitive_used: same
    addressed_by_arm: ARM_COSINE at every (cluster_cos, corruption) cell
  - name: regression_bit_identity_high_cluster_high_corrupt
    plain_english: "Does the exact-carrier saturation observed in Cell 4 +
                     bipolar-vs-Gaussian reproduce at (0.90, 0.75)?"
    primitive_used: same
    addressed_by_arm: ARM_COSINE_C0.90_R0.75

# Compute architecture (USER-locked 2026-07-02)
compute_architecture:
  class: sequential-CPU with justification
  justification: >
    Cell is small (n_pairs=500, N_DIM=2048, 3 seeds, 24 arms per seed).
    Estimated per-seed wall ~30-60s on local CPU. GPU batching would give
    little speedup relative to setup overhead; per-arm computation is
    dominated by DG projection (matmul that numpy handles fine at this
    scale). Wall time < 10 min total is expected.
  storage_strategy: no_composition
  storage_justification: >
    Cell tests analytical-scope of retrieval primitive only. Each arm has
    its own storage (per-encoder); no cross-arm composition. Not applicable
    to sharded-vs-bundled physics law.

# Progress logging (Section 17)
progress_logging: print_flush_true

# CHUNKED + defensive error checking (Section 13)
cell_chunked: false  # single cell handles all seeds inline via
                     # write_partial_seed checkpoint (SH-4)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns

# Section 16 (run_mode verification post-dispatch)
expected_run_mode_on_smoke_landing: smoke
```

## Scope discipline (USER-locked)
SUBSTRATE KNOWS ALMOST NOTHING. This is a MECHANISM analytical-scope probe
on a SUPERVISED synthetic binding task. Determines the actual scope of a
prior Skunkworks JL atom (currently MM_STANDARD; may promote to
CG_MEASURED_BOUND with clear regime characterization). Does NOT grant
substrate general-knowledge or language capability.

## Cell-author self-correction pattern (CG_META tier)
If the verdict overclaims the honest read, cell-author self-corrects in
interpretation section. Anti-personification: substrate operates on integer
indices + real-valued vectors.

## Dispatch plan
1. Selftest first on local .venv (per formula-selftests discipline).
2. If selftests pass: smoke via `local_cpu_queue` (USER-locked SMOKE-only on
   local per 2026-07-01).
3. HARD HOLD before any FULL dispatch. Director + Skunkworks review verdict.

## Estimated wall time
Local CPU smoke: 60-180s expected (24 arms per seed x 3 seeds; each arm
~1-3s dominated by DG encode + retrieve).

Timeout: 1800s (30min) for safety margin.
