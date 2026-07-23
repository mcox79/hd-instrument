# PRE-REG: vision_integrated_recognize_bind_ground_v1 (2026-07-23)

## Purpose
Assemble the THREE separately-validated, never-chained vision pieces into ONE glass-box pipeline on
REAL images (sklearn `load_digits`, real 8x8 photos upscaled to 32x32), and add the genuinely can-fail
NOVEL-CATEGORY probe the prior audit flagged as never tested (every prior "held-out" test was a
held-out INSTANCE of a KNOWN class; no cell ever held out a whole CLASS from training/binding).

Pieces reused (imported as modules, functions called, NOT copy-pasted where avoidable):
- `exp_reader_image_shape_recognition_hog_v1` (HG): HOG front-end (`feat_hog`), real dataset loader
  (`load_digits_up`), Kanerva content encoder (`GB.encode_record` etc via `HG.GB`).
- `exp_grounding_attn_bind_illusory_conjunction_v1` (ATN): FHRR bind/unbind/cleanup, attention-gated
  scene encoder (`encode_scene` ATTN/FLAT/SCRAM), illusory-2AFC + color-of-shape readouts, feature
  extractors `color_feature`/`shape_feature` (dimension-and-content agnostic; reused verbatim on REAL
  tinted photographic windows instead of synthetic drawn shapes).
- `exp_grounding_attn_bind_incremental_curve_v1` (INC): `ProtoStore` running-mean prototype classifier
  (the improving-with-exposure front-end).
- `exp_reader_perception_meaning_grounding_v1` (GRD) + `_sharded_v1` (GRDSH): `random_words`,
  `build_store_sharded`, `i2w_heldout_sharded` (the per-class sharded store that recovered the
  perception-meaning grounding lift the additive store lost to crosstalk, atom 29438/lift+0.123).

## Design (honest framing)
This is an INTEGRATED BATTERY sharing one real dataset + one class ontology + one train/test split
across all three mechanisms, chained PER-OBJECT: a real digit photo is (a) tinted with a jittered
color (independent 2nd feature, Treisman-fair: two parallel feature maps, color + shape/identity),
placed in a multi-object scene; (b) RECOGNIZED via `ProtoStore` running-mean shape-prototype argmax
on the real-pixel HOG descriptor of that window; (c) BOUND via an attention spotlight (ATTN arm) vs a
pre-attentive FLAT arm (illusory conjunctions) vs a SCRAM anti-cheat (wrong-location attention); (d)
GROUNDED by taking that SAME real instance's own whole-image HOG content code (independent encoder,
matches the validated grounding pipeline) and querying the SHARDED word store built only from TRAIN
instances of the SEEN classes. This is NOT a single differentiable forward pass (no such thing exists
in this glass-box project) -- it is 3 validated glass-box measurements composed over the same object,
each with its own discriminator, which is the honest and correct way to "integrate" inspectable VSA
mechanisms. Reported explicitly this way to avoid over-claiming a tighter coupling than what is built.

## Dataset / split
sklearn `load_digits` (real 8x8 photos, ~174-183 per class, upscaled to 32x32 via `HG.load_digits_up`).
SEEN_CLASSES = digits 0-7 (8 classes). NOVEL_CLASSES = digits 8-9 (2 classes), held out ENTIRELY from
ALL training/binding (ProtoStore exposures, grounding-store shards) -- used ONLY in the novel-class
probe. Per-seen-class: first `k_train_seen` instances -> train pool (exposures + grounding train
split); remainder -> held-out TEST pool (used for ALL headline evaluation: recognition, binding,
grounding). Deterministic first-k split (no shuffling of instance order; matches `GRD.split_masks`
convention).

## Compute architecture
(b) sequential-CPU with justification: per-object/per-scene loops over a few hundred real 32x32 images
per seed; each op (HOG on a 32x32 window, cosine scoring against <=8 shards/prototypes) is
microseconds; estimated wall time smoke ~20-40s, FULL ~2-4 min (5 seeds) -- CPU-sequential is
appropriate (this is NOT a matmul-heavy batchable primitive workload; it is a small glass-box
diagnostic battery). INLINE-LOCAL per USER instruction (no remote/GPU -- avoids an unauthorized origin
push).

Storage strategy: SHARDED (per-class store `build_store_sharded`/`i2w_heldout_sharded`) is the ONLY
grounding-store structure used (per task instruction: "use the sharded/sparse fix"; the additive-store
null result is already banked at 29438/atom cited in the sharded cell and not re-litigated here).

## Bands (pre-registered BEFORE running; HYPOTHESIZED unless marked)

### Headline: integrated pipeline on HELD-OUT INSTANCES of KNOWN (seen) classes
- FRONT_RECOG_HP = 0.75 / FRONT_RECOG_HF = 0.30 (ProtoStore shape-argmax on held-out test images,
  forced 8-way, chance=0.125). HYPOTHESIZED@HG recognition cell LOO acc1=0.969 digits (40/class);
  expect somewhat lower under a smaller 81-dim window descriptor + color-tint noise but comfortably
  above floor.
- GROUND_HP = 0.30 / GROUND_HF = 0.175 (sharded hog i2w on held-out seen-class test images,
  chance=0.125). HYPOTHESIZED@GRDSH STRONG_GROUND_MIN convention (0.30), reused directly.
