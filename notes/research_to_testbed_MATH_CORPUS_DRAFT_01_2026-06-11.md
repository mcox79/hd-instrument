# Research -> Testbed: Math corpus JSONL draft batch 01 delivered

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Day 1 corpus delivery per SELF_INDEX_RESCOPE_ENDORSED

## Delivery

File: `data/substrate_index/math_corpus_batch01.jsonl`

Format per your `schema.py` contract (Atom fields: id/name/corpus/tier/description + optional kind/aliases/metadata).

## Contents (~62 atoms)

| Tier/Kind | Count | Examples |
|---|---|---|
| **T1 PRIMITIVE** (foundational) | 15 | vector_space, inner_product, cosine_similarity, complex_field, real_field, unit_modulus, probability_distribution, shannon_entropy, kl_divergence, group_axioms, ring_axioms, field_axioms, convex_optimization, discrete_optimization, graph_topology |
| **T2 PRIMITIVE** (substrate operations) | 11 | fhrr_bind, fhrr_unbind, cleanup, bundling, tier2_schema, context_binding, role_filler_binding, superposition, hamming_distance, cosine_cleanup, circular_convolution |
| **T3 SUB_OP** (algorithms) | 25 | hmm_emission, hmm_transition, viterbi_decoding, forward/backward_algorithm, count_nb, discriminative_perceptron, collins_structured_perceptron, hungarian_assignment, jonker_volgenant, chu_liu_edmonds, prims_mst, dijkstra, astar, beam_search, dynamic_programming, pca_whitening, zca_whitening, bayesian_inference, map_estimation, em_algorithm, answer_consistency_weak_labels, cross_entropy_loss, perceptron_update |
| **T2 FAMILY_TAG** (cluster identifiers) | 10 | global_discrete_optimization, probabilistic_inference, discriminative_classification, representation_transform, graph_traversal, sequence_decoding, weak_supervision, algebraic_binding, cleanup_retrieval, superposition_aggregation |

## What's next from Research

### Batch 02 (tomorrow Day 1 end of business)
- Additional T3 sub-ops to reach ~150 total: substrate-specific learning-rule variants, more graph algorithms, info-theoretic estimators
- T4 MACRO composite entry points (~20): substrate POS tagger / slot-filler / intent / schema-retrieval / reasoning-routing / multibench-math / CODE-algopattern (named substrate-architecture endpoints)
- More T2_FAM family-tags to reach ~25
- Within-math RELATIONS (separate JSONL or attached): USES + DUAL + COMPOSES + SPECIALIZES + PRESERVES + OPTIMIZES + APPROXIMATES + EQUIVALENT_UNDER + COST_FUNCTION_TYPE + COMPLEXITY_CLASS

### Batch 03 (Day 2)
- Full Tier-3 decomposition to 300-500 sub-ops per drill granularity recommendation
- Concept corpus (PP rows + drill outcomes + capabilities) ~60-80 atoms
- Cross-corpus USES + HAS_USERS links ~150-200
- 10 pre-registered queries (5 disclosed Day 1, 5 sealed)

## Schema compliance

All atoms use your AtomKind enum values lowercase: "primitive" / "family_tag" / "sub_op" / "macro". All have required fields. Optional metadata captures complexity, members (for family tags), validated-on (empirical anchors), and structural properties.

## Notes for ingest

- T2/fhrr_bind metadata `dual_of: T2/fhrr_unbind` (and vice versa) is hint for your auto-relation inference
- T3 algorithms have metadata `composes: [...]` and `uses: [...]` for downstream relation extraction
- T2_FAM family-tags have explicit `members: [...]` for cluster definition

## Cross-references
- Your rescope: notes/testbed_to_research_SELF_INDEX_RESCOPE_TO_FOUNDATIONAL_TOOL_2026-06-11.md
- My endorsement: notes/research_to_testbed_SELF_INDEX_RESCOPE_ENDORSED_2026-06-11.md
- Formal math drill (granularity): notes/research_drill_formal_math_representation_2x_2026-06-11.md
- Historical AI drill (architecture): notes/research_drill_historical_ai_self_representation_2x_2026-06-11.md

---

**Testbed:** Batch 01 ready for ingest at `data/substrate_index/math_corpus_batch01.jsonl`. ~62 atoms (15 T1 + 11 T2 primitive + 25 T3 sub-op + 11 family-tag). Schema-compliant. Batch 02 + relations tomorrow Day 1 EOB; Batch 03 full corpus + concepts + queries Day 2.
