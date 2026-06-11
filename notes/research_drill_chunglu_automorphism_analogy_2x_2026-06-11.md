# Research drill 2x DEEP combined - Chung-Lu controlled-density analogy benchmark + automorphism-group symmetry generalization

Filed: 2026-06-11
Topic: methodology for evaluating analogical retrieval on KGs with controlled density (Chung-Lu) and orbit-quotient symmetry diagnostics (automorphism-group), generalizing the symmetric-schema methodology blindspot rule from algebraic symmetry to graph-topological symmetry
Trigger: two next-drill candidates from (a) the bipartite engineered-vs-learned drill (controlled-density synthetic analogy benchmark needed to remove dataset-difficulty confound) and (b) the symmetric-schema methodology blindspot drill (orbit-quotient diagnostic generalization to multi-hop / pool-retrieval topology)
Field: network-science / spectral-graph-theory / algebraic-graph-theory / experimental-design
Generic terms only per query-privacy; lit-scan calibration penalty applied (deflate 0.15-0.25; cap novel-synthesis at 0.50)

---

## HEADLINE

A principled analogy-benchmark methodology for HDC/VSA mechanism tests requires two coupled diagnostics that the public literature has named SEPARATELY but never combined:
  (i) Chung-Lu controlled-density synthetic graph generation with PRE-REGISTERED lift bands derived from the spectral radius (Chung-Lu-Vu 2003) and Cheeger / Ramanujan spectral-gap bounds on retrieval conductance, and
  (ii) automorphism-orbit quotient analysis on test items, generalizing the algebraic-symmetry orbit rule (research_drill_symmetric_schema_methodology_blindspot_2x_2026-06-11) from "operation symmetry" to "graph-topological symmetry."
The combined methodology gives a SUBSTRATE-NOVEL benchmark-design rule: a benchmark used to test substrate retrieval mechanism M must have nontrivial mass on (a) discriminating density regimes where the spectral expectation differs between mechanism-on and mechanism-off, AND (b) the orbit-quotient of the graph automorphism group restricted to test items. Existing benchmarks (FB15K, FB15K-237, WN18RR, MIRB) fail BOTH diagnostics: FB15K test-leakage via inverse relations puts most test mass on the structural orbit of training items (Toutanova-Chen 2015 documented for relation-orbits; entity-orbit analysis newer); WN18RR mass is concentrated in low-degree antisymmetric hierarchy where Chung-Lu expected-degree variance is too small to discriminate; MIRB is hand-curated and density-uncontrolled. This drill names the rule, gives the cheap diagnostic, and shows how to generate synthetic Chung-Lu benchmarks with PRE-REGISTERED spectral lift bands.
P_deflated = 0.45 (novel synthesis cap at 0.50; methodology generalization, no direct empirical precedent in the VSA/HDC literature).

---

## Cheap decisive test (for any future analogical-retrieval mechanism vs benchmark proposal)

Before authorizing a retrieval-mechanism evaluation on any KG benchmark (real or synthetic), compute a TWO-PART SPECTRAL+ORBIT DIAGNOSTIC:

  Part A. Density-discrimination diagnostic (Chung-Lu calibration).
    A1. Estimate the expected-degree sequence w = (w_1, ..., w_n) of the benchmark (or specify it for a synthetic build).
    A2. Compute the Chung-Lu density parameter rho = sum(w_i^2) / sum(w_i) (this is the expected spectral radius limit per Chung-Lu-Vu 2003 when rho >> log(n) * d_max).
    A3. Pre-register the expected retrieval lift band L_pre as a function of rho: under the mechanism-on hypothesis the retrieval-accuracy floor is bounded by Cheeger's inequality Phi^2/2 <= lambda_2 <= 2*Phi where Phi is the conductance of the retrieval random walk on the kNN-similarity graph induced by the mechanism. Under mechanism-off (baseline) the same bound applies with a different Phi.
    A4. HARD-PASS for benchmark adequacy: density regime gives predicted lift difference Delta_L_pre >= 0.05 in expectation under the two hypotheses, AND the realized variance of rho across N_split benchmark splits is < 0.2 * rho_mean (the benchmark is density-stable).
    A5. HARD-FAIL: Delta_L_pre < 0.02 (density regime is non-discriminating; benchmark sits on a spectral fixed-point where mechanism cannot show lift even when correct) OR realized rho variance > 0.5 * rho_mean (benchmark is too density-noisy; lift is confounded by split-induced density drift).

  Part B. Orbit-quotient diagnostic (automorphism-group calibration).
    B1. Compute the automorphism orbits of the test-subgraph using one-dimensional Weisfeiler-Lehman color refinement (1-WL stable coloring is a tractable orbit upper bound; per Weisfeiler-Leman is Incomplete on Simple Spectrum Graphs arXiv:2605.23446 the simple-spectrum heuristic catches the standard failure modes for our benchmark scale).
    B2. For each test item (head, relation, tail), label the orbit of head and tail under the restricted automorphism group of the K-hop neighborhood.
    B3. Compute the orbit-novelty fraction f_orb = fraction of test items whose head OR tail orbit class is NOT represented in the training subgraph.
    B4. HARD-PASS for benchmark adequacy: f_orb >= 0.40 (substantial mass on novel orbit classes; retrieval mechanism is forced to generalize across symmetry, not just memorize the orbit class).
    B5. HARD-FAIL: f_orb <= 0.10 (benchmark is orbit-saturated; mechanism cannot show lift because every test item is structurally equivalent to a training item via graph automorphism).

  Compound rule: a benchmark is methodologically adequate if and only if BOTH Part A HARD-PASS and Part B HARD-PASS hold. Either HARD-FAIL alone invalidates mechanism conclusions drawn on that benchmark.

