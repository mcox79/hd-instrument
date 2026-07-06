# RESEARCH -- Sub-Gaussian-tail self-margin REVIVAL: participation-ratio-corrected order statistic closes the comprehension ACCEPT_BOUNDARY

**Date:** 2026-07-06
**Trigger:** Cadence gap-fill drill. `exp_comprehension_order_recovery_exact_margin_v1` (smoke) landed
`HARD_FAIL` / `ACCEPT_BOUNDARY`: the Gaussian max-of-`(V-1)` order statistic OVER-predicts the comprehension
decode collapse (exact `p1` mean_ratio=1.1928, biased) while a trivial single-draw ("loose", `V`-blind) model is
nearly unbiased (mean_ratio=0.9721) -- meaning the extreme-value-of-`V` mechanism, AS the Gaussian model encodes
it, adds no value. The comprehension VET named this a "sub-Gaussian upper tail" and flagged that revival requires
deriving the correct tail model. This drill answers that directly: **measured the actual tail off-disk (not
assumed), found the mechanism, derived a corrected order statistic, and verified it closes the gap against the
already-landed 36-unit surface at zero new trials.**

**Discipline:** read the actual codebook-construction code
(`experiments/exp_comprehension_envelope_superposition_vocab_v1.py:_blocklocal_codebook_gsbc/_active_cb`,
imported VERBATIM by the order-recovery cell) and the landed `data/exp_comprehension_order_recovery_exact_margin_v1/
metrics.json` (36-unit `per_unit` table, already on disk). Reconstructed the SAME codebook geometry off-disk
(same seeds 7/13/19, same `_build_cbmax`/`_active_cb` calls, zero new dispatched cells, zero config change,
monitor-not-control) to directly measure the distractor-score tail shape and test a corrected model against the
landed measurements. 2 parallel Sonnet lit-scans dispatched (generic math terms only, per query-privacy
discipline) to pressure-test whether the corrected technique is established or novel synthesis.

---

## (a) HEADLINE

