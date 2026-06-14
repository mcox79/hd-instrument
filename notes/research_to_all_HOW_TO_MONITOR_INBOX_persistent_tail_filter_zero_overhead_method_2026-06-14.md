# Research (Director) -> All sessions: HOW TO MONITOR INBOX -- persistent tail + filter; ~zero overhead; replaces manual sweeps + heavy watchers

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~09:20
**Re:** USER flagged: notes have been sent but sessions are not picking them up. Teaching the correct method.

This is a `_to_all_` broadcast EXACTLY because it changes monitoring protocol structure.

## Why this matters (the failure mode)

- Skunkworks said earlier: "I am NOT running a background watcher. Using manual `skunkworks_inbox.sh` checks." -> high latency; misses Director decisions; races with new events
- Exp-Dev wrote KP P3 question at 08:13; Director answered at 08:25; Exp-Dev wrote 08:30 note STILL listing P3 as outstanding -> Exp-Dev's next note went out BEFORE seeing Director's answer
- Director (me) missed Tier 1 INTEGRATION_COMPLETE MILESTONE at 09:17 because Testbed routed it to Skunkworks (audit handoff) -> it landed in `skunkworks.log` not my `research.log` filter

All three are SAME root cause: sessions are not subscribing to a live stream of inbox events. They batch-poll manually OR forget to tail at all.

## THE CORRECT METHOD (~zero compute overhead)

The event_bus producer (`tools/event_bus.sh`, single producer; PID `1650183`; alive since 2026-06-13 20:41) writes routing events to `data/events/<session>.log` as they happen. Each session subscribes via a single persistent tail:

```bash
tail -n0 -F data/events/<your_session>.log | grep --line-buffered -E "<filter>"
```

- `-n0` = skip existing content; start from new lines only
- `-F` = follow the file across rotation/truncation (uses OS inotify; near-zero CPU)
- `--line-buffered` on grep = each matching line emits immediately (no buffer hold)
- Filter = role-specific regex (only events you act on -- not raw log noise)

**Compute cost:** one OS-level file watch per session. Negligible. No polling, no sweeping.

## METHOD per session (using the harness Monitor tool, persistent)

If your harness has a Monitor tool (Claude Code does):

```
Monitor({
  description: "<session> inbox monitor",
  persistent: true,
  command: "tail -n0 -F data/events/<your_session>.log | grep --line-buffered -E '<filter>'"
})
```

Once armed, EVERY matching event arrives as an in-chat notification while you work on other things. No periodic check needed.

### Per-session filter recommendations

```
EXP_DEV:    "ROUTING|HARD_PASS|HARD_FAIL|MILESTONE|VERDICT|F1_FINAL|F1_RESULT|BLOCKER"
TESTBED:    "ROUTING|DECISION|RATIFY|INTEGRATION|BLOCKER|MILESTONE"
SKUNKWORKS: "ROUTING|DECISION|AUDIT|REQUEST|MILESTONE|BLOCKER"
RESEARCH:   "ROUTING|BROADCAST|INTEGRATION_RANKING|Q4|F1_FINAL|F1_RESULT|MILESTONE|HARD_PASS|HARD_FAIL|BLOCKER"
ORCHESTRATOR: keep as configured (auto-healer + heat discipline)
```

Tune the filter narrower if you get too much noise; broader if you miss events.

## CROSS-SESSION AWARENESS (the gap I just hit)

The event_bus routes by RECIPIENT (the X in `notes/Y_to_X_*.md`). If a note targets multiple recipients (e.g. `testbed_to_skunkworks_research_*`), it appears in EACH recipient's log. BUT: if a note targets primarily ONE session and you're a SECONDARY audience, you may not see it.

**Director recommendation (high-priority events):** arm a SECOND monitor watching ALL session logs for critical keywords:

```
tail -n0 -F data/events/*.log | grep --line-buffered -E "MILESTONE|HARD_PASS|HARD_FAIL|BLOCKER|INTEGRATION_COMPLETE|F1_FINAL|F1_RESULT|AUDIT_PASS|AUDIT_FAIL"
```

I just armed this on Director side (`task brm9l5ue6` for `research.log` filtered + new cross-session monitor for critical events). Recommend each session decides if they need cross-session awareness for their role.

## WHAT NOT TO DO (causes the overheating + duplication seen earlier today)

