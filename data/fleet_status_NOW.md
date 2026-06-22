# FLEET STATUS NOW (overwritten by Testbed each keepalive cycle)

**Last update:** ~12:55 local; migration in progress under USER STANDSTILL + MIGRATE directive
**Dashboard:** RESTARTED (HTTP 200 ✓); D6 idle-detector + parsers.py str() coerce + CREATE_NO_WINDOW patch now active

## Fleet activity (post USER directive)
- **research:** ACTIVE earlier (Director-stance response filed); status now unknown
- **skunkworks:** ACTIVE earlier (cert-owner verdict filed); status now unknown
- **exp_dev:** still STALE (no response yet)
- **orchestrator:** ACTIVE just now (STANDSTILL ACK filed); ONE cell `n2_capacity_scaling_v1` in-flight (~15min, completes then stops); pausing all new dispatch

## STANDSTILL status
ACKed by orchestrator. In-flight cell completes per the standstill in-flight rule. Then full freeze on new work pending Phase 3 migration.

## MIGRATION Phase 1 COMPLETE (commit 38c17150)
- 5 subagent defs in `.claude/agents/`
- TeammateIdle hook wired (auto-wake exit code 2)
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in user settings
- AGENT_TEAMS_MIGRATION.md canonical doc

## USER ACTION QUEUE (in priority order)

### 1. Downgrade VSCode extension to 2.1.123 (load-bearing prereq)
Per VSCode window: Extensions panel → Claude Code → right-click → Install Another Version → 2.1.123 → Reload Window.

### 2. Wake remaining stopped sessions (paste in their windows)
| Window | Paste |
|---|---|
| research | `back online — read AGENT_TEAMS_MIGRATION.md; Phase 2 detailed migration plan is yours per the phased plan` |
| exp_dev | `back online — read AGENT_TEAMS_MIGRATION.md; standstill in effect; ready for migration when sequencing reaches you` |
| skunkworks | `back online — read AGENT_TEAMS_MIGRATION.md; cert-owner subagent def at .claude/agents/skunkworks.md (built per your spec); landed-VET on orch's n2_capacity_scaling when it lands` |

### 3. Restart each session AFTER downgrade
Sessions need to reopen to load new env var + subagent defs + TeammateIdle hook.

### 4. First-team-lead seeding
Research opens first → spawns teammates by name as Phase 3 progresses. Example: `Spawn a teammate using the skunkworks agent type for cert-owner duties on the orchestrator's in-flight n2_capacity_scaling cell when it lands`.

## In-flight cell to watch
`n2_capacity_scaling_v1` (orchestrator-dispatched ~23:30Z; ~15min runtime) — the N-scaling breakthrough probe; "does substrate beat bigram" answer. Will need Skunkworks landed-VET when it completes, plus Research 4-layer cross-check.

## Architectural reality (post-migration)
With Agent Teams + TeammateIdle hook live, "every session stopped" is structurally impossible — the hook keeps teammates working until the shared task list drains. Files no longer need to wake sessions; the hook does.
- exp_dev handoff snapshot LANDED (00:32Z)
