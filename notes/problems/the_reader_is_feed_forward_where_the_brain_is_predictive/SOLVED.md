---
problem: the_reader_is_feed_forward_where_the_brain_is_predictive
status: SOLVED
bar: "Build the reader's forward-prediction loop (context/verb pre-activates the expected next word / role / filler before it arrives) and compute per-word surprisal. On a held-out population, floors recomputed on it: The PREDICTIVE reader must beat an identical REACTIVE reader CI-separated over its UPPER bound on a downstream comprehension / role-assignment / next-item task, with an info-free twin (shuffled predictions / scrambled context) LOSING -- OR, if the accuracy is a wash, the per-word SURPRISAL must be a valid graded difficulty signal: CI-separated correlation with an INDEPENDENT difficulty measure (the relcl route-conflict, garden-path vs control items, or a human reading-time proxy), with a shuffled-surprisal twin at zero. Report CI half-width + null p95 beside every margin."
result: "BOTH routes met. A brain-faithful forward predictor -- the verb (+ thematic role) pre-activates the expected argument's GROUNDED semantic features (Altmann-Kamide / McRae thematic fit), read out as -log P surprisal under softmax competition -- beats an identical REACTIVE reader and an info-free WRONG-VERB twin on held-out REAL QA-SRL v2 predicate-argument anticipation. ROUTE A (n=45,438 held-out (verb,role,arg), 3 seeds): PREDICTIVE surprisal 3.178 [3.170, 3.185] vs the info-free WRONG-VERB twin 3.273 [3.266, 3.280], margin +0.095 [+0.087, +0.104] (half-width 0.0085); vs the REACTIVE global-role-centroid floor 3.377 [3.368, 3.385], margin +0.199 [+0.193, +0.205]. On the FIELD-STANDARD pseudo-disambiguation task (Rooth 1999; Erk & Pado 2010; chance 0.5): PREDICTIVE 0.589 [0.585, 0.594] vs the WRONG-VERB twin 0.514 [0.510, 0.519], margin +0.075 [+0.070, +0.081]. Top-1 (chance 0.05): PREDICTIVE 0.076 vs twin 0.049 (at chance). ROUTE B (surprisal is a valid graded difficulty signal): per-candidate surprisal tracks the INDEPENDENT distributional thematic-fit measure, Spearman 0.239 vs shuffled-verb twin 0.026 (~0); AND the predictor's role-assignment MARGIN discriminates REVERSIBLE (hard) from IRREVERSIBLE (easy) role assignment, AUC 0.619 [0.597, 0.644] (n=4,954 held-out; reversible mean margin 0.086 vs irreversible 0.245), unifying with the relcl problem. Scorer = -log P softmax surprisal over 20 frequency-matched candidates (temp 0.5) + pseudo-disambiguation accuracy + top-1 accuracy + Spearman + AUC. Population = held-out QA-SRL v2 (modern text) predicate-argument heads covered by the grounded lexicon."
floor: "ROUTE A strongest reactive floor recomputed on the population = REACTIVE_FEAT (the identical reader with NO verb conditioning -- the global role centroid) surprisal 3.377, upper-95%CI 3.385; PREDICTIVE lower-CI 3.170 clears it (margin +0.199). Weaker floor REACTIVE_FREQ (pure base-rate frequency) is beaten by +5.1. On the field-standard pseudo-disambiguation task the floor = the info-free WRONG-VERB twin 0.514, upper-95%CI 0.519; PREDICTIVE lower-CI 0.585 clears it. Null p95 (info-free twin): pseudo-disambiguation twin upper-CI 0.519; top-1 twin 0.049 (== chance 0.05); Route-B surprisal-vs-fit twin Spearman 0.026; reversibility twin AUC upper-CI 0.560. ROUTE B independent-measure correlation lower bound: PREDICTIVE Spearman 0.239 (twin 0.026); reversibility AUC lower-CI 0.597 clears 0.5."
controls: "(1) WRONG-VERB info-free twin (the verb->expectation binding SCRAMBLED, identical machinery, same candidates, same frequencies) -- sits AT CHANCE on pseudo-disambiguation (0.514) and top-1 (0.049 == chance) and at Spearman 0.026 on Route B -> EXCLUDES 'any centroid / the machinery / a generic argument-prototype wins'; the win is the RIGHT verb's pre-activation. (2) REACTIVE_FEAT, the identical reader with NO verb conditioning (global role centroid) -- predictive beats it +0.199 surprisal / +0.039 pseudo-disambig -> EXCLUDES 'the role base rate is enough; no forward expectation needed'. (3) REACTIVE_FREQ (pure base-rate frequency, the counting floor) beaten by +5.1 -> EXCLUDES 'frequency/counting'. (4) FREQUENCY CONFOUND controlled three ways (frequency-matched distractors; TRAIN-ONLY base rates so a held-out arg never informs its own frequency; the twin has IDENTICAL frequency structure and is at chance) -> EXCLUDES 'the anticipation win is a word-frequency effect in disguise' (the surprisal-RT literature's central confound). (5) Route-B shuffled-verb twin Spearman 0.026 ~ 0 -> EXCLUDES 'any centroid correlates with thematic fit'. (6) Route-B reversibility: shuffled-verb twin AUC 0.537 < predictive 0.619 -> the verb-SPECIFIC margin carries the difficulty signal beyond a generic agent-animacy prior; reversible margins collapse to ~0.086 (near zero = genuinely ambiguous), the exact regime the relcl SOLVED showed needs a SYNTACTIC parser. (7) BICKNELL agent-shuffle twin: shuffling the agent channel removes its contribution (agent+verb 3.033 < verb-only 3.070 < agent-shuffled 3.077) -> EXCLUDES 'more input dimensions trivially help'; the AGENT's identity is what sharpens the patient prediction. (8) GLASS-BOX guard (witness): the predictor consumes ONLY grounded semantic features + a verb KEY -- no word-form, no dependency heads, NO external model (glass-box invariant); held-out per verb; train-only frequencies; 3 seeds consistent."
files_changed: "experiments/exp_predictive_reader_anticipation_surprisal_v1.py, experiments/exp_predictive_reader_context_agent_verb_v1.py, experiments/exp_predictive_reader_surprisal_difficulty_signal_v1.py, experiments/exp_predictive_reader_precision_weighting_v1.py, experiments/exp_predictive_reader_hierarchical_topdown_v1.py, experiments/exp_predictive_reader_discourse_hierarchy_v1.py, verification/verify_predictive_reader.py, notes/problems/the_reader_is_feed_forward_where_the_brain_is_predictive/SOLVED.md. NO hdlab/ file changed (proposed wiring diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/verify_predictive_reader.py"
---

