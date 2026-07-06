# Research — deriving the EXACT decode-collapse constant for the phase-linear RNS codebook (union-bound -> exact order-statistic)

**Date:** 2026-07-06
**Trigger:** Follow-on theory drill on the just-VET'd `rns_subblock_margin_selfcheck_v1` (HARD_PASS, MM tier).
The MM cell validated the `SB* ~ sigma^2` scaling law but its closed-form prediction ("correct" arm, the
textbook M-ary union bound) over-predicts the collapse boundary `SB*` by a measured `gm_ratio_err` of 2.39-2.73x
(all three moduli: m=9 -> 2.727x, m=19 -> 2.388x, m=43 -> 2.544x; `data/exp_rns_subblock_margin_selfcheck_v1/metrics.json`,
verified on disk this drill). Director's question: is the EXACT prefactor derivable, and can it tighten the
prediction from ~2.5x to the CG-promotion bar of <1.5x? **Notes-only drill: no cell built, no dispatch.**
**Discipline:** read the actual cell source in full (`experiments/exp_rns_subblock_margin_selfcheck_v1.py`) before
any external dispatch, to get the EXACT formula and exact SB* definition (not just the summary metrics) --
this let the derivation below be checked directly against the landed metrics rather than guessed. 3 parallel
Sonnet lit-scans (generic math terms only, no substrate-novel mechanism names off-platform, per
[[feedback-query-privacy-decomposition]]). Lit-scan calibration applied where relevant (deflate 0.15-0.25;
novel-synthesis cap 0.50) -- see Sec. 5 for the explicit tension this drill flags (the derivation is unusually
well-grounded for a "novel synthesis," being a zero-free-parameter theoretical formula independently checked
against the FULL landed measured data, not a fit).

---

## HEADLINE

