# Research drill: math + science ingest extractor design
**Date:** 2026-06-27
**Drill type:** 2x research (broad lit-scan + narrow operational design)
**Author:** research (Director)
**USER context:** intermittent flight wifi; produce design + recommendation; Director dispatches first one when USER returns
**Strategic anchor:** USER 2026-06-22 vision Phase 3 = substrate proposes new mathematics (prereq: substrate knows existing mathematics); M3 glass-box conversational AI needs structured knowledge to reason from

---

## 0. Prior-art audit (mandatory before designing)

Verified before drafting. Substrate already has math-domain extractors authored ~2026-06-13 (13 days old, pre-dating chunk-ingest KB v2 architecture):

| Source | Tool | Target format | Landed? |
|--------|------|---------------|---------|
| ProofWiki v1 | `tools/substrate_ingest_proofwiki_v1.py` | OLD `data/substrate_index/*/atoms.jsonl` | unknown (atoms partition) |
| OEIS v1 | `tools/substrate_ingest_oeis_v1.py` | OLD atoms.jsonl | partial (smoke 1K default) |
| Lean mathlib v2 | `tools/substrate_ingest_lean_mathlib_v2.py` | OLD atoms.jsonl | unknown |
| Coq library v2 | `tools/substrate_ingest_coq_library_v2.py` | OLD atoms.jsonl | unknown |
| Mizar v1 | `tools/substrate_ingest_mizar_library_v1.py` | OLD atoms.jsonl | unknown |
| DLMF / MathWorld v1 | `tools/substrate_ingest_dlmf_mathworld_v1.py` | OLD atoms.jsonl | unknown |
| arXiv abstracts | `data/arxiv_abstracts_cache/` exists; `exp_n7_arxiv_abstracts_ingest_cert_v1_smoke_probe/` | OLD atoms.jsonl | unknown smoke probe |
| PubMed | NOT TRIED | n/a | no |

**Key architectural mismatch:** prior extractors wrote to OLD `data/substrate_index/<corpus>/atoms.jsonl` partition. That partition IS already picked up by the new KB v1 via `atoms` source class (capped at 5000 lines/file), BUT:
- v1 filename-metadata KB indexes by atom-id-as-filename (low signal)
- v2 chunk-ingest KB targets file-based `source_classes` registered in `config/director_kb_schema.json` — this is the canonical KB now
- No math source classes are registered in v2 schema (only `wordnet/verbnet/framenet` lexical + `gene_ontology/kegg_pathway/neurolex` bio)

**Design implication (load-bearing):** new extractors must follow `hdlab/director_kb_bio_sources.py` pattern: cache external content to disk + add source class to schema + let the existing chunk-ingest pipeline pick it up. This composes with `tools/director_kb_continuous_ingest.py` (Principle 4 schema-as-config; Principle 11 chain-grade primitive only).

Do NOT rewrite the OLD partition extractors. Leave them in tree; their atoms still flow through the `atoms` source class. Design NEW extractors that fit v2.

---

## 1. Extractor designs

### 1.1 ProofWiki (formal mathematical theorems + proofs)

**Source:** https://proofwiki.org — MediaWiki instance; ~30k pages (theorems + definitions + axioms + book proofs)
**License:** CC-BY-SA 3.0 — provenance + attribution required in each chunk's metadata
**Estimated facts:** ~25k theorem pages + ~8k definition pages + ~2k axiom pages ≈ 35k atoms (file-level); ~120k–200k content chunks at 200-800 char target

**Source-class registration (additive to schema):**
```json
"proofwiki": {
  "root_dir": "data/math_kb_cache/proofwiki",
  "glob": "**/*.md",
  "max_files": null,
  "encoding": "utf-8",
  "license_tag": "CC-BY-SA-3.0",
  "provenance_url_field": "proofwiki_url",
  "rejects_log_field": "skip_reason",
  "mode": "text"
}
```

