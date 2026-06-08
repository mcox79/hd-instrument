# Research -> Exp-Dev: 5x deep-dive 5 ranked anchors AUTHORIZE

**From:** Research  **Date:** 2026-06-08 ~03:15  **Re:** Per user audit "did you route
these for experiments?" — the 5x deep dive drill handoff had 5 ranked engineering anchors
not yet explicitly AUTHORIZED. Filing per always-route-to-exp-dev convention.

## Anchors authorized (rank-ordered)

### Anchor I1 (HIGHEST PRIORITY): SUBSTRATE-KG-TRIPLES-KHOP
- Source: drill handoff Anchor 1; Research note Section "Strategic Implications"
- Substrate-product reading: encode public KG subset (NELL-595 or Freebase-mini) as VSA
  (entity, relation, entity) triples; run 2-hop and 3-hop queries; measure recall@K
  against gold paths. **Lowest-risk extension of PP-11 synthetic K=12 recovery=0.987 result
  to real KG data.**
- Tier: LOCAL CPU (1-2 hr) at N=1024 or N=4096
- HARD-PASS: recall@K >= 0.70 on real KG 2-hop; **gates KG QA as substrate product**
- BORDER: 0.55-0.70 (works partially)
- HARD-FAIL: < 0.55 (real KG bindings don't behave like synthetic clean bindings)

### Anchor I2 (HIGHEST PRIORITY): SUBSTRATE-BRIDGE-EXTRACTION-PIPELINE
- Source: drill handoff Anchor 2; BridgeRAG (arXiv 2604.03384; April 2026 training-free
  SOTA) as reference; IRCoT (ACL 2023) structural template
- Substrate-product reading: small LLM (Pythia-160M sanity-check first → Llama-3.1-8B
  if Pythia confirms) extracts bridge entity from hop-1 results; feed named bridge as
  explicit hop-2 query into substrate retrieval; measure HotpotQA dev recall@2
- Tier: PYTHIA-160M LOCAL PRE-TEST (~3 min $0) → escalate Llama-3.1-8B if Pythia
  confirms (~2-3 hr local CPU or GPU)
- HARD-PASS: recall@2 >= 0.55 (lifts from 0.31-0.37 ceiling; principled rescue validated;
  BridgeRAG-equivalent mechanism confirmed for substrate)
- HARD-FAIL: < 0.45 (BridgeRAG mechanism doesn't transfer to substrate; structural
  issue beyond grounding-signal cleanness)

### Anchor I3: SUBSTRATE-PPR-SPREADING-ACTIVATION (HippoRAG-equivalent)
- Source: drill handoff Anchor 3; HippoRAG (NeurIPS 2024) reference architecture
- Substrate-product reading: implement K-hop spreading activation over substrate triple
  store; each spreading step = VSA K-hop lookup from seed entities; measure convergence
  depth (K required for full 2-hop neighborhood coverage) + retrieval recall@K
- Tier: LOCAL CPU SMOKE (~1-2 hr), Remote CPU for scaling
- HARD-PASS: PPR-spreading converges within K=5 + recall@K >= 0.70 at 2-hop neighborhood
  (HippoRAG-equivalent at substrate cost; 10-30x lower than IRCoT per drill)
- BORDER: K=6-10 convergence (works but slower than HippoRAG)
- HARD-FAIL: > K=10 convergence OR recall@K < 0.55 (PPR doesn't behave PageRank-like
  over VSA bindings)

### Anchor I4: SUBSTRATE-BEAM-RETRIEVAL (Beam Retrieval VSA equivalent)
- Source: drill handoff Anchor 4; Beam Retrieval (Zhang et al. 2023; +44.6% EM on MuSiQue)
- Substrate-product reading: maintain K=3 candidate partial chains in parallel; each
  hop expands each chain by one K-hop step; score by accumulated binding consistency;
  prune to K survivors. **Mirrors Beam Retrieval +44.6% EM gain on MuSiQue (largest
  single improvement in lit), implemented in VSA over stored triples.**
- Tier: LOCAL CPU SMOKE (K=2, chain length 2; ~1-2 hr)
- HARD-PASS: substrate beam-retrieval recall@2 >= 0.55 on MuSiQue subset (+X over baseline)
- BORDER: 0.40-0.55
- HARD-FAIL: < 0.40 (beam mechanism doesn't help substrate; per-chain VSA scoring is
  too noisy)

### Anchor I5: SUBSTRATE-LEGAL-CITATION-DEMO (customer-pitch prototype)
- Source: drill handoff Anchor 5; SYMBALS (PMC 2021) citation snowballing literature
- Substrate-product reading: load ~500 paper citation records as VSA (paper_id, cites,
  paper_id) triples; forward/backward snowballing via K-hop; verify completeness against
  known citation set; **customer-demo-grade prototype requiring NO LLM, NO fuzzy retrieval
  — just substrate K-hop over clean bindings**
- Tier: LOCAL CPU (~1 hr; very fast)
- HARD-PASS: substrate K-hop snowball recovers >= 95% of known citation set in 3 hops
  (demo-ready; legal/medical pitch backed empirically)
- BORDER: 80-95% (works; demo-acceptable)
- HARD-FAIL: < 80% (citation snowball needs different mechanism than K-hop traversal)

## Strategic priorities

If I1 (real KG triples) AND I2 (BridgeRAG-equivalent) BOTH HP:
- v1.5 ships KG QA at 10-30x cost advantage vs IRCoT (HippoRAG-equivalent)
- v1.5 ALSO ships free-text multi-hop via small-LLM bridge extraction (BridgeRAG-equivalent)
- Substrate becomes published-SOTA multi-hop architecture at categorical cost advantage

If only I2 HP:
- v1.5 ships free-text multi-hop via bridge extraction; KG QA needs further work

If I3 (PPR) HP:
- HippoRAG-equivalent capability explicit; substrate ships KG QA at production-grade

If I5 (citation demo) HP:
- Customer pitch backed empirically for legal/medical/scientific verticals immediately
- Sales asset; cheapest to build

## Cross-references

- 5x deep dive drill: notes/research_drill_iterative_multihop_where_it_works_5x_2026-06-08.md
- Drill handoff (with the 5 anchors): notes/exp_dev_handoff_research_iterative_multihop_where_works_5x_2026-06-08.md
- Strategic synthesis (re-prioritization): notes/research_to_exp_dev_iterative_pattern_universal_principle_strategic_2026-06-08.md
- Existing N1-N3 / R1-R3 native substrate battery: notes/research_to_exp_dev_NATIVE_substrate_multihop_HotpotQA_2026-06-07.md
- Existing N1b / T5 additions: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md

---

**Exp-Dev:** authorize all 5 ranked anchors. I1+I2 are highest yield (real KG validation
+ BridgeRAG-equivalent). I5 is cheapest (1 hr, customer-demo grade). I3+I4 add HippoRAG
and Beam-Retrieval published mechanisms to substrate's KG QA story. Total ~6-10 hr CPU
across all 5 anchors. Outcomes determine v1.5 KG QA architecture + customer pitch
empirical backing.

These supplement N1-N3 / R1-R3 (already routed) with literature-aligned mechanism tests.
