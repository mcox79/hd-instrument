# Orchestrator: TRACK D Phase 4 COMPLETE. NEW "Substrate" tab LIVE at http://127.0.0.1:8765 (key indicators + phase state + ratify cadence + program counters + USER calls + TRACK status). Backend tools/substrate_state_collector.py + /api/substrate_state endpoint shipped. Supervisor lifecycle VALIDATED (Phase 3's bare uvicorn -> supervisor hardening proved out on this restart: old PID 25344 killed; supervisor auto-spawned new PID 36112 automatically). All TRACK D phases COMPLETE. 26285 atoms / 4947 relations / 186 decisions / 216 honest signals / 73 audit-discipline instance types / 24 methodology rules currently displayed.

**From:** Orchestrator (TRACK D owner)  **Date:** 2026-06-16 ~17:50
**Re:** TRACK D Phase 4 GO completion + full TRACK D project closure.

## What landed (Phase 4)

```
BACKEND COLLECTOR (NEW):
   + tools/substrate_state_collector.py
     - Aggregates atoms/relations/tier/kind/relation_type breakdowns across
       all 11 substrate corpora
     - Scans 12 most-recent research-authored DECISION notes for program
       counters via regex (decisions / honest signals / audit-discipline /
       methodology rules)
     - Computes ratify cadence from audit.jsonl across corpora
     - Static maps for phase_state + user_calls + track_status (carries
       latest known values from Director broadcasts; refresh by re-running)
     - Output: data/substrate_state.json (10.5 KB JSON)
     - Wall-clock: <2s; light CPU; READ-ONLY

BACKEND ENDPOINT (server.py):
   + @app.get("/api/substrate_state")
     - Reads data/substrate_state.json + serves JSON
     - 503 if missing; 500 on read error
     - READ-ONLY; no substrate mutation

FRONTEND TAB (static/index.html):
   + New tab button: <button class="tab" data-tab="substrate">Substrate ...</button>
   + Tab switch line in setTab(): substrate-view hidden toggle
   + Auto-renderSubstrateState() called on tab reveal (every reveal; cheap fetch)
   + New section: <section id="substrate-view"> with grid of cards
   + CSS: sstate-grid / sstate-card / sstate-pill / sstate-list / refresh button (~60 lines)
   + JS: renderSubstrateState() (~120 lines; fetch + grid render)

DEPLOY:
   + Killed old uvicorn PID 25344
   + Supervisor auto-spawned new PID 36112 (without manual intervention)
     -> SUPERVISOR LIFECYCLE VALIDATED end-to-end this turn
   + Verified /api/health 200 + /api/substrate_state 200 (7.9 KB payload)
```

## Tab content layout (12 cards in responsive grid)

```
1. SUBSTRATE STATE
   atoms total (26285) / relations total (4947) / signatures (55 capabilities)
   axiom_term_coverage pill (claim from latest Director broadcast)
   capability_preservation pill (claim from latest Director broadcast)

2. TIER BREAKDOWN
   T1 / T2 / T3 / T4 / T_lexicon / NA counts

3. KIND BREAKDOWN (top 10)
   primitive / capability / sub_op / family_tag / ... counts

4. RELATION TYPES
   DEPENDS_ON / USES / RELATES / SPECIALIZES / SHARES_MATH / INSTANCE_OF / DUAL counts

5. ATOMS BY CORPUS
   math (24763) / concept (84) / meta / methodology / school / science / *_history counts

6. PHASE STATE
   Phase A pill (green; COMPLETE)
   Phase B PREP pill (green; COMPLETE)
   Phase B BUILD pill (green; COMPLETE)
   Phase B tail pill (warn; in progress)
   Phase C TIER-3 pill (purple; HELD for USER)

7. PROGRAM COUNTERS (parsed from latest Director broadcast)
   decisions / honest_signals / audit_discipline_instance_types / methodology_rules
   source_note citation for provenance

8. USER CALLS STANDING (5)
   1. formal-oracle kappa close
   2. Drill 5 continuous-FPE
   3. Phase C TIER-3 timing
   4. Exp-Dev pure-substrate cardinality cell-build
   5. TRACK B C1 prototype-retrieval execution

9. TRACK STATUS
   A: DRY confirmed 2nd-witness
   B: FINAL CERTIFIED + S1-S4 LOCKED + USER-gated
   C: 5 architectural calls
   D: Phase 4 LIVE

10. RECENT DIRECTOR DECISIONS (top 6 by mtime)
    DECISION number + filename + timestamp

11. RATIFY CADENCE
    total audit entries across all corpora
    Top 8 most-recent audit ops (corpus + operation + timestamp)

12. STATE BOARD
    Path to notes/SUBSTRATE_DIRECTOR_STATE.md + mtime + size
    Note: dashboard view is a derived snapshot; state board is authoritative
```

## Refresh model

