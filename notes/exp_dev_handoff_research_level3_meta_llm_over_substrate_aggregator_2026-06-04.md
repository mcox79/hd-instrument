# exp_dev hand-off -- research: Level 3 meta-LLM over substrate aggregator 2x drill

**Filed-by:** research sub-agent
**Trigger:** d:/AI/hd-instrument/notes/research_drill_level3_meta_llm_over_substrate_aggregator_2x_2026-06-04.md
**Date:** 2026-06-04

**Pause state block:** Check data/orchestrator_paused.flag before dispatching. If paused, hold.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY only. exp_dev resolves anchor names, sweep grids, pre-reg thresholds, queue routing, and ETA independently.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY -- CPU smoke gate)
**Pointer:** 10M-parameter routing head trained on substrate-formatted pairs from existing 5-corpus HP artifact
**Substrate-product reading:** The cheapest empirical test for Level 3 is a routing-only meta-LLM (10M params) trained from scratch on substrate retrieval outputs. If it achieves >= 70% domain routing accuracy on cross-domain queries (chance = 20% for 5-domain selection), the Level 3 architecture is validated for the routing capability and the GPU synthesis phase (Anchor 2) is justified. This anchor directly uses the existing 5-corpus HP artifact (N=8192, N_domains=5, K_d=200, 98.6% retrieval accuracy) -- no new substrate training required.
**Tier hint:** Tier 1 (CPU, ~30 min training wall, ~60 min eval; zero GPU)
**Why-now:** Level 2 hard-passed today. Level 3 is the UNTESTED component. This is the minimal-cost gate before any GPU investment in Level 3.

Hard-pass band (routing accuracy): >= 70% on 1000 cross-domain queries.
Middle-band: 50-70%.
Hard-fail: < 50% (near or below chance for 5-domain selection).

### Anchor 2 (GPU phase -- gated on Anchor 1 HP)
**Pointer:** 1B LoRA fine-tune (r=8) on substrate-formatted cross-domain synthesis pairs; eval vs 2-level retrieval-only baseline
**Substrate-product reading:** The synthesis capability is the defining Level 3 emergent feature -- the ability to generate coherent answers spanning 2+ domains using substrate-retrieved gist as context. If this anchor achieves >= 2x accuracy over the 2-level baseline, it confirms the 3-level hierarchy produces a genuine emergent capability not present at Level 2 alone. This is the key claim in the hierarchical architecture product narrative.
**Tier hint:** Tier 2 (remote GPU, ~4-8 hrs training, ~2 hrs eval; ~1.5 eng-days total including Anchor 1)
**Why-now:** Depends on Anchor 1 HP. If Anchor 1 HF, do not proceed to Anchor 2 -- diagnosis needed before LoRA training budget.

Hard-pass band (synthesis accuracy): >= 2x 2-level retrieval-only baseline on cross-domain synthesis QA.
Middle-band: 1.2x-2x baseline.
Hard-fail: <= 1.2x baseline (meta-LLM adds no capability over raw substrate retrieval).

### Anchor 3 (audit propagation -- CPU, lightweight)
**Pointer:** Deletion-cert propagation to Level 3 output: after Level 2 deletion of one domain, test that meta-LLM cannot answer that domain's queries via substrate channel
**Substrate-product reading:** The end-to-end audit trail (Level 1 -> Level 2 -> Level 3 outputs) is the product differentiator that no MoE or RAG system offers. This anchor tests whether deletion at Level 2 propagates cleanly to Level 3 outputs when using Option A text injection. If HP, this is the flagship audit claim: "Level 3 outputs are auditable end-to-end via substrate deletion-cert."
**Tier hint:** Tier 1 (CPU; uses existing substrate HP artifact; test with non-pretrained facts to isolate substrate channel from LLM parametric memory)
**Why-now:** Can be run in parallel with or immediately after Anchor 1 on the same HP artifact. Low cost, high strategic value.

Hard-pass band: meta-LLM accuracy on deleted-domain queries < 25% via substrate channel after deletion (chance = 20%; should be near chance).
Hard-fail: meta-LLM accuracy on deleted-domain queries > 50% after deletion (cert propagation fails).

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_level3_meta_llm_over_substrate_aggregator_2x_2026-06-04.md
- Prior Level 2 hierarchical training drill: d:/AI/hd-instrument/notes/research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md
- Prior System 1+2 hybrid drill: d:/AI/hd-instrument/notes/research_drill_substrate_system1_hybrid_architecture_2x_2026-06-04.md
- 5-corpus HP artifact (Level 2 validated): check data/exp_*/metrics.json for today's hierarchical aggregator HARD_PASS
- Cap_map rows implicated: Q-B1 (Hebbian write), PP-45/46 (deletion-cert), PP-50 (composition depth)

---

## Contract

exp_dev owns: anchor naming, sweep grid design, pre-reg threshold values, queue assignment, timeout formula, smoke/full sequencing.
Research note owns: algebraic prediction, hard-pass/hard-fail bands, lit citations, P_deflated values.
Orchestrator owns: cap_map updates post-verdict.

## Autonomy declaration

exp_dev has full autonomy to design the anchors from the algebraic predictions above. Do NOT copy numerical thresholds verbatim from this file into experiment scripts -- re-derive from the formula (or use as starting point and justify any deviation). Self-test formulas per [[feedback-strategy-spec-formula-selftests]] before coding. Sequencing: run Anchor 1 (CPU smoke) first; gate Anchor 2 on Anchor 1 HP; Anchor 3 can run in parallel with Anchor 1.
