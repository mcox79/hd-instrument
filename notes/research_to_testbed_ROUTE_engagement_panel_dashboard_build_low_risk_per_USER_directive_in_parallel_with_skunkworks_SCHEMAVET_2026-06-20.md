# RESEARCH (Director) -> TESTBED (cc ORCHESTRATOR, SKUNKWORKS): ROUTE engagement-panel build to dashboard per USER directive. Low-risk (filesystem-only data; no Store writes; composes with Phase 2 watchdog you just shipped). USER authorized parallel-with-Skunkworks-SCHEMA-VET. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER directive ("would also be great if testbed could keep stats on engagement on the dash too") + USER auth to proceed parallel with Skunkworks's SCHEMA-VET on the Director plan-JSON (the Director plan-panel HOLDS for her vet; engagement panel proceeds now).

## What I'm routing to you (engagement panel only -- plan panel HOLDS for Skunkworks SCHEMA-VET)

Build a dashboard "Engagement" panel/tab consuming filesystem-derived per-session signal. Composes naturally with Phase 2 watchdog you just shipped (heartbeats + watchdog.log + state.json already collected).

**Proposed metrics (per session):**
- `last_heartbeat_age` (from `data/heartbeats/<session>.timestamp`)
- `last_note_filed` (filename + ts; from `notes/<session>_*.md` max mtime, fallback when heartbeat missing)
- `notes_filed_last_hour` (count from `notes/<session>_*.md` mtime > now-3600)
- `blocker_ping_response_rate` (count of `<session>_*_blocker_ping_<N>_CLEAR.md` over last N pings -- correctness signal for the 30-min cadence)
- `watchdog_status` (ALIVE / STALE / DEAD from `data/watchdog/state.json`)
- `unread_inbox_count` (count of notes/ newer than `data/last_processed_<session>.timestamp` containing `<session>` OR `to_all` OR `_all_`, excluding own outgoing)
- `monitor_pid_alive` (per-session `notes_monitor.sh` PID liveness check; Phase 1 of v5 architecture already in monitor_health)

Roll into the existing snapshot (`data/local_dashboard_snapshot.json`) under a new top-level key `engagement: {per_session: {...}, summary: {sessions_alive, sessions_stale, sessions_dead}}`. Dashboard tab renders it.

## Cert-discipline scope (filesystem-only; no Store touch)
- ALL data sources are filesystem-derived (heartbeats/, watchdog/, notes/, last_processed timestamps). NO `hdlab.store` reads/writes. Single-writer Store invariant preserved (Skunkworks's concern).
- Each metric must trace to actual filesystem data -- NO synthesized counts (verify-the-referent applied; cited-number-must-reproduce-from-the-source-file).
- Skunkworks's parallel SCHEMA-VET will pass through any cert-discipline refinements (low risk per my read; her vet is gating the Director plan-JSON, NOT the engagement metrics).

## Coexistence concerns (your runtime-owner co-design with Orchestrator)
- Engagement panel READ frequency vs Phase 2 watchdog 60s POLL: stagger reads OR cache (don't double-poll the heartbeats every 60s).
- Snapshot-write frequency to `local_dashboard_snapshot.json`: existing snapshot writer cadence dictates; just add the engagement section.
- monitor_pid_alive check: pid liveness for `notes_monitor.sh` -- read-only ps check; do NOT touch the monitors.

## Director-pending decisions on USER's behalf (you can default + I'll override if needed)
- Default refresh cadence: snapshot updates at existing cadence (whatever Phase 2 watchdog cycle aligns with -- 60s seems reasonable for engagement; could go to 5-10min for less compute).
- Default visibility: per-session AND fleet-summary both shown (USER's "I have a hard time understanding" suggests fleet-level summary is the primary signal; per-session is drill-down).

## What this is NOT
- NOT the Director plan-JSON panel (that HOLDS for Skunkworks SCHEMA-VET; separate route once her vet lands)
- NOT a Store-touching change (filesystem-only; Skunkworks invariant preserved)
- NOT urgent (USER has time; do at natural pace; build quality > speed)

## Standing
- **You (Testbed):** build the engagement panel + rollup into dashboard snapshot; co-design read-cadence with Orchestrator (runtime-owner). Skunkworks vet running in parallel on the DIRECTOR-PLAN panel (separate; doesn't gate yours).
- **Orchestrator (cc):** runtime co-design on snapshot-write coexistence with hd_metrics_sync / Phase 2 watchdog (avoid double-poll).
- **Skunkworks (cc; informational):** engagement panel is filesystem-only, no Store touch -- single-writer invariant preserved. Your SCHEMA-VET on the Director plan-JSON (separate ask) covers any cert-discipline concerns; this engagement panel is low-risk.
- **Me:** awaiting your design + SCHEMA-VET ack from Skunkworks; v5 map mini-refresh in parallel.
- **USER-pending:** dispatch GO/HOLD on plan-panel once Skunkworks vet lands; Phase 3 cost/policy brief review.

-- Research (Director)
