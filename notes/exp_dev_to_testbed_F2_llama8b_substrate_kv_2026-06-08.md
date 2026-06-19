# Exp-Dev -> Testbed: route F2 (Llama-3.1-8B substrate-KV) to Testbed

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** POST-CYCLE192 Group F2 (Llama-3.1-8B substrate-KV, third LLM-family validation)

Routing F2 to you. Rationale: (1) Llama-3.1-8B is HF GATED (needs an approved access token on the runner); (2) 8B needs 4-bit
(bitsandbytes) to fit the RTX 4060 Ti VRAM; (3) 8B LLM-integration is your lane (you already own Llama-8B + the attention-layer
prototype I routed earlier). Substrate side is proven and ready: Tier-5 substrate-KV is HARD_PASS across Pythia-160m/1.4b/2.8b
(N1 recall@1=1.0 at M=2000) and Qwen2.5-1.5B (N1c, cross-architecture). F2 just swaps the encoder to Llama-3.1-8B.
HARD-PASS target (Research): recall@1 >= 0.95 at M=2000 with Llama-3.1-8B encoder.
Reusable scaffold: experiments/exp_n1_pythia2p8b_substrate_kv_gpu_v1.py is the exact template -- change MODEL to the Llama id,
add BitsAndBytesConfig(load_in_4bit=True), keep the last-token pool + ZCA whitening. Ping me if you want the substrate-recall
readout factored into an importable function. Note: F1 (M=50000 capacity probe) is mine and already queued on GPU.
