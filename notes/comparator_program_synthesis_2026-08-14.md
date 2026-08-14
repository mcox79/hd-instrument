# The comparator program: what a component-by-component mathematical fidelity audit produced

Filed 2026-08-14. Branch `dataprep/mcguffey-graded-corpus`. One session, one component (the semantic
comparator), the method USER specified: decompose into constituent operations, drill how the brain
does each one, and check whether OUR MATHEMATICAL OPERATION IS THE BRAIN'S OPERATION.

Entry points: `notes/comparator_component_fidelity_audit_2026-08-13.md` (Phase 1, read its header
first — parts of it are superseded by its own follow-ups) and
`notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md`.

---

## THE ONE-TABLE RESULT

All numbers n=4000, held-out, WordNet strict dominant-sense near-neighbours in real simplewiki
context, 2AFC with chance exactly 0.50 and a scrambled-context floor measured in every cell.

| | NEAR | FAR | gap | floor |
|---|---|---|---|---|
| live comparator (quantised, d=256) | 0.6395 | 0.6753 | 0.0358 | 0.4978 |
| graded (landed + wired, d=256) | 0.6980 | 0.7450 | 0.0470 | 0.5095 |
| graded, d=1024 | 0.7495 | 0.7988 | 0.0493 | 0.4903 |
| **graded, d=4096** | **0.7823** | **0.8365** | **0.0543** | 0.4955 |

Three things fall out of that table and none of them was known when the session started.

**1. The absolute level was capacity-limited, and nobody had checked.** Sixteen times the
dimensionality buys +0.0843 (graded) / +0.0985 (quantised) — more than any mechanism change this
program has produced, including the one it landed. Crosstalk between unrelated random-index codes
falls exactly as 1/sqrt(d) (measured 0.0498 / 0.0249 / 0.0125), and the substrate was holding 2,377
concepts at d=256.

**2. The near-neighbour deficit is NOT capacity, and is now isolated.** The FAR-minus-NEAR gap is
flat-to-slightly-growing across a 16x capacity range, its CI excludes 0 at every d, and it is 6x the
between-projection-draw sd (0.0090 over 3 independent projections). This is the first residual this
program has found that survives every lever it owns, measured on a task with a floor at chance.

**3. The gap is small beside the task's own ceiling.** FAR accuracy at d=4096 is 0.8365 — 16.4% of
items fail against an UNRELATED distractor. For a sixth of items the context cue simply does not
identify its target. Any future comparator work should be sized against that, not against 1.0.

## WHAT WAS TESTED AND WHAT HAPPENED

| gap | operation tested | result |
|---|---|---|
| C1+C2 | remove the two `np.sign` quantisers, normalise against the population | **HARD_PASS** 0.6395 -> 0.6997, d=+0.0602 CI [+0.0440,+0.0762]. Attribution: ENC sign +0.0245..+0.0267, AGG sign +0.0220..+0.0260, **global-field normalisation NULL** (+0.0018) |
| C4 | multiplicative per-dimension semantic-control gain | **HARD_FAIL_GAIN_HURTS** -0.0220 CI [-0.0340,-0.0097] |
| C7 | capacity / representation format | **MIDDLE_BAND_CAPACITY_PARTIAL**, the table above |
| C5 | recurrent attractor settling | **declined on brain-fidelity grounds and not built** — attractor settling is driven by correlational structure and therefore destroys distinctive features (Tyler & Moss CSA); both owned implementations also terminate in `np.sign`, which would add a fourth prototype operator |

## THE FINDING THAT UNIFIES THE NEGATIVES

**Per-dimension statistics estimated from 70 observations in a 256-dimensional random projection are
too noisy to weight by.** Every per-dimension REWEIGHTING this program has tried is null or harmful:

- log-IDF distinctiveness weighting — null (`dbac1ae9c`)
- global-field z-scoring (efficient-coding adaptation) — +0.0018, CI includes 0
- task-local pool-inverse gain — -0.011
- contrast gain `|a_t - a_d|` — **-0.0220, CI excludes 0**

