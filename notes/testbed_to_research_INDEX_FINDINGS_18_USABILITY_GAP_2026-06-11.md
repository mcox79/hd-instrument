# Testbed -> Research: FINDINGS #18 -- substrate usability gap after massive ingestion

**From:** Testbed  **Date:** 2026-06-11 late evening
**Trigger:** USER question post-compaction "after this massive ingestion - how will the substrate know what it has and how to use it?"
**Status:** USER answered "yes" to "file note + implement (A) directly"

## TL;DR

Ingestion alone is necessary but not sufficient. Substrate today has STORAGE + basic RETRIEVAL but lacks the layers that turn a corpus into a usable knowledge base. Six concrete gaps surfaced. USER green-lit (A) `serves_capability` field implementation directly; Research please refine + dispatch the other five.

## What works today (storage + basic retrieval)

- Partitioned store (math 144 / concept 66 / meta 8 + 8 history partitions); provenance preserved per atom
- Three retrieval indexes: semantic (bge-large) + algebra (HRR cleanup) + content-reference (name-match) -> RRF fusion
- Typed edges: DEPENDS_ON / USES / COMPOSES / DUAL / EQUIVALENT_UNDER / SUPERSEDES / DEFINED_OVER / GENERALIZES / INSTANCE_OF
- `solution_history` per capability + `cross_capability_best_overlap()` quantifies universal levers (discriminative_perceptron at 92pct of caps)
- `discover.cluster_unification()` surfaces redundancies / gaps autonomously
- Substrate-eval composite_C classifies new content (Option B+E+H dual-process recognition pending re-validation)
- Substrate-extracted methodology rules (first: count_NB -> discriminative_perceptron +0.299)

## The six gaps that block usability

### Gap 1 -- capability -> math reverse index (USER GREEN-LIT, implementing now)

Math atoms link to other math atoms via DEPENDS_ON tree. When MWP needs "fraction operations + algebraic substitution", there is no path from `cap=MWP` to `[atoms_relevant_to_MWP]`. Symptom: ingesting 500 math atoms doesn't automatically improve MWP retrieval -- substrate doesn't know which atoms are relevant to which capability.

Fix shape: add `serves_capability: List[str]` field to Atom schema. Wire at ingest-time for new batches; retroactive backfill for existing 218 via Research-authored mapping or substrate-eval inference. Cheap. Done at write time.

### Gap 2 -- compositional path search over typed edges

Typed edges exist; graph-walk to assemble a composition (primitive A o B o C -> realizes capability X) does not. Per [[substrate-tier-3-atoms-insufficient-need-pipeline-2026-06-11]]: Tier 3 atoms are PRIMITIVES; Tier 4 requires END-TO-END PIPELINE wiring primitives into capability-realizing mechanism. Today substrate must be hand-wired per capability.

Fix shape: Dijkstra/A* over the typed-edge graph with capability as target. Edge-weight = empirical evidence from solution_history. ~1 week.

### Gap 3 -- substrate-self-knowledge QA layer (D6 -- previously deferred)

Substrate should answer:
- "What do I know about topic X?"
- "What math have I NOT yet tried on capability Y?"
- "Which atoms have ever produced a measurable lift?"
- "Is there a known composition path from atom A to capability B?"

This is the QUERY layer over the index. D6 was deferred in the unrouted-experiments inventory; USER question elevates its priority. Without it the corpus is read-only literature.

Fix shape: query endpoint accepting natural-language probe; routes via lexicon -> partition -> retrieval -> compositional path search -> answer. ~1 week.

### Gap 4 -- intent router / lexicon as front-door

Lexicon partition exists; concept atoms exist; no explicit lookup-table front-door that resolves arbitrary NL probes to atom subsets. Per [[substrate-two-axes-semantic-vs-content-referenced-2026-06-11]]: semantic + content-references both needed.

Fix shape: lexicon-keyed intent router maps NL probe -> atom partitions + retrieval mode (semantic / algebra / hybrid). Ships alongside Gap 3.

### Gap 5 -- provenance back from solution_history -> atoms

When a solution lifted +0.114 on ASDiv, WHICH atoms were the load-bearing ones? Today we know the METHOD (e.g. "HRR binding chain") but not the exact atom set. `methodology_rule_extraction` only sees the rule pattern, not the operands.

Fix shape: extend solution_history record with `atoms_used: List[atom_id]`. Wire when filing new solutions; retroactive backfill where possible.

### Gap 6 -- algebra-vec coverage for science domains

Math has 13-category taxonomy enabling cosine-based shared-basis detection. Physics/chemistry/biology lack analogue. Without it science atoms collapse to semantic-only -- the weakest signal per Day-1 60pct EMBEDDING_DRIFT finding.

Fix shape: science algebra taxonomy ~ {physical_quantity / conservation_law / symmetry / phase_relation / scale_invariance / reaction / equilibrium / field / particle / mechanism / chemical_structure / biochemical_process / evolutionary_dynamic / ecological_relation / ...}. Research authors. ~2-3 days.

## Sequencing recommendation

Without Gap-1 + Gap-3 in place, math+science ingestion DILUTES retrieval rather than compounds it. Per [[substrate-mwp-comprehension-blind-spot-corpus-limited-2026-06-12]]: more corpus is the right answer, but it needs the index/router/composition layer to be PRODUCTIVE.

Proposed order:
1. **(A) Gap 1** -- `serves_capability` field. USER green-lit. Testbed implementing now. ~half day.
2. **(F) Gap 6** -- science algebra taxonomy. Research authors. ~2-3 days. Lands BEFORE science ingestion.
3. **(C) Gap 3 + Gap 4** -- self-knowledge QA + intent router. Testbed builds. ~1 week.
4. **(B) Gap 2** -- compositional path search. Testbed builds. ~1 week.
5. **(E) Gap 5** -- solution_history atom provenance. Testbed builds during natural cycle close. ~2 days.

## Asks for Research

Q1: Endorse the six-gap framing? Any gap missing? Order correct?

Q2: For Gap 6 -- can Research author a science algebra taxonomy on Day 2-3 BEFORE science ingestion lands? Mirror the math 13-category structure.

Q3: For Gap 1 implementation -- should `serves_capability` be derived (substrate-eval inference at ingest) or authored (Research-supplied per atom)? Mixed seems best (Research seed + substrate-eval auto-extend).

Q4: Should this be filed as a Cycle X Type C architectural refinement candidate (substrate-self-improvement signal)?

Q5: Anything in Research's pipeline (math batch 03 Phase B-D, science batch 01) needs to wait for Gap 1+6 to be in place? If yes, hold those drops; ship the index/router layer first.

## Cross-references

- [[substrate-tier-3-atoms-insufficient-need-pipeline-2026-06-11]] -- primitives are not pipelines
- [[substrate-mwp-comprehension-blind-spot-corpus-limited-2026-06-12]] -- corpus deficiency root cause
- [[substrate-two-axes-semantic-vs-content-referenced-2026-06-11]] -- semantic + content-references both needed
- [[substrate-self-index-foundational-tool]] -- 15 modules in backend/substrate_index/
- USER directive locked: [[notes/research_to_testbed_USER_MASSIVE_MATH_SCIENCE_INGESTION_PRIORITY_2026-06-11.md]]
