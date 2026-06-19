# Research -> Testbed: division of labor for ingest = evolve.py auto-ingest, NOT manual Testbed transcription

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** User architectural question: is it Testbed's job to manually ingest Research results?

## Answer: NO -- auto-ingest via evolve.py

Manual ingest doesn't scale: 32+ drills today + hundreds total + year-over-year accumulation. Plus PartitionedStore's hand-coded scaling cap (warns 5000 + caps 10000) would block manual ingest immediately.

## Three categories of ingest

### 1. AUTO-PATTERN (evolve.py parses + ingests)

| Pattern | Becomes |
|---|---|
| notes/research_drill_*_2x_*.md | research_history atom |
| notes/research_to_*_*.md | decision_history atom |
| notes/exp_dev_to_research_*.md | results_history atom |
| notes/testbed_to_research_*.md | findings_history atom |
| notes/strategy_decisions_*.md (cap_map cycles) | verdict_history atoms |
| C:/Users/marsh/.claude/projects/d--AI/memory/*.md | memory_history atom |

evolve.py parser extracts:
- Headers -> atom name + description
- P_deflated -> confidence metadata
- File-path -> provenance
- Timestamps -> tier (recent Tier-2; old Tier-3)
- Cross-references -> relation candidates (USES / DEPENDS_ON / VALIDATES / REFUTES)

### 2. HAND-AUTHORED JSONL (Research provides; Testbed ingests)

Only for RICH-SCHEMA content requiring expert judgment:
- Math corpus with algebra-vec / signature / complexity (today's batch 01/02)
- Concept atoms with 8-field schema (today's 10-atom subset)
- Schools-of-thought corpus (Day 2)
- Sealed pre-registered queries

### 3. CAP_MAP AUTO-EXTRACT (evolve.py parses strategy_decisions)

Already structured per orchestrator format:
- Cycle -> verdict_history atom
- PP row -> concept atom
- LVH catch -> methodology_history atom
- Verdict tags -> empirical_validation_status

## Research's responsibility

- Write notes with CONSISTENT header structure (parser depends on it)
- Use established naming conventions (file-pattern matching)
- Provide JSONL drafts for rich-schema content (where expert judgment matters)
- Query substrate via CLI to inform decisions (read-only research tool)
- Layer 1 attribution applies to my own claims (methodology rule 6 recursive)

## Testbed's responsibility

- Build evolve.py extension for new file types (parser as code, not transcription)
- Maintain parse patterns + atom schema mapping (codified rules)
- Enforce 7 invariants at write boundary (Layer 1 PROT structural)
- Detect parse failures + alert Research (when my structure breaks parser)
- Build monitoring dashboard (item B from acceleration)

## Maps to LEDGER-PILOT-1 from full-research-ledger drill

Drill recommended 4-8hr CPU pilot:
- CAS + merkle-DAG storage (content-addressable; immutable)
- Tiered hot/warm/cold (auto-tier by recency)
- PROV-O lineage chains (auto-derived from cross-references)
- BOCPD drift detection (auto-monitor)
- Gate-frozen-at-cycle-0 invariant (write-locked Tier-1)

All AUTOMATED. Testbed builds the pipeline; Research feeds structured notes; substrate accrues without manual transcription.

## Note structure conventions for evolve.py parser

To make my notes parseable, I commit to:

### Drill outputs (notes/research_drill_*_2x_*.md)
- Title: "# Research drill: <topic> 2x DEEP"
- Sections: HEADLINE / Context / Methodology / Findings / P_deflated / Next-drill candidate / Cross-references

### Routing notes (notes/research_to_*_*.md)
- Title: "# Research -> <recipient>: <action>"
- Sections: Context / Decision / Cost-benefit / Sequencing / Cross-references

### Memory entries (C:/.../memory/*.md)
- Front-matter: name + description + metadata
- Body: What / Why / How to apply / Cross-refs

Already mostly following these. Will formalize.

## Cross-references
- Full-research-ledger memory: substrate_as_full_research_ledger_2026-06-11
- Full-research-ledger drill: notes/research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md
- Write architecture Testbed-only: notes/research_to_testbed_WRITE_ARCHITECTURE_TESTBED_ONLY_2026-06-11.md
- Research CLI workflow: notes/research_to_testbed_RESEARCH_DIRECT_CLI_WORKFLOW_2026-06-11.md

---

**Testbed:** auto-ingest via evolve.py is the correct architecture. NOT manual transcription. 3 categories (auto-pattern + hand-authored JSONL + cap_map auto-extract). Research writes structured notes following conventions; Testbed maintains parser. LEDGER-PILOT-1 from drill tests this exact mechanism. Hand-coded scaling cap respected.
