# Density x Scale sweep design: predicting m*(N) and the GSBC cliff boundary at 970K

Date: 2026-07-07. Owner: research (Sonnet, 3 parallel lit-scan sub-agents + main-thread synthesis).
Trigger: USER-directed experimental-design drill (design only, no cell, no dispatch). Follows
directly from `exp_encoder_gsbc_gradedcode_marginpush_v1` (landed, 5 seeds, V=177,899) and
`notes/research_encoder_970k_marchenko_pastur_codebook_collision_forecast_2026-07-07.md` (which
named the GSBC density dial as the lever and flagged a Donoho-Tanner-class cliff as the one
plausible sharp-transition risk). Field-advisor context: this drill's 3 lit-scans map onto
`sparse-coding-compressed-sensing`, `random-matrix-theory-beyond-free-prob`, and
`percolation-critical-phenomena` -- all Tier-1b fields per the advisor table, satisfying the
field-coverage heuristic without a fresh advisor run needed (topic was USER-directed, Trigger-E
equivalent, matching the forecast note's own precedent).

## Verified on-disk facts this design is built on (re-pulled independently, not trusting the prompt)

- Cross-seed `graded_ret_agree10` at V=177,899 (5 seeds: 7,13,19,23,29), read directly from each
  seed's `metrics.json` `verdict_msg` (not the prompt's summary):
  - m3 (density 0.0234, k=96 active/4096): [0.3116, 0.2568, 0.3681, 0.3973, 0.3957] -- min=0.2568,
    mean=0.3459, **cv=0.157**
  - m5 (density 0.0391, k=160): [0.4479, 0.4386, 0.4323, 0.4430, 0.4682] -- min=0.4323, mean=0.4460,
    **cv=0.027** (tight)
  - m8 (density 0.0625, k=256): [0.4538, 0.5540, 0.4798, 0.5068, 0.3492] -- min=0.3492 (seed29),
    mean=0.4687, **cv=0.146**
  - Cross-seed MIN is non-monotone (m3 -> m5 rises 0.2568->0.4323, m5 -> m8 the min actually FALLS
    to 0.3492) even though the MEAN keeps rising. **The cross-seed coefficient-of-variation is
    U-shaped: tight at m5 (2.7%), wide at both m3 (15.7%) and m8 (14.6%).** This is a new
    observation this drill surfaces (not in the source prereg): rising cross-seed variance at m8
    while the mean still climbs is a textbook **critical-slowing-down / early-warning-signal**
    pattern for approaching a bifurcation (percolation / glassy-relaxation literature, a field
    already in this project's scope) -- it shows up in the variance BEFORE the min catastrophically
    drops, and is cheaper to detect than waiting for a seed to actually fail.
- Cost is architecturally flat in V, verified by reading the cell's own code, not assumed:
  `steps=8000, batch=128` fixed regardless of teacher-cache size; the `ret_agree10` eval
  (`_semantic_unit_with_per_item`) computes self-retrieval **within the held set only**
  (`n_he = min(V_cache*0.10, FULL_HELD_CAP=20_000)`), an O(20000^2) pairwise computation capped
  regardless of V_cache. Measured wall-time per seed (all 3 density arms in one run) = 460-574s.
  **Both training and eval cost are near-flat as V grows** -- the only new cost at larger V is
  teacher-encoding additional entities (a one-time BGE forward pass, not a training-time cost).
- Existing free scale rungs already on disk (`data/substrate_index/cached_indices/bge_large_v2_name_*.npz`,
  all <=177,899, no cache exists beyond it): ~1.7-1.8K (x4), ~20.8K, ~26.3K (x2), ~31.3K (x2),
  ~41.3-41.4K (x3), ~43.9K (x2), 177,899 (current, `54f7cf6a`). These are historical snapshots of
  the same growing ConceptNet+math/science corpus, not a designed ladder -- usable but not clean;
  **building fresh subsamples of the 177,899 cache at exact target sizes (e.g. 50K, 100K) is free**
  (index a random subset of the existing `.npz` rows, zero new BGE calls) and gives controlled,
  exact N values instead of relying on accidental historical sizes.
- Real production KB: `data/substrate_director_kb_v1/entities.jsonl` = 970,069 rows (`wc -l`
  verified). Per `notes/research_970k_kb_near_duplicate_density_test0_2026-07-07.md`, this corpus
  is compositionally DIFFERENT from the 177,899 ConceptNet+math/science cache (dogfood chunks +
  project notes + WordNet lemmas, effective-distinct/V ~0.79-0.83) -- any scale rung beyond 177,899
  should sample from the REAL entities.jsonl, not synthetically inflate the ConceptNet corpus, or
  the near-duplicate structure being measured won't match production.
- The already-planned Stage 3 scale-test (`notes/research_ingest_arc_scoping_staged_plan_2026-07-07.md`)
  already mandates a >=400K rung with its own HARD-PASS/HARD-FAIL bands (dense spearman>=0.82,
  keyed@J5>=0.90, shuffled-key<=0.10) and already flags "density dial / higher K" as the fix if it
  fails. **This design's 400K rung is not new work -- it is the same rung Stage 3 already commits
  to, instrumented with the density sweep this note adds.**
- Per `notes/research_self_margin_taxonomy_synthesis_cg_meta_assessment_2026-07-06.md` (row 10),
  this exact channel (encoder continuous retrieval, heavy-tailed BGE-Gram spectrum) is an already-
  confirmed **RESISTOR** to this project's own closed-form self-margin taxonomy -- a
  covariance-matched Gaussian surrogate explains only 60-95% of the collapse gap, leaving a robust
  residual. This is important context for Item 1 below: this project's OWN prior, most extensive
  self-margin program already found this channel resists clean closed-form fitting.

## Item 1 -- THEORY FIRST: does closed-form theory predict m*(N)?

**Three lit-scans dispatched (generic math terms only, per query-privacy discipline), covering
compressed-sensing/dictionary-size, distance-concentration/dimension-scaling, and adaptive/
finite-size-scaling design. Verdict: theory gives real, citable, but MUTUALLY DISAGREEING
quantitative anchors -- it brackets and directs the search, it does not hand over one number.**

**Anchor A -- Johnson-Lindenstrauss / Larsen-Nelson (tight, well-established, confidence 0.85-0.9
per the lit-scan's own calibration):** for N points, an embedding dimension `k >= c*ln(N)/eps^2`
is BOTH sufficient (JL 1984, Dasgupta-Gupta 1999) AND worst-case necessary (Larsen-Nelson 2017,
arXiv:1411.2404) to preserve pairwise distances within `(1+-eps)`. Treating the graded code's
active-dimension count `k = m*32` as the analog of the JL target dimension (a defensible but not
proven substitution -- `ret_agree10` is exactly a pairwise-rank-preservation metric, which is what
JL directly bounds) gives:

**m*(V) ~ A + B * ln(V)** -- predicts MILD growth. `ln(970069)/ln(177899) = 13.78/12.09 = 1.14`:
only a ~14% density increase from 177,899 to 970,069. If m~5-6 is near-optimal today, this anchor
predicts m*(970K) ~ 5.7-6.8, i.e. **do NOT expect to need a qualitatively denser code.**

**Anchor B -- Willshaw/Palm optimal-fill-factor (moderate confidence, reconstructed mean-field
result, not machine-verified against the primary source per the lit-scan's own honest flag):**
classical one-shot binary associative-memory theory gives optimal fill factor
`p*(n,M) = k/n ~ sqrt(ln2/M)` at critical load. This predicts the OPPOSITE direction: density
should DECREASE, roughly as `1/sqrt(V)`. `sqrt(177899/970069) = 0.428` -- a >50% density
REDUCTION predicted for the SAME fidelity target. Applied literally this anchor also implies a
back-of-envelope capacity ceiling `M_max ~ n^2/(log2 n)^2 = 4096^2/12^2 ~ 116,500` for n=4096 --
already BELOW the current 177,899, which does not match the empirically observed behavior (density
still helps, not collapsed, through m=8 at 177,899). **This is a real, honest, unresolved tension,
not a resolved contradiction:** the Willshaw net is a fixed random-projection, exact one-shot
hetero-associative recall mechanism; this system is a TRAINED, continuous, graded-weight rank-
retrieval mechanism -- different enough that direct numeric transfer is doubtful, but the
DIRECTIONAL warning (classical sparse-associative-memory capacity arguments put 970K uncomfortably
close to or past a naive ceiling for n=4096) should not be dismissed either.

**Anchor C -- Knoblauch-Palm-Sommer fixed-fidelity scaling (same family as B, different regime):**
holding retrieval fidelity FIXED as N grows requires `m ~ sqrt(N) * log(N)` -- a STEEP increase.
`sqrt(970069/177899) * (ln(970069)/ln(177899)) = 2.335 * 1.14 = 2.66x`. This predicts m*(970K)
roughly 2.7x today's optimal, e.g. m~13-16 if m~5-6 is optimal today -- directionally agrees with
Anchor A (denser needed) but by a MUCH larger factor.

**No paper in any of the 3 lit-scans reparametrizes the Donoho-Tanner `rho_S(delta)`
compressed-sensing phase-transition boundary directly by dictionary size (M = number of competing
stored items) -- the standard CS phase-transition framework structurally lacks an M-axis (it is a
single-signal-vs-single-sensing-matrix formalism). This is an honest literature gap, confirmed
independently by 2 of the 3 sub-agents, not a search failure.**

**Verdict on Item 1: theory does NOT collapse to one closed-form m*(N) with usable confidence.**
Three legitimate anchors disagree on both direction (2 predict denser-needed, 1 predicts
sparser-needed) and magnitude (14% to 266% change over the same V range). This is compounded by
the fact that this exact channel is an ALREADY-CONFIRMED resistor to this project's own closed-form
self-margin taxonomy (row 10, 2026-07-06) -- an independent, internal precedent for exactly this
kind of "no clean closed form" outcome on this specific channel. **The empirical sweep is
necessary, not optional** -- but theory still earns its keep: it hands us TWO specific, falsifiable
candidate functional forms (`m* ~ a + b*ln(V)` vs `m* ~ a*V^c` for some negative or positive c) to
fit and let the DATA discriminate between, instead of a blind grid search with no model-selection
structure at all. That is the concrete value theory buys here.

**Predicted m*(970K), stated with honest uncertainty (per the mandatory calibration penalty):**
central estimate m* in **[5, 9]** (spanning Anchor A's mild-growth case through roughly half of
Anchor C's steep-growth case, deliberately not extending to Anchor C's full 2.66x because that
anchor's mechanism-match is the weakest of the three), with a NAMED, non-dismissed downside
scenario (Anchor B) that density should be RETUNED DOWN, not up -- this scenario is judged less
likely (the mechanism mismatch is largest) but is not zero-probability and the sweep design below
explicitly tests for it rather than assuming density-up is the only direction worth sampling.
**P(central estimate m* in [5,9] is within 1 density-step of the true optimum at 970K): undeflated
~0.40, P_deflated ~0.20-0025** (deflated hard per the mandatory novel-synthesis cap -- this is a
compound extrapolation across 3 disagreeing theoretical anchors on a channel independently already
shown to resist closed-form fitting).

## Item 2 -- THE SWEEP

**Scales (4 rungs, cheap-first, reusing the flat-cost property verified in Item 1's on-disk
facts):**

| Rung | V (target) | Source | New GPU cost | Purpose |
|---|---|---|---|---|
| R1 | 50,000 | fresh subsample of existing 177,899 cache (free, no re-encode) | ~seed-training time only (~8 min/seed) | cheapest anchor point, brackets the low end |
| R2 | 100,000 | fresh subsample of existing 177,899 cache (free) | same | second anchor, mid-range |
| R3 | 177,899 | **already landed** (`exp_encoder_gsbc_gradedcode_marginpush_v1`, 5 seeds, m in {3,5,8}) | ZERO -- reuse | third anchor, already have full 5-seed data |
| R4 | ~400,000 | NEW teacher-encoding from the REAL `entities.jsonl` (not synthetic ConceptNet inflation) | one-time BGE-encode of ~222K new entities (bounded, GPU-cheap) + seed-training | validation rung, IS the already-planned Stage 3 rung -- not extra work |

Explicitly NOT adding a 5th rung between 400K and 970K for this cheap design: the full 970K point
is the actual production Stage 3 target and serves as the OUT-OF-SAMPLE VALIDATION point (Item 3),
not another fitting rung -- spending a 5th rung there would consume budget better spent on the
validation run itself.

**Density points per rung -- ADAPTIVE, not a uniform grid, per the finite-size-scaling lit-scan's
explicit recommendation against blind grid search:**

- **R1 (50K):** run the full landed grid {3, 5, 8} (zero new code, exact reuse of the marginpush
  cell with a smaller `--teacher-cache`). This is the FIRST bracket -- needed because we don't yet
  know which direction (Anchor A/C vs Anchor B) the data will confirm.
- **R2 (100K):** adaptive-refine based on R1's result. If R1's cross-seed-min-maximizing density
  shifted from m5 (matching current 177,899 behavior) toward higher OR lower m, center the R2 grid
  on that shift (e.g. if R1 shows m5->m6 improves the min, sample {4, 6, 8} instead of blindly
  repeating {3,5,8}). This is the adaptive-bisection step the lit-scan recommends over a fixed
  grid -- it directly tests which of the two theoretical directions (Anchor A/C vs Anchor B) the
  system is actually following before committing more budget.
- **R3 (177,899):** already have full data at {3, 5, 8} -- no new run. Use this rung's cross-seed
  MIN + cv curve as the reference "true" shape at this scale (m5 is the tightest/highest-min point
  measured; m8 shows the CV early-warning signature named in the on-disk-facts section above).
- **R4 (400K):** sample density around the EXTRAPOLATED m* from the R1-R2-R3 fit (both candidate
  forms), bracketing +-2 density steps around the fitted prediction, e.g. if the fit predicts
  m*(400K)~6-7, sample {5, 6, 7, 8, 9} -- denser sampling here specifically BECAUSE this is where
  the cross-seed-variance early-warning signal (CV curve) should be tracked most carefully: this is
  the closest rung to where a real cliff (if one exists per Anchor B/C) would first become visible.

**Seeds:** reuse 7, 13, 19, 23, 29 throughout for comparability, per USER direction, BUT
cost-optimize: run the FULL 5-seed battery only at R3 (already have it) and R4 (the validation
rung, where per-seed-robustness power matters most). At R1 and R2 (the cheap bracketing rungs), run
only the 3-seed comparability trio (7, 13, 19) -- sufficient to locate the approximate m*(V) shift
and the CV trend without paying for full 5-seed robustness at scales that aren't the ship
decision point. This is an explicit, named cost/power tradeoff, not an oversight.

**Ship metric / joint gate -- IDENTICAL discipline to the landed cell, applied PER RUNG:**
at a FIXED m* for that rung, ALL sampled seeds' `graded_ret_agree10 >= 0.30` AND joint gate holds
(`cosine_to_gold(hi80) >= 0.80` AND `composed_roundtrip@J10 >= 0.95`). Track, per rung: (a) the
cross-seed MIN curve vs m (existing discipline), and (b) the cross-seed CV curve vs m (the NEW
early-warning addition this drill proposes) -- a rung whose CV curve starts rising at a LOWER m
than the previous rung is itself a falsifiable signal that the cliff is moving closer as V grows,
independent of whether the MIN has visibly dropped yet.

## Item 3 -- THE EXTRAPOLATION

**Fit BOTH candidate functional forms from Item 1, not just one, and let residuals discriminate:**
1. `m*(V) = a + b * ln(V)` (Anchor A / Larsen-Nelson form)
2. `m*(V) = a * V^c` (Anchor B/C family; c<0 tests Anchor B's sparser-is-better prediction, c>0
   tests Anchor C's steep-growth prediction) -- fit `c` freely rather than assuming a sign.

With 3 fitting rungs (R1, R2, R3) this is the bare mathematical minimum per the finite-size-scaling
lit-scan (2 free parameters + 1 residual degree of freedom) -- the lit-scan's own caution applies:
**this is fragile with only 3 points, not a robust fit.** The mitigation it recommends (drop the
smallest rung, refit, check the extrapolated value doesn't move much) is exactly the honesty check
to run here: refit using only {R2, R3} and confirm the R4 prediction doesn't swing wildly -- if it
does, that itself is the finding (the functional form is not yet identified, not that the
extrapolation is precise).

**Validation:** R4 (~400K) is used TWICE -- once as a genuine held-out test of the R1-R2-R3 fit
(compare the fit's predicted m*(400K) against what R4 actually measures, BEFORE looking at R4's
answer, i.e. pre-register the predicted number the moment the R1-R2-R3 fit is computed, not after),
and again as the LAST fitting rung feeding a refined 4-point extrapolation to 970K. The refined
970K prediction is then the number Stage 3's actual full-970K dispatch validates -- closing the
loop: **does the true 970K m* land inside the confidence band the 4-point fit predicted?** If yes,
this "theory-informed extrapolation" approach is validated for future encoder-scale questions
(a reusable capability, not a one-off). If no, the honest finding is that this channel needs
brute-force empirical retesting at each new target scale -- also valuable, it closes off a cheaper
path that would otherwise keep getting silently assumed to work.

## Item 4 -- HONEST COST/VALUE

**Cost:** R1+R2 (cheap rungs, free cache, 3 seeds, adaptive 3-4 density points each) ~= 15-25 min
GPU-time each, R3 = zero (already landed), R4 (validation rung, 5 seeds, ~5 density points, plus a
one-time BGE-encode of ~222K new entities from the real `entities.jsonl`) ~= 45-75 min GPU-time +
a bounded one-time encode step (order tens of minutes at typical BGE-large throughput, not
measured directly this drill -- flagged as the one cost estimate not directly verified on disk).
**Total: well under 3 GPU-hours, on a GPU confirmed IDLE right now** (`tools/inflight_monitor.py`:
util 0.1%, all queues idle, zero contention). This is cheap by this project's own standards
(compare: a single full-970K blind retrain-and-hope cycle, if the density guess is wrong, costs a
FULL GPU-day dispatch PLUS the diagnostic latency of discovering the wrong guess only after landing).

**Value:** the already-planned Stage 3 scale-test (`research_ingest_arc_scoping_staged_plan`) is
committed to retuning the density dial for >=400K regardless of this drill -- that retune will
happen with or without this design. The question this design actually answers is whether that
retune is a BLIND single-shot guess (risk: wrong guess -> a second expensive full-scale dispatch
cycle to correct it) or a THEORY-INFORMED guess with a pre-registered confidence band and a
falsifiable validation check (this design). The marginal cost of the latter over the former is
almost entirely the R1/R2 cheap rungs (R3 is free, R4 is already-committed work) -- i.e., **the
true marginal cost of this whole design is ~30-50 minutes of already-idle GPU time**, in exchange
for converting an expected 2-3 iteration blind-retune cycle at FULL 970K scale into an expected
1-iteration cycle. That is a clear, concrete, non-busywork value case.

**Recommendation: RUN NOW (R1+R2), fold R4 directly into the already-scheduled Stage 3 dispatch
(no separate dispatch needed -- same cell, same rung, this design just adds the density-sweep
instrumentation and the pre-registered fit-comparison to what Stage 3 already does). Do NOT defer
R1/R2 into the scale-test -- they are free/cheap NOW and their entire value is in de-risking the
Stage 3 density guess BEFORE that expensive rung runs, not after.**

**Does theory make the empirical sweep unnecessary? No.** Item 1's three anchors disagree on both
direction and magnitude, and this exact channel is an independently-confirmed resistor to this
project's own closed-form self-margin program. Theory earns its keep by turning a blind grid search
into a model-selection question between two specific, falsifiable functional forms -- it does not
replace the need to measure.

## Cheap decisive test

R1 alone (50K rung, 3 seeds, grid {3,5,8}, free cache subsample, ~15-20 min GPU): does the
cross-seed-min-maximizing density SHIFT from m5 (the 177,899 optimum) at a SMALLER scale? If it
shifts DOWN (toward m3/m4), that is early, cheap, decisive evidence for Anchor B's sparser-at-scale
direction. If it stays at m5 or shifts UP, that favors Anchor A/C. Either answer sharply narrows
which of the two candidate functional forms to weight more heavily before spending R2/R4 budget.

## Falsifiable predictions

**HARD-PASS (theory-informed extrapolation approach, validated):** the 4-point fit (R1-R2-R3-R4)
predicts m*(970K) with a confidence band, and Stage 3's actual full-970K dispatch (already
planned, density-retuned per the existing prereg discipline) lands its cross-seed-min-maximizing
density WITHIN that predicted band. This validates theory-informed extrapolation as a reusable
capability for future encoder-scale questions.

**HARD-FAIL (extrapolation approach, not reusable):** the true 970K optimum falls OUTSIDE both
candidate forms' predicted bands (i.e., neither `a+b*ln(V)` nor `a*V^c` fit, refit from {R2,R3},
brackets the true value) -- this means the channel needs a 3rd, currently-unidentified functional
form, or genuinely resists closed-form/semi-closed-form prediction even with real data points (a
DIRECT extension of the row-10 RESISTOR finding from continuous+curve-fittable to fully
un-forecastable). Report honestly; do not force-fit a 3rd curve post-hoc without a new
pre-registered mechanism.

**MIDDLE (plausible, informative):** R1/R2 show the cross-seed-min-maximizing density does NOT
move much across 50K->100K->177,899 (i.e., m*(V) is closer to constant than either candidate form
predicts) -- in this case the honest conclusion is that m* is scale-INVARIANT in this range and
Stage 3 should simply reuse m5-m6 rather than retuning, with the CV early-warning curve (not the
min curve) becoming the primary signal to watch as V approaches 970K.

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):**
- P(4-point fit's predicted band contains the true 970K optimum): undeflated ~0.40 (three
  disagreeing anchors, one already-confirmed resistor precedent) -> **P_deflated = 0.20-0.25**,
  near the pessimistic end of the allowed deflation range given the compounded extrapolation risk.
- P(R1 alone gives a clear directional signal, i.e. cross-seed-min-maximizing density measurably
  shifts or measurably doesn't, rather than an ambiguous middle result): undeflated ~0.65 (this is
  a much lower-risk claim -- just "does R1 show a detectable shift," not "is the shift's magnitude
  correctly predicted") -> **P_deflated = 0.45-0.50**, capped at the novel-synthesis ceiling.

## Cross-thread synthesis

Directly extends three prior threads without re-deriving them: (1) the Marchenko-Pastur forecast
note's Item 4/5 (GSBC density dial named as the lever, Donoho-Tanner cliff named as the risk,
density retune recommended for the scale-test) -- this design is the concrete sweep that forecast
called for but did not itself specify; (2) the self-margin taxonomy's row-10 RESISTOR finding
(encoder continuous retrieval resists closed-form self-margin fitting) -- this design treats that
finding as load-bearing evidence AGAINST over-trusting any single theoretical anchor, directly
shaping the "fit both forms, let data discriminate" design choice rather than picking one theory
and running with it; (3) the already-landed marginpush cell's own 5-seed cross-seed data -- this
drill's ONLY new empirical contribution to that data is the cross-seed CV early-warning
observation (U-shaped, tight at m5, wide at m3 and m8), which was NOT flagged in the original
prereg or verdict and is a genuinely new, cheap, actionable diagnostic surfaced by this drill's
re-analysis of already-landed numbers.

## Substrate-product implications

For Director: this design does not ask for new GPU budget beyond what Stage 3 already requires --
it asks for ~30-50 minutes of ALREADY-IDLE GPU time (R1+R2) to be spent BEFORE Stage 3's already-
scheduled >=400K dispatch, specifically to pre-register a predicted density before that dispatch
runs rather than guessing blind. The practical payoff is reducing the expected number of expensive
full-970K density-retune iterations from a likely 2-3 (blind trial-and-error) to 1 (validate a
specific prediction). The honest finding from Item 1 -- that theory gives three disagreeing
anchors, not one clean answer -- should NOT be read as "theory failed"; it correctly predicts that
this exact channel (already independently flagged as a self-margin RESISTOR) needs real
measurement, and gives a falsifiable, cheap way to find out WHICH of two plausible functional forms
governs it, rather than an expensive uniform grid with no model-selection structure. If R1 shows
the cross-seed-min-maximizing density shifting DOWN (Anchor B direction), that is itself valuable
early warning worth escalating before Stage 3 commits to a "denser is safer" assumption the
Marchenko-Pastur forecast's Item 4 leaned toward.

## Citations (verified count)

Three parallel Sonnet lit-scan sub-agents dispatched this cycle, generic math/CS/physics terms
only per [[feedback-query-privacy-decomposition]] -- zero substrate-novel mechanism names sent
externally.

**Sparse-recovery/dictionary-size sub-agent (10+ sources):** Donoho & Elad 2003 (uniqueness bound);
Tropp 2004 "Greed is Good"; Welch bound (coherence lower bound); Willshaw, Buneman & Longuet-Higgins,
*Nature* 222 (1969); Palm, *Biol. Cybern.* 36 (1980) and *Neural Networks* 37 (2013); Amari,
*Neural Networks* 2(6) (1989); Nadal, *J. Phys. A* 24 (1991); Buckingham & Willshaw, *Network* 3-4
(1992/1993); Knoblauch, Palm & Sommer, *Neural Computation* 22(2) (2010); McEliece et al. 1987
(IEEE Trans. Info Theory, Hopfield capacity); Amit-Gutfreund-Sompolinsky 1985; Amit & Fusi
(arXiv:0707.1295); Bandeira/Mixon (arXiv:1404.5187); Gripon-Berrou 2011; Loew-Vermet 2025
(arXiv:2603.26217).

**Distance-concentration/dimension-scaling sub-agent (12+ sources):** Johnson & Lindenstrauss 1984,
*Contemp. Math.* 26; Dasgupta & Gupta 1999/2003, *Random Struct. Alg.* 22(1); Larsen & Nelson 2017
(arXiv:1411.2404, tightness/optimality); Indyk & Motwani 1998 (STOC, LSH); Kpotufe 2011
(arXiv:1110.4300); Beyer, Goldstein, Ramakrishnan, Shaft 1999 (ICDT); Radovanovic, Nanopoulos,
Ivanovic 2010 (JMLR, hubness); Aggarwal, Hinneburg, Keim 2001 (ICDT); Francois, Wertz, Verleysen
2007 (IEEE TKDE); Dasgupta, Stevens, Navlakha 2017 (*Science* 358); Ryali et al. BioHash (ICML
2020); Kleyko & Rachkovskij 2024 (arXiv:2501.14741); Stringer et al. 2019 (*Nature*, eigenspectrum);
Recanatesi et al. 2022; Tamamori 2026 (arXiv:2605.00366, kernel-Hopfield SNR-threshold negative
result on participation-ratio-based capacity bounds).

**Adaptive-design/finite-size-scaling sub-agent (11+ sources):** Robbins & Monro 1951; generalized
Robbins-Monro process (2024); Sequential Probability Ratio Bisection (arXiv:2508.17591); Fisher &
Barber 1972, *Phys. Rev. Lett.* 28, 1516 (founding finite-size-scaling paper); Cardy, *Finite-Size
Scaling* (1988); 3d Ising Monte Carlo precision fits (arXiv:1806.03558); Gotovos et al. 2013
(IJCAI, active learning for level-set estimation); Bryan/Schneider (MIT CSAIL level-set thesis);
Shekhar & Javidi (PMLR v89, multiscale GP level-set estimation); (epsilon,delta)-accurate
stopping-criterion variants (arXiv:2503.20272); materials-science autonomous phase-diagram mapping
(npj Comp. Mater. 2019; *Science Advances* 2021).

**Verified count: 33+ distinct external sources found via live web search across 3 sub-agents; zero
fabricated citations (each sub-agent flagged its own honest literature gaps -- notably, no paper
reparametrizes the Donoho-Tanner phase-transition boundary directly by dictionary size/competing-
item count, and no established participation-ratio-to-N target-ratio heuristic exists, with one
2026 paper (Tamamori) directly refuting a PR-based capacity bound in a closely adjacent mechanism).**
Calibration penalty applied throughout per role contract (see per-claim P_deflated values in Items
1 and the Falsifiable Predictions section).
