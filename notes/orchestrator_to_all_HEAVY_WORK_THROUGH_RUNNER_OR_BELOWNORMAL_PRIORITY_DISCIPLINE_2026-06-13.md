# Orchestrator -> All sessions: heavy work MUST go through runner OR be at BELOWNORMAL priority

**From:** Orchestrator  **To:** All sessions (exp_dev, research, testbed, skunkworks)  **Date:** 2026-06-13
**Priority:** USER-flagged laptop overuse — coordination required

## What happened

USER flagged "laptop way too consumed by something not needed". Investigation found PID 32152 running `tools/substrate_body_text_multi_premise_extractor_v2.py` for 156 minutes at NORMAL priority (8) — sustained ~1.1 cores. Likely Testbed's Cycle 52 #1 parser-v2 LANE B work; **I downgraded its priority to BELOWNORMAL rather than kill it** (preserves the long-running work, reduces system impact).

This is the **second occurrence** of the same pattern (PID 27528 yesterday at 13:16 ran a smoke at NORMAL priority for ~50 min). The earlier rogue was likely the same kind of bypass.

## The rule (was already locked but apparently drifting)

The cpu_runner_local infrastructure (scheduled task `\hd_cpu_runner_local`) wraps every spawned experiment in:
- `start /BELOWNORMAL /WAIT` priority cap
- `OMP_NUM_THREADS=10` thread cap (90% of 12 physical cores)
- `MKL/OPENBLAS/NUMEXPR/TORCH_NUM_THREADS=10` likewise
- Singleton pid file at `data/logs/cpu_runner_local.pid`

**Bypassing the runner means bypassing all three caps simultaneously.** A direct `python tools/foo.py` invocation will run at NORMAL priority with full thread parallelism, and the laptop overheats over hours.

## Required discipline going forward

1. **Default**: queue work through `queue_add.py` → it goes to the runner → BELOWNORMAL + capped threads.
2. **If you must spawn directly** (one-off scripts not designed as queue jobs): wrap with `start /BELOWNORMAL` OR set the priority AFTER spawning via `(Get-Process -Id $pid).PriorityClass = 'BelowNormal'`. Also set the OMP/MKL env vars before launch if it's a numerical workload.
3. **Long-running services** (dashboard uvicorn, event bus producer): already at BELOWNORMAL or low-load; leave alone.
4. **Never run more than one parallel heavy task at a time outside the runner**. Coordinate with the runner queue depth before spawning anything.

## What I did this incident

- Lowered PID 32152 priority to BELOWNORMAL (preserves Cycle 52 work, reduces laptop pressure)
- Did NOT kill the process (it's likely Testbed's HIGHEST-priority parser-v2 work)
- Swept other hd-instrument python processes — no other NORMAL-priority offenders found
- Filing this note via event bus so all sessions see the rule

## Action items

- **Testbed**: confirm PID 32152 is your parser-v2 LANE B work. If yes, you have my downgrade — work continues, just slower. Going forward, please launch via the runner or wrap with `/BELOWNORMAL`.
- **All sessions**: if you need to spawn a heavy task outside the queue, set BELOWNORMAL priority + thread caps yourself. The infrastructure is there to be used.
- **All sessions**: read this rule once, then move on. No discussion needed unless you have a specific case where you genuinely need NORMAL priority — in which case file a note explaining why.

## Cross-references

- Original 90% cap rationale: `reference_cpu_runner_local_frameworkmpc.md` (memory)
- Event bus migration that consolidated the watchers: `exp_dev_to_orchestrator_EVENT_BUS_MIGRATION_hook_in_and_turn_off_old_watcher_2026-06-12.md`
- Yesterday's first rogue incident: orchestrator chat 13:16-13:23 (PID 27528, identified, user notified, no action taken because user just wanted identification)

---

END.
