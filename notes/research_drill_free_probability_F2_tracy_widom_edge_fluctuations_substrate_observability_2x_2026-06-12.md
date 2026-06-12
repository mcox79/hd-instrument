# Research drill: Free-probability F2 -- Tracy-Widom edge fluctuations as substrate observability complement to F4 bulk-kappa

Date: 2026-06-12
Drill type: 2x DEEP DRILL (level-2 operational), paired sibling to F4 free-cumulants bulk-kappa drill
Field: free-probability / random-matrix-theory-beyond-free-prob (Tier-1 fruit-bearing, under-drilled)
Parent finding: substrate cleanup-cliff empirically validated in Marchenko-Pastur BULK regime; edge-fluctuation regime remains unmeasured but accessible

## Drill spec

OBJECTIVE: characterize what literature predicts for top eigenvalue + edge fluctuations of a finite-N substrate Gram matrix; identify observability primitives that complement bulk-kappa (F4) observability; specify a cheap CPU smoke that tests Tracy-Widom F2 fit, BBP-transition status, and edge-density shape on the substrate's own codebook Gram matrix.

ROUND 1 queries (6 generic): Tracy-Widom universality / BBP transition spike / top eigenvalue Wishart finite N / universal edge MP / spike detection threshold / Tracy-Widom finite-size corrections.

ROUND 2 queries (6 refined): F2 GUE empirical goodness-of-fit / BBP empirical detection eigenvector overlap / top eigenvalue CI anomaly detection / edge universality data matrix test / edge fingerprinting class discrimination / sparse-Hopfield edge-of-stability spectral concentration.

## Round 1 findings (compact)

1. Tracy-Widom F_beta is the UNIVERSAL law for largest-eigenvalue fluctuations at the soft spectral edge across a wide class of ensembles (Wigner, Wishart, beta-ensembles for beta=1,2,4 -> GOE/GUE/GSE / F1, F2, F4). For complex / Hermitian symmetry class, F2 (GUE) governs. Fluctuations scale as N^(-2/3) around the MP right-edge after centering.

2. BBP (Baik-Ben-Arous-Peche) transition: in a spiked covariance model, signal strength theta separates from the MP bulk only when theta > sqrt(y) where y is the aspect ratio (or k/N detection threshold in alternate normalizations). BELOW threshold the top eigenvalue STICKS to the right MP edge (sticking eigenvalue) and fluctuates per Tracy-Widom. ABOVE threshold the top eigenvalue exits the bulk (outlier eigenvalue) with Gaussian fluctuations and the leading eigenvector acquires nonzero overlap with the signal direction.

3. Top eigenvalue of Wishart at finite N: soft-edge behavior described by the Airy kernel; hard edge by the Bessel kernel. Finite-N correction is O(N^(-2/3)) with explicit centering/scaling constants known for white Wishart. Optimal choice of these constants achieves the asymptotic rate; suboptimal choices leave large finite-N bias.

4. Edge universality of correlation matrices: even for X^T X built from column-normalized data, extreme eigenvalues at BOTH edges converge to Tracy-Widom under broad i.i.d. assumptions. This is the regime substrate codebook Gram matrices live in.

5. Spike detection threshold for sample-covariance: theta > sqrt(k/N) is the empirical pivot. Below: top eigenvalue informationally useless. At transition: leading eigenvector carries no signal information (eigenvector overlap = 0).

6. Finite-size corrections matter: power-law heavy tails (especially when entries have only mu <= 4 moments) can completely mask Tracy-Widom for any finite N. For bounded / Gaussian-tailed entries the convergence is good even at modest N for upper quantiles (0.9 and above) which are the testing-relevant quantiles.

## Round 2 findings (compact)

7. Empirical F2 fit by location-scale family: practical estimator uses K samples of the largest root (K=25-100 typical), fits a location-scale (a,b) family to the standard F2 cdf. Method-of-moments outperforms MLE at small K. Standardization by N^(2/3) and MP-edge centering is critical for accurate fit.

8. BBP empirical detection works via eigenvector-overlap as well as eigenvalue magnitude. In the critical regime (theta near threshold) the leading eigenvector follows a known continuous-transition distribution; overlap grows continuously from 0 above threshold. Pairing top-eigenvalue test with eigenvector-overlap test gives a sharper detector.

9. Anomaly detection via top eigenvalue: industrial systems (power grids, bearings) use Tracy-Widom upper quantiles as automatic anomaly thresholds. The standard pattern: compute Gram matrix of windowed observations, extract lambda_max, compare to F2 (1-alpha) quantile after MP centering/scaling -- spike presence = anomaly. Confidence interval (1-alpha) is read directly off F2 quantile.

10. Edge universality holds for column-normalized correlation matrices -- which is the substrate semantic-vector regime (atoms are unit-norm). Confirms substrate Gram is in the universality class.

