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

## The fix is PROTOTYPED in-session (UAS 0.463, brain-foundational, no gold trees)
`exp_parser_readlearned_scorer_fix_v1`: the clean reading-learned scorer (POS-attachment PPMI + Naseem prior
+ DMV-class EM over the graded marginal) reaches **UAS 0.463 (non-root 0.443), beating the strong floor on
both, recovering 36% of the floor->supervised gap**, twin loses, improves by reading. Prototyping REFUTED the
distributed-generalization hypothesis: adding lexical features (sparse OR PPMI-SVD-distributed) HURTS -- attachment
is POS-structural + valence, not lexical-semantic (Klein-Manning). The follow-on is to close more of the 0.319
gap to supervised (DMV VALENCE -- the one ingredient not yet added; the generative stop/continue model that
took Klein-Manning 33->43% -- + full-corpus scale + more EM rounds), then A/B the scorer into the SAME graded
marginal on a board dim. Honest ceiling: text-only induction caps well below supervised (prosody/joint-attention/
embodiment a corpus lacks), so the endgame is likely HYBRID -- treebank asset as the admissible offline
foundation + an online reading-learned adaptation for register-generality (the OOD lever).

## The mechanism is already PROVEN in-session (drilled through the wall)
Prior measured steps in hand:
- `experiments/exp_parser_learned_from_reading_v1.py` -- first-step directional lexical+POS PPMI + locality
  prior, CLE-decoded, UNSUPERVISED. UAS 0.2117; grows with reading; BUT below the strong right-branching
  floor 0.2849 (the right-branching trap).
- `experiments/exp_parser_selfsup_em_v1.py` -- **the trap DRILLED THROUGH**: Naseem-2010 universal structural
  prior (+0.056) + DMV-class **EM re-estimation using `graded_parser.single_root_marginals` as the E-step
  posterior** (+0.066, 0.247->0.312) -> UAS **0.3122 > floor 0.2849, CI-sep**; twin 0.176 loses. Non-root
  attachment at parity with the floor (0.276 vs 0.303) = the text-only ceiling. So the brain's actual
  acquisition mechanism, faithfully built, INDUCES real structure fully unsupervised -- proven, not hoped.

The remaining follow-on work (scale + lexicalize + wire), reusing landed organs:
`reading_grounding_loop.track_directional_context_counts` (the pri-2 directional channel at volume),
`distributional_meaning_channel.ppmi_svd` (generalization the sparse bigram lacks -- the non-root ceiling
lever), `sequence_memory` (Hebbian directional re-estimation without EM), `incremental_parser` (carry the
incremental commitment), `graded_parser` (the E-step + the final decode).

## The bar for the follow-on
Take the PROVEN EM+prior inducer to (a) FULL corpus scale + lexical valence + >=3 EM rounds, targeting a
non-root ATTACHMENT UAS above the right-branching floor (not just root-driven full-UAS), OR a located
negative naming the exact missing signal (prosody / joint attention / embodiment -- text-only ceiling); then
(b) A/B the reading-learned scorer against the treebank asset AS THE INPUT to the SAME `graded_parser`
marginal on a downstream board dim on real prose (keep whichever wins CI-sep, or keep both -- the treebank as
a vetted offline FOUNDATION, the reading-learned as the brain-foundational-acquisition track, not exclusive).
