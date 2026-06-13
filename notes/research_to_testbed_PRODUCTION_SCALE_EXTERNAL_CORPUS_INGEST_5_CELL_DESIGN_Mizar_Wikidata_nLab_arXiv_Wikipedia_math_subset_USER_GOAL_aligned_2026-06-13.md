# Research -> Testbed: Production-scale EXTERNAL CORPUS INGEST -- honest inventory + 5 concrete cell designs (Mizar + Wikidata + nLab + arXiv + Wikipedia math subset) -- USER-goal-aligned

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER question on Testbed ingest process for science / math literature / Wikidata; honest inventory + scale-up cell designs to close USER goal "substrate understands own math + needs the background to do that"

## TL;DR (honest inventory)

| Component | Status | Scale | USER-goal-aligned? |
|---|---|---|---|
| Phase 1 evolve auto-ingest (research_drill_*.md) | OPERATIONAL | ~600 atoms incremental | YES (Cycle 13 4.3x growth proven) |
| Phase 2-5 + Phase 6 bulk JSONL ingest | OPERATIONAL | per-batch | YES |
| Phase-2-light extractor (Z>=3 recurrence + smoke) | OPERATIONAL but methodology issue | per-file | partial (smoke->full degradation per Heaps + Good-Turing drill; not yet methodology-fixed) |
| T1 algebra-dict-specific ingest tool | OPERATIONAL | BATCH 01-16 in queue | YES (150 atoms in routing-note queue; not yet ingested) |
| dl_wikipedia_10k/100k/1m.py downloaders | OPERATIONAL | up to 1M articles | NO (general-purpose; not math-targeted yet) |
| probe_arxiv_subjects.py | PROBE ONLY | subject metadata | NO (not full text + entity ingest) |
| Wikidata SPARQL endpoint scraper | NOT BUILT | -- | gap |
| Mizar Mathematical Library ingest | NOT BUILT | -- | **direct USER-goal alignment gap** |
| nLab / nCatLab scraper | NOT BUILT | -- | gap |
| Math StackExchange / MathOverflow ingest | NOT BUILT | -- | gap |
| Lean / Coq / Agda library ingest | NOT BUILT | -- | gap |
| Semantic Scholar / DBLP integration | NOT BUILT | -- | gap |

Current substrate atom count: ~1742+ atoms (production index). With BATCH 01-16 ingest pending: ~1892. With full production-scale external corpus ingest (5 cells below): potential ~50K-500K atoms math + science.

## 5 concrete cell designs (priority-ordered by USER-goal alignment)

### CELL 1: Mizar Mathematical Library ingest (HIGHEST PRIORITY; direct L6-PROOF + USER-goal alignment)

**Why first**: Mizar has ~50K formalized theorems each with EXPLICIT AXIOM DEPENDENCIES (depth-N proof graphs). Directly maps onto substrate algebra_dict.axioms + DEPENDS_ON + is_axiom flag. Mizar Mathematical Library is the LARGEST publicly available checked mathematical knowledge base. CHTV-1 type-checker can verify Mizar proofs at substrate-level after ingest.

**Source**:
- Mizar Mathematical Library: http://mizar.org/library/
- Available format: MML article text + .voc vocabulary files + .miz formal source + .abs abstract files
- License: Mizar license (permissive academic use)
- Pre-existing structured form: 1200+ articles, 50K+ theorems with axiom-dependency graph

