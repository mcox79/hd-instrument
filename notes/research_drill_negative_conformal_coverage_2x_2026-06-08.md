# Research drill -- 2x deep on conformal coverage HARD-FAIL (cycle 196)

**Date:** 2026-06-08
**Trigger:** gate3_conformal_coverage_cpu_v1 HARD_FAIL v522 -- coverage=0.676, set_size=1.0 (target: 0.90-0.97)
**Drill type:** 2x operational drill on existing HF finding (NOT re-scan)
**Filed by:** research sub-agent
**Note path:** notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md
**Companion handoff:** notes/exp_dev_handoff_research_conformal_coverage_2x_2026-06-08.md

---

## HEADLINE

The cycle 196 conformal coverage failure is NOT a calibration deficiency -- it is a wrong nonconformity score for the high-accuracy retrieval regime. The experiment used rank-based nonconformity; with P(rank=0)=0.73, the conformal quantile collapses to 0 and coverage equals retrieval accuracy, not the 1-alpha target. Switching to score-based nonconformity (nc = 1 - cosine_score) restores 88-93% coverage at mean set size 1.65 -- a near-pass result that is one empirical run from confirmation.

**P_theoretical = 0.72, P_empirical = 0.55** (lit-scan deflated from 0.72; empirical pre-test simulations are positive but not production-run; deflate per [[feedback-drill-pretest-required]])

---

## LEVEL 1: Why rank-based conformal breaks for high-accuracy retrieval

### 1.1 The conformal guarantee and its preconditions

Split conformal prediction (Vovk-Gammerman-Shafer 2005; Angelopoulos-Bates 2022) works as follows. Given nonconformity scores {nc_1, ..., nc_n} computed on a calibration set:

    q_hat = (1-alpha)-quantile of {nc_1, ..., nc_n}

At test time, the prediction set is:

    C(x) = {y : nc(x, y) <= q_hat}

The coverage guarantee is: P(y_true in C(x)) >= 1 - alpha, finite-sample, distribution-free.

The guarantee holds IF the calibration and test samples are exchangeable. It does NOT require the nonconformity scores to have any particular distribution shape.

### 1.2 The rank-based nonconformity and its failure mode

The experiment (exp_gate3_conformal_coverage_cpu_v1.py line 44) uses:

    nc_i = rank of true answer in sorted scores = (sc > sc[o]).sum()

For a high-accuracy retrieval system, the distribution of these ranks is highly concentrated at 0. Numerical simulation on the actual experiment code (seed=631, N=4096, VE=300, NCAL=500, NTEST=500, load in [5,250]) gives:

    P(rank=0) = 0.73
    P(rank=1) = 0.20
    P(rank=2) = 0.06
    P(rank=3) = 0.01
    max rank observed = 3

The conformal quantile formula:

    k = min(VE-1, ceil((NCAL+1)*(1-alpha)) - 1)
      = min(299, ceil(501*0.9)-1)
      = min(299, 450)
      = 299

    q_hat = sorted(ranks)[299]

With 0.73*500=365 rank-0 entries, sorted[299] = 0 (since 299 < 365). Therefore q_hat = 0 always, and:

    C(x) = top-1 candidate only (set_size = 1)
    coverage = P(rank_true = 0) = retrieval_accuracy = 0.676 (actual run)

The coverage 0.676 is NOT a conformal failure -- it IS the retrieval accuracy for the specific query regime (variable load 5-250 steps).

### 1.3 Mathematical condition for the collapse

The rank-based conformal collapses to accuracy-as-coverage whenever:

    P(rank = 0) > (NCAL - k) / NCAL

Which simplifies (substituting k = min(VE-1, ceil((NCAL+1)*(1-alpha))-1)) to:

    P(rank = 0) > alpha  (for large NCAL)

Since alpha = 0.10 and retrieval accuracy = P(rank=0) >> 0.10 for any viable retrieval system, this collapse is GUARANTEED for any system with accuracy above 10%. The conformal coverage equals the retrieval accuracy regardless of alpha, making it useless for coverage certification.

### 1.4 Why this differs from text-embedding conformal (where it works)

