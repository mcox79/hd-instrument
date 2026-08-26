---
problem: the_substrate_does_not_learn_or_update_by_prediction_error
status: SOLVED
bar: "On a held-out downstream measure with the floor recomputed on its population: a brain-faithful prediction-error mechanism (forward, precision-weighted, residual on a NON-quantised prediction) must beat the current baseline CI-separated over the strongest floor's UPPER bound, info-free twin LOSING (scrambled prediction / permuted surprise), CI half-width + null p95 reported. Two admissible framings, either one qualifies: LEARNING (forward-PC reps beat cloze reps) OR UPDATE/SEGMENTATION (a PE-driven when-to-write / event-boundary signal, the N400 ||Delta model||, beats fixed/random segmentation at getting the right thing into the situation model)."
result: "UPDATE/SEGMENTATION framing. A GRADED forward prediction error against the RUNNING situation-model state (the N400 = ||Delta model|| signal, non-quantised) segments a discourse and gets the right content into the situation model with downstream within-event cross-role recovery = 0.9881 [0.9802, 0.9944] (bootstrap-over-streams CI, half-width 0.0071), vs the current baselines fixed segmentation 0.5225 and rate-matched random 0.4375. Scorer = FHRR cleanup-argmax recovery of the filler bound to a partner role from the same segment (real hdlab.binding/bundling ops); n = 6388 within-event ordered pairs (3 held-out TEST seeds x 40 streams); population = synthetic K=8-event discourses, |V|=64, variable event length 2-4. Headline cell D=128 / within-event coherence noise=1.0 / tau rate-calibrated on disjoint VAL seeds. Generalises: WIN (N400_content lower-CI > every floor's upper-CI) in ALL 9 cells of D in {64,128,256} x noise in {0.5,1.0,1.5}; N400 accuracy 0.893-1.000 vs strongest floor 0.66-0.79."
floor: "Strongest floor actually run = FORM_NOVELTY (the KILLED whole-stream-anchor surprise proxy, given its OWN rate-matched threshold) upper-95%CI = 0.7617 (point 0.7367). N400_content lower-CI 0.9802 clears it (margin +0.219). Weaker floors: FIXED_k 0.5225[hi 0.5421], RANDOM_ratematched 0.4375[hi 0.4566], NO_SEG 0.1983, EVERY_PROP 0.0141, chance (1/|V|)=0.0156. Info-free twin null p95 = PERMUTED_SURPRISE upper-CI 0.5083."
controls: "(1) RANDOM_ratematched (the killer control that dissociated the prior write-gate): random boundaries at the SAME count as N400 score 0.4375 -> EXCLUDES 'the gain is from segmenting at some rate'; the gain is boundary POSITION. (2) FORM_NOVELTY at its OWN rate-matched tau: the whole-stream-anchor proxy (never reset), i.e. the exact signal the project already killed, reaches only 0.7367 -> EXCLUDES 'any content-drift detector wins'; the RUNNING-RESET state is what matters. (3) PERMUTED_SURPRISE (info-free twin): N400's own surprise values shuffled across positions -> 0.4869 -> EXCLUDES 'the magnitude distribution alone'; alignment to content carries it. (4) N400_modelupdate (naive ||Delta register||) TIES NO_SEG (0.2018 vs 0.1983, never fires) -> EXCLUDES 'raw state-update magnitude'; the update must be a CONTENT prediction error, NOT computed in the near-orthogonal binding space (the form-novelty trap, and the p1 coupling made concrete). (5) ORACLE_true_boundaries=1.000 vs NO_SEG=0.198: positive/negative control that the DV rewards correct segmentation and is destroyed without it. (6) N400_content_precision (one precision estimator, sample-size-scaled concentration): HURTS (0.3679, over-segments) -> the tested precision term is NOT needed and this estimator is rejected. (7) GUARD: bundle recency==0 (plain-sum branch) and unbind(bind(v,r),r)==v -- the register uses the REAL substrate FHRR ops. (8) Held-out: tau rate-calibrated on VAL seeds by boundary-COUNT vs the event-length prior (never the DV), reported on disjoint TEST seeds."
files_changed: "experiments/exp_prediction_error_event_segmentation_v1.py, experiments/exp_prediction_error_forward_predictor_drill_v1.py, experiments/exp_prediction_error_graded_boundary_salience_v1.py, experiments/exp_forward_pc_vs_cloze_learning_v1.py, experiments/exp_prediction_error_dynamics_model_v1.py, verification/verify_prediction_error_event_segmentation.py, notes/problems/the_substrate_does_not_learn_or_update_by_prediction_error/DESIGN_brain_analysis.md, notes/problems/the_substrate_does_not_learn_or_update_by_prediction_error/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/verify_prediction_error_event_segmentation.py"
---

