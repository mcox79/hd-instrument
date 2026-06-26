# exp_dev hand-off -- research: n5 revival slow-learning cortex context compression

**Filed by:** research (Opus 4.7 1M)
**Filed at:** 2026-06-26
**Trigger:** USER deep revival drill on n5 trigram HARD_FAIL. Companion to research note `notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md`.

**Pause state:** Pause flag check is exp_dev's responsibility on pickup; this file is pickup-eligible whenever pause clears or for queue-refill on next cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file POINTS to anchors and substrate-product reasoning; cell-author owns experiment design, hyperparameter selection, harness wiring, smoke tests, and pre-reg envelope-fail-band derivation.

---

## Anchor candidates (rank-ordered)

### ANCHOR_1 (rank-1, cheapest decisive, ships immediately)

- **Pointer:** `slow_cortex_bigram_predictor_v1`
- **Substrate-product reading:** Slow-learning cortex-style trigram predictor. Build W_bigram and W_trigram by Hebbian outer-product writes of (BUNDLED context, target_word) over text8 train split. At query time score linearly (NO HRR-bind at query). Interpolate logits_bigram + logits_trigram via alpha, softmax with beta. 4-arm: BIGRAM_BASELINE (replicate n5 within 0.02) / TRIGRAM_BUNDLE_SLOW (cell-rank-1 mechanism) / TRIGRAM_HRR_REPLICATION (anchor n5 HARD_FAIL within 0.02) / TRIGRAM_BUNDLE_NREM_REPLAY (add proven-bound replay decorator). Decisive question: does slow-learning bundle-at-context beat n5 HRR-blend AND bigram baseline?
- **Tier hint:** MEASURED_MECHANISM expected at first land; chain-grade-eligible if TRIGRAM_BUNDLE_SLOW HARD_PASS replicates with cv <= 0.03 AND TRIGRAM_HRR_REPLICATION HARD_FAILs as expected (cross-arm discriminator visible).
- **Why now:** USER reframe is structurally correct. n5 HARD_FAIL was wrong-LAYER not wrong-FAMILY. The substrate has every primitive; cell is a recomposition not new research. Cheapest possible test of the reframe. Standalone-shippable now.
- **P_deflated:** 0.40 (capped at novel-synthesis 0.50; -0.10 for substrate-specific composition risk; +0.05 for mechanism-family-validated by Saffran 1996 + Tino-BCM 2003).
- **Reference for design context:** Section "Cheap decisive test" + Section 4 Cell 1 of the parent research note.
- **Compose-with:** Drill 3 ANCHOR_1 `lang_ingest_vocab_bigram_meta_m7_v1` (this cell can BUNDLE into that one with extended arm-set, or ship standalone; recommend standalone for cleaner discriminator unless compute budget tight).

### ANCHOR_2 (rank-2, CONTINGENT on Gap 3 BCM HARD_PASS)

- **Pointer:** `gap3_LM_extension_v1`
- **Substrate-product reading:** Extend the in-flight `gap3_cls_two_tier_BCM_slow_replay_v1` cell with a SECONDARY ENDPOINT: at end of training, evaluate text8 next-token prediction using W_schema as W_cortex_LM. Adds one endpoint to existing 4-arm Gap 3 cell. Decisive question: does Gap 3 BCM rule generalize from categorical-schema to sequence-prediction?
- **Tier hint:** MEASURED_MECHANISM; chain-grade-eligible if HP and beats bigram baseline by >= 0.04.
- **Why now:** ONLY-IF Gap 3 `gap3_cls_two_tier_BCM_slow_replay_v1` lands HARD_PASS FIRST (currently dispatched per status_log 2026-06-26). Cheapest extension; piggybacks on existing dispatch.
- **P_deflated:** 0.30.

### ANCHOR_3 (rank-3, CONTINGENT on Gap 3 + Gap 4 BOTH HARD_PASS)

- **Pointer:** `TWO_TIER_replay_trained_LM_v1`
- **Substrate-product reading:** Full brain-aligned LM architecture. Two W matrices: W_episodic (fast, hippocampus, eta_fast = 1.0 per triple) + W_cortex_LM (slow, BCM rule at eta_slow = 1e-3 during NREM replay). At query: try W_cortex_LM first (schema-completion path); if low-confidence, fall back to W_episodic. Marquee composition cell: demonstrates SAME architecture handles schema-extraction + retention + sequence-prediction.
- **Tier hint:** MEASURED_MECHANISM at first; chain-grade-eligible with cross-task validation.
- **Why now:** ONLY-IF Gap 3 + Gap 4 both land HARD_PASS. Marquee product story if validated.
- **P_deflated:** 0.30.

