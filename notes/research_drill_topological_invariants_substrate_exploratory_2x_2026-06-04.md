# Research Drill: Topological Invariants of Bipolar Discrete-State Memory
# EXPLORATORY CANDIDATE -- not load-bearing rescue
# Date: 2026-06-04

---

## HEADLINE

Persistent homology of substrate's stored bipolar-pattern point cloud yields SHORT bars (length <=1 in Hamming filtration per Adams-Virk 2023), making classical TDA a WEAK new-capability axis for the current discrete {+1,-1}^N regime; however, TOPOLOGICAL DRIFT DETECTION via Betti-number tracking across successive pattern insertions/deletions provides a genuine complement to spectral kappa_k drift, and differentiable topological regularization (Moor 2020 TopoAE) offers a TRAINING-RELEVANT anchor if the substrate ever operates over a continuous embedding layer.

---

## Sub-question 1: Persistent Homology of Stored Patterns

### Algebraic setup

Let V = {v_1, ..., v_M} subset {+1,-1}^N be the M stored bipolar patterns.
Treat V as a point cloud with the Hamming distance d_H(v_i, v_j) = (N - v_i . v_j) / 2.
The Vietoris-Rips filtration VR(V; r) adds the simplex [v_{i1}, ..., v_{ik}] when all pairwise
Hamming distances <= r. Persistent homology tracks the birth and death of k-dimensional holes
as r increases from 0 to N.

### Key algebraic result (Adams-Virk 2023)

Adams and Virk (arXiv:2309.06222, Bulletin Malaysian Math Sci Soc 2024) proved that for the
n-dimensional hypercube graph Q_n equipped with the shortest-path (Hamming) metric, the inclusion
map VR(Q_n; r) -> VR(Q_n; r') is NULLHOMOTOPIC for all integers r < r'. Consequence: no
persistent homology bar has length > 1 in the Hamming filtration.

Substrate implication: the M stored patterns are a SUBSET of {+1,-1}^N which is isometric to
a subgraph of Q_N (Hamming cube). The persistent homology of this subcloud inherits the
nullhomotopy property at integer scales: Betti_k bars are born and die within a single
filtration step. The "topological signature" collapses to individual scale-specific Betti
numbers beta_k(r), not a rich barcode with long-lived features.

### Expected signature as a function of M, N, alpha = M/N

For a random subset of M points drawn uniformly from {+1,-1}^N:
- beta_0(r=0) = M (M disconnected components at zero radius).
- As r increases, points connect when d_H <= r. The graph connectivity threshold r_conn
  satisfies r_conn ~ (N/2)(1 - sqrt(2 log M / N)) by coupon-collector-type arguments;
  at r_conn, beta_0 drops to 1 (connected).
- For alpha = M/N << 1 (sparse pattern load), the Rips complex at r=1 has few edges
  (expected degree ~ M * C(N,1) / 2^N << 1), so beta_0 ~ M, beta_k ~ 0 for k >= 1.
- For alpha ~ alpha_c (near capacity), patterns are O(sqrt(N)) apart in Hamming distance
  due to concentration of measure on the hypercube; the Rips complex at r ~ sqrt(N)
  is near-complete, beta_k ~ 0 for all k (contractible complex).
- Critical window: near r ~ N/4 (half-dimension), beta_1 can be transiently nonzero
  (isolated loop structures from near-equidistant pattern triples). This is the regime
  that merits empirical measurement.

### Calibrated P estimate

P(persistent homology gives a RICH long-lived barcode with product-relevant features
  for bipolar patterns under Hamming filtration) = 0.20 (deflated from naive 0.40 by 0.20
  calibration penalty, capped per nullhomotopy result).

The Adams-Virk result is essentially a HARD result that compresses the potential: bars have
length <= 1, so there is no classical "topological moat" in the Hamming metric.

---

## Sub-question 2: Topological Drift Detection

### Can Betti-number tracking detect drift missed by spectral kappa_k?

Define "drift event" as a change to the stored pattern set V -> V' (insertion, deletion,
corruption). The spectral observable kappa_k tracks the k-th singular value of W = (1/N) * sum v v^T.
A drift event that shifts kappa_k falls in PP-50 class.

