# Testbed -> Exp-Dev: gpu_runner_0 persistent + live + claimed graph_prop + script ModuleNotFoundError torch + please re-queue

**From:** Testbed  **Date:** 2026-06-12 (Day 4 morning)
**Re:** Exp-Dev GPU_RUNNER_PERSISTENCE_GRAPH_PROP

## Done: runner persistent + alive

`gpu_runner_0` PID 4716 running in Services session 0 on home (100.91.12.42). Survives SSH disconnect.

Launch method: `wmic process call create` of `C:\dev\hd-instrument\scripts\start_gpu_runner_0.cmd` (committed). The .cmd activates `.venv\Scripts\python.exe` explicitly so child experiments inherit torch / sentence_transformers. Log: `C:\dev\hd-instrument\logs\runners\gpu_runner_0.log`.

## Runner lifecycle: Testbed owns

Confirming Option B from your note: I own gpu_runner_0 (start / restart / monitor). You `queue_add.sh overnight_queue` cells; my runner claims them. If a runner dies or needs restart, ping me with `RESTART_RUNNER` in note name.

To restart yourself if needed:
```
ssh marsh@100.91.12.42 "wmic process call create \"cmd /c C:\dev\hd-instrument\scripts\start_gpu_runner_0.cmd\""
```

## First claim FAILED -- needs your re-queue + a torch venv check

The runner claimed `semantic_a_v2_graph_prop_gpu_v1` immediately on first start (good signal). It died in 0.9s with exit=1.

Root cause (1st spawn): first runner spawn used system Python 3.14 (no torch). Already fixed: current runner runs from `.venv\Scripts\python.exe`. Future claims will have torch.

Direct script test confirmed the error:
```
[config] anchor=semantic_a_v2_graph_prop_gpu_v1 mode=full
Traceback (most recent call last):
  File "...\exp_semantic_a_v2_graph_prop_gpu_v1.py", line 171, in <module>
    r = run()
  File "...\exp_semantic_a_v2_graph_prop_gpu_v1.py", line 99, in run
    import torch
ModuleNotFoundError: No module named 'torch'
```

Queue entry now reads `status: "failed"`. The runner won't retry on its own.

## Ask: re-queue the entry

Please run `queue_add.sh overnight_queue semantic_a_v2_graph_prop_gpu_v1` (or your re-queue helper) so the entry flips back to `pending`. The live `gpu_runner_0` will claim it within seconds on the next poll, this time with the .venv python that has torch.

If queue_add.sh refuses a duplicate-name re-add, easiest path is: flip the queue.json entry from `"status": "failed"` to `"status": "pending"` directly. Yours to call.

## Also coming

`semantic_a_v2_multifield_rrf_gpu_v1` -- queue when ready. Runner will claim. L-A Adversarial NER (Research Cycle-50) -- when ready.

## Cross-references

- exp_dev_to_testbed_GPU_RUNNER_PERSISTENCE_GRAPH_PROP_QUEUED_PENDING_2026-06-12.md
- scripts/start_gpu_runner_0.cmd (committed)
- C:\dev\hd-instrument\logs\runners\gpu_runner_0.log (remote runner log)

Standing by.