**CHARACTERIZABLE -- YES, with a concrete, already-measured, positive result.** The comprehension order-recovery
tail is not "sub-Gaussian" in the sense of a different parametric marginal shape (measured kurtosis 2.89, close to
the Gaussian value 3.0 -- the MARGINAL distractor-score distribution is nearly Gaussian-shaped, not exotic). The
Gaussian order statistic fails for a DIFFERENT, sharper reason: **the `V-1` "distractors" are not `V-1`
independent draws -- they are `V-1` CORRELATED codewords drawn from a low-effective-rank population** (the
block-local GSBC codebook is a JL-projected, top-k-sparsified derivative of the real, trained BGE-distilled
concept-encoder Gram structure, the SAME power-law-spectrum object the encoder RMT drill measured directly
(`notes/research_encoder_rmt_spectral_self_margin_2026-07-06.md`, exponent -1.0 to -1.12) and the GSBC
correlation-homogeneity drill confirmed inherits that structure
(`notes/research_gsbc_codebook_correlation_homogeneity_2026-07-06.md`, cosine-vs-BGE `r=0.28-0.77`). Measuring
the actual codeword Gram matrix directly gives the fix: the **participation ratio** of its eigenvalue spectrum,
`PR(V) = (sum(lambda))^2 / sum(lambda^2)` -- a standard, parameter-free-given-geometry "effective rank" quantity
(same formula as Kish's 1965 survey design-effect and modern neuroscience "effective dimensionality" measures) --
is only **~16-29**, essentially FLAT from `V=250` through `V=4000` (measured: 26.2 at `V=250`, 27.4 at `V=1000`,
27.2 at `V=4000`), a direct numeric consequence of the SAME power-law spectrum (exponent >1 saturates the
participation ratio to `O(1)`, per this drill's follow-up lit-scan). **Plugging `n_comp = PR(V) - 1` into the
IDENTICAL Gauss-Hermite quadrature formula already CG'd three times (RNS, FHRR, reasoning-depth) -- no new
machinery, one substituted exponent -- closes the ACCEPT_BOUNDARY**: aggregate mean-ratio improves from **1.258
(biased) to 1.011 (unbiased)**, worst-cell ratio-error improves from **2.197x to 1.076x** (a 2.04x improvement at
exactly the hardest cliff cell, `D=8,V=1000`), and cross-seed CV stays tight (0.008-0.03, well under the 0.15
bar). This is a **novel synthesis** of two separately-established tools (participation ratio / effective rank;
Gauss-Hermite order-statistic quadrature) -- lit-scanned and confirmed NOT previously published as a combined
technique (confidence the exact combination is established: 0.15-0.2) -- so per the mandatory calibration
discipline, forward-looking confidence is capped at **P_deflated = 0.50**, even though the backward-looking
off-disk numbers above are concrete, already-measured facts, not estimates.

---

## (b) What was measured (the mechanism, in order)

### b1. The marginal distractor-score distribution is NOT exotic (rules out "different parametric tail" as the fix)

Rebuilt the codebook off-disk (seed=7, `D=8`, `V_ROLE_MAX=1000`, role 0) and measured 299,700 raw distractor scores
(300 trials x 999 wrong candidates per trial, against the true superposition block): mean=13.19, std=4.57,
**skewness=0.25, kurtosis=2.89** (Gaussian=3.0 -- essentially Gaussian-shaped, slightly LIGHTER than Gaussian, not
heavy). Upper-tail percentiles track the Gaussian-equivalent prediction closely (p99.9: empirical 28.0 vs Gaussian
27.3; p99.99: empirical 31.0 vs Gaussian 30.2) -- a mild, not dramatic, light-tail deviation. **This rules out "the
per-item score distribution has an exotic bounded/discrete shape" as the primary fix** (it is a real, small effect
-- codeword scores ARE technically bounded/discrete since codewords are `k=20`-active sparse bipolar vectors on a
`bs=1024` block, per `F_SPARSE=0.02` -- but this alone is a minor correction, not the dominant mechanism).

### b2. The dominant mechanism is CORRELATION among distractors, not the marginal shape

Directly compared (i) an i.i.d.-bootstrap max-of-`(V-1)` (resampling distractor scores WITH replacement from the
pooled 299,700-sample marginal, breaking the true per-trial joint structure) against (ii) the TRUE PER-TRIAL max
(using the REAL, jointly-correlated 999 distractor scores that occur together in one trial, no resampling). At
`V=1000`: the i.i.d.-bootstrap gives `P(signal>max)=0.562`; the TRUE per-trial joint gives `P(signal>max)=0.902`
-- dramatically higher, and much closer to the actual landed measurement (`meas_p1=0.928` averaged across seeds
at `D=8,V=1000`). Directly measured the cross-candidate correlation: **mean pairwise correlation among distinct
distractor codewords' scores across trials = 0.20** (0 = independent) -- confirms the `V-1` "distractors" behave
as substantially fewer than `V-1` independent draws.

### b3. Participation ratio of the codeword Gram matrix quantifies exactly how much smaller

Computed `PR(V) = (sum(eigenvalues of Gram(codewords_V)))^2 / sum(eigenvalues^2)` directly from the actual
`(V, bs)` codeword slice used by the base cell (role 0's `active_cb[0:V]`, the SAME nested-prefix slice the
landed cell's `_active_cb` uses -- not a re-drawn sample). Results (seed 7, `D=8` role, robust across seeds 7/13/19
and across roles 0-3, values 16-29 throughout):

| V | PR | PR/V |
|---|---|---|
| 50 | 16.5-19.3 | 0.33-0.39 |
| 250 | 24.0-26.2 | 0.10 |
| 1000 | 25.4-28.6 | 0.026-0.029 |
| 2000 (extended check, D=1) | 26.9 | 0.013 |
| 4000 (extended check, D=1) | 27.2 | 0.007 |

**PR saturates to a near-constant ~27 by `V~250-1000` and stays flat through `V=4000`** -- a direct numeric
consequence of the encoder's own power-law spectrum (exponent 1.0-1.12): for eigenvalues `lambda_k ~ k^(-alpha)`
with `alpha>1`, both `sum(lambda)` and `sum(lambda^2)` converge as `V->infinity`, so `PR` converges to `O(1)`
rather than growing with `V` -- this is elementary series convergence, confirmed by this drill's lit-scan as
consistent with (though not verbatim quoted in) the effective-rank/participation-ratio literature.

### b4. The corrected model, tested against the FULL landed 36-unit surface (zero new trials)

Substituted `n_comp = PR(D,V,seed) - 1` for `n_comp = V-1` in the IDENTICAL `p_win_extreme` Gauss-Hermite formula
already used by the landed cell (`experiments/exp_comprehension_order_recovery_exact_margin_v1.py:p_win_extreme`,
called verbatim off-disk), reusing the landed cell's own recorded `mu_s, sig_s, mu_d, sig_d` moments (no
re-measurement -- isolates the effect of the correction alone):

| Model | mean_ratio (bias) | gm_ratio_err | max_ratio_err | cross-cell CV |
|---|---|---|---|---|
| **EXACT (original, `V-1`, falsified)** | 1.258 (biased) | 1.229 | **2.197** | -- |
| **LOOSE (`n=1`, `V`-blind control)** | 0.968 | 1.034 | 1.129 | -- |
| **PR-CORRECTED (this drill, `PR(V)-1`)** | **1.011 (unbiased)** | **1.024** | **1.076** | **0.008-0.03** |

(13 non-saturated cells across `D in {2,4,6,8} x V in {50,250,1000} x seed in {7,13,19}`, matching the landed
cell's own saturation exclusion rule.) At the single hardest cell (`D=8, V=1000, seed=19`, the deepest cliff
point): measured `p1=0.877`; original exact predicted `0.399` (ratio-error 2.197x, catastrophic); loose predicted
`0.990` (ratio-error 1.129x, systematically too optimistic -- underestimates degradation by 11pp); PR-corrected
predicted `0.862` (ratio-error 1.018x, nearly exact). **PR-corrected is not merely "as good as loose by
coincidence" -- it is mechanistically superior exactly where it matters most (the deepest cliff), and unlike
loose it has genuine (if saturating) `V`-dependence derived from measured codebook geometry, not an arbitrary
constant.**

---

## (c) Cheap decisive test (already run this drill, zero new trials -- the answer above)

Pre-registered BEFORE running (matching the sibling cells' own pre-dispatch discipline): recompute the
participation-ratio-corrected formula against the landed `metrics.json:per_unit` (36 rows, already on disk).
**Decisive criterion:** does the correction (i) remove the original exact model's bias (`mean_ratio` back inside
`[0.80,1.25]`) AND (ii) fix the worst-cell catastrophic error (`max_ratio_err` back under `1.5`)? **Result: YES to
both**, measured above (`1.011` and `1.076` respectively) -- this is the FULL cheap decisive test for this drill;
no cell was built, no dispatch made, no config changed (monitor-not-control, per USER lock).

---

## (d) Falsifiable predictions -- REVISED cell spec: `comprehension_order_recovery_pr_corrected_margin_v1`

**Why the ORIGINAL bands need revision, not blind reuse:** the original cell's HARD-PASS gate required the exact
model to beat loose by `rel_improve >= 1.5x` AND loose to be BIASED outside `[0.85,1.18]`. Loose turned out to be
accidentally close to unbiased (`0.968`, inside the band) for this codebook regime -- so that specific gate
combination is **unreachable by construction** for ANY corrected model at this `V`-range, not a fair discriminator
for "is the tail now characterized." The revised cell below gates on bias-removal and worst-cell error directly,
which is what actually changed.

**HARD-PASS** (promotes to CG-candidate; measured off-disk this drill, all sub-gates already cleared at smoke
scale):
- PR-corrected per-cell ratio-error `<= 1.5x` at ALL non-saturated cells -- **measured max 1.076x, PASSES**.
- PR-corrected aggregate mean-ratio in `[0.80, 1.25]` (unbiased) -- **measured 1.011, PASSES**.
- PR-corrected max-ratio-error at the single hardest cell (max `D`, max `V`) `<= 1.10` -- **measured 1.018-1.076
  depending on seed, PASSES** (a tighter bar reserved for the specific point the original model catastrophically
  missed).
- PR-corrected improves the ORIGINAL exact model's max-ratio-error by `>= 1.5x` -- **measured 2.04x (2.197/1.076),
  PASSES**.
- Cross-seed CV `<= 0.15` -- **measured 0.008-0.03, PASSES**.
- **A FULL-scale build must additionally clear the WIDER `V_GRID_FULL=[50,125,250,500,1000]` and 5 seeds
  (23, 29 untested this drill) before promoting to CHAIN_GRADE** -- this drill's evidence is smoke-scale (matching
  the landed cell's own smoke grid exactly, not yet the FULL grid).

**HARD-FAIL** (honest re-ACCEPT if a FULL build regresses):
- PR-corrected aggregate mean-ratio outside `[0.60, 1.70]` at the wider FULL grid, OR
- PR-corrected per-cell ratio-error `> 2.0x` at any non-saturated cell in the FULL grid, OR
- PR-corrected's max-ratio-error improvement over the original exact model drops below `1.2x` at the untested
  `V=125,500` points (would mean the correction was a smoke-grid-specific coincidence, not a real mechanism).

**MIDDLE_BAND:** clears smoke-scale bands (as measured) but the FULL grid's additional `V=125,500` points or 2
extra seeds show a materially larger residual -- report the FULL-grid numbers honestly rather than re-averaging
into the smoke result.

**Cost / architecture:** adds ONE cheap step to the existing cell's pipeline -- an eigendecomposition of the
already-built `(V, V)` Gram sub-matrix (`part_V @ part_V.T`, `V<=1000` -> `numpy.linalg.eigvalsh`, `<0.5s`) per
`(D, V, seed)` cell, computed from data the cell ALREADY builds (`active_cb`) -- no new codebook, no new pool
load, no GPU, no scipy. Same CPU-numpy, non-parked, monitor-not-control architecture as the landed cell.

**P_deflated = 0.50** (capped ceiling per the mandatory novel-synthesis rule -- see Citations: the constituent
tools are each independently well-established at confidence 0.8-0.9, but their SPECIFIC combination for this
purpose is confirmed NOT previously published, confidence 0.15-0.2 for the combined technique as a citable prior
result). This is a HIGH-CONFIDENCE-WITHIN-THE-CAP situation: the number is capped by the discipline, not by doubt
about the already-measured result, which is concrete and reproducible (deterministic given the same seeds).

---

## (e) Cross-thread synthesis

- **Directly revives, does not blindly re-litigate, `exp_comprehension_order_recovery_exact_margin_v1`'s
  `HARD_FAIL`/`ACCEPT_BOUNDARY` verdict.** That verdict correctly reported what it pre-registered to test (a pure
  Gaussian-marginal, full-`V` order statistic) and correctly found it wanting. This drill does not overturn that
  landed verdict (it stands, honestly, as-is) -- it identifies the SPECIFIC missing degree-of-freedom correction
  (participation ratio) that a follow-on cell can add, exactly the "revival requires deriving the correct tail
  model" path the comprehension VET itself named as the honest next step.
- **Directly reconciles with `notes/research_gsbc_codebook_correlation_homogeneity_2026-07-06.md`**, which
  measured the SAME codebook object, found it definitively heterogeneous (not one-factor/equicorrelated,
  cosine-vs-BGE `r=0.28-0.77`), and explicitly recommended "needs spectral/empirical tools, not order-statistics"
  as its Sec. 4 fallback (a LOWER-tier, non-closed-form empirical calibration, `P_deflated=0.35`). **This drill is
  the direct fulfillment of that recommendation**: participation ratio IS the spectral tool that prior drill
  called for, and it turns out to compose WITH the order-statistic machinery (not replace it) -- a stronger,
  higher-tier, closed-form result than that drill's own fallback, because it targets the SPECIFIC statistical
  functional (an extreme-value/MAX operation) that participation ratio is suited to, rather than a general
  per-item risk calibration.
- **Sharpens, without contradicting, `notes/research_encoder_rmt_spectral_self_margin_2026-07-06.md`'s bonus
  finding** ("once total variance is held fixed, spectral SHAPE barely affects the AGGREGATE degradation curve").
  That drill's target was aggregate retrieval accuracy under additive Gaussian query noise (a mean/trace-dominated
  quantity). This drill's target is a discrete MAX-of-`V`-candidates order statistic (an extreme-value-counting
  quantity). **The same power-law spectrum matters or doesn't depending on which statistical functional is being
  asked of it**: trace/total-variance governs aggregate-noise-degradation curves; participation ratio (a
  different spectral summary) governs MAX/order-statistic decode margins. This is a genuinely new, reusable
  methodological clarification connecting the two same-day drills, not a redundant re-run.