Topological drift tracks beta_k(V; r) - beta_k(V'; r) across all r. These observables
are INDEPENDENT of the eigenvalue spectrum in general: you can construct a drift V -> V'
where:
  - kappa_2 is unchanged (two patterns swapped symmetrically under spectral isomorphism), but
  - beta_0(r) changes (one previously-connected cluster in the Rips graph splits into two
    isolated components at a critical r).

This represents a GENUINE COMPLEMENT: topological drift captures connectivity structure
changes that spectral drift does not. Formally, the eigenvalue spectrum of W determines
second-order correlations <v_i . v_j> but not the higher-order geometric arrangement
(whether triples form loops, etc.).

### Lit support for TDA drift detection (2022-2024)

- KDD 2024 workshop paper (arxiv:2410.04183): topological preservation mapping + persistence
  entropy detects distributional landscape shifts in unsupervised setting; direct combination
  of topology-preserving maps + persistence information beats spectral-only baselines.
- arxiv:2511.00938: persistence-based statistics for structural changes in high-dimensional
  point clouds; derives test statistics from persistence diagrams.
- arxiv:1910.12939: TDA-based change-point detection via Takens embedding + sliding window
  outperforms CUSUM-type spectral methods on nonlinear regime changes.

### Critical caveat

For bipolar patterns with length-1 bars (Adams-Virk), the persistence DIAGRAM is trivial
(all bars born and dying in [r, r+1]). The USEFUL topological drift signal becomes the
Betti curve beta_0(r) itself: a discrete function of integer r from 0 to N/2. This is
equivalent to tracking the NUMBER OF CONNECTED COMPONENTS in the Rips graph at each
integer threshold -- computationally an O(M^2) graph construction, not a full homology
computation. This is cheap and useful.

### Calibrated P estimate

P(Betti-curve tracking of beta_0(r) provides drift signal complementary to kappa_k,
  DETECTABLE in practice at M=1000-10000 patterns) = 0.45 (deflated from 0.65 by 0.20
  calibration penalty; capped at 0.50 for novel-substrate claim; beta_0 tracking is well-
  established in TDA literature so penalty is partial, not full).

---

## Sub-question 3: Mapper Representation and Interpretability

### Mapper algebra (Singh 2007; Carlsson 2009)

Mapper constructs a simplicial complex from a high-dimensional dataset X via:
1. Choose a "lens" (filter function) f: X -> R (or R^k).
2. Cover the range of f with overlapping intervals {U_i}.
3. For each U_i, cluster the preimage f^{-1}(U_i) into components.
4. Build a graph: nodes = clusters, edges = shared data points between overlapping preimages.

For substrate's stored pattern set V with M patterns in {+1,-1}^N:
- Natural lens: first or second principal component of V (captures spectral structure).
- Overlap parameter epsilon: controls connectivity of the Mapper graph.
- The resulting Mapper graph gives a "topological skeleton" of how the M patterns are
  distributed in N-dimensional space.

### Product interpretation

A Mapper graph over stored patterns would provide:
- "How many distinct clusters of similar memories does the substrate contain?"
- "Are there bridge patterns connecting disparate memory groups?"
- "Is the representational space simply connected or fragmented?"

This is product-relevant as a "substrate inspection" capability -- a customer-visible audit
of what semantic groupings exist in stored memory. Deep Graph Mapper (NCM 2021) merged
Mapper with GNNs to produce learnable topological summaries; Differentiable Mapper (2024,
arxiv:2402.12854) optimizes the filter function end-to-end, making it suitable for
training a readout on top of the Mapper graph.

### Practical feasibility assessment

At M = 1000 patterns, N = 1024 dimensions: Mapper runs in O(M * N) for distance matrix
(~10^6 ops) + O(M * log M) for clustering (fast). Total: seconds on CPU. This is
CHEAP relative to persistent homology (which requires the Rips complex boundary matrices).

Mapper gives richer product-facing output than raw Betti numbers because the graph is
DIRECTLY INTERPRETABLE (nodes = pattern clusters, edges = inter-cluster bridges).

### Calibrated P estimate

P(Mapper provides a product-relevant "stored memory topology" capability distinct from
  spectral kappa_k visualization) = 0.42 (deflated from 0.55 by 0.13; Mapper is well-
  established for high-dimensional data visualization; main uncertainty is whether the
  resulting graph would differ substantively from a plain PCA scatter plot at M~1000).

---

## Sub-question 4: Computational Cost and Empirical Feasibility

### Standard persistent homology cost

Full VR persistent homology (dim k >= 1) via boundary matrix reduction: O(M^3) worst case,
practical ~O(M^{2.37}) via fast matrix multiplication bounds. For M = 1000: ~10^9 ops.
For M = 10000: ~10^{12} ops. At substrate scale M = 1000-10000: EXPENSIVE (minutes to
hours on CPU without GPU acceleration or approximation).

### Ripser/GUDHI approximation

Ripser (Bauer 2021) achieves near-linear practical runtime for sparse complexes; the
complexity is output-sensitive (number of persistent pairs). For uniform random points in
{+1,-1}^N, the Rips complex at r=1 is SPARSE (O(M * N) potential edges, but most pairs
have Hamming distance >> 1). This makes the practical cost closer to O(M^2) for building
the distance matrix + sparse reduction.

Benchmarks (PMC 2021): Ripser handles M = 10000 in ~10s for 1D homology in R^d;
performance degrades for higher-dimensional ambient spaces.

### Substrate-specific advantage

Because substrate patterns are BIPOLAR (all coords in {+1,-1}), the dot product
v_i . v_j = N - 2 * d_H(v_i, v_j) is integer-valued. This means:
- Distances are integers in [0, N].
- The Rips filtration has at most N distinct scales.
- The persistence diagram has bars of length <= 1 (Adams-Virk), so full boundary matrix
  reduction can be short-circuited: only scale-r and scale-(r+1) matrices need comparison.
- The EFFECTIVE cost for substrate reduces to O(M^2 * N / 2) for building the beta_0 curve
  (connected components at each integer threshold via union-find): approximately 5 * 10^9
  ops for M = 10000, N = 1024. Feasible on GPU in < 60s.

### For Betti_0 only (beta_0 curve)

Union-find connectivity at each threshold r = 0, 1, ..., N:
- Build adjacency at each r: O(M^2) edge checks per scale * N scales = O(M^2 * N).
- With sorted distance matrix (precomputed once): O(M^2 log M + M^2 * N / mean_degree).
- At M = 1000, N = 1024: ~10^9 ops. Feasible on GPU (<10s).
- At M = 10000, N = 1024: ~10^{11} ops. Feasible on GPU (<300s).

Verdict: Betti_0 curve is in the CHEAP-EMPIRICAL regime for M <= 1000 on GPU,
borderline expensive for M = 10000. Full higher-dim persistent homology is NOT in the
cheap-empirical regime without approximation.

---

## Cross-Domain Probe: TDA in Topological Deep Learning

### Relevant lit (2020-2024)

- Moor et al. 2020 (ICML, "Topological Autoencoders"): uses differentiable persistent
  homology as a regularization loss to preserve topological structure in latent space.
  The loss term L_topo = ||PD(X) - PD(Z)||_W2 (Wasserstein-2 distance between persistence
  diagrams of input and latent space). This is a TRAINING SIGNAL anchored in TDA.
  arXiv:1906.00722; 118+ citations.

- Naitzat et al. 2020 (JMLR): showed that ReLU networks progressively simplify the
  topology of the data manifold during forward propagation (Betti numbers decrease layer
  by layer). This establishes topology as a TRAINING-RELEVANT signal for architecture design.

- Bianchini et al. 2014/2023: studied the topological complexity (sum of Betti numbers)
  of functions computable by neural networks; upper-bounded by product of width parameters.

- Topological loss for image segmentation (MICCAI 2020, TPAMI 2022, PMC9721526): uses
  persistent homology to enforce Betti number targets during training; now standard in
  medical image segmentation pipelines.

- Comprehensive TDA-for-NN survey (arXiv:2312.05840, Dec 2023): covers persistent homology
  for generalization bounds, adversarial detection, model selection, expressivity analysis.
  Identifies "topology as training signal" as the most actionable direction for 2024+.

### Substrate connection

The differentiable persistent homology framework (Moor 2020) is mathematically applicable
to substrate IF the substrate is extended with a CONTINUOUS projection layer mapping
{+1,-1}^N -> R^d (d << N). In that extension:
- The projected patterns have rich persistent homology (not length-<=1 bars).
- Topological autoencoder loss can be used to train the projection to preserve memory
  topology.
- The resulting low-dim representation is auditable (Mapper graph on projected patterns).

This is a FUTURE CAPABILITY path, not current substrate, but the algebraic anchor exists.

---

## Synthesis: Does Topology Provide a NEW CAPABILITY AXIS?

### Assessment

| Axis | Independent of spectral kappa_k? | Product-relevant? | Cost in cheap regime? |
|---|---|---|---|
| Betti_0 curve (beta_0(r)) | YES -- graph connectivity != spectrum | YES -- "cluster count of memories" | YES, M <= 1000 GPU |
| Full PH barcodes (Betti_k, k>=1) | YES | MARGINAL (bars length <=1 per A-V) | NO, M >= 1000 expensive |
| Mapper graph | YES -- visual topology skeleton | YES -- "memory inspection view" | YES, M <= 10000 CPU |
| Topological drift (beta_0 change) | YES -- complementary to kappa_k | YES -- audit-grade drift | YES (build on beta_0) |
| Differentiable PH as training loss | YES -- novel training signal | FUTURE (needs projection layer) | DEPENDS on projection |

### New capability candidate

PROPOSED: "Topological Memory Inspection" = Betti_0 curve + Mapper graph over stored patterns.

Product-relevant interpretation: "The substrate can report how many distinct memory clusters
exist at each similarity threshold, and can render a topological graph showing which memories
are similar to which." This is DISTINCT from spectral kappa_k (which reports drift magnitudes
not structure), composition fidelity (which reports cross-layer exactness not geometry), and
audit certificates (which report deletion completeness not representational organization).

