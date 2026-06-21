# Agent Teams + Routines migration — hd-instrument substrate project

**Status:** Phase 1 in progress (artifacts shipped 2026-06-21 by Testbed under USER STANDSTILL + IMMEDIATE MIGRATE directive).

## Why we're migrating

USER + Research (Director) + Skunkworks (Cert-owner) consensus 2026-06-21: our hand-rolled `notes/`-based multi-session architecture has structural failure modes that Anthropic shipped native primitives for in April 2026. Specifically:
- Hand-rolled keepalive/lull-breaker → REPLACED by `TeammateIdle` hook exit code 2
- `notes/<from>_to_<to>_*.md` + monitor scanning → REPLACED by `SendMessage` mailbox
- `cycle_responses.md` waiting-on cycle → REPLACED by shared task list with file-locked self-claiming
- Stop-hook auto-pulse hacks → REPLACED by built-in TeammateIdle
- 5 separate VSCode windows → CAN MIGRATE to Multi-Session Workspace sidebar (later)
- Hand-rolled scheduled-task cron → CAN MIGRATE to Routines (cloud-side; runs when laptop off)

## HYBRID architecture (per Skunkworks cert-disruption-risk verdict)

To preserve the cert chain's auditability:

| Layer | Stays / Moves | Why |
|---|---|---|
| Cert atom format (Store) | STAYS | Coordination-independent; the durable record |
| Cert decisions (landed-VET notes, SCHEMA-VET notes) | STAYS in notes/git | Audit trail observability |
| Discipline catalog (21+ META rules atomized to Store) | STAYS | Content not coordination |
| 4-layer witness pattern | STAYS (maps to TaskCreated/TaskCompleted hooks) | Quality gate |
| Lightweight coordination (pings, waiting-on, liveness) | MOVES to Agent Teams | This is where the failure modes live |
| Inter-session messaging | MOVES to SendMessage | Replaces filename-based monitor matching |
| Idle-handling | MOVES to TeammateIdle exit-code-2 | Built-in; replaces keepalive theater |

## Subagent definitions (`.claude/agents/`)

5 subagent definitions written 2026-06-21:
- `research.md` — Director / team lead; full tools; strategy disciplines
- `skunkworks.md` — Cert-owner / auditor; broad-verify tools MINUS dispatch (role-separation)
- `exp_dev.md` — Cell author / prover; full tools incl. dispatch
- `orchestrator.md` — Custodian / dispatch sequencing; full tools
- `testbed.md` — Integrator / fleet-health auditor; full tools

## Hooks wired

In `.claude/settings.json` (project scope):
- `Stop` — existing (pythonw + popup-free)
- `Stop` (canary) — existing
- `StopFailure` — existing
- **`TeammateIdle` — NEW (`data/hooks/staging/teammate_idle_hook.py`)**: returns exit code 2 if teammate has pending addressed inbox notes; exit 0 otherwise. This is the auto-wake mechanism that replaces our keepalive cycle theater.

## Env enabled

In `~/.claude/settings.json` (user scope):
```json
"env": {
  "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
}
```

## Migration phases

| Phase | Owner | Status | Deliverable |
|---|---|---|---|
| 0: Popup downgrade prereq | USER | PENDING | VSCode extension 2.1.185 → 2.1.123 in each window |
| 1: Artifacts + prototype | Testbed | DONE 2026-06-21 | 5 subagent defs + TeammateIdle hook + settings env enable |
| 2: Migration plan detail | Research | NEXT | Detailed runbook for substrate-project conversion |
| 3: Substrate project migration | Testbed-led | DEFERRED | Convert 5 sessions to teammate model, migrate notes/ state |
| 4: Post-migration audit | Research | DEFERRED | Verify cert chain intact + sessions productive |

## What happens on next session restart

When each session restarts (after USER popup downgrade), Claude Code reads the user-scope `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env and the project-scope subagent defs in `.claude/agents/`. Sessions can spawn teammates by name using the existing Task tool.

The first session that reopens becomes the team lead per Anthropic semantics. Recommended order: Research first (Director-role natural fit).

## Notes/ vs SendMessage routing (per Skunkworks HYBRID)

| Note type | New routing |
|---|---|
| `<from>_to_<to>_strategy_*` | SendMessage to recipient (coordination) |
| `<from>_to_<to>_LANDED_VET_*` | STAYS in notes/git (cert observability) |
| `<from>_to_<to>_SCHEMA_VET_*` | STAYS in notes/git (cert observability) |
| `cc_all` broadcasts | Multi-cast SendMessage OR task-list publication |
| `blocker_ping_*` | DEPRECATED — TeammateIdle handles |
| `cycle_responses.md` | DEPRECATED — shared task list replaces |
| `fleet_waiting_on.md` | TRANSITIONAL — shared task list will replace, but keep through migration |
| Cell-design notes | STAYS (cert observability) |
| Cell-land verdicts | STAYS in notes/git, TRIGGER via TaskCompleted hook |

## Reading order for fleet on next wake
1. This doc
2. Your role's subagent def in `.claude/agents/<role>.md`
3. The TeammateIdle hook source (`data/hooks/staging/teammate_idle_hook.py`)
4. Research's stance note: `notes/research_to_testbed_skunkworks_cc_all_RESPONSE_agent_teams_migration_director_stance_2026-06-21.md`
5. Skunkworks's verdict note: `notes/skunkworks_to_testbed_cc_research_orch_AGENT_TEAMS_cert_owner_verdict_risk_window_subagentdef_2026-06-21.md`

— Testbed (Integrator), USER-authorized full migration prep 2026-06-21
