# Stein Prediction #1 rejection — literature-grounded synthesis

Returned 2026-05-19. Unbiased deep research on why random replay at K=4
is **BWT-positive AND pre-shift-neutral** when wave14b Stein synthesis
predicted it should hurt pre-shift bpc. The Stein prediction #1 failed;
this note diagnoses why, surveys what the actual replay literature says
about the asymmetry, and lists rescue framings for the broader bias-
variance picture.

## TL;DR

Random replay being BWT-positive AND pre-shift-neutral is **the modal
empirical finding in the continual-learning replay literature**, not a
surprise. The (2B-1)/N variance argument is the wrong knob: pre-shift
bpc is bottlenecked by W's joint capacity over the replay-augmented
stream, which is gradient-coupled (interference), not by per-sample
estimator variance. The Stein framing survives in restricted forms
(retrieval, fusion, β), but the "replay is a Stein shrinkage estimator
on W" mapping is now falsified.

## 1. What the replay literature actually says about asymmetry

The asymmetry "BWT-positive AND pre-shift-neutral" is the *expected*
shape, not the surprise. Five independent literature lines say so.

### 1.1 Buzzega DER / DER++ (2020, arXiv:2004.07211) — empirical baseline

DER stores past LOGITS in a reservoir and replays them with a KL term.
Reported across Split-CIFAR-10, Permuted-MNIST, Class-Inc-CIFAR-100:
DER and even plain ER+reservoir lose ZERO accuracy on the current task
vs no-replay, while gaining 5-15 points of average accuracy from BWT
recovery. The plasticity-loss term ("interference between rehearsal and
new data") is reliably below noise for replay fractions up to ~0.5. The
"Rethinking ER" follow-up (arXiv:2010.05595) explicitly diagnoses what
DOES hurt plasticity: bias balancing (off), augmentation (off), loss
balancing (off). Sample-count of replay itself is NOT on the list.

**Mechanism Buzzega gives**: with reservoir sampling, the replayed
batch is statistically a sample of the joint training distribution. The
gradient direction it pushes on is approximately the same gradient SGD
would compute under multi-task joint training — which IS the
information-theoretic upper bound for what W can achieve.

### 1.2 Lin 1992 (Machine Learning 8) — rehearsal ≈ joint training

Lin's original experience-replay paper (DOI:10.1007/BF00992699) makes
the point Buzzega formalizes: replaying past transitions with current
ones makes the SGD trajectory equivalent in expectation to joint
training over the union of distributions. The "pre-shift cost" of
replay is the *gradient noise* introduced by mismatch between the
true joint distribution and the replay-buffer's sample. With reservoir
or uniform random replay over the whole pool, this mismatch is *zero
in expectation*. So pre-shift cost is exactly seed noise.

Implication: pre-shift bpc being flat across rf ∈ {0, 0.25, 0.5, 0.9}
is the Lin-1992 prediction. The Stein prediction (replay = pure bias
when variance is already small) ran orthogonal to this.

### 1.3 Rolnick et al. 2018 (arXiv:1811.11682) — ER for general CL

Rolnick et al. study large-buffer ER on Atari and report: ER at
fractions up to 0.5 of buffer-to-stream ratio does not hurt current-
task return, even in regimes where the current task is highly novel.
They explain via "implicit multi-task objective" — same argument as
Lin and Buzzega.

### 1.4 Wang et al. 2024 survey (arXiv:2302.00487) — stability-plasticity
isn't symmetric

Wang's survey explicitly notes (Sec 3.2, Sec 5.1) that replay methods
predominantly trade compute for stability, NOT plasticity. The
plasticity tax shows up only when (a) buffer is biased toward an early
task, (b) loss term over-weights rehearsal, or (c) buffer samples lie
on the new-task data manifold and create direct gradient conflict. Plain
random replay over a reservoir-style pool avoids all three.

### 1.5 Lyle et al. / Klein 2025 (arXiv:2503.20018) — replay ALSO
recovers plasticity

The 2025 finding is even stronger: in continual settings with extended
training, replay doesn't just leave plasticity alone — it actively
*prevents* the loss-of-plasticity phenomenon (Dohare et al., Nature
2024, PMC11338828). The mechanism: random replay keeps the gradient
distribution stationary, which prevents the dead-unit / saturated-
activation cascade Dohare diagnosed.

**Bottom line**: the BWT-positive / pre-shift-neutral asymmetry is what
the literature says replay does. The Stein-paradox framing predicted
the opposite of the established empirical pattern. The wave14b
synthesis pulled too hard on the bias-variance analogy.

## 2. Why the (2B-1)/N variance argument fails — precise diagnosis

The wave14b Stein argument was:
> bundle decomposition signal-to-noise is sqrt(N/(2B-1)); at K=4, B=5,
> N=4096 → variance ≈ 0.0022. So we are in the LOW-variance regime, and
> random replay (which has zero relevance to the current minibatch) is
> all bias, no useful variance reduction. Therefore replay = pure bias
> = pre-shift hurt.

Four things are wrong with this:

### 2.1 (2B-1)/N is the *retrieval* variance, not the *training-objective*
variance

The Plate/Frady-Sommer derivation gives variance of the cosine score
between a bundle-extracted atom and a codebook entry. That's the
variance of an *output* of pool retrieval. The training objective for
W is byte-CE on the input stream; the retrieval cosine doesn't appear
in W's gradient at all under random replay. So (2B-1)/N is not the
operative noise term in the bias-variance decomposition of W.

Even more directly: at K=4, replay doesn't even invoke the bundle —
random replay re-samples bytes from past contexts, computes their
4-grams, and feeds them as additional training examples. Bundle-
decomposition variance is irrelevant to whether replay hurts pre-shift.

### 2.2 Stein's regime variable is dim(parameter), not bundle size

Stein dominance requires k ≥ 3 components in θ. Our parameter is W,
which has 256 × 4096 entries — k = ~10^6. The "low-variance regime"
in Stein is per-component σ²/||X||² — when this is small, JS
shrinkage savings vanish but JS does NOT hurt. Stein's theorem is
ASYMMETRIC: dominance is one-sided. Even in the "low-variance regime,"
JS isn't worse than MLE, just not better. So even if the Stein analogy
held, the prediction "replay hurts pre-shift" wasn't a Stein
prediction — it was an extra step grafted on.

This is the precise failure mode the user's
[don't-overextend-theorems] memory rule warns about. Stein's theorem
says "JS dominates"; it does NOT say "non-optimal shrinkage hurts."

### 2.3 BSC ±1 carriers violate Gaussianity, but not the way assumed

The wave14b synthesis worried about Gaussianity of the carriers. The
actual problem is different: even granting "approximate Gaussianity"
via CLT on the sum-bundle, the noise in W's *gradient update* is NOT
distributed like the noise Stein's theorem assumes (independent
Gaussian observations of a fixed mean θ). Delta-rule training gives
W_t+1 = W_t - η (W_t x - y) x^T. The "noise" is the data distribution
x ~ p_t plus its target y, which is structured (Markov-correlated
4-grams of English text). This is closer to a Robbins-Monro stochastic
approximation problem than to a one-shot Stein estimation problem.

### 2.4 Replay does NOT shrink W toward zero or any fixed prior

Stein shrinkage moves the estimator toward a *prior mean*. Random
replay moves W toward the joint-distribution optimum (Lin 1992
argument). These are different operations:
- Stein: θ_JS = θ_MLE + s · (μ_prior - θ_MLE)
- Random replay: W_replay = argmin_W E_{joint} L(W) ≠ argmin_W E_{B} L(W) + λ ||W||²

There is no Stein-like prior implicit in random replay. The wave14b
synthesis got this wrong: it treated "average gradient over old
batches" as a shrinkage operation, but average gradient over the
mixture distribution is just SGD on the mixture, not shrinkage.

### Net diagnosis

The (2B-1)/N number applies to retrieval calibration (the wave14b
**bundle LLR factor 2/(B-1) calibration** is a legitimate Stein-shaped
finding — Frady-Sommer-LLR cited at the bottom of wave14b). It does
NOT apply to W training under replay. The synthesis confused two
distinct estimator problems.

## 3. Alternative theoretical framings, ranked

Five candidate framings that PREDICT BWT-positive AND pre-shift-neutral.
Rank is by how cleanly each explains the K=4 result, not by how famous
the framing is.

### Rank 1 — Lin-style multi-task equivalence (BEST FIT)

Lin 1992, formalized by Rolnick 2018 and Buzzega 2020. Random replay
makes the empirical training distribution at step t closer to the
joint distribution over past + present. SGD on a stationary mixture is
unbiased for the joint optimum. So:
- Pre-shift bpc moves toward the JOINT optimum, which is at most
  ε-worse than the pre-shift-only optimum, where ε = additional
  irreducible loss from sharing W between two distributions. At K=4
  on this corpus, A and B share atoms so ε ≈ 0. **PREDICTION: flat
  pre-shift across rf. CONFIRMED.**
- Post-shift bpc on A retains because A's distribution is still
  in W's training set. **PREDICTION: BWT-positive monotone in rf.
  CONFIRMED on Phase B.**

What this framing requires: (i) reservoir-like sampling (uniform over
the whole past stream, which our setup approximates), (ii) replay
fraction within "implicit multi-task regime" (under ~0.5; at rf=0.9
the framing predicts mild plasticity hit — we see +0.005 bpc which
is within seed noise but consistent in sign).

### Rank 2 — Linear mode connectivity (Mirzadeh-Farajtabar 2020,
arXiv:2010.04495)