**Atom-schema:**
- Entity types (additive): `THEOREM`, `DEFINITION`, `AXIOM`, `PROOF`, `MATHEMATICAL_OBJECT`, `MATHEMATICAL_FIELD` (algebra, analysis, topology, etc.)
- Relation types (additive): `STATES_THEOREM`, `DEFINES`, `ASSUMES_AXIOM`, `PROOF_OF`, `CITES_THEOREM`, `CITES_DEFINITION`, `IN_FIELD`, `GENERALIZES`, `SPECIAL_CASE_OF`
- Each page-file emits chunks via existing `director_kb_chunk_ingest.py` (no new chunking code needed)
- Per-page extra-tags: `proofwiki_pageid`, `proofwiki_url`, `entity_type` (THEOREM/DEFINITION/AXIOM), `mathematical_field` (best-effort regex from categories), `cites_pages` (list — comma-joined for storage)

**Extraction tool design:** `hdlab/director_kb_math_sources.py` (new module, mirrors `director_kb_bio_sources.py`):
1. `fetch_proofwiki(repo_root, force=False)` — download MediaWiki XML dump (`https://dumps.wikimedia.org/proofwiki/latest/proofwiki-latest-pages-articles.xml.bz2` if available, else page-by-page via `Special:Export` paginated — 30k pages at ~1 req/sec with 1.0s throttle = ~8h; cache once, never re-fetch)
2. `parse_proofwiki(xml_path, max_pages=None)` — XML SAX parse `<page>` entries with namespace=0; extract title + wikitext body; convert wikitext to markdown via minimal transform (`[[X]]` → `[X](X.md)`; `== H ==` → `## H`; drop templates `{{...}}`); detect entity_type from category tags
3. `materialize_proofwiki(parsed, out_dir)` — write one markdown file per page to `data/math_kb_cache/proofwiki/<safe_filename>.md` with YAML front-matter (license, url, entity_type, fields, citations)
4. Chunk-ingest picks up `**/*.md` glob automatically once schema source-class registered

**Wall-cost (full ingest):**
- Fetch: 8h one-time (rate-limited; or 30min if XML dump URL works)
- Parse + materialize: ~30min (XML SAX is fast)
- Chunk ingest into KB: ~3-4min added to continuous ingest cycle (35k files × 4-6 chunks/file ≈ 175k new atoms; CharTrigramEncoder is O(n) on content bytes; current full ingest ~7min on ~17k files, so ~+4min)
- **Total cold ingest: ~9h one-time; subsequent re-ingests: +4min/cycle**

**Quality/coverage tradeoffs:**
- Full = ~35k file atoms + ~175k content chunks; covers entire ProofWiki corpus
- Smoke = 500 theorem pages from "Featured" + "Most-linked" categories; ~3k chunks; ingest cost ~30s; **always run smoke first per discriminator-must-survive-scale (USER 2026-06-26)**
- Sample-vs-full risk: smoke may pass discriminator at 3k chunks but fail at 175k (anisotropy / V_C feasibility). Pre-reg MUST include capacity-feasible regime check per BIAS-S (USER 2026-06-24)

**Discoverability heuristics (which atoms most useful for Director-KB queries):**
- Theorem-name-as-query is HIGHEST signal (e.g., "Cauchy-Schwarz inequality" → rank-1 the theorem page chunk)
- Proof-step content useful for Phase 3 "substrate proposes new mathematics" (chunked proof bodies = reasoning examples)
- CITES_THEOREM relation graph = math-dependency-graph (substrate can traverse for chain-of-proof queries)
- `entity_type=AXIOM` chunks form the bedrock set (~2k atoms; small enough to fit in dense WM)

---

### 1.2 OEIS (Online Encyclopedia of Integer Sequences)

**Source:** https://oeis.org — ~370k sequences (as of 2026-06)
**License:** OEIS Foundation; "noncommercial use" — research use OK; attribution required; SHOULD NOT redistribute as-is bulk corpus, but can extract derived knowledge
**Estimated facts:** ~370k sequence entries; flat-file dump available

**Source-class registration:**
```json
"oeis": {
  "root_dir": "data/math_kb_cache/oeis",
  "glob": "**/A*.md",
  "max_files": null,
  "encoding": "utf-8",
  "license_tag": "OEIS-Foundation-noncommercial",
  "provenance_url_field": "oeis_url",
  "rejects_log_field": "skip_reason",
  "mode": "text"
}
```

