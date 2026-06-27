# Research drill 3x -- substrate self-monitoring (metacognition; "I know what I don't know")

Filed: 2026-06-27 ~18:30 PDT
By: research (Opus 4.7 1M)
USER directive 2026-06-27 ~18:00 PDT: drill all high-priority 3x; consider testability with current substrate elements; build experiments to prove out.
Budget: ~30 min synthesis; lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap P<=0.50).
Relation to prior work: builds ABOVE 2026-06-26 runtime self-monitoring drill (cortex-composed / margin / perturbation / ensemble / W_meta). That drill targeted PER-QUERY confidence. This drill targets META-knowledge ("the substrate has/lacks knowledge about X") -- a layer above per-query confidence. Both layers are required for safe conversational use.

---

## (a) HEADLINE

Substrate currently has a retrieval-confidence layer (refuse-gate at V_REL=256; HRR cleanup-strength; ultrametric structural confidence) but NO META-knowledge layer that says "I lack coverage in region R of concept space" before a query is even issued. Three orthogonal angles converge on the same buildable mechanism: a partition-coverage signal harvested from M=10M routing combined with posterior-entropy-over-readouts gives substrate a calibrated "I don't know this region" answer that's testable today on synthetic data without any language dependence. Top-2 cell proposals below; both are CPU-eligible.

---

## ANGLE A -- PURE MATH (Bayesian posterior entropy / calibration)

Three substrate-mappable proposals:

**A1. Posterior entropy over top-K cleanup scores.** After multi-readout retrieval returns the top-K candidates with cosine scores, normalize via softmax (temperature tuned on held-out) and compute Shannon entropy. High entropy = "many candidates equally plausible" = "I don't know which one." Substrate has top-K compose primitive (chain-grade 2026-06-26 smoke HARD_PASS) -- entropy is a 5-line addition over its output. Lit anchor: token-level entropy is the canonical white-box LLM uncertainty signal (Sun et al. 2025 KDD survey).

**A2. Cosine separation (top-1 vs top-K+1..N) as signal-to-clutter ratio.** If top-1 cosine is 0.85 and second-rank is 0.83, retrieval is high-conflict; if top-1 is 0.85 and rank-K+1 onwards averages 0.05, retrieval is clean. Ratio (top1 - mean_rest) / std_rest is a calibration-friendly signal. Substrate-native because all cosines are already computed during ultrametric clustering.

**A3. Bootstrap predictive variance via perturbation.** Re-query with K=5 epsilon-bit-flipped versions of the input; compute variance over returned top-1 scores. Was filed as Anchor #3 in 2026-06-26 drill (perturbation-agreement). Not duplicating here; flagging composition.

P_deflated A1 = 0.55; A2 = 0.50; A3 = 0.45 (already in flight).

---

## ANGLE B -- BRAIN (rACC + feeling-of-knowing + tip-of-tongue)

Three brain-mappable substrate mechanisms:

**B1. Refuse-gate as ACC analog (conflict detector).** Anterior cingulate cortex + right dorsolateral PFC operate as a conflict-detection circuit (Maril/Wagner fMRI on TOT states). Substrate's refuse-gate at V_REL=256 fires when cleanup-margin falls below threshold -- it's already a binary conflict detector. Upgrade: refuse-gate should emit CONTINUOUS conflict signal (margin magnitude, not just binary fire), enabling downstream consumers to act on graded uncertainty.

**B2. Partial-cleanup magnitude as tip-of-tongue analog.** TOT state = brain reports "I KNOW I know it" while retrieval explicitly fails. In substrate terms: a query where (a) cosine to nearest concept-cluster centroid is HIGH but (b) cleanup to specific atom is LOW = "the region is familiar but the specific item won't crystallize." Two-stage retrieval signal substrate already has the components for (cluster-level via ultrametric, atom-level via cleanup). Behavioral prediction: substrate should produce TOT-like cases where it refuses retrieval but correctly identifies the CATEGORY of the missing item. Brain-aligned, falsifiable, novel substrate behavior.

**B3. Feeling-of-knowing as ACC pre-retrieval prediction.** FOK = subjects predict retrievability BEFORE attempting retrieval (Hart 1965; Schraw). Substrate analog: predict "is this query in a high-coverage partition" by checking which of the M=10M partitions the query hashes to and looking up that partition's historical fill density + atom-mean-cosine. Cheap pre-flight signal; analogous to brain's metacognitive prediction. P_deflated 0.55.

