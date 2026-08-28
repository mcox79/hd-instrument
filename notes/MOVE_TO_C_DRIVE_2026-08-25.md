# hd-instrument moved D:\AI -> C:\AI  (2026-08-25)

The project was moved off the USB stick (D:) onto the internal NVMe (C:). This note is the
record of what happened and how to run from the new location.

## New layout (mirrors the old one)
- Repo:    `C:\AI\hd-instrument`
- Config:  `C:\AI\.claude`  (hooks + permissions, re-pointed to C:)
- venv:    `C:\AI\hd-instrument\.venv`  (REBUILT at C:, not copied — exact prior versions)
- Working dir for sessions: `C:\AI`  (same relationship as `D:\AI` before)

## How to get back up and running
Open EACH of your three working sessions with the folder set to **`C:\AI`**:
  - this strategy / architect session
  - "solve hd-instrument problem" (solver)
  - "research"
The SessionStart hook (now C:-pointed) auto-injects STATUS.md as before. Do your work in the
C: sessions from now on — not the old D: ones.

Optional sanity check in a terminal at `C:\AI\hd-instrument`:
```
.venv\Scripts\python.exe -c "import hdlab.substrate; print('OK')"
.venv\Scripts\python.exe tools\board.py self-test
```

## What was verified at C: (2026-08-25)
- Copy: 255,631 files match source exactly (byte diff <5 MB = post-copy hook drift on D:, not data).
- venv: `import hdlab.substrate` OK; `board.py self-test` PASS; `verification/test_meaning_fusion.py` PASS.
- Scheduled jobs: all 15 `hd_*` tasks re-pointed D:->C:; a triggered run executed from the C: venv.

## Scheduled jobs — what is ON vs OFF now
ENABLED (necessary): hd_director_kb_continuous_ingest, hd_durability_cron, hd_cpu_runner_local,
  hd_substrate_capability_registry_scan, hd_substrate_capabilities_aggregate, hd_capability_registry_audit.
DISABLED (dead orchestrator/old-fleet era, left off on purpose): hd_session_watchdog (RETIRED),
  hd_heartbeat_watchdog, hd_health_check, hd_landing_notifier, hd_metrics_sync, hd_orchestrator_watchdog,
  hd_orch_daily_audit, hd_orch_daily_research_drill, hd_orch_scope_expansion.
Note: the hourly ARCHITECT cron (session-only) was deleted for the move; recreate it if you want the loop.
Note: hd_durability_cron's last PRE-move run returned exit 5 -- pre-existing, worth a separate look.

## The old D: copy
UNTOUCHED and still fully works. Nothing was deleted. When you have worked on C: and are satisfied,
deleting `D:\AI\hd-instrument` (and the other moved folders) is a separate, deliberate step -- your call.
Six legacy daemons + all writers were stopped/disabled on D: before the copy; the two `.claude` settings
on D: still carry D: paths (that's why the D: copy still works if you ever open it).

## NOT moved (left on D: on purpose -- separate projects)
`estate-planner`, `nimbalyst-local`, `privacy-scan`.