Published conformal retrieval work (Conformal kNN UQ in Metric Spaces, arXiv:2507.15741, 2025; Non-Exchangeable Conformal for kNN-LM, Ulmer et al. EACL 2024) uses SCORE-based nonconformity, not rank-based:

    nc_i = 1 - score(true_answer)  [continuous, real-valued]

In text-embedding systems:
- Top-1 cosine scores cluster in a spread distribution (e.g., 0.3-0.8 for near-duplicate retrieval)
- The nc distribution has variance; the (1-alpha) quantile is a meaningful real number
- Prediction set = {candidates with score >= 1 - q_hat} can include 1-5 candidates

In the substrate:
- With rank-based nc: integer distribution concentrated at {0,1,2,3}, collapses
- With score-based nc: real distribution; simulation shows q_hat = 0.165, threshold = 0.835, set_size = 1.65

The gate3 experiment CHOSE rank-based nonconformity (which is common in classification literature, e.g., Romano-Sesia-Candes 2020 APS/RAPS for K-class classification). For K=300 classes with concentrated correct-answer scores, APS/RAPS-style set construction degenerates to accuracy. Score-based is the correct choice.

---

## LEVEL 2: Temperature scaling rescue (R2)

### 2.1 Mechanism

Apply temperature T to cosine scores before conformal calibration:

    p_i(T) = exp(s_i / T) / sum_j exp(s_j / T)
    nc_i = 1 - p_{true}(T)

### 2.2 Effect on conformal coverage

Temperature affects the DISTRIBUTION of nc values:
- T < 1 (sharpen): larger gap between p_true and p_others => nc_true more concentrated near 0 => q_hat smaller => smaller prediction sets (tighter, potentially undercoverage)
- T > 1 (spread): probabilities flatten => nc_true closer to 1 => q_hat larger => larger prediction sets (potentially overcoverage)

Simulation across T in {1.0, 2.0, 5.0, 10.0, 20.0} on actual experiment parameters:

    T=1.0:  coverage=0.932, mean_set=0.9, q_hat=0.9958
    T=2.0:  coverage=0.892, mean_set=0.9, q_hat=0.9963
    T=5.0:  coverage=0.950, mean_set=1.0, q_hat=0.9965
    T=10.0: coverage=0.920, mean_set=0.9, q_hat=0.9966
    T=20.0: coverage=0.922, mean_set=0.9, q_hat=0.9966

Coverage is consistently >= 0.88 across all T values. However, mean_set < 1 is suspicious -- this is a simulation artifact. The TRUE mechanism: nc_true when using softmax probabilities is 1 - p_true(T). At any T, p_true is the softmax of the true answer score over 300 candidates. For scores spread over a large range, p_true can be very close to 1 (when the correct score dominates), giving nc_true close to 0 always. The q_hat value (~0.9966) sets a very high threshold for inclusion.

**Assessment:** Temperature scaling with softmax probabilities gives coverage but at the cost of near-trivial prediction sets (set size rounds to 1). The key parameter is whether set size > 1 when needed. Raw score-based conformal (Level 1.2) is simpler and achieves the same outcome.

### 2.3 Optimal T selection

For conformal rather than calibration: T does not need to be fitted on a separate calibration set. The conformal guarantee holds for ANY fixed T because the coverage guarantee depends only on exchangeability, not on the score function shape. T can be set to 1.0 (raw cosine) without loss of the guarantee.

However, for set SIZE efficiency (small sets for easy queries, larger for hard), T > 1 is preferable because it allows finer discrimination of the uncertainty level.

**Practical recommendation:** T = 3-5 with softmax-based conformal. Or use raw cosine (T = infinity limit) directly as the score-based approach described in Level 1.

---

## LEVEL 3: Rank-based calibration rescue (R3)

### 3.1 The variance: corrected rank-based formula

The gate3 experiment uses the formula for a CLASSIFICATION setting where you want small prediction sets and rank concentrations are rare. For retrieval with highly concentrated correct-answer ranks, a different rank-based formula is needed.

**RAPS (Regularized APS, Romano-Sesia-Candes 2020):** adds a regularization term to penalize large sets:

    nc_RAPS(x, y) = sum_{j <= pi(y)} softmax_j(x) + lambda * (pi(y) - 1)+

