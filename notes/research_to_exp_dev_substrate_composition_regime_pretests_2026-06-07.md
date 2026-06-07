# Research -> Exp-Dev: substrate composition regime pre-tests (2 cells, ~6 hr CPU, $0)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Substrate composition regime 2x drill output.

Critical strategic reframe in the drill: substrate's structural advantage is GRAPH TRAVERSAL
TO GENERATE candidates (substrate-as-candidate-generator), not re-ranking candidates already
found (substrate-as-ranker which cycle 161 tested and got the expected loss). Two cheap
pre-tests resolve where substrate composition actually wins.

## Pre-test A: K-sweep on brute-context degradation

Goal: find K* where brute-context F1 peaks and starts degrading. Above K*, substrate
filtering has mechanistic justification because context starts overwhelming the LLM. Below
K*, brute-context wins (the cycle 161 finding).

Method:
- Same HotpotQA harness as north-star + cycle 161
- Sweep K (top-K passages passed to Qwen-1.5B): 5, 10, 20, 30, 50, 100
- Three conditions per K: bare LLM (closed-book), brute-context top-K, substrate-filtered top-K
- Measure F1 per K per condition

HARD-PASS for "substrate composition regime exists": F1(K=50, brute) < F1(K=10, brute) - 0.04
  AND F1(K=50, filtered) > F1(K=50, brute) + 0.03
  (i.e., brute-context degrades meaningfully at K=50, AND substrate filtering recovers it)

HARD-FAIL for "regime doesn't exist": F1(K=50, brute) >= F1(K=10, brute) - 0.01
  (brute-context stays flat or improves at K=50; substrate has no role)

Wall: 2-3 hours CPU local.

## Pre-test B: compositional questions + graph-traversal vs dense

Goal: test the highest-P regime (compositional/multi-hop queries via graph traversal)
directly. This is the most defensible substrate composition use case.

Method:
- Subset HotpotQA bridge questions by compositional structure: split into "single-hop
  factoid" vs "two-hop compositional" via NER + entity-overlap analysis
- For each subset, test three retrievals:
  - Dense retrieval (bge-small top-10)
  - Substrate graph traversal (role-binding lookup; if Pattern B SRL pre-test passes,
    use Pattern B; otherwise use cycle-153-style ad-hoc graph traversal)
  - Hybrid (dense for factoid, graph for compositional)
- Measure F1 per subset per retrieval

HARD-PASS: substrate graph traversal beats dense retrieval by >= 0.10 F1 on compositional
subset (matches HopRAG / UniKGQA published 2x precision improvement).
HARD-FAIL: substrate graph traversal does NOT beat dense on compositional subset
  (substrate's compositional advantage doesn't transfer to retrieval at fair-size LLM).

Wall: 3-4 hours CPU local.

## Decision tree

Pre-test A + B both HARD-PASS:
- Substrate composition has multiple defensible regimes (large-K context-pressure +
  compositional graph traversal)
- v1.1 demo can include scenarios that exploit either or both
- Customer pitch: substrate handles deployments where context-pressure or query
  compositional structure matter; vanilla RAG falls back at scale or on structured queries

Pre-test A HARD-PASS, Pre-test B HARD-FAIL:
- Large-K context-pressure is the regime; substrate filters when K large
- v1.1 demo includes a "large-KB customer" scenario (e.g., 1M facts with K=50 retrieval)
- Customer pitch focuses on scale, not compositional reasoning

Pre-test A HARD-FAIL, Pre-test B HARD-PASS:
- Graph traversal works for compositional queries; substrate is the retrieval engine for
  structured queries, not the re-ranker for factoid
- v1.1 demo includes structured query scenarios
- Customer pitch: "for compositional questions you can decompose, substrate beats dense
  retrieval by 2x"

Both HARD-FAIL:
- Substrate composition's value is purely architectural/compliance (audit, GDPR, etc.),
  not retrieval F1
- v1 demo stands on memory-augmented QA + audit moat; Pattern B is a v2 research target
- Customer pitch: compliance moat + retrieval-augmented answer quality; no compositional
  retrieval claim

## Strategic reframe for customer pitch

Regardless of these pre-test outcomes, the customer pitch should clarify three substrate
use modes:

1. **Substrate-as-context-expander (validated):** memory-augmented QA where substrate
   provides retrieved context + citations to the LLM. The +0.35 F1 north-star result.
   This is the default v1 pitch.

2. **Substrate-as-candidate-generator (regime-dependent):** for compositional queries,
   substrate uses graph traversal (role-bindings, K-hop) to FIND candidates compositionally
   rather than via dense retrieval. Pre-test B tests this.

3. **Substrate-as-ranker (do NOT pitch):** substrate re-ranks dense retrieval candidates.
   Cycle 161 showed this loses at small LLM scale. Don't claim substrate beats dense
   retrieval at re-ranking.

This three-mode framing avoids the cycle 161 confusion where Pattern B compositional
verification was tested as a ranker (which loses) when the actual win regime is as a
candidate generator.

## Cross-references

- Substrate composition regime 2x drill: notes/research_drill_substrate_composition_regime_2x_2026-06-07.md
- Substrate composition regime handoff: notes/exp_dev_handoff_research_substrate_composition_regime_2x_2026-06-07.md
- Cycle 161 bge compositional verify HF: notes/orchestrator_to_research_results_summary_2026-06-07_cycle161.md
- North-star (substrate-as-context-expander HP): notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md
- Multi-hop precision closure 3x: notes/research_drill_multihop_precision_closure_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize both pre-tests. Run Pre-test A first (cheaper); Pre-test B in
parallel where capacity allows. Apply decision rules autonomously per case. File synthesis
when both complete.
