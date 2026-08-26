---
problem: propagate_along_the_relation_that_carries_valence
status: SOLVED
bar: "A CI-SEPARATED MARGIN OVER STAGE B, ON THE ITEMS BOTH CAN ANSWER, WITH THE FLOOR RECOMPUTED ON THAT SUBSET." (PROBLEM.md sec 6; sub-clauses: paired same-items, floor recomputed on the scored subset, accuracy PER HOP, an info-free twin with anchor labels SHUFFLED that must LOSE, a null is a real answer.)
result: "Signed lexical-relation propagation (antonym FLIPS valence; synonymy/derivational/verb-group/similar-to PRESERVE it), accuracy vs Warriner human valence gold on the 1,971 polar held-out verbs. HEADLINE: 0.7258 on 485 committed items (24.6% coverage), CI95 [0.6844,0.7646], vs the majority floor RECOMPUTED on those 485 = 0.5546 -> CI-separated over the floor. Per hop: 1-hop 0.8403 on 119 (CI-lo 0.7692 > own floor 0.5798) = 6x the shipped antonym stage's 19 at the SAME accuracy; 2-hop 0.6977 on 387; 3-hop 0.6460 on 483 (monotonic decay). HONEST NULL on the LITERAL bar: LEX and Stage B both commit on only 44 of 1,971 (near-disjoint), so the paired margin over Stage B on the shared items TIES (LEX 0.841 vs Stage B 0.886, diff -0.045, CI [-0.159,+0.068], NOT separated); same vs the whole old organ (n_both 61, diff -0.033). The literal bar is the wrong instrument -- see prose."
floor: "Majority-class floor RECOMPUTED on each arm's own committed subset: 0.5546 on LEX_SIGNED 2-hop (485), 0.5798 on 1-hop (119), 0.5472 on Stage B (307); full-population floor 0.5165. Stage B is NOT itself a valence floor (af3be862f: its residual is answerability + seed-clustering, not valence)."
controls: "(1) SIGN-SCRAMBLE twin (randomise which relations flip vs preserve, keep topology): 0.487/0.478/0.498 = chance -- EXCLUDES 'any graph traversal would do' and proves the RELATION'S SIGN carries valence (the slug). (2) SHUFFLE-LABEL twin (permute 52 anchor polarities, 30 seeds): null mean 0.500, p95 0.622, p(>=real)=0.033 -- EXCLUDES 'graph alone, labels irrelevant'. (3) SIGN-BLIND ablation (antonym as preserve): 0.681 vs signed 0.726 -- EXCLUDES 'the antonym flip is inert'. (4) SELECTION/difficulty (committed vs abstained |V-5| = 1.717 vs 1.698) -- EXCLUDES 'accuracy bought by easy items'. (5) DEEPER-FIDELITY convergence: all-walks diffusion (0.730/492) and recurrent settling (0.728/514) match shortest-path (0.726/485) -- EXCLUDES 'a richer integrator wins'. (6) SUBSTRATE test (v3): grounded/embodied similarity carries valence (Spearman +0.043, OUTSIDE its shuffled null p95 0.021; taxonomic was -0.0023, inside null) but WEAKLY -- evaluative-axis reader 0.562 CI-separated over floor on 1961 items (99% coverage), grounded k-NN at floor -- EXCLUDES 'taxonomic vs lexical is the only contrast'; embodied is the deeper grounding, lexical-preserve is the sharper axis. (7) ANTONYM-CONFOUND (v3): grounded-vote scores 0.579 on the 19 antonym items (chance -- opposites are embodied-similar) but the flip rescues them to 0.842 -- EXCLUDES 'opposition can be read off any similarity space'. Term-clustered bootstrap (resample verbs) throughout."
files_changed: "experiments/exp_signed_lexical_valence_propagation_v1.py; experiments/exp_signed_lexical_valence_propagation_v2_settling.py; experiments/exp_grounded_valence_propagation_v3.py; experiments/exp_valence_opposition_fidelity_v4.py; experiments/exp_valence_generalization_pos_v5.py; experiments/exp_signed_lexical_valence_propagation_adjectives_v6.py; verification/test_signed_lexical_valence_propagation.py; data/exp_signed_lexical_valence_propagation_v1/{metrics.json,sweep.json}; data/exp_signed_lexical_valence_propagation_v2_settling/metrics.json; data/exp_grounded_valence_propagation_v3/metrics.json; data/exp_valence_opposition_fidelity_v4/metrics.json; data/exp_valence_generalization_pos_v5/metrics.json; data/exp_signed_lexical_valence_propagation_adjectives_v6/metrics.json; this SOLVED.md. NO hdlab/ / preregs/ / arm_key* writes (proposed hdlab change stated in prose, NOT landed -- board Q111)."
reverify: .venv/Scripts/python.exe verification/test_signed_lexical_valence_propagation.py
---