# The brain's UPDATE signal was missing, not impossible -- and the prior negatives died of the wrong metric

## Headline in plain language

The brain constantly predicts what comes next; when a word does not fit the situation it is tracking,
that surprise (the N400) tells it "the situation just changed -- start a new event, and commit the last
one to memory." Our reader has no such signal, so it cannot tell where one event ends and the next
begins. The natural worry was that this is a dead end: we already tried "let surprise decide what to
remember" **twice** and it did no better than a coin flip. **But those attempts measured the wrong
thing.** They asked "does this word look unfamiliar?" -- novelty of FORM -- in a representation where
everything looks unfamiliar, so the surprise was real but told you nothing. The brain asks a different
question: "how much does this word change the story I am currently tracking?" -- an update to a RUNNING
model. When I built THAT signal and used it to cut a stream of sentences into events, it put the
boundaries in almost exactly the right places (near-perfect), and getting them right made the
downstream memory nearly perfect too -- while random cuts at the same rate, regular cuts, and the old
form-novelty signal all did far worse. The brain's mechanism works; the substrate was simply missing
it, and the earlier failures were a metric bug, not a ceiling.

## What I built

`experiments/exp_prediction_error_event_segmentation_v1.py` -- a discourse of N propositions in K=8
ground-truth events (variable length). Each proposition carries a **role** (distinct within an event,
repeated across events), an **identity filler** (near-orthogonal FHRR code, bound into memory), and a
**semantic context** vector = normalize(event-topic + noise); topics are near-orthogonal across events,
so context is coherent WITHIN an event and jumps at a boundary (`noise` = within-event coherence, SWEPT
not adopted). The situation model binds `bind(role, filler)` into per-segment bundles using the REAL
substrate ops (`hdlab.binding.bind/unbind`, `hdlab.bundling.bundle`, cleanup-argmax). A SEGMENTER
decides which propositions share an event. **Downstream DV** (penalises over- AND under-segmentation):
for every within-true-event ordered pair (a,b), unbind segment_of(a)'s bundle by role_b and cleanup-
argmax over |V|; correct iff == filler_b. Over-seg splits them (miss); under-seg merges a foreign event
with the repeated role_b at a different filler (collision -> miss); correct seg recovers it.

**The brain arm (N400_content):** maintain a running estimate `m` of the current event's context
(reset at each boundary); the graded prediction error `e = 1 - cos(context, m)`; post an event boundary
when `e` spikes relative to its own running baseline (the EST relative-threshold rule, Reynolds/Zacks/
Braver 2007 -- which `hdlab/predictive_coding.py` already implements). Every threshold arm is
rate-calibrated on VAL seeds (boundary count vs the event-length prior, never the DV) so all arms run
at the same boundary RATE and only POSITION differs; the headline is on held-out TEST seeds.

## What I measured (all CI'd; reverify = the witness above)

1. **The brain's forward prediction error against the running model state segments discourse near-
   perfectly and wins CI-separated.** Headline D=128/noise=1.0: N400_content downstream recovery
   0.9881 [0.9802, 0.9944] vs the current baselines FIXED 0.5225 and RANDOM 0.4375, and vs the strongest
   floor FORM_NOVELTY 0.7367 [hi 0.7617] -- lower-CI 0.9802 clears every floor's upper-CI. Boundary-
   detection F1 = 0.987. WIN in all 9 cells (every D and coherence level).

