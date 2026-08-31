---
problem: the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision
status: SOLVED
bar: "PASS = BOTH gates. (1) INFORMATIVE: live per-argument surprisal predicts the reader's OWN comprehension errors (who-did-what wrong) CI-separated over chance (AUC/point-biserial lower bound > 0.5), and a SHUFFLED-surprisal twin (same values permuted across arguments) LOSES CI-separated. (2) ACTIONABLE: gating ONE brain-faithful decision by the signal -- surprisal-abstain (hold the highest-surprisal answers) OR surprisal-weighted predict-and-revise -- beats the un-gated reader on a downstream comprehension metric CI-separated, with the info-free (random same-rate) twin NOT helping. Report CI half-width + null p95 beside every margin; precision-weight as the graded brain signature. A rigorous NEGATIVE is a full PASS: if the live signal is too weak to drive a decision (informative but not actionable, or ceiling'd), enumerate WHY."
result: "INFORMATIVE PASS: live per-argument surprisal (hdlab.predictive_reader driven on the reader's OWN patient bindings through SituationReader.read, role-capable) predicts the reader's own who-did-what errors AUC 0.651 [0.630,0.672] (ROC-AUC; n=2606 QA-SRL v2 dev+test patient items, MODERN text; CI half-width 0.021), shuffle-surprisal twin AUC p95 0.519 (loses). ACTIONABLE PASS via surprisal-abstain: committed accuracy at 80% coverage 0.633 vs random-abstain twin 0.598 -> margin +0.035 [+0.022,+0.050] CI-sep (half-width 0.014). Generalizes to 19c LitBank narrative: AUC 0.624 [0.556,0.690] (n=311, 14 docs), twin p95 0.562."
floor: "un-gated reader base accuracy 0.599 (no surprisal signal); random same-rate abstention twin committed acc 0.598 (flat); shuffled-surprisal AUC null p95 0.519 (chance 0.5). The live signal clears all three CI-separated."
controls: "(1) shuffled-surprisal twin R=500 (values permuted across arguments) -> AUC null p95 0.519 = EXCLUDES 'any per-argument number ranks errors'. (2) random same-rate abstention twin -> committed acc 0.598 flat = EXCLUDES 'any withholding at this rate helps'. (3) info-free random-adopt reanalysis twin p95 -0.005 = EXCLUDES 'any reanalysis helps'. (4) NON-CANONICAL stratum n=603 (passive/fronted) gives reanalysis its strongest shot -> +0.003 [-0.010,+0.016] = EXCLUDES 'the re-selection wall is a canonical-case artifact'. (5) LitBank 19c slice = EXCLUDES 'modern-vocabulary artifact'. (6) precision terciles (top 0.684 vs bottom 0.628) = EXCLUDES 'diagnosticity is precision-flat'."
files_changed: "experiments/_forward_prediction_live.py; experiments/exp_forward_prediction_live_decision_v1.py; experiments/exp_forward_prediction_reselector_probe_v1.py (the exemplar re-selector prototype); experiments/exp_forward_prediction_richer_space_probe_v1.py (wider-feature dimensionality-vs-structure + taxonomic-metric probe); experiments/exp_forward_prediction_agent_conditioned_reselector_v1.py (owner-directed build B); experiments/exp_forward_prediction_agent_conditioned_surprisal_v1.py (build C, agent-conditioned flag) + data/forward_prediction_agent_conditioned_surprisal_v1/metrics.json; experiments/exp_forward_prediction_flag_negative_diagnosis_v1.py (WHY the flag negative) + data/forward_prediction_flag_negative_diagnosis_v1/metrics.json; experiments/exp_forward_prediction_two_factor_flag_v1.py + experiments/exp_forward_prediction_confusability_flag_v1.py + experiments/exp_forward_prediction_parse_disagreement_flag_v1.py (the two-factor / confusability / parse-disagreement exploration) + their data/*/metrics.json; notes/problems/.../research_drill_4_candidate_competition_mechanism_2026-08-31.md; verification/test_forward_prediction_live_decision_organ.py; data/forward_prediction_live_decision_v1/metrics.json; data/forward_prediction_reselector_probe_v1/metrics.json; data/forward_prediction_richer_space_probe_v1/metrics.json; data/forward_prediction_agent_conditioned_reselector_v1/metrics.json; notes/problems/.../research_drill_3_thematic_fit_ranking_mechanism_2026-08-31.md; notes/problems/the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision/{SOLVED.md,research_drill_1_surprisal_as_error_signal_2026-08-31.md,research_drill_2_grounded_space_reselection_wall_2026-08-31.md}. hdlab/ UNTOUCHED."
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
  - **DECOMPOSITION (the actionable finding):** the re-selection wall = ~+0.08 ESTIMATOR CLASS (FIXED
    by the exemplar store, CI-sep) + a residual ~0.13 to the parse that is relational STRUCTURE, NOT
    dimensionality. Tested DIRECTLY (`experiments/exp_forward_prediction_richer_space_probe_v1.py`,
    n_common=2316): swapping the 12-d grounded space for a fairly-trained RICHER distributional space
    (Random Indexing over 6M text8 tokens, 40k vocab, 1024-d -- a glass-box substrate organ, offline
    foundation, NO LLM) does NOT help -- it is WORSE than grounded-12d (0.400 vs 0.463, -0.063 CI-sep;
    window co-occurrence captures TOPICAL relatedness "vessel~dock", the wrong signal for thematic-fit
    ranking "vessel~ferry"), and FUSING grounded+distributional only ties grounded (-0.011). No space
    (grounded / distributional / fused) out-selects the reader's parse (all 0.13-0.20 below). **So the
    "just add dimensions" hypothesis is RULED OUT: the residual is verb-specific relational EVENT
    STRUCTURE, not a bigger flat vector.** The follow-on is therefore a STRUCTURED verb-role ->
    rich-filler event store (Chersoni SDM; angular-gyrus GEK; McRae event knowledge; FHRR role-filler
    binding) -- and the shelf has no such asset (VERIFIED BY ENUMERATION: `lexical_similarity` = 89
    hand-authored concepts; `distributional_meaning_channel` = substitutability-scoped, WordSim rho
    -0.24; `ppmi_sparse_encoder` = supervised trigram encoder). This is the Phase-1 meaning-supply lever.

  We do NOT generalize the narrow failure to "impossible": the estimator-class half is now fixed and
  measured; the residual is a named, unbuilt asset (the Phase-1 lever), not a ceiling.

