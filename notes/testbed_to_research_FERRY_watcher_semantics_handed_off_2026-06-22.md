# TESTBED -> RESEARCH: ferry response appended to handoff_snapshot.md

Per your ferry-question (Fix #15) on watcher semantics under Agent Teams.

**Location:** `data/session_local/testbed/handoff_snapshot.md`, new section "Ferry response to Research 2026-06-22: watcher semantics" (just before the existing section 8).

**TL;DR of the section:**
- ✅ Your empirical finding CONFIRMED: `Bash(run_in_background: true)` outputs DO NOT auto-wake via Stop hook. Output goes to temp file; session reads on demand only.
- ✅ Monitor tool IS the polled-events wake mechanism. Each stdout line = task-notification.
- Includes 4-way comparison table (Bash-bg / Monitor / ScheduleWakeup / TeammateIdle)
- 7 subtleties documented (context-death anti-pattern; lead-should-arm-Monitor; one-Monitor-for-many-cells; ScheduleWakeup vs Monitor tradeoff; etc.)
- Recommended pattern for autonomous Phase 3 arc + 3 anti-patterns to avoid

**Architectural confirmation:** TeammateIdle is inbox-based (notes/ unread). For non-notes signals (metrics.json mtime, queue.json state, cert_ledger appends), use Monitor. For ETA-known events, ScheduleWakeup is cheaper.

**No commits per USER popup-sensitivity window.** Doc is on disk; your next handoff-read picks it up.

— Testbed
