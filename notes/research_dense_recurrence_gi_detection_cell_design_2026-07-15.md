# Research drill: dense-recurrence GI-detection escalation — dataset verification + ready-to-build cell design

Date: 2026-07-15. Dispatch: research (opus synthesis) + 4 parallel Sonnet lit-scan sub-agents (pair-input evaluation
methodology / degree-corrected nulls; GI-network hub biology; Horlbeck GSE116198 schema+access verification;
brain-grounding on dense-recurrence-vs-sparse-exposure). Research-only — no code, no compute, no cell dispatched.
Director's call on the detection verdict and next dispatch.

## HEADLINE

**The tension is resolvable, and the resolution is a well-known, named problem class, not a novel design.** The
STRUCTURAL_UNDERPOWER diagnosis (curated near-zero-singles paralog pocket, avg degree ~1.0 → held-out-from-identity
is structurally impossible) is correct and generalizes beyond this program: it is exactly what Park & Marcotte (2012,
*Nat Methods*, PMC3531800) formalized as the **C3 test-pair problem** (neither entity recurs) in pair-input
prediction, and what Pahikkala et al. (2015, *Brief Bioinform*) formalized as the **S4 setting** in drug-target
prediction — both papers exist specifically because this failure mode is common and previously under-recognized
across biology. The escalation target — **Horlbeck et al. 2018 (Cell, GEO GSE116198)** — is **CONFIRMED
ingest-ready and genuinely dense**: 472 genes × 472 genes, 222,784 ordered / ~111,628 unordered pairs, i.e. every
gene recurs in ~471 training-eligible pairs. This is the **C1/S1 setting** (both entities recur; only the specific
pairing is novel) — the correct, well-precedented regime for testing whether gene-identity codes carry pair-specific
relational structure. GI score is a quadratic-fit residual (observed − expected from single-phenotype quadratic fit),
i.e. main effects are stripped by construction, same property the earlier Costanzo fair-test refute needed and
lacked.

**But the literature also supplies the sharpest possible warning about what will make this hard**: genetic-interaction
networks in this exact data class are **known hub-dominated** (essential genes carry ~5x the interaction degree of
nonessential genes; GI-degree itself is a systematically predictable, partner-independent gene property — Costanzo
2016; "Conserved rules govern genetic interaction degree across species," PMC3491379), and a pure degree-preserving
baseline (XSwap edge-permutation prior, Zietz et al. 2024 *GigaScience*) achieved **AUROC ≥0.95 on 17/20 edge types**
in a comparable biological network (Hetionet) — i.e., a naive frequency/hub baseline is a real, not hypothetical,
near-saturating confound in exactly this data regime. The escalation cell's entire discriminating value rests on
whether SYM clears **both** ADDITIVE and this DEGREE floor, not just chance.

## Dataset verification (Horlbeck et al. 2018, GEO GSE116198)

