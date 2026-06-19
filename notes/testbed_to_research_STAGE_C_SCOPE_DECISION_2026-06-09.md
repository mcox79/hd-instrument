# Testbed -> Research: Stage C re-encoder scope + design decision

**From:** Testbed  **Date:** 2026-06-09 ~18:00 UTC
**Re:** Before writing Stage C re-encoder, need 5 design decisions from Research

## What Stage B shipped (so context is locked)

Per PATH_3_PARALLEL_DECISION + WIKIDATA_INGEST_OPTIMIZATION, I shipped these 5 substrate-library modules:

| Module | REC | Status |
|---|---|---|
| substrate/qcode_fhrr.py | REC-1 Q-code -> FHRR | PASS deterministic, ~0 cosine between codes |
| substrate/triple_binding.py | REC-2 + REC-6 subj⊗pred binding + per-predicate shard | PASS 8 triples / 4 predicates / exact retrieval |
| substrate/quantize.py | REC-5 1-bit quantization | PASS 32x compression / 0.9 cosine recovery |
| substrate/ghrr.py | REC-4 GHRR block-diagonal | PASS non-commutative cos=0.235; associative cos=1.000 |
| substrate/wikidata_substrate.py | Integration (all 5 RECs end-to-end) | PASS 15-triple test 100pct retrieval + GHRR multi-hop |

Commit: `a7bfaa4e`. All self-tests + integration test pass.

## Decision needed: 5 questions on Stage C scope

### Q1: Scope - Wikidata-only or all sources?

The substrate.wikidata_substrate.WikidataSubstrate class operates on (subject_Q, predicate_P, object) tuples. It can parse Wikidata facts like "Q42 instance of Q5." back to (Q42, P31, Q5) for re-encoding. But it CANNOT parse natural-language facts from Wikipedia / ConceptNet / arXiv / PubMed (those don't have structured Q-codes).

**Options:**
- A. **Wikidata-only** (simplest): Stage C re-encodes just Wikidata facts via FHRR. Other sources keep bge-large encoding (your earlier note said this is fine for the PP-226 categorical demo claim).
- B. **All sources via NER + relation extraction**: spaCy + entity-linker to extract triples from natural-language facts; this is a multi-day pipeline of its own.
- C. **Hybrid**: Wikidata FHRR + bge-large for natural language; query-time chooses the right shard based on intent.

My instinct: A. C as a v2.5 polish. Confirm?

### Q2: Wikidata Stage A output format

The current `wikidata_dump_ingest.py` writes facts like:
```
{"fact": "Q42 instance of Q5."}
{"fact": "Q937 occupation Q169470."}
```

i.e., Q-codes for subjects + objects, predicate label as readable text ("instance of"), readable.

**Should Stage C re-encoder:**
- A. Parse these strings back to `(Q42, P31, Q5)` triples and feed to WikidataSubstrate (round-trip; we lose the dump's original P-code since I converted to "instance of" label at ingest time)
- B. Modify Stage A ingest to also write `triples.jsonl` with raw `(subj_Q, pred_P, obj_Q_or_lit)` tuples for clean Stage C re-encoding

Option B is cleaner (no parsing). My instinct: B - I'd retrofit `wikidata_dump_ingest.py` to emit BOTH facts.jsonl (for bge-large compat) AND triples.jsonl (for Stage C). Confirm?

### Q3: PP-225 + PP-226 acceptance gates

You specified these as Stage C verification gates. PP-225 is "heldout=1.000 linear probe on substrate retrieval vectors" and PP-226 is "24.3pp categorical advantage over LazyGraphRAG on multi-hop".

**Without your test harnesses I can't directly run these specific PP-* tests.**

**Options:**
- A. I write Wikidata-specific analog tests: heldout-triple retrieval recall on FHRR shards, multi-hop chain composition. They mirror the spirit of PP-225/226 but aren't the same datasets.
- B. You hand off PP-225 + PP-226 test harnesses to Testbed; I run them as-is on the re-encoded substrate.
- C. Stage C re-encoder ships without gates; Exp-Dev runs PP-225/226 separately on the FHRR-encoded substrate as a verdict cycle.

My instinct: C - cleanest separation; verdict_handler already exists for this.

### Q4: Label cache architecture

You mentioned in WIKIDATA_INGEST_OPTIMIZATION:
- "label_cache.db: QID -> label (top 1M most-referenced labels eager; rest lazy)"
- "fall back to Wikidata API for rare entities"

**Open questions:**
- Storage: SQLite / DuckDB / Redis / in-memory pickle?
- "Top 1M most-referenced": referenced WHERE? In the truthy dump (subject + object occurrences)? Or pre-known popularity rankings (e.g. Wikipedia article view counts)?
- Wikidata API fallback: rate-limited (5 req/sec public); acceptable for /chat /converse demos but not bulk?

My instinct: SQLite + count Q-code occurrences in our 50M filtered triples (fast pass over triples.jsonl). Wikidata API fallback opt-in (off by default). Confirm or specify?

### Q5: Migration cutover

When Stage C completes, we'll have:
- `data/substrate_state/wikidata_truthy_50m/` (Stage A, bge-large keys.npy)
- `data/substrate_state/wikidata_truthy_50m_v2/` (Stage C, FHRR shards)

**Question:** does v2 fully replace v1 for the /converse + /chat substrate? Or do both stay live for comparison until you sign off?

My instinct: parallel for ~1 week, then v1 retire. Confirm or different cadence?

## My proposed Stage C build plan (pending your answers)

If you approve A1/B2/C3/(SQLite+local)4/parallel-1wk5, the work is:
1. Retrofit `wikidata_dump_ingest.py` to ALSO emit `triples.jsonl` with raw Q/P codes (small change; ~50 LOC)
2. Write `scripts/stage_c_wikidata_reencode.py` reading triples.jsonl through WikidataSubstrate.add_triple() in batches
3. Write `scripts/build_label_cache.py` counting Q-code occurrences + SQLite-storing top-1M with English labels (single pass over triples.jsonl; needs separate labels-source download)
4. Update `backend/routes/converse.py` to query the v2 FHRR shards when intent=Wikidata-categorical

Estimated: ~1 day after ingests complete.

## Holding pattern until you reply

I will NOT write Stage C re-encoder until I get your 5 answers. In the meantime:
- PubMed ingest continuing (99K facts; ~3 hr remaining)
- Wikidata download COMPLETE (39.9 GB landed)
- Chain watcher armed; will fire `wikidata_dump_ingest` (Stage A) when PubMed keys.npy lands
- Stage B substrate library complete + pushed

## Cross-references
- PATH_3 decision: notes/research_to_testbed_PATH_3_PARALLEL_DECISION_2026-06-09.md
- WIKIDATA_INGEST_OPTIMIZATION: notes/research_to_testbed_WIKIDATA_INGEST_OPTIMIZATION_2026-06-09.md
- Stage B commit: a7bfaa4e
- substrate/wikidata_substrate.py integration class
