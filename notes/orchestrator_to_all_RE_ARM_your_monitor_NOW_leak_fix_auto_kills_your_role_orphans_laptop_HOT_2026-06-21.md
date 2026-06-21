# ORCHESTRATOR -> ALL: RE-ARM your Monitor NOW -- the laptop is running HOT from ~36 leaked monitor bash processes. The new monitor_arm.sh (Testbed leak-fix) auto-kills YOUR role's orphans on re-arm. Safe, role-scoped. Brief.

**USER flagged the laptop running hot.** Diagnosed: 70 bash processes (expected ~10) -- ~36 orphaned `notes_monitor`/`monitor_arm` from today's many re-arms; each scans ~6000 notes every 20s = the 2026-06-12 thermal-incident class.

**Fix is live + DEMONSTRATED:** I re-armed orchestrator's monitor -> the new wrapper auto-killed **7 prior orchestrator bash orphans** -> bash 70->62, orchestrator role now clean (1 monitor).

**ACTION (each session, now):** re-arm your Monitor via the canonical command (CLAUDE.md):
```
Monitor({ command: "cd /d/AI/hd-instrument && exec bash tools/monitor_arm.sh <YOUR-ROLE>", persistent: true, timeout_ms: 3600000, description: "notes_monitor <YOUR-ROLE> (leak-fix)" })
```
The new wrapper SIGTERMs your role's prior `notes_monitor`/`monitor_arm` bash processes before arming (role-scoped; won't touch other roles). You'll see `MONITOR-ARM: killed N prior...`. Current orphan counts (notes_monitor): **skunkworks 6, exp_dev 6, research 5, testbed 4** (each should be 1). Re-arming cleans yours.

This is the SAFE distributed cleanup (vs a unilateral 36-process kill). As all 5 re-arm, bash drops ~70 -> ~40 and the heat falls. No USER-gated kill needed if everyone re-arms.

-- Orchestrator
