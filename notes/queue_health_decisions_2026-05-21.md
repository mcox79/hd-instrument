# Queue Health decisions — 2026-05-21

## Cycle 1 (07:57-07:58) — bootstrap

**Observed:**
- Both runners alive and idle. GPU heartbeat 07:57:29 pid 27080; CPU heartbeat 07:57:27 pid 124796.
- Queues empty of pending work: GPU 81 completed / 12 failed / 7 inconclusive, CPU 20 completed / 10 failed. No `pending` status anywhere.
- No PAUSED flag in either queue dir.
- `runner_v2_prod.py` on remote had no PAUSED awareness (grep for "PAUSED" returned nothing).
- `tools/pause_runner.py` did not exist on remote.

**Decided + executed:**
1. Pulled remote `experiments/runner_v2_prod.py` and `tools/cutover.py` to local mirror.
2. Patched runner_v2_prod.py main loop with PAUSED-aware idle (before `claim_next_pending`, check `queue_dir/PAUSED`, set status="paused", sleep `POLL_INTERVAL_S`, do NOT advance `consecutive_empty`). 5 LOC + comment.
3. Wrote `tools/pause_runner.py`: CLI for `--gpu/--cpu/--both/--resume/--hard/--status`. `--hard` writes PAUSED then delegates to `cutover.py --gpu-only` / `--cpu-only` which kills the running experiment, atomically requeues it via safe_queue, and relaunches the runner (which immediately sees PAUSED and idles).
4. scp'd both files to remote. Confirmed remote runner now has "PAUSED" at lines 293/296/298.
5. Ran `cutover.py --skip-healer` to restart both idle runners and pick up the patch. Result: GPU pid 39160 idle, CPU pid 150568 idle. Process listing confirms one runner chain per queue, no duplicates from prior ssh-survival.

**Rationale for cutover during idle:** runners must restart to pick up the patched code. Doing so while idle (queues empty, no `running` entries to requeue) is the lowest-disruption window. Healer left untouched (not in scope).

**Next:** start 5-min poll loop. Healthy state should produce log lines only; alerts only on anomaly.

## Cycle 11 (08:54) — workstation reboot ALERT

**Observed:**
- Snapshot at 08:51:36 marks both runners `alive=false`. Heartbeats frozen since 08:43:56 (CPU) / 08:43:57 (GPU).
- Direct SSH: no python.exe processes on remote (PIDs 39160 and 150568 absent).
- `Win32_OperatingSystem.LastBootUpTime = 05/21/2026 08:44:16` — workstation rebooted ~20s after heartbeats froze.
- Runner queue logs end at last `DONE` line for each runner, no graceful `exiting` message → killed by OS shutdown, not graceful idle-exit.
- Both `data/overnight_queue/queue.json` and `data/remote_cpu_queue/queue.json` report 0 pending and 0 running.

**Decided:**
- **No relaunch this cycle.** Charter invariant: "if pending experiments exist AND no PAUSED flag is set, the corresponding runner is alive within 5 minutes." With pending=0, the conditional does not fire.
- **Wrote alert file** so the user/META session can see the reboot and decide whether to relaunch proactively.
- Healer is owned by another session — not in my scope to relaunch.
- Next 5-min cycle will catch any `pending > 0` and relaunch within the window.

**Rationale:** strict reading of charter scope. Don't take unsolicited action on a runtime ambiguity; alert and let the system + user decide.

## Cycle 11b (08:56) — user override: relaunch now

**Observed:** user instructed "do it now" — proactive relaunch despite pending=0.

**Decided + executed:**
- Ran `ssh marsh@home C:/dev/hd-instrument/.venv/Scripts/python.exe C:/dev/hd-instrument/tools/cutover.py --skip-healer`.
- Cutover step 4 confirmed the stale PIDs (39160/150568) were already dead.
- New runners launched: GPU pid 7760, CPU pid 40128. Cutover wrapper PIDs: GPU=34044, CPU=37476.
- Verified GPU heartbeat at 08:56:27 reports `status=running, current=wave14s_chargeflip_forensics_v1` — work appeared in the queue between cycle 11 (pending=0 then) and the relaunch, and the new runner claimed it immediately. The user's call to relaunch ahead of the invariant was vindicated.
- Cleared `queue_health_alert.md` (runners back, no alert state).
- Healer NOT relaunched (owned by another session).