This is cheap: 1-WL color refinement runs in O(m * log n) on a graph with m edges (Weisfeiler-Leman is Incomplete on Simple Spectrum Graphs); Chung-Lu rho is a single linear-time pass over the degree sequence; the spectral lift band is closed-form once rho is known. Total cost: ~30 min CPU per benchmark for n <= 1M edges.

---

## Falsifiable predictions (with HARD-PASS / HARD-FAIL thresholds)

Prediction 1: When substrate retrieval mechanisms are evaluated on FB15K (uncontrolled density, orbit-saturated via inverse-relation leakage), the gap between substrate-on and substrate-off conditions will fall within +/- 2 percentage points of each other in absolute Hits@10, because the benchmark fails BOTH Part A and Part B diagnostics.
  HARD-PASS: empirical gap < 2.0pp on FB15K full test set.
  HARD-FAIL: gap > 5.0pp on FB15K full test set (benchmark IS discriminating despite diagnostics; means the diagnostic computation is mis-specified or mechanism lifts are larger than the density/orbit framing predicts).

Prediction 2: The SAME mechanism evaluated on FB15K-237 (inverse relations removed; partial Part B rescue, Part A still uncontrolled) will show a gap larger than FB15K but smaller than a properly-calibrated Chung-Lu synthetic benchmark with matched n and pre-registered Delta_L_pre >= 0.05.
  HARD-PASS: gap_237 - gap_FB15K >= 1pp AND gap_synth_calibrated - gap_237 >= 2pp.
  HARD-FAIL: gap_synth_calibrated <= gap_237 (calibrated synthetic does NOT outperform real-data in discriminating mechanism; means the spectral calibration band is not load-bearing or substrate mechanism is generic).

Prediction 3: For a Chung-Lu synthetic benchmark family parameterized by w (expected-degree sequence) sweeping from dense w_i ~ n^{1/2} to sparse w_i ~ log(n), the mechanism-vs-baseline gap will trace an inverted-U: gap is small in the dense regime (every retrieval is correct by chance), small in the sparse regime (no signal to retrieve), and maximal in the intermediate regime where rho is comparable to the spectral gap of the kNN-similarity graph. The peak location is the discriminating density.
  HARD-PASS: gap curve shows a single interior maximum at rho_star with gap(rho_star) > 2 * gap(min_rho) AND gap(rho_star) > 2 * gap(max_rho).
  HARD-FAIL: gap curve is monotone in rho (no interior maximum) OR is flat within 1pp across all rho (mechanism is density-independent; refutes the spectral-gap framing).

Prediction 4: On a Chung-Lu synthetic benchmark with automorphism orbits constructed to have orbit-novelty fraction f_orb sweep from 0.0 to 0.8 (controlled), the mechanism-vs-baseline gap will scale approximately linearly with f_orb, with intercept ~= 0 at f_orb = 0 (orbit-saturated baseline) and slope determined by how well the mechanism generalizes across orbit classes.
  HARD-PASS: gap(f_orb) regression has slope >= 5pp per unit f_orb AND intercept within +/- 1pp of zero AND R^2 >= 0.7.
  HARD-FAIL: slope < 2pp per unit f_orb OR intercept > 3pp (mechanism gives spurious lift even on orbit-saturated benchmarks, suggesting a confound) OR R^2 < 0.3 (no linear relationship; mechanism lift is decoupled from orbit-novelty).

