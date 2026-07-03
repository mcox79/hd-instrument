# Pre-reg: substrate_spoke3_hippocampal_encoder_bipolar_vs_gaussian_filler_smoke (2026-07-03)

## Anchor name
`substrate_spoke3_hippocampal_encoder_bipolar_vs_gaussian_filler_smoke_2026_07_03`

## Cell file
`experiments/exp_substrate_spoke3_hippocampal_encoder_bipolar_vs_gaussian_filler_smoke_2026-07-03.py`

## Purpose (revival criterion for Skunkworks MM_TENTATIVE)
Tests whether the prior Skunkworks Gaussian-JL analytical prediction (baseline
cosine degrades at cluster_cos~0.90 with dim-zero partial cue) holds under
Gaussian filler geometry after having FAILED at bipolar geometry in Cell 4
(commit 1350c7789). Bipolar+dim-zero produces DETERMINISTIC bit-identity signal
channel; Gaussian filler introduces continuous variance and should activate
the Gaussian-JL assumption bed the analytical model was built on.

If the prediction VALIDATES at Gaussian: analytical model is scope-refined
(Gaussian-JL only; not bipolar-adjacent geometries). W2 discriminative-regime
path opens with a filler-geometry qualifier.

If the prediction ALSO FAILS at Gaussian: analytical model has deeper limitation;
W2 discriminative-regime path may be unreachable with THIS primitive at any
bipolar-adjacent cluster-cos-0.90 geometry.

## Task class
SAME as Cell 4 discriminative-regime cell (episodic-binding + partial-cue
retrieval; N=500 pairs; adversarial cluster-shared codebook; 75% dim-zero
partial-cue corruption). ONLY the filler geometry changes.

## Filler geometry sweep (2 regimes)

### Regime A - BIPOLAR (Cell 4 reproduction; code-integrity gate)
- Fillers: {-1, +1} bipolar random with adversarial cluster structure
- flip_frac = 0.026 -> within-cluster filler cos_theoretical =
  (1 - 2*0.026)^2 = 0.900 (matches Director target cluster_cos~0.90)
- Signal channel at 75% dim-zero cue: bit-identity deterministic

### Regime B - GAUSSIAN REAL (Skunkworks Gaussian-JL prediction test)
- Fillers: Gaussian real-valued, per-dim ~ N(0, 1) with cluster mixing
- Cluster geometry: anchor_filler ~ N(0, 1); member = sqrt(rho) * anchor +
  sqrt(1 - rho) * per_member_noise; rho = 0.90 -> theoretical cluster_cos =
  rho = 0.90 (matches Regime A target within tolerance)
- Signal channel at 75% dim-zero cue: continuous Gaussian variance
  (NOT deterministic bit-identity)

Both geometries: role_key SHARED within cluster (bipolar in both, per
convention that binding role * filler produces the episode). Only FILLER
geometry differs; role_key remains bipolar so that role_key * filler in the
Gaussian regime is still a well-defined per-dim scaled Gaussian.

## Arms (4 arm-templates x 2 geometries x 3 seeds = 24 units)

| Arm | Encoder kind | Geometry | Role |
| --- | --- | --- | --- |
| `ARM_HIPPO_BIPOLAR` | hippocampal | bipolar | LOAD_BEARING (regression; HP4) |
| `ARM_HIPPO_DG_ONLY_BIPOLAR` | dg_only | bipolar | ablation |
| `ARM_COSINE_BASELINE_BIPOLAR` | cosine | bipolar | REGRESSION (HP4: r@1 = 1.000) |
| `ARM_RANDOM_BASELINE_BIPOLAR` | random | bipolar | chance floor |
| `ARM_HIPPO_GAUSSIAN` | hippocampal | gaussian | LOAD_BEARING (HP2, HP3) |
| `ARM_HIPPO_DG_ONLY_GAUSSIAN` | dg_only | gaussian | ablation |
| `ARM_COSINE_BASELINE_GAUSSIAN` | cosine | gaussian | LOAD_BEARING (HP1) |
| `ARM_RANDOM_BASELINE_GAUSSIAN` | random | gaussian | chance floor |

Director spawn prompt says "5 arms x 2 regimes x 3 seeds = 30 units";
authored as 4 arm-templates (cardinality-clean 24 units). Deviation flagged
to caller; happy to expand to 5 templates on re-spawn (e.g. add N=800 or
50-corrupt sensitivity if wanted).

