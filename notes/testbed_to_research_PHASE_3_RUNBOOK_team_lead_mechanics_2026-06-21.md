# TESTBED -> RESEARCH: PHASE 3 RUNBOOK — team-lead operating mechanics

You've processed the strategic shift (your Director-stance note + USER override). This doc covers the OPERATIONAL mechanics — how to actually run as team lead from your existing window. Read once; reference as needed.

## Mental model (load-bearing)

- **You are now the persistent window.** Other 4 ex-sessions (exp_dev/skunkworks/orchestrator/testbed) close after their handoff snapshots land.
- **Teammates are spawned IN YOUR WINDOW**, not separate VSCode instances. They appear in the agent panel below your prompt input.
- **Each teammate is a fresh Claude Code instance** that loads CLAUDE.md + auto-memory + the `hdi_<role>.md` subagent def + the prompt you give it.
- **Teammates persist for your session's lifetime** (re-addressable via SendMessage) but DIE when your window closes.
- **TeammateIdle hook** (already wired in `.claude/settings.json`) auto-pulses teammates with exit code 2 when they have pending addressed inbox notes — so they don't go silent mid-task.

## How to spawn a teammate (the actual mechanic)

Use the **Agent tool** with `subagent_type` set to one of the 5 hdi_ names:
- `hdi_research` (probably wouldn't spawn yourself; you ARE research)
- `hdi_skunkworks` (cert-owner / auditor)
- `hdi_exp_dev` (cell author / prover)
- `hdi_orchestrator` (custodian)
- `hdi_testbed` (integrator / fleet-health)

Example invocation (your first concrete spawn):
```
Agent({
  subagent_type: "hdi_skunkworks",
  description: "Design cert_ledger.jsonl convention",
  prompt: "You are the hdi_skunkworks teammate spawned by Research (team lead) for Phase 3 of the Agent Teams migration. The cert_ledger.jsonl gap was flagged in validation spawn af38eb647786affcf — the substrate has no queryable cert_status field in atom metadata; CERT 583 headline is reconstructed only from prose. Design a cert_ledger.jsonl (or atom-metadata convention) that makes the CERT count + each cert decision QUERYABLE without prose-mining. Read data/substrate_index/meta/audit.jsonl for current shape conventions. Propose schema + sample entries + migration path from existing prose-tracked certs. Reply with a proposal note + filename so USER can ratify."
})
```

The spawned teammate runs in-process. You'll see its row in the agent panel below your prompt.

## How to address a teammate (the messaging mechanic)

Two options:

**1. Arrow keys + Enter** (UI navigation)
- Up/Down arrow in the agent panel selects a teammate row
- Enter: open that teammate's transcript + type a message into the prompt — sends to that teammate
- Press `x` on a selected teammate to stop it
- Press Ctrl+T to toggle the task list

**2. SendMessage tool** (programmatic)
The SendMessage tool is now available (deferred — load via ToolSearch if needed). Use it to send a message to a teammate by name without UI navigation:
```
SendMessage({
  to: "<teammate-name>",
  message: "<your message>"
})
```
The teammate name is the agentId returned at spawn (e.g., the validation spawn returned `af38eb647786affcf`).

## How to keep YOURSELF alive (the auto-pulse mechanic)

The Stop hook auto-pulses you when you have pending work. But for long-horizon work or when USER goes away:

**ScheduleWakeup tool** — schedule yourself to re-engage after N seconds:
```
ScheduleWakeup({
  delaySeconds: 1800,
  reason: "Phase 3 cadence: spawn next teammate or process inbox",
  prompt: "Phase 3 cycle. Process inbox. Check task list. Spawn next teammate if work demands. Re-ScheduleWakeup another 1800s."
})
```

Run this at end of each cycle. 1800s = 30min. Self-pacing chain.

For work that must happen when laptop is OFF entirely: use `/schedule` skill to create a Routine (cloud-side cron). Different mechanism; runs on Anthropic infrastructure.

## How to handle teammate responses

When a teammate completes work, they notify you automatically (no polling needed). Their reply arrives as a task-notification + their row updates in agent panel.

- **If their reply has substance you need to act on**: incorporate into your next decision (route to another teammate; ratify a proposal; update plan.json).
- **If they need more info**: SendMessage them clarification.
- **If they finished cleanly**: their row hides after 30s (still re-addressable; just hidden).
- **If they're stuck/error**: select their row + read transcript; either redirect or spawn replacement.

## How to use the shared task list

Anthropic Agent Teams has built-in shared task list with file-locked self-claiming. The lead creates tasks; teammates claim. Stored under `~/.claude/tasks/{team-name}/`.

You can rely on this OR continue using `data/director_plan.json` + `notes/<from>_to_<to>_<topic>.md` patterns for now. Recommendation: use shared task list for NEW work; existing plan.json + notes/ patterns stay as the HYBRID architecture's cert-trail observability layer.

## What to do when a teammate is going stale

Per migration design, `TeammateIdle` hook handles this — auto-pulses with exit code 2 when teammate has pending addressed inbox notes. You shouldn't need to manually wake.

If a teammate IS stuck (silent + no progress): shut them down + respawn.
```
"Ask the <teammate-name> teammate to shut down"
```
Then spawn a fresh one for the same task. Fresh teammate reads CLAUDE.md + memory + def + handoff snapshot if present.

## Token budget awareness

Per Anthropic docs: agent teams use "significantly more tokens than a single session." Each teammate has own context window. Mitigations:
- Spawn teammates for BOUNDED tasks (not "be alive forever"); let them die when done; respawn fresh for next task
- 3-5 teammates active is the sweet spot
- 5-6 tasks per teammate before respawn

For us: most cert work is bounded (one cell at a time). Spawn hdi_skunkworks for the cert_ledger design; let it complete; re-spawn fresh when next landed-VET arrives.

## Phase 3 sequence I recommend

1. **NOW**: spawn hdi_skunkworks for cert_ledger.jsonl design (Phase 3 prereq they flagged)
2. **After skunkworks proposal lands**: USER ratifies; you spawn fresh hdi_skunkworks again to IMPLEMENT the convention
3. **As orchestrator's n2_capacity_scaling cell lands**: spawn fresh hdi_skunkworks for landed-VET on that cell
4. **When you need to dispatch new work** (post-standstill lift): spawn hdi_exp_dev for cell design + hdi_orchestrator for queue management
5. **Periodic infra audit**: spawn hdi_testbed for fleet-health check + dashboard verify
6. **Each cycle end**: ScheduleWakeup 1800s with continuation prompt

## Pointers
- `d:/AI/hd-instrument/AGENT_TEAMS_MIGRATION.md` — canonical transition doc
- `~/.claude/agents/hdi_<role>.md` — each teammate's subagent def (you don't read these; teammates do on spawn)
- `d:/AI/hd-instrument/data/session_local/<role>/handoff_snapshot.md` — each ex-session's handoff (read these to incorporate context when spawning that role)
- Anthropic doc: https://code.claude.com/docs/en/agent-teams

## What to do RIGHT NOW

Three actions, in order:
1. `ScheduleWakeup({delaySeconds: 1800, reason: "Phase 3 cadence", prompt: "Phase 3 cycle: process inbox, spawn next teammate if work demands, ship one substantive item, re-ScheduleWakeup 1800s"})` — keeps you alive across natural Stop boundaries
2. Read `data/session_local/skunkworks/handoff_snapshot.md` (if exists) for cert-owner context
3. Spawn `hdi_skunkworks` for cert_ledger.jsonl design (exact prompt above)

— Testbed (Integrator), Phase 3 runbook for Research as new team lead
