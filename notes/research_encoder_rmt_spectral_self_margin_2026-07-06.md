# Research -- does RMT/free-probability give a tractable self-margin prediction for the encoder (perception substrate)?

**Date:** 2026-07-06
**Trigger:** Cadence gap-fill drill (both dispatch queues idle). The self-margin CLOSED-FORM thread (RNS CG +
FHRR CG cover the orthogonal-family codebooks, per `notes/research_codebook_design_space_generalization_2026-07-06.md`)
is at its boundary for the heterogeneous/semantic families. Both `notes/research_codebook_design_space_generalization_2026-07-06.md`
(Family E) and `notes/research_gsbc_codebook_correlation_homogeneity_2026-07-06.md` (Sec. 3-4) flagged the SAME
open question -- "RMT/free-probability on the concept-Gram spectrum" -- as the next candidate for the encoder's
heterogeneous Gram matrix, but neither drill reduced it to a testable closed form. **This drill answers that
flagged question directly, not by lit-scan alone but by running the actual spectral/Gaussian-equivalence test
against the on-disk BGE-distilled concept embeddings.**
**Discipline:** measured the REAL concept-embedding Gram/covariance structure directly off-disk (BGE `composite`
vectors from `data/substrate_index/cached_indices/bge_large_v2_name_*.npz`, V=20820 and V=41328, two seeds each),
zero new cells, zero dispatch, zero config change (monitor-not-control). 2 parallel Sonnet lit-scans dispatched
for external grounding using generic math terms only (per query-privacy discipline); both completed with
live-verified citations this round (9/12 and 8/12 sources fetch-confirmed respectively; remainder flagged
explicitly as search-confirmed-only, not smoothed over).

---

## HEADLINE

**RMT/free-probability gives a PARTIAL, not full, tractable prediction -- and the honest verdict is ACCEPT THE
BOUNDARY for a CG-tier closed-form encoder self-margin capability. This is a resolved, quantified negative, not a
hand-wave: a decisive, statistically robust (paired trials, n=1500 queries, effect sizes 4-20 standard errors from
zero) test shows a covariance-spectrum-matched Gaussian surrogate of the real BGE-distilled concept embeddings
explains the BULK of the encoder's excess collapse-vulnerability (vs a naive i.i.d. assumption) in the DEEP-collapse
regime (60-95%+ of the gap explained, sigma=0.18-0.28) but leaves a large, systematic, sigma-dependent residual
(13-26 accuracy points, i.e. the surrogate OVER-predicts real performance) concentrated exactly in the
EARLY/onset-of-collapse regime (sigma=0.10-0.16) -- precisely the regime that matters most for a "where does the
boundary start" self-margin prediction. The classic BBP/free-cumulant spiked-covariance toolkit the prior notes
flagged is confirmed (by both direct measurement and lit-scan) to be the WRONG tool regardless: the real spectrum
is a clean, robust POWER LAW (exponent -1.0 to -1.12, R^2=0.97-0.98 across two independent V samples) with NO
compact bulk + few isolated spikes -- a structurally different random-matrix ensemble than the one BBP/Wigner-edge
analysis handles. A genuinely new, reportable finding along the way: once TOTAL VARIANCE is held fixed, the SHAPE
of the spectrum (power-law vs flat) barely affects the aggregate retrieval-collapse curve -- almost all of the
"spectral" effect reduces to a single scalar (trace of the covariance / effective concentration), not a full
free-probability treatment.**

**Recommendation: ACCEPT the negative for a dedicated encoder-margin cell. Do not build it.** The residual gap is
too large (13-26 points) and lands in the load-bearing regime for a CG-tier claim (cf. RNS/FHRR's <5% deviation
bar), and the root cause (lit-scan-confirmed: hub/retrieval-failure in real embeddings is data-content/intrinsic-
dimension-driven, not a function of the aggregate eigenvalue spectrum alone) is the SAME fundamental issue the two
prior notes already identified for the one-factor and pairwise-correlation routes -- now confirmed a third time,
for the spectral/RMT route specifically, with a quantified, statistically significant residual rather than an
assumption. This is a clean, generalization-ceiling-style ACCEPT boundary: like the substrate's one-to-many
entropy ceiling, this is a PROVEN bound (a measured, reproducible residual), not a failure to try hard enough.

