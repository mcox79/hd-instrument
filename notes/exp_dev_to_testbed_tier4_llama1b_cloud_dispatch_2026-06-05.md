# Exp-Dev -> Testbed: dispatch Tier-4-Llama substrate-attention swap on cloud H100 (USER AUTHORIZED)

**From:** Exp-Dev  **To:** Testbed (cloud GPU lane)  **Inform:** Research + Orchestrator + User  **Date:** 2026-06-05 ~13:00
**Re:** Phase-2 CRITICAL test. User authorized cloud H100 ($1-3) for Tier-4-Llama 2026-06-05 (chose "Cloud H100" over local bf16). Cloud GPU is your lane.

## What + why
Replicate the validated Pythia Tier-4 result (substrate-Hebbian linear/Hopfield attention substituted for one attention
layer; Pythia HARD_PASS: ppl_ratio 1.06, entropy_ratio 3.08, grad_ratio 0.7) at Llama-3.2-1B. This is THE critical
Phase-2 architecture-scaling test: does substrate-as-attention hold at 1B params? OOM on local 4060Ti 8GB -> cloud.

## Anchor
`substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1`

## Reference scaffold (the validated Pythia version)
experiments/exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1.py
- substrate_attention_forward: phi=elu+1, causal normalized linear attention; shape contract (B,T,nh,hd)
- swaps ONE mid attention layer (Pythia used SWAP_LAYER=6 of 12)

## Llama-3.2-1B adaptation needed (model-specific -- your lane owns model internals + cloud):
- MODEL_ID = meta-llama/Llama-3.2-1B (base; file-first HF token already validated for it per your delivery note)
- Swap target: model.model.layers[L].self_attn (LlamaAttention) -- L = mid layer (1B has 16 layers -> SWAP_LAYER=8)
- LlamaAttention differs from Pythia GPTNeoX: RoPE position_embeddings passed in; GQA (num_key_value_heads < num_heads
  -> repeat_kv before substrate linear-attn); keep Llama's q/k/v/o_proj + RoPE, replace ONLY the softmax-attention core
  with the substrate causal-linear-attention (phi(q) @ cumsum(phi(k) outer v), normalized).
- dtype=float32 (H100 has memory; fp32 for the Tier-4 stability that the Pythia version needed) + grad-clip 1.0.
- attn_implementation="eager" (needed for the swap + output_attentions/entropy).

## Pre-reg bands (same as Pythia Tier-4)
HARD-PASS: ppl_ratio (substrate-swapped / baseline) <= 1.5x AND entropy_ratio in band AND grad-norm finite/bounded.
MIDDLE: ppl_ratio 1.5-3x. HARD-FAIL: ppl_ratio > 3x OR NaN/divergence.

## Dispatch
Lambda H100 (your SkyPilot path; auto-failover validated). ~$1-3, ~15-30 min wall. Batch with any other authorized
cloud model-load cell if pending (none from me right now). Please build the Llama-specific swap (you own model
internals + cloud), smoke on cloud, run, scp metrics back. I'll capture the verdict + report to Research.

## Note: residual-only Phase-2 cells (audit-core-1B HP, EX-CONCEPT-1B MIDDLE, K2-XOR-1B mechanism-confirmed) are
running fine on the local CPU runner -- no cloud needed for those. Only the model-load cells (Tier-4, generation) need cloud.
**END.**
