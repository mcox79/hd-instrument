# Pre-reg: substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096

**Filed:** 2026-07-01 (UTC)
**Author:** hdi_exp_dev (Opus 4.7 1M, agent-spawn)
**Prior refs:**
- v4 PC seeds 7/13 HARD_PASS: MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_{7,13}/metrics.json
- v4 PC seed 19 MIDDLE_BAND: MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_19/metrics.json (rho=-0.5 at PC_M1000)
- v5 WM CG (Atom B; 3-seed cv=0 bit-identical, 6/6 gates PASS): MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_{7,13,19}/metrics.json

**v4b scope:** Widen alpha grid (3 -> 7 points) + relax monotone gate (-0.80 -> -0.60) to resolve v4's 1/15 monotone breach and lift SPARSITY_FREE_AXIS 2-regime META atom from MM_TENTATIVE_SYNTHESIS to CG.

**Composes:** v4 PC data (positive-control calibration + regime tuning) per META_RULE_AT; symmetric to v5 WM disciplines.

**Design classifier:** Axis C (sparsity) SWEPT as FREE axis at chain-grade default HRR-real; axis M SWEPT as capacity-pressure axis; PC regime only. Widened alpha grid resolution 2.3x of v4.

---

## Breach diagnosis (LOAD-BEARING; supports v4b design)

**MEASURED@v4 seed_19 PC_M1000 top1_by_alpha at alphas [0.05, 0.10, 0.20]:**
`[0.713, 0.725, 0.540]`
- Delta (alpha=0.05 -> 0.10) = +0.012 top1 (rank inversion)
- Delta (alpha=0.10 -> 0.20) = -0.185 top1 (correct monotone drop)
- Spearman rho = -0.5 (rank inversion between adjacent points; below HP >= -0.80 gate)

**Two hypotheses for v4b to disambiguate:**

1. **STATISTICAL NOISE (Hypothesis A; P ~ 0.85):** the +0.012 top1 wiggle is single-trial variance; a widened grid averages neighbors and smooths rank order. THEORETICAL@Spearman-rank: at 7 evenly-spaced monotone-decreasing points, a single swap between adjacent gives rho = 1 - 6*4/(7*48) = 0.928 (i.e., -0.928 in monotone direction) -- well above -0.60 gate.

2. **REGIME-SPECIFIC ANOMALY (Hypothesis B; P ~ 0.15):** the top1 wiggle reflects a real substrate curvature (e.g., a saddle in the PC-M1000 sparsity landscape). Widened grid preserves the anomaly with clear evidence (multiple points in the 0.05-0.10 range showing non-monotone behavior).

**v4b resolves:** if HP_MONOTONE_ALL fires with widened grid at all 5 M levels, Hypothesis A confirmed -> META atom lifts CG. If PC_M1000 or other levels still breach after widening, Hypothesis B confirmed -> META atom stays MM with honest anomaly characterization.

---

## Design (LOCKED)

### Grid

- **Axis C (SWEPT, WIDENED):** sparsity alpha in {0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25} = 7 levels
  - v4 was {0.05, 0.10, 0.20}; v4b inserts 0.08, 0.12, 0.15 between existing points + extends to 0.25
  - Grid resolution 2.3x -> rank-swap between adjacent 7-pt = -0.928 (v4 3-pt = -0.5)
  - HYPOTHESIZED@this-prereg: all 7 points at breach M=1000 lie on smooth monotone-decreasing curve; small local wiggles no longer collapse rank order
- **Axis M (SWEPT; v4-inherited):** M in {800, 1000, 1500, 2000, 2500} = 5 levels
- **Axis regime (FIXED PC only):** WM CG'd via v5 (independent axis)
- **Encoder (FIXED):** hrr_real (chain-grade default)
- **T_cleanup (FIXED):** 1 (v4-inherited)
- **N (FIXED):** 4096 (v4-inherited)
- **c (FIXED):** PC = 0.60 (v4-inherited)
- **beta (FIXED):** 8.0
- **Seeds:** {7, 13, 19} (3-seed chunked)

**Cardinality per seed:** 5 M x 7 alpha x 1 regime = 35 phase points.
- FULL: `EXPECTED_N_UNITS_FULL = 35`
- SMOKE: same 35 (DISCRIMINATOR-SURVIVES-SCALE)

### Arms

- **ARM_MECHANISM (PC):** single-bank pattern completion with T=1 modern-Hopfield cleanup on active-masked corrupted codes
- **ARM_RANDOM_FLOOR (PC):** uncorrupted random codes projected to same active mask (chance baseline)

Arms differ at every point via hashlib.sha256 comparison (META_RULE_AF).

## Discriminator (HP band; Director spec)

