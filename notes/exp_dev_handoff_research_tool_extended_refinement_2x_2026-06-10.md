# exp_dev hand-off -- research: PP-326 tool-extended-real refinement 2x

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** PP-326 TOOL-EXTENDED-REAL HARD_PASS at AUC=0.866. Gap of -0.134 from synthetic 1.000. Research drill identifies 5 concrete mechanisms and 5 experimental paths to close the gap.

**Research note:** d:/AI/hd-instrument/notes/research_drill_tool_extended_refinement_2x_2026-06-10.md

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. PP-326-EVENT-STRATIFICATION (cheap decisive test, no new data)
- Anchor pointer: research note Section "Cheap decisive test" and Stream D6 (distal endpoint anchoring).
- Substrate-product reading: stratify existing real-tool test set by event type (distal contact / proximal transfer / vibrational / quasi-static). AUC breakdown determines whether the gap is endpoint-anchoring failure vs uniform distributional shift. This is a zero-collection diagnostic that gates all downstream intervention choices.
- Tier hint: local CPU (inference-only pass over existing test set with event-type labels).
- Why now: this is the decision gate. Running it first avoids spending GPU budget on the wrong intervention.

### 2. PP-326-DOMAIN-RAND-NOISE (domain randomization on sensor noise)
- Anchor pointer: research note Stream B (force chain / vibrotactile filtering), Prediction 1.
- Substrate-product reading: re-train with domain-randomized sensor noise injected during training (Gaussian on force channels + structured vibration noise 100-500 Hz band). HARD-PASS target: AUC > 0.93. HARD-FAIL: AUC < 0.87 after randomization.
- Tier hint: GPU (full re-train with augmented data pipeline).
- Why now: highest P_deflated of any single intervention (0.48). Addresses the most common sim-to-real failure mode documented in visuotactile literature (VTDexManip 34% failure reduction precedent).

### 3. PP-326-REAL-DATA-FINETUNE (fine-tune on real-sensor trial sequences)
- Anchor pointer: research note Stream D1 (VTDexManip, VINT-6D), Prediction 2.
- Substrate-product reading: fine-tune on 500+ real-tool trial sequences. HARD-PASS: AUC > 0.945 (closes >60% of gap). HARD-FAIL: AUC < 0.90 (architecture mismatch).
- Tier hint: GPU (fine-tune run, smaller than full re-train).
- Why now: P_deflated = 0.50. Strongest supported path with direct empirical precedent from robotics benchmarks.

### 4. PP-326-ADVERSARIAL-DROPOUT (adversarial correlated sensor dropout)
- Anchor pointer: research note Stream D3 (NeuralFeels Science Robotics), Prediction 4.
- Substrate-product reading: stress test with simultaneous dropout of 3 of 5 contact sensors. HARD-PASS (resilient): AUC > 0.82. HARD-FAIL (brittle): AUC < 0.70. This is a product requirement probe, not a gap-closing experiment.
- Tier hint: CPU (inference-only with dropout applied at test time).
- Why now: adversarial correlated failure is the deployed failure mode. Must be characterized before any demo deployment of tool-extended capability.

### 5. PP-326-MULTI-TOOL-DIVERSITY (train on diverse tool types, test generalization)
- Anchor pointer: research note Stream D5 (SimToolReal, multi-tool integration), Prediction 5.
- Substrate-product reading: train on 5 diverse tool geometries (rigid/compliant/articulated), test on held-out tool type. HARD-PASS: AUC > 0.91 on held-out tool. HARD-FAIL: AUC < 0.87 (no generalization benefit).
- Tier hint: GPU (multi-tool training batch).
- Why now: P_deflated = 0.35, but multi-tool support is a v2.0 architecture requirement. Early signal on whether current architecture supports it without structural changes.

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_tool_extended_refinement_2x_2026-06-10.md -- full research note with all stream details, predictions, and citations
- d:/AI/hd-instrument/notes/substrate_capability_map.md -- current cap_map; PP-326 row state
- d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-10_v3_cliff_crossed.md -- today's session state
- d:/AI/hd-instrument/notes/research_drill_synthetic_to_real_gap_audit_2x_2026-06-10.md -- adjacent real-vs-synthetic gap findings from today

---

## Contract

exp_dev will:
1. Read the research note at the pointer above before designing any anchor.
2. Run PP-326-EVENT-STRATIFICATION first (it is the decision gate).
3. Use event-type stratification result to decide which of anchors 2-5 to prioritize.
4. Pre-register HARD-PASS and HARD-FAIL bands per the thresholds in the research note Predictions section.
5. Apply the pre-dispatch speed+harden+progress discipline per `feedback_pre_dispatch_speed_harden_progress_discipline.md`.

## Autonomy declaration

exp_dev owns: anchor naming, N/M/K/seed/threshold/queue assignment, smoke profile design, full run configuration. This file provides direction and pointers only.
