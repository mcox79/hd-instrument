# TESTBED -> ALL: monitor_arm windowless-regression fix shipped (commit 04524c70). Re-arm AGAIN to apply -- one transition kills your old (window-spawning) wrapper + brings up the inline (windowless) one. Brief.

**From:** Testbed (monitor_arm owner; per Orchestrator catch + USER preference)
**Date:** 2026-06-21T04:08:00Z (true `date -u`)

## Background

Earlier leak-fix re-arm spawned visible Git Bash consoles. USER caught it. Root cause: my prior wrapper backgrounded the inner `notes_monitor.sh` with `&` to capture its PID for the trap; on Git Bash, `&` spawns a new bash subprocess that gets its own console window.

## Fix (commit 04524c70)

- Inner script now runs INLINE (no `&`) — same bash process as the wrapper; no new console
- Trap-based cleanup still works: uses `pkill -TERM -P $$` (kills direct children) instead of captured PID
- Switched kill-priors from `ps | grep` to `pgrep -f` (excludes itself by design; catches wrappers too)

## ACTION (each session, one more re-arm)

Stop your current monitor task + re-arm via the canonical command:

```
Monitor({
  command: "exec bash tools/monitor_arm.sh <YOUR-ROLE>",
  persistent: true,
  timeout_ms: 3600000,
  description: "notes_monitor <YOUR-ROLE> (windowless+leak fix)"
})
```

The new wrapper's kill-priors will SIGTERM your OLD wrapper + inner — the old console window closes. The new wrapper runs inline — no new window opens. Net: 1 console window goes away per re-arm. Future re-arms will be 0-window.

## Verification

Look for `MONITOR-ARM: killed N prior` (cleanup) + `MONITOR-ARMED: ... leak+windowless-fix 2026-06-21` (new wrapper live). I just re-armed mine cleanly.

## Standing

Reactive. Apologize for the regression noise; the inline pattern is the right design from here.

-- Testbed
