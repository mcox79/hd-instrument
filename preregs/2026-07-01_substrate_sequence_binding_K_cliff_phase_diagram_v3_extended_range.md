# Pre-registration: substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range

**Filed:** 2026-07-01 (hdi_exp_dev spawn)
**Predecessor:** `preregs/2026-06-28_substrate_sequence_binding_K_cliff_phase_diagram_full_v2.md`
**Skunkworks trigger:** e5f50e02 (Option A recommendation — extend K range above current cliff)
**Task class:** Stage 1 phase-diagram MM -> CG lift; escape META_RULE_Q saturation
**Dispatch queue:** remote_cpu_queue (numpy; CPU-eligible per PROT-020)

## 1. Predecessor state (v2 landed 3-seed)

v2 grid: K={20,50,100,200,500,1000} x N={2048,4096,8192,16384} x Q={1,2,4} = 72 pts/seed.

Per-seed band distribution (MEASURED@d:/AI/hd-instrument/data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_{7,13,19}/metrics.json):

- seed_7:  SAT=43, MB=10, FLOOR=7, TRANS=12 (MIDDLE_BAND)
- seed_13: SAT=43, MB=7,  FLOOR=6, TRANS=16 (MIDDLE_BAND)
- seed_19: SAT=42, MB=10, FLOOR=6, TRANS=14 (MIDDLE_BAND)

Real bound on SAT cells: SUBSTRATE_top1=1.000. Saturation concentrated at K<=200 x N>=8192.
Cross-seed consistent (SAT variance = 1 point). n_MB well below HP_MIN_MB_POINTS=22 threshold.

## 2. v3 mechanism (Option A — extend K range)

Shift K axis UP:
- **DROP:** K={20, 50, 100} (universally SAT at N>=8192; contribute all SAT cells to n_SAT bloat)
- **KEEP:** K={200, 500, 1000} (spans SAT-boundary; K=1000 already MB/TRANS at N=16384)
- **ADD:** K={2000, 4000, 8000} (predicted to push N=16384 cells into MB/FLOOR)

Same axis cardinality (6 K x 4 N x 3 Q = 72 pts). Same arms / bands / HP gate as v2.

## 3. Analytical scale justification (DISCRIMINATOR-MUST-SURVIVE-SCALE — option B)

Plate/Kanerva HRR bundle recall SNR ~ sqrt(N/K) / sqrt(log V) THEORETICAL@sqrt-capacity.

v2 EMPIRICAL@d:/AI/hd-instrument/data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_7/metrics.json:summary_per_phase_point (for K=1000/N=16384/Q=1 -> 0.77; already TRANS/MB):

| K    | N=2048 | N=4096 | N=8192 | N=16384 | expected band       |
|------|--------|--------|--------|---------|---------------------|
| 200  | (0.49) | (0.85) | (1.00) | (1.00)  | v2 SAT-preserved    |
| 500  | (0.12) | (0.34) | (0.71) | (0.98)  | v2 mixed            |
| 1000 | (0.06) | (0.11) | (0.32) | (0.75)  | v2 mixed            |
| 2000 | ~0.03  | ~0.06  | ~0.15  | ~0.45   | HYPOTHESIZED FLOOR/MB |
| 4000 | ~0.02  | ~0.03  | ~0.07  | ~0.22   | HYPOTHESIZED FLOOR/TRANS |
| 8000 | ~0.01  | ~0.02  | ~0.04  | ~0.10   | HYPOTHESIZED deep FLOOR |

Extrapolation basis: v2 K=1000 mean recall halves ~each 2x-N step; K also halves ~each 2x-K step.
So K=8000/N=16384 predicted ~0.10 (deep FLOOR) — this is the DISCRIMINATOR-SURVIVES-SCALE preview.

Predicted band distribution at full v3:
- SAT (K=200,500 x N=16384, K=200 x N=8192): ~6-9 cells (satisfies HP_MIN_SAT_POINTS=6)
- MB [0.30, 0.70]: ~24-30 cells (satisfies HP_MIN_MB_POINTS=22)
- FLOOR: ~20-25 cells (satisfies HP_MIN_FLOOR_POINTS=6)
- TRANS: ~15-20 cells

## 4. Pre-reg fields (SCHEMA-VET)