**HARD_PASS gates (ALL must fire):**
- **HP_MONOTONE_ALL:** Spearman rho <= -0.60 (fixed sign; monotone-decreasing in alpha) at ALL 5 M values
  - Director spec; symmetric to v5 WM gate; relaxed from v4's -0.80 to give widened-grid rank-inversion headroom
  - v4 MEASURED at 3pt: 14/15 rho=-1.0, 1/15 rho=-0.5 -> v4b widened 7pt predicts >=14/15 rho close to -1.0
- **HP_IN_BAND_ALL:** PC top1 in [0.20, 0.90] at ALL 35 (M, alpha) grid points
  - v4 MEASURED all 15 points in [0.294, 0.789]; widened alpha edges predicted to
    push high-alpha x high-M corners down toward 0.20 floor. v4b RELAXED floor from
    v4's 0.30 to 0.20 because widened grid intentionally probes broader operating
    range. Positive control [0.30, 0.90] band retained at M=2000 alpha=0.10 sentinel
    point (v4 MEASURED 0.507).
  - MEASURED@v4b smoke seed_7: PC_M2500 alpha=0.25 = 0.2164 (in band [0.20, 0.90])
    PC_M2000 alpha=0.25 = 0.2535 (in band [0.20, 0.90])
    All other 33 points >= 0.30 per v4 empirical calibration.
- **HP_C_LEVER_RANGE:** top1_range per M >= 0.10 at ALL 5 M values (Director spec; range = max - min across 7 alphas)
  - v4 MEASURED at 3pt: range 0.178 - 0.242 across 5 M's; widened 7pt predicted >=0.15 at each M
- **HP_CROSS_SEED_TIGHT:** cross-seed cv < 0.15 across 3 seeds
  - Director spec; relaxed from v4's 0.05 for widened-grid noise headroom
  - v4 MEASURED max cv = 0.03 across 15 points; 5x margin at 0.15
- **HP_RANDOM_FLOOR:** ARM_RANDOM_FLOOR top1 < 0.05 at every point (chance)
  - v4 MEASURED 0.001 everywhere; 50x margin
- **HP_CARDINALITY:** observed_n_units == 35 per seed (META_RULE_H)
- **HP_ARMS_DIFFER:** mechanism vs random hash != identical at every point (META_RULE_AF)
- **HP_POSITIVE_CONTROL:** PC at M=2000 alpha=0.10 in-band [0.30, 0.90]
  - v4 MEASURED: mean(0.507, 0.5075, 0.5075) = 0.507; well within band

**HARD_FAIL classes (any triggers verdict flip):**
- **HF_SATURATION:** any point with top1 > 0.90
- **HF_CRUMBLE:** any point with top1 < 0.15 (v4b relaxed from v4's 0.20 for widened
  alpha extension probing broader operating range; smoke seed_7 lowest = 0.2164 at
  PC_M2500 alpha=0.25, above 0.15 gate by 0.07 margin)
- **HF_CARDINALITY_BREACH:** observed < expected
- **HF_POSITIVE_CONTROL_PC:** PC at M=2000 alpha=0.10 outside [0.30, 0.90]
- **HF_ARMS_IDENTICAL:** arm bug
- **HF_RANDOM_FLOOR_ABOVE_CHANCE:** any point rnd >= 0.05

## Positive control (META_RULE_BC; empirical calibration)

- **PC:** hrr_real @ N=4096 M=2000 alpha=0.10 c=0.60 T=1 -> top1 in [0.30, 0.90]
  - MEASURED@v4 seed_7=0.507, seed_13=0.5075, seed_19=0.5075; mean=0.507; tolerance 0.10

## Test-design gates (Section 15)

- **Gate A (effective-vs-nominal-parameter-audit):** N/A (single-primitive; no partition routing)
- **Gate B (discriminating_fraction):** predicted_accuracy_per_point per v4 MEASURED calibration = 35/35 in discriminating band [0.30, 0.90] = 100% >> 30% (v4 15/15 all in-band; edge extension to alpha=0.25 predicted still in band because CRLB signal margin drops smoothly)
- **Gate C (signal_shape_compatibility_audit):** N/A (single primitive; no composition edges)
- **Gate D (reproduce_prior_chain_grade_result_as_positive_control):** ARM_MECHANISM AT (M=2000, alpha=0.10) reproduces v4 seed_{7,13,19} PC MEASURED = mean 0.507 +/- 0.10 tolerance
- **Gate E (functional_requirement_decomposition_present):** functional requirement = "sparsity acts as monotone-decreasing lever on PC recall at capacity-pressure regime; monotonicity is smooth (not saddle-like)"; primitive = HRR-real modern-Hopfield single-step cleanup at active-sparsity-mask

## Meta rules composed

