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

---
## UPDATE 3: single-hop rerank HURTS (0.42->0.34) -- the gap is genuine multi-hop, not ranking
hotpot_bge_rerank_v1 smoke (n=50): bge top-10 -> cross-encoder/ms-marco-MiniLM rerank -> recall@2hop:
  bge-only = 0.42   reranked = 0.34   (lift -0.08)
A standard single-hop passage reranker makes it WORSE: it ranks the directly-question-relevant fact high but pushes the
BRIDGING fact (relevant to the answer chain, NOT directly to the question) down. This is the defining signature of true
2-hop: supporting fact #2 is reachable only via an entity bridge from fact #1, not by question-similarity.

### Corrected north-star conclusion (clean + actionable)
  - Encoder choice dominates: bge-small 0.42 >> MiniLM 0.16 >> Llama-base 0.00 (Llama-base is not a retriever).
  - Coverage is fine: bge recall@10 = 0.74 (both facts in the pool).
  - Ranking alone CANNOT close it: single-hop rerank hurts. The residual gap is GENUINE MULTI-HOP REASONING.
  - => This is exactly where the substrate's iterative K-hop relay (and the LLM's decomposition) earns its keep:
    retrieve hop-1, extract the bridge entity, re-query for hop-2. The crude "q+hop1" vector bridge also hurt; a proper
    entity-bridge decomposition is the next cell. This is a concrete, fair-size, demonstrable substrate value-add story.
Next genuine cell: entity-bridge K-hop decomposition on bge top-10 (does hop1->bridge->hop2 lift recall@2hop toward 0.74).

---
## UPDATE 4 (FINAL): embedding-based multi-hop plateaus at ~0.42 -> decomposition/LLM-loop is REQUIRED
Third multi-hop method tested. All three plateau at/below naive bge (0.42):
  - vector bridge (q+hop1):        0.38  (-0.04)
  - cross-encoder rerank:          0.34  (-0.08)
  - text-level iterative (re-enc): 0.40  (-0.02)
Recall@10 ceiling is 0.74 (facts ARE present), but NO similarity/ranking method reaches it. The bridging fact is reachable
only by understanding the question's compositional structure (extract bridge entity from hop1, query for the entity).

### Strategic conclusion for the north-star ("functional system beats LLMs at relative size")
HotpotQA 2-hop at fair size is NOT solvable by retrieval/reranking alone (embedding ceiling ~0.42). It REQUIRES explicit
multi-hop decomposition -- an LLM-in-the-loop that decomposes the question + an audited substrate retrieval/K-hop layer
underneath. This is precisely the system-level value story: the assembled system (small LLM decomposer + bge retrieval +
substrate K-hop/audit/storage) does multi-hop that neither bare retrieval nor a bare small LLM does well alone.

### Recommended next builds (need encoder/scope confirmation)
1. Entity-bridge K-hop: extract NPs/entities from hop1, query bge for the bridge entity, recall@2hop. (spaCy NER, CPU.)
2. LLM-decomposition loop: small LLM splits the 2-hop question into 2 single-hop queries; bge retrieves each. The real recipe.
3. THEN measure F1 of a small LLM answering with substrate-retrieved vs bare -- the actual head-to-head north-star metric.
