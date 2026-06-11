# Research -> Testbed: Research workflow now uses substrate CLI directly

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** User direction: Research should have direct substrate access; verified CLI operational

## Workflow change

Going forward, Research uses substrate CLI directly via Bash:
- `python -m backend.substrate_index.cli stats` -- substrate state
- `python -m backend.substrate_index.cli query "<text>"` -- semantic retrieval
- `python -m backend.substrate_index.cli related <atom_id>` -- find related atoms
- `python -m backend.substrate_index.cli paths <src> <tgt>` -- lineage trace
- `python -m backend.substrate_index.cli gaps` -- discovery findings
- `python -m backend.substrate_index.cli algebraic <atom_id>` -- shared-basis (post v2)

Verified: stats CLI works (60 atoms / 143 relations / 4 partitions).

## How Research uses substrate

Before dispatching new drill: query substrate for past similar drill outcomes
Before filing routing: query substrate for past similar architectural decisions
Before claiming "new" finding: query substrate for analogous prior findings
Before recommending build: query substrate for past plateau/lift evidence

Substrate becomes Research's working memory + reference + insight engine.

## Connects to full-research-ledger vision

Substrate currently has 60 math + 10 concept = 70 atoms; missing 381 PP + ~32 drills today + 50 memory + 150 routings + 235 cap_map.

Once full-research-ledger lands (4 new partitions), Research queries become:
- "What past drill found a result similar to X?"
- "What lineage led to current architectural decision Y?"
- "Which methodology rule was applied in similar past case?"
- "What patterns persist across cycles 220-235?"

## Layer-1-attribution applies to my queries too

Per methodology rule 6: when I claim lift from a substrate query result, I attribute to the specific mechanism (relations vs semantic vs algebraic) not aggregate.

## Honest about current limits

Substrate's 60-atom corpus is small for my Research needs. The full-research-ledger ingest is the bridge from "substrate as Testbed deliverable" to "substrate as Research workflow tool."

## Cross-references
- Full-research-ledger routing: notes/research_to_testbed_SUBSTRATE_AS_FULL_RESEARCH_LEDGER_2026-06-11.md
- 5-tier progression memory: substrate_on_substrate_5_tier_progression_2026-06-11
- Substrate self-index foundational tool memory

---

**Testbed:** Research workflow now uses substrate CLI directly. Verified operational. Full-research-ledger ingest (4 new partitions) is the bridge from "Testbed deliverable" to "Research workflow tool." Layer 1 attribution applies to Research's substrate queries too.
