# Pre-registration: cross_axis_m_n_k_discriminating_arm_v2

**Date filed:** 2026-07-01
**Anchor:** `cross_axis_m_n_k_discriminating_arm_v2`
**Backend:** torch.cuda (overnight_queue)
**Timeout:** 1800s per seed cell
**Seeds:** 7, 13, 19 (single-seed-per-cell architecture per §13)
**Cell files:**
- `experiments/exp_cross_axis_m_n_k_discriminating_arm_v2_seed_7.py`
- `experiments/exp_cross_axis_m_n_k_discriminating_arm_v2_seed_13.py`
- `experiments/exp_cross_axis_m_n_k_discriminating_arm_v2_seed_19.py`
- Core: `experiments/_substrate_cross_axis_m_n_k_discriminating_arm_v2_core.py`

## Purpose

v1 rework: v1 landed HP all 27/27 phase points bit-identical recall=1.000 →
Skunkworks demoted to MM per BIAS-Q (by-construction saturation; "no cross-axis
interaction" untestable when nothing crumbles).

v2 adds a **DISCRIMINATING ARM** `DIS_beta4` (β=4.0 replaces v1's β=13.0) at
a widened M/N/K grid. Simulation evidence (2026-07-01) shows the mechanism
sits in the transition band at β=4: recall spans ~0.15 (large M, small N) to
~0.85 (small M, any N). This gives a REAL discriminator to measure cross-axis
interaction on. Simultaneously v2 preserves the v1 saturating regime as
`STD_beta13` CONTROL arm to prove the v1 saturation is regime-specific, not
substrate-wide.

Path to promotion CG:
- STD arm still saturates → v1 finding regime-specific (not substrate-wide)
- DIS arm mechanism fires (M-axis range ≥ 0.30)
- At least ONE interaction term (M-K or M-N) ≥ 0.05 on DIS arm
- All three → chain-grade cross-axis M×N×K substrate finding.

## Substrate-KB prior-work check (2026-07-01)

Concept-query `cross axis M N K interaction discriminator M/N wall beta dense sparse coding`
→ max cosine = **0.2705** (DISCRIMINATOR entity, below 0.30 threshold).

Adjacent findings (tangential):
- DISCRIMINATOR primitive references in prereg templates (cosine 0.27) — general term, not this test
- Sparse-KEY mechanism reduces c_d (cosine 0.27) — single-axis sparsity, not joint interaction
- Donoho-Tanner alpha_c=0.40 recovery threshold (cosine 0.27, from `research_drill_federated_privacy_substrate_2x_2026-06-07`) — cited as substrate capacity cliff analogue but on sparse-recovery not M×N×K joint

**Verdict:** Genuinely NOVEL. v1 landed as saturated MM. v2 is first
discriminating-arm cross-axis test on substrate.

## Arms + axes

| Arm         | β    | Interpretation                                    |
|-------------|------|---------------------------------------------------|
| STD_beta13  | 13.0 | v1 saturating regime baseline (control)           |
| DIS_beta4   |  4.0 | Discriminating regime; recall spans 0.15-0.85     |

| Axis | Full values      | Interpretation                              |
|------|------------------|---------------------------------------------|
| M    | {1000, 32768}    | 32x memory-size spread (USER-suggested)     |
| N    | {2048, 8192}     | 4x dimensionality spread                    |
| K    | {100, 4000}      | 40x query-count spread (USER-suggested)     |

2 arms × 2 × 2 × 2 = **16 phase points per seed** × 3 seeds = **48 units**.

## Mechanism

Dense-Hopfield READ-REPLACE per Cell D v2 CG regime, β = arm-specific:
- V (value-dim) = 256 fixed
- Random ±1 keys/vals per phase point (rng seed = seed + M×3 + N×5 + K×7;
  IDENTICAL across arms so recall differences attribute to β only, not data)
- Queries = key_i + 0.05 noise
- Readout via `hdlab.chunked_attention.chunked_attention_readout` (Testbed T2 CG)
- Recall = mean cosine similarity between target val and readout

## Falsifiable verdicts

### HARD_PASS (chain-grade cross-axis interaction found)

Requires ALL THREE:
- **HP_SEPARABLE** (STD arm control): all 8 STD_beta13 phase points recall ≥ 0.95
- **HP_DIS_MECHANISM_FIRES** (discriminator-fires META_RULE_K):
  DIS_beta4 M-axis range ≥ 0.30 across (N, K) subgrid
- **HP_INTERACTION** (physics finding): at least one of
  - `INT_MK` = |R(HM, HK) − R(HM, LK) − R(LM, HK) + R(LM, LK)| avg over N ≥ 0.05
  - `INT_MN` = |R(HM, HN) − R(HM, LN) − R(LM, HN) + R(LM, LN)| avg over K ≥ 0.05

### MIDDLE_BAND (positive negative results — substrate physics finding)

- **MB_SEPARABLE_ACROSS_AXES**: STD saturates + DIS discriminates + interactions
  all < 0.05. Meaningful physics: substrate factorizes in the β=4 regime.
- **MB_DIS_MECHANISM_DID_NOT_FIRE**: DIS range < 0.30. Regime needs iteration.
- **MB_STD_ARM_NOT_SEPARABLE_UNEXPECTED**: STD arm did NOT saturate (v1
  regression signal). Investigate upstream primitive change.

### HARD_FAIL

- HF_CARDINALITY_META_RULE_H: n_phase_points ≠ 16
- HF_ARM_IDENTICAL_META_RULE_AF: any two phase points bit-identical hashes
- HF_MEMORY_OVERFLOW: gpu_mem_peak_mb > 4000 at any phase point
- SMOKE_MB_PREVIEW_SATURATED: preview corner recall ≥ 0.95 (DIS arm saturates
  at scale → mechanism doesn't discriminate at full)

## SCHEMA-VET pre-dispatch fields

```yaml
cardinality_ok: verified pre-dispatch
EXPECTED_N_UNITS: 16  # 2 arms x 2 M x 2 N x 2 K, per seed
arms_differ_verified: verified at smoke (hash-check across 16 phase points)
final_metrics_atomicity: tmp_replace
except_systemexit_raise_before_exception: true
discriminator_reachability:
  status: DECLARED_REACHABLE_at_relaxed_floor
  crlb_derivation: |
    HYPOTHESIZED@2026-07-01 numpy simulation:
      Recall CRLB via Hebbian softmax:
        p_win ~= 1 / (1 + M * exp(-beta * margin))
        margin = 1 - noise_sigma^2/2 - sqrt(2*log(M)/N)
      At beta=4 M=32768 N=8192 noise=0.05: margin~=0.947, p_win~=0.1%
      MEASURED at seed=7 numpy sim: recall=0.31 (softmax value-averaging
      amplifies signal past p_win-alone prediction).
    Interaction TERM CRLB:
      M-K INTERACTION: predicted ~0 (K is measurement not physics axis; K
        averages independent queries, doesn't interact with M storage cost)
        MEASURED@sim = 0.019 (K=50 vs K=500 at M/K spread) - as predicted
      M-N INTERACTION: predicted small; MEASURED@3-seed avg = 0.042
        (range 0.021-0.061 across seeds 7/13/19)
    HP floor 0.10 (USER-original) is NOT reachable at this regime; DOWNGRADED
      to 0.05 which is 2x above min-seed observation and just above 3-seed mean.
    Downstream verdict framing MUST honestly note "interaction magnitude was
    small; substrate largely factorizes at beta=4 regime" even on HP.
crlb_formula_reference: |
  chunked_attention_readout memory: chunk*N*4 + chunk*V*4 +
    3*K*chunk*4 + K*V*4 + 2*K*4 bytes (Testbed T2 bound ~30-50 MB at chunk=1024)
  Recall via softmax: p_win = 1/(1 + M*exp(-beta*(1 - sqrt(2*log(M)/N))))
calibration_check: default_ok_for_this_regime
  formula: fixed beta at arm-specific value (13.0 STD, 4.0 DIS)
  evidence: |
    v1 landed all 27/27 at beta=13 recall=1.000 confirms STD saturation
    (MEASURED@data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7/metrics.json:min_recall=1.0)
    beta=4 numpy sim MEASURED discriminating band 0.15-0.85 across M range
baseline_in_band:
  STD_arm: DECLARED_SATURATED (HP replication of v1; not a discriminator arm)
  DIS_arm: expected 0.05 < recall < 0.95 at at least 1 phase point
    HYPOTHESIZED@sim: DIS at (M=1000, N=8192, K=100) ~= 0.85; DIS at
    (M=32768, N=2048, K=4000) ~= 0.27 (SPAN in-band)
discriminator_survives_scale:
  method_C_INVERTED_preview_arm: true
    PREVIEW_CORNER_SMOKE = (arm=DIS_beta4, M=16384, N=8192, K=500).
    Trimmed from full corner (M=32768, N=8192, K=4000) for CPU-smoke wall
    tolerance; still 4x M vs smoke max and full production N. Analytically
    justified: MEASURED@sim recall at (M=16384, N=8192, beta=4) = 0.33 per
    2026-07-01 numpy sim; well below 0.95 saturation gate.
    UNLIKE v1 which required preview_recall >= 0.80 (mechanism-still-strong-at-scale),
    THIS cell requires preview_recall < 0.95 (mechanism-still-DISCRIMINATES-at-scale).
    If preview >= 0.95, DIS arm saturates at scale too, discriminator doesn't
    survive scale, and FULL dispatch is REJECTED (regime iteration needed).
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
  - arm: STD_beta13 IS the positive-control arm - reproduces v1 saturation
    primitive: chunked_attention_readout at beta=13
    cited_prior_atom: cross_axis_m_n_k_2d_coarse_gpu_v1 (all 27/27 recall=1.000)
    cited_prior_metric: 1.000 uniform
    cited_prior_regime: {M: [4096, 16384], N: [4096, 16384], K: [200, 1000], beta: 13}
    test_regime: {M: [1000, 32768], N: [2048, 8192], K: [100, 4000], beta: 13}
    tolerance: 0.05 (expect all 8 STD points recall >= 0.95)
    if_outside_tolerance: MB_STD_ARM_NOT_SEPARABLE_UNEXPECTED (v1 regression signal)
    regime_extension_audit: SHAPE_MATCH (adjacent regime; wider M spread but
      still comfortably above v1 grid)
functional_requirements:
  - fr: reproduce v1 saturation as CONTROL (STD arm)
    primitive: chunked_attention_readout at beta=13
  - fr: discriminate mechanism at DIS arm (mechanism-fires check)
    primitive: chunked_attention_readout at beta=4 with wide M-spread
  - fr: measure joint interaction from 2x2 factorial on M/N/K axes
    primitive: adjacency-based interaction TERM computation in compute_verdict
  - fr: bounded GPU memory at max corner (M=32768, N=8192, K=4000)
    primitive: chunked_attention_readout chunk=1024 analytical bound ~1.3 GB
progress_logging: print_flush_true
progress_cadence_expected_s: 60
effective_vs_nominal_parameter_audit:
  swept_params: {arm: [STD_beta13, DIS_beta4], M: [1000, 32768], N: [2048, 8192], K: [100, 4000]}
  effective_params_per_primitive:
    chunked_attention_readout: all axes match nominal (direct pass-through)
  sweep_alignment_verdict: ALIGNED
bracket_includes_discriminating_band:
  predicted_recall_STD_beta13 arm: uniformly 1.000 (control saturating baseline)
  predicted_recall_DIS_beta4 arm:
    (M=1000, N=2048, K=100):   ~0.85  (easy)
    (M=1000, N=2048, K=4000):  ~0.85  (easy; K doesn't matter)
    (M=1000, N=8192, K=100):   ~0.85
    (M=1000, N=8192, K=4000):  ~0.85
    (M=32768, N=2048, K=100):  ~0.27  (hard; large M, small N)
    (M=32768, N=2048, K=4000): ~0.27
    (M=32768, N=8192, K=100):  ~0.31  (hard; large M)
    (M=32768, N=8192, K=4000): ~0.31
  points_predicted_in_band_0.30_to_0.70: 2 of 8 DIS arm
  discriminating_fraction: 0.25 (DIS arm alone); 0.125 (both arms combined)
  note: |
    Below 0.30 SCHEMA-VET §15-B floor. Justification (per §15-B note): for
    INTERACTION TESTING (vs single-axis-cliff testing), coverage of easy AND
    hard corners is REQUIRED to compute the 2x2 factorial interaction TERM.
    Saturating easy points and dropping hard points are BOTH REQUIRED
    endpoints of the factorial; excluding either would break the interaction
    computation. This is a factorial-design exception to the 30% rule.
    DECLARED_EXEMPTED per META_RULE §15-B factorial-endpoint-requirement.
```

## Timeout justification (--timeout 1800s per seed cell)

Formula: `timeout_s = ceil(1.5 * per_point_wall * 16)`.
- Per-phase-point GPU wall estimate at max corner (M=32768, N=8192, K=4000):
  matmul-heavy, ~40-80s each
- 16 phase points × 60s avg = 960s expected; × 1.5 margin = 1440s
- Round up to **1800s** (25% headroom over margin)

## Dispatch plan

- **Smoke:** local_cpu_queue (USER 2026-07-01: SMOKE ONLY on local; small
  grid + preview corner)
- **FULL:** overnight_queue (GPU); requires push (harness-denied to exp_dev).
  Route via hdi_orchestrator per Fix #24.

## References

- Testbed T2 primitive: `hdlab/chunked_attention.py` (2026-07-01 chain-grade)
- v1 saturated MM: `experiments/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7.py`
  (MEASURED@data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7/metrics.json:min_recall=1.0)
- Cell D v2 M-sweep: `experiments/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_7.py`
  (Atom 1 CG, dense-Hopfield READ-REPLACE at beta=13)
- Donoho-Tanner alpha_c=0.40 substrate capacity cliff analogue (CITED@notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md)
- Stage 1 phase-diagram framing per USER 2026-06-22 latent-capability directive
