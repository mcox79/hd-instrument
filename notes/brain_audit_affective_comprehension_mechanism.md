# Brain-foundational audit: how affective/goal meaning is comprehended from narrative text

Date: 2026-08-05
Author: research (Sonnet, lit-scan + synthesis)
Scope: mechanistic decomposition of (a) contextual word-affect, (b) maintained character affect/goal
state, (c) irony/incongruity, (d) goal-owner / affected-party attribution, from narrative text.
Status: literature synthesis, deflated per lit-scan calibration penalty (see footer). Reference doc for
synthesis against `hdlab` Component-3/5 goal-owner pipeline — not itself a design or a build.

---

## 0. Headline answer to the load-bearing question

Affective word meaning is **not a lookup table**. There is no evidence for a static word->valence
dictionary implemented anywhere in the language system. The converging picture across embodied
semantics (Barsalou), constructionist affect (Barrett), and hub-and-spoke semantics (Lambon Ralph) is:
word forms retrieve **modality-general conceptual representations** in a transmodal hub (anterior
temporal lobe, ATL), which are **grounded** by re-activating distributed valuation/interoceptive/
sensorimotor "spoke" systems (OFC/vmPFC, insula, amygdala, motor/premotor cortex) — and the specific
mix of spokes activated, and the *reading* given to the hub concept, is **actively selected/shaped by
context** via a separate controlled-retrieval system (IFG + pMTG, the "semantic control network").
A dictionary lookup only reproduces the *decontextualized default sense*; every one of the four
target phenomena (contextual disambiguation, implicit/sparse affect, irony, goal-owner attribution)
is precisely the class of thing a fixed lookup cannot do, and precisely the class of thing the
control network + situation model + mentalizing network exist to do. This maps directly onto the
observed substrate failure mode (fixed word->valence table breaks on "studied hard", idiom,
implicit dread, irony) — the fix implied by the biology is not a bigger/better table, it is a
**controlled retrieval + situation-model-constrained reweighting process**, i.e. an active inference
step, not a static resource.

---

## 1. Subsystem-by-subsystem decomposition

For each subsystem: NAME/region, COMPUTATION, POSITION/ORDER, OBJECTIVE/METRIC, LEARNING/PLASTICITY.

### 1.1 Wordform / lexical access (early, feedforward)

- **Region/circuit**: left posterior middle temporal gyrus (pMTG) + inferior occipito-temporal
  (visual word form area, for reading) -> superior temporal sulcus/gyrus (for auditory).
- **Computation**: maps orthographic/phonological form to a distributed lexical-semantic address;
  begins ~150-250ms post-word-onset (N400 window reflects the *cost* of this + subsequent integration,
  not this stage alone).
- **Position**: first, essentially feedforward from sensory cortex, but immediately modulated by
  top-down predictions (see 1.6).
- **Objective**: fast, coarse activation of the candidate lexical-semantic space — recall, not
  precision; ambiguity is *not* resolved here, all senses/associates are transiently co-activated
  (well-established in lexical ambiguity literature, e.g. Rodd, Duffy, Swinney's classic cross-modal
  priming showing multiple-sense activation immediately post-onset regardless of context).
- **Learning**: statistical/distributional learning across the lifespan (frequency, co-occurrence);
  slow, experience-driven tuning of form-to-meaning mapping (consistent with distributional-semantics
  models like word2vec/BERT as a *partial* computational analogy for this stage only — NOT for later
  stages).

### 1.2 Transmodal semantic hub (ATL) — hub-and-spoke model

- **Region/circuit**: bilateral anterior temporal lobes (ATL), especially ventral/lateral ATL;
  connected via uncinate fasciculus to frontal/limbic spokes.
- **Computation**: integrates modality-specific "spoke" representations (visual, auditory,
  sensorimotor, valuation/affective, praxic) into an amodal, graded conceptual representation — the
  hub-and-spoke architecture (Patterson, Nestor & Rogers 2007; Lambon Ralph et al. 2010, 2017).
  Damage here (semantic dementia) causes a graceful, modality-independent semantic degradation that
  a pure feature-list or pure modality-specific model cannot explain — strong evidence the hub is a
  genuine dimensionality-reducing convergence zone, not a router.
- **Position**: receives converging input from spokes (sensory, motor, affective/valuation cortex)
  and from the lexical stage; feeds forward to control network and to situation-model integration.
  Bidirectional with spokes — concept activation *re-activates* the spokes (grounding/simulation),
  it does not just summarize them.
- **Objective**: coherence/graded-similarity representation that supports generalization across
  instances (cross-modal, cross-context) while remaining partially groundable — i.e. minimizes
  representational cost while preserving enough spoke-linkage for re-simulation.
- **Learning**: developed via statistical convergence over co-occurring multimodal experience
  (semantic cognition connectionist models, Rogers & McClelland 2004); hub organization itself
  appears to emerge from graph-theoretic properties of ATL's convergent white-matter connectivity
  (small-world/hub topology), not innately specified per-concept.

### 1.3 Affective/valuation grounding spokes

- **OFC / vmPFC (orbitofrontal / ventromedial prefrontal cortex)**: computes a common-currency
  **value/valence estimate** integrating multiple attribute dimensions (Rangel, Camerer & Montague
  2008 — value-based decision framework; Rolls 2000 on OFC reward/punishment representations).
  Object/word/scenario -> value signal. This is where "goodness/badness for the agent" is computed,
  not retrieved.
- **Amygdala**: rapid salience/threat-relevance + fear/arousal tagging; also implicated in
  reward/appetitive salience, not purely negative (LeDoux; Cunningham & Brosch 2012 salience-network
  account of amygdala function in evaluation broadly, not "fear module" narrowly).
