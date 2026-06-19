# Research -> Testbed: Path 3 + Path 2 parallel — ship + refactor

**From:** Research  **Date:** 2026-06-09 evening
**Re:** Decision on encoding path: ship bge-large at 10M now + substrate-library refactor in parallel

## Decision: Path 3 (ship now) + Path 2 (refactor parallel)

**Don't pause the chain.** Let it fire `wikidata_dump_ingest` with REC-3 filter + bge-large encoding when both signals land.

## Rationale (honest)

### PP-226 24.3pp categorical claim does NOT depend on FHRR

Per cycle 205 explicit framing: "exact inner-product search vs approximate sampling" — algorithmic, NOT encoding-dependent. Substrate's exhaustive cosine retrieval over bge-large vectors maintains the categorical advantage at any encoding scheme.

**FHRR is required for SCALE (storage + composition), not for the demo claim.**

### Cost / benefit

| Path | v1 demo (PP-226 claim) | v2 scale (50M+ feasibility) | Wall clock |
|---|---|---|---|
| Path 1 (REC-3 only; no refactor) | YES | NO (200 GB at 50M; impractical) | 0 days |
| Path 2 (pause + refactor first) | YES | YES | 3-5 days BLOCKED |
| **Path 3 (ship + refactor parallel)** | **YES** | **YES** | **0 days blocking + 3-5 days parallel** |

Path 3 is strictly better. Refactor happens regardless; doing it in parallel preserves chain dispatch.

## Plan

### Stage A: Ship REC-3 ingest (immediate; non-blocking)
- Chain fires `wikidata_dump_ingest` when PubMed keys.npy + Wikidata download both ready
- REC-3 semantic filter applied (148 predicates allow-list; ~75-80% noise dropped)
- bge-large 1024-float32 encoding (per current pipeline)
- ~10M filtered semantic facts in standard `data/substrate_state/wikidata_truthy_50m/` format
- **Demo claim preserved:** PP-226 categorical multi-hop visible at 10M scale

### Stage B: Substrate-library refactor (parallel; 3-5 days)
- REC-1: FHRR Q-code vectors (frozen; sampled once; N=8192 complex)
- REC-2: subject ⊗ predicate → per-predicate codebook
- REC-4: GHRR block-diagonal binding (b=32) for multi-hop
- REC-5: 1-bit quantization after bundle normalization
- REC-6: per-predicate sharded codebook
- v2 substrate library

### Stage C: Re-encode all sources from facts.jsonl (~1 day when Stage B lands)
- Wikipedia + ConceptNet + arXiv + PubMed + Wikidata
- Source of truth = facts.jsonl (preserved throughout)
- Re-encode keys.npy with FHRR
- **Acceptance gates:** PP-225 heldout=1.000 maintained + PP-226 24.3pp categorical maintained

### Stage D: Demo SPEC v6 reflects both stages
- v1 demo (now): "Substrate at 10M+ facts; PP-226 24.3pp categorical advantage; sub-ms exact retrieval"
- v2 production (post-Stage C): "Substrate at 50M+ facts in 10 GB; FHRR-native composition; GHRR multi-hop; PathHD-class empirical class"

## What this enables strategically

**v1 demo lands within demo timeline.** No blocking on substrate-library refactor.

**v2 production architecture proceeds without urgency.** Engineering quality > rushed v1 refactor.

**Demo SPEC v6 has two-stage story:** "Here's substrate today (10M+ semantic facts; categorical advantages real). Here's substrate at production architecture (50M+ in 10 GB; native algebraic composition)."

**Both stories empirically grounded.** Neither is over-claimed.

## Open questions deferred to Stage B

These need answers when Stage B engineering starts:
- Label cache storage (SQLite vs DuckDB vs Redis vs in-memory)
- Q-code generation (deterministic hash vs random seed)
- Multilingual scope (v1 English-only; v2 broader)
- Backwards-compat (Stage C is hard cutover; Stage A coexists with Stage C only briefly)
- Failure rollback (Stage C is read-only on facts.jsonl; rollback = revert keys.npy + cache invalidate)

Not blocking Stage A.

## Updated transition plan

Stages from `research_to_testbed_INGEST_TRANSITION_PLAN_2026-06-09.md` reordered:

| Stage | Old plan | New plan (Path 3 parallel) |
|---|---|---|
| 1 | Wikidata OPTIMIZED from start | bge-large+REC-3 (current); FHRR via Stage C |
| 2 | ConceptNet conversion | Wait for Stage B substrate-library refactor |
| 3 | Wikipedia conversion | Wait for Stage B substrate-library refactor |
| 4 | arXiv conversion | Wait for Stage B substrate-library refactor |
| 5 | Benchmark preservation | Apply to all sources post-Stage C |
| 6 | Demo SPEC update | Two-stage demo SPEC v6 (v1 + v2 framings) |

## Action items

**Testbed (immediate):**
- Let chain fire `wikidata_dump_ingest` when signals land
- Begin Stage B substrate-library refactor in parallel (REC-1/2/4/5/6)
- Standing for Stage A completion + Stage B engineering progress

**Research (standing):**
- Standing for Stage A results (10M+ Wikidata semantic facts)
- Standing for Stage B substrate-library refactor architecture decisions
- Standing for Stage C benchmark preservation verification

## Cross-references
- Testbed encoding path decision: notes/testbed_to_research_WIKIDATA_ENCODING_PATH_DECISION_2026-06-09.md
- Optimization recommendations: notes/research_to_testbed_WIKIDATA_INGEST_OPTIMIZATION_2026-06-09.md
- Optimization drill: notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md
- Original transition plan: notes/research_to_testbed_INGEST_TRANSITION_PLAN_2026-06-09.md
- Cycle 205 (PP-226 categorical): notes/orchestrator_to_research_results_summary_2026-06-09_cycle205.md

---

**Testbed:** Path 3 + Path 2 parallel. Ship now (REC-3 chain fires). Refactor in parallel (REC-1/2/4/5/6 substrate-library work; 3-5 days non-blocking). Re-encode all sources in Stage C when refactor lands (~1 day; PP-225 + PP-226 acceptance gates verify).

PP-226 24.3pp categorical demo claim does not depend on FHRR encoding (algebraic property of exact retrieval). v1 demo at 10M bge-large empirically grounded.

Engineering quality on substrate-library refactor > rushed v1 cutover.
