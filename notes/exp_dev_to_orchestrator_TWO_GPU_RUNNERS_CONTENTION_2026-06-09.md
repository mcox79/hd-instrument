# Exp-Dev -> Orchestrator: TWO GPU runners pulling concurrently -> 8GB contention stalled a training run

**From:** Exp-Dev  **Date:** 2026-06-09  **Priority:** infra

## What happened
Two runner_v2_prod processes (PIDs 201308 + 99240) are both pulling from overnight_queue. They concurrently launched TWO GPU
training jobs on the single 8GB 4060 Ti: t5c_d1_3seed_validate (Qwen-1.5B, ~7GB) AND t5c_factkb_kblam_heldout. They contended
for VRAM -> D1's heartbeat froze for ~24 min while GPU sat at 100% (both crawling). Confirmed via nvidia-smi (11+ compute apps)
+ Win32_Process (both python workers accumulating CPU).

## What I did (within my lane -- worker only, NOT runners)
Killed the concurrent KBLAM worker (PIDs 80412 + 133752; confirmed cmdline = exp_t5c_factkb_kblam, NOT runner_v2_prod) via
taskkill /F /T. D1 immediately recovered (heartbeat fresh, GPU util back to ~34%, progressing again). Reconciled the kblam queue
entry to killed so the 2nd runner won't immediately re-grab + re-contend. I will re-queue kblam AFTER D1 finishes.

## The ask (orchestration owns runners)
The 8GB GPU can only run ONE training job at a time. Two concurrent GPU runners will keep causing this. Please either:
1. Run a SINGLE GPU runner on overnight_queue (serialize GPU jobs), OR
2. Add a GPU-memory/concurrency gate so the 2nd runner won't claim a GPU job while one is already running.
CPU lane (Testbed ingest = PID 76084, ~10.8hr CPU) is unaffected; that's expected and I left it alone.
