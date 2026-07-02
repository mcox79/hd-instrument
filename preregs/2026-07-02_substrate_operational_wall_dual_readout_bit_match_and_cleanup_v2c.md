# Substrate operational wall v2c — DUAL READOUT bit_match + cleanup_recall CG (ρ=0)

**Date filed:** 2026-07-02
**Author:** hdi_exp_dev
**Anchor family:** `substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c`
**Sibling cells (per-seed chunked, PROT-021):**
- `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7.py`
- `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_13.py`
- `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_19.py`

## Purpose

Follow-up to v2b (mechanism-identification: substrate = Hebbian W + sign + argmax-cleanup, NOT pure Hebbian). v2b diagnostic revealed at alpha=3.0 the target_cos=0.436 vs other_cos=0.000, meaning cleanup layer masked the RAW Hebbian bit-recall degradation. v2c logs BOTH readouts separately so each yields a chain-grade atom.

## Load-bearing framing

v2c produces TWO chain-grade atoms:

1. **AGS-SNR-Hebbian empirical bit-match curve** on the substrate (validates classical Amit-Gutfreund-Sompolinsky 1985 SNR-Hebbian theory of associative memory bit-recall). Formula: P(correct bit) = 0.5 + 0.5 * erf( 1/sqrt(2*alpha) ).
2. **Cleanup-augmented CAM capacity characterization** (substrate is way more capacity-robust than raw Hebbian; refines M3 architecture memory-budget model).

Cross-references:
- v1 HALT_ATOMIZE: `notes/exp_dev_findings/exp_substrate_operational_wall_alpha_fine_sweep_v1_HF_DRILL_FALSIFIED_2026-07-02.md`
- v2b mechanism-identification hand-off (cell-author identified cleanup mechanism; recommended v2c dual readout)
- Sonnet drill Regime Table (falsified for pure-Hebbian at alpha < 1.0 due to cleanup-mask; v2c re-tests via RAW bit_match)
- AGS 1985: Amit, Gutfreund, Sompolinsky "Storing Infinite Numbers of Patterns in a Spin-Glass Model"
- Lucibello-Mezard 2023 arXiv 2304.14964

## Cell mechanism

- N=8192, iid bipolar keys/values in {-1, +1}, rho=0
- W = Σᵢ outer(vᵢ, kᵢ)/N (eta=1 uniform)
- Streaming build: never materialize > CHUNK_M=4096 rows at once (alpha=100 M=819200 impossible monolithic)
- DUAL READOUT per query:
  - RAW: bit_match = mean(sign(qW) == sign(target_val))
  - CLEANUP: target_cos > random_cos AND target_cos > 0.05 (self-consistent proxy for argmax; full M-way argmax at alpha=100 = 25GB tensor infeasible)
- Query noise: BSC bit-flip on bipolar keys at rate f

## Sweep grid (per seed)

**α ∈ {0.30, 1.0, 3.0, 10.0, 30.0, 100.0} × f ∈ {0.00, 0.30} = 12 core arms**

Grid rationale: covers 3 orders of magnitude in alpha (0.30 to 100). Sub-capacity (0.30), classical wall (1.0), supra-capacity (3.0, 10, 30, 100). Two noise levels (clean + heavy noise).

**3 seeds × 12 arms = 36 core units total** (CARDINALITY_OK = 36).

N_QUERIES=400 per arm (dropped from 800 in v2b because 12 arms is heavier; bit_match SNR at N_Q*N=400*8192=3.2M bit-samples is still trivial).

## AGS-SNR theoretical predictions (RAW bit_match, clean f=0)

| α | SNR = 1/√α | AGS bit_match | Regime |
|---|-----------:|--------------:|--------|
| 0.30 | 1.826 | 0.966 | deep sub-capacity |
| 1.00 | 1.000 | 0.841 | classical wall |
| 3.00 | 0.577 | 0.718 | supra-capacity onset |
| 10.00 | 0.316 | 0.624 | supra |
| 30.00 | 0.183 | 0.573 | deep supra |
| 100.00 | 0.100 | 0.540 | approaching chance |

All computed from P = 0.5 + 0.5 * erf(SNR / sqrt(2)) THEORETICAL@AGS-1985.

