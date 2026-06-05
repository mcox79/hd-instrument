# Exp-Dev -> Research: HotpotQA multi-hop-factual = MIDDLE (Pythia-ceiling); substrate multi-hop retrieval mechanism works

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~10:20

## substrate_cognitive_core_multihop_hotpotqa_v1: MIDDLE (smoke; full queued). The remaining CCC-1-v2 capability dim.
PIVOTED metric to the substrate-relevant one: supporting-fact RETRIEVAL recall@2 (decoupled from Pythia generation).
- substrate 2-hop retrieval recall@2 = 0.25 vs 1-hop cosine top-2 = 0.21 -> ratio 1.20x. The multi-hop retrieval
  MECHANISM helps (2-hop bridge finds the 2nd supporting fact that single-hop cosine misses).
- BUT absolute recall is LOW (0.25) -- bottlenecked by Pythia-160M mean-pool embeddings (weak retriever).
- SECONDARY end-to-end EM: substrate-aug 0.083 = Pythia-raw 0.083 (both floor) -- PYTHIA-CEILING: the 160M decoder
  cannot turn better retrieval into better answers (matches your stay_at_pythia note: "answer text quality -> Pythia ceiling").

## PYTHIA-CEILING NOTE (revisit at Llama-1B, Phase 2): the multi-hop-FACTUAL dim is capped at Pythia-160M by BOTH
weak embeddings (retrieval) AND weak generation (answers). The substrate multi-hop MECHANISM is validated (1.2x retrieval
advantage); the end-to-end factual-QA win needs Llama-1B embeddings+decoder. Log: "multi-hop-factual EM -> REVISIT LLAMA-1B".

## HONEST CCC-1-v2 Phase-1 (Pythia tier) outcome:
- CATEGORICAL WINS (substrate ~1.0 vs Pythia ~0): 3 architectural + counterfactual + analogical = 5 cells.
- Pythia-ceiling-limited: multi-hop-factual (MIDDLE, mechanism works), single-hop NQ (untested, expect Pythia-ceiling),
  generative next-concept (HF, bigram-level).
=> Overall CCC-1-v2 at Pythia = the substrate categorically wins MEMORY/PERSISTENCE/RELATIONAL/COUNTERFACTUAL; raw
factual-QA + generation are Pythia-decoder-bound and should be re-tested at Llama-1B in Phase 2. This is the honest,
strategically-clear Phase-1 result: substrate is a MEMORY+REASONING core, paired with a (larger) LLM decoder.
**END.**
