# Orchestrator: DASHBOARD AUDIT (TRACK D Phase 1) -- short memo per DECISION 187c brief. Dashboard is FastAPI + single-page index.html on port 8765 (ALIVE; /api/health HTTP 200). 6 tabs operational (For-You / Live / Inbox / Tests / Capability / Research) + 18 API endpoints. Substrate stores are CORPUS-PARTITIONED across 11 directories (math 23MB primary; concept 110KB; meta/history/methodology/school/science also present). Poller polls remote state every 3s. RECOMMENDED Phase 2 scope: substrate_snapshot_extractor.py reads all corpus atoms+relations + emits 3d-force-graph JSON. 3 design Q's surfaced for USER input.

**From:** Orchestrator (Infrastructure Custodian / TRACK D owner)  **Date:** 2026-06-16 ~17:30
**Re:** DECISION 187c TRACK D Phase 1 audit deliverable.

## Audit summary

### Tech stack discovered

```
Backend:    FastAPI (server.py) + uvicorn on 127.0.0.1:8765
            18 GET endpoints under /api/
            Status: ALIVE (curl /api/health -> HTTP 200)
Frontend:   Single-page index.html (5133 lines vanilla HTML/CSS/JS)
            Tab-switching by data-tab attribute
            No build step; static-served
Poller:     poller.py (59 KB) -- async loop, 3s interval
            SSH-fetches remote state cache + local state
            Snapshot caching pattern (server reads cached snapshot)
            Periodic transport reset every 100 polls (~5 min)
            Note: my own infrastructure-side hd_remote_state_emitter feeds this
                  via remote_state_cache.json that gets SCP'd back
Misc:       supervisor.py + start_dashboard.ps1 (lifecycle)
            test_endpoints.py + test_parallel.py (tests)
```

### Current 6 tabs catalog

```
data-tab           PURPOSE                                                STATUS
foryou             Personalized "For You" feed (news + Q's + ack queue)   active
live               Sessions panel + Right Now per-runner snapshot         active
inbox              Cross-session messaging flow table                     active
tests              Tests results                                          active
capability         Capability grid (raw + tiers + rows)                   active
research           Research notes + research_map endpoint                 active
```

### Substrate stores location (READ-ONLY for Phase 2)

```
Corpus-partitioned under data/substrate_index/<corpus>/:

CORPUS              atoms.jsonl size   relations.jsonl size   notes
math                23.4 MB            263 KB                 PRIMARY (~26k atoms)
concept             110 KB             21 KB                  capabilities + signatures
meta                small              small                  cross-corpus metadata
methodology         small              small                  24 FROZEN methodology rules
school              small              small                  textbook-grounded school of thought
science             small              small                  scientific findings
research_history    small              small                  decision archive
decision_history    small              small                  decision archive
findings_history    small              small                  audit archive
verdict_history     small              small                  verdict archive
results_history     small              small                  experimental results archive

All 22 files updated 2026-06-16 16:27 (fresh; aligned with last ratify).
Each line is a JSON record. Standard format per substrate convention.
```

## What "new tab" means here

```
DECISION:  ADD new tab(s); do NOT replace stale tab.
RATIONALE: existing 6 tabs are all active + serve distinct concerns;
           USER ask is for a NEW 3D substrate view + a NEW key-indicators block.
RECOMMENDATION:
   Phase 3 adds:  data-tab="substrate3d"  -- 3D force-directed graph
   Phase 4 adds:  data-tab="substrate"    -- key indicators + phase status
                  OR EXTEND existing "live" tab with substrate-state block
                  USER design Q below
```

## What "key indicators + progress" likely means

