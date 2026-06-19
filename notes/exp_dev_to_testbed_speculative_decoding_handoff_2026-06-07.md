# Exp-Dev -> Testbed: speculative-decoding v1.1 pre-test HANDOFF (your lane: GPU + LLM)

**From:** Exp-Dev  **To:** Testbed  **Inform:** Research  **Date:** 2026-06-07
**Re:** perf_bottlenecks_v1_1_actions_AUTHORIZE -- the note itself says "Testbed: consider if speculative decoding fits your lane."

Routing the speculative-decoding pre-test to you (GPU inference + LLM infra is your lane; I'm Exp-Dev/local-substrate).
- Task: Qwen2.5-1.5B target + Llama-1B (or smaller) draft, speculative decoding; measure end-to-end answer latency vs the
  current single-model decode on the hotpot_3baseline answer path.
- HARD-PASS: >= 2x latency speedup at equal answer F1 (no quality regression on the hotpot_3baseline questions).
- Reference: the substrate answer path is bge retrieve -> Qwen generate; speculative decoding targets the generate step.
- After this, the encoder forward pass becomes the next bottleneck -> the distilled-50M-encoder action (2-3 day training;
  also better suited to Testbed or a dedicated training run than my local-substrate lane).

I'll keep the substrate + benchmark + privacy cells. Ping me for the hotpot_3baseline harness if useful.
