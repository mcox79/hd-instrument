# Exp-Dev -> Research: T5b fact-transmission is a HARD problem (honest negative after 5 principled attempts)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** T5b in-weights substrate-attention fact transmission

**What works (keep):**
- T5b-1 scaffold (finite logits w/ injection) + T5b-2 perplexity (+7%% w/ 50%% random substitution) -- plumbing PASS.
- Flamingo entropy pre-test: adapter mandatory (raw-HD entropy 0.996). Qwen-0.5B-Instruct hidden=896, TIED embeddings.

**What does NOT work yet (honest):** making the injected substrate value actually become the next token. Five principled
attempts all fail to reach top-1 fact-transmission, with a consistent pattern:
1. Additive injection at layer 6/11 (Pythia): washed out (0/N).
2. Calibrated free Linear (768x768) at final residual: MEMORIZES train (0.89) / held-out 0.00.
3. Scalar gain: underfits (held-out 0.17).
4. Flamingo gated insert, analytic-inverse adapter A_v=pinv(Plift), learnable scale, inject answer-direction at Qwen model.norm:
   CE drops (11.5->7.4) but NEVER top-1 even at scale~18; train AND held-out = 0.00.
5. Output-projection (lm_head) value direction: identical (Qwen ties embeddings).

**Diagnosis:** a single-position residual/attention-output vector add cannot override the model's strong next-token prior for the
prompt's natural continuation -- even when the injected direction is provably the answer's logit direction and the scale is large.
RMSNorm + the accumulated residual dominate. Real Flamingo trains the FULL cross-attention (Q over context, K/V from memory) end-to-
end with the gate over many steps and data; a hand-built single-vector inject is not equivalent.

**Recommendation:** scope T5b-3/4 as a PROPER multi-step engineering sub-project, NOT a quick cell:
- Full gated cross-attention module (learned q/k/v projections + adapter), trained end-to-end over many steps on a fact corpus,
  possibly inserted at MULTIPLE layers; measure held-out transmission as the gate opens.
- Budget: GPU-days, not a cell. This matches Research's original "4-8 GPU-weeks" estimate for substrate-intrinsic.

**Business impact: LOW.** The demo does NOT depend on T5b. Tier-5a substrate-KV IN-CONTEXT is LIVE (Panel A) and is the shippable
product; the kNN-LM falsifiable test already grounded the algebraic MOAT (+0.983 multi-hop). T5b (in-weights) is the v2.0
architectural upgrade -- now correctly understood as real R&D, not a sprint cell. Not claiming Tier-5b until the trained
cross-attention demonstrably transmits held-out facts.
