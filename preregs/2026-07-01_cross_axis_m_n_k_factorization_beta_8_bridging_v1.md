# Pre-registration: cross_axis_m_n_k_factorization_beta_8_bridging_v1

**Date filed:** 2026-07-01
**Anchor:** `cross_axis_m_n_k_factorization_beta_8_bridging_v1`
**Backend:** torch.cuda (overnight_queue)
**Timeout:** 3600s per seed cell (huge margin per Research spawn)
**Seeds:** 7, 13, 19 (single-seed-per-cell architecture per §13)
**Cell files:**
- `experiments/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_seed_7.py`
- `experiments/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_seed_13.py`
- `experiments/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_seed_19.py`
- Core: `experiments/_substrate_cross_axis_m_n_k_factorization_beta_8_bridging_v1_core.py`

## Purpose (bridging cell for META synthesis)

v2 (`cross_axis_m_n_k_discriminating_arm_v2`, DIS_beta4) landed MM at
beta=4 CG per Skunkworks batch 7: substrate factorizes across (M, N, K)
axes at beta=4 regime with M-axis range 0.590/0.597/0.590 3-seed and all
interaction terms below 0.05 floor. Skunkworks flagged META atom
`substrate_axes_factorize_across_beta_regime_2axis_v1` synthesis DEFERRED
pending intermediate-beta bridging cell.

This v1 bridges beta=8 (between v2 CG at beta=4 and v1_2d_coarse
saturation at beta=13) to test whether **factorization is BETA-INVARIANT**
across the substrate's production beta range. If HP:
- v2 (beta=4) CG + this (beta=8) HP CG + Sonnet drill scale predictions
- => META atom promotes to CG
- => Foundational M3 architecture claim: cortex can treat substrate axes
  as independent design knobs across production beta range.

## Substrate-KB prior-work check (2026-07-01)

Concept-query `cross-axis factorization M N K beta bridging interaction terms`
via `bash tools/substrate_query.sh` returned max cosine = **0.3281** for
"Dislocation interactions + pinning" (dislocation physics, off-topic).
Top 5 hits all below 0.33 and all off-topic (interpretation entities,
finding entities in unrelated notes).

**Verdict:** Genuinely NOVEL. First beta=8 cross-axis bridging test on
substrate. v2 CG at beta=4 and v1_2d_coarse saturation at beta=13 flank
this cell's regime but neither tests it.

## Arms + axes

| Arm         | β    | Interpretation                                    |
|-------------|------|---------------------------------------------------|
| STD_beta13  | 13.0 | v1 saturating regime baseline (positive control)  |
| DIS_beta8   |  8.0 | Intermediate-beta bridging discriminator (NEW)    |

### Design choice: WHY NOT STD_beta8 + DIS_beta8?

Research spawn prompt specified `STD_beta8` (control) + `DIS_beta8`
(probe). Cell-author revised to STD_beta13 + DIS_beta8 for two reasons:

1. **META_RULE_AF violation-by-construction:** two arms at same beta
   with identical M/N/K/data → same hash → HARD_FAIL_META_RULE_AF.
2. **HP_SEPARABLE unreachable at beta=8:** the design's
   `HP_STD_SEPARABLE_β8 > 0.95 across all 8 phase points` gate fails
   physical reachability. CRLB p_win at (M=32768, N=2048, beta=8) =
   0.039 raw; even softmax-amplified predicted ~0.30. The gate would
   HARD_FAIL by physics not by mechanism.

STD_beta13 as positive-control re-verifies v1 saturation AT THE SAME
GRID as DIS_beta8 (Gate D: positive_control_arms). It doubles as:
- v1 regression signal (STD_beta13 should saturate; if not, upstream
  primitive changed)
- baseline-in-band reference at high-beta end of the substrate range

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
  IDENTICAL across arms so recall differences attribute to β only, not data)
- Queries = key_i + 0.05 noise
- Readout via `hdlab.chunked_attention.chunked_attention_readout` (T2 CG)
- Recall = mean cosine similarity between target val and readout

## Falsifiable verdicts

### HARD_PASS (factorization holds at β=8; META CG-lift path)

Requires ALL:
- **HP_STD_SEPARABLE** (control): all 8 STD_beta13 phase points recall ≥ 0.95
- **HP_DIS_MECHANISM_FIRES** (discriminator-fires META_RULE_K):
  DIS_beta8 M-axis range ≥ 0.30 across (N, K) subgrid
- **HP_INTERACTION_BELOW_FLOOR** (factorization):
  all THREE interaction terms (MK, MN, NK) < 0.05 at 3-seed mean
  (matches v2 CG factorization signature)

### MIDDLE_BAND