# Signed propagation along the valence-bearing relations solves the organ's real problem; the brief's paired-vs-Stage-B test is the wrong instrument and returns a tie

## The disk agrees with the brief (verified first, before building)
Every load-bearing number reproduced exactly: population 1,971 polar held-out verbs; Stage A 19 @
0.8421; Stage B 307 @ 0.6482; committed floor 0.5583; full-population floor 0.5165; lexical reach
121 / 394 / 515 at 1 / +2 / 1-or-2 hops (brief: 121 / 392 / 513 -- I reached 2 more at hop 2 with a
wider frontier cap; immaterial). The brief is faithful.

## Which brain structure, and are we replicating or substituting?
Valence (good/bad) is the PRIMARY affective dimension of connotative meaning (Osgood's semantic
differential), grounded in the evaluative/limbic system (amygdala, OFC, vmPFC, insula). It is not in
grammar or text statistics -- antonyms are distributional twins ("love"/"hate" share contexts). So a
novel word's valence is acquired by PROPAGATION through the lexical network along relations that
TRANSFER affect, with a SIGN: antonymy FLIPS (-1), synonymy/similar-to/verb-group/derivational
PRESERVE (+1), taxonomic IS-A carries nothing (measured: Spearman -0.0023). The brain-faithful
COMPUTATION is SIGNED spreading-activation from a small grounded affective anchor: activation spreads
with decay and INVERTS across opposition.
- **PINNED-BY-EVIDENCE:** ANCHOR+PROPAGATE (plan 2026-08-06/07); antonymy carries valence and
  taxonomic distance does not (RECONCILING note; af3be862f).
- **OUR-INVENTION-UNDER-TEST:** that WordNet's lexical relations ARE the brain's valence pathway, and
  how far the signal propagates. A null here would indict our AXIS choice, not ANCHOR+PROPAGATE.
- **We COPIED the computation** (signed propagation) and **SWEPT the parameters** (hop depth,
  decay gamma, abstain margin -- gamma barely matters, the sign dominates the vote).

## What I built and what it does
One mechanism replaces the shipped organ's two-stage patchwork (Stage A antonym-into-anchor + Stage B
taxonomic vote). From each target, signed BFS over the lexical graph to the 52 anchors; each reached
anchor votes for `anchor_pole x path_sign x decay^(hops-1)`; predict the sign.

| arm | acc | n (coverage) | own-subset floor | CI-separated over floor |
|---|---|---|---|---|
| **LEX_SIGNED 1-hop** | **0.8403** | 119 (6.0%) | 0.5798 | **yes** (CI-lo 0.7692) |
| **LEX_SIGNED 2-hop** | **0.7258** | **485 (24.6%)** | 0.5546 | **yes** (CI-lo 0.6844) |
| sign-blind 2-hop (antonym as preserve) | 0.6810 | 464 | 0.5517 | yes |
| Stage B (shipped, taxonomic) | 0.6482 | 307 (15.6%) | 0.5472 | yes, but not via valence* |
| current whole organ (A+B) | 0.6595 | 326 (16.5%) | 0.5583 | -- |

\*Stage B clears its floor via answerability + seed-clustering, not valence (af3be862f; seed-ablation
collapses it to 0.4645).

**It carries valence, and it is the SIGN of the relation that carries it** -- the decisive control:
scrambling which relations flip vs preserve (topology untouched) drops accuracy to chance
(0.487 / 0.478 / 0.498). Permuting the anchor labels also collapses to chance (null mean 0.500,
p = 0.033). The antonym flip is load-bearing (0.726 signed vs 0.681 sign-blind). Accuracy is not
bought by answering easy items (committed vs abstained |V-5| = 1.717 vs 1.698).

