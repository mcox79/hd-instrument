# Research -- GSBC block-local codebook decode-margin PREREQUISITE: is codeword correlation homogeneous or heterogeneous?

**Date:** 2026-07-06
**Trigger:** Cadence gap-fill drill (GPU busy w/ FHRR 5-seed re-VET, remote-CPU idle). The codebook design-space
drill (`notes/research_codebook_design_space_generalization_2026-07-06.md`, Family D) flagged the GSBC block-local
sparse codebook -- the LANGUAGE/generation-carrying family -- as needing a one-factor/equicorrelated closed-form
generalization of the RNS/FHRR order-statistic self-margin formula, but named an explicit, unresolved PREREQUISITE:
"does the per-pair correlation distribution look roughly homogeneous, or does it have real semantic/heterogeneous
structure?" That drill measured only a single mean cosine (~0.5) and did not check homogeneity. **This drill
answers that prerequisite directly, off-disk, against the actual decode codebook (not the mean-only proxy the
prior drill used).**
**Discipline:** measured the REAL block-local sparse codebook object (`_blocklocal_codebook_gsbc`, the function
Stage A/C of `exp_generation_decoder_gsbc_native_blocklocal_v1.py` actually decodes against) directly from the
on-disk native-GSBC filler pool (`data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz`) and the on-disk BGE
ground-truth semantic cache (`data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz`) -- zero
new trials, no cell, no dispatch, no config change. 2 parallel Sonnet lit-scans dispatched for external grounding
using generic math terms only (per query-privacy discipline); **both completed with live-verified citations this
round** (the prior drill's 3 lit-scans all hit a `529 Overloaded` outage; that outage has cleared).

---

## HEADLINE

**The GSBC block-local codebook's per-pair cosine correlation is DEFINITIVELY HETEROGENEOUS, not homogeneous/
equicorrelated -- verified directly, not merely suspected. Pairwise codeword cosine correlates strongly with an
INDEPENDENT ground-truth semantic-similarity measure (Pearson r=0.71-0.77 at the currently-deployed anchor
sparsification D=3, across 3 seeds and up to V=3000, n up to 4.5M pairs; still r=0.28-0.37 at the most-sparsified
boundary regime D=26), while the iid control codebook shows r~0.001 at every sparsification level. A one-factor/
equicorrelated model has NO mechanism to produce correlation with an external, independently-measured semantic
signal -- so this single number is dispositive, not merely suggestive. The prerequisite the prior drill flagged
FAILS. The one-factor closed-form generalization does NOT apply to GSBC as scoped.**

**Root cause, now confirmed rather than hypothesized: GSBC block-local codes are a JL-projected + top-k-sparsified
+ signed derivative of the SAME real, trained, BGE-distilled concept-encoder Gram structure that Family E
(`hdlab/concept_encoder.py`'s 177899-concept codebook) already has -- i.e. Family D (GSBC) is not a fifth,
independent codebook-family case; it is Family E's heterogeneous-correlation problem, viewed through a lossy
compression, and inherits the same "needs spectral/empirical tools, not order-statistics" conclusion. This
resolves the prior drill's open question (Sec. 3: "is Family D a genuinely separate closed-form opportunity, or
does it collapse into Family E?") -- it collapses into Family E.**

**Recommendation: ACCEPT the negative for the one-factor cell (do not build it) and fold GSBC into the
ALREADY-flagged Family E follow-on (RMT/free-probability spectral drill on the concept-Gram spectrum), rather than
spinning up a second, separate research thread. A cheaper, lower-tier, empirically-calibrated (not closed-form)
alternative is named below (Sec. 4) as a non-parked, ready-to-spec fallback if the substrate wants ANY GSBC
per-item risk signal sooner than a full spectral treatment -- explicitly NOT eligible for the RNS/FHRR CG tier.**

---

## 1. WHAT WAS MEASURED (and why the prior drill's number was the wrong proxy)

### 1a. The prior drill measured the WRONG object

`notes/research_codebook_design_space_generalization_2026-07-06.md` (Family D) cited `controls.dense_bipolar_cone`
(~0.5) from `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` as evidence of GSBC codeword
correlation. Re-reading `exp_generation_decoder_gsbc_native_blocklocal_v1.py:552-565` this drill: that "cone" is
computed on `dense_gsbc_lex` (`make_dense_bipolar_gsbc`), the DENSE N=8192-dim bipolar-cast contrast arm -- an
explicitly-mismatched pipeline the cell's own header (lines 47-52) says COLLAPSES on correlated fillers and is
NOT the generation mechanism. The actual measured value on-disk is 0.352 (all 3 seeds), not the ~0.5 the prior
note recalled from the file's header comment (which cites a DIFFERENT, unlogged "raw 0.511" figure) -- neither
number is the right object to answer the homogeneity question. **The actual decode-relevant codebook is
`cb_gsbc` from `_blocklocal_codebook_gsbc()` (lines 237-250): a SPARSE (~2% active), bs-dimensional (bs=N/D)
bipolar code per concept, JL-projected from the real GSBC_EXPAND2X dense code then top-k-sparsified and signed.
This is the object Stage C's per-block argmax (`argmax(cb @ seg)`, line 274) actually competes against, and the
object this drill measured directly.**

### 1b. Method

Reused `_load_pool()`, `_gsbc_dense()`, `_blocklocal_codebook_gsbc()`, `_blocklocal_codebook_synth()` verbatim
(imported the cell module, not reimplemented) against the on-disk 10000-concept native-GSBC pool. For the SAME
sample of V concepts, pulled ground-truth BGE semantic vectors (`composite`, 1024-dim, from the corpus-wide
177899-concept cache) via the pool's `concept_rows` index mapping, giving an INDEPENDENT semantic-similarity
matrix to correlate against. Computed pairwise cosine of the actual sparse `cb_gsbc` codebook and of the iid
`cb_synth` control codebook (same V, bs, seed), at D in {3, 6, 12, 26} spanning the deployed "direct" anchor
(D=3, V=1024) through the sparsest "boundary" cliff region (D=26).

### 1c. Results

| D | bs | k_active | **r(gsbc_cos, bge_truth)** | spearman | gsbc mean/std | synth mean/std | var-ratio (gsbc/synth) |
|---|---|---|---|---|---|---|---|
| 3 | 2730 | 55 | **0.7674** (seed7) / 0.7103 (seed13) / 0.7061 (seed19) / 0.7624 (seed7,V=3000) | 0.774 | 0.149 / 0.071 | -0.00003 / 0.019 | 13.99 |
| 6 | 1365 | 27 | **0.6220** | 0.617 | 0.132 / 0.076 | -0.00003 / 0.027 | 7.96 |
| 12 | 682 | 14 | **0.5367** | 0.535 | 0.147 / 0.102 | -0.00006 / 0.038 | 7.06 |
| 26 | 315 | 6 | **0.2824** (seed7) / 0.3714 (seed13) | 0.272 / 0.363 | 0.131 / 0.136 | 0.00016 / 0.056 | 5.84 |

(iid synth control: r vs bge_truth is -0.0014 to +0.0012 at every D -- indistinguishable from zero, as expected
for a codebook constructed with no dependence on concept identity. n = 523,776 pairs at V=1024; 4,498,500 pairs at
the V=3000 robustness check.)

Robustness checks run: 3 different projection seeds at D=3 (0.706-0.767, consistent), one 3x-larger V (V=3000,
n=4.5M pairs, r=0.762, consistent), and a trimmed-tail check (dropping the top 1% of BGE-similarity pairs, to rule
out a handful of near-duplicate outliers driving the whole correlation) -- trimmed r stays at 0.69-0.75 at D=3,
i.e. the correlation is a BULK property of the distribution, not an artifact of a few extreme pairs.

Skew/kurtosis: gsbc distribution is right-skewed at every D (skew 0.56 at D=3 rising to 0.84 at D=26) vs synth's
near-zero skew (D=3: -0.003) -- consistent with a heavy right tail of elevated-correlation (semantically related)
pairs riding on top of a homogeneous-looking bulk. Near-exact-collision check (cosine >= 0.999, i.e. literally
duplicate sparse codes -- a genuine decode-tie failure mode, not just a soft margin reduction): 0/523776 at D=3,
2/523776 (0.0004%) at D=26 -- rare at the deployed anchor, but nonzero and growing as sparsification increases,
which is itself informative for Sec. 4 below.

### 1d. Concrete evidence -- the top-correlated pairs are semantically real, not noise

Top-10 highest-cosine GSBC codeword pairs at D=3 (V=1024, seed 7) include, verbatim from the on-disk vocabulary:
`T2/oeis_A017658`/`T2/oeis_A017556` (gsbc_cos=0.709, bge_truth=0.935 -- two OEIS integer-sequence entries),
`T2/oeis_A005550`/`T2/oeis_A005549` (gsbc=0.691, bge=0.975), `T3/wikidata_Q16044893`/`T3/wikidata_Q10428220`
(gsbc=0.709, bge=0.960), and `CN_lots_people`/`CN_lot_of_people` (gsbc=0.636, bge=0.980 -- a near-duplicate phrase
pair). These are not artifacts: they are exactly the kind of near-synonym/near-duplicate concept clusters a real,
trained semantic encoder is SUPPOSED to place close together, and the block-local sparse projection preserves
that closeness (attenuated, not eliminated) even after JL-projecting GSBC_DIM=8192 down to bs=2730-315 and
sparsifying to 6-55 active dims.

---

## 2. WHY THIS IS A DEFINITIVE TEST, NOT A SUGGESTIVE ONE

Under a TRUE one-factor/equicorrelated model (Dunnett-Sobel / Vasicek-ASRF / Li one-factor-copula -- the route
the prior drill proposed), every pairwise correlation is generated as `rho + noise` from a SINGLE shared latent
factor plus idiosyncratic per-item noise; critically, the model has **no channel through which the specific
identity of a pair could align with an INDEPENDENTLY measured external semantic-similarity signal** -- doing so
would require the "shared factor" to literally encode semantic content for every possible pair simultaneously,
which is a contradiction of what "one shared factor" means. Observing r=0.28-0.77 (reproducible across seeds,
sample sizes, and sparsification levels, immune to a top-1%-tail trim) against an INDEPENDENT ground truth is
therefore not merely "high variance" -- it is direct proof the correlation structure is content-dependent
(heterogeneous), which a one-factor model cannot produce by construction. This is the same logic Family E's
"cat/kitten >=0.4, cat/airplane <=0.1" selftest gate already established for the RAW concept-encoder Gram matrix
(`hdlab/concept_encoder.py:849-850`); this drill shows the SAME structure survives, attenuated but intact, through
the GSBC block-local compression pipeline.

---

## 3. ANSWERS TO THE DIRECTOR'S QUESTIONS

**Q1 (homogeneous or heterogeneous):** **HETEROGENEOUS**, verified directly (Sec. 1-2), not assumed. The
homogeneity prerequisite for the one-factor closed-form route FAILS at every tested sparsification level
(D=3,6,12,26), though the correlation-with-ground-truth strength decays monotonically as sparsification increases
(r: 0.77 to 0.28) -- more aggressive compression destroys, but does not eliminate, the semantic signal.

**Q2 (is a block-conditional or numeric-quantile self-prediction still tractable, or does GSBC resist closed-form
self-margin like the encoder):** GSBC resists closed-form self-margin for the SAME reason Family E does (Sec. 4
of the prior drill correctly anticipated this route would be needed if the prerequisite failed) -- because it now
appears GSBC IS Family E's problem, inherited through a lossy JL+sparsify+sign compression, not a structurally
independent codebook family. A pure numeric-quantile empirical calibration (not closed-form) is tractable and
cheap (Sec. 4 below), but it would be a MEASURED_MECHANISM-tier monitor artifact at best, not a CG-eligible exact
formula like the RNS/FHRR cases -- an honest, explicitly lower tier.

**Q3 (recommendation -- build or ACCEPT):** **ACCEPT the negative for the originally-scoped one-factor cell.**
Do not build it. Fold the underlying question into the ALREADY-flagged Family E follow-on (RMT/free-probability
spectral drill on the concept-Gram spectrum, `notes/research_codebook_design_space_generalization_2026-07-06.md`
Sec. 1 Family E) -- since GSBC's Gram structure is now confirmed (not merely plausible) to be a compressed
derivative of that same object, a single spectral drill can address both families rather than opening a second,
duplicative research thread. A cheaper, lower-confidence, non-closed-form fallback is specified in Sec. 4 if the
substrate wants a GSBC-specific signal sooner than a full spectral treatment.

---

## 4. FALLBACK CANDIDATE (spec only, non-parked, explicitly LOWER TIER than the RNS/FHRR CG cases)

**Self-nearest-neighbor empirical confusability calibration.** Not a closed-form formula -- an empirically
calibrated per-item risk proxy, in the spirit of the substrate's existing conformal-calibration cadence (Bet
C1-C5), monitor-only.

**Mechanism:** for each concept in the deployed block-local codebook, compute its OWN nearest-neighbor cosine
WITHIN the codebook itself (`cb_gsbc @ cb_gsbc.T`, self-contained -- no external BGE oracle needed at decode time,
since the codebook is already on-disk). This is a cheap, already-available-at-decode-time covariate. Calibrate
(isotonic regression or quantile binning) this self-NN-distance covariate against MEASURED per-item decode
failures, concentrating the calibration set in the "boundary" cliff region (D=12, D=26, high V) where genuine
failures actually occur in the landed cell's own boundary-map (the "direct" deployed region currently shows ZERO
failures, exact_ordered=1.000, so there is no failure signal to calibrate against there -- the boundary region is
the only place this calibration has data to learn from).

