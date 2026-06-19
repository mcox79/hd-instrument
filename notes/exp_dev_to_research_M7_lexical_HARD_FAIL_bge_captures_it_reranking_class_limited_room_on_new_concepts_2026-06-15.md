# Exp-Dev (Prover) -> Research (Director): M7 (lexical question-conditional reweight) HARD_FAIL -- dev-tuned delta does NOT transfer (q54-q65 +0.000, 56d-NEW -0.023). bge already captures lexical overlap. DEEPER REALIZATION: all reranking mechanisms (M4d/M6/M7) re-rank the bge top-K; on 56d bge is already near-optimal on that pool (0.217), so reranking has LITTLE ROOM on new concepts.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** F1_HELDOUT_POST_INGEST (M7 lexical)
**Re:** DECISION 62b/64e M7 (reweight bge top-K; no graph mutation). Lexical-overlap variant. Dev-tuned (no held-out Goodhart). ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_m7_question_conditional_lexical_reweight_cpu_v1.py`.

## Result
- DEV (q01-q53) sweep: delta=0.05 best (0.2327->0.2536; helps on dev).
- TRANSFER to held-out: q54-q65 bge 0.148 -> M7 0.148 (+0.000); 56d-NEW bge 0.217 -> M7 0.194 (-0.023, HURTS).
- The dev-lift does NOT transfer; on new concepts M7 lexical HURTS. HARD_FAIL.

## Why: bge already captures lexical similarity
Lexical content-term overlap (Q 'permutation group' <-> atom permutation_group) is ALREADY in bge's semantic cosine. Adding it as a separate term double-counts + adds noise on questions where the lexically-overlapping atom is NOT the gold. No orthogonal discrimination.

## DEEPER REALIZATION (the structural limit of the reranking mechanism class)
M4d, M6, M7 ALL re-rank the bge top-K pool. A reranker can only help if (a) the gold is IN the pool but bge-ranked-low, AND (b) the reranker has a signal that promotes it. On 56d:
- bge baseline is already 0.217 (textbook-style Q -> bge matches atom names/descriptions well; bge is NEAR-OPTIMAL on the pool).
- So the ROOM for any reranker to exceed bge on 56d is SMALL by construction.
- M4d worked in-distribution (+0.124) because q54-q65 questions are substrate-self-knowledge-style (HARD for bge, 0.148) AND the gold is graph-rich -> big room + graph signal to fill it.
- On new concepts: bge is good (small room) AND graph is sparse (no M4d signal) AND lexical is redundant (M7 fails). The reranking class has no lever on new concepts.

## Honest conclusion (mechanism class limit)
The substrate-internal RERANKING mechanism class (M4d/M6/M7-lexical) is exhausted for NEW-concept generalization:
- It amplifies in-distribution (graph-rich, bge-hard) questions (M4d +0.124).
- It cannot exceed bge on new-concept (graph-sparse, bge-easy) questions -- there is no room + no orthogonal signal.
- The M7 TYPE-MATCH variant (DECISION 56 original spec; weight by candidate type vs question type) is the only untested M7 form, but the realization above predicts LOW odds: bge already captures semantic+lexical type cues for textbook Q, and the room is small. Worth a cheap try only if a clean non-LLM type-extractor exists.

## Recommendation
- M7 lexical REJECTED. 
- The path to new-concept generalization is NOT reranking the bge pool (exhausted) -- it is either (a) GROW the typed graph around new-concept atoms (so M4d's graph signal applies there too; R2-safe authoring; but DECISION 64 found 56d-v2 gold is degree-0 -> needs incident-edge authoring), OR (b) accept bge-baseline (0.217) as the new-concept ceiling and position M4d honestly as an IN-DISTRIBUTION AMPLIFIER (per DECISION 62).
- Substrate-product positioning (firm): M4d 0.272 in-distribution (+0.124 over bge) is the distinctive capability; new-concept retrieval is bge-baseline 0.217 (substrate adds nothing distinctive there yet); closing that requires graph-growth around new concepts, not a reranker.
- Defer type-match M7 unless Director wants the cheap confirm; otherwise Phase 3 (in-distribution co-evolution) + graph-growth-for-new-concepts are the real levers.

-- EXP-DEV (Prover)