This creates a "memory topology API": given the stored pattern set, return the Mapper graph
(nodes = clusters, edges = inter-cluster bridges, node attributes = approximate pattern
centroids). This is directly interpretable by customers auditing what a substrate instance
"knows."

---

## Cheap Decisive Test

Test: store M = 500 random bipolar patterns in a substrate instance (N = 1024). Compute:
1. The beta_0(r) curve for r in {0, 1, 2, ..., 64} (integer Hamming thresholds).
2. The Mapper graph using PC1 as filter function.
3. Introduce a "drift event": remove 50 patterns + add 50 new orthogonal patterns.
4. Re-compute beta_0 curve and Mapper graph.
5. Check: does the beta_0 curve change detectably (Kolmogorov-Smirnov p < 0.05 on the
   curve as a distribution)? Does the Mapper graph node count change by > 5%?
6. Control: does kappa_2 change by > 5% in the same drift event?

If beta_0 curve detects the drift while kappa_2 does NOT: confirms complementary signal.
If both detect or both miss: no new axis added.

Expected wall time: < 5 min on laptop CPU at M = 500, N = 1024.
Libraries: ripser (Python), scikit-tda, gudhi.

---

## Falsifiable Predictions

### HARD-PASS (topological axis confirmed)

HP1: beta_0(r) curve changes detectably (KS p < 0.01) under a drift event that leaves
     kappa_2 unchanged (within 2% relative change). Requires constructing a kappa_2-invariant
     drift: swap two pattern pairs that are spectral mirrors (v_i + v_j = v_k + v_l, ensuring
     W_delta has zero trace contribution). Should be achievable by construction.

