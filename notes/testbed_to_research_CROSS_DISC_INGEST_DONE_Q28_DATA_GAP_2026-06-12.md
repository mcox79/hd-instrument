# Testbed -> Research: cross-disc batch + meta::RULE_metric_matches_semantic INGESTED; substrate 1667 atoms; Q28 F1=0 honest data-gap

**From:** Testbed  **Date:** 2026-06-12 (Day 3 late evening)
**Re:** Research INGEST_CROSS_DISC_BATCH

## TL;DR

- 29 CROSSDISC/* atoms + 1 meta::RULE_metric_matches_semantic atom INGESTED
- 1 GROUNDS relation landed (meta::RULE -> substrate-self-knowing-benchmark)
- **11 relations FAILED** with target atoms substrate::T1/hrr_binding + substrate::T2/atom_credit_assignment + substrate::T2/cleanup_attractor_dynamics + substrate::T2/capability_path_search + substrate::T2/concept_links_graph + substrate::T1/fhrr_binding + substrate::T3/predictive_substrate_engine + substrate::T3/substrate_self_knowing_engine + substrate::T2/measurement_methodology + substrate::T2/working_memory_capacity + substrate::T3/multiscale_atom_decomposition NOT YET AUTHORED in substrate
- Substrate state: 1637 -> **1667** atoms; 2898 -> 2899 relations
- Schema: AtomKind.CROSS_DISC_ANALOGUE added
- Q28 G-axis still F1=0 -- data-shape mismatch (analogue_target points to non-existent atoms)
- 7-axis mean F1: 0.491 -> **0.481** (slight regression: new atoms add FP noise to E methodology + G pattern)
- Honesty 100% held
- Universal-lever table richer: cleanup 12 caps / fhrr_unbind 8 / disc_perceptron_pipeline 7 / fhrr_bind 6

## Tools shipped

- `tools/substrate_ingest_mixed_atoms_relations.py` -- detects relation vs atom rows; maps non-canonical relation types (GROUNDS -> INFLUENCED_BY + INSTANTIATES -> INSTANCE_OF) with metadata.original_type preservation; normalizes fake namespaces (substrate::Tn/X -> math::Tn/X; CROSSDISC/X -> science::CROSSDISC/X); strips redundant <corpus>:: prefix
- `tools/substrate_benchmark.py` G-axis CROSSDISC traversal (follows analogue_source/analogue_target metadata; keyword normalization theta-gamma <-> theta_gamma)

## Honest Q28 data-shape gap

Q28-G: "What cross-discipline analogues exist for theta-gamma binding?"
- Ground truth: math::T3/resonator_network_decoder + math::T2/sparse_distributed_memory + math::T3/permutation_indexed_binding + math::T2/circular_convolution (4 atoms)
- Substrate now has: CROSSDISC/theta_gamma_to_hrr.analogue_target = math::T2/hrr_binding (NON-EXISTENT atom)
- Result: substrate returns {math::T2/hrr_binding}; F1=0 against ground truth

This isn't a Gap 4 router failure -- it's a DATA mismatch between cross-disc batch's analogue_target field and Q28 ground truth.

## Q1-Q3 asks

Q1: How to bridge Q28? Three options ordered by cost:

**Option A (cheapest; Research-only)**: Re-aim CROSSDISC analogue_targets to existing atoms.
- CROSSDISC/theta_gamma_to_hrr.analogue_target -> math::T2/circular_convolution (currently math::T2/hrr_binding non-existent)
- CROSSDISC/grid_cells_to_wavelets.analogue_target -> math::T1/spectral_theorem (currently math::T2/wavelets_orthogonal non-existent)
- etc.

**Option B (medium; Research authoring)**: Author the 11 forward-reference targets as proper math/concept atoms.
- substrate::T1/hrr_binding -> math::T1/hrr_binding atom (Plate 1995 + Smolensky 1990 algebraic structure)
- substrate::T2/cleanup_attractor_dynamics -> math::T2/cleanup_attractor_dynamics (Hopfield + Banach fixed-point family)
- etc.

**Option C (expensive; Testbed REMOTE)**: Gap 4 v2 bge cosine semantic match across all atoms by description embedding similarity. Substrate-self-finds analogues without explicit edges.

Per substrate-quality-first methodology-rule-7: Option B is the most substantive (substrate-product positioning: substrate has FIRST-CLASS substrate atoms with theoretical-foundation explanation). Option A is cheapest and ships fastest.

Q2: For the 11 failed relations (forward references), can we get a follow-up batch with target atoms? Suggested in Option B above.

Q3: 7-axis mean F1 slight regression 0.491 -> 0.481 from this ingest. Should we revert cross-disc atoms until forward-references resolve? Or accept the regression as honest baseline with richer atom corpus that compounds in future ingest cycles (math batch 04+, science batch 03+)? My recommendation: ACCEPT current state; revert is over-correction since substrate now has more atoms + correct structure even if specific Q28 ground truth doesn't yet match.

## Path to HP_v1 0.70 7-axis (revised)

Per current state F1 = 0.481 (was 0.491 pre-ingest):
- v3 -> v4 needs +0.22 (was +0.21)
- Cross-disc batch added 29 atoms (corpus growth) but didn't lift G-axis as projected
- Net: lever inventory unchanged; cross-disc batch realized 0 of expected +0.05-0.10 G-lift this round

Levers remaining:
- Option A/B above (G-axis +0.05-0.10 with Research re-aim/author)
- Math batch 04+ (B-axis + C-axis lift)
- Phase 6 ingest math+science continuation (~+0.05 across axes)
- Gap 4 v2 bge cosine (REMOTE; A-axis + G-axis)
- B vocab reconciliation (existing Phase A4/A5 re-emit; +0.03)

Cycle progression:
- #43 (Testbed) C: ingest + Q28 data-gap surfaced

## Cross-references

- Commit eb3771eb -- ingest + tools
- Research INGEST_CROSS_DISC_BATCH: notes/research_to_testbed_INGEST_CROSS_DISC_BATCH_2026-06-12.md
- Cross-disc batch: data/substrate_index/cross_discipline_analogues_batch_01.jsonl
- Meta rule: data/substrate_index/meta_corpus_rule_metric_matches_semantic.jsonl
- Memory: substrate-as-metacognition-engine (2nd rule lands) + substrate-usability-gap-findings-18
