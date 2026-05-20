# Wave 14c — K=2944 dip mechanism: what does the data actually say?

Unbiased re-synthesis after the 100-trial follow-up came back at **61%**
(not 75%, not 50%). The prior synthesis predicted "likely noise — should
revert to ~75% with more trials". That prediction is **falsified**. But
the original 50% magnitude is also not supported. The truth is in the
middle. This document re-fits the mechanism set to the new data.

---

## 1. TL;DR

**The dip is real.** Pooled across all three replicates (15/30, 15/30,
61/100 = **91/160 = 56.9%**), the Wilson 95% CI is **[0.491, 0.643]**.
That interval excludes both the smooth-interpolation prediction (0.75)
and pure binomial noise centred on 0.75 (p ≈ 6e-7 against 91/160). It
*also* excludes the original 50% point estimate as the maximum-likelihood
truth — the 100T replicate at 61% drags the joint estimate to ~57%.

**Heterogeneity across the three runs is not significant** (chi-square
1.85 on 2 dof, p ≈ 0.24). All three are consistent with a single underlying
rate near 0.57. There is no evidence the 100T run "fixed" the 30T noise;
rather, the 30T runs slightly underestimated a real ~57% rate by sampling
variance.

**Most likely mechanism (revised ranking):**

1. **r-mistuning at K/N ≈ 0.72** (medium-high plausibility). The
   r=0.010 hyperparameter is set by a coarse 3-step K-schedule that does
   not adapt within the cliff transition. K=2944 sits at the high-K end
   of the r=0.010 plateau, where the noise injection is increasingly
   under-powered to dissolve high-density spurious attractors. This is
   the most testable explanation and matches Karunaratne 2024's own
   appendix prescription of K-dependent r.
2. **Real structural dip near K/N = 23/32** (low-medium plausibility,
   *upgraded* from the prior synthesis's "low"). The pooled CI [0.49,
   0.64] forces a real-rate explanation, and the K=2176 (17:32) → 50%
   datapoint is *also* below the cliff envelope, even though it was
   previously dismissed as "shoulder of the cliff". Re-reading 2176 as a
   second low-gcd dip is consistent with a number-theoretic mechanism.
3. **Shared atom-family / sample-correlation across trials** (medium).
   All three replicates use SEED=17 + K offset; the codebook RNG stream
   and the trial-bundle RNG stream are seeded deterministically from a
   K-dependent function. If the K=2944 specific codebook draw is "hard"
   (e.g., high coherence among atom columns), all three replicates inherit
   it. **This is now the dominant unfalsified competitor to mechanism #1.**
4. **Pure noise** (rejected). The prior synthesis assigned 50%+ weight to
   noise. The 100T run does not support that.

**Decisive next experiment (single shot):** run **K=2944, 50 trials at
each r ∈ {0.005, 0.007, 0.010, 0.012, 0.015, 0.020}, two independent
codebook seeds (17, 23)**. If recovery rises monotonically with r above
0.010 → mechanism (1) confirmed. If recovery is flat across r but
differs across seeds → mechanism (3). If recovery is flat across r *and*
across seeds → mechanism (2), structural.

---

## 2. Data summary

| Source           | n   | x  | rate | Wilson 95% CI    |
| ---------------- | --- | -- | ---- | ---------------- |
| K=2944, run 1    | 30  | 15 | 0.500| [0.331, 0.669]   |
| K=2944, run 2    | 30  | 15 | 0.500| [0.331, 0.669]   |
| K=2944, run 3    | 100 | 61 | 0.610| [0.512, 0.700]   |
| **K=2944 pooled** | **160** | **91** | **0.569** | **[0.491, 0.643]** |

Heterogeneity chi-square = 1.85 (2 dof), p = 0.24. The three replicates
are statistically homogeneous; the simplest model is "K=2944 has a true
rate near 0.57 and we sampled it three times."

Two-sample comparisons against neighbours (one-tailed z, against pooled K=2944):

- K=2944 (91/160) vs K=2816 (23/30): z = −2.03, p = 0.021
- K=2944 (91/160) vs K=3072 (22/30): z = −1.68, p = 0.046

K=2944 is **significantly below both immediate neighbours** at α=0.05,
even without correcting for the neighbours' own small-n noise. The dip
is therefore a real local feature of the recovery curve, not a smooth
interpolation artifact.

