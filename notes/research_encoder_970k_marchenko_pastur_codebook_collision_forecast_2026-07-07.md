# Encoder codebook collision / retrieval-crowding forecast at 970K production scale

Date: 2026-07-07. Owner: research (Sonnet). Trigger: USER-directed forward-derivation drill
("what does the >=400K scale-test's outcome look like BEFORE spending a GPU run"), analysis-only,
no dispatch. Field-advisor context: `free-probability` is flagged tier-1/fruit-bearing +
under-drilled (F1 Marchenko-Pastur on block codes explicitly named); this drill is that named
candidate, executed as a USER-directed engineering-forecast (Trigger-E-equivalent), not a fresh
abstract lit-scan pick.

## HEADLINE

**The encoder has TWO distinct readouts with TWO distinct collapse mechanisms, and only ONE of
them is actually at risk from "collision" in the Marchenko-Pastur/birthday sense.** (1) The
discrete SBC block-argmax code (K=128 slots x L=32, `N_DIM=4096`) that backs keyed bind/unbind
algebra is governed by the **collision-count** regime (disjoint-block decode, taxonomy family 2):
its combinatorial code space (32^128 ~ 10^192) is so astronomically larger than V=970,069 that
*random* birthday collisions are a non-issue (M >> N^2 by ~180 orders of magnitude) -- this
channel is forecast to **hold, not cliff**, at production scale, UNLESS the production KB carries
a materially higher *structured* near-duplicate rate than today's ConceptNet-based 177,899. (2)
The continuous dense readout that backs retrieval-ranking (`ret_agree10`) is governed by
**distance-concentration / hubness** (order-statistic family, PR-corrected): this channel is
**already failing today** (0.18-0.27 at V=177,899, 18% of production scale, below the 0.30 bar)
and the literature is unambiguous that this failure mode gets monotonically *worse*, not better,
as V grows at fixed ambient dimension -- with **no cliff**, but also **no spontaneous recovery**.
**Forecast: plain-SBC ret_agree10 is expected to HARD-FAIL at 970K (graceful further decline from
an already-failing baseline); the GSBC graded-code lever is directionally the RIGHT fix (it already
measures 1.5-3x better at the SAME 177,899 scale) but its own density-dial retune is unverified
past ~160K and is the one place a genuine sharp (Donoho-Tanner-class) cliff could plausibly
appear, not the base encoder's smooth decline.**

## Item 1 -- Decode-mode classification (per [[reference_self_margin_taxonomy_splits_by_decode_regime]])

On-disk geometry, independently pulled (not trusting the prompt's framing):
`experiments/exp_encoder_migration_step1b_v3_..._core.py`: `N_DIM_DEFAULT = 4096`,
`K_BLOCKS_PRIMARY = 128` (`# L=32; sparsity 3.125%`), student `Linear(1024->2048) GELU
Linear(2048->4096)` distilling a BGE-large-v2 (1024-dim) teacher. `crlb_floor_computed = 0.901`
at K=128 via `r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K)` (THEORETICAL, unchanged
across the v2-v4 lineage). Two readouts share this geometry:

| Readout | What it measures | Decode mode | Taxonomy family |
|---|---|---|---|
| Keyed bind/unbind (`keyed@J5` acc@1, `shuffled_key` control) | Discrete K=128-slot, L=32-way block-argmax code roundtrip | **Disjoint-block**: each of K=128 blocks independently argmaxed over L=32 alternatives, non-overlapping dimensions | Family 2, collision-count: `p1 = n_distinct(codebook)/V`, exact |
| Retrieval-ranking (`ret_agree10`) + dense semantic (spearman-to-teacher) | Continuous 4096-dim embedding, nearest-neighbor rank agreement vs BGE teacher's own top-10 | **Correlated superposition-adjacent**: not a bundle/sum, but V points competing in a shared continuous manifold -- structurally the same "many correlated competitors" problem the taxonomy's family-1 PR-correction was built for | Family 1 (order-statistic), PR-corrected: effective competitor count `m = PR(V)`, not V |

This is the classification step the taxonomy mandates BEFORE forecasting: **the two readouts do
not share a failure mechanism** and must be forecast separately. Treating them as one "codebook
collision" question (as a naive read of "Marchenko-Pastur on the encoder" might invite) would
conflate a near-zero-risk channel with an already-failing one.

**Important scope note on the CRLB:** `r_max=0.901` is a **V-independent** per-key decodability
SNR bound (single bind/unbind roundtrip against one stored code) -- it does not, by itself, predict
collision or retrieval degradation as V grows. It only becomes V-relevant indirectly: if the
production KB's larger vocabulary genuinely shrinks the *effective* `sigma_teacher` (the
discriminative margin between a concept and its most-confusable neighbor, likely to shrink as
near-duplicate density rises), re-deriving the SAME formula with a smaller measured `sigma_teacher`
at 970K would predict a lower `r_max` even with K unchanged -- this is the ingest-scoping note's
own flagged Q1 ("CRLB floor... not re-derived for 970K's larger vocabulary"), and this drill agrees
it is a real, currently-unmeasured gap, not resolved by this analysis.

