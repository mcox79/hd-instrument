# Pre-reg: substrate_spoke3_hippocampal_encoder_hippo_arm_cluster_cos_boundary_smoke (2026-07-03)

## Anchor name
`substrate_spoke3_hippocampal_encoder_hippo_arm_cluster_cos_boundary_smoke_2026_07_03`

## Cell file
`experiments/exp_substrate_spoke3_hippocampal_encoder_hippo_arm_cluster_cos_boundary_smoke_2026-07-03.py`

## Purpose (Skunkworks-approved rank-1 post-Sec6 boundary characterization)

Closes the empirical expansion criterion of
`MATH_CA3_AUTO_ASSOCIATOR_ANTI_SIGNAL_CROSS_GEOMETRY_2ND_WITNESS`
(CG_HN_ARCHITECTURAL) by directly characterizing whether the CA3 anti-signal
(HIPPO r@1 < DG_ONLY r@1 at cluster_cos~0.90) is universal or scope-refines
to a cluster_cos threshold. The prior lower-cluster-cos probe
(commit `6d0da70dc`) measured `ARM_HIPPO` across the {0.30,0.50,0.70,0.90} x
{0.50,0.75} grid but did NOT measure the CA3-ablated `ARM_HIPPO_DG_ONLY`
across the same grid. Without DG_ONLY at each grid cell the CA3-anti-signal
delta cannot be evaluated regime-by-regime.

The prior bipolar-vs-Gaussian smoke did measure a single cell
(cluster_cos~0.90, corrupt=0.75): HIPPO_GAUSSIAN r@1 = 0.5000
MEASURED@data/exp_substrate_spoke3_hippocampal_encoder_bipolar_vs_gaussian_filler_smoke_2026_07_03/metrics.json:per_arm_aggregate.ARM_HIPPO_GAUSSIAN.recall_at_1_mean,
HIPPO_DG_ONLY_GAUSSIAN r@1 = 0.6627 at the same cell -> delta = -0.163
(CA3 anti-signal). This cell propagates the DG_ONLY measurement across the
full 2D grid so the delta = HIPPO - DG_ONLY curve can be traced across
cluster_cos.

Cycle 178 substrate-side hypothesis (research drill
`notes/research_2x_drill_ca3_anti_signal_at_cluster_codebook_mechanism_analysis_2026-07-03.md`)
predicted an inverted-U for HIPPO across cluster_cos: mild cluster boosts
completion, high cluster collapses it. HP1 tests that on the HIPPO arm
directly.

## Framing discipline (LOAD-BEARING per USER 2026-07-02)
- SUBSTRATE KNOWS ALMOST NOTHING. This is a MECHANISM BOUNDARY probe on a
  SUPERVISED synthetic episodic-binding regime. NOT a general-knowledge or
  language claim.
- Anti-personification: substrate operates on integer indices + real-valued
  vectors.
- No sigma / capacity claims without formula verification.
- Regime constants: N_DIM=2048, DG_DIM=8192, DG_SPARSITY=0.02, N_PAIRS=500,
  CLUSTER_SIZE=5. T-F capacity C_TF = 8192 / (2 * ln(50)) ~= 1047
  THEORETICAL@. Load N_PAIRS/C_TF ~= 47.8%.
- Cell-author self-correction pattern (CG_META tier): if verdict overclaims,
  self-correct in interpretation.

## Prior-work check (concept-query 2026-07-03)
`bash tools/substrate_query.sh "HIPPO arm cluster_cos boundary CA3 anti-signal empirical closure"`
top-5 hits all at cosine <= 0.29 (generic wordnet / verbnet / dictionary
entries + one legacy `notes/research_drill_ness_hidden_objective_...` note
at 0.29). NONE at cosine>0.30. Genuinely novel probe within the substrate
KB. The prior lower-cluster-cos probe (2026-07-03) is the near-adjacent
work; this cell extends it by adding DG_ONLY across the same grid + single
regression check at the load-bearing regime.

