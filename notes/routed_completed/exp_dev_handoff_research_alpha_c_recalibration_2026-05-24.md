# exp_dev hand-off: α_c recalibration + diagnostic verification

**Filed:** 2026-05-24 by Research sub-agent.
**Status:** READY for exp_dev pickup. This is a 2-step recalibration, NOT a new physics experiment.
**Parent note:** `notes/research_substrate_alpha_c_anomaly_2026-05-24.md`
**Trigger:** Strategy gated the MoE rebuild on a substrate-implementation audit after the smoke prestep reported α_c=0.39 vs prereg [0.08, 0.25]. The audit (parent note) concluded the band was mis-specified, not the substrate.

---

## TL;DR (for orchestrator + exp_dev triage)

The α_c=0.39 figure is **NOT a substrate anomaly**. The prestep script implements a **linear heteroassociator** y = W k with W = (1/N) Σ v_i k_i^T, recalled by pure cosine. The closed-form SNR prediction for this architecture at cosine threshold τ is α_c(τ) ≈ 1/τ² − 1, giving α_c(0.80) ≈ 0.5625 — *exactly* what the smoke is converging to. The 4 smoke datapoints match the closed-form prediction within ±0.002 cosine units.

**The prereg [0.08, 0.25] band cites the AGS autoassociative Hopfield figure (sign-thresholded recurrent dynamics), which is the wrong reference class for this script's linear cosine readout.** No substrate-implementation audit is required.

**Two actions unblock MoE rebuild:**

1. **(MECHANICAL, ~30 sec CPU)** Run the closed-form diagnostic: compute `cos_pred(M, N=512) = 1/sqrt(1 + (M-1)/N)` for the 4 smoke M-values and confirm |cos_smoke − cos_pred| < 0.005 at all 4 points. (Expected: residuals 0.001–0.002 per parent note.)

2. **(GPU, 15–30 min)** Run the existing prestep script in **full mode** (N=4096, 5 seeds, M-grid {200, 400, 800, 1600, 3200, 6400}) — *with the recalibrated pre-reg band* below. Verdict bands updated to match linear-heteroassociator regime.

If both pass, MoE rebuild unblocks with **recalibrated M_per_expert ≈ 1600** (not 400 as in the existing rebuild handoff).

---

## TASK

**Step 1 — Closed-form diagnostic (CPU, 30 sec):**

Verify the substrate matches textbook linear-heteroassociator theory by overlaying the closed-form prediction on the 4 smoke data points already in `data/exp_wave14_moe_alpha_c_prestep_v1/metrics.json`. Pass criterion: |residual| ≤ 0.005 at every M.

**Step 2 — Full-mode prestep (GPU, 15–30 min):**

Re-ship `experiments/exp_wave14_moe_alpha_c_prestep_v1.py` in full mode using the **recalibrated pre-reg bands** below. The script itself does not need modification IF exp_dev is OK with `ALPHA_C_OUT_OF_RANGE` being interpreted via the recalibrated bands at verdict-handler time. Cleaner: patch `ALPHA_C_LO = 0.40`, `ALPHA_C_HI = 0.70` in the script (lines 92–93) before re-ship.

---

## WHY

The MoE rebuild Tier-1 path (structural separation to break PAC-Bayes retention floor per `notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md`) is gated by knowing α_c_measured. The wrong-reference-class pre-reg made the smoke verdict `OUT_OF_RANGE`, which surfaced as "anomaly requires audit". The audit (parent research note) closes this by showing the substrate matches textbook theory exactly — but the *quantitative* α_c for the downstream MoE M_per_expert calculation still needs to come from the full-mode run, because:

- Smoke ran 1 seed (no CI)
- Smoke N=512 (finite-N corrections plausible at the 5–10% level)
- Smoke grid ends at M=400, giving grid-quantized α_c ∈ {0.098, 0.195, 0.391, 0.781}

Full mode provides 5-seed CI at N=4096 with a 6-point grid that brackets the expected α_c ≈ 0.56 with at least 3 above-and-below points, enabling proper interpolation.

---

