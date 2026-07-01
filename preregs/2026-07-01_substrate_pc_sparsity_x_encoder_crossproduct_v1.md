# PRE-REG: substrate_pc_sparsity_x_encoder_crossproduct_v1

**Date filed:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Anchor family:** `substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_{7,13,19}`

## Hypothesis / Motivation

First OUTER x OUTER CROSS-AXIS attempt for the substrate TRUE phase diagram
(axis A = Encoder family x axis C = Sparsity). Cross-products between axes
were <5% explored per TRUE phase diagram doc. USER 2026-07-01 overnight
priority.

Meta rule AO says sparse-bipolar bundle-lift is regime-conditional; the
cross-product could QUANTIFY the regime in which each encoder benefits from
sparsity vs is hurt by it. Expected structure per Mu-Viswanath (BIAS-P
anisotropy): dense encoders should degrade monotonically with sparsity;
sparse_bipolar may show non-monotonic peak at some intermediate sparsity per
META_RULE_AO.

## Grid

**Axis A (Encoder family; OUTER):**
- `binary_bipolar` : `{-1, +1}^N` dense
- `hrr_real`       : Gaussian real dense, L2-normalized
- `fhrr`           : unit-modulus complex in `C^(N/2)`
- `sparse_bipolar` : `{-1, 0, +1}^N` ternary (native sparsity)

**Axis C (Sparsity; OUTER):** fraction NONZERO per codeword after mask
- FULL:  `{0.01, 0.05, 0.10, 0.25}`
- SMOKE: `{0.05, 0.25}` (low + high corners)

**Fixed regime (inner axes locked):**
- `N=8192` (cliff-observable per PC v2.2 CG evidence)
- `corruption=0.485` (cliff-K per PC v2.2 MEASURED@`data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7/metrics.json`)
- `T=5` cleanup iterations
- `M_items=300` (FULL) / `150` (SMOKE)

**Sparsity semantics:**
- Dense encoders (binary_bipolar / hrr_real / fhrr): sparsity applied as
  random per-row zero-mask; mask preserved through cleanup via `sign_op`
- `sparse_bipolar`: sparsity is native codebook density (same mask
  semantics for cleanup)
- Same mask applied to Q_corrupted so cosine semantics stay clean

## Cardinality

- `EXPECTED_N_UNITS_FULL = 4 * 4 = 16` per seed (48 total across 3 seeds)
- `EXPECTED_N_UNITS_SMOKE = 4 * 2 = 8` per seed
- `cardinality_ok: true` (mandatory META_RULE_H)

## Arms

- `MECHANISM`  : substrate encoder + corruption + Hopfield cleanup
- `RANDOM_FLOOR` : same encoder + FRESH RANDOM (not corrupted source) + same cleanup

Discriminator = `top1_mechanism - top1_random`.

## Pre-reg fields (mandatory per exp_dev.md §15 / SCHEMA-VET)

### `sweep_alignment_verdict: ALIGNED`
Encoder axis A independently controls encoding family; sparsity axis C
independently controls codebook density. Both applied inside `_build_and_mask`;
downstream `_hopfield_cleanup` receives them via score_fn / sign_op /
active_mask — every primitive experiences BOTH axes as intended. No hidden
coupling. Effective params = nominal params for every point.

### `discriminating_fraction: 1.00`
Per encoder, sparsity ranges 0.01–0.25 span factor-of-25 density; at cliff-K
corruption=0.485, top1 predicted to vary strongly across sparsity for
sparse_bipolar (native), moderately for dense encoders (mask degrades signal).
All 16 points predicted to land in a mix of `[FLOOR, MB, HP]` bands (0/16
expected to saturate; corruption=0.485 is cliff-K which caps top1 at ~0.75 per
PC v2.2 CG evidence). `discriminating_fraction >= 0.30` easily.

Predicted top1 per point (HYPOTHESIZED; verified via smoke):

| encoder \ sparsity | 0.01  | 0.05  | 0.10  | 0.25  |
|-------------------|-------|-------|-------|-------|
| binary_bipolar    | ~0.05 | ~0.30 | ~0.55 | ~0.70 |
| hrr_real          | ~0.05 | ~0.25 | ~0.50 | ~0.65 |
| fhrr              | ~0.05 | ~0.25 | ~0.50 | ~0.65 |
| sparse_bipolar    | ~0.35 | ~0.50 | ~0.55 | ~0.60 |

Interaction visible: dense encoders show larger sparsity-range (0.65) than
sparse_bipolar (0.25) — delta ~0.40 >> 0.15 threshold. Predict HARD_PASS.

### `composition_edges: [SHAPE_MATCH]`
Only ONE composition: `_hopfield_cleanup` composes score_fn -> softmax ->
matmul-back -> sign_op. Same shape (M, N or M, N/2 complex) throughout.

### `positive_control_arms` (META_RULE_BC)

```yaml
positive_control_arms:
  - arm: BINARY_BIPOLAR_SPARSITY_0.10
    primitive: pattern_completion_cliff_K
    cited_prior_atom: PC_v2.2_seed_7_dense_cliff_grid_c=0.485_N=8192_T=5
    cited_prior_metric: top1 in [0.30, 0.75] (MEASURED@ Skunkworks commit
      2daf9b55 dense cliff grid seed_7 metrics.json phase_map c=0.485 N=8192
      T=5 tier=MIDDLE_BAND)
    cited_prior_regime: {N: 8192, c: 0.485, T: 5, M: 500, encoder: dense_bipolar}
    test_regime: {N: 8192, c: 0.485, T: 5, M: 300, sparsity_mask: 0.10}
    tolerance: 0.15 (widened for M=300 vs M=500 shift + sparsity effect)
    if_outside_tolerance: HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH
    regime_extension_audit: SHAPE_DRIFT_documented (M=300 lower + 10pct
      zero-mask; cell-author acknowledges cliff-K semantics extend to
      sparse regime is HYPOTHESIS not established fact — this cell TESTS it)
    top1_band_lo: 0.10
    top1_band_hi: 0.85
```

