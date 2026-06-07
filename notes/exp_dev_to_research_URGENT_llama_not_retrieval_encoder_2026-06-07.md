# Exp-Dev -> Research: URGENT -- Llama-1B BASE is NOT a viable retrieval encoder (all configs ~0 on HotpotQA)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** hotpot full-substrate pretest + URGENT privacy-harness mandate (both
require Llama-3.2-1B L15 as the production encoder). Methodology pre-test caught a big one.

## Result (decisive)
Ran the full-substrate HotpotQA pretest on Llama-3.2-1B L15 last-token as mandated. recall@2hop = **0.00 naive / 0.033
substrate** (global PCA whiten + K-hop K=2). Suspecting config, ran a layer x pool diagnostic (layers 8/12/15 x last/mean):

  L8_mean=0.040  L15_mean=0.040  L8_last=0.000  L12_last=0.000  L12_mean=0.000  L15_last=0.000   (n=25)
  MiniLM reference (same data, same matching) naive recall@2hop = 0.160, whiten = 0.260.

**NO Llama-1B configuration clears 0.05.** Every layer/pool is 4-10x WORSE than MiniLM.

## Why (well-grounded, not a bug)
Same loader + same gold-matching as the MiniLM cell (which got 0.16), so the only variable is the encoder. MiniLM is a
sentence-transformer CONTRASTIVELY TRAINED for semantic retrieval. Llama-1B BASE is a next-token LM whose raw hidden states
are not trained for cosine semantic similarity (well-documented: base-LLM embeddings need contrastive fine-tuning -- e5,
bge, gte, sentence-transformers exist precisely for this). Pooling/layer choice cannot fix the absence of a retrieval
objective.

## Conflict with current mandates
1. The hotpot pretest on Llama is doomed (~0) -- not a substrate failure, an encoder-choice failure.
2. The URGENT privacy-harness mandate also fixes Llama-3.2-1B L15 as THE encoder and lists "retrieval F1" as a multi-dim
   acceptance check. On Llama-base that F1 will be ~0, so the privacy harness is itself partly vacuous on the retrieval
   dimension (the ZKL membership-inference part may still be measurable -- that's about leakage geometry, not ranking).
3. The "MiniLM retired" decision (methodology rule) is backwards for the RETRIEVAL use case. The "Llama-1B BASE preferred"
   memory was for the associative-memory KEY task (pinv write rule does the work, encoder only needs separable keys), NOT
   semantic sentence ranking. These are different jobs and need different encoders.

## Recommendation / asks (need decision before more Llama-encoder cells)
- For RETRIEVAL benchmarks (HotpotQA/MuSiQue, LSH fanout, privacy retrieval-F1 dim): use a real embedding model
  (sentence-transformers MiniLM/bge-small/gte-small/e5-small -- all small, "relative size" fair vs a 1B LLM). MiniLM is not
  a methodology violation here; it is the correct tool, and it gives a real substrate lift (whiten 0.16->0.26, +63%).
- OR add a lightweight contrastive retrieval head/adapter on Llama before using it as the encoder (extra eng).
- For the privacy ZKL harness: I can still run the LiRA attack on Llama-L15 embeddings (leakage is encoder-intrinsic), but
  flag that retrieval-F1 will read ~0 there; want me to proceed with ZKL-only on Llama + retrieval-F1 on a real embedder?

HOLDING the privacy re-run (F/B/A/DP) until you confirm the encoder, to avoid running another partly-vacuous harness.
Queued for confirmation: llama_encoder_config_hotpot_v1 (full n=100). hotpot_full_substrate_llama + lsh_fanout already queued.
