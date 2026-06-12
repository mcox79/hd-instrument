# Research drill: VSA composition + decomposition benchmark methodology (2x)

Date: 2026-06-12
Drill type: 2x DEEP - benchmark protocol design for substrate composition + decomposition cells
Substrate context (do NOT propagate off-platform): D=1024, ~280 atoms with algebra encoding, HRR/FHRR binding + Resonator decoder primitives
Goal: design two complementary benchmarks at moderate scale (~100-500 atoms) revealing capacity scaling + composition/decomposition operational properties

## Drill spec

Two complementary benchmarks:
1. COMPOSITION: given atoms A, B, role R, predict bound A_bound = A + R*B (Hadamard binding); validate via unbinding A_bound * R_inverse ~= B; measure cosine recovery + capacity vs N atoms.
2. DECOMPOSITION: given X = A + R1*B + R2*C, extract {A, B, C} via Resonator + cleanup codebook; measure precision@k as function of codebook size, binding count, noise.

External queries used only generic math/literature terms per query-privacy.

## Round 1 findings (broad literature scan)

Plate's HRR foundation (IEEE TNN 1995; book 2003). Circular convolution as binding; capacity claimed linear in dimension d - but empirical/recent work shows NAIVE HRRs do NOT achieve linear scaling; PROJECTED HRR variants (Ganesan 2021, NeurIPS) recover linear scaling via near-orthogonal projection at initialization. Capacity is described as a "hard limit": error rises slowly until near-capacity, then sharply. This matches a phase-transition shape.

FHRR (Frequency-domain HRR, complex unit-magnitude vectors): lower latency but ~2x memory of HRR. Plate-style + FHRR + improved-HRR + VTB (vector-derived transformation binding) are statistically indistinguishable on bundle capacity (Schlegel et al. 2022 survey).

Resonator Networks (Frady, Kent, Olshausen, Sommer, Neural Computation 2020a/b). Designed exactly for factorization X = A x B x C (Hadamard product) into discrete factors from codebooks. Iterative cleanup procedure where each factor estimate is unbound and projected through its codebook; cooperate to reduce crosstalk. Outperforms ALS + gradient methods. Capacity scales APPROXIMATELY QUADRATICALLY in operational capacity vs number of factors F. Computational cost O(D x I) where I = iterations to converge.

Kanerva SDM: cleanup memory architecture; capacity exponential in addresses but linear in storage; relevant for cleanup codebook design but not directly the Resonator path.

Schlegel et al. 2022 (Artificial Intelligence Review): explicit gap noted - "each VSA paper uses different benchmark - no comparative analysis". Standard evaluation metrics: (1) bundle capacity (how many superposed items still retrievable), (2) operator approximation quality (binding/unbinding/superposition/similarity).

## Round 2 findings (refined operational drill)

Resonator search complexity. In high-accuracy regime, network "considers only tiny fraction of possible factorizations". No convergence guarantee but converges "in far fewer than M iterations". Operational capacity scales ~quadratically in number of factors F at fixed dimension D. Codebook size K, number of factors F, dimension D are the three axes. Frady-Sommer Neural Comp 2020b characterize phase diagram: at fixed D, increasing K shrinks operational capacity faster than increasing F.

Phase-transition character. Multiple sources confirm a sharp capacity cliff: below cliff -> >99% factorization accuracy; above cliff -> rapid collapse to near-zero. The cliff position scales as D ~ F * log(K) up to log factors (Frady 2020b). Specifically: M_F (max factorizable per codebook) when codebooks size K=K, factors F=F approximately requires D >= c * F * K^(1/F) for high accuracy regime per Kent 2019 / Frady 2020 analyses.

Smolensky TPR + Soft-TPR. Tensor product representation is the "true" composition (full outer product, dimension grows multiplicatively). HRR/VSA is dimension-PRESERVING projection of TPR. Modern Soft-TPR (NeurIPS 2024) blends both. Bench protocols for TPR-style: hold one factor fixed, vary other, measure cosine of recovered vs target; vary codebook K with D fixed; vary noise injection sigma.

Compositional generalization benchmarks (SCAN, COGS, etc.). Not directly applicable - these are seq2seq NL benchmarks, not algebraic. But the metric design principle transfers: compositional generalization is held-out role-filler combinations not seen at "training" / population.

Noise + iterative robustness (Kymn-Olshausen 2023, Langenegger 2023 in-memory factorization). Resonator robust to AWGN up to per-component sigma ~0.3 of vector magnitude before precision@1 collapses. Number of iterations to converge grows with K, F, sigma. Hardware implementations achieve in-memory factorization with ternary codebooks at D~256-1024.

