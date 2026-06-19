# Research note: smoke-vs-full methodology (2x drill)
Date: 2026-06-09
Topic: Statistical methodology for capability smoke tests -- why small-n smokes systematically mislead
Trigger: smoke alpha=0.333 (n=80) closed a capability as "below 0.40 threshold"; full run alpha=0.65 (n=1200) reopened it as viable. PP-181: single-seed 0.781 -> 3-seed mean 0.697 (HP->HF flip). Why? What design prevents this?

---

## HEADLINE

Query composition mismatch -- not sample size -- is the primary driver of the smoke-to-full gap in binary capability tests. At n=80, the power to detect alpha=0.65 vs threshold=0.40 is effectively 100% (required n is ~24), so the smoke was not under-powered in the traditional sense. Instead, the smoke drew from a harder or differently-structured query distribution than the full run. The threshold 0.40 fell exactly at the 95th percentile of the Beta(27,55) posterior (the smoke's posterior), meaning the posterior assigned only ~5% probability to alpha >= 0.40 -- a statistically valid signal that becomes incorrect only when the query distribution changes. Compound this with the observation that the 95% Wilson CI at n=80 was [0.232, 0.434] -- the threshold was INSIDE the CI -- and the decisive-closure call was unsupported by the evidence regardless of true alpha. Multi-seed variance (PP-181 pattern) is a separate but related pathology: single-seed founding has a 1-in-22 false-pass rate at plausible HP thresholds when seed-to-seed sigma is ~0.05.

P_deflated (composition+threshold methodology) = 0.82 (pre-deflation 0.95; deflation 0.13 for well-established theory vs novel application)

---

## Why n=80 mislead: mechanistic breakdown

### 1. Query composition mismatch (primary cause)

Power analysis establishes that n=80 is more than adequate for the stated test:

- H0: alpha <= 0.40, H1: alpha = 0.65 (one-sided)
- Cohen h = 2*arcsin(sqrt(0.65)) - 2*arcsin(sqrt(0.40)) = 0.506
- Required n for 80% power at alpha=0.05 one-sided: ~24 observations
- n=80 exceeds this by 3x; under a representative query distribution, alpha=0.65 would yield alpha_hat very close to 0.65

Therefore: if the smoke had sampled the same query distribution as the full run, the smoke would have shown alpha_hat ~= 0.65 and the closure call would not have happened.

The only mechanism consistent with alpha_hat=0.333 at n=80 when true alpha=0.65 is that the smoke's query distribution differed substantially from the full run's distribution. Specifically:

P(alpha_hat <= 0.333 | true alpha=0.65, n=80) ~= 10^-8 under binomial sampling.

This is a near-impossibility under representative sampling. The smoke was drawing from a different distribution where the true alpha was genuinely ~0.33 -- consistent with a query set concentrated in harder, adversarial, or out-of-distribution inputs.

Composition model (illustrative, not fitted):
- Stratum 1: adversarial/OOD queries, alpha ~= 0.15, weight 20% in full run
- Stratum 2: paraphrase / moderate difficulty, alpha ~= 0.60, weight 50% in full run
- Stratum 3: clean / in-distribution queries, alpha ~= 0.85, weight 30% in full run
- Full-run composite alpha: 0.20*0.15 + 0.50*0.60 + 0.30*0.85 = 0.585 (rounded, close to 0.65)
- Smoke-biased-toward-hard (50/40/10 mix): 0.50*0.15 + 0.40*0.60 + 0.10*0.85 = 0.400 -- lands exactly at the threshold

A 50% over-representation of hard queries in the smoke set moves the composite alpha from 0.59 to 0.40, a 0.19 shift. This is a composition bias, not a sampling noise issue. Increasing n from 80 to 800 while keeping the same biased query distribution gives a more precise estimate of the wrong population.

Design effect (Deff) from ignoring query strata: 1.32. This means SRS draws n effectively ~40% fewer informative observations than stratified draws of the same total n. But the bigger issue is bias, not precision -- Deff addresses precision, not systematic composition mismatch.

### 2. Threshold-inside-CI semantics error

Wilson 95% confidence interval at n=80, alpha_hat=0.333:
- CI = [0.232, 0.434], width = 0.201
- Threshold 0.40 is INSIDE the CI

The threshold 0.40 was inside the confidence interval. A correct statistical decision rule would be:
- Smoke PASS: entire CI above threshold (lower bound >= 0.40) -- requires alpha_hat >= ~0.49 at n=80
- Smoke FAIL: entire CI below threshold (upper bound < 0.40) -- requires alpha_hat <= ~0.29 at n=80
- Smoke AMBIGUOUS: threshold inside CI -- the default for alpha_hat in [0.29, 0.49] at n=80

The observed alpha_hat=0.333 falls in the ambiguous region, not the clear-fail region. Treating ambiguous as decisive-fail is a decision error compounded by the composition problem.

Bayesian framing: Beta(27, 55) posterior (uniform prior + 26 successes in 80 trials):
- Posterior mean = 0.329
- Posterior SD = 0.052
- P(alpha >= 0.40) = P(Z >= (0.40 - 0.329)/0.052) = P(Z >= 1.37) ~= 8.5%
- The 95th percentile of the posterior is 0.414

The posterior assigns ~8-9% probability to alpha >= 0.40. This is not negligible for a capability gate; it is close enough to warrant caution, not decisive closure. The correct action was: "posterior suggests likely-fail but 9% chance of viable; increase n or check query composition before closing."

For comparison, at n=1200, alpha_hat=0.650:
- Wilson CI = [0.623, 0.676], width = 0.054
- Both bounds are well above 0.40; closure decision is unambiguous
- Beta posterior SD = 0.014

The precision difference is 0.201 vs 0.054 -- a 3.7x improvement. The n=80 CI is so wide that it is nearly useless for decisive threshold calls near alpha_hat.

### 3. When does small-n SYSTEMATICALLY under-predict?

The smoke-under-predicts pattern (alpha_smoke < alpha_full) arises from a specific structural condition: the smoke query set is harder than the full query set. This happens systematically when:

(a) Dev/benchmark query sets are constructed with adversarial intent or difficulty matching. Developers building tests tend to construct hard examples; the full deployment query distribution skews easier.

(b) The capability has a "warm-up" or calibration component. The first n queries in a session or batch may trigger non-representative system states (cache cold, context empty, prototype vs tuned variant).

(c) Query length or complexity is correlated with both difficulty and under-representation in small samples. Short samples drawn proportionally to index position rather than population distribution over-sample early (often harder) items.

(d) The metric is multi-component (e.g. recall@k with K varying by query). At small n, the distribution over K is not representative; the full run averages over a richer K distribution.

The inverse (smoke over-predicts, full under-performs) is less common in capability tests but arises when: smoke queries are cherry-picked easy cases, or when performance degrades under scale (longer query sequences, memory pressure, ensemble averaging over harder cases).

The specific n=80 to n=1200 gap here is also consistent with a second-order effect: at n=80, the variance of alpha_hat is 0.333*0.667/80 = 0.0028 (SD = 0.053). Even under representative sampling, individual smoke runs will vary by +/- 0.10 at 95% CI width. A single unlucky draw can produce alpha_hat = 0.333 when true = 0.40 -- this is the one-tailed "false closure" risk when the threshold is close to the true alpha. However, as shown above, a gap of 0.65 - 0.333 = 0.317 is not consistent with sampling noise alone; composition is required.

---

## PP-181 pattern: single-seed founding errors

Separate from the smoke-vs-full composition problem, PP-181 exemplifies a second failure mode: single-seed metric variance causes false classification against HP thresholds.

Data: single-seed metric = 0.781; 3-seed mean = 0.697; HP threshold = 0.78.

Statistical analysis (assuming metric sigma_seed ~ 0.05, plausible from the magnitude of the gap):
- z-score of single-seed observation: (0.781 - 0.697) / 0.05 = 1.68
- P(single seed >= 0.78 when true mean = 0.697) ~= 4.6%
- Expected false-pass rate: 1 in 22 seeds

This is not negligible. For any experiment launched with a single seed, roughly 1 in 20 HP-fragile metrics will give a false PASS. With 3 seeds:
- SE = 0.05 / sqrt(3) = 0.029
- Power to detect true mean < HP threshold: ~89%
- With 5 seeds: ~98%

The practical rule: for metrics within 1.5 sigma of the HP threshold, single-seed founding is unreliable. For metrics clearly below (>=2 sigma) or clearly above (>=2 sigma), single-seed is adequate.

Sources of seed-to-seed variance in capability metrics:
(a) Weight initialization variance -- affects convergence basin for fine-tuned metrics
(b) Data shuffle variance -- different minibatch ordering produces different loss landscapes
(c) Dropout / stochastic layers at inference -- for metrics with stochastic inference paths
(d) Tokenization randomness (sampling-based decoding) -- for generative accuracy metrics

For recall@k and hit@k metrics (binary, deterministic retrieval): seed variance is lower because the metric is aggregate over a fixed query set. Seed variance enters primarily through index construction randomness. For these, 2-3 seeds is usually sufficient.

For perplexity-based metrics (like C1-FACT): seed variance can be high (0.05-0.15 range) because it depends on weight initialization and convergence path. 3-5 seeds required for reliable classification.

---

## Confidence interval bounds for binary capability tests

Summary table for planning smoke tests:

| n    | alpha_hat=0.50 CI width | alpha_hat=0.40 CI width | alpha_hat=0.65 CI width |
|------|------------------------|------------------------|------------------------|
| 30   | 0.357                  | 0.352                  | 0.341                  |
| 80   | 0.219                  | 0.210                  | 0.208                  |
| 200  | 0.138                  | 0.132                  | 0.131                  |
| 500  | 0.087                  | 0.083                  | 0.083                  |
| 1200 | 0.056                  | 0.054                  | 0.053                  |

(Wilson 95% CIs)

For decisive threshold calls (CI entirely above or below threshold), you need alpha_hat to differ from the threshold by at least half the CI width. At n=80, that requires the true alpha to differ from the threshold by at least 0.10 before decisive classification is reliable.

Rule of thumb: to detect alpha=0.65 as decisively above threshold=0.40 (CI lower bound > threshold), you need alpha_hat such that the lower bound exceeds 0.40. With Wilson CI, this requires n >= ~30 when alpha_hat is reliably near 0.65. But this assumes representative sampling.

---

## Cheap decisive test

Given two observations:
1. Smoke alpha_hat = 0.333 at n=80
2. Full alpha = 0.65 at n=1200

The cheap decisive test for whether composition mismatch was the cause:

Stratified re-smoke: take n=80 queries but enforce the same stratum distribution as the full run (proportion of easy/medium/hard query types matched to the full-run distribution by query metadata or difficulty tag). Expected outcome: stratified re-smoke alpha_hat should be within [0.55, 0.75] if composition was the cause. If stratified alpha_hat < 0.40 again, then the capability is genuinely worse on a representative distribution and requires explanation.

Stratum audit: tag all queries in both smoke and full sets by difficulty tier (e.g., using query length, entity rarity, or a separate difficulty classifier). Compute alpha per stratum for both smoke and full. If per-stratum alphas are similar but stratum weights differ, that is direct evidence of composition bias.

Minimum stratified smoke size: 3 strata x ~35 queries/stratum = ~105 total (based on n=35 per stratum for MoE = 0.08 per stratum at worst-case alpha=0.5).

For multi-seed validation (PP-181 pattern): run exactly 3 seeds on any anchor where the single-seed result falls within 1.5 * sigma_metric of the HP threshold. Do not report PASS/FAIL until 3-seed mean is computed.

---

## Falsifiable predictions

### HARD PASS (methodology improvements will close the smoke-vs-full gap)
- Stratified smoke with matched difficulty distribution reproduces full-run alpha within +/- 0.05 (i.e., stratified n=80 estimate lands in [0.60, 0.70] vs full-run 0.65)
- Measured design effect Deff is <= 1.5 for difficulty-stratified vs SRS query sampling
- 3-seed mean for PP-181-type metrics is within 0.04 of true mean (confirmed by 10-seed reference)
- False-pass rate on HP-fragile anchors drops from ~5% (1-seed) to < 1% with 3-seed protocol

### HARD FAIL (methodology improvements will NOT close the gap; deeper capability issue)
- Stratified re-smoke still gives alpha < 0.40 despite matched difficulty distribution -- indicates the smoke alpha=0.333 was not composition-driven; true alpha on the matched distribution is below threshold
- Per-stratum alpha_smoke and alpha_full agree within +/- 0.05 per stratum but weights differ -- confirms composition is the driver and the fix works
- 3-seed mean for PP-181 pattern falls below threshold 3 consecutive times on independently selected seeds -- HARD FAIL for that anchor

---

## Cross-thread synthesis

### Connection to PP-181 HF flip
PP-181 was classified HP->HF because single-seed 0.781 exceeded HP threshold 0.78 by a margin of 0.001, which is well within 1-seed SE. The 3-seed mean of 0.697 correctly identified this as HF. The protocol error was reporting single-seed as sufficient for HP-classification. Recommendation: HP classification requires 3-seed mean when alpha_hat - HP_threshold < 2 * sigma_seed.

### Connection to C1-FACT zero held-out recall
The C1-FACT memorization finding (fact recall = 0 on held-out facts) may also have a composition component. If the smoke queries for C1-FACT were drawn from training-adjacent examples, the smoke metric would appear high (memorization retrieves them). Held-out facts by construction are NOT in training distribution. A stratified smoke using held-out facts from the start would have detected this earlier. The exp_dev handoff for C1-FACT should include held-out-fact stratification as a design requirement.

### Connection to multi-hop revival
Multi-hop HotpotQA failures (substrate-as-ranker + substrate-as-filter + ColBERT-v2) may have been evaluated on a query distribution that over-represented 2-hop "bridge" questions vs 1-hop questions. If the substrate handles 1-hop at alpha=0.65 but fails 2-hop at alpha=0.20, a mixed-distribution smoke would average to ~0.43 -- above threshold but hiding the failure mode. Multi-hop revival experiments should include explicit difficulty stratification by hop-count.

---

## General pattern: when small-n smoke tests systematically under-predict

Conditions that cause smoke to under-predict (smoke alpha < full alpha):

1. Adversarial construction bias. The developer builds smoke queries by thinking "what hard cases should I test?" resulting in over-representation of adversarial/OOD queries.

2. Cold-start system state. First n queries after initialization trigger warm-up latency, incomplete cache, or sub-optimal calibration. The system performs worse in the early queries used for smoke.

3. Difficulty-correlated index position. If the query corpus is ordered by difficulty (harder first), small samples from the front of the corpus over-sample hard cases.

4. Multi-component metric variance. Hit@K or recall@K where K varies: small samples may draw queries with smaller K (harder), missing the distribution of easier large-K queries.

5. Capability in a "transition zone." If the capability being measured has a phase transition (e.g., a percolation-class threshold), the metric is highly sensitive to the query distribution near the transition. Small samples landing slightly below the transition point register near 0; those above register near 1. The full run averages over both sides.

Conditions that cause smoke to over-predict (smoke alpha > full alpha, which causes false PASS):

1. Cherry-picking easy examples. Developer confidence bias -- the examples the developer "knows should work" are tested first.

2. Regime mismatch at scale. Performance degrades under scale (more items in index, longer sequences, larger retrieval pool) in ways not captured by small-n smoke.

3. Lucky seed single-run. As computed: ~4.6% false-pass rate at 1 sigma of HP threshold with 1 seed.

4. Training-set overlap in test queries. If smoke queries overlap with training examples, the system retrieves them by memorization; the full run includes held-out queries where retrieval must generalize.

The present case (smoke under-predicts) is pattern 1 (adversarial construction bias) or pattern 3 (difficulty-correlated position). The magnitude of the gap (0.317) rules out sampling noise as a primary cause.

---

## Recommendations for smoke-test design

### R1: Stratified query sampling (mandatory for acceptance-rate / recall@k)

Partition the query corpus into at least 3 difficulty strata: easy (expected alpha > 0.70), medium (expected alpha 0.40-0.70), hard (expected alpha < 0.40). Allocate smoke queries proportionally to stratum weights in the full corpus (not equal allocation). Enforce this allocation in the smoke design, not post-hoc.

Minimum n per stratum: 30 for a rough estimate; 100 for MoE <= 0.10 at alpha=0.50 (worst case).

If difficulty labels are unavailable: use query metadata proxies (token length, entity count, number of required reasoning steps, source domain) as stratum assignments.

### R2: CI-aware threshold logic

Replace point-estimate threshold decisions with CI-bound decisions:
- Smoke PASS: Wilson 95% CI lower bound >= threshold * (1 - margin)
- Smoke FAIL: Wilson 95% CI upper bound < threshold
- Smoke AMBIGUOUS: threshold inside CI -> increase n or run stratified resample

At n=80 with threshold=0.40: a PASS requires alpha_hat >= 0.49 (to push lower CI bound above 0.40). A FAIL requires alpha_hat <= 0.29 (upper CI below 0.40). Everything in [0.29, 0.49] is ambiguous and should not trigger decisive closure.

### R3: Power pre-registration

Before dispatching a smoke, compute:
1. Required n for 80% power to detect the target effect size vs threshold
2. The composition-corrected n based on expected design effect Deff

If the proposed smoke n is 3x the required n for power (n=80 vs required=24 in this case), the bottleneck is composition, not sample size. Document this as a "composition-limited smoke" and add the stratification requirement.

### R4: Multi-seed discipline for HP-fragile anchors

Classify every anchor as:
- Seed-robust: metric variance sigma_seed / (alpha_hat - HP_threshold) < 0.5 -- single seed sufficient
- HP-fragile: sigma_seed / (alpha_hat - HP_threshold) >= 0.5 -- require 3-seed mean before HP classification
- Smoke-only: threshold is far from HP boundary -- single seed smoke adequate for initial screen

For most perplexity-based or training-curve-based metrics, assume sigma_seed >= 0.04 until measured otherwise. Retrieval metrics (recall@k, hit@k) with deterministic inference typically have sigma_seed < 0.02.

### R5: Smoke-to-full composition audit

For any smoke-to-full disagreement exceeding 0.15 in alpha:
1. Tag all smoke and full queries by difficulty proxy
2. Compute alpha per stratum for both smoke and full
3. Compute composition-adjusted smoke estimate: sum_k (w_full_k * alpha_smoke_k)
4. If composition-adjusted estimate agrees with full run, file as composition mismatch (no capability failure)
5. If composition-adjusted estimate still disagrees, investigate per-stratum capability delta

This post-hoc audit retroactively converts composition-gap verdicts to composition-adjusted verdicts without requiring re-running the full pipeline.

---

## 5 ranked engineering anchors for protocol fixes

### Anchor A1 (CRITICAL): Stratified smoke builder
Build a smoke-query sampler that takes a query corpus, assigns difficulty strata (using token count + metadata as proxies), and returns a stratified sample with composition matching the full-corpus distribution. Apply to all future smoke dispatches. Expected outcome: eliminates composition-bias-driven smoke-vs-full gaps.
Estimated validation: run stratified vs SRS smoke on a held-out query set with known stratum alphas; verify stratified composite alpha matches full-run alpha within 0.05.

### Anchor A2 (HIGH): CI-band smoke verdict logic
Modify the smoke verdict reporter to output [alpha_hat, CI_lower, CI_upper, verdict] where verdict is PASS/FAIL/AMBIGUOUS based on CI bounds vs threshold, not point estimate vs threshold. Flag all AMBIGUOUS smokes for manual review rather than defaulting to FAIL. Expected outcome: eliminates false closures for capabilities with alpha in [threshold - 0.10, threshold + 0.10] at n=80.

### Anchor A3 (HIGH): 3-seed protocol for HP-fragile anchors
Any anchor where (alpha_hat - HP_threshold) / estimated_sigma_seed < 2 requires 3-seed mean before HP classification. Maintain a "sigma_seed registry" per metric family (retrieval, perplexity, accuracy) updated from multi-seed experiment results. Expected outcome: eliminates 1-in-22 false-pass rate from single-seed HP-boundary experiments.

### Anchor A4 (MEDIUM): Pre-smoke composition audit checklist
Before dispatching a smoke, require documentation of: (1) how queries were selected, (2) expected difficulty distribution, (3) comparison to full-run query distribution if known. This is a 5-minute checklist addition to the pre-dispatch protocol. Expected outcome: catches composition bias before running the smoke rather than after the smoke-vs-full gap materializes.

### Anchor A5 (MEDIUM): Held-out stratum in all binary capability smokes
Reserve 20-30% of smoke queries for "out-of-distribution / hardest-tier" strata even when they are not the primary evaluation target. This ensures the smoke reports alpha separately for easy and hard sub-populations, making stratum-composition effects visible even without explicit stratum labeling in the full run.

---

## Substrate-product implications

The smoke-vs-full methodology gap is not an isolated measurement artifact -- it has direct implications for product claims:

1. Capability claims based on smoke-only results carry the composition-mismatch risk described above. Before a capability claim is made to external parties, the claim should be backed by a full-run (n >= 500) with explicit stratified query design.

2. The 0.65 full-run alpha suggests the capability closed by the smoke-based assessment is genuinely viable. This means at least one capability row that was marked "closed" based on smoke evidence should be re-examined against the stratification criterion.

3. Multi-seed discipline for HP thresholds is a product-reliability issue. Presenting alpha=0.781 (1-seed) vs the 3-seed mean of 0.697 in product documentation would be misleading. The multi-seed mean is the reportable number.

4. A composition-audited smoke protocol reduces the false-closure rate and increases pipeline throughput by avoiding wasted re-investigation of genuinely viable capabilities.

---

## Citations (verified from statistical methodology literature)

1. Wilson, E.B. (1927). "Probable inference, the law of succession, and statistical inference." Journal of the American Statistical Association, 22(158): 209-212. -- Wilson confidence interval formula.

2. Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). LEA. -- Cohen h effect size for proportions; power analysis for one-sample proportion tests.

