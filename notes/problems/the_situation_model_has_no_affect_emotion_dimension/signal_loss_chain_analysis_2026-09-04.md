# The affect chain, end to end: signal-loss budget vs the brain, and the iteration

Instrument: `experiments/exp_affect_chain_signal_loss_v1.py` (oracle-substitution ladder).
Companion research: research_affect_emotion_brain_mechanism, research_experiencer_psych_verb_brain_mechanism,
research_emotion_term_denotation_and_experiencer_coref (all 2026-09-04).

## The chain (every stage brain-foundational)
    raw text
      -> POS tagger (frontend, glass-box)                         [brain: lexical categorization]
      -> parse / frame shape (arc parser; alternator transitivity) [brain: incremental parsing]
      -> emotion lexicon: DENOTATION gate (WordNet-Affect-style)   [brain: emotion-label lexicon]
         + VALENCE value (Warriner) + CATEGORY (curated family)    [brain: core affect + conceptualization]
      -> psych-verb EXPERIENCER-LINKING frame (VerbNet/PropBank)   [brain: stored argument-structure linking]
      -> coreference (bind experiencer surface -> character)       [brain: Centering / anaphora]
      -> per-character AFFECT register (overwrite dynamics)        [brain: appraisal-system state]
      -> "how does X feel" answer

## The measurement: an ORACLE-SUBSTITUTION LADDER
For each stage we swap the glass-box component for its competent-reader oracle and measure how much
end-to-end accuracy (F1 of (character, emotion) triples vs a competent-reader reference) it recovers.
Oracles: POS/parse = spaCy (reference-only, never on the glass-box path); coref = LitBank GOLD clusters
(the annotation = the binding ceiling); emotion lexicon + experiencer frame are shared (brain-faithful,
not swept). The reference (ceiling) = the all-oracle rung ~ a competent reader on the explicit tier.

## SIGNAL-LOSS BUDGET -- WHERE WE LOSE SIGNAL
Measured on the chain (F1 vs the competent-reader reference). The 100-doc table is the CYCLE-0 lexicon;
the CYCLE-1 denotation-gate 40-doc ladder reconfirms the SAME dominance (G0 0.514 -> +spaCyPOS 0.555 ->
+goldCoref 0.945; gold coref recovers +0.430 of the 0.486 total = 89%), so the finding is robust to the
lexicon change.

| rung | what is oracle | F1 (100 docs, cycle-0) |
|---|---|---|
| G0 glass-box | nothing (full glass-box) | 0.581 |
| G1 +spaCy POS | POS/parse | 0.624 |
| G2 +GOLD coref | coreference | 0.945 |
| G3 ceiling | POS + coref | 1.000 |

- **COREFERENCE is 87% of the end-to-end signal loss** (gold coref alone recovers +0.364 of the 0.419
  total gap; spaCy POS recovers +0.043). The reader's coref binds the emotion experiencer correctly on
  only **36%** of experiencer mentions vs gold.
- Emotion DETECTION recall vs the competent-parser reference = **0.96** (lexicon + tagger coverage is
  near-ceiling; NOT a bottleneck).
- **The affect extraction + experiencer-linking + valence rules are near-perfect GIVEN good coref
  (F1 0.945 with gold coref).** The bottleneck is entirely the upstream COREF organ -- a separate
  organ, owned by other problems (name-clustering, referent-linking). This is the single most useful
  finding: to improve character-emotion tracking, improve coreference.

## COMPARISON TO THE BRAIN (a competent reader), itemized
- DETECTION: ~ceiling (0.96) -- a competent reader identifies explicit emotion statements; so do we.
- EMOTION TYPING: valence primary (matches brain: online reading recovers valence, Gygax 2004);
  category is the curated family (clean).
- EXPERIENCER ROLE (subject vs object): PINNED psych-verb frame -- matches the brain's lexical linking
  (authored A/B 1.0 vs naive 0.33).
- BINDING (which character): the brain uses Centering (recency + subjecthood + parallelism + topic
  salience) + implicit-causality verb bias; OUR coref lags badly here (0.36 vs gold). THE gap.
- INFERENCE: the brain infers unstated emotion (OCC appraisal over causation+goal); we do NOT (the
  located negative).

