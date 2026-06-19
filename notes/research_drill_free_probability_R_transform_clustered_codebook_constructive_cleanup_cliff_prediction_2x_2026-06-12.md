# Research drill: Free-probability R-transform for clustered VSA codebook cleanup-cliff prediction (2x DEEP)

Date: 2026-06-12
Drill type: 2x DEEP scan (two rounds of 6 literature queries each)
Topic: Constructive closed-form path from observed clustered codebook geometry to cleanup-cliff prediction via free-probability R-transform
Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: applied (P estimates deflated 0.15-0.25; novel-synthesis P capped 0.50; HARD-PASS / HARD-FAIL thresholds explicit)
Privacy per [[feedback-query-privacy-decomposition]]: all queries used generic math/literature terms only; no substrate-specific configs, atom names, or numerical parameters off-platform
Adjacency anchor: free-probability (Tier-1, drill_count=1 prior, scope-bonus eligible); random-matrix-theory-beyond-free-prob (Tier-1b, Tracy-Widom edge)

## HEADLINE

Free-probability theory provides a CONSTRUCTIVE closed-form path from clustered codebook geometry to cleanup-cliff prediction via three composable transforms: (1) operator-valued R-transform additive over block-structured signal + binding noise, (2) Stieltjes-transform fixed-point equation closes the recovered-signal spectrum, (3) Tracy-Widom edge of the deformed spectrum predicts the binding-count F* at which cleanup collapses. The substrate's BBP-supercritical + structured-Wishart regime is exactly where this machinery shines because R-transform composition is ADDITIVE in this regime. Substrate-product positioning: R-transform is the substrate-NATURAL mathematical foundation for capacity claims; clustered codebook + two-vector mixing IS the structured-spectrum regime.

## Round 1 findings (compact)

Q1 R-transform block-structured matrix spectrum: Operator-valued free probability handles Gaussian block matrices with general covariance; operator-valued R-transform composes additively across blocks; Far-Mingo-Speicher framework applies. (Helton-Mai-Speicher 2013 analytic subordination; Banna-Mai 2018 operator-valued matrices with free/exchangeable entries.)

Q2 Free cumulants clustered correlation matrix: Free cumulants are additive for freely-independent variables; asymptotic spectral distribution of cross-correlation matrices computable via free cumulant moment sequences; higher-order free cumulants characterize global eigenvalue fluctuations.

Q3 Voiculescu R-transform operator-valued: R-transform R_mu satisfies linearization R_{mu+nu} = R_mu + R_nu under free convolution; operator-valued analog extends to triples (M, E, B) with conditional expectation E onto subalgebra B; Voiculescu asymptotic freeness theorem extends to operator-valued case.

Q4 Spiked covariance BBP: Extreme eigenvalues detach from bulk above BBP threshold; outlier eigenvalue position is a function of deformation strength; spiked correlation, spiked separable Wishart, spiked Fisher all undergo BBP-type transitions; R-transform of the deformation determines outlier location.

Q5 Free convolution Stieltjes transform: Stieltjes transform m_mu(z) = integral d_mu(x)/(z-x); free-convolution Stieltjes obeys fixed point m_{fc,t} = m_V(z + t m_{fc,t}(z)); inversion formula rho(E) = (1/pi) lim Im[m(E+i*eta)] recovers density.

Q6 Operator-valued semicircle block matrices: Block random matrices converge to operator-valued semicircular elements over an appropriate subalgebra; explicit convergence rates available; matrices of free semicirculars and matrix-valued semicirculars connected through quadratic matrix equation with positivity constraints.

## Round 2 findings (compact, refined)

Q7 Marchenko-Pastur deformation: q-deformation of Marchenko-Pastur gives closed-form spectral moments via orthogonal-polynomial combinatorics; singular correlation matrices with block-diagonal structure yield MP-like spectrum with modified shape parameter c; correlated time series produce longer-tail, higher-peak deformed MP.

Q8 Stieltjes transform clustered Wishart: For population covariance with K spike clusters, the limiting spectrum forms K clusters; iterative Stieltjes equation m_F(z) = integral d_H(tau)/(tau(1 - c - c*z*m_F(z)) - z) where H is population eigenvalue distribution (Silverstein-Bai-Choi framework); supports block-diagonal H.

Q9 R-transform additive convolution structured noise: For C = A + B with A=signal, B=noise: R_C(g) = R_A(g) + R_B(g); semicircle noise gives R_B(g) = sigma^2 * g; this is the linearization property that makes spectrum of signal+noise computable in closed form from individual R-transforms.

Q10 Hopfield capacity spectral: Hopfield Hebbian capacity 0.138*N (Amit-Gutfreund-Sompolinsky); modern Hopfield dense / exponential capacity ~exp(d); spectral approach to Hebbian-like networks gives capacity bounds via spectral gap of interaction matrix; analogous machinery applies to VSA cleanup as eigenvalue separation problem.