- BIND_ILL_HP = 0.75, BIND_MARGIN_HP = 0.15, BIND_FLAT_MAX = 0.62, BIND_SCRAM_MAX = 0.66,
  BIND_ILL_HF = 0.60 (illusory-2AFC, chance=0.5, vocab-size-independent). HYPOTHESIZED@prior
  ATTN/INC cells measured ATTN 0.815-0.833 vs FLAT 0.515-0.521; banded conservatively below that for
  regime drift (real photographic identity content vs synthetic drawn shapes).
- WORD_SCRAMBLE_COLLAPSE_MIN = 0.10 (sharded hog clean - wordscramble, chance=0.125-based).
- LABEL_SHUFFLE_MAX = 0.30 (front-end recognition under shuffled prototype labels must collapse
  toward chance=0.125).
- END_TO_END_HP = 0.55 / END_TO_END_HF = 0.20 (composite per-object: RECOGNIZE correct AND GROUND
  correct, on held-out seen-class instances). HYPOTHESIZED as an approx product of the two component
  rates (0.75 x 0.75 ~ 0.56).

HP_SCOPE: {ATTN: [BIND_ILL_HP, BIND_MARGIN_HP], FLAT: [BIND_FLAT_MAX], SCRAM: [BIND_SCRAM_MAX],
recognition: [FRONT_RECOG_HP, LABEL_SHUFFLE_MAX], grounding: [GROUND_HP, WORD_SCRAMBLE_COLLAPSE_MIN]}
(FLAT/SCRAM/label-shuffle/word-scramble are must-fail-control arms; they do NOT inherit the
ATTN/recognition/grounding HARD_PASS gates.)

### Novel-category probe (calibration probe, no prior empirical anchor; THEORETICAL null, not a blind
guess -- so banded around the theoretical no-signal point rather than the generic +/-50% HYPOTHESIZED
rule, per the "theoretical prediction" allowance)
- NOVEL_RECOG_ACC_MAX = 0.05 and NOVEL_GROUND_ACC_MAX = 0.05: structural sanity checks (forced-choice
  accuracy on a class with NO prototype/shard is mathematically ~0; if measured above this, flag
  LEAKAGE_SUSPECT, not a capability finding).
- NOVEL_SCORE_GAP (grounding-level) = mean(best-WRONG-shard score on seen held-out test, excluding
  true class) - mean(best-shard score on novel-class instances, forced into the 8 seen shards).
  THEORETICAL@null-hypothesis (plain cosine shard readout has no explicit open-set/novelty mechanism)
  predicts gap ~ 0 (a novel-class query's best "wrong-class" match should score like any other
  wrong-class match). Bands: |gap| <= 0.05 => WALL_CONFIRMED (the expected, live negative: the system
  cannot tell a genuinely novel category from an ordinary wrong-class mismatch); gap >= 0.10 =>
  SURPRISE_NOVELTY_SIGNAL (an interesting positive deviation, not required, not the expected outcome);
  0.05 < gap < 0.10 => MIDDLE_BAND_WEAK_SIGNAL.
- NOVEL_SHAPE_SCORE_GAP: same band structure (0.05 / 0.10) applied to the ProtoStore shape-prototype
  score gap (recognition-level analog of the grounding-level gap above).

CRLB_n/a: discriminators are (i) forced-choice accuracies vs analytic chance, (ii) a 2AFC vs chance
0.5, (iii) score-gap contrasts vs a theoretical null of 0; none is a closed-form noise-floor cap.

## Anti-cheat / must-fail controls (ALL must fire before the headline is trusted)
- FLAT (pre-attentive, no attention binding) illusory-2AFC near chance.
- SCRAM (attention points at wrong object) illusory-2AFC collapses to ~FLAT.
- LABEL-SHUFFLE (ProtoStore prototypes filed under permuted class labels) recognition + downstream
  binding collapse toward chance.
- WORD-SCRAMBLE (class<->word assignment permuted before building the grounding store) i2w collapses.
- arms-must-differ (META_RULE_AF): ATTN/FLAT/SCRAM scene-rep hashes differ; raw-vs-hog grounding codes
  differ.

## Multi-seed / smoke discipline
SMOKE uses the SAME HD dims (N_scene=1536, N_ground=4096) and SAME class count (8 seen + 2 novel) and
SAME M-sweep [2,3,4] as FULL (per DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C) -- only per-class
instance count (16 vs 40), scene count, and seed count (2 vs 5) are reduced for speed. FULL = 5 seeds
[7,13,17,23,29]. WALK-BACK GATE: if smoke effect size is borderline (any headline gap within 20% of its
HARD_PASS threshold), double FULL n_scenes before shipping (recorded at ship time in the completion
report, not pre-committed here since it is smoke-contingent).

## Deterministic seeding
All RNGs are `np.random.default_rng(<fixed int>)`. No `hash()`-seeded RNG, no `list(set(...))`
ordering. Static scan (`assert_no_nondeterministic_seeding`) run in `self_test()`.

## LOCAL ONLY
No push, no remote-persist, no atom banking by this agent (skunkworks VETs + banks per role
separation). INLINE-LOCAL FULL dispatch via `local_cpu_queue` (pure numpy/sklearn, CPU).
