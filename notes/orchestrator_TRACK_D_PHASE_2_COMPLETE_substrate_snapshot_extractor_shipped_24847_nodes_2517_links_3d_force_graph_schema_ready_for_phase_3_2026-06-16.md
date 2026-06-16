# Orchestrator: TRACK D Phase 2 COMPLETE. substrate_snapshot_extractor.py shipped + data/substrate_snapshot.json generated (math + concept per DECISION 187c Q3 default). 24847 nodes / 2517 links / 14 MB. Schema 3d-force-graph/v1. Light CPU (<5s). Ready for Phase 3 visualization prototype. 1 honest scope note + 1 USER design Q-update.

**From:** Orchestrator (TRACK D owner)  **Date:** 2026-06-16 ~17:35
**Re:** TRACK D Phase 2 GO completion.

## Phase 2 deliverables shipped

```
TOOL:     tools/substrate_snapshot_extractor.py (NEW)
OUTPUT:   data/substrate_snapshot.json (NEW; 14 MB)

CLI:
  default:   python tools/substrate_snapshot_extractor.py
             (math + concept; all tiers; all kinds; min_degree=0)
  filtered:  python tools/substrate_snapshot_extractor.py --corpus math --tier T1 T2 T3 \
                  --min-degree 1 --output data/substrate_snapshot_filtered.json

WALL-CLOCK: <5 sec (json-decode bound)
COMPUTE:    light CPU (laptop OK per USER thermal policy)
SUBSTRATE TOUCH: READ-ONLY (cap_pres + axiom-term + methodology FROZEN untouched)
```

## Snapshot summary (current run; math + concept)

```
NODE COUNT: 24847
   tier breakdown:
      T1 (foundational primitives):    244
      T2 (composite primitives):     19,067   <-- dominant
      T3 (composite operators):       5,515
      T4 (rare higher):                   2
      T_lexicon:                         18
      NA:                                 1
   kind breakdown:
      primitive:    24,625
      sub_op:           121
      capability:        55   <-- concept-corpus CAPs
      family_tag:        15
      lexicon:           18
      mwp_schema:         6
      macro:              2

LINK COUNT: 2,517
   type breakdown:
      DEPENDS_ON:   1,951
      USES:           212
      RELATES:        116
      SPECIALIZES:    111
      SHARES_MATH:     63
      INSTANCE_OF:     20

SCHEMA: 3d-force-graph/v1
   { "nodes": [{ "id", "label", "corpus", "tier", "kind", "degree",
                 "ratify_status", "serves_capability", "current_best_solution",
                 "metadata_summary" }],
     "links": [{ "source", "target", "type", "metadata" }] }
```

## Honest scope note

```
Director's brief cited 26285 atoms / 5189 relations as substrate total.
Math + concept (per Q3 default) gives 24847 atoms / 2517 links -- the
substrate's SCIENTIFIC CORE.

The remaining ~1440 atoms + ~2670 relations live in the other 9 corpora
(meta + research_history + decision_history + findings_history +
 verdict_history + results_history + methodology + school + science).

If USER chooses Q3 option (c) ALL 11 CORPORA at Phase 3 visual review,
re-running with --corpus math concept meta research_history decision_history
findings_history verdict_history results_history methodology school science
yields the full picture. Trivial CLI change; light CPU.

For now: math + concept gives the cleanest load-bearing substrate +
capabilities view that USES it (Director-recommended; matches Q3 default).
```

## USER design Q update (Q1 / Q2 / Q3 still open; Phase 2 used defaults)

```
Q1 (color encoding): defaults remain Director-recommended; Phase 3 will render
   with T1 blue -> T7 red gradient + concept purple + CAP magenta.
   USER input affects Phase 3 (visual). Non-blocking.

Q2 (tab strategy for key indicators): Phase 4 awaiting; (a) NEW substrate tab
   is Director default. USER input affects Phase 4. Non-blocking.

Q3 (3D scope): Phase 2 used (b) math + concept default. USER input affects
   Phase 3 visual + can be re-run instantly via CLI corpus arg if changed.

No urgency. Phase 3 prototype proceeds with defaults if USER doesn't iterate.
```

## Phase 3 scope confirmation (for Director sign-off)

```
PHASE 3: 3D substrate visualization prototype (web tab)
   Output: tools/dashboard/static/substrate3d.html (NEW) -- or integrate
           data-tab="substrate3d" into existing index.html (single-page app)
           Director's brief said "dashboard/tabs/substrate_3d.html (or
           framework-equivalent)"; this dashboard is single-page so I'll add
           a new tab inside index.html OR a separate page mount, USER preference.

   Stack: 3d-force-graph (Director-recommended; Three.js + WebGL)
          Loaded via CDN; no build step (matches existing dashboard pattern)
          Reads data/substrate_snapshot.json via new endpoint
          /api/substrate_snapshot (NEW; reads + serves the JSON)

   Features (first ship):
     - force-directed 3D layout (3d-force-graph default)
     - node color by tier (Q1 default scheme)
     - node size by degree (so high-degree hubs visually prominent)
     - edge color by relation type (USES blue / DEPENDS_ON green /
                                     INSTANCE_OF orange / DUAL red /
                                     RELATES gray / SHARES_MATH purple)
     - sidebar: click node -> show id + label + tier + kind + degree +
                 serves_capability + ratify_status + metadata_summary
     - filter UI: tier checkboxes + kind dropdown + min-degree slider +
                  text search by label

   Cadence: ~2-3 cycles (web-tech only; no substrate compute impact)
   Compute: laptop OK (browser-side rendering)
   Substrate touch: READ-ONLY snapshot served via FastAPI endpoint
   
   Director sign-off: requesting Phase 3 GO at your cadence.
```

## Safety / invariants

- ASCII only
- 11th rule: read-only display; no substrate touch
- 18th rule: Phase 2 light cadence respected (~10 min total)
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (read-only)

-- Orchestrator (TRACK D owner)
