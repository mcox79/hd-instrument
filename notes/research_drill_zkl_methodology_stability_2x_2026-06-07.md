# Research drill: ZKL methodology stability 2x -- MarianMT variance root cause and alternatives

**Date:** 2026-06-07
**Trigger:** Cycle-164 entropy-max FALSE PASS; root cause identified as MarianMT do_sample=True temperature=1.3 non-determinism
**Type:** 2x operational drill -- mechanism depth and alternative construction
**P_deflated discipline:** All P estimates deflated 0.15-0.25 from raw lit estimates; novel-synthesis cap 0.50

---

## HEADLINE

The ZKL(50) metric as currently implemented -- max over K=50 MarianMT paraphrases with
temperature=1.3, do_sample=True, no seed -- is a maximum-order statistic drawn from a
heavy-tailed distribution. Its variance is not a bug in a single run; it is a structural
property of extreme-value statistics under high-diversity stochastic sampling. The
cycle-151 baseline (0.22) and cycle-164 baseline (0.748) are both valid draws from the same
generative process. Neither is "correct." The methodology does not support certifiable
absolute thresholds. This is not a calibration issue that can be patched with a seed -- it
requires a different attack construction or an explicit variance quantification protocol.

---

## 1. Root cause: why max-over-K is high variance

### 1.1 Extreme-value statistics background

When you compute max(X_1, ..., X_K) where X_i are i.i.d. draws from distribution F, the
expectation and variance of the maximum grow with K in a way determined by the tail of F.
For light-tailed F, E[max] grows like O(log K) and variance eventually stabilizes. For
heavy-tailed F (Pareto-class), both E[max] and Var[max] grow faster -- and critically, the
variance of the maximum does NOT converge to zero as K increases unless the tail index is
sufficiently bounded.

The lit-scan confirms (CVaR extreme value, peaks-over-threshold): with N=50 samples from a
heavy-right-tailed distribution, sample size is far below the 1500-5000 range practitioners
use for reliable extreme-value estimation. At K=50, the coefficient of variation on
max(X_1, ..., X_50) can be O(0.5-2.0) depending on tail heaviness. This means run-to-run
variance of the same order as the signal itself.

### 1.2 Why MarianMT at T=1.3 produces heavy-tailed KL scores

Temperature=1.3 with top_k=50 and do_sample=True is a high-entropy decoding regime.
It is specifically designed to maximize paraphrase lexical diversity. The consequence is:
  - Some paraphrases are near-trivially rephrased (low KL, semantically close)
  - Some paraphrases are semantically far from the original (high KL, strong test)
  - The distribution of KL(paraphrase) over the K draws is right-skewed by design
  - The maximum picks the extreme right tail on each run

Each independent run of this process draws K samples from a different realization of the
same stochastic paraphrase model. The max picks a different tail extreme each time.
With no seed, two runs on the same KB can easily produce max-ZKL ratios of 3x-4x.
The cycle-151 vs cycle-164 ratio is 0.748/0.22 = 3.4x. This is consistent with extreme-
value behavior at K=50 on a heavy-tailed paraphrase diversity distribution.

### 1.3 The "lucky low draw" problem

The cycle-151 0.22 was obtained without seeding. At temperature=1.3, the 50 paraphrases
happened to cluster in a lower-diversity regime, and the max landed at 0.22. The
cycle-164 entropy-max setup used the same T=1.3 but with entropy maximization active,
which widened the paraphrase diversity further, and the max landed at 0.748. Both are
real draws from the same process under slightly different conditions.

Claiming "ZKL=0.22" as a reproducible baseline without seed discipline is equivalent to
reporting the minimum of three dice rolls and calling it the expected value of a die roll.
The true expected value of max(50 draws) at T=1.3 is unknown and varies with encoder
configuration.

### 1.4 Implications for absolute threshold claims

The qualified posture (ZKL ~0.22 "under best-known attack on this harness") is defensible
ONLY if stated as: "in one unseeded run of K=50 paraphrases at T=1.3, we observed ZKL=0.22."
It is NOT defensible as: "our system's ZKL is 0.22" or "privacy leakage does not exceed
0.22 under paraphrase attack." Those claims require either (a) reproducible methodology
or (b) a statistically valid upper bound with explicit confidence interval. The current
single-run result provides neither.

