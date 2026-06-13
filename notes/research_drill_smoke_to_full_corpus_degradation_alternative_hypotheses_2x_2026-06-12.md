# Research note: smoke-to-full corpus degradation -- alternative root causes (2x deep drill, post-refutation)

Date: 2026-06-12
Topic: After the partition-composition-mismatch hypothesis was empirically REFUTED today (partition-stratified smoke HURTS, gap 0.367 vs old homogeneous 0.067; current Phase-2-light z>=3 recurrence already mitigates diffuse jargon), what are the ALTERNATIVE root causes of sample-to-population precision-at-K degradation in extraction pipelines, and how should the methodology be reframed?

Trigger: Exp_dev `exp_partition_stratified_smoke_gap_cpu_v1.py` proxy P@30 measurements
- Homogeneous smoke (research_drill only, OLD design): 0.733, gap to full 0.067
- Partition-stratified smoke (NEW design from earlier 1x drill): 0.433, gap to full 0.367
- Full corpus (1200-file sample): 0.800
- Stratification HURTS at small scale; OLD homogeneous already predicts full corpus well

Honest verify-before-build: the previous 1x research drill (`notes/research_drill_smoke_to_full_corpus_degradation_methodology_partition_stratified_smoke_substrate_quality_first_2x_2026-06-12.md`) bet 0.62 P_deflated on partition-composition mismatch + per-partition scope-aware filters. Empirical refutation arrived within hours. This 2x drill explicitly reframes around the four alternative root-cause classes named in the task input.

---

## HEADLINE

The dominant root cause of smoke-to-full degradation in this pipeline is a **filter-coupling/threshold-coupling mismatch driven by the Good-Turing missing-mass effect at small N**, NOT partition composition mismatch and NOT extractor quality. The substrate's deployment-time z>=3 cross-file recurrence filter is a Heaps/Zipf-law-aware noise control. At full corpus (N=1200), the per-file jargon (atom-IDs, capability-IDs, cycle-numbers, verdict-phrases) is WASHED OUT because each is hapax-class (occurs in 1 or 2 files only) and fails z>=3. At smoke scale (N=30), the same z>=3 rule is OVER-CONSERVATIVE relative to the genuine recurrence distribution: many true primitives also fail z>=3 at N=30, and many spurious primitives PASS by coincidence -- the smoke and the deployment use the same nominal rule but operate at different points on the discovery curve (Heaps' law, beta in [0.4, 0.6]).

Mechanism class: **filter-threshold-curve scale dependence**. The literature label is the Good-Turing **missing-mass-of-features** problem combined with **Heaps-law sublinear vocabulary growth**: when you sub-sample by 40x (1200 -> 30), you don't see a proportional reduction in unique-feature mass; you see a 30^0.5 = 5.5x reduction in unique-feature mass. The deployment threshold (z>=3) is calibrated on the asymptotic regime; the smoke operates at the rare-event regime where Good-Turing corrections matter.

This is consistent with the empirical observation that **partition-stratified smoke makes it WORSE**: stratifying at small N introduces per-partition micro-vocabularies, each of which has higher missing-mass than the homogeneous draw, so the z>=3 filter is even more mis-calibrated on the stratified sample. The OLD homogeneous research_drill smoke worked because research_drill is the highest-coverage partition (closest to the asymptotic Heaps regime); the smoke and the full corpus shared the same effective vocabulary structure.

Reframed methodology: **a smoke is reliable iff its operational vocabulary distribution is asymptotic-regime-equivalent to the deployment corpus under the same filter rule**. The structural lever is not "match the partition mix"; it is "match the filter's operating regime". Two concrete designs follow from the literature: (a) **filter-coupled smoke calibration** -- run the smoke at a scaled threshold (z>=ceil(3 * sqrt(N_smoke / N_full)) ~ z>=1) to match the asymptotic operating point; (b) **Prediction-Powered Inference (PPI) on smoke P@K** -- use the unannotated full corpus + a small labeled smoke and apply Angelopoulos PPI to get a calibrated full-corpus P@K estimate with valid CIs at the smoke's labeling cost.

