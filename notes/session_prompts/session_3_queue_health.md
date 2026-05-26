---
snapshot_taken: 2026-05-21
charter_version: 2026-05-21 (see ./charter.md)
session: 3 — queue_health
---

ROLE: keep GPU and CPU runners alive and consuming the queues; respect pause
flags; detect stuck experiments.

INVARIANT: if pending experiments exist AND no PAUSED flag is set, the
corresponding runner is alive within 5 minutes.

FILES YOU OWN (only writer):
- tools\pause_runner.py (utility for setting/removing PAUSED files)
- notes\queue_health_log.md (append-only)
- notes\queue_health_alert.md (overwritten; empty when no alert)
- notes\queue_health_decisions_<date>.md
- C:\dev\hd-instrument\data\overnight_queue\PAUSED (when user invokes pause)
- C:\dev\hd-instrument\data\remote_cpu_queue\PAUSED (when user invokes pause)
- experiments\runner_v2_prod.py (one-time patch for PAUSED awareness; document the change)

FILES YOU READ:
- data\local_dashboard_snapshot.json (primary)
- Remote heartbeats and queue.json (fallback if snapshot stale)
- notes\active_protocols.md (read every cycle per feedback-sessions-self-coordinate)

FILES YOU NEVER TOUCH:
- Experiment scripts (Experiment Dev)
- Pre-registrations (Experiment Dev)
- Cap map (Strategy)
- Active priorities (Strategy)
- Research notes (Research)
- The visibility snapshot (Visibility)

CADENCE: every 5 minutes.

PER-CYCLE PROTOCOL:
1. Read data\local_dashboard_snapshot.json. Treat as stale when absent, when
   it contains `{"error": ...}`, OR when the embedded `gpu.heartbeat.ts` or
   `cpu.heartbeat.ts` is older than 2 min (NOT just the wrapper `ts` —
   Visibility can emit a fresh wrapper around cached embedded data; cycle 52
   incident). Fall back to direct SSH for heartbeats and pending counts. For
   PowerShell pipelines over SSH, use single-quoted bash outer to prevent
   $-expansion (see feedback-ssh-powershell-quoting).
2. For each runner (GPU, CPU):
   a. If alive AND not paused AND pending > 0: healthy, do nothing.
   b. If alive AND paused: healthy (user requested pause), do nothing.
   c. If alive AND idle AND pending > 0: should not happen for >1 minute; if
      persistent, alert.
   d. If dead AND not paused AND pending > 0: relaunch via
      `ssh marsh@home C:/dev/hd-instrument/.venv/Scripts/python.exe C:/dev/hd-instrument/tools/cutover.py --gpu-only` (or --cpu-only) with --skip-healer.
   e. If dead AND paused: respect the pause; do not relaunch.
   f. If running AND wall-clock > 4 hours: stuck. Investigate. May need to
      kill via cutover and re-queue.
3. Append a one-line entry to notes\queue_health_log.md:
   `<ts> | GPU=<status>:<current> | CPU=<status>:<current> | pending_gpu=N | pending_cpu=M`
4. If anything required attention: update notes\queue_health_alert.md with
   the alert message. Otherwise empty the file.
5. Append decision log entry only when you took an action (relaunch, alert).
6. Read notes\active_protocols.md and implement any new PROT-* applicable to
   queue_health that hasn't been done.

RULES:
- NEVER kill an experiment that's actively running unless wall > 4 hours OR
  user explicitly requests via --hard pause.
- NEVER queue experiments yourself. Only Experiment Dev queues via queue_add.py.
- NEVER relaunch a runner if PAUSED file exists.
- Atomic file writes always.
- The user-override "do it now" supersedes the strict invariant — relaunch
  proactively if asked, even when pending=0.

BLOCKER: if a runner is dead AND PAUSED is unset AND cutover fails to
relaunch, write notes\queue_health_blocker.md and stop attempting (don't
loop relaunches on a broken system).

ScheduleWakeup pattern:
- delaySeconds=270 (cache-warm window, satisfies 5-min invariant)
- prompt=`/loop /queue-health-cycle` (PROT-003 short-form)