LMC: the loss surface of CL has the property that the multi-task
minimum and the sequentially-trained minimum are connected by linear
paths of low error, IF the optimization is regularized toward the
shared region. Random replay is the simplest such regularization.

Prediction for our setup: small replay fractions should be enough to
keep W in the LMC region between A-optimum and joint-optimum. At
K=4 with similar A and B distributions, this region is wide → no
plasticity tax. Consistent with our data.

This framing predicts a knee: when A and B become more dissimilar
(e.g., compare across natural language vs code corpora), pre-shift
SHOULD start to suffer at high rf. Falsifiable.

### Rank 3 — Plasticity-preservation through stationary gradient
distribution (Dohare 2024, Klein 2025)

Dohare (Nature 2024) shows backprop networks lose plasticity in
continual settings via dead units and gradient-variance collapse.
Klein 2025 (arXiv:2503.20018) shows replay PREVENTS this. Mechanism:
random replay keeps the gradient distribution stationary, which keeps
the effective rank of the feature representation full.

For OUR substrate this matters less directly (we don't have deep
features, W is shallow Hebbian), but the principle applies: replay
keeps W's row-norms balanced and prevents single-mode collapse.
Predicts BWT-positive (no collapse) AND pre-shift-neutral (no
gradient-direction starvation).