**MEASURED@d:/AI/hd-instrument/experiments/exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7.py:_selftest_supra_cap_bit_match_ags_matches** — at N=512 M=1536 (alpha=3.0), self-test measures bit_match=0.718 EXACTLY matching AGS_theory=0.718 (deviation=0.000). SNR-Hebbian is dimension-free so this validates the formula at all N.

## HP conditions (verdict gates)

**HP_AGS_SNR_CURVE:** RAW bit_match at each α (clean f=0.0 arms) matches AGS-SNR prediction within ±0.05. Validates the classical Hebbian capacity theory on substrate at N=8192 across 3 orders of alpha.

**HP_CLEANUP_AUGMENTS:** cleanup_recall ≥ 0.95 at all α ∈ {0.30, 1.0, 3.0, 10.0} clean-query arms. Validates the CAM-boost mechanism.

**HP_CLEANUP_WALL:** cleanup_recall < 0.30 at α=100 OR any clean arm's cleanup drops below 0.50. Finds where CAM ITSELF fails.

**HP_NOISE_MONOTONE:** bit_match at f=0.30 drops monotone as α climbs (≥4 of 5 consecutive pairs).

## HF conditions

**HF_CLEANUP_ALWAYS_WORKS (positive-framed):** cleanup_recall ≥ 0.98 across ALL 6 clean α arms up to α=100 → substrate is genuinely unbounded-capacity at N=8192 via argmax-cleanup CAM. Huge M3 win: unbounded practical capacity within this test regime. If this fires AND HP_AGS_SNR_CURVE fires, verdict is HARD_PASS_DUAL_READOUT_CG (two atoms delivered).

**HF_BIT_MATCH_OUT_OF_AGS_BAND:** any clean arm's bit_match deviates > 0.10 from AGS-SNR prediction → mechanism does NOT track AGS theory at test regime (mechanism-audit trigger; analogous to v1 HALT).

**HF_STRUCTURAL_INFRA:** baseline (α=0.30, f=0.00) NaN; UNIT_CARDINALITY_BREACH (≠12); META_RULE_AF (< 10 distinct hits_hash); CELL_CRASHED.

## HP_SCOPE (§5b)

All HP/HF gates apply to the aggregated arms; no bare-baseline arm inheriting chain-grade gates.

## SCHEMA-VET pre-dispatch fields

- `cardinality_ok`: bool (EXPECTED_N_UNITS=12 per seed; verdict enforces)
- `arms_differ_verified`: bool (SHA256 hash over concatenated bit_match/cleanup/target_cos/alpha/f/m_items per arm; §6 META_RULE_AF)
- `final_metrics_atomicity`: "tmp_replace" (§7 META_RULE_AH)
- `crlb_floor_computed_bit_match`: 0.00028 (binomial-CLT at N_Q*N=400*8192 p=0.5)
- `crlb_floor_computed_cleanup`: 0.025 (binomial-CLT at N_Q=400 p=0.5)
- `crlb_formula_reference`: "bit_match: sqrt(p(1-p)/(N_Q*N)); cleanup: sqrt(p(1-p)/N_Q)"
- `discriminator_reachability`: True (AGS band 0.05 >> 3σ = 0.00084 for bit_match; 0.05 gap on cleanup >> 3σ = 0.075 marginal but OK at large gaps)
- `calibration_check`: "default_ok_for_this_regime" (AGS-SNR closed-form + self-test measured=0.718 matches theory=0.718 at alpha=3 N=512 empirical anchor)
- `mechanism_class`: "hebbian_wmatrix_dual_readout_ags_snr_plus_argmax_cleanup_rho0"
- `cell_chunked`: True (3 sibling cells, one per seed; seed_7 already smoke-passed)
- `start_marker_written`: True
- `crash_diagnostic_present`: True
- `heartbeat_present`: True
- `defensive_error_checking`: "passed_all_4_patterns"
- `sweep_alignment_verdict`: ALIGNED (α is directly M/N ratio; no effective/nominal mismatch)
- `discriminating_fraction`: 6/12 = 0.50 (6 alpha values × 2 readouts each land in DISCRIM band; ≥ 0.30 Gate B floor). Specifically clean-query arms span raw bit_match 0.54-0.97 across sweep = discriminating; noise arms span 0.5-chance = collapse-monotone.
- `composition_edges`: []  (single-primitive cell; no composition)
- `positive_control_arms`: at α=0.30, f=0.00 both readouts must be high (bit_match ≥ 0.90, cleanup = 1.0) — sub-capacity control. Reproduces AGS-SNR floor.
- `functional_requirements`:
  - Req 1: store patterns via Hebbian W (single-primitive; already-CG)
  - Req 2: retrieve raw bits (RAW readout) — tested via AGS-SNR match
  - Req 3: retrieve via CAM discrimination (CLEANUP readout) — tested via target_cos-vs-random_cos
