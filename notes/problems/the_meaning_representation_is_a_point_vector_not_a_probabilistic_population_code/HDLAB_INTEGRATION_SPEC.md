# HDLAB INTEGRATION SPEC -- parser-free BF learned channel, by REUSING the substrate's existing organs (Q111)

**What to add, in one line.** Turn the substrate's EXISTING co-occurrence store into a brain-foundational IDENTITY
channel by adding DIRECTIONAL ORDER TYPING (the only new bit), removing the NOT_BF supervised parser from the
learned meaning channel -- at no accuracy cost, and it grows by reading.

## THIS IS REUSE, NOT A NEW ORGAN (owner directive: use the tools the substrate already has)
Every piece already exists in `hdlab/`; the change is one BF enhancement to the existing store:
- **Co-occurrence store:** `hdlab.reading_grounding_loop.ConceptSpace.observe_context_counts(lemma, ctx_lemmas)` /
  `all_context_counts()` -- the separable ROUTE-B store (2026-08-24, currently DEFAULT-OFF). It today accumulates
  an UNORDERED bag (`Counter.update(ctx_lemmas)`) -- i.e. the NOT_BF relatedness channel.
- **PPMI read-out:** the substrate's own PPMI (`hdlab.distributional_meaning_channel.ppmi_svd`, or the byte-identical
  `experiments.exp_learned_structured_meaning_v1.dep_ppmi_matrix`).
- **Lemmatiser:** `reading_grounding_loop.normalize_lemma` (BF, morphological stripping).
- **The ONE new BF bit:** feed `observe_context_counts` with DIRECTION+DISTANCE-TYPED context lemmas
  (`f"{dir}{dist}__{lemma}"`, e.g. `"R1__sit"`) instead of the plain bag. Direction typing = temporal-order coding
  (the `sequence_memory` S-matrix principle). This turns the existing bag (relatedness) into an IDENTITY /
  substitutability channel WITHOUT a parser.

**Verified byte-identical (witness A6):** feeding the existing `ConceptSpace` ROUTE-B store with the directional-typed
lemmas reproduces the experiment's directional counts exactly. So this is literally the existing organ + typing.

## THE CHANGE (small, additive, in existing organs)
1. In the reading loop's ROUTE-B call sites (`reading_grounding_loop` ~L1362-1380, where `observe_context_counts`
   is already called with the masked context multiset), build the context list with DIRECTION+DISTANCE typing:
   for center token i, add `f"{'L' if d<0 else 'R'}{abs(d)}__{lem[i+d]}"` for `d in (-1,1,-2,2)` in range. Gate it
   behind a `track_directional_context_counts` flag (or reuse `track_context_counts`).
2. Turn the ROUTE-B store ON during reading (it is default-off; the cost is a Counter update per token).
3. Consolidate OFFLINE with the existing PPMI (`ppmi_svd` / `dep_ppmi_matrix`) -> the learned IDENTITY channel;
   add it to the convergent read alongside grounded + taxonomic. It SUPERSEDES the unordered bag channel.
4. Carry the per-word GAIN = `sum(all_context_counts()[lemma].values())` as the precision scalar.

## BF verification (each operation is the brain's computation)
direction+distance typing = temporal-order coding (`sequence_memory`; theta-phase sequencing); PPMI =
`max(0, log[p(w,c)/(p(w)p(c))])` = the fixed point of Hebbian-predictive association (Levy-Goldberg 2014) +
neural rectification; L2 = divisive normalisation (Carandini-Heeger); learned from the raw stream = statistical /
predictive language acquisition (Saffran; Christiansen-Chater). NO treebank, NO supervised POS, NO perceptron, NO
hard decode -> strictly more BF than the arc-eager parser it removes. Detail: `ALL_BF_UPSTREAM_TRACE.md` Sec 2.

## MEASURED BASIS (held-out SimLex-999 / SimLex+SimVerb ranking, 3000-boot)
- Parser-free chain {grounded, directional-SEQ, WordNet} MRR **0.298** vs the NOT_BF-parser chain {grounded, DEP,
  WordNet} **0.294** (+0.004, CI [-0.011,+0.020]) -- NO accuracy cost, removes a NOT_BF component + the read-time
  parser + enables online learning (`exp_bf_learned_channel_landing_v1`). Info-free twin loses.
