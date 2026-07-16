# Research: integration biology, route-boundary calibration, and a 5-form combination-rule menu for the memory-assimilation arena's gate module

Director drill, 2026-07-16. Synthesis over 3 parallel Sonnet lit-scans (route-boundary calibration mechanisms;
neuromodulatory-gain arithmetic; Bayesian cue-combination + race-model formalisms) plus full integration of two
same-day prior notes (`research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`,
`research_consolidation_gate_quantitative_signals_2026-07-16.md`) and the route-boundary lit-scan's own filed note
(`research_threshold_calibration_gate_boundary_2026-07-16.md`). This is the pre-load deliverable for the
multi-source memory-assimilation arena's gate module (`research_multisource_memory_assimilation_arena_2026-07-16.md`):
concrete, swappable combination-rule forms to race once that arena is built. No code, no cell. Generic
math/neuroscience terms only in all external queries.

## HEADLINE

Three independent lit-scans today (this drill) plus three from earlier today (the signal-mechanism and
quantitative-signals notes) converge on the SAME two-part answer. **(1) There is no published equation for how
the brain's confluence node combines novelty + salience + goal information** — Lisman & Grace 2005 itself states
this qualitatively ("contributes along with...") and gives only a downstream ~200ms temporal-coincidence AND-gate
(hippocampal LTP requires Schaffer-collateral input AND VTA dopamine-terminal stimulation within a narrow window),
not an equation for the upstream convergence. **(2) Wherever the broader neuromodulation literature DOES commit to
an explicit equation, it is overwhelmingly MULTIPLICATIVE GAIN** (Cohen/Servan-Schreiber sigmoid gain parameter,
Aston-Jones/Cohen LC-NE adaptive gain, Doya's NE-as-softmax-inverse-temperature and ACh-as-learning-rate scalar,
Yu & Dayan's Kalman-gain framing of ACh/NE precision) — no paper models neuromodulatory gating as a pure additive
bias. But this multiplicative-gain evidence operates WITHIN one system (scaling a response function or a
learning-rate); at the SYSTEMS level (hippocampus-fast vs. cortex-slow), the best-supported architecture is a
discrete BRANCH/ROUTE (CLS anatomical separation, Tse's near-step 3h-fail/48h-pass transition, Varga et al. 2025's
episodic-vs-schematic dissociation into separate neural systems), not a blended scalar. The route BOUNDARY itself
is empirically ADAPTIVE (schema-richness-gated, per Tse) but via mechanisms (SDT/DDM leaky-recency criterion
update, STN/pre-SMA conflict-triggered threshold-raise) that the literature never connects to a formal
reward-rate/cost-of-error optimization for consolidation specifically — that connection is the single largest
actionable, genuinely-novel-synthesis opportunity this drill identifies. Below: the biology (Part 1), the
calibration mechanism (Part 2), and a 5-form menu (Part 3) built directly from both, ready to race.

## Part 1 — Biology of integration: what combines with what, and how

**The confluence node (Lisman & Grace 2005, *Neuron* 46:703-713).** No explicit arithmetic is stated for how
novelty, salience, and goal/reward information combine upstream of VTA dopamine firing — the paper's own language
is qualitative convergent-afferent summation ("novelty... contributes along with salience and goal information").
The one quantitative claim in the paper is a **temporal coincidence rule downstream**: hippocampal Schaffer-collateral
stimulation paired with VTA-dopamine-terminal stimulation within a ~200ms window triggers LTP. This is an AND-gate
in TIME (both inputs must co-occur in a narrow window), not an arithmetic combination rule for the three upstream
signals. Later reviews that describe VTA as "combining" novelty+salience+goal are extending/interpreting the
paper, not quoting a stated equation — confirmed absence, now cross-checked a THIRD time today (two earlier
same-day lit-scans plus this one), independently.

**Neuromodulatory gating: multiplicative gain dominates wherever an equation exists.**
- Cohen, Servan-Schreiber & McClelland's catecholamine-gain theory (Servan-Schreiber, Printz & Cohen 1990, *Science*
  249:892-895; Cohen & Servan-Schreiber 1992, *Psychol Bull*): activation = sigmoid(**gain**·net_input − bias) —
  gain is an explicit multiplicative scalar on net input, pre-nonlinearity, distinct from the additive bias term in
  the same equation. Both terms exist in the model, but only gain is attributed to catecholamine action; bias is a
  separate free parameter.