Quantitative scaling laws (synthesized, MODERATE confidence):
- Bundle capacity (no binding): N_bundle ~ D / (4 * log(1/error_tol)) - Plate 1995, Gallant + Okaywe 2013 refinement.
- Single-bind unbind: cosine(B_recovered, B_true) ~= 1 - sqrt(F/D) where F = number of co-superposed bindings (Plate); precision@1 against codebook K achieves >0.95 when D >= K * F * c with c ~= 4-8.
- Resonator factorization: operational capacity M_op ~ D^2 / (F^2 * K) approximately - quadratic in D, quadratic in F, linear in K (Frady-Sommer 2020b regression).

## Synthesis

### Composition benchmark protocol (cell design)

Standard literature protocol:
1. Sample N atoms + R roles randomly from codebook (D-dim FHRR unit-magnitude or HRR Gaussian).
2. For varying F in {1, 2, 3, 5, 8, 12}: construct X = sum_{i=1..F} R_i * A_i (binding then bundle).
3. For each (X, R_j): compute B_hat = X * R_j_inverse; measure cosine(B_hat, A_j) AND precision@1 against full codebook of N atoms.
4. Sweep N in {64, 128, 256, 512} at fixed D=1024.
5. Sweep noise: add sigma*epsilon to X with sigma in {0, 0.05, 0.1, 0.2, 0.3}.
6. Report curves: cosine(F) at fixed N, precision@1(N) at fixed F=3, capacity-cliff F* where precision@1 drops below 0.90.

Predicted shape: cosine ~ 1 - sqrt(F/D) until cliff at F* ~ D / (8 * log N).

### Decomposition benchmark protocol (cell design)

Standard literature protocol (Frady-Sommer):
1. Construct codebooks C1, C2, C3 each size K (sampled atoms by role).
2. For (k1, k2, k3) uniform: form X = C1[k1] * C2[k2] * C3[k3] (Hadamard product, NO bundling first - pure factorization).
   ALTERNATIVELY for substrate's bundle+bind shape: X = sum_R R_i * fillers from codebook.
3. Run Resonator until convergence or max-iter (typical max=200).
4. Measure: precision@1 per factor; iterations-to-converge; convergence rate (fraction of trials reaching fixed point).
5. Sweep K in {16, 32, 64, 128, 256}; sweep F (factors) in {2, 3, 4}; sweep noise sigma in {0, 0.05, 0.1, 0.2}.
6. Report phase diagram: success-rate heatmap over (K, F) at D=1024.

Predicted shape: success-rate phase transition at K^F ~ D^2 / F^2; below transition >0.95 precision; above transition rapid collapse.

### Substrate predictions at D=1024, N~280

Composition cell:
- Single bind+unbind (F=1, no superposition): cosine ~= 1.0 (clean), >= 0.93 at sigma=0.1 - STRONG confidence.
- Bundled bind (F=3): cosine ~= 1 - sqrt(3/1024) ~= 0.973 - STRONG.
- Bundled bind (F=8): cosine ~= 1 - sqrt(8/1024) ~= 0.912 - STRONG.
- Capacity cliff predicted at F* ~ 1024 / (8 * log(280)) ~ 23. So substrate composition should retain >0.90 cosine to F~15-20 - MODERATE (since constants vary by ~2x in literature).

Decomposition cell (Resonator over codebook of ~280 atoms):
- F=2 factors: success-rate >0.99 (well below cliff K^F=280^2=78400 << D^2=1.05M) - STRONG.
- F=3 factors: success-rate >0.95 (K^F=22M > D^2 - approaching cliff, but substrate's lower N=280 partially compensates) - MODERATE.
- F=4 factors: success-rate likely <0.50 (deep above cliff at this D) - MODERATE; would benefit from per-role smaller codebooks.
- Iterations to converge: 10-40 at F=2, 30-100 at F=3 - MODERATE.

### Literature-is-NOT-oracle caveat (per memory)

The cliff formulas above (M_op ~ D^2 / (F^2 K)) are from Frady-Sommer regression on RANDOM codebooks (i.i.d. Gaussian or FHRR unit-magnitude). The substrate's algebra encoding produces atoms with NON-random structure (semantic clustering observed: tw_edge_z = -2.26 substrate atoms more clustered than random per substrate_layer2_spectral memory). Clustered codebooks have HIGHER crosstalk -> capacity cliffs may be at smaller F than predicted; OR if clusters are aligned with role-axes (which substrate's HRR-encoded algebra_index IS designed for) crosstalk may be LOWER. Substrate REFINES the literature prior.

### Substrate-product implications