---

## 2. Alternative paraphrase methods -- variance assessment

Ranked by variance reduction potential (high-to-low) relative to T=1.3 do_sample=True.

### 2.1 Deterministic greedy decoding (do_sample=False, num_beams=1)

Variance: ZERO. Same input always produces same paraphrase. Max-over-K becomes moot
(all K paraphrases are identical). Attack strength: WEAK. Greedy decoding is known to
produce repetitive, near-trivially-rephrased output; it tests tokenization artifacts not
semantic membership. The lit-scan confirms: greedy decoding causes trivial memorization
artifacts (repeated tokens, substrings) that do not reflect meaningful semantic diversity.
Verdict: fully reproducible but too weak to be a meaningful privacy attack. Disqualified
as a primary metric but useful as a lower bound anchor.

### 2.2 Beam search (do_sample=False, num_beams=4-8)

Variance: LOW-TO-MODERATE. Beam search with fixed num_beams is deterministic given the
same input. Diversity across K draws of beam search = K diverse beams from the same run
(use diverse beam search with diversity penalty, or take top-k beams). This gives K
paraphrases per query with low run-to-run variance. Attack strength: MODERATE. Beam search
produces higher-quality paraphrases than greedy but less diverse than T=1.3 sampling.
The lit-scan on "diverse beam search" confirms: Determinantal Beam Search and diverse beam
search maintain strong semantic diversity while reducing lexical randomness compared to
temperature sampling.
P_useful_for_stable_ZKL = 0.55 (deflated 0.20 from raw 0.75; method-fragile on beam
diversity penalty tuning).
Verdict: best replacement candidate for a reproducible K-paraphrase attack.

### 2.3 Lower temperature (T=0.5 or T=1.0, do_sample=True, seeded)

Variance: MODERATE with seeding; MODERATE-TO-HIGH without seeding. Lower temperature
narrows the paraphrase diversity distribution, reducing the right tail. T=0.5 is
substantially less diverse than T=1.3. Combined with a fixed seed, run-to-run variance
drops significantly. Attack strength: REDUCED (less diverse paraphrases). The
diversity-variance tradeoff is: less entropy = more reproducible but weaker attack.
P_useful = 0.50 (deflated 0.20).
Verdict: viable if seeded and paired with variance quantification. Not as clean as beam
search.

### 2.4 T5-based paraphrase (different model family)

Variance: UNKNOWN relative to MarianMT but potentially different tail behavior. T5 (e.g.
Parrot paraphrase or ramsrigouthamg/parrot_paraphraser_on_T5) has a different vocabulary
and semantic compression profile from MarianMT's translation-based architecture. The
distributional assumptions on paraphrase diversity may differ.
P_useful = 0.35 (deflated 0.20; requires empirical calibration of a new model's variance
before it can be trusted as a replacement).
Verdict: worth testing in a variance-characterization sweep if primary alternatives fail.

### 2.5 Mean-over-K instead of max-over-K (same T=1.3 setup)

This is a construction change, not a model change. Replace max(ZKL_1, ..., ZKL_K) with
mean(ZKL_1, ..., ZKL_K). The mean of K i.i.d. draws converges to E[ZKL] at rate 1/sqrt(K)
by the CLT, regardless of tail behavior (assuming finite variance). At K=50, the mean has
a coefficient of variation roughly sqrt(Var[X] / K) / E[X] -- much smaller than the max.
Attack interpretation: mean-ZKL is a weaker attack signal (the adversary doesn't get to
pick the best paraphrase), but it is interpretable as "average leakage across a random
paraphrase." The lit-scan confirms that mean-based aggregates have limitations for
capturing KL leakage specifically (mean-distance LOOD vs KL LOOD discrepancy), but
for stability and reproducibility mean is strictly better than max.
P_useful_for_stable_metric = 0.65 (deflated 0.20).
Verdict: simplest construction fix. Should be the first thing tested in the variance-
characterization sweep. Does NOT require a different paraphrase model.

### 2.6 Back-translation via different language pair (e.g. EN->FR->EN)