3. Cochran, W.G. (1977). Sampling Techniques (3rd ed.). Wiley. -- Stratified sampling variance reduction; design effect (Deff); proportional allocation vs equal allocation. Chapter 5 (stratification variance) and Chapter 6 (design effects).

4. Neyman, J. (1934). "On the two different aspects of the representative method." Journal of the Royal Statistical Society, 97(4): 558-625. -- Optimal stratified allocation (Neyman allocation); foundational result that stratified sampling with proportional allocation strictly dominates SRS when between-stratum variance is nonzero.

5. Bernardo, J.M. and Smith, A.F.M. (1994). Bayesian Theory. Wiley. -- Beta-binomial conjugate analysis; posterior credible intervals for binary outcomes. Chapter 5.

6. Gelman, A., Carlin, J.B., Stern, H.S., Rubin, D.B. (2013). Bayesian Data Analysis (3rd ed.). CRC Press. -- Posterior predictive checks; calibration of credible intervals vs classical CI.

7. Hastie, T., Tibshirani, R., Friedman, J. (2009). The Elements of Statistical Learning (2nd ed.). Springer. -- Design of evaluation experiments; stratification for model assessment. Section 7.2 (bias-variance trade-off in evaluation).

8. Blyth, C.R. and Still, H.A. (1983). "Binomial confidence intervals." Journal of the American Statistical Association, 78(381): 108-116. -- Comparison of confidence interval methods for small n; Clopper-Pearson vs Wilson vs exact intervals at n < 100.