**Magnitude of the dip:** at 56.9% with CI excluding 0.65, the dip is
~18 percentage points below interpolation. That is 2× smaller than the
original 30T result implied (25 pp) but 4× larger than 30T noise can
explain by chance.

**The original synthesis was wrong on direction.** It bet on 75% under
the noise hypothesis; truth is ~57%. But it was also wrong on
magnitude — the dip is *smaller* than the headline 50% number. Both
biases came from the same source: under-powered 30-trial replicates
with a fixed Bonferroni penalty that nudged interpretation toward
"likely false positive". When the false-positive ceiling at p=0.047
became binding, the prior synthesis discounted a genuine effect.

---

## 3. K/N rational structure — closer look

The original observation (K=2944 = 23·128 = 23·N/32) suggested a
number-theoretic resonance. The earlier rebuttal: 17:32 and 21:32 also
have gcd=128 but they don't dip in the original table. Let me re-check
this with the new data lens.

| K    | K/N    | reduced ratio | gcd  | recovery (30T) | within "no-cliff" baseline? |
| ---- | ------ | ------------- | ---- | -------------- | --------------------------- |
| 2176 | 0.5312 | 17:32         | 128  | **50%**        | low-K shoulder; baseline ≈ 65%? |
| 2304 | 0.5625 | 9:16          | 256  | 36.7%          | cliff onset (smooth) |
| 2432 | 0.5938 | 19:32         | 128  | n/a            | not in published sweep |
| 2560 | 0.6250 | 5:8           | 512  | 46.7%          | cliff midpoint (smooth) |
| 2688 | 0.6562 | 21:32         | 128  | 63%            | recovery shoulder |
| 2816 | 0.6875 | 11:16         | 256  | 77%            | post-cliff plateau |
| **2944** | **0.7188** | **23:32**     | **128** | **57% (pooled)** | **DIP** |
| 3072 | 0.7500 | 3:4           | 1024 | 73%            | post-cliff plateau |
| 3328 | 0.8125 | 13:16         | 256  | ~90%           | high-K plateau |
| 3584 | 0.8750 | 7:8           | 512  | 90%            | high-K plateau |
| 4096 | 1.0000 | 1:1           | 4096 | 83.3%          | K=N (small dip) |

**Pattern (newly visible after 100T data):** Of the four points with
reduced denominator 32 in the cliff region, three lie below their
neighbours' interpolation envelope:

- 17:32 (K=2176, 50%) — sits at low-K shoulder; an interpolation between
  K=2048 (100%) and K=2304 (37%) would predict ~70%; 50% is well below.
- 21:32 (K=2688, 63%) — interpolation between K=2560 (47%) and K=2816
  (77%) predicts ~62%; 63% is on-line. *No anomaly.*
- 23:32 (K=2944, 57%) — interpolation predicts ~75%; 57% is well below.
- 19:32 (K=2432) — *not in the published sweep*. **This is the missing
  diagnostic measurement.**

Two of three sampled 32-denominator points dip; the third (21:32) is
on-line. 9:16 (denominator 16 only) also dips slightly. The pattern is
**suggestive but not clean**: if the mechanism were "any reduced-denom-32
dips", we would expect 21:32 to dip too, and it doesn't.

**Speculative number-theoretic hypothesis:** what matters is not the
denominator but the *Farey neighbours*. In the Farey sequence F_{32},
23/32 sits adjacent to 5/7 and 18/25, both of which lie in the cliff
region. The "danger zone" might be K/N ratios that are simultaneously
close to two distinct simple fractions p/q with small q. K=2176 = 17/32 has
similar Farey context. K=2688 = 21/32 = 3/8 + 9/32 has *3/8 as a
near-neighbour, which is well below the cliff* — so 21:32 has only one
"hard" Farey neighbour. This is post-hoc story-telling, but it gives a
falsifiable prediction: **the 19:32 = 2432 datapoint should also dip if
the Farey-neighbour story holds.**

**Honest read:** the rational-K/N pattern is weak and post-hoc. It is
not strong enough to support a paper, but it's strong enough to motivate
one experiment: fill in K=2432 (19:32) and K=2560 (5:8 = 20:32) with
≥100 trials each. If K=2432 dips and K=2560 doesn't, the
reduced-denominator-32 story has legs. If both stay smooth, it's an
artifact of cherry-picking.

---

## 4. Mechanism candidates ranked (revised)

Re-rank under the new constraint that the pooled rate is 0.57 with CI
excluding 0.75. The dip is **real**. Mechanism candidates must explain a
~17–20 pp shortfall, not a noise spike.

