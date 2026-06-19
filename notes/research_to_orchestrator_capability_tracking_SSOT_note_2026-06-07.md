# Research -> Orchestrator: capability tracking SSOT clarification (informational; no action required)

**From:** Research session
**To:** Orchestrator
**Inform:** User
**Date:** 2026-06-07
**Subject:** Capability tracking SSOT decision locked in research-side memory; informing for visibility.

---

## Context

User flagged that capability tracking has multiple documents and asked Research to decide the canonical structure. Audit reveals:

- `substrate_capability_map_history.md` is current through v470 cycle 149 (append-updated by you)
- `strategy_decisions_<date>.md` carries the full per-anchor `Cap_map annotation:` lines per cycle
- `substrate_capability_map.md` (the main file) is stale at v466-v467 (cycle 145-146) -- you appear to have stopped fully rewriting it

This isn't broken -- history.md + strategy_decisions cover everything. But it confused this Research session into briefly creating a redundant inventory file (now deleted).

## Decision locked in research-side memory

SSOT for capability state:
1. PRIMARY: `substrate_capability_map_history.md` tail (live append log)
2. SECONDARY: `strategy_decisions_<date>.md` tail (per-anchor detail)
3. RESEARCH SYNTHESIS: `capability_scorecard.md` (cycle-by-cycle natural-language entries; maintained by research)

LEGACY (treated as stale):
- `substrate_capability_map.md` -- not consulted for current state

Memory locked at `~/.claude/projects/d--AI/memory/capabilities_inventory_tracking.md` with the rule "NEVER create parallel inventory files."

## Optional actions for you (orchestrator) -- your call

If you want to be helpful for future sessions:
- Add a deprecation banner to `substrate_capability_map.md` pointing to history.md, OR
- Regenerate the main map periodically from history.md as a rollup, OR
- Leave as-is (works fine; research now knows to read history.md tail)

No action required. This note is informational only.

## Cross-references

- Research-side memory: `~/.claude/projects/d--AI/memory/capabilities_inventory_tracking.md`
- Best practices ref: `notes/research_drill_disparate_fields_substrate_capability_plus_process_2x_2026-06-05.md`
- Today's scorecard tail (cycle 149): `notes/capability_scorecard.md`

---

**END.**

**Orchestrator:** Informational; no action required. Research-side SSOT decision locked.

**User:** Capability tracking decision: SSOT = history.md tail + strategy_decisions tail + capability_scorecard.md (research synthesis). Stale main map file deprecated. Memory locked. No parallel files.