**Cell design**:
```python
# tools/substrate_ingest_mizar_library_v1.py
# 1. Download Mizar MML mirror (http://mizar.uwb.edu.pl or mirror)
# 2. Parse .miz files to extract: theorem_name, statement, axiom_dependencies (theorem-refs), proof_steps
# 3. Map to substrate Q2+Q3 convention:
#    - canonical_name = mizar_theorem_identifier
#    - tier = T1 (foundational) | T2 (intermediate) | T3 (applied)
#    - partition = math_foundation
#    - algebra_dict.axioms = parsed axiom_dependencies
#    - algebra_dict.statement = mizar_theorem_statement (cleaned)
#    - is_axiom = (no axiom_dependencies)
#    - DEPENDS_ON edges = each axiom_dependency relation
# 4. Ingest with existing substrate_evolve_phase6_bulk_jsonl.py pipeline
# 5. Pre-reg HARD-PASS: 30K+ atoms ingested + depth-5 chains exist + cross-validation 100 random theorems substrate-prove HARD-PASS via L6-PROOF
```

**Cost**: ~3-5 days build + ~1-2 days ingest + Testbed deduplication review (substrate-quality-first per methodology rule 7). ~30K-50K atoms added. Largely remote_cpu_queue safe.

**Substrate-product positioning**: substrate becomes FIRST cognitive architecture with native ingest of formalized mathematical knowledge at scale + L6-PROOF verification over the ingested corpus.

### CELL 2: Wikidata SPARQL endpoint scraper (~math/science Q-entities)

**Why**: Wikidata Q199 (mathematics) + Q5878 (logic) + Q333 (physics) + ... taxonomies hold ~100K-500K math/science Q-entities with structured properties (P31 instance-of + P279 subclass-of + P527 has-part). Directly maps to substrate INSTANCE_OF + SPECIALIZES + DEPENDS_ON edges per CHTV-1 generalized typing context.

**Source**: SPARQL endpoint at https://query.wikidata.org/sparql

**Cell design**:
```python
# tools/substrate_ingest_wikidata_math_science_v1.py
# SPARQL query example:
# SELECT ?item ?itemLabel ?parent ?parentLabel WHERE {
#   ?item wdt:P31/wdt:P279* wd:Q11862829 .  # academic discipline / math subclass
#   OPTIONAL { ?item wdt:P279 ?parent . }
# }
# Iterate over math/science categories: Q11862829 + Q333 + Q12483 + ...
# Map P31 = INSTANCE_OF, P279 = SPECIALIZES, P527 = DEPENDS_ON (or USES depending on)
# Filter: keep only items with English label + at least one substrate-relevant property
# Q2+Q3 convention applied
```

**Cost**: ~2-3 days build + ~1-2 days SPARQL extraction (rate-limited; SPARQL endpoint quota); ~100K-500K candidate atoms; Testbed deduplication review heavy. remote_cpu_queue safe (no GPU).

**Substrate-product positioning**: substrate becomes first cognitive-architecture-with-Wikidata-grade ingest at math/science depth.

### CELL 3: arXiv math.* + cs.LG full-text + abstract ingest

**Why**: ~500K math + ML papers; recent (last 5 years) covers current research surface. Abstract-level entity extraction + DEPENDS_ON inference via citation graph.

**Source**:
- arXiv OAI-PMH harvesting API
- arXiv bulk data via S3 (for-pay; ~$50-200/month)
- arXiv harvest tools: arxiv-public-datasets, paperscape

**Cell design**:
```python
# tools/substrate_ingest_arxiv_math_cs_v1.py
# 1. Use OAI-PMH to harvest arXiv math.* + cs.LG abstracts + titles + authors + categories + citation_graph
# 2. Per paper:
#    - canonical_name = arxiv_id (e.g. arxiv_2501_12345)
#    - tier = T3 (specific paper instance)
#    - partition = research_history
#    - algebra_dict.axioms = none (it's a paper not a theorem)
#    - algebra_dict.statement = abstract_text
#    - DEPENDS_ON = citation references (paper -> cited papers)
# 3. Entity extraction from abstract -> link to existing substrate math atoms (BATCH 01-16 corpus)
# 4. INSTANCE_OF -> arxiv category (math.NT + math.PR + cs.LG + ...)
```

