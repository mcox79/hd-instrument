# Substrate operational wall — alpha-fine × f-noise cross sweep (Cell D v2 ρ=0 baseline)

**Date filed:** 2026-07-02
**Author:** hdi_exp_dev
**Anchor family:** `substrate_operational_wall_alpha_fine_sweep_v1`
**Sibling cells (per-seed chunked, PROT-021):**
- `exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7.py`
- `exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_13.py`
- `exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_19.py`

## Purpose

Chain-grade closure of the substrate's **operational saturation wall** at ρ=0 (iid keys, clean-encoding baseline). Twin HFs today (Dim H shape, Dim S metric) both saturated at recall=1.000 for α ≤ 0.30, N=8192 because CLT washout at large N erases the discriminator per the Sonnet 2x drill (`notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md`). This cell tests the drill's operational-wall prediction:

- **Discriminating zone predicted at α ∈ [0.85, 0.92]** (clean queries)
- **Cheap wall probe via noise arm f ∈ [0.40, 0.43]** at any α (mandatory-noise-arm discipline)
- **Spin-glass collapse predicted α > 0.92**

Complements the Löwe correlated-key CG (α_c(ρ) for ρ>0) — this is the ρ=0 baseline.

## Load-bearing framing

This cell is dual-purpose:
1. **CG the substrate's ρ=0 operational wall** (empirical validation of drill Regime Table).
2. **Empirically validate the CLT-washout theory + mandatory-noise-arm discipline** — every future Dim-X sweep MUST use this cell as the calibration reference for margin computation.

## Cell mechanism

- N=8192, iid bipolar keys/values in {-1, +1}
- Hebbian W = Σᵢ outer(vᵢ, kᵢ)/N (Cell D v2 canonical template, eta=1.0 uniform i.e. no Zipf reinforce)
- Readout: out = sign(q @ W.T); match = argmax(cos(out_n, vals_norm))
- Query noise: BSC bit-flip on bipolar keys at rate f
- Metrics: recall@1 (primary), plus top-5 hit-rate for M3 semantic-retrieval framing

## Sweep grid (per seed)

**α ∈ {0.60, 0.85, 0.90, 0.95} × f ∈ {0.00, 0.20, 0.30, 0.40, 0.43} = 20 core arms**

Per drill Regime Table (empirically calibrated):
- α=0.60 = below wall, structural saturation control
- α=0.85 = predicted DISCRIMINATING (margin 0.104)
- α=0.90 = predicted DISCRIMINATING (margin 0.053)
- α=0.95 = predicted COLLAPSE (margin <0)

Noise arm rationale (drill P3): at α=0.30, f=0.43 gives margin ~0.10 (edge). At α ≥ 0.85, noise arms sharpen the collapse.

**3 seeds × 20 arms = 60 core units total.**

N_QUERIES=800 per arm (statistical power at cliff: σ_min(p=0.5)=0.0177 per binomial-CLT).

## HP conditions (verdict gates)

**HP_STABLE_BELOW_WALL:** at α=0.60 clean (f=0.00), recall ≥ 0.95 (structural saturation confirmed).

**HP_DISCRIMINATING_ZONE_FIRES:** at (α=0.85, f=0.00) OR (α=0.90, f=0.00), recall ∈ [0.30, 0.95] for at least ONE point (transition zone characterized).

**HP_COLLAPSE_ABOVE_WALL:** at α=0.95 clean (f=0.00), recall ≤ 0.50 (spin-glass collapse confirmed).

**HP_NOISE_SHARPENS_WALL:** at (α=0.60, f=0.43), recall ∈ [0.30, 0.85] (cheap-noise wall probe fires per drill P3). This validates the mandatory-noise-arm discipline for future Dim-X cells.

## HF conditions

**HF_WALL_MISPLACED:** all α ∈ {0.85, 0.90} arms saturate at recall ≥ 0.98 (clean) AND all collapse arms crash to <0.10 — implies wall is elsewhere (Sonnet drill Regime Table falsified).

**HF_NO_TRANSITION:** at α=0.90 clean recall ≥ 0.98 AND α=0.95 clean recall <0.10 (extremely narrow cliff; wider grid needed).

**HF_STRUCTURAL_INFRA:** baseline (α=0.60, f=0.00) < 0.85 (implementation bug); OR bit-identical arm signatures (META_RULE_AF); OR CARDINALITY_BREACH len(core) ≠ 20.

## HP_SCOPE (§5b)

All HP/HF gates apply to the aggregated mechanism arms above. No bare-baseline arm inheriting chain-grade gates.

## SCHEMA-VET pre-dispatch fields

