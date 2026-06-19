# Research (Director) -> Orchestrator: DASHBOARD + 3D SUBSTRATE VISUALIZATION PROJECT BRIEF (TRACK D; USER-initiated 2026-06-16 ~17:18; DECISION 187c). Substrate has 26285 atoms / 5189 relations / 115 signatures / 207-of-207 axiom term coverage -- well within standard 3D graph visualization bounds (3d-force-graph / Three.js / plotly handle 10k-100k nodes interactively). 4-phase project, light first (Phase 1 audit before building). Parallel with substrate-internal lanes; NO impact on cap_pres / axiom-term / methodology invariants.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~17:23
**Re:** USER ASK: "new tab showing current construction of the substrate with key indicators and progress, as well as a representation? Can we see a picture of the substrate in 3d?" + "great project for orchestration to take on" + "do some research on this"

## Director research summary on FEASIBILITY (3D substrate visualization)

```
SUBSTRATE SCALE:
   26285 atoms; 5189 relations; 115 signatures; 207-of-207 axiom term coverage
   Average atom degree ~0.39 relations/atom (sparse; clusters likely visible)

STANDARD 3D GRAPH VIZ STACK (proven for this scale):

   3d-force-graph (https://github.com/vasturiano/3d-force-graph)
      Three.js + WebGL based. Handles 10k-100k nodes interactively.
      Force-directed layout reveals natural topology (clusters emerge).
      Color/size by node attribute; click/hover for atom detail.
      React + vanilla JS versions. THIS IS THE NATURAL CHOICE.

   Plotly Scatter3d
      Python-friendly; good for static or notebook snapshots; networkx
      layouts feedable. Less interactive but easier to embed.

   deck.gl
      Highest perf (100k+); steeper learning curve. Overkill for 26k.

   PyVis / Cytoscape.js
      Primarily 2D; less natural for this ask.

RECOMMENDATION: 3d-force-graph for the new dashboard tab; plotly as a
   fallback if the dashboard is Python/Streamlit/Dash-based.

ENCODING DESIGN (color + size + filter):
   Color by atom type or tier:
      T1 (atomic ops): cool blue
      T2 (composite primitives): teal
      T3 (composite operators): green
      T4-T7 (higher tier): yellow -> orange -> red gradient
      concept (capabilities, signatures): bright purple
      CAP (load-bearing capabilities): bright magenta
   Size by degree (more relations = bigger node) OR by flagship status
      (ratified + flagship = largest; QUALIFIED + filed = medium;
      authored = small).
   Edge color by relation type:
      USES (capability uses operator): solid blue
      DEPENDS_ON (operator depends on primitive): solid green
      INSTANCE_OF (subtype/instance): solid orange
      DUAL (inverse pair): solid red
      RELATES (general): thin gray
      SHARES_MATH (cross-domain bridge): thin purple
   Filter UI:
      filter by tier (T1-T7 / concept / CAP)
      filter by ratify status (load-bearing / QUALIFIED / authored / DROPPED)
      text search by atom name
      collapse low-degree atoms (visual decongestion)

PERFORMANCE: 3d-force-graph at N=26k with edge subsampling settles in
   <5s; interactive rotation/zoom @60fps modern laptop. No backend
   re-render needed.

NOVEL BUT NOT EXPERIMENTAL: this is well-explored knowledge-graph viz
   territory; the value-add is the SUBSTRATE-SPECIFIC encoding choices
   (tier color scheme; ratify-status size encoding; relation-type edge
   coloring; flagship/load-bearing highlighting).
```

## Project scope (4 phases; sequential)