- Aston-Jones & Cohen (2005, *Annu Rev Neurosci* 28:403-450) extend the same multiplicative-gain formalism to
  tonic/phasic LC-NE firing modes (utility-driven exploit/explore gain). Underlying single-unit electrophysiology
  (Waterhouse & Woodward) is described qualitatively as signal-to-noise enhancement — the multiplicative-gain
  reading is the standard modeling gloss on that data, not itself a fitted equation from the original recordings
  (flagged as a real but secondary-level interpretive step).
- Yu & Dayan (2005, *Neuron* 46:681-692): ACh = expected uncertainty, NE = unexpected uncertainty, both framed via
  a Kalman-filter analogy — uncertainty **multiplicatively scales the learning-rate gain** on prediction-error-driven
  updates (learning rate proportional to uncertainty, i.e. a Kalman gain). NE's unexpected-uncertainty role
  additionally carries a discrete model-switching/reset function (approximating a change in generative-model
  regime) — not purely a scalar, a branching element embedded inside an otherwise-multiplicative framework.
- Doya (2002, *Neural Networks* 15:495-506): dopamine = the additive TD-error correction ITSELF (`V <- V + alpha*delta`,
  additive-in-effect as a value-update correction term); noradrenaline = softmax inverse-temperature (`beta*Q(a)`,
  literal multiplicative gain on action-value); acetylcholine = learning-rate scalar (`alpha*delta`, multiplicative
  on the update); serotonin = discount-factor parameter (multiplicative-in-effect on future-value weighting).
- **Net picture: dopamine's OWN computational role (as a prediction-error signal) is additive** (a correction term
  summed into a value estimate); **but wherever dopamine, NE, or ACh act as GATES/modulators on OTHER processes
  (plasticity, gain, learning rate), the literature models that gating as multiplicative.** No source in this scan
  models gating itself as a pure additive bias.

**Synaptic tagging and capture (STC) as a concrete AND-gate.** Frey & Morris 1997 (*Nature* 385:533-536); Redondo &
Morris 2011 (*Nat Rev Neurosci* 12:17-30): potentiation-induction sets a short-lived, protein-synthesis-independent
local "tag"; durable change requires a SEPARATE, independently-triggered capture event (plasticity-related proteins
supplied by strong tetanization elsewhere, or by a salience/arousal signal). At the single-synapse level this is a
strict conjunctive (AND) gate — durable change occurs only if BOTH tag-present AND capture-available co-occur;
absent either, the tag decays back to baseline (a hard zero, not a partial credit). **Reconciling binary-AND with
graded recurrence:** the population/behavioral-level readout of repeated exposure (ACT-R's log-sum power law,
conjugate-Bayesian precision accumulation, per the earlier same-day quantitative-signals note) is GRADED — but this
is not in tension with a binary microscopic mechanism: a graded curve is exactly what emerges from averaging many
discrete binary tag-capture events across synapses/trials. Binary-AND at the mechanism level and graded-monotonic
at the population/behavioral level are the SAME underlying process viewed at different scales, not competing
accounts — an important reconciliation this drill adds beyond the earlier notes' separate treatment of "is
recurrence graded or floored."

**Verdict on additive vs. multiplicative vs. branching at the integration node, honestly stated.** No primary paper
gives an explicit equation for the specific 3-signal upstream confluence (novelty+salience+goal at VTA) — that is a
confirmed, triply-cross-checked literature gap, not a search failure. Where explicit arithmetic exists in the
neighboring literature, it favors: multiplicative gain for WITHIN-system neuromodulatory scaling (Cohen/Servan-
Schreiber, Aston-Jones/Cohen, Yu-Dayan, Doya-NE/ACh); additive correction for dopamine's OWN prediction-error role
specifically; strict conjunctive AND for STC's tag/capture mechanism (graded only in population-level aggregate);
and discrete branching/routing for the SYSTEMS-level hippocampus-vs-cortex architecture (CLS, Tse, Varga et al.
2025). All four forms are real, evidenced, and operating at different levels of the same overall system — the
brain is not "one arithmetic operation," it is a stack of different operations at different scales, which is
itself the single most important qualitative finding for menu design below (Part 3): a menu that tries to pick ONE
arithmetic form to cover ALL of this is picking the wrong scale to unify at.

## Part 2 — Route-boundary calibration (full detail in `research_threshold_calibration_gate_boundary_2026-07-16.md`, summarized here)

The fast/slow route boundary is **ADAPTIVE, but via at least three mechanistically distinct knobs that the
literature never unifies**:

