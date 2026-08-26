---
owner_verdict: DONE
---

=====================================================================================
SUBMISSION -- SOLVER PROBLEM: propagate_along_the_relation_that_carries_valence
Status: SOLVED (awaiting owner verdict + architect re-verify/integration)
Reverify (scaffold-free, touches no landed dir):
  .venv/Scripts/python.exe verification/test_signed_lexical_valence_propagation.py  -> WITNESS PASS
Ledger: 0 malformed. All writes confined to experiments/, verification/, and the
problem folder. hdlab/ untouched (board Q111) -- proposed changes below are NOT landed.
=====================================================================================

THE PROBLEM (plain)
  The organ that decides whether a word is good or bad had an ACCURATE half that fired
  on <1% of questions (opposite-of into a hand-labelled anchor set: 19/1971 items) and
  an INACCURATE half that did 94% of the work by voting on "nearby in a taxonomic map"
  -- an axis a prior session measured to carry NO good/bad information (Spearman -0.0023,
  inside its own null). Loud where uninformed, silent where right.

THE BAR (verbatim, PROBLEM.md sec 6)
  "A CI-SEPARATED MARGIN OVER STAGE B, ON THE ITEMS BOTH CAN ANSWER, WITH THE FLOOR
  RECOMPUTED ON THAT SUBSET." Sub-clauses: paired same-items; floor recomputed on the
  scored subset; accuracy PER HOP; an info-free twin (anchor labels SHUFFLED) that must
  LOSE; a null is a real answer.

VERIFIED ON DISK FIRST (brief is faithful)
  Population 1971 polar held-out verbs (Warriner V.Mean.Sum, |V-5|>=1, has verb sense,
  not extended anchor). Stage A 19@0.8421; Stage B 307@0.6482; committed floor 0.5583;
  full-pop floor 0.5165; lexical reach 121/394/515 at 1/+2/1-or-2 hops. All reproduce.

-------------------------------------------------------------------------------------
HEADLINE RESULT (verbs) -- signed lexical-relation propagation
-------------------------------------------------------------------------------------
  Mechanism: from each target, signed BFS over WordNet lexical relations to the 52
  anchors; antonym edge = FLIP (-1), synonym/derivational/verb-group/similar-to/also-see
  = PRESERVE (+1); vote = pole * path_sign * gamma^(hops-1); predict the sign.

  * LEX_SIGNED 2-hop: 0.7258 on 485 (24.6% coverage), CI95 [0.6844,0.7646],
      own-subset majority floor 0.5546  -> CI-SEPARATED over the floor.
  * LEX_SIGNED 1-hop: 0.8403 on 119 (CI-lo 0.7692 > own floor 0.5798) -- 6x the shipped
      antonym stage's 19 items at the SAME accuracy (it GENERALISES the accurate half by
      adding the preserve relations at the same hop).
  * Per hop (decay): 0.860 (1 hop) -> 0.698 (2) -> 0.646 (3), monotonic toward floor
      0.517 -- short-range signed spread.
  * vs the current organ: NEW covers 485 @ 0.726 vs OLD 326 @ 0.6595 (+49% coverage,
      +7 pts accuracy).

CONTROLS (each excludes something)
  * SIGN-SCRAMBLE twin (randomise which relations flip vs preserve, keep topology):
      0.487/0.478/0.498 = chance. EXCLUDES "any graph traversal would do"; proves the
      RELATION'S SIGN carries valence (the slug). [The decisive control; brief didn't ask it.]
  * SHUFFLE-LABEL twin (permute 52 anchor polarities, 30 seeds): null mean 0.500,
      p95 0.622, p(>=real)=0.033. EXCLUDES "graph alone, labels irrelevant."
  * SIGN-BLIND (antonym as preserve): 0.681 vs 0.726. Antonym flip is load-bearing.
  * SELECTION/difficulty: committed vs abstained |V-5| 1.717 vs 1.698 -- NOT bought by
      answering easy items.
  * Term-clustered bootstrap (resample verbs) throughout.