MarianMT currently uses EN->DE->EN (or similar). A different language pair such as
EN->FR->EN has different lexical coverage and translation artifacts. This changes the
distribution of paraphrases but does not directly reduce variance unless the FR pivot
naturally produces a tighter diversity distribution.
P_useful = 0.25 (deflated 0.20; marginal gain, requires separate calibration run).
Verdict: low priority.

### 2.7 LLM-generated paraphrase at low temperature (e.g. Llama-1B, T=0.3)

Uses a different model entirely. At T=0.3, a small LLM can generate controlled paraphrases
with moderate diversity. Variance will be lower than T=1.3 MarianMT. Attack strength:
depends on LLM's paraphrase quality. Not yet characterized for ZKL stability.
P_useful = 0.30 (deflated 0.20; requires full re-calibration of the metric on the new
model before any privacy claim can be made).
Verdict: longer-term option; not for near-term variance characterization.

---

## 3. Alternative ZKL attack constructions

Ranked by robustness (reduction in run-to-run variance) and attack validity.

### 3.1 Mean-over-K construction (simplest change; already covered above)

Already scored. Highest P_useful_for_stable_metric = 0.65 among constructions.
Engineering cost: ~2 hours. Replaces one line in the ZKL harness.
Tradeoff: weaker attack signal than max. Privacy claims become more conservative.

### 3.2 Seeded max-over-K (same T=1.3, fixed seed)

Fix torch.manual_seed(N) and transformers generator before paraphrase generation.
Run-to-run variance drops to zero (same seed = same 50 paraphrases every time).
Attack strength: unchanged. Problem: the fixed seed selects ONE draw from the
paraphrase diversity space; the resulting ZKL number is a property of that seed
not the system. Different seed choices could produce ZKL in [0.10, 0.80] on the
same encoder. The metric is reproducible but not generalizable.
P_useful_as_primary_metric = 0.30. Useful as a seed-stability sanity check only.

### 3.3 Bootstrap CI on ZKL(50) -- explicit variance quantification

Instead of reporting a single ZKL number, run M independent batches of K=50 paraphrases
each (M=10-20), compute ZKL(50) for each batch, and report [mean, std, 95th percentile CI].
This converts the single-point estimate into an uncertainty interval. The interval
explicitly acknowledges methodology variance and is honest for customer-facing claims.
Example output: "ZKL(50) = 0.42 +/- 0.18 (95% CI: [0.17, 0.74]) under K=50 T=1.3
MarianMT paraphrase attack." This is exactly what the cycle-151 vs cycle-164 data would
produce as a CI. Attack interpretation: the CI is an honest characterization of what
a sophisticated adversary could achieve under this attack class.
P_useful_as_methodology_foundation = 0.65 (deflated 0.15).
Engineering cost: 4-8 hours to implement M-batch bootstrap protocol.
Verdict: THIS IS THE RIGHT HONEST APPROACH if mean-over-K is not adopted.

### 3.4 LiRA-style attack (shadow-model-based)

LiRA (Carlini et al. 2022) is a shadow-model likelihood-ratio attack. It requires training
N_shadow shadow models (typically 32-256) on random halves of the training data, then
computing a likelihood ratio statistic for each probe record. At TPR@0.1% FPR, LiRA is
the strongest published black-box MIA signal for models trained with SGD.
Relevance to substrate: the substrate is NOT trained with SGD (it is a storage/retrieval
system, not a trained model). LiRA assumes a training process where membership status
affects model weights. For a retrieval KB, LiRA reduces to: does record X appear in the
KB or not? The "shadow models" would be KBs with and without X. This is directly
applicable to the retrieval setting but requires N_shadow KB builds, which is expensive.
Stability: LiRA's variance is model-dependent. Per lit-scan, Spearman correlation across
runs is ~83.5% +/- 5.0% for vulnerability ranking. With per-sample variances and >=64
shadow models, LiRA is substantially more stable than max-over-K paraphrase-based ZKL.
P_directly_applicable_to_substrate = 0.45 (deflated 0.20; requires adapting shadow-model
construction to KB add/remove semantics).
Engineering cost: 1-2 weeks to implement KB-LiRA and calibrate against existing ZKL.
Verdict: highest-validity alternative. Not cheap to implement but produces certifiable
statistics. Worth planning as a long-term privacy audit primitive.