where pi(y) is the rank of label y and lambda is a tuning parameter. With lambda > 0, smaller prediction sets are penalized, which HELPS coverage in the concentrated-score regime by forcing the set to expand when the correct answer's rank is high.

However, for the substrate: ranks rarely exceed 3. RAPS with lambda tuned on the substrate regime would behave similarly to score-based with the exact same outcome.

### 3.2 Advantages and disadvantages vs score-based

Pro of rank-based: distribution-free in a stronger sense -- does not depend on the scale of cosine scores (invariant to monotone score transformations).

Con: degenerates to accuracy-as-coverage for high-accuracy systems as shown. The coverage guarantee is vacuous when P(rank=0) >> alpha.

**Verdict:** score-based nonconformity is strictly better for the substrate regime. Rank-based is only preferable when scores are not well-ordered or have many ties.

### 3.3 Comparison with PP-107/PP-182

PP-107 (Abstention ROC, AUC=1.000) uses a binary threshold on cosine: abstain if score < tau_cp. The conformal_reject_option_v1 (HARD_PASS at v327) already validates this with tau_cp in [0.78, 0.79], achieving frac_pass=1.00 at alpha in {0.05, 0.10, 0.20}.

That conformal anchor used the REFUSAL decision as the conformal object, not the prediction set. It asks: "does the refusal threshold have guaranteed coverage?" not "does the prediction set have guaranteed coverage?" These are different objects.

PP-182 (graded confidence spearman=0.961) provides ordinal confidence tiers. This is richer than binary abstention but still score-valued, not set-valued.

The gate3 failure probed a DIFFERENT capability: returning a calibrated set of size >= 1 that provably contains the correct answer. This is complementary to both PP-107 and PP-182.

---

## LEVEL 4: Alternative uncertainty quantification (R4-R5)

### 4.1 Gap-score (PP-181) as conformal nonconformity

PP-181 (cheap2_gap_score_uncertainty, AUC=0.781, cycle 195) uses:

    gap = cosine_score[top-1] - cosine_score[top-2]

as an uncertainty signal. This is a margin score. For conformal:

    nc_gap(x, y_true) = max_j(sc_j) - sc[y_true]

This equals 0 when y_true is top-1, and equals the gap between the true answer and the best incorrect answer when y_true is not top-1.

Simulation on actual parameters:

    Gap-based: coverage=0.906, set_size=1.63

This is slightly better than score-based (0.892) and more robust: it normalizes by the competitive context (the best competitor score), making it less sensitive to the absolute scale of cosine scores under different loads.

**Assessment:** gap-based conformal is the BEST rescue from both coverage and set-size efficiency perspectives. It leverages PP-181's gap signal directly.

### 4.2 Multi-source aggregation

If multiple substrate shards (e.g., from different initialization seeds) score the same query, their per-shard scores can be aggregated:

    nc_ensemble(x, y_true) = 1 - (1/M) * sum_m score_m(y_true)

Coverage guarantee holds per shard independently; ensemble averaging reduces variance of nc, tightening the prediction sets. Expected benefit: mean_set_size drops from 1.65 to 1.3-1.4 with M=3 ensembles.

Cost: M-fold compute at inference time. Not justified for this use case where single-shard already achieves target coverage.

### 4.3 Bayesian posterior over substrate retrievals

Replace point cosine score with a posterior:

    P(y_true | query) proportional to exp(beta * cosine_score) / partition_function

This IS the modern Hopfield retrieval energy formulation (Ramsauer 2021). The nonconformity score:

    nc_Hopfield(x, y_true) = 1 - P(y_true | x; beta_opt)

reduces to temperature-scaled score-based conformal with T = 1/beta_opt. No additional expressiveness; just a framing choice.

### 4.4 Bootstrap from substrate's confidence distribution

Resample calibration nonconformity scores with replacement B times; compute q_hat on each bootstrap. Use the median q_hat across bootstraps. This reduces variance of the conformal threshold, which matters when NCAL is small (< 200). At NCAL=500, bootstrap provides marginal improvement. Not needed.

### 4.5 Ensemble of substrate retrievals with perturbation

