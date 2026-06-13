# Testbed -> Research: FULL ACCOUNTING of downloaded external science/math/knowledge corpora on remote desktop -- 4.37M facts across 5 corpora + 30GB raw + pre-computed bge vectors -- READY TO INGEST per USER directive

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close)
**Re:** USER directive "get a full accounting of the science/math/knowledge we've downloaded and share with research"

## TL;DR

Substantial external corpora ALREADY DOWNLOADED + bge-VECTORIZED on remote desktop (`C:/dev/hd-instrument/data/substrate_state/`). Five production-scale corpora totaling **4.37 million facts + ~29.5 GB raw + matching pre-computed vector embeddings**. Ingest pipelines to substrate-atom format have NOT been built yet; Research just filed 5-CELL design + CELL 1 Mizar parser skeleton.

## Production corpora inventory (remote desktop)

| Corpus | Raw size | Records (facts_added) | Source | Status |
|---|---|---|---|---|
| `arxiv_2m` | **1.83 GB** | **234,352 facts** | 117,466 arxiv papers (abstracts + entity extraction) | facts.jsonl + keys.npy bge vectors |
| `conceptnet_8m` | **3.52 GB** | **457,875 facts** | 8M ConceptNet rows (subject-relation-object) | facts.jsonl + keys.npy bge vectors |
| `pubmed_5m` | **0.77 GB** | **99,225 facts** | 60,120 PubMed abstracts | facts.jsonl + keys.npy bge vectors |
| `wikidata_truthy_50m` | **21.91 GB** | **3,397,252 facts** | 5.69M Wikidata truthy triples (94.5M lines scanned) | facts.jsonl + 253 keys_partial_*.npy (sharded) |
| `wikipedia_100k` | **1.43 GB** | **184,354 facts** | 94,010 Wikipedia articles (sentence-level extraction) | facts.jsonl + keys.npy bge vectors |
| **TOTAL** | **~29.5 GB** | **4,373,058 facts** | -- | all bge-encoded; ready for substrate-atom mapping |

Plus test/smoke/sanity subsets: `arxiv_test` (n/a), `conceptnet_smoke`, `pubmed_test`, `wikidata_smoke`, `wikidata_test` (empty), `wikipedia_sanity`.

## Pre-existing infrastructure

### Downloaders (exist; OPERATIONAL)
- `tools/dl_wikipedia_10k.py`
- `tools/dl_wikipedia_100k.py`
- `tools/dl_wikipedia_1m.py`
- `tools/dl_cwq.py`
- `tools/dl_multihop.py`
- `tools/dl_webqsp.py`
- `tools/probe_arxiv_subjects.py` (probe-only)

### Experiments using these corpora (exist)
- `experiments/exp_wikipedia_ingest_benchmark_gpu_v1.py`
- `experiments/exp_wikipedia_ingest_100k_gpu_v1.py`
- `experiments/exp_wikipedia_ingest_1m_gpu_v1.py`
- `experiments/exp_substrate_wikipedia_layer15_cache_extraction_v1.py`

### Pre-existing facts.jsonl record format (sample)
```jsonl
{"fact": "Q31 currency Q4916."}             # wikidata: Q31 (Belgium) has currency Q4916 (Euro)
... (varies by corpus)
```

## Gap: facts.jsonl -> substrate-atom-with-DEPENDS_ON-edges pipeline

The 4.37M facts sit as structured triples in facts.jsonl + matching bge vectors. The MAPPING from facts.jsonl to substrate Atom + RelationType edges has NOT been built. Per Research's 5-CELL external corpus ingest design (filed 2026-06-13):

| Cell | Status | Maps from |
|---|---|---|
| CELL 1 Mizar | NOT BUILT (parser skeleton just filed) | New download needed (Mizar MML) |
| CELL 2 Wikidata SPARQL | NOT BUILT | New SPARQL queries; alternative: **map from existing wikidata_truthy_50m facts.jsonl** (3.4M facts on disk now) |
| CELL 3 arXiv full | NOT BUILT | Could supplement existing arxiv_2m (234K facts) with OAI-PMH harvest |
| CELL 4 nLab | NOT BUILT | New download needed |
| CELL 5 Wikipedia math-targeted | NOT BUILT | Could filter existing wikipedia_100k (184K facts) by category |

## Honest framing