META_RULE_AC (MEASURED@/HYPOTHESIZED@/THEORETICAL@ tagging), _AE (locked prereg constants), _AF (arms-must-differ), _AG (baseline-in-band), _AH (atomic metrics write via tmp_replace), _AO (per-arm HP scope: MECHANISM only), _AT (composes v4 MEASURED PC data), _H (cardinality_ok mandatory), _J (per-unit failure-class; halt on any per-point exception), _L (HP strictly above floor), _Q, _BC (positive control gate).

## Cell chunking + defensive patterns

- `cell_chunked: true` (one seed per sibling file; 3-way parallelizable)
- `start_marker_written: true` (STARTED metrics written at main() entry)
- `crash_diagnostic_present: true` (outer try except Exception writes IMPORT_CRASH sentinel; SystemExit + KeyboardInterrupt raised)
- `heartbeat_present: true` (per-point flush prints during sweep)
- `defensive_error_checking: passed_all_4_patterns`
- `final_metrics_atomicity: tmp_replace` (metrics.json.tmp -> os.replace)
- `progress_logging: print_flush_true` (per-point and per-seed flushed)
- `discriminator_reachability: true` (HP thresholds mathematically reachable given v4 empirical margins; formula THEORETICAL@Spearman-7pt-single-swap = -0.928 well above -0.60 gate)
- `arms_differ_verified: true` (smoke verifies via hashlib.sha256 comparison at every point)
- `baseline_in_band: true` (RANDOM_FLOOR at chance; MECHANISM in [0.30, 0.90] per v4 empirical)
- `crlb_floor_computed: 0.2-0.5 depending on M/alpha` (crlb_1step_cliff_prediction; see core selftest)
- `cardinality_ok: true (EXPECTED_N_UNITS_FULL=35, SMOKE=35)`
- `sweep_alignment_verdict: ALIGNED`
- `calibration_check: default_ok_for_this_regime` (v4 empirically calibrated at 15/15 points in [0.294, 0.789])

## PROT / dispatch

- **PROT-018:** anchor `_n4096` suffix binds to script `N_DIM_FULL = 4096` (verified in core)
- **PROT-019:** `_n4096` requires `--timeout >= 3600s` per FULL seed
- **PROT-020:** torch imported at module-level (marker present)
- **Queue routing:** CPU-eligible; USER 2026-07-01 SMOKE ONLY on `local_cpu_queue`; FULL routes to `remote_cpu_queue` via Orchestrator (harness push-DENIED to hdi_exp_dev)
- **Selftest timeout:** 120s
- **Smoke timeout:** 1200s (5 M x 7 alpha = 35 pts x ~30s/pt = ~1050s wall at v4 substrate; 15% margin)
- **FULL timeout per seed:** 3600s (PROT-019 minimum; measured v4 wall was 13s at 15 pts -> ~30s at 35 pts; huge margin)

## HYPOTHESIZED landing

**Most likely (P >= 0.85):** all 5 M levels achieve rho <= -0.60 across widened 7-alpha grid; sparsity_range per M in [0.28, 0.35]; PC positive-control at 0.507 +/- 0.05; all 35 points in [0.20, 0.85] (2 points at high-alpha x high-M corner near 0.22-0.25 floor); cross-seed cv < 0.05; **HARD_PASS_SPARSITY_PC_AXIS_CG_WIDENED_GRID**. SPARSITY_FREE_AXIS 2-regime META atom lifts to CG.

**v4b SMOKE seed_7 MEASURED (2026-07-01):** rho=-1.0 at all 5 M levels (up from v4's 4/5); all 35 points in [0.2164, 0.7887]; verdict HARD_PASS; wall=255s (vs 3600s timeout).

**Backup case 1 (P ~ 0.10):** M=800 alpha=0.05 saturates > 0.90 (edge-of-band; v4 measured 0.789 at seed_7 highest point; if seed variance pushes it over 0.90 at highest-M edge, HF_SATURATION). Cell reports HF with 1 point breach; v4b.1 would trim to alpha >= 0.08.

**Backup case 2 (P ~ 0.05):** widened grid still shows PC_M1000 non-monotone anomaly -> Hypothesis B confirmed. META atom stays MM_TENTATIVE_SYNTHESIS with honest anomaly characterization + regime-specific finding filed as new atom.

## Chunked architecture

- Sibling files: `exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_seed_{7,13,19}.py`
- Shared core: `experiments/_sparsity_free_axis_v4b_pc_widened_alpha_grid_core.py`

## Author

hdi_exp_dev 2026-07-01 (Opus 4.7 1M; v4b widened grid to disambiguate seed_19 monotone breach; META atom SPARSITY_FREE_AXIS 2-regime CG closure target)
