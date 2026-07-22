# Pre-reg: reader_image_content_recognition_v1

Date: 2026-07-21
Author: hdi_exp_dev (dispatched by Director)
Local-only. No push, no remote-persist, no store mutation, no atom banking (Skunkworks VETs on land).

## Question (not an assertion)

The grounding brick (`exp_reader_image_word_grounding_v1`, commit 4ab64c095) established that the
McGuffey illustration<->word association pipeline works but is perception-BINDING not
perception-MEANING: keyed retrieval survived pixel-scramble because the WORD-KEY does the work
(content-blind is fine when a key isolates). It also found a glass-box content SEPARATOR:
off-diagonal cosine raw=0.252 vs ink-mask(Otsu)=0.092 vs edge=0.511 (edge BACKFIRED on woodcut
hatching). MEASURED@data/exp_reader_image_word_grounding_v1/metrics.json:rungs.*.img_offdiag_cosine_mean.

THIS cell tests the distinct, harder claim: KEYLESS content-based RECOGNITION. Given an
illustration's HD encoding, retrieve/predict its referent BY IMAGE CONTENT with NO stored word-key
-> the image's content must determine the answer. This is where content-sensitivity actually
matters: raw-pixel (content-blind, background-dominated) should be near-chance; ink-mask
(content-sensitive) is the test. If ink-mask also fails, that is the honest signal that glass-box
woodcut recognition needs MORE (resonator scene-factoring or a black-box feature extractor).

## Referent-class structure (fair, specified, glass-box)

Multi-instance referent classes derived from McGuffey nearby-text via a SPECIFIED filter:
a word is a referent class iff its PRIMARY (most-frequent) WordNet sense is a depictable physical
object (lexname in {noun.animal, noun.artifact, noun.food, noun.plant, noun.body}). This "primary
sense" rule removes most function-word/adjective noise that only has obscure SECONDARY concrete
noun senses (the loose "any noun synset" filter passed come/good/work/white/black). Label noise is
INTRINSIC to OCR nearby-text and cannot be fully removed (still leaks come/still/back/john) -> this
is reported as an honest bound, NOT curated away.

- PRIMARY class set: primary-depictable, K_MIN=2 -> 43 classes over 56 images (128 img-class instances).
  MEASURED@inline-probe. chance(NN-shared perm-null)=0.107.
- SECONDARY (sensitivity): K_MIN=3 (18 classes, 47 imgs); ANIMAL-only primary-sense (10 classes,
  23 imgs; FLAGGED small-N/noisy, reported not headline).

Class sets and filter are declared BEFORE the run and are NOT selected by which gives best accuracy.

## Encoder arms (ONE variable = image front-end)

Reuse the grounding brick's IDENTICAL Kanerva record encoder + Rahimi/Kleyko thermometer levels
(atom 29407 recipe). Three front-ends, headline = raw vs ink:
- rung1_raw : raw grayscale resized (content-blind negative control; background-dominated).
- rung2_edge: Sobel edge (reference; backfired on hatching in the grounding brick).
- rung2b_ink: global-Otsu binary ink mask (content-sensitive; THE test arm).
positions/levels/quantization/retrieval identical across arms; only the front-end differs.

## Keyless recognition protocol (NO word-key; content determines the answer)

PRIMARY metric -- NN-SHARED-REFERENT (robust to tiny per-class N):
  for each image, find its NEAREST OTHER image by CONTENT cosine (encode->cosine, no key);
  score = fraction of images whose nearest content-neighbor shares >=1 depictable referent class.
  chance = permutation-null (mean shared-referent rate over 200 random-neighbor permutations).
  This directly asks: does image CONTENT group woodcuts by referent?

SECONDARY metric -- LEAVE-ONE-OUT CLASS PROTOTYPE (cross-instance generalization, harder):
  for each image i and class c, proto_c = sign(sum encode(j) for j in c, j != i) (bundle of OTHER
  instances). Predict argmax cosine(encode(i), proto_c). Multi-label: correct if any true class of
  i is top-1 (acc1) / top-3 (acc3). Genuinely keyless AND held-out (i never in its own prototype).
  operative chance = label-scramble acc1 (see must-fail).

## MUST-FAIL controls (the discriminator the grounding brick lacked)

1. CONTENT-SCRAMBLE (per-image pixel/level shuffle, independent permutation per image): destroys
   spatial content, keeps only the level MULTISET. Keyless content-recognition MUST collapse toward
   chance (keyed retrieval survived scramble via the key; keyless must NOT). Applied per-arm.
