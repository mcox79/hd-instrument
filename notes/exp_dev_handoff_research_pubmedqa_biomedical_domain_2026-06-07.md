# exp_dev hand-off -- research: PubMedQA biomedical domain 2x

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_pubmedqa_biomedical_domain_2x_2026-06-07.md
Urgency: HIGH -- biomedical is Tier-1 regulated-industry customer segment; 28-point RAG gap needs resolution before medical customer conversations

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

### Anchor 1: pubmedqa_encoder_swap_pubmedbert_v1 (PRIMARY GATE)

Anchor pointer: Research note Section 3 Path 1 + Section 4 Pre-test 1
Substrate-product reading: Swap bge-small for PubMedBERT-base-embeddings (NeuML/pubmedbert-base-embeddings on HuggingFace). Re-embed PubMedQA knowledge base. Re-run cycle 166 eval. Simultaneously run TriviaQA regression. This is the cheapest single experiment that gates all downstream encoder decisions.
Tier hint: CPU laptop, ~3-4 hr total. No GPU needed. No changes to substrate algebra.
Why-now: This test distinguishes "encoder mismatch" (fixable 2-day swap) from "substrate algebra failure" (deeper issue). Without this result, medical customer conversations cannot be grounded in honest numbers.

Pre-reg bands:
  HARD-PASS: substrate PubMedQA >= 0.73 AND TriviaQA regression <= 0.01. Encoder-mismatch hypothesis confirmed. Ship encoder-agnostic deployment recommendation.
  MIDDLE-BAND: substrate PubMedQA 0.62-0.73. Encoder is a significant contributor but not the only cause. Route to Anchor 3 (K-hop sweep) as secondary.
  HARD-FAIL: substrate PubMedQA < 0.62. Encoder swap insufficient. Investigate classification type (Anchor 2) or substrate algebra as primary cause.

### Anchor 2: pubmedqa_confusion_matrix_analysis_v1 (PARALLEL DIAGNOSTIC)

Anchor pointer: Research note Section 4 Pre-test 2
Substrate-product reading: Run cycle 166 substrate eval on PubMedQA and log full 3x3 confusion matrix (yes/no/maybe x predicted yes/no/maybe). Compare to RAG confusion matrix. No encoder change, no architecture change. Pure diagnostic.
Tier hint: CPU laptop, ~1 hr. Run in parallel with Anchor 1.
Why-now: Cheapest diagnostic available. If substrate systematically fails on "maybe" class but not "yes/no", the failure is classification-type not retrieval quality. This changes the repair path (K tuning or prompting, not encoder swap).

Pre-reg bands:
  HARD-PASS: "maybe" precision < 0.30 with "yes/no" precision > 0.65. Classification-type is a significant secondary cause. Add class-specific prompting to repair list.
  MIDDLE-BAND: uniform confusion across all three classes. Retrieval is the bottleneck.
  HARD-FAIL: substrate confusion matrix closely matches RAG. Neither classification type nor retrieval quality explains the gap; investigate answer extraction or LLM reasoning.

### Anchor 3: pubmedqa_k_hop_sweep_v1 (SECONDARY, RUN AFTER ANCHOR 1)

Anchor pointer: Research note Section 4 Pre-test 3
Substrate-product reading: Run substrate on PubMedQA with K = 2, 5, 10 top facts and also full-abstract (no K truncation). Goal: quantify how much of the 28-point gap is K-hop coverage vs encoder vocabulary.
Tier hint: CPU laptop, ~2 hr. Run only if Anchor 1 returns MIDDLE-BAND (not HARD-PASS).
Why-now: If K=5 brings substrate to 0.62+ without encoder change, K tuning is a zero-engineering-day quick win. If K-sweep is flat, confirms encoder is the dominant factor.

Pre-reg bands:
  HARD-PASS: K=5 substrate >= 0.62, K=10 >= 0.65. K-hop coverage is a real secondary contributor. Set K=5 as biomedical default.
  MIDDLE-BAND: K=5 vs K=2 shows +3-5 pts but plateaus at K>=5. Some coverage effect, not dominant.
  HARD-FAIL: K=2 vs K=10 are within 0.02. K-hop is not the issue. Encoder vocabulary or classification type is the entire gap.

---

## Sequencing

Run Anchor 1 and Anchor 2 in parallel (both < 4 hr CPU, independent).
Run Anchor 3 only if Anchor 1 returns MIDDLE-BAND.
Do NOT run Anchor 3 if Anchor 1 HARD-PASSes (encoder swap solved it; K tuning is secondary).

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_pubmedqa_biomedical_domain_2x_2026-06-07.md
- Cycle 166 eval context: check data/ directory for cycle 166 metrics
- Production architecture memory: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md
- Encoder noise robustness note (related mechanism): d:/AI/hd-instrument/notes/research_drill_substrate_encoder_noise_robustness_2x_2026-06-07.md
- Multi-hop ceiling note (different failure, same benchmark family): d:/AI/hd-instrument/notes/research_drill_multihop_precision_ceiling_3x_2026-06-07.md

---

## Contract section

This handoff proposes 3 anchor candidates. Exp_dev selects from these based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 3.

SEQUENCING CONSTRAINT: Anchor 1 and Anchor 2 are parallel. Anchor 3 gates on Anchor 1 MIDDLE-BAND result.

URGENCY NOTE: Anchor 1 is the highest-priority unresolved benchmark question for medical customer conversations. If queue is empty and no higher-urgency anchors are pending, Anchor 1 should be next.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, and parameter values for each anchor
- Choosing local CPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md (all three anchors are CPU-only)
- Writing experiment scripts that follow the feedback_metrics_required_fields_write_metrics.md convention
- Choosing whether to use the HuggingFace model hub directly or a locally cached version of PubMedBERT-base-embeddings

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Making customer-facing claim revisions based on these results (orchestrator owns after verdicts are in)
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
- Deciding that the biomedical encoder is the new default production encoder (that requires user authorization after verdicts confirm)
