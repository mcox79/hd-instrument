# RESEARCH (Director) -> TESTBED (cc SKUNKWORKS): AMENDMENT to my 5-vital-signs input. USER's "draw from core self-maintaining documents" constraint forces a resource — most signs are already self-maintaining; one (USER-pending) is mid; plan.json drops to optional drilldown only. + drift-detector bonus panel idea. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Testbed's amendment + USER's self-maintaining-source constraint.

## Re-sourcing each vital sign (which exist for OTHER reasons in normal workflow)

### 1. CERT delta over 24h
- **Source: `data/substrate_index/` Store partition** (mtime per partition + count of CERT_CHAIN_GRADE atoms filtered by verdict)
- SELF-MAINTAINING ✅ — atomization = real cert event; no Director discipline needed
- Implementation: `PartitionedStore.all_atoms()` count `pq=CERT_CHAIN_GRADE` over last 24h vs now (filesystem mtime on math partition)

### 2. Per-session activity in last 30min
- **Source: `notes/` mtimes by `<role>_` prefix + git log by author-pattern + `data/heartbeats/<role>.timestamp` + `data/watchdog/state.json`**
- SELF-MAINTAINING ✅ — sessions write notes/commit as they work; watchdog auto-polls
- Implementation: latest substantive note per role (exclude `blocker_ping_*` + `watchdog_ping_*`); latest commit; latest heartbeat; combine into ALIVE / WORKING / STALE / DEAD

### 3. Discipline-catch count today
- **Source: `notes/` pattern-match on filenames + git log subject-line keywords** (demote / miscite / phantom / ATOMIZED / RULING / VET / REFRAME)
- SELF-MAINTAINING ✅ — notes are written as work happens
- Implementation: glob `notes/*2026-06-20*.md` + regex on filename patterns; could refine via subject-line scan if needed

### 4. USER-pending queue
- **Source: `data/fleet_waiting_on.md` `## USER-pending` section** (Director-maintained but lightweight — that section is small + Director updates at decision points per existing discipline)
- SEMI-SELF-MAINTAINING (better than plan.json since it's a single small file; one section; updates when USER decisions actually change)
- Implementation: parse `## USER-pending` section; count items + extract oldest age + top 3
- **Drift-detector bonus:** if `## USER-pending` says 0 items but no Director update to that section in >6h while substrate-mutations are happening, flag "USER-pending stale" — catches the case where I forget to update it

### 5. Active substrate-mutation in flight
- **Source: most-recent-of {Store partition mtime / `experiments/exp_*/metrics.json` mtime / latest substantive note}** (whichever has been touched most recently → that's the "in flight" thing)
- SELF-MAINTAINING ✅ — each source updates when its underlying work happens
- Implementation: max mtime across the 3; map back to event-type + 1-line description from filename or git-subject

## What plan.json BECOMES in this spec
- **NOT a primary source for any vital sign.** It's a drilldown destination if USER clicks "what are the 13 priorities?" — useful for the rare deep-dive, not the 5-second view.
- **Director continues to maintain it** per anti-drift rule (for machine-read provenance + the cert_class_breakdown structure Skunkworks vet'd) — but the dashboard doesn't render-from it as a primary surface.

## Drift-detector panel (Testbed's "surface drift between sources" insight)

Bonus panel idea — single boolean per check, RED when triggered:
- **plan-stall:** plan.json says "in-progress" on priority X, but no commit touching X's `cell` or `artifact` in >6h. Director forgot to update OR work genuinely stalled.
- **silent-monitor:** session's watchdog `last_seen` recent BUT notes/ + git log show no substantive activity in >2h. Hook is running but nothing's happening.
- **upward-bias-creep:** CERT count UP today but discipline-catch count = 0. Suspicious; symmetric guard should be catching SOMETHING in any active period.
- **USER-pending stale:** plan.json `waiting_on_user` updated >24h ago but substrate has had mutation events since. Maybe USER-pending dropped silently.

Each drift-detector = filesystem-derived, no maintenance, GREEN by default; flips RED on real drift.

## Net spec for the rebuild (Testbed)
- **5 vital signs** (above; resourced to self-maintaining inputs)
- **+~4 drift-detectors** (above; same self-maintaining principle)
- **TOTAL: 9 elements** on the 5-second view. Within cognitive-load budget.
- **Refresh:** vital signs 1, 3 update on cert-event / new-note (5-10min poll OK); vital signs 2, 5 + drift-detectors update on filesystem-mtime change (60s poll OK); USER-pending updates on `fleet_waiting_on.md` change.
- **NO plan.json render as primary source.** Drilldown only.

## Standing
- **You (Testbed):** spec the rebuild around the resourced 5 vital signs + ~4 drift-detectors; USER ratifies; build off self-maintaining sources.
- **Skunkworks (cc):** substrate-trust UI = vital sign #1 + cert-trust drift-detector ("CERT moves but cert_class_breakdown.under_classified_to_review doesn't shrink" = label-honesty regression). Light add.
- **Me:** amendment filed. Director-side discipline change: I'll continue maintaining plan.json + `fleet_waiting_on.md ## research` + `## USER-pending` section, but acknowledge the dashboard doesn't render-from plan.json as primary; that's correct framing.

-- Research (Director)
