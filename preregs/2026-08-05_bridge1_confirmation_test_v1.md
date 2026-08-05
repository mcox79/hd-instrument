# PRE-REG: BRIDGE-1 confirmation test -- governor-only necessary-not-sufficient

anchor_name: bridge1_confirmation_test_v1
date: 2026-08-05
author: exp_dev
status: FILED

## What this cell is

A can-fail CONFIRMATION measurement, not a build. Runs the UNMODIFIED current BRIDGE-1 mechanism
(experiments/exp_bridge1_governor_grounding_v1.py, commit 96e8e8404, imported and never edited --
GOVERNOR_VERB_CLASS/ADJ_MODIFIER_CLASS/extract_governor_feats/TRAIN_ITEMS/COLLISION_ITEMS/
UNSEEN_ITEMS/valence_for_type reused verbatim) on three held-out subsets to empirically test the
deep-drill synthesis ruling in notes/deepdrill_SYNTHESIS_bridge1_certainty.md: governor-only sense
selection is NECESSARY-NOT-SUFFICIENT -- it should PASS the local-governor subset but FAIL
(wrong-direction, at/below majority baseline) on governor-matched/event-differing pairs and on
discourse-decisive pairs.

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "governor-only sense selection event-differing discourse-decisive
appraisal confirmation test bridge1"` -> top hit cosine=0.3281 (WordNet "a controversial decision
on affirmative action", off-topic), no on-topic hit above 0.30. Genuinely novel measurement, not a
rediscovery.

## Subsets (all authored here; disjoint from BRIDGE-1's TRAIN vocab; no explicit valence word in
any B/C local clause -- gold set by object/event or prior discourse, never by a lexical leak)

- A. LOCAL-GOVERNOR (positive control): BRIDGE-1's own COLLISION_ITEMS (12) + UNSEEN_ITEMS (9) = 21
  items, reused unmodified. Expected near-full-reproduction of BRIDGE-1's own 0.967/0.956 numbers
  (pooled here as one accuracy, ~0.96).
- B. GOVERNOR-MATCHED / EVENT-DIFFERING: 6 new minimal pairs (12 items). Same governor verb per
  pair (beat/broke/attacked/aided/comforted/shot), opposite event valence set by the OBJECT noun
  only (game vs dog; record vs arm; problem vs stranger; enemy vs refugee; enemy vs widow; film vs
  intruder). extract_governor_feats has no object-identity feature -- prediction is identical for
  both pair members by construction; gold differs -> ceiling = 0.50 for a correctly-implemented
  governor-only reader, independent of implementation quality.
- C. DISCOURSE-DECISIVE: 6 new minimal pairs (12 items). Local target clause is BIT-IDENTICAL
  across both members ("it approached the child"), gold set entirely by a PRIOR sentence that
  establishes the referent as benign or threatening (peanut-in-love pattern, Nieuwland & Van
  Berkum 2006). Governor verbs (approach/grab/touch/follow/circle/watch) are disjoint from TRAIN
  vocab. extract_governor_feats has no channel to the `prior` field at all -> ceiling = 0.50 by
  construction, same reasoning as B but via a different structural blind spot (no discourse
  memory, not just no object-identity).
- Scramble control on C: same 12 governor-arm predictions (which cannot change -- `prior` is never
  read by the mechanism), scored against a seeded shuffle of the 12 gold labels. Confirms C's low
  accuracy is architectural (governor-only ignores discourse either way), not a fragile item-
  construction confound.

## Bands (pre-registered before running, per notes/deepdrill_SYNTHESIS_bridge1_certainty.md
"Immediate can-fail CONFIRMATION test")

- RULING_CONFIRMED: acc_A >= 0.85 AND acc_B <= 0.60 AND acc_C <= 0.60.
- RULING_RELAXED (surprise): acc_B >= 0.75 OR acc_C >= 0.75 -- would mean governor-only implicitly
  encodes enough event/goal/discourse info to handle these subsets; re-check item construction for
  leakage before trusting it.
- else MIDDLE_BAND -- report honestly which gate cleared/missed.
- HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer than 5 seeds land.

Majority baseline for every subset is exactly 0.50 by construction (each subset is an exactly-
balanced set of minimal pairs: 21 items in A split ~evenly across 6 collision forms + 9 single-
context items already balanced in BRIDGE-1's own design; 12/12 balanced in B and C).

## Compute architecture
Sequential-CPU, justified: reuses BRIDGE-1's own tiny compute profile (perceptron fit over ~140
feature-dicts + FHRR N_DIM theta training over a few thousand synthetic bandit steps per seed);
full run (5 seeds, FULL_N_TRAIN_THETA=8000) completed in 28.0s wall-clock, in-process foreground.
No GPU batching candidate; this is a measurement cell reusing an already-validated primitive, not a
new sweep.

## Cell-template mandates
- arms_differ_verified: n/a-by-design -- this cell measures ONE unmodified mechanism across THREE
  subsets, not mechanism-vs-control arms. `arms_differ_exempted`: the informative comparison is
  subset-to-subset (A vs B vs C), documented explicitly in the cell docstring.
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException) -- present
- crlb_n/a: "no swept capacity dimension; sign-accuracy discriminator only"
- baseline_in_band: n/a (confirmation-measurement cell; majority baseline = 0.50 by construction
  for every subset, declared before running)
- discriminator survives scale: full-N == smoke-N (item sets identical; only n_train_theta differs,
  4000 smoke / 8000 full, matching BRIDGE-1's own precedent) -- MEASURED@d:/AI/hd-instrument/
  data/exp_bridge1_confirmation_test_v1_smoke/metrics.json and .../exp_bridge1_confirmation_test_v1/
  metrics.json: identical verdict (RULING_CONFIRMED) and near-identical means at both scales.
- cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
- per-unit failure-class instrumentation: per-seed try/except with failure_class recorded, no bare
  except
- calibration_check: default_ok_for_this_regime (bands set BEFORE running from the 0.50-by-
  construction majority floor per subset)
- deterministic_seeding: torch.Generator + Python `random.Random` per seed, hashlib-derived digests
- cell_chunked: true (per-seed unit via tools/exp_checkpoint.py unit_key/completed_units/
  record_unit/load_units)
- progress_logging: print_flush_true; full run elapsed_s=28.0s, well under the 1800s §17 threshold

## Local-only discipline
LOCAL-only, glass-box, no borrowed embedding, no origin push (not authorized this task). Ran
in-process/foreground to completion twice (smoke then full); results committed to the local repo.
