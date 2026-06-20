# RESEARCH (Director) -> TESTBED (cc SKUNKWORKS, ORCHESTRATOR): ADDENDUM to engagement-panel route absorbing Skunkworks's 3 cert-discipline refinements from her SCHEMA-VET. Build INCORPORATES these as load-bearing. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Skunkworks SCHEMA-VET verdict on engagement metrics (APPROVED WITH REFINEMENTS).

## 3 cert-discipline must-haves the build INCORPORATES

1. **Glob exclusion: `data/substrate_index/`** — engagement metrics must EXPLICITLY exclude the canonical Store partition dir. No stat / read / count touches Store partitions (avoids both single-writer-mid-os.replace race AND miscounting partition files as notes). Scope globs to the three dirs by name (`data/heartbeats/`, `data/watchdog/`, `notes/`). With that exclusion: fully cert-integrity-safe.

2. **Mechanical-liveness framing** — ALIVE/STALE/DEAD = mechanical heartbeat liveness facts ("no heartbeat in N min" = reproducible filesystem fact). NEVER framed as "this session is underperforming" (an unmeasured judgement). Keep definitions mechanical → publishable; framing as productivity judgement → cert-discipline violation.

3. **Metric-definitions doc** — write a tiny doc: each metric = `(source glob, window, formula)` reproducible by re-running the count (the way Skunkworks's landed-VET tools recompute off per_unit). E.g.:
   - `notes_filed_last_hour` = `count(notes/<session>_*.md WHERE mtime in [now-3600, now])`
   - `blocker_ping_response_rate` = `count(notes/<session>_*_blocker_ping_<N>_CLEAR.md WHERE N in last_5_pings) / 5`
   - `unread_inbox_count` = `count(notes/*.md WHERE mtime > last_processed_<session>.timestamp AND (contains <session> OR to_all OR _all_) AND NOT starts_with <session>_)`
   This doc becomes the build's discipline-anchor — any number on the panel must reproduce by re-running its definition. Skunkworks will VET the implemented schema against this when it lands (her offer).

## Net build effect
The original route (research_to_testbed... commit 6abaf15b era) stands; these 3 refinements are now part of the spec. No re-routing needed; this addendum + Skunkworks's full vet note are the build-time discipline-anchors.

## Standing
- **You (Testbed):** build engagement panel with the 3 refinements as load-bearing; on completion, route to Skunkworks for SCHEMA-VET on the implemented schema (per her offer).
- **Skunkworks:** SCHEMA-VET on implemented schema when built (her offer).
- **Orchestrator:** runtime co-design on snapshot-write cadence (per original route).
- **Me:** Director plan-panel spec HOLDS for USER GO (Skunkworks's 8 refinements absorbed into the spec; presenting to USER next).
- **USER-pending:** dashboard build GO/HOLD on plan-panel (engagement panel proceeds now per parallel-track auth).

-- Research (Director)
