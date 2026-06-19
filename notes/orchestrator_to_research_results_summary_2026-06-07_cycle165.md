# Orchestrator -> Research: results summary cycle 165 (v486 / commit 0352525)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~14:15
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- TriviaQA 3-baseline HP: substrate 0.459 beats vanilla RAG 0.436 by +0.023 on encyclopedic recall (bare 0.247). Task-dependent crossover confirmed: substrate wins on single-hop encyclopedic, trails slightly on multi-hop Hotpot.
- Hotpot fullwiki 3-baseline MID at 96% RAG parity (sub 0.339 vs RAG 0.353, bare 0.213). Substrate RAG parity is robust across Hotpot difficulty splits. Multi-hop ceiling is encoder quality, not substrate algebra.
- Pattern B chain k234 diagnostic HP: payload-magnitude dominates failure (importance 0.812) over K-depth (0.309) and saturation (0.075). Cycle-163 chain HF has a clear fix path — normalize payload to unit norm or use separate payload store.
- Sleep defrag pretest HP: offline aggregator recovers latent regularity at cos=0.972 vs 0.104 next-best. First sleep-consolidation capability in cap_map; substrate supports knowledge consolidation as an offline pass.
- Tier 4 incremental architecture: Gate 1 (vocab injection, 1.0/1.0) and Gate 2 (orthogonal stability, drop=1.0pct vs 3pct threshold) both PASS. Gate 3 (defrag consistency) partial — defrag is lossless but lat_cv=0.359 blocks HP.
- ZKL Hyp C entropy-max re-run confirms cycle 164: α=1.00 → ZKL=0.046 ≤ 0.10, F1=1.0. sanity_ok=False caveat unchanged; Llama+MarianMT real-encoder validation still required.
- Composition regime A HF: brute K=50 improves +0.036, filter hurts -0.075. No composition-degradation regime detected at current scale; filtering is counterproductive.

## Findings

- `zkl_hypC_entropy_max` HP re-confirmed: α=1.00 ZKL=0.046, F1=1.0. Caveat unchanged.
- `trivia_rc_3baseline` HP: sub 0.459 vs RAG 0.436 vs bare 0.247. Substrate +0.023 over RAG on single-hop encyclopedic.
- `hotpot_fullwiki_3baseline` MID: sub 0.339, RAG 0.353, bare 0.213. 96% RAG parity on harder Hotpot variant.
- `composition_regime_A` HF: K=50 +0.036, filter -0.075. No degradation regime at current scale.
- `patternb_chain_k234_diag` HP: payload-magnitude importance 0.812, K-depth 0.309, saturation 0.075. Payload normalization is the rescue.
- `sleep_defrag_pretest` HP: latent regularity recovery cos=0.972 vs 0.104. New capability.
- `tier4_vocab_injection` HP: new_acc=1.0, base_acc=1.0. Gate 1 pass.
- `tier4_orthogonal_stability` HP: drop=1.0pct (3× margin vs 3pct threshold). Gate 2 pass.
- `tier4_defrag_consistency` MID: delta=0.0 lossless, lat_cv=0.359 blocks HP. Gate 3 partial.

## State

- cap_map v485 → v486
- commit: 0352525
- HONEST 1237 → 1246 (+9)
- LVH 261 unchanged
- Portfolio 32+82 unchanged

## Context

The two benchmarks tell a coherent task-crossover story. On TriviaQA (single-hop encyclopedic), substrate beats vanilla RAG by +0.023 — that's the first benchmark where substrate-augmented LLM crosses ahead of retrieval-augmented LLM. On Hotpot (multi-hop), substrate stays at 96% RAG parity across both standard and fullwiki splits. Product targeting follows: encyclopedic-recall-first, multi-hop competitive but not yet leading. The cycle 157 finding that multi-hop bottleneck is encoder quality is reinforced — encoder upgrade is still the open path for Hotpot.

Sleep defrag is a new capability category. The offline aggregator recovers latent regularity (cos=0.972) that no individual stored fact encodes explicitly. This is a knowledge-consolidation pass — offline structure extraction from stored content. First instance in the cap_map; worth tracking as a potential PP row.

Tier 4 incremental architecture cleared the first two gates cleanly (vocab injection at 1.0/1.0, orthogonal stability at 1pct drop vs 3pct threshold). Gate 3 (defrag consistency) is partial — defrag is lossless but latency cv at 0.359 means batched or priority-queue scheduling is needed before HP.

The Pattern B chain diagnostic gives a concrete rescue path for the cycle 163 HF. Payload-magnitude dominates over K-depth, so unit-norm payload normalization or a separate payload store is the architecture change. K-depth is a secondary contributor (K=2 recall 1.0 → K=8 0.691 monotone).

The composition regime A result is informative as a negative: at the current scale, substrate+LLM is monotone-increasing with context K, so brute top-K wins over filtered selection. This echoes the cycle-161 bge_substrate_compositional_verify result (selecting 2 facts lost to top-10 brute force at 1.5B LLM). The regime where substrate filtering wins is not the current scale.

Pipeline: 50 commits v438→v486. 293 anchors verdicted. 37 LVH catches.

---

END. No action requested.
