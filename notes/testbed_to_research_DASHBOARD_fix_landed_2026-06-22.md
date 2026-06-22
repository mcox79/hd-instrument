# TESTBED -> RESEARCH: DASHBOARD HEALTH FIX LANDED

## TL;DR

Applied per `testbed_to_research_DASHBOARD_simplest_fix_report_2026-06-22.md`. Health endpoint now returns HTTP 200 in 0.5s warm (15.4s cold from Store load).

## Verification result

- **HTTP 200 in 0.503131s** (warm cache, second hit)
- **HTTP 200 in 15.372035s** (cold start, first hit after restart — Store load of 177k atoms via DuckDB+torch)
- All other endpoints verified working alongside (snapshot 0.2s, director_plan 0.2s)

## Changes (single commit, path-scoped: `tools/dashboard/server.py` only)

Commit `3baa3975` — TWO bugs fixed, not one:

1. **D3 plan-stall git log cache** (the report's prescribed fix): subprocess git log was called inside per-priority loop; cached once outside. Eliminates redundant N*~3s calls.

2. **D6 idle-without-reason KeyError** (pre-existing bug surfaced during verify): setdefault keyed `waiting_lines` but append path used `f"{current_sub}_lines"` with current_sub == `waiting_on` → KeyError on every role with a `### Waiting on` subsection. Renamed dict key to `waiting_on_lines` to match the sub-name convention. This was the actual cause of the HTTP 500 (the 8s timeout was only the cold-start manifestation).

Without fix #2 alone, the endpoint would still 500. Applied under the Testbed pre-authorized infra refinements (USER 2026-06-21).

## Restart mechanics note (for the dashboard infra)

The first `schtasks /End /TN hd_dashboard ; Start-Sleep 2 ; schtasks /Run /TN hd_dashboard` sequence reported SUCCESS but the listening process (a pythonw.exe started 7:36) survived. Last-Run-Time updated but the spawned child wasn't killed. Had to `Stop-Process -Id <listener>` directly then `schtasks /Run`. The Task's "End" semantics don't reliably reach the spawned uvicorn child on this setup. Not blocking, but worth noting if future restarts look like no-ops.

## Phase 4 follow-ups from the original report

Not addressed (deferred per the report's "NOT URGENT" note): D5/D6 false-RED under Agent Teams architecture, Live tab cosmetic, Cycle history panel retirement. Punt to a future "Phase 4 dashboard cleanup" cycle.

— Testbed (Integrator), Agent Teams teammate spawn
