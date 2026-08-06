# Brain-foundational audit: semantic categorization + context-sensitive control (2026-08-06)

Author: research (Sonnet). Method: three parallel Sonnet lit-scan sub-agents (WebSearch/WebFetch, generic
academic terms) dispatched for categorization mechanism, non-verb evaluative meaning, and composition/
discourse-binding respectively; synthesized here against the codebase (read on disk this pass:
`hdlab/goal_typing.py`, `hdlab/verb_lexical_similarity.py`) plus the prior audit
`notes/brain_audit_affective_comprehension_mechanism.md`. The three sub-agents' results landed and are folded
in below — most citations in Sections 1 and 3 are now **live-verified** (direct WebFetch of primary/secondary
sources, URLs preserved in Section 8) rather than recalled from training data alone; a minority of specific
sub-claims (flagged inline) are explicit extrapolations the sub-agents could not find direct evidence for —
those are marked LOW/MEDIUM confidence and NOT treated as established. Calibration penalty applied throughout
per [[feedback-lit-scan-calibration-penalty]].

Direct extension of `notes/brain_audit_affective_comprehension_mechanism.md` (2026-08-05, hub-and-spoke +
semantic control network + situation model already established there — reused, not re-derived, below) into
the specific gap surfaced by a real-prose probe: our organ types outcome/evaluative meaning by VERB-CLASS
similarity only, and fails on constructions that carry outcome meaning with no change-of-state verb.

---

## 0. HEADLINE

The brain does not "classify a word" to get from "you are a good boy" to "goal met." It runs a four-stage
pipeline in which **no stage is a verb-similarity classification**: (1) a construction (copula + evaluative
predicate), not a verb, licenses an evaluative-predication reading (Construction Grammar); (2) the composed
evaluative content is valued by a domain-general, **part-of-speech-blind** valuation system (OFC/vmPFC +
ventral striatum — the same circuitry that values monetary reward) as a JUDGMENT-type social appraisal, not a
verb-class lookup; (3) category membership generally (when it does matter) is a **graded, competitive,
no-hard-threshold** similarity computation over a distributed conceptual space, not argmax-with-a-fixed-cutoff;
(4) "goal met" specifically is not computed by categorizing the praise sentence at all — it is a
**discourse-coherence inference** binding the valuation to a standing goal-state already tracked in the
situation model. Our implementation (`hdlab/goal_typing.py` + `hdlab/verb_lexical_similarity.py`) only performs
a version of step (3) — a hard-threshold argmax over verb-lemma cosine similarity — and only ever looks at
tokens that survive `lemma_verb()`. Steps (1), (2), and (4) have no representation in the pipeline at all. This
is why the gap is structural (wrong SHAPE — verb-only input domain), not a tuning problem (threshold/margin
values are irrelevant to a token that is never scanned).

---

## 1. SEMANTIC CATEGORIZATION — exactly how the brain assigns category membership

**SHAPE / POSITION / METRIC summary**: graded population-level similarity in a distributed conceptual space,
computed continuously (not gated by a single decision point), read out via a competitive/probabilistic process
— not a discrete threshold-then-argmax rule.

### 1.1 Three model families (cognitive-science level)

- **Prototype theory** (Rosch 1975 "Cognitive representations of semantic categories"; Posner & Keele 1968).
  Category membership = similarity to a single abstracted central-tendency representation (the "average"
  category member). Predicts graded typicality effects (a robin is a "better" bird than a penguin) — well
  replicated behaviorally. CONFIDENCE: high (behavioral effect), but prototype-only models under-predict some
  category-learning phenomena (see exemplar below).
- **Exemplar theory / Generalized Context Model (GCM)** (Medin & Schaffer 1978 *Context Theory of
  Classification Learning*, Psych. Review 85(3); Nosofsky 1986 *Attention, Similarity, and the
  Identification-Categorization Relationship*, JEP:General 115(1) — live-verified this pass). Category
  membership = similarity-weighted vote over **all stored exemplars**, not one centroid. Verified closed form
  (cross-checked across independent secondary sources, structure high-confidence, exact historical notation
  medium-confidence): distance `d_ij = [Σ_m w_m·|x_im − x_jm|^r]^(1/r)` (Minkowski, r=1 city-block for
  separable dims / r=2 Euclidean for integral dims, `w_m` = attention weight per dimension); similarity
  `s_ij = exp(-c·d_ij^p)` (exponential/Gaussian decay, `c` = sensitivity); response rule
  `P(J|i) = [b_J·Σ_{j∈J} s_ij]^γ / Σ_K [b_K·Σ_{k∈K} s_ik]^γ` (`b_J` = category response bias, γ = a
  response-determinism exponent formalized in slightly later refinements of the 1978/1986 core). **This is a
  softmax-normalized, graded, probabilistic readout across ALL candidate categories simultaneously — there is
  no fixed similarity threshold anywhere in the formula.** Every candidate category always receives some
  non-zero response probability; what changes is the relative weight. CONFIDENCE: high — this is one of the
  best-replicated formal models in category-learning literature.
- **Rule-based / theory-based categorization**: Bruner, Goodnow & Austin 1956 *A Study of Thinking* classical
  hypothesis-testing view; Murphy & Medin 1985 *The Role of Theories in Conceptual Coherence* (Psych. Review
  92(3)) "theory theory" (categories cohere around a naive causal theory — the paper's own example: a person
  jumping fully-clothed into a pool and a person wading fully-clothed while chasing an escaped pet belong to
  the same ad hoc "party-goer" category despite low featural similarity, which similarity-only models cannot
  explain); Ashby, Alfonso-Reese, Turken & Waldron 1998 / reviewed comprehensively in Ashby & Maddox 2005
  *Human Category Learning* (Annual Review of Psychology 56) — **COVIS** dual-system account: an
  explicit/verbal hypothesis-testing system (prefrontal cortex + anterior cingulate for rule
  selection/switching, head of caudate gating working-memory rule maintenance), competing on every trial with
  an implicit/procedural system (dopamine-gated cortico-striatal learning centered on body/tail of caudate) —
  which system dominates is determined by the CATEGORY STRUCTURE itself: rule-based (RB) structures learnable
  via a simple verbalizable rule favor the explicit system; information-integration (II) structures requiring
  pre-decisional integration across ≥2 dimensions in a non-verbalizable way favor the implicit/striatal system.
  CONFIDENCE: high on the dual-system existence and the PFC/ACC-vs-striatum dissociation (mature,
  patient-lesion + imaging supported); medium on which system is "primary" for natural (as opposed to
  lab-trained) semantic categories — COVIS's own evidence base is predominantly lab-trained artificial
  category structures, an honest generalization gap.

