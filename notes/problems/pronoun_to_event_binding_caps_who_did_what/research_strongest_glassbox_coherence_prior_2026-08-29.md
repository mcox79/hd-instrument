# Research drill: strongest glass-box coherence PRIOR for the anti-typical pronoun->event residual

Date: 2026-08-29
Scope: SOLVER-side literature drill. No experiments dispatched. No plan/status/cap_map/hdlab edits.
Question: is there ANY brain-faithful coherence-PRIOR mechanism that is (a) glass-box, no external
LLM, no open-world KB, and (b) NOT already refuted as "typicality" by the sibling problem?

Deflation applied per lit-scan calibration discipline: P estimates deflated 0.15-0.25; novel-synthesis
recoverable-fraction estimates capped and stated as deflated ranges, not point hopes.

--------------------------------------------------------------------------------------------------
FRAME (Kehler & Rohde 2013)
--------------------------------------------------------------------------------------------------
P(referent | pronoun) proportional to P(pronoun | referent) [LIKELIHOOD = production / grammatical
prominence: subjecthood, recency, Cb, first-mention] x P(referent) [PRIOR = which entity gets
re-mentioned next, driven by semantics / coherence].

The structural binder in hand already occupies the LIKELIHOOD term (Centering cues). The residual
lives in the PRIOR. The sibling refuted TWO specific PRIOR realizations on this exact data:
  - a general coherence / next-mention prior (did NOT beat its info-free twin on the residual), and
  - a WordNet+ConceptNet KB (dead despite 87% coverage),
because BOTH encode ENTITY-level typicality and the residual is anti-typical (19% of gold antecedents
favored by NO structural cue; cue-conflict core where recency/subjecthood/topicality disagree).

The decisive move below: find a PRIOR realization that is (i) lexicalized on the VERB / EVENT, not on
entity world-knowledge, and (ii) mechanistically specific in a way the general next-mention prior was
not -- so it is genuinely outside the sibling's refutation envelope.

--------------------------------------------------------------------------------------------------
Q1. IMPLICIT CAUSALITY (IC) AS A LEXICON, NOT A KB
--------------------------------------------------------------------------------------------------
MECHANISM. IC is a per-verb bias toward re-mentioning one argument as the CAUSE of the event. In a
causal continuation ("Sally frightened Mary because she..."), the verb alone shifts the preferred
antecedent: stimulus-experiencer verbs (frighten, surprise) are subject-biased; experiencer-stimulus
verbs (fear, love) are object-biased. Critically, this bias is marked in the verb's LEXICAL ENTRY --
Hartshorne & Snedeker (2013) state it is NOT reliably derivable from thematic roles or semantic class
("each verb is marked in its lexical [entry]"). So the admissible signal is a static VERB->scalar
TABLE, i.e. a lexicon, not a reasoning KB.

KEY STUDIES / EFFECT SIZES.
- Ferstl, Garnham & Manouilidou (2011): norms for 305 English verbs; bias score -100 (all NP2) to
  +100 (all NP1), from ~96-respondent sentence completion. This IS the ready-made lexicon.
- Hartshorne & Snedeker (2013), 328 verbs: grand-mean object bias ~58.4% (their conservative
  "chance"). Per-verb biases are strong and reliable at the extremes -- class 31.1 (frighten/surprise)
  = 35.7% object bias (i.e. strong SUBJECT bias); class 31.2 (fear/love) = 81.5% object bias.
  IMPORTANT CEILING ON DERIVATION: predicting IC direction FROM semantic class is weak -- VerbNet
  correctly classified only 56% of verbs; coarse taxonomies 28-31%; a fine-grained 6-class model only
  R2=0.2 / 60% direction-correct. => Do NOT derive IC from class; use the MEASURED per-verb norm.
- Rudolph & Forsterling (1997) meta-analysis: IC replicable across 4 languages; per-verb data for
  ~256 verbs; biases stable across studies and correlate with Brown & Fish (1983) causal attribution
  -- i.e. IC is a robust, cross-study, lexical constant, not a lab artifact.
- IC is "one factor... by no means the only" (Ferstl 2011) -- expect a partial signal, not a solver.

IS IT DISTINCT FROM THE REFUTED TYPICALITY KB? YES, at the level that matters. WordNet/ConceptNet
encode ENTITY typicality (is a mayor a typical permit-granter). IC encodes VERB-argument prominence
(does "deny" throw causal weight on NP1 or NP2), independent of who the entities are. They are
orthogonal dimensions; a same-gender cue-conflict case that entity-typicality cannot split may still
be split by the verb's IC bias. Caveat: IC is itself a form of statistical regularity ("typical
explanation direction for this verb") -- but it is EVENT-STRUCTURE typicality, not entity-world
typicality, so it is not the thing the sibling killed.

