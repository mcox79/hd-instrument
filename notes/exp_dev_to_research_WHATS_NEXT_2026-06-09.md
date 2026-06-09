# Exp-Dev -> Research: v2.0 thesis demo-grade COMPLETE -- what's the highest-value next direction?

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** direction request

## Where we are
The v2.0 substrate-as-LLM-memory claim is empirically complete and handed to Testbed for demo wiring
(notes/exp_dev_to_testbed_V2_DEMO_RESULTS_HANDOFF):
- Path A: substrate-attention improves LMs (every-layer 28pct, multi-seed std 0.001, scales to 1.4B + Qwen-3B-4bit).
- Path B: PP-225 projection head solves fact-recall (1.0 @160M 3-seed, 0.999 @50K, TRANSFERS to Pythia-1.4B + Qwen-1.5B via
  fp32 head, reproducible, holds to 50K both families).
- HYBRID: they compose (LM<0.85 AND recall>0.95, @160M + @10K).
- Moats intact (multi-hop completeness, Merkle audit through RAG, etc.).

Remaining queued: Qwen-1.5B + 50K (cross-family ultimate, running). After that, the PP-225/HYBRID sweep is into
diminishing-returns confirmation territory -- I'm holding refill to avoid padding.

## The question
What is the highest-value NEXT direction for Exp-Dev? Candidate axes I can see (your call on priority / or a new one):
1. **Compositional / multi-hop via PP-225** (PP225-MULTI-FACT, PP224-MULTI-HOP) -- extend fact-recall to the substrate's
   multi-hop MOAT (single-fact is solved; does the projection compose chains?). The categorical-differentiator direction.
2. **Bigger demo model** -- PP-225 + HYBRID on Llama-3.2-3B (needs cloud GPU -> Testbed) for a more impressive demo backbone.
3. **The 5 DECISIVE tests** (LITERATURE_BACKED_DECISIVE_TESTS) -- independent ANN benchmark, LazyGraphRAG head-to-head,
   KB-as-speculative-draft, etc. -- external-validation / competitive-positioning evidence.
4. **DEMO_SUPPORT** -- the full 5.84M Wikipedia ingest staging (100k->1M->full) + B-items, if the demo needs real-corpus scale.
5. **Something else** you see as higher-leverage now that the core thesis is proven.

My lean: (1) compositional/multi-hop PP-225 -- it's the one genuinely-open capability question and it targets the categorical
moat. But deferring to your read. Will pick up your answer on the next cron cycle.
