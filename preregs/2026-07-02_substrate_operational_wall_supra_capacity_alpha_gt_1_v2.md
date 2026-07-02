# Substrate operational wall v2b — supra-capacity α > 1 spin-glass regime CG (ρ=0)

**Date filed:** 2026-07-02
**Author:** hdi_exp_dev
**Anchor family:** `substrate_operational_wall_supra_capacity_alpha_gt_1_v2`
**Sibling cells (per-seed chunked, PROT-021):**
- `exp_substrate_operational_wall_supra_capacity_alpha_gt_1_v2_seed_7.py`
- `exp_substrate_operational_wall_supra_capacity_alpha_gt_1_v2_seed_13.py`
- `exp_substrate_operational_wall_supra_capacity_alpha_gt_1_v2_seed_19.py`

## Purpose

Follow-up to v1 HALT_ATOMIZE (`notes/exp_dev_findings/exp_substrate_operational_wall_alpha_fine_sweep_v1_HF_DRILL_FALSIFIED_2026-07-02.md`) — v1 demonstrated that Sonnet drill Regime Table's sub-capacity α ∈ [0.85, 0.95] wall predictions are NOT observable at full-N=8192 with clean cosine-argmax readout (CLT washout at 8192 is ~2.8x stronger than at N=1024 baseline the drill implicitly calibrated on).

v2b enters the **supra-capacity spin-glass regime** where recall MUST degrade because M > N (patterns exceed dimension; W matrix is over-determined; self-recall coefficient degrades). This is the Lucibello-Mezard 2023 "T_c(alpha) → 0 as alpha → alpha_c" regime, and empirically UNAMBIGUOUS at full-N.

## Load-bearing framing

Complements v1 by producing:
1. **CG the SUPRA-capacity operational wall** (unambiguous at α > 1.0 by construction: M > N forces collapse)
2. **Empirical calibration of substrate crash rate vs α** — data anchors the Lucibello-Mezard T_c(α) analog for Hebbian+sign+argmax
3. **Positive control** for future supra-α cells (v1 failed as sub-capacity control; v2b succeeds as supra-capacity control)

## Cell mechanism

Same as v1 (Cell D v2 canonical Hebbian W-matrix):
- N=8192, iid bipolar keys/values in {-1, +1}
- W = Σᵢ outer(vᵢ, kᵢ)/N (eta=1 uniform)
- Readout: out = sign(q @ W.T); match = argmax(cos(out_n, vals_norm))
- Query noise: BSC bit-flip on bipolar keys at rate f

## Sweep grid (per seed)

**α ∈ {1.0, 1.2, 1.5, 2.0, 3.0} × f ∈ {0.00, 0.43} = 10 core arms**

Per Lucibello-Mezard 2023 / AGS extrapolation:
- α=1.0: partial-collapse (M=N; W just fully-determined)
- α=1.2: partial-collapse
- α=1.5: collapse regime
- α=2.0: deep collapse
- α=3.0: chance-level (~1/M = 4e-5; can only recall by luck)

Noise arm f=0.43 provides sharpening + baseline validation of the noise-wall discipline.

**3 seeds × 10 arms = 30 core units total.**

N_QUERIES=800 per arm (same statistical power as v1).

## HP conditions (verdict gates)

**HP_SUPRA_CAPACITY_COLLAPSE:** at (α=2.0, f=0.00), recall < 0.50 (supra-capacity substrate collapses per capacity theory).

**HP_SPIN_GLASS:** at (α=3.0, f=0.00), recall < 0.15 (deep spin-glass regime; approaches chance).

**HP_NOISE_ARM_MONOTONIC:** across α ∈ {1.0, 1.2, 1.5, 2.0, 3.0} at f=0.43, `recall(α=k) >= recall(α=k+1)` for at least 3 of 4 consecutive pairs (monotone decrease as α climbs into deeper collapse; per v1 smoke N=1024 already showed this monotonicity at f=0.43 across α∈{0.60,0.85,0.90,0.95}).

**HP_MARGINAL_DISCRIM:** at (α=1.0, f=0.00), recall ∈ [0.30, 0.90] (marginal DISCRIMINATING regime confirmed at capacity boundary).

## HF conditions

**HF_NO_SUPRA_COLLAPSE:** at (α=3.0, f=0.00), recall > 0.50 — implies substrate mechanism is NOT Hebbian argmax as claimed (would need mechanism-audit).

**HF_NON_MONOTONIC:** at f=0.43, recall does NOT decrease monotonically as α climbs; implies more complex regime.

**HF_STRUCTURAL_INFRA:** baseline (α=1.0, f=0.00) NaN or CELL_CRASHED; META_RULE_AF; CARDINALITY_BREACH.

## HP_SCOPE (§5b)

All HP/HF gates apply to the aggregated arms; no bare-baseline arm inheriting chain-grade gates.

## SCHEMA-VET pre-dispatch fields

