# exp_dev hand-off -- research: multi-hop maximization 2x

Filed-by: research sub-agent (Sonnet)
Date: 2026-06-09
Trigger: research_drill_multihop_maximization_2x_2026-06-09 mandate -- depth ceiling + complexity extension for substrate K-hop moat
Research note path: d:/AI/hd-instrument/notes/research_drill_multihop_maximization_2x_2026-06-09.md

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the experiment cells; this file provides anchor candidates, context pointers, and tier hints only.

---

## Pause state block

Experiments are authorized to queue immediately. No pause gate active at time of filing.
GPU anchors (Rank 6) should be batched with other GPU cells per [[feedback-batch-cloud-experiments]].
CPU anchors (Ranks 1-5, 7-8) are local runner eligible.

---

## Anchor candidates (rank-ordered)

### Rank 1: khop_depth_sweep_cpu_v1
Substrate-product reading: establishes the public-facing depth claim (K=4..10 on real KG, extending PP-119's K=3). Current gap: PP-119 validates to K=3; v445 validates K=10 on synthetic clean bindings; KG regime at K=4..10 is untested.
Tier hint: CPU, smoke ~1-2 hours.
Why now: K=10 depth ceiling is the top open question from the mandate. Cheap, fast, builds directly on validated PP-119 infrastructure.
Pre-reg anchor: recall@1 >= 0.70 at K=5 (HARD-PASS); recall@1 < 0.50 at K=5 (HARD-FAIL).
Cross-ref: PP-119, v445 (substrate_native_reasoning_k_hop_n16384_K10).

### Rank 2: khop_conditional_and_not_cpu_v1
Substrate-product reading: enables compliance-style queries ("X that is Y but not Z") using AND+NOT composition in a K-hop chain. Novel composition not yet tested.
Tier hint: CPU, 2-3 hours.
Why now: PP-162 (AND=1.000) + PP-104 (NOT) validated separately. Their composition within a K-hop chain is the untested gap from the mandate Level 2.2.
Pre-reg anchor: recall >= 0.75 on conditional 3-step query (HARD-PASS); recall < 0.50 (HARD-FAIL).
Cross-ref: PP-162, PP-104, PP-119.

### Rank 3: khop_audit_k10_cpu_v1
Substrate-product reading: closes the deep-chain audit gate for regulated industries -- EU AI Act Art.12 compliance at K=10 depth. PP-207 validated audit at short depth; K=10 is untested.
Tier hint: CPU, 1-2 hours. Lightweight: Merkle chain is O(K*log M).
Why now: PP-207 (recall=1.000, audit=1.000) at depth likely 3-5 hops. Extending to K=10 is cheap. High product value for regulated verticals.
Pre-reg anchor: audit completeness >= 0.99 at K=10 (HARD-PASS); < 0.90 (HARD-FAIL).
Cross-ref: PP-207, PP-184, PP-185.

### Rank 4: khop_aggregate_count_cpu_v1
Substrate-product reading: enables analytic queries over K-hop results ("how many entities at distance K satisfy C?"). Composites existing AND + COUNT primitives in a K-hop chain. Untested composition.
Tier hint: CPU, 2-3 hours.
Why now: mandate Level 2.6. COUNT primitive validated (PP-163 style). AND validated (PP-162). Chain composition is the gap.
Pre-reg anchor: COUNT accuracy >= 0.80 at K=3 (HARD-PASS); < 0.60 at K=2 (HARD-FAIL).
Cross-ref: PP-162, PP-163, PP-119.

### Rank 5: khop_cyclic_dense_k10_cpu_v1
Substrate-product reading: confirms substrate handles dense cyclic KG topology (as in Wikidata, FB15K-237) at K=10 depth. PP-161 validated at lower K and lower density.
Tier hint: CPU smoke, 2-3 hours; GPU if smoke passes.
Why now: PP-161 (cyclic, recall=0.925 at lower depth). Wikidata and production KGs are dense cyclic. K=10 dense cyclic is the production-relevant extension.
Pre-reg anchor: recall@1 >= 0.80 at K=10, avg_degree=20 (HARD-PASS); < 0.55 (HARD-FAIL).
Cross-ref: PP-161, PP-177, PP-119.

### Rank 6: khop_50m_sharded_gpu_v1
Substrate-product reading: validates K-hop at Wikidata production scale (50M entities, sharded). Infrastructure validated (PP-85 100M single-step, PP-132-136 cross-shard GPU HP). K-hop pipeline at 50M is the missing link for enterprise KG pitch.
Tier hint: GPU. Batch with other GPU cells.
Why now: the 50M scale demo gate is the blocking item for enterprise Wikidata pitch. PP-166 confirms latency scales; K-hop pipeline at this scale is untested.
Pre-reg anchor: 2-hop recall@5 >= 0.65 (HARD-PASS); < 0.35 (HARD-FAIL infrastructure failure).
Cross-ref: PP-85, PP-132, PP-133, PP-135, PP-146, PP-148, PP-166.

### Rank 7: khop_probabilistic_confidence_cpu_v1
NOTE: Gated by PP-155 rescue (per-strength-level sharding). Do NOT dispatch until PP-155 reaches HP (win >= 0.95).
Substrate-product reading: enables uncertainty-aware chain queries for risk scoring. Confidence propagates through K-hop via binding amplitude.
Tier hint: CPU, 2-3 hours. After PP-155 HP rescue.
Pre-reg anchor: rank correlation of confidence vs oracle >= 0.80 at K=3 (HARD-PASS); < 0.50 (HARD-FAIL).
Cross-ref: PP-155, PP-119, PP-226.

### Rank 8: khop_temporal_bitemporal_cpu_v1
Substrate-product reading: enables historical provenance queries ("who owned X at time T") for financial compliance and legal discovery. Bitemporal infrastructure validated; K-hop + temporal conditioning untested.
Tier hint: CPU, 2-3 hours.
Pre-reg anchor: 2-hop recall@1 >= 0.70 conditioned on time T (HARD-PASS); < 0.40 (HARD-FAIL temporal key interference).
Cross-ref: PP-104 bitemporal, PP-119, PP-166.

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_multihop_maximization_2x_2026-06-09.md
- Prior multi-hop iterative drill: d:/AI/hd-instrument/notes/research_drill_iterative_multihop_where_it_works_5x_2026-06-08.md
- Cap_map K-hop anchors: PP-119, PP-120, PP-124, PP-161, PP-177, PP-185, PP-189, PP-190, PP-196, PP-197, PP-207, PP-211, PP-213, PP-214, PP-226 (see d:/AI/hd-instrument/notes/substrate_capability_map.md)
- v445 K=10 synthetic validation: substrate_native_reasoning_k_hop_n16384_K10 HARD_PASS
- v534 K=3 KG validation: substrate_khop_3hop_cpu_v1 HARD_PASS (recall=1.000)
- PP-226 completeness moat: decisive3_multihop_completeness_cpu_v1 HP (0.996 vs 0.753)
- PP-189/190 vs kNN-LM: substrate_vs_knnlm/iterative_knnlm_gpu_v1 HP (substrate=1.000 at hop3)
- PP-155 (probabilistic, gate for Rank 7): factrep_ep2_continuous_strength_cpu_v1 MIDDLE_BAND

---

## Contract section

exp_dev has full autonomy over:
- Cell design (sizes, M/N ratios, shard configurations, seed counts)
- Order of dispatch within the ranked list
- Whether to smoke Ranks 6-8 before full-grid
- Whether to combine Ranks 1+3 into a single cell
- Pre-reg band tuning within the HARD-PASS/HARD-FAIL bounds above

exp_dev must NOT modify these bounds without flagging to Orchestrator:
- Rank 1 HARD-FAIL: recall < 0.50 at K=5 (this refutes the algebraic independence model)
- Rank 2 HARD-FAIL: recall < 0.50 (refutes AND+NOT composition)
- Rank 3 HARD-FAIL: audit < 0.90 (refutes Merkle chain at depth)
- Rank 6 HARD-FAIL: recall < 0.35 (infrastructure failure; different from model failure)

PP-155 gate for Rank 7 is a hard prerequisite: check cap_map for PP-155 HP status before dispatching khop_probabilistic_confidence_cpu_v1.

## Autonomy declaration

Research has provided ranked anchors, context pointers, and pre-reg bounds. exp_dev owns execution. No experiment design in this prompt. Per [[feedback-no-experiment-design-in-prompts]], the cell structure, hyperparameters, and dispatch schedule are entirely exp_dev's domain.
