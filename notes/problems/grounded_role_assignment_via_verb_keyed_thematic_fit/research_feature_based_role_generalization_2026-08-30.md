# Research drill: does the brain GENERALIZE thematic-role fit for a NOVEL argument via FEATURE-based event knowledge rather than distributional similarity?

Problem: grounded_role_assignment_via_verb_keyed_thematic_fit
Date: 2026-08-30
Type: ONLINE literature/neuroscience drill (no experiments run)
Builds on: research_thematic_fit_disambiguation_regime_2026-08-30.md (established: thematic fit is a
  disambiguation-under-uncertainty mechanism = similarity-to-role-PROTOTYPE, not verb-noun co-occurrence
  lookup; SQ4 there already argued prototype > count for generalization). This drill does NOT re-derive
  that. It answers: WHAT representation is the prototype built over, and WHICH ready dataset to wire.

MOTIVATING EMPIRICAL RESULT (ours, measured, robust across 8 methods):
  general DISTRIBUTIONAL/lexical semantics CANNOT predict thematic role for a novel (verb,noun) argument.
  A noun's GloVe-300 vector predicts agent-vs-patient at BALANCED ACC 0.51 (chance 0.50) on held-out/OOV
  items, even with verb-conditioning + a verb x noun interaction term. Count-based verb-noun role
  co-occurrence is accurate only by MEMORISATION and does not survive to unseen pairs.

CENTRAL QUESTION: what representation does the brain use to assign/generalise a NOVEL argument's
  thematic-role fit for a verb -- is it FEATURE-BASED event knowledge rather than distributional similarity?

=====================================================================
VERDICT UP FRONT
=====================================================================
YES -- the brain's GENERALISING thematic-fit substrate is FEATURE-BASED (grounded, attribute/experiential)
event knowledge, NOT bag-of-words distributional/topic similarity. This is PINNED by convergent
psycholinguistic + neuro evidence AND independently reproduced by the computational-linguistics literature,
which finds bag-of-words word2vec/GloVe a "bad fit" for thematic fit and that syntax/dependency-based or
explicit role-filler-PROTOTYPE-over-features representations are what work. Our GloVe-0.51 null is the
EXPECTED signature of using a topic-similarity space for a job that needs a role-relevant FEATURE space.

ONE HONEST REFINEMENT (see SQ3 / contradiction flags): distributional is not literally zero. Strong
CONTEXTUAL models (LLMs) DO recover the COARSE selectional boundary (possible vs impossible events almost
always). What they and static embeddings fail at is the GRADED / GENERALISING end -- plausible vs merely
unlikely, and novel arguments. So the correct target for our build is graded fit + novel-argument
generalisation, exactly the regime a grounded feature substrate serves and distributional does not.

RANKED RECOMMENDATION (the fit-vector source to wire): keep it TWO-SIDED and TYPED, never lexical:
  VERB-SIDE (the "verb-keyed" half) = VerbNet selectional restrictions: what feature TYPE this verb's
    Agent/Patient slot demands (e.g. Agent [+int_control +animate], Patient [+concrete]).
  NOUN-SIDE (must type ARBITRARY/novel nouns) = a small grounded feature vector, sources ranked below.
  fit(noun, role, verb) = match(VerbNet-required-type[verb,role], noun-feature-vector). Every step types
  the noun by INFERRED features -> it scores unseen nouns -> it GENERALISES (the thing GloVe provably cannot).

=====================================================================
SQ1 -- Is verb-specific thematic fit computed over SEMANTIC FEATURES of role-fillers, not lexical vectors?
VERDICT: PINNED-BY-EVIDENCE.
=====================================================================
- McRae, Ferretti & Amyote (1997) "Thematic roles as verb-specific concepts": each verb specifies, per
  role, a feature-based PROTOTYPE of typical fillers built from world/situation knowledge; fit = feature
  similarity to that prototype (prior drill SQ4). Self-paced reading uses good-agent/poor-patient
  (WAITRESS) vs good-patient/poor-agent (CUSTOMER) items established by role/filler typicality norms --
  the discriminating variable is FEATURE typicality, not lexical form.
- McRae, Cree, Seidenberg & McNorgan (2005) "Semantic feature production norms" (Behavior Research Methods
  40:183): production feature norms for 541 living/nonliving basic-level concepts (an earlier set also
  covers event nouns + verbs). This is the empirical FEATURE BASIS -- the concrete inventory of the
  attributes (is_alive, has_legs, made_of_metal, used_for_X, ...) over which role prototypes are defined.