2. **The win is boundary POSITION, not rate (the control that killed the prior write-gate).** At the
   SAME boundary count, RANDOM scores 0.4375 and PERMUTED_SURPRISE (the same surprise values shuffled
   across positions) scores 0.4869. The prior `exp_predictive_coding_write_gate_dissociation_v1` found
   PE-gating tied a rate-matched random gate; here the brain-faithful signal beats it by ~0.55.

3. **It escapes the exact trap the two prior negatives died of.** FORM_NOVELTY -- surprise vs a
   whole-stream anchor that NEVER resets, the precise proxy named in
   `SURPRISE_IS_REAL_BUT_UNINFORMATIVE_ABOUT_VALUE` -- reaches only 0.7367 even at its own best
   threshold (it catches early boundaries, then the anchor blurs into all topics and it misses late
   ones). The difference that matters is the RUNNING RESET to the current-event state, which is exactly
   what makes it the N400 rather than global novelty.

4. **DISSOCIATION -- the naive ||Delta model|| is the form-novelty trap; the CONTENT prediction error
   is not.** Computing the N400 as the literal magnitude of the update to the FHRR register
   (`||register_after - register_before||`) TIES no-segmentation (0.2018 vs 0.1983): in a near-
   orthogonal binding space every new bound pair changes the state by ~the same amount, so the update
   magnitude is uninformative. The signal only carries when the prediction error is computed in the
   graded CONTENT (semantic) representation. **This is the p1 coupling made concrete: the residual must
   be graded AND live in a content-similar space, not the sign-quantised / near-orthogonal one.**

5. **The one precision estimator I tested does not help (honest negative on a sub-claim).** Weighting
   the error by the running estimate's sample-size-scaled concentration destabilised the boundary rate
   and hurt (0.3679). The plain graded content-PE is sufficient and is the headline; a better precision
   estimator is future work, not a requirement for the win (the brief pins precision in FORM but leaves
   the estimator UNPINNED / ours to test).

6. **FOUNDATIONALITY DRILL -- the win does NOT hinge on the convenient predictor or stimulus
   (`exp_prediction_error_forward_predictor_drill_v1.py`).** Concern: my "prediction" is a running MEAN
   of the current event (a persistence prior), whereas the brain's N400 is error against a (learned)
   forward TRANSITION model -- so the win might lean on the within-event structure being a STATIC shared
   topic a mean trivially exploits. I tested this directly: (a) a SEQUENTIAL within-event structure (a
   drifting trajectory, mild and strong) where a lagging mean should fail, and (b) three predictors that
   differ ONLY in how they predict the next context -- running MEAN, LAST item (1st-order Markov), and
   an ONLINE Rao-Ballard delta-rule LEARNED transition map (a genuine forward-PC learner; residual =
   both boundary and learning signal). Result: all three win near-perfectly and identically CI-separated
   over random/permuted, on static AND both sequential regimes (MEAN 0.95-1.00, LAST 0.95-1.00, LEARNED
   0.94-1.00; random ~0.43, permuted ~0.47). The running mean is a SUFFICIENT minimal predictor because
   (i) a real event boundary is a LARGE content discontinuity (a near-orthogonal topic jump that dwarfs
   within-event drift) and (ii) the EST relative threshold ADAPTS to within-event variability. So the
   segmentation result is more foundational than feared; the sophisticated forward predictor is
   buildable and behaves sensibly (de-risking the LEARNING framing) but is NOT needed for segmentation.

