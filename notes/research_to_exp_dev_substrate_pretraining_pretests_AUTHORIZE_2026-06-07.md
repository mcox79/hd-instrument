# Research -> Exp-Dev: substrate pre-training 3 pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Substrate pre-training 3x drill output.

Per blanket Exp-Dev authorization + user's "not sending this thing out a virgin" mandate.

## Authorize all 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_substrate_pretraining_2026-06-07.md`.

### Pre-test 1 (PRIMARY GATE): CELL-2 v3 Pattern B compression + NQ + TriviaQA recall@5
~2 hr CPU. Uses existing CELL-2 v3 cache (5.84M Wikipedia articles, L15 embeddings).

Method: compress L15 embeddings to Pattern B 16-byte format; build HNSW index;
measure NQ-open + TriviaQA recall@5 on substrate-only retrieval.

HARD-PASS: recall@5 >= 65% on NQ-open AND >= 70% on TriviaQA (encoder-Pattern B
combination viable).
HARD-FAIL: < 50% on either (L15 encoder not suitable for Pattern B compression
at this scale; architecture needs debugging before v1.1 engineering investment).

This is the PRIMARY GATE per drill. If HF, the entire pre-training direction needs
revisit before 1-2 week engineering investment.

### Pre-test 2: Bridge coverage measurement on HotpotQA
~1-2 hr CPU. Quantify: how much does pre-trained Wikipedia substrate raise cold-start
bridge coverage for HotpotQA?

HARD-PASS: bridge coverage >= 80% on HotpotQA bridge questions (validates drill
prediction; closes multi-hop revival path structurally).
BORDER: 70-80%.
HARD-FAIL: < 65% (no improvement over no pre-training; bridge coverage doesn't
benefit from Wikipedia pre-load as much as predicted).

### Pre-test 3: Exact match (EM) improvement on encyclopedic Q&A
~2-3 hr CPU. Substrate + Qwen-1.5B with pre-trained Wikipedia vs bare Qwen-1.5B.
Run on 200 NQ + TriviaQA questions; measure EM delta.

HARD-PASS: substrate-augmented Qwen EM >= bare Qwen + 0.15 (substantial parametric
gap closure; substrate + small LLM matches frontier LLM on encyclopedic queries).
BORDER: +0.05 to +0.15.
HARD-FAIL: < +0.05.

## v1.1 ship pathway if pre-tests pass

1. Build distributable 93 MB binary base substrate (1 week eng)
2. Customer overlay mounting layer (Pattern B composes base + customer)
3. Two-layer query routing (Layer 1 score-threshold; fallback Layer 0)
4. Documentation + integration guide

Total: 1-2 weeks eng to v1.1 deployable pre-trained substrate.

## Cross-references

- Pre-training 3x drill: notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_substrate_pretraining_2026-06-07.md
- Unified synthesis: notes/research_to_exp_dev_3_drills_unified_routing_2026-06-07.md

---

**Exp-Dev:** authorize 3 pre-tests. PT1 (NQ+TriviaQA recall@5) is the PRIMARY GATE; if
HF, v1.1 engineering investment is NOT justified. Apply HARD-PASS/HARD-FAIL autonomously.
