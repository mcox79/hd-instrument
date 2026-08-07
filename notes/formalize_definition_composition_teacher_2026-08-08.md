# FORMALIZE: the DEFINITION-COMPOSITION TEACHER (curriculum grounding engine)

**Filed:** 2026-08-08 by Director, formalize-first (the B program's 5x-HARD-FAIL history + USER's
"be very careful, easy to slip up + declare a hard fail" caution both demand it). Status of the
hypothesis: **VALIDATED on fresh held-out** (ee22c7861, Director disk-VET'd) -- not a proposal, a
build-ready design for a proven mechanism.

## 0. ONE-LINE
Ground a new (OOV) word's valence/meaning by COMPOSING the already-grounded words in its dictionary
DEFINITION (gloss) -- the way a person actually learns a new word: look it up, and the definition
reduces the unknown word to words you already know. This is the curriculum's non-vacuum TEACHER.

## 1. VALIDATED EVIDENCE (why this is build-ready, not a bet)
- Fresh held-out N=28 (14/14, systematic WordNet result-verb-hypernym draw, provably disjoint from
  the seed lexicon AND the first probe's 16 words). The ORIGINAL composition rule (ARM A, NO
  light-verb filter): **coverage 75%, acc-when-fires 0.905 (19/21), acc-overall 0.679 (> chance 0.5),
  +25pp coverage vs the relational baseline (9 words it grounds that the relational path structurally
  misses), scramble collapses 0.68->0.36** (genuine gloss-content signal). Commit ee22c7861 / cell
  exp_definition_composition_grounding_retest_freshset_v1.py.
- REJECTED (do NOT use): the post-hoc light-verb filter -- on fresh data it HURT (coverage 75%->61%,
  acc-overall 0.68->0.54) = curve-fit to the original 16. The teacher uses ARM A's rule, unfiltered.
- HONEST caveat carried forward: the fresh set was drawn under clear result-verb roots
  (destroy/damage/improve/construct) = cleaner than arbitrary OOV verbs -> acc-overall 0.68 may be
  optimistic for arbitrary vocabulary. The build's fair test MUST include a harder/arbitrary slice.

## 2. BRAIN-FIDELITY (SHAPE + POSITION + METRIC; which structure, does it SHARE an owned process)
- **Which brain structure?** Vocabulary acquisition from a definition = ANTERIOR TEMPORAL LOBE
  semantic-hub COMPOSITION (the amodal hub that represents a word's meaning as a bound combination of
  features/known concepts; Patterson-Lambon Ralph hub-and-spoke) + HIPPOCAMPAL fast-mapping (bind the
  new lexical form to the composed meaning in one/few shots) + Harnad grounding-TRANSFER (a new symbol
  grounded by reduction to already-grounded symbols -- "symbolic theft" done honestly: the definition
  is the honest transfer, not a stolen embedding).
- **Does it SHARE an owned process -> REUSE, don't rebuild?** YES. The ATL-hub composition is exactly
  hdlab/lexical_similarity.py (shared-FEATURE FHRR bundle over CONCEPT_FEATURES, Cox-2024-style). The
  grounded VALUATION that turns composed features into felt POS/NEG is the owned earned-theta valuation
  (context_grounded_valence / the appraisal-sim theta) + the OUTCOME_SEED anchor. So the teacher is a
  RE-POINT/compose over owned organs, NOT a new organ.
- **SHAPE:** gloss text -> tokenize -> for each content-word, is it already grounded? (seed direct /
  ATL-hub one-hop / relational-lookup) -> COMPOSE the grounded words' valences (signed weighted sum;
  sign -> POS/NEG; 0 -> abstain). Brain-faithful = amodal-hub feature composition + valuation readout.
- **POSITION:** a TEACHER that seeds the acquisition loop's exposure counter with a grounded prior
  BEFORE consequence-from-exposure refines (exactly where wordnet_polarity_propagation already injects
  pseudo-counts; the definition-composition source is a NEW, higher-coverage grounding channel added
  alongside the existing relational one -- they are COMPLEMENTARY: on the fresh set, composition
  covered 9 words the relational path missed, the relational path covered 2 composition missed).
