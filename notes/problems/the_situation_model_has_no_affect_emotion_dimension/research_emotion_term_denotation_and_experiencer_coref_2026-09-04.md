Research note: emotion-term DENOTATION vs ASSOCIATION (gate design) + experiencer-PRONOUN binding (coref fallback)

date: 2026-09-04
scope: notes/problems/the_situation_model_has_no_affect_emotion_dimension/
author: research sub-agent (self-search, no sub-agent fan-out, per task instruction)
calibration: lit-scan penalty applied per [[feedback-lit-scan-calibration-penalty]] -- P estimates
deflated 0.15-0.25 off the raw literature-convergence read; novel-synthesis P capped at 0.50.
companion notes in this same folder (read first if you have not): research_affect_emotion_brain_mechanism_2026-09-04.md
(valence-primary/category-secondary architecture) and research_experiencer_psych_verb_brain_mechanism_2026-09-04.md
(per-verb subject-experiencer vs object-experiencer argument structure, Levin/VerbNet/PropBank).
THIS NOTE SITS ON TOP OF THE SECOND ONE: that note tells you WHICH GRAMMATICAL SLOT in a clause
holds the experiencer for a given verb (deterministic, lexical). This note is about what to do when
that slot is filled by a PRONOUN and you need to know WHICH CHARACTER it refers to (probabilistic,
discourse-level).

======================================================================
HEADLINE
======================================================================

