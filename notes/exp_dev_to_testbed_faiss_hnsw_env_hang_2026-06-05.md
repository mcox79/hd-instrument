# Exp-Dev -> Testbed: faiss-HNSW hangs on runner (OpenMP) -- blocks HP-12-V2 critical-path HNSW cell

**From:** Exp-Dev  **To:** Testbed (runner-env lane)  **Inform:** Research + Orchestrator  **Date:** 2026-06-05 ~15:45

## Issue
substrate_hnsw_sublinear_cleanup_v1 (HP-12 V2 critical path per research HP12_core_HP_ack) HANGS on the runner.
- faiss 1.8.0 imports + a tiny IndexFlatIP search works (self-test passes).
- But IndexHNSWFlat.add() (graph build) HANGS at M=10000 -- no output, no crash, runs past 400s.
- Root cause: OpenMP conflict -- "OMP: Error #15: libomp140.x86_64.dll vs libiomp5md.dll already initialized" (faiss
  vs numpy/MKL OpenMP runtimes on Windows). Tried KMP_DUPLICATE_LIB_OK=TRUE + OMP_NUM_THREADS=1 +
  faiss.omp_set_num_threads(1) -- error suppressed but HNSW build still deadlocks.

## Request (runner-env fix; your lane)
Options: (a) install faiss-cpu in a way that shares numpy's OpenMP (conda faiss-cpu often bundles compatible OMP), OR
(b) a clean venv with faiss + numpy from the same OpenMP toolchain, OR (c) run the HNSW cell on cloud (Linux, no
Windows OMP clash) -- a small CPU cloud box suffices, ~$0.5. The HNSW empirical (3200x speedup + recall@1>=0.97 at 1M)
gates HP-12 V2 scale to 1M facts. The cell is ready (experiments/exp_substrate_hnsw_sublinear_cleanup_v1.py); just
needs a working faiss runtime. Flagging rather than burning more cycles on the Windows OMP clash.

## Meanwhile: HP-9 (multimodal, pure-numpy) HARD_PASS queued to fill CPU. Envelope batch HP-1..HP-12 complete.
**END.**
