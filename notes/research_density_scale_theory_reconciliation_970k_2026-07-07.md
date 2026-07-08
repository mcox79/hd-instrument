# Why the three density-scaling theories disagree, and which one governs our channel: a decode-mechanism reconciliation

Date: 2026-07-07. Owner: research (Sonnet, 3 parallel lit-scan sub-agents + main-thread synthesis).
Trigger: USER-directed theory-reconciliation drill (design-only, no cell, no dispatch), following
directly from `notes/research_density_scale_sweep_design_970k_extrapolation_2026-07-07.md` (which
found the 3 disagreeing anchors but did not explain WHY they disagree or resolve which one applies).
USER's hypothesis under test: the disagreement is a regime artifact -- each theory is the right
answer for a different (orthogonality, fidelity, load) corner, and the real controlling variable is
effective load = N_effective/capacity, N_effective corrected for orthogonality (participation ratio /
effective rank).

## HEADLINE

**The hypothesis is CONFIRMED, but the resolving variable is not "orthogonality" alone -- it is
DECODE MECHANISM (does the code family store items by additive superposition/interference in a
shared weight structure, or by geometric placement of distinct points in a shared continuous
manifold), with orthogonality/correlation entering as a SECOND-ORDER correction only after the
mechanism match is made.** Each theory's implicit pattern-generation model assumes a specific storage
mechanism: Willshaw/Palm and Knoblauch-Palm-Sommer (KPS) both model **additive/interference storage**
(patterns literally superimposed in one shared synaptic structure, à la Hopfield); Johnson-Lindenstrauss
(JL) / Larsen-Nelson models **geometric placement** (points sitting as distinct locations in a shared
metric space, no additive interference). Our own project's own prior taxonomy work (self-margin
taxonomy, `reference_self_margin_taxonomy_splits_by_decode_regime`) already classified our system's TWO
readouts into exactly these two mechanism families -- Family 2 (collision-count, additive/superposition,
discrete SBC block-argmax) and Family 1 (order-statistic, geometric/crowding, continuous ret_agree10) --
without originally connecting that classification to which of the 3 external theories applies. **The
density-scale question this drill is reconciling (m* for the continuous ret_agree10 gate) belongs to
Family 1 (geometric/crowding) -- meaning JL/Larsen-Nelson (Anchor A) is the mechanism-matched theory,
not Willshaw/Palm (Anchor B) or KPS (Anchor C), whose assumptions belong to the DISCRETE channel (a
separate, already-forecast-to-HOLD question, not the one the density-dial retune is being asked to
answer).** Once mechanism-matched, orthogonality/correlation THEN enters correctly (via the
participation-ratio/effective-rank correction to N in the JL bound) -- but its magnitude on the final
number is small (the log compresses it); the far larger effect of getting the reconciliation right is
excluding Anchor C's ~2.4-2.7x-growth pull from the prediction entirely, not adjusting Anchor A's own
number.

## Item 1 -- What each theory actually assumes (per 3 parallel lit-scans, generic terms only)

**Anchor A (JL / Larsen-Nelson).** Assumes an ARBITRARY point configuration (worst case over all
possible N-point sets) and bounds the ambient dimension needed to preserve EVERY pairwise distance
within (1+-eps) uniformly. No storage mechanism at all -- it is a pure geometry/embedding statement, not
a memory-capacity statement. Confirmed via lit-scan (Larsen & Nelson, FOCS 2017): the k=Theta(ln(N)/eps^2)
bound is tight only for an adversarially-constructed point set; for STRUCTURED data (low intrinsic/manifold
dimension, low participation ratio / effective rank in the Gram spectrum), the true requirement is smaller
and scales with the INTRINSIC dimension, not raw N (Baraniuk & Wakin 2009, manifold-JL: k ~ O(K_manifold *
log(...)), K_manifold not N; Indyk & Naor 2007, doubling-dimension embeddings; subspace-embedding results
approaching k~rank(subspace)). Fidelity target: uniform, worst-case, ALL-pairs preservation -- structurally
identical to what `ret_agree10` (a pairwise rank-agreement metric) actually measures, per the source note's
own flagged substitution.