Q11 VSA capacity (Clarkson-Schlegel-Plate 2023, Linearithmic Clean-up Kroneker Rotation Products 2025): Bounds on VSA dimensions for set membership, set-intersection-estimation; HRR / spatter / Hadamard-binding are lossy and require cleanup module; capacity is dimension-versus-bind-count tradeoff with closed-form bounds in the asymptotic regime.

Q12 Tracy-Widom edge clustered codebook: TW distribution governs largest eigenvalue fluctuations of deformed Wishart / signal-plus-noise / heterogeneous Gram matrices; signal-detection sequential test uses edge eigenvalues with TW null distribution; for clustered block models, Kesten-Stigum threshold SNR>1 enables polynomial-time recovery; community-detection / cleanup share the same edge-eigenvalue mathematics.

## Synthesis: constructive composition

Frame the substrate cleanup problem as a deformed spectrum problem. Let:
- C in C^{N x N} = codebook Gram matrix (clustered, block-structured covariance from intentional clustering)
- F = binding count (number of role-filler pairs bound into composite vector)
- alpha in [0,1] = two-vector mixing weight (algebra-HRR vs identity-augmented)
- K = codebook size (~280 atoms in current corpus)

Step 1: Decompose C into block-structured signal + within-cluster spread.
C = C_signal + C_noise
where C_signal is block-diagonal (cluster means), C_noise is within-cluster fluctuation. Operator-valued free probability says: under appropriate asymptotic freeness, R_C = R_{C_signal} + R_{C_noise} (Helton-Mai-Speicher 2013 confirms this for general covariance).

Step 2: Bound state X under F bindings is sum of F freely-rotated copies of code vectors plus binding crosstalk. Approximating crosstalk as semicircular noise with variance sigma^2(F):
R_X(g) = F * R_{C}(g) + sigma^2(F) * g
where the F factor comes from additive composition under free convolution (Q9), and sigma^2(F) typically scales linearly in F for random-permutation HRR binding.

Step 3: Recovered signal spectrum via Stieltjes transform fixed point (Silverstein-Bai-Choi, Q8):
m_X(z) satisfies: z = -1/m_X(z) + R_X(m_X(z))
Invert with Stieltjes inversion: rho_X(E) = (1/pi) Im[m_X(E + i*0+)].

Step 4: Cleanup cliff prediction via Tracy-Widom edge. Cleanup succeeds iff the bound-state's projection onto each cluster mean exceeds within-cluster spread by enough margin. This is exactly a BBP-type detection problem: the spike (cluster signal) detaches from the bulk (binding-noise + within-cluster spread) iff lambda_signal > lambda_BBP_threshold. The TW distribution governs edge fluctuations (Q12).

Closed-form cliff condition:
F* satisfies: lambda_max(C_signal) / [F* * sigma^2_signal + sigma^2_binding(F*)] = lambda_BBP

Solving (under linear sigma^2_binding(F) = beta * F):
F* approx lambda_max(C_signal) / (sigma^2_signal + beta * lambda_BBP) / (lambda_BBP)
Or more cleanly: F* = (1/lambda_BBP) * lambda_max(C_signal) / (sigma^2_signal + beta * lambda_BBP).

Under alpha-mixing (two-vector encoding):
sigma^2_effective(alpha) = alpha^2 * sigma^2_algebra + (1-alpha)^2 * sigma^2_identity + 2*alpha*(1-alpha)*sigma_cross
Minimum sigma^2_effective at alpha* = sigma^2_identity / (sigma^2_algebra + sigma^2_identity) (for orthogonal cross-term); at alpha=0.5 this gives near-optimal noise reduction when the two sources are roughly balanced.

## Pre-registered prediction (substrate's current corpus state, K~280, ~32 collision atoms)

Given the structured-Wishart + BBP-supercritical regime confirmed in prior drill:

HARD-PASS: Cleanup cliff at F* in [8, 12] with alpha=1.0 (algebra-HRR only), AND F* in [15, 25] with alpha=0.5 (two-vector mixing). Cliff sharpness scaling as N^{2/3} per TW edge fluctuation.

HARD-FAIL: F* < 5 with alpha=1.0 (would indicate noise dominates signal even at low bind counts, refuting structured-spectrum regime); OR F* > 35 with alpha=0.5 (would indicate clustering reduces effective dimension below what BBP predicts, refuting the structured-Wishart fit); OR cliff sharpness scales as N^{1/2} or N^1 (would refute Tracy-Widom universality, suggesting non-Wishart-class spectrum).

MIDDLE-BAND: F* outside both pass ranges but within wider [3, 50] with alpha-mixing benefit in [1.3x, 3x] range still supports the framework with refined sigma^2_binding(F) model.

## Cheap decisive test

Two python cells, no external dependencies beyond existing substrate code:
Cell A: Compute lambda_max(C_signal), spectral gap, and within-cluster sigma^2 from the existing codebook Gram matrix. Fit beta = sigma^2_binding/F linearly from 3-4 bind-count probes. Plug into closed-form F* formula. Cost ~5 minutes CPU.
Cell B: Empirically measure cleanup accuracy at F in {2, 4, 8, 12, 16, 20, 24, 32} for both alpha=1.0 and alpha=0.5; locate the F where accuracy crosses 0.5; compare to closed-form F* prediction. Cost ~15 minutes CPU.
Decisive iff predicted-vs-measured F* match within +/-30% AND TW-edge scaling N^{2/3} confirmed via varying N in {512, 1024, 2048}.