- **GEO record directly fetched.** Supplementary files, all plain-text gzip (no binary/xlsx risk): `GSE116198_GImap_sgRNA_sequences_barcodes.txt.gz` (35.6 KB), `GSE116198_sgRNA_pair_phenotypes.txt.gz` (106.9 MB — the phenotype/GI-bearing file, per-sgRNA-pair single + double phenotypes), `GSE116198_sgRNA_pair_read_counts.txt.gz` (45.7 MB raw counts). Raw reads also on SRA (SRP151988).
- **Scale confirmed with correction**: 472×472 = 222,784 ordered gene-pair perturbations (matches abstract); ~111,628 unique unordered pairs (472·471/2 ≈ 111,156, consistent). Every gene recurs in ~471 pairs — a genuinely dense all-by-all design, the opposite of the exhausted paralog pocket's degree ~1.0.
- **GI-score construction, moderately confirmed** (search-summary of methodology; Cell.com direct fetch blocked 403; GitHub `mhorlbeck/GImap_tools` repo confirmed to exist with `GImap_analysis.py`, formula not read line-by-line — flag as recalled-not-line-verified): expected double-phenotype from a **quadratic fit** of the two single-gene phenotypes (Costanzo-lineage extension of the multiplicative/log-additive null); GI score = observed − expected. This strips main effects by construction, same as the task's premise.
- **Processed gene-level tables**: the earlier scout drill (`notes/research_dataset_scout_high_snr_conjunction_module1_replacement_2026-07-15.md`) already located Tables S1-S7 (Mendeley `10.17632/rdzk59n6j4.1`) — use these for the final gene×gene GI matrix directly rather than re-deriving from raw sgRNA-pair counts; this avoids re-implementing the quadratic-fit step and any risk of introducing a different null than the paper's own.
- **Two cell lines available (K562 primary, Jurkat secondary)** with reported replicate correlation R=0.75 (K562) / R=0.44 (Jurkat) — Jurkat is noisier. This supplies a genuine cross-study/cross-line generalization check (train on K562 calls, evaluate ranking on independent Jurkat calls) as a secondary, harder robustness arm — directly following the leakage-avoidance recommendation in `notes/research_sparse_detection_vs_regression_conjunction_reframe_2026-07-15.md` ("held-out evaluation should ideally be cross-study where possible").
- **Alternative denser candidates checked and ruled inferior for this purpose**: Costanzo 2016 yeast SGA is also dense (thousands of partners/gene for well-covered genes) but its readily-downloadable matrix form (thecellmap.org) is a **profile-similarity (Pearson correlation) matrix**, not the raw pairwise GI-score matrix — the raw GI scores ship as long-format pair lists, less turnkey. SLKB pools 11 CDKO screens including Horlbeck but its native table (16,059 SL + 264,424 non-SL) is smaller/sparser than raw Horlbeck, not denser. Kuzmin 2018 trigenic data is structured around triples, not a dense pairwise subset. **Verdict: Horlbeck GSE116198 remains the best-verified dense-recurrence target**; Costanzo-matrix is a viable secondary/cross-species replication candidate for a later scale-up, not a replacement.

## Split design (the load-bearing methodological fix)

**Use the C1/S1 setting explicitly, and report it as its own class — do not rely on a random split to land there
by accident.** Park & Marcotte's headline warning is exactly the failure mode to avoid: naive random splitting on
pair data causes the C1 class to dominate test sets in a way that's disconnected from the true C1/C2/C3 population
mix and can silently overstate generalization if C1 pairs are trivially memorizable via a shared feature (here:
overall gene hubbiness). Concretely:

1. **Definition of the held-out set**: for the full Horlbeck 472-gene matrix, randomly mask a fraction (recommend
   15-20%) of the ~111,628 unordered cells as TEST, subject to a **minimum-training-degree floor per gene**: every
   gene must retain **>=K training pairs** after masking (K=50-100 is a reasonable start — leaves each gene with
   >10% of its ~471 partners even at K=50). This is precisely Pahikkala's **S1 setting** (leave-**pair**-out on a
   fully "warm" matrix, not leave-row/column-out) and is the standard construction in matrix-completion /
   recommender-systems literature for exactly this "recurring-entity, novel-pair" regime.
2. **Leakage discipline (Kriegeskorte "double dipping," PMC2841687)**: the near-zero-singles-style precondition
   filtering that broke the earlier attempts is not needed here (GI score is already residualized), but two leakage
   traps remain and must be avoided: (a) the gold-standard hit/no-hit label threshold (e.g. a z-score or percentile
   cut on |GI|) must be FIXED before looking at the test split — pick the paper's own significance convention if one
   exists, else pre-register a percentile (e.g. top 5-10% |GI| magnitude) BEFORE partitioning, never tuned post hoc;
   (b) model INPUT features must be constituent-only (gene identity / gene embedding derived from OTHER training
   pairs only) — never any quantity derived from the held-out cell's own GI score, single-phenotypes, or read counts.