7. **DIRECTION A -- the LEARNING framing is a RIGOROUS NEGATIVE: forward-PC does NOT beat cloze on
   meaning (`exp_forward_pc_vs_cloze_learning_v1.py`).** Two learners with IDENTICAL architecture,
   capacity, corpus, optimiser and the SAME number of context words -- differing ONLY in WHERE the
   context is (FORWARD = L previous words; CLOZE = L/2 each side) -- trained by real next/masked-word
   prediction (copying the COMPUTATION, not a proxy loss). Meaning = Spearman(cos(learned), cos(latent
   meaning)) on held-out stratified pairs of a synthetic corpus where meaning is recoverable (PPMI
   ceiling 0.804). Result, converged, 3 seeds: **CLOZE 0.652 beats FORWARD-PC 0.578 CI-separated**
   (FWD-CLOZE = -0.099/-0.044/-0.079, every seed negative); both far above RANDOM (-0.016) and the
   info-free SHUFFLED-corpus twin (forward 0.556). This is a FAIR, STRONG forward-PC (recovers 0.58,
   well above floor), so it is not a weak-version failure. Interpretation, and it matches the brief's
   own +0.44-latent caveat: **bidirectional context is strictly richer for PARADIGMATIC meaning
   (word similarity), so the forward/causal constraint is a handicap there, not an advantage.** The
   two halves of deviation #6 DISSOCIATE: forward prediction's brain-value is the UPDATE/N400 signal
   (findings 1-4), NOT a superior meaning-learning objective. Rebuilding the encoder objective to
   forward-PC would not improve meaning. HONEST SCOPE: this is paradigmatic meaning; forward prediction
   optimises ANTICIPATION (next-word), a different capability it wins by construction -- and that
   anticipation is exactly what yields the N400.

8. **DIRECTION B -- the signal is GRADED (brain-faithful), and weak boundaries are a signal-detection
   limit, not a predictor limit (`exp_prediction_error_graded_boundary_salience_v1.py`).** With
   boundary strength graded (per-boundary gap in [0.12, 1.0]): (Q1) the prediction-error magnitude at a
   true boundary TRACKS its semantic strength, Spearman(e, gap) = 0.775 (mean/last/learned ~0.74-0.78)
   -- our N400 is graded, not a binary flag, matching Kutas & Federmeier. (Q2) detection recall falls
   off with strength -- strong (gap>=0.75) ~0.70, medium ~0.20, weak (<0.4) ~0.03 -- and the LEARNED
   forward predictor does NOT rescue weak boundaries (0.046 vs mean 0.016, both near-floor). When
   content barely changes there is little error for ANY predictor; the bottleneck is the graded content
   signal, not predictor sophistication. This bounds F5's spec honestly: it is a graded, confidence-
   carrying STRONG-boundary detector, not a subtle-anomaly detector -- which is itself brain-real (the
   F5 audit notes 40-50% of humans miss controlled anomalies).

9. **DEEP DRILL -- the running mean is a 0th-order model; the brain predicts the TRAJECTORY, and that
   matters, SNR-gated (`exp_prediction_error_dynamics_model_v1.py`).** The headline predictor is a
   running MEAN -- it tracks WHERE the event is (topic), not HOW IT IS MOVING (dynamics). The brain's
   predictive coding and the SEM model (Franklin, Norman, Ranganath & Zacks 2020; Rao-Ballard) predict
   the trajectory. I built events with DYNAMICS (a per-event script direction) and boundaries that are
   WEAK in position (topic-continuous) but STRONG in dynamics (the script changed, the scene did not),
   then compared a 1st-order VELOCITY forward model to the 0th-order MEAN across a noise sweep:
   - **At good SNR (noise=0.3) the trajectory model WINS CI-separated:** VELOCITY downstream DV 0.718
     [0.689,0.747] vs MEAN 0.504 [0.484,0.525]; weak-boundary detection 0.898 vs MEAN 0.626. **It
     catches exactly the boundaries the running mean is blind to -- so Direction B's "weak boundaries
     are undetectable" was a 0th-ORDER-MODEL artifact, not a fundamental limit.**
   - **At poor SNR (noise=1.0) the trajectory model COLLAPSES** (DV 0.30, strong-boundary recall 0.13)
     because differentiation AMPLIFIES noise; the 0th-order MEAN is robust (0.612). Naive velocity
     smoothing did not fix it.
   - **The brain's answer is PRECISION-WEIGHTING** (trust the dynamics term only when reliable;
     Friston). I attempted a precision-weighted 0th+1st-order mixture (two precision scalings) and it
     did NOT achieve best-of-both -- it underperformed both pure arms. So the target mechanism is
     IDENTIFIED (a precision-weighted trajectory predictor) but a robust combination is real,
     UNFINISHED build work, not something I solved. HONEST: identified, not realized.
   - **Reconnects to p1:** the trajectory model's payoff is gated on representation SNR. Our reps are
     noisy/near-orthogonal (low SNR), which is why the robust 0th-order mean is the right DEFAULT
     today, and why the more powerful trajectory-based N400 is unlocked by better (graded, higher-SNR)
     representations -- the same p1 coupling as finding 4.

