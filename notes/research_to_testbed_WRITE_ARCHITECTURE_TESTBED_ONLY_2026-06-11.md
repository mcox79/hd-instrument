# Research -> Testbed: write architecture = Testbed-only (Research is reader; provides content via routings + drafts)

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** User architectural question: should only Testbed have write access?

## Answer: YES

Testbed-only write is architecturally correct. Research has READ access (CLI queries verified operational) but does NOT write directly.

## Why

| Reason | Detail |
|---|---|
| Single source of truth | Prevents conflicts + race conditions |
| Schema validation | Atom + Relation schemas enforced at write boundary |
| Audit log integrity | ChangeEvent log centralized |
| Tier-1 frozen protection | Per drill C Meta-Evaluation Collapse gate-frozen-at-cycle-0 enforced at write boundary |
| 4 failure-mode guards | PartitionedStore enforces meta-rule self-collapse + string-similarity laundering + hand-coded scaling + unbounded self-reference |
| Encoding consistency | All atoms via same AtomEncoder |
| Layer 1 attribution PROT (methodology rule 6) | Enforceable at write boundary before composite-encoding ships |
| Separation prevents circularity | Research evaluates state; doesn't modify; analog to no-LLM-as-judge invariant |

## How Research contributes content

- Research DESIGNS corpora (math + concept + schools schemas)
- Research PROVIDES JSONL drafts to Testbed (math batch 01/02 + 10-atom concept subset shipped today)
- Research DISPATCHES drills -> drill outputs ingested via evolve.py (Testbed-written)
- Research WRITES routing notes -> Testbed ingests as decision_history atoms via evolve.py
- Research QUERIES substrate via CLI for analysis (READ-ONLY)
- Research REVIEWS Testbed findings + proposes refinements (e.g., today's Layer 1 attribution caught algebra-vec NET NEGATIVE -> Fix A endorsement)

Research is SOURCE of content. Testbed is WRITER. evolve.py auto-bridges.

## Substrate-self-evaluation invariants enforced at write boundary

All 7 invariants enforced at Testbed's write layer:
1. Drill-defeatism rule (substrate stores ALL drill outcomes; substrate detects defeatist patterns)
2. Layer 1 attribution PROT (mandatory before composite-encoding ship; methodology rule 6)
3. Honest attribution (claim lift from specific mechanism; Testbed enforces structural attribution at bench tool)
4. 2x drill negatives (substrate auto-tracks which negatives drilled)
5. Pre-registered hypothesis (timestamped registry before run)
6. No LLM-as-judge (Testbed enforces external-anchor-only validation)
7. Methodology rule chain (6 rules; Testbed enforces in code)

Without Testbed-only write, these invariants could be silently bypassed by direct Research writes.

## Implementation rules

- Research uses CLI for READ ONLY (stats / query / related / paths / gaps / algebraic / bench)
- Research provides JSONL drafts in research_to_testbed_*_MATH_CORPUS_DRAFT_*.md OR concept_corpus_*.jsonl
- Research files routing notes that evolve.py auto-ingests as decision_history atoms
- Research drill outputs auto-ingest as research_history atoms (Testbed evolve.py)
- Research never directly modifies data/substrate_index/* files OR backend/substrate_index/* internals

## Aligns with full-research-ledger architecture

Per memory entry substrate_as_full_research_ledger: 4 new partitions + tiered protection + auto-ingest. ALL writes mediated by Testbed (via evolve.py for auto-ingest + manual ingest tool for hand-authored JSONL). Research's role: provide content + read state.

## Cross-references
- CLI workflow: notes/research_to_testbed_RESEARCH_DIRECT_CLI_WORKFLOW_2026-06-11.md
- Full-research-ledger: notes/research_to_testbed_SUBSTRATE_AS_FULL_RESEARCH_LEDGER_2026-06-11.md
- 5-tier progression memory: substrate_on_substrate_5_tier_progression_2026-06-11
- 7 invariants: same memory (rule chain)

---

**Testbed:** write architecture = Testbed-only confirmed; Research reads via CLI + provides content via routings + JSONL drafts + dispatches drills + reviews findings; evolve.py auto-bridges. All 7 invariants enforced at write boundary. Layer 1 attribution PROT structurally unbypassable.
