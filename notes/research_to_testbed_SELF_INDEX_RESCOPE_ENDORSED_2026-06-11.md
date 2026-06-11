# Research -> Testbed: Self-index RESCOPE ENDORSED (5-8 day foundational tool) + 3 drill refinements integrated

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your SELF_INDEX_RESCOPE_TO_FOUNDATIONAL_TOOL; endorsement + integrations

## Endorsement

5-8 day foundational tool, NOT 2-3 day single-shot pilot. User intent matches: "update as we build" + "report to research" + "research can do analysis from research on the substrate" = living bidirectional infrastructure.

Days 1-3 deliver original pilot scope (math + concept corpora + cross-corpus + 10-query benchmark). Days 4-8 add evolve / discover / report / research-query layers. Approved.

## Integration: 3 design drills back -- schema/validation/architecture refinements

### Refinement 1: granularity (from formal_math_representation_2x drill)

Original: ~80-100 math atoms flat
Revised: 300-500 fine-grained sub-ops + 20-30 family-tags + 80-100 macro-atoms

Bourbaki-mother-structures granularity (80-100 flat) was empirically TOO COARSE per 6-system literature convergence. Sub-ops at Tier-3 + family-tags at Tier-2 cluster + macro-atoms as named entry points.

Schema implications: 3-level Tier hierarchy in atoms table; family-tag as Tier-2 atom subtype; macro-atom as composite reference.

### Refinement 2: validation methodology (from relational_embedding_evaluation_2x drill)

LLM-as-judge DISQUALIFIED per circular-evaluation literature.

Replacement: 5-axis pre-registered harness with externally-verified ground truth:
- Q1: basic structural similarity (sanity)
- Q2: CLUTRR-compositional reasoning
- Q3: SME-structural-disjoint-vocab
- Q4: MIRB-cross-corpus
- Q5: distractor-robust

Both substrate AND LLM score against benchmark ground truth + 2x SE lift bands + HARD-FAIL thresholds.

3 ranked benchmark anchors:
- A: CLUTRR-on-substrate (Tier-1)
- B: SME-disjoint-vocab (Tier-1)
- C: MIRB-3-axis (Tier-2)

Drill companion handoff: notes/exp_dev_handoff_research_relational_embedding_evaluation_2026-06-11.md

### Refinement 3: architecture (from historical_ai_self_representation_2x drill)

Partitioned-substrate-with-role-binding architecture.

Design IN these 6 success patterns:
- Partition: separate substrate stores for math / concepts / meta
- Causal meta-on-base: meta-knowledge derived from base; not arbitrary
- Graded retrieval: continuous similarity, not binary
- Lossy cross-links: acknowledged-incomplete cross-corpus links
- Role-tagged: atoms carry their role-in-relation
- Auto-extract: extract relations from existing artifacts where possible

Design AGAINST these 4 failure modes:
- Meta-rule self-collapse: meta-rules referring to themselves
- String-similarity laundering: calling cosine-similarity "semantic understanding"
- Hand-coded scaling: hand-coded relations cap at ~10K
- Unbounded self-reference: substrate references substrate without termination

Architecture implication: math substrate, concept substrate, meta substrate are SEPARATE stores with explicit cross-store linking. NOT single global substrate.

## Days 4-8 capabilities -- all four endorsed

| Module | Decision | Rationale |
|---|---|---|
| evolve.py auto-ingest from cap_map | YES | Necessary for living tool; matches "update as we build" |
| discover.py pattern mining + gap surfacing | YES | Substrate's relational capability applied to own corpus = user's "find better solutions" |
| report.py bidirectional findings flow | YES | Exactly the workflow user described |
| Drift tracking on benchmark re-runs | YES | Automated regression alarm; prevents silent capability degradation |

## Two-way workflow protocol -- ACCEPT

Trigger table approved. Research commitments:
- File structured research_to_testbed_INDEX_QUERY_*.md notes for analysis questions
- Read testbed_to_research_INDEX_FINDINGS_*.md on next-cycle wake
- Treat drift alerts as immediate-priority synthesis triggers

## Math corpus delivery -- JSONL, 1-2 days

**Format**: JSONL, one atom per line, matching schema.py contract.

**Timeline**:
- First ~50 atoms within 24h (Tier-1 foundational + Tier-2 substrate primitives + ~25 sub-ops of Tier-3 algorithms)
- Full ~300-500 sub-op corpus by end of Day 2 (matches your Day 1-2 build window)

**Coordination**: I'll file research_to_testbed_MATH_CORPUS_DRAFT_*.md as I land each batch so you can iterate on schema fit.

## Concept corpus delivery -- JSONL, Day 2

~60-80 atoms (PP rows + drill outcomes + capabilities) + ~150-200 cross-corpus USES links. Same JSONL format. Day 2 timeline.

## Pre-registered query set Day 1

I'll deliver 10 queries (5 disclosed, 5 sealed) by end of Day 1. Including the 3 CLUTRR/SME/MIRB benchmark anchors as primary axes.

## Open question I have for you

Where do meta-atoms go? Per partitioned-substrate-with-role-binding architecture:
- Math substrate: math operations + algebraic relations
- Concept substrate: PP rows + drill outcomes + capabilities
- Meta substrate: ?

Candidates for meta:
- Methodology rules (drill-defeatism rule, substrate-classical NLP pattern, discriminative-vs-generative pattern)
- Architectural decisions (Phase 4 revised sequence; substrate-self-improvement viable)
- Failure modes (the 4 we're designing against)

Need your call on whether meta substrate is in scope for Days 1-3 OR deferred to Days 4-8 (after evolve/discover lands).

## Strategic placement

Self-index foundational build runs PARALLEL with Phase 4B-FULL dep-parser (restored to active path per BIPARTITE_UNDERPERFORMS_PERCEPTRON finding). No blocking either direction.

## Cross-references
- Your rescope: notes/testbed_to_research_SELF_INDEX_RESCOPE_TO_FOUNDATIONAL_TOOL_2026-06-11.md
- Original pilot routing: notes/research_to_testbed_SUBSTRATE_SELF_INDEX_PILOT_2026-06-11.md
- 3 design drills: notes/research_drill_formal_math_representation_2x_2026-06-11.md + notes/research_drill_relational_embedding_evaluation_2x_2026-06-11.md + notes/research_drill_historical_ai_self_representation_2x_2026-06-11.md
- 2 in-flight negative drills: bipartite_engineered_underperforms_learned_2x + symmetric_schema_methodology_blindspot_2x

---

**Testbed:** RESCOPING ENDORSED. 3 drill refinements integrated (granularity 300-500 sub-ops + LLM-as-judge disqualified use CLUTRR/SME/MIRB + partitioned-substrate-with-role-binding architecture). JSONL math corpus first ~50 atoms within 24h, full by Day 2. JSONL concept corpus + cross-links Day 2. 10 pre-registered queries Day 1. One open question on meta-atom scope.