**Why this is plausible and not hand-waved:** Sec. 1's near-exact-collision count (0 at D=3, 2/523776 at D=26)
plus the Hubs-in-Space finding below (Radovanović et al. 2010 -- NN-confusability is intrinsically local/
heterogeneous in high dimensions, not a population-level constant) both point the same direction: failures should
concentrate on a small, locally-identifiable subset of near-duplicate-prone items, which is exactly what a
self-NN-distance covariate would flag cheaply.

**Pre-registered bands (deflated per role discipline -- capped BELOW the usual 0.50 novel-synthesis ceiling,
since this is empirical calibration, not a derived closed form, an additional discount per
[[feedback-lit-scan-calibration-penalty]]):**
- **HARD-PASS**: self-NN-cosine covariate, calibrated via isotonic regression on held-out boundary-region trials,
  achieves Spearman rho >= 0.4 between the calibrated risk score and actual per-item decode failure (binary), AND
  the calibration transfers out-of-sample (a fresh V/D grid point not used for fitting) within 10 percentage
  points of in-sample calibration error. P_deflated = **0.35** (capped below the usual 0.50 -- empirical
  calibration on a heterogeneous, content-dependent signal carries more generalization risk than a derived closed
  form; per [[feedback-lit-scan-calibration-penalty]] and the covariate-shift caveat surfaced by lit-scan Sec. 5).
