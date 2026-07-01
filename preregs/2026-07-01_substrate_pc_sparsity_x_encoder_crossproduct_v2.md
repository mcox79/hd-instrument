# PRE-REG: substrate_pc_sparsity_x_encoder_crossproduct_v2

**Date filed:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Anchor family:** `substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_{7,13,19}`
**Parent cell:** v1 (`substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_*`)
**Drill kind:** CAPACITY_LIFT_2X_DRILL
**Skunkworks reference:** a7708cb2 (v1 tier = MM_capacity_bound; META_RULE_Q trip)

## Hypothesis / Motivation

v1 landed MM_capacity_bound: 10/16 phase points SATURATED at top1=1.000 (M=300, N=8192, corruption=0.485). Only `fhrr` showed genuine per-encoder-sparsity discrimination (`per_encoder_sparsity_range`=0.297 MEASURED@data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_7/metrics.json). The three real-valued encoders (`binary_bipolar`, `hrr_real`, `sparse_bipolar`) failed to differentiate across sparsity because M=300 items in N=8192 gives capacity ratio too far below break threshold to expose the sparsity axis.

v2 is a 2x-drill capacity-lift per Skunkworks recommendation "M=600 or M=1000". Goal: convert 10 SATURATED cells to discriminating so all four encoders show cross-encoder x cross-sparsity separation.

## What changed vs v1

| Field | v1 | v2 | Rationale |
|-------|-----|-----|----------|
| `M_ITEMS_FULL` | 300 | **600** | 2x-drill per Skunkworks a7708cb2 |
| `M_ITEMS_SMOKE` | 150 | **300** | Half-full M (was v1 full M) for smoke speed |
| `SPARSITY_LEVELS_FULL` | (0.01, 0.05, 0.10, 0.25) | **(0.05, 0.10, 0.25, 0.50)** | Drop always-FLOOR s=0.01; add near-break-edge s=0.50 |
| `SPARSITY_LEVELS_SMOKE` | (0.05, 0.25) | **(0.10, 0.50)** | Smoke covers mid-low + high-corner |
| `POSITIVE_CONTROL` | binary_bipolar@s=0.10 | **binary_bipolar@s=0.25** | s=0.10 predicted below discriminating band at M=600 |
| `POSITIVE_CONTROL_SMOKE` | binary_bipolar@s=0.05 | **binary_bipolar@s=0.50** | Smoke high-corner |
| `HARD_PASS` gate | interaction_pairs_visible>=2 | **n_encoders_with_sparsity_range>=3 AND interaction_pairs_visible>=2** | v1 shipped HARD_PASS on 1-of-4-encoders discrimination; v2 requires 3+ encoders |

Everything else (encoder primitives / corruption / cleanup / random_floor / calibration / hardening / chunked-per-seed / defensive-error-checking) is identical to v1.

## Grid

**Axis A (Encoder family; OUTER):** unchanged from v1.
- `binary_bipolar` : `{-1, +1}^N` dense
- `hrr_real`       : Gaussian real dense, L2-normalized
- `fhrr`           : unit-modulus complex in `C^(N/2)`
- `sparse_bipolar` : `{-1, 0, +1}^N` ternary (native sparsity)

**Axis C (Sparsity; OUTER):** SHIFTED UP for v2 capacity-lift.
- FULL:  `{0.05, 0.10, 0.25, 0.50}`
- SMOKE: `{0.10, 0.50}`

**Fixed regime (v2):**
- `N=8192` (unchanged; cliff-observable per PC v2.2 CG evidence)
- `corruption=0.485` (unchanged; cliff-K MEASURED@commit 2daf9b55 phase_map c=0.485 N=8192 T=5)
- `T=5` cleanup iterations (unchanged)
- `M_items=600` FULL / `300` SMOKE (v2 CAPACITY-LIFT)

## Capacity-lift physics (THEORETICAL)

