# Per-session launcher pattern for Phase 1 hardening hooks

**Status:** ACTIVATED at project-level `.claude/settings.json`. Currently-running Claude sessions won't pick this up until restart. New sessions are **fail-safe by default** (no `CLAUDE_SESSION_NAME` env var -> hook is a no-op = doesn't change anything).

## To activate hardening for a specific session

Each Claude Code session window must be launched with `CLAUDE_SESSION_NAME=<session>` env var set. Per-platform launch:

### Windows PowerShell (start the testbed session window)
```powershell
$env:CLAUDE_SESSION_NAME = 'testbed'
claude
```

### Windows CMD
```cmd
set CLAUDE_SESSION_NAME=testbed
claude
```

### Git Bash / Linux / macOS
```bash
CLAUDE_SESSION_NAME=testbed claude
```

Same pattern for each session (substitute name): `testbed`, `research`, `exp_dev`, `orchestrator`, `skunkworks`.

## What happens when the env var is set

1. **Stop hook** fires when Claude wants to stop the turn:
   - GUARD 1 (load-bearing): if `stop_hook_active=true` -> exit 0 (loop prevention)
   - GUARD 2: continuation counter < HARD_CAP (default 10)
   - GUARD 3: only blocks if unread inbox notes are newer than `data/last_processed_<session>.timestamp`
   - If all 3 guards align with "block" -> session continues with `{"decision":"block","reason":"..."}`
   - Otherwise -> normal stop
2. **StopFailure hook** fires when an API error caused stop:
   - Retryable errors (overloaded 529 / rate-limit 429) get backoff+jitter+retry up to MAX_RETRIES (default 5)
   - Non-retryable errors -> normal stop
   - Cause logged to `data/api_failures/<session>.jsonl`

## Per-session integration (TBD; needs each session's workflow update)

For the Stop hook to be useful long-term, each session needs to:

1. **Update `data/last_processed_<session>.timestamp`** at the end of each successful inbox-processing turn (so the hook stops blocking on notes already handled).
2. **Reset `data/hook_state/stop_continuations_<session>`** on real-USER-input (so the cap doesn't permanently lock).

These are session-side workflow integrations -- not part of the hook itself. Without them, the hook still works but:
- The hook blocks repeatedly on the same notes until cap fires (then truly stops; counter resets manually).
- The cap-counter only resets when manually deleted.

In practice the safety guards (loop prevention + cap) make this safe but suboptimal until per-session integration ships.

## Removing / disabling

To disable for a specific session: launch without the env var (or unset it):
```powershell
Remove-Item Env:CLAUDE_SESSION_NAME
claude
```

To disable globally for this project: delete or rename `.claude/settings.json` (the hooks become unregistered).

To remove permanently:
```
rm d:/AI/hd-instrument/.claude/settings.json
rm -rf d:/AI/hd-instrument/data/hooks/staging
```

## Coexistence verification (post-install Orchestrator runtime-owner checklist)

After registering, verify per the Orchestrator runtime-owner spec:

1. **v5 monitors still fire** -- `ls notes` and observe events flowing
2. **event_bus.sh singleton holds** -- `ls -la data/.event_bus.lock` (only one)
3. **No double-30-min task** -- only `hd_blocker_ping` running, no duplicate
4. **Stop hook respects stop_hook_active + cap** -- the dry-run-tests prove this (16/16 PASS), but re-confirm in a live session by:
   - Send a fake "unread note" (touch `notes/test_to_<session>_<date>.md`) and observe the hook fires once and then respects cap
   - Inspect `data/hook_state/stop_continuations_<session>` to confirm the counter increments and caps
5. **hd_metrics_sync uninterrupted** -- watch `data/.metrics_sync/sync.log` continues normal cadence

## Files

- `data/hooks/staging/stop_hook.py` -- Phase 1.1 (3-guard fail-safe; env-var gated)
- `data/hooks/staging/stop_failure_hook.py` -- Phase 1.2 (backoff + jitter + cap)
- `data/hooks/staging/dry_run_tests.py` -- 16/16 PASS
- `data/hooks/staging/COEXISTENCE_DESIGN.md` -- full design + Skunkworks invariant
- `data/hooks/staging/PER_SESSION_LAUNCHER_PATTERN.md` -- this file
- `.claude/settings.json` -- project-level hook registration (commits to repo)