- **HARD-FAIL**: Spearman rho < 0.15 (the covariate carries no useful signal beyond noise), OR the calibration
  fails to transfer out-of-sample (>20-point degradation) -- would mean per-item confusability in this codebook is
  NOT locally predictable from the codebook's own self-similarity structure alone (would need the query's original
  BGE embedding as a covariate too, which breaks the "no external oracle at decode time" cheapness property).
- **MIDDLE**: useful in-sample signal (rho >= 0.4) that does not transfer well out-of-sample -- would mean the
  calibration is real but overfit to the specific V/D grid tested, needing a larger/more diverse calibration set.

**Cost:** cheap. The self-NN-cosine computation reuses the already-built `cb_gsbc` matrix (one matmul, already
computed as part of the landed cell's normal operation); isotonic regression is a few lines (`sklearn.isotonic` or
a hand-rolled PAV, both already used elsewhere on this substrate per the conformal-calibration cadence). The
calibration DATA is the expensive part -- needs enough boundary-region trials with recorded per-item pass/fail,
which the existing `exp_generation_decoder_gsbc_native_blocklocal_v1.py` boundary grid already generates as a
byproduct (no new measurement machinery, purely a new analysis pass over already-collected `per_unit` records,
PLUS a per-item rather than per-trial failure label, which the current cell's scoring (`_score_blocklocal`) does
not currently expose at that granularity -- a small widening, not a new mechanism).