- **METRIC:** does the teacher correctly ground a held-out OOV word's valence (acc-when-fires) at what
  coverage (fraction reachable), with scramble-collapse (real signal) -- the brain's metric = did the
  learner acquire the right meaning from the definition, generalizing to novel words.

## 3. THE MECHANISM (validated ARM-A spec, to promote into hdlab)
1. Sense: `wn.synsets(word,'v')[0].definition() + .examples()`, tokenized (a human reads the example
   sentence too). [Follow-up: principled sense-selection beyond first-sense for polysemy -- deferred.]
2. Ground each gloss content-word via, in order: (A) OUTCOME_SEED_POS/NEG direct; (B) lexical_similarity
   ATL-hub (CONCEPT_FEATURES direct valence, or one-hop cosine >= 0.50); (C) wordnet_polarity_propagation
   .dictionary_lookup one-hop on the gloss word. [+ Cross-POS core, section 4.]
3. COMPOSE: signed weighted sum over grounded gloss content-words; sign -> POS/NEG; 0 -> abstain.
   NO light-verb filter (validated: it hurts on fresh data).
4. INJECT: a confident composed valence -> Bayesian pseudo-counts into the consequence loop's exposure
   counter ONCE (reuse the exact wordnet_polarity_propagation pseudo-count injection contract), then
   consequence-from-exposure refines/overrides. Definition-composition is a DENSE PRIOR, not a lock.

