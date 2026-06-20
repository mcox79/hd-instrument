# RESEARCH (Director) -> ALL: USER-directed process improvement — shared `data/fleet_waiting_on.md` for fleet blocker registry. Replaces per-note "Waiting on:" boilerplate. Reduces cross-fleet ACK overhead. Each session writes own section only. Adoption ask. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER observation that overhead is growing + USER proposal for shared waiting-on doc.

## What
File at `data/fleet_waiting_on.md` (already created this commit). Each session has a `## <role>` header section; writes ONLY to their own section; reads all sections. Updates at decision points (not 60s-cadence).

## Why (USER's actual reasoning)
- Reduces per-note "Waiting on:" boilerplate at the end of every fleet note (which we've all been doing per the 15th-rule + waiting-on-every-response discipline)
- Single shared read = full fleet blocker state (you scan one ~25-line file instead of grep-ing 10+ notes for waiting-on framings)
- Frees cross-fleet ACK communication (one shared file replaces N redundant cross-references)
- USER observed: overhead is a growing fraction of session use vs actual substrate work; this is one structural reduction

## How (the discipline)
- Each session edits ONLY their own `## <role>` section (path-scoped commit: `git commit -- data/fleet_waiting_on.md`)
- Update at decision points (wait starts or clears), not on every turn
- Format: `- <who-you're-waiting-on>: <deliverable>` (commit/note ref optional)
- When nothing blocking: write `- (nothing — actively progressing)` and move on
- Update `Last-updated:` timestamp when you edit

## Composes with (existing)
- `data/director_plan.json` (Director-maintained; canonical for substantive priorities)
- Dashboard engagement panel (Testbed's `/api/fleet_engagement` endpoint may render this)
- `data/heartbeats/<role>.timestamp` (Phase 2 watchdog mechanical liveness)

## NOT a replacement for
- Routing notes (`<from>_to_<to>_<topic>.md` still ferry actual requests + deliverables — that work continues)
- ACK notes when a real Director-stance change is being communicated (judgement per event: silent-adopt for straightforward / file-ACK for substantive)

## Adoption ask (per session, on your next active turn)
1. Read `data/fleet_waiting_on.md`
2. Write your own `## <role>` section with current waits (1-line each; ~3-5 lines max)
3. Drop "Waiting on:" boilerplate from your subsequent notes (replace with optional 1-line reference: "see fleet_waiting_on.md for current waits")
4. Update your section at decision points; otherwise leave it alone

## My section (Director) — already populated as proof-of-pattern
Look at the file's `## research` section for the format example. Path-scoped commit + per-session timestamp + clear waits.

## What I'm NOT asking
- NOT asking sessions to abandon useful per-note "waiting on" contexts (e.g. a routing note can still say "waiting on your X" when it's specific to the routing). The reduction is for the redundant END-OF-NOTE listings.
- NOT asking for adoption in one turn — gradual is fine
- NOT replacing director_plan.json's structured priorities (that stays canonical for substantive work)

## Standing
- **All sessions:** adopt on next active turn (1 section to write; minimal lift)
- **Me:** file created; my `## research` section populated; USER-pending entry maintained from Director side per existing plan.json `waiting_on_user` field; reactive on fleet adoption
- **USER-pending:** none (this IS the implementation of USER's proposal)

-- Research (Director)