### Rank 4 — Aljundi MIR / gradient-interference framing (2019,
arXiv:1908.04742)

MIR's premise: random replay hurts only when replay gradients
*interfere* with current gradients (loss surface curvature
misalignment). Plain random replay has zero EXPECTED gradient
interference if the buffer is unbiased; the variance is what matters.

For our K=4 setup, A and B are similar enough that the average MIR
score is low — gradient interference is mostly orthogonal. So replay
adds variance but no bias. The variance gets absorbed by SGD
averaging. Predicts pre-shift neutral. This framing is closely
related to Rank 1 but emphasizes the gradient-geometry view.

### Rank 5 — Noise injection / implicit regularization

Orvieto 2023 (arXiv:2206.04613), Camuto 2021 (arXiv:2102.07006):
noise injection during training implicitly penalizes high-frequency
components in the Fourier domain and produces calibrated classifiers
with large margins. Random replay is effectively a (correlated) noise
injection on the training distribution.

This is the BRUTAL-HONESTY framing: maybe the result is just "all
SGD-ish learning is robust to bounded noise injection, and random
replay is bounded noise." Predicts pre-shift neutral up to noise-level
caps, breaks down only when replay fraction is extreme (probably > 0.9
for our setup). Consistent with our +0.005 bpc at rf=0.9 (the only rf
where the sign is positive, weakly).