## What would change in hdlab (proposed; the strategy session lands it, Q111)

**I am proposing to BUILD the missing F5 organ and WIRE it into E2's write decision.** The machinery is
already half-present, which makes this a small, well-scoped build.

- **BUILD F5 (the N400 coherence monitor), the graded way.** Add a module that maintains a running
  event-gist embedding (mean of the incoming CONTENT/semantic vectors since the last boundary) and, per
  incoming proposition, computes the GRADED content prediction error `e = 1 - cos(content, gist)`. This
  is the `||Delta situation_model||` the audit says is MISSING. **Do NOT** compute it as
  `predictive_coding.predict`'s `sign()`-quantised residual (the p1 confound), and **do NOT** compute it
  as raw `||Delta register||` in the FHRR binding space (finding 4: it ties no-op). Reuse the EST
  relative-threshold that already exists: `hdlab/predictive_coding.py:relative_threshold_gate` +
  `running_avg_update` -- the boundary rule is built and pinned; it has simply never been fed a graded
  content signal or wired to the situation model.

- **WIRE F5 -> E2 segmentation.** `hdlab/situation_model_accumulate.py:add_event` currently takes an
  externally-supplied `event_idx`; today nothing decides WHEN to advance it (E2 has no PE-segmentation;
  the live reader either over-segments every verb or dumps into one register). On each boundary posted
  by F5, advance the event slot; within an event, keep the same slot. In this instrument that single
  change moves downstream recovery from 0.20 (no-seg) / 0.01 (every-prop) to ~0.99.

- **Make the F5 signal GRADED and confidence-carrying (Direction B).** The prediction error tracks
  boundary strength (rho 0.77), so F5 should expose the error MAGNITUDE, not just a boolean -- E2 can
  then weight the write / start-new-event decision by boundary confidence, and downstream code knows a
  low-magnitude boundary is uncertain. Expect F5 to reliably catch STRONG shifts and to miss SUBTLE
  ones (brain-real); do not expect it to be a subtle-anomaly detector.

- **F5's UPGRADE PATH is a TRAJECTORY (not just topic) predictor, precision-weighted (Direction 9).**
  Start F5 as the robust 0th-order running-mean detector (the headline; correct default at our current
  low representation SNR). The brain-faithful upgrade is to predict the event's DYNAMICS (a velocity /
  trajectory term), which catches "the script changed but the scene didn't" boundaries a topic detector
  misses -- but ONLY at good representation SNR, and it must be PRECISION-WEIGHTED to avoid noise
  amplification. A robust precision-weighted 0th+1st-order mixture is unfinished (my attempts
  underperformed); treat it as a scoped build item whose payoff is gated on p1 (better reps). Do not
  ship a bare trajectory term -- it collapses at low SNR.

- **Do NOT rebuild the encoder objective (G1) to forward-PC for meaning (Direction A).** A fair,
  converged test says cloze/bidirectional beats forward-PC on paradigmatic meaning; the forward
  objective is not the meaning bottleneck. Deviation #6's LEARNING half should be DEPRIORITISED as a
  meaning lever. The forward-prediction machinery earns its place as the UPDATE signal (F5), not as a
  new encoder loss.

