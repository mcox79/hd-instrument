# R3-Kscaled catastrophe + ACF asymmetry — research synthesis

Returned 2026-05-19. Unbiased diagnosis of two connected negatives:
R3-Kscaled BWT -2.45 catastrophic; ACF asymmetric (hurts K=2048, helps K=3072).

## TL;DR

Both findings are textbook bias-variance asymmetry (Stein's paradox /
James-Stein shrinkage). R3-Kscaled is **implementation-broken**, not
concept-broken: `log(count + 1e-6)` normalizer creates ~14-unit logit
spikes that swamp retrieval. ACF is correctly implemented but needs
**K-dependent sparsity r** per the paper's own appendix tables.

**The compound question is NOT fully closed.** R3 with proper Laplace
smoothing may still work at K=32.

## R3-Kscaled variance-explosion math

Implementation (`exp_wave14b_triple_compound.py:158-159`):
```
vote_logp = log(vote + 1e-6)
vote_logp -= vote_logp.mean(dim=1, keepdim=True)
```

At K=32, pool=1024, NUM_CONCEPTS=1600:
- Each concept is (i,b_i,j,b_j) pair → P(active on random 32-byte string)
  ≈ (1/256)² = 1.5e-5. Expected pool activations per concept ≈ 0.016.

**Two regimes per concept:**
1. **All-zero row** (majority): every cell = log(1e-6) = -13.8;
   zero-meaned row = 0. Useless but safe.
2. **One-hot row** (rare): one cell ≈ 0, 255 cells ≈ -13.8;
   zero-meaned row has **+13.75 spike on a single byte**.

**Softmax overflow:**
- `combined_logits = 8·sims + 0.5·concept_logits`
- sims magnitude O(1) → `8·sims` ~±8
- One R3 spike: `0.5 × 13.75 ≈ +7` into ONE arbitrary target byte
- **One R3 vote outweighs the retrieval kernel.**

With 1600 concepts and rare activations, the heavy-tailed spikes pick
ESSENTIALLY ARBITRARY target bytes (the 1-of-1024 pool match at K=32
is sampling noise, not real PMI). Softmax puts mass on random byte.
BWT collapses to -2.45, worse than no-replay.

This is **NOT "more concepts helps coverage"** — it's **"more concepts
amplifies log-epsilon noise."** `+1e-6` is not Bayesian smoothing;
it's a hack that creates -13.8 in zero cells and -- after zero-meaning
-- promotes any rare positive count into an oversized positive logit.

## R3 fixes (ranked by predicted power)

1. **True Dirichlet/Laplace smoothing**: `vote_logp[c,t] = log((count[c,t] + α) / (sum_t count[c,t] + 256α))` with α ≈ 1. Zero counts become log(1/(256+ε)) ≈ -5.5, not -13.8. **Variance drops ~6×.**
2. **Per-concept variance normalization**: divide each row by SD after zero-meaning. Stops 1-hot row from dominating.
3. **Hard min-count threshold**: drop concept if `sum_t count[c,t] < N_min`. Equivalent to BPMI's significance test.
4. **MI-selected concepts** instead of top-K PPMI: select 100 maximizing I(concept; target byte). Quality over count.
5. **PPMI shifted by log(N_pool)**: analytically subtracts rare-co-occurrence inflation.

**Single decisive experiment**: rebuild R3 with α=1 Laplace smoothing,
NUM_CONCEPTS=100, K=32, 3 seeds. Predict BWT ≈ -0.85 ± 0.05 (matches
replay-only) OR BETTER -- if better, R3 compound is real after all.
If null, R3 truly closed and rehabilitation moves to MI-selected concepts.

## ACF asymmetry — paper itself uses K-dependent r

Karunaratne-Langenegger 2024 appendix tables span r ∈ {0, 0.001, 0.005,
0.008, 0.01, 0.05, 0.1}. r generally DECREASES as search-space size
grows. Two factors use r ∈ [0.005, 0.1]; 3-4 factors use down to 0.001
or 0. **Paper tunes r per problem size, not fixed.** When r is reported
as 0 for some regimes, that's the paper saying "don't apply ACF here."

