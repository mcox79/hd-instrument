# PRE-REG: BRIDGE-1 context-conditioned grounding (governor/frame -> appraisal valence)

anchor_name: bridge1_governor_grounding_v1
date: 2026-08-05
author: exp_dev
status: FILED

## What this cell is

BRIDGE-1 per notes/PLAN_grounded_semantic_organ_build.md Section 3 FOUNDATION and the VET
notes/brain_fidelity_vet_components.md. An EARNED, glass-box map from (target word, its sentence
context) to the FROZEN earned appraisal-sim's input dims (congruence HURT/HELP/NEUTRAL, coping
HIGH/LOW), scored by DOWNSTREAM DIFFERENTIAL GROUNDING on collision pairs -- NOT isolated 2AFC,
NOT bag-of-words. Reuses:
- experiments/exp_grounded_appraisal_sim_earned_v1.py: Codebook, phi(), train_theta(), CONG/COPE/
  TYPES tables -- the FROZEN valuation spoke (theta is trained once per seed on the SAME synthetic
  bandit task as the original cell; text-bridging code never touches theta after training).
- hdlab/thematic_role_labeler.py: train_perceptron/scramble_weights (the EARNED cue-integration
  engine, reused verbatim) + frame_slot_role/VERB_FRAMES (Component-3 frame signal, one feature).
- A NEW lightweight governor/adjective-modifier extractor (nearest-VERB-before-target,
  nearest-ADJ-before-target over POS-tagged tokens) -- same shape as the repo's existing
  is_passive_clause / role_feats POS-window detectors, not a full parser but a real, uniform,
  non-per-item-hand-tuned rule.

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "context-conditioned grounding governor frame appraisal valence
bridge"` -> top hit cosine=0.3076 (generic WordNet entity "conditioned", ANTONYM_OF unconditioned;
not on-topic). NONE at cosine>0.30 on-topic. Genuinely novel build, not a rediscovery.

## Mechanism (what is EARNED vs SUPPLIED)

SUPPLIED (seed knowledge, glass-box, disjoint TRAIN/TEST governor+adjective vocab pools):
- GOVERNOR_VERB_CLASS: word -> {HARM, HELP, NEUTRAL} (12 harm verbs, 8 help verbs, 16 neutral verbs,
  split into disjoint TRAIN-only and TEST-only sub-pools so the classifier cannot memorize specific
  governor words seen in training).
- ADJ_MODIFIER_CLASS: word -> {HARM, HELP} (6 harm adjectives, 6 help adjectives, same disjoint
  TRAIN/TEST split).
- LOW_COPE_CUES: closed-class cue words signaling low coping capacity (exhausted/helpless/...).

EARNED (the deliverable, trained per-seed via hdlab.thematic_role_labeler.train_perceptron on
governor/adjective-CLASS features + frame + cope-cue + order -- NEVER the target word string, NEVER
raw governor token identity):
- A cue-integration averaged perceptron: features -> predicted TYPE in {BLOCK_HIGH, BLOCK_LOW,
  RECIPROCITY, NEUTRAL} (the appraisal-sim's own episode-type vocabulary, which maps 1:1 to
  (congruence, coping) via CONG/COPE).
- Predicted TYPE -> (cong, cope) -> synthetic ep dict -> phi(cb, ep, action, "FULL") @ theta_FULL,
  producing VALENCE = Q(harm@coherent-target) - Q(help@coherent-target) under the FROZEN theta.
  This is the appraisal-sim's OWN forward pass -- not a lookup table.

## Eval design (differential grounding on collision pairs)

6 collision FORMS (hard/trick/blow/cross/sound/bear -- covers 4 of the audit's example words plus 2
more), each in TWO contexts whose GOVERNOR (verb-path) or ADJACENT-ADJECTIVE (adj-path) forces
opposite congruence sign (e.g. "she practice hard" [NEUTRAL, non-harm] vs "he strike her hard"
[BLOCK_HIGH, harm]). All 12 collision items use ONLY TEST-pool governor/adjective vocabulary (never
seen during TRAIN perceptron fitting) -- this is the disjoint-vocab discipline (Section 2 of the
plan) applied to governor words, not just target words.

Held-out UNSEEN-CONCEPT set: 9 items with target NOUNS never used anywhere in TRAIN or the collision
set (insult/gift/curse/warning/reward/penalty/favor/threat/warrior), still drawn from the TEST
governor/adjective vocab pool, single-context each (not paired) -- tests that the LEARNED
governor-class -> TYPE mapping transfers to genuinely novel target concepts (not per-word
memorization, guaranteed structurally since target-word identity is never a classifier feature, but
measured empirically here rather than assumed).

