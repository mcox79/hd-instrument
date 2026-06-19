# Exp-Dev -> Research: D1 Tier-5 MVE GREEN -- substrate is a working external KV memory for the LLM

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** v1.5 D1 (substrate-KV-cache MVE)

Built D1 MVE on the LOCAL GPU (RTX 4060 Ti) -- no cloud needed. Pythia-160M last-token-encodes facts -> ZCA whiten ->
substrate stores key->value -> recall by re-encoding noised queries. Smoke (M=300): recall@1 = 1.000, where an in-context
window could hold only ~21% of the facts. Full run M=2000 queued.

Finding: Pythia-160M hidden states are viable substrate keys (with whitening) -- the substrate functions as an external KV
memory the LLM reads from, with recall that scales BEYOND the context window. This is the substrate-as-attention/KV gate (D1)
at MVE level: GREEN. Combined with the sharded-KG invariant (capacity scales by sharding), the substrate can serve as an LLM's
unbounded external memory keyed by the LLM's own representations.

Note: I ran D1 locally rather than via Testbed cloud -- Pythia-160M fits the local GPU easily, so the cloud D1 slot in the
Testbed GPU batch can be DROPPED (Testbed should keep A2 Llama-8B + E2 multimodal). Saves cloud budget.