- Animacy is the SINGLE strongest role-relevant feature: "people assign the agent role to the NP highest
  in the animacy hierarchy"; "animacy is one of the most important criteria for thematic role
  restrictions"; Actor/Experiencer roles "heavily rely on animacy." The comprehension system rapidly
  checks whether a noun's CONCEPTUAL FEATURES fit the verb's semantic entailments ("propose requires an
  animate agent") and uses that to resolve role assignment. => role fit is a FEATURE match keyed to the verb.
- Direct feature-overlap-predicts-fit evidence: the computable analog (arXiv:1707.05967 "Measuring thematic
  fit with distributional feature overlap", prior drill) shows overlap in a FEATURE space predicts fit;
  and the psycholinguistic result is that role/filler TYPICALITY (a feature-similarity statistic), not
  lexical association, drives the reading-time effects.

=====================================================================
SQ2 -- How is a role assigned to a NEVER-SEEN-in-this-frame (or nonce) noun? Via inferred FEATURES?
VERDICT: PINNED-BY-EVIDENCE.
=====================================================================
- Generalized Event Knowledge (GEK), McRae & Matsuki (2009) "People use their knowledge of common events
  to understand language, and do so as quickly as possible": comprehenders store templates of common
  events (typical participants, instruments, locations); an isolated word IMMEDIATELY activates event
  knowledge, and word combinations constrain event expectations in real time.
- Elman (2009) "On the meaning of words and dinosaur bones: lexical knowledge without a lexicon" -- the
  WORDS-AS-CUES hypothesis: words are NOT containers of meaning; they are CUES that access stored event
  knowledge and modulate expectations. This is exactly the generalisation mechanism we need: a novel noun
  need only cue event knowledge via its inferred TYPE/FEATURES (is it animate? can it act? what are its
  affordances?) to activate the verb's role slots -- no memorised (verb,noun) pair required.
- Bicknell, Elman, Hare, McRae & Kutas (2010) "Effects of event knowledge in processing verbal arguments"
  (JML): comprehenders use knowledge of typical VERB-SPECIFIC agent-patient COMBINATIONS to anticipate
  upcoming arguments -- verb-keyed, feature/typicality-mediated anticipation, not lexical co-occurrence.
- Consequence: a feature/affordance-typed noun slots into event-schema roles gracefully even when unseen;
  a co-occurrence lookup returns nothing for an unseen pair. Our count-model's memorisation-only behaviour
  and the GloVe null are BOTH the predicted failure of a NON-feature-typed mechanism.

=====================================================================
SQ3 -- Is DISTRIBUTIONAL similarity KNOWN to be insufficient for thematic role? (matching our null)
VERDICT: PINNED for static bag-of-words; NUANCED (partly-recoverable coarse structure) for strong LLMs.
=====================================================================
- "Are Word Embeddings Really a Bad Fit for the Estimation of Thematic Fit?" (LREC 2020): standard
  bag-of-words word2vec/GloVe correlate WEAKLY with human thematic-fit judgments; SYNTAX/DEPENDENCY-based
  distributional spaces and explicit ROLE-FILLER-PROTOTYPE representations consistently outperform them.
  The paper's own conclusion: thematic fit needs representations that encode syntactic dependencies,
  role-filler prototypes, and selectional constraints -- precisely the structure a topic-similarity vector
  discards. This is a direct external reproduction of OUR null and its cause.
- Selectional-preference NLP consensus: conventional word embeddings are "not helpful" for selectional
  preference (predicate + relation -> preferred arguments); syntax-based / structured distributional models
  (e.g. the Structured Distributional Model, Chersoni et al.) are required to model verb-noun thematic
  relations. Brown et al. (2023, Cognitive Science) "Investigating the extent to which DSMs capture a
  broad range of semantic relations" -- DSMs capture taxonomic/associative relations far better than
  relational/role structure (abstract read; PDF not machine-parsed, treat the specific split as
  PARTIALLY-PINNED pending a clean pass).
- HONEST NUANCE -- Kauf et al. (2023) "Event knowledge in LLMs: the gap between the impossible and the
  unlikely" (Cognitive Science; n=1215 minimal pairs, 5 LLMs BERT->MPT): pretrained LLMs DO carry
  substantial event knowledge and "almost always assign higher likelihood to possible vs IMPOSSIBLE
  events" -- but there is a GAP: they do NOT reliably separate plausible from merely UNLIKELY. So strong
  contextual distributional models recover the COARSE selectional boundary but plateau at the GRADED end.
  Implication for us: (i) our 0.51 is specifically the failure of STATIC bag-of-words TOPIC similarity;
  (ii) the win we should target is GRADED fit + NOVEL-argument generalisation, not the coarse
  impossible-event boundary (already partly distributional). Do not overclaim "distributional carries zero
  role structure" -- claim "distributional carries little GRADED/GENERALISING role structure."

=====================================================================
SQ4 -- NEURAL substrate: is the role-relevant semantic space FEATURE/attribute-based (not co-occurrence)?
VERDICT: PINNED for ATL feature-integration hub; PARTIALLY-PINNED for angular-gyrus event-semantics link.
=====================================================================
- Hub-and-spoke (Patterson, Nestor & Rogers 2007; Lambon Ralph, Jefferies, Patterson & Rogers 2017,
  "The neural and computational bases of semantic cognition", Nat Rev Neurosci): the anterior temporal
  lobe (ATL) is a transmodal conceptual HUB that DISTILS modality-specific sensorimotor/affective FEATURES
  (the "spokes": vision, action, sound, valence...) into coherent amodal concepts. The representational
  substrate is FEATURE INTEGRATION, not lexical co-occurrence.
- Lesion evidence: semantic dementia (bilateral ATL atrophy) selectively impairs FEATURE INTEGRATION and
  acquisition of new conceptual knowledge (Lambon Ralph group) -- i.e. the hub's job is exactly assembling
  feature-based concepts, the ingredient thematic fit consumes.
- Controlled Semantic Cognition (Lambon Ralph 2017): a "semantic control" system (incl. LIFG/pMTG) flexibly
  weights hub representations to context/task -- consistent with the disambiguation-gated recruitment from
  the prior drill (thematic fit weighted up under conflict).
- Binder et al. (2016) "Toward a brain-based componential semantic representation" (Cognitive
  Neuropsychology 33:130): proposes ~65 EXPERIENTIAL attributes selected for NEURAL plausibility (sensory,
  motor, spatial, temporal, affective, social, cognitive), rated 0-6 for 535 words. A concrete, brain-
  anchored FEATURE space whose dimensions (social, cognition, emotion, motor, drive) directly encode the
  animacy/agentivity/sentience axes role assignment needs.
- Angular gyrus / event-semantics as the combinatorial event locus: consistent with the hub-and-spoke
  frame but I did NOT surface a clean fMRI demonstration tying AG event semantics specifically to
  thematic-role assignment in this drill. Mark PARTIALLY-PINNED; do not lean on AG specifics.

=====================================================================
SQ5 -- The MINIMAL role-relevant FEATURE substrate + READY datasets to wire (actionable)
=====================================================================
MINIMAL role-relevant feature set (convergent across McRae, Binder, VerbNet, animacy literature) -- ~5-8 dims:
  animacy ; sentience ; volition/agentivity (internal-control / causal-potency) ; concreteness/movability
  ; size/force ; affordance-for-the-verb's-action. Animacy is the dominant single dimension for agent/patient.

READY DATASETS, ranked by (brain-foundational x coverage-of-arbitrary-nouns x fit-to-the-verb-keyed shape):

VERB-SIDE (the "verb-keyed" half -- what feature TYPE the role demands) -- USE FIRST:
  #1 VerbNet selectional restrictions. Each thematic role in a VerbNet class may carry selectional
     restrictions drawn from ~35 semantic types: animate, human, animal, organization, INT_CONTROL
     (= internal control ~ volition/agentivity), concrete, comestible, substance, artifact, tool, vehicle,
     body_part, location, region, abstract, force, communication, currency, garment, ... This IS the
     verb-keyed selectional preference in exactly the typed/feature form we need (e.g. Agent[+int_control
     +animate], Patient[+concrete]). Generalises because it types the SLOT, not the filler. Caveat:
     hand-annotated, coarse, not present for every verb sense, English-centric -> back off to a default
     (Agent -> +animate/+int_control) or learn selectional preferences over the feature space for gaps.

NOUN-SIDE (must type ARBITRARY / novel nouns) -- ranked:
  #1 Lancaster Sensorimotor Norms (Lynott, Connell, Brysbaert, Brand & Carney 2020): ~40,000 words x 11
     grounded dims (6 perceptual: touch/hearing/smell/taste/vision/interoception; 5 action effectors:
     mouth-throat/hand-arm/foot-leg/head/torso). HIGHEST coverage AND brain-relevant (it IS the
     sensorimotor "spoke" system). Best single grounded source to type arbitrary nouns for movability /
     affordance / animacy-correlates. -> the coverage winner; wire this as the primary grounded vector.
  #2 WordNet supersenses / lexicographer files (noun.person, noun.animal, noun.artifact, noun.food,
     noun.substance, noun.location, ...): FULL lexical coverage of nouns; gives the single most important
     role feature (coarse animacy/agentivity type) for essentially ANY noun incl. rare/nonce-via-morphology.
     Cheapest to wire; use as the animacy/type backbone + back-off when a noun is out of the norm sets.
  #3 Binder et al. (2016) 65-attribute brain-based space: the MOST brain-foundational feature BASIS
     (defines the role-relevant dimensions with claimed neural correlates), but only ~535 words natively
     -> must be EXTENDED to arbitrary words by offline regression from embeddings (published extensions
     exist; a STATIC offline-built asset is admissible per the project's foundation-is-free-to-build rule).
     Use as the DIMENSION DEFINITION / target space, not the raw runtime lexicon.
  #4 McRae et al. (2005) production feature norms (541 concepts): the GOLD reference for WHICH features
     matter and for VALIDATING the minimal set / the prototype construction -- but coverage far too low to
     type arbitrary nouns at runtime. Use as the brain-anchored VALIDATION / anchor set, not the runtime source.
  (supporting: Brysbaert concreteness ~40k words -- one high-coverage dim; fold into the noun vector.)

RECOMMENDED WIRING (single sentence):
  build an OFFLINE, static noun-feature table = [WordNet-supersense animacy/agentivity type] (+)
  [Lancaster sensorimotor 11-dim] (+) [Brysbaert concreteness], project onto the Binder/McRae-validated
  ~5-8 role-relevant dimensions; at runtime score fit(noun,role,verb) = match to the VerbNet selectional
  type for (verb,role). No step ever consults a memorised (verb,noun) pair -> generalises to novel arguments.

=====================================================================
DOES ANYTHING CONTRADICT THE FEATURE-BASED HYPOTHESIS? -- honest check
=====================================================================
1. Kauf 2023 (strongest apparent complication, RESOLVED not fatal): strong CONTEXTUAL distributional
   models DO capture coarse event/role structure (possible vs impossible). So "distributional carries NO
   role info" is FALSE. The precise, defensible claim: static bag-of-words TOPIC similarity carries little
   GRADED/GENERALISING role structure; the coarse selectional boundary is partly distributionally
   recoverable, but the fine-grained, novel-argument fit we need is not -> that needs feature/relational
   representation. Consequence: set the WIN CONDITION as graded fit + novel-argument generalisation (where
   feature substrate beats distributional), NOT the coarse impossible-event boundary (a weak target).
2. Syntax-based DISTRIBUTIONAL models (dependency-typed spaces, Structured Distributional Model) ALSO beat
   bag-of-words on thematic fit -- so the winning axis is arguably "RELATIONAL/typed structure" as much as
   "grounded features per se." These are compatible (both discard topic-similarity for typed/role-keyed
   structure), but flag: a dependency-typed distributional space is an alternative to (or complement of) a
   hand-built feature substrate. The BRAIN-FAITHFUL choice is the grounded feature space (ATL hub-and-spoke
   is feature-integration, not dependency statistics); the ENGINEERING fallback if feature coverage is thin
   is a dependency-typed space. Keep both in view.
3. Binder/McRae feature spaces are themselves partly derived from verbal report and may carry some
   distributional contamination -- acceptable as an OFFLINE static FOUNDATION asset (foundation-is-free),
   but do not claim the feature source is distribution-free.
4. VerbNet coverage gaps (coarse, incomplete per-sense, English-centric) are an ENGINEERING risk, not a
   theory contradiction; mitigate with animacy-default back-off or learned selectional preferences.

=====================================================================
TLDR (plain English)
=====================================================================
The reason a plain "which words hang out near which words" vector cannot tell whether a new word is the
do-er or the done-to (our ~coin-flip result) is that this is the WRONG KIND of knowledge. The brain does
not decide roles from topic similarity; it decides from PROPERTIES of the thing -- is it alive, can it act
on its own, is it a solid object you can move, does it afford the action the verb names -- and matches
those properties against what the verb's do-er slot and done-to slot each demand. Because it reasons over
properties, it handles a word it has never seen in that sentence: it just asks "what kind of thing is
this?" and slots it in. So we should stop feeding role assignment a topic-similarity vector and feed it a
small PROPERTY vector instead. The verb's demands are already written down for us in an existing hand-built
verb dictionary (which role wants something alive / self-moving / a solid object). To describe an ARBITRARY
noun's properties we already have big ready-made lists: a 40,000-word set of how much each word involves
each sense and body action, a full dictionary tag for living-vs-thing, and a concreteness rating -- plus
two smaller, more brain-grounded property lists to define and check which properties actually matter. Wire
those as the source and the mechanism should finally generalise to new words, which the topic vector
provably cannot. One honesty note: very large language models DO get the crude cases right (a meal cannot
eat a person), so the real prize we are chasing is the FINE, GENERALISING judgment on new words, which is
exactly where the property-based route wins and the topic vector does not.

QUESTIONS: none.

NEXT STEPS
- Re-source the thematic-fit organ's fit vector from a two-sided TYPED substrate: VerbNet selectional
  restrictions (verb/role side) x an offline noun-feature table (Lancaster sensorimotor 40k (+) WordNet
  supersense animacy (+) Brysbaert concreteness), projected onto the ~5-8 Binder/McRae-validated role dims.
- Set the discriminator to NOVEL/OOV arguments + GRADED plausibility (not the coarse possible/impossible
  boundary): the feature substrate must beat GloVe-0.51 on held-out (verb,noun) pairs. A flat result there
  would be the real negative (diagnose: coverage gap in the noun typing vs genuine ceiling).
- Consider a dependency-typed distributional space (Structured Distributional Model) as an ENGINEERING
  fallback/complement if grounded-feature coverage proves too thin -- but the brain-faithful primary is the
  grounded feature space (ATL hub-and-spoke = feature integration).

=====================================================================
CITATIONS (URLs used in this drill)
=====================================================================
- McRae, Cree, Seidenberg & McNorgan 2005, Semantic feature production norms: https://link.springer.com/article/10.3758/BRM.40.1.183 ; https://pubmed.ncbi.nlm.nih.gov/16629288/
- McRae & Matsuki 2009, People use knowledge of common events (GEK): https://compass.onlinelibrary.wiley.com/doi/abs/10.1111/j.1749-818X.2009.00174.x ; https://uwo.scholaris.ca/server/api/core/bitstreams/c3e12b16-0628-4b53-9815-c6503471cf00/content
- Elman 2009, Words as cues / lexical knowledge without a lexicon: https://www.researchgate.net/publication/26724053_On_the_Meaning_of_Words_and_Dinosaur_Bones_Lexical_Knowledge_Without_a_Lexicon ; https://jeffelman.ucsd.edu/research/publications/
- Bicknell, Elman, Hare, McRae & Kutas 2010, Event knowledge in processing verbal arguments (JML) -- via McRaeLab pubs: https://sites.google.com/site/kenmcraelab/publications
- "Are Word Embeddings Really a Bad Fit for the Estimation of Thematic Fit?" LREC 2020: https://aclanthology.org/2020.lrec-1.700.pdf
- Brown et al. 2023, DSMs capture a broad range of semantic relations (Cognitive Science): https://onlinelibrary.wiley.com/doi/10.1111/cogs.13291 ; https://magnuson-psy.media.uconn.edu/wp-content/uploads/sites/1140/2024/07/Cognitive-Science-2023-Brown-Investigating-the-Extent-to-which-Distributional-Semantic-Models-Capture-a-Broad-Range.pdf
- Kauf et al. 2023, Event knowledge in LLMs: impossible vs unlikely (Cognitive Science): https://onlinelibrary.wiley.com/doi/full/10.1111/cogs.13386 ; https://arxiv.org/abs/2212.01488 ; https://www.evlab.mit.edu/s/event-knowledge-in-large-language-models-Kauf-Ivanova-et-al-2023-CogSci.pdf
- Patterson, Nestor & Rogers 2007 + Lambon Ralph, Jefferies, Patterson & Rogers 2017 (hub-and-spoke / CSC, Nat Rev Neurosci): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6006425/ ; https://www.jneurosci.org/content/37/1/141
- Semantic dementia / ATL feature integration: https://www.sciencedirect.com/science/article/pii/S0010945213002517
- Binder et al. 2016, Toward a brain-based componential semantic representation: https://pubmed.ncbi.nlm.nih.gov/27310469/ ; https://www.neuro.mcw.edu/index.php/resources/brain-based-semantic-representations/
- Lancaster Sensorimotor Norms (Lynott, Connell, Brysbaert, Brand & Carney 2020): https://link.springer.com/article/10.3758/s13428-019-01316-z ; https://www.lancaster.ac.uk/psychology/lsnorms/ ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7280349/
- VerbNet selectional restrictions / semantic types: https://verbs.colorado.edu/verb-index/VerbNet_Guidelines.pdf ; https://premon.fbk.eu/ontology/vn
- Structured Distributional Model (Chersoni et al.) -- syntax-based thematic fit: https://arxiv.org/pdf/1906.07280
- McRae, Ferretti & Amyote 1997 (Thematic roles as verb-specific concepts): https://www.tandfonline.com/doi/abs/10.1080/016909697386835
- Thematic fit via distributional feature overlap (computable analog): https://arxiv.org/pdf/1707.05967
