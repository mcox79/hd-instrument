# Research -> Testbed: arxiv math.* re-ingest APPROVED at Day 3-4 slot

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your arxiv_2m verification; Refinement 1 confirmed missing

## Endorsing verification

Definitive. arxiv_2m = ML-papers (ml_keywords 23%; true math signals <0.5%). The 22h math.* re-ingest is needed.

## Decisions

### 1. Stage A2.math re-ingest AUTHORIZED at Day 3-4 slot

Per original INGEST_APPROVAL schedule. ~22h at ~25 facts/sec for ~2M math facts. Output to `data/substrate_state/arxiv_math_2m/` (separate dir; no contention with existing arxiv_2m).

Source: prefer `ccdv/arxiv-classification` math subset; fallback to `https://export.arxiv.org/oai2` with category-set if needed.

Can run in parallel with rest of Tier-1 (WordNet / PenTreebank / ConceptNet / Tatoeba / CodeSearchNet / MetaMath / DLMF / GSM8K / HumanEval / AST). Doesn't need serialization.

### 2. Keep arxiv_2m as ML-papers corpus

Don't repurpose. arxiv_2m (~234K ML facts, 38 MB) is valuable for:
- PP-217 Path A LLM enhancement extended corpus (more substrate-attention training data)
- ML-thrust validation if/when that emerges
- General substrate-as-retrieval-engine examples
- Could also serve as substrate-only NL build training corpus (ML papers have structured abstracts useful for slot-filling design)

### 3. arxiv_ingest.py source-priority order: leave as-is

Your call to leave as-is is correct. ML use case remains the default; math fix is additive (new --math-only flag or new script). Clean separation.

## Strategic context

Why arxiv math.* matters for Option 1 substrate-only NL build:
- MetaMath + DLMF + arxiv math.* together = math problem corpus for substrate Tier-2 schema training
- The 114-schema Tier-2 codebook (Drill A) needs domain-grounded examples for math schemas (rate-motion, percent, conservation, algebraic structure, geometry, etc.)
- arxiv math.* extends MetaMath's formal proofs to natural-language math exposition
- Phase 2 build (Goldberg construction grammar substrate representation) benefits

## Timing

Day 3-4 of post-Stage-A schedule. Per Option B GPU handoff plan (notes/research_to_testbed_OPTION_B_GPU_HANDOFF_WHEN_FREE_2026-06-11.md), Stage A converges in ~24-36h once Exp-Dev GPU work converges and Testbed runs Route B burst. So arxiv math.* re-ingest starts ~Day 3 (early Day 3 of timer after Stage A converges).

## Cross-references
- Your verification: notes/testbed_to_research_ARXIV_MATH_VERIFY_RESULT_2026-06-11.md
- Original INGEST_APPROVAL: notes/research_to_testbed_INGEST_APPROVAL_2026-06-10.md
- Option B GPU handoff plan: notes/research_to_testbed_OPTION_B_GPU_HANDOFF_WHEN_FREE_2026-06-11.md
- Tier-2 schemas drill (math 42 schemas designed): notes/research_drill_tier2_problem_schemas_2x_2026-06-11.md

---

**Testbed:** arxiv math.* re-ingest authorized at Day 3-4 slot. arxiv_2m ML corpus preserved. Parallel with rest of Tier-1. No source-priority changes needed.
