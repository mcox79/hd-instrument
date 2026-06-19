# exp_dev hand-off -- research: embodied AI boundary probe (2x)

**Filed:** 2026-06-10 by research sub-agent.
**Trigger:** Research drill completed for embodied AI boundary probe (2x depth).
Research note: `notes/research_drill_embodied_AI_boundary_probe_2x_2026-06-10.md`

**Pause state:** check `data/orchestrator_paused.flag` before dispatching any GPU/CPU anchors.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Summary of research findings

The drill found that the substrate can implement the full Lakoff/Johnson image-schema and conceptual-metaphor stack as explicit codebook primitives using existing bind/unbind/superpose operators. The v3.0 compositional milestone (L5 recall 1.000) directly enables 3-level composition required for schema + metaphor + abstract-concept encoding. Five laptop-CPU-testable experiment anchors are ready.

Key finding: the hard boundary is physical actuation, not representation. Every embodied AI property this side of physical robotics is an engineering challenge, not a principled impossibility. P_deflated (simulated embodiment sufficient for grounded abstract reasoning) = 0.65.

---

## Anchor candidates (rank-ordered)

### 1. IMG-SCHEMA-A1 -- Image schema codebook retrieval
- **Anchor pointer:** `notes/research_drill_embodied_AI_boundary_probe_2x_2026-06-10.md` Section 8 "IMG-SCHEMA-A1"
- **Substrate-product reading:** Gate test for the entire embodied AI stack. If 30 schemas at N=1024 maintain separability and retrieval accuracy > 0.85 with 200 bound items, the schema-as-primitive approach is viable for downstream metaphor and affordance work. Pre-reg HARD-PASS: > 0.85; HARD-FAIL: < 0.50.
- **Tier hint:** local_cpu_queue (pure numpy/torch, no training, < 5 min run time)
- **Why now:** Cheapest test in the stack; gates everything downstream. Does not require any new substrate infrastructure -- only a codebook design script on top of existing bind/unbind/recall.

### 2. AFFORDANCE-A2 -- Object-action pair generalization
- **Anchor pointer:** `notes/research_drill_embodied_AI_boundary_probe_2x_2026-06-10.md` Section 8 "AFFORDANCE-A2"
- **Substrate-product reading:** Establishes whether the substrate can generalize affordance knowledge to novel objects via shared property shards. Empirical baseline from PMC affordance embeddings (2022): 84.71% at 200-dim skip-gram. The substrate at N=1024 with explicit role-filler should match or exceed this baseline. Pre-reg HARD-PASS: > 0.80; HARD-FAIL: < 0.50.
- **Tier hint:** local_cpu_queue (50 object-action pairs, pure encoding + retrieval)
- **Why now:** Second-cheapest test; directly relevant to product claim about affordance-sensitive retrieval.

### 3. GROUNDED-ABSTRACT-A4 -- Body-schema co-activation on abstract retrieval
- **Anchor pointer:** `notes/research_drill_embodied_AI_boundary_probe_2x_2026-06-10.md` Section 8 "GROUNDED-ABSTRACT-A4"
- **Substrate-product reading:** The decisive test for the core embodied AI claim. If abstract concept queries co-activate the correct body-schema shards, the grounding is structural and interpretable. This is the test that separates the substrate's explicit-schema approach from implicit LLM embedding approaches. Pre-reg HARD-PASS: > 0.70 of 50 abstract concepts show correct schema shard activation; HARD-FAIL: < 0.40.
- **Tier hint:** local_cpu_queue (50 abstract concepts + schema codebook, pure retrieval)
- **Why now:** Central product claim. If this passes, the "interpretable grounded reasoning" product angle is empirically supported.

### 4. METAPHOR-EXTENSION-A3 -- Novel metaphor recognition via schema generalization
- **Anchor pointer:** `notes/research_drill_embodied_AI_boundary_probe_2x_2026-06-10.md` Section 8 "METAPHOR-EXTENSION-A3"
- **Substrate-product reading:** Tests whether the substrate can generalize beyond encoded metaphors to novel expressions, using schema-geometry rather than memorization. Control condition (bag-of-words) required. Pre-reg HARD-PASS: > 0.75 correct schema cluster assignment AND > 0.10 gap over control; HARD-FAIL: < 0.50 OR gap <= 0.0.
- **Tier hint:** local_cpu_queue (30 canonical metaphors + 20 novel expressions as test set)
- **Why now:** Depends on A1 passing (schema codebook established). Queue after A1 result is in.

### 5. SENSORIMOTOR-LOOP-A5 -- Simulated active inference loop
- **Anchor pointer:** `notes/research_drill_embodied_AI_boundary_probe_2x_2026-06-10.md` Section 8 "SENSORIMOTOR-LOOP-A5"
- **Substrate-product reading:** Tests whether the substrate can close a prediction-error-minimization loop in a simulated environment (10x10 grid, 5 object types). This is the PP-272 active inference mechanism implemented end-to-end. Pre-reg HARD-PASS: goal-reach > 2x random baseline AND mean prediction error decreasing across 10 episodes; HARD-FAIL: goal-reach <= random baseline.
- **Tier hint:** remote_cpu_queue or local_cpu_queue (100 steps x 10 episodes; thin simulation wrapper ~100 lines)
- **Why now:** Requires grid-world simulation wrapper (not in current codebase). Queued after A1+A2+A4 confirm the codebook layer. Most complex of the 5 anchors.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_embodied_AI_boundary_probe_2x_2026-06-10.md`
- v3.0 compositional cliff crossed: `C:\Users\marsh\.claude\projects\d--AI\memory\substrate_v3_compositional_cliff_crossed.md`
- PP-257 multi-modal binding design: search `notes/` for PP-257 reference
- PP-272 active inference design: search `notes/` for PP-272 reference
- Existing bind/unbind/recall implementation: `hdlab/` substrate core

---

## Contract

exp_dev takes these anchors and decides: queue routing, N, M, thresholds, smoke gate design, full profile design, dispatch order. Research does not constrain any of those decisions.

If IMG-SCHEMA-A1 HARD-FAILs (cross-schema cosine > 0.15 or retrieval < 0.50): research should be re-engaged to investigate whether N needs to be higher, whether the role-filler decomposition is the right approach, or whether an alternative schema encoding strategy is needed before proceeding to A2-A5.

## Autonomy declaration

exp_dev is fully autonomous on all dispatch decisions for these anchors within the authorized queue envelope. No additional orchestrator approval required for local_cpu_queue or remote_cpu_queue Tier B/C items. GPU (Tier A) items require pause-state check before dispatch.
