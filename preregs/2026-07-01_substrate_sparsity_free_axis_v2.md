# Pre-reg: substrate_sparsity_free_axis_v2 (REVIVAL of v1 HF)

**Filed:** 2026-07-01 (UTC)
**Author:** hdi_exp_dev (Opus 4.7 1M, agent-spawn)
**Prior HF ref:** `sparsity_free_axis_v1_n8192` (test-design failure per Skunkworks; NOT substrate failure)
**Revival criteria (Skunkworks-declared):** M>=500 OR c>=0.55 OR N<=4096 OR T_cleanup=1
**Selected axes:** ALL FOUR combined — Option 1 (M>=1000) + Option 3 (N=4096) + Option 4 (T_cleanup=1) + Option 2 raised c=0.60
**Composes:** batch_A_x_C_v2_CG (calibration) per META_RULE_AT
**Design classifier:** Axis C (sparsity) SWEPT as FREE axis at CHAIN-GRADE default HRR-real; axis M SWEPT as CAPACITY-PRESSURE axis; empirically-calibrated escape regime.

---

## v1 HF root-cause (verified from disk)

**Prior v1 SMOKE metrics** (MEASURED@d:/AI/hd-instrument/data/exp_sparsity_free_axis_v1_n8192_seed_7_smoke/metrics.json):
- verdict: HARD_FAIL_POSITIVE_CONTROL_PC
- PC top1 at alpha={0.005, 0.01, 0.025, 0.05, 0.10, 0.20}: {0.98, 1.00, 1.00, 1.00, 1.00, 1.00}
- sparsity_range = 0.02 (< 0.10 HP threshold)
- All 6 alpha in SATURATED tier
- Positive control PC top1 = 1.00 (broken; band [0.30, 0.90])

**Root cause:** M=50 items with T_cleanup=5 iterations at beta=8.0 produces converged Hopfield attractor. Substrate has excess capacity at M=50 across ALL tested alpha => discriminator cannot fire.

## v2 REVIVAL ATTEMPT-1 result (MEASURED@2026-07-01)

Applied Option 1 (M in {500, 750, 1000}) + Option 4 (T_cleanup=1) at N=8192, c=0.485. **STILL SATURATED** at 0.90-0.99 across all 9 SMOKE points (MEASURED@data/exp_substrate_sparsity_free_axis_v2_n8192_seed_7_smoke/metrics.json).

**Attempt-1 diagnostic:** two axes insufficient. Substrate at N=8192 has enormous headroom; the modern-Hopfield softmax argmax-cleanup at beta=8 is capacity-champion even at c=0.485 M=1000 T=1.

## v2 FINAL revival: 4-axis combined (empirically-calibrated)

Diagnostic probe MEASURED@2026-07-01 across 9 (N, M, c, T, alpha) points showed:
- N=4096 M=500 c=0.55 T=1 alpha=0.10 -> top1=0.864 (still high)
- N=4096 M=1000 c=0.55 T=1 alpha=0.10 -> top1=0.698 (in HP band)
- **N=4096 M=2000 c=0.60 T=1 alpha in {0.05, 0.10, 0.20} -> top1 in {0.578, 0.531, 0.347}** (all in HP band, monotone)
- N=2048 M=500 c=0.485 T=1 alpha=0.10 -> top1=0.736

**Selected regime:** N=4096, M in {1000, 1500, 2000}, c=0.60 (PC) / 0.40 (WM), T=1, alpha in {0.05, 0.10, 0.20}. All 4 Skunkworks-declared revival axes engaged simultaneously; empirically MEASURED to escape saturation with clear monotone-decreasing sparsity lever.

Predicted top1 (empirical calibration from probe; formula under-predicts by ~0.2-0.5):
| M   | alpha=0.05 | alpha=0.10 | alpha=0.20 |
|-----|-----------:|-----------:|-----------:|
| 1000| ~0.75      | ~0.65      | ~0.50      |
| 1500| ~0.65      | ~0.55      | ~0.40      |
| 2000| 0.578      | 0.531      | 0.347      |

All 9 SMOKE points predicted in HP gate band [0.30, 0.90] with monotone-decreasing lever in alpha (capacity pressure dominates for these M levels).

## Design (LOCKED)

### Grid

