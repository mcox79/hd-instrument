# Research: how the brain/grammar assigns the EXPERIENCER role of an emotion from sentence syntax

Date: 2026-09-04
Drill type: literature scan (direct, no sub-agent fan-out per task instruction)
Upstream consumer: per-character AFFECT register (situation-model affect/emotion dimension)

## HEADLINE

Experiencer-role assignment is **PINNED-BY-EVIDENCE** as a *lexically stored, per-verb linking fact*, not a
syntactic default. Every emotion-bearing predicate type in English (psych verb, predicate adjective, adverb,
"to X's N" construction, deverbal/underived noun, passive) has a distinct but **reliable structural binding
rule**, and the one place processing actually gets harder (object-experiencer verbs: "The dog frightened Mary")
is well documented with reading-time, ERP/MEG, acquisition, and aphasia evidence. This is directly usable as a
priority-ordered rule table for an extractor: **verb-class lookup first (dominant signal), construction-pattern
rules second (adjective/adverb/PP/noun), with passive-voice-flip and genitive-binding as two special-case
transforms.**

## 1. Psych-verb classes (class membership -- PINNED-BY-EVIDENCE, this is the extractor's core lexicon)

### Cross-linguistic theoretical base
Belletti & Rizzi 1988 ("Psych-verbs and Theta Theory," *Natural Language and Linguistic Theory* 6:291-352)
established the canonical 3-way split from Italian, each class sharing the theta-grid [Experiencer, Theme] but
differing in how it maps to syntax:
- **Class I -- *temere* "fear" type**: Experiencer = subject, Theme = object. Canonical transitive.
- **Class II -- *preoccupare* "worry" type**: Theme = subject, Experiencer = object.
- **Class III -- *piacere* "please/appeal" type**: Experiencer = oblique/dative, Theme = subject; both SVO and
  OVS surface orders attested. (English analogs: *appeal to, matter to, occur to X*.)
The Experiencer argument in Class II/III is diagnosed by dative case, *essere* ("be") auxiliary selection, and
free word order -- i.e., independent morphosyntactic fingerprints, not just semantic assignment by fiat.
[PINNED-BY-EVIDENCE, foundational GB-era result, still the reference point for every later account including
Pesetsky 1995 and Landau 2010.]

### English mapping: Levin 1993 / VerbNet (this is what an extractor should encode directly)
Levin (*English Verb Classes and Alternations*, 1993) gives four psych-verb classes; VerbNet operationalizes
them as **admire-31.2** (subject-experiencer) and **amuse-31.1** (object-experiencer), plus two intransitive
oblique-experiencer classes (**marvel-31.3**, **appeal-31.4**). VerbNet role definitions confirmed directly:
amuse-31.1 = "Cause V Experiencer" (Cause=subject/stimulus, Experiencer=object); admire-31.2 = Experiencer
subject, Stimulus object. PropBank framesets (cross-checked directly) encode the SAME fact per-verb at the
NLP-resource level: **fear** -- Arg0 = "scaredy cat" (Experiencer/subject), Arg1 = "afraid of" (Stimulus/object).
**frighten** -- Arg0-PAG = "cause of fear" (Stimulus/subject), Arg1-PPT = "frightened entity" (Experiencer/
object). This is an independent, applied confirmation that real NLP argument-structure resources store the
mapping as a per-verb (per-roleset) fact, not derive it from a general rule. [PINNED-BY-EVIDENCE]

#### SUBJECT-EXPERIENCER list ("fear-type" / admire-31.2 -- experiencer = SUBJECT, stimulus = OBJECT)
admire, adore, appreciate, cherish, esteem, exalt, favor, idolize, prize, relish, respect, revere, savor,
treasure, value, venerate, worship, abhor, detest, despise, disdain, dislike, distrust, dread, envy, execrate,
hate, loathe, mistrust, resent, believe, bewail, deplore, enjoy, **fear**, lament, like, **love**, miss, mourn,
**pity**, regret, rue, suffer, support, tolerate, trust, want, crave, yearn (for), long (for), care (about),
worry (about) [alternating -- see note below], grieve (over/for) [alternating].
Common core for a lexicon (highest frequency, least ambiguous): **fear, love, hate, like, admire, adore, enjoy,
dread, envy, pity, trust, distrust, resent, loathe, despise, cherish, respect, miss, regret, mourn, crave.**