Hopfield storage capacity `C ~ N / (2 log M)`. Capacity pressure ratio `2*M*log(M) / N_eff` where `N_eff = sparsity * N`. Empirical break edge observed at `cap_ratio ~ 1.67` (v1 seed=7: binary_bipolar @ s=0.25 M=300 N=8192 gave `top1=0.887` at `cap_ratio=1.67` MEASURED@data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_7/metrics.json).

v2 predicted capacity ratios (THEORETICAL @ N=8192 M=600):

| sparsity | N_eff | cap_ratio | Predicted tier |
|----------|-------|-----------|----------------|
| 0.05 | 410 | 18.74 | FLOOR / breaking |
| 0.10 | 819 | 9.37 | breaking / FLOOR edge |
| 0.25 | 2048 | 3.75 | MIDDLE_BAND (mechanism arm ~0.5-0.8) |
| 0.50 | 4096 | 1.87 | HARD_PASS / near saturation edge |

Compare v1 M=300: cap_ratios were (8.36, 4.18, 1.67, 0.42) for sparsities (0.05, 0.10, 0.25, 1.00) - only s=0.25 (cap=1.67) was near break edge. v2 shifts the entire grid onto the break edge from BOTH sides.

## Cardinality

- `EXPECTED_N_UNITS_FULL = 4 * 4 = 16` per seed (48 total across 3 seeds)
- `EXPECTED_N_UNITS_SMOKE = 4 * 2 = 8` per seed
- `cardinality_ok: true` (mandatory META_RULE_H)

## Arms

- `MECHANISM`  : substrate encoder + corruption + Hopfield cleanup
- `RANDOM_FLOOR` : same encoder + FRESH RANDOM query (independent mask) + same cleanup

Discriminator = `top1_mechanism - top1_random`.

## SCHEMA-VET fields (mandatory per exp_dev.md §15)

### `sweep_alignment_verdict: ALIGNED`
Same as v1: encoder axis A and sparsity axis C are independently controlled inside `_build_and_mask`; downstream `_hopfield_cleanup` receives both via score_fn / sign_op / active_mask. Effective params = nominal params for every point.

### `discriminating_fraction: 1.00`
Per capacity-ratio prediction table above, all 16 points span mixed `[FLOOR / MB / HP]` tiers. THEORETICAL prediction (verified via smoke): 0/16 SATURATED, 4-8/16 in `[FLOOR]`, 4-8/16 in `[MB, HP]`. Predicted top1 per point (HYPOTHESIZED; verified via smoke):

| encoder \ sparsity | 0.05  | 0.10  | 0.25  | 0.50  |
|-------------------|-------|-------|-------|-------|
| binary_bipolar    | ~0.02 | ~0.05 | ~0.50 | ~0.85 |
| hrr_real          | ~0.02 | ~0.05 | ~0.45 | ~0.85 |
| fhrr              | ~0.15 | ~0.35 | ~0.55 | ~0.65 |
| sparse_bipolar    | ~0.05 | ~0.15 | ~0.60 | ~0.85 |

If prediction holds: per_encoder_sparsity_range for all 4 encoders will be >= 0.50 (much larger than 0.15 threshold). v2 target: n_encoders_with_sparsity_range>=0.15 == 4/4 (v1 was 1/4). `discriminating_fraction >= 0.30` easily.

### `composition_edges: [SHAPE_MATCH]`
Same as v1: single composition `_hopfield_cleanup` -> score_fn -> softmax -> matmul-back -> sign_op. Same shape (M, N or M, N/2 complex) throughout.

### `positive_control_arms` (META_RULE_BC + Gate D)

