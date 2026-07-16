# Research: quantitative magnitudes of the 3 consolidation-gate signals + their combination rule

Director drill, 2026-07-16. 2x-depth follow-up to `research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`
(the "v4" note that specified the qualitative 3-signal ingest gate and flagged our SURPRISE signal as too COARSE —
detects whole-relation presence, not within-schema derivability). Four parallel Sonnet lit-scans (dopamine/novelty
dose-curve; schema-congruency consolidation-rate; recurrence/spacing thresholds; Bayesian-surprise/free-energy
combination formalism) + director synthesis. Research-only: no code, no cell dispatched. Generic
math/neuroscience terms only in all external queries.

## HEADLINE

The quantitative literature gives REAL numbers for two of the three signals (surprise has an exact functional
FORM — saturating Hill function, R²=0.84; schema-fit has an exact temporal window — 3h-fail/48h-pass, ~15x
compression vs. the ~1-month schema-formation baseline) but explicitly confirms, a second independent time, that NO
published study quantifies how the three signals JOINTLY determine consolidation. The theoretical fix is not a new
biology paper — it's Friston's precision-weighted prediction-error formalism (free energy), which gives an exact
mathematical FORM for exactly the mechanism v4 was missing: schema-fit should not be a separate multiplicative
gate bolted onto surprise, it should be the MIXING WEIGHT that decomposes raw prediction-error into a
schema-consistent (cheap, local, fast-track) component and a schema-inconsistent (costly, structural, slow-track)
component — i.e., `fast_track_score = raw_PE * schema_fit` and `slow_track_score = raw_PE * (1 - schema_fit)`. This
is directly derivable from precision-weighting logic and directly fixes the v4 coarseness complaint (raw_PE alone
cannot tell "genuinely new to the whole foundation" from "new-but-a-slot-fill-in-known-structure"; the schema_fit
mixing weight is exactly that split). Recurrence's role is separately derivable and separately confirmed graded
(not floored): conjugate-Bayesian precision accumulation, `local_precision = f(recurrence_count)`, monotonic,
saturating — matching both the ACT-R log-sum-power-law activation equation and the statistical-learning literature's
"strengthens with repetition, no hard floor" finding. **No paper unifies all three into one named quantity — that
unification (below) is director synthesis over independently-citable pieces, explicitly capped at P<=0.50 per
lit-scan calibration discipline.**

## Part A — the quantum of each signal

### A1. SURPRISE / prediction-error — quantitative table