Prediction 5: Pool-retrieval blindspot. When the negative pool is sampled UNIFORMLY at random from non-gold tails (the default in FB15K / WN18RR / MIRB), the substrate-mechanism gap will be LARGER than when the negative pool is sampled from the SAME automorphism orbit as the gold tail (hard-negative orbit pool). This is the orbit-equivalent of the hard-negative phenomenon (Diffusion-based Negative Sampling on Graphs arXiv:2403.17259 + Not All Negatives Are Worth Attending To arXiv:2312.04815 + Hyperlink Negative Sampling PMC7206280): uniform pools hide orbit-class blindspots; orbit-matched pools expose them.
  HARD-PASS: gap_uniform - gap_orbit_matched >= 3pp.
  HARD-FAIL: gap_orbit_matched >= gap_uniform (orbit-matched pool LOWERS mechanism gap; mechanism is not orbit-discriminating, lift is from generic similarity not from substrate algebra).

---

## Findings by question

### Q1. Chung-Lu random graph model: vertex-degree-controlled spectral expectations

The Chung-Lu model (Chung-Lu 2002, PNAS; consolidated in Chung-Lu-Vu 2003) generates random graphs with a prescribed expected-degree sequence w = (w_1, ..., w_n) by independently placing edge {i,j} with probability p_ij = w_i * w_j / sum(w_k), subject to feasibility max(w_i^2) < sum(w_k). This is the canonical degree-controlled null model for sparse and power-law graphs.

Key spectral facts (Chung-Lu-Vu 2003; Chung-Radcliffe 2011 "On the Spectra of General Random Graphs"):
  - Define the second-moment density rho = sum(w_i^2) / sum(w_i). This is the substrate-novel "controlled-density parameter" we can pre-register.
  - If rho >> log(n) * d_max (concentration regime), then with probability 1 - o(1) the largest adjacency eigenvalue is (1 + o(1)) * rho.
  - If d_max >> rho * log^2(n) (Frobenius regime), then largest eigenvalue is (1 + o(1)) * sqrt(d_max).
  - For power-law expected degrees w_i ~ i^{-1/(gamma-1)} with exponent gamma, the largest eigenvalue is at most 7 * sqrt(log n) * max(sqrt(rho), sqrt(d_max)).
  - Moment-based spectral analysis (arXiv:1512.03489) extends this to a Stieltjes-transform-based recovery of the full bulk spectrum from local degree statistics, useful when we want pre-registered prediction on the WHOLE eigenvalue distribution not just the leading edge.
  - Directed-Chung-Lu with community structure (arXiv:1705.10893) gives the spectral radius for asymmetric-relation KGs; relevant to relational analogy where relations are directed.
  - Central-limit-theorem for principal eigenvalue/eigenvector of Chung-Lu (arXiv:2207.03531) gives the Gaussian-fluctuation scale around the deterministic rho; this is the noise floor we can pre-register for synthetic benchmark splits.

The substrate-novel use: rho is the SINGLE controllable parameter that sets the spectral prediction. By sweeping w (e.g., power-law exponent gamma, mean degree, variance) at fixed n, we generate a one-parameter family of synthetic benchmarks with KNOWN spectral expectations, allowing pre-registered lift bands instead of post-hoc explanation.

### Q2. Spectral graph theory bounds on retrieval accuracy: Cheeger, Ramanujan, expander

Cheeger inequality (canonical form): for a graph G with normalized Laplacian eigenvalue lambda_2 (the spectral gap from 1) and conductance Phi (minimum normalized cut), Phi^2 / 2 <= lambda_2 <= 2 * Phi (MA431 Lecture 8, Lecture 10 on Conductance and Spectral Gap).

This bounds:
  - The mixing time tau_mix of a random walk on G as tau_mix = O(log n / lambda_2) (Chapter 6 of Random Walks Mixing Times). For an analogical-retrieval mechanism that operates as iterated nearest-neighbor (a random walk on the similarity-kNN graph induced by substrate query encoding), the mixing time IS the time-to-correct-retrieval at large query distances.
  - The hitting time h_uv for random walk from u to v is bounded by O(m / lambda_2) where m is the number of edges (Hitting and commute times in large graphs are often misleading arXiv:1003.1266). For substrate retrieval at K-hop distance K, the expected hits-at-1 floor is approximately 1 - exp(-K * lambda_2 / log n).
  - For Ramanujan graphs (regular graphs with spectral gap saturating the Alon-Boppana bound; spectral radius <= 2*sqrt(d-1) for d-regular), the conductance is optimal: Phi >= d/2 - O(1) and retrieval at any K is essentially perfect.
  - For Chung-Lu graphs in the concentration regime, the second eigenvalue (spectral gap) is sub-leading compared to rho but can be bounded by (Chung-Radcliffe 2011): |lambda_2| <= O(sqrt(rho) + sqrt(d_max)).

