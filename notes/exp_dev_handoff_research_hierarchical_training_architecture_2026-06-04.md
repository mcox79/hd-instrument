# exp_dev hand-off -- research: hierarchical training architecture 2x drill

**Filed-by:** research sub-agent
**Trigger:** d:/AI/hd-instrument/notes/research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md
**Date:** 2026-06-04

**Pause state block:** Check data/orchestrator_paused.flag before dispatching. If paused, hold.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY only. exp_dev resolves anchor names, sweep grids, pre-reg thresholds, queue routing, and ETA independently.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY)
**Pointer:** Substrate distillation write from N concurrent domains -- retrieval accuracy + deletion-cert validation
**Substrate-product reading:** Sub-question (4) identified that substrate can store domain-tagged knowledge from N sub-LLMs via Hebbian writes with algebraic deletion-cert. This is the core of the hierarchical architecture's unique capability. No published system combines distillation + deletion-cert + incremental write.
**Tier hint:** Tier 1-2 (CPU smoke first; no GPU needed at N_substrate=8192, N_domains=10-50)
**Why-now:** The cheap decisive test from the research note is directly testable at small scale with zero GPU cost. If this passes HP1+HP2, it anchors the entire hierarchical narrative. If it fails HF1 or HF2, the narrative needs rescoping before further investment.

Hard-pass: retrieval accuracy >= 80% at N_domains=50, K_d=100, N_substrate=8192; deletion delta < 1% for all other domains.
Hard-fail: accuracy < 50% at N_domains=20; deletion degrades any domain > 5%.

### Anchor 2
**Pointer:** Wall-time speedup from N concurrent independent training jobs (coordination overhead measurement)
**Substrate-product reading:** Sub-question (2) predicts ~80-95x wall-time speedup at N=100 fully-independent models. The algebraic argument is clean but the practical straggler + scheduler overhead has not been measured at this specific configuration.
**Tier hint:** Tier 2 (local CPU/GPU; simulate N=10, 50, 100 parallel jobs via subprocess; measure actual wall-time vs theoretical)
**Why-now:** The wall-time claim is central to the flagship narrative. A measured straggler curve at N=10,50,100 gives confidence before committing to cloud experiments.

### Anchor 3
**Pointer:** Incremental domain addition (no forgetting below capacity threshold)
**Substrate-product reading:** Sub-question (5) predicts zero forgetting for new domain writes below capacity cliff. This is the continual learning advantage. If confirmed, it directly differentiates from LoRA/full-fine-tune.
**Tier hint:** Tier 1 (CPU; pure algebraic test; N_substrate=8192, grow N_domains from 1 to 200; track retrieval accuracy per domain)
**Why-now:** Tests the capacity cliff shape directly; informs where N_substrate must be set for production deployment.

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md
- Prior training-speedup routing: d:/AI/hd-instrument/notes/research_routing_tier4_training_speedup_small_scale_battery_2026-06-02.md
- Cap_map (deletion-cert rows PP-45/46): d:/AI/hd-instrument/data/cap_map.md
- Phase 0.5 distillation spec: d:/AI/hd-instrument/notes/research_routing_v359_phase05b_distillation_mvp_full_spec_2026-06-03.md

---

## Contract

exp_dev owns: anchor naming, sweep grid design, pre-reg threshold values, queue assignment, timeout formula, smoke/full sequencing.
Research note owns: algebraic prediction, hard-pass/hard-fail bands, lit citations, P_deflated values.
Orchestrator owns: cap_map updates post-verdict.

## Autonomy declaration

exp_dev has full autonomy to design the anchors from the algebraic predictions above. Do NOT copy numerical thresholds verbatim from this file into the experiment scripts -- re-derive from the formula (or use as a starting point and justify any deviation). Self-test formulas per [[feedback-strategy-spec-formula-selftests]] before coding.
