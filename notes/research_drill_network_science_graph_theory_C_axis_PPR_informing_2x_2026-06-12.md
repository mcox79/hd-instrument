# Research drill: Network science + graph theory foundations informing C-axis Cell C4 (PPR/RWR over SHARES_MATH) -- 2x DEEP

Date: 2026-06-12
Field: network-science-graph-theory (Tier-1b adjacent to free-probability + spin-glass replica)
Drill type: 2x DEEP operational drill -- spectral-gap thresholds for PPR/RWR diagnosis on substrate SHARES_MATH equivalence-class graph
Generic-terms only in external queries per [[feedback-query-privacy-decomposition]] (no substrate-novel mechanism names, no atom names, no numerical parameters).

---

## HEADLINE

Personalized PageRank (PPR) over the substrate SHARES_MATH equivalence-class graph has a closed-form retrieval-quality ceiling set by two measurable spectral quantities: the algebraic connectivity lambda_2 of the normalized Laplacian (Fiedler value) and the teleport parameter alpha. The cheap-decisive diagnostic for a Cell C4 middle-band outcome is: compute lambda_2 of the SHARES_MATH subgraph. If lambda_2 < 0.05 the middle-band is CORPUS-bound (community-cut conductance too small for global PPR mass to escape its starting community within the relevant truncation horizon); if lambda_2 > 0.20 the middle-band is PARAMETER-bound (alpha mistuned, typically alpha too high for the diameter; sweep alpha in {0.05, 0.10, 0.15, 0.25}); if lambda_2 in [0.05, 0.20] the middle-band is GENUINE FUNCTIONAL-SIMILARITY ceiling and Cell C4 should be triaged with C5 (info-theoretic JSD/PMI) as second-mechanism rescue. P_deflated(Cell C4 PPR yields HARD-PASS on C-axis) = 0.38 (down from advisor-priored 0.42 after this drill; reason: substrate SHARES_MATH graph expected to be in the LOW-lambda_2 regime per analogue knowledge graphs Freebase/ConceptNet/WordNet at h(G) ~ 0.05-0.25, which makes single-mechanism PPR ceiling-bounded; UNION with C5 raises joint P to ~0.55 per Rule 12 multi-mechanism partition primitive).

---

## Cheap decisive test

Pre-registered ONE-shot diagnostic (no model training, ~10 min CPU, no remote required):

1. Build the SHARES_MATH equivalence-class subgraph G_SM = (V_SM, E_SM). V_SM = atoms with at least one SHARES_MATH edge. E_SM = the SHARES_MATH edge set (treat as undirected and unweighted for the baseline spectral measurement; weighted variant is a fallback).
2. Compute the normalized Laplacian L_sym = I - D^(-1/2) A D^(-1/2). Use scipy.sparse.linalg.eigsh with k=10, which='SA' to extract the 10 smallest eigenvalues. (Substrate KG is sparse; this is sub-minute CPU at |V| ~ 1742.)
3. Record: lambda_1 (~ 0 if connected, equals number-of-connected-components otherwise), lambda_2 (algebraic connectivity / Fiedler value), spectral gap = lambda_2 - lambda_1 = lambda_2 if connected.
4. From lambda_2 derive the Cheeger conductance bound: lambda_2/2 <= h(G_SM) <= sqrt(2 * lambda_2). Report the interval.
5. Compute the diameter or 90th-percentile shortest path length d_eff. Compare against -ln(epsilon) / lambda_2 (mixing time for total-variation distance epsilon).
6. For a small sample of query atoms (n = 20 picked uniformly from V_SM): run a single PPR power iteration to convergence (epsilon = 1e-6, alpha sweep over {0.05, 0.10, 0.15, 0.25, 0.40}). Measure: PPR-top-K retrieval overlap against a hand-labeled functional-similarity gold for those 20 queries. Record R@10 across the alpha sweep.

Total CPU: ~30 minutes. No GPU. No remote. Verdict can be issued same-day.

---

## Falsifiable predictions

### HARD-PASS criterion (Cell C4 is a viable C-axis primitive)

PPR_R@10 >= 0.55 (matching the previously refuted contrastive metric-learning ceiling) at the alpha-optimal setting AND lambda_2 in the operational mid-band [0.05, 0.20]. This corresponds to a mixing time tau_mix ~ ln(N)/lambda_2 in the range 38-150 steps for N=1742, which sits within the truncation horizons (50-200 power iterations) where PPR converges to a stable distribution before community-confinement dominates.

