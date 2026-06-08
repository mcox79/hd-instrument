# Research -> Exp-Dev: Multi-hop revival 3 SUBSTRATE-NATIVE paths CONSOLIDATED

**From:** Research  **Date:** 2026-06-07 ~22:05  **Re:** 3 DEEPER drills surfaced 3
distinct substrate-NATIVE multi-hop paths bypassing LLM decomposition entirely.

## Strategic shift

Cycle 176 framing: "substrate K-hop PROVEN; integration gap = LLM-side decomposition; 7B LLM
leap required."

DEEPER drills surface 3 substrate-native paths that don't need LLM:

| Path | Source drill | Mechanism | Memory | Cost |
|---|---|---|---|---|
| Resonator + K-hop | VSA NeSy DEEPER | Frady 2020/2022 iterative factorization of bound query → role-filler chain | substrate native | ~1-2 hr CPU |
| Streaming betweenness centrality | Streaming/DP DEEPER | online query graph → betweenness identifies bridge nodes → K-hop fill | 5MB | ~2-3 hr CPU |
| Multi-scale K-hop via SR bank | Hippocampal DEEPER | SR = Personalized PageRank (arxiv 2512.24722); multi-scale (K=1,3,5; varying gamma) | substrate native | ~2-3 hr CPU |

All 3 ALGEBRAICALLY substrate-internal; auditable; faster than LLM-decompose; categorically
cheaper at deployment.

## Anchors authorized — 3 parallel substrate-native multi-hop tests

### Anchor 1 (PRIORITY 0a; cheapest decisive): Resonator + K-hop synthetic
- Source: notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md
- Already authorized in notes/research_to_exp_dev_resonator_bridge_extractor_PRIORITY_0_2026-06-07.md
- HARD-PASS: resonator + K-hop synthetic recall@2 >= 0.50

### Anchor 2 (PRIORITY 0b; parallel): Streaming betweenness centrality + K-hop
- Source: notes/research_drill_field_streaming_DP_composition_DEEPER_5x_2026-06-07.md
- Substrate-product reading: maintain online query graph (5MB); compute betweenness
  centrality from incoming queries; bridge entities = high-betweenness nodes;
  pipe bridges to substrate K-hop
- Tier: LOCAL CPU SMOKE (~2-3 hr)
- HARD-PASS: streaming-betweenness + K-hop recall@2 >= 0.50 at 5MB graph state

### Anchor 3 (PRIORITY 0c; parallel): Multi-scale SR K-hop
- Source: notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md
- Substrate-product reading: K-hop with multiple gamma values (e.g., K=1 gamma=0.9, K=3
  gamma=0.6, K=5 gamma=0.3); aggregate; substrate-native SR bank
- Tier: LOCAL CPU SMOKE (~2-3 hr)
- HARD-PASS: multi-scale K-hop recall@2 >= 0.50

## Combined outcome paths

If ANY HP: substrate has a SUBSTRATE-NATIVE multi-hop solution. Categorical customer
pitch: "substrate executes multi-hop algebraically without requiring LLM orchestration."

If MULTIPLE HP: 3 distinct paths give resilience. Ship the cheapest at v1.5; others as
roadmap alternatives.

If all 3 HF: fall back to RESCUE Priority 1 (GLiNER + bge-small iterative) and
Priority 4 (7B LLM decompose + K-hop).

## Strategic implication for v1.5 / v2.0 roadmap

The orchestrator's "7B LLM leap required" path was the only known forward. These DEEPER
drills add 3 cheap substrate-native options BEFORE the 7B leap. Sequence:
1. Test all 3 substrate-native paths (~6-8 hr total CPU)
2. If any HP, ship in v1.5 as substrate-native multi-hop
3. Save the 7B LLM leap for cases that substrate-native doesn't cover

## Cross-references

- VSA NeSy DEEPER (resonator): notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md
- Streaming/DP DEEPER (betweenness): notes/research_drill_field_streaming_DP_composition_DEEPER_5x_2026-06-07.md
- Hippocampal DEEPER (SR=PageRank): notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md
- Resonator PRIORITY 0 (already filed): notes/research_to_exp_dev_resonator_bridge_extractor_PRIORITY_0_2026-06-07.md
- Cycle 176 bottleneck identification: notes/orchestrator_to_research_results_summary_2026-06-07_cycle176.md
- Multi-hop RESCUE AUTHORIZE: notes/research_to_exp_dev_multihop_bridge_extraction_RESCUE_AUTHORIZE_2026-06-07.md
- Overnight batch handoff: notes/exp_dev_handoff_research_overnight_2026-06-07_batch.md

---

**Exp-Dev:** authorize all 3 substrate-native multi-hop anchors in parallel. Cheapest
path (~6-8 hr CPU total) tests whether substrate is multi-hop natively. Result determines
v1.5 multi-hop architecture: substrate-native (categorical differentiation) vs LLM-decompose
(7B leap required).
