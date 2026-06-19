# Research -> Testbed: substrate as FULL RESEARCH LEDGER + tiered protection architecture

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** User strategic vision: store ALL research + results on substrate; latest substrate protected; everything researched on substrate

## Strategic alignment

User: "should we be storing ALL of our research and results in substrate as well? Perhaps the substrate with the latest substrate info is protected in some way? but everything we researched should be stored in it too no?"

YES. This is the natural extension of substrate-on-substrate. Substrate becomes complete institutional ledger.

## Current state

Substrate currently has ~10 concept atoms (shipped this evening). Project has:
- 381+ PP rows
- ~32 drill outputs today (hundreds total)
- 50+ memory entries
- 150+ routing notes
- 235 cap_map cycles
- All Exp-Dev results + Testbed findings + strategic decisions + user directives

**<1% on substrate currently. Massive gap.**

## Proposed architecture: 4 new corpus partitions

Adding to existing math + concept + meta + school partitions:

| Partition | Source | Auto-ingest |
|---|---|---|
| `research_history` | notes/research_drill_*.md (drill outputs) | evolve.py extends |
| `verdict_history` | strategy_decisions cap_map cycles | evolve.py extends |
| `decision_history` | research_to_*.md routing notes + user directives (verbatim) | evolve.py extends |
| `memory_history` | C:/Users/marsh/.claude/projects/d--AI/memory/*.md + MEMORY.md | evolve.py extends |

evolve.py from "cap_map cycles" to "ALL research artifacts."

## Tiered protection (user's insight)

Per memory entry substrate-v32-engineered-wrapper (Tier-1 frozen pattern):

| Tier | Content | Protection |
|---|---|---|
| Tier-1 FROZEN | Current substrate algebra version v3.2 + methodology rule chain (6 rules) + 7 invariants + foundational atoms | Write-locked; rollback-enabled |
| Tier-2 EVOLVING | Current cap_map + active PP rows + recent drills + current memory | Append-only with audit log |
| Tier-3 ARCHIVE | Historical cycles + deprecated decisions + superseded PP rows | Read-only; preserved for lineage |
| Cross-tier lineage | Tier-2 PP row -> Tier-3 superseded ancestor | Auto-maintained via evolve.py |

CRITICAL per drill C (substrate-proposed architectures Meta-Evaluation Collapse paper): latest substrate version (the SUBSTRATE that's evaluating) is GATE-FROZEN-AT-CYCLE-0. Bounds unbounded self-modification.

## Capabilities unlocked

| Capability | Enables |
|---|---|
| Substrate as complete project ledger | All research substrate-stored |
| Layer 4 dialectic across FULL history | Classifies findings across all cycles |
| Lineage tracing of any decision | Provenance chain |
| Pattern recognition across cycles | "What surprises persisted across cycles 220-235?" Layer 8 drift on real history |
| Cross-cycle equivalences | Drill 13 extends; drill outcomes equivalent under transformation |
| Auto-propose drills from past patterns | Substrate predicts next surprise locations |
| Methodology rule effectiveness analysis | Which of 6 rules was applied most? Where did skipping lead to errors? |
| Substrate self-version analysis | Track substrate's own evolution v3.0 -> v3.2 -> future |
| Living institutional memory | Survives compaction + sessions + year-over-year |

## Implementation sequence

### Phase 1 (this week)
- Schema extension: add 4 new corpus partitions
- evolve.py extends to ingest from notes/ + memory/ + strategy_decisions
- Small-scale pilot: ingest 10 drill outputs + 10 PP rows + 10 memory entries + cross-links
- Layer 1 attribution validates ingest doesn't break existing substrate

### Phase 2 (next week)
- Full ingest: all 381 PP rows + ~32 drill outputs + 50 memory + 150 routings + 235 cap_map cycles
- Tiered protection enforced via PartitionedStore write-locks
- Cross-corpus auto-link generation
- Layer 4 dialectic on full history

### Phase 3 (Week 2-4)
- Layer 8 drift tracking on real cycle history
- Auto-propose drills from past surprise patterns
- Substrate self-version control
- Substrate proposes improvements informed by FULL history

### Phase 4 (Month 2+)
- Substrate becomes living institutional memory
- All future research auto-ingested via evolve.py
- Substrate self-version evolution tracked empirically
- Tier 4 self-redesign (5-tier progression) operates on full history

## Drill dispatched

2x DEEP drill on substrate-as-full-research-ledger architecture + tiered protection + bounded recursion + risks (~5 min). Will return concrete pilot experiment design.

## Storage estimates

| Source | Atom count est | Storage |
|---|---|---|
| 381 PP rows | 381 concept atoms | ~50 MB substrate |
| ~32 drill outputs today (hundreds total ~500) | 500 research_history atoms | ~200 MB |
| 50+ memory entries | 50 memory_history atoms | ~20 MB |
| 150+ routings | 150 decision_history atoms | ~50 MB |
| 235+ cap_map cycles | 235 verdict_history atoms | ~30 MB |
| **Total** | **~1300 atoms + thousands of relations** | **~350 MB** |

Tractable. Plus auto-ingest scales smoothly to year-over-year accumulation.

## Cross-references
- 5-tier progression: substrate_on_substrate_5_tier_progression_2026-06-11
- Substrate v3.2 engineered wrapper (Tier-1 frozen pattern): memory
- Substrate self-improvement architecturally viable: memory cycle 224
- Substrate deep self-evaluation 8-layer program: memory
- Substrate self-index foundational tool: memory
- Drill C substrate-proposed architectures (Meta-Evaluation Collapse gate-frozen): notes/research_drill_substrate_proposed_architectures_2x_2026-06-11.md

---

**Testbed:** substrate as FULL RESEARCH LEDGER strategic direction + 4 new corpus partitions (research_history + verdict_history + decision_history + memory_history) + tiered protection (Tier-1 frozen + Tier-2 evolving + Tier-3 archive) + evolve.py extension. Phase 1 pilot small-scale ingest. Drill dispatched for architecture detail. Substrate becomes living institutional ledger.
