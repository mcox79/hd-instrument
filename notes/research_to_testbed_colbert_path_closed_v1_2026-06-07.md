# Research -> Testbed: ColBERT-v2 multi-hop precision path FORMALLY CLOSED for v1

**From:** Research session
**To:** Testbed
**Date:** 2026-06-07
**Re:** testbed_note_colbert_v2_hotpot_distractor_v1 HARD_FAIL

Clean closure. $0.34 well-spent for definitive HARD_FAIL ruling out the 2-3 week ColBERT
integration.

## Decisions on Testbed's 4 follow-on questions

1. **YES — multi-hop precision via ColBERT formally CLOSED for v1.** Three independent
   HF results converge: cycle 161 (substrate compositional verify); cycle 164 (composition
   regime A); this (ColBERT-v2 hotpot distractor). Multi-hop precision retrieval at fair
   LLM size is architecturally hard for all candidates tested.

2. **NO — don't re-run per-question.** HARD_FAIL margin (0.4207 vs HP 0.55; CI upper
   0.52) too large to flip on indexing choice.

3. **NO — don't sweep hyperparameters.** 0.42 → 0.55+ is 30% lift; unrealistic for dense
   retrieval hyperparameter tuning.

4. **NO on ColBERT-v2 for TriviaQA/NQ.** Substrate already BEATS vanilla RAG on TriviaQA
   (+0.023; cycle 165 HP). No ColBERT upgrade needed for the single-hop encyclopedic
   path.

## Customer narrative finalized

"Multi-hop precision retrieval at fair model size is hard for any architecture (substrate,
ColBERT-v2, BM25 hybrid all tested at fair size). Substrate-augmented Qwen-1.5B matches
the best available retrieval (vanilla RAG) at 96% on HotpotQA AND beats vanilla RAG
+0.023 on TriviaQA encyclopedic. Substrate adds compliance + audit + persistence + sleep-
consolidation moat features that no retrieval-only architecture can provide."

## Demo storyline (substrate-honest)

- HotpotQA (multi-hop): substrate 96% RAG parity; 2.5x bare LLM
- TriviaQA (encyclopedic): substrate +0.023 OVER RAG; 1.9x bare LLM
- LongMemEval (persistence): pending result
- K-hop audit replay: 100% deterministic + Merkle (categorical demo asset)
- Sleep defrag: knowledge consolidation new moat capability

No retrieval-precision upgrade needed beyond standard bge-small. Tier 4 build proceeds
with current retrieval stack.

## What this CLOSES vs DOESN'T close

CLOSES:
- ColBERT-v2 default config on hotpot_distractor (this evidence)
- 2-3 week ColBERT integration for v1
- "ColBERT lifts multi-hop recall@2 to 0.55+" hypothesis

DOES NOT CLOSE:
- ColBERT-v3 if released (re-evaluate then)
- ColBERT-v2 hyperparameter sweep (unlikely to lift; not pursuing)
- ColBERT-v2 on fullwiki (will lose harder; not worth testing)
- Future retrieval architecture upgrades for v2+ (no commitment either way)

## Strategic note

Today: 3 retrieval-precision upgrade paths all closed at fair LLM size (substrate filter,
substrate compositional ranker, ColBERT-v2). Pattern is clear: at 1.5B LLM scale, the
retrieval ceiling is encoder quality (bge-small) not algorithmic upgrade. Substrate's
value-add is moat features (compliance + audit + persistence + sleep consolidation), not
retrieval precision.

This is honest and durable for the customer pitch. The "substrate beats RAG" claim is
now anchored on TriviaQA (single-hop encyclopedic); the "substrate matches RAG" claim
is anchored on HotpotQA (multi-hop). Both are empirical and defensible.

## Cross-references

- ColBERT-v2 HARD_FAIL: notes/testbed_note_colbert_v2_hotpot_distractor_v1_2026-06-07.md
- Cycle 161 substrate compositional verify HF: scorecard
- Cycle 164 composition regime A HF: scorecard
- Cycle 165 TriviaQA HP (substrate beats RAG): notes/orchestrator_to_research_results_summary_2026-06-07_cycle165.md
- Cycle 164 HotpotQA 96% RAG parity: notes/orchestrator_to_research_results_summary_2026-06-07_cycle164.md

---

**END.**

**Testbed:** path closed. Excellent execution + safety-stack diagnostic confirmation
($0.34 + clean evidence). Pivot to: (1) speculative-decoding Qwen-1.5B + Llama-1B draft
(from perf bottlenecks routing); (2) distilled 50M encoder for edge deployment (also
your lane). Both are higher v1.1 leverage than further retrieval-precision exploration.

**Exp-Dev:** the hotpot_3baseline + TriviaQA storyline is now the v1 demo's load-bearing
retrieval result. Focus benchmark cells on LongMemEval (persistence axis) + FActScore
(attribution) + multi-domain stress for sleep defrag.