1. **SDT/DDM criterion-and-boundary adaptation** — trial-history- and reward-rate-adaptive (Norton, Fleming, Daw &
   Landy 2017, *PLoS Comput Biol* 13:e1005304), but demonstrably SUBOPTIMAL/leaky (recency-weighted, not the
   Bayes-exact static optimum) — this is itself informative: the brain-faithful target is a leaky/EWMA tracker,
   not an exact Bayes update.
2. **Conflict-triggered threshold-raise** — a causally distinct, subcortical mechanism (STN hyperdirect pathway,
   pre-SMA; Frank et al., *Nat Neurosci* 2011) raises the DDM boundary specifically under response CONFLICT,
   independent of reward-rate/base-rate. Maps naturally onto "surprise high AND recurrence borderline -> hold for
   provenance review" as a first-principles-justified branch, not an ad hoc rule.
3. **BCM sliding LTP/LTD threshold** — real, homeostatic (Abraham et al. 2001, *PNAS* 98:10924-10929), but
   evidenced at the single-synapse plasticity-DIRECTION level, not the route-selection level — flagged explicitly
   as a probably-WRONG donor mechanism for a route threshold (structural mismatch, not just untested).
4. **The consolidation-route boundary itself** (Tse et al. 2007/2011) is empirically schema-gated, not fixed — but
   **no paper derives this transition rate from a formal Neyman-Pearson/Bayes-cost optimization** (tau* =
   C_FP/(C_FP+C_FN)), the exact normative apparatus Bogacz et al. (2006, *Psychol Rev* 113:700-765) proved optimal
   for DDM boundaries in perceptual 2AFC tasks. This connection — applying Bogacz-style normative threshold theory
   to memory-consolidation routing — appears never to have been made in either literature. That is the single
   largest actionable, explicitly novel-synthesis opportunity (capped P<=0.50 per discipline, stated in the source
   note).

