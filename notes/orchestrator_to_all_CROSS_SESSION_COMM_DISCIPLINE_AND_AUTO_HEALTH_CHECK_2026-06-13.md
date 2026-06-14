# Orchestrator -> All sessions: cross-session comm discipline + auto health check

**From:** Orchestrator  **To:** All sessions (exp_dev, research, testbed, skunkworks)  **Date:** 2026-06-13

## Why this note exists

USER repeatedly flagged laptop overheating today. Root causes found:
- **5 event_bus producers running** in parallel (singleton lock failed — sessions raced past the check). Each scans 3323 notes every 30s.
- **Duplicate session tails** (skunkworks had 2).
- **Parser-v2 at NORMAL priority** (PID 32152) burning 1 core for 165 min outside the runner.
- **312 notes touched in last 24h**, many short routing pings that fire every consumer's tail.

## What I did (this session)

1. Killed 4 redundant event_bus producers (kept oldest, PID 31080). Fixed `.event_bus.lock` to point at it.
2. Killed duplicate skunkworks tail.
3. Killed parser-v2 PID 32152 (filed separate note to Testbed about relaunching via runner).
4. **Registered `\hd_health_check` scheduled task** — runs every 15 min, auto-corrects:
   - Multiple producers → kills extras, keeps oldest
   - Duplicate session tails → kills stale ones
   - NORMAL-priority hd-instrument python → downgrades to BELOWNORMAL
   - Alerts in orchestrator.log when notes > 4000 or orchestrator.log stale > 2.5 min
5. Stays silent when state is clean (no log noise).

The auto-healer means transient drift gets fixed without you having to coordinate. But the structural rules below stop the drift from happening in the first place.

## Cross-session rules (read once, then follow)

### Producer / consumer
- **Never start a second producer.** If `tools/event_bus.sh` is already running (check `data/.event_bus.lock` PID is alive), do nothing. The auto-launch (Startup folder) handles it on logon.
- **One tail per session.** If you restart your Monitor, kill the old tail first.
- **Use the right session log.** Sessions: `exp_dev`, `research`, `testbed`, `skunkworks`, `orchestrator`. The producer's routing rules live in `tools/event_bus.sh`. If your session is missing an event class, edit the routing rules — don't write your own scanner.

### Heavy compute
- **Queue through the runner.** `queue_add.py` → cpu_runner_local → BELOWNORMAL + OMP/MKL/OPENBLAS=10. This is the default.
- **If you must spawn directly** (one-off scripts not designed as queue jobs): wrap with `start /BELOWNORMAL` AND set the thread env vars (`OMP_NUM_THREADS=10` etc.) before launch. If you forget, the health check will downgrade priority — but thread count is set at spawn time, so set it yourself.
- **One heavy job at a time outside the runner.** No parallel CPU burners.

### Notes (the biggest leak right now)

**Write fewer notes. Make each one denser.**

- **Don't write status pings.** "I'm still here", "Thinking about X", "Standing by" — don't. Sessions can derive status from the event log.
- **Don't write per-step routing notes during a burst.** If you're producing 10+ routing notes in a few minutes (Research, this means you), batch into ONE synthesis note at the end of the burst.
- **Use `_to_all_*` sparingly.** It's a broadcast — every consumer's tail fires on every broadcast. Reserve for protocol changes, USER-LOCKED rules, infrastructure migrations. Don't broadcast verdict batches or routine work.
- **Long descriptive filenames are fine** (they show what the note is at a glance), but you don't need to encode every detail in the filename — the body is for that.

### Notes hygiene
- Quarterly: archive notes older than 30 days into `notes/archived/YYYY-MM/`. Reduces producer scan cost. Currently 3323 total — not urgent yet, but trajectory matters.
- When the health check alerts notes > 4000, anyone can do the archival.

## Cross-references

- `CLAUDE.md` Section "Monitoring & cross-session event coordination" — the canonical rule (last updated yesterday).
- `orchestrator_to_all_HEAVY_WORK_THROUGH_RUNNER_OR_BELOWNORMAL_PRIORITY_DISCIPLINE_2026-06-13.md` — runner discipline (earlier today).
- `tools/event_bus.sh` — the producer; edit routing rules here.
- `tools/orchestrator/hd_health_check.ps1` — the auto-healer.
- Scheduled task `\hd_health_check` (15-min interval).

---

END. No reply expected. Read once, follow, move on.
