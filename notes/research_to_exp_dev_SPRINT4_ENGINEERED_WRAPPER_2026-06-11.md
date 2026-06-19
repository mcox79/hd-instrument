# Research -> Exp-Dev: SPRINT-4 ENGINEERED WRAPPER -- substrate v3.2

**From:** Research  **Date:** 2026-06-11
**Re:** 5 engineering drills complete -- substrate v3.2 architecture

## v3.2 Architecture (synthesized from 5 3x DEEP drills)

Substrate v3.1 (static algebra + temporal refresh + context fields + temporal policy) confirmed empirically (PP-348/PP-349/PP-350/PP-351/PP-352 cycle 227).

**Sprint-4 = engineered wrapper layer.** ALL 5 protection mechanisms require NO substrate core changes. They ride on substrate's existing algebra via Python wrapper + routing.

## Sprint-4 anchors (cheapest decisive tests first)

### Tier 0 -- cheapest engineering gates (<1hr each)

| Anchor | Cost | Mechanism |
|---|---|---|
| **FHRR-RS-parity-T0** | 15 min CPU | FHRR-as-Reed-Solomon parity in ~30 lines torch; encode_rs/decode_rs |
| **Tier-1-frozen-T0** | <1hr CPU | Tier-1 atoms frozen by policy + Tier-3 mutable; locality F9 |
| **Per-tier-importance-defaults-T0** | <1hr CPU | Tier-1 always important; Tier-3 importance-by-access; engineered importance per-tier |
| **Write-lock-after-threshold-T0** | <1hr CPU | shard marked immutable after threshold; per-shard protection scheme 1 |

### Tier 1 -- multi-substrate wrappers (4-8 hr each)

| Anchor | Cost | Architecture |
|---|---|---|
| **2-substrate FastSlow CLS** | ~4 hr | hippocampal CLS analog; fast store + slow store + transfer protocol |
| **3x Redundant substrate** | ~2 hr | 3 W matrices mirrored for critical content; reliability under noise |
| **PerRole substrate (math/code/comm)** | ~6 hr | per-domain isolation prevents compositional crosstalk |
| **Crystallized substrate (Tier-1 only)** | ~4 hr | dedicated substrate for frozen Tier-1 atoms |
| **ExcitabilityGated substrate** | ~6 hr | priority protection above capacity cliff |

### Tier 2 -- combined v3.2 unified test

| Anchor | Test |
|---|---|
| **v3.2-unified-architecture** | All 5 engineered layers + 3 v3.1 capabilities running in ONE substrate over ONE episode; demonstrate end-to-end |
| **v3.2-multi-seed n=5** | confirm wrapper layer doesn't introduce seed-instability |
| **v3.2-scale-test** | v3.2 at 100K + 1M edits (vs current 50K validated for refresh alone) |

## Architectural priorities (per cycle 226 meta-finding)

Privilege temporal + contextual mechanisms in P_deflated. The 5 engineering layers DO map to substrate's temporal/contextual strengths:
- Per-tier defaults = CONTEXTUAL (tier IS context)
- Write-lock-after-threshold = TEMPORAL (lock after N writes)
- Multi-substrate transfer = TEMPORAL (slow consolidation)
- Reed-Solomon parity = ALGEBRAIC (FHRR-native)
- Tier-1-frozen + Tier-3-mutable = CONTEXTUAL (tier structure)

These should empirically validate per the pattern. (CORE-PERIPHERY-FIXED was a different beast -- fixed topological protection in substrate's actual algebra; refresh-cycle replaced it.)

## What this enables strategically

Substrate v3.2 = production-grade engineering wrapper over validated v3.1 core. Customer pitch becomes:
- Compositional symbolic engine (validated)
- Lifelong self-modification (PP-349/352 to 50K; engineered wrapper extends further)
- Multi-drive integration via temporal policy (validated)
- Polysemy + context resolution (validated)
- Audit + GDPR + sub-ms (validated)
- **PLUS engineered protection/locality/redundancy for production deployment** (Sprint-4 validates)

## Cheap critical path tonight

If you can get to:
1. FHRR-RS-parity-T0 (15 min)
2. Tier-1-frozen-T0 (<1hr)
3. Per-tier-importance-defaults-T0 (<1hr)
4. Write-lock-after-threshold-T0 (<1hr)

That's ~3hr CPU for 4 decisive engineering gates. By morning we know if the wrapper layer is implementable AT THE CHEAPEST mechanisms before scaling to multi-substrate (which is heavier engineering).

## Cross-references
- Memory: substrate_v32_engineered_wrapper_2026-06-11.md
- 5 engineering drills: research_drill_*_engineered_3x_2026-06-11.md + research_drill_per_shard_protection_3x_2026-06-11.md + research_drill_multi_substrate_engineered_3x_2026-06-11.md + research_drill_erasure_coded_redundancy_3x_2026-06-11.md + research_drill_locality_engineered_3x_2026-06-11.md + research_drill_engineered_importance_3x_2026-06-11.md
- v3.1 validation: PP-348/349/350/351/352 cycle 227
- Drill pattern: drill_pattern_temporal_contextual_not_structural_2026-06-11.md

---

**Exp-Dev:** Sprint-4 ENGINEERED WRAPPER LAYER. Tier 0 cheap gates (FHRR-RS + Tier-1-frozen + per-tier-importance + write-lock; ~3hr CPU). Tier 1 multi-substrate (heavier engineering). Tier 2 v3.2 unified end-to-end.

User pushback validated: substrate isn't fundamentally limited; missing features are engineering choices realizable via wrapper. v3.2 implementable WITHOUT substrate core changes.
