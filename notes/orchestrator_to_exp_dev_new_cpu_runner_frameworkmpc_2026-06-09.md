# Orchestrator -> Exp-Dev: new CPU runner available on FrameworkMPC

**From:** Orchestrator  **To:** Exp-Dev  **Date:** 2026-06-09 ~19:57

## What's new

User asked for a third runner on the FrameworkMPC laptop (alongside `home`'s `gpu_runner_0` + `cpu_runner_0`). It's up and idle.

## Runner details

- **ID**: `cpu_runner_local`
- **Host**: FrameworkMPC (Tailscale 100.124.176.29) — NOT `home`
- **Queue dir**: `data/local_cpu_queue/queue.json` (FrameworkMPC's local repo at `D:\AI\hd-instrument\`)
- **Heartbeat**: `data/local_cpu_queue/heartbeat.cpu_runner_local.json`
- **Log**: `data/logs/cpu_runner_local.log`
- **Scheduled task**: `\hd_cpu_runner_local` (user-level, at-logon, survives reboot)
- **Singleton PID**: `data/logs/cpu_runner_local.pid` (idempotent re-launch via task)
- **Current state**: alive, idle, fresh heartbeat (status=idle)

## 90% CPU capacity cap

User constraint: no single experiment may use more than 90% of laptop capacity. Implemented at two layers:

1. **Thread caps** (in launcher .bat — applied to runner process AND inherited by all child experiments):
   - `OMP_NUM_THREADS=10` / `MKL_NUM_THREADS=10` / `OPENBLAS_NUM_THREADS=10` / `NUMEXPR_NUM_THREADS=10` / `TORCH_NUM_THREADS=10`
   - 10 of 12 physical cores = 83% physical / 62% logical. Caps each experiment's inner-loop parallelism.
2. **Process priority**:
   - Launcher uses `start /BELOWNORMAL` for the runner itself.
   - `runner_v2_prod.py` passes `BELOW_NORMAL_PRIORITY_CLASS` to every child experiment it spawns (built-in, no opt-in).
   - Combined: even if an experiment ignores OMP and spawns its own pool, OS-level scheduling keeps interactive UI responsive.

If you have a specific experiment that legitimately needs more parallelism, dispatch it to `home`'s `cpu_runner_0` instead — that one has no cap.

## How to dispatch from your usual flow

The queue location difference is the only change. Your existing `queue_add.py` pattern works; just point at the FrameworkMPC queue dir.

If you're using `tools/queue_add.py` from a FrameworkMPC shell:
```
python tools/queue_add.py local_cpu_queue <anchor_name> experiments/exp_<anchor>.py --prereg preregs/<...>
```

If dispatching from elsewhere (e.g. from `home` or by editing queue.json directly), the absolute path is:
```
D:\AI\hd-instrument\data\local_cpu_queue\queue.json
```

The runner polls every few seconds and will claim the next pending entry. Heartbeat updates on each cycle.

## Path differences (FrameworkMPC vs home)

| | FrameworkMPC | home |
|---|---|---|
| repo root | `D:\AI\hd-instrument\` | `C:\dev\hd-instrument\` |
| python | `D:\AI\hd-instrument\.venv\Scripts\python.exe` | `C:\dev\hd-instrument\.venv\Scripts\python.exe` |
| sys-Python child | `C:\Users\marsh\AppData\Local\Programs\Python\Python311\python.exe` | same |

The runner_v2_prod.py code is the same (git repo synced).

## What to use this runner for

Best fit: CPU-only experiments where the desktop's `cpu_runner_0` is busy or queued behind a long job. Also: experiments that need an isolated machine to avoid contention with desktop workloads.

Not a fit: GPU experiments (no GPU on FrameworkMPC), or experiments that need >10 threads of parallelism.

## Status check from anywhere

Dashboard at http://frameworkmpc:8765/ now also covers the FrameworkMPC machine. Direct check on FrameworkMPC:
```powershell
Get-Content D:\AI\hd-instrument\data\local_cpu_queue\heartbeat.cpu_runner_local.json
```

---

END. No action required; runner is ready when you have something to dispatch.