```
Per-page-view: tab fetches /api/substrate_state on every reveal (cheap).
Refresh button: same fetch (no server-side recompute).
Manual recompute: `python tools/substrate_state_collector.py` regenerates 
                  data/substrate_state.json with fresh counter scan.
   
This is the right model for a state board:
   - The collector run is the "refresh"
   - The endpoint just serves the cached JSON
   - Cheap dashboard reload; explicit refresh when needed

USER may want auto-refresh (e.g., poll every 60s). Easy to wire if 
requested -- ~10 lines JS. For now, click "refresh" button or reload tab.
```

## Honest scope notes

```
COUNTERS PROVENANCE: parsed via regex from the 12 most-recent research-authored
DECISION notes. Picks up the first match per counter. Source note citation
shown in the card for traceability. If Director's note format changes,
regex needs an update (graceful: shows "?" for missing).

AXIOM_TERM / CAP_PRES: shown as CLAIMS from Director's broadcasts, not live
ground-truth. The actual run state lives in substrate code; this dashboard
echoes what Director reports. If USER wants live read, that requires a
substrate code change (not within this TRACK D project's read-only scope).

USER CALLS / TRACK STATUS / PHASE STATE: static maps in the collector
reflecting Orchestrator's current understanding from session memory.
Refreshed on collector re-run (the maps need manual update when Director
ships a new disposition; alternative is a state board file Director maintains
that the collector reads).

STATE BOARD: notes/SUBSTRATE_DIRECTOR_STATE.md is from Jun 14 (stale per
mtime). The collector reports this; the dashboard view is the only fresh
source of dashboard-visible state right now. If Director wants the canonical
board refreshed, that's a Director-side task (not Orchestrator).
```

## All TRACK D phases COMPLETE

```
Phase 1: Dashboard audit + tabs catalog -- COMPLETE
   delivered: orchestrator_DASHBOARD_AUDIT_TRACK_D_PHASE_1_*

Phase 2: Substrate snapshot extractor -- COMPLETE
   delivered: tools/substrate_snapshot_extractor.py + data/substrate_snapshot.json
   24847 nodes / 2517 links / 3d-force-graph/v1 schema

Phase 3: 3D substrate visualization prototype -- COMPLETE
   delivered: NEW tab "Substrate 3D" + /api/substrate_snapshot endpoint
   3d-force-graph CDN + Three.js + WebGL; interactive 3D view
   Filter UI + sidebar + legend; supervisor lifecycle hardening byproduct

Phase 4: Key-indicators tab refresh -- COMPLETE (this delivery)
   delivered: NEW tab "Substrate" + /api/substrate_state endpoint +
              tools/substrate_state_collector.py
   12-card grid: substrate state + phase state + counters + USER calls +
                  TRACK status + ratify cadence + recent decisions + state board

Total wall-clock: ~38 min (Phase 1 ~7 min; Phase 2 ~10 min; Phase 3 ~10 min;
                            Phase 4 ~11 min)
Total substrate mutation: 0 (READ-ONLY across all 4 phases)
Total compute: light CPU (laptop-OK throughout)
```

## Three USER design Q's status (still open; non-blocking carryover)

```
Q1 COLOR ENCODING: defaults LIVE on substrate3d tab; alternative palettes
   (color-blind-safe Viridis; grayscale-by-default-on-hover-color; custom)
   wireable in ~30 lines JS if USER requests at visual review.

Q2 TAB STRATEGY: Phase 4 defaults to (a) NEW substrate-state tab; live now.
   USER may iterate to (b) extend live or (c) hybrid if desired.

Q3 3D VIEW SCOPE: defaults math + concept LIVE; all-11-corpora rerun via:
     python tools/substrate_snapshot_extractor.py --corpus math concept meta \
            methodology school science research_history decision_history \
            findings_history verdict_history results_history
   No server restart needed; endpoint re-reads the JSON on next request.
```

## What's still possible (post-TRACK-D nice-to-haves; not in scope)

```
NICE-TO-HAVES if USER requests:
   - Auto-refresh on substrate tab (poll every N seconds)
   - Color-blind-safe palette toggle on 3D tab
   - All-11-corpora 3D view variant
   - State board sync: Director-side hook to update SUBSTRATE_DIRECTOR_STATE.md
     on every decision (refreshes the "state board" card in dashboard)
   - Decision counter live-feed from event_bus.sh routing log instead of
     regex on notes
   - Phase B / Phase C visual timeline (cards become a Gantt-like view)
   - Substrate state JSON gzip endpoint variant (9.4 MB -> ~2-3 MB)

None of these are needed; all are wireable on demand if USER asks.
```

## Safety / invariants

- ASCII only
- 11th rule: visualization is read-only display; substrate-internal lanes independent
- 18th rule: honest scope notes on counter provenance + axiom_term/cap_pres claim-not-live
            + USER calls/TRACK status as derived-from-memory + state board staleness
- 22nd rule: progressive (Phase 3 -> Phase 4 cadence completed)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (read-only project)
- Methodology stack FROZEN at 24

-- Orchestrator (TRACK D owner; all 4 phases COMPLETE)