GLASS-BOX IMPLEMENTABLE? YES. Static float table keyed on lemma (spaCy lemmatizer, already available
in the pipeline); ~305-328 entries; O(1) lookup; fully inspectable. No LLM, no open world.

--------------------------------------------------------------------------------------------------
Q2. COHERENCE-RELATION / CONNECTIVE CUES (and the CONSEQUENTIALITY companion)
--------------------------------------------------------------------------------------------------
MECHANISM. IC is NOT a free-floating verb constant -- it is GATED by the coherence relation, which is
often marked on the surface by the connective. "because" -> Explanation relation -> IC (cause) bias
fires. "and so" / "so" -> Result relation -> IMPLICIT CONSEQUENTIALITY (I-Cons) bias fires, which can
point to a DIFFERENT argument than IC. "and then" / bare "and" -> Occasion/Contiguity -> weak, defer
to parallelism/likelihood. This is decisive for a reading system: the RIGHT lexicon to consult
depends on the local connective, and the connective is readable from surface text with zero world
knowledge.

KEY STUDIES.
- Kehler, Kertz, Rohde & Elman (2008), "Coherence and Coreference Revisited": connectives carry their
  own focusing properties; "and similarly" (Parallel) vs "and so" (Result) shift interpretation and
  reading times; pronoun coreference is a by-product of establishing the coherence relation. This is
  the paper that separates connective-driven PRIOR from grammatical LIKELIHOOD.
- Rohde & Horton (2014), anticipatory eye-movements: readers project the upcoming coherence relation
  IMMEDIATELY at the offset of an IC verb, BEFORE the pronoun -- confirms IC+relation is a genuine
  predictive PRIOR, not a post-hoc rationalization.
- Crinean & Garnham (2006) + the 305-verb IMPLICIT CONSEQUENTIALITY corpus (companion to Ferstl 2011):
  I-Cons is a SEPARATE per-verb bias for who gets re-mentioned in the CONSEQUENCE of an event
  ("John liked Mary and so she..."). Two-mechanism account: IC = empty argument slots in verb
  semantics; I-Cons = Contiguity Principle (discourse-structural). For NARRATIVE next-mention (events
  followed by their consequences, which is most of LitBank narration) I-Cons is arguably MORE relevant
  than IC, and a matching static 305-verb lexicon already exists.

IS THIS A SEPARABLE GLASS-BOX SIGNAL? YES. The connective is a closed-class surface token; the
relation label is a deterministic map from that token; the per-verb IC/I-Cons value is a table
lookup. No world knowledge enters. Separable from the sibling's general next-mention prior BECAUSE it
conditions the prior JOINTLY on (verb identity) x (local connective) -- a specific factorization a
generic P(referent) estimator does not have.

GLASS-BOX IMPLEMENTABLE? YES. Connective -> relation lookup table (~10 tokens) x {Ferstl IC norms,
consequentiality norms}. Two static tables + one gate rule.

--------------------------------------------------------------------------------------------------
Q3. PARALLELISM / GRAMMATICAL-ROLE PARALLELISM
--------------------------------------------------------------------------------------------------
MECHANISM. In conjoined / structurally parallel clauses, a pronoun prefers the antecedent in the SAME
grammatical role (subject->subject, object->object), independent of information status / word order.

KEY STUDIES / EFFECT SIZES.
- Smyth (1994); Chambers & Smyth (1998): parallelism is a "very strong perceptual strategy" for both
  subject-subject and object-object dependencies.
- Kehler et al. (2008): under a Parallel relation, assignment is overwhelming -- 100% of subject
  pronouns to the preceding subject, 88.12% of nonsubject pronouns to the preceding nonsubject;
  parallel-assignment rates 64-90% across conditions. But this effect is CONDITIONAL on the Parallel
  coherence relation being operative (again connective-gated: "and similarly").
- Stevenson, Nelson & Stenning (1995): parallelism interacts with (does not override) thematic focus.

IS THERE A STRONGER VERSION THAN WHAT IS IN HAND? The binder already has a parallelism cue. The
literature's lift is the GATING insight (Kehler 2008): parallelism should be applied at FULL strength
ONLY when the coherence relation is Parallel (surface-cued), and DISCOUNTED otherwise. Ungated
parallelism (blanket "prefer same role") is the weaker version; relation-gated parallelism is the
stronger, and it is what the current cue is probably missing. Low marginal yield vs Q1/Q2 but free.

