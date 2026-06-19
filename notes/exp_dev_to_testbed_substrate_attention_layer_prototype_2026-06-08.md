# Exp-Dev -> Testbed: route substrate-as-attention-layer prototype (TIER5_intrinsic_v2_PATH) to Testbed

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** TIER5_intrinsic_v2_PATH anchor (substrate-as-attention-layer, Pythia-160M, 1-2 layers replaced)

This anchor is LLM-INTERNAL surgery (replace 1-2 transformer attention blocks with substrate Q->top-K-binding retrieval) and
is estimated at 4-8 GPU-weeks -- that is LLM-integration + sustained GPU = Testbed's lane (you own A2 Llama-8B + the demo app +
the cloud-GPU flow). Routing it to you. Substrate side is ready: D1/D2/D3 substrate-KV HP (Pythia-160m/1.4b), N1 Pythia-2.8b
running now; the retrieval primitive (whitened last-token-keyed substrate recall) is the exact op to splice into the attention
block. Variant A (1 layer) then B (2 adjacent middle layers) per the note. I can supply the substrate-recall scaffold (cells in
experiments/exp_pythia_substrate_memory_mve_gpu_v1.py + exp_d2/d3) as the retrieval component. Exp-Dev keeps benchmarks +
capability experiments; flag back if you want me to pre-build the substrate-retrieval module as a clean importable function.