**Atom-schema:**
- Entity types: `INTEGER_SEQUENCE`, `GENERATING_FUNCTION`, `RECURRENCE_RELATION`
- Relation types: `FIRST_TERMS`, `GENERATED_BY`, `SATISFIES_RECURRENCE`, `RELATED_SEQUENCE` (cf:, see also), `OFFSET`, `IS_KEYWORD` (e.g., easy, hard, nice, core), `AUTHORED_BY`
- One markdown file per A-id: `A000045.md` (Fibonacci) — front-matter has A-id + first 50 terms; body has name + comments + formulas + references + xrefs

**Extraction tool design:**
1. `fetch_oeis(repo_root, force=False)` — `stripped.gz` (~10MB; A-id + first terms) + `names.gz` (~30MB; A-id + name). Existing `tools/substrate_ingest_oeis_v1.py` already implements this; reuse the download logic but write to NEW cache path
2. `parse_oeis_to_files(stripped_gz, names_gz, max_seqs=None, fetch_details=False)` — emits one .md per A-id. If `fetch_details=True`, additionally calls `https://oeis.org/A{id}/internal` for richer body (rate-limited 1 req/sec; 370k seq = 100h — NOT recommended; default OFF)
3. **No fetch_details by default:** name + first terms + xref-from-stripped is enough; full body fetch is opt-in for chain-grade probes

**Wall-cost:**
- Fetch: 1min (~40MB total)
- Parse + materialize 370k files: ~5min (one file per sequence; filesystem overhead is the bottleneck; consider sharding into `data/math_kb_cache/oeis/A0/`, `A1/`, ..., `A3/` subdirs for filesystem speed)
- Chunk ingest: 370k files × 1-2 chunks/file ≈ 500k atoms; ~12-15min added to continuous ingest cycle — **THIS IS THE EXPENSIVE ONE**
- **Total cold ingest: ~25min; subsequent re-ingests +15min/cycle (~3x current cost)**

**Quality/coverage tradeoffs:**
- Full 370k = significant ingest-cost spike (KB triples from ~54k internal + 754k lexical + 222k bio → +500k = ~1.5M total atoms; query latency impact unknown — needs measurement)
- Smoke: top-10k "Core" + "Nice" + "Easy" sequences (~10k atoms; covers Fibonacci, primes, Catalan, etc.); cost ~30s
- Tiered approach RECOMMENDED: ship smoke FIRST, then dispatch capacity-sweep cell measuring query latency at 100k vs 370k, then decide on full

**Discoverability heuristics:**
- Sequence-recognition use case ("given 1,1,2,3,5,8 → A000045") is the killer query — needs FIRST_TERMS as searchable content, NOT just metadata. Materialization must put first 20 terms in chunk content body
- xref graph (RELATED_SEQUENCE) = sequence-similarity-graph; substrate already has bind/unbind primitives for traversal
- Keyword `core` (1000-ish sequences) is the high-signal subset; could be a separate `oeis_core` source class for prioritized retrieval

---

### 1.3 PubMed (neuro subset)

**Source:** NCBI E-utilities API (`eutils.ncbi.nlm.nih.gov`)
**License:** PubMed abstracts are public domain (NLM-produced metadata); full-text varies (often paywalled); we extract ABSTRACTS ONLY
**Estimated facts (neuro subset):** filtering by MeSH `Neurosciences[MAJR]` OR brain-region terms ≈ ~1.5M papers total; useful recent subset (last 10 years) ≈ ~500k papers

**Source-class registration:**
```json
"pubmed_neuro": {
  "root_dir": "data/science_kb_cache/pubmed_neuro",
  "glob": "**/PMID*.md",
  "max_files": null,
  "encoding": "utf-8",
  "license_tag": "public-domain-NLM-abstracts",
  "provenance_url_field": "pubmed_url",
  "rejects_log_field": "skip_reason",
  "mode": "text"
}
```

