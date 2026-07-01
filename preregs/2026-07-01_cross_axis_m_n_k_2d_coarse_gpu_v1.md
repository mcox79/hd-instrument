# Pre-registration: cross_axis_m_n_k_2d_coarse_gpu_v1

**Date filed:** 2026-07-01
**Anchor:** `cross_axis_m_n_k_2d_coarse_gpu_v1`
**Backend:** torch.cuda (overnight_queue)
**Timeout:** 3600s per seed cell
**Seeds:** 7, 13, 19 (single-seed-per-cell architecture per §13)
**Cell files:**
- `experiments/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7.py`
- `experiments/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_13.py`
- `experiments/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_19.py`
- Core: `experiments/_substrate_cross_axis_m_n_k_2d_coarse_gpu_v1_core.py`

## Purpose

First joint (M, N, K) cross-axis interaction test. Prior single-axis M sweep,
N sweep, K sweep all reached CG independently but joint (M, N, K) interactions
untested. Closes Stage 1 phase-diagram gap: is dense-Hopfield READ-REPLACE
recall SEPARABLE across M/N/K, or is there a joint capacity regime where
mechanism collapses despite adjacent single-axis points holding?

Substrate physics finding if joint interaction found: informs commercial
deployment (M/N/K corner-case constraints).

## Substrate-KB prior-work check (2026-07-01)

Concept-query `cross axis M N K joint interaction 2D grid capacity phase diagram`
returned max cosine=0.30 (below directional threshold). Adjacent findings:

- Cap-int integration (cosine 0.30) CITED@notes/research_to_exp_dev_CONCEPTNET_acquisition
- Phase Diagram Context (cosine 0.28) CITED@preregs/2026-05-29_phase_region_cd_n4096.md
- N_DIM phase diagram v1 (cosine 0.27) CITED@notes/exp_dev_to_orchestrator_substrate_stage1_integration
- Joint sweep 2D drill (cosine 0.27) CITED@notes/research_drill_capacity_codebook_vs_envelope

**Verdict:** Genuinely NOVEL joint cross-axis test. Prior work is single-axis
or CD-slice only. Rediscovery risk LOW.

## Axes

| Axis | Full values          | Interpretation                                    |
|------|----------------------|---------------------------------------------------|
| M    | {4096, 8192, 16384}  | Number of stored key/val patterns (memory size)   |
| N    | {4096, 8192, 16384}  | Vector dimensionality (both keys and queries)     |
| K    | {200, 500, 1000}     | Number of queries drawn per phase point (probe K) |

3 x 3 x 3 = **27 phase points** per seed x 3 seeds = **81 units total**.

## Mechanism

Dense-Hopfield READ-REPLACE per Cell D v2 CG regime:
- beta = 13.0 (fixed base; no adaptive scaling in this coarse map)
- V (value-dim) = 256 fixed
- Random +/-1 keys and vals per phase point (rng seed = seed + M*3 + N*5 + K*7)
- Queries = key_i + 0.05 noise (K queries per point)
- Readout via `hdlab.chunked_attention.chunked_attention_readout` (Testbed T2 CG)
- Recall metric: mean cosine similarity between target val and readout, over K queries

## Falsifiable verdicts

### HARD_PASS (chain-grade separability)

- **HP_ALL_HOLD** (CHAIN_GRADE_NO_INTERACTION): recall >= 0.70 at ALL 27 phase points
  - Interpretation: mechanism is SEPARABLE across M/N/K axes; single-axis sweeps
    generalize to joint config
  - HYPOTHESIZED@this cell: floor 0.70 chosen conservatively; Cell D v2 CG at
    similar M/N regime measured recall > 0.90; 0.70 gives margin for coarse-K=200
    corner (fewer queries -> higher noise floor)

### MIDDLE_BAND (interaction characterized OR band-hugging)

- **MEASURED_MECHANISM_INTERACTION_MAPPED**: some phase point recall < 0.40 AND
  that point is ADJACENT (differs in exactly 1 axis) to a HP point.
  Interpretation: JOINT interaction found; substrate physics finding
- **MB (no clean pattern)**: some HP, some in intermediate band, but no adjacent
  HF-HP pairs

### HARD_FAIL

