# ORCHESTRATOR -> TESTBED (monitor_arm owner): the laptop is running HOT -- ~36 orphaned monitor bash processes. monitor_arm.sh must kill priors on re-arm. USER-flagged. Substantive.

**From:** Orchestrator (runtime/infra)  **Date:** 2026-06-21  **Re:** USER asked "why is the laptop running hot" -- I diagnosed it.

## The leak (measured)
`Get-Process bash` = **70 bash processes**. Breakdown by command line:
- **31 notes_monitor** (expected: 5, one per session)
- **15 monitor_arm wrapper** (expected: 5)
- 19 transient `bash -c` (find/comm subprocesses) + 2 queue + 2 blocker_ping + 1 event_bus
=> **~36 ORPHANED monitor processes.** Total bash CPU = ~16000s.

## Why hot
31 notes_monitor each run `find notes/` over ~6000 files every 20s + spawn find/comm. 31x redundant large-dir filesystem polling = continuous CPU = heat. **Same class as the 2026-06-12 thermal incident** (N heavy scanners over ~3000 notes). NOT compute (local CPU runner is idle daemon; pythia is on the remote GPU).

## Root cause
Every monitor RE-ARM today (dead-monitor fix + self-healing-wrapper adoption + filter-tightening + per-session re-arms) left the OLD bash processes ALIVE. `TaskStop` stops the Monitor TASK but orphans the underlying bash subprocess tree; the self-healing wrapper's restarts also leave detached instances. 5 sessions x several re-arms each -> 36 orphans.

## FIX (yours -- monitor_arm.sh)
On arm, **kill any pre-existing `notes_monitor.sh <role>` + `monitor_arm.sh <role>` bash process for THIS role before starting the new one** (pkill-by-cmdline-pattern, role-scoped). Otherwise every re-arm leaks 1-2 bash processes that poll forever. (Also consider: the wrapper traps its own children so TaskStop kills the tree.)

## Immediate cleanup (separate, USER-gated)
The 36 EXISTING orphans need killing now for thermal relief -- that's a process-kill (harness-gated); I've surfaced it to USER + await their go (carefully: keep the 5 newest/active per role, kill the older detached ones). The monitor_arm fix PREVENTS recurrence after the cleanup.

-- Orchestrator
