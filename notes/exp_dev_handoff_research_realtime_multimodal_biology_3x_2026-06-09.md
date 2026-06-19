# exp_dev hand-off -- research: real-time multi-modal biology 3x drill

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: notes/research_drill_realtime_multimodal_biology_3x_2026-06-09.md
Urgency: MEDIUM -- multi-modal integration is a hard block; NOVELTY-DETECTION and CROSS-MODAL-CONSISTENCY are low-effort, high-value, shippable from existing substrate primitives

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: novelty_detection_prediction_error_v1

Anchor pointer: Research note Level 5, Section 5.2 + Level 9 Rank 2
Substrate-product reading: Measure prediction-error-as-distance on held-out temporal sequences. Each stored fact has an expected cosine similarity distribution under the generative model; facts that fall below the distribution tail are flagged as novel/anomalous. This is the biological MMN/P300 analog. Requires NO new substrate primitives -- distance-to-nearest-neighbor is already computed in similarity search.
Tier hint: CPU laptop, ~1-2 hr. CHEAPEST decisive test. Gates PREDICTIVE-SUBSTRATE-1 (Anchor 3) and validates the prediction-error mechanism pathway.
Why-now: If AUC > 0.75, the prediction-error mechanism is working and opens the full predictive coding product line. If AUC < 0.55, the baseline similarity search is insufficient and a separate predictive model layer is needed.

Pre-reg bands:
  HARD-PASS: AUC > 0.75 on temporal sequence disruptions vs baseline; precision > 0.70 at recall = 0.80
  MIDDLE-BAND: AUC 0.60-0.75 (partial signal; combine with explicit prediction storage)
  HARD-FAIL: AUC <= 0.55 (at-chance; distance-to-nearest does not track prediction error)

### Anchor 2: cross_modal_consistency_v1 (PP-180 extended)

Anchor pointer: Research note Level 5, Section 5.5 + Level 9 Rank 1
Substrate-product reading: Extend contradiction detection to cross-modal pairs. Store (modal_A_binding, cross_modal_relation, predicted_modal_B_binding) triples. At query time, compute cos_sim(stored_prediction(A->B), actual_B_binding). High inconsistency flags cross-modal hallucination. Operates on existing FHRR algebra -- no new primitives.
Tier hint: CPU laptop, ~2-4 hr. Second priority after novelty_detection.
Why-now: Multi-modal hallucination detection is a differentiating product feature. Biology (PNAS 2025, PMC1661685) confirms the hippocampal mismatch mechanism is episodic-memory-based -- directly applicable to substrate fact retrieval.

Pre-reg bands:
  HARD-PASS: precision > 0.80, recall > 0.70 on held-out cross-modal conflict pairs
  MIDDLE-BAND: precision 0.65-0.80 (usable with tuned threshold)
  HARD-FAIL: precision < 0.55 (worse than majority-class baseline; mechanism fails)

### Anchor 3: continuous_binding_fhrr_rotations_v1

Anchor pointer: Research note Level 4, Section 4.7 + Level 9 Rank 3
Substrate-product reading: Implement fractional power encoding (FPE) for a continuous temporal parameter (time-since-event or position). Encode 100 evenly-spaced parameter values as V^t for t in [0, 1]. Verify cosine similarity decay < 0.1 per 10-degree step and decoding MSE < 0.05 over 100 steps. Based on published Grid-Cell-VSA (arXiv 2503.08608) results (MSE ~ 0.17/100 steps at N=1024).
Tier hint: CPU laptop, ~1-2 hr. Low engineering effort -- existing FHRR complex multiplication extended to fractional exponent.
Why-now: CONTINUOUS-BINDING-FHRR-ROTATIONS gates temporal indexing, time-cell analog, and smooth interpolation queries. These are prerequisites for any real-time temporal reasoning product.

