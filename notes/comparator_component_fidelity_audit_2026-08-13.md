# Comparator component-by-component MATHEMATICAL FIDELITY AUDIT

Filed 2026-08-13. Branch `dataprep/mcguffey-graded-corpus`, HEAD at audit time `4093464b4`.
Scope: THE SEMANTIC COMPARATOR — the thing that decides whether two concepts are the same or
different. Method mandated by USER: *"break down the component into constituents and drill how the
brain does it and work, component by component, ensuring that each operates just like the brain, in
particular in the MATHEMATICAL OPERATIONS AND REPRESENTATIONS."*

The failure this corrects: on 2026-08-13 four cells tested WHOLE MECHANISMS and all four failed,
because nobody had first checked, PER CONSTITUENT OPERATION, whether our arithmetic is the brain's
arithmetic. A gap table naming components is not enough; the unit of work is the equation.

Prior drill (biology, not re-derived here): `notes/brain_drill_encoder_lexical_semantics_2026-08-13.md`
(`471798502`) + five lit scans `notes/lit_scan_*_2026-08-13.md` (`ce2e99388`).

---

> **SUPERSEDED IN PART, 2026-08-14 — READ THIS FIRST.** Row C1's *mechanism* claim (that
> per-component magnitude destruction is the BINDING CONSTRAINT on near-neighbour discrimination)
> was tested, produced a HARD_PASS, and was then **refuted as an explanation** by an adversarial
> landed-VET: `notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md`. The numbers in
> this note are correct and reproduce bit-exactly; the *prototype-operator argument is
> mathematically correct and predicts the right direction*; but it is NOT the dominant cause of the
> measured effect. The unmodified quantised comparator at d=1024 beats the graded one at the live
> d=256, and destroying all magnitude in the unprojected term space costs only 27% of the effect.
> Correct reading: **at d=256 the quantised comparator is capacity-limited.** Row C7
> (representation format / capacity), which this audit ranked LAST, is promoted to the head of the
> queue. Two further corrections are recorded inline below: the log-IDF mechanism I predicted was
> refuted, and I transposed Carandini & Heeger.

## HEADLINE — ONE ARITHMETIC DEFECT, FIVE SITES, AND IT IS A PROTOTYPE OPERATOR

Every composition step in this substrate ends in a **per-component magnitude-destroying
normalisation**: `np.sign(...)` on the real path, `s / |s|` per component on the FHRR path. The
comparator therefore never sees HOW MUCH evidence a dimension carries, only WHICH WAY it leans.

That is not a small infidelity. It is mathematically a **prototype extractor**. Write a concept's
accumulated evidence as `shared + distinctive`, where `shared` is the category-common component
(high magnitude, present in most encounters) and `distinctive` is what separates goat from sheep
(low magnitude, present in few). Then

    sign(shared + distinctive) = sign(shared)     wherever |shared| > |distinctive|

which is almost everywhere. **The distinctive component is annihilated by construction, and the
modal/prototype pattern is what survives.** Rogers, Lambon Ralph, Garrard, Bozeat, McClelland,
Hodges & Patterson 2004 (*Psychol Rev* 111:205-235) describe exactly this as the signature of a
DEGRADING ATL hub: distinctive features go first, shared features survive, errors appear as
WITHIN-CATEGORY COORDINATE CONFUSIONS (couch -> "chair", goat -> "sheep"), and representations
drift toward the prototype.

**Our comparator has semantic dementia built into its arithmetic, and coordinate confusion is
precisely the failure we cannot fix.**

The brain's actual normalisation is the opposite operation. Divisive normalisation (Carandini &
Heeger 2012, *Nat Rev Neurosci* 13:51-62; Heeger 1992) is

    r_i = x_i^n / (sigma^n + SUM_j x_j^n)          <- denominator SHARED across the pool

A **shared** denominator preserves every ratio inside the pool: a strong distinctive dimension stays
strong relative to a weak one. A **per-component self** denominator (`x_i / |x_i|`) sets every ratio
to exactly 1. We named our operation after the brain's and implemented its inverse.

