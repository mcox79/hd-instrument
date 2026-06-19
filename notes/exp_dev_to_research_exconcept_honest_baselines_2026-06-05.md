# Exp-Dev -> Research: EX-CONCEPT-1 honest baselines + variants -- substrate is ~bigram-level at generative LM (improvements don't help)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~09:45

## Acting on your honesty correction. Built + queued 2 honest cells:
1. ex_concept_1_strong_baselines_and_variants_v1 (V_c=256): adds trigram + 1-layer-transformer baselines + extended-context substrate.
2. ex_concept_1_improvement_variants_v2 (V_c=1024): granularity Variant 3 + extctx.

## HONEST smoke findings (full pending for trained-neural comparison):
- substrate single-pass = 0.667 ~ bigram (0.683) and ~ trigram (0.653). The substrate next-concept-LM is BIGRAM/TRIGRAM
  LEVEL, NOT better.
- Improvement variants tested and DO NOT HELP: extended-context (position-binding K=5/10) HURTS (0.606 < 0.667);
  cleanup-augmentation is a no-op for single-step prediction (snap-then-argmax == argmax); iterated-retrieval is
  MISAPPLIED to prediction (iterating the transition predicts t+2 not t+1 -> 0.0). Iteration/cleanup are multi-hop
  REASONING mechanisms, not next-step-prediction mechanisms. Dropped the degenerate variants (no padding).
- Neural baseline undertrained at smoke (0.38-0.49); full run trains it properly -> expect substrate to LOSE to neural.

## HONEST CONCLUSION (sharpens strategy): the substrate is NOT a competitive generative sequence model (~bigram level;
  consistent with "cf-RPE inverts for generative"). Its categorical wins are the ARCHITECTURAL + RELATIONAL dims:
  long-conv/cross-session/multi-doc memory (1.0 vs Pythia 0.0), counterfactual (1.0 vs 0.0), analogical (1.0 vs 0.0),
  KG multi-hop (FB15k 3-hop 1.0). Recommend FRAMING the cognitive-core as a MEMORY+REASONING substrate paired with an
  LLM decoder (Bridge A/D) for generation -- NOT as a standalone generative LM. The EX-CONCEPT-1 "HP" should be
  downgraded to "substrate learns from real Pythia concepts (sanity check), but is bigram-level at generative LM."

## Infra: installed scikit-learn 1.9.0 on the runner venv (VQ cells were falling back to intractable numpy k-means).
## CCC-1-v2 status: 5/7 (3 architectural + counterfactual + analogical). Remaining: HotpotQA/NQ multi-hop-factual (the substrate-QA pipeline; building next).
**END.**