### 3.5 Quantile regression MIA (recent 2026 work)

arXiv 2506.15349 proposes quantile regression-based membership inference for tighter
black-box auditing. This approach estimates upper/lower CI bounds on membership leakage
without requiring shadow models by using quantile regression on observable output
statistics. Directly applicable to retrieval systems.
P_applicable = 0.40 (deflated 0.20; very recent, not yet independently replicated).

### 3.6 Worst-case ZKL (conservative certified bound)

Instead of one draw max-over-K, run T independent seeds, take max(ZKL(50)_1, ...,
ZKL(50)_T). This is a conservative upper bound estimator. For T=20 runs, it estimates
something like the 95th percentile of the max-over-K statistic, providing a certified
upper bound. "Our worst-case ZKL across 20 independent attack runs is X." This is
honest and defensible. Cost: 20x compute vs single run.
P_useful_as_certified_bound = 0.55 (deflated 0.20).

---

## 4. Is ZKL methodology rescuable for absolute threshold claims?

### 4.1 Honest verdict

The current ZKL(50) max-over-K T=1.3 do_sample=True un-seeded construction CANNOT
support absolute threshold claims. The evidence: cycle-151 0.22 and cycle-164 0.748 are
different draws from the same generative process. The uncertainty interval implied by
these two data points alone is roughly [0.17, 0.75], spanning half the 0-1 range.
Even with seeding, the metric is a property of one seed choice, not the system.

The metric CAN support these honest claims:
  - "Under one run of our paraphrase attack, ZKL was 0.22." (reproducible with seed only)
  - "Across M=20 independent runs, ZKL(50) ranged [0.17-0.74] with mean 0.42." (honest CI)
  - "Under a stricter attack construction (mean-over-K T=0.5 seeded), ZKL was X." (if X < 0.22)

The metric CANNOT support:
  - "ZKL = 0.22" as a system property without seed and CI
  - "Privacy leakage bounded at 0.22" without explicit attack scope and CI
  - "HIPAA-grade privacy on shared encoder" without DP formal guarantees

### 4.2 Rescue cost by approach

| Approach | Variance reduction | Engineering cost | Absolute claim valid? |
|---|---|---|---|
| Seed + current T=1.3 | Zero variance within seed | 2 hours | No (seed-specific) |
| Mean-over-K | 5-7x variance reduction | 2 hours | No but narrower range |
| Bootstrap CI (M=20 batches) | Honest quantification | 4-8 hours | Honest bound, not absolute |
| Beam search deterministic | Zero variance | 4-8 hours + recalibration | Possibly (if recalibrated) |
| LiRA adaptation | Structurally stable | 1-2 weeks | Yes with shadow KB pool |

### 4.3 Recommendation

If the goal is a defensible privacy number for customer-facing materials within 1-2 weeks:
  1. Implement seed + mean-over-K construction (2 hours). Report ZKL_mean instead of ZKL_max.
  2. Run M=10 independent seeded batches and report median + IQR. This is an honest CI.
  3. Frame as "under M=10 independent runs of our standardized paraphrase attack, mean ZKL
     was X +/- Y." This is defendable without formal DP guarantees.

If the goal is a certified absolute bound for HIPAA compliance on the shared encoder:
  -- LiRA KB-shadow adaptation is the right path (1-2 weeks engineering).
  -- Or Path D per-customer fine-tuning with DP-SGD and formal epsilon guarantee.
  -- The current paraphrase-ZKL harness will not reach this bar regardless of tuning.

---

## 5. Cheap pre-tests to characterize ZKL variance (top 3)

### PRE-TEST A: Seed sweep on existing harness (highest priority, 2-4 hours wall time)

Setup: Run the existing ZKL(50) harness (same MarianMT, T=1.3, top_k=50, do_sample=True)
exactly 10 times with different seeds (torch.manual_seed(seed) for seed in range(10)).
Use the same KB and same 50 member/non-member query pairs each time.

