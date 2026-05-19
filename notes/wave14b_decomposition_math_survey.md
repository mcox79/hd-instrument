# Decomposition Math Survey for Wave 14.B (unbiased)

Synthesized 2026-05-18 from research agent survey. The agent was
prompted to describe what each mathematical area DOES, not whether
it has been used in ML. The mapping below is my synthesis.

## The general problem class

Given a known combiner f and finite codebook S, recover (a, b) in
S × S from observing c = f(a, b). The math falls into seven main
camps, each tackling a different f and exploiting a different
structural property of S.

## Direct relevance to Wave 14.B (resonator networks)

**Kent-Frady-Olshausen-Sommer 2020, "Resonator Networks 2":**

- For PRODUCT resonator (`c = a_1 ⊙ a_2 ⊙ ... ⊙ a_F`) with each
  factor from codebook of size M: operational capacity is
  `M^F < O(N² / F)`.
- The network is NOT a gradient descent. It iterates dynamics
  that almost always converge in the operational regime but
  can enter limit cycles above capacity.
- Multi-restart is the standard defense against limit cycles.
- Capacity dramatically exceeds ALS, gradient descent, multiplicative
  weights, sum-of-squares relaxations.

**For Wave 14.B base case** (F=2 product equivalent via position
binding, M=32, N=4096): M^F = 1024 vs. N²/F = 8.4M. We are FOUR
orders of magnitude below the cliff. 100% recovery is expected.

**Kymn et al. 2024 algebraic characterization:** convergence
controlled by spectral properties of codebook Gram matrix. Random
bipolar codebooks are well-conditioned, supporting our setup.

## Cross-cutting principles that constrain our experiments

### Identifiability before algorithms

Every area distinguishes "information-theoretically possible" from
"polynomial algorithm exists." The gap (statistical-computational
gap) is the active frontier. For us: information is abundantly
present (Section 1 of pre-reg), so the question is purely
algorithmic.

### Linear count bounds

- Bilinear inverse: L ≥ 2(K+N) - 4 (Kech-Krahmer 2017)
- Tensor CP: k(A) + k(B) + k(C) ≥ 2R + 2 (Kruskal 1977)
- Phase retrieval: m = 4n - 4 real, 4n - 1 complex
  (Bandeira-Cahill-Mixon-Nelson)
- ICA: at most one Gaussian source (Comon 1994)

These say "you need linearly many measurements in the intrinsic
dimensions of the factors." Our N=4096 vs. log(K²)=10 bits is
wildly above any such bound.

### Geometric transversality controls rate

- Friedrichs angle controls alternating projection rate
  (Bauschke-Borwein 1993)
- Incoherence controls compressed sensing (Donoho-Tanner)
- Kruskal rank controls tensor decomposition uniqueness
- Non-Gaussianity controls ICA

For us: the position codes p1, p2 are random bipolar — they
DECOUPLE the (a, b) recovery into two cleanly transversal
constraints. This is why Gate 2 (oracle resonator) hit 100%.

### Nonconvex landscapes are often benign

Sun-Qu-Wright 2018, Li-Ling-Strohmer-Wei 2019: phase retrieval and
blind deconvolution have NO spurious local minima above
measurement thresholds. The resonator analog is "no limit cycles
below capacity."

## Hardness boundaries we should respect

### Computational vs statistical gap

For sparse PCA, planted clique, and similar: information is
present at threshold k=2log(n), but no efficient algorithm beats
k=√n. Overlap Gap Property (Gamarnik) and SoS lower bounds explain
this. The lesson: we should NOT expect 14.B to scale to arbitrary
codebook sizes — there is a computational ceiling well below the
information-theoretic one.

### Tensor rank is NP-hard

Håstad 1990. If we frame our problem as exact tensor decomposition
in the worst case, it's intractable. The reason ours is tractable:
RANDOM codebooks satisfy Kruskal genericity with overwhelming
probability. Adversarial codebooks would defeat us.

### Limit cycles in nonconvex Douglas-Rachford

Bauschke-Noll counterexamples: DR can cycle without entering the
intersection of two nonconvex sets. The resonator analog applies.
Multi-restart with random initialization is the empirically
validated escape — Wave 13.3 needed it, our Wave 14.B uses 8
restarts by default.

## What this changes about our planned sweeps

**Original plan (pre-reg):**
1. Sweep M (bundle size) at K=32, N=4096 — find recovery curve
2. Sweep K (codebook size) at M=2, N=4096 — find phase boundary
3. Integrate with continual learning

**Revised plan informed by survey:**

The capacity scaling tells us where to expect cliffs:
- For sum-resonator with bundle size B, codebook K: capacity
  ~ B × log(K) ≲ N / const.
- At N=4096, K=32: cliff expected around B = 128-256 atoms
  bundled.
- At N=4096, B=2: cliff expected around K = 2048+ codebook.

So sweep #1 should reach B=128 or higher to see the cliff.
Sweep #2 needs K=2048+ to see the cliff. Both are feasible.

**Additional sweep informed by Kymn et al.:** vary the codebook
Gram-matrix spectrum (controlled non-orthogonality) to see how
the conditioning interacts with recovery. Useful for understanding
what happens when codebook atoms drift in continual learning
(which they would not in our frozen design, but it's a robustness
check).

## What this means for continual-learning integration

The most useful capability isn't pushing the capacity ceiling
higher — it's **mining structure from many partial decompositions**.

Specifically, after the pool stores N episode bundles
(c_1, c_2, ..., c_N), each decomposed into its 2-atom parts via
14.B, the question becomes: **which atoms appear in many
decompositions?** Those recurrences are the latent "slot fillers"
of the agent's experience. This is a clustering problem in the
codebook, not a single-decomposition problem.

The math survey makes clear this is the AMP / belief propagation
regime: we have many noisy decompositions and want to infer the
latent atom distribution. Donoho-Maleki-Montanari 2009 (AMP state
evolution) gives sharp asymptotic phase transitions for exactly
this problem.

So the realistic Wave 14.B program has THREE layers:
1. Single-bundle decomposition (current, working)
2. Many-bundle structure mining (AMP / spectral / clustering)
3. Continual-learning integration (decomposition + structure
   mining applied to evolving pool)

## Key references

- Resonator Networks 2 (Kent-Frady-Olshausen-Sommer 2020):
  https://direct.mit.edu/neco/article/32/12/2332/95653/
- Algebraic resonator characterization (Kymn et al. 2024):
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10789822/
- Kruskal's tensor uniqueness:
  Bhaskara-Charikar-Moitra-Vijayaraghavan 2014 arXiv:1304.8087
- AMP state evolution: Donoho-Maleki-Montanari 2009 PNAS
- Bauschke-Borwein projections 1993
- Phase retrieval landscape: Sun-Qu-Wright 2018
- Overlap Gap Property: Gamarnik 2020 PNAS

## Pre-registration update

The original Wave 14.B pre-reg stands. The sweeps are revised
upward in scope based on the predicted phase transitions, but the
falsification criterion at the base case (≥ 50% at K=32, M=2) is
already met at 100%. No methodological change.
