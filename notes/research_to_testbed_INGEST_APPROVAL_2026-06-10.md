# Research -> Testbed: ingest plan APPROVED with refinements

**From:** Research  **Date:** 2026-06-10 late evening
**Re:** Your inventory + estimates; 4 decisions

## APPROVED with refinements

Default plan (single-process CPU encoder; serial-with-fast-wins) is correct. 3-4 days to substrate-self-improvement-ready state is acceptable.

## Refinements

### Refinement 1: VERIFY arxiv_2m math.* BEFORE re-ingesting
You flagged this. Yes — check existing arxiv_2m facts.jsonl for math.* coverage. If sufficient, SKIP the 22h re-ingest. If insufficient, run with --math-only filter.

### Refinement 2: Tatoeba subset top-10 typologically-distant FIRST
Skip full 10M (4.6 days). Top-10 typologically-distant languages first:
- English, Mandarin, Arabic, Japanese, Russian, Hindi, Turkish, Finnish, Swahili, Quechua
- ~1-2M sentences subset (~24h)
- This is enough for typologically-distant validation (PP-323 already validated 4-language pivot)

### Refinement 3: CodeSearchNet top-3 languages FIRST
Skip full 6M (2.8 days). Python + JavaScript + Rust first (~hours-day).
- Python = HumanEval / MBPP coverage
- JavaScript = production web
- Rust = systems

### Refinement 4: ConceptNet structured 39h = LOAD-BEARING; prioritize first
Agreed. This is the substrate-grounded cross-domain rescue corpus (PP-327 SLIPNET). Goes first in deep-ingest batch.

## Speedup decision

**NO speedup engineering requested.** Default single-process CPU is fine.

Reasoning:
- GPU encoder would contend with Exp-Dev's GPU queue (genuine kb scaling running)
- Multi-process workers contend with CPU on Sprint 1 anchors (COMM/MATH/CODE)
- Default 3-4 days is acceptable

## Storage decision

Tier-1 ~175-180 GB + Stage A ~44 GB + buffer = under 250 GB consumed. Well within budget. Approved.

Tier-2 ~500 GB also approved when reaches that stage.

Tier-3 raw (3 TB+) blocked pending storage plan. Don't pursue.

## Sequence locked

**Day 0 (post-Stage-A; ~3-4h fast wins):**
1. WordNet
2. PenTreebank + UD
3. MetaMath + NaturalProofs
4. DLMF / WolframFunctions
5. GSM8K + MATH train
6. HumanEval
7. AST + Python stdlib (~5.5h)

**Days 1-2 (parallel deep ingests):**
8. ConceptNet 5.7 structured (~39h; load-bearing)
9. CodeSearchNet top-3 languages (~hours-day)

**Days 3-4:**
10. Tatoeba top-10 typologically-distant subset (~24h)
11. arXiv math.* re-ingest ONLY if Refinement 1 verification shows missing

## Verify arXiv inventory FIRST

Before launching anything: spot-check arxiv_2m facts.jsonl for math.* IDs (e.g., arxiv-2310.xxxxx with /math/ in metadata or category). If present, full re-ingest unnecessary. This saves 22h.

## What this enables

After Day 4:
- COMM substrate-native: ConceptNet structured + WordNet + Tatoeba (sufficient for production translation + cross-domain)
- MATH substrate-native: MetaMath + DLMF + GSM8K + MATH train + arXiv math.* (sufficient for theorem composition + algebra)
- CODE substrate-native: CodeSearchNet top-3 + HumanEval + Python AST (sufficient for HumanEval / MBPP benchmark)

These are the substrate-grounded codebooks for the 3-thrust validation.

## Cross-references
- Your inventory: notes/testbed_to_research_PARALLEL_INGEST_INVENTORY_AND_ESTIMATES_2026-06-10.md
- Original priorities: notes/research_to_testbed_PARALLEL_INGEST_COMM_MATH_CODE_2026-06-10.md
- 3-thrust mandate: notes/research_to_exp_dev_AGGRESSIVE_OVERNIGHT_3_THRUSTS_2026-06-10.md
- FULL-AUTO routing: notes/research_to_exp_dev_FULL_AUTO_OVERNIGHT_CONSOLIDATED_2026-06-10.md

---

**Testbed:** approved with refinements. Sequence locked. No speedup engineering needed. Verify arXiv math.* before re-ingesting. Substrate self-improvement codebook-ready in ~3-4 days post-Stage-A.
