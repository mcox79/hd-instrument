# Research: brain vs our coref/experiencer-binding mechanism, itemized diff

date: 2026-09-04
scope: notes/problems/the_situation_model_has_no_affect_emotion_dimension/
author: research sub-agent (direct web search, no sub-agent fan-out, per task instruction)
calibration: lit-scan penalty applied per [[feedback-lit-scan-calibration-penalty]] -- established-literature
items below are reported at their literature-convergence confidence, then DEFLATED 0.15-0.25 for the
inferential step "this general psycholinguistic mechanism specifically explains our system's failure
mode." The single-most-important-difference synthesis in section 3 is NOVEL SYNTHESIS on my part
(connecting the on-disk trace to the definite-description literature) and is capped at P=0.50, further
deflated to P=0.40.
field-advisor note: `tools/orchestrator/research_field_advisor.py` was run per protocol; its output
(spin-glass/thermodynamics/free-probability field-adjacency scores) is from the UNRELATED substrate-physics
research thread and has no bearing on this psycholinguistics/coreference question. Not used below.

======================================================================
HEADLINE
======================================================================

Two things are true at once. (1) Every item the task asked about is a real, well-cited, precise
mechanism-diff between our post-hoc ranked-list resolver and the brain's cue-based, incremental,
decaying, graded-agreement, verb-predictive retrieval system (items 1-6, 8 below) -- and each predicts a
real failure mode. (2) But an on-disk trace already run in THIS SAME problem folder
(`signal_loss_chain_analysis_2026-09-04.md`, section "TRACING THE COREF LOSS") shows that items 1-6 are
NOT where the 36%-vs-gold gap is actually coming from: of 637 scorable experiencer mentions, only
16.5% are named characters at all, genuine named-pronoun coref errors are ~61/637 (~9.6% of the loss),
and the other ~90% of the loss is common-noun-headed referents ("the man," "the child," "the woman" --
83.5% of gold experiencers) that our proper-name-centric coref organ cannot cluster/re-identify the way
gold does. This is why THREE brain-inspired PRONOUN-resolution fixes (global-protagonist fallback,
Centering resolver, fallback-only) all failed near-identically (-0.001, -0.051, -0.003): they were all
tuning the ranking formula for a candidate pool that was only ever going to matter for ~10% of the
mentions. Item 7 (referent segmentation) is therefore promoted from "one of eight" to THE dominant
mechanism-diff, and the brain-mechanism that explains it is NOT Lewis-Vasishth cue-based retrieval
(that literature is about resolving PRONOUNS to antecedents already in the discourse model) -- it is
the DEFINITE-DESCRIPTION / BRIDGING-REFERENCE literature (Clark & Haviland 1977; Poesio & Vieira 1998;
Gundel, Hedberg & Zacharski 1993; Ariel 1990), which is about how a common-noun NP gets matched to, or
newly added as, a discourse referent using DESCRIPTIVE CONTENT and associative inference, not
grammatical agreement or recency ranking. Section 3 gives the single most important difference.

======================================================================
1. ITEMIZED MECHANISM-DIFF (as requested, items 1-8)
======================================================================

### Item 1 -- CUE-BASED RETRIEVAL vs hard-filter ranked list

OURS: a feed-forward one-pass ranker over a fixed candidate list; scores = recency distance + a
maintained frequency/salience overlay; gender/number applied as a HARD FILTER (non-matching candidates
are removed from the pool, not down-weighted).

