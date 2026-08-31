---
problem: the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision
status: SOLVED
bar: "PASS = BOTH gates. (1) INFORMATIVE: live per-argument surprisal predicts the reader's OWN comprehension errors (who-did-what wrong) CI-separated over chance (AUC/point-biserial lower bound > 0.5), and a SHUFFLED-surprisal twin (same values permuted across arguments) LOSES CI-separated. (2) ACTIONABLE: gating ONE brain-faithful decision by the signal -- surprisal-abstain (hold the highest-surprisal answers) OR surprisal-weighted predict-and-revise -- beats the un-gated reader on a downstream comprehension metric CI-separated, with the info-free (random same-rate) twin NOT helping. Report CI half-width + null p95 beside every margin; precision-weight as the graded brain signature. A rigorous NEGATIVE is a full PASS: if the live signal is too weak to drive a decision (informative but not actionable, or ceiling'd), enumerate WHY."
result: "INFORMATIVE PASS: live per-argument surprisal (hdlab.predictive_reader driven on the reader's OWN patient bindings through SituationReader.read, role-capable) predicts the reader's own who-did-what errors AUC 0.651 [0.630,0.672] (ROC-AUC; n=2606 QA-SRL v2 dev+test patient items, MODERN text; CI half-width 0.021), shuffle-surprisal twin AUC p95 0.519 (loses). ACTIONABLE PASS via surprisal-abstain: committed accuracy at 80% coverage 0.633 vs random-abstain twin 0.598 -> margin +0.035 [+0.022,+0.050] CI-sep (half-width 0.014). Generalizes to 19c LitBank narrative: AUC 0.624 [0.556,0.690] (n=311, 14 docs), twin p95 0.562."
floor: "un-gated reader base accuracy 0.599 (no surprisal signal); random same-rate abstention twin committed acc 0.598 (flat); shuffled-surprisal AUC null p95 0.519 (chance 0.5). The live signal clears all three CI-separated."
controls: "(1) shuffled-surprisal twin R=500 (values permuted across arguments) -> AUC null p95 0.519 = EXCLUDES 'any per-argument number ranks errors'. (2) random same-rate abstention twin -> committed acc 0.598 flat = EXCLUDES 'any withholding at this rate helps'. (3) info-free random-adopt reanalysis twin p95 -0.005 = EXCLUDES 'any reanalysis helps'. (4) NON-CANONICAL stratum n=603 (passive/fronted) gives reanalysis its strongest shot -> +0.003 [-0.010,+0.016] = EXCLUDES 'the re-selection wall is a canonical-case artifact'. (5) LitBank 19c slice = EXCLUDES 'modern-vocabulary artifact'. (6) precision terciles (top 0.684 vs bottom 0.628) = EXCLUDES 'diagnosticity is precision-flat'."
files_changed: "experiments/_forward_prediction_live.py; experiments/exp_forward_prediction_live_decision_v1.py; experiments/exp_forward_prediction_reselector_probe_v1.py (the exemplar re-selector prototype); verification/test_forward_prediction_live_decision_organ.py; data/forward_prediction_live_decision_v1/metrics.json; data/forward_prediction_reselector_probe_v1/metrics.json; notes/problems/the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision/{SOLVED.md,research_drill_1_surprisal_as_error_signal_2026-08-31.md,research_drill_2_grounded_space_reselection_wall_2026-08-31.md}. hdlab/ UNTOUCHED."
reverify: ".venv/Scripts/python.exe verification/test_forward_prediction_live_decision_organ.py"
---

# The forward-prediction organ is now a LIVE control signal (validated as a flag + confidence gate; the re-selector is a brain-attested next lever)

## What was asked
`hdlab/predictive_reader.py` computes the brain's best account of the N400 -- a verb (+ role)
pre-activates the expected argument's grounded MEANING features, and the mismatch of the actual
argument is read out as `-log P` softmax SURPRISAL. It was held-out-validated IN ISOLATION on QA-SRL
but was a PURE INERT ISLAND: never computed on any live reader path (`situation_reader`/`substrate`
do not import it; the one file that does, `incremental_parser`, keeps it inert by default). So the
forward half of predictive coding drove no decision. The bar: compute the surprisal LIVE through
`SituationReader.read()`, prove it is decision-relevant (predicts the reader's OWN who-did-what
errors, shuffled-surprisal twin losing), and drive ONE brain-faithful decision that measurably
improves the reader -- or, if too weak, enumerate WHY.

