# Drill: ordinal magnitude coding + composition, best-in-class (brain-first)

**Filed by:** research sub-agent. **Trigger:** confirmed-on-real-data finding that swapping a modular/cyclic
ordinal code for a monotone (thermometer/cumulative) code moved a real ordinal-conjunction task from below-chance
(0.16) to well-above (0.57). Current monotone code is crude: uniform-bin thermometer + learned non-negative linear
weights per constituent + additive composition. Question: what is the best-in-class upgrade path, brain-first,
for encoding magnitude and composing multiple magnitudes for zero-shot generalization to novel combinations.
**Method:** 3 parallel Sonnet lit-scans (brain magnitude coding; brain magnitude combination + generalization;
ML/stats ordinal + monotone-composition best-in-class), generic public math/neuroscience terms only, no
substrate-specific names/numbers sent off-platform, per [[feedback-query-privacy-decomposition]].

---

## HEADLINE

The brain does not use one magnitude code — it runs **two coexisting schemes** (monotone "summation"/accumulator
coding in parietal cortex vs bell-shaped "labeled-line" tuned coding in prefrontal cortex), and separately
**log/Weber-Fechner-compresses** the axis before either code is read out. Our current thermometer code gets the
"monotone, not cyclic" part right (that's the 0.16->0.57 win) but skips the compression step entirely — it bins
magnitude linearly, while every biological magnitude axis found in this scan is compressive (log or power-law).
That mismatch is the single cheapest, most direct fix available. Separately, the strongest DIRECT biological
evidence for zero-shot generalization to *novel combinations* of magnitudes is not from the monotone/tuned coding
debate at all — it is grid-like entorhinal/prefrontal coding of independently-learned rank dimensions (Park,
Miller & Boorman 2021, *Nat Neurosci*) and cortical representation of novel stimuli as **linear combinations of
familiar population codes** (2025 hippocampus/neocortex compositional-generalization work) — both of which endorse
keeping composition additive/linear rather than moving to a nonlinear monotone combiner, provided the encoding
itself (not the combiner) is fixed first.

## Cheap decisive test

Re-run the existing ordinal-conjunction cell with **log-spaced (or empirical-quantile / Weber-scaled) thermometer
bin edges** in place of uniform bins, holding the architecture fixed (same additive composition, same
non-negative learned weights, same held-out novel-combination split). This isolates the encoding-density question
from the composition-rule question and is a same-day, same-harness change (bin-edge function only, no new
mechanism).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 — log-compressed bins.**
- HARD-PASS: accuracy on the held-out novel-combination split improves by >=0.05 absolute over the current 0.57
  (i.e. >=0.62), with the same architecture otherwise unchanged.
- HARD-FAIL: delta <0.02 (either direction) — means linear-uniform binning was not the active bottleneck and the
  compression lever is not where the remaining gap lives; do not iterate bin-edge variants further if this fires.

**Prediction 2 — reliability-weighted (per-instance) additive combination in place of fixed learned weights.**
- HARD-PASS: closes >=30% of the CURRENT failure cases (cases the present fixed-weight combiner gets wrong)
  without introducing new failures elsewhere, i.e. a net localized improvement, not just a global average bump.
- HARD-FAIL: no localized improvement (failure-case overlap with baseline >=90%) — means the fixed-weight
  combiner was not the bottleneck either, and the gap is upstream (in the per-constituent encoding, not the
  combination rule).

**Prediction 3 — nonlinear monotone lattice/isotonic combiner instead of linear sum (lower-priority, listed for
completeness).**
- HARD-PASS: beats linear-additive combiner by >=0.05 on the SAME novel-combination split specifically (not just
  IID held-out).
- HARD-FAIL: no improvement or regression — per the ML lit-scan (Xu et al. 2021 "How Neural Networks Extrapolate";
  Trask et al. 2018 NALU), this is the EXPECTED outcome unless the true combination rule has genuine nonlinear
  interaction (saturation/diminishing-returns across constituents), which has not been established for this task.
  Treat a HARD-FAIL here as informative confirmation, not a wasted cycle.

All three predictions carry the standard calibration deflation (see P_deflated values below); this is uncharted
substrate regime with no direct published precedent for the exact composition, so P estimates are capped at 0.50
and further deflated per severity of novelty.

---

## (a) Brain magnitude-coding summary

**Two coexisting codes, different cortex, different job.** Parietal cortex (monkey LIP) carries **monotonic
"summation" coding**: firing rate ramps continuously with numerosity, independent of attention/reward/size/density
— a graded, accumulator-like output (Roitman, Brannon & Platt, *PLoS Biology* 2007). Prefrontal cortex carries
**bell-shaped "labeled-line" tuned coding**: each neuron peaks at a preferred numerosity and falls off on both
sides, producing the classic numerical-distance and size effects (Nieder, Freedman & Miller, *Science* 2002;
Nieder & Merten, *J Neurosci* 2007). Both coexist across the fronto-parietal network (Nieder, *Nat Rev Neurosci*
2016) — summation coding is more parietal/sensory/ordinal, labeled-line coding is more prefrontal/categorical/
discriminative. This maps cleanly onto our own result: our task needed the monotone/ordinal axis (parietal-style),
not fine categorical discrimination, which is consistent with monotone-only being sufficient for the 0.57 win.

**Log/Weber-Fechner compression is the dominant framing, though contested at the margins.** Dehaene's neural
model derives the distance/size effects and scalar variability from a log-transformed, fixed-noise-width number
line; human IPS fMRI shows log-Gaussian tuning (Piazza et al., *Neuron* 2004); topographic numerosity maps in
human parietal cortex (7T fMRI, intracranial recordings) show orderly spatial arrangement of preferred
numerosities — genuine place coding, not just abstract tuning. Caveat: whether "log" vs "linear-with-scalar-noise"
is the right primitive is a live mathematical-equivalence dispute (Algom 2021 explicitly argues "Weber-Fechner law"
is overused as a label) — but every empirical account found is COMPRESSIVE in some form (log or power-law), never
linear-uniform. This is the concrete, actionable gap in our current thermometer code.

**Place vs rate: both, at different levels.** LIP is closer to a pure rate code in an undifferentiated population
(no discrete labeled channels). PFC and human IPS look more like a place/population code — a labeled line per
preferred magnitude, with real cortical topography. Domain-generality (does one magnitude system serve number,
time, space, value alike — Walsh's ATOM theory) is genuinely contested: some studies support a shared/coupled
system, a 2018 *Psychonomic Bulletin & Review* paper argues explicitly against a single common system beyond early
childhood. Treat "one universal magnitude code" as unproven, not as the biological anchor.

## (b) Brain magnitude-combination + generalization summary

**Combination is reliability-weighted LINEAR averaging at the behavioral level (Bayesian cue integration), not
literal multiplication.** Ernst & Banks (*Nature* 2002) is the foundational, well-replicated result: cue weights
scale with inverse variance. Mechanistically this is implemented via **divisive-normalization circuits**
(weighted linear sum -> nonlinearity -> pool-normalize), which produces superadditive-looking behavior for weak
cues and near-additive for strong cues as an EMERGENT property, not an explicit multiply (Ohshiro/Angelaki/
DeAngelis normalization-model papers). OFC expected-value coding is similar: true multiplicative (magnitude x
probability) tuning exists mostly at the POPULATION level, not in single neurons. Net: the brain's default answer
to "how do you combine magnitudes" is additive/linear with per-cue reliability weighting, not a multiplicative or
deeply nonlinear combiner — this is a strong argument FOR keeping our composition additive and upgrading only the
weighting scheme.

**Transitive inference and novel-combination generalization use a geometric "cognitive map," and this is the
strongest direct evidence for zero-shot generalization to unseen combinations.** Hippocampal/entorhinal/OFC
circuits build genuine geometric (Euclidean-distance) maps of rank/value relationships that support inference to
untrained pairs (DeVito, Lykken, Kanter & Eichenbaum 2010; recent 2023-2025 map-like-space fMRI work). Grid-cell-
like coding generalizes from space to abstract conceptual dimensions (Constantinescu, O'Reilly & Behrens, *Science*
2016), and critically, Park, Miller & Boorman (*Nat Neurosci* 2021) show a grid-like entorhinal/mPFC code supports
inference across a **2D combination of two independently-learned rank dimensions never jointly sampled** — this is
the single most on-point biological result for "novel combinations of magnitudes," not just novel single values.
Complementary mechanistic evidence: generative replay assembles novel compound representations from previously
separate elements during planning (Schwartenbeck et al., *Cell* 2023), and a 2025 hippocampus/neocortex paper finds
cortex represents novel stimuli as **linear combinations of familiar-stimulus population codes** — i.e., the
cortical mechanism licensing generalization to new combinations is itself additive/linear. This literature
(2023-2025) is newer and less battle-tested than points above; treat as promising, not settled.

## (c) Best-in-class ordinal/monotone-ML summary

Cumulative-link/proportional-odds models (McCullagh 1980) and modern rank-consistent deep variants (CORAL, CORN)
give well-established ordinal representations, but ALL reported generalization evidence in the literature found is
IID-style (unseen samples within the trained rank range), not unseen *combinations* — this specific gap is open,
not contradicted. Thermometer/unary codes are exactly how SAT/CSP cardinality encodings represent sums of many
variables (totalizer/merge networks), but naive vector addition of two thermometer codes does NOT yield a valid
thermometer code of the sum — composition requires a purpose-built merge, a real caveat for any scheme that adds
raw thermometer vectors directly. Monotonic neural networks (deep lattice networks, min-max/Sill networks, COMET,
isotonic regression, monotone gradient boosting) all improve IID generalization via the monotonicity prior itself,
but no source tested whether a lattice/isotonic combiner beats a plain linear sum specifically on held-out novel
COMBINATIONS. The most directly relevant ML result is **inductive-bias matching**: Xu et al. (ICLR 2021, "How
Neural Networks Extrapolate") show generic nonlinear networks default to linear behavior far from the training
distribution and only extrapolate correctly when the target's true structure is built into the architecture; NALU
(Trask et al., NeurIPS 2018) shows a tied-weight LINEAR accumulation structure extrapolates addition far beyond
training range while a generic MLP fails. Together these argue: if the true combination rule is additive (which
the brain evidence above also suggests), match that bias with a linear/additive combiner rather than reaching for
a more expressive nonlinear monotone lattice — the nonlinear route is motivated only if there is direct evidence
of genuine interaction (saturation, diminishing returns) between constituents, which has not been established
here.

## Ranked shortlist of concrete encoding upgrades

| Rank | Upgrade | Bio rationale | ML rationale | Risk/cost | P_deflated |
|---|---|---|---|---|---|
| **1** | **Log/power-law-compressed thermometer bin spacing** (denser bins at low magnitude, sparser at high, replacing uniform spacing) | Every biological magnitude axis found (IPS, PFC, mental number line) is compressive (log-Gaussian or power-law), never linear-uniform; this is the single documented mismatch between our crude code and every biological account | Matches the actual (Weber-law-shaped) discriminability structure of ordinal categories; zero architecture change, pure re-parameterization of bin edges | Lowest cost (bin-edge function only); lowest risk | **0.35** |
| **2** | **Reliability-weighted additive combination** (per-instance/per-constituent confidence-scaled weights, e.g. inverse-variance-style gain, replacing fixed global non-negative weights) | Directly matches Ernst & Banks Bayesian cue-integration + divisive-normalization circuit account — the brain's actual default combiner | Keeps the additive backbone that NALU/Xu-et-al favor for extrapolation, while adding the one degree of freedom (per-cue reliability) the brain literature says matters | Low-moderate cost (needs a per-constituent confidence estimate); moderate risk if confidence estimate itself is noisy | 0.30 |
| 3 | Dual-code hybrid: retain monotone/summation axis as primary readout, ADD a secondary bell-shaped/tuned (RBF-like) code per constituent for fine within-range discrimination | PFC labeled-line coding coexists with parietal summation coding for a reason (categorical fine discrimination vs ordinal comparison) | None of the ML lit-scan sources address tuned/RBF codes for compositional generalization specifically — untested combination | Higher cost (new code family); real risk of reintroducing non-monotonicity that caused the original 0.16 failure if not done carefully | 0.20 |
| 4 | Grid-like/toroidal joint code for pairs of magnitudes (encode (mag_A, mag_B) as a 2D periodic/grid-like joint representation rather than pure additive sum), following Constantinescu/Park entorhinal grid-code work | Strongest DIRECT bio evidence for zero-shot generalization to novel independently-learned combinations (Park et al. 2021) | No direct ML precedent found for combining this with ordinal/thermometer readout; reintroduces periodicity, which was JUST refuted (0.16 below-chance) for single-axis ordinal readout | High cost, high risk — worth a separate exploratory branch, not a replacement for the core fix, given the fresh negative result on periodicity in this exact setting | 0.15 |
| 5 | Nonlinear monotone lattice/isotonic combiner replacing the linear sum | None found specific to compositional generalization (brain evidence favors linear/additive combination, not this) | Xu et al. 2021 / NALU argue AGAINST this unless genuine nonlinear interaction between constituents is established | Low cost to implement, but literature predicts null result; useful mainly as a confirmatory HARD-FAIL check (Prediction 3) | 0.15 |

**How to test the top 2 (one line each):**
1. **Log-compressed bins:** swap uniform thermometer bin edges for log-spaced (or empirical-quantile) edges, rerun the existing novel-combination held-out split unchanged otherwise, compare accuracy against the 0.57 baseline (Prediction 1 thresholds above).
2. **Reliability-weighted combination:** compute a per-constituent confidence/variance estimate (e.g. from repeated-context calibration noise already available), replace fixed non-negative weights with confidence-scaled weights, and check whether it closes a specific, localizable subset of current failure cases rather than just moving the global average (Prediction 2 thresholds above).

---

## Cross-thread synthesis

- Directly downstream of the confirmed monotone-vs-modular result (this session, 0.16->0.57) that established
  "match code to data structure: MONOTONIC for magnitude / cyclic for space" as the active lever
  (`project_reasoning_mechanism_improve_additive_map_construction_proof_encoding_lever_2026-07-14.md`). This drill
  refines that lever: monotonic-vs-cyclic was the coarse (binary) fix; log-compression is the next-order
  (continuous) refinement within the monotonic family.
- Consistent with the standing additive-composition thread (`hdlab/additive_map.py`, MRR 0.128 CHAIN_GRADE,
  `project_additive_map_builder_integration_endgame_functional_plus_strict_via_shared_api_2026-07-13.md`) and the
  sibling SR-compose fusion drill (`notes/research_sr_compose_close_gap_to_additive_map_2026-07-14.md`), which
  independently found (different mechanism, same spirit) that SCORE-level/embedding-level additive fusion beats
  reaching for a more complex nonlinear combiner as the first move — the ML lit-scan here (Xu et al. 2021, NALU)
  gives an independent, general-theory reason for that same preference (match the combiner's inductive bias to the
  target's true — additive — structure) rather than defaulting to more expressive nonlinear machinery.
- Directly relevant to `project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md`
  ("brain uses ADDITIVE/GEOMETRIC degree-invariant codes; our discrete HRR-bind = memorizing regime") — the Park
  et al. 2021 grid-code result (rank 4 above) is the most concrete NEW biological anchor surfaced this drill for
  that thread's "novel-relation generalization" frontier, distinct from and complementary to the ordinal-magnitude
  fix that is this drill's main deliverable.

## Substrate-product implications

- The immediate, cheap fix (log-compressed thermometer bins) is a pure re-parameterization — no new mechanism,
  no new training loop, testable same-day on the existing cell. If it passes, it directly raises the ceiling on
  every downstream ordinal-conjunction capability that depends on the monotone code (not just this one task).
- If reliability-weighting (rank 2) also passes, it gives the substrate a principled way to handle constituents of
  heterogeneous quality/noisiness within one composed judgment — relevant to any future capability that combines
  attributes measured with different confidence (a general product capability, not a one-off fix).
- The grid-like joint-code idea (rank 4) is flagged as a separate, higher-risk exploratory branch, not a
  near-term commitment — it directly touches the periodicity question this session just refuted for single-axis
  readout, so it needs its own isolated test before any resource commitment, per
  [[feedback-dont-dismiss-adjacent-methods]] (don't dismiss it either, given how strong the Park et al. evidence is
  for exactly the "novel combination" generalization question).
- No claim here is a capability WIN yet — per [[feedback-construction-proof-is-not-a-capability-win]], every
  ranked item above is a testable hypothesis with pre-registered HARD-PASS/HARD-FAIL thresholds, not a result.

## Citations (verified count)

34 distinct sources cited across the three lit-scans (brain magnitude coding: 17; brain combination/generalization:
19, with overlap; ML ordinal/monotone: 15), all with author/year/venue and a retrievable URL returned by the
sub-agents' searches. Key load-bearing citations repeated above: Roitman/Brannon/Platt 2007 (PLoS Biology, monotone
LIP coding); Nieder/Freedman/Miller 2002 (Science, tuned PFC coding); Piazza et al. 2004 (Neuron, log-Gaussian IPS
tuning); Ernst & Banks 2002 (Nature, Bayesian cue integration); Park/Miller/Boorman 2021 (Nat Neurosci, grid-like
code for novel 2D rank combinations); Xu et al. 2021 (ICLR, extrapolation theory); Trask et al. 2018 (NeurIPS,
NALU). No citations were invented; each sub-agent was instructed to report only search-verified sources.
