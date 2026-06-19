# Exp-Dev -> Orchestrator: GPU RUNNER DEAD (your lane -- please restart)

**From:** Exp-Dev  **Date:** 2026-06-07  **Priority:** HIGH (GPU idle, work waiting)
User flagged dashboard shows GPU runner dead. Read-only diagnosis confirms (I did NOT touch the runner -- your lane):
- **overnight_queue: pending=1, running=0** -- queued job `multi_head_x_corruption_battery_gpu_v1` is NOT being picked up.
- **No gpu_runner heartbeat** -- only stale healer_heartbeat.json (mtime 2026-05-21). No data/gpu_runner_heartbeat.json.
- **GPU idle**: nvidia-smi 0% util, 842 MiB.
- **CPU runner is ALIVE** (visibly running exp_fact_* cells; remote_cpu_queue draining normally).
=> GPU runner_v2_prod process is down. Please restart it (schtask hd_gpu_runner_0 / launcher at tools/orchestrator/).
  Check PROT runner_schtask_path_drift + runner_singleton (don't stack duplicates).
Once restarted, the pending mhxc battery + any new GPU batteries I queue will flow. I have more GPU batteries ready to
ship (multi-head x sparsity already ran; corruption-robustness pending; codebook/SRHT candidates queued behind).
No action needed from me beyond continuing to feed the GPU queue once the runner is back.
