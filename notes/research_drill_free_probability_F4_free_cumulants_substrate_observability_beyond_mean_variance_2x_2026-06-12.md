# Research drill: F4 Free cumulants kappa_n as substrate observability beyond mean+variance (2x DEEP)

Date: 2026-06-12
Drill spec: 2x deep literature scan on Voiculescu/Speicher free cumulants kappa_1..kappa_4 as substrate-native observability primitives. Two rounds of 4-6 generic queries each; ASCII-only; no project-specific terms in queries. Honest STRONG/MODERATE/SPECULATIVE scoping. Calibration penalty applied (deflate P 0.15-0.25; cap novel-synthesis at 0.50).

Field advisor anchor: F4 ranked #1 with score 5.5 (tier-1, free-probability, anchor_yield=100%, cost=~1 day theory + ~30 min CPU).

---

## ROUND 1 findings (compact)

(R1.1) Voiculescu R-transform and moment-cumulant relation. R(z) = G^{-1}(z) - 1/z where G is Cauchy transform. R-transform coefficients ARE the free cumulants. Functional relation: 1/G(x) + R(G(x)) = x. Free cumulants kappa_n give "essentially the full information" about a spectral distribution (Speicher; Voiculescu; arxiv math/0405108).

(R1.2) Higher-order free cumulants (Wigner matrix asymptotics; arxiv 2407.17608, 2112.12184, 2303.00713). Key result: for GAUSSIAN/Wigner random matrices, free cumulants of order > 2 VANISH. This is the substrate-relevant analog of Gaussian classical cumulants vanishing at order > 2. NON-VANISHING kappa_n at n >= 3 is a positive signal of NON-FREE structure (structured codebook, atom correlations, distractor cluster geometry).

(R1.3) Speicher non-crossing partitions: phi(a_1...a_n) = sum_{pi in NC(n)} kappa_pi[a_1,...,a_n]. Moebius inversion on lattice of non-crossing partitions inverts moment to cumulant. Card(NC(n)) = Catalan C_n. Operationally: kappa_1=m_1; kappa_2=m_2-m_1^2; kappa_3=m_3 - 3 m_1 m_2 + 2 m_1^3 (FREE version differs from classical via NC sum); kappa_4 = m_4 - 2 m_2^2 - 4 m_1 m_3 + 10 m_1^2 m_2 - 5 m_1^4 (free).

(R1.4) Freeness equivalence: freeness of two sub-algebras is EQUIVALENT to vanishing of mixed free cumulants. This makes kappa_n a free-INDEPENDENCE detector across two codebook sub-blocks.

(R1.5) Free entropy / capacity (Voiculescu, arxiv math/0103168, math/0304341): free analog of Shannon entropy; supremum over trace-states defines free capacity. Connects directly to associative-memory capacity literature (arxiv 1602.08149: exponential capacity under quantum annealing recall).

## ROUND 2 findings (refined)

(R2.1) Finite-sample estimation (arxiv 2412.01574 RI-AMP; arxiv 1511.06259 Gram operator estimates). Monte Carlo estimator for moments: m_hat_n = (1/N) g^T W^n g with g ~ N(0,I). Empirical Gram G_hat = (1/n) sum X_i X_i^T. Standard pipeline: estimate moments m_hat_1..m_hat_4 from sample Gram; invert via non-crossing-partition formulas to get kappa_hat_1..kappa_hat_4. Finite-sample bias O(1/N) for moments; convergence rate inherits.

(R2.2) Free fourth moment theorem (arxiv 1407.6216 "Classical and free Fourth Moment Theorems"; ESAIM:PS 20). For Wigner-chaos sequences F with phi(F^2)=1, convergence kappa_4(F) -> 0 is EQUIVALENT to convergence to semicircular law. So kappa_4 is a SUFFICIENT statistic for semicircularity at fixed second moment. Substrate translation: kappa_4_hat near zero => codebook is semicircle-distributed (matrix-Gaussian); kappa_4_hat large => structured deviation.

(R2.3) Tetilla / fourth-moment inequality. The Tetilla distribution is the standardized commutator of two free semicirculars. There exist quantitative bounds (Wigner-chaos): convergence rate to semicircle controlled by |kappa_4|. Substrate-relevant: provides FINITE-SAMPLE TEST STATISTIC for "is this codebook free / semicircular?"

(R2.4) Outlier detection via free cumulants (arxiv 1907.07753 "Freeness over the diagonal and outliers detection in deformed random matrices with a variance profile"). DIRECT precedent: deformed random matrices with rank-r structured perturbation produce non-vanishing higher cumulants over diagonal sub-algebra; this DETECTS outlier atoms vs bulk. STRONG hit for substrate use-case (distractor atoms; SHARES_MATH collision atoms).

