# Research: scoping the REAL-DATA capability test for the full 4-signal ingest gate

**Filed by:** research (director synthesis over 2 parallel Sonnet lit-scans + full re-read of 4 same-day prior notes)
**Date:** 2026-07-16
**Trigger:** direct follow-on to `notes/research_multisource_arena_real_corpora_landscape_2026-07-16.md`. That note
mapped real corpora for the CORROBORATION axis only (Weather/Book/Restaurant truth-discovery hub). The open question
this drill scopes: does the brain-faithful 4-signal ingest-gate buy a CAPABILITY EDGE on REAL data, or are we mostly
accumulating synthetic construction-proofs? Answering that needs a real multi-source claim stream where ALL FOUR
signals (surprise/unexpectedness, schema-fit, recurrence, importance) are computable AND there is ground truth —
scoping only, no code, no cell.
**Scope discipline:** design/scoping only. Both external lit-scans used generic public-literature search terms
(collaborative knowledge graph vandalism detection, degree-weighted path count permutation null, drug repurposing
gold standard) — no substrate-mechanism names sent off-platform.

---

## HEADLINE

**A single real corpus already carries all four signals natively, at scale, with labeled ground truth, and — uniquely
among everything surveyed so far — a PUBLISHED, QUANTIFIED degree-bias exploit and its debiased fix: Wikidata's
edit-history/vandalism-detection literature (WDVC/WDVD corpus + WWW'19 debiasing paper) paired with Wikidata's own
constraint-violation study.** Recurrence is a literal per-statement field (reference count, rank qualifier); schema-fit
has a literal ground-truth cross-check (mandatory-type/constraint-violation reports, empirically tied to 76.5M
removed statements); surprise is computable by training a link-prediction model on a graph snapshot and scoring
held-out edits by rank; importance is literal (out/in-degree, sitelinks); ground truth is the WDVC reverted-vandalism
label (198,147 positive out of 82.68M revisions) or the constraint-violation-vs-removal dataset. The content-wall risk
is not hypothetical here — it is ALREADY MEASURED: a naive frequency/registration proxy alone gives a **310.7x**
vandalism-rate bias ratio (Heindorf et al., WWW 2019), and their own debiased model only gets that down to **11.9x**
while holding near-identical AUC — meaning even the field's own best fix does not fully kill the degree confound.
A second corpus family (Hetionet/Rephetio/XSwap + repoDB) supplies the field's most rigorous PUBLISHED
degree-normalization methodology (permutation-null DWPC) and the single cleanest evidence in either scan that
structure can beat degree specifically OUT-OF-SAMPLE (degree-only baseline collapses from 97.9% in-sample to 54.1%
on external validation; full structural model holds 85.5%) — this is the fairness-control template the gate's own
test must replicate, not just cite.

## Part 1 — Ranked real-corpus candidates

### Candidate 1 (TOP PICK, cheapest to pilot): Wikidata edit history + WDVC/WDVD vandalism corpus + constraint-violation study

- **What it is:** Wikidata publishes full edit-revision history (82.68M manual revisions, Oct 2012-Jun 2016, WDVC
  2015/2016 release) with reverted-vandalism labels (198,147 positive, ~0.24% base rate — realistic extreme
  imbalance, not a toy-balanced arena) used at WSDM Cup 2017. Separately, "A Study of the Quality of Wikidata"
  (arXiv:2107.00156) directly intersects constraint violations with removed statements: 76.5M removed statements
  (26.2M distinct subjects) against a 1.15B-statement snapshot, with 33.04% of a 2.31M removal sample violating
  mandatory type constraints.
- **All four signals present, natively:**
  - *Recurrence*: reference count is a literal per-statement field (68-73% of statements carry >=1 reference,
    RQSS 2024 measurement) plus a preferred/normal/deprecated rank qualifier — real corroboration structure, not
    inferred.
  - *Schema-fit*: literal, independently-scored ground truth exists (mandatory-type-constraint / symmetric-constraint
    violation flags), separate from whatever graph-structural proxy the gate itself computes — lets schema-fit be
    VALIDATED against an external criterion, not just self-referentially defined.
  - *Surprise*: train a link-prediction/embedding model on a held-back graph snapshot (pre-edit state); score each
    incoming edit/statement by 1 - reciprocal_rank(asserted value | model) — directly reuses the existing
    `additive_map.score_all` machinery, just pointed at a different (real, external) graph.
  - *Importance*: out-degree, in-degree, and sitelinks-count are literal fields; PageRank/hub-centrality is
    computable directly on the dump — a genuine downstream-connectivity measure, distinct from recurrence
    (source corroboration) and schema-fit (local structural conformance).
  - *Ground truth*: WDVC reverted-vandalism label, OR the removed-statement/constraint-violation dataset (these are
    two independent, cross-checkable ground-truth sources on the same corpus family).
- **Temporal arrival stream (bonus — solves a gap flagged in the prior corpora note):** WDVC's edit-by-edit history is
  a real, multi-year, timestamped arrival stream — the one arena ingredient the earlier truth-discovery-corpus survey
  found NO real corpus supplied. This closes that gap.
- **Access:** WDVC/WDVD data and feature-extraction code are free (GitHub: `heindorf/cikm16-wdvd-feature-extraction`,
  `heindorf/www19-*`); Wikidata dumps are CC0.
- **Published degree-bias precedent (the content-wall control, already done by someone else):** Heindorf et al.,
  "Debiasing Vandalism Detection Models at Wikidata," WWW 2019 — the `isRegisteredUser` feature (a frequency/degree
  analog: anonymous vs. registered editor) alone gives anonymous edits a 9.00% vandalism rate vs. 0.03% for
  registered — a 310.7x ratio. Their debiased FAIR-S model cuts this to 11.9x while holding ROC 0.963 / PR 0.316
  (vs. undebiased ROC 0.947 / PR 0.458 from the WSDM Cup winner). This is directly reusable: it hands us both the
  naive baseline AND a field-validated debiasing method to benchmark our own gate against.

### Candidate 2 (best degree-normalization + out-of-sample discipline, weaker on native recurrence/temporal): Hetionet/Rephetio + repoDB

- **What it is:** Hetionet (2,250,197 edges/24 types integrated from 29 public source databases) + Rephetio's own
  physician-curated gold standard (755 positive disease-modifying treatments, 29,044 negatives, 2-MD kappa=0.499) OR
  the independent repoDB benchmark (6,677 approved / 4,123 failed drug-indication pairs, from DrugCentral/UMLS +
  AACT/ClinicalTrials.gov failed-trial records — a genuine positive+negative label source, not positives-only).
- **Signal mapping:**
  - *Schema-fit / structural score*: DWPC (Degree-Weighted Path Count, Himmelstein & Baranzini 2015) — metapath-based
    connectivity score with an explicit degree-downweighting exponent (w=0.4, tuned across 9 candidates).
  - *Degree-null baseline, already built*: XSwap / edge-prior (Zietz et al., GigaScience 2024) generates
    degree-preserving permuted-network nulls; DWPC's own permutation-null variant tested 1,206 metapaths, 709
    remained significant after FDR<5% correction — i.e. real structure survives degree-normalization for the
    MAJORITY but not all metapaths, a graded, honestly-reported result (not a clean win or clean kill).
  - *Recurrence*: weaker here — per-edge-type source count exists (which of the 29 databases asserted an edge) but
    no published per-edge-type source-OVERLAP statistic was found; would need direct inspection of the graph files,
    not a paper table (confirmed gap, not a search failure).
  - *Importance*: node degree/hub centrality — but this is the confound itself here, not an independent signal; would
    need explicit permutation-null correction (DWPC's own method) to separate importance-the-signal from
    importance-as-degree-proxy.
  - *Ground truth*: repoDB or Rephetio's own gold standard (two independent, NOT yet cross-validated against each
    other — a confirmed open gap, itself informative: nobody has checked whether label-mining-derived repoDB and
    physician-curated Rephetio agree).
- **The single most decision-relevant number in this whole drill:** on Rephetio, the prior-probability-only
  (effectively a degree/base-rate) baseline scores AUROC=97.9% IN-SAMPLE (near-tying the full structural model's
  97.4%) but COLLAPSES to 54.1% (near chance) on EXTERNAL validation (DrugCentral), while the full DWPC-based
  structural model holds 85.5% out-of-sample. This is a real, published, quantified demonstration that a degree
  baseline can look like it wins in-sample and be worthless out-of-sample — exactly the discipline our own gate's
  real-data test must reproduce (train/test split must be a genuine external or temporal split, not a random
  in-distribution split, or the degree-baseline comparison is meaningless).
- **Gap vs. Candidate 1:** no native temporal arrival stream (static integrated snapshot); recurrence is thinner
  (source-count, not source-count-with-overlap-structure); but the degree-normalization methodology (DWPC/XSwap) and
  the in-sample-vs-out-of-sample degree-collapse result are the single strongest content-wall-control precedent
  found in either scan.

### Candidate 3 (fallback / hybrid, already scoped yesterday): truth-discovery corpora + a disjoint schema

Weather (labeled copying graph) or Book (real, uninstrumented copying) paired with a UMLS/Hetionet structural schema,
per `notes/research_multisource_arena_real_corpora_landscape_2026-07-16.md`. Weaker than Candidates 1/2 for a FULL
4-signal test specifically because schema-fit would be computed against a corpus DISJOINT from the claim stream (an
artificial pairing) rather than natively co-occurring in one real corpus, and there is no real downstream-connectivity
(importance) analog documented for either. Retained as the cheapest possible corroboration-only pilot if Candidates
1/2 prove too heavy to stand up quickly, not as the primary full-4-signal recommendation.

**Ranking:** Candidate 1 (Wikidata WDVC/WDVD + constraint-violations) is the top pick — cheapest to pilot (all data
and baseline feature-extraction code already public and downloadable), the only one with a NATIVE temporal stream,
and the only one with an already-published, already-quantified degree-bias number to benchmark against directly.
Candidate 2 (Hetionet/Rephetio/repoDB) is the essential SECOND corpus — not a replacement, a companion — because it
supplies the out-of-sample/temporal-split discipline and the permutation-null degree-normalization methodology that
Candidate 1's literature does not itself provide (WDVD's debiasing paper corrects a demographic/frequency feature,
not a graph-degree/hub-centrality feature specifically).