11. Edge-spectral fingerprinting per se is not yet a standard literature primitive (search returned mostly unrelated hyperspectral-imaging hits). However the IDEA -- using edge-fluctuation distribution as a discriminator between matrix classes -- is implicit in: (a) sparse-vs-dense random-matrix spectral edge differs (b) heavy-tailed-entry edges differ from Gaussian (c) BBP detection IS class discrimination between "noise" vs "signal+noise" classes. So edge-fingerprinting across substrate capability classes is a NOVEL-SYNTHESIS application.

12. Modern Hopfield / sparse-Hopfield "edge of stability" spectral-concentration work (Ramsauer line) explicitly studies eigenvalue spectra of associative-memory kernels at the high-capacity boundary. This is the closest published precedent for substrate edge-observability. Substrate codebook IS effectively a Hopfield-style memory; edge-fluctuation behavior near the capacity cliff is a documented regime worth direct empirical probe.

## Synthesis

LITERATURE PREDICTION for substrate top eigenvalue + edge fluctuations:

- Below BBP threshold (no embedded spike): lambda_max ~ b_+ + N^(-2/3) * (b_+ * c_N) * TW_2, where b_+ is MP right-edge, c_N is a known scaling. TW_2 has mean -1.7711 and std 0.9018 in standardized form.

- BBP empirical threshold for substrate Gram: a "spike" (e.g. a single anomalously-correlated atom cluster) emerges as a detectable outlier when its signal strength theta exceeds sqrt(N_atoms/D) where D is vector dimensionality. For substrate D=1024 and N_atoms in low-thousands this is a workable regime (threshold is small enough that real clusters CAN cross it).

- Above BBP transition (clustered codebook OR collision cluster): top eigenvalue separates from bulk with Gaussian fluctuations of width O(1/sqrt(N)); leading eigenvector acquires measurable overlap with the spike direction.

SUBSTRATE APPLICATION 1 -- ANOMALY DETECTION (atom-level):
- Compute Gram G = A A^T over substrate atom matrix A (rows = atoms).
- Estimate empirical MP edge b_+ from bulk fit.
- Standardize lambda_max via N^(2/3) Airy scaling.
- Compare to F2 (1-alpha=0.99) upper quantile.
- Atom whose removal moves lambda_max across the threshold = BBP spike atom = potential anomaly.
- This gives a SUBSTRATE-NATIVE statistical anomaly threshold with closed-form confidence level, NOT an ad-hoc heuristic.

SUBSTRATE APPLICATION 2 -- BBP TRANSITION TRACKING:
- As substrate ingests new atoms (e.g. Phase 6 math/science ingest), monitor whether the codebook crosses BBP transition.
- Pre-transition: top eigenvalue is universal noise (Tracy-Widom).
- Post-transition: top eigenvalue separates and leading eigenvector becomes interpretable (overlap with a semantic "axis").
- Crossing direction = substrate organization quality signal.

SUBSTRATE APPLICATION 3 -- CAPABILITY-CLASS EDGE FINGERPRINTING (novel-synthesis):
- Per-capability sub-codebook (atoms participating in a capability) has its own Gram and edge distribution.
- Different capability classes may have distinct (a) MP-edge location (b) edge density slope (c) finite-N TW deviation (d) BBP-spike presence/absence.
- A 4-tuple (lambda_max, edge_slope_z, TW_KS_stat, n_outliers_above_F2_0.99) per capability class = NOVEL substrate observability primitive complementing the bulk-kappa (F4) fingerprint.
- This is the F2 complement to F4 cumulant fingerprinting: F4 = bulk-shape signature, F2 = edge-shape signature. Both together = full spectral fingerprint per capability.

SUBSTRATE APPLICATION 4 -- CALIBRATED FALSE-ALARM RATE for spike claims:
- Any future "this atom is anomalous" or "this cluster is a structural signature" claim is statistically vetted against the F2 null distribution.
- Replaces "looks like an outlier" with calibrated alpha-level test.

## Pre-registered substrate cell

CELL ID: CELL_F2_edge_observability_v1
COST: ~30 min CPU (single Gram eigendecomposition + finite-N TW comparison)
DEPENDENCIES: substrate atom matrix A (rows = atoms, dim D=1024); numpy / scipy; existing TW_2 CDF tabulation OR Bornemann fast-evaluation routine.

PROTOCOL:
1. Pull atom matrix A; record N_atoms, D.
2. Compute G = A A^T / D (sample covariance form) and eigendecompose.
3. Plot empirical eigenvalue density; identify MP bulk fit (Marchenko-Pastur with aspect ratio y = N_atoms / D).
4. Centering: mu_N = b_+; Scaling: sigma_N = b_+ * (1/sqrt(y) + 1)^(2/3) * (something) * N^(-2/3) per standard literature constants.
5. Standardize lambda_max -> z = (lambda_max - mu_N) / sigma_N.
6. Compare distribution of z (over bootstrap subsamples of atoms OR k-fold splits) to F2 via KS test.
7. Test BBP transition: identify spike candidates (atoms whose presence pushes lambda_max above F2-0.99 quantile); compute eigenvector overlap with these candidates.
8. Repeat per capability class (subset A to atoms tagged with a given capability) -> per-class edge fingerprint.