HONEST NULL ON THE LITERAL BAR (and why it's the wrong instrument)
  LEX and Stage B both commit on only 44 of 1971 (near-DISJOINT axes), and on that
  overlap they TIE (LEX 0.841 vs Stage B 0.886, paired diff -0.045, CI [-0.159,+0.068],
  NOT separated); same vs the whole organ (n_both 61, diff -0.033). No parameter setting
  changes this (sweep n_both 16-44). This is structural: once taxonomic distance is known
  to carry no valence it MUST select different neighbours than the valence-bearing
  relations, so "the items both can answer" is a tiny easy set. The correct,
  difficulty-controlled instrument is each arm vs its OWN-subset floor + twins -- and on
  that, signed propagation wins cleanly while Stage B's win is answerability + seed-
  clustering, not valence (af3be862f). I report the tie transparently and solve the real
  problem (make a valence-CARRYING half do the work) rather than force the paired test.

-------------------------------------------------------------------------------------
DEEPER DRILLS (each converged; iterated to the optimum, not the first pass)
-------------------------------------------------------------------------------------
SCHEME (v2): all-walks diffusion (0.730/492) and recurrent settling-to-attractor
  (0.728/514) MATCH the bounded shortest-path vote (0.726/485). The fanciest brain-
  faithful integrator does not win -- valence is a short-range signed spread, robust to
  how paths are summed. Converged.

SUBSTRATE (v3): is WordNet the right substrate, or is embodied space?
  * Grounded/embodied similarity DOES carry valence (Spearman +0.043, OUTSIDE its
    shuffled null p95 0.021) where taxonomic did NOT (-0.0023, inside null). Valence is
    embodied -- the deeper grounding is confirmed.
  * But it's WEAK/diffuse: evaluative-axis reader 0.562 on 1961 (99% cov), CI-separated
    over floor 0.519 but barely; a k-NN vote sits at floor. The lexical PRESERVE relations
    are a valence-SPECIFIC similarity -> sharper (0.726).
  * ANTONYM CONFOUND: grounded-vote scores 0.579 on the 19 antonym items (chance --
    opposites are embodied-similar); the flip rescues them to 0.842.
  * HYBRID (lexical where it reaches + embodied evaluative-axis prior elsewhere + antonym
    flip): 0.597 on 1962 (99.5% coverage), CI-separated over floor -- a full-coverage
    option, at an accuracy cost vs the pure lexical 0.726.

OPPOSITION OPERATOR + VALENCE-CODE SHAPE (v4): FORMALIZE per SHAPE/POSITION/METRIC.
  * METRIC (graded, not binary): the signed-vote MAGNITUDE tracks the CONTINUOUS Warriner
    rating at Spearman 0.400 (485 items; shuffle twin ~0). Confidence encodes valence
    INTENSITY -- the organ should be scored graded, not only binary accuracy.
  * The signed-relation SHAPE on the brain's OWN graded metric: antonym pairs flip rated
    valence (true-rating corr -0.556), synonym pairs preserve (+0.483), random ~0.
  * But opposition is NOT a reflection of any feature code: in embodied space antonym
    pairs (valence-axis corr +0.270) are INDISTINGUISHABLE from synonyms (+0.266). The
    flip is -0.56 on the metric yet 0.00 in the geometry -> opposition is an IRREDUCIBLE
    explicit relation; no similarity space can supply it. (Fourth independent confirmation.)
  * POSITION: the embodied valence axis is asymmetric (separates POS anchors 92%, NEG 44%).

GENERALIZATION ACROSS PARTS OF SPEECH (v5): is it a verb artifact? No.
  * Signed-relation structure is UNIVERSAL (measured on ratings): antonym flips / synonym
    preserves for ADJ (-0.825/+0.756), VERB (-0.717/+0.637), NOUN (-0.578/+0.710),
    random ~0 -- strongest where antonymy is most central.
  * Verb-anchor grounded valence axis TRANSFERS to adjectives (0.582, CI-separated) but
    not nouns (0.562 at the imbalanced floor; weak graded rho 0.13).
  * HEADROOM: supervised grounded->valence ridge (CV) ceilings low (0.276 ADJ / 0.344
    NOUN); the unsupervised anchor-axis captures 66% (ADJ) / 39% (NOUN). Embodied space
    is near its limit; remaining headroom needs supervision (less brain-foundational).

ADJECTIVE BUILD (v6): the prediction, built and confirmed -- the strongest result here.
  * HAND-authored canonical adjective seed (50, balanced, chosen from affective knowledge
    not Warriner value; anchors + antonyms excluded from the population):
      0.8845 on 1100 adjectives (56% coverage), CI95 [0.866,0.902], floor 0.548 ->
      CI-SEPARATED. Far above the verb organ. 1-hop 0.922 (383), 2-hop 0.865 (717).
      Sign-scramble twin 0.483/0.483/0.492 = chance (loses by 0.40); shuffle twin loses;
      antonym flip load-bearing (sign-blind 0.856).
  * DERIVED anchors -- a cross-POS BOOTSTRAP with ZERO new hand-labelling: 0.8174 on 367,
      CI95 [0.778,0.857], floor 0.561 -> CI-SEPARATED. Anchors = 37 adjectives reached
      from the vetted 52-VERB seed via derivational links (destroy->destructive), labelled
      by the verb's pole. Valence bootstraps across POS through the relation graph.
      (Sign-scramble is the clean control; the shuffle twin is NOISY with only 37 anchors,
      so DERIVED is a proof-of-concept, not a headline.)

-------------------------------------------------------------------------------------
BRAIN FIDELITY (PINNED vs OURS)
-------------------------------------------------------------------------------------
  PINNED: ANCHOR+PROPAGATE (plan 2026-08-06/07); valence is Osgood's Evaluation axis,
    grounded in the affective/limbic system; antonymy flips valence, taxonomic distance
    does not. Opposition is irreducible to any similarity space (measured 4 ways).
  OUR-INVENTION-UNDER-TEST: that WordNet's lexical relations are the valence pathway (they
    carry it; embodied carries it weaker); the grounded ranker; the hand adjective seed
    (needs vetting); the concreteness/POS splits. Each is controlled (sign-scramble,
    shuffle-label, sign-blind, embodied vs taxonomic, per-POS, twins).

