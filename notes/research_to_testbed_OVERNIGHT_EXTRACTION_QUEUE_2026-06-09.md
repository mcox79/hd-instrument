# Research -> Testbed: overnight CPU extraction queue (parallel to GPU + Q2)

**From:** Research  **Date:** 2026-06-09 ~14:45 UTC
**Re:** User direction — Testbed should also queue overnight CPU extraction in addition to /converse build.

## Current overnight state

- **Exp-Dev:** 32 GPU anchors queued (BATCH 5) for 4060 Ti
- **Testbed Q2:** Wikipedia 100K ingest running (PID 124696; ~8hr)
- **Testbed /converse:** backend/converse/templates.py + routes/converse.py started
- **CPU bandwidth:** Q2 is dominant consumer; lightweight build work coexists fine

## Overnight CPU extraction queue (post-Q2)

Once Q2 Wikipedia 100K completes, queue these sequentially. Each writes substrate state + JSONL streaming + checkpoint resume per `experiments/_stream.py` discipline.

### EXTRACT-1: ConceptNet 8M assertions (priority 1; ~1-2 hr)
- Source: ConceptNet 5.7 CSV (already on runner OR HF download)
- Format: pre-structured triples (subject, relation, object)
- No NER needed — direct ingest
- Substrate impact: ~8M common-sense facts
- Acceptance: 8M assertions ingested + sample recall@1 ≥ 0.95

### EXTRACT-2: arXiv abstracts (priority 2; ~3-5 hr)
- Source: Kaggle arXiv dump or HF mirror
- ~2M papers; abstracts only (not full text)
- Extraction: spaCy + sciSpaCy NER for scientific entities
- Substrate impact: ~10-20M scientific facts
- Acceptance: 2M abstracts processed + sample recall@1 ≥ 0.90 on scientific queries

### EXTRACT-3: Wikidata subset (priority 3; ~5-10 hr)
- Source: Wikidata dump (~30GB compressed)
- Direct triple load (no NER; already structured)
- Filter to top-50M most-frequent triples (or full 100M if disk allows)
- Substrate impact: 50M-100M structured triples
- Acceptance: target M ingested + sample recall@1 ≥ 0.95

### EXTRACT-4 (stretch): PubMed abstracts (~10 hr)
- Source: NCBI PubMed bulk download
- ~30M biomedical abstracts
- Extraction: sciSpaCy for biomedical entities
- Substrate impact: ~100M+ medical facts
- Acceptance: 30M abstracts processed + sample recall@1 ≥ 0.90 on medical queries
- Strategic value: healthcare vertical demo asset (aligns with PP-209 DDI proof)

## Why this maximizes overnight value

**Substrate KB scales 169 facts → ~200M+ facts overnight**

This directly supports:
- Demo claim "substrate at 200M-fact scale" (categorical vs LLM context window)
- Cycle 200 healthcare vertical demo (PP-209 DDI uses substrate's biomedical knowledge)
- Multi-domain conversational capability (CONV anchors need broad KB)
- substrate-around-LLM scale story (substrate handles wider query range)

## CPU sharing strategy

| Time | Q2 | EXTRACT-1 | EXTRACT-2 | EXTRACT-3 |
|---|---|---|---|---|
| Now | Running | Queued | Queued | Queued |
| After Q2 (~+8hr) | Done | Running | Queued | Queued |
| After EXTRACT-1 (~+10hr) | Done | Done | Running | Queued |
| After EXTRACT-2 (~+13-15hr) | Done | Done | Done | Running |
| After EXTRACT-3 (~+20-25hr) | Done | Done | Done | Done |

Cleanly sequential; each blocks on prior completion. Resume capability via `_stream.py`.

## /converse build continues in parallel

Backend build is lightweight CPU; runs alongside extraction without contention.

## Acceptance gates per extraction

- 100% data ingested per source
- Sample recall@1 ≥ 0.90 per source
- Substrate state persisted via memmap (per VERIFY signoff)
- Per-shard PP-107 confidence calibrated
- Audit chain entries for each ingested fact (provenance)

## Cross-references
- BATCH 5 GPU: notes/research_to_exp_dev_BATCH_5_OVERNIGHT_GPU_2026-06-09.md
- /converse build: notes/research_to_testbed_BUILD_SUBSTRATE_CONVERSE_2026-06-09.md
- Q2 running: notes/testbed_to_research_Q2_RUNNING_what_during_2026-06-09.md
- experiments/_stream.py (Exp-Dev shipped today)
- DEMO SPEC v5: notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md

---

**Testbed:** queue EXTRACT-1/2/3 sequentially post-Q2. EXTRACT-4 PubMed is stretch
(healthcare vertical asset). Substrate scales 169 → ~200M facts overnight = categorical
demo claim "substrate at production scale."

/converse build continues in parallel (lightweight CPU; no contention).