## Task class
SAME as Cell 4 / bipolar-vs-Gaussian / lower-cluster-cos probe
(episodic-binding + partial-cue retrieval; N=500 pairs; adversarial
cluster-shared codebook; Gaussian filler). ONLY cluster_cos and corruption
vary across HIPPO/DG_ONLY arms.

## Sweep design (2D characterization; HIPPO arm coverage + DG_ONLY ablation)

### cluster_cos in {0.30, 0.50, 0.70, 0.90}
- 0.30 = essentially random (no cluster structure)
- 0.50 = mild cluster (Cycle 178 predicted BONUS regime)
- 0.70 = moderate cluster
- 0.90 = high cluster (Cell 4 regime; regression HIPPO=0.517 MEASURED@)

### corruption in {0.50, 0.75}
- 0.50 = moderate corruption
- 0.75 = Cell 4 regime; regression

### Filler geometry
Gaussian only (bipolar-vs-Gaussian probe already confirmed Gaussian is the
canonical regime; both geometries reproduce the anti-signal within noise).

## Arms

### Grid arms (2D characterization)
- `ARM_HIPPO_ONE_SHOT_C{cc}_R{corr}` (LOAD_BEARING) - hippocampal mechanism
  with CA3 auto-association (use_ca3=True, sparsify_after_settle=True). 4
  cluster_cos x 2 corruption = 8 grid cells.
- `ARM_HIPPO_DG_ONLY_C{cc}_R{corr}` (NEW; ablation) - DG-only baseline
  (use_ca3=False). Tests the CA3-anti-signal boundary directly: delta =
  HIPPO_ONE_SHOT - HIPPO_DG_ONLY at each grid cell. 8 grid cells.

### Regression arms (single cell only, at the load-bearing regression regime)
- `ARM_COSINE_BASELINE_C090_R075_regression` - confirms Cell 4 exact-carrier
  saturation reproduces bit-identical (Cell 4 = 1.000 MEASURED@).
- `ARM_RANDOM_BASELINE_C090_R075_regression` - chance floor sanity.

Total per-seed: 8 HIPPO + 8 DG_ONLY + 1 COSINE + 1 RANDOM = 18 arms.
`SEEDS = [11, 17, 23]` -> 18 * 3 = 54 total unit-instances.

### ARMS-MUST-DIFFER exemption (META_RULE_AF)
`arms_differ_exempted`: none. All 18 arms produce distinct queries per seed
(HIPPO uses CA3 settle; DG_ONLY uses raw DG code; COSINE returns corrupted
episodes; RANDOM draws fresh bipolar). Every arm has a distinct storage /
query pathway.

## HP band

### HP1 (Cycle 178 inverted-U validation for CA3 mechanism)
At corruption=0.50, HIPPO_ONE_SHOT mean r@1 at cluster_cos in {0.30, 0.50}
is monotonically HIGHER than at cluster_cos=0.90 by at least 0.10.
- MEASURED@ prior lower-cluster-cos probe (HYPOTHESIZED for this cell):
  HIPPO_C030_R050 = 1.0000, HIPPO_C090_R050 = 0.7567 -> observed delta =
  +0.243 in prior probe. HP1 requires reproduction of that monotone drop
  at >= 0.10.

### HP2 (CG_HN_ARCHITECTURAL boundary - regression + delta curve)
Two-part:
- HP2a (regression): HIPPO_ONE_SHOT at (cluster_cos=0.90, corrupt=0.75) mean
  r@1 in [0.44, 0.60] (regression band around prior 0.517 +/- 0.06;
  reproduces Cell 4 + prior lower-cluster-cos probe pattern).
  HYPOTHESIZED@ prior probe HIPPO_C090_R075 = 0.5107 MEASURED@; prior
  bipolar-vs-Gaussian HIPPO_GAUSSIAN = 0.5000 MEASURED@.
- HP2b (anti-signal delta at high cluster): delta at
  (cluster_cos=0.90, corrupt=0.75) = HIPPO_ONE_SHOT - HIPPO_DG_ONLY <= -0.05
  (CA3 hurts at high cluster; reproduces bipolar-vs-Gaussian
  delta = -0.163 MEASURED@).