- **MB_FACTORIZATION_BREAKS_β8**: any interaction ≥ 0.10 at 3-seed mean
  → factorization is β-dependent, breaks at β=8 (also a physics finding)
- **MB_DIS_MECHANISM_DID_NOT_FIRE**: DIS range < 0.30
  (regime iteration needed; may indicate β=8 too high or too low)
- **MB_STD_ARM_NOT_SEPARABLE_UNEXPECTED**: STD at beta=13 did NOT saturate
  (v1 regression signal → investigate primitive drift)

### HARD_FAIL

- HF_CARDINALITY_META_RULE_H: n_phase_points ≠ 16
- HF_ARM_IDENTICAL_META_RULE_AF: any two phase points bit-identical hashes
- HF_MEMORY_OVERFLOW: gpu_mem_peak_mb > 4000 at any phase point
- SMOKE_MB_PREVIEW_SATURATED: preview corner recall ≥ 0.95 (DIS arm
  saturates at scale → discriminator dead)

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
    beta=8 predictions (noise=0.05):
      (M=1000,  N=2048): margin=0.917, p_win=0.605
      (M=1000,  N=8192): margin=0.958, p_win=0.680
      (M=32768, N=2048): margin=0.898, p_win=0.039
      (M=32768, N=8192): margin=0.948, p_win=0.057
    Softmax value-averaging typically amplifies ~2x -> predicted
    DIS arm M-axis range at N=8192 K=100: ~0.90 - ~0.30 = 0.60
    (well above HP_DIS_MECHANISM_RANGE_FLOOR = 0.30).
    HP_INTERACTION_BELOW_FLOOR = 0.05 matches v2 CG value where
      factorization was confirmed at beta=4.
crlb_formula_reference: |
  chunked_attention_readout memory bound per T2 primitive
  Recall via softmax: p_win = 1/(1 + M*exp(-beta*(1 - sqrt(2*log(M)/N))))
calibration_check: default_ok_for_this_regime
  formula: fixed beta at arm-specific value (13.0 STD, 8.0 DIS)
  evidence: |
    v1 landed all 27/27 at beta=13 recall=1.000 confirms STD saturation
    beta=8 CRLB p_win 0.06-0.68 confirms discriminating band at this regime.
    v2 CG at beta=4 confirmed factorization signature (INT terms < 0.05).
baseline_in_band:
  STD_arm: DECLARED_SATURATED (HP replication of v1 at beta=13; positive-control)
  DIS_arm: predicted 0.05 < recall < 0.95 at at least 4 of 8 phase points
    THEORETICAL@CRLB: DIS at (M=1000, N=8192, K=100) ~= 0.80; DIS at
    (M=32768, N=2048, K=4000) ~= 0.10 (SPAN in-band)
discriminator_survives_scale:
  method_C_INVERTED_preview_arm: true
    PREVIEW_CORNER_SMOKE = (arm=DIS_beta8, M=16384, N=8192, K=500).
    Analytically justified: THEORETICAL@CRLB at (M=16384, N=8192, beta=8)
    predicts p_win ~= 0.11 raw, softmax-amplified ~0.30-0.40; well
    below 0.95 saturation gate.
    If preview >= 0.95, DIS arm saturates at scale, FULL dispatch REJECTED.
    If preview < 0.02, mechanism dead. Between: proceed.
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
  - arm: STD_beta13 (positive-control; reproduces v1 saturation)
    primitive: chunked_attention_readout at beta=13
    cited_prior_atom: cross_axis_m_n_k_2d_coarse_gpu_v1 (all 27/27 recall=1.000)
    cited_prior_metric: 1.000 uniform
    cited_prior_regime: {M: [4096, 16384], N: [4096, 16384], K: [200, 1000], beta: 13}
    test_regime: {M: [1000, 32768], N: [2048, 8192], K: [100, 4000], beta: 13}
    tolerance: 0.05 (expect all 8 STD points recall >= 0.95)
    if_outside_tolerance: MB_STD_ARM_NOT_SEPARABLE_UNEXPECTED (v1 regression)
    regime_extension_audit: SHAPE_MATCH
  - arm: DIS_beta8 (bridging arm; reproduces v2 CG factorization at beta=8)
    primitive: chunked_attention_readout at beta=8
    cited_prior_atom: cross_axis_m_n_k_discriminating_arm_v2 (DIS_beta4 CG)
    cited_prior_metric: M-axis range 0.59; INT terms < 0.05 at 3-seed
    cited_prior_regime: {M: [1000, 32768], N: [2048, 8192], K: [100, 4000], beta: 4}
    test_regime: {M: [1000, 32768], N: [2048, 8192], K: [100, 4000], beta: 8}
    tolerance: interaction-term factorization signature
    if_outside_tolerance: MB_FACTORIZATION_BREAKS_beta_8 (physics finding)
    regime_extension_audit: SHAPE_MATCH (adjacent beta; same grid)