GLASS-BOX IMPLEMENTABLE? YES, already partly in hand. The upgrade is a gate, not new data.

--------------------------------------------------------------------------------------------------
Q4. THE DECISIVE ONE: is the anti-typical residual world-knowledge-bound?
--------------------------------------------------------------------------------------------------
MECHANISM OF THE HARD CASES. Hobbs (1979): pronoun interpretation is predominantly driven by
semantics, world knowledge, and inference in service of establishing discourse coherence -- the
pronoun is resolved as a by-product of the inference that makes the two clauses cohere. Winograd
Schema Challenge (Levesque 2011; Kocijan et al. 2023 "The Defeat of..."): a curated set of pronoun
cases deliberately built to be "Google-proof" -- structural and lexical-cooccurrence cues are
NEUTRALIZED by construction, and only relevant background knowledge flips the answer. This is exactly
the shape of the sibling's residual: cue-conflict + no-structural-cue + anti-typical.

IMPLICATION. A large fraction of the anti-typical residual is, by its own construction, precisely the
slice that requires an inference over world knowledge to resolve. NO compact lexicon / connective /
parallelism signal can touch that slice -- it is the genuinely irreducible glass-box core. Honest
statement: the sibling's KB death is consistent with this; a KB fails not because KBs are useless but
because the residual's coherence turns on SITUATION-SPECIFIC inference (this permit, this denial),
not on retrievable type-facts.

BUT (the non-defeatist half, per "don't generalize a narrow failure to impossible"): "world-knowledge
-bound" is NOT coextensive with "residual". A MEASURABLE sub-slice of the residual is resolvable by
verb-argument structure + connective WITHOUT world knowledge -- namely the cases where the cue
conflict is between grammatical prominence (likelihood term) and event-causal/consequential prominence
(the IC/I-Cons prior). Those look "anti-typical" to a structural binder precisely because the binder
lacks the IC/I-Cons dimension; they are not world-knowledge-hard, they are verb-lexicon-hard. That
sub-slice is what the untested mechanism can recover.

--------------------------------------------------------------------------------------------------
BOTTOM LINE
--------------------------------------------------------------------------------------------------
SINGLE STRONGEST GLASS-BOX MECHANISM WORTH TESTING:
  A per-verb IMPLICIT-CAUSALITY + IMPLICIT-CONSEQUENTIALITY bias LEXICON (Ferstl et al. 2011 causality
  norms, 305 verbs, + the companion 305-verb consequentiality corpus), CONNECTIVE-GATED (because ->
  IC; so/and-so/result -> I-Cons; and-similarly -> relation-gated parallelism; bare and/then ->
  defer to likelihood). Two static float tables + a ~10-token connective->relation gate. glass-box,
  O(1) lookup, no LLM, no open-world KB.

WHY IT IS OUTSIDE THE SIBLING'S REFUTATION:
  - It is VERB/EVENT-lexicalized, not ENTITY-world-typicality -> orthogonal to the WordNet/ConceptNet
    KB that died.
  - It conditions the prior JOINTLY on (verb) x (connective) -> a specific factorization the sibling's
    GENERAL next-mention prior did not have. The refutation covers "a generic coherence prior"; it
    does NOT cover this verb-lexicon-x-connective-gate. => genuinely-stronger UNTESTED version exists.

DEFLATED RECOVERABLE FRACTION (honest, coverage-bound):
  The ceiling is set by COVERAGE, not per-item accuracy. IC/I-Cons only fires when a residual pronoun
  sits in a diagnostic config: a two-human-argument transitive IC/I-Cons verb with a same-gender
  competitor AND a diagnostic connective / adjacency. In free LitBank narrative that config is a
  MINORITY of residual pronouns -- deflated estimate ~10-20% of the residual is in-config. Of those
  in-config cases, IC/I-Cons picks the correct direction ~60-75% (vs ~50% for a coin flip on a
  cue-conflict case). Net deflated recoverable ~= 0.15 coverage x 0.20 accuracy-gain-over-chance
  ~= 2-5 percentage points of the residual. Small, real, and separable. NOT a residual-solver.
  RISK of this recommendation: if the in-config coverage on the actual residual is <8%, the ceiling
  collapses to ~1-2 points and it is not worth wiring -- so the FIRST step is a pure COUNTING probe
  (how many residual items are in an IC/I-Cons-diagnostic config), NOT a model. Do not build before
  that count clears ~10%.

