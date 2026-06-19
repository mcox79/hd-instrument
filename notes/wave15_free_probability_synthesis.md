# Wave 15: Free Probability — Synthesis and Honest Assessment

Drafted 2026-05-18 from unbiased free-probability survey. The agent
described the math; this doc does the HDC mapping per the
unbiased-research rule.

## What the math actually does

Free probability is a noncommutative probability theory developed by
Voiculescu (1983+). It studies algebras (not sets) with a linear
functional (trace). The headline calculations are:

- **R-transform**: linearizes addition of "free" random variables.
  R_{a+b}(z) = R_a(z) + R_b(z). Closed form for many distributions.
- **S-transform**: linearizes multiplication. S_{ab}(z) = S_a(z) S_b(z).
- **Asymptotic freeness**: independent unitarily-invariant random
  matrices become free as N -> infinity. Spectra of sums and products
  computable via free convolution.
- **Free CLT**: normalized sum of free i.i.d. variables converges to
  semicircle (free Gaussian).
- **Marchenko-Pastur**: spectrum of sample covariance of random
  matrices is the free Poisson distribution. Exact closed form.

The math is a **spectral calculus** for sums and products of random
matrices, exact in the high-dimensional limit.

## Honest reassessment of what this gives us

I initially queued Wave 15 expecting a new HDC primitive. The survey
makes clear: free probability does NOT introduce a new mechanism. It
introduces ANALYTICAL TOOLING for predicting spectra of operations we
already perform.

This is still valuable but the value is different:
- NOT: "free probability is the next substrate."
- IS: "free probability gives closed-form predictions for capacity,
  convergence thresholds, and spectral properties of our existing
  substrate."

Three concrete applications follow.

## Application 1: Closed-form prediction of resonator capacity

Current state: Kent-Frady-Olshausen-Sommer 2020 give EMPIRICAL
operational capacity M^F < N^2 / F for the resonator network. The
2024 Kymn et al. paper provides an algebraic characterization in
terms of codebook Gram-matrix spectrum.

Free probability extends this. For a random codebook of K vectors
in dimension N (large N), the Gram matrix `X X^T` has spectrum
converging to Marchenko-Pastur with parameter K/N. The resonator's
iteration matrix is a polynomial in this Gram matrix. The polynomial
spectrum is computable by operator-valued free probability (linearization
trick).

**Concrete payoff**: derive a closed-form expression for the
operational capacity of our specific bundle structure (sum of M
position-bound codebook atoms) at given (K, N, M). Compare to our
bundle-sweep empirical numbers. If theory predicts our sweep results,
we have a tool to predict capacity at scales we can't easily run
(e.g., N=65536, K=4096).

**Engineering work required**: write down our resonator's iteration
operator in terms of free random matrices (the codebook can be
treated as a Haar-like ensemble in the high-N limit). Solve the
matrix-Dyson equation. Compare to empirical results.

**Estimated effort**: 2-3 days of math + 1 day of implementation.

## Application 2: Predicting W matrix spectrum after delta-rule training

Current state: we train W via delta-rule updates of the form
W <- (1-decay) W + alpha (target - W ctx) ctx^T. This is many rank-1
updates with structured rank-1 directions. After many updates W's
spectrum has some distribution we don't currently characterize.

Free probability prediction: in the limit of many updates with
independent contexts, W's spectrum converges to a deterministic
distribution computable by free additive convolution. The
distribution depends on:
- alpha and decay (control the "mixing")
- The covariance of contexts (which depends on codebook + binding)
- The signal direction (target_atom * ctx^T has known structure)

**Concrete payoff**: closed-form prediction of W's spectrum lets us:
1. Detect under-training (W spectrum too sparse).
2. Detect over-training (W spectrum hits some fixed-point regime).
3. Pick alpha and decay analytically rather than by sweep.
4. Predict perplexity floor before running.

**Engineering work**: derive the asymptotic distribution. This is a
non-standard application; I don't think there's literature directly
on "delta-rule trained W spectrum" but the building blocks
(Marchenko-Pastur, sample covariance, free convolution) are standard.

**Estimated effort**: 1-2 weeks of math. Risk: might not have a clean
closed form due to the recursive structure of delta updates.

## Application 3: Phase transition predictions

