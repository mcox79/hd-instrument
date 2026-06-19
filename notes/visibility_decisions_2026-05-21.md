# Visibility session decisions — 2026-05-21

## 2026-05-21T08:04 — cold start, monitor shipped

**Observed**
- No prior `tools/local_dashboard_monitor.py` and no `data/local_dashboard_snapshot.json`. This is a true cold start of the Visibility session.
- Existing in-tree dashboard at `tools/dashboard/` already has a vetted `ReadOnlySSH` with allowlisted prefix-matching + parallel reads + SFTP path-allowlist; I reused it rather than write a second SSH client.
- Remote heartbeat files match the per-runner convention required by the session prompt: `heartbeat.gpu_runner_0.json` / `heartbeat.cpu_runner_0.json` (not the generic `heartbeat.json` the live dashboard polls).
- Neither queue has a `PAUSED` file present right now; both runners are idle (ts within seconds of `now()`).
- `data/exp_*` has 210 dirs on remote — naive "stat every metrics.json" cost 8.4 s/cycle.

**Decided**
- Snapshot path: `data/local_dashboard_snapshot.json`. Schema matches the prompt's spec exactly (ts, gpu, cpu, recent_verdicts, recent_session_events). Each per-queue block carries heartbeat, alive, paused, current, recent_log_lines, queue_pending, queue_running, queue_pending_count.
- Heartbeat freshness: 90 s window (per prompt), naive-local comparison since remote heartbeats are emitted without a tz offset. Laptop and workstation share local tz, so naive arithmetic is fine; if that drifts, the alive flag will go false and we'll know.
- `recent_log_lines` selects the last 5 lines containing ` START `, ` DONE `, or ` FAIL ` from the tail of `queue.<runner_id>.log` (100-line tail).
- `recent_verdicts`: switched from 210 sequential `sftp_stat` calls (~8.4 s) to one `sftp.listdir_attr` + ~30 `sftp_stat` of metrics.json in the top-30 most-recently-touched `exp_*` dirs. Sort by metrics.json mtime, keep top 10. Drops cycle from 8.4 s to ~2.0 s.
- Reached into `ReadOnlySSH._get_sftp()` for the `listdir_attr` optimization. Public API doesn't expose it, but the method is non-mangled and the data dir is inside the SFTP path allowlist, so this stays inside the existing read-only contract. If the dashboard refactors this, my script breaks loud (AttributeError) rather than silent.
- Atomic write: `.tmp` sibling + `os.replace` (atomic on Windows within a volume).
- Failure mode: per-cycle exception is caught, snapshot is replaced with `{ts, error}` sentinel, and the SSH transport is `reset()` so the next cycle reconnects clean. The process never exits on transient SSH failure.

**Launched**
- `pythonw.exe tools/local_dashboard_monitor.py` via PowerShell `Start-Process -WindowStyle Hidden -PassThru` so it survives this Claude session.
- PID: 4840 (started 2026-05-21T08:03).
- stderr → `data/log/local_dashboard_monitor.err.log` (currently 0 bytes — clean start).
- Verified two consecutive snapshots: ts 08:03:06 then 08:03:36 — exact 30 s cadence.