**Cost**: ~3-5 days build + ongoing daily harvest cron. ~500K-1M atoms (papers); ~5K-50K extracted entity-class atoms. remote_cpu_queue safe.

**Substrate-product positioning**: substrate becomes daily-updated math/science research surface; LLMs train periodically with cut-off, substrate ingests daily.

### CELL 4: nLab / nCatLab category theory wiki scraper

**Why**: nLab has ~10K-30K category theory articles with rich cross-linking; complements BATCH 06 categorical foundations + L3 DisCoCat ship plan. Direct depth boost for substrate's categorical-substrate positioning.

**Source**: https://ncatlab.org/nlab/show/HomePage (MediaWiki interface; permissive license)

**Cell design**:
```python
# tools/substrate_ingest_nlab_v1.py
# 1. Recursive scrape of nLab pages starting at HomePage + Category_theory + Type_theory + Homotopy_type_theory
# 2. Per article:
#    - canonical_name = nlab_article_slug
#    - tier = T2 / T3
#    - partition = math_foundation::category_theory
#    - algebra_dict = parsed mathematical content
#    - DEPENDS_ON = inter-article wiki-link references
# 3. Cross-link to BATCH 06 atoms (category + functor + natural_transformation + monoidal_category + isomorphism)
```

**Cost**: ~2-3 days build + ~1 day scrape (rate-limited). ~10K-30K atoms. remote_cpu_queue safe.

**Substrate-product positioning**: substrate becomes deepest categorical-substrate cognitive architecture; nLab is THE reference for category theory; substrate ingests it natively.

### CELL 5: Wikipedia math/science targeted subset (refinement of existing dl_wikipedia_*.py)

**Why**: dl_wikipedia_*.py downloaders exist but are general-purpose. Math/science targeting via category tree traversal needed. Mid-priority because Wikidata (CELL 2) covers the structured Q-entity backbone; Wikipedia adds prose-form + cross-reference linkage.

**Cell design**:
```python
# tools/substrate_ingest_wikipedia_math_science_targeted_v1.py
# 1. Traverse Wikipedia Category:Mathematics + Category:Physics + Category:Computer_science (depth-N tree)
# 2. Filter dl_wikipedia_*.py results to math/science article subset
# 3. Per article:
#    - canonical_name = wikipedia_article_title
#    - tier = T1/T2/T3 per heuristic (T1 = foundational e.g. "Vector space"; T3 = specific e.g. "Erdos-Ko-Rado theorem")
#    - partition = math_foundation OR science_foundation
#    - DEPENDS_ON = inter-article links
# 4. Cross-link to Wikidata Q-entity IDs (CELL 2 dependent)
```

**Cost**: ~2-3 days build (reuses dl_wikipedia_*.py for download stage) + ~1-2 days categorical filter + ingest. ~50K-200K atoms math/science. remote_cpu_queue safe.

## Combined production-scale ingest projection

If all 5 cells ship + ingest:
- Mizar: ~30K-50K formalized theorems with axiom-dependency graph (L6-PROOF directly applicable)
- Wikidata: ~100K-500K Q-entities structured math/science
- arXiv: ~500K-1M paper records + ~50K extracted math/science entity atoms
- nLab: ~10K-30K category theory deep articles
- Wikipedia math/science targeted: ~50K-200K prose articles cross-linked to Wikidata

Substrate atom count projection: 1742 -> 300K-2M atoms across math + science. Substrate-product positioning artifact extension: FIRST cognitive architecture with this scale of structured math/science ingest + L6-PROOF + Curry-Howard + CHTV-1 verifier + categorical type theory.

## Methodology + discipline preservation

- meta::RULE_authoring_substrate_queries_first: Research provides cell-design CANDIDATES; Testbed retains ingest authority + verification
- substrate-quality-first (methodology rule 7): each cell must preserve quality at scale (Phase-2-light smoke + Heaps + Good-Turing methodology applies)
- 9th methodology rule (refine-via-empirical-FAIL): expect cells to surface unforeseen ingest issues; iterate per HARD-FAIL feedback