**Honest assessment**: Rank 1 (Lin / Buzzega) gives the tightest fit
to our data, with Rank 2 (LMC) as the next-most-principled. Rank 5
(noise injection) is the parsimony-winner — it explains the pattern
with the weakest assumptions, but doesn't predict the BWT-positive
side without additional structure.

## 4. Brain-inspired mechanism mapping

The user wants the mechanism, not the AI analogy. Five neuroscience
findings, with what each predicts for our setup.

### 4.1 Foster-Wilson 2006 (Nature 440) — awake reverse replay at reward

After reward, hippocampal place cells fire in REVERSE order of the
just-traversed trajectory. The functional interpretation (Mattar-Daw
2018; Joo-Frank 2018, Neuron) is credit assignment, not memory
protection. Reverse replay backs up reward to states that led to it.

Mapping: this is closer to TD-learning credit assignment than to
memory rehearsal. NOT directly relevant to BWT-positive pre-shift-
neutral. (User's existing wave14b_r7 note already established this
gap re Mattar-Daw.)

### 4.2 Karlsson-Frank 2009 (Nature Neuroscience 12) — forward remote
replay during rest

Place cells fire forward sequences for trajectories the animal is NOT
currently on. Functional interpretation: maintenance / consolidation
of remote spatial memory. THIS is the BWT-protective mechanism.

Mapping: random replay over the pool corresponds to Karlsson-Frank
forward remote replay — sampling sequences from past episodes
without regard to the current behavioral demand. Their key result:
remote replay does NOT disrupt current spatial behavior or new
learning. **This is the biological signature of BWT-positive AND
pre-shift-neutral.**

### 4.3 Schapiro et al. 2018 (Nature Comm 9:3920) — replay prioritizes
WEAK memories

Human hippocampal fMRI: rest-period replay correlates with weakly-
encoded items, and predicts memory improvement only with intervening
sleep. Mechanism: weak memories have a wider error gradient and benefit
more from rehearsal.

Mapping: this is the MIR/loss-magnitude argument in disguise. Doesn't
predict pre-shift neutrality directly; predicts that *adaptive*
priority should beat random when replay budget is tight. For us, this
maps onto the F2 (loss-magnitude priority) experiment in wave14b_r7.

### 4.4 Joo-Frank 2018 review (Nature Rev Neurosci) — replay is content-
based, not plan-based

Replay reactivates past experience independent of upcoming choice.
Functional content is determined by what's relevant to past learning,
not what's needed for current decision. Mechanism for pre-shift
neutrality: replay engages a different memory pathway than online
encoding, so the two don't compete for the same synaptic resources.

Mapping: biological replay is OFFLINE; our online replay is INLINE.
The biological mechanism for "no plasticity tax" is offline-only
operation. Our setup doesn't have offline phases, so the brain's
solution doesn't directly transfer — but the principle "replay
should not compete for the synapses currently being updated" is
worth implementing as a clean-room ablation (e.g., consolidation
pass between epochs vs interleaved).

### 4.5 Wittkuhn-Schuck 2021 (Nature Comm 12:1795) — replay even in
visual cortex without memory demand

Sub-second neural sequences in human visual cortex during rest,
independent of hippocampus. Suggests replay-like phenomena are a
general property of trained neural populations, not a specialized
memory mechanism.

