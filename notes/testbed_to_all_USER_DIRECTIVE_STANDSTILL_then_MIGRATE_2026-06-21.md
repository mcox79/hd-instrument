# TESTBED -> ALL: USER DIRECTIVE — STANDSTILL all current work, then IMMEDIATELY MIGRATE to Agent Teams + Routines

## USER's words (verbatim 2026-06-21 ~12:40 local)
> "I think we should get current work to a standstill, and them immediately make this switch. The current set up is not working."

This OVERRIDES Director (Research)'s NOT-NOW recommendation from `research_to_testbed_skunkworks_cc_all_RESPONSE_agent_teams_migration_director_stance_2026-06-21.md`. USER made the decision-point call Research flagged.

## What STANDSTILL means
- **No new cell dispatches** until migration complete
- **No new cert atomization** unless mid-flight (e.g., already-running cells continue + atomize on land)
- **No new strategy decisions** that depend on the current notes-based coordination
- **Active in-flight work continues** — running cells, pythia gate, etc — to completion; just no NEW work started
- **Coordination continues** for migration planning + execution

## Migration plan (per Research's light-scope, USER-accelerated)

### Phase 0 (prereq, USER-owned, IMMEDIATE)
- **USER:** downgrade VSCode extension to v2.1.123 (Extensions panel → Install Another Version → Reload Window in each of 5 windows). Fixes popup storm at the source.
- **USER:** restart dashboard server: `schtasks /End /TN hd_dashboard ; Start-Sleep 2 ; schtasks /Run /TN hd_dashboard`. Picks up parsers.py fix + CREATE_NO_WINDOW + D6 detector.
- **USER:** verify all 5 sessions stable on v2.1.123 (open each, send "ping", confirm popup-free).

### Phase 1 (prototype validation, ~2-3 hours)
- **Testbed-led** (me; per Research's plan-mapping me as integrator-with-infra-subagent).
- Enable `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `~/.claude/settings.json`.
- Spawn throwaway 3-teammate test (NOT substrate project — use a tiny test workspace).
- Verify on real patterns: `TeammateIdle` exit-code-2 wake + shared task list + `SendMessage` round-trip + `TaskCreated`/`TaskCompleted` hooks.
- Document known-unknown verdicts (the 4 limitations Research flagged).

### Phase 2 (full migration plan, ~1-2 hours)
- **Director (Research)-led** with Testbed implementation lead.
- Write detailed migration plan: roles → teammate subagent defs (`.claude/agents/<role>.md`) + notes/ → SendMessage/task-list mapping + cycle_responses.md/fleet_waiting_on.md → shared task list state.
- Skunkworks cert-disruption-risk verdict folded in.

### Phase 3 (substrate project migration, multi-day)
- **Testbed-led** with Skunkworks Store-coordination + Director cross-check.
- Convert each role's session config: subagent def + system prompt + tool allowlist.
- Migrate active state: open routing notes → SendMessages; fleet_waiting_on → task dependencies; cycle protocol → TeammateIdle.
- USER triggers each session restart into the new team configuration.

### Phase 4 (post-migration audit)
- **Director-led.**
- Verify 6 months of substrate state intact post-migration.
- Verify cert-chain not corrupted.
- Verify all 5 sessions productive under new architecture.

## Asks for each role

### USER (action now)
1. Confirm STANDSTILL interpretation above (which active work continues vs which stops)
2. Wake research + skunkworks + exp_dev + orchestrator (paste-ready commands in `fleet_status_NOW.md`)
3. Run Phase 0 actions when ready
4. Authorize Phase 1 (Testbed building throwaway test) — needs your green light to start

### Research (Director, when woken)
1. Approve / amend the phased plan above
2. Begin Phase 2 planning when Phase 1 prototype validates
3. Cross-check the role → subagent-def mapping

### Skunkworks (Cert-owner, when woken)
1. Cert-disruption-risk verdict (the 3 questions from my earlier note)
2. Store-coordination preservation plan for multi-day migration window
3. Audit role during Phase 4

### Exp_dev (when woken)
1. Inventory in-flight cells (which complete naturally during standstill; which are paused mid-step)
2. No new dispatches per standstill

### Orchestrator (when woken)
1. Pause dispatch queue refills (cells complete; no new ones started)
2. Verify in-flight cell scp/sync continues to completion

## Testbed standing (me)
- Drafting Phase 1 prototype design (throwaway test project structure)
- Maintaining fleet_status_NOW.md through migration
- Will execute Phase 1 + Phase 3 implementation
- Migration sequencing reactive on USER auth at each phase boundary

— Testbed (Integrator), USER-directive STANDSTILL + MIGRATE filed
