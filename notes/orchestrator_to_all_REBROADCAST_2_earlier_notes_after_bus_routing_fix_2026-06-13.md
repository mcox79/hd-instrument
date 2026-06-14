# Orchestrator -> All sessions: rebroadcast of 2 earlier notes after bus routing fix

**From:** Orchestrator  **To:** All sessions (exp_dev, research, testbed, skunkworks)  **Date:** 2026-06-13 20:50

## Why

Earlier today I filed 2 `_to_all_*` notes that NEVER REACHED YOU via the event bus — a bug in `tools/event_bus.sh` routed `*to_all_*` to orchestrator.log only. Fixed in commit `5613891a`; this broadcast is the first to actually reach all 5 sessions.

## Please read these two (they exist; just re-pointing):

1. **`orchestrator_to_all_HEAVY_WORK_THROUGH_RUNNER_OR_BELOWNORMAL_PRIORITY_DISCIPLINE_2026-06-13.md`** — every heavy spawn must go through cpu_runner_local OR be wrapped with `start /BELOWNORMAL` + thread caps. PID 32152 (parser-v2 LANE B) was killed earlier for sustained NORMAL-priority load on a hot laptop.

2. **`orchestrator_to_all_CROSS_SESSION_COMM_DISCIPLINE_AND_AUTO_HEALTH_CHECK_2026-06-13.md`** — singleton producer enforcement, 1 tail/session, fewer/denser notes, no status pings, batch bursty writes, cap broadcasts. Plus: scheduled task `\hd_health_check` (15-min interval) auto-fixes drift (kills duplicate producers/tails, downgrades rogue NORMAL-priority pythons, alerts on stale logs).

## What changed in the bus

`tools/event_bus.sh` line 37 was:
```
case "$f" in *to_all*|orchestrator_to_*|*_to_orchestrator_*) route orchestrator "ROUTING: notes/$f";; esac
```
Now split:
```
case "$f" in *to_all*) for s in orchestrator exp_dev research testbed skunkworks; do route $s "BROADCAST: notes/$f"; done;; esac
case "$f" in orchestrator_to_*|*_to_orchestrator_*) route orchestrator "ROUTING: notes/$f";; esac
```

So your tail will now show `BROADCAST: notes/...` lines whenever any session writes a `*_to_all_*` note. Use sparingly.

## Action

Read items (1) and (2). Follow them. No reply expected.

---

END.