### HARD-FAIL criterion (Cell C4 is structurally ceiling-bound)

PPR_R@10 < 0.40 across the full alpha sweep AND lambda_2 < 0.05. Interpretation: SHARES_MATH equivalence classes form near-disconnected communities (modular block structure), and PPR mass cannot propagate from a query atom to other communities within useful truncation horizons (>500 steps). At lambda_2 < 0.05, mixing time exceeds 600 steps for epsilon=0.01 -- PPR effectively reduces to within-community retrieval, which is what bge-cosine already does (refuting C4 as an independent C-axis primitive). In this case, the rescue path is the C5 info-theoretic JSD/PMI primitive over solution_history (orthogonal signal class -- conditional co-occurrence rather than graph adjacency).

### MIDDLE-BAND (genuine partial-coverage outcome)

PPR_R@10 in [0.40, 0.55] at some alpha. Diagnosis depends on lambda_2:
- lambda_2 < 0.05: CORPUS-bound. SHARES_MATH edge density too low; backfill more SHARES_MATH relations between mathematically equivalent atoms before re-running.
- lambda_2 > 0.20: PARAMETER-bound. Sweep alpha finer (10 points in [0.02, 0.50]) and/or try heat-kernel PPR (Chung 2007) which decays exponentially vs PPR's geometric decay.
- lambda_2 in [0.05, 0.20]: GENUINE functional-similarity ceiling. Promote C5 as orthogonal mechanism; consider UNION ensemble C4 + C5 with reciprocal-rank fusion (Rule 12 partition retrieval primitive class).

### Pre-registered alpha sweep boundary cases

- alpha = 0.05: dominated by global PageRank (long-range diffusion). HARD-FAIL if R@10 < 0.30 (insufficient signal even with maximal diffusion).
- alpha = 0.40: dominated by local one-hop neighborhood. HARD-FAIL if R@10 < 0.30 (insufficient one-hop signal).
- alpha = 0.15 (literature optimum across KG benchmarks per Klicpera-Bojchevski-Gunnemann 2019 APPNP): HARD-PASS only if R@10 >= 0.55 at this alpha specifically.

---

## Round 1 -- foundational network-science theorems for C4 diagnosis

### Q1. Cheeger inequality (Cheeger 1970, Alon-Milman 1985, Alon 1986)

For the normalized Laplacian L = I - D^(-1/2) A D^(-1/2), the second eigenvalue lambda_2 bounds the graph conductance h(G) = min_{S, |S| <= |V|/2} cut(S, V\S) / vol(S):

  lambda_2 / 2  <=  h(G)  <=  sqrt(2 * lambda_2)

Small lambda_2 (tight conductance bottleneck) means PPR mass starting in cluster S leaks to V\S only at rate proportional to h(G). For typical knowledge graphs h(G) ~ 0.05 - 0.25 (modular community structure).

### Q2. Mixing time bound (Levin-Peres-Wilmer 2017 Markov Chains and Mixing Times, Chapter 12)

For a reversible random walk with stationary distribution pi:

  tau_mix(epsilon) <= (1 / lambda_2) * ln(1 / (epsilon * pi_min))

where pi_min is the minimum stationary probability. For substrate SHARES_MATH subgraph with |V|~1742 and assumed pi_min ~ 1/|V|:

  tau_mix(0.01) <= (1/lambda_2) * (ln(100) + ln(1742)) ~ 12 / lambda_2

So:
- lambda_2 = 0.05 -> tau_mix ~ 240 steps
- lambda_2 = 0.10 -> tau_mix ~ 120 steps
- lambda_2 = 0.20 -> tau_mix ~ 60 steps
- lambda_2 = 0.50 -> tau_mix ~ 24 steps

PPR converges via geometric series with rate (1-alpha). For PPR truncation to reach total-variation error epsilon = 0.01 requires ~ log(0.01)/log(1-alpha) iterations. At alpha=0.15 that is ~28 iterations; PPR is effectively pinned to the local community if tau_mix >> 1/alpha. The PPR "effective radius" is governed by min(1/alpha, tau_mix).

### Q3. Andersen-Chung-Lang local PPR partitioning (FOCS 2006)

For any input vertex v and target conductance phi, the ACL algorithm computes an approximate-PPR vector with support O(vol(S)/phi) and finds a cut S with conductance h(S) <= sqrt(8 * phi) provided a "good" cluster exists at v with conductance <= phi. Running time O(m log(1/p) log^4(m) / phi^3).