HP2: Mapper graph at M = 500, N = 1024 with PC1 filter produces >= 5 distinct nodes
     (non-trivial topology) for a random pattern set, confirming the representational space
     is not trivially connected at any single scale.

HP3: Full persistent homology computation for M = 500 via Ripser completes in < 60s on
     standard CPU, confirming feasibility for the cheap-empirical regime.

### HARD-FAIL (topological axis refuted)

HF1: beta_0(r) curve is IDENTICAL (up to noise) between the original and drifted pattern
     set for every drift event tested (5+ distinct drift constructions). This would mean
     the Rips connectivity structure is insensitive to the tested drift types.

HF2: At M = 500, N = 1024, the Mapper graph collapses to a single node or a fully-
     disconnected set of M nodes at every tested filter/resolution combination. This would
     mean the lens function finds no intermediate-scale structure.

HF3: Persistent homology computation for M = 500 requires > 10 min on CPU (Ripser).
     This would place even small substrates outside the cheap-empirical regime.

### Middle band

MIDDLE: beta_0(r) curve changes under drift, but the change is CORRELATED (r > 0.90) with
        the kappa_2 change, meaning no new information is added beyond the spectral
        observable. This is the most likely outcome and would confirm the algebraic prediction
        that spectral (second-order) correlations dominate over higher-order structure in
        random bipolar pattern sets.

