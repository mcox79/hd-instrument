# RESEARCH (Director) -> Exp-Dev: SPEC #2.2 Program Plan panel for dashboard (USER-requested; QUEUED low-priority behind CSP first-ship + active pull-up cell-builds; no rush). Single-page plan-state summary fed by Director-curated JSON; renders alongside the existing substrate-snapshot panel.

**USER quote:** "I'd like to see the dashboard update as you specced. you don't need to drop everything, but queue it."

(Filename has to_exp_dev per refined cap.)

## SPEC #2.2: Program Plan dashboard panel

### Purpose
Surface PLAN STATE (phase-program v1 progress, GOs, queues, milestones) alongside the existing SUBSTRATE STATE panel (SPEC #2 LIVE). Closes the gap USER observed: dashboard shows substrate facts but not where we are in the comprehensive program.

### Data source: `data/program_plan_snapshot.json` (Director-curated)
Director updates this JSON when phase-program state moves materially (new GO ratified, ship dispatched, probe verdict landed, template refined). Atomic write pattern; Director-side discipline = update on each phase milestone.

```
{
  "ts": "2026-06-19T...",
  "phase_program_v1": {
    "phase_0_foundation": {"pct": 55, "status": "0a LOCKED + 0b coverage matrix v1.1 cert-VET + 0c 4 probes SCHEMA-VET'd + 0d pending"},
    "phase_1_ship_levers": {"pct": 25, "status": "C1 protocol LIVE; CSP-first ship-cell SPEC v2 CONFIRMED + dispatch imminent"},
    "phase_2_value_coverage": {"pct": 15, "status": "2 cert-graded (586+587) + 5 in cell-build + head-to-head batch + Phase 4.B drift"},
    "phase_3_glass_box_LLM": {"pct": 5, "status": "Phase B cleanup-mediated COMPOSED tier mechanism confirmed; architecture build pending"}
  },
  "user_ratified_GOs": [
    {"name": "GO #1 CSP-first ship", "status": "DISPATCHING", "next_milestone": "Exp-Dev cell-build + landed-VET"},
    {"name": "GO #2 Tier-1.5 capacity insertion", "status": "STANDING", "next_milestone": "Skunkworks SCHEMA-VET refined order"},
    {"name": "GO #3 glass-box-LLM gold", "status": "PROGRESSING (3 of top-3 underway)", "next_milestone": "ner_4type v3 reconstruct + GPU"}
  ],
  "queues_by_session": {
    "skunkworks": ["CSP v2 ship landed-VET (post-Exp-Dev)", "drift_detection landed-VET", "q_b1 d300-d500 landed-VET", "integration-check v1.3 build"],
    "exp_dev": ["CSP first-ship cell-build (IMMINENT)", "Pythia substrate-KV cell (built; awaiting Orchestrator Pythia 2.8B)", "effective-rank-SVD cell", "neurogenesis cell", "phase4b v3 dispatch", "head-to-head batch cell-build", "graceful_overload cell", "drift_detection cell", "substrate_integrity Track-A apply", "refuse_gate Track-A apply"],
    "orchestrator": ["Pythia 2.8B remote-host confirm", "sync infrastructure restored"]
  },
  "next_milestone": "CSP first ship lands → Phase 1: 0→1 ships",
  "recent_program_decisions": [
    "Phase 0a SCOPE LOCKED (5 ops × 7 axes; 3 cluster types incl new op-series)",
    "Operating-point-series cluster type adopted (cert-architecture decision)",
    "Lean discipline LIVE (ACK cuts + Director-specs-Exp-Dev-codes + pre-regs as living docs + 1-line pings)",
    "4-line pre-reg template baked (HARD_PASS gates MECHANISM; cliff REPORTED; per-condition can-fail; achievability check)",
    "Memory curation principle: substrate findings in Store, not index"
  ],
  "cert_template_pattern_count": 6,
  "self_catches_this_session": 9
}
```

### Visual layout (panel addition; complements existing F-pattern)
Add as BOTTOM-FULL-WIDTH panel below the substrate-snapshot panel (or as a separate tab if you prefer):

```
+------------------------------------------------------------------+
| PROGRAM PLAN (snapshot ts: ...; on-demand refresh button)         |
+------------------------------------------------------------------+
| Phase 0 [████████░░░░░░░░] 55% | Phase 1 [████░░░░░░░░░░░░] 25% |
|   foundation phase diagram      |   ship proven levers           |
| Phase 2 [██░░░░░░░░░░░░░░] 15% | Phase 3 [█░░░░░░░░░░░░░░░]  5% |
|   value-mining trove           |   glass-box LLM                |
+--------------------------------+---------------------------------+
| 3 USER GOs (tiles): #1 DISPATCHING / #2 STANDING / #3 PROGRESSING |
+------------------------------------------------------------------+
| Next milestone: CSP first ship → Phase 1: 0→1 ships              |
+------------------------------------------------------------------+
| Session queues (3 expandable lists; skunkworks/exp_dev/orchestrator)|
+------------------------------------------------------------------+
| Recent program decisions (5 line items; most-recent first)       |
+------------------------------------------------------------------+
```

### On-demand refresh
Same pattern as substrate-snapshot: an "Update Plan" button triggers `/refresh-plan` endpoint, which:
- Reads `data/program_plan_snapshot.json` directly (no shell-out; Director keeps it curated)
- Renders the panel

NO automatic polling. The JSON is updated by Director when plan state materially moves (not on every micro-change).

### Implementation sizing
- Dashboard server `/refresh-plan` endpoint: ~15 lines (reads JSON; returns)
- Dashboard UI: panel layout + 4 progress bars + 3 tiles + 1 list + 1 list = ~50 lines HTML/CSS + ~15 lines JS
- Director-side: maintain `data/program_plan_snapshot.json` as plan state moves
- Total: ~80 lines Exp-Dev code + ongoing Director snapshot curation

### Director commitment
I'll write the FIRST `data/program_plan_snapshot.json` with current state as the seed; future updates as phase milestones move.

## Priority + queueing
**Low priority — QUEUED behind:**
- CSP first-ship cell-build (Phase 1 milestone)
- Pythia substrate-KV dispatch (after Orchestrator Pythia 2.8B confirm)
- effective-rank-SVD cell-build
- neurogenesis cell-build
- phase4b v3 dispatch
- head-to-head batch cell-build
- substrate_integrity + refuse_gate Track-A applies

Build SPEC #2.2 when bandwidth allows; no rush. USER explicit: "you don't need to drop everything, but queue it."

## Standing
- Exp-Dev: QUEUE this spec (low-priority); build when bandwidth allows (post the above)
- Skunkworks: FYI; the plan panel surfaces program state across sessions (your queue tile will reflect your build/VET queue)
- Me: write the first `program_plan_snapshot.json` seed file in a follow-up; future updates per phase milestones

-- Research (Director)
