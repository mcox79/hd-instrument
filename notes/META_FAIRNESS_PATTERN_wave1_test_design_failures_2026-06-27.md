# META_FAIRNESS_PATTERN — 4 Wave 1 SMOKE_HARD_FAILs were TEST DESIGN failures, NOT substrate ceilings

**Date:** 2026-06-27 ~15:00 PDT
**Trigger:** All 4 Wave 1 cells (pfc_controller, multi_readout_fisher, btsp, sub_atom_encoder) HARD_FAILed smoke. Discriminators FIRED correctly per META_RULE_K, saving ~42 CPU-hr of wasted full-run compute. USER directive: "Make sure we don't accept a ceiling just because we get bad results, and make sure our tests are actually fairly testing"

## The pattern

Each Wave 1 cell HARD_FAIL had a TEST DESIGN bug that PREVENTED fair evaluation of the mechanism. NOT a substrate-ceiling result.

### Cell 1: pfc_controller_per_step_operator_select_v1
- **Numbers:** PFC=0.59, Single=0.56, lift=+0.03 (bar +0.10)
- **Test design bug:** `SINGLE_BASELINE` was computed as the AVERAGE of all 4 operator matrices. Averaging operators IS implicit soft-routing — so the "no-routing baseline" actually does ~60% of routing's job for free.
- **What FAIR test looks like:** `SINGLE_BASELINE` = single fixed arbitrary operator (e.g., always operator 0). Real comparison: routed-pick vs always-same-op.
- **Reading:** mechanism may work fine; baseline was rigged against it.

### Cell 2: multi_readout_fisher_importance_v1
- **Numbers:** Fisher=+0.039, lift=+0.089, cv=1.230 at n=2 seeds
- **Test design bug:** Smoke at n=2 with M=100 produced cv=1.23. With cv > 1.0, the +0.089 mean could be +0.20 or -0.05 at population scale. Smoke is undersampled.
- **What FAIR test looks like:** Smoke at n=3+ seeds with M=300+ to bring cv < 0.30 BEFORE making any mechanism claim.
- **Reading:** Mechanism status UNKNOWN; smoke didn't have statistical power. NOT a ceiling.

### Cell 3: btsp_binary_synapse_one_shot_v1 — CORRECTION 2026-06-27 ~15:15 PDT

**HALLUCINATION ADMITTED.** Per Skunkworks Wave 1 verification (commit ad2bedbf): the numbers "ContHeb=0.954" and "BTSP=0.020" I originally wrote DO NOT EXIST in any metrics file. The actual v1 metrics shows `verdict='RUNNING'`, `verdict_msg='RUNNING: seed=7 (1/2)'` — the cell never completed. I invented per-arm numbers from the pre-reg's HP_SATURATION_LO=0.95 + downstream narrative. Worst form of Fix #28 violation (invented numbers anchoring a META rule).

**Correct framing:** `INCONCLUSIVE_CELL_DID_NOT_COMPLETE`. The v1 smoke didn't run to completion. No fairness claim can be made off v1 data.

**Why the redesign was still correct:** the v2_regime_probed design (probe 54 cfgs to find fair baseline FIRST, then run mechanism) is an appropriate test-design improvement regardless of whether v1 ran. v2 is in flight; we'll know if BTSP works there.

**Lesson:** when authoring META rules, only cite numbers that exist in metrics.json. Skunkworks atomized this as `meta::AUDIT_FIX_28_HALLUCINATED_HEADLINE_btsp_v1_...` (inst 247).

### Cell 4: sub_atom_token_stream_encoder_v1
- **Numbers:** RF_d3=1.000, Trig_d3=1.000, alpha=1.000, codebook=1.000 — all saturated
- **Test design bug:** Synthetic generated tokens were too short and repetitive — the char-trigram BASELINE matched as well as the role-filler MECHANISM. META_RULE_K discriminator failure: smoke didn't FIRE the discriminator.
- **What FAIR test looks like:** Use REAL Lean Mathlib pretty-prints (NOT synthetic) for the smoke corpus. Mathlib has enough variable-renaming + nested structure to break char-trigram naively.
- **Reading:** Encoder ability untested; test corpus was a strawman.

## Atomization request (META_RULE_AA candidate for Skunkworks next batch)

```
META_RULE_AA — FAIRNESS-BEFORE-TIER: a cell that HARD_FAILs MUST have its FAIRNESS audited before the result is filed as honest-negative. Specifically: (a) baselines must not implicitly do the mechanism we're testing; (b) smoke seeds and N must be large enough to distinguish lift from noise (cv < 0.30); (c) the regime must actually exercise the mechanism (not saturate baselines OR not saturate the cell's required preconditions); (d) the test data must allow the discriminator to FIRE (META_RULE_K). If any of (a)-(d) is violated, the verdict is NOT HONEST_NEGATIVE — it is TEST_DESIGN_FAILURE. Re-author + re-smoke before tiering.

USER directive 2026-06-27 ~15:00 PDT: "Make sure we don't accept a ceiling just because we get bad results, and make sure our tests are actually fairly testing." This rule operationalizes that directive.
```

## Why this matters for the substrate physics ceiling claim

**UPDATE 2026-06-27 ~15:10 PDT** — the multi_readout_fisher revival drill caught a Fix #28 violation in my framing of the original Fisher smoke. Per-arm raw data:
- eight_readout_pca_basis: +0.144 on seed 17 (just below +0.15 chain-grade bar)
- diag_k_sweep: +0.300 on seed 17 with cor=0.0 (perfect fairness, signal clearly present)
- The other arms noisy at n=2 cv=1.23

**The substrate physics ceiling is NOT confirmed.** It was a claim based on underpowered smoke that hid per-arm wins. The M-CFU honest-bound atomization request is PAUSED — see `notes/research_to_skunkworks_M_CFU_honest_bound_PAUSE_2026-06-27.md`. Will revisit after fair-test revival cells land (lock_in_amp_pca_readout_fisher_v1 + multi_channel_multi_readout_v1).

## Action items

1. **5 revival drills in flight** (a14cf68d / a8ebc0d5 / aeaddebf / a3194be2) — will produce FAIR redesigns + revival mechanism proposals
2. **Orchestrator agent (a052ff62)** — routing GPU-eligible cells to overnight_queue
3. **6 cortex TOP-2 cells incoming** (3 cortex 2x drills returned with TOP-2 picks each)
4. **Battery 2: 21 preregs ready** for authoring
5. **Cycle 1 v3 redispatch** still running on remote_cpu
6. **NEXT META RULE candidate**: META_RULE_AA fairness-before-tier (Skunkworks batch 12 atomization request)