**Yes -- the exact prefactor is derivable in closed form, and it is NOT the min-distance/chord-length route (a)
or the random-matrix/free-probability route (c); it is route (b), the exact order-statistic of the m-1
competitors, and on the substrate's OWN landed data it tightens the geometric-mean SB* offset from 2.39-2.73x
down to 1.01-1.15x -- comfortably inside the <1.5x CG-promotion bar the VET named.** The mechanism: this
codebook's m-1 "competitor" residues, under additive Gaussian noise, are (to a precision this drill verified
directly against the landed metrics, RMS residual 0.012 vs the union bound's 0.264) **mutually independent**
Gaussian correlation statistics -- not adjacent-on-a-circle competitors the way M-PSK symbols are. That
independence is a real structural fact about THIS codebook (random per-dimension integer frequencies `k_j`
decorrelate any two codewords' cross terms to ~0 in expectation), not an assumption borrowed from elsewhere, and
it means the textbook-exact answer for "M-ary orthogonal/simplex signaling" applies directly: `P_correct =
E_x[Phi(x*sqrt(2*sb)/sigma)^(m-1)]` where `x ~ N(1, sigma^2/(2*sb))` -- a single, smooth, rapidly-converging
1-D integral (Gauss-Hermite quadrature, ~20-30 points, standard practice per the lit-scan), not the naive
union-bound multiplication `(m-1)*Q(sqrt(sb)/sigma)` the landed cell currently uses. This is the SAME
theoretical family the landed cell's own docstring already cites ("THEORETICAL@Proakis... M-ary orthogonal
signalling") -- the landed cell used the LOOSE (union-bound) corollary of that same theory, not the theory's own
exact result. **Feasibility answer (Q2): YES, decisively** -- verified this drill by recomputing the exact
integral on the landed cell's OWN `(m, sb_grid, sigma)` grid and comparing to the ALREADY-MEASURED `SB*_meas`:
ratio lands at 1.01-1.15x, not merely under 1.5x but close to the statistical noise floor of the 800-trial x
5-seed measurement itself. **A cell spec is delivered below (Sec. 4)**, non-parked, remote-dispatchable, extending
`rns_subblock_margin_selfcheck_v1` with a 4th prediction arm (`predict_exact`) alongside the existing
`predict_correct` (renamed conceptually to "union-bound arm," kept as a live control) and `predict_wrong_scaling`.
P_deflated for a fresh FULL dispatch reproducing this = **0.50** (capped novel-synthesis per role discipline; see
Sec. 5 for why this drill's confidence is unusually high for that cap, and why the cap is kept anyway).

---

## 1. WHY THE UNION BOUND WAS LOOSE -- mechanism, not mystery

The landed cell's `pred_acc_correct(sb, m, sigma) = 1 - min(1, (m-1)*Q(sqrt(sb)/sigma))` is the standard
first-order union bound (Boole's inequality / first-truncation Bonferroni) over the m-1 pairwise events
"competitor c's noisy correlation beats the true residue's." This drill derived, from the cell's OWN decode
arithmetic (`sims = Re(cb @ conj(V).T)/sb`, additive complex Gaussian noise `~ CN(0, sigma^2)` per dim), the exact
distribution of the decision statistics:

- `sim[true] ~ N(1, sigma^2/(2*sb))` (mean 1 exact from `|codeword|^2=1`; noise variance derived exactly from the
  linear-combination-of-Gaussians identity, not asymptotic).
- `sim[c] ~ N(0, sigma^2/(2*sb))` for each competitor c=1..m-1, and -- the load-bearing structural fact --
  **these m-1 statistics are mutually independent of each other and of `sim[true]`**, because the codebook's
  per-dimension frequencies `k_j` are drawn i.i.d. uniform in `[1,m)`, which decorrelates any two DIFFERENT
  codewords' cross term to ~0 in expectation (confirmed empirically this drill: the exact-integral formula, which
  assumes exactly this independence and adds NO other correction, tracks the FULL measured accuracy curve to RMS
  error 0.012 across all 120 measured `(m,sigma,sb)` points -- if the independence assumption were meaningfully
  wrong, this residual would not be this small).

Given genuine independence, the EXACT (not bounded, not approximate) probability that the true residue beats
ALL m-1 competitors is `P_correct = E_x[Phi(z(x))^(m-1)]`, `z(x) = x*sqrt(2*sb)/sigma`, `x ~ N(1,sigma^2/(2sb))`
-- literally the joint CDF of the maximum of m-1 i.i.d. standard normals, conditioned on the true statistic's
draw. The union bound is the first-order Taylor/Boole truncation of this same exact quantity (`1-(1-Q)^n ~= nQ`
for small `Q`) -- it is not a DIFFERENT theory, it is a DELIBERATELY LOOSENED corollary of the exact one the cell
already cites. This directly answers the task's framing of the choice as (a) vs (b) vs (c):

- **(a) min-distance / chord-length route (2*sin(pi/m)-type):** WRONG MODEL for this codebook. That framing
  applies to M-PSK, where competitors have a genuine geometric ADJACENCY (only the 2 angularly-nearest symbols
  dominate error). This codebook's random-per-dimension-frequency construction gives NO such adjacency -- every
  competitor is exchangeable/equidistant from the true residue in expectation (lit-scan 1 confirms this
  explicitly: "For orthogonal/simplex signaling all M-1 competitors are exchangeable/equidistant, so the
  QAM/PSK-style nearest-neighbor-only shortcut doesn't apply"). A "2 nearest neighbor" correction (this drill's
  first hypothesis, tested and REJECTED before external dispatch -- see Sec. 5) does NOT reconcile the observed
  ratios across m=9/19/43 with a single consistent target error rate, confirming (a) is the wrong route for
  THIS construction specifically (it would be right for a true M-PSK-style adjacent-phase codebook, which this is
  not, despite superficially being "roots of unity").
- **(b) tighter union bound / exact order-statistic:** THIS is the tight, closed-form, verified route. It is not
  merely "tighter than Bonferroni" -- for genuinely independent competitors it is EXACT (the binomial expansion
  `1-(1-Q)^n` IS the closed-form answer, no residual approximation error beyond the independence assumption
  itself, which this drill verified holds to ~1% at these config points).
- **(c) random-matrix / free-probability edge:** CONFIRMED NOT NEEDED, and confirmed WHY not, by a dedicated
  lit-scan (citations in Sec. 6): RMT/free-probability machinery (Tracy-Widom edge statistics, R-/S-transform
  free convolution) is built for STRONGLY CORRELATED spectra (eigenvalue repulsion, Vandermonde structure) or
  genuinely non-commuting ("free") objects -- not independent scalars. The lit-scan found direct evidence
  (Cizeau & Bouchaud-style heavy-tailed-random-matrix analysis) that RMT edge statistics THEMSELVES degenerate
  back to classical extreme-value theory once true independence dominates and repulsion is weak -- i.e., reaching
  for RMT here would not produce a different or better answer, it would (at best) rediscover the same classical
  order-statistics result this drill already derived and verified directly.

**Answer to Q1: (b) is tightest and closed-form** (a smooth, well-behaved 1-D integral, standard Gauss-Hermite
quadrature, same "closed form" status the landed cell already grants to `Q(x)` itself, which is also just an
integral). (a) is the wrong mechanism for this specific codebook (no adjacency structure). (c) is confirmed
inapplicable and would not improve on (b) even if invoked.

---

## 2. NUMERIC VERIFICATION -- checked directly against the landed metrics, not just derived on paper

This drill computed `pred_acc_exact(sb, m, sigma)` (the formula above, via `scipy.stats.norm` + `scipy.integrate.quad`)
on the landed cell's EXACT `(MODULI, SB_GRID, SIGMAS)` grid and compared to the ALREADY-MEASURED accuracy surface
in `data/exp_rns_subblock_margin_selfcheck_v1/metrics.json` (120 measured points, `per_unit` array). Two checks:

**(A) Full pointwise fit across all 120 measured `(m,sigma,sb)` points** (not just the SB* crossing):

| | union-bound arm (`predict_correct`, landed) | exact-integral arm (`predict_exact`, this drill) |
|---|---|---|
| Max absolute error vs measured | 0.687 | 0.047 |
| RMS error vs measured | 0.264 | 0.012 |

The exact-integral arm's residual (0.012 RMS) is at the scale of ordinary Monte-Carlo seed noise for 800 trials x
5 seeds -- i.e., this zero-free-parameter formula essentially reproduces the measured curve within measurement
noise, not merely "close."

**(B) SB* geometric-mean offset, recomputed the SAME way the cell's own `classify()` function does it**
(`_cross_sb` 0.5-crossing interpolation, `_gm_ratio_err` geometric-mean log-ratio, same `SB_GRID`):

| modulus | `gm_ratio_err` union-bound (landed, MEASURED) | `gm_ratio_err` exact-integral (this drill) | `p_meas` (measured exponent) | `p_exact` (this drill) |
|---|---|---|---|---|
| m=9 | 2.727x | **1.109x** | 1.967 | 2.009 |
| m=19 | 2.388x | **1.050x** | 1.976 | 1.989 |
| m=43 | 2.544x | **1.014x** | 1.976 | 2.010 |

All three moduli land inside the <1.5x CG-promotion bar with margin to spare, and the scaling exponent match is
if anything tighter than the union-bound arm's own (`exp_err_correct` was up to 0.192 for m=43; the exact-integral
arm's exponents cluster even closer to the theoretical 2.0, 1.99-2.01 vs measured 1.97-1.98).

**Cross-check on option (a) before rejecting it (per [[feedback-dont-dismiss-adjacent-methods]]):** this drill
also tested whether a "2 nearest-neighbor" correction (replacing `(m-1)` with `2` in the SAME union-bound
formula, the natural guess by analogy to M-PSK) could explain the observed ratios. Solving for the implied
target error rate `P_target` that would make `ratio = ln((m-1)/P)/ln(2/P)` match each modulus's observed ratio
gives WILDLY inconsistent values (`P~0.90` for m=9, `P~0.41` for m=19, `P~0.28` for m=43) -- i.e., no single
"2 nearest neighbors" story fits all three moduli simultaneously. This confirms (a) is genuinely the wrong
mechanism for this codebook (no adjacency structure exists to exploit), not merely a less-convenient derivation
of the same right answer -- and that the RIGHT explanation is route (b)'s full independence-based order
statistic, which DOES fit all three moduli simultaneously with no per-modulus tuning (Sec. 2's table above uses
the exact same formula, zero free parameters, across m=9/19/43).

---

## 3. FEASIBILITY (Q2), ANSWERED PLAINLY

**Yes, and by a wide margin, not marginally.** The <1.5x bar is cleared with room (1.01-1.15x measured), using a
formula with ZERO free/fitted parameters (both `pred_acc_exact`'s mean-separation term of 1 and its variance
term `sigma^2/(2*sb)` come directly from the codebook's own construction, not a curve fit to the measured data --
the measured data was used only to CHECK the derivation, exactly the same epistemic status as the landed cell's
existing `formula_selftest()`). The honest caveat (kept prominent, not buried): the independence assumption
underlying the exact formula is a structural property of THIS specific phase-linear, random-per-dimension-
frequency codebook -- it is not a universal fact about "roots-of-unity codebooks" in general (an M-PSK-style
codebook with SHARED, not per-dimension-random, frequencies would have genuine competitor adjacency and would
need option (a) instead). The formula's excellent fit is evidence the substrate's actual construction has this
independence property to good approximation at these config points (`sb>=4`), not a guarantee it would hold
under a different codebook-construction choice.

---

## 4. THE CORRECTED-PREFACTOR CELL -- spec only, extends `rns_subblock_margin_selfcheck_v1`

**Design principle:** minimal-diff extension of the landed, HARD_PASS `rns_subblock_margin_selfcheck_v1`. Reuse
`phasor_codebook()`, `collapsed_codebook()`, `decode_acc()`, `run_sweep()`, and `_cross_sb`/`_loglog_slope`/
`_gm_ratio_err` VERBATIM (no changes to the measurement machinery, which already HARD_PASSED). Add exactly one
new prediction function and widen the classify/report surface to carry a 4th arm.

**New function (the only new arithmetic):**
```
def pred_acc_exact(sb: int, m: int, sigma: float) -> float:
    """EXACT M-ary-orthogonal-signaling order-statistic (Hajek ECE361 L8 eq 8.1 / Proakis Ch.4 family):
    P_correct = E_x[ Phi(x*sqrt(2*sb)/sigma)^(m-1) ],  x ~ N(1, sigma^2/(2*sb)).
    Exact given mutually-independent competitor statistics (verified this codebook's construction gives this
    to ~1% via the union-bound-vs-exact residual check, notes/research_decode_margin_exact_prefactor_derivation_2026-07-06.md).
    Evaluated via Gauss-Hermite quadrature (scipy.integrate.quad or a fixed ~24-point Gauss-Hermite rule)."""
```

**Arms (per (m, sb, sigma), all PAIRED on the same measured surface already produced by the landed cell -- no
new measurement trials needed, only new prediction curves against the SAME `metrics.json` `per_unit` data,
OR re-measured fresh with identical seeds for a clean FULL landing):**
- `measured_decode` : unchanged, reused. [MECHANISM]
- `predict_union` : the landed cell's existing `pred_acc_correct`, KEPT as a live control/baseline arm (renamed
  in reporting only, not in code, to avoid breaking any existing consumer of `pred_correct`). [CONTROL / BASELINE]
- `predict_exact` : the new function above. [PREDICTION, the genuine new discriminator]
- `predict_wrong_scaling` : unchanged, reused. [CONTROL 1, unaffected by this change]
- `collapsed_codebook` : unchanged, reused. [CONTROL 2, unaffected]

**Discriminator / controls (additive to the landed cell's existing gates, does not replace them):**
- **MECHANISM (new)**: `predict_exact`'s `gm_ratio_err` (computed identically to the landed `_gm_ratio_err`)
  must be `<= 1.5` at every modulus -- the CG-promotion bar named by the Director.
- **CONTROL (new, relative-improvement gate)**: `predict_exact`'s `gm_ratio_err` must be strictly better than
  `predict_union`'s at every modulus, by at least 1.5x (i.e. `gm_ratio_err_union / gm_ratio_err_exact >= 1.5`)
  -- isolates that the independence-based exact treatment is doing genuine work, not just re-parameterizing
  noise.
- **Retained from landed cell, unchanged**: scaling-exponent bands (`p_meas` in `[1.6,2.4]`), wrong-scaling
  control separation, collapsed-codebook control collapse, reachability. All of these already HARD_PASSED and
  are NOT expected to move (the new arm only changes the prefactor treatment, not the measurement or the other
  two controls).

**Pre-registered bands (deflated per role discipline):**
- **HARD-PASS**: `predict_exact` achieves `gm_ratio_err <= 1.5x` at ALL 3 moduli (the CG-promotion bar), AND
  is `>= 1.5x` tighter than `predict_union` at all 3 moduli, AND all of the landed cell's existing HARD_PASS
  gates (scaling exponent, wrong-scaling separation, collapsed control) continue to pass unchanged.
  P_deflated = **0.50** (capped novel-synthesis per role discipline -- see Sec. 5 for the explicit tension:
  this drill's OWN recomputation against the landed data already shows 1.01-1.15x, well inside the band, so a
  fresh FULL dispatch reproducing this on a NEW measurement (different seeds, same grid) is expected to pass;
  the cap is kept per discipline rather than raised, because a fresh dispatch could still surface an
  implementation bug in porting the derivation to code, a numerical-integration edge case at the smallest
  `sb=4` grid point, or a subtle seed-dependent fluctuation not present in the single seed-set analyzed here).
- **HARD-FAIL**: `predict_exact`'s `gm_ratio_err` exceeds 4x at any modulus (i.e., the "exact" formula performs
  WORSE than or comparable to the existing union-bound arm's own HARD_PASS threshold) OR the independence
  assumption breaks down badly enough that `predict_exact` tracks the measured curve no better than
  `predict_union` (relative-improvement control fails) -- this would mean the codebook's actual competitor
  correlation structure is NOT well-approximated as independent at production scale, a genuinely useful negative
  (it would mean the number-theoretic decorrelation argument in Sec. 1 does not hold as cleanly at other
  moduli/seeds as it did here, and any future capacity claim for this codebook should stay with the looser,
  already-HARD_PASSED union-bound arm rather than the tighter one).
- **MIDDLE**: `predict_exact` improves on `predict_union` (relative-improvement control passes) but does not
  reach the `<=1.5x` bar (lands in `(1.5, 4]x`) -- a legitimate partial result: tighter, but not tight enough to
  claim the substrate "knows its own decode-margin boundary precisely."

**Cost:** trivially cheap -- one new ~15-20 line function (`pred_acc_exact`, using `scipy.stats.norm.cdf/pdf` +
`scipy.integrate.quad`, both already available in the repo's `.venv`) plus report-surface widening in `classify()`
to carry a 4th arm's `gm_ratio_err`/`p_exact`. No new measurement trials required for the retrospective check
(can run entirely against the ALREADY-LANDED `metrics.json`'s `per_unit` array as a zero-cost validation before
any new dispatch); a clean FULL re-landing (same seeds/grid as the landed cell, ~25s CPU, no GPU, no referent
gate, same remote-dispatchable class) would make the new arm's numbers a first-class, independently-verified
metrics.json entry rather than a notes-only recomputation. Estimated total diff: ~40-60 new lines against the
existing ~680-line landed cell.

**Autonomy note (exp_dev owns, per [[feedback-no-experiment-design-in-prompts]]):** exact quadrature method
(scipy `quad` vs a fixed Gauss-Hermite rule), integration window width (this drill used `mean +/- 12*std`, ample
for double-precision accuracy at these `sigma`/`sb` ranges but exp_dev should verify at the smallest `sb=4` grid
point where `std` is largest), whether to re-run FULL fresh or validate retrospectively against the landed
`metrics.json` first, and the exact 1.5x/4x band placement in code (this note names the mechanism and the
falsifiable comparison, not the final implementation).

---

## 5. HONESTY ON THE CALIBRATION TENSION (per [[feedback-lit-scan-calibration-penalty]])

This drill's confidence is unusually high for something bearing the standard "novel-synthesis, cap P at 0.50"
label, and that tension is worth stating plainly rather than smoothing over. The derivation used ZERO free
parameters (both the mean-separation and variance terms came directly from the codebook's construction, not
fit to data), and it was checked -- not merely asserted -- against the FULL 120-point measured surface already
sitting in `data/exp_rns_subblock_margin_selfcheck_v1/metrics.json`, landing at RMS residual 0.012 (measurement-
noise scale) and `gm_ratio_err` 1.01-1.15x across all three tested moduli. That is a stronger evidential position
than a typical "the literature suggests X might apply" research finding. Per role discipline, the P_deflated for
"a FRESH FULL cell dispatch reproduces this within the pre-registered <1.5x/relative-improvement bands" is
still capped at 0.50 (Sec. 4) -- the cap is kept deliberately, not because the underlying math is in doubt, but
because a fresh dispatch is a genuinely separate event (new seeds, a real code-port of the integral, a real
`classify()` gate) with its own, if small, failure surface, and the role's calibration discipline exists
precisely to prevent research from over-promising on dispatch-time confidence. This drill also explicitly tested
and REJECTED its own first hypothesis (the "2 nearest-neighbor" / min-distance route, option (a)) before
settling on the order-statistic route (b) -- reported in Sec. 2 rather than silently discarded, per
[[feedback-research-every-finding-for-mechanism-and-envelope-push]] (a rejected hypothesis is itself a finding:
it confirms this codebook's construction lacks M-PSK-style adjacency, a fact worth knowing for any FUTURE
codebook-design choice on this substrate).

---

## Cheap decisive test

Before any dispatch: run the `pred_acc_exact` formula (Sec. 4) as a pure Python/scipy recomputation against the
ALREADY-LANDED `data/exp_rns_subblock_margin_selfcheck_v1/metrics.json` (zero new trials, <5s CPU) and confirm
`gm_ratio_err <= 1.5x` at all 3 moduli using the exact `_cross_sb`/`_gm_ratio_err` functions already in the landed
cell's source. **This drill already ran that test** (Sec. 2): all three moduli land at 1.01-1.15x. If a fresh
FULL dispatch (new seeds) reproduces this, promote to CG; if a fresh dispatch instead lands the exact arm above
1.5x (seed-dependent fluctuation or an integration-window edge case not caught here), treat as MIDDLE and
investigate the `sb=4`/largest-`sigma` corner specifically (smallest-`sb` grid point, where the Gaussian
approximation to `sim[true]`/`sim[c]` is least buffered by CLT-style averaging and any residual non-Gaussianity
would show up first).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, repeated from Sec. 4 for scan-ability)

- HARD-PASS: `predict_exact` gm_ratio_err <= 1.5x at all 3 moduli AND >= 1.5x tighter than `predict_union` at all
  3 moduli AND all pre-existing landed-cell gates (scaling exponent, wrong-scaling separation, collapsed
  control) continue to pass unchanged. P_deflated = 0.50 (capped novel-synthesis; see Sec. 5 for why the cap is
  kept despite strong internal evidence).
- HARD-FAIL: `predict_exact` gm_ratio_err > 4x at any modulus, OR it fails to beat `predict_union` by the
  relative-improvement margin (independence assumption breaks down at production scale) -- a genuinely useful
  negative, reportable prominently, meaning the substrate should keep using the looser (already-HARD_PASSED)
  union-bound arm for any future capacity claim on this codebook.
- MIDDLE: `predict_exact` beats `predict_union` but lands in (1.5, 4]x -- tighter, not yet CG-tight.

---

## CROSS-THREAD SYNTHESIS

- **With `rns_subblock_margin_selfcheck_v1`** (HARD_PASS, MM, re-verified on disk this drill): this drill does
  not contradict or repeat that result -- it takes the SAME landed measurement surface and asks a narrower,
  genuinely new question (can the union-bound arm's own acknowledged looseness, explicitly bounded and
  MIDDLE/HARD-FAIL-gated in the landed cell's own pre-registered bands, be closed with a tighter closed form).
  The landed cell's `HP_OFFSET_MAX = 4.0` band already anticipated this gap would need future tightening --
  this drill is the direct, structural follow-through on that gap, not a new direction.
- **With `notes/research_mechanism_selfverification_scoping_2026-07-06.md`** (the parent scoping drill that
  proposed the landed cell): that note explicitly named "derive/adopt a standard closed-form prediction... could
  be wrong (wrong scaling law, wrong constant), and finding out is genuine information" as the strong version of
  the self-check (Sec 2b of that note). This drill is that exact follow-through: the constant WAS wrong (loose
  by a knowable, derivable amount), and the derivation of WHY (independence structure, not adjacency) is itself
  new information about this codebook's design, beyond "the scaling law holds."
- **With the substrate's own stated engineering-grounding (BIST / noise-margin analysis, Szabo & Tanaka 1967,
  already cited by the landed cell):** this drill's finding maps cleanly onto that same tradition -- moving from
  a coarse, deliberately-conservative margin BOUND (union bound, analogous to a worst-case static timing margin)
  to a TIGHT, exact margin PREDICTION (the order-statistic integral, analogous to a statistical/at-speed timing
  analysis that models the actual joint distribution of competing paths rather than a pessimistic sum-of-worst-
  cases). The honest engineering analogy from the parent note (Sec. 4 there) extends naturally: "the substrate
  moving from a conservative bound to an exact prediction of its own margin" is precisely what a mature BIST/
  margin-analysis discipline does over time in the hardware tradition this substrate already cites.
- **Per [[feedback-research-every-finding-for-mechanism-and-envelope-push]]**: the REJECTED "2 nearest-neighbor"
  hypothesis (Sec. 2) is itself a envelope-relevant finding -- it establishes that THIS specific phase-linear,
  random-per-dimension-frequency codebook construction has NO adjacency structure among competing residues (all
  m-1 competitors are exchangeable). Any FUTURE substrate codebook design that instead shares frequencies across
  residues (an M-PSK-style construction) would need the DIFFERENT, adjacency-based route (a) instead -- a
  concrete, falsifiable design note for the substrate's own codebook-choice space going forward.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- If the corrected-prefactor arm HARD-PASSes on a fresh FULL dispatch: the substrate gains a PRECISE (not merely
  scaling-law-level) self-prediction of its own decode-margin boundary -- upgrading "the substrate knows a
  scaling law governs its own limits" (already landed) to "the substrate can predict, to within ~10-15%, exactly
  where its own decode collapses, as a function of its own design parameters" -- the CG-tier claim the Director
  asked this drill to test for. This is a genuine, narrow instance of design-level self-knowledge, distinct from
  (and a direct quantitative sharpening of) the already-landed MM result.
- If it HARD-FAILs on a fresh dispatch despite this drill's strong retrospective fit: that would itself be
  valuable and reportable -- it would mean the independence assumption, while excellent at THESE specific
  moduli/seeds, does not generalize robustly, and any future capacity/margin claim for this codebook should stay
  anchored to the looser but already-validated union-bound arm, per
  [[feedback-measured-bounds-are-method-config-contingent-not-fundamental]].
- **Still monitor-not-control, unchanged from the parent cell's USER-locked framing:** this remains a REPORTING
  refinement (a tighter number in `metrics.json`), never a config-changing action -- it does not alter `sb`,
  does not edit any landed math cell, and does not auto-trigger anything. A human (or Strategy) reads the
  tightened margin number and decides what, if anything, to do with it.
- **Cap_map implication:** if the corrected-prefactor arm HARD-PASSes, this is grounds for Strategy to consider
  promoting the existing `cap_math_mechanism_margin_audit` candidacy (flagged by the parent scoping note) from
  MM to CG-eligible, specifically on the strength of "the substrate's prediction of its own limits is now exact,
  not merely scaling-law-correct." Strategy decides; research does not modify cap_map.

---

## CITATIONS (verified external count this drill: 12, across 3 lit-scans; builds directly on but does not
re-count the 24 citations already logged in the parent scoping note, since this is a narrower quantitative
follow-through on the SAME mechanism, not a new question)