## Item 2 -- Discrete algebra channel: collision-count forecast (HOLDS, with a named caveat)

Standard uniform birthday scaling (verified via lit-scan): for N items placed into M codewords,
P(collision) ~ N^2/2M, non-negligible once N exceeds roughly 0.1-0.3*sqrt(M). At N=970,069 and
M=32^128 ~ 10^192, N^2/2M ~ 10^12/10^192 -- collision probability from *uniform-random* assignment
is identically zero to any practical precision. Even severe combinatorial pessimism (assume only
an effective handful of "genuinely independent" blocks out of the nominal 128, say 20-30) still
leaves M >> 10^30, dwarfing N^2 ~ 10^12 by ~18+ orders of magnitude. **The combinatorial margin on
this channel is not a close call.**

The real risk is NOT random collision but **structured collision**, and here collision-entropy
theory gives the exact correction: true collision probability of a per-block usage distribution is
`sum(p_i^2)`, minimized only at uniform (`1/L`) and strictly larger under any skew -- and per-block
skew composes **multiplicatively** across the K=128 blocks (`prod_k sum_s p_k(s)^2`), not
additively. This means the combinatorial-explosion margin and the skew penalty are in direct
tension: a single skewed block barely matters (multiplied against 127 others), but if MANY blocks
simultaneously collapse toward low-entropy usage for a *cluster* of near-identical concepts, the
product can erode the margin fast for that specific cluster -- while leaving the aggregate
`n_distinct/V` ratio for the rest of the vocabulary untouched. **This is a real-but-narrow risk**:
it predicts occasional exact-codeword collisions concentrated among genuinely near-duplicate
entities (disambiguation stubs, near-identical geographic/taxonomic entries -- exactly the entity
classes documented as a named Wikidata quality problem, Shenoy et al. 2021; the Freebase-to-Wikidata
migration discarded ~90% of Freebase's ~50M auto-generated entities partly over duplication/quality
concerns), not a general capacity cliff.

**Forecast: keyed@J5 acc@1 and the shuffled-key control are expected to remain near-ceiling
(>=0.90, <=0.10 leak) at 970K.** This channel's collapse, if it happens, will look like a small
number of specific near-duplicate collisions, diagnosable and fixable via KB dedup -- not a
capacity cliff requiring a code-family change.

## Item 3 -- Continuous retrieval channel: distance-concentration forecast (ALREADY FAILING, degrades further, no cliff)

Lit-scan finding (Beyer et al. 1999; Radovanovic/Nanopoulos/Ivanovic 2010 hubness; ANN-benchmark
scaling papers arXiv:2509.07789, arXiv:2404.19284): distance concentration / hubness is a
well-established, **smooth, monotonic** degradation mode as the number of stored points grows at
fixed ambient dimension -- NOT a sharp threshold. Empirical ANN-benchmark work reports recall decay
with corpus size as gradual and *parameter-recoverable* (larger search budget restores recall),
not a cliff. Separately, the n>>p regime of random-matrix theory (Chen & Pan 2012, Bernoulli
18(4): top eigenvalue of the normalized sample covariance -> 1 a.s. as p/n -> 0) says spectral
*estimation* noise actually **decreases** as V grows at fixed dimension -- i.e., the classical
Marchenko-Pastur "spreading" concern does NOT apply in this project's regime (V >> n_dim by a
factor of ~43-237x across the 177,899-970,069 range); the failure mode here is point-crowding
(distance concentration), not covariance-estimation noise.

