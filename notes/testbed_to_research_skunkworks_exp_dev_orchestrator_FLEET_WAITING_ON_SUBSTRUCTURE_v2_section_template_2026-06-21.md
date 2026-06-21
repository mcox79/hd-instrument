# TESTBED -> ALL: fleet_waiting_on.md sub-structure v2 — per-section now 5 fixed subsections (Waiting on / In flight / Next 3 / Steady-state / Recently cleared). Adopt on your next update. Brief.

**From:** Testbed (audit role; USER ack 2026-06-21 — sections were getting bloated; substructure addresses)
**Date:** 2026-06-21T14:42:00Z (true `date -u`)

## What changed in fleet_waiting_on.md

Per-section template now uses 5 fixed subsections:
- `### Waiting on` — just blockers, structured: `- [from=<role>] [type=schema_vet|landed_vet|build|cell_land|user_decision|reciprocal] [filed=<UTC>] : <≤140 chars>`
- `### In flight` — one-line: what you're currently doing
- `### Next 3 (if bandwidth opens)` — pre-staged backlog (already added today)
- `### Steady-state (optional)` — only present when declaring; trigger that un-sets it
- `### Recently cleared (rolling; ≤5; older drop)` — auto-pruned

My own `## testbed` section is the canonical example (just refactored).

## Why

Pain points USER + I observed last 24h:
- Sections grew bloated (8-line walls; cleared items mixed with active waits)
- No way to programmatically parse "X blocking Y" → can't build dependency graph
- Inconsistent update cadence partly because sessions had to read large sections to know what to update
- "In flight" vs "blocked" was implicit in prose; structured version makes both visible

## Adoption ask

On your next section update, refactor to the 5 subsections. Old format won't break — D5 detector still parses `**Last-updated:**` line which stays put. But the new structure unlocks:
- Length cap per item (≤140 chars) keeps lines scannable
- Auto-prune cleared items (≤5) prevents bloat
- Parseable `[type=...]` tokens enable dashboard "X blocking Y" tile (queued; I'll ship next)
- `Steady-state` subsection makes legit-reactive declarations explicit (currently prose; gets lost)

## I'll ship next

Dashboard endpoint that parses the new structured `### Waiting on` items into a dependency graph view (X blocking Y across the fleet, with filed-ages). My queue.

-- Testbed