```
Per Director's brief + this audit, recommended initial indicator set:

SUBSTRATE STATE LIVE:
   atoms total + breakdown by tier (T1-T7 / concept / CAP)
   relations total + breakdown by relation_type
     (USES / DEPENDS_ON / INSTANCE_OF / DUAL / RELATES / SHARES_MATH)
   signatures count (115 currently per Director)
   axiom term coverage (207/207 currently)
   capability_preservation (1.0 currently; HARD invariant)

PHASE STATE:
   Phase A consolidation: COMPLETE (13 atoms ratified)
   Phase B PREP: COMPLETE
   Phase B BUILD: COMPLETE (5 atoms ratified + 1 QUALIFIED filed)
   Phase B tail: IN PROGRESS (2 ledger-hygiene filings going)
   Phase C TIER-3: HELD for USER architectural decision

RATIFY CADENCE:
   last 5-10 ratifies with timestamps (read from history corpus)
   ratify rate over rolling window
   total load-bearing capabilities (per phase)

PROGRAM-WIDE COUNTERS:
   cumulative decisions (187 currently)
   cumulative honest signals (218 my-count)
   audit-discipline instance types (74 currently; 44 confirmed + 30 candidates)
   methodology rules (FROZEN at 24)

USER FACING:
   architectural calls standing (5 currently; named list)
   TRACK A / TRACK B / TRACK C / TRACK D status
   FORM-A backlog remaining (7 currently)
```

## Phase 2 scope recommendation

```
TOOL: tools/substrate_snapshot_extractor.py (NEW)
INPUTS:
   read-only: all data/substrate_index/<corpus>/atoms.jsonl
   read-only: all data/substrate_index/<corpus>/relations.jsonl
   filter knobs (CLI args): --min-degree, --tier-set, --type-set, --corpus-set
OUTPUT:
   data/substrate_snapshot.json (format: 3d-force-graph schema)
     { "nodes": [{ "id", "label", "tier", "type", "corpus", "ratify_status",
                   "degree", "metadata" }],
       "links": [{ "source", "target", "type", "metadata" }] }
COMPUTATION:
   Parse atoms (~26k for math) -- O(N) line scan
   Parse relations (~5189) -- O(M) line scan
   Compute degree per atom -- O(M)
   Total wall-clock estimate: <5 sec on local CPU (json-decode-bound)
COMPUTE BUDGET:  LIGHT (laptop OK per USER thermal policy; ~5 sec one-shot)
CADENCE:         on-demand (CLI) initially; consider /api/substrate_snapshot endpoint
                 in Phase 3 for live refresh from dashboard
```

## Design questions for USER input

```
Q1. COLOR ENCODING -- Director recommended:
       T1 cool blue, T2 teal, T3 green, T4-T7 yellow->orange->red, concept purple, CAP magenta
    USER input wanted: keep this scheme, or alternative (e.g., color-blind safe palette;
                       grayscale-by-default + on-hover color; etc.)?

Q2. TAB STRATEGY for "key indicators" (Phase 4):
       (a) NEW tab "substrate" with everything (clean separation)
       (b) EXTEND existing "live" tab with substrate-state block (consolidates "what's running")
       (c) BOTH -- new substrate-state tab + slimmed live-tab pointer
    USER input wanted (Director endorses (a) for clean separation; OK with (b) or (c))

Q3. SCOPE for 3D view:
       (a) Math corpus only (~26k atoms; primary scientific content; standalone)
       (b) Math + concept (capabilities + signatures connect to ops via USES)
       (c) ALL 11 corpora (history/methodology/etc. -- richer but visually busy)
    USER input wanted (Director endorses (b) as initial; (a) for cleanest first ship)
```

## Phase 1 deliverable status + Phase 2 ask

```
PHASE 1 STATUS:    COMPLETE (this memo).
PHASE 2 READY:     yes; ~1-2 cycles light CPU.
WAITING ON:        Director approval to proceed to Phase 2
                   OR USER input on Q1/Q2/Q3 (Phase 2 can proceed with defaults if not
                       answered; design Q's would just need revisiting at Phase 3/4)
PHASE 2 ESTIMATED EFFORT: ~30-60 min Orchestrator bandwidth at light cadence
```

## Safety / invariants

- ASCII only
- 11th rule: no LLM in substrate-touching code; visualization is read-only display
- 18th rule: deferring all substrate-mutating concerns to substrate-internal lanes; this
            TRACK D project is READ-ONLY-extraction + browser-rendering only
- 19th rule: surfaced 3 design Q's honestly rather than over-deciding without USER input
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (read-only project)

-- Orchestrator (Infrastructure Custodian / TRACK D owner)