## Verdict: SOLVED -- both gates met, plus a rigorous brain-attested negative on the third
- **INFORMATIVE (PASS).** The live per-argument surprisal is a strong RISK signal for the reader's
  own patient mis-bindings: **AUC 0.651 [0.630, 0.672]** over chance (n=2606 QA-SRL dev+test patient
  items, scored through the live role-capable `read()`), point-biserial r=0.263, **shuffle-surprisal
  twin p95 0.519** (loses). This is the first time the organ's signal is computed on a live reader
  path at all.
- **ACTIONABLE (PASS) via surprisal-abstain.** Withholding the highest-surprisal answers (the brain's
  "withhold/re-read when surprised") raises committed accuracy monotonically 0.62 -> 0.70 as coverage
  drops 0.9 -> 0.5, while a random-abstention twin stays flat ~0.60. **Margin at 80% coverage +0.035
  [+0.022, +0.050]** CI-separated over the un-gated reader AND the info-free twin.
- **Precision-diagnosticity GRADED signature (the brain's can-fail curve) -- CI-SEPARATED at power.**
  The surprisal->error AUC is steeper for SHARP (high-precision) verbs than diffuse ones -- **top-
  precision-tercile AUC 0.684 vs bottom 0.628, gap +0.056 [+0.005, +0.110] CI-separated** (the median
  split is +0.029 [-0.014,+0.071], directional -- the effect concentrates at the extremes, as
  expected). A sharply-constraining verb makes a more trustworthy prediction, so its error signal is
  more diagnostic (Friston precision-weighting; Federmeier f-PNP). Measured at the DECISION layer, not
  on raw surprisal magnitude.
- **GENERALIZATION.** The INFORMATIVE signal transfers to 19c LitBank narrative: **AUC 0.624 [0.556,
  0.690]** (n=311), twin p95 0.562 (loses). The meaning-level prediction is not a modern-vocabulary
  artifact (it predicts features, not word-forms -- Nieuwland 2018). Abstain generalizes directionally
  there (+0.024, not CI-sep at that n / error rate 0.68).

## The wall we crossed, and the wall we hit (and understood to the mechanism)
The bar offered TWO candidate decisions: surprisal-abstain OR surprisal-weighted predict-and-revise.
A brain-foundational research drill (folded below) reframed BOTH, and the data confirmed the reframe:

- **Re-read / withhold (abstain) is the brain's most directly-evidenced control ACTION** (regressions
  to re-check, Levy/Bicknell/Slattery/Rayner 2009; semantic-P600 conflict monitoring, Van Herten &
  Kolk 2005/06). It WORKS live (the PASS above).