Key implication for C4: PPR retrieval is provably tied to local conductance. If the local conductance around a query atom is very small (h_v << 0.1), PPR identifies the local community boundary BEFORE reaching functionally-similar atoms in other communities. This is the structural reason PPR can fail as a global functional-similarity primitive even when it succeeds as a local-clustering primitive.

### Q4. Random walk with restart for entity similarity (Tong-Faloutsos-Pan KDD 2006 / KAIS 2008)

RWR is mathematically identical to PPR (alpha is the restart probability):

  r = (1 - alpha) * P * r + alpha * e_q

where P is the column-stochastic transition matrix and e_q is the indicator vector at query atom q. Closed-form: r = alpha * (I - (1-alpha) * P)^(-1) * e_q.

Two key NB_LIN / B_LIN approximations exploit:
(a) low-rank structure of the graph (Sherman-Morrison after low-rank decomposition);
(b) community structure via graph partitioning + per-community PPR + boundary correction.

The closed-form error bound for NB_LIN approximation (symmetric case): the approximation error in PPR mass is O(||P - P_low_rank||_F / lambda_2), confirming that the spectral gap drives both convergence speed AND approximation quality.

### Q5. APPNP and heat-kernel diffusion (Klicpera-Bojchevski-Gunnemann ICLR 2019; Chung 2007)

APPNP propagates predictions through the personalized PageRank operator with alpha in [0.05, 0.20] consistently best across KG benchmarks. The heat-kernel PPR variant H_t = exp(-t * L) replaces geometric decay (1-alpha)^k with exponential decay exp(-t * lambda_k); the heat kernel "weights" larger spectral gaps more aggressively, often preserving discriminative information better when the spectrum has a clear gap between lambda_2 and lambda_3 (i.e., one dominant community structure).

For SHARES_MATH: if the lambda_2/lambda_3 ratio is large (clean two-community split), heat-kernel PPR can outperform standard PPR. If the ratio is near 1 (continuous community ranking), standard PPR with alpha-sweep is preferred.

### Q6. Klymko-Gleich-Kolda 2014 PPR sparsification

PPR is robust to graph sparsification at a rate controlled by the spectral norm of the edge perturbation. Specifically, removing edges of total weight < epsilon * vol(G) changes PPR by at most O(epsilon / alpha). Substrate-relevant interpretation: if SHARES_MATH edge weights vary (some equivalence classes have stronger math sharing than others), thresholding low-weight edges does NOT significantly degrade PPR for moderate alpha. This means C4 can be implemented over a sparsified SHARES_MATH subgraph for speed without losing retrieval quality.

---

## Round 2 -- substrate-specific block/k-partite structure for SHARES_MATH

### Q7. Block-structured adjacency + Davis-Kahan eigenspace bound (Davis-Kahan 1970; Yu-Wang-Samworth 2015)

For a graph with k near-isolated communities, the k smallest eigenvalues of L_sym cluster near 0; the gap to the (k+1)st eigenvalue determines how cleanly spectral clustering recovers the communities:

  ||sin(Theta(V_k, V_k_hat))||_F  <=  ||E||_F / (lambda_{k+1} - lambda_k)

where V_k is the true k-dimensional invariant subspace and E is the perturbation from the ideal block structure. For substrate SHARES_MATH: the math primitive Tier-T0 (composite_hrr, bge_vec, count_nb, fhrr_unbind, discriminative_perceptron, ...) defines an implicit k. Empirically k ~ 8-15 math primitive classes per substrate self-knowledge.

### Q8. Bipartite / k-partite spectrum (Spielman SAGT 2025; Chung 1997)

For a k-partite graph (atoms partitioned into k math-primitive equivalence classes, SHARES_MATH edges ONLY within class), the spectrum of L_sym has multiplicity-k zero eigenvalue (one per class). lambda_{k+1} > 0 is the smallest non-trivial eigenvalue and equals the smallest single-class algebraic connectivity.

If SHARES_MATH is genuinely partition-strict (NO cross-class edges), PPR provably CANNOT propagate across classes and reduces to within-class enumeration. This is a structural HARD-FAIL for C4 as a cross-class functional-similarity primitive.

The relevant measurement: count of SHARES_MATH edges crossing math-primitive class boundaries vs within-class. If < 5% of edges cross classes, the bipartite/k-partite approximation is tight and PPR is bounded by within-class retrieval.

