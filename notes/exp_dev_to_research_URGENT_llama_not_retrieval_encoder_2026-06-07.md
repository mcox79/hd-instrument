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

---
## UPDATE: tested bge-small (real small retriever, ~33M) -- encoder DOMINATES
hotpot_substrate_bge_v1 smoke (n=50, same data/matching):
- **bge-small-en-v1.5 naive recall@2hop = 0.42** -- vs MiniLM 0.16, vs Llama-1B-base 0.00.
- whiten + bridge-hop on bge = 0.38 (lift -0.04): substrate machinery HELPS weak encoders (MiniLM 0.16->0.26) but does
  NOT help an already-contrastively-trained strong one (bge). bge is already well-conditioned.

### Net picture (encoder ladder on HotpotQA 2-hop, all same harness)
  Llama-1B base (any layer/pool)  ~0.00-0.04   [NOT a retrieval encoder]
  MiniLM-L6 (33M, contrastive)     0.16 -> 0.26 with whiten  [substrate adds +63%]
  bge-small-en-v1.5 (33M)          0.42 naive                [best; substrate adds nothing on top]

### Recommendation (firmer)
Adopt **bge-small-en-v1.5** as the fair small retrieval encoder for the v1 benchmark suite (33M is clearly "relative size"
vs a 1B LLM, and it is 2.6x better than MiniLM, infinitely better than Llama-base). Path to the 0.70 target from bge's
0.42: real iterated-pinv K-hop (not the crude q+hop1 bridge, which hurts here) and/or a cross-encoder rerank on bge top-k.
The substrate's distinctive value (whitening lift, pinv capacity, K-hop, audit) is orthogonal to encoder ranking quality --
demonstrate it on the encoder where it helps (weak/raw keys) and use bge where raw ranking is what matters.

---
## UPDATE 2: the gap to 0.70 is RANKING, not retrieval -- clean path found
hotpot_bge_recall_at_k_v1 smoke (n=50): both supporting facts present in bge-small top-k:
  top-2 = 0.42   top-5 = 0.56   top-10 = **0.74**   top-20 = 0.90
=> The two supporting facts ARE in bge's candidate pool (recall@10=0.74 >= the 0.70 target). The HotpotQA multi-hop
problem at 1B-relative size is a RE-RANKING problem, not a retrieval-coverage problem. Actionable v1 recipe:
**bge-small top-10 retrieval -> cross-encoder rerank (or substrate K-hop / question-decomposition) -> recall@2hop ~0.70.**
This is a concrete, fair-size (33M encoder), demonstrable north-star path. Next cell I'll build: a reranker on bge top-10
to confirm the lift 0.42 -> ~0.74. The substrate's audit/K-hop/storage layers sit on top of this retrieval stack.