2. LABEL-SCRAMBLE (shuffle class membership): prototypes built from RANDOM images -> LOO recognition
   MUST collapse to chance. Confirms the LOO signal uses true class structure.

## Design-gate (pre-registered)

- REAL baseline = perm-null chance + raw-pixel content-blind negative control (if raw ALSO recognizes
  by content, the test is broken/leaky).
- CAN-FAIL = ink NN-shared at chance is an HONEST NEGATIVE (glass-box ink recognition doesn't work on
  woodcuts -> strategic fork: resonator scene-factoring or black-box extractor).
- DIFFICULTY-ON = keyless, real illustrations, cross-instance held-out (LOO), multi-object scenes.
- ONE VARIABLE = image front-end across arms.
- Multi-seed (HD codebook seed): 5 full, 2 smoke. GLASS-BOX (Otsu threshold + specified features, no
  learned CNN). Deterministic seeding (fixed int seeds; no hash()/list(set())).

## Pre-registered bands (PRIMARY set, NN-shared; chance ~0.107 measured perm-null)

- CHANCE_EPS = 0.03 (within chance+eps => at chance)
- INK_LIFT_MIN = 0.05      (ink_nn - chance >= this, robust mean-std, for content-sensitivity)
- INK_OVER_RAW_MIN = 0.03  (ink_nn - raw_nn >= this: ink beats content-blind control)
- SCR_COLLAPSE_MIN = 0.03  (ink_clean_nn - ink_scramble_nn >= this: recognition is content-driven)
- RAW_CONTENT_BLIND_MAX = 0.05 (raw_nn - chance <= this: raw is the content-blind control)
- STRONG_RECOG_MIN = 0.30  (ink_nn >= this = STRONG clean recognition; HYPOTHESIZED unlikely)

Tiered verdict (strictly-above-floor per META_RULE_L; band-floor => MIDDLE_BAND):
- GLASSBOX_RECOG_STRONG: ink_nn >= STRONG_RECOG_MIN and all content-sensitivity gates pass.
- GLASSBOX_RECOG_CONTENT_SENSITIVE (weak-but-real, the LIKELY landing per probe): ink_lift >=
  INK_LIFT_MIN (robust) AND ink_over_raw >= INK_OVER_RAW_MIN AND scr_collapse >= SCR_COLLAPSE_MIN
  AND raw is content-blind. Confirms ink content-sensitive, raw content-blind, content-driven; but
  absolute recognition weak -> un-stalls direction, flags strategic fork for STRONG.
- RECOG_AT_CHANCE (honest negative): ink_lift < CHANCE_EPS -> glass-box ink recognition fails on
  woodcuts -> strategic fork (resonator / black-box extractor).
- MIDDLE_BAND: signal present but one gate short (e.g. scramble doesn't fully collapse, or ink not
  robustly above raw).

HYPOTHESIZED landing (from 5-seed inline probe, MEASURED@scratchpad probe, NOT the cell):
ink_nn~0.179 raw_nn~0.125 chance~0.107 ink_scr~0.136 -> GLASSBOX_RECOG_CONTENT_SENSITIVE.

## Compute architecture

Class: (b) sequential-CPU with justification. n_img=56, N=10000, numpy; full run < ~90s wall.
Per-primitive matmuls are tiny (56x56 cosine, 56x43 prototypes); GPU batching buys nothing at this
scale and the encoder IS the glass-box primitive under test. Storage: no_composition / no chained
retrieval (prototypes are single-level bundles, no multi-hop) -> bundled-bundle acceptable
(semantic-gist prototype, explicitly the mechanism). run FULL locally, foreground to completion.

## Cell-template mandates

- arms_differ_verified (raw/edge/ink codes bit-differ) at self_test.
- final_metrics_atomicity = tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: recognition = NN-shared/LOO vs perm-null chance + scramble collapse, not a noise-floor cap.
- baseline_in_band: raw is the content-blind control near chance; perm-null chance is the floor; the
  scramble + label-scramble controls are the AG-style discriminator-fires gates.
- deterministic_seeding: fixed int seeds only (source-scanned by validity preflight).
- discriminator-fires: self_test asserts on synthetic (shared foreground on random background) that
  ink NN-shared > raw NN-shared and that per-image scramble collapses recognition.
- progress_logging: print_flush_true (cell < 90s; flush anyway).
- defensive_error_checking: start_marker + crash_diagnostic present; heartbeat exempt (single-process,
  < 90s wall, foreground).
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
