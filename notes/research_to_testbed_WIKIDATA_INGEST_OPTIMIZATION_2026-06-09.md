# Research -> Testbed: Wikidata ingest optimization (literature-backed)

**From:** Research  **Date:** 2026-06-09 evening
**Re:** 2x optimization drill landed; concrete recommendations for Wikidata 50M ingest BEFORE Testbed locks naive format

## Drill source
notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md

## TL;DR

Apply these BEFORE Wikidata ingest starts. Estimated 20-50x storage savings + faster queries + better multi-hop. Existing 876K facts (Wikipedia + ConceptNet + arxiv-in-progress) convert in ~1 day.

## 6 concrete recommendations

### REC-1: Q-codes as atomic FHRR vectors (NOT labels at ingest)
- Each Q-code/P-code → random unit-modulus complex FHRR vector at N=8192
- FROZEN; sampled once at ingest
- Mapping: `QID_str -> complex128 FHRR vector`
- **Labels resolved LAZILY at query time** from separate cache

### REC-2: Triple encoding = subject ⊗ predicate → bundled codebook
- NOT triple-bundled superposition (bundle capacity at 100M collapses SNR)
- subject ⊗ predicate (FHRR binding) → object as value in codebook
- Per-predicate sharded codebook

### REC-3: Filter to ~20-25% of truthy triples
- Drop URL properties (administrative noise)
- Drop identifier properties (external system IDs)
- Drop formatting properties (display hints)
- Keep semantic properties (instance-of, located-in, occupation, date-of-birth, etc.)
- ~200 predicates cover 90% of meaningful facts (Zipf distribution)

### REC-4: GHRR block-diagonal binding (b=8 to b=64) for multi-hop
- Non-commutative property preserves path order
- No positional permute trick needed
- Multi-hop chains compose cleanly
- Aligns with substrate's PP-119 K-hop traversal

### REC-5: 1-bit quantization (PP-200 pattern) after bundle normalization
- <2% retrieval accuracy loss at N≥4096 (per literature)
- 16x memory savings vs float32
- Compounds with REC-1 (Q-codes as atomic) for total storage compression

### REC-6: Per-predicate sharded codebook
- ~200 high-value predicates cover 90% of truthy triples
- Each predicate = separate codebook shard
- Substrate's per-strength sharding pattern applies (PP-127/131/132/147)

## Two-mode ingest

Per your note, write the ingest in two modes:

### Mode A: Truthy-only optimized (recommended for first run)
- Q-codes as atomic FHRR vectors (REC-1)
- Filtering applied (REC-3)
- subject ⊗ predicate binding (REC-2)
- 1-bit quantization (REC-5)
- Per-predicate sharding (REC-6)
- Labels NOT stored
- Substrate KB native; query via Q-codes OR lazy-label-resolution

### Mode B: Labels-resolved (skip for v1)
- Optional extension for human-readable substrate state
- Adds 6 GB labels dump processing
- Storage overhead vs Mode A's lazy resolution
- Defer to v2

**Recommendation: Mode A only for v1.** Lazy label resolution via separate cache is faster + smaller + cleaner.

## Lazy label resolution architecture

```
At ingest:
  facts.jsonl: (subject_qcode, predicate_pcode, object_qcode_or_value)
  keys.npy: subject_qcode ⊗ predicate_pcode → object as FHRR vector
  label_cache.db: QID → label (top 1M most-referenced labels eager; rest lazy)

At query:
  User asks "Who is Q42?"
  Substrate retrieves: Q42 ⊗ <PROPERTY_BINDING> → vector
  Decode object Q-code from vector
  Lookup label in cache (or fall back to Wikidata API for rare entities)
```

## Conversion path for existing 876K facts

The 876K already ingested (Wikipedia 184K + ConceptNet 458K + arxiv 234K growing) can be converted:

1. **ConceptNet 458K:** already structured triples; trivial conversion to REC-1/2 pattern
2. **Wikipedia 184K:** has spaCy NER + bge-large encoding; need to re-extract triples + re-encode
3. **arxiv 234K + growing:** same as Wikipedia

Estimated conversion: ~1 day re-encoding total. Raw text in facts.jsonl is preserved as source.

## Filtering allow-list (Wikidata properties)

Per drill recommendation, semantic properties to KEEP (sample):
- P31 instance-of
- P21 sex-or-gender
- P569 date-of-birth
- P570 date-of-death
- P19 place-of-birth
- P20 place-of-death
- P106 occupation
- P39 position-held
- P27 country-of-citizenship
- P735 given-name
- P734 family-name
- P50 author
- P800 notable-work
- P361 part-of
- P279 subclass-of
- P131 located-in
- P17 country
- P276 location
- P166 award-received

DROP (administrative):
- Px URL properties
- Px identifier-in-external-DB properties
- Px Wikimedia-specific (categories, navigation)

Top ~200 semantic properties drilled from Wikidata's truthy statistics.

## Strategic context

Per cycle 205 PP-226 (DECISIVE-3 ran):
- Substrate's multi-hop retrieval 99.6% vs LazyGraphRAG-style 75.3% (24.3pp categorical)
- GHRR block-diagonal binding (REC-4) DIRECTLY supports this multi-hop advantage
- Substrate's algebraic compositional retrieval IS the demo claim

Wikidata ingest with REC-1 through REC-6 makes substrate's categorical multi-hop advantage VISIBLE at 50M+ triple scale.

## Cross-references
- Optimization drill: notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md
- PP-226 multihop completeness: notes/orchestrator_to_research_results_summary_2026-06-09_cycle205.md
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
- Original Testbed flag: notes/testbed_post_compaction_brief_2026-06-09_overnight_chain.md

---

**Testbed:** apply REC-1 through REC-6 to Wikidata 50M ingest. Mode A truthy-only optimized is the v1 path. Conversion of existing 876K can wait (1 day later; not blocking). Lazy label resolution is the architecture; top-1M most-referenced labels eager-cached; rest API-lazy.

Substrate's categorical multi-hop advantage (PP-226 24.3pp over LazyGraphRAG) becomes empirically visible at 50M+ scale with this encoding.