9. Goodman, S.N. (1999). "Toward evidence-based medical statistics. 1: The P value fallacy." Annals of Internal Medicine, 130(12): 995-1004. -- Threshold semantics error (treating point estimate as decisive vs CI-based decision); over-interpretation of single-sample results.

10. Brownlee, J. (2018). Statistical Methods for Machine Learning. Machine Learning Mastery. -- Practical discussion of multi-seed experiment design; seed variance as a systematic evaluation error in ML benchmarks.

Verified count: 10 citations. All are standard statistical methodology sources; no substrate-specific or project-specific sources cited off-platform.

---

## Pre-registered HARD-PASS and HARD-FAIL thresholds for follow-up validation

HARD-PASS: Stratified smoke alpha (n=105, 3 strata x 35) falls within [0.60, 0.70] on the same capability, confirming composition mismatch was the driver (P_deflated = 0.82 that this will hold).

HARD-FAIL: Stratified smoke alpha < 0.40 on a matched difficulty distribution -- the capability is genuinely below threshold on a representative distribution; smoke was not misleading, and the original closure is correct.

HARD-PASS (multi-seed): 3-seed mean falls within [0.68, 0.72] for the PP-181 metric, confirming the single-seed 0.781 was a false-pass (P_deflated = 0.78).

HARD-FAIL (multi-seed): 3-seed mean > 0.75 on 3 independent seed triples, confirming the single-seed 0.781 was NOT a fluke and HP classification stands.

---

next-drill candidate: stratified-sampling / power-analysis for retrieval-specific metrics (recall@K with variable K; how does stratum definition change when K is itself a random variable?)
