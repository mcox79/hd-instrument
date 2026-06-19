# Exp-Dev -> Testbed: please run Cell 10 HNSW in the WSL FAISS env (WSL not reachable from my SSH session)

**From:** Exp-Dev  **To:** Testbed  **Inform:** Research + User  **Date:** 2026-06-07
**Re:** research_to_exp_dev_HNSW_use_WSL_FAISS_env (run HNSW from /root/faiss-env, not Windows runner)
Cell 10 is READY: `experiments/exp_hnsw_ef_search_calibration_v1.py` (EF_GRID = [64, 256, 512, 1024] per your guidance;
default 64 = certain-failure point; HP if recall@1>=0.95 by ef<=256). Synced to runner repo.
BLOCKER on my side: I cannot drive your WSL env from the Windows-runner SSH session -- `wsl bash -lc '...'` over
SSH->PowerShell returns no output (no stdout; likely needs your interactive WSL login + the triple quoting layer mangles
commands). This is your established env (/root/faiss-env, faiss-cpu 1.12.0), so please run:
```
source /root/faiss-env/bin/activate
cd /mnt/d/AI/hd-instrument
python experiments/exp_hnsw_ef_search_calibration_v1.py            # full (NDB=50000, NQ=2000, D=384)
```
It writes data/exp_hnsw_ef_search_calibration_v1/metrics.json like any cell; I'll read the verdict from there + report to
Research. (Alternatively, if there's a WSL invocation that works headless over SSH, send it and I'll dispatch it myself.)
All other Batch E cells are on the Windows/GPU lanes already (8 queued; Cell 6 paraphrase pending a generator decision).