- **HF_INTERACTION_FOUND** (design gate; interaction is a MB not HF outcome since
  it's a POSITIVE finding). This gate reserved for pure-instrumentation failures:
- HF_CARDINALITY_META_RULE_H: n_phase_points != 27
- HF_ARM_IDENTICAL_META_RULE_AF: any two phase points bit-identical hashes
- HF_MEMORY_OVERFLOW: gpu_mem_peak_mb > 4000 at any phase point (chunk=1024 bound
  ~1.2 GB analytical; 4 GB gives 3x margin)
- Mechanism death at smoke: min_recall < 0.10 in smoke grid

## SCHEMA-VET pre-dispatch fields

```yaml
cardinality_ok: pre-verified pre-dispatch
EXPECTED_N_UNITS: 27  # 3 M x 3 N x 3 K, per seed
arms_differ_verified: verified at smoke (hash-check across 27 phase points)
final_metrics_atomicity: tmp_replace
except_systemexit_raise_before_exception: true (no BaseException catch)
discriminator_reachability: true
  crlb_note: |
    Recall THEORETICAL@Hebbian superposition: recall = f(M, N, K, beta) with
    baseline noise sqrt(M/N) as key-key overlap floor. At worst corner
    M=16384, N=4096: sqrt(M/N)=2.0; beta=13 with softmax winner-take-most
    should still concentrate on correct key at recall > 0.7 unless joint
    interaction kicks in. Discriminator reachable analytically.
crlb_formula_reference: |
  chunked_attention_readout memory: chunk*N*4 + chunk*V*4 +
    3*K*chunk*4 + K*V*4 + 2*K*4 bytes; Testbed T2 bound ~10-30 MB at chunk=1024
  Recall floor: baseline max_distractor = sqrt(2*log(M)/N); p_win = 1/(1 + M*exp(-beta*(1-max_distractor)))
calibration_check: default_ok_for_this_regime
  formula: fixed beta=13 per Cell D v2 CG at M in [4096, 16384] N in [4096, 16384]
  evidence: Cell D v2 CG (Atom 1) HARD_PASS at those regimes with beta=13
baseline_in_band:
  DECLARED_EXEMPTED: single-arm phase-diagram map cell.
    No baseline arm designed; this cell measures mechanism only across the (M,N,K)
    grid to detect joint interactions. Per META_RULE_AG the exemption criterion
    is single-arm cells with no discriminator gate against a baseline; HP/HF
    bands here are absolute recall thresholds not gap thresholds.
discriminator_survives_scale:
  method_C_preview_arm_at_full_N_in_smoke: true
    Smoke runs a preview phase point at PREVIEW_CORNER_SMOKE = (M=16384, N=16384, K=200)
    with FULL chunk_size = 1024. If preview_corner_recall < 0.80 in smoke,
    smoke returns MIDDLE_BAND and FULL dispatch is REJECTED. This ensures the
    discriminator (HP=0.70) is reachable at the worst-case corner before
    committing GPU-hours.
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
  - arm: chunked_attention_readout at (M=4096, N=4096, K=200) reproduces Cell D v2 CG
    primitive: chunked_attention_readout
    cited_prior_atom: Cell D v2 dense-Hopfield READ-REPLACE (Atom 1)
    cited_prior_metric: recall >= 0.90 at similar regime with beta=13
    cited_prior_regime: {M: ~10k, N: 8192, beta: 13, V: 256}
    test_regime: {M: 4096, N: 4096, beta: 13, V: 256}
    tolerance: 0.20 (K=200 vs prior K, and lower N/M product introduces some drift)
    if_outside_tolerance: MEASURED_MECHANISM_REGIME_DRIFT (do not overclaim CG)
    regime_extension_audit: SHAPE_MATCH (same primitive; adjacent regime)
functional_requirements:
  - fr: dense-Hopfield recall at joint (M, N, K) configs
    primitive: chunked_attention_readout (T2 CG)
  - fr: detect joint capacity interaction (if any) across M/N/K
    primitive: adjacency-based verdict logic in compute_verdict
  - fr: bounded GPU memory at max corner (M=N=16384, K=1000)
    primitive: chunked_attention_readout chunk=1024 analytical bound ~1.2 GB
progress_logging: print_flush_true
progress_cadence_expected_s: 60
effective_vs_nominal_parameter_audit:
  swept_params: {M: [4096,8192,16384], N: [4096,8192,16384], K: [200,500,1000]}
  effective_params_per_primitive:
    chunked_attention_readout: M (keys), N (dim), K (queries) - ALL nominal
      match effective (direct pass-through; no partition or oracle indirection)
  sweep_alignment_verdict: ALIGNED
bracket_includes_discriminating_band:
  predicted_recall_per_corner:
    M4096_N16384_K200: ~0.95 (easy: N/M=4; low query count)
    M16384_N4096_K1000: ~0.55 (hard: N/M=0.25; superposition interference)
    M16384_N16384_K1000: ~0.85 (mid: N/M=1; balanced)
  points_predicted_in_band_0.30_to_0.70: ~6-9 of 27
  points_predicted_saturated_above_0.90: ~8-12 of 27
  discriminating_fraction: 0.22-0.33 (near threshold; interaction test requires
    coverage of all corners including easy + hard to establish separability, not
    just discriminating-band coverage)
  note: For interaction TESTING (vs single-axis-cliff testing), coverage of easy
    AND hard corners is REQUIRED to establish separability. Saturating easy points
    is NOT a design flaw; they anchor the HP baseline for interaction detection.
```

## Timeout justification (--timeout 3600s per seed cell)

Formula: `timeout_s = ceil(1.5 * smoke_wall_s * scale_factor)`.
- Smoke wall estimate: ~60-120s (small grid on CPU + one FULL_N preview)
- FULL 27 phase points at avg ~50-100s each on GPU (upper bound at M=N=16384)
- Total FULL cell wall estimate: ~1500-2700s worst case
- 3600s timeout gives 25% headroom over worst-case estimate

## Dispatch plan

- **Smoke:** local_cpu_queue (USER 2026-07-01: SMOKE ONLY on local; laptop-preserving)
- **FULL:** overnight_queue (GPU); requires push (harness-denied to exp_dev).
  Route via hdi_orchestrator per Fix #24 GPU dispatch rules.

## References

- Testbed T2 primitive: `hdlab/chunked_attention.py` (2026-07-01 chain-grade)
- Cell D v2 M-sweep: `experiments/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_7.py`
  (Atom 1 CG, MEASURED@data/exp_cortex_hippo_dense_layer_M_sweep_v3/metrics.json)
- N-sweep amend CG (Atom family)
- Stage 1 phase-diagram framing per USER 2026-06-22 latent-capability directive