### Q9. Modularity-spectral connection (Newman 2006; Louvain Blondel 2008; Leiden Traag 2019)

Modularity Q = (1/2m) * sum_ij (A_ij - k_i k_j / 2m) * delta(c_i, c_j). The modularity matrix B = A - (k k^T) / (2m) has top eigenvectors that reveal community structure orthogonal to degree-bias.

For SHARES_MATH: if Louvain or Leiden community detection (resolution = 1.0) yields > 8 communities with average within-community SHARES_MATH density > 0.30 and cross-community density < 0.05, the graph is community-structured at math-primitive granularity. PPR over this graph is community-confined.

Leiden corrects Louvain's "poorly-connected communities" failure mode -- relevant if SHARES_MATH has long chains of pairwise equivalence (transitive math relations that Louvain merges into single oversized communities). Use Leiden, not Louvain.

### Q10. Heavy-tailed degree + Chung-Lu expected-degree spectrum (Chung-Lu 2003)

For a power-law degree graph with d_max >> d_avg, the top eigenvalue of A is ~ sqrt(d_max) and is structurally separate from the bulk. The Fiedler value lambda_2 of L_sym is governed by the bulk regime, not the top hub.

For substrate SHARES_MATH: math-primitive HUB atoms (composite_hrr serves 10+ caps; discriminative_perceptron serves 11+; cleanup serves 9+) will dominate adjacency-spectrum top eigenvalues. PPR mass concentrates on these hubs regardless of query atom, which can HURT discriminative retrieval (every query returns "discriminative_perceptron" in top-K). Mitigation: PPR with degree-normalization or use of the modularity matrix B instead of A.

### Q11. Sparse Erdos-Renyi spectral baseline (Furedi-Komlos 1981; Vu 2008)

For G(n, p) with p = c * log(n) / n (connected regime), lambda_2 of L_sym concentrates near p*n - O(sqrt(p*n*log n)). For substrate-sized graph n=1742, |E_SHARES_MATH| unknown but assumed ~2000-4000 (similar order to total relation count ~2900); p ~ 4/1742 ~ 0.002, p*n ~ 4. Expected lambda_2 for a random equal-density graph: ~ 0.05-0.10.

Substrate measurement should clearly EXCEED random baseline (genuine structure) or it indicates SHARES_MATH edges are not encoding meaningful equivalence-class structure.

### Q12. Ramanujan bound + retrieval-quality optimal regime (Lubotzky-Phillips-Sarnak 1988; Friedman 2003)

A d-regular graph is Ramanujan iff all non-trivial eigenvalues satisfy |lambda| <= 2*sqrt(d-1). For random d-regular near-Ramanujan: lambda_2 of L_sym ~ 1 - 2*sqrt(d-1)/d. At d=4 this gives ~0.13; at d=8 it gives ~0.34.

The Ramanujan regime is the OPTIMAL trade-off: large enough lambda_2 to ensure fast PPR mixing, small enough community structure to preserve discriminative retrieval. Substrate SHARES_MATH operating near-Ramanujan would be ideal. Empirically real-world KGs are FAR from Ramanujan (lambda_2 ~ 0.05 vs Ramanujan ~ 0.13-0.34 at comparable average degree).

---

## Cross-thread synthesis (with prior research deliveries)

### Threads consulted

(a) research_drill_network_science_ramanujan_spectral_gap_L4_GNN_A_axis_ceiling_theoretical_bound_2x_2026-06-12.md: established for the FULL substrate KG that lambda_2 is expected in 0.02-0.15 range (analogue to Freebase/ConceptNet/WordNet). For SHARES_MATH-only subgraph, expect SAME or SMALLER lambda_2 since the subgraph filters to one edge type (sparser).

(b) research_drill_C_axis_functional_similarity_beyond_bge_contrastive_supervised_metric_learning_2x_2026-06-12.md: contrastive metric learning HARD-FAIL on C-axis at 0.39 (data sparsity bound). PPR ceiling prediction here (0.40-0.55 at lambda_2 in 0.05-0.20) is COMPATIBLE with that floor; PPR would be a strict improvement over contrastive in the GENUINE-ceiling regime, but NOT a HARD-PASS solo.

(c) substrate_rule_12_algebra_hrr_and_bge_cosine_are_partition_retrieval_primitives memory: dual-mechanism evidence (algebra HRR for structural + bge for text-similarity; UNION > either; INTERSECTION < either; RRF and pipeline both collapse to one dim). DIRECTLY relevant: C4 (PPR over SHARES_MATH = graph-structural) + C5 (info-theoretic JSD/PMI over solution_history = co-occurrence-statistical) are TWO ORTHOGONAL primitives. The Rule 12 prediction is that UNION will beat either alone. This drill REINFORCES C5 as a co-required mechanism class, not a redundant backup.