BRAIN: content-addressable, direct-access cue-based retrieval (Lewis & Vasishth 2005, "An
Activation-Based Model of Sentence Processing as Skilled Memory Retrieval," Cognitive Science 29(3):
375-419, realized in ACT-R; McElree 2000, "Sentence comprehension is mediated by content-addressable
memory structures," J. Psycholinguistic Research 29(2):111-123; McElree, Foraker & Dyer 2003, "Memory
structures that subserve sentence comprehension," J. Memory and Language 48:67-91). At the retrieval
site (the pronoun), a probe carrying a bundle of CUES (gender, number, animacy, thematic-role fit,
grammatical position) is matched IN PARALLEL against every chunk in declarative memory; retrieval speed
is roughly constant regardless of list length or distance (direct access, not a scan), while ACCURACY
degrades with the number/similarity of competitors (this is the empirical signature that rules out our
kind of serial/ranked search: search predicts distance/list-length effects on latency, direct-access
retrieval does not, and the human data show the latter -- Foraker & McElree 2011 sluicing studies).

PRECISE DIFFERENCE: (a) hard filter vs graded weighted match -- ours permanently excludes anything
outside the agreement filter; the brain's retrieval strength is a SUM/product over graded cue-matches,
so a candidate can still win despite a partial mismatch if other cues are strong (this is what produces
attraction errors, item 4). (b) Ours computes salience as a GLOBAL, cumulative, non-decaying frequency
count over the whole document/window; the brain's cue-match strength for a given candidate is that
candidate's OWN current activation trace (recency-weighted reinforcement, item 3), which is not the
same quantity as "how many times has this character been mentioned overall."
PREDICTED FAILURE: mis-ranking when a formerly-frequent character has gone STALE (should have decayed,
but our undecayed frequency overlay keeps it "salient") competes with a just-introduced or
just-reactivated character of the same gender -- a scene-transition/topic-shift failure mode.
RELEVANCE GIVEN THE TRACE (section 3): this failure mode can only occur on the ~16.5% of experiencers
that are NAMED (pronoun-to-named-antecedent competition needs >=2 named same-gender candidates); the
trace found only 29 wrong-name errors involving a named pronoun bound to the wrong NAMED character, so
this mechanism, however real, is capped at a small slice of the total loss.

### Item 2 -- INCREMENTALITY & PREDICTION vs post-hoc one-pass

OURS: resolves after the mention list exists (post-hoc), does not integrate forward-predictive
information from the clause the pronoun sits in.

BRAIN: resolves the pronoun THE MOMENT it is read, using predictive context generated before the
anaphor arrives. Altmann & Kamide 1999 ("Incremental interpretation at verbs: restricting the domain of
subsequent reference," Cognition 73:247-264) show listeners narrow the referential domain from verb
selectional restrictions before the argument is even uttered (anticipatory eye movements to "the cake"
right after hearing "eat," before "cake" is spoken). Nieuwland & Van Berkum (2006, "Individual
differences and contextual bias in pronoun resolution: Evidence from ERPs," Brain Research 1118:155-167;
also "When peanuts fall in love: N400 evidence for the power of discourse," J. Cognitive Neuroscience)
show readers pre-activate gender features of an expected referent, producing an N400 mismatch effect if
the pronoun's actual gender conflicts with the pre-activated expectation. Levy 2008 ("Expectation-based
syntactic comprehension," Cognition 106:1126-1177) formalizes processing cost as inversely proportional
to the prior probability of the incoming material -- i.e. the brain has a probability distribution over
likely referents BEFORE the pronoun, and resolution at the pronoun is a rapid update/confirmation, not a
from-scratch search.
PRECISE DIFFERENCE: our system never consults clause-internal predictive structure (e.g. the current
verb's argument-structure/experiencer-linking fact -- see the companion note
research_experiencer_psych_verb_brain_mechanism_2026-09-04.md, which shows this fact is
PINNED-BY-EVIDENCE and per-verb deterministic) when combining candidate scores; it only uses retrospective
history features.
PREDICTED FAILURE: mis-resolution specifically at psych-verb clauses ("she was afraid," "it frightened
her") where the verb's OWN argument structure already fixes which grammatical position is the
Experiencer, independent of any candidate-ranking -- our system is not using the single strongest,
cheapest cue for exactly the sentence types this problem is about.

### Item 3 -- ACTIVATION DECAY & REACTIVATION vs fixed-window/cumulative recency

OURS: recency likely a simple distance measure combined with a non-decaying cumulative-frequency
salience overlay.

BRAIN: ACT-R base-level activation (Anderson & Schooler 1991, "Reflections of the environment in
memory," Psychological Science 2(6):396-408) follows a power-law: B_i = ln(sum_j t_j^-d) over the times
t_j since each PAST mention of item i (d ~ 0.5). Recency is EMERGENT from this equation, not a designed
feature: a character mentioned 3x recently has higher summed activation than one mentioned once at equal
recency (accumulated reactivation), while a character not mentioned for many sentences decays toward
zero regardless of how many times it was mentioned earlier in the document. This combines with fan
effects (Anderson 1974: many competing chunks sharing a cue slow/weaken each one's retrieval).
PRECISE DIFFERENCE: structurally similar in spirit (recency term + frequency term) but different in
FORM and in COMBINATION: the brain's decay is a single continuous equation applied uniformly to every
candidate and combined MULTIPLICATIVELY/additively with cue-match strength in one joint retrieval
score; ours is almost certainly separate heuristic terms (recency distance, frequency count, agreement
filter) bolted together without a principled joint function.
PREDICTED FAILURE: our system over-favors a globally-frequent protagonist over a just-reactivated minor
character after a topic shift -- this is EXACTLY the reported failure of the "global-protagonist
salience fallback" fix (F1 recovery -0.001): a frequency-only heuristic with no decay is precisely what
a non-decaying "maintained-salience overlay" produces, and the brain's mechanism (power-law decay,
recency emergent not primary) predicts that fix would wash out, which is what was measured.

### Item 4 -- AGREEMENT AS A GRADED CUE vs a hard filter

OURS: gender/number/animacy mismatch removes a candidate from consideration entirely.

BRAIN: agreement functions as a graded, WEIGHTED retrieval cue, not a binary gate -- demonstrated
definitively by agreement-attraction / "illusion of grammaticality" effects (Wagers, Lau & Phillips 2009,
"Agreement attraction in comprehension: Representations and processes," J. Memory and Language 61(2):
206-237): "The key to the cabinets were rusty" is often judged acceptable because "cabinets" (plural)
intrudes as a partial-match distractor, showing the retrieval computes a parallel feature-match score in
which a partial match still contributes non-zero retrieval strength and can dominate when the correct
target's other cues are weak. The grammaticality ASYMMETRY (the illusion is much stronger in the
ungrammatical direction) further shows agreement checking is fallible, probabilistic evidence
combination, not deterministic gatekeeping.
PRECISE DIFFERENCE: a hard filter cannot even reproduce the human ERROR pattern, but more importantly for
us it fails in the OPPOSITE direction from a human: when our own upstream gender/number tagging of the
TRUE antecedent is wrong or coarse (mis-tagged span, epicene name, group noun, singular-they, free
indirect discourse), the hard filter PERMANENTLY, UNRECOVERABLY excludes the correct antecedent, with
zero chance of recovery via any other cue -- whereas the brain's graded system would still retrieve it
at reduced (not zero) strength if other cues (recency, subjecthood, thematic fit) compensate.
PREDICTED FAILURE: total, uncorrectable misses (not merely wrong-ranked) whenever upstream gender/number
attribution is wrong -- plausible for common-noun-headed entities ("the child," "the parent," group
nouns) whose gender/number is often genuinely ambiguous or context-dependent. This item is the ONE
pronoun-mechanics item that plausibly reaches INTO the common-noun majority (item 7's territory),
because gender/number mis-tagging is more common exactly on descriptive, non-named NPs.

### Item 5 -- DISCOURSE FOCUS/CENTERING as emergent attention vs hand-coded frequency rank

OURS: a "maintained-salience/frequency overlay" -- a hand-coded mention counter used as a ranking
feature (and, per the task's context, a dedicated recency+subjecthood+gender "Centering resolver" was
already tried as a full replacement and FAILED WORSE than the ranker, -0.051).

BRAIN: Centering (Grosz, Joshi & Weinstein 1995, "Centering: A framework for modeling the local
coherence of discourse," Computational Linguistics 21(2):203-225; empirically validated by Gordon, Grosz
& Gilliom 1993, "Pronouns, Names, and the Centering of Attention in Discourse," Cognitive Science 17(3):
311-347) treats the "center of attention" as an EMERGENT property of a continuously-updated attentional
state, not a raw mention-frequency count. Gordon et al.'s key finding is the REPEATED-NAME PENALTY: using
a full name (rather than a pronoun) to refer to the entity that IS the current center of attention causes
a measurable READING-TIME COST -- direct behavioral proof that "in focus" status is graded, continuously
updated by grammatical-role transitions (subject-subject continuation is cheapest), and used
predictively by the parser, not computed by tallying mentions after the fact.
PRECISE DIFFERENCE: "subjecthood" and "recency" are not, in the human data, independent hand-added
ranking features -- they are STATISTICAL SIGNATURES that emerge from the SAME activation/decay/cue-
retrieval process (items 1 and 3) operating together with the cross-linguistic fact that subjects are
more likely to be pronominalized and re-mentioned. Building a "Centering resolver" as a separate additive
formula (recency + subjecthood + gender, scored independently and combined) is exactly NOT what Centering
is: it reproduces the surface correlates without the underlying generative process, so it just adds a
FOURTH rigid heuristic that can conflict with the other three in ways the brain's single joint-activation
equation would resolve gracefully.
PREDICTED FAILURE: this literature directly predicts what was measured -- a hand-coded Centering-style
formula, bolted onto the same one-pass hard-filter architecture, does not help and can actively hurt
(-0.051), because it is optimizing the SURFACE FEATURES of Centering without its GENERATIVE MECHANISM
(incremental, decaying, graded-cue retrieval). This is the clearest evidence in the whole investigation
that the problem is architectural (item 1's paradigm), not a matter of which features are in the ranking
formula.

### Item 6 -- IMPLICIT CAUSALITY as an online verb-generated expectation (currently absent)

OURS: no implicit-causality feature.

BRAIN: implicit-causality (IC) verbs bias pronoun-antecedent assignment by lexical class (Garvey &
Caramazza 1974, "Implicit causality in verbs," Linguistic Inquiry 5:459-464, and "Factors influencing
assignment of pronoun antecedents," Cognition 3:227-243): NP1-biasing (stimulus-subject) verbs like
"frighten," "amaze," "anger" push a following "because"-pronoun toward NP1; NP2-biasing (experiencer-
subject) verbs like "admire," "fear," "envy" push toward NP2. Ferstl, Garnham & Manouilidou (2011,
"Implicit causality bias in English: a corpus of 300 verbs," Behavior Research Methods 43(1):124-135)
provide norms for 305 verbs (largely overlapping the psych-verb classes already in the companion note's
lexicon). Koornneef & Van Berkum (2006, "On the use of verb-based implicit causality in sentence
comprehension: Evidence from self-paced reading and eye tracking," J. Memory and Language 54(4):445-465)
show via self-paced reading AND eye-tracking that the IC bias operates IMMEDIATELY/online: reading
slows AT THE PRONOUN ITSELF when its gender conflicts with the IC-predicted referent, before any
subsequent disambiguating content is read -- i.e. IC bias is a real-time predictive retrieval cue, not a
post-hoc plausibility check.
PRECISE DIFFERENCE: our resolver is blind to exactly the cue the brain uses first and fastest for
psych-verb constructions -- the canonical sentence types this whole problem is about ("she was afraid,"
"it frightened her") ARE implicit-causality-bearing psych-verb constructions, so the verb itself already
constrains which theta-role/clause-position is the Experiencer, independent of any anaphoric-history
ranking.
PREDICTED FAILURE: mis-resolution on multi-character sentences with an IC-biased verb and a subsequent
pronoun/because-clause, where the brain resolves immediately from verb semantics and our system falls
back to recency/salience and gets it wrong whenever the more-recent/salient character is not the
IC-favored one. NOTE per the trace (section 3): IC bias helps disambiguate WHICH of several NAMED
candidates a pronoun refers to -- it does not address the common-noun clustering problem, so, like item
1, it is capped at improving roughly the ~10% named-pronoun slice.

### Item 7 -- REFERENT SEGMENTATION: gold spans given, but ENTITY CLUSTERING is not -- THE DOMINANT ITEM

OURS: given gold mention SPANS (boundaries), but still has to decide which spans corefer to the same
entity (clustering) -- this is the actual coref job, and it is proper-name-centric (built around a named-
character canonicalizer).

BRAIN, framed correctly: the task's brief cites Gernsbacher's Structure Building Framework (1990,
Language Comprehension as Structure Building) for how discourse referents are built from the input
(laying a foundation, then mapping/attaching new information, with active suppression of irrelevant
structure and enhancement of relevant structure) -- this is the right FRAME but the wrong LEVEL of
literature for explaining OUR specific 36% number. The trace on disk
(signal_loss_chain_analysis_2026-09-04.md) found: of 637 scorable experiencer mentions, only 16.5% are
named characters; 83.5% are COMMON-NOUN cluster heads ("the man," "the child," "the woman"); genuine
named-pronoun coref errors are ~61/637 (~9.6% of the total loss); the other ~90% is the common-noun
referent representation gap. The RIGHT brain-mechanism literature for THIS specific gap is the
definite-description / bridging-reference literature, a distinct sub-field from pronoun-cue-retrieval:
- Clark & Haviland 1977 ("Comprehension and the given-new contract," in Discourse Production and
  Comprehension, Ablex, pp.1-40): a reader treats a definite NP as GIVEN information and searches for an
  antecedent to attach it to; when no direct antecedent exists, the reader performs a BRIDGING inference
  (adds an implicit proposition connecting the new NP to something already in the discourse model via a
  relation the reader infers the writer intended -- e.g. "the door" after "a house" bridges via
  part-whole). This is NOT a retrieval-among-candidates operation, it is an INFERENCE operation over
  world/lexical relations.
- Poesio & Vieira 1998 ("A Corpus-based Investigation of Definite Description Use," Computational
  Linguistics 24(2):183-216): an empirical corpus study finding definite descriptions split into
  systematic categories -- discourse-new (never seen before), anaphoric with a HEAD-NOUN MATCH to an
  earlier mention (the tractable majority case), and bridging/associative (no head match, requires an
  inferred link) -- and shows resolution strategy differs sharply by category; head-match anaphora is the
  cheap, high-yield slice, bridging is the hard residual.
- Gundel, Hedberg & Zacharski 1993 ("Cognitive status and the form of referring expressions in
  discourse," Language 69(2):274-307): the Givenness Hierarchy -- a referring expression's FORM (pronoun
  vs demonstrative vs definite description vs indefinite) conventionally encodes the SPEAKER'S assumed
  COGNITIVE STATUS of the referent (in-focus, activated, familiar, uniquely identifiable, referential,
  type-identifiable) in the listener's mind -- i.e. the brain uses the FORM of the referring expression
  itself as a structural cue to how (and whether) to search for an antecedent, something a
  form-agnostic ranker does not do.
- Ariel 1990 (Accessing Noun-Phrase Antecedents, Routledge): Accessibility Theory -- referring
  expressions are markers of the antecedent's degree of mental accessibility (salience + unity/
  connectivity to the anaphor); definite descriptions mark LOW accessibility (expect a less-recent,
  possibly non-focal antecedent, often needing content-based matching), pronouns mark HIGH accessibility
  (expect the current focus) -- meaning the RIGHT resolution procedure differs by referring-expression
  type, not one procedure applied uniformly.
PRECISE DIFFERENCE: the brain's discourse-referent tracker treats a common-noun/definite-description
mention as a first-class trackable entity, resolved via DESCRIPTIVE-CONTENT matching (does this NP's
head noun and modifiers match an existing tracked entity's description?) and BRIDGING inference (is
there a plausible relation to an existing entity even without a head match?), with the referring
expression's FORM itself signaling which procedure to use (Givenness Hierarchy) and how far back to
look (Accessibility). Our coref organ, per the trace, is effectively built around NAMED-character
identity (a canonicalizer keyed on proper names) and has no comparable descriptive-content-matching or
bridging mechanism for entities that are only ever referred to by common nouns -- which is 83.5% of
the population this problem cares about.
PREDICTED FAILURE (measured, not merely predicted): of 244 reader abstains, 212 are because gold is a
common-noun entity the canonicalizer cannot name (only 32 are genuine misses on a named cluster); of
155 wrong-name errors, 126 are on common-noun-gold mentions (only 29 are a named pronoun bound to the
wrong named character). This is exactly the signature the definite-description literature predicts for
a system with no head-match/bridging mechanism: it either cannot name the entity at all (abstain) or
names it inconsistently across common-noun re-mentions (wrong-name).

### Item 8 -- EMOTION-EXPERIENCER BINDING into the situation model

OURS: attaches affect to the resolved character entity (per SOLVED.md, this part is already built and
measured near-ceiling GIVEN correct coref: F1 0.945 with gold coref).

BRAIN: per the companion note (research_affect_emotion_brain_mechanism_2026-09-04.md, already verified
in that note's own session) and the event-indexing model (Zwaan & Radvansky 1998, "Situation models in
language comprehension and memory," Psychological Bulletin 123(2):162-185; Zwaan, Langston & Graesser
1995, "The construction of situation models in narrative comprehension: An event-indexing model,
Psychological Science 6(5):292-297) -- situation models track five core dimensions (protagonist, time,
space, causation, motivation/intentionality) with NO separate emotion dimension in the canonical model;
a character's emotional state is instead a continuously-updated PROPERTY BOUND TO THE PROTAGONIST NODE
ITSELF. Neurally this binding is supported by a partially separate affective-appraisal system (amygdala,
vmPFC/OFC, anterior insula -- dissociated from the belief/goal "cognitive ToM" network per Campanella et
al. 2022's triple dissociation, cited in the companion note), whose valence+arousal output (Russell 1980
circumplex; Barrett 2006 constructed emotion) is written onto the SAME discourse-referent node that
coreference/protagonist-tracking maintains -- one representation with an appraisal-written field, not two
independently-indexed representations needing a separate binding step.
PRECISE DIFFERENCE / RELEVANCE: this makes coref failure MAXIMALLY costly for affect specifically -- if
entity resolution (items 1-7) misidentifies WHICH node "she"/"the child" points to, the emotion is
written onto the WRONG node, because there is exactly one binding site per entity in both the brain's
architecture and any correct implementation. There is no independent "emotion-binding" mechanism to get
right once coref is correct.
PREDICTED FAILURE: none additional -- this item CONFIRMS, rather than adds to, the diagnosis: the
signal-loss trace found the affect-extraction+experiencer-linking+valence rules are near-perfect given
good coref (F1 0.945 with gold coref), so the entire 36%-vs-89% story is upstream of the affect register,
in entity resolution (items 1-7, dominated by item 7).

======================================================================
2. WHY THE THREE PRIOR FIXES FAILED -- READING THE MEASURED NUMBERS THROUGH ITEMS 1-7
======================================================================

- Global-protagonist salience fallback (-0.001, a wash): item 3's prediction exactly -- a non-decaying,
  cumulative-frequency "salience" signal with no reactivation dynamic will guess the wrong same-gender
  character about as often as the right one, because "most frequent overall" is not the brain's notion
  of "currently activated." It also could only ever fire on named/gender-taggable candidates -- it does
  nothing for the 83.5% common-noun majority (item 7).
- Recency+subjecthood+gender Centering resolver, as REPLACEMENT (-0.051, worse than baseline): item 5's
  prediction exactly -- a hand-coded additive formula reproduces Centering's SURFACE correlates without
  its GENERATIVE mechanism (incremental graded-cue retrieval, items 1-3), so it is a fourth rigid
  heuristic competing with, not unifying with, the existing ranker's heuristics, and a hard gender filter
  (item 4) makes any upstream gender mis-tag unrecoverable. As a REPLACEMENT it also lost whatever
  incidental value the existing ranker had on the 16.5% named slice.
- Same as fallback-only (-0.003, still a wash): consistent with the same diagnosis -- fallback-only
  removes the "replacement" risk but keeps the "wrong problem" risk: it is still a pronoun-ranking
  heuristic addressing item 1-6 mechanics, and the trace shows those mechanics gate at most ~10% of the
  loss regardless of how well-tuned the ranking formula is.

======================================================================
3. THE SINGLE MOST IMPORTANT DIFFERENCE AND THE MECHANISM TO IMPLEMENT
======================================================================

The single most important difference is NOT a pronoun-retrieval mechanism (items 1-6). It is
REFERENT-TYPE COVERAGE (item 7): the brain's discourse-referent tracker treats common-noun/definite-
description mentions as first-class trackable entities, re-identified by DESCRIPTIVE-CONTENT matching
(head-noun/modifier match, the dominant tractable case per Poesio & Vieira 1998) and BRIDGING/associative
inference (Clark & Haviland 1977) when no head match exists, with the referring expression's own FORM
signaling which procedure and search depth to use (Gundel/Hedberg/Zacharski 1993 Givenness Hierarchy;
Ariel 1990 Accessibility Theory). Our coref organ's entity model is effectively PROPER-NAME-CENTRIC (a
named-character canonicalizer) with no comparable mechanism for clustering or re-identifying an entity
that is only ever referred to by common nouns. Since 83.5% of gold experiencer mentions are exactly this
type, and the measured genuine named-pronoun coref error is only ~9.6% of the total loss, no amount of
improving items 1-6 -- however brain-faithful -- can close more than a small fraction of the 36%-vs-89%
gap; three attempts at exactly that (items 1,3,5 in practice) all measured near-zero or negative, which
is the predicted outcome once you know where the loss actually is.

MECHANISM TO IMPLEMENT: extend the coref organ with a common-noun/definite-description entity tracker,
in priority order: (a) HEAD-NOUN-MATCH clustering -- when a new definite common-noun NP ("the man")
shares its head noun (allowing simple morphological/synonym variants) with an existing tracked entity's
most recent description within a bounded discourse window, cluster them (this is Poesio & Vieira's
cheapest, highest-yield category and requires no world-knowledge inference, only lexical matching --
directly buildable glass-box); (b) FORM-SENSITIVE SEARCH DEPTH -- use the referring expression's form
(bare pronoun vs demonstrative vs definite description vs indefinite) to set how far back / how strict
the match must be, per the Givenness Hierarchy, rather than one fixed window for every expression type;
(c) as a harder second phase, BRIDGING inference for common nouns with no head match but a plausible
lexical/world relation to a tracked entity or location (part-whole, role-filler, set-member) -- this
phase is the harder, possibly located-negative-worthy residual (bridging needs relational/world
knowledge, arguably touching the same meaning-channel gap already named as the located negative for
inferred emotion in SOLVED.md section 8). Only AFTER (a)-(b) close most of the common-noun gap does it
become worth revisiting items 1, 4, and 6 (graded cue-based retrieval + implicit-causality bias) to
recover the residual ~10% named-pronoun slice -- building that architecture first, before (a)-(b), is
optimizing the wrong 90% of the problem.

======================================================================
4. CHEAP DECISIVE TEST
======================================================================

Using the already-built trace instrument (`experiments/exp_affect_chain_signal_loss_v1.py --trace`),
add a HEAD-NOUN-MATCH clustering pass (no new model, a rule: two common-noun-headed mentions with
compatible head noun/synonym and compatible gender/number/animacy, within N sentences, are the same
entity) as a coref override BEFORE the existing ranker, and re-run the same 637-mention trace. This is
cheap (a lexical rule pass, hours not days) and decisive because it directly tests the item-7 hypothesis
without building the harder cue-based-retrieval architecture (items 1-6) or the bridging-inference phase.

Two sub-tests, since the trace already separates the populations:
(i) COMMON-NOUN slice (83.5% of mentions, ~90% of the loss): does head-noun-match clustering reduce the
    212 canonicalizer-abstains and the 126 common-noun wrong-name errors?
(ii) NAMED slice (16.5% of mentions, ~9.6% of the loss): unaffected by (i); this is where items 1,4,6
    (graded retrieval + implicit-causality) would be tested separately, on the 61 genuine named errors.

======================================================================
5. FALSIFIABLE PREDICTIONS -- HARD-PASS / HARD-FAIL
======================================================================

PREDICTION A (item 7 dominance, head-noun-match clustering):
- HARD-PASS: head-noun-match clustering alone recovers >=15 percentage points of overall experiencer-
  binding accuracy (0.36 -> >=0.51) on the same 100-doc / 637-mention population, with the common-noun
  abstain count dropping by a proportional amount (a large chunk of the 212 canonicalizer-abstains
  resolved). This would confirm referent-type coverage, not pronoun mechanics, is the dominant lever, and
  justify building the harder bridging phase next.
- HARD-FAIL: recovers <5 percentage points, OR the abstain/wrong-name counts on the common-noun slice do
  not move proportionally. This would mean the common-noun failure is NOT simple head-match clustering
  (e.g. gold's own common-noun clustering criteria differ structurally from head-noun identity, or most
  common-noun mentions genuinely require bridging/world-knowledge from the start) -- redirect to
  measuring what FRACTION of the 212 abstains are head-match-eligible at all before concluding the
  mechanism is wrong (an underpowered test is not the same as a refutation).

PREDICTION B (items 1/4/6, graded cue-based retrieval on the residual named-pronoun slice):
- HARD-PASS: replacing the hard gender filter with a graded cue-combination score (recency-decayed
  activation + graded agreement + implicit-causality bias, combined per candidate, no elimination step)
  recovers >=5 of the ~9.6 percentage points attributable to the 61 genuine named-pronoun errors, without
  regressing the correctly-resolved 37.4% agree rate.
- HARD-FAIL: recovers <2 percentage points on that named-pronoun slice, which would mean the 61 residual
  errors are dominated by something else entirely (e.g. mention-detection/attribute-extraction noise
  upstream of retrieval, or genuinely hard multi-candidate ambiguity even for a competent reader) rather
  than the ranking mechanism -- in that case do not keep iterating on retrieval formulas for this slice.

======================================================================
6. CROSS-THREAD SYNTHESIS (prior entries, this same problem folder)
======================================================================

- SOLVED.md (owner_verdict: SOLVED) landed the affect register itself, near-ceiling given good coref
  (F1 0.945), and named coreference as the dominant, separately-filed loss (87-89% of end-to-end loss),
  section 7/7a/NEXT STEPS #1. This research note answers exactly the mechanism-diff question SOLVED.md's
  section 7a left open ("what EXACTLY differs between our implementation and the brain's mechanism").
- signal_loss_chain_analysis_2026-09-04.md ran the per-mention trace that this note leans on directly;
  its own conclusion ("the real gap is common-noun ENTITY segmentation/clustering... not a pronoun
  heuristic") is INDEPENDENTLY CONFIRMED here from the opposite direction: I was asked to explain the
  pronoun-mechanism gap from first-principles brain literature, and the literature itself (once you ask
  "what population does this literature even apply to") points away from pronoun-retrieval mechanics and
  toward the definite-description/bridging literature, which the trace's raw numbers already implied.
  Two independent methods (a numeric trace, and a literature-coverage argument) converge on the same
  answer -- this raises confidence in the reframe beyond what either alone would support.
- research_emotion_term_denotation_and_experiencer_coref_2026-09-04.md proposed the Centering + implicit-
  causality pronoun fallback that (per the task's framing) became one of the three failed fixes; this note
  explains, with the trace's numbers, why that proposal -- while literature-faithful for what it targeted
  -- targeted a small (~10%) slice of the loss.
- research_experiencer_psych_verb_brain_mechanism_2026-09-04.md's psych-verb experiencer-linking frame
  remains the correct, working, PINNED mechanism for item 2/6's "which grammatical slot is the
  Experiencer" question; it is unaffected by this note's findings and continues to be the right
  foundation for whichever coref fix is built next.
- research_affect_emotion_brain_mechanism_2026-09-04.md's finding that Zwaan-Radvansky's five dimensions
  have no separate emotion slot (item 8) is reused here unchanged, and is corroborated rather than
  challenged by this note.

======================================================================
7. SUBSTRATE-PRODUCT IMPLICATIONS
======================================================================

In plain terms: the affect/emotion tracker itself works well once it knows who is being talked about.
The remaining weakness is figuring out WHO "the man," "the child," or "she" refers to across a story --
and the numbers show that failure is concentrated almost entirely (about nine-tenths of it) on
descriptions like "the man" or "the child" rather than on pronouns pointing to named characters like
"Mary" or "John." That is good news for the product: the fix is not a large, uncertain rebuild of
pronoun logic (three attempts at that already came back flat or worse); it is a narrower, cheaper,
literature-grounded addition -- teaching the reader to recognize when two descriptions like "the man"
and "him" three sentences later are the same person, the same way readers do it, by matching what the
description SAYS (a matching head word, matching gender) before resorting to anything more clever. This
is buildable without any outside AI model, reuses the existing coreference machinery, and has a cheap,
fast test (re-run the existing measurement tool with one new rule added) that will show within a day
whether it is the right lever, rather than committing to a larger, slower rebuild first. The risk of this
recommendation: if gold's own common-noun grouping does not line up with simple head-word matching (for
example if the same person is called "the girl" in one place and "the child" in another with no shared
word), the cheap fix will underperform and a harder, slower capability (teaching the reader to infer
relationships between descriptions, not just match words) would be needed instead -- the cheap test above
is designed to reveal that quickly rather than assume it will work.

======================================================================
8. CITATIONS (verified count)
======================================================================

Fresh-verified this session via WebSearch (title/journal/year cross-checked against publisher, index, or
author-hosted PDF pages): 19 --
Lewis & Vasishth 2005; McElree 2000 / McElree-Foraker-Dyer 2003; Van Dyke & McElree 2006; Van Dyke &
McElree 2011; Wagers, Lau & Phillips 2009; Altmann & Kamide 1999; Nieuwland & Van Berkum 2006 (both
papers); Levy 2008; Anderson & Schooler 1991; Gordon, Grosz & Gilliom 1993; Garvey & Caramazza 1974 (both
papers); Ferstl, Garnham & Manouilidou 2011; Koornneef & Van Berkum 2006; Gernsbacher 1990; Zwaan &
Radvansky 1998; Zwaan, Langston & Graesser 1995; Clark & Haviland 1977; Poesio & Vieira 1998; Gundel,
Hedberg & Zacharski 1993; Ariel 1990.

Not independently re-searched this session, cited at high confidence as standard/foundational (already
in use in on-disk prior notes in this same folder): Grosz, Joshi & Weinstein 1995 (Centering framework
core paper).

Cited by cross-reference to a companion note already verified in its own session (not re-verified here):
Campanella et al. 2022; Shamay-Tsoory & Aharon-Peretz 2007; Russell 1980; Barrett 2006; Lindquist et al.
2012 (all in research_affect_emotion_brain_mechanism_2026-09-04.md, item 8 only).

Verified count for THIS note's own claims: 19/20 fresh-verified, 1 high-confidence-unverified
(Grosz-Joshi-Weinstein 1995), 5 cross-referenced from a sibling note.

======================================================================
TLDR (plain English)
======================================================================
The part of the reader that tracks feelings works well once it knows which person a sentence is about.
The part that is losing almost all the points is figuring out which person "she," "the man," or "the
child" refers to. We tried three brain-inspired fixes to the PRONOUN-guessing part (recency, frequency,
grammar rules) and all three failed to help. This research explains why: a direct count of the actual
misses shows nine out of ten of them are not pronoun mistakes at all -- they are cases where the person
is called "the man" or "the child" rather than by name, and our reader has no good way to recognize that
two such descriptions, mentioned in different places, refer to the same person. The pronoun-guessing
fixes could only ever help the smaller one-in-ten slice, which is why none of them moved the needle. The
fix that should move the needle is different and cheaper: teach the reader to match descriptions by their
key word (matching "the man" to "him" to "the man" again) before trying anything fancier, then measure it
with the same tool we already built.

======================================================================
QUESTIONS
======================================================================
None.

======================================================================
NEXT STEPS
======================================================================
1. Build the head-noun-match common-noun clustering pass and re-run the existing trace instrument
   (`exp_affect_chain_signal_loss_v1.py --trace`) -- this is the cheap decisive test (section 4) and
   should be done before any further pronoun-mechanism work.
2. If Prediction A HARD-PASSes: file the bridging-inference phase (section 3, mechanism step c) as the
   next problem, flagging its likely dependency on the same meaning-channel gap already named as the
   located negative for inferred emotion.
3. If Prediction A HARD-FAILs: measure what fraction of common-noun abstains are even head-match-eligible
   before concluding the mechanism is wrong; if most are not head-match-eligible, go straight to bridging
   inference rather than iterating on head-match variants.
4. Only after (1)-(3): revisit items 1/4/6 (graded cue-based retrieval + implicit-causality bias) as a
   targeted fix for the residual ~9.6% named-pronoun slice (Prediction B), reusing the existing
   psych-verb experiencer-linking frame as the highest-weight cue when the clause contains a psych verb.