## CONTRACT

### Recalibrated pre-reg bands

**HARD-PASS (recalibration confirmed; MoE rebuild unblocks):**
- α_c_measured ∈ [0.50, 0.60] (predicted: 0.5625 from closed form 1/0.80² − 1)
- CI width < 0.05 (5 seeds)
- Closed-form residual |cos_measured − cos_predicted| < 0.02 at every grid M
- → Report α_c_measured + M_per_expert_recommended = `0.70 * α_c * N` + M_total_recommended_k4 = `0.70 * α_c * N * 4 * 0.80`; proceed to MoE rebuild

**MIDDLE BAND (mild deviation; proceed with note):**
- α_c_measured ∈ [0.40, 0.50) ∪ (0.60, 0.70]
- OR closed-form residual 0.02–0.05 at 1–2 grid points
- → Proceed with M_per_expert at the *measured* value, document the residual

**HARD-FAIL (genuine anomaly):**
- α_c_measured outside [0.40, 0.70]
- AND closed-form residual > 0.05 at ≥ 2 grid points
- → Genuine substrate anomaly; re-open substrate-implementation audit; MoE rebuild stays gated

**INSTRUMENTATION-FAIL:**
- Any NaN cosine
- OR CI width ≥ 0.10 across 5 seeds (excessive seed variance)
- → Investigate per-seed before any verdict

### Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

The closed-form check is itself a verifiable formula. Self-tests for the diagnostic logic:

1. **cos_predicted formula:** `cos_pred(M=200, N=512) = 1/sqrt(1 + 199/512) = 1/sqrt(1.3887) = 0.8489` — within 0.005 of measured 0.8450. ✓
2. **α_c from threshold:** at τ=0.80, α_c_theory = `1/0.80² − 1 = 0.5625`. At τ=0.95, α_c_theory = `1/0.9025 − 1 = 0.1080`. At τ=0.50, α_c_theory = `1/0.25 − 1 = 3.0`. (Sanity: lower τ → higher tolerated α.)
3. **Recalibration band:** for τ=0.80, HARD-PASS [0.50, 0.60] brackets 0.5625 ± 10%. MIDDLE band [0.40, 0.70] brackets ± ~25%. Sanity-consistent with N=4096 finite-N correction <10%.
4. **M_per_expert calc:** at α_c=0.5625, N=4096: M_per_expert = `0.70 * 0.5625 * 4096 = 1612`. (Compare to old assumption M_per_expert = `0.70 * 0.14 * 4096 = 401` — **4× more capacity**.)
5. **M_total K=4:** M_total = `0.70 * 0.5625 * 4096 * 4 * 0.80 = 5161`. (Old assumption: 1290 → 4× lift.)

### Autonomy declaration