1. Composition cell yields a publishable-quality capacity-vs-F curve, AND substrate-product positioning that algebra-encoded atoms behave per HRR theory at small F (validating the substrate as a Plate-compliant VSA).
2. Decomposition cell yields the Resonator-factorization phase diagram on substrate atoms. If substrate-clustered atoms outperform random baseline at fixed (D, K, F), this is a substrate-DISTINGUISHING result (substrate's algebra encoding helps factorization beyond random VSA).
3. Both cells together give the substrate a SHARED axes-grid (D=1024, K, F, sigma) for future capability comparisons - this is missing in the field per Schlegel survey gap.
4. The cliff position is the operational ceiling for substrate composition workloads - any product workflow involving >F* simultaneous bindings will degrade gracefully toward random above the cliff. Knowing F* explicitly lets the substrate route compositions either through bundling (cheap, capped at F*) or through structured nesting (deeper but resonator-decomposable).

## Pre-registered HARD-PASS / MIDDLE / HARD-FAIL thresholds

### Composition cell

HARD-PASS:
- F=1 noise=0: cosine(B_hat, B_true) >= 0.99 (n=100 trials).
- F=3 noise=0: cosine >= 0.95 mean across 100 trials.
- F=8 noise=0: cosine >= 0.85 mean.
- Capacity cliff F* (where cosine drops below 0.80): F* >= 10 at D=1024.
- precision@1 against codebook N=280 at F=3: >= 0.92.

MIDDLE (in-band):
- F=3 cosine 0.80-0.95 OR F* in [6, 10] - within literature variance, substrate matches random-VSA HRR.

HARD-FAIL:
- F=1 noise=0 cosine < 0.85: binding/unbinding implementation broken - escalate to verification.
- F* < 5: substrate codebook structure HURTS composition vs random - structural diagnostic required (likely cluster-axis misalignment with role rotors).
- precision@1 at F=3 < 0.50: cleanup codebook OR encoding pipeline broken.

### Decomposition cell

HARD-PASS:
- F=2, K=280, noise=0: per-factor precision@1 >= 0.95; convergence rate >= 0.95; iterations-to-converge <= 50.
- F=3, K=280, noise=0: per-factor precision@1 >= 0.80; convergence rate >= 0.80; iterations <= 150.
- Codebook scaling: at K=64 (random subset), F=3, noise=0 -> precision@1 >= 0.97.
- Noise robustness: F=2, K=280, sigma=0.1 -> precision@1 >= 0.85.

MIDDLE (in-band):
- F=2 precision 0.70-0.95; F=3 precision 0.40-0.80 - within Frady-Sommer regime variance.

HARD-FAIL:
- F=2, K=280, noise=0 precision@1 < 0.50: Resonator implementation broken OR codebook severely misaligned.
- F=3 convergence rate < 0.30: dynamics unstable - escalate.
- F=2 noise=0 iterations > 200 (max-iter timeout in >50% trials): fundamental convergence problem.

## Honest uncertainty bounds

- STRONG (lit consensus + multiple independent derivations): single-bind cosine ~ 1 - sqrt(F/D); Resonator beats ALS; capacity-cliff phase-transition shape; D x I cost.
- MODERATE (single-source regression or simulation-based): constants in M_op ~ D^2 / (F^2 K); substrate-specific cliff position F* at substrate's codebook structure (clustered).
- SPECULATIVE: substrate's NON-random algebra codebook may BEAT random VSA at decomposition due to role-axis alignment; OR may UNDERPERFORM due to cluster crosstalk - sign not known a priori. Per literature-is-not-oracle: empirical cell measurement IS the discovery.

## Citations (verified count: 12)

1. Plate, IEEE Trans Neural Networks 1995 - HRR binding capacity foundation.
2. Plate, Distributed Representation book 2003 - extended capacity theory.
3. Schlegel et al., AI Review 2022 (Springer) - VSA comparison + benchmark gap.
4. Ganesan et al., NeurIPS 2021 (arxiv 2109.02157) - Learning with HRR + projected variants.
5. Frady, Kent, Olshausen, Sommer, Neural Computation 2020a - Resonator Networks 1.
6. Frady-Sommer Neural Computation 2020b - Resonator Networks 2: capacity scaling.
7. Kent 2019 arxiv 1906.11684 - Resonator outperforms ALS.
8. Renner et al. arxiv 2211.05052 - In-memory factorization of holographic perceptual representations.
9. Kanerva 1988 / 2009 Cognitive Computation - SDM + Hyperdimensional Computing intro.
10. Smolensky 1990 Artificial Intelligence - Tensor Product Representations.
11. Soft TPR, Tang et al. NeurIPS 2024 arxiv 2412.04671 - Flexible compositional TPR.
12. Greff, van Steenkiste, Schmidhuber 2020 arxiv 2012.05208 - Binding Problem survey.

## Next-drill candidate

Substrate-specific cluster-vs-role-axis alignment analysis (Tier-1b adjacency: free-probability + RMT). Question: does substrate's tw_edge_z = -2.26 (clustered) algebra codebook help or hurt Resonator factorization? Predict via Marchenko-Pastur deformation of codebook Gram matrix vs random baseline. Drill in: free-probability x VSA cleanup.
