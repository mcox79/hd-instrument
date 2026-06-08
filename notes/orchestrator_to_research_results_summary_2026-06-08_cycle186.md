# Orchestrator -> Research: results summary cycle 186 (v512 / commit de2cc638)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~11:00
**Trigger:** verdict_handler dispatch w/ cap_map state change. 13-batch.

## Headline

- 9 HP + 3 MID + 1 HF (closure), 0 LVH. +7 PP rows (PP-137..PP-143). Portfolio 32+136 → 32+143.
- Two cycle-183 MID rescues cleared to HP: skewed shard online split (PP-131 0.824→1.000); hierarchical KG sub-shard (PP-132 0.735→1.000 via within-relation subject sub-sharding). Sharding architecture story tightened.
- Mycorrhizal MID also cleared (cycle 165 0.56 → cycle 181 0.62 → cycle 186 0.75 with sim-weighted multi-hub) — but sim-weighted = uniform-union exactly; uniform is sufficient.
- Sleep-defrag family founded across 3 anchors (PP-141 cross-shard chain pre-compute O(1), PP-142 inverted property shards O(K), PP-143 shard merge primitive — elastic sharding now bidirectional split+merge).
- Resonator K=4 CLOSED — third consecutive HF (0.537 at N=16384 with multi-axis attack); hard angular-degeneracy limit. K≥8 territory remains valid.
- PubMedQA benchmark HP at 99.7% of raw encoder (PP-137); HotpotQA MID at 8pt deficit (PP-138, separate from extraction bottleneck).
- Legal citation 500-seed HP at closure=1.000 across 2000 cases — PP-120 statistical confidence production-grade.

## Findings

### Benchmarks
- `pubmedqa_substrate_retrieval_benchmark` HP: r@5=0.997 vs raw 1.000 (n=1000). Within noise; pipeline green for head-to-head. PP-137.
- `hotpotqa_multihop_retrieval_benchmark` MID: r@10=0.640 vs raw 0.720 (n=50). Functional but below parity. PP-138; whitening + larger N first rescues.
- `legal_citation_500seed` HP: closure=1.000 at 500 seeds / 2000 cases. 10× extension of PP-120; band-LIFT to VALIDATED warranted.

### MID rescues (3 cleared, 1 closure)
- `mycorrhizal_simweighted_rescue` HP: 0.750 multi-hub. Sim-weighted = uniform-union exactly; uniform is sufficient.
- `skewed_shard_online_split` HP: 0.824 → 1.000 via online elastic split. PP-131 MID cleared.
- `hierarchical_subshard_kg` HP: 0.735 → 1.000 via within-relation subject sub-sharding. PP-132 MID cleared.
- `resonator_k4_multiaxis_rescue` HF CLOSED: 0.537 at K=4 N=16384 with multi-axis attack. Third HF; hard angular-degeneracy limit at K=4. K≥8 still valid.

### Sleep-defrag family (3 HP, new PP rows)
- `cross_shard_chain_extraction` HP: post-defrag 2-hop=0.990 via A→B→C pre-compute as A→C. PP-141; multi-hop latency amortized to O(1).
- `inverted_property_shards` HP: sleep-defrag inverted index recall=1.000. PP-142; property-range O(K) not O(all_shards × K).
- `shard_merge_primitive` HP: 60→37 shards (-38%) at pre=post=1.000. PP-143; elastic sharding bidirectional (split+merge).

### Other (2 HP + 1 MID)
- `n1b_perhop_ablation` HP: single-pass joint=1.000; per-hop sequential=0.855. Single-pass is optimal; decomposition granularity not the constraint.
- `counterfactual_do_demo` MID: do()=0.865, factual divergence=1.000. PP-139; native Pearl do() queries; rescue to HP via explicit interventional role vectors.
- `preference_bindings` MID: personalized=0.870, cross-customer divergence=0.965. PP-140; per-customer differentiation real; HP rescue via per-customer shard.

## State

- cap_map v511 → v512
- commit: de2cc638
- HONEST 1384 → 1397 (+13)
- LVH 263 unchanged
- Portfolio 32+136 → 32+143 (+7 PP rows: PP-137..PP-143)

## Context

The cycle settles the sharding-architecture rescue story cleanly. Both cycle-183 MIDs (PP-131 skewed shard, PP-132 per-relation KG) cleared to HP via their predicted mechanisms: online elastic split for hotspot (the policy PP-129 already validated), and within-relation subject sub-sharding for dense relations. Combined with cycle-185's PP-134 subject-sharding strategy + PP-132 MID→HP upgrade, the production KG layout is now: shard by relation, sub-shard by subject. Cycle-186 PP-143 shard merge adds the back-side of elastic sharding — shard count can shrink as well as grow without retraining.

The sleep-defrag family is a new product capability category. PP-141 amortizes cross-shard chain extraction to O(1) at query time by pre-computing transitive closures during off-peak; PP-142 builds an algebraic inverted property index via the same mechanism; PP-143 merges shards when load decreases. Three HPs in one cycle establishes sleep-maintenance as a coherent latency-and-cost optimization layer beneath the production sharding architecture.

Resonator K=4 is closed by third-consecutive HF at 0.537 with multi-axis attack at N=16384. The angular-degeneracy limit is hard at K=4; K≥8 territory remains valid via the cycle-178 verdict. K=2 proof-of-concept also holds (cycle 177).

PubMedQA benchmark HP at 99.7% of raw encoder retrieval makes the biomedical story head-to-head. HotpotQA multi-hop benchmark MID at 8pt deficit (r@10 0.640 vs raw 0.720, n=50) is a separate axis from the LLM-extraction bottleneck (cycle 184); whitening + larger N are the first rescue paths.

Legal citation 500-seed HP at closure=1.000 / 2000 cases gives PP-120 production-grade statistical confidence (10× the cycle-181 sample). Band-LIFT to VALIDATED warranted.

The do() demo MID (0.865) and preference bindings MID (0.870) both have HP rescues queued (explicit interventional role vectors; per-customer shard).

Pipeline: 71 commits v438→v512. 444 anchors verdicted. 39 LVH catches.

---

END. No action requested.
