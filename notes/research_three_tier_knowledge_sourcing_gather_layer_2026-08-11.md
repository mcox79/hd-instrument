# Research: Three-tier knowledge system — gather-layer resource inventory (sourcing drill, no build)

Method: field advisor run first (its 22-field substrate-physics taxonomy does not cover KG/knowledge-architecture
topics — same gap already flagged in `research_cskg_prior_art_novelty_due_diligence_2026-07-10.md` and
`research_grounding_percolation_reachability_cskg_audit_2026-07-11.md`; recommend adding a `knowledge-architecture`
field tag at next meta-map refresh). KB-check against those two prior notes + `cskg_commonsense_core_kcore_density_gate_2026-07-10.md`
confirms no dedup conflict: those drills answered "is CSKG novel / does CSKG's graph reach abstract concepts from a
grounded seed"; this drill answers "what ELSE should feed the gather-layer" — a distinct, complementary question.
3 parallel Sonnet lit-scan sub-agents (science/domain KBs; large corpora; process/causal structured KBs) +
director (self) synthesis and disk-verification of what we already own. Generic public resource names only in all
external queries (ChEBI, Reactome, CauseNet, ATOMIC2020, etc. are standard field terms, not substrate-novel
framing); no configs/numbers/mechanism names went off-platform.

## HEADLINE (4-line)

1. **The gap is real and now quantified, not just asserted.** Disk-verified on our own `data/cskg_foundation_v1/metrics.json`:
   of 1,244,136 spine typed edges, `/r/Causes` is **1.39%** (17,249 edges), and even the generous bucket
   (Causes + ATOMIC xEffect/oEffect + HasSubevent/HasFirstSubevent/HasLastSubevent) is only **14.83%** — and 711,428
   of our 1.24M edges (57%) come from ATOMIC, which is *social/interpersonal* commonsense (PersonX bakes a cake →
   xIntent/xReact/xWant), not physical-science process-role knowledge. CSKG's own "Causes"-family relations are
   sparse **and** the wrong register for "combustion consumes fuel."