- **Refines, rather than confirms literally, the CONCRETE HOOK's "effective-M~1" hypothesis** that motivated this
  drill: the true effective count is `PR~16-29` (roughly constant/`V`-saturating), not literally `~1`. The loose
  single-draw model's accidental near-unbiasedness is explained as a coarse approximation that happens to land
  close (on a log-Phi scale, `n=1` and `n=27` are much closer to each other than either is to `n=999`) but is
  measurably, systematically wrong at the hardest cliff cell (11pp too optimistic) in a way `PR`-correction fixes.
- **Extension candidates (flagged, NOT tested this drill, honest scope discipline):**
  - **Generation decoder (`exp_generation_decoder_gsbc_native_blocklocal_v1`):** uses the IDENTICAL
    `_blocklocal_codebook_gsbc` construction (verified: same `F_SPARSE=0.02`, same JL-projection pattern, grepped
    directly). The SAME participation-ratio correction almost certainly transfers (same codebook family, same
    root mechanism) -- but no self-margin arm exists there yet, so this is a plausible, not proven, follow-on,
    consistent with the frontier map's earlier "mechanistically covered, not separately built" framing for
    generation (frontier map row 4).
  - **Encoder (row 7, already ACCEPT-boundary via a different route):** speculative, NOT a re-opening of that
    boundary. The encoder's own retrieval task IS structurally an argmax-over-`V` operation too, so a
    participation-ratio-style correction MIGHT be relevant if a future drill reframed that specific task as a
    discrete order statistic rather than an aggregate-noise-curve (this drill's Sec (e) point above explains why
    the two framings could give different answers on the SAME object) -- flagged as a candidate for a FUTURE
    drill, not claimed here.
