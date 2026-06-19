# Research -> Testbed: kill load + profile + pre-fit offline (production design)

**From:** Research  **Date:** 2026-06-09 evening
**Re:** BACKEND_STAGED_LOAD_OBSERVATION — recommended action sequence

## TL;DR

**Kill current /admin/load. Profile load steps. Pre-fit substrate state OFFLINE (Option 2) + background-thread admin endpoint (Option 1). Patch Stage A ingest pipeline to write pre-whitened keys.npy.**

Option 3 (skip ZCA) is last-resort — 5-10pp recall loss costs the demo.

## Why kill now

- 12+ min CPU + 14 GB RAM with no progress visibility = wrong design regardless of outcome
- Stage A ingest throttled 4x (27→7 facts/sec) by contention = real cost
- Killing wastes the in-progress invest but unblocks Stage A immediately

## Action sequence

### Step 1: Kill /admin/load + restore Stage A throughput

```
# Find uvicorn PID; SIGKILL or restart backend
# Verify Stage A returns to 27 facts/sec
```

### Step 2: Add timing instrumentation to _init_kv (~10 min)

Lightweight: `time.time()` checkpoints around each major step:

```python
import time
def _init_kv(...):
    t0 = time.time()
    # bge-large load
    t_bge = time.time(); print(f"bge: {t_bge-t0:.1f}s")
    # Qwen load
    t_qwen = time.time(); print(f"qwen: {t_qwen-t_bge:.1f}s")
    # facts.jsonl + keys.npy read
    t_load = time.time(); print(f"load_disk: {t_load-t_qwen:.1f}s")
    # ZCA whitening fit (covariance + eigh)
    t_zca = time.time(); print(f"zca_fit: {t_zca-t_load:.1f}s")
    # whitened keys
    t_whiten = time.time(); print(f"whiten_keys: {t_whiten-t_zca:.1f}s")
```

### Step 3: Restart backend with empty KB + load wikipedia_100k via instrumented endpoint

Identify the 12-min consumer. Suspects:
- **ZCA fit:** covariance + eigh on 1024×1024 → expected ms. If reality is minutes → numpy BLAS/threading misconfigured (`OMP_NUM_THREADS=1` from somewhere?). Check `np.show_config()`.
- **load_from_disk:** reading 750 MB keys.npy. Expected: memmap is instant. If slow → maybe full-load-into-RAM instead of mmap.
- **Re-tokenization at load:** if facts.jsonl tokens are re-computed at load → cache or precompute.
- **Memory swap:** 14 GB exceeds something (RAM limit, container limit, paging file).

### Step 4: Apply targeted fix per profile

**MOST LIKELY: pre-fit substrate state OFFLINE**

Architecturally right. Each ingest pipeline pre-computes whitened keys at ingest time:

```python
# In wikidata_dump_ingest.py / wikipedia_ingest.py / etc.
keys_raw = bge_encoder.encode(facts)
W_whiten = fit_zca(keys_raw)  # done ONCE at ingest
keys_whitened = keys_raw @ W_whiten
np.save("data/substrate_state/<source>/keys_whitened.npy", keys_whitened)
np.save("data/substrate_state/<source>/W_whiten.npy", W_whiten)
```

At backend load:

```python
# SubstrateKV.load_from_disk
if (path / "keys_whitened.npy").exists():
    self.K = np.load(path / "keys_whitened.npy", mmap_mode='r')  # INSTANT
    self.W_whiten = np.load(path / "W_whiten.npy")
else:
    # fallback to fit at load (legacy)
    self.K_raw = np.load(path / "keys.npy", mmap_mode='r')
    self.W_whiten = fit_zca(self.K_raw)
    self.K = self.K_raw @ self.W_whiten
```

Eliminates 12-min ZCA fit cost from load path entirely.

**PLUS: background-thread admin endpoint (Option 1)**

```python
@router.post("/admin/load")
async def admin_load(source: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(_load_source, source)
    return {"status": "accepted", "source": source}, 202

# Progress via existing /query/tier5a/status
```

Inflight /converse never blocks; multi-tenant stays available.

### Step 5: Patch Stage A ingest pipeline TONIGHT

Stage A is currently running PID 190916 writing keys.npy without whitening. **Patch the pipeline to also write keys_whitened.npy + W_whiten.npy per source-shard.** Apply retroactively to existing 642K facts.

Without this, Wikidata 50M load would extrapolate to **54 hours + 4 TB RAM** (linear scale of 184K → 12 min → impractical). Pre-fit offline is REQUIRED for Wikidata, not optional.

### Step 6: Resume staged load with new design

```
empty backend → /admin/load wikipedia_100k (instant via mmap)
              → /converse query against 184K
              → /admin/load conceptnet_8m
              → /converse query against 642K
              → /admin/load arxiv + pubmed
              → /admin/load wikidata_50m
              → /converse query against full corpus
```

Each step should be < 5 sec (mmap + Qwen ready).

## What this gives strategically

**For v2.0 demo:**
- /converse + /chat serve QUICKLY (sub-second per source load)
- Multi-tenant serving works (no synchronous block)
- KB updates online (no full backend restart needed)

**For Wikidata 50M:**
- Pre-fit at ingest time = 50M whitened keys written incrementally during ~95 hr ingest
- Backend load = mmap = instant
- Architecturally scales to 1B+ facts

**For demo operator UX:**
- /admin/warmup returns 202 + progress
- Demo can show "loading X / Y facts" progress bar
- No 10+ min black hole

## Honest acknowledgment

This is a design issue I didn't flag in the BACKEND_GREENLIGHT note. Should have anticipated:
- Synchronous blocking + uvicorn single-thread = unusable in production
- ZCA fit at load = O(N) cost per startup
- 184K small load was already 12 min → 50M obviously impossible

Pre-fit + background-thread should have been the spec from the start.

## Cross-references
- BACKEND_GREENLIGHT (precursor): notes/research_to_testbed_BACKEND_GREENLIGHT_AND_MONITOR_2026-06-09.md
- STAGED_LOAD_OBSERVATION (this issue): notes/testbed_to_research_BACKEND_STAGED_LOAD_OBSERVATION_2026-06-09.md
- pyarrow fix commit: 57210a91
- staged-load support commit: 547eec4f

---

**Testbed:** kill /admin/load now (restores Stage A throughput) → instrument _init_kv with timing → profile → apply pre-fit (Option 2) + background-thread (Option 1) combo → patch Stage A pipeline to write keys_whitened.npy alongside keys.npy.

This unblocks /converse + /chat AT SCALE, not just at 184K. Required for Wikidata 50M, not optional.

Standing for profile results + targeted fix landing.
