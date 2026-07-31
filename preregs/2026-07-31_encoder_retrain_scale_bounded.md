# Pre-reg: encoder-retrain SCALE (bounded) -- situation-model cross-frame entity re-id

Cell: `experiments/exp_situation_model_assembly_encoder_retrain_scale_v1.py`
Anchor: `situation_model_assembly_encoder_retrain_scale_v1`
Predecessor: `exp_situation_model_assembly_encoder_retrain_lite_v1` (commit 8eb1b3129 / d21b8f49e; MIDDLE-positive)
Date: 2026-07-31 | Author: exp_dev | Mode: INLINE-LOCAL CPU foreground (push-free), resumable per-condition.

## Question
Does the MIDDLE-positive lite (held-out loop 0.474->0.534) become a CLEAN PASS with modest more
seeds/diversity/unfreeze, or PLATEAU (top-layer fine-tune near ceiling)? Decisive read for the scale
decision. NOT the full from-scratch retrain (Director-gated).

## One variable
Per condition, ONLY the encoder weights differ vs the frozen v2 baseline (identical DRIFT-guarded eval
pipeline). Across conditions the swept axes are: unfreeze-depth {1,3,6 of 6 layers}, contexts-per-train-
entity {40,80} (steps scaled), seed {7,13,19}.

## Fairness gate
Held-out ENTITIES: 20 colors split 10 train / 10 held (SPLIT_SEED=71013); every eval query targets a
novel held-out entity. Train-entity eval computed in parallel for the memorization gap.

## Palette note (THEORETICAL)
eb.COLORS has exactly 20 words; held pool needs K_TRACK+N_DISTRACT=10 disjoint colors -> 10 train max.
Growing the palette requires bumping V_FILL, which changes CHANCE=1/V_FILL + filler cleanup tables + all
bands -> breaks the one-variable comparison to the landed frozen baseline. So the honest diversity lever
is contexts-per-entity, not palette size.

## Pre-registered bands (FIXED before running)
- CLEAN_PASS: EXISTS a config where, robust across >=2 seeds, held-out per-type tuned loop acc >= 0.60 for
  ALL 3 query types AND held-out within-minus-cross >= 0.30 AND held-out q_agree >= 0.60 AND memorization
  gap (train-minus-held loop acc) <= 0.15 AND no collapse. => break the wall, escalate to scale.
- PLATEAU: best tuned_loop_mean across ALL conditions within 0.03 of lite 0.534. => top-layer ceiling;
  deeper/from-scratch retrain is the next question (Director+USER), not a quick win.
- MIDDLE_TRAJECTORY: between -- reported WITH the trajectory (how far diversity/depth/seeds moved loop_mean
  + per-type min toward the bar = extrapolation signal).
- INVALID: a can-fail floor did not collapse OR POOLED_READER reservoir-decodable (validity gate inherited
  VERBATIM from the lite).

## Can-fail floors (must collapse near chance 0.05; validity gate)
random_addr, no_coref, wrongrole, shuffled, most_recent, pooled_reader. (Smoke MEASURED: all 0.00-0.12.)

## A-type diagnosis (deliverable)
Per-query-type oracle-headroom capture ((tuned-frozen)/(oracle-frozen)) for a/b/c + per-frame-pair ENT-rep
within-minus-cross MARGIN (question<->statement = a-relevant name<->name; question<->tag = b-relevant
name<->mark), frozen vs tuned. Tests whether a's non-recovery is because a is name-addressed (routing not
the bottleneck; residual = role/state decode, orthogonal to the entity-consistency retrain).

## Smoke (MEASURED 2026-07-31, eval_n=24)
- smoke_d3_s7: tuned loop 0.649 vs frozen 0.493, all 3 types lift (discriminator FIRES).
- smoke_d6_s7 (full unfreeze, 30 steps): tuned loop 0.421 < frozen 0.493, train 0.363 < held (overfit/
  representation-drift at full unfreeze -> depth axis discriminates).
- floors_ok=True (all floors collapsed). Verdict path reached MIDDLE_TRAJECTORY (not INVALID).

## Hardening
arms_differ (frozen vs tuned), tmp_replace atomic + per-condition units.jsonl resume, except SystemExit
before Exception (no BaseException), start_marker, crash_diagnostic, print-flush, DRIFT GUARD, real_code_path
self-test, per-call --budget-sec so each foreground call stays under the 10-min timeout.
