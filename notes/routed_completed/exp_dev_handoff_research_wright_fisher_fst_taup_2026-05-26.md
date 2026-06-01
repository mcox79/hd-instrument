# Exp_dev hand-off — Wright-Fisher complementary instrumentation (F_ST + σ(τ_p) scaling)

**Filed:** 2026-05-26 by Research sub-agent.
**Parent research note:** `notes/research_wright_fisher_substrate_2026-05-26.md`.
**Routing:** complementary finite-N + cross-expert instrumentation; ZERO GPU spend if existing data sufficient.
**Pause-gate aware:** if `data/orchestrator_paused.flag` exists, queue_add is gated; Test 1 + Test 3 are POST-HOC ANALYSIS on existing artifacts and can run without queue dispatch.

---

## TASK

Two zero-GPU CPU-cheap post-hoc analyses on existing substrate data, plus one CONDITIONAL low-GPU re-ship if existing data is insufficient.

### Test 1 — Plateau-residence-time variance scaling σ(τ_p) vs N

Look at existing Bet B continual-learning runs at multiple N values. If runs at N ∈ {1024, 2048, 4096} exist (likely under `data/exp_wave14_betB_*`), compute per-seed plateau-residence-time τ_p at each N value (per-corpus, per-similarity-class), then fit `log(σ(τ_p)) vs log(N)` slope.

Decision tree:
- If multi-N data exists → run Test 1 analysis only (zero GPU).
- If multi-N data does NOT exist → file Test 2 to the queue (low-GPU re-ship at 3 N values).

### Test 3 — Cross-expert retention correlation F_ST analog (post-MoE-rebuild)

On in-flight or post-completion MoE-rebuild data (`data/exp_wave14_moe_shift_partition_v*`), compute per-arm F_ST_analog = 1 - mean_within_expert_variance / total_variance. Compare SHIFT arm vs PARTITION arm.

### Test 2 — CONDITIONAL low-GPU re-ship (only if Test 1 instrumentation-fail)

If Test 1 cannot run (no multi-N data), ship Bet B 3-stage continual at N ∈ {1024, 2048, 4096}, 5 seeds each, with explicit τ_p logging per seed per plateau.

---

## WHY

Closes the Wright-Fisher Tier-1b scope-expansion drill. Parent note found WF is COMPLEMENTARY (not competitive) to Saad-Solla — describes finite-N stochastic structure around Saad-Solla's deterministic plateau heights. Test 1 falsifies the WF-as-finite-N-correction position with a sharp prediction (σ(τ_p) ∝ N^{-1/2}). Test 3 adds a new SHIFT-vs-PARTITION discriminator (F_ST analog) ORTHOGONAL to the DMPK bimodality signature from the mesoscopic-transport drill (`notes/research_mesoscopic_transport_moe_2026-05-25.md`). Combining the two yields a 2x2 discriminator panel that catches mode-collapse failures the existing instrumentation may miss.

Tests 1 and 3 are CPU re-analysis only. Test 2 is conditional and would be small (~30 GPU-min) if needed.

---

## CONTRACT

### Test 1 (CPU re-analysis)

**Input:** any `data/exp_wave14_betB_*` runs at multiple N values with per-seed retention curves.

**Output:** `data/exp_wave14_research_wf_taup_scaling_v1/metrics.json` with:
- `tau_p_by_seed_by_N`: nested dict {N: {seed: [τ_p_per_plateau]}}
- `sigma_tau_p_by_N`: dict {N: σ across seeds, per plateau}
- `log_sigma_vs_log_N_slope`: scalar
- `log_sigma_vs_log_N_ci95`: [low, high]
- `verdict`: HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL

**Pre-registered HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL bands:**
- **HARD-PASS** (WF-as-finite-N-correction confirmed): slope ∈ [-0.7, -0.3] (consistent with WF diffusion's N^{-1/2} prediction within 40%) AND CI95 width < 0.4.
- **HARD-FAIL** (WF correction refuted): slope ∈ [-0.1, 0.1] (no N-dependence — constant noise, non-diffusive mechanism) OR slope < -0.8 (faster-than-WF — higher-order correction dominates).
- **MIDDLE BAND**: slope ∈ [-0.3, -0.1] or slope ∈ [-1.0, -0.7] (partial mapping, framework directionally correct but quantitatively off).
- **INSTRUMENTATION-FAIL**: no multi-N data exists, OR fewer than 3 seeds per N value, OR τ_p extraction NaN/undefined. Then file Test 2 conditional re-ship.

### Test 3 (CPU post-hoc on MoE-rebuild data)

**Input:** any `data/exp_wave14_moe_shift_partition_v*` runs with per-expert per-cell retention vectors.

**Output:** `data/exp_wave14_research_wf_fst_signature_v1/metrics.json` with:
- `F_ST_per_arm`: dict {arm: F_ST_analog scalar per (K, M_total) cell}
- `cross_expert_covariance_per_arm`: dict {arm: cov matrix (K, K) per cell}
- `verdict`: SHIFT_CONFIRMED / PARTITION_CONFIRMED / MODE_COLLAPSE / INCONSISTENT

**Pre-registered HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL bands:**
- **SHIFT_CONFIRMED**: SHIFT arm F_ST > 0.7 AND PARTITION arm F_ST < 0.3 (clean separation).
- **PARTITION_CONFIRMED**: SHIFT arm F_ST < 0.3 AND PARTITION arm F_ST > 0.7 (inverted from prediction — investigate).
- **MODE_COLLAPSE**: F_ST > 0.7 in either arm BUT only 1-2 experts have non-zero variance (i.e., F_ST high because most experts are dead, not because alleles are partitioned).
- **INCONSISTENT**: F_ST_SHIFT - F_ST_PARTITION within 0.2 (no discrimination).
- **INSTRUMENTATION-FAIL**: no per-expert retention vectors logged in existing artifacts. Then add the instrumentation cell to the next MoE-rebuild re-ship.

### Test 2 (CONDITIONAL low-GPU re-ship — only if Test 1 INSTRUMENTATION-FAIL)

**Input contract:** Bet B 3-stage continual-learning script extended to N ∈ {1024, 2048, 4096}, 5 seeds each, all other parameters held to the v189 baseline.

**Output:** `data/exp_wave14_research_wf_taup_reship_v1/metrics.json` (same structure as Test 1).

**Pre-registered bands:** same as Test 1.

**Compute budget:** estimated 30 GPU-min total (3 N values × 5 seeds × 3 stages). GPU queue.

---

## AUTONOMY

You (exp_dev) decide:
- Anchor names.
- Which existing artifacts qualify for Test 1 / Test 3 (verify per-seed retention + per-N coverage).
- Test 1 vs Test 2 routing (Test 2 only if Test 1 returns INSTRUMENTATION-FAIL).
- Whether to ship Tests 1 + 3 as one combined analysis script or two.
- Queue choice (Test 2 → GPU; Tests 1 + 3 are CPU-laptop or CPU-remote, your call).
- ETA for Test 2 if needed.

Pre-registered HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL bands ABOVE are LOAD-BEARING — do NOT modify without strategy hand-off.

Per [[feedback-strategy-spec-formula-selftests]] the σ(τ_p) ∝ N^{-1/2} prediction is the load-bearing closed form. Self-test cells:
- INPUT: σ(τ_p)[N=1024] = X (measured); PREDICTION: σ(τ_p)[N=4096] = X / 2 (factor of 2 = √4).
- INPUT: σ(τ_p)[N=1024] = X (measured); PREDICTION: σ(τ_p)[N=2048] = X / √2 (factor of 1.41).
- Verify the predicted-vs-measured residuals before declaring HARD-PASS.

---

## CROSS-REF

- Parent research note: `notes/research_wright_fisher_substrate_2026-05-26.md`
- Complementary frameworks (do NOT supersede; both still load-bearing):
  - `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` (Saad-Solla; deterministic ODE; plateau heights)
  - `notes/research_mesoscopic_transport_moe_2026-05-25.md` (DMPK; orthogonal SHIFT/PARTITION discriminator)
- F_ST + DMPK 2x2 discriminator panel (per parent note Sec d, cross-ref to mesoscopic-transport drill).

---

**End hand-off.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
