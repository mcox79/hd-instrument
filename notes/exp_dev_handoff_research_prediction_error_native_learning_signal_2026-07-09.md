# exp_dev hand-off -- research: prediction-error as native learning signal + grounding link

Filed-by: research sub-agent
Date: 2026-07-09
Trigger: notes/research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md
Urgency: MEDIUM-HIGH -- cheap, extends an ALREADY-LANDED cell family with real positive on-disk signal
(v2's PRED-only arm already outscores its own HYBRID arm), not a from-scratch build.

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ranked anchor candidates only. Experiment design details (exact
matrix wiring, seed grid, corpus) are to be authored by exp_dev from the research note's Falsifiable
Predictions section. Do NOT treat the description below as an implementation spec.

---

## Anchor candidates (rank-ordered)

### Anchor 0 (do FIRST, near-zero cost, not really a new experiment): read `v2`'s `ARM_PREDICTIVE_ONLY`
cell source + confirm what it actually wires

Anchor pointer: Research note "Disk-verify note" table + S2 "Measurable test" section.

Substrate-product reading: The research note found, via already-landed `metrics.json` on disk (not
hallucinated), that `exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2`'s
own verdict shows its PRED-only arm (`gap=0.566`) beating its own HYBRID arm (`gap=0.517`). Before
authoring any new cell, confirm from the `v2` cell source whether `ARM_PREDICTIVE_ONLY` already implements
a continuous, precision-weighted write-strength curve (reusing `predictive_coding.residual_magnitude` +
`proportional_gate`) into a matrix functionally separate from the contrastive channel -- or whether it is a
simpler ablation (e.g., binary write-gate only). This determines whether Anchor 1 below is genuinely new
scope or a duplicate of already-landed work.

Tier hint: read-only, no dispatch, ~10 minutes.

### Anchor 1: dedicated precision-weighted `W_pred` matrix, kept structurally separate from the
existing contrastive channel

Anchor pointer: Research note S2 (concrete design) + Cheap decisive test + Falsifiable Prediction rows 1-3.

Substrate-product reading: Tests whether a SECOND, dedicated weight matrix -- updated via the existing
`hdlab/predictive_coding.py` primitives (`predict`, `residual_magnitude`, `proportional_gate`,
`gated_write`), kept structurally separate from the existing no-gradient contrastive-Hebbian channel
(`testbed/substrate_lm/primitives.py` Primitive 2, explicitly commented "Substitutes for InfoNCE / triplet
loss in a NO-GRADIENT setting") -- measurably improves concept-HD clustering quality on the Spoke1 metric
suite (`cat_kitten_cos`, `cat_airplane_cos`, `sparse_rate`, `intra_concept_cv`), either alone or combined
with the existing contrastive channel. Directly extends, does not replace, the existing Spoke1 harness.

Tier hint: CPU-only, reuses existing Spoke1 corpus/harness; new code limited to a second weight matrix and
one new arm wiring (research note estimates ~1-2 hr local_cpu build + smoke, matching the original Spoke1
design note's own cost estimate).

Why-now: cheap (reuses primitives already on disk, no new representational math), and the existing `v2`
landed data already gives a positive signal worth following up on rather than a cold-start hypothesis.

Pre-reg bands (full detail in research note Falsifiable Predictions table):
  Row 1 (predictive channel alone): HARD-PASS `cat_kitten_cos >= 0.25` AND `cat_airplane_cos <= 0.15`;
    HARD-FAIL `cat_kitten_cos < 0.15`.
  Row 2 (combined predictive + existing contrastive vs. `ARM_FULL_HYBRID` alone): HARD-PASS combined beats
    `ARM_FULL_HYBRID`'s `cat_kitten_cos` by >= 0.05 absolute with `intra_concept_cv` within 15% of
    `ARM_FULL_HYBRID`'s; HARD-FAIL no improvement or >15% stability cost.
  Row 3 (precision-weighting ablation, weighted vs. flat write at matched write-budget): HARD-PASS
    weighted beats flat by >= 0.05 on `cat_kitten_cos`; HARD-FAIL no measurable difference.

### Anchor 2 (higher-leverage, higher-risk, cross-thread): prediction-error-against-ingest-data as the
shared exogenous reconstruction target for the self-play Speaker/Listener differentiation problem

Anchor pointer: Research note S3 (grounding-link hypothesis) + Falsifiable Predictions table, row 4.

Substrate-product reading: `research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md` named "exogenous
grounding... as a backstop only when internal architectural asymmetry is degenerate/absent" but left the
specific mechanism unspecified. This anchor tests whether wiring prediction-error against the substrate's
real ingest stream (not a self-generated or contrastive-paired target) as a SHARED reconstruction target
both Speaker and Listener branches must independently satisfy reduces
`corr(failure_mask_speaker, failure_mask_listener)` below the already-landed B1 cross-fit baseline (0.39,
per that note). This is the direct, concrete instantiation of that note's named-but-unspecified fallback.

Tier hint: depends on the self-play cell's existing harness (exp_dev to identify nearest extension point);
likely moderate cost since it touches the self-play cell family, not the Spoke1 family.

Why-now: LOWER priority than Anchor 1 -- P_deflated is lower (0.25, the lowest of all rows in the research
note, explicitly flagged as two inferential steps removed from directly-tested literature) and it depends
on the self-play cell's current state (check whether B1/B1+PS work from that note's own hand-off has
already been picked up before adding a third arm). Recommend running AFTER Anchor 1, and only after
confirming the self-play B1+PS cell's status.

Pre-reg bands (full detail in research note Falsifiable Predictions table, row 4):
  HARD-PASS: `corr(failmask) <= 0.30` with grounding intact (`>= 0.50`).
  HARD-FAIL: `corr(failmask) >= 0.39` (no better than the already-landed B1 baseline).
  MIDDLE_BAND: `corr(failmask)` in (0.30, 0.39).

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md
- Existing primitives to reuse (Anchor 1): hdlab/predictive_coding.py; testbed/substrate_lm/primitives.py
  (Primitive 2, the no-gradient contrastive-Hebbian channel this drill proposes NOT to replace, only to
  complement)
- Existing Spoke1 cell family (Anchor 1 extension point):
  experiments/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1.py,
  experiments/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2.py,
  experiments/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026-07-02.py,
  experiments/exp_substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1.py
- Design note for the Spoke1 family: notes/design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md
- Self-play cross-link (Anchor 2): notes/research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md,
  notes/research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md
- Correlation-hurts-capacity precedent (why `W_pred` must stay structurally separate, Anchor 1):
  notes/reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md
- Landed metrics referenced in this hand-off (read directly, not summarized elsewhere):
  data/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2_smoke/metrics.json,
  data/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1_smoke/metrics.json,
  data/exp_substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1/metrics.json

---

## Contract section

This handoff proposes one near-zero-cost verification step (Anchor 0) and two ranked buildable anchors
(Anchor 1 recommended first, Anchor 2 second and contingent on self-play cell status). Exp_dev authors
exact matrix wiring, seed grid, and corpus reuse for whichever anchor(s) it picks up. Do NOT treat the
anchor descriptions above as implementation specs.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchor(s) to pick up first (Anchor 0 -> Anchor 1 recommended order, but exp_dev may
  reprioritize based on current queue state and what Anchor 0's read reveals)
- Choosing exact matrix/arm wiring for Anchor 1 within the pre-registered bands above
- Identifying the nearest existing self-play cell to extend for Anchor 2, and deciding whether to run it
  at all given its lower P_deflated and dependency on the self-play thread's current state
- Choosing local CPU vs remote_cpu_queue routing per the SMOKE-only-local rule

Exp_dev is NOT autonomous in:
- Declaring Spoke1 CG/promotion status based on this hand-off alone -- the research note explicitly flags
  the toughest already-run check (apples-to-apples/softmax-controlled) as MIDDLE_BAND, not HARD_PASS;
  Skunkworks/VET decides tier per landed-VET discipline
- Merging the new predictive channel into the EXISTING contrastive weight matrix -- the research note and
  the correlation-hurts-capacity precedent both require the two channels to remain structurally separate
  matrices, not merged into one
- Dispatching Anchor 2 without first checking whether the self-play B1/B1+PS cells from
  `research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`'s own hand-off have already been picked
  up (avoid duplicate/conflicting work on the same cell family)
