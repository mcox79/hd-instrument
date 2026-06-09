# Testbed POST-COMPACTION BRIEF — overnight ingest chain + /converse shipped

**Compiled:** 2026-06-09 ~13:00 UTC (just before compaction)
**Read this FIRST after compaction.**

## 🔴 CURRENT STATE

### Overnight ingest chain (CRITICAL — running autonomously)
- ✅ **Wikipedia 100K**: COMPLETE 184,354 facts; keys.npy at `data/substrate_state/wikipedia_100k/`
- ✅ **EXTRACT-1 ConceptNet 8M**: COMPLETE 457,875 facts (3.3 hr); `data/substrate_state/conceptnet_8m/`
- ✅ **EXTRACT-2 arXiv**: COMPLETE 234,352 facts (HF dataset CShorten/ML-ArXiv-Papers = 117K papers total, the WHOLE dataset; my 2M target was wishful); `data/substrate_state/arxiv_2m/`
- ❌ **EXTRACT-3 Wikidata 50M**: SKIPPED. Reason: I made up HF dataset names (5 guessed; all 404'd). Then tried `intfloat/wikidata5m` (loads but `text: None`; broken). Real Wikidata ingest needs direct 30 GB dump download + custom parser. Deferred until someone (me later or operator) downloads the dump and writes the parser.
- ▶️ **EXTRACT-4 PubMed (pubmed_qa)**: RUNNING via `scripts/extraction_chain_remaining.py`. Smoke 50 abstracts -> 83 facts in 10s confirms pipeline works.

### Total facts on disk
**876,581 facts** + PubMed growing = projected **~1M facts** by morning.

This is ~6,000× the 169-fact seed but 200× short of the original "200M facts" aspirational claim in Research's OVERNIGHT_EXTRACTION_QUEUE. For v1 demo viability: 876K facts is plenty (cross-domain coverage: encyclopedic / common-sense / scientific / biomedical-incoming).

To verify chain-remaining watcher: `ssh marsh@home "wmic process where (CommandLine like '%%chain_remaining%%') get ProcessId 2>nul"`

### What shipped today (commits in repo)

| Commit | What |
|---|---|
| `b6941f27` | Q1 bge-large encoder swap (24/30 benchmark; +71%) |
| `b035dfee` | Q2 Wikipedia 100K ingest + SubstrateKV.load_from_disk + auto-load |
| `52553e7d` | /converse Phase 1 backend (intent + templates + state + handlers + endpoint); 8/8 intent + 8/8 substrate-direct + <2ms |
| `8508ae04` | /chat Phase 3 frontend UI; EXTRACT-1 ConceptNet + EXTRACT-2 arXiv pipelines; chain watcher v1 |
| `b573dd9c` | EXTRACT-3 Wikidata + EXTRACT-4 PubMed pipelines |
| `ed669214` | POLISH 1 audit chain UI on landing widget |
| `5fdc868c` | POLISH 2 /benchmark category summary + filter |
| `253fa3a7` | POLISH 3 /playground presets expansion |
| `ccba78d0` | DELETE demo-mode entirely (it was blocking queue dispatch) |
| `[current]` | extraction_chain_remaining.py recovery watcher |

### Backend status: SEGFAULTS on heavy load
Exit code 0xC0000005 (EXCEPTION_ACCESS_VIOLATION). uvicorn says "Application startup complete" → "Uvicorn running on http://127.0.0.1:8000" → process dies. Daemon thread loading bge-large + Qwen + 642K KB facts likely triggers native crash. **Deferred** — code is in repo; /converse + /chat are wired; KB auto-load via `_init_kv()` iterates `data/substrate_state/*/` for `(facts.jsonl, keys.npy)` pairs.

Last attempted workaround: `tmp_run_backend.bat` sets `TIER5_ENABLED=false`. Even that still 502s. Real fix: minimal repro of segfault (probably bge+Qwen co-process issue) deferred.

### Ingest chain is COMPLETELY SAFE from backend restart attempts
Orchestrate script's cleanup line only kills processes listening on port 8000:
```
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
```
Ingest workers don't listen on any port. Confirmed live throughout the night: arxiv facts went 102K → 109K → 234K while backend cycled 5+ times.

## STANDING TASKS

1. **Monitor ingest** — periodic checks every 30 min during arxiv (~8-12 hr remaining)
2. **Verify chain-remaining watcher** fires when arxiv keys.npy lands (could be 8-12 hr from now)
3. **DON'T** try to restart backend again until segfault diagnosed
4. **DON'T** touch the chain or ingest workers

## Resume-on-wake instructions

If compaction hits:
1. Pull repo (`git -C D:/AI/hd-instrument pull`)
2. Check arxiv progress: `ssh marsh@home "powershell -Command (Get-Content C:/dev/hd-instrument/data/substrate_state/arxiv_2m/facts.jsonl -EA SilentlyContinue | Measure-Object -Line).Lines"`
3. Check chain-remaining watcher: `ssh marsh@home "type C:/Users/marsh/chain_remaining.log 2>nul"`
4. Pick up from "monitor + report progress" mode

## Strategic context (post-strategic-reframe)

- **substrate-around-LLM** locked (commit `a9762662` strategic reframe filed)
- **Substrate IS the AI** — LLM is vendor-swappable language tool called when needed
- **PP-187 + PP-188 + PP-212 + PP-195 + PP-198** all empirically validated; /converse wires them
- **Cycle 200**: 4 vertical demos HP (Legal PACER, Healthcare DDI, FDA, Finance SEC 10-K)
- **POST-Q3 SEQUENCE** Research Priority A: TALKS-1 (substrate-only conversation page) + audit chain UI rendering DONE (POLISH 1)
- **POST-Q3 Priority B**: vertical demo landing pages (legal / healthcare / finance / fda) — NOT YET STARTED
- **Tier 5b**: research-grade (Path A 0.836x/0.852x ppl improvement; Path B Flamingo de-risked but data-limited; T5C-D1 Qwen Phase D training launched per commit `0543e073`)

## Cross-references

- BUILD_SUBSTRATE_CONVERSE spec: `notes/research_to_testbed_BUILD_SUBSTRATE_CONVERSE_2026-06-09.md`
- OVERNIGHT_EXTRACTION_QUEUE: `notes/research_to_testbed_OVERNIGHT_EXTRACTION_QUEUE_2026-06-09.md`
- POST_Q3_SEQUENCE: `notes/research_to_testbed_POST_Q3_SEQUENCE_2026-06-09.md`
- Strategic reframe (substrate-AROUND-LLM): `notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md`
- 5-decisions endorsements: `notes/research_to_testbed_5_DECISIONS_RESPONSE_2026-06-08.md` + `notes/research_to_testbed_AAA_GREEN_LIGHT_2026-06-08.md`