- **Auto-revise-toward-the-prediction is what the brain does FIRST but it IS the "good-enough" error**
  (Ferreira 2003; Gibson 2013). We tested it as the ambitious decision and it **FAILS**: using
  surprisal to RE-SELECT the patient (adopt the lowest-surprisal alternative) does not beat the reader
  at any threshold (delta -0.002 [-0.009,+0.004]); the info-free twin also hurts (p95 -0.005). Given
  its STRONGEST shot -- the **non-canonical regime** (passive/fronted, n=603, where word-order is
  unreliable and thematic-fit should help most) -- it STILL does not help (+0.003 [-0.010,+0.016]).
  This is the ENUMERATED NEGATIVE the bar welcomes, and a second research drill pinned it precisely:

  > **The flag-works / re-selector-fails split is a KNOWN, brain-attested dissociation, not a bug.**
  > Detecting an out-of-distribution argument (violation detection) needs one coarse boundary -- easy,
  > and 12 grounded sensorimotor dimensions draw it well (AUC 0.65). Ranking two IN-distribution
  > plausible competitors needs the distribution's fine internal metric -- verb-specific, relational,
  > exemplar-based -- which a **centroid of sensorimotor means throws away** (Santus 2017: cosine-to-
  > prototype conflates senses; Nosofsky: prototypes lose within-category discrimination). Kauf et al.
  > 2023 is a near-exact large-scale analog (models separate impossible/possible but not likely/
  > unlikely). The brain runs the fine version in a DIFFERENT hub -- angular-gyrus / generalized event
  > knowledge (McRae & Matsuki; Elman 2009; Metusalem 2012), not the ATL sensorimotor-feature hub.

  So the honest claim is NOT "surprisal can't rank" -- it is **"the grounded PROTOTYPE is the wrong
  estimator; a structured, verb-specific EXEMPLAR/event store is the brain's re-selector."** I
  PROTOTYPED that fix and DECOMPOSED the wall (`experiments/exp_forward_prediction_reselector_probe_v1.py`,
  n=2462 of the reader's OWN live who-did-what items, exemplar store fit on QA-SRL train):

  - **The estimator class WAS part of the wall, and the fix recovers it CI-separated.** Keeping the
    SAME 12-d grounded space but swapping the prototype CENTROID for an EXEMPLAR store (re-selection
    top-1 = mean of the top-3 most-similar SEEN fillers of that verb-role; Erk 2007; Nosofsky) lifts
    re-selection top-1 accuracy **0.364 -> 0.445, +0.081 [+0.061,+0.102] CI-separated** over the
    prototype (nearest-exemplar +0.075 CI-sep; Santus feature-overlap did NOT help, -0.023). The
    prototype centroid was demonstrably the wrong estimator, exactly as drill 2 predicted.
  - **But it does NOT yet cross the wall to beat the PARSE.** Even the exemplar re-selector (0.445),
    and even GATED by the validated surprisal FLAG (trigger on the top 10-50% most-surprising bindings,
    re-select with the exemplar store), stays BELOW the reader's own positional/parse pick (0.579) at
    every trigger level (best -0.011 at the tightest trigger) -- though exemplar beats prototype at
    every level (e.g. -0.011 vs -0.016), so the estimator-class gain is robust.
  - **DECOMPOSITION (the actionable finding):** the re-selection wall = ~+0.08 ESTIMATOR CLASS (now
    FIXED by the exemplar store, CI-sep) + a residual ~0.13 to the parse that is the MEANING
    REPRESENTATION itself (its 12-d dimensionality + missing relational/event structure). That residual
    is the Phase-1 meaning-supply lever, and it is genuinely UNBUILT: VERIFIED BY ENUMERATION the shelf
    has no broad-coverage general-semantic word space (`lexical_similarity` = 89 hand-authored concepts,
    open-vocab is "a missing-LEARNING follow-up"; `distributional_meaning_channel` = substitutability-
    scoped, WordSim rho -0.24; `ppmi_sparse_encoder` = supervised trigram encoder). So the follow-on is
    a STRUCTURED verb-role -> rich-filler event store (Chersoni SDM; angular-gyrus GEK; FHRR role-filler
    binding), NOT more of the 12-d centroid.

  We do NOT generalize the narrow failure to "impossible": the estimator-class half is now fixed and
  measured; the residual is a named, unbuilt asset (the Phase-1 lever), not a ceiling.

## Brain-fidelity labeling (PINNED vs OUR-INVENTION)
- **PINNED (replicated):** forward pre-activation of expected FEATURES; surprisal = -log P softmax
  (Hale/Levy/Michaelov, the N400); that misinterpretation lives at low-probability argument sites
  (Ferreira good-enough); that the brain flags conflict (semantic P600) and can re-read (regressions);
  precision-weighting (sharper prediction -> more diagnostic error). The abstain/withhold decision.
- **OUR-INVENTION-UNDER-TEST (labeled, per drill 1):** that the surprisal of the reader's OWN binding
  is DIAGNOSTIC of a comprehension error -- validated here as a RISK FLAG (AUC 0.65), NOT a verdict.
  The abstain threshold / coverage. The grounded space as the feature basis (its coarseness is the
  measured ceiling for re-selection).

## What I did NOT establish (and would withdraw first if wrong)
- **First to withdraw:** the precision-diagnosticity signature is CI-separated only at the tercile
  EXTREMES (+0.056 [+0.005,+0.110]); the median split is directional (+0.029 [-0.014,+0.071]). The
  graded signature is real at the extremes but modest -- if it fails to replicate, the abstain/AUC
  gates stand on their own.
- Abstain generalization to 19c LitBank is DIRECTIONAL (+0.024), not CI-separated at n=311 -- the
  INFORMATIVE signal generalizes CI-sep there, the abstain ACTION does not yet.
- AGENT-role who-did-what was not scored (agents are frequently pronouns the role binder cannot bind);
  the signal is validated on PATIENT selection. Cross-role generalization is untested.
- The population is items where the reader COMMITTED a grounded non-pronoun patient (65% of gold items;
  the rest are reader-abstains / extraction misses / pronoun gold / ungrounded picks -- reported in
  `population.*_counts`). The signal is validated on the reader's committed who-did-what, not on its
  recall.

## KEY REALIZATIONS (the enabling moves)
1. **Run read() on QA-SRL by auto-marking nominals as singleton mentions.** The reader derives its
   candidate arguments from the CoNLL coref column, so feeding it its OWN pos-tagger's nominals (via a
   temp CoNLL) isolates the ROLE-ASSIGNMENT variable exactly as the QA-SRL power cell supplies gold
   candidates -- letting the reader bind roles itself, live, on gold-annotated text.