## Part 2 — Concrete per-signal definitions on real data (reusing existing signal functions)

| Signal | Existing substrate function | Real-data instantiation (Candidate 1 primary) |
|---|---|---|
| Surprise / unexpectedness | `additive_map.score_all` -> `raw_PE = 1 - reciprocal_rank(true_target)` | Train the same rank-based scorer on a frozen pre-edit Wikidata graph snapshot; score each incoming statement/edit by its reciprocal rank under the trained model. Zero new mechanism — different graph, same function signature. |
| Schema-fit | `hdlab/reachability_audit.py` `build_schema_fit` (today's upgrade: pairwise Resource-Allocation index or SR/PPR resolvent, per `research_schema_fit_derivability_signal_upgrade_2026-07-16.md`) | Compute the SAME pairwise RA/PPR score on the Wikidata adjacency graph, AND separately record the corpus's own literal constraint-violation flag (mandatory-type-constraint pass/fail) as an independent, externally-sourced cross-check — two schema-fit measurements on the same data, one ours, one native to the corpus, letting us validate our proxy against a real independent criterion for the first time in this program. |
| Recurrence | `local_precision(c) = recurrence_count(c) / (recurrence_count(c) + TAU)` (per `research_consolidation_gate_quantitative_signals_2026-07-16.md`) | `recurrence_count(c)` = literal reference count on the statement (Wikidata's own field); TAU calibrated on this corpus specifically (not imported from ACT-R, per the same note's standing caution). |
| Importance (4th signal, not yet built — flagged as an addendum in `research_surprise_decomposition_unexpectedness_vs_importance_2026-07-16.md`) | none yet — new build, near-zero-cost | `importance(entity) = normalized(out_degree + in_degree + sitelinks_count)` or a PageRank/hub-centrality score computed directly on the graph. This is the cheapest of the four to build (pure graph statistic, no model training) and is the one signal this drill newly operationalizes rather than reusing. |

Combination arithmetic to test: reuse the fast_track/slow_track decomposition (`fast_track_score = raw_PE *
schema_fit`, `slow_track_score = raw_PE * (1 - schema_fit)`) from the same-day quantitative note, gated by
`local_precision` (HOLD if below `PRECISION_MIN`), with `importance` entering as a tie-break / prioritization weight
on WHICH held/borderline candidates get reviewed first (a value-of-information role, not a pass/fail gate input) —
consistent with the surprise-decomposition drill's finding that importance/salience is a mechanistically distinct
signal from prediction-error, not a fourth term to multiply in blindly.

## Part 3 — Controlling for the content-wall

**The naive baseline the gate must beat is not hypothetical — it is measured, on real data, in both corpus families:**

- Wikidata/WDVD: registration-status/frequency proxy alone -> 310.7x vandalism-rate bias ratio (9.00% anon vs 0.03%
  registered). The field's OWN best debiasing (FAIR-S) only gets this to 11.9x while holding near-identical AUC —
  i.e. even a serious published fix leaves real residual degree/frequency leakage. Our gate must be benchmarked
  against BOTH the naive 310.7x-biased model AND the FAIR-S-debiased model; beating only the naive one is a weak
  claim given the field's own fix is already available off-the-shelf.
- Hetionet/Rephetio: prior-probability/degree-only baseline hits AUROC=97.9% IN-SAMPLE (looks like it wins) but
  collapses to 54.1% (near chance) on OUT-OF-SAMPLE external validation, while the full structural model holds
  85.5%. XSwap/edge-prior separately shows plain degree alone reaches AUROC>=0.95 on 17/20 Hetionet edge-type
  networks IN-SAMPLE — degree is an extremely strong baseline within-distribution, not a strawman.

**Fairness disciplines the real-data test must adopt (both directly derived from the above, not invented here):**

1. **Report AUPRC, not just AUROC.** The disease-gene DWPC paper shows AUROC drops only ~0.04 (0.83->0.79) under
   degree-permutation while AUPRC drops 3x (0.06->0.02) — AUROC is close to uninformative once degree is this
   strong; AUPRC is where genuine structural signal separates from a degree confound. Any HARD-PASS claim reported
   only in AUROC should be treated as unverified.
2. **Split out-of-sample / temporally, not randomly.** Per the Rephetio 97.9%->54.1% collapse: a random in-distribution
   split lets a degree-only model look like it generalizes when it hasn't. On Wikidata, this means training the
   surprise-model on a graph snapshot strictly BEFORE the test window's edits/labels (a genuine temporal holdout,
   which the WDVC's multi-year timestamped history makes directly possible) — not a random train/test split over
   all revisions pooled together.
3. **Benchmark against the field's SOTA degree-corrected baseline, not just naive degree.** DWPC's permutation-null
   methodology and Heindorf's FAIR-S debiasing are both off-the-shelf, already-published "smart degree-correction"
   baselines. Beating naive degree/frequency alone is a low bar (per this program's recurring pattern of degree/
   freq-explained negatives); the real bar is beating these ALREADY-DEBIASED published baselines.
4. **Ablate each of the 4 signals individually**, per the synthetic arena design's own HARD-FAIL criterion (removing
   any one signal changes decision accuracy by <2% => that signal was redundant) — directly reusable here unchanged.