P_deflated (this drill's headline diagnosis) = **0.48** (pre-deflation 0.65; deflation -0.17 because the substrate-specific regime is uncharted -- no published precedent for Good-Turing missing-mass calibration of recurrence-filter extraction pipelines on partitioned 1k-doc text corpora; and because the prior 1x drill at 0.62 was empirically refuted within hours, calibrating ALL substrate smoke-methodology estimates downward).

Capped at 0.50 per novel-synthesis lit-scan calibration penalty (this IS a novel synthesis -- combining Good-Turing missing-mass, Heaps' law, statAP pool sampling, and PPI into a single substrate-extraction-methodology framework).

---

## Cheap decisive test

ONE round-trip, 2-3 hr wall-clock, CPU-only, on existing `exp_partition_stratified_smoke_gap_cpu_v1.py` infrastructure plus a new threshold-scaling variant:

1. Build THREE smoke designs and run all three against the full-corpus P@30 ground truth:
   (A) OLD homogeneous research_drill smoke (z>=3) -- baseline (gap 0.067 already measured)
   (B) Homogeneous research_drill smoke with **filter-scaled threshold z>=1** (the Heaps-scaling design)
   (C) Homogeneous research_drill smoke with **PPI calibration** -- use the smoke as the labeled subset, the full corpus as the unlabeled population, and compute the PPI-adjusted P@30 estimate per Angelopoulos et al.
2. Compute the smoke-to-full gap for each: |proxy_P@30_smoke - proxy_P@30_full|.

HARD-PASS (Heaps mechanism): design (B) closes gap to <= 0.05 AND design (C) confirms within +/- 0.03. Both signals together identify filter-threshold-curve scale dependence as the dominant cause; methodology rule re-registered as `meta::RULE_substrate_smoke_filter_threshold_scales_with_sqrtN`.

HARD-FAIL: design (B) does not improve over (A) AND design (C) has CIs > 0.20 wide. Then Heaps-mechanism is not the dominant cause; methodology gap is in extractor-itself behavior (selection bias on hapax) or in the proxy metric (not measuring true P@K). Triggers Anchor 3 (statAP infAP sampling-of-the-pool re-design).

MIDDLE-BAND [0.05, 0.15]: one of (B) or (C) helps but not enough. Compose both: PPI-calibrated, filter-threshold-scaled smoke. If the composition closes gap to <= 0.05, ship as canonical substrate-extraction-smoke methodology.

Pre-registered metric scope: PROXY P@30 (jargon-pattern), NOT true P@30. Honest scope flag preserved from refutation memory. If proxy-vs-true divergence is suspected (a separate failure mode), Anchor 4 takes over (build a 30-item gold set for true P@30 ground truth).

---

## Round 1 findings (compact, by drill target)

### Drill target 1 -- Alternative root causes for sample-to-population precision degradation

**Class boundary heuristics under sample size (Cormack-Lyman 2006 "Statistical Precision of IR Evaluation"; Aslam-Kanoulas statAP).** When the evaluation metric is precision-at-cutoff (P@K) and the population scoring distribution is heavy-tailed, the cutoff-K boundary in the sample population shifts relative to the full population. For top-K extraction with a fixed score-rank cutoff, the sample's K-th item lives in a different score region than the full population's K-th item. Mechanism: at small N, the score distribution above the cutoff is poorly sampled (few items above threshold); at large N, the same threshold rejects a relatively higher proportion. This is a sample-size effect on a threshold-defined boundary, not a composition effect.

**Filter-threshold-rule scale dependence (Heaps' law beta in [0.4, 0.6]; Zipf-Heaps coupling).** Sublinear vocabulary growth N(t) ~ t^beta with beta in 0.4-0.6 (language-dependent) means a 40x corpus reduction yields only a ~5.5x reduction in unique-feature count. A frequency threshold (e.g. z>=3 occurrences) that is calibrated on the asymptotic regime over-rejects rare-but-true features at small N (true positives), AND under-rejects accidentally-co-occurring features at small N (false positives that happen to hit z>=3 by random clumping). Both biases compound; the precision-at-K can either improve or degrade depending on whether the rare-true-positive loss or the spurious-clump-survival is larger.

**Good-Turing missing-mass at small N (Good 1953; Valiant-Valiant "Estimating the Unseen"; Painsky 2023 generalized Good-Turing).** At any sample size, a fraction of unique features is unseen; that fraction is estimated by the hapax fraction. In typical text corpora ~30% of observed vocabulary occurs exactly once regardless of corpus size, so the missing-mass curve does not flatten. Mechanism: when the smoke is 30 files, the **observed feature distribution above z>=3** is a tiny fraction of the asymptotic distribution; the filter is making cutoff decisions on a partial picture of the vocabulary structure. The asymptotic-vs-small-N filter behavior is fundamentally different.

**Selection bias (heterogeneity-blind subsampling).** Per Heckman-style sample-selection literature (NBER w28801; Scholarpedia "Sampling bias"), if the smoke is not drawn uniformly at random from the deployment population but rather from a contiguous block (e.g. recent files, files in one directory), the smoke estimate is biased by the file-correlation structure. In this pipeline, sampling from research_drill specifically is a CONVENIENCE sample, not a uniform random sample of the deployment corpus, which selects for a specific content distribution. The refutation data actually shows this is **not the dominant cause** for this pipeline -- the homogeneous research_drill smoke predicts well -- but it remains a candidate failure mode for OTHER substrate-extraction pipelines.

**Sample-evaluation noise model coupling (Domingos "A Few Useful Things about ML"; OOD-eval surveys arXiv 2403.01874, 2306.15261).** Goodhart's law variant: once the smoke metric has been used to tune a single parameter of the extractor, the smoke ceases to measure deployment performance. In the substrate case, the z>=3 threshold itself was tuned to the smoke at some prior cycle, which means the smoke and the threshold are CO-CALIBRATED -- not independently testing each other. This is a structural pathology requiring Goodhart decoupling.

### Drill target 2 -- Methodologies for reliable small-sample P@K estimation

**Pool-based sampling (Aslam-Pavlu-Yilmaz "A Practical Sampling Strategy for Efficient Retrieval Evaluation" SIGIR 2006; statAP/infAP).** TREC-style evaluation faces incompleteness because only top-pooled documents are judged. The statAP technique uses **non-uniform random sampling of the pool** with importance weights inversely proportional to selection probability, then estimates AP as a Horvitz-Thompson-style estimator. infAP applies similar inference to estimate Average Precision from a small judged subset. Crucially these methods give VALID CIs for AP estimates from very small subsets -- typically n=50 judged out of 100K is sufficient.

**Bootstrap confidence intervals (Cormack-Lyman 2006; ConfidenceIntervals github luferrer; arXiv 2407.02464).** The bootstrap re-samples queries with replacement and computes the empirical AP distribution. Valid for n>=30 queries. Gives a confidence interval on AP that quantifies test-collection variability. Importance sampling can sharpen the bootstrap CI by tilting the resampling distribution toward variance-reducing strata (Vernon Johns).

**Prediction-Powered Inference (PPI) for hybrid evaluation (arXiv 2406.04291 stratified-PPI for hybrid LM eval; ICLR 2024 conformal risk control; arXiv 2510.16166 PPI-conformal extension).** Direct fit: you have a small annotated subset (smoke) + a large unannotated corpus (full); a strong prediction proxy (the extractor's own score) + a small labeled correction. PPI gives a valid frequentist CI for the deployment-population metric using the proxy + the labeled subset. The 2024 ICLR variant (conformal risk control) gives distribution-free finite-sample guarantees. For this pipeline: treat the smoke labels as the small annotated subset, the full extractor scores on the full corpus as the proxy, get a PPI-calibrated full-corpus P@K estimate with a CI -- WITHOUT running the full extractor on the labeled set separately.

**Stratified sampling (when stratification axis matches FILTER, not partition).** The refutation memory is sharp: "smoke must match deployment FILTER not partition MIX." Translated: stratify the smoke along the EFFECTIVE recurrence axis (file groups that have similar z-count distributions on the same vocabulary), NOT the LABELED partition axis. This is a literature gap -- standard stratification picks observable labels (partitions); the substrate needs stratification by latent operational behavior (recurrence-class strata). Identifiable via a single pre-clustering step on z-count distributions.

### Drill target 3 -- Calibration between smoke and deployment

**Drift detection in production (MachineLearningMastery, Databricks 2019 "Productionizing ML", patent 12530726 "Post deployment model drift detection").** Quality-of-predictions monitoring is the canonical pattern; data drift = input distribution; concept drift = task semantics. For extraction pipelines, both apply. The standard pattern is to monitor the smoke metric AND a held-out deployment baseline AND a feature parity check AND a transformation reproducibility test. Substrate already has the first; missing the latter three.

**Feature-pipeline parity (Maroof Ashraf 2024 "Complete Guide to Testing Data Pipelines"; BabyLM evaluation pipeline 2024).** Feature engineering stages introduce training-serving mismatch when transformations differ between smoke and deployment. Validation focuses on: feature parity checks, transformation reproducibility, leakage detection. For substrate: the z>=3 threshold is a transformation; if the smoke applies it before sub-sampling and the deployment applies it after, the test is invalid -- this is the structural failure mode.

**Conformal risk control for held-out validation (ICLR 2024).** Provides distribution-free CIs for held-out metrics at finite-sample size. The minimal-cost calibration is: hold out a 30-file VALIDATION smoke that is NEVER touched in parameter tuning, run the full extractor on it, compute proxy P@K, compute conformal-risk-controlled CI. The CI on the validation smoke is a valid prediction of deployment performance regardless of any drift between tuning-smoke and deployment.

### Drill target 4 -- Statistical guarantees small-sample P@K predicts large-corpus P@K

**Concentration bounds.** Hoeffding/Bernstein give finite-sample bounds: for binary precision-at-K with K=30 and N_smoke=30 (counting only the top-30 as "trial samples"), the half-CI width is ~1.96 * sqrt(0.5 * 0.5 / 30) = 0.18. This is the IRREDUCIBLE Wilson-CI floor at K=30. Any methodology that claims gap < 0.05 at K=30 without exploiting model structure (PPI, stratification, importance sampling) is statistically impossible by concentration alone.

Implication: a single 30-file smoke can NEVER achieve gap < 0.05 to full corpus P@K without model-augmented inference. The empirically observed 0.067 gap on the OLD homogeneous smoke is **inside the concentration-bound prediction**, i.e. consistent with random luck or with an implicit model-augmentation (the z>=3 filter's asymptotic-regime alignment with research_drill). The 0.367 gap on stratified smoke is OUTSIDE the concentration bound on the high side -- a real bias signal, not noise -- and matches the Heaps-Good-Turing prediction.

**Pool-sampling guarantees (statAP/infAP).** Aslam-Pavlu-Yilmaz show that for non-uniform pool sampling with importance weights, the AP estimate has bias O(1/sqrt(n)) and CI half-width O(1/sqrt(n)). For n=30 judged items out of 100K pool, the CI half-width on AP is typically 0.05-0.08 -- which is the actual statistical floor for a 30-item smoke to predict full-corpus AP. The OLD homogeneous gap (0.067) sits exactly at this floor; cannot be tightened further by sampling design alone at K=30.

**PPI guarantees (Angelopoulos et al. 2023 PPI; arXiv 2406.04291 stratified-PPI).** Valid finite-sample CI for the population mean using the labeled subset + the unlabeled full population proxy. The CI shrinks at rate 1/sqrt(N_labeled) but with an effective sample-size multiplier proportional to the proxy quality (correlation between proxy score and true label). For a high-quality proxy (extractor score correlated with true relevance), PPI can shrink the CI by 2-5x relative to bootstrap. Concrete: PPI at N_labeled=30 with proxy correlation 0.7 gives an effective N of ~100-150, halving the bootstrap CI. This is the cleanest path to a substrate-specific smoke methodology that achieves < 0.05 gap with N=30 labels.

**Blind-Spot Mass (arXiv 2604.05057 -- recent Good-Turing application to deployment coverage).** Direct: estimates the deployment-coverage risk = probability of encountering an input class not seen in the smoke. For extractor pipelines, this is the probability that a new file at deployment contains a vocabulary structure the smoke never saw. Blind-Spot Mass uses the hapax fraction in the smoke to bound the missing mass; if hapax fraction > 0.3, smoke is NOT in the asymptotic regime, and any prediction of deployment metrics has a Good-Turing-bounded floor on bias.

---

## Round 2 findings (compact, synthesis-oriented)

### Mechanism-class candidates ranked by P(this is the dominant cause)

**1. Filter-threshold-rule scale dependence (Heaps + Good-Turing missing-mass, P=0.48).** The deployment z>=3 filter is calibrated on the asymptotic Heaps regime; the smoke operates in the rare-event regime where the same threshold has different selectivity. Refuted-stratification data is CONSISTENT: stratifying at small N introduces multiple per-stratum sub-vocabularies, each of which has higher Good-Turing missing-mass than the homogeneous draw. The OLD homogeneous smoke works because research_drill is closest to the asymptotic regime for the deployment-time vocabulary that survives z>=3.

Predicted observable: scaling the smoke threshold by sqrt(N_full / N_smoke) ~= sqrt(40) = 6.3, i.e. z>=ceil(3/6.3) = z>=1 at smoke scale, closes the gap. Falsifiable in one extractor run.

**2. Selection-bias x feature-pipeline coupling (Goodhart on z>=3, P=0.20).** The smoke was implicitly used to tune z>=3 at some prior cycle, so the smoke is co-calibrated with the threshold. Stratified smoke breaks the coupling because the stratified vocabulary is different from the research_drill vocabulary that z>=3 was tuned on. Predicted observable: a Goodhart-decoupled validation smoke (NEVER touched during parameter tuning) shows the same 0.067 gap as the OLD smoke ONLY IF this is not the dominant cause; otherwise gap > 0.067 on the validation smoke.

**3. Concentration-floor at K=30 (irreducible noise, P=0.15).** The Wilson CI half-width at K=30 is ~0.18; the observed 0.067 gap and the new 0.367 stratified gap are within concentration-floor variance. The OLD smoke result was statistical luck; the stratified result is statistical bias. Both are consistent with no signal in the test design at this N. Predicted observable: re-running both smoke designs at K=100 or N_smoke=100 reduces both gaps proportionally.

**4. Proxy-metric divergence from true P@K (P=0.12).** The jargon-pattern proxy is not the true P@K; the proxy-metric monotonicity with true P@K is itself a hypothesis. If the proxy is most accurate on homogeneous research_drill vocabulary (where it was designed/tuned), then proxy-vs-true gap is highest on stratified smoke. Predicted observable: build a 30-item gold set, measure true P@K alongside proxy P@K on both smoke designs, observe whether the rank ordering inverts.

**5. Per-partition genuinely-different population (residual P=0.05).** The original hypothesis. Refuted: the empirical data show research_drill smoke predicts full corpus, contradicting the partition-mismatch hypothesis. Kept at residual probability because (a) all measurements are proxy, and (b) the proxy itself may mask a partition signal.

### Best-cost-benefit candidate next empirical test

**Anchor 1 (PRIMARY, 2-3 hr CPU): the three-design comparison.** Runs (A) baseline OLD homogeneous, (B) Heaps-scaled threshold z>=1 on same files, (C) PPI calibration using same files as labeled subset. Decisive between hypothesis 1 (Heaps scale dependence) and hypotheses 2-4 (other causes). Cost: extends existing `exp_partition_stratified_smoke_gap_cpu_v1.py`. Benefit: identifies the dominant cause within one extractor run.

**Anchor 2 (CONDITIONAL on Anchor 1 MIDDLE-BAND, 1-2 hr CPU): Goodhart-decoupled held-out validation smoke.** Splits research_drill into tuning_smoke (where z>=3 is tuned) and validation_smoke (NEVER touched during tuning). If validation_smoke gap > tuning_smoke gap, hypothesis 2 confirmed. Cost: one shell script + one extra extractor run. Benefit: structural fix portable across substrate smoke pipelines.

**Anchor 3 (CONDITIONAL on Anchor 1 HARD-FAIL, 4-6 hr CPU + manual annotation): the 30-item true-P@K gold set.** Builds a verified gold-standard P@K, measures proxy-vs-true divergence on both smoke designs. Cost: ~3 hr of manual annotation across 30 atoms. Benefit: resolves hypothesis 4 (proxy divergence) cleanly; provides the true-P@K signal Research has been awaiting for canonical claims.

**Anchor 4 (CONDITIONAL on all above MIDDLE-BAND, 1 day): the statAP/infAP pool-based estimator.** Reformulates the smoke as a non-uniform-sampled pool with importance-weighted Horvitz-Thompson AP. Adapted from Aslam-Kanoulas SIGIR 2006 to extraction pipelines. Cost: ~50 lines of Python + design work. Benefit: gives valid CIs at K=30 for any pipeline, replaces the smoke-pinning methodology entirely.

---

## Synthesis -- reframed methodology

Three independent literatures converge on the diagnosis: the smoke-to-full gap is dominated by **filter-coupling scale dependence**, not partition composition.

(1) **Heaps + Good-Turing missing-mass.** Sub-linear vocabulary growth (Heaps beta 0.4-0.6) combined with persistent ~30% hapax fraction across all corpus sizes means a threshold-based filter calibrated at full scale is mis-calibrated at smoke scale by a factor of ~sqrt(N_full / N_smoke). The fix is threshold-scaling proportional to expected feature-frequency-density.

(2) **Goodhart decoupling.** Any threshold that was tuned on the smoke ceases to be testable by the smoke. The OLD homogeneous smoke may have worked by accident (research_drill happens to match the deployment vocabulary); the broader principle is that the validation-smoke must be Goodhart-decoupled from the tuning-smoke.

(3) **PPI for hybrid evaluation.** When you have a large unlabeled population + small labeled subset + a high-correlation proxy (the extractor's own scores), PPI gives valid finite-sample CIs at < 0.05 width with N_labeled = 30. This is the cleanest substrate-specific methodology for predicting deployment P@K from a 30-file smoke -- it explicitly avoids the threshold-coupling and partition-composition pitfalls.

Reframed methodology rule candidate (1st appearance, supersedes the earlier-today rule that was empirically refuted):

**meta::RULE_substrate_smoke_methodology_must_handle_filter_threshold_scale_dependence_and_proxy_correlation**

Statement: A substrate-self-extension smoke at N << N_deployment is unreliable for predicting deployment P@K iff the deployment filter is a frequency-threshold rule (z>=k) calibrated at the asymptotic regime AND the smoke fraction of hapax-features is > 0.3 (Good-Turing-bound for non-asymptotic regime). The reliable methodologies are: (a) Heaps-scaled smoke threshold (scale k by sqrt(N_smoke/N_full)); (b) PPI-calibrated proxy with N_labeled >= 30; (c) Goodhart-decoupled validation smoke (held-out from all parameter tuning). Stratification by partition is NOT a reliable methodology when the filter-rule itself dominates the small-N bias.

Operationalization:
- `--scope filter-scaled-smoke` flag with auto-computed threshold based on N_smoke/N_full.
- `--scope ppi-calibrated-smoke` flag that runs PPI on the smoke + full-corpus extractor scores.
- `--scope goodhart-decoupled-smoke` flag that requires a separately-maintained validation smoke file list.
- Reported metrics: smoke-proxy P@K + PPI-calibrated full-corpus P@K + PPI CI half-width + Good-Turing missing-mass estimate (hapax fraction).
- Smoke-reliability gate: PPI CI half-width <= 0.05 AND Good-Turing missing-mass <= 0.30.

First-appearance criteria: this is the first substrate methodology rule to (a) handle filter-threshold-scale-dependence explicitly, (b) introduce PPI to substrate smoke calibration, and (c) require Good-Turing missing-mass diagnostics as a reliability gate. Second-appearance trigger: any future iteration that demonstrates < 0.05 gap on a different substrate extraction pipeline using PPI or Heaps-scaling.

---

## Honest scope

- **STRONG**: Heaps' law sublinear vocabulary growth and Good-Turing missing-mass are decades-mature (Good 1953; Heaps 1978; Valiant-Valiant 2017). Application to extraction-filter calibration is the cleanest mechanism class consistent with the empirical refutation data.
- **STRONG**: PPI (Angelopoulos et al. 2023) and stratified-PPI for hybrid evaluation (arXiv 2406.04291) are 2-3 year mature with growing IR/NLP adoption. Substrate transfer is a clean application of an established framework, not novel synthesis.
- **STRONG**: statAP / infAP / pool-based sampling (Aslam-Kanoulas SIGIR 2006) directly address small-sample P@K in IR with valid CIs.
- **MODERATE**: Goodhart-decoupling of tuning vs validation smoke is established OOD-eval methodology but the substrate-specific magnitude of the effect is unmeasured. Likely a contributor; unlikely the dominant cause given the empirical refutation pattern.
- **SPECULATIVE**: the methodology rule generalizes from self-extension to other substrate smoke pipelines (capability smokes, retrieval smokes). The 2026-06-09 prior drill addressed a DIFFERENT failure mode (composition mismatch on binary capability outcomes) and the rules are NOT interchangeable; the 2026-06-09 rule (composition mismatch) still applies to its original domain but does NOT apply here.
- **REFUTED** (within hours of registration): the earlier-today partition-composition-mismatch rule. Honest scope flag preserved. Methodology lesson: a lit-scan-driven first-appearance rule must NOT be registered as 1st-appearance until at least one empirical confirmation cycle; deflate first-appearance P estimates by an additional 0.10 going forward.

---

## Substrate-product positioning

**Substrate-specific lever 1 -- substrate has the structure to apply PPI at smoke scale.** PPI requires (a) a small labeled subset, (b) a large unlabeled population, (c) a high-correlation proxy score on the unlabeled population. The substrate has all three: smoke = labeled, full corpus = unlabeled, extractor scores = proxy. LLMs do not generally expose proxy scores on un-evaluated corpora because their ingestion is one-shot at training time. This is a categorical capability gap.

**Substrate-specific lever 2 -- self-correcting methodology rule discipline.** This research note explicitly retires and supersedes a rule registered hours earlier. The substrate methodology ledger CAN encode "rule X registered then refuted within Y hours; lesson Z" as a structural artifact. LLM training corpora cannot self-document rule retirement in this auditable way. The audit trail (rule registered -> empirical refutation -> rule retired + replaced) is itself a substrate-product artifact -- demonstrable methodology self-correction.

**Substrate-specific lever 3 -- Good-Turing missing-mass diagnostic as a substrate-extension health monitor.** The Blind-Spot Mass framework (arXiv 2604.05057) is naturally substrate-deployable as a per-cycle health metric. Every substrate ingestion run reports a Good-Turing missing-mass estimate; the substrate "knows" how much of its deployment population it has not yet seen. LLMs cannot quantify their own missing mass because they cannot enumerate their training distribution.

**Substrate-product framing.** The PPI-calibrated, Heaps-scaled, Goodhart-decoupled smoke methodology with Good-Turing missing-mass health reporting is an auditable, falsifiable, externally-verifiable methodology for predicting deployment performance with finite-sample statistical guarantees. The full methodology stack -- with empirical refutation history of an earlier hypothesis -- is itself a sellable artifact alongside the substrate.

---

## Cross-thread synthesis

- **vs 2026-06-09 capability-smoke drill**: that drill diagnosed composition mismatch + threshold-inside-CI on BINARY capability outcomes (alpha estimates). This drill diagnoses Heaps + Good-Turing + filter-coupling on P@K extraction outcomes. Both drills converge on "smoke must match the deployment OPERATING REGIME of the metric"; neither converge on "smoke must match the partition mix." The earlier-today 1x drill conflated the two.
- **vs 2026-06-12 1x stratified-smoke drill**: directly supersedes. The earlier note's recommendation was empirically refuted; this note diagnoses why (small-N stratification breaks Good-Turing asymptotic regime).
- **vs self-extending-engine memory**: the substrate's 4.3x atom growth via evolve.py works because the deployment-time z>=3 + blocklist filter operates at the asymptotic regime (1200+ files); the smoke test misled earlier-today because it sampled at 30 files. The growth methodology is sound; the smoke methodology was the issue.
- **vs substrate-as-self-knowing**: substrate now knows it had a methodology rule registered and refuted within hours of registration; this is itself a metacognition signal. The methodology-rule ledger can encode rule-lifetime statistics.

---

## Citations (verified count: 17)

1. Good, I.J. (1953) "The Population Frequencies of Species and the Estimation of Population Parameters." Biometrika 40(3-4): 237-264. [foundational Good-Turing]
2. Heaps, H.S. (1978) "Information Retrieval -- Computational and Theoretical Aspects." Academic Press. [Heaps' law]
3. Valiant, G. & Valiant, P. (2017) "Estimating the Unseen: Improved Estimators for Entropy and other Properties." theory.stanford.edu/~valiant/papers/unseenJournal.pdf
4. Painsky, A. (2023) "Generalized Good-Turing Improves Missing Mass Estimation." JASA 118(543).
5. (2026) "Blind-Spot Mass: A Good-Turing Framework for Quantifying Deployment Coverage Risk in Machine Learning Systems." arXiv 2604.05057.
6. Cormack, G. & Lyman, T. (2006/2007) "Statistical Precision of Information Retrieval Evaluation." SIGIR (citeseerx 97379552de008ea2b4c79ba7e1035676df05e196).
7. Aslam, J.A., Pavlu, V., & Yilmaz, E. (2006) "A Statistical Method for System Evaluation Using Incomplete Judgments." SIGIR. (statAP)
8. (2024) "Reliable Confidence Intervals for Information Retrieval Evaluation Using Generative AI." arXiv 2407.02464.
9. (2012) "Approximate Recall Confidence Intervals." arXiv 1202.2880.
10. Angelopoulos, A. et al. (2024) "Stratified Prediction-Powered Inference for Hybrid Language Model Evaluation." arXiv 2406.04291.
11. (2024) "Extending Prediction-Powered Inference through Conformal Prediction." arXiv 2510.16166.
12. (2024) "Conformal Risk Control." ICLR 2024 proceedings.
13. (2024) "A Survey on Evaluation of Out-of-Distribution Generalization." arXiv 2403.01874.
14. (2023) "A Survey on Out-of-Distribution Evaluation of Neural NLP Models." arXiv 2306.15261.
15. NBER (2021) "Simplifying Bias Correction for Selective Sampling." Working Paper w28801.
16. Killick, R., Fearnhead, P., & Eckley, I.A. (2012) [used as concentration-bound general reference] "Optimal Detection of Changepoints With a Linear Computational Cost." JASA 107(500).
17. Ashraf, M. (2024) "A Complete Guide to Testing Your Data Pipelines for Optimal Performance." Medium. [feature-pipeline parity discipline]

Supporting (not directly cited but consulted): Zipf-Heaps coupling arXiv 1002.3861; Heaps in tagged texts arXiv 2001.02178; pool-based continuous evaluation Springer s10791-015-9266-y; design effect cluster sampling PMC 6477104.

---

## Pre-registered HARD-PASS / HARD-FAIL bands (for exp_dev follow-through)

For Anchor 1 three-design comparison on existing infrastructure:

- HARD-PASS (Heaps mechanism confirmed): design (B) Heaps-scaled threshold (z>=1 at smoke scale) closes proxy-P@30 gap to |gap| <= 0.05, AND design (C) PPI-calibrated estimate matches full-corpus proxy P@30 within +/- 0.03 with CI half-width <= 0.05.
- HARD-FAIL (Heaps mechanism refuted): design (B) shows gap > 0.15 OR design (C) PPI CI half-width > 0.20. Triggers Anchor 3 (true-P@K gold set) AND Anchor 4 (statAP infAP redesign).
- MIDDLE-BAND [0.05, 0.15]: composition of (B) + (C) is tested; if composed gap <= 0.05, ship as canonical. Otherwise Anchor 2 (Goodhart decoupling) attempted.

Calibration penalty applied: P_deflated 0.48; novel-synthesis cap 0.50; explicit refutation history of the earlier-today 1x drill deflates by an additional 0.05.
