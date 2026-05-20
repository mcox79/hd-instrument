# Wave 14c — ACF cliff substructure: noise or signal?

Unbiased research synthesis on the K=2944 dip and K=4096 sub-step in the ACF
recovery cliff. The framing is descriptive: what does resonator dynamics do at
K/N=0.72, and is the observation distinguishable from binomial noise?

---

## 1. TL;DR

The K=2944 dip from ~75% to 50% is **marginal at single-level significance**
(two-tailed p ≈ 0.003 against an interpolated baseline of 0.75) but **collapses
to family-wise p ≈ 0.047** once Bonferroni-corrected across the 16 K-levels
swept. That is borderline — not noise, not headline. The K=4096 dip is weaker
and not significant. Most likely explanation: **single-seed correlation
combined with mild r-mis-tuning at the high-K end of the schedule**; option
(d) plus (c). A 100-trial follow-up at K=2944 is decisive and cheap.

---

## 2. Noise-floor analysis (binomial CI)

Observation: K=2944, k=15/30 successes = 50.0%.
Interpolated baseline from K=2816 (23/30) and K=3072 (22/30): p ≈ 0.75.

**Clopper-Pearson 95% CI** for the observation: **[0.313, 0.687]**.
This CI does *not* contain the interpolated 0.75. So the dip is statistically
inconsistent with a true rate of 0.75 *at this single level*.

**Per-level significance tests (H0: true p at K=2944 is 0.75):**

| Test                                  | Value     |
| ------------------------------------- | --------- |
| P(X ≤ 15 \| n=30, p=0.75) (one-tailed) | 0.0027    |
| Two-tailed p                          | 0.0055    |
| P(X ≤ 15 \| n=30, p=0.70)              | 0.0169    |
| P(X ≤ 15 \| n=30, p=0.65)              | 0.0652    |
| P(X ≤ 15 \| n=30, p=0.60)              | not tiny  |

So if the true rate is 0.75, the dip is a 1-in-370 event. If the true rate is
0.70 (i.e. the neighbors are themselves slightly noisy upward), it is a
1-in-60 event. If the true rate is 0.65, it is plausible (6.5%).

**Bayes factors** (point hypotheses on the observation 15/30):

| Comparison                       | BF (alt / 0.75) |
| -------------------------------- | --------------- |
| p=0.50 vs p=0.75                 | 75              |
| p=0.55 vs p=0.75                 | 64              |
| p=0.60 vs p=0.75                 | 41              |

Decisive evidence in favour of *some* sub-0.75 true rate at K=2944 — *if* we
treat this level in isolation.

**Multiple-testing correction (the brutal part):**

The sweep has 16 K-levels. The relevant question is not "is THIS level
anomalous?" but "is ANY level among 16 anomalous?". Under H0 (all true rates
equal the interpolation baseline 0.75):

- Per-level two-tailed p = 0.0029
- Bonferroni 16-level family-wise p ≈ **0.047**
- Exact independent-trials family-wise p ≈ **0.046**

So at the conventional 0.05 threshold, the dip is **just barely significant
after correcting for multiple comparisons**, and would not survive any
stricter correction (Holm, BH at α=0.01).

**Standard error reference points:**

- SE at p=0.75, n=30: 7.9 pp → ±1.96 SE = ±15.5 pp band around 75%
- SE at p=0.75, n=100: 4.3 pp → ±1.96 SE = ±8.5 pp band

A 100-trial repeat at K=2944 would discriminate p=0.75 (CI [0.65, 0.83]) from
p=0.55 (CI [0.45, 0.65]) cleanly — non-overlapping CIs.

The K=4096 (25/30 = 83.3%) dip relative to K=3584 (90%) and K=5120 (96.7%):
P(X ≤ 25 | n=30, p=0.93) = 0.055 — *not* significant. K=4096 is well within
30-trial noise.

---

## 3. Resonator capacity literature on cliff substructure

I searched Frady-Sommer-Kent (Resonator Networks 1 and 2; arxiv:1906.11684 and
arxiv:2007.03748), Karunaratne-Cherri-Langenegger (ACF; arxiv:2412.00354),
Mirus et al. (algebraic characterization; Scientific Reports 2024), and the
2026 review (OpenReview FNrZd3Ls1d) for any reports of cliff substructure.

**What the literature reports:**