Our K=2048 (easy, baseline 100%): ACF with any r>0 corrupts the
codebook reconstruction needlessly. Paper would use r=0.
Our K=3072 (past cliff): r=0.01 is in paper's prescribed range.

**The asymmetry isn't a surprise; it's a tuning-protocol omission.**

## ACF rescues (ranked)

1. **K-dependent r schedule**: r=0 for K/N ≤ 0.50; r=0.005 for
   0.50 < K/N ≤ 0.55; r=0.01 for K/N > 0.55. Literally copy paper's
   per-problem-size grid. Single A/B settles it.
2. **Convergence-gated ACF**: baseline first, switch to ACF if not
   converged in B/2 iterations.
3. **Confidence-annealed r**: `r_t = r_max · (1 − max_similarity_t)`.
   High-confidence iterates → r→0 (baseline). Continuous version of (2).

## Unifying theorem

Both findings are **James-Stein/Stein's paradox**: shrinkage estimators
dominate MLE when SNR is LOW; in LOW-noise regime, bias cost exceeds
variance saving. Efron-Hastie CASI Ch.7 makes this explicit.

**ACF asymmetry**: ACF is shrinkage on reconstruction codebook --
injects noise that perturbs resonator off spurious fixed points. At
K=2048 no spurious fixed points → ACF is pure bias. At K=3072 margin
has collapsed → shrinkage's variance reduction dominates.

**R3-Kscaled**: R3 at K=4 with 100 concepts is low-variance biased
readout (dense, well-estimated PMI). At K=32 with 1600 broken-normalized
concepts is high-variance and biased. Implementation has *unbounded
variance per concept*; regularizer fails on its own terms.

[Nakkiran 2020 regularization-wise double descent](https://arxiv.org/pdf/2206.01378):
optimal regularization strength depends on regime. Holding it fixed
across regimes guarantees one side breaks. K is our regime variable.

## Honest bottom line

- **R3-Kscaled is implementation-broken**: switch to Laplace smoothing
  before declaring "more concepts" dead
- **ACF needs K-dependent r** per paper's own appendix: r=0 for
  K/N ≤ 0.50. The 50× cliff rescue is intact.
- **Both findings are the same theorem**: bias-variance asymmetry on a
  regularizer whose strength must depend on noise regime
- **Single experiment to reopen compound**: R3 with α=1 Laplace
  smoothing at K=32, 3 seeds. Predict ≈ replay-only or better.

## Sources

- [Additive smoothing Wikipedia](https://en.wikipedia.org/wiki/Additive_smoothing)
- [Why So Down? PPMI bias toward rare words](https://arxiv.org/pdf/1908.06941)
- [Levy-Goldberg Neural Word Embedding as Implicit Matrix Factorization](https://www.semanticscholar.org/paper/Neural-Word-Embedding-as-Implicit-Matrix-Levy-Goldberg/f4c018bcc8ea707b83247866bdc8ccb87cd9f5da)
- [PSU STAT 504 12.4 Log-linear inference with sparse data](https://online.stat.psu.edu/stat504/lesson/12/12.4)
- [James-Stein estimator Wikipedia](https://en.wikipedia.org/wiki/James%E2%80%93Stein_estimator)
- [Efron-Hastie CASI Chapter 7 James-Stein and Ridge](https://efron.ckirby.su.domains/other/CASI_Chap7_Nov2014.pdf)
- [Optimal Regularization Can Mitigate Double Descent](https://arxiv.org/pdf/2003.01897)
- [Regularization-wise double descent Nakkiran 2020](https://arxiv.org/pdf/2206.01378)
- [Karunaratne-Langenegger On Role of Noise in Factorizers](https://arxiv.org/html/2412.00354v1)