Current state: bundle sweep just showed 100% recovery at B=32 with
K=32 in N=4096, much beyond the M^F < N^2/F threshold predicted by
Kent-Frady-naive. We have a phase transition curve we don't know.

Free probability prediction: for any specific bundle structure (sum,
product, weighted sum), the detection threshold for a low-rank
signal in a noisy bundle is given by the BBP (Baik-Ben Arous-Peche)
transition, which is computable from the marginal distributions via
free probability. Specifically:

For a rank-1 signal `x x^T` added to a Marchenko-Pastur sample
covariance: the largest eigenvalue is detectable above a sharp
threshold `||x||^2 = lambda_critical(MP_parameter)`.

The analog for our setup: there's a sharp threshold for when an atom
can be extracted from a bundle via codebook projection. Below
threshold: 0% recovery (signal indistinguishable from noise). Above:
high recovery.

**Concrete payoff**: replace heuristic "where does it break" sweeps
with closed-form predictions of break-points.

**Engineering work**: identify the BBP analog for resonator
decomposition. Predict our bundle-sweep cliff analytically. Compare.

**Estimated effort**: 3-5 days.

## What Wave 15 is NOT

- NOT a new mechanism for prediction or memory.
- NOT a replacement substrate.
- NOT a new training algorithm.

The original Wave 15 framing was over-optimistic. Free probability
is analytical tooling for the substrate we already have.

## What Wave 15 IS

A predictive theory layer that:
1. Replaces empirical phase-transition sweeps with closed-form
   predictions.
2. Lets us evaluate substrate choices analytically before coding.
3. Gives us bounds and benchmarks for "is our empirical result
   what theory predicted?" — a verification tool.

This is similar in spirit to having a theoretical baseline against
which to interpret experiments. Every successful empirical sweep
should match a theoretical prediction; mismatches reveal something
interesting about the implementation.

## Concrete next-step priorities

If we pursue Wave 15:

**Priority 1 (highest payoff, smallest scope)**: derive the BBP
threshold for our bundle structure. This is well-defined math with
known building blocks. Output is a single closed-form curve we can
overlay on bundle-sweep results.

**Priority 2 (medium scope)**: write down the codebook + bundle
operations in free-probability notation. Compute the operational
capacity formula. Compare to Kent-Frady empirical numbers.

**Priority 3 (high effort, uncertain)**: closed-form W spectrum
under delta-rule. Could yield big insight or no clean answer.

## Recommendation

**Don't make Wave 15 a priority right now.** Reasoning:

1. Wave 14.B sweep is showing wide operating envelope - the empirical
   data is informative without needing closed-form predictions.
2. Wave 4.5 v3 negative result needs a rehabilitation effort (v4)
   that's higher-priority than analytical tooling.
3. Continual-learning integration of 14.B is the high-leverage next
   experiment given the wide envelope.
4. Wave 15 priority-1 (BBP threshold) is worth a brief side-quest
   IF we have someone with time to do the math - low cost, high
   sanity-check value.

Updated priority order:
1. Wave 4.5 v4 (rehabilitation: SGD without Adam preconditioning,
   codebook-span projection).
2. Wave 14.B continual-learning integration (Option D.1 or D.2 from
   the W-replacement design).
3. Wave 14.C (hierarchical decomposition, Connes-Kreimer rooted trees).
4. Wave 15 priority-1 only (BBP threshold side-quest).

Lower-tier waves (15.2, 15.3) deferred until evidence requires
analytical backstop.

## References (from agent survey)

- Voiculescu-Dykema-Nica, *Free Random Variables* (CRM 1992)
- Hiai-Petz, *The Semicircle Law, Free Random Variables and Entropy*
  (AMS 2000)
- Nica-Speicher, *Lectures on the Combinatorics of Free Probability*
  (Cambridge 2006)
- Mingo-Speicher, *Free Probability and Random Matrices* (Springer 2017)
- Chen-Garza Vargas-Tropp-van Handel 2024, "A new approach to strong
  convergence", arXiv:2405.16026 (sharp strong convergence rates)
- Marcus-Spielman-Srivastava + Marcus 2024, finite free probability
- Helton-Far-Mai-Speicher, operator-valued subordination (Dyson-equation
  numerical methods)