**The decisive fact that changes this forecast from "watch and see" to "expect failure": at
V=177,899 (only 18% of the 970K target), `ret_agree10` is ALREADY measured at 0.18-0.27, below the
0.30 bar.** No mechanism identified in this drill predicts improvement with MORE competing points;
distance concentration is monotonic in the wrong direction. Absent a structural fix (density dial,
larger ambient dimension, graded coding), **plain-SBC `ret_agree10` is forecast to decline further
at 970K and HARD-FAIL the 0.30 bar with high confidence** -- this is not a marginal call requiring
the empirical test to adjudicate; the empirical test's main value here is measuring the *rate* of
further decline (for capacity planning), not resolving genuine pass/fail uncertainty on the plain
SBC path.

No PR(V) scaling-law paper for real embedding corpora was found in the lit-scan (item 2 of the
free-probability sub-agent's report is an honest literature gap, not a search failure) -- so the
"how much worse at 970K" question is NOT closed-form derivable from published results. The
qualitative direction (worse, not better, no cliff) is solid; the quantitative slope requires the
empirical measurement Item 5 below designs for.

## Item 4 -- Does GSBC help or hurt at 970K specifically

The adjacent lineage (`exp_encoder_v11_gsbc_graded_sparse_v1`, `v12_gsbc_gwta_expansion_v1`,
`exp_encoder_gsbc_gradedcode_retrieval_v1`; graded SBC + circular-conv binding + FlyHash-style
expansion) already measures `ret_agree10` = 0.31-0.68 **at the SAME scale** (n_train=160,109) where
plain SBC measures 0.18-0.27 -- a real, already-on-disk 1.5-3x improvement, not a speculative one.
Two independent mechanisms explain why this should help directionally:

1. **FlyHash-style expansion buys ambient headroom.** Per the lit-scan (Dasgupta/Stevens/Navlakha
   2017, fly olfactory circuit m~40d expansion; Chen & Pan's n>>p convergence result): a larger
   post-expansion ambient dimension directly reduces the point-crowding/distance-concentration
   effect that's driving plain-SBC's failure -- more "room" per stored point.
2. **Graded (non-one-hot) codes preserve continuous rank information** that pure block-argmax
   discards -- this is a plausible direct explanation for the already-measured 1.5-3x gain on a
   *rank-agreement* metric specifically (a metric that rewards preserved ordering, which coarse
   one-hot quantization destroys).

**But the "hurt" case is real and specific, not generic pessimism.** The GSBC lineage's own note
flags "density dial + full-M=177,899 composition VET" as still OPEN -- meaning GSBC's
*compositional/algebra* side has not itself been verified at even the CURRENT full scale, let
alone 970K. This matters because GSBC's headroom mechanism is structurally a **compressed-sensing /
sparse-recovery** problem (more active code, larger ambient dimension, but still finite), and this
is the ONE place the lit-scan found a genuine, textbook, SHARP threshold: Donoho-Tanner phase
transitions (`rho_S(delta) ~ (2e*log(1/delta))^-1`) and their dictionary-learning/associative-memory
analogues (NOODL; classical Hopfield capacity collapse) show recovery probability flipping from
~1 to ~0 abruptly once items-per-ambient-dimension crosses a critical ratio -- unlike the smooth
decline expected on plain-SBC's continuous retrieval channel. **If GSBC's expansion/density factor
is NOT retuned upward for 970K's larger V (i.e., tested with the SAME fixed expansion that worked
at 160K), it is the more likely of the two channels to exhibit an actual cliff, not the base
encoder's graceful decline.** This is a directly falsifiable, narrow claim (Item 5 test 3).

**Verdict: GSBC helps (measured, not speculative) but is UNVERIFIED past ~160K on its own
composition side, and is the more cliff-prone of the two code families if its density dial isn't
re-tuned for the larger V.** Net recommendation: GSBC is very likely still the right production
lever, but the scale-test must retune its expansion factor for 970K, not reuse the 160K-tuned
config.

## Item 5 -- Scale-test design recommendation

**Test 0 (cheapest, CPU-only, do BEFORE any GPU dispatch, directly tests the dominant structured-
collision hypothesis from Item 2):** measure empirical near-duplicate density in
`data/substrate_director_kb_v1/entities.jsonl` directly -- sample entity pairs, compute BGE-teacher
cosine similarity, and compare the fraction with similarity > 0.95 (or another near-duplicate
threshold) in a 177,899-entity subsample vs a 400K-970K sample. This is a pure data-quality
diagnostic, costs nothing beyond embedding a sample, and either confirms or refutes the "structured
collision, not random birthday" hypothesis before spending any GPU budget on the encoder itself.

**Test 1 (the ladder, not a single point):** don't test only at one intermediate N. Fit the actual
decline curve with at least 3 points (e.g. 177,899 [existing] -> ~400K -> ~700K -> 970K) for
`ret_agree10` and dense spearman on BOTH plain-SBC and GSBC. A single-point 400K test risks a false
PASS if the true curve only bites hard closer to 970K, or a false pessimism if the curve is
sub-linear/saturating. This is cheap to add (same cell, more teacher-cache sizes) and turns a
binary gate into an extrapolatable slope.

**Test 2 (gate the two channels SEPARATELY, do not conflate):**
- Discrete channel (keyed@J5, shuffled-key): HARD-PASS = stays >= 0.90 acc@1 / <= 0.10 leak through
  970K. HARD-FAIL = drops below 0.90 OR leak exceeds 0.10 -- and if it fails, cross-check against
  Test 0's near-duplicate measurement (this channel's failure, per Item 2, should correlate with
  measured near-duplicate density, not appear as a generic capacity collapse; if it fails WITHOUT
  elevated near-duplicate density, the collision-count model itself is wrong and needs revision).
