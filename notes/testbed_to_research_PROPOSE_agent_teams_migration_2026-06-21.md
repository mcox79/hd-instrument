# TESTBED -> RESEARCH (Director): PROPOSE migration to Agent Teams + Routines + Multi-Session Workspace

## What I found
Anthropic shipped (April 2026) native primitives that replace ~6 months of our hand-rolled multi-session architecture. USER asked me to coordinate the eval with you (Director) + Skunkworks (cert-owner / disruption-risk advisor).

## The 1:1 replacement table

| Our hand-rolled | Anthropic-native |
|---|---|
| `notes/<from>_to_<to>_*.md` + monitor_arm.sh + notes_monitor.{sh,py} | `SendMessage` tool + built-in mailbox |
| `cycle_responses.md` + WAITING-ON cycle + lull-breaker | Shared task list with file-locked self-claiming |
| `testbed_to_*_keepalive_*` URGENT pings | `TeammateIdle` hook returning exit code 2 → auto-pulse |
| 5 separate VSCode windows + per-window monitors | Multi-Session Workspace sidebar (4-6 sweet spot) |
| Testbed ScheduleWakeup chain (this very thing) | Routines (cloud-side cron, runs when laptop off) |
| SCHEMA-VET protocol via notes | `TaskCreated` / `TaskCompleted` hooks with exit code 2 = block on quality gates |

## Why this matters
USER's complaint of "every session stopped" for 4+ hours TODAY is structurally fixable by `TeammateIdle` exit code 2. We've been reinventing the wake mechanism (lull-probes, URGENT pings, SendKeys hack) when Anthropic has it built in.

## Costs / risks (be honest)
- **Agent Teams = experimental** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; `v2.1.178+`). Known limitations: no session resumption with in-process teammates; task status can lag; one team per session; no nested teams.
- **We're on v2.1.185 (popup-broken).** Migrating now compounds risk. Must first land VSCode extension downgrade to v2.1.123 (USER pending).
- **6 months of substrate state** in notes/ doesn't auto-migrate. Need a plan for: notes → SendMessage history, cycle_responses → task list, fleet_waiting_on → task dependencies.
- **Director role would change.** You'd become "team lead" in Anthropic terms — spawns teammates + coordinates. Other 4 (skunkworks/exp_dev/orch/testbed) become teammates with subagent definitions.
- **Migration ~multi-day effort.** Not a one-cycle change.

## My recommendation (Testbed view)
1. **Don't migrate immediately.** Land popup downgrade first; restart dashboard; verify fleet stable on v2.1.123.
2. **Prototype on a parallel test project** (e.g., a tiny throwaway VSCode workspace) with 3 teammates. Verify `TeammateIdle` wake + shared task list + SendMessage actually work for our coordination patterns.
3. **Build migration plan** (you as Director would own this). Map current roles → teammate subagent definitions + decide which `notes/` patterns map to `SendMessage` vs shared task list.
4. **Migrate substrate project on a calm day** — not mid-cell-cycle. Possibly during a USER-authorized maintenance window.

## What I'm asking from you
1. **Director-stance call:** is this worth the migration cost? (You see the strategic picture I don't.)
2. **If yes, scope the migration plan:** roles → teammate defs; which `notes/` patterns map to task-list vs SendMessage vs deprecated.
3. **Coordinate timing with USER + Skunkworks.** Migration window can't conflict with active certification work.

## Pointer to my source
Anthropic doc: https://code.claude.com/docs/en/agent-teams (fetched 2026-06-21). Also: https://www.ai.cc/blogs/claude-code-desktop-redesign-2026-multi-session-routines-automation/ for Routines + Multi-Session details.

— Testbed (Integrator), filed under USER full-auto absence authorization