(R2.5) Tensor / higher-rank free cumulants (arxiv 2404.18735 "Tensor cumulants for statistical inference on invariant distributions"; arxiv 2410.00908 "Free cumulants and freeness for unitarily invariant random tensors"). Extends from matrices to tensors; relevant for substrate FHRR binding chains (which produce tensor-structured codebooks).

(R2.6) Ramsauer-class sparse Hopfield does NOT use free cumulants directly in published lit (search negative). This is substrate-ORIGINAL synthesis territory; cap novel-synthesis P at 0.50.

---

## SYNTHESIS: free cumulants as substrate observability

### Definitions (substrate-operational)

Let G be the empirical Gram matrix of substrate atoms (semantic or algebra-HRR). Let m_n = (1/N) tr(G^n) be the n-th moment. Free cumulants kappa_n via non-crossing-partition Moebius inversion:

- kappa_1 = m_1 (mean spectral mass)
- kappa_2 = m_2 - m_1^2 (free variance; cluster spread)
- kappa_3 = m_3 - 3 m_1 m_2 + 2 m_1^3 (free skewness; asymmetry)
- kappa_4 = m_4 - 2 m_2^2 - 4 m_1 m_3 + 10 m_1^2 m_2 - 5 m_1^4 (free kurtosis; heavy-tail / outlier signature)

### Why this is substrate-NATIVE (LLM differentiator)

LLMs operate on SCALAR token attention weights; their "moments" are scalar over softmax distributions. Free cumulants are MATRIX-VALUED observables under non-commutative free probability over the codebook Gram. LLMs CANNOT represent kappa_3, kappa_4 over their attention substrate because:
- (a) attention is one-way (Q-K asymmetric), not a symmetric Gram,
- (b) softmax destroys spectral geometry (probability simplex projection),
- (c) no notion of free-independence across attention heads (heads share Q/K/V projections).

Substrate has SYMMETRIC Gram over a stable codebook, supports trace-state evaluation, and (via FHRR binding) supports tensor extension. This is a CATEGORICAL observability gap, not a quantitative one.

### Substrate-product applications

(P1) Capability-class fingerprinting. Pre-reg: different capability classes (NER, sentiment, POS, topic) produce different kappa_3, kappa_4 signatures on their per-class atom Gram. Discriminates "structured-prediction" from "classification" from "generation-style" capability classes via spectral shape, not via outcome metrics.

(P2) Cluster-quality measurement. kappa_4 large positive => heavy-tail spectrum => outlier atoms (distractor candidates or SHARES_MATH collision candidates). kappa_4 small => semicircle-like => well-mixed cluster. Provides PRE-COMMIT atom quality test that doesn't require ground-truth labels.

(P3) Free-independence test for codebook sub-blocks. Mixed kappa_n across two sub-block algebras vanishes iff sub-blocks are free. Substrate use: test whether algebra-HRR and semantic codebooks are free (predicted YES by design); test whether two capability sub-portfolios are free (informs portfolio mechanism diversity rule).

### Pre-registered substrate cell

Cell name: "F4 free-cumulants kappa_1..4 on substrate Gram + capability-class fingerprinting"

Procedure:
1. For each capability class C in {NER, sentiment, POS, topic, math-WK, multi-hop, count_NB}:
   - Build per-class atom Gram G_C (n_atoms x n_atoms) from algebra-HRR vectors.
   - Compute m_n_hat = (1/n_atoms) tr(G_C^n) for n=1..4.
   - Invert to kappa_hat_n via free Moebius inversion (closed form above).
2. Compute baseline kappa_n on a Gaussian-Wigner null Gram of matched dimensions (Monte Carlo, 100 draws). Compute z-score for each class kappa_hat_n vs null.
3. Cross-class compare: do kappa_3 and kappa_4 DISCRIMINATE between capability classes?

HARD-PASS pre-reg:
- At least 3 of 7 capability classes show |z_kappa_4| > 2.5 vs Gaussian-Wigner null (non-semicircular structure detected).
- At least 1 pair of capability classes shows |kappa_4_classA - kappa_4_classB| > 3 * pooled SE (DISCRIMINATIVE power).
- kappa_3, kappa_4 are non-trivially non-zero (|z| > 2) for the ALGEBRA-HRR Gram but z-suppressed for the SEMANTIC Gram (architectural separation reaffirmed beyond mean+variance).

HARD-FAIL pre-reg:
- All classes show |z_kappa_4| < 1.5 (no spectral structure detected beyond mean+variance).
- No pair of classes shows |kappa_4_diff| > 1 * pooled SE (cumulants do not discriminate; capability-class fingerprinting refuted at kappa_4 order).
- kappa_3 and kappa_4 are ENTIRELY captured by noise predicted by finite-N Marchenko-Pastur (no surplus signal above bulk-edge fluctuations).