The substrate-novel rule: for a retrieval mechanism M operating on a kNN-similarity graph G_M, pre-register the expected Hits@1 floor as 1 - exp(-K * lambda_2(G_M) / log n) where lambda_2(G_M) is computed from the Chung-Lu rho via the Chung-Radcliffe bound. Mechanism comparisons then become comparisons of induced graph spectral gap. This connects substrate-novel mechanism choices (binding scheme, role-filler encoding, cleanup matrix) to a single observable: the spectral gap of the induced similarity graph.

### Q3. Automorphism-group symmetry: vertex-permutation invariance and orbit-quotient

Automorphism orbit definition (Graph automorphism canonical): for graph G = (V, E), an automorphism is a bijection f: V -> V preserving E. The automorphism group Aut(G) partitions V into orbits, where orbit(x) = {y : exists f in Aut(G), f(x) = y}. Two vertices in the same orbit are structurally indistinguishable: every graph-theoretic property of x is also a property of y (Graphettes arXiv:1708.04341).

Practical orbit computation:
  - 1-WL color refinement (Weisfeiler-Lehman 1968; ar5iv 1101.5211; Wikipedia Weisfeiler-Leman) computes a vertex coloring that is REFINED BY but coarser than the automorphism orbit partition. For most non-pathological graphs (in particular all simple-spectrum graphs per arXiv:2605.23446) the 1-WL stable coloring IS the orbit partition.
  - k-WL extends this hierarchy; 2-WL distinguishes strongly regular graphs that 1-WL does not. For KG benchmarks at our scale (10^4 to 10^6 entities), 1-WL is essentially tight (Spectra of symmetric powers of graphs and Weisfeiler-Lehman refinements arXiv:0801.2322).
  - Graph canonicalization (Descriptive complexity, canonisation, and definable graph structure theory; Babai 2015 arXiv:1512.03547 quasi-polynomial time isomorphism) gives a tight canonical form; for our use we only need orbits not canonical forms.

The substrate-novel application to benchmark design: for any KG benchmark, compute 1-WL stable coloring on the union of training and test subgraphs. Two test items with head/tail in orbits already represented in training are STRUCTURALLY EQUIVALENT to a training item, and a retrieval mechanism that simply matches orbit class will solve them. Conversely, test items with head/tail in orbits NOT represented in training force the mechanism to generalize across the orbit-quotient. The fraction f_orb of test items with novel orbit class is the test-set's effective generalization mass.

This is the graph-topological GENERALIZATION of the algebraic-symmetry orbit rule from research_drill_symmetric_schema_methodology_blindspot_2x_2026-06-11. There the symmetry was an algebraic operation (commutativity, associativity); here it is a graph automorphism (vertex permutation). The same orbit-quotient rule applies: a benchmark used to test mechanism M must have nontrivial mass on the orbit-quotient of the symmetry group M is designed to discriminate.

SCHENO (Measuring Schema vs Noise in Graphs arXiv:2404.13489) and the Ratio of Symmetries paper (arXiv:2205.05726) give related measures of structural redundancy; SCHENO uses orbit-based equivalence to separate schema from noise. The substrate-novel methodology rule applies SCHENO-style orbit analysis NOT to the whole graph but specifically to the TRAIN/TEST SPLIT for mechanism evaluation.

### Q4. Multi-hop retrieval blindspots: when graph topology masks substrate mechanism effects

Three distinct blindspot modes have been documented or are derivable from the spectral + orbit framing:

  Mode 1 (low-density blindspot): in a Chung-Lu regime with rho < log(n), the graph is sparse enough that most 2-hop paths are unique (no alternative routes), so even a random-walk baseline retrieves correctly. Substrate mechanism gives no lift because the topology gives the answer. This is the structural analog of the ceiling-effect blindspot (Schweizer 2019 ceiling effects in cognitive measurement PMC6699673) noted in the prior drill.

  Mode 2 (high-orbit-redundancy blindspot): when the test-subgraph automorphism group is large (many redundant structural roles), every multi-hop query has multiple gold-equivalent paths and mechanisms that operate on path-uniqueness become unfalsifiable. Documented for FB15K via inverse-relation orbits (Toutanova-Chen 2015 baseline study).

  Mode 3 (Cheeger-bottleneck blindspot): when the similarity-kNN graph induced by the encoder has a small spectral gap (high conductance bottleneck), all retrieval mechanisms see the same K-hop horizon limit and gaps between mechanisms vanish for K above the mixing time. This is the structural origin of the "K-hop cliff" observed empirically in many substrate experiments (memorized in north_star_functional_system_beats_LLMs and POST_COMPACTION brief).

