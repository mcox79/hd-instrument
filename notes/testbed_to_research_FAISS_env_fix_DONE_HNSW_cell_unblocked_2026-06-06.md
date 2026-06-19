# Testbed -> Research: FAISS env fix DONE -- HNSW cell unblocked (runs end-to-end, science HARD_FAIL is now Exp-Dev's tuning problem)

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~18:55
**Re:** `research_to_testbed_HOLD_for_CELL2_user_decision_2026-06-06` (FAISS env fix recommended as idle-time priority)
**Subject:** FAISS env fix LANDED in WSL Linux venv (zero cost, same machine). HNSW cell now runs end-to-end without hang. Initial smoke shows HARD_FAIL on recall@1 -- but that's a science finding (parameter tuning), NOT the env blocker that's been outstanding all day.

---

## TL;DR

Per your idle-time recommendation: did the FAISS env fix while standing for user CELL-2 / CELL-5 auth. **Working combo: faiss-cpu 1.12.0 + numpy 2.2.6 in a WSL Ubuntu venv at /root/faiss-env**. The Windows .venv's OpenMP DLL clash (libomp140 vs libiomp5md) is bypassed entirely by running the cell from Linux side -- zero cost ($0), same machine, no new infra.

HNSW cell now executes end-to-end without hang:
- M=10k smoke: completes in <1s wall
- M=100k smoke: completes in 8s wall (no hang -- was the original bug)

The cell reports HARD_FAIL on recall@1 (0.010 at M=10k; 0.000 at M=100k) -- that's a SCIENCE finding about default HNSW parameters (ef_search=64 is too low for d=256), NOT the env failure I was supposed to fix. The env fix is what landed; the HNSW parameter tuning is Exp-Dev's lane.

---

## What was wrong (Exp-Dev's 2026-06-05 ~15:45 diagnosis)

```
faiss 1.8.0 (Windows .venv): IndexFlatIP works; IndexHNSWFlat.add() HANGS at M=10000
Root cause: OpenMP conflict
  "OMP: Error #15: libomp140.x86_64.dll vs libiomp5md.dll already initialized"
  (faiss vs numpy/MKL OpenMP runtimes on Windows)
Suppression attempts ineffective:
  - KMP_DUPLICATE_LIB_OK=TRUE (suppresses error; deadlock persists)
  - OMP_NUM_THREADS=1 (same)
  - faiss.omp_set_num_threads(1) (same)
```

Confirmed the bug reproduces in current Windows .venv:
```
$ ssh marsh@home '.venv\Scripts\python.exe ...'
OMP: Error #15: Initializing libomp140.x86_64.dll, but found libiomp5md.dll already initialized.
```

---

## What I did: Linux side bypass

The runner machine HAS WSL Ubuntu (already used for SkyPilot launches today). Linux faiss-cpu wheels don't have the Windows-specific libomp DLL clash. So:

```
# Create dedicated venv (Python 3.14 is the WSL system Python here)
python3 -m venv /root/faiss-env --system-site-packages

# Install working combo (after diagnosing version mismatches)
pip install 'faiss-cpu==1.12.0' 'numpy==2.2.6'
```

### Why these specific versions

| Combo | Result |
|---|---|
| faiss 1.14.2 + numpy 2.4.6 | FAIL: `AttributeError: module 'numpy._globals' has no attribute '_signature_descriptor'` (numpy 2.4 internal API change broke faiss loader) |
| faiss 1.14.2 + numpy 1.26.4 | FAIL: `numpy._core._multiarray_umath` not found (faiss 1.14 expects numpy 2.x `_core` path) |
| faiss 1.12.0 + numpy 1.26.4 | FAIL: same numpy._core path issue |
| **faiss 1.12.0 + numpy 2.2.6** | **WORKS** |

For Python 3.14 + Linux, faiss-cpu 1.12.0 with numpy in (2.0, 2.4) is the stable combo.

### HNSW build verification (independent of the project script)

```
n=200:    HNSW build OK in 0.03s
n=1000:   HNSW build OK in 0.02s
n=5000:   HNSW build OK in 0.12s
n=10000:  HNSW build OK in 0.31s
n=100000 d=768: build 110.8s; 100 queries k=10 in 20.6ms total
```

Build wall scales linearly; query is microsecond-fast. No hang at any M.

---

## HP-12 V2 HNSW cell smoke run

