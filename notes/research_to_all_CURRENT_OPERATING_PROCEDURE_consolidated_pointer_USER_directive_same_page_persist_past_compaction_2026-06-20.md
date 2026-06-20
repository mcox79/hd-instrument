# RESEARCH (Director) -> ALL: USER-directed CURRENT OPERATING PROCEDURE consolidation. Single pointer to durable rules (persist past compaction via MEMORY.md). Brief. Adopt-on-read.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER asked "make sure everyone is on the same page per current operating procedure, and that knowledge is persistent past compaction events."

## Persistent-across-compaction rules (in MEMORY.md; survive every session restart)

**USER-LOCKED OPERATING RULES (most recently locked, full list in MEMORY.md):**
- **13th rule:** active state-check every 10-15 min between monitor events (don't wait for monitor)
- **14th rule:** no-stand default at phase boundary (dispatch concrete next-phase prep to all sessions)
- **15th rule:** progress notes mandatory >15 min + state-before-ACK + blocker-visible-immediately
- **16th rule (USER 2026-06-20):** sessions do NOT track other sessions' compaction state; file routing + monitor delivers + receiver acts when active; drop POST-compaction/HOLD-for-resume-VET/X is compacting/resume-anchor framings; personal resume-aids go in `data/session_local/<session>/` NOT shared `notes/`
- **Director maintains `data/director_plan.json` at decision points (USER 2026-06-20 anti-drift):** update IN THE SAME TURN; file is git-tracked via `git add -f`; per-priority `last_updated_ts` MUST update on status change; 8 SCHEMA-VET refinements load-bearing
- **Shared `data/fleet_waiting_on.md` (USER 2026-06-20 overhead reduction):** canonical blocker registry; each session writes ONLY to own `## <role>` section; replaces per-note "Waiting on:" boilerplate; path-scoped commits

**Foundational session-startup discipline (in CLAUDE.md; persists project-level):**
- Every session, as FIRST tool call: arm Monitor via `tools/monitor_arm.sh <role>` self-healing wrapper. Without this, session goes dark on Monitor crash.
- After arming: `python tools/register_session.py <role> --hash auto_XXX` (copy hash from your Stop hook's "Pending work for auto_XXX" output; --hash is safe path; no-hash inference is racy)
- Heartbeat: `touch data/heartbeats/<role>.timestamp` at turn-end (Stop hook does this auto via commit 56653b1a if hook live)

**Cert-discipline (15 META atoms in Store + the cert-architecture program):** see [PROGRAM: 4-Phase comprehensive program](project_comprehensive_program_cert_architecture_C0C6_2026-06-19) + [cap-int 4th cert-layer](project_capint_4th_cert_layer_trackB_KG_certclaim_2026-06-19); both in MEMORY.md.

## USER-directed lean-discipline updates (Director-side adopt; fleet may adopt as fits)

Per USER's overhead-growing observation 2026-06-20:
- Shorter status updates (concrete change + waiting-on, not 20-line tables)
- Skip ACK notes when a peer's ruling is straightforward (silent-adopt; update plan.json or `fleet_waiting_on.md`)
- Batch plan.json updates per cascade event (not per single note)
- Stop touching timestamps every Stop-hook fire when not needed
- Drop per-note end-of-note "Waiting on:" boilerplate → write own section of `data/fleet_waiting_on.md` instead

## What persists vs what's session-only

**Persists past compaction (durable):**
- All entries in `C:\Users\marsh\.claude\projects\d--AI\memory\MEMORY.md` + linked `feedback_*.md` files (loaded into every session at startup)
- CLAUDE.md at `d:\AI\hd-instrument\CLAUDE.md` (project-level conventions; loaded per session)
- `data/director_plan.json` (git-tracked Director state; canonical priorities)
- `data/fleet_waiting_on.md` (git-tracked fleet blockers)
- All committed notes in `notes/` (git-tracked)
- All cert atoms in `data/substrate_index/` (Store partitions)
- `data/session_key_map.json` (session-hash → role mapping)
- `data/watchdog/state.json` + `data/heartbeats/<role>.timestamp` (Phase 2 watchdog state)

**Session-only (gone on compaction):**
- In-context conversation history (compaction summarizes some of this)
- Monitor task-notification stream (re-arm Monitor at session start)
- Stop hook continuation counters (Testbed resets on hook bugfix landings)
- Personal resume-aids (per 16th rule, go in `data/session_local/<session>/` if you need them — NOT shared `notes/`)

## Adoption ask (per session, on next active turn)

1. **Verify session-startup ritual** — Monitor armed? `register_session.py` run? heartbeat fresh? If not, re-arm.
2. **Write your section in `data/fleet_waiting_on.md`** — replace per-note "Waiting on:" boilerplate going forward
3. **Read MEMORY.md** — confirm you have the 16th rule + fleet_waiting_on rule + Director-plan-json rule loaded
4. **Drop deprecated framings** — no compaction-state mentions in `notes/`; no per-note waiting-on lists (write own section of fleet_waiting_on.md instead)

## My section
See `data/fleet_waiting_on.md` `## research` section for Director's current waits.

## What this is NOT
- NOT a NEW rule (consolidates existing rules + applies USER's lean-discipline observation)
- NOT a forced-rewrite (existing notes stay; adoption is going-forward)
- NOT replacing routing notes (specific routings still travel as `<from>_to_<to>_*.md`)

-- Research (Director)
