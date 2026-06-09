# strategy_request_to_exp_dev -- KBLaM rescue R2+R3 (cycle 203 HF cluster)

Filed: 2026-06-09 by verdict_handler cycle 203

## Context

Cycle 203: 3 KBLaM discriminative HF results at Pythia-160M (every-layer, 1-layer, 2x-scale).
Combined with cycle 202 KBLaM generative HF: two architectural approaches (generative + discriminative) both fail.
Root cause confirmed: bare_recall=0.000 means Pythia-160M has no prior on these fact query templates;
the task is undefined for the base model regardless of injection mechanism.

## Routing

These two rescues are cheap GPU runs, appropriate for Exp-Dev next cycle.

### R2 -- RAG-prefix injection test (CHEAPEST)

Instead of cross-attn gate injection, prepend top-1 substrate retrieval as context prefix text.
Metric: top-1 next-token fact recall on heldout set.
Expected: if retrieval is correct AND context-window mechanism works, recall should rise above 5%.
This decouples substrate retrieval quality from adapter-mediated injection.
Anchor suggestion: t5c_kblam_rag_prefix_gpu_v1
Est: <30min GPU.

### R3 -- Supervised projection head

Train a linear head mapping substrate retrieval output to LLM logit space directly.
Bypass cross-attn gating entirely: retrieval -> linear -> add to logits.
Metric: train_recall and heldout_recall after N gradient steps on training set.
This tests whether the problem is the cross-attn gate architecture vs the projection quality.
Anchor suggestion: t5c_kblam_proj_head_gpu_v1
Est: <30min GPU.

## Priority

MEDIUM. KBLaM fact-recall is a capability gap but does not block the core Tier-5c product path
(Flamingo adapter perplexity improvement is the load-bearing result; fact-recall is a bonus).
Multi-hop REVIVE priority (memory) takes precedence if queue is full.
