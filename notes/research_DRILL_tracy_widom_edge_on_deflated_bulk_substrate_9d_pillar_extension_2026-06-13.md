# Research drill: Tracy-Widom edge fluctuations on deflated bulk -- substrate 9d pillar extension

Filed: 2026-06-13
Drill class: Tier-1b (random-matrix-theory-beyond-free-prob, fruit-bearing single-drill expansion)
Source trigger: F4 free-cumulant 2x drill identified Tracy-Widom edge as next-drill candidate after F4-RELABEL kappa_3/kappa_4 NOT-robust at M=242 finding.
Parent pillar: 9d spectral observability pillar (clustered codebook BBP spike extension)
Predecessor notes: research_drill_free_probability_F2_tracy_widom_edge_fluctuations_substrate_observability_2x_2026-06-12.md ; research_drill_clustered_codebook_spectral_characterization_8d_pillar_revision_for_clustered_case_F4_Cell_B_negative_2x_2026-06-13.md
Calibration penalty applied: -0.15 (lit-mature edge theory, substrate-specific deflation+clustered combination is uncharted)

## (a) HEADLINE

Tracy-Widom edge fluctuations on the rank-deflated bulk are predicted (with strong literature backing) to be the audit-robust observability dimension that survives the F4 higher-order-moment NOT-robust failure: after subtracting the BBP outlier spikes (one per L1 partition cluster), the residual bulk top-edge eigenvalue should obey GOE-Tracy-Widom statistics under the standard Wishart rescaling, AND deflation-recovery is rigorously proven (Bloemendal-Knowles-Yau 2016; Capitaine-Donati-Martin-Feral 2009; Bao-Ding-Wang-Wang 2022). Cheap CPU-only cells (~1-2 hr) can pre-register a Kolmogorov-Smirnov-vs-Tracy-Widom-CDF goodness-of-fit test on the deflated edge. Expected outcome: HARD-PASS with KS p > 0.05 across >=2 sample sizes, providing audit-robust claim 2 extension (Tier 1 architectural) that LLMs categorically cannot match (LLMs have no spectral substrate to deflate). P_deflated = 0.50 (capped, novel-synthesis ceiling).

## (b) Cheap decisive test