### ANCHOR_4 (rank-4, parallel exploratory; ships if compute spare)

- **Pointer:** `predictive_coding_LM_hierarchy_v1`
- **Substrate-product reading:** Stack two predictive-coding layers per Caucheteux-King 2022/2023 hierarchy: L1 predicts at bigram time scale; L2 predicts at trigram/discourse time scale; refuse-gate at top. Adds calibrated-refuse to LM output. Tests Caucheteux hierarchical-PC hypothesis on substrate.
- **Tier hint:** MEASURED_MECHANISM; orthogonal lever to bundle-at-context.
- **Why now:** spare-compute exploratory; lower-priority unless ANCHOR_1 HARD_FAILs (then becomes relevant for diagnostic).
- **P_deflated:** 0.25.

### ANCHOR_5 (rank-5, falsification probe)

- **Pointer:** `SDM_context_pooled_LM_v1`
- **Substrate-product reading:** Sparse distributed memory (Kanerva 1988 / Bricken-Pehlevan 2021) over W rows close to query: instead of single-row lookup, POOL across rows whose context-signature has high cosine to query. Tests SDM as alternative read-side mechanism.
- **Tier hint:** MEASURED_MECHANISM if HP; mostly a falsification probe.
- **Why now:** different mechanism class than Hebbian outer-product; useful for ruling out read-side alternatives.
- **P_deflated:** 0.20.

---

## Context pointers (file paths, not summaries)

- Primary research note (this drill): `notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md`
- n5 HARD_FAIL anchor metrics: `data/exp_n5_trigram_concept_lm_v1/metrics.json`
- Gap 3 BCM in-flight cell (compose-with ANCHOR_2/3): `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md`
- Gap 4 TWO_TIER in-flight (compose-with ANCHOR_3): `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md`
- Drill 3 ANCHOR_1 lang_ingest (compose-or-extend target): `notes/exp_dev_handoff_research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`
- Path C v2 encoder pivot (fallback if HARD_FAIL): `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
- META_HARNESS_RIGGED methodology audit (INFRA_1 requirement): `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md`
- chain-grade primitives backing the pipeline: `hdlab/{char_trigram_encoder, sequence_memory, bundling, memory, predictive_coding, continual}.py`
- Per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]]: at N=16384 with text8 17M tokens, route via hdi_orchestrator to remote_cpu_queue (laptop CPU too slow for N=16384^2 matrix updates at this volume)

---

## Contract

This file is a HAND-OFF, not an experiment design. Per [[feedback-no-experiment-design-in-prompts]]:

- Cell author owns: hyperparameter selection (eta, alpha, beta interpolation, N_DIM, V_TOK), pre-reg envelope-fail-bands derivation, smoke-test design, harness wiring, V_TOK choice (recommend 8192 to match Drill 3 ANCHOR_1).
- This file provides: substrate-product reading (why-now / what-it-tests), tier hints, P_deflated estimates, compose-with pointers, fallback diagnostic paths.
- Pre-dispatch verify-the-referent (Fix #26): cell-author should run `tools/predispatch_check.py slow_cortex_bigram_predictor_v1` to check for recent_landings + atoms.jsonl prior evidence; specifically check for any prior cell with `slow_cortex_*` or `slow_learning_lm_*` anchors.

---

## Autonomy declaration

This hand-off is the structural feed from research to exp_dev. Per orchestrator routing convention (auto-discovered by exp_dev on emergency-refill cycles; scans `notes/exp_dev_handoff_*.md` sorted by mtime), this file is autonomous-pickup-eligible.

exp_dev should:
1. Read this file + primary research note (path above).
2. Run pre-dispatch verify-the-referent gate.
3. Design cell per cell-author autonomy; smoke-test locally.
4. Ship via queue_add per pause-flag state.
5. Post-ship REMOTE VERIFY per [[feedback-verify-the-referent-arrives-not-just-producer-acted]].

If ANCHOR_1 cannot ship for any reason (compute budget, INFRA_1/2/3 not yet committed, etc), defer to ANCHOR_2 (which piggybacks on Gap 3 cell already dispatched -- minimal new compute).

---

-- research (Opus 4.7 1M)
