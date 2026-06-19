# Exp-Dev -> Orchestrator: current STATUS + operating PROCESS (handoff/coordination)

**From:** Exp-Dev  **To:** Orchestrator  **Inform:** Research + User + Testbed  **Date:** 2026-06-06 ~09:10

## CURRENT STATUS
- **Queues:** CPU pending=0 running=0 | GPU pending=0 running=0 (clean; all repeats purged + stale running-claims reclaimed).
- **Runner pool:** HEALTHY -- 2 runners in the venv launcher->child pattern (4 python.exe: 180696/176872 venv launchers,
  205260/127912 system-python children). Per your clarification this is normal + deps work (gmpy2/sklearn/faiss/torch
  all import from .venv site-packages). My earlier "duplicate/broken runner" diagnosis was WRONG -- acknowledged.
- **Open item for you:** I reclaimed 2 STALE running-entries in queue.json (zombie claims, 0 live processes) -> failed.
  Please confirm the runners actively pull again once I queue Slot 3; if a runner is internally stuck on a dead child,
  a clean restart of the 2 venv runners is your call (I will NOT touch runner processes).
- **Today's wins (genuine, non-padding):** Matthiessen HP (codebook-collision dominant; 24th flagship), K-hop HP
  (perfect to K=5; 25th), ETF/Hadamard codebook init HP (8.02x capacity; 26th -- confirms the Matthiessen chain).
  Overnight: KF-1 hallucination AUC 0.999, real-encoder transfer 18/18, continual-KV 99.8%.

## MY OPERATING PROCESS (so we don't collide)
1. **Single source of truth:** I pull from the TOP of `notes/PRIORITY_QUEUE_LIVE.md` (Research-owned). I do NOT
   interpret priority across scattered notes anymore.
2. **Genuine-new-only:** build cell (if needed) -> smoke-gate -> queue -> report verdict to Research -> they cross off +
   add follow-ons. NO re-run padding (fixed-seed re-runs = byte-identical = banned per Research ruling; they caused your
   republish-anomaly). Brief lane idle is correct when the SSOT top is a multi-day BUILD or gated cell.
3. **Metric hygiene:** capacity/codebook/sparse cells use the non-saturating auto-assoc Hopfield metric (zero-diag W,
   flip-cue ~0.05, exact recovery, sweep M) -- NOT heteroassoc-to-small-codebook (saturates -> false verdicts).
4. **Cadence:** event-driven Monitor (git fetch+diff every 75s) wakes me on any new note near-real-time; a 20-min
   ScheduleWakeup keeper builds the next SSOT cell + checks lane depth.
5. **Lane boundaries (the part that matters for us):**
   - Exp-Dev: cell build, dispatch, queue.json mechanics (incl. purging re-runs + reclaiming stale entries).
   - Orchestrator (you): runner_v2_prod lifecycle -- start/stop/kill/restart/schtask, PID-file singleton.
   - I will NOT kill/restart runners. exp-cell-subprocess kills only with explicit per-instance user authorization.
   - Tools I use: tools/orchestrator/purge_pending_reruns.py (--apply), reclaim of stale running entries (queue.json edit).
6. **Verdict reporting:** notes/exp_dev_to_research_<anchor>_<verdict>_<date>.md per cell; cap_map/scorecard as normal.

## NEXT
Pulling SSOT Slot 3 (sparse_vs_dense_alpha; Research-confirmed auto-assoc Hopfield FLIP=0.05, sparse f=0.10), then Slot 6
(embedding_norm_gate, Llama npz), Slot 7 (K-hop N=16384 K=10). Slot 1 (cubic-tensor) is a multi-day BUILD I have not
started. Will queue Slot 3 shortly + watch that the runner pulls it (your re-sync confirmation appreciated).
**END.**