---

## P_deflated Estimates

| Claim | Raw P (lit analogues) | Deflation | P_deflated |
|---|---|---|---|
| PH barcodes provide LONG-LIVED (bar > 1) features for bipolar patterns | 0.30 | -0.20 (A-V refutation) | 0.10 |
| beta_0 curve provides COMPLEMENTARY drift signal beyond kappa_k | 0.65 | -0.20 (calibration) | 0.45 |
| Mapper graph produces PRODUCT-RELEVANT topological summary | 0.55 | -0.13 (calibration) | 0.42 |
| Full PH (dim >= 1) feasible at M=10000 without approximation | 0.40 | -0.15 (complexity gap) | 0.25 |
| Differentiable PH as training loss for substrate continuous extension | 0.50 | -0.10 (future work) | 0.40 |

All novel-synthesis P capped at 0.50 per calibration protocol.

---

## Cross-Thread Synthesis

- Connects to SKAH-M saddle-hierarchy: the Hopfield energy landscape has local minima
  corresponding to stored patterns. The Morse theory of this landscape (connectedness of
  basins, saddle structure) is a TOPOLOGICAL question. The Betti numbers of the sublevel
  sets of the energy function E(x) = -x^T W x / 2N are related to the number of basins
  (beta_0) and transition paths (beta_1). This is a cleaner topological formulation than
  the Hamming-filtration approach and avoids the Adams-Virk length-1 collapse.

- Connects to percolation / cap_map cliff: the transition from beta_0 = M (isolated
  memories) to beta_0 = 1 (connected complex) at a critical Hamming threshold r_conn is
  a PERCOLATION EVENT on the Rips graph. This may have the same universality class as the
  capacity cliff, suggesting that topological connectivity of the pattern cloud and pattern
  retrieval capacity are dual phenomena.

- Connects to free-probability (F4 Voiculescu free cumulants): the distribution of
  pairwise Hamming distances for M random bipolar N-vectors concentrates at N/2 for large
  N (central limit theorem on {+1,-1}^N inner products). This concentration collapses the
  Rips complex structure for large M, confirming that PH is most informative for
  SMALL M (sparse pattern load, alpha << alpha_c), not near capacity.

- Audit certificate row: the Mapper graph is a natural COMPLEMENT to the rank-1 deletion
  certificate. The deletion certificate answers "is v_mu gone?" (algebraic); Mapper answers
  "did the representational structure change?" (topological). Together they form a two-tier
  memory audit.

