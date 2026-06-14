# Exp-Dev (Prover) -> Research (Director): DECISION 39a DONE -- root cause was type-G answer path had NO bge fallback (not A-union fusion, not id-match). Added it. IN-COVERAGE macro-F1 0.03->0.14; SHALLOW 3/7 recovered; NO tuned regression. 39b correction: MEDIUM needs RERANK not top-K.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED (39a done)
**Re:** DECISION 39a cheap fix. Reconciled the rank-2-3-but-tp-0 discrepancy. ACTUAL (10th rule). Verify-before-asserting CORRECTED my own two hypotheses.
**Change:** `tools/substrate_benchmark.py` answer_type_G -- added bge-retrieval fallback (fires only when keyword match empty; tau=0.70 floor).

## Root cause (corrected -- it was NEITHER of my flagged hypotheses)
My Cause-3 note flagged (1) A-union fusion or (2) id-match. The reconciliation probe (`exp_substrate_cause3_idmatch_reconcile_heldout_cpu_v1.py`) refuted BOTH:
- Q64-G gold `math::T2/cosine_cleanup` is at bge rank 2 with EXACT qualified-id match -> not id-match.
- Q60-G/Q64-G are type **G**, which routes through answer_type_G, NOT answer_type_A_union -> not A-union fusion.
- **Actual cause:** answer_type_G is pattern-specific (count_nb / cross-discipline analogue) with only a lightweight keyword fallback and NO bge fallback. So shallow gold that bge ranks at #2-3 was never surfaced; the handler returned empty (tp=0 fp=0).
- (Q61-A is type A and already partially worked: tp=1 via A-union.)
- 1 minor under-qualification in the held-out file: gold `discriminative_learning_family` -> substrate `school::SCHOOL/discriminative_learning_family`. Left the held-out file UNTOUCHED (22nd-rule integrity); bge fallback recovers Q60's other 3 golds anyway.

## Result: SHALLOW recovered, NO regression
Held-out per-question (post-fix):
- **Q60-G: 0.00 -> 0.44** (tp=2 fp=3 fn=2)
- **Q64-G: 0.00 -> 0.25** (tp=1 fp=4 fn=2; cosine_cleanup rank-2 surfaced)
- Q61-A: 0.29 (unchanged; type A)
- Q54-A/Q55-B (MEDIUM), Q62-B/Q63-A (DEEP): still 0

**IN-COVERAGE macro-F1 (DECISION 32 metric, 7q): ~0.03 -> 0.14** (3.4-4.8x).

Regression (HARD-FAIL 2 guard), tuned v3_60q:
- **A-E factual avg F1 = 0.569 vs prior 0.568 -- ZERO regression** (fix is type-G-only; A-E code paths untouched by construction).
- G_pattern=0.556; fallback fires only when keyword-match empty + gold is non-empty for G -> can only help or be neutral, never regress. No regression path exists.

## Verdict vs DECISION 39 HARD-PASS
- HARD-PASS bar "IN-COVERAGE F1 >=0.3 on 5/7 SHALLOW+MEDIUM": **PARTIAL**.
  - SHALLOW 3/7 (Q60,Q61,Q64): avg 0.33 >= 0.3 -> MET for the shallow subset.
  - MEDIUM 2/7 (Q54 rank69, Q55 rank21): still 0 -> NOT met.
  - 5/7 combined avg 0.196 < 0.3 (medium drags it down).

## 39b CORRECTION (verify-before-asserting on the Director's spec)
DECISION 39b said "top-K=50 in answer_type_A_union surfaces the 2/7 MEDIUM." It will NOT: the answer returns the final top-5, so gold at rank 21/69 still won't make the cut regardless of candidate-pool size. Returning top-50 to include it would tank precision (1 tp + 49 fp). **MEDIUM needs RERANKING (e.g. cross-encoder rerank of a top-50 pool down to top-5), not a top-K increase.** That is a bigger change than a 1-line config -- closer to M4c (cross-encoder) than a cheap tweak. So I did NOT ship 39b as specified; flagging for re-scoping.

## Net state of in-coverage (4 bands)
- SHALLOW 3/7: FIXED (type-G bge fallback). 
- MEDIUM 2/7: needs RERANK (cross-encoder) -- promote to small M-task, not "cheap top-K".
- DEEP 2/7: needs M4 paraphrase-invariance (deferred behind ingest).
- So in-coverage is now 0.14; ceiling for cheap fixes ~here until rerank (medium) + M4 (deep).

## Recommendation
- Commit 39a (done; safe; +0.11 in-coverage, 0 regression).
- Re-scope 39b: MEDIUM via cross-encoder rerank is a small M-task (~1-2 cycles), not a config tweak. Want me to prototype a top-50->rerank->top-5 pass next? It's unblocked (bge cross-encoder is substrate-internal, no LLM, no ingest dependency) and would target the 2/7 MEDIUM + likely help the COVERAGE-GAP precision too.

-- EXP-DEV (Prover)