Key citation: Tip-of-Tongue and FOK Enhance Metacognitive Sensitivity of Confidence Evaluation of Semantic Memory (Journal of Cognition 2024) shows TOT/FOK states are EMPIRICAL CALIBRATION SIGNALS not noise -- this is a strong P bump for the substrate-aligned TOT-mechanism cell.

P_deflated B1 = 0.50 (incremental from refuse-gate); B2 = 0.50; B3 = 0.55.

---

## ANGLE C -- CROSS-DOMAIN ML (epistemic/aleatoric + conformal + OOD)

Three substrate-mappable algorithms:

**C1. Partition-coverage as epistemic uncertainty signal.** Epistemic uncertainty = "model lacks data here" (reducible). Substrate has M=10M partition routing -- each partition has a fill density (atoms per partition). Low-density partitions = low coverage = high epistemic uncertainty. Direct lookup at query time; near-zero compute cost. Lit anchor: Sale et al. 2025 (ICML) on epistemic/aleatoric separation in conformal prediction confirms the conceptual frame.

**C2. Conformal prediction set via per-partition cosine quantile.** Build a calibration set per-partition; compute the alpha-quantile of cosine scores; at query time, return prediction set = all atoms above the quantile. Guarantees calibrated coverage (1-alpha) per partition. Lit anchor: EPICSCORE (Sale et al. 2025) augments conformal scores with Bayesian predictive distribution -- substrate's per-partition density naturally provides the Bayesian prior. Substrate-natural because the partition structure is ALREADY there.

**C3. OOD detection via partition-routing failure.** Out-of-distribution input = a query that routes to a NEAR-EMPTY partition (or fails to route at all -- hash collision sparse). Lookup cost = O(1). Lit caveat (Yuan et al. 2025 "OOD Detection Methods Answer the Wrong Questions"): naive OOD detection often answers a different question than intended; substrate's mechanism is grounded in coverage, not in distance from a training-distribution mean, so dodges one common failure mode.

P_deflated C1 = 0.60 (highest of the drill -- substrate-natural + cheap + lit-grounded); C2 = 0.50; C3 = 0.55.

---

## TESTABILITY (per USER directive 2026-06-27 ~18:00 PDT)

All three angles converge: substrate's M=10M partition routing + multi-readout top-K + ultrametric clustering + refuse-gate provide the raw signals. Each angle adds a different transformation. We can build a unified meta-knowledge layer on synthetic data TODAY without any language dependence.

**Synthetic test design (CPU-eligible):**
- N=5000 synthetic queries, half drawn from substrate's covered concept space, half drawn from a held-out region (controlled OOD).
- Ground truth = which queries SHOULD substrate know (by construction)
- Discriminators below test whether substrate self-reports calibrated to ground truth.

---

## TOP-2 CELL PROPOSALS (CPU-eligible; falsifiable)

### Cell #1 -- `meta_knowledge_partition_coverage_v1` (Angle C1 + B3; recommended Top-1; P_deflated 0.60)

**Mechanism:** For each query, compute three signals: (a) partition fill-density at routed partition, (b) atom-mean-cosine within partition, (c) posterior entropy over top-K=10 cleanup scores. Combine via logistic regression fit on a 1000-query calibration set with binary correctness labels. Output: calibrated P(substrate-knows-this) in [0,1].

**Arms (3):**
- ARM_BASELINE: refuse-gate-only (current binary signal).
- ARM_PARTITION_DENSITY: partition fill-density alone, isotonic-calibrated.
- ARM_COMPOSED: all three signals via logistic regression.

**Discriminator (concrete numbers):**
- HARD_PASS: ARM_COMPOSED ECE <= 0.05 AND AUROC >= 0.75 AND confidence_when_correct > confidence_when_wrong by >= 0.3 std (per USER directive) AND refuse-gate fires for >= 90% of OOD queries (controlled synthetic OOD set).
- HARD_FAIL: ECE > 0.10 OR AUROC < 0.65 OR no separation between correct/wrong confidence distributions.
- MIDDLE_BAND: ECE in [0.05, 0.10] OR AUROC in [0.65, 0.75].

**By-construction-saturation check (per META_M7 + USER 2026-06-22 caught the pattern):** if ARM_PARTITION_DENSITY alone hits HARD_PASS, ARM_COMPOSED's lift over it must be >= 0.05 absolute AUROC to claim mechanism (else attribute the win to partition density alone).

