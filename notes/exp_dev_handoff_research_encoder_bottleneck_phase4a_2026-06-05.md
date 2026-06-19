# exp_dev hand-off -- research: encoder bottleneck phase 4a infrastructure

**Filed-by:** research sub-agent (Sonnet), 2026-06-05
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_encoder_bottleneck_phase4a_infrastructure_2x_2026-06-05.md
**Per [[feedback-no-experiment-design-in-prompts]]:** This file names anchor candidates and context pointers only. Exp_dev owns all design decisions (sweep grids, threshold formulas, queue choice, pre-reg bands).

---

## Pause state

Check data/orchestrator_paused.flag before dispatch. If flag present, hold.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TIER-1, CPU, ~20 min): MiniLM VQ fidelity baseline

**Anchor pointer:** cheap-decisive-test from research note Sub-Q1
**Substrate-product reading:** Determines immediately whether the existing off-the-shelf 22M encoder (all-MiniLM-L6-v2) meets V_c=100k substrate fidelity threshold without any training. If HARD-PASS: unblocks 8+ substrate architecture experiments at zero incremental cost. If HARD-FAIL: confirms distillation is required, sizes the gap.
**Tier hint:** CPU laptop smoke, <60s scoping level
**Why now:** Zero-cost gate that determines whether Phase 4a-1 distillation investment is necessary. Blocks no GPU resources.

### Anchor 2 (TIER-2, CPU, ~2h): Mini-batch k-means codebook construction at V_c = 10k/100k

**Anchor pointer:** Build VQ codebook from Wikipedia sentence embeddings via MiniLM
**Substrate-product reading:** Concrete artifact (codebook .npy file + assignment accuracy metric) that becomes the substrate input layer. Validates the two-step pipeline: encoder -> VQ -> substrate.
**Tier hint:** Remote CPU (not GPU); pure numpy/sklearn
**Why now:** Needed before any substrate architecture experiment can use VQ concept-IDs. Prerequisite for working memory loop and CoT cache experiments.

### Anchor 3 (TIER-3, GPU, ~2-3h, ~$10-15): Distilled encoder training

**Anchor pointer:** 6-layer 768-dim student distilled from Llama-1B layer-10 activations
**Substrate-product reading:** Produces the production-quality encoder supporting V_c up to 500k. Quality gate: Spearman rho >= 0.84, geometry RMSE < 0.05. Closes the V_c gap identified in research note.
**Tier hint:** GPU (A100); ONLY if Anchor 1 shows HARD-FAIL or V_c=1M is required
**Why now:** Conditional on Anchor 1 result; do not dispatch until Anchor 1 verdict is in hand.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_encoder_bottleneck_phase4a_infrastructure_2x_2026-06-05.md
- Cap map (cross-modal binding PP-23 row, audit vector store row): d:/AI/hd-instrument/notes/substrate_capability_map.md
- Phase 3 production blueprint (Gemma-2-2B encoder): reference in task context (not a local file path)

---

## Contract

Exp_dev designs all experiments, writes all scripts, files all pre-reg bands, dispatches via queue_add.sh, and verifies post-ship queue presence. Orchestrator does not design experiments in this handoff.

## Autonomy declaration

Exp_dev has full autonomy over: anchor naming, sweep parameters, threshold formulas, queue assignment (CPU vs GPU), ETA estimates, and pre-reg HARD-PASS/HARD-FAIL numerical bounds. The research note provides the WHAT and WHY; exp_dev owns all HOW decisions.