### HP3 (mechanism scope characterization - boundary threshold)
Identify a cluster_cos threshold in [0.30, 0.90] where the sign of delta =
HIPPO_ONE_SHOT - HIPPO_DG_ONLY transitions. Specifically, at corrupt=0.75
sweep: delta at cluster_cos <= threshold is NEUTRAL or POSITIVE (|delta| <
0.05 or delta > 0); delta at cluster_cos >= threshold is NEGATIVE
(anti-signal delta <= -0.05). Threshold interior to sweep axis (i.e. not
just at 0.30 or 0.90 edges) = HP3 PASS.

`HARD_PASS = HP1 AND HP2a AND HP2b AND HP3`

## Failure classes

### HF-anti-signal-universal
HIPPO_ONE_SHOT <= HIPPO_DG_ONLY (delta <= -0.05) at ALL cluster_cos values
for at least one corruption sweep. CA3 anti-signal is a universal
architectural constraint; CG_HN_ARCHITECTURAL parent atom stays broad
scope; no cluster_cos scope-refinement possible.

### HF-regression-broken
HP2a fails: HIPPO_ONE_SHOT at (0.90, 0.75) outside [0.44, 0.60] regression
band. Codebook / encoder drift from prior probes; downstream boundary
verdict UNRELIABLE.

### HF-no-inverted-U
HP1 fails: HIPPO_ONE_SHOT at low cluster is NOT higher than at
cluster_cos=0.90 (delta < 0.10 or reversed). Refutes Cycle 178 substrate-
side inverted-U hypothesis for CA3 mechanism.

### HF-baseline-out-of-band-META_RULE_AG
RANDOM regression arm r@1 > 5*chance (0.010). Retrieval bug.

### HF-dg-sparse-rate-architectural
Hippocampal DG sparse rate outside [0.008, 0.040] at any grid cell.

### MIDDLE_BAND
Partial HP set fires (e.g. HP1 and HP2 fire but no interior boundary in
HP3).

## Regime
- N_DIM = 2048
- DG_DIM = 8192
- DG_SPARSITY = 0.02 (T-F capacity ~1047 THEORETICAL@
  C_TF = 8192/(2*ln(50)))
- N_PAIRS = 500 (load ~48% of C_TF)
- CLUSTER_SIZE = 5
- Filler geometry: Gaussian only, rho = cluster_cos target
- SEEDS = [11, 17, 23]
- Corruption values: {0.50, 0.75}

## Selftests (before smoke dispatch)
1. `arg_parse_default_is_smoke` - argparse default returns "smoke" mode.
2. `corrupt_cue_50pct_and_75pct` - both corruption values produce exact
   zero-count per row + preserve non-zero episode values.
3. `gaussian_within_cluster_cos_at_each_rho` - empirical filler-cos matches
   theoretical rho at each cluster_cos in {0.30, 0.50, 0.70, 0.90} within
   +/- 0.06.
4. `gaussian_filler_is_real_valued` - Gaussian fillers NOT bipolar
   (>10 unique values, variance in [0.7, 1.3]).
5. `arms_differ_hash_micro` - HIPPO_ONE_SHOT and HIPPO_DG_ONLY produce
   distinct queries on same episodes at (0.90, 0.75).
6. `determinism_gaussian` - same (seed, rho) -> bit-identical fillers.
7. `scale_sentinel_n_dim_8192` - codebook + corrupt-cue work at N_DIM=8192.
8. `regression_hippo_and_cosine_at_load_bearing_regime` - reduced-N (100
   pairs, 1 seed) probe at (0.90, 0.75) reproduces qualitative pattern:
   COSINE r@1 >= 0.95, HIPPO_ONE_SHOT r@1 >= 0.35, HIPPO_DG_ONLY r@1 >
   HIPPO_ONE_SHOT (anti-signal fires at reduced-N).
9. `primitive_selftests_chain` - `hdlab.hippocampal_encoder --self-test`
   returns 13/13 passed.