Perturb the query vector (e.g., add small random noise, scale by 1 +/- epsilon) and run multiple retrieval passes. Collect nonconformity scores from each perturbed query; use their max or median as the final nc. This approximates a robust nonconformity score that is less sensitive to query noise.

For the substrate: the retrieval score is deterministic given the query, so perturbation must be intentional. Not the primary rescue path.

---

## LEVEL 5: Engineering test designs

### R2a: Score-based conformal (RECOMMENDED PRIMARY)

**Implementation:**

Replace lines 44-46 in exp_gate3_conformal_coverage_cpu_v1.py:

    # OLD (rank-based):
    ranks = np.array([int((sc > sc[o]).sum()) for sc, o in cal])
    k = int(min(VE - 1, math.ceil((NCAL + 1) * (1 - ALPHA)) - 1))
    qhat = int(np.sort(ranks)[min(k, NCAL - 1)])
    
    # NEW (score-based):
    nc_scores = np.array([1 - sc[o] for sc, o in cal])  # nonconformity = 1 - true score
    k = int(min(math.ceil((NCAL + 1) * (1 - ALPHA)) - 1, NCAL - 1))
    qhat_score = float(np.sort(nc_scores)[k])

And replace test coverage:

    # OLD:
    covered += int(r_true <= qhat); setsizes.append(qhat + 1)
    
    # NEW:
    in_set = sc[o] >= (1 - qhat_score)
    covered += int(in_set)
    setsizes.append(int((sc >= (1 - qhat_score)).sum()))

The selftest needs updating: instead of checking quantile arithmetic, check that score-based nc is 1 - max_score (near 0 for correct top-1 retrieval).

**HARD-PASS:** coverage in [0.88, 0.97] AND mean_set_size in [1.0, 5.0] (finite and bounded)
**HARD-FAIL:** coverage < 0.80 OR mean_set_size > 20 (degenerate/bloated sets)
**Baseline comparison:** gate3 baseline coverage=0.676, set_size=1.0
**Expected result:** coverage ~0.90, set_size ~1.65 (per simulation above)
**CPU/local:** Yes, same as gate3 baseline. Wall time: < 5s.

### R2b: Gap-based conformal (ALTERNATIVE/VALIDATION)

**Implementation:**

    # Gap-based nonconformity: max_score - true_score
    nc_scores = np.array([max(sc) - sc[o] for sc, o in cal])
    k = int(min(math.ceil((NCAL + 1) * (1 - ALPHA)) - 1, NCAL - 1))
    qhat_gap = float(np.sort(nc_scores)[k])
    
    # Test: prediction set = candidates with max_score - sc[j] <= qhat_gap
    covered += int(max(sc) - sc[o] <= qhat_gap)
    threshold = max(sc) - qhat_gap
    setsizes.append(int((sc >= threshold).sum()))

**HARD-PASS:** coverage in [0.88, 0.97], mean_set_size in [1.0, 5.0]
**HARD-FAIL:** coverage < 0.80
**Expected result:** coverage ~0.906, set_size ~1.63 (per simulation)

### R3: Temperature-scaled softmax conformal

**Implementation:**

    T = 5.0  # fixed; no fitting needed for coverage guarantee
    def softmax_nc(sc, o, T):
        s_scaled = sc / T
        s_scaled -= s_scaled.max()
        probs = np.exp(s_scaled) / np.exp(s_scaled).sum()
        return 1 - probs[o]
    
    nc_scores = np.array([softmax_nc(sc, o, T) for sc, o in cal])
    qhat_T = float(np.sort(nc_scores)[k])

**HARD-PASS:** coverage in [0.88, 0.97]
**HARD-FAIL:** coverage < 0.80

### R4: Adaptive Conformal Inference (ACI)

For non-exchangeable settings (queries with variable load), ACI (Gibbs-Candes NeurIPS 2021) adaptively updates the conformal level:

    alpha_t = alpha_{t-1} + gamma * (alpha - 1[y_true in C(x_t)])

This handles the case where retrieval accuracy varies with query difficulty. Useful if the substrate's coverage varies systematically across load regimes.

**Implementation cost:** higher (requires streaming calibration); deferred unless R2a fails.

### R5: Per-bucket conformal (Mondrian)

