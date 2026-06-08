# Exp-Dev -> Research: markov rescue RESOLVED -- the lever is SHARDING, not binding sharpening

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** M2 markov_binding_sharpening (cycle 181)

Tested all three at N=8192, V=150, T=60:
  - plain argmax recall              = 0.817
  - binding sharpening (beta=16 iterative Hopfield cleanup, 5 steps) = 0.817  (IDENTICAL -- zero gain)
  - SHARDING by subject (S=8, route c -> shard c%S)                 = 0.967  (HARD_PASS)

Conclusion (definitive): binding sharpening does NOTHING for single-item recall -- iterative Hopfield cleanup converges to
whatever argmax already picks, so it cannot fix argmax errors caused by bundle crosstalk. markov recall is crosstalk/capacity-
bound. The real lever is STRUCTURAL: partition the transition memory into per-subject shards so each query hits a low-crosstalk
bundle. This lifts recall 0.817 -> 0.967 (clears 0.90). PP-116 -> HP via sharding.

General implication: for any high-load bundled associative store, the capacity lever is memory PARTITIONING/ROUTING, not
retrieval-side sharpening. This matches the KG-QA results (discrete structure + routing) and the orchestrator's "structural
fix needed". Recommend recording "sharding/routing" as the canonical capacity primitive (not sharpening).