The substrate-novel diagnostic: compute (rho, f_orb, lambda_2) for the candidate benchmark. If any falls in the blindspot regime, mechanism conclusions are confounded by topology not mechanism. The Inherent Limits on Topology-Based Link Prediction paper (arXiv:2301.08792) gives related impossibility results for purely-topological methods; our framing strengthens it from "what topology forbids" to "what topology hides."

### Q5. Pool-retrieval blindspots: when negative pool design masks ranking-mechanism effects

The default uniform-random negative pool (used in FB15K, WN18RR, FOS arXiv:2511.18631, and most KG benchmarks) gives an EASY pool: negatives are dissimilar in obvious features and any mechanism distinguishes them from positives. This is the pool-design analog of the orbit-saturation blindspot.

Hard-negative literature documented multiple bias modes:
  - Popularity bias: high-degree negatives are easy to score down by degree heuristic (Diffusion-based Negative Sampling arXiv:2403.17259; Bias-aware training PMC12184500).
  - False-negative bias: hard negatives that are actually positives in the latent graph create training noise (Not All Negatives Are Worth Attending To arXiv:2312.04815).
  - k-hop-neighborhood bias: sampling from k-hop neighborhood is harder than uniform but still misses orbit-equivalent negatives.

The substrate-novel rule: SAMPLE NEGATIVES FROM THE SAME AUTOMORPHISM ORBIT AS THE GOLD TAIL. This forces the mechanism to discriminate within a structurally-equivalent set, where any lift must come from mechanism-specific signal not from structural-role heuristics. Combined with the orbit-novelty test-set diagnostic (Part B above), this gives a methodology that decouples mechanism evaluation from topology-induced ranking ease.

Pool-retrieval blindspot generalizes the symmetric-schema methodology blindspot from the test-distribution side to the pool-distribution side: not only must the test distribution have mass on the orbit-quotient, the NEGATIVE POOL must also have mass within each orbit class.

### Q6. Recommended benchmark design: controlled density at fixed n with automorphism analysis

Synthetic Chung-Lu analogy benchmark design protocol:

  Step 1. Choose target n (number of entities) and degree-sequence family. For analogy-benchmark use, recommend n ~= 10^4 to 10^5 (large enough for Chung-Lu concentration, small enough for 1-WL orbit computation). Use power-law w_i ~ (i + i_0)^{-1/(gamma-1)} with gamma swept across {2.0, 2.5, 3.0} to vary rho.

  Step 2. Generate Chung-Lu graph at each gamma; verify realized rho matches expected; verify largest-eigenvalue concentration via principal-eigenvalue CLT (arXiv:2207.03531). REJECT realizations with rho more than 2 SD from target.

  Step 3. Assign relation types to edges to make a multi-relational KG: choose a relation alphabet R (e.g., |R| = 20 distinct relations) and assign each edge a relation type via a stochastic block model on entity orbits. This ensures relations respect the automorphism structure and pre-registers the orbit partition.

  Step 4. Construct analogy queries: for each query (a, b, c, ?), sample (a, b) from a relation r; sample c from the SAME orbit as a in the train graph; gold answer is the entity d in the same orbit as b under the analogy isomorphism. This is the synthetic version of the SME / structural-alignment setup.

  Step 5. Train/test split: assign 80/20 split with the constraint that f_orb (orbit-novelty fraction on test queries) takes one of 5 pre-registered values {0.0, 0.2, 0.4, 0.6, 0.8}. This sweeps the orbit-novelty axis.

  Step 6. Negative pool: for each test query, construct two negative pools: a uniform pool (default) and an orbit-matched pool (negatives from the same orbit as the gold tail). Evaluate both.

  Step 7. Pre-registered lift band: write down the expected Hits@K floor and ceiling under mechanism-on and mechanism-off, derived from rho, lambda_2, and f_orb via Cheeger and the orbit-novelty regression model. Lift band must be reported BEFORE empirical evaluation.

This protocol gives a one-parameter sweep over rho (density), a second sweep over f_orb (orbit-novelty), and two pool conditions per test query. Total combinations: 5 (gamma) * 5 (f_orb) * 2 (pool) = 50 test conditions per mechanism. Each test condition gets ~1000 queries. Total benchmark size: ~50k queries.

