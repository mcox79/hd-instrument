# Deeper brain-fidelity drill: is the adjective signed-magnitude op good enough, and how much further can we push it?

Second, finer-resolution drill (owner: "do another, deeper brain foundational research drill. is there further we
can push this?"). Web-grounded literature drill (hdi_research, 2026-08-27) + three decisive probes run on owned
data. PINNED / OUR-INVENTION labelled. The disk outranks the brief and the first drill where they disagree.

## 0. THE META-FINDING (the deepest one): the benchmark is BLIND to two of the brain's three magnitude operations

Spearman rho against human ratings is INVARIANT to any monotone transform of the axis coordinate. The two things
the brain provably does to magnitude -- **Weber/logarithmic compression** and **tuned place-coding** -- are
monotone re-parameterizations of the same scalar. So a static 1-D projection scoring rho 0.72 can look
"good enough" *precisely because rho cannot see the brain's actual code.* The projection faithfully implements the
brain's FIRST magnitude operation (a monotonic summation/accumulator readout) and silently omits the SECOND (a
log-compressed TUNED POPULATION that supports discrimination) and the THIRD (a POLE-ANCHORED, context-relative
REFERENCE-POINT comparison that produces the semantic-congruity and markedness effects). **"The read-out is ONE
operation where the brain has THREE" recurs at the magnitude level, one level below the word-class routing.**

## 1. The neural code [PINNED]: summation -> tuned/log-Gaussian

Magnitude is carried by (at least) two codes in series: monotonic "summation" neurons in LIP (Roitman/Brannon/
Platt 2007) feeding non-monotonic TUNED "number neurons" in PFC/IPS whose tuning is Gaussian on a LOG axis --
the neural signature of Weber-Fechner (Nieder 2007; Dehaene 2003; Piazza 2004). A single scalar projection IS the
summation code; it is faithful to stage 1 and to rank-order, and it DISCARDS the log-compressed tuned population
that makes discriminability degrade with magnitude. **Consequence we must state honestly: a log-compressed +
tuned-basis encoder is more brain-faithful but CANNOT improve rho (monotone invariance) -- its value shows only
under a DISCRIMINATION/COMPARISON metric, which the current benchmark does not provide.**

## 2. ATOM's shared "more/less" axis [PINNED as PARTIAL] -- TESTED on our data, strong version REFUTED

Walsh's ATOM (2003) posits a generalized magnitude metric shared across number/space/time/brightness, supported by
cross-dimensional interference (size-congruity, SNARC; Bueti & Walsh 2009). But the STRONG single-axis reading is
contested: Marghetis et al. 2018 ("not singularly represented") and the GradiATOM meta-analysis find PARTIAL
sharing / cortical gradients that DISSOCIATE by mid-childhood -- "shared polarity component + dimension-specific
gain," not one axis.

**PROBE B (run on our 4 dimension axes -- valence/arousal/dominance/concreteness):** the axes are largely
ORTHOGONAL (pairwise cosines |<=0.36|); the top shared component explains only ~0.45 of axis variance, barely
above the RANDOM-axis twin (~0.38); a shared-axis + per-dimension-residual model gives NO clean win (it helps the
weak arousal/dominance dims modestly but HURTS valence and concreteness). **=> the strong single-magnitude-axis
claim is REFUTED on our representation; independent per-dimension axes (the v1 design) are the faithful choice,
matching the partial-sharing literature.** [OUR-INVENTION vindicated by test.]

## 3. Semantic congruity + reference points [PINNED] -- the flagship faithfulness gap the benchmark cannot see

The distance effect always co-occurs with a SEMANTIC-CONGRUITY effect (Banks/Clark/Lucy 1975): "choose the larger"
is faster for large pairs, "choose the smaller" for small pairs -- comparison is ANCHORED TO A POLE, not a
symmetric subtraction (Banks balloons-vs-yoyos: the fast direction is set by the REFERENCE, not the stimuli).
MARKEDNESS is the lexical face of the same asymmetry (unmarked "tall" names the whole dimension + high pole;
marked "short" is pole-only); the scale's ZERO/direction is asymmetric. **Our op is a symmetric dot product; the
brain runs a directional, pole-anchored, context-relative comparison.** The most brain-faithful NEXT mechanism is a
pole-anchored reference-point COMPARATOR -- but validating it needs a COMPARISON benchmark (congruity/min-effect),
which is not cleanly on disk, so it is filed as the flagship follow-up, not claimed here.