```
PHASE 1 -- DASHBOARD AUDIT + TABS CATALOG (LIGHT; pure-discovery)
   Output: notes/orchestrator_DASHBOARD_AUDIT_*.md
   Tasks:
     - catalog current dashboard tabs + technologies (Streamlit? Dash? Custom HTML?)
     - identify dashboard refresh cadence + data sources currently consumed
     - identify what tab would need to be added (new vs replacing stale tab)
     - identify what "key indicators" + "progress" the USER likely wants
       (atoms + relations + axiom term + cap_pres + ratifies + decisions
       + honest signals + audit-discipline candidates + USER calls standing
       + methodology rules + scorecard state)
   Deliverable: SHORT memo (1-2 pages) + recommended next-phase scope.
   Cadence: ~1 cycle (light); NO substrate touch.

PHASE 2 -- SUBSTRATE SNAPSHOT EXTRACTOR (LIGHT; pure-extraction)
   Output: tools/substrate_snapshot_extractor.py + data/substrate_snapshot.json
   Tasks:
     - read-only FHRR store query: dump atoms (name + tier + type + metadata)
     - read-only relations dump (src + dst + relation_type + metadata)
     - compute degree per atom + cluster heuristic (optional)
     - output JSON in 3d-force-graph format:
         { "nodes": [{ "id", "label", "tier", "type", "ratify_status", "degree", ... }],
           "links": [{ "source", "target", "type", ... }] }
     - light filter knobs (min_degree, tier_set, type_set) for downstream UI
     - refreshable on demand (no caching dependency)
   Cadence: ~1-2 cycles; LIGHT compute; NO heavy ops.

PHASE 3 -- 3D SUBSTRATE VISUALIZATION PROTOTYPE (web tab)
   Output: dashboard/tabs/substrate_3d.html (or framework-equivalent)
   Tasks:
     - 3d-force-graph integration consuming substrate_snapshot.json
     - tier color scheme + ratify-status size encoding + relation-type edges
     - filter UI (tier checkboxes; type filter; text search; min-degree slider)
     - hover/click reveals atom metadata in side panel
     - load-bearing CAPS highlighted; QUALIFIED findings distinguished
     - performance budget: 60fps on modern laptop @ N <=26k atoms with
       reasonable edge subsampling
   Cadence: ~2-3 cycles; web-tech only; NO substrate compute impact.

PHASE 4 -- KEY-INDICATORS TAB REFRESH (parallel with Phase 3)
   Output: dashboard/tabs/substrate_state.html (or refresh existing)
   Tasks:
     - live indicators block (refresh from heartbeats + scorecard):
         atoms / relations / signatures / axiom term coverage
         capability_preservation invariant
         load-bearing capabilities count (per phase)
         QUALIFIED findings filed
         ratify cadence (last N ratifies + timestamps)
         USER architectural calls standing (5 currently)
         cumulative decisions + honest signals + audit-discipline candidates
         methodology rules count (FROZEN at 24)
     - phase status block (Phase A / B PREP / B BUILD / B tail / C TIER-3)
     - last 5-10 phase-boundary decisions summarized
   Cadence: ~1-2 cycles; pure-extraction + simple rendering.

TOTAL: ~5-8 cycles depending on dashboard infra discovered in Phase 1.
   Light first; web-tech; substrate-internal invariants UNTOUCHED.
```

## Resource policy

```
Compute: LIGHT throughout. No remote-desktop GPU required.
USER policy: 18th-rule refuses to heavy-compute speculative work; this entire project
   is on-laptop / browser-rendered. No conflict with substrate-internal compute lanes.
Substrate touch: READ-ONLY only. NO atom mutation. NO relation mutation. cap_pres=1.0
   + axiom-term + methodology FROZEN preserved trivially.
Cadence: USER-input may come at any time on visual design choices (tier color scheme,
   filter UI, indicators selection); Orchestrator surfaces design Q's to USER as they
   arise; otherwise proceeds with sensible defaults per this brief.
```

## Key indicators (recommended initial list for Phase 4)

```
SUBSTRATE STATE:
   atoms total + breakdown by tier (T1/T2/T3/T4/T5/T6/T7/concept/CAP)
   relations total + breakdown by relation_type (USES/DEPENDS_ON/INSTANCE_OF/DUAL/RELATES/SHARES_MATH)
   signatures count (115 currently)
   axiom term coverage (207-of-207 currently)
   capability_preservation (1.0 currently; HARD invariant)

PHASE STATE:
   Phase A consolidation: COMPLETE (13 atoms ratified)
   Phase B PREP: COMPLETE
   Phase B BUILD: COMPLETE (5 atoms ratified + 1 QUALIFIED filed)
   Phase B tail: IN PROGRESS (2 ledger-hygiene filings going)
   Phase C TIER-3: HELD for USER architectural decision

RATIFY CADENCE:
   last 5-10 ratifies with timestamps
   ratify rate over rolling window
   total load-bearing capabilities (Phase A + Phase B + ...)

USER FACING:
   architectural calls standing (5 currently; named list)
   cumulative decisions (187 currently)
   cumulative honest signals (218 my-count / ~220 cross-session)
   audit-discipline instance types (74 currently; 44 confirmed + 30 candidates)
   methodology rules (FROZEN at 24)

PROGRESS:
   ratifies last 24h
   FORM-A backlog remaining (7 currently; runway FIRMED thin)
   TRACK A / TRACK B / TRACK C / TRACK D status
```

## Orchestrator START INSTRUCTION

```
PHASE 1 ONLY for now -- dashboard audit + tabs catalog. Don't build until audit memo
lands and Director approves Phase 2 scope. Keep Phase 1 SHORT (1-2 pages). Surface
design Q's to Director or USER as they arise. Light cadence.

USER can iterate on tier color scheme + filter UI design + key-indicators selection
as Phase 2/3/4 progress. Treat USER as design-input source; Director as cadence-setter.
```

## Safety / invariants

- ASCII only
- 11th rule: no LLM in substrate authoring loop; visualization is read-only display
- 18th rule: light cadence; no heavy compute commitment without USER GO
- substrate state invariants UNTOUCHED (read-only project)
- methodology FROZEN at 24 (no new rules from infra work)

---

**Orchestrator:** Phase 1 dashboard audit + tabs catalog GO. Light cadence. Output
short memo + recommended Phase 2 scope. Substrate touch: READ-ONLY only.
**USER:** Brief addresses your dashboard ask substantively. Phase 1 lands first as
audit memo; you'll have input on visual design as Phase 2/3/4 progress. No substrate-
internal impact; parallel with TRACK A / TRACK B / TRACK C lanes.

Tag: DASHBOARD_3D_SUBSTRATE_BRIEF_PROJECT_DISPATCHED_orchestrator_phase_1_audit_first -- Research (Director)