- `cardinality_ok`: bool (EXPECTED_N_UNITS=20 per seed; verdict enforces)
- `arms_differ_verified`: bool (SHA256 hash of hits vector per arm; §6 META_RULE_AF)
- `final_metrics_atomicity`: "tmp_replace" (§7 META_RULE_AH)
- `crlb_floor_computed`: 0.0177 (binomial-CLT at N_Q=800, p=0.5)
- `crlb_formula_reference`: "sigma_min = sqrt(p(1-p)/N_Q)"
- `discriminator_reachability`: True (HP band gaps ≥ 0.15 >> 3σ = 0.053)
- `calibration_check`: "default_ok_for_this_regime" (drill Regime Table is empirical calibration)
- `mechanism_class`: "hebbian_wmatrix_canonical_operational_wall_baseline_rho0"
- `cell_chunked`: True (3 sibling cells, one per seed)
- `start_marker_written`: True
- `crash_diagnostic_present`: True
- `heartbeat_present`: True
- `defensive_error_checking`: "passed_all_4_patterns"
- `sweep_alignment_verdict`: ALIGNED (all sweep params are directly consumed by mechanism; no effective/nominal mismatch)
- `discriminating_fraction`: 0.30 (6/20 arms predicted DISCRIM per drill calibration; ≥ 0.30 Gate B floor)
- `composition_edges`: []  (single-primitive cell; no composition)
- `positive_control_arms`: (α=0.60, f=0.00) recall ≥ 0.95 = reproduces Cell D v2 sub-wall baseline; tolerance 0.05
- `functional_requirements`: Requirement 1 (store M patterns via Hebbian W); Requirement 2 (retrieve clean & noisy query); Requirement 3 (predict cliff regime per drill wall theory)
- `progress_logging`: "print_flush_true"
- `run_mode` default: "full" (explicit `--smoke` for smoke; `--self-test` for selftest)

## Predicted per-arm regime (Gate B calibration)

| α | f | predicted regime | expected recall |
|---|---|------------------|-----------------|
| 0.60 | 0.00 | SAT | ~1.00 |
| 0.60 | 0.20 | SAT | ~1.00 |
| 0.60 | 0.30 | SAT | ~0.95 |
| 0.60 | 0.40 | SAT_EDGE | 0.85-1.00 |
| 0.60 | 0.43 | DISCRIM | 0.40-0.65 (drill P3) |
| 0.85 | 0.00 | DISCRIM | 0.95-0.999 (drill Regime Table) |
| 0.85 | 0.20 | DISCRIM | 0.60-0.90 |
| 0.85 | 0.30 | DISCRIM_LOW | 0.30-0.70 |
| 0.85 | 0.40 | COLLAPSE | 0.05-0.30 |
| 0.85 | 0.43 | COLLAPSE | 0.05-0.20 |
| 0.90 | 0.00 | DISCRIM | 0.30-0.70 (drill P2) |
| 0.90 | 0.20 | DISCRIM_LOW | 0.20-0.50 |
| 0.90 | 0.30 | COLLAPSE | 0.05-0.30 |
| 0.90 | 0.40 | COLLAPSE | <0.20 |
| 0.90 | 0.43 | COLLAPSE | <0.15 |
| 0.95 | 0.00 | COLLAPSE | <0.30 (drill Regime Table) |
| 0.95 | 0.20 | COLLAPSE | <0.20 |
| 0.95 | 0.30 | COLLAPSE | <0.15 |
| 0.95 | 0.40 | COLLAPSE | <0.10 |
| 0.95 | 0.43 | COLLAPSE | <0.10 |

SAT: 4/20; DISCRIM: 6/20; COLLAPSE: 10/20 → **discriminating_fraction = 0.30** (Gate B floor 0.30).

## Wall-time estimate

Per drill notes: W-matrix at N=8192 (256 MB float32) build ~1s + readout at N_Q=800 × N × M ~ 5-15s per arm. 20 arms × ~10s = ~200s per seed sweep + build overhead + smoke preview arm at N=8192. Total per-seed FULL wall ~15-25 min. Timeout 3600s (1h) safe headroom.

## Dispatch plan

- **Queue:** remote_cpu_queue (numpy CPU-bound; matmul 8192×8192)
- **Timeout:** 3600s per seed cell
- **Smoke gate:** local_cpu_queue single-seed smoke (seed_7 at N=1024, 5 arms) + full-N=8192 preview arms at (α=0.60, f=0.0), (α=0.85, f=0.0), (α=0.95, f=0.0), (α=0.60, f=0.43) — MUST show discriminator fires at PREVIEW before FULL dispatch (Discriminator-must-survive-scale pattern C).

## Citations

- Sonnet 2x drill: `notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md` (drill Regime Table THEORETICAL@drill_line_118-133)
- Löwe correlated-key CG: `notes/research_correlated_key_capacity_hopfield_fhrr_2026-07-01.md` (α_c(ρ) formula)
- Amit-Gutfreund-Sompolinsky 1985 CITED (α_c = 0.138 classical wall)
- Berry-Esseen CITED (CLT error bound O(1/√N))
- Substrate Cell D v2 template: `exp_distributional_shape_zipfian_v3_hebbian_wmatrix_canonical_seed_7.py`

## Numbers tagged (META_RULE_AC)

- crlb_floor 0.0177  THEORETICAL@binomial-CLT at N_Q=800 p=0.5
- drill margin at α=0.85 = 0.104  CITED@notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md:line_129
- drill discriminating zone α ∈ [0.85, 0.92]  CITED@same:line_24
- CLT washout O(1/√8192)=0.011  THEORETICAL@Berry-Esseen