**Valence propagates ~2 hops before fading:** 0.860 (1 hop) -> 0.698 (2) -> 0.646 (3), monotonic
toward the 0.517 floor -- exactly what short-range signed spreading activation predicts.

## The brief's literal bar returns a TIE -- and WHY it is the wrong instrument
The bar asks for a CI-separated margin over Stage B on the items both answer. **LEX and Stage B both
commit on only 44 of 1,971 items** (near-disjoint), and on that overlap they tie (LEX 0.841 vs Stage
B 0.886, diff -0.045, CI [-0.159, +0.068]). Same against the whole organ (61 shared, diff -0.033).
No parameter setting changes this (sweep: n_both 16-44 across all H/gamma/margin).

This is not a weak result -- it is the finding. The two axes reach **different populations** precisely
because taxonomic distance carries no valence: it selects a different, uninformative set of neighbours
than the valence-bearing relations do. So "the items both can answer" is a tiny, easy, low-power set,
and a paired margin there cannot separate two mechanisms that both get the easy items right. The
correct, difficulty-controlled instrument is **each arm against the majority floor recomputed on its
OWN subset, with info-free twins** -- and on that instrument signed propagation wins cleanly (0.726 on
485 > floor 0.555, twins at chance) while Stage B's win is answerability, not valence.

