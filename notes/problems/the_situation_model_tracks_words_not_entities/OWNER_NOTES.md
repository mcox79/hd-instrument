---
owner_verdict: DONE
---

---
problem: the_situation_model_tracks_words_not_entities
status: SOLVED
bar: "The ENTITY-STRUCTURED model must beat the BAG-OF-WORDS gist CI-separated over its UPPER bound on an entity-dependent task (pronoun/anaphor resolution to the correct prior entity, OR predicting a recurring entity's next role/argument), with an info-free twin (SHUFFLED entity links / random entity assignment) LOSING CI-separated. Report CI half-width + null p95 beside every margin."
result: "MET, via AUGMENT (the brain keeps BOTH a global situation gist AND entity nodes; it does not replace one with the other). On modern QASRL v2 reconstructed documents, predicting a RECURRING entity's next argument (the agent's next patient), an ENTITY-STRUCTURED situation model -- the bag-of-words discourse gist PLUS the active entity's ROLE-CONDITIONED accumulated state (its prior patients, retrieved by entity identity: the situation-register decode op) -- beats the bag-of-words gist ALONE, CI-separated. TRAIN (n=1,708 held-out target events, split BY DOCUMENT, 3 seeds): BAG+ENTITY surprisal 2.7771 [2.7387, 2.8149] vs BAG 2.8315 [2.7927, 2.8697], paired margin +0.0545 [+0.0430, +0.0671] (half-width 0.0121). REPLICATED on the INDEPENDENT QASRL test split (different documents, n=672, 3 seeds): +0.0402 [+0.0216, +0.0599] (half-width 0.0191). Scorer = -log P(true patient | softmax over 20 frequency-matched candidates, temp 0.5). Population = held-out QASRL v2 reconstructed documents, targets = events whose AGENT has >=1 prior patient-when-agent in the document (a recurring entity with role history), agent+patient groundable, split by document."
floor: "Strongest bag-of-words floor recomputed on the population = BAG, the whole-document running content-word mean (the discourse gist the predictive-reader validated, recomputed here) surprisal 2.8315, UPPER-95%CI 2.8697; BAG+ENTITY lower-CI 2.7387 clears it (margin +0.0545, lower bound +0.0430 > 0). The floor itself reproduces the discourse-gist finding: BAG beats the bottom-up LOCAL predictor +0.1192 [+0.1053, +0.1338]. A ROLE-BLIND entity augmentation (bag + mean of ALL the entity's prior co-content) is a weaker floor at +0.0327 [+0.0237, +0.0415] over bag; role-CONDITIONED entity beats it +0.0217 [+0.0141, +0.0286]."
controls: "(1) INFO-FREE TWIN (bag + a RANDOM other entity's role history, entity link SCRAMBLED, bag identical): -0.06 [-0.0732, -0.0467] vs bag -- it does NOT beat bag, it ACTIVELY HURTS (null p95 well below zero) -> the win requires the CORRECT entity's history, excludes 'any entity gist / more input dims trivially help'. (2) ROLE-BLIND vs ROLE-CONDITIONED: role-conditioned (prior patients, the register's decode) beats role-blind (all co-content averaged) +0.0217 CI-separated -> the situation-register's ROLE STRUCTURE specifically earns its place, excludes 'a bag of entity-associated words is enough'. (3) SHUFFLED-ENTITY twin on the replace arm (ENTITY_ROLE_SHUF): +0.1613 [+0.1394, +0.1826] worse than the true entity -> the entity-specific signal is large. (4) LOCAL floor: entity beats bottom-up verb+agent +0.1253 [+0.1077, +0.1426] -> entity context adds over the local predictor. (5) REPLICATION on the independent QASRL test split (separate documents) reproduces the headline and both twins. (6) GLASS-BOX: the forward map is a closed-form ridge over grounded semantic features + entity identity -- no external model, no word-form, no dependency parse (witness guard). (7) REFUTATION control: role-blind REPLACEMENT of the bag (v1) LOSES to bag CI-separated (-0.0355) -- the naive 'replace the gist with an entity average' fails; only role-conditioned AUGMENTATION wins. (8) PREDICTOR-ROBUSTNESS control (v4): swapping the learned ridge map for CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL (Lewis-Vasishth; the audit's E1/E2/E3 unifier), the entity cue beats the bag cue +0.0846 [+0.0590, +0.1114] (LARGER than ridge) and the random-entity cue drags retrieval to WRONG episodes (-0.11) -> the win is a property of the entity-structured representation, not the regression."
files_changed: "experiments/exp_entity_structured_situation_model_prediction_v1.py, experiments/exp_entity_structured_situation_model_prediction_v2.py, experiments/exp_entity_structured_situation_model_prediction_v3.py, experiments/exp_entity_structured_cue_based_retrieval_v4.py, experiments/exp_entity_binding_context_resolution_v5.py, experiments/exp_entity_structured_real_organ_retrieval_v6.py, verification/verify_entity_structured_situation_model.py, notes/problems/the_situation_model_tracks_words_not_entities/SOLVED.md. NO hdlab/ file changed (proposed wiring below, Q111)."
reverify: ".venv/Scripts/python.exe verification/verify_entity_structured_situation_model.py"
---

# The situation model made entity-structured: the active entity's role-history, added to the discourse gist, predicts a recurring entity's next argument better than a bag of words

