# Pre-registration: cross_axis_m_n_k_factorization_beta_5_bridging_v2

**Date filed:** 2026-07-02
**Anchor:** `cross_axis_m_n_k_factorization_beta_5_bridging_v2`
**Backend:** torch.cuda (overnight_queue)
**Timeout:** 3600s per seed cell (huge margin per Research spawn)
**Seeds:** 7, 13, 19 (single-seed-per-cell architecture per §13)
**Cell files:**
- `experiments/exp_cross_axis_m_n_k_factorization_beta_5_bridging_v2_seed_7.py`
- `experiments/exp_cross_axis_m_n_k_factorization_beta_5_bridging_v2_seed_13.py`
- `experiments/exp_cross_axis_m_n_k_factorization_beta_5_bridging_v2_seed_19.py`
- Core: `experiments/_substrate_cross_axis_m_n_k_factorization_beta_5_bridging_v2_core.py`

## Purpose (iteration on v1 β=8 empirical saturation)

v1 (`cross_axis_m_n_k_factorization_beta_8_bridging_v1`, DIS_beta8) SMOKE
landed MIDDLE_BAND per META_RULE_K discriminator-fires gate:
- DIS_beta8 M-axis range = 0.0001 across smoke grid (all recalls 0.9999-1.0000)
- PREVIEW_CORNER (M=16384, N=8192, K=500, β=8): recall = 0.9991
- Follow-up numpy sim (M in {32768, 65536, 131072}, β=8): recalls 0.9920-0.9981

Load-bearing finding: β=8 saturates the substrate across the production
(M, N, K) grid; softmax value-averaging amplifies FAR MORE than the CRLB
2x rule-of-thumb (empirically ~15x at β=8). See atomize hand-off note:
`notes/exp_dev_findings/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_HF_beta8_SATURATES_2026-07-02.md`

v2 iterates DIS_β to 5 (halfway between v2 CG at β=4 and empirical β=8
saturation). If HP:
- β=4 CG + β=5 CG + documented β=8 saturation upper bound
- => META atom `substrate_axes_factorize_across_beta_regime_2axis_v1` CG
- => M3 architecture claim: substrate axes are independent design knobs
  across production β range.

## Substrate-KB prior-work check (2026-07-02)

Concept-query `cross-axis factorization beta 5 bridging discriminating M N K`
via `bash tools/substrate_query.sh` returned max cosine = **0.3066** for
"Discriminating outcomes" (general terminology entity, off-topic). Top 5
hits all below 0.31 and all off-topic.

**Verdict:** Genuinely NOVEL iteration. First β=5 cross-axis bridging on
substrate; v1 β=8 established the empirical upper bound for saturating
regime.

## Arms + axes

| Arm         | β    | Interpretation                                     |
|-------------|------|----------------------------------------------------|
| STD_beta13  | 13.0 | v1_2d_coarse saturating regime (positive control)  |
| DIS_beta5   |  5.0 | Discriminating bridging arm (NEW, iteration on β=8)|

### Design choice: WHY NOT STD_beta5 + DIS_beta5?

Same rationale as v1 (documented + carried forward):
1. **META_RULE_AF violation-by-construction:** two arms at same β with
   identical M/N/K/data → same hash → HARD_FAIL_META_RULE_AF.
2. **HP_SEPARABLE unreachable at β=5:** CRLB p_win at (M=32768, N=2048,
   β=5) = 0.003 raw; softmax-amplified <<0.95 gate. Would HARD_FAIL by
   physics not by mechanism.
3. **STD_β13 doubles as v1_2d_coarse positive-control** (Gate D reproduce
   prior CG at test regime).

| Axis | Full values      | Interpretation                              |
|------|------------------|---------------------------------------------|
| M    | {1000, 32768}    | 32x memory-size spread                      |
| N    | {2048, 8192}     | 4x dimensionality spread                    |
| K    | {100, 4000}      | 40x query-count spread                      |

2 arms × 2 × 2 × 2 = **16 phase points per seed** × 3 seeds = **48 units**.

## Mechanism

