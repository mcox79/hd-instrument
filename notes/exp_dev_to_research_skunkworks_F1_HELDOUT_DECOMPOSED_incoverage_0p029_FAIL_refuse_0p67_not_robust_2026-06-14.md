# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): F1_HELDOUT_DECOMPOSED (DECISION 32). IN-COVERAGE F1=0.029 (HARD_FAIL -- capability does NOT transfer even with gold present) + COVERAGE-GAP refuse-rate=0.67 (not robust; ~1/3 hallucinate).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED
**Re:** DECISION 32 two-number split. ACTUAL (10th rule). Canonical scorer + bge cache; held-out q54-q65 (13q), bucketed by gold-in-index.

## Buckets
- IN-COVERAGE (>=1 gold atom in index), 7q: Q54, Q55, Q60, Q61, Q62, Q63, Q64
- COVERAGE-GAP (no gold in index), 6q: Q56, Q57(D-boolean), Q58, Q59, Q65, Q_neg_2

## (a) IN-COVERAGE macro-F1 = 0.029  -> HARD_FAIL (<0.50)

| q | tp | fp | fn | F1 | behavior |
|---|---|---|---|---|---|
| Q54-A | 0 | 5 | 5 | 0.00 | hallucinated 5, retrieved 0 of present gold |
| Q55-B | 0 | 0 | 1 | 0.00 | returned nothing |
| Q60-G | 0 | 0 | 4 | 0.00 | returned nothing |
| Q61-A | 1 | 4 | 4 | 0.20 | partial |
| Q62-B | 0 | 0 | 6 | 0.00 | returned nothing |
| Q63-A | 0 | 5 | 5 | 0.00 | hallucinated 5 |
| Q64-G | 0 | 0 | 3 | 0.00 | returned nothing |

**This is the deeper finding (DECISION 32 HARD_FAIL branch): capability does NOT transfer to held-out even when gold atoms ARE in the index.** Only Q61 got a single TP. The rest either returned nothing (refused on present-gold queries -> missed real answers) or hallucinated wrong atoms. So the 0.022 is NOT purely a coverage artifact -- the retrieval/answer capability itself does not generalize to untuned held-out phrasing. (Caveat: these in-coverage questions have MIXED gold -- e.g. Q54 has 1/5 gold present -- so full-gold F1 is also coverage-capped; but even recall-on-present-gold is ~0.04, so the conclusion holds.)

## (b) COVERAGE-GAP refuse-rate = 0.67 (4/6)  -> NOT ROBUST (target >=0.95)

| q | fp | refused? |
|---|---|---|
| Q56-C | 0 | YES (returned nothing) |
| Q57-D | (boolean: no-path) | YES (correct no-path) |
| Q58-E | 0 | YES |
| Q65-E | 0 | YES |
| Q59-F | 26 | NO -- hallucinated 26 FPs |
| Q_neg_2 | 5 | NO -- hallucinated 5 FPs |

**Refuse-rate 0.67 -- between HARD-FAIL (0.50) and HARD-PASS (0.95). The 18th-rule refuse-discipline is PARTIAL, not robust:** it refuses ~2/3 of unknown-topic queries but hallucinates ~1/3 (Q59 with 26 FPs is the worst). Confirms Cause 2 (refuse-discipline doesn't generalize) -- the categorical soundness gap.

## Honest synthesis (both directions)
- The substrate has TWO real held-out gaps, BOTH failing their bars: capability-transfer (IN-COVERAGE 0.029) AND refuse-robustness (COVERAGE-GAP 0.67). 
- The IN-COVERAGE 0.029 is MORE concerning than the retraction framed -- it's not just "69% coverage gap"; even on present-gold, capability doesn't transfer. The DECISION 32 split surfaced this (it would have been hidden in the aggregate 0.022).
- DECISION 33 (refuse-discipline M1 confidence-calibration) addresses (b). But (a) -- capability not transferring even with coverage -- is a separate, deeper retrieval-generalization gap that M1 won't fix (M1 makes it refuse MORE, which raises (b) refuse-rate but lowers (a) recall further). There is a real precision/recall tension: the substrate already refuses on 4/7 in-coverage queries (returned nothing) -- MORE refusal hurts (a).

## Recommendation
- (b) DECISION 33 M1 (confidence calibration) will raise COVERAGE-GAP refuse-rate toward 0.95 -- good for soundness. I can run it (my F1-BRIDGE H1 tau-gate IS this mechanism; tau=0.80 cut FP 70.6pct). But watch the (a) tradeoff: it must NOT push in-coverage recall lower (already 0.029). Falsifier: IN-COVERAGE F1 must not drop > 0.05 (it's near floor already).
- (a) capability-transfer is the harder, separate problem (untuned-phrasing retrieval generalization) -- likely needs query-side robustness (paraphrase-invariant retrieval), not just a refuse gate. Flagging as distinct from DECISION 33.

Both numbers tagged. Ready to run DECISION 33 M1 on your go (I have the tau-gate mechanism).

-- EXP-DEV (Prover)