(1) The denotation/association distinction you are implementing is not an ad hoc engineering
choice -- it is an established, 20+ year old line in affective psycholinguistics ("emotion-label
words" vs "emotion-laden words": Pavlenko 2008; Altarriba & Bauer 2004; Altarriba & Basnight-Brown),
it dissociates NEURALLY (ERP: larger N170 and LPC for emotion-label than emotion-laden words --
Zhang, Wu, Meng & Yuan 2017, replicated in a 2024 bilingual ERP study), and it is EXACTLY what
WordNet-Affect (Strapparava & Valitutti 2004) was built to isolate: a curated a-label subset of
WordNet synsets for actual emotional/affective concepts, further marked STATIVE (felt by the
experiencer, e.g. "afraid") vs CAUSATIVE (a property of the stimulus, e.g. "frightening") on the
adjective sub-hierarchy -- which is your gate's exact denotation/evocation line, already annotated
by hand in a published resource. PINNED, P=0.75 (deflated from a near-1.0 raw read; this is
converging, multiply-replicated lexical-semantic + neurolinguistic evidence, not a single study).

(2) For pronoun-to-antecedent binding, the brain-relevant account is Centering Theory (Grosz,
Joshi & Weinstein 1995) plus its empirically-tuned refinements (Gordon, Grosz & Gilliom 1993;
Gordon & Chan 1995; Gernsbacher 1989; Arnold's probabilistic multi-constraint account) -- a
SALIENCE RANKING, not a search: grammatical subject/topic (backward-looking center) outranks
object outranks oblique, recency and role-PARALLELISM sharpen the ranking, and repeating a name
where a pronoun was expected measurably slows readers ("repeated name penalty"), which is direct
behavioral evidence the brain is tracking exactly this ranked list. For the specific case of an
emotion-experiencer pronoun, there is an ADDITIONAL brain-relevant cue not available for ordinary
pronouns: IMPLICIT CAUSALITY verb bias (Garvey & Caramazza 1974; Ferstl, Garnham & Manouilidou 2011,
a norm-collected corpus of 300+ verbs including most psych/emotion predicates) -- many emotion verbs
carry a strong, measured, per-verb bias toward attributing subsequent reference to a SPECIFIC
argument (stimulus vs experiencer), which is a free, lexicon-driven disambiguator that stacks with
Centering's structural ranking. PINNED cue hierarchy given below. P=0.55 (deflated; Centering itself
is very well established, the specific claim that IC bias should be layered in as a coref fallback
for THIS use case is my synthesis, capped at the novel-synthesis ceiling).

Cheap decisive test for both: see section 5.

======================================================================
1. IS THE DENOTATION-vs-ASSOCIATION DISTINCTION ESTABLISHED? (yes, with citations)
======================================================================

STATUS: PINNED-BY-EVIDENCE.

Primary citation -- Pavlenko, A. (2008). "Emotion and emotion-laden words in the bilingual lexicon."
Bilingualism: Language and Cognition, 11(2), 147-164.
- Distinguishes three word classes in the affective lexicon: EMOTION WORDS (also called
  "emotion-label words" in later literature) that directly NAME an emotion -- happy, afraid, angry --
  vs EMOTION-LADEN WORDS that carry emotional connotation without naming an emotion -- death, wedding,
  shark, prison, puppy -- vs neutral words. Pavlenko argues emotion words need their own
  representational treatment in the mental lexicon, distinct from both abstract and concrete words.
  This is your NRC-failure-mode exactly: "war," "death," "money," "mother," "married," "time" are
  emotion-LADEN (associative), not emotion-label (denotative).

Second citation -- Altarriba, J. & Bauer, L. M. (2004). "The distinctiveness of emotion concepts: a
comparison between emotion, abstract, and concrete words." American Journal of Psychology, 117(3),
389-410. And Altarriba, J., Bauer, L. M., & Benvenuto, C. (1999), Behavior Research Methods,
Instruments & Computers, 31(4), 578-602 (norming study).
- Independently establishes the same class: emotion words (happy, anxious) show distinct priming
  and recall profiles vs abstract and concrete words; emotion-laden words are a separate category
  again (dream, shark). Emotion words had the highest number of free associations of the three
  classes -- a distinctiveness signature, not just a labeling convenience.

Third citation (dedicated emotion-word vs emotion-laden-word comparison) -- Altarriba & Basnight-
Brown lines of work (e.g. "The representation of emotion vs. emotion-laden words in English and
Spanish," Affective Simon Task studies): direct behavioral dissociation -- negative EMOTION words
produce the typical valence-congruency ("Affective Simon") effect, while emotion-LADEN words (both
polarities) produce a different effect pattern. This is a processing dissociation, not just a
lexicographic one.

Neural dissociation (answers your "is it brain-relevant" question directly) -- Zhang, J., Wu, C.,
Meng, Y., & Yuan, Z. (2017). "Different Neural Correlates of Emotion-Label Words and Emotion-Laden
Words: An ERP Study." Frontiers in Human Neuroscience, 11:455 (+ 2017 corrigendum, same volume,
article 589). Lexical-decision ERP study:
- P100 (early, posterior): NO difference between the two word types.
- N170 (early-intermediate, right occipital): LARGER for emotion-label words than emotion-laden
  words.
- LPC / Late Positivity Complex (late, semantic-integration stage): negative emotion-label words
  produced a right-lateralized LPC effect that negative emotion-laden words and positive words of
  either type did NOT produce.
- Interpretation offered by the authors: emotion-label words EXPLICITLY denote a felt state and
  so are integrated as such; emotion-laden words only IMPLICITLY connote emotion via associated
  concepts, and the brain's later semantic-integration stage treats them differently.
A 2024 follow-up (late Chinese-English / other bilingual populations, PubMed 38738622) replicates
the emotion-label vs emotion-laden ERP dissociation cross-linguistically, and a companion 2019
"emotion conflict" ERP paper (Exp Brain Res) further differentiates the two word types under
Stroop-like conflict, i.e. this is a small but real and replicating sub-literature, not one-off.

CAVEAT (per [[feedback-strategic-reads-run-ahead-of-evidence]]): all of the neural evidence above
comes from lexical-decision tasks on isolated words (mostly Chinese two-character compounds in the
2017 study), not continuous narrative reading. The generalization "this dissociation holds during
narrative comprehension of English text" is plausible but NOT the thing that was directly measured.
Treat the ERP citation as evidence the distinction is REAL AND EARLY (pre-150ms differences), not as
proof it operates identically inside a reading pipeline.

PINNED PRINCIPLE (your framing, connected to formal semantics -- this specific formulation is MY
synthesis, flagged as such, capped P=0.50 as novel-synthesis, though each piece it connects is
independently well-established):

  An emotion word DENOTES a (temporary) AFFECTIVE STATE OF AN EXPERIENCER -- a STAGE-LEVEL predicate
  in the sense of Carlson (1977, "Reference to Kinds in English"): true of an individual AT A TIME,
  like "hungry" or "available," not a lasting property of the individual. "Afraid," "angry," "glad"
  pattern with stage-level predicates (episodic, time-bound, licensed in "there"-existentials'
  cousins like locative/temporal modification: "she was afraid THEN," "afraid AT THAT MOMENT").
  This is distinct from two other classes NRC conflates with it:
    (a) an EVALUATIVE property of an object/event -- individual-level, describes the STIMULUS's
        quality, not the experiencer's state: "excellent," "wonderful," "great," "terrible." These
        answer "what kind of thing is X," not "how does the experiencer feel."
    (b) an EMOTION-ASSOCIATED CONCEPT -- a noun/event that correlates with an emotion in the world
        but requires an extra world-knowledge inference to attribute a SPECIFIC felt state to a
        SPECIFIC experiencer: "war," "death," "wedding," "money," "mother." NRC's association method
        (crowd word-association norming) captures exactly this evocative halo, which is why it fires
        on all of them -- it was never designed to test denotation, only co-occurring association.
  Gate on (a subset of) stage-level, experiencer-denoting terms only; exclude (a) and (b).

======================================================================
2. WORDNET-AFFECT (Strapparava & Valitutti 2004): confirmed as the right resource
======================================================================

STATUS: PINNED-BY-EVIDENCE (confirmed directly from the resource's own documentation page,
wndomains.fbk.eu/wnaffect.html, and the LREC 2004 paper, ACL Anthology L04-1208).

What it is: a hand-built extension of WordNet where a SUBSET of WordNet synsets (roughly ~1000+
lemmas across the labeled synsets) is manually assigned one of a hierarchy of ~300 "a-labels"
(affective labels). This is the opposite construction method from NRC: NRC is built from
CROWD-SOURCED WORD ASSOCIATION (Mechanical Turk workers naming which of 8-10 emotions a word makes
them think of -- an association/evocation method by design), while WordNet-Affect is EXPERT-CURATED
SYNSET LABELING against a fixed emotion-concept hierarchy (a denotation method by design). This
methodological difference is exactly why NRC over-fires on "money"/"war"/"time" and WordNet-Affect
does not: NRC's collection method cannot distinguish "makes me think of fear" from "means fear."

Top-level a-label hierarchy (11 categories, confirmed): EMOTION, MOOD, TRAIT, COGNITIVE STATE,
PHYSICAL STATE, HEDONIC SIGNAL, EMOTION-ELICITING SITUATION, EMOTIONAL RESPONSE, BEHAVIOUR, ATTITUDE,
SENSATION. This is itself a usable filter: for a strict "denotes a felt emotional STATE" gate, you
want the EMOTION category (and arguably MOOD) and NOT trait (personality, individual-level: "brave,"
"generous"), not attitude (belief-tinged stance: "hostile," "admiring" lean attitude), not
emotion-eliciting-situation (that IS the association-only class you're trying to exclude), not
cognitive-state/physical-state/sensation (adjacent but not affect proper).

EMOTION category is further split by VALENCE into positive / negative / ambiguous / neutral
(surprise sits in "ambiguous" -- valence depends on context, which is itself a useful modeling fact:
surprise denotes an arousal spike without a fixed valence sign).

The single most useful structural fact for your gate, confirmed directly from the documentation:
WordNet-Affect marks a STATIVE / CAUSATIVE distinction on the adjective sub-hierarchy -- i.e. it
already separates "emotions felt BY the referent" from "emotions caused BY the referent" at the
lexical-resource level. Concretely this is your exact "afraid" (stative, experiencer-denoting, GATE
ON) vs "frightening" (causative, stimulus-property, GATE OFF / route to a different signal) split,
already hand-annotated by the resource's authors in 2004 for a different purpose (affective
computing / text classification) but structurally identical to what you need. This is strong
independent confirmation that the stative/causative (denotes-a-state-of-the-experiencer vs
describes-a-property-of-the-stimulus) cut is not just your invention -- it is a recognized, separately
citable structural fact about English emotion-adjective morphology, and it generalizes beyond
WordNet-Affect's specific label set (see Section 3, "causative-only" column, which follows this same
logic for terms outside WNA's exact coverage).

Recommendation: use WordNet-Affect's EMOTION (+ optionally MOOD) a-label subset, filtered to stative
forms on the adjective side, as your primary DENOTES-EMOTION gate; treat NRC purely as an
association/priming signal for a DIFFERENT downstream purpose (e.g. detecting emotionally-loaded
scene content), never as the felt-state gate. Coverage caveat: WordNet-Affect is a fixed ~2004
resource and will miss some modern/informal terms (e.g. "freaked out," "stoked") -- the manually
curated list in Section 3 below is deliberately broader than WNA's raw synset list for this reason,
built to be WNA-compatible in spirit but not restricted to WNA's exact lemma coverage.

======================================================================
3. THE EMOTION-TERM INVENTORY (paste-ready)
======================================================================

Legend: CORE = denotes an experiencer's felt state, gate ON with confidence. BORDERLINE = judgment
call, noted why; consider a lower-confidence tier rather than excluding outright. EXCLUDE = the NRC
failure mode itself (evaluative-of-object or associative-of-concept, not experiencer-denoting) --
listed for contrast, do NOT gate.

--- FEAR family ---
CORE adjectives (stative): afraid, fearful, scared, frightened, terrified, petrified, horrified,
alarmed, apprehensive, anxious, nervous, worried, uneasy, panicked, panicky, spooked, aghast, dread-
filled, shaken, unnerved
CORE nouns: fear, fright, terror, dread, horror, panic, alarm, anxiety, apprehension, trepidation,
angst, fearfulness
CORE verbs (experiencer as grammatical subject): fear, dread
BORDERLINE: timid, phobic (trait-leaning, not episodic); tremble, quake, shudder, quail (these are
PHYSIOLOGICAL SYMPTOMS/behaviors of fear, not the emotion word itself -- useful as a secondary
signal, not a primary denotation)
EXCLUDE (causative/stimulus-property companions -- keep in a SEPARATE stimulus-flagging map, not
the experiencer-affect gate): frightening, terrifying, scary, alarming, horrifying, horrific,
dreadful (also independently evaluative: "a dreadful mess")

--- ANGER family ---
CORE adjectives: angry, mad, furious, irate, enraged, incensed, livid, indignant, outraged, annoyed,
irritated, exasperated, cross, fuming, seething, wrathful
CORE nouns: anger, rage, fury, wrath, ire, indignation, outrage, annoyance, irritation, exasperation
CORE verbs: seethe, fume, resent
BORDERLINE: resentful, hostile, animosity, hostility (these lean ATTITUDE/trait -- durable stance
toward someone -- rather than an episodic emotional state; include only with lower confidence)
EXCLUDE (causative): infuriating, maddening, annoying, irritating, exasperating, aggravating

--- SADNESS family ---
CORE adjectives: sad, unhappy, miserable, sorrowful, mournful, grief-stricken, heartbroken, downcast,
dejected, despondent, gloomy, melancholy, melancholic, forlorn, wretched, desolate, crestfallen,
disconsolate, woeful, blue (informal), heartsick
CORE nouns: sadness, sorrow, grief, misery, despair, melancholy, gloom, dejection, despondency,
heartbreak, anguish, woe, unhappiness
CORE verbs: grieve, mourn, despair
BORDERLINE: depressed (clinical/trait sense competes with episodic-state sense -- context-dependent);
weep, cry, sob (physiological/behavioral symptom of sadness, like tremble for fear -- secondary
signal not primary denotation); lament (also a speech-act sense, "to lament that...")
EXCLUDE (causative): saddening, depressing, heartbreaking, distressing
NOTE: "sad" itself has a dual use -- stative ("I am sad") vs evaluative-of-object ("a sad film,"
"a sad state of affairs"). Keep as CORE but flag the dual-use ambiguity; disambiguate by checking
whether the head noun is an animate experiencer or an inanimate object/event.

--- JOY / HAPPINESS family ---
CORE adjectives: happy, glad, joyful, joyous, cheerful, delighted, elated, ecstatic, thrilled,
jubilant, gleeful, merry, buoyant, blissful, content, contented, satisfied, gratified, excited,
pleased, proud (see also PRIDE family)
CORE nouns: joy, happiness, delight, elation, glee, cheer, bliss, jubilation, ecstasy, contentment,
gladness, euphoria, gratification, excitement
CORE verbs: rejoice, exult, delight (in) ("she delighted in the news" -- experiencer-subject sense)
BORDERLINE: gloat (blends joy + a superiority/contempt component -- schadenfreude); relieved, relief
(arguably its own minor family -- resolution of a prior fear/tension state; include as CORE, it is a
clearly denoting, felt, experiencer-bound state)
EXCLUDE (causative): delightful, pleasing, gratifying, thrilling, exciting (note: "excited" is CORE
stative, "exciting" is the causative/stimulus-property adjective -- same root, opposite gate status)
EXCLUDE (pure evaluative, THE classic NRC-over-fire case, never gate): excellent, wonderful, great,
fantastic, terrific, superb, marvelous, awesome (evaluates the STIMULUS's quality; does not report
the experiencer's felt state even when it correlates with one)

--- DISGUST family ---
CORE adjectives: disgusted, revolted, repulsed, nauseated, sickened, grossed-out (informal)
CORE nouns: disgust, revulsion, repugnance, loathing, distaste, aversion
BORDERLINE: appalled (blends disgust + anger/moral outrage); loathe, abhor, detest, despise (attitude-
leaning, durable stance rather than episodic feeling, similar caveat to "hate"); nausea (physical-
state a-label in WordNet-Affect terms, not emotion proper, though tightly coupled)
EXCLUDE (causative): disgusting, revolting, repulsive, nauseating, repugnant, sickening, gross
(informal, also independently evaluative)

--- SURPRISE family ---
CORE adjectives: surprised, astonished, amazed, astounded, stunned, shocked, startled, dumbfounded,
flabbergasted, taken aback
CORE nouns: surprise, astonishment, amazement, shock
BORDERLINE: bewildered, bewilderment (blends confusion, a cognitive-state a-label, not pure emotion);
wonder, awe (blend surprise + admiration/reverence; WordNet-Affect's "ambiguous valence" note applies
directly here)
EXCLUDE (causative): surprising, astonishing, amazing, shocking, startling, stunning

--- TRUST / LOVE family (Plutchik's "trust"; OCC's Attraction group) ---
CORE adjectives: loving, affectionate, fond, devoted, adoring, smitten, enamored
CORE nouns: love, affection, adoration, fondness, devotion, infatuation, tenderness
CORE verbs: love, adore, cherish
BORDERLINE (flag prominently -- this is the family closest to NRC's own worst failure mode):
trust, trusting, confident, secure -- these are largely EPISTEMIC/ATTITUDINAL stances (a belief
about reliability) rather than an episodic felt emotion; admire, admiration (blends respect/cognitive
appraisal with positive affect). Recommend: EXCLUDE bare "trust" from a strict felt-state gate unless
paired with an explicit feeling-verb frame ("she felt a rush of trust"); this directly targets the
NRC "father"->trust failure mode you named.

--- ANTICIPATION family (Plutchik) -- MOST BORDERLINE OF ALL, treat as mostly EXCLUDE ---
CORE-ish (weak): hopeful, hope, eager, eagerness
EXCLUDE (the exact NRC "time"->anticipation failure mode -- these are cognitive/temporal-orientation
words, not felt-affect words): anticipation, anticipate, expect, expectant, expectation
Recommendation: drop "anticipation"/"anticipate" from the gate entirely; keep only hope/hopeful/
eager/eagerness, which do denote a genuine (if mild) positive affective state.

--- SHAME / GUILT family (self-conscious emotions; OCC "Attribution" group; not in Ekman-6 but
essential for narrative character affect) ---
CORE adjectives: ashamed, guilty, embarrassed, humiliated, mortified, remorseful, contrite,
shamefaced, sheepish
CORE nouns: shame, guilt, embarrassment, humiliation, remorse, contrition, mortification
BORDERLINE: regret, regretful (blends a cognitive counterfactual judgment with the affect); repent,
repentant (more volitional/behavioral than purely affective)

--- PRIDE family (self-conscious, positive) ---
CORE adjectives: proud, triumphant
CORE nouns: pride, triumph
BORDERLINE: smug (blends satisfaction + superiority, near-pejorative); vain, vanity (trait-leaning)

--- JEALOUSY / ENVY family ---
CORE adjectives: jealous, envious
CORE nouns: jealousy, envy
CORE verb: envy
BORDERLINE: covetous, covet (blends desire, not pure emotion)

--- LONELINESS / LONGING family (common in narrative, outside all six major taxonomies) ---
CORE adjectives: lonely, homesick
CORE nouns: loneliness, homesickness, longing
BORDERLINE: yearn (for), long (for), crave (blend desire + an affective ache; include as CORE if the
product wants longing represented, since it is genuinely experiencer-bound and felt, not merely
evaluative)

--- BOREDOM / CALM (low-arousal states, often omitted from basic-emotion lists but real) ---
CORE adjectives: bored, calm, relaxed, serene, at ease
CORE nouns: boredom, calm, serenity
BORDERLINE: apathetic, apathy (blends a cognitive/motivational deficit with low affect)

--- EXPLICITLY EXCLUDE -- the generalizable NRC-failure class, restated as a closed rule rather
than a word list, plus the paradigm-case words you named ---
(a) Evaluative-of-object/event, not experiencer-denoting: excellent, wonderful, great, terrible,
    awful, horrible, amazing, fantastic (these ARE gated correctly in a sentiment/valence system,
    just not in an experiencer-affect system).
(b) Emotion-associated concept nouns requiring a world-knowledge leap to attribute a felt state to
    a specific person: money, war, death, marriage, married, mother, father, friends, time, wedding,
    funeral, birthday, prison, gift. These evoke emotion at the CONCEPT level (statistically, across
    many texts) but say nothing about whether THIS experiencer, in THIS sentence, felt anything, let
    alone what.

Suggested lexicon schema for a solver (flat, paste-ready shape):
  term -> {pos: adj|noun|verb, family: fear|anger|sadness|joy|disgust|surprise|trust|anticipation|
  shame|pride|jealousy|longing|calm, gate: core|borderline, stance: stative|causative|na,
  polarity: neg|pos|ambiguous}
Populate `gate: core` rows first (the CORE lists above, ~140 terms before verbs/borderlines,
~190-210 including verbs and the flagged borderlines you choose to keep at reduced confidence).

======================================================================
4. Q2: HOW THE BRAIN BINDS AN EXPERIENCER PRONOUN TO ITS ANTECEDENT
======================================================================

STATUS: PINNED-BY-EVIDENCE for the general salience-hierarchy account; the specific IC-bias-as-
fallback-for-emotion-predicates layering is novel synthesis (capped P=0.50).

4.1 Centering Theory -- the core structural account
Grosz, B. J., Joshi, A. K., & Weinstein, S. (1995). "Centering: A framework for modeling the local
coherence of discourse." Computational Linguistics, 21(2), 203-225.
- Every utterance U_n has a ranked list of FORWARD-LOOKING CENTERS, Cf(U_n) -- all discourse
  entities it introduces, ranked by grammatical role: SUBJECT > OBJECT > OTHER (obliques, PPs).
  The highest-ranked is the "preferred center," Cp.
- U_n also has exactly one BACKWARD-LOOKING CENTER, Cb(U_n): the highest-ranked entity of Cf(U_n-1)
  that is realized (mentioned again) in U_n. This is the entity the utterance is "about" -- the
  discourse topic in a formal sense.
- Rule 1 ("pronoun rule"): if any element of Cf(U_n) is pronominalized, the Cb(U_n) MUST be
  pronominalized too. Practically: if you are going to use a pronoun for anything in this sentence,
  the topic/most-salient entity gets the pronoun, and it should be interpreted as continuing to
  refer to the established topic. This directly licenses a "resolve the ambiguous pronoun to the
  established topic/Cb" default.
- Transition preference ordering (cheapest processing to most disruptive): CONTINUE > RETAIN >
  SMOOTH-SHIFT > ROUGH-SHIFT. A reader/hearer prefers continuations that keep the same Cb as
  subject across sentences; a shift is a real, measurable processing cost.

4.2 Behavioral confirmation -- the "repeated name penalty"
Gordon, P. C., Grosz, B. J., & Gilliom, L. A. (1993). "Pronouns, names, and the centering of
attention in discourse." Cognitive Science, 17(3), 311-347.
- Reading times are SLOWER when a highly salient, continuing topic (the Cb) is referred to with a
  REPEATED NAME instead of a pronoun ("the repeated name penalty") -- direct behavioral evidence
  that readers maintain a ranked salience structure and expect the top-ranked entity to be
  pronominalized, exactly as Centering predicts. This is the single strongest piece of evidence that
  Centering's ranking is not just a linguist's formalism but something real readers compute online.

4.3 Grammatical-role PARALLELISM (independent of thematic role)
Gordon, P. C., & Chan, D. (1995). "Pronouns, passives, and discourse coherence." Journal of Memory
and Language, 34(2), 216-231.
- The repeated-name penalty (and by extension the pronoun preference) attaches to the entity in the
  SAME GRAMMATICAL ROLE (subject) across sentences, INDEPENDENT of its thematic/semantic role --
  i.e. even when an active-to-passive shift changes who is agent vs patient, readers still prefer to
  continue reference with the current grammatical subject. This is the PARALLELISM cue: an ambiguous
  pronoun is preferentially resolved to the antecedent that occupied the SAME grammatical role in the
  preceding clause (subject-to-subject, object-to-object), a separate and additive cue from raw
  subject-salience. (Later replicated for German: "Grammatical Role Parallelism Influences Ambiguous
  Pronoun Resolution in German," Frontiers in Psychology 2017, PMC5524765 -- cross-linguistic
  robustness.)

4.4 Suppression / enhancement and first-mention advantage
Gernsbacher, M. A. (1989). "Mechanisms that improve referential access." Cognition, 32(2), 99-156.
Gernsbacher, M. A., & Hargreaves, D. J. (1988). "Accessing sentence participants: the advantage of
first mention." Journal of Memory and Language, 27(6), 699-717.
- Two complementary memory mechanisms: ENHANCEMENT boosts activation of a just-re-mentioned
  antecedent; SUPPRESSION dampens activation of competing (non-antecedent) entities. A pronoun that
  is gender/number-DISCRIMINATING (matches only one candidate) triggers suppression of the other
  candidate FASTER and more strongly than an ambiguous pronoun -- i.e. hard morphological
  constraints (gender/number agreement) are applied first and fast, before softer salience cues
  finish resolving ties.
- Independently, the FIRST-MENTIONED participant in a sentence is more accessible than the second-
  mentioned one, even controlling for grammatical subjecthood -- an additional, partially independent
  recency/primacy-within-clause cue.

4.5 Probabilistic multi-cue integration (the realistic, non-categorical picture)
Arnold, J. E. (and Kehler, Kertz, Rohde, Elman -- the "Bayesian/expectancy" line, e.g. Kehler et al.
2008 "Coherence and coreference revisited," and Arnold 1998/2001 on thematic-role effects on
pronoun/reference-form choice): salience is not one binary cue but a WEIGHTED COMBINATION of
recency, grammatical role/subjecthood, thematic role, syntactic parallelism, and
givenness/discourse-topic status, integrated probabilistically rather than by a single hard rule.
This is the realistic brain-level picture Centering approximates categorically: treat the cues
below as ADDITIVE evidence, not a strict lexicographic ordering, though the ordering below is the
right PRIORITY when cues conflict and a single answer is needed cheaply.

4.6 PINNED cue hierarchy (synthesis across 4.1-4.5, ordered by priority for a cheap resolver)
  0. HARD FILTER FIRST: gender/number/animacy agreement -- eliminate any candidate the pronoun
     morphologically cannot refer to (Gernsbacher: this is fast and applied before soft ranking).
  1. RECENCY: prefer the most recently mentioned matching candidate (most local antecedent).
  2. GRAMMATICAL ROLE / subjecthood: prefer the candidate that was the SUBJECT of the immediately
     preceding clause (Centering's Cb-ranking; the repeated-name-penalty evidence).
  3. PARALLELISM: prefer the candidate whose grammatical role in the prior clause MATCHES the
     pronoun's role in the current clause (subject-pronoun prefers prior subject, object-pronoun
     prefers prior object), even when this cuts against raw thematic salience (Gordon & Chan 1995).
  4. PROTAGONIST / GLOBAL TOPIC SALIENCE: prefer the entity that has been the dominant Cb / most-
     repeated subject across the current discourse segment (the "main character" of the current
     scene), when cues 1-3 tie or are weak (Centering's segment-level Cb chain; also converges with
     situation-model "protagonist" tracking, Morrow/Greenspan/Bower and Zwaan & Radvansky's
     event-indexing "protagonist" dimension, already cited in the companion affect-mechanism note).
  5. (Emotion-predicate-specific, see 4.7) IMPLICIT CAUSALITY verb bias, when the predicate itself
     is a psych/emotion verb with a norm-collected bias -- this can override or sharpen 1-4 for the
     specific case this problem is about.

4.7 Implicit causality: a free, per-verb disambiguator specific to emotion/psych predicates
Garvey, C., & Caramazza, A. (1974). "Implicit causality in verbs." Linguistic Inquiry, 5(3), 459-464.
Ferstl, E. C., Garnham, A., & Manouilidou, C. (2011). "Implicit causality bias in English: a corpus
of 300 verbs." Behavior Research Methods, 43(1), 124-135.
- IC verbs split (per your companion note's Belletti & Rizzi / Levin / VerbNet classes) into
  STIMULUS-EXPERIENCER ("frighten," "annoy," "amuse," "delight," "anger" -- experiencer = OBJECT)
  and EXPERIENCER-STIMULUS ("fear," "love," "admire," "envy," "pity" -- experiencer = SUBJECT)
  verbs. Garvey & Caramazza's classic finding, replicated and extended with norms for 300+ verbs by
  Ferstl et al.: when a sentence with such a verb is continued with "because," respondents
  overwhelmingly attribute the causing/explaining clause to a PREDICTABLE argument depending on verb
  class -- typically the STIMULUS argument for stimulus-experiencer verbs (NP1 bias) and the
  EXPERIENCER for experiencer-stimulus verbs (NP2 bias), though the exact split is verb-specific and
  the corpus gives per-verb percentages rather than a clean binary rule.
- WHY THIS MATTERS FOR YOUR COREF PROBLEM SPECIFICALLY: this bias is not just about "because"-
  clauses -- Stevenson, Crawley & Kleinman (1994, "Thematic roles, focus, and the representation of
  events," Language and Cognitive Processes) showed IC bias and grammatical role/thematic role
  JOINTLY predict which entity a subsequent pronoun (not just a because-clause) is preferentially
  understood to continue reference to. So for a sentence like "Tom frightened Bill. He was still
  shaking an hour later," the verb "frighten" (stimulus-experiencer, object-experiencer class)
  carries a norm-measurable bias toward attributing the FOLLOWING clause's subject pronoun to the
  EXPERIENCER (Bill, the object of "frighten") rather than the stimulus (Tom) -- distinct from
  (and sometimes in tension with) the plain subject-preference default in 4.6 rule 2, which would
  otherwise favor Tom. This is a genuine additional, brain-relevant, per-verb-lexicalized cue,
  available for free once you have the psych-verb class table your companion note already built.
- Ferstl et al. 2011's 300+-verb corpus with per-verb bias percentages is directly reusable: it is a
  free numeric prior, keyed by verb, that can weight candidate 4.6 rule 2/3 ties without any new
  annotation effort -- most emotion verbs in your Section 3 inventory that have a transitive
  stimulus-experiencer or experiencer-stimulus reading (frighten, delight, sadden, anger, annoy,
  scare, fear, love, admire, envy, pity, dread...) are IN that corpus or in the same VerbNet classes
  the corpus covers.

4.8 Cheap, brain-faithful fallback for uncertain coref (direct answer to your question)
When full coreference resolution is uncertain (confidence below threshold), bind the emotion-
experiencer pronoun to:
  (a) the current discourse CENTER (Cb) of the active segment -- operationally, the entity that has
      been the grammatical SUBJECT of the most recent 1-2 clauses and/or the most-repeated subject
      across the current scene/paragraph (the "protagonist" default), per Centering Theory's Rule 2
      transition preference (CONTINUE is cheapest/most expected) and Gordon-Grosz-Gilliom's
      repeated-name-penalty evidence that this is what readers actually expect; THEN
  (b) if the predicate is a psych/emotion verb with a known IC bias (Ferstl et al. 2011 lookup),
      let that bias ADJUST the default toward the experiencer argument specifically when the verb
      class is stimulus-experiencer (the class where "who is the experiencer" and "who is
      grammatically prominent" diverge -- exactly your "it frightened her" pattern, where the
      experiencer is the OBJECT, not the salient subject).
This is cheap (no full coref machinery needed -- just a running "current subject/topic" pointer plus
a per-verb IC-bias lookup table) and is directly grounded in (a) the best-established structural
account of discourse salience in psycholinguistics and (b) a norm-collected, freely reusable verb
resource that already exists for exactly the predicate class your problem is about.

======================================================================
5. CHEAP DECISIVE TEST
======================================================================

For Q1 (denotation gate): take the sentence set that motivated this request (the NRC over-fire
cases: "war"->fear, "death"->sadness, "money"->joy, "friends"->joy, "married"->joy, "mother"->joy,
"father"->trust, "time"->anticipation, "excellent"->joy). Run the Section-3 CORE-only gate against
the same sentences. HARD-PASS threshold: the gate fires ZERO of these 9 false positives while still
firing on a held-out set of >=20 sentences containing genuine emotion-label terms (afraid, furious,
delighted, ashamed, etc.) with recall >=0.85. HARD-FAIL threshold: if recall on genuine emotion-label
sentences drops below 0.60 to achieve the false-positive elimination (i.e. the gate over-corrected
into being too narrow to be useful), or if more than 1 of the 9 named false positives still fires.

For Q2 (coref fallback): on a small hand-built test set (~30-50 sentences) of the pattern "PRONOUN
+ emotion-predicate" where the true antecedent is known, compare (i) current coref system alone
(baseline, ~61% correct per your stated 39% error rate), (ii) current coref + Centering-based
protagonist fallback on low-confidence cases, (iii) (ii) + IC-bias adjustment for stimulus-
experiencer verbs. HARD-PASS threshold: (iii) improves accuracy over (i) by >=10 percentage points
with the improvement concentrated in the LOW-CONFIDENCE subset (not just noise), and outperforms
(ii) alone by >=3 points specifically on stimulus-experiencer-verb sentences (isolating the IC-bias
contribution). HARD-FAIL threshold: if (ii)/(iii) do not beat (i) on the low-confidence subset by at
least 5 points, the fallback is not adding brain-faithful signal beyond what coref already does and
the mechanism should be reconsidered (e.g. the "protagonist" heuristic may need scene-boundary
resets that this note has not specified).

======================================================================
6. CROSS-THREAD SYNTHESIS WITH PRIOR ENTRIES
======================================================================

- research_affect_emotion_brain_mechanism_2026-09-04.md established that affect is a NEURALLY
  SEPARATE situation-model dimension (double-dissociation evidence) and that VALENCE is primary/
  fast, CATEGORY is secondary/effortful (Barrett 2006/2016; Lindquist et al. 2012). This note's
  Section 3 inventory is exactly the lexical trigger set for populating the CATEGORY field in that
  design -- gate on CORE denoting terms to license a category label; let non-gated but valenced
  content (the EXCLUDE list, or NRC-style broad valence) populate the coarser VALENCE-only field when
  no category term is present. This operationalizes the "category only when conceptually licensed"
  design principle from that note directly.
- research_experiencer_psych_verb_brain_mechanism_2026-09-04.md established the per-verb structural
  experiencer/stimulus argument mapping (subject-experiencer vs object-experiencer classes,
  Belletti & Rizzi 1988 / Levin 1993 / VerbNet / PropBank) -- PINNED-BY-EVIDENCE as a lexical fact,
  not a syntactic default. This note's Section 4 takes that mapping as GIVEN and adds the layer on
  top: when the experiencer SLOT (correctly identified by that note's table) is filled by a PRONOUN,
  Centering Theory + IC-bias tell you WHICH DISCOURSE ENTITY that pronoun refers to. The two notes
  compose: verb-class table -> which argument is the experiencer -> if that argument is pronominal,
  Section 4's cue hierarchy -> which character.

======================================================================
7. SUBSTRATE-PRODUCT IMPLICATIONS
======================================================================

In plain terms: right now the system flags a character as "feeling joy" whenever a word like
"money," "mother," or "married" appears near them, because the word list it uses (NRC) was built by
asking people what a word REMINDS them of, not what feeling the word actually NAMES. That produces
constant false alarms. Switching the gate to a curated list of words that actually NAME a feeling
(afraid, delighted, ashamed, furious -- about 150-200 words total, given in Section 3, ready to
paste into a lexicon file) should sharply cut those false alarms while keeping the real hits, because
this exact word-list-quality distinction is a matter of settled research in how psychologists study
emotion words, and there is a published, hand-built dictionary (WordNet-Affect) that already draws
the line the same way, for the same reason.

Separately, about a third of the time the system currently guesses the WRONG character for a felt
emotion, because the sentence says "she was afraid" and the system's pronoun-tracking picks the
wrong "she." The fix suggested here does not require building a new pronoun-tracker from scratch: it
is a cheap default rule modeled on how human readers actually track "who is this story mainly about
right now," plus a small, already-published table of about 300 emotion-related verbs that tells you,
for each verb, which side of the sentence (the person who feels it, or the thing that caused it) a
reader expects a follow-up pronoun to point back to. Both pieces are cheap to implement and are
backed by measured reading-time and brain-recording evidence, not just linguistic theory.

Risk of this recommendation: the emotion-term list (Section 3) will still miss some genuine emotion
expressions that use metaphor or physiological description rather than a direct emotion word (e.g.
"her stomach knotted," "he saw red") -- this note deliberately does not attempt those, since they are
a different (much harder, non-lexical) detection problem. The coref fallback (Section 4) is a
heuristic default, not a full comprehension model -- it will still misfire on scenes with rapid
protagonist switches or ensemble casts with no clear single "current topic," which is exactly the
kind of case the cheap decisive test in Section 5 needs to check before relying on it broadly.

======================================================================
8. CITATIONS (verified count: 14 distinct sources, all confirmed via direct web search this
session; none taken from memory alone)
======================================================================

1. Pavlenko, A. (2008). Emotion and emotion-laden words in the bilingual lexicon. Bilingualism:
   Language and Cognition, 11(2), 147-164.
2. Altarriba, J., & Bauer, L. M. (2004). The distinctiveness of emotion concepts: a comparison
   between emotion, abstract, and concrete words. American Journal of Psychology, 117(3), 389-410.
3. Altarriba, J., Bauer, L. M., & Benvenuto, C. (1999). Concreteness, context availability, and
   imageability ratings and word associations for abstract, concrete, and emotion words. Behavior
   Research Methods, Instruments & Computers, 31(4), 578-602.
4. Altarriba & Basnight-Brown line of work on emotion vs emotion-laden words and the Affective
   Simon Task (English/Spanish bilinguals).
5. Zhang, J., Wu, C., Meng, Y., & Yuan, Z. (2017). Different neural correlates of emotion-label
   words and emotion-laden words: an ERP study. Frontiers in Human Neuroscience, 11:455 (+
   corrigendum, article 589).
6. 2024 bilingual ERP follow-up replicating the emotion-label vs emotion-laden dissociation
   (PubMed 38738622).
7. Strapparava, C., & Valitutti, A. (2004). WordNet-Affect: an affective extension of WordNet.
   Proceedings of LREC 2004 (ACL Anthology L04-1208); resource documentation at
   wndomains.fbk.eu/wnaffect.html.
8. Carlson, G. N. (1977). Reference to kinds in English (stage-level vs individual-level predicate
   distinction; connective framing, not directly about emotion words -- my synthesis).
9. Grosz, B. J., Joshi, A. K., & Weinstein, S. (1995). Centering: a framework for modeling the
   local coherence of discourse. Computational Linguistics, 21(2), 203-225.
10. Gordon, P. C., Grosz, B. J., & Gilliom, L. A. (1993). Pronouns, names, and the centering of
    attention in discourse. Cognitive Science, 17(3), 311-347.
11. Gordon, P. C., & Chan, D. (1995). Pronouns, passives, and discourse coherence. Journal of
    Memory and Language, 34(2), 216-231.
12. Gernsbacher, M. A. (1989). Mechanisms that improve referential access. Cognition, 32(2), 99-156.
    Also Gernsbacher, M. A., & Hargreaves, D. J. (1988). Accessing sentence participants: the
    advantage of first mention. Journal of Memory and Language, 27(6), 699-717.
13. Garvey, C., & Caramazza, A. (1974). Implicit causality in verbs. Linguistic Inquiry, 5(3),
    459-464. Ferstl, E. C., Garnham, A., & Manouilidou, C. (2011). Implicit causality bias in
    English: a corpus of 300 verbs. Behavior Research Methods, 43(1), 124-135.
14. Stevenson, R. J., Crawley, R. A., & Kleinman, D. (1994). Thematic roles, focus, and the
    representation of events. Language and Cognitive Processes, 9(4), 519-548 (IC bias extended to
    pronoun continuation, not just because-clauses).

TLDR: There is a real, well-studied difference between words that NAME a feeling (afraid, joy,
furious) and words that merely REMIND people of a feeling (war, money, married) -- psychologists
have measured this difference behaviorally and in brain recordings for 20 years, and there is
already a hand-built dictionary (WordNet-Affect) that draws exactly this line. Section 3 of this
note is a ready-to-use list of about 150-200 English words that actually name a feeling, organized
by feeling-family and by whether each word describes the person feeling it or the thing causing it.
Separately, when a sentence uses "she" or "he" to say who felt an emotion, the system currently
guesses the wrong person about 4 times in 10; there is a well-established, cheap rule from reading
research for doing this better (default to whoever the passage is currently "about," adjusted by a
small published lookup table of which side of an emotion-verb the feeling belongs to), which does
not require rebuilding the whole pronoun-tracking system.

QUESTIONS: none.

NEXT STEPS: (1) paste Section 3's CORE lists into the emotion-term lexicon file and run the
Section-5 decisive test against the 9 named NRC false-positive sentences plus a held-out
genuine-emotion set. (2) build the small IC-bias lookup (a subset of the Ferstl et al. 2011 verb
list restricted to verbs already in the companion psych-verb note's subject/object-experiencer
tables) and wire it as a tie-breaker behind the existing coref system per Section 4.8, then run the
Section-5 coref decisive test on a hand-built 30-50 sentence set before considering it for the live
pipeline.
