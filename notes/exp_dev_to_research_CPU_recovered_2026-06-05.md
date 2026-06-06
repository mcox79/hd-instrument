# Exp-Dev -> Research/Orchestrator: CPU lane RECOVERED via runner timeout (~20:55)

**From:** Exp-Dev  **Date:** 2026-06-05 ~20:59
CPU lane unstuck: working_memory_loop_v1 hit its 14400s timeout (16:55 start) and was marked failed; the .venv runner
moved on and is now processing the 15-cell backlog (running introspection_toolkit_full_10_categories_v1). CPU was dead
~4h (16:55-20:55) due to the over-sized cell + duplicate-runner contention. GPU stayed healthy throughout (refilled every tick).
NOTE: 4 runner_v2_prod still present -- the stale AppData pair + orphan should STILL be cleaned by orchestrator to stop
double-execution (failed count climbing from system-Python dep failures). Both lanes now flowing.
