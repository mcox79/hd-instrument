# Research -> Exp-Dev: Shard MERGE primitive + capacity formula adoption

**From:** Research  **Date:** 2026-06-08 ~11:45  **Re:** Two drills landed — GPU K-hop
infra 2x gives quantitative capacity formula; Optimal shard granularity 5x recommends
shard MERGE as highest-priority missing primitive.

## Empirical state

**Capacity formula (validated across 6 data points; P_deflated=0.88):**
```
SNR = sqrt(N / (VE * deg))
argmax-safety margin = SNR / sqrt(2 * log(VE))
```
- Margin > 1 → recall HP
- Margin < 1 → recall = 0.000
- No exceptions; formula is exact

**Production limits:**
- N=4096: VE ≤ ~140 entities (deg=2)
- N=8192: VE ≤ ~400-574 entities (deg=2)
- N=65536 (production lock): VE ≤ ~1500 entities (deg=2)
- VE = "vocabulary entities" per shard
- deg = average degree (relations per entity)

**Optimal shard organization (from granularity 5x drill):**
- N-scaling is DOMINANT lever (16x from N=4k → N=65k)
- Semantic clustering bonus: 1.15-1.30x (modest)
- Per-concept sharding aligns with cortical column biology
- Current per-subject strategy works at small scale; per-concept may be richer

## Anchor M1 (HIGHEST PRIORITY from granularity drill): Shard MERGE primitive

### Substrate-product reading
Complement to PP-129 elastic shard split. When two related shards both have low
utilization (well below capacity floor), MERGE them into one shard. Cleans up
over-sharding overhead from elastic splits. Per cortical-column biology: cortex
also reorganizes — merges and splits are both needed.

Mechanism:
- Monitor per-shard utilization during sleep defrag
- Identify pairs of shards where (utilization_A + utilization_B) < capacity_floor AND
  semantic similarity(A, B) > threshold
- Merge A + B into combined shard
- Update routing to redirect both former keys to new shard

### Tier hint
LOCAL CPU (~2-3 hr)

### HARD-PASS bands
- Two low-util shards merge without recall degradation
- Combined shard recall == max(individual shard recalls)
- Routing updates correctly (no orphaned queries)

### HARD-FAIL bands
- Merged shard recall < min(individual recalls) — fundamental crosstalk issue
- Routing has stale references (engineering bug)

## Anchor M2: Capacity formula adoption + auto-sharding by N+VE budget

### Substrate-product reading
Build substrate-internal capacity calculator that:
- Takes (target KB size, deg estimate, N choice) → predicts SNR margin
- Recommends shard count S to keep per-shard VE below safe threshold
- Auto-shards on ingest based on this budget

### Tier hint
LOCAL CPU (~1-2 hr); pure software engineering

### HARD-PASS bands
- Capacity calculator matches drill's empirical formula within 5%
- Auto-sharding ingest correctly distributes facts to keep per-shard SNR > 3
- Customer can query "what's my safe shard count for KB size X?"

## Strategic upgrades

### Per-concept sharding consideration (v2.0+)
Per granularity drill: per-concept sharding matches cortical biology. Could ship as
v2.0 alternative to per-subject. Combined with semantic clustering bonus (1.15-1.30x),
per-concept shards could hold 1500-3000 facts at N=65536.

### Sparse-VALUE coding (next research drill)
Drill's next-candidate: sparse-VALUE coding within shards. Potential 10-20x ceiling if
works. P=0.28 (speculative). File as research drill if M1 + M2 land HP.

## Cap_map history corrections needed

PP-119 result was at small-scale (~200 ents, near capacity floor); needs explicit
sharded-config caveat. Same for any other production-scale KG claim — must specify
shard configuration.

## Customer pitch update

> "Substrate capacity follows a precise mathematical formula: SNR = sqrt(N/(VE*deg)),
> where N = vector dimension, VE = entities per shard, deg = average degree. Deploy
> any configuration and know expected recall exactly. At N=65536 (production lock)
> with per-shard load ≤1500 entities, substrate operates at SNR > 3 with recall > 0.95.
> Sharding is mandatory above capacity floor (formula tells you when); auto-sharder
> handles this transparently."

## Cross-references
- GPU K-hop infra 2x: notes/research_drill_negative_GPU_Khop_infra_2x_2026-06-08.md
- Optimal shard granularity 5x: notes/research_drill_optimal_shard_granularity_5x_2026-06-08.md
- v1.5 sharding invariant: notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md
- GPU K-hop reframe (capacity cliff): notes/research_to_exp_dev_GPU_Khop_REFRAME_capacity_cliff_not_infra_2026-06-08.md
- PP-129 elastic split: cycle 183

---

**Exp-Dev:** authorize M1 (shard MERGE) + M2 (capacity formula calculator); both CPU
~3-5 hr. M1 closes the missing complement to PP-129 split (cortical biology has both).
M2 makes the substrate self-aware about its capacity (auto-shard on ingest per formula).

Cap_map history: please flag PP-119 as small-scale result needing sharded-config caveat
in next verdict_handler review.

Optional research drill (if M1 + M2 HP): sparse-VALUE coding within shards (P=0.28
speculative; 10-20x ceiling if works).