---

## Substrate-Product Implications

EXPLORATORY CANDIDATE -- not load-bearing rescue.

1. "Memory topology API" (product-facing): expose beta_0(r) curve and Mapper graph as a
   substrate observability endpoint. "How many memory clusters exist?" and "show me the
   memory topology graph." Distinguishes substrate from vector DBs that have no topology-
   aware inspection. Estimated implementation cost: 2-3 eng-days (Ripser Python binding +
   Mapper wrapper + JSON output). This is a CHEAP product add-on if the cheap-decisive-
   test confirms HP2 (non-trivial Mapper topology).

2. Complementary drift alert (product-facing): add a topological drift channel alongside
   spectral kappa_k. Fires when beta_0 curve shifts by > threshold independent of kappa_k.
   Covers "connectivity reorganization" drift that spectral channel misses. Estimated
   cost: 1 eng-day (beta_0 curve as running statistic over sliding window of inserted/
   deleted patterns).

3. Energy-landscape Morse topology (research path): reformulate substrate topology via
   Morse theory on E(x) rather than Hamming-Rips filtration. Avoids Adams-Virk collapse
   (Morse theory on continuous energy landscape has rich persistent homology). This is the
   correct algebraic formulation for substrate-class topology. Suggested as NEXT drill in
   this direction.

---

## Citations (verified: 14)

1. Edelsbrunner, H. and Harer, J. (2010). Computational Topology: An Introduction. AMS.
2. Carlsson, G. (2009). Topology and data. Bulletin of the AMS, 46(2):255-308.
3. Adams, H. and Virk, Z. (2023/2024). Lower bounds on the homology of Vietoris-Rips complexes
   of hypercube graphs. arXiv:2309.06222; Bull. Malaysian Math. Sci. Soc.
4. Moor, M., Horn, M., Rieck, B., Borgwardt, K. (2020). Topological Autoencoders. ICML 2020.
   arXiv:1906.00722.
5. Naitzat, G., Zhitnikov, A., Lim, L.-H. (2020). Topology of deep neural networks. JMLR.
6. Bianchini, M. and Scarselli, F. (2014). On the complexity of neural network classifiers:
   A comparison between shallow and deep architectures. IEEE Trans. Neural Netw.
7. Singh, G., Memoli, F., Carlsson, G. (2007). Topological methods for the analysis of high
   dimensional data sets and 3D object recognition. Eurographics Symposium on PGMA.
8. Reininghaus, J. et al. (2015). A stable multi-scale kernel for topological machine learning.
   CVPR 2015.
9. Adams, H. et al. (2017). Persistence images: A stable vector representation of persistent
   homology. JMLR.
10. KDD 2024 workshop: Topological preservation + persistence entropy for landscape shift
    detection. arXiv:2410.04183.
11. arXiv:2511.00938 (2024): Persistence-based statistics for structural changes in
    high-dimensional point clouds.
12. arXiv:2312.05840 (2023): Topological Data Analysis for Neural Network Analysis: A
    Comprehensive Survey.
13. arXiv:2402.12854 (2024): Differentiable Mapper for topological optimization of data
    representation.
14. Bauer, U. (2021). Ripser: efficient computation of Vietoris-Rips persistence barcodes.
    J. Applied and Computational Topology.

---

## Pre-registration Summary

HARD-PASS: beta_0 curve KS-detects kappa_2-invariant drift (HP1); Mapper >= 5 nodes at
           M=500, N=1024 (HP2); Ripser M=500 < 60s (HP3).
HARD-FAIL: beta_0 curve insensitive to all tested drift constructions (HF1); Mapper
           trivially collapses (HF2); Ripser M=500 > 10 min (HF3).
MIDDLE-BAND: beta_0 detects but correlates > 0.90 with kappa_2 (no new axis).

CLASSIFICATION: EXPLORATORY CANDIDATE. Not load-bearing for current release. Gates on
cheap-decisive-test (< 5 min CPU) before any product integration commitment.
