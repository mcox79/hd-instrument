# Research: Dense per-concept multi-bucket KG — prior art, source-depth split, and density-optimum validation

**Date:** 2026-07-14
**Mode:** 3 parallel Sonnet lit-scan sub-agents (prior-art/COMET-Mosaic survey; source-depth full-vs-thin-slice quantification; KG-density-vs-reasoning-performance literature check) + director (Opus) synthesis. Generic public KG-research terms only in every external query — no substrate configs/partition sizes sent off-platform. This drill directly follows and stress-tests `research_ideal_foundation_spec_size_density_optimum_2026-07-14.md` (same day, 11:36) against fresh external evidence rather than re-deriving its architecture.

Field advisor run at cycle start (`research_field_advisor.py`): top candidates are semiconductor/free-probability physics drills, not knowledge-foundation work — this cycle is a director-routed topic dispatch, not an advisor-driven pick, so the advisor output is recorded for cadence-tracking only and not used to steer this drill.

---

## HEADLINE

**(a) Genuinely unbuilt, not a download-and-use gap.** No single resource, and no existing merge (including CSKG, which we already hold a slice of), delivers dense, *balanced* per-concept multi-relation-type coverage. ConceptNet 5.7 has the broadest relation-type *vocabulary* (taxonomic/property/part-whole/functional/causal/spatial all named relations) but is thin and skewed per individual concept (dominated by RelatedTo/Synonym lexical edges, not the characterizing buckets). CSKG inherits that same skew rather than fixing it (top-3 relations = >50% of all 6M edges). BabelNet is 99.98% one untyped "relatedness" bucket. COMET/Dense-ATOMIC prove multi-bucket generation is *possible* but only within the narrow social/event domain, and — the sharpest finding this cycle — **Dense-ATOMIC (ACL 2023, arXiv:2210.07621) exists precisely because full-scale ATOMIC2020 remained sparse per-node even at full published size**, which is direct evidence against "just re-ingest the full source and density solves itself."

**(b) The re-ingest/enrich/acquire split is NOT re-ingest-heavy — it's closer to balanced, with re-ingest as the largest but not dominant lever.** Best available (mostly-estimated, weakly-evidenced) split: ~40-50% closes via re-ingesting fuller existing licensed sources (ConceptNet 5.7 full, CSKG full merge, Wikidata beyond -CS subset), ~15-20% needs KG-completion/link-prediction, ~20-25% needs LLM-assisted generation (COMET-style, strongest lever specifically for causal/social buckets), ~10-15% needs genuinely new sources (numeric/measured attributes — none of the 4 core sources are strong here, consistent with the already-diagnosed "0 numeric attrs" finding). **This build-shape verdict is corrected from a naive "just ingest more" framing**: the Dense-ATOMIC counter-evidence means re-ingest alone is necessary-but-insufficient even for the source it's supposedly "full" for.

**(c) The >=4-5-of-7-bucket density-optimum target is UNVALIDATED, and the one directly relevant paper found found points the opposite direction from what the target assumes.** No paper defines these 7 semantic buckets or tests a count threshold. The single closest hit — arXiv:2508.15291 ("Evaluating Knowledge Graph Complexity via Semantic, Spectral, and Structural Metrics for Link Prediction") — measures "Node-level Maximum Relation Diversity" as an isolated variable across FB15k-237/WN18RR/CoDEx and finds it **inversely correlated** with link-prediction MRR/Hit@1 (raw degree/degree-entropy correlate positively; relation-type diversity does not — diverse relational context fragments the embedding). This is a different question (embedding-based link-prediction difficulty, not downstream reasoning/QA benefit from richer characterization) but it is a genuine, must-not-bury caveat against the density-optimum hypothesis as currently framed, and it directly affects how the earlier same-day spec's Section 1 target should be read: **the bucket-coverage target should be treated as an open, falsifiable hypothesis about OUR specific glass-box VSA readout (where roles are structurally separated by binding, not fused into one dense embedding as in FB15k-237-style TransE/ComplEx models), not an imported, literature-validated design principle.** The mechanism that produces the inverse correlation (embedding ambiguity from fused relational contexts) may or may not transfer to a role-separated bind/unbind readout — that distinction is itself the falsifiable claim and is not yet tested either way.

---

## 1. Prior-art survey (full detail)