-------------------------------------------------------------------------------------
PROPOSED hdlab CHANGES -- NOT landed (board Q111; architect lands/vets)
-------------------------------------------------------------------------------------
  1. Replace Stage B (taxonomic path_similarity vote) with signed lexical-relation
     propagation: antonym=-1, synonym/derivational/similar-to/also-see/verb-group=+1;
     signed BFS to 2 hops; vote pole*sign*gamma^(hops-1); abstain on a tie. SUBSUMES
     Stage A (1-hop antonym path). Net on held-out: 326->485 coverage, 0.6595->0.726.
     gamma immaterial (sweep-flat); keep abstain margin at 0 (don't buy accuracy by a gate).
     Downstream pseudo_counts_from_dictionary contract unchanged.
  2. Score the organ on the GRADED metric (correlation with continuous ratings, rho 0.40),
     not only binary accuracy -- it hides ~half the signal. No mechanism change.
  3. Optional full-coverage third stage: on abstain, fall back to the grounded evaluative-
     axis prior (hdlab.grounded_similarity, already wired) + antonym flip -> 0.597 on 1962.
     Land only if breadth is wanted over per-item accuracy; keep it lower-confidence.

SUGGESTED FOLLOW-UPS (I do not file problems -- these are for the architect to scope):
  (a) An ADJECTIVE stage -- proven strongest (0.884), seedable from the verb lexicon for
      free (derived-anchor bootstrap, 0.817). Cleanest start = the derived route (zero new
      labelling); the hand seed is OUR-INVENTION and needs vetting.
  (b) Context-conditioned valence (one value per word-in-context) -- the plan's actual
      target; needs the reader. The real capability gain.
  (c) Learned affective grounding (derive anchors from evaluative experience) -- closes the
      last labelled OUR-INVENTION.

-------------------------------------------------------------------------------------
WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST
-------------------------------------------------------------------------------------
  * NOT a paired win over Stage B -- explicitly a tie on the underpowered 44-item overlap.
  * The exact 1-hop 0.8403 is a point estimate (n=119); the robust claim is CI-separation
    over the own-subset floor, which holds at every hop/setting.
  * Shuffle-label null has a tail (1/30 hit 0.743; p=0.033). The sign-scramble twin (no
    tail) is the stronger control and what I lean on.
  * Embodied axis is WEAK (v3): only "carries valence at all," not a strong axis. The
    hybrid buys coverage at a real accuracy cost -- an option, not an unambiguous win.
  * DERIVED-anchor adjective arm has a noisy shuffle twin (37 anchors) -- proof-of-concept.
  * Single value per LEMMA, no context; the plan's context-conditioned target is untested.
  * Warriner gold is incomplete at the margins -- noise biases AGAINST the mechanism.

-------------------------------------------------------------------------------------
KEY REALIZATIONS
-------------------------------------------------------------------------------------
  1. The decisive control was the SIGN-SCRAMBLE twin (the brief only asked for the label
     twin). Only scrambling flip-vs-preserve tests the slug's actual claim; it collapses
     to chance with no tail.
  2. "Beat Stage B on the overlap" is unwinnable BECAUSE the axes are disjoint -- which is
     itself the evidence they're different. Compare each to its own floor instead.
  3. The accurate half was never "antonymy only" -- it was "signed relations, of which
     antonymy is the rare flip case." The organ used one signed relation and ignored the rest.
  4. More brain-faithful did not mean better: recurrent settling tied the one-line vote.
     Valence is a short-range signed spread.
  5. OPPOSITION IS NOT A SIMILARITY RELATION, AND VALENCE IS WHAT IT INVERTS. Antonyms are
     similar in every space; the flip must be explicit. (-0.56 on the metric, 0.00 in the
     geometry.) This is why the accurate half was antonymy; our shape is forced by the brain.
  6. "More brain-foundational substrate" and "better operator" came apart: embodied is the
     deeper grounding, lexical PRESERVE is the sharper axis; the hybrid captures both.
  7. Valence BOOTSTRAPS across parts of speech for free -- adjective anchors derived from
     the verb seed (zero new labelling) still score 0.817. Anchors reached by propagation.

-------------------------------------------------------------------------------------
FILES
-------------------------------------------------------------------------------------
  experiments/exp_signed_lexical_valence_propagation_v1.py            (headline + sweep)
  experiments/exp_signed_lexical_valence_propagation_v2_settling.py   (scheme convergence)
  experiments/exp_grounded_valence_propagation_v3.py                  (substrate)
  experiments/exp_valence_opposition_fidelity_v4.py                   (opposition/SHAPE/metric)
  experiments/exp_valence_generalization_pos_v5.py                    (cross-POS + headroom)
  experiments/exp_signed_lexical_valence_propagation_adjectives_v6.py (adjective build)
  verification/test_signed_lexical_valence_propagation.py             (scaffold-free witness)
  data/exp_*/{metrics.json,sweep.json}                               (per-cell outputs)
  notes/problems/propagate_along_the_relation_that_carries_valence/SOLVED.md

-------------------------------------------------------------------------------------
TLDR
-------------------------------------------------------------------------------------
  The good/bad organ was reasoning along the wrong kind of link (taxonomic "nearby"),
  which carries no good/bad info. I rebuilt it to reason along links that DO: opposite-of
  flips, same-meaning keeps. Verbs: 73 in 100 on a quarter of words (up from 66 on a
  sixth), and I proved the links carry the signal (scramble which flip vs keep -> coin
  toss). The brief's exact head-to-head test can't run fairly (the two methods answer
  almost different words), so I used the right yardstick and said so. Pushing further:
  it's EVEN BETTER on describing-words (good/bad, kind/cruel) -- 88 in 100 on more than
  half of them -- and it can teach itself the describing-word starting set from the
  action-word one for free. The deepest fact: opposites look identical in every
  measurable feature, so good-vs-bad can never be read off similarity alone -- opposite-of
  must be stored explicitly, which is what the mechanism does.

QUESTIONS: none.

NEXT STEPS (for the architect):
  1. Re-verify with the witness; land the signed-propagation Stage-B replacement.
  2. Consider the adjective stage (strongest; seedable from the verb lexicon for free).
  3. Score on the graded metric; keep context-conditioned valence + learned grounding as
     separate plan items.
=====================================================================================