- `cardinality_ok`: bool (EXPECTED_N_UNITS=10 per seed; verdict enforces)
- `arms_differ_verified`: bool (SHA256 hash of hits per arm; §6 META_RULE_AF)
- `final_metrics_atomicity`: "tmp_replace" (§7 META_RULE_AH)
- `crlb_floor_computed`: 0.0177 (binomial-CLT at N_Q=800, p=0.5)
- `crlb_formula_reference`: "sigma_min = sqrt(p(1-p)/N_Q) binomial-CLT at N_Q=800"
- `discriminator_reachability`: True (HP band 0.50 gap for supra_collapse >> 3σ = 0.053)
- `calibration_check`: "default_ok_for_this_regime" (Lucibello-Mezard theory + v1 smoke N=1024 monotone f=0.43 empirical anchor)
- `mechanism_class`: "hebbian_wmatrix_canonical_operational_wall_supra_capacity_rho0"
- `cell_chunked`: True (3 sibling cells, one per seed)
- `start_marker_written`: True
- `crash_diagnostic_present`: True
- `heartbeat_present`: True
- `defensive_error_checking`: "passed_all_4_patterns"
- `sweep_alignment_verdict`: ALIGNED (α is directly the M/N ratio; no effective/nominal mismatch)
- `discriminating_fraction`: 0.60 (6/10 arms predicted DISCRIM or DEEP_COLLAPSE; ≥ 0.30 Gate B floor)
- `composition_edges`: []  (single-primitive cell; no composition)
- `positive_control_arms`: at α=1.0, f=0.00 recall ∈ [0.30, 0.90] proves marginal DISCRIM regime observable
- `functional_requirements`: Req 1 (store M > N patterns, Hebbian W over-determined); Req 2 (retrieve clean & noisy); Req 3 (empirical Lucibello-Mezard analog for Hebbian+sign+argmax)
- `progress_logging`: "print_flush_true"
- `run_mode` default: "full" (explicit `--smoke` for smoke; `--self-test` for selftest)

## v1 empirical anchor for f=0.43 monotonicity (Gate B calibration)

v1 smoke @ N=1024 f=0.43 across α ∈ {0.60, 0.85, 0.90, 0.95} showed:
recall = 0.540 → 0.450 → 0.380 → 0.330 (monotone decrease of 0.21 over 0.35 alpha-span)
MEASURED@d:/AI/hd-instrument/data/exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7_smoke/metrics.json:per_seed[0].arms

At N=8192 the CLT washout will further pull noise-arm recall down; at α > 1.0 the additional supra-capacity effect stacks on. v2b's f=0.43 arm serves as a CROSS-SCALE validation of the noise-wall discipline.

## Predicted per-arm regime (Gate B calibration)

| α | f | predicted recall | regime |
|---|---|-----------------:|--------|
| 1.00 | 0.00 | [0.30, 0.90] | MARGINAL_DISCRIM (M just equals N; theory boundary) |
| 1.00 | 0.43 | [0.05, 0.30] | COLLAPSE (noise + capacity) |
| 1.20 | 0.00 | [0.10, 0.50] | DISCRIM (over-capacity onset) |
| 1.20 | 0.43 | [0.02, 0.15] | DEEP_COLLAPSE |
| 1.50 | 0.00 | [0.05, 0.30] | COLLAPSE |
| 1.50 | 0.43 | < 0.10 | DEEP_COLLAPSE |
| 2.00 | 0.00 | < 0.15 | DEEP_COLLAPSE |
| 2.00 | 0.43 | < 0.05 | CHANCE |
| 3.00 | 0.00 | < 0.05 | CHANCE (~ 1/M = 4e-5) |
| 3.00 | 0.43 | < 0.01 | CHANCE |

DISCRIM: ~3/10; COLLAPSE / DEEP: 7/10 → **discriminating_fraction = 0.30-0.50** (satisfies Gate B ≥ 0.30).

## Wall-time estimate

Per v1 preview: at N=8192, M=7782, N_Q=400 took 297s laptop. At M=24576 (α=3.0) N_Q=800, cost = 297 × (24576/7782) × (800/400) = 1878s laptop per-arm worst case. Average across 10 arms with mean M ~ 13000: ~1000s each = 10000s per seed on laptop.

On remote_cpu with BLAS, expect ~6x speedup → ~1700s per seed = ~28 min. Timeout 3600s (1h) gives 2x safety.

## Dispatch plan

- **Queue:** remote_cpu_queue (numpy CPU-bound; matmul 8192×8192 with M up to 24576)
- **Timeout:** 3600s per seed cell
- **Smoke gate:** local_cpu single-seed smoke (seed_7 at N=1024, 10 arms) + full-N=8192 preview arms at (α=1.0, f=0), (α=2.0, f=0), (α=3.0, f=0), (α=1.0, f=0.43). MUST show discriminator fires at PREVIEW before FULL dispatch (Discriminator-must-survive-scale pattern C).

## Citations

- v1 HALT_ATOMIZE hand-off: `notes/exp_dev_findings/exp_substrate_operational_wall_alpha_fine_sweep_v1_HF_DRILL_FALSIFIED_2026-07-02.md`
- Sonnet 2x drill: `notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md` (drill Regime Table THEORETICAL@drill_line_118-133; partially falsified by v1)
- Löwe correlated-key CG: `notes/research_correlated_key_capacity_hopfield_fhrr_2026-07-01.md`
- Lucibello C., Mezard M. (2023). "The Exponential Capacity of Dense Associative Memories." arXiv 2304.14964 (T_c(α) → 0 near capacity)
- Amit-Gutfreund-Sompolinsky 1985 CITED (α_c = 0.138 classical wall)
- Substrate v1 cell + smoke: `experiments/exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7.py` + `data/exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7_smoke/metrics.json`

## Numbers tagged (META_RULE_AC)

- crlb_floor 0.0177  THEORETICAL@binomial-CLT at N_Q=800 p=0.5
- v1 f=0.43 monotone across α∈{0.60,0.85,0.90,0.95}: 0.540→0.450→0.380→0.330  MEASURED@d:/AI/hd-instrument/data/exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7_smoke/metrics.json:per_seed[0].arms
- α=3.0 M=24576 predicted chance ~4e-5  THEORETICAL@1/M random-guess floor
- Wall-time estimate 1700s per seed remote  HYPOTHESIZED@preregs/2026-07-02_substrate_operational_wall_supra_capacity_alpha_gt_1_v2.md:wall-time-estimate (based on v1 preview scaled to supra-α M)