## Cross-thread synthesis

This drill closes the loop on three prior threads:
1. Structured-Wishart + BBP-supercritical regime (prior free-probability x VSA drill): confirms substrate IS in the regime where R-transform composition is well-defined; this drill makes that observation constructive (gives a formula, not just a regime label).
2. Layer 2 spectral observability (tw_edge_z structured codebooks): the negative tw_edge_z values empirically confirm clustering, which is the C_signal piece of the decomposition; this drill says HOW that clustering predicts capacity.
3. Substrate-extracted methodology rule "capability-portfolio-mechanism-diversity-is-the-lever" applies: F* depends on TWO levers (alpha-mixing AND cluster structure), and combining them multiplicatively (not adding) is the predicted lift mechanism.

## Substrate-product implications

The R-transform composition formula is the substrate's NATIVE mathematical foundation for capacity claims. LLMs offer no analog: they have no clustered-codebook spectrum, no R-transform composition, no closed-form binding-noise model. The substrate's structured codebook IS the regime where this machinery shines; LLM-attention-as-binding (Q11 surfaced this analogy) does not have block-structured covariance because attention weights are learned not structured.

This converts a research artifact into a substrate-product mathematical positioning artifact: the substrate has a closed-form capacity formula derivable from observed geometry, which is empirically falsifiable AND gives design knobs (alpha, cluster count, codebook size) with predictable effects. Per literature-is-not-oracle: literature provides the framework (R-transform composition, BBP, TW); substrate refines with measured beta, lambda_max, sigma^2 from its own corpus.

## Honest scope

STRONG: R-transform additive composition under free independence (Voiculescu); Stieltjes-transform fixed-point recovery for clustered Wishart (Silverstein-Bai-Choi); Tracy-Widom edge for deformed-spectrum BBP outlier detection. These are textbook and verified.

MODERATE: Application of operator-valued R-transform to VSA binding crosstalk as semicircular noise. Plausible (Q9 confirms semicircle is the canonical free-additive noise model) but specific to substrate's binding mechanism; needs empirical sigma^2_binding(F) linear-fit check.

SPECULATIVE: Closed-form F* formula with explicit lambda_max / (sigma^2 + beta*lambda_BBP) structure. Combines three textbook results into a substrate-specific prediction that has NO direct literature precedent at this level of specificity. Calibration penalty applied: P_deflated for full closed-form match in HARD-PASS band = 0.35 (deflated from raw 0.55 estimate by 0.20 per uncharted-regime penalty).

## Citations (verified)

13 distinct sources confirmed across 12 queries:
1. Helton-Mai-Speicher (2013) Analytic subordination theory of operator-valued free additive convolution - arxiv 1303.3196
2. Banna-Mai (2018) Operator-Valued Matrices with Free or Exchangeable Entries - arxiv 1811.05373
3. Speicher (2017) Operator-Valued Free Probability Theory and Block Random Matrices - Springer chapter
4. Capitaine (2016) Spectrum of deformed random matrices and free probability - arxiv 1607.05560
5. Baik-Ben Arous-Peche (BBP) phase transition - Barbier lecture notes
6. Silverstein-Bai-Choi framework, surveyed in Bun-Bouchaud-Potters (2016) arxiv 1610.08104
7. Tracy-Widom for heterogeneous Gram matrices - arxiv 2008.04166
8. Tracy-Widom for elliptical model edge eigenvalues - IMA-Inf-Inf 2025
9. Clarkson-Schlegel-Plate (2023) Capacity Analysis of Vector Symbolic Architectures - arxiv 2301.10352
10. Kroneker-Rotation linearithmic cleanup (2025) - arxiv 2506.15793
11. q-deformation of Marchenko-Pastur (2026) - arxiv 2601.09427
12. Amit-Gutfreund-Sompolinsky Hopfield 0.138 capacity - classical
13. Voiculescu R-transform foundational - reviewed in arxiv 1101.4389 matricial R-transform

## P_deflated summary

Headline framework correctness: 0.65 (R-transform composition + BBP + TW are textbook)
Specific closed-form F* prediction band match: 0.35 (novel-synthesis cap applied 0.50, then 0.15 uncharted-regime deflation)
TW edge scaling N^{2/3} confirmation: 0.55 (well-supported by literature universality)
Substrate-product positioning artifact value: 0.70 (regardless of empirical match, the mathematical positioning IS the artifact)

Next-drill candidate: random-matrix-theory-beyond-free-prob (Tracy-Widom universality at finite N corrections; Dyson Brownian motion gives the cliff-sharpness scaling at finite-K; this would refine the cliff-sharpness HARD-PASS / HARD-FAIL bounds from "scaling exponent" to "explicit constant"). Tier-1b, drill_count low, adjacency anchor=free-probability fruit-bearing.