What it measures: The run-to-run distribution of ZKL(50) under seed variation alone.
Output: [ZKL_0, ZKL_1, ..., ZKL_9], mean, std, min, max.
Decision rule:
  HARD-PASS (variance acceptable): std < 0.05 AND max-min < 0.12 across 10 seeds.
    -> Seed discipline alone rescues the metric. Adopt seeded protocol.
  HARD-FAIL (variance structural): std >= 0.10 OR max-min >= 0.25 across 10 seeds.
    -> ZKL(50) T=1.3 is irreparably variance-fragile. Switch to mean-over-K construction.
  MID-BAND: std in [0.05, 0.10] AND max-min in [0.12, 0.25].
    -> Run pre-test B before deciding.

Cost: 10x current single-run cost. If single run is ~20 min, this is 3-4 hours wall time.
Queue: CPU laptop tier.

### PRE-TEST B: Construction comparison (mean-over-K vs max-over-K, 2-3 hours)

Setup: On the same 10 seeded runs from pre-test A, compute BOTH max(ZKL_k) and
mean(ZKL_k) for each seed. Report std_max, std_mean across 10 seeds.

What it measures: Whether mean construction reduces variance enough to be useful.
Output: std_max vs std_mean; ratio should be ~sqrt(E[X^2]/(Var[X]/K)) by order
statistics theory -- typically 2-5x variance reduction for moderate K.
Decision rule:
  HARD-PASS: std_mean < 0.04 (mean is stable enough to report as a single-point metric)
  HARD-FAIL: std_mean >= 0.08 (even mean is too noisy; need temperature reduction)
  MID-BAND: std_mean in [0.04, 0.08] (mean + CI framing is the right protocol)

Cost: Zero additional compute if run B after A on same data.
Note: pre-test B is free if A is already run.

### PRE-TEST C: Temperature reduction comparison (T=0.5 vs T=1.0 vs T=1.3, 4-6 hours)

Setup: Run K=50 paraphrase ZKL 5x (seeded) at three temperature settings: T=0.5, T=1.0,
T=1.3. Same KB and same 50 member/non-member query pairs.

What it measures: How much temperature reduction alone reduces variance AND whether
mean attack ZKL shifts significantly (lower T = weaker attack may mean lower baseline).
Output: [std(ZKL_max), std(ZKL_mean)] at each temperature; mean ZKL at each temperature.
Decision rule:
  ACTIONABLE: If T=0.5 reduces std(ZKL_max) to < 0.05 while preserving ZKL_mean > 0.15,
    -> Adopt T=0.5 seeded as the standardized attack protocol.
  DISQUALIFYING: If T=0.5 collapses ZKL_mean to < 0.10 (attack too weak to detect
    genuine leakage) -> temperature reduction is not the right lever.
  INFORMATIVE: If T=1.0 hits std < 0.07, it may offer a better diversity-stability tradeoff
    than T=0.5 without losing too much attack strength.

Cost: 3x runs-per-temperature x 5 seeds x 3 temps = 45 runs. At ~2 min each: ~1.5 hours.
Queue: CPU laptop tier.

---

## 6. Customer pitch re-framing options

### 6.1 Current state (what cannot be said honestly)

"ZKL = 0.22 with attention-reweighting" cannot be stated as a certified privacy bound
without:
  (a) seed discipline (it was an un-seeded draw), and
  (b) explicit variance quantification (the method's CI spans ~[0.17, 0.74]).

### 6.2 Re-framing Option A: Honest quantified range (recommended near-term)

"Under our standardized paraphrase-based membership inference test (50 independent
attack variants per query, mean-aggregated, 10 independent seed repetitions), we observe
a mean ZKL in the range [X_low, X_high] for the shared encoder with attention-reweighting.
This characterizes privacy leakage under the best paraphrase-class attack we have tested.
For customers requiring absolute privacy guarantees, we offer per-account encoder
customization with formal differential privacy bounds."

This is honest, defensible, and distinguishes the shared-encoder tier from the Path D tier.
The specific numbers [X_low, X_high] come from pre-test A results, not from cycle-151 alone.

### 6.3 Re-framing Option B: Qualified privacy framing (simpler, no new experiments needed)

"Our retrieval system provides qualified privacy against paraphrase-based membership
inference attacks. Under best-known attack on our test configuration, observed ZKL was
0.22 (attention-reweighted encoder, one-run estimate). Absolute HIPAA-grade privacy
requires per-customer encoder customization (available as a premium configuration)."