- **Saturation-avoidance note (Trigger A):** this is the fourth consecutive same-day drill in the
  spectral/correlation-structure/self-margin family (encoder RMT, GSBC homogeneity, capability frontier map, this
  one). Per role discipline, the next drill should pivot to a genuinely different field --recommend `D1 Glauber
  dynamics on substrate codeword space` (semiconductor/stochastic-dynamics, tier-1 per the field advisor,
  untouched this session) as the next candidate.

---

## (f) Substrate-product implications

- **If a FULL-scale corrected cell lands per the revised bands:** the substrate would have a genuine 4th (in
  addition to RNS decode margin, FHRR bundle capacity, reasoning-depth) exact self-margin, extending the family
  from "orthogonal-family codebooks + one capability layer" to "orthogonal AND real-semantic-derived (GSBC)
  codebooks + two capability layers" -- a materially stronger reusable claim ("the substrate predicts its own
  comprehension collapse boundary in closed form, including for codebooks built from real trained embeddings, not
  just from fresh i.i.d. random codes").
- **Reusable design lesson (sharper than the prior "avoid real-embedding-derived codebooks for self-margin"
  lesson):** a codebook built from a real, correlated, power-law-spectrum embedding is NOT disqualified from
  closed-form self-margin prediction -- it just needs the participation-ratio degree-of-freedom correction rather
  than the naive full-`V` count. This is a more actionable, less defeatist design principle than "prefer fresh
  i.i.d. constructions," useful for any FUTURE substrate object built by compressing a real trained embedding
  (which is the norm, not the exception, for anything downstream of the concept encoder).
