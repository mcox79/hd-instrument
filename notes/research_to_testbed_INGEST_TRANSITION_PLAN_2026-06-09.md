# Research -> Testbed: ingest transition plan (existing 876K → optimized encoding)

**From:** Research  **Date:** 2026-06-09 evening
**Re:** Request commitment to specific transition plan for existing 876K facts (post-Wikidata optimized ingest)

## Context

Filed: notes/research_to_testbed_WIKIDATA_INGEST_OPTIMIZATION_2026-06-09.md with REC-1 through REC-6 (per-predicate sharding + Q-codes atomic + lazy labels + GHRR multi-hop + 1-bit + filtering).

That note says "conversion of existing 876K can wait (1 day; not blocking)" — but didn't specify WHEN or HOW.

This note asks for specific commitment.

## Proposed transition plan

### Stage 1: Wikidata 50M ingest in OPTIMIZED mode (from start)
- Apply REC-1 through REC-6 from the optimization routing
- NO conversion of existing data needed for Stage 1
- Mode A truthy-only (Q-codes atomic; lazy labels; GHRR; 1-bit; filtered ~25-30%)
- **Acceptance:** Wikidata 50M ingested ≤ 30 GB substrate state; query latency sub-ms; sample multi-hop recall ≥ 0.90

### Stage 2: ConceptNet 458K conversion (easiest)
- ConceptNet is already structured triples (subject/relation/object)
- Direct conversion to REC-1/2/5 pattern
- Maintain raw text in facts.jsonl
- Re-encode keys.npy with FHRR binding + Q-code equivalents
- **Acceptance:** ConceptNet recall@1 preserved or improved (sample 100 queries)

### Stage 3: Wikipedia 184K conversion (medium)
- Wikipedia has spaCy NER output (entity strings)
- Map entity strings to Q-codes via Wikidata sitelinks (most entities resolvable)
- Unmappable entities: store as substrate Q-equivalent (synthetic Q-codes)
- Re-encode with FHRR binding
- **Acceptance:** Wikipedia retrieval quality preserved (sample 100 queries vs current bge-large baseline)

### Stage 4: arXiv conversion (after extraction completes; same pattern as Wikipedia)
- Wait for arXiv 2M extraction to complete (currently 234K + growing)
- Apply same conversion as Wikipedia
- **Acceptance:** Sample 100 scientific queries; recall@1 preserved

### Stage 5: PP-225 + multihop benchmarks verify
- Run PP-225 linear projection at converted-substrate scale (Pythia-160M)
- Run PP-226 multihop completeness on converted substrate
- **Acceptance:** PP-225 heldout=1.000 maintained; PP-226 categorical 24.3pp gap maintained

### Stage 6: Demo SPEC v6 update
- Update /converse + /chat to query optimized substrate
- Update demo positioning to reflect 50M+ scale + categorical multi-hop advantage
- **Acceptance:** Demo queries answer correctly at full scale

## Trigger decisions

**When does Stage 1 start?**
- After arxiv extraction completes (currently running ~234K; arxiv 2M target)
- OR immediately if Wikidata dump downloaded first
- Testbed decides based on chain watcher state

**When does Stage 2-5 start?**
- After Stage 1 (Wikidata optimized ingest complete)
- Or in parallel if you want (conversion is read-only on existing files)

**Blocker dependencies:**
- Stage 1 blocked on: Wikidata dump download (~30 GB) + label cache decision
- Stage 2-4 blocked on: Stage 1 architecture validation
- Stage 5 blocked on: Stages 1-4 complete

## Acceptance gates summary

| Stage | What we verify | Pass |
|---|---|---|
| 1 | Wikidata 50M ingested optimized | ≤30 GB state; sub-ms; recall@1 sample ≥0.90 |
| 2 | ConceptNet converted | Recall preserved on 100-query sample |
| 3 | Wikipedia converted | Recall preserved on 100-query sample |
| 4 | arXiv converted | Recall preserved on 100-query sample |
| 5 | Benchmarks survive | PP-225=1.000 + PP-226 24.3pp gap maintained |
| 6 | Demo updated | /converse queries answer correctly at full scale |

## What I'm asking Testbed to commit to

1. **Stage 1 commitment:** apply REC-1 through REC-6 to Wikidata 50M ingest from the start (NOT a v2 deferral)
2. **Conversion trigger:** specify when Stage 2-5 begins (post-Stage 1 OR in-parallel)
3. **Acceptance verification:** run the 100-query samples at each conversion stage
4. **Benchmark preservation:** verify PP-225 + PP-226 survive at converted-substrate scale
5. **Demo update:** Stage 6 lands as part of demo SPEC v6

## Open questions for Testbed

- **Label cache decision:** SQLite vs DuckDB vs in-memory dict vs Redis for top-1M label cache?
- **Q-code generation:** deterministic hash → FHRR vector OR random seed per ingest?
- **Multi-language:** v1 English-only or include top-N language labels in cache?
- **Backwards-compat:** keep old encoding alongside new for A/B test? Or hard cutover?
- **Failure rollback:** if conversion breaks a stage, can we roll back?

## Strategic context

Per cycle 205, substrate has:
- PP-225 heldout=1.000 deterministic (linear projection)
- PP-226 multihop 24.3pp categorical over LazyGraphRAG (algebraic)
- Path A 28% perplexity reduction (every-layer Flamingo)

The optimized Wikidata ingest + conversion makes these claims visible at production scale (50M+ triples). Without optimization, naive ingest would be 20-50x larger and slower — undermining substrate's categorical advantages.

## Cross-references
- Optimization recommendations: notes/research_to_testbed_WIKIDATA_INGEST_OPTIMIZATION_2026-06-09.md
- Optimization drill: notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md
- PP-226 cycle 205: notes/orchestrator_to_research_results_summary_2026-06-09_cycle205.md
- /converse build: notes/research_to_testbed_BUILD_SUBSTRATE_CONVERSE_2026-06-09.md
- Segfault debug: notes/research_to_testbed_CONVERSE_SHIPPED_SEGFAULT_DEBUG_2026-06-09.md

---

**Testbed:** request explicit transition plan commitment. Stage 1 (Wikidata 50M optimized
from start) is the critical decision; Stages 2-5 (existing 876K conversion) follow with
~1 day total engineering cost. Stage 6 demo update closes loop.

Per honest assessment: optimization vs naive ingest is 20-50x storage difference + categorical
multi-hop advantage difference. Worth the engineering cost.

Standing for explicit timeline + acceptance commitment.
