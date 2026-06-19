# Exp-Dev -> Orchestrator: ESCALATION -- duplicate runners STILL present; CPU lane stalled ~1h

**From:** Exp-Dev  **To:** Orchestrator  **Inform:** User  **Date:** 2026-06-05 ~18:03  **Re:** 17:50 duplicate-runner flag (not yet actioned)

## STILL UNRESOLVED (re-checked 18:03):
- runner_v2_prod count = 4 (the stale AppData system-Python pair PIDs 44396 + 61232 still alive alongside the .venv pair).
- CPU lane STALLED ~1h: substrate_working_memory_loop_v1 (old oversized instance, started 16:55) still "running";
  ZERO CPU completions in ~1h; 16 cells pending behind it. The orphan AppData working_memory (PID 128036, cpu_s>3900)
  appears to still be pegging a core.

## Request (URGENT -- user is out and wants both lanes productive):
1. Kill stale AppData runner_v2_prod PIDs 44396 + 61232 (system-Python set).
2. Kill orphan exp PID 128036 (working_memory, ~1h, pegging core) and PID 24900 if it is the stuck current run.
3. Re-assert PID-file singleton so only the .venv CPU+GPU runners remain.
After cleanup the CPU lane will drain the 16 pending (working_memory is now shrunk to ~2-3min so a re-pull is cheap).
GPU lane is healthy (draining + I topped it up). I cannot kill PIDs (blocked -- your lane).
**END.**

## UPDATE 18:15 (3rd escalation): CPU STILL frozen -- completed=541 unchanged across 3 ticks (~75min), working_memory_loop_v1 still running, runners=4. GPU also went idle once (I refilled). The stale AppData runner pair + orphan MUST be killed for CPU to drain. URGENT.

## UPDATE 18:44 (4th escalation): CPU STILL frozen ~105min (completed=541 since 16:55), working_memory_loop_v1 still "running", runners=4. This is now likely a genuine DEADLOCK/hang (job should have finished by ~106min even 2x-contended). The duplicate AppData runner pair + orphan PID 128036 need killing -- I cannot (blocked). 16 CPU cells starved the entire user-absence window. Please action.

## UPDATE 19:13 (5th escalation): CPU STILL frozen ~135min (completed=541 since 16:55). working_memory_loop_v1 still "running", runners=4 (PIDs 44396+61232 AppData stale + orphan 128036). CPU lane dead the ENTIRE user-absence window. GPU healthy (I refill every tick). Needs orchestrator PID kill -- I am blocked.

## UPDATE 19:42 (6th escalation): CPU frozen ~165min (completed=541). 6 escalations, no orchestrator action observed -- the orchestrator session may be inactive. NOTE: working_memory_loop_v1 has a 14400s timeout (started 16:55) so the .venv runner should AUTO-RECOVER the CPU lane ~20:55 if not killed sooner. GPU healthy throughout (refilled each tick). Stale AppData runners 44396+61232 + orphan 128036 should still be killed.

## UPDATE 20:11 (7th escalation): CPU frozen ~195min. No orchestrator action through 7 flags. Auto-recovery via working_memory 14400s timeout expected ~20:55 (~45min). GPU healthy throughout.

## UPDATE 20:40 (8th escalation): CPU frozen ~225min. Runner timeout auto-recovery imminent (~20:55). If runners NOT cleaned, CPU will recover but the stale AppData pair + orphan will keep double-executing -> still needs your cleanup.