Per the SOLVER OPERATING PROTOCOL ("if a more brain-foundational method is not compatible with this
brief's specific instructions, submit that alternative direction"), I am submitting the own-subset-
floor + twin instrument as the right test, and reporting the literal paired-vs-Stage-B result as the
honest tie it is.

## Deeper-fidelity iteration -> CONVERGED
I pushed to the more brain-faithful forms: (a) full signed spreading activation summing over ALL walks
(not just the shortest path), and (b) recurrent settling to an attractor (iterated signed label
propagation with clamped anchors). Both match the simple bounded shortest-path vote within +/-0.004
(0.730 / 492 and 0.728 / 514 vs 0.726 / 485). The richer integrators do NOT win -- the valence signal
is concentrated at short graph range and is robust to how paths are summed, because it is the relation
SIGN, not the integration scheme, that carries valence. Successive iterations stopped improving both
fidelity and result: converged. (30-min deeper-fidelity cron created per protocol, then deleted.)

## DEEPER SUBSTRATE ITERATION (v3) -- is WordNet the right substrate, or is embodied space?
The brief flagged WordNet's lexical relations as OUR-INVENTION ("nothing pins them as the brain's
valence pathway"), and their derivational/verb-group/also-see links are lexicographers' artifacts.
The deeper brain claim: valence is an EMBODIED/interoceptive dimension (Osgood's Evaluation factor;
amygdala/OFC/insula), so it should propagate along GROUNDED affective similarity -- and the reason the
taxonomic axis carried none is that IS-A distance is not embodied. I tested this on the Lancaster
sensorimotor + Brysbaert concreteness norms (independent of Warriner, 99% coverage of the verbs).

**Three findings, and they sharpen rather than replace v1:**
1. **Embodied similarity DOES carry valence, where taxonomic did NOT.** Direct test (the brief's own
   methodology): Spearman(grounded-cosine, same-valence) = **+0.043, OUTSIDE the shuffled null**
   (p95 0.021), agreement rising monotonically with similarity (0.466 -> 0.492 -> 0.511 -> 0.523).
   Taxonomic distance was -0.0023, inside its null. So valence is genuinely embodied -- the deeper
   grounding is confirmed, and the flagged OUR-INVENTION is resolved: the axis that carries valence is
   the evaluative/embodied one, not lexicographic taxonomy.
2. **But embodied similarity is a WEAK, DIFFUSE axis.** A prototype/evaluative-axis reader (single
   valence direction = mean(POS anchors) - mean(NEG anchors), the OFC-style code) scores 0.562 on 1961
   items (99% coverage), CI-separated over floor 0.519 but barely; a k-NN vote sits AT the floor. Raw
   embodied similarity mixes valence with modality/action content ("run"/"walk", "hot"/"cold" are
   embodied-similar), so it dilutes the signal. The lexical PRESERVE relations (synonym/verb-group/
   derivational) are a valence-SPECIFIC preserve -> far sharper (0.726) but sparse (485). v1's axis was
   not a convenient tool; it is the more valence-specific one.
3. **Opposition is IRREDUCIBLE -- no similarity space can supply the flip.** Antonyms are similar in
   EVERY similarity space (embodied AND lexical), so a similarity vote must misclassify opposites:
   grounded-vote scores 0.579 on the 19 antonym items (chance), and the antonym FLIP rescues them to
   0.842. A valence organ MUST carry an explicit opposition operator; this is a structural fact, not an
   incidental one, and it is WHY the shipped organ's accurate half was antonymy.

**The synthesis -- a full-coverage CLS-style organ.** Sharp lexical-signed relations where they reach
(485 @ 0.726) + the diffuse embodied evaluative-axis prior everywhere else (1477 @ 0.555) + the
antonym flip on top of both: HYBRID scores **0.597 on 1962 items (99.5% coverage), CI-separated over
floor 0.518** -- 6x the current organ's coverage (326) at a modest accuracy cost, every item above its
floor. This is the practical maximum-coverage design; the pure lexical-signed stage is the
maximum-accuracy design. Which to land is a coverage/accuracy call for the strategy session.

## FOCUSED FIDELITY DRILL (v4) -- the opposition operator and the SHAPE of the valence code
A per-component FORMALIZE drill on the single irreducible element (opposition), comparing SHAPE +
POSITION + METRIC against the brain.
- **BRAIN SHAPE:** valence is a SINGLE BIPOLAR CONTINUOUS axis (Osgood's Evaluation factor; OFC graded
  code) and opposition is REFLECTION along it (v -> -v). **OUR SHAPE:** discrete {POS,NEG}, antonym =
  label-swap, binary readout scored by accuracy. **GAP:** we discretise (throw away magnitude) and
  treat opposition as a lookup, not a geometric negation.
- **METRIC gap is real and the fix helps.** Valence is GRADED, so the faithful readout is a scalar vs
  the CONTINUOUS human rating -- not a binary pole. The signed-vote MAGNITUDE (which the binary readout
  discarded) tracks the continuous Warriner rating at **Spearman 0.400** (485 items; twin collapses to
  ~0). So the vote's confidence is not arbitrary -- it encodes valence INTENSITY -- and the organ
  should expose a graded valence, scored on the graded metric, where it is validated more strongly than
  binary accuracy shows.
- **The signed-relation SHAPE is confirmed on the brain's OWN graded metric.** Across pairs, antonymy
  FLIPS rated valence (true-rating corr **-0.556**), synonymy PRESERVES it (**+0.483**), random ~0.00.
  This is the cleanest possible statement of "antonym = flip, synonym = preserve": measured directly on
  human valence ratings, not inferred from accuracy.
- **But opposition is NOT a reflection of any word-intrinsic code -- it is an irreducible RELATION.**
  In embodied space, antonym pairs (embodied valence-axis corr **+0.270**) are INDISTINGUISHABLE from
  synonym pairs (**+0.266**): the flip is geometrically INVISIBLE in the features, because opposites
  share everything except their sign. So no similarity metric or feature space can compute the flip;
  it must be carried by the explicit antonym relation. (Fourth independent confirmation of
  irreducibility, and the sharpest: the flip is -0.56 on the brain metric yet 0.00 in the geometry.)
- **POSITION:** the embodied valence axis is ASYMMETRIC -- it separates POS anchors (92% on the
  positive end) far better than NEG (44%), so even a graded embodied readout is a weak, one-sided proxy.

**Net fidelity verdict:** the mechanism's SHAPE is right where the brain forces it (signed relations,
an explicit irreducible flip, graded confidence) and our only real gap was the READOUT -- reporting a
binary pole instead of the graded valence the vote already computes. That is a reporting/scoring fix,
not a mechanism change.

