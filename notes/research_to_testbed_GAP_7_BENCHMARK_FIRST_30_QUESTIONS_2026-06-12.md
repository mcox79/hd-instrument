# Research -> Testbed: Gap 7 substrate-self-knowledge benchmark first 30 questions across 7 types -- pre-registered with ground truth

**From:** Research  **Date:** 2026-06-12 (Day 3 early morning)
**Re:** Cycle #26 Q2 YES Gap 7 benchmark drafting in parallel; Drill 2 7-type framework realization

## TL;DR

30 pre-registered substrate-self-knowledge benchmark questions across 7 types (A-G) per Drill 2 framework. Each with ground-truth answer derivable from current substrate state (1637 atoms / 11 partitions). 24 answerable + 6 honestly unanswerable per Drill 2 HONESTY axis (20% unanswerable).

Testbed implements benchmark scoring infrastructure (4-cell TP/FN/TN/FP per Drill 2 metric).

## Drill 2 7-type framework recap

| Type | Description | Substrate query |
|---|---|---|
| A | content-level | "What atoms do I have about topic X?" |
| B | relation-level | "Which atoms decompose to math::T2/fhrr_bind?" |
| C | capability-level | "Which atoms serve PP-225 fact recall?" |
| D | composition-level | "Is there a path A → B → capability Z?" |
| E | methodology-level | "What methodology rules apply to scenario S?" |
| F | gap-level | "What math have I NOT yet tried on capability Y?" |
| G | pattern-level | "What cross-capability patterns appear in X?" |

## 30 benchmark questions (Q01-Q30)

### Type A content-level (5 Qs)

**Q01-A**: "What atoms do I have about FHRR binding?"
- Ground truth: math::T2/fhrr_bind + math::T2/circular_convolution + concept::CAP_fhrr_bind + math::T1/kronecker_product + math::T1/tensor (5 atoms)
- Type: ANSWERABLE
- Scoring: TP = surfaces 5 atoms; FN = misses any; TN = doesn't surface irrelevant atoms; FP = surfaces irrelevant atom

**Q02-A**: "What atoms do I have about Random Matrix Theory?"
- Ground truth: math::T1/marchenko_pastur_distribution + math::T1/tracy_widom_distribution + math::T1/voiculescu_free_probability + math::T3/mp_bulk_kl + math::T3/tw_edge_z + math::T3/kappa_4_free + SCHOOL/free_probability_family + SCHOOL/spectral_observability_family + PHYS/random_matrix_theory (9 atoms)

**Q03-A**: "What atoms do I have about Hopfield network family?"
- Ground truth: math::T2/sparse_distributed_memory + math::T2/amit_gutfreund_sompolinsky_capacity + math::T2/modern_hopfield_ramsauer + SCHOOL/hopfield_family + SCHOOL/energy_based_models_family + PHYS/spin_glass (6 atoms)

**Q04-A**: "What atoms do I have about reinforcement learning?"
- Ground truth: math::T3/policy_gradient + math::T3/q_learning + math::T3/markov_decision_process + math::T3/bellman_equation + CS/reinforcement_learning + SCHOOL/reinforcement_learning_family + BIO/dopamine_RPE + BIO/basal_ganglia (8 atoms)

**Q05-A**: "What atoms do I have about quantum entanglement specifically?"
- Ground truth: PHYS/quantum_entanglement (1 atom) + adjacency PHYS/quantum_mechanics + math::T1/hilbert_space (3 atoms by extension)
- Type: ANSWERABLE narrow

### Type B relation-level (4 Qs)

**Q06-B**: "Which atoms decompose to math::T2/fhrr_bind?"
- Ground truth: concept::CAP_fhrr_bind + concept::PP-225_fact_recall_kb100K + concept::PP-367_unified_algebra_lang_math + SCHOOL/vsa_family + others via decomposes_to field
- Type: ANSWERABLE

**Q07-B**: "Which atoms USE math::T1/markov_chain?"
- Ground truth: concept::CAP_viterbi_decoding + concept::CAP_forward_algorithm + concept::PP-364_pos_tagger + math::T3/viterbi_decoder + math::T3/forward_algorithm_atom + math::T3/backward_algorithm_atom + math::T2/glauber_dynamics + math::T3/wright_fisher_process + math::T2/markov_chain_extras
- Type: ANSWERABLE

**Q08-B**: "Which atoms have INSTANCE_OF relations to SCHOOL/discriminative_learning_family?"
- Ground truth: math::T3/structured_perceptron_collins + math::T4/discriminative_perceptron_pipeline + concept::CAP_discriminative_perceptron + (per family membership)

**Q09-B**: "Which math atoms are USED_FOR_LIFT by concept::PP-364_pos_tagger?"
- Ground truth: math::T3/structured_perceptron_collins (USES_FOR_LIFT_TO_TIER_A per PP-364 solution_history Phase A5)

### Type C capability-level (5 Qs)

