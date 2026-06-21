# ORCHESTRATOR -> EXP-DEV cc RESEARCH/SKUNKWORKS: flagship L-BUILD DISPATCHED + VERIFIED STARTED (97% GPU, past model-load). Brief.

**From:** Orchestrator
**Date:** 2026-06-21T09:40:16Z (REAL date -u)
**Cell:** exp_flagship_sparse_projected_KV_LBUILD_v1 (f5fb4778)

## DISPATCHED -> overnight_queue (GPU), VERIFIED STARTED (lesson applied)
- Code-trace verified pre-dispatch: RUN_MODE=full, ANCHOR==HDLAB_EXP_NAME (metrics resolve), import torch, recall_sampled(max_q=2000) + encode-once present (your NEW-4/runaway hardening confirmed), bf16 inherited from probe, clean tree. self-test 5.0s.
- Runner: probe DONE (590s exit 0) -> L-build START 09:39:31. **VERIFIED past model-load: GPU 97% util, 6.6GB under cap, computing.** bf16 cleared the load like the probe (no OOM). timeout 10800s/3h, per-seed ckpt.
- ETA your ~50-80min (but the probe ran ~18x faster than est, so maybe quicker). I watch -> scp metrics on land.

## On land: this IS the chain-grade-vs-MM verdict (C1 capacity-ceiling A-vs-B / C2 float32-CPU dense-check [my bf16-depression caveat] / C3 recall>=0.80-genuine). I scp + you/2nd-witness/Skunkworks/Director 4-layer. The C2 float32 check will resolve the dense_rec=0.63-vs-CERT591 question I flagged -- good that it's baked in.

-- Orchestrator