- Cliff is described as **sharp but smooth-monotone** in published curves.
  Frady-Sommer report operational capacity M_max scaling quadratically with N
  for F=2 factors, with accuracy dropping from ~1 to ~0 across a narrow M
  range. They do not characterize sub-structure within the transition; their
  trial counts and grid spacing are coarser than ours.
- Limit cycles are acknowledged as the dominant failure mode at high K/N.
  Karunaratne 2024 (the ACF paper) explicitly frames the noise injection r as
  a means to *break* limit cycles. The paper does not report a recovery curve
  with sub-step dips; it reports binary accuracy thresholds (≥99%) and
  operational capacity multipliers (~50× over baseline).
- The 2023 algebraic characterization paper (Mirus et al., Sci Rep) gives an
  algebraic framework but reports parameter-recovery error vs SNR, not the
  step-by-step capacity curve.
- The 2026 OpenReview review does not report non-monotonicity.

**No paper I found reports cliff sub-structure or non-monotone dips at
specific rational K/N ratios for bipolar resonator networks.** The literature
treats the cliff as a smooth phase transition. This is consistent with two
explanations: (i) nobody looked at fine resolution with ≥30 trials, or (ii)
there is no such structure and finer sweeps still show smooth behavior.

**Closest related results in associative-memory literature:**

