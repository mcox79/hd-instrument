# Research: spectral/diffusion transforms for concept-vector arrangement at scale

Date: 2026-07-10
Mode: self-directed drill (no sub-agent dispatch this cycle per explicit instruction) -- WebSearch/WebFetch + reasoning only.
Field-advisor context: run at cycle start (`research_field_advisor.py`). This drill is a directed USER question, not organic field-ranking; nearest existing adjacency is `network-science-graph-theory` (Tier-1b, parent=spin-glass/free-probability) and `sparse-coding-compressed-sensing`. No existing drill count for "spectral graph theory applied to concept arrangement" specifically -- this opens that sub-field.

## HEADLINE

Yes, there is a real, decades-old, rigorously-proven transform (graph-Laplacian spectral decomposition / diffusion maps / graph Fourier transform) that arranges connected concepts at nearby coordinates and compresses to a low-rank "gist" -- but it optimizes for SMOOTHNESS/cluster-coherence, not for linear composability, so "vector addition lands at meaningful points" is NOT a proven consequence of this specific machinery (weakest of the 5 claims). The random-walk/symmetric-normalized Laplacian is a genuinely load-bearing, proven fix for the degree/hub-popularity bias that plagues the unnormalized version (same failure class as the additive-code collapse we just killed) -- this is textbook, not speculative. And yes: a slow "nudge toward neighbor average" consolidation loop IS, exactly and provably, an Euler-discretized heat-diffusion step on the graph Laplacian (no eigendecomposition required to run it) -- but unclamped it provably collapses to the trivial constant mode (GNN oversmoothing theory gives the exact exponential collapse rate), so a restart/anchor term or early-stopping is not optional, it is the single required safety valve.

## 1. The spectral/harmonic transform, concretely

**Graph.** Concepts = nodes `V`, `|V|=N`. Edge weights `W_ij >= 0` = similarity / co-activation / associative-link strength (substrate-native: whatever produces a concept-concept affinity today). Degree matrix `D = diag(d_i)`, `d_i = sum_j W_ij`.

**Laplacians.**
- Unnormalized: `L = D - W`. PSD, `L @ 1 = 0` (constant vector is the trivial null-space eigenvector).
- Symmetric normalized: `L_sym = I - D^{-1/2} W D^{-1/2}`.
- Random-walk normalized: `L_rw = I - D^{-1} W = I - P`, where `P = D^{-1} W` is the random-walk transition matrix.

**Why eigenvectors = "nearby concepts get nearby coordinates."** The quadratic form `x^T L x = 1/2 * sum_ij W_ij (x_i - x_j)^2` is a smoothness energy: it is large when strongly-connected nodes have very different scalar values. Minimizing this energy subject to orthogonality constraints (Rayleigh-Ritz) is *solved exactly* by the Laplacian eigenvectors, ordered by eigenvalue `0 = lambda_1 <= lambda_2 <= ... <= lambda_N`. The Fiedler vector (`lambda_2` eigenvector, Fiedler 1973) is the smoothest non-trivial signal on the graph and is the classic 2-way graph-partition solution. Embedding a concept `i` into `R^k` via `y_i = (u_2(i), ..., u_{k+1}(i))` (the `k` smallest non-trivial eigenvectors) is exactly Belkin & Niyogi's Laplacian Eigenmaps construction [1]: it solves `min_Y tr(Y^T L Y)` subject to `Y^T D Y = I`, and by construction strongly-connected concepts end up close together in `Y`-space.

**Low frequency = gist, high frequency = idiosyncratic detail.** This is the direct graph analogue of ordinary Fourier analysis. Graph Signal Processing (Shuman et al. 2013 [3]) formalizes it: any function `f: V -> R` is a "graph signal"; the Graph Fourier Transform is `f_hat = U^T f` (project onto the Laplacian eigenbasis `L = U Lambda U^T`), inverse is `f = U f_hat`. Low-`lambda` components vary slowly across edges (community-level structure); high-`lambda` components oscillate node-to-node (noise / idiosyncratic detail). A rank-`k` compression keeps only the lowest-`lambda` block: `f_k = U_k U_k^T f`.