## Pre-reg gates (SCHEMA-VET compliance)
```yaml
# META_RULE_H (cardinality_ok)
expected_n_units: 54  # (8 HIPPO + 8 DG_ONLY + 1 COSINE + 1 RANDOM) * 3 seeds
cardinality_ok: mandatory

# META_RULE_J (per-unit failure-class instrumentation)
per_unit_failure_class: mandatory

# META_RULE_K (discriminator-fires)
discriminator_fires: delta_HIPPO_minus_DG_ONLY_transitions_sign_across_cluster_cos_sweep_at_least_one_corruption

# META_RULE_L (strictly-above-floor)
hp1_delta_strict: true  # >= 0.10 monotone drop (not just ">")
hp2a_regression_band: strict  # [0.44, 0.60] inclusive; strict outside
hp2b_anti_signal_strict: true  # delta <= -0.05
hp3_threshold_strict: true  # threshold interior to sweep axis

# META_RULE_M (calibration_check)
calibration_check: default_ok_for_this_regime
calibration_evidence: >
  Regime is direct extension of Cell 4 + bipolar-vs-Gaussian + prior lower-
  cluster-cos probe (all N_DIM=2048, DG_DIM=8192, sparsity=0.02, N_PAIRS=500).
  Anchor HIPPO_C090_R075 mean r@1 = 0.5107 MEASURED@ prior lower-cluster-cos
  probe; anchor HIPPO_DG_ONLY_C090_R075 delta = -0.163 MEASURED@ bipolar-vs-
  Gaussian probe. Bands transferred directly.

# META_RULE_AC (HYPOTHESIZED/MEASURED/THEORETICAL tagging)
# All numbers tagged in-line (see cell docstring + HP bands).

# META_RULE_AF (arms-differ-verified)
arms_differ_verified: true

# META_RULE_AG (baseline_in_band)
baseline_in_band: true  # RANDOM arm r@1 <= 5*chance = 0.010

# META_RULE_AH (final_metrics_atomicity)
final_metrics_atomicity: tmp_replace

# Discriminator-must-survive-scale
discriminator_survives_scale: analytical_justification
# Rationale: same N_DIM/DG_DIM/N_PAIRS regime as prior lower-cluster-cos
# probe which produced discriminative measurements HIPPO_C090_R075 = 0.5107
# with r@5 approaching but not saturating. HP2b anti-signal delta was
# MEASURED@ -0.163 at the load-bearing cell in bipolar-vs-Gaussian smoke;
# 6-cell delta grid extension is the discriminator this cell tests.

# Section-15 gates
sweep_alignment_verdict: ALIGNED
# cluster_cos IS what both HIPPO and DG_ONLY encoders directly experience
# through the filler variance channel; no compositional dilution.

discriminating_fraction: 0.50
# Prior probe HIPPO grid: C030=1.0, C050 in [0.997, 1.0], C070 in [0.946,
# 0.999], C090 in [0.510, 0.757]. 2/4 cluster_cos values (0.70, 0.90) are
# below saturation at at least one corruption. DG_ONLY expected to expose
# more discriminating band because CA3 collapse is regime-specific;
# prediction is 3/4 cluster_cos cells in discriminating band on the delta
# curve.

composition_edges: []

positive_control_arms:
  - arm: ARM_HIPPO_ONE_SHOT_C090_R075
    primitive: hippocampal_encoder_with_ca3
    cited_prior_atom: (MEASURED@ prior lower-cluster-cos probe metrics.json
                        HIPPO_C090_R075 mean r@1 = 0.5107 +
                        bipolar-vs-Gaussian HIPPO_GAUSSIAN r@1 = 0.5000)
    cited_prior_metric: 0.5107
    cited_prior_regime: {N_DIM: 2048, DG_DIM: 8192, N_PAIRS: 500,
                          cluster_cos: 0.90, corrupt: 0.75, filler: gaussian}
    test_regime: {same}
    tolerance: 0.06
    if_outside_tolerance: HARD_FAIL_REGRESSION_BROKEN
  - arm: ARM_COSINE_BASELINE_C090_R075_regression
    primitive: cosine_baseline
    cited_prior_atom: (MEASURED@ prior lower-cluster-cos probe
                        COSINE_C090_R075 mean r@1 = 1.0000)
    cited_prior_metric: 1.0000
    tolerance: 0.01
    if_outside_tolerance: HARD_FAIL_REGRESSION_BROKEN

functional_requirements:
  - name: cluster_cos_boundary_for_CA3_anti_signal
    plain_english: "At what cluster_cos does the CA3 auto-associator stop
                     hurting one-shot recall? Below the threshold CA3 should
                     be neutral or beneficial; above it CA3 collapses the
                     completion."
    primitive_used: hippocampal_encoder retrieve(use_ca3=True) vs
                    retrieve(use_ca3=False)
    addressed_by_arm: delta = ARM_HIPPO_ONE_SHOT - ARM_HIPPO_DG_ONLY across
                       grid
  - name: cycle_178_inverted_U_for_HIPPO_mechanism
    plain_english: "Does the CA3 mechanism produce an inverted-U across
                     cluster_cos (mild boost at low cluster, collapse at
                     high cluster) as substrate-KB Cycle 178 hypothesized?"
    primitive_used: hippocampal_encoder retrieve(use_ca3=True)
    addressed_by_arm: HIPPO_ONE_SHOT at cluster_cos in {0.30, 0.50, 0.70,
                       0.90} at corrupt=0.50
  - name: regression_at_load_bearing_cell
    plain_english: "Does the load-bearing (0.90, 0.75) HIPPO_ONE_SHOT and
                     COSINE regression reproduce Cell 4 pattern?"
    primitive_used: same
    addressed_by_arm: HIPPO_ONE_SHOT and COSINE at (0.90, 0.75)

compute_architecture:
  class: sequential-CPU with justification
  justification: >
    Cell is small (n_pairs=500, N_DIM=2048, 3 seeds, 18 arms per seed).
    Estimated per-seed wall ~30-60s on local CPU. DG projection is the
    heaviest step and numpy handles it fine at this scale. Wall time < 10
    min total expected. GPU batching would give little speedup relative to
    setup overhead.
  storage_strategy: no_composition
  storage_justification: >
    Cell tests analytical-scope of retrieval primitive only. Each arm has
    its own storage (per-encoder); no cross-arm composition. Not applicable
    to sharded-vs-bundled physics law.

progress_logging: print_flush_true

cell_chunked: false  # single cell handles all seeds inline via per-seed
                     # checkpoint (SH-4)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns

expected_run_mode_on_smoke_landing: smoke
```