**Anchor B (Willshaw/Palm optimal fill factor).** Assumes i.i.d. random, mutually independent sparse
binary patterns superimposed additively into ONE shared synaptic matrix (dendritic-sum / clipped
outer-product model) -- confirmed via lit-scan (Willshaw, Buneman & Longuet-Higgins 1969; Palm 1980).
Optimizes AGGREGATE information stored per synapse (the ln2~0.69 bits/synapse asymptote), which is a
DIFFERENT objective than "hold every pattern's fidelity above a floor" -- it tolerates some patterns
degrading as long as the average/aggregate efficiency is maximized. Per the KPS 2010 paper itself
(same family, confirmed via lit-scan): this p1~0.5-fill-factor, maximize-aggregate-information regime is
explicitly DIFFERENT from the paper's own "maximize pattern count M_eps at fixed per-pattern error
level eps" regime (p1~0.16) -- i.e. even within the classical literature, "optimal fill factor" already
means something narrower than "the fidelity target our sweep actually gates on."

**Anchor C (KPS fixed-fidelity).** Also assumes i.i.d./near-orthogonal patterns superimposed additively
into a shared structure (same mechanism family as Anchor B, confirmed by both lit-scans), but holds a
FIXED per-pattern (or all-pattern) error/fidelity level constant as pattern count M grows and asks how a
capacity-controlling parameter must scale to preserve that fixed target. The clearest documented instance
(McEliece, Posner, Rodemich & Venkatesh 1987, Hopfield-capacity paper, confirmed via lit-scan): network
size must grow as ~M*ln(n) (superlinear) if EVERY pattern must be exactly recoverable with vanishing error,
vs. only ~M (linear) if merely MOST patterns' basins need to be stable. This is the textbook instance of
"fixed, uniform, per-item fidelity criterion" forcing steep growth -- structurally the same shape as
Anchor A's uniform all-pairs criterion, but for an ADDITIVE-INTERFERENCE storage mechanism, not a
geometric one.

**Where correlation/orthogonality cuts, and the real tension found in the literature:** for the
additive-interference family (Anchor B/C), BOTH lit-scans independently confirm correlated/non-orthogonal
patterns REDUCE achievable capacity (Löwe, Ann. Appl. Probab. 1998, correlated-pattern Hopfield critical
load alpha_c shrinks with correlation; a 2020s arXiv feature-correlation paper found independently,
same direction) -- correlation HURTS this mechanism family because correlated patterns concentrate
crosstalk/interference in the shared storage structure. For the geometric family (Anchor A), correlation
HELPS -- reduced effective/intrinsic dimension means FEWER ambient dimensions are needed to preserve
distances faithfully (manifold-JL, doubling-dimension results). **This is a genuine, literature-confirmed
opposite-sign effect of the SAME variable (redundancy) on the two mechanism families -- not a
contradiction to explain away, but the actual reason "does correlation help or hurt" has no single
answer: it depends entirely on whether the channel being asked about stores items additively or
places them geometrically.** All three lit-scan sub-agents independently flagged that no published
paper unifies these two literatures under one "effective load" variable -- this reconciliation (matching
each theory to a decode mechanism, then applying the mechanism-appropriate correlation-correction sign)
is this drill's own synthesis, not a lifted result, and is flagged accordingly in the calibration section.

## Item 2 -- Classifying OUR encoder's regime

Per the two prior notes in this thread (re-verified, not re-derived): our encoder has exactly the two
mechanism families named above, already present as two SEPARATE, already-classified channels (not a
new classification -- this drill's contribution is connecting that existing classification to the 3
theories' mechanism assumptions):

- **Discrete SBC channel** (`keyed@J5`, `shuffled_key`): K=128-block disjoint-slot argmax code. This
  IS an additive/collision-style mechanism (Family 2, collision-count) -- matches Anchor B/C's implicit
  storage model. Its forecast is SEPARATE from the density-dial question at hand (already forecast to
  HOLD at 970K per the marchenko-pastur note's Item 2, `P_deflated ~0.60-0.65`, combinatorial margin
  ~180 orders of magnitude, re-confirmed with the measured effective-distinct count in the near-dup
  Test-0 note). **The density-dial retune this sweep is designing for is NOT gating this channel.**
- **Continuous retrieval channel** (`ret_agree10`, dense spearman-to-teacher): points competing in a
  shared continuous manifold, no additive interference between stored codes -- Family 1, order-statistic,
  PR-corrected, per the taxonomy. This IS the geometric-placement mechanism -- matches Anchor A's
  implicit model, not B or C's. **This is the channel the density-dial retune targets** (the sweep's
  ship metric is `graded_ret_agree10 >= 0.30`, a per-item, uniform, all-items-must-clear-the-bar
  criterion -- exactly Anchor A's "preserve every pairwise relationship" framing, not Anchor B's
  aggregate-information-per-synapse framing).

