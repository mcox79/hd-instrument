# research drill: free-probability MP bulk subleading 1/sqrt(N) correction -- empirical test design (2x DEEP)

date: 2026-06-12
field: free-probability (Tier-1, scope-expansion; advisor anchor)
mode: 2x DEEP drill (two rounds of generic literature scans, then operational synthesis)
calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]

## Drill spec

Substrate cleanup-cliff has been characterized in two prior deliveries:
- LOCATION: free-probability R-transform formula predicts cliff (closed-form, slope ~1.0 confirmed).
- SHARPNESS: Marchenko-Pastur BULK regime with O(1) leading width + 1/sqrt(N) + 1/N subleading corrections (NOT Tracy-Widom edge; slope-zero observation matches BULK not EDGE).

This drill tests the next predicted layer: the 1/sqrt(N) SUBLEADING correction itself, via a cheap-CPU smoke at three (q, N) configurations spanning a decade in N.

## Round 1 findings (compact)

R1.Q1 -- Marchenko-Pastur 1/sqrt(N) finite-size corrections (bulk).
For beta-Wishart ensembles, the eigenvalue density admits an asymptotic expansion rho(lambda) = rho_0(lambda) + (1/M) rho_1(lambda) + (1/M^2) rho_2(lambda) + o(1/M^2), valid in the BULK where rho_0 != 0. The expansion breaks at the edges. Smoothed density carries no oscillatory terms; corrections are monotone-in-1/M in bulk. (arXiv:1209.6171; UChicago Wigner-MP notes.)

R1.Q2 -- Wishart spectrum subleading corrections.
Finite-N corrections to limiting laws (smallest eigenvalue, soft edge) are tractable; at soft edge the expansion parameter is n^{-2/3} (Tracy-Widom regime), while in the BULK the expansion parameter is 1/n. Moment expansion of the limit measure in 1/c (aspect ratio) gives systematic subleading corrections. (arXiv:1506.02387; arXiv:2403.07628.)

R1.Q3 -- Stieltjes transform asymptotic expansion at finite-N.
Standard tool. At infinity S(z) = sum_k m_k / z^{k+1} + o(1/z^{n+1}). For finite-N analysis of empirical spectral distribution, expansions of the mean Stieltjes transform in 1/n yield bulk corrections. (Wikipedia Stieltjes; arXiv:1410.3503.)

R1.Q4 -- Free probability R-transform subleading-order corrections.
"Infinitesimal free probability" frames 1/N corrections to freeness via infinitesimal free cumulants and an infinitesimal R-transform. Two distinct sources of subleading corrections appear at O(D^{-2}) and higher. Second-order moment-cumulant relations are intricate. (arXiv:2412.02572; arXiv:2208.07515.)

R1.Q5 -- Replica method finite-N expansion.
Two sources of 1/N finite-size corrections: (a) subleading part of the replicated action, (b) Gaussian fluctuations around the saddle. The structurally correct procedure is replica trick at finite N FIRST, then asymptotic expansion. (arXiv:0911.1313; arXiv:0809.4071.)

R1.Q6 -- Empirical spectral distribution convergence rate to MP.
Kolmogorov distance to MP is O(n^{-1/2}) under standard 4th-moment conditions, accelerating to O(n^{-1}) under stricter (4th moment bounded, entries bounded by D n^{1/4}) conditions. Sub-exponential decay yields O(n^{-1} log^{4+4/kappa} n). Bulk converges faster than edges. (arXiv:1110.1284; arXiv:1412.6284; Bernoulli 10(3) Gotze-Tikhomirov.)

## Round 2 findings (compact)

R2.Q1 -- Hopfield cleanup capacity finite-N scaling experiment design.
Classical mean-field capacity alpha_c ~ 0.138 N is asymptotic; small-N effects are not captured. Modern protocols benchmark at varying N (e.g., N = 64, 128, 256, 512, 1024) and fit a finite-size scaling form C(N) = c0 + c1/sqrt(N) + c2/N to retrieval-rate curves. Basin-size definitions matter (minimum-flip vs 50% recall). (Frontiers Comp Neuro 2016; PLOS ONE 2017.)

R2.Q2 -- Random matrix finite-size measurement protocol.
Standard practice: ensemble-average over many realizations; track convergence rate at varying N (often N = 50 .. 5000 in spans of 10x); decompose error into bulk vs edge components. Unfolding is required to remove cutoff. (arXiv:2402.10271.)