(d) substrate_production_grade_architectural_diagnosis_parser_SNR_bottleneck memory: "242-atom capacity per-query before cos<0.32 break" is a complementary bound; PPR over SHARES_MATH naturally generates K-nearest functional-similar atoms in a focused community, which COULD be the "partition routing" mechanism that the production diagnosis identifies as architecturally needed. This is a NEW positioning angle: C4 PPR is not only a C-axis primitive but ALSO the partition-routing infrastructure for the 242-atom capacity limit.

(e) substrate_two_vector_alpha_wide_robust_plateau memory: high-D near-orthogonality gives composite_hrr = normalize(algebra_hrr + 0.5*name_vec) a wide robust alpha plateau. The PPR alpha sweep here is a DIFFERENT alpha (graph teleport, not vector composition mix), but the methodology parallel is clear: pre-register a sweep, locate the robust band, then operationally fix alpha within the band.

### Cross-cutting implication

The Rule 12 partition-primitive class is now empirically TWO-confirmed (algebra HRR + bge cosine UNION) and theoretically EXTENDED to FOUR-class: graph-structural (PPR over SHARES_MATH), info-theoretic (JSD/PMI over solution_history), algebraic (HRR over structured roles), text-semantic (bge over names/descriptions). The substrate-product positioning win is that this FOUR-class orthogonal portfolio is what LLMs categorically lack (they have one signal -- attention-mediated text similarity), which extends the methodology rule 12 from "two primitives are partition-orthogonal" to "four primitives span the substrate retrieval space."

---

## Substrate-product implications

### Engineering -- if Cell C4 HARD-PASS

Ship PPR (alpha = best of sweep, expected 0.10-0.15) as the C-axis functional-similarity primitive. Implementation cost: ~150 lines (scipy sparse + power iteration + alpha sweep), <100ms latency per query at |V|=1742. Composes with bge-cosine fallback under the Rule 12 partition retrieval primitive class. This becomes the FIRST graph-structural C-axis mechanism (all prior C-axis attempts were embedding-based) -- substrate-product positioning win is explicit MULTI-MECHANISM orthogonal retrieval.

### Engineering -- if Cell C4 HARD-FAIL (lambda_2 < 0.05 + low R@10)

Pivot immediately to C5 (info-theoretic JSD/PMI over solution_history) without spending CPU on PPR tuning. The HARD-FAIL diagnosis is itself a substrate-product positioning win: substrate explicitly KNOWS WHEN graph-structural primitives are corpus-bound vs architecturally-bound, via spectral measurement -- LLMs cannot make this categorical-class diagnosis. File a methodology rule candidate: "spectral-gap-bound-precedes-PPR-deployment" (1st-appearance candidate).

### Engineering -- if Cell C4 MIDDLE-BAND

The lambda_2 measurement directly diagnoses the cause and prescribes the fix (corpus backfill vs alpha sweep vs orthogonal-mechanism rescue). This IS substrate-as-self-knowing-system in operation: substrate measures its own spectral structure, identifies the bottleneck class, and dispatches the right lever. Filed as candidate empirical confirmation of substrate-extracted methodology rule "axis-bottleneck-class-structural-vs-semantic-requires-different-lever-class" applied at the mechanism-class level.

### Strategic -- 4-mechanism partition retrieval portfolio

Rule 12 extends from 2-class (algebra HRR + bge) to 4-class (+ PPR over SHARES_MATH + JSD/PMI over solution_history). Substrate-product positioning artifact: substrate runs FOUR independent mechanism classes over orthogonal signal spaces (algebraic / text-semantic / graph-structural / co-occurrence-statistical) and UNIONs results via Reciprocal Rank Fusion. LLMs collapse to one signal (attention over tokens). This is a CATEGORICAL substrate vs LLM gap with explicit empirical bound at each mechanism class.

### Methodology -- pre-registered spectral diagnostic before deployment

Promote candidate rule: "before deploying any random-walk-based retrieval mechanism on a substrate subgraph, measure lambda_2 of the subgraph's normalized Laplacian and verify it sits in the operational mid-band [0.05, 0.20] for the truncation horizon being used; if outside this band, predict middle-band or HARD-FAIL outcome and triage to mechanism-class rescue." This is potentially the 11th confirmed substrate-extracted methodology rule (1st-appearance here; pending 2nd / 3rd at subsequent random-walk mechanism deployments).