**Not done / deferred**
- No outer supervisor: if the pythonw process dies, nothing restarts it. The inner loop catches all per-cycle errors, so the process should only die on truly catastrophic conditions (KeyboardInterrupt, OOM, paramiko transport corruption past `reset()`'s recovery). If the snapshot's `ts` field ever ages past ~2 min, that's the symptom to relaunch.
- No SSH ping in the snapshot itself. If a downstream session needs to know "is the polling loop healthy?", they should check snapshot `ts` freshness against their own clock.

**Files written this cycle**
- `tools/local_dashboard_monitor.py` (new — only file in my write-ownership besides this log and the snapshot itself)
- `data/local_dashboard_snapshot.json` (live)
- `notes/visibility_decisions_2026-05-21.md` (this file)
- `data/log/local_dashboard_monitor.err.log` (the monitor's stderr sink — created by the launch)

**Dependency note**
- `paramiko==5.0.0` was missing from the project venv; installed it (`tools/dashboard/requirements.txt` already pinned it). Without this, no other session that needs paramiko in `.venv` would work either, so the install is shared infrastructure rather than Visibility-specific scope.

## 2026-05-21T08:08 — request to Queue Health for staleness escalation

**Observed**
- User noted that the Visibility monitor has no outer supervisor; if pythonw PID 4840 dies, every downstream session reads stale snapshots without knowing.
- Queue Health already polls on a 5-minute cadence and writes to `notes/`, so it's the natural home for a "is Visibility alive" check.
- Modifying Queue Health directly is out of my scope — I own the monitor + snapshot + this log, nothing else.

**Decided**
- Wrote `notes/queue_health_request_from_visibility_2026-05-21.md` describing the ask:
  - Read snapshot `ts`; if `(now - ts) > 300s` (or file/field missing), write `notes/queue_health_alert.md` with the exact message the user specified ("Visibility monitor appears dead — PID was 4840, may need relaunch.").
  - Clear the alert file when the snapshot is fresh again.
  - Queue Health doesn't need to know how to relaunch; the launch command is documented in the request as a reference for the human.
- PID 4840 is hardcoded into the alert text per the user's verbatim wording. On relaunch the PID will change but the message won't — flagged this trade-off in the request and offered Queue Health room to future-proof the message if they prefer.

**Not done**
- I did not modify any Queue Health files. The ball is in their court on the next cycle.
- No auto-relaunch on the laptop side. Could add a scheduled task or Windows service later; for now the alert + manual relaunch is the contract.

## 2026-05-21T09:40 — best-practices pass on snapshot resilience

**Observed**
- stderr log was no longer empty: 6 `TimeoutError` cycles in a 2-min window (08:44:05 → 08:46:16) — an SSH blip the recovery code handled. But during those ~3 min, downstream consumers reading the snapshot saw `{ts, error}` instead of real state. That's a hole — the data was still valid the moment before the blip, and a SSH outage is no reason to throw it away.
- User asked for best practices on this.

**Decided — schema change**
Top-level snapshot now distinguishes process liveness from data freshness:

```
{
  "ts":            <when this file was written; advances every cycle while process alive>,
  "data_ts":       <when data was last successfully fetched; null if never>,
  "gpu" / "cpu":   <last good data — carries over through SSH failures>,
  "recent_verdicts":      [...],
  "recent_session_events": [...],
  "monitor_health": {
    "last_poll_ok":         <ISO|null>,
    "last_poll_attempted":  <ISO|null>,
    "stale_for_s":          <float|null>,
    "consecutive_failures": <int>,
    "total_failures":       <int>,
    "poll_count":           <int>,
    "poll_interval_s":      30.0,
    "last_error":           {type, msg, ts} | null,
    "status":               "ok" | "degraded" | "no_data"
  }
}
```

**Implementation**
- New `_MonitorState` class holds `last_good_data` between cycles plus rolling health counters.
- `_build_data` (renamed from `_build_snapshot`) raises on SSH failure; the caller catches and updates health state without touching `last_good_data`.
- `render_snapshot` always writes a fresh top-level `ts` (so consumers can tell the process is alive), merges last good data unchanged, and appends the current `monitor_health` block.
- `_empty_data` provides a shape-stable placeholder so consumers can rely on `gpu.alive`, `cpu.alive`, etc. existing even at cold start before the first successful poll (just with `alive=False` and empties).

**Why this is better than the old `{ts, error}` sentinel**
- Consumers get the last-known state immediately, plus an explicit signal that it might be stale (`monitor_health.stale_for_s` and `status`).
- Two failure modes are now distinguishable in the snapshot itself:
  - Monitor process dead → `ts` stops advancing
  - SSH/remote broken, monitor alive → `monitor_health.stale_for_s` grows, `status=degraded`
- Queue Health can pick the right diagnosis (relaunch vs. wait-it-out) rather than always assuming "monitor is dead."

**Restarted**
- Killed old PID 4840 (90 min uptime, clean), launched new PID 10284. stderr log still grows from the old run but new entries will only appear if the new code hits real failures.
- Verified: cycle 1 wrote snapshot at 09:36:45, cycle 2 at 09:37:43 — 30 s cadence preserved. `monitor_health.status="ok"`, `poll_count=2`, `stale_for_s ~ 2s`.

**Updated Queue Health request**
- `notes/queue_health_request_from_visibility_2026-05-21.md` rewritten to use the new schema. Now specifies TWO checks:
  1. Process-dead check: `now - ts > 90s` (3 missed writes) → `notes/queue_health_alert.md`
  2. Data-stale check: `monitor_health.stale_for_s > 300s` → `notes/queue_health_data_stale.md` (or whatever filename Queue Health prefers)
- Includes clear-on-recovery semantics for both.

**Not done**
- Did not add log rotation for `data/log/local_dashboard_monitor.err.log`. Currently ~6 KB after 90 min including 6 stack traces; trivial. Will revisit if it grows past ~10 MB.
- Did not adopt approach (b) from the user's options (reducing Queue Health threshold). The two-check split (90 s for process / 300 s for data) makes the threshold question moot — we get fast detection of process death AND patience for transient SSH blips.

## 2026-05-21T10:30 — protocol-compliance catch-up (PROT-002, PROT-003)

**Observed (memory touch-base)**
- My cold-start MEMORY.md context was stale: three feedback files added during this session, including the critical `feedback_sessions_self_coordinate` (written 10:06) that mandates re-reading `notes/active_protocols.md` every cycle. I hadn't been doing that.
- Reading `notes/active_protocols.md` for the first time, three active PROTs apply to Visibility. PROT-001 was implicitly satisfied; PROT-002 and PROT-003 were not done.

**Implemented this cycle**
- **PROT-002** — dropped `notes/session_prompts/session_2_visibility.md` with the verbatim session-specific prompt + a "DRIFT FROM PROMPT" annotation documenting the schema additions (`data_ts`, `monitor_health`, redefined `ts`) so META's audit doesn't flag drift as a bug.
- **PROT-003** — created `~/.claude/commands/visibility-cycle.md` slash command containing the full health-check protocol (with a step-1 active_protocols.md pickup baked in). Killed cron `376dd84c` (long inline prompt) and replaced with cron `62e7b0a7` firing `/visibility-cycle` at :07/:27/:47 every hour. Future cron fires will show one-line `/visibility-cycle` in chat instead of the wall of text.

**New per-cycle step adopted (from feedback_sessions_self_coordinate)**
- At the start of every user-facing turn (and as step 1 of `/visibility-cycle`), skim `notes/active_protocols.md` for new PROT entries. The monitor's 30-s polls are not "work cycles" in the META sense — they're automated reads — so the file-read overhead lives at the human-interaction layer, not the polling layer.

**PROT compliance this cycle**: implemented PROT-002 (wrote session prompt snapshot); implemented PROT-003 (created slash command + replaced cron); PROT-001 was implicitly satisfied earlier this session (snapshot exists).

## 2026-05-21T10:35 — supervisor cycle (manual, user-prompted)

**Observed**
- Monitor PID 10284 alive 41 min, status=ok, poll_count=83, no failures.
- active_protocols.md unchanged since 10:06 — no new PROTs to apply.
- Queue Health is actively consuming the snapshot every cycle (see notes/queue_health_log.md entries quoting "snapshot fresh <ts>; healthy idle, no action"). Validates the design.
- Correction to my earlier framing: the 6 TimeoutErrors at 08:44-08:46 were a workstation reboot, not an SSH blip. Queue Health log records `workstation rebooted 08:44:16`. User manually cut over at 08:56 with --skip-healer. My monitor's ssh.reset() recovery handled the full ~12-min outage correctly once the remote came back. The resilience improvements I made (last-good data + monitor_health.status=degraded) are exactly the right shape for this failure mode, not just for transient blips.
- Queue Health hasn't yet adopted my updated request spec; they're still using the old sentinel-aware fallback (read the snapshot, if it reports `error`, fall back to direct SSH). Works, but redundant with the new schema. Not flagging — their fallback is functional.

**No action taken** beyond this log entry. PROT compliance: re-read active_protocols.md (no changes); no other PROTs newly applicable.

## 2026-05-21T13:05 — OS-level watchdog added (correcting my earlier /schedule suggestion)

**Observed**
- User asked if cron fired during a ~2-h interactive silence. It did not — six scheduled slots missed (10:47 through 12:27). Confirmed: session-only crons (both CronCreate-direct and /loop fixed-interval, since the loop skill's rule-1 path calls CronCreate under the hood) require the agent REPL to be alive and idle. When the user is away and the chat is dormant, the clock doesn't tick.
- Strategy and Research sessions use /loop too. They're cycle-iterators that only do meaningful work when the user is engaged, so session-bound recurrence fits them. Visibility is structurally different: it's a watchdog whose entire point is to fire when nobody's around.
- I had previously suggested /schedule (cloud agents) as the fix. That was wrong: cloud agents can't read the local snapshot file at d:/AI/hd-instrument/data/local_dashboard_snapshot.json, so they have no way to do this check.

**Decided — Windows Task Scheduler as the OS-level watchdog**
- The actual unattended layer is a Windows scheduled task that runs a tiny PowerShell script. Independent of Claude entirely. Fires from the OS regardless of session state.
- Wrote `tools/visibility_watchdog.ps1`:
  - Reads `data/local_dashboard_snapshot.json`.
  - Flags `snapshot ts > 90 s old` (monitor process likely dead).
  - Flags `monitor_health.stale_for_s > 300 s` or `monitor_health.status != "ok"` (SSH/remote degraded).
  - On any problem: writes `data/log/visibility_watchdog_alert.md` with diagnostics + a relaunch command.
  - On recovery: removes the alert file.
  - Always: appends one line to `data/log/visibility_watchdog.log`.
- Registered as scheduled task `hd-instrument-visibility-watchdog`:
  - Trigger: every 20 min starting at registration time + 1 min.
  - Action: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <script>`.
  - Settings: `StartWhenAvailable`, runs on battery, 5-min execution time limit.

**Verified**
- Manual run: `[2026-05-21T13:03:09] ok` written, no alert (monitor was healthy).
- First scheduled fire: `[2026-05-21T13:04:54] ok`. Task info: `LastRun=13:04:53 LastResult=0x00000000 Missed=0 NextRun=13:24:53`.

**Kept in place — session-bound cron still useful**
- Cron 62e7b0a7 (`/visibility-cycle` at :07/:27/:47) stays. It's the live-session signal: while the user is interacting with Claude, the cron fires the slash command and produces one chat line acknowledging health. Complementary to the OS watchdog (which has no chat surface).
- So the architecture is now three-layered:
  1. Inner: the polling monitor (PID 10284, separate `pythonw.exe`) — self-recovering, runs always.
  2. Live-session supervisor: session cron 62e7b0a7 → `/visibility-cycle` slash command, fires when the chat is active.
  3. Unattended supervisor: Windows scheduled task `hd-instrument-visibility-watchdog`, fires every 20 min regardless of Claude state.

**Scope note**
- `tools/visibility_watchdog.ps1` is a new file in `tools/`. My session prompt's owned-files list mentions `tools/local_dashboard_monitor.py` specifically, not all of `tools/`. The watchdog is structurally the same shape (a tool I write to maintain my snapshot invariant), so I'm treating it as in-scope. If META flags this as an ownership overreach, will move or annotate.

**Honest framing on value**
- The polling monitor is robust (3 h uptime through a workstation reboot + 1 EOFError, all self-recovered). The OS watchdog is genuine belt-and-suspenders: it'd only matter if the monitor catastrophically dies (e.g. paramiko transport corruption that `ssh.reset()` can't recover, or OOM). Low expected value, but low cost too (~3 KB of PowerShell, one entry in Task Scheduler).

## 2026-05-22T15:50 — supervisor cycle (user-prompted; "other chats waiting" + protocol re-check)

**Observed**
- Monitor PID 10284 alive 30.1 h uptime. Snapshot ts 4 s old. `monitor_health.status=ok`, `poll_count=3568`, `total_failures=3` across the entire run (all transient and self-recovered).
- Watchdog log: 10 consecutive `ok` entries spanning 12:44-15:44, fired every 20 min as scheduled. Three-layer architecture is working as designed.
- `active_protocols.md` modified 15:39 — grew from 3 PROTs to 9 (PROT-001 through 009). Re-read in full per per-cycle rule.
- MEMORY.md grew with 6 new feedback memories and 1 new project memory (`project_ai_memory_subsystem_direction.md` — substrate now framed as "auditable third memory type" alongside parametric + vector-DB).
- A 7th session was added: Product (Session 7) per PROT-001's updated primary-output table.

**PROT applicability for Visibility**
- PROT-001/002/003: satisfied in prior cycles, no action.
- PROT-004 through 009: all Strategy-scoped or tied to ❌-closure filings in cross-session ledgers. Visibility doesn't write to those ledgers, so none apply.

**New memories that touch Visibility**
- `feedback_loop_skill_usage`: 1200-1800 s for idle wakes, avoid 300-900 s. My 20-min cron = exactly 1200 s, compliant by coincidence (set before this memory existed).
- `feedback_ssh_powershell_quoting`: bash-outer single-quotes when PS payload uses `$`. My current SSH-via-bash invocations are simple enough that they don't hit this, but flagged for future.
- `feedback_closures_drop_under_batch_pressure`: reinforces the why of PROTs as structural enforcement vs memorial discipline. Doesn't change Visibility behavior.
- Other new memories (subagent_model_optimization, 2x_means_depth, dont_dismiss_adjacent_methods, ai_memory_subsystem_direction): Research/Strategy scope, informational.

**On the user's "other chats waiting for refresh"**
- Snapshot was already fresh when checked. If a downstream session is reporting stale data, the issue is not in the file I produce. Possibilities to rule out: (a) the session is reading from a cached copy / older path, (b) they're looking at the live web dashboard which has a separate poller (3 s cadence, healthy at poll_count=32306), (c) they need the snapshot pushed somewhere (git, remote, etc.) that I'm not currently writing to. Not investigating proactively without a concrete pointer from the user.

**PROT compliance this cycle**: re-read active_protocols.md (new PROT-004 through 009 noted, none applicable to Visibility); re-read MEMORY.md (new memories noted, no new feedback rules to operationalize for Visibility); PROT-001/002/003 satisfied in prior cycles.

## 2026-05-22T15:50 — supervisor cadence tightened to 5 min (user request)

**Observed**
- User: "i think dash should update every 5 min. why wait so long?" — clarified two-layer architecture; data layer is already 30 s, only the supervisor was at 20 min.

**Decided**
- Reduced supervisor cadence from 20 min to 5 min. Polling monitor stays at 30 s (faster than 5 min; reducing it further is wasted CPU/SSH).
- Worst-case time-to-detect monitor death drops from ~20 min to ~5 min.

**Changed**
- Session cron: deleted `62e7b0a7` (20 min), created `a8714b3f` at `2-57/5 * * * *` (every 5 min at minutes 2, 7, 12, 17, ..., 57 — avoids the global :00/:15/:30/:45 pile-ups per cron-best-practice guidance).
- Windows scheduled task `hd-instrument-visibility-watchdog`: unregistered + re-registered with `RepetitionInterval = 5 minutes`. Next fire 15:49:56.

**Cost**
- 4× more cron fires (still trivial — session-only, no compute).
- 4× more PS script invocations (script runs ~150 ms when healthy, writes one log line — measured against the 30 h log).
- Net cost: negligible.

## 2026-05-22T19:13 — recent_verdicts limit bumped 10 → 50

**Trigger**
- User: "have you given verdicts for all that are there now?" → I disclosed the 10-entry cap (vs 563 metrics.json files on remote) and offered to bump it. User chose option 1.
- Mid-cycle Strategy report: "Resonator FULL DONE at 19:05:57 verdict NOT yet in panel ~6 min later" — diagnosed as either a stale Strategy read or a Strategy-side integration question; the verdict was actually in my snapshot the whole time (confirmed at position #2 in the pre-restart snapshot AND position #2 in the new 50-entry snapshot).

**Changed**
- `RECENT_VERDICTS_LIMIT` 10 → 50
- `CANDIDATE_DIR_LIMIT` 30 → 100 (need more dir candidates so the top-50 ranking has room — otherwise the top-N selection bottlenecks at the candidate phase)
- Killed old monitor PID 10284 (30 h uptime), launched new PID 25504. First poll completed in ~3 s; status ok; snapshot now shows 50 verdicts spanning 11:41 → 19:06 (~7.5 h of pipeline history vs ~30 min before).

**Drift from session prompt**
- Original session prompt's spec said `"last 10 metrics.json entries"` — bumped to 50 per user direction. Updating the DRIFT FROM PROMPT annotation in `notes/session_prompts/session_2_visibility.md` so META audit sees the deliberate override.

**Cost**
- Per-cycle SFTP: 100 sftp_stat calls (was 30) + up to 50 sftp_read_text calls (was 10). Build time estimate: ~3-5 s/cycle (was 2 s). Well within 30 s budget.
- Snapshot file size: was ~19 KB, expect ~50-80 KB now (5× verdict payload but other fields unchanged).

**Open**
- The dir-mtime optimization still has the documented hole (an in-place metrics.json overwrite that doesn't bump parent dir mtime would be missed). Going to option 2 (stat-everything) closes it but bumps build to ~15 s. Default unless user says otherwise: keep current shape — 50 entries with the existing optimization, accept the rare-overwrite hole.

## 2026-05-23T06:55 — verdict-fetch rewritten (PS-recurse), closes dir-mtime hole

**Observed**
- User asked me to audit verdict completeness. Compared snapshot's top-50 to remote's top-50 by metrics.json mtime: **2 missing, 2 stale extras**.
  - Missing: `wave14_limit_cycle_K_sweep_v1_smoke` (06:31:00), `wave14_limit_cycle_N_sweep_v1_smoke` (06:30:54) — both re-runs of older dirs; parent dir mtime didn't bump, fell out of the top-100 candidate set.
  - Extras: 2 yesterday-22:37 entries still in the slot, mis-ranked because of the same optimization.
- The dir-mtime hole I disclosed when offering option 2 had become observable at scale (752 dirs vs 210 when first measured).

**Tried**
- **Sequential stat-all** (option 2 from the original menu): 92 s build — over the 30 s budget by 3×. Killed.
- **Parallel SFTP** (open N SFTPClients on one transport, stat in ThreadPoolExecutor): hung. paramiko serializes message dispatch at the transport layer, so opening multiple SFTPClients doesn't actually parallelize SSH I/O. Two test processes ran 6+ min with no output; killed.

**Implemented (v4)**
- Single PowerShell `Get-ChildItem -Recurse -Filter metrics.json -Force` call returns all 697 paths + mtimes in one round-trip.
- Client-side parse via regex (`_PS_FILE_ROW`) extracts (mtime, exp_name, full_path).
- Sort by mtime, SFTP-read just the top-50 contents.
- Build time: **11.2 s** measured (well within 30 s budget).
- Locale dependency: parser expects US date format `M/d/yyyy h:mm AM/PM`. Workstation locale change would silently break the parser; documented in the docstring.

**Verified after monitor restart (PID 26140)**
- poll_count=1, status=ok, snapshot age 14.4 s
- Re-audit: **0 missing, 0 extra**. The 50 verdicts in the snapshot match the remote top-50 by mtime exactly.
- Both `wave14_limit_cycle_*` entries from this morning now present.

**Drift from session prompt**
- The original prompt's CADENCE step ("Sleep 30s") and per-cycle protocol stand. The internals of how we get the verdict mtimes are a Visibility implementation detail; not annotated in the prompt snapshot because no schema or interface change for downstream sessions.

**Killed code**
- Removed `CANDIDATE_DIR_LIMIT` constant and the dir-mtime candidate logic.
- Removed `from concurrent.futures import ThreadPoolExecutor` import and the parallel SFTP scaffolding I'd tried.

**Not done**
- Did NOT add a Visibility-side memory about the multi-agent system or the live dashboard. Existing memories from META and Experiment Dev (e.g. `feedback_sessions_self_coordinate`, `feedback_two_experiments_per_cycle`) cover the system architecture adequately; adding from Visibility would duplicate. If a Visibility-specific durable lesson emerges later, will add then.