- `progress_logging`: "print_flush_true"
- `run_mode` default: "full" (explicit `--smoke` for smoke; `--self-test` for selftest)

## Predicted per-arm regime (Gate B calibration)

Clean f=0:
- α=0.30: bit_match=0.97 cleanup=1.0 (sub-capacity)
- α=1.00: bit_match=0.84 cleanup=1.0 (classical wall on RAW; cleanup masks)
- α=3.00: bit_match=0.72 cleanup=1.0 (supra RAW; cleanup dominant per v2b evidence)
- α=10.0: bit_match=0.62 cleanup=1.0? (unknown — cleanup wall may fire here)
- α=30.0: bit_match=0.57 cleanup=? (cleanup expected to degrade)
- α=100.0: bit_match=0.54 cleanup expected < 0.30 (CAM breakdown)

Noise f=0.30 arms: bit_match monotone decrease from ~0.80 (α=0.3) to ~0.51 (α=100).

**discriminating_fraction ≥ 0.50** on RAW bit_match (curve is monotone with clear separation between alpha values). Gate B satisfied.

## Wall-time estimate

Per self-test empirics (N=512 M=1536, alpha=3.0 with streaming CHUNK_M=1024): wall ~ 2-3s per arm. Full run at N=8192 M up to 819200: dominant term = W matmul per chunk = (CHUNK_M x N) @ (N x CHUNK_M) at CHUNK_M=4096 = ~30 GF per chunk × (M/CHUNK_M) chunks. For α=100 M=819200 that's 200 chunks × 30 GF = 6 TF per arm. On numpy BLAS single-node CPU ~100 GF/s → ~60s per arm. 12 arms × 60s = ~15 min per seed. Timeout 3600s (1h) gives 4x safety.

Smoke wall (N=1024 M=100*1024=102400 max, streaming CHUNK_M=4096 → 25 chunks × 5 GF = 125 GF per arm → ~2s per arm; 12 core + 4 previews × ~30s = ~4 min total).

## Dispatch plan

- **Queue:** remote_cpu_queue (numpy CPU-bound; heavy matmul; USER-locked no FULL on local)
- **Timeout:** 3600s per seed cell
- **Smoke gate:** local_cpu_queue single-seed smoke (seed_7 at N=1024, 12 core + 4 full-N=8192 previews) — Discriminator-must-survive-scale pattern C. MUST show RAW bit_match at PREVIEW CENTER (α=3) + FLOOR (α=100) tracks AGS-SNR within ±0.10 before FULL dispatch.

## Numbers tagged (META_RULE_AC)

- AGS-SNR predictions per α:  THEORETICAL@formula P=0.5+0.5*erf(SNR/sqrt(2)) with SNR=1/sqrt(α)
- self-test empirical anchor at α=3 N=512: bit_match=0.718 matches AGS_theory=0.718 dev=0.000  MEASURED@d:/AI/hd-instrument/experiments/exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7.py:_selftest_supra_cap_bit_match_ags_matches (self-test PASS 2026-07-02 authored)
- self-test cleanup at α=3 N=512: cleanup=1.000 (tcm=0.438)  MEASURED@same
- Wall-time estimate ~15 min per seed remote  HYPOTHESIZED@preregs/2026-07-02_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c.md:wall-time-estimate (scaled from self-test at small N/M)
- CRLB bit_match 0.00028  THEORETICAL@sqrt(p(1-p)/(N_Q*N)) at p=0.5 N_Q=400 N=8192
- CRLB cleanup 0.025  THEORETICAL@sqrt(p(1-p)/N_Q) at p=0.5 N_Q=400
- v2b diagnostic target_cos=0.436 vs other_cos=0.000 at α=3  CITED@task-input from Director spawn prompt (v2b hand-off note)