## 4. THE CROSS-POS GROUNDED CORE (the confirmed real coverage lever)
- CONFIRMED gap (re-test, disk-VET'd): 0 evaluative ADJECTIVES in lexical_similarity CONCEPT_FEATURES;
  the coverage-limited verbs had glosses dominated by adjectives/nouns ("undesirable"/"fond"/"attached")
  the verb-restricted grounding sources cannot reach. An 18-word adjective-seed extension already
  rescued 4 zero-coverage verbs in the exploratory arm.
- DESIGN (mirror the verb seed, invariant-OK DATA): a SMALL supplied ADJECTIVE (and minimal NOUN)
  valence seed (~20-30 unambiguous words: undesirable/harmful/cruel/broken/worthless vs
  beautiful/kind/healthy/fond/valuable) + propagation via WordNet adjective relations (similar_to /
  antonym / attribute), exactly mirroring wordnet_polarity_propagation for verbs. Glass-box, no borrow.
- This is a SUPPLY (a grounded-core seed = DATA, invariant-OK -- the child's pre-grounded adjective
  vocabulary), NOT a hand-built detector. It EARNS nothing; it grounds the CORE the composition selects
  from. Every downstream selection/composition/construction remains earned.

## 5. WIRE-DON'T-ISLAND reuse map (every load-bearing piece is owned; the teacher is glue + 1 seed)
- ATL-hub composition:      hdlab/lexical_similarity.py (CONCEPT_FEATURES shared-feature cosine)
- Verb valence anchor:      hdlab/verb_lexical_similarity.py (OUTCOME_SEED_POS/NEG + Tier-3 overlay)
- Relational teacher (compl): hdlab/wordnet_polarity_propagation.py (antonym+path_sim; pseudo-counts)
- Refine engine:            hdlab/consequence_learning_loop.py (exposure counter + consolidate)
- Anti-drift gate:          hdlab/self_improving_loop.py (decide_keep_or_revert abstain-band)
- Orchestration glue:       hdlab/word_learning_tool.py (dictionary-first then consequence-refine)
- NEW (this build):         the definition-COMPOSITION grounding source (validated ARM-A rule) + the
                            cross-POS adjective/noun seed. Both plug into the SAME pseudo-count contract
                            word_learning_tool already consumes -> minimal new surface.

## 6. CURRICULUM ROLE (why this is the bootstrapping keystone; the non-vacuum teacher)
"Learning to read in a vacuum never happens" (USER). The teacher is the caregiver: a small grounded
CORE (verb seed + adjective/noun seed + the sim-earned affect primitives) + the dictionary that DEFINES
every new word in terms of the core. The learner climbs KNOWN -> UNKNOWN: word N+1's gloss composes from
the N already grounded; each newly-grounded word ENLARGES the core the next definition can draw on
(recursive -- a genuine developmental ladder). This is HOW the "growing library of competencies" gets
its grounding for free-via-exposure instead of hand-built.

## 7. BUILD INCREMENTS + CAN-FAIL GATES (test-first; each strict-ADD; Director runs witness in .venv)
- **INC-1: promote the validated teacher into hdlab** (definition-composition grounding source, ARM-A
  rule, pseudo-count injection). GATE: reproduces the fresh-held-out numbers (acc-when-fires ~0.9,
  coverage ~0.75, scramble collapse) from within hdlab; +HARDER slice added (arbitrary OOV verbs, not
  just result-verb-hypernyms) -- report acc/coverage on the harder slice separately (honest, may be
  lower; a lower number there is a COVERAGE/foundation read, not a ceiling).
- **INC-2: cross-POS grounded core.** GATE: adjective/noun seed + propagation lifts coverage on fresh
  held-out (rescues the zero-coverage verbs) WITHOUT tanking acc-when-fires; scramble still collapses;
  the seed is small + principled, NOT fitted to the held-out glosses (check: draw the held-out set
  AFTER fixing the seed).
- **INC-3: fair-regime re-test of the shelved word_acquisition_loop WITH the full teacher wired in**
  (the test its premature HARD_FAIL never got -- inc1/inc1b used only the thin relational prior + a
  degenerate valence channel; this wires the validated definition-composition teacher + cross-POS core).
  GATE: does the loop now LEARN (beat its prior 2/7 // enrich_delta<0)? If not -> DIAGNOSE per section 8,
  NO ceiling claim.

## 8. ANTI-PREMATURE-HARD_FAIL PROTOCOL (USER caution, operationalized -- apply to every gate above)
Before any gate is called a FAIL, triage in order (a null almost always = a broken condition, not a
ceiling):
1. **Foundation present?** Was the grounded CORE (seed + cross-POS) actually loaded, and did the word's
   gloss contain >=1 core word? If not -> COVERAGE/foundation gap (enlarge core / deeper recursion),
   NOT a mechanism fail. (Report coverage SEPARATELY from accuracy, always.)
2. **Teaching signal reached the learner?** Did the composed prior actually inject (pseudo-counts > 0)?
   A loop that never received the teacher's signal is a wiring bug, not a learner ceiling.
3. **Genuinely-new + learnable content?** Is the held-out truly disjoint AND non-degenerate (not all
   one class, not saturated)? An underpowered/misaligned eval (like the earn-from-exposure learnable
   n=0) reads as HARD_FAIL but is a broken experiment.
4. **Fair regime?** Not tested in a vacuum (no core, no dictionary, extraction-starved). Only after 1-4
   pass is a shortfall a candidate real limit -- and even then, run the brain-fidelity element audit
   before concluding.
Report every gate as coverage-vs-accuracy separated + scramble control + the triage result. NEVER
aggregate; NEVER call a coverage-limited abstain a "wrong" that proves a ceiling.

## 9. HONEST OPEN RISKS
- Sense-selection is first-sense-only (polysemy unhandled) -> some glosses are the wrong sense's.
- acc-overall 0.68 was on a clean result-verb set; arbitrary vocabulary + non-valence axes (sense,
  role, hypernym -- the teacher COULD teach these too, untested) are open.
- The cross-POS seed is a SUPPLY -- must stay small + principled + drawn-before-the-eval, or it becomes
  eval-gaming (the exact trap the light-verb filter fell into).
- Recursion depth > 1 was noise-limited in the probe -> the ladder's deeper rungs need the cross-POS
  core to be clean first.

## 10. BOTTOM LINE
The definition-composition teacher is a VALIDATED, brain-faithful (ATL-hub composition + Harnad
transfer), glass-box grounding channel that sidesteps the extraction wall by grounding new words from
their definitions -- the non-vacuum caregiver the curriculum needs. It reuses owned organs almost
entirely (glue + one small cross-POS seed). Build order INC-1 -> INC-2 -> INC-3, each strict-ADD,
test-first, with the anti-premature-HARD_FAIL protocol governing every gate. This is the concrete
first build of the USER-greenlit developmental curriculum.