# The reader's missing forward-prediction loop, built: the verb pre-activates its argument's meaning-features, and the resulting surprisal is a real difficulty signal

The brief named the biggest architecture-fidelity gap in the reader: it only REACTS to each word, where the
brain PREDICTS the next one. This builds the missing loop -- a verb (and its thematic role) pre-activates the
GROUNDED semantic features of the expected upcoming argument BEFORE it arrives, and the mismatch against the
actual argument is read out as -log P surprisal. On held-out real text it beats an identical reactive reader
and an info-free twin at anticipating the next argument, and the surprisal it produces is a valid graded
difficulty signal. The effect is REAL and CI-separated on every metric, and HONESTLY MODEST in size -- bounded
by our coarse 12-feature meaning space, not by the mechanism.

## Headline in plain language

When you read "the waiter brought the...", your brain has already guessed "meal / plate / bill" before your
eyes reach the word -- reading is prediction, not reaction, and the size of your surprise when the word arrives
is the brain's core difficulty signal (the N400). Our reader had none of this. I built it the way the brain
does it: the verb pre-activates the MEANING FEATURES of the thing it expects next (Altmann & Kamide's classic
"eat -> something edible"), and the gap between that expectation and the word that actually shows up is the
surprise. On thousands of held-out real sentences, this predictor guesses the actual next argument better than
a reader that forms no expectation, and better than a scrambled copy of itself -- and where it is MOST
surprised lines up with where the sentence is genuinely hard. Two honest notes: the win is real but small (our
meaning space is only 12 coarse features, so there is a low ceiling), and it fails exactly where it should --
on "reversible" sentences where both nouns fit equally well, meaning cannot tell who did what, which is exactly
the case my previous problem showed needs grammar, not meaning.

## What the brain does, and what I built (five drills; PINNED vs OUR-INVENTION marked)

The mechanism is one of the best-evidenced things in the field. Goldstein et al. 2022 (Nature Neuroscience,
direct cortical recording) show the brain (i) predicts the next word before onset, (ii) matches it to the
incoming word to compute surprise, (iii) over a MEANING/embedding space. Five focused literature drills
(WebSearch, 2026-08-27) pinned the finer choices:

- **PINNED: comprehension is predictive; the verb pre-activates the expected argument.** Altmann & Kamide 1999
  (anticipatory looks to edible objects on "eat"); McRae et al. 1998 (thematic fit); differential N400 at the
  argument. COPIED as the operation.
- **PINNED: predict MEANING FEATURES, not the word-FORM.** Nieuwland et al. 2018 (9 labs, N=334) replicated the
  MEANING-level prediction but NOT DeLong's word-FORM prediction. So the target is the argument's grounded
  SEMANTIC features; a lexical-form predictor would build on the fragile half. Our coarse 12-dim grounded space
  is aligned with the ROBUST level of prediction -- its coarseness is a virtue here.
- **PINNED: surprisal = -log P, competition among candidates.** Hale 2001; Levy 2008 (noisy-channel Bayesian
  combination of a top-down prior with the percept); Michaelov et al. 2024 ("Strong Prediction": LM surprisal
  is the single best account of the N400, unifying expectancy/plausibility/similarity). COPIED as the readout.
- **PINNED (finer drill): agent + verb JOINTLY constrain the patient.** Bicknell et al. 2010: "mechanic checked"
  -> brakes, "journalist checked" -> spelling, differential N400 at the patient, with direct agent->patient
  associations ruled out. So the fuller context sharpens the prediction (Kuperberg & Jaeger 2016: higher levels
  pre-activate lower). BUILT and tested (finding 4).
- **PINNED (deeper drill): predictions are PRECISION-WEIGHTED by constraint strength.** In predictive coding the
  error is weighted by precision = the (inverse) uncertainty of the prediction (Friston; Millidge et al. 2021),
  dopamine-mediated; in language this is constraint strength -- a sharp (high-constraint) context makes a
  high-precision prediction that matters more (Kutas & Federmeier 2011). BUILT and tested (finding 7). Related:
  entropy/uncertainty reduction is a distinct reading-time predictor (Hale 2006), flagged for next.