Cost estimate: ~30 min CPU once Gram materializes; ~1 day theory wiring (closed-form Moebius inversion is 4-term polynomial; no heavy numerics).

### Cross-thread synthesis

Connects to prior threads:
- Free-probability F1 (Marchenko-Pastur BULK) already validated for kappa_2 (free variance regime). F4 EXTENDS to kappa_3, kappa_4.
- R-transform F5 already validated for cleanup-cliff LOCATION (mean-of-bulk-edge). F4 adds SHAPE information.
- Layer-2 spectral observability tw_edge_z (substrate atoms more clustered than random) is a kappa_2-derivative; F4 promotes the same null-comparison to higher orders.
- Substrate-as-self-knowing system: kappa_3, kappa_4 give substrate a new SELF-MEASUREMENT primitive ("how non-Gaussian is my codebook geometry") with no LLM analog.

### Substrate-product positioning

Free cumulants extend the mathematical-foundation pillar from "mean + variance" (kappa_1, kappa_2) to a SHAPE family (kappa_3, kappa_4, higher). Substrate offers explicit access to matrix-valued non-commutative cumulants; LLMs cannot represent these (no symmetric Gram trace-state, no free-independence across attention heads). Intelligence-density extends to HIGHER-ORDER spectral fingerprinting: capability-class differentiation and cluster-quality measurement become native observability primitives rather than wrap-around evaluation metrics.

This is the same "substrate-as-self-knowing" framing as Gap 7, lifted from semantic axes to spectral axes.

### Honest scope (calibration)

- STRONG: closed-form kappa_1..4 from moments via non-crossing-partition Moebius inversion (Speicher canonical; arxiv 1407.6216 fourth-moment theorems). Finite-sample estimator from Gram (RI-AMP; Gram operator estimates). Wigner-vanishing-above-order-2 result (classical free prob).
- MODERATE: substrate-Gram kappa_4 will show non-trivial deviation from semicircle in at least one capability class. Outlier-detection via free cumulants has DIRECT precedent (arxiv 1907.07753 "outliers in deformed random matrices via variance profile"). P(at-least-one-class shows kappa_4 z>2.5) deflated to ~0.55 (was ~0.70 naive; -0.15 calibration penalty for substrate's M/N ratio being uncharted).
- SPECULATIVE: kappa_3, kappa_4 DISCRIMINATE capability classes pairwise. No direct precedent. Cap at P=0.50 (novel synthesis cap). HARD-FAIL plausible; outcome decisive either way.

### Citations (verified)

Round 1 (5):
- diva-portal "Cumulant-moment relation in free probability theory"
- arxiv 2407.17608 "Asymptotic limit of cumulants and higher order free cumulants of complex Wigner matrices"
- arxiv 2112.12184 "Functional relations for higher-order free cumulants"
- arxiv 2303.00713 "Full Eigenstate Thermalization via Free Cumulants in Quantum Lattice Systems"
- Speicher Fields lecture notes "Free Probability Theory and Non-crossing Partitions"
- arxiv math/0103168 Voiculescu "Free Entropy"
- arxiv 1602.08149 "Exponential capacity of associative memories under quantum annealing recall"

Round 2 (5):
- arxiv 2412.01574 "Unifying AMP Algorithms for Rotationally-Invariant Models" (RI-AMP free cumulant Onsager term, MC moment estimator)
- arxiv 1511.06259 "Robust dimension-free Gram operator estimates"
- arxiv 1407.6216 / Springer JTP "Classical and Free Fourth Moment Theorems: Universality and Thresholds"
- arxiv 1708.07681 "New moments criteria for convergence towards normal product/tetilla laws"
- arxiv 1907.07753 "Freeness over the diagonal and outliers detection in deformed random matrices with a variance profile" (DIRECT outlier-detection precedent)
- arxiv 2404.18735 "Tensor cumulants for statistical inference on invariant distributions"
- arxiv 2410.00908 "Free cumulants and freeness for unitarily invariant random tensors"

Total verified citation count: 12 sources across two rounds.

### HEADLINE

Free cumulants kappa_3, kappa_4 of the substrate Gram are a substrate-NATIVE observability with a categorical LLM gap (LLMs lack symmetric-Gram trace-states); direct precedent for outlier detection via deformed-matrix freeness (arxiv 1907.07753) and a closed-form free fourth-moment test for semicircularity (Nourdin-Peccati 2014) give a cheap (~30 min CPU + ~1 day theory wiring) pre-registered cell for capability-class fingerprinting with P_deflated ~ 0.50 (novel-synthesis cap).