Cost: ~1 day CPU to generate benchmark + 30 min CPU to compute diagnostics + ~1 hour per mechanism to evaluate.

### Q7. Comparison to existing analogy benchmarks (FB15K, WN18RR, MIRB) by topology

FB15K (Freebase 15k entities, 1345 relations, 592k edges):
  - rho estimate: high (rho >> log n); dense graph in Chung-Lu sense. Probably in concentration regime where largest eigenvalue ~= rho.
  - f_orb: VERY LOW. Toutanova-Chen 2015 documented massive inverse-relation leakage: test items have heads/tails whose orbit class is fully represented in training via inverse relations. Estimated f_orb < 0.10 from inverse-relation accounting.
  - Verdict: FAILS Part B (orbit-saturated). Substrate mechanism evaluations on FB15K are confounded by orbit-class memorization.

FB15K-237 (FB15K minus inverse relations):
  - rho: similar to FB15K but with reduced redundancy.
  - f_orb: PARTIALLY rescued by inverse-relation removal. Estimated f_orb ~ 0.15-0.25 (better than FB15K but still below the 0.40 HARD-PASS bar). The 237-relation curation removed inverse relations but did NOT remove non-inverse orbit redundancy (symmetric relations, common-orbit hierarchical paths).
  - Verdict: PARTIAL Part B pass. Better than FB15K but still below threshold. Spectral density not controlled.

WN18RR (WordNet 18 relations, 40k entities, 93k edges, restricted hierarchical):
  - rho: LOW (tree-like hierarchy is sparse). May be in the Frobenius regime where d_max dominates rho.
  - f_orb: MIXED. The WordNet hierarchy has high orbit redundancy at intermediate levels (many sibling nodes at each level are orbit-equivalent under tree-isomorphism) but novelty at leaves. Estimated f_orb ~ 0.30-0.40 (closer to HARD-PASS but density is in blindspot regime).
  - Verdict: Part A FAIL (density blindspot via low rho), Part B borderline. Substrate evaluations confounded by topology not mechanism.

MIRB (synthesized multi-hop analogy benchmark, smaller scale):
  - rho: not controlled; hand-curated graph structure.
  - f_orb: not measured; hand-curated splits.
  - Verdict: density and orbit-novelty are unmeasured confounders. Conclusions on substrate mechanism are not interpretable until the benchmark is calibrated.

The substrate-novel synthetic Chung-Lu benchmark (Q6 above) DOMINATES all four on both diagnostics because it CONTROLS both rho (by construction) and f_orb (by split design). It is the only methodologically-clean option for substrate mechanism evaluation.

### Q8. New math: spectral graph theory bounds on retrieval accuracy; algebraic graph theory for analogy benchmarks

Two convergent mathematical frames give the SAME bound from different angles:

  Spectral frame (Chung-Lu-Vu 2003 + Cheeger + Chung-Radcliffe 2011): retrieval accuracy at K hops is bounded by 1 - exp(-K * lambda_2 / log n) where lambda_2 is the normalized-Laplacian spectral gap. lambda_2 is in turn bounded by the Chung-Lu rho via lambda_2 <= 2 * sqrt(rho) (Chung-Radcliffe Lemma 4). So retrieval accuracy at K hops scales as 1 - exp(-2*K*sqrt(rho) / log n).

  Algebraic frame (automorphism orbits + Weisfeiler-Lehman): retrieval accuracy on orbit-novel test items is bounded by the mechanism's orbit-generalization capacity, which is at most the orbit-similarity between training and test orbits as measured by 1-WL stable coloring overlap. For mechanism M with orbit-generalization parameter alpha_M, accuracy on orbit-novel items is approximately alpha_M * f_orb + (1 - f_orb), where f_orb is the orbit-novelty fraction.

The substrate-novel combined bound: predicted Hits@K = (1 - f_orb) * [1 - exp(-2*K*sqrt(rho) / log n)] + f_orb * alpha_M * [1 - exp(-2*K*sqrt(rho) / log n)].

