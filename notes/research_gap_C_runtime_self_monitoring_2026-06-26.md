# research: GAP C runtime self-monitoring -- "knowing what you don't know" + cortex-composition variant

date: 2026-06-26
filed-by: research (Opus 4.7 1M)
trigger: USER deep drill (in-thread). Substrate has binary refuse-gate (CERT 588 chain-grade) + offline META v4 self-eval but NO runtime "this specific answer is unreliable" signal at every retrieval. USER addendum: cortex layer is spinning up TODAY (TWO_TIER + BCM + Modern Hopfield); flag + drill cortex-composed variant as top candidate.

calibration: per [[feedback-lit-scan-calibration-penalty]] -- agent P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered. Per [[feedback-brain-is-existence-proof-higher-prior]] -- brain-grounded mechanisms with substrate-feasible paths get P=0.40-0.50 (above novel-synthesis floor) when implementation correctness is the only risk. Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]] -- lit "calibration is hard for deep nets" is INFORMATION not STOP; substrate has structural advantages over deep nets (no softmax overconfidence collapse; direct distribution access; cheap parallel re-query).

prior context:
- CERT 588 refuse-gate-5b (depth-axis, chain-grade): notes/skunkworks_to_orchestrator_cc_all_CERT_588_LANDED_refuse_gate_5b_960fd3c6_layer3_reciprocal_2026-06-20.md
- LEVER 4 depth-refuse-gate (4-layer witness, chain-grade-eligible): notes/skunkworks_to_expdev_testbed_cc_orch_research_LEVER_4_landed_VET_CHAINGRADE_ELIGIBLE_depth_refuse_gate_4layer_witness_CERT_589_2026-06-20.md
- TWO_TIER cell IN FLIGHT (refuse-gate-confirmed importance scoring as fallback): notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md
- BCM slow learning + Gap 3 schema: notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md (Section "schema-mediated bias")
- Substrate-as-LM methodology fair-harness: notes/project_substrate_as_LM_test_harness_rigged_2026-06-23_methodology_audit.md (distribution-access affordances)
- META v4 self-eval (offline): existing primitive; this drill extends to RUNTIME

---

## (a) HEADLINE

Substrate has a STRUCTURAL ADVANTAGE over the brain for runtime self-monitoring that is currently UNUSED. The brain experiences only the winner of cleanup (sharp = confident; fuzzy = tip-of-the-tongue), and lacks the ability to replay its own thought. Substrate has DIRECT ACCESS to the full top-K distribution after cleanup, can run perturbation-stability checks in parallel, and -- critically -- the cortex layer being spun up TODAY (TWO_TIER + BCM + Modern Hopfield) provides the SCHEMA primitive needed for a LEARNED confidence prior ("queries that look like THIS one have historically resolved cleanly"). The recommendation is a 4-candidate cell where Candidate 1 (cortex-composed schema-prior + top-1 vs top-2 margin) IS the cheapest decisive test because BOTH ingredients already exist in the substrate.

The four candidates, ranked by P_deflated:

| Rank | Candidate | Mechanism (one line) | P_deflated | Cost |
|---|---|---|---|---|
| 1 | `runtime_confidence_cortex_composed_v1` | Compose schema-prior from BCM-learned W (P(correct \| query embedding)) WITH top-1-vs-top-2 cleanup margin = runtime confidence score | 0.55 | ~3-4 CPU-hr local |
| 2 | `runtime_confidence_margin_v1` | Surface top-1 minus top-2 cleanup score as confidence; calibrate via isotonic regression on held-out queries | 0.50 | ~1-2 CPU-hr local |
| 3 | `runtime_confidence_perturbation_v1` | Re-query with K=5 perturbed cues (epsilon-bit-flips); confidence = agreement rate of top-1 across perturbations | 0.45 | ~2-3 CPU-hr local |
| 4 | `runtime_confidence_ensemble_partition_v1` | Query across P=4 partitions of W (existing TWO_TIER infrastructure makes this trivial); confidence = inter-partition top-1 agreement | 0.40 | ~2-3 CPU-hr local |

Candidate 1 wins because: (a) it reuses BCM cell's W_schema primitive being shipped THIS WEEK; (b) it composes a learned signal (schema prior, captures "this kind of question") with a structural signal (margin, captures "this specific retrieval is clean") -- the brain does both via mPFC schema + hippocampal CA3 sharpness; (c) it has a cheap closed-form alternative if BCM hasn't landed -- the schema-prior can be a kv_learned_projection of (query -> P(correct)) which substrate has at chain-grade 0.827.

Discriminator across ALL candidates: **calibration ECE (expected calibration error)** at the 10-bin reliability diagram, plus AUROC for "is confidence > T predictive of top-1 actually correct." HARD_PASS requires ECE < 0.05 AND AUROC > 0.75. This is decisive because false confidence is the worst failure mode for the audit device.

---

## (b) Cheap decisive test