## OWNER-DIRECTED FOLLOW-ON BUILDS (drill 3 -> built + tested; beyond the one-decision bar)
The owner directed building the re-selector components drill 3 named. Two were built as one-variable
can-fail probes on the reader's OWN live items; BOTH are informative NEGATIVES that CONVERGE on one
conclusion.

- **B. Agent-conditioned exemplar retrieval -- NEGATIVE, and diagnostic**
  (`exp_forward_prediction_agent_conditioned_reselector_v1.py`). Condition patient re-selection on the
  AGENT (the partial event; McRae combination; Michaelov 2024 agent-preference; angular-gyrus context
  update), holding estimator=exemplar-top3 and space=grounded FIXED -- the ONLY new variable is whether
  the exemplar pool is agent-gated. Result (gold agent n=988, reader agent n=2058, K in {10,20,40}):
  agent-conditioning does NOT beat the verb-only exemplar (WORSE, -0.065 to -0.095 CI-sep), AND the real
  agent is statistically INDISTINGUISHABLE from a RANDOM-agent twin (delta CI includes 0 at every K,
  both agent sources) -- the agent SIGNAL is null HERE. DIAGNOSIS: agent-conditioning has nothing to
  condition because the patient-similarity METRIC (grounded-12d) cannot rank patients -- the metric is
  UPSTREAM of the conditioning (reorders drill 3's B-first tractability ranking; the substrate says A is
  the binding constraint). CAVEAT: only the hard agent-gated form was built; the random-agent twin (real
  ~ random) is the evidence the signal is null across conditioning forms in this space.
