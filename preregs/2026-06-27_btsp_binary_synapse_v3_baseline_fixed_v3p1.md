# PRE-REG: btsp_binary_synapse_v3_baseline_fixed_v3p1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M agent spawn, Research team-lead dispatch)
**Barrier:** B3 (consolidation under saturation) - Wave 2 redesign
**Skunkworks audit:** notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3)
**Predecessor:** experiments/exp_btsp_binary_synapse_v3_sparse_regime_swept.py

## TRIGGERS v3.1 OVER v3

v3 hit BinHeb baseline mean ~0.99 across all (fp, fq) cells (Skunkworks "test-design bug"). Root cause located: line 326 `W_bin = np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0` introduces +1 bias on entries where W==0, collapsing W_bin to mean=0.9932 (99.66% entries are +1). The "binary baseline" thus classifies trivially well via positive-bias dominance, leaving BTSP no headroom.

## HYPOTHESIS

With proper bipolar binarization (row-median split), BinHeb baseline at headline (fp=0.005, fq=0.0025) DROPS into informative band [0.10, 0.50] (sparse-input + binary-matrix has fundamental capacity limits). At THAT regime, BTSP_sparse has headroom to exceed BinHeb by >= 0.05 per Wu-Maass 2025 mechanism.

If BinHeb still saturates at >= 0.95 after row-median fix, the test-design bug is deeper than binarization and the Wave 2 audit must surface a v3.2 redesign.

## ROOT-CAUSE FIX

Replace:
```python
W_bin = np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0
```
With proper row-median bipolar:
```python
row_meds = np.median(W, axis=1)
W_bin = np.where(W >= row_meds[:, None], 1.0, -1.0)
```
Zero-rows fall back to random {-1, +1} (deterministic per seed).

## DIAGNOSTIC PROBE (CARRIED FORWARD TO METRICS)

Selftest asserts `abs(mean(W_bin)) < 0.30`. If still bigger, binarization fix incomplete.
Metrics report `mean_W_bin` per (seed, fp) cell.

## ARMS (4)

1. ARM_CONT_HEBBIAN_BASELINE -- dense reference (unchanged from v3)
2. ARM_BINARY_HEBBIAN_BASELINE -- FIXED row-median bipolar binarization
3. ARM_BTSP_SPARSE_SWEEP -- 25 cells over (fp, fq) grid (unchanged from v3)
4. ARM_DIAG_TAG_FRACTION_SWEEP -- diagnostic (unchanged)

## SWEEP GRID

Same as v3: fp in {0.005, 0.01, 0.025, 0.05, 0.10}; fq in {0.0025, 0.01, 0.05, 0.10, 0.25}.

## PRE-REG BANDS

**HARD_PASS:**
- BinHeb at headline NOT saturating: `mean_acc < 0.95`
- AND `abs(mean_W_bin) < 0.30` (proper bipolar)
- AND at some grid cell `(fp <= 0.10, fq <= 0.25)`: BTSP - BinHeb >= 0.05
- AND observed tag_fraction in [0.5*fq, 2*fq + 0.05]
- AND cv across seeds < 0.10

**MIDDLE_BAND:**
- Lift in [0.03, 0.05) OR HARD_PASS arithmetic with tag-band miss

**HARD_FAIL:**
- BinHeb at headline still >= 0.95 (binarization fix incomplete)
- OR `abs(mean_W_bin) > 0.30` (binarization still biased)
- OR max BTSP-BinHeb lift across grid < 0.03 (mechanism null)
- OR cardinality breach

## REGIME

Same as v3: N_DIM=2048, N_CAT=100, N_TRAIN=10, proto_noise=0.85, alpha=0.0488.
Seeds full=[11,13,19]; smoke=[11].

**Smoke FULL_N_PREVIEW**: 1-seed BinHeb at full N=2048 headline cell to confirm discriminator survives scale (per USER feedback discriminator-must-survive-scale).

## CARDINALITY_OK

EXPECTED_N_UNITS = n_seeds * (1 cont + 5 binheb_per_fp + 25 btsp_grid + 25 diag) = n_seeds * 56.
Full: 3*56=168. Smoke: 1*56=56 + 1 preview.

## FAIRNESS (META_RULE_AA)

- All arms read SAME SURFACE: cosine over W @ query_sparse against prototypes
- BinHeb reads matched-sparsity test queries (same `_sparse()` function as BTSP)
- Discriminator FIRES at headline cell (META_RULE_K)
- Baseline NOT trivially doing the mechanism (no eligibility, no tag)

## DISPATCH

Queue: remote_cpu_queue (~2 CPU-hr full).
Timeout: 7200s (2 hours wall).

## EXPECTED OUTCOMES

- HARD_PASS: confirms Wu-Maass mechanism in our task class once binarization unbiased
- HARD_FAIL with BinHeb still saturating: deeper redesign needed (sparse input space too small)
- HARD_FAIL with lift < 0.03: BTSP-binary genuinely null at our prototype-classification (atomize HONEST_NEG)
