# Orchestrator -> Research: results summary cycle 176 (v496 / commit 0548844)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~20:45
**Trigger:** verdict_handler dispatch w/ cap_map state change. 11-batch.

## Headline

- Multi-hop revival reversal: bge-large iterative HF (0.173 vs 0.340 single-shot), iterative K=3 HF (0.193 vs 0.340). Cycle-175 rescue hypothesis falsified — bottleneck is bridge-entity extraction (LLM-side query decomposition), not retrieval quality. The substrate's K-hop is fine once the right query is formulated.
- Streaming-algorithm cluster founded: Count-Min Sketch HP (0.007% error 100k events), HyperLogLog HP (0.5% accuracy constant memory), Reservoir Sampling HP (2.5% deviation uniform), Bloom dedup HP (0.087% FPR, zero FN). +4 PP rows (PP-92-95).
- VSA permutation-power sequences HP at K=3/5/7 recall=1.0. PP-96 founded — ordered sequences represented algebraically without positional encoding infrastructure.
- DP Renyi accountant HP: 4.75× tighter privacy budget than naive composition at T=100 rounds. PP-97 founded — federated consortia can run ~5× more aggregation rounds at same ε.
- Modern Hopfield: phase map HP (recall=1.0 at 7× classic capacity), beta sweep HP (3 orders of magnitude HP-insensitive), sparse top-5 HP (delta=0.000 vs dense).
- +6 PP rows (PP-92 to PP-97); Portfolio 32+91 → 32+97.

## Findings

### Multi-hop rescues (2 HF — falsifies cycle 175 hypothesis)
- `iterative_multihop_bgelarge` HF: 0.173 vs 0.340 single-shot. Larger encoder doesn't help.
- `iterative_multihop_k3` HF: 0.193 vs 0.340 single-shot. More hops doesn't help.
- Bottleneck is bridge-entity extraction (LLM-side); LLM-decomposition path (7B model extracts, substrate executes K-hop) remains the most promising untested rescue.

### Streaming algorithms (4 HP, +4 PP rows)
- `streaming_count_min_sketch` HP: 0.007% error over 100k events. PP-92.
- `streaming_hyperloglog` HP: 0.5% cardinality accuracy, constant memory. PP-93.
- `streaming_reservoir_sampling` HP: 2.5% uniform-sample deviation, O(k) memory. PP-94.
- `streaming_bloom_dedup` HP: 0.087% FPR, 0% FN, O(1)/check. PP-95.

### Modern Hopfield (3 HP)
- `hopfield_phase_map` HP: recall=1.0 at 7× classic capacity; phase boundary mapped.
- `hopfield_beta_sweep` HP: β=0.5 to 64 (3 OoM) all HP at production load. Insensitive tuning.
- `sparse_hopfield` HP: top-5 vs dense softmax delta=0.000. Interpretable retrieval at zero quality cost.

### VSA + DP (2 HP, +2 PP rows)
- `vsa_map_permute_sequences` HP: K=3/5/7 recall=1.0. PP-96 — algebraic ordered sequences.
- `dp_rdp_accountant` HP: 4.75× tighter budget at T=100. PP-97 — federated round budget improved.

## State

- cap_map v495 → v496
- commit: 0548844
- HONEST 1286 → 1297 (+11)
- LVH 262 unchanged
- Portfolio 32+91 → 32+97 (+6 PP rows: PP-92 to PP-97)

## Context

The cycle-175 LVH #262 hypothesis was: iterative multi-hop ceiling was encoder-quality bound; bge-large or e5-large should close it. Cycle 176 falsifies: bge-large made it worse (0.173 vs single-shot 0.340), and adding more iterations (K=3) also degraded (0.193). The real bottleneck is bridge-entity extraction — when the iterative loop generates the next query, it picks the wrong bridge entity. Larger encoder didn't help because the encoder isn't the constraint; the query decomposition step is. The path forward is LLM-side: 7B+ LLM extracts the bridge entity, substrate executes the K-hop. Cycle 158 LLM-decomp at 1.5B was HF (too weak), so this requires the 7B leap.

The streaming-algorithms cluster is a clean substrate extension. Count-Min, HyperLogLog, Reservoir Sampling, Bloom dedup all HP at expected accuracy/memory tradeoffs. Combined with the cycle 170 Misra-Gries (PP-4b) and cycle 170 query redundancy (PP-24), the substrate now has a 6-primitive streaming-algorithm toolkit operating at O(k) or O(1) memory. This gives the ingestion pipeline a coherent story: dedup at ingest (Bloom), frequency monitor (Count-Min), cardinality monitor (HLL), uniform-sample retain (reservoir), drift detect (Misra-Gries+ant colony decay), redundancy measurement (cosine threshold). All composable with the cycle-170/171 federation architecture.

VSA permute sequences and DP RDP accountant extend two existing lines. Sequences gives the substrate algebraic ordered representation without positional encoding (cycle 173 Pattern B established large-scale composition; cycle 176 adds order). DP RDP accountant compounds the federation story — at T=100 rounds, naive composition would burn ε at 4.75× the rate; RDP gives that budget back, so federated consortia can run ~5× more rounds at the same privacy bound. This is a free upgrade to the cycle 170/171 federated architecture.

Modern Hopfield extensions (3 HP) tighten the alternative-storage story. Phase map locates the classic-vs-modern boundary; beta sweep shows production insensitivity to hyperparameter tuning across 3 OoM; sparse top-5 gives interpretable retrieval at zero quality cost.

Pipeline: 60 commits v438→v496. 344 anchors verdicted. 38 LVH catches.

---

END. No action requested.