Dense-Hopfield READ-REPLACE per Cell D v2 CG regime, β = arm-specific:
- V (value-dim) = 256 fixed
- Random ±1 keys/vals per phase point (rng seed = seed + M×3 + N×5 + K×7;
  IDENTICAL across arms → recall differences attribute to β only)
- Queries = key_i + 0.05 noise
- K > M path: `numpy.choice(replace=True)` (bug-fixed 2026-07-02 in v1 core;
  carried forward)
- Readout via `hdlab.chunked_attention.chunked_attention_readout` (T2 CG)
- Recall = mean cosine similarity between target val and readout

## Falsifiable verdicts

### HARD_PASS (factorization holds at β=5; META CG-lift)

Requires ALL:
- **HP_STD_β13_SATURATES** (control): all 8 STD_beta13 phase points recall ≥ 0.95
- **HP_DIS_β5_MECHANISM** (discriminator-fires META_RULE_K):
  DIS_beta5 M-axis range ≥ 0.30 across (N, K) subgrid
- **HP_INTERACTION_BELOW_FLOOR** (factorization signature):
  all THREE interaction terms (MK, MN, NK) < 0.05 at 3-seed mean
- **HP_CROSS_SEED_TIGHT** (reproducibility): cv < 0.15 on M-axis range across 3 seeds

### MIDDLE_BAND

- **MB_FACTORIZATION_BREAKS_β5**: any interaction ≥ 0.10 at 3-seed mean
  → factorization is β-dependent, breaks at β=5 (physics finding)
- **MB_DIS_MECHANISM_DID_NOT_FIRE**: DIS range < 0.30
  (β=5 still saturates → discriminating band tighter than expected; iterate to β=4.5 or β=6)
- **MB_STD_ARM_NOT_SEPARABLE_UNEXPECTED**: STD at β=13 did NOT saturate
  → v1_2d_coarse regression signal → investigate upstream primitive drift

### HARD_FAIL

- HF_CARDINALITY_META_RULE_H: n_phase_points ≠ 16
- HF_ARM_IDENTICAL_META_RULE_AF: any two phase points bit-identical hashes
- HF_MEMORY_OVERFLOW: gpu_mem_peak_mb > 4000 at any phase point
- SMOKE_MB_PREVIEW_SATURATED: preview corner recall ≥ 0.95

## SCHEMA-VET pre-dispatch fields