- **A. A better similarity METRIC (taxonomic vs topical) -- NEGATIVE, confirms the axis**
  (`exp_forward_prediction_richer_space_probe_v1.py`). Swap grounded-12d for a distributional space
  (Random Indexing over 6M text8 tokens, 40k vocab, glass-box, NO LLM) in WINDOW (topical) and
  SYMMETRIC-PATTERN ("X and Y" coordination = taxonomic; Schwartz 2015) modes + their fusion with
  grounded. Result (n=2316, pairwise-common subsets): TAXONOMIC beats TOPICAL as predicted (sympattern
  -0.043 vs window -0.058 vs grounded), but NO flat metric beats grounded-12d CI-sep (best fused_
  sympattern ties grounded at -0.003), and none beats the reader's PARSE (all 0.14-0.19 below).
- **THE CONVERGENT CONCLUSION (the deep understanding, EVIDENCED not speculated).** FOUR independent
  attempts to out-select the parse with a plausibility signal -- richer DIMENSIONS (drill-2 probe), a
  better ESTIMATOR (exemplar, +0.08 but caps at 0.46), the right similarity AXIS (taxonomic), and
  AGENT-conditioning -- ALL fail the same way: none beats the reader's parse (~0.59). This is
  MacWhinney's COMPETITION MODEL live: English who-did-what is WORD-ORDER dominant; thematic-fit
  plausibility is a WEAK cue that cannot override structural parsing. So the forward-prediction signal's
  validated value is as a CONFIDENCE / FLAG (the abstain gate, which works), NOT a re-selector. The ONLY
  thing that would cross the wall is the FULL structured event store combining all four ingredients WITH
  the parse's structural/dependency information (SDM proper; Chersoni/Lenci) -- a large Phase-1 build,
  now MOTIVATED BY EVIDENCE (every cheap approximation converged to "it is structure"), not a guess.
- **C. Agent-conditioned SURPRISAL as a sharper FLAG (Michaelov 2024 applied to the part that WORKS) --
  DIRECTIONAL, not CI-sep** (`exp_forward_prediction_agent_conditioned_surprisal_v1.py`). Does
  conditioning the surprisal centroid on the AGENT sharpen the error flag (not re-selection -- the flag
  is the validated win)? On the agent-applicable subset (current agent grounded; coverage 0.41 gold /
  0.85 reader): agent-conditioned surprisal is directionally >= verb-only (gold AUC 0.690 -> 0.699;
  FUSED verb+agent 0.705, +0.015 [-0.003,+0.035]), reader-agent ~flat (fused +0.008) -- but NOT
  CI-separated. THE NEGATIVE IS DIAGNOSED (`exp_forward_prediction_flag_negative_diagnosis_v1.py`) --
  and NOT to "the coarse grounded space" (that was a hand-wave; the diagnosis corrected it):
  (1) conditioning is NOT inert -- the agent-weighted centroid really shifts (cos(verb_c,agent_c)=0.76,
  corr(s_verb,s_agent)=0.84, median |dsurprisal|=0.17). (2) DIRECTION depends on AGENT QUALITY: with a
  CLEAN gold agent it raises surprisal MORE on errors (+0.082 vs +0.056 -- weakly right, the +0.009 gain);
  with the READER's NOISY agent it raises surprisal more on CORRECT items (+0.030 vs +0.053 -- WRONG
  direction), so agent-extraction noise HURTS. (3) DOMINANT cause -- ~48% (gold) / 45% (reader) of the
  reader's errors have s_verb(pick) <= s_verb(gold): the reader chose something MORE thematically expected
  than the correct answer -- good-enough / SEMANTIC-ILLUSION errors (Ferreira; drill 1) that are LOW-
  surprisal and STRUCTURAL, which NO plausibility signal (verb, agent, or richer) can flag. Sharpening
  plausibility helps on the anomaly half but HURTS on the structural half (makes a plausible-but-wrong
  pick look even more expected), netting ~zero. So the flag ceiling and the re-selection wall are the
  SAME structural-vs-plausibility boundary, not two coarse-space problems.