## 3b. Opposition is RELATIONAL, not raw-geometric [PINNED] -- TESTED, and it refines v1

The irreducibility finding predicts raw geometry cannot separate antonyms from synonyms (they share distributional
context; Nguyen 2016 needed injected lexical-contrast). **PROBE A (antonym vs synonym adjective pairs, non-circular
disjoint axis/test vocab split, n=341+341):** raw GloVe cosine AUC 0.356 -- it INVERTS (antonyms cos 0.360 >
synonyms 0.262); the geometric anchored-axis opposition-product is modest (0.587, beats raw cosine +0.231
CI[0.191,0.269] but weak); only the DEFINITIONAL channel (0.969) and the EXPLICIT antonym relation (oracle,
labels ARE the relation) separate them cleanly.
**=> a precise decomposition of the adjective op: signed MAGNITUDE (position on the scale) IS geometrically
recoverable (v1: valence 0.72), but OPPOSITION (is this pair opposite?) is NOT -- it must come from the explicit
relation (or the definitional channel). Two computationally distinct sub-operations with different homes.**

## 4. Acquisition/grounding [PINNED] -- perceptual magnitude, TESTED, a real metric move

ATOM ties magnitude to the ACTION/perception system. Denotational scalar adjectives (size/brightness/weight/
concreteness) ground PERCEPTUALLY, independently of the sensorimotor-SIMILARITY route that was ruled out (the
size-weight illusion shows a perceptual heaviness representation independent of sensorimotor prediction).
Concreteness is the tell: "concrete" has NO clean lexical antonym pole, so an antonym-anchored axis MUST
underperform (v1: 0.26).

**PROBE C (Brysbaert concreteness recovery, n=5226):** a GloVe axis anchored by high- vs low- Lancaster
PERCEPTUAL-strength words recovers concreteness at 0.525 vs the antonym axis 0.260 -- **+0.266 CI[0.237,0.294],
shuffled-Lancaster twin loses (-0.008).** **=> denotational-scalar magnitude grounds PERCEPTUALLY, not in antonymy; the router must anchor
each adjective dimension in its APPROPRIATE source (evaluative -> antonym/affect poles; perceptual/denotational ->
sensorimotor strength). A single antonym-pole anchor is the wrong supply for denotational scales.**

## 5. Two circuits, not one adjective system [PINNED]

Evaluative value lives in OFC/vmPFC/amygdala ("common currency"); denotational magnitude in IPS; the two
dissociate (Kober factor analysis). Our recovery gradient valence 0.72 >> dominance 0.41 > arousal 0.28 ~=
concreteness 0.26 is exactly the Osgood EPA factor-strength order AND the two-circuit prediction: the one op we
apply is well-matched to the EVALUATIVE circuit (valence has the richest lexicalized antonymy) and poorly matched
to DENOTATIONAL dimensions -- which PROBE C then fixes by switching the grounding source. **The gradient is
evidence we were running one op across two systems.**

## VERDICT: keep the projection as the backbone; the fidelity levers are (a) grounding source per dimension, (b) a
reference-point comparator, (c) a discrimination benchmark

The static SemAxis projection is faithful to the brain's stage-1 summation readout and is the right ENCODER. It is
a convenient approximation of the DECISION/comparison operation, and the current benchmark cannot expose that. The
cheapest real win (SHIPPED here): dimension-appropriate grounding (PROBE C, concreteness 0.22 -> 0.54). The
deepest faithfulness build (FILED, needs a new benchmark): the pole-anchored reference-point comparator.

## Ranked next mechanisms (status after this drill)

1. **Dimension-appropriate grounding source** (evaluative -> antonym poles; denotational -> perceptual strength).
   TESTED + WON (PROBE C). READY to wire into the router.
2. **Reference-point / pole-anchored comparator** (congruity + markedness + Kennedy relative standard). FILED as
   flagship; needs a comparison/congruity benchmark (not on disk) -- rho is provably blind to it.