| Finding | Value / form | Citation | Confidence |
|---|---|---|---|
| DA firing rate vs. reward-PE magnitude | **Saturating Hill function**, f(r)=f_max·r^0.5/(r^0.5+σ^0.5), R²=0.84, n=40 neurons, p=4.6e-127; individual neurons differ only by a scalar gain | Eshel, Tian, Bukwich & Uchida 2016, *Nat Neurosci* 19:479-486 | High (primary, directly fitted) |
| Positive vs negative PE asymmetry | Contested: older work reports floor/rectification (near-zero baseline firing can't go further down); Eshel 2016's corrected analysis reports no rectification once weak-baseline neurons are properly weighted | Bayer & Glimcher 2005 (secondary); Eshel et al. 2016 | Medium (unresolved tension) |
| Rescorla-Wagner alpha <-> measured DA/behavioral learning-rate calibration | **Not found** — only qualitative correspondence claims | — | Gap (confirmed absence) |
| Hippocampal-VTA loop: novelty-magnitude -> DA-release-magnitude dose curve | **Not found** — circuit is described only qualitatively (novelty detected -> subiculum -> accumbens -> pallidum -> VTA -> DA -> hippocampal LTP) | Lisman & Grace 2005, *Neuron* 46:703-713 | Gap (confirmed absence) |
| Common vs. distinct novelty (two-system) quantitative dissociation | **Explicitly stated in the literature as not yet reported**: "direct quantitative comparisons of hippocampal dopamine release from LC-TH+ vs VTA-TH+ axons... yet to be reported" | Duszkiewicz, McNamara, Takeuchi & Genzel 2019, *Trends Neurosci* 42:102-114 | High-confidence NEGATIVE finding |
| Novelty -> consolidation ("behavioral tagging") window | **Threshold/binary, not graded**: ~1h window around training; 5-min novel-environment exposure sufficient; same env pre-familiarized 1h earlier does NOT work (novelty is categorical here, not dose-graded) | Moncada & Viola 2007, *J Neurosci* 27:7476; Ballarini et al. 2009, *PNAS* 106:14599 | Medium (secondary-sourced effect sizes) |

**Form verdict: SATURATING (not linear, not a hard step) for the core DA-firing-vs-PE relationship; but every
attempt to find a graded NOVELTY-magnitude -> CONSOLIDATION-strength dose curve came back empty or came back
explicitly binary/threshold (the behavioral-tagging window).** This is the single most load-bearing quantitative
finding of Part A: the brain's own novelty-consolidation coupling looks more like a TIME-WINDOW GATE than a
continuous dose-response curve, at the level of detail the literature currently reports.

### A2. SCHEMA-FIT / congruency — quantitative table

| Finding | Value / form | Citation | Confidence |
|---|---|---|---|
| Schema formation time | ~13 training sessions, ~1 month | Tse et al. 2007, *Science* 316:76-82 | High (primary, full text) |
| New schema-consistent paired-associate learning | 1 trial to acquire | Tse et al. 2007 | High |
| Hippocampal-independence temporal gradient | Lesion at 3h post-training -> AT CHANCE (not yet consolidated); lesion at 48h -> fully above chance, statistically = sham (Group x Delay F=15.77, df=1/13, P<0.005) | Tse et al. 2007, Fig. 4 | High (exact stats) |
| Fold-compression vs. schema-formation baseline | NOT stated by the authors as a ratio — ~1 month (schema build) vs. somewhere in [3h fail, 48h pass] (new-item consolidation); a reader-computed ratio is ~15x-240x depending which endpoint is used, but this number is NOT in the primary source | Tse et al. 2007/2011 | Gap — no explicit fold-speedup number published |
| mPFC mechanistic replication | Zif268/Arc immediate-early-gene upregulation specifically for new schema-consistent PAs vs. old PAs or a new (non-schema) spatial map | Tse et al. 2011, *Science* 333:891-895 | High |
| SLIMM formal model | **No equations, no learning-rate parameter, no numeric weights** — explicitly qualitative/schematic (boxes-and-arrows); own "Outstanding Questions" box admits the synaptic mechanism is unspecified | van Kesteren, Ruiter, Fernandez & Henson 2012, *Trends Neurosci* 35:211-9 | High-confidence gap (verified via full text) |
| U-shaped congruency-memory curve | Confirmed with real numbers: quadratic coefficient beta approx 0.5-1.05, Bayes factors BF10=12-85 across measures, up to BF10=620 on the congruent side (asymmetric U, congruent side steeper) | Quent, Greve & Henson 2022, *Psych Science*, N=137, 4 experiments | High (primary, quantitative) |
| McClelland 2013 connectionist mechanism | Reported (not independently verified from primary equations) as reduced INTERFERENCE from pre-organized hidden-layer structure, NOT a literal per-item learning-rate multiplier | McClelland 2013, *J Exp Psychol Gen* 142:1190-1210 | Medium (secondary-sourced characterization) |

**Form verdict: GATE/THRESHOLD for the hippocampal-independence transition (binary pass/fail dissociated by a
narrow time window, not a smooth rate curve) + a separately-graded, asymmetric U-SHAPED modulation of raw memory
STRENGTH by congruency (continuous, quantified, real effect sizes). No source commits to schema-fit as a pure
multiplier or additive bonus on rate.**

### A3. RECURRENCE / repetition — quantitative table

| Finding | Value / form | Citation | Confidence |
|---|---|---|---|
| Statistical-regularity detection onset | Neural entrainment to structure present as early as the first ~20s timepoint, learning index significantly increasing by the 3rd timepoint (graded, not a step) | EEG frequency-tagging study, *Neurobiology of Language* 2023 | High |
| Reliable exposure count | ~432 exposures in a 5-min phase (144 scenes x 3 items) for shape-pair statistics, "rapid, no overt task" | Fiser & Aslin 2001/2002 | High |
| Claimed 2-3-repetition threshold | Circulated in secondary summaries; **could not independently verify against primary source** | (unverified, flagged) | Low — do not use |
| Spacing-effect optimal gap | ~10-30% of retention interval; ~20% for weeks-scale delay, ~5% for a 1-year delay; explicitly non-monotonic (inverted-U) in gap size at fixed retention interval | Cepeda et al. 2006 (*Psych Bull*, 254 studies, ~14,000 Ss), Cepeda et al. 2008 (*Psych Science*, "Temporal Ridgeline") | High (meta-analytic) |
| Formal combined model | ACT-R base-level activation: `B_i = ln(sum_{j=1}^n t_j^-d)` — log-sum of power-law decay over every prior presentation; Pavlik & Anderson 2005 extend with presentation-specific decay `d_i` depending on activation-at-study-time (mechanistically produces the spacing effect) | ACT-R declarative memory; Pavlik & Anderson 2005 | High (explicit equation) |
| Minimum replay count for consolidation | **Not found** — one-shot (n=1) hippocampal learning is well-documented; strength/durability scale with subsequent replay FREQUENCY (graded), not a discrete count threshold | One-shot learning, PLOS Biology; SWR replay-frequency literature | Medium (positive evidence for "no floor," but assembled from several partial sources) |

**Form verdict: GRADED/CONTINUOUS, confirmed by the strongest evidence in this whole drill (an explicit closed-form
equation, ACT-R's log-sum power law) — no hard minimum-count floor exists in the literature. Spacing (gap-to-retention-interval
ratio), not raw repetition count, is what shows the non-monotonic (inverted-U) shape.**

## Part B — how they factor together (the crux)

### B4. Confirmed gap (2nd independent confirmation)

No empirical study found jointly quantifies prediction-error x schema-congruency x recurrence -> consolidation
probability/strength as one measured relationship. This is now confirmed across THREE independent lit-scans total
(2 from the 2026-07-15 v4 drill + this drill's dedicated combination-rule scan) with no shared priors between the
scanning sub-agents. Treat as a settled fact about the literature's current state, not an artifact of query
phrasing.

### B5. The theoretical forms that DO combine PE and prior/schema mathematically

| Framework | Exact form | Does it subsume schema-fit? | Citation |
|---|---|---|---|
| Itti & Baldi Bayesian surprise | `S(D,M) = D_KL(P(M|D) \|\| P(M))` | **Yes, intrinsically** — surprise depends only on the shape of the prior; a well-fit prior barely moves under new data (KL~0), a poorly-fit prior must shift a lot (KL large). No separate schema-fit term is needed or proposed — schema IS the prior. | Itti & Baldi 2005/2006/2009 (*Vision Research*; PMC2782645) |
| Friston free energy / precision-weighted PE | `epsilon_tilde = Pi * epsilon`, `Pi = Sigma^-1` (precision = inverse variance of the relevant level's prior) | **Yes, via hierarchy** — precision functions as confidence-in-schema. A well-established (high-precision) structural-level prior can absorb a surprising-but-consistent instance as a cheap LOW-LEVEL update (the specific new pairing) without requiring the expensive HIGH-LEVEL structural belief to be revised; a schema-inconsistent surprising instance has no high-precision template to land in, so the error propagates and forces costly structural revision. | Friston 2005; Friston 2010, *Nat Rev Neurosci* "The free-energy principle: a unified brain theory?"; PMC4235126 |
| Schema-conditioned PE, explicit consolidation formalism | **Not found** as a named "KL(posterior\|\|prior-given-schema)" account in the consolidation literature specifically | N/A | Closest: Spens & Burgess 2023/2024, *Nat Hum Behav* (generative-model/VAE account of schema-based memory distortion) — does not use this exact formalism |
| Recurrence as precision-sharpening | `posterior_precision = prior_precision + sum(observation_precisions)` (conjugate Bayesian updating) | Directly citable, independent of the schema question — each repeated observation adds precision monotonically, shrinking posterior variance | Murphy, "Conjugate Bayesian analysis of the Gaussian distribution"; Bayesian drift-diffusion reformulations (precision-weighted evidence accumulation) |

### B6. Adjudication — 3 separate signals, or one unifying quantity?

**Neither, cleanly.** The honest answer, cross-checked across the sub-agent report and director synthesis: Friston's
hierarchical precision-weighting gives a principled reason why schema-fit and surprise should NOT be combined into
a single flat scalar (that would lose the fast-track/slow-track distinction that is the entire empirical point of
Tse's result) — but it also shows they are not independent either. The right characterization is a **2-way
decomposition of one underlying prediction-error quantity, keyed by schema-fit as a mixing weight, plus one
separate precision-accumulation gate for recurrence.** This is director synthesis over independently-citable
pieces (Itti-Baldi's prior-absorption logic + Friston's hierarchical precision-weighting + conjugate-Bayesian
precision accumulation for repetition) — **no single paper states this decomposition; flag as novel synthesis,
capped at P<=0.50 per lit-scan calibration discipline.**

## Concrete derivable substrate rule

This directly targets the v4 complaint: raw surprise (`1 - reciprocal_rank(true_target)` from `additive_map.score_all`)
detects whole-relation presence but cannot distinguish "genuinely new to the whole foundation" from "new but a
slot-fill within an already-known structural type." The fix, derived from B5/B6 above:

```
INPUTS (all already exist, zero new scoring mechanism):
  raw_PE(candidate)      = 1 - reciprocal_rank(true_target | current X, D)     [additive_map.score_all, unchanged]
  schema_fit(candidate)  = reachability_score(candidate's support edges)       [reachability_audit.py, unchanged]
  recurrence_count(c)    = # distinct-provenance instances of this (relation-type, motif)

STEP 1 -- RECURRENCE -> LOCAL PRECISION (graded, per A3 -- log-sum / saturating, NOT a hard floor in theory;
          practical floor retained as a variance-control heuristic since n=1 estimates are inherently noisy)
  local_precision(c) = recurrence_count(c) / (recurrence_count(c) + TAU)        [TAU: substrate-calibratable]
  if local_precision(c) < PRECISION_MIN:  -> HOLD / PROVISIONAL (not yet trustworthy, regardless of PE/schema_fit)

STEP 2 -- SCHEMA-CONDITIONED DECOMPOSITION (the v4 fix -- replaces the flat raw_PE reading)
  fast_track_score(c) = raw_PE(c) * schema_fit(c)          [schema-CONSISTENT novelty: new instance,
                                                             known structural type -- Tse's PAL result --
                                                             cheap slot-fill, compose_entity+insert only]
  slow_track_score(c) = raw_PE(c) * (1 - schema_fit(c))    [schema-INCONSISTENT novelty: no known structural
                                                             template -- must propagate to costly full re-fit]

STEP 3 -- ROUTE (replaces the v4 ad hoc decision tree with a principled 2-score comparison)
  if local_precision(c) < PRECISION_MIN:                          HOLD / PROVISIONAL
  elif max(fast_track_score, slow_track_score) < SURPRISE_FLOOR:  SKIP (redundant either way)
  elif fast_track_score >= slow_track_score:                      FAST-TRACK CONSOLIDATE (cheap)
  else:                                                            SLOW-TRACK CONSOLIDATE (costly re-fit)
  special case: slow_track_score near-max (raw_PE saturates, schema_fit~0 -- Duszkiewicz "distinct novelty")
                AND local_precision only just at threshold -> flag for provenance review before folding
```

`TAU`, `PRECISION_MIN`, `SURPRISE_FLOOR` are explicitly OURS to calibrate — the biology gives the FORM
(saturating/log-sum for precision-from-recurrence; multiplicative mixing-weight for schema-fit x surprise) but
not the constants; no paper hands us numbers transferable to a KGE coordinate geometry. This is the honest
Part-B position: **form borrowed, weights measured.**

This is a genuine improvement over the v4 decision tree (Section 4 of the 2026-07-15 note), not a relabeling: v4
treated schema_fit as a ROUTING THRESHOLD applied AFTER a flat surprise score; this version treats schema_fit as
the MIXING WEIGHT that decomposes surprise itself into two orthogonal components before routing — which is what
actually fixes the "detects whole-relation-presence, not within-schema derivability" coarseness complaint, since a
candidate that is new-to-the-relation-vocabulary-overall (would score high raw_PE) but structurally slots into a
well-modeled neighborhood (high schema_fit) now correctly produces a HIGH fast_track_score and a LOW
slow_track_score, rather than one undifferentiated high-surprise reading.

## Cheap decisive test

Reuse the v4 pilot's REDUNDANT (batch 1) and GENUINE-NOVEL-RELIABLE (batch 2) candidate sets against the
already-fitted `additive_map` (X, D) — zero new acquisition. Compute `fast_track_score`/`slow_track_score` for every
batch-2 candidate, split into schema_fit tertiles, and for each tertile compare held-out MRR-improvement-after-fold
under two consolidation paths: (i) cheap fast-track (`compose_entity`+`insert_entity` only, no re-fit) vs. (ii) full
interleaved SGD re-fit.

- **HARD-PASS:** top-tertile schema_fit candidates achieve >=90% of full-re-fit's MRR improvement via the CHEAP
  fast-track path alone; bottom-tertile schema_fit candidates achieve <=50% of full-re-fit's improvement via the
  cheap path (i.e., the decomposition is load-bearing — it correctly predicts WHICH candidates can skip the
  expensive re-fit, not just a routing label that doesn't change any downstream outcome).
- **HARD-FAIL:** fast-track achieves >=90% of full-re-fit's improvement regardless of schema_fit tertile (schema_fit
  isn't predicting anything real about consolidation cost — same collapse-onto-redundant-signal failure class as
  the R7/MIR precedent already on file); OR local_precision shows no relationship to correct exclusion of
  batch-3 (ONE-OFF NOISE) candidates across a reasonable TAU sweep (recurrence-as-precision-accumulation isn't
  functioning as a real gate, independent of tuning).
- **MIDDLE band (realistic modal expectation):** top-tertile clears 70-90% and bottom-tertile lands 50-70% — real
  signal, threshold-tuning problem rather than a redesign.

## Falsifiable predictions (restated compactly, HARD-PASS + HARD-FAIL)

- P(cheap decisive test, as specified above, HARD-PASSes) = the single most decision-relevant open question — see
  P_deflated below.
- HARD-FAIL localization 1: if schema_fit-tertile split shows no MRR-improvement differentiation -> the
  reachability_audit schema_fit signal and the additive_map surprise signal are more redundant than the theory
  predicts (matches the v4 note's single biggest flagged uncertainty, P=0.30 there — this test directly resolves
  it rather than assuming it away).
- HARD-FAIL localization 2: if TAU/PRECISION_MIN sweep shows no setting separates NOISE (batch 3) cleanly from
  GENUINE-NOVEL (batch 2) -> recurrence-count is measuring the wrong thing (e.g., needs cross-provenance weighting,
  not raw count) — a metric-design problem, not a combination-rule problem.

## Cross-thread synthesis

- Directly supersedes Section 4 ("Gate combination logic") of `research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`
  — the ad hoc decision tree there is replaced by the derived 2-way decomposition above; the recurrence-as-hard-floor
  framing there is retained only as a PRACTICAL variance-control approximation to a theoretically continuous
  precision-accumulation process (A3/B5), an important nuance v4 did not have.
- Confirms and sharpens v4's flagged single biggest uncertainty ("is the additive_map surprise signal genuinely
  non-redundant with reachability_audit's schema_fit signal, P=0.30") — this drill's cheap decisive test is a direct
  empirical resolution of that exact question, not a new question.
- Consistent with `research_rank_vs_dimensionality_brain_check_2026-07-15.md`'s general finding that the brain
  achieves capability by SUMMING several low-rank/simple components rather than one complex operator — the
  fast_track/slow_track decomposition here is structurally the same move (two simple multiplicative terms summing
  the routing decision) applied to the consolidation-gate problem instead of the readout-operator problem.
- The Tse et al. 2007 3h-fail/48h-pass dissociation (A2) is the single most load-bearing NEW quantitative anchor
  this drill adds beyond v4 — v4 cited Tse qualitatively ("~48h") but this drill confirms the exact contrasting
  failure point (3h) that defines the transition as a genuine narrow-window gate, not a vague "fast" claim.

## Substrate-product implications

1. The decomposition costs ZERO new scoring mechanism beyond v4's already-proposed pieces (`score_all` for raw_PE,
   `reachability_audit.py` for schema_fit) — it is a different ARITHMETIC combination of the same two already-VET-confirmed
   signals, not a new build. The cheap decisive test is correspondingly cheap.
2. The single biggest calibration risk (per Part A) is that the biology gives us a FORM for recurrence-as-precision
   (log-sum/saturating) but zero transferable constants — TAU must be measured on our own KGE coordinate geometry,
   not imported from ACT-R's declarative-memory decay parameters (different substrate, different noise model).
   Flag this explicitly so no future session mistakes a borrowed FORM for a borrowed NUMBER.
3. If the cheap decisive test's HARD-FAIL localization 1 fires (schema_fit and surprise ARE redundant on this
   substrate despite different coordinate geometries), the fix is not to abandon the decomposition — it is to find
   a genuinely orthogonal schema-fit proxy (candidates from Tier-1 fields in the field advisor: network-science
   spectral-gap measures, or a second graph-metric independent of BFS-reachability) before re-testing the same
   arithmetic form.
4. The A2 finding that schema-fit's memory-strength effect is an ASYMMETRIC U-shape (steeper on the congruent side,
   Quent et al. 2022) suggests the substrate rule's `schema_fit` term may eventually need a nonlinear (not linear)
   transform before use as a mixing weight — flagged as a plausible v6 refinement, not built into this rule yet
   (keep the linear mixing-weight form until the cheap decisive test shows it's insufficient — don't over-engineer
   ahead of evidence).

## Citations (verified count: 20 distinct sources across 4 lit-scans; several flagged gaps are themselves
confirmed-absence findings, not search failures)