**Diffusion maps (Coifman & Lafon 2006 [2])** make the "zoom level" an explicit dial. Using the random-walk operator `P = D^{-1} W` (eigenpairs `(lambda_k, psi_k)`, same eigenvectors as `L_rw`, eigenvalues `1 - lambda_k(L_rw)`), the diffusion-map embedding at scale `t` is `Psi_t(i) = (lambda_2^t psi_2(i), lambda_3^t psi_3(i), ...)`. Since `|lambda_k| < 1` for `k>1`, larger `t` exponentially suppresses higher-frequency components -- `t` is literally a coarse-graining/"gist depth" knob, later shown (Q3) to be exactly what a consolidation loop's iteration count controls.

**Complexity, honestly.**
- Exact eigendecomposition of a dense `N x N` matrix: `O(N^3)` time, `O(N^2)` memory. Infeasible past a few thousand concepts.
- Lanczos / Krylov-subspace methods (sparse `W`, `nnz` nonzeros): cost per iteration is one sparse matvec, `O(nnz)`; total for `k` eigenpairs and `s` iterations (`s` a small multiple of `k`, growing with `1/`spectral-gap`) is roughly `O(s * nnz + s^2 N)` -- near-linear in `N` for sparse, well-gapped spectra. Lanczos/Arnoldi are numerically less stable than randomized methods but standard (scipy/ARPACK `eigsh`).
- Randomized SVD / randomized range-finders: `O(N d k)` for the sketch plus `O(N k^2)` for the small dense eigenproblem on the sketch -- competitive with Lanczos, more numerically robust, no dependence on spectral gap for the accuracy guarantee.
- Nystrom (landmark) approximation: pick `m << N` landmark nodes, exact-decompose the `m x m` submatrix (`O(m^3)`), extend to all `N` nodes at `O(Nm)` -- **linear in N**, the practical answer for "how do we ever do this at concept-DB scale."

## 2. Degree-invariance: is it real, and what does it cost?

**Yes, this is real and load-bearing, not speculative** -- it is one of the best-established results in spectral graph theory (von Luxburg's tutorial [4] is the standard reference; Ng-Jordan-Weiss 2002 [5] is the standard algorithm).

**The failure mode of the unnormalized Laplacian:** minimizing the raw cut `x^T L x` with no volume normalization is known to produce degenerate partitions that isolate low-degree/outlier vertices into their own singleton cluster, because the objective doesn't penalize small cluster *volume* -- it only counts edges cut, so peeling off one low-degree node is "cheap." **This is structurally the same failure class as an additive code collapsing on the low-degree tail**: both are "the raw/unnormalized objective is dominated by whatever has the most connections/mass, and starves the sparse tail."

**The fix.** Normalized cut (Shi-Malik-style) relaxes to the generalized eigenproblem `L u = lambda D u`, equivalent to eigendecomposing `L_rw = D^{-1} L = I - P`. Ng-Jordan-Weiss instead eigendecompose `L_sym = I - D^{-1/2} W D^{-1/2}` and then **row-normalize** each embedded point to unit length before clustering -- this row-normalization is a second, necessary degree-correction: `L_sym` eigenvectors relate to `L_rw` eigenvectors by `u_rw = D^{-1/2} u_sym`, so raw `L_sym` coordinates still carry a residual `1/sqrt(d_i)` magnitude scaling that must be divided out to get pure directional (degree-free) coordinates.

**Precisely what "invariance" means here.** `L_rw` and `L_sym` are similar matrices (same eigenvalues); both solve the volume-normalized Rayleigh quotient `min (x^T L x)/(x^T D x)`, which measures a node's pull on cluster assignment *relative to its own degree*, not in absolute edge-count terms. This removes the specific failure mode where high-degree "hub"/popularity nodes dominate the embedding geometry and drag everything toward themselves. Von Luxburg [4] explicitly recommends `L_rw` in practice for exactly this reason, and Von Luxburg, Belkin & Bousquet's consistency results show normalized spectral clustering converges to a sensible large-`N` limit under mild conditions, while the unnormalized version can converge to a degenerate limit dominated by the degree/density profile rather than genuine cluster structure.

**Honest caveat -- what it does NOT guarantee.** Normalization corrects the *bias direction* (systematic pull toward hubs), not the *estimation variance*: low-degree nodes still get noisier eigenvector coordinates on thin data (fewer edges = less averaging = higher variance), even under `L_rw`/`L_sym`. It is a fix for popularity-bias, not a fix for data-sparsity-driven noise on the tail. Also: `L_rw` is non-symmetric (though similar to a symmetric matrix, so still real-eigenvalued) -- either solve the symmetric generalized eigenproblem `L u = lambda D u` directly, or eigendecompose `L_sym` and transform back via `u_rw = D^{-1/2} u_sym`.

**Cost of normalizing:** requires `D^{-1}` or `D^{-1/2}`, undefined for isolated (degree-0) nodes -- must regularize (`d_i + eps`) or exclude singletons before normalizing.

## 3. Is consolidation == graph diffusion == the transform?

**A single micro-step of "nudge concept `i` toward its neighbors' weighted average"** is:
```
x_i <- (1 - alpha) x_i + alpha * (sum_j W_ij x_j) / d_i
```
i.e., in matrix form, `x <- (1-alpha) x + alpha * P x = x - alpha * L_rw x`. **This is exactly the explicit-Euler discretization of the heat/diffusion equation `dx/dt = -L_rw x`**, whose exact solution is the heat kernel `x(t) = e^{-t L_rw} x(0) = sum_k e^{-t lambda_k} <x(0), u_k> u_k`. So: **yes, precisely** -- running many small consolidation steps IS an incremental solver for the low-frequency Laplacian eigenbasis, with NO explicit eigendecomposition ever required. Because `e^{-t lambda_k}` decays fastest for large `lambda_k` (high-frequency / idiosyncratic detail) and slowest for small `lambda_k` (community-level gist), the consolidation loop is a continuously-tunable, soft version of the Q1 low-rank compression: `t` = "how much has been consolidated" = the diffusion-maps scale parameter, directly.

This is also the mechanism behind classic semi-supervised label propagation: Zhu-Ghahramani-Lafferty's harmonic solution and, with a verified citation, **Zhou, Bousquet, Lal, Weston & Scholkopf's "Learning with Local and Global Consistency" [8]**, whose iterative update is `x^{(t+1)} = alpha * S x^{(t)} + (1-alpha) x^{(0)}` (`S = D^{-1/2} W D^{-1/2}`), converging in closed form to `(I - alpha S)^{-1} (1-alpha) x^{(0)}` -- a Tikhonov-regularized / personalized-PageRank-style resolvent of the normalized Laplacian. **The `(1-alpha) x^{(0)}` restart/anchor term is the critical difference from vanilla diffusion** (see below).

**Where it breaks: oversmoothing collapse.** The trivial fixed point of unclamped diffusion IS the constant eigenvector (`L`'s null space, eigenvalue 0 of `L` / eigenvalue 1 of `P`). Run vanilla neighbor-averaging for too many steps with no restart term and no deflation of the DC component, and **every concept vector converges to the same degree-weighted global mean.** This is precisely GNN oversmoothing: Li et al. (2018) [6] show graph convolution IS Laplacian smoothing, and stacking layers drives representations toward a shared subspace, destroying discriminative information. Oono & Suzuki (2020) [7] formalize the rate: under repeated normalized aggregation (+ReLU), node representations converge **exponentially in the number of layers/steps, at a rate governed by the spectral gap (`lambda_2`, algebraic connectivity)** to the invariant subspace spanned by eigenvalue-0 eigenvectors (one dimension per connected component). A well-connected, high-spectral-gap concept graph collapses to the trivial mode *fast* -- this is a genuine, provable, silent failure mode (metrics can look "smooth/coherent" while the vectors are actually information-free).

**The fix (used identically in label propagation and modern GNN practice):** either (a) a restart/anchor term (`(1-alpha) x^{(0)}`, i.e., personalized-PageRank-style diffusion, which converges to a non-trivial fixed point balancing smoothness against fidelity to the original signal), or (b) hard early-stopping after a small fixed number of steps (= an implicit low-pass filter at a tunable cutoff, exactly the Q1 top-k truncation), or (c) explicit deflation of the DC/mean mode before each step. **This is not optional** given the proven exponential-collapse dynamics.

## 4. Incremental / streaming updates as the DB grows

**Nystrom out-of-sample extension** (Bengio, Paiement, Vincent, Delalleau, Le Roux & Ouimet 2004 [9], the unifying framework for LLE/Isomap/MDS/Eigenmaps/spectral-clustering out-of-sample extension): given existing eigenpairs `(lambda_k, u_k)` on `m` existing nodes and a new node with similarity vector `w = [W(new,1), ..., W(new,m)]`, the extension is
```
u_k(new) = (1/lambda_k) * sum_i w_i * u_k(i)
```
-- literally a similarity-weighted average of the new node's neighbors' *existing* coordinates, rescaled by `1/lambda_k`. **Cost: O(degree of new node) per eigenvector, O(k * degree) total** -- cheap, no re-decomposition. Note this is exactly one Nystrom-flavored diffusion step (Q3), so the practical answer is: **placing a new concept = run one (or a few) diffusion steps centered on it, seeded from its neighbors' current vectors.** Accuracy: exact for points consistent with the existing low-rank structure; degrades for a genuinely novel node with weak/no similarity to existing concepts (nothing informative to interpolate from) -- extrapolation beyond the sampled manifold is a known weak point of Nystrom, not a bug specific to this application.

**Rank-1/few perturbation + when to actually recompute.** Treat a new node (or a batch) as a low-rank perturbation of the existing Laplacian. The Davis-Kahan sin(theta) theorem (Davis & Kahan 1970 [10]) bounds how much the *retained* top-k eigenvectors rotate: the bound scales as `||perturbation|| / eigengap`. Operational policy: if the new edges are weak relative to the gap between the retained and discarded eigenvalue blocks, old eigenvectors barely move and Nystrom projection is sufficient; if new edges are comparable to or exceed the gap, the top-k subspace itself is stale and warrants a real (batched) recompute. Practical compromise from the online-spectral-clustering / incremental-kernel-PCA literature: **use Nystrom/diffusion-step placement continuously; schedule a full Lanczos re-solve periodically (every K new concepts, or when a cheap running estimate of the spectral gap crosses a threshold)** rather than after every insertion.

## 5. Composition, curvature, and the brain

**(a) Does spectral/disentangled geometry make vector addition land at meaningful points?** This is the weakest-evidenced of the five claims -- flag it honestly as **aspirational for pure Laplacian eigenmaps.** Bernardi et al. 2020 (Cell) [15] show PFC/hippocampal population geometry is simultaneously *disentangled* (factorized, near-orthogonal per-variable directions) and high-dimensional enough to support flexible generalization -- an empirical finding measured via cross-condition decoder generalization, established from *task-structured* neural recordings, not from any graph-Laplacian construction. Nothing in the Belkin-Niyogi / Coifman-Lafon / Shuman literature proves or even claims linear compositionality (`a+b=c` landing meaningfully) -- the Laplacian eigenbasis is optimized purely for *smoothness/cluster-coherence*, a different desideratum. The closest actual theoretical support for word-analogy-style linear compositionality is Arora, Li, Liang, Ma & Risteski's RAND-WALK model (2016) [16], a log-linear generative model over a PMI/co-occurrence structure (spectral-*adjacent*, since PMI-factorization is itself a similarity-matrix factorization, but requiring the specific log-linear/isotropy assumptions of that model) -- not a property of generic Laplacian smoothing.

**(b) Hyperbolic embeddings** (Nickel & Kiela 2017 [11]): a genuine, big win *specifically* for tree-like/hierarchical structure. Constant-negative-curvature (Poincare ball) space represents trees with exponentially lower distortion at fixed dimension than Euclidean space (a tree with branching factor `b` needs only `O(log b)` hyperbolic dimensions vs `O(b)` Euclidean, per the combinatorial constructions of Sarkar 2011 [12] and Sala et al. 2018 [13]). This is conditional on the knowledge actually being tree-shaped (e.g., is-a taxonomies) -- it is not a general-purpose replacement for spectral methods on arbitrary associative graphs. Combining hyperbolic geometry with spectral/diffusion constructions is an active, emerging research direction, not a mature settled toolkit -- treat as promising, gated by a cheap diagnostic (Gromov delta-hyperbolicity on the actual concept graph) before committing any build effort.

**(c) Grid cells as SR eigenvectors** (Stachenfeld, Botvinick & Gershman, "The hippocampus as a predictive map," Nature Neuroscience 2017 [14]): place cells ~ rows of the Successor Representation matrix `SR = sum_t gamma^t P^t = (I - gamma P)^{-1}` -- itself the resolvent of exactly the same random-walk operator `P` used throughout this note (so `SR`'s eigenvectors are the *same* eigenvectors as `P`/`L_rw`, only the eigenvalues are transformed, `1/(1-gamma*lambda_P)`). Grid cells are reported to resemble the SR's eigenvectors, i.e. approximately the low-frequency eigenbasis of the same operator. **Evidence level: a well-regarded, empirically-supported normative/computational-level theory, not settled physiological consensus** -- it competes with and is complementary to oscillatory-interference and continuous-attractor mechanistic models of grid cells that explain the same phenomenon through non-eigenvector mechanisms. Treat as "one well-supported normative hypothesis," not "proven brain implementation of eigendecomposition."

## HONEST LIMITS

1. **Spectral methods capture RELATIONAL/topological structure of the concept graph as given -- they do not provide grounding.** A perfectly coherent, degree-invariant spectral arrangement of concepts with no exogenous referent is still ungrounded (consistent with the standing finding that grounding needs an active, exogenous sampling process, not just internal geometric coherence).
2. **All practical constructions here are approximate, not exact** (Lanczos, randomized SVD, Nystrom, finite-step diffusion truncation). Approximation quality is governed by the spectral gap / eigenvalue decay of the actual concept graph. A near-random or near-complete graph (flat spectrum, no gap) means low-rank compression discards real structure, not just noise -- this is a property of the data, not a tuning knob.
3. **Oversmoothing/collapse is a genuine, provable failure mode, not hypothetical** (Oono-Suzuki [7]). An unclamped consolidation loop WILL collapse to the trivial constant mode at a rate set by the spectral gap. The failure is silent -- collapsed vectors can still look "smooth" and self-consistent while carrying zero discriminative information.
4. **Thin-data regime limits factorization.** Early in the substrate's life (few concepts, sparse edges), eigenvectors beyond the first 1-2 fit noise, not structure -- there is a minimum connectivity density below which this machinery is premature and should not be relied on for arrangement decisions.
5. **Composition-lands-meaningfully (Q5a) is the least-supported claim** -- explicitly aspirational, not proven for Laplacian-eigenmap-style geometry.
6. **Degree-invariance (Q2) fixes bias, not variance.** Low-degree/thin-data nodes are still noisier even under normalized Laplacians -- normalization is not a cure for data sparsity.

## BUILD RECOMMENDATION

**Yes** -- the consolidation loop's per-step update rule should literally be a random-walk-normalized diffusion step:
```
x_i <- (1 - alpha) x_i + alpha * (sum_j W_ij x_j) / d_i     [= x <- (1-alpha)x + alpha*P*x]
```
This is degree-invariant *by construction* (each neighbor's contribution to node `i` is normalized by `i`'s own degree, not by the neighbor's popularity), requires no eigendecomposition to run online, and is provably an Euler-discretized heat-diffusion / low-pass filter -- i.e., it IS the incremental solver for the graph Fourier transform's low-frequency components.

**Mandatory safety valve:** include a restart/anchor term (Zhou et al.-style `(1-alpha) x^{(0)}` personalized-PageRank form, or hard early-stopping after a small fixed step count, or periodic deflation of the running mean). This is not optional -- the Oono-Suzuki collapse dynamics are exponential and will silently zero out discriminative content if omitted.

**Cheapest incremental version for a growing DB:**
- Never do a full eigendecomposition online. Use the diffusion loop itself (already needed for existing-concept updates) as the entire online update mechanism -- this sidesteps `O(N^3)`/Lanczos cost for the common case entirely.
- Place a brand-new concept by seeding it from a similarity-weighted average of its neighbors' *current* vectors (one Nystrom-style / diffusion-centered step, cost `O(degree of new node)`).
- Reserve full/explicit spectral analysis (top-k Lanczos) as a periodic **offline diagnostic**, not the online update rule: use it to measure the current spectral gap, check oversmoothing risk, and decide whether the top-k subspace has drifted enough (Davis-Kahan-motivated trigger) to warrant a batched recompute -- e.g., every K new concepts or when the running spectral-gap estimate (obtainable nearly free from the diffusion loop itself via power-iteration deflation) drops below a threshold.
- Do not adopt hyperbolic geometry by default -- gate it behind a cheap Gromov delta-hyperbolicity / degree-distribution diagnostic on the actual concept graph; only invest if the diagnostic shows genuine tree-like structure.
- Do not expect vector-addition composition to fall out of this machinery for free. If linear composability is wanted, treat it as a separate objective (PMI/log-linear factorization a la Arora et al. [16], or explicit compositional training) layered alongside, not a free byproduct of Laplacian smoothness.

## Cheap decisive test

Build (or reuse) a synthetic scale-free graph (power-law degree, planted community structure) as a controlled stand-in for the substrate concept graph. Run, on IDENTICAL data:
(a) unnormalized Laplacian eigenmap embedding, vs
(b) random-walk-normalized diffusion-loop embedding (few iterations of `x <- (1-alpha)x + alpha*P*x` WITH restart term).

Measure `corr(node degree, embedding-vector deviation-from-centroid-norm)` in each case.

**HARD-PASS:** `|corr|` under (b) drops below ~0.10, while `|corr|` under (a) is >0.40 on the same test graph -- confirms the fix transfers to this new mechanism (same signature as the additive-code degree-collapse we already killed).

**HARD-FAIL (either signals the recipe, not the direction, needs revision):**
- (b) still shows `|corr| > 0.30` (normalization doesn't transfer to this construction), OR
- (b) collapses to near-constant vectors within <20 diffusion steps at the alpha needed for useful mixing (oversmoothing dominates before structure forms; restart-term strength needs retuning).

## Cross-thread synthesis

- Directly continuous with `project_grounding_needs_active_intervention_exogenous_referent_3source_synthesis_2026-07-09.md`: spectral arrangement is a RELATIONAL-coherence tool, not a grounding mechanism -- it operates entirely on the "borrowed/bake-in" side, doesn't touch the "active-intervention" grounding gap.
- Directly relevant to the recent additive-code degree-collapse finding (`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md` family): the unnormalized-Laplacian failure mode (Q2) is the textbook, decades-proven analogue of that exact bug pattern, and the normalized-Laplacian fix is the textbook analogue of the fix, giving external validation that "normalize by own degree, not by neighbor popularity" is the right general-purpose lever, not a one-off patch.
- Opens `network-science-graph-theory` (Tier-1b adjacency, currently 0 drills) as a live field for the research field-advisor's tracking -- recommend logging this drill under that field going forward.

## Substrate-product implications

- If adopted, the consolidation loop becomes a single, cheap, degree-invariant operation with a provable low-pass-filter interpretation and a known, provable failure mode (with a known fix) -- this converts "consolidation" from a heuristic averaging step into an instrumented, falsifiable piece of substrate physics (matches the observable-substrate design principle: measurable spectral gap, measurable collapse rate, measurable HARD-PASS/HARD-FAIL criteria above).
- Concept-DB growth becomes O(degree) per insertion in steady state (Nystrom-style placement), with only periodic O(sparse-Lanczos) audits -- this is the concrete scalability answer to "how do we not recompute the whole arrangement every time a concept is added."
- Hyperbolic geometry and forced compositionality are explicitly NOT recommended as default build targets from this drill -- both require additional, currently unmet preconditions (diagnosed tree-structure; a separate compositional-training objective).

## Citations (verified count: 16, all confirmed via WebSearch/WebFetch this session)

1. Belkin, M. & Niyogi, P. (2003). Laplacian Eigenmaps for Dimensionality Reduction and Data Representation. Neural Computation.
2. Coifman, R.R. & Lafon, S. (2006). Diffusion Maps. Applied and Computational Harmonic Analysis.
3. Shuman, D.I. et al. (2013). The Emerging Field of Signal Processing on Graphs. IEEE Signal Processing Magazine 30(3):83-98.
4. von Luxburg, U. (2007). A Tutorial on Spectral Clustering. Statistics and Computing.
5. Ng, A.Y., Jordan, M.I. & Weiss, Y. (2002). On Spectral Clustering: Analysis and an Algorithm. NIPS.
6. Li, Q., Han, Z. & Wu, X.-M. (2018). Deeper Insights into Graph Convolutional Networks for Semi-Supervised Learning. AAAI.
7. Oono, K. & Suzuki, T. (2020). Graph Neural Networks Exponentially Lose Expressive Power for Node Classification. ICLR.
8. Zhou, D., Bousquet, O., Lal, T.N., Weston, J. & Scholkopf, B. (2004). Learning with Local and Global Consistency. NIPS.
9. Bengio, Y., Paiement, J.-F., Vincent, P., Delalleau, O., Le Roux, N. & Ouimet, M. (2004). Out-of-Sample Extensions for LLE, Isomap, MDS, Eigenmaps, and Spectral Clustering. NIPS.
10. Davis, C. & Kahan, W.M. (1970). The Rotation of Eigenvectors by a Perturbation, III. SIAM Journal on Numerical Analysis 7:1-46.
11. Nickel, M. & Kiela, D. (2017). Poincare Embeddings for Learning Hierarchical Representations. NIPS.
12. Sarkar, R. (2011). Low Distortion Delaunay Embedding of Trees in Hyperbolic Plane.
13. Sala, F. et al. (2018). Representation Tradeoffs for Hyperbolic Embeddings. ICML.
14. Stachenfeld, K.L., Botvinick, M.M. & Gershman, S.J. (2017). The Hippocampus as a Predictive Map. Nature Neuroscience.
15. Bernardi, S., Benna, M.K., Rigotti, M., Munuera, J., Fusi, S. & Salzman, C.D. (2020). The Geometry of Abstraction in the Hippocampus and Prefrontal Cortex. Cell 183(4):954-967.
16. Arora, S., Li, Y., Liang, Y., Ma, T. & Risteski, A. (2016). RAND-WALK: A Latent Variable Model Approach to Word Embeddings. TACL.

## Falsifiable predictions with calibrated P (lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]])

Note: items 1-4 below rest on rigorously-proven pure mathematics (not uncertain as pure theorems); the P estimates below are about *substrate-application success* (an uncharted regime), which is where the deflation applies -- pure-math correctness is not what's being hedged.

- P(normalized-Laplacian/PPR diffusion step measurably removes degree bias in the substrate's actual concept graph, per the decisive test above) = 0.55 (deflated from a base ~0.75 given proven generality of the theorem; substrate-specific transfer is the uncertain part). HARD-FAIL: `|corr|>0.3` persists under normalization.
- P(consolidation-loop-as-implemented is a *useful*, non-collapsing incremental GFT solver without further tuning) = 0.50 (capped -- novel-synthesis cap per [[feedback-lit-scan-calibration-penalty]]; the equivalence itself is definitional/certain, but avoiding collapse in practice needs the restart-term tuned correctly, unverified for this substrate). HARD-FAIL: collapse to near-constant vectors within <20 steps at usable alpha.
- P(hyperbolic geometry is a net win if adopted without the gating diagnostic) = 0.25 -- LOW, explicitly not recommended without first measuring delta-hyperbolicity.
- P(vector-addition composition falls out of pure spectral/Laplacian arrangement) = 0.15-0.20 -- lowest confidence of all five, flagged aspirational.
- P(grid-cell/SR-eigenvector story is the literal, sole, settled mechanism in biological entorhinal cortex) = 0.40 -- reasonably well-supported normative hypothesis, not settled mechanism (competing models exist).

## Next-drill candidate

`network-science-graph-theory` (Tier-1b, currently 0 logged drills) -- natural follow-up angle: expander/Ramanujan spectral-gap bounds as a predictive proxy for the substrate's pool-retrieval quality bound, directly reusing the spectral-gap machinery established in this drill (Oono-Suzuki collapse rate, Davis-Kahan staleness trigger).
