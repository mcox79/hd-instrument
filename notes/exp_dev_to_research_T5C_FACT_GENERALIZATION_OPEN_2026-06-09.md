# Exp-Dev -> Research: Tier-5c results -- architecture WORKS (ppl), but external-fact-USE does NOT generalize (held-out=0). Research needed.

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** Tier-5c Phase C/D + C1-FACT product claim

## Confirmed (HARD_PASS) -- the ARCHITECTURE works
- **Phase C (Pythia-160M, 2-layer Flamingo, memory=past tokens):** perplexity 0.835x (~20% improvement), gates engaged, stable.
- **Phase D (Qwen-2.5-1.5B, L12+13, bf16):** perplexity 0.851x (~15% improvement), gates engaged, stable. Cross-architecture confirmed.
- Recipe that works (bracketed empirically): gate-lr 1e-3, main-lr 3e-4 + wd 0.01, warmup 500 + cosine, grad-clip 1.0,
  LayerNorm-before-xattn, Adam betas 0.9/0.95, eval@500 + early-stop. (gate-lr 0.05 diverged; 1e-5 inert; 1e-3 is the sweet spot.)
So multi-layer substrate-attention measurably IMPROVES language modeling on two model families. The v2.0 architecture is sound.

## OPEN / negative -- the PRODUCT claim does NOT yet hold
**C1-FACT (trained Flamingo over an EXTERNAL fact-KB; held-out fact recall): HARD_FAIL.**
- train-recall 1.000 (learns the 9 train facts perfectly), HELD-OUT-recall 0.000 (zero generalization), gate 0.52 (engaged).
- The adapter MEMORIZES the train facts; it does NOT learn the general "retrieve-the-matching-slot-and-answer" behavior, so
  held-out facts (whose slots ARE in the KB) get nothing.

## The research question for you
Phase C/D prove substrate-attention helps LANGUAGE MODELING (perplexity via the memory). But "the LLM USES external substrate
FACTS it never trained on" -- the categorical product claim -- is NOT demonstrated (held-out=0, memorizes). Why, and what's the
right design? Hypotheses to investigate:
1. Too few train facts (9) -> trivial memorization. (I drafted a 240-fact rescue but am holding it for your guidance.)
2. The adapter learns prompt->answer directly, not query->retrieve-slot->answer (no pressure to use the KB generally).
3. Needs explicit retrieval supervision / contrastive key-matching loss (vs only next-token CE).
4. Memory/key structure: my slot = fact's last-token hidden; maybe key should be subject-encoding + value = answer-embedding
   separately (so retrieval is by-subject, output is the value).
Please survey the prior art (RETRO, kNN-LM, Atlas, Memorizing-Transformer, KBLaM, Knowledge Capsules) for how they achieve
GENERALIZABLE retrieval (not memorization), and recommend the experimental design (fact count, loss, key/value structure,
retrieval supervision). This is the gate between "substrate improves the LLM's LM" (proven) and "substrate is the LLM's
swappable knowledge store" (the real v2.0 product claim). Drafted rescue (240 facts) ready to run on your rec.

Note: full results in data/exp_t5c_{c1,d1,c1fact}*/metrics.json + progress.jsonl. Recipe in exp_t5c_c1_multilayer_flamingo_train_gpu_v1.py.
