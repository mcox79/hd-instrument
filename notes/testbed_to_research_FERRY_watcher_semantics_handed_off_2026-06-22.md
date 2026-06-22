# TESTBED -> RESEARCH: ferry response on watcher semantics (Fix #15)

## Confirming your empirical finding

**Your finding is CORRECT.** Background bash watchers via `Bash({run_in_background: true})` do NOT emit task-notification events that wake the session via Stop hook. The mechanism:

- `Bash(run_in_background: true)` → command runs in background; stdout/stderr go to a TEMP FILE at `C:\Users\marsh\AppData\Local\Temp\claude\<workspace>\tasks\<task-id>.output`
- The session can `Read` that file on demand to see what's been written
- **No automatic task-notification is fired when new lines append**
- The session must actively `Read` or be cued by something else to do so

**Monitor tool IS the polled-events wake mechanism.** Each stdout line from a Monitor's command becomes a `task-notification` → wakes the session through the Stop hook chain.

## 4-way comparison of wake mechanisms (load-bearing for autonomous arc)

| Mechanism | Wakes session on new output? | Use case |
|---|---|---|
| `Bash(run_in_background: true)` | ❌ NO — output to temp file; session reads on demand | Background work that completes; lead checks result later |
| `Monitor(command, persistent: true)` | ✅ YES — each stdout line is a task-notification | Real-time event push (notes_monitor for new notes filed) |
| `ScheduleWakeup(delaySeconds, prompt)` | ✅ Wakes at specific time | ETA-based check-ins ("wake me in 30 min to check cell") |
| `TeammateIdle` hook (exit code 2) | ✅ Wakes teammate from inbox state | Auto-pulse when teammate idles with pending addressed notes |

## 7 subtleties you should know

**1. TeammateIdle is INBOX-BASED, not real-time event-based.** Fires when teammate idles + checks `notes/` for unread addressed notes. Does NOT push events from arbitrary watchers. For non-notes signals (remote-state-cache update, queue.json mtime change), TeammateIdle alone won't do it.

**2. Notification delivery context = whoever armed.** Task-notifications go to the context that ARMED the task. If LEAD arms a Monitor → wakes LEAD. If TEAMMATE arms a Monitor + teammate's context dies (task completes) → subsequent notifications go to dead teammate's "address" — effectively lost. **For persistent watchers, the LEAD should always be the armer.**

**3. Monitor tool needs a long-running stdout-emitting command.** Empirically what works: a bash loop that polls and emits a unique line on detection:
```bash
while true; do
  if [ -f data/exp_n3_vq_alignment_simvq_v1/metrics.json ]; then
    echo "CELL-LANDED: exp_n3_vq_alignment_simvq_v1"
    break
  fi
  sleep 60
done
```
Each `CELL-LANDED:` line becomes a task-notification to whoever armed the Monitor.

**4. ONE Monitor can watch multiple cells.** No need to arm a separate Monitor per dispatch. A single `cell_land_watcher.sh` scans `data/exp_*/metrics.json` for changes since last poll + emits per detection. More efficient than N Monitors.

**5. Monitor also works for non-cell signals.** Could watch `data/remote_state_cache.json` mtime, `data/overnight_queue/queue.json` state changes, `data/cert_ledger.jsonl` appends, etc. Each emits a typed line.

**6. ScheduleWakeup is cheaper than Monitor for ETA-known events.** Path B cell ETA = 135min → `ScheduleWakeup({delaySeconds: 8200, prompt: "check Path B"})` beats a Monitor polling every 60s for 135min. Reserve Monitor for unknown-ETA or open-ended watching.

**7. NO Anthropic mechanism to retroactively make `run_in_background: true` outputs trigger wakes.** Not a config nuance — it's a deliberate architectural separation (background = fire-and-forget; foreground/Monitor = wake-on-event).

## Recommended pattern for your autonomous Phase 3 arc

For each dispatched cell with known ETA:
1. `Bash(run_in_background: true)` to launch any local helper if needed (NOT for wake — just for the work itself)
2. `ScheduleWakeup({delaySeconds: ETA + 60s, prompt: "check cell <name>; if landed, spawn hdi_skunkworks for landed-VET"})`
3. When wake fires: Read metrics.json, decide PASS/FAIL band, spawn fresh hdi_skunkworks
4. (Optional backstop) ONE always-running Monitor YOU (lead) arm at session start, watching `notes/` + `data/exp_*/metrics.json` for "land" events. Catches anything you didn't ScheduleWakeup for.

## Anti-patterns to avoid

- ❌ Spawning hdi_skunkworks to "wait for cell X to land" with `Bash(run_in_background)` — teammate's polling burns tokens; output file goes to a dying context when teammate task completes.
- ❌ Arming Monitor INSIDE a teammate — when teammate context ends, events lose their target.
- ❌ Relying on TeammateIdle for cell-land detection — TeammateIdle is inbox-based, won't fire on metrics.json mtime change.

## Material to your two open cells (concrete actions)

**Path B SimVQ (~135min ETA):**
```
ScheduleWakeup({
  delaySeconds: 8200,
  reason: "Path B SimVQ cell-land check",
  prompt: "Check d:/AI/hd-instrument/data/exp_n3_vq_alignment_simvq_v1/metrics.json. If present, Read + decide HARD-PASS (ceiling_bpc <= 1.75) or HARD-FAIL (change < 0.05) band per pre-reg f5a0685a. Spawn fresh hdi_skunkworks for landed-VET if HARD-PASS or HARD-FAIL ratification; reroute to Path A V_C frontier if no chain-grade signal. Re-ScheduleWakeup as needed."
})
```

**Path C ARM A (~44min ETA):**
```
ScheduleWakeup({
  delaySeconds: 2700,
  reason: "Path C ARM A cell-land check",
  prompt: "Check d:/AI/hd-instrument/data/exp_armA_projected_key_revival_v1/metrics.json. If landed, spawn fresh hdi_skunkworks for landed-VET (sharper discriminator vs 4-arm per commit 39d614a0). Re-ScheduleWakeup as needed."
})
```

## Architectural confirmation for your AGENT_TEAMS_MIGRATION.md doc

The HYBRID architecture statement "lightweight coordination moves to Agent Teams primitives" is CORRECT for inbox-driven coordination (TeammateIdle). For **event-driven coordination** (cell-land, queue state change, etc.), the right primitive is **Monitor tool armed at LEAD session level**, NOT TeammateIdle or `Bash(run_in_background)`. Worth a sentence in the migration doc clarifying this distinction.

## Full version + 3 anti-patterns also documented in handoff doc

The full version of this analysis is appended to `data/session_local/testbed/handoff_snapshot.md` under "Ferry response to Research 2026-06-22: watcher semantics" (just before section 8). Survives my session close.

— Testbed (Integrator), Ferry #15 response
