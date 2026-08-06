# Deep brain-foundational audit: SEMANTIC FEATURE ACQUISITION + GROUNDING (2026-08-06)

**Filed by:** research (Sonnet). **Methodology note:** three parallel Sonnet lit-scan sub-agents
were dispatched (Binder feature taxonomy + developmental acquisition; abstract-concept grounding;
fast-mapping/novel-word learning). All three completed and their WebSearch/WebFetch-verified
findings are folded in below (confidence flags are each sub-agent's own self-report, carried
through unchanged: HIGH = primary source directly fetched and read; MEDIUM = triangulated across
2+ independent secondary sources; LOW = single-source or title/abstract-only). An initial pass of
this note was drafted before the sub-agents returned (from trained knowledge only, flagged
"recalled, not fetched") per an in-session directive not to block further — that draft has been
SUPERSEDED by this version once all three returned; disk-verified internal grounding (below) is
unchanged across both versions.

Internal (disk-verified) grounding comes from three same-session prior drills, cited throughout
rather than re-derived: `notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md` (ATL hub
SHAPE/POSITION/METRIC, 38 citations, freshly web-verified that session),
`notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md` (verb-feature SHAPE taxonomy +
a measured pilot, ~25 citations, freshly web-verified that session), and
`notes/research_drill_biology_led_learning_mechanism_earned_grounding_simulation_appraisal_action_causal_credit_2026-08-03.md`
(the appraisal->action-tendency dopaminergic-RPE learning mechanism, disk-verified against a
HARD_PASS organ). Direct reads of `hdlab/lexical_similarity.py` and
`hdlab/verb_lexical_similarity.py` (full docstrings + tag tables) are disk-verified this session and
are the ground truth for Deliverable 4.

---

## HEADLINE