| Resource | Scale | Dense multi-bucket per typical concept? | License/usability | Maintained |
|---|---|---|---|---|
| Cyc/OpenCyc/ResearchCyc | Full Cyc ~500K concepts/5M assertions (2012); OpenCyc ~239K terms/2.09M triples | Full Cyc *by design* is deep multi-predicate (hand-axiom'd) but proprietary/undownloadable; public OpenCyc is overwhelmingly taxonomic only | OpenCyc Apache-licensed but discontinued ~2017 | Dead since 2017 |
| Wikidata (full) | 1.65B statements, 122.4M items (wikidata.org/wiki/Wikidata:Statistics) | No — avg 12.5 facts/entity (arXiv:2009.11564), long-tail skewed; many facts are same-type external-IDs, not distinct semantic categories | CC0, full JSON/RDF dumps | Active |
| CSKG (arXiv:2012.11490) | 2.2M nodes, 6M edges, 7-source merge | Weakly — top-3 relations (RelatedTo 1.7M, Synonym 1.2M, Antonym 401K) are >50% of all edges; well-connected in aggregate, not balanced per-node | CC-BY 4.0, public download | Static since 2021 |
| ConceptNet 5.7 | ~34M edges, 42 relation types (arXiv:1612.03975) | Best categorical VOCABULARY spread of any static resource, but per-concept extremely sparse (most concepts: 1-3 edges, RelatedTo-dominated) | CC-BY-SA 4.0, full dumps | Frozen post-2021 |
| ATOMIC / ATOMIC2020 | 877K tuples/9 relations (orig.); 1.33M tuples/23 relations (arXiv:2010.05953) | No — single-domain by construction (social/event), and per Dense-ATOMIC, still sparse per-node even at full scale | Research-only license | Static since 2020 |
| NELL | 120M confidence-weighted beliefs (2018) | No — noisy, category-membership-heavy | Free, CMU | Dormant since ~2018 |
| YAGO4.5 | 49M entities, 109-132M facts (arXiv:2308.11884) | No net gain over Wikidata — consistency cleaning removed ~28% of Wikidata's triples | Free, downloadable | Active (2024 paper) |
| DBpedia | 9.5B triples (2016 peak) | Partial — richer infobox property variety (~26 facts/entity) than Wikidata but long-tailed/inconsistent | CC-BY-SA+GFDL | Active, shrinking relevance |
| BabelNet | 22.9M synsets, 1.9B relations | No — 99.98% of edges are one untyped "relatedness" bucket; typed lexical relations are ~364K, a tiny fraction | Non-commercial license, API-gated | Active |
| COMET/Mosaic (AllenAI) | Neural generation, trained on ATOMIC2020's 23 relations (arXiv:2010.05953) | Conditionally yes — can generate across all 23 relation types per queried concept, closest to "on-demand multi-bucket," but scoped to social/event domain only, generated (noisy) not curated | Open code/weights (research use) | No successor generalizing beyond event/social domain |
| Dense-ATOMIC (ACL 2023, arXiv:2210.07621) | Densifies ATOMIC's existing 9/23-relation set via completion model (Rel-CSKGC) | Improves multi-hop connectivity WITHIN ATOMIC's existing relation set, not cross-category bucket diversity; exists specifically because full ATOMIC2020 remained sparse per-node | — | 2023 |
| "Dimensions of Commonsense Knowledge" (arXiv:2101.04640, Ilievski et al.) | 13-dimension relation-organizing taxonomy | A FRAMEWORK for organizing relations across sources, not a built dense KG | — | 2021 |

**Verdict:** if one resource had to be picked today for direct reuse, ConceptNet 5.7 full is the highest-leverage single re-ingest (broadest already-licensed relation-type vocabulary spanning our 7 buckets); CSKG (what we already partially hold) remains the best available pre-merged base but does not itself solve the balance problem and needs the same corrective re-weighting regardless of ingest depth.

## 2. Source-depth quantification (full source vs our thin slice)

Per-source bucket supply confirmed: ConceptNet (property/functional/causal/part-whole/spatial via HasProperty/UsedFor/Causes/PartOf/AtLocation — social/agentive essentially absent by design), CSKG (inherits ConceptNet's skew, no per-node diversity statistic found in the paper — full-text extraction did not surface one, flagged as a probable-not-confirmed literature gap), Wikidata (taxonomic/property/spatial strongest, ~13-14 statements/item average but Recoin, WWW 2018, shows completeness is highly class-conditioned and most non-flagship items are far below their class peers), ATOMIC2020 (causal + social/agentive by design, its distinguishing contribution vs ConceptNet — but Dense-ATOMIC's own framing admits it stays sparse per-node at full scale).

**Estimated re-ingest/enrich/acquire split** (explicitly flagged: qualitative direction is evidence-anchored, percentages are the sub-agent's own reasoned estimate, not measured):
- Re-ingest more of already-licensed existing sources: **~40-50%**
- KG-completion/link-prediction: **~15-20%** (evidence: helps mid-frequency partial-coverage nodes, does not close true long-tail sparsity per few-shot-KGC literature, arXiv:2301.01172-class surveys)
- LLM-assisted/COMET-style generation: **~20-25%** (best lever specifically for causal/social buckets)
- Genuinely new source needed: **~10-15%** (numeric/measured attributes — none of the 4 core sources are strong here)

## 3. Density-optimum validation (the sharpest finding this cycle)

**Verdict: entirely unvalidated as a specific threshold, and the closest relevant paper points the opposite direction.** arXiv:2508.15291 defines "Node-level Maximum Relation Diversity" (distinct relation predicates touching one entity, raw schema-predicate cardinality, not semantic-category bucketing) across FB15k-237/WN18RR/CoDEx-S/M/L and finds it inversely correlated with MRR/Hit@1 — diverse relational context fragments the embedding and creates ambiguity, while raw degree/degree-entropy correlate positively. No paper anywhere defines the 7 semantic buckets (taxonomic/property/part-whole/functional/causal/spatial/social) used in the same-day sibling note, nor tests any specific bucket-count threshold. CommonsenseQA-adjacent work (arXiv:1811.00937, arXiv:2307.12382, arXiv:2109.09309) shows relation-type variety exists and matters directionally to what gets asked, but no per-concept dosage/threshold study exists. KG quality/completeness surveys (Zaveri et al.-style, 18 dimensions/69 metrics) define completeness structurally with no per-entity relation-type-count heuristic.

**Why the inverse-correlation finding does not automatically refute the density-optimum hypothesis, but must gate it:** arXiv:2508.15291's mechanism is embedding fragmentation in FUSED dense-vector link-prediction models (TransE/ComplEx-class). Our glass-box VSA readout separates role and filler structurally via bind/unbind rather than fusing all relations into one dense embedding per entity — whether that structural separation avoids the fragmentation mechanism, or reproduces it in a different guise (e.g. bundle-crosstalk scaling with number of distinct relation types bound into one entity's superposition), is precisely the open, falsifiable question and is NOT answered by this literature either way.

---

## Cheap decisive test

**Two-part test, reusing the same-day sibling note's Part A/B harness plus a new Part C that directly operationalizes the inverse-correlation caveat:**

- **Part A/B (already specified in `research_ideal_foundation_spec_size_density_optimum_2026-07-14.md` Section 7):** k-core overlap + per-concept bucket-coverage measurement on our own active partition. No change needed — still the first buildable step, zero new data.
- **Part C (new, this drill's addition):** on the SAME active-partition sample used for Part B, measure per-entity relational-inference retrieval quality (existing BFS/retrieval harness, e.g. the Test3 harness referenced in the cold-start note) STRATIFIED by bucket-diversity count (0/1/2/3/4+ buckets populated), holding raw degree roughly constant across strata where possible (bucket-diversity and raw degree are correlated by construction — the strata must control for this, not just report diversity alone, to actually test the arXiv:2508.15291 caveat rather than reproduce the degree confound it explicitly warns about).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**HARD-PASS (density-optimum hypothesis survives the caveat, in our specific glass-box regime):**
1. Part C shows retrieval/relational-inference quality is flat-to-increasing across bucket-diversity strata AFTER controlling for degree — i.e., our bind/unbind readout does NOT reproduce the FB15k-237-style fragmentation penalty.
2. The re-ingest split's largest-single-lever prediction holds: after a small-scale ConceptNet-5.7-full pilot re-ingest on a sampled overlap set, measured bucket-coverage gain from re-ingest alone is >=35% of the total gap (validating the ~40-50% estimate is in the right ballpark, not wildly off).

**HARD-FAIL (informative negatives — do not force the density-optimum story if these occur):**
1. Part C shows retrieval/relational-inference quality DECREASES with bucket-diversity count even after degree-controlling — this would mean the arXiv:2508.15291 fragmentation mechanism DOES transfer to our bind/unbind regime, directly falsifying the same-day sibling note's Section 1 density target as currently framed (a >=4-5-bucket target would then be actively counterproductive, not just unvalidated-but-harmless).
2. The ConceptNet-5.7-full pilot re-ingest gain is <15% of the total gap on the sampled overlap set — would mean re-ingest is a much smaller lever than estimated and the split should re-weight toward completion/generation, changing the recommended build order in the sibling note.

---

## Cross-thread synthesis

- **`research_ideal_foundation_spec_size_density_optimum_2026-07-14.md`** (same day, prior cycle) proposed the CORE+MODULE architecture and the >=4-5-of-7-bucket density target as its own novel synthesis, explicitly flagged (P=0.42, capped) as "a REASONABLE, literature-consistent operationalization but not itself a number pulled from a published paper." This drill's Section 3 finding sharpens that honest flag into a specific, named counter-risk (arXiv:2508.15291's inverse correlation) rather than a generic "untested" caveat — the sibling note's Section 1 target should be read as gated by this drill's Part C test, not as independently validated.
- **`research_cskg_prior_art_novelty_due_diligence_2026-07-10.md`** already established CSKG's entity-resolution/relation-normalization layer as adoptable wholesale. This drill adds: the RELATION-BALANCE problem (top-3 relations >50% of edges) is a separate, unresolved defect in that same resource, not fixed by adopting its merge methodology.
- **`cskg_commonsense_core_kcore_density_gate_2026-07-10.md`** established the k=12-14 dense-band aggregate density numbers this drill's Part A still reuses unchanged.
- This drill's Part C is a genuinely NEW addition to the existing Section 7 test design in the sibling note — the sibling note's own falsifiable predictions did not anticipate the degree-vs-diversity confound; Part C should be treated as required, not optional, before trusting Part B's raw bucket-coverage numbers as a design signal.

## Substrate-product implications

1. **Do not treat CSKG (or any full-scale re-ingest of it) as sufficient on its own** — its relation-balance skew is structural to the resource, not an artifact of our thin slice; any re-ingest plan must include an explicit re-weighting/down-sampling step for RelatedTo/Synonym-class edges, or the balance problem persists at any scale.
2. **ConceptNet 5.7 full is the single highest-leverage re-ingest target** (broadest already-licensed relation-type vocabulary) — prioritize it over Wikidata-full or ATOMIC2020-full expansion if only one re-ingest is buildable next.
3. **Before spending budget on the >=4-5-bucket target as a design constant, run Part C.** This is now the load-bearing gating test for the entire density-optimum framing in the sibling spec — if it HARD-FAILs, the correct fix is not "try a different threshold" but re-examine whether bucket-diversity-as-count is even the right observable, versus e.g. bucket diversity WITHOUT increasing bind-crosstalk (a structurally different design lever: separate sub-bundles per bucket rather than one fused per-entity bundle).
4. **The re-ingest/enrich/acquire split is a planning input, not a committed budget allocation** — it is mostly-estimated (flagged honestly above); the ConceptNet-5.7-full pilot re-ingest (HARD-PASS/FAIL prediction 2 above) is the cheap way to convert the biggest slice of this estimate into a measured number before committing further build effort.

## Honest gaps / deflation

- CSKG's own paper's per-node relation-diversity statistic could not be confirmed either way (PDF full-text extraction failed in the sub-agent's search) — treated as a probable, not confirmed, literature gap. Flagging this explicitly rather than asserting it.
- The re-ingest/enrich/acquire percentage split is overwhelmingly a reasoned estimate from one sub-agent, weakly anchored to qualitative evidence (Dense-ATOMIC's existence, Recoin's completeness framing, few-shot-KGC degradation patterns) — treat the specific percentages as placeholders to be replaced by Part C's pilot measurement, not as a delivered number.
- Per lit-scan calibration discipline (deflate 0.15-0.25 off an undeflated read, cap novel-synthesis P at 0.50):
  - P(the "genuinely unbuilt, no download-and-use resource exists" verdict holds up under deeper resource-by-resource scrutiny) = **0.55** (deflated from a near-certain undeflated read; the survey covered 11 resources but is not exhaustive — a resource-specific miss is possible).
  - P(the re-ingest/enrich/acquire split is directionally correct — re-ingest is the single largest lever but not dominant/sufficient alone) = **0.45** (moderate; the qualitative direction is evidence-anchored via Dense-ATOMIC/Recoin, the percentages are not).
  - P(the density-optimum target, as currently framed with a fixed bucket-count threshold, survives Part C's degree-controlled test in our specific bind/unbind regime) = **0.35** (capped near novel-synthesis ceiling; genuinely unknown in either direction, and the one closest external analog points against it, though in a different model class).
  - P(arXiv:2508.15291's fragmentation mechanism transfers from dense fused embeddings to our structurally-separated bind/unbind readout) = **0.30** (deflated; plausible but the mechanisms are different enough that transfer is far from assured — this is the actual falsification target of Part C, not a settled prior).

**P_deflated = 0.38** (overall verdict-set viability across all three questions; slightly below the sibling note's 0.40 because this drill surfaces one specific, previously-unflagged counter-risk — the inverse relation-diversity/performance correlation — that the sibling note's own deflation did not have visibility into).

## Citations (verified count: 3 sub-agent lit-scans, ~30 distinct new sources this drill; sibling note's ~45 sources reused by direct reference, not re-verified this cycle)

**Prior-art survey:** Wikipedia "Cyc"; wikidata.org/wiki/Wikidata:Statistics; arXiv:2009.11564 ("Machine Knowledge" survey, avg facts/entity); arXiv:2012.11490 (CSKG paper); CSKG stats (ResearchGate 351988818); arXiv:1612.03975 (ConceptNet 5.5); github.com/commonsense/conceptnet5/wiki/relations; Sap et al. 2019 ATOMIC (ResearchGate 335685676); AAAI ATOMIC2020 paper; arXiv:2308.11884 (YAGO4/4.5); DBpedia dataset page (github.com/dbpedia/extraction-framework/wiki); babelnet.org/statistics; arXiv:2010.05953 (COMET-ATOMIC2020) + github.com/allenai/comet-atomic-2020; arXiv:2210.07621 (Dense-ATOMIC, ACL 2023); arXiv:2101.04640 (Dimensions of Commonsense Knowledge, Ilievski et al.).

**Source-depth quantification:** arXiv:1612.03975 (ConceptNet 5.5 relation table); arXiv:2012.11490 (CSKG, full-text extraction attempted, inconclusive on per-node stat); Wikidata:Statistics live page; Recoin (Balaraman et al., WWW 2018, dl.acm.org/doi/10.1145/3184558.3191641); arXiv:2010.05953 (ATOMIC2020); arXiv:2210.07621 (Dense-ATOMIC, "one-hop annotation" sparsity admission); arXiv:2301.01172-class few-shot/sparse-KGC survey literature.

**Density-optimum literature:** arXiv:2508.15291 (KG complexity metrics for link prediction — Node-level Maximum Relation Diversity, the load-bearing citation for Section 3); arXiv:2310.11917 (semi-inductive link prediction benchmark); arXiv:2507.18977 (long-tail entity prediction in temporal KGs); arXiv:1811.00937 / ACL N19-1421 (CommonsenseQA); arXiv:2307.12382 (CommonsenseVIS); arXiv:2109.09309 (ConceptNet vs SWOW word associations); arXiv:2510.02657 (Less LLM More Documents, saturation curves); arXiv:2510.14271 (denoising KGs for RAG); Zaveri et al.-style KG quality taxonomy + Maastricht systematic-review citation on KG completeness.

**Reused by direct reference, not re-verified this cycle:** all citations in `research_ideal_foundation_spec_size_density_optimum_2026-07-14.md` and its own cross-thread list (`cskg_commonsense_core_kcore_density_gate_2026-07-10.md`, `research_cskg_prior_art_novelty_due_diligence_2026-07-10.md`, `research_grounding_percolation_reachability_cskg_audit_2026-07-11.md`, `research_grounding_foundation_build_plan_2026-07-13.md`, `research_brain_grounding_flexibility_open_spoke_registry_2026-07-14.md`).