**Lit-scan 1 -- exact M-ary orthogonal/simplex signaling SER formula (4 sources):**
1. Hajek, B. "ECE 361 Lecture Notes 8: Energy-Efficient Communication -- Part II." University of Illinois,
   Spring 2011. https://courses.grainger.illinois.edu/ece361/sp2011/Newlectures/Lecture08.pdf -- derives the
   EXACT integral `P(C) = Integral[Phi(x)^(M-1) * phi(x-mu)] dx` (eq. 8.1), the direct-error form via integration
   by parts to avoid catastrophic cancellation (eq. 8.3), the union bound (eq. 8.6), and the intermediate exact
   binomial form `P(E) < 1 - [1-Q(mu/sqrt2)]^(M-1)` (eq. 8.7) -- the precise closed forms this drill's derivation
   independently re-derived from the substrate's own decode arithmetic and matched.
2. Proakis, J. & Salehi, M. *Digital Communications*, 5th ed. McGraw-Hill, 2008, Ch. 4 (M-ary orthogonal/
   biorthogonal/simplex signaling over AWGN) -- the canonical textbook home of this result (already partially
   cited by the landed cell for the union-bound corollary; this drill's contribution is the EXACT, not the
   bounded, member of the same family).
3. Simon, M.K. & Alouini, M.-S. *Digital Communication over Fading Channels: A Unified Approach to Performance
   Analysis.* Wiley, 2005 -- MGF-based unified framework generalizing this integral family.