## GENERALIZATION DRILL (v5) -- is the whole result a VERB artifact?
Every v1-v4 number is on polar verbs. Tested across parts of speech (Warriner ratings; WordNet
relations per POS; grounded axis built from the verb anchors).
- **The signed-relation structure is UNIVERSAL.** Measured directly on human ratings, "antonym flips
  valence, synonym preserves it" holds for every POS, strongest where antonymy is most central:
  ADJECTIVES antonym rating-corr **-0.825** / synonym **+0.756**; VERBS -0.717 / +0.637; NOUNS -0.578
  / +0.710; random ~0.00 throughout. So the mechanism's core is a general lexical property, not a verb
  artifact -- and adjectives (antonymy's home turf, 215 antonym pairs) are where it is sharpest.
- **The verb-anchor embodied valence axis transfers to adjectives but not nouns.** ADJ pole-acc 0.582
  on 1925 (floor 0.513, CI-separated; graded rho 0.181, twin ~0). NOUN 0.562 on 4250 sits AT the
  imbalanced floor 0.564 (NOT separated) though a weak graded rho 0.133 survives -- an honest bound:
  cross-POS embodied transfer works for adjectives, is too weak for nouns.
- **Headroom is small, and we are near it.** A supervised ridge (grounded 12-dim -> continuous valence,
  5-fold CV = the known-answer arm) ceilings at only 0.276 (ADJ) / 0.344 (NOUN); the unsupervised
  anchor-axis already captures 66% (ADJ) / 39% (NOUN) of that. Embodied features simply contain little
  linear valence; pushing the grounded reader harder is not worth it (and nouns' remaining headroom is
  reachable only by supervision -- less brain-foundational than anchor+propagate).

## ADJECTIVE BUILD (v6) -- the prediction, built and confirmed
v5 predicted signed propagation would be STRONGER on adjectives. Built it, two anchor sources, scored
vs Warriner (anchors + their antonyms excluded from the population; independent gold):
- **HAND-authored canonical adjective seed (50 words, balanced, chosen from affective knowledge not
  Warriner value): 0.8845 on 1100 adjectives (56% coverage), CI95 [0.866, 0.902], floor 0.548 ->
  CI-separated.** Far above the verb organ (0.726 on 485 = 25%) in BOTH accuracy and coverage. 1-hop
  0.922 (383), 2-hop 0.865 (717). Sign-scramble twin at chance (0.483/0.483/0.492 -> LOSES by 0.40);
  shuffle-label twin loses (mean ~0.52); antonym flip load-bearing (sign-blind 0.856). This is the
  strongest result in the whole problem, exactly where the brain says opposition is most central.
- **DERIVED anchors -- a cross-POS BOOTSTRAP with ZERO new hand-labelling: 0.8174 on 367**, CI95
  [0.778, 0.857], floor 0.561 -> CI-separated. Anchors are the 37 adjectives reachable from the vetted
  52-VERB seed via valence-preserving derivational links (destroy -> destructive), labelled by the
  verb's pole. So valence BOOTSTRAPS across parts of speech through the relation graph: a grounded verb
  seed seeds an adjective organ for free. Sign-scramble twin at chance (the clean control); the
  shuffle-label twin is NOISY here (0.70/0.21/0.66 -- only 37 anchors, so a permutation can preserve
  much structure), so the sign-scramble is the load-bearing control and DERIVED is a proof-of-concept,
  not a headline. Antonym flip matters more here (sign-blind 0.763, -0.054) -- the sparser the anchors,
  the more the explicit flip carries.

**So the mechanism generalises AND improves on adjectives, and it can be seeded across POS from the
existing verb lexicon for free.** Authoring/landing an adjective stage in the live organ is a change
to hdlab (board Q111) -- a SUGGESTED follow-up for the architect (below), proven here in experiments/.

## PROPOSED hdlab change (NOT landed -- board Q111; strategy session lands it)
Replace Stage B (taxonomic path_similarity vote) in `hdlab/wordnet_polarity_propagation.py` with
signed lexical-relation propagation:
1. Build signed neighbours over antonym (sign -1) + synonym/derivational/similar-to/also-see/
   verb-group (sign +1), restricted to verb senses (already the scope).
2. Signed BFS to 2 hops; vote `pole x path_sign x gamma^(hops-1)`; abstain on an exact tie. This
   SUBSUMES Stage A (the antonym-into-anchor case is the 1-hop antonym path) -- so it collapses two
   stages into one and generalises the accurate stage from 19 to 119 items at the same accuracy.
3. Net effect on the held-out set: coverage 326 -> 485 (+49%), accuracy 0.6595 -> 0.726, on an axis
   PROVEN to carry valence (sign-scramble + label-shuffle both at chance) rather than one measured to
   carry none. gamma is immaterial (sweep-flat); keep the abstain margin at 0 (do NOT buy accuracy by
   raising a gate -- the brief's own rule, applied symmetrically).
The pseudo-count fusion contract downstream (`pseudo_counts_from_dictionary`) is unchanged: same
DictLookup shape, confidence from the vote margin.
4. **Expose the GRADED valence** (v4): the signed-vote magnitude tracks continuous human valence at
   Spearman 0.400, so the confidence field already encodes valence INTENSITY, not just a pole. Keep
   returning `(pole, |vote|)` -- but the strategy session should score the organ on the GRADED metric
   (correlation with the continuous rating), not only binary accuracy, because the binary metric hides
   ~half of what the mechanism captures. No mechanism change; a scoring/reporting fidelity fix.

**Optional third stage for coverage** (if the consumer wants an answer on every word, not just the 485
the relations reach): after the signed lexical stage abstains, fall back to the grounded evaluative-
axis prior (Lancaster+Brysbaert, via `hdlab.grounded_similarity` which is already wired) with the
antonym flip retained. That yields 0.597 on 1962 items (99.5% coverage), every item above its floor.
Land this ONLY if downstream wants breadth over per-item accuracy -- it trades 0.726 on 485 for 0.597
on 1962. Keep it a SEPARATE lower-confidence stage so the fusion can weight it below the sharp one.

**SUGGESTED to the architect (I do not file problems): extend the organ to ADJECTIVES.** v6 proves it
is the strongest form of this mechanism (0.884 on 1100 vs verbs' 0.726 on 485), and it can be seeded
across POS from the EXISTING verb lexicon for free (derived-anchor bootstrap, 0.817). Landing it means
adding an adjective anchor set + adjective-scoped signed neighbours to hdlab -- a new stage, not a tweak
-- so it is the architect's to scope and vet (the hand seed is OUR-INVENTION-UNDER-TEST and needs the
usual vetting; the derived-anchor route needs zero new labelling and is the cleaner start).

## What I did NOT establish / would withdraw first
- **Withdraw first:** the exact 1-hop 0.8403 as a stable point estimate -- n=119, CI [0.769, 0.904];
  the ROBUST claim is CI-separation over the own-subset floor, which holds at every hop and setting.
- **The shuffle-label null has a tail:** 1 of 30 permutations reached 0.743 (> real 0.726); the
  permutation p is 0.033, not <0.001. The sign-scramble twin (0.49, no tail) is the stronger control
  and is what I lean on for "the relation's sign carries valence."
- **Not a paired win over Stage B** -- explicitly a tie on the underpowered overlap (stated above).
- **Single value per word, no context.** The plan's target is a CONTEXT-conditioned valence; this
  assigns one value per lemma. So this is a strong FLOOR for the direction on isolated lexemes, not a
  test of context-conditioned valence -- the same caveat the archive carries.
- **Warriner gold is incomplete/ambiguous at the margins** (|V-5|>=1 threshold); gold noise biases
  AGAINST the mechanism (conservative). WordNet is used only as a population filter for verb senses,
  never to grade -- the gold pre-dates the organ by years (the free predictor).
- **The embodied/grounded axis is WEAK (v3):** 0.562 CI-separated over floor but the margin is small
  (+0.043) and a k-NN vote does not clear the floor -- only the prototype/evaluative-axis reader does.
  I would NOT claim embodied similarity is a strong valence axis; the robust claim is only that it
  carries valence at all (Spearman outside null), unlike taxonomy. The hybrid's 0.597 buys coverage at
  a real accuracy cost vs the pure lexical 0.726 -- it is an option, not an unambiguous improvement.

## KEY REALIZATIONS
1. **The decisive control was the SIGN-SCRAMBLE twin, and the brief did not ask for it.** The brief's
   required twin (shuffle anchor LABELS) proves the labels matter; but the slug's actual claim is that
   *the relation carries valence*, which only the SIGN-SCRAMBLE twin (randomise flip-vs-preserve, keep
   topology) can test. It collapses to chance with no tail -- cleaner than the label twin -- and it is
   what turns "propagation works" into "the signed relation structure is what makes it work."
2. **"Beat Stage B on the overlap" is unwinnable BECAUSE the brief's own prior finding is true.** Once
   taxonomic distance is known to carry no valence, it must select DIFFERENT neighbours than the
   valence-bearing relations -- so the two axes are near-disjoint and their overlap is a tiny easy set
   where any mechanism ties. The right move was to stop trying to force the paired test and compare
   each axis to its own-subset floor. The disjointness IS the evidence that the axes are different.
3. **The accurate half was never really "antonymy only" -- it was "signed relations, of which antonymy
   is the rare flip case."** Generalising Stage A's 19 items to 119 came not from finding more antonyms
   but from adding the PRESERVE relations (synonym/derivational/verb-group) at the same 1 hop, at
   identical accuracy. The organ had been using one signed relation and ignoring the others.
4. **More brain-faithful did not mean better -- and that was the point.** Recurrent settling (the
   attractor form) tied the one-line shortest-path vote. That is a real finding about the phenomenon:
   affective valence is a SHORT-RANGE signed spread, so the integration scheme is nearly irrelevant.
   Reporting the convergence (rather than shipping the fanciest arm) is the honest result.
5. **OPPOSITION IS NOT A SIMILARITY RELATION, AND VALENCE IS EXACTLY WHAT OPPOSITION INVERTS.** The
   deepest realization, and it survived the substrate push: antonyms are similar in every space we can
   build (embodied sensorimotor AND lexical), because "hot"/"cold" and "love"/"hate" share almost
   everything except their sign. So NO similarity metric -- however brain-faithful its grounding -- can
   supply the valence flip; it must be an explicit operator. That is why the organ's accurate half was
   antonymy, why a similarity vote alone plateaus at chance on opposites, and why the correct mechanism
   is similarity-that-preserves PLUS opposition-that-flips. Testing the embodied substrate did not
   replace v1 -- it explained why v1's shape (signed, with an irreducible flip) is forced by the brain.
6. **"More brain-foundational substrate" and "better operator" came apart, and both answers were
   real.** Embodied space is the more brain-foundational GROUNDING of valence (proven: it carries
   valence where taxonomy does not), yet the lexical PRESERVE relations are the better propagation AXIS
   (0.726 vs 0.562), because they are a valence-SPECIFIC similarity while embodied similarity is broad.
   The push farther did not overturn the answer; it located exactly where "brain-foundational" and
   "effective" diverge -- and the hybrid captures both.
7. **-0.56 on the metric, 0.00 in the geometry -- the single number that settles the opposition
   question.** The focused v4 drill measured antonymy two ways: on human valence RATINGS it flips
   strongly (true-rating corr -0.556, synonyms +0.483); in the embodied FEATURE geometry it is
   invisible (antonyms +0.270, synonyms +0.266 -- identical). That gap is the whole finding: valence
   opposition is real and strong but lives in NO feature space, so it can only be an explicit relation.
   It also exposed our one genuine fidelity gap -- a binary readout for a graded brain quantity -- which
   the vote magnitude already fixes (rho 0.400 with continuous ratings). The drill sharpened the
   mechanism's justification without changing the mechanism: it is the shape the brain forces.
8. **The verb result was a slice, not an artifact -- and the test that proved it needed NO anchors.**
   The cleanest generalization check bypassed the (verb) anchor set entirely: just correlate the
   ratings of antonym pairs and synonym pairs, per POS. "Antonym flips, synonym preserves" holds for
   adjectives, verbs, and nouns, scaling with how central antonymy is to each class. Measuring the
   RELATION directly on the gold -- rather than measuring a mechanism that uses the relation -- is what
   made the generalization claim clean and anchor-independent.
9. **VALENCE BOOTSTRAPS ACROSS PARTS OF SPEECH FOR FREE (v6).** The strongest result -- 0.884 on
   adjectives -- came where the brain says opposition is most central, confirming the whole direction.
   But the sharper realization is the DERIVED-anchor arm: adjective anchors reached from the grounded
   VERB seed via derivational links (destroy -> destructive), with ZERO new hand-labelling, still score
   0.817. So a small grounded affective seed in ONE part of speech propagates to seed an organ in
   ANOTHER through the relation graph. This is the anchor+propagate premise turned on itself -- the
   anchors are themselves reached by propagation -- and it is how the brain would bootstrap a large
   evaluative lexicon from a few grounded exemplars without re-grounding every word.

## TLDR
The component decides if a word means something good or bad by starting from ~50 hand-labelled words
and reasoning outward. It was doing that along the wrong kind of link -- "sits near it in a dictionary
map" -- which we already knew carries no good/bad information. I rebuilt it to reason along the links
that DO carry good/bad: an OPPOSITE-OF link flips it, a same-meaning link keeps it. That version is
right about 73 times in 100 and ventures an answer on a quarter of the words -- versus the old 66-in-
100 on a sixth -- and I proved the links are really carrying the signal: scramble which links flip vs
keep, and it drops to a coin toss. The brief's specific success test (beat the old "nearby in the map"
method head-to-head) can't be run fairly, because the two methods answer almost totally different
words -- so I compared each to the right yardstick instead and said so plainly. Pushing further, the
same idea works EVEN BETTER on describing-words (good/bad, kind/cruel) -- 88 in 100 on more than half
of them -- and it can teach itself the describing-word starting set from the action-word one for free.

## QUESTIONS
None.

## NEXT STEPS
1. Strategy/architect: re-verify with the witness, then land the proposed Stage-B replacement (one
   signed-propagation stage subsuming both current stages).
2. The 2 remaining "no anchor in range" corners are a rounding error; do NOT expand the anchor set as
   the fix (78 of 83 abstentions are disagreements, not reach gaps -- and signed propagation cuts them
   by answering 485 not 326).
3. SUGGESTED to the architect (I do not file problems): (a) an ADJECTIVE stage -- proven strongest here
   (0.884), seedable from the verb lexicon for free; (b) score the organ on the GRADED metric, not only
   binary accuracy; (c) the context-conditioned form (one valence per word-in-context) -- the plan's
   actual target, a separate build; (d) learned affective grounding (derive anchors from experience) --
   the last labelled OUR-INVENTION. These are hdlab/plan changes for the architect to scope, all proven
   or scoped here in experiments/.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT. Re-verified scaffold-free (test_signed_lexical_valence_propagation.py PASS: 1-hop 0.8403 CI-lo 0.7742 > floor 0.5798; signed 2-hop 0.7258 vs sign-blind 0.6810; sign-scramble twin -> 0.49; shuffle-label p=0.000; grounded carries valence rho 0.0429 outside null; opposition -0.556 on ratings yet 0.270~0.266 in embodied geometry; graded rho 0.400; adjectives HAND 0.8845). Replaced taxonomic Stage B (carries NO valence) with signed lexical-relation propagation (antonym flips, synonym/derivational/verb-group preserve); the sign-scramble twin proves the RELATION'S SIGN carries valence. Literal paired-vs-Stage-B bar ties (near-disjoint by construction); solver invoked the alternative-instrument clause correctly (own-subset floor + info-free twins). Deep findings: opposition IRREDUCIBLE (no similarity space supplies the flip); embodied is the deeper grounding but weaker axis; graded readout hidden by binary pole; universal across POS, sharpest on adjectives. Review in PROBLEM.md; priority cleared. hdlab landing (Stage-B replacement in wordnet_polarity_propagation.py, default-off + witness) recorded as a proven-ready deliberate landing. AUDIT UPDATE folded into notes/BRAIN_FOUNDATIONAL_AUDIT.md (affect/valence tier). Committed (no push).

LANDED_BY_STRATEGY: 2026-08-26 -- signed lexical-relation propagation landed in hdlab/wordnet_polarity_propagation.py as dictionary_lookup(..., signed_propagation=True), DEFAULT-OFF (byte-identical when off). Promoted signed_neighbours/signed_reach/predict_signed (credited clean-lift); verified IDENTICAL to the cell mechanism across 22 probes (0 mismatches). Witness verification/test_valence_signed_propagation_landing.py PASS (default byte-identical; sign load-bearing; coverage 16>6 vs Stage A+B; graded valence exposed). Organ self_test PASS with new signed checks; solver's full witness still PASS. Turn on per-consumer.