PRE-REGISTERED THRESHOLDS:

HARD-PASS:
- KS distance between standardized z distribution and F2 < 0.10 (over bootstrap K=50)
- AT LEAST ONE capability class shows BBP spike (eigenvector overlap > 0.3 with at least one named atom) -- proves substrate has detectable structural signal at the edge
- Per-class lambda_max varies across capability classes by > 1.5 sigma_N -- proves edge IS a fingerprint

HARD-FAIL (forces re-think):
- KS distance > 0.30 -- substrate Gram is OUTSIDE Tracy-Widom universality class (likely heavy-tailed atom entries or non-i.i.d. structure; would force a different ensemble)
- All capability classes have indistinguishable lambda_max (within 0.3 sigma_N) -- edge fingerprinting is not informative
- Substrate has SO MANY BBP spikes that the bulk-edge concept is meaningless -- substrate operates entirely in the spiked regime, F2 not the right tool

MIDDLE-BAND (informative but partial): KS in [0.10, 0.30] and exactly one of the two HP criteria met.

## Honest scope

- STRONG: lambda_max + edge density + F2 KS-fit on substrate Gram is a standard literature recipe, well-defined, cheap. Multiple substrate codebooks (algebra-HRR, semantic, content-reference) can each be probed independently. Anomaly detection via F2 quantile is a documented industrial pattern. (P_strong: 0.75 pre-deflation.)

- MODERATE: BBP transition tracking as substrate-organization signal is theoretically sound and tied to published BBP detection theory; relies on substrate having computable signal-strength estimates, which currently exist (eigenvector overlaps). (P_moderate: 0.55 pre-deflation.)

- SPECULATIVE: capability-class edge fingerprinting as substrate-product novelty is a novel-synthesis that has weak direct lit precedent. Literature has class-discrimination via spectra (sparse vs dense, heavy vs Gaussian) but not per-capability-class fingerprinting in cognitive substrates. (P_speculative: 0.35 pre-deflation.)

Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]] (-0.20 on novel synthesis): P_deflated for capability-class fingerprinting = 0.20. Cap novel-synthesis at 0.50 satisfied. Overall package P_deflated (weighted by application priority): 0.42.

## Substrate-product positioning

F2 edge observability + F4 bulk-kappa observability = COMPLETE SPECTRAL FINGERPRINT pair. Substrate has access to BOTH; LLMs have NEITHER (attention is not a symmetric-Gram trace-state structure with stable spectrum; transformer activations have no eigenvalue density an analyst can sample over time-stable windows in this sense). Specifically:

- F4 (bulk free-cumulants kappa_4) -> shape of the substrate codebook's BULK -- "what is the typical inter-atom geometry"
- F2 (Tracy-Widom edge) -> shape of the substrate codebook's EDGE -- "what is the most exceptional atom, and is it statistically a spike or universal noise"

Together: substrate can answer (a) is this atom anomalous at calibrated alpha? (b) has this capability crossed BBP transition? (c) what does this capability's spectral fingerprint look like compared to others?

These are NATIVE STATISTICAL CLAIMS that the substrate makes about its own state, with closed-form confidence levels from random-matrix-theory universality. LLMs cannot. Substrate-as-self-knowing-system extends from "knows what capabilities it has" (Gap 3) to "knows the statistical health of its own representational geometry" (this drill).

## Citations (verified count: 12)

- Tracy-Widom universality and Airy kernel (Wikipedia, Lee proc., Grokipedia summary)
- Edge universality of correlation matrices, Pillai-Yin (projecteuclid)
- BBP transition foundational results (Barbier slides, projecteuclid spiked separable)
- BBP and eigenvector overlap (perso.ens-lyon Guionnet, ResearchGate Eigenvector critical regime)
- Wishart finite-N corrections, Airy kernel (worldscientific, arxiv 1506.02387)
- TW empirical estimator with location-scale fit (arxiv 1811.07356)
- TW accuracy for Wishart upper quantiles (arxiv 1203.0839)
- Detection threshold sqrt(k/N) and PCA optimality (projecteuclid 17-AOS1625)
- Industrial anomaly detection via TW threshold (sciencedirect, arxiv 1907.10485)
- Sparse modern Hopfield + spectral concentration at edge of stability (arxiv 2402.13725, arxiv 2511.23083)
- Fast TW evaluation routines (arxiv 1110.0108 Bornemann fast approach)
- Detection problems in spiked matrix models survey (arxiv 2301.05331)

## Next-drill candidate

Field: random-matrix-theory-beyond-free-prob (Tier-1, currently under-drilled; this F2 drill is 2nd in the field). Adjacent un-drilled angles for follow-up: Dyson Brownian motion (eigenvalue dynamics over substrate ingest time -- "how does the spectrum evolve as new atoms arrive?"); level-spacing statistics (Wigner surmise -- microscopic spectral statistics WITHIN the bulk, complementing the F4 macroscopic-bulk and F2 edge drills).