**Autonomy note (exp_dev owns, if Director elects to pursue this over the Family E spectral route):** whether to
widen the existing cell's `per_unit` recording to expose per-item pass/fail labels or author a standalone analysis
script consuming raw `metrics.json`; exact isotonic-vs-quantile-binning choice; which specific (V,D) boundary
points to use for calibration vs held-out transfer-check.

---

## Cheap decisive test

Already run, this drill (Sec. 1-2): reconstructed the actual on-disk `cb_gsbc` block-local sparse codebook (not
the dense-cast contrast arm's proxy) at 4 sparsification levels, correlated its pairwise cosine against an
independent BGE ground-truth semantic-similarity matrix for the SAME concepts, and checked robustness across 3
seeds, a 3x larger V, and a top-1%-tail trim. Zero new trials; <30s CPU total. Pre-registered discriminating
criteria (stated before running, per role discipline):
- **Homogeneous (would support the one-factor route):** |r(gsbc_cos, bge_truth_cos)| < 0.10, indistinguishable
  from the iid synth control's ~0.001, at every D tested.
- **Heterogeneous (would reject the one-factor route):** |r| statistically far from 0 (>0.2, with n>100k pairs,
  reproducible across seeds) at any D.
- **Result: HETEROGENEOUS, at HARD-FAIL strength for the homogeneity hypothesis** -- r ranges 0.28-0.77 across
  D=3..26, reproducible across 3 seeds, a 3x larger V, and immune to top-1%-tail trimming.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**For the homogeneity question itself (already resolved this drill, restated for scan-ability):**
- HARD-PASS (homogeneous, one-factor applies): |r(gsbc_cos, bge_truth)| < 0.10 at every D. **NOT MET.**
- HARD-FAIL (heterogeneous, one-factor rejected): |r| > 0.2, reproducible across seeds/V, n>100k pairs. **MET**
  (r=0.28-0.77, Sec. 1).

**For the fallback candidate (Sec. 4, if built in a future cycle):**
- HARD-PASS: self-NN-cosine covariate achieves Spearman rho >= 0.4 vs measured per-item decode failure, transfers
  out-of-sample within 10 points. P_deflated = 0.35 (capped below the usual novel-synthesis ceiling).
- HARD-FAIL: rho < 0.15, or out-of-sample transfer degrades >20 points.
- MIDDLE: in-sample signal present but does not transfer.

---

## CROSS-THREAD SYNTHESIS

- **With `notes/research_codebook_design_space_generalization_2026-07-06.md` (Family D and Family E sections):**
  this drill resolves the exact prerequisite that note's Family D section flagged as unresolved ("does the 'cone'
  correlation actually look homogeneous/exchangeable... or does it have real semantic heterogeneity the model
  would miss?") -- answer: heterogeneous, confirmed. It also resolves an implicit open question in that note's
  own Sec. 2 framing (treating Family D and Family E as two separate rows in the 5-family inventory): Family D
  is now shown to be Family E's problem viewed through a lossy compression, not a structurally distinct case.
  Recommend the future RMT/free-probability spectral drill that note already recommended for Family E (Wigner
  edge/Tracy-Widom, free cumulants) be scoped to cover BOTH the raw concept-encoder Gram matrix AND the GSBC
  block-local compressed derivative, rather than treating them as two separate follow-on drills.
- **With `feedback_research_every_finding_middle_negative_for_mechanism_and_envelope_push` (memory, USER-locked):**
  this negative (one-factor route rejected) is itself a mechanism-clue and a design lesson: it tells the substrate
  that ANY future codebook built by projecting/compressing a real trained embedding (rather than generating
  fresh i.i.d. per-dimension randomness, as Families A/B do) will inherit that embedding's heterogeneous Gram
  structure, attenuated but not erased, even under aggressive sparsification (Sec. 1's monotonic-but-nonzero decay
  from D=3 to D=26). This generalizes beyond GSBC to any future substrate codebook built the same way.
- **With the substrate's conformal-calibration cadence (Bet C1-C5):** Sec. 4's fallback candidate is structurally
  the SAME kind of tool (data-driven, isotonic/quantile calibration of an uncalibrated proxy against measured
  outcomes) already used elsewhere on the substrate -- not a new methodological import, a reuse of an existing
  discipline applied to a new object (per-item decode-confusability rather than a global coverage guarantee).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- **Immediate:** no change to the landed cell's verdict (`exp_generation_decoder_gsbc_native_blocklocal_v1`
  remains HARD_PASS at its anchor -- this drill does not touch measurement machinery or config, per monitor-not-
  control discipline). This drill only closes off a PROPOSED future capability (closed-form GSBC self-margin
  prediction) that had not yet been built.