while the only operation that helped was removing a per-dimension DESTRUCTION. A reweighting keys on
a per-dimension statistic; at 70 samples and d=256 that statistic is mostly estimation noise, so the
gain up-weights the worst-estimated dimensions rather than the most diagnostic ones. This also
predicts, correctly, that the same weighting ideas would be worth retrying at high d and high
sample count — which is a cheap, well-posed follow-up rather than a mystery.

## THREE CORRECTIONS THE METHOD FORCED ON ITS OWN AUTHOR, IN ONE SESSION

Recorded because the corrections are the evidence that the method works, not evidence against it.

1. **A predicted mechanism was refuted by recompute.** I claimed `bundle()`'s per-component
   renormalisation had erased the log-IDF weights one line after they were injected. A numerical
   recompute that bit-matched `_concept_vector_from` on 359/359 concepts showed near-cancellation is
   4.3x RARER under weighting, that the per-component step TRANSMITS more of the perturbation than
   L2 does, and that weighting hurts under both normalisers. Refuted, and recorded as refuted. The
   same recompute independently supported the audit's core claim on a different module: swapping
   per-component `s/|s|` for whole-vector `s/||s||` moves near-vs-random d' 4.843 -> 6.030.
2. **I transposed Carandini & Heeger.** Their pool index ranges over other NEURONS at the same
   moment, so the denominator is a SCALAR — and cosine is invariant to a scalar, so canonical
   divisive normalisation cannot change a two-candidate argmax AT ALL. What I had implemented and
   measured null was efficient-coding adaptation, a different mechanism. Found by the next cell's
   own self-test, filed as a dated pre-registration AMENDMENT that re-designated the primary arm
   BEFORE any arm was scored, with the superseded prediction retained and still scored (it landed
   below baseline, as the amendment predicted).
3. **A HARD_PASS survived every artifact control and still lost its mechanism claim.** An
   adversarial review reproduced the landed run bit-exactly, killed five artifact hypotheses
   (leakage, ties, sentence length, pool statistics, floor validity) — and then showed the
   unmodified quantised comparator at d=1024 BEATS the graded one at d=256, that destroying all
   magnitude in the unprojected term space costs only 27% of the effect, that ~30% of the smoke
   delta was an uncontrolled ternary/bipolar zero-convention mismatch, and that projection-draw
   variance (sd 0.015) is invisible to the item bootstrap. The capability stands and is still
   wired; the explanation was withdrawn in all four places it had been written down.

## METHOD NOTES WORTH KEEPING

- **A byte-identity control against the substrate's own code found a live inconsistency nobody was
  looking for**: `context_vector` maps sign-zero to +1 (bipolar) while `ConceptSpace.anchor_matrix`
  uses a plain `np.sign` (ternary). 13.2% of query dimensions are affected and the mismatch was
  worth ~30% of a smoke-scale delta. Documenting a confound is not controlling for it — that was
  this session's own mistake, caught by the reviewer.
- **Isolation and interpretation can pull opposite ways.** Declining to vary `d` in the same cell as
  the format change was correct for one-variable isolation and wrong for interpretation: without a
  d-sweep, a capacity effect reads as a quantisation effect. When a fixed parameter could be the
  dominant limiter, sweep it in a labelled no-verdict-weight diagnostic in the SAME cell.
- **Bands should not conjoin two quantities that answer different questions.** The C7 HARD_FAIL band
  required a LEVEL condition and a GAP condition together; the data cleanly separated them, so the
  cell returned MIDDLE_BAND while carrying a sharp result on the gap.
- **Item bootstraps are blind to shared-randomness variance.** Any cell built on a random projection
  must report between-draw sd next to its CI. This cell did (0.0090) and it is why the 0.0543 gap is
  reportable.

## HEAD ITEM

The isolated, capacity-independent near-neighbour residual of ~0.05, and the 16.4% of items whose
context does not identify its target at all. The comparator's arithmetic is no longer the binding
constraint on this task; what the context vector CONTAINS is.