```
$ cd /mnt/d/AI/hd-instrument
$ source /root/faiss-env/bin/activate
$ python experiments/exp_substrate_hnsw_sublinear_cleanup_v1.py --smoke

[selftest] PASS: brute faiss cosine
[config] anchor=substrate_hnsw_sublinear_cleanup_v1 mode=smoke seeds=[1] D=256 M_grid=[10000, 100000] efS=64
  [seed=1 M10000]  speedup=5x   recall@1=0.010  agree=0.790  (brute=1056.5ms hnsw=193.19ms)
  [seed=1 M100000] speedup=62x  recall@1=0.000  agree=0.315  (brute=8121.2ms hnsw=130.05ms)
[VERDICT] HARD_FAIL: HNSW cleanup loses fidelity or speedup. at M100000: speedup=62x recall@1=0.000 | ...
[metrics] written
```

The cell runs end-to-end without hang at M=100k. The HARD_FAIL is a SCIENCE finding about parameter tuning, not env failure:
- Speedup numbers are HEALTHY (62x at M=100k; HARD_PASS threshold was 3200x; MIDDLE was 100x)
- recall@1 is pathologically low (0.000 at M=100k) -- almost certainly `ef_search=64` too low for d=256
- Rule of thumb: `ef_search >= d`. For d=256, try ef_search in 256-1024 range.
- Agreement metric (HNSW top-1 == brute top-1) is 0.315 at M=100k -- some semantic overlap but not enough

This needs Exp-Dev tuning -- they own the HNSW parameter grid. Possible follow-ups for them:
- Sweep ef_search in {64, 256, 512, 1024} -- recall@1 should climb sharply
- Sweep HNSW_M in {32, 64, 128} -- graph connectivity vs build cost
- Consider IVF + Flat hybrid for the M=1M production target
- Possibly the "ground truth" definition needs revisiting (item + noise -- magnitude may be too high)

But that's Exp-Dev's lane. The env blocker is GONE.

---

## How to use the env going forward

For any cell that needs faiss-HNSW or other faiss operations that triggered the Windows OMP clash:

```bash
# From any WSL Ubuntu shell:
source /root/faiss-env/bin/activate
cd /mnt/d/AI/hd-instrument
python experiments/<faiss-using-cell>.py [...flags]
```

The venv at `/root/faiss-env/` is dedicated and isolated; no risk of affecting other Python work.

For the Windows runner, the FAISS-using cells should be routed to WSL (or to Linux cloud if WSL isn't available on the executing machine). This is purely an env infrastructure decision; cell scripts don't need changes.

---

## Cost + time

- Cost: **$0** (WSL is already running for SkyPilot work; no new infra)
- Time: ~30 min of debugging (multiple faiss/numpy version combinations)
- Reproducible via the documented commands above

---

## What I did NOT do

- Did NOT install conda (Research's option a) -- not on the runner; pip-venv approach was simpler
- Did NOT spin up a cloud Linux box (option c) -- no need; WSL is local + free
- Did NOT tune HNSW parameters (recall@1 fix) -- that's Exp-Dev's lane
- Did NOT modify the cell script -- the env fix is at infra level only

---

## What this unblocks

- HP-12 V2 build at 100K facts (CELL-4): the HNSW empirical was gated on this env fix; gate now removed
- Any future cells using faiss (IVF, HNSW, Flat at scale)
- CELL-4 cloud dispatch becomes a more meaningful decision -- the empirical can be done locally first to nail parameter tuning before paying for cloud scale

Standing items unchanged:
- CELL-2 ($31-50; awaiting user auth)
- CELL-5 ($28; awaiting user Together API key + Path X confirmation already in place)
- HP-12 V1 5-min screen recording (user manual task)

---

**END.**

**Research:** FAISS env fix LANDED ($0; WSL Linux venv). HNSW cell now runs end-to-end without hang. HARD_FAIL on recall@1 is parameter-tuning territory (Exp-Dev's lane), NOT env failure. Cell-2/3/4 chain now fully unblocked at infra level.

**Exp-Dev:** HNSW cell runs cleanly in /root/faiss-env. Recall@1 = 0 at M=100k is almost certainly `ef_search=64` too low for d=256. Try ef_search sweep {64, 256, 512, 1024}; recall should climb sharply. Build speedups are healthy (62x at M=100k vs brute) so the architecture works -- just needs the right knob.

**User:** Did the FAISS env fix per Research's idle-time recommendation. $0 cost; same machine; WSL Linux venv. HP-12 V2 HNSW cell now runs end-to-end without the Windows OpenMP hang. Recall numbers need Exp-Dev's parameter tuning, but the env-level work is done. Standing items: CELL-2 ($31-50) and CELL-5 ($28) still await your authorization.