## Part 4 — Pre-registered can-fail test design

**HARD-PASS (brain-faithful 4-signal gate earns a genuine real-data capability edge):**
- On a genuine temporal/external holdout (not random split), the gate's AUPRC beats the naive degree/frequency
  baseline by a material relative margin AND beats the field's own SOTA degree-corrected baseline (FAIR-S on
  Wikidata, or permutation-null DWPC on Hetionet/Rephetio) — clearing the higher, already-debiased bar, not just the
  naive one.
- The gate's out-of-sample performance degrades LESS than the naive degree-only baseline's in-sample-to-out-of-sample
  gap (mirroring the Rephetio 97.9%->54.1% collapse pattern) — i.e. the schema-conditioned, precision-weighted
  combination genuinely generalizes better, not just scores marginally higher on one fixed split.
- Ablating any single signal (surprise, schema-fit, recurrence, importance) costs >=2% accuracy/AUPRC (all four are
  doing independent work, per the synthetic arena's own HARD-FAIL threshold reused here).
- The specific brain-derived combination arithmetic (schema-fit as a mixing weight on raw_PE, not a flat learned
  blend) beats a learned-logistic combination of the same four raw features by a nontrivial margin — this is the
  discriminating test between "any sensible combination of 4 features helps" and "the SPECIFIC brain-faithful form
  is earning its complexity."

**HARD-FAIL (real corpora don't support a genuine capability claim — another content-wall confirmation):**
- The gate's apparent advantage over naive degree/frequency evaporates or reverses under the temporal/external split
  (same failure signature as Rephetio's degree-only collapse, but happening to OUR gate instead of the baseline —
  meaning our gate was ALSO fitting degree/frequency, not genuine structure).
- AUPRC gain over the field's already-published degree-corrected SOTA baseline (FAIR-S / permutation-null DWPC) is
  null or negative — the gate isn't even beating the existing state of the art, let alone adding brain-faithful
  value on top of it.
- Ablating any one signal changes accuracy by <2% (redundant signal, exact reuse of the synthetic arena's own
  threshold).
- The brain-derived combination form does not beat a learned-logistic blend of the same raw features — the
  "brain-faithful" framing is not earning anything beyond generic multi-feature combination.

**MIDDLE band (realistic modal expectation, consistent with how the analogous Hetionet DWPC result actually landed
— 709/1206 metapaths survived degree-normalization, not all 1206, not zero):** the gate beats naive degree clearly,
beats the SOTA degree-corrected baseline on SOME but not all signal/entity-type strata (e.g. works better on
higher-connectivity entity types where richer path structure exists, weaker on sparse/long-tail entities where the
signals themselves have less to work with) — a real, partial, stratified win rather than a clean HARD-PASS or
HARD-FAIL, which would still be a genuinely informative and actionable result (tells us WHERE the gate adds value,
not just whether it does globally).

## Cheap decisive test

Before any arena-build cell or real-data ingest cell is authored: pull the already-public WDVD feature-extraction
code (`heindorf/cikm16-wdvd-feature-extraction`) and, in a throwaway script (no substrate cell, no GPU/CPU queue),
recompute the naive registration-status bias ratio on a small WDVC sample to confirm the 310.7x number replicates
locally (a cheap sanity check that the published baseline is reproducible before building anything on top of it).
In parallel, pull Hetionet's public data + the XSwap/edge-prior code and recompute the in-sample AUROC>=0.95
degree-only result on 1-2 edge types, confirming the field's own strongest-baseline claim reproduces. Only after both
baselines are confirmed reproducible locally should any new signal-scoring cell (surprise/schema-fit/recurrence/
importance on either corpus) be authored — this order avoids building the harder 4-signal machinery before
confirming the comparison baselines it will be measured against are solid.

## Cross-thread synthesis

- Directly extends `research_multisource_arena_real_corpora_landscape_2026-07-16.md` — that note answered "where
  does real corroboration data come from" (Weather/Book); this note answers the harder question it left open —
  where does a real corpus exist that ALSO supplies schema-fit ground truth, a native temporal stream, and a
  downstream-connectivity/importance signal, all four in ONE corpus, not four disjoint ones stitched together.
- Directly reuses `research_schema_fit_derivability_signal_upgrade_2026-07-16.md`'s pairwise RA/PPR upgrade
  (zero new build) and gives it, for the first time in this program, an INDEPENDENT external ground-truth
  cross-check (Wikidata's own constraint-violation flags) rather than only a self-referential BFS-reachability
  label.
- Directly reuses `research_consolidation_gate_quantitative_signals_2026-07-16.md`'s fast_track/slow_track
  combination arithmetic and recurrence-as-precision form unchanged — this drill supplies the real-data corpus to
  test that arithmetic on, which that note's own cheap decisive test could only test on the existing synthetic/
  internal arena.
- Directly reuses `research_surprise_decomposition_unexpectedness_vs_importance_2026-07-16.md`'s flagged 4th signal
  (downstream-reach/importance, "no external stakes required") — Part 2 above is the first concrete operational
  definition of that signal on real data (degree/PageRank/sitelinks), moving it from "candidate addendum" to
  "buildable now, near-zero cost."
- Sharpens the recurring content-wall risk (named explicitly in the task): this drill found the risk is not just a
  plausible worry, it is ALREADY MEASURED TWICE in the literature (Wikidata's 310.7x bias ratio, Hetionet's
  97.9%->54.1% in-sample/out-of-sample degree collapse) — both directly reusable as the fairness gate our own test
  must clear, not something we need to discover from scratch.

## Substrate-product implications

1. The cheapest, most consequential next move is NOT building the 4-signal gate cell first — it's the two
   reproduction checks in the "cheap decisive test" section (confirm the 310.7x Wikidata bias ratio and the
   Hetionet degree-only AUROC>=0.95 both replicate locally), which validates the comparison baselines before any
   new signal-scoring machinery is built on top of them.
2. Both real corpora are large enough that a full pipeline run is a genuine compute commitment (82.68M revisions;
   2.25M edges) — the pilot should start with a stratified SAMPLE (e.g. a few thousand labeled-vandalism-positive
   revisions + a matched negative sample from WDVC, or the existing 755/29,044-pair Rephetio gold standard directly)
   rather than the full corpus, to keep the first pass cheap and CPU-only.
3. If this real-data test HARD-PASSes even partially (the realistic MIDDLE-band outcome described above), it would
   be the FIRST capability result in this program's recent run that is not synthetic-construction-proof-only — worth
   flagging explicitly to the director/USER as a different category of result than the last several negatives
   (foundation-builder v1-v4, real-data-negatives-as-bulk-artifacts, realdata-unreadable-test-design-mismatch), all
   of which were synthetic-arena or bulk-aggregate findings, not genuine external-corpus, temporally-held-out results.
4. If it HARD-FAILs (gate collapses to degree/frequency under the temporal split, same as the last several
   real-data threads), that is ALSO a valuable, cheap, sharply-localized negative — it would mean the specific
   failure mode is the temporal/external-generalization gap, not "no real interaction data exists" (already refuted
   by the pockets/subset-curation thread) and not "signals collapse in any single-source graph" (already refuted by
   the synthetic multi-source arena design) — narrowing the open question to exactly one remaining axis: does the
   gate's combination arithmetic generalize out-of-distribution, or does it only look good in-sample like every
   naive baseline surveyed here.

## Citations (verified count: ~20 distinct sources across 2 independent parallel lit-scans, several cross-confirmed within a scan)

**Wikidata/vandalism-detection scan:** Heindorf, Potthast, Stein, Engels, "Towards Vandalism Detection in Knowledge
Bases: Corpus Construction and Analysis" (WDVC, SIGIR 2016) and WSDM Cup 2017 overview (arXiv:1712.05956,
wsdm-cup-2017.org); Heindorf, Potthast, Engels, Stein, "Overview of WDVD" (arXiv:1703.03861, 47-feature model,
GitHub `heindorf/cikm16-wdvd-feature-extraction`); Heindorf, Potthast, Stein, Engels, "Debiasing Vandalism Detection
Models at Wikidata," WWW 2019 (ACM DOI 10.1145/3308558.3313507, 310.7x/11.9x bias-ratio numbers, FAIR-S model);
Beghaeiraveri, Gray, McNeill, "RQSS," Semantic Web Journal 2024 (DOI 10.3233/SW-243695, reference-quality scoring);
"A Study of the Quality of Wikidata" (arXiv:2107.00156, 76.5M removed statements / constraint-violation overlap);
Wikidata Help:Ranking and Property:P2241 (rank/deprecation-reason fields); Wikidata:Database reports/Constraint
violations (live page); Ferranti et al., SHACL/SPARQL constraint formalization, Semantic Web Journal 2024.

**Hetionet/degree-normalization scan:** Himmelstein, Baranzini, "Heterogeneous Network Edge Prediction: A Data
Integration Approach to Prioritize Disease-Associated Genes," PLOS Comp Biol 2015 (PMC4497619, DWPC method,
0.83/0.79 AUROC and 0.06/0.02 AUPRC unpermuted-vs-permuted numbers); Himmelstein et al., "Systematic integration of
biomedical knowledge prioritizes drugs for repurposing" (Rephetio), eLife 2017 (DOI 10.7554/eLife.26726, 755/29,044
gold standard, 97.4%/97.9% in-sample and 85.5%/54.1% external-validation AUROC numbers); Zietz et al., "Evaluating
the impact of network architecture-driven false discoveries" (XSwap/edge-prior), GigaScience 2024 (DOI
10.1093/gigascience/giae001, PMC10848215, AUROC>=0.95 on 17/20 networks); Brown & Patel, "repoDB," Scientific Data
2017 (DOI 10.1038/sdata.2017.29, PMC5349249, 6,677/4,123 positive/negative pairs); Bizon et al., ROBOKOP (Nature
Scientific Reports, biolink provenance fields); Chandak & Zitnik, PrimeKG (GitHub `mims-harvard/PrimeKG`); Hetionet
connectivity-search follow-up, PMC10375517.