## Controls (must run, pre-registered can-fail)

1. BAG-OF-WORDS control: same perceptron-training pipeline, but features = raw lowercase tokens
   (excluding the target word) instead of governor/adj CLASS + frame + cope + order. Because TRAIN
   and TEST(collision+unseen) governor/adjective vocab pools are fully disjoint by construction, BOW
   has zero informative signal for the discriminating tokens at test time -- MUST fall to ~chance.
2. PER-FORM FIXED TABLE control (simulates `resolve_valence_blind`): for each collision word FORM,
   take the governor-arm's own prediction on context A and apply it UNCHANGED to context B (a
   single, context-blind table entry per form). Both members of every collision pair get an
   IDENTICAL predicted TYPE -> per-item sign accuracy on the 12 collision items is EXACTLY 0.50 by
   construction (one member of each of the 6 pairs is necessarily wrong).
3. SCRAMBLED-GOVERNOR control: GOVERNOR_VERB_CLASS and ADJ_MODIFIER_CLASS values (not keys) are
   permuted with a fixed seed BEFORE feature extraction (both TRAIN and TEST use the same broken
   dict) -- breaks the true governor-word -> class correspondence while preserving feature *shape*.
   Must collapse toward chance.
4. THETA WITNESS: assert VALENCE(BLOCK_HIGH) != VALENCE(BLOCK_LOW) even though both share
   congruence=HURT (they differ only in coping HIGH/LOW) -- proves theta's full phi encoding (which
   binds coping, not just congruence) drives the value, not a congruence-only lookup. Also report the
   theta arm's SHA256 digest per seed (arms-must-differ, META_RULE_AF) against RANDOM theta.
5. ARMS-MUST-DIFFER: governor / bow / per_form / scrambled arms' predicted-TYPE sequences on the
   pooled (collision+unseen) eval set must not be bit-identical across all four arms.

## Bands (pre-registered before running)

- HARD_PASS: differential_grounding_acc (12 collision items) >= 0.75 AND bow_control_acc <= 0.60
  AND unseen_concept_acc >= 0.70 AND (differential_grounding_acc - bow_control_acc) >= 0.15 AND
  per_form_table_acc <= 0.60 AND scrambled_acc <= 0.60.
- HARD_FAIL: differential_grounding_acc < 0.60 OR |differential_grounding_acc - bow_control_acc| <
  0.05 OR per_form_table_acc >= differential_grounding_acc - 0.05.
- else MIDDLE_BAND (report which gate failed; drill the mechanism per the plan's Section 5 -- is
  governor extraction wrong, is the verb-class seed too sparse, or does this need full situation-
  level context beyond the local governor).

## Compute architecture
Sequential-CPU, justified: this is the substrate-primitive being validated (perceptron fit over
~140 tiny feature-dicts + FHRR N_DIM=256 theta training over a few thousand synthetic bandit steps);
wall time << 10s total per seed. No GPU batching candidate.

## Cell-template mandates
- arms_differ_verified: true (governor/bow/per_form/scrambled predicted-TYPE sequences + theta
  hashes, asserted in self-test and full run)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException) -- present
- crlb_n/a: "no swept capacity dimension; classification accuracy discriminator only, not a
  cleanup-capacity claim"
- baseline_in_band: n/a (this is a differential-grounding accuracy cell, not a saturation-prone
  cleanup baseline; the RANDOM-theta arm inside the reused sim code path IS still near chance, as
  the theta-witness section checks)
- discriminator survives scale: full-N == smoke-N here (item counts are small by design; the
  discriminator is the CONTROLS' gap, not a capacity sweep) -- smoke and full run identical item
  sets, differ only in theta-training step count (smoke=1500, full=6000)
- cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
- per-unit failure-class instrumentation: per-seed try/except with failure_class recorded, no bare
  except
- calibration_check: default_ok_for_this_regime (bands set BEFORE running from the 0.50-by-
  construction per-form-table floor and chance=0.50 for a 2-way sign discriminator, not tuned after
  seeing results)
- deterministic_seeding: torch.Generator + Python `random.Random` per seed, hashlib-derived
  (not builtin hash()) where any string->int seed derivation is needed; sorted() iteration order
  throughout
- cell_chunked: true (per-seed unit via tools/exp_checkpoint.py unit_key/completed_units/
  record_unit/load_units)
- progress_logging: print_flush_true (all print() calls use flush=True; timeout well under 1800s so
  §17 is not strictly mandatory but applied anyway for auditability)

## Local-only discipline
LOCAL-only, glass-box, no borrowed embedding. Run in-process/foreground to completion. git-commit
after landing. NO origin push (not authorized this task).