## Scope discipline (USER-locked)
SUBSTRATE KNOWS ALMOST NOTHING. MECHANISM boundary probe on a SUPERVISED
synthetic episodic-binding regime. Characterizes the empirical scope of a
prior CG_HN_ARCHITECTURAL atom; may promote to CG_META tier
(scope-refinement) or keep parent broad-scoped. Does NOT grant substrate
general-knowledge or language capability.

## Cell-author self-correction pattern (CG_META tier)
If verdict overclaims relative to per-arm reads, cell-author self-corrects
in interpretation section.

## FRAMING NOTE (director-side)
The prior lower-cluster-cos probe DID measure HIPPO across the same grid
(commit 6d0da70dc, metrics landed). The genuinely NEW measurement this
cell adds is HIPPO_DG_ONLY across the same grid so the delta = HIPPO -
DG_ONLY curve can be traced by regime. The spawn-prompt's claim
"HIPPO arm was NOT directly measured across the same grid" is not aligned
with the on-disk metrics; flagged to Director in exp_dev report.

## Dispatch plan
1. Selftest on local .venv (per formula-selftests discipline).
2. If selftests pass: smoke via `local_cpu_queue` (USER-locked SMOKE-only
   on local).
3. HARD HOLD before any FULL dispatch. Director + Skunkworks review verdict.

## Estimated wall time
- Smoke: ~5-10 min on local CPU (3 seeds x ~18 arms x few seconds per arm).
- FULL: deferred; regime is already smoke-sufficient for boundary
  characterization at this scale (500 pairs at ~48% T-F load).

## Timeout
Per-experiment `--timeout 1800` (30 min hard cap; well above expected wall).
