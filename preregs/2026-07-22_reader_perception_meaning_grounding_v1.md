# Pre-reg: reader_perception_meaning_grounding_v1

Date: 2026-07-22  |  Author: hdi_exp_dev  |  LOCAL-ONLY (no push, no bank)

## Question
Finish the deferred image-grounding integration: wire CONTENT-AWARE recognition INTO the
word<->referent bind so grounding becomes perception-MEANING (recognize WHAT the picture is ->
that drives the word<->picture match) instead of the current content-BLIND rote binding
(atom 29428: keyed word->image retrieval saturates for ANY encoder because orthogonal word-keys
isolate their payload).

## Mechanism (the integration)
Clean labeled images = a captioned corpus (real word<->referent pairs; NOT McGuffey woodcuts).
- PRIMARY sklearn olivetti faces: 40 identity classes x 10 (64x64). SECONDARY load_digits: 10 x 40.
- Each class = a near-orthogonal random bipolar referent word.
- Store binds TRAIN instances: `M = sum_{train} bind(word_class(img), image_code(img))`.
- Ground a HELD-OUT image (never bound): `i2w  q = M * code(x_heldout)` -> argmax cosine vs word
  codebook. Cross-instance held-out => CONTENT recognition (not rote code recall) drives the match.
- Also `w2i` (word -> held-out image among distractors).

## Two arms, ONE variable = image encoder front-end (everything downstream identical)
- CONTENT-BLIND `rung1_raw`: Kanerva record of grid intensities (the current grounding encoder, 29428).
- CONTENT-AWARE `rung3_hog`: specified glass-box HOG oriented-gradient shape front-end (29431).

## KEY MUST-FAIL discriminator (analog of the compgen sign-flip): GLOBAL PIXEL-SHUFFLE
ONE fixed permutation (SHUFFLE_SEED=424242) of the front-end input grid, applied identically to
EVERY image (train + held-out).
- CONTENT-BLIND raw: a consistent global permutation only RELABELS the random record positions ->
  inter-image similarity preserved -> grounding UNCHANGED (shuffle-INVARIANT).
- CONTENT-AWARE hog: destroys the spatial gradient locality HOG needs -> shape descriptor collapses ->
  recognition gone -> grounding COLLAPSES toward chance (shuffle-SENSITIVE).
Shuffle-sensitivity of BOTH arms = the load-bearing result. If content-aware is ALSO shuffle-invariant
=> not using content => honest negative.

## Design gate (all 4)
1. REAL baseline = content-blind raw grounding through the same bind store.
2. can-fail: content-features may not help beyond rote (aligned faces: raw pixels of one identity
   already correlate) OR both arms shuffle-invariant -> HONEST NEGATIVE reported. Genuine both ways.
3. difficulty-on: CROSS-INSTANCE held-out at 40 classes (olivetti chance=1/40=0.025); raw NOT
   saturated (prior LOO raw=0.79 MEASURED@data/exp_reader_image_shape_recognition_hog_v1/metrics.json).
4. ONE variable: encoder front-end (raw vs hog); split/words/store/retrieval identical.
Plus base-rate must-fail: class<->word SCRAMBLE -> grounding collapses to chance.

## Pre-registered bands (HYPOTHESIZED)
- AWARE_OVER_BLIND_MIN = 0.05  (hog i2w - raw i2w, clean)
- SHUFFLE_SENS_MIN = 0.15      (hog i2w clean - shuffled; content-aware must drop)
- SHUFFLE_INVARIANT_MAX = 0.08 (raw i2w clean - shuffled; content-blind ~invariant)
- SCR_COLLAPSE_MIN = 0.10      (hog i2w clean - wordscramble)
- STRONG_GROUND_MIN = 0.30     (hog i2w >= this = STRONG absolute)
- RAW_SAT_MAX = 0.95           (baseline_in_band flag)
- CHANCE_EPS = 0.03

Verdicts:
- PERCEPTION_MEANING_WIN/STRONG: aware>=blind+0.05 AND aware shuffle-sens>=0.15 AND blind shuffle-sens
  <=0.08 AND scramble collapses AND aware lift>chance.
- CONTENT_AWARE_NOT_USING_CONTENT: aware shuffle-invariant (honest negative).
- CONTENT_DOESNT_HELP_GROUNDING: aware no better than blind (honest negative).
- BOTH_SHUFFLE_SENSITIVE_ENCODER_NOT_ISOLATED / MIDDLE_BAND.

## Compute architecture
sequential-CPU (numpy). Justified: light (400 img, N=8192, 5 seeds, 2 arms, 2 conditions); wall < ~5min
full; no meaningful GPU speedup at this scale; the encoder/metric IS what is validated. Storage =
no_composition (single additive store; not a chained-retrieval cell). LOCAL foreground to completion.

## SCHEMA-VET
- arms_differ_verified: true (raw/hog codes bit-differ)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise before except Exception (no BaseException)
- crlb_n/a: grounding = held-out retrieval vs chance + shuffle-sensitivity contrast + scramble collapse
- baseline_in_band: content-blind raw i2w in (chance, RAW_SAT_MAX); flagged at smoke if saturated
- deterministic_seeding: true (fixed int seeds; SHUFFLE_SEED fixed; no hash()/list(set()))
- discriminator-fires (self_test): hog cross-instance grounding high + hog shuffle-sens > raw
  shuffle-sens + scramble collapses on a synthetic localized-shape set
- cardinality_ok: n/a (no sweep axis; fixed arms x seeds x conditions x 2 datasets)
- progress_logging: print_flush_true
- real_code_path: self_test constructs the REAL encoder + store + retrieval at tiny scale
- no external LLM; glass-box; local-only; not banked
