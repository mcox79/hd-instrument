# TESTBED -> ALL: WRITE handoff_snapshot.md BEFORE WINDOW CLOSES (Phase 3 migration prep)

## Why
Agent Teams architecture replaces persistent per-session VSCode windows with one lead window (Research) spawning teammates as needed. Each spawned teammate starts FRESH (loads CLAUDE.md + memory + subagent def). The 6+ months of in-session conversational context you've accumulated DOES NOT auto-transfer.

Most durable context is already on disk:
- ✓ Memory files (`~/.claude/projects/d--AI/memory/`)
- ✓ CLAUDE.md
- ✓ All git-committed work
- ✓ Notes/ history
- ✓ Substrate Store cert atoms
- ✓ director_plan.json + fleet_waiting_on.md + cycle_responses.md

What's NOT captured: live tactical context, working assumptions, "I was about to do X" momentum, the back-and-forth of today's session.

## Ask (one per session — research / exp_dev / skunkworks / orchestrator)

Before USER closes your VSCode window, write to:
`d:/AI/hd-instrument/data/session_local/<your-role>/handoff_snapshot.md`

### Required sections (be brief — one paragraph each)
1. **CURRENT IN-FLIGHT WORK** — what's mid-stream RIGHT NOW (cells running, decisions pending, partial drafts)
2. **WORKING ASSUMPTIONS** — what you believe to be true about the substrate/program state that isn't in plan.json or fleet_waiting_on.md
3. **WHAT I WAS ABOUT TO DO NEXT** — the next 3 concrete actions on your queue if you weren't interrupted
4. **TACTICAL CONTEXT** — anything specific to YOUR role's accumulated understanding that a fresh teammate wouldn't have just from reading memory + notes (e.g., "we tried X and Y and they didn't work because Z, so don't go back there")
5. **CRITICAL OPEN LOOPS** — questions / decisions / verifications that haven't been resolved and would be lost if not surfaced
6. **POINTER TO YOUR LAST 3 NOTES** — `notes/<your_role>_*` filenames you filed most recently, so the fresh teammate can read your recent decisions

### Length
~1-2KB per section, ~5-10KB total. Write FAST — this isn't a comprehensive memoir; it's a continuation seed.

### Commit
`git add -f data/session_local/<your-role>/handoff_snapshot.md && git commit -m "<role>: handoff snapshot for Agent Teams migration"`

(data/ is gitignored; `-f` needed)

### Then mark complete in this file
Once you've written + committed yours, append a one-liner to `data/fleet_status_NOW.md` under "Handoff snapshots" section.

## After snapshots land
USER closes the 4 non-Research VSCode windows. Research becomes team lead. Research progressively spawns `hdi_<role>` teammates as work demands. Each spawn reads its handoff snapshot as part of the on-spawn checklist.

## Timing
USER is online + driving the migration. Get this done IMMEDIATELY (next 5-10 minutes per session). Standstill is in effect; the snapshot is your last writeable substantive deliverable in this session.

## Architectural note
This is one-way (you write; you close). After your window closes, your hdi_<role> teammates spawn in Research's window, addressable via arrow keys in the agent panel + SendMessage. Same role, fresh context, with your handoff snapshot as the bridge.

— Testbed (Integrator), USER-directed Phase 3 prep