Mapping: this is the cleanest argument that "replay is what trained
networks do automatically when not currently encoding." Predicts
that ANY system with sufficient redundancy in the substrate (our
N=4096 BSC dimensions, very over-parameterized for K=4) will replay
gracefully without competing with current encoding. Pre-shift
neutrality is the default, not the surprise.

### Bottom-line biology mapping

The reason hippocampal replay is BWT-positive AND pre-shift-neutral
is **temporal segregation** (Joo-Frank 2018) + **redundant substrate**
(Wittkuhn-Schuck 2021). Replay happens during quiescent periods when
new encoding is gated off; replay engages a structurally-redundant
representation that doesn't share resources with online encoding.
Our HDC substrate's N=4096 over-parameterization for K=4 gives the
redundancy half for free; we don't have the temporal-segregation half,
which is why the literature framings (Rank 1-3 above) match better
than direct biology mapping.

## 5. Rescues for the Stein framing — honest about post-hoc-ness

The user wants me NOT to throw out the Stein framing wholesale.
Five rescues, sorted by principled-ness.

### Rescue 1 — Stein applies to retrieval, not training (PRINCIPLED)

The wave14b synthesis's strongest Stein link was always to retrieval-
score shrinkage and bundle-LLR calibration. The (2B-1)/N constant
appears legitimately there. Prediction #1 mis-applied the framing to
W training, where the bias-variance decomposition has different
parameters.

**Move**: keep the Stein framing for the bundle-LLR factor 2/(B-1),
β annealing, R10 fusion. Drop it for W-training-under-replay. This
is the cleanest split and consistent with the original synthesis's
"6 of 8 mechanisms" qualifier.

### Rescue 2 — Stein dominance is asymmetric; the prediction was a
misuse (PRINCIPLED)

As noted in §2.2: Stein's theorem says JS dominates MLE — i.e., is
NEVER WORSE. The wave14b prediction "replay should hurt pre-shift"
was a SECOND step grafted on, not a Stein-theorem prediction. The
modified framing: Stein-like shrinkage in the right place is never
worse, only better. Random replay at rf=0.9 being +0.005 bpc within
seed noise is CONSISTENT with this modified framing.

**Move**: weaken predictions from "X must hurt in low-variance regime"
to "X should not help in low-variance regime, may help in high-
variance regime." This is the honest reading of Stein.

### Rescue 3 — Stein constants are different for Hebbian-trained
estimators (PARTIALLY PRINCIPLED)

Efron-Hastie CASI Ch.7 (already in wave14b sources) shows JS-like
dominance generalizes to exponential families with different
shrinkage constants. For Hebbian outer-product estimators of a
matrix-valued quantity (W), the relevant theorem is Stein-Haff or
Tsukuma-Kubokawa for Wishart-shrinkage. The constants are NOT
(k-2)/||X||² but something involving the eigenvalue spectrum of W.

**Honest assessment**: this is the most defensible rescue, but it
requires re-deriving from scratch. Whether the new constants would
predict ANY pre-shift effect from replay is an open question.

### Rescue 4 — The prior is not what we thought (SEMI-POST-HOC)

In Stein-Bayes, shrinkage moves estimator toward a prior mean μ. The
wave14b synthesis implicitly assumed μ = 0 (so replay = move-toward-
zero = shrinkage). If instead μ = "joint distribution optimum," then
random replay IS Stein-toward-prior, with prior = joint optimum. In
that case the prediction reverses: replay should HELP both pre-shift
(by moving toward Bayes-optimal joint) and BWT (same reason).

**Honest assessment**: this rescues the framing by changing the prior
from "null" to "joint." That's the Lin-1992 multi-task argument
dressed in Stein clothes. Re-derivation is post-hoc, but the new
framing predicts BOTH our findings (pre-shift neutral AND BWT
positive) without further surgery. **This is the best rescue if we
want to keep "Stein-like" language at all.**