**Substrate prereqs verified:** partition routing M=10M exists; top-K compose primitive smoke HARD_PASS 2026-06-26; refuse-gate-5b CHAIN_GRADE CERT 588.

**Compute:** ~5000 queries x 3 arms x 3 seeds = 45000 retrievals. CPU on laptop ~15-30 min.

---

### Cell #2 -- `meta_knowledge_tip_of_tongue_v1` (Angle B2; brain-novel-behavior witness; P_deflated 0.50)

**Mechanism:** Test whether substrate exhibits TOT-like states -- queries where cluster-level cosine is HIGH (substrate "recognizes the region") but atom-level cleanup is LOW (substrate "can't crystallize the specific item"). Use 5000 synthetic queries where half are clean atoms and half are NOISY versions of atoms (controlled SNR sweep). Predict: TOT-rate (cluster-high + cleanup-low) should track SNR monotonically AND substrate should correctly identify the CATEGORY of the missing item even when refusing retrieval.

**Arms (3):**
- ARM_CLEAN: noise-free queries (baseline; expect refuse-gate rarely fires).
- ARM_NOISY_LOW_SNR: SNR = 0.3 (expect high TOT-rate).
- ARM_NOISY_MID_SNR: SNR = 0.6 (expect moderate TOT-rate).

**Discriminator (concrete numbers):**
- HARD_PASS: TOT-rate monotonic in SNR (Spearman rho <= -0.7) AND in TOT cases, cluster-identification accuracy >= 0.70 (substrate KNOWS the category even when refusing the specific atom). Brain-aligned behavior witness.
- HARD_FAIL: no monotonic SNR -> TOT-rate relationship OR cluster-identification at chance (0.10 for K=10 clusters).
- MIDDLE_BAND: monotonic but weak (rho in [-0.5, -0.7]) OR cluster-acc in [0.40, 0.70].

**Substrate prereqs verified:** ultrametric clustering CHAIN_GRADE; cleanup primitive chain-grade; multi-readout exists.

**Compute:** ~5000 queries x 3 arms x 3 seeds = 45000 retrievals. CPU on laptop ~15-30 min.

---

## COMPOSITION NOTE

Cell #1 (partition-coverage) is the substrate-product-ready audit-device upgrade (calibrated "I don't know this" signal). Cell #2 (TOT-like states) is the substrate-novel-behavior witness (substrate exhibits brain-aligned graceful-degradation pattern). Both layer naturally above the 2026-06-26 runtime-confidence cell -- cortex-composed-v1 gives per-query confidence; partition-coverage-v1 gives PRE-query coverage prediction; TOT-v1 gives post-query graceful-degradation signal. Three timescales, three orthogonal mechanisms.

If both Cell #1 and Cell #2 HARD_PASS, substrate has a complete metacognitive stack (pre-query coverage + per-query confidence + post-query graceful-degradation) -- a chain-grade enabler for M3 (glass-box conversational AI).

---

## CONTRACT

- Research OWNS mechanism claims + falsifiable bands.
- exp_dev (spawn `hdi_exp_dev` per agent-spawn-only) OWNS cell-spec authoring + smoke + dispatch.
- Skunkworks (spawn `hdi_skunkworks`) OWNS landed-VET classification per by-construction-saturation default (MM until cert-owner tiers up).
- Per Fix #28: read per-arm metrics, not verdict_msg framings.
- Per CARDINALITY_OK META_RULE_H: cells must declare EXPECTED_N_UNITS = 5000 queries x 3 arms x 3 seeds = 45000.
- Per Fix #26 pre-dispatch verify-the-referent gate: run `tools/predispatch_check.py meta_knowledge_partition_coverage` before any spawn.

---

## SOURCES (lit-scan calibration anchors)

- Sun et al. 2025 "Uncertainty Quantification and Confidence Calibration in LLMs: A Survey" (KDD 2025) -- white-box vs black-box UQ taxonomy.
- Maril/Wagner 2001 fMRI -- ACC + right dlPFC conflict-detection circuit during TOT.
- Tip-of-Tongue and FOK Enhance Metacognitive Sensitivity (Journal of Cognition 2024 / PMC12047626) -- empirical calibration value.
- Sale et al. 2025 (ICML/PMLR vol 266) -- aleatoric/epistemic uncertainty in conformal prediction.
- EPICSCORE 2025 -- Bayesian-augmented conformal scores; partition density as natural prior.
- Yuan et al. 2025 "OOD Detection Methods Answer the Wrong Questions" -- caveat anchor.