2. **The right INFORMATIVE framing is a RISK FLAG, not a verdict (drill 1).** The closest pinned
   mechanism is the semantic-P600 conflict monitor; "surprisal = wrong" is OUR-INVENTION. Framing it as
   risk (AUC), and abstain as the confidence readout, is what made the actionable win honest.
3. **The decision the brain does FIRST (auto-revise) is the one to AVOID committing.** The drill's
   sharpest steer: revise-toward-plausible IS the good-enough error. Testing it and watching it fail
   -- especially in the non-canonical regime where it should most help -- is what makes the negative
   trustworthy rather than a tuning artifact.
4. **Decompose the negative before excusing it (drill 2).** The flag-works/re-selector-fails split is a
   prototype-vs-exemplar dissociation with a named brain locus (angular gyrus / event knowledge) and a
   near-exact prior analog (Kauf 2023). That turns "our revision failed" into "the centroid is the
   wrong estimator class; build the structured event store" -- a direction, not a ceiling.
5. **PROTOTYPE the fix in the SAME space to separate estimator-class from dimensionality.** Swapping
   only the estimator (centroid -> exemplar store) while holding the 12-d features fixed is the fair
   test of drill 2's claim: it recovered +0.08 CI-sep (estimator class was real) and localized the
   residual to the meaning representation -- turning "the grounded space is the ceiling" from an
   assertion into a MEASURED decomposition (estimator +0.08 fixed; ~0.13 residual = Phase-1 lever).

## AUDIT UPDATE (fold into notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
`predictive_reader` is no longer a pure inert island in evidence: its surprisal is now computed LIVE
through `SituationReader.read()` and shown decision-relevant. NEW PINNED-AND-MEASURED: (a) the forward-
prediction signal is a validated **error-RISK flag** on the reader's own who-did-what (AUC 0.651 CI-sep,
shuffle twin loses, generalizes to 19c narrative); (b) it drives a validated **confidence/abstain**
decision (+0.035 CI-sep committed-accuracy over random abstention); (c) **precision-weighted
diagnosticity** is a directional graded signature (sharper verb -> more diagnostic). NEW MEASURED
DEVIATION / CEILING: the grounded 12-d sensorimotor CENTROID is a valid violation-DETECTOR but an
invalid argument RE-SELECTOR (revision fails even in the non-canonical regime) -- a prototype-vs-
exemplar dissociation (Kauf 2023; Santus 2017; Nosofsky) whose brain locus is the angular-gyrus / event-
knowledge hub, NOT the ATL feature hub. The forward predictor is thus a FLAG, wired; the RE-SELECTOR is
the Phase-1 meaning-supply follow-on. Correct the audit's `predictive_reader` "island" line to "island
in code; validated LIVE as a flag/abstain signal in experiments, proposed for a default-off wire (Q111)."