> **CORRECTION (2026-08-14, filed with `preregs/2026-08-13_task_local_normalisation_pool_AMENDMENT_A1.md`).**
> The sentence above is right about what our operation destroys, and it is the finding this audit
> stands on. But the PRESCRIPTION I derived from it in row C1 field 5 — "apply divisive
> normalisation with the population as the pool" — TRANSPOSES the cited equation and is wrong. In
> Carandini & Heeger the pool index `j` ranges over other NEURONS IN THE SAME POPULATION at the
> same moment, so the denominator is a **SCALAR for the whole representation**. Cosine is invariant
> to a scalar, so canonical divisive normalisation **cannot change a two-candidate argmax at all** —
> not weakly, identically not at all. What I implemented and measured instead (per-dimension mean/sd
> across the anchor population) is efficient-coding ADAPTATION (Laughlin 1981; Fairhall et al.
> 2001), a different real mechanism, and it measured NULL (+0.0018, CI [-0.0030,+0.0065]) in
> `data/exp_graded_divisive_comparator_v1`. The per-dimension gain that CAN act here is **semantic
> control gain** (row C4), and the correction is recorded rather than silently patched because the
> mis-citation is exactly the kind of error this audit method exists to catch.

### Measured, this session, on the live path

`experiments/diag_anchor_field_geometry_v1.py`, 400 concepts, 70 held-out profile sentences each, d=256,
byte-identity to `hdlab.grounding_acquisition_loop.context_vector` asserted before measuring:

| anchor field transform | ‖field mean‖ / ‖anchor‖ | top-1 PC var | participation ratio | mean pairwise cos | p99 pairwise cos |
|---|---|---|---|---|---|
| **SIGN (live code)** | **0.5841** | 0.0296 | 126.6 | **0.3397** | 0.5572 |
| GRADED (sign removed) | 0.3545 | 0.0607 | 77.0 | 0.1319 | 0.3373 |
| GRADED + field-centred | 0.0000 | 0.0607 | 77.0 | -0.0020 | 0.2085 |
| GRADED + divisive-norm (z) | 0.0000 | 0.0558 | 80.8 | -0.0020 | 0.2064 |
| SIGN + divisive-norm (z) | 0.0000 | 0.0305 | 131.0 | -0.0022 | 0.1739 |

Read that first row as an indictment. **Under the live code, 58% of every concept vector's norm is
the field mean — the component shared by all 400 concepts — and two arbitrary unrelated concepts sit
at cosine 0.34.** Concepts are near-duplicates of the population average before any near-neighbour
question is even asked. Removing the binarisation alone cuts the shared component to 0.35 and mean
pairwise cosine 2.6x; a brain-faithful divisive normalisation removes it entirely.

Also measured: the accumulated anchor sums have |value| p50=29, p90=74, max=615, and **13.85% of
dimensions carry |sum| < 10% of p90** — near-zero evidence. `sign()` rescales every one of those to
full ±1. So the operation does not merely discard the distinctive signal; it **amplifies pure noise
to maximum weight at ~1 dimension in 7**.

### The same claim, proven analytically with no corpus and none of our code

`experiments/diag_sign_annihilates_distinctive_v1.py`: two near-neighbours share a category
component S and differ only in a distinctive component D, at d=256 (the substrate's live context
dimensionality), 4,000 trials per row.

| |D|/|S| | cos(a1,a2) SIGN | cos(a1,a2) GRADED | frac pairs BIT-IDENTICAL under sign | D-recovery SIGN | D-recovery GRADED |
|---|---|---|---|---|---|
| 0.02 | 0.9821 | 0.9996 | **10.13%** | 0.1212 | 1.0 |
| 0.05 | 0.9552 | 0.9975 | 0.18% | 0.1841 | 1.0 |
| 0.10 | 0.9099 | 0.9900 | 0.00% | 0.2620 | 1.0 |
| 0.20 | 0.8216 | 0.9614 | 0.00% | 0.3716 | 1.0 |
| 0.80 | 0.4156 | 0.6077 | 0.00% | 0.6533 | 1.0 |

D-recovery is `cos(a1 - a2, D1 - D2)`: how much of the code's difference between the two concepts
IS the true distinctive difference. **At a 2% distinctive:shared ratio, one near-neighbour pair in
ten becomes BIT-IDENTICAL — not degraded, annihilated. At 10%, only 26% of the difference direction
is real distinctive meaning; the other 74% is quantisation noise.**

Note the second-order point, which matters for diagnosis: `cos(a1,a2)` is LOWER under sign than
under the graded code at every ratio. sign() makes near-neighbours look MORE separated while making
the separation MEAN LESS. A comparator can therefore show a healthy-looking margin and still decide
wrongly, which is exactly the pattern in the landed cell (`mean_winning_cos` 0.1476, accuracy
floor-hugging).