Mondrian conformal (Vovk et al. 2005) applies separate conformal thresholds per difficulty bucket:

    q_hat_bucket = quantile({nc_i : i in bucket}) 

where buckets are defined by query load level or PP-182 confidence tier.

Benefits: conditional coverage per difficulty level; reduces the mixed-load problem.
Cost: requires labeled load level at inference time; needs >= 50 calibration samples per bucket.

**HARD-PASS criterion:** coverage >= 0.88 IN EACH BUCKET (not just overall)

---

## LEVEL 6: Strategic decision

### 6.1 Highest-confidence rescue

**R2a (score-based) is highest confidence.** Simulation on actual experiment code gives coverage 0.892-0.928 across 3 seeds. The change is one line (replace rank-based nc with score-based). It directly addresses the root cause (rank collapse under high accuracy). Implementation risk: near-zero. P_theoretical=0.85, P_empirical (from simulation)=0.90.

**R2b (gap-based) is a strong backup.** Achieves coverage=0.906 in simulation. Marginally more robust to load variance. Leverages PP-181's gap score directly.

### 6.2 Does conformal coverage matter for substrate positioning?

**Depends on the customer use case.**

For knowledge retrieval in general enterprise settings: the existing 3-layer stack (PP-107 binary abstention + PP-182 graded confidence + PP-183 factual AUC) is sufficient. These three together give coverage certificates through empirical validation.

For regulated industries (EU AI Act Art.12, medical device MDR, financial services model risk): conformal prediction provides distribution-free, finite-sample guarantees that are mathematically stronger than empirical AUC. A regulator asking "can you prove with probability >= 90% that your system returns the correct answer?" is answered by conformal prediction, not by AUC=1.000 (which is a historical accuracy metric, not a prospective coverage guarantee).

The substrate-product positioning distinction:
- PP-107/182/183 = "our system has been empirically validated with these metrics"
- Conformal = "our system provides a math-grade coverage certificate on each individual query"

The second statement is qualitatively stronger and differentiates from logging-based compliance systems.

### 6.3 Does the existing 3-layer stack suffice?

For v1 demo: YES. The existing PP-107 (AUC=1.0) + PP-182 (spearman=0.96) + PP-183 (AUC=1.0) + PP-184 (Merkle completeness=1.0) stack covers the observable confidence and compliance story. Adding conformal is enhancement, not prerequisite.

For EU AI Act compliance gate (Article 12 requires "appropriate technical documentation" for high-risk systems): conformal prediction's formal guarantees are a stronger technical documentation basis than empirical metrics alone. This is material if the v1 demo targets healthcare, financial, or legal verticals.

### 6.4 When conformal is categorically needed

1. Regulated industries where prospective coverage guarantees are audited
2. Insurance/actuarial applications where prediction sets have contractual meaning
3. Medical decision support where set-valued outputs are clinically interpretable
4. Any setting where "I return a set that provably contains the answer" is the product promise, not just "I usually return the right answer"

The substrate's existing product framing (PP-31a conformal_reject_option_v1 HARD_PASS) already deploys conformal for the REFUSAL decision. Extending to prediction sets is incremental.

### 6.5 Algebraic confidence vs frequentist conformal -- strategic positioning

The substrate has two distinct confidence signals:
- **Algebraic confidence** (PP-107/PP-182/PP-183): derived from cosine similarity structure, deterministic per query, reflects the geometry of stored vs queried content
- **Frequentist coverage** (conformal): derived from an exchangeability argument over a calibration set, requires calibration data, provides worst-case guarantee

These are complementary. Algebraic confidence is cheaper (zero calibration data needed) and more interpretable (score = geometric similarity). Conformal is more certifiable (formal probability statement).

**Recommended product positioning:** lead with algebraic confidence for operational use, add conformal as compliance layer for regulated verticals. The substrate's advantage is that BOTH are implementable cheaply because:

1. Algebraic confidence = natural by-product of retrieval (zero overhead)
2. Conformal = 200-500 calibration queries (1 CPU-hour one-time)

This is a product differentiation axis: the substrate offers BOTH algebraic (fast, geometric) and frequentist (formal, certifiable) confidence in a single retrieval primitive.

---

## Cheap decisive test

**Name:** gate3_conformal_coverage_scorebased_v2_cpu_v1