**Surprise/novelty:** Eshel, Tian, Bukwich & Uchida 2016, *Nat Neurosci* 19:479-486 (PMC4767554, primary, verified);
Bayer & Glimcher 2005, *Neuron* (abstract-level, primary blocked); Schultz 1997/2016 reviews (verified); Lisman &
Grace 2005, *Neuron* 46:703-713 (verified existence, no quantitative primary data retrieved); Duszkiewicz et al.
2019, *Trends Neurosci* 42:102-114 (verified, explicit-gap statement confirmed in full text); Moncada & Viola 2007,
*J Neurosci* 27:7476 (verified); Ballarini et al. 2009, *PNAS* 106:14599-14604 (verified).

**Schema-congruency:** Tse et al. 2007, *Science* 316:76-82, DOI 10.1126/science.1135935 (verified, primary full
text, exact stats obtained); Tse et al. 2011, *Science* 333:891-895 (verified via van Kesteren 2012 citation);
van Kesteren, Ruiter, Fernandez & Henson 2012 (SLIMM), *Trends Neurosci* 35:211-9 (verified, primary full text,
confirmed no equations); Quent, Greve & Henson 2022, *Psych Science* (verified, primary, quantitative); McClelland
2013, *J Exp Psychol Gen* 142:1190-1210 (existence verified, mechanism characterization from secondary sources only).

