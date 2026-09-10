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

## 5b. LAYER 1 BUILT + MEASURED (2026-09-10) -- affective valence un-blinds antonymy WITHOUT WordNet
`experiments/exp_valence_polarity_meaning_channel_v1.py` (SimVerb, no WordNet in the channel). The primary graded
dimension antonyms reverse is AFFECTIVE VALENCE (Osgood 1957 semantic differential; Russell circumplex; Barrett/
Lindquist core affect -- PINNED). REUSING `hdlab.affect_lexicon` over the on-disk Warriner VAD norms (the affective
spoke `grounded_similarity` OMITS), a SIGNED valence read separates synonyms from antonyms:
| representation | syn-vs-antonym AUC |
|---|---|
| distributional (learned SEQ) -- the relation-blind floor | 0.535 |
| **VALENCE** (signed) | **0.718** (+0.183 over floor, CI [0.084, 0.281]) |
| **VAD** (valence+arousal+dominance) | **0.750** |
| WordNet (SUPPLIED, reference) | 0.875 |
Complementary (corr with distributional 0.11), info-free twin collapses (0.502). So a GROUNDED, LEARNED-not-supplied
affective dimension recovers MOST of the supplied ontology's antonym discrimination (0.535 -> 0.75 of 0.875) with NO
ontology. **This is layer 1 of the fix, built and CI-separated.**
- LITERATURE placement: the standard NLP fixes are SUPERVISED thesaurus injection (counter-fitting, Mrksic 2016;
  lexical-contrast embeddings, Nguyen 2016) = the supplied ontology we avoid, or contrastive PATTERNS (Lin 2003;
  Mohammad 2013; AntSynNET Nguyen 2016). The affective-valence / core-affect route is the brain-foundational one and
  is less used for antonymy -- Osgood's Evaluation axis as the antonym separator.
- HONEST RESIDUAL: valence catches **77%** of antonyms (the affectively-opposed: love/hate, win/lose, help/harm).
  The ~23% CONVERSES (buy/sell, open/close, give/take) are NOT affectively opposed (measured: buy +0.46/sell +0.08)
  and are NOT separated by valence -- they reverse a DIRECTIONAL state (possession, openness), which needs LAYER 2.
  And COHYPONYMS (walk/run) are not a polarity problem (valence AUC 0.52) -- they need feature-specificity, not sign.

## 5c. LAYER 2 BUILT + WALL RESEARCHED (2026-09-10) -- directional path semantics splits the residual in two
`experiments/exp_directional_consequence_channel_v1.py` (base + 1M Simple-Wikipedia lines, parser-free, no
ontology). A verb's SIGNED DIRECTIONAL SIGNATURE = its association with OPPOSED path markers
(up/down, in/out, on/off, to/from, more/less, ...), PPMI(v,pole+)-PPMI(v,pole-) per axis -- the grammaticalised
direction of state change (Talmy 1985/2000 path semantics; force-dynamic direction). Converse antonyms should have
OPPOSITE signatures. Measured on canonical pairs (dir_sim; negative = opposite):
| converse | dir_sim | works? | |
|---|---|---|---|
| increase/decrease | **-0.78** | YES | scalar direction (more/less) grammaticalised |
| open/close | **-0.54** | YES | aperture (on/off, up/down) |
| add/remove | -0.26 | YES | |
| rise/fall | -0.16 | weak | vertical (up/down) |
| **buy/sell** | **+0.38** | NO | direction is in the ARGUMENT ROLES, not a particle |
| **give/take** | **+0.62** | NO | ditto |
Info-free twin collapses (0.50). So the directional-path signal genuinely separates SCALAR / SPATIAL directional
antonyms (LAYER 2a -- built, brain-foundational, learned, no ontology) but NOT TRANSFER CONVERSES (buy/sell,
give/take, lend/borrow), whose polarity is in WHO-DOES-WHAT-TO-WHOM. On the mixed converse subset (n=41) it beats
chance (AUC 0.57) and beats valence (+0.06) directionally but not CI-separated -- because it AVERAGES the working
scalar converses with the failing transfer ones.

**THE RESIDUAL, PRECISELY LOCATED (layer 2b), AND THE WALL RESEARCHED THROUGH (2026-09-10):** TRANSFER CONVERSES
reverse the ROLE MAPPING (buy: subject GAINS; sell: subject GIVES). I drilled into it
(`exp_role_asymmetry_converse_channel_v1.py`): the hypothesis was that SUBJECT-side (left) context differs while
OBJECT-side (right) is shared, using the parser-free directional SEQ features. MEASURED: it does NOT separate them
(subject-side AUC 0.436 ~chance; role-asymmetry 0.570 weak; canonical buy/sell R>L but give/take R<L, and synonyms
like give/provide also R>L; twin collapses). **WHY -- the wall, understood 100%: ADJACENCY (+-2 tokens) is too
coarse to isolate argument ROLES.** The discriminating entities (buyer vs seller -- the argument HEADS) sit at
variable distances behind determiners/adjectives ("the wealthy customer bought"), so L1/L2 capture shared
FUNCTION-WORD context, not the role-bound head nouns. **Transfer-converse polarity lives in the ROLE-BOUND ARGUMENT
HEADS (agent-head vs patient-head), which co-occurrence of ANY directional flavour cannot represent -- it requires
ARGUMENT-STRUCTURE PARSING + ROLE-BINDING.** This is the sharpest instance of the ORIGINAL finding (meaning is a
similarity embedding, lacking COMPOSITIONAL role structure): the last ~few% of antonyms need a representation that
BINDS fillers to roles, not a bag of contexts.

**HOW TO DRILL THROUGH (the true generative-event layer, its own problem):** extract role-bound argument heads with
`hdlab.incremental_parser` (BF subject/patient, no supervised treebank) or the dependency parse; represent a verb by
the distribution over its SUBJECT-role heads vs OBJECT-role heads BOUND to the role (FHRR role-binding -- the
substrate's binding algebra); converses have SWAPPED role->head bindings (buy's subject-head distribution ~ sell's
recipient-head distribution). REUSE `hdlab.predictive_reader` (verb+role -> expected argument features) and
`hdlab.situation_reader` (who-did-what). Bar: separate synonyms from transfer converses using ROLE-BOUND heads,
above the adjacency floor, no ontology. This is why the substrate's generative world-model WITH ROLES is the named
main event -- the transfer-converse residual PROVES co-occurrence similarity structurally cannot reach it.

## THE LAYERED FIX (summary): the meaning representation gains POLARITY in three brain-foundational layers, none
using WordNet -- (1) AFFECTIVE VALENCE (love/hate; built, AUC 0.535->0.75 CI-sep), (2a) DIRECTIONAL PATH SEMANTICS
(increase/decrease, open/close; built, works on scalar/spatial), (2b) THEMATIC-ROLE / GENERATIVE-EVENT structure
(buy/sell; located, the generative-world-model problem). Together they cover affective, scalar-directional, and
role-directional opposition -- the three ways antonyms reverse meaning.

## 5. HOW TO TEST IT (the next problem's bar)
Build the predictive-consequence channel from the forward organs above; on SimVerb it must (a) raise
synonym-vs-antonym AUC above the ~0.51-0.53 distributional/perceptual floor CI-separated WITHOUT WordNet, (b) ADD to
the meaning fusion (a complementary axis, correlation with the similarity channels low but its AUC high), (c) its
info-free twin loses. If it clears (a)-(c), the substrate has LEARNED meaning-with-polarity -- the depth the current
representation lacks, and the route past the ~1/3-of-a-reader ceiling.
