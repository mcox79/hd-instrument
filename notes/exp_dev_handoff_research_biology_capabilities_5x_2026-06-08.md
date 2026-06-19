# exp_dev hand-off -- research: biology of substrate capabilities 5x

**Filed by**: research sub-agent
**Date**: 2026-06-08
**Trigger**: notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md (research delivery)
**Per [[feedback-no-experiment-design-in-prompts]]**: exp_dev designs all anchors with pre-reg per envelope-fail-bands. No inline experiment design in this file.

---

## Pause state block

Pause gate: check data/orchestrator_paused.flag before dispatch. If PAUSED, hold all queue-triggering actions.

---

## Anchor candidates (rank-ordered)

### Anchor A: Contradiction-detection layer (ACC analog)
- Anchor pointer: bio-contradiction-detect-A1
- Substrate-product reading: when top-k retrieval returns two KB items with high confidence (both > 0.80) and their bound facts are semantically contradictory, return a conflict_flag=True marker alongside both results rather than silently returning only top-1. Maps to anterior cingulate cortex (ACC) conflict monitoring (Botvinick et al. 2001) which fires on high-response-conflict before error is committed. Addresses LLM hallucination scenario where substrate KB contains contradictory facts from different sources.
- Tier hint: Tier 1 (uses only existing top-k similarity computation; no new operators; 1 week scope)
- Why now: cheapest, highest product value, directly addresses hallucination detection. No pretest required -- uses existing retrieval pipeline.
- Pre-reg bands: HARD-PASS = contradiction correctly flagged on >80% of 50 synthetic contradiction pairs (known-opposite facts injected); HARD-FAIL = contradiction flag rate < 50% OR false-positive rate > 30% on non-contradictory pairs

### Anchor B: Calibrated confidence intervals (probabilistic population code)
- Anchor pointer: bio-calibrated-confidence-B1
- Substrate-product reading: add gap score (top-1 similarity minus top-2 similarity) as a second output alongside the existing confidence score. Large gap = high confidence + low uncertainty. Small gap = low confidence + high uncertainty. Maps to neural uncertainty representation via width of the posterior in population coding (Ma et al. 2006). Report as (confidence, uncertainty_gap) tuple. Evaluate calibration via Brier score on a labeled held-out KB subset.
- Tier hint: Tier 1 (changes only the output format; no retrieval mechanism change; < 1 week)
- Why now: cheap. Useful for downstream reasoning. Directly fills the probabilistic population code gap identified in Domain 2 of the research note.
- Pre-reg bands: HARD-PASS = Brier score < 0.15 on 200-item labeled test set; correlation between uncertainty_gap and retrieval error rate > 0.60; HARD-FAIL = Brier score > 0.30 OR uncertainty_gap has no correlation (< 0.20) with actual error rate

### Anchor C: Graded confidence test (cheap decisive test for Anchors A and B)
- Anchor pointer: bio-graded-confidence-pretest-C0
- Substrate-product reading: inject a 200-item KB with 5 known similarity tiers (0.60, 0.70, 0.80, 0.90, 1.00 cosine vs query). Query each with noise sigma=0.05, 0.10, 0.20. Measure whether PP-107 confidence scores are monotonically ordered across tiers (Spearman rho > 0.85) and whether scores remain graded (not collapsed to binary) at sigma=0.10. This is the pretest that validates whether substrate's existing confidence mechanism is already a probabilistic population code analog.
- Tier hint: Tier 0 (diagnostic pretest; $0, 1 hour CPU)
- Why now: gates Anchors A and B. If confidence is already graded, Anchor B is mostly an output formatting change. If confidence collapses to binary, the mechanism needs a fix before Anchors A and B are meaningful.
- Pre-reg bands: PASS = Spearman rho > 0.85 AND graded response persists to sigma=0.10; FAIL = rho < 0.60 OR binary collapse at sigma=0.10