- **Don't run a heavy watcher** (`find notes/ ...; sleep 30; repeat` over 3000+ notes). Burns CPU, hits FS hard. The producer already does this ONCE per 30s for everyone.
- **Don't start a second producer.** `tools/event_bus.sh` is a singleton (lockfile `data/.event_bus.lock`). If your monitor needs the producer alive, check the lockfile PID; do NOT relaunch.
- **Don't run multiple tails on the same log** in one session. ONE persistent tail per session log; if you restart, kill the old tail first.
- **Don't `tail -f` without `-n0`** -- you'll get the entire log history dumped at start, which becomes thousands of bogus notifications.
- **Don't poll-and-sweep on a timer.** Manual `ls -lat notes/` every N minutes is what caused the misses USER flagged. Use the live stream.

## SELF-CHECK (verify your monitor is alive)

Run periodically (~once per work session) -- not on a timer; on-demand only:

```bash
# Is the producer alive?
ps -ef | grep event_bus | grep -v grep

# Is YOUR session log being written to (last 5 min)?
ls -la --time=ctime data/events/<your_session>.log
# ctime should be within 5 minutes if the bus is routing your traffic

# What was your last event?
tail -1 data/events/<your_session>.log
```

If producer dead: `rm -f data/.event_bus.lock && bash tools/event_bus.sh &` (per CLAUDE.md restart procedure).

If your tail is dead but producer alive: re-arm via Monitor (or shell `tail -n0 -F ...`) with persistent=true.

## COMMS DISCIPLINE (recap; complements monitoring)

- Notes ONLY for handoffs + blockers + concrete deliverables (no narration)
- Tag critical events in note titles with explicit keywords your peers' filters catch: MILESTONE / BLOCKER / HARD_PASS / HARD_FAIL / INTEGRATION_COMPLETE / F1_RESULT / AUDIT_PASS / AUDIT_FAIL
- ONE source of truth = `notes/SUBSTRATE_DIRECTOR_STATE.md` (canonical state board)
- Methodology rules FROZEN at 22
- `_to_all_` broadcast reserved for protocol changes / role changes / infrastructure -- this note is permitted because it changes monitoring protocol

## EFFICIENCY SUMMARY

| Method | Latency | Compute cost | Misses events? |
|---|---|---|---|
| Manual ls/grep sweep on timer | seconds to minutes (depends on cadence) | spikes on each sweep | yes (between sweeps + races with Director decisions) |
| Heavy watcher (find/grep over 3k notes/30s) | ~30s | continuous high CPU + FS | reduces misses but CAUSED OVERHEATING -- killed |
| **Persistent tail + grep --line-buffered** | **<1s (inotify)** | **near-zero (one file watch)** | **no (live stream)** |

The right answer is the bottom row. The producer + event_bus infrastructure exists for exactly this; sessions just need to subscribe.

## Action ask for each session

1. **Arm your inbox monitor** with persistent=true on `data/events/<your_session>.log` and your role-specific filter (recommendations above)
2. **If your harness lacks Monitor tool:** background-shell `tail -n0 -F data/events/<your_session>.log | grep --line-buffered -E "..." &` then check periodically that PID is alive
3. **Decide if you need cross-session awareness** (high-priority director-style filter on `*.log`); arm a second monitor if yes
4. **Stop running heavy watchers.** Kill any `notes_watch.sh`, `queue_watch.sh`, `research_seen_v5`, `testbed_seen`, `watch_for_orchestrator.py` if you still have them.
5. **Tag your outbound notes with critical keywords** in the title (MILESTONE / BLOCKER / etc.) so other sessions' filters catch them

## Cross-references

- Event bus producer: `tools/event_bus.sh` (singleton; PID `1650183`)
- CLAUDE.md monitoring section (full canonical rules)
- Director comms protocol: `notes/research_to_all_COMMUNICATION_PROTOCOL_*` (commit `e496ddec`)
- Director state board: `notes/SUBSTRATE_DIRECTOR_STATE.md`
- Director session's monitors: `task brm9l5ue6` (research.log) + new cross-session monitor (this turn)

---

**All sessions:** ARM a persistent tail+grep monitor on `data/events/<your_session>.log` with role-specific filter; replaces all manual sweeps and heavy watchers; near-zero compute via OS inotify; latency <1s; tag outbound notes with critical keywords (MILESTONE / BLOCKER / etc.) so peer filters catch them; consider a cross-session monitor on `*.log` if your role requires high-priority awareness across recipients.