- **Research-thread consolidation:** rather than 2 open follow-on drills (Family D one-factor generalization,
  Family E spectral analysis), there is now 1 -- a real cost saving in future research cycles, and a more accurate
  picture of the substrate's codebook-design space (4 mechanistically distinct cases, not 5: i.i.d.-competitor
  order-statistic [Families A/B, CG-eligible], correlated-heterogeneous [Families D+E merged, spectral/empirical
  tools needed], attractor-dynamics [Family C, different math], = 3 cases, simpler than the prior drill's
  4-way split once D and E are recognized as the same underlying object at different compression levels).
- **Design lesson for future codebooks (reinforcing the prior drill's Sec. 1 conclusion):** any future substrate
  codebook wanting CHEAP, EXACT, closed-form self-margin-prediction should prefer fresh i.i.d.-per-dimension
  random-phase/frequency construction (Families A/B's proven property) over projecting/compressing a REAL trained
  embedding (GSBC/encoder route) -- the latter inherits semantic Gram structure that resists closed-form treatment
  regardless of how aggressively it is compressed or sparsified (this drill's direct evidence: heterogeneity
  survives from bs=2730 down to bs=315, a 8.7x compression, decaying but never vanishing).
- **If Director elects to pursue Sec. 4's fallback in a future cycle:** it would give the language/generation
  backbone a CHEAP, monitor-only, per-item risk flag -- explicitly a lower-confidence, lower-tier deliverable than
  the RNS/FHRR CG candidates (empirical calibration, not derived closed form), useful primarily for the
  currently-open boundary/cliff region where the landed cell already shows real failures to calibrate against.
- **Still monitor-not-control:** every measurement in this drill is read-only against already-landed on-disk
  artifacts (the native-GSBC pool cache, the BGE semantic cache, the landed cell's own functions) -- zero
  config changes, zero new trials, zero modification to N/D/V or any stored artifact.

---

## CITATIONS

**Verified-external-citation count this drill: 12 of 15 fully live-verified (fetch/search confirmed this
session); 3 flagged as recalled/partial (noted individually below).** Both lit-scan sub-agents' web-search
backend worked this round (the prior drill's `529 Overloaded` outage has cleared).

**Lit-scan 1 -- correlated-extremes machinery for heterogeneous (non-exchangeable) competitor pools:**
1. Chernozhukov, V., Chetverikov, D. & Kato, K. (2015). "Comparison and anti-concentration bounds for maxima of
   Gaussian random vectors." *Probability Theory and Related Fields* (arXiv:1301.4807). Explicit bounds for maxima
   of Gaussian vectors with ARBITRARY covariance -- the modern generalization of Slepian/Sudakov-Fernique to the
   heterogeneous case that would replace the one-factor route if a closed-form treatment were pursued later.
   VERIFIED LIVE.
2. Vershynin, R. (2018). *High-Dimensional Probability*, and Talagrand, M. (2014/2021). *Upper and Lower Bounds
   for Stochastic Processes* -- generic-chaining/majorizing-measures machinery giving matching bounds on
   E[max] from the intrinsic covariance-induced metric, no exchangeability assumption. VERIFIED LIVE (textbook
   material, standard).
3. Borell (1975); Tsirelson-Ibragimov-Sudakov (1976) -- Borell-TIS concentration inequality for Gaussian process
   maxima. Recalled, not independently fetched this session -- standard/uncontroversial.
4. Majumdar, S.N., Pal, A. & Schehr, G. (2020). "Extreme value statistics of correlated random variables: a
   pedagogical review." *Physics Reports* 840:1-32 (arXiv:1910.10667). Confirms correlated-variable extreme-value
   statistics is a genuinely different, less-universal regime than the iid Gumbel/Fréchet/Weibull case. VERIFIED
   LIVE.
5. Miccichè, S. (2024). "Role of correlations in the maximum distribution of multiscale stationary Markovian
   processes." arXiv:2405.11539. Correlation reshapes the tail exponent of the maximum's distribution relative
   to the iid case. VERIFIED LIVE.
6. Aldous, D. (1989). *Probability Approximations via the Poisson Clumping Heuristic*, Springer -- rare
   high-threshold exceedances cluster into "clumps" driven by locally correlated near-neighbors; clump count
   (not raw exceedance count) governs extreme/max behavior -- directly the "near-duplicate clump dominates the
   tail" mechanism relevant to Sec. 1's near-exact-collision finding. VERIFIED LIVE (existence/venue), chapter-
   level applicability to this specific framing not independently fetched.
7. Indyk-Motwani (1998); Charikar (2002, SimHash) -- standard LSH collision-probability formalism, ties collision
   probability monotonically to pairwise similarity (textbook basis for Sec. 4's self-NN covariate). VERIFIED
   LIVE (tutorial-level).
   **Gap explicitly reported by lit-scan 1:** no literature directly connects heterogeneous semantic-correlation
   structure to a formal EVT/tail-risk framing for LSH/embedding false-positive rate -- this would be a novel
   synthesis (combining citation 1 or 4/6 with the LSH setting), not an existing result.

**Lit-scan 2 -- empirical self-density confusability calibration (Sec. 4's fallback candidate):**
8. Breunig, M., Kriegel, H.-P., Ng, R. & Sander, J. (2000). "LOF: Identifying Density-Based Local Outliers."
   *SIGMOD*. Foundational local-reachability-density-via-kNN statistic underlying Sec. 4's self-NN covariate.
   VERIFIED LIVE.
9. Karpusha, Yun & Fehérvári (2020). "Calibrated Neighborhood Aware Confidence Measure for Deep Metric Learning."
   arXiv:2006.04935 -- the strongest direct precedent: local embedding-space density -> calibrated retrieval
   confidence, validated against held-out empirical accuracy. VERIFIED LIVE (abstract fetch succeeded).
10. Radovanović, M., Nanopoulos, A. & Ivanović, M. (2010). "Hubs in Space: Popular Nearest Neighbors in
    High-Dimensional Data." *JMLR* 11:2487-2531. Establishes NN-confusability is intrinsically local/heterogeneous
    (hub vs. antihub) in high dimensions -- direct support for why a population-level formula would be wrong and
    a local covariate is the right tool. VERIFIED LIVE (search/abstract; PDF fetch failed as binary).
11. Cui, Zhang, Deng, Dong & Zhu (2023). "Learning Sample Difficulty from Pre-trained Models for Reliable
    Prediction." *NeurIPS* 36 -- per-sample difficulty via feature-space Mahalanobis distance, penalizing
    overconfidence for calibration. VERIFIED LIVE (abstract); full-text fetch failed (binary).
12. Zadrozny, B. & Elkan, C. (2002). "Transforming Classifier Scores into Accurate Multiclass Probability
    Estimates." *KDD*. Canonical justification for isotonic regression as the right tool when the score-to-
    outcome relationship is too complex for closed form (exactly Sec. 4's use case). VERIFIED LIVE.
13. Niculescu-Mizil, A. & Caruana, R. (2005). *ICML* -- corroborates isotonic regression's practical effectiveness
    across model families. VERIFIED LIVE (cited within another source; not independently fetched).
14. arXiv:2002.10199, "Better Classifier Calibration for Small Data Sets" -- caveat: isotonic regression can drive
    apparent calibration error to zero while overfitting a small calibration set; directly informs Sec. 4's
    out-of-sample-transfer HARD-PASS/HARD-FAIL criterion. VERIFIED LIVE.
15. arXiv:2110.15231, "Exploring Covariate and Concept Shift for Detection and Calibration of OOD Data" -- caveat:
    calibration validity is in-distribution only; informs why Sec. 4's fallback is capped at P=0.35, not 0.50.
    VERIFIED LIVE.

**Substrate-internal (verified on disk this drill, load-bearing, not counted toward external total):**
- `experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py` (read in full; `_blocklocal_codebook_gsbc`,
  `_gsbc_dense`, `_blocklocal_codebook_synth`, `_decode_blocklocal`, `make_dense_bipolar_gsbc` -- reused verbatim
  for this drill's measurement, not reimplemented).
- `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` (read; confirmed actual
  `controls.dense_bipolar_cone` = 0.352, not the ~0.5 the prior drill recalled -- and confirmed this is the WRONG
  object regardless, per Sec. 1a).
- `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` (loaded; 10000-concept native GSBC_EXPAND2X pool,
  `nz_idx`/`nz_val`/`concept_rows`/`meta_json`).
- `data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz` (loaded; 177899-concept BGE
  `composite` semantic vectors + `id_order_json` name mapping -- the independent ground-truth ranking used for
  the decisive correlation test, Sec. 1-2).
- `hdlab/concept_encoder.py:849-850` (cited, not re-run this drill; the cat/kitten vs cat/airplane selftest gate
  this drill's finding structurally parallels and confirms extends through the GSBC compression pipeline).
- `notes/research_codebook_design_space_generalization_2026-07-06.md` (read in full; the parent drill this note
  resolves the open prerequisite for).

---

*Research complete 2026-07-06. Decisive homogeneity/heterogeneity question resolved directly against on-disk
data (not a lit-scan-based probability estimate) -- HETEROGENEOUS, at HARD-FAIL strength for the homogeneity
hypothesis, reproducible across 3 seeds, a 3x larger V, and immune to tail-trimming. Both lit-scan sub-agents'
search backend worked this round (12/15 citations live-verified). Notes-only drill per task instruction -- no
cell built, no dispatch, no routing/hand-off files (USER-locked ferry-deprecation override; the fallback cell
spec, Sec. 4, is delivered directly in this note for Director to act on or defer).*