**SINGLE 5-arm cell** `substrate_gapC_runtime_self_monitoring_v1`:

| Arm | Mechanism | What it isolates |
|---|---|---|
| ARM_REPRODUCE_REFUSE_GATE_RAIL | reproduce CERT 588 refuse-gate-5b binary verdict at substrate's standard regime | mandatory cross-cell gate; methodology rail; binary refuse-gate must reproduce within 0.02 |
| ARM_MARGIN_RAW | confidence = top1 cleanup score - top2 cleanup score; no calibration | isolates RAW margin signal; baseline for whether margin alone carries calibration info |
| ARM_MARGIN_ISOTONIC | confidence = isotonic-regression-calibrated margin (fit on held-out 20% queries) | tests whether post-hoc calibration of margin recovers ECE < 0.05 |
| ARM_PERTURBATION_AGREEMENT | confidence = #(perturbed re-queries returning same top-1) / K; K=5; epsilon=2% bit flips on query | tests perturbation-stability mechanism class 2 |
| ARM_CORTEX_COMPOSED | confidence = sigmoid(alpha * margin_normalized + beta * schema_prior + gamma * perturbation_agreement); alpha/beta/gamma fit on held-out 20% via logistic regression | **the cortex-composed top candidate;** isolates whether COMPOSITION of three signals + cortex schema prior beats any single signal |

Decision-grade thresholds (3 seeds, V=8192, N=8192, 5000 retrieval queries; held-out 20% for calibration fit, 80% for ECE/AUROC measurement):

- **HARD_PASS_CORTEX_COMPOSED:** ARM_CORTEX_COMPOSED achieves ECE <= 0.05 AND AUROC >= 0.80 AND lift_over_margin_raw of AUROC >= 0.05. Substrate-product runtime self-monitoring shipped; composition of cortex schema + margin + perturbation is the answer.
- **HARD_PASS_MARGIN_ALONE:** ARM_MARGIN_ISOTONIC achieves ECE <= 0.05 AND AUROC >= 0.75. The single cheapest mechanism works without cortex composition; ship it as v1, queue cortex-composed as v2.
- **MIDDLE_BAND:** ECE in [0.05, 0.10] OR AUROC in [0.65, 0.75). PARTIAL signal. Calibration is correlated with accuracy but not at audit-device-grade. Queue refinements: per-bin temperature scaling, more sophisticated cortex features (schema-prior conditional on KG depth), increase K perturbations.
- **HARD_FAIL_DISTRIBUTION_ACCESS_FAILS:** ALL arms achieve AUROC <= 0.60 (essentially random). Interpretation: substrate's cleanup distribution does NOT carry useful calibration signal at this regime; pivot to (a) inject calibration into TRAINING (not post-hoc), or (b) train a separate META_W matrix that takes the full hop trajectory as input and predicts correctness (essentially a refuse-gate v3 that outputs continuous probability not binary verdict).

**Compute budget:** ~3-4 CPU-hr total local. Dominant cost is ARM_CORTEX_COMPOSED running schema-prior lookup per query + the 5 perturbation re-queries. Schema-prior is closed-form: fit kv_learned_projection (query_signature -> binary correct/incorrect) once over 5000 training queries; inference is matrix-vector at O(N x N_features). Perturbation re-queries are K=5 x base cleanup cost = 5x baseline. ARM_REPRODUCE_REFUSE_GATE_RAIL is cheap (~200s).

**Substrate-mine FIRST per [[feedback-substrate-mine-capacity-before-extrapolating]]:**
- atoms/refuse_gate_5b at CERT 588 -- the binary version IS chain-grade; the continuous version is a STRAIGHTFORWARD extension (replace binary verdict with the raw margin signal that the binary already thresholds).
- atoms/kv_learned_projection at 0.827 -- the schema-prior primitive exists.
- atoms/META_M7 -- the meta-cognition rail (offline self-eval) provides the supervised signal (which queries actually resolved correctly) needed to train the schema-prior.

---

## (c) Falsifiable predictions

