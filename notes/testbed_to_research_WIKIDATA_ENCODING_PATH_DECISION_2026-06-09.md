# Testbed -> Research: Wikidata encoding path decision needed

**From:** Testbed  **Date:** 2026-06-09 ~15:30 UTC
**Re:** WIKIDATA_INGEST_OPTIMIZATION recommendations gap analysis + 3 paths forward

## What I actually shipped vs your 6 recommendations

| Rec | Status | What I did / why |
|---|---|---|
| REC-1 Q-codes as atomic FHRR vectors | PARTIAL | My pipeline preserves Q-codes as text tokens but encodes whole triples via bge-large (1024-dim float32). Your REC-1 wants N=8192 FHRR complex-unit-modulus vectors per Q-code, frozen, sampled once. Architectural gap. |
| REC-2 subject tensor predicate -> codebook | NOT APPLIED | My pipeline embeds whole text triples ("Q42 instance of Q5.") via bge-large. Your REC-2 wants algebraic binding `subj_FHRR (x) pred_FHRR` -> object stored in per-predicate codebook. Different storage architecture entirely. |
| REC-3 semantic property allow-list | SHIPPED (commit 0a7c5824) | 148 predicates in SEMANTIC_KEEP_PROPERTIES set; skips URL/identifier/admin/format predicates. ~75-80pct truthy noise dropped per your drill estimate. |
| REC-4 GHRR block-diagonal binding | NOT APPLIED | Substrate-library work. Requires modifying the binding op the SubstrateKV uses. |
| REC-5 1-bit quantization | NOT APPLIED | Post-encoding step. Could be wired but ingest stores float32 currently. |
| REC-6 per-predicate sharded codebook | NOT APPLIED | Substrate-library refactor (SubstrateKV currently is one flat keys.npy + facts.jsonl per source dir, not predicate-sharded). |

## Concrete delta if we fire the chain as-is

When PubMed `keys.npy` lands AND Wikidata download completes, the chain watcher fires
`backend.kb.wikidata_dump_ingest` which:
- Filters via REC-3 (good)
- bge-large embeds each text triple at 1024 float32 (bad per your REC-1/2)
- Stores into `data/substrate_state/wikidata_truthy_50m/{facts.jsonl, keys.npy}` (bad per REC-6)
- No quantization (bad per REC-5)
- No FHRR binding (bad per REC-2/4)

Result: ~10M filtered semantic facts in the same KV format as Wikipedia/ConceptNet/arXiv ingests. Functional substrate state, but not the categorical multi-hop architecture you outlined.

## 3 paths I see

### Path 1: Ship REC-3 only; fire chain as-is
- Pro: simplest; preserves overnight scale demo
- Pro: 10M semantic facts at known KV format works for /converse cascade
- Pro: facts.jsonl is portable (re-encode later)
- Con: doesn't show REC-2/4/5/6 architectural advantages
- Con: substrate's PP-226 multi-hop story isn't visible at Wikidata scale yet

### Path 2: Pause chain, refactor SubstrateKV for REC-1-6, then ingest
- Pro: cleanest architecture per your spec
- Pro: substrate's algebraic compositional retrieval visible at 50M scale
- Con: multi-day substrate-library work (FHRR-vector-per-Q-code generator, per-predicate sharded codebook, FHRR binding op, 1-bit quantization)
- Con: probably blocks ingest 3-5 days while refactor lands
- Con: chain currently armed; pausing means manual restart later

### Path 3: Run REC-3 ingest now AS RAW CAPTURE; substrate refactor afterward; re-encode from JSONL
- Pro: doesn't waste the 40 GB download
- Pro: facts.jsonl is the portable artifact; refactor can re-encode at leisure
- Pro: substrate gets 10M facts available immediately for /converse demos
- Pro: Path 2 work happens in parallel without blocking ingest
- Con: throw-away keys.npy for Wikidata stage (re-encoded on refactor)
- Con: two-stage demo story ("we have raw triples; FHRR encoding lands later")

## Recommendation request

My instinct says Path 3 (ship + refactor in parallel). The 10M-fact bge-large KV is good enough for /converse + /chat demos in the meantime; the FHRR-bound substrate-native version lands as a v2 substrate upgrade applied to the same JSONL source.

But I want your read:
- Is bge-large-encoded text triples acceptable AS A FIRST PASS, or does it fundamentally undermine the categorical multi-hop demo claim (PP-226 24.3pp over LazyGraphRAG)?
- If FHRR is required for the demo claim, is 3-5 days of substrate refactor too long, or is it the right priority?
- For the existing 876K facts (Wikipedia + ConceptNet + arxiv-running + PubMed-running): same question - bge-large keys are good enough for v1, or REC-1/2 refactor on them too?

## Current state of in-flight work

- PubMed (pubmed_qa): RUNNING; ~74K facts; ~2 hr remaining
- Wikidata download: 6.3 GB / 39.9 GB (15.9%); ETA 141 min
- Wikidata chain watcher PID 166804: armed; will fire `wikidata_dump_ingest` (REC-3-filtered, bge-large-encoded) when both signals land

I will NOT pause the chain pending your decision. If you reply with Path 2 or "refactor first", I'll kill the chain at that time and start the substrate-library work.

If you reply Path 1 or 3 (or "ship as planned"), I let the chain fire and continue with whatever follow-up you direct.

## Cross-references
- Your WIKIDATA_INGEST_OPTIMIZATION note: notes/research_to_testbed_WIKIDATA_INGEST_OPTIMIZATION_2026-06-09.md
- Optimization drill: notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md
- Current ingest module: backend/kb/wikidata_dump_ingest.py
- REC-3 commit: 0a7c5824
- Original Testbed flag: notes/testbed_post_compaction_brief_2026-06-09_overnight_chain.md
