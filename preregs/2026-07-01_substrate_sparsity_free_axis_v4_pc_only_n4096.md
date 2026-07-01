# Pre-reg: substrate_sparsity_free_axis_v4_pc_only_n4096

**Filed:** 2026-07-01 (UTC)
**Author:** hdi_exp_dev (Opus 4.7 1M, agent-spawn)
**Prior refs:**
- v1 HF (Atom 4): `sparsity_free_axis_v1_n8192` — test-design failure (T=5 saturation at M=50)
- v2 HF (Atom 17): `substrate_sparsity_free_axis_v2_n4096` — HARD_FAIL_POSITIVE_CONTROL_WM ONLY; PC data was HP-clean but was overridden by the WM gate
- v3 cell-author (2026-07-01): architectural-bug finding — v2/v3 shared core `_sparsity_free_axis_v2_core.py` line 419 computes `vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, ...)` but only uses it in calibration diagnostics (lines 443-445); NEVER in the WM readout path. WM top1 is INSENSITIVE to CORRUPTION_WM by construction. v3 c=0.55 escalation was architecturally unachievable (v3 c=0.55 top1 identical to v2 c=0.40: 0.9526, 0.9626, 0.8228 at three matching points).

**v4 scope (Option D from prior cell-author):** RETIRE WM regime entirely; PC-only. Bank the PC sparsity axis CG today; defer WM corruption-recovery to a future v5 with the readout bug fixed.

**Composes:** v2 PC-scope MEASURED data (positive-control calibration) per META_RULE_AT.

**Design classifier:** Axis C (sparsity) SWEPT as FREE axis at chain-grade default HRR-real; axis M SWEPT as capacity-pressure axis; PC regime only.

---

## WM regime deferred to v5 (LOAD-BEARING; sub-agent readers, note)

The WM regime in v2/v3 is architecturally broken. Filing this pre-reg WITHOUT a WM arm is intentional and CORRECT — running WM again in v4 would waste compute and mask a real substrate question with an unfixed instrument bug.

- **Bug:** `experiments/_sparsity_free_axis_v2_core.py:419` `vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, sub_seed)` computed and only referenced at lines 443-445 (calibration cosine diagnostic), then `del` at line 448. The `readouts = keys * bank_trace` uses raw `vals` via the pre-corruption `bank_trace = _bind_hadamard(keys, vals).sum(dim=0)`, and `_hopfield_cleanup(readouts_normed, vals, T_WM, ...)` cleans back to raw `vals` too. Corruption never reaches the readout.
- **Empirical confirmation:** three matching WM top1 values at v2 c=0.40 vs v3 c=0.55: 0.9526, 0.9626, 0.8228 IDENTICAL.
- **v5 scope:** rewrite WM readout so that `vals_corr` is the actual retrieval key (e.g., unbind `bank_trace` with `keys_corr` OR add `vals_corr` as the noisy key to the cleanup step, not clean `vals`). Detailed in `notes/wm_readout_architectural_bug_deferred_v5_2026-07-01.md`.

---

## v2 PC data re-read supports v4 HARD_PASS (MEASURED cite base)

**MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v2_n4096_seed_{7,13,19}/metrics.json**

Cross-seed aggregation (3 seeds x 3 M x 3 alpha = 27 points):

| M    | alpha=0.05 mean | alpha=0.10 mean | alpha=0.20 mean | Spearman rho | max cv |
|------|----------------:|----------------:|----------------:|-------------:|-------:|
| 1000 | 0.7210          | 0.7077          | 0.5393          | -1.0000      | 0.0229 |
| 1500 | 0.6433          | 0.5860          | 0.4335          | -1.0000      | 0.0180 |
| 2000 | 0.5852          | 0.5148          | 0.3608          | -1.0000      | 0.0208 |

**All 27 points MEASURED in [0.3555, 0.7300]** — well within HP band [0.30, 0.90].
**Spearman = -1.0** at all 3 M levels (monotone-decreasing).
**Cross-seed cv <= 0.023** everywhere (well below 0.05 gate).
**Random floor = 0.001** (well below 0.05 chance gate).

If v2 were re-verdicted on PC-scope-only, it would land HARD_PASS_SPARSITY_MONOTONE_PC. v4 makes this HP eligible by removing WM from the verdict question AND extending the M grid at the ends for additional evidence.

## Design (LOCKED)

### Grid