GENUINELY IRREDUCIBLE GLASS-BOX SLICE:
  The remainder of the anti-typical residual (the majority) is Hobbs/Winograd world-knowledge-bound by
  construction: its coherence turns on situation-specific inference, not on any static lexicon,
  connective, parallelism, or type-fact KB. No no-external-LLM, no-open-world-KB mechanism recovers
  it. That is the honest structural wall, and it is DIFFERENT from "we picked a bad prior" -- it is
  "this slice requires an inference engine over world knowledge that the glass-box, no-LLM constraint
  forbids." State it as a constraint-imposed ceiling, not a capability ceiling.

DECISION FOR THE SOLVER:
  Worth ONE cheap counting probe (config coverage on the residual) before any build. If coverage
  >~10%, the connective-gated IC+I-Cons lexicon is the strongest untested glass-box prior and is
  outside the sibling's refutation. If coverage <~8%, declare the residual constraint-bound
  (world-knowledge, no-LLM forbidden) and stop drilling the prior.

--------------------------------------------------------------------------------------------------
TLDR (plain language)
--------------------------------------------------------------------------------------------------
The hard leftover pronoun cases are the ones where the usual "who is grammatically prominent" clues
disagree or point the wrong way. The one honest new idea that is NOT the type-of-thing that already
failed: some verbs quietly tilt toward "the do-er" and others toward "the done-to", and the little
word joining the two clauses ("because" vs "so") tells you which tilt applies. This is a small fixed
dictionary of verbs (about 300, already published, twice -- one list for cause, one for consequence),
no outside AI and no world-fact database. It is different from the fact-database that already flopped
because it is about the VERB, not about the people. But it only helps on the minority of leftover
cases that actually contain such a verb plus such a joining word -- best honest guess about 1 in 5 of
the leftovers, and it gets maybe 2 out of 3 of those right, so it recovers only a few points overall.
The rest of the hard cases genuinely need real-world reasoning that our no-outside-AI rule forbids --
that is a rule we chose, not a wall in the brain.

QUESTIONS: none.

NEXT STEPS (for the SOLVER; not executed here):
  1. COUNTING PROBE ONLY: on the residual items, count how many contain a Ferstl/consequentiality-
     listed transitive verb with two same-gender human arguments AND a diagnostic connective/adjacency.
     This single number decides go/no-go. No model.
  2. If coverage clears ~10%: obtain the two published norm tables (Ferstl et al. 2011 causality;
     the 305-verb consequentiality companion) as static CSV lexicons.
  3. Design the can-fail test as connective-gated-IC-prior vs its info-free twin (shuffled verb->bias
     table), scored ONLY on the in-config residual slice, with the structural binder as the real
     baseline -- so any lift is attributable to the verb dimension, not to re-touching easy cases.

--------------------------------------------------------------------------------------------------
SOURCES
--------------------------------------------------------------------------------------------------
- Ferstl, Garnham & Manouilidou (2011). Implicit causality bias in English: a corpus of 300 verbs.
  Behavior Research Methods. https://link.springer.com/article/10.3758/s13428-010-0023-2
- Implicit consequentiality bias in English: A corpus of 300+ verbs. Behavior Research Methods.
  https://link.springer.com/article/10.3758/s13428-020-01507-z (PMC: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8367889/)
- Hartshorne & Snedeker (2013). Verb argument structure predicts implicit causality: the advantages of
  finer-grained semantics. Lang. & Cognitive Processes 28(10):1474-1508.
  https://dash.harvard.edu/entities/publication/73120378-e20e-6bd4-e053-0100007fdf3b
- Kehler, Kertz, Rohde & Elman (2008). Coherence and Coreference Revisited. J. Semantics 25(1):1.
  https://academic.oup.com/jos/article-abstract/25/1/1/1616215
- Kehler & Rohde (2013). A probabilistic reconciliation of coherence-driven and centering-driven
  theories of pronoun interpretation. Theoretical Linguistics.
  https://www.researchgate.net/publication/272575348
- Rohde & Horton (2014). Anticipatory looks reveal expectations about discourse relations. Cognition.
  https://www.sciencedirect.com/science/article/abs/pii/S0010027714001693
- Crinean & Garnham (2006). Implicit causality, implicit consequentiality and semantic roles.
  Language and Cognitive Processes.
- Smyth (1994); Chambers & Smyth (1998) -- grammatical-role parallelism in pronoun resolution.
- Rudolph & Forsterling (1997). The psychological causality implicit in verbs: A review.
  https://www.researchgate.net/publication/236876251
- Hobbs (1979). Coherence and coreference. Cognitive Science.
- Levesque, Davis & Morgenstern (2011) The Winograd Schema Challenge; Kocijan et al. (2023) The defeat
  of the Winograd Schema Challenge. Artificial Intelligence. https://dl.acm.org/doi/10.1016/j.artint.2023.103971
