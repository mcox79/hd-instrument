# exp_dev hand-off -- research: LoRA retrieval degradation 3x deep

## Filed-by
research sub-agent, 2026-06-06

## Trigger
Research note: d:/AI/hd-instrument/notes/research_drill_LoRA_retrieval_degradation_3x_deep_2026-06-06.md
Trigger event: Q4 HARD_FAIL (-28.9% top-5-RP after CELL-5 LoRA merge). Level-3 user-requested
drill on BIG negative finding.

## Pause state block
Check d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatching. If present, queue
the anchor candidates below but do NOT dispatch. If absent, dispatch per queue routing.

## Per [[feedback-no-experiment-design-in-prompts]]
This hand-off provides TASK + WHY + CONTRACT + AUTONOMY only. exp_dev decides anchor names, sweep
grids, threshold formulas, HF/HP numerical bounds, queue choice, and ETA autonomously.

---

## Anchor candidates (rank-ordered)

### Anchor 1: Layer-depth RP probe post-CELL-5 (PRIORITY -- cheap, resolves mechanism)
Why-now: The 3x drill identifies layer-depth specificity as the key discriminator between
Hypothesis A (SFT decoder-semantics drift, upper-layer dominant) and Hypothesis C (LoRA rank
perturbation, uniform across layers). A single probe cell measuring top-5-RP at L=2, 6, 10, 15
for both base and CELL-5 merged costs ~3 minutes on remote runner and resolves this cleanly.

Substrate-product reading: if degradation is top-heavy (L=15 >> L=6), confirms the production
extraction layer choice (L=15 for base, consider fallback to L=10 for adapted models).

Tier hint: cheap smoke / diagnostic. CPU-eligible if model fits; GPU if not.

Anchor pointer: see Section 9 (Cheap decisive test) of research note.

---

### Anchor 2: Q-CELL-3-1 feature-mimic validation (CRITICAL PATH)
Why-now: CELL-3 feature-mimic is the Tier-1 rescue path with P_deflated = 0.55. Q-CELL-3-1
was already in plan before this drill. The 3x drill CONFIRMS the design is correct (MSE on
teacher L=15, BASE teacher, Wikipedia training data). If Q-CELL-3-1 is not yet dispatched,
it should be Anchor 2 priority.

Substrate-product reading: if top-5-RP >= 0.330, the 22M student compression path is viable
for production and the 1B base encoder can be replaced at inference time (45x compute reduction).

Tier hint: GPU run, moderate cost. Remote runner.

Anchor pointer: see Section 6 (CELL-3 production recommendation) and Section 7 Tier 1 fallback
in research note.

---

### Anchor 3: MLP-only LoRA SFT test (rescue path verification)
Why-now: Hypothesis D (attention-only LoRA specifically damages retrieval routing) has
P_deflated = 0.41. The rescue is to apply LoRA to FFN layers only (up_proj, gate_proj, down_proj)
while freezing all attention. If this preserves top-5-RP > 0.320, it opens a path to adapting
the retrieval encoder for instruction-following WITHOUT destroying retrieval geometry.

Substrate-product reading: if confirmed, enables future cascade distillation anchors that combine
instruction-following capability with preserved retrieval. This would close the gap between
CELL-5 capability gain (FD ratio 3.91 -- good) and Q4 retrieval loss (bad).

Tier hint: GPU run (same scale as CELL-5). Remote runner.

Anchor pointer: see Section 4 Rank-4 rescue path and Hypothesis D in research note.

---

### Anchor 4: Rank sweep r={4, 8} on SFT (Hypothesis C elimination)
Why-now: Hypothesis C (rank-r perturbation disrupts retrieval subspace) has P_deflated = 0.32.
If r=4 also gives top-5-RP < 0.280, Hypothesis C is eliminated and Hypothesis A is confirmed
as the dominant mechanism. This is cheap (1-2 run cells, same pipeline as CELL-5).

Substrate-product reading: if r=4 preserves RP > 0.310, lower-rank LoRA is a viable PEFT
approach for future distillation with less retrieval damage.

Tier hint: CPU or light GPU. Cheap.

Anchor pointer: see Section 4 Rank-5 rescue path and Hypothesis C falsifiable prediction in
research note.

---

## Context pointers

Primary research note:
  d:/AI/hd-instrument/notes/research_drill_LoRA_retrieval_degradation_3x_deep_2026-06-06.md

Prior Q4 result context (cycle 145):
  d:/AI/hd-instrument/data/exp_CELL-5/metrics.json (CELL-5 LoRA verdict)

CELL-3 feature-mimic plan:
  d:/AI/hd-instrument/notes/ (search exp_dev_handoff or Q-CELL-3 routing files)

Cap map:
  d:/AI/hd-instrument/data/cap_map.md (or most recent version)

---

## Contract section

exp_dev is authorized to:
- Design and queue Anchor 1 (layer-depth probe) immediately if runner capacity available
- Design and queue Anchor 2 (Q-CELL-3-1) if not already dispatched
- Design and queue Anchors 3 and 4 if queue depth allows
- Propose deprioritization of Anchors 3-4 if queue is at capacity; surface to orchestrator

exp_dev is NOT authorized to:
- Commit cap_map changes (strategy agent owns this)
- Design anchors beyond the 4 candidates above without orchestrator routing
- Interpret verdict results (verdict_handler owns this)

## Autonomy declaration

exp_dev decides: anchor naming, exact sweep parameters, pre-reg threshold values, queue
assignment (overnight_queue vs remote_cpu_queue), ETA estimates, and smoke vs full run mode.
The research note provides WHY and mechanism analysis; all implementation decisions are exp_dev's.