- **Axis C (SWEPT):** sparsity alpha in {0.05, 0.10, 0.20} = 3 levels (v2-inherited)
- **Axis M (SWEPT; EXTENDED):** M in {800, 1000, 1500, 2000, 2500} = 5 levels
  - v2 was {1000, 1500, 2000}; v4 adds M=800 (predicted top1 ~0.75) + M=2500 (predicted top1 ~0.30)
  - HYPOTHESIZED@this-prereg: M=800 top1_at_alpha=0.05 ~ 0.78 (still in band, top-side); M=2500 top1_at_alpha=0.20 ~ 0.30 (still in band, bottom-side)
  - If either edge saturates OR crumbles: cell still HP on the 3 interior M levels (v2-inherited data survives)
- **Axis regime (FIXED PC only):** WM retired due to v2/v3 architectural bug
- **Encoder (FIXED):** hrr_real (chain-grade default)
- **T_cleanup (FIXED):** 1 (v2-inherited; single-step CRLB readout)
- **N (FIXED):** 4096 (v2-inherited)
- **c (FIXED):** PC = 0.60 (v2-inherited empirical escape calibration)
- **beta (FIXED):** 8.0
- **Seeds:** {7, 13, 19} (3-seed chunked)

**Cardinality per seed:** 5 M x 3 alpha x 1 regime = 15 phase points.
- FULL: `EXPECTED_N_UNITS_FULL = 15`
- SMOKE: same 15 (DISCRIMINATOR-SURVIVES-SCALE — smoke uses FULL grid)

### Arms

- **ARM_MECHANISM (PC):** single-bank pattern completion with T=1 modern-Hopfield cleanup on active-masked corrupted codes
- **ARM_RANDOM_FLOOR (PC):** uncorrupted random codes projected to same active mask (chance baseline)

Arms differ at every point via hashlib.sha256 comparison (META_RULE_AF); pre-reg field `arms_differ_verified: bool` reported from smoke gate.

## Discriminator (HP band; META_RULE_L strictly-above-floor)

**HARD_PASS gates (ALL must fire):**
- **HP_PC_MONOTONE:** Spearman rho <= -0.80 (fixed sign; monotone-decreasing in alpha) at ALL 5 M values
  - v2 MEASURED: rho = -1.0 at all 3 M levels; extrapolation to M=800/2500 predicted -1.0 too
- **HP_PC_IN_BAND:** PC top1 in [0.30, 0.90] at ALL 15 (M, alpha) grid points
  - v2 MEASURED: 27/27 v2 points in [0.3555, 0.7300]; extension edges predicted still in band
- **HP_CROSS_SEED_TIGHT:** cross-seed cv < 0.05 on top1 at each (M, alpha)
  - v2 MEASURED: max cv = 0.023 across 9 v2 points; margin 2x
- **HP_RANDOM_FLOOR:** ARM_RANDOM_FLOOR top1 < 0.05 at every point (chance)
  - v2 MEASURED: random floor 0.001 everywhere; margin 50x
- **HP_CARDINALITY:** observed_n_units == 15 per seed (META_RULE_H)
- **HP_ARMS_DIFFER:** mechanism vs random hash != identical at every point (META_RULE_AF)
- **HP_POSITIVE_CONTROL:** PC at M=2000 alpha=0.10 in-band [0.30, 0.90]
  - v2 MEASURED: mean(0.5070, 0.5300, 0.5075) = 0.515; well within band

**HARD_FAIL classes (any triggers verdict flip):**
- **HF_SATURATION:** any point with top1 > 0.90 => PC saturation at that regime (unlikely per v2 MEASURED but the extended M=800 edge could push top-side; if so cell reports HF and PC axis needs regime nudge)
- **HF_CRUMBLE:** any point with top1 < 0.20 => too much capacity pressure (unlikely per v2 MEASURED but M=2500 edge could push bottom-side)
- **HF_CARDINALITY_BREACH:** observed < expected
- **HF_POSITIVE_CONTROL_PC:** PC at M=2000 alpha=0.10 outside [0.30, 0.90]
- **HF_ARMS_IDENTICAL:** mechanism == random hash (arm bug)
- **HF_RANDOM_FLOOR_ABOVE_CHANCE:** any point rnd >= 0.05 (mask-leak or similar)

## Positive control (META_RULE_BC; empirical calibration)

- **PC:** hrr_real @ N=4096 M=2000 alpha=0.10 c=0.60 T=1 -> top1 in [0.30, 0.90]
  - MEASURED@ v2 seed_7=0.5070, seed_13=0.5300, seed_19=0.5075; mean=0.515

## Test-design gates (§15)