```yaml
positive_control_arms:
  - arm: BINARY_BIPOLAR_SPARSITY_0.25_v2
    primitive: pattern_completion_cliff_K
    cited_prior_atom: v1_seed_7_binary_bipolar_s=0.25 (MEASURED@data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_7/metrics.json:phase_map)
    cited_prior_metric: top1=0.887 at (M=300, s=0.25, N=8192, c=0.485)
    cited_prior_regime: {N: 8192, c: 0.485, T: 5, M: 300, sparsity: 0.25}
    test_regime: {N: 8192, c: 0.485, T: 5, M: 600, sparsity: 0.25}
    tolerance: 0.35 (M double drops top1 substantially per capacity-lift THEORETICAL)
    if_outside_tolerance: FLAG for cell-author review, not HARD_FAIL (predicted movement is the whole point)
    regime_extension_audit: CAPACITY_LIFT_INTENTIONAL (M doubled; primitive stable; regime change is the drill)
    top1_band_lo: 0.10  # allow full band; primary discriminator is sparsity_range not point-value
    top1_band_hi: 0.95
```

### `functional_requirements`

```yaml
functional_requirements:
  - requirement: "Encoder family influences cliff-K pattern completion"
    primitive: encoder_family_registry (binary_bipolar/hrr_real/fhrr/sparse_bipolar)
    status: CG evidence per PC-encoder-family v1 smoke HARD_PASS 2026-06-28 + v1 encoder_pairs_differ 6/6 MEASURED@v1 metrics
  - requirement: "Sparsity axis is a discriminator within the phase diagram AT MATCHED CAPACITY"
    primitive: _apply_sparsity_mask_real / _apply_sparsity_mask_fhrr / _build_sparse_bipolar_native (density-parameterized)
    status: HYPOTHESIZED at v2 M=600 (v1 M=300 saturated for 3/4 encoders)
  - requirement: "Cross-encoder cross-sparsity interaction is measurable when capacity pressure matches break threshold"
    primitive: per_encoder_sparsity_range + interaction_pair_deltas + n_encoders_with_sparsity_range
    status: HYPOTHESIZED (v2 tests via HARD_PASS band = 3+ encoders show range >= 0.15)
```

### `crlb_floor_computed` + `discriminator_reachability`

```yaml
crlb_floor_computed:
  s=0.05:  crlb_1step_cliff = 0.4116 THEORETICAL@sqrt(2 log M / (s*N)) at M=600 N=8192
  s=0.10:  crlb_1step_cliff = 0.4375
  s=0.25:  crlb_1step_cliff = 0.4605
  s=0.50:  crlb_1step_cliff = 0.4713
crlb_formula_reference: 0.5 * (1 - sqrt(2 * log(M) / (sparsity * N)))
capacity_ratio_ref: 2 * M * log(M) / (sparsity * N)  # break edge ~1.67 MEASURED@v1
discriminator_reachability: true
  Rationale: at s=0.50 (cap_ratio=1.87) substrate near break edge; c=0.485 sits
  ABOVE crlb cliff so mechanism arm should be well-defined but reduced from
  SAT to HP band; at s=0.10 (cap_ratio=9.37) substrate deeply above capacity
  so mechanism arm should drop to FLOOR; the range >=0.15 gate is REACHABLE.
```

### `baseline_in_band` (META_RULE_AG)
RANDOM_FLOOR arm expected in `[0.001, 0.03]` (chance = 1/M = 0.00167 at M=600). Baseline is the discriminator arm; not the "regime baseline". Mechanism arm expected in `[0.02, 0.85]` across grid - spans full discriminating band by design.

### `cardinality_ok`, `arms_differ_verified`
Both mandatory; verified by pre-flight `--self-test` (checks encoder codebook distinctness at 12 combos + capacity-ratio monotonicity + calibration).

### `final_metrics_atomicity: "tmp_replace"`
`metrics.json` written via `os.replace(tmp, final)` after all seeds aggregate; never leaves canonical path in mid-mutation state.

### `except SystemExit: raise` ordering
Verified in outer try/except of seed_7/13/19 sibling cells:
```python
except SystemExit: raise
except KeyboardInterrupt: raise
except Exception as e: _write_import_crash_sentinel(e); raise
```

### `calibration_check: default_ok_for_this_regime`
Corruption model per encoder calibrated to `E[cos(Q_corrupted, source)] = 1 - 2c` (verified in selftest with tol=0.15 at c=0.30). PC v2.2 evidence at c=0.485 N=8192 T=5 dense: MEASURED_MECHANISM cliff-K. v2 selftest additionally verifies capacity-ratio monotonicity across sparsity.