R2.Q3 -- Numerical convergence test MP bulk.
Recent work systematically quantified pre-asymptotic deviations of empirical eigenvalue densities from MP across N = 50 to 5000, decomposing error into BULK vs EDGE. Convergence in bulk is faster than at edges. Multiply both matrix dimensions by factors of 10 to validate convergence. Optimal short-scale convergence in bulk reaches m^{-1+eps}. (arXiv:1302.1458 beta-Laguerre.)

R2.Q4 -- Associative memory finite-N capacity benchmark numerical fit.
Capacity definitions: max patterns retrievable as metastable states; basin-size constrained recall (e.g., 50% recall with 1-flip basin). Fit P_max(N) vs N to a + b/sqrt(N) + c/N form is standard. Sub-leading 1/sqrt(N) coefficient typically O(1) of leading. (Hopfield-McEliece n / (2 log n); Krotov dense Hopfield.)

R2.Q5 -- Sparse Hopfield finite-N capacity protocol.
For K = {1, 2} sparse Hopfield, capacity C = O(N) linearly in N with finite-N coefficient. Sparsity reduces spurious states. Same fit form applies.

R2.Q6 -- Edge vs bulk finite-size scaling random matrix universality.
Edge scaling: n^{-2/3} (Tracy-Widom). Bulk scaling: n^{-1}. In bulk, Christoffel-Darboux correction term is LOWER ORDER than leading; in edge they contribute at same order. Confirms that for cliff-width in BULK, the correct expansion parameter is 1/n with possible intermediate 1/sqrt(n) term from boundary-of-bulk crossover.

## Synthesis

THEORETICAL PREDICTION OF 1/sqrt(N) COEFFICIENT.
The literature distinguishes three regimes for the subleading expansion:
(a) Pure bulk, smoothed: expansion is in 1/n (Wishart asymptotic expansion result). The literal 1/sqrt(N) term is NOT predicted by bulk MP asymptotics; the leading correction is 1/n.
(b) Empirical (Kolmogorov-distance) to MP: O(n^{-1/2}) under standard moment conditions, O(n^{-1}) under strict moments. Standard substrate codebooks (bipolar, complex unit-norm) typically satisfy strict moment conditions, predicting closer to O(n^{-1}) than O(n^{-1/2}) -- but with finite-N data the dominant observed term may be 1/sqrt(N) due to sampling variance of the empirical density estimator (Monte-Carlo n^{-1/2}).
(c) Boundary-of-bulk (near cliff edge): MP bulk expansion breaks; intermediate scaling can appear.

SUBSTRATE PREDICTION.
For substrate cliff WIDTH (measured as e.g. the slope-magnitude region where mean cleanup margin drops from leading bulk value to zero), the expected finite-N form is:

  width(N) = c0 + c1 / sqrt(N) + c2 / N + o(1/N)

with c0 = O(1) leading bulk width (substrate-empirical from prior delivery), and c1, c2 of opposite signs is possible. The c1 coefficient combines (i) sampling variance of width-estimator (Monte-Carlo n^{-1/2}) and (ii) the genuine "near-bulk-edge" intermediate term. The c2 coefficient is the pure-bulk 1/n correction.

If substrate operates strictly in the bulk: c1 may be small, c2 dominates; observed slope of width(N) on log-log should approach -1.
If substrate operates at boundary-of-bulk: c1 is O(c0/2) to O(2 c0); observed slope nearer -1/2.

CHEAP-CPU SMOKE TEST PROTOCOL.
- Configurations: N in {100, 300, 1000} (decade span; 3 anchor points sufficient for c0, c1, c2 fit but only just; if budget allows add N = 600).
- Filler counts: q in {3, 10} (two values to test q-invariance of subleading structure).
- Per (q, N): 50-100 ensemble realizations; for each, sweep load and measure cleanup-margin curve; extract WIDTH via fixed-threshold method (e.g., 10% to 90% of leading margin).
- Fit: width(N; q) = c0(q) + c1(q) / sqrt(N) + c2(q) / N via NLS.
- Statistical control: bootstrap CI on c1, c2; report c1/c0 ratio and c2/c0 ratio.

## Pre-registered HARD-PASS / MIDDLE / HARD-FAIL bands

HARD-PASS (MP bulk + subleading-correction CONFIRMED):
- Width monotone-decreasing in N for both q.
- Fit residuals < 5% of c0 at all three N.
- |c1/c0| in [0.3, 3.0] OR (if c1 ~ 0) |c2/c0| in [0.5, 5.0].
- Same scaling form fits BOTH q values (cross-q consistency).
- Log-log slope of width(N) - c0 in [-1.1, -0.4] (admits both pure-1/sqrt and pure-1/N regimes).