- The directional typing earns its place over the EXISTING bag: the bag alone ~0.02 MRR (C7 Study A) vs
  directional-SEQ ~0.09-0.15 -- order coding is what converts relatedness into identity.
- **Grows by reading (the north-star, EXECUTED):** reading +500k modern Simple-Wikipedia lines (parser-free) raised
  SEQ MRR **0.071 -> 0.146** (`exp_ppc_grow_to_strength_v1`); the learned channel closes most of the gap to the
  ontology (CM 0.203) purely by reading more.
- **PRECISION is a SATURATING function of gain (a BF refinement the growth revealed):** the RAW evidence count
  tracks correctness only in the unsaturated regime (rho 0.226 -> -0.016 as reading grows -- count becomes
  frequency); the brain-foundational precision is a SATURATING gain (Poisson Fisher information saturates;
  Weber-Fechner) -- use `log1p(gain)` for the precision weight. [numbers folded from the grow run]

## THE FUSION (fixing the fitted weight; turn on with exposure)
Replace `convergent_cue_reader.DEFAULT_W` (a fitted OUR-INVENTION scalar) with the intrinsic per-query GAIN RATIO,
using the SATURATING gain. Brain-foundational rule (measured): gain-modulate ONLY channels whose evidence is EARNED
(grounded, SEQ); a SUPPLIED ontology's gain is UNIFORM (its feature-count anti-tracks; uniform beats it CI-sep
+0.0155). At current exposure the earned channels are still catching up, so gain-weighting is net-neutral; land the
channel now, and turn ON saturating-gain weighting as the learned channel reaches ontology parity.

## SECOND LANDABLE -- the AFFECTIVE-VALENCE dimension (un-blinds meaning to antonymy; CI-separated capability)
The learned + perceptual channels are RELATION-BLIND: synonym-vs-antonym AUC ~0.51-0.53 (they score love/hate as
similar as synonyms). Only the supplied ontology discriminates (0.87). FIX (reuse, BF): add the SIGNED AFFECTIVE
dimension -- `hdlab.affect_lexicon.valence(word)` (+arousal/dominance) over the on-disk Warriner VAD norms; the
affective spoke `grounded_similarity` currently OMITS. Antonyms are opposite poles on it (Osgood 1957 Evaluation
axis; Russell/Barrett core affect -- PINNED). MEASURED (`exp_valence_polarity_meaning_channel_v1`): a signed valence
read lifts syn-vs-antonym AUC 0.535 -> 0.72 (VAD 0.75) WITHOUT WordNet, CI-separated [+0.084,+0.281], complementary
(corr 0.11), twin collapses. LAND: append valence(+A,+D) as extra dims to the meaning representation and fuse it as
a channel (it is the polarity axis, not a relatedness axis). Covers ~77% of antonyms (the affectively-opposed);
scalar-directional (increase/decrease) is layer 2a (path-marker signature, `exp_directional_consequence_channel_v1`);
transfer converses (buy/sell) need the role-binding generative channel (a NEW problem, `NEXT_GAP...md` §5c).

## INVARIANTS (do NOT change)
- Recall/recognition path (attractor: `ca3_completer`, `gap_detector`, `hippocampal_encoder`) reads the normalised
  vectors and is BYTE-IDENTICAL; the gain is a separate scalar the RANKING reads (`exp_ppc_no_regression_v1` INV1/2).
- No external tool/LLM at inference; glass-box and online.

## REVERIFY
`.venv/Scripts/python.exe verification/test_ppc_meaning_representation.py` (A6 proves the reuse path; C/D cover the
parser-free channel + landing). Grow-by-reading: `experiments/exp_ppc_grow_to_strength_v1.py`.

## BF-STATUS DELTAS to record (Q111)
- `ConceptSpace` ROUTE-B store: add directional-typed variant -> the learned IDENTITY channel (BF).
- `pos_tagger` / `arceager_parser`: remain NOT_BF but NO LONGER REQUIRED by the meaning chain's learned channel.
- `convergent_cue_reader`: fitted `w` -> intrinsic SATURATING gain ratio (BF fix; turn on with exposure).
- `distributional_meaning_channel`: the existing PPMI/substitutability organ -- reuse its PPMI; note it is tuned to
  substitutability classification, so the SIMILARITY read-out uses the directional-SEQ cosine, not its taught direction.