## THE ITERATION (getting closer)
**Cycle 1 -- emotion DENOTATION gate (the ladder found the lexicon over-fires).** The signal-loss study
showed the NRC Emotion Lexicon is an ASSOCIATION lexicon (flags war->fear, death->sadness, money->joy,
friends->joy, married->joy, excellent->joy) -- emotion-LADEN concepts, not emotion-LABEL states
(Pavlenko 2008; Altarriba & Bauer 2004; Zhang et al. 2017 N170/LPC dissociation). Replaced the NRC gate
with a curated emotion-DENOTING term inventory (WordNet-Affect-style, ~230 terms by family x POS;
causatives "frightening" and evaluatives "excellent" excluded), keeping Warriner for the valence VALUE
and the curated family as the CATEGORY. Result: the "how does X feel" reliable-slice accuracy rose
**0.625 -> 0.788** (vs floor 0.31, twin 0.39, CI-separated), valence-sign **0.766 -> 0.838**, positive
control 5.9x -> **10.6x**. Cost: ~80% fewer affects extracted (higher precision, some recall of
borderline emotions traded away -- explicit affect is now sparse, ~1 per 23 events).

**Cycle 2 -- brain-faithful COREF fallback (the dominant loss): a CAN-FAIL NEGATIVE, honestly reported.**
Added a Centering global-topic-salience fallback: when the reader's coref leaves an experiencer pronoun
UNRESOLVED, bind it to the gender-compatible PROTAGONIST (the most-frequently-mentioned named character
of matching gender) -- the research-recommended cheap fallback (Grosz-Joshi-Weinstein 1995 level 4).
Measured as ladder rung G1b_salienceCoref (40 docs): F1 recovery = **-0.001 (a wash)**. It adds a few
correct bindings (recall +0.004) and an equal number of wrong ones (precision -0.006). WHY IT FAILS:
the protagonist guess is as often wrong as right -- there are usually several same-gender characters, and
the experiencer of a given emotion is frequently NOT the global protagonist. The dominant coref loss
(gold coref recovers +0.43) is therefore NOT closeable by a crude affect-side fallback; it requires a
proper Centering resolver (recency + subjecthood + role-parallelism + gender + implicit-causality verb
bias, per the research), which is the COREF ORGAN's job (name-clustering / referent-linking problems),
not an affect-register patch. This negative is the value: it proves the affect dimension is sound and
hands the coref organ a precise target -- bind emotion-experiencer pronouns (reader 0.38 vs gold; gold
recovers +0.43 F1 end-to-end).

## TRACING THE COREF LOSS -- what ACTUALLY happened (637 scorable experiencer mentions, 100 docs)
The aggregate "coref = 87% of loss" is real in F1-vs-reference terms, but a per-mention TRACE
(`--trace`) shows the MECHANISM is not what "coref error" first suggests:
- SURFACE of the experiencer: 39.6% personal pronouns, 53.4% common-noun NPs ("the man", "the child"),
  4.4% named, 2.7% plural/it.
- GOLD canonical type: **only 16.5% of experiencers are NAMED characters; 83.5% are COMMON-NOUN cluster
  heads** ("child", "man", "woman") -- most narrative experiencers are UNNAMED entities.
- Reader outcome: agree 37.4%, abstain(None) 38.3%, wrong-name 24.3%.
- ABSTAIN breakdown: of 244 abstains, **212 are because the GOLD is a common-noun entity** the reader's
  proper-name-centric canonicalizer cannot name; only 32 are genuine misses on a NAMED cluster. Of
  personal-pronoun abstains, an antecedent was available in just **3** cases -- i.e. the reader almost
  never abstains on a resolvable named pronoun.
- WRONG-NAME breakdown: 126 of 155 are on common-noun-gold mentions; only 29 are a named pronoun bound
  to the WRONG named character.
- **GENUINE named-character pronoun coref errors = ~61/637 ~= 9.6%.** The other ~90% of the "loss" is
  the COMMON-NOUN REFERENT REPRESENTATION gap: (a) most experiencers are unnamed common-noun entities,
  and (b) the reader's coref/entity model clusters/names them differently from gold, so the character-
  NAME comparison mismatches.

WHY the three affect-side coref fixes failed, now explained by the trace: they all targeted PRONOUN
resolution (recency/salience/gender), but resolvable named pronouns were already handled well (only 3
abstains had an available antecedent). The real gap is common-noun ENTITY segmentation/clustering, which
is the coref/entity ORGAN's job (referent formation), not a pronoun heuristic and not an affect patch.
This is the precise, traced conclusion -- and it changes the recommended fix from "better pronoun coref"
to "name and track common-noun entities as characters" (extend the reader's entity model, or have the
affect register canonicalize common-noun coref clusters by their head).
The affect dimension itself is brain-faithful and near-ceiling given its inputs. The dominant signal
loss in the end-to-end chain is UPSTREAM COREFERENCE (87%), not the affect extraction -- which reframes
the next-highest-value work as improving the coref organ (and, for the unstated tier, the OCC-appraisal
meaning channel). The emotion-denotation gate (cycle 1) is a real, landed precision win independent of coref.

