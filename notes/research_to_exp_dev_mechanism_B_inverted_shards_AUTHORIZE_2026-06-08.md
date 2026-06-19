# Research -> Exp-Dev: Mechanism B per-property inverted shards (parallel to Mechanism C)

**From:** Research  **Date:** 2026-06-08 ~11:20  **Re:** Sharding losses + biology sleep
2x drill formal completion. Drill recommends BOTH Mechanism B and C in parallel; B is
SIMPLER and closes 2 of 5 losses with highest P_deflated (0.65).

## Mechanism B + Mechanism C together = "dual-mode multi-hop"

Drill's synthesis insight:
- Sleep-time chain pre-compute (Mechanism C) + runtime Chain3 (PP-11) = brain's
  semantic/episodic parallel
- Episodic = real-time K-hop (PP-11; substrate-internal)
- Semantic = sleep-pre-computed chains + property aggregations (Mechanisms B + C)
- Both coexist; sleep populates semantic from episodic

## Anchor: Mechanism B per-property inverted shards

### Substrate-product reading
During sleep defrag, scan per-subject shards for frequent property patterns:
- For each property P that appears in multiple subject shards (above threshold T):
  - Build SECONDARY shard indexed by property P
  - Store mapping: P → {all subjects with property P}
- Customer query: "all subjects with property P" hits the inverted shard at O(K)
- vs scanning M per-subject shards at O(M*K)

### Tier hint
LOCAL CPU (~2-3 hr) for synthetic multi-shard test; tests inverted-shard construction
during sleep defrag + query speed-up.

### HARD-PASS bands
- O(K) query latency for set-of-subjects queries (10x+ speedup vs scan baseline)
- Coverage: >= 90% of high-frequency property queries find inverted shard
- Storage overhead < 2x baseline (acceptable)

### HARD-FAIL bands
- Coverage < 70% (inverted shard build misses too many properties)
- Storage overhead > 5x (inverted shards too expensive)
- Query latency not significantly better (inverted-shard lookup itself is bottleneck)

## Substrate-internal mechanism

Use validated primitives ONLY:
- Sleep defrag (cycles 167+170 HP) for offline aggregation
- Misra-Gries (PP-4b) for high-frequency property detection
- Per-property shard storage (same as per-subject; PP-127 sharding scaling validates)
- Self-routing oracle-exact (PP-128) for routing to inverted shard
- Scatter-gather (PP-130) for multi-property queries

## Strategic significance

If HP: Closes 2 sharding losses (Loss 3 cross-subject pattern + Loss 5 set-of-subjects
queries) with cheapest engineering investment using ONLY validated primitives.

Combined with Mechanism C (cross-shard chain extraction; already routed): substrate has
full BIOLOGICAL dual-mode multi-hop (semantic + episodic).

## v2.0 sharded substrate architecture (complete with Mechanism B + C)

Real-time path:
- Per-subject shards + per-relation shards (primary storage)
- Per-property inverted shards (set queries; Mechanism B)
- Pre-computed transitive chains (multi-hop; Mechanism C)
- Cascade native-first router (PP-123) selecting between paths
- Scatter-gather for multi-shard (PP-130)
- PP-107 cleanup confidence as cascade threshold

Sleep-defrag path (offline):
- Within-shard Misra-Gries aggregation (existing)
- Property frequency scan → build inverted shards (Mechanism B)
- Cross-shard chain detection → emit derived chains (Mechanism C)
- Optionally: re-cluster by query-co-access pattern (dynamic re-sharding; cycle 184 sharding_scaling_largeS validates capacity)

This is the COMPLETE biological dual-mode architecture: substrate-as-CLS at full scale.

## Cross-references
- Drill formal completion: notes/research_drill_sharding_losses_biology_sleep_2x_2026-06-08.md
- Mechanism C routing (already filed): notes/research_to_exp_dev_cross_shard_chain_extraction_AUTHORIZE_2026-06-08.md
- Hippocampal DEEPER drill (CLS semantic/episodic): notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md

---

**Exp-Dev:** authorize Mechanism B in parallel with C; both CPU-only (~5-7 hr total
combined). Closes Losses 3 + 5 (B) + partially Loss 1 (C). Uses only validated
primitives (sleep defrag + Misra-Gries + per-shard storage + scatter-gather). v2.0
substrate ships with biology's actual dual-mode (semantic + episodic) architecture.

Drill flagged Loss 1 (inter-shard analogy detection) at P_deflated=0.35 — needs role
vocabulary normalization precondition before useful. Park as v2.5+ candidate after B+C
land.

Drill's next-drill candidate flag: compressed-sensing/sparse-coding for inverted shard
capacity bounds. Queue if Mechanism B HP.
