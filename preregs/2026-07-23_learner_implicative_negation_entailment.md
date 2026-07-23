# Pre-registration: learner_implicative_negation_entailment_v1

**Filed:** 2026-07-23, BEFORE the FULL run. Data-availability counts (item counts per verb/negation
cell) were inspected to choose a feasible split -- this is NOT the same as peeking at the
discriminator outcome (accuracy numbers); see "Data-availability audit" below for the exact
numbers that were known before band-setting.

## Task

Real, non-construction-favorable UD-EWT-mined implicative-verb x negation entailment. Karttunen
(1971) implicative-verb classification (CITED, externally published): positive implicatives
(V(X) entails X; NOT-V(X) entails NOT-X) vs negative implicatives (V(X) entails NOT-X; NOT-V(X)
entails X). Gold label = the Karttunen truth table applied to (verb polarity_class, Polarity=Neg
scoping the matrix verb) -- a genuine XNOR/parity interaction (Minsky & Papert 1969 CITED: not
linearly separable in the two raw cues).

Mined via `tools/build_negation_factuality_gold.py` extension (`find_implicative_items` /
`build_implicative_gold` / `write_implicative_gold`), lexicon = {manage, bother, dare (pos);
fail, forget, neglect, avoid, hesitate, decline (neg)}; `get`/`happen`/`refrain` excluded
(ambiguous or zero-incidence at maxtok=40). Gold artifact:
`data/gold_implicative_negation_ewt_v1/gold_implicative_negation_ewt_v1.json`.

## Data-availability audit (MEASURED@ this cycle, counts only, before any accuracy is computed)

n=114 items total (29 negated, 85 affirmative) across 9 verbs (dare has n=1, kept but never
tested alone). Per (verb, negated) cell:
```
avoid    aff=15 neg=2    (neg-impl)
bother   aff=5  neg=6    (pos-impl)  <- ONLY pos-impl verb with negated instances at all
dare     aff=1  neg=0    (pos-impl)
decline  aff=7  neg=1    (neg-impl)
fail     aff=14 neg=2    (neg-impl)
forget   aff=21 neg=9    (neg-impl)
hesitate aff=1  neg=9    (neg-impl)
manage   aff=19 neg=0    (pos-impl)  <- zero negated occurrences in the entire corpus
neglect  aff=2  neg=0    (neg-impl)
```

**Data limitation flagged explicitly:** `bother` is the ONLY verb with any pos-implicative
negated instances (6 of them). This forces a design choice below.

## Splits (decided from the counts above, before computing any accuracy)

**SEEN-verb split** (primary discriminator): item-level stratified 70/30 by (verb_lemma,
negated), sorted keys + fixed seed (no `hash()`), ALL 9 verbs included (bother's 6 pos-impl-neg
items stay in this pool so both classes' negated cells are represented in train -- required for
the linear-model contradiction argument below to bite).

**HELD-OUT-VERB split**: `avoid` and `hesitate` held out entirely (both neg-impl, n=17+10=27,
11 negated + 16 affirmative combined) from a model trained on the remaining 7 verbs
(`manage, bother, fail, forget, decline, neglect, dare`, n=87, includes bother's 6 negated
pos-impl items in training). **Scope caveat (declared before running):** because `bother` is the
sole pos-impl-negated source, held-out verbs are necessarily both neg-impl-class -- this tests
generalization to an unseen member of the MAJORITY class, not symmetric both-class transfer.
Flagged honestly, not hidden post-hoc.

## Why this is provably beyond-linear given the ACTUAL observed data (not just synthetic XOR)

