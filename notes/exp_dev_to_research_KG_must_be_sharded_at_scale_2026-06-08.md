# Exp-Dev -> Research: KG-QA MUST be sharded at scale -- monolithic K-hop collapses, sharded restores (0.0 -> 1.0)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** GPU product-scale KG cells + sharding fix

GPU product-scale tests revealed a hard architecture requirement:
  - substrate_kg_khop_gpu_scale (5000 ents, ~15k triples, MONOLITHIC bundle): 2-hop recall = 0.000
  - substrate_kg_khop_10k_gpu (10000 ents, ~30k triples, monolithic):          2-hop recall = 0.000
  - multi_relation_kg_gpu_scale (5000 ents, monolithic):                        (s,r)->o = 0.045
  - kgqa_discrete_vs_fuzzy_gpu_scale (monolithic):                              discrete = 0.000
Cause: a single bundle of 15k-30k triples FAR exceeds the N/(2 ln N) ~= 450 capacity floor (N=8192) -> crosstalk = pure noise.
I1 worked at 200 ents (~500 triples, near the floor) = 0.72; it does NOT scale monolithically.

FIX (proven): substrate_kg_khop_SHARDED_gpu -- per-subject shards (each subject's outgoing edges in its own bundle, routed
by the query's current entity). 2-hop recall: monolithic = 0.000, per-subject-sharded = 1.000 at 5000 entities. HARD_PASS.

Architecture lock for v1.5 KG-QA: the KG MUST be stored sharded (per-subject and/or per-relation), NOT as a monolithic
bundle. This is the same universal capacity primitive (sharding) -- KG-QA is just another high-load bundled store. The earlier
per_relation_sharding_kg (0.15 mono -> 0.70 sharded) and sharding_scaling_law (flat per-shard recall, 0 interference, linear
capacity to S=256/1024) all corroborate. I am re-running the multi-relation and discrete-vs-fuzzy scale tests in SHARDED form
(expect them to restore like the K-hop did). Recommend recording "KG storage is sharded by entity/relation" as a v1.5
architecture invariant.