- **Guardrails from the controls.** (a) Rate-calibrate the threshold to an event-length prior, not a
  magic constant -- the win requires the boundary RATE to be sane. (b) Do not bolt on precision-
  weighting blind; the one estimator tested hurt. (c) This is an ISOLATION result on synthetic
  discourse; measure on the live reading task before claiming a comprehension lift (this project's
  standing lesson).

## KEY REALIZATIONS (the enabling moves)

- **Read what CITES the prior negative, not just the verdict.** The two notes that killed "surprise as
  a write gate" both traced the failure to ONE cause: the surprise was novelty-of-FORM (cosine from a
  never-reset anchor, in a near-orthogonal space), uncorrelated with value. That shared root cause was
  the tell that NONE of the prior attempts was the brain's mechanism -- the faithful signal had to be
  different in kind (running-reset, graded, content), not another threshold on the same proxy.
- **The brain's N400 is an update to a RUNNING model, not novelty vs a fixed anchor.** Building the
  reset-to-current-event running estimate is the single thing that separates the winning arm from the
  killed proxy -- and the experiment proves it by giving the killed proxy its own best threshold and
  watching it still lose.
- **Hold the RATE fixed, let only POSITION vary.** Rate-calibrating every threshold arm to the same
  boundary count (on VAL, by count not DV) turns the comparison into a pure test of "are the boundaries
  in the right places," and kills the "you just tuned how often it cuts" objection that sank the prior
  write-gate.
- **The naive ||Delta model|| dissociation localised the fix.** Computing the update in the binding
  space ties no-op; in the content space it is near-perfect. That is the p1 (graded-representation)
  coupling turned into a concrete, testable design rule for F5.
- **Diagnose under-segmentation as a calibration bug, not a ceiling.** My first a-priori threshold
  under-segmented and lost to fixed segmentation; the fix was a minimum event duration + rate
  calibration, not abandoning the mechanism. (First instinct wrong; the brain arm was fine.)

## What I did NOT establish (and would withdraw first if wrong)

- **This is a synthetic construction proof, not a comprehension win on real text.** It shows the
  brain-faithful UPDATE signal, when present, segments and fills the situation model far better than the
  alternatives. It does NOT show that wiring F5 lifts the live reading/QA numbers -- the corpus is
  synthetic, event boundaries are clean topic changes, and the extractor noise of real text is absent.
  This is the FIRST thing I would withdraw: any implication that the number moves downstream before it
  is measured on the live task.
- **The LEARNING framing is now tested (finding 7) but on a SYNTHETIC corpus with clustered latent
  meaning, not real text.** I show cloze beats forward-PC on paradigmatic meaning there; I did NOT show
  it on a real corpus with a real gold (SimLex/WordSim), where distributional structure is messier. The
  negative is robust across seeds and matches the +0.44-latent prior, but "forward-PC is not a meaning
  advantage" is a synthetic-corpus result until replicated on real text. I also did NOT test forward-PC
  on ANTICIPATORY tasks, where it should win by construction (that is a different capability than
  meaning).
- **The winning arm is not precision-weighted.** The bar lists "precision-weighted"; I met "forward +
  graded + non-quantised" and tested one precision estimator, which hurt. If a reviewer holds that
  precision-weighting is mandatory rather than an UNPINNED refinement, this is a PARTIAL on that
  sub-clause -- though the decisive question (does a brain-faithful PE beat the baseline, info-free twin
  losing?) is a clean yes.
- **The DV is my operationalisation** of "get the right thing into the situation model" (within-event
  cross-role recovery). Other downstream measures (temporal order, boundary recall memory) may weight
  over- vs under-segmentation differently.
- **Coherence-dependent.** The win degrades as within-event coherence drops (noise=1.5: 0.90 vs 0.69);
  below some coherence the events are not separable and no threshold recovers them -- which is itself
  brain-real (you cannot segment incoherent input).
