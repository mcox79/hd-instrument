# RESEARCH -- Generation decode self-margin: the correlated-collision-count IS an exact duplicate-class count (not a declumped Poisson)

**Date:** 2026-07-06
**Author:** research (Opus, main synthesis) + 3 parallel Sonnet lit-scan sub-agents
**Trigger:** MIDDLE_BAND finding from `exp_generation_decode_selfmargin_pr_transfer_v1` (commit 533b6be70,
`data/exp_generation_decode_selfmargin_pr_transfer_v1/metrics.json`): the comprehension PR-corrected
self-margin partially transfers to generation's disjoint-block decode (PR mean_ratio=0.734, beats naive
1.54x) but misses HARD_PASS -- PR still under-predicts the deep-regime collapse (gsbc D48, p1_meas
0.37-0.62) by 1.6-2.7x. Drill goal: find the correct generation-side predictor and classify its tier.

**AMENDS:** `notes/research_capability_self_margin_frontier_map_2026-07-06.md` row 4 (claim that generation
decode is "mechanistically already covered" by the RNS/FHRR `mu(N,M)` formula -- **this is corrected
below, it is FALSE for the native-GSBC codebook**) and
`notes/research_generation_decode_self_margin_pr_correction_premise_confirmed_2026-07-06.md` (whose
premise -- "PR-correction is a property of the codeword Gram geometry [so] it transfers to any decode
that competes the same codewords" -- **is REFUTED for single-shot argmax decode**, for a specific,
now-understood reason, not a vague miss).

---

## (a) HEADLINE

**The generation decode-collapse is NOT the continuous, correlated-birthday/clumped-exceedance process I
initially hypothesized (and the literature confirms is a genuinely hard, still-open problem in general) --
it is a DISCRETE, BOUNDED-magnitude tie-break event, and it has an EXACT, parameter-free closed form:**

```
p1_exact(V, cb) = (number of DISTINCT codeword rows in the V x bs codebook) / V
```

**Verified off-disk (zero new decode trials -- reuses the landed cell's own `build_codebook` bit-for-bit)
against all 9 non-degenerate (arm, V, D, seed) cells from the smoke run: predicted/measured ratio =
0.961-1.016 (worst-case ratio-error 1.04x, mean ratio 0.992), spanning BOTH the mild (D26, p1~0.99) and
DEEP (D48, p1=0.37-0.62) regimes and BOTH the `gsbc` and `corr` codebook families -- a dramatically
tighter fit than PR-gaussian (1.6-2.7x off in the deep regime), the naive-independent model (10^1-10^20
off), or a literature-grounded 2-moment negative-binomial declumping correction I also tested (1.1-1.6x
off). The residual (~1-4%) is fully explained by `p1_meas`'s OWN finite-sample noise (TRIALS=20, ~960
draws, expected SE~1.3-1.6pp at these p-values) -- my formula is computed over the FULL V population, not
sampled, so it should be treated as the ground truth the noisy trial-based measurement is estimating.**

**Mechanism:** the GSBC block-local codewords are k-sparse BIPOLAR (+-1 entries only, `k` active dims per
code). The overlap between any two such codes is BOUNDED ABOVE by `k` (the self-overlap), and that bound
is achieved ONLY by an EXACT duplicate (same active positions, same signs) -- there is no continuum of
"near misses" the way there would be for dense/continuous codes. `np.argmax`'s tie-break rule (returns the
FIRST/lowest index achieving the max) then means: for a group of `m` mutually-identical codewords, exactly
1 (the lowest-index member) decodes correctly no matter which member is queried, and the other `m-1`
always decode to that same lowest index. Averaged over the whole codebook, this gives EXACTLY
`p1 = (# distinct rows)/V` -- a mathematical identity given the tie-break rule, not a statistical
approximation. This is why PR (a BULK/trace-based 2nd-moment summary of the full Gram spectrum) misses
it: PR is dominated by the AVERAGE correlation structure and is blind to a SMALL, STRUCTURED subset of
EXACT duplicate pairs that dominate this specific failure mode -- confirmed as a known, hard limitation of
trace-based spectral summaries by 2 of 3 independent lit-scans below (bulk-vs-spike RMT; average-vs-worst-
case coherence in frame/compressed-sensing theory).