Secondary confirmation of the same defect in the code's shape: sign() RAISES the field's
participation ratio 77 -> 127, i.e. it flattens the spectrum toward noise. The brain's cortical
semantic code is DENSE, GRADED and LOW-effective-dimensional (Huth et al. 2012 *Neuron* 76:1210-1224,
first ~4 group PCs; Huth et al. 2016 *Nature* 532:453-458; Tiesinga et al. 2023 sEEG, ~two-thirds of
temporal-pole electrodes active per exemplar). The graded field is the one that looks like that.

---

## THE FIDELITY TABLE

Constituents as mandated: (i) how features are combined; (ii) how context modulates; (iii) how two
representations are compared; (iv) how a winner is selected; (v) how the result settles; (vi) what
the representation format is. Our code split (i) into TWO separate binarisations, so it gets two
rows. Rows are ordered by (predicts a known failure) x (we already own the organ).

### C1 — PER-OCCURRENCE COMBINATION: how one encounter becomes a vector   **[RANK 1]**

1. **BRAIN OPERATION.** Graded population response. Cortical neurons encode by firing RATE, and the
   information in a small population is carried by the graded rates, not by a thresholded
   present/absent code (Rolls & Tovee 1995; Panzeri & Treves information-theoretic decoding work).
   The pooling of afferent evidence is a weighted sum followed by DIVISIVE NORMALISATION with a
   POOL-SHARED denominator, `r_i = x_i^n / (sigma^n + SUM_j x_j^n)` (Carandini & Heeger 2012,
   *Nat Rev Neurosci* 13:51-62; Heeger 1992 *Vis Neurosci* 9:181-197) — the single most
   experimentally supported canonical cortical computation. Ratios inside the pool are PRESERVED.
2. **OUR OPERATION.** `hdlab/grounding_acquisition_loop.py:117-134`, `context_vector`:
   `acc += rng.choice([-1.,1.], size=d)` per content word, then **`out = np.sign(acc)`** (line 132),
   `out[out==0] = 1.0`. Kanerva random-indexing bundle followed by a **1-bit quantiser**. d=256
   (line 79). Also `hdlab/bundling.py:34-39` for the FHRR path: `s = vectors.sum(0)` then
   `out = s / |s|` PER COMPONENT — the complex-plane form of the same quantiser (amplitude to 1,
   phase kept). Also `hdlab/binding.py:104-105` `bsc_bundle`: sum then `sign`, ties to +1. Also
   `hdlab/concept_encoder.py:519-522`: `sign(acc) * top-K mask`.
3. **SAME OR DIFFERENT.** DIFFERENT — **WRONG OPERATION, and it is the inverse of the right one.**
   Both are "normalisation"; the brain's denominator is SHARED ACROSS THE POOL (preserves ratios),
   ours is EACH COMPONENT'S OWN MAGNITUDE (destroys every ratio, sets them all to 1). Not a
   different parameterisation of the same family — the opposite sign of the same knob.
4. **PREDICTS A KNOWN FAILURE?** YES, THREE.
   - *Near/far collapse* (`data/exp_near_vs_far_diagnostic_v1`, `804b02246`): the working channel
     degrades monotonically as pairs tighten, 0.276 pooled -> 0.304 FAR -> 0.125 NEAR (CI includes
     0). A prototype operator is exactly a mechanism that keeps category-level (FAR) information and
     loses within-category (NEAR) information.
   - *Differentia supply at chance despite coverage 2.9% -> 35.0%* (`9825510bf`): supplying more
     distinctive features cannot help when composition annihilates minority components. Supply and
     shape were confounded; this row separates them and predicts supply was never the binding
     constraint. (Consistent-with, not proven-by.)
   - *Distinctiveness weighting null* — **I PREDICTED THIS ROW WOULD EXPLAIN IT AND IT DOES NOT.
     SEE THE CORRECTION BELOW.**

**CORRECTION, same session, before this note was used for anything.** I hypothesised that the
log-IDF distinctiveness-weighting null (`data/exp_distinctiveness_weighted_composition_v1`,
`dbac1ae9c`) was caused by `bundle()`'s per-component renormalisation erasing the injected weights
one line later. **An adversarial numerical recompute REFUTES that hypothesis in both of its
mechanistic claims**, and I record the refutation rather than the prediction:

- Near-cancellation is 4.3x RARER under weighting, not commoner (0.68% vs 2.94% of components below
  10% of the concept's median |s_j|): unequal weights make exact destructive interference LESS
  likely. The "weights cause more noise amplification" claim is refuted by SIGN.
- The per-component step TRANSMITS more of the weighting perturbation than whole-vector L2 does
  (cos(weighted, unweighted) 0.9448 per-component vs 0.9897 under L2), the opposite of the
  prediction.
- Weighting hurts under BOTH normalisers (d' gain -0.682 per-component, -0.771 under L2), so the
  normaliser cannot be what killed it.
- The actual cause is visible in the cell's own file: `analytic_weighted_rho` vs
  `analytic_uniform_rho` (A 0.7254 vs 0.7406; B 0.6545 vs 0.6443; C 0.0826 vs 0.0790) is the EXACT
  weighted cosine in feature-incidence space — no `bundle()`, no normalisation of any kind — and it
  already misses the +0.03 band. With mean k=2.91 features per concept and a weight range spanning
  only 2.34x, log-IDF simply does not carry enough discriminative signal to restructure the cosine.
  Refuting the renormalisation does not revive the route.
- Verbatim verdict, for accuracy: `HARD_FAIL_SHAPE`, `B(CSKG) rho_w=0.536 d_uni=-0.018`,
  `C(CSKG no-lexrel, STRICTEST) rho_w=0.080 d_uni=-0.000`; arm A is VOID at 3.5% coverage.
  Reproduction check: the recompute bit-matched `_concept_vector_from` on 359/359 concepts and
  reproduced metrics.json's UNIFORM/WEIGHTED SimLex values 0.6762 / 0.7001 exactly.

**THE SAME RECOMPUTE PRODUCED INDEPENDENT SUPPORT FOR THIS ROW'S CORE CLAIM, on a different module
and a different number system.** Holding the weighting fixed and changing ONLY the normaliser —
`bundle()`'s per-component `s/|s|` versus whole-vector L2 `s/‖s‖`, which is Carandini-Heeger's
POOL-SHARED denominator — the near-vs-random separation on the FHRR lexical path is:

| normaliser | d' near/random | d' near/disjoint-random |
|---|---|---|
| per-component `s/|s|` (live `bundling.py:37-39`) | 4.843 | 6.070 |
| whole-vector L2 `s/‖s‖` (pool-shared denominator) | **6.030** | **8.959** |

**The per-component step costs 20-32% of d' by itself, with nothing else changed.** Two independent
paths — the real-valued context path (geometry table above) and the complex FHRR lexical path
(here) — show the same defect in the same direction. Scope, stated honestly: these pairs come from
the hand-authored `CONCEPT_FEATURES` lexicon, so this is a claim about what the OPERATION does to
whatever near/far structure exists, NOT a capability claim; the SimLex-999 arm at n=35
(se_rho ~ 0.177) is inside noise and licenses nothing. Note also that `bundling.py:41-42` ALREADY
uses whole-vector L2 for real-valued input — the brain-faithful form is present in the same
function, applied only to the other dtype.
5. **BRAIN-FAITHFUL REPLACEMENT.** Delete the terminal `sign()`; keep the graded sum; apply divisive
   normalisation with the ACTIVE POPULATION as the normalisation pool. **Do we own the organ?**
   Partly and wrongly wired: `hdlab/grounded_similarity.py:143-151` already computes exactly the
   right statistic — per-dimension z-scoring against the whole-population mean and sd — but only on
   the 12-dim sensorimotor table, never on the context-vector path. This is REUSE of an owned
   operation moved to a new site, not a new build.

### C2 — ACROSS-OCCURRENCE ACCUMULATION: how encounters become a concept   **[RANK 2]**

1. **BRAIN OPERATION.** Slow, offline, replay-driven cortical consolidation building a graded
   distributed store (CLS: McClelland, McNaughton & O'Reilly 1995; Davis & Gaskell 2009; Dumay &
   Gaskell 2007 sleep-gated lexical competition, 2021 meta-analysis g=0.50). Crucially the stored
   quantity is a graded synaptic weight distribution, and its statistics — how OFTEN a feature
   co-occurred, i.e. exactly the magnitude — are what distinctiveness is computed from (Cree,
   McNorgan & McRae; Tyler & Moss CSA: a feature's fate is set by DISTINCTIVENESS x CORRELATIONAL
   STRENGTH, both of which are frequency statistics).
2. **OUR OPERATION.** `hdlab/reading_grounding_loop.py:420-424` `ConceptSpace.observe`:
   `self._sums[lemma] += ctx_vec` (a genuine graded accumulator — correct), then
   line 446 `anchor_matrix`: **`mat = np.sign(np.stack([...]))`**, and line 456 `bundle`:
   `return np.sign(s)`. The graded accumulator is built and then **thrown away at read time**.
3. **SAME OR DIFFERENT.** DIFFERENT — **RIGHT OPERATION, WRONG PLACE.** We compute the brain's
   quantity (a graded frequency-weighted accumulation) and then discard it one line before it is
   used. A dimension where 36 of 70 encounters agreed is made bit-identical to one where 70 of 70
   agreed. This is the cheapest fix in the audit: the information already exists in memory.
4. **PREDICTS A KNOWN FAILURE?** YES — and it is the quantitative one. `sign()` at this site is
   what produces the measured ‖field mean‖/‖anchor‖ = **0.5841** and mean pairwise cosine
   **0.3397** above. Any 2AFC decision is then a small difference riding on a large common offset,
   which is the definition of a low-d' discriminator. It also explains why the landed
   context-conditioned cell hugs its floor (0.6395, `367ce167f`) instead of clearing it.
5. **BRAIN-FAITHFUL REPLACEMENT.** Return the raw `_sums` (already stored) and normalise against
   the anchor-field population. **Organ owned:** yes — `ConceptSpace` already holds the graded sums;
   `anchor_matrix()` merely needs a graded mode. Additive and default-off, following the repo's own
   `ReadoutConfig` precedent (`reading_grounding_loop.py:514+`).

### C3 — COMPARISON: how two representations are scored   **[RANK 3]**

1. **BRAIN OPERATION.** There is no cosine anywhere in the brain. Comparison is a DEEP RECURRENT
   NONLINEAR transformation whose core operation is pattern completion via a compact abstract label
   feeding back onto unimodal features (Jackson, Rogers & Lambon Ralph 2021 *Nat Hum Behav* 5:774+;
   Rogers, Cox, Lu, Shimotake et al. 2021 *eLife* 10:e66276 — ECoG, code reorganises at ~473 ms,
   anterior-posterior position predicts degree of dynamic change r^2=0.73). What is comparable to a
   similarity is the state's trajectory, and it is computed on a code that has already been
   normalised against the concurrently active population.
2. **OUR OPERATION.** `hdlab/reading_grounding_loop.py:665-677` `canonicalize_fast`:
   `nb = np.sign(new_raw_sum)` (a THIRD binarisation, of the query), then
   `sims[ok] = (mat[ok] @ nb) / (norms[ok] * nn)` — cosine between two ±1 vectors, which equals
   `1 - 2*Hamming/d`. **The decision variable of this entire substrate is a Hamming distance between
   two 256-bit majority-vote patterns.**
3. **SAME OR DIFFERENT.** DIFFERENT — **WRONG METRIC, on a code already corrupted by C1/C2.**
   I rank the metric BELOW C1/C2 deliberately: a cosine on a properly normalised graded code is a
   defensible first-order read-out of a settled state, whereas a Hamming distance on prototype
   patterns cannot represent the distinction at all. Fix the code before litigating the metric.
4. **PREDICTS A KNOWN FAILURE?** PARTIALLY. It is the site where the C1/C2 damage becomes a decision,
   and `mean_winning_cos = 0.1476` in the landed run (`data/exp_context_conditioned_near_neighbour_v1/metrics.json`)
   confirms the margin being adjudicated is thin. But no refuted route isolates the metric itself,
   so I do not claim it as an independent cause.
5. **BRAIN-FAITHFUL REPLACEMENT.** Cosine on the divisively-normalised graded code (i.e. C1+C2 fixed
   makes C3 acceptable). Do NOT add recurrence here — see C5.

### C4 — CONTEXT MODULATION: how the task/context reshapes the comparison

1. **BRAIN OPERATION.** Semantic control does NOT select from a candidate list; it applies
   **multiplicative GAIN** to the task-relevant dimension. Chiou & Lambon Ralph 2018 (*Cortex*,
   PMC6006425), DCM: IFG's effective connectivity to the spoke holding the currently relevant
   feature dimension is selectively boosted, F(2,34)=3.86, p=.03; control "dynamically heightens its
   connectivity with relevant components of the representation system." Same hub weights + different
   control settings reproduce context-dependent behaviour (Hoffman, McClelland & Lambon Ralph 2018
   *Psychol Rev* 125:293-328). Retrieving a NON-DOMINANT association recruits a HIGHER-dimensional
   coding regime (Gao et al. 2022 *eLife*).
2. **OUR OPERATION.** Two states of the world. (a) `concept_similarity(a, b)` — a bare 2-arg pure
   function, NO context port at all (`hdlab/lexical_similarity.py:599-615`). (b) The one working
   channel, the landed context-conditioned cell: context enters as the QUERY VECTOR only
   (`context_vector_masked` -> `canonicalize_fast`), i.e. **additively, as another point in the same
   space**, never as a gain on dimensions.
3. **SAME OR DIFFERENT.** DIFFERENT — **RIGHT IDEA, WRONG ALGEBRA.** Gain is MULTIPLICATIVE and
   acts per-dimension; ours is an additive extra vector. Note this is the one row where we already
   have a POSITIVE result (d12 = +0.1005, CI [0.0795,0.1227], scrambled floor 0.4975 at chance), so
   the position gap is partly closed and the algebra gap is not.
4. **PREDICTS A KNOWN FAILURE?** It EXPLAINS A SUCCESS, which is the same evidence run forwards:
   adding any context port at all moved 0.5390 -> 0.6395. That is the strongest single argument in
   this audit that the fidelity method works. It does not explain a failure of its own.
5. **BRAIN-FAITHFUL REPLACEMENT.** Multiplicative per-dimension gain derived from the context,
   applied to the anchor code before comparison. **Organ owned:** partly — `ReadoutConfig` FIX 2
   (`reading_grounding_loop.py:514+`) already applies a per-ANCHOR affine correction; it needs to be
   per-DIMENSION to be gain in the brain's sense. DEFERRED behind C1/C2: a gain applied to a
   binarised code has nothing graded to act on, which is why this must not be built first.

> **TESTED AND CLOSED, 2026-08-14 — `HARD_FAIL_GAIN_HURTS`** (`data/exp_task_local_normalisation_pool_v1`,
> prereg `e07d8ffb3` + AMENDMENT A1 `0b445b3bf`, n=4000). Both baselines reproduced EXACTLY
> (`R_LIVE` 0.6395, `R_BASE` 0.6997), so the read is licensed. Multiplicative per-dimension control
> gain `g = |a_t - a_d|` scored **0.6777, d = -0.0220 CI [-0.0340,-0.0097]** — significantly WORSE.
> The demoted pool-inverse form scored 0.6883, also below baseline, exactly as the amendment
> predicted in advance.
>
> **MECHANISM OF THE NEGATIVE, and it unifies this whole program:** the gain does not privilege
> DISTINCTIVE dimensions, it privileges NOISY ones. With 70 observations per concept in a 256-dim
> random projection, the dimensions with the largest anchor-difference are disproportionately the
> worst-estimated. Every per-dimension REWEIGHTING this program has tried is null or harmful —
> log-IDF (`dbac1ae9c`, null), global-field z-scoring (+0.0018, null), pool-inverse (-0.011),
> contrast gain (-0.0220) — while the only thing that helped was removing a per-dimension
> DESTRUCTION. **Per-dimension statistics estimated from 70 samples in a 256-dimensional random
> projection are too noisy to weight by.** That is an estimation-noise statement, and it points at
> C7, not at C4.

### C5 — SETTLING / STABILISATION   **[EXPLICIT NEGATIVE RECOMMENDATION]**

1. **BRAIN OPERATION.** Recurrent attractor settling to a fixed point; hippocampal CA3 completion
   with cue re-injection (Hasselmo 2002; Neunuebel & Knierim 2014 *Neuron* 81:416-427); ATL hub
   settling over ~200-500 ms (Rogers et al. 2021 *eLife*).
2. **OUR OPERATION.** NONE in the comparator: strictly feedforward, one-shot. We DO own the organs —
   `hdlab/iterative_attractor.py:104-126` (softmax over codebook, `beta = temp*sqrt(D)`, cue
   re-injection `alpha`, max 8 steps, tol 1e-3*sqrt(D)), `hdlab/cleanup_family.py:107-231`
   (classical Hopfield with Hebbian outer product + `sign` update; modern Hopfield with softmax then
   `sign`), `hdlab/dg_pattern_separation.py:117-132` (random expansion + k-WTA + L2, orphaned:
   ZERO hdlab importers).
3. **SAME OR DIFFERENT.** DIFFERENT — missing entirely. **But see field 4; the naive fix is wrong.**
4. **PREDICTS A KNOWN FAILURE? NO — AND THE STANDING "REUSE THE OWNED ORGAN" RULE MUST NOT FIRE
   HERE.** Tyler & Moss's Conceptual Structure Account (*TiCS* 2001; Taylor, Devereux & Tyler 2011)
   states the mechanism explicitly: distinctive features are WEAKLY CORRELATED with a concept's
   other features, and **attractor settling is driven by correlational structure**, which is exactly
   why distinctive features are computationally FRAGILE. Adding CA3-style pattern completion to the
   comparator would make near-neighbour discrimination WORSE, not better; the brain pays that cost
   and compensates with control gain (C4). Worse, `classical_hopfield` and
   `modern_hopfield_continuous` both terminate in `np.sign(...)`, so wiring them in would add a
   FOURTH prototype operator. **We already have an attractor network's nonlinearity (`sign`) with
   none of its recurrent weights: all of the prototype drift, none of the completion benefit.**
   Recommendation: do NOT wire `cleanup_family` / `iterative_attractor` into the comparator. This is
   a case where the owned organ is the right organ for a DIFFERENT metric (episodic recall), and the
   reuse rule must be evaluated against the brain's metric for THIS component, per the FORMALIZE
   discipline (SHAPE + POSITION + METRIC).
5. **BRAIN-FAITHFUL REPLACEMENT.** None, for now. Revisit only after C1-C3 land and only paired with
   real C4 gain, which is the brain's own compensator for it.

### C6 — WINNER SELECTION

1. **BRAIN OPERATION.** Graded competition / normalisation-based selection, not a hard argmax; the
   normalisation pool implements the competition (Carandini & Heeger 2012). Semantic aphasia shows
   selection failing specifically when a WEAK TARGET must beat a STRONG COMPETITOR (Jefferies &
   Lambon Ralph 2006 *Brain* 129:2132-2147).
2. **OUR OPERATION.** `canonicalize_fast:699` `best = int(np.argmax(sims))`, first-max tie-break;
   `concept_encoder:564` the same.
3. **SAME OR DIFFERENT.** DIFFERENT in form (hard argmax vs graded competition), but for a 2AFC
   accuracy metric argmax IS the deterministic limit of the softmax and cannot change the expected
   score. **Low priority by the BRAIN'S metric for this task.**
4. **PREDICTS A KNOWN FAILURE?** NO. Recorded so the audit is complete, not ranked for build.
5. **REPLACEMENT.** Deferred. (`modern_hopfield_readout.py` exists, orphaned, if ever needed.)

### C7 — REPRESENTATION FORMAT

1. **BRAIN OPERATION.** Neocortical semantic code: DENSE, GRADED, LOW effective dimensionality
   (~4-12 shared dims; Huth 2012/2016; Binder et al. 2016 ~65 experiential attributes; Tiesinga 2023
   ~2/3 of electrodes active). Explicitly NOT sparse, NOT binary. Sparse coding is the MTL/
   hippocampal regime (~0.2%, Waydo et al. 2006) — a different system; conflating them is a trap.
2. **OUR OPERATION.** Context path: **256-dim bipolar ±1** (`D = 256`,
   `grounding_acquisition_loop.py:79`). Lexical path: 8192-dim complex64 unit-phase. Grounded path:
   12-dim real graded. Encoder: 4096-dim ternary at 2% sparsity.
3. **SAME OR DIFFERENT.** DIFFERENT — binary where the brain is graded; and at d=256 with 2,377
   anchors the space is heavily overcomplete, which is why the shared component dominates.
4. **PREDICTS A KNOWN FAILURE?** CONTRIBUTES to C1/C2 rather than being independent — a 1-bit code
   is what makes the magnitude loss total rather than partial. Measured: 13.85% of dimensions carry
   < 10% of p90 evidence and are amplified to full weight.
5. **REPLACEMENT.** Graded real at the same d (free — the sums are already float64). A dimensionality
   change is NOT proposed: it is confounded with the format change and must not ride along in the
   same cell.

> **PROMOTED FROM LAST TO FIRST, 2026-08-14.** Declining to vary `d` was right for ISOLATION and
> wrong for INTERPRETATION: without a d-sweep, a capacity effect reads as a quantisation effect,
> and that is exactly what happened (see the header and
> `notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md`). Measured crosstalk between
> unrelated codes falls exactly as 1/sqrt(d): **0.0498 at d=256, 0.0249 at d=1024, 0.0125 at
> d=4096** (`experiments/exp_capacity_ceiling_near_far_v1.py` self-test S4), and the substrate holds
> 2,377 concepts at d=256. Every negative in rows C1 and C4 is consistent with the substrate running
> where crosstalk and estimation noise bind. The cell that tests this — and the sharper question of
> whether the NEAR/FAR gap survives 16x the capacity — is
> `preregs/2026-08-14_capacity_ceiling_and_the_near_far_gap.md`.

---

## TOP 5, COMPRESSED

| # | constituent | brain | ours | verdict | predicts |
|---|---|---|---|---|---|
| 1 | per-occurrence combination | divisive norm, POOL-shared denominator, ratios preserved | `sign()` / `s/|s|` per component, ratios destroyed | WRONG OP (the inverse) | near/far collapse; +20-32% d' measured by swapping ONLY this normaliser. Does NOT explain the IDF-weighting null (predicted it would; refuted, see correction) |
| 2 | across-occurrence accumulation | graded frequency-weighted consolidation | graded sum COMPUTED then `sign()`ed away at read | RIGHT OP, WRONG PLACE | shared component 0.58 of norm; pairwise cos 0.34; floor-hugging 0.6395 |
| 3 | comparison | recurrent nonlinear settling on a normalised graded code | cosine of two ±1 vectors = Hamming/256 | WRONG METRIC on a corrupted code | thin margin (mean winning cos 0.1476) |
| 4 | context modulation | MULTIPLICATIVE per-dimension gain (IFG->spoke) | context added as another VECTOR | RIGHT IDEA, WRONG ALGEBRA | explains the +0.1005 success; blocked behind 1-2 |
| 5 | settling | recurrent attractor completion | none — and DO NOT ADD IT | missing BY DESIGN | attractor settling DESTROYS distinctive features (Tyler & Moss) |

---

## WHAT THIS BUYS THE NEXT BUILD

The four refuted routes were all attempts to add better INFORMATION (better weights, more
differentia, better genus, a better channel) to a comparator whose ARITHMETIC destroys the
information it already has. That is why they were null, and it is why none of them is evidence about
the underlying question. The first cell must change the ARITHMETIC and nothing else.

Build order, by (predicts a known failure) x (own the organ):
1. **C1+C2 — remove the binarisations, normalise against the population.** Both organs owned
   (`ConceptSpace._sums` already graded; `grounded_similarity`'s z-scoring is the right statistic).
   Tested on the context-conditioned testbed, which is the one measurement with range and a working
   scrambled floor.
2. **C4 — multiplicative per-dimension gain.** Only after 1, because gain needs something graded.
3. **C3/C6/C7** — downstream. **C5 — explicitly declined.**

## DISCLOSURES

- Right file / right version: all line numbers read at HEAD `4093464b4` on branch
  `dataprep/mcguffey-graded-corpus`, files read in full or by cited range, not grepped.
- Right environment: `.venv/Scripts/python.exe` for every measurement.
- Right corpus: the probe uses the SAME cached corpus assets
  (`data/exp_context_conditioned_near_neighbour_v1_cache/corpus_assets_b12e14604e346f01.pkl`) and the
  SAME per-word `hashlib`-seeded profile split as the landed cell.
- Right metric: the probe asserts byte-identity with `hdlab.grounding_acquisition_loop.context_vector`
  BEFORE measuring, so the "SIGN (live)" row is the live code and not a re-implementation.
- Right arm: refuted-route numbers quoted from each cell's own `metrics.json` verdict string.
- The probe measures ANCHOR-FIELD GEOMETRY ONLY. It deliberately does NOT compute task accuracy,
  so that the Phase-2 discriminator bands can be pre-registered without having seen the
  discriminator.
- `hdlab/` is UNMODIFIED as of this note.
- No tool call was denied during this audit.