- **Anterior insula (AI)**: interoceptive representation — bodily-state simulation associated with
  the concept/scenario (Craig 2009 "how do you feel" — interoceptive predictive model; Critchley &
  Garfinkel 2017). Central to constructionist accounts of emotion (Barrett) where affect = a
  prediction about interoceptive state, not a categorical readout.
- **Computation (grounding spokes collectively)**: they don't classify a word into a fixed
  valence bin; they **simulate** the bodily/motivational consequence the word/scenario implies,
  producing a graded, context-sensitive value/arousal estimate. This is why "studied hard" and "hit
  hard" produce different value simulations from the identical token "hard" — grounding is keyed to
  the *situated scenario* (what is "hard," in what frame), not the token.
- **Position**: parallel spokes downstream of/interleaved with ATL hub activation; feed forward into
  situation-model affect state (1.5) and receive top-down constraint from context/prediction (1.6).
- **Objective/metric**: minimize prediction error on expected homeostatic/motivational consequence
  (allostasis — Barrett's predictive account); i.e. "correct" = accurately anticipates the
  organism-relevant consequence of the situation, not matching a lexicon entry.
- **Learning**: reinforcement-learning-like plasticity in OFC/amygdala/insula from lived
  interoceptive-outcome pairing across development ("core affect" is constructed from repeated
  interoceptive experience per Barrett's constructionist theory — not a small fixed set of innate
  "basic emotions" as in Ekman's classical view, which is the *contested* alternative — see Section 3).

### 1.4 Semantic control network (contextual disambiguation) — THE key subsystem for the substrate's failure mode

- **Region/circuit**: left inferior frontal gyrus (IFG, esp. BA45/47) + posterior middle temporal
  gyrus (pMTG) + dorsomedial prefrontal cortex (dmPFC), sometimes framed as overlapping the multiple-
  demand/domain-general control network intersected with semantic regions (Jefferies 2013 "the
  neural basis of semantic cognition" controlled-semantic-cognition (CSC) framework; Noonan, Jefferies
  et al. 2013; Badre & Wagner 2007 on IFG selection-among-competitors).
  Under this framework the hub (1.2) alone gives you the *default, most-typical* interpretation of a
  concept; IFG/pMTG bias retrieval toward the **contextually relevant** interpretation when the
  default is wrong or multiple candidates compete.
- **Computation**: (i) **selection among competing representations** (IFG, analogous to
  response-conflict resolution more generally — same circuitry implicated in Stroop-like
  interference), and (ii) **controlled retrieval of weak/nondominant associations** when strong,
  automatic (hub-driven) retrieval would be misleading — e.g., retrieving the effortful/laborious
  sense of "hard" in "studied hard" over the far more frequent injury/harm-adjacent physical-force
  sense. Homophone/polysemy resolution, idiom vs. literal selection, metaphor comprehension all
  recruit this network preferentially over literal/dominant-sense processing (meta-analytic evidence,
  e.g. Rapp et al. on metaphor; Vigliocco et al. on abstract/figurative language engaging control
  regions more than concrete/literal language).
- **Position**: **recurrent, not purely feedforward** — receives the hub's default activation plus
  top-down context/prediction (from situation model, 1.5, and predictive language mechanisms, 1.6),
  and *re-weights* which spokes/senses dominate. This is functionally a bias-competition process
  (Desimone & Duncan biased-competition applied to semantic retrieval), iterated as more context
  arrives (which is why disambiguation is often not resolved instantaneously but over a window of
  ~200-600ms and can be revised by later context — garden-path-like reanalysis for word sense).
- **Objective/metric**: **contextual relevance / coherence with the situation model**, not frequency
  or literal match — the "correct" output is whichever sense/valence maximizes fit with the
  established discourse context, computed via top-down constraint satisfaction, closely related to
  the "relevance" construct in pragmatics (Sperber & Wilson) though the neural instantiation is
  domain-general cognitive control applied to semantic competitors.
- **Learning**: control-network engagement strength scales with control **demand** (semantic
  distance from dominant sense) — this is a control-allocation policy that is itself learned/tuned
  (conflict-monitoring/adaptive-control literature, ACC-IFG loop, see 1.8), but the *content* it
  operates over (which senses exist, their relative dominance) is inherited from 1.1/1.2's
  statistical learning. So: representations are learned by exposure statistics; the *arbitration
  policy* is learned by control-demand history (harder, more effortful, more plastic — repeatedly
  disambiguating a given word/context pairing strengthens the non-dominant retrieval pathway,
  consistent with priming/adaptation effects in this network).
- **This is THE component most directly implicated in the substrate's exact failure mode.** A fixed
  word->valence table is architecturally equivalent to running only stage 1.1/1.2 (default/dominant
  sense) with no 1.4 (no controlled re-weighting toward the *contextually licensed* sense). The
  fix implied by the biology: valence must be computed by retrieval-with-competition constrained by
  the running situation model, not read off a static table, and there must be an explicit
  representation of "current strength of context-bias to override default sense."

### 1.5 Situation model / event model maintenance (working memory + DMN narrative network)

- **Region/circuit**: default-mode network (DMN) — medial prefrontal cortex (mPFC), posterior
  cingulate/precuneus, angular gyrus, lateral temporal cortex — increasingly implicated not as
  "task-negative noise" but as the substrate for **narrative/event situation models** (Baldassano et
  al. 2017 showed DMN regions represent event-level narrative structure at long timescales, with
  hierarchical temporal receptive windows: sensory cortex = short timescale/word-level, DMN =
  long timescale/scene-and-narrative-level). Working-memory maintenance recruits DLPFC/parietal in
  concert for the active, currently-relevant slice of the situation model.
- **Computation**: builds and updates a multidimensional **situation model** per Zwaan & Radvansky's
  event-indexing model (1998) — tracked dimensions are (1) protagonist/character, (2) temporality,
  (3) spatiality, (4) causation, (5) **intentionality** (goals/motivations of characters). A new
  sentence is integrated cheaply if it continues the same value on these dimensions (same
  protagonist, same time, same location, causally continuous, same goal-in-progress); a
  **discontinuity update** (more costly, measurable in reading-time slowdowns) is triggered when a
  dimension shifts — e.g. new protagonist, goal abandoned/achieved, causal break. This event-indexing
  dimension set is the most directly relevant piece of cognitive-science machinery for goal-owner
  attribution: intentionality is tracked as **its own first-class dimension bound to a
  protagonist-index**, exactly the "who owns this goal" representation the substrate needs, updated
  incrementally sentence-by-sentence rather than recomputed from scratch.
- **Position**: sits above the sentence-level semantic/affective processing (1.1-1.4); receives their
  output as updates and provides the **top-down context/constraint** that 1.4 uses to disambiguate.
  Recurrent loop: situation model biases word-level interpretation, word-level interpretation updates
  the situation model.
- **Objective/metric**: minimize integration cost / maximize coherence — "correct" state is
  whichever update keeps the five event-indexing dimensions maximally consistent with all evidence
  so far (a coherence/relevance-maximization objective, closely related to discourse-coherence
  theories, e.g. Centering Theory for the entity/protagonist-tracking sub-piece, Kintsch & van Dijk's
  construction-integration model for the broader coherence computation).
- **Learning**: the event-indexing dimension set itself (character/time/space/causation/intention) is
  argued to be a **relatively fixed cognitive architecture** (not learned per-story), acquired
  developmentally alongside general narrative competence (children show goal/intention tracking in
  narrative comprehension from ~3-4 years, well before literacy, per developmental ToM literature —
  i.e., a pre-linguistic scaffold that reading later hooks into, consistent with the "grounded ~6yo
  foundation reading builds on" framing already active in this project). The *content* filled into
  the dimensions per-story is of course fully online/episodic.

### 1.6 Predictive coding of language (throughout, recurrent)

- **Region/circuit**: distributed — implicated broadly across the language network (IFG, temporal
  cortex) with the N400 ERP component as the most-replicated electrophysiological signature.
- **Computation**: the brain continuously generates probabilistic expectations for upcoming words/
  meanings/affect given context (Kuperberg & Jaeger 2016 unify decades of N400/P600 literature under
  a predictive-processing account: N400 amplitude indexes ease of **semantic retrieval given
  prediction**, not simply "surprise" in a naive sense — it reflects pre-activation of features
  including, critically, **affective/evaluative features**, not just lexical identity). Federmeier &
  Kutas and later work show affect-congruent words are read faster/lower-N400 even when literal
  meaning is held constant, i.e. *valence itself is predicted*, not just computed post-hoc.
- **Position**: this is not a separate stage but a **modulatory signal present at every stage above**
  — it biases 1.1's initial activation, sharpens 1.4's competition (predicted sense gets a head
  start), and is generated by 1.5's situation model (the model licenses expectations about what
  should happen/be felt next). This is the mechanistic substrate of "implicit/sparse affect" (Section
  2.3 below): when no explicit valence word appears, the situation model's prediction of the
  emotionally-loaded next state is itself what carries the affective inference forward — affect can
  be **inferred from schema-consistent absence of expected relief/resolution**, not just read off
  present words.
- **Objective/metric**: minimize prediction error (surprisal) while maintaining a well-calibrated
  generative model of the discourse — classic predictive-coding/free-energy framing (Friston), applied
  to language specifically by Kuperberg & Jaeger.
- **Learning**: the predictive generative model is continuously updated via prediction-error-driven
  plasticity — both slow (statistical language learning across the lifespan) and fast (within-
  discourse, adapting expectations to the specific narrative's established schema/register within a
  passage — this is why irony works structurally, see 1.7/2.4).

### 1.7 Mentalizing / Theory-of-Mind network (goal & intention attribution, irony)

- **Region/circuit**: temporoparietal junction (TPJ, bilateral, right-lateralized dominance) +
  dorsomedial prefrontal cortex (dmPFC) + precuneus/posterior cingulate + (for affective ToM
  specifically) ventromedial PFC — the canonical mentalizing network (Saxe & Kanwisher 2003 on TPJ
  selectivity for belief representation; Frith & Frith 2006 review; Mar 2011 meta-analysis showing
  substantial overlap between narrative-comprehension networks and ToM/mentalizing networks —
  narrative comprehension IS largely an exercise of the mentalizing system when characters are
  involved).
- **Computation**: represents **other agents' mental states as distinct from the reader's own /
  from the literal world-state** — beliefs, desires, intentions, and (for irony specifically) the
  gap between a speaker's/character's **literal utterance** and their **communicative intent**.
  TPJ is specifically implicated in representing belief content that diverges from reality (false-
  belief tasks) and, by extension, in representing an utterance's *intended* meaning as distinct from
  its *literal* meaning (relevant models: the "echoic mention" / pretense theories of irony in
  pragmatics — Sperber & Wilson's relevance-theoretic echoic-mention account, and Gibbs' work on
  irony processing — converge on irony comprehension requiring representation of a **second, attributed
  perspective** against which the literal statement is evaluated as incongruent).
- **Position**: downstream consumer of 1.5's situation model (needs the established
  character/goal/context state to know what a "normal"/expected utterance would be) and of 1.6's
  prediction (irony is detected as a **violation** — literal-surface valence maximally mismatches the
  valence predicted by the situation model/character-goal state). This is a genuinely two-pass or
  parallel-competing-interpretation computation: literal meaning is computed (can't be fully
  suppressed — classic finding that literal meaning of irony is not fully inhibited even when
  intended meaning is understood, Giora's graded-salience hypothesis), and the intended meaning is
  computed via mentalizing-network inference over speaker/character state, with the **incongruity
  itself** (magnitude of literal-vs-attributed-intent mismatch, contextualized by the character's
  known stance) serving as the detector signal for irony rather than either reading alone.
- **Objective/metric**: minimize error in predicting *other minds*' internal states given behavior +
  context — a distinct optimization target from 1.3's valuation-for-self; this is valuation/state-
  estimation-for-other, computed via a structurally similar but separately implemented system
  (simulation-theory vs. theory-theory debate on mentalizing mechanism is itself contested, see
  Section 3).
- **Learning**: ToM/mentalizing capacity develops on a well-characterized ontogenetic timeline
  (explicit false-belief passing ~4yo; implicit/anticipatory-looking precursors earlier, ~15mo per
  some paradigms — contested, see Section 3) via social-interaction experience; the network's
  engagement during **reading** specifically (as opposed to live social interaction) is a later-
  developing transfer/reuse of the same circuitry (Mar 2011's narrative-ToM overlap finding), i.e.
  reading comprehension of character mental states is not a separate faculty but literally reuses
  the social-cognition mentalizing system — directly consonant with the project's own "does this
  reuse an existing brain circuit" discipline.

### 1.8 Anterior cingulate cortex (ACC) — conflict/incongruity monitoring

- **Region/circuit**: dorsal ACC, tightly coupled with IFG (1.4) and DLPFC.
- **Computation**: monitors for **conflict/incongruity between competing representations** (classic
  conflict-monitoring theory, Botvinick et al. 2001) and signals the need for increased control
  allocation. In the affective/narrative domain this is the plausible substrate for *detecting* that
  something is off (surface valence doesn't fit predicted valence — the irony/incongruity trigger)
  even before the mentalizing network has resolved *what* the correct reinterpretation is.
- **Position**: sits at the interface of 1.4 (semantic control), 1.6 (prediction), and 1.7
  (mentalizing) — a domain-general "surprise/conflict" alarm that recruits the domain-specific
  reinterpretation machinery (mentalizing for irony, controlled retrieval for word-sense) once
  tripped.
- **Objective/metric**: minimize downstream error by allocating control proportional to detected
  conflict — a resource-allocation policy, not a content computation.
- **Learning**: control-allocation policy tunable by conflict-frequency history (adaptive control);
  well-established in cognitive-control literature generally, less narrative-text-specific evidence
  directly, so this component's role in irony specifically is **inference from adjacent literature**,
  not directly demonstrated by an irony-specific ACC study — flag as moderate-confidence, not
  established.

### 1.9 Hippocampal relational/episodic binding (cross-sentence, cross-paragraph persistence)

- **Region/circuit**: hippocampus (relational binding, pattern separation/completion) + adjacent
  medial temporal lobe cortex.
- **Computation**: binds **arbitrary relational structures** — who did what to whom, when, where —
  into a retrievable episodic trace; critically, per Cohen & Eichenbaum's relational-memory theory,
  hippocampal binding is what allows **flexible, novel recombination** of previously-encountered
  elements (e.g., inferring a transitive relation never directly stated). For narrative comprehension
  this is the substrate for **maintaining character-state across long spans** (paragraphs, not just
  the current sentence) where working memory (1.5's WM component) alone would decay/overwrite.
  Distinguish: **working memory** = the actively-maintained, currently-in-focus slice of the situation
  model (limited capacity, rapidly updated, prefrontal/parietal); **hippocampal episodic memory** =
  the durable store that WM content consolidates into / retrieves from, supporting reference back to
  a character's established goal/affect state many sentences or pages later (anaphora/coreference
  resolution over long distances routes through this system, per relational-memory accounts of
  discourse coreference — directly the substrate this project's coreference_resolver module already
  targets, per the "coreference = hippocampal relational antecedent-retrieval" mechanism-identification
  already logged as a project anchor).
- **Position**: parallel store alongside WM; WM content is written to hippocampal binding
  continuously and read back when a discontinuity/callback requires retrieving an out-of-focus
  character/goal state (e.g., "she still hadn't forgiven him" many paragraphs after the original
  offense — requires binding "offense" to "her" as a persistent affective/relational fact retrievable
  on demand, not actively rehearsed the whole time).
- **Objective/metric**: maximize retrieval fidelity for relational structure under interference —
  pattern separation (keep similar-but-distinct episodes distinguishable) vs. pattern completion
  (retrieve a full episode from a partial cue) are the two competing sub-objectives, believed to be
  implemented by distinct hippocampal subfields (DG for separation, CA3 for completion).
- **Learning**: fast, one-shot (or few-shot) binding — hippocampal plasticity operates on a much
  faster timescale than cortical statistical learning (complementary learning systems theory,
  McClelland, O'Reilly & Norman), consistent with narrative comprehension being able to bind a
  character's goal/affect state from a *single* introductory sentence and hold it as a queryable fact
  for the rest of the text, rather than needing many repetitions the way word-level statistical
  learning does.

---

## 2. Load-bearing questions, answered directly

### 2.1 Lookup lexicon vs. grounded/embodied simulation?

**Grounded simulation, not lookup**, on convergent evidence from three largely independent research
programs:
- **Barsalou's Perceptual Symbol Systems / situated conceptualization**: concepts are represented
  by reactivating modality-specific states from perception/action/introspection, situationally
  assembled rather than stored as amodal fixed entries; behavioral evidence includes modality-
  switch costs, sensorimotor interference effects on comprehension speed.
- **Barrett's constructionist theory of emotion**: there is no fixed, universal "anger circuit" or
  fixed word->emotion-category mapping; emotional meaning is *constructed* per-instance from core
  affect (a graded, low-dimensional valence/arousal state, largely interoceptively grounded) plus
  conceptual knowledge plus context, on the fly — the emotion category (and its associated valence)
  assigned to a given experience or word can vary by culture, individual, and immediate context
  (variability data: the same facial expression / same word is categorized with different
  valence/category by different perceivers/contexts at rates incompatible with a fixed universal
  lookup).
- **Hub-and-spoke (Lambon Ralph)**: neuropsychological double dissociation data — semantic dementia
  patients lose graded, modality-general conceptual knowledge (consistent with hub damage) while
  retaining fluent lexical retrieval mechanics, which a pure-lookup-table architecture (in which the
  table itself IS the semantic content) cannot cleanly explain; conversely, damage to specific spokes
  (e.g., some FTD variants) causes modality-specific but not global semantic deficits.

**Implication for a fixed word->valence table**: it can only ever reproduce the *decontextualized
population-modal default*, and will be systematically wrong whenever (i) context licenses a
non-default sense (2.2), (ii) affect must be inferred rather than read off an explicit word (2.3),
or (iii) the surface sense is being used non-literally (2.4). These are not edge cases in narrative
text — per the constructionist account they are close to the *typical* case, since affect is always
constructed relative to a situation, and a lexicon captures only the situation-independent prior.

### 2.2 Contextual disambiguation ("studied hard" != harm; idiom != literal)

Mechanism = **1.4 semantic control network (IFG+pMTG) performing biased competition, constrained by
1.5's situation model and 1.6's predictive pre-activation.** Key empirical anchors:
- Rodd, Davis & Johnsrude (2005) and related fMRI work: ambiguous words with a **subordinate**
  (contextually-forced, non-dominant) sense selectively increase IFG/pMTG activity relative to
  dominant-sense or unambiguous controls — direct neural evidence that overriding a default sense is
  a distinct, effortful computation, not a side effect of lexical access itself.
- Giora's graded-salience hypothesis: the **most salient** (frequent/prototypical/foregrounded)
  meaning is activated regardless of context (even when context strongly favors a different meaning,
  the salient meaning shows some priming) — meaning *access* is not fully context-gated, but meaning
  *selection/use* is, via the control network suppressing/deprioritizing the inappropriate but salient
  candidate. This predicts measurable "residual" activation of the wrong (dominant) sense even in
  clear disambiguating context — relevant if the substrate wants to model confidence/uncertainty
  rather than hard either/or classification.
- Idiom comprehension specifically: literature (Cacciari & Tabossi; Vigliocco et al. neuroimaging
  meta-analyses) shows idioms engage similar control-network machinery as fresh metaphor when
  non-decomposable, but highly familiar/frozen idioms can become **direct-retrieval** items (i.e.,
  with enough exposure, "kick the bucket" -> death becomes closer to a stored unit, reducing reliance
  on live compositional control) — meaning the brain's solution is not "always run full context-
  control inference," it is "run control-mediated inference until repetition promotes a fast-path,"
  a graded automatization account (consistent with skill-acquisition literature generally, e.g.
  proceduralization).

### 2.3 Implicit/sparse affect (dread from "melancholy, hollow, a burden" with no explicit harm word)

Mechanism = **schema/situation-model-driven inference (1.5) + predictive pre-activation of the
implied consequence (1.6) + grounding-spoke simulation (1.3), combined — not any single word's stored
valence.** No single mechanism "reads" dread off these words; dread is the **integrated output** of:
(i) each content word (melancholy, hollow, burden) individually grounding to a *mildly* negative,
low-arousal, effortful/depleted simulation via 1.2/1.3 — none of them individually encode "harm" or
"danger," (ii) the situation model (1.5) aggregating these into a scene-level affective state via
coherence-maximization (multiple mutually-reinforcing low-grade-negative cues raise confidence in a
negative overall state disproportionately to any one cue — a Bayesian cue-integration process, well
established generally in perceptual cue-combination literature and argued to extend to
affective/semantic integration), and (iii) predictive machinery (1.6) extrapolating forward from that
integrated state toward an anticipated negative outcome — i.e., "dread" is specifically a
**prediction about a forthcoming negative event**, not a description of the current one, so it is
intrinsically a product of the predictive/situation-model layer, not retrievable from present-tense
lexical content at all. This strongly implies implicit affect cannot be solved by improving a word-
level detector no matter how rich; it requires an integrate-then-predict step operating over the
situation model.

### 2.4 Irony / narrative incongruity

Mechanism = **1.6 prediction generates an expected valence/outcome from the situation model; 1.8 ACC
detects the conflict when literal surface valence diverges sharply from that prediction; 1.7
mentalizing network resolves the conflict by attributing an *intended* (non-literal) meaning to the
speaker/character, using the same belief/intent-representation machinery used for social ToM
generally.** This is explicitly a **two-stage or dual-representation** process: literal meaning is
computed (and per Giora's graded-salience data, not fully suppressed even after resolution — readers
show residual access to the literal meaning of irony even when they've correctly inferred the
sarcastic intent), while the mentalizing-attributed intended meaning is computed in parallel/
subsequently and typically dominates for behavioral output (what the reader "concludes" the passage
means). The **detector signal** for irony is the *magnitude and directionality* of the
literal-vs-predicted mismatch, contextualized by what is independently known about the
speaker/character's likely stance (mentalizing must already have some prior model of the character to
know a compliment is *unlikely* to be sincere here) — meaning irony detection is not decodable from
the sentence in isolation; it requires (a) an established character-stance/situation-model state and
(b) an incongruity-detection step referencing that state, structurally identical to (a)+(b) needed
for goal-owner attribution (2.5) — both are situation-model-referenced inference, not sentence-local
classification.

### 2.5 Goal/intention attribution and who-is-affected

Mechanism = **1.7 mentalizing (TPJ/dmPFC) computes the intentional-state content; 1.5's situation
model (specifically Zwaan & Radvansky's INTENTIONALITY dimension) binds that content to a
protagonist-index and maintains it as a persistent, updatable fact; 1.9 hippocampal relational
binding stores/retrieves it across long spans.** Concretely, per the event-indexing model, every
clause is evaluated for whether it continues, advances, or violates the currently-tracked goal of the
currently-tracked protagonist; a shift in either protagonist-index or intentionality state triggers a
measurable processing cost (slower reading times / increased N400-family responses at
goal-discontinuity points — this is one of the more robust, frequently-replicated findings in the
situation-model literature, e.g. work following Zwaan, Magliano & Graesser 1995; Rinck & Bower on
goal-tracking in narrative). **Who-is-affected** (as distinct from who-holds-the-goal) requires the
mentalizing/situation-model system to additionally track a **second role** — the target/patient of an
action relative to a goal-holder's intent — which functionally is a **thematic-role x
intentional-state binding**: agent-with-goal vs. patient-of-goal-directed-action are represented as
distinct bound roles under the same event representation, not inferred post-hoc from surface word
order or verb morphology alone (this directly supports a frame-based, not positional, role
assignment architecture — consonant with the project's already-established finding that thematic
roles are frame-conditioned, not positional). Critically, goal-ownership binding is **maintained
across sentences as a standing situation-model fact**, retrievable and updatable (goal achieved /
abandoned / transferred to another character), not recomputed fresh each sentence — this is the
direct biological analog of "maintained character state," and its persistence mechanism is the
combination of active WM maintenance (while in focus) handing off to hippocampal relational storage
(while out of focus), per 1.9.

---

## 3. Contested vs. established (honesty flags)

- **Established, high-confidence**: hub-and-spoke ATL architecture (strong neuropsych double-
  dissociation evidence); semantic control network IFG/pMTG role in resolving weak/subordinate senses
  (converging fMRI + patient lesion data, e.g. semantic aphasia patients show control deficits
  distinct from semantic-dementia hub deficits); N400 as an index of contextual facilitation
  including affective congruence; TPJ role in false-belief/mentalizing representation; Zwaan
  event-indexing model's core claim that discourse updates are costlier across dimension-shifts
  (extensively replicated reading-time effect).
- **Established but actively debated on MECHANISM (not existence)**: whether emotion categories are
  natural kinds with dedicated circuits (classical/basic-emotion view, Ekman, Panksepp) vs.
  constructed from domain-general core-affect + concept knowledge (Barrett constructionist view). The
  constructionist view is better supported by the *within-category variability* and *context-
  dependence* data most relevant to this project (word/scenario affect is genuinely context-variable,
  not a fixed readout), but this remains a live, not fully settled, debate in affective neuroscience
  — treat "affect = constructed, not looked up" as well-supported but not unanimous consensus.
  DEFLATE weight accordingly if used to justify a specific architecture choice.
- **Established relation, contested boundary**: DMN's role as *the* narrative/situation-model
  substrate (Baldassano et al.) is a relatively recent (2017-era) and still-consolidating finding;
  robust that long-timescale narrative structure is represented hierarchically outside sensory
  cortex, less settled exactly which DMN sub-regions do which sub-computation.
- **Inference from adjacent literature, not directly demonstrated**: ACC's specific role in
  irony/incongruity detection (Section 1.8) is inferred from the general conflict-monitoring
  literature plus the logical need for *some* detector between prediction (1.6) and reinterpretation
  (1.7); I did not find (in this pass) an irony-specific ACC lesion/imaging study directly confirming
  this role as opposed to a related account (e.g., that IFG's own competition-resolution machinery,
  1.4, suffices without an additional ACC signal). Flag as moderate-confidence, worth a targeted
  follow-up search if the substrate build leans on an explicit incongruity-detector module.
- **Genuinely contested**: age of onset / mechanism of *implicit* ToM competence (violation-of-
  expectation infant paradigms suggesting precursors as early as ~15 months vs. the classical
  explicit false-belief milestone at ~4 years) — the developmental-mechanism debate is unresolved and
  not load-bearing for this project's adult-comprehension target, noted for completeness only.
- **Simulation-theory vs. theory-theory of mentalizing** (does the brain infer others' mental states
  by running its own decision/valuation machinery on their situation ["simulation"], or by applying
  learned folk-psychological rules ["theory-theory"]) — unresolved in the literature generally;
  relevant because it bears on whether goal/affect attribution to a *character* should be implemented
  by literally re-running the same valuation machinery used for the reader's own affect (simulation
  account, favors sharing 1.3's OFC/insula/amygdala machinery for character-state estimation too) or
  by a separate rule-based inference module. The overlap finding (Mar 2011, narrative comprehension
  substantially recruits the same mentalizing network as live social cognition) mildly favors a
  shared/simulation-flavored account, but this should be treated as a hypothesis, not settled fact.

---

## 4. Integrated end-to-end pipeline

```
wordform (1.1, feedforward, fast/coarse)
   |
   v
ATL semantic hub (1.2): amodal concept activation, ALL candidate senses/spokes initially co-active
   |                                              ^
   v                                              | re-simulation / grounding feedback
grounding spokes (1.3, parallel): OFC/vmPFC value, amygdala salience, insula interoception
   |  (produces graded, situation-relative value/arousal estimate per candidate sense)
   v
=== semantic control network (1.4, IFG+pMTG): biased competition among candidate senses/values ===
   ^                                              ^
   |  top-down bias                               |  top-down prediction
   |                                               |
situation model (1.5, DMN + WM): protagonist / time / space / causation / INTENTIONALITY dims
   ^        |                                      ^
   |        v (updates)                            |
   |  predictive coding (1.6): expectation for upcoming word/sense/affect, generated FROM situation
   |        |                  model, fed forward to bias 1.1/1.2/1.4
   |        v
   |  === CONFLICT CHECK (1.8, ACC): literal-vs-predicted mismatch magnitude ===
   |        |                                      |
   |        | (low mismatch: proceed)              | (high mismatch: trigger reinterpretation)
   |        v                                      v
   |  situation-model update              mentalizing network (1.7, TPJ+dmPFC):
   |  (affect/goal state revised           attribute INTENDED (non-literal) meaning;
   |   for current protagonist)            resolve irony / non-literal intent
   |        |                                      |
   |        +------------------<--------------------+
   |        v
   +--- hippocampal relational store (1.9): bind (protagonist, goal, affect-state) as a
        persistent, retrievable fact; write on update, read on later reference/callback
```

**Which components dominate at each stage:**
- **Single-word, in-isolation**: 1.1 -> 1.2 -> 1.3 (fast, largely feedforward, produces the
  *default* reading only).
- **Word-in-sentence-context, disambiguation-required**: add 1.4 (control) + 1.6 (prediction) as
  the dominant modulators — this is where "studied hard" gets resolved correctly, and where a fixed
  lookup table structurally cannot follow.
- **Sentence-in-discourse, implicit/cumulative affect**: 1.5 (situation model aggregation) + 1.6
  (predictive extrapolation) dominate; individual word-level valence becomes a minor input to a
  larger integration, not the answer itself.
- **Incongruity / irony**: 1.6 (predicted valence) x 1.8 (conflict detection) x 1.7 (mentalizing
  reattribution), gated by an established 1.5 character-stance prior — cannot fire correctly without
  that prior already in place.
- **Goal-owner / affected-party attribution**: 1.7 (mentalizing content) bound via 1.5's
  intentionality dimension to a protagonist-index, persisted via 1.9 across the discourse; this is
  the most purely *structural-binding* component of the four target phenomena — less about computing
  a value and more about correctly indexing WHO a computed value/state belongs to.

**Recurrence**: the diagram is not a single feedforward pass. 1.4/1.5/1.6 form a tight recurrent loop
that iterates as each new word arrives — situation-model predictions bias word-level resolution,
word-level resolution updates the situation model, continuously, which is why disambiguation and
affect-tracking are inherently online, incremental, revisable processes (garden-path-style revision
is possible at every level, not just syntax) rather than a single bottom-up-then-done computation.

---

## 5. Substrate-product implications (not framed as publication; direct architecture read)

1. **Do not fix contextual-valence failures by enriching a word->valence table.** The biology has no
   such table; it has a *default* (hub/dominant-sense) reading plus a *controlled override* process
   keyed to situation-model fit. The architectural analog: a base (context-free) valence estimate per
   token/lemma (playing the role of 1.1-1.3's default activation) PLUS an explicit re-weighting step
   that is a function of (current situation-model state, competing-sense candidates), structurally
   separate from the base estimate — not a bigger table, a second stage that can override the first.
2. **Implicit/sparse affect requires integration-then-prediction over several tokens, not a per-token
   detector however sensitive.** If the substrate's affect signal is computed token-by-token and then
   pooled, it will systematically miss "dread from melancholy+hollow+burden" cases UNLESS the pooling
   step itself does Bayesian-style cue integration (several weak congruent cues -> confident
   aggregate) AND a forward-projection step (aggregate state -> anticipated near-future valence,
   which is what "dread" actually denotes). This is a different computational demand than valence
   classification per se.
3. **Irony/incongruity detection is structurally a byproduct of having (a) a working situation-model
   affect prediction and (b) an explicit mismatch-magnitude computation between predicted and
   surface valence, gated by (c) an established character-stance prior.** Do not build irony
   detection as an independent classifier over surface features; it should fall out of the existing
   prediction-vs-observation machinery if that machinery is genuinely predictive (i.e., if the
   substrate's situation-model component actually generates a valence expectation before reading the
   next clause, not just a valence estimate after).
4. **Goal-owner attribution is a binding/indexing problem, not a valence problem**: the relevant
   biological analog (Zwaan intentionality dimension bound to protagonist-index, persisted via
   hippocampal-style relational storage) argues for keeping "who owns this goal" as a standing,
   explicitly-indexed situation-model slot that updates incrementally and is queryable across
   sentence boundaries — which is exactly the direction the project's Component-3 (frame-conditioned
   thematic roles) -> Component-5 (goal-owner selection/binding) pipeline is already headed, per prior
   in-flight work (MEMORY: "roles are FRAME-based not positional; goal-owner rides the
   SUBJECT-EXPERIENCER frame"). This literature independently supports frame/role-conditioned
   binding over positional heuristics, and further specifies that the binding must PERSIST (not be
   recomputed per-sentence) and must be an explicit dimension alongside protagonist/time/space/
   causation, not an emergent side-effect of coreference alone.
5. **Reuse-not-rebuild flag**: mentalizing-for-narrative substantially reuses live social-cognition
   mentalizing machinery (Mar 2011). If the substrate already has (or plans) a self/other or
   affect-attribution-to-self component, the biology recommends **sharing that mechanism** for
   character-affect attribution rather than building a parallel "fictional-character affect" module —
   directly consistent with the project's standing "which brain structure, does it reuse an existing
   process" discipline.
6. **Automatization pathway**: idiom/frozen-expression handling suggests the substrate should allow
   a fast-path direct-retrieval route for highly frequent fixed expressions (bypassing full
   compositional control-network-style inference), while keeping the full controlled-retrieval path
   for novel/rare non-literal usage — a two-speed design rather than either "always compositional" or
   "always table-lookup."

---

## 6. Cheap decisive test (falsifiable, brain-referenced)

**Test**: On a held-out set of sentences requiring (a) contextual sense override (e.g. "studied
hard"/idiom items), (b) implicit/sparse affect (no explicit polarity word, 3+ weak congruent cues),
(c) irony (surface-valence-inverted relative to established character stance), and (d) goal-owner
attribution across a 2-3 sentence span with a distractor character present — compare substrate output
under two conditions:
  1. **Baseline**: current/table-driven valence + positional role assignment (control condition,
     representing "stage 1.1-1.3 only, no 1.4/1.5/1.6/1.7/1.9").
  2. **Situation-model-gated**: valence/role assignment gated by an explicit situation-model state
     (protagonist index + intentionality dimension + running predicted-valence signal), i.e. adding
     the equivalent of 1.4-1.7/1.9.

**HARD-PASS** (biology-consistent, worth building out): condition 2 shows >=15 percentage points
absolute accuracy improvement over condition 1 specifically on the (b) implicit-affect and (d)
goal-owner subsets (the two subsets whose brain-analog literally cannot be solved without the
situation-model layer per Sections 2.3/2.5), with (a) and (c) subsets showing improvement but not
necessarily as large (since (a)/(c) have partial fast-path/table shortcuts available per Section 5.6
that (b)/(d) structurally lack).

**HARD-FAIL** (falsifies the "situation-model-gating is the fix" hypothesis, or reveals the gating
implementation is not actually capturing the mechanism): condition 2 shows <5 points improvement on
(b) and (d), OR shows improvement on (a)/(c) but NOT on (b)/(d) — the latter pattern would indicate
the substrate is correctly doing *contextual disambiguation* (a solvable-by-control-network problem)
while still failing *integration/prediction* (a genuinely different computational demand per Section
2.3), meaning the fix that was built addresses a different subsystem than the one actually
bottlenecking implicit-affect and goal-owner performance — a diagnostically useful failure, not a
dead end, since it would pinpoint which of 1.4 vs. 1.5/1.6 vs 1.9 is the still-missing piece.

**P_deflated estimate for "situation-model-gating closes most of the gap"**: 0.45 (novel-synthesis
cap applies: this is architecture-level synthesis across established literature, not a directly-
tested-in-narrative-AI claim; deflated from an undeflated confidence of ~0.65 per lit-scan calibration
penalty, since no direct precedent exists for this exact substrate applying this exact biological
decomposition).

---

## 7. Cross-thread synthesis with prior project entries

- Directly supports and specifies the mechanism behind `research_verb_affectedness_type_gate` and
  `research_word_grounding_lexicon_structure_content_unification` (both 2026-07): this audit provides
  the missing "why a fixed table fails" mechanistic account those threads needed, and names the
  specific replacement subsystem (semantic control network, not a richer lexicon).
- Directly extends `research_working_memory_integration_upper_limit_2026-07-16`: Section 1.5/1.9
  distinguishes WM-resident vs. hippocampal-relational-store situation-model content, which bears
  on capacity/decay questions from that thread — WM upper-limit constraints apply only to the
  actively-in-focus slice; long-range persistence (needed for "she still hadn't forgiven him" style
  callbacks) is a *different* (hippocampal-style relational) mechanism with different capacity
  characteristics, not subject to the same limit.
- Directly grounds the in-flight Component-3/Component-5 goal-owner pipeline work referenced in
  MEMORY (frame-conditioned role assignment, subject-experiencer frame): Section 2.5 independently
  arrives at frame/role-conditioned + persistently-bound goal-ownership from the situation-model
  literature, without reference to the project's own prior conclusions — convergent validation, not
  circular reasoning, since this synthesis was built from the neuroscience literature independently.
- Opens one clearly novel adjacency not previously drilled per the field-advisor scan: **irony/
  incongruity detection as a byproduct of predictive-coding mismatch (Section 2.4/5.3)** — this
  reframes irony from "a special-case classifier problem" to "a diagnostic side-effect of a properly
  predictive situation-model," which if correct removes the need for dedicated irony-detection work
  once (b) implicit-affect and (d) goal-owner infrastructure exists. Recommend flagging this as a
  candidate for the cheap decisive test in Section 6 rather than separate dedicated build effort.

---

## Citations (verified count: 24 named findings/models cited by author+year across Sections 1-3;
all drawn from established cognitive/affective neuroscience and psycholinguistics literature current
through the trained-knowledge cutoff; no live web/arxiv fetch was performed for this pass — flag for
a follow-up verification drill if exact citation years/venues need confirmation before being treated
as load-bearing in a design doc). Key names for follow-up verification: Barsalou (perceptual symbol
systems); Barrett (constructionist theory of emotion); Lambon Ralph, Patterson & Rogers (hub-and-
spoke ATL); Jefferies (controlled semantic cognition, IFG/pMTG); Rodd, Davis & Johnsrude (ambiguity
fMRI); Giora (graded salience hypothesis); Zwaan & Radvansky (event-indexing model); Baldassano et
al. (DMN narrative hierarchy); Kuperberg & Jaeger (predictive coding of language, N400); Saxe &
Kanwisher (TPJ mentalizing); Frith & Frith (mentalizing network review); Mar (narrative-ToM
meta-analysis); Sperber & Wilson (relevance theory, echoic-mention irony account); Botvinick et al.
(conflict monitoring, ACC); Cohen & Eichenbaum (relational memory, hippocampus); McClelland, O'Reilly
& Norman (complementary learning systems); Rangel, Camerer & Montague (value-based decision
framework); Craig (interoception); Critchley & Garfinkel (interoceptive predictive model); Rogers &
McClelland (semantic cognition connectionist model); Desimone & Duncan (biased competition); Badre &
Wagner (IFG selection); Cunningham & Brosch (amygdala salience account); Kintsch & van Dijk
(construction-integration model).

**Calibration note (mandatory per role contract)**: this document is a lit-scan/framework-synthesis
product. P estimates herein are deflated 0.15-0.25 from raw confidence per
[[feedback-lit-scan-calibration-penalty]]; the single explicit novel-synthesis claim (Section 6) is
capped at P=0.50 and reported at 0.45. Do not treat Section 1-3 mechanistic claims as substrate-
verified; they are literature-grounded hypotheses for the substrate build to test against, not
already-confirmed substrate behavior.
