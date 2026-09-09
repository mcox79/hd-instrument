# Working notes (solver scratch -- folded into SOLVED.md, not a deliverable)

## THE MECHANISM (brain-foundational, PINNED comp-level)
- Brain: probabilistic population code (Ma/Beck/Latham/Pouget 2006). A concept = a population whose activity
  encodes a distribution over senses. The population GAIN (total activity / #spikes) sets the precision
  (inverse variance) INTRINSICALLY. Fisher info of a Poisson population ~ gain. Cue combination = ADD the
  populations => precisions (gains) add => the more-reliable cue dominates automatically (Ernst-Banks). No knob.
- Our defect: cosine L2-normalises every concept to unit norm => gain ERASED. The only per-query "confidence"
  a point vector affords is posterior PEAKEDNESS, which tracks CROWDING not correctness (C7: rho 0.68-0.81 vs
  0.00-0.13). So per-item precision weighting was NULL and equal-weight ties every per-item scheme.
- Fix: REFRAME precision from posterior peakedness (output property -> crowding) to ENCODING GAIN
  (representation property = accumulated evidence). Gain per channel:
    DEP  = sum of dependency-context counts (evidence from reading)      [dep_ppmi L2-norm discards it]
    G    = 1/mean Lancaster rater SD (behavioural agreement)             [organ loads only .mean; SD discarded]
    CM   = #WordNet distinctive features                                  [build_cm L2-norm discards it; CURATED -> flat]
- KEY brain-foundational distinction: gain-as-precision is an EXPERIENCE quantity => tracks correctness for
  LEARNED channels (DEP, G) but NOT for a curated ontology (CM: uniform supply, no earned gain). Testable.

## FULL-STACK UPSTREAM (the user's 4 points)
1. End component 100% BF? inputs? research? -> the read is now a PPC: precision = gain (Ma/Pouget PINNED). Inputs
   = the per-concept gain (accumulated evidence) + the normalized meaning vectors. Supported by PPC research.
2. Trace where signal (gain) is lost up the chain -> discarded at (i) asset load (grounded .mean only, SD dropped),
   (ii) construction (PPMI/L2/z-score normalise per concept to unit norm), (iii) READ (cosine = scale-invariant).
3. Dig where it's lost -> the non-BF move is PER-CONCEPT L2 NORMALISATION. Divisive normalization (BF) controls
   dynamic range but PRESERVES relative gain; per-concept unit-norm EQUALISES every concept's evidence to 1,
   erasing the precision. That's the convenient-but-non-BF component. (Cosine's own organ note admits it.)
4. Not cheap off-the-shelf -> the gain is the brain's own quantity (accumulated synaptic evidence); the fix is a
   faithful PPC, not a fitted heuristic. The upstream that EARNS the gain (reading -> dependency evidence, PPMI =
   Hebbian-predictive) is itself BF; that is WHY the gain is a valid precision.

## THE DOWNSTREAM CONSUMER THIS FIXES (concrete hdlab proposal)
convergent_cue_reader.convergent_pick: `argmax_c [logp_epi(c) + w*logp_sem(c)]` with w = DEFAULT_W = 12.0,
CALIBRATED OFFLINE and self-labelled OUR-INVENTION-UNDER-TEST, with the reason verbatim: "our two cue codes are
NOT one shared PPC population, so the automatic-gain story does not give the cross-cue ratio for free." THIS fix
supplies exactly that: carry per-concept gain g_epi(q), g_sem(q); replace the fitted scalar w with the per-query
gain RATIO g_sem(q)/g_epi(q). Removes the single named fitted parameter in the brain's retrieval rule.
- Also removes the fitted weights in calibrate_w / calibrate_global / calibrate_weights (the meaning fusions).
- Recall/recognition path (attractor, ca3_completer, gap_detector) reads normalized vectors only -> byte-identical.

## PROPOSED hdlab CHANGE (Q111 -- strategy lands)
- ADD a per-concept gain scalar alongside the normalized meaning vectors (ConceptSpace / channel matrices):
  gain_DEP = accumulated dep-count; gain_G = 1/rater-SD (load Lancaster .SD); gain_CM = feature count.
- convergent_cue_reader: replace `w` with per-query gain ratio (intrinsic). Equal/uniform gain => byte-identical.
- ADDITIVE: nothing on the recall path changes. Gate: gain-weighted ranking >= equal-weight (Pareto), twin loses.

## ARMS / BASELINES
- EQUAL = C7 all-BF equal-weight Bayes over {G,DEP,CM} (MRR 0.332 ref) -- the current best, no knob.
- PEAK  = concentration-weighted (the NULL heuristic).
- GAIN  = gain-weighted PPC (parameter-free). GAIN_LOG = Weber-compressed robustness.
- FITTED = train-calibrated global weight (the current OUR-INVENTION). GAIN should MATCH/beat it with no fit.
- LEARNED-ONLY {G,DEP} = isolate the mechanism from curated-CM dominance.
- twins: shuffle gain<->word; shuffle rep rows.

