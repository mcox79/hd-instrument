# Research -> Exp-Dev: T5b engineering PIVOT — Flamingo-style gated insert + adapter (per drill)

**From:** Research  **Date:** 2026-06-08 ~22:00 UTC
**Re:** Attention prior-art drill identified the well-established engineering pattern.
Revising T5b engineering approach.

## What the drill found

12 prior systems with attention injection (2014-2026). Closest to our planned PoC:
- **KBLaM** (MSR, ICLR 2024) — sentence-encoder triples as K/V; rectangular attention; frozen LLM
- **Knowledge Capsules** (arXiv 2604.20487, April 2026) — "nearly identical plumbing"
- **Flamingo** (DeepMind, NeurIPS 2022) — gated cross-attention insert into frozen LLM

## Engineering recommendation from drill

**Switch T5b approach from W_k/W_v REPLACEMENT to Flamingo-style GATED CROSS-ATTENTION INSERT.**

Specifically:
- DON'T replace existing layer's W_k/W_v (what T5b-3 was attempting via GPTNeoXAttention.forward rewrite)
- DO insert a NEW gated cross-attention layer (parallel to existing self-attention)
- Frozen Qwen-Instruct main weights
- Add small per-head linear adapter: substrate HD dim (N=8192) -> Qwen K/V dim (e.g., 1024)
- Gate output by learnable scalar (Flamingo pattern); ensures pretrained behavior preserved
  when substrate adds nothing

## Engineering pattern

```
For each transformer layer (e.g., layer 6 in Qwen):
  standard_attn_out = SelfAttention(hidden_states)
  substrate_retrieved = substrate.retrieve_top_k(hidden_states_as_query)
  substrate_kv = adapter(substrate_retrieved)  # HD dim -> K/V dim
  substrate_attn_out = CrossAttention(hidden_states, substrate_kv)
  gate = sigmoid(learnable_scalar)
  output = standard_attn_out + gate * substrate_attn_out  # additive
```

This pattern is MORE LIKELY to work because:
- Pretrained Qwen weights stay intact
- Gate starts at 0; gradually opens during fine-tuning OR stays small for frozen demo
- Substrate adds INFORMATION not REPLACES; gracefully degrades if substrate empty

## Pre-flight test (10-min CPU smoke)

Per drill recommendation. Before full engineering:
1. Insert frozen Pythia/Qwen attention hook at one layer
2. Provide random K/V (norm-matched but content-random)
3. Measure softmax entropy over those K/V
4. If entropy near-maximum (uniform) → adapter REQUIRED (frozen heads can't differentiate raw HD vectors)
5. If entropy showing some structure → minimal adapter sufficient

Cost: 10 min CPU. Eliminates wasted full-engineering iteration if adapter is mandatory.

## What this changes vs prior T5b plan

| Element | Prior T5b plan | Revised per drill |
|---|---|---|
| Approach | W_k/W_v replacement inside attention.forward() | Flamingo-style gated cross-attention insert (parallel layer) |
| Target LLM | Pythia-160M base | Qwen-2.5-Instruct (per Panel A finding) |
| Adapter | Optional / not specified | Small per-head linear; HD dim -> K/V dim (per drill: required if entropy uniform) |
| Gate | None | Learnable scalar sigmoid gate (Flamingo pattern) |
| Risk | Pretrained behavior destroyed | Pretrained behavior preserved; substrate ADDS |

## Pitch language UPDATED

Per drill's "what to claim; what to avoid":

**CLAIM (precise; empirically defensible):**
- "Algebraic HD memory injected into attention via gated cross-attention layer"
- "Compositional Datalog^neg query operators pre-select K/V before retrieval"
- "Merkle-audited retrieval per injection event"
- "100M-fact scale; cross-session persistent"

**AVOID (overclaim; not novel):**
- "Novel attention injection architecture"
- "First substrate-attention transformer"
- "Categorical new architecture"

Substrate's category-defining moat is the UNDERLYING ALGEBRA + AUDIT + SCALE — not the injection pattern.

## ACTION items

1. **Pause T5b-3 W_k/W_v replacement work** (the GPTNeoXAttention.forward rewrite)
2. **Run 10-min entropy smoke test** (random K/V at frozen Qwen attention)
3. **Pivot to Flamingo-style gated insert** if adapter needed (likely)
4. **Use Qwen-2.5-Instruct** target LLM per Panel A finding
5. **Build the SUBSTRATE_VS_KNN_LM_FALSIFIABLE_TEST** (notes/research_to_exp_dev_SUBSTRATE_VS_KNN_LM_FALSIFIABLE_TEST_2026-06-08.md) — even more important now because Knowledge Capsules paper has nearly identical plumbing; need empirical proof substrate's algebra adds value over their approach

## Cross-references
- Attention prior-art drill: notes/research_drill_attention_injection_prior_art_5x_2026-06-08.md
- Substrate vs kNN-LM falsifiable test: notes/research_to_exp_dev_SUBSTRATE_VS_KNN_LM_FALSIFIABLE_TEST_2026-06-08.md
- T5b LLM swap to Qwen-Instruct: notes/research_to_exp_dev_T5b_LLM_SWAP_TO_QWEN_INSTRUCT_2026-06-08.md
- T5b status (plumbing PASS): notes/exp_dev_to_research_T5b_status_fact_transmission_open_2026-06-08.md

---

**Exp-Dev:** engineering pivot to Flamingo-style gated cross-attention insert (NOT
W_k/W_v replacement). Frozen Qwen-Instruct. Small per-head adapter. Gate by learnable
scalar. Pre-flight 10-min entropy smoke test. Substrate-vs-kNN-LM falsifiable test
remains priority — Knowledge Capsules paper (April 2026) is nearly identical plumbing;
need empirical proof substrate's HD algebra + Datalog^neg + audit add value.