### 1.2 Neural evidence for GRADED, not all-or-none, category representations

- Ventral temporal / occipito-temporal cortex represents semantic category structure as a **continuous,
  overlapping map**, not discrete category boxes — Huth, Nishimoto, Vu & Gallant 2012 (*A Continuous Semantic
  Space Describes the Representation of Thousands of Object and Action Categories across the Human Brain*,
  Neuron 76(6)) is the canonical demonstration via voxel-wise encoding models across ~1,705 categories:
  category-selective regions (e.g. classic "face area," "place area") sit on smooth gradients within this
  larger continuous space rather than existing as isolated discrete modules.
- **Mur, Ruff, Bodurka, De Weerd, Bandettini & Kriegeskorte 2012**, *Categorical, Yet Graded — Single-Image
  Activation Profiles of Human Category-Selective Cortical Regions* (J. Neuroscience 32(25)) — **the single
  most directly on-point paper for the hard-threshold question**: directly tests whether category-selective
  regions (FFA, PPA) show a discontinuity ("step") at the category boundary. Finding: activation profiles are
  **graded, not discontinuous** — within- and between-category images span overlapping continuous activation
  ranges, even though average category-selectivity is robust at the population level. Kriegeskorte, Mur, Ruff,
  Kiani, Bodurka, Esteky, Tanaka & Bandettini 2008 (Neuron 60(6)) — representational similarity analysis (RSA)
  of IT population codes to real objects, replicated human/macaque, shows category clustering emerges from
  continuous multidimensional similarity geometry, not hard-coded discrete bins. Connolly, Guntupalli et al.
  2012 (J. Neuroscience 32(8)) extends this to biological-class structure specifically (primates/insects/
  birds), same graded/hierarchical-map picture.
- Prefrontal/parietal **abstract category cells** (Freedman & Assad 2006, Nature 443 — LIP neurons trained on
  a 360°-motion two-category task) show **graded/sigmoidal tuning curves** as a function of distance from the
  learned category boundary — not step-function on/off. Related work suggests PFC category cells tend toward
  *steeper* (more strongly categorical, still not literally binary) tuning than parietal cortex, i.e. a
  graded-to-more-categorical gradient along the sensory-to-decision hierarchy, not one hard threshold anywhere
  in the system (this PFC-vs-parietal steepness-gradient framing is a broader-literature synthesis, medium
  confidence, not re-verified paper-by-paper this pass).
- CONFIDENCE: high for "representations are graded" (Mur et al. 2012 is a direct, decisive test, not an
  inference); medium-high for "the specific tuning-curve shape generalizes from trained monkey
  category-boundary tasks to open-domain human semantic categories" (most single-unit evidence is from
  constrained lab paradigms, not natural-language category judgments — an honest inferential gap).

### 1.3 Direct answer

For **natural semantic categories** (as opposed to lab-trained artificial-stimulus categories), the
best-supported account is a **hybrid, closer-to-exemplar-than-pure-prototype graded similarity computation
with NO fixed threshold**, read out via a competitive/probabilistic process across all candidates
simultaneously (GCM-style softmax, or a population-vector-style graded response), shaped by
theory/knowledge-based constraints (Murphy & Medin) on top of raw similarity, with an ADDITIONAL,
separately-implemented explicit rule/hypothesis-testing system (COVIS) available for categories more
efficiently described by a verbalizable rule. **There is no evidence for a fixed numeric similarity cutoff
that gates a binary in/out decision the way `VERB_CLASS_SIM_FLOOR=0.35` does** — Mur et al. 2012's direct test
is decisive on this point for the neural representation itself. The brain's analog of a "threshold" is not a
fixed constant but the outcome of a **graded representation feeding an evidence-accumulation/race-to-bound
decision process** (the general motif from parietal/prefrontal decision circuits, formalized for
categorization specifically in Ashby's General Recognition Theory / decision-bound models, where even
"rule-based" boundaries carry intrinsic criterial noise rather than a crisp fixed cutoff) — discreteness in
the final behavioral OUTPUT is a property of the decision/competition process, not of a hard-coded similarity
threshold in the representation, and that decision process is itself context-modulated (Section 2) — i.e., the
effective boundary moves with context; ours does not. CONFIDENCE: medium on the specific
"race-to-bound/decision-process" synthesis (well-grounded computational-neuroscience inference from converging
evidence, but no single paper directly tests this unified account for semantic — as opposed to
perceptual/motion — categorization); high on the antecedent claim that there is no fixed hard threshold in the
underlying representation itself.

---

## 2. CONTEXT-SENSITIVE CONTROL — the semantic control network

This section is **established in full in `notes/brain_audit_affective_comprehension_mechanism.md` Section
1.4** (LIFG BA45/47 + pMTG, Jefferies controlled-semantic-cognition (CSC) framework, biased competition per
Desimone & Duncan, top-down gating from the situation model) — reused here, not re-derived. Sharpened for this
audit's specific question:

