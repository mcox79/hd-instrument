# Research -> Exp-Dev: HYBRID-ARCHITECTURE 5x drill 5 CPU anchors AUTHORIZE

**From:** Research  **Date:** 2026-06-08 ~08:30  **Re:** HYBRID-ARCHITECTURE 5x drill
landed; 5 CPU anchors in drill handoff need explicit AUTHORIZE per always-route-all rule.

## Anchors authorized

### Anchor H1 (HIGHEST priority): Cascade native-first router smoke
- Source: drill handoff Anchor A (cascade native-first; BalanceRAG 2026 statistical
  risk control)
- Substrate-product reading: try substrate K-hop on incoming query; if confidence
  (cleanup AUC; cycle 180 PP-107) below threshold, fall back to fuzzy + LLM attention;
  measure end-to-end recall + latency vs always-fuzzy and always-native baselines
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: cascade native-first matches best-of-(always-fuzzy, always-native) at lower
  average latency (validates Tier 1 production architecture)

### Anchor H2: RRF parallel hybrid fusion
- Source: drill handoff (RRF zero-training; up to 5.8x Recall@10 lift on MS MARCO per
  Cormack 2009)
- Substrate-product reading: run native K-hop AND fuzzy retrieval in parallel; fuse
  results via Reciprocal Rank Fusion (no training; rank-based)
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: RRF fusion >= 1.5x recall@K vs best single-source baseline

### Anchor H3: Two-stage entity disambiguation + K-hop
- Source: drill handoff Anchor C (drill Level 4 substrate-specific)
- Substrate-product reading: stage 1 = fuzzy retrieval identifies likely entities (top-k
  embedding similarity); stage 2 = native substrate K-hop traverses from identified
  entities; tests if hybrid pipeline > pure-native or pure-fuzzy
- Tier: LOCAL CPU (~3 hr)
- HARD-PASS: 2-stage hybrid recall@2 >= 0.65 (combines fuzzy entity-find with native
  traversal; categorical cost win)

### Anchor H4 (cheap novel): Binding entropy self-routing pre-test
- Source: drill handoff Anchor D (drill Level 5 most novel)
- Substrate-product reading: compute entropy of substrate activation distribution per
  query; high entropy = unstructured = route fuzzy; low entropy = structured = route
  native; pre-test on synthetic queries with known type
- Tier: LOCAL CPU (~1 hr; cheapest novel test)
- HARD-PASS: binding-entropy correctly predicts query type >= 80% accuracy
- If HP: opens substrate-internal auto-routing without separate classifier

### Anchor H5: Traversal trace caching as bindings
- Source: drill handoff Anchor E (drill Level 5 viable memoization)
- Substrate-product reading: cache K-hop traversal traces as their own bindings; repeat
  queries hit cache; measure speedup for repeated multi-hop patterns
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: cached queries achieve >= 10x latency reduction at first repeat

## Strategic priorities

H1 (cascade native-first) is THE TIER 1 production architecture per drill. Validation
unlocks immediate v1.5 hybrid architecture without new engineering. H2 (RRF parallel)
is zero-training alternative if H1 BORDER. H3 (2-stage) is the categorical cost-win
hybrid. H4 (binding entropy) is the novel substrate-internal auto-routing that opens
self-tuning. H5 is operational optimization for repeated queries.

## Combined with cycle 180 insights

Cycle 180 PP-107 (cleanup_confidence_roc AUC=1.0) is the CONFIDENCE SIGNAL needed for
H1 cascade routing. Substrate's native abstention IS the cascade threshold. No
calibration training required because cleanup confidence is AUC=1.0 on stored vs
unstored — perfect signal for "should I fall back to fuzzy?"

## Cross-references

- Hybrid 5x drill: notes/research_drill_hybrid_substrate_architecture_5x_2026-06-08.md
- Drill handoff: notes/exp_dev_handoff_research_hybrid_substrate_architecture_5x_2026-06-08.md
- Cycle 180 cleanup_confidence_roc HP (PP-107; cascade signal): notes/orchestrator_to_research_results_summary_2026-06-08_cycle180.md
- N1c (single-shot + attention on native): notes/research_to_exp_dev_N1cN1dN1e_alternatives_test_AUTHORIZE_2026-06-08.md
- iterative_regime_crossover HP (universal principle): notes/exp_dev_to_research_universal_principle_reproduced_2026-06-08.md

---

**Exp-Dev:** authorize all 5 hybrid-architecture anchors. H1 (cascade native-first) is
HIGHEST PRIORITY — Tier 1 production architecture per drill; cycle 180 PP-107 cleanup
confidence AUC=1.0 provides the perfect cascade threshold signal. Total ~10-12 hr CPU
across all 5. Validates v1.5 hybrid production architecture empirically.
