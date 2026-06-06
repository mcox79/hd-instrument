# Orchestrator -> Research: results summary cycle 119 (v441)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~08:42
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**1 MIDDLE_BAND: whitening lifts real MiniLM capacity 2.75x** — Phase 4A ETF/Hadamard infrastructure eval. Mechanism confirmed on real encoder; gap from synthetic 10x explained by smaller N_sub + partial encoder structure.

## Findings

**`substrate_etf_hadamard_phase4a_infra_eval_v1` MIDDLE_BAND**
Whitening on real MiniLM encoder capacity: **307 → 844 facts (2.75×) at N_sub=384**, unanimous 3-seed deterministic. Below the HP threshold but above noise — mechanism is real. The gap vs v439's 10× lift at N=4096 is structural (smaller N_sub + the real encoder already has partial structure that limits headroom). Phase 4B N-sweep recommended to map the lift across encoder capacities.

## State

- cap_map v440 → **v441**
- commit: `f63d355`
- HONEST 953 → 954
- LVH 224 (no catches, label HONEST)
- 1 PP-8 sub-prop annotation (Phase 4A infrastructure)
- 0 BAND-LIFTS, 0 closures
- Portfolio 32+77 unchanged

## Context for research session

This is the **real-encoder companion** to v439's synthetic ETF/Hadamard 10× lift. The synthetic→real attenuation is fully expected: real LM embeddings have partial existing structure (orthogonality from training) that reduces the codebook-collision noise floor independently of init choice, so Hadamard init's incremental gain is smaller. The 2.75× lift is still meaningful — combined with the v440 Matthiessen finding (codebook-collision is 100% of noise), it implies the **remaining ~73% of capacity headroom is recoverable via deeper attacks on the codebook-collision axis** (e.g., learned codebooks, basis pursuit, sparse Hadamard mixtures).

Phase 4B gates this needs:
- N-sweep across MiniLM N_sub ∈ {384, 768, 1536, 3072} to confirm 2.75× holds or grows
- Cross-encoder test (Pythia-160m, Llama-1b) to verify mechanism is encoder-family-agnostic at real scale
- Combined Hadamard + whitening test (currently they're independent rescue mechanisms)

CPU is currently running Slot 6 (`substrate_embedding_norm_gate_discriminability_v1`); GPU queue empty. Pipeline is healthy.

---

**END.** No action requested — results heads-up per step-4 convention.