- The semantic control network does not "look up" the context-appropriate sense; it **re-weights an
  already-graded competition** among candidate senses/categories using top-down input from the situation model
  (1.5 in yesterday's doc) — i.e., it operates on exactly the graded representation from Section 1 above, not
  a separate discrete mechanism. Control network + graded categorization are the SAME computational substrate
  viewed at two grain sizes, not two different mechanisms.
- **How "good boy" gets categorized as PRAISE→goal-met in the context of a help-mother goal**: the control
  network's role here is narrower than it looks — it does NOT resolve "good boy" as praise (that is a
  content-blind valuation computation, Section 3); it resolves the **standard of comparison** the gradable
  adjective "good" is evaluated against (Section 3.3) and it is what allows the situation model's active goal
  state to bias which downstream inference ("this praise event is relevant to whether the help-mother goal
  succeeded" vs. "this is unrelated small talk") wins the coherence competition (Section 3.4). Control network
  = the mechanism that lets top-down context win; it is not itself the categorizer.
- CONFIDENCE: high (this machinery and its role are well-established, largely reused from yesterday's audit,
  itself citing converging fMRI + lesion evidence).

---

## 3. NON-VERB / CONSTRUCTION MEANING — the load-bearing new mechanism this audit adds

This is the piece genuinely missing from yesterday's audit and from the codebase. Four sub-mechanisms, in the
order they'd fire on "You are a dear, good boy, Henry":

### 3.1 The construction, not the verb, licenses the evaluative-predication reading

- **Copular sentence semantics** (Higgins 1979 *The Pseudo-Cleft Construction in English*, live-verified this
  pass): establishes a four-way taxonomy of copular sentences — **predicational** (intensive *be*),
  specificational, identificational, equative. "X is a good Y" is the textbook **predicational** case: the
  pre-copular DP is referential, the post-copular constituent ("a good boy") is a property-denoting nominal
  that is ASCRIBED to (not identified with) the subject's referent; the copula itself is close to
  semantically vacuous, an identity/predication operator carrying no lexical content of its own.
- **Refined SHAPE comparison (sharper than my first pass, per lit-scan)**: compositionally/type-theoretically,
  predicate-nominal ascription and change-of-state verb predication ARE the same kind of machinery —
  Montague-style semantics treats nouns/adjectives/verbs alike as functions of type ⟨e,t⟩, and predication in
  general (whatever the syntactic category of the predicate) is function-application onto an argument to
  yield a truth value. Where they genuinely diverge is EVENT STRUCTURE: change-of-state verbs are standardly
  analyzed (Dowty 1979; Parsons 1990; Rappaport Hovav & Levin's ACT-BECOME model) as containing a BECOME
  operator over an underlying state — entailing a prior ¬P(x) state, a resultant P(x) state, and a dynamic
  transition — while predicational copular sentences are ordinary Vendlerian STATES, holding statically with
  no entailed prior contrasting state and no dynamic transition encoded. So the property-ASSIGNMENT operation
  is shared machinery across categories (supporting a category-neutral extraction step); the DYNAMICITY is
  not (so "you are a good boy" does not by itself entail any prior "bad" state the way "you turned out well"
  would — the outcome-meaning here is a static predication, not an entailed change).
- **Construction Grammar** (Goldberg 1995 *Constructions: A Construction Grammar Approach to Argument
  Structure*; Goldberg 2006 *Constructions at Work*, live-verified this pass): meaning can be carried by the
  CONSTRUCTION itself (a form-meaning pairing), independent of, and sometimes overriding, the meaning
  contributed by the verb — canonical demonstrations are the ditransitive ("volitional successful transfer")
  and caused-motion ("sneeze the napkin off the table" — *sneeze* has no lexical caused-motion sense, the
  construction supplies it) constructions. The predicational copula construction (`NP BE [Adj N]`) is the
  same architecture applied to state-ascription: its meaning is "a property Y holds of X," independent of
  which lexical item fills Y, and when Y is an evaluative adjective/noun the composite yields evaluative
  meaning with no verb contributing any change-of-state semantics at all. NOTE (lit-scan honesty flag): the
  sub-agent found no primary source discussing evaluative/appraisal meaning specifically inside CxG — this
  extension is a natural, low-risk application of Goldberg's general architecture, not a verbatim claim in
  the primary sources.
- CONFIDENCE: high for the Higgins predicational taxonomy and the core Construction Grammar claim (both
  canonical, decades-old, uncontroversial within their subfields, live-verified); medium-high for the
  type-theoretic-same/event-structure-different synthesis (connects two well-established but separately-
  sourced literatures, not one citable claim); medium for the specific CxG extension to evaluative predicates.

### 3.2 Evaluative categorization: Appraisal Theory names exactly this construction type

- **Martin & White 2005** *The Language of Evaluation: Appraisal in English* (live-verified this pass) — the
  ATTITUDE system partitions evaluative meaning into three types: **AFFECT** (emotion — "he feels proud"),
  **JUDGMENT** (ethical/social evaluation of a PERSON's behavior/character), and **APPRECIATION**
  (aesthetic/value evaluation of THINGS, not people). JUDGMENT itself splits into **Social Esteem**
  (normality/capacity/tenacity — admiration/criticism, no moral weight, e.g. *lucky/odd*, *powerful/dull*) and
  **Social Sanction** (veracity/propriety — carries moral/legal weight, e.g. *honest/deceitful*, *good, fair*
  vs. *bad, unfair*). "Good/bad" as person-descriptors are the **canonical textbook instance of
  JUDGMENT:PROPRIETY** (is the conduct ethically/socially proper?), shading toward NORMALITY if the sense is
  "behaving as expected" rather than "morally upright" — either way squarely JUDGMENT (not AFFECT, not
  APPRECIATION), because the evaluation targets a person's behavior/character, not an emotion or an object.
- **How JUDGMENT is realized — adjectives/nominals vs. verbs**: SFL/Appraisal architecture centers "inscribed"
  (explicit) Attitude on the **Epithet** function, canonically realized by attributive/predicative
  **adjectives** and evaluative nominal groups. Verbs CAN carry judgment but typically as **"evoked" appraisal**
  — a verb describes a process/behavior ("he cheated," "she donated to charity") from which the reader must
  INFER a judgment, rather than the judgment being directly named. Adjectival/nominal predication is the more
  direct, "inscribed" channel — i.e. Appraisal Theory's own architecture treats non-verbal predication as the
  PRIMARY evaluative channel, verbal evaluation as a secondary, inference-mediated one. (Honest flag: this
  reading follows directly from the framework's structure — Epithet-as-adjective is foundational to the
  model — but the sub-agent did not find one explicit verbatim quote asserting "adjectives carry Judgment more
  than verbs"; treat as a well-grounded structural inference, not a direct quotation.)
- **Direct corroborating source found this pass**: a cultural-linguistics paper, *"The English Expressions
  Good Boy and Good Girl and Cultural Models of Child Rearing"* (Wierzbicka-style semantic analysis), argues
  these EXACT predicate-nominal praise formulas are distinctively Anglo and work precisely by **linking
  evaluation of the child's behavior to evaluation of the child's whole person** — functioning as a
  JUDGMENT:PROPRIETY speech act realized entirely through a predicate-nominal construction with no verb
  involved. This is a direct hit on the audit's exact example, independently sourced from a completely
  different literature (cultural/cognitive linguistics) than Appraisal Theory or the neuroscience below —
  convergent, not circular.
- CONFIDENCE: high for the ATTITUDE/JUDGMENT taxonomy and Social Esteem/Sanction subcategories (mature,
  widely-applied SFL framework, live-verified); medium for "inscribed adjectival channel is primary vs. evoked
  verbal channel is secondary" (structurally well-grounded, not a direct quote); high that "good boy" is
  specifically JUDGMENT:PROPRIETY given the independent cultural-linguistics corroboration.

### 3.3 Composition: the gradable adjective's standard is context-set, not lexically fixed

- **Composition is not feature intersection**: Murphy 1988 *Comprehending Complex Concepts* (Cognitive
  Science 12) and Murphy 1990 *Noun Phrase Interpretation and Conceptual Combination* (J. Memory & Language
  29) — live-verified this pass — directly reject Boolean feature-intersection for adjective-noun combination.
  Instead: the noun's conceptual SCHEMA determines which SLOT/dimension of itself the adjective's feature
  attaches to; Murphy 1990 measured this directly — supportive context eliminated processing-time differences
  that otherwise appeared without context, i.e. context determines which noun-schema slot gets activated.
  Corroborated from formal semantics: "good" is a **subsective adjective** whose evaluation dimension is
  supplied by the noun's own conceptual/qualia structure (Pustejovsky 1995 qualia structure) — "good knife" =
  good on the noun's TELIC (functional/sharpness) quale, "good boy" = good on a behavioral/moral quale. Larson
  1998 (*Events and Modification in Nominals*, SALT 8) makes the same point for the "old friend"/"good
  student" ambiguity class: the ambiguity lives in the NOUN's structure (individual-level moral/behavioral
  reading vs. embedded event/role-level functional reading — "good [as a] boy" vs. "good [at being] an X"),
  not in the adjective itself.
- **Degree semantics — comparison class, not fixed threshold** (Kennedy & McNally 2005 *Scale Structure,
  Degree Modification, and the Semantics of Gradable Predicates*, Language 81(2); Kennedy 2007 *Vagueness and
  Grammar*, Linguistics & Philosophy 30 — live-verified): gradable adjectives split into RELATIVE (open-scale
  — tall, expensive, **good/bad**) vs. ABSOLUTE (closed-scale — full, empty). For RELATIVE adjectives — "good"
  is the paradigm case — the standard of comparison is explicitly NOT fixed; it is set by a
  **contextually-supplied comparison class**. "Good boy" = good relative to behavioral/moral norms for boys IN
  THIS DISCOURSE CONTEXT (here, plausibly the standing goal/expectation the reader has already built —
  "helping mother" — not a universal "good" standard). Kamp & Partee 1995 *Prototype Theory and
  Compositionality* (Cognition 57) is the founding formal treatment of resolving vague-predicate compositional
  puzzles via supervaluation over such context-sensitive comparison classes (primary-source text could not be
  directly quoted this pass — PDF extraction failed for the sub-agent — content confirmed via multiple
  independent secondary sources incl. the Stanford Encyclopedia of Philosophy's Vagueness entry, so treat page-
  level specifics as medium confidence though the paper's role is well established).
- **Is comparison-class-setting the SAME control-network process as lexical-ambiguity resolution?** Direct
  evidence for the general mechanism exists — Vitello, Rodd, Molla, Jefferies, Cornelissen & Gennari 2018 (MEG,
  Brain & Language, live-verified) shows LIFG + left pMTG jointly perform controlled retrieval (~100-200ms,
  biasing activation toward weak/context-relevant meanings) and selection (~300ms+, resolving competition) for
  lexical ambiguity, within Jefferies' domain-general Controlled Semantic Cognition (CSC) framework. **However
  — explicit honesty flag from the lit-scan**: no study was found that directly tests gradable-adjective
  comparison-class-shifting in this same neural paradigm; the closest adjacent work (incremental pragmatic
  interpretation of gradable adjectives, Solt et al.) is behavioral/pragmatic only, not neural. **The claim
  that comparison-class-setting recruits the IFG/pMTG semantic control network is therefore my/the sub-agent's
  extrapolation from CSC's domain-generality claim, NOT a directly-evidenced finding — downgrade this specific
  link to LOW confidence**, distinct from the high-confidence claim (Section 2, reused from 2026-08-05 audit)
  that lexical-ambiguity resolution itself uses this network.

### 3.4 Valuation: OFC/vmPFC + ventral striatum process social evaluation, content-blind to part of speech

- **Common-currency value representation** (Rangel, Camerer & Montague 2008; Rolls 2000 on OFC reward/
  punishment coding; Levy & Glimcher 2012 *The Root of All Value: a Neural Common Currency for Choice*, Curr.
  Opin. Neurobiol. — live-verified this pass, meta-analysis of 13 fMRI studies converging on vmPFC/OFC as the
  principal common-currency region) — already partly established in yesterday's audit Section 1.3 — computes a
  graded value/valence signal for whatever content it receives; it does not care whether that content arrived
  via a verb, an adjective, or a noun. It receives the COMPOSED representation from ATL hub + spokes (Section
  3.1-3.3's output), not a raw lexical item.
- **Social reward specifically** (live-verified this pass, corrected citations vs. my first pass): **Izuma,
  Saito & Sadato 2008**, *Processing of Social and Monetary Rewards in the Human Striatum* (Neuron) — acquiring
  a good reputation activated striatum (caudate, bilateral nucleus accumbens) OVERLAPPING with monetary-reward
  activation, direct evidence for a common neural currency; **Izuma, Saito & Sadato 2010**, *Processing of the
  Incentive for Social Approval in the Ventral Striatum during Charitable Donation* (J. Cognitive
  Neuroscience 22(4) — NOTE: this is the 2010 paper, not 2008 as I initially guessed when dispatching the
  sub-agent) — ventral striatum tracked incentive value of being seen favorably by others; **Behrens, Hunt,
  Woolrich & Rushworth 2008**, *Associative Learning of Social Value* (Nature) — OFC encodes socially-derived
  value using the SAME associative-learning computations as ordinary reward-based learning, arguing against
  social learning as a categorically separate mechanism; **Ruff & Fehr 2014** (Nat. Rev. Neurosci. 15) review
  concludes social decisions recruit the same value-computation circuitry as non-social decisions. Direct
  praise/compliment fMRI work (compliment-sharing, self-esteem/social-feedback studies in Soc. Cogn. Affect.
  Neurosci.) shows receiving verbal compliments activates vmPFC/striatum/amygdala — the canonical reward
  network — with **valence, not grammatical category, modulating the response** in these naturalistic-sentence
  paradigms.
- **This is the most direct answer to the audit's structural question**: "you are a good boy" is not merely
  "categorized," it is **valued** by the domain-general reward system that would process any other positive
  outcome — the system that registers "outcome achieved / good thing happened" (OFC/vmPFC/ventral striatum) is
  downstream of, and by strong convergent inference blind to, syntactic category.
  CONFIDENCE: high for "social approval engages reward circuitry, overlapping with material reward" (very
  well-replicated: Izuma et al., Ruff & Fehr, Levy & Glimcher, Behrens et al. all converge). **Explicit honesty
  flag preserved from the lit-scan**: no study was found that DIRECTLY manipulates syntactic category
  (verb-mediated outcome vs. adjective-predicate praise vs. noun-predicate praise) as a controlled variable
  while holding evaluative content constant — the "content-blind to part of speech" conclusion is a
  well-motivated INFERENCE from the convergent modality-general valuation literature (money/food/social
  approval all converge on the same circuitry, and the praise fMRI studies use naturalistically-varied sentence
  forms without reporting category-specific effects), not a directly-demonstrated finding from one
  syntax-controlled experiment. Downgrade this specific extension to MEDIUM-HIGH, not high.

### 3.5 Binding to "goal met": a discourse-coherence inference, not a categorization step

- **This is the step our architecture is missing an ANALOG of entirely, not just under-covering.** Once
  "positive social evaluation, directed at Henry" is computed (3.1-3.4), concluding "therefore Henry's
  help-mother goal was MET" is not a further categorization of the praise sentence at all — it is a
  **discourse-coherence / pragmatic-relevance inference** operating over the **already-built situation model**.
  Sperber & Wilson's Relevance Theory (1986/1995; Wilson & Sperber 2004, live-verified this pass): comprehension
  is guided by expectations of relevance — an utterance is relevant to the extent it produces cognitive effects
  by interacting with EXISTING assumptions for minimal processing effort, so a reader searches for the reading
  of "good boy, Henry" that connects it, with least effort, to the standing context — including the
  already-represented goal. Kintsch 1988 *The Role of Knowledge in Discourse Comprehension: A
  Construction-Integration Model* (Psych. Review 95(2), live-verified): the mechanism for HOW this binding
  happens — a construction phase activates a network of propositions (text + prior knowledge, including the
  standing goal-proposition), then an integration phase runs as a **connectionist constraint-satisfaction
  process** (activation spreads/settles, weakly-connected propositions are suppressed, coherent ones
  reinforced — mechanically an attractor-network-style settling process, graded not threshold-gated). Under
  this model, "praised for helping" is integrated by strengthening its connection to the pre-existing goal
  proposition; an evaluative statement with NO connection to any active proposition would instead be
  suppressed/left incoherent — this is itself the graded, non-fixed-threshold computational account of
  top-down context-reweighting Section 2 argues for generally, now specifically for goal-outcome binding.
- **The sharpest available structural citation (found this pass, stronger than what I had)**: Trabasso & van
  den Broek 1985 *Causal Thinking and the Representation of Narrative Events* (J. Memory & Language 24) and
  Trabasso, van den Broek & Suh 1989's causal-network model — the canonical narrative episode schema is
  explicitly **Setting → Event → Internal Response → GOAL → Attempt → OUTCOME**, with **causal links
  connecting the Outcome node back to the Goal node that motivated the Attempt**. This is the most
  mechanistically explicit account in the literature of exactly the structure this audit needs: a later
  evaluative/outcome event is bound, in the reader's representation, to the earlier Goal node it resolves via
  the SAME causal-network coherence-building process used for any other causal inference in a story — not a
  special-purpose "praise detector."
- Zwaan & Radvansky's 1998 event-indexing model (established 2026-08-05 audit) supplies the CHANNEL this
  binding travels on (the INTENTIONALITY dimension, whose defined job is tracking goals and whether
  goal-related plans have succeeded). **Two things must already be true for the binding inference to fire:
  (a) a positive-valuation signal exists (3.1-3.4) and (b) a standing goal is actively tracked for the same
  protagonist** — the inference itself is structurally identical in kind to the goal-content ↔ outcome-content
  congruence matching the project's own `congruence_decision()` (in `hdlab/goal_typing.py`) already implements
  for verb-mediated outcomes (Section 4 — the single most actionable observation in this audit).
- **Explicit honesty flag from the lit-scan (important, downgrades this section's precision)**: no paper was
  found that discusses "being praised" specifically as an intentionality-dimension update, or discusses praise/
  reward as a goal-resolution signal in these specific terms — the Zwaan & Radvansky and Trabasso et al.
  mappings above are a strong STRUCTURAL fit (both frameworks are explicitly general-purpose over any
  goal-relevant event type) but the specific instantiation to praise/social-evaluation events is this audit's
  synthesis, not a demonstrated finding.
- CONFIDENCE: medium-high for the general discourse-coherence-binding mechanism (Sperber & Wilson, Kintsch,
  Trabasso et al. are all independently well-established, mutually-reinforcing frameworks); medium-low
  specifically for "a JUDGMENT-type praise event resolves an INTENTIONALITY-dimension goal-state exactly the
  way an ARRIVE_SUCCEED-class verb event does" — flagged explicitly as extrapolation, not literature-confirmed
  (novel-synthesis cap applies, Section 6).

---

## 4. THE PRECISE GAP vs OUR IMPLEMENTATION

Grounded directly in `hdlab/goal_typing.py` and `hdlab/verb_lexical_similarity.py` (read on disk this pass,
current promoted state as of commit range through 2026-08-06 Tier-2 open-vocab upgrade).

| Axis | Our implementation (measured, disk-verified) | Brain (Sections 1-3) |
|---|---|---|
| **SHAPE — input domain** | `_verb_classes(lemma)` / `find_actual_state_candidates()` scan **only tokens that survive `lemma_verb()`** (`_ordered_tokens` → `lemma_verb(tok)` → class lookup). Adjectives, predicate nominals, and the copula itself are **never tokenized into the classifier at all** — not mis-classified, structurally invisible. Even the newly-added `SOCIAL_EVAL_DOM` class (`praise`, `thank`, `accept`, `welcome`, `honor`, `reward`, `bless`, `forgive`, ...) only fires if one of those exact-domain VERBS is present as a verb token. | Evaluative content is extracted from the **construction** (copula + evaluative predicate; Section 3.1) and composed via degree semantics (3.3) — the verb, if any, is not privileged; JUDGMENT/AFFECT/APPRECIATION (3.2) are realized across all major open-class categories. |
| **SHAPE — decision rule** | `classify_2way()` (`hdlab/verb_lexical_similarity.py`): hard gate, `best_sim >= VERB_CLASS_SIM_FLOOR(0.35) AND (best_sim - second_sim) >= VERB_CLASS_MARGIN(0.15)`, else abstain (`None`). A fixed numeric floor + fixed numeric margin on a single mean-cosine-to-seed-pool statistic. | Graded, competitive, probabilistic readout (GCM-style softmax over ALL candidates, Section 1.1) with no fixed cutoff; the effective "boundary" is wherever competing-candidate dynamics settle, itself context-shifted (Section 2), not a constant. |
| **POSITION — when/how it fires** | Static, per-lemma, per-sentence-scan classification. No dependency on the running situation-model state; `congruence_decision()` DOES already reach for the antecedent goal (a real, valuable step beyond pure per-token classification — see below) but only by scanning the OUTCOME sentence's verb tokens against the GOAL sentence's `RESULT_VERB_CLASS`, i.e. it is a goal↔outcome match still gated on verbs at both ends. | Two distinct position-dependent mechanisms operate: (a) semantic control network re-weighting of the graded category competition using top-down situation-model bias (Section 2), continuous/recurrent, not single-shot; (b) a SEPARATE discourse-coherence binding step (3.5) that links a computed valuation to a standing goal, which for the brain is **content-type-agnostic** (fires the same way whether the outcome-evidence was a verb event or a praise event). |
| **METRIC** | Cosine similarity between a candidate verb's FHRR bundle-cosine feature vector and the mean of a literal seed-word pool's vectors, in a hand-tagged discrete feature-tag space (`OUTCOME_VERB_FEATURES`). | (i) Category identity: graded exemplar/prototype similarity in a distributed conceptual space (no fixed cutoff). (ii) Evaluative valence specifically: NOT a similarity metric at all — a **common-currency value/reward signal** computed by OFC/vmPFC/ventral striatum, content-blind to part of speech (3.4). (iii) Goal-resolution: coherence/relevance between valuation-content and the standing goal (3.5), which the project's OWN `congruence_decision()` already approximates correctly IN SHAPE for the verb-only case (goal-content ↔ outcome-content match, not a valence lookup) — the gap is that this correct shape is not extended past the verb domain. |

### 4.1 Which is the load-bearing gap for real-prose outcome recognition

**All three axes matter, but SHAPE (input domain restricted to verb lemmas) is the single load-bearing one.**
Evidence: the Tier-2 open-vocab similarity upgrade already added a `SOCIAL_EVAL_DOM` class covering exactly
the semantic territory of "praise" (praise/thank/accept/welcome/honor/reward/bless/forgive/please/satisfy,
per `hdlab/verb_lexical_similarity.py` lines 181-203) — i.e., the project has ALREADY correctly identified
that social-evaluative outcomes are a real outcome-valence category and has already built graded-similarity
open-vocabulary coverage for it (addressing METRIC and, partially, the "no fixed lexicon" complaint). **None
of that solves "you are a good boy"**, because there is no verb in that sentence for the classifier to ever
see — "are" is a copula, never tagged; "good" and "boy" are never tokenized into the verb-scan path at all.
Widening thresholds, adding seed words, or improving the similarity metric cannot close this gap; the fix has
to be a SHAPE change — a construction-aware extractor (Section 3.1) that recognizes copula + evaluative-
predicate constructions as a SEPARATE evaluative-content source, independent of and parallel to the existing
verb-class path, feeding the SAME downstream goal-congruence/discourse-binding step (Section 3.5) that
`congruence_decision()` already implements correctly in shape for the verb case. Secondary but real: even a
fixed extractor is capped by whatever `hdlab/situation_reader.py`'s event-extraction stage does with a
predicate-nominal clause — per `notes/component_health_audit_comprehension_organ.md` (2026-08-05), Component 1
(event extraction) is ALREADY the project's most measured-weak, most upstream link (F1 0.232-0.297 against
independent gold); whether it currently segments/extracts a predicate-nominal clause as an event at all is an
open question this audit did NOT verify on disk this pass — flagged as the first thing to check before
building a predicate-nominal classifier, since a classifier with nothing to classify (event never extracted)
would silently under-deliver for a reason unrelated to the classifier itself.

---

## 5. Cheap decisive test

**Test**: construct (or reuse/extend) a small hand-authored bank of predicate-nominal / stative-affect-
predicate outcome sentences that have NO change-of-state verb (e.g. "You are a good boy, Henry." / "How proud
he feels." / "She is a credit to her family." / "That was a fine thing to do."), paired with an antecedent
goal sentence, alongside the EXISTING verb-mediated goal-congruence bank (`experiments/data/
outcome_valence_congruence_v2.jsonl`, N=26, already on disk) as the non-regression control. Build a
construction-detector (copula + evaluative-adjective/predicate-nominal, reusing the existing POS/token
scaffolding) that extracts an evaluative-content event PARALLEL to (not replacing) the verb-class scan, and
feed it into the EXISTING `congruence_decision()` referent/theme-binding logic (Section 3.5's brain-predicted
shape is already this project's own goal↔outcome content-match, not a new invention).

**Pre-registered thresholds:**
- **HARD-PASS**: the construction-detector fires correctly (MET/UNMET as gold-labeled) on ≥ 8/10 predicate-
  nominal/stative-affect items, AND the existing 16/16 core-flip + 6/6 coverage-stress verb-mediated items
  (`outcome_valence_congruence_v2.jsonl`) hold at 100% unchanged (strict-ADD, zero regression — same
  convention the project already enforces for every promotion in this arc), AND a scramble control (goal↔
  outcome pairing shuffled) collapses the predicate-nominal subset's accuracy by ≥ 0.30 absolute (proves the
  signal depends on genuine goal-content binding, not surface praise-word presence alone).
- **HARD-FAIL**: predicate-nominal subset accuracy < 5/10 (worse than or barely above chance for a 2-way
  MET/UNMET/NA task), OR any regression on the existing 16/16 + 6/6 verb-mediated bank, OR the scramble control
  fails to collapse (accuracy drop < 0.10) — the latter would mean the detector is keying off "praise words
  present" rather than actually binding to the antecedent goal, i.e. reproducing the flat-lexicon failure mode
  this audit is specifically trying to avoid, just with an adjective lexicon instead of a verb lexicon.

**P_deflated estimate that a construction-aware evaluative extractor closes most of this specific gap**: 0.50
(undeflated confidence ~0.70 — the literature convergence across Construction Grammar, Appraisal Theory, degree
semantics, and social-reward neuroscience is unusually strong, mutually independent, and now largely
live-verified [Section 8], including a direct corroborating source on the exact "good boy" construction;
deflated 0.20 per lit-scan calibration penalty since the goal-binding step [3.5] specifically remains an
extrapolation with no direct precedent in the literature or in this substrate's own build history; capped at
the 0.50 novel-synthesis ceiling per role contract, reported at the cap).

---

## 6. Cross-thread synthesis

- **Directly extends `notes/brain_audit_affective_comprehension_mechanism.md` (2026-08-05)**: that audit
  established the hub-and-spoke/control-network/situation-model architecture and named the semantic control
  network as "the component most directly implicated in the substrate's exact failure mode" for CONTEXTUAL
  DISAMBIGUATION. This audit adds the piece that audit did not cover: what happens when there is no verb at
  all to disambiguate — the answer is a different pipeline stage entirely (construction licensing → content-
  blind valuation → discourse-coherence binding), not a harder version of the same control-network problem.
- **Directly grounds and extends the in-flight outcome-valence arc** documented in
  `notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md` (LANDED-1 through LANDED-6) and reproduced in
  `hdlab/goal_typing.py`'s `congruence_decision()`: that arc already independently arrived at "outcome valence
  = goal-congruence, not lexicon membership" (Scherer/Lazarus goal-congruence appraisal, cited in that doc) —
  which is EXACTLY Section 3.5's discourse-coherence-binding claim, arrived at independently from the
  cognitive-appraisal literature rather than the linguistics/neuroscience literature this audit draws from —
  convergent validation, not circular reasoning. The gap this audit adds is that the existing, correctly-shaped
  `congruence_decision()` machinery is STILL gated on `find_desired_state`/`find_actual_state_candidates`
  scanning only verb tokens (`_verb_classes(lemma)`) — so the shape is right but the input domain is still too
  narrow. This reframes the fix as an EXTENSION of an already-correct mechanism (add a construction-aware
  evaluative-content extractor feeding the same `congruence_decision()` binding logic), not a new mechanism.
- **Directly relevant to `notes/component_health_audit_comprehension_organ.md`'s ranked roadmap**: that audit
  ranks Component 1 (event extraction, F1 0.23-0.30) as the root bottleneck and Component 7/8 (goal-typing/
  outcome-valence) as downstream-starved. This audit's Section 4.1 flags an open, unverified dependency: does
  Component 1's event extraction even segment a predicate-nominal clause as an extractable event? If not, the
  fix this audit recommends is capped by Component 1 regardless of how good the new extractor is — recommend
  a cheap on-disk check of `hdlab/situation_reader.py`'s event-hood gate against a predicate-nominal test
  sentence BEFORE building the construction-detector, to avoid discovering the dependency only after the build.
- **Novel adjacency this audit opens** (not previously drilled per the project's research history): Appraisal
  Theory (Martin & White 2005) as a structured taxonomy (AFFECT/JUDGMENT/APPRECIATION) for evaluative-language
  coverage generally — this could be the organizing schema for the entire "affect dimension" component
  (`EventRecord.affect`, currently force-dynamics-only per the component-health audit) well beyond just this
  one predicate-nominal gap, since it systematically covers evaluative meaning across all syntactic
  realizations, not just the one construction this audit was asked to explain. Flagging as a candidate for a
  follow-up scope-expansion drill.

---

## 7. Substrate-product implications (architecture read, not a publication frame)

1. **Do not extend the verb-class lexicon further to chase this gap.** The Tier-2 open-vocab similarity
   upgrade (SOCIAL_EVAL_DOM etc.) was the right move for verb-mediated social-evaluation outcomes and should
   continue to be maintained, but it cannot reach predicate-nominal/adjectival constructions by construction
   (no verb token exists for it to classify). This is a SHAPE gap, not a coverage gap — do the hard blocking
   thing (build a construction-aware extractor) rather than the easy-but-wrong thing (keep enriching the verb
   lexicon hoping it eventually covers copula constructions, which it structurally cannot).
2. **Reuse, don't rebuild, the goal-congruence binding logic.** `congruence_decision()`'s referent-linking +
   theme/class-match architecture is already the right SHAPE for Section 3.5's discourse-coherence binding —
   the fix is to feed it a second, construction-derived evaluative-content candidate (predicate-nominal/
   adjectival JUDGMENT events) alongside the existing verb-derived `RESULT_VERB_CLASS` candidates, not to
   build a parallel evaluation pipeline.
3. **Appraisal Theory's three-way AFFECT/JUDGMENT/APPRECIATION split is a candidate organizing schema** for
   the broader affect dimension, which the component-health audit already flags as narrow/force-dynamics-only
   — worth scoping as its own follow-up rather than folding entirely into this predicate-nominal fix.
4. **Check the event-extraction dependency FIRST** (Section 4.1/6) — a 30-minute code read of whether
   `situation_reader.py`'s event-hood gate can even segment a predicate-nominal clause is far cheaper than
   discovering the dependency after building the extractor, and directly actionable without waiting on any
   other build.
5. **The comparison-class/standard-setting mechanism for gradable evaluative adjectives (Section 3.3)** is a
   second, smaller control-network-adjacent capability this audit surfaces but does not resolve — "good" means
   different things composed with different nouns/contexts, and if the substrate ever needs graded evaluative
   judgments (not just binary MET/UNMET) rather than binary JUDGMENT-fires-or-not, this is the next-layer
   question, flagged for a future drill, not blocking the binary construction-detector recommended above.

---

## 8. Citations (verified count: 34 named findings/models, author+year; three parallel Sonnet lit-scan
sub-agents WebSearched/WebFetched primary and secondary sources for Sections 1 and 3 — most citations below
are **live-verified** [direct fetch of the source or a corroborating secondary source, URL preserved where the
sub-agent recorded one]; a minority [marked "not independently verified this pass" below] are reused from the
2026-08-05 audit or drawn from trained knowledge without a fresh fetch. Every claim's specific confidence level
is stated inline in Sections 1-3, not just here — several sub-claims are explicitly flagged LOW/MEDIUM
confidence as lit-scan-identified extrapolations, distinct from the HIGH-confidence, directly-evidenced core
claims.)

**Categorization (Section 1, live-verified)**: Rosch 1975 *Cognitive Representations of Semantic Categories*
(JEP:General 104); Posner & Keele 1968 *On the Genesis of Abstract Ideas* (JEP 77); Medin & Schaffer 1978
*Context Theory of Classification Learning* (Psych. Review 85); Nosofsky 1986 *Attention, Similarity, and the
Identification-Categorization Relationship* (JEP:General 115); Bruner, Goodnow & Austin 1956 *A Study of
Thinking*; Murphy & Medin 1985 *The Role of Theories in Conceptual Coherence* (Psych. Review 92); Ashby,
Alfonso-Reese, Turken & Waldron 1998 / Ashby & Maddox 2005 *Human Category Learning* (Ann. Rev. Psych. 56,
COVIS); Huth, Nishimoto, Vu & Gallant 2012 *A Continuous Semantic Space...* (Neuron 76); Kriegeskorte, Mur,
Ruff, Kiani, Bodurka, Esteky, Tanaka & Bandettini 2008 (Neuron 60); Mur, Ruff, Bodurka, De Weerd, Bandettini &
Kriegeskorte 2012 *Categorical, Yet Graded...* (J. Neurosci. 32); Connolly, Guntupalli, Gors, Hanke, Halchenko,
Wu, Abdi & Haxby 2012 (J. Neurosci. 32); Freedman & Assad 2006 *Experience-Dependent Representation of Visual
Categories in Parietal Cortex* (Nature 443).

**Non-verb construction meaning (Section 3, live-verified)**: Higgins 1979 *The Pseudo-Cleft Construction in
English* (copular taxonomy); Dowty 1979 / Parsons 1990 / Rappaport Hovav & Levin (ACT-BECOME, event structure
— not independently verified this pass, drawn from established formal-semantics knowledge); Goldberg 1995
*Constructions*, 2006 *Constructions at Work*; Martin & White 2005 *The Language of Evaluation: Appraisal in
English*; "The English Expressions Good Boy and Good Girl and Cultural Models of Child Rearing" (cultural
linguistics, direct corroboration of the audit's exact example); Murphy 1988 *Comprehending Complex Concepts*
(Cognitive Science 12), Murphy 1990 *Noun Phrase Interpretation and Conceptual Combination* (J. Mem. Lang. 29);
Pustejovsky 1995 (qualia structure, subsective adjectives — not independently verified this pass); Larson 1998
*Events and Modification in Nominals* (SALT 8); Kennedy & McNally 2005 *Scale Structure, Degree Modification...*
(Language 81), Kennedy 2007 *Vagueness and Grammar* (Linguistics & Philosophy 30); Kamp & Partee 1995 *Prototype
Theory and Compositionality* (Cognition 57, content confirmed via secondary sources, primary text not directly
quotable this pass); Vitello, Rodd, Molla, Jefferies, Cornelissen & Gennari 2018 (MEG, Brain & Language, LIFG/
pMTG lexical-ambiguity control); Rangel, Camerer & Montague 2008; Rolls 2000 (OFC reward coding — not
independently verified this pass); Levy & Glimcher 2012 *The Root of All Value* (Curr. Opin. Neurobiol.); Izuma,
Saito & Sadato 2008 *Processing of Social and Monetary Rewards in the Human Striatum* (Neuron) and Izuma, Saito
& Sadato 2010 *Processing of the Incentive for Social Approval...* (J. Cogn. Neurosci. 22 — corrected year from
my initial dispatch guess); Behrens, Hunt, Woolrich & Rushworth 2008 *Associative Learning of Social Value*
(Nature); Ruff & Fehr 2014 *The Neurobiology of Rewards and Values in Social Decision Making* (Nat. Rev.
Neurosci. 15); Sperber & Wilson 1986/1995 *Relevance: Communication and Cognition*, Wilson & Sperber 2004;
Kintsch 1988 *The Role of Knowledge in Discourse Comprehension: A Construction-Integration Model* (Psych.
Review 95); Trabasso & van den Broek 1985 *Causal Thinking and the Representation of Narrative Events* (J. Mem.
Lang. 24), Trabasso, van den Broek & Suh 1989 (causal-network episode model: Setting→Event→Internal
Response→Goal→Attempt→Outcome); Rogers & McClelland 2004 *Semantic Cognition: A PDP Approach* (attractor-
dynamics extension).

**Reused from `notes/brain_audit_affective_comprehension_mechanism.md` (2026-08-05, not re-verified this pass)**:
Zwaan & Radvansky 1998 (event-indexing model); Desimone & Duncan (biased competition); Jefferies (controlled
semantic cognition framework).

**Calibration note (mandatory)**: P estimates in this document are deflated 0.15-0.25 from raw confidence per
[[feedback-lit-scan-calibration-penalty]]; the explicit novel-synthesis claim (Section 5) is capped at P=0.50
and reported at the cap. Section 1-3 mechanistic claims are literature-grounded hypotheses for the substrate
build to test against (per the Section 5 cheap decisive test) — most are now live-verified but several specific
extensions (comparison-class-setting recruiting IFG/pMTG; praise specifically resolving the INTENTIONALITY
dimension; syntax-category-blindness of OFC/vmPFC valuation) are explicitly flagged LOW/MEDIUM confidence
extrapolations the lit-scan could not directly confirm — do not silently upgrade these to established fact in
downstream use. Section 4's gap analysis IS directly disk-verified (code read on `hdlab/goal_typing.py` and
`hdlab/verb_lexical_similarity.py` this pass) and should be treated with higher confidence than the
literature-synthesis sections.