**Explicit uncertainty flags carried forward from sub-agents:** (1) one sub-agent's initially-extracted
"Graph-Linguistic Fusion" (arXiv:2505.18136) head-to-head AUROC/PR-AUC numbers could NOT be reproduced on a repeat
fetch and are explicitly REJECTED as possibly fabricated by the fetch summarizer — not used anywhere in this note's
claims. (2) No per-edge-type source-overlap statistic (e.g. "% of PPI edges asserted by >=2 sources") was found
published for Hetionet/SPOKE — confirmed gap, would need direct file inspection, not assumed. (3) repoDB and
Rephetio's own gold standard have never been published as cross-validated against each other (confirmed gap,
flagged as a possibly-useful but out-of-scope side check). (4) SPOKE as "the" successor to Hetionet is medium
confidence (plausible, matches known lineage, not independently triple-verified this cycle).

## P_deflated

Corpus-existence/characterization claims (Part 1, that these datasets exist, are downloadable, and the cited
numbers are accurate): well-supported by ~20 citations across 2 independent scans, with the two most load-bearing
numbers (310.7x bias ratio; 97.9%->54.1% degree collapse) each pulled directly from primary-paper text — raw
confidence ~0.75, deflated 0.20 per lit-scan calibration penalty -> **0.55**.