4. Sason, I. & Shamai, S. "Performance Analysis of Linear Codes under Maximum-Likelihood Decoding: A Tutorial."
   *Foundations and Trends in Communications and Information Theory*, 2006.
   https://webee.technion.ac.il/people/sason/monograph_postprint.pdf -- documents the union bound's asymptotic
   looseness (a genuine constant-factor-2 SNR-threshold gap as M->infinity, matching this drill's finding that
   the looseness is bounded and roughly consistent rather than unboundedly growing).

**Lit-scan 2 -- union-bound tightness / order-statistics for independent Gaussian maxima (4 sources):**
5. "Boole's inequality / Bonferroni inequalities." Wikipedia. https://en.wikipedia.org/wiki/Boole%27s_inequality
   -- confirms the union bound is the first-order Bonferroni truncation; for INDEPENDENT events the full
   correction is the closed-form binomial expansion `1-(1-Q)^n`, no heavier machinery needed.
6. Sidak, Z. (1967). *JASA* 62:626-633. https://www.math.toronto.edu/mccann/assignments/477/Sidak67.pdf -- proves
   the independence-CDF formula is a valid bound under general correlation (checked and confirmed NOT the
   binding constraint here, since this codebook's competitors are independent, not merely bounded-by-independence).
7. Slepian, D. (1962). "Slepian's lemma." https://en.wikipedia.org/wiki/Slepian%27s_lemma -- monotonicity of
   max-probability in pairwise correlation; used to confirm the direction of the (here negligible) residual
   correlation effect.
8. Leadbetter, Lindgren & Rootzen (1983); Poisson-clumping / Stein-Chen approximation
   (https://projecteuclid.org/journals/annals-of-probability/volume-18/issue-2/Poisson-Approximation-Using-the-Stein-Chen-Method-and-Coupling/10.1214/aop/1176990854.full)
   -- confirms the numeric finding that for independent Gaussian competitors in the relevant `n,Q` regime
   (n=8..42, Q~1e-2..1e-6), the exact-vs-union-bound ratio stays bounded in ~1.00-1.22x, consistent with this
   drill's directly-measured 1.01-1.15x.

**Lit-scan 3 -- random-matrix / free-probability applicability check (4 sources):**
9. "Free convolution." Wikipedia. https://en.wikipedia.org/wiki/Free_convolution -- confirms free convolution is
   the free-probability analogue for NON-COMMUTING objects exhibiting asymptotic freeness, not classically-
   independent scalars -- the wrong tool class for this problem.
10. Tao, T. "254A Notes 5: Free Probability" (2010). https://terrytao.wordpress.com/2010/02/10/245a-notes-5-free-probability/
11. "Tracy-Widom distribution." Wikipedia -- confirms Tracy-Widom edge statistics require eigenvalue repulsion
    (Vandermonde/beta-ensemble structure), absent here.
12. Cizeau & Bouchaud-style heavy-tailed random-matrix analysis (per lit-scan synthesis, arXiv:0909.5228 family)
    -- direct evidence that RMT edge statistics DEGENERATE to classical extreme-value theory once independence
    dominates and repulsion is weak, confirming route (c) would not have produced a different or better answer
    even if invoked.

**Substrate-internal (verified on disk this drill, not counted toward external total but load-bearing):**
- `data/exp_rns_subblock_margin_selfcheck_v1/metrics.json` (HARD_PASS, re-verified this drill: full `per_unit`
  120-point surface used for the pointwise RMS-error check in Sec. 2; `per_modulus` `gm_ratio_err_correct`
  2.39-2.73x confirmed as the starting point this drill improves on).
- `experiments/exp_rns_subblock_margin_selfcheck_v1.py` (read in full this drill; exact `pred_acc_correct`,
  `decode_acc`, `_cross_sb`, `_gm_ratio_err` implementations used to build an apples-to-apples comparison,
  not a re-derivation of the cell's own reporting conventions).
- `preregs/rns_subblock_margin_selfcheck_v1.md` (read for smoke-result context and FULL-staging plan; confirms
  the FULL run is non-parked, remote-dispatchable, CPU-only, ~25s, matching the corrected-prefactor extension's
  own cost profile).
- `notes/research_mechanism_selfverification_scoping_2026-07-06.md` (parent scoping note, read in full for
  cross-thread synthesis, not re-cited for its own 24 external citations).

---

*Research complete 2026-07-06. Derivation checked directly (not merely asserted) against the full landed
`metrics.json` measured surface (120 points) before any external lit-scan dispatch -- the numeric result (Sec. 2)
was established first from the substrate's own on-disk data and code, then 3 parallel Sonnet lit-scans (exact
M-ary signaling SER formula; union-bound tightness / order-statistics; random-matrix / free-probability
applicability) supplied citation-grounding and confirmed no better/different route exists among the task's
three named options. Generic math terms only, no substrate-novel mechanism names off-platform. Lit-scan
calibration applied (novel-synthesis cap 0.50, Sec. 5 states explicitly why the cap is kept despite unusually
strong internal verification). HARD-FAIL thresholds specified. Notes-only drill per Director instruction -- no
cell built, no dispatch, no routing files (USER-locked ferry-deprecation override; the ready cell spec is
delivered directly in this note, Sec. 4).*
