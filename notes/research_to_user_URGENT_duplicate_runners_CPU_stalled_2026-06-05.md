# Research -> User (URGENT on return): Duplicate runners; CPU lane stalled ~105 min during your absence

**From:** Research session
**To:** User (top priority on return)
**Inform:** Testbed (runner-env lane; possible action) + Orchestrator + Exp-Dev
**Date:** 2026-06-05 ~19:00
**Subject:** Exp-Dev escalated 4 times to Orchestrator with no action. Duplicate AppData system-Python runners are deadlocking the CPU lane. Phase 4a CPU work hasn't progressed during your 5-hour absence. Manual PID kill required.

---

## What you need to know (high-priority on return)

CPU lane has been stalled ~105 minutes (from ~16:55 to ~18:44+). **The 5-hour productivity window you expected for Phase 4a CPU work has been largely lost.** GPU lane stayed healthy (Exp-Dev kept it topped up).

Root cause: 4 runner_v2_prod processes are running on marsh@home runner. Should be 2:
- CORRECT .venv pair: PIDs 180112 + 145588
- STALE AppData system-Python pair (started 8:11 AM): **PIDs 44396 + 61232**
- Plus orphan exp subprocess **PID 128036** (working_memory; cpu_s ~3900; pegging core)
- Plus stuck current run **PID 24900** (if it's the deadlocked job)

The AppData runners use system Python (NOT the project venv) so they lack gmpy2/sklearn/faiss; their cell copies likely FAIL on import, polluting verdicts.

## Action needed (manual; PID kills require your lane)

From PowerShell on marsh@home:

```powershell
# Verify which PIDs are actually present
tasklist /v | findstr runner_v2_prod
tasklist /fi "PID eq 44396"
tasklist /fi "PID eq 61232"
tasklist /fi "PID eq 128036"

# Kill stale AppData system-Python runners + orphan
taskkill /F /PID 44396
taskkill /F /PID 61232
taskkill /F /PID 128036
# If 24900 is the stuck current run:
taskkill /F /PID 24900

# Verify only .venv runners remain
tasklist /v | findstr runner_v2_prod
# Should show only PID 180112 + 145588 (.venv pair)
```

After cleanup, CPU lane drains the 16 pending cells (Exp-Dev confirmed working_memory_loop is now shrunk to 2-3 min so re-pull is cheap).

## Why automation didn't catch this

Per [[feedback-runner-singleton-check]] (2026-05-27): "PID-file lock + duplicate_runner_detected watchdog landed". Someone bypassed the PID-file lock to start the AppData runners. The watchdog should have detected this; investigate why it didn't fire.

Both Exp-Dev and Research are correctly blocked from killing runner processes (role separation). Orchestrator did not respond to 4 escalations during your absence. **Process gap: when Orchestrator is silent, runner PID kills have no fallback.**

## Exp-Dev's side work during the stall

Exp-Dev correctly:
- Detected the issue at 17:50
- Escalated 4 times to Orchestrator
- Pre-shrunk the working_memory_loop_v1 spec so future pulls are cheap
- Kept GPU lane healthy (topped up queue)
- Maintained CPU queue depth (16 cells pending)

## Phase 4a status (post-cleanup)

Once you action the PID kills, Phase 4a CPU work proceeds:
- PHASE4A-4 pre-registered rescues template
- PHASE4A-3 two-tier write/read path
- PHASE4A-5 substrate eval harness (~5-7 days)
- Plus HP-5 medical Q&A scaffold

PHASE4A-1 MiniLM is already loadable (Testbed installed sentence-transformers at 16:53).

## Suggestion for prevention

Per the gap exposed: when Orchestrator silent + Research/Exp-Dev blocked from PIDs, who actions?

Options:
- Testbed runner-env lane could be extended to "runner PID lifecycle" (currently they do installs + cloud only)
- Watchdog auto-action: detect AppData-Python runner -> alert + kill
- Pre-startup check: every runner start checks if matching PID already present; refuses to dual-start

Worth raising in next process review.

---

**END.**

**User:** Top priority on return. Three taskkill commands needed (PIDs 44396, 61232, 128036, and possibly 24900). CPU lane drains automatically after. ~105 min lost during your absence; Phase 4a CPU work stalled but GPU lane healthy.

**Testbed:** If you have authority to kill runner PIDs, please action ASAP. Otherwise standing for user.

**Orchestrator:** 4 unactioned escalations. Process gap exposed (runner PID lifecycle when Orchestrator silent).
