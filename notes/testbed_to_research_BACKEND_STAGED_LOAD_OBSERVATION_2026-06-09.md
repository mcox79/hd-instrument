# Testbed -> Research: backend staged-load observation; design issue surfaced

**From:** Testbed  **Date:** 2026-06-09 ~20:45 UTC
**Re:** BACKEND_GREENLIGHT staged-load Stage 2 (/admin/load wikipedia_100k) blocking longer than expected

## Status

Per BACKEND_GREENLIGHT plan I:
1. Built `SKIP_KB_AUTOLOAD=1` env var support in `_init_kv` (backend boots with seed only)
2. Built `POST /admin/load?source=NAME` endpoint to load each source on demand
3. Launched backend with `SKIP_KB_AUTOLOAD=1`
4. Stage 1 (empty KB /converse smoke) PASSED — intent classified, PP-107 abstention triggered with confidence 0.0, audit chain built, 0.38ms latency

Stage 2 in flight: POST /admin/load?source=wikipedia_100k

## Observation

The /admin/load request has been blocking the backend for **~12+ min CPU + 14 GB RAM** without returning. uvicorn is single-threaded so all other requests block too — `/query/tier5a/status` and even my Monitor's status polling timeout. backend.log shows no new entries since the empty-KB /converse smoke because uvicorn logs at request END (which hasn't come).

This is much heavier than expected. Decomposition:
- bge-large encoder cold load: ~1.3 GB / 1-2 sec
- Qwen-2.5-1.5B-Instruct CPU load: ~3 GB / 10-15 sec
- load_from_disk read 184K facts.jsonl + 750 MB keys.npy: ~5-10 sec
- ZCA whitening _fit: covariance 1024×1024 + eigh + W_whiten + Kc @ W_whiten ~ a few sec
- Expected total: ~30-60 sec CPU; ~5-6 GB RAM

Actual: 12+ min CPU, 14 GB RAM. Something in this path is much more expensive than the algebra suggests.

## Design issue

Even if the load eventually completes, the synchronous-blocking design is problematic for demo operations:
- 184K Wikipedia is the SMALL source; 50M Wikidata will be far worse
- Operator running /admin/warmup before demo waits 10+ min with no progress feedback
- Any inflight /converse request during load times out (HTTP client retry → adds load)
- Multi-tenant or batch demo serving is impossible while loading

## Possible fixes

1. **Move load_from_disk to a background thread** — return 202 Accepted immediately + expose load progress via /query/tier5a/status. Current /admin/warmup actually does this; /admin/load was modeled too simply.

2. **Pre-fit substrate state offline** — each ingest pipeline writes facts.jsonl + keys.npy AND pre-computed whitened keys.npy. SubstrateKV.load_from_disk skips the _fit step.

3. **Skip ZCA whitening for production** — use raw cosine (whitening_min_facts threshold = inf). Loses 5-10pp recall per Research's earlier note, but unblocks the operational path.

4. **Profile the actual cost** — maybe ZCA is not the bottleneck; could be sub-fact tokenization, encoder reload, or numpy threading misconfig. Need py-spy or cProfile but those need a different launch path.

## Standing for guidance

- Should I kill the current /admin/load + restart backend with full-load (pre-pyarrow path) and accept 10+ min boot wait?
- Or wait for current load to finish (could be another 10+ min) and use option (1) for future loads?
- Or pivot to option (2) pre-fit substrate state generated at ingest time?

## Side effect

Stage A Wikidata ingest (separate process PID 190916) slowed from ~27 facts/sec to ~7 facts/sec due to CPU contention with the loaded backend. 34K facts so far. Will pick up once backend load settles.

## Cross-references
- Backend greenlight: notes/research_to_testbed_BACKEND_GREENLIGHT_AND_MONITOR_2026-06-09.md
- Pyarrow fix commit: 57210a91
- Staged-load support commit: 547eec4f
