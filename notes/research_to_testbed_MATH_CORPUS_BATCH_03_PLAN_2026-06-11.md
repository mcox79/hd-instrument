# Research -> Testbed: math corpus batch 03 design plan (300-500 sub-op decomposition + T4 macros + 27-tag refactor)

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Day 2 substrate-intrinsic priority math corpus batch 03

## Scope

Batch 03 extends batch 01+02 to full Tier-3 sub-op decomposition + T4 macro composite-entry-points + 27-tag 5-super-group family refactor per drill 5 free-prob+family-tag.

| Tier | Current (batch 01+02) | Target batch 03 | Net new |
|---|---|---|---|
| T1 foundational | 15 atoms | 20-25 atoms | +5-10 |
| T2 substrate primitives | 11 atoms | 15-20 atoms | +4-9 |
| T2 family-tags | 11 atoms | 27 atoms (5 super-groups: binders/unbinders/mixers/transformers/observers) | +16 |
| T3 sub-ops | 25 atoms | 300-500 atoms | +275-475 |
| T4 macros | 0 atoms | 20-25 atoms | +20-25 |
| Total atoms | 62 | ~400-600 | +320-540 |

Plus algebra-vec on all new atoms (13-category taxonomy + 14-field schema + concept_links).

## T3 sub-op decomposition strategy

Each T3 algorithm atom currently in batch 01 (~25 atoms) decomposes into ~10-15 sub-ops:

Example: T3/viterbi_decoding decomposes into:
- T3_SUB/viterbi_initialization
- T3_SUB/viterbi_state_transition
- T3_SUB/viterbi_emission_update
- T3_SUB/viterbi_max_update
- T3_SUB/viterbi_backpointer
- T3_SUB/viterbi_traceback
- T3_SUB/viterbi_length_normalization
- T3_SUB/viterbi_log_space_arithmetic

Each sub-op has algebra-vec + signature + complexity + concept_links.

Multiply ~25 base algorithms x ~12 sub-ops = ~300 sub-op decomposition. Plus 50-100 more from algorithm variants (Hungarian variants + MST variants + Bayesian variants).

## T4 macro composite-entry-points

Substrate-architecture validated capabilities:
- T4/substrate_POS_tagger (PP-364 + PP-379)
- T4/substrate_slot_filler (PP-369)
- T4/substrate_intent_classifier (PP-370)
- T4/substrate_schema_retrieval (PP-372)
- T4/substrate_reasoning_routing (PP-371)
- T4/substrate_math_word_problem_solver (PP-376 + PP-375)
- T4/substrate_code_algopattern_classifier (PP-378)
- T4/substrate_text_classifier (AG-News validated today)
- T4/substrate_sentiment_classifier (SST-2 validated today)
- T4/substrate_chunker (UD-EWT validated today)
- T4/substrate_NL_pipeline_demo (ATIS HARD_PASS today)
- T4/substrate_fact_recall (PP-225 kb100K)
- T4/substrate_unified_algebra (PP-367)
- T4/substrate_CRF (universal; per drill in flight)
- T4/substrate_3op_composition (per drill in flight; future)

Each T4 macro decomposes_to: list of T3 sub-ops + T2 primitives + T1 foundational.

## 27-tag family-tag refactor per drill 5

Replace current 11 family-tags with 27 organized into 5 super-groups:

| Super-group | Family-tags | Examples |
|---|---|---|
| Binders | algebraic_binding + role_filler_binding + context_binding + sequence_binding + tensor_product_binding | FHRR bind + role-filler + context-mod |
| Unbinders | conjugate_inverse + content_addressable_recall + cleanup_retrieval + cross_correlation_unbinding | FHRR unbind + cleanup |
| Mixers | superposition_aggregation + weighted_sum + count_weighted + softmax_aggregation + voting | bundling + Tier-2 schemas + count-NB |
| Transformers | representation_transform + whitening + projection + dimensionality_reduction + normalization | PCA + ZCA + L2-norm |
| Observers | similarity_measure + spectral_observable + statistical_distribution + capacity_measure + drift_detector | cosine + Hamming + free-prob F4 + KL |

5 super-groups x ~5-6 family-tags = 27 family-tags. Each has algebra-vec + members list.

## Implementation sequencing

Phase 1 Day 2 morning: T4 macros (~20-25 atoms) + 27-tag refactor (substrate-architecture-level)
Phase 2 Day 2 afternoon: T1 + T2 primitive extensions (~15-20 atoms)
Phase 3 Day 2 evening: T3 sub-op decomposition first wave (~100 sub-ops) from highest-priority algorithms (Viterbi + Hungarian + count-NB + discriminative perceptron)
Phase 4 Day 3+: T3 sub-op decomposition full wave (300+ sub-ops) + concept corpus full + schools corpus + cross-corpus relations

## Substrate-intrinsic outcomes

- Substrate-self-index discovers more structural unifications (per Layer 3 today: 5 of 6 substrate-proposed equivalences point at probabilistic-DP + graph_traversal unification)
- Layer 2 spectral observability gets M >= 100 threshold met (drill 5 free-prob+family-tag)
- Layer 5 capability-substrate dialectic operates on rich corpus (decomposes_to + family_tag_members + substrate_lever fields)
- v2 hybrid two-index Index 2 atom-to-atom shared-basis retrieval works on rich algebra-vec (Findings 05 DEMO validated)
- Substrate becomes its own roadmap empirically

## Cross-references
- Drill 5 free-prob + family-tag: notes/research_drill_free_probability_family_tag_2x_2026-06-11.md
- Drill 14 algebra taxonomy + formal systems: notes/research_drill_algebra_taxonomy_formal_systems_2x_2026-06-11.md
- Layer 3 Findings 06 substrate-internal discovery: notes/testbed_to_research_INDEX_FINDINGS_06_LAYER3_SUBSTRATE_PROPOSES_EQUIVALENCES_2026-06-11.md
- Substrate self-evaluation 8-layer program memory
- 5-tier progression memory
- Substrate-CRF universal NL drill (in flight)
- Substrate 3-op compositional extension drill (in flight)
- Free-probability F4 3x DEEP drill (in flight)

---

**Testbed:** math corpus batch 03 plan filed; T1+T2+T3+T4 atoms + 27-tag refactor + algebra-vec on all + decomposes_to + concept_links; Phase 1 Day 2 morning T4 macros + 27-tag; Phase 2-3 Day 2 afternoon-evening; Phase 4 Day 3+ full T3 sub-op decomposition. Substrate-intrinsic priority per user refocus.
