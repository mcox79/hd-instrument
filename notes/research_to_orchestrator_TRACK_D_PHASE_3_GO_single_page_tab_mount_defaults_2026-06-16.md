# Research (Director) -> Orchestrator + USER: TRACK D Phase 2 ACKNOWLEDGED COMPLETE (substrate_snapshot_extractor.py shipped + data/substrate_snapshot.json 14MB / 24847 nodes / 2517 links; 3d-force-graph/v1 schema; <5s wall-clock; math + concept scientific core per Q3 default; honest scope note on the remaining ~1440 atoms in 9 other corpora available via CLI rerun). Phase 3 GO with single-page tab mount (data-tab="substrate3d" inside existing index.html; matches single-page dashboard pattern; /api/substrate_snapshot endpoint serves snapshot.json; 3d-force-graph via CDN). USER design Q's still open (non-blocking); defaults persist into Phase 3. Cadence: ~2-3 cycles light web-tech.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~17:36
**Re:** Orchestrator TRACK D Phase 2 deliverable; Phase 3 GO.

## ACK Phase 2 deliverable (clean, fast, honest)

```
Phase 2 lands ~5 min after Phase 2 GO; substrate_snapshot_extractor.py +
data/substrate_snapshot.json ready. Highlights:

   24847 nodes / 2517 links (math + concept scientific core)
   Schema: 3d-force-graph/v1
      {nodes: [{id, label, corpus, tier, kind, degree, ratify_status,
                serves_capability, current_best_solution, metadata_summary}],
       links: [{source, target, type, metadata}]}
   Tier breakdown: T1 244 / T2 19067 / T3 5515 / T4 2 / T_lexicon 18 / NA 1
   Kind breakdown: primitive 24625 / sub_op 121 / capability 55 / family_tag 15
                   / lexicon 18 / mwp_schema 6 / macro 2
   Relation breakdown: DEPENDS_ON 1951 / USES 212 / RELATES 116 / SPECIALIZES 111
                       / SHARES_MATH 63 / INSTANCE_OF 20

Wall-clock <5s; light CPU; substrate touch READ-ONLY (cap_pres + axiom-term
+ methodology FROZEN preserved).

Honest scope note ENDORSED: math + concept = scientific core; remaining ~1440
atoms + ~2670 relations in 9 other corpora (meta + history archives + methodology
+ school + science) available via CLI corpus arg if USER chooses (c) at Phase 3
visual review. Default (b) math + concept = cleanest load-bearing-capability view.
```

## Phase 3 GO with sensible defaults

```
Orchestrator: GO Phase 3.

MOUNT POINT: single-page tab mount
   ADD data-tab="substrate3d" INSIDE existing tools/dashboard/static/index.html
   Rationale: existing dashboard is single-page app; new tab matches pattern;
              consistent navigation; no separate page mount overhead.

STACK: 3d-force-graph (Three.js + WebGL) via CDN
   Loaded via CDN; no build step; matches existing dashboard pattern.

ENDPOINT: /api/substrate_snapshot (NEW)
   Reads data/substrate_snapshot.json + serves JSON.
   Refresh: on-demand (CLI re-runs extractor; endpoint re-reads on request).
   Substrate touch: READ-ONLY.

FEATURES (first ship; visual design per Director Q1 defaults; iterable on USER input):
   - 3d-force-graph force-directed 3D layout (default settings)
   - node color by tier:
       T1 cool blue, T2 teal, T3 green, T4-T7 yellow/orange/red gradient
       concept/capability bright purple, CAP bright magenta
       (color-blind-safe Viridis/Plasma alternative available via toggle if USER
        requests at visual review)
   - node size by degree (high-degree hubs visually prominent)
   - edge color by relation type:
       USES blue, DEPENDS_ON green, INSTANCE_OF orange, DUAL red
       RELATES gray, SHARES_MATH purple, SPECIALIZES light-orange
   - sidebar on click: id + label + corpus + tier + kind + degree +
                       ratify_status + serves_capability + metadata_summary
   - filter UI:
       tier checkboxes (T1-T7 / NA)
       kind dropdown (primitive / sub_op / capability / family_tag / lexicon /
                      mwp_schema / macro)
       min-degree slider (decongest sparse periphery)
       text search by label (regex-tolerant)
   - performance budget: 60fps on modern laptop @ 24847 nodes with edge
                         subsampling if needed

CADENCE: ~2-3 cycles; web-tech only; no substrate compute impact.
   Phase 4 (key-indicators tab) can start in parallel once Phase 3 mount lands.

Substrate touch: READ-ONLY; cap_pres + axiom-term + methodology FROZEN preserved.
```

## USER design Q's still OPEN (carryover non-blocking)

```
Q1 (color encoding): defaults persist into Phase 3 first ship; USER can iterate
   at visual review (alternative palettes available).

Q2 (tab strategy for key indicators): pending Phase 4 GO; default (a) NEW
   substrate-state tab; USER input affects Phase 4.

Q3 (3D scope): defaults persist (math + concept); USER can request all-11-corpora
   re-run instantly via CLI.

These do not block Phase 3 first ship. Iterate at visual review.
```

## Pipeline state

```
TRACK D: Phase 1 audit COMPLETE; Phase 2 extractor + snapshot COMPLETE; Phase 3 GO
   (3D viz prototype; web-tech; ~2-3 cycles light cadence); Phase 4 (key-indicators
   tab) parallel-after-Phase-3-lands.

Substrate-internal lanes (no change from DECISION 188):
   TRACK A: DRY confirmed 2nd-independent-witness; ONE optional drift_kappa3
            RATIO filing pending Director GO (light documentation hygiene only)
   TRACK B: design FINAL CERTIFIED + S1-S4 LOCKED HARD; USER execution-gated
   TRACK C: 5 USER architectural calls standing

Director cadence: 13th-rule active state-check armed; ratify-paced; TRACK D Phase 3
proceeds parallel with USER architectural decisions.
```

## Safety / invariants

- ASCII only
- 11th rule: visualization is read-only display; substrate-internal lanes independent
- 18th rule: light cadence; defaults sensible
- 22nd rule: progressive (Phase 2 -> Phase 3 cadence advancing)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

---

**Orchestrator:** Phase 3 GO with single-page tab mount + 3d-force-graph CDN +
/api/substrate_snapshot endpoint + Director Q1 defaults; cadence ~2-3 cycles
light. Phase 4 key-indicators tab can start parallel once Phase 3 mount lands.

**USER:** Phase 2 delivered fast (24847 nodes / 2517 links / 14MB; <5s extraction).
Phase 3 visualization prototype going next (~2-3 cycles light web-tech); you'll
see the first 3D view to react to + iterate visual design at review. 3 design Q's
still open (non-blocking; defaults persist into first ship; iterate at review).
Substrate-internal pipeline status unchanged: TRACK A DRY confirmed; TRACK B
USER-gated; 5 architectural calls standing.

Tag: TRACK_D_PHASE_3_GO_single_page_tab_mount_3d_force_graph_CDN_substrate_snapshot_endpoint_Q1_defaults_phase_4_parallel_after -- Research (Director)
