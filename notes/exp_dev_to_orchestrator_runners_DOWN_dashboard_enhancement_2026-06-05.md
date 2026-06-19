# Exp-Dev -> Orchestrator: BOTH RUNNERS DOWN (urgent) + dashboard enhancement request (user-routed)

**From:** Exp-Dev  **To:** Orchestrator (runner-mgmt + dashboard are your lane)  **Inform:** User + Testbed  **Date:** 2026-06-05 ~08:10
**Trigger:** User noticed a job queued for GPU but dashboard shows GPU idle; asked to route a dashboard update to the relevant session. Investigating revealed the real cause.

## CRITICAL: both runner processes are DOWN -- pending jobs will not execute
Diagnosis on marsh@home just now:
- overnight_queue: pending=1 (my per-token Pythia re-queue) running=0. remote_cpu_queue similar.
- `Get-CimInstance Win32_Process -Filter "Name='python.exe'"` -> NO python runner process and NO exp_ process alive.
- schtasks: hd_gpu_runner_0 AND hd_cpu_runner_0 both Status=Ready, **Last Run Time 6/2/2026, Last Result
  -2147023829 (0x80070005 ACCESS DENIED)**. The schtasks have not successfully launched since 6/2.
- nvidia-smi 100% util but compute-apps are ALL desktop (dwm/chrome/code/etc) -- NO experiment compute on GPU.
- Recent jobs DID complete (R-series, CONT-LRN, mode5 ~through 07:5x), so a manually-launched runner loop was alive
  until ~07:5x and has since EXITED/crashed (possibly around the truncated per-token extraction's os._exit(99) at ~07:52).

=> The dashboard showing "GPU idle" is TECHNICALLY CORRECT (nothing is running) but the real problem is the RUNNER IS
   DOWN, so queued work is silently piling up. This blocks ALL sessions' experiments, not just mine.

**ACTION NEEDED (your lane -- runner mgmt):** relaunch the runner loops (singleton-checked per
[[feedback-runner-singleton-check]]; the schtask path-drift + access-denied may need the
[[feedback-runner-schtask-path-drift]] recipe). Also check the heartbeat_watchdog -- if it were alive,
silent_idle/gpu_idle should have fired; it may be down too. Confirm runner PID-file lock after relaunch.

## Dashboard enhancement (the user's explicit request)
Current dashboard cannot distinguish three states that all render as "idle":
  (a) idle + runner ALIVE + no queued work (truly nothing to do)
  (b) idle + runner ALIVE + job starting (transient)
  (c) idle + runner DOWN + work piling up  <-- THE DANGEROUS ONE (current state; invisible today)
**Requested panel additions (per [[feedback-orchestrator-status-visibility]] + [[feedback-watchdog-full-event-set]]):**
1. Runner-alive/heartbeat per queue (last runner-loop heartbeat ts; RED if stale > e.g. 90s) -- detects (c).
2. Currently-running experiment NAME + elapsed per runner (not just idle/busy).
3. Pending-queue-depth per queue (so backlog is visible).
4. A runner_down watchdog event (extend the 13-event set) firing when pending>0 AND no runner heartbeat.

This is purely your lane (dashboard + watchdog). I'm only flagging the requirement + the user request.

## My side (unblocked the moment runners are back)
- per-token Pythia extraction (re-queued, watchdog-fix) -> then EX-CONCEPT-1-real (built, ready).
- CCC-1-EXTRA (FB15k-237 ready), CCC-1-REVISED-v2 (HotpotQA), GPU-OPT-1 -- all ready to build.
- Also: runner repo is 646 commits behind origin/main (Testbed's finding) -- a `git pull --ff-only` is worth doing at the same runner-side window.
**END.**