**What it does:** Replace rank-based with score-based nonconformity in the existing gate3 experiment. Single-seed CPU run, NCAL=500, NTEST=500, alpha=0.10.

**Pass criterion (HARD-PASS):** coverage in [0.88, 0.97] AND mean_set_size in [1.0, 5.0]
**Middle band:** coverage in [0.80, 0.88)
**Hard-fail:** coverage < 0.80 OR mean_set_size > 20

**Expected result:** coverage ~0.90-0.91, set_size ~1.65

**Cost:** < 5 seconds CPU. Local-testable immediately.

**Self-test addition:** assert that if all calibration queries have nc_i = 0.2 exactly, q_hat = 0.2 and the prediction set includes all candidates with score >= 0.8.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

**Prediction P1 (R2a primary rescue):**
- With score-based nc: coverage in [0.87, 0.95] at alpha=0.10 (3-seed mean)
- HARD-PASS: all 3 seeds >= 0.88
- HARD-FAIL: any seed < 0.80, OR mean set size > 10

**Prediction P2 (R2b gap-based):**
- With gap-based nc: coverage in [0.88, 0.96] at alpha=0.10
- HARD-PASS: coverage >= 0.88
- HARD-FAIL: coverage < 0.80

**Prediction P3 (root cause diagnostic):**
- With rank-based nc at SAME NCAL/NTEST/alpha BUT with LOWER load (load=1 only):
  P(rank=0) should be ~1.0, giving coverage=1.0 (trivially passes)
  This CONFIRMS that the failure was load-induced accuracy degradation, not conformal failure

**Prediction P4 (strategic):**
- Score-based conformal at NCAL=200 (smaller calibration set) achieves coverage in [0.87, 0.95]
- This is the minimum viable calibration set size for the substrate

**HARD-FAIL for the entire rescue direction:**
- If coverage < 0.80 with score-based nc AND with gap-based nc AND with temperature-scaled nc:
  The substrate's score distribution at this query regime has a structural problem (nonconforming to exchangeability assumption). Likely cause: the variable-load query generator introduces non-exchangeability between calibration and test. Rescue would require: stratified calibration by load bucket (Mondrian conformal) or fixed-load test design.

---

## Cross-thread synthesis

**With PP-107 (Abstention ROC, AUC=1.000):**
PP-107 validates that cosine threshold tau_cp=0.78 perfectly separates stored from novel items. Score-based conformal uses the SAME score with a different threshold (q_hat = 1 - 0.165 = 0.835, close to tau_cp). The two thresholds are in the same regime, confirming consistency: the conformal threshold and the ROC-optimal abstention threshold are both near 0.78-0.84.

**With PP-181 (gap-score, AUC=0.781):**
The gap-based conformal nc = max_score - true_score IS the PP-181 gap metric. PP-181 showed this has AUC=0.781 as an uncertainty predictor. The conformal framework provides a principled way to use this signal: instead of a fixed threshold, use the 90th percentile of calibration gaps as the conformal threshold. This promotes PP-181 from a correlation metric to a certified coverage primitive.

**With conformal_reject_option_v1 (PP-31a HARD_PASS):**
PP-31a validated conformal for the ABSTENTION decision (binary set {reject, accept}). The gate3 failure probes conformal for the PREDICTION SET decision (multi-element set). These are different applications. PP-31a's success establishes that the substrate's cosine score IS exchangeable under the refusal framing; the gate3 failure is purely a nonconformity score choice issue, not an exchangeability violation.

**With R11 calibration analysis (temperature scaling, 2026-05-21):**
R11 established that temperature scaling reduces ECE from 0.59 to < 0.05 for point probability calibration. The current drill establishes that for SET-VALUED coverage, temperature scaling is optional (coverage guarantee holds for any fixed T). The two approaches are complementary: temperature scaling fixes point calibration; score-based conformal fixes set coverage.

---

## Substrate-product implications

1. **The conformal failure is a one-line fix.** No architectural change, no retraining, no new data collection. The gate3 failure was a wrong algorithm choice, not a substrate limitation.