**Recurrence:** Schapiro/Turk-Browne statistical-learning line (Schapiro et al. 2012/2013/2016/2017; Hippocampus,
PMC5876146) (verified existence, primary numeric detail partially unretrieved — flagged); Fiser & Aslin 2001/2002
(verified via secondary citation); EEG frequency-tagging study, *Neurobiology of Language* 2023 (verified, primary);
Cepeda et al. 2006, *Psych Bull* (verified meta-analysis); Cepeda et al. 2008, *Psych Science* "Temporal Ridgeline"
(verified, primary); Pavlik & Anderson 2005, ACT-R spacing model (verified, equation-level).

**Combination theory:** Itti & Baldi 2005/2006/2009 (PMC2782645; ilab.usc.edu PDF, verified primary, exact equation);
Friston 2005/2010, *Nat Rev Neurosci* (verified, PMC4235126, exact equation); Spens & Burgess 2023/2024, *Nat Hum
Behav* (verified existence, confirmed does NOT use the exact schema-conditioned-KL formalism); Murphy, "Conjugate
Bayesian analysis of the Gaussian distribution" (verified, standard reference, exact equation).

## Deflated confidence (lit-scan calibration: deflate 0.15-0.25 off undeflated read; novel-synthesis capped at 0.50)

- **P(the quantum-table numbers reported here are accurate representations of the cited primary sources)** = **0.70**
  (undeflated ~0.85-0.90 for the items marked "High/primary"; several items are secondary-sourced or
  partially-blocked full-text, explicitly flagged in the tables above — this is a genuine access-limitation
  deflation, not a doubt about the underlying science).