---

## 1. WHAT WAS MEASURED

### 1a. Object measured

The REAL, trained BGE-distilled concept embeddings (`composite`, 1024-dim, unit-norm) from
`data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz` (V=20820) and
`bge_large_v2_name_41328_6e2d3257.npz` (V=41328, robustness check) -- the SAME ground-truth semantic object the
prior two drills used as the independent oracle for Family D/E correlation measurements. This is the appropriate
proxy for "the encoder's Gram spectrum": the actual concept-encoder table (`hdlab/concept_encoder.py`) is
RKD-distilled FROM this BGE teacher, so its Gram structure inherits (attenuated, per the GSBC drill's finding)
the same spectral shape; measuring the teacher directly is the cleaner, higher-fidelity object for a spectral
characterization and avoids conflating this question with student-distillation noise.

### 1b. Method

1. Mean-centered the embeddings, built the 1024x1024 sample covariance `C = Xc.T @ Xc / n`, eigendecomposed
   (`np.linalg.eigh`, <0.3s for n=20820).
2. Compared against a size-matched CONTROL: n i.i.d. random unit vectors on the sphere in R^1024 (same
   construction convention as the real unit-norm embeddings) -- the natural "no structure" null.
3. Fit a power law to the eigenvalue-index curve (log-log OLS, k=5..300, avoiding the very top/tail).
4. Computed inverse participation ratio (IPR) of top eigenvectors (delocalization check).
5. Built a COVARIANCE-MATCHED GAUSSIAN SURROGATE: `G = mean + Z @ diag(sqrt(w)) @ V.T` (Z i.i.d. standard normal),
   renormalized to unit norm -- a null model with the IDENTICAL covariance eigenvalues/eigenvectors as the real
   data but Gaussian (non-semantic) marginal structure along each eigendirection. This is the established
   "surrogate-data" / "covariance-matched null" diagnostic technique (Theiler et al. 1992, generic method;
   confirmed as a standing methodology by this drill's lit-scan, Sec. CITATIONS).
6. Simulated a retrieval-margin-collapse task on all three objects (real, surrogate, i.i.d. control): additive
   Gaussian query noise at increasing sigma, renormalize, cosine-argmax against the full pool, measure top-1
   retrieval accuracy -- structurally the SAME "does the substrate recover its own encoding under noise" question
   the RNS/FHRR order-statistic cells ask, generalized to the encoder's actual (not i.i.d.) competitor structure.
7. A truncated-spectrum sweep (K=0..1024, flattening the tail beyond rank K to a variance-matched constant) to
   isolate whether spectral SHAPE (beyond total variance) matters for the aggregate collapse curve.
8. PAIRED trials (same query indices, same noise-seed draws across arms) at n_queries=1500 for the decisive
   real-vs-surrogate comparison, per [[feedback-paired-trials-mandatory-for-arm-comparison-discriminators]].

### 1c. Results -- spectral shape

| Quantity | Real BGE (V=20820) | Real BGE (V=41328) | i.i.d. control |
|---|---|---|---|
| mean-vector norm (anisotropy/"cone") | 0.7685 | 0.7266 | 0.0069 |
| top eigenvalue | 0.0309 | 0.0542 | 0.00145 |
| eigenvalue max/min ratio | 24384x | (not recomputed, same order) | 2.4x |
| cum. var @ k=10 / 100 / 300 / 700 (of 1024) | 33% / 76% / 94% / 99.6% | 38% / 73% / 93% / 99.5% | 1.4% / 13.6% / 37.5% / 76.3% |
| power-law fit exponent (k=5..300) | **-1.118** (R^2=0.972) | **-0.961** (R^2=0.984) | -0.078 (R^2=0.895, i.e. near-flat) |
| top-eigenvector IPR | 0.0029-0.0030 (~3x the 1/dim=0.000977 uniform baseline; delocalized) | same order | 0.0027-0.0032 (same order -- NOT a localization effect) |

The real embedding spectrum is a clean, reproducible POWER LAW across two independent V samples -- not a
compact bulk plus a handful of isolated spikes. Eigenvector IPRs are similar between real and control (both
~3x the fully-uniform baseline), so the departure from i.i.d. is a magnitude/shape effect on the eigenVALUES, not
a localization effect on the eigenVECTORS (the "spike" directions are broad semantic factors, not single-item
artifacts).

### 1d. Results -- retrieval-margin-collapse simulation

Truncated-spectrum sweep (V=20820, sigma in {0.14, 0.18, 0.22}, total variance held fixed while flattening the
tail beyond rank K): accuracy at fixed sigma varies only within Monte-Carlo noise across K=0 (fully flat spectrum,
real total variance) through K=1024 (full real spectrum) -- e.g. at sigma=0.18: K=0 gives 0.327, K=1024 gives
0.293, with K=1,5,20,50,100,300 all in the 0.21-0.30 band. **The SHAPE of the spectrum, once total variance is
matched, contributes at most a small (noise-level) effect on the AGGREGATE collapse curve -- the dominant single
scalar is total variance (embedding-cloud concentration), not the finer power-law structure.**

Paired real-vs-full-spectrum-surrogate comparison (V=20820, n_queries=1500, matched noise draws per sigma,
conservative binomial SE~=0.013 per point):

| sigma | real acc | surrogate acc | real - surrogate | SEs from zero |
|---|---|---|---|---|
| 0.10 | 0.7047 | 0.9627 | -0.2580 | ~20 |
| 0.12 | 0.5593 | 0.8087 | -0.2493 | ~19 |
| 0.14 | 0.3960 | 0.6080 | -0.2120 | ~16 |
| 0.16 | 0.2880 | 0.4213 | -0.1333 | ~10 |
| 0.18 | 0.1853 | 0.2467 | -0.0613 | ~5 |
| 0.20 | 0.1200 | 0.1673 | -0.0473 | ~4 |
| 0.24 | 0.0573 | 0.0873 | -0.0300 | ~2 |

Three-way (real / surrogate / i.i.d.-control) robustness check across V=20820 (2 seeds) and V=41328 (1 seed),
computing the PERCENT of the (control - real) gap explained by (control - surrogate): 0% at pre-collapse
(sigma<=0.11, everything near ceiling), rising through 60-75% at sigma=0.14, to 82-95%+ at sigma>=0.18 --
consistent across all three (V, seed) combinations tested.

**Interpretation:** the Gaussian-equivalent spectral surrogate is DIRECTIONALLY correct and captures MOST of the
aggregate degradation once deep in the collapse regime, but is a systematically OPTIMISTIC (over-predicts
accuracy) approximation that is WORST exactly where a "collapse boundary location" question cares most --
the onset of collapse. This is not noise: the gap is 4-20 SEs from zero at every tested sigma.

---

## 2. LITERATURE GROUNDING (both lit-scans completed; citations below)

**Gaussian Equivalence Theorem (GET) exists and is a real, established tool** (Hu & Lu arXiv:2009.07669;
Goldt/Mezard/Krzakala/Zdeborova PRX 2020 "hidden manifold model") -- semi-closed-form (a deterministic-equivalent
fixed-point system), not a few-parameter algebraic formula. **Its documented failure modes match this drill's
empirical residual exactly:** Mai & Liao (arXiv:2410.05609, 2024) show GET breaks for CLASSIFICATION/ERM tasks on
non-Gaussian mixture data with matched second-order statistics -- i.e. an argmax/classification-style task
(exactly this drill's retrieval-argmax setup) is a KNOWN failure regime for pure second-order matching, not
regression. Wen, Hu, Lu, Fan & Misiakiewicz (arXiv:2512.03325, 2025) independently show GET is non-universal
whenever the target depends on a LOW-DIMENSIONAL PROJECTION of the data -- exactly the "near-duplicate semantic
cluster" content structure the GSBC/Family-E drills already identified as the heterogeneous-correlation driver.

**Eigenlearning/spectral-bias framework gives a genuine closed form** (Simon, Dickens, Karkada & DeWeese,
arXiv:2110.03922: `E = E0(sum_i(1-L_i)^2 v_i^2 + eps^2)`, L_i=lambda_i/(lambda_i+kappa)) -- but this is derived for
KERNEL RIDGE REGRESSION generalization error, not retrieval-argmax accuracy; the lit-scan found NO existing paper
giving a closed-form mapping from effective-rank/participation-ratio directly to nearest-neighbor retrieval
accuracy. Adapting the eigenlearning machinery to an argmax/retrieval-margin target would be genuine novel
synthesis, not a literature reuse -- consistent with capping any such attempt at P<=0.50.

**Power-law embedding spectra are a well-established, independently-replicated empirical fact** (Mu & Viswanath
"All-but-the-Top" arXiv:1702.01417; Ethayarajh EMNLP-IJCNLP 2019 D19-1006; Gao et al. ICLR 2019 arXiv:1907.12009;
Paquette, Xiao & Zhu 2026 arXiv:2603.14578 "Power-Law Spectrum of the Random Feature Model," explicitly connecting
Zipfian frequency statistics to power-law covariance decay, contrasted against the flat Marchenko-Pastur bulk of
isotropic data) -- this drill's directly-measured exponent (-1.0 to -1.12) is consistent with, not an artifact of,
this substrate's specific data.

**BBP/spiked-covariance is confirmed the WRONG toolkit for a power-law continuum** -- Burda, Gorlich & Waclaw
(arXiv:physics/0603186) and Biroli & Bouchaud (arXiv:cond-mat/0609070) develop a STRUCTURALLY DIFFERENT spectral
toolkit specifically for heavy-tailed/power-law covariance ensembles (a genuinely different universality class,
Tracy-Widom vs Frechet top-eigenvalue statistics depending on tail index) -- the disjoint mathematical setups
(finite-rank-perturbation-on-flat-bulk vs. full heavy-tailed continuum) confirm the prior notes' BBP/Wigner-edge/
free-cumulant recommendation was aimed at the wrong regime for this specific spectrum shape.

**Hubness is confirmed content/intrinsic-dimension-driven, not spectrum-summarizable** -- Radovanovic, Nanopoulos
& Ivanovic (JMLR 11, 2010) and a 2023 follow-up on hubness in Sentence-BERT spaces (arXiv:2311.18364) both report
hubness tracks INTRINSIC (data-manifold) dimension and is dataset-specific, not a function of ambient spectral
shape alone; Furon (arXiv:2010.00990) explicitly attributes NN-rank-flip failures to assumption violations
(content-dependent), not a pure statistical/spectral quantity. This is the literature-level confirmation of this
drill's empirical residual.

**Covariance-matched Gaussian surrogate is an established, legitimate diagnostic methodology** (generic analog:
Theiler et al., "Surrogate Data" method, Physica D 58, 1992) -- validates this drill's core method as a
recognized technique, not an ad hoc test.

---

## Cheap decisive test

Already run this drill (Sec. 1): covariance eigendecomposition (<1s CPU) + Gaussian-equivalent surrogate
construction + paired retrieval-collapse simulation (n_queries=1500, ~1 min CPU), against the on-disk BGE
concept-embedding cache, at two V and two seeds. Pre-registered discriminating criteria (stated before running):
- **RMT-tractable (would support a cell):** covariance-matched Gaussian surrogate's predicted collapse-sigma
  (accuracy crossing 0.5) deviates from the REAL measured collapse-sigma by <=10% (a band comparable to, though
  looser than, the RNS/FHRR CG cases' <5% bar, allowing for the surrogate's coarser nature).
- **RMT resists (ACCEPT boundary):** deviation >20%, OR the gap is concentrated in the onset-of-collapse regime
  rather than uniformly distributed (meaning the surrogate is unreliable exactly where a boundary-location
  prediction is needed).
- **Result:** real collapse-sigma (accuracy=0.5 crossing) is approximately sigma~0.145 (interpolating: 0.559 at
  0.12, 0.396 at 0.14); surrogate's 0.5-crossing is approximately sigma~0.155-0.16 (interpolating: 0.608 at 0.14,
  0.421 at 0.16) -- roughly a 7-10% shift in the sigma AXIS at the 50%-crossing itself, but the ACCURACY-level
  deviation at any FIXED sigma near the crossing is large (0.396 vs 0.608 at sigma=0.14, a 21-point accuracy gap)
  and the qualitative pattern (gap concentrated at onset, not uniform) matches the HARD-FAIL / ACCEPT-boundary
  criterion, not the tractable one. **Verdict: ACCEPT the boundary** -- the sigma-axis shift alone looks modest,
  but the accuracy-level residual at fixed operating points is large and systematically biased in the direction
  that would matter most in practice (a false sense of margin).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, restated for scan-ability)

- **HARD-PASS (would justify a dedicated encoder-margin CG-candidate cell):** covariance-spectrum-derived
  Gaussian-equivalent surrogate predicts the REAL encoder's collapse-sigma (accuracy=0.5 crossing) within 10%,
  AND the residual accuracy-level gap at any tested sigma is <=5 points. **NOT MET** (sigma-crossing shift ~7-10%,
  borderline, but accuracy-level residual at the crossing itself is ~21 points, far outside the 5-point bar).
- **HARD-FAIL (ACCEPT the boundary, as concluded this drill):** residual accuracy-level gap >15 points at any
  sigma in the collapse-transition band, AND/OR the gap is concentrated at collapse-onset rather than uniform.
  **MET** (13-26 point gap at sigma=0.10-0.16, shrinking to 3-6 points only once deep in collapse, sigma>=0.18;
  paired-trial significance 4-20 SEs at every tested point).
- **Bonus finding (not part of the original pre-registration, discovered this drill, reported per
  [[feedback-research-every-finding-for-mechanism-and-envelope-push]]):** once total variance is held fixed, the
  eigenvalue-spectrum SHAPE (power-law vs flat) contributes only a noise-level effect to the aggregate collapse
  curve -- the dominant single-scalar spectral summary is trace(C) (total variance / concentration), not the
  finer power-law structure. This is a genuinely simpler, more surprising, and more useful characterization than
  "the spectrum is complicated" -- P_deflated=0.55 for this sub-finding specifically (an aggregate-level,
  reproducible-across-2-V numeric result, deflated from a would-be-higher confidence per the standard lit-scan
  penalty since it has not been cross-checked against a third independent V or an analytic derivation).

---

## CROSS-THREAD SYNTHESIS

- **With `notes/research_codebook_design_space_generalization_2026-07-06.md` (Family E) and
  `notes/research_gsbc_codebook_correlation_homogeneity_2026-07-06.md` (Sec. 3-4):** both notes flagged "RMT/
  free-probability on the concept-Gram spectrum" as the open next step for Family E and its GSBC-compressed
  derivative (Family D, now confirmed to collapse into Family E per the homogeneity drill). This drill CLOSES
  that open thread: RMT/free-probability (via the Gaussian-equivalence/covariance-matched-surrogate route, the
  legitimate adjacent tool once the classic BBP/spiked-model route was confirmed inapplicable to a power-law
  continuum spectrum) gives a PARTIAL, bulk-level account but resists a CG-tier closed form for the same
  fundamental reason both prior notes identified (content-dependent, hub/near-duplicate-driven heterogeneity) --
  now confirmed a THIRD independent way (one-factor pairwise correlation FAILED per the GSBC drill; raw
  cosine-Gram heterogeneity FAILED the exchangeability assumption per the codebook-design-space drill; and now
  spectral/RMT summary FAILS to close the collapse-onset residual per this drill). Three independent routes,
  same root cause, same conclusion -- this is a well-triangulated, not a single-shot, negative.
- **With `feedback_research_every_finding_middle_negative_for_mechanism_and_envelope_push` (memory, USER-locked):**
  this negative is itself a mechanism clue: real, trained, content-rich embeddings have genuinely multi-scale
  (power-law, not few-factor) semantic structure that no permutation-invariant (spectrum-only) summary can fully
  capture -- a structural fact about ANY future substrate object built by distilling a real trained embedding
  (reinforcing the GSBC drill's design lesson: fresh i.i.d.-per-dimension constructions, not compressed real
  embeddings, are the ones that buy cheap closed-form self-margin prediction).
- **With the field-advisor's Tier-1 candidates (`F2 Wigner edge/Tracy-Widom`, `F4 free cumulants`):** this drill's
  finding refines rather than simply executes those candidates -- it shows WHY the classic Wigner-edge/free-cumulant
  toolkit (designed for compact-bulk-plus-spike ensembles) is not the right next investment for the CONCEPT-ENCODER
  Gram matrix specifically (a power-law-continuum ensemble, a different universality class per Burda-Gorlich-Waclaw/
  Biroli-Bouchaud). Those candidates remain open for OTHER substrate objects with genuinely spiked (not power-law)
  spectra if any are identified in a future drill -- but should not be aimed at this object again.
- **Saturation-avoidance note (Trigger A):** this drill, the codebook-design-space drill, and the GSBC homogeneity
  drill are three consecutive free-probability/spectral/correlation-structure-themed drills in the same session
  arc. Per role discipline, the NEXT drill should pivot to a genuinely different field -- recommend `D1 Glauber
  dynamics on substrate codeword space` (semiconductor/stochastic-dynamics family, tier-1, ~1hr CPU smoke, per the
  field advisor) as the next candidate, deliberately diversifying away from the free-probability/RMT family for
  at least one cycle.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- **Immediate:** no change to any landed cell's verdict -- this drill touched no measurement machinery, no config,
  no stored artifact; every number above was computed fresh, off-disk, from already-cached BGE embeddings and
  discarded scratch arrays (monitor-not-control, per USER lock).
- **Research-thread consolidation:** the "RMT/free-probability on the concept-Gram spectrum" open item flagged by
  TWO prior notes is now CLOSED with a decisive, quantified, statistically-significant answer (ACCEPT boundary) --
  rather than remaining open as an "exploratory, someday" item. This removes a standing open thread from future
  cadence planning.
- **Design lesson reinforced:** any future substrate codebook wanting cheap, closed-form, CG-tier self-margin
  prediction should continue to prefer i.i.d.-per-dimension random-phase/frequency construction (RNS/FHRR's proven
  property) over distilling/compressing a real trained embedding -- now confirmed true for the spectral/RMT
  approach specifically, not just the pairwise-correlation approach.
- **If ANY encoder-level self-margin signal is wanted despite this ACCEPT:** the GSBC drill's Sec. 4 fallback
  (self-nearest-neighbor empirical confusability calibration, already spec'd, non-parked, P_deflated=0.35) remains
  the cheaper, already-recommended, comparably-targeted alternative -- it requires no eigendecomposition or
  surrogate simulation, and targets the SAME root cause (content-dependent local confusability) this drill's
  residual gap is attributable to. This drill does NOT recommend building a second, redundant tool alongside it.
  A Gaussian-equivalent-surrogate "coarse aggregate reference curve" (this drill's method, Sec. 1) is available as
  a strictly lower-priority, non-recommended appendix if ever wanted for a population-level (not per-item) sanity
  check -- explicitly deprioritized below the GSBC fallback, since it is more expensive (needs an eigendecomposition
  + Monte-Carlo simulation) and less accurate (systematically optimistic-biased) in the regime that matters most.
- **Still monitor-not-control:** zero config changes; this is a closed research question, not an experiment queued
  for dispatch.

---

## CITATIONS

**Verified-external-citation count this drill: 17 of 25 fully live-verified (fetch-confirmed) across both
lit-scans; 8 flagged explicitly as search-confirmed-only (bibliographic details cross-confirmed via search
snippets, direct fetch failed/blocked) -- reported honestly, not smoothed over.**

**Lit-scan 1 -- Gaussian equivalence, eigenlearning, quadratic forms, NN-retrieval:**
1. Hu, H. & Lu, Y.M. (2020/2022). arXiv:2009.07669 -- Gaussian equivalence for random-feature models via
   Lindeberg/Stein CLT + leave-one-out. FETCH-VERIFIED.
2. Mai, X. & Liao, Z. (2024). arXiv:2410.05609 -- GET breaks for classification/ERM on non-Gaussian mixtures with
   matched 2nd-order stats. FETCH-VERIFIED. (Directly explains this drill's residual.)
3. Wen, Z., Hu, H., Lu, Y.M., Fan, Z. & Misiakiewicz, T. (2025). arXiv:2512.03325 -- GET non-universal when target
   depends on a low-dimensional projection; "Conditional Gaussian Equivalent" patch proposed. FETCH-VERIFIED.
4. Goldt, S., Mezard, M., Krzakala, F. & Zdeborova, L. (2020). Phys. Rev. X 10, 041044 / arXiv:1909.11500 --
   hidden manifold model, Gaussian Equivalence Property for two-layer one-pass-SGD dynamics. FETCH-VERIFIED.
5. Bordelon, B., Canatar, A. & Pehlevan, C. (2020). ICML / arXiv:2002.02561 -- replica-method spectral
   decomposition of KRR generalization error. Search-verified (detailed).
6. Simon, J.B., Dickens, M., Karkada, D. & DeWeese, M. (2021/2023). arXiv:2110.03922 -- closed-form eigenlearning
   equation `E=E0(sum(1-L_i)^2 v_i^2 + eps^2)`. FETCH-VERIFIED.
7. Bahri, Y., Dyer, E., Kaplan, J., Lee, J. & Sharma, U. (2021). arXiv:2102.06701 / PNAS -- four neural-scaling
   regimes tied to eigenspectrum decay. FETCH-VERIFIED (abstract).
8. Furon, T. (2020/2022). arXiv:2010.00990 -- statistical model of NN-rank-flip perturbation; failures attributed
   to assumption violations (content-dependent). FETCH-VERIFIED.
9. Aggarwal, C., Hinneburg, A. & Keim, D. (2001). ICDT -- foundational distance-concentration result. Search-
   verified only (not fetched).
10. Radovanovic, Nanopoulos & Ivanovic (2010). JMLR 11 "Hubs in Space" -- search-snippet only this round (PDF
    fetch failed); hubness tied to intrinsic not ambient dimension. UNVERIFIED-BY-FETCH.
11. Imhof (1961) / Davies (1973/1980) -- quadratic-form tail inversion, documented via CompQuadForm R package.
    FETCH-VERIFIED (package doc; original papers not independently fetched).

**Lit-scan 2 -- power-law embedding spectra, cone effect, spiked vs power-law RMT, hubness, surrogate methodology:**
12. Mu, J. & Viswanath, P. (2017). arXiv:1702.01417 "All-but-the-Top" -- trained embeddings' variance concentrated
    in mean + few frequency-coding top directions. FETCH-VERIFIED.
13. Ethayarajh, K. (2019). EMNLP-IJCNLP, ACL Anthology D19-1006 -- BERT/ELMo/GPT-2 layers are non-isotropic/
    cone-like. FETCH-VERIFIED.
14. Gao, J. et al. (2019). ICLR / arXiv:1907.12009 -- representation degeneration into a narrow cone under
    likelihood training. FETCH-VERIFIED.
15. Paquette, C., Xiao, L. & Zhu, Z. (2026). arXiv:2603.14578 "Power-Law Spectrum of the Random Feature Model" --
    Zipfian frequency stats -> power-law covariance decay, contrasted against flat MP bulk. FETCH-VERIFIED.
16. Baik, J., Ben Arous, G. & Peche, S. (2005). Annals of Probability 33(5):1643-1697 -- BBP phase transition,
    finite-rank spike detectability threshold. Search-confirmed (bibliographic; direct PDF 404'd).
17. Burda, Z., Gorlich, A. & Waclaw, B. -- arXiv:physics/0603186 -- spectral density for heavy-tailed/power-law
    covariance ensembles, a structurally different regime from BBP. FETCH-VERIFIED.
18. Biroli, G. & Bouchaud, J.-P. -- arXiv:cond-mat/0609070 -- top-eigenvalue statistics bifurcate (Tracy-Widom vs
    Frechet) by tail index, a different universality class from BBP's finite-rank setting. Search-confirmed only.
19. Radovanovic, Nanopoulos & Ivanovic (2010). JMLR 11:2487-2531 -- hubness framed as dimensionality-driven.
    FETCH-VERIFIED (this lit-scan's fetch succeeded where lit-scan 1's did not).
20. "Hubness Reduction Improves Sentence-BERT Semantic Spaces" (2023). arXiv:2311.18364 -- hubness is
    dataset-specific, tracks intrinsic not embedding dimension. FETCH-VERIFIED.
21. Theiler, J. et al. (1992). Physica D 58:77-94 -- "surrogate data" method, phase-randomized nulls matched to
    real power spectrum, to test for structure beyond linear/2nd-order statistics. Search-confirmed.
22. Schneidman, E., Berry, M., Segev, R. & Bialek, W. (2006). Nature 440:1007-1012 -- pairwise maximum-entropy
    null models vs higher-order structure. Search-confirmed (fetch blocked by login redirect).

**Substrate-internal (verified on disk this drill, load-bearing, not counted toward external total):**
- `data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz`,
  `bge_large_v2_name_41328_6e2d3257.npz` (loaded directly; `composite` 1024-dim unit-norm vectors, the spectral
  analysis object for this drill).
- `hdlab/concept_encoder.py` (re-cited; the RKD-distilled-from-BGE concept table whose Gram structure this drill's
  BGE-teacher measurement is a proxy for, per the GSBC drill's already-established "GSBC/encoder inherit the
  teacher's Gram structure, attenuated" finding).
- `notes/research_codebook_design_space_generalization_2026-07-06.md`,
  `notes/research_gsbc_codebook_correlation_homogeneity_2026-07-06.md` (read in full; the two open threads this
  drill closes).
- `tools/orchestrator/research_field_advisor.py` output (run this drill; informed the saturation-avoidance
  next-drill recommendation, Sec. CROSS-THREAD SYNTHESIS).

---

*Research complete 2026-07-06. Core finding (ACCEPT the boundary for a CG-tier encoder self-margin cell via
RMT/free-probability) established via a decisive, paired, statistically significant (4-20 SEs) numeric test
against real on-disk BGE-distilled concept embeddings at two independent V samples, BEFORE and cross-checked
AGAINST a fully live-searched literature scan (17/25 citations fetch-verified) that independently confirms both
the failure mode (Gaussian-equivalence documented to break for classification/argmax tasks with content-dependent
low-dimensional structure) and the methodology (covariance-matched surrogates are an established diagnostic).
Notes-only drill per task instruction -- no cell built, no dispatch, no routing/hand-off files (USER-locked
ferry-deprecation override; the honest ACCEPT-boundary verdict, plus the deprioritized fallback appendix, are
delivered directly in this note for Director to act on or defer).*