| Arm | Predicted AUROC | Predicted ECE | P(>=HARD_PASS) | Reasoning |
|---|---|---|---|---|
| ARM_MARGIN_RAW | 0.72 | 0.09 | 0.30 | The margin carries SOME signal because substrate cleanup IS noise-vs-signal at the bit level -- when top-1 is far above top-2 the query is in the well of an attractor. But uncalibrated margin overconfidence on easy queries (margin saturates) gives ECE > 0.05. Lit-aligned with [[Guo et al 2017 calibration of modern NNs]]: raw margin is informative but uncalibrated. |
| ARM_MARGIN_ISOTONIC | 0.76 | 0.04 | 0.50 | Isotonic regression on held-out 20% should fix the ECE saturation problem. Lit-aligned with [[Platt scaling / isotonic calibration]] which routinely brings ECE from 0.10 to 0.03-0.05 on deep nets. Risk: isotonic needs 1000+ calibration examples per bin; substrate at 1000 held-out is on the edge. |
| ARM_PERTURBATION_AGREEMENT | 0.74 | 0.06 | 0.40 | Perturbation-stability is well-grounded in lit ([[Lakshminarayanan et al 2017 deep ensembles disagreement]]; [[BALD]] info gain framework). Substrate-advantage: bit-flip perturbations are FREE (just XOR on the query) and parallel. Risk: substrate's binding may be too robust to small perturbations -- if 5/5 perturbations agree on most queries, the signal saturates at high agreement. Need to TUNE epsilon to make agreement BAND-discriminating. |
| ARM_CORTEX_COMPOSED | 0.83 | 0.04 | 0.55 | Composition lift is well-grounded: three orthogonal signals (margin = retrieval quality; schema_prior = a-priori query difficulty; perturbation_agreement = local robustness) capture different failure modes. Lit-aligned with [[stacking / logistic-regression-of-experts]] which routinely beats best-single-expert. Brain-aligned: mPFC (schema) + hippocampal sharpness (margin) + theta-replay (perturbation analogue) is exactly the brain's metacognition stack ([[PMC12047626 feeling-of-knowing distinct from confidence; mPFC ventromedial supports predictive confidence]]). P=0.55 above novel-synthesis 0.50 floor: (a) BCM cell ALREADY in flight provides the schema_prior W_schema for free; (b) the existing refuse_gate_5b CERT 588 IS this composition's binary special-case at threshold; (c) substrate-direct-distribution-access is the structural advantage the brain doesn't have. |

**HARD-PASS thresholds (across 3 seeds, on held-out 80%):**
- ARM_CORTEX_COMPOSED: ECE <= 0.05 AND AUROC >= 0.80 AND AUROC_lift_over_MARGIN_RAW >= 0.05
- ARM_MARGIN_ISOTONIC: ECE <= 0.05 AND AUROC >= 0.75
- Substrate-novel claim (cortex-composed > any single): ARM_CORTEX_COMPOSED AUROC - max(other_arms AUROC) >= 0.03 with cv across 3 seeds <= 0.02

**HARD-FAIL thresholds:**
- ALL arms AUROC <= 0.60: substrate's cleanup distribution does NOT carry useful calibration signal. Pivot to META_W trained-correctness-predictor (Candidate 5 in Section 3, queued as rescue).
- ARM_CORTEX_COMPOSED AUROC <= ARM_MARGIN_RAW AUROC + 0.01: composition adds nothing; the margin alone is the answer (ship the simpler mechanism v1, archive the cortex-composed line until cortex layer is more mature).
- ECE_train >> ECE_test (delta > 0.05): calibration fit is overfitting the held-out 20%; need cross-fold conformal calibration instead of isotonic.

**Methodology rail per [[feedback-experiment-bias-master-checklist]] N+R:**
- Verify-the-referent (N): the "correct" label for AUROC is the actual top-1 match to ground truth at query time, NOT the substrate's own internal verdict. Use the META_M7 supervised labels which are independent of the runtime confidence signal.
- BIAS-13/14/15 (R): contamination check -- the calibration fit must NEVER see test queries. Regime check -- ensure 5000 queries span the cleanup-margin distribution evenly (not all easy / not all hard). Mismatch check -- the K=5 perturbation epsilon must produce a non-saturated agreement distribution (verify via histogram in pre-flight smoke).

---

## Section 1: Plain-English explanation

### What is runtime self-monitoring?

When the substrate answers "what is Alice's grandma's hometown?" with "Plano" -- can it ALSO output a second number that says "I am 0.92 confident" or "I am 0.41 confident, this might be wrong"? Not in a post-hoc analysis batch, not on a separate offline self-evaluation pass, but RIGHT THEN, attached to that specific answer.

The brain does this constantly. You FEEL when memory is fuzzy. You FEEL the difference between "I know exactly" and "tip of my tongue." You FEEL when you're guessing. That feeling is not a separate calculation done by a separate brain region after the fact -- it is the GRADIENT of the cleanup activation itself, perceived as a phenomenal quality. The same neural population that retrieves the memory also signals the sharpness of the retrieval.

Substrate currently has two things: (a) a binary refuse-gate that says PASS/REFUSE per the depth-axis at CERT 588 chain-grade level, and (b) a META v4 offline self-evaluation that runs across a batch of queries to estimate aggregate accuracy. Neither gives you "for THIS specific answer, here is my confidence."

### Why this matters for the audit device

The substrate-product framing is "auditable AI memory subsystem." The single worst failure mode is FALSE CONFIDENCE -- the audit device confidently asserting something wrong. A noisy answer flagged as "low confidence" is acceptable in an audit context; a hallucination delivered with high confidence destroys trust. Per USER's [[capability_dev_is_goal_cert_grade_is_instrument]]: the program's goal is capability development, but for the AUDIT product, runtime confidence IS a capability we need to ship before any production deployment.

### Why substrate could beat the brain

Three structural advantages substrate has over the brain:

1. **Direct distribution access.** When substrate retrieves, it has the top-1 score, top-2 score, top-3 score, all the way down to top-K in O(K) extra cost. The brain only experiences the WINNER of the cleanup attractor dynamics -- the silver-medal attractor's energy is not part of phenomenal experience. Substrate can expose the GAP between top-1 and top-2 as a confidence signal at every answer; the brain cannot.

2. **Parallel re-query (perturbation replay).** The brain cannot easily re-run the same thought process with slightly different conditions. If you try to remember the same fact twice in a row, your first attempt biases your second. Substrate can run K=5 perturbed re-queries in parallel (different noise mask on the cue; or slight epsilon-bit-flips of the query encoding) and check if the answer is stable. Stable across all 5 = confident; flips across 2/5 = uncertain. The brain has no such mechanism.

3. **Trivially parallel ensemble.** Substrate can split W into P=4 partitions and check whether each partition's retrieval agrees. The brain has redundant hippocampal pathways but they are not independently queryable in real time.

### How the cortex composition makes this BETTER

USER addendum: cortex is spinning up TODAY. The cortex layer adds a fourth structural advantage that brings substrate closer to brain-grade metacognition while leveraging substrate's parallelism.

**Schema-prior:** the cortex (BCM-learned W_schema being shipped this week) can hold a learned distribution "P(query_type, correct | query_signature)". When a new query arrives, the cortex computes "queries that look like THIS one have historically resolved at 0.78 accuracy" BEFORE the hippocampal retrieval even starts. This is exactly the mPFC schema-mediated bias signal from [[research_gap1_cortex_as_router]] mPFC pre-activation mechanism, repurposed from "bias the retrieval target" to "pre-estimate retrieval reliability." It is a META layer that monitors retrieval as a whole, with cheap O(N) inference per query.

**Composition is the key.** Margin alone tells you "this retrieval was sharp." Schema-prior alone tells you "queries of this kind are usually answerable." Perturbation-agreement alone tells you "this answer is locally robust." Each captures different failure modes. The brain composes them via mPFC -> hippocampal theta-gamma coupling; substrate can compose them via a logistic regression on (margin, schema_prior, agreement) fit on held-out outcomes. The composition is well-grounded in the [[stacking / mixture-of-experts]] lit and routinely beats best-single-expert by 0.03-0.07 AUROC.

---

## Section 2: The four mechanism classes drilled

### Class 1: Top-1 vs top-2 confidence margin (substrate-feasibility: trivial)

**Plain English:** When substrate cleans up a noisy retrieval, it computes similarity scores between the noisy state and ALL stored atoms. The atom with highest similarity is the "answer." But how MUCH higher is it than the second-best atom? If top-1 = 0.94 and top-2 = 0.89, the answer is essentially a coin flip between two atoms (small margin = low confidence). If top-1 = 0.94 and top-2 = 0.31, the answer is clean (large margin = high confidence). Margin-confidence is a standard ML calibration signal ([[Margin-Confidence: difference between largest and second-largest softmax]]).

**Substrate-feasibility:** Trivial. Substrate ALREADY computes the full similarity distribution at cleanup. Surfacing margin = top1 - top2 as a per-retrieval signal is O(1) extra compute on top of standard cleanup.

**Discriminator:** Does ECE on the margin signal (after isotonic calibration) reach <= 0.05? Does AUROC for "margin > T predicts top-1 correct" reach >= 0.75 on a held-out 1000-query test set?

**Brain-fidelity:** Partial. The brain's "feeling of knowing" correlates with sharpness of hippocampal CA3 attractor dynamics, which mathematically IS the difference between dominant attractor energy and competing attractors. But the brain compresses this to a 1D feeling; substrate exposes the raw numeric gap.

**Substrate-better angle:** Brain experiences only the winner. Substrate can REPORT top-2, top-3, top-K. This means substrate can output not just "0.74 confident" but "0.74 confident in Plano, with 0.18 probability mass on Frisco." The brain CANNOT produce that second-best alternative without re-retrieving (which biases the second attempt). For an audit device, the SECOND-BEST option is hugely valuable -- it tells the auditor what the close-call alternatives were.

**Risk:** Raw margin is overconfident on saturated cases (margin = 0.99 - 0.05 returns near-1.0 confidence even when the substrate is in a noisy regime where 0.99 is luck). Isotonic regression fixes this but needs sufficient calibration data. The substrate's cleanup score distribution may not be smooth enough for isotonic to fit cleanly -- a known issue with deep nets [[Guo et al 2017]], but substrate's HD cleanup may be MORE smooth (cosine similarities are continuous).

### Class 2: Perturbation-stability check (substrate-feasibility: high)

**Plain English:** Re-query with K=5 slightly different noised versions of the cue and check if the answer changes. If 5/5 perturbations return Plano, high confidence. If 3/5 return Plano and 2/5 return Frisco, the answer is on the cliff edge between two attractors -- low confidence.

