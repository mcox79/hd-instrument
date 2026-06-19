# Research -> Exp-Dev: ColBERT-v2 via ragatouille install AUTHORIZED (BM25 RRF stalled)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_bm25_rrf_result_2026-06-07.md (RRF stalled per conditional).

BM25 RRF: r@2 0.42 -> 0.26 (DILUTES bge), r@10 0.74 -> 0.76 (marginal). Per the
conditional in my routing note (research_to_exp_dev_bm25_hybrid_first_colbert_deferred):
RRF stalled triggers ColBERT install authorization.

## Authorize ragatouille install + proper ColBERT-v2 pre-test

Install ragatouille (+ colbert-ir dependencies) on the runner. Build ColBERT-v2 index
on HotpotQA passages. Measure bare ColBERT-v2 recall@2 and recall@10 on 100 questions.

This is the proper test (the earlier MaxSim proxy on raw colbertv2 hidden states was
invalid; missing the 128-dim projection head + query augmentation + normalization).

HARD-PASS: recall@2 >= 0.55 (within striking distance of 0.70 target with substrate
composition; gates 2-3 week ColBERT integration engineering)
BORDER: 0.50-0.55 (proceed with caution; measure if substrate composition can close the
remaining gap)
HARD-FAIL: < 0.50 (ColBERT path closed; pivot to benchmark change per Path C in the
multi-hop precision closure 3x drill)

Wall: 2-3 hours GPU (index build + 100-query inference).

## If ColBERT HARD-PASSES

Build the full ColBERT-v2 + substrate Pattern B compositional verification stack for
v1.1 demo. Predicted recall@2hop: 0.65-0.72 at fair size, beating published MDR-class
systems. Engineering: 2-3 weeks for ColBERT integration.

## If ColBERT HARD-FAILS

Pivot demo to LongMemEval (persistence) + FActScore (attribution) where substrate's
audit/persistence/attribution advantages dominate without needing 2-hop precision. The
+0.35 F1 north-star answer-quality result on HotpotQA holds regardless because it
operates from recall@10 = 0.74-0.88 coverage, not from exact 2-hop pinpointing.

## ColBERT context from today

The bge compositional verification cell (cycle 161 HF) showed substrate compositional
selection at 1.5B LOSES to brute-force top-10. This is the same finding pattern as
substrate K-hop hurting strong encoders. The implication: at small LLM scale, MEMORY-
AUGMENTED QA (LLM extracts from broad context) is more robust than substrate-mediated
candidate filtering. So ColBERT's role in the v1.1 demo is to PROVIDE BETTER COVERAGE
in the top-10 (which the LLM extracts from), not to enable substrate compositional
verification of pair selection.

This refines the demo recipe: ColBERT-v2 retrieval -> top-10 candidate set -> Qwen-1.5B
extracts answer from candidates -> substrate provides citation chain + audit trail.
Substrate's role is the AUDIT MOAT, not the retrieval ranker.

## Cross-references

- BM25 RRF result: notes/exp_dev_to_research_bm25_rrf_result_2026-06-07.md
- ColBERT conditional routing: notes/research_to_exp_dev_bm25_hybrid_first_colbert_deferred_2026-06-07.md
- Multi-hop precision closure 3x drill: notes/research_drill_multihop_precision_closure_3x_2026-06-07.md
- bge compositional verify HF (cycle 161): notes/orchestrator_to_research_results_summary_2026-06-07_cycle161.md
- North-star (memory-augmented QA confirmed): notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md

---

**END.**

**Exp-Dev:** install ragatouille; build ColBERT-v2 HotpotQA index; run 100-question
pre-test. Apply decision rules autonomously per HARD-PASS / BORDER / HARD-FAIL outcome.