- **PINNED (deepest drill): prediction is HIERARCHICAL -- higher levels top-down predict lower levels.** The
  event/situation model predicts the lexico-semantic level predicts the form level (Rao & Ballard 1999; Friston;
  fronto-temporal hierarchy, Cerebral Cortex 2022). And the ATL is a FLEXIBLE context-dependent hub, NOT fixed
  prototypes (Cerebral Cortex 2023) -- which is why multi-prototype is NOT the faithful answer and hierarchical/
  contextual prediction IS. BUILT and tested within-clause (finding 8).
- **OUR-INVENTION-UNDER-TEST (swept, not adopted):** the role-specific CENTROID as the selectional-preference
  instantiation (this IS the literature-standard thematic-fit model, Santus et al. 2017 EMNLP -- prototype of
  the verb's role fillers); the softmax TEMPERATURE; the grounded space as the feature basis; the learned
  linear forward map (ridge; the Rao-Ballard generative-prediction instantiation) for the agent+verb composition.

Data: REAL modern-text predicate-argument triples from QA-SRL v2 (deliberately NOT the ~200-year-old McGuffey
corpus -- the age confound the brief warns about does not apply). Six cells:

1. `exp_predictive_reader_anticipation_surprisal_v1` -- the headline (Route A + a Route-B correlation). Verb
   (+role) pre-activates the expected argument's grounded features; readout is -log P over 20 frequency-matched
   candidates. Arms: PREDICTIVE (verb-role centroid), REACTIVE_FEAT (global role centroid, no verb), REACTIVE_FREQ
   (pure base rate), WRONG_VERB (info-free twin: the verb->expectation binding scrambled). Field-standard
   pseudo-disambiguation accuracy added for comparability.
2. `exp_predictive_reader_context_agent_verb_v1` -- the Bicknell fidelity refinement. A learned linear forward
   map predicts the patient's features from [verb centroid] vs [verb centroid ++ agent features]; agent-shuffled
   twin.
3. `exp_predictive_reader_surprisal_difficulty_signal_v1` -- Route B as a distinctive difficulty signal. The
   predictor's role-assignment MARGIN (true vs swapped agent/patient under the verb's agent- and patient-centroids)
   should collapse on REVERSIBLE (both-animate) sentences; validated against an INDEPENDENT animacy resource.
4. `exp_predictive_reader_precision_weighting_v1` -- the deeper-drill fidelity build: each verb-role's precision
   (concentration / inverse argument-entropy of its selectional-preference distribution) modulates the size of the
   predictive advantage (finding 7).
5. `exp_predictive_reader_hierarchical_topdown_v1` -- the brain-foundational build: a context hierarchy (reactive
   -> verb -> verb+agent -> +event) where each higher level top-down sharpens the argument prediction (finding 8).
6. `exp_predictive_reader_discourse_hierarchy_v1` -- THE REAL BUILD: reconstructs modern documents from QA-SRL,
   runs the `n400_coherence_monitor` to maintain a running situation model, and shows the event model top-down
   conditions the word-level predictor ACROSS sentences (finding 9).

## What I measured (all CI'd; reverify = the witness, PASS 8/8)

1. **ROUTE A -- the predictive reader beats an identical reactive reader AND the info-free twin, CI-separated,
   on held-out real text.** n=45,438, 3 seeds. Surprisal (lower = better anticipation): PREDICTIVE 3.178
   [3.170, 3.185] vs WRONG-VERB twin 3.273 [3.266, 3.280] (margin +0.095 [+0.087, +0.104], half-width 0.0085)
   vs REACTIVE_FEAT 3.377 (margin +0.199) vs REACTIVE_FREQ (margin +5.1). **BAR ROUTE A MET.**

2. **The field-standard pseudo-disambiguation metric agrees, and the twin is exactly at chance.** (Rooth 1999;
   Erk & Pado 2010; chance 0.5.) PREDICTIVE 0.589 [0.585, 0.594] vs WRONG-VERB twin 0.514 [0.510, 0.519], margin
   +0.075 [+0.070, +0.081]. Top-1 accuracy (chance 0.05): PREDICTIVE 0.076, REACTIVE_FEAT 0.047, WRONG-VERB
   0.049 -- **only the verb-conditioned arm clears chance**; the global centroid and the twin are at chance, so
   the win requires verb-specific pre-activation and cannot be a metric artifact.

3. **ROUTE B(i) -- surprisal is a valid graded difficulty signal against an INDEPENDENT measure, twin at zero.**
   Per-candidate PREDICTIVE surprisal tracks the distributional thematic-fit (co-occurrence PMI, a different
   information source than the grounded features): Spearman 0.239, shuffled-verb twin 0.026 (~0). **BAR ROUTE B
   MET.**

4. **BICKNELL FIDELITY -- the fuller context (agent+verb) sharpens the prediction over the verb alone.**
   n=16,654. MAP_VERB_AGENT surprisal 3.033 vs MAP_VERB 3.070 (agent helps +0.037 [+0.034, +0.040]); the
   agent-SHUFFLED twin (3.077) is if anything slightly WORSE than verb-only -- a wrong agent mildly misleads.
   The brain's compositional agent+verb->patient prediction reproduces on real text.