- **D. TWO-FACTOR FLAG exploration (the diagnosis's optimization opportunity -- tested to the mechanism).**
  The diagnosis said surprisal misses STRUCTURAL semantic-illusion errors (the reader picked a
  more-plausible-but-wrong argument); drill 1 + drill 4 say the brain flags those with a SECOND stream
  (LIFG selection / semantic-P600 = retrieval interference). Built + tested three candidate second-factor
  signals as complements to surprisal, evaluated (drill 4's pre-registered gate) on the LOW-SURPRISAL
  error subset (the illusion quadrant), CI-sep bar:
  - NON-CANONICITY (passive/fronted) -- FAILS: AUC 0.487 (~chance); the reader's wired parse handles
    non-canonical constructions, so its structural errors are NOT there (`exp_forward_prediction_two_factor_flag_v1.py`).
  - CANDIDATE COUNT -- weak/DIRECTIONAL: standalone AUC 0.67; flags the low-surprisal errors (0.571 on
    the LOW subset, beats chance); combined lift over surprisal +0.009..+0.033, NOT CI-sep. Partly a
    raw-difficulty (more competitors -> more errors) effect, but with a real "competition erodes competence"
    component (reader/chance error ratio rises 0.44->0.67).
  - COMPETITOR CONFUSABILITY (drill 4's brain-faithful signal: posterior-weighted meaning-similarity of the
    reader's pick to the other candidates; cue-based retrieval interference) -- FAILS its gate
    (`exp_forward_prediction_confusability_flag_v1.py`): AUC 0.468 on the LOW subset (~chance, below the
    null p95 0.546), WORSE than count (-0.103), and it HURTS combined with surprisal (-0.049). The CRUDE
    count beat the BRAIN-FAITHFUL signal.
  INTERPRETATION -- NOW DIRECTLY TESTED AND CONFIRMED. Hypothesis: the reader binds POSITIONALLY (word-
  order/parse), not by semantic cue-match, so its errors are STRUCTURAL and no semantic signal can capture
  them. DECISIVE TEST (n=355 grounded errors): the reader's wrong-pick-to-GOLD grounded similarity = 0.221,
  IDENTICAL to the typical competitor-to-gold baseline 0.229 (the wrong pick is MORE similar to gold than a
  random competitor only 48.5% of the time = CHANCE; 44% of errors are clearly unrelated, 40% near-twin, 16%
  in-between). So the reader's wrong pick bears NO special meaning-relation to the correct answer -- it is a
  structurally-selected wrong entity. CONFIRMED: the errors are STRUCTURAL/positional, not semantic near-twin
  / retrieval errors -- which is exactly why EVERY semantic signal (surprisal-reselection, agent, richer
  metric, confusability) failed. THE CORRECTED OPTIMIZATION (redirects the second factor from semantic to
  STRUCTURAL): a two-factor flag = surprisal (thematic anomalies) + PARSE-METHOD DISAGREEMENT (the reader
  already computes BOTH a positional and a parse-router binding; when they DISAGREE the binding is
  structurally uncertain -- the actual LIFG/P600 STRUCTURAL conflict, not semantic interference). Deployable
  (both bindings exist), brain-faithful, and aimed at the structural errors confusability could not reach.
  BUILT + TESTED (`exp_forward_prediction_parse_disagreement_flag_v1.py`) -- and it FAILS in the OPPOSITE
  direction, which is the TERMINAL finding: when positional and router DISAGREE the reader is MORE accurate
  (20% error) than when they AGREE (44%); disagree-AUC 0.44 (BELOW chance). Disagreement flags where the
  router did HELPFUL extra work (passives/ditransitives), NOT where the parse FAILED. So the reader's
  structural errors are SILENT POSITIONAL DEFAULTS -- the parse should have overridden the "nearest post-verbal
  nominal" rule but did not, so BOTH methods agree on the wrong answer. They look CONFIDENT -- which is exactly
  why NOTHING flags them (surprisal, confusability, agent, richer metric, AND parse-disagreement all fail: the
  reader is CONFIDENTLY wrong). TERMINUS: the ~half of errors surprisal misses are SILENT PARSE-COVERAGE
  failures, unflaggable by ANY self-consistency/plausibility signal; the ONLY lever is a BETTER PARSER (the p2
  predictive parser -- the ORIGINAL filed follow-on, "residual ceiling is parser recall"). The candidate-count
  that weakly worked is just a raw difficulty proxy.
- **THE UNIFYING META-FINDING (refined by the diagnosis).** Across SIX probes -- richer dimensions,
  exemplar estimator, taxonomic metric, agent-conditioned re-selection, agent-conditioned flag, and the
  flag-negative diagnosis -- there are TWO nested limits, and the deeper one is NOT "the coarse grounded
  space": (i) FEATURE SUPPLY -- the grounded space is coarse, capping the plausibility signal's quality
  (the Phase-1 lever, real but secondary); (ii) THE STRUCTURAL-vs-PLAUSIBILITY BOUNDARY -- ~HALF the
  reader's who-did-what errors are STRUCTURAL (the reader chose a MORE-plausible-but-wrong binding; a
  semantic illusion), and these are out of scope for ANY plausibility signal in ANY representation --
  only the PARSE's structural information reaches them. This is why the SAME boundary appears as the
  re-selection wall (plausibility can't out-select the parse) AND the flag ceiling (plausibility can't
  flag structural errors) AND English being word-order-dominant (Competition Model). The forward-
  prediction MECHANISM is faithful and validated as a FLAG on the thematic-anomaly half; the residual is
  a DIVISION OF LABOR (the parse owns structural disambiguation; the plausibility signal owns thematic
  anomalies), not one missing feature. The Phase-1 structured event store helps (i); it will NOT cross
  (ii) without the parse -- the SDM proper fuses BOTH, which is why that is the named follow-on.

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
6. **RULE OUT the easy hypothesis before naming the hard one.** The obvious "the space is too small,
   add dimensions" was testable and WRONG: a fair 1024-d distributional space is WORSE than 12-d for
   thematic ranking (topical co-occurrence is the wrong axis). Running that probe converted "build a
   richer meaning space" (vague) into "build a STRUCTURED event store, NOT a bigger flat embedding"
   (precise) -- a much sharper follow-on. Ruling out the cheap explanation is what makes the expensive
   one trustworthy.
7. **DIAGNOSE a negative before labeling it -- I was wrong once and the diagnosis caught it.** I first
   attributed the flag-probe negative to "the coarse grounded space." Decomposing it (inert? direction?
   structural?) showed that was a hand-wave: the conditioning FIRES, and the real cause is that ~half the
   errors are STRUCTURAL semantic-illusions (the reader's wrong pick is MORE plausible than the gold) that
   NO plausibility signal can flag -- plus agent-EXTRACTION noise actively hurting. That reframed the
   whole result: the flag ceiling and the re-selection wall are ONE structural-vs-plausibility boundary,
   and the fix is a DIVISION OF LABOR with the parse, not one missing feature. "Ask whether a component
   is missing before claiming an intrinsic ceiling" caught a real mislabel.

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
1. **Build the RE-SELECTOR (highest yield, Phase-1 meaning lever) -- as STRUCTURE, evidenced by a
   FOUR-WAY convergent negative.** Four independent plausibility levers were built + tested and NONE
   out-selects the parse: richer DIMENSIONS (ruled out), the exemplar ESTIMATOR (+0.08 but caps at
   0.46), the taxonomic METRIC (better than topical, still < grounded), and AGENT-conditioning (null vs
   twin). So the follow-on is unambiguous: a STRUCTURED verb-role -> rich-filler event store that
   combines the exemplar estimator + a dependency-parsed selectional metric + agent/event conditioning
   WITH the parse's structural information (SDM proper; Chersoni/Lenci; FHRR role-filler binding), NOT
   any single flat component. This is a large Phase-1 build, now motivated by evidence.
2. **Wire the abstain flag now (Q111):** the validated confidence/abstain decision does not depend on
   the re-selector build. Wire the FUSED (verb+agent) surprisal (directionally the best flag) rather
   than verb-only.
3. **Feed `gap_detector`'s write-gate from this surprisal** (the memory-level node; learner-on path).
4. Agent-role (not just patient) who-did-what slice for cross-role generalization.
   (The agent-conditioned-SURPRISAL flag probe -- build C above -- is DONE: directional, not CI-sep.)