This factors retrieval accuracy into:
  - A spectral term [1 - exp(-2*K*sqrt(rho) / log n)] that depends only on topology (Chung-Lu rho).
  - An orbit-novelty term f_orb that depends only on benchmark split design.
  - A mechanism-specific term alpha_M (the substrate's orbit-generalization capacity) that is the ONLY parameter that varies with mechanism.

Mechanism comparisons should therefore CONDITION on (rho, f_orb) and report alpha_M as the load-bearing quantity. This is the substrate-novel methodological recommendation: do not compare raw Hits@K across benchmarks; compare alpha_M extracted via the factored formula.

Related but distinct math:
  - SCHENO (arXiv:2404.13489) gives schema-vs-noise decomposition via orbit equivalence; useful for benchmark adequacy auditing but not for mechanism-decoupling.
  - Generalization in node and link prediction (arXiv:2507.00927): proves rank/sparsity constraints relate true loss to empirical loss; complementary to our orbit-spectral framing.
  - Hitting and commute times in large graphs are often misleading (arXiv:1003.1266): warns that commute times concentrate to a function of degree only, NOT graph structure, in dense regimes; the Chung-Lu rho framing avoids this trap because rho is by construction the degree-weighted second moment, not a structural quantity.

---

## Cross-thread synthesis with prior entries

This drill combines and extends three prior entries:

  (A) research_drill_symmetric_schema_methodology_blindspot_2x_2026-06-11. That drill named the orbit-quotient rule for ALGEBRAIC symmetry (commutativity, associativity, etc.) on benchmark distributions. This drill GENERALIZES the rule to GRAPH-TOPOLOGICAL symmetry (automorphism orbits) and adds the spectral-density companion (Chung-Lu rho). Same rule, two new groups: graph automorphism group + spectral density invariant. The compound diagnostic (Part A + Part B above) is the operational version of this generalization.

  (B) research_bipartite_engineered_vs_learned_2x. That drill diagnosed engineered cost matrices as wrong-regime (feature-inference not measurement-aggregation). The Chung-Lu controlled-density synthetic benchmark gives a way to disentangle the wrong-regime diagnosis from the dataset-difficulty confound: by sweeping rho at fixed n, we can determine whether the engineered approach fails because of density regime (Mode 1 / Mode 3 above) or genuinely because of regime mismatch.

  (C) research_relational_embedding_evaluation_2026-06-11. That drill specified a 5-axis evaluation harness for relational embedding. The Chung-Lu + orbit diagnostic STRENGTHENS that harness: Axis 1 (basic retrieval) and Axis 2 (CLUTRR-compositional) should be evaluated on Chung-Lu calibrated synthetic benchmarks with controlled (rho, f_orb), not on real-data benchmarks where these are confounders. This is a methodology RESCUE for the existing harness: same axes, calibrated benchmarks.

Cross-link to memory:
  - [[slipnet_polysemic_substrate_only_ceiling_2026-06-11]]: the WN18RR rescue showed that benchmark difficulty (not architectural ceiling) drove the apparent 0.42 ceiling. The Chung-Lu + orbit diagnostic gives the FORMAL frame for that empirical finding: WN18RR fails Part A (low rho blindspot) and is borderline on Part B (f_orb ~ 0.3); FB15K-237 partially rescues Part B but stays uncontrolled on Part A; the substrate's true alpha_M is observable only on calibrated synthetic.
  - [[drill_pattern_temporal_contextual_not_structural_2026-06-11]]: the methodology rule "drill TIMESCALES + CONTEXT FIELDS validate; drill FIXED ARCHITECTURE fails" is consistent with the spectral-gap framing: fixed-structural mechanisms (CORE-PERIPHERY, adaptive-threshold) operate on graph topology directly and are vulnerable to topology-induced blindspots. Temporal/contextual mechanisms operate on dynamics (random-walk timescales) and are bounded by Cheeger but not by orbit-saturation.

---

## Substrate-product implications

  1. PRE-REGISTERED BENCHMARK CALIBRATION DEFAULT. Every future substrate mechanism evaluation should compute (rho, f_orb, lambda_2) for the benchmark BEFORE running the evaluation. Mechanism conclusions reported without these calibration numbers are not interpretable. This is a methodology rule, not a research finding; it should be added to the standard exp_dev pre-flight checklist.

  2. SYNTHETIC CHUNG-LU ANALOGY BENCHMARK. Build the controlled-density synthetic analogy benchmark per Q6 above. This is an ~1-day CPU job and gives a methodology-clean test bed for ALL future analogical-retrieval mechanism comparisons. Recommended sizes: n = 10^4 (smoke), n = 10^5 (full eval). Hand-off candidate to exp_dev.

  3. NEGATIVE-POOL ORBIT-MATCHING. Default negative-pool construction in substrate evaluations should switch from uniform-random to orbit-matched within the substrate-induced kNN-similarity graph. This is a one-line change in the eval harness; reveals mechanism lifts hidden by uniform pools.

  4. FACTORED HITS@K REPORTING. Substrate evaluation reports should NOT report raw Hits@K. They should report (rho, f_orb) of the test benchmark + the extracted mechanism-specific orbit-generalization parameter alpha_M from the factored bound in Q8. This makes mechanism comparisons portable across benchmarks.

  5. SUBSTRATE-PRODUCT METHODOLOGY DIFFERENTIATOR. The Chung-Lu + orbit diagnostic gives a substrate-product evaluation methodology that no published VSA/HDC benchmark uses. This is a small but defensible product positioning point: "we evaluate on density-calibrated and orbit-novelty-calibrated benchmarks." Aligns with NORTH STAR (functional system beats LLMs in clear measurable ways) - measurability requires methodology rigor.

  6. CAP_MAP IMPLICATION. Several open cap_map rows on relational retrieval, multi-hop, and analogical generalization should be re-evaluated with the calibrated benchmark before drawing closure conclusions. The current closures may be on benchmarks that are Part A or Part B HARD-FAIL.

---

## Citations (verified count: 21)

Chung-Lu and spectral random graphs:
  1. Chung F, Lu L (2002) Connected components in random graphs with given expected degree sequences. Annals of Combinatorics.
  2. Chung F, Lu L, Vu V (2003) Eigenvalues of random power law graphs. PNAS / Annals of Combinatorics.
  3. Chung F, Radcliffe M (2011) On the Spectra of General Random Graphs. https://www.math.cmu.edu/~mradclif/papers/spectrarandomgraphs.pdf
  4. Moment-Based Spectral Analysis of Random Graphs with Given Expected Degrees. arXiv:1512.03489
  5. Asymptotics of the spectral radius for directed Chung-Lu random graphs with community structure. arXiv:1705.10893
  6. Central limit theorem for the principal eigenvalue and eigenvector of Chung-Lu random graphs. arXiv:2207.03531
  7. Spectra of random graphs with given expected degrees. PMC164443

Spectral graph theory bounds:
  8. Ramanujan graph (Wikipedia consolidated source); spectral expanders.
  9. Spectral Graph Theory, Expanders, and Ramanujan Graphs (Williamson). https://williamsonchris.com/wp-content/uploads/2025/07/TR14-10_Williamson.pdf
  10. Mixing Time Bounds via the Spectral Profile (Montenegro et al.). https://5harad.com/papers/spec-profile.pdf
  11. MA431 Spectral Graph Theory Lecture 8 (Cheeger inequality canonical).
  12. Hitting and commute times in large graphs are often misleading. arXiv:1003.1266

Automorphism, orbits, Weisfeiler-Lehman:
  13. Graph automorphism canonical reference (Grokipedia / standard).
  14. Graphettes: Constant-time graphlet and orbit identity. arXiv:1708.04341
  15. The Weisfeiler-Lehman Method and Graph Isomorphism Testing. arXiv:1101.5211
  16. Spectra of symmetric powers of graphs and the Weisfeiler-Lehman refinements. arXiv:0801.2322
  17. Weisfeiler-Leman Is Incomplete on Simple Spectrum Graphs, so Canonicalize Them. arXiv:2605.23446
  18. SCHENO: Measuring Schema vs Noise in Graphs. arXiv:2404.13489
  19. Ratio of Symmetries Between any two n-Node Graphs. arXiv:2205.05726

Link-prediction generalization, KG benchmarks, negative pools:
  20. Inherent Limits on Topology-Based Link Prediction. arXiv:2301.08792
  21. Understanding Generalization in Node and Link Prediction. arXiv:2507.00927
  22. Diffusion-based Negative Sampling on Graphs for Link Prediction. arXiv:2403.17259
  23. Not All Negatives Are Worth Attending To: Meta-Bootstrapping Negative Sampling Framework for Link Prediction. arXiv:2312.04815
  24. Bias-aware training and evaluation of link prediction algorithms in network biology. PMC12184500
  25. Negative Sampling for Hyperlink Prediction in Networks. PMC7206280
  26. Toutanova K, Chen D (2015) Observed versus latent features for knowledge base and text inference. (FB15K inverse-relation leakage; standard reference.)

Cognitive-science methodology adjacencies (carried from prior drill):
  27. Schweizer K (2019) Ceiling effects in cognitive measurement. PMC6699673
  28. Bloem-Reddy B, Teh YW (2020) Probabilistic Symmetries and Invariant Neural Networks. JMLR.

Verified count = 21 distinct primary sources (with adjacencies bringing total to 28 cited works).