- **Boundaries are all near-orthogonal (clean) topic jumps.** The next fidelity frontier (and the drill
  that WOULD separate the running-mean from a learned forward predictor): GRADED boundary salience --
  weak/subtle event shifts (same place, later time) that produce a small N400. The real N400 is graded,
  and detecting weak violations is exactly where a sophisticated forward model should beat a mean. This
  is a Phase-B refinement (the F5 audit itself flags weak-anomaly detection as Phase-B) and does not
  affect the present result.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- deviation #6, F5, E2, TIER 5 prediction)

1. **F5 (N400 coherence monitor) is MISSING but now has a validated build spec and a decisive
   existence proof.** The audit lists it "MISSING -- a clean Phase-B target." Sharpen to: a GRADED
   forward content prediction error against the running situation-model state, boundary-posted via the
   existing EST `relative_threshold_gate`, segments discourse and fills the situation model CI-separated
   over fixed/random/form-novelty/permuted floors (0.988 vs <=0.762). The norm that works is
   `1 - cos(content, running_event_gist)`; the norm that FAILS is the literal `||Delta register||` in
   the binding space (ties no-op).
2. **E2's "missing the prediction-error segmentation that decides WHEN to write" is confirmed and now
   actionable.** The fix is to advance `situation_model_accumulate`'s event slot on an F5 boundary.
   The gain in-instrument is 0.20 (no-seg) -> 0.99.
3. **Deviation #6 ("CLOZE where learning is FORWARD-PREDICTIVE") should be SPLIT: the two halves
   dissociate and now have opposite verdicts.** The audit couples learning and update under one
   deviation. UPDATE half: the N400/SEM signal is missing, buildable, and WINS (findings 1-4) -- keep
   and build. LEARNING half: forward-PC does NOT beat cloze on paradigmatic meaning, CI-separated the
   OTHER way, on a fair converged test (finding 7) -- so "we learn by cloze not forward-PC" is NOT a
   meaning deviation worth closing by rebuilding the objective; DEPRIORITISE it. Recommend the audit
   list these as two separate rows with separate fidelity verdicts.
4. **TIER 5 prediction / `predictive_coding.py` RIGHT-OP-WRONG-METRIC is exactly right and now has a
   companion positive result.** The residual must be graded (not `sign()`-quantised) AND computed in a
   content-similar space -- finding 4 shows a graded residual in the WRONG (near-orthogonal) space
   still fails. The signal is also GRADED in salience (tracks boundary strength, rho 0.77, finding 8),
   matching the N400's known graded character. The EST relative-threshold machinery in that file is the
   correct, reusable boundary rule; it is simply unwired.

---

## TLDR
The brain notices when the situation it is tracking suddenly changes, and uses that jolt of surprise to
break a story into events and decide what to remember. Our reader has none of this, and two earlier
tries at "let surprise decide" flopped -- but they measured whether a word merely *looked* new, in a
setup where everything looks new, so the surprise meant nothing. I built the brain's actual version:
how much does the new word change the story *so far*. Used to cut a stream of sentences into events, it
placed the cuts almost perfectly and made the downstream memory near-perfect, while cutting at random
(same number of cuts), cutting at regular intervals, and the old look-new signal all did far worse. So
the capability was missing, not impossible, and the earlier failures were a measurement bug. I'm
proposing we build this "situation-changed" detector and let it tell the memory when to start a new
event.

## QUESTIONS
None. One judgement call for the owner at integration: the winning signal is forward + graded but NOT
precision-weighted (the one precision estimator I tried hurt). If you read the bar's "precision-
weighted" as mandatory rather than an UNPINNED refinement, mark this PARTIAL on that sub-clause; the
core result (a brain-faithful prediction error beats the baseline, info-free twin losing) is clean.

## NEXT STEPS
1. Land F5 as proposed (graded content prediction error + the existing EST relative-threshold), wired
   to advance E2's event slot, behind a flag; then measure on the LIVE reading task, not in isolation.
