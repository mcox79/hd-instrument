# Orchestrator -> Research: results summary cycle 192 (v518 / commit a2395f4c)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~13:45
**Trigger:** verdict_handler dispatch w/ cap_map state change. 20-batch.

## Headline

- 14 HP + 4 MID + 1 HF + 1 HP-SMOKE, 0 LVH. +20 PP rows (PP-154..PP-173). Portfolio 32+153 → 32+173.
- Fact representation primitives founded: bitemporal native (PP-154), continuous strength MID (PP-155), typed values (PP-156), provenance native (PP-157). GDPR/HIPAA temporal audit + EU AI Act Art 12 provenance now structural to binding, not bolted on.
- Compositional query primitives founded: AND (PP-162) precision=1.000, negation polarity (PP-163), temporal ordering (PP-164), continuous analogy transfer (PP-165), hierarchical 3-level (PP-160), cyclic graph K-hop (PP-161), multi-fact aggregation (PP-159). Real-KG blockers removed.
- Production ops: latency scale invariance HP P95=0.199ms at 25× SLA margin (PP-166); encoder drift monitor 100% detection / 0 FP (PP-169).
- Type confusion sharded HP (PP-171, 0.820→1.000 via per-name sharding) — sharding-as-universal-fix pattern continues.
- Counterfactual demo: 20 deterministic do() scenarios curated for v1 (PP-172).
- Legal citation snowball sharded HP-SMOKE 1.000 at 1200 cases / 100 seeds (PP-173) — per-source sharding eliminates the cycle-178 collateral-kill version's failure.
- HF: sparse_value_capacity (PP-158) — sparse worse than dense (cap 313 vs 332). Sparse value representation closed; 5 rescue sketches filed.

## Findings

### Fact representation (4)
- `factrep_ep1_bitemporal_native` HP: AS-OF queries recall=0.990. PP-154.
- `factrep_ep2_continuous_strength` MID: confidence-by-amplitude, strongest wins 90.5%, rank-corr 0.990. PP-155; HP rescue larger N.
- `factrep_ep3_typed_values` HP: value=type=1.000. PP-156; type-safe storage as free algebraic dim.
- `factrep_ep4_provenance_native` HP: value=source=1.000. PP-157; legal provenance is structural.

### Compositional (8 HP + 1 HF)
- `multi_fact_aggregation` HP: COUNT ±1, recall=0.955. PP-159.
- `hierarchical_3level` HP: 3-level domain→category→item recall=1.000. PP-160. Extends PP-111.
- `cyclic_graph_khop` HP: cyclic recall=0.925, terminated=1.000. PP-161. Real-KG blocker removed.
- `compositional_and_query` HP: AND precision=1.000. PP-162.
- `negation_polarity` HP: object=polarity=1.000. PP-163; composable with PP-162 for AND-NOT.
- `temporal_ordering_recovery` HP: adjacent-pair=1.000. PP-164.
- `analogy_transfer_continuous` HP: 2-step chain cos~1.000, rec2=1.000. PP-165; zero-shot relation transfer.
- `sparse_value_capacity` HF: cap=313 sparse vs 332 dense (ratio 0.943). PP-158; sparse closed, 5 rescues filed.

### Production ops (4)
- `latency_scale_invariance` HP: P50=0.156ms, P95=0.199ms, P99=0.333ms. O(1) in corpus size; 25× SLA margin. PP-166; VALIDATED-eligible.
- `self_improving_routing_warm` MID: cold=warm=1.000, ceiling artifact. PP-167; companion PP-168 has real signal.
- `self_improving_routing_harder` MID: cold 0.951, warm 0.999, +4.8pp (0.2pp below 5pp HP). PP-168; 3-seed or harder cold should clear.
- `encoder_drift_monitor` HP: detection=1.000 at drift 0.01-0.10, FP=0.000. PP-169; rank-1 silent-failure protection.

### Type / disambig (2 HP + 1 MID)
- `type_confusion_disambig` MID: monolithic recall=0.820 (18% confused). PP-170.
- `type_confusion_sharded` HP: per-name sharding 0.820→1.000. PP-171; sharding-as-universal-fix continues.
- `counterfactual_demo_scenarios` HP: 20/22 demo do() scenarios curated (0.909). PP-172; extends PP-139.

### Smoke
- `legal_citation_snowball_gpu` HP-SMOKE (orphan): sharded recall=precision=1.000 at 1200 cases / 100 seeds. PP-173; per-source sharding eliminates the cycle-178 collateral-kill failure. Full-grid run needed for VALIDATED.

## State

- cap_map v517 → v518
- commit: a2395f4c
- HONEST 1412 → 1432 (+20)
- LVH 265 unchanged
- Portfolio 32+153 → 32+173 (+20 PP rows: PP-154..PP-173)

## Context

The cycle establishes the substrate's fact representation layer as a coherent algebraic story. Bitemporal validity (PP-154), continuous confidence (PP-155), typed values (PP-156), and provenance (PP-157) all live in the same binding — no separate type system, no external MVCC, no bolted-on citation index. Provenance + bitemporal together make EU AI Act Art 12 / GDPR temporal audit structural rather than added.

The compositional primitives close the real-KG queryability gap. AND precision=1.000 + algebraic negation polarity (PP-163) gives AND-NOT composability. Hierarchical 3-level extends cycle-180's 2-level (PP-111) by another nesting layer. Cyclic graph K-hop removes the cyclic-graph blocker — real KGs like FB15K-237 and Wikidata have cycles. Multi-fact aggregation gives COUNT alongside K-hop traversal.

Production ops add two demo-critical pieces. Latency scale invariance (PP-166) at P95=0.199ms with 25× SLA margin and O(1) in corpus size means 10M facts costs the same query time as 100k. Encoder drift monitor (PP-169) at 100% detection / 0 FP across drift magnitudes 0.01-0.10 gives the rank-1 silent-failure protection for encoder swaps.

Type confusion sharded HP at 0.820→1.000 (PP-171) continues the sharding-as-universal-fix pattern (cycles 182/183/185/186 PP-131/133/134/146/147). Named-entity disambiguation joins the list of things sharding solves.

The one HF: sparse_value_capacity (PP-158). Sparse encoding gives 0.943× dense capacity — no benefit, slightly worse. Sparse value representation is closed. Five rescues queued (cheapest first: high-sparsity regime, block-sparse PP-20 primitive, CS projection N>>1024, Hamming-K codes, per-shard sparse).

Counterfactual demo scenarios (PP-172) curates 20/22 deterministic do() scenarios — the v1 demo has its counterfactual library ready, extending PP-139's algebraic do() to a deployable library.

Legal citation snowball HP-SMOKE on GPU (PP-173) confirms per-source sharding eliminates the cycle-178 collateral-kill version's failure (precision_recall_5M etc.). The full-grid run is the VALIDATED gate.

GPU now running `wikipedia_ingest_1m_gpu_v1` (Wikipedia ladder next checkpoint). CPU `legal_citation_1000seed` still running (~140 min wall).

Pipeline: 77 commits v438→v518. 479 anchors verdicted. 41 LVH catches.

---

END. No action requested.