- **Gate A (effective-vs-nominal-parameter-audit):** N/A (no partition routing; single-primitive)
- **Gate B (discriminating_fraction):** predicted_accuracy_per_point per v2 MEASURED calibration = 27/27 in discriminating band [0.30, 0.90] = 100% >> 30%. Extension edges (M=800, M=2500) predicted in-band; if either edge lands out-of-band, that's HF but 9/15 interior points are v2-inherited HP-clean.
- **Gate C (signal_shape_compatibility_audit):** N/A (single primitive; no composition edges)
- **Gate D (reproduce_prior_chain_grade_result_as_positive_control):** ARM_MECHANISM AT (M=2000, alpha=0.10) reproduces v2 seed_{7,13,19} PC MEASURED = mean 0.515 +/- 0.10 tolerance. If v4 seed_{7,13,19} MEASURED at (M=2000, alpha=0.10) deviates > 0.10 from mean 0.515, cell is invocation-mismatch => HF_POSITIVE_CONTROL_PC.
- **Gate E (functional_requirement_decomposition_present):** functional requirement = "sparsity acts as monotone-decreasing lever on PC recall at capacity-pressure regime"; primitive = HRR-real modern-Hopfield single-step cleanup at active-sparsity-mask.

## Meta rules composed

META_RULE_AC (MEASURED@/HYPOTHESIZED@/THEORETICAL@ tagging), _AE (locked prereg constants), _AF (arms-must-differ), _AG (baseline-in-band), _AH (atomic metrics write via tmp_replace), _AO (per-arm HP scope: MECHANISM only), _AT (composes v2 MEASURED PC data), _AV, _H (cardinality_ok mandatory), _J (per-unit failure-class; halt on any per-point exception), _L (HP strictly above floor), _Q, _BC (positive control gate), BROKEN-PC-BEFORE-STRUCTURAL-FRAMING (v4 cleanly clears this gate — PC-only means no WM structural framing possible).

## Cell chunking + defensive patterns

- `cell_chunked: true` (one seed per sibling file; 3-way parallelizable)
- `start_marker_written: true` (STARTED metrics written at main() entry)
- `crash_diagnostic_present: true` (outer try except Exception writes IMPORT_CRASH sentinel; SystemExit + KeyboardInterrupt raised)
- `heartbeat_present: true` (per-point flush prints during sweep)
- `defensive_error_checking: passed_all_4_patterns`
- `final_metrics_atomicity: tmp_replace` (metrics.json.tmp -> os.replace)
- `progress_logging: print_flush_true` (per-point and per-seed flushed)

## PROT / dispatch

- **PROT-018:** anchor `_n4096` suffix binds to script `N_DIM_FULL = 4096` (verified in core)
- **PROT-019:** `_n4096` requires `--timeout >= 3600s` per FULL seed
- **PROT-020:** torch imported at module-level (marker present)
- **Queue routing:** CPU-eligible; per USER 2026-07-01 SMOKE runs on `local_cpu_queue`; FULL routes to `remote_cpu_queue` via Orchestrator (harness push-DENIED to hdi_exp_dev)
- **Selftest timeout:** 120s
- **Smoke timeout:** 900s (5 M x 3 alpha = 15 pts x ~30s/pt at N=4096 substrate = ~450s wall; 2x margin)
- **FULL timeout per seed:** 3600s (PROT-019 minimum)

## HYPOTHESIZED landing

**Most likely (P >= 0.85):** monotonicity CG at all 5 M levels; sparsity_range in [0.15, 0.30]; PC positive-control 0.515 +/- 0.05; all 15 points in [0.30, 0.85]; **HARD_PASS_SPARSITY_PC_AXIS_CG**.

**Backup case 1 (P ~ 0.10):** M=800 alpha=0.05 saturates > 0.90 (edge-of-band). Cell reports HF_SATURATION with 1 point breach; v4.1 would trim to M >= 1000.

**Backup case 2 (P ~ 0.05):** M=2500 alpha=0.20 crumbles < 0.20 (edge-of-band). Cell reports HF_CRUMBLE with 1 point breach; v4.1 would trim to M <= 2000.

**In either backup case:** the 9 v2-inherited interior points still MEASURED HP-clean; a v4.1 trim would land quickly.

## Chunked architecture

- Sibling files: `exp_substrate_sparsity_free_axis_v4_pc_only_seed_{7,13,19}.py`
- Shared core: `experiments/_sparsity_free_axis_v4_pc_only_core.py`

## Author

hdi_exp_dev 2026-07-01 (Opus 4.7 1M; PC-only v4 per prior cell-author Option D; v2 PC data supports HP-clean; WM regime deferred to v5 architectural fix)