3. **Report performance separately by pair class** (Park & Marcotte's core prescription) even though this design
   deliberately targets C1 — a sanity table showing C1 (this cell's target) vs. an incidentally-available C2 slice
   (if any gene is more aggressively masked than the K floor allows) makes the split's integrity auditable rather
   than assumed.
4. **Secondary, harder arm**: K562-trained model, evaluated by ranking Jurkat-called GI pairs (cross-cell-line
   generalization) — accepting the known R=0.44 Jurkat replicate-noise ceiling as a quantified, not unknown, cost.

## Arms

1. **SYM (bind)**: the project's compositional bind of gene-A code and gene-B code, decoded/scored against the GI
   target — the architecture under test.
2. **ADDITIVE**: gene-A and gene-B each get an independently-fit scalar/vector "propensity" (row + column fixed
   effects / two-way main-effects regression — the classic additive/bilinear-without-interaction baseline), summed.
   This is the natural null given the earlier Costanzo fair-test refute found real interactions additive-capturable
   at bulk scale — the direct question here is whether that finding also holds inside a residual-by-construction
   target, or whether Horlbeck's design (which already removed the additive component once, at the raw-fitness
   level) leaves genuinely non-additive structure in what remains.
3. **DEGREE/FREQ floor**: an XSwap-style degree-preserving baseline (Zietz et al. 2024) — score each held-out pair
   by a function of each gene's OWN average |GI| magnitude across its training partners (its measured "hub-ness" /
   interaction-propensity), with **zero pair-specific information**. Given the field-precedent AUROC ≥0.95 result on
   a comparable biological network, this baseline should be assumed strong going in, not a token control — it is the
   arm most likely to eat into any apparent SYM lift.
4. **MEMORIZE**: pure train-pair lookup / nearest-neighbor memorization — expected to overfit and collapse toward
   chance on the held-out C1 split; validates the split genuinely forces generalization rather than table-lookup.
5. **CHANCE**: random ranking baseline; AUPRC should approximate the positive base rate (per the field-standard
   caution in `research_sparse_detection_vs_regression_conjunction_reframe_2026-07-15.md` that chance-level AUPRC
   tracks base rate, not 0.5).

## Readout

**Detection/ranking, not continuous regression** — directly inherited from, and consistent with, the sibling drill
`notes/research_sparse_detection_vs_regression_conjunction_reframe_2026-07-15.md`, which already established (a)
GI-magnitude distributions are zero-inflated/heavy-tailed in exactly this data class and (b) the field's own standard
evaluation for GI-scoring methods is AUPRC/AUROC/enrichment-factor against a fixed gold-standard hit list (the same
Benchmarking-GI-Scores paper that scouted the paralog compendium reports exactly this). Metrics: **AUPRC (primary),
precision@k (k = 1%, 5%, 10% of held-out pairs), enrichment factor vs. random**, all against a FIXED pre-registered
|GI| threshold or percentile cut, computed separately per arm and per pair-class (C1 primary, cross-line secondary).
This design is explicitly NOT vacuous (unlike a magnitude-margin test against the GI residual itself, which the task
correctly flags as vacuous by construction) because detection from bare gene IDENTITY on a held-out PAIR requires the
model to have learned something about each gene's role from its OTHER training pairs — that is a genuine
generalization test, not a tautology.

## Falsifiable predictions