- The user's memory was correct: substantial download work HAS been done (prior sessions); 29.5 GB across 5 corpora bge-vectorized
- The download phase is PARTIALLY complete (Mizar + nLab not yet downloaded)
- The ingest-to-atoms phase has NOT been built (Research's 5-CELL design is the path forward)
- Wikidata SPARQL (CELL 2) could partially leverage existing wikidata_truthy_50m without re-download
- Wikipedia math-targeted (CELL 5) could filter existing wikipedia_100k without re-download

## Atom-yield projection (if ingest pipelines ship)

Per Research 5-CELL projection: 1742 -> 300K-2M atoms post external ingest. With existing 4.37M facts on disk, the ACTUAL yield could exceed projection -- the bottleneck is **(a) entity-extraction + dedupe pipeline + (b) bge vector reuse from existing keys.npy files**.

Wikidata truthy 3.4M facts alone, mapped at 1:1 to atoms, would 1900x the current substrate (1844 atoms). At a 10% retention rate (filter for math + science + entity-of-interest), still ~340K new atoms.

## Recommendations

1. **Priority lift CELL 2 Wikidata SPARQL design**: reuse existing wikidata_truthy_50m facts.jsonl + keys.npy (no re-download needed; 21.9 GB ready)
2. **Coordinate with Exp-Dev**: desktop runners are dead (per Exp-Dev's just-filed routing); restart needed before ingest cells run
3. **LFS migration P0.3 BLOCKER unresolved**: external corpus ingest will produce massive shards exceeding GitHub 100MB
4. **Build extract-from-facts.jsonl mapper FIRST** as common substrate (used across all 5 cells); reuses existing bge vectors via keys.npy load

## Routing

**Testbed**:
- Inventory complete + shared per USER directive
- Standing for Research direction on ingest priority (CELL 2 leveraging existing wikidata download = HIGHEST near-term return; CELL 1 Mizar fresh download = HIGHEST USER-goal alignment)
- L6-PROOF PHASE 2 substrate_query.py prove subcommand SHIPPED today (commit 60bf3300); EMPIRICALLY VALIDATED at depth-2 (PP-376 PROVED via INSTANCE_OF chain to SCHOOL/structured_prediction_family axiom)

**Research**:
- This inventory shared
- Direction on which existing corpora to map first
- Direction on whether to do facts.jsonl -> substrate atoms via existing bge vectors (fast path) or fresh SPARQL/parse (clean path)

**Exp-Dev**:
- Desktop runners reportedly dead per your routing; user said "exp_dev will restart them"

## Cross-references

- `C:/dev/hd-instrument/data/substrate_state/` (remote desktop; raw corpora + bge vectors)
- research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_5_CELL_DESIGN_*_2026-06-13.md (5-cell design)
- research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*_2026-06-13.md (Mizar parser skeleton)
- testbed L6-PROOF commit 60bf3300 + HP_v1+ 0.75 HARD-PASS commit 00073a25 + T1 backfill complete commit 1c211ea5

---

**Testbed:** FULL ACCOUNTING external corpora downloaded remote desktop 4.37M facts 29.5GB ready-to-ingest + arxiv_2m 234K facts 1.83GB + conceptnet_8m 458K facts 3.52GB + pubmed_5m 99K facts 0.77GB + wikidata_truthy_50m 3.4M facts 21.91GB sharded 253 partial_npy + wikipedia_100k 184K facts 1.43GB + all bge-encoded keys.npy vectors ready + downloader tools dl_wikipedia_10k/100k/1m + probe_arxiv_subjects exist + 4 experiments exp_wikipedia_ingest_* exist + facts.jsonl -> substrate atoms mapper NOT BUILT (gap) + Research 5-CELL ingest design filed 2026-06-13 + CELL 1 Mizar parser skeleton filed + CELL 2 Wikidata SPARQL can REUSE existing wikidata_truthy_50m (fast path) + CELL 5 Wikipedia can FILTER existing wikipedia_100k by category + projection 4.37M facts could 1900x substrate at 1:1 or 340K new atoms at 10pct retention substantially exceeds Research 5-CELL 300K-2M projection + LFS migration P0.3 BLOCKER unresolved + standing for Research direction on map-existing vs fresh-SPARQL/parse + L6-PROOF PHASE 2 SHIPPED today commit 60bf3300 prove subcommand 5-edge typing context EMPIRICALLY VALIDATED at depth-2 + USER substrate-self-mathematical-understanding goal substantively advanced.
