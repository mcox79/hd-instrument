# Research -> Exp-Dev: ColBERT-v2 + BM25-hybrid pre-tests (multi-hop precision closure)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Multi-hop precision closure 3x drill output.

Authorize both pre-tests. ColBERT is the gating decision for 2-3 week integration;
BM25-hybrid is a cheap parallel test for floor lift. Both run on existing HotpotQA harness.

## 1. ColBERT-v2 bare pre-test (PRIORITY 1; gating)

Goal: measure bare ColBERT-v2 recall@2 and recall@10 on HotpotQA 2-hop without iterative
logic or fine-tuning. This single result decides whether the ColBERT engineering path is
worth the 2-3 week investment.

Method:
- Ragatouille ColBERT-v2 index build on HotpotQA-distractor passages
- 100 HotpotQA bridge questions
- Measure recall@2 and recall@10
- Compare to bge-small naive baseline (recall@2=0.42, recall@10=0.74)

HARD-PASS: recall@2 >= 0.55 (within striking distance of 0.70 with substrate composition)
BORDER: 0.50-0.55 (proceed with caution; measure if substrate composition can close
the remaining gap)
HARD-FAIL: < 0.50 (ColBERT path closed; pivot to benchmark change)

Wall: 2-3 hours GPU runner.

## 2. BM25 + bge-small RRF hybrid pre-test (PRIORITY 2; cheap parallel)

Goal: measure whether BM25 + bge-small reciprocal rank fusion gives floor lift over
bge-small alone. Composites with substrate Pattern B pair verification.

Method:
- BM25 retrieval top-10
- bge-small retrieval top-10
- RRF fusion to combined top-10
- Measure recall@2 and recall@10 on same 50-100 HotpotQA questions

HARD-PASS: recall@2 >= 0.50 (5-10 percentage points lift over bge-small alone)
BORDER: 0.45-0.50 (marginal lift; informative)
HARD-FAIL: <= 0.42 (no lift; abandon hybrid path)

Wall: 2-3 hours CPU.

## Decision tree

ColBERT HARD-PASS AND substrate Pattern B pair verification (queued separately) HARD-PASS:
- v1.1 demo recipe: ColBERT-v2 + substrate Pattern B verification + Llama-1B generation
- Predicted recall@2hop: 0.65-0.72 at fair size, beating published MDR-class systems
- Engineering: 2-3 weeks for ColBERT integration; substrate Pattern B compositional
  verification is 1-2 weeks separately

ColBERT HARD-PASS, Pattern B verification HARD-FAIL:
- v1.1 demo recipe: ColBERT-v2 alone + Llama-1B (no Pattern B layer)
- Predicted recall@2hop: 0.55-0.65 at fair size
- Engineering: 2-3 weeks for ColBERT integration only

ColBERT BORDER, Pattern B HARD-PASS:
- v1.1 demo recipe: bge-small + BM25 hybrid + Pattern B verification
- Predicted recall@2hop: 0.55-0.65
- Engineering: 1-2 weeks; lower cost than full ColBERT integration

ColBERT HARD-FAIL:
- Benchmark pivot to LongMemEval (persistence) + FActScore (attribution)
- The +0.35 F1 north-star result + audit + GDPR + bitemporal + causal + qualified
  privacy story carries the demo without HotpotQA multi-hop precision
- Engineering: minimal (already-validated substrate; new benchmarks to test)

## Strategic context: scaling LLM is NOT the answer

The drill found published evidence (2412.12841 + 2509.21199) that the compositionality
gap at small LLM sizes does NOT close with parameter count. 3B or 7B will not close
where 1.5B failed. This is architectural, not parameter-count. So the only fair-size
paths to closure are:
- Late-interaction retrieval (ColBERT)
- Substrate-native compositional decomposition (Pattern B)
- Hybrid combinations

LLM-decomp at any fair-size scale is conclusively closed for multi-hop bridging.

## What does NOT need to change

The +0.35 F1 north-star result on HotpotQA answer-quality is defensible even if 2-hop
retrieval precision plateaus at 0.42. Memory-augmented QA works because the LLM extracts
good answers from broad top-10 context (recall@10 = 0.74); it doesn't need exact bridge
pinpointing. So the demo headline can stand on answer-quality even in the ColBERT
HARD-FAIL scenario.

## Customer pitch implications

ColBERT HARD-PASS: substrate v1.1 competes on retrieval precision against MDR-class at
fair size, plus audit moat. Strong pitch for compliance-required customers.

ColBERT HARD-FAIL + benchmark pivot: substrate pitches on persistence (LongMemEval),
attribution (FActScore), audit + GDPR + causal + qualified privacy. Pivot lands on
substrate's structural differentiators rather than retrieval competition.

Either pitch is defensible. The technical roadmap differs.

## Cross-references

- Multi-hop precision closure 3x drill: notes/research_drill_multihop_precision_closure_3x_2026-06-07.md
- Multi-hop closure handoff: notes/exp_dev_handoff_research_multihop_precision_closure_2026-06-07.md
- Multi-hop fair-size ceiling (cycle 158 closure of LLM-decomp): notes/exp_dev_to_research_multihop_fairsize_ceiling_2026-06-07.md
- North-star validation: notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md
- Three-paths v1 benchmark resolution: notes/research_to_exp_dev_three_paths_v1_benchmark_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize both pre-tests. ColBERT GPU first; BM25-hybrid CPU in parallel.
Apply decision tree autonomously. File synthesis with both results so I can route the
v1.1 demo recipe selection.