5. **ROUTE B(ii) / UNIFICATION WITH THE RELCL PROBLEM -- the surprisal margin flags "semantics cannot resolve
   this; hand it to syntax."** n=4,954 held-out. The predictor's role-assignment margin discriminates REVERSIBLE
   (both animate; hard) from IRREVERSIBLE (inanimate patient; easy) role assignment: AUC 0.619 [0.597, 0.644],
   reversible mean margin 0.086 (near zero == genuinely ambiguous) vs irreversible 0.245 (+0.159 [+0.123, +0.195]).
   The shuffled-verb twin (AUC 0.537) retains only a generic agent-animacy signal; the verb-specific predictor
   beats it. This is the SAME regime the relcl SOLVED proved needs a syntactic filler-gap parser -- the two
   problems unify: a SEMANTIC forward predictor resolves IRREVERSIBLE role assignment and its own surprisal
   FLAGS the reversible cases it cannot, which are exactly the ones syntax must carry.

6. **HONEST SIZE.** The effect is real and CI-separated on every metric but MODEST in absolute terms
   (pseudo-disambiguation 0.589 vs 0.5; top-1 0.076 vs 0.05). The ceiling is the coarse 12-dimension grounded
   feature space (11 sensorimotor means + concreteness), which under-resolves the fine argument distinctions a
   richer space would separate. This is the project's standing representation-quality coupling (p1): the
   prediction MACHINERY is correct and buildable now; its PAYOFF scales with representation quality.

7. **PRECISION-WEIGHTING -- the predictive advantage scales with the verb's selectional-preference PRECISION
   (constraint strength), the center of predictive coding the flat-temperature predictor was missing.**
   (`exp_predictive_reader_precision_weighting_v1`, n=44,304, 4,716 verbs, 3 seeds.) Precision = the
   concentration of a verb's argument grounded-feature distribution (mean cosine of its train args to their
   centroid; the (inverse) argument ENTROPY). HIGH-precision (sharp) verbs give a predictive benefit of 0.157
   over the info-free twin vs 0.046 for LOW-precision (diffuse) verbs -- margin +0.110 [+0.089, +0.131]
   CI-separated (pseudo-disambiguation benefit +0.042 [+0.028, +0.056]; Spearman(precision, benefit) 0.082,
   shuffled -0.001). This is Friston precision-weighting / Kuperberg-Federmeier constraint strength, reproduced:
   a sharp prediction carries the benefit; a diffuse verb ("get/have/take") carries almost none. It also
   EXPLAINS finding 6's modest average -- the aggregate is DILUTED across low-precision verbs that appropriately
   do not predict (the brain predicts SELECTIVELY, by expected utility; Kuperberg & Jaeger 2016). The prediction
   is faithful AND its precision structure is faithful.

8. **HIERARCHICAL TOP-DOWN PREDICTION -- the brain-foundational architecture, not the cheap follow-ons.**
   (`exp_predictive_reader_hierarchical_topdown_v1`, n=15,921 held-out, 3 seeds.) Prediction in the brain is
   hierarchical: the higher-level EVENT/situation model top-down predicts the lower-level lexico-semantic
   representation ("Predictive coding across the fronto-temporal hierarchy", Cerebral Cortex 2022). I built a
   CONTEXT HIERARCHY predicting the patient's features and each higher level of context sharpens the prediction
   MONOTONICALLY, CI-separated at every step: L0 reactive 3.357 -> L1 verb 3.063 (verb over reactive +0.294) ->
   L2 verb+agent 3.025 (agent over verb +0.038 [+0.035, +0.041]) -> L3 +EVENT 2.981 (event over verb+agent
   +0.044 [+0.041, +0.047]; TOP over local verb +0.082 [+0.078, +0.086]). The EVENT level (the running-gist the
   N400 monitor uses -- the mean grounded vector of the sentence's other content words) adds MORE than the agent
   did, and the SHUFFLED-event twin loses (+0.058 [+0.054, +0.062]). This is the hierarchical predictive-coding
   signature: higher-level context top-down improves the lower-level argument prediction. It is measured WITHIN
   single clauses (thin event context); the full gain needs cross-sentence DISCOURSE, which composes THIS
   word/feature predictor with the already-built EVENT-level `n400_coherence_monitor` -- the missing top-down link
   between two organs we already have. (BUILT next, finding 9.)

9. **THE REAL BUILD -- the CROSS-SENTENCE DISCOURSE hierarchy: the event/situation model top-down conditions
   the word-level predictor, and it WINS.** (`exp_predictive_reader_discourse_hierarchy_v1`, n=5,622 held-out
   target patients, split BY DOCUMENT, 3 seeds.) I reconstructed real modern documents from QA-SRL (sentenceId =
   SOURCE:DOC_SENTNUM regroups sentences into ordered documents; GOLD arguments), ran the ACTUAL
   `hdlab.n400_coherence_monitor` across each document to maintain a running SITUATION MODEL (the event gist,
   reset at boundaries), and used that gist to top-down condition the argument predictor. Predicting a patient
   from [verb + agent + the running EVENT gist as-of-before-its-sentence] beats [verb + agent] alone: DISCOURSE
   surprisal 2.863 vs LOCAL 2.950, margin +0.088 [+0.081, +0.095] CI-separated. The info-free twin (the gist from
   a RANDOM other document) does not just fail to help -- it HURTS (2.988, worse than local by 0.038), so the
   discourse channel carries genuine document-specific predictive information. This composes the two organs into
   the real fronto-temporal generative hierarchy across sentences. **THE REAL BUILD IS DONE and it works.**
   - **HONEST DISSOCIATION (a real sub-finding): for PREDICTION, a whole-document (no-reset) gist is marginally
     BETTER than the event-reset gist (NORESET 2.832 vs DISCOURSE 2.863, -0.031 [-0.035, -0.026] CI-separated).**
     The event-boundary RESET is load-bearing for the coherence monitor's SEGMENTATION job (proven in the prior
     problem) but the top-down PREDICTIVE signal integrates over a LONGER time-scale than the segmentation signal
     -- consistent with the multi-timescale fronto-temporal hierarchy (different levels, different windows). Both
     the reset and no-reset discourse gists beat local; the twin loses to both.