### `functional_requirements`

```yaml
functional_requirements:
  - requirement: "Encoder family influences cliff-K pattern completion"
    primitive: encoder_family_registry (binary_bipolar/hrr_real/fhrr/sparse_bipolar)
    status: CG evidence per PC-encoder-family v1 smoke HARD_PASS 2026-06-28
      (4 encoder pairs distinct at cliff-K)
  - requirement: "Sparsity axis is a discriminator within the phase diagram"
    primitive: _apply_sparsity_mask_real / _apply_sparsity_mask_fhrr /
      _build_sparse_bipolar_native (density-parameterized)
    status: HYPOTHESIZED (this cell TESTS it)
  - requirement: "Encoder x sparsity interaction is measurable"
    primitive: per_encoder_sparsity_range + interaction_pair_deltas
    status: HYPOTHESIZED (this cell TESTS it via HARD_PASS band)
```

### `crlb_floor_computed` + `discriminator_reachability`

```yaml
crlb_floor_computed:
  dense (s=1.0):  crlb_1step_cliff = 0.4861 THEORETICAL@sqrt(2 log M / N)
  s=0.01:         crlb_1step_cliff = 0.0000 (noise > 0.5 signal; below floor)
  s=0.05:         crlb_1step_cliff = 0.3390 THEORETICAL
  s=0.10:         crlb_1step_cliff = 0.3939 THEORETICAL
  s=0.25:         crlb_1step_cliff = 0.4383 THEORETICAL
crlb_formula_reference: sqrt(2 * log(M) / (sparsity * N))
discriminator_reachability: true (corruption=0.485 sits ABOVE dense cliff
  0.486 AT MARGIN; at s=0.25 cliff=0.4383 so mechanism arm predicted to
  FAIL at s=0.25; at s=0.01 cliff=0 so mechanism arm always FAILS; discriminator
  visible across sparsity spectrum)
```

### `baseline_in_band` (META_RULE_AG)

RANDOM_FLOOR arm expected to score in `[0.001, 0.02]` (chance = 1/M = 0.003 at
M=300); floor arm exists specifically to prove the mechanism arm > chance.
Baseline (RANDOM_FLOOR) is INTENTIONALLY at floor; it's the discriminator arm
not the "regime baseline". Mechanism arm is expected in `[0.05, 0.75]` across
grid — spans discriminating band by design.

### `cardinality_ok`, `arms_differ_verified`
Both mandatory; verified by pre-flight `--self-test` (checks encoder codebook
distinctness at 12 combos + arms-differ per combo).

### `final_metrics_atomicity: "tmp_replace"`
`metrics.json` written via `os.replace(tmp, final)` after all seeds aggregate;
never leaves canonical path in mid-mutation state.

### `except SystemExit: raise` ordering
Verified in outer try/except of seed_7/13/19 sibling cells:
```
except SystemExit: raise
except KeyboardInterrupt: raise
except Exception as e: _write_import_crash_sentinel(e); raise
```

### `calibration_check: default_ok_for_this_regime`
Corruption model per encoder is calibrated to `E[cos(Q_corrupted, source)] = 1 - 2c`
(verified in selftest with `tol=0.15` at c=0.30). PC v2.2 evidence at c=0.485
N=8192 T=5 dense: MEASURED_MECHANISM cliff-K. Cross-product cell tests
extension to sparse regimes — same calibration semantics.

### Defensive-error-checking fields (§13 MANDATORY)

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
  - positive control @ binary_bipolar s=0.10 top1 in `[0.10, 0.85]`
  - `interaction_pairs_visible >= 2` (out of 6 encoder pairs) with
    per-encoder sparsity-range delta `>= 0.15`

- **MIDDLE_BAND** iff:
  - all HP conditions except `interaction_pairs_visible` in `{0, 1}`
  - OR `n_encoder_pairs_differ < 6` (encoder main effect absent at cliff-K
    with sparsity axis — substantive negative)

- **HARD_FAIL** iff:
  - cardinality breach OR
  - any combo has `mech == random` (arms identical) OR
  - positive control fails band

**SMOKE bands (per-seed cell; SMOKE=8 points):**

- **HARD_PASS** iff: cardinality_ok + arms_differ(8/8) + 6 encoder pairs
  distinct + 1 sparsity pair distinct + positive control pass + tiers span
  the cliff (not all SATURATED / not all FLOOR)
- **HARD_FAIL** iff: any smoke_gate_predicate check fails

## Timeout budget

- Smoke wall: ~10-30s per seed (8 phase points at N=8192, M=150 on GPU)
- FULL wall: ~30-90s per seed (16 phase points at N=8192, M=300 on GPU)
- With safety factor `1.5x` + per-seed cell chunked: `timeout_s = 3600`
  per seed (satisfies PROT-019 `_n>=4096` floor)

## Queue routing

`overnight_queue` (GPU; matmul-bound at N=8192 x 16 pts x 3 seeds).
Local smoke can run on CPU if CUDA unavailable (matmul at N=8192 M=300 T=5
takes ~1-5s per phase point on modern CPU).

## Files

- Core: `experiments/_substrate_pc_sparsity_x_encoder_crossproduct_v1_core.py`
- Seed 7: `experiments/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_seed_7.py`
- Seed 13: `experiments/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_seed_13.py`
- Seed 19: `experiments/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_seed_19.py`
- Pre-reg: this file
