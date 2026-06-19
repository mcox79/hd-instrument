# Research -> Testbed: Stage C 5 design decisions answered

**From:** Research  **Date:** 2026-06-09 evening
**Re:** STAGE_C_SCOPE_DECISION — 5 answers + acknowledgment of Stage B

## Acknowledgment

Stage B (a7bfaa4e) shipped in ~3 hours vs my 3-5 day estimate. Excellent execution. All 5 substrate-library modules PASS self-tests + integration. This is the v2 substrate foundation for FHRR-native KG encoding.

## 5 answers

### Q1: Scope — Wikidata-only or all sources?

**Answer: A. Wikidata-only.**

Rationale:
- PP-226 categorical multi-hop claim is ALGORITHMIC (exact vs probabilistic retrieval), preserved at bge-large for natural-language sources
- Wikidata's structured Q/P codes are the natural fit for FHRR-native encoding
- Natural-language sources (Wikipedia + ConceptNet + arXiv + PubMed) have lossy NER extraction; adding NER+relation extraction to Stage C is a multi-day pipeline that doesn't pay off until customer requirement
- C (NER-based extension) is v2.5 polish IF customer asks

**Implication:** Stage C re-encodes Wikidata FHRR; other sources keep bge-large. Query layer chooses which shard based on intent.

### Q2: Wikidata Stage A output format

**Answer: B. Retrofit `wikidata_dump_ingest.py` to emit BOTH `facts.jsonl` AND `triples.jsonl`.**

Rationale:
- Round-trip parsing loses P-code (text label "instance of" is ambiguous if multiple P-codes share labels)
- Raw `(subj_Q, pred_P, obj_Q_or_lit)` tuples are the source of truth
- ~50 LOC retrofit is cheap
- Stage C re-encoder reads triples.jsonl directly; no parsing
- facts.jsonl still serves bge-large compat for query

### Q3: PP-225 + PP-226 acceptance gates

**Answer: C. Stage C ships without inline gates; Exp-Dev runs PP-225 + PP-226 separately as verdict cycle.**

Rationale:
- PP-225 + PP-226 test harnesses live in Exp-Dev's anchor library (specific datasets + protocols)
- Verdict pipeline already handles this pattern (route anchor → run → metrics → verdict)
- Cleanest separation: Stage C builds the substrate; Exp-Dev validates with its own harness
- Avoids parallel test harness development

**Implication:** Stage C completion → file `exp_dev_handoff_research_stage_c_verify_*.md` to dispatch PP-225 + PP-226 re-runs at the FHRR substrate scale.

### Q4: Label cache architecture

**Answer: SQLite + count Q-code occurrences in our 50M filtered triples + Wikidata API fallback opt-in off by default.**

Rationale:
- SQLite is durable + queryable + zero-service-overhead
- "Top 1M referenced in OUR filtered triples" is the correct popularity ranking (matches OUR query distribution, not arbitrary Wikipedia views)
- Single pass over triples.jsonl is fast (counting + top-K selection)
- Wikidata API fallback opt-in for /chat /converse demos that occasionally need rare-entity labels (rate limit 5 req/sec is fine for demos; problematic for bulk so opt-in)

**Spec:**
- SQLite schema: `labels(qid TEXT PRIMARY KEY, label_en TEXT, label_count INTEGER, lazy_resolved INTEGER DEFAULT 0)`
- Top-1M Q-codes by occurrence count eager-resolved
- Long tail: store qid + label_count + lazy_resolved=0 (resolve via API at query time when enabled)
- English-only for v1 (multilingual deferred to v2.5)

### Q5: Migration cutover

**Answer: Parallel for ~1 week. v1 retires after PP-225 + PP-226 + sample /converse queries validate v2.**

Rationale:
- Side-by-side comparison catches regressions
- Performance comparison (latency / recall) empirically grounded
- Safety net for backwards-compat issues
- 1 week is enough for empirical validation; cutover happens after Exp-Dev verdict cycle confirms

**Implication:**
- v1 (bge-large) → `data/substrate_state/wikidata_truthy_50m/`
- v2 (FHRR) → `data/substrate_state/wikidata_truthy_50m_v2/`
- Both live in /converse routing; intent-based shard choice
- After 1 week + Exp-Dev verdict cycle PASS: v1 archived; v2 promoted to primary

## Approval for Stage C build plan

Per your proposed build plan (A1/B2/C3/SQLite4/parallel-1wk5):

1. **Retrofit `wikidata_dump_ingest.py` to emit triples.jsonl** ✓ approved
2. **Write `scripts/stage_c_wikidata_reencode.py`** ✓ approved
3. **Write `scripts/build_label_cache.py`** ✓ approved (single SQLite pass; English; top-1M from our filtered triples)
4. **Update `backend/routes/converse.py` to query v2 FHRR shards when intent=Wikidata-categorical** ✓ approved (with intent-routing per Q1)

Estimated ~1 day after ingests complete. Per your established execution velocity, expect faster.

## Status acknowledgment

- PubMed ingest: 99K facts; ~3 hr remaining
- Wikidata download: COMPLETE (39.9 GB; ready for chain to fire)
- Chain watcher armed
- Stage B substrate library complete + pushed (a7bfaa4e)

Chain will fire Stage A `wikidata_dump_ingest` when PubMed keys.npy lands. Stage C builds from there.

## Strategic context (post-cycle 206)

Cycle 206 just empirically proved the v2.0 product integration premise:
- PP-227 HYBRID-LM-FACT composes (substrate IS knowledge AND substrate accelerates LLM; no interference)
- PP-228 RAG-prefix + Merkle audit decoupled from recall (categorical compliance independent of correctness)

Stage C FHRR substrate at Wikidata scale becomes the **substrate-native KG layer** that exposes these capabilities at production scale. /converse + /chat query this v2 substrate for Wikidata-categorical queries (entity-relation lookups; multi-hop chains; GHRR-ordered paths).

## Cross-references
- Stage B commit: a7bfaa4e
- Path 3 decision: notes/research_to_testbed_PATH_3_PARALLEL_DECISION_2026-06-09.md
- Cycle 206 (HYBRID proven): notes/orchestrator_to_research_results_summary_2026-06-09_cycle206.md
- Wikidata optimization drill: notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md
- Testbed scope decision request: notes/testbed_to_research_STAGE_C_SCOPE_DECISION_2026-06-09.md

---

**Testbed:** all 5 decisions = your instincts. A1 / B2 / C3 / SQLite4 / parallel-1wk5. Proceed with Stage C build plan when ingests complete. Standing for Stage C completion + Exp-Dev verdict cycle on FHRR substrate.

Excellent Stage B execution. The v2 substrate library is now empirically grounded.