#### OBJECT-EXPERIENCER list ("frighten-type" / amuse-31.1 -- experiencer = OBJECT, stimulus = SUBJECT)
amuse, charm, delight, entertain, fascinate, **frighten**, offend, perplex, sadden, terrify, horrify, torment,
enchant, thrill, worry [alternating], concern [alternating], bother, annoy, cheer, comfort, amaze, disgust,
interest, entice, scare, confuse, shock, upset, surprise, satisfy, excite, inspire, impress, trouble, embarrass,
humiliate, irritate, exasperate, distress, alarm, appall, astonish, astound, dismay, disturb, unsettle, unnerve,
stun, overwhelm, gratify, relieve, reassure, soothe, calm, please, disappoint, depress, discourage, encourage,
intrigue, move (emotionally), touch (emotionally), stir, agitate, unsettle, madden, infuriate, anger [alternating
with subject-exp "be angry at"], repel, revolt, nauseate, disquiet, haunt, devastate, crush (emotionally),
gladden, delight, tickle (amuse).
Common core for a lexicon: **frighten, scare, terrify, delight, please, annoy, anger, surprise, disgust, amaze,
astonish, shock, upset, worry, disappoint, embarrass, comfort, satisfy, excite, bore, amuse, horrify, alarm,
impress, thrill, sadden, depress, offend, humiliate, relieve, disturb.**

