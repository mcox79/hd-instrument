# NEXT GAP -- the reading-learned arc SCORER (the brain-foundational path to EXCEED the frozen treebank parser)

**Why this is the real prize.** This solution located the wall with a number: routing the parse through the
graded probabilistic parse fixes only ~1.9% of head errors; **~99% of the residual is SCORER error** the
exact normalization cannot touch. The scorer is a frozen SUPERVISED surface-feature averaged-perceptron
trained once on the UD-EWT treebank -- the deepest NOT_BF component in the front-end. The brain does not
batch-train on labelled trees; it acquires syntax from READING. We proved (Prong 2) the attachment signal
is in the raw stream and **GROWS with reading** (UAS 0.177->0.212 unsupervised, monotonic) -- the property
the frozen perceptron structurally lacks. Closing the gap to the supervised ceiling (0.57 at first-step) is
where the parser can EXCEED, and it is the #1 shared wall (`CROSS_SOLUTION_IMPROVEMENT_MAP` Target 1, ~16
consumers).

## What it needs to do
Produce a GRADED, globally-normalized distribution over dependency structures whose arc scores come from
LEXICALIZED PROBABILISTIC EXPECTATION learned INCREMENTALLY from reading (not from gold trees), and that
KEEPS IMPROVING as it reads -- reaching (then exceeding, via lexical-semantic generalization the surface
perceptron cannot represent) the frozen treebank scorer's UAS.

## The brain-foundational mechanism (name it, then replicate)
- **Distributional / statistical acquisition** (Saffran 1996; Christiansen-Chater NoN): syntax bootstrapped
  from co-occurrence + prediction over the raw stream. PINNED at the computational level.
- **Lexicalized surprisal / expectation** (Hale 2001, Levy 2008; MacDonald 1994 PDC): P(structure | words)
  as accumulated predictive evidence. The graded posterior IS the surprisal landscape.
- **Valence / head-argument counts** (the DMV insight, Klein-Manning 2004): each head has a learned
  distribution over how many left/right dependents it takes -- the dominant unsupervised structure signal
  beyond distance. Our first-step PPMI omits valence; adding it is the next fidelity step.
- **Iterative refinement by re-reading** (EM / online consolidation): the brain refines its parse model by
  re-encountering structures -- the online propose-verify grow loop (MINERVA-2 episodic), NOT a batch
  treebank pass.

## Why the naive bolt-on FAILS (measured, so we don't repeat it)
`exp_parser_semantic_scorer_augment_v1`: adding the reading-learned lexical PPMI to the supervised scorer
does NOT exceed it (+0.0006, not CI-sep) -- the supervised scorer already carries a head-word x dep-word
bigram feature trained on gold arcs, so the unsupervised PPMI is a weaker estimate of a signal it has. =>
the path is to REPLACE the acquisition (a full reading-learned scorer with valence + generalization), not
to augment the frozen one.

## First measured step already in hand (build on it)
`experiments/exp_parser_learned_from_reading_v1.py` -- directional lexical+POS PPMI + locality prior,
CLE-decoded, UNSUPERVISED. UAS 0.2117, beats adjacency/random, twin loses, grows with reading. The reading
substrate to reuse: `reading_grounding_loop.track_directional_context_counts` (the pri-2 directional
channel), `distributional_meaning_channel.ppmi_svd` (generalization the sparse bigram lacks),
`predictive_reader` (verb->argument selectional fit), `incremental_parser` (the BF left-corner builder to
carry the incremental commitment).

## The bar for the follow-on
Reading-learned scorer UAS beats the first-step 0.21 CI-sep AND closes >=half the gap to the supervised
0.78, with the growth curve still rising, twin losing -- OR a located negative naming exactly which brain
mechanism (valence? generalization? incrementality?) the residual needs. Then: the graded parse over the
reading-learned scorer EXCEEDS the frozen treebank parser on a downstream board dim on real prose.
