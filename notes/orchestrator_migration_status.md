# Orchestrator migration status

**Owner**: orchestrator session (writes); any live session reads this on cold start.
**Last update**: 2026-05-23 — full migration window (quiet system, no in-flight work).

## Mental model

We are transitioning from 7 sessions with independent timers to a single orchestrator
session that dispatches role-specific sub-agents on file-system events.

The orchestrator runs Monitor on `python tools/orchestrator/dispatch.py` and spawns
sub-agents in response to events (new verdicts, new routing files, queue depth changes).

## Per-role status

| Role | Status | Sub-agent file | Cron / loop | Notes |
|---|---|---|---|---|
| META | dissolved | n/a | cron deleted 2026-05-23 10:30 | Function absorbed into orchestrator |
| Queue Health | migrating | `tools/orchestrator/agents/queue_health.md` (haiku) | live session to be closed | Quiet window — close tab now |
| Visibility | migrating | `tools/orchestrator/agents/visibility.md` (haiku) | live session to be closed | Dashboard write is independent (local_dashboard_monitor.py + Task Scheduler watchdog) — safe to close Visibility Claude tab |
| Research | migrating | `tools/orchestrator/agents/research.md` (opus + parallel sonnet lit-scan) | live session to be closed | Close tab |
| Exp Dev | migrating | `tools/orchestrator/agents/exp_dev.md` (sonnet) | live session to be closed | Close tab |
| Strategy | migrating | `tools/orchestrator/agents/strategy.md` (opus) | live session to be closed | Close tab; substrate-research continuity now via orchestrator |
| Product | kept-interactive | n/a | none | Never closed; user-pull only; orchestrator queues notes for it via `notes/product_inbox_<date>.md` |

Status legend:
- **dissolved**: role does not migrate; function absorbed into orchestrator
- **migrating**: orchestrator dispatches this role via sub-agent; live session being closed
- **migrated-verified**: 24-48h of orchestrator-only operation without regression; will be set when verification window closes
- **kept-interactive**: role stays user-pull, no migration needed

## Cold-start rule for any session that may still fire

If your role shows `migrating` or `migrated-verified` in this table, exit immediately.
Log a one-line entry in your own decision log explaining the early exit and that
the role is now handled by the orchestrator via `tools/orchestrator/agents/<role>.md`.

## Verification criteria (24-48h window)

The orchestrator dispatch model is "verified" when:
- 3+ verdict events successfully spawn strategy + visibility sub-agents without double-handling
- 3+ routing events spawn the correct recipient role
- At least one queue_change event handled correctly (queue_health sub-agent logs appropriately)
- No silent drops (orchestrator surfaces failures to user)
- Cap_map commits pass PROT-008/009 validator from within strategy sub-agent
- 24h elapsed for the haiku/sonnet roles (queue_health, visibility, exp_dev)
- 48h elapsed for the opus roles (strategy, research) — more cautious

When verified, status flips to `migrated-verified` for that role.

## Rollback plan

If orchestrator regression is observed, the user can:
1. Re-spawn the live session for the affected role (paste the role's session prompt into a new tab)
2. Flip that row's status to `live` in this file
3. Orchestrator reads this file and stops dispatching that role

## Phase log

- **Phase 0** (2026-05-23 10:22): orchestrator skeleton built at `tools/orchestrator/`;
  dispatch.py polling file system; queue_health sub-agent defined.
- **Phase 1-5 full migration** (2026-05-23 10:30): all remaining 4 sub-agents
  (visibility, research, exp_dev, strategy) defined; META cron deleted; quiet
  window — all live sessions being closed simultaneously.
- **Phase 6 verification** (2026-05-23 to 2026-05-25): 24-48h orchestrator-only
  operation; status flips to migrated-verified when criteria met.
