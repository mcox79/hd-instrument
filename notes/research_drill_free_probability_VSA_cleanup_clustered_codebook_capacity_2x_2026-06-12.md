# Research drill: free-probability x VSA cleanup x clustered codebook capacity (2x DEEP)

date: 2026-06-12
field: free-probability (Tier-1 underdrilled; advisor rank #1 candidate F4)
scope: 2x DEEP -- two rounds, 6 generic-math queries each, no substrate-novel names in queries
calibration penalty: applied (deflate P by 0.15-0.25; novel-synthesis cap P=0.50)

## Drill spec (recap, kept off-platform)

Substrate question (local-only): under intentional clustering of an N=280, D=1024 HRR/FHRR codebook (atoms grouped by VSA family / operation type / domain so that within-cluster similarity encodes meaning), does Resonator-style cleanup capacity vs the uniform-on-sphere Frady-Sommer cliff D^2/(F^2 K) LIFT, DROP, or stay unchanged? Empirical Tracy-Widom edge z is significantly negative on the codebook Gram (more clustered than random).

External queries used only generic literature terms (Marchenko-Pastur deformation, BBP, spiked covariance, structured Hopfield capacity, structured sparsity phase transitions, block stochastic spectral gap, Stieltjes free convolution).

## Round 1 findings (compact)

R1-a Marchenko-Pastur deformation / free probability. MP is the free-probability analogue of Poisson (free Poisson). Free multiplicative convolution of MP laws gives the canonical handle on products of correlated Gaussian / Wishart matrices. Pastur and Marchenko-Pastur deformation theory covers additive deformation of Wigner and multiplicative deformation of Wishart, both of which describe what happens when a random spectrum is perturbed by a structured (low-rank or block) signal. Key statement: when a deterministic structured matrix A is added to a free random matrix B, the limiting spectrum equals the free additive convolution mu_A box-plus mu_B; the bulk is unchanged but a finite set of outliers may appear above a critical perturbation strength.

R1-b Free cumulants / block / cyclic. Speicher-school result: structured (block / cyclic) random matrices have their spectrum determined by cyclic cumulants of the entries, computable via an extremization problem over operator-valued free probability. The free cumulants of the limit distribution carry the structural information; first-order moments are equivalent. For our setting this means: a clustered codebook Gram is the natural domain of operator-valued free probability, and its spectrum is computable in principle from the block structure of the cluster covariance.

R1-c Spiked covariance / BBP. Canonical result: if the population covariance has k "spikes" above the bulk, the largest sample eigenvalue separates from the MP bulk iff the spike exceeds the BBP threshold. Three regimes: subcritical (spike sticks to bulk edge, eigenvector delocalized, no detection); critical (Tracy-Widom-like fluctuations but shifted limit); supercritical (spike jumps out of bulk, eigenvector localizes on the planted direction). Geometric reading: cluster centroids in a clustered codebook play the role of spikes; each centroid above BBP threshold contributes a detectable rank-1 direction.

R1-d Hopfield / structured patterns. Classical Hopfield random-pattern capacity is alpha_c = 0.138 N. With clustered patterns: capacity can be raised to Theta(b^(n/b)) for clusters of size b, and using neural cliques up to O(n^2). Exponential capacity is achievable when patterns share redundancy or live in low-dim cluster manifolds, at the cost of reduced worst-case noise tolerance. Net direction: clustering LIFTS capacity but the cliff sharpens (less margin for noise once you exceed cluster radius).

R1-e Correlated associative memory. Effects of feature correlations on associative memory capacity (2025 arXiv): memory capacity scales exponentially with separation in input space; feature correlations REDUCE capacity slightly at constant separation but do not alter the exponential scaling. Counter-result (autonomous-retrieval / continual-learning 2025): moderate correlation actually IMPROVES retrieval by reshaping attractor-basin geometry. Pseudo-inverse-style decoders (which are exactly what Resonator-cleanup is) orthogonalize correlated patterns and recover error-free retrieval at higher load. This is the most directly substrate-relevant result.

R1-f Spectral density of correlated entries. Recent unifying derivation (2025) gives spectral density for correlated ensembles that interpolates Marchenko-Pastur and elliptic laws as special cases. Diagonal deformation plus variance profile: support of empirical spectrum coincides with the pseudospectrum. For clustered codebooks this means: clustering shows up as a band/block variance profile and shifts the bulk edge predictably; the cliff location moves but the existence of a cliff persists.

## Round 2 findings (compact, refined)

R2-a Tracy-Widom edge universality under correlations. Bourgade and others: extreme eigenvalues of correlation matrices converge to Tracy-Widom after centering/scaling despite strong entry dependence; the necessary condition is a local square-root singularity in the support. Edge fluctuations exhibit a third-order phase transition in the large-deviation rate function; left and right deviations follow distinct power laws. For our substrate: the empirical negative tw_edge_z is consistent with a non-Tracy-Widom regime, which the literature reads as "the local square-root assumption is violated" -- i.e., the codebook is in the structured / block regime where free probability with operator-valued kernel applies instead of vanilla Tracy-Widom.

R2-b Wishart with block / generalized structure. Generalized Wishart spectral density is obtained via free multiplicative convolution. The block-structured non-symmetric correlation Wishart model has been derived in closed form; the limiting spectrum is wider than MP and the edge is softer. For cleanup, a softer edge means the cliff transition is less abrupt, giving a finite-width crossover instead of a sharp cutoff.

R2-c Compressed sensing with structured / clustered support. Phase-transition curves shift FAVORABLY when non-zero coefficients are clustered: empirical recovery achievable at substantially lower measurement rates than for unstructured sparsity, even with up to 10 clusters. Donoho-Tanner-style phase diagrams for block-sparse signals have been characterized; the recovery threshold is governed by block size, not total k. Direct analogy: in VSA cleanup, "support" = which atoms are bound in the superposition; clustered codebook = clustered support; literature predicts the recovery (cleanup) threshold scales with clusters-active rather than atoms-active.

R2-d Stochastic block model spectral gap. SBM detection threshold (Massoulie, Mossel-Neeman-Sly): the second eigenvalue of the adjacency / Laplacian separates from the bulk above the Kesten-Stigum threshold; spectral algorithms achieve information-theoretically optimal community recovery at sufficient gap. For substrate: each cluster acts as a planted community; recovery (cleanup) succeeds when the inter-cluster Gram gap exceeds a BBP/KS-style threshold; below it, clusters merge in cleanup output.

R2-e Modern Hopfield / Ramsauer / sparse. Ramsauer-Hochreiter dense Hopfield achieves exponential capacity but only approximate retrieval and may need low temperature to avoid metastable states. Hu-Yang-Wu sparse modern Hopfield (NeurIPS 2023) and "Sparse and Structured Hopfield Networks" (Martins, 2024) derive tighter retrieval-error bounds than dense and show that block / structured sparsity in the energy gives EXACT retrieval at exponential capacity while preserving the attention-transformer link. For VSA cleanup the takeaway is sharp: replacing the implicit "all atoms compete uniformly" cleanup with a structure-aware (cluster-routed) cleanup recovers the exponential-capacity guarantee that vanilla cleanup forfeits.

R2-f Free convolution / Stieltjes for correlated. Local free additive convolution law has been established for A + U B U^* with deterministic A, B and Haar U; this gives the eigenvalue density of any structured-plus-noise model in closed form via Stieltjes transform fixed-point. For substrate this means: spectrum of (cluster-structured deterministic part) + (orthogonal-noise part) of the codebook Gram is exactly computable; the cliff location can be predicted from cluster geometry without simulation.

## Synthesis

- The free-probability prior is unambiguous on the QUALITATIVE direction: structured / clustered codebooks have spectra that differ from MP / uniform via free convolution with a deterministic block / spike component. The bulk softens, a finite set of outlier eigenvalues appears, and the cliff transition becomes a finite-width crossover governed by BBP-style thresholds.
- The Hopfield-capacity prior (classical + modern + sparse) is consistent: structured patterns LIFT capacity from O(N) to O(b^(N/b)) or exponential, IF the decoder is structure-aware. With a structure-blind decoder, structured patterns can DROP capacity (intra-cluster crowding) because the decoder cannot exploit the cluster separation.
- Compressed-sensing structured-sparsity prior agrees: clustered support shifts the recovery threshold favorably when the recovery algorithm is structure-aware (block-LASSO, group-LASSO), neutrally / unfavorably when it is not.
- Resonator-style cleanup is a pseudo-inverse / matched-filter decoder. The pseudo-inverse Hopfield rule is documented to orthogonalize correlated patterns and recover error-free retrieval at higher load. Therefore Resonator cleanup is in the structure-aware decoder class for at least linear-correlation structure, but not necessarily for higher-order cluster geometry.
- Predicted direction for substrate: LIFT, magnitude moderate, with a caveat. The clustered codebook gives Resonator cleanup an effective per-query codebook of size K_per_cluster (not K_total), provided cluster centroids exceed the BBP threshold relative to the noise floor. If centroids are subcritical, the literature predicts DROP because intra-cluster crowding dominates.
- Mechanistic reading: Frady-Sommer D^2 / (F^2 K) is the uniform-on-sphere prediction; under clustering the relevant denominator becomes F^2 K_eff with K_eff somewhere between (clusters-active) and (atoms-active per cluster), shifted by the cluster spectral gap. Net cliff location moves to HIGHER load, with a softer crossover (less abrupt).

## Substrate-product positioning prediction

- Expected direction at D=1024, N=280 clustered codebook: cleanup capacity LIFTS vs the uniform Frady-Sommer prediction, by a factor between 1.3x and 3x at F=3, with HARD-FAIL at <1.0x (no lift) and HARD-PASS at >2.0x (clear lift confirming clustered codebook is a feature not a bug).
- Uncertainty bound: literature does not give a closed-form substrate-specific number; the substrate's empirically-negative tw_edge_z is consistent with the structured / block regime, supporting the LIFT prediction qualitatively but not quantitatively.
- Substrate-product framing: the clustered codebook is the substrate's MEANING ENCODING; literature confirms this is mathematically a structured-Wishart + free-convolution regime; this is the substrate's natural mathematical context (operator-valued free probability + structured-Hopfield + block-LASSO phase transitions), NOT vanilla MP / uniform Frady-Sommer; treating it as the latter is the literature's toy case, not the substrate's home.

## Pre-registered prediction for Cell A + Cell B cleanup at F=3 fillers

HARD-PASS: cleanup top-1 accuracy at F=3 fillers on clustered codebook >= 2.0x cleanup top-1 accuracy predicted by Frady-Sommer uniform formula D^2 / (F^2 K) extrapolation at matched (D, K, F).
HARD-FAIL: cleanup top-1 accuracy at F=3 on clustered codebook <= 1.0x the uniform Frady-Sommer prediction at matched (D, K, F).
MIDDLE-BAND: 1.0x - 2.0x = partial lift, consistent with structure-blind decoder bottleneck; would trigger follow-up drill on cluster-routed cleanup.
Calibration penalty applied: raw lit-prior gives P(LIFT >= 2.0x) ~ 0.55; deflate by 0.20 -> P_deflated ~ 0.35. Capped at 0.50 per novel-synthesis rule. Final P_deflated = 0.35.

## Honest scope

- STRONG: qualitative direction (structured codebook is in the structured-Wishart / free-convolution regime, not uniform MP). Multiple independent literature streams agree.
- STRONG: existence of BBP-style threshold and finite-width crossover replacing sharp cliff.
- MODERATE: direction of capacity change (LIFT) under structure-aware decoder. Literature consensus is positive but decoder-structure-awareness is a precondition; whether Resonator cleanup qualifies for higher-order cluster geometry is open.
- MODERATE / SPECULATIVE: magnitude (1.3x - 3x). No closed-form substrate-specific number in literature; this is calibrated extrapolation from sparse-Hopfield-vs-dense lift ratios.
- SPECULATIVE: that the empirically-negative tw_edge_z translates monotonically into cleanup-capacity lift. The two are mathematically linked but not in closed form for VSA decoders.

## Mathematical foundation framing

Free probability with operator-valued kernel (Speicher cyclic cumulants) IS the substrate's natural mathematical home for clustered-codebook spectrum analysis. Vanilla Marchenko-Pastur / uniform-Frady-Sommer / classical-Hopfield-0.138-N capacity are all the limits of this framework when structure is removed. The substrate's empirical observation that tw_edge_z < 0 is the literature's signature of being OUT OF the toy regime and IN the structured regime where free convolution applies. This is a substrate-product strength: the substrate operates in the mathematically richer regime, and the literature provides the tools to analyze it precisely.

## Citations (verified count)

R1: Marchenko-Pastur deformation / free probability -- 8 web results, of which 4 directly relevant (MDPI 2024 studies; arXiv 1607.05560 deformed random matrices and free probability; q-deformation arXiv 2601.09427; ResearchGate).
R1: Free cumulants / block matrix -- 9 results, 5 directly relevant (Speicher chapter; arXiv 2309.14315 structured matrices cyclic cumulants; arXiv 2410.00908 free cumulants tensors; arXiv 2303.00713 ETH free cumulants; NCBI cumulant note).
R1: Spiked covariance / BBP -- 8 results, 4 directly relevant (Annals of Stat. 1905.13060; supercritical 1907.12251; detection limits El Alaoui; ultra-high-dim 2604.26178).
R1: Hopfield clustered vs random -- 9 results, 5 directly relevant (Springer small-world capacity; arXiv 1411.4625 robust exponential; arXiv 1709.05340 dynamic capacity; arXiv 1307.8104 multilevel; arXiv 1403.3305 noise facilitation).
R1: Associative memory correlated patterns -- 8 results, 5 directly relevant (arXiv 2508.01395 feature correlations; arXiv 0707.0565 uninformative memories; Frontiers 2025 autonomous retrieval; arXiv 2304.14964 dense exponential; arXiv 2412.05501 plasticity).
R1: Random matrix deformation clustered -- 9 results, 5 directly relevant (arXiv 2505.11948 correlated spectral density hetero-associative; arXiv 2404.17573 diagonal deformation; arXiv 2202.04707 band/block correlated; arXiv 2409.11381 edge correlated entries; Springer 2016 local spectral correlated).
R2: Tracy-Widom edge correlated -- 9 results, 6 directly relevant (arXiv 1112.2381 edge universality correlation; arXiv 2201.00300 combinatorial edge; arXiv 1407.8015 deformed Wigner edge; Annals 2020 correlated band rigidity; Wikipedia; Springer 2022 convergence rate).
R2: Wishart block / generalized -- 7 results, 4 directly relevant (arXiv 1407.1282 generalized Wishart free multiplicative; nonsymmetric Wishart correlation; arXiv 1802.03451 spectral density estimation; concentration stable entries).
R2: Compressed sensing structured sparsity -- 7 results, 5 directly relevant (ScienceDirect 2025 phase transitions structured sparsity; arXiv 2411.09868 phase transitions structured; arXiv 1111.1041 minimax denoising; arXiv 1410.4593 adaptive structured; ResearchGate structured acquisition).
R2: Stochastic block model spectral gap -- 9 results, 5 directly relevant (CMU Rinaldo SBM PCA; Massoulie UCSD talk; arXiv 1506.08621 degree-corrected; PMLR Chin 2015 optimal rate; arXiv 2002.05577 uniqueness).
R2: Sparse modern Hopfield Ramsauer -- 9 results, 6 directly relevant (arXiv 2402.13725 sparse structured Hopfield Martins; OpenReview sparse modern Martins; arXiv 2411.08590 Hopfield-Fenchel-Young; arXiv 2404.03900 nonparametric modern; arXiv 2309.12673 sparse modern Hopfield model; NeurIPS 2023 sparse modern).
R2: Stieltjes free convolution correlated -- 9 results, 5 directly relevant (arXiv 1508.05905 local stability free additive; arXiv 1610.08104 Bun-Bouchaud-Potters cleaning correlation; arXiv 1510.04430 random matrices; arXiv 1807.11694 deep residual free probability; Univ Toulouse Capitaine semicircular convolution).

Total verified directly-relevant sources: 59 across 12 queries.

## Cross-thread synthesis

- Reinforces prior cap_map row on free-probability as load-bearing (Bet I 2/3 envelopes). Specifically extends from "spectrum exists" to "spectrum is operator-valued-free-convolution-computable for clustered codebooks."
- Connects directly to memory note substrate_vsa_position_is_meaning_validated: the L1 categorical clustering ratios 22x-500M+ are consistent with the spiked-covariance / BBP super-critical regime; cluster centroids are well above the BBP threshold; LIFT prediction is supported by substrate's own empirics.
- Reinforces feedback-literature-is-not-oracle: literature gives qualitative direction (LIFT under structure-aware decoder) but magnitude requires substrate empirics (Cell A + Cell B at F=3).
- Reinforces feedback-dont-dismiss-adjacent-methods: sparse-Hopfield-Ramsauer was adjacent to "exponential capacity via clustering" and the dispatch revealed the most directly substrate-relevant mathematical structure.
- Adjacency for next drill: F2 Tracy-Widom edge fluctuations on substrate W eigenvalues (advisor rank #5; field free-probability; substrate-tw_edge_z anomaly diagnostic).

## Next-drill candidate

field: free-probability, drill F2 (Tracy-Widom edge on W eigenvalues) OR drill F5 (R-transform on clustered codebook spectrum). Both extend the operator-valued free-probability frame established here. Preferred: F5 R-transform, because it gives a constructive closed-form path from cluster geometry to cleanup-cliff prediction.