Config constants:
- `N_DIM = 2048`, `DG_DIM = 8192`, `DG_SPARSITY = 0.02` (T-F capacity ~1047)
- `N_PAIRS = 500` (~48% of C_TF)
- `CORRUPTION = 0.75`
- `CLUSTER_SIZE = 5`
- `FLIP_FRAC_BIPOLAR = 0.026`, `GAUSSIAN_CLUSTER_RHO = 0.90`
- `SEEDS = [11, 17, 23]`

## HP band (LOAD_BEARING)

| Gate | Definition | Interpretation if fires |
| --- | --- | --- |
| HP1 | `ARM_COSINE_BASELINE_GAUSSIAN` r@1 mean <= 0.90 | Baseline degrades at Gaussian; Skunkworks Gaussian-JL prediction VALIDATED |
| HP2 | `ARM_HIPPO_GAUSSIAN` r@1 mean >= 0.60 | Mechanism fires at Gaussian regime |
| HP3 | `ARM_HIPPO_GAUSSIAN` - `ARM_COSINE_BASELINE_GAUSSIAN` r@1 delta >= 0.10 | Missing discriminative-regime WIN witness for W2 (mechanism separates from baseline at Gaussian) |
| HP4 | `ARM_COSINE_BASELINE_BIPOLAR` r@1 mean >= 0.99 (band tolerance for 3-seed mean) | Regression: bipolar bit-identity determinism reproduces Cell 4 |

Verdict tiers:
- HARD_PASS: HP1 AND HP2 AND HP3 AND HP4 (Gaussian-JL prediction validated + W2 witness + code integrity)
- HARD_FAIL_COSINE_STILL_SATURATES_AT_GAUSSIAN: HP1 fails (COSINE_GAUSSIAN r@1 > 0.90); Skunkworks Gaussian-JL prediction ALSO fails at Gaussian
- HARD_FAIL_HIPPO_BROKEN_EVERYWHERE: HP2 fails (HIPPO_GAUSSIAN < 0.60) AND HIPPO_BIPOLAR also below 0.60 -> mechanism has scale/regime issue not filler-geometry-diagnosable
- HARD_FAIL_REGRESSION_BROKEN: HP4 fails -> code drift from Cell 4; downstream Gaussian verdict UNRELIABLE
- MIDDLE_BAND: some HP fires but not all (e.g. HP1 fires but HP3 doesn't -> baseline degrades but mechanism doesn't win)

## Envelope FAIL bands (explicit)
- HF-baseline: `ARM_RANDOM_BASELINE_*` r@1 > 0.010 (5x chance at N=500) -> retrieval implementation bug
- HF-dg-rate: HIPPO arm dg_sparse_rate outside [0.008, 0.040] -> DGProjection top-K broken
- HF-card: `actual_n_units < 24` -> cardinality breach META_RULE_H

## Compute architecture
- Class: (b) sequential-CPU with justification
- Justification: per-arm numpy operations at N=500 pairs x N_DIM=2048 (arm wall
  ~1-2s in Cell 4). Total wall time budget ~60-120s for 24 units. Below 10s
  per-phase-point wall-time sanity threshold for batching mandate; sequential
  CPU acceptable per §GPU-batching rule.
- Storage strategy: no_storage (this cell tests single-hop encoding+retrieval;
  no downstream composition. Marks `no_composition` per Skunkworks storage
  strategy declaration META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW).

## SCHEMA-VET checklist
- `sweep_alignment_verdict: ALIGNED` - filler_geometry axis sweep aligns with
  what each arm's encoder experiences (COSINE encoder sees filler dims
  directly; HIPPO encoder sees them through DG expansion; both experience the
  filler-geometry change 1:1).
- `discriminating_fraction`: predicted 4/4 arm-configs in discriminating band
  [0.10, 0.90] at GAUSSIAN regime; BIPOLAR regime intentionally saturated
  (regression sanity, code-integrity gate). Overall 1.00 predicted in band
  including bipolar-saturated-COSINE=regression.
- `composition_edges`: none (single-hop cell).
- `positive_control_arms`: `ARM_COSINE_BASELINE_BIPOLAR` reproduces Cell 4
  MEASURED r@1 = 1.000; `ARM_HIPPO_BIPOLAR` reproduces Cell 4 MEASURED
  r@1 = 0.978 tolerance 0.10.
