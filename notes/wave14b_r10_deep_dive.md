# R10 deep dive — research agent synthesis

Returned 2026-05-19. User specifically requested "do not close r10 yet,
do deep research unbiased" after R10's K=16 single-seed result
showed +0.024 pre-shift / +0.009 post-shift (below 0.03 threshold).

## Bottom line

**R10 finding is suggestive but under-powered, not genuinely null.**
Three reasons:

1. **Single seed.** Byte-LM bpc seed variance is plausibly 0.005-0.015
   at this scale. Observed +0.024/+0.009 sits well within the noise
   band of a single replicate.

2. **The redundancy theorem we relied on (Lippl-Stachenfeld 2025) is
   noise-free.** It assumes orthogonal/disentangled features, no
   bundle interference. At K=16 the context bundle is no longer
   near-orthogonal across queries (bundle interference ~K/N is real);
   per-position decompose accuracy drops below 100%. The corollary
   does NOT formally extend.

3. **The +0.024 → +0.009 shrinkage is informative.** Multiple
   mechanisms predict it. M3 in particular: C3-factored A_only routes
   around W; post-shift it loses less than C1; slack for concepts
   shrinks naturally.

## Where K=16 deviates from theorem assumptions

| Assumption | K=4 | K=16 |
|---|---|---|
| Orthogonal component features | bipolar atoms near-orthogonal | bundle non-orthogonal across queries |
| Noiseless training data | bpc>2; not noiseless | per-position decompose drops below 100% |
| Fixed feature map | W trained, basis fixed | same |
| Linear readout | softmax-then-mix | same |
| Borel-function-of-G kernel | argmax-decompose is sharp delta of G | argmax is non-smooth quantizer; PPMI on noisy decoded bytes carries decompose noise *independent* of kernel noise |

The fourth row is the precise crack. The redundancy corollary requires
the concept signal to be a deterministic Borel function of G. At K=16
the argmax in `decompose_pool` is itself a noisy estimator, so PPMI
computed against this carries noise structurally independent of
retrieval noise. Independent-noise variance reduction (Bayesian model
averaging) IS possible.

## 5 mechanisms by which the +0.024 / +0.009 gap could be real

**M1. Independent-noise variance reduction.** Factored retrieval score
and PPMI concept indicator are both unbiased estimators of the same
Bayes-optimal LLR with partly independent noise. Bienayme + convex
combination = lower variance. At K=4 both have zero noise → no slack;
at K=16 retrieval noise sigma_r ~ sqrt((2B-1)/N) ≈ 0.09 → real.

**M2. Decompose-residual signal.** Per-position argmax is MAP byte;
softmax posterior carries probability mass that kernel lumps as
"interference." PPMI on argmax is NOT a Borel function of G — it's a
function of argmax(G·phi), a non-smooth quantizer. This IS the
non-Borel-of-G escape Lippl-Stachenfeld leaves open. Test: replace
argmax with soft posterior in decompose_pool.

**M3. Distribution-shift covariance.** Post-shift, W has drifted to
corpus B; pool + PPMI remain anchored to A. Retrieval kernel
<W phi(z), x_i> has systematic bias from W-G mismatch; PPMI is biased
only by corpus-A frequencies. **A_only routes around W** → post-shift,
A_only loses less than C1 → slack for concept gain shrinks naturally.
*Predicts the observed pre→post shrinkage.*

**M4. Effective-rank gap from bundle interference.** Retrieval kernel
effective rank drops with K (correlated bundle noise across positions);
concept atoms span a different/higher-rank subspace. Compute eff-rank
of K=16 retrieval kernel vs PPMI-pair kernel.

**M5. Pre-registration threshold mis-set.** The 0.03 threshold was
chosen by analogy to C3 factored vs C1 (+0.098 magnitude). Bayes-floor
improvement from adding one noisy independent estimator to a strong
one is bounded by (1/2) log2(1 + sigma_r^2/sigma_c^2) in bits — at
K=16 this can be 0.01-0.03 bpc. Threshold was numerically aspirational.

## Battery of experiments (~5h GPU total)

Ranked by info per GPU hour:

1. **Multi-seed at K=16 (5 seeds).** ~75 min. Resolves M1, M5.
   Mean ± SD of linear-fusion-vs-A_only gap. Reject null if mean/SE > 2.78 (t-test).
2. **K-sweep at N=4096: K in {4, 8, 12, 16, 24, 32}, 3 seeds.** ~30 min.
   Resolves M4. Monotone gap vs K = R10 under-powered; peaks at moderate K = independent-noise signature.
3. **N-sweep at K=16: N in {1024, 2048, 4096, 8192}, 2 seeds.** ~45 min.
   Resolves M1, M4. Smaller N → higher per-position noise penalty → gap should grow.
4. **Soft-posterior PPMI ablation.** ~20 min. Replace argmax with soft
   posterior. Resolves M2.
5. **W-removal ablation (alpha=1 condition).** ~20 min. alpha in
   {0.3, 0.5, 0.7, 1.0}. Resolves M3.
6. **Concept-count sweep.** ~30 min. NUM_CONCEPTS in {50, 100, 500, 2000}.
7. **Concept method variants at K=16.** ~45 min. CP, NMF, soft-PPMI.

## Decision rules from multi-seed

- mean(linear-A_only) post-shift < 0.005, SD ~0.01: kill the hypothesis cleanly
- mean > 0.015, SD < 0.008 (t > 2.78): meaningful effect; **redundancy
  corollary fails at K=16**; M1/M2/M4 live
- intermediate: needs K-sweep + N-sweep

## What if M3 is right

If M3 is the mechanism, the more interesting question isn't "do concepts
beat A_only" but "do concepts beat A_only when W is drifted" — which
is the continual-learning headline R7 partially answered (random
replay > concept-tagged for BWT). The two findings are consistent:
concepts derived from pool can't escape pool-based retrieval; *fresh*
signal (W-removal, external Y, random replay) can.

## Sources

- [Lippl-Stachenfeld 2025 ICLR arXiv:2405.16391](https://arxiv.org/abs/2405.16391)
- [Lippl-Stachenfeld v2 HTML](https://arxiv.org/html/2405.16391v2)
- [Kleyko-Frady-Sommer Capacity Analysis 2023](https://arxiv.org/abs/2301.10352)
- [Frady-Kent-Olshausen-Sommer Resonator Networks I & II](https://openreview.net/pdf?id=FNrZd3Ls1d)
- [Wu et al. PMI for RAG arXiv:2411.07773](https://arxiv.org/abs/2411.07773)
- [Velickovic 2024 Softmax is not Enough](https://arxiv.org/abs/2410.01104)