**Rationale:** user override is authoritative per charter ("treat user instructions as authoritative"). Action was in-scope (cutover relaunch). The vindicating signal is that GPU was working a fresh experiment within seconds of restart, indicating work was indeed about to arrive.

## Cycle 27b (10:21) — PROT-002 + PROT-003 compliance (corrective)

**Observed:** user flagged that I have not been following the /loop-related protocols in MEMORY.md. Re-read `feedback_sessions_self_coordinate.md` (memory) → it says to read `notes/active_protocols.md` every cycle. I have NEVER done this — went 26 cycles without reading it. Two active protocols apply to Queue Health:

- **PROT-002** (one-shot): write verbatim session-specific prompt snapshot to `notes/session_prompts/session_3_queue_health.md`. Not done.
- **PROT-003** (one-shot): wrap long /loop prompts in a slash command under `~/.claude/commands/`. Not done — every wakeup has been re-emitting the multi-paragraph protocol body into chat.

**Decided + executed:**
1. Wrote `notes/session_prompts/session_3_queue_health.md` with my full session-specific prompt (role, files-owned, cadence, per-cycle protocol). PROT-002 done.
2. Wrote `C:/Users/marsh/.claude/commands/queue-health-cycle.md` modeled on the existing `strategy-cycle.md` / `meta-cycle.md`. PROT-003 done.
3. Replaced the next ScheduleWakeup prompt from the long-form charter+protocol wall to `/loop /queue-health-cycle`. Next cycle and all subsequent cycles will show only the short command in chat.
4. Added "Read notes/active_protocols.md every cycle" as step 6 in the session_3 prompt's per-cycle protocol so this miss is structurally prevented next session/cold-start.

**Lesson for memory:** `feedback-sessions-self-coordinate` is a load-bearing memory I should not just read but ENFORCE. The protocol miss is exactly the failure mode `feedback_closures_drop_under_batch_pressure` warns about — a rule "enforced by reading at cold start" silently dropped because nothing in my per-cycle protocol re-checked it. Now baked into the per-cycle list.

PROT compliance this cycle: implemented PROT-002 (wrote session-3 prompt); implemented PROT-003 (created queue-health-cycle.md slash command + re-set /loop). PROT-001 already satisfied (queue_health_log.md exists from cycle 1).

## Cycle 29 (10:25) — PROT-003 verification

First fire under short-form `/loop /queue-health-cycle` at 10:25. Chat now shows only `/queue-health-cycle` instead of the multi-paragraph wall — PROT-003 step 4 verified. NOTE: Skill tool returned "Unknown skill" when /loop's dynamic-mode step 1 tried to invoke `/queue-health-cycle` directly — the slash command file is not registered in the agent's runtime skill catalog (those are baked at conversation start). Practical workaround: Read the slash command file (or remember the cycle protocol) and execute its steps directly. PROT-003's primary goal (clean chat) is met; the agent-side resolution gap is cosmetic and shared by all sessions using this pattern.

## Cycle 52 (12:34) — snapshot data_ts staleness detected

**Observed:** snapshot wrapper `ts=12:33:47` (fresh) but `data_ts=12:16:11` and the embedded `gpu.heartbeat.ts=12:16:11` (17 min stale). My freshness check looked at the wrapper `ts` and would have read stale runner state as authoritative had I not noticed the stuck recent_log_lines.

**Action:** fell back to direct SSH per protocol. Confirmed actual GPU heartbeat is fresh (12:34:26, 126B), pid 7760 alive+idle, queue empty. Queue health is fine; the anomaly is in Visibility's snapshot generation (probably emitting cached embedded heartbeat data while updating the wrapper timestamp).

**Lesson for my freshness check:** evaluate `data_ts` (or the embedded `gpu.heartbeat.ts` / `cpu.heartbeat.ts`) for staleness, not just the wrapper `ts`. The wrapper `ts` only proves Visibility emitted SOMETHING recently, not that the embedded data is fresh. Updated session_3 prompt and slash command to clarify this on next read. Not raising an alert — this is Visibility's domain to fix.

PROT compliance this cycle: no new PROT entries to implement.