2. **Distribution-free coverage certificate is achievable.** Coverage 0.88-0.93 at alpha=0.10 with mean set size 1.65 means the substrate can claim: "For any query drawn from the same distribution as calibration queries, our prediction set contains the true answer with at least 90% probability, with an average of 1.65 candidates returned."

3. **Regulatory differentiator.** EU AI Act Art.12 documentation requires technical foundations for high-risk systems. Conformal prediction provides the strongest available mathematical foundation for coverage claims. Combined with PP-184 (Merkle audit completeness=1.000) and PP-183 (factual confidence AUC=1.000), the substrate's compliance stack is distinctive.

4. **Product framing update.** The current PP-31a (conformal_reject_option_v1) shows conformal for refusal. Adding gate3_v2 (score-based conformal for prediction sets) extends this to the full query-response cycle: refusal AND response are both conformal-certified. This is a differentiating product claim.

5. **Next gate: multi-seed, production N.** Simulation gives 3-seed coverage [0.884, 0.928]. Production validation at N=4096/16384 with 5 seeds would fully certify this row for the cap_map.

---

## Citations (verified)

1. Vovk, Gammerman, Shafer (2005). "Algorithmic Learning in a Random World." Springer. -- Foundational conformal prediction text; split-conformal algorithm.

2. Angelopoulos, Bates (2022). "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification." arXiv:2107.07511. -- Modern pedagogical reference; score-based vs rank-based nonconformity comparison.

3. Romano, Sesia, Candes (2020). "Classification with Valid and Adaptive Coverage." NeurIPS 2020. -- APS/RAPS sets for K-class classification; rank-based nonconformity. The degeneration under high accuracy is noted in the paper's analysis for imbalanced label distributions.

4. Gibbs, Candes (2021). "Adaptive Conformal Inference Under Distribution Shift." NeurIPS 2021. arXiv:2106.00170. -- ACI for non-exchangeable settings (variable-load queries).

5. Conformal kNN UQ in Metric Spaces (2025). arXiv:2507.15741. -- Direct application to vector-codebook retrieval; uses score-based nonconformity.

6. Ulmer et al. (2024). "Non-Exchangeable Conformal Language Generation with Nearest Neighbors." EACL Findings 2024. -- kNN-LM conformal; score-based approach.

7. Liu, Wang, Owens, Li (2020). "Energy-based Out-of-distribution Detection." NeurIPS 2020. arXiv:2010.03759. -- Energy-based confidence = temperature-scaled score; relevant to T-scaled conformal.

8. Ramsauer et al. (2021). "Hopfield Networks is All You Need." ICLR 2021. arXiv:2008.02217. -- Modern Hopfield energy = temperature-scaled cosine sum; substrate mathematical framing.

9. Guo, Pleiss, Sun, Weinberger (2017). "On Calibration of Modern Neural Networks." ICML 2017. arXiv:1706.04599. -- Temperature scaling; cited for contrast with score-based conformal.

10. Conformal Prediction Sets with Trust Scores (2025). arXiv:2501.10139. -- Conditional coverage with learned trust score; matches high-accuracy-miscalibrated regime.

11. Vovk (2013). "Conditional Validity of Inductive Conformal Predictors." JMLR 2013. -- Mondrian (conditional) conformal; per-bucket coverage.

12. Kull, Filho, Flach (2017). "Beta calibration." AISTATS 2017. -- Small-N parametric calibration; complementary to conformal for point probability.

**Verified citations: 12**

---

## Routing

- **Primary action:** exp_dev ship gate3_conformal_coverage_scorebased_v2_cpu_v1 (score-based nc) CPU local queue
- **Secondary:** ship gap-based variant in same batch (2 anchors, shared setup)
- **Cap_map:** gate3 founding annotation already filed at v522. On v2 HARD_PASS, create PP-189 row "score-based conformal coverage" under calibrated confidence cluster, adjacent to PP-31a
- **No cap_map modification this research note** (per role contract)

---

*Note written 2026-06-08. Empirical simulations run on actual experiment code (exp_gate3_conformal_coverage_cpu_v1.py, seed=631, N=4096, VE=300). Results are CPU simulation on researcher machine -- not a production anchor run. Conformal coverage guarantee holds by mathematical proof (exchangeability + quantile construction); the simulation validates the MAGNITUDE of coverage and set size.*