- `functional_requirements`: single functional requirement = "one-shot
  episodic binding of role_key * filler with partial-cue retrieval"; primitive
  = `HippocampalEncoder` (DG expansion + CA3 Marr-style completion).
- `arms_differ_verified: bool` (set by smoke gate; regression arm hash exempt
  since BIPOLAR arms share input episodes across cross-geometry arm-family).
- `final_metrics_atomicity: tmp_replace`
- `crlb_n/a`: this is a saturation/degradation test not a CRLB-bounded
  discriminator (no fixed noise floor formula; empirical is the object).
- `baseline_in_band` at smoke (RANDOM r@1 in [0.001, 0.010] band).
- `cardinality_ok`: `expected_n_units = 4 arms x 2 geometries x 3 seeds = 24`.
- `cell_chunked: false` (small-N cell; single-file 3-seed loop with per-seed
  checkpoint via `_seed_checkpoint.py` helper).
- `start_marker_written: true`, `crash_diagnostic_present: true`,
  `heartbeat_present: true`.
- `progress_logging: print_flush_true` + line_buffered_stdout.
- `calibration_check: default_ok_for_this_regime` - all defaults match Cell 4
  MEASURED regime except flip_frac (0.10 -> 0.026 targeting cluster_cos 0.90).

## Cardinality
`EXPECTED_N_UNITS = len(SEEDS) * len(ARM_SPECS) = 3 * 8 = 24`.
Verdict enforces via `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if
`actual_n_units < 24`.

## Selftests (7)
1. `arg_parse_default_is_smoke`
2. `corrupt_cue_correct_fractions` (0.75)
3. `bipolar_within_cluster_cos_hits_0_90` (flip_frac=0.026 -> obs_cos in [0.85, 0.95])
4. `gaussian_within_cluster_cos_hits_0_90` (rho=0.90 -> obs_cos in [0.85, 0.95])
5. `arms_differ_hash_micro` (HIPPO vs DG_ONLY vs COSINE queries differ)
6. `regression_arm_bit_identical` (BIPOLAR N=500 75% HIPPO r@1 within tolerance
   of Cell 4 MEASURED 0.978 at Cell 4 flip_frac=0.10; but this cell uses
   flip_frac=0.026 so tolerance widened to [0.85, 1.00])
7. `primitive_selftests_chain` (`python -m hdlab.hippocampal_encoder --self-test`)

## Regime dispatch
- SMOKE-only. USER-locked SMOKE-only-on-local_cpu.
- `local_cpu_queue`, `--timeout 900s`.
- HOLD before any FULL dispatch pending USER review of verdict.

## Framing discipline (LOAD-BEARING)
- SUBSTRATE KNOWS ALMOST NOTHING. MECHANISM probe on SUPERVISED synthetic
  episodic-binding regime. NOT a general-knowledge or language claim.
- PRIOR SKUNKWORKS ANALYTICAL FAILED at bipolar (Cell 4 empirical proved
  this; commit 1350c7789 landed HARD_FAIL_NO_MECHANISM_SEPARATION at
  BIPOLAR flip_frac=0.10). This cell tests the COUNTERFACTUAL Gaussian
  regime.
- If Gaussian-JL prediction VALIDATES: analytical model scope-refined
  (Gaussian-JL assumption applies to Gaussian fillers only, not bipolar-
  adjacent geometries); W2 discriminative-regime path opens with
  filler-geometry qualifier.
- If Gaussian-JL prediction ALSO FAILS: model has deeper limitation; W2
  discriminative-regime may not be achievable with this primitive at any
  cluster_cos-0.90 geometry.
- No sigma claims without formula + filler-geometry annotation.
- Anti-personification: substrate operates on integer indices + real-valued
  vectors; no narrative labels.

## Ancestors / linked artifacts
- Cell 4 pre-reg: `preregs/2026-07-03_substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke.md`
- Cell 4 landed metrics: `data/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke_2026_07_03/metrics.json` (commit 1350c7789)
- Director analytical calibration note: `notes/director_analytical_calibration_note_gaussian_JL_vs_bipolar_determinism_2026-07-03.md` (commit 7214cb82e)