- Continuous channel (ret_agree10, dense spearman): given the forecast is "already failing,
  degrades further, no cliff," the useful HARD-FAIL/HARD-PASS bands are on the EXTRAPOLATED 970K
  value from the fitted slope, not a single-scale readout: HARD-PASS = extrapolated 970K
  `ret_agree10` >= 0.30 AND dense spearman >= 0.82 (matches the ingest-scoping note's Stage-3
  bands). HARD-FAIL = extrapolated 970K value falls below an absolute usability floor (proposed:
  0.10 for `ret_agree10` -- below this, retrieval is not meaningfully better than random for
  top-10 purposes) even if the decline is smooth and non-catastrophic-looking at 400K.

**Test 3 (GSBC-specific, addresses Item 4's cliff-risk directly):** run GSBC's scale-test with an
EXPLICIT density-dial sweep at each scale point (not the fixed 160K-tuned config) -- e.g. 2-3
expansion-factor settings per scale point. This is the one test where a genuinely sharp
(Donoho-Tanner-class) failure is plausible, and a fixed-config test would misattribute a
retunable-parameter failure to "GSBC doesn't scale."

## Cheap decisive test

Test 0 above (near-duplicate density measurement in the real 970K production KB) is the single
cheapest, most decisive next action: it is CPU-only, requires no new training, and directly
adjudicates which of this drill's two named risks (structured discrete-channel collision vs.
generic continuous-channel decline) actually dominates in the REAL production KB rather than a
generic literature-derived prior.

## Falsifiable predictions

**HARD-PASS (discrete channel, plain SBC or GSBC):** keyed@J5 >= 0.90 AND shuffled-key <= 0.10 at
970K, for BOTH code families.
**HARD-FAIL (discrete channel):** either drops below its floor; this drill predicts this is
UNLIKELY (P below) and, if it happens, predicts it correlates with Test 0's near-duplicate density
measurement rather than appearing as a generic capacity collapse.

**HARD-PASS (continuous channel, plain SBC):** extrapolated 970K `ret_agree10` >= 0.30 -- this
drill predicts this will NOT happen (P below).
**HARD-FAIL (continuous channel, plain SBC):** extrapolated 970K `ret_agree10` < 0.10 (unusable) --
this drill's base-case expectation, though the fitted slope from Test 1's ladder is needed to
confirm whether the true floor lands in [0.10, 0.30) (still-failing-but-not-unusable) or below
0.10.