## PRECISELY HOW OUR IMPLEMENTATION DIFFERS FROM THE BRAIN (mechanism-diff)
Full drill: research_brain_vs_our_coref_binding_mechanism_diff_2026-09-04.md. The 8-item diff
(ours / brain+citation / predicted failure), summarized:
1. RETRIEVAL: ours = hard-filtered ranked list; brain = content-addressable parallel cue-matching /
   direct access (Lewis & Vasishth 2005; McElree 2003) -> a stale-but-frequent character can beat a
   just-reactivated one.
2. INCREMENTALITY: ours = post-hoc one pass; brain = online verb-driven expectation (Altmann-Kamide
   1999; Levy 2008) -> misses exactly at psych-verb clauses.
3. DECAY: ours = fixed/cumulative recency; brain = power-law decay + reactivation (Anderson-Schooler
   1991) -> predicted the -0.001 salience-fallback wash.
4. AGREEMENT: ours = hard gender filter; brain = graded weighted cue (Wagers-Lau-Phillips 2009).
5. CENTERING: ours = hand-coded recency+subjecthood; brain = emergent from attention (Gordon-Grosz-
   Gilliom 1993) -> predicted the -0.051 when we hand-coded surface features without the mechanism.
6. IMPLICIT CAUSALITY: absent in ours; brain uses it online (Koornneef-Van Berkum 2006).
7. REFERENT SEGMENTATION (the DOMINANT item): ours is proper-name-centric and forms NO referent for
   common-noun-only entities; brain builds a referent for every entity via descriptive-content match +
   bridging (Clark-Haviland 1977; Poesio-Vieira 1998; Gundel-Hedberg-Zacharski 1993; Ariel 1990) --
   matches the trace numbers almost exactly.
8. EMOTION-EXPERIENCER binding: already near-ceiling given correct coref (F1 0.945) -> the loss is
   entirely upstream in 1-7, dominated by 7.

SINGLE MOST IMPORTANT DIFFERENCE (independently confirmed by the trace): our coref has NO mechanism for
entities referred to only by common nouns (83.5% of experiencers). FIX SPEC: head-noun-match clustering
first (the cheap glass-box Poesio-Vieira dominant case), then bridging inference, before revisiting the
pronoun-retrieval architecture (cue-based retrieval + IC bias).

## THE ITERATION -- ALL COREF PROTOTYPES (can-fail; measured; honest)
Experiencer-binding recovery vs gold (head-lemma identity, n=295; reader baseline 0.380):
- Cycle 2a global-protagonist salience fallback -> F1 -0.001 (WASH).
- Cycle 2b Centering resolver, full replacement -> F1 -0.051 (HURTS: naive recency+subjecthood is worse
  than the reader's coref -- surface features without the generative attention mechanism).
- Cycle 2b' Centering resolver, fallback-only -> -0.003 (WASH).
- Cycle 3 referent-former (head-noun clustering), full replacement -> identity 0.278 (WORSE: over-merges).
- Cycle 3' referent-former, ADDITIVE naive head-match (reader-first) -> identity 0.380 -> 0.400 (+0.020),
  but chain-F1 -0.095 (its head-lemma labels do not match gold's longest-head labels).
- Cycle 3b FAITHFUL referent MODEL (experiments/discourse_referents.py: definiteness a/the -> new-vs-link;
  head-noun + number + modifier compatibility so 'the old man' != 'the young man'; recency-linking;
  longest-head labels matching gold's convention) -> identity 0.380 -> 0.390 (+0.010); chain-F1 -0.002
  (WASH). Finer entity distinctions do not help the head-lemma metric, and the glass-box referent LABELS
  still do not match gold cluster labels well enough to register as chain-F1 gains.

CONCLUSION (exhaustive -- SIX coref prototypes): every glass-box prototype recovers at most +0.01-0.02 by
a forgiving head-lemma identity metric and ~0 at the chain-F1 level; ONLY gold coref recovers the +0.43.
The DIRECTION is validated (common-noun referent formation is where the signal is), but closing the gap
needs a FULL faithful coref build: head-match + definiteness/modifiers (done in the prototype) PLUS
bridging inference + cue-based retrieval + the reader's OWN NP detection (not gold spans) + entity
labeling consistent with how the situation model names characters. That is a substantial COREF-ORGAN
research problem (owned by the name-clustering / referent-linking problems), NOT an affect-register patch
(the affect dimension is near-ceiling given good coref, F1 0.945). The prototype
(experiments/discourse_referents.py) + this spec are the validated hand-off to the coref organ.