The brain does not have a feature LIST — it has a **learned, graded, distributed activity pattern
across ~65 experiential attributes spanning 14 neural-system domains** (Binder, Conant, Humphries,
Fernandino, Simons, Aguilar & Desai 2016, *Cognitive Neuropsychology* — HIGH, PubMed abstract
fetched: Vision, Somatic, Audition, Gustation, Olfaction, Motor, Spatial, Temporal, Causal, Social,
Cognition, Emotion, Drive, Attention), bound into a retrievable concept by **repeated associative
co-activation** (Barsalou's "accumulating... aggregate results of superimposing information on
relevant neural systems time after time," HIGH — direct quote fetched) consolidated via **fast
hippocampal one-shot binding -> slow cortical statistical integration via replay** (Complementary
Learning Systems, McClelland/McNaughton/O'Reilly 1995, MEDIUM). **Concrete concepts ground directly
in perceptual/motor spokes; abstract concepts ground via at least four convergent, non-exclusive
routes**, none alone sufficient (Desai, Reilly & van Dam 2018's explicit "multifaceted abstract
brain" conclusion, MEDIUM): situated/introspective simulation (Barsalou & Wiemer-Hastings 2005,
HIGH — fetched directly, quantified 11.47x more introspection-language for abstract vs concrete
words), affective/valence experience (Kousta, Vigliocco, Vinson, Andrews & Del Campo 2011's
Affective Embodiment Hypothesis, HIGH-fetched but genuinely **contested** — Paivio 2013 dispute
flagged), metaphorical mapping onto concrete source domains (Lakoff & Johnson, HIGH-fetched
overview but this framework's **own source material self-concedes** no direct neural evidence
exists for the specific GOAL-relevant mapping), and — for goal/outcome-valence concepts
specifically — value-to-action-coupling circuitry (Reber et al. 2017's vmPFC double-dissociation,
HIGH-fetched) plus mirror-neuron goal-of-action-chain coding (Fogassi et al. 2005, HIGH-fetched)
plus this substrate's own already-earned dopaminergic-RPE analog (`pfc_gate_cfrpe_trained_v2`,
disk-verified HARD_PASS). New words get features not by fresh induction from raw sensory data but
by **Bayesian inference over an already-grounded taxonomic hypothesis space, sharply reweighted by
a "size principle"** (Xu & Tenenbaum 2007 — with n=1 example, ~57% basic-level generalization;
with n=3 identical subordinate examples, generalization narrows to ~7% — MEDIUM-HIGH, well-
triangulated), layered under coarser Markman/shape-bias constraints, and — for verbs specifically —
**syntactic bootstrapping**: the argument-structure frame a verb appears in supplies semantic
evidence independent of, and sometimes in the total absence of, direct perceptual grounding
(Naigles 1990's transitive/intransitive frame-flip result; Landau & Gleitman 1985's blind-children
"look"/"see" acquisition — both HIGH, well-triangulated). **`hdlab/lexical_similarity.py` and
`hdlab/verb_lexical_similarity.py` implement NEITHER of these two brain properties**: their feature
tags are (1) SUPPLIED once by a human, never statistically induced from co-activation across
experience, and (2) ABSTRACT SYMBOLIC LABELS with zero experiential content — a `POS_VALENCE` tag
is constructed identically (a random FHRR index vector) to a `NAUTICAL` tag. **A genuine literature
gap, independently corroborated by the fast-mapping sub-agent, sharpens this: even the BEST real
computational induction mechanisms found (Fazly, Alishahi & Stevenson 2010; Alishahi & Stevenson
2008) still take a PRE-GIVEN, human-annotated "meaning-element" vocabulary as input — i.e., the
published literature's own best induction algorithms have exactly the same "supplied symbolic
feature vocabulary" limitation this substrate's lexicons have; no system was found that induces
BOTH the feature values AND the feature ontology from grounded data at open-domain scale.**

**Bottom line on which sub-gap is load-bearing:** the LEARNED-vs-SUPPLIED gap is the one currently
blocking raw COVERAGE and has a cheap, already-piloted buildable path (the verb drill's Tier-2
similarity-extension mechanism). The GROUNDED-vs-ABSTRACT-SYMBOLIC gap is deeper and, per this
session's literature scan, **the field itself has not solved it either** — the best published
induction mechanisms extend symbolic labels further, they do not ground them. For genuinely
open-ended generalization on abstract/affective concepts (goal/hope/fail), **the GROUNDED gap is
the harder ceiling**, and closing (a) first is still correct — it is a precondition for testing how
far symbolic extension can carry abstract concepts before hitting that ceiling, not a substitute
for closing it.

---

## 1. WHERE FEATURES COME FROM (brain SHAPE / POSITION / METRIC)

### 1a. The spoke systems ARE the grounding — Binder's componential model (verified this session)

Binder, Conant, Humphries, Fernandino, Simons, Aguilar & Desai (2016, "Toward a brain-based
componential semantic representation," *Cognitive Neuropsychology* 33(3-4):130-174 — **HIGH**,
PubMed abstract fetched directly) proposes **~65 experiential attributes across 14 domains**:
Vision (brightness/color/motion/form/biological-motion), Somatic (touch/temperature/weight/
texture/pain), Audition, Gustation, Olfaction, Motor (head-face/upper-limb/lower-limb/practice),
Spatial (landmark/path/scene/direction), Temporal, Causal (agentive/consequential), Social
(interaction/human/communication/self-relevance), Cognition, Emotion (benefit/harm/valence/
arousal), Drive (hunger/needs), Attention. Attributes are rated on a **graded, continuous scale**
(originally 0-6; **MEDIUM-domain-detail confidence**, sub-attribute-list-within-domain
approximately but not verbatim confirmed). A direct follow-up, Tong, Binder, Humphries, Mazurchuk,
Conant & Fernandino (2022, "An fMRI Dataset for Concept Representation with Semantic Feature
Annotations," *Scientific Data* 9:349 — **HIGH**, full content fetched) retained **54 of the
original 67 attributes** after dropping 13 for excessive intercorrelation (r>0.8) — i.e., even the
brain's own dimensions are not cleanly orthogonal, consistent with graded overlapping neural coding
rather than a clean discrete feature list — collected via crowdsourced ratings, ~30 participants per
feature, 1-7 Likert scale. Fernandino, Tong, Conant, Humphries & Binder (2022, "A Distributed
Network for Multimodal Experiential Representation of Concepts," *J Neuroscience* 42(37):7121-7132
— **MEDIUM**, full text paywalled, search-snippet triangulated) directly compared a multimodal
experiential-attribute model against single-modality models AND against a pure distributional
(word-co-occurrence) model in predicting neural similarity structure: **the multimodal experiential
model explained more variance than either alternative** — a direct, quantified confirmation that
grounded/experiential feature content is doing real, separable neural work beyond what text
co-occurrence alone captures (directly relevant to Section 4's SHAPE gap).

### 1b. Statistical/Hebbian learning binds spoke features into one concept (verified this session)

**Barsalou's accumulation mechanism** (Barsalou & Wiemer-Hastings 2005 lineage; direct quote
retrieved via a PMC review, **MEDIUM-HIGH**): *"On each occasion when pizza is consumed, a
distributed associative pattern becomes established across these neural systems. Across many
episodes... an increasingly entrenched associative network emerges throughout the brain,
accumulating the aggregate results of superimposing pizza information on relevant neural systems
time after time."* This is explicitly accumulation-based associative binding through repeated
grounded experience — functionally Hebbian ("fire together, wire together") though the fetched text
does not itself use that exact formal terminology.

**Rogers & McClelland's computational hub-and-spoke PDP model** (Rogers, Lambon Ralph, Garrard,
Bozeat, McClelland, Hodges & Patterson 2004, *Psychological Review* 111(1):205-235; book: Rogers &
McClelland 2004, *Semantic Cognition* — **MEDIUM**, search-triangulated, not directly fetched): a
feedforward connectionist network where item+context units feed a hidden "representation"/hub layer
generating modality-specific attribute outputs, trained by **gradual, error-driven weight
adjustment** ("semantic knowledge is acquired through the gradual adjustment of connection
strengths in the course of day-to-day experience") — i.e., a supervised/error-correction learning
process over many trials, explicitly NOT a one-shot hand-coded feature list. This produces the
documented developmental hallmarks the model was built to explain: progressive category
differentiation (broad->fine as training accumulates, paralleling Keil/Mandler's developmental
findings), transient illusory correlations, basic-level advantage, and graceful/graded degradation
under damage (semantic dementia). A directly-fetched PMC review (PMC3884130, **MEDIUM**) confirms
the anatomical mapping: ATL = transmodal hub; spokes = ventral occipitotemporal (vision), posterior
superior temporal gyrus (audition/verbal), inferior parietal cortex (motor/action) — and
importantly states the ATL hub is causally implicated in **ACQUISITION of novel concepts**, not
just storage of old ones (demonstrated via feedback-driven category-learning tasks in
semantic-dementia patients).

**The two-stage learning dynamic — Complementary Learning Systems** (McClelland, McNaughton &
O'Reilly 1995, *Psychological Review* 102(3):419-457 — **MEDIUM**, well-triangulated, primary PDF
not directly extractable this session): **hippocampus** performs fast, sparse, pattern-separated
near-one-shot binding of a novel multimodal experience (avoiding catastrophic interference);
**neocortex** extracts slow, distributed, interleaved statistical regularities across many such
episodes via small incremental weight changes. Consolidation = hippocampal-driven **reinstatement/
replay** of the episode pattern in neocortex (including offline, e.g. sleep), with each replay
producing a small neocortical update; semantic/generalized concept knowledge is the accumulated
residue of many such replays. This is the SAME fast-episodic + slow-statistical-via-replay
architecture this substrate's own Aug-3 drill already grounds the appraisal/goal-credit learning
mechanism in (hippocampal reverse replay, Foster & Wilson 2006) — a genuine, disk-checkable REUSE
candidate this audit flags but does not resolve (Section 4).

### 1c. Developmental acquisition — even the feature ONTOLOGY is learned, not innate (verified)

Landau, Smith & Jones (1988, *Cognitive Development* 3:299-321, "The importance of shape in early
lexical learning" — **HIGH**, well-triangulated canonical finding): by ~age 2, children extend
novel object names primarily by shape similarity over texture/size, a bias that STRENGTHENS with
development (2yo -> adult). Critically, **Colunga & Smith (2005)** built a connectionist model
whose emergent shape-weighting bias tracked the ACTUAL co-occurrence statistics between object
solidity and naming pattern in real child-directed vocabulary (most early nouns name solid,
shape-organized artifact categories) — a direct computational demonstration that the shape bias is
NOT a perceptual default but an emergent product of statistical learning over the ambient
vocabulary's structure. **Cross-linguistic confirmation** (English vs Japanese children show
different bias strength, tracking each language's different naming statistics — **MEDIUM**) rules
out an innate-only account. Training studies show teaching children shape-organized categories
CAUSALLY induces a precocious shape bias and accelerates subsequent vocabulary growth — direct
experimental (not just correlational) evidence the feature-weighting POLICY, not just individual
feature values, is learned from grounded experience. **This is the single sharpest verified finding
for Deliverable 4's framing**: the brain doesn't just learn WHICH tag applies to a word, it learns
WHICH DIMENSIONS ARE WORTH TAGGING AT ALL from statistical structure in the input — a capability
this substrate's hand-authored, fixed tag vocabulary has no analog of whatsoever.

Yu & Smith's cross-situational learning in 12-14-month-old infants (Section 3) and Smith's
embodied-attention/head-camera work (PMC5866780, "The developing infant creates a curriculum for
statistical learning" — **LOW-MEDIUM**, title/thrust confirmed, not deeply fetched) add that the
infant's OWN motor/attentional behavior actively SAMPLES and GENERATES the correlated multimodal
training data (holding an object close, rotating it) rather than passively receiving a supplied
feature list — learning is active self-sampling over a self-generated, developmentally-ordered
curriculum, not exposure to external ground truth.

### 1d. Verb-specific features — verified this session, corroborating and sharpening the sibling drill

Vinson & Vigliocco (2008, "Semantic feature production norms for a large set of objects and
events," *Behavior Research Methods* 40(1):183-190 — **MEDIUM**, triangulated across search
sources, primary PDF paywalled/blocked, consistent with the sibling verb drill's own independent
"paywalled" flag): norms from ~280 participants over 456 words — 169 concrete-object nouns, 71
event nouns, **216 event verbs** — the first systematic property-listing norm set for events/verbs
(prior norm databases, e.g. McRae's, covered only concrete nouns). **Structural finding**: noun/
object features are more intercorrelated and organized along tight taxonomic lines (many animals
share "has legs"/"is alive"); verb/event features are more idiosyncratic and distributed, producing
a semantic space that is more multidimensional but LESS taxonomically clustered — retrieving one
verb's features is less likely to facilitate retrieval of semantically related verbs than the
analogous noun case. Vigliocco, Vinson, Lewis & Garrett's FUSS model (2004, *Cognitive Psychology*
48:422-488 — **HIGH**, abstract directly fetched) explicitly argues this is a difference in the
STATISTICS of real-world feature co-occurrence for objects vs events, not a difference in
representational format or learning mechanism — the same underlying featural machinery, applied to
domains with different natural feature-density. A directly-fetched PMC review (PMC4029073,
**MEDIUM**) confirms the matching neural dissociation: concrete nouns show stronger inferior
temporal (visual/object-form) activation; concrete verbs show stronger motor/premotor activation —
directly mirroring the behavioral feature-type asymmetry in actual brain data, and independently
corroborating the sibling verb drill's own Kemmerer 2008 citation (fractionated, non-unified verb
meaning systems).

---

## 2. GROUNDING OF ABSTRACT CONCEPTS (goal, hope, fail, praise — the crux, verified this session)

**(i) Situated/introspective simulation, quantified.** Barsalou & Wiemer-Hastings (2005, "Situating
abstract concepts," in *Grounding Cognition* — **HIGH**, chapter PDF fetched directly): property-
listing studies find abstract words (truth, freedom, justice) elicit disproportionately more EVENT
properties (properties of the situations they occur in) and INTROSPECTIVE properties (mental
states, emotions, motivations of an agent in that situation) plus social/relational content, versus
concrete words' predominantly ENTITY (physical/observable) properties. Zdrazilova et al. (PMC6015825
— **HIGH**, fetched directly) quantify this with a real effect size: **introspection-related
utterances are ~11.47x more likely, and person/participant references ~7.39x more likely**, when
people describe abstract vs concrete word meanings. Abstraction grounds in more complex,
relational, social/introspective content, not in simple object-perception content — it does not
escape grounding.

**(ii) Affective/interoceptive grounding — the Affective Embodiment Hypothesis, genuinely
contested.** Kousta, Vigliocco, Vinson, Andrews & Del Campo (2011, *JEP: General* — **HIGH**,
PubMed abstract fetched directly): abstract words carry disproportionately higher emotional
valence than concrete words at matched frequency, and this affective content explains a RESIDUAL
abstract-word processing advantage even after statistically controlling for imageability (dual
coding theory) and context availability — i.e., emotion, not just imageability, is doing real
explanatory work. **Flagged explicitly, per the sub-agent's own finding: this is a LIVE, CONTESTED
empirical debate** — Paivio (2013, dual-coding defender) published a critical response and Kousta
et al. replied; treat as an active controversy, not settled consensus. This predicts FAIL/SUCCESS/
HOPE-type outcome-valence words specifically should ground especially well via affective simulation
given their strong inherent valence.

**(iii) No single mechanism — Desai's explicit multi-system conclusion.** Desai, Reilly & van Dam
(2018, "The multifaceted abstract brain," *Phil Trans R Soc B* — **MEDIUM**, search-triangulated):
a meta-analysis across four abstract-concept domains (numerical, emotional, moral judgment,
theory-of-mind) concludes there is **no single grounding mechanism for all abstract concepts** —
different abstract-concept TYPES recruit different combinations of event-based, interoceptive,
introspective, and sensorimotor representation, directly arguing against any monolithic
"abstract=affect-only" or "abstract=metaphor-only" account. Two Desai-lineage follow-ups (2024,
PubMed 38342187, title-only-confirmed, **LOW-MEDIUM**; 2026, ScienceDirect, title-only, **LOW**)
extend this into an explicit "multiple representation framework": abstract meaning = sensory +
motor + emotional + social + mentalizing + hub representations working jointly, with the 2024 paper
specifically titled around **mental-state concepts engaging the mentalizing network** — directly
relevant to GOAL/DESIRE/INTENTION.

**(iv) Value-to-action coupling — a genuine double dissociation, directly relevant to what "goal"
computationally IS.** Reber, Feinstein, O'Doherty, Liljeholm, Adolphs & Tranel (2017, "Cortical
areas needed for choosing actions based on desires," *Brain* 140(6):1539-1552 — **HIGH**, fetched
directly): patients with vmPFC lesions, after satiety-based devaluation of a food reward, could
still correctly JUDGE the food as now less desirable (intact desirability knowledge, an OFC-type
value representation) but FAILED to inhibit action toward the now-devalued goal — a clean double
dissociation between (a) having a value/desirability representation and (b) COUPLING that value to
action selection. **This is the single sharpest mechanistic finding of this section**: a "goal," at
the neural-computational level, is not merely a value signal — it is a value signal actively
coupled to an action policy, and these are separable neural components (OFC value vs vmPFC
coupling).

**(v) Mirror-neuron goal-of-action-chain coding — directly fetched, concrete, single-neuron-level.**
Fogassi, Ferrari, Gesierich, Rozzi, Chersi & Rizzolatti (2005, *Science* — **HIGH**, fetched
directly): macaque parietal (AIP) mirror neurons, during grasp-to-eat vs grasp-to-place-in-container
tasks with kinematically IDENTICAL initial reach/grasp movements, fire DIFFERENTIALLY depending on
the downstream goal of the action CHAIN — some neurons fire only for grasp-to-eat, others only for
grasp-to-place. This shows the parieto-frontal mirror system encodes the goal/intention of an
action sequence, prospectively, distinct from its literal motor kinematics, and is proposed as the
biological mechanism allowing observation of a partial action to predict its ultimate goal
(intention-reading) — a plausible developmental/evolutionary precursor to the higher-level
mentalizing network's more abstract theory-of-mind computations. This grounds CONCRETE, immediate,
embodied goals; per the sibling verb-feature drill's own independently-verified finding (Muraki,
Pexman & Binney 2025; Lin, Bi, Zhao et al. 2015), ABSTRACT/social/narrative-timescale goals instead
recruit the mentalizing network (mPFC/TPJ) — two partially dissociable routes, both real and both
disk/lit-corroborated, not this note's own invention.

**(vi) Conceptual metaphor theory — the framework's OWN source material concedes the weakest neural
evidence of the four routes.** Lakoff & Johnson's account (a review specifically on metaphor
neural circuitry, PMC4267278 — **HIGH**, fetched directly): the **SOURCE-PATH-GOAL** image schema
maps onto the Purposeful Action Schema via the primary metaphor "Purposes Are Destinations" ("goals
are destinations," "on track," "long road ahead," embedded in the "Life Is A Journey" family). The
neural evidence the review itself cites (Singer et al. 2006 shared insula/ACC for physical +
empathic pain; Thibodeau & Boroditsky 2013 crime-framing behavioral effects; Zhong & Liljenquist
2006 / Williams & Bargh 2008 moral/social-warmth priming) is **for entirely different metaphor
families** (pain, purity, warmth) generalized to the goal/path mapping BY ANALOGY, not direct
evidence for it. **The fetched review itself explicitly states**: "there is no one 'module' in the
brain that handles... metaphor, or abstract thought," individual variation in imagery is large, and
"current neuroscience techniques are not likely to find evidence of all the metaphors" claimed —
this is a genuine, source-conceded gap, the weakest-evidenced of the routes surveyed for direct
neural instantiation, though the most frequently invoked in popular accounts.

**Composite, synthesized answer for GOAL / HOPE / FAIL specifically (this note's own synthesis,
capped novel-synthesis P<=0.50, built from the six verified components above):** GOAL (mental-state
sense) = mentalizing network (mPFC/TPJ) representation of a desired future state, COUPLED to action
policy via vmPFC (Reber), with a concrete-action precursor in parietal mirror-neuron goal-chain
coding (Fogassi). HOPE = the same mentalizing representation of a future, unrealized, desired state
plus reward-ANTICIPATION circuitry (ventral striatum/OFC) for its positive-anticipatory-valence
component. FAIL/SUCCESS (outcome valence relative to a goal) = **the most directly and cleanly
grounded of the three, not a metaphorical extension at all** — it is (a linguistic label for) the
dopaminergic reward-prediction-error signal (Schultz 1997, disk-cited via the Aug-3 drill, not
re-verified this session): success = better-than-expected/goal-attained outcome (positive RPE);
fail = worse-than-expected/goal-blocked outcome (negative RPE). This substrate already has a
disk-verified HARD_PASS organ (`pfc_gate_cfrpe_trained_v2`) earning exactly this signal in its
appraisal-simulation domain — see Section 4.

---

## 3. THE LEARNING MECHANISM — how a NEW word gets features (verified this session)

**Fast mapping** (Carey & Bartlett 1978, "Acquiring a single new word" — **HIGH**, well-
triangulated): n=20 children, single exposure to a novel color word ("chromium," olive-green) in a
contrastive frame ("bring me the chromium tray, not the red one"); all succeeded immediately;
follow-up testing weeks-to-months later showed most retained only PARTIAL, category-level knowledge
(it's a color word, distinct from an already-known color) — full adult-like feature content
requires much later "extended/slow mapping." Markson & Bloom (1997, *Nature* 385:813-815,
"Evidence against a dedicated system for word learning in children" — **HIGH**, well-triangulated,
title itself is the correction some secondary sources mis-report the opposite direction of):
children fast-mapped a novel WORD and an arbitrary FACT about an object with equal facility and
equal 1-week retention — direct evidence fast mapping is **domain-general** encoding/inference
machinery applied to language, not a dedicated linguistic module. Mechanistically: mutual
exclusivity (Markman 1990) does the disambiguation work — a novel word is assumed to label the
one unlabeled thing in the scene — so the FIRST-PASS content assigned is minimal/categorical, not a
full feature vector.

**Cross-situational statistical learning, with a real formal mechanism, not just a behavioral
phenomenon.** Yu & Smith (2007, *Psychological Science* 18:414-420 — **HIGH**, fetched directly):
under trials with ZERO within-trial disambiguation (any word could map to any pictured object),
learners still converge on correct word-object mappings purely by tracking co-occurrence
consistency ACROSS trials. Siskind (1996, *Cognition* 61:39-91 — **MEDIUM**, well-triangulated): an
actual rule-based cross-situational + contrast-principle computational ALGORITHM predating Yu &
Smith's human study by over a decade — a genuine, implemented existence-proof that cross-situational
statistics alone are sufficient in principle to solve the reference-ambiguity ("gavagai") problem.
Frank, Goodman & Tenenbaum (2009, *Psychological Science* 20:578-585 — **MEDIUM**, well-
triangulated): a Bayesian generative model performing JOINT inference over speaker referential
intent and word-referent mapping, outperforming pure co-occurrence association and matching human
data — a real formal computational model, not a hand-wave.

**Distributional bootstrapping over a grounded, hierarchically-structured PRIOR — the size
principle, with real numbers.** Xu & Tenenbaum (2007, *Psychological Review* 114(2):245-272 —
**MEDIUM-HIGH**, math independently corroborated across 3+ triangulated sources including a PMC
paper walking through the derivation): word learning as Bayesian inference over a hypothesis space
STRUCTURED by an already-grounded taxonomic hierarchy (subordinate < basic < superordinate), with
likelihood proportional to (1/|hypothesis size|)^n — the "size principle"/suspicious-coincidence
effect. Concretely: with **1** example, learners generalize broadly (**~57%** basic-level
generalization); with **3** identical subordinate-level examples, generalization sharply narrows
(**~7%**) — confirmed in both adults and 3-4-year-olds across multiple taxonomies. This is the
clearest formal answer to "how does a new word get features": selection from an ALREADY-STRUCTURED
hypothesis space via Bayesian updating, never induction from a blank slate. Markman's (1990)
constraints (whole-object, taxonomic, mutual-exclusivity) prune the hypothesis space by KIND
before this taxonomic-level Bayesian reasoning even begins; Landau/Smith/Jones's shape bias supplies
a learned dimension-weighting prior operating within that pruned space — three layered, all
verified, all resting on pre-existing grounded structure.

**Syntactic bootstrapping for VERBS specifically — the channel that operates independent of, or
even in the total absence of, direct grounded observation.** Naigles (1990, "Children use syntax to
learn verb meanings," *Cognitive Development* — **HIGH**, well-triangulated canonical result):
24-27-month-olds shown an ambiguous scene (simultaneous causal push-into-squat action + non-causal
mutual arm-waving) interpret a novel verb ("gorping") as the CAUSAL action when introduced
transitively ("the duck is gorping the bunny") but as the NON-CAUSAL action when introduced
intransitively ("the duck and bunny are gorping") — same scene, same novel verb, syntax alone flips
the assigned meaning. Landau & Gleitman (1985, *Language and Experience: Evidence from the Blind
Child* — **MEDIUM-HIGH**, well-triangulated): blind children acquire perception verbs ("look,"
"see") on a normal developmental timetable despite lacking the matching visual-grounding channel
entirely, using the verbs' syntactic environments as the primary evidentiary source instead — the
foundational demonstration that syntax can carry semantic weight when grounded observation is
UNAVAILABLE. Gleitman (1990, *Language Acquisition* 1:3-55 — **HIGH**, well-triangulated): for verb
pairs describing the identical physical event from different perspectives (chase/flee, buy/sell),
the observable world scene alone cannot determine which verb applies — syntax MUST contribute
independent information. **Relationship to semantic bootstrapping (Pinker):** current consensus
treats syntactic and semantic bootstrapping as complementary, not competing, though there is a real,
acknowledged tension over sufficiency (Pinker argued Gleitman overstated how far syntax alone
carries verb learning) — flagged as a genuine, still-open theoretical question, not resolved
consensus.

### The load-bearing sub-question, now answered with real citations: is there an actual
### computational INDUCTION mechanism, or only descriptive behavioral literature?

**Real, implemented mechanisms exist — and they share this substrate's exact limitation.** Fazly,
Alishahi & Stevenson (2010, *Cognitive Science* 34:1017-1063 — existence **HIGH**, well-
triangulated + public code release; content detail **MEDIUM**): an incremental, EM/alignment-style
model representing each word's meaning as a probability distribution over "meaning elements,"
updated per-exposure via general-purpose statistical alignment (no dedicated word-learning module),
reproducing human suspicious-coincidence learning curves. **Critical, load-bearing limitation,
directly analogous to this substrate's own gap**: the meaning-element VOCABULARY itself is
pre-specified from an annotated corpus — the model induces which elements apply to a NEW word, but
does not induce the elements/dimensions themselves from grounded/perceptual data. Alishahi &
Stevenson (2008, *Cognitive Science* 32:789-834 — **MEDIUM-HIGH**): a Bayesian model directly
targeting VERB argument-structure acquisition, clustering usage instances into probabilistic
syntax-semantics construction associations and reproducing developmental overgeneralization/
retreat trajectories — the closest direct computational analog to this substrate's own verb-feature
Tier-2 problem, though scoped to argument-structure/semantic-role induction, not full featural
content. Regier (1996, *The Human Semantic Potential* — **MEDIUM**, not directly fetched): a
connectionist network taking GROUNDED perceptual primitives (motion features from simple 2D
object-movement scenes) as input and learning to classify spatial-term meaning across languages
(English/German/Russian/Japanese/Mixtec) — the closest single hit to "grounded primitives in, word
meaning out," but scoped narrowly to spatial prepositions. Piantadosi, Tenenbaum & Goodman (2012,
*Cognition* 123:199-217 — **MEDIUM-HIGH**): a Bayesian program-induction model over a compositional
"language of thought," combining a small set of grounded primitives (subitizing-based small-set
cardinality) with probabilistic-grammar search to construct compositional meanings for new number
words, reproducing empirically-documented "knower-level" developmental stages — structurally
matches the exact spec of "grounded primitives + search -> new-word feature composition," but
validated only on the number-word domain. Abend, Kwiatkowski, Smith, Goldwater & Steedman (2017,
*Cognition* 164:116-143 — **MEDIUM**): a CCG-based Bayesian model jointly inducing grammar and
lexicon from sentence-meaning pairs at corpus scale, the most engineering-scale instantiation of
syntactic bootstrapping as a real algorithm (not just a behavioral phenomenon); a 2024 follow-up
found syntactic and semantic bootstrapping are STRONGEST when learned jointly, resolving the
Pinker/Gleitman tension computationally in favor of complementarity.

**Explicit, disk-relevant gap (the sub-agent's own flagged conclusion, independently corroborating
this audit's Section 4):** no single published system was found that takes (i) a small set of
GROUNDED core primitives, (ii) a novel word's syntactic frame, and (iii) its distributional context,
and jointly outputs an open-domain feature-set for that word across BOTH nouns and verbs uniformly.
Every real mechanism found covers only part of the pipeline: domain-narrow-but-grounded (Regier:
spatial terms only; Piantadosi et al.: number words only), or feature-vocabulary-narrow (Fazly et
al.: meaning-elements pre-given, not perceptually induced), or verb-specific-but-shallow (Alishahi
& Stevenson: argument structure/semantic roles, not full features), or syntax-scale-but-not-
grounded (Abend et al.: corpus-scale grammar+lexicon induction, no perceptual grounding component).
**This is directly relevant to calibrating Deliverable 4's tractability claim**: the field's own
best induction mechanisms have NOT solved the "grounded primitives + open-domain feature induction"
problem either — this substrate's gap (a) is closable via the SAME kind of similarity-extension-
over-a-pre-given-vocabulary approach the literature's best systems already use (Fazly et al.'s own
limitation matches exactly), but gap (b) (grounding the vocabulary itself) remains open EVEN IN
THE PUBLISHED LITERATURE, not just in this substrate.

---

## 4. THE PRECISE GAP vs OUR IMPLEMENTATION

Disk-verified this session directly from `hdlab/lexical_similarity.py` and
`hdlab/verb_lexical_similarity.py` (full file reads, not recalled):

| Dimension | Brain (Sections 1-3 above) | This substrate (`hdlab/*_lexical_similarity.py`) |
|---|---|---|
| **SHAPE** | Continuous, graded, DISTRIBUTED activity across ~65 attributes / 14 neural-system domains (Binder et al. 2016, verified); a feature's vector content IS the relevant sensorimotor/affective computation, and a multimodal EXPERIENTIAL model measurably beats a pure distributional model at predicting neural similarity (Fernandino et al. 2022, verified) | Discrete, mutually-orthogonal-ish SYMBOLIC STRING TAGS (`"NAUTICAL"`, `"POS_VALENCE"`, `"RESULT_ROOT"`), each an opaque label bundled via FHRR `bundle()`; **the vector for `POS_VALENCE` is constructed IDENTICALLY to the vector for `NAUTICAL`** — a random `unit_phase_vec` index — the representation itself makes zero distinction between a nominally-affective tag and a nominally-taxonomic one; neither carries any actual experiential content |
| **POSITION** | Continuously updated across the whole lifespan; even the feature ONTOLOGY (which dimensions matter) is itself learned from the statistics of grounded experience (Colunga & Smith 2005's computational demonstration that the shape bias emerges from vocabulary statistics, verified) | A human decided the tag vocabulary and word-to-tag assignments ONCE, at authoring time (`CONCEPT_FEATURES`: 89 concepts; `OUTCOME_VERB_FEATURES`/`GOAL_VERB_FEATURES`: ~150 lemma-keys) — a static dictionary, frozen unless a human edits it again. Both modules' own docstrings state this explicitly: "General open-vocabulary feature coverage... is a separate, missing-LEARNING follow-up, not claimed here." |
| **METRIC** | A feature "belongs" to a concept to the degree it reliably CO-ACTIVATES when the concept is grounded-experienced — a statistical/associative criterion (Barsalou's accumulation quote, verified), refined by error-driven weight adjustment over many trials (Rogers & McClelland, verified) | The verb module's own docstring states the assignment PROCESS directly: "Tags assigned by applying the SAME written rubric to each word's actual meaning... decided BEFORE any classification was run" — i.e., a human applying a linguistic taxonomy BY HAND is the metric, not a measurement over any data |

### The two-part gap, named exactly per the task brief

**(a) LEARNED vs SUPPLIED** — is the ASSIGNMENT PROCESS (which word gets which tags) done by
induction from data/grounded experience, or decided once by a human? **Currently: 100% SUPPLIED**,
both modules explicit and honest about this. **Tractability: HIGH, buildable NOW, and now
independently corroborated by the literature's own best induction mechanisms** — Fazly, Alishahi &
Stevenson's real computational system (Section 3) has the EXACT SAME "pre-given meaning-element
vocabulary" shape as this substrate's hand-tagged lexicons, meaning extending an already-supplied
symbolic vocabulary to new words via similarity/statistical induction is a legitimate, literature-
precedented, state-of-the-art-consistent engineering move, not a shortcut. The same-session verb
drill already piloted exactly this (measured, not theorized): a Tier-2 similarity-extension
fallback scored 8/8 and 6/6 on a held-out pilot with real scramble-collapse — a small-scale analog
of Xu & Tenenbaum's Bayesian-taxonomic-prior generalization (verified above). **Routing per the
USER error-flavor rule: missing-LEARNING -> reuse/expand `hdlab/learner` + the already-piloted
similarity-extension mechanism.**

**(b) GROUNDED vs ABSTRACT-SYMBOLIC** — does a feature tag's VECTOR/CONTENT actually derive from
sensorimotor/affective/interoceptive/social experience, or is it an arbitrary opaque label
indistinguishable in construction from any other tag? **Currently: 100% abstract-symbolic**,
confirmed by direct code read. **Tractability: LOW, and this session's lit-scan confirms the field
itself has not solved this either** — no published system was found that induces the feature
ONTOLOGY (not just feature values) from grounded/perceptual data at open-domain scale; even Regier's
grounded spatial-term model and Piantadosi et al.'s grounded number-word model are narrow-domain
existence proofs, not general solutions. This is genuinely, currently, an open research problem —
not merely a build gap unique to this substrate. **Routing per the USER error-flavor rule:
missing-GROUNDING -> the experiential-simulation "6yo grounded foundation" program** (`MEMORY.md`;
`notes/foundational_grounded_knowledge_layer_program_2026-08-03.md`) — the correct, already-
authorized long-term destination.

### Which sub-gap is more load-bearing for open-vocabulary generalization?

For raw COVERAGE, **(a) is the near-term binding constraint** and should close first — cheap,
piloted, and literature-precedented even in its "pre-given vocabulary" limitation. But closing (a)
alone only ever propagates SUPPLIED SYMBOLIC LABELS further. For TRUE open-ended generalization on
abstract/affective concepts specifically (goal/hope/fail/praise, the class this audit was asked to
target), **(b) GROUNDED-vs-ABSTRACT-SYMBOLIC is the deeper ceiling, and this session's verified
lit-scan sharpens rather than softens that conclusion**: the best published induction systems
extend labels, they do not ground them; Desai et al.'s own explicit conclusion is that abstract-
concept grounding requires MULTIPLE cooperating neural systems (interoceptive, mentalizing,
metaphoric-structural, event-simulation) with no unified computational account of how they combine,
even in the pure neuroscience/cognitive-science literature, let alone in a built system.

**One concrete, disk-checkable bridge candidate, honestly capped (not overclaimed), now sharpened
by two newly-verified findings:** Section 2's outcome-valence grounding (dopaminergic RPE) is this
substrate's single strongest existing candidate for closing part of gap (b), and Reber et al.
(2017)'s verified double-dissociation adds a precise mechanistic refinement — a "goal" needs not
just a value signal but a value-to-action-COUPLING signal, meaning the appraisal-simulation's
`pfc_gate_cfrpe_trained_v2` organ (which already couples its RPE to a Go/NoGo action policy, per the
Aug-3 drill) is a CLOSER structural match to what a goal-concept computationally needs than a bare
valence-scalar would be. Bridging that coupled RPE+policy signal into a text verb's `RESULT_VALENCE`
tag is still the same unverified "sim-to-text transfer" step the Aug-3 drill capped at P=0.35 — this
audit does not raise that number, but the newly-verified Reber finding makes the target shape of
the bridge more precise (couple to action-selection, not just to a scalar).

---

## Cheap decisive test

A desk-review test, no GPU, ~2-3 hours, directly discriminating which sub-gap is ALREADY binding
(not just theorized):

1. Draw ~20-30 OOV abstract/affective/social-evaluative words from `data/corpora/mcguffey_graded` +
   `data/corpora/graded_readers_grade1` (same corpus-provenance discipline the verb drill already
   used) that are OOV of BOTH `hdlab/lexical_similarity.py` and `hdlab/verb_lexical_similarity.py`
   — candidates: envy, grateful, ashamed, loyal, betray, shame, pride, mercy, courage, despair
   (verify OOV status against the actual dicts before selecting).
2. For each word, ask: can its TRUE meaning be expressed as a subset/near-subset of tags ALREADY IN
   the existing domain-tag vocabulary (fits by ANALOGY to an existing hand-tagged neighbor,
   consistent with Fazly-et-al-style pre-given-vocabulary extension), or does it require a
   genuinely NEW tag/dimension no existing word has?
3. For words requiring a new tag: is the new tag still expressible within the SAME rubric family
   already used to build the existing lexicons, or does its correct definition presuppose the very
   experiential/affective content it's meant to encode (circular, ungrounded, not resolvable by
   adding another symbolic tag)?
4. **New, literature-informed addition to the test:** for the outcome-valence subset specifically,
   check whether the `pfc_gate_cfrpe_trained_v2` organ's RPE trace (on a matched set of held-out
   appraisal-simulation episodes) correlates with the hand-assigned `RESULT_VALENCE` polarity for
   the corresponding verb — a first, cheap, disk-only check of the Section 4 bridge candidate before
   any real sim-to-text experiment is designed.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered per project convention)

| Prediction | HARD-PASS | HARD-FAIL | MIDDLE-BAND |
|---|---|---|---|
| Most OOV abstract words fit the EXISTING tag ontology by analogy (supports "(a) close first") | >=70% of the sampled OOV set fits an existing domain-tag scheme with a new WORD entry but no new DIMENSION | <40% fit without inventing a new dimension (ontology itself, not just coverage, is already the bottleneck at small scale) | 40-70% |
| New tags needed (if any) stay within the SAME rubric family used to build the existing lexicons | >=80% of new-tag cases are expressible via the same linguistic-taxonomy rubrics (extension, a SUPPLY task) | >=30% of new-tag cases require a tag whose correct definition is circular/presupposes the affective content it encodes (direct evidence gap (b) already binds) | 20-30% |
| The RPE+action-coupling bridge candidate (Section 4, sharpened by Reber et al. 2017) is viable for the outcome-valence tag slice | `pfc_gate_cfrpe_trained_v2`'s RPE trace correlates with hand-assigned `RESULT_VALENCE` polarity on a held-out verb set, without retraining | RPE trace shows no correlation (appraisal-simulation's RPE and the text lexicon's polarity tags measure genuinely different things, not the same signal via two channels) | -- |

**P_deflated:** P(the "(a) close first, (b) is the deeper ceiling" ranking survives the cheap
decisive test above) = 0.60 raw prior (now moderately HIGHER than the initial recalled-only draft's
0.55, because the ranking is now independently corroborated by verified external evidence — Fazly
et al.'s real system sharing gap (a)'s exact shape, and Desai et al.'s explicit multi-system
conclusion sharpening gap (b) — not just this substrate's own docstrings) deflated by the standard
0.20 (mid-band per [[feedback-lit-scan-calibration-penalty]], reflecting that most citations ARE now
freshly verified this session but the RANKING JUDGMENT itself remains this note's own synthesis) ->
**P_deflated = 0.48**, just under the 0.50 novel-synthesis cap. P(the RPE+action-coupling bridge
candidate for outcome-valence tags survives a real test) is carried over from the Aug-3 drill's own
capped estimate, **P=0.35** — this audit sharpens the target shape of that bridge (Reber's
coupling finding) but does not raise the number; sim-to-text transfer remains the unverified step.

---

## Cross-thread synthesis

This audit is the biology-and-mechanism-acquisition companion to two same-session drills that
established the SHAPE of the target feature spaces
(`notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md` for nouns,
`notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md` for verbs) — this note answers
"where do features ORIGINATE and how do they get GROUNDED," which neither of those asked; read
alongside, not instead of, them. It directly extends
`notes/research_drill_biology_led_learning_mechanism_earned_grounding_simulation_appraisal_action_causal_credit_2026-08-03.md`'s
finding that the substrate already owns a genuinely earned, grounded, learned RPE signal
(`pfc_gate_cfrpe_trained_v2`, HARD_PASS) — this audit's Section 2/4 identifies that signal as the
brain-correct grounding substrate for outcome-valence-type abstract concepts, and Reber et al.
(2017)'s newly-verified double-dissociation sharpens exactly WHAT shape that bridge needs (value +
action-coupling, not a bare scalar) — a connection the Aug-3 drill did not draw (it was scoped to
the appraisal-simulation side, not the text-facing lexicon side). This audit formalizes and splits
the "missing-LEARNING follow-up" scope caveat already self-reported in both hdlab modules'
docstrings into the two distinct sub-gaps the task brief asked for, and — new this revision —
independently corroborates that split against real, verified computational-linguistics/cognitive-
science literature (Fazly et al.'s shared limitation; Desai et al.'s explicit multi-system
conclusion), not just this substrate's own honesty-flagged scope notes.

## Substrate-product implications

- **Near-term, cheap, literature-corroborated:** the verb drill's Tier-2 similarity-extension
  mechanism is the correct answer to gap (a), independently supported both by developmental
  literature (Xu & Tenenbaum's size principle) AND by the closest published computational systems
  (Fazly et al.'s pre-given-vocabulary extension) sharing the exact same shape/limitation — should
  ship as already spec'd in that drill's "READY FOR EXP_DEV" section.
- **Do not overclaim closing gap (a) as "solving grounding."** Every word the Tier-2 mechanism
  types is still an abstract symbolic label wearing a plausible-sounding name — extending REACH,
  not depth. State this explicitly in any downstream verdict/cap_map entry, per the "buried win
  gets oversold" failure pattern already diagnosed elsewhere in this substrate's history.
- **Concrete, newly-sharpened finding for the grounded-foundation program:** outcome-valence/goal-
  attainment concepts (fail/succeed/hope) have, per this session's verified lit-scan, the MOST
  direct, well-characterized, already-partially-earned neural grounding mechanism (dopaminergic RPE
  coupled to action selection, per Reber 2017) of any abstract-concept type surveyed — a
  literature-backed argument for sequencing the grounded-foundation program to tackle outcome-
  valence/goal concepts BEFORE more diffuse abstract vocabulary (truth, freedom, justice), which
  per Desai et al.'s own explicit conclusion needs multiple, still-uncombined grounding systems
  even in the pure research literature.
- **Newly-flagged, genuinely important caveat this revision adds:** the field's own best
  computational induction mechanisms (Section 3) have NOT solved gap (b) either — this is not a
  substrate-specific shortfall to feel uniquely behind on, but it does mean no "just adopt paper X's
  method" shortcut exists for grounding; the experiential-simulation program remains the only
  currently-charted path, and should not be deprioritized on the assumption that some existing
  published system already does this.

## Citations (verified count)

**Disk-verified this session (7 artifacts, read directly):** `hdlab/lexical_similarity.py` (full
docstring + tag table); `hdlab/verb_lexical_similarity.py` (full docstring + both tag tables);
`notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md`;
`notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md`;
`notes/research_drill_biology_led_learning_mechanism_earned_grounding_simulation_appraisal_action_causal_credit_2026-08-03.md`;
`notes/PLAN_grounded_semantic_organ_build.md` (existence/mtime checked);
`notes/foundational_grounded_knowledge_layer_program_2026-08-03.md` (existence/mtime checked).

**External literature — 3 parallel Sonnet lit-scan sub-agents dispatched and returned this session
(generic-terms-only WebSearch/WebFetch per query-privacy discipline). Confidence flags are each
sub-agent's own self-report, carried through unchanged.**

*Directly fetched / HIGH confidence (11):* Binder, Conant, Humphries, Fernandino, Simons, Aguilar &
Desai (2016), *Cognitive Neuropsychology* — componential feature model (PubMed abstract); Tong,
Binder, Humphries, Mazurchuk, Conant & Fernandino (2022), *Scientific Data* — feature-annotation
dataset (full fetch); Barsalou & Wiemer-Hastings (2005), "Situating abstract concepts" (chapter PDF
fetch); Zdrazilova et al., "Communicating abstract meaning" (PMC6015825, full fetch); Kousta,
Vigliocco, Vinson, Andrews & Del Campo (2011), *JEP:General* — Affective Embodiment Hypothesis
(PubMed abstract); Fogassi, Ferrari, Gesierich, Rozzi, Chersi & Rizzolatti (2005), *Science* —
parietal goal-of-action-chain coding (PDF fetch); Reber, Feinstein, O'Doherty, Liljeholm, Adolphs &
Tranel (2017), *Brain* — vmPFC value/action-coupling double dissociation (full fetch); Lakoff &
Johnson metaphor-circuitry review (PMC4267278, full fetch); Vigliocco, Vinson, Lewis & Garrett
(2004), *Cognitive Psychology* — FUSS model (PubMed abstract); Yu & Smith (2007), *Psychological
Science* — cross-situational statistical learning (full fetch); Markson & Bloom (1997), *Nature* —
domain-general fast mapping (well-triangulated, title-verified correcting a common mis-citation).

*Verified via search / secondary-source triangulation, not full-text fetched (18):* Fernandino,
Tong, Conant, Humphries & Binder (2022), *J Neuroscience* — multimodal-beats-unimodal neural
prediction; Rogers, Lambon Ralph, Garrard, Bozeat, McClelland, Hodges & Patterson (2004),
*Psychological Review* — hub-and-spoke PDP; McClelland, McNaughton & O'Reilly (1995), *Psychological
Review* — Complementary Learning Systems; Landau, Smith & Jones (1988) + Colunga & Smith (2005) —
shape bias, statistically emergent; Vinson & Vigliocco (2008), *Behavior Research Methods* — verb
feature norms (paywalled, LOW-MEDIUM, independently corroborating the sibling verb drill's own
identical flag); Desai, Reilly & van Dam (2018), *Phil Trans R Soc B* — multifaceted abstract brain;
Carey & Bartlett (1978) — fast mapping origin; Siskind (1996), *Cognition* — cross-situational
computational algorithm; Frank, Goodman & Tenenbaum (2009), *Psychological Science* — Bayesian
cross-situational model; Xu & Tenenbaum (2007), *Psychological Review* — size principle (math
independently corroborated via PMC3310181); Markman (1990), *Cognitive Science* — mutual
exclusivity; Naigles (1990), *Cognitive Development* — syntactic frame flips verb interpretation;
Landau & Gleitman (1985) — blind children, syntactic bootstrapping origin; Gleitman (1990),
*Language Acquisition*; Fazly, Alishahi & Stevenson (2010), *Cognitive Science* — real induction
mechanism sharing this substrate's pre-given-vocabulary limitation; Alishahi & Stevenson (2008),
*Cognitive Science* — verb argument-structure Bayesian induction; Piantadosi, Tenenbaum & Goodman
(2012), *Cognition* — grounded-primitive compositional induction (number words); Abend, Kwiatkowski,
Smith, Goldwater & Steedman (2017), *Cognition* — corpus-scale joint syntax-semantics induction.

*Narrower/exploratory, LOW confidence (title/abstract-only or 403-blocked, 6):* two 2024/2026
Desai-lineage mentalizing-network papers (titles confirmed, full text blocked); interoception
special issue, *Phil Trans R Soc B* 2018 (403 blocked); Regier (1996), *The Human Semantic
Potential* — grounded spatial-term connectionist model (not directly fetched); Damasio somatic-
marker hypothesis (general decision-theory account, secondary sources only); Paivio (2013) dual-
coding critique of Kousta et al. (search-level, flags the affective-embodiment debate as contested).

**Total citation count this note: 7 disk-verified + 35 external (11 directly fetched, 18
search-verified secondary-source, 6 narrower-relevance/title-only) = 42, with the field's own
computational-mechanism gap (Section 3's final paragraph) explicitly flagged as a genuine, current
open problem rather than papered over.**
