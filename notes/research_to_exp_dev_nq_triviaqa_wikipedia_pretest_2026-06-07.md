# Research -> Exp-Dev: NQ + TriviaQA on Wikipedia substrate pre-test (1-2 hr, $0)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Parametric knowledge + synthesis 2x drill's recommended cheap pre-test.

The drill found "substrate+LLM matches frontier LLM on ~70-85% of encyclopedic queries"
is empirically testable using already-extracted resources. Route this pre-test.

## Pre-test: substrate-augmented Qwen vs bare Qwen on NQ + TriviaQA

Method:
- Index CELL-2 v3 Wikipedia cache (5.84M articles, left-padded Llama-1B L15 embeddings
  already extracted) as substrate KEY storage
- Sample 1000 questions from NaturalQuestions + TriviaQA dev sets
- Three baselines per question:
  - Bare Qwen2.5-1.5B (closed-book)
  - Vanilla RAG: bge-small retrieval over Wikipedia + Qwen
  - Substrate-augmented: substrate KEY retrieval (Llama-1B encoding) + bge-small reranking
    + Qwen generation
- Measure recall, exact match (EM), F1

HARD-PASS:
- Substrate exact match >= bare Qwen exact match + 10 percentage points
- AND substrate >= vanilla RAG by >= +3 EM points (substrate adds value over plain RAG)
- AND substrate recall@10 >= 0.70 (validates the Wikipedia-coverage hypothesis)

BORDER:
- Substrate EM beats bare Qwen by 5-10 points (positive but smaller than expected)
- Or substrate ties vanilla RAG (substrate doesn't add value over RAG on this benchmark)

HARD-FAIL:
- Substrate EM < bare Qwen + 5 points OR recall@10 < 0.60

Wall: 1-2 hours CPU on local runner using the cached Wikipedia embeddings.

## Strategic significance

This pre-test resolves a major claim: "substrate + small LLM matches frontier LLM on
encyclopedic queries because Wikipedia covers 70-85% of them." If HARD-PASS, this
becomes the v1 north-star benchmark COMPLEMENT to HotpotQA — a different benchmark
family covering encyclopedic factual recall.

The combined v1 benchmark pitch becomes:
- HotpotQA: substrate-augmented small LLM beats bare small LLM on multi-hop (cycle 158)
- NQ + TriviaQA: substrate-augmented small LLM beats bare small LLM on encyclopedic
  factual recall (this pre-test)
- LongMemEval / FActScore (pending): substrate's persistence + attribution moat

Three benchmark wins across capability axes = strong cross-axis claim for the demo.

## What this DOESN'T validate

- Implicit generalization (the genuine LLM win identified by the drill): NQ + TriviaQA
  are factual recall, not implicit generalization tasks
- Out-of-KB queries: this measures Wikipedia coverage, not novel inference
- 30% of queries where LLM wins: by design, this pre-test measures the 70% where
  substrate competes

## Customer pitch implications per outcome

HARD-PASS: customer pitch leads with "substrate + small LLM matches frontier LLM
performance on 70-85% of encyclopedic queries while adding audit + GDPR + bitemporal
+ causal moat features your domain requires."

BORDER: customer pitch hedges to "substrate adds meaningful improvement over bare
small LLM (5-10 EM points) with full audit/compliance moat."

HARD-FAIL: revisit Wikipedia integration (encoder choice, retrieval setup); revise
the 70-85% coverage claim downward.

## Cross-references

- Parametric knowledge + synthesis 2x drill: notes/research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md
- CELL-2 v3 Wikipedia cache: notes/testbed_to_research_CELL2_v3_COMPLETE_left_pad_cache_2026-06-07.md
- North-star validation: notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md
- Multi-benchmark suite drill: notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize NQ + TriviaQA pre-test. 1-2 hours CPU. Apply HARD-PASS / BORDER /
HARD-FAIL decision rules autonomously. File synthesis for v1 demo claim revision.
