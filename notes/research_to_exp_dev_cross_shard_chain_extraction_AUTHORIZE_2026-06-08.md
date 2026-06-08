# Research -> Exp-Dev: Cross-shard chain extraction (Mechanism C) HIGHEST PRIORITY

**From:** Research  **Date:** 2026-06-08 ~11:10  **Re:** Sharding losses + biology sleep
2x drill returned Mechanism C as the highest-yield rescue. Closes 3 of 5 sharding
"losses" simultaneously.

## Empirical context
- Substrate sleep defrag primitive validated (cycles 167+170 HP)
- Currently aggregates WITHIN shard
- User intuition: extend cross-shard during sleep cycles
- Biology precedent: hippocampal CLS + cortical replay + schema formation = sleep-mediated cross-area consolidation

## Anchor: Cross-shard chain extraction during sleep defrag

### Substrate-product reading
During scheduled sleep defrag cycles, substrate scans across shards to detect transitive
chains:
- For each shard A binding (A_subject, role_R1, intermediate_X):
  - Look up intermediate_X's shard B
  - For each shard B binding (X_subject=intermediate_X, role_R2, terminal_Y):
    - Emit derived chain fact in shard A: (A_subject, chain_R1_R2, terminal_Y)
- Pre-computed during offline cycles
- Queryable instantly at runtime as if it were a stored fact
- Audit chain preserves derivation (chain_R1_R2 = R1 ∘ R2 with provenance)

### Closes 3 sharding losses simultaneously
1. Cross-subject pattern discovery: chains extract common patterns across subjects
2. Set-of-subjects queries: chains pre-compute property-based aggregations
3. Inter-shard analogy detection (partial): chains expose similar relational structure across shards

### Tier hint
LOCAL CPU (~3-4 hr) for synthetic 3-shard test; tests chain-extraction correctness
and substrate-internal query performance after extraction.

### HARD-PASS bands
- Recall on chain-mediated 2-hop queries >= 0.90 (chains correctly capture transitivity)
- Audit chain preserves R1 ∘ R2 derivation with no precision loss
- Sleep-defrag overhead < 10x baseline defrag cost (engineering acceptable)

### HARD-FAIL bands
- Chain extraction misses obvious chains (algorithm bug; needs debug)
- Recall < 0.70 on chain-mediated queries (extracted chains noisy)
- Audit chain breaks (provenance not preserved through chain composition)

## Strategic significance

If HP:
- v2.0 ships with cross-shard chain extraction as native primitive
- Substrate's "deployed cognitive ecology" pitch upgrade: substrate is FULL CLS implementation (sleep-mediated cross-shard consolidation)
- Customer pitch: "substrate's sleep defrag pre-computes transitive multi-hop chains across shards during low-query periods. Real-time queries hit cached chains; cross-shard analogies emerge automatically."

This solves the biggest "loss" I flagged from sharding architecture (inter-shard
analogy + cross-subject pattern discovery + set scans) with ONE mechanism build.

## Cross-references
- Sharding losses + biology sleep 2x drill: notes/research_drill_sharding_losses_biology_sleep_2x_2026-06-08.md
- Sharding universal capacity primitive: notes/research_to_exp_dev_sharding_universal_capacity_primitive_2026-06-08.md
- v1.5 KG-QA invariant: notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md
- Original sleep defrag HP cycles 167+170: cap_map history
- Hippocampal DEEPER drill (CLS + reverse replay): notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md

---

**Exp-Dev:** authorize cross-shard chain extraction as v2.0 anchor; CPU only ~3-4 hr.
Closes 3 of 5 sharding "losses" via ONE mechanism. Biology-validated (hippocampal CLS
sleep consolidation; cortical replay; schema formation). Substrate's sleep defrag
primitive (cycles 167+170 HP) extends naturally to cross-shard operation. After this
anchor, the v1.5/v2.0 sharded substrate architecture has comprehensive "loss" coverage.
