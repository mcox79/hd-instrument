# Pre-registration: h4b_regime_redesign_probe_v1

**Date:** 2026-07-02
**Cell:** `experiments/exp_h4b_regime_redesign_probe_v1.py`
**Anchor:** `h4b_regime_redesign_probe_v1`
**Author:** hdi_exp_dev (spawned by hdi_research)
**Priors:**
- `notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md` (drill abe94cac; §5.1 + §3.1 Bayes-floor)
- `notes/research_h4_revival_confidence_calibration_2x_drill_2026-07-02.md` (h4b origin)
- `experiments/exp_h4b_margin_top1_top2_gap_predictor_v1.py` (harness base; HF'd smoke-preview AUC 0.545 @ N=8192 items=3600 p≈0.046 INTRA_COS=0.6)

## Purpose (from spawn brief)

Determine whether h4/h4b failures were REGIME confound or MECHANISM-CLASS limit. Drill verdict: BOTH. This cell disentangles the two drivers via a 6-arm sweep across (INTRA_COS, p) space. Sibling cell `lane_x_prime_stochastic_consistency` (dispatched separately) tests mechanism-substitute at same regime; complementary evidence.

## Mechanism

**Same as h4b** — top-1 vs top-2 similarity gap as contamination-risk predictor:
- For each query q, compute `sims = kb_aug @ q`; `gap = sims[0] - sims[1]`; `risk = -gap`
- AUC(risk, is_contaminated_in_top_K) is the discriminator
- Distinct from h4 (density-averaging); spatial-margin does not dilute with M

**Contamination injection parametrized by `p_target`:**
- `n_false_injected = max(1, round(p_target * 2 * N_Q))` false facts
- Each false fact tied to a randomly-chosen cluster centroid c_j (unit-normalized `INTRA_COS·centroid + sqrt(1-INTRA_COS^2)·rv`)
- Queries balanced from all clusters (round-robin): N_Q positives from same-cluster-as-injected + N_Q negatives from other clusters
- Per-query `is_contaminated` = 1 iff ANY injected false-fact index ∈ top-K similarities

Realized contamination_rate is measured and reported; `p_target` and realized `p_realized` both logged for post-hoc regime characterization.

## Arms (6)

| Arm | INTRA_COS | p_target | drill prediction |
|-----|----------|----------|------------------|
| A   | 0.6      | 0.046    | AUC 0.53-0.55 (reproduce h4b HF) |
| B   | 0.6      | 0.20     | AUC 0.58-0.65 (contam UP; INTRA_COS unchanged) |
| C   | 0.4      | 0.046    | AUC 0.58-0.63 (INTRA_COS DOWN; contam unchanged) |
| D   | 0.3      | 0.10     | AUC 0.68-0.78 (BOTH improved — HP TARGET) |
| E   | 0.5      | 0.10     | AUC 0.60-0.68 (mild both) |
| F   | 0.4      | 0.20     | AUC 0.75-0.85 (contam UP + INTRA_COS DOWN) |

All numbers HYPOTHESIZED@drill §5.3 predicted-AUC table.

## Regime (from drill)

- N = 8192 (h4-harness scale; do NOT reduce)
- items = 3600 (N_CLUST=60, PER=60)
- N_Q = 200 per arm (drill's specific sample size)
- Seeds = [7, 17, 23] (matches h4b FULL seeds)

Total units per FULL run: **6 arms × 3 seeds = 18** (EXPECTED_N_UNITS).

## Bands (drill §5.1 §5.3)

**Primary discriminator = Arm D (INTRA_COS=0.3, p=0.10):**
- **HARD_PASS:** Arm D AUC ≥ 0.68 AND Arm A ≤ 0.55 (3-seed cv on Arm D ≤ 0.04)
  - Interpretation: REGIME_CONFOUND primary — h4-family observables work in relaxed regime
- **MIDDLE_BAND:** Arm D AUC in [0.60, 0.68), OR HP metrics but Arm A > 0.55 (h4b reproduction failed)
- **HARD_FAIL:** Arm D AUC < 0.60
  - Interpretation: MECHANISM_LIMIT primary — spatial margin dead even at improved regime

Secondary confirmatory band: Arm F ≥ 0.75 supports HP; < 0.65 supports HF.

## Compute architecture

**(b) numpy-batched-CPU with justification.**

Load-bearing op per arm per seed: KB construction (3600 items × N=8192 = ~120 MB float32) + one BLAS matmul `qs @ kb_aug.T` shape (400, ~3600). Per-seed matmul wall ~2-5s on numpy CPU BLAS. Per-arm 3 seeds × ~5s = ~15s. 6 arms × 15s = ~90s wall. Plus overhead ~2-3 min.

GPU launch overhead >> per-arm matmul runtime at this scale; batched-numpy matches BLAS peak throughput on modern CPU. This is the reference-parity mode with h4b (which was CPU-numpy). GPU speedup would be marginal (~1.5x on the matmul, negated by dispatch overhead + memcpy).

Expected FULL wall: **~5-10 min** on remote_cpu_queue.

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok`: EXPECTED_N_UNITS = 18 (6 arms × 3 seeds). Verdict HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if observed < 18.
- [x] Per-unit failure-class instrumentation: outer try/except records failure_class per arm; ARM_FAILED sentinel + full traceback.
- [x] Discriminator-fires gate: smoke Arm A reproduces h4b HF (AUC in [0.50, 0.60]); smoke Arm D at reduced N preview (see smoke section).
- [x] Strictly-above-floor: HP band 0.68 vs floor 0.60; band width 0.08; 5% × 0.08 = 0.004 → HP requires ≥ 0.68 strict.
- [x] HP_SCOPE: Arm D primary; Arm A must satisfy reproduction gate (≤ 0.55); other arms are diagnostic, not HP-gated.
- [x] calibration_check: `default_ok_for_this_regime` — no adaptive tuning; gap is parameter-free.
- [x] arms_differ_verified: 6 arms produce different contamination injection schemes; hash-verified at smoke gate.
- [x] final_metrics_atomicity: `tmp_replace` via write_metrics helper.
- [x] `except SystemExit: raise` before `except Exception`.
- [x] crlb_n/a: "AUC discriminator; no closed-form noise floor. Drill §3.1 Bayes-floor formula gives Δ/σ√2 requirement (in cell verdict logic as regime-check)."
- [x] baseline_in_band: contamination_rate ≈ 0.5 by construction (balanced pos/neg queries); AUC chance floor = 0.5. Realized p ≈ p_target verified per arm.
- [x] discriminator_survives_scale: smoke includes Arm A + Arm D at reduced N_Q=50 (full N=8192, items=3600); if Arm A AUC > 0.60, cell is broken (h4b reproduction fails). If Arm D preview AUC < 0.55, REJECT FULL.
- [x] arms_differ_exempted: N/A (all 6 arms differ)
- [x] HYPOTHESIZED numbers tagged in cell comments + this pre-reg (META_RULE_AC)

## Cell-chunking / defensive-error patterns

- `cell_chunked`: false (single-cell 6-arm sweep; ~5-10 min wall well within timeout; per-arm loop resilient to single-arm failure via per_unit tracking)
- `start_marker_written`: true (writes `_start_marker.json` at main() entry)
- `crash_diagnostic_present`: true (except Exception → CELL_CRASHED metrics.json + traceback)
- `heartbeat_present`: true (per-arm progress print with flush=True; wall ~15s/arm ≪ 60s cadence so per-arm print suffices)
- `defensive_error_checking`: "passed_all_4_patterns"
- `progress_logging`: "print_flush_true" (per-arm + per-seed prints; ~5-10 min wall < 30 min threshold but discipline still applied)

## Smoke gate design

**Smoke config:** all 6 arms, seed=1 only, N=8192, items=3600 (full-N for discriminator-survives-scale gate), N_Q=50 (reduced from 200 to speed smoke to ~30-60s).

**Smoke pass criteria:**
1. All 6 arms produce metrics (cardinality 6 units)
2. Arm A AUC in [0.48, 0.60] — reproduce h4b HF regime (±0.05 tolerance for reduced-N_Q noise)
3. Arm D AUC > 0.55 — discriminator-preview at full-N; if fails, REJECT FULL
4. Per-arm realized contamination_rate approximately p_target (within factor 2x)
5. `_arms_must_differ_verified` = true

If smoke fails any gate, DO NOT dispatch FULL; re-spec regime.

## Compute-formula verifications (executed by author)

- Bayes-floor at (μ=0.622, σ=0.005): AUC 0.65 requires Δ = 0.385 × 0.005 × √2 = 2.72e-3 = 0.44% of μ. THEORETICAL@Fawcett 2006. h4b observed Δ ≈ 8e-4 → AUC 0.545 confirmed.
- p_target=0.10 realized: injecting n_false ≈ round(0.10 × 400) = 40 false facts across 60 clusters gives ~0.67 false-per-cluster; per-query top-K=10 contamination rate ≈ 40/3600 × 10 × cluster-locality-bonus ≈ 0.10-0.15 (validated empirically at smoke).
- Design-effect K_eff at K=60, ρ=0.6: 60/(1+59×0.6) = 1.65. Cluster-averaging SNR gain √K_eff ≈ 1.28x (drill §3.2). Not used in this cell (h4b spatial-only), but relevant for band interpretation.

## Dispatch plan

- **Smoke:** author runs `python experiments/exp_h4b_regime_redesign_probe_v1.py --smoke` locally on d:/AI/hd-instrument/.venv; verifies smoke gate criteria above.
- **FULL:** target queue `remote_cpu_queue`; timeout 1800s (30 min; conservative — expect ~5-10 min wall + startup overhead).
- Dispatch handled by hdi_orchestrator (author cannot push to origin/main).

## Downstream interpretation matrix (from drill §5.3)

If this cell + `lane_x_prime_stochastic_consistency_predictor_v1` both land:

| Arm D verdict | Lane X verdict | Interpretation |
|---|---|---|
| HARD_PASS | HARD_PASS | Both work: regime-fix AND mechanism-substitute available; 4-signal cortex header viable |
| HARD_PASS | HARD_FAIL | Regime is ONLY problem; use spatial gap in relaxed regime |
| HARD_FAIL | HARD_PASS | Mechanism class dead everywhere; only stochastic-consistency works; drop spatial from 4-signal arch |
| HARD_FAIL | HARD_FAIL | Substrate cannot host per-query contamination-detection; pivot cortex-confidence to different task class |

*End pre-registration.*