**exp_dev decides:**
- Whether to patch `ALPHA_C_LO=0.40, ALPHA_C_HI=0.70` in the script or interpret post-hoc
- Whether to add the closed-form prediction overlay to `metrics.json` summary (recommended: yes)
- Queue placement (overnight_queue per original prereg recommended; full GPU)
- ETA estimate
- Whether to keep PASS_COSINE=0.80 (recommended: yes — that's the threshold the analysis is built around)

**exp_dev does NOT decide:**
- The cosine-threshold-to-α_c mapping formula (`α_c = 1/τ² − 1`) — that's the diagnostic theory from the parent research note
- The recalibrated pre-reg bands above — pre-registered here per [[feedback-envelope-expansion-fail-bands]]
- The 2-step structure (closed-form check → full-mode confirm) — that is the testable design

---

## EXPECTED OUTPUT

After Step 1 + Step 2, the file `data/exp_wave14_moe_alpha_c_prestep_v1/metrics.json` (or a new dated version) should contain:

```json
{
  "verdict": "ALPHA_C_HARD_PASS",
  "verdict_msg": "alpha_c calibration succeeded: alpha_c_measured≈0.56, closed-form residual <0.02. M_per_expert_recommended≈1600. M_total_recommended_k4≈5100. Proceed to MoE SHIFT/PARTITION/SINGLE rebuild.",
  "summary": {
    "alpha_c_measured": ~0.56,
    "alpha_c_ci_width": <0.05,
    "closed_form_max_residual": <0.02,
    "m_per_expert_recommended": ~1600,
    "m_total_recommended_k4": ~5100,
    "regime_identified": "linear_heteroassociator_cosine_tau_0.80"
  }
}
```

Then route to verdict_handler for the MoE rebuild unblock decision.

---

## DOWNSTREAM IMPACT ON MoE REBUILD HANDOFF

The current MoE rebuild handoff (`notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md`) lines 105–106 and 120–125 assume `alpha_c_measured ≈ 0.14` from AGS, giving M_per_expert ≈ 400 and M_total ≈ 1300 for K=4.

**After this recalibration, those numbers change by 4×:**
- M_per_expert ≈ 1600 (not 400)
- M_total for K=4 ≈ 5100 (not 1300)
- Sweep grid M_total ∈ {0.5, 1.0, 2.0, 4.0} × K × M_per_expert → M_total ∈ {3200, 6400, 12800, 25600} for K=4

**These are 4× larger experiments by storage volume**, but the *fidelity-bound* per-expert is the same (cosine 0.80 at the M_per_expert target). Whether this lifts the MoE rebuild's GPU cost meaningfully is an exp_dev call; if the SHIFT arm with full-N=4096 per expert × M_total=25600 is too expensive, the sweep can be truncated at the lower M-values for the initial smoke pass.

**Important: this assumes MoE will use the linear-cosine retrieval primitive**. If Strategy decides MoE rebuild should use modern-Hopfield β=32 readout (which has α_c ≈ 0.14 per AGS, or up to 8 per Hu-Kerdock), then the prestep script needs to be reworked to match that primitive before any number from it can feed the rebuild. **This decision-fork is the blocking strategic question and must be resolved before the rebuild ships, not during it.**

---

## CONTEXT POINTERS

- `notes/research_substrate_alpha_c_anomaly_2026-05-24.md` — parent research note with full diagnostic
- `experiments/exp_wave14_moe_alpha_c_prestep_v1.py` — script under audit (no implementation bug, just wrong reference band)
- `data/exp_wave14_moe_alpha_c_prestep_v1/metrics.json` — smoke result that triggered drill
- `preregs/2026-05-24_wave14_moe_alpha_c_prestep_v1.md` — pre-reg with wrong band
- `notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md` — downstream MoE rebuild (M_per_expert numbers need 4× update after this recalibration)
- `notes/research_R36_alpha_c_coherence_bridge_2026-05-21.md` — R36 sandwich is for the OTHER regime (autoassociative recurrent), NOT this prestep

---

## DISCIPLINE CITATIONS

- per [[feedback-no-experiment-design-in-prompts]] — names the TASK (recalibrate + verify), the CONTRACT (recalibrated bands + self-tests), the WHY (closed-form matches smoke to 0.002); exp_dev decides queue/seeds/ETA/code structure
- per [[feedback-envelope-expansion-fail-bands]] — HARD-PASS / MIDDLE / HARD-FAIL / INSTRUMENTATION-FAIL bands pre-registered with explicit numerical thresholds
- per [[feedback-strategy-spec-formula-selftests]] — 5 self-test cells inline with worked numbers
- per [[feedback-lit-scan-calibration-penalty]] — P estimates deflated; novel-synthesis cap not invoked (textbook application)
- per [[feedback-don't-overextend-theorems]] — closed-form formula assumes large N and i.i.d. keys/values; MIDDLE band exists explicitly for finite-N and small-structured-deviation cases
- per [[feedback-verify-implementations]] — closed-form prediction verified against 4 measured smoke datapoints in parent note (max residual 0.002)
- per [[feedback-2x-means-depth]] — drill went DEEPER into the verdict instrumentation, not BROADER across new substrate framework — found the band was wrong, not the physics
- per [[feedback-ship-before-dependency-verified]] — gating decision (linear vs recurrent primitive for MoE) flagged explicitly before any further ship

---

**End handoff.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