**Orthogonality/correlation measurement for this channel (from the near-dup Test-0 note, re-used not
re-derived):** effective-distinct count at 970K = 771,036-803,689 (0.79-0.83x raw V=970,069), driven by
two concentrated, narrow, mechanically-understood sources (document-chunk near-duplicates from KB
ingest, mean cluster size 8.6-10.1; WordNet polysemous-lemma collapse), NOT diffuse redundancy across
the whole corpus. This is exactly the kind of "reduced participation ratio / effective rank" structure
the manifold-JL correction is built for -- a cluster of 8-10 near-identical chunk rows contributes
roughly ONE effective direction to the relevant Gram-spectrum participation ratio, not 8-10, which is
consistent (self-consistently, computed independently of the near-dup note's own birthday-margin
calculation) with using N_eff ~= 787,000 (midpoint of the measured 771K-804K band) as the corrected
count for Anchor A's ln(N) term.

**Match verdict: Anchor A (JL/Larsen-Nelson, intrinsic-dimension-corrected) is the mechanism-matched
theory for the channel this sweep actually gates.** Anchor B and Anchor C's assumptions (i.i.d.
additive-interference patterns) describe the DISCRETE channel's regime, not the continuous channel's --
their pull toward much denser (Anchor C) or much sparser (Anchor B) codes is answering a question about
a different mechanism than the one `ret_agree10` measures.

## Item 3 -- Predicting m*(970K)

Applying Anchor A with the effective-distinct correction (arithmetic independently verified, not
hand-waved):

```
ln(970,069)  = 13.7851   (raw)
ln(177,899)  = 12.0890
ln(787,363)  = 13.5764   (effective-distinct midpoint, 771,036-803,689 band)

ratio_raw       = 13.7851/12.0890 = 1.1403  (+14.0% growth)
ratio_corrected = 13.5764/12.0890 = 1.1230  (+12.3% growth)
```

Applied to today's near-optimal density range (m~5-6, per the landed 5-seed 177,899 data where m5 has
the tightest cross-seed CV at 2.7% and the highest cross-seed MIN):

```
raw-N prediction:        m*(970K) ~ 5.70 - 6.84   (source note's original [5.7, 6.8])
effective-N prediction:  m*(970K) ~ 5.62 - 6.74   (this drill's correction)
```

**The orthogonality correction moves Anchor A's own number by only ~1.5% relative (14.0% -> 12.3%
growth) -- a small, honest, second-order effect, because the log compresses count changes heavily.**
The much larger effect of this drill's reconciliation is EXCLUDING Anchor C's pull from the blended
estimate: Anchor C (mechanism-mismatched, i.i.d.-additive-interference regime, not this channel's
regime) predicted ratio 2.36-2.66x (m~11.8-16.0), and the source note's original [5,9] band was built
by blending "Anchor A's mild-growth case through roughly half of Anchor C's steep-growth case" --
i.e. Anchor C's mismatched pull was doing most of the work widening the band upward to 9. With Anchor C
excluded on mechanism-mismatch grounds, this drill's revised central estimate and band:

**m*(970K) central estimate = 6 (nearest grid point to the [5.62, 6.74] Anchor-A-corrected range),
band [5, 7] on the {3..12} grid -- narrower than the source note's [5, 9], with the exclusion of {8, 9}
specifically because that upper range was Anchor-C-driven, not Anchor-A-driven.** Direction: **roughly
flat to mild growth from m5 @ 177,899**, not the steep growth a naive reading of "3 theories, 2 say
denser" might suggest. A residual allowance up to m7 (rather than capping strictly at m6) is kept for
two honest reasons, not overconfidence: (1) this exact channel is an independently-confirmed RESISTOR
to closed-form self-margin fitting (row 10, 2026-07-06) -- Anchor A should not be trusted to the last
decimal even where it's the mechanism-matched theory; (2) the already-landed 177,899 data shows the
cross-seed CV curve starting to rise at m8 (an early-warning signal for approaching a bifurcation,
per the source note's own re-analysis) -- this is weak evidence the system may want a LITTLE headroom
above the bare Anchor-A number as V grows, not a reason to abandon the mechanism-match, but a reason not
to round down to a single point.

## Item 4 -- A named caveat this reconciliation surfaces (hubness, not dimension-count)

Correlation/redundancy has TWO distinct effects on the continuous channel, not one, and this drill's
Anchor-A match only addresses the first:

1. **Dimension-requirement effect (addressed above):** reduced effective dimension -> fewer ambient
   dimensions needed to preserve overall geometry -> Anchor A's correction is directionally and
   mechanistically justified.
2. **Hub-formation effect (NOT addressed by the dimension-requirement correction, a separate,
   already-flagged risk in the marchenko-pastur note's own citations):** concentrated near-duplicate
   clusters (the SAME 15.86%-of-V chunk population driving the effective-distinct correction) are
   exactly the structure the hubness literature (Radovanovic, Nanopoulos, Ivanovic 2010, already cited
   in the marchenko-pastur note) predicts will distort a top-10 rank-agreement metric locally, even if
   the AGGREGATE dimension requirement is adequately met. A cluster of 8-10 near-identical items
   competing for the same few "top-10 slots" in each other's neighbor lists is a local crowding problem
   the global JL-style dimension count does not fix by construction -- it is a within-cluster problem,
   not a whole-corpus dimension problem. **This means: even if the aggregate `ret_agree10` tracks this
   drill's Anchor-A-predicted trend at the chosen m*, the chunk-cluster subpopulation (~15.86% of items)
   should be expected to show WORSE `ret_agree10` than the non-chunk population at the SAME m** --
   this is a new, cheap, falsifiable, additive test (stratify any sweep rung's item-level ret_agree10
   results by chunk-cluster membership, exactly the axis the near-dup Test-0 note already proposed for
   the discrete channel's `keyed@J5`/`shuffled_key`, extended here to the continuous channel).

## Cheap decisive test

Stratify R1's (50K rung, already-designed in the density-scale-sweep note, not new dispatch) per-item
`ret_agree10` results by whether each item is a member of a document-chunk near-dup cluster (same
grouping the near-dup Test-0 note already computed on the full `entities.jsonl`) vs. not. This requires
zero new GPU work beyond what R1 already runs -- only a post-hoc regrouping of already-logged per-item
results using an already-computed cluster-membership table. Two questions answered at once, cheaply:
(a) does the aggregate trend match Anchor A's mild-growth prediction (the reconciliation's headline
claim), and (b) does the chunk-cluster subpopulation show the predicted hub-degradation gap (Item 4's
caveat) independent of (a).

## Falsifiable predictions

**HARD-PASS (reconciliation approach validated):** across R1(50K)->R2(100K)->R3(177,899, already
landed)->R4(~400K), the cross-seed-min-maximizing density stays within {5, 6, 7} throughout -- i.e.
roughly flat/mild growth as Anchor A (orthogonality-corrected) predicts, NOT a monotone climb toward
or past m9-10 (which would indicate Anchor C's i.i.d.-additive-interference regime actually governs
this channel despite the mechanism mismatch this drill identifies) and NOT a monotone fall toward m3-4
(which would indicate Anchor B's aggregate-information objective actually governs despite this
channel's per-item fidelity gate).

**HARD-FAIL (mechanism-classification wrong, novel-synthesis claim refuted):** the cross-seed-
min-maximizing density trajectory shows CLEAR super-linear growth consistent with Anchor C's
sqrt(V)*ln(V) form (by R4/400K, Anchor C predicts ratio ~1.6-1.8x today's density already, i.e. m
pushing toward/past the top of the currently-tested {3,5,8} grid, likely requiring extension to
m10-12) -- this would mean the "additive-interference vs geometric-placement" mechanism split this
drill proposes is WRONG for this channel (the continuous readout behaves more like a collision-style
mechanism than the taxonomy's Family-1 classification implies), extending the row-10 RESISTOR finding
from "resists closed-form curve-fitting" to "resists mechanism classification," a stronger and more
consequential negative result.

**HARD-FAIL (opposite direction):** the trajectory shows a clear monotone DECLINE toward m3-4 as V
grows (Anchor B's direction) -- would mean the aggregate-information-efficiency objective is somehow
the one the ship metric is actually rewarding, contrary to this drill's reading of `ret_agree10` as a
per-item uniform fidelity gate; would require re-examining whether the metric's cross-seed-MIN
selection criterion behaves more like an average-case than a worst-case statistic in practice.

**MIDDLE (hub-effect confirmed, dimension-count effect also confirmed -- both true simultaneously,
most likely outcome per this drill's own synthesis):** aggregate trend matches Anchor A (HARD-PASS
above) AND the chunk-cluster subpopulation shows measurably worse `ret_agree10` than the non-chunk
population at the same m (Item 4's caveat confirmed) -- this is the most mechanistically coherent
outcome and would mean the two named effects (global dimension adequacy vs. local hub crowding) are
BOTH real and separable, actionable via a cheap targeted fix (deduplicate/merge the chunk clusters,
per the near-dup note's own already-identified ~14% V-reduction opportunity) rather than a global
density increase.

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):**
- P(Anchor A is the mechanism-matched theory for this channel, i.e. the aggregate trend stays flat/mild
  through R4 rather than tracking Anchor C or Anchor B): undeflated ~0.55-0.60 (solid taxonomy match +
  solid literature on both mechanism families independently, but the cross-domain bridge connecting
  them -- explicitly, no unifying paper found by any of the 3 lit-scans -- is this drill's own synthesis)
  -> **P_deflated = 0.35-0.40**.
- P(the specific corrected band [5,7] contains the true 970K optimum, narrower claim than the source
  note's own P_deflated=0.20-0.25 for its wider [5,9] band): this drill does NOT claim a higher
  confidence than the source note despite narrowing the band -- narrowing a band on the same amount of
  evidence should not, by itself, raise confidence; **P_deflated = 0.20-0.25, held at the source note's
  existing figure**, with the honest caveat that if the narrower band is wrong, it is more likely wrong
  than the wider band would have been (a direct, stated tradeoff of this drill's sharper claim).
- P(the hub-formation caveat, Item 4, is measurably confirmed when tested): undeflated ~0.50-0.60
  (mechanistically well-supported by cited hubness literature and the near-dup note's own cluster
  measurements, but untested on this specific encoder) -> **P_deflated = 0.35-0.40**, capped at the
  novel-synthesis 0.50 ceiling.

## Cross-thread synthesis

Directly extends three prior threads without re-deriving them: (1) the density-scale sweep design's
Item 1 (the 3 disagreeing anchors) -- this drill answers the "why do they disagree" question that note
explicitly left open, and revises its blended [5,9] band down to [5,7] on mechanism-matching grounds,
not new data; (2) the self-margin taxonomy's Family 1/Family 2 decode-mode classification -- this drill
is the first to connect that internal taxonomy directly to the external theories' own implicit storage-
mechanism assumptions, resolving why "does correlation help or hurt" has no single answer in the
literature (it depends on which family is being asked about) and giving the taxonomy a second point of
external validation (its Family 1/2 split now also predicts which of 3 independently-derived external
theories applies, not just internal capability forecasts); (3) the near-dup Test-0 note's effective-
distinct measurement and its own "chunk-cluster vs non-chunk, stratify per-item results" methodology --
reused verbatim here, extended from the discrete channel (where it was proposed) to the continuous
channel (where this drill proposes the same stratification for a different, hub-formation reason).

## Substrate-product implications

For Director: this drill does not change the recommended action from the density-scale sweep design
(R1+R2 now, fold R4 into Stage 3, per that note's own cost/value case) -- it sharpens the PREDICTION
that sweep will be checked against, from a wide [5,9] band with implicit weight on a mechanism-
mismatched theory (Anchor C) to a narrower [5,7] band built on a mechanism-matched theory (Anchor A)
plus an honest resistor-channel margin. The practical value: if R1/R2 land within [5,7], that is a
stronger confirmation of the theory-informed-extrapolation approach (validates the mechanism-matching
reconciliation, not just "some theory happened to be close"); if R1/R2 instead show density climbing
toward Anchor C's much steeper prediction, that is a MORE surprising and MORE informative negative
result than the source note's wider band would have registered (a plain miss inside [5,9] would have
been ambiguous about which theory was closer; a miss outside the narrower [5,7] band cleanly implicates
Anchor C and forces re-examining whether the continuous channel secretly behaves like an additive-
interference mechanism). Separately, Item 4's hub-formation caveat gives a concrete, cheap, near-zero-
cost mitigation path independent of the density-dial question entirely: deduplicating the ~153,773
chunk rows to their ~15,626 effective source-document units (already identified in the near-dup note)
would reduce BOTH the dimension-requirement pressure (smaller effective V, per Item 3) AND the
hub-formation risk (fewer near-identical competitors per cluster) simultaneously -- a single cheap
KB-hygiene action addressing two separate mechanisms this drill identifies, worth prioritizing before
or alongside the density-dial retune itself.

## Citations (verified count)

Three parallel Sonnet lit-scan sub-agents dispatched this cycle, generic math/CS/neuroscience terms
only per [[feedback-query-privacy-decomposition]] -- zero substrate-novel mechanism names sent
externally. One sub-agent flagged degraded PDF full-text access (poppler unavailable, some PDFs
returned corrupted binary) -- findings from that agent are marked accordingly above where confidence
is medium rather than high.

**Correlated-pattern/fill-factor sub-agent (8 sources):** Willshaw, Buneman & Longuet-Higgins, *Nature*
222 (1969); Palm, *Biol. Cybernetics* 36 (1980); Buckingham & Willshaw, *Network* (1992); Gibson &
Robinson, *Neural Networks* 5 (1992); Nadal & Toulouse (1990); Nadal, *J. Phys. A* 24 (1991); Knoblauch,
Palm & Sommer, *Neural Computation* 22(2) (2010); Löwe, *Ann. Appl. Probab.* (1998, correlated-pattern
Hopfield capacity + moderate-deviations companion).

**Fixed-fidelity-scaling sub-agent (2 new + reuse of KPS/Löwe above):** McEliece, Posner, Rodemich &
Venkatesh, *IEEE Trans. Info. Theory* (1987, Hopfield associative memory capacity); a 2020s arXiv
feature-correlation-and-associative-memory-capacity paper (found via search, exact identifier not
independently confirmed by second source -- flagged low-confidence citation).

**JL/intrinsic-dimension sub-agent (8 sources):** Larsen & Nelson, FOCS (2017, arXiv:1411.2404,
tightness); Baraniuk & Wakin, *Found. Comput. Math.* 9 (2009, manifold-JL); Clarkson (2008, geodesic-
distance sharpening); Indyk & Naor, *ACM Trans. Algorithms* 3(3) (2007, doubling dimension); Gao,
Ganguli et al. (2017, participation-ratio dimensionality theory) + arXiv:2509.26560 (2026, PR
bias-correction); Donoho & Tanner-family phase-transition work (arXiv:1111.6822); "Universal Hopfield
Networks" (arXiv:2202.04557, unifying auto-/hetero-associative models, NOT unifying with JL -- cited as
evidence the cross-domain gap is real).

**Verified count: 18 distinct new external sources found via live web search across 3 sub-agents this
cycle (builds on 66 already-verified sources across the two prior notes in this thread); zero fabricated
citations. All three sub-agents independently and explicitly flagged the SAME honest gap: no published
paper unifies JL-type distance-preservation theory and Willshaw/Hopfield-type associative-memory-capacity
theory under one "effective load" variable, and no paper explicitly plugs a participation-ratio/effective-
rank correction into either a JL bound or a Willshaw fill-factor formula as an N_eff substitute. This
drill's mechanism-matching reconciliation (Item 1-2) is therefore NOVEL SYNTHESIS on this project's part,
not a literature-confirmed unification -- calibrated accordingly throughout (P_deflated capped at 0.40,
below the standard 0.50 novel-synthesis ceiling, given three independent lit-scans confirming the same
gap rather than one).**
