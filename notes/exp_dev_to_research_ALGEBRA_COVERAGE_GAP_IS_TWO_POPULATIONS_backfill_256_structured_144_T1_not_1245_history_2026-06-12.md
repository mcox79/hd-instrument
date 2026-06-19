# Exp-Dev -> Research/Testbed: the algebra/composite coverage "13.9pct" is TWO populations -- backfill target is 256 STRUCTURED atoms (144 T1-foundational), NOT the 1245 history atoms (correctly bge-served). Structured coverage is actually 48.6pct.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate usability / wiring-gap. NO LLM. PartitionedStore stats (local).
**Cell:** exp_substrate_algebra_coverage_gap_diagnosis_cpu_v1.py (re-runnable post-ingestion).

## The 13.9pct headline decomposes cleanly
- total atoms 1743; composite_hrr/algebra covered 242 (raw 13.9pct).
- gap = 1501 = **HISTORY 1245** (decision/research/verdict/findings/results history -- the substrate's self-ingested NARRATIVE
  provenance; descriptions but no algebra; 0 of them carry algebra -- correctly served by the bge semantic index, free-text path)
  + **STRUCTURED 256** (algebra-eligible math/science/concept atoms missing an authored algebra dict -- the REAL backfill target).
- **STRUCTURED coverage (excluding history corpus) = 242/498 = 48.6pct** -- the honest number. The 13.9pct headline conflates
  bge-served narrative with algebra-eligible atoms.

## The actionable backfill target (256 structured atoms)
- by corpus: **science 126, concept 60, math 45, meta 17, school 4, methodology 4**.
- **high-value subset = 144 T1-FOUNDATIONAL atoms lacking algebra**: vector_space, cosine_similarity, complex_field, real_field,
  unit_modulus, probability_distribution, shannon_entropy, kl_divergence, group_axioms, ring_axioms, field_axioms,
  discrete_optimization, graph_topology, ... -- these are CORE math/foundational primitives that SHOULD be fully algebra-encoded
  (they are exactly the atoms compose/decode/identity retrieval should reach).

## Why this matters
- Reframes the usability/wiring-gap worry: the substrate is NOT 86pct unwired. Narrative history (68pct of atoms) is correctly
  bge-served by design; the algebra channel covers ~49pct of structured atoms and the remaining backfill is a well-scoped,
  enumerable 256 (start with the 144 T1-foundational).
- Directly actionable for the FINDINGS #18 Gap-1 / algebra-vec authoring program: author algebra dicts for the 144 T1 atoms
  first (highest retrieval value), then the 126 science + 60 concept.

## Routing
- **Research:** the science algebra-vec taxonomy (FINDINGS #18 Gap 6) should prioritize the 144 T1-foundational atoms enumerated
  here -- they are the highest-value, clearly-eligible backfill. Science (126) is the largest structured-uncovered corpus.
- **Testbed:** algebra/composite coverage is 48.6pct of STRUCTURED atoms (not 13.9pct of all) -- the bge/algebra split is working
  as designed (history -> bge, structured -> algebra). Re-run this cell after each ingestion to track structured coverage.
- **Exp-Dev:** diagnosis complete; concrete backfill list surfaced. Holding.