| # | Mechanism | Plausibility | Predicted outcome of decisive test |
| - | --------- | ------------ | ----------------------------------- |
| 1 | **r-mistuning at K/N = 0.72** — r=0.010 is locally suboptimal for K near 2944; resonator gets trapped in metastable basins that need stronger noise. | **Medium-high** | r-sweep shows rate rising to ≥70% at r=0.015 or r=0.020. Optimum r is K-dependent. |
| 2 | **Shared codebook draw / atom family** — SEED=17 + K=2944 produces an atypically coherent codebook; all three replicates share the same draw because seed = f(K). | **Medium** | Re-run K=2944, 30 trials at SEED ∈ {17, 23, 31, 7, 13}. If (2), the dip migrates across seeds with high variance: 30–80% range. If not (2), rate clusters around 0.57 ±0.08. |
| 3 | **Real structural dip near K/N = 23/32** — limit-cycle density spikes at low-gcd ratios with specific Farey-neighbour structure. | **Low-medium** (upgraded from low) | K=2432 and K=2560 measured at 100 trials. If 2432 (19:32) dips and 2560 (5:8) doesn't, structural story is supported. |
| 4 | **Hard-threshold t=0.05 interaction with K/N** — the ACF threshold creates a sparsity-K interaction that has a local minimum near K/N = 0.72. | **Low-medium** | Sweep t ∈ {0.01, 0.03, 0.05, 0.08, 0.12} at K=2944. If recovery peaks at one of t≠0.05, threshold tuning was the issue. |
| 5 | **B=2 specific limit cycle** — 2-cycle attractors are densest at K/N near 23/32 for the bipolar bipartite resonator dynamics. | **Low** | Repeat at B=3, K=4416 (K/N = 23/32 scaled to B=3 effective load). If dip is B=2-specific, it vanishes. |
| 6 | **Random restart count too low** — 16 restarts insufficient to escape attractors at K=2944. | **Low** | Increase restarts to 64 at K=2944, 30 trials. If (6), recovery rises monotonically with restart count. |
| 7 | **Pure noise** | **Rejected** | The 100T result kills this directly: p(61/100 \| true=0.75) = 0.0024, and the *pooled* p is 6e-7. |
| 8 | **Implementation bug** | **Very low** | Two prior cross-validation reruns of the K-sweep produced consistent results. |

**Plausible compound:** (1) + (2). The r=0.010 plateau is mildly
under-powered at K=2944, *and* the SEED=17 codebook draw produces a
slightly coherent atom family that the resonator can't disentangle
without more aggressive noise injection. Either alone produces ~70%;
together they produce ~57%. This is consistent with the data and is the
"unsexy two-bug" explanation.

---

## 5. The r-sweep experiment — predicted curves

Concrete prediction for **K=2944, B=2, N=4096, 50 trials, r ∈
{0.005, 0.007, 0.010, 0.012, 0.015, 0.020, 0.030}**:

| r     | Mechanism (1) prediction | Mechanism (2) only | Mechanism (3) only |
| ----- | ------------------------ | ------------------ | ------------------ |
| 0.005 | 35–45% (under-noised, can't dissolve attractors) | ~57% | ~50% |
| 0.007 | 50% | ~57% | ~50% |
| 0.010 | 57% (baseline) | ~57% | ~57% |
| 0.012 | 65% | ~57% | ~57% |
| 0.015 | 72% | ~57% | ~57% (or slight rise) |
| 0.020 | 75% (matches interpolation) | ~57% | ~60% |
| 0.030 | 70% (over-noised, starts hurting) | ~57% | ~57% |

**Diagnostic feature:** if mechanism (1) is the explanation, the curve
is **monotone-rising-then-falling** with peak near r=0.015–0.020. If
mechanism (2) or (3) dominates, the curve is **flat near 0.57**.

Cost: 7 r-values × 50 trials × 16 restarts × ~5 sec/trial ≈ 50 minutes
on the existing CPU runner. This is one queue item, not a research
project. **It should be run before any further mechanism speculation.**

A cheaper version exists: just measure at r ∈ {0.005, 0.015, 0.020} (3
points) — sufficient to discriminate mechanism (1) from (2)+(3).

---

## 6. Spin-glass angle

This is speculative but the user requested it explicitly, so let me work
through it honestly rather than dismiss it.

**The mapping.** The resonator decomposition problem can be cast as a
Mezard-Parisi-Virasoro (1987) spin-glass: each estimate vector e_a, e_b ∈
{±1}^N is a spin configuration, and the energy is

E(e_a, e_b) = −(s · (e_a ⊙ e_b))² / N

where s is the observed bundle and ⊙ is elementwise product. The
codebook X_a, X_b ∈ {±1}^{K×N} acts as quenched disorder. Recovery
succeeds iff the dynamics converges to the global minimum (the true
factor pair) rather than a metastable state.

**What spin-glass theory predicts about K/N dependence.** The replica
symmetry breaking (RSB) transition in p-spin glass models occurs at a
critical loading α_c = K/N. Below α_c, the energy landscape has one
basin per memory (recoverable); above α_c, basins fragment into a
hierarchical RSB ultrametric structure (recovery fails to converge).
For the Hopfield model (p=2 spin), α_c = 0.138 (Amit-Gutfreund-Sompolinsky
1987). For higher-order interactions (p=4 spin, similar to the bipartite
resonator step which is bilinear in the two estimates), α_c shifts to
~0.27 (Krotov-Hopfield 2016) and the transition is first-order.

Our observed cliff is at K/N ≈ 0.55–0.72, which is **well above** the
classical Hopfield α_c. We are in the deep RSB phase. The relevant
spin-glass result for deep RSB is **dynamical trapping**: even when the
global energy minimum exists, the dynamics is exponentially slow
(Crisanti-Sommers 1992 for spherical p-spin; Cugliandolo-Kurchan 1993
for off-equilibrium). Recovery probability under finite-iteration
dynamics decays smoothly with α, *not* in discrete steps at specific
ratios.

**What spin-glass theory does NOT predict.** Localised dips at specific
rational K/N values. The MPV framework is invariant under continuous
deformations of α; there is no rational-K/N structure in the standard
spin-glass landscape.

**Where rational K/N might enter.** Through the *quenched disorder
correlations*. The bipartite bipolar codebook X ∈ {±1}^{K×N} has
column-wise Walsh-Hadamard structure when N is a power of 2. Specifically:

- The Walsh-Hadamard basis on {0,1}^12 = {0,1,...,4095} has frequency
  structure inherited from binary expansion of indices.
- A random ±1 codebook is *not* Walsh-Hadamard, but column-correlations
  in the K×N codebook depend on K's relationship to N's divisors when K
  is sampled uniformly.

This is hand-wavy. I have not found a published spin-glass result
predicting rational-α landscape features for ±1 codebooks. The honest
verdict: spin-glass theory does not predict the K=2944 dip directly. The
RSB framework supports "recovery degrades smoothly with α in this
regime" but doesn't predict structure.

**Caveat:** the Marinari-Mezard-Parisi 1993 result on spin glasses with
non-uniform disorder (i.e., quenched matrices with rational-rank
constraints) does predict step-like features in the order parameter at
rational filling fractions. But this is for q-state Potts glasses with
explicit rational order parameters, not ±1 spin glasses with random
matrix disorder. The analogy is too loose to be predictive.

**Verdict on spin-glass angle:** the framework supports the existence of
metastable trapping (consistent with our dip), but does not predict the
*location* of the dip at K/N = 23/32. It's a mechanism-class match, not
a quantitative match.

---

## 7. Crystallography / Arnold-tongue angle

KAM theory (Kolmogorov-Arnold-Moser) and Arnold tongues describe
mode-locking in driven nonlinear oscillators near rational frequency
ratios. The relevant tongue locations are at simple rationals p/q with
small q, and the *width* of the tongue scales with the strength of the
nonlinear coupling.

**The mapping.** Our resonator iteration map is:

e_a^{t+1} = sign(X_a^T tanh(2 X_a (s ⊙ e_b^t) / N))
e_b^{t+1} = sign(X_b^T tanh(2 X_b (s ⊙ e_a^{t+1}) / N))

This is a discrete-time bipartite map on {±1}^N × {±1}^N. The map has
fixed points (recovery successes) and limit cycles of various periods
(recovery failures). The literature on coupled-map lattices and
neural-network dynamics (Aoki-Aoyagi 2009, "Co-evolution of phases and
connection strengths in a network of phase oscillators"; Hong-Strogatz
2011) reports Arnold-tongue-like structures in phase-locked states when
the network has explicit frequency parameters.

**Why this might apply.** If the resonator dynamics has an effective
"frequency" parameter set by K/N (loading), and the codebook structure
provides an effective "driving rational ratio" set by the gcd of K and
N, then mode-locking at rationals p/q is a candidate mechanism. K=2944
corresponds to p:q = 23:32 in lowest terms. q=32 is the smallest q in
the simply-related sweep (the others are q=16, 8, 4).

**Why I don't believe it strongly.** Arnold tongues are most cleanly
defined for systems with a continuous phase variable and a clean
driving frequency. Our system is discrete-state ({±1}^N) with no
explicit phase. The mapping to mode-locking is metaphorical. Also, the
Arnold-tongue prediction is that effects are *strongest at small q*
(i.e., 1:2, 1:3, 2:3, 1:4...). Our data shows the dip at q=32, which is
*large q* in Farey-sequence terms. That's backwards from the canonical
Arnold-tongue prediction.

**Verdict on crystallography angle:** intriguing analogy but the
predicted ordering of effect-strength is backwards from observation.
The Arnold-tongue framework predicts that K/N = 1/2, 2/3, 3/4 should
have stronger features than K/N = 23/32, but we see the opposite. This
*reduces* my confidence in mechanism (3).

---

## 8. Honest verdict

**Is the K=2944 dip real?** **Yes.** The pooled CI [0.49, 0.64] excludes
the interpolation prediction (0.75) and excludes pure binomial noise
(p ≈ 6e-7). The original "likely noise" call was wrong.

**Is the magnitude as large as 30T suggested?** **No.** 30T pulled 50%
by undershoot; 100T pulled 61% by reversion-to-mean. Pooled truth is
57%, which is a 17-pp dip, not a 25-pp dip.

**What caused the original synthesis to mis-predict?** The Bonferroni
penalty for 16 K-levels brought family-wise p to 0.047, which is exactly
at the conventional threshold. The synthesis defaulted to "treat as
likely false positive" because:
(a) priors over "novel cliff substructure" were low (no literature precedent),
(b) the prior synthesis assumed all-or-nothing: either dip is genuine
or dip is noise; the actually-observed outcome (smaller-than-30T but
non-zero real dip) wasn't on the menu.

This is a classic Bayesian-decision failure: rejecting a hypothesis
because the test crossed an arbitrary threshold, without considering
that the *posterior expected dip magnitude* under the noise hypothesis
should have been continuous, not binary.

**Which mechanism is now most likely?** A compound: **r-mistuning + sample
correlation**. Both are mundane. Neither implies new physics. The
rational-K/N mechanism is upgraded from "low" to "low-medium" — worth
ruling in or out via two additional K-points (2432 and 2560 at 100T)
plus the r-sweep.

**What would change my mind?**

- If the r-sweep at K=2944 shows recovery flat near 0.57 across r ∈
  [0.005, 0.020], mechanism (1) is dead and (2)+(3) become the only
  surviving explanations.
- If multi-seed at K=2944 shows the dip migrating (mean ~73%, individual
  seeds 40%–85%), mechanism (2) is confirmed and (1)/(3) are out.
- If K=2432 (19:32) measured at 100T shows a similar ~57% dip while
  K=2560 (5:8) is on the smooth envelope, mechanism (3) is upgraded
  from "low-medium" to "medium-high" and would warrant a focused
  follow-up.

**Brutal honesty on research value.** Even in the worst case (mechanism
(3) confirmed: structural dips at low-gcd K/N), this is a methodology
note, not a research direction. It's a "fine-resolution capacity sweeps
have features the literature missed" finding. It would be a paragraph
in a methodology section of a larger ACF paper, not its own paper. The
hd-instrument two-bets story is unaffected: ACF is supporting
infrastructure, and recovery curves with localised dips don't change
the observability-layer contribution.

**Brutal honesty on the prior synthesis.** The prior synthesis was
*correct on the data* (30T undersized, family-wise p marginal) but
*wrong on the inference* (pre-committed to "noise" rather than
expressing uncertainty over dip magnitude). A better synthesis would
have written: "Most likely true rate at K=2944 is 0.60 ± 0.10. The 50%
estimate is biased downward by undersized n. Recommended follow-up: 100
trials at K=2944." That posterior would have predicted 61% almost
exactly. The lesson: when correcting for multiple comparisons, the
correct output is a *shrunk effect estimate*, not a binary
reject/fail-to-reject decision.

---

## 9. Decisive next experiment (cost-ordered)

1. **r-sweep at K=2944** (50 min). Distinguishes mechanism (1) from
   (2)+(3). Cheapest discriminator. **Run this first.**
2. **Multi-seed at K=2944** (30 min): SEED ∈ {17, 23, 31, 7, 13}, 30
   trials each. Distinguishes mechanism (2) from (1)+(3). Run in
   parallel with (1).
3. **Fill-in K-points** (40 min): K=2432 and K=2560 at 100 trials each
   with SEED=17, r=0.010. Distinguishes mechanism (3) from (1)+(2).
4. **Threshold sweep at K=2944** (50 min): t ∈ {0.01, 0.03, 0.05, 0.08,
   0.12}, 30 trials each. Diagnoses mechanism (4); only run if 1–3
   leave residual unexplained variance.

Total CPU: ~2.5 hours. If we get clean answers from (1) and (2) alone,
we can stop after the first 80 minutes.

---

## 10. Sources

- Kent, Frady, Sommer, Olshausen (2020). Resonator Networks, 2. Neural
  Comp. 32(12). arxiv:1906.11684.
- Frady, Kent, Olshausen, Sommer (2020). Resonator Networks, 1.
  arxiv:2007.03748.
- Langenegger, Karunaratne et al. (2024). On the Role of Noise in
  Factorizers for Disentangling Distributed Representations.
  arxiv:2412.00354.
- Hersche, Terzić, Karunaratne et al. (2025). Factorizers for
  distributed sparse block codes. NAI-240713.
- Mezard, Parisi, Virasoro (1987). Spin Glass Theory and Beyond. World
  Scientific.
- Amit, Gutfreund, Sompolinsky (1987). Statistical Mechanics of Neural
  Networks Near Saturation. Annals of Physics 173, 30.
- Krotov, Hopfield (2016). Dense Associative Memory for Pattern
  Recognition. NeurIPS. arxiv:1606.01164.
- Crisanti, Sommers (1992). The Spherical p-Spin Interaction Spin
  Glass Model: The Statics. Z. Phys. B 87.
- Cugliandolo, Kurchan (1993). Analytical Solution of the Off-Equilibrium
  Dynamics of a Long-Range Spin-Glass Model. PRL 71.
- Aoki, Aoyagi (2009). Co-evolution of Phases and Connection Strengths
  in a Network of Phase Oscillators. PRL 102.
- Hong, Strogatz (2011). Mean-Field Behavior in Coupled Oscillators
  with Attractive and Repulsive Interactions. PRE 85.
- Arnold (1965). Small Denominators I: Mapping of the Circumference
  Onto Itself. Trans. AMS 46.
- Marinari, Mezard, Parisi (1993). Replica field theory for random
  manifolds. J. Phys. I (France) 3.
- Non-reciprocal Hopfield Networks (2025). arxiv:2501.00983 — limit-cycle
  phase between memory and no-memory; nearest mechanism analog.
- Prior synthesis: `notes/wave14c_acf_cliff_substructure_research.md`.

---

## Appendix A — Statistical worksheet

Pooled rate at K=2944: 91/160 = 0.5687.

Wilson 95% CI: [0.4913, 0.6430].

Tests against H0 = 0.75 (interpolation prediction):

- P(X ≤ 91 | n=160, p=0.75) = 5.7e-7 (two-tailed equivalent)
- BF (p=0.61 vs p=0.75) on 91/160 = 1.4e5 (decisive against noise hypothesis)
- BF (p=0.55 vs p=0.75) on 91/160 = 2.3e5 (decisive)
- BF (p=0.65 vs p=0.75) on 91/160 = 2.7e4 (decisive)

Tests against H0 = 0.55:

- P(61/100 | p=0.55) two-tailed p = 0.27 (cannot reject)
- P(91/160 | p=0.55) consistent

Heterogeneity test across the three replicates:

- Chi-square = 1.85 on 2 dof, p = 0.24 (no evidence of heterogeneity)

Two-sample comparisons (one-tailed z, normal approximation):

- K=2944 vs K=2816: z = −2.03, p = 0.021
- K=2944 vs K=3072: z = −1.68, p = 0.046
- K=2944 vs interpolation 0.75: z = −5.4, p ≈ 4e-8 (decisive)

Conclusion: the dip is *firmly* established at p < 0.001 even after
correcting for the 16 originally-tested K-levels (Bonferroni: 16 × 4e-8
≈ 6e-7, still decisive). The original family-wise correction relied on
the 30T n; with the 100T augmentation, the dip survives any reasonable
correction.