**Atom-schema (two-tier — IMPORTANT design decision):**
- **Tier A: paper-level atoms** — one .md per PMID with title + abstract + MeSH terms + authors. Entity type `PAPER`. Relations: `AUTHORED_BY`, `PUBLISHED_IN_JOURNAL`, `PUBLISHED_YEAR`, `MESH_TAG`
- **Tier B: entity-level concept atoms** — extracted via MeSH-vocabulary lookup against fixed concept lists (brain regions from NeuroLex, drugs from DrugBank-subset, diseases from MeSH-D). Entity types `BRAIN_REGION`, `NEUROTRANSMITTER`, `DRUG`, `DISEASE`. Relations: `MENTIONED_IN_PAPER`, `CO_MENTIONED_WITH` (paper-level co-occurrence)
- **Ship Tier A first; Tier B as separate cell after Tier A baseline** (per stage-progression discipline — don't skip)

**Extraction tool design:**
1. `fetch_pubmed_neuro(repo_root, query, max_papers=10000, force=False)`:
   - `esearch.fcgi?db=pubmed&term=<query>&retmax=10000` to get PMID list (paginate via retstart)
   - `efetch.fcgi?db=pubmed&id=<batch_of_200_PMIDs>&rettype=abstract&retmode=xml` (batch 200 PMIDs/call; 1 req/sec throttle per NCBI policy → 500k papers / 200 / 1/sec = ~42min for fetch)
   - Default query: `(Neurosciences[MAJR] OR brain[MAJR] OR neuron[MAJR]) AND ("2015"[PDAT] : "3000"[PDAT]) AND hasabstract[All Fields]`
2. `parse_pubmed_xml(xml_path)` — XML SAX parse `<PubmedArticle>` entries; extract PMID + title + abstract + MeSH headings + journal + year + authors
3. `materialize_pubmed_papers(parsed, out_dir)` — one .md per PMID at `data/science_kb_cache/pubmed_neuro/PMID<id>.md`; shard into PMID-prefix subdirs

**Wall-cost:**
- Fetch (500k papers, neuro filter): 42min — but bounded by NCBI rate-limit; consider API-key (free; raises to 10 req/sec → 6min)
- Parse + materialize: ~15min (XML parse is fast; filesystem write of 500k small files is the cost)
- Chunk ingest: 500k files × 2-3 chunks/file (abstracts are short; ~1500 chars typical) ≈ 1.2M atoms; ~30min added to continuous ingest cycle — **VERY LARGE**
- **Total cold ingest: ~1h with API-key; subsequent re-ingests +30min/cycle — RECOMMEND opting out of continuous ingest for pubmed_neuro; manual re-ingest only**

**Quality/coverage tradeoffs:**
- Full neuro subset (500k papers) approximately TRIPLES KB size — needs USER vetting before dispatch
- Smoke: 5k recent high-impact papers (top journals × 5 years); cost ~3min; sufficient to validate the pipeline
- License risk: paper abstracts public domain; safe to redistribute. Full-text NOT extracted — only metadata + abstract
- Calibration penalty per lit-scan: large noise floor (abstracts are NOT vetted facts; biomedical literature has reproducibility crisis). Down-weight `MENTIONED_IN_PAPER` as evidence (P=0.30 not P=0.70). PMI co-occurrence is signal but weak

**Discoverability heuristics:**
- Tier B concept atoms (BRAIN_REGION, NEUROTRANSMITTER, etc.) compose with EXISTING NeuroLex + Gene Ontology atoms — synergy with current bio KB
- Tier A paper atoms useful when Director asks "what's known about X" — returns ranked abstracts as evidence
- MeSH-tag-as-query is highest signal (canonical controlled vocab); free-text query lower signal
- BIAS-13 contamination risk: papers cite each other; substrate may learn citation patterns instead of fact patterns. Pre-reg discriminator must control for citation-graph baseline

---

### 1.4 arXiv (math + physics)

**Source:** arXiv OAI-PMH API or bulk S3 dump
**License:** arXiv metadata public; abstract redistribution allowed; full-text per-paper license varies (mostly CC-BY)
**Estimated facts (math + physics):** ~800k math papers + ~1.5M physics papers (cumulative since 1991) ≈ 2.3M papers; recent subset (last 10y) ≈ 1M papers

**Source-class registration:**
```json
"arxiv_math_physics": {
  "root_dir": "data/science_kb_cache/arxiv_math_physics",
  "glob": "**/arxiv_*.md",
  "max_files": null,
  "encoding": "utf-8",
  "license_tag": "varies-per-paper-metadata-CC0",
  "provenance_url_field": "arxiv_url",
  "rejects_log_field": "skip_reason",
  "mode": "text"
}
```

**Atom-schema:**
- Entity types: `ARXIV_PAPER`, `ARXIV_CATEGORY`, `ARXIV_AUTHOR`
- Relation types: `IN_CATEGORY` (e.g., `math.AG` algebraic geometry, `hep-th` high-energy theory), `AUTHORED_BY`, `SUBMITTED_DATE`, `CROSS_LISTED`, `CITES_ARXIV` (optional; requires citation-graph fetch from inspire-hep / semantic-scholar)
- Per-paper .md: front-matter (id, categories, authors, date) + body (title + abstract)

**Extraction tool design:**
1. `fetch_arxiv_oai(repo_root, from_date, set="math:OR:physics", force=False)`:
   - OAI-PMH endpoint: `https://export.arxiv.org/oai2?verb=ListRecords&set=math&metadataPrefix=arXiv&from=YYYY-MM-DD`
   - Paginate via resumptionToken; default 1000 records/page; 1 req/3sec throttle (arXiv policy)
   - 1M papers / 1000 per page / 3sec = ~50min fetch — acceptable
2. `parse_arxiv_oai(xml_path)` — XML parse OAI-PMH responses; extract metadata
3. `materialize_arxiv(parsed, out_dir)` — one .md per arXiv-id at `data/science_kb_cache/arxiv_math_physics/<yymm>/arxiv_<id>.md`

**Wall-cost:**
- Fetch (1M recent papers): ~50min
- Parse + materialize: ~15min
- Chunk ingest: 1M files × 2 chunks/file ≈ 2M atoms; ~50min added to continuous ingest cycle — **HUGE; arguably exceeds substrate working capacity**
- **Total cold ingest: ~2h; subsequent re-ingests +50min/cycle — DEFINITELY opt out of continuous; manual or scheduled-weekly re-ingest**

**Quality/coverage tradeoffs:**
- Full = 1M abstracts triples KB size again — needs USER vetting; combined with pubmed_neuro this is ~4x current KB
- Smoke: 10k recent math+physics papers (last 30 days); cost ~3min
- **Lowest signal-density per atom** of the 4 sources: abstracts are short, jargon-heavy, often opaque without paper body. CharTrigramEncoder may produce noisy cosine retrieval on math LaTeX-heavy abstracts (BIAS-S regime check: encoder may not survive scale)

**Discoverability heuristics:**
- Category-as-query (e.g., `math.AG`) returns category-cluster — useful for topic-area exploration
- Author-as-query returns author's body of work — useful but lower priority for substrate-as-Director-KB
- Full-text would be MUCH higher signal; OUT OF SCOPE for v1 (license + size)
- **Synergy with ProofWiki:** arXiv math papers cite ProofWiki theorems → cross-source CITES edges possible in v2

---

## 2. Sequencing recommendation (priority order)

**Ranking criteria:**
1. **Signal density per atom** (does each ingested atom contribute structured knowledge or noise?)
2. **Ingest cost (cold + steady-state)** under no-lock-in (small wins shippable in 1 cycle)
3. **Strategic prerequisite weight** for USER vision Phase 3 (substrate proposes new mathematics)
4. **Schema-vetting risk** (how many new entity types + relation types added; cap-int integration discipline)
5. **License + redistribution risk**

| Rank | Source | Signal | Cost (cold) | Strategic weight | Schema risk | License risk |
|------|--------|--------|-------------|------------------|-------------|--------------|
| 1 | ProofWiki | HIGH | 9h one-time + 4min/cycle | LOAD-BEARING for Phase 3 | LOW (theorem/proof schema clean) | LOW (CC-BY-SA) |
| 2 | OEIS smoke (10k Core) | HIGH | 30s | HIGH for Phase 3 | LOW | LOW |
| 3 | OEIS full | HIGH | 25min + 15min/cycle | HIGH | LOW | MEDIUM (don't redistribute bulk) |
| 4 | PubMed neuro smoke (5k) | MED | 3min | MED (M3 reasoning evidence) | MED (Tier B concept extraction adds entity types) | LOW |
| 5 | arXiv smoke (10k recent) | LOW | 3min | LOW (broad coverage diagnostic) | LOW | LOW |
| 6 | PubMed neuro full (500k) | MED | 1h + 30min/cycle | MED | MED | LOW |
| 7 | arXiv full (1M) | LOW | 2h + 50min/cycle | LOW | LOW | MEDIUM |

**RECOMMENDED FIRST: ProofWiki.**

Rationale (under USER's bias-checklist + experiment-design discipline):
- **Highest signal density:** every chunk is a vetted mathematical fact (theorem statement, definition, axiom, proof step). No "papers say X" noise floor.
- **Smallest manageable size:** 35k file atoms + ~175k chunks is ~3x current KB. Larger than ideal but bounded; doesn't require staged tiering.
- **Strategic load-bearing:** USER Phase 3 = "substrate proposes new mathematics." Substrate must KNOW existing mathematics first. ProofWiki is the most-structured open dataset for this (Coq/Lean/Mizar are MORE formal but harder to extract usable English-language chunks — those should stay in the OLD partition atoms.jsonl for now).
- **Schema cleanliness:** theorem/proof/axiom is a small, clean new entity-type set (3-4 new types; 6-7 new relations); cap-int INTEGRATION-CHECK discipline easy to satisfy.
- **License clean:** CC-BY-SA 3.0 with provenance + attribution per chunk; redistribution legal.
- **Discriminator-must-survive-scale (USER 2026-06-26):** smoke ingest 500 pages → measure cosine query top-1 vs random baseline → if discriminator holds at 500, project to 35k. Full-N preview arm in smoke: ingest 500 + measure top-1 at FULL-N substrate cosine threshold; if baseline >=0.95 of mechanism, reject full dispatch and rethink.

Second: OEIS smoke 10k Core (cheap; high-signal; orthogonal to ProofWiki; can run in parallel cycle).
Third: dispatch ProofWiki full only after smoke HARD_PASS + USER vet.
Fourth: PubMed/arXiv only after USER decision on KB-size budget (their bulk would 4x KB; needs capacity-sweep cell first).

---

## 3. Actionable cell spec — FIRST EXTRACTOR (ProofWiki smoke)

### Pre-reg: `preregs/n8_proofwiki_smoke_ingest_chunk_kb_v1.md`

**Anchor:** `n8_proofwiki_smoke_ingest_chunk_kb_v1`
**Author:** research → routes to `hdi_skunkworks` for cell-author + `hdi_orchestrator` for dispatch (HYBRID architecture)
**Stage:** Stage 3 (compositional understanding) — substrate-knows-math is compositional knowledge prerequisite
**Runtime estimate:** 8min total (5min smoke fetch via Special:Export 500 pages × 0.6sec, 1min materialize, 30sec chunk-ingest, 1min query smoke)
**Compute:** local_cpu (no GPU needed; CharTrigramEncoder is cheap)

**REQUIRED_FIELDS (per Skunkworks-VET format):**
- `arms`: 4
  - A: `BASELINE_FILENAME_QUERY` — query existing v1 filename-metadata KB for "Cauchy-Schwarz" → record top-1 cosine + filename
  - B: `SMOKE_INGEST_500` — fetch 500 ProofWiki "Featured" pages → materialize → chunk-ingest → query "Cauchy-Schwarz" against new chunks → record top-1 cosine + chunk-content snippet
  - C: `FULL_N_PREVIEW_DISCRIMINATOR` — same query as B but cosine threshold computed assuming N=35k chunks via analytical scaling (tau_full = tau_smoke × sqrt(35000/500)); if smoke top-1 cosine doesn't clear scaled threshold, HARD_FAIL discriminator
  - D: `CONTAMINATION_CONTROL` — query "Banana Republic" (non-math) against new chunks; expect bottom-quartile cosine; if top-1 cosine > 0.5, encoder is leaking name-similarity → BIAS-S regime failure
- `HARD_PASS`:
  - B top-1 cosine >= 0.85 on theorem-name queries (5 probe queries: Cauchy-Schwarz, Pythagoras, Bayes, Euler-Lagrange, Mean-Value-Theorem)
  - B top-1 chunk content contains the theorem statement (verify-the-referent: not just filename match)
  - C analytical scaling holds (smoke discriminator survives full-N projection)
  - D contamination control PASSES (non-math queries don't rank math chunks above 0.5)
  - **MIDDLE_BAND if:** B passes but C fails (discriminator doesn't survive scale; needs full-N test cell)
  - **HARD_FAIL if:** B top-1 cosine < 0.7 OR D contamination > 0.5
- `EXPECTED_N_UNITS`: 500 pages → ~2500 chunks (5 chunks/page avg)
- `HARD_FAIL_CARDINALITY_BREACH`: if observed chunks < 1500 OR > 4000 (silent-truncation guard per META_RULE_H)
- `cardinality_ok` field required in metrics.json output
- `no silent except` per META_RULE_J — all fetch errors record + halt OR re-raise
- `verify_the_referent`: B verdict checks that returned chunk CONTENT contains theorem statement, NOT just that filename matches
- `experimental_bias_checklist`: BIAS-S (regime check — encoder behavior at 500 vs 35k), BIAS-Q (suspect 1.000 results — flag if any cosine = 1.0 exactly), BIAS-N (verify-the-referent in verdict field)

### Cell skeleton: `cells/n8_proofwiki_smoke_ingest_chunk_kb_v1.py`

```python
"""n8 ProofWiki smoke ingest into chunk-KB v2 (research; 2026-06-27).

Stage 3 prerequisite: substrate-knows-math for Phase 3 (substrate proposes new mathematics).
Smoke arm: 500 Featured pages; HARD_PASS gate per pre-reg.

Composes ONLY on chain-grade primitives:
  - hdlab.director_kb_chunk_ingest (Wave 4 v1)
  - hdlab.director_kb_query (with --filename-contains for verification)
  - new: hdlab.director_kb_math_sources.fetch_proofwiki_featured + parse + materialize

No silent except (META_RULE_J). cardinality_ok in metrics. verify_the_referent.
"""
# ... (skeleton; cell author fleshes out per hdi_skunkworks)
```

### New module to ship: `hdlab/director_kb_math_sources.py`

Mirrors `hdlab/director_kb_bio_sources.py` exactly. Initial functions:
- `fetch_proofwiki_featured(repo_root, max_pages=500, force=False)` — Special:Export 500 most-viewed Featured pages
- `parse_proofwiki_xml(xml_path, max_pages=None)` — XML SAX parse + wikitext-to-markdown transform
- `materialize_proofwiki(parsed, out_dir)` — one .md per page with YAML front-matter (title, url, entity_type, license=CC-BY-SA-3.0, fields)
- Function signatures + docstrings match bio_sources pattern; determinism contract identical

### Schema patch: `config/director_kb_schema.json`

Add to `source_classes`:
```json
"proofwiki": {
  "root_dir": "data/math_kb_cache/proofwiki",
  "glob": "**/*.md",
  "max_files": null,
  "encoding": "utf-8",
  "license_tag": "CC-BY-SA-3.0",
  "provenance_url_field": "proofwiki_url",
  "rejects_log_field": "skip_reason",
  "mode": "text"
}
```

Add to `entity_types`: `THEOREM`, `DEFINITION`, `AXIOM`, `PROOF`, `MATHEMATICAL_FIELD` (5 new)
Add to `relation_types`: `STATES_THEOREM`, `DEFINES`, `ASSUMES_AXIOM`, `PROOF_OF`, `CITES_THEOREM`, `IN_FIELD`, `GENERALIZES`, `SPECIAL_CASE_OF` (8 new)

(Schema bump: `schema_version` v1 → v2; `schema_date` 2026-06-26 → 2026-06-27; principle-1 wipe-and-rebuild safe per existing schema-as-config design)

### Dispatch sequence (when USER returns):
1. Director runs `tools/predispatch_check.py n8_proofwiki_smoke_ingest_chunk_kb_v1` (Fix #26)
2. Director spawns `hdi_skunkworks` to cell-author + smoke-VET per Skunkworks-format
3. Skunkworks dispatches via `hdi_orchestrator` → local_cpu queue (no GPU needed)
4. On landing: TaskCompleted hook fires → research evaluates HARD_PASS gate → if PASS, queue ProofWiki FULL dispatch + OEIS smoke parallel; if MIDDLE_BAND, queue full-N test cell; if FAIL, root-cause + redesign

---

## 4. Calibration notes (lit-scan discipline; USER 2026-06-24 bias-checklist)

- **Lit-scan calibration penalty applied:** original probability estimates of "extractor will pass first dispatch" deflated 0.20 across all 4 sources (novel-synthesis ingestion under no-lock-in architecture is unusual in lit). Capped at P=0.50 per discipline.
- **BIAS-S regime check applied:** smoke discriminators may NOT survive full-N (anisotropy / cosine threshold scales with sqrt(N_atoms) per Mu-Viswanath). Pre-reg full-N preview arm required (Check C).
- **BIAS-Q suspect-1.000 applied:** any cosine = 1.0 exactly in smoke → flag as potential identity-match leak (filename-based shortcut, not content match)
- **BIAS-N verify-the-referent applied:** B arm verdict requires content-string match, not just filename match (caught prior false-positive class)
- **Brain-is-existence-proof (USER 2026-06-23) applied:** humans learn mathematics from formal texts (ProofWiki-like). HIGH prior (P=0.65 not 0.30) that substrate-with-mathematical-chunks can answer math queries — only risk is implementation correctness
- **Empowered-to-experiment (USER 2026-06-22) applied:** literature is mixed on KG-ingest-into-VSA scaling; substrate's bet is on doing what's considered hard. Default DISPATCH the smoke (cost bounded; discriminator honest)
- **Stage-progression discipline (USER LOCKED 2026-06-26):** ProofWiki ingest is Stage 3 (compositional understanding) work, NOT Stage 4 (LM equivalence). Don't conflate; don't claim ProofWiki ingest "makes substrate a language model"

---

## 5. Open questions for USER (when wifi returns)

1. **KB-size budget:** PubMed full (500k) + arXiv full (1M) = 1.5M new atoms = 4x current KB. Do you want to authorize that or stay in smoke-tier across all sci sources?
2. **PubMed Tier B (concept extraction):** worth shipping as separate cell after Tier A smoke, or skip and stay paper-level only?
3. **arXiv full-text:** OUT OF SCOPE v1 due to license + size. Want a separate research drill on arXiv-LaTeX-source full-text extraction (high signal, complex license)?
4. **Cross-source CITES edges (arXiv → ProofWiki):** v2 enhancement after both land; want it pre-reg'd now or deferred?
5. **OEIS sequence-recognition use case:** is "given first 5 terms identify A-id" a chain-grade discriminator you want substrate to pass, or just nice-to-have?

---

## 6. Sources cited (lit-scan; query-privacy generic terms only)

- MediaWiki XML export format spec (mediawiki.org public docs)
- OEIS Foundation download policy + stripped.gz/names.gz format (oeis.org/download.html public docs)
- NCBI E-utilities documentation + rate-limit policy + MeSH controlled vocabulary (ncbi.nlm.nih.gov public docs)
- arXiv OAI-PMH API documentation (arxiv.org/help/oa public docs)
- Mu & Viswanath 2018 "All-but-the-top" cosine-anisotropy paper (referenced for BIAS-S scaling check; cited generically)
- Hyperdimensional computing literature on KG ingestion (Plate FHRR; Gayler VSA; Kanerva sparse distributed memory) — referenced via memory:project_session_2026-06-23_strategic_decisions_full_arc.md

---

## File pointers (absolute paths)

- This design: `d:/AI/hd-instrument/notes/research_drill_math_science_extractor_design_2026-06-27.md`
- Schema config (to patch): `d:/AI/hd-instrument/config/director_kb_schema.json`
- Bio-source reference pattern: `d:/AI/hd-instrument/hdlab/director_kb_bio_sources.py`
- Chunk-ingest primitive (chain-grade v1): `d:/AI/hd-instrument/hdlab/director_kb_chunk_ingest.py`
- Continuous ingest (composes new source-class automatically): `d:/AI/hd-instrument/tools/director_kb_continuous_ingest.py`
- OLD ProofWiki extractor (reference; OLD partition format): `d:/AI/hd-instrument/tools/substrate_ingest_proofwiki_v1.py`
- OLD OEIS extractor (reference; OLD partition format): `d:/AI/hd-instrument/tools/substrate_ingest_oeis_v1.py`
- Pre-dispatch check tool (Fix #26): `d:/AI/hd-instrument/tools/predispatch_check.py`
- USER strategic-vision memory: `~/.claude/projects/d--AI/memory/project_user_strategic_vision_self_improvement_portal_core_mathematics_USER_2026-06-22.md`
- USER bias-checklist memory: `~/.claude/projects/d--AI/memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`
