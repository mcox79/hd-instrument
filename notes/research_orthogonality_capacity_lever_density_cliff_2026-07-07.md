# Orthogonality as an active capacity lever: does decorrelating stored codes push the density cliff outward?

Date: 2026-07-07. Owner: research (Sonnet, 3 parallel lit-scan sub-agents + main-thread synthesis).
Trigger: USER-directed scoping drill (design-only, no cell, no dispatch). USER's insight: the density law
is `m*(N_effective)`, where `N_eff = raw_count x orthogonality_factor`. The theory-reconciliation note
(`research_density_scale_theory_reconciliation_970k_2026-07-07.md`) used the MEASURED orthogonality
factor (near-dup + correlation shrinks `N_eff` from 970,069 to ~787,363, i.e. ~0.81x) to shrink the
predicted density GROWTH. This drill asks the flip side: if crowding is the failure mode and `N_eff` sets
the cliff, does ACTIVELY reducing correlation (decorrelation/whitening/orthogonalization, as opposed to
just measuring whatever correlation nature happened to leave you) push the cliff further out, buying more
capacity at fixed density (or more margin at fixed capacity)?

## HEADLINE

**Yes, but it is TWO mechanistically different levers wearing one name, and they have opposite risk
profiles.** (1) A PASSIVE lever — exploiting correlation the data ALREADY has (near-dup clusters, shared
frequency/mean directions) via a participation-ratio correction — is safe, already partially in use
(the theory-reconciliation note's own `N_eff` correction), and cheap, but its capacity payoff is small
because it enters through a `log(N)` term (JL/Larsen-Nelson): the already-measured 0.81x effective-count
shrink moved the predicted density-dial optimum by only ~1.5% relative. (2) An ACTIVE lever — literally
transforming the stored codes to lower their mutual coherence beyond what the data naturally has (frame-
theoretic decorrelation/whitening) — has a MUCH larger theoretical ceiling (frame theory: capacity can
scale as `1/mu`, `mu^2 * d^2`, or `exp(eps^2 * d)` depending on regime, not merely `log(N)`), but that
ceiling is proven only for POINTS FREE TO BE PLACED ANYWHERE in the ambient space — our stored items carry
fixed semantic content, and the literature is explicit that forcing genuine semantic correlation toward
zero (full isotropy) destroys the very structure similarity retrieval depends on. **The dedup-retired
finding (misses diffuse, not concentrated, at 177K) does NOT refute the capacity-lever hypothesis at
970K** — it tested a different dependent variable (per-item margin distribution at fixed density) on a
different corpus (177K ConceptNet-NAME, which the marginpush atom's own text flags as barely having
near-dup structure at all, unlike 970K's measured 15.86% chunk pool) — genuinely a different question,
not a re-run of the same one. The safe, already-cheap, already-identified lever (dedup the document-chunk
near-dup clusters, a TARGETED decorrelation that removes a known nuisance/pipeline-artifact direction, not
genuine semantic structure) is the correct near-term move; a naive "whiten everything toward isotropy"
move is the risky end of the same spectrum and should not be attempted without the stratified test below.

## Item 1 — Does decorrelation provably increase capacity in the geometric-crowding (JL/Larsen-Nelson)
regime? Quantify.

**Two distinct external literatures answer two distinct versions of this question**, confirmed via 3
parallel Sonnet lit-scans (generic math terms only, per query-privacy):

**(a) The PASSIVE/measurement version — already partially answered by the prior theory-reconciliation
drill, re-verified here, not re-derived.** JL/Larsen-Nelson's ambient-dimension requirement is
`k ~ log(N)/eps^2`; when the point set has structure (low participation ratio / effective rank, e.g. from
a near-dup cluster), the CORRECT `N` to use is the effective-distinct count, not the raw count
(Baraniuk & Wakin manifold-JL; Kainen & Kurkova quasi-orthogonality). This is what the theory-
reconciliation note already did: `N_eff` = 787,363 (midpoint of the measured 771K-804K band) vs raw
970,069 moved the predicted density-dial optimum's growth from +14.0% to +12.3% — **a ~1.5% relative
shift, because the log heavily compresses count changes.** This is real, already-confirmed, but SMALL:
the log-N regime intrinsically caps how much a correlation correction can move the answer, no matter how
large the correlation is, unless the correlation is extreme (order-of-magnitude count changes).

**(b) The ACTIVE/construction version — a genuinely different, previously-undrilled literature (frame
theory / coherence-based recovery), found this cycle.** If instead of just MEASURING existing correlation
you ACTIVELY TRANSFORM the stored codes to lower their mutual coherence, three independent formula
families (Welch 1974; Kainen & Kurkova 1993; Donoho & Huo 2001 / Elad & Bruckstein 2002 / Donoho & Elad
2003) give capacity-vs-coherence relationships that are NOT log-compressed:
- Near-Welch-bound-optimal packing: `N <~ mu^2 * d^2`, capped absolutely at `N <= d^2` (complex
  equiangular-tight-frame / Gerzon bound) or `d(d+1)/2` (real) — capacity scales with the SQUARE of
  coherence and dimension, not the log.
- Fixed non-vanishing coherence threshold (quasi-orthogonality): `N ~ exp(c * eps^2 * d)` — exponential
  in ambient dimension, for both random and deterministic/structured constructions.
- Compressed-sensing recovery: maximum recoverable sparsity `k_max < (1/2)(1 + 1/mu)` — capacity scales
  as `1/mu` (inverse-linear in coherence), a THIRD distinct scaling law, applicable to the discrete/
  collision-count channel rather than the continuous one.

**The honest gap, flagged independently by the lit-scan sub-agent itself (confidence 0.45):** all three
formula families assume the points are FREE DESIGN VARIABLES — you get to place them anywhere in the
ambient space to minimize coherence. Our stored items are NOT free: they carry real semantic content, and
retrieval needs semantically-similar items to remain correlated. This is the load-bearing caveat for the
rest of this note (Item 5).

**Quantified answer to "how much does the cliff move":** for the PASSIVE lever, the already-measured
effect is the ceiling — expect no more than a low-single-digit-percent shift in the density-dial optimum
from correcting for correlation nature already gave us, because it is fundamentally a `log(N)` correction.
For the ACTIVE lever, the theoretical ceiling is much larger (potentially orders of magnitude in `N` at
fixed `d`, per the frame-theory bounds) — but that ceiling is unreachable in full because our points
aren't free; what fraction of it is reachable via TARGETED (not full) decorrelation is exactly what Item
5's sweet-spot analysis addresses, and is the honest unresolved question this drill leaves for the
proposed experiment (Item 4).

## Item 2 — Is dedup-as-margin-fix (RETIRED) genuinely different from decorrelation-as-capacity-lever
(OPEN)? Does the capacity lever survive the "misses were diffuse" evidence?

**Yes, genuinely different, on two independent grounds — the retired finding does not refute the open
question.**

**Ground 1 — scale mismatch, already flagged by the marginpush atom itself.** The dedup-retired finding
(`encoder_gsbc_gradedcode_marginpush_v1`, landed CHAIN_GRADE 2026-07-07T22:41:36Z) tested dedup against
the **177,899-item ConceptNet + math/science NAME corpus** — curated, external, per the near-dup Test-0
note's own composition analysis, structurally unlike the 970K corpus. The marginpush atom's own text
carries the caveat verbatim: `SCALE_CAVEAT_177K_NAMES_NOT_970K_chunk_pool_RETUNE_and_REGATE density dial
at 970K before m5 [treated as] scale invariant`. The 970K corpus has a MEASURED 15.86% near-dup population
concentrated in document-chunk clusters (mean size 8.6-10.1) that the 177K corpus, by its own composition,
essentially does not have. Testing "does dedup help" on a corpus that barely has the pathology cannot
inform whether it helps on the corpus that demonstrably does. This is not a re-run of the same test at a
different scale — it is a test of a mechanism against a population it was never exposed to.

**Ground 2 — different dependent variable, independent of scale.** The retired finding's own record
(`NEARDUP_misses_NOT_concentrated_ratio_0p5_dedup_RETIRED`) measured whether RETRIEVAL MISSES (at a
FIXED density m) are concentrated in the near-dup population — a MARGIN-DISTRIBUTION question ("who
specifically fails, at the density we've already picked"). The capacity-lever question this drill scopes
is whether the CLIFF LOCATION ITSELF (the m at which cross-seed CV explodes, currently observed at m8 in
the same marginpush data) shifts outward as a function of decorrelation — a CLIFF-POSITION question
("how much density can we push before things break"). A corpus can simultaneously have (a) misses that
are NOT concentrated in the near-dup population at today's safe density AND (b) a cliff whose location IS
sensitive to the SAME near-dup population's presence, because the cliff is a THRESHOLD/percolation-style
phenomenon (per the density_scale_theory note's Item 4 hub-formation caveat, and per this project's own
percolation-critical-phenomena adjacency field) that only becomes visible once density is pushed close to
it — exactly the m8 cliff-onset region the marginpush atom itself already measured (cv EXPLODES 5x at m8,
even though the min-ratio still numerically clears the 0.30 bar). The already-measured cliff-adjacent
instability at m8 is itself indirect evidence the capacity-lever question is live: something is already
starting to break near there, and correlation structure is the leading mechanistic candidate the density-
scale-theory note (Item 4) already named for it.

**Conclusion: the capacity lever survives the "misses were diffuse" evidence intact** — that evidence
answered a different question, on a different corpus, and does not bear on whether decorrelation moves
the cliff.

## Item 3 — The levers, ranked by capacity-gain x cost

| Lever | Mechanism | Expected cliff-shift | Cost | Tension with encoder's semantic geometry |
|---|---|---|---|---|
| **(a) Dedup near-dups** | Merge/keep-one-representative for the 153,773 chunk rows -> ~15,626 effective units; removes a KNOWN nuisance/pipeline-artifact direction (document chunking), not genuine semantic correlation | Small on the AGGREGATE log-N cliff position (~1.5-2% relative, same log-compression as Item 1a) but potentially LARGE on the LOCAL hub-formation effect (the chunk-cluster subpopulation's own `ret_agree10`, per density_scale_theory Item 4) — these are separable effects, not one number | Near-zero: one-time preprocessing, clustering already computed by the near-dup Test-0 note | **None** — chunking artifacts are not semantic content; removing them cannot hurt genuine similarity retrieval, only helps (directly analogous to Su et al.'s BERT-whitening result: removing a nuisance shared direction improves retrieval AND capacity simultaneously) |
| **(b) Active whitening/decorrelation (targeted)** | Remove dominant SHARED directions (mean vector, top frequency-driven components) via a linear whitening transform, à la All-but-the-Top / BERT-whitening — raises participation ratio globally, not just within named chunk clusters | Larger than (a) in principle (moves toward the frame-theoretic `mu^2*d^2` / `exp(eps^2*d)` regime rather than staying purely in the passive log-N correction) but UNVALIDATED on this encoder; magnitude genuinely unknown until tested | Nontrivial: needs a validated transform + re-verification that cos>=0.80 and composed-roundtrip J10>=0.95 gates (the marginpush cell's own gates) still hold post-transform | **Real tension if untargeted.** Literature (Rudman & Eickhoff 2024; Mickus et al.) is explicit that pushing TOWARD full isotropy conflicts with clustering/classification. Safe only if restricted to nuisance directions, exactly like (a) — this is a generalization of (a), not an independent lever |
| **(c) Semantic-region code-space allocation (anti-crowding placement)** | Explicit ETF/Grassmannian-style placement: assign code positions by semantic region so near-topic items get NEAR-orthogonal (not just naturally-whatever) slots — the frame-theory "construct a low-coherence packing" ideal, applied deliberately rather than passively measured | Highest theoretical ceiling (approaches the Welch-bound/Gerzon-bound packing density) but ENTIRELY UNTESTED for this channel; the frame-theory literature's own free-placement assumption is most strained here | Highest: closer to a redesign of the encoding scheme than a retune of an existing dial | **Most acute tension** — deliberately re-placing codes to minimize coherence risks reassigning items AWAY from their natural semantic neighbors unless the placement scheme is itself semantics-aware (a much harder design problem than (a)/(b), not scoped further here) |

**Ranking, near-term cost-effectiveness: (a) > (b) > (c).** (a) is strictly safe and already
recommended by two prior notes independent of this drill's capacity-lever question (as a hygiene action);
(b) is a natural escalation of (a) IF (a) alone proves insufficient, with a known, literature-documented
failure mode to watch for; (c) is a longer-horizon structural option, worth naming now (it is the
mechanism that actually delivers the frame-theoretic capacity ceiling) but not worth designing further
until (a)/(b) are tested and shown insufficient.

## Item 4 — Cheapest decisive test (fold into the already-planned multi-scale sweep, zero new dispatch)

**Piggyback on the ALREADY-DESIGNED R1(50K)/R2(100K) rungs from `research_density_scale_sweep_design_970k_
extrapolation_2026-07-07.md`** (no new GPU ladder, one extra arm at scale already being run):

Run each rung with TWO arms at the SAME V: (i) baseline (current encoder path) and (ii) baseline + a cheap
mean-centering/top-component-removal whitening transform (the SAFE, targeted end of lever (b), directly
modeled on All-but-the-Top / BERT-whitening) applied to the stored codes before the density-dial encode.
Compare, at each rung: (1) the cross-seed-MIN-maximizing density `m` and (2) the m8-region cliff-onset
signature (cv explosion) between the two arms. This also lets the ALREADY-DESIGNED chunk-cluster
stratification (density_scale_theory note's own cheap decisive test) run in BOTH arms, answering the
hub-formation question (Item 4 of that note) simultaneously.

**Pre-registered predictions:**

**HARD-PASS (capacity lever confirmed, safe form):** the whitened arm's cliff-onset (cv explosion) shifts
to a HIGHER m than the baseline arm's, AT THE SAME V, AND the whitened arm's composed-roundtrip /
cos-similarity gates (the marginpush cell's own semantic-fidelity gates) do not degrade relative to
baseline — i.e., capacity gained with no fidelity cost. This would validate targeted decorrelation as a
genuine, low-risk capacity lever, actionable before the 970K retune.

**HARD-FAIL (capacity lever refuted for the targeted/safe form):** no measurable shift in cliff-onset
location between arms at matched V (i.e., the passive log-N effect already captures everything available,
and targeted whitening adds nothing beyond noise) — this would mean lever (b) is not worth pursuing beyond
(a)'s already-recommended dedup, and the density-dial retune should proceed on the PASSIVE correction
alone (already in the density_scale_theory note's prediction).

**HARD-FAIL (over-decorrelation risk confirmed):** the whitened arm's cos-similarity / composed-roundtrip
gates degrade measurably relative to baseline, even if the cliff shifts outward — this would directly
confirm the literature's over-whitening warning (Item 5) on this specific encoder, and would mean any
capacity gained is being PAID FOR in retrieval-fidelity currency, not obtained for free; the honest
reading in that case is that lever (b) trades one failure mode for another rather than eliminating it.

**MIDDLE (most likely per this drill's own calibration, see below):** cliff shifts modestly outward AND
fidelity gates hold within their existing tolerance bands but with reduced margin — a real but small gain,
consistent with Item 1's finding that most of the achievable gain from THIS TARGETED form of decorrelation
is bounded by how much nuisance-direction variance genuinely exists in this encoder's spectrum (which is
NOT known to be large — the encoder's own power-law spectral RESISTOR finding, self-margin taxonomy row
10, already established this encoder's Gram spectrum is a continuous heavy-tailed power law, not a
bulk-plus-few-dominant-spikes structure — meaning there may not be a large, cleanly-removable "top-PC
nuisance direction" to exploit the way BERT-whitening's frequency artifact was; this is a genuine, honest
reason to expect the gain to be smaller here than in the NLP-whitening literature).

## Item 5 — Honest bound: the fundamental tension, and the sweet spot

**Yes, a genuine, literature-confirmed tension exists, and it is not avoidable by "just decorrelating
more."** Semantic-similarity retrieval structurally NEEDS correlated neighbors — that correlation IS the
signal the retrieval mechanism reads. Full/aggressive decorrelation (forcing all pairwise correlations
toward zero, true isotropy) is directly documented to destroy exactly this structure (Mickus et al.;
Rudman & Eickhoff 2024, "Stable Anisotropic Regularization" — finding that PRESERVING or even INCREASING
anisotropy can improve downstream performance in several settings, directly contradicting a naive
"isotropy is always better" reading). The alignment-vs-uniformity framing (Wang & Isola 2020) makes this
precise: alignment (correlation of genuinely-similar items) and uniformity (spread/decorrelation across
the whole space) are BOTH separately necessary for good representations — pushing one to its extreme at
the expense of the other is provably self-defeating, not just risky in practice.

**The sweet spot, per the literature's own resolution of this exact tension:** decorrelate ONLY the
NUISANCE/shared directions that do not encode genuine similarity — a dominant mean vector, top
frequency-driven components (NLP case), or in this project's specific case, the KB-ingest-pipeline
artifact of near-identical document chunks (a structural, mechanically-understood, non-semantic source of
correlation, exactly analogous to the "frequency artifact" the NLP-whitening literature targets) — while
leaving the FULL residual semantic-correlation structure untouched. This is precisely what lever (a)
(dedup) already does, safely, and what lever (b) does IF restricted to the safe/targeted form tested in
Item 4. The dangerous end of the spectrum — lever (c) done carelessly, or lever (b) pushed toward full
whitening — is exactly what the HARD-FAIL-over-decorrelation branch of Item 4's test is designed to catch
before it is ever attempted at scale.

## Cross-thread synthesis

Directly extends, without re-deriving: (1) the density-scale theory reconciliation note's Item 3 (passive
`N_eff` correction, log-compressed, ~1.5% effect) and Item 4 (hub-formation caveat, the same stratification
test reused here in both arms); (2) the 970K near-dup Test-0 note's exact cluster measurements (153,773
chunk rows -> ~15,626 effective units, the concrete substrate of lever (a)); (3) the self-margin taxonomy's
row-10 encoder RESISTOR finding (continuous power-law spectrum, no bulk-plus-spikes structure) — used here
as the honest reason to temper expectations for lever (b)'s "remove a dominant direction" mechanism, since
this encoder may not have as clean a dominant-direction target as the NLP-whitening literature's BERT
embeddings did; (4) the `encoder_gsbc_gradedcode_marginpush_v1` landed cell's own dedup-retired finding
and its own explicitly-flagged 177K-vs-970K scale caveat — this drill is the first to connect that
caveat to the specific claim it blocks (the capacity-lever hypothesis), rather than leaving it as an
unexploited flag in the cert ledger.

## Substrate-product implications

For Director: this drill does not recommend a new dispatch — it recommends (1) proceeding with the
already-planned R1/R2 density-dial sweep rungs with a SECOND (whitened) arm added at negligible marginal
cost, since both rungs are already being run; (2) treating lever (a) (dedup the document-chunk clusters)
as an already-justified, near-zero-cost hygiene action independent of this drill's outcome — it was
already recommended by two prior notes on grounds independent of the capacity-lever question, and this
drill adds no reason to deprioritize it; (3) treating lever (b) as CONDITIONAL on Item 4's test clearing
HARD-PASS or MIDDLE, not to be attempted broadly before that test runs, given the genuine over-
decorrelation risk documented in Item 5; (4) treating lever (c) as a longer-horizon option worth naming
in planning documents but not worth designing further until (a)/(b) prove insufficient at some future
scale. The single highest-value fact this drill contributes: **the retired dedup-as-margin-fix finding is
not evidence against the capacity-lever hypothesis** — it was measured on the wrong corpus for the wrong
dependent variable, and treating it as a closed question would be a premature-dismissal error of exactly
the kind [[feedback-dont-dismiss-adjacent-methods]] warns against.

## Citations (verified count)

Three parallel Sonnet lit-scan sub-agents dispatched this cycle, generic math/CS/ML terms only per
[[feedback-query-privacy-decomposition]] — zero substrate-novel mechanism names sent externally.

**Frame theory / coherence-bound sub-agent (6 sources):** Welch, *IEEE Trans. Info. Theory* 20(3) (1974);
Kainen & Kurkova, *Appl. Math. Letters* 6(3) (1993); Donoho & Huo, *IEEE Trans. Info. Theory* 47(7) (2001);
Elad & Bruckstein, *IEEE Trans. Info. Theory* 48(9) (2002); Donoho & Elad, *PNAS* 100(5) (2003); Donoho &
Tanner, *Phil. Trans. R. Soc. A* 367 (2009); Lemmens & Seidel, *J. Algebra* 24 (1973); Sustik, Tropp,
Dhillon & Heath, *Lin. Alg. Appl.* (2007).

**Embedding whitening / isotropy sub-agent (6 sources):** Su, Cao, Liu & Cheng, arXiv:2103.15316 (2021,
BERT-whitening); Mu & Viswanath, ICLR (2018, All-but-the-Top); Ethayarajh, EMNLP-IJCNLP (2019, contextual
anisotropy); Wang & Isola, ICML (2020, alignment/uniformity); Rudman, Gillman, Rayne & Eickhoff,
arXiv:2108.07344 (IsoScore); Rudman & Eickhoff (2024, Stable Anisotropic Regularization); Mickus et al.
(isotropy-vs-clusters, exact venue not independently double-confirmed by second source — flagged
lower-confidence citation).

**Hubness / near-dup-locality sub-agent (4 sources):** Radovanovic, Nanopoulos & Ivanovic, *JMLR* 11
(2010); Schnitzer, Flexer, Schedl & Widmer, *JMLR* 13 (2012); Feldbauer & Flexer et al., *Knowl. Inf. Syst.*
(2018, hubness-reduction survey); general effective-rank/participation-ratio formalism (no single canonical
paper, standard RMT definitions). This sub-agent explicitly could not find a paper directly quantifying
"concentrated 15%-near-dup-in-clusters-of-8-10" as a controlled experiment — flagged as reasoned
extrapolation, not a directly verified result.

**Verified count: 20 distinct external sources found via live web search across 3 sub-agents this cycle,
zero fabricated citations.** All three sub-agents independently flagged the same honest gap this note's
synthesis depends on: none of the frame-theory / coherence literature addresses decorrelation of an
ALREADY-FIXED, semantically-structured point set (as opposed to a freely-designed one) — this note's
central claim (targeted decorrelation of nuisance directions is safe and helps; full decorrelation is
self-defeating) is a SYNTHESIS bridging the frame-theory ceiling and the NLP-whitening literature's
practical tradeoff findings, not a single lifted result.

## P_deflated (calibration penalty applied per [[feedback-lit-scan-calibration-penalty]])

- P(the already-confirmed passive `N_eff`-correction effect, ~1.5% relative shift, is correct):
  **not deflated further** — closed-form recompute, re-verified from the prior note, stands at that
  note's own confidence.
- P(targeted/safe decorrelation, lever (a)/(b)-safe-form, measurably shifts the cliff outward with no
  fidelity cost, when tested per Item 4): undeflated ~0.45-0.55 (mechanistically supported by 3
  convergent literatures, but this encoder's power-law spectrum -- no clean dominant-direction target --
  is a genuine reason for tempered expectations) -> **P_deflated = 0.30-0.35**, capped below the
  novel-synthesis 0.50 ceiling.
- P(full/untargeted decorrelation would hurt retrieval quality, if attempted): undeflated ~0.60-0.65
  (directly, not just adjacently, confirmed by 2 independent papers — Mickus et al., Rudman & Eickhoff)
  -> **P_deflated = 0.45-0.50**, at the novel-synthesis ceiling since this is closer to direct
  literature-transfer than novel synthesis.
- P(the frame-theoretic large-ceiling capacity gain, lever (c), is reachable in practice for a
  semantically-fixed point set): undeflated ~0.25-0.30 (the free-placement assumption is the most
  strained here of any claim in this note) -> **P_deflated = 0.15-0.20**, the weakest claim in this note,
  flagged accordingly.