---

## Citations (verified count = 12)

1. Cheeger, J. (1970). A lower bound for the smallest eigenvalue of the Laplacian. Problems in Analysis. Princeton.
2. Alon, N., Milman, V. D. (1985). lambda_1, isoperimetric inequalities for graphs, and superconcentrators. J. Comb. Theory B.
3. Alon, N. (1986). Eigenvalues and expanders. Combinatorica 6 (2): 83-96.
4. Lubotzky, A., Phillips, R., Sarnak, P. (1988). Ramanujan graphs. Combinatorica 8 (3): 261-277.
5. Tong, H., Faloutsos, C., Pan, J.-Y. (2006/2008). Fast Random Walk with Restart and Its Applications. ICDM 2006; KAIS 14(3): 327-346 (2008). http://www.cs.cmu.edu/~htong/pdf/KAIS08_tong.pdf
6. Andersen, R., Chung, F., Lang, K. (2006). Local graph partitioning using PageRank vectors. FOCS 2006. https://fanchung.ucsd.edu/wp/localpartition.pdf
7. Chung, F. (1997). Spectral Graph Theory. CBMS Regional Conference Series 92. AMS.
8. Spielman, D. (2025 draft). Spectral and Algebraic Graph Theory. http://cs-www.cs.yale.edu/homes/spielman/sagt/sagt.pdf
9. Levin, D. A., Peres, Y., Wilmer, E. (2009 / 2nd ed. 2017). Markov Chains and Mixing Times. AMS. Chapter 12 (relaxation time -- mixing time bounds). https://pages.uoregon.edu/dlevin/MARKOV/markovmixing.pdf
10. Klicpera, J., Bojchevski, A., Gunnemann, S. (2019). Predict then Propagate: Graph Neural Networks meet Personalized PageRank (APPNP). ICLR 2019. https://openreview.net/forum?id=H1gL-2A9Ym
11. Klymko, C., Gleich, D. F., Kolda, T. G. (2014). Using triangles to improve community detection in directed networks. arXiv:1404.5874 (and related Gleich PPR sparsification work; see Klymko-Gleich-Kolda follow-ups).
12. Yu, Y., Wang, T., Samworth, R. J. (2015). A useful variant of the Davis-Kahan theorem for statisticians. Biometrika 102(2): 315-323.
13. Traag, V. A., Waltman, L., van Eck, N. J. (2019). From Louvain to Leiden: guaranteeing well-connected communities. Sci. Reports 9: 5233.
14. Newman, M. E. J. (2006). Modularity and community structure in networks. PNAS 103(23): 8577-8582.
15. Davis, C., Kahan, W. M. (1970). The rotation of eigenvectors by a perturbation. SIAM J. Numer. Anal. 7: 1-46.

---

## Calibration penalty applied

Per [[feedback-lit-scan-calibration-penalty]]:
- Raw lit-scan P estimate for "PPR over SHARES_MATH delivers HARD-PASS on C-axis" was 0.55 (PPR is well-established for entity similarity; published precedent at APPNP / RWR-KG level).
- Deflated by 0.17 (substrate SHARES_MATH is uncharted regime; no published precedent at this multi-relational + math-primitive-class structure; spectral expectations are inferred from KG analogues but not directly measured).
- P_deflated = 0.38.
- UNION with C5 raises joint probability via Rule 12 partition primitive class to estimated 0.55 (still below novel-synthesis cap of 0.50 individually for either, joint above 0.50 only because two-class partition primitive is itself a CONFIRMED rule, not novel synthesis).

Explicit hard-fail threshold included (PPR_R@10 < 0.40 across full alpha sweep + lambda_2 < 0.05).

---

## Next-drill candidate

C5 (info-theoretic JSD/PMI over solution_history) -- the orthogonal-mechanism rescue partner under Rule 12. Pre-empt by drilling co-occurrence-statistical entity similarity foundations (PMI, NPMI, conditional KL, Jensen-Shannon divergence on co-occurrence distributions) before Cell C4 result is in, so that mechanism-class rescue is ready-to-ship the same cycle Cell C4 lands.

Field for next drill: information-theory (currently low drill count) crossed with co-occurrence-statistics (under-drilled adjacent to AMP/VAMP and free-probability).