**HARD-PASS (continuous channel, GSBC, density-dial retuned):** extrapolated 970K `ret_agree10` >=
0.30 AND dense spearman >= 0.82 -- this drill's cautiously-optimistic case, contingent on the
density dial actually being retuned for 970K (Test 3).
**HARD-FAIL (continuous channel, GSBC, FIXED 160K-tuned config):** a sharp (non-graceful) drop
between two adjacent scale points on Test 1's ladder -- this drill's specific prediction for WHERE
a genuine cliff is most likely to appear in this system, if one appears at all.

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):**
- P(plain-SBC `ret_agree10` HARD-PASSes at 970K): undeflated ~0.08 (already failing at 18% of
  scale, no improving mechanism identified) -> P_deflated ~0.05 (floor; deflation direction here
  makes the estimate MORE pessimistic, consistent with "don't smoke a result that's already
  failing").
- P(discrete channel HARD-PASSes at 970K, both families): undeflated ~0.80-0.85 (solid
  combinatorial-margin argument, textbook-verified birthday scaling) -> P_deflated ~0.60-0.65
  (deflated for the unmeasured real-world near-duplicate rate in `entities.jsonl`, the genuinely
  open empirical unknown).
- P(GSBC, density-dial-retuned, HARD-PASSes at 970K): undeflated ~0.45-0.55 (based on the
  already-measured 1.5-3x gain at 177,899, a real effect, extrapolated with uncertainty) ->
  P_deflated ~0.30-0.35, capped at the novel-synthesis 0.50 ceiling per the mandatory penalty (no
  direct scale-ladder precedent yet exists in this lineage for GSBC specifically).

## Cross-thread synthesis

Composes three prior threads without re-deriving them: (1) the ingest-scoping note's Item 1 gap
(177,899 vs 970,069, CRLB not re-derived for 970K) -- this drill sharpens that into two SEPARATE
forecasts (discrete: likely holds; continuous: likely fails further) rather than one generic
"capacity cliff" worry; (2) the self-margin taxonomy's family classification (order-statistic vs
collision-count) -- this is a direct, on-the-nose application of that taxonomy to a NEW capability
(encoder retrieval) the taxonomy was not originally built on, and it classifies cleanly into the
two existing families without needing a 4th mechanism (unlike the resonator's basin-proliferation
held-out failure) -- a positive data point for the taxonomy's generality, though still only one
new capability tested against it, not a re-certification; (3) the GSBC lineage's own "next: density
dial" flag -- this drill independently arrives at the same recommendation (retune, don't reuse
fixed config) via the Donoho-Tanner phase-transition literature, giving that flag an external
theoretical grounding it didn't have before.

## Substrate-product implications

For Director: this reframes "will the >=400K scale-test pass" from a single binary uncertainty
into two separable, differently-confident forecasts. The discrete/algebra channel is very likely
fine (P_deflated ~0.60-0.65 HARD-PASS) and does not need heavy scale-test investment -- a light
confirmatory check suffices. The continuous/retrieval channel on plain SBC is very likely to fail
further (P_deflated ~0.05 HARD-PASS) -- the scale-test's main value there is measuring the DECLINE
RATE for planning, not adjudicating genuine uncertainty; Director should not expect the >=400K test
to rescue plain-SBC retrieval. The GSBC lever remains the right production bet (already measured
1.5-3x better at current scale) but its own scale-test MUST include a density-dial retune, not a
fixed-config test, or a genuine cliff risk (the one place this analysis identifies real
sharp-transition precedent) could be misdiagnosed as "GSBC doesn't scale" when the real issue is an
untuned parameter. The single cheapest next action (Test 0, near-duplicate density measurement in
the real `entities.jsonl`) can run before any GPU dispatch and will directly discriminate between
this drill's two named risk mechanisms in the ACTUAL production KB rather than leaving it as a
literature-derived prior.

## Honest bounds -- what's derivable vs what needs the empirical test

**Derivable from theory + on-disk facts (this drill, no new experiment needed):** the two-channel
classification itself; the discrete channel's combinatorial safety margin (solid, textbook);
the qualitative direction of the continuous channel's decline (worse, not better, no cliff from
pure distance-concentration); the identification of GSBC's density-dial as the one place a sharp
transition is plausible (Donoho-Tanner precedent); the fact that plain-SBC `ret_agree10` is
ALREADY failing before any scale growth is applied.