### Rescue 5 — Stein holds above the bundle-SNR threshold (POST-HOC)

Suppose the prediction held only when bundle SNR is too low to support
reliable retrieval (so retrieval = noise = useless = pure-bias replay).
At K=4, B=5, N=4096 we have SNR=sqrt(819), far above any threshold.
The prediction was always about high-K regime, where SNR drops. 

**Honest assessment**: this is post-hoc. The original prediction
explicitly cited K=4 as the test. Reframing as "K=4 was the low-
variance regime where the prediction should NOT have applied" reads
the test as a self-falsification. Acceptable as honest-update; not
acceptable as "Stein survives at K=4."

### Rescue ranking summary

| Rescue | Principled? | Predicts our data? | Cost |
|---|---|---|---|
| 1: Stein for retrieval only | Yes | Yes | Drop training-side claims |
| 2: Stein is asymmetric | Yes | Yes (consistent, not predicted) | Weaken predictions |
| 3: Hebbian Stein constants | Partly | Unknown | Derivation work |
| 4: Prior = joint optimum | Semi-post-hoc | Yes (both findings) | Honesty tax |
| 5: High-K only | Post-hoc | Trivially | Dishonest |

**Best move**: combine 1 + 2 + 4. Drop W-training claims (1),
weaken to asymmetric-only predictions (2), restate the prior as the
multi-task / joint optimum (4). This preserves the unifying-language
benefit of "shrinkage" without overextending the theorem.

## 6. Falsifiable predictions from the best surviving framing

Best surviving framing: **Lin-multi-task with LMC-region argument**
(Rank 1 + Rank 2 in §3). Three pre-registered, ≤1h GPU each, at K=4.

### P1 — Replay tax appears at corpus-dissimilarity threshold

Setup: train baseline W on corpus A (English markdown). Continue on
B drawn from a maximally-dissimilar distribution: random byte stream
(uniform[0,256)). Repeat at rf ∈ {0, 0.5, 0.9}.

Prediction: pre-shift bpc on A is now MONOTONICALLY worse with rf
under random replay — Δ(rf=0.9) ≥ +0.05 bpc above rf=0. Reason: when
A and B share zero structure, the LMC region between optima collapses,
so replay's "join-distribution" target pulls W away from A.

Falsifier: pre-shift bpc stays within ±0.02 bpc across rf even with
random-byte B.

### P2 — MIR-style priority recovers what random misses, but only at
small rf

Setup: rf=0.1, compare random replay vs MIR-loss-magnitude replay
(score by current-W CE on pool entry, sample ∝ score).

Prediction: MIR beats random by ≥0.03 bpc on BWT at rf=0.1; gap
shrinks to <0.01 at rf=0.5. Reason: small rf is the regime where
sample-efficient prioritization matters; at large rf, coverage
dominates relevance (Chaudhry 2019 small-buffer regime).

Falsifier: MIR ≤ random across all rf.

### P3 — Replay variance does not transfer through bundle decomposition

Setup: at K=4, rf=0.5, ablate the bundle calibration factor 2/(B-1)
ON vs OFF. Measure pre-shift bpc.

Prediction: bundle calibration affects ONLY C2/C3 retrieval-path
predictions, not C1 baseline. Pre-shift bpc gap (C1 vs no-replay)
is UNCHANGED by calibration. Reason: the legitimate Stein knob is
on the retrieval side, orthogonal to W-training-under-replay.

Falsifier: calibration changes the replay-vs-no-replay gap by >0.01
bpc, indicating Stein knobs do couple.

## 7. Sources

