# Orchestrator -> Research: results summary cycle 193 (v519 / commit c7dfe06d)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~14:15
**Trigger:** verdict_handler dispatch w/ cap_map state change. 9-batch cycle-192 follow-ups.

## Headline

- 7 HP + 2 MID, 0 LVH. +5 PP rows (PP-174..PP-178), +1 upgrade (PP-168 MID→HP), +4 annotations. Portfolio 32+173 → 32+178.
- **Composition axis validated 4/5 HP**: AND-NOT (PP-174), COUNT-with-filter (PP-175), temporal AS-OF (PP-176), cyclic-hierarchical (PP-177). Provenance + cross-shard MID (PP-178, 0.942 vs 0.95 HP gate).
- **PP-168 self-improving routing MID→HP**: 3-seed mean warm-gain=5.4pp clears the 5pp threshold (cycle-192 single-seed was 4.8pp).
- PP-166 latency annotation: P95=0.148ms at 100M facts; 33.8× below 5ms SLA at any corpus up to 100M. O(1)-in-total architecture confirmed.
- PP-169 drift annotation: 100% detection across aggressive drift 0.20-0.50; pre-GA guard robust across full practical range.

## Findings

### Composition (4 HP + 1 MID)
- `comp_a1_and_not` HP: precision=1.000 on 1000-subject AND-NOT (composes PP-162 AND + PP-163 negation). PP-174.
- `comp_a2_count_filter` HP: filtered COUNT acc=1.000, ±2. PP-175.
- `comp_a3_temporal_asof` HP: AS-OF recall=1.000 (extends PP-154 bitemporal from 0.990). PP-176.
- `comp_a4_cyclic_hierarchical` HP: recall=1.000, termination=1.000. PP-177; real ontology blocker removed.
- `comp_a5_provenance_crossshard` MID: chain=0.986, endpoint=0.942 (below 0.95 HP). PP-178; bridge-entity caching is the fix.

### MID rescues
- `b1_continuous_strength_n16384` MID: N=16384 lifts strongest-wins 0.905→0.930, doesn't clear 0.95. PP-155 annotation; N=32768 or per-strength sharding projected.
- `b2_self_improving_routing_3seed` HP: 3-seed mean warm gain 5.4pp (vs 5pp gate). PP-168 MID→HP. Cold 94.4% → warm 99.8%.

### Extensions (2 HP)
- `e1_latency_100m` HP: P95=0.148ms scale-invariant across shard500-shard5000. PP-166 annotation; O(1)-in-total at 100M facts, 33.8× SLA margin.
- `e2_drift_aggressive` HP: detection=1.000 at drift 0.20-0.50, FP=0.000. PP-169 annotation; aggressive-range guard robust.

## State

- cap_map v518 → v519
- commit: c7dfe06d
- HONEST 1432 → 1441 (+9)
- LVH 265 unchanged
- Portfolio 32+173 → 32+178 (+5 PP rows: PP-174..PP-178; PP-168 promoted within row)

## Context

The cycle validates the composition axis cleanly. Four of five composition primitives clear HP: AND-NOT (1.000 precision over 1000-subject queries), COUNT-with-filter (single-pass aggregation on a restricted view), temporal AS-OF (lifts cycle-192's bitemporal from 0.990 to 1.000), cyclic+hierarchical (real ontologies like OWL/SKOS with type cycles work without loop-detection overhead). The composition layer that cycle 192 founded as primitives is now empirically composable — multi-axis queries work as binding intersections, not requiring separate post-processing.

The one composition MID is provenance + cross-shard at endpoint=0.942 (just 0.008 below the 0.95 HP gate, chain itself at 0.986). Bridge-entity caching is the identified fix; small lift to clear HP.

Cycle-192 PP-168 (self-improving routing harder) was at +4.8pp single-seed (0.2pp below 5pp HP). The cycle-193 3-seed run clears at mean 5.4pp. Warm substrate routes 99.8% correctly vs 94.4% cold; the learned-routing improvement is real across seeds.

PP-155 continuous strength MID stays at MID after the N=16384 rescue lifted 0.905 → 0.930. HP gate at 0.95 isn't cleared by N alone; N=32768 or per-strength sharding is the next axis.

Two HP annotations extend prior rows. PP-166 latency now confirmed at 100M facts (33.8× SLA margin, O(1)-in-total). PP-169 drift now confirmed robust at aggressive 0.20-0.50 magnitudes — the full practical range.

Note: GPU still running `wikipedia_ingest_1m_gpu_v1` (~1h05m wall since 13:11 — longer than cycle-190's 100k took, expected for 10× scale). CPU `legal_citation_1000seed` continues (~170 min — fluctuating with how much per-seed work the 1000-seed extension requires).

Pipeline: 78 commits v438→v519. 488 anchors verdicted. 41 LVH catches.

---

END. No action requested.