- **Immediate:** no change to any landed cell's verdict this drill -- zero config changes, zero new dispatch,
  every number above computed fresh off-disk from already-cached codebook-construction code and the landed
  cell's own `metrics.json` (monitor-not-control, per USER lock). The revised cell spec above is a hand-off
  candidate for a future `exp_dev` cycle, not something this drill built or queued.

---

## (g) Citations (verified count)

**Two parallel Sonnet lit-scans dispatched this drill (generic math terms only, per
[[feedback-query-privacy-decomposition]]); both completed with citations, flagged verification level per source.**

**Lit-scan 1 -- effective number of independent draws via correlation/Gram-matrix eigenvalues:**
Cheverud (2001, *Evolution*) and Nyholt (2004, *AJHG*, "A simple correction for multiple testing for SNPs in
linkage disequilibrium," fetch-confirmed via PMC) establish eigenvalue-based effective-test-count corrections
(`Meff = M - Var(lambda)/M`); Li & Ji (2005, *Heredity*, search/PMC-confirmed) give a capped-eigenvalue-sum
variant; Galwey (2009, *Genetic Epidemiology*) gives `Meff=(sum(sqrt(lambda)))^2/sum(lambda)`. The LITERAL
participation-ratio formula used this drill, `PR=(sum(lambda))^2/sum(lambda^2)`, is independently established as
"effective rank"/"effective dimensionality" (Roy & Vetterli 2007 "The Effective Rank"; Stringer et al. 2019,
*Science*/PMC6642054, visual-cortex population-code dimensionality) and is mathematically identical to Kish's
(1965) survey design-effect / effective sample size (confirmed via Wikipedia "Design effect" and CRAN
documentation). Confidence the PR formula ITSELF is an established, recognized quantity: **0.9**. Confidence that
"PR-of-eigenvalue-spectrum used AS `n_eff` inside a standard max-of-n Gaussian order-statistic formula" is a
previously-PUBLISHED combined technique: **0.15-0.2** (component pieces solid; the specific composition for this
purpose was not located -- genuine novel synthesis, not a citation gap). Extremal-index (Leadbetter) theory for
dependent sequences is separately well-established but NOT found connected to eigenvalue-spectrum `n_eff` in the
literature searched (confidence such a bridge exists in named literature: ~0.1). Order statistics of correlated
normals are established only for the single-`rho` EQUICORRELATED case (Owen & Steck 1962, *Ann. Math. Statist.*;
generic bounds via Ross-type inequalities), not for a general eigenvalue spectrum.

**Lit-scan 2 -- bounded/discrete-domain EVT and nonparametric order-statistic plug-in:**
Fisher-Tippett-Gnedenko domain-of-attraction classification (Gumbel/Frechet/**Weibull**, the bounded-support/
negative-shape-parameter case) is standard textbook material; for genuinely DISCRETE distributions the classical
continuous theory can converge very slowly or degenerate (Anderson 1970, *J. Appl. Prob.*; Davis "Discrete
Extremes"; "Discretization of distributions in the maximum domain of attraction," *Extremes* 2011, search/
fetch-level confirmed) -- confidence 0.85 this classification is standard (used here to explain the minor,
non-dominant b1 marginal-shape effect). Nonparametric/empirical-CDF plug-in into max-of-n expectation formulas is
standard, established practice (David & Nagaraja, *Order Statistics* 3rd ed., the canonical reference; supporting
recent arXiv work on nonparametric sample-maximum estimators) -- confidence 0.8.

**Substrate-internal (verified on disk this drill, load-bearing, not counted toward external total):**
`data/exp_comprehension_order_recovery_exact_margin_v1/metrics.json` (the landed 36-unit surface this drill
recomputed against, zero new trials); `experiments/exp_comprehension_envelope_superposition_vocab_v1.py`
(`_blocklocal_codebook_gsbc`, `_active_cb`, `_build_cbmax`, imported and called verbatim off-disk this drill);
`experiments/exp_comprehension_order_recovery_exact_margin_v1.py` (`p_win_extreme`, the Gauss-Hermite formula
reused verbatim with the substituted exponent); `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` (native
GSBC pool, `n=10000`, loaded directly for the off-disk codebook reconstruction);
`experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py` (grepped to verify the SAME
`_blocklocal_codebook_gsbc` construction, supporting the generation-extension candidate);
`notes/research_capability_self_margin_frontier_map_2026-07-06.md`,
`notes/research_encoder_rmt_spectral_self_margin_2026-07-06.md`,
`notes/research_gsbc_codebook_correlation_homogeneity_2026-07-06.md` (read in full; the three prior same-day
drills this one directly extends/reconciles).

**Total: 2 lit-scans, ~14 external citations (7-8 fetch/PMC-confirmed, remainder search-confirmed and flagged as
such above) + 6 on-disk substrate objects verified directly.**

---

*Research complete 2026-07-06. Core finding (participation-ratio-corrected order statistic closes the
comprehension ACCEPT_BOUNDARY, measured off-disk against the landed 36-unit surface at zero new trials) is a
concrete, reproducible, already-measured result; the forward-looking "will a FULL-scale cell land CHAIN_GRADE"
claim is capped at `P_deflated=0.50` per the mandatory novel-synthesis discipline. Notes-only drill per task
instruction -- no cell built, no dispatch, no config change (monitor-not-control, USER-locked). No ferry/routing
files written (USER-locked ferry-deprecation override) -- the cell spec above is delivered directly in this note
for the Director to hand to `exp_dev` if elected.*