```yaml
prereg_id: 2026-07-01_substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range
version: v3
anchor_prefix: substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range
seeds: [7, 13, 19]
cell_chunked: true
start_marker_written: true               # via _write_minimal_metrics STARTED phase
crash_diagnostic_present: true           # _write_import_crash_sentinel + outer try
heartbeat_present: false                 # single-seed runtime bounded; per-seed print
defensive_error_checking: passed_all_4_patterns

# CELL-TEMPLATE MANDATES
arms_differ_verified: true               # via SUBSTRATE / RANDOM / SHUFFLE distinct code paths
arms_differ_exempted: []
final_metrics_atomicity: tmp_replace     # os.replace(tmp, final)
run_mode_verified: true                  # HDLAB_RUN_MODE default 'full'; argparse --smoke/--self-test

# CRLB / capacity feasibility
crlb_n/a: "HRR bundle recall is bounded by capacity ratio N/K (Plate 1994) not by CRLB. Discriminator reachability verified via analytical SNR gradient in Section 3."
discriminator_reachability: true

# Baseline in band (META_RULE_AG)
baseline_in_band: true                   # RANDOM/SHUFFLE ~1/V ~1e-4; SUBSTRATE >>>
baseline_arms: [RANDOM, SHUFFLE]

# HP scope (META_RULE §5b)
HP_SCOPE:
  SUBSTRATE: [HP_MIN_MB_POINTS, HP_ARMS_DIFF_MIN, HP_MIN_SAT_POINTS, HP_MIN_FLOOR_POINTS, cardinality_ok]
  RANDOM: []                              # baseline arm; no HP gates apply
  SHUFFLE: []                             # baseline arm; no HP gates apply

# Cardinality (META_RULE_H)
cardinality_ok_required: true
EXPECTED_N_UNITS_FULL: 72                 # 6 K x 4 N x 3 Q
EXPECTED_N_UNITS_SMOKE: 6                 # smoke corners
EXPECTED_N_RECORDS_FULL: 21600            # 72 x 3 arms x 100 queries
EXPECTED_N_RECORDS_SMOKE: 72              # 6 x 3 x 4

# Calibration (META_RULE_M)
calibration_check: default_ok_for_this_regime
calibration_evidence: "v2 empirical distribution across same N/Q axes matches Plate 1994 SNR predictions; extending K axis holds all other calibration constant."

# Sweep alignment (§15 gate A)
sweep_alignment_verdict: ALIGNED
swept_params: {K: [200,500,1000,2000,4000,8000], N: [2048,4096,8192,16384], Q_level: [1,2,4]}
effective_params_per_primitive:
  sequence_binding: "K is nominal_K (single primitive; no partition routing); N is nominal_N (dimensionality); Q is BASE_TAG_DENSITY * Q_level"

# Discriminating fraction (§15 gate B)
predicted_accuracy_per_point: "See Section 3 table"
points_in_discriminating_band_MB: 27       # HYPOTHESIZED (band [0.30, 0.70])
points_in_sweep: 72
discriminating_fraction: 0.375

# Signal shape compat (§15 gate C)
composition_edges: []                     # single-primitive cell; no composition

# Positive control (§15 gate D)
positive_control_arms:
  - arm: SUBSTRATE_K200_N16384_Q1
    primitive: sequence_binding
    cited_prior_atom: v2_seed_7 K=200 N=16384 Q=1
    cited_prior_metric: 1.000              # MEASURED@v2 seed_7
    cited_prior_regime: {K: 200, N: 16384, Q: 1, V_ITEMS: 1200, V_POS: 1200}
    test_regime: {K: 200, N: 16384, Q: 1, V_ITEMS: 8500, V_POS: 8500}
    tolerance: 0.10
    if_outside_tolerance: HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH
    regime_extension_audit: SHAPE_MATCH (only V codebook size increased 1200->8500 to accommodate max K=8000; V/K margin same as v2 at K=1000)

# Functional requirements (§15 gate E)
functional_requirements:
  - "Bind K (position, item) pairs into single N-dim bundle" -> sequence_binding primitive
  - "Recover item from bundle given position query" -> unbind + cosine cleanup
  - "Measure phase diagram (K, N, Q) -> top1 recall band" -> 72-pt sweep with 3 arms

# Bands (LOCKED)
BAND_SAT: 0.90
BAND_MB_LO: 0.30
BAND_MB_HI: 0.70
BAND_FLOOR: 0.10

# HP gates (LOCKED, same as v2)
HP_MIN_MB_POINTS: 22
MB_MIN_MB_POINTS: 10
HP_ARMS_DIFF_MIN: 0.20
HP_MIN_SAT_POINTS: 6
HP_MIN_FLOOR_POINTS: 6

# HARD_FAIL guards (LOCKED, same as v2)
HF_all_saturated: META_RULE_Q trip -> HARD_FAIL
HF_all_floored: no signal -> HARD_FAIL
HF_arms_identical: code bug -> HARD_FAIL
HF_avg_arms_diff_lt_0.05: mechanism dead -> HARD_FAIL

# Smoke DISCRIMINATOR-SURVIVES-SCALE gate (v3 new; option A verification)
SCALE_GATE_K_THRESHOLD: 2000
SCALE_GATE_MIN_ESCAPES: 2                 # smoke K>=2000 corners with SUBSTRATE_top1 < 0.90
smoke_gate_scale_check: "check_smoke_discriminator_survives_scale() in core; HARD_FAIL_SMOKE_DISCRIMINATOR_NOT_SURVIVING_SCALE overrides any HP tier if <2 K>=2000 escapes"

# Runtime budget (per-seed)
smoke_wall_budget_s: 300                  # 6 corners x 4 queries; max K=8000/N=16384 dominates
full_wall_budget_s: 5400                  # 72 x 100 queries; K=8000/N=16384 point ~60s worst-case; safety 90min
smoke_timeout: 600
full_timeout: 7200                        # 2h budget per seed on remote_cpu_queue
```

