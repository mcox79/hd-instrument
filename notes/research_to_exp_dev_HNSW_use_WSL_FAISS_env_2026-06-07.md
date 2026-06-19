# Research -> Exp-Dev: Cell 10 HNSW -- use Testbed's WSL /root/faiss-env (not Windows runner)

**From:** Research session
**To:** Exp-Dev
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-07 ~06:45
**Re:** exp_dev_to_research_batchE_batch1_2026-06-07.md (Cell 10 HNSW PARKED)
**Subject:** Cell 10 HNSW PARKED on Windows OpenMP conflict. Testbed established WSL FAISS env at /root/faiss-env (faiss-cpu==1.12.0 + numpy==2.2.6 on Python 3.14). Dispatch HNSW cell FROM the WSL side, not the Windows runner.

---

## Cell 10 HNSW routing

You noted "Needs the Testbed FAISS env fix" -- it's already done (testbed_to_research_FAISS_env_fix_DONE_HNSW_cell_unblocked_2026-06-06.md).

The fix is at WSL Ubuntu: `/root/faiss-env/`. Activation:

```bash
source /root/faiss-env/bin/activate
cd /mnt/d/AI/hd-instrument
python experiments/<HNSW-cell-script>.py
```

**Dispatch HNSW cell from WSL side**, not the Windows runner. The Windows OpenMP conflict (libomp140 vs libiomp5md) is bypassed by running on Linux.

## What works on Windows runner vs WSL

| Lane | Use for |
|---|---|
| Windows runner | All non-FAISS cells (Batch E batch-1 majority); GPU lane (when restored) |
| WSL /root/faiss-env | Cell 10 HNSW + any future FAISS-using cell (IVF, HNSW, Flat at scale) |

For Batch E batch-2 (Cell 5 BGE-large + Cell 6 KF-1 paraphrase + Cell 7 fp16 parity): no FAISS dependency, Windows runner is fine.

## Batch-1 results outstanding for HNSW

Once Cell 10 dispatches via WSL:
- ef_search sweep {64, 256, 512, 1024} per Testbed's earlier guidance
- Goal: ground production HNSW configuration; prevent certain-failure mode at default ef_search=64

## Cross-references

- FAISS env fix: testbed_to_research_FAISS_env_fix_DONE_HNSW_cell_unblocked_2026-06-06.md
- WSL venv path: /root/faiss-env/
- Working combo: faiss-cpu==1.12.0 + numpy==2.2.6 on Python 3.14 Linux
- Testbed's earlier guidance: ef_search >= d (so >=256 for d=256)

## Contract

You dispatch Cell 10 from WSL when convenient. No new design needed; just env routing change.

---

**END.**

**Exp-Dev:** Cell 10 dispatches from WSL `/root/faiss-env/`. Use `source /root/faiss-env/bin/activate && python experiments/<cell>.py`. Testbed already set up env; no new infra needed.

**Testbed:** No action; just visibility that your env fix is being used for Cell 10.

**User:** Routing clarification only; Cell 10 HNSW will dispatch via WSL env Testbed set up earlier today.
