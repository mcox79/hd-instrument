# exp_dev hand-off -- research: streaming / continual extraction architecture

Filed-by: research sub-agent
Trigger: notes/research_drill_streaming_continual_extraction_2x_2026-06-05.md
Date: 2026-06-05

## Pause state

Per [[feedback-obey-user-pause-explicitly]]: check data/orchestrator_paused.flag before dispatching.
If flag present, queue this handoff for next resume cycle.

Per [[feedback-no-experiment-design-in-prompts]]: this handoff contains TASK + WHY + CONTRACT + AUTONOMY only.
It does NOT specify anchor names, sweep grids, threshold formulas, or pre-committed cap_map decisions.
exp_dev owns all of those.

---

## Anchor candidates (rank-ordered)

### Rank 1: Streaming substrate write smoke test (STREAM-V1 class)
Anchor pointer: prefill-KV streaming write pipeline; bipolar outer-product update gated by confidence score
Substrate-product reading: establishes whether live inference traffic can build the substrate without a separate extraction pass -- eliminates entire data-pipeline component in commercial deployment
Tier hint: CPU smoke (< 15 min wall), no GPU required
Why now: Alchemist (arXiv:2503.01066) and vLLM Hook v0 (arXiv:2603.06588) provide the serving-stack integration points; the substrate write primitive (rank-1 Hebb update) is already implemented; the gap is wiring them together and measuring retrieval accuracy vs batch-extracted baseline

### Rank 2: Hallucination contamination gate (STREAM-V2 class)
Anchor pointer: entropy gate on logit distribution; threshold calibration; contamination rate measurement
Substrate-product reading: quantifies the safety margin for commercial deployment; determines whether streaming is viable for non-regulated domains without manual curation
Tier hint: CPU, depends on STREAM-V1 smoke passing
Why now: HALT (arXiv:2602.02888) provides the per-token logit-entropy detector; the contamination rate target (<5%) is falsifiable with a seeded hallucination corpus

### Rank 3: Multi-layer consistency gate (STREAM-V3 class)
Anchor pointer: layer-2 energy gate (substrate energy check on candidate fact); combined contamination reduction
Substrate-product reading: enables streaming in higher-stakes domains; also validates that substrate energy function is discriminating novel-valid from novel-hallucinated patterns
Tier hint: CPU, depends on STREAM-V2 baseline
Why now: algebraic analysis predicts O(epsilon_H^2) contamination rate under combined gate; this is a strong falsifiable prediction

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_streaming_continual_extraction_2x_2026-06-05.md
vLLM Hook paper: arXiv:2603.06588
Alchemist paper: arXiv:2503.01066
HALT paper: arXiv:2602.02888
DDAM paper: arXiv:2511.23347
Phase 3 blueprint (layer selection 8/10/12): check notes/ for Phase 3 architecture files
Bipolar write primitive: hdlab/ (Hebb outer product update, already implemented)

---

## Contract

exp_dev owns:
- Anchor naming (no pre-committed names here)
- Sweep grid (N choices, layer choices, gate theta values)
- Pre-registration bands (HP/MID/HF thresholds)
- Queue routing (CPU vs GPU; use CPU for smoke)
- Cap_map decision post-verdict

Research owns:
- The algebraic model and P_deflated estimates in the research note
- Literature citations (7 verified)
- Falsifiable prediction structure (HP1-HP4, HF1-HF4)

## Autonomy declaration

exp_dev has full autonomy on implementation details, anchor parameterization, and queue ordering.
The research note's falsifiable predictions (HP/HF thresholds) are advisory pre-registration inputs,
not binding constraints -- exp_dev adjusts based on observed smoke results.