## 5. Smoke corners (v3)

```python
SMOKE_CORNERS = (
    (200,  16384, 1),   # low-K high-N low-Q  -> expect SAT (survives extension)
    (500,  8192,  2),   # mid                 -> expect MB
    (2000, 8192,  1),   # mid-high-K mid-N    -> expect MB (K=2000 fresh)
    (4000, 16384, 1),   # high-K high-N low-Q -> expect MB/TRANS (extension-critical)
    (8000, 16384, 1),   # SCALE preview: DISCRIMINATOR-MUST-SURVIVE-SCALE gate
    (8000, 2048,  4),   # very-high-K low-N high-Q -> expect deep FLOOR
)
```

Smoke HP requirements:
- SUBSTRATE_top1 at (200, 16384, 1) >= 0.80 (SAT survives — required positive control)
- SUBSTRATE_top1 at (8000, 16384, 1) < 0.90 (DISCRIMINATOR-SURVIVES-SCALE gate)
- >= 2 of {(2000,8192,1), (4000,16384,1), (8000,16384,1), (8000,2048,4)} with SUBSTRATE < 0.90
- Not ALL 6 smoke corners saturate (META_RULE_Q)

If smoke fails scale gate: HARD_FAIL_SMOKE overrides any HARD_PASS band tier; block full dispatch.

## 6. Verdict rubric (full 3-seed pooled)

Same as v2 (see core file `aggregate_and_verdict`).

Expected v3 tier: **HARD_PASS** if predicted band distribution holds (n_MB ~27 >> 22; n_SAT ~6-9 >= 6;
n_FLOOR ~20-25 >= 6). If v3 lands MB with n_MB in [10, 21], retain **MIDDLE_BAND** and pivot to
Option B (drop lowest-K axis further OR bracket refinement) via Skunkworks re-recommendation.

## 7. Dispatch plan

- **Queue:** remote_cpu_queue (numpy; PROT-020 CPU routing; laptop CPU quota preserved)
- **Order:** seed_7 smoke -> if scale_gate_pass -> seed_7 full + seed_13 full + seed_19 full (parallel)
- **Timeout:** 7200s per full seed (2h budget); 600s per smoke
- **Blocker:** commit + push to origin/main required (remote_cpu_queue reads main). exp_dev is
  harness-DENIED push; caller must push via hd_metrics_sync or Orchestrator dispatch.

## 8. Rationale for extending K only (not N or Q)

v2 landed shows the saturation is a K-axis phenomenon. All (K=200, N=any) cells saturate at
N=16384; the fix is more K. Reducing N would only rescale the cliff (still hit SAT at low-K).
Increasing Q would add noise but wouldn't push high-N cells past SAT bound. Extending K UP is
the minimal-drift fix per Skunkworks Option A recommendation.

## 9. Reproducibility

- Seeds: [7, 13, 19] (v2 seeds; keep for cross-version comparison)
- Codebook V=8500 (up from v2's 1200 to accommodate max K=8000 with slack)
- Regime float32 numpy (deterministic under seeded RNG); no CUDA nondeterminism
- Bit-identical codebook per-seed reproducible per numpy default_rng semantics

END PREREG