- Hopfield networks: 0.14 N capacity is a sharp first-order ("blackout
  catastrophe") transition; no sub-structure reported.
- Modern dense associative memory: smooth retrieval vs memory-load curves at
  finite temperature; sharp at T=0.
- Non-reciprocal Hopfield networks (arxiv:2501.00983) *do* show a limit-cycle
  phase between memory and no-memory regions, bounded by Hopf and fold
  bifurcations. This is the closest analog to the kind of mechanism that
  could produce a localised dip — limit-cycle attractor density spiking in a
  narrow K/N window. But it is reciprocal-vs-non-reciprocal, not directly the
  resonator dynamics.

**Bottom line on literature:** zero direct precedent for sub-step dips in
resonator capacity curves. This is either novel or noise.

---

## 4. The K/N = 0.72 specifically — any prior reports?

K=2944 = 2⁷ · 23, N=4096 = 2¹². gcd = 128. Lowest-terms ratio **23:32**.

The grid structure across our sweep:

| K    | K/N    | gcd  | reduced ratio |
| ---- | ------ | ---- | ------------- |
| 2176 | 0.5312 | 128  | 17:32         |
| 2304 | 0.5625 | 256  | 9:16          |
| 2432 | 0.5938 | 128  | 19:32         |
| 2560 | 0.6250 | 512  | 5:8           |
| 2688 | 0.6562 | 128  | 21:32         |
| 2816 | 0.6875 | 256  | 11:16         |
| **2944** | **0.7188** | **128** | **23:32** |
| 3072 | 0.7500 | 1024 | 3:4           |
| 3328 | 0.8125 | 256  | 13:16         |
| 3584 | 0.8750 | 512  | 7:8           |
| 4096 | 1.0000 | 4096 | 1:1           |

K=2944 has gcd=128 (one of the *least-aligned* ratios in the sweep, alongside
K=2176, K=2432, K=2688). If number-theoretic alignment with N mattered, we
would expect 2688 (21:32) and 2176 (17:32) to dip as well. They don't —
K=2688 is the *peak* of the sub-cliff at 63%, K=2176 is at 50% but inside
the cliff's low-K shoulder so not anomalous.

**No paper that I found cites rational-K/N effects for bipolar resonators.**
Karunaratne 2025 sparse-block-code work (arxiv:2412.00354 and the SBC paper
journals.sagepub.com 10.3233/NAI-240713) does talk about block-structured
codebooks where M_block and N have aligned divisor structure, but those are
sparse block codes, not the dense bipolar setting we have here.

The 23:32 ratio claim does **not** have literature backing. If it is real, it
would be novel. The closer-to-Occam read: the dip is a sample-correlation
artifact at a single K-step.

---

## 5. K=N (square codebook) edge case — math view

At K=N, the codebook matrix X ∈ {±1}^{N×N} is square. Two regimes:

1. **Generic random ±1 with high probability:** Random ±1 matrices are full
   rank with probability 1 − o(1) as N → ∞ (Komlós 1967; Tao-Vu result).
   So for typical random codebooks, K=N is not degenerate — the codebook is
   invertible (up to vanishingly small probability events).
2. **ACF rank-1 update / hard-threshold step:** The ACF step replaces
   `tanh(2·scores)` with `hard_threshold(scores, t)` and writes
   `e_new = sign(X_r.T @ alpha)` where `alpha` is a sparsified score
   vector. At K=N with t=0.05 and N=4096, `alpha` is sparse and
   `X_r.T @ alpha` is a *combination of column vectors* of X_r. When K=N,
   X_r is square: every direction in {±1}^N is reachable as a column
   combination. So in principle K=N is *more* expressive, not less.
3. **Resonator dynamics view (Frady-Sommer):** The OLS-weighted resonator
   has guaranteed fixed-point property when the codebook is well-conditioned.
   At K=N, condition number of a random ±1 matrix grows as O(√N), which is
   moderate but not catastrophic. OP (outer-product) weighting degrades
   more, but Frady-Sommer report OLS≈OP for large N.

**Why K=4096 might still dip at 83.3%:** The hard threshold t=0.05 in the
ACF step truncates *more* of the score vector when K is large (more columns
contribute small-magnitude scores). At K=N, the "easy" sparsity assumption
of ACF (a few large scores dominate) weakens. But this should manifest as a
smooth degradation, not a localised dip.

**My read:** K=4096's dip to 83.3% is 30-trial noise, NOT a square-codebook
artifact. The ACF capacity curve in the original paper goes well past K=N
(they sweep into K/N=2 and beyond) and shows no special K=N feature.

---

## 6. Candidate mechanisms ranked

| # | Candidate                                       | Plausibility | Evidence                                                                                                                                                                                             |
| - | ----------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | **(d) Seed-correlation artifact**               | **High**     | Same SEED=17 used across all K-levels. The 30 atom-sets are drawn from the same RNG stream; consecutive K's are correlated through shared RNG state. K=2944 specifically may have drawn a "hard" sample by luck.            |
| 2 | **(a) 30-trial noise (post-correction)**        | **High**     | Family-wise p ≈ 0.047. Barely significant. With 16-comparison correction, the dip is exactly the kind of "1 in 16 false positive" expected.                                                  |
| 3 | **(c) r-mis-tuning at K=2944**                  | Medium       | The r-schedule jumps in coarse 3-step ladder (0, 0.005, 0.010). The r=0.01 plateau spans K/N from 0.55 to 1.5+. Optimal r is K-dependent in the underlying physics. K=2944 may sit at a local optimum for r ≈ 0.008–0.009 rather than 0.010. |
| 4 | **(b) Real narrow resonance at K/N=23/32**      | Low          | No literature precedent. Other low-gcd ratios (17:32, 19:32, 21:32) do not dip. Number-theoretic explanation would need a specific mechanism (e.g., limit-cycle period commensurate with N), and none is published for bipolar resonators.    |

I rank: **(d) ≈ (a) > (c) > (b)**.

Combined plausibility: the dip is likely a **conjunction of (d) and (c)** —
specific seed pulled a hard sample at K=2944, and r=0.010 is slightly
suboptimal at that K, amplifying the difficulty.

---

## 7. Follow-up experiments (with predicted outcomes)

| # | Experiment                                                       | Decisive on              | Predicted outcome                                                                                                                          |
| - | ---------------------------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | **K=2944, 100 trials, SEED=17 (same seed)**                        | (a) noise vs systematic  | **70%** likely. If (a) dominates, repeat gives ~75% ±8 pp. If (b)/(c) dominates, stays near 50–60% with CI [0.45, 0.65].                          |
| 2 | **K=2944, 30 trials × 5 seeds ∈ {17, 23, 31, 7, 13}**                | (d) seed-correlation     | **70%** likely. If (d) dominates, distribution across seeds spans 40–80%, mean ≈ 73%. If (b) dominates, all 5 seeds cluster at 50–60%.                              |
| 3 | **K=2944, sweep r ∈ {0.007, 0.008, 0.009, 0.010, 0.011, 0.012, 0.015}, 30 trials each, SEED=17** | (c) r-mis-tuning         | **55%** likely effect. If (c) dominates, recovery has a minimum at r=0.010 with adjacent r values (0.008, 0.012) showing 65–75%. If (c) absent, all r values give 50% ±8 pp at the same seed. |
| 4 | **Re-run full K-sweep (16 levels) with 5 different seeds, 30 trials each** | Cliff substructure across seeds | If real, the K=2944 dip persists across seeds. If artifact, the dip migrates to a different K at each seed (random-position 1-in-16 outlier).          |
| 5 | **K=2944, 30 trials, with B=3 (three factors)**                  | Generalisation           | If real and B=2-specific (e.g., 2-cycle limit), the dip vanishes at B=3. If real and general (e.g., 23/32 number-theoretic), persists.                                |

**Recommended priority order:** #1 is cheapest and most decisive on the
single most likely explanation (noise). Run #1 first. If it pulls back to
~75%, the dip was noise — stop. If it stays at ~55%, run #2 and #3 in
parallel to discriminate seed-correlation vs r-mis-tuning.

**Cost note:** all of these are CPU-bound, 30-100 trials × 100 iters × 16
restarts × N=4096 dot products. Each trial is seconds. Full suite is hours,
not days.

---

## 8. Publication-grade verdict

**Headline material:** No. The K=2944 dip is not strong enough evidence of a
new resonator-capacity phenomenon to lead a paper.

**Methodological note material:** Yes, but only as a *negative result* —
"sub-step features in the recovery cliff are within binomial noise at 30
trials; we recommend ≥100 trials for fine-grained capacity characterisation."
This is useful for the resonator capacity literature, where 30 trials is
common but undersized for the precision people *imply* in their plots.

**For the two-bets story (small bet = HDC memory for LLM):** The ACF cliff
substructure is irrelevant. ACF is supporting infrastructure; the substrate
contribution is the *bundle/binding/cleanup observability layer*, not the
shape of the recovery curve.

**Worth following up if and only if:** experiment #1 (100 trials at K=2944)
shows recovery staying ≤60%. That would be the threshold for "real
sub-structure" with non-overlapping CIs. Even then, it is a small contribution
to the resonator capacity literature, not a research direction in itself.

**Brutal honesty:** This is a 1-hour follow-up to settle the question, not a
research project. Run experiment #1, get the answer, move on. The temptation
to read mechanistic stories into a single-level dip with family-wise p=0.047
is what produces overcooked papers. The literature has no precedent for
sub-step dips, and Occam's razor says: undersized trial count + seed
correlation + 16 simultaneous comparisons = one expected false positive.

---

## 9. Sources

- Kent, Frady, Sommer, Olshausen (2020). Resonator Networks, 2: Factorization
  Performance and Capacity Compared to Optimization-Based Methods. Neural
  Computation 32(12). arxiv:1906.11684. https://arxiv.org/abs/1906.11684
- Frady, Kent, Olshausen, Sommer (2020). Resonator Networks 1: An Efficient
  Solution for Factoring High-Dimensional, Distributed Representations of Data
  Structures. arxiv:2007.03748. https://arxiv.org/abs/2007.03748
- Langenegger, Karunaratne et al. (2024). On the Role of Noise in Factorizers
  for Disentangling Distributed Representations. arxiv:2412.00354.
  https://arxiv.org/abs/2412.00354 — ACF / IMF noise schedule; r is treated as a
  hyperparameter requiring search, not a closed-form K-dependent expression.
- Hersche, Terzić, Karunaratne et al. (2025). Factorizers for distributed
  sparse block codes. https://journals.sagepub.com/doi/10.3233/NAI-240713
- Capacity Analysis of Vector Symbolic Architectures (2023). arxiv:2301.10352.
  https://arxiv.org/abs/2301.10352
- Mirus et al. (2023). Validating an algebraic approach to characterizing
  resonator networks. Sci Rep. https://www.nature.com/articles/s41598-023-50089-1
- Recent Advances in Resonator Networks (2025 review).
  https://openreview.net/pdf?id=FNrZd3Ls1d
- Critical Dynamics and Cyclic Memory Retrieval in Non-reciprocal Hopfield
  Networks (2025). arxiv:2501.00983.
  https://arxiv.org/abs/2501.00983 — limit-cycle phase between memory and
  no-memory regimes; nearest analog mechanism to a localised cliff dip.
- IBM in-memory-factorizer code. https://github.com/IBM/in-memory-factorizer
- Spencer Kent's resonator-networks reference implementation.
  https://github.com/spencerkent/resonator-networks