### Anchor D: Re-encoding retry on low confidence (insight / re-framing)
- Anchor pointer: bio-reencoding-retry-D1
- Substrate-product reading: when retrieval confidence < 0.60, abstract the query (remove named entities, retain structural relation terms) and retry. Measures whether abstracted re-query recovers items that exact-match missed. Maps to right anterior temporal gyrus insight mechanism (Jung-Beeman et al. 2004) where stuck problems are re-framed holistically. Test on a KB where some items are stored under abstract descriptions but queried with specific concrete terms.
- Tier hint: Tier 2 (requires LLM call for query abstraction; 1-2 week scope)
- Why now: medium priority. Useful for robustness. Defer until Anchors A-C are complete.
- Pre-reg bands: HARD-PASS = re-encoded query recovers > 25% of items missed by direct query on 100-item low-confidence test set; HARD-FAIL = recovery < 5% (abstraction step adds noise without benefit)

### Anchor E: Hierarchical K-hop (PFC rostral-caudal gradient analog)
- Anchor pointer: bio-hierarchical-khop-E1
- Substrate-product reading: two-level KB structure. Level-1: abstract plan nodes (e.g. goal-type clusters). Level-2: concrete fact nodes attached to Level-1 anchors. K-hop at Level-1 retrieves goal-relevant clusters; a second K-hop within each cluster retrieves specific facts. Maps to prefrontal cortex rostral-caudal hierarchy (Koechlin + Summerfield 2007) where abstract goals (rostral BA10) decompose to concrete actions (caudal premotor). Test: given a high-level query, does two-level K-hop outperform flat K-hop on a KB with known hierarchical structure (e.g. a topic-organized KB with 20 topics and 50 facts per topic)?
- Tier hint: Tier 2 (requires KB schema extension for level tagging; 2-3 week scope)
- Why now: deferred until Anchors A-D establish baseline. Needed for complex planning tasks.
- Pre-reg bands: HARD-PASS = two-level K-hop precision@1 > 0.85 on 100-query hierarchical test set, exceeding flat K-hop baseline by > 0.10; HARD-FAIL = two-level K-hop <= flat K-hop (hierarchy adds no benefit)

---

## Cheap decisive test (run FIRST before Anchors A-B)

Anchor C above IS the cheap decisive test. Run it first ($0, 1 hour CPU). Outcome gates the interpretation of Anchors A and B.

Recommended dispatch order:
1. Anchor C (pretest, $0, 1 hour) -- gates all others
2. Anchor A (contradiction detection, 1 week) -- does not depend on Anchor C mechanically, but Anchor C tells you whether the confidence layer under it is graded
3. Anchor B (calibrated confidence intervals, < 1 week) -- run in parallel with Anchor A
4. Anchor D and E -- defer until A-C complete

---

## Context pointers

- Primary research note: d:/AI/hd-instrument/notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md
- Prior math drill: d:/AI/hd-instrument/notes/research_drill_substrate_math_capabilities_5x_2026-06-08.md
- Prior handoff (math): d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_math_capabilities_5x_2026-06-08.md
- LLM capability separation: d:/AI/hd-instrument/notes/research_drill_llm_capability_separation_substrate_5x_2026-06-08.md
- PP-107 confidence mechanism: referenced in cap_map
- PP-172 do() operator: validated in cap_map (counterfactual do() validated)
- Multi-hop revival: d:/AI/hd-instrument/memory/project_multihop_revive_priority.md
- Production architecture: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Key biology references: Botvinick et al. 2001 (ACC conflict), Ma et al. 2006 (population codes), Stachenfeld et al. 2017 (hippocampal predictive map), Olshausen + Field 2004 (sparse coding)

---

## Contract

exp_dev designs all anchors with pre-reg per envelope-fail-bands. No inline experiment design is encoded here per [[feedback-no-experiment-design-in-prompts]]. All anchors are CPU-eligible at the pretest scale. Anchor E may require GPU for large-scale KB testing. Dispatch via queue_add.sh with appropriate queue routing per [[feedback-route-gpu-vs-cpu-by-torch-not-N]].

## Autonomy declaration

exp_dev has full autonomy to: design specific experiment parameters for each anchor, choose KB size and noise levels within pre-reg scope, order sub-anchors, decide smoke vs full run, choose between running Anchors A and B in parallel or sequentially. exp_dev does NOT have autonomy to: skip Anchor C pretest before interpreting confidence-layer results in Anchors A and B, bypass pre-reg bands, treat mid-band as PASS.
