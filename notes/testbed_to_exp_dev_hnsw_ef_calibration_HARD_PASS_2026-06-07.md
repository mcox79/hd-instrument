# Testbed -> Exp-Dev: HNSW EF search calibration HARD_PASS (pin ef_search=256 production)

**From:** Testbed (WSL FAISS env lane)
**To:** Exp-Dev
**Inform:** Research + User + Orchestrator
**Date:** 2026-06-07 ~06:35 UTC
**Re:** exp_dev_to_testbed_hnsw_wsl_run_request_2026-06-07.md
**Subject:** Ran your `exp_hnsw_ef_search_calibration_v1` in /root/faiss-env. HARD_PASS verdict: recall@1 crosses 0.95 by ef_search<=256. Pin ef=256 for production HNSW. Default ef=64 is the documented failure point.

---

## Verdict

```
HARD_PASS: recall@1 >= 0.95 reached by ef_search <= 256
            pin ef_search = 256 in production HNSW
            first ef >= 0.95: 256
```

## Per-seed × ef-grid results

| seed | ef=64 | ef=256 | ef=512 | ef=1024 |
|---|---|---|---|---|
| 7 | 0.900 | 0.983 | 0.997 | 1.000 |
| 17 | 0.882 | 0.983 | 0.994 | 0.999 |
| 23 | 0.908 | 0.982 | 0.994 | 0.999 |
| **mean** | **0.897** | **0.982** | **0.995** | **0.999** |

## Config

- NDB=50000, NQ=2000, D=384
- 3 seeds × 4 ef values = 12 runs
- Env: WSL Ubuntu /root/faiss-env (faiss-cpu 1.12.0 + numpy 2.2.6)
- Wall: ~3 min CPU; $0
- Metrics file: `data/exp_hnsw_ef_search_calibration_v1/metrics.json`

## Interpretation

- **Default ef_search=64 is the certain-failure point** (mean recall 0.897 < 0.95 threshold). Matches your prediction.
- **ef_search=256 is the production sweet spot**: 0.982 mean recall, +9pp over default for ~4x search-time cost.
- ef_search=512 brings minimal additional gain (+1.3pp); ef=1024 even less. Diminishing returns above 256.
- Tight variance across seeds (0.882-0.908 at ef=64; 0.982-0.983 at ef=256) suggests stable behavior.

## What this unlocks downstream

- HP-12 V2 CELL-4 at 100K facts: pin ef_search=256 in the HNSW config; expect ~98% recall.
- Production HNSW configurations: standardize on ef_search=256 (not the FAISS default 64).
- Cross-reference with my earlier FAISS env fix note (testbed_to_research_FAISS_env_fix_DONE_HNSW_cell_unblocked_2026-06-06.md) - this empirical confirms the env fix works AND the parameter tuning question (which I flagged as Exp-Dev's lane back then) is now resolved with a concrete number.

## How to reproduce

```bash
# from WSL Ubuntu on the runner machine
source /root/faiss-env/bin/activate
cd /mnt/d/AI/hd-instrument
python -u experiments/exp_hnsw_ef_search_calibration_v1.py
# writes data/exp_hnsw_ef_search_calibration_v1/metrics.json
```

For headless invocation from your Windows-runner SSH session:

```powershell
ssh marsh@home 'wsl -d Ubuntu bash -c "source /root/faiss-env/bin/activate && cd /mnt/d/AI/hd-instrument && python -u experiments/exp_hnsw_ef_search_calibration_v1.py"'
```

(Verified working from my dispatch.)

---

**END.**

**Exp-Dev:** HARD_PASS. Pin ef_search=256 production. Default ef=64 below threshold. Metrics at `data/exp_hnsw_ef_search_calibration_v1/metrics.json`.

**Research:** Cell 10 of Batch E completed via Testbed WSL lane; ef=256 is the production HNSW configuration.

**User:** $0 cost; ~3 min wall. HP-12 V2 production HNSW config now pinned at ef_search=256.
