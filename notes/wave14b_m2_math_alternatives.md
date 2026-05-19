# M2 in-basis math alternatives — research agent synthesis

Returned 2026-05-19. Unbiased survey of pure-math operations whose output
is provably outside the span of any bilinear retrieval kernel over a fixed
pool.

## The closure restated precisely

Lippl-Stachenfeld 2024/2025 ([arXiv:2405.16391](https://arxiv.org/abs/2405.16391)):
when both retrieval and concept signals are kernels whose Gram matrices
are functions of the pool's Gram matrix `G = X X^T`, the concept channel
adds nothing. **The mathematical escape is any signal that is NOT a
Borel function of `G`.**

## 8 directions surveyed

### Direction 1 — Non-commutative free cumulants kappa_n (n >= 3) of per-position pool slices [STRONGEST + CHEAPEST]

Free cumulants are defined via Mobius inversion over non-crossing
partitions. Cumulants of order >= 3 are NOT in the span of pairwise
moments — provably new functionals.

**Math escape:** retrieval is degree-2; kappa_n for n >= 3 of pool-derived
operators are non-Borel in `G`.

**Concept signal:** treat K stacked per-position pool slices as a tuple of
self-adjoint operators on R^N. Compute kappa_3(P_r, P_s, P_t) for triples
of positions. Score `kappa_3(q, q, P_r)` as additive logit to C3-factored.

**Tractability:** GOOD. K=4 -> only C(6,3)=20 triple cumulants. Each trace
is a degree-3 polynomial in matrices <=1024x4096. Under 1h GPU.

**Test:** drop-in to `exp_wave14b_m2_with_proper_rerank.py`. lambda in {0.01, 0.1, 1.0}.

### Direction 2 — Persistent H_1 of pool's filtered VR complex

Persistence diagrams are stable invariants of order-type, not of G.
Two pools with identical Gram matrices but different higher-order
simplex fillings give different barcodes.

**Math escape:** order-type + simplicial-inclusion structure jointly,
not just pairwise distances.

**Tractability:** MEDIUM. Pool-only PH cacheable; per-query incremental
update <1h achievable.

### Direction 3 — Steenrod squares Sq^i on F_2-cohomology of pool nerve [OUT OF SCOPE]

Detects topological structure that cup-product alone doesn't. Defer
unless persistent homology hits.

### Direction 4 — Spectral graph signal processing [CHEAPEST]

Build k-NN graph on pool; Laplacian L=D-W; eigenvectors phi_j are graph
Fourier basis. Projection <q, phi_j> for j >= 2 is non-local in G — the
redundancy theorem covers row-wise G functions, not eigenfunctions of L.

**Tractability:** GOOD. Pool eigendecomposition: 5s. Per-query projection
trivial. Under 30 min end-to-end.

### Direction 5 — Free cumulants of empirical G

R-transform calculus of (1/P) X X^T encodes information beyond spectral
moments. Use adaptive temperature beta(P, kappa_3(G)).

**Tractability:** GOOD. Under 5 min.

### Direction 6 — Information bottleneck with EXTRA-pool relevance Y [CLEANEST ESCAPE]

Tishby IB: min I(X;T) - beta I(T;Y) with Y from OUTSIDE the pool
(e.g., KenLM 5-gram log-prob). The redundancy theorem assumes T=f(pool);
external Y breaks the assumption tautologically.

**Math escape:** by construction.

**Tractability:** MEDIUM (need to train projector + KenLM). ~2h.

### Direction 7 — Wavelet scattering transform (Mallat-Bruna)

S_J(x) = |W_J_k ... |W_J_1 x| ... | is non-expansive, translation
invariant, deformation stable. Order-2 scattering coefficients capture
cross-scale interactions invisible to first-order energies.

**Math escape:** non-linear in x, so not in the bilinear span.

**Tractability:** GOOD. kymatio GPU 1D scattering. Pool of 1024 N=4096
in ~10s.

### Direction 8 — Algebraic K-theory / Grothendieck stable equivalence

Math escape exists in principle but **no clean bridge to a scorable
signal** on our substrate. Honest defer.

## Tomita-Takesaki / KMS — math agent's verdict

At finite dimension Tomita-Takesaki reduces to spectral calculus of
S = J Delta^{1/2}, which IS recoverable from Gram-like data. The genuine
escape requires infinite-dim type-III case. **Skip at our finite scale.**

## Tractability matrix

| Direction | <1h GPU? | escape strength | priority |
|---|---|---|---|
| 1. NC cumulants kappa_3 | YES | strong (orders >= 3) | **A** |
| 4. Graph Laplacian spectral | YES | strong (non-local in G) | **A** |
| 2. Persistent H_1 | partial | strong (filtration+order) | A |
| 6. IB with external Y | medium | tautological | **A** |
| 7. Scattering transform | YES | strong | B |
| 5. Free cumulants of G | YES | medium | B |
| 3. Steenrod squares | NO (weeks) | strong (refines cohomology) | C |
| 8. K-theory | NO (no bridge) | unclear at scale | skip |

## Recommended test order

1. **Direction 1 (kappa_3 NC cumulants of pool slices)** — most
   theoretically illuminating, cheap. If positive: first concrete
   demonstration that bilinear retrieval is strictly weaker than the
   substrate could support. Publishable.
2. **Direction 2 (persistent H_1)** — topology genuinely outside Gram
   span. Predict null on byte-LM (text has weak H_1), but null is
   informative.
3. **Direction 4 (graph Laplacian eigenmodes)** — cheapest, cleanest
   theorem escape. Sanity check.
4. **Direction 6 (IB with KenLM external Y)** — tautological escape;
   if this doesn't win, the problem is byte-LM, not the math.
5. **Direction 7 (scattering)** — cheap triangulation.
6. **Direction 5 (G cumulants)** — falls out of direction 1.
7. **Direction 3 (Steenrod)** — only if 2 hits.

## Sources

- [Lippl-Stachenfeld 2024 kernel theory of compositional generalization](https://arxiv.org/abs/2405.16391)
- [Speicher free probability notes](https://arxiv.org/pdf/0911.0087)
- [Speicher cumulant decomposition](https://arxiv.org/pdf/2307.02281)
- [Adams persistence images JMLR](https://jmlr.csail.mit.edu/papers/volume18/16-337/16-337.pdf)
- [Steenrod-Epstein cohomology operations](https://www.sas.rochester.edu/mth/sites/doug-ravenel/otherpapers/steenrod-epstein.pdf)
- [Stratified graph spectra](https://arxiv.org/pdf/2201.03696)
- [Tomita-Takesaki review](https://arxiv.org/pdf/1301.1836)
- [Bruna-Mallat scattering](https://www.di.ens.fr/~mallat/papiers/Bruna-Mallat-Pami-Scat.pdf)
- [Tishby information bottleneck](https://arxiv.org/abs/physics/0004057)