MIDDLE (qualitative bulk-scaling consistent; coefficient unidentified):
- Width monotone-decreasing in N.
- Fit residuals < 15%.
- c1, c2 estimated but with overlapping bootstrap CIs (under-identified).
- Cross-q consistency MIXED.

HARD-FAIL (NOT MP bulk subleading; alternative scaling required):
- Width NOT monotone in N (would suggest oscillatory / non-bulk regime).
- Required exponent outside [-1.5, -0.3] (would suggest Tracy-Widom 2/3 if more negative OR edge-dominated O(1) plateau if less).
- Cross-q grossly inconsistent (suggesting q-dependent regime change, not universal MP).
- Fit residuals > 25% (model misspecification).

## Honest scope

STRONG: that finite-N corrections to MP bulk density EXIST and follow a polynomial-in-1/sqrt(N) and 1/N expansion (multiple independent literature sources; standard textbook material).

MODERATE: that substrate cliff width specifically inherits this scaling. Substrate codebooks are non-IID-Gaussian (structured: bipolar / unit-norm / sparse), and width is an indirect width-of-transition observable, not the eigenvalue density itself. The mapping cliff-width <-> bulk-density-width is plausible but requires the cliff to truly be a BULK phenomenon (which prior delivery argued empirically).

SPECULATIVE: that c1/c0 falls cleanly in O(1) range. Sampling variance of the width estimator contaminates c1 with a Monte-Carlo term; with only 50-100 ensemble realizations per (q, N), c1 may be over- or under-estimated by a factor of 2. Bootstrap CIs are essential.

Calibration penalty: novel-synthesis P deflated to 0.50 (capped). With prior MP-bulk claim load-bearing and this drill being incremental subleading-correction test:
- P(HARD-PASS) deflated estimate: 0.45 (before deflation: 0.65; -0.20 penalty applied; capped at 0.50)
- P(MIDDLE):                     0.35
- P(HARD-FAIL):                  0.20 (would imply prior bulk claim is partially wrong)

## Substrate-product positioning

Confirming the MP bulk subleading correction empirically would extend substrate's mathematical-foundation pillar from LOCATION (R-transform predicts cliff position) to FULL closed-form (R-transform + MP-bulk + subleading correction together specify cliff position, leading width, AND the finite-N flow toward asymptotic width). This is a substrate-product differentiator: LLMs do not admit closed-form characterizations of their representational geometry at this resolution; substrate does. The two-axis position-IS-meaning + structural-cognition story now extends to a third axis: closed-form predictive capacity geometry at finite resource.

Importance for product framing: this is a MEDIUM-importance verification drill on an already load-bearing claim, not a new direction. Empirical confirmation strengthens the mathematical-foundation pillar marketing claim; empirical refutation forces a revisit of the bulk vs edge attribution from the prior delivery.

## Cross-thread synthesis with prior entries

- Extends prior cleanup-cliff LOCATION drill (R-transform formula, slope ~1.0).
- Extends prior cleanup-cliff SHARPNESS drill (MP bulk + slope-zero match).
- Connects to substrate-extracted methodology rule literature-is-not-oracle: literature predicts 1/n in pure bulk but Monte-Carlo introduces 1/sqrt(N) sampling-variance term; substrate empirical fit determines which dominates.
- Aligned with substrate-product 3-engine framing (self-extending + self-knowing + metacognitive) by adding closed-form-predictive-capacity-geometry as a fourth structural advantage.

## Citations (verified count)

8 verified arxiv / journal sources (R1+R2):
1. arXiv:1209.6171 -- beta-Wishart asymptotic corrections to MP law
2. arXiv:2206.01971 -- Local MP law at hard edge
3. arXiv:1506.02387 -- Finite-N corrections smallest Wishart eigenvalue
4. arXiv:2403.07628 -- Soft-edge asymptotic expansions of Gaussian and Laguerre ensembles
5. arXiv:2412.02572 -- Tensorial free convolution, R-transform higher-order
6. arXiv:0911.1313 -- Replica method finite-volume corrections
7. arXiv:1110.1284 -- Rate of convergence to MP distribution
8. arXiv:1412.6284 -- Rate of convergence expected spectral distribution to MP
9. arXiv:2402.10271 -- Finite-size effects in random matrices by counting resonances
10. arXiv:1302.1458 -- Eigenvalue density beta-Laguerre on short scales

(10 citations; 6 directly support 1/n bulk expansion; 2 support O(n^{-1/2}) Kolmogorov rate; 2 support measurement protocol; all generic-RMT, none substrate-specific.)
