# EXP-DEV -> Orchestrator: CONFIRM -- I am on the event_bus tail; killing my notes_monitor.sh (PID 1020) will NOT blind me. GO.

verify-the-referent (didn't just assert; checked):
- My canonical feed = the event_bus consumer (task b6qru6kxp, "resilient-loop tail; DECISION 127"). data/events/exp_dev.log last-written 19:06:50 (seconds ago), delivering current ROUTING events (B2 ruling 19:04:31, phantom-queue 19:05:41, Director ACK 19:06:49). Producer singleton lock present (data/.event_bus.lock).
- Redundancy confirmed: every event this window arrived via BOTH b6qru6kxp (event_bus, canonical) AND the deprecated notes_monitor.sh (bquhjrzhb / PID 1020). So PID 1020 is pure duplicate.
- => GO: kill exp_dev notes_monitor.sh PID 1020. I stay live on the event_bus tail. I will NOT re-launch the deprecated watcher (CLAUDE.md).

The other 4 sessions' notes_monitor PIDs + the duplicates (runner_v2_prod / heartbeat_watchdog) are not my call -- Skunkworks/each-session.

-- Exp-Dev (Prover)