**HARD-PASS**: on the held-out C1 split (recurring genes, >=K training pairs each, novel pairing), SYM's AUPRC beats
**both** ADDITIVE and DEGREE/FREQ floor by a relative margin **>=25-30%** (module registry's standard margin,
consistent with the sparse-detection drill's own bar), AND clears **>=2x the positive base rate** in absolute AUPRC,
AND MEMORIZE collapses toward chance on the same held-out split (confirming the split isn't leaking memorizable
structure). This would mean gene-pair identity carries genuine pair-specific (not merely additive-propensity or
hub-degree) relational information recoverable even after the paper's own quadratic-fit residualization — a real,
usable conjunction-module target, and the first real-data case in this program's history where SYM's proven synthetic
capability transfers to a residual-already-stripped, dense, real biological measurement.

**HARD-FAIL (additive-capturable again)**: SYM's AUPRC is statistically indistinguishable from ADDITIVE (within the
run's own noise band) even though both clear DEGREE and CHANCE — meaning the GI residual's held-out-predictable
component is itself decomposable into independent per-gene propensity terms, i.e. the Hill-Goddard-Visscher-class
finding from the prior negative-drill (`drill_negative_why_real_interactions_additive_capturable_where_genuine_2026-07-15.md`)
recurs even inside a construction that already stripped one layer of additivity. This would be a strong, clean,
second-domain confirmation that the additive escape hatch is not just a population-genetics allele-frequency artifact
but a more general property of what's learnable from bare entity identity in these networks.

**HARD-FAIL (degree-dominated)**: SYM's AUPRC is statistically indistinguishable from the DEGREE/FREQ floor — meaning
no pair-specific (relational) structure is recoverable from gene identity at all beyond each gene's own measured
hub-ness; everything generalizable is single-gene "how interactive is this gene overall," never "how do THESE TWO
specific genes interact." Given the Zietz et al. AUROC≥0.95 precedent in a structurally similar network, this is a
real, not token, failure mode to pre-register against — if it lands, the honest reading is that Horlbeck's residual
STILL correlates strongly with gene-level pleiotropy/hub status (a known, literature-documented property, PMC3491379)
and the module-co-membership "beyond-degree" signal that Costanzo's hierarchical-modularity work documents as real
in principle is not recoverable from bare gene-ID + this feature set alone — would motivate escalating to richer
constituent features (protein-complex membership, pathway annotation) rather than gene-identity codes alone, exactly
the same scoping conclusion the sibling detection-reframe drill pre-registered for its own HARD-FAIL case.

**MIDDLE_BAND (most likely outcome by this drill's own calibration)**: SYM beats DEGREE meaningfully but only ties or
marginally beats ADDITIVE — partial pair-specific structure exists but is small relative to the additive/hub
components, consistent with the "genuine interaction is a real minority, not absent" framing of the prior negative
drill. This would still be informative (confirms a non-trivial beyond-degree residual exists) but would not clear the
25-30% margin bar and should be reported honestly as MIDDLE, not rounded up to PASS.

## Brain-grounding

**Dense recurrence sharpens relational profiles; it is not an absolute biological wall at degree ~1, but IS a real
statistical-estimation wall for any system (biological or computational) that must fit a per-entity free parameter.**
Four convergent lit-scan findings, with an important honest complication:

- **Rich-club/hub connectivity** (van den Heuvel & Sporns) confirms integrative/associative brain processing is
  architecturally hub-dependent at the network level — but this is about which regions integrate, not about how many
  times an individual entity must be observed; only loosely transferable, flagged as such.
- **Word-frequency effects on distributional-semantic quality** are strong and well-documented (rare words get
  systematically poorer word2vec/GloVe vectors; this is a NAMED, actively-mitigated problem — Cambridge Rare Word
  benchmark, fastText subword workarounds). This is the closest computational analog to the Horlbeck-vs-paralog-pocket
  contrast: an entity's embedding quality is bottlenecked by its co-occurrence count, directly supporting "more
  recurrence -> sharper profile."
- **Concept-learning literature cuts the other way on the "hard floor" framing**: Tenenbaum-style rational
  generalization shows informative one-shot inference is real (contingent on strong structured priors, not on brute
  co-occurrence count), and fast-mapping/N400 evidence shows single-exposure word learning produces real, if sparse,
  memory traces — directly against a claim that degree-1 entities carry literally zero relational signal in
  biological systems.
- **Honest synthesis**: the STRUCTURAL_UNDERPOWER diagnosis is correct as an **estimation-statistics** claim (you
  cannot fit a free per-entity relational parameter from a single training observation of that entity, held out or
  not — this is true regardless of whether biology "could" extract something from one exposure via strong priors,
  because the test harness here has no such prior to fall back on) but should not be over-claimed as a universal
  biological law of a hard floor at degree 1. Horlbeck's ~471-partner recurrence sits far up the gradient where this
  estimation problem is comfortably solved; the exhausted paralog pocket's degree ~1.0 sits at the genuinely
  unresolvable end of that same gradient — both readings are consistent, and the escalation is justified on
  estimation-statistics grounds independent of how strongly one wants to lean on the brain analogy.

## Cheap decisive test

Before building the full cell: a **single cheap pre-check** — compute the DEGREE/FREQ-floor arm's AUPRC alone,
first, on the C1 split (no SYM/ADDITIVE training needed yet, just each gene's own training-partner-average |GI| as
the score). If this alone already clears the same >=2x-base-rate bar with a large margin (as the Zietz precedent
suggests is plausible), that immediately calibrates how hard SYM's bar really is before investing in the full
4-arm build — cheaper than discovering it after SYM/ADDITIVE are both fully trained.

## Cross-thread synthesis

This drill directly resolves the tension named in the task by recognizing it as a **known, named methodological
problem** (Park & Marcotte C1/C2/C3; Pahikkala S1-S4) rather than a program-specific dead end — the near-zero-singles
paralog pocket is a real-world instance of the C3/S4 regime (structurally unsolvable), and Horlbeck is a real-world
instance of the C1/S1 regime (solvable, standard, well-precedented). It inherits and extends three same-day notes:
the dataset scout (`research_dataset_scout_high_snr_conjunction_module1_replacement_2026-07-15.md`) had already
flagged Horlbeck as rank-3 on SNR grounds (weaker/cell-line-dependent replicate correlation) but for a DIFFERENT
purpose (SNR-optimal AND-gate pair mining); here Horlbeck is not competing on SNR, it is the uniquely dense-recurrence
option, a different axis entirely, and the two rankings do not conflict. It directly reuses the sparse
detection-vs-regression reframe (`research_sparse_detection_vs_regression_conjunction_reframe_2026-07-15.md`) for
the readout methodology (AUPRC/hurdle-style, not continuous MAE) and its leakage-avoidance design (cross-study split
recommendation, now concretely instantiated as K562-train/Jurkat-eval). It extends the reachability-audit drill's
(`research_reachability_audit_arena_selection_vs_fundamental_null_2026-07-15.md`) core lesson — that a
degree/frequency baseline can be a large, hard-to-beat confound in relational-prediction tasks (there: CoDEx
relation-frequency baseline matching embeddings on ~40% of FB15k-237; here: Zietz et al. XSwap degree baseline at
AUROC>=0.95 on Hetionet) — into a concrete, pre-registered DEGREE-floor arm for this cell, rather than treating it as
an afterthought control.

## Substrate-product implications

If HARD-PASS lands, this would be the program's first real-biological-data confirmation that the conjunction/bind
mechanism adds value beyond both additive gene-propensity AND raw hub-degree — directly de-risking the PIVOT's
foundation-sourcing plan (ingest real measured non-additivity, not LLM-generated) by showing the target architecture
actually learns something a cheap baseline cannot, on a real, large (222,784-pair), already-quadratic-residualized
dataset, with no further curation risk (unlike the exhausted near-zero-singles pocket). If MIDDLE_BAND or HARD-FAIL,
the scoping value is still real and cheap: it would pin down, with a second independent real-data domain, whether
"genuine pairwise structure recoverable from bare entity identity, beyond additive and degree" is a narrow or
essentially absent regime in real biological interaction data — informing whether the PIVOT's conjunction-module
content-sourcing strategy needs richer per-gene features (complex/pathway membership) rather than identity-only
codes, a scoping question with the same actionable clarity as the sibling detection-reframe drill's own HARD-FAIL
branch.

## P_deflated

Raw confidence that SYM clears BOTH the ADDITIVE and DEGREE floors with the full 25-30% margin (HARD-PASS): ~0.40-0.45.
This reflects genuine, literature-grounded optimism (Costanzo's hierarchical-modularity work documents real
beyond-degree functional-module structure in GI networks, giving SYM something real to potentially recover) balanced
against a specific, well-evidenced, and severe headwind (Zietz et al.'s AUROC>=0.95 degree-baseline precedent in a
comparable biological network, plus this program's own repeated finding that real interaction signal tends to be
additive-decomposable at scale). Applying the mandatory lit-scan calibration penalty (deflate 0.15-0.25 for
cross-domain literature synthesis not yet tested against this program's own held-out real data) and the
novel-synthesis P cap of 0.50:

**P_deflated = 0.28**

The single largest residual uncertainty is the DEGREE floor's strength: if it lands near the Hetionet precedent
(AUROC>=0.95), the bar SYM must clear becomes very steep and MIDDLE_BAND or HARD-FAIL (degree-dominated) becomes the
modal expected outcome rather than HARD-PASS — this is why the "cheap decisive test" above (compute the degree floor
alone, first) is recommended as the actual first build step, not the full 4-arm cell.

## Citations (verified count: 9 directly fetched/confirmed this session; several more search-confirmed but not fetched, flagged individually above)

Directly fetched/confirmed: (1) Park & Marcotte 2012, *Nat Methods* 9:1134 ("Flaws in evaluation schemes for
pair-input computational predictions"), PMC3531800 — C1/C2/C3 taxonomy, random-split inflation finding; (2) Pahikkala
et al. 2015, *Brief Bioinform* 16(2):325 (DOI 10.1093/bib/bbu010) — S1-S4 settings, nested-CV recommendation; (3)
Kriegeskorte, Simmons, Bellgowan, Baker 2009, *Nat Neurosci* 12:535 ("Circular analysis... double dipping"),
PMC2841687; (4) Zietz, Himmelstein, Kloster et al. 2024, *GigaScience* 13:giae001 — XSwap degree-preserving null,
Hetionet AUROC results; (5) GEO GSE116198 record (supplementary file listing, sizes, formats); (6) Horlbeck et al.
2018, *Cell* (abstract/scale figures via search, direct fetch 403-blocked); (7) `github.com/mhorlbeck/GImap_tools`
repo (README confirmed, formula not line-verified); (8) Costanzo et al. 2016, *Science* 353:aaf1420 (scale, hub
degree ratio, hierarchical modularity — PubMed abstract + TheCellMap.org supplement); (9) "Conserved rules govern
genetic interaction degree across species," PMC3491379.

Search-confirmed, not independently fetched full-text this session (moderate confidence): SLKB (slkb.osubmi.org,
NAR 2024 D1418) native-table scale; Kuzmin et al. 2018, *Science* 360:eaao1729 trigenic-map scale; FredHutch/gimap
CRAN/JOSS package; "Prediction of Genetic Interactions Using Machine Learning and Network Properties," PMC4620407;
CoDEx relation-frequency-baseline figure (carried forward from the same-day reachability-audit drill, itself
independently verified in that session); Cambridge Rare Word benchmark / fastText subword-mitigation literature;
Tenenbaum rational-generalization / fast-mapping N400 literature; van den Heuvel & Sporns rich-club connectome
literature.

Calibration note: this is a dataset-verification-plus-cell-design drill combining (a) directly-verified dataset
access/schema facts (high confidence), (b) a well-precedented methodological fix borrowed from an established
literature (Park & Marcotte / Pahikkala — high confidence the terminology and design are correctly applied), and (c)
an untested empirical prediction about how this specific cell will perform on this specific data (the P_deflated
figure above, appropriately capped and deflated per [[feedback-lit-scan-calibration-penalty]]). Per
[[feedback-dont-dismiss-adjacent-methods]], the DEGREE floor was not treated as a token control but elevated to a
first-class, pre-registered arm precisely because the literature shows it is frequently the dominant explanatory
factor in this data class — dismissing it would have repeated the same premature-dismissal failure mode this
program has already been warned about.