- **P(the fast_track/slow_track decomposition is the right FORM to adopt, i.e. genuinely improves over v4's ad hoc
  decision tree when tested)** = **0.40** (novel synthesis, capped at 0.50 per discipline, further deflated for
  compound risk — it is well-motivated by Friston's hierarchical precision-weighting logic but this exact
  decomposition has never been tested on any KGE-style coordinate geometry, brain-derived or synthetic).
- **P(cheap decisive test, as specified, HARD-PASSes)** = **0.30** (undeflated ~0.45-0.50; this is the harder,
  compound claim requiring schema_fit-tertile-conditioned MRR-improvement differentiation, not just a routing-label
  check — genuinely uncertain until measured).
- **P(recurrence-as-precision-accumulation, log-sum/saturating form, transfers cleanly to a hard TAU/PRECISION_MIN
  setting on this substrate without re-derivation)** = **0.35** (the FORM is well-supported across two independent
  formalisms — ACT-R and conjugate-Bayes — converging on the same shape, which raises confidence in the FORM
  specifically; the CONSTANT is explicitly not transferable, per substrate-product implication #2).

## Next-drill candidate

If the cheap decisive test is piloted and HARD-FAIL localization 1 fires (schema_fit and surprise prove redundant
on this substrate): next drill is a genuinely orthogonal schema-fit proxy from `network-science-graph-theory`
(Tier-1 in the field advisor) — spectral-gap / expander-mixing measures as a second, independently-derived
schema-fit signal to test against reachability_audit's BFS-based one, before concluding the decomposition itself
is wrong rather than just under-differentiated by a single degenerate metric. If the test instead shows the
decomposition works but TAU/PRECISION_MIN need substrate-specific tuning: that is a cheap follow-up sweep, not a
new research drill.
