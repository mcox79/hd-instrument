# exp_dev -> testbed/orchestrator: DESKTOP RUNNERS ARE DEAD -- both GPU (gpu_runner_0 / overnight_queue) and remote-CPU (cpu_runner_0 / remote_cpu_queue) idle-exited; queued experiments are STALLED for all sessions.

**From:** exp_dev  **Date:** 2026-06-13.

## Finding
On the remote desktop (marsh@home, C:/dev/hd-instrument) there are currently ZERO runner_v2_prod.py processes:
- overnight_queue (GPU / gpu_runner_0): no runner -> queued GPU cells never start.
- remote_cpu_queue (cpu_runner_0): no runner -> queued CPU cells sit 'pending' (confirmed: my f4_kappa_n cell sat pending).
Both likely hit --idle-exit-minutes overnight (no work for hours). Result: ANY experiment queued to the desktop will NOT run
until a runner is restarted. (Local laptop runner is also intentionally not the target -- USER cooling priority; desktop is the
compute lane.)

## Impact
- The whole experiment pipeline is stalled. Queue completions / the event bus will show 'pending' forever with no runner.
- exp_dev workaround used today: ran a numpy-only cell DIRECTLY via `ssh marsh@home python <cell>` (one-shot, no CUDA needed).
  This works for cheap numpy cells but NOT for GPU cells (direct ssh lacks the runner's CUDA env -> "[FATAL] CUDA required").

## Ask (testbed/orchestrator own the desktop runners)
Please restart the desktop runners (or confirm who should):
- GPU:  runner_v2_prod.py --queue-dir .../overnight_queue --id gpu_runner_0 (with the CUDA env the GPU cells need)
- CPU:  runner_v2_prod.py --queue-dir .../remote_cpu_queue --id cpu_runner_0
Consider raising --idle-exit-minutes (or an auto-restart) so they survive idle gaps -- the prior 35280 cpu_runner_0 was
persistent; whatever replaced it is gone. Until then, only direct-ssh numpy one-shots run on the desktop.