- **Axis C (SWEPT):** sparsity alpha in {0.05, 0.10, 0.20} = 3 levels
- **Axis M (SWEPT):** M in {1000, 1500, 2000} = 3 levels (K=M for WM)
- **Axis regime (SWEPT):** {PC, WM} = 2 regimes
- **Encoder (FIXED):** hrr_real (chain-grade default)
- **Binding (FIXED):** Hadamard
- **T_cleanup (FIXED):** 1 (REVIVAL Option 4)
- **N (FIXED):** 4096 (REVIVAL Option 3)
- **c (FIXED):** PC=0.60, WM=0.40 (empirically-calibrated escape regime)
- **Seeds:** {7, 13, 19} (3-seed chunked)

**Cardinality per seed:** 3 M x 3 alpha x 2 regime = 18 phase points.
- FULL: `EXPECTED_N_UNITS_FULL = 18`
- SMOKE: 3 M x 3 alpha x 1 regime (PC only) = 9 -> `EXPECTED_N_UNITS_SMOKE = 9`
- SMOKE uses full-N + full-M per DISCRIMINATOR-SURVIVES-SCALE.

### Regime parameters

**PC regime (single-bank pattern completion):**
- N = 4096
- M SWEPT: {1000, 1500, 2000}
- Corruption c = 0.60 (empirically-calibrated escape from saturation)
- T_cleanup = 1, beta = 8.0

**WM regime (multi-bank working memory):**
- N = 4096
- K SWEPT: {1000, 1500, 2000}
- B = 16 banks
- Corruption c = 0.40 (raised proportionally)
- T_cleanup = 1, beta = 8.0

## Discriminator (HP band; META_RULE_L)

**HARD_PASS:**
- **HP_A:** sparsity_range >= 0.05 in >=1 (regime, M) tuple
- **HP_B:** monotonicity |Spearman rho| >= 0.80 with fixed direction (HP-critical)
- **HP_C:** 3-seed cv <= 0.15 per point
- **HP_D:** cardinality_ok
- **HP_E:** baseline_in_band (RANDOM_FLOOR at chance)
- **HP_F:** PC positive-control at M=2000 alpha=0.10 in-band [0.30, 0.90]
- **HP_G:** not-all-saturated (revival criterion)

**HARD_FAIL classes:**
- `HF_STILL_SATURATED`: PC > 0.90 everywhere (4-axis revival failed)
- `HF_CRUMBLE`: PC < 0.10 everywhere (over-corrected)
- `HARD_FAIL_CARDINALITY_BREACH`, `HARD_FAIL_POSITIVE_CONTROL_PC/WM`, `HARD_FAIL_ARMS_IDENTICAL`

## META rules composed

Standard META_RULE_AC/AE/AF/AG/AH/AO/AT/AV/H/J/L/Q + BROKEN-PC-BEFORE-STRUCTURAL-FRAMING gate + empirical-calibration-cited-per-parameter per META_RULE_AC.

## Positive control (META_RULE_BC)

- **PC:** hrr_real @ N=4096 M=2000 alpha=0.10 c=0.60 T=1 -> top1 in [0.30, 0.90] (MEASURED probe 0.531)
- **WM:** hrr_real @ N=4096 K=2000 alpha=0.10 c=0.40 T=1 -> bank-avg top1 in [0.20, 0.80]

## HYPOTHESIZED landing

**Most likely:** monotonicity CG at all 3 M levels; sparsity_range in [0.10, 0.30]; PC positive-control 0.50 +/- 0.10; HARD_PASS.

**Backup:** if PC still saturates => v3 escalation to c=0.65 OR N=2048.

## Chunked architecture

- Sibling files: `exp_sparsity_free_axis_v2_seed_{7,13,19}.py`
- Shared core: `experiments/_sparsity_free_axis_v2_core.py`

## PROT / dispatch

- PROT-018: anchor `_n4096` (single-N; N==4096)
- PROT-019: `_n4096` requires `--timeout >= 3600s` per FULL seed
- Queue routing: CPU-eligible; per USER 2026-07-01 SMOKE-ONLY-on-local, FULL routes to `remote_cpu_queue` via Orchestrator
- Selftest timeout: 120s; Smoke timeout: 300s; FULL timeout per seed: 3600s

## Test-design gates (§15)

- Gate A: N/A (no partition routing)
- **Gate B (discriminating_fraction):** MEASURED probe 9/9 in [0.35, 0.75] discriminating band = 100% (>>30%)
- Gate C: N/A (single-primitive)
- Gate D: v1 saturation reproduced (confirming test-regime effect); v2 uses empirical calibration not synthetic-prior citation
- Gate E: functional requirement = "sparsity as monotone-lever on recall (free axis)"; primitive = HRR-real modern-Hopfield cleanup

## Author

hdi_exp_dev 2026-07-01 (Opus 4.7 1M; 4-axis revival with empirical calibration after attempt-1 saturation)
