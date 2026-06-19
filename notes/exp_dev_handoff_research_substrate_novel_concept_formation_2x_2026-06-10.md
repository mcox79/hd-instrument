# exp_dev hand-off -- research: substrate novel concept formation

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_novel_concept_formation_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered, cheapest decisive first)

### 1. anomaly_driven_explore_v1 (TIER 1 -- cheapest, diagnostic, ~1 min CPU)
- Substrate-product reading: validates cleanup margin as a real-valued anomaly signal distinguishing novel inputs from familiar ones. If HARD-PASS (AUROC >= 0.80), this directly enables a product feature: "the substrate tells you what it doesn't know." Also confirms the trigger mechanism for the discovery loop.
- Tier hint: CPU smoke; < 1 min wall; DIAGNOSTIC (prerequisite for all discovery-loop anchors)
- Why now: cheapest test; required to confirm the exploration trigger before building the full discovery loop; cleanup margin is used implicitly in every experiment but never tested as an explicit anomaly detector

### 2. combinatorial_primitive_concept_blend_v1 (TIER 1 -- ~5 min CPU)
- Substrate-product reading: validates FHRR binding as concept creation -- a blended concept retrieved at >= 85% accuracy on queries referencing both source schemas, but NOT on queries referencing only one. If HARD-PASS, adds "cross-domain concept blending" to the cap_map as a new capability class.
- Tier hint: CPU smoke; ~5 min wall; Tier-1 (new capability class opener if PASS)
- Why now: algebraically straightforward extension of confirmed KV injection and K-hop; binding two schema vectors is mechanistically identical to a K=2 relational hop; low implementation risk; highest P_deflated (0.40) of all discovery anchors

### 3. hierarchical_schema_v1 (TIER 1 -- ~10 min CPU)
- Substrate-product reading: validates two-pass schema extraction to find Tier-1 universals across domains. If HARD-PASS (pass-2 output cosine > 0.70 to universal structure), opens the "self-organizing knowledge base" product narrative where the substrate discovers its own concept vocabulary from streaming data.
- Tier hint: CPU; ~10 min wall; Tier-1 (new capability, extends confirmed single-pass PP-282/284)
- Why now: direct algebraic extension of confirmed schema extraction (one additional majority-vote operation); needed before DISCOVERY-LOOP can be validated; determines whether two-level hierarchy is stable

### 4. discovery_loop_active_schema_v1 (TIER 2 -- ~30 min CPU)
- Substrate-product reading: validates the full active-inference + schema-extraction + anomaly-check loop as a coherent discovery engine. If HARD-PASS (>= 3 coherent novel concepts per 10 queries), the substrate can claim "generates novel hypotheses from KB anomalies" -- a capability no pure retrieval system has.
- Tier hint: CPU; ~20-40 min wall; Tier-2 (integration of 3 confirmed primitives; main uncertainty is whether integration noise degrades loop coherence)
- Why now: depends on anchors 2 and 3 passing first (combinatorial blend + hierarchical schema); ship after those are confirmed

### 5. codebook_expand_cleanup_residual_v1 (TIER 2 -- ~20 min CPU)
- Substrate-product reading: validates online codebook expansion from anomalous inputs. If HARD-PASS (+20% retrieval improvement after expansion, < 5% prior interference), enables truly open-ended concept formation -- the substrate grows its own vocabulary from novel inputs. This is the only anchor that enables GENUINELY new atomic concepts (not just novel compositions of existing atoms).
- Tier hint: CPU; ~20 min wall; Tier-2 (novel mechanism; no prior validation; highest risk)
- Why now: lowest P_deflated (0.28) but closes the Level 6 honest limitation about fixed codebook; if PASS, substantially upgrades the discovery narrative

---

## Honest gap note (for orchestrator context)

Research finding establishes that substrate has a genuine gap vs LLMs on:
- Free-form combinatorial brainstorming fluency (LLM advantage is LARGE)
- Aesthetic / interestingness judgment (substrate has no training signal for this)
- Mathematical pattern induction (T5 type) -- substrate level-code encoding of numerics has not been tested

The above anchors address the tractable gaps. The honest expectation is:
- ANOMALY-DRIVEN-EXPLORE: likely PASS (cleanup margin is well-calibrated from first principles)
- COMBINATORIAL-PRIMITIVE-BLEND: likely PASS (algebraically isomorphic to confirmed K=2 hop)
- HIERARCHICAL-SCHEMA: uncertain (P=0.35; depends on second-pass stability)
- DISCOVERY-LOOP: uncertain (P=0.32; depends on integration coherence)
- CODEBOOK-EXPANSION: most uncertain (P=0.28; novel mechanism)

Do NOT dispatch the creative writing or open-ended brainstorming test batteries (T2, mathematical T5) until the structured anchors (1-3) confirm the primitive mechanisms are working. LLM comparison should come AFTER substrate primitives are validated individually.

---

## Context Pointers

- Research note: notes/research_drill_substrate_novel_concept_formation_2x_2026-06-10.md
- Active inference empirical: data/exp_pp272_*/metrics.json (PP-272 confirmed)
- Schema extraction empirical: data/exp_pp282_*/metrics.json, data/exp_pp284_*/metrics.json (confirmed)
- K-hop empirical: data/exp_khop_*/metrics.json (K=10, N=16384, V_c=1024, 100% accuracy)
- Multi-context paraconsistent: data/exp_pp280_*/metrics.json (PP-280 confirmed)
- Compositional cliff crossing: notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md (L5 recall 0.000->1.000)
- Prior reasoning anchor: notes/exp_dev_handoff_research_substrate_native_reasoning_2026-06-06.md

---

## Contract

exp_dev's job: design anchors, set pre-reg thresholds, ship to queue, verify post-ship.
Orchestrator's job: decide which anchors to activate and when.
This file is a ranked option list -- not a dispatch order.

## Autonomy Declaration

exp_dev owns: anchor naming, sweep grid design, threshold formula self-test, queue selection, ETA estimation, smoke vs full run decision.
exp_dev does NOT own: cap_map write decisions, strategy pivots, or composition ordering between these anchors.