```yaml
cardinality_ok: verified pre-dispatch
EXPECTED_N_UNITS: 16  # 2 arms x 2 M x 2 N x 2 K, per seed
arms_differ_verified: verified at smoke (hash-check across 16 phase points)
final_metrics_atomicity: tmp_replace
except_systemexit_raise_before_exception: true
discriminator_reachability:
  status: DECLARED_REACHABLE_at_crlb
  crlb_derivation: |
    THEORETICAL@CRLB Hebbian softmax:
      p_win = 1/(1 + M*exp(-beta*margin))
      margin = 1 - noise^2/2 - sqrt(2*log(M)/N)
    beta=5 predictions (noise=0.05):
      (M=1000,  N=2048): margin=0.917, p_win=0.089
      (M=1000,  N=8192): margin=0.958, p_win=0.107
      (M=32768, N=2048): margin=0.898, p_win=0.003
      (M=32768, N=8192): margin=0.948, p_win=0.004
    Empirical softmax amplification (from v1 beta=8 finding):
      at beta=8 M=32768: CRLB p_win = 0.057, MEASURED recall = 0.998
      amplification factor ~= 17x at high beta
    At beta=5 M=32768 CRLB p_win = 0.004; amplification factor should be
      LOWER at lower beta (weaker concentration); predicted recall ~0.10-0.25.
    At beta=5 M=1000 CRLB p_win = 0.107; predicted recall ~0.60-0.80.
    Predicted M-axis range: ~0.50-0.65 (well above HP floor 0.30).
    HP_INTERACTION floor 0.05 matches beta=4 CG value.
  amplification_factor_calibration: |
    v1 rule-of-thumb was 2x (from cell-author estimate); empirical from
    v1 beta=8 finding was ~17x. Corrected estimate for beta=5 is 5-8x
    (weaker concentration than beta=8; still amplified from CRLB).
    HYPOTHESIZED range for beta=5.
crlb_formula_reference: |
  chunked_attention_readout per T2 primitive; Recall via softmax
calibration_check: default_ok_for_this_regime
  formula: fixed beta at arm-specific value (13.0 STD, 5.0 DIS)
  evidence: |
    STD at beta=13 saturation VERIFIED@v1_2d_coarse landed 27/27 = 1.000
    DIS at beta=4 CG VERIFIED@cross_axis_m_n_k_discriminating_arm_v2 3-seed
      M-axis range 0.590/0.597/0.590 + INT terms < 0.05
    DIS at beta=8 empirically SATURATED VERIFIED@v1_bridging smoke MB
    beta=5 THEORETICAL@CRLB targets discriminating band between beta=4 and beta=8
baseline_in_band:
  STD_arm: DECLARED_SATURATED (HP replication of v1_2d_coarse at beta=13)
  DIS_arm: predicted 0.05 < recall < 0.95 at multiple phase points
    THEORETICAL@CRLB: DIS at (M=1000, N=8192, K=100) ~= 0.70; DIS at
    (M=32768, N=2048, K=4000) ~= 0.15 (SPAN in-band)
discriminator_survives_scale:
  method_C_INVERTED_preview_arm: true
    PREVIEW_CORNER_SMOKE = (arm=DIS_beta5, M=16384, N=8192, K=500).
    THEORETICAL@CRLB at (M=16384, N=8192, beta=5) predicts p_win ~= 0.008,
    softmax-amplified predicted recall ~0.15-0.30; well below 0.95 gate.
    If preview >= 0.95, beta=5 still saturates and FULL dispatch REJECTED.
cell_chunked: true
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
composition_edges:
  - from: chunked_attention_readout (T2 primitive)
    to: cosine-similarity recall metric
    A_natural_output_shape: (K, V) float32
    B_natural_input_shape: (K, V) target vals
    verdict: SHAPE_MATCH
positive_control_arms:
  - arm: STD_beta13 (positive-control; reproduces v1_2d_coarse saturation)
    primitive: chunked_attention_readout at beta=13
    cited_prior_atom: cross_axis_m_n_k_2d_coarse_gpu_v1 (all 27/27 recall=1.000)
    cited_prior_metric: 1.000 uniform
    cited_prior_regime: {M: [4096, 16384], N: [4096, 16384], K: [200, 1000], beta: 13}
    test_regime: {M: [1000, 32768], N: [2048, 8192], K: [100, 4000], beta: 13}
    tolerance: 0.05 (expect all 8 STD points recall >= 0.95)
    if_outside_tolerance: MB_STD_ARM_NOT_SEPARABLE_UNEXPECTED (regression)
    regime_extension_audit: SHAPE_MATCH
  - arm: DIS_beta5 (discriminating bridging; extends beta=4 CG factorization)
    primitive: chunked_attention_readout at beta=5
    cited_prior_atom: cross_axis_m_n_k_discriminating_arm_v2 (DIS_beta4 CG)
    cited_prior_metric: M-axis range 0.59; INT terms < 0.05 at 3-seed
    cited_prior_regime: {M: [1000, 32768], N: [2048, 8192], K: [100, 4000], beta: 4}
    test_regime: {M: [1000, 32768], N: [2048, 8192], K: [100, 4000], beta: 5}
    tolerance: interaction-term factorization signature
    if_outside_tolerance: MB_FACTORIZATION_BREAKS_beta_5 (physics finding)
    regime_extension_audit: SHAPE_MATCH (adjacent beta; same grid)
functional_requirements:
  - fr: reproduce v1_2d_coarse saturation as CONTROL (STD at beta=13)
    primitive: chunked_attention_readout at beta=13
  - fr: discriminate mechanism at bridging beta=5 (mechanism-fires check)
    primitive: chunked_attention_readout at beta=5 with wide M-spread
  - fr: measure joint interaction from 2x2 factorial on M/N/K axes at beta=5
    primitive: adjacency-based interaction TERM computation in compute_verdict
  - fr: verify factorization signature (INT < 0.05) matches beta=4 CG signature
    primitive: 3-seed reproducibility of interaction-term measurement
  - fr: bounded GPU memory at max corner (M=32768, N=8192, K=4000)
    primitive: chunked_attention_readout chunk=1024 analytical bound ~1.3 GB
progress_logging: print_flush_true
progress_cadence_expected_s: 60
effective_vs_nominal_parameter_audit:
  swept_params: {arm: [STD_beta13, DIS_beta5], M: [1000, 32768], N: [2048, 8192], K: [100, 4000]}
  effective_params_per_primitive:
    chunked_attention_readout: all axes match nominal (direct pass-through)
  sweep_alignment_verdict: ALIGNED
bracket_includes_discriminating_band:
  predicted_recall_STD_beta13 arm: uniformly ~1.000 (positive-control baseline)
  predicted_recall_DIS_beta5 arm (softmax-amplified from CRLB, factor 5-8x):
    (M=1000, N=2048, K=100):   ~0.60  (mid)
    (M=1000, N=2048, K=4000):  ~0.60
    (M=1000, N=8192, K=100):   ~0.70  (mid-high)
    (M=1000, N=8192, K=4000):  ~0.70
    (M=32768, N=2048, K=100):  ~0.10  (low; large M, small N)
    (M=32768, N=2048, K=4000): ~0.10
    (M=32768, N=8192, K=100):  ~0.20  (low; large M)
    (M=32768, N=8192, K=4000): ~0.20
  points_predicted_in_band_0.30_to_0.70: 4 of 8 DIS arm
  discriminating_fraction: 0.5 (well above 0.30 SCHEMA-VET §15-B floor)
  note: |
    Factorial-endpoint exemption inherited from v2 (successful precedent);
    v2 core's factorial-INTERACTION-TERM computation requires easy AND
    hard corners of the 2x2 factorial. Excluding either breaks interaction.
```

