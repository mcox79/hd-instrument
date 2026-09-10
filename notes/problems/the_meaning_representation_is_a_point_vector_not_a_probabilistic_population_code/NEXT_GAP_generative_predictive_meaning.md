# THE NEXT GAP, IDENTIFIED WITH A NUMBER: learned meaning is RELATION-BLIND; the fix is a PREDICTIVE/CONSEQUENCE channel

Evidence: `experiments/exp_meaning_depth_gap_v1.py` (SimVerb-3500 relation labels, n=806 covered pairs).

## 1. THE GAP (measured, not asserted)
Every meaning axis the substrate can LEARN is RELATION-BLIND: it cannot tell "same meaning" from "OPPOSITE meaning."
Synonym-vs-ANTONYM separability (AUC; 0.5 = cannot tell apart):
- GROUNDED (perceptual)        **0.508**  (chance -- SYN 0.427 ~ ANT 0.420 ~ COHYP 0.469; scores opposites AS similar)
- SEQ / distributional (learned) **0.531**  (near chance -- antonyms share contexts, the classic distributional failure)
- TAXONOMIC / WordNet (SUPPLIED)  **0.875**  (the ONLY channel that discriminates -- because a human curated the synsets)

The channels are LOW-correlated (0.08-0.18): they are DIVERSE axes, not redundant. But the two the substrate can
ACQUIRE from experience are ~chance at the one thing that separates meaning from relatedness. So the whole meaning
system leans on a SUPPLIED ontology for polarity, and the fusion barely beats that ontology. This is why we cap at
~1/3 of a competent reader: we have relatedness, not meaning.

## 2. WHY THIS IS FUNDAMENTAL (not fixable with more of the same)
Antonyms (love/hate, buy/sell, rise/fall, open/close) are DISTRIBUTIONALLY NEAR-IDENTICAL (same syntactic slots,
same neighbour words) and often PERCEPTUALLY similar. The discriminating signal is therefore NOT in co-occurrence
context or perceptual features -- both are shared. It is in the word's EFFECT ON THE WORLD: buy vs sell reverse who
owns what; rise vs fall reverse direction; help vs harm reverse the consequence-valence. **Synonyms make the SAME
forward predictions/consequences; antonyms make OPPOSITE ones.** Distributional similarity (what co-occurs) and
perceptual similarity (how it looks) are structurally blind to this; only a GENERATIVE/PREDICTIVE model of what the
word DOES to a situation carries it. (This is also why more reading grows SEQ toward the ontology's RELATEDNESS
level but not past it -- it is learning the wrong quantity harder.)

## 3. WHAT THE MISSING CHANNEL NEEDS TO DO
1. **Represent a word by its FORWARD PREDICTIONS / CONSEQUENCES in a situation** (the events/states it predicts, the
   result-valence it implies), NOT by its co-occurrence contexts or static features.
2. **Separate same-context / opposite-effect words** -- antonyms, converses, cause vs effect -- which every
   similarity channel conflates.
3. **Be LEARNED from reading** (predict-then-check across situations), not supplied by an ontology.
4. **Be a genuinely different, STRONG axis** -- complement (not duplicate) the similarity channels, so the fusion
   gains where similarity is blind.
Measurable target (can-fail): raise synonym-vs-antonym AUC well above the distributional/perceptual floor
(~0.51-0.53) WITHOUT WordNet, CI-separated, and ADD to the meaning fusion; info-free twin losing.

## 4. WHAT COULD PROVIDE IT (brain-foundational; REUSE the substrate's existing forward organs)
PINNED premise: comprehension is PREDICTIVE -- the brain continuously predicts upcoming meaning and reads the error
(N400; Kutas-Federmeier; Altmann-Kamide anticipatory eye-movements; Elman 2009 generalized event knowledge). A
word's meaning is its role in that generative model. The substrate ALREADY BUILT the pieces; none feeds the WORD
meaning channel yet:
- **`hdlab.predictive_world_model`** -- online FORWARD event-transition predictor (recent event-concepts -> next
  event-concept). Represent a word by the distribution over next-events it predicts.
- **`hdlab.generalized_event_knowledge`** -- graded associative readout of what-content-follows given the situation
  (Elman/McRae). The forward "what comes next" signal.
- **`hdlab.consequence_learning_loop`** -- learns a verb's RESULT-VALENCE from the episode's MET/UNMET consequence,
  cross-situationally. Directly separates help/harm, waste/save, buy/sell by OPPOSITE consequence-valence -- exactly
  the antonym axis, LEARNED not supplied.
- **`hdlab.predictive_reader`** (verb+role -> expected argument features) and **`hdlab.n400_coherence_monitor`**
  (prediction error) -- the word/feature level and the error signal.

THE MECHANISM (proposed, reusing the above): a PREDICTIVE-CONSEQUENCE meaning channel where
`meaning(word) = the distribution over forward events/states + the consequence-valence the word predicts`. Two
words are SAME-meaning iff they predict the SAME continuations and consequences; OPPOSITE iff opposite. Similarity
in this space is meaning-identity-WITH-polarity, learned from reading by prediction -- the un-supplied version of
what only WordNet gives today. This is the substrate's "generative world-model" (the named main event), and this
measurement is its sharp new justification: it is the ONLY thing that can un-blind LEARNED meaning to polarity.

Complementary supports (secondary): grounding-as-SIMULATION (Barsalou -- run the referent's simulation to read its
consequences, not a static feature vector); AFFECTIVE/valence grounding (the Warriner VAD norms already on disk --
love/hate differ sharply in valence, a cheap partial antonym separator); contrastive-frame learning (antonyms
recur in "not X but Y" / "either X or Y" frames -- a specific learnable textual signal).

## 5. HOW TO TEST IT (the next problem's bar)
Build the predictive-consequence channel from the forward organs above; on SimVerb it must (a) raise
synonym-vs-antonym AUC above the ~0.51-0.53 distributional/perceptual floor CI-separated WITHOUT WordNet, (b) ADD to
the meaning fusion (a complementary axis, correlation with the similarity channels low but its AUC high), (c) its
info-free twin loses. If it clears (a)-(c), the substrate has LEARNED meaning-with-polarity -- the depth the current
representation lacks, and the route past the ~1/3-of-a-reader ceiling.