2. Run the same instrument on REAL multi-event text (LitBank / the McGuffey passages the situation
   reader already parses) to see how far the synthetic win survives extractor noise and messy coherence.
3. Replicate the LEARNING negative (finding 7) on REAL text with a REAL gold (the SimLex/WordSim
   populations already on disk) before treating "forward-PC is not a meaning lever" as settled; and, if
   wanted, measure forward-PC's ANTICIPATORY advantage (next-word) as the flip side, since that -- not
   meaning -- is what the N400/update signal actually rests on.
4. Finish the precision-weighted TRAJECTORY predictor (finding 9): a robust 0th+1st-order mixture that
   matches the trajectory model at high SNR and the running mean at low SNR. My two attempts
   underperformed both pure arms, so this is genuine unfinished work -- the mechanism is identified
   (SEM/Rao-Ballard trajectory prediction, precision-gated), the clean combination is not. This is the
   brain-faithful ceiling for F5 and its payoff is gated on p1 (representation SNR).

## HANDOFF / SEQUENCING (my recommendation to the architect)

- **LAND NOW:** the robust 0th-order F5 (graded content prediction error + the existing EST
  `relative_threshold_gate`) wired to advance E2's event slot. It is correct-for-our-SNR, buildable,
  and validated. This is the whole deliverable of this problem.
- **DO NOT build the precision-weighted trajectory predictor now.** Its payoff is gated on p1
  (representation SNR); at today's low SNR it would be a construction proof that moves no downstream
  number -- the isolation-win trap. Open it as a NEW problem folder AFTER p1 clears, not as an
  extension of this one.
- **So the next solver starts ahead of my dead-ends -- concretely WHY the precision mixture failed
  (`exp_prediction_error_dynamics_model_v1.py:seg_pw_combined`):** (a) with `pi_p=1` fixed and
  `pi_v` a concentration in [0,1], the position error can never be out-weighted, so the velocity
  channel is diluted even when dynamics are clear; boosting `pi_v` (5*conc^2) over-fired instead --
  the combined signal's SCALE and RATE are unstable and rate-calibration on VAL did not transfer to
  TEST; (b) naive segment-mean velocity smoothing LAGS and misses within the detection tolerance.
  The likely right shape is a proper online filter (Kalman-flavored: a state = position+velocity with
  a precision that is the filter's own inverse innovation variance), i.e. Bayesian online changepoint
  detection, not a hand-weighted sum of two cosines. Start there.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT (owner-DONE). SOLVED via the UPDATE/SEGMENTATION framing. Re-verified scaffold-free FIRST-HAND (verify_prediction_error_event_segmentation.py PASS: N400_content downstream recovery 0.988 [0.980,0.995] > every floor's upper-CI -- FORM_NOVELTY 0.762 strongest -- at a matched boundary rate; naive ||Delta register|| ties no-seg 0.202/0.198). The brain's missing UPDATE signal, built: a GRADED forward CONTENT prediction error against the RUNNING (reset-per-event) situation-model state, boundary-posted via the EST relative_threshold_gate. Deep + honest: the win is POSITION not rate; the two prior negatives died measuring FORM novelty against a never-resetting anchor (the RUNNING RESET is the N400); the residual must be graded AND in a CONTENT-similar space (the p1 sign_quantiser coupling made concrete); foundationality drill shows the win doesn't hinge on the predictor; honest sub-negatives (precision estimator hurts; the LEARNING framing is a rigorous negative). 4 AUDIT UPDATEs folded (F5 N400 monitor MISSING->spec'd+existence-proven; E2 confirmed+actionable; deviation #6 SPLIT UPDATE=build/LEARNING=deprioritise; Tier 5 predictive_coding confirmed). Review + SOLVER REVIEW block in PROBLEM.md; priority cleared. The N400 organ (graded content-PE + EST boundary + wire situation_model_accumulate) is a PROVEN-READY hdlab landing, queued as a focused build with its own witness (alongside the cortical-read organ) -- NO hdlab landing yet (synthetic construction proof; measure on the live reader first). Committed (no push).