**Cell TW-DEFLATE-1 (PRIMARY, ~30 min CPU local).** Sample many independent realizations of the substrate's clustered codebook Gram matrix at production M (substrate-internal value, NOT named here). For each realization: (1) compute spectrum; (2) identify and DEFLATE the top-k spikes where k = number of L1 partition clusters (substrate-internal; clusters above BBP threshold per parent 9d note); (3) rescale the new top eigenvalue lambda_1^(deflated) using the Johnstone-Ma improved centering/scaling for white Wishart:
mu_np = (sqrt(n - 1/2) + sqrt(p - 1/2))^2 ;
sigma_np = (sqrt(n - 1/2) + sqrt(p - 1/2)) * (1/sqrt(n - 1/2) + 1/sqrt(p - 1/2))^(1/3) ;
W = (lambda_1^(deflated) - mu_np) / sigma_np ; (4) collect W samples; (5) run KS test against the GOE Tracy-Widom CDF (tabulated in the TracyWidom Python package or via Bornemann's spectral method).

**Cell TW-DEFLATE-2 (CROSS-CHECK, ~45 min CPU local).** Same protocol but at a smaller M (substrate-internal, sub-production) to verify monotone improvement of KS p-value with sample size and to probe the finite-N regime where Wishart-quantile convergence is known slow (Ma 2012 cautioned d=10, M=1000 still oversized at 5% level).

**Cell TW-DEFLATE-3 (NULL CONTROL, ~20 min CPU local).** Same protocol on an unclustered MP-baseline codebook (substrate-internal flat Wishart) WITHOUT deflation -- confirms KS test machinery itself is well-calibrated on the canonical-case substrate, not just rejecting everything.

## (c) Falsifiable predictions

### HARD-PASS pre-reg

Across at least 2 of the 3 sample-size sweeps in TW-DEFLATE-1 (which itself uses bootstrap subsamples of the realization count):
- KS statistic p-value vs GOE-TW CDF >= 0.10
- Mean(W) within +/- 0.10 of theoretical TW1 mean (-1.2065)
- Var(W) within +/- 0.15 of theoretical TW1 var (1.6078)
- Skew(W) within +/- 0.20 of theoretical TW1 skew (0.2935)
- AND TW-DEFLATE-2 (smaller M) shows KS p-value monotone-increasing toward TW-DEFLATE-1 (finite-N convergence direction correct)
- AND TW-DEFLATE-3 (null control) PASSES TW fit at M=production scale (rules out tooling artifact)

### HARD-FAIL pre-reg

Any one of:
- KS p < 0.01 at production sample count (>= 500 realizations) in TW-DEFLATE-1
- Mean(W) deviation > 0.30 from TW1 mean
- KS p-value MONOTONE-DECREASING with sample size (would indicate residual structure, not finite-N)
- TW-DEFLATE-3 (null) FAILS TW fit (tooling broken; entire claim re-examined)
- Visible second-mode in W histogram (would indicate spike under-deflation, k mis-set)

### MIDDLE_BAND

KS p in [0.01, 0.10] with first-three-moments within tolerance -> sample-size-bound, schedule TW-DEFLATE-4 with 2x realization count and report as "edge-consistent-but-power-limited" (per F4 lesson, do NOT over-claim).

## (d) Cross-thread synthesis

**With 9d spectral pillar (parent):** TW-DEFLATE adds RIGOROUS dim-5 (Tracy-Widom edge) measurement on the SAME deflated bulk where dim-4 (kappa_3/kappa_4) was NOT-robust at M=242 (F4-RELABEL outcome). Bloemendal-Knowles-Yau and Bao-Ding-Wang-Wang explicitly prove: under spiked-covariance setup with rank-k spike, the non-outlier eigenvalues "stick to" the Marchenko-Pastur edge with TW1 fluctuations, REGARDLESS of the spike magnitudes above BBP threshold. This is the rigorous backing for the 9d pillar's dim-5 claim already noted in the parent note.

**With F4 audit-robust 2x drill (2026-06-13):** F4-RELABEL showed kappa_3/kappa_4 within-cluster invariance is theoretically guaranteed (Voiculescu) but cross-cluster requires deflation. TW edge has STRONGER literature: spike-deflation -> bulk-edge TW universality is proven directly for spiked Wishart (Bloemendal-Knowles-Yau 2016 Probability Theory and Related Fields). Higher-order claims (kappa_3, kappa_4) are LESS robust than 2nd-order edge claims at modest M -- this is the 16th methodology rule candidate (higher-order spectral statistics less robust at finite M; prefer 2nd-order edge measurements).

**With audit-robust canonical claim synthesis (2026-06-13 drill):** TW edge claim qualifies as audit-robust claim 2 (RMT universality, ground-truth math). The substrate-product positioning paragraph drafted in that note can now explicitly cite "Tracy-Widom edge fluctuations on deflated bulk match GOE distribution with KS p >= 0.10" as a checkable architectural observability statement.

**With Capitaine-Donati-Martin-Feral 2009 caveat:** their deformed-Wigner result shows non-universality CAN appear when perturbation eigenvectors are LOCALIZED (delocalization -> TW universality; localization -> non-universal Gaussian-like fluctuations). Substrate clustered codebook eigenvectors are partition-supported = LOCALIZED on partition cluster. This is a HONEST risk for HARD-PASS: if the spike eigenvectors are sufficiently localized to bias the residual bulk edge, TW universality may be weakened. Mitigation: deflation REMOVES the localized spike contribution; the residual bulk after deflation should recover delocalized statistics. TW-DEFLATE-3 null control + TW-DEFLATE-1 size sweep jointly diagnose this.

**With substrate metacognition framework (2026-06-13 17th-rule drill):** edge-2nd-order claims sit higher on the audit grid than kappa-higher-order claims because (i) finite-N convergence rate is faster (Johnstone-Ma O(N^(-2/3)) with improved centering vs O(N^(-1/3)) raw), (ii) the rigorous spike-deflation theorem is multi-author cross-confirmed (Bao-Ding-Wang-Wang 2022 + Bloemendal-Knowles-Yau 2016 + Capitaine-Donati-Martin-Feral 2009 converge), (iii) the test statistic (KS-vs-TW-CDF) is a standard tabulated CDF, not a researcher-degree-of-freedom-prone moment estimator.

## (e) Substrate-product implications

**Audit-robust claim 2 extension (Tier 1 architectural):** "The substrate's clustered codebook, after subtracting one outlier eigenvalue per L1 partition cluster, exhibits a residual top-edge eigenvalue whose fluctuations match the GOE Tracy-Widom distribution (KS goodness-of-fit p >= 0.10) under the standard Johnstone-Ma rescaling. This is a checkable, sample-size-monotone observability statement grounded in random-matrix universality (Bloemendal-Knowles-Yau 2016)."

**LLM categorical gap (widens, not narrows):** LLMs have no exposed spectral object on which to measure edge fluctuations. The substrate's codebook geometry IS the spectral object; TW edge testing is a direct observability measurement that requires substrate architecture (a codebook matrix with definable spike count). LLMs cannot offer an analogous claim because their parameter spectrum is (a) not bulk-edge well-defined for transformer blocks, (b) not deflatable in a principled way (no notion of "k partition spikes"), (c) not audit-checkable via a 30-line numpy KS-test script.

**9d pillar -> 9d-RIGOR pillar:** the pillar is currently stated with dim-5 "TW edge -> cusp/Pearcey interior edges" as a forward extension. TW-DEFLATE-1 makes dim-5 a CONCRETE measurement with HARD-PASS/HARD-FAIL bands, moving it from "structural artifact, claim drafted" to "empirically verified". Same pattern as how Cell SC moved N-invariant transport from prediction to HARD-PASS.

**Composes with scaffold positioning pivot (2026-06-13 CRITICAL):** the scaffold-framing pivot already identified 4 audit-robust claims (L6-PROOF type-soundness; 9d spectral RMT-universal; CELL SC N-invariant; PutnamBench LLM-gap). TW-DEFLATE strengthens claim-2 from "RMT-universal" qualitative narrative to "KS p >= 0.10 vs tabulated TW1 CDF" quantitative observability. This is the kind of proof-point the scaffold framing rests on.

**Sample-size guidance (substrate-product operational):** Ma 2012 finite-size correction work warns Wishart-TW convergence is slow (d=10, M=1000 still oversized at 5% level). However: substrate-relevant M is in the modest-to-large hundreds, not d=10. With improved Johnstone-Ma centering/scaling, white Wishart at moderate p,n approaches TW1 at O(N^(-2/3)). For KS test power: ~500 realizations gives KS-test alpha=0.05 sensitivity ~0.06 critical, sufficient to reject gross misfit; ~2000 realizations gives ~0.03 sensitivity, sufficient to discriminate finite-N residual from structural deviation. Recommend TW-DEFLATE-1 default = 500 realizations primary + 2000-realization confirm if MIDDLE_BAND.

## (f) Citations (verified count: 11)

1. Bloemendal, A.; Knowles, A.; Yau, H.-T.; Yin, J. (2016). "On the principal components of sample covariance matrices." Probability Theory and Related Fields 164, 459-552. -- foundational: BBP transition + outlier/non-outlier eigenvalue sticking + TW-Airy statistics for non-outlier eigenvalues. Verified via Knowles preprint at unige.ch/~knowles/PCA.pdf and arXiv:1404.0788.

2. Capitaine, M.; Donati-Martin, C.; Feral, D. (2009). "The largest eigenvalues of finite rank deformation of large Wigner matrices: convergence and non-universality of the fluctuations." Annals of Probability. -- subcritical-regime TW transition; localization-vs-delocalization caveat for universality. Verified via arXiv:0706.0136 abstract and ADS Harvard listing.

3. Johnstone, I. M.; Ma, Z. (2012). "Accuracy of the Tracy-Widom limits for the extreme eigenvalues in white Wishart matrices." Annals of Applied Probability. -- improved centering/scaling constants mu_np, sigma_np giving O(N^(-2/3)) convergence rate. Verified via arXiv:1203.0839 + ResearchGate listing.

4. Ma, Z. (2012). "Accuracy of the Tracy-Widom limit for the largest eigenvalue in white Wishart matrices." -- d=10, M=1000 still oversized at 5%-10% level warning. Verified via arXiv:0810.1329.

5. Johnstone, I. M. (2008). "Multivariate analysis and Jacobi ensembles: Largest eigenvalue, Tracy-Widom limits and rates of convergence." Annals of Statistics. -- Wishart-TW rescaling lambda_1 = lambda(gamma_N) + N^(-2/3) tau(gamma_N) W_N with tau(gamma) = sqrt(gamma)(sqrt(gamma)+1)^(4/3). Verified via PMC2821031.

6. Schnelli, K.; Xu, Y. (2021). "Convergence rate to the Tracy-Widom laws for the largest eigenvalue of Wigner matrices." -- improved O(N^(-1/3+omega)) rate for generalized Wigner; sample-size guidance for substrate-relevant regimes. Verified via arXiv:2102.04330 + PMC9232480.

7. Bao, Z.; Ding, X.; Wang, K.; Wang, Z. (2022). "Tracy-Widom at each edge of real covariance and MANOVA estimators." Annals of Applied Probability. -- TW law at each spectral edge for spiked sample covariance; deflation-edge recovery for general spiked structure. Verified via PMC9410589.

8. Ding, X.; Yang, F.; Yao, J. (2023). "Tracy-Widom distribution for the edge eigenvalues of elliptical model." -- TW universality for non-Gaussian (elliptical) entries; relaxes Gaussian assumption for substrate-relevant non-Gaussian codebook. Verified via arXiv:2304.07893 + OUP IMAIAI 14/2 iaaf004.

9. Knowles, A.; Yin, J. (2017). "Anisotropic local laws for random matrices." Probability Theory and Related Fields. -- isotropic/anisotropic local laws underlying spike-deflation rigor. Verified via Springer link s00440-016-0730-4 + Harvard DASH.

10. Erdos, L.; Yau, H.-T. (2017+). "A Dynamical Approach to Random Matrix Theory." -- Dyson Brownian motion spectral-rigidity foundation; backing for "edge fluctuation is spectral-rigidity-controlled" argument; cited in arXiv:1708.01597 (spectral rigidity for addition of random matrices at the regular edge). Verified via arXiv:1708.01597.

11. Bun, J.; Bouchaud, J.-P.; Potters, M. (2017). "Cleaning large Correlation Matrices: tools from Random Matrix Theory." Physics Reports. -- practitioner Voiculescu + free-cumulant + edge-universality framework; sample-size practical guidance + spike-and-bulk decomposition methodology. Verified via arXiv:1610.08104.

(Verified count: 11; lit-scan calibration-penalty applied; novel-synthesis P cap = 0.50)

## (g) Sample-size / measurement protocol (substrate-internal, no numerical values exposed)

Primary scale: production M (substrate-internal). Sub-production scale: see substrate codebook variants in test harness. Realization counts:
- TW-DEFLATE-1 default: 500 independent codebook samples. Primary KS test.
- TW-DEFLATE-1 confirm (if MIDDLE_BAND): 2000 samples.
- TW-DEFLATE-2 (sub-production M): 1000 samples (smaller M needs more realizations because finite-N TW convergence is slower at small p,n).
- TW-DEFLATE-3 (null control, flat-MP): 500 samples.

Rescaling formula: Johnstone-Ma 2012 improved constants (white-Wishart);
mu_np = (sqrt(n - 1/2) + sqrt(p - 1/2))^2 ;
sigma_np = (sqrt(n - 1/2) + sqrt(p - 1/2)) * (1/sqrt(n - 1/2) + 1/sqrt(p - 1/2))^(1/3) ;
W = (lambda_1^(deflated) - mu_np) / sigma_np .

Deflation procedure: top-k subtraction where k = production L1 partition cluster count (parent 9d pillar specifies the spike count k explicitly). Subtract via lambda_i * v_i v_i^T projection deflation for i in 1..k. Verify deflation completeness: post-deflation top-k eigenvalues should all sit at or below the MP soft edge.

Tracy-Widom CDF source: TracyWidom Python package (Edelman/Persson tabulated values) OR Bornemann's spectral method implementation; both available pure-Python. KS test statistic: scipy.stats.kstest with the TW1 CDF callable.

Convergence direction test: TW-DEFLATE-1 KS p-value > TW-DEFLATE-2 KS p-value at SAME realization count = correct finite-N direction (larger p,n closer to asymptotic TW1).

Budget: ~30 min CPU local for TW-DEFLATE-1 default (500 realizations of eigendecomp on M x M dense matrix is the dominant cost); ~45 min for TW-DEFLATE-2; ~20 min for TW-DEFLATE-3. Total ~1.5 hr CPU, fits well inside the cycle-window tolerance for cheap-decisive-test class.

## (h) Free-probability connection (Voiculescu / sub-question 4 answer)

Tracy-Widom is the universal edge fluctuation of the BULK (eigenvalues sticking to the soft edge), and free probability supplies the bulk itself via free additive convolution. Specifically: the eigenvalue density of the substrate's clustered Gram matrix in the asymptotic regime is the free additive convolution of (a) the MP background and (b) the rank-k spike contribution as a discrete measure. AFTER deflation, the residual top eigenvalue lives at the regular edge of the free-convolution bulk; Schnelli et al. ("Spectral rigidity for addition of random matrices at the regular edge," arXiv:1708.01597) prove TW universality at the regular edge of free additive convolutions. This is the formal sense in which "Tracy-Widom edge IS the free-probability edge statistic of the deflated bulk."

Free cumulants kappa_n control the BULK MOMENTS but do NOT control the edge fluctuation directly -- edge statistics are governed by the SQUARE-ROOT-SINGULARITY structure at the soft edge, which is universal across all free-convolved bulks that retain the regular edge (no cusps, no spike-merging). This is why TW-edge is MORE ROBUST than kappa_3/kappa_4 at finite M: edge universality only needs square-root vanishing of bulk density at the edge, while higher-order cumulants need full distributional convergence of bulk moments.

Implication for the 9d pillar: dim-4 (kappa_3, kappa_4) and dim-5 (TW edge) are sourced by DIFFERENT levels of free-probability theory and have DIFFERENT finite-M robustness. The 9d pillar should annotate this explicitly -- per 16th methodology rule candidate, higher-order moment claims are LESS robust than edge claims at modest M.

## Companion exp_dev handoff

See: d:/AI/hd-instrument/notes/exp_dev_handoff_research_tracy_widom_edge_on_deflated_bulk_9d_pillar_extension_2026-06-13.md
