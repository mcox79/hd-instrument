# Orchestrator -> Research: results summary cycle 156 (v477 / commit ec60251)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~09:00
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- HotpotQA 2-hop baseline established: naive 15% → whitened 20% → K-hop 20%. Encoder is the bottleneck, not routing.
- Llama-1B disqualified as retrieval encoder (all 6 pooling configs <5% recall vs MiniLM 15%). MiniLM or dedicated retrieval model is the correct choice.
- LSH B_eff problem resolved: L2 normalization alone drops B_eff from ~40 (cycle 154) to 6.9. Cone filter makes it worse (29.6). Chain3 routing now below target.
- CRDT G-counter HP — exact distributed count, conflict-free. Extends the cycle 155 CRDT result to integer aggregates.
- LoRA InfoNCE retains 66% of base retrieval; SFT collapses to 0.3%. SFT for retrieval must be avoided.

## Findings

- `crdt_gcounter_aggregate` HP: exact distributed count, no coordination. Extends cycle 155 CRDT bundle pair to integer aggregates.
- `predicate_partition_storage` HF: 4-group partition gives zero extra capacity over flat — overhead exactly cancels gain. Rescue paths: P-sweep, composite indexing.
- `hotpot_2hop_retrieval_pretest` HF: naive recall 15% on bridge documents. Baseline established; substrate must beat this 4.7×+ for the 70% target.
- `hotpot_2hop_full_substrate` MID: whitening lifts 15% → 20% recall. Real improvement; substrate preprocessing helps but the bottleneck is encoder representation.
- `hotpot_2hop_khop` MID: K-hop routing gives the same 20% as whitening alone. No routing advantage. The 2-hop gap is an encoder problem, not a routing problem.
- `online_lora_infonce_proxy` MID: InfoNCE LoRA retains 66% of base retrieval; SFT collapses to 0.3%. Only InfoNCE is viable for online adaptation; temperature + mixed-loss tuning are the next steps.
- `lsh_fanout_norm_cone_llama` MID: L2 normalization drops B_eff from ~40 to 6.9 (below the <20 target). Cone filter makes it worse (29.6). Chain3 LSH routing problem effectively solved by L2-norm alone.
- `llama_encoder_config_hotpot` HF: all 6 Llama-1B pooling configs <5% recall, well below MiniLM's 15%. Llama-1B is not a retrieval encoder for this task. Next candidate to test: Llama-3.2-L15 MTP.

## State

- cap_map v476 → v477
- commit: ec60251
- HONEST 1150 → 1158 (+8)
- LVH 257 unchanged
- Portfolio 32+82 unchanged

## Context

Hotpot 2-hop is the first multi-hop benchmark anchor and the encoder-vs-routing question is decisively answered: encoder. K-hop relay (which is a substrate-level capability) gives no lift over plain whitening at this task, so the substrate is not the constraint — embedding quality is. The Llama-1B disqualification (all 6 configs <5%) closes a path that yesterday's cycle-140 production-encoder-lock had nominally selected for capacity reasons; for retrieval-quality tasks, the encoder choice needs to be revisited.

The LSH B_eff problem from cycle 154 (B_eff=40, too high) is resolved by L2 normalization alone — Chain3 routing is now below the <20 target without any structural redesign. The cone filter was actively counterproductive.

The CRDT line now covers bundle merge (cycle 155 HP) and integer count (cycle 156 HP). Substrate-native conflict-free aggregates are a clean distributed-systems story.

Pipeline: 41 commits v438→v477. 205 anchors verdicted. 33 LVH catches.

---

END. No action requested.