### Defensive-error-checking fields (§13 MANDATORY; all inherited from v1)

```yaml
cell_chunked: true (3 sibling files: seed_7, seed_13, seed_19)
start_marker_written: true (_write_minimal_metrics "STARTED" at main() entry)
crash_diagnostic_present: true (_write_import_crash_sentinel; SystemExit raise ordering ok)
heartbeat_present: true (per-phase-point flush print via [point] tag)
defensive_error_checking: "passed_all_4_patterns"
```

## Verdict bands (LOCKED before dispatch)

**FULL bands (per-seed cell):**

- **HARD_PASS** iff:
  - `cardinality_ok` (16/16)
  - all 16 combos `arms_differ` (mech vs random)
  - all 6 encoder pairs distinct (main effect on axis A)
  - positive control @ binary_bipolar s=0.25 top1 in `[0.10, 0.95]`
  - **`n_encoders_with_sparsity_range >= 3`** (v1 was 1; v2 target: escape single-encoder discrimination)
  - `interaction_pairs_visible >= 2` (out of 6 encoder pairs) with per-encoder sparsity-range delta `>= 0.15`

- **MIDDLE_BAND** iff:
  - HP fails on either `n_encoders_with_sparsity_range < 3` (partial capacity-lift)
    OR `interaction_pairs_visible < 2` (main effects only)
  - OR `n_encoder_pairs_differ < 6` (encoder main effect absent)

- **HARD_FAIL** iff:
  - cardinality breach OR
  - any combo has `mech == random` (arms identical) OR
  - positive control fails band

**SMOKE bands (per-seed cell; SMOKE=8 points at N=8192 M=300):**

- **HARD_PASS** iff: cardinality_ok + arms_differ(8/8) + 6 encoder pairs distinct + 1 sparsity pair distinct + positive control pass + tiers span the cliff + **`sat_frac <= 0.75`** (v1 was 62.5pct sat; v2 must at least ATTEMPT escape)
- **HARD_FAIL** iff: any smoke_gate_predicate check fails

## DISCRIMINATOR-SURVIVES-SCALE compliance

Applied CHECK A: smoke at FULL N=8192 (not smaller smoke-N). Smoke uses M=300 (half full M=600) purely for wall-time; N + corruption + iters + encoder set + sparsity mid+high corners are FULL regime. Rejection criterion: if smoke sat_frac > 75% (worse than v1 baseline 62.5%), v2 capacity-lift failed the drill and cell-author iterates to v3 (M=1000+ or N-reduction).

## Timeout budget

- Smoke wall: ~20-45s per seed (8 phase points at N=8192, M=300 on GPU; ~40s on CPU)
- FULL wall: ~60-120s per seed (16 phase points at N=8192, M=600 on GPU)
- With safety factor `1.5x` + per-seed cell chunked: `timeout_s = 3600` per seed (satisfies PROT-019 `_n>=4096` floor)

## Queue routing

- FULL: `overnight_queue` (GPU; matmul-bound at N=8192 x 16 pts x 3 seeds; also acceptable `remote_cpu_queue` per Fix #24 exemption since cell is small)
- Smoke: `local_cpu_queue` acceptable (matmul at N=8192 M=300 T=5 takes ~1-5s per phase point on modern CPU)

## Files

- Core: `experiments/_substrate_pc_sparsity_x_encoder_crossproduct_v2_core.py`
- Seed 7: `experiments/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_seed_7.py`
- Seed 13: `experiments/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_seed_13.py`
- Seed 19: `experiments/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_seed_19.py`
- Pre-reg: this file
- v1 core (reference): `experiments/_substrate_pc_sparsity_x_encoder_crossproduct_v1_core.py`
- v1 pre-reg (reference): `preregs/2026-07-01_substrate_pc_sparsity_x_encoder_crossproduct_v1.md`