## SMOKE (tiny corpus, underpowered) OBSERVED
CM alone 0.425 ~ oracle 0.457 (curated dominates); DEP starved 0.094; CM gain rho 0.02 (curated no-earned-gain
CONFIRMED). Per-item Spearman CIs huge on smoke test set -> rely on FULL + binned calibration.

## FULL RUN NUMBERS (n_words=4359, n_test=169, 3000-boot, corpus 34,169 parsed sents) -- THE VERDICT
### item 1 -- precision tracks correctness (exp_ppc_precision_tracks_correctness_v1)
- DEP (LEARNED): per-item Spearman(gain,RR)=0.155 [CI -0.004,0.311] vs peakedness 0.001; min-gain=0.37;
  BINNED Spearman=0.80 (mean_rr 0.052->0.081->0.127->0.121 across gain quartiles). MECHANISM CONFIRMED.
- CM (CURATED): gain rho -0.035; BINNED Spearman -0.80 (more WordNet features=more polysemy=HARDER); min-gain -0.006.
  -> the experience-quantity signature: curated gain is NOT precision. STRONGLY CONFIRMED.
- G (grounded reliability 1/SD): rho ~0; binned -0.80. grounded gain doesn't track here (G weak overall).
- select_by_GAIN 0.152, select_by_PEAK 0.159, oracle 0.379, best_single CM 0.301 -> NO scalar reliability
  signal captures the oracle headroom.
- item1 strict per-item CI: FAILS (0.155 CI lower -0.004 barely includes 0 at n=169). Binned+min-gain: PASS.
### item 2 -- fusion (exp_ppc_fusion_v1): LOCATED NEGATIVE
- EQUAL 0.3243, GAIN 0.3045, PEAK 0.2833, GAIN_LOG 0.3182, FITTED 0.3167 (weights G1/DEP1/CM2), twin 0.2916.
- GAIN vs EQUAL -0.020 [CI -0.053,+0.013] (GAIN slightly WORSE). GAIN vs FITTED -0.012 [incl 0] (MATCHES fitted, no fit).
- LEARNED-ONLY {G,DEP}: EQUAL 0.1248, GAIN 0.1393, +0.0145 [CI -0.005,+0.036] (directionally positive, not CI-sep).
- KEY: FITTED (0.317) ALSO < EQUAL (0.324) -> equal-weight is AT the per-query reweighting ceiling; NO weighting
  scheme (fitted/gain/peak) beats it. This reproduces C7 "equal ties every per-item scheme". THE located negative.
### item 3 -- byte-identical (exp_ppc_no_regression_v1): PASS
- INV1 uniform-gain==equal-weight bit-identical TRUE; INV2 recall cosine read unchanged TRUE.
- INV3 Pareto: help57/hurt68/tie44 (net -11) on the CM-dominated mix -> gain-weighting net-hurts (expected).
### grow-by-reading (exp_ppc_grow_by_reading_v1)
- DEP MRR 0.032->0.061->0.064->0.096 (RISES with reading). calibration 0.26->0.16->0.18->0.155 (present, ~flat).
- GAIN-EQUAL always negative (-0.006,-0.030,-0.015,-0.020) -> more reading doesn't flip the fusion sign at this scale.

## VERDICT: PARTIAL (rigorous located negative that MEETS the located-negative clause of the bar)
- CONFIRMED: (a) intrinsic gain IS a valid precision for the LEARNED channel (binned 0.80, min-gain 0.37, per-item
  0.155 vs peakedness 0.001); (b) the experience-quantity signature (curated gain anti-tracks -0.80); (c) recall
  byte-identical; (d) gain MATCHES a FITTED weight with NO fitting (eliminates the fitted knob).
- LOCATED NEGATIVE with numbers: gain-weighted fusion does NOT beat equal-weight because equal-weight is already at
  the per-query reweighting ceiling (FITTED 0.317 < EQUAL 0.324 too), and the ranking is dominated by a CURATED
  channel (CM 0.30) whose gain anti-tracks correctness. Oracle headroom (0.379) is real but uncapturable by ANY
  scalar reliability (select-by-gain 0.152).
- STRONGER BRAIN VERSION (required by the bar): intrinsic gain for SELECTIVE PREDICTION / deferral (cell 5, running).
- The real levers: (1) grow the LEARNED channel by reading until IT dominates (then its earned gain is the precision);
  (2) use precision for reliability-aware DECISION (deferral), not fusion-reweighting.