## Heat-aware queueing per Exp-Dev's correction

- All 5 cells: remote_cpu_queue SAFE (no laptop heat)
- Test batches small to start (5K-10K atoms); scale up post-HARD-PASS verification
- LFS migration P0.3 (user-auth-blocked) becomes critical: production ingest will produce massive .jsonl shards exceeding GitHub 100MB

## Priority sequencing

1. **CELL 1 Mizar** first (USER-goal direct: L6-PROOF applicability + formalized-theorem corpus + axiom-dependency graph)
2. **CELL 2 Wikidata** next (highest atom count return + structured Q-entity backbone for INSTANCE_OF + SPECIALIZES)
3. **CELL 4 nLab** third (categorical-substrate positioning depth)
4. **CELL 5 Wikipedia math/science** fourth (prose cross-link breadth)
5. **CELL 3 arXiv** fifth (most operational complexity; live-update cron)

Total ~13-20 days build + ~5-10 days ingest + Testbed verification. Production-scale substrate self-knowing math + science corpus achievable Cycle 52-53.

## Substrate-product positioning artifacts (post production ingest)

15+ artifacts at Cycle 51 close + post CHTV-1; production ingest adds:
- FIRST cognitive architecture with Mizar-grade formalized math ingest + L6-PROOF verifiable
- FIRST with Wikidata-scale structured Q-entity backbone + INSTANCE_OF + SPECIALIZES typed edges
- FIRST with nLab-grade categorical knowledge + L3 DisCoCat-aware corpus
- FIRST with daily-updated arXiv + cross-linked to Wikidata + Wikipedia at scale

LLM categorical gaps compound (training cutoff vs daily update + prose-only vs typed-edges + no checkable ground truth vs CHTV-1 1.0 precision).

## Routing

- **Testbed**: CELL 1-5 candidate; coordinate with Exp-Dev queue; prioritize CELL 1 Mizar (~3-5 days build)
- **Exp-Dev**: remote_cpu_queue available per heat clarification; CELL 1-5 are CPU-only + I/O-bound; safe queue
- **Research**: standing for cell verdicts + BATCH 17+ on-demand authoring if ingest reveals gaps; LFS migration P0.3 critical-path BLOCKER for production-scale ingest visibility

## Cross-references

- notes/exp_dev_to_research_RESUMING_queued_handoffs_on_REMOTE_desktop_heat_was_laptop_only_2026-06-13.md (remote queue clarification)
- notes/research_drill_smoke_to_full_corpus_degradation_alternative_hypotheses_2x_2026-06-12.md (Heaps + Good-Turing methodology fix needed before production-scale)
- BATCH 01-16 routing notes (Research-side T1 algebra corpus precondition)
- memory `substrate-as-self-extending-engine-4-3x-growth-2026-06-12` (Phase 1 auto-ingest proven; production scale precedent)

---

**Testbed:** PRODUCTION-SCALE EXTERNAL CORPUS INGEST honest inventory + 5 concrete cell designs CELL 1 Mizar Mathematical Library 50K theorems axiom-dependency graph L6-PROOF direct + CELL 2 Wikidata SPARQL 100K-500K Q-entities INSTANCE_OF SPECIALIZES backbone + CELL 3 arXiv math.* cs.LG 500K papers + CELL 4 nLab 10K-30K categorical depth + CELL 5 Wikipedia math/science targeted 50K-200K prose breadth + combined projection 300K-2M atoms math+science + all 5 cells remote_cpu_queue SAFE + priority sequence Mizar Wikidata nLab Wikipedia arXiv + ~13-20 days build + Cycle 52-53 production-scale substrate self-knowing math+science + LFS migration P0.3 BLOCKER production visibility + USER goal substrate understands own math production-scale path + USER full-auto overnight continuing.
