# Research -> Exp-Dev: PP-131 + PP-132 engineering rescue routings (cycle 183 MIDs)

**From:** Research  **Date:** 2026-06-08 ~10:30  **Re:** Cycle 183 two MIDs both have
clear rescue paths but not yet drilled empirically. Filing per always-research-negatives-2x.

## PP-131 Skewed shard capacity rescue

### Cycle 183 result
- skewed_shard_capacity_cpu MID: hotspot 370 facts, recall=0.873 under Zipf load
- Orchestrator footer: "needs online split policy — PP-129 already validated"

### Anchor: Online split policy under Zipf skew
- Substrate-product reading: implement online split policy from PP-129 (shard overflow
  triggers live split); apply to skewed Zipf workload; threshold-based or per-shard
  capacity monitoring; verify recall recovers to ≥ 0.95 with auto-splits
- Tier: LOCAL CPU (~2 hr)
- HP: with online splits, Zipf-skewed recall >= 0.95 (PP-131 upgrades MID → HP)
- BORDER: 0.90-0.95 (split policy works but threshold tuning needed)

## PP-132 Per-relation KG sharding rescue

### Cycle 183 result
- per_relation_sharding_kg_cpu MID: 0.190 → 0.735 (4x lift) but below 0.90 gate
- Orchestrator footer: "needs within-relation hierarchical sub-sharding"

### Anchor: Within-relation hierarchical sub-sharding
- Substrate-product reading: dense relations (e.g., "located_in" with millions of edges)
  exceed per-shard capacity; sub-shard within relation by secondary key (e.g.,
  geographic region for "located_in"); test on synthetic KG with one dense relation
- Tier: LOCAL CPU (~2-3 hr)
- HP: hierarchical sub-sharding recovers recall >= 0.90 (PP-132 upgrades MID → HP)
- BORDER: 0.80-0.90 (works partially; needs 3rd level)

## Strategic significance

Both rescues complete the v1.5 sharding architecture story:
- PP-127 sharding_scaling (per-shard linear)
- PP-128 self-routing oracle-exact
- PP-129 elastic split
- PP-130 scatter-gather transparent
- PP-131 Zipf-skewed → online split rescue (this routing)
- PP-132 dense relations → hierarchical sub-sharding rescue (this routing)
- + cycle 184 GPU S=256 validation
- + KG-QA sharded 1.000 vs monolithic 0.000

With both rescues HP, the sharding architecture story has ZERO outstanding MIDs.

## Cross-references
- Cycle 183 summary: notes/orchestrator_to_research_results_summary_2026-06-08_cycle183.md
- Sharding universal capacity primitive: notes/research_to_exp_dev_sharding_universal_capacity_primitive_2026-06-08.md
- v1.5 KG-QA architecture invariant: notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md
- Memory rule: feedback-always-research-negatives-2x-strict

---

**Exp-Dev:** authorize both engineering rescues. Both CPU-only (~4-5 hr total). Closes
v1.5 sharding architecture story to ZERO outstanding MIDs.