2. **The single most direct, highest-fidelity fix for typed directional process-role knowledge is biology-domain
   and already-obtainable: Reactome + Rhea.** Both model reactions as first-class objects with typed
   input/output/catalyst/regulator roles (not incidental annotation — it's the core schema), both are CC BY 4.0 /
   CC0, both ship clean offline flat-file dumps, and Reactome directly extends the KEGG pathway maps we already
   cache (`data/bio_kb_cache/kegg/`) with a richer per-reaction role model. This is the direct upgrade path for the
   biological register of "combustion" (cellular respiration: glucose + O2 → CO2 + H2O + energy, an explicit
   Reactome/KEGG reaction chain).
3. **For general-domain (non-biological) causal directionality — the literal "combustion" case — no single
   structured KB found is a complete drop-in fix.** CauseNet (11.6M web/Wikipedia-extracted causal pairs, CC BY 4.0,
   trivially downloadable) is the best *scale* pickup for generic "X causes Y" claims across all domains. WorldTree/
   Explanation Bank is the best *precision* pickup — it is the one resource in the entire scan whose schema
   explicitly, by design, tags a "causal/process" category at natural-language granularity, and its example rows
   literally include "burning fuel requires oxygen" / "combustion is a kind of chemical reaction that releases
   energy" — but it is small (~9,000 rows), elementary-school-grade, and EULA-gated (not a fully open license).
4. **The corpora category (Wikipedia, OpenStax, CK-12, PubMed) is qualitatively different from the structured-KB
   category: it is OBTAINABLE but not directly MERGEABLE.** These are raw prose that need the REASONING/extraction
   step (tier 2 of the user's architecture) to become usable process-role facts — they are not append-and-done like
   CauseNet/ATOMIC2020/Reactome. Simple English Wikipedia and OpenStax textbooks are the highest-density,
   cheapest-to-obtain prose sources for that extraction step (both well under 1GB, OpenStax license needs a
   per-title verify pass — flagged below, not silently assumed CC BY).

---

## What we already own (disk-verified, not re-asserted from memory)

| Resource | Location | Size (disk) | Status |
|---|---|---|---|
| CSKG foundation v1 (ConceptNet+ATOMIC+WordNet+Wikidata-CS+FrameNet+Roget+VisualGenome merge) | `data/cskg_foundation_v1/` | 482,588 nodes / 1,238,686 typed edges | HARD_PASS built 2026-07-26 |
| CSKG raw source | `data/grounding_testbed/cskg.tsv.gz` | 112 MB, 6,001,531 rows | source of above |
| Brysbaert concreteness, Warriner VAD, Lancaster sensorimotor norms, Kuperman AoA | `data/grounding_testbed/*.csv` | ~40k-word CSVs each | ingested as grounding channels |
| Gene Ontology | `data/bio_kb_cache/go/go-basic.obo` | 31 MB | **go-basic, NOT go-plus/go.obo — see gap below** |
| KEGG human pathways | `data/bio_kb_cache/kegg/*.kgml` | 13 MB | pathway maps only, no reaction-role typing beyond KGML's own coarse edges |
| NeuroLex | `data/bio_kb_cache/neurolex/` | 5.5 MB | neuroscience ontology |
| GloVe-300d embeddings | `data/gensim_cache/glove-wiki-gigaword-300/` | cached | distributional, not KG-grounded |
| WordNet, VerbNet, FrameNet | via NLTK, `hdlab/director_kb.py` API-mode ingest | live API pull | already wired into director_kb schema |
| ProofWiki (math) | `config/director_kb_schema.json` references `data/math_kb_cache/proofwiki` | **directory not found on disk** | configured but appears unpopulated — flag for a follow-up check, out of scope here |

**Near-zero-cost fix identified in this drill**: swap `go-basic.obo` → `go.obo`/`go-plus.owl` (same GO license, same OBO
Foundry host, larger file). go-basic strips the `regulates`/`negatively_regulates`/`positively_regulates` edges and
the cross-product logical links to CHEBI/CL/PATO/PR that go-plus retains — i.e. we are currently missing GO's own
directional-regulation edges and its chemistry cross-references, for free, by having downloaded the wrong variant.
This is not a new resource, just a re-download; worth doing regardless of what else gets added.

---

## Ranked resource inventory

Legend: Proc = carries explicit process-role/causal/directional knowledge (Y/N/Partial). Obtain = offline
obtainability (High/Medium/Low, per whether it's a clean one-time flat-file/dump download vs. license-gated vs.
API-dependent with no static archive).

### (b) Science/domain KBs — the category with the sharpest, most rigorous process-role schema

| Resource | Uniquely covers | Complements owned stack | Size | License | Obtain | Proc |
|---|---|---|---|---|---|---|
| **Reactome** | Curated pathways as typed Reactions (hasInput/hasOutput/catalystActivity/regulatedBy), chained into causal pathway sequences | Extends KEGG (already owned) with per-reaction role typing KEGG's KGML lacks | 15,492 human reactions / 2,742 pathways (v90) | CC BY 4.0 (data), CC0 (annotations) | High — flat file/MySQL/Neo4j/BioPAX/SBML, no gate | **Y** — schema-level, not incidental |
| **Rhea** | Expert-curated biochemical reactions, ChEBI-native, substrate/product role-typed, mass-balanced | Turns ChEBI's static taxonomy into an actual directional reaction layer; feeds UniProt's own enzyme annotations | 11,000+ curated reactions | CC BY 4.0 | High — flat file/RDF at ftp.expasy.org, SPARQL optional | **Y** |
| **ChEBI** | Chemical/molecular entity ontology, functional roles (has_role) | New chemistry-taxonomy layer we don't have at all | 180,000+ classes, ~500MB OWL | Free, unrestricted | High — OBO/OWL/TSV/SDF/SQL flat files | Partial — taxonomic/role, not reaction-directional on its own (needs Rhea) |
| **go.obo / go-plus.owl** (upgrade from go-basic, already owned) | Regulates-edges + CHEBI/CL/PATO/PR cross-products stripped from go-basic | Recovers directional regulation + chemistry links from a resource we already have | modestly larger than go-basic (still <100MB) | Same as GO (CC BY 4.0) | High — same OBO Foundry host | Y (regulates edges) |
| **WorldTree / Explanation Bank** | Hand-curated multi-fact explanation graphs for elementary/middle-school science QA; schema explicitly tags causal/if-then/process categories | The only resource found built *specifically* around causal-explanation-as-a-category, at natural-language granularity | ~9,000 tablestore rows / ~5,000 questions, low tens of MB | EULA-gated (free, click-through, tied to AI2 terms) | Medium — direct zip download but license-gated | **Y** — explicit example: "burning fuel requires oxygen" |
| UMLS | Meta-thesaurus, 190+ vocabularies, ~3.49M concepts | Semantic Network has coarse causes/disrupts/treats relations | ~35 GB full | Free but individual click-through license (UTS account) | Medium | Partial — coarse, clinical-scoped |
| SNOMED CT | Clinical concepts, causative-agent typed relations | Disease-causation only | ~370,934 concepts | Same UMLS/NLM gate | Medium | Partial — clinical scope only |
| QUDT, PhySH | Units/quantities ontology; physics subject-heading taxonomy | Infrastructure (dimensional consistency, topic classification), not knowledge content | small | Free/open | High | N — neither carries causal facts |
| NCBI Taxonomy, MeSH | Organism taxonomy; medical subject headings | Pure is-a backbones | 73MB / small | Public domain / free | High | N |

### (c) Large corpora — obtainable but require the REASONING/extraction step, not a direct merge

| Resource | Register | Size | License | Obtain | Notes |
|---|---|---|---|---|---|
| **Simple English Wikipedia** | Pedagogically-simplified, more overtly causal per sentence than full Wikipedia | 284,173 articles, well under 1GB compressed | CC BY-SA 4.0 + GFDL | High — dumps.wikimedia.org, no gate | Best "small, easy, high-signal" text pickup |
| **OpenStax science textbooks** (Biology 2e, Chemistry 2e, Physics, A&P 2e, Microbiology, Environmental Science, Astronomy) | Textbook-pedagogical — explicit worked causal-mechanism teaching prose | 50+ titles, well under 1GB for the science subset | **CC BY 4.0 confirmed for Biology 2e directly; blanket claim NOT verified** — conflicting signals on a possible 2025/2026 licensing-policy change found but not resolved | High for download; License needs a per-title verify pass before ingest | Highest explanatory density of anything scanned, IF license confirms |
| CK-12 FlexBooks | K-12 STEM, even more simplified than OpenStax | tens-hundreds MB | **CC BY-NC 3.0 — non-commercial only** | High | Restriction may matter depending on eventual product license |
| Full English Wikipedia | Mixed encyclopedic register, diffuse science content across ~6.9M articles | ~25GB compressed (raw), ~20GB+ (cleaned plaintext) | CC BY-SA 4.0 + GFDL | High but large — recommend category-filtered subset (WikiProject Chemistry/Biology/Physics tags), not full ingest | |
| PubMed baseline abstracts | Terse, jargon-dense, low explanatory density | ~25-35GB compressed (36M+ records) | Mixed — NLM terms, not uniform CC | High (bulk FTP/HF mirror) | Weakest register for this specific gap |
| PMC Open Access Subset | Full-text biomedical, richer (Methods/Discussion sections explain mechanisms) | multi-hundred-GB to low-TB (3.4M+ articles) | **Split** — filter to CC BY/CC0/CC BY-SA/CC BY-ND group only, exclude NC group | High but needs subsampling strategy | Best biomedical-mechanism corpus IF filtered + subsampled |
| ARC Corpus + SciQ support paragraphs | Purpose-built science-filtered sentence/paragraph pool | 14M sentences / 1.4GB (ARC) + tens of MB (SciQ) | AI2 research-permissive | High | Pre-filtered = higher extraction hit-rate per document than raw Wikipedia |
| S2ORC / Semantic Scholar Academic Graph | Cross-disciplinary full-text | N/A — **no static archive anymore** | ODC-By (current), mixed (legacy) | **Low — API-dependent, not a one-time download** | Deprioritize; overlaps PMC OA + arXiv |
| arXiv full-text bulk | Physics/math preprints, terse/formal | 9.2TB, growing ~100GB/month | Mixed per-paper | **Low — AWS Requester-Pays, real dollar cost** | Use metadata-only mirror (low single-digit GB, CC0) instead if arXiv topic coverage wanted at all |

### (e) Structured process/procedure/causal KBs — the category that directly targets directionality

| Resource | Type | Complements owned stack | Size | License | Obtain | Proc |
|---|---|---|---|---|---|---|
| **CauseNet-Precision** (+Full as recall superset) | Web/Wikipedia-extracted binary causal pairs | Directly fills the 1.39%-`/r/Causes` sparsity found on our own disk, at 10x+ scale, general-domain (not social/biological only) | Precision: ~200K relations/135MB (~83% precision); Full: 11.6M relations/1.8GB | CC BY 4.0 (data), MIT (code) | High — direct JSON/JSONL, causenet.org + Zenodo, no gate | **Y** — every edge is a typed causes relation |
| **ATOMIC2020** | Extends owned ATOMIC from 9 social relations to 23 (+7 physical-entity, +7 event-centered) | New relations (`Causes`, `isBefore`, `isAfter`, `HasSubEvent`, `HinderedBy`, `MadeUpOf`) are exactly the ordering/directionality primitives ConceptNet lacks; marginal-value ingest since original ATOMIC already owned | ~1.33M tuples, 91.3% human-validated acceptance | CC BY 4.0 | High — direct download, HF mirror | **Y** — explicit `Causes`/`isBefore`/`isAfter` |
| WikiHow-derived procedural structure (wikiHow Hierarchy KB, proScript) | Literal step-ordered/partially-ordered task decomposition, 110K+ procedures | The ONLY resource in the whole scan encoding "step 1 precedes step 2" natively at scale | 110K+ procedures / 772K+ steps | **CC BY-NC-SA — non-commercial restriction** | High (direct GitHub/CSV) but license caveat | Y — procedural ordering, not causal-why |
| ASER | Event-relational KG, 14 PDTB discourse-relation types (Precedence, Result, Reason, Condition, ...) | Clause-level discourse-typed edges at huge scale (438M eventualities in Full) | Core: 53M eventualities/52M edges | **Conflicting — MIT (code) vs CC BY-NC-SA cited for data; unresolved, needs direct LICENSE-file check** | **Medium-low** — SharePoint links, not a simple HTTP dump | Y, but license/obtain friction |
| Full Wikidata + causal-property slice (P828/P1542/P1478/P1536/P1479/P1537) | General KB; specific causal properties are editorially curated | Cleanest possible license (CC0); causal slice would need a self-built dump-filter pass (no pre-packaged "causal slice" found) | Full dump ~130GB compressed | CC0 | High for full dump; slice requires build effort | Y but sparse (mainly diseases/historical events) |
| PropBank | Numbered argument-structure frame files | Coverage bridge to VerbNet/FrameNet (already owned) via SemLink | ~11,600 lemmas | CC BY-SA 4.0 | High | N — argument structure, no causality/ordering |
| ConceptNet Numberbatch | Retrofitted embeddings over ConceptNet | Similarity-proxy over structure we already have; adds no new relational content | — | CC BY-SA 4.0 | High | N |
| GLUCOSE | Story-grounded causal statements + generalized causal rules (10 dimensions) | Generalized-rule half could function as reusable causal-inference rules, not just eval data | ~310K-670K annotations (count discrepancy, unresolved) | **Unresolved — verify against source before use** | Unresolved | Y, pending verification |
| Event2Mind | ATOMIC precursor | Fully superseded by ATOMIC2020 | — | CC0 | High | Superseded, not recommended standalone |

---

## Complementarity map — how the recommended set covers the "combustion consumes fuel" example specifically

- **CSKG (owned)**: "wood RelatedTo fire" — associative, no directionality. Confirmed gap.
- **GO/KEGG (owned, GO upgrade recommended)**: biological process taxonomy + pathway maps; the biological analog of
  combustion (cellular respiration) is IN KEGG already as a pathway, but KGML's typed edges are coarser than a full
  reaction-role model.
- **Reactome/Rhea (new)**: supplies the missing reaction-role typing (input/output/catalyst/regulator) for the
  biological register — makes "glucose + O2 → CO2 + H2O + energy, catalyzed by X" a first-class structured fact,
  not prose.
- **CauseNet (new)**: supplies general-domain (non-biological) "X causes Y" pairs extracted at web-scale — very
  plausibly contains "combustion causes CO2 release" or equivalent phrasing, extracted from actual Wikipedia
  sentences, at far larger scale and better license than any hand-curated alternative.
- **ATOMIC2020 (new)**: supplies event-ordering (`isBefore`/`isAfter`) and event-decomposition (`HasSubEvent`) —
  general process-structure primitives (not domain-specific), extending the ATOMIC we already own from social-only
  to physical-entity + event-centered.
- **WorldTree (new)**: the only resource that literally already contains, hand-authored, "burning fuel requires
  oxygen" / "combustion is a kind of chemical reaction that releases energy" as gold-standard rows — small, but the
  most direct textual hit in the entire scan.
- **Simple Wikipedia + OpenStax (new, tier-2 raw material)**: neither is a structured KB — both are the prose
  source a downstream reading/extraction pipeline would mine for the long tail of general-domain process facts
  ("combustion" specifically) that no structured KB in this scan fully covers at the needed granularity. This is
  the tier-2 REASON step of the user's architecture, not a tier-1 gather-and-merge.

**No single resource found closes the general-domain (non-biological) process-role gap on its own.** The
recommended combination (CauseNet for scale + WorldTree for precision/exemplar + Simple-Wikipedia/OpenStax for
raw-material breadth) is deliberately redundant across three different acquisition strategies (web-extraction,
hand-curation, prose-for-extraction) — this is the user's own "union + reasoning assembles what no single source
holds" thesis, applied concretely to this specific example.

---

## Recommended incorporation set (bigger, not smaller — ranked by marginal enabling value)

1. **go-basic.obo → go.obo/go-plus.owl** (near-zero cost, re-download of an owned resource, recovers regulation edges + chemistry cross-products)
2. **Reactome** (full flat-file dump, MySQL or Neo4j) — extends KEGG with reaction-role typing
3. **Rhea** (flat-file/RDF) — extends ChEBI (if ingested) or stands alone as chemistry-reaction-role layer
4. **CauseNet-Precision** (200K relations, 135MB) as the safe starting slice; CauseNet-Full (11.6M, 1.8GB) as a later recall expansion
5. **ATOMIC2020** (1.33M tuples) — marginal-cost extension of an already-owned resource shape
6. **ChEBI** (chemistry ontology) — new domain entirely, pairs directly with Rhea
7. **WorldTree/Explanation Bank** (~9K rows) — small, EULA-gated, but the highest-precision causal-explanation exemplar found
8. **Simple English Wikipedia** (full dump, <1GB) — cheapest, best-licensed, highest-density prose source
9. **OpenStax science-subset textbooks** — pending per-title license verification; if confirmed CC BY, highest pedagogical-explanation density of any corpus scanned
10. **Wikidata causal-property slice** (P828/P1542/P1478/P1536/P1479/P1537) — CC0, but requires a self-built dump-filter (no pre-packaged slice exists); lower priority given CauseNet already covers this space at larger scale with less engineering
11. **WikiHow-derived procedural structure** (wikiHow Hierarchy KB) — the only source of literal step-ordering; CC BY-NC-SA license caveat needs a decision before committing engineering time
12. *(Lower priority / needs resolution first)* ASER (license conflict unresolved, SharePoint-gated download), GLUCOSE (license/size unresolved), UMLS/SNOMED (license-gated, clinical-scoped, narrower fit), PMC OA subset (valuable but needs a subsampling strategy — defer until 1-9 are landed), full Wikidata dump (130GB, defer in favor of the causal-slice-only extraction)

## Top 2-3 highest-value, obtainable, science-grade FIRST additions

1. **Reactome + Rhea (paired)** — the most rigorous, schema-level, directly-typed process-role resource found in
   the entire scan; both CC BY 4.0/CC0, both offline flat-file installable, both a natural extension of KEGG
   (already owned). Highest confidence, lowest license/obtainability risk of any recommendation in this note.
2. **CauseNet-Precision** — the best scale pickup for general-domain causal directionality (the "combustion" case
   specifically), fixing the disk-verified 1.39% `/r/Causes` sparsity at 10x+ scale, CC BY 4.0, zero-gate download.
3. **WorldTree/Explanation Bank paired with Simple English Wikipedia** — WorldTree as a small, hand-curated,
   exactly-on-target gold-standard/seed set (contains the literal combustion example); Simple Wikipedia as the
   cheap, well-licensed, high-signal raw-prose source for the tier-2 extraction step that structured KBs alone
   cannot supply for general-domain process facts.

---

## Cheap decisive test (pre-registered, no build performed this cycle — design only)

Build a held-out probe set of N=30-50 hand-authored "X consumes/produces/causes Y in process Z" facts spanning
biology, chemistry, and physics (the combustion/respiration/photosynthesis register specifically), sourced
independently of any resource under test (e.g. drawn fresh from a science-fact list, not copy-pasted from
WorldTree). Measure recovery rate (fraction of probe facts reconstructable via a 1-2-hop graph query) under two
conditions:
- **Baseline**: CSKG foundation v1 alone (already built, `data/cskg_foundation_v1/`).
- **Enriched**: CSKG foundation v1 + Reactome + Rhea + CauseNet-Precision + WorldTree, ingested via the same
  `hdlab/director_kb.py`-style deterministic triple-extraction pattern already used for GO/KEGG (obo_go/kegg_kgml
  modes) — Reactome/Rhea will need NEW parser modes (flag: this is real engineering, not a drop-in, since neither
  fits the existing obo_go/kegg_kgml/jsonl_edges dispatch cleanly without a new extractor).

**Controls (required, per lit-scan calibration discipline)**: (1) shuffled-relation control — permute relation
labels across the enriched KB before querying; recovery must collapse toward baseline (rules out an artifact where
the enriched KB "wins" merely from more entity coverage, not more relational structure). (2) baseline-plus-random-
edges control — add an equal NUMBER of random (non-causal) edges to CSKG instead of the real enriched sources;
recovery must NOT rise to the enriched level (rules out "more edges of any kind helps" as the explanation).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS**: enriched recovery rate ≥ baseline + 0.30 (absolute, on the 30-50-fact probe) AND the shuffled
  control collapses to within 0.05 of baseline AND the random-edges control stays within 0.10 of baseline (i.e. the
  gain is from the SPECIFIC new relational content, not generic density). This would validate the recommended
  incorporation set as a genuine, not cosmetic, fix for the process-role gap.
- **HARD-FAIL**: enriched recovery rate < baseline + 0.10 (the new sources don't cover the needed granularity/
  register despite being "process-role" resources on paper), OR the shuffled control does NOT collapse (probe
  design leak — recovery was never really testing relational structure), OR the random-edges control matches the
  enriched result (density alone explains the gain, not content specificity — would redirect effort toward corpus-
  extraction (tier 2) rather than more structured-KB ingestion).
- **MIDDLE_BAND**: recovery gain in [0.10, 0.30) — real but partial; would indicate the structured-KB layer alone is
  necessary-but-not-sufficient and the tier-2 extraction-from-corpora step (Simple Wikipedia/OpenStax) is load-
  bearing for full coverage, not merely a nice-to-have.

## Cross-thread synthesis

- Directly extends `research_cskg_prior_art_novelty_due_diligence_2026-07-10.md` (confirmed CSKG is correctly
  adopted, not rebuilt) and `research_grounding_percolation_reachability_cskg_audit_2026-07-11.md` (confirmed
  CSKG's graph structure is dense enough to reason over and reach abstract concepts from a grounded seed) — those
  two drills validated the STRUCTURE of what we own; this drill identifies what's missing from its CONTENT
  (process-role/causal specificity), a distinct and complementary finding, not a re-drill of the same question.
- Directly operationalizes `project_PIVOT_build_ideal_knowledge_foundation_from_existing_tools_USER_AUTHORIZED_2026-07-14`
  and `project_foundation_llm_built_kb_vetted_plus_substrate_condenses_knowledge_while_reading_USER_2026-07-23` —
  this drill supplies the concrete resource list for the "FULL+VETTED external tool" foundation tier those
  directives call for, and the corpora-vs-structured-KB distinction found here maps directly onto the user's own
  "gather (tier 1, many complementary sources) → reason (tier 2) → consolidate (foundation/growing middle tier)"
  architecture: structured KBs (Reactome/Rhea/CauseNet/ATOMIC2020) are genuine tier-1 gather-layer material;
  corpora (Wikipedia/OpenStax) require the tier-2 reasoning/extraction step before they become gather-layer facts.
- Extends the already-owned bio ingest pattern (`hdlab/director_kb.py` `obo_go`/`kegg_kgml` modes,
  `hdlab/director_kb_bio_sources.py`) — Reactome/Rhea are the natural next bio-domain ingest targets using the
  same schema-as-config pattern, but will need new parser modes (flagged honestly above as real engineering, not
  a trivial config change).

## Substrate-product implications

1. **The recommended set is not "replace CSKG" but "layer onto CSKG"** — CSKG remains the commonsense-relatedness
   backbone; Reactome/Rhea/CauseNet/ATOMIC2020/WorldTree each add a DIFFERENT missing axis (biological reaction-role
   typing, general-domain causal scale, general-domain causal precision, event-ordering) rather than duplicating
   what's already there. This directly executes the user's "union + reasoning assembles what no single source
   holds" thesis with concrete, licensed, obtainable candidates rather than leaving it as a stated principle.
2. **License due-diligence is load-bearing, not a footnote**: CK-12 (CC BY-NC), WikiHow-derived data (CC BY-NC-SA),
   ASER (data license unresolved/conflicting), GLUCOSE (unresolved), UMLS/SNOMED (individual click-through gate)
   all carry real restrictions that must be resolved BEFORE ingestion, not discovered after. OpenStax's blanket
   license status could not be confirmed this cycle (Biology 2e verified CC BY 4.0 directly; other titles and a
   possible 2025/2026 policy change were not resolved) — flag this explicitly rather than assuming.
3. **The corpora-vs-structured-KB distinction is a genuine architectural finding**: it means the "gather layer" as
   specified needs TWO different ingestion mechanisms, not one — a schema-as-config triple extractor (already built,
   reused for GO/KEGG/WordNet/VerbNet/FrameNet) for structured sources, and a SEPARATE reading/extraction mechanism
   (not yet built, and explicitly the harder, blocking problem per the project's own "do the hard blocking thing"
   discipline) for corpus sources. Landing the structured-KB tier first (items 1-6 above) is the correct sequencing
   precisely because it does NOT require that harder extraction mechanism to exist yet — it is genuine, real,
   obtainable progress on the gather layer that does not block on, or substitute for, solving reading/extraction.
4. **The disk-verified 1.39%/14.83% causal-sparsity numbers should become a standing acceptance-gate metric** for
   any future foundation-store rebuild (analogous to the existing k-core density gate and the relation-
   reconstruction shuffle-control gate already used in `exp_cskg_foundation_v1.py`) — track causal-edge fraction
   pre/post each new ingest as a concrete, falsifiable measure of whether the gather layer is actually closing this
   specific gap, not just growing in raw size.

## Citations (verified count: approximately 75 distinct URLs across 3 parallel Sonnet lit-scan sub-agents)

Sub-agent A (science/domain, ~21 sources): ChEBI/EBI, ChEBI NAR paper, GO Cross Product Guide, GO annotation
downloads, Reactome Data Model, Reactome Download, Reactome License, Reactome v90 news, Rhea NAR 2022, Rhea
license (reusabledata.org), UniProt-Rhea enzyme annotation (PMC), UniProt re3data, WorldTree Explanation Bank,
WorldTree V2 NSF PAR, Jansen et al. 2016 ACL (C16-1278), UMLS NLM, UMLS 2025AB technical bulletin, SNOMED CT
licensing (NLM), QUDT GitHub, PhySH GitHub, NCBI Taxonomy FTP, MeSH RDF docs.

Sub-agent B (corpora, ~39 sources): WikiProject Chemistry, Wikimedia dump page, Wikipedia:Database download,
wikimedia/wikipedia (HF), Wikipedia:Reusing content, Commons:Licensing, Wikipedia-monthly blog, Simple Wikipedia
stats (ExpandedRamblings), arXiv doc-level simplification paper, GitHub Dump-of-Simple-English-Wiki, Internet
Archive simplewiki dump, CITL NIU OpenStax overview, OpenStax Biology 2e preface, OpenStax licensing help article,
OpenStax licensing-update blog post, OpenStax commercial-use help, CK-12 Wikipedia page, CK-12 Terms of Use,
freekidsbooks CK-12 index, ncbi/pubmed (HF), NLM 2016 baseline stats, PubMed download page, PMC FTP Service, PMC
OA subset info, PMC Bulk FTP, PMC OA on Academic Torrents, PMC Open Access file list, Europe PMC downloads, S2ORC
GitHub, S2ORC paper (arXiv:1911.02782), S2ORC README, Semantic Scholar API tutorial, arXiv bulk data access,
arXiv S3 cost analysis, Kaggle arXiv dataset, TDS arXiv 1.7M-articles post, OpenBookQA paper, SciQ (HF), ARC paper
(arXiv:1803.05457), TQA dataset page (AI2).

Sub-agent C (process/causal, ~19 sources): causenet.org, CauseNet Zenodo record, ATOMIC2020 relation breakdown
(deepwiki), comet-atomic-2020 GitHub, ASER paper (arXiv:1905.00270), ASER GitHub, WikiHow-Dataset GitHub,
wikihow_hierarchy GitHub, proScript (arXiv:2104.08251), wikihow-cleaned (HF), ConceptNet Numberbatch GitHub,
ConceptNet Numberbatch blog post, Wikidata entities dump, Wikidata:Licensing, Wikidata Help:Modeling causes,
propbank.github.io, propbank-frames GitHub, GLUCOSE GitHub.

Director spot-verification (this cycle): `data/cskg_foundation_v1/metrics.json` relation_distribution/
source_distribution (disk-read, not sub-agent-reported); `config/director_kb_schema.json` source_classes
enumeration (disk-read); `data/bio_kb_cache/{go,kegg,neurolex}` directory listings + sizes (disk-read).

No substrate-novel mechanism names, configs, or numerical parameters were sent in any external query.

## Deflated confidence summary (per lit-scan calibration discipline: deflate 0.15-0.25, cap novel-synthesis P at 0.50)

- P(Reactome/Rhea ingestion is low-engineering-risk given the existing GO/KEGG bio-ingest pattern) = **0.55**
  (deflated from a more confident read — the existing `obo_go`/`kegg_kgml` parser modes do NOT directly cover
  Reactome's own flat-file schema or Rhea's RDF/flat-file schema; a genuinely new parser mode is required, which is
  real, non-trivial engineering, not a config change).
- P(CauseNet-Precision materially improves recovery on a held-out general-domain causal probe beyond what CSKG's
  own sparse `/r/Causes` provides) = **0.55** (capped at the 0.50-adjacent range for an untested combination;
  moderate confidence given CauseNet's scale and Wikipedia-extraction provenance overlaps our own CSKG source
  material, which cuts both ways — could mean genuine complementary coverage, or could mean redundant re-discovery
  of facts already implicitly present).
- P(WorldTree's ~9,000-row corpus, despite its small size and EULA gate, meaningfully raises recovery on a broader
  held-out science-process probe beyond its own elementary-level scope) = **0.40** (deflated — small, narrow-grade
  corpus; valuable as an exemplar/seed set, uncertain as a scale contributor).
- P(a Simple-Wikipedia/OpenStax extraction pipeline can reliably produce clean structured process-role triples
  WITHOUT a downstream extraction-quality mechanism that does not yet exist in this project) = **0.35** (capped at
  the 0.50 novel-synthesis ceiling and deflated below it — this is explicitly the harder, unsolved tier-2 problem,
  not a simple merge; treat as a known blocking dependency, not an assumed win).
- P(OpenStax's actual current licensing, once directly verified per-title, permits the intended reuse without
  restriction) = **0.55** (genuinely uncertain pending direct verification; Biology 2e confirmed CC BY 4.0
  directly, but conflicting signals on a possible policy change were found and NOT resolved this cycle — do not
  proceed on an assumption here).

## Next-drill candidate

If the science/domain ingestion path is pursued: drill the Reactome/Rhea flat-file schema directly (read one
sample dump file end-to-end) to scope the new parser-mode engineering effort concretely before committing an
exp_dev cycle to it. If the corpora/extraction path is prioritized instead: this connects directly to the
already-in-flight frame-activation reading build (`project_frame_activation_reading_B_direction_2026-08-11`) — the
SAME graded frame/script-activation matching mechanism being built for ProPara bridging is the natural extraction
mechanism for turning Simple-Wikipedia/OpenStax prose into structured process-role facts; this is a genuine
cross-thread convergence point worth flagging to the Director for sequencing, not a coincidence — both need the
same underlying "trigger word activates a graded-matched process frame with unstated participants" capability.