## Timeout justification (--timeout 3600s per seed cell)

Research spawn specified 3600s per seed.
- Per-phase-point GPU wall estimate at max corner (M=32768, N=8192, K=4000):
  matmul-heavy, ~40-80s GPU
- 16 phase points × 60s avg = 960s expected; × 1.5 margin = 1440s
- 3600s per Research spawn (~4x margin over est)

## Dispatch plan

- **Smoke:** local_cpu_queue (USER 2026-07-01 LOCKED: SMOKE ONLY on local)
- **FULL:** overnight_queue (GPU); requires push to origin/main (harness-denied
  to exp_dev). Route via hdi_orchestrator per Fix #24.

## Discipline verification (this cell)

- Substrate-KB concept-query FIRST: DONE (max cosine=0.31, off-topic)
- CRLB reachability computed in Python: DONE (p_win by regime shown above)
- v1 β=8 saturation empirical finding preserved in atomize note + docstring
- Discriminator-must-survive-scale: preview_corner method C INVERTED
- STD_β13 preserved as positive-control (Gate D + Fix #24 rationale)
- ARMS-MUST-DIFFER: two different β values (13.0 vs 5.0) → distinct hashes
- CARDINALITY_OK = 48 (3 seeds × 16 phase points)
- All numbers tagged MEASURED@ / THEORETICAL@ / HYPOTHESIZED@ / CITED@

## References

- v1 saturated MB source: `experiments/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_seed_7.py`
  MEASURED@`data/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_smoke_seed_7/metrics.json`
- v1 atomize hand-off: `notes/exp_dev_findings/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_HF_beta8_SATURATES_2026-07-02.md`
- β=4 CG source: `experiments/exp_cross_axis_m_n_k_discriminating_arm_v2_seed_7.py`
  + prereg `preregs/2026-07-01_cross_axis_m_n_k_discriminating_arm_v2.md`
- β=13 saturated source: `experiments/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7.py`
- Testbed T2 primitive: `hdlab/chunked_attention.py`
- META atom target: `substrate_axes_factorize_across_beta_regime_2axis_v1`
  (unfired; promotes to CG on this cell HP as β=4/β=5 dual evidence + β=8/β=13
  saturation upper bounds)