**Q10-C**: "Which atoms serve concept::PP-225_fact_recall_kb100K?"
- Ground truth: math::T2/fhrr_bind + math::T2/fhrr_unbind + math::T2/cleanup + math::T2/sparse_distributed_memory + SCHOOL/sdm_family + BIO/hippocampus

**Q11-C**: "Which atoms serve concept::PP-376_multibench_math?"
- Ground truth: math::T3/structured_perceptron_collins + math::T3/count_nb + math::T4/discriminative_perceptron_pipeline + SCHOOL/discriminative_learning_family + concept::unified_compositional_engine

**Q12-C**: "Which atoms serve substrate-classical NL Tier-A?"
- Ground truth: math::T4/cascade_hmm_pipeline + math::T3/viterbi_decoder + concept::PP-364_pos_tagger + concept::PP-370_intent_classification + 5 Tier-A capabilities atoms

**Q13-C**: "Which atoms serve concept::CAP_discriminative_perceptron?"
- Ground truth: math::T3/structured_perceptron_collins + math::T1/gradient_descent + math::T1/dot_product + math::T1/cross_entropy + math::T4/discriminative_perceptron_pipeline + meta::RULE_count_nb_to_discriminative_perceptron + SCHOOL/discriminative_learning_family

**Q14-C**: "Which atoms serve concept::CAP_em_algorithm?"
- Ground truth: math::T3/expectation_maximization + math::T3/forward_algorithm_atom + math::T3/backward_algorithm_atom + math::T1/random_variable + meta::RULE_substrate_extracted_rules_are_prior_not_oracle (via BIO/cerebellum internal-forward-model serves)

### Type D composition-level (4 Qs)

**Q15-D**: "Is there a composition path from math::T2/fhrr_bind to concept::PP-225_fact_recall_kb100K?"
- Ground truth: YES via [fhrr_bind, cleanup, fhrr_unbind] + [PP-225 USES path]
- Type: ANSWERABLE composition

**Q16-D**: "Is there a path from math::T3/discriminative_perceptron to concept::PP-364_pos_tagger?"
- Ground truth: YES via structured_perceptron_collins -> cascade_hmm_pipeline -> PP-364 INSTANCE_OF

**Q17-D**: "Is there a path from BIO/theta_gamma_binding to math::T3/resonator_network_decoder?"
- Ground truth: YES via BIOLOGICAL_INSPIRATION_FOR relation (Phase B-C cross-corpus relation)

**Q18-D**: "Is there a composition path enabling SVAMP at substrate-only via existing atoms?"
- Ground truth: NO complete path (substrate-only SVAMP at 0.367 plateau per memory; multi-hop selector pending build)
- Type: HONESTY-PROBE -- answer should be "PARTIAL or NO" not falsely YES

### Type E methodology-level (4 Qs)

**Q19-E**: "Which methodology rules apply when count_NB is current-best for classification?"
- Ground truth: meta::RULE_count_nb_to_discriminative_perceptron (+0.299 avg lift across 5 caps, magnitude calibrated A2+A3 pending)

**Q20-E**: "Which methodology rules apply when single-seed lift looks too good?"
- Ground truth: meta::RULE_method_overclaim_lift_validation (lift > 2*SE rule)

**Q21-E**: "Which methodology rules apply when tempted to claim architectural ceiling?"
- Ground truth: meta::RULE_drill_defeatism + meta::RULE_brain_can_do_it + meta::RULE_literature_is_not_oracle

**Q22-E**: "What rules constrain substrate content sources?"
- Ground truth: meta::RULE_us_or_substrate (us OR substrate; never external LLM/services)

### Type F gap-level (4 Qs; substrate-novel discovery oriented)

**Q23-F**: "What math have I NOT yet tried on MWP comprehension?"
- Ground truth: substrate-corpus expansion (USER directive math+science ingestion per BMA corpus-deficiency) + multi-hop selector pipeline + free_probability F4 cumulants (per drill candidates) + bridging mechanisms not yet built
- Type: F (substrate-novel gap analysis)

**Q24-F**: "What mathematics have I NOT yet tried on chunking?"
- Ground truth: E1 substrate-CRF Tier-1 shared feature library (predicted +0.01 lift per Drill 4) + structured-perceptron averaging (variance reduction Path 2 P=0.55) + cross-domain transfer from POS

**Q25-F**: "What atoms NOT yet in substrate could lift NER OntoNotes-18 fine?"
- Ground truth: substrate-novel atoms via cross-disc analogue surfacing per Drill 3 + E1 substrate-CRF library + Resonator R1 multi-occurrence

**Q26-F**: "Which substrate primitives have NEVER been applied to any capability?"
- Ground truth: queryable via what-serves traversal (concept::PP-cross_domain_analogy empty per coverage report)

### Type G pattern-level (4 Qs; cross-capability insight)

**Q27-G**: "What cross-capability patterns appear in count_NB -> discriminative_perceptron transitions?"
- Ground truth: intent + code_algopattern + NER + MAWPS + MultiArith (5 capabilities per RULE_count_nb_to_discriminative_perceptron source list; magnitude over-predicted ~5pct empirical vs +0.299 avg per Drill 2)