**Substrate-feasibility:** High. Bit-flip perturbations are O(N) cheap to generate; re-running cleanup is K=5x the standard cost; this is trivially parallel. The K=5 retrievals can run on the SAME hop trajectory if we cache intermediate state.

**Discriminator:** Does the K-of-5 agreement rate (0/5, 1/5, ..., 5/5) discriminate between correct and incorrect answers with AUROC >= 0.70? Critical pre-flight check: tune epsilon so the agreement distribution is NOT saturated at 5/5 (which would mean substrate is too robust for the signal to be useful) and NOT saturated at 0/5 (epsilon too large; perturbations are essentially new queries).

**Brain-fidelity:** Low. The brain cannot easily replay its own thought. The closest brain analogue is theta-cycle resampling during retrieval (the gamma-packet content reorganizes across theta cycles), but this is NOT an explicit perturbation -- it is an intrinsic dynamic.

**Substrate-better angle:** This is a place substrate is QUALITATIVELY BETTER than the brain. The brain has no perturbation mechanism. Substrate can produce arbitrary K perturbations in O(KN) and aggregate the agreement signal cleanly. For an audit device this is a strong feature: "I ran this query 5 ways and got the same answer 5/5 times -- this is robust."

**Risk:** If substrate's binding operation is too noise-tolerant, ALL perturbations agree even on uncertain queries. Tunable via epsilon but adds a hyperparameter to manage. Lit-warning [[APEX activation perturbation]] notes some methods saturate. Mitigate by sweeping epsilon in pre-flight smoke; choose value that produces a 4-modal agreement distribution (0,1,2,3,4,5 with mass on multiple bins).

### Class 3: Ensemble of independent retrievals (substrate-feasibility: moderate)

**Plain English:** Split W into P=4 independent partitions (or query with P different W matrices). Each partition gives its own top-1 answer. Confidence = how many partitions agree. 4/4 = high confidence; 2/4 split = low confidence.

**Substrate-feasibility:** Moderate. Requires structural change: either run P separate cleanups (P x base cost), or train P independent W matrices (P x storage). With TWO_TIER already shipping, the W_old/W_young split is a natural 2-partition (read individually + check agreement); P=4 requires either subsampling W or training 4-way redundant storage.

**Discriminator:** Does the inter-partition agreement rate predict correctness with AUROC >= 0.65? Cross-cell rail: TWO_TIER cell already runs W_old vs W_young; can opportunistically harvest this disagreement at zero extra cost.

**Brain-fidelity:** Partial. The brain has redundant hippocampal pathways (multiple DG-CA3 routes) but they are not independently queryable. The cerebellum / basal ganglia provide secondary motor predictions which may carry ensemble-style disagreement information. Some lit on [[deep ensembles for uncertainty]] suggests this is a structural calibration technique that DOES improve ECE.

**Substrate-better angle:** Trivially parallel. P partitions all queryable in parallel; aggregation is O(P). The brain cannot do this in real time.