#### Alternating / ambiguous class (flag for the extractor, do not force a single class)
**worry** and **concern** genuinely alternate: "Mary worries about the dog" (subject-experiencer, intransitive+PP)
vs. "The dog worries Mary" (object-experiencer, transitive). **grieve** similarly alternates ("Mary grieves for
her dog" vs., less common, causative uses). These need frame-based (not lemma-only) disambiguation: transitive
NP-V-NP frame maps to amuse-type; intransitive-with-PP frame maps to admire-type. This is consistent with
Landau 2010's finding that some "frighten"-class verbs are agentive/eventive and others purely stative
(worry, concern) -- the class is not perfectly homogeneous even within amuse-31.1.

### Third class (dative/oblique experiencer, English residue of Belletti & Rizzi Class III)
appeal (to), matter (to), occur (to), seem [+ Exp-PP] ("it seems to Mary that..."), happen (to), come as [a
surprise] (to). Rule: **experiencer = object of "to."** [PINNED-BY-EVIDENCE, direct English reflex of the
*piacere* class.]

## 2. Is the mapping lexically stored? -- PINNED-BY-EVIDENCE

Yes, at two independent levels of evidence:

**(a) Theoretical/linking-rule level.** UTAH (Baker 1988, formalized via Belletti & Rizzi 1988 and Pesetsky
1995 *Zero Syntax: Experiencers and Cascades*) treats the Experiencer-to-syntactic-position mapping as fixed
per verb by the verb's own theta-grid and its **decomposed causal semantics**, not by a single universal
thematic-hierarchy default applied uniformly. Pesetsky's key generalization (fetched and confirmed): frighten-
type verbs **encode causation** (the stimulus caused the mental state) while fear-type verbs do **not** encode
causation (the stimulus must instead be the *target* of the emotion, not necessarily its cause) -- e.g. "Mary
feared the exam" does not entail the exam did anything causal, but "The exam frightened Mary" does. This
causal/non-causal split, not raw thematic hierarchy, is what is stored per verb. Landau 2010 (*The Locative
Syntax of Experiencers*) adds that object-experiencers are uniformly **grammaticalized as (often null) locative/
dative PPs** cross-linguistically (20+ languages surveyed) -- explaining why object-experiencers show oblique
syntactic behavior (restricted passivization, binding asymmetries) despite occupying a structural object
position.

**(b) Processing-architecture level.** Constraint-based lexicalist parsing (MacDonald, Pearlmutter & Seidenberg
1994, and the broader MacDonald/Seidenberg/Trueswell program) establishes generally that verb-specific
argument-structure/frequency information is retrieved from the lexicon and used immediately, incrementally,
to guide thematic-role assignment during parsing -- there is no separable "generic" thematic-assignment stage
that ignores lexical identity. Applied to psych verbs specifically, this predicts (and the data below confirm)
that experiencer-role assignment is verb-triggered the instant the verb is recognized, not computed from a
subject-general default. The PropBank/VerbNet cross-check above (Arg0/Arg1 differing by verb, not by a general
rule) is the applied-NLP mirror of this same claim.

Caveat per lit-scan calibration discipline: the deeper claim that this is *neurally* stored as a discrete
lexical-retrieval event (rather than emergent from distributional statistics at prediction time) is
OUR-INVENTION-UNDER-TEST as a substrate-implementation choice -- the cited literature pins the *linguistic*
fact (verb-specific, not rule-general) but does not by itself mandate a symbolic-lookup implementation over a
distributional one. Either substrate implementation is compatible with the behavioral/psycholinguistic data.

## 3. The object-experiencer processing penalty -- PINNED-BY-EVIDENCE, multiple converging measures

This is the best-quantified part of the literature and gives usable effect sizes:

**Reading time (adults, healthy).** Gattei, Vasishth & Dickey (self-paced reading, Spanish object-experiencer
vs. agentive dative verbs) and the follow-up Gattei, Dickey, Wainselboim & Paris 2015 (*Quarterly Journal of
Experimental Psychology*, "The thematic hierarchy in sentence comprehension") found that when the sentence's
surface word order does NOT respect the verb's required thematic-hierarchy mapping (i.e., non-canonical
OVS order, or an object-experiencer verb's indirect argument-to-syntax mapping such as *gustarle* "to like/
please"), readers take reliably longer at the second argument region than when word order/mapping is direct
(*gritarle* "to shout at" -- an agentive dative control). Direction and reliability of the slowdown are
established; the papers report the effect at the argument-region level rather than a single omnibus millisecond
figure I can quote with confidence -- treat the delta as "reliable but not independently re-derived here."

**MEG (adults, healthy).** Brennan & Pylkkanen 2010 (*Language and Cognitive Processes* 25(6):777-807),
"Processing psych verbs: Behavioural and MEG measures of two different types of semantic complexity," found
object-experiencer (amuse-type) psych verbs carry measurably greater lexical-semantic processing complexity
than subject-experiencer (fear-type) verbs, with both behavioral (RT) and MEG neural signatures distinguishing
the two classes -- consistent with the causative decomposition Pesetsky proposes (amuse-type verbs must
compose an extra CAUSE component online).

**ERP.** General ERP literature on thematic-role assignment (reviewed via multiple sources) shows atypical/
non-canonical thematic-role mappings elicit an N400 effect (semantic-integration cost) and, when the mapping
forces syntactic reanalysis or conflict resolution, a semantic P600. This is the expected signature for
object-experiencer sentences whenever animacy or canonical-word-order expectations are violated (e.g. an
inanimate stimulus subject followed by an animate experiencer object is actually the CANONICAL case for
amuse-type verbs, so the violation-triggering configuration is specifically noncanonical *word order*, i.e.
OVS/passive-like orders, not the verb class per se).

**Aphasia (Broca's, agrammatic) -- concrete effect sizes, directly fetched.** Thompson & Lee (*Journal of
Neurolinguistics*, ~2009), "Psych verb production and comprehension in agrammatic Broca's aphasia":
| Condition | Subject-Exp accuracy | Object-Exp accuracy |
|---|---|---|
| Active comprehension | 75% | 65% |
| Passive comprehension | 52% (chance: t(7)=.456, p=.662) | 72% |
| Active production | 85.4% | 47.9% |
| Passive production | 15.7% | 36.5% (diff significant: t(7)=-2.517, p=.040) |
Voice preference on first attempt: subject-experiencer verbs produced 79% active / 21% passive; object-
experiencer verbs produced 38% active / 62% passive. Interpretation offered (Argument Structure Complexity
Hypothesis, ASCH): object-experiencer verbs have objectively more complex argument structure (extra CAUSE
layer per Pesetsky), so they are harder to produce actively -- but once passivized, the Experiencer lands in
subject position, which agrammatic speakers strongly prefer regardless of verb class, so object-experiencer
PASSIVES are actually *easier* than object-experiencer actives. This is a striking, reusable diagnostic: the
brain's damaged-state behavior reveals a **standing preference for Experiencer-in-subject-position**, overridden
only when the lexical entry for the verb forces otherwise.

**Acquisition -- important correction to the naive hypothesis.** Hartshorne, O'Donnell & Tenenbaum (*Cognition*,
"Psych verbs, the linking problem, and the acquisition of language," PMC5143181) directly tested whether
children default to an experiencer-subject template and found the OPPOSITE of the naive expectation: children
acquire **frighten-type (object-experiencer) verbs comprehension EARLIER** than fear-type verbs despite
frighten-type verbs being lower-frequency in the input. Reliable fear-type comprehension does not emerge until
around age 5. Follow-up production data (Experiment 9): by age 4-5, children productively generalize the
causal/episodic vs. habitual-attitude semantic distinction to choose the correct syntactic frame for novel
verbs (65.6% frighten-syntax for episodic-cause scenarios vs. 33.3% for habitual-attitude scenarios, **d=0.6**).
The authors explicitly argue AGAINST a model where fear-verbs are "the default" and frighten-verbs are learned
exceptions -- both classes are acquired via the SAME semantic-to-syntax mapping rule (causal event -> object-
experiencer syntax; stable attitude -> subject-experiencer syntax), and frighten-type is easier early because
caused, observable episodes have clearer real-world/perceptual correlates for a young learner than an internal,
enduring attitude state does.
Where children DO show a documented, large, robust delay is a different phenomenon: **passive comprehension of
non-actional (including psych) verbs**. Maratsos, Fox, Becker & Chalkley 1985 ("Semantic Restrictions on
Children's Passives") is the classic, still-replicated finding: 4-year-olds comprehend actional passives
("Superman was held by Batman") but fail on non-actional/mental-verb passives ("Goofy was liked by Donald");
this actional-vs-non-actional passive comprehension gap persists **2-3 years** into grade school. This is the
piece of evidence closest to what a "children over-apply an actor/agent-as-subject template" story predicts --
but it is a template about AGENTHOOD/CAUSATION in passives generally, not specifically an "experiencer=subject"
overextension onto object-experiencer verbs. [Correcting the framing in the task prompt: the acquisition
literature does NOT show children mis-binding the experiencer role of frighten-type verbs to the wrong argument;
it shows children struggle to parse the PASSIVE VOICE of non-actional verbs at all, which is a different failure
mode. Marking this explicitly since it changes what an extractor should worry about: passive-voice handling,
not experiencer-role confusion per se.]

**What this says about the brain's default linking.** Converging picture across aphasia + acquisition +
processing-cost evidence: there is a standing, robust **surface preference for Experiencer-in-subject-position**
(shown by aphasics' passive-voice preference reversing by verb class, and by the fact that object-experiencer
ACTIVES carry a measurable extra processing/production cost relative to subject-experiencer actives). But this
preference is a *linear/positional* bias, not a role-assignment error -- it does not cause healthy adults or
typically-developing children past ~5 to actually mis-assign WHO the experiencer is. The verb-specific lexical
entry always wins for role assignment; the "default" only shows up as a *difficulty/cost* signal (slower RT,
lower accuracy under damage, later acquisition), not as systematic mis-binding. **For an extractor this means:
class-lookup should be treated as near-deterministic (PINNED), while any residual uncertainty budget belongs on
verbs outside a known lexicon (novel/rare verbs), where a subject-experiencer default is the literature-
supported fallback prior** (per Hartshorne et al.'s finding that stable, non-episodic predicates default toward
attitude/subject-experiencer framing, and per the general cross-linguistic markedness asymmetry: subject-
experiencer is the "elsewhere" case in most inventories, object-experiencer requires a causal-event stimulus).

## 4. Non-verb constructions -- binding rules

**(a) Copular "be/feel/seem + emotion adjective."** "Mary was afraid," "Mary felt happy," "Mary seemed
delighted." PropBank confirms "afraid" as adjective retains the SAME Arg0(Experiencer)/Arg1(Stimulus-of) frame
as the verb "fear" ("afraid of" = Arg1). **Rule: experiencer = the subject of the copula, full stop, regardless
of which adjective is used** -- this holds for both etymologically subject-experiencer adjectives (afraid,
fearful, happy, glad, sad, angry, jealous, envious, proud) and for adjectives that are morphologically the
PASSIVE PARTICIPLE of an object-experiencer verb (delighted, frightened, pleased, annoyed, surprised, amazed,
disgusted, worried, scared, embarrassed, thrilled) -- in both cases the copula subject is the experiencer
because the participial adjective has already "absorbed" the external Cause argument the way a true passive
does (see SS5). [PINNED-BY-EVIDENCE via PropBank cross-verification + standard passive-adjective analysis;
this is the single most reliable non-verb rule and should be the extractor's highest-confidence fallback
pattern.]

**(b) Affective adverbs ("she spoke angrily," "he answered fearfully").** These are the class traditionally
called subject-oriented / agent-oriented adverbs (Jackendoff 1972 onward): they predicate an emotional state
or attitude of the CLAUSE SUBJECT while modifying the manner of the described action. **Rule: experiencer =
subject of the clause the adverb attaches to**, independent of whether the adverb's base adjective is
subject-experiencer-derived (angrily <- angry) or object-experiencer-participle-derived (frighteningly is
NOT subject-oriented -- see caveat below). Caveat: adverbs built on object-experiencer participles or on the
CAUSE-side adjective ("frighteningly," "surprisingly," "annoyingly") are STIMULUS/SPEAKER-oriented, not
subject-oriented ("She spoke frighteningly" = her manner of speaking was frightening [to some unstated
experiencer, often the speaker/observer], NOT that she herself was frightened). This is an important
extractor gotcha: **-ly adverbs from object-experiencer stems do NOT bind the clause subject as experiencer;
adverbs from subject-experiencer/plain-adjective stems do.** [PINNED-BY-EVIDENCE for the general subject-
oriented-adverb mechanism; the object-experiencer-adverb caveat is a direct, low-risk extrapolation from the
verb-class facts in SS1, flagged OUR-INVENTION-UNDER-TEST only insofar as I did not find a paper stating the
adverb-specific caveat explicitly -- treat as high-confidence but unverified-in-print.]

**(c) "to X's N" ("to her delight," "to his horror," "to everyone's surprise").** Confirmed via the "affected
experiencer" / Aff(ect)-head literature (Bosse, Bruening & Yamada 2012, *Natural Language & Linguistic Theory*,
"Affected experiencers"; related work on non-core/free datives in German, Hebrew, Albanian, Japanese): a
dedicated syntactic head introduces the experiencer as a non-core (non-subcategorized) argument and adds a
conventional implicature that the sentence's event is the SOURCE of that experiencer's psychological state.
**Rule: experiencer = the possessor in the genitive ("her," "his," "everyone's").** This is fully general and
does not depend on verb class at all, since these are typically sentence-adverbial / parenthetical PPs
attached above the main clause. [PINNED-BY-EVIDENCE]