**In-principle calibration recipe** (synthesizing findings 1+2+4): a route threshold should be set by (a) a
theory-fixed FORM — the Neyman-Pearson/Bayes-risk cutoff tau* = C_FP/(C_FP+C_FN), where C_FP/C_FN are
pre-registered cost constants — with (b) the base-rate term estimated ONLINE via a leaky/EWMA tracker (matching
the brain's demonstrated-suboptimal-but-real adaptivity, finding 1), and (c) a distinct, additive threshold-RAISE
triggered by measured decision conflict (finding 2; operationalizable on this substrate as the margin between the
top-1 and top-2 candidate scores — narrow margin = high conflict = raise the threshold before committing).

## Part 3 — Formal menu: 5 concrete, swappable combination-rule forms

Each form below is stated as a functional form over the 3 signals (`surprise`, `schema_fit`, `recurrence`),
how its parameters are set, and its discriminating prediction against the others.

### Form 1 — BRANCH/ROUTE with calibrated thresholds (reliability-gate + salience bypass -> fast/slow on schema-fit)

- **Form:** cascade, not a single scalar. `recurrence -> local_precision` (STC-style graded accumulation, Part 1)
  gates a HOLD/PROVISIONAL branch below `PRECISION_MIN` (bypassable by a one-shot high-salience event, per the
  amygdala/arousal STC bypass); items clearing that gate route on `schema_fit` vs. an adaptive threshold `tau`;
  `surprise` (schema-conditioned, per the same-day signal-mechanism note's A1 fix) sets a separate SKIP floor for
  low-magnitude deviations regardless of route.
- **Weight-setting:** form is theory-fixed (branch structure), threshold VALUE is data-adaptive: `tau` from
  Neyman-Pearson tau*=C_FP/(C_FP+C_FN) (pre-registered cost constants) with the base-rate term tracked online via
  leaky EWMA (Part 2 recipe); conflict-triggered raise adds a measured margin term (top1-vs-top2 candidate-score
  gap) with no free weight beyond the raise magnitude.
- **Discriminating prediction:** produces a bimodal/near-step distribution of route decisions as `schema_fit`
  crosses `tau` (matching Tse's sharp 3h-fail/48h-pass transition) — testable via decision-entropy near the
  boundary (should be LOW once calibrated, vs. today's uncalibrated ~0.53-0.57 routing accuracy, which is closer
  to maximum-entropy/coin-flip).
- **Brain-faithful:** YES — the best-supported form overall (CLS anatomical separation + Tse near-step function +
  Varga et al. 2025 dissociation + STN/SDT adaptive-threshold literature all converge here); the threshold VALUE is
  engineering-calibrated since biology hands no transferable constants (Part 2, finding 4's gap).

### Form 2 — PRECISION-WEIGHTED BAYESIAN FUSION (Ernst-Banks inverse-variance / log-likelihood summation)

- **Form:** `combined = sum_i(w_i * x_i)`, `w_i = precision_i / sum_j(precision_j)`, precisions additive
  (`tau_combined = sum_i(tau_i)`) — each signal expressed as a mean+variance estimate, not a point score;
  `recurrence` directly supplies precision via conjugate-Bayesian accumulation (more corroboration = higher tau).
  Exact form and N-cue generalization confirmed today via Ernst & Banks 2002 (*Nature* 415:429-433, primary) and
  Alais & Burr 2004 (*Curr Biol* 14:257-262, primary replication in a different modality pair).
- **Weight-setting:** theory-derived, not hand-tuned — weights fall out of each signal's estimated noise/precision;
  the only free choice is HOW variance is estimated per signal (e.g., recurrence-count-derived precision, per A3).
- **Discriminating prediction:** predicts a SMOOTH, continuous consolidation-strength gradient as compound
  reliability varies (opposite of Form 1's bimodal prediction) — directly falsifiable against Form 1 by the same
  parametric sweep. Also predicts EXCHANGEABILITY: two signals with equal measured precision should be weighted
  identically regardless of WHICH signal they are (schema_fit-precision and recurrence-precision interchangeable)
  — Form 1 explicitly does NOT predict this (schema_fit and recurrence play structurally different, non-exchangeable
  roles there).
- **Brain-faithful:** PARTIAL. Ernst-Banks fusion is itself real, well-evidenced multisensory-integration biology —
  but it fuses multiple noisy estimates of the SAME latent quantity (e.g., two size estimates). Our 3 signals are
  different IN KIND (a magnitude-of-deviation, a structural-fit, and a temporal-reliability quantity), not multiple
  noisy readings of one quantity — this is a genuine disanalogy the CLS anatomical-separation literature argues
  against (Part 1's "not one blended computation" verdict). Best treated as the strongest ENGINEERING baseline,
  not the most brain-faithful candidate.

### Form 3 — ADDITIVE with learned weights (logistic regression)

- **Form:** `P(consolidate) = sigmoid(w1*surprise + w2*schema_fit + w3*recurrence + b)`, weights fit by MLE/logistic
  regression from labeled outcome data. This is literally the already-run `learned` arm in
  `exp_ingest_gate_combination_rule_race_v1` (DECONF_AUC=0.628).
- **Weight-setting:** purely data-learned; can optionally be initialized/regularized from Form 2's precision-derived
  weights as a prior, but requires no theoretical commitment.
- **Discriminating prediction:** the cue-combination literature (today's lit-scan #3) confirms this is a legitimate
  REDUCTION of Bayesian fusion only under conditionally-independent, Gaussian-noise cues — it diverges specifically
  when a signal's reliability itself varies trial-to-trial in a way not captured as a plain regressor (causal-
  inference/cue-conflict structure). Discriminating test: add recurrence as a multiplicative INTERACTION term
  (recurrence x schema_fit, recurrence x surprise) rather than only a main effect — if interaction terms materially
  improve fit, the arena has causal-inference-like structure this flat-additive form is structurally blind to;
  if not, the flat additive form is adequate and simplest.
- **Brain-faithful:** LOW — no neuroscience literature proposes a flat single-neuron-level weighted sum across
  novelty+schema+recurrence; useful strictly as the atheoretical, already-tested engineering ceiling-check.

### Form 4 — MULTIPLICATIVE/GATED (AND-threshold; Friston fixed-weight decomposition)

- **Form:** `fast_track = raw_PE * schema_fit`; `slow_track = raw_PE * (1 - schema_fit)`; consolidate iff
  `max(fast_track, slow_track) > floor`. Literally the already-run `brain` arm in
  `exp_ingest_gate_combination_rule_race_v1` — empirically AT CHANCE (DECONF_AUC=0.530) with the current
  (schema-blind, global-rank) `raw_PE` input.
- **Weight-setting:** theory-fixed, zero free weights beyond the floor — the entire point of Friston's
  precision-weighting form is that `schema_fit` itself IS the mixing weight.
- **Discriminating prediction:** should show a genuine boost over `schema_fit`-alone SPECIFICALLY for candidates
  with high surprise AND high schema-fit (the exact case schema_fit alone cannot distinguish "boring known
  instance" from "meaningful deviation within a known template") — this incremental-lift-on-a-specific-subpopulation
  test is the clean discriminator, distinct from an AUC-averaged-over-everything metric (this is exactly the
  `local_surprise` 6th-arm test already proposed and pre-registered in
  `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`).
- **Brain-faithful:** HIGH IN FORM (multiplicative gain is the dominant arithmetic wherever the neuromodulation
  literature commits to an equation at all — Part 1's convergent finding) — but the CURRENT instantiation failed
  for a diagnosed, fixable reason (schema-blind global surprise input, not multiplicative combination per se). Form
  not refuted; input broken.

### Form 5 — TWO-ACCUMULATOR RACE (Usher-McClelland LCA / Brown-Heathcote LBA style) — novel, confirmed literature gap

- **Form:** two independent accumulators race to a decision boundary. Accumulator F integrates schema-CONSISTENT
  evidence (`drift_F = schema_fit + lambda*recurrence`); accumulator S integrates schema-VIOLATING evidence
  (`drift_S = surprise * (1 - schema_fit)`); whichever hits its own threshold first determines FAST-track vs.
  SLOW-track consolidation. Uniquely among all 5 forms, TIME-TO-THRESHOLD is itself a usable output (a
  confidence/urgency signal), not just a binary/route label.
- **Weight-setting:** drift-rate combination weights (`lambda`) can be theory-motivated or fit; boundary separation
  set via the SAME Bogacz reward-rate-optimal normative form used for Form 1's `tau` (reframed as accumulator
  height), or adapted via the STN/conflict mechanism (Part 2, finding 2) raising both boundaries under measured
  conflict.
- **Discriminating prediction:** uniquely predicts a REACTION-TIME-like variable — candidates near the
  schema_fit/surprise decision boundary should show characteristically slower time-to-decision than clear-cut
  cases, consistent with Tse's transition being sharp ON AVERAGE but with individual-item latency/uncertainty
  variance that no other form on this list has any mechanism to represent (Forms 1-4 are all single-shot scalar
  decisions with no intrinsic time axis).
- **Brain-faithful:** genuinely UNTESTED/NOVEL for this specific application — confirmed as a literature gap today
  (extensive searches combining "race model"/"accumulator model" with "memory consolidation"/"schema congruency"
  surfaced only single-gate/dual-pathway-WEIGHTING framings, never a literal race-to-threshold formalization) — but
  architecturally the most naturally brain-faithful of the 5, since accumulator-race dynamics are the best-evidenced
  general decision mechanism in neuroscience broadly, simply never wired to this specific problem. Highest novelty,
  highest payoff if right, least de-risked.

## Part 4 — Which form best matches the evidence, and the cleanest default

**Best match to the brain's branch/route evidence: Form 1.** The convergent literature (CLS anatomical separation,
Tse's near-step transition, Varga et al. 2025's episodic-vs-schematic dissociation into separate neural systems,
STN/SDT adaptive-threshold causal-manipulation studies) is the most consistent, most causally-supported, and least
contested body of evidence surfaced across all 6 lit-scans run today (3 earlier, 3 this drill). Form 2 (Bayesian
fusion) is the strongest ENGINEERING alternative but carries a specific disanalogy (fuses same-type cues; ours
differ in kind). Form 4 (multiplicative gate) has the strongest per-equation biological precedent (Part 1's
gain-dominant finding) but has already been empirically tested on this substrate and failed for a diagnosed,
separate reason (input, not form). Form 3 is the honest atheoretical baseline. Form 5 is the highest-upside,
zero-precedent stretch candidate.

**Cleanest default to try first: Form 1, calibrated per Part 2's recipe.** It reuses the already-built
`_four_batch_routing` cascade in `experiments/exp_ingest_gate_combination_rule_race_v1.py` with zero new
machinery — the diagnosed problem (routing_accuracy ~0.53-0.57, barely above the 0.50 random-routing floor) is a
threshold-CALIBRATION problem, not an architecture problem, per both this drill and the earlier signal-mechanism
note's independent conclusion. It also has the most convergent, least-contested supporting literature of any of
the 5 forms.

## Cheap decisive test

Extend the already-proposed 6th arm (`local_surprise`, schema-conditioned prediction error, zero new acquisition,
per `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`) with TWO more arms in the SAME
race, on the SAME already-fitted `additive_map`/reachability-audit pilot batches, still zero new acquisition:

- **Arm 7 — `calibrated_branch` (Form 1):** the existing `_four_batch_routing` cascade, but with `SURPRISE_MIN`
  replaced by an online leaky-EWMA tracker toward the Neyman-Pearson tau* implied by the current observed
  redundant-vs-novel ratio in the last W cycles (Part 2's recipe), plus a conflict-triggered threshold-raise term
  (top1-vs-top2 candidate-score margin).
- **Arm 8 — `race_toy` (Form 5), pure simulation only, no substrate cell:** a minimal two-accumulator race over the
  SAME batch-1/2/3 candidate scores already computed for the other arms (drift_F, drift_S as specified in Form 5),
  checked only for whether time-to-threshold correlates with batch difficulty (batch 2 harder/more-ambiguous
  candidates should show longer simulated time-to-threshold than batch 1/3's clear-cut cases) — this is a
  spreadsheet-level check, not a dispatched cell, and gates whether Form 5 is worth building for real.

- **HARD-PASS (Form 1 confirmed as best-in-class):** Arm 7's routing_accuracy clears >=0.70 on the 4-batch routing
  task (vs. today's 0.53-0.57) AND its decision-entropy near the calibrated `tau` boundary is measurably lower than
  under the fixed-threshold baseline (confirms genuine calibration, not just a lucky threshold pick).
- **HARD-FAIL (Form 1's calibration mechanism doesn't help on this substrate):** Arm 7 shows <5% relative
  improvement over the fixed-threshold baseline — meaning either the base-rate-tracking recipe doesn't transfer to
  this substrate's candidate-score distributions, or (per Part 2 finding 1's honest caveat) the leaky/EWMA
  approximation itself needs a different decay constant than assumed; route to a threshold-decay-constant sweep
  before abandoning Form 1.
- **Arm 8 gating rule:** if `race_toy`'s time-to-threshold does NOT correlate with batch difficulty (r<0.2) even in
  this cheap toy form, do NOT build Form 5 as a real cell — the novel-synthesis risk (confirmed literature gap,
  zero precedent) is not worth the implementation cost without even a toy-level positive signal.
- **MIDDLE band:** Arm 7 improves 5-20% relative — real signal, needs a second calibration pass (cost-ratio
  constants or EWMA decay) before either full adoption or abandonment.

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

1. **Route (Form 1) vs. Fusion (Form 2) are discriminable by decision-distribution shape**, not just accuracy: a
   parametric sweep of schema_fit/surprise/recurrence should show a bimodal/step-like routing-decision distribution
   if Form 1 is correct, vs. a smooth unimodal gradient if Form 2 is correct. HARD-FAIL for Form 1: if the swept
   distribution is smooth/unimodal despite calibrated thresholds, Form 2's fusion framing is more accurate than the
   route framing on this substrate, regardless of what the biology literature favors architecturally.
2. **Form 4's multiplicative form is separable from its (broken) input**, per the already-registered `local_surprise`
   test in the signal-mechanism note: if `local_surprise`-alone clears chance (>=0.65) AND the recomputed
   multiplicative combination with the corrected input reaches within TIE_EPS of `schemafit_alone` (0.836), Form 4
   is REDEEMED as a viable candidate distinct from Form 1; if `local_surprise` stays at chance even localized, Form
   4 is settled as inferior to Form 1 on this substrate specifically (not a general refutation of multiplicative
   gating biology).
3. **Form 5 is gated on a cheap toy correlation check** (Arm 8 above) before any real implementation — HARD-FAIL
   localization: if time-to-threshold shows no relationship to independently-known batch difficulty even in
   simulation, the race-model novelty is not paying for itself on this substrate, and the next-drill candidate
   (STN/pre-SMA "decision-conflict-as-ranking-margin," already flagged in the route-boundary note) should be tested
   as a simpler enhancement to Form 1 instead of building the full race architecture.

## Cross-thread synthesis

- Directly consumes and extends all three same-day prior notes without re-deriving them:
  `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md` (non-redundancy argument + the
  already-registered `local_surprise` 6th arm, reused verbatim as Form 4's discriminating test);
  `research_consolidation_gate_quantitative_signals_2026-07-16.md` (the quantitative per-signal forms — saturating
  Hill for DA/surprise, Tse's 3h/48h window for schema-fit, ACT-R log-sum for recurrence — used as the numeric
  backbone for Forms 1-5's parameter definitions); `research_threshold_calibration_gate_boundary_2026-07-16.md`
  (the route-boundary calibration mechanism, used directly as Form 1's weight-setting recipe).
- Directly supplies the missing piece flagged by `research_multisource_memory_assimilation_arena_2026-07-16.md`
  (the arena design note): that note explicitly deferred "the eventual gate mechanism design" as out of scope;
  this note is that deferred design, ready to plug into the arena once built — the 5 forms above should be raced
  inside the multi-source arena (not the current single-static-KG test), since that arena note's own finding is
  that a single graph cannot distinguish schema-fit from recurrence from surprise in the first place, which would
  make any of Forms 1-5 look artificially collapsed if raced prematurely on the old arena.
- Confirms, for a FOURTH independent time across today's 6 total lit-scans, that no published study states a joint
  combination law for these 3 (or Lisman-Grace's original 3: novelty/salience/goal) signals — this is now as
  close to a settled fact about the literature's current state as a lit-scan discipline permits.
- The Part 1 "stack of different operations at different scales" finding (multiplicative-within-system,
  conjunctive-at-STC, branching-at-systems-level) is a genuinely new synthesis point beyond the earlier notes —
  it explains WHY earlier attempts to find "the one combination rule" kept coming up empty: the brain is not
  running one arithmetic operation, it is running different ones at different levels, and Forms 1-5 above are
  best read as candidates for the SYSTEMS-level (routing) decision specifically, informed by but not identical to
  the within-system multiplicative-gain mechanisms.

## Substrate-product implications

1. Race Forms 1, 3, and 4 (all buildable with zero new acquisition, reusing the already-fitted pilot) as the
   near-term 3-arm race, per the cheap decisive test above — this is a direct, immediately actionable extension of
   the already-running `exp_ingest_gate_combination_rule_race_v1` design, adding 2 arms (calibrated-branch,
   corrected-local-surprise-multiplicative) to the existing 5.
2. Hold Form 2 (Bayesian fusion) as a documented, precedent-backed alternative but NOT a near-term build priority —
   the CLS anatomical-separation disanalogy (fusing different-KIND signals, not multiple noisy readings of one
   quantity) is a real, literature-grounded reason to expect it underperforms Form 1 specifically for this
   cross-signal-type problem, though it remains the correct form if the arena ever needs to fuse multiple
   same-kind redundant estimates of a single quantity (e.g., multiple independent recurrence estimators).
3. Gate Form 5 (race model) behind the cheap Arm 8 toy-simulation check before spending any real implementation
   effort — it is the single highest-payoff-if-right candidate (matches the general neuroscience decision-mechanism
   literature better than any static-scalar form, and uniquely supplies a confidence/urgency readout) but also the
   only one with zero direct precedent for this specific application; the toy gate keeps this option open without
   pre-committing engineering time.
4. The Part 2 route-boundary calibration recipe (Neyman-Pearson tau* + leaky-EWMA base-rate tracking + STN-style
   conflict-triggered raise) is directly reusable as Form 1's weight-setting mechanism AND, per the route-boundary
   note's own next-drill flag, connects to a not-yet-drilled angle (`decision-conflict-as-ranking-margin`, using
   the top1-vs-top2 candidate-score gap as a cheap conflict proxy) that this note operationalizes concretely for
   the first time as part of Form 1 and Form 5's boundary-raise mechanism.
5. Before racing any of these 5 forms for real, per the arena note's own precondition: verify the arena achieves
   pairwise |r|<0.3 among the 3 raw signals first — racing combination FORMS on a still-collapsed arena would
   produce uninterpretable results regardless of which form is correct.

## Citations (verified count: 19 distinct sources across 3 lit-scans this drill; cross-referenced against 21+20+17
sources in the 3 same-day prior notes, several independently corroborating across scans)

**Neuromodulatory gain arithmetic:** Servan-Schreiber, Printz & Cohen 1990, *Science* 249:892-895 (primary, exact
equation); Cohen & Servan-Schreiber 1992/1993, *Schizophrenia Bulletin* 19:85-104, PMID 8095737 (primary); Aston-Jones
& Cohen 2005, *Annu Rev Neurosci* 28:403-450 (primary/theoretical); Waterhouse & Woodward 1980 and related NE
electrophysiology (primary, qualitative SNR framing); Yu & Dayan 2005, *Neuron* 46:681-692 (primary, Kalman-gain
framing); Dayan & Yu companion theoretical papers (secondary/theoretical); Doya 2002, *Neural Networks* 15:495-506
(primary/theoretical); Lisman & Grace 2005, *Neuron* 46:703-713, PMID 15924857 (primary, confirmed no upstream
combination arithmetic).

**Route-boundary calibration** (full citation list in `research_threshold_calibration_gate_boundary_2026-07-16.md`,
17 sources): Norton, Fleming, Daw & Landy 2017, *PLoS Comput Biol* 13:e1005304 (primary); Bogacz, Brown, Moehlis,
Holmes & Cohen 2006, *Psychol Rev* 113:700-765 (primary, normative form); Frank et al. 2011, *Nat Neurosci*,
PMC3394226 (primary, STN/conflict); Bienenstock, Cooper & Munro 1982, *J Neurosci* 2:32-48 (primary theory); Abraham
et al. 2001, *PNAS* 98:10924-10929 (primary); Tse et al. 2007/2011, *Science* 316:76-82 / 333:891-895 (primary).

**Bayesian cue-combination and race models:** Ernst & Banks 2002, *Nature* 415:429-433 (primary, exact equation);
Alais & Burr 2004, *Curr Biol* 14:257-262 (primary replication); Knill & Pouget 2004, *Trends Neurosci* 27:712-719
(secondary review); Usher & McClelland 2001, *Psychol Rev* 108:550-592 (primary, LCA); Brown & Heathcote 2008,
*Cogn Psychol* 57:153-178 (primary, LBA, closed-form); "A Neural Model of Schemas and Memory Consolidation," bioRxiv
(searched, confirms gap — no race-model formalization of consolidation found).

**Substrate-internal (cited for cross-thread accuracy, not external lit):**
`data/exp_ingest_gate_combination_rule_race_v1/metrics.json`;
`experiments/exp_ingest_gate_combination_rule_race_v1.py`;
`notes/research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`;
`notes/research_consolidation_gate_quantitative_signals_2026-07-16.md`;
`notes/research_threshold_calibration_gate_boundary_2026-07-16.md`;
`notes/research_multisource_memory_assimilation_arena_2026-07-16.md`.

## Deflated confidence (lit-scan calibration: deflate 0.15-0.25; novel-synthesis capped at 0.50)

- **P(no explicit combination arithmetic exists at the Lisman-Grace confluence node, and multiplicative gain
  dominates wherever the broader neuromodulation literature does commit to an equation)** = **0.60** (undeflated
  ~0.80 — this is a highly convergent finding across independent primary sources; deflated for the compound claim
  covering both the negative-existence part and the multiplicative-dominance part together).
- **P(the systems-level architecture is branch/route rather than blend/sum, Form 1 over Form 2)** = **0.50** (capped
  — well-supported by CLS/Tse/Varga et al. 2025, but the discriminating parametric sweep (bimodal vs. smooth
  distribution) has never been run in either the biology literature or on this substrate; this is director synthesis
  extending real evidence to a not-yet-tested substrate claim).
- **P(the 5-form menu as constructed — including the STC binary/graded reconciliation and the "stack of scales"
  synthesis — correctly represents the state of the art, i.e. no 6th load-bearing form was missed)** = **0.45**
  (novel synthesis capped at 0.50; reasonable confidence given convergence across 6 total lit-scans today, but
  genuinely a director-constructed menu, not itself published anywhere as a 5-item list).
- **P(the cheap decisive test's Arm 7 — calibrated_branch — HARD-PASSes at >=0.70 routing_accuracy)** = **0.35**
  (undeflated ~0.50; genuinely uncertain — the SDT literature's own finding that biological adaptation is
  suboptimal/leaky, not exactly Bayes-optimal, suggests a MIDDLE-band outcome is more likely than a clean
  HARD-PASS, consistent with the route-boundary note's own P=0.40 estimate for its narrower version of this test).
- **P(Arm 8's race-model toy check shows a positive time-to-threshold/difficulty correlation, gating Form 5 open)**
  = **0.40** (genuinely novel, zero precedent either way in the literature or on this substrate; this is exactly why
  it's gated behind a cheap toy check rather than assumed).

## Next-drill candidate

If Arm 7 (calibrated_branch) lands in MIDDLE band (5-20% improvement, not a clean HARD-PASS): the next drill is the
STN/pre-SMA "decision-conflict-as-ranking-margin" angle already flagged in
`research_threshold_calibration_gate_boundary_2026-07-16.md` — specifically, whether the top1-vs-top2 candidate-score
margin (a cheap, already-computable quantity from `additive_map.score_all`) is a valid conflict proxy for
threshold-raising, tested as an isolated addition to Form 1 before considering Form 5's full race-model build. This
is an unexplored, concretely-scoped angle (`network-science-graph-theory`-adjacent per the field advisor's Tier-1
listing) with a direct, cheap implementation path already identified.