- [James-Stein estimator (Wikipedia)](https://en.wikipedia.org/wiki/James%E2%80%93Stein_estimator)
- [Efron-Hastie CASI Ch.7](https://efron.ckirby.su.domains/other/CASI_Chap7_Nov2014.pdf)
- [Lin 1992 "Self-Improving Reactive Agents", Machine Learning 8 (DOI 10.1007/BF00992699)](https://link.springer.com/article/10.1007/BF00992699)
- [Robins 1995 "Catastrophic Forgetting, Rehearsal and Pseudorehearsal"](https://www.semanticscholar.org/paper/Catastrophic-Forgetting,-Rehearsal-and-Robins/5ac423a83b4321b43249224fcc528bb70e086826)
- [Buzzega et al. 2020 "Dark Experience for General Continual Learning" (arXiv:2004.07211)](https://arxiv.org/abs/2004.07211)
- [Buzzega et al. 2021 "Rethinking Experience Replay: a Bag of Tricks" (arXiv:2010.05595)](https://arxiv.org/abs/2010.05595)
- [Rolnick et al. 2018 "Experience Replay for Continual Learning" (arXiv:1811.11682)](https://arxiv.org/abs/1811.11682)
- [Aljundi et al. 2019 "MIR" (arXiv:1908.04742)](https://arxiv.org/abs/1908.04742)
- [Mirzadeh et al. 2020 "Linear Mode Connectivity in Multitask and Continual Learning" (arXiv:2010.04495)](https://arxiv.org/abs/2010.04495)
- [van de Ven et al. 2020 "Brain-inspired replay" (Nature Comm 11:4069)](https://www.nature.com/articles/s41467-020-17866-2)
- [Bricken et al. 2023 "SDM is a Continual Learner" (arXiv:2303.11934)](https://arxiv.org/abs/2303.11934)
- [Wang et al. 2024 "Comprehensive Survey of Continual Learning" (arXiv:2302.00487)](https://arxiv.org/abs/2302.00487)
- [Klein et al. 2025 "ER Addresses Loss of Plasticity" (arXiv:2503.20018)](https://arxiv.org/abs/2503.20018)
- [Dohare et al. 2024 "Loss of plasticity in deep continual learning" (Nature)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11338828/)
- [Chaudhry et al. 2019 "Tiny Memory Continual Learning" (arXiv:1902.10486)](https://arxiv.org/abs/1902.10486)
- [Foster & Wilson 2006 "Reverse replay of behavioural sequences" (Nature 440:680)](https://www.nature.com/articles/nature04587)
- [Karlsson & Frank 2009 "Awake replay of remote experiences" (Nat Neurosci 12:913)](https://www.nature.com/articles/nn.2344)
- [Schapiro et al. 2018 "Replay prioritizes weakly learned items" (Nature Comm 9:3920)](https://www.nature.com/articles/s41467-018-06213-1)
- [Joo & Frank 2018 "The hippocampal sharp wave-ripple in memory retrieval" (Nat Rev Neurosci 19:744)](https://www.nature.com/articles/s41583-018-0077-1)
- [Mattar & Daw 2018 "Prioritized memory access" (Nat Neurosci 21:1609)](https://www.nature.com/articles/s41593-018-0232-z)
- [Wittkuhn & Schuck 2021 "Dynamics of fMRI patterns" (Nature Comm 12:1795)](https://www.nature.com/articles/s41467-021-21970-2)
- [Orvieto et al. 2023 "Explicit Regularization via Noise Injection" (arXiv:2206.04613)](https://arxiv.org/abs/2206.04613)
- [Camuto et al. 2021 "Asymmetric Heavy Tails in Gaussian Noise Injection" (arXiv:2102.07006)](https://arxiv.org/abs/2102.07006)
- [Plate 1995/2003 "Holographic Reduced Representations"](https://www.researchgate.net/publication/220571783_Holographic_Reduced_Representations)
- [Frady-Sommer 2019 "Resonator Networks" (arXiv:1906.11684)](https://arxiv.org/abs/1906.11684)
- [Melchior-Wiskott "Hebbian-Descent" (arXiv:1905.10585)](https://arxiv.org/abs/1905.10585)