**(d) Emotion nouns ("her fear," "a wave of terror swept over him").**
- Genitive-possessor nominals ("her fear," "his joy," "Mary's dread of the exam") are deverbal/de-adjectival
  nominalizations that **preserve the argument structure of their base predicate**: since "fear" is a
  subject-experiencer predicate, "her fear (of the dog)" keeps "her" = Experiencer, "(of the) dog" = Stimulus,
  exactly mirroring "she fears the dog." **Rule: the genitive possessor of an emotion noun = experiencer**,
  by the same nominalization-preserves-argument-structure logic used broadly in generative nominalization
  theory (Grimshaw 1990, argument-structure nominals). [PINNED-BY-EVIDENCE as a general nominalization
  principle; application to specific emotion nouns is a direct, low-risk extrapolation.]
- "Metaphorical container/motion" constructions -- "a wave of terror swept over him," "fear washed over her,"
  "a pang of jealousy struck him," "dread crept up her spine" -- put the emotion noun in subject position (as
  a moving/acting force) and mark the experiencer as the **object of a locative/goal preposition** (over, upon,
  through) or as the direct object of a light "affect" verb (struck, gripped, seized, overcame, consumed).
  **Rule: experiencer = the PP object of the locative preposition, or the direct object of the light
  affect-verb.** This pattern is the clearest possible surface confirmation of Landau 2010's core claim that
  experiencers are grammaticalized as LOCATIVES cross-linguistically -- English idiomatically encodes "being
  emotionally affected" as "being a location that an emotion moves into/over," which is exactly Landau's
  locative-syntax analysis surfacing at the metaphor level. [PINNED-BY-EVIDENCE for the descriptive pattern;
  the Landau-locative explanatory link is a reasonable theoretical connection I am drawing, marked
  OUR-INVENTION-UNDER-TEST as an explicit link (the surface pattern itself is well attested, the causal
  explanation via Landau's syntax is my synthesis, not a claim from a single cited paper).]

## 5. Passives and implicit experiencers -- PINNED-BY-EVIDENCE

"Mary was frightened (by the dog)": the object-experiencer verb's DEEP-STRUCTURE object (Mary, the Experiencer)
is promoted to surface subject by ordinary passivization; the Stimulus/Cause, if present, appears in the
by-phrase, and if absent is existentially bound (implicit-argument reading: "someone/something frightened
Mary," un-specified). **Rule: in a passive of an object-experiencer verb, experiencer = surface subject,
exactly as in any ordinary passive** -- there is nothing exceptional about the ROLE-BINDING mechanism itself;
what IS well documented as exceptional is (i) restrictions on which psych verbs freely passivize at all
(Belletti & Rizzi's *piacere*-class datives and some stative amuse-class verbs like "concern," "cost," "cost"
resist passivization or sound archaic passivized: "?Mary is concerned by the news" vs. fully natural "Mary is
worried by the news"), and (ii) the aphasia data in SS3 showing that PASSIVES of object-experiencer verbs are,
if anything, easier/preferred for damaged parsers precisely because they put the Experiencer in subject
position matching the standing surface preference. There is no evidence anywhere in the literature scanned
that the passive changes WHO binds as experiencer -- only that it changes accessibility/preference. For the
adjectival-passive case ("Mary was frightened," stative reading, no implied ongoing causer), see SS4(a): the
participle "frightened" behaves as a plain subject-experiencer adjective at that point, with the Stimulus
optionally reappearing as an "of"-PP ("Mary was frightened of the dog," a genuinely stative construction distinct
from the true verbal passive "Mary was frightened by the dog"). [PINNED-BY-EVIDENCE]

## Cheap decisive test

Take a held-out set of ~30-50 sentences spanning all 5 construction types above (psych-verb active,
psych-verb passive, copular+adjective, affective adverb, "to X's N", emotion-noun-with-possessor,
emotion-noun-as-subject-metaphor), each hand-labeled with the true experiencer. Run the existing
subcategorization-frame extractor's proposed rule table (verb-class lookup -> construction-pattern fallback ->
passive-flip transform -> genitive-binding transform) and score exact-match experiencer-binding accuracy.
This requires NO new corpus (existing sentence-generation or LitBank-style annotated data can seed the set) and
is a same-day check.

## Falsifiable predictions

**HARD-PASS thresholds:**
- Subject-experiencer / object-experiencer verb-class lookup (using the enumerated lists above as the lexicon)
  achieves >=95% correct experiencer-binding on unambiguous, non-alternating verbs in simple active-voice
  sentences. (This should be close to 100% since it is a closed-class lookup problem, not an inference problem
  -- if it is below 95%, the lexicon or the frame-detection code has a bug, not a linguistic-theory gap.)
- Copular+emotion-adjective rule (experiencer = copula subject) achieves >=95% on a held-out adjective set
  including both plain (afraid, happy) and passive-participle-derived (frightened, delighted) adjectives.
- Passive-of-object-experiencer-verb rule (experiencer = surface subject) achieves >=95%.

**HARD-FAIL thresholds (would falsify "class-lookup is sufficient" and force a probabilistic/contextual
fallback):**
- If accuracy on the ALTERNATING class (worry, concern, grieve, anger) falls below 70% using frame-shape
  disambiguation (transitive NP-V-NP vs. intransitive+PP), this is a HARD-FAIL for "frame shape alone
  disambiguates alternating verbs" -- would indicate the extractor needs an additional cue (animacy of subject,
  presence of "about"/"at" PP) beyond raw transitivity.
- If accuracy on affective-adverb sentences falls below 70%, this is a HARD-FAIL for "adverb stem class alone
  determines subject-orientation" -- the object-experiencer-participle-adverb caveat in SS4(b) was flagged as
  unverified-in-print and may not hold as cleanly as predicted; would need re-derivation from a broader adverb
  corpus.
- If the "to X's N" or emotion-noun-possessor rules fall below 80% on hand-labeled sentences, that would falsify
  the claim that these are fully general, verb-class-independent rules, and would suggest a more restricted
  construction inventory is needed.

## Cross-thread synthesis with prior entries

This drill sits directly upstream of `notes/problems/the_situation_model_has_no_affect_emotion_dimension/` (the
problem this note is filed under) and is structurally parallel to the existing
`notes/problems/situation_model_has_no_spatial_location_dimension/research_deictic_center_and_hierarchical_
spatial_frameworks_2026-08-28.md` drill -- both are "which linguistic register needs its own extraction pass on
top of the existing subcategorization/argument-structure machinery" questions. The relevant prior organ is
whatever component currently does subcategorization-frame-driven attachment (PP-attachment, verb-argument
role assignment) for the situation model; per the brain-foundational checklist, REUSE should be checked first:
if a thematic-role/argument-structure assignment organ already exists (semantic-role-labeling-style component),
the psych-verb Experiencer/Stimulus distinction is a *lexicon addition* to that existing organ (a per-verb-class
flag: SUBJ_EXP vs OBJ_EXP vs DAT_EXP), not a new mechanism. The passive-flip and copular-adjective rules should
likewise reuse whatever passive-voice detection and copula-complement extraction already exists for ordinary
(non-psych) argument-structure work, since the transformation logic (deep-object -> surface-subject) is
identical to ordinary passive handling, not psych-verb-specific.

## Substrate-product implications

In plain terms: knowing WHO feels an emotion in a sentence is mostly a **vocabulary-lookup problem**, not a
hard reasoning problem, for the large majority of everyday emotion words -- roughly 95% accuracy should be
achievable just from a list of which emotion verbs put the feeler in the subject slot ("Mary feared...") versus
the object slot ("...frightened Mary"), plus four simple pattern rules for adjectives ("Mary was afraid"),
descriptive words like "angrily," the phrase "to X's delight/horror," and possessive phrases like "her fear."
The only genuinely hard part, worth budgeting real engineering time for, is a small handful of words that swing
both ways depending on how they're used in the sentence ("worry," "concern," "grieve," "anger") -- these need
a sentence-shape check, not just a word lookup. The cost of getting this wrong is that the system would
attribute an emotion to the wrong character (e.g., think the dog is scared instead of Mary) -- a visible,
easily-checked kind of error, and one a small hand-built list plus a handful of rules should catch the vast
majority of the time. Risk in this recommendation: the two "flagged as unverified" rules above (the
object-experiencer-adverb caveat and the metaphor-noun-to-Landau-locative link) are my own synthesis rather
than a directly cited experimental result -- they are low-risk generalizations from solid adjacent evidence,
but a solver should treat them as hypotheses to spot-check against real sentences, not as facts with the same
evidentiary weight as the verb-class lists.

## Citations (verified count: 13 sources with content directly fetched/confirmed + 6 additional sources
identified via search with claims cross-corroborated across >=2 independent search results)

Directly fetched/confirmed (full or substantial content retrieved):
1. Belletti, A. & Rizzi, L. (1988). "Psych-verbs and theta theory." *Natural Language and Linguistic Theory*
   6:291-352.
2. Levin, B. (1993). *English Verb Classes and Alternations: A Preliminary Investigation*. University of
   Chicago Press. [class structure + VerbNet operationalization]
3. VerbNet class amuse-31.1 (cs.rochester.edu/~gildea/VerbNet) -- member list, frames, roles, fetched directly.
4. VerbNet class admire-31.2 (verbs.colorado.edu) -- 47-member list, frames, roles, fetched directly.
5. Pesetsky, D. (1995). *Zero Syntax: Experiencers and Cascades*. MIT Press. [causal vs. target-of-emotion
   distinction]
6. Landau, I. (2010). *The Locative Syntax of Experiencers*. Linguistic Inquiry Monographs 53, MIT Press.
7. Hartshorne, J.K., O'Donnell, T.J. & Tenenbaum, J.B. "Psych verbs, the linking problem, and the acquisition
   of language." *Cognition* (PMC5143181, fetched in full).
8. Maratsos, M., Fox, D.E.C., Becker, J.A. & Chalkley, M.A. (1985). "Semantic restrictions on children's
   passives." *Cognition* 19(2):167-191.
9. Thompson, C.K. & Lee, M. (2009). "Psych verb production and comprehension in agrammatic Broca's aphasia."
   *Journal of Neurolinguistics* (PMC2824436, fetched in full for exact accuracy figures).
10. Brennan, J. & Pylkkanen, L. (2010). "Processing psych verbs: Behavioural and MEG measures of two different
    types of semantic complexity." *Language and Cognitive Processes* 25(6):777-807.
11. Gattei, C., Dickey, M.W., Wainselboim, A.J. & Paris, L. (2015). "The thematic hierarchy in sentence
    comprehension: A study on the interaction between verb class and word order in Spanish." *Quarterly
    Journal of Experimental Psychology*.
12. PropBank frameset "fear" (verbs.colorado.edu/propbank) -- Arg0/Arg1 definitions, fetched directly.
13. PropBank frameset "frighten" (verbs.colorado.edu/propbank) -- Arg0/Arg1 definitions, fetched directly.

Identified/corroborated via search (not independently full-text fetched, but content cross-corroborated across
>=2 independent search snippets):
14. Baker, M. (1988) UTAH -- Uniformity of Theta Assignment Hypothesis.
15. MacDonald, M.C., Pearlmutter, N.J. & Seidenberg, M.S. (1994). "The lexical nature of syntactic ambiguity
    resolution." *Psychological Review*.
16. Grimshaw, J. (1990). *Argument Structure*. MIT Press. [causal analysis of fear vs. frighten stimulus;
    nominalization argument-structure preservation]
17. Bosse, S., Bruening, B. & Yamada, M. (2012). "Affected experiencers." *Natural Language & Linguistic
    Theory* 30(4):1185-1230.
18. Jackendoff, R. (1972). *Semantic Interpretation in Generative Grammar*. MIT Press. [subject-oriented
    adverbs]
19. Gattei, C., Vasishth, S. & Dickey, M. (2010 conference work, precursor to entry 11). Self-paced reading,
    Spanish object-experiencer verbs.

Note per lit-scan calibration discipline: item 3's "biorxiv verb-specific-linking N400" hit was located but
returned only binary PDF stream on fetch (unreadable) -- NOT counted in the verified citations above; flagging
it only as an existence pointer for a future drill, not as evidence used in this note.

## TLDR

We looked up how English sentences signal WHO feels an emotion. For most emotion words this is basically a
vocabulary question: some words put the feeler first ("Mary feared the dog" -- Mary feels it), other very
common words put the feeler second ("The dog frightened Mary" -- Mary still feels it, even though "dog" comes
first). We found solid, well-tested lists of which common emotion words belong to which group, plus simple
rules for related phrasings (descriptions like "was afraid," "spoke angrily," "to her delight," "her fear").
Scientists have also shown, with real reading-time and brain-response experiments and studies of people with
language-related brain damage, that the "feeler comes second" words are measurably harder to process and are
more likely to trip up a damaged or still-developing language system -- which matches what we'd want an
automatic extractor to also expect and handle carefully. A few words genuinely swing both ways ("worry,"
"concern") and need a bit more than a plain word list.

## QUESTIONS

None.

## NEXT STEPS

1. Hand the two verb-class lists (SS1) to whoever owns the subcategorization-frame / argument-structure
   extraction organ as a direct lexicon addition (a SUBJ_EXP / OBJ_EXP / DAT_EXP / ALTERNATING flag per verb).
2. Build the cheap decisive test set (SS "Cheap decisive test") before any new code is written, so the
   HARD-PASS/HARD-FAIL thresholds above are actually checked against real sentences, not assumed.
3. Treat the two OUR-INVENTION-UNDER-TEST synthesis links (object-experiencer-adverb caveat; metaphor-noun-to-
   Landau-locative connection) as flagged hypotheses in whatever downstream design doc cites this note --
   they are reasonable but not directly evidenced in a single paper the way the verb-class lists are.
4. If a follow-up 2x-research drill is warranted, the highest-value next question is the alternating-verb
   disambiguation problem (worry/concern/grieve/anger) -- that is where the literature is thinnest and where
   the extractor is most likely to need something beyond lookup.