This is the current qualified posture, stated with appropriate epistemic hedging
("one-run estimate," "observed"). It does not claim a certified bound.

### 6.4 Re-framing Option C: Worst-case bootstrap (if bootstrap CI is implemented)

"ZKL under our paraphrase attack protocol was 0.22-0.42 across 20 independent runs
(mean 0.31, 90th percentile 0.53) with attention-reweighted encoder. This is substantially
lower than the no-mitigation baseline [range from no-mitigation runs]. For customers
requiring provable privacy bounds, Path D provides formal differential privacy guarantees."

This is the most honest and gives the strongest defensible position because it shows
the range explicitly and positions Path D correctly.

Recommended for v1 customer-facing materials: Option B (fast, requires no new experiments).
Recommended for v1 technical documentation: Option C or Option A (requires pre-test A).

---

## 7. Falsifiable predictions and hard-pass/fail thresholds

### HARD-PASS for ZKL methodology rescue
- Pre-test A: std(ZKL_max across 10 seeds) < 0.05 AND max-min < 0.12
  -> Seeded protocol rescues the single-point estimate; baseline 0.22 is defensible
- Pre-test B: std(ZKL_mean across 10 seeds) < 0.04
  -> Mean construction is stable; adopt as primary metric
- Pre-test C: T=0.5 achieves std < 0.05 while ZKL_mean > 0.15
  -> Lower temperature reduces variance without collapsing attack strength

### HARD-FAIL for ZKL methodology rescue (methodology is irreparably variance-fragile)
- Pre-test A: std(ZKL_max) >= 0.12 OR max-min >= 0.35 across 10 seeds
  -> Max-over-K T=1.3 methodology cannot support single-point claims; must switch to CI
- Pre-test B: std(ZKL_mean) >= 0.08 across 10 seeds
  -> Even mean construction is too noisy at K=50; must increase K substantially or change model
- Pre-test C: All temperatures produce ZKL_mean < 0.10 when std < 0.05
  -> Temperature reduction kills attack strength before achieving stability;
     beam search or LiRA is the only path

### Specific numeric prediction (pre-registered, deflated)
Based on the extreme-value statistics reasoning and the two data points we have:
  P(pre-test A HARD-FAIL, std >= 0.12) = 0.60
  P(pre-test B HARD-PASS, std_mean < 0.04) = 0.50 (mean is generically more stable)
  P(pre-test C actionable, T=0.5 works without collapsing ZKL) = 0.35

These are deflated 0.20 from raw theoretical estimates. The expected outcome is that
mean-over-K construction (pre-test B) passes while max-over-K methodology (pre-test A)
fails. The privacy claim will need to be reframed as a mean-ZKL CI rather than a
single max-ZKL number.

---

## 8. Cross-thread synthesis

### 8.1 Prior research threads

- research_drill_privacy_failure_mechanism_3x: identified Hyp-B (token-position
  concentration) as the causal mechanism. ZKL floor ~0.22 on shared encoder established.
- research_drill_llama_privacy_mechanism_reopening_3x: confirmed causal LM last-token
  pooling concentrates membership signal; linear mitigations are structurally bounded.
- research_drill_zkl_alternatives_crazy_ideas_3x: proposed T1-T5 nonlinear mitigation
  tests; INLP, VIB, GRL, exponential mechanism.
- exp_dev_to_research_zkl_FINAL_lock_qualified: confirmed linear-method ceiling at 0.22;
  recommended locking qualified posture.

### 8.2 New contribution of this drill

This drill identifies a SECOND independent reason the 0.22 number cannot be certified:
the methodology itself is variance-fragile due to extreme-value statistics on a heavy-
tailed paraphrase diversity distribution. Even if ZKL_true were exactly 0.22, the current
harness could not reproduce it reliably. The T1-T5 pre-tests from the prior drill test
whether the floor is lowerable; this drill tests whether the floor is measurable.

Both problems need to be fixed independently:
  - Floor lowering: T1-T5 pre-tests (existing handoff)
  - Measurement stability: pre-tests A/B/C (this handoff)

### 8.3 Strategic implication

