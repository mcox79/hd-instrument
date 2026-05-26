---
snapshot_taken: 2026-05-21
charter_version: 2026-05-21 (see ./charter.md)
session: 2 — visibility
---

ROLE: maintain a fresh local snapshot of remote experiment state so other
sessions read it cheaply.

INVARIANT: the snapshot file at data\local_dashboard_snapshot.json reflects
the remote workstation's state as of <= 60s ago.

FILES YOU OWN (only writer):
- d:\AI\hd-instrument\data\local_dashboard_snapshot.json
- d:\AI\hd-instrument\tools\local_dashboard_monitor.py (the polling script itself)
- notes\visibility_decisions_<date>.md

FILES YOU READ (via SSH only):
- C:\dev\hd-instrument\data\overnight_queue\heartbeat.gpu_runner_0.json
- C:\dev\hd-instrument\data\overnight_queue\queue.json
- C:\dev\hd-instrument\data\overnight_queue\queue.gpu_runner_0.log (tail)
- C:\dev\hd-instrument\data\overnight_queue\PAUSED (existence check)
- C:\dev\hd-instrument\data\remote_cpu_queue\heartbeat.cpu_runner_0.json
- C:\dev\hd-instrument\data\remote_cpu_queue\queue.json
- C:\dev\hd-instrument\data\remote_cpu_queue\queue.cpu_runner_0.log (tail)
- C:\dev\hd-instrument\data\remote_cpu_queue\PAUSED (existence check)
- C:\dev\hd-instrument\data\session_events.jsonl (tail)
- C:\dev\hd-instrument\data\exp_*\metrics.json (recent verdicts)

FILES YOU NEVER TOUCH:
- Anything in experiments\, preregs\, hdlab\
- notes\substrate_capability_map.md
- notes\active_priorities.md
- Anything other sessions own

SNAPSHOT SCHEMA (the JSON you write):
{
  "ts": ISO-8601 timestamp of this snapshot,
  "gpu": {
    "heartbeat": <contents of heartbeat.gpu_runner_0.json or null>,
    "alive": bool (heartbeat ts within 90s of now),
    "paused": bool (PAUSED file exists),
    "current": current experiment name or null,
    "recent_log_lines": last 5 START/DONE/FAIL lines,
    "queue_pending": list of pending experiment names,
    "queue_running": list of running experiment names,
    "queue_pending_count": int
  },
  "cpu": <same shape>,
  "recent_verdicts": [ last 10 metrics.json entries with name+verdict+verdict_msg+elapsed_s+mtime ],
  "recent_session_events": [ last 30 lines from session_events.jsonl ]
}

CADENCE: poll every 30 seconds.

PER-CYCLE PROTOCOL:
1. SSH and read the files in FILES YOU READ above.
2. Assemble the snapshot dict per schema.
3. Atomic write to data\local_dashboard_snapshot.json (.tmp then rename).
4. Sleep 30s.

INITIAL TASKS (cold start):
1. Read the universal charter and the MEMORY.md it references.
2. Write tools\local_dashboard_monitor.py implementing the per-cycle protocol.
3. Verify a single manual run produces a valid snapshot file.
4. Launch the monitor as a detached background process on the laptop.
5. Verify the snapshot updates every 30s.
6. Append your initial decision log entry.
7. Report to user: snapshot path, launch PID, sample contents.

SCOPE RULES:
- You only READ from remote. You only WRITE to one local file (+ your script
  and decision log).
- If a remote file doesn't exist or read fails, record null in the snapshot
  rather than crashing.
- If the script itself dies, restart it. Do not silently let it stay dead.

BLOCKER: if remote SSH connection is broken, write notes\visibility_blocker.md
and pause polling until resolved.

---

## DRIFT FROM PROMPT (Visibility-only annotation, not part of prompt)

The schema actually written has additional fields beyond what this prompt specifies:
- top-level `data_ts` (when data was last successfully fetched)
- top-level `monitor_health` block (status, stale_for_s, consecutive_failures,
  last_error, etc.)
- the `ts` field's semantics shifted: it now means "when this file was last
  written" (always fresh while monitor process alive), not "when data was
  fetched". `data_ts` carries the latter.
- per-queue blocks are unchanged.

Rationale: a transient SSH failure should not wipe last-good data from the
snapshot. The added fields let downstream consumers distinguish "monitor
process is dead" (ts stale) from "SSH/remote broken, monitor alive"
(stale_for_s growing, status=degraded). See
notes\visibility_decisions_2026-05-21.md "best-practices pass on snapshot
resilience" for full reasoning.

**Verdict-count override (2026-05-22)**: prompt says "last 10 metrics.json
entries"; user explicitly directed bump to 50 to give Strategy more pipeline
history. Decision in notes\visibility_decisions_2026-05-21.md "recent_verdicts
limit bumped 10 → 50".