3. **Relational opposition** (explicit antonym relation for the sign; definitional channel for pair-separation).
   TESTED (PROBE A) -- geometry cannot do opposition; use the relation. Compose with the magnitude projection.
4. **Independent per-dimension axes** (NOT one ATOM axis). TESTED (PROBE B) -- strong shared-axis REFUTED on our
   data; keep independent axes.
5. **Log-compressed tuned-basis encoder** (Weber/number-neuron code). Faithful but rho-invisible; build only with
   a discrimination metric. FILED.
6. **Context-relative standard** (Kennedy relative/absolute; "tall for a jockey"). Needs a comparison-class corpus.
   FILED.

## 7. INTENSITY IS MARKEDNESS, NOT GEOMETRY -- the wall drilled through (owner: drill every negative to resolution)

Acquiring the WordNet-INDEPENDENT crowd intensity-ordering golds (Cocos 2018 crowd n=79; Wilkinson & Oates n=42;
+ de Melo, flagged) via `tools/fetch_scalar_adj_intensity.py` produced a hard NEGATIVE, then -- on drilling it --
the real mechanism.

- **The static SemAxis op does NOT order fine within-scale intensity** (warm<hot<scorching). On the proper
  chance floor (mean |rho| of 50 random axes on the SAME tiny scale -- a 3-term scale has E|rho|~0.67 by chance):
  crowd SemAxis |rho| 0.680 vs random-floor 0.643 (+0.037, CI straddles 0); wilkinson/de Melo the op is BELOW
  its floor; orientation-resolved accuracy 0.45-0.63 (~chance). The op captures the DIMENSION/pole (coarse), NOT
  the graded degree -- exactly the log-compressed/tuned-code gap this drill predicted rho was blind to, now shown
  on a benchmark that CAN see it. [A first pass reported mean |rho| 0.68 as a win; that was small-n |rho|
  inflation -- the random floor is also ~0.64. Corrected.]
- **MARKEDNESS orders intensity, CI-above chance, on the WordNet-INDEPENDENT sets.** Stronger scalar terms are
  RARER (lower frequency) and LATER-ACQUIRED (higher AoA) -- Greenberg markedness; Zipf; Horn scales; scalar
  implicature. Direction is FIXED A PRIORI (no orientation bit). Pooled pairwise accuracy (bootstrap over scales,
  chance 0.5): crowd FREQ 0.648 [0.559,0.727], AoA 0.691 [0.602,0.771]; wilkinson FREQ 0.750 [0.604,0.865];
  de Melo FREQ 0.655 [0.566,0.743] -- all CI-above 0.5, with the SHUFFLED-FREQUENCY twin at chance (0.50-0.54).
  Norms: the AoA-51715 frequency + age-of-acquisition columns (independent, non-WordNet). [experiment
  `exp_adjective_intensity_ordering_v1.py`.]
- **=> the adjective magnitude op is TWO sub-operations:** DIMENSION + POLARITY (which scale / which pole) =
  geometric SemAxis projection (validated by v1 rating-recovery, valence 0.72); DEGREE / INTENSITY (how far along,
  fine ordering) = MARKEDNESS (frequency / acquisition order), NOT geometry. This is brain-faithful and
  DEVELOPMENTALLY grounded (a child learns "big" before "enormous"; the weaker pole is the unmarked, more
  frequent, earlier-acquired one) -- and it is Kennedy's "scale built from ordering evidence" (Q4a) made concrete:
  the ordering evidence in the lexicon is frequency/acquisition, not the antonym endpoints.

## Residual honesty

- The reference-point comparator and the tuned-basis encoder are the two most brain-faithful upgrades and BOTH are
  invisible to the rating-recovery benchmark. Claiming them requires a comparison/discrimination dataset we do not
  own -- so they are FILED with their can-fail tests, not claimed.
- PROBE A's EXPLICIT-relation arm is an ORACLE (labels are the relation); the meaningful contrast is raw-cosine
  (fails/inverts) vs definitional (separates). The signed-magnitude geometric opposition-product is ~chance --
  honestly reported, and it is WHY opposition must be relational.