## PROPOSED hdlab CHANGE (Q111 -- strategy lands; a proposed diff, not a landed one)
A default-off flag on `SituationReader` (byte-identical when off, the causation/timeline additive
pattern): `predict_surprisal=False`. When on, `read()` (a) fits/loads a `PredictiveReader` on the QA-SRL
triple corpus once, (b) for each bound (predicate, agent/patient, filler) computes the surprisal among
the sentence's candidate nominals, exposing it as additive metadata on `EventRecord` (e.g.
`patient_surprisal`, `precision`), and (c) an optional `surprisal_abstain_tau` marks the highest-
surprisal bindings LOW-CONFIDENCE (a `low_confidence` flag / abstain) -- the validated decision. NO
external LLM, NO spaCy (the reader's own pos_tagger + arc_parser + grounded space). This is the FIRST
live node of the prediction-error hierarchy. Do NOT wire auto-revision (it fails; see the wall).

## ADJACENT COMPONENTS -- capability / fidelity / opportunity (seeds the next problems)
| Component | Brain role | Fidelity now | Opportunity -> next problem |
|---|---|---|---|
| `grounded_similarity` (12-d sensorimotor centroid) | the feature basis prediction runs in | **OUR-INVENTION prototype** -- valid detector, invalid re-selector (measured) | **THE seeded follow-on:** a structured verb-role -> grounded-filler EXEMPLAR/event store (angular-gyrus GEK; Chersoni SDM; FHRR-compatible role-filler binding) as the RE-SELECTOR. The Phase-1 meaning-supply lever. Highest yield. |
| `gap_detector` (CA1 novelty / write-on-surprise) | memory write-gate | WIRED but ablation-AMBIGUOUS (fires no decision) | **My live surprisal is its natural drive signal** ("surprised -> write to memory") -- the same prediction-error signal at the memory level, and on the LEARNER-ON critical path. |
| `n400_coherence_monitor` (backward event-coherence) | detect incoherence | ISLAND; flagged does-not-hold at real operating point | Compose forward (this) + backward -> **event boundaries from prediction-error peaks** (Zacks/EST). |
| `slot_attention_wm` (PBWM WM-gate) | gate WM entry | ISLAND | The WM-gating level of the same hierarchy; unwired. |
| role binder (`predicate_argument_frontend`, positional/wired) | who-did-what | parse-as-TRUTH (un-brain-faithful, per SPACE) | My abstain converts the pick toward parse-as-EVIDENCE (flag low-confidence bindings). |

## ADJACENT DEFECT TO FILE (robustness, not mine to fix)
`hdlab/frame_induction.is_passive_real` loops `range(lo, v_idx)` and indexes `tokens[i]` with no upper
guard, so `read()` raises `IndexError` on edge-case sentences where the emitted predicate index exceeds
the sentence length (an additive frame-primary-role metadata path, un-disableable by any constructor
flag). Rate here: ~1 in ~1300 sentences. A one-line bounds check (`range(lo, min(v_idx, len(tokens)))`)
fixes it. This driver skips+counts these honestly (`population.*_counts.reader_crash`).

## TLDR (plain English)
We had built the brain's "guess the next word's meaning and notice when you're wrong" machine, proved
it works on its own, then left it switched off inside the reader. I switched it on: as the reader works
out who-did-what in real sentences, it now computes that surprise live, and the surprise reliably marks
the places the reader gets who-did-what wrong (a scrambled version of the surprise marks nothing). I
used it for one concrete thing the brain does -- hold back the answers it's most surprised by -- and
that makes the reader measurably more accurate on the answers it does commit to, where holding back at
random does not. It even works on 200-year-old novels, not just modern text, because the guess is about
meaning, not exact words. I also tested the more aggressive move -- when surprised, swap in the more
plausible answer -- and it does NOT help, and I found out exactly why: our "meaning" is a blurry average
of what a verb usually acts on, which is enough to say "that's weird" but not to pick the right one of
two reasonable options. That is a known split (the brain does the fine version in a different part of
the brain), and it points cleanly at the next build: give the machine a richer, verb-specific memory of
what actually fills each slot.

## QUESTIONS
None.

## NEXT STEPS (follow-on problems)
1. **Build the RE-SELECTOR (highest yield, Phase-1 meaning lever):** the exemplar-store prototype here
   (experiments/exp_forward_prediction_reselector_probe_v1.py) already recovers the ESTIMATOR-CLASS
   portion (+0.08 CI-sep) -- promote it as the re-selection estimator. The remaining ~0.13 to beat the
   parse is the FEATURE space: build a structured verb-role -> RICH-filler event store (broad-coverage
   distributional/relational features; Chersoni SDM; angular-gyrus GEK; FHRR role-filler binding) to
   replace the 12-d grounded centroid, and retest gated revision with THIS as the prior. The measured
   decomposition (estimator +0.08 fixed; ~0.13 residual = feature space) tells the follow-on exactly
   where the yield is.
2. **Wire the abstain flag now (Q111):** the validated confidence/abstain decision does not depend on
   the re-selector build.
3. **Feed `gap_detector`'s write-gate from this surprisal** (the memory-level node; learner-on path).
4. **(measure-only) wider-feature probe:** how much of the re-selection gap is dimensionality vs
   estimator class (Kauf predicts it narrows but does not close).
5. Agent-role who-did-what slice; strengthen the precision signature to CI-separation at power.