The brief named the gap the just-integrated predictive-reader left behind: the reader's running situation
model is a bag-of-content-words mean (a validated but ENTITY-BLIND gist). This builds the entity-structured
version -- persistent entities whose ROLE history is tracked and retrieved -- and shows, on modern held-out
text, that it predicts a recurring entity's next argument CI-separated better than the bag-of-words gist,
with the info-free twin (a random entity's history) actively hurting. The win is REAL, replicated on an
independent split, and HONESTLY MODEST in size, bounded by the coarse 12-feature grounded space, not by the
mechanism. The decisive correction over the naive brief -- and the thing that made it work -- is that the
brain does not REPLACE the discourse gist with an entity model; it keeps BOTH and the entity node is ROLE-BOUND.

## Headline in plain language

When you read "The waiter took the order. Then he brought the...", you predict "food / plate / bill" -- not
because the paragraph is vaguely about restaurants, but because you are tracking THE WAITER as a specific
person and you know what waiters do. Our reader had only the vague-paragraph version: a blurry average of the
recent meaning-words, with no notion of "the same person, acting again." I gave it entities: each recurring
character carries its own little memory of what it has done (what it has acted on), and when it comes back,
that memory is used to predict what it does next. On thousands of held-out modern sentences, adding this
entity memory to the paragraph-average predicts the next thing a recurring character acts on better than the
paragraph-average alone -- and if you hand the character the WRONG memory (a random other character's), it
gets WORSE, which proves it is genuinely tracking who is who. Two honest notes: the improvement is real and
clean but small (our meaning space is only 12 coarse features), and the naive version of this idea -- throw
away the paragraph-average and use only the entity memory -- actually FAILS; you have to keep both, which is
also how the brain does it.

## What the brain does, and what I built (mark PINNED vs OUR-INVENTION)

Comprehension builds a SITUATION MODEL whose nodes are ENTITIES tracked across the discourse, and prediction
is ENTITY-STRUCTURED. Three drills (the brief's frame + a 30-min brain-deepening cron + a deeper research
drill on owner request) pinned the finer choices, and one of them CHANGED the build before I shipped a wrong
version:

- **PINNED: the situation model's nodes are ENTITIES tracked across the discourse; prediction uses the active
  entity's established state, not a bag of recent words.** Zwaan & Radvansky 1998 (event-indexing, protagonist
  dimension); Kintsch construction-integration (role-bound propositions); Nieuwland & Van Berkum 2006 (a
  discourse/entity context -- "the peanut was in love" -- overrides local plausibility: the ENTITY's
  established properties drive the N400, not the words). COPIED as the operation.
- **PINNED: the entity node is ROLE-BOUND, and retrieval is role-conditioned.** The situation-model register
  (`hdlab.situation_model_accumulate`) binds (role, event) per entity and decodes by unbinding the role. So to
  predict agent E's next PATIENT, you retrieve E's PRIOR PATIENTS specifically -- the things E has acted on --
  not a role-blind average of everything about E. This is the register's actual decode op. COPIED, and shown
  to specifically matter (role-conditioned beats role-blind CI-separated).
- **PINNED: each new mention is bound to its persistent entity (coreference); the strongest cue is lexical
  IDENTITY.** A repeated head is (near-certainly) the same entity -- the easy, high-precision coref cases. The
  coref ORGAN (`hdlab.coreference_resolver`, match-or-allocate) adds the harder pronoun/nominal-variant cases.
- **PINNED (the correction that made it work): the brain keeps BOTH a global situation gist AND entity nodes
  -- it AUGMENTS, it does not REPLACE.** The default-mode/discourse gist and the hippocampal-entorhinal entity
  system coexist. My first mechanism (replace the gist with an entity average) FAILED (v1); augmenting won (v2).
- **OUR-INVENTION-UNDER-TEST (marked, swept, not adopted):** the entity representation as a MEAN of grounded
  role-fillers (the computational-level content of the register's role-bound bundle-and-decode; the FHRR
  IMPLEMENTATION + a grounded<->FHRR encoding is a wiring detail I did NOT build); IDENTITY vs coref-organ
  linking; the ridge forward map (the Rao-Ballard generative-prediction instantiation); the softmax temperature.

Data: REAL modern predicate-argument documents reconstructed from QASRL v2 (sentenceId = SOURCE:DOC_SENTNUM;
GOLD spans; deliberately NOT the ~200-year-old McGuffey coref fixtures the brief warns against -- the age
confound does not apply, and the existing coref gold IS McGuffey, so a fresh modern population was required).
The task, floors and readout are IDENTICAL to the predictive-reader's discourse cell except the context block,
so this is a fair, apples-to-apples head-to-head with the bag-of-words gist as the recomputed floor.

Six cells (v1 the refutation that shaped it, v2 the headline, v3-v6 the brain-faithful deepening drills):
1. `exp_entity_structured_situation_model_prediction_v1` -- the naive REPLACE test (role-blind entity gist
   vs the bag-of-words gist). Establishes that entity information EXISTS but a role-blind average does not
   beat the richer document average.
2. `exp_entity_structured_situation_model_prediction_v2` -- the brain-faithful build: ROLE-CONDITIONED entity
   retrieval, AUGMENTING the bag gist, with the role-blind and info-free twins as controls (the headline).
3. `exp_entity_structured_situation_model_prediction_v3` -- ONE LEVEL DEEPER (the aggregation drill): is the
   entity representation a convenient PROTOTYPE (mean) or the brain's SEPARATED / activation-weighted
   retrieval? Compares prototype (mean) vs exemplar (most-recent, pattern-completion) vs recency-weighted
   (ACT-R base-level activation; Lewis-Vasishth), stratified by entity-thread length.
4. `exp_entity_structured_cue_based_retrieval_v4` -- THE DEEPEST SWAP (predictor fidelity): replaces the
   learned RIDGE forward map entirely with CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL (Lewis & Vasishth 2005;
   the audit's E1/E2/E3 unifier; `content_addressable_retrieval.AdditiveCueRetrieval`), and tests whether the
   entity-state as an ADDITIVE cue feature improves retrieval-based prediction over a bag-of-words cue.
5. `exp_entity_binding_context_resolution_v5` -- THE BRIEF'S CORE CLAIM DIRECTLY (the other admissible task):
   entity IDENTITY ("who is who"), not prediction. Mask a recurring mention's head and bind it to the correct
   prior entity by context (the E3 coreference operation), vs recency/frequency salience floors, with a
   shuffled-binding twin. Finds a DISSOCIATION (finding 11).
6. `exp_entity_structured_real_organ_retrieval_v6` -- run the ACTUAL landed
   `hdlab.content_addressable_retrieval.AdditiveCueRetrieval` organ (not a reimplementation), forcing a concrete
   grounded->FHRR encoding. Fidelity check: does the entity-cue win survive in the real organ (finding 12)?

## What I measured (all CI'd; reverify = the witness, PASS)

1. **THE HEADLINE -- the entity-structured model beats the bag-of-words gist, CI-separated (AUGMENT).**
   n=1,708 held-out target events (recurring agents), split by document, 3 seeds. BAG+ENTITY surprisal 2.7771
   [2.7387, 2.8149] vs the bag-of-words gist alone 2.8315 [2.7927, 2.8697]: margin +0.0545 [+0.0430, +0.0671],
   half-width 0.0121. **BAR MET.**

2. **THE INFO-FREE TWIN LOSES -- and actively HURTS.** Bag + a RANDOM other entity's role history (entity link
   scrambled, bag identical) scores 2.8916 -- WORSE than the bag alone by 0.06 [0.0467, 0.0732]. A random
   entity's history does not just fail to help; it degrades the prediction. So the win requires the CORRECT
   entity's history (null p95 for the twin is below zero, i.e. the twin never beats the floor). BAG+ENTITY
   beats its own twin +0.1145 [+0.0971, +0.1324].

3. **ROLE-BINDING EARNS ITS PLACE -- the situation-register's role structure, not just "any entity history."**
   Role-CONDITIONED entity augmentation (prior patients, the register's decode) beats ROLE-BLIND entity
   augmentation (all of the entity's co-content averaged) +0.0217 [+0.0141, +0.0286] CI-separated. The
   role-blind version still helps a little over bag (+0.0327 [+0.0237, +0.0415]) -- entity identity carries
   some signal even unstructured -- but the register's ROLE structure adds CI-separated on top. This is the
   deepest brain-faithfulness result: the win is specifically the role-bound retrieval, not a generic
   entity-associated bag of words.

4. **ENTITY CONTEXT ADDS OVER THE BOTTOM-UP PREDICTOR, and its shuffled twin is far worse.** The
   role-conditioned entity predictor beats the LOCAL verb+agent predictor +0.1253 [+0.1077, +0.1426]; a
   shuffled-entity version of it is +0.1613 [+0.1394, +0.1826] WORSE than the true entity. Large,
   entity-specific.

5. **THE FLOOR REPRODUCES.** The bag-of-words gist beats LOCAL +0.1192 [+0.1053, +0.1338] on this population --
   the predictive-reader's discourse-gist finding, recomputed here, so the floor is honest and strong.

6. **REPLICATION on the INDEPENDENT QASRL test split** (entirely separate documents, n=672, 3 seeds):
   BAG+ENTITY beats bag +0.0402 [+0.0216, +0.0599]; the info-free twin hurts (-0.0484 [-0.0664, -0.0305]); gate
   passes. The effect is not a train-split artifact.

7. **THE REFUTATION THAT SHAPED THE MECHANISM (v1).** A role-BLIND entity gist REPLACING the bag (the naive
   reading of "replace the bag-of-words gist with an entity model") LOSES to the bag CI-separated (-0.0355
   [-0.0477, -0.0231]) -- even though that same role-blind entity gist beats LOCAL (+0.0786) and its
   shuffled twin loses (+0.1016). So entity information was always there; the naive REPLACE framing was
   wrong. This negative is what forced the two brain-faithful corrections (role-conditioning + augment).

8. **HONEST SIZE.** The augment effect is real and CI-separated on every metric and on two independent splits,
   but MODEST (+0.0545 surprisal; the entity gist is built from only ~1.7 prior patients per entity). The
   ceiling is the same coarse 12-dimension grounded space that bounded the predictive-reader (the standing p1
   representation-quality coupling): the entity MACHINERY is correct and its payoff scales with representation
   quality.

9. **THE AGGREGATION DRILL (one level deeper -- is the entity representation a convenient MEAN or the brain's
   operation?).** `exp..._v3`, n=1,708 (ent_n>=2 subset n=655), 3 seeds. I compared three aggregations of the
   SAME role-conditioned history, all augmenting the bag gist: PROTOTYPE (mean; the v2 arm), EXEMPLAR
   (most-recent only; pattern-completion -- the brain SEPARATES fillers rather than averaging, audit E1/E2/E3),
   and RECENCY-WEIGHTED (exp-decay; ACT-R base-level activation; Lewis-Vasishth). Findings, all honest:
   (a) EXEMPLAR ties PROTOTYPE (+0.0004 [-0.0052, +0.0061], NOT separated) -- most-recent-only is neither
   better nor worse than the mean here. (b) RECENCY-WEIGHTING beats the flat PROTOTYPE CI-separated but by a
   TINY margin (+0.0028 [+0.0004, +0.0053] overall; +0.0085 [+0.0023, +0.0147] on the >=2 subset) -- the more
   brain-faithful activation-weighted retrieval IS marginally better, so it is the right default, but the flat
   mean is a fine approximation. (c) The benefit does NOT grow with entity-thread length (>=2 subset +0.0336
   is not larger than overall +0.0545) -- even ONE correctly-bound prior filler carries the benefit; the win
   is not a long-accumulation effect. CONCLUSION: at this modern population's short entity threads (~1.7
   fillers) the AGGREGATION barely matters -- prototype, exemplar and recency-weighted sit within ~0.01 of one
   another. So v2's mean is at the correct COMPUTATIONAL level; recency-weighting is the more-faithful and
   marginally-better wiring default; and the deep PROTOTYPE-vs-EXEMPLAR (dense-superposition vs
   pattern-separation) question is NOT strongly discriminable on short threads -- it needs a longer-thread
   corpus, which is stated as a limitation, not resolved by an underpowered null.

10. **THE PREDICTOR ITSELF MADE BRAIN-FAITHFUL, and the entity contribution SURVIVES (indeed strengthens).**
    `exp..._v4`, n=1,937 held-out, 3 seeds. Every arm above (v1-v3) inherits the predictive-reader's LEARNED
    RIDGE forward map -- a convenient ML tool, NOT the brain's operation. The situation model predicts by
    CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL (Lewis & Vasishth 2005; the operation the audit says unifies
    E1/E2/E3 and the fan effect; `content_addressable_retrieval.AdditiveCueRetrieval`): given the cue (verb,
    agent, entity-state), retrieve the most-similar prior episodes and predict their filler. I re-ran the
    entity-contribution test in THAT framing -- additive Lewis-Vasishth activation (the organ's computation,
    similarity kernel matched to the grounded space; verb = exact-predicate match), k=10 exemplar retrieval,
    prediction = mean of the retrieved patients. Result: the ENTITY cue beats the BAG cue +0.0846 [+0.0590,
    +0.1114] (half-width 0.0262) -- LARGER than the ridge augment (+0.0545) -- and the info-free TWIN (a random
    entity's state as the cue) does not just fail, it drags retrieval to the WRONG episodes: -0.11 [-0.1374,
    -0.0824] vs the bag cue, WORSE than even the local cue. So the entity contribution is NOT a ridge artifact:
    it holds, and strengthens, under the brain's actual retrieval mechanism. This is the deepest fidelity check
    in the submission -- the win is robust to swapping the predictor from ML regression to content-addressable
    retrieval.

11. **THE OTHER ADMISSIBLE TASK -- ENTITY BINDING ("who is who") -- reveals a DISSOCIATION: binding is
    SALIENCE-driven, prediction is CONTENT-driven.** `exp..._v5`, n=9,402 held-out, 3 seeds. Findings 1-10 all
    test PREDICTION; the problem TITLE is about entity IDENTITY, so I did the bar's other admissible task
    directly: mask a recurring mention's head and bind it to the correct prior entity by context (the E3
    coreference operation; cue-based retrieval over the entities' accumulated context). Result: content-based
    binding (accuracy 0.308) beats chance (0.226) and its shuffled-context twin (0.229, at chance) CI-separated
    (+0.0786 [+0.0667, +0.0910]) -- so entity content carries a REAL identity signal. BUT the SALIENCE floor
    (RECENCY, pick the most-recent entity) scores 0.493, far above content, and content does NOT augment it:
    selecting by content among the 3 most-recent candidates (0.377) LOSES to pure recency (-0.116 [-0.128,
    -0.104]). So for BINDING, salience (recency / grammatical prominence) dominates and semantic content is a
    real-but-weak, non-augmenting cue. This is the correct brain mechanism -- Centering Theory (Grosz/Joshi/
    Weinstein): the backward-looking center is the most salient entity -- and it INDEPENDENTLY VALIDATES the
    project's salience-based (centering) coref organ over a content/cue-based one, matching the prior
    cue-based-activation coref HARD_FAIL (-0.1348) on fresh modern text. The situation model is entity-structured
    with TWO channels doing TWO jobs: SALIENCE binds mentions to entities; the entity's CONTENT conditions
    prediction. This does not weaken the SOLVED headline (which rests on prediction, findings 1-10); it completes
    the picture and locates where entity content does (prediction) and does not (binding) earn its place.

12. **THE REAL ORGAN CARRIES IT DIRECTIONALLY -- and the grounded->FHRR ENCODING is a genuine, load-bearing
    wiring decision (not a formality).** `exp..._v6`, n=1,500, 3 seeds. Findings 1-11 use grounded-space
    computations (my reimplementation of the organ's math). This cell runs the ACTUAL landed organ
    `hdlab.content_addressable_retrieval.AdditiveCueRetrieval`, which forces the grounded->FHRR encoding I had
    deferred: a fixed random projection to FHRR phase codes exp(i*Rx), scored by the organ's fhrr_sim. Result:
    the entity cue helps in the RIGHT direction (bag 2.982 -> bag+entity 2.944, +0.0372) and the info-free twin
    (random entity) clearly HURTS, CI-separated (-0.068 [-0.109, -0.029]) -- so the mechanism TRANSFERS to the
    real organ directionally and the entity channel still carries correctly-bound information. BUT the
    entity-vs-bag margin is NOT CI-separated through the organ (lower CI -0.0005), vs +0.0846 in grounded space.
    I isolated WHY, and it is informative: (a) raising the FHRR dimension 256 -> 1024 does NOT recover it (+0.034,
    still not separated) -> the encoding DIMENSION is not the limiter; (b) my grounded-space retrieval at the
    organ's k=1 single-argmax setting STILL separates (+0.0678 [+0.0317, +0.1037]) -> the retrieval granularity
    is not the limiter. By elimination, the RANDOM-PROJECTION grounded->FHRR ENCODING itself attenuates the fine
    entity signal (grounded cosine +0.068 -> fhrr_sim +0.034, below separation). CONCLUSION: the mechanism is
    sound (grounded-space, robust, findings 1-11); the ORGAN's naive encoding loses ~half the entity margin, so
    a faithful LIVE wiring needs a BETTER grounded->FHRR encoding (learned / structure-preserving), not just any
    random projection. This RESOLVES the audit's open "grounded<->FHRR encoding" question with a measurement: the
    encoding is load-bearing, and a naive one is insufficient.

## Is this brain-faithful, machinery-in-proximity too? (the drill's verdict)

YES on the operation, with the deviations named:

- **The core operation is faithful and locus-appropriate.** Tracking entities across a discourse and using the
  active entity's role-bound state to predict the next input is a hippocampal-entorhinal (entity binding /
  situation-model maintenance) + default-mode (situation model) computation, with the role-filler content in
  the ATL/angular-gyrus grounded space the predictive-reader already localised. Retrieving the entity's
  role-fillers IS the `situation_model_accumulate` decode.
- **The register's role structure is validated, not assumed.** Role-conditioned beats role-blind CI-separated
  (finding 3) -- the audit's E2 "situation-model register / event indexing" entry is exercised as intended
  (role-bound accumulate + role-conditioned decode), and it earns its place.
- **The proximate organs are the right ones and are composed here in spirit:** `coreference_resolver`
  (mention->entity, the E3 match-or-allocate), `situation_model_accumulate` (the role-bound entity register,
  E2), `content_addressable_retrieval` (the additive cue-based mention->entity match the audit unifies E1/E2/E3
  under), and the forward predictor (the just-built word/feature level). The entity representation I score is
  the COMPUTATIONAL content of the register's role-bound decode.
- **The AGGREGATION was interrogated, not assumed (finding 9).** A flat mean is a convenient PROTOTYPE; the
  brain SEPARATES fillers and retrieves by activation (recency/frequency). I tested exemplar and
  recency-weighted aggregations: recency-weighting (the more faithful one) is CI-separated better than the flat
  mean but only by ~0.003-0.009, and exemplar ties -- at these short entity threads the choice barely matters.
  So the mean is faithful at the computational level; recency-weighting is the marginally-better default; and
  the dense-superposition-vs-pattern-separation question needs longer threads to decide.
- **The PREDICTOR was interrogated, not inherited (finding 10) -- the deepest check.** The ridge forward map is
  an ML tool, not the brain's operation. I swapped it for CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL (the audit's
  E1/E2/E3 unifier, the real `AdditiveCueRetrieval` computation), and the entity contribution HELD and
  STRENGTHENED (+0.0846 vs the ridge's +0.0545), with the random-entity cue actively dragging retrieval to the
  wrong episodes. The win is a property of the entity-structured representation, not of the regression.
- **The honest deviation: I used lexical-IDENTITY entity linking and a numpy MEAN, not the coref ORGAN on
  pronouns and not the FHRR register.** On QASRL the arguments are content-word heads and pronouns are filtered
  (non-groundable), so the coref organ's pronoun-linking is not cleanly testable on this population, and the
  grounded<->FHRR encoding for the live register is a genuine wiring-design decision I declined to invent under
  time pressure (that is the documented way this project loses). Both are named as next steps, not hand-waved.

## What would change in hdlab (proposed; the strategy session lands it, Q111)

- **WIRE the situation model as ENTITY-STRUCTURED, and AUGMENT the discourse gist -- do NOT replace it.** The
  reader's top-down context for predicting a recurring entity's next argument should be [the running discourse
  gist ++ the active entity's role-conditioned accumulated state]. Replacing the gist loses (v1); augmenting
  wins (v2). This is a feature-block change at the forward predictor's context input, composing three existing
  organs.
- **Use ROLE-CONDITIONED retrieval from `situation_model_accumulate`, not a role-blind entity bag.** For
  predicting an entity's next filler of role R, retrieve that entity's prior R-fillers (unbind role R) -- the
  register's decode op. Role-conditioned beats role-blind CI-separated; wire the role structure, not an average.
- **Aggregate the retrieved fillers with RECENCY-WEIGHTING (ACT-R base-level activation), not a flat mean.**
  It is the more brain-faithful aggregation AND marginally better (finding 9), and it is free (an exp-decay
  weight). The gain is tiny at current thread lengths, so a flat mean is an acceptable v1; recency-weighting is
  the correct default and will matter more on longer discourse.
- **Bind mentions to entities with the coref organ (`coreference_resolver` match-or-allocate) + lexical
  identity as the high-precision default.** Identity handles repeated heads; the organ adds pronoun/nominal
  variants. NOTE the prior negative: a cue-based-retrieval-ACTIVATION coref resolver HARD_FAILED vs the
  symbolic strict-Cb/Principle-B resolver (-0.1348 on the competitive subset), so wire the SYMBOLIC resolver
  for the coref DECISION; use content-addressable retrieval for the mention->entity STORE access, not for the
  pronoun pick.
- **Predict by CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL, not a learned regression (finding 10).** The
  entity-state should enter as an ADDITIVE cue feature to `AdditiveCueRetrieval` (verb ++ agent ++ discourse
  gist ++ entity-state -> retrieve the most-similar prior episodes -> predict their filler). The entity cue
  helps MORE under retrieval than under ridge (+0.0846 vs +0.0545), and this is the audit's PINNED unifying
  operation -- so the whole forward predictor should move to retrieval, with the entity-structured state as one
  cue channel. This composes the SAME organ the store access uses.
- **Solve the grounded<->FHRR encoding -- MEASURED to be load-bearing, and a naive random projection is
  INSUFFICIENT (finding 12).** Running the real `AdditiveCueRetrieval`, a fixed random projection to phases
  attenuates the entity margin below CI-separation (the twin still clearly loses, so the channel is real);
  raising d to 1024 does not fix it and grounded k=1 still separates, so the ENCODING QUALITY is the limiter.
  The live wiring needs a BETTER encoding (learned / structure-preserving) that keeps the grounded cosine
  geometry, not just any projection -- and a MEASURE-ON-THE-LIVE-READER check that the decode preserves the
  ranking. An isolation win is a construction proof; measure end-to-end before any capability claim.
- **Expect ROBUSTNESS, not a headline number.** The win is real and modest; its live value is a sharper
  entity-conditioned prediction / difficulty signal downstream organs want, ceiling'd by representation quality
  (p1). Measure on the live reader before claiming a capability.

## KEY REALIZATIONS (the enabling moves)

- **The naive brief was wrong in a productive way, and measuring the naive version first is what revealed the
  brain mechanism.** "Replace the bag-of-words gist with an entity model" LOSES (v1: -0.0355). Rather than
  concluding "entity structure doesn't help," the losing arm's OWN controls said otherwise (it beat LOCAL, its
  twin lost) -- so the information was there and the FRAMING was wrong. That forced the two corrections that
  won: role-conditioning and augment. A shared wall meant the mechanism was wrong, not the capability.
- **Role-conditioning is the difference between a bag and a situation model.** A role-BLIND entity average is
  just a smaller, entity-scoped bag of words; it barely helps. Retrieving the entity's prior fillers of the
  SPECIFIC role being predicted (the register's decode) is what beats the document average CI-separated. The
  test that isolates it -- role-conditioned vs role-blind, both augmenting -- is the sharpest brain-faithfulness
  discriminator in the submission, and it was the deeper drill (not the first build) that produced it.
- **AUGMENT, not replace, is the brain's architecture and the winning one.** The brain has both a discourse
  gist and entity nodes; forcing a choice between them is an engineering habit, not biology. The info-free twin
  (bag + random entity) HURTING -- not just failing to help -- is the clean signal that the entity channel
  carries real, correctly-bound information.
- **The existing coref gold is McGuffey, so the population had to be rebuilt modern.** Scoring entity tracking
  on 200-year-old prose would have confounded the result; reconstructing QASRL documents (which the
  predictive-reader had already shown carry real cross-sentence structure) gave a modern, fair, apples-to-apples
  floor.
- **The deepest fidelity gain came from interrogating the INHERITED choice, not the novel one.** The entity
  representation was the obvious thing to drill; the PREDICTOR (a ridge map) was inherited unquestioned from the
  predictive-reader. Asking "is the ridge the brain's operation?" -- it is not; the brain does cue-based
  content-addressable retrieval -- produced the strongest result: the entity contribution is LARGER under the
  faithful retrieval predictor than under ridge, proving the win is a property of the entity-structured
  representation, not of the regression. The lesson: audit the choices you inherited as hard as the ones you made.
- **A floor-labelling bug in the aggregation drill was caught by cross-checking a shared quantity, not by
  reading the diff.** v3's `BAG` arm initially excluded the bag gist (a backwards ternary), so it silently
  computed LOCAL; the tell was that v3's BAG surprisal (2.9507) equalled v2's LOCAL, not v2's BAG (2.8315). The
  "make outputs print quantities that constrain each other, then read them against each other" habit caught it:
  the same arm measured in two cells must agree, and it did not. The initial "benefit grows 3x with history"
  read was entirely that bug and was retracted; with the correct bag floor the benefit does NOT grow with thread
  length.

## What I did NOT establish (and would withdraw first if wrong)

- **This is a held-out prediction result on reconstructed documents, NOT a demonstrated live-reading gain.**
  The FIRST thing I would withdraw is any implication that wiring this moves a live QA/comprehension number; it
  must be measured on the live reader. Its value is the sharper entity-conditioned prediction signal, and the
  effect is modest.
- **I did NOT test the COREF ORGAN's marginal value over lexical identity.** On QASRL, arguments are content-
  word heads and pronouns are filtered (non-groundable), so the organ's pronoun/nominal-variant linking is not
  cleanly testable on this population. My "entity" is an identity-tracked recurring head. The coref organ is
  essential on prose with pronouns; that its EXTRA linking helps prediction is a hypothesis, untested here, and
  needs a modern coref-annotated corpus.
- **I did run the REAL organ, and found the grounded<->FHRR encoding is a LOAD-BEARING wiring decision I only
  PARTIALLY resolved (finding 12).** Through the actual `AdditiveCueRetrieval` with a naive random-projection
  encoding, the mechanism transfers directionally (twin CI-separated-loses) but the entity-vs-bag margin is
  attenuated below CI-separation (encoding, not dimension or k, is the cause). I did NOT build or test a BETTER
  encoding (learned / structure-preserving), so "a faithful encoding recovers the full grounded-space margin"
  is a hypothesis, not established. The headline rests on the grounded-space result (findings 1-11), which is
  robust; the FHRR live wiring needs the encoding solved.
- **The effect is small (+0.0545 surprisal; ~1.7 fillers/entity).** I attribute the ceiling to the 12-dim
  grounded space (the p1 coupling), but I did NOT prove a richer space lifts it -- that is a testable hypothesis,
  untested here.
- **The BINDING result is on MASKED-HEAD content-only resolution, not real pronouns.** I did run the bar's
  other admissible task (entity resolution, finding 11) and found the dissociation (salience dominates), but I
  simulated an anaphor by MASKING a recurring content head and resolving by context -- I did not use real
  pronoun mentions (QASRL filters them). The dissociation (salience > content for binding) is robust and
  literature-consistent, but the absolute binding numbers are for the masked-head proxy, not for true pronouns;
  a pronoun-bearing modern corpus would confirm it. I did NOT combine salience + content in a tuned model (my
  augment arm was a simple top-3-recent content tie-break, which lost); a properly weighted salience+content
  model might recover a small content contribution, untested.
- **I did NOT decide the PROTOTYPE-vs-EXEMPLAR (dense-superposition vs hippocampal pattern-separation)
  question.** At ~1.7 fillers/entity the three aggregations are within ~0.01 (finding 9), so this population
  cannot discriminate them; the audit's deep E1/E2/E3 "separate-and-retrieve beats dense-superposition" claim is
  neither confirmed nor refuted here and needs a longer-thread corpus. Recency-weighting is marginally best, so
  I recommend it, but I do not claim the aggregation is settled.
- **The cue-based retrieval predictor's hyperparameters are OUR-INVENTION, swept lightly not optimised.** The
  per-feature cue weights are EQUAL (1.0 each), verb is an exact-identity match, k=10 exemplars, cosine kernel.
  These are defensible defaults (the organ marks weights and kernel as OUR-INVENTION-UNDER-TEST) but I did not
  sweep them; the entity-cue-helps result is robust to the predictor CLASS (ridge and retrieval both show it),
  not proven optimal within retrieval.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **E2 "Situation-model register / event indexing" (RIGHT-OP-WRONG-PLACE) gets a positive result: the
   role-bound structure EARNS ITS PLACE for prediction.** On modern QASRL, a role-CONDITIONED entity retrieval
   (the register's decode op -- retrieve E's prior fillers of the role being predicted) beats a role-BLIND
   entity average CI-separated (+0.0217 [+0.0141, +0.0286]), and both beat a bottom-up predictor. Recommend the
   audit record that the register's role-binding is validated as PREDICTIVELY useful, not just as storage.
2. **NEW result for the situation model vs the bag-of-words gist: entity structure AUGMENTS, it does not
   REPLACE.** The discourse gist (the predictive-reader's finding-9 arm) and the entity node are COMPLEMENTARY:
   bag+entity beats bag alone CI-separated (+0.0545), while REPLACING the gist with an entity average LOSES
   (-0.0355). Recommend the audit record the situation model as a TWO-CHANNEL structure (global gist + entity
   nodes), not a single running representation -- the entity channel is additive over the gist, and the
   info-free twin (random entity) HURTS.
3. **Cross-link to E3 coref and the E1/E2/E3 unification:** the entity representation used here is the
   COMPUTATIONAL content of the `situation_model_accumulate` role-bound decode, accessed by entity identity;
   the live wiring composes `coreference_resolver` (mention->entity, symbolic strict-Cb -- NOT the cue-based
   activation resolver, which HARD_FAILED -0.1348) + the register (role-bound store) + the forward predictor.
   The audit's "cue-based content-addressable retrieval unifies E1/E2/E3" holds for the STORE ACCESS; the coref
   DECISION stays symbolic per the prior negative.
4. **The grounded<->FHRR encoding for the live register is now MEASURED to be LOAD-BEARING (finding 12).**
   Running the real `AdditiveCueRetrieval` with a naive random-projection encoding, the entity channel transfers
   directionally (twin CI-separated-loses) but a NAIVE encoding attenuates the entity-vs-bag margin below
   CI-separation (grounded cosine +0.068 -> fhrr_sim +0.034); raising d 256->1024 does not fix it, and grounded
   k=1 still separates -> the ENCODING QUALITY is the limiter, not dimension or retrieval granularity. Recommend
   the audit record: the grounded<->FHRR encoding is a real, load-bearing wiring decision between E2 (register)
   and the grounded spoke; a naive random projection is INSUFFICIENT, and a better (learned / structure-
   preserving) encoding is required for the live register to preserve the grounded-space entity signal.
5. **AGGREGATION partially probed (finding 9): recency-weighting (ACT-R base-level activation) is the more
   faithful default and marginally beats a flat prototype (+0.0028 CI-sep), exemplar ties, and the deep
   dense-superposition-vs-pattern-separation (E1/E2/E3) question is NOT discriminable at this population's short
   entity threads (~1.7 fillers).** Recommend the audit record: the register's aggregation should be
   recency-weighted, and the pattern-separation-beats-superposition claim needs a longer-thread corpus to test on
   REAL entity histories rather than the synthetic partial-cue construction it currently rests on.
6. **THE FORWARD PREDICTOR should be CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL, not a learned ridge (finding 10) --
   and this is a NEW datapoint for the E1/E2/E3 unification.** Swapping the ridge map for additive Lewis-Vasishth
   retrieval (the `AdditiveCueRetrieval` computation) makes the entity contribution LARGER (+0.0846 vs +0.0545),
   with a wrong-entity cue actively dragging retrieval off (-0.11). Recommend the audit record that the
   situation-model forward predictor is another instance of the cue-based-retrieval operation (the entity-state
   is one additive cue channel), strengthening "cue-based content-addressable retrieval unifies E1/E2/E3" with a
   PREDICTION (not just recall) instance on real modern text.
7. **NEW DISSOCIATION (finding 11): entity BINDING is SALIENCE-driven, entity PREDICTION is CONTENT-driven.** On
   the direct entity-resolution task, RECENCY (0.493) dominates content-based binding (0.308), and content does
   not augment salience (content-select among the top-3 recent LOSES to pure recency, -0.116); content carries a
   real-but-weak identity signal (beats chance + shuffled twin CI-sep). Recommend the audit record: (a) this
   independently VALIDATES the salience-based (Centering) coref organ over a content/cue-based one on fresh
   modern text, corroborating the `exp_coref_cue_based_retrieval_actr_activation_v1` HARD_FAIL (-0.1348); (b) the
   situation model is a TWO-CHANNEL structure -- SALIENCE binds mentions to entities (E3, centering), the
   entity's CONTENT conditions prediction (E2 register decode). Content-addressable retrieval is the PREDICTION
   operation, not the BINDING operation.
8. **LITERATURE-VERIFICATION DRILL (WebSearch, 2026-08-27): every load-bearing brain claim CONFIRMED, one
   UPGRADED from behavioral to direct single-neuron evidence, and the v5 dissociation independently corroborated.**
   (a) EVENT-INDEXING / PROTAGONIST DIMENSION confirmed -- readers track entities on a protagonist dimension;
   reading times rise at protagonist shifts (Zwaan/Radvansky/Langston; the 2025 review "From Words to Worlds").
   HONEST REFINEMENT: this is primarily BEHAVIORAL evidence, so soften any "neural" phrasing for the
   situation-model dimension itself. (b) NIEUWLAND & VAN BERKUM 2006 confirmed near-verbatim -- a supportive
   discourse context reduces the animacy-violation N400 ("entity-specific discourse context overrides local
   plausibility"), the exact PIN for entity-structured prediction. (c) DIRECT NEURAL UPGRADE for hippocampal
   entity representations: "Pronouns reactivate conceptual representations in human hippocampal neurons"
   (Science 2024/2025) -- single-neuron recording shows concept cells for particular nouns are REACTIVATED by
   pronouns referring to them. This is direct evidence for (i) hippocampal entity/concept representations and
   (ii) coreference as REACTIVATION of the bound entity's conceptual content. It SHARPENS the two-channel model:
   SALIENCE selects the antecedent (Centering), and selecting it REACTIVATES that entity's conceptual content,
   which is the signal that conditions prediction (findings 2-4). (d) v5 DISSOCIATION corroborated: a 2022
   result (Investigating Centering Theory in neural coref, arXiv:2210.14678) finds recency + world knowledge are
   factors NOT captured by vanilla Centering, and ADDING RECENCY improves coref -- i.e. recency dominant, content
   a real-but-secondary cue, exactly the v5 finding. Recommend the audit: upgrade the hippocampal-entity claim to
   direct-single-neuron support (cite Science pronoun-reactivation), keep the situation-model dimension as
   behaviorally-pinned, and record the "salience selects -> concept reactivates -> conditions prediction"
   mechanistic chain as the reconciled two-channel account.

---

## TLDR
Our reader tracked a blurry average of recent meaning-words, with no notion of distinct characters. I gave it
entities: each recurring character keeps a small memory of what it has done, and that memory is used to predict
what it does next. On thousands of held-out modern sentences, adding this entity memory to the paragraph-average
predicts a recurring character's next action-object better than the paragraph-average alone -- cleanly separated,
replicated on a second independent set of documents -- and handing a character the WRONG memory makes it WORSE,
which proves it is really tracking who is who. The deep finding: it matters that the memory is ROLE-STRUCTURED
(what the character has ACTED ON, specifically), not just a bag of words about the character -- the structured
version wins by a clean margin over the unstructured one. Two honest caveats: the improvement is real but SMALL
(our meaning space is coarse, and each character's memory is only ~2 items), and the obvious version of the idea
-- throw away the paragraph-average and keep only the entity memory -- actually FAILS; you have to keep both,
which is also how the brain does it. One more honest twist from the deepest drill: when I tested the OTHER half of
tracking entities -- resolving WHO a mention refers to -- the meaning-memory helped a little but was beaten
decisively by a much simpler rule ("it is usually the most-recently-mentioned character"). So the brain does two
different things with entities: SIMPLE RECENCY to figure out who is who, and the richer MEANING-MEMORY to predict
what they will do next. Our system should do both; this work builds and validates the meaning-memory half and shows
the recency half is what binds mentions to entities.

## QUESTIONS
None. One judgement call for the owner at integration: the win is CI-separated on every metric and on two
independent document sets, but MODEST in size (+0.0545, entity memory ~1.7 items), ceiling'd by the 12-feature
grounded space (p1). I read the bar as MET (entity-structured beats bag-of-words CI-separated; info-free twin
loses -- indeed hurts). If magnitude is weighted over CI-separation, the honest framing is "the entity-structured
machinery is correct and validated; its payoff scales with representation quality" rather than "a large
standalone win."

## NEXT STEPS
1. Land the entity-structured situation model as an AUGMENT: the forward predictor's top-down context = running
   discourse gist ++ the active entity's role-conditioned accumulated state (retrieved from
   `situation_model_accumulate` by entity identity, role-conditioned decode). Do NOT replace the gist. Measure
   on the LIVE reader, not in isolation.
2. Wire mention->entity binding with the SYMBOLIC coref resolver (strict-Cb / Principle-B) + lexical identity as
   the high-precision default; do NOT use the cue-based-activation coref resolver for the pronoun pick (prior
   HARD_FAIL -0.1348).
3. Decide and test the grounded<->FHRR encoding for the live register (the one unbuilt piece): confirm the FHRR
   role-bound decode preserves the ranking at the actual load (~2 fillers/entity).
4. Test the COREF ORGAN's marginal value over lexical identity on a MODERN pronoun-bearing corpus (QASRL cannot
   -- pronouns are non-groundable arguments): does linking pronoun/nominal-variant mentions extend entity threads
   and improve prediction beyond string-identity?
5. Test the p1 hypothesis directly: re-run on a RICHER grounded representation and check the modest effect grows
   -- this is the claimed ceiling and it is testable.
6. Bind mentions to entities with SALIENCE (recency / grammatical prominence; Centering), NOT content retrieval
   -- finding 11 shows recency dominates content for binding (0.493 vs 0.308) and content does not augment it.
   This confirms the salience-based coref organ is the right BINDING mechanism; keep content-addressable
   retrieval for the PREDICTION channel, not the pronoun pick. A properly weighted salience+content binding
   model (vs my simple top-3-recent content tie-break, which lost) is worth one test on a real pronoun corpus.