Novel-synthesis claim (that piloting one of these real corpora will reveal a GENUINE brain-faithful capability edge,
specifically, as opposed to another content-wall/degree-explained negative): capped at 0.50 per
[[feedback-lit-scan-calibration-penalty]], and deflated further given this program's recent, repeated pattern of
real-data negatives resolving to degree/frequency/bulk-aggregate artifacts (chem-QSAR, Costanzo epistasis fair-test,
reachability-audit) — **0.30**, reflecting genuine skepticism that this specific real-data test breaks that pattern,
while still being worth running because a HARD-FAIL here would be sharply localizing (narrows the open question to
out-of-distribution generalization specifically, per Substrate-product implication #4) rather than an ambiguous
negative.

**Overall P_deflated = 0.35** (blended, weighted toward the novel-synthesis component since "does the gate show a
genuine edge on real data" is the actual decision-relevant claim, not merely "do suitable real corpora exist" — that
existence question is well-answered at 0.55, but the capability-edge question this drill was commissioned to scope
is the harder, lower-confidence one).

---

*Scoping only. No cell dispatch, no code shipped. Next step if the USER wants to proceed: the cheap decisive test
above (reproduce the two published baselines locally on a small sample of each corpus, no GPU/CPU queue) as the
gating check before any real-data ingest-gate cell is authored.*