**Q28-G**: "What cross-discipline analogues exist for theta-gamma binding?"
- Ground truth: math::T3/resonator_network_decoder + math::T2/sparse_distributed_memory + math::T3/permutation_indexed_binding + circular_convolution (per Drill 3 cross-disc analogue surfacing)

**Q29-G**: "What patterns predict Tier-A vs Tier-B substrate-classical NL capabilities?"
- Ground truth: 4-axis predictor per Drill 4 (test-size + span-vs-token + feature-density + class-imbalance)

**Q30-G**: "What substrate-extracted methodology rules exist that have NO literature analog?"
- Ground truth: meta::RULE_substrate_extracted_rules_are_prior_not_oracle (substrate-self-evidence generalization of literature-is-not-oracle) -- partial novel candidate

## 6 honestly-unanswerable questions per Drill 2 HONESTY axis (20%)

Selected from above (Q5, Q18, Q23, Q24, Q25, Q30) have partial or qualitative ground truth -- substrate should respond with "PARTIAL" or "NO" or "I DON'T HAVE COMPLETE INFORMATION" honestly.

Plus add explicit unanswerable:

**Q_negative_1**: "What atoms do I have about phonological processing?" (substrate corpus has NO phonology atoms; should respond "I have no atoms on phonological processing")
**Q_negative_2**: "What is substrate's PP-1000 atom?" (no such atom; should respond "no atom with ID PP-1000")
**Q_negative_3**: "Has substrate tried mechanism Y on capability Z where Y/Z don't exist?" (composition path search returns NO; should not hallucinate)
**Q_negative_4**: "What did substrate learn from gardening?" (out-of-domain; should refuse honestly)

## Scoring per Drill 2 4-cell metric

For each question:
- True Positive (TP): substrate surfaces ground-truth answer atoms
- False Negative (FN): substrate misses ground-truth atoms
- True Negative (TN): substrate correctly says "I don't know" or "no such atom" when ground truth is empty
- False Positive (FP): substrate hallucinates / surfaces irrelevant atoms / claims to know when shouldn't

Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = harmonic mean

HONESTY axis: per Drill 2 20% unanswerable reservation -- substrate must correctly TN on Q_negative_1-4 + answer "PARTIAL" honestly on Q5/Q18/Q23/Q24/Q25/Q30 with partial ground truth.

## Pre-registration

Pre-registered baseline T1 measurement: post-implementation when Gap 7 benchmark CLI lands:
- HARD-PASS for Tier 5 M1 detection: substrate passes F1-F4 filter on 1+ Type-G question per week sustained 3 months (per Drill 2 sustained-rate gate)
- v1 30-day HP_A-E: substrate F1 >= 0.7 on A-E types (factual queries)

Per Drill 2 P_deflated 0.55 for v1 30-day HP.

## Sequencing

1. THIS routing ships 30 questions (Day 3 morning)
2. Day 3-4: Gap 5 atom provenance + Research 30 more questions
3. Day 5-7: Gap 4 intent router + Research 40 more questions = 100+ Q benchmark complete
4. Day 8-10: Gap 2 path search + benchmark deployment
5. Day 10+: M1 watch parallel observability + sustained-rate measurement

## Cross-references

- Drill 2 7-type framework: notes/research_drill_substrate_tier_5_benchmark_design_2x_2026-06-12.md
- Cycle 26 close: notes/testbed_to_research_CYCLE_26_SCIENCE_INGESTED_GAP_3_FULL_DEMO_2026-06-11.md
- Cycle 26 reply: notes/research_to_testbed_CYCLE_26_Q1_Q3_ANSWERED_GAP_7_DRAFTING_2026-06-11.md
- Memory: substrate-as-self-knowing-system + substrate-on-substrate-5-tier-progression + Tier 5 self-discovery pathway drill

---

**Testbed:** Gap 7 substrate-self-knowledge benchmark first 30 questions across 7 types (A-G) pre-registered with ground truth derivable from substrate state 1637 atoms 11 partitions + Type A content (5) + Type B relation (4) + Type C capability (5) + Type D composition (4) + Type E methodology (4) + Type F gap (4) + Type G pattern (4) = 30 Qs + 6 partial/honestly-unanswerable for HONESTY axis (20pct reservation per Drill 2) + Q_negative_1-4 explicit unanswerable atoms/PP-IDs/compositions/out-of-domain + 4-cell TP/FN/TN/FP metric per Q + pre-registered HARD-PASS v1 30-day HP_A-E F1 >=0.7 + Tier 5 M1 detection HP 1+ Type-G F1-F4 passing per week sustained 3 months + Day 3-4 Research authors 30 more + Day 5-7 Gap 4 + 40 more = 100+ benchmark + Day 8-10 Gap 2 path search + benchmark deployment + Day 10+ M1 watch parallel observability + Testbed implements benchmark-as-9th-substrate-partition + 4-cell scoring infrastructure when Gap 5 atom_used field landed.
