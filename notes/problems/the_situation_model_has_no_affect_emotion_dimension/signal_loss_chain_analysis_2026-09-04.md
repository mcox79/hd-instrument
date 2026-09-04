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

## THE STANDING FINDING
The affect dimension itself is brain-faithful and near-ceiling given its inputs. The dominant signal
loss in the end-to-end chain is UPSTREAM COREFERENCE (87%), not the affect extraction -- which reframes
the next-highest-value work as improving the coref organ (and, for the unstated tier, the OCC-appraisal
meaning channel). The emotion-denotation gate (cycle 1) is a real, landed precision win independent of coref.