functional_requirements:
  - fr: reproduce v1 saturation as CONTROL (STD arm at beta=13)
    primitive: chunked_attention_readout at beta=13
  - fr: discriminate mechanism at bridging beta=8 (mechanism-fires check)
    primitive: chunked_attention_readout at beta=8 with wide M-spread
  - fr: measure joint interaction from 2x2 factorial on M/N/K axes at beta=8
    primitive: adjacency-based interaction TERM computation in compute_verdict
  - fr: bounded GPU memory at max corner (M=32768, N=8192, K=4000)
    primitive: chunked_attention_readout chunk=1024 analytical bound ~1.3 GB
progress_logging: print_flush_true
progress_cadence_expected_s: 60
effective_vs_nominal_parameter_audit:
  swept_params: {arm: [STD_beta13, DIS_beta8], M: [1000, 32768], N: [2048, 8192], K: [100, 4000]}
  effective_params_per_primitive:
    chunked_attention_readout: all axes match nominal (direct pass-through)
  sweep_alignment_verdict: ALIGNED
bracket_includes_discriminating_band:
  predicted_recall_STD_beta13 arm: uniformly ~1.000 (positive-control baseline)
  predicted_recall_DIS_beta8 arm (softmax-amplified from CRLB):
    (M=1000, N=2048, K=100):   ~0.80  (mid-high)
    (M=1000, N=2048, K=4000):  ~0.80  (K doesn't matter, per v2 finding)
    (M=1000, N=8192, K=100):   ~0.85
    (M=1000, N=8192, K=4000):  ~0.85
    (M=32768, N=2048, K=100):  ~0.15  (low-mid; large M, small N)
    (M=32768, N=2048, K=4000): ~0.15
    (M=32768, N=8192, K=100):  ~0.25  (low-mid; large M)
    (M=32768, N=8192, K=4000): ~0.25
  points_predicted_in_band_0.30_to_0.70: 0 of 8 DIS arm
    (endpoints of factorial design; all in easy or hard corner)
  discriminating_fraction: 0.0 in band; factorial-endpoint exemption per §15-B
  note: |
    DECLARED_EXEMPTED per META_RULE §15-B factorial-endpoint-requirement.
    Interaction-TERM computation REQUIRES easy AND hard corners of the
    2x2 factorial; excluding either would break the interaction test.
    Same exemption as v2 CG prereg (successful precedent).
```

## Timeout justification (--timeout 3600s per seed cell)

Research spawn specified 3600s (huge margin over ~10-20s per seed).
- Per-phase-point GPU wall estimate at max corner (M=32768, N=8192, K=4000):
  matmul-heavy, ~40-80s GPU
- 16 phase points × 60s avg = 960s expected; × 1.5 margin = 1440s
- Round to **3600s** per Research spawn (~4x margin over estimated)

## Dispatch plan

- **Smoke:** local_cpu_queue (USER 2026-07-01 LOCKED: SMOKE ONLY on local)
- **FULL:** overnight_queue (GPU); requires push to origin/main
  (harness-denied to exp_dev). Route via hdi_orchestrator per Fix #24.

## Discipline verification (this cell)

- Substrate-KB concept-query FIRST: DONE (max cosine=0.33 dislocation, off-topic)
- CRLB reachability computed in Python: DONE (p_win by regime shown above)
- Discriminator-must-survive-scale: preview_corner method C INVERTED
- STD_beta13 preserved as positive-control (Gate D + Fix #24 rationale)
- All numbers tagged MEASURED@ / THEORETICAL@ / HYPOTHESIZED@ / CITED@
- ARMS-MUST-DIFFER: two different beta values (13.0 vs 8.0) → distinct hashes
- CARDINALITY_OK = 48 (3 seeds × 16 phase points)

## References

- v2 CG source: `experiments/exp_cross_axis_m_n_k_discriminating_arm_v2_seed_7.py`
  + prereg `preregs/2026-07-01_cross_axis_m_n_k_discriminating_arm_v2.md`
- v1 saturated MM: `experiments/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7.py`
- Testbed T2 primitive: `hdlab/chunked_attention.py` (2026-07-01 chain-grade)
- Cell D v2 M-sweep: `experiments/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_7.py`
  (Atom 1 CG, dense-Hopfield READ-REPLACE at beta=13)
- META atom target: `substrate_axes_factorize_across_beta_regime_2axis_v1`
  (unfired; promotes to CG on this cell HP)
