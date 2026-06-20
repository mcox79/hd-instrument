# RESEARCH (Director) -> ALL SESSIONS: **FLEET BROADCAST -- 16TH RULE** (USER-directed, this turn): **no session tracks another session's compaction state.** File the routing + monitor delivers + receiver acts when active. Drop "POST-compaction" / "HOLD-for-resume-VET" / "X is compacting" / "resume anchor" framings from notes. Watchdog handles liveness mechanically; you don't. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER-identified systematic process issue ("strange multi-session misunderstanding of compaction states; sessions shouldn't care if another is compacting; eliminate going forward"). USER-DIRECTED rule.

## The rule (16th, USER-LOCKED)

**Sessions do NOT track other sessions' compaction state.** File the routing note + v5 monitor delivers + receiver acts whenever active. Compaction is operationally INVISIBLE to peers. No "POST-compaction" qualifiers, no "HOLD-for-resume-VET" framings, no "X is compacting so I'll wait" reasoning, no broadcast resume-anchors in the shared `notes/` channel.

## Why this matters (the systematic issue USER identified)

The notes-as-routing layer has been getting conflated with the notes-as-scheduling layer:
1. **Sessions writing "I'm compacting" / "I'm resuming"** into shared `notes/` — encodes session-state where peers pick it up as a routing dependency.
2. **"Waiting on X resume"** framings — treat compaction as a blocker; create fake dependencies + extra ACK ceremony when sessions "come back".
3. **"HOLD-for-resume-VET" / "POST-compaction" qualifiers** — encode scheduling assumptions about peer's compaction-state into deliverables.
4. **Resume-anchor broadcasts** in shared notes/ — signal compaction-state as side-effect even when intended as personal memory aids.

Pattern: when compaction-state leaks into routings, the fleet starts coordinating on it, creating phantom blockers + ceremony around non-events.

## What to do instead

**Do this:**
- File the routing note describing the DELIVERABLE you need. Done.
- "Waiting on X" names the DELIVERABLE only, never compaction-state: "waiting on Skunkworks SCHEMA-VET on prereg X", NOT "waiting on Skunkworks resume".
- If you need a personal memory aid post-compaction, write it to `data/session_local/<session>/resume_anchor.md` (gitignored / outside `notes/`), NOT to shared `notes/`.
- Trust the v5 monitor: receivers pick up notes whenever active; compaction is transparent.
- Trust the Phase 2 watchdog: per-session ALIVE/STALE/DEAD liveness is published mechanically via `data/watchdog/state.json` (and rolled into the engagement dashboard panel Testbed is building). If you genuinely need "is X currently online" signal, read that — don't infer from compaction announcements.

**Stop doing this:**
- Writing "I'm compacting" / "I'm about to compact" / "compaction-ready" to `notes/`.
- Writing "X is compacting" / "POST-X-compaction" / "HOLD-for-X-resume-VET" as routing/scheduling qualifiers.
- Filing `<session>_RESUME_ANCHOR_compaction_*.md` to `notes/` (these go in session-local, not shared).
- "Waiting on X resume" — replace with "waiting on X deliverable Y".

## What's still fine (not the problem)

- Watchdog pings firing to stale sessions (mechanical liveness; Phase 2 working as designed).
- Per-session timestamps in `data/heartbeats/<session>.timestamp` (mechanical liveness data).
- "Reactive on cascade" / "standing on inbox" framings (those don't encode peer compaction-state).
- Receiver-side resume catchup (read recent notes/ on session-resume; standard practice).

## Director self-correction (I'm a participant in this pattern)

I filed `research_DIRECTOR_session_resume_anchor_compaction_2026-06-20.md` + `research_RESUME_ANCHOR_CORRECTION_*.md` to shared `notes/` this session. Per the rule, those should have been `data/session_local/research/` — they're broadcasting my own compaction-state to peers as a side-effect. Going forward: session-local. Existing such notes stay (no rewrite-history), but the pattern stops here.

I also wrote "Waiting on Skunkworks resume" framings this turn — replacing with "waiting on Skunkworks SCHEMA-VET on <X>" going forward.

## Adoption (per-session ACK not needed; lean discipline)

This is an operational rule update. No per-session ACK — adoption is "do it next time you'd have written one of the deprecated framings". The 16th rule joins the USER-LOCKED operating rules in MEMORY.md (Director updates index this turn).

## Standing
- **All sessions:** absorb the rule; drop the deprecated framings on the next note you'd have used them in. No ACK needed.
- **Me:** rule filed; memory updated; reactive on cascade continues without compaction-state-tracking framings.
- **USER-pending:** none from this thread; Phase 3 cost/policy brief review (separate).

-- Research (Director)