## Is this truly brain-faithful, machinery-in-proximity too? (the drills' verdict)

YES on the operation, with the proximate machinery audited:

- **The core operation is faithful and, unusually, LOCUS-faithful.** Predicting an argument's grounded features
  from the verb is an anterior-temporal-lobe (entity conceptual features) + angular-gyrus (verb+noun event
  combination) computation (fMRI: verb-argument thematic prediction localises there, distinct from the IFG
  structure stream). So predicting in our grounded (ATL-spoke) space matches not just the behaviour but the
  brain region. The role-specific centroid IS the literature-standard thematic-fit model (Santus 2017).
- **The proximate machinery has the ERROR half but was missing the FORWARD half.** `n400_coherence_monitor.py`
  (built, p-prediction-error problem) computes error against the RUNNING GIST -- a BACKWARD-looking event-
  coherence / segmentation signal, NOT a top-down next-item predictor. My forward predictor is the missing
  complementary half. Together they are the brain's two-level predictive hierarchy: a fast WORD/FEATURE
  predictor (temporal cortex; this build) feeding a slower EVENT predictor (frontal; the coherence monitor).
- **`predictive_coding.py` is RIGHT-OP-WRONG-METRIC and I did NOT route through its defect.** Its residual is on
  a `sign()`-quantised prediction (big and small mismatches indistinguishable) with no precision term. My
  surprisal is GRADED, in the CONTENT space, and in -log P form -- the exact corrections the audit and the
  prior N400 problem already identified.

## What would change in hdlab (proposed; the strategy session lands it, Q111)

- **BUILD the forward-prediction organ (the missing WORD/FEATURE level of the predictive hierarchy).** A module
  that, at each verb (and each argument slot), pre-activates the expected argument's grounded features from a
  role-specific selectional-preference table (verb x role -> centroid of grounded feature vectors), learned
  OFFLINE from a predicate-argument corpus (QA-SRL / a parsed corpus; a static offline-built asset is admissible
  per the pivot). Expose per-argument surprisal = -log P(actual | softmax competition among candidates) as a
  GRADED signal. ~1 small module + a precomputed table; reuses `grounded_similarity.grounded_vector`.
- **WIRE surprisal as shared difficulty infrastructure, not a one-off.** The per-word surprisal feeds: (a) the
  relcl route-CONFLICT / difficulty readout (surprisal flags where role assignment is ambiguous -> reversible ->
  needs syntax); (b) write-gating / salience; (c) the event-segmentation confidence in `n400_coherence_monitor`.
  Wire once, many consumers.
- **Condition on the ACCUMULATED context (agent+verb), not the verb alone (Bicknell).** The fuller-context
  predictor is CI-separated better; expose it as the default once the subject/agent is available in the register.
- **Do NOT predict word-FORMS, and do NOT route surprisal through `predictive_coding.predict`'s sign()-quantised
  residual.** Predict grounded FEATURES (the replicable level; Nieuwland); keep the residual graded and in the
  content space (the p1 coupling, already learned by the N400 problem).
- **EXPOSE PRECISION alongside surprisal (now validated, finding 7).** Precompute each verb-role's
  selectional-preference precision (the concentration / inverse argument-entropy of its grounded-feature
  distribution) and ship it beside the surprisal: the predictive benefit is real for HIGH-precision (sharp)
  verbs and near-zero for LOW-precision (diffuse) ones, so downstream consumers should TRUST the prediction in
  proportion to precision (Friston precision-weighting; Kuperberg-Federmeier constraint strength). This is a
  static per-verb scalar (cheap) and it turns "predict everywhere equally" into "predict where it pays"
  (Kuperberg & Jaeger expected utility). Full precision-weighted BELIEF UPDATING (a per-item learned precision)
  remains the harder follow-on the prior N400 problem flagged; the per-verb precision scalar is the buildable
  v1 and it is validated here.
- **Expect ROBUSTNESS, not a headline number, and MEASURE ON THE LIVE READER before any capability claim.** The
  isolation win is real but modest; its live value is a difficulty/anticipation signal downstream organs want,
  not a standalone accuracy jump. This is the project's standing isolation-vs-capability lesson.

## Which follow-ons are BRAIN-FOUNDATIONAL, and which are cheap tweaks (a 5th drill, on owner challenge)

The owner challenged the "cheap follow-ons" framing directly: "we do the RIGHT thing, not the cheap things -- are
those brain foundational?" A 5th drill (WebSearch, 2026-08-27) answered it, and it changed the plan:

- **MULTI-PROTOTYPE is NOT brain-foundational -- REJECTED.** The ATL is a FLEXIBLE, CONTEXT-DEPENDENT hub, NOT a
  set of fixed prototypes ("a flexible hub that enables context-sensitive semantic representation rather than fixed
  prototypical meanings", VLPFC modulating the hub by context; Cerebral Cortex 2023). Storing K discrete sense
  clusters would replicate a convenient NLP pattern, not the brain's mechanism. The brain's answer to polysemy is
  CONTEXTUAL modulation of one flexible representation -- which is the hierarchical/contextual direction below, not
  multi-prototype. Do NOT build multi-prototype.
- **ENTROPY / UNCERTAINTY-REDUCTION is a cost METRIC, largely SUBSUMED -- DEPRIORITISED.** It is a distinct
  reading-time predictor (Hale 2006), but the underlying MECHANISM (prediction uncertainty = inverse precision) is
  already built (finding 7). Entropy REDUCTION additionally requires incremental prediction, which folds into the
  hierarchical/continuous direction. Not an independent foundational mechanism.
- **HIERARCHICAL TOP-DOWN PREDICTION is THE brain-foundational thing -- so I BUILT it, within-clause (finding 8)
  AND the full CROSS-SENTENCE discourse version (finding 9, THE REAL BUILD).** Higher levels (event/situation)
  top-down predict lower levels (lexico-semantic); the residual is the N400 (Rao-Ballard; Friston; fronto-temporal
  hierarchy, Cerebral Cortex 2022). The discourse hierarchy composes the built `n400_coherence_monitor` (event
  level) with this word/feature predictor across real reconstructed documents and WINS CI-separated (finding 9).
  This was the right thing to build, and it is done.
- **The remaining foundational build: ENTITY-LEVEL discourse tracking (coreference in the situation model).** The
  discourse gist (finding 9) is a bag-of-content running mean; the brain tracks ENTITIES across sentences (who is
  "it"/"they"). Wiring the coreference organ (E3, NEEDS_ADAPTER) into the situation model so the top-down
  prediction is entity-structured is the next genuinely-foundational step -- a real build, and the correct next
  problem.
- **CONTEXTUAL (not static) features (p1).** Goldstein's embeddings are contextual; our grounded lookup is
  context-free. This is the representation-quality lane (p1), the same flexible-hub finding -- foundational but a
  different problem than the prediction loop.
- **RAW PRE-ACTIVATION vs NORMALISED SURPRISAL** (Nour Eddine 2023 vs Michaelov 2024) is a readout-form empirical
  question, resolvable only on human N400/RT data -- a validation detail, not a mechanism gap.

## KEY REALIZATIONS (the enabling moves)

- **The drills changed a build choice before I wrote a wrong version.** Nieuwland's failed FORM-prediction
  replication said: predict MEANING FEATURES, not the word. Had I built a next-WORD predictor (the obvious ML
  default) I would have chased the fragile half. Predicting grounded features -- and realising our coarse space
  is ALIGNED with the robust level -- is the move.
- **The apples-to-apples info-free twin is the wrong-VERB centroid, not a weak baseline.** My first "reactive"
  floor (the global centroid) was near-degenerate, and a wrong-verb centroid could beat IT while still losing to
  the predictor. Reframing the primary control as PREDICTIVE vs WRONG-VERB (identical machinery, only the
  verb->expectation binding scrambled) is what makes "the win is the RIGHT verb's pre-activation" airtight -- and
  the twin sits exactly at chance on the field-standard metric.
- **Switching to the field-standard pseudo-disambiguation metric (the fairness drill) made the result both fair
  and legible.** A 20-way ranking gave an uninterpretable absolute number; the standard attested-vs-corrupted
  accuracy (0.589 vs chance 0.5, twin at 0.514) is comparable to the literature and shows the twin at chance
  cleanly. Removing a mild base-rate leak (train-only frequencies) made the win CLEANER, not weaker.
- **The reversibility result unified this problem with the previous one.** Asking "when does the semantic
  predictor's surprisal spike for a ROLE reason?" led to: it cannot spike when both nouns fit equally (reversible),
  so its MARGIN collapsing to ~zero there IS the difficulty signal -- and that is precisely the regime the relcl
  parser exists for. One forward predictor produces both an anticipation win (irreversible) and a
  "hand-to-syntax" flag (reversible).
- **Reading what the PROXIMATE organ actually computes stopped a redundant build.** The N400 coherence monitor
  looks BACKWARD (error vs the running gist); this problem is the FORWARD half. Seeing that they are two levels
  of one hierarchy (rather than the same thing) is what makes the wiring proposal coherent.

## What I did NOT establish (and would withdraw first if wrong)

- **This is a held-out anticipation + difficulty-signal result on real predicate-argument pairs, NOT a
  demonstrated live-reading gain.** The FIRST thing I would withdraw is any implication that wiring this moves a
  live QA/comprehension number; it must be measured on the live reader. Its value is the difficulty/anticipation
  SIGNAL, and the anticipation effect is modest.
- **The effect size is small (pseudo-disambiguation 0.589, top-1 0.076).** I attribute the ceiling to the coarse
  grounded space, but I did NOT prove that a richer space lifts it -- that is a hypothesis (the p1 coupling),
  testable but untested here. If a reviewer holds that a small effect is not a "win", the CI-separation and the
  twin-at-chance are clean, but the magnitude is honestly low.
- **Surprisal was validated against a distributional/plausibility difficulty proxy and an animacy-based
  reversibility label, NOT against human reading times or N400 amplitudes.** These are legitimate proxies (the
  bar lists "a human reading-time proxy") but they are proxies; I did not run real RT/ERP data.
- **The reversibility twin is not fully at chance (AUC 0.537).** A wrong-verb centroid retains a generic
  agent-animacy signal, so that control is weaker than the anticipation twin (which IS at chance). The clean
  twin-at-zero claim rests on the anticipation and the Spearman-vs-fit controls; the reversibility result is
  reported with its residual-signal caveat.
- **The predictor is a role-specific PROTOTYPE (centroid) selectional-preference model.** It is the literature
  standard, but I did not exhaustively compare it against exemplar or fully-learned-map alternatives beyond the
  agent+verb ridge; "the centroid is optimal" is not claimed.
- **The precision estimator is OUR-INVENTION, swept not proven optimal.** Precision = mean cosine of a verb's
  train args to their centroid (resultant concentration). It reproduces the constraint-strength effect
  CI-separated, but the per-verb Spearman is weak (0.082, noisy per-verb benefit estimates); the clean signal is
  the tercile contrast. A better precision/entropy estimator is future work, not claimed here.
- **No hdlab change was built or landed** -- proven in experiments/ + verification/; the diff is proposed for the
  strategy session (Q111).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **Tier 5 "FEED-FORWARD where the brain is PREDICTIVE" (the top deviation, line ~84) now has a built, validated
   FORWARD predictor and a build spec.** Sharpen: a role-specific grounded-feature forward predictor (verb -> the
   expected argument's ATL-spoke features; the literature-standard thematic-fit prototype) with -log P softmax
   surprisal beats an identical reactive reader and an info-free wrong-verb twin on held-out real QA-SRL
   anticipation (surprisal +0.199 vs reactive; pseudo-disambiguation 0.589 vs twin 0.514 at chance), and its
   surprisal is a valid graded difficulty signal (Spearman 0.239 vs distributional fit; reversibility AUC 0.619).
   Effect is CI-separated but MODEST, ceiling'd by the 12-dim grounded space (p1 coupling).
2. **Tier 5 `predictive_coding.py` RIGHT-OP-WRONG-METRIC (line ~498): the FORWARD half is now built and it must
   be GRADED + content-space + -log P, NOT the sign()-quantised residual.** The forward predictor and the
   existing `n400_coherence_monitor` are TWO LEVELS of one predictive hierarchy: a WORD/FEATURE forward predictor
   (temporal/ATL-AG) and the EVENT-coherence monitor (frontal, backward-looking-gist). Recommend the audit record
   them as a hierarchy, not as competitors.
3. **NEW locus note:** verb-argument thematic PREDICTION localises to the ANTERIOR TEMPORAL LOBE (entity features)
   + ANGULAR GYRUS (verb+noun event combination), distinct from IFG (structure). Predicting in the grounded
   (ATL-spoke) space is locus-faithful, which strengthens the case for grounded-feature prediction over a
   form/lexical predictor.
4. **NEW cross-link to the relcl problem:** the forward predictor's role-assignment MARGIN is a gold-free
   difficulty signal that collapses on REVERSIBLE role assignment -- the exact regime the relcl filler-gap parser
   exists for. Semantics (this predictor) handles irreversible role assignment; its surprisal FLAGS the reversible
   cases for syntax. The two organs compose: surprisal-as-difficulty feeds the relcl route-conflict readout.
5. **PRECISION-WEIGHTING is validated and should be recorded as PINNED-and-built for Tier 5.** The predictive
   benefit scales with the verb's selectional-preference precision (constraint strength): HIGH-precision verbs
   +0.157 vs LOW-precision +0.046 over the info-free twin, CI-separated. This is the Friston precision term the
   `predictive_coding.py` audit line notes is MISSING ("no precision term") -- now shown to matter and estimable
   as a static per-verb scalar (inverse argument entropy). The remaining gap is per-item learned precision (the
   harder belief-updating form the prior N400 problem flagged), not the existence of a precision effect.

---

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT / SOLVED (owner-DONE). Full SOLVED re-read FRESH (standing rule).
Re-verified scaffold-free FIRST-HAND (verify_predictive_reader.py, 8/8 PASS: anticipation surprisal PRED 3.137 vs twin
3.275 +0.138 CI-sep; pseudo-disambig 0.575 vs twin 0.512 at chance; acc@1 0.081 vs twin 0.043; Spearman(surprisal,fit)
0.231 vs twin -0.001; reversibility AUC 0.585 vs twin 0.532; Bicknell agent+verb 2.998<3.024; precision high 0.135 vs
low 0.028 +0.106; hierarchical L0 3.364->L3 3.063 monotone + shuffled-event loses; discourse 2.889<local 2.966 +0.077 +
shuffled-discourse twin loses + reset<no-reset honest dissociation). BOTH bar routes met. The verb (+role) pre-activates
the expected argument's GROUNDED features (Altmann-Kamide/McRae), -log P softmax surprisal; beats REACTIVE +0.199 and the
info-free WRONG-VERB twin (IDENTICAL frequency structure, AT CHANCE -- the central frequency confound decisively
excluded). Glass-box (grounded features + verb key only). Five literature drills; precision-weighting (Friston) BUILT;
the full CROSS-SENTENCE discourse hierarchy composing the REAL n400_coherence_monitor across reconstructed documents
BUILT + WINS. HONEST modest size (12-dim grounded ceiling = the p1 representation coupling). UNIFIES with relcl (the
surprisal margin flags reversible cases for syntax). NO hdlab landed: the forward-prediction organ (verb x role ->
grounded-centroid table + -log P surprisal + per-verb precision scalar, offline-built static asset) is QUEUED as a
proven-ready default-off deliberate landing (a focused build, not a heartbeat-cram) -> composes into p1's wire-and-measure
+ feeds the relcl route-conflict; measure on the live reader before any capability claim. AUDIT UPDATEs folded (2b new
entry; tier-5 FEED-FORWARD->PREDICTIVE now built + predictive_coding forward-half-built-graded; ATL/AG locus; relcl
cross-link; precision PINNED-and-built). Solver's named next build (ENTITY-LEVEL discourse tracking = wire coref into the
situation model) packaged as a new problem to restore the >=3 floor. Review EXCELLENT + SOLVER REVIEW in PROBLEM.md;
priority cleared. Committed.
6. **The forward predictor and the `n400_coherence_monitor` are two levels of ONE hierarchy, and the top-down
   link is now BUILT and shown to WIN -- across sentences.** A within-clause context hierarchy (reactive -> verb
   -> verb+agent -> +event) sharpens the prediction monotonically CI-separated (finding 8), AND the full
   CROSS-SENTENCE discourse hierarchy -- the `n400_coherence_monitor`'s running situation model top-down
   conditioning the word-level predictor over reconstructed documents -- beats local +0.088 CI-separated with the
   shuffled-document twin actively hurting (finding 9). Recommend the audit record: (a) these two organs form a
   validated generative hierarchy (compose them); (b) a real DISSOCIATION -- the event-boundary RESET helps
   SEGMENTATION but a longer no-reset window helps PREDICTION (-0.031 CI-sep), i.e. prediction integrates over a
   longer time-scale than segmentation; (c) MULTI-PROTOTYPE is NOT the faithful answer to polysemy (the ATL is a
   flexible context-dependent hub, not fixed prototypes; Cerebral Cortex 2023) -- context/hierarchy is the
   direction, not sense-clustering. The next foundational build is ENTITY-LEVEL discourse (coreference, E3) in the
   situation model.

---

## TLDR
Our reader only reacted to words; the brain guesses the next one before it arrives, and how surprised it is is a
core difficulty signal. I built that: the verb pre-activates the MEANING features of the argument it expects
(the classic "eat -> something edible"), and the gap to the actual word is the surprise. On tens of thousands of
held-out real sentences it predicts the next argument better than a reader with no expectation and better than a
scrambled copy of itself (which sits at pure chance), and its surprise is a genuine difficulty signal -- it even
collapses to "I can't tell" exactly on the reversible sentences that my last problem showed need grammar, not
meaning. Five checks (a general brain-science drill, a finer one, a fairness drill, a deeper predictive-coding
drill, and a foundationality drill) confirmed the mechanism is faithful down to the brain region and fair by the
field's own standard test; that the predictor helps MORE for verbs that make a SHARP prediction ("eat") and barely
at all for vague ones ("get") -- the "predict harder when the context is constraining" effect at the heart of the
brain's prediction machinery; and, doing the RIGHT thing rather than the cheap one, that the full brain
architecture -- the running story-so-far steering the guess about the next word ACROSS sentences -- genuinely
improves the prediction on real documents. The one honest caveat: the AVERAGE win is real and clean but SMALL,
precisely because it is (correctly) concentrated where the context is constraining -- the machinery is right and
ready; its payoff grows with a richer meaning space.

## QUESTIONS
None. One judgement call for the owner at integration: the anticipation effect is CI-separated on every metric
(surprisal, the field-standard pseudo-disambiguation, and top-1) with the info-free twin at chance, but it is
MODEST in absolute size (pseudo-disambiguation 0.589 vs 0.5), ceiling'd by the coarse 12-feature grounded space.
I read the bar as clearly MET (both routes, controls clean, twin losing). If you weight absolute magnitude over
CI-separation, the honest framing is "the forward-prediction machinery is correct and validated; its payoff
scales with representation quality (p1)" rather than "a large standalone win".

## NEXT STEPS
1. Land the forward-prediction organ (role-specific grounded-feature selectional-preference table + -log P
   surprisal) behind a flag; expose surprisal as a shared graded difficulty signal. Do NOT predict word-forms;
   do NOT route through the sign()-quantised residual. Measure on the LIVE reader, not in isolation.
2. Wire the surprisal signal to the relcl route-conflict readout (it flags reversible role assignment for syntax)
   and to the N400 event-segmentation confidence -- one signal, several consumers.
3. Default to the agent+verb (fuller-context) predictor once the subject is in the register (Bicknell; CI-separated
   better than verb-only).
4. Test the p1 hypothesis directly: re-run the anticipation on a RICHER meaning representation and check the modest
   effect grows -- this is the claimed ceiling and it is testable.
5. Ship the per-verb PRECISION scalar beside surprisal (validated, finding 7): trust the prediction in proportion
   to constraint strength.
6. The DISCOURSE-level generative hierarchy is BUILT and validated (finding 9) -- land it by composing the
   `n400_coherence_monitor` (event level) with the word-level predictor across sentences, using the NO-RESET
   (longer-window) gist for the predictive channel and the RESET gist for segmentation (the dissociation). DO NOT
   build multi-prototype (the ATL is a flexible context-dependent hub, not fixed prototypes); entropy-reduction is
   subsumed by precision + incremental prediction.
7. OPEN THE NEXT foundational problem: ENTITY-LEVEL discourse tracking -- wire the coreference organ (E3,
   NEEDS_ADAPTER) into the situation model so the top-down prediction is entity-structured (who is "it"/"they"),
   not a bag-of-content running mean. This is the correct next build.
