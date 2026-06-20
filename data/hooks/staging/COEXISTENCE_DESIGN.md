# Phase 1 Hardening Coexistence Design

**Status:** STAGED (data/hooks/staging/); NOT YET REGISTERED.
**Author:** Testbed (per Director hardening proposal + Orchestrator runtime-owner spec + Skunkworks cert-integrity input).
**Date:** 2026-06-20.

## Purpose

Document how the staged Stop hook + StopFailure hook coexist with the existing runtime infra surface BEFORE Orchestrator approves register and surfaces to USER for harness-gated auth.

## Existing infra surface (Orchestrator-owned; this design must NOT conflict)

| Component | Cadence | Owner | Touch-point Risk |
|---|---|---|---|
| **v5 `notes_monitor.sh`** (5 procs, one per session) | 20s poll, set-diff | Orchestrator | Reads `notes/` directory. Stop hook ALSO reads `notes/` but via per-session `data/last_processed_<session>.timestamp` the monitor does NOT touch -> NO race. |
| **`event_bus.sh` singleton** (`data/.event_bus.lock`; Startup auto-start) | continuous | Orchestrator | Secondary routing. Watchdog must NOT kill/duplicate. (Watchdog not in Phase 1.) |
| **`hd_blocker_ping` scheduled task** | 30-min cadence, survives compaction | Orchestrator | Phase 2 watchdog folds heartbeat INTO this (reuse, don't duplicate). |
| **`hd_metrics_sync` scheduled task** | 20-min cadence (S4U logon now; popup-free) | Orchestrator | File-copy + git push; has pre-push Store-LOAD gate. Watchdog revive must NOT interrupt mid-sync (Store-write safety). |

## Skunkworks load-bearing cert-integrity invariant

**Single-writer Store-write discipline must be PRESERVED.**

- `save_atoms` is NOT cross-session concurrency-safe (two concurrent same-partition saves -> NULL seam -> whole Store unloadable; the documented corruption-incident pattern).
- Stop hook does NOT trigger Store-writes -- it only decides session-continuation. The session itself follows the existing coordinated-window discipline for any actual Store-write.
- Auto-continue does NOT race the NULL-seam hazard.
- Future watchdog-revive must NOT trigger or enable a concurrent Store-write (e.g., don't revive INTO a Store-write mid-operation; preserve coordinated-window norm).
- Orchestrator post-install verify-the-referent invariant: confirm a revive cannot race a single-writer window.

## Phase 1.1 Stop hook (`stop_hook.py`)

**Triggers:** Claude Code Stop event (turn ends; about to stop).

**3 load-bearing safety guards (CHECKED IN ORDER):**

1. **GUARD 1 (LOAD-BEARING): `stop_hook_active` flag.** If true (already in a Stop-hook-triggered continuation), exit 0 immediately. **This is THE protection against the documented ~50min loop bug that burned a session's quota.** Dry-run-PROVED (T1).
2. **GUARD 2: HARD_CAP continuation counter.** Per-session counter in `data/hook_state/stop_continuations_<session>`. Hard cap (default 10; env-override `HD_STOP_HOOK_HARD_CAP`). At cap -> exit 0. Counter reset on real-USER-input cycle (TBD per session integration). Dry-run-PROVED (T2, T5b).
3. **GUARD 3: Concrete signal gate.** Only blocks (continues session) if there is REAL pending work. Currently: unread inbox notes for this session newer than per-session `data/last_processed_<session>.timestamp`. Filter matches v5 notes_monitor.sh convention (session OR to_all OR _all_; exclude own-outgoing). Dry-run-PROVED (T3 no-signal-no-block + T4 signal-blocks).

**Coexistence:**
- Reads `notes/` (same as v5 monitor) but uses isolated per-session timestamp file (`data/last_processed_<session>.timestamp`) that the monitor does NOT touch. Pure-read; no race.
- Writes only to per-session counter file (`data/hook_state/stop_continuations_<session>`). Not in any other component's path.
- Does NOT trigger Store-writes. Cert-integrity invariant preserved.

**Session integration TBD (USER-pending design):**
- When session processes the unread inbox notes (its turn re-engages from the block), it should UPDATE `data/last_processed_<session>.timestamp` to mark them processed. (Otherwise the hook keeps blocking on the same notes until the cap fires.)
- Counter reset on real-USER-input (TBD: how to distinguish hook-triggered continuation from real-input).

## Phase 1.2 StopFailure hook (`stop_failure_hook.py`)

**Triggers:** Claude Code StopFailure event (API error caused stop).

**Logic:**
- Parse error type + HTTP status from input JSON.
- Determine retryable: `overloaded_error` (HTTP 529, base 30s), `rate_limit_error` (HTTP 429, base 60s). All other errors NON-retryable -> exit 0; counter reset.
- Read attempt counter from `data/api_failures/<session>.attempt`. At MAX_RETRIES (default 5) -> exit 0; counter reset.
- Compute backoff: `base * 2^attempt + random[0..15]` seconds.
- Log failure to `data/api_failures/<session>.jsonl` (one line per event; includes timestamp, error type, status, retryable flag, attempt count).
- Increment counter; emit retry decision JSON to stdout.

Worst-case: 5 attempts at base=30: 30 + 60 + 120 + 240 + 480 = ~15 min total before giving up.
Worst-case: 5 attempts at base=60 (rate_limit): 60 + 120 + 240 + 480 + 960 = ~31 min total.

**Coexistence:** Does NOT touch Store; only writes per-session state files.

## Dry-run-PROVED (16/16 PASS)

See `dry_run_tests.py` output. All 16 checks pass:

| # | Test | Result |
|---|---|---|
| T1 | stop_hook_active=true -> exit 0 + no decision (LOAD-BEARING) | PASS |
| T2 | continuation cap reached -> exit 0 | PASS |
| T3 | no concrete signal -> exit 0 + counter NOT incremented | PASS x2 |
| T4 | pending unread inbox -> decision=block + counter +1 | PASS x3 |
| T5a | cap-1 blocks + counter -> cap | PASS x2 |
| T5b | at cap exits 0 | PASS |
| F1 | non-retryable -> no retry | PASS |
| F2 | retryable -> retry + counter +1 | PASS x2 |
| F3 | retry-cap exhausted -> exit 0 + counter reset | PASS x2 |

## What's NOT yet built (Phase 2)

- Watchdog process (heartbeat folded into `hd_blocker_ping`; revive via tmux/Task Scheduler restart).
- Per-session Windows Task Scheduler restart-on-failure.

Per Director: Phase 2 becomes Testbed's next major Integrator-role build IF Phase 1 drops session-death rate substantially after a few days.

## Register path (USER-pending)

Per Orchestrator (runtime-owner): Registration is harness-gated and requires USER DIRECT auth.

1. **USER reviews this design doc + dry-run-test output.**
2. **USER + Orchestrator approve.**
3. **Orchestrator executes register** (scheduled-task / hook config write) per Windows / Claude Code settings. Testbed does NOT self-register.
4. **Orchestrator post-install verify-the-referent:**
   - 5 v5 monitors still fire (`ls notes` test)
   - `event_bus.sh` singleton holds (one lock)
   - No double-30-min scheduled task
   - Stop hook respects `stop_hook_active` + cap (dry-run-prove the loop-guard NOT assert)
   - `hd_metrics_sync` uninterrupted
5. **Per-session integration: timestamp-update + counter-reset on real-USER-input** (TBD; needs per-session workflow edit).

## USER-pending decisions

- (a) **Power-settings nod** (Phase 1.3; `powercfg /change standby-timeout-ac 0` + `hibernate-timeout-ac 0`). Local + reversible. Orchestrator can execute on USER nod.
- (b) **Register-auth** (Phase 1.1 + 1.2 hooks). Persistence-write; harness-gated. Triggered after USER review of this design + dry-run.
- (c) **Phase 3** (concurrency reduction / Batch API / separate workspaces / higher account tier). Cost decisions. Surface only if Phase 1+2 insufficient.

## Files in this staging dir

```
data/hooks/staging/
  stop_hook.py             Phase 1.1; load-bearing 3-guard implementation
  stop_failure_hook.py     Phase 1.2; backoff + jitter + retry-cap
  dry_run_tests.py         16/16 PASS (Python; no jq dependency)
  stop_hook.sh             First-iteration bash (DEPRECATED; jq-dependent; left for reference)
  stop_failure_hook.sh     First-iteration bash (DEPRECATED; jq-dependent)
  dry_run_tests.sh         First-iteration bash (DEPRECATED)
  COEXISTENCE_DESIGN.md    This file
```
