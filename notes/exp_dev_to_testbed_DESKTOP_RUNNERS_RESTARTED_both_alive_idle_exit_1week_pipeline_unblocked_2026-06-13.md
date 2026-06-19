# exp_dev -> testbed/orchestrator: DESKTOP RUNNERS RESTARTED (closes the dead-runners flag). Both alive, idle-exit raised to 1 week, pipeline unblocked.

**From:** exp_dev  **Date:** 2026-06-13. Per USER directive "restart those runners".

## Done
- gpu_runner_0 -> overnight_queue (GPU; .venv python torch 2.5.1+cu121, CUDA available) -- PID 37708 (+worker 29388).
- cpu_runner_0 -> remote_cpu_queue -- PID 18316 (+worker 19296). Already ran the pending f4_kappa_n cell (DONE 4.3s, exit 0).
- Both: --idle-exit-minutes 10080 (1 week) so they don't idle-exit overnight again; --singleton-pid-file in data/logs/.
- Launcher committed: tools/start_desktop_runners.cmd. Launched detached via Win32_Process.Create (survives ssh disconnect).

## Durability note (for testbed/orchestrator to decide)
These survive ssh disconnect + idle, but NOT a desktop REBOOT (no Scheduled Task -- elevation blocked; no Startup entry yet).
For reboot-durability, add tools/start_desktop_runners.cmd (or a .vbs wrapper) to the desktop user's Startup folder -- same
pattern exp_dev used for the laptop event-bus producer. Flagging for whoever owns desktop infra; exp_dev can set it up on request.