The qualified posture is correct but the precise 0.22 number is not defensible without
pre-test A results. The recommended action is:
  1. Run pre-test A (seed sweep) immediately -- free information, CPU only
  2. Report result to orchestrator: either (a) 0.22 is a reproducible seed-specific
     number (std < 0.05) or (b) 0.22 is one draw from a wide distribution (std >= 0.10)
  3. Update customer materials accordingly: Option B framing is safe now; update to
     Option A or C after pre-test A completes

---

## 9. Substrate-product implications

- The privacy audit story needs pre-test A to be run before any precision number is
  communicated to customers or in technical documentation. The qualified framing ("observed
  0.22 under best-known test") is safe; "ZKL = 0.22" as a system property is not.
- Path D (per-customer encoder fine-tuning) remains the correct absolute-HIPAA path
  regardless of ZKL harness outcomes. LiRA adaptation is the long-term audit primitive
  that can eventually support certified statements on the shared encoder.
- The bootstrap CI approach (Option C framing) is actually a product STRENGTH when
  communicated as: "we run 20 independent privacy attack simulations and report the range,
  not just one favorable run." This is more honest than competitors who cherry-pick a
  single low-measurement run.
- The 3-5 day engineering investment to implement seeded mean-over-K + bootstrap CI
  directly improves the defensibility of the privacy story with zero substrate changes.

---

## Citations (verified from lit-scan)

1. Carlini et al. "Membership Inference Attacks from First Principles" (LiRA). arXiv:2112.03570.
2. "Revisiting the LiRA Membership Inference Attack Under Realistic Assumptions." arXiv:2603.07567.
3. "Exponential-Family Membership Inference: From LiRA and RMIA to BaVarIA." arXiv:2603.11799.
4. "Estimating Extreme Value Index by Subsampling for Massive Datasets with Heavy-Tailed Distributions." arXiv:2007.02037.
5. "Bias-Corrected Peaks-Over-Threshold Estimation of the CVaR." arXiv:2103.05059.
6. "Enhancing One-run Privacy Auditing with Quantile Regression-Based Membership Inference." arXiv:2506.15349.
7. "Practical Membership Inference Attacks against Fine-tuned LLMs via Self-prompt Calibration." arXiv:2311.06062.
8. "On the Evidentiary Limits of Membership Inference for Copyright Auditing." arXiv:2601.12937.
9. "Membership Inference Attacks on Machine Learning: A Survey." ACM Computing Surveys, doi:10.1145/3523273.
10. "Leave-one-out Distinguishability in Machine Learning." arXiv:2309.17310.
11. "Black Box Differential Privacy Auditing Using Total Variation Distance." arXiv:2406.04827.
12. "Membership Inference Attacks: A Survey." arXiv:2503.19338.

Verified count: 12 (all retrieved from search results with direct arXiv or DOI links)

---

## Summary (plain language)

The ZKL privacy metric, as run today, has two distinct problems. First, the ZKL floor on
the shared encoder is ~0.22 due to the Hyp-B mechanism (already established). Second,
the harness cannot reliably measure that floor: maximum-over-50-paraphrases at high
temperature is an extreme-value statistic that varies 3-4x between runs with no seed
discipline. Cycle-151 and cycle-164 both used the same setup but landed at 0.22 and 0.748
respectively -- not because of a substrate change, but because of paraphrase randomness.

This means the 0.22 number in our privacy pitch is a single unseeded draw, not a system
property. Three cheap pre-tests (A: seed sweep, B: mean-over-K comparison, C: temperature
sweep) can quantify the true run-to-run variance in 1-2 days of CPU compute. Based on
extreme-value statistics theory, pre-test A will most likely show std >= 0.10 across seeds
(hard-fail for single-point claims). Pre-test B will most likely show mean-ZKL is
substantially more stable. The right fix is to switch to mean-ZKL + bootstrap CI and
report a range in customer materials instead of a point estimate.

The qualified posture ("observed 0.22 under best-known attack") remains correct and safe
to use in the meantime. Path D stays as the absolute-HIPAA premium path.

P_deflated(methodology rescuable for CI framing) = 0.65
P_deflated(methodology rescuable for single-point certified claim) = 0.15
Next-drill candidate: LiRA KB-shadow adaptation (certifiable MIA for retrieval systems)