**Genuinely needs the empirical test, not derivable from this drill:** the actual near-duplicate
rate in the 970K production KB (no PR(V)-vs-real-corpus scaling law exists in the literature per
the free-probability sub-agent's honest gap report -- this is a real absence, not a search
failure); the quantitative SLOPE of the continuous channel's decline (qualitative direction is
solid, the exact curve is not); whether GSBC's density-dial retune actually recovers headroom at
970K or merely shifts where its own cliff sits (Donoho-Tanner gives the qualitative shape of a
sharp transition, not this system's specific critical ratio).

## Citations (verified count: 3 parallel Sonnet lit-scan sub-agents dispatched this cycle,
generic math/CS/ML terms only per [[feedback-query-privacy-decomposition]] -- zero substrate-novel
mechanism names sent externally)

Distance-concentration/hubness/ANN-scaling sub-agent (11 sources): Beyer, Goldstein, Ramakrishnan,
Shaft, "When Is Nearest Neighbor Meaningful?" (ICDT 1999); Van Daele et al., "The Curse Revisited"
(PMLR 2022); Radovanovic, Nanopoulos, Ivanovic, "Hubs in Space" (JMLR 11, 2010); Tomasev PhD thesis
2013; scikit-hubness (arXiv:1912.00706); Donoho & Tanner, "Observed Universality of Phase
Transitions..." (arXiv:0906.2530); Aggarwal, Hinneburg, Keim / JMLR 18 "Behavior of Intrinsically
High-Dimensional Spaces"; ANN-Benchmarks (arXiv:1807.05614); "Approximate NN Search on Dynamic
Datasets" (arXiv:2404.19284); "Filtered ANN Search" (arXiv:2509.07789); entity-resolution/blocking
survey (ACM CSUR 53:2, 2020) + "(Almost) All of Entity Resolution" (arXiv:2008.04443).

Marchenko-Pastur/free-probability/compressed-sensing sub-agent (13 sources): Chen & Pan,
"Convergence of the largest eigenvalue..." (Bernoulli 18(4), 2012, arXiv:1211.5479); Cai, Zhang,
Zhou, "Optimal rates... covariance matrix estimation" (arXiv:1010.3866); "Local Marchenko-Pastur
Law at the Hard Edge" (arXiv:1206.1730); Killingback et al., "Scaling Laws for Embedding Dimension
in Information Retrieval" (arXiv:2602.05062, 2026); Heaps'-law/Zipf sublinear-growth literature
(arXiv:1412.4577); Donoho & Tanner phase-transition framework (arXiv:1004.1218 and Donoho's noise-
sensitivity paper); NOODL dictionary-learning phase transition (arXiv:1902.11261); Hopfield-capacity
phase transition (arXiv:1009.1286); Dasgupta, Stevens, Navlakha, "A neural algorithm for a
fundamental computing problem" (Science 358(6364), 2017); Ryali et al., "Bio-Inspired Hashing"
(ICML 2020, arXiv:2001.04907); Sharma & Navlakha (arXiv:1812.01844).

Birthday-paradox/collision-entropy/entity-dedup sub-agent (9 sources): birthday-problem standard
asymptotics; "A Non-Uniform Birthday Problem with Applications to Discrete Logarithms" (IACR
ePrint 2010/616); collision-entropy/Renyi-2 literature (arXiv:1202.5921); Chung & Vadhan, "Tight
Bounds for Hashing Block Sources" (arXiv:0806.1948); non-uniform coupon-collector literature
(arXiv:1510.09045); Shenoy, Ilievski, Garijo, Schwabe, Szekely, "A Study of the Quality of
Wikidata" (arXiv:2107.00156, 2021); Freebase-to-Wikidata migration entity-count facts (contextual,
via the Wikidata-quality study).

**Verified count: 33 distinct external sources found via live web search across 3 sub-agents; zero
fabricated citations (each sub-agent flagged its own honest gaps -- notably, no direct PR(V)-vs-
corpus-size scaling law and no Wikidata-specific near-duplicate-rate-vs-scale study were found,
reported as genuine literature absences, not search failures).** Calibration penalty applied per
role contract throughout (see per-claim P_deflated values in Item 5).
