# exp_dev hand-off -- research: substrate composition regime 2x

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_substrate_composition_regime_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the experiment; this file provides anchor candidates and context pointers only.

---

## Summary of Finding

Substrate compositional filtering (Pattern B) loses to brute-context top-10 at 1.5B scale because K=10 is below the context-pressure crossover. Three regimes with defensible filtering advantage were identified. The most actionable are (1) K-sweep to find the brute-context degradation crossover and (2) compositional query subtype split to test graph-traversal retrieval vs dense retrieval on structured questions.

---

## Anchor Candidates (rank-ordered)

### Anchor 1: K-sweep brute-context degradation test (Regime 1)
- Substrate-product reading: Find K* where brute-context F1 peaks and degrades. Above K*, substrate filtering has mechanistic justification. Below K* (current K=10), brute-context wins.
- Tier hint: CPU local, 2-3 hours, $0
- Why now: Pre-test required per drill-pretest-required rule before engineering authorization. Direct falsification of the crossover claim. Cheap, unambiguous.
- HARD-PASS: F1(K=50, brute) < F1(K=10, brute) - 0.04 AND F1(K=50, filtered) > F1(K=50, brute) + 0.03
- HARD-FAIL: F1(K=50, brute) >= F1(K=10, brute) - 0.01

### Anchor 2: Compositional question subset annotation + graph traversal vs dense (Regime 5)
- Substrate-product reading: If >= 20 questions in the existing benchmark are 2-hop compositional, graph-traversal retrieval should outperform dense retrieval on that subset. This tests whether substrate Pattern B is being used correctly (graph traversal) vs incorrectly (post-retrieval selection).
- Tier hint: CPU local, 3-4 hours, $0
- Why now: This is the highest P_theoretical regime (0.78). Pre-test is subset annotation (check compositional fraction first -- if <15%, abort). If compositional fraction is sufficient, this directly tests the mechanistic alignment claim from the cross-thread synthesis.
- HARD-PASS: F1(graph, compositional) > F1(dense, compositional) + 0.05 AND N_compositional >= 20
- HARD-FAIL: N_compositional < 10 OR F1(graph) <= F1(dense)

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_composition_regime_2x_2026-06-07.md
- Prior cycle verdict: data/exp_bge_compositional_verify/metrics.json (cycle 161 HF)
- North-star context: notes/research_POST_COMPACTION_BRIEF_2026-06-07_morning.md
- Cap_map: data/substrate_capability_map.md

---

## Contract Section

Research has identified regime conditions and pre-test designs. exp_dev owns:
- Exact anchor code design
- Pre-reg bands (informed by HARD-PASS/HARD-FAIL above, not bound by them)
- Smoke gate
- Queue dispatch decision
- Queue routing (CPU local for both anchors above)

## Autonomy Declaration

exp_dev has full autonomy to modify anchor designs, add smoke gates, or defer either anchor based on queue state or engineering judgment. This file is a context-provision hand-off, not a design specification.
