# Prereg: learner_implicative_sign_supplied_generalization_v1

Filed BEFORE running. Follow-up to banked 29490
(`exp_learner_implicative_negation_entailment_v1`), which showed the sign x negation XOR/XNOR
rule is real and beyond-linear on the SEEN-verb split, but held-out-VERB generalization was
structurally blocked because the feature encoding was one-hot VERB IDENTITY (`verb=<lemma>`),
which has zero cross-verb overlap by construction -- no fact could ever transfer across verbs
under that encoding, regardless of learner quality.

## The honest next step (this cell)

Replace the feature with the SUPPLIED per-verb implicative SIGN (`sign=pos|neg`, from
Karttunen 1971's published classification, already curated + gold-blind in
`tools/build_negation_factuality_gold.py:IMPLICATIVE_LEXICON`) + `neg=<True|False>`. This
feature has cross-verb overlap (multiple verbs share `sign=pos` / `sign=neg`), so held-out-verb
transfer is now structurally POSSIBLE -- the open question is whether the Learner module
actually COMPOSES it.

## Data-availability audit (MEASURED@ this run, BEFORE band-setting)

`tools.build_negation_factuality_gold.build_implicative_gold(maxtok=40)`: n=114 items, 9 verbs.
Joint (sign, negated) cell counts:
```
(pos, False)=25  [manage=19, bother=5, dare=1]
(pos, True) = 6  [bother=6 -- SOLE SOURCE, no other verb supplies this cell]
(neg, False)=60  [decline=7, avoid=15, fail=14, forget=21, neglect=2, hesitate=1]
(neg, True) =23  [avoid=2, fail=2, forget=9, hesitate=9, decline=1]
```
Leave-one-verb-out (LOVO) analysis: holding out ANY verb except `bother` leaves all 4 joint
cells populated by >=1 remaining verb (genuine sign-transfer test, cross-verb overlap does its
job). Holding out `bother` uniquely zeroes the `(pos, True)` cell entirely -- a categorically
HARDER test (extrapolation to a joint state with ZERO training exemplars anywhere), not a
"held-out verb with the fact transferable from elsewhere" test. These are pre-registered as TWO
DISTINCT metrics, not conflated:
- **COVERED subset**: LOVO test items whose own `(sign, negated)` cell has >= `MIN_CELL_COVERAGE`
  (3, matching `gam_plugin`'s own interaction min_coverage -- the actual mechanistic threshold
  for whether GAM's residual table has an entry) occurrences among the OTHER verbs in that fold's
  training set. This is the fair "sign fact supplied, verb held out, compose+generalize" test.
- **UNCOVERED subset**: LOVO test items whose own cell has ZERO such occurrences (structurally,
  only `bother`'s 6 negated items, per the audit above). Reported SEPARATELY as a harder,
  non-gating "extrapolate to a never-observed joint state" probe.

## Analytical (THEORETICAL) pre-registration of expected behavior

`gam_plugin.learn()` fits per-feature (main effect) Laplace log-odds PLUS a residual per co-
occurring PAIR, gated on `min_coverage` (default 3) instances of that EXACT pair in the fit data.
This means: on the COVERED subset, GAM has direct evidence for every joint cell (since coverage
was verified above) and should recover the TRUE joint table (interaction term = exact residual),
giving near-ceiling accuracy. On the UNCOVERED subset (bother-negated), GAM has ZERO instances of
the `(sign=pos, neg=True)` pair, so its interaction table has no entry there and the score falls
back to MAINS-ONLY (additive) -- which we compute by hand from the marginals above:
`P(REALIZED|sign=pos)=25/31=0.806`, `P(REALIZED|neg=True)=23/29=0.793` -- BOTH marginals point
toward REALIZED, so the additive fallback predicts REALIZED for `(pos,True)`, which is WRONG
(true label NOT_REALIZED). **THEORETICAL prediction: module accuracy on the UNCOVERED subset
~0%, matching the LINEAR arm's failure mode exactly** -- this is the honest, pre-registered,
structurally-forced expectation, not a rigged threshold. A parameter-free k=5 Jaccard SIMVOTE
faces the identical problem on the uncovered subset: its two nearest partial-match groups
(`sign=pos,neg=False` and `sign=neg,neg=True`) BOTH have majority label REALIZED, so SIMVOTE is
also expected to predict REALIZED (wrong) on the uncovered subset. **THEORETICAL: all three arms
converge near 0% on the uncovered subset -- this would NOT indicate "the sign fact is useless,"**
it indicates the module's compositional mechanism is associative/residual-table generalization
(needs >=1 direct joint exemplar), not symbolic rule application (which a human, told the
Karttunen definition explicitly, uses to solve this cell correctly with zero exemplars -- the
BRAIN-CHECK below).

On the COVERED subset, LINEAR (additive, max_interactions=0) is analytically expected to plateau
around `(60+25)/114 ~= 0.746` (recovers the 2 cells where each marginal happens to agree with the
majority direction; flips the other 2) -- a real, provable Minsky-Papert-style ceiling, not near-
zero, because the joint-cell sizes are imbalanced (this is why the HARD_FAIL linear ceiling below
is set at 0.80, not 0.55). SIMVOTE on the COVERED subset is analytically expected to ALSO reach
near-ceiling: with only 2 binary features, once all 4 joint cells are populated by ANY verb, an
exact-match k-NN is equivalent to a full joint-table lookup -- this is the "similarity trivially
solves it" risk the routing note itself flagged. **We pre-register this as a LIKELY outcome, not
a surprise, and define an explicit middle PASS tier (below) that reports it honestly instead of
forcing the margin-over-simvote gate to fail the whole cell.**

## Pre-registered bands (LIVE, BEFORE running)

### Positive control (mechanism sanity; gating)
`run_positive_control()` on synthetic XOR (registry auto-select) must choose `ruleind` or `gam`
with `compression_ratio > 1.0`. Failing this is `HARD_FAIL_MECHANISM` regardless of anything else.

### Primary gate -- COVERED-subset LOVO (the "supply the fact, compose, generalize" test)
- `HP_COVERED_ACC_MIN = 0.85`
- `HP_COVERED_MARGIN_LINEAR_MIN = 0.15` (module must decisively beat linear -- guaranteed
  achievable per the ~0.746 linear ceiling computed above; this is the core "beyond-linear"
  claim)
- `HF_COVERED_MARGIN_LINEAR_MAX = 0.05` (if module doesn't beat linear by at least this on the
  covered subset even though the sign fact IS supplied and the cell IS covered, that is a
  genuine deeper HARD_FAIL -- composition itself is broken, not a data-thinness artifact)
- `MIN_N_COVERED_TEST = 15` (feasibility floor)
- `SCRAMBLE_COLLAPSE_MIN = 0.25` (module accuracy under a scrambled verb<->sign permutation must
  collapse by at least this much relative to the true-sign covered-subset accuracy -- confirms
  the SUPPLIED sign fact, not some other correlate, is load-bearing)

### Similarity-margin sub-tiers (both pre-registered; NEITHER is post-hoc)
- **Tier A (decisive, beats both)**: `margin_module_simvote_covered >= 0.10` -> report as
  `HARD_PASS_COMPOSE_BEATS_LINEAR_AND_SIMILARITY`.
- **Tier B (beyond-linear only, similarity trivially solves via lookup)**:
  `margin_module_simvote_covered < 0.10` AND `acc_simvote_covered >= 0.85` -> report as
  `HARD_PASS_BEYOND_LINEAR_NOT_BEYOND_SIMILARITY` (still a genuine, pre-registered PASS on the
  core claim -- rule composes + generalizes beyond an additive readout given the supplied fact --
  but explicitly, honestly NOT a demonstration of beating similarity-based memorization at this
  task's tiny 2-feature cardinality; `is_similarity_near_chance_on_heldout = False` reported).
- If `margin_module_simvote_covered < 0.10` AND `acc_simvote_covered < 0.85` (similarity ALSO
  fails to solve it, i.e. genuinely near chance) but module still clears `HP_COVERED_ACC_MIN` and
  `HP_COVERED_MARGIN_LINEAR_MIN`: report as Tier A' `HARD_PASS_COMPOSE_BEATS_LINEAR_AND_SIMILARITY`
  (similarity near-chance counts as "beaten," a stronger result than Tier A's numeric margin
  alone would suggest).

### Non-gating, separately reported -- UNCOVERED subset (bother-negated, n=6)
`unseen_joint_cell_extrapolation`: `PASS` if `acc_module_uncovered >= 0.80`, else
`BOUND_CONFIRMED_ASSOCIATIVE_NOT_SYMBOLIC` (the pre-registered, analytically-expected outcome --
see Analytical section above). This does NOT gate the overall verdict; it is reported as a
distinct, harder finding about the learner's generalization MECHANISM (residual-table /
similarity-lookup vs symbolic rule application).

## BRAIN-CHECK (pre-registered, not post-hoc)

Given the Karttunen classification EXPLICITLY as a symbolic definition ("V(X) entails X" etc,
not induced from exposure), a human WOULD compute `bother`'s negated entailment correctly with
zero exposure to that exact combination, by applying the definitional rule directly -- this is
symbolic composition, not associative recall. If the module's uncovered-subset accuracy lands
near 0% (as analytically predicted), that is NOT a brain-shared bound -- it indicates the current
learner architecture (GAM residual tables, k-NN similarity) implements associative/statistical
generalization, not explicit symbolic rule application over the supplied fact. This is an honest,
mechanism-level finding to report, distinct from the covered-subset result.

## Controls
- Positive control: synthetic mini-XOR (module must choose ruleind/gam, `compression_ratio>1.0`).
- Scramble control: verb<->sign permutation (SCRAMBLE_SEED=770321, fixed int, not hash()-derived).
- `arms_differ_verified`: hash test over covered-subset predicted-class tuples (linear/simvote/
  module must not be bit-identical).
- Deterministic seeding: `random.Random(fixed_int)` + `sorted(set())` only; no `hash()`-seeded
  RNG or ordering (PROT-023).

## Compute architecture
Class (b) sequential-CPU. n=114 real items, closed-form counting/log-odds/rule-search. No torch,
no matmul. Wall time sub-second. LOCAL-ONLY, foreground-to-completion, NO queue, NO push, NO
remote-persist, NO hdlab mutation, NO atom bank (skunkworks VETs this).

## Cell-template mandatory subset (applicable to this local measurement cell)
- `arms_differ_verified` at self-test + full.
- `final_metrics_atomicity`: tmp_replace (os.replace).
- `except SystemExit/KeyboardInterrupt: raise` BEFORE `except Exception` (no BaseException).
- `crlb_n/a`: accuracy/compression-ratio measurement, not a capacity/CRLB-bound cell.
- `baseline_in_band`: n/a (LINEAR/SIMVOTE are the discriminating baselines under test).
- `discriminator survives scale`: n/a (fixed real-data n=114).
- `cardinality_ok`: EXPECTED_N_UNITS=1 (single real-data fit + synthetic control + scramble
  control; no seed/sweep axis).
- `calibration_check`: default_ok_for_this_regime (MDL two-part code, module-wide formula).
- `deterministic_seeding`: true.
- All numbers in the cell docstring/comments tagged MEASURED@ / THEORETICAL@ / CITED@.
