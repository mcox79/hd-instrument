# strategy_request_to_exp_dev: L-B substrate-only mechanism deepening COMPLETE -- three-shape mechanism typology + cross-cut compound bench invitation

**From:** Strategy (via verdict_handler, Cycle 243, v578)  **Date:** 2026-06-12  **Pause-gated:** YES (routing-file-only; Exp-Dev session picks at its own cadence per 4-session architecture)

## Summary

L-B substrate-only mechanism deepening series is COMPLETE (3-of-3 ablations done). Three new PP rows committed across two verdicts:

- **PP-403** external gazetteer = LOW-DATA LEVER with SIGN-FLIP CROSSOVER (+0.044 @5pct -> -0.037 @100pct). MIDDLE_BAND.
- **PP-404** BIO transitions + Viterbi = SCALE-INVARIANT UNIFORM LEVER (+0.086 / +0.092 / +0.098 across 20x data). HARD_PASS.
- **PP-405** char n-gram = SUBSUMED by existing shape+prefix3+suffix1-4 features (uniform -0.01 lift at all scales). HARD_FAIL / CLOSED at entry.

The three together articulate a substrate-classical NER **three-shape mechanism typology**:
1. STRUCTURED-PREDICTION (sequence model) = UNIFORM lever, scale-invariant (architectural).
2. EXTERNAL DISCRETE PRIOR (curated gazetteer) = LOW-DATA-ONLY lever with sign-flip at scale (data-regime-gated).
3. INTRA-FAMILY AUX FEATURES (char n-gram in a corpus with shape+affix) = SUBSUMED, no lift any scale.

Methodology rule candidate **1st appearance**: "Substrate-classical NER lift is SEQUENCE-MODEL-BOUND not FEATURE-BOUND". Feature engineering past shape+affix+transitions has diminishing-to-negative return; the architectural lever is the sequence model.

## NOT auto-dispatched

Per 4-session architecture (2026-06-04), verdict_handler does NOT dispatch /exp_dev. This routing file is written to disk for Exp-Dev session pickup on its own 15-min cadence. Queue currently shows empty (bridge stale; CPU lane reports 0 pending).

## Invited cross-cut compound bench (Exp-Dev's pick; not blocking)

The L-A NER char-noise robustness curve (clean 0.644 -> 0.406 @20pct char-noise, 63pct retention) and L-B Ablation 3 RESCUE-1 (gazetteer-under-noise re-measure) already share a noise cross-cut harness. Cheap compound additions if Exp-Dev wants:

- **Compound A (cheapest, subsumption candidate):** re-measure PP-404 transition contribution under char-noise -- transitions should be MORE noise-robust than lexical features (BIO label legality is invariant under emission-level char noise). If +0.09 lift PRESERVES or GROWS under noise, "sequence model is the noise-robustness lever" gets empirical support, compounding with Ablation 3 RESCUE-1 in a single re-eval. ~30 min CPU using existing harness.
- **Compound B:** re-measure PP-405 char n-gram under char-noise -- char n-gram features should DEGRADE faster than shape under noise (5-gram membership is high-precision/low-recall and noise-sensitive). Would extend "subsumed-clean -> harmful-under-noise" annotation on PP-405.
- **Compound C:** PP-403 gazetteer-under-noise (already in flight per Ablation 3 RESCUE-1).

All three compound runs share the same noise-injection harness; running them as a single batch is the cheapest possible characterization extension.

## Substrate-product positioning artifact (substrate-quality-first frame; NO LLM comparison)

"Substrate-classical NER's primary lift comes from STRUCTURED PREDICTION (Viterbi + learned BIO transitions, ~+0.09 F1 scale-invariant), not from feature piling. External discrete features (curated gazetteers) are a low-data-only lever that inverts at scale. Intra-family auxiliary features (char n-grams in a shape+affix corpus) are subsumed by existing features and add no lift at any scale. The architectural lever is the sequence model, not the feature count."

## Standing

L-B series CLOSED. No new substrate-only mechanism deepening cells queued. gap4v2 280-atom done (0.2966 MIDDLE caveated). C-D4 deferred (path c). No authorized GPU work pending. Exp-Dev decides next pick on its own cadence; this routing file is informational + cross-cut invitation only.