For an additive/linear model over one-hot verb features + a single shared negation weight
(score = intercept + w_verb + w_neg*neg), fitting `bother` (pos-impl: neg=0->REALIZED,
neg=1->NOT_REALIZED, needs w_neg very NEGATIVE relative to bother's bias) and `forget`
(neg-impl: neg=0->NOT_REALIZED, neg=1->REALIZED, needs w_neg very POSITIVE relative to forget's
bias) SIMULTANEOUSLY is impossible with ONE shared w_neg (THEORETICAL, derived here, not cited) --
a real, data-grounded (not merely hypothetical) linear-separability failure, because both verbs'
negated cells are populated in the real mined data.

## Arms

- **ARM_LINEAR**: `gam_plugin.learn()` with `max_interactions=0` (pure additive mains: intercept +
  per-verb-feature log-odds + per-neg-feature log-odds, no pairwise term) -- a genuine linear/
  log-linear readout over the same two feature families.
- **ARM_SIMVOTE**: parameter-free Jaccard-similarity k=5 majority vote over feature sets (no
  learned parameters).
- **ARM_MODULE**: `hdlab.learner.registry.learn()` fed all 3 plugins (estimation with
  `key_fn=verb_lemma` alone [fair "weak" single-cue candidate per the module's own documented
  design]; ruleind with `max_conjunct=2, min_coverage=2, purity_thresh=0.85`; gam with full
  interactions allowed, `min_coverage=2`) -- auto-selects via MDL compression. Reported: chosen
  plugin name + compression ratios of all 3 candidates.

Feature encoding for ALL arms: `feat_fn(inst) = ["verb=<lemma>", "neg=<True|False>"]` --
deliberately NOT handed polarity_class directly.

## Pre-registered bands (BEFORE running)

**Positive control (mechanism check, synthetic mini-XOR, run first):** `registry.learn()` on a
20-per-quadrant synthetic XOR(a,b) task MUST auto-select ruleind or gam (NOT estimation) with
compression_ratio > 1.0. If this fails, the module itself is broken -- do not trust it on the
real (thin) data; HARD_FAIL_MECHANISM.

**HARD_PASS_SEEN** (the core grow-thrust discriminator) iff ALL of:
  (a) ARM_MODULE auto-selects ruleind or gam (NOT estimation, NOT KEEP_EPISODIC) on the real task.
  (b) ARM_MODULE SEEN-verb test-split accuracy >= 0.85.
  (c) ARM_MODULE beats ARM_LINEAR by >= 0.20 absolute AND beats ARM_SIMVOTE by >= 0.20 absolute
      on the SEEN-verb test split.
  (d) Scramble control (verb<->polarity_class permutation, fixed deterministic shuffle, NOT
      `hash()`-seeded): ARM_MODULE's SEEN-verb accuracy collapses by >= 0.25 absolute vs the
      real-labeled run.

**HARD_FAIL_SEEN** iff ARM_LINEAR already clears >= 0.80 on the SEEN-verb split (verb-identity
leaks the class near-losslessly at the feature level actually used -- same failure mode as
PP-attach), OR ARM_MODULE does not beat ARM_LINEAR+ARM_SIMVOTE decisively despite a clean
mechanism control, OR n_seen_test < 15 (data too thin to trust the split).

**HELD-OUT-VERB generalization (separate, harder bar, reported honestly regardless of direction):**
  - HARD_PASS_HELDOUT iff ARM_MODULE held-out-verb accuracy >= 0.65 AND beats
    ARM_LINEAR/ARM_SIMVOTE by >= 0.15 on held-out verbs.
  - **Expected/pre-registered HARD_FAIL_HELDOUT (analytically anticipated, stated BEFORE running,
    not an ex-post excuse):** because verb-identity is one-hot, held-out verbs share ZERO feature
    overlap with any training verb -- ALL feature-conjunction-based arms (LINEAR, RULEIND, GAM,
    SIMVOTE) structurally degenerate to the SAME marginal-negation-conditioned baseline on
    held-out items (no cue exists that could transfer specifically FROM verb identity). If this
    is what happens, it is a REPRESENTATION-level bound (implicative-verb polarity is a genuine
    lexically-stored fact, not a productive rule over verb *form*), not a nonlinear-learner
    deficiency -- report the margin-collapse explicitly, this is the informative case, not a
    disqualifying one.
  - **BRAIN-CHECK (stated before running):** Karttunen's classification is itself a closed LEXICAL
    inventory, not a compositional/phonological rule -- there is no independent evidence humans
    guess a novel verb's implicative polarity from surface form alone; per-verb lexical storage
    (not blind productive generalization) is the expected human account too. A held-out-verb
    HARD_FAIL under this design is therefore expected to be a brain-shared bound, not a substrate
    deficiency, UNLESS ARM_MODULE's margin over LINEAR/SIMVOTE also collapses to ~0 on held-out
    (which would confirm the structural-bound account) vs. staying positive-but-below-threshold
    (which would suggest a milder power/data issue, not a hard representational wall).

**Overall verdict tiers:**
  - `HARD_FAIL_MECHANISM` -- positive control fails; do not trust the real-data result.
  - `HARD_PASS_LEARNER_CLASS_HELPS_SEEN_AND_HELDOUT` -- HARD_PASS_SEEN + HARD_PASS_HELDOUT.
  - `HARD_PASS_SEEN_HELDOUT_BOUND` -- HARD_PASS_SEEN but held-out fails per the analytically-
    anticipated representational bound (the grow-thrust payoff on real seen data, with an honest,
    pre-anticipated held-out caveat).
  - `HARD_FAIL_TASK_IS_LINEAR_OR_SIMILARITY_SHAPED` -- HARD_FAIL_SEEN condition met.
  - `MIDDLE_BAND` -- anything else (e.g. SEEN passes (a)+(b)+(d) but margin in [0.05,0.20), or
    n_seen_test in [15, threshold) borderline).

## Controls (load-bearing)

- Positive-control mechanism check (synthetic XOR, module auto-selects nonlinear).
- Scramble control (verb<->class permutation; deterministic, NOT `hash()`-seeded).
- arms_differ hash check (LINEAR vs SIMVOTE vs MODULE-chosen predictions on the same eval set
  must not be bit-identical).
- Held-out-verb split guards circularity (verb-identity memorization) directly.

## Compute architecture

Class (b) sequential-CPU, n=114 total items, closed-form counting/log-odds/rule-search only (no
matmul, no torch). Wall time: sub-second. LOCAL-ONLY, foreground-to-completion, no queue, no push,
no remote-persist, no hdlab mutation, no atom bank (skunkworks VETs). Deterministic:
OMP/MKL/OPENBLAS_NUM_THREADS=1, `random.Random(fixed_int_seed)` / `sorted(set(...))` only, no
`hash()`-seeded RNG or ordering.

## Cell-template declarations

- `cell_chunked`: false (single-seed-equivalent; deterministic, no seed sweep -- task is not
  seed-sensitive, it's a fixed real-data mining + fit).
- `arms_differ_verified`: true (hash check at self-test + full).
- `final_metrics_atomicity`: tmp_replace.
- `except SystemExit/KeyboardInterrupt: raise` BEFORE `except Exception`.
- `crlb_n/a`: accuracy/compression-ratio measurement, not a capacity/CRLB-bound cell.
- `baseline_in_band`: n/a (no saturating baseline arm in the METa_RULE_AG sense; SIMVOTE/LINEAR
  ARE the discriminating baselines under test, not architecture-floor sentinels).
- `discriminator survives scale`: n/a (fixed real-data n=114, not a scale-swept cell).
- `cardinality_ok`: EXPECTED_N_UNITS = 1 (single real-data fit + 1 synthetic control + 1 scramble
  control; no seed/sweep axis).
- `calibration_check`: default_ok_for_this_regime (MDL two-part code, same formula module-wide).
- `deterministic_seeding`: true.
- `progress_logging`: n/a (sub-second wall).

All numbers in this prereg tagged: counts above = MEASURED@ this cycle's mining run; theoretical
argument = THEORETICAL (derived above); Karttunen/Minsky-Papert = CITED (see research note).
