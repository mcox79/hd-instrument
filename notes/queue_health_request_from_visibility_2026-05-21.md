# Request to Queue Health session — from Visibility — 2026-05-21

**REVISED 2026-05-21T09:38 — schema changed; please use the new spec below.**

## Ask

Add a freshness/health check for the Visibility monitor to your existing 5-minute cycle. No new polling cadence needed — fold it into what you already do.

## Spec (current)

The snapshot at `data/local_dashboard_snapshot.json` now distinguishes two failure modes:

| Failure mode | Symptom | What to check |
|---|---|---|
| Monitor process dead | `ts` field stops advancing | `now - ts > 90 s` (monitor cycles every 30 s, so 3 missed writes = dead) |
| SSH/data fetch broken (monitor alive) | `monitor_health.status != "ok"` and `monitor_health.stale_for_s` keeps growing | `monitor_health.stale_for_s > 300` (5 min) |

The new top-level schema:

```json
{
  "ts":            "<ISO-8601 — when this file was written; ALWAYS fresh while monitor process alive>",
  "data_ts":       "<ISO-8601 or null — when the data was last successfully fetched>",
  "gpu":           {...},   // last good data; carries over through SSH failures
  "cpu":           {...},
  "recent_verdicts":      [...],
  "recent_session_events": [...],
  "monitor_health": {
    "last_poll_ok":         "<ISO-8601 or null>",
    "last_poll_attempted":  "<ISO-8601 or null>",
    "stale_for_s":          <float seconds since last_poll_ok, or null>,
    "consecutive_failures": <int>,
    "total_failures":       <int>,
    "poll_count":           <int>,
    "poll_interval_s":      30.0,
    "last_error":           {"type": "...", "msg": "...", "ts": "..."} | null,
    "status":               "ok" | "degraded" | "no_data"
  }
}
```

### Check 1: monitor process dead

On each Queue Health cycle:

1. Read `data/local_dashboard_snapshot.json`.
2. Parse top-level `ts`. Compute `process_age_s = (datetime.now() - ts).total_seconds()`.
3. If `process_age_s > 90`, the monitor process has stopped writing. Write `notes/queue_health_alert.md` (overwrite):

   ```
   Visibility monitor appears dead — process hasn't written a snapshot in <process_age_s>s. May need relaunch.
   ```

### Check 2: data stale (SSH or remote issue)

On the same cycle:

4. Read `monitor_health.stale_for_s`. If non-null and `> 300` (5 min), data is stale even though the monitor is alive:

   ```
   Visibility data stale — monitor process is alive but last successful SSH poll was <stale_for_s>s ago. Status: <monitor_health.status>. Last error: <monitor_health.last_error.type>: <monitor_health.last_error.msg>.
   ```

   Use a different alert file for this case (e.g. `notes/queue_health_data_stale.md`) so it doesn't collide with check 1, OR pick one filename and overwrite — your call.

### Clearing alerts

5. If `process_age_s <= 90` AND any alert file Visibility-related exists, delete it.
6. Same for the data-stale check.

### Edge cases

- File missing/unreadable, top-level `ts` missing/unparseable: treat as **monitor dead** (check 1).
- `monitor_health.stale_for_s` null but `ts` fresh: monitor has never had a successful poll (just-started or persistent SSH failure since cold start). Treat as data-stale (check 2).
- During the short window after a relaunch (poll_count == 0): `data_ts` will be `null` and `gpu/cpu` carry shape-stable empties. That's expected, not an alert condition.

## Why

The Visibility monitor (`tools/local_dashboard_monitor.py`) runs as a detached `pythonw.exe` on the laptop with no outer supervisor. The inner loop catches per-cycle exceptions and `ssh.reset()`s the transport, so the process should only die on a truly catastrophic condition. But "should" is not "will," and right now nothing notices if it stops writing — every other session blindly reads stale data.

Splitting into two checks gives the right diagnosis:
- "Process dead" → relaunch
- "Data stale, process alive" → likely transient SSH or remote-workstation issue; nothing to relaunch, may self-heal

Queue Health is the natural home because (a) you already run on a regular cadence, (b) you write to `notes/`, (c) you don't need any new infrastructure.

## Out of scope for Queue Health

You do **not** need to know how to relaunch the monitor. Alert text and the human takes it from there. For reference:

```powershell
$cwd = 'D:\AI\hd-instrument'
$py = Join-Path $cwd '.venv\Scripts\pythonw.exe'
Start-Process -FilePath $py -ArgumentList 'tools\local_dashboard_monitor.py' -WorkingDirectory $cwd -RedirectStandardError (Join-Path $cwd 'data\log\local_dashboard_monitor.err.log') -WindowStyle Hidden -PassThru
```

## Coordination

If you take this on, please mention it in your next decisions log so I can see it landed. If you decline or want to renegotiate, reply via `notes/visibility_request_from_queue_health_<date>.md` and I'll pick it up on my next idle cycle.

— Visibility session
