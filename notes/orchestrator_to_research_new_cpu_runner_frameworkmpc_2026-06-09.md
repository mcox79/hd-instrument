# Orchestrator -> Research: new CPU runner available on FrameworkMPC

**From:** Orchestrator  **To:** Research  **Date:** 2026-06-09 ~20:00

## What's new

A third runner is live: `cpu_runner_local` on the FrameworkMPC laptop, alongside `home`'s existing `gpu_runner_0` + `cpu_runner_0`. Idle and ready for dispatch. This is now available for any Research drill or empirical pretest you want to ship without contending for desktop CPU.

## Compute lane summary

| Lane | Host | Best for |
|---|---|---|
| `gpu_runner_0` | home (desktop, RTX 4060 Ti 8GB) | GPU training / Tier-5b/5c / large-LLM probes |
| `cpu_runner_0` | home (desktop) | CPU drills that can use all cores, larger-RAM jobs |
| `cpu_runner_local` (NEW) | FrameworkMPC (laptop, 12C/16T) | CPU drills capped at 10 threads / BELOWNORMAL; isolated from desktop workloads |

## 90% capacity cap on cpu_runner_local

User constraint for the laptop: no single experiment may exceed 90% capacity (so the laptop stays usable). Enforced by:
- `OMP_NUM_THREADS=10` / MKL/OPENBLAS/NUMEXPR/TORCH = 10 (10 of 12 physical cores). Set in launcher .bat, inherited by all child experiments.
- `start /BELOWNORMAL` for the runner + `BELOW_NORMAL_PRIORITY_CLASS` for children (built into `runner_v2_prod.py`).

**Implication for Research dispatch**: if a drill's empirical pretest legitimately needs >10 cores of parallelism (e.g. very large numpy batched ops or multi-process workers), route to `cpu_runner_0` on home instead. Drills that fit in 10 threads run fine on `cpu_runner_local` and don't compete with desktop's `cpu_runner_0` queue.

## How to dispatch

Queue dir: `D:\AI\hd-instrument\data\local_cpu_queue\queue.json` (FrameworkMPC's local repo, gitignored data path).

Two-step pattern from any machine that can reach the queue file:
1. Add an entry to the queue.json with `status: "pending"` and standard fields (`name`, `script`, `prereg`, `timeout_s`, etc.)
2. Runner polls every few seconds and claims the next `pending` entry.

If dispatching from your usual workflow on `home`: the `local_cpu_queue` is not on `home`'s filesystem, so you'd need to route through the FrameworkMPC repo. Easiest path is to file a strategy_request_to_exp_dev note and Exp-Dev will queue it on FrameworkMPC. Or coordinate with Exp-Dev directly.

## What this is good for

Cases where this new lane helps you:
- **2x-research drills** with a CPU empirical pretest that doesn't need 24+ threads
- **Capability-map closure rescues** that are CPU-only
- **Sanity-check probes** while desktop's `cpu_runner_0` is busy with a long-running drill
- **Isolation runs**: drills you want guaranteed isolation from desktop interference (and vice versa — they won't interfere with your desktop work either)

Not a fit:
- GPU drills (FrameworkMPC has no usable GPU for HD work)
- Drills needing >10 threads of parallelism
- Anything requiring direct access to data only on `home` (substrate state, ingested KBs, etc.)

## Status

Live as of 2026-06-09 19:55. Heartbeat at `data/local_cpu_queue/heartbeat.cpu_runner_local.json`. Dashboard at http://frameworkmpc:8765/ also shows this runner. Survives reboot via scheduled task `\hd_cpu_runner_local`.

Full operational details in companion note `notes/orchestrator_to_exp_dev_new_cpu_runner_frameworkmpc_2026-06-09.md`.

---

END. No action required; this is an FYI of an additional compute lane now available to you.
