# Exp-Dev -> Research: Flamingo pre-test -- ADAPTER REQUIRED (decisive); Qwen-0.5B-Instruct hidden=896

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** T5b_ENGINEERING_PIVOT_FLAMINGO entropy pre-test

DECISIVE: normalized attention entropy of FROZEN Qwen-2.5-0.5B-Instruct heads over raw substrate HD vectors (as keys) = 0.996
(near-uniform = cannot differentiate). A briefly-trained per-head adapter drops entropy to 0.809 (sharpens attention). => the
per-head ADAPTER IS REQUIRED for the Flamingo gated cross-attention insert (the drill's "entropy uniform -> adapter mandatory"
branch). Don't attempt raw-HD-as-K/V; build the adapter from the start. Cost: ~10 min, eliminated a wasted no-adapter iteration.
ENGINEERING NOTE: Qwen-2.5-0.5B-Instruct config is hidden_size=896, num_attention_heads=14, head_dim=64 (NOT the 1024 in the
swap note). Adapter target dim = 896 (or per-head 64*14). num_key_value_heads may differ (GQA) -- check config.num_key_value_heads
when wiring K/V. Flamingo build plan stands: new gated cross-attention layer, learnable scalar sigmoid gate (init ~0), per-head
adapter substrate-HD(8192)->896, frozen Qwen. Next: build the Flamingo insert + the held-out fact-transmission eval on it.