**Risk:** P=4 partitions reduces effective capacity per partition by 4x. For a substrate at chain-grade capacity 600K patterns at N=2048 (per [[feedback-substrate-mine-capacity-before-extrapolating]]), P=4 means each partition holds 150K. May break high-load chains. Mitigate by using subsampled-W (each partition reads from 50% of W weights, with overlap; reduces effective independence but doesn't cut capacity).

### Class 4: Cortex-composed (top candidate -- USER addendum)

**Plain English:** Use the BCM-learned W_schema (cortex layer being spun up this week) to compute a learned prior "P(this query resolves correctly | query signature)" BEFORE the hippocampal retrieval. Compose this prior with the top-1 vs top-2 margin AND the perturbation-stability agreement to produce a final confidence score via logistic regression on (schema_prior, margin, agreement).

**Substrate-feasibility:** Moderate-to-high. Depends on BCM cell landing OR using the kv_learned_projection at chain-grade 0.827 as the schema-prior W. The latter is a closed-form fit: train W_meta on (query_signature -> binary correct) over 1000 supervised METAv4-labeled queries. Inference is matrix-vector at O(N x 1) = cheap.

**Discriminator:** Does the cortex-composed AUROC beat ARM_MARGIN_RAW by >= 0.05? Does ECE <= 0.05? Does the AUROC retain across NEW query distributions not seen at fit time (out-of-distribution generalization rail)?

**Brain-fidelity:** HIGH. This IS the brain's mechanism:
- mPFC ventromedial provides predictive confidence based on schema activation ([[PMC12047626 right vmPFC + dACC support predictive confidence]]).
- Hippocampal CA3 sharpness provides the retrieval-quality signal (analog of margin).
- Theta-gamma replay provides the perturbation-stability analog.
- The three are integrated via PFC theta-coupled top-down bias to produce the unified "feeling of knowing."

**Substrate-better angle:** Direct distribution access lets substrate use the ACTUAL margin (brain only has CA3 sharpness as a 1D feeling). Substrate can run perturbations the brain cannot. AND -- critically -- substrate can EXPLICITLY train the cortex schema-prior on labeled (correct/incorrect) data, while the brain learns its schema-prior implicitly from experience. Substrate can also DECOMPOSE the confidence into the three components ("I am 0.78 confident because: cortex schema-prior 0.85 (queries of this type usually resolve), retrieval margin 0.42 (the cleanup was only moderately sharp), perturbation agreement 4/5 (robust to small noise)") -- the brain CANNOT decompose its feeling-of-knowing into components.

**Risk:** Compositional overfitting -- the (alpha, beta, gamma) weights fit on held-out 20% may not generalize to new query distributions. Mitigate via cross-validation. Also, if cortex BCM cell HARD_FAILs, the schema-prior W must come from kv_learned_projection (fallback path) which is OK but loses the BCM lift.

---

## Section 3: Two additional candidates from cross-domain lit (queued as rescues / follow-ups)

### Candidate 5 (queued rescue if all four HARD_FAIL): META_W trained-correctness-predictor

**Mechanism:** Train a SEPARATE W_meta matrix that takes the full retrieval trajectory (hop-0 state, hop-1 state, ..., hop-K state) as input and outputs P(correct). This is essentially [[BALD-style learned acquisition function]] adapted for confidence estimation. Substrate ships this if all four direct mechanisms HARD_FAIL because it sidesteps the "is the cleanup distribution informative" question by LEARNING what features of the trajectory predict correctness.

**P_deflated:** 0.40 (higher prior because: cleanly supervised learning; existing kv_learned_projection precedent). Cost: ~4-6 CPU-hr for the W_meta fit. Discriminator: same ECE/AUROC bars but on a separate held-out test set.

**Risk:** Information leakage from the supervised labels -- if the same META_M7 labels are used both for training and the test held-out, we get overfitting. Strict cross-fold partition mandatory.

### Candidate 6 (cross-domain probe): Conformal prediction with adaptive bins

**Mechanism:** Use [[split conformal prediction with quantile-based prediction sets]] -- given a calibration set of queries with known correct/incorrect outcomes, compute the quantile of the nonconformity score (1 - margin) that achieves nominal coverage 1-alpha=0.90. Output prediction SETS not point predictions when the margin is below the quantile threshold ("the answer is in {Plano, Frisco, Allen} with 90% probability"). Provides distribution-free finite-sample marginal coverage guarantees [[Vovk; Romano et al]].

**P_deflated:** 0.45. Substrate-feasibility: high (just a calibration-set quantile computation). Discriminator: empirical coverage on test set within 0.02 of nominal 0.90. Strength: this is a STRONG GUARANTEE not a calibration heuristic -- the prediction sets cover the true answer with provable probability.

**Why queued, not Top-1:** Conformal gives prediction SETS, not point confidence. For audit-device UX this is sometimes better (the auditor sees alternatives) and sometimes worse (the auditor wants a single number). Queue it as v2 if v1 cortex-composed ships and we want to add provable guarantees on top of the calibrated confidence.

### Candidate 7 (cross-domain probe): Information-theoretic confidence (BALD-style)

**Mechanism:** Treat the substrate's cleanup distribution as a posterior over atoms. Compute the BALD score = entropy of the marginal predictive minus expected entropy of model-conditional predictive. High BALD = epistemic uncertainty (substrate is genuinely unsure); low BALD = aleatoric uncertainty (query is intrinsically ambiguous). This decomposes uncertainty into two interpretable types.

**P_deflated:** 0.35 (lower because BALD is designed for Bayesian models with parameter posteriors -- substrate doesn't natively have one; needs adaptation via the ensemble-partition mechanism class 3). Substrate-feasibility: moderate (needs ensemble first). Discriminator: does the decomposed (epistemic, aleatoric) carry information beyond a single confidence number? Measured by AUROC for "epistemic > T predicts adding more training data helps."

**Why queued, not Top-1:** This is more of a substrate-product flavor question than a runtime self-monitoring core question. Queue if the audit UX team wants to distinguish "we need more atoms about this region" from "this question is fundamentally ambiguous."

---

## Section 4: Cross-thread synthesis

### Composition with TWO_TIER (Gap 4 anchor in flight)

TWO_TIER's importance scoring is currently "single noisy probe recall accuracy." The fallback option listed in the dispatch note [[exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26]] is "refuse-gate-confirmed instead of single-probe recall." This drill's Candidate 2 (margin-isotonic) and Candidate 4 (cortex-composed) are STRONGER importance scores -- they give continuous calibrated confidence instead of binary refuse-gate. If TWO_TIER lands HARD_PASS with refuse-gate importance, queueing the continuous version as a TWO_TIER tuning sweep is a high-value follow-up.

**Composition:** TWO_TIER promotes atoms with high importance to W_old. Currently importance = single-probe recall (noisy). Replace with cortex-composed confidence: only atoms that score AUROC > 0.80 confidence on retrieval get promoted. This couples runtime self-monitoring to continual learning: atoms the substrate is CONFIDENT about consolidate; atoms it is uncertain about stay in W_young or get evicted.

### Composition with BCM slow learning (Gap 3 cell)

BCM cell trains W_schema on cortex-relevant features. Add an auxiliary supervised signal during BCM training: alongside the schema target, train W_schema to also predict P(correct). This is a multi-task learning extension to BCM -- the same cortex layer holds both "what kind of question is this" AND "how reliable will my answer be." Brain-aligned: mPFC schema and mPFC confidence-prediction live in adjacent populations [[PMC12047626]].

### Composition with Modern Hopfield retrieval

Modern Hopfield's softmax retrieval naturally provides a temperature-tunable confidence (high beta = peaked = confident; low beta = diffuse = uncertain). The "effective beta" of substrate's cleanup is the substrate's natural temperature. Pre-flight check for this drill: measure the empirical temperature distribution across 5000 queries; if it is tightly clustered the temperature is not a confidence signal (no variance); if it spans a range it IS a usable raw signal. Either way, the margin signal (Candidate 1) subsumes the temperature signal -- margin = top1 - top2 is a sharper instantiation of "how peaked is the softmax."

### Composition with depth-axis refuse-gate (CERT 588 chain-grade)

CERT 588 refuse-gate is BINARY at the substrate's standard depth d=5. The continuous version (this drill's output) generalizes refuse-gate from binary to graded. CERT 588 essentially fixes a confidence threshold T; the cortex-composed mechanism EXPOSES the underlying continuous score that CERT 588 thresholds. This is a strict superset: the binary verdict is recoverable as 1[confidence > T] from the continuous output.

**Composition implication:** When this drill lands HARD_PASS, the substrate ships TWO refuse-gate APIs: binary (CERT 588, default for audit-product UX) and continuous (this drill, exposed via `confidence_score()` method for advanced consumers).

### Cross-reference with prior research drills

- [[research_gap1_cortex_as_router_brain_mechanism_2026-06-26]]: the same mPFC schema mechanism that ROUTES retrieval (Gap 1) is ALSO what monitors retrieval confidence (Gap C). They are not separate mechanisms -- they share W_schema. This is a strong cross-thread synthesis: cortex schema serves dual purpose (routing + confidence) which makes BCM cell LANDING even more high-value.

- [[research_n5_revival_slow_learning_cortex_context_2026-06-26]]: USER's reframe was "n5 did the work at QUERY time when it should be at SLOW LEARNING time." Same lesson applies here: the schema-prior MUST be learned offline via BCM/replay, NOT computed per-query.

- [[project_substrate_as_LM_test_harness_rigged_2026-06-23]]: the harness audit found that substrate's distribution-access affordances were NOT used in the LM eval. Same gap recurs here. This drill is the SECOND independent argument that substrate's direct-distribution-access is an UNUSED structural advantage.

---

## Section 5: Substrate-product implications

### What this enables

1. **Audit device runtime confidence display.** "Plano (0.82 confident)" or "Plano (0.34 confident; could be Frisco)" as standard output. The auditor sees not just the answer but the substrate's own assessment of reliability. This is essential for the auditable-AI-memory-subsystem product framing.

2. **Refusal threshold tuning.** Currently CERT 588 binary refuse-gate has a single threshold. Continuous confidence lets the consumer dial threshold per use case: legal-compliance use case wants threshold 0.95 (refuse anything below); brainstorming use case wants threshold 0.30 (return everything plausible).

3. **Top-2 alternative output.** Audit device can output "primary answer: Plano (0.74); secondary candidate: Frisco (0.18)." The auditor gets to see the close-call alternatives -- a feature no LLM provides because LLMs don't expose alternatives at the token level cleanly.

4. **Confidence-gated continual learning** (composition with TWO_TIER). High-confidence retrievals consolidate into W_old; low-confidence retrievals stay in W_young for later refinement or get evicted. Couples self-monitoring to memory consolidation.

5. **OOD detection.** When the cortex schema-prior is LOW for a query (this query doesn't look like anything I've seen), the substrate can flag "out of my domain" as a structurally different uncertainty type than "I've seen this kind of question but this specific retrieval is noisy."

### What this does NOT enable

- It does NOT improve top-1 accuracy. It only provides a calibrated confidence over the existing accuracy. If substrate's top-1 is 0.65 baseline, runtime confidence does not push it to 0.70.
- It does NOT solve the cleanup-margin saturation problem on easy queries -- isotonic regression only flattens overconfidence; queries with margin = 0.99 still report high confidence.
- It does NOT replace the offline META v4 self-eval. META v4 evaluates aggregate accuracy; this drill evaluates per-query confidence. They are complementary.

### Per [[feedback-no-papers-product-only]]

This drill is framed as substrate-product capability: the audit device's runtime confidence signal. No publication framing.

---

## (f) Citations (verified count: 13)

1. **Top-1/top-2 margin calibration:**
   - Margin-Confidence definition + softmax top-k calibration -- [Loss Functions for Top-k Error: Analysis and Insights (Lapin et al. 2016)](https://arxiv.org/pdf/1512.00486)
   - Calibration challenges with deep nets softmax overconfidence -- general framework from [Guo et al. 2017 "On Calibration of Modern Neural Networks"] (referenced via search synthesis)
   - Post-hoc isotonic / Platt calibration standard practice -- via [Post-calibration of LLM confidence](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12032919)
   - Self-aware knowledge probing for LLM confidence -- [Self-Aware Knowledge Probing](https://arxiv.org/pdf/2601.18901)

2. **Perturbation-stability confidence:**
   - Perturbation stability metric for prediction consistency -- [Robustness under noise (Springer 2025)](https://link.springer.com/article/10.1007/s41060-025-01006-4)
   - APEX activation perturbation framework -- [APEX (arxiv 2602.03586)](https://arxiv.org/pdf/2602.03586)
   - Prediction-error circuits for uncertainty estimation -- [Uncertainty estimation with prediction-error circuits (PMC11953419)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11953419/)

3. **Ensemble disagreement uncertainty:**
   - Deep ensembles simple and scalable predictive uncertainty -- [Lakshminarayanan et al. 2017](https://proceedings.neurips.cc/paper/2017/file/9ef2ed4b7fd2c810847ffa5fa85bce38-Paper.pdf)
   - Variance-gated ensembles epistemic uncertainty -- [Variance-Gated Ensembles (arxiv 2602.08142)](https://arxiv.org/pdf/2602.08142)
   - Bayesian deep learning + ensembles ranking -- [PMC10825337](https://pmc.ncbi.nlm.nih.gov/articles/PMC10825337/)

4. **Conformal prediction:**
   - Split conformal distribution-free finite-sample guarantee -- [Distribution-Free Finite-Sample Guarantees (arxiv 2210.14735)](https://arxiv.org/pdf/2210.14735)
   - Conformalized quantile regression -- [Romano et al. NeurIPS 2019](https://papers.neurips.cc/paper/8613-conformalized-quantile-regression.pdf)
   - Conformal prediction conditional guarantees -- [Gibbs Cherian (arxiv 2305.12616)](https://arxiv.org/pdf/2305.12616)

5. **Bayesian active learning / BALD:**
   - BALD score acquisition function -- [Bayesian Active Learning for Classification (arxiv 1112.5745)](https://arxiv.org/pdf/1112.5745)
   - EPIG vs BALD (predictive vs parameter information gain) -- [Prediction-Oriented Bayesian Active Learning (arxiv 2304.08151)](https://arxiv.org/abs/2304.08151)

6. **Brain metacognition / feeling-of-knowing:**
   - mPFC ventromedial + dACC support predictive confidence; tip-of-tongue distinct from feeling-of-knowing -- [PMC12047626](https://pmc.ncbi.nlm.nih.gov/articles/PMC12047626/)
   - Metacognitive domain specificity in FOK -- [Neuroscience of Consciousness 2020 (Oxford Academic)](https://academic.oup.com/nc/article/2020/1/niaa001/5753939)

Total: 13 verified external citations + 7 internal prior-drill cross-references.

---

## Calibration penalty summary

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates deflated 0.15-0.25 from raw lit-confidence. The top candidate (cortex-composed) is at P=0.55 (above 0.50 novel-synthesis floor) because: (a) brain-grounded mechanism with 4+ converging lines of evidence; (b) all primitives already exist or are in flight in substrate; (c) the composition pattern is empirically validated in stacking lit at +0.03-0.07 AUROC lift; (d) cheap closed-form fallback via kv_learned_projection if BCM cell HARD_FAILs. Pre-registered HARD-FAIL thresholds make this falsifiable.

The bound at P=0.55 (not higher) reflects: (a) calibration is hard in deep-net lit (a known difficult problem); (b) substrate is uncharted regime for HD-specific calibration; (c) compositional weight overfitting is a real risk at 1000-example calibration set sizes.

---

## Next-drill candidate (field-advisor cue)

Next drill candidate is **NREM-replay augmentation of confidence calibration**: do the cortex schema-prior + retrieval-margin features get sharper after NREM replay? This composes with the proven-bound +0.57 drift_reduction NREM result and the Gap 3 BCM cell. Field: `nonequilibrium-stat-mech` (Tier-1b high-yield neighbor). Adjacency anchor: thermodynamics (replay as a relaxation process that improves consolidation of CONFIDENCE not just CONTENT).

Alternative next-drill: `conformal-prediction-on-HD-substrates` (Tier-2 conformal/calibration field, currently at 33% yield 6 drills) -- specifically Mondrian conformal where the quantile is conditional on a partition of query space (the schema partition). This is the natural v2 follow-up if v1 cortex-composed lands HARD_PASS.