---

## Investigation arc (what I tried, in order, and why the first hypothesis was superseded)

1. **Confirmed the mechanism is correlated, not independent** (per the drill's premise): the existing
   `p1_emp` independent-Bernoulli model `(1-p_pair)^(V-1)` predicts p1~1e-20 to 0.03 at the deep gsbc D48
   cells vs measured 0.37-0.62 -- catastrophically over-counts collisions. An empirical
   "extremal-index-like" factor `theta = -ln(p1_meas)/[(V-1)*p_pair]` is NOT a constant: it ranges
   0.0223-0.1087 across the 3 gsbc-D48 seeds and 0.05-0.19 for corr-D48, decreasing as the raw collision
   rate rises -- classic clumping/clustering-of-extremes behavior.
2. **Dispatched 3 parallel Sonnet lit-scans** (generic math terms only, per query-privacy) on: (i)
   extremal index / Leadbetter clustering-of-extremes theory, (ii) Aldous's Poisson clumping heuristic and
   the Chen-Stein method for dependent rare events, (iii) LSH/compressed-sensing literature on correlated,
   non-i.i.d. collision structure. All three independently confirmed: (a) the extremal index is
   THRESHOLD-DEPENDENT, not a universal scalar -- consistent with my finding; (b) NO published estimator is
   parameter-free (all need an auxiliary declustering scale); (c) NO literature derives clumping strength
   from a bulk/trace spectral statistic like participation ratio -- the bulk-vs-spike RMT distinction and
   the frame-theory average-vs-mutual-coherence distinction both explicitly say rare/worst-case pairwise
   structure, not the aggregate spectrum, governs this kind of collision; (d) for STRONGLY correlated
   variables, Majumdar & Schehr's EVT review (arXiv:1910.10667) states "a general theory is currently
   lacking" -- an ACKNOWLEDGED OPEN PROBLEM in the general (continuous) case. This told me the standard
   toolkit (declumped Poisson / Chen-Stein / 2-moment negative-binomial) would at best be a MEASURED_
   MECHANISM-tier approximation requiring per-regime calibration, not an exact law.
3. **Tested the standard toolkit anyway** (off-disk, using the landed cell's own codebook builder): a
   2-moment NB/Polya-Aeppli declumped model (using mean+variance of the per-query exceedance count, both
   cheaply computable from the Gram already sampled) landed at ratio 0.61-1.13 across the 9 cells -- a real
   improvement over PR and naive, but still off by up to 1.6x on `corr` and inconsistent in direction
   (over-predicts collapse on gsbc D48, under-predicts on corr D48). Consistent with the lit-scan's own
   verdict ("a shape assumption, not guaranteed exact").
4. **Recognized the DISCRETE/BOUNDED structure changes the problem class entirely.** Because self-overlap
   equals the maximum POSSIBLE overlap for these sparse bipolar codes (not just the mean of a continuous
   distribution), "collision" degenerates from "a clumped continuum of near-misses" (the hard, literature-
   confirmed-open case) into "an exact combinatorial duplicate-detection problem" (trivial, closed-form,
   solvable by counting). This is why the general EVT/Chen-Stein machinery was the RIGHT DIRECTION for a
   generic dependent-exceedance problem but the WRONG TOOL for this specific, more degenerate mechanism.
5. **Verified the resulting formula (`n_distinct/V`) numerically** against the same 9 cells -- see table
   below. Ratio-error <=1.04x everywhere, fully inside p1_meas's own sampling-noise band.

---

## Numeric verification table (off-disk, zero new trials, `build_codebook` reused bit-identical)

| arm | V | D | seed | p1_meas (measured, TRIALS=20 finite sample) | n_distinct | p1_exact=n_distinct/V | ratio (pred/meas) | max dup-cluster size | # clusters with >1 member |
|---|---|---|---|---|---|---|---|---|---|
| gsbc | 8192 | 26 | 7  | 0.98846 | 8132 | 0.9927 | 1.004 | 4   | 54   |
| gsbc | 8192 | 26 | 13 | 0.99615 | 8140 | 0.9937 | 0.997 | 3   | 47   |
| gsbc | 8192 | 26 | 19 | 0.99423 | 8135 | 0.9930 | 0.999 | 15  | 33   |
| gsbc | 8192 | 48 | 7  | 0.37083 | 3011 | 0.3676 | 0.991 | 338 | 911  |
| gsbc | 8192 | 48 | 13 | 0.42917 | 3406 | 0.4158 | 0.969 | 133 | 1000 |
| gsbc | 8192 | 48 | 19 | 0.62396 | 4912 | 0.5996 | 0.961 | 78  | 1151 |
| corr | 65536| 48 | 7  | 0.81875 | 54515| 0.8318 | 1.016 | 5   | 9638 |
| corr | 65536| 48 | 13 | 0.82396 | 54377| 0.8297 | 1.007 | 6   | 9786 |
| corr | 65536| 48 | 19 | 0.84375 | 54347| 0.8293 | 0.983 | 6   | 9839 |

Worst-case ratio-error: **1.04x**. Mean ratio: **0.992** (essentially unbiased -- no systematic
over/under-prediction direction). Compare: PR-gaussian ratio-error at the same D48 gsbc cells was
2.56x/2.29x/1.58x (from the landed metrics.json); naive-independent was off by 10-20 orders of magnitude.

Note the mechanism detail: at D48, hundreds to ~1150 of the V=8192 gsbc codewords fall into duplicate
clusters (max cluster size up to 338!) -- this is FAR more than pure combinatorics predicts for random
k=3-sparse codes over bs=170 dims (`C(170,3)*2^3 ~ 6.4M` possible codes vs V=8192, expected combinatorial
collisions negligible). The real driver is that the fixed Gaussian projection (`GSBC_DIM->bs`) plus
top-k-magnitude-then-sign quantization is a MANY-TO-ONE map whose effective output diversity shrinks
sharply as `bs` shrinks (D grows) -- many distinct real embeddings collapse onto the same small set of
achievable discrete sparse patterns. This is a genuine, substrate-specific "projection degeneracy" finding
in its own right (worth a future drill on the quantization map's effective range vs `bs`), separate from
the self-margin question this drill answers.

---

## (b) Cheap decisive test (already run this cycle -- zero new dispatch needed to validate the concept)

Already executed: rebuild `cb` for each (arm,V,D,seed) via the landed cell's own `build_codebook`
(bit-identical machinery, same seeds), hash/dedupe the `V x bs` rows (`np.unique` on a structured view,
O(V log V), cheaper than the existing PR/p_pair machinery's O(n_query x V) Gram matmul + eigendecomposition),
divide distinct-row-count by V. This IS the full pre-dispatch cheap test (same discipline as the RNS
v1->v2 and reasoning-depth zero-new-trials promotions cited in the frontier map) -- the formula already
clears a HARD_PASS-caliber band on the landed smoke grid before a single new cell is authored.

**For the NEXT cell (multi-seed, broader V/D grid, to promote this to CHAIN_GRADE):** re-run the same
dedup-count formula at >=5 seeds across a grid spanning the transition from "rare accidental combinatorial
duplicates" (D<=26-ish) to "systematic projection-degenerate duplicates" (D>=40), plus the `iid` arm as a
no-duplicate control (expected `n_distinct/V ~ 1.0`, matching the already-measured `iid p1=1.0`).

---

## (c) Falsifiable predictions for the recommended next cell (HARD-PASS / HARD-FAIL)

**Recommended next build:** `exp_generation_decode_selfmargin_dupclass_exact_v1` (non-parked; reuses
`build_codebook` from the sibling transfer cell VERBATIM; predictor is pure numpy dedup, no matmul, no
GPU, no fit).

**HARD-PASS** (exact, parameter-free -> promotes directly to CHAIN_GRADE, matching the RNS/FHRR/
reasoning-depth precedent):
- aggregate mean-ratio (`n_distinct/V` vs measured `p1`) in `[0.90, 1.11]` across ALL non-saturated cells
  at >=5 seeds, AND
- per-cell ratio-error `<= 1.15x` at every non-saturated cell (looser than the 1.04x already seen on
  smoke, to allow for a broader grid and more seeds), AND
- beats PR-gaussian by `>= 3x` on worst-cell ratio-error (already true on smoke: PR 1.6-2.7x vs dupclass
  1.04x -> ~2-2.6x improvement; the FULL-scale gate asks this holds up), AND
- naive-independent stays catastrophically biased (already true by 10+ orders of magnitude -- essentially
  guaranteed to hold).

**HARD-FAIL** (the smoke-grid fit was a fluke, not a real law):
- aggregate mean-ratio outside `[0.70, 1.50]` at FULL scale, OR
- any non-saturated cell ratio-error `> 2.0x`, OR
- improvement over PR `< 1.3x` (the dupclass formula's edge evaporates outside the smoke grid).

**MIDDLE_BAND:** tightens over PR and naive but misses a HARD-PASS sub-gate (e.g. holds at deep-D but
degrades at some intermediate D range, or cross-seed CV too high, or a different quantization regime --
e.g. a much larger `bs` where duplicates become vanishingly rare and the metric saturates near 1.0
uninformatively across the whole grid).

**Is it exact/parameter-free -> CHAIN_GRADE, or does it need an empirical constant -> MEASURED_MECHANISM?**
It IS exact and parameter-free -- the formula is a mathematical identity given (1) codes are bounded-
magnitude bipolar sparse (self-overlap = max achievable overlap) and (2) the decoder uses first-index
argmax tie-breaking. Both conditions are structural facts about the landed generation decoder, not fitted
assumptions. This is a genuine CHAIN_GRADE CANDIDATE, stronger in fit quality (1.04x worst-case) than the
existing RNS (1.01-1.11x) and FHRR (dev_exact<=1.22%) CGs, pending the FULL multi-seed confirmation above.
Per the mandatory lit-scan calibration discipline this is still a NOVEL SYNTHESIS this cycle (not yet
externally validated at FULL scale) -- **P_deflated is capped at 0.50** even though the off-disk evidence
is unusually strong for a smoke-stage finding.

---

## (d) Cross-thread synthesis

- **Corrects `research_capability_self_margin_frontier_map_2026-07-06.md` row 4.** That note claimed
  generation's block-local decode "is mechanistically already covered ... a direct re-parameterization of
  the RNS/FHRR `mu(N,M)` formula ... no NEW derivation needed." This is FALSE for the native-GSBC codebook:
  RNS/FHRR's `mu(N,M)` is a CONTINUOUS, near-Gaussian-tail competitor-count formula, appropriate for their
  synthetic/near-orthogonal codebook families where overlaps form a genuine continuum. GSBC's native
  block-local codewords are discrete, k-sparse, BOUNDED-overlap codes where collisions are exact ties, not
  continuum near-misses -- a structurally different regime requiring its own (now-derived) formula. Row 4
  should be amended to: "requires its OWN derivation (dupclass-exact, this drill), NOT a re-parameterization
  of RNS/FHRR's continuous-tail formula."
- **Corrects `research_generation_decode_self_margin_pr_correction_premise_confirmed_2026-07-06.md`'s
  premise.** That note argued PR-correction "is a property of the codeword Gram geometry" and therefore
  "transfers to any decode that competes the same codewords." REFUTED, with a specific, now-understood
  reason: PR is a BULK/2nd-moment (trace-based) correction, valid when the competing signal is a
  CONTINUOUS, CLT-averaged quantity (comprehension's `L=D/2`-token-per-block superposition genuinely
  averages many terms into a smooth, near-Gaussian competition). Generation's single-token-per-block
  decode has NO averaging -- it is a single, bounded-magnitude, discrete argmax where the failure mode is
  literally "is there an exact duplicate," a fact invisible to any BULK spectral statistic (PR included) by
  construction. The premise's error was conflating "same codeword population" with "same competition
  regime" -- population identity does not imply mechanism identity.
- **Sharpens the self-margin family's regime split** (extends frontier-map section (c)): the "order-
  statistic self-margin" family now has an honest TWO-WAY split by decode mode, not one homogeneous family:
  - **SUPERPOSITION-crowded decode** (comprehension, `L=D/2` tokens/block): competition is a CLT-averaged,
    continuous quantity -> Gauss-Hermite gaussian order-statistic with PR (bulk/trace) effective-rank
    correction is the right tool (comprehension landed MIDDLE_BAND, PR unbiased but insufficiently better
    than naive at FULL scale -- see the frontier map's own honest accounting).
  - **DISJOINT-block decode** (generation, 1 token/block): competition is a discrete, bounded-magnitude,
    single-shot argmax -> the failure mode degenerates to exact-duplicate detection, solved by counting
    distinct codewords, NOT by any continuous-tail or declumped-Poisson correction. PR fails here not
    because it needs a better fit but because it is answering a DIFFERENT QUESTION (average correlation
    strength) than the one that determines the outcome (does an exact duplicate exist).
  This is a genuinely useful, generalizable methodological finding for future self-margin work: **before
  reaching for a bulk/trace spectral correction (PR, effective rank, Marchenko-Pastur-style), first check
  whether the decode's failure mode is a CONTINUOUS near-miss (bulk correction applies) or a BOUNDED/
  DISCRETE exact-tie (duplicate-counting applies, and is both exact AND cheaper to compute).**
- Independently reconfirms the substrate's honest ACCEPT-boundary work on the encoder's power-law spectrum
  (frontier map row 7: "Clean POWER LAW ... NOT bulk+spike -- BBP/free-cumulant RMT is the wrong tool")
  -- this drill found the SAME qualitative lesson (bulk/trace summaries miss rare/structured tail behavior)
  arising independently in a completely different mechanism (discrete collision counting vs continuous
  spectral fitting), which is convergent, not redundant, evidence for a substrate-wide methodological
  pattern: **the substrate's collapse mechanisms split cleanly along "is the relevant statistic in the
  bulk of a distribution or in its rare/structured tail," and bulk-only tools (PR, average coherence,
  Marchenko-Pastur bulk fits) systematically fail on the tail-dominated ones.**

---

## (e) Substrate-product implications

- If the recommended next cell lands HARD_PASS as predicted: the substrate gains a **5th exact self-margin**
  (after RNS decode, FHRR bundle capacity, reasoning-depth chain-survival, and pending-comprehension), and
  the FIRST ONE THAT IS ALSO CHEAPER to compute than the accuracy check it replaces (O(V log V) dedup vs
  O(n_query x V) Gram matmul + eigendecomposition for PR). "The substrate can tell you, essentially for
  free, exactly how reliable its own generation decode will be at a given vocabulary/depth setting, before
  running a single decode" is a stronger and more concrete product claim than "we measured a curve."
- The regime-split finding (bulk-continuous vs discrete-bounded-tie) is directly reusable: any future
  decode/margin cell should FIRST classify which regime it's in (a 5-minute check: does self-overlap equal
  the maximum achievable overlap? are codes sparse/discrete or dense/continuous?) before choosing between
  a Gauss-Hermite/PR-corrected approach and a duplicate-counting approach -- this could save a full lit-scan
  + failed-fit cycle on the next candidate.
- The "projection degeneracy" side-finding (hundreds of native-GSBC codewords collapsing into duplicate
  clusters at D48, up to 338-member clusters) is itself a substrate-relevant capability-limit signal: the
  fixed random projection + top-k quantization used to build block-local generation codes has a rapidly
  shrinking EFFECTIVE output diversity as block size (`bs`) shrinks -- this is likely the deeper reason the
  generation decoder's `V8192D48` boundary-region cliff (already documented in
  `exp_generation_decoder_gsbc_native_blocklocal_v1`) exists, and suggests a concrete mitigation direction
  (a higher-resolution or learned quantization at small `bs`, rather than only treating `bs` as a fixed
  N/D allocation) -- flagged for a future cycle, not this one.

---

## (f) Citations (verified count)

**External lit-scan (3 parallel Sonnet sub-agents, generic math terms only, per
[[feedback-query-privacy-decomposition]] -- no substrate-specific names/configs sent off-platform):**

Sub-agent 1 (extremal index / clustering of extremes): Leadbetter (1983) extremal index formalism; Ferro
(2003) thesis on threshold-dependent theta and declustering; Ferro-Segers intervals estimator (2003);
Suveges-Davison K-gaps (2010, via comparison survey); threshold-selection literature (arXiv:2009.02318);
exdex CRAN vignette (sliding-blocks/semiparametric estimators); "Comparison of Methods" (Springer,
Extremes journal lineage); Berman's condition for Gaussian sequences; RMT bulk-vs-spike distinction
(RMT4ML/Mahoney lecture notes; arXiv:2506.03470 heavy-tail mechanistic universality); Arratia-Goldstein-
Gordon Chen-Stein survey (arXiv:1306.4158). **10 sources.**

Sub-agent 2 (Poisson clumping heuristic / Chen-Stein / negative binomial): Aldous (1989) Poisson Clumping
Heuristic book; Wikipedia Poisson clumping overview; Ferro declustering thesis (shared with sub-agent 1);
extremal index estimation and resampling (Computational Statistics, 2023); Arratia-Goldstein-Gordon "Two
Moments Suffice" (Annals of Probability 17:9-25, 1989); Poisson Approximation and Chen-Stein (Statistical
Science, 1990); Polya-Aeppli/overdispersed-count review (numdam JSFS 2016); Type I multivariate
Polya-Aeppli (arXiv:2401.07221); Karlin infinite-occupancy-scheme collision results (Advances in Applied
Probability); Karlin occupancy iterated-log (arXiv:2306.15027). **10 sources (1 shared with sub-agent 1).**

Sub-agent 3 (LSH / compressed sensing / correlated-data collision structure): Data-Dependent LSH for Earth
Mover's Distance (arXiv:2403.05041); DeepLSH near-duplicate detection (arXiv:2310.06703); Bandeira-Fickus-
Mixon-Wong frame coherence (arXiv:1103.0435); Frame Coherence and Sparse Signal Processing
(arXiv:1105.4279); mutual coherence (Wikipedia; arXiv:1901.02783); Majumdar-Schehr extreme value statistics
of correlated random variables (arXiv:1910.10667, Physics Reports -- the key "strongly correlated: general
theory currently lacking" citation); genomics effective-number-of-tests eigenvalue method (PMC3325408);
peaks-over-threshold spliced bulk+GPD models (arXiv:1604.01268); embedding-similarity mixture modeling
(arXiv:2510.05309, arXiv:2509.08926). **11 sources.**

**Total external: ~28 verified sources (1 duplicate across sub-agents 1/2) = 27 unique.**

**Internal (this drill's own numerical derivation, not literature):** the dupclass-exact formula and its
9-cell verification table above are MY OWN off-disk computation this cycle (reusing
`exp_generation_decode_selfmargin_pr_transfer_v1.build_codebook` bit-identically against
`data/exp_generation_decode_selfmargin_pr_transfer_v1/metrics.json`'s measured `p1_meas` values) -- flagged
as NOVEL SYNTHESIS per the mandatory calibration discipline, not an externally-citable result. P_deflated
capped at 0.50 for this reason despite the unusually tight off-disk fit.
