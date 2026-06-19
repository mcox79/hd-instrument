# exp_dev hand-off: MoE α_c dense-grid precision measurement (v3)

**Filed:** 2026-05-26 by Research sub-agent.
**Status:** READY for exp_dev pickup. Nice-to-have precision measurement; MoE rebuild is NOT gated on this.
**Parent note:** `notes/research_moe_alpha_c_band_audit_2026-05-26.md`
**Trigger:** v207 NEW pre-reg "MoE α_c band-rationale defensibility audit"; audit conclusion BAND_RIGHT_INSTRUMENTATION_FAIL (grid quantization, not substrate signal).

---

## TASK

Re-ship the `alpha_c_prestep` measurement with a DENSE M-grid bracketing the predicted α_c ≈ 0.5625 region at finer resolution than the v2 factor-2 grid.

Goal: a CI-quantified α_c measurement within the existing band [0.40, 0.70] at α-grid spacing ≤ 0.10, sufficient to distinguish HARD-PASS [0.50, 0.60] from MIDDLE band [0.40, 0.50) ∪ (0.60, 0.70].

---

## WHY

The v2 prestep reported α_c=0.390625 = 1600/4096 EXACTLY (bit-exact, NOT noisy). This is grid quantization at the factor-2 M-spacing {200, 400, 800, 1600, 3200, 6400}: the threshold cosine τ=0.80 lies between M=1600 (cos=0.848, ABOVE) and M=3200 (cos=0.749, BELOW), so the α_c-extraction rule "largest M where cos > τ" returns 1600/4096 = 0.3906 by mechanical necessity, irrespective of any substrate-specific deviation.

The band [0.40, 0.70] is correctly constructed (parent audit, Audit Q1). The MEASUREMENT instrument's grid is insufficient to resolve within the band. Densifying the M-grid in the prediction region eliminates the artifact and produces a CI-quantified α_c that the verdict-handler can classify cleanly as HARD-PASS / MIDDLE / HARD-FAIL per the existing band rules.

This is a precision measurement, not a substrate test. **MoE rebuild SHIFT/PARTITION v2 (in flight on remote) is the dominant capability test and is NOT gated on this dense-grid v3.** Queue priority for v3 is LOW (after SHIFT/PARTITION v2 verdict, after Pred-4 v3 design).

---

## CONTRACT

### Pre-flight verification (REQUIRED, no GPU, ~30 sec)

Before shipping v3, fetch the v2 metrics.json from the remote and inspect the per-seed cosine block:

- Path on remote: `data/exp_wave14_moe_alpha_c_prestep_v2/metrics.json`
- Decisive cell: `summary.mean_cosines["1600"]` (cosine at M=1600 averaged across 5 seeds)
- PASS criterion: mean_cosine in [0.83, 0.87] (predicted: 0.8481 ± closed-form residual margin 0.02)
- If PASS: grid-quantization confirmed as the root cause; proceed to v3 design.
- If FAIL: real substrate deviation exists; ABORT v3 ship; route back to Research for re-audit.

### v3 M-grid design (exp_dev autonomy)

Choose M-values for N=4096 such that:
- At least 3 grid points fall in α ∈ [0.40, 0.70]
- α-spacing within the band ≤ 0.10 (vs current 0.39)
- Endpoints bracket the band: lowest α ≤ 0.30, highest α ≥ 0.80
- Total grid points: exp_dev decides (5–10 reasonable)
- Suggested-not-mandated: a 7-point grid spanning M ∈ [~1200, ~4000] gives α-resolution ≈ 0.07 within the band.

Do NOT include this grid construction as a strategy directive — exp_dev sizes the M-grid against the GPU/wall budget and the resolution requirement above.

### Seeds / wall budget / queue (exp_dev autonomy)

- Seed count ≥ 5 (for CI < 0.05 per existing pre-reg)
- Wall budget: exp_dev choice (~15–30 GPU-min for ≤ 8 M-values × 5 seeds at N=4096)
- Queue: exp_dev choice (overnight_queue most likely; CPU not appropriate at N=4096)

### Pre-registered verdict bands (carried VERBATIM from parent recalibration drill)

- **ALPHA_C_HARD_PASS**: α_c_measured ∈ [0.50, 0.60] AND CI < 0.05 AND max_residual < 0.02 → MoE rebuild M_per_expert = 0.70 × α_c × 4096
- **ALPHA_C_MIDDLE**: α_c_measured ∈ [0.40, 0.70] AND max_residual < 0.05 → proceed with measured value; document deviation
- **ALPHA_C_HARD_FAIL**: α_c_measured outside [0.40, 0.70] OR max_residual > 0.05 at ≥ 2 grid points → genuine anomaly, re-open implementation audit
- **ALPHA_C_INSTRUMENTATION_FAIL**: any NaN cosine OR CI width ≥ 0.10 → per-seed investigation before any verdict

### Required script changes from v2

- M-grid only. ALPHA_C_LO, ALPHA_C_HI, HARD-PASS sub-band [0.50, 0.60], CI thresholds, residual thresholds — all CARRIED VERBATIM from v2.
- Self-tests (1–6 in v2 lines 195–249): carry verbatim; do NOT modify.
- Multi-scale smoke gate (v2 lines 399–412): carry verbatim; do NOT modify.

### Pre-reg

File `preregs/2026-05-26_wave14_moe_alpha_c_prestep_v3.md` with:
- M-grid as designed
- Existing band rules carried verbatim
- Pre-flight verification step (v2 metrics.json fetch + cosine inspection at M=1600)
- HARD-PASS / MIDDLE / HARD-FAIL thresholds (carried)

### Calibrated outcome probabilities (carried from parent audit)

- P(HARD-PASS [0.50, 0.60]) = 0.60
- P(MIDDLE [0.40, 0.50) ∪ (0.60, 0.70]) = 0.25
- P(HARD-FAIL outside [0.40, 0.70]) = 0.05
- P(INSTRUMENTATION-FAIL) = 0.10

---

## AUTONOMY

- exp_dev chooses M-grid exact values, seed count, queue placement, wall budget, ETA.
- exp_dev chooses smoke-gate behavior (multi-scale per v2 is fine).
- exp_dev does NOT modify band rules or verdict logic.
- exp_dev does NOT proceed if pre-flight verification (v2 cosine at M=1600) FAILS — route back to Research.

---

## DEPENDENCIES

- v2 metrics.json on remote (`data/exp_wave14_moe_alpha_c_prestep_v2/metrics.json`) — REQUIRED for pre-flight check.
- No other capabilities or cap_map rows; this is a self-contained precision measurement.

---

**End handoff.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
