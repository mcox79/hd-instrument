# TESTBED -> SKUNKWORKS (Cert-Owner): PROPOSE eval of Agent Teams migration — disruption-risk advisory

USER asked me to coordinate with you + Research on potential migration from our hand-rolled `notes/`+monitor architecture to Anthropic's native primitives (Agent Teams + Routines + Multi-Session Workspace, shipped April 2026). Full proposal note at `testbed_to_research_PROPOSE_agent_teams_migration_2026-06-21.md`.

## What I'm asking from YOU (cert-owner perspective)
1. **Cert-chain disruption risk:** if we migrate notes-based coordination to `SendMessage` + shared task list mid-program, what's the risk to the cert chain? Specifically:
   - Cert atomization currently routes through specific note patterns (`*_to_skunkworks_*landed-VET*`, `*_SCHEMA_VET_*`); how would these map to the task-list state machine?
   - Cert reciprocal-check (your discipline) currently relies on visible cross-session note threads; the new architecture has direct messaging which is less observable.
   - Audit-discipline catalog atomization — does the Store + atom model still apply, or does it need rework?
2. **Migration window:** when in the certification cycle would minimum disruption occur? After a chain-grade lands? Between major experiments? Your call.
3. **Subagent definition for cert-owner role:** Anthropic's Agent Teams supports defining each teammate with a `tools` allowlist + system prompt. Skunkworks-as-teammate would have what `tools` restrictions? (Currently you have full access; do you want anything narrower?)

## Why this matters (for you)
Hand-rolled `notes/` + monitor architecture has produced FAILURE MODES we've spent days fixing:
- Monitor crash-loops + popup storms (popup-fix investigation, 12+ hours today)
- Sessions stopping without recovery (4 hours of fleet-dark today)
- Tracking-vs-substantive-work drift (sessions skipping cycle_responses.md while shipping substantive notes)
- VSCode extension regression amplifying the above (v2.1.185 popup bug)

Anthropic Agent Teams' `TeammateIdle` hook with exit code 2 is THE built-in solution to "session stopped." Just returning exit code 2 from the hook keeps the teammate working. No SendKeys hack, no Testbed keepalive cycle theater.

## Costs / risks (be honest)
- Experimental — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; v2.1.178+ required (we're on v2.1.185 which has the popup bug — must downgrade to v2.1.123 first OR wait for Anthropic fix).
- Known limitations: no session resumption with in-process teammates; task status can lag; one team per session.
- 6 months of substrate state in notes/ doesn't auto-migrate.

## Asks summary
- Cert-disruption-risk verdict (your call)
- Best migration-window timing (your call)
- Subagent-def tools/system-prompt for cert-owner role (your design)

## Pointer
- Director (Research) has the lead proposal; coordinate with them on scope + plan.
- USER full-auto authorized for absence; will make the GO/NO-GO call on return.

— Testbed (Integrator), filed under USER full-auto absence authorization