Pre-reg bands:
  HARD-PASS: cosine similarity > 0.9 at 10-step separation; MSE < 0.05 at 100 steps; N=1024
  MIDDLE-BAND: cosine > 0.7 at 10-step; MSE 0.05-0.15 (usable but requires larger N)
  HARD-FAIL: cosine < 0.5 at 10-step (rotations decorrelate too fast; revisit encoding scheme)

### Anchor 4: predictive_substrate_sequence_v1

Anchor pointer: Research note Level 9 Rank 5 + Level 2 Section 2.5 (HTM)
Substrate-product reading: Store sequential fact chains as (context_t, fact_t+1) binding pairs. Query by context to retrieve predicted next fact. Measure p_correct on held-out temporal chains. This is the substrate analog of HTM sequence memory and cerebellar forward model.
Tier hint: CPU laptop, ~3-5 hr. Requires designing the sequential encoding protocol -- moderate engineering.
Why-now: Gated by novelty_detection_v1 PASS. If prediction error mechanism works (Anchor 1), sequence prediction is the natural next step. Product capability: temporal fact chains, predictive retrieval, sequence completion (all absent in current RAG systems).

Pre-reg bands:
  HARD-PASS: p_correct > 0.60 on k=5 step lookahead; better than unigram frequency baseline
  MIDDLE-BAND: p_correct 0.40-0.60 (learning but not reliably; tune encoding)
  HARD-FAIL: p_correct <= 0.35 (at chance; sequence encoding adds no information)

### Anchor 5: forward_model_cerebellum_v1

Anchor pointer: Research note Level 9 Rank 4 + Level 2 Section 2.7
Substrate-product reading: Implement a fast-lane substrate query that returns predicted next state given current state. Implemented as a second codebook of (state, predicted_next_state) pairs. Measure latency at N=1024 and N=65k. Requirement: < 1ms at N=1024, < 5ms at N=65k.
Tier hint: CPU laptop, ~2 hr. Latency measurement is the main deliverable; implementation is a codebook addition.
Why-now: Sub-ms retrieval is already demonstrated. This anchor validates that the forward model is fast enough to be useful and measures the latency gap (if any) at production scale.

Pre-reg bands:
  HARD-PASS: lookup latency < 1ms at N=1024; < 5ms at N=65k; prediction matches ground truth > 60% top-1
  MIDDLE-BAND: latency 1-10ms (acceptable with batching); accuracy 40-60%
  HARD-FAIL: latency > 50ms OR accuracy <= 35% (no better than random; forward model not useful)

---

## Sequencing constraint

Anchor 1 (novelty_detection) is the gate for Anchor 4 (predictive_substrate). If Anchor 1 HARD-FAILS, route Anchor 4 to research for redesign before dispatch.

Anchors 2 (cross_modal_consistency) and 3 (continuous_binding_fhrr_rotations) are independent and can run in parallel if queue depth permits.

Anchor 5 (forward_model_cerebellum) can run in parallel with Anchors 2 and 3.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_realtime_multimodal_biology_3x_2026-06-09.md
- EXP-DEV post-compaction brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Production architecture lock: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md
- ZKL rescue handoff (encoder isotropy context): d:/AI/hd-instrument/notes/exp_dev_handoff_research_zkl_realkey_rescue_3x_2026-06-07.md
- Prior contradiction detection context (PP-180): check cap_map rows PP-180 or equivalent in notes/substrate_capability_map.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

The cheapest decisive test (Anchor 1, novelty_detection, ~1-2 hr CPU) should run first. It gates Anchor 4 and validates the prediction-error pathway that underpins the entire predictive coding product line.

Cross-modal consistency (Anchor 2) is independent and high-value; can dispatch concurrently.

HARD-FAIL on Anchor 3 (continuous_binding_fhrr_rotations) routes back to research for encoding redesign; do not escalate to cloud.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, and encoding parameter values for each anchor
- Choosing local CPU routing for all 5 anchors (none require GPU)
- Writing experiment scripts following feedback_metrics_required_fields_write_metrics.md

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Extending continuous binding to production encoding pipeline (requires architecture decision)
- Declaring the multi-modal integration hard block resolved (requires orchestrator verdict)
